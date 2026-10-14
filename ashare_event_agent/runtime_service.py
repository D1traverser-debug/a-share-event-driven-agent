from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .checks import audit_event_times, audit_source_completion, sha256_file, write_json
from .controller import WorkflowController
from .engine import MarketDayEngine, WorkflowError
from .models import Artifact, ArtifactKind, GateStatus, Stage, TaskContract, TaskMode
from .schemas import (
    AttributionPackage, EventLedgerPackage, ExecutionPlan, FreezeCard, GateDecision,
    IndustryResearchPackage, LearningAudit, MarketStructurePackage, OutcomePackage,
    RecallGrade, RecallPoolPackage, ReplayEval, RuleProposal, SourceCompletionPackage,
    StockBaseContext, UniversePackage,
)
from .store import SQLiteStateStore

DATA_DIR = Path(os.getenv("ASHARE_EVENT_DATA_DIR", "/data"))
DB_PATH = Path(os.getenv("ASHARE_EVENT_DB", str(DATA_DIR / "ashare_event_state.db")))
RUNS_DIR = Path(os.getenv("ASHARE_EVENT_RUNS", str(DATA_DIR / "runs")))

store = SQLiteStateStore(DB_PATH)
engine = MarketDayEngine(store)
controller = WorkflowController(engine)


def _load(task_id: str):
    state = store.load(task_id)
    if state is None:
        raise ValueError(f"task not found: {task_id}")
    return state


def _require_stage(state, stage: Stage):
    if state.stage != stage:
        raise ValueError(f"task {state.contract.task_id} is at {state.stage.value}; expected {stage.value}")


def _save_advance(state):
    store.save(state)
    return controller.advance(state)


def _gate(state, name: str, decision: GateDecision, revision_key: str | None = None):
    status = GateStatus(decision.status)
    state.set_gate(name, status, decision.evidence, "; ".join(decision.defects + decision.remaining_boundaries))
    if revision_key and decision.revision_target:
        state.working[revision_key] = decision.revision_target
    if status == GateStatus.FAIL:
        return engine.block(state, f"{name} failed: {'; '.join(decision.defects)}")
    return _save_advance(state)


def _summary(state, detail: bool = False) -> dict[str, Any]:
    out = {
        "task_id": state.contract.task_id,
        "status": "BLOCKED" if state.stage == Stage.BLOCKED else ("COMPLETE" if state.stage == Stage.COMPLETE else ("FROZEN" if state.stage == Stage.FROZEN else "IN_PROGRESS")),
        "current_stage": state.stage.value,
        "trading_date": state.contract.trading_date,
        "freeze_hash": state.frozen_hash,
        "gate_status": {k: v.status.value for k, v in state.gates.items()},
        "blocked_reason": state.blocked_reason,
        "updated_at": state.updated_at.isoformat(),
        "next_action": _next_action(state),
    }
    if detail:
        out["contract"] = state.contract.model_dump(mode="json")
        out["gates"] = {k: v.model_dump(mode="json") for k, v in state.gates.items()}
        out["artifacts"] = {k.value: v.model_dump(mode="json") for k, v in state.artifacts.items()}
    return out


def _write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _record_artifact(state, kind: ArtifactKind, path: Path) -> None:
    state.artifacts[kind] = Artifact(kind=kind, path=str(path), exists=path.is_file(), sha256=sha256_file(path) if path.is_file() else None)


def _build_pick_report(state) -> Path:
    plan = state.working.get("execution_plan") or {}
    recall = state.working.get("recall_pool") or {}
    market = state.working.get("market_structure") or {}
    lines = [
        f"# A-share Premarket Pick Report | {state.contract.trading_date}", "",
        f"Frozen hash: `{state.frozen_hash or ''}`",
        f"Main-board only: {state.contract.mainboard_only}",
        f"Auction used: {state.contract.auction_used}",
        f"Execution assurance: **{plan.get('assurance','DEGRADED')}**",
        f"Preferred microstructure observed: {bool(plan.get('preferred_microstructure_observed'))}", "",
        "## First-read answer", str(plan.get("first_read_answer") or "N/A"), "", "## Execution candidates",
    ]
    candidates = plan.get("candidates") or []
    if not candidates:
        lines.append("- NO TRADE / no executable candidate accepted.")
    for row in candidates:
        lines.extend([
            f"- **{row.get('name','')} ({row.get('ticker','')})** | {row.get('slot','')}",
            f"  - Strategy: {row.get('strategy','')}",
            f"  - Trigger: {'; '.join(row.get('trigger') or [])}",
            f"  - Invalidation: {'; '.join(row.get('invalidation') or [])}",
            f"  - Why this: {'; '.join(row.get('why_this') or [])}",
            f"  - Why not peers: {'; '.join(row.get('why_not_peers') or []) or 'N/A'}",
        ])
    lines.extend(["", "## Risk / buyability gate"])
    for row in plan.get("risk_assessments") or []:
        lines.extend([
            f"- **{row.get('ticker','')}** | {row.get('decision','')} | assurance={row.get('assurance','')}",
            f"  - Risk flags: {'; '.join(row.get('risk_flags') or []) or 'None'}",
            f"  - Hard veto: {'; '.join(row.get('hard_veto_reasons') or []) or 'None'}",
            f"  - Evidence: {'; '.join(row.get('evidence_refs') or [])}",
        ])
    if not plan.get("risk_assessments"):
        lines.append("- No risk assessments recorded (final audit should not accept a non-empty U1 without them).")
    market_risk_lines = [f"- {x}" for x in (plan.get("market_risk_flags") or [])] or ["- None recorded"]
    lines.extend([
        "", "## Market-level risk flags", *market_risk_lines,
        "", "## No-trade conditions", *[f"- {x}" for x in (plan.get("no_trade_conditions") or [])],
        "", "## Backup chain", *[f"- {x}" for x in (plan.get("backup_chain") or [])],
        "", "## Recall boundary",
        f"- U0 tickers: {len(recall.get('u0_tickers') or [])}",
        f"- U1 candidates: {len(recall.get('u1_candidates') or [])}",
        f"- Height records: {len(market.get('heights') or [])}",
        f"- Role hypotheses: {len(market.get('roles') or [])}", "",
        "> This report is a frozen recommendation/research artifact, not a guarantee of return. Post-close facts must never be written back into it.",
    ])
    return _write_text(RUNS_DIR / state.contract.task_id / "PICK_REPORT.md", "\n".join(lines) + "\n")


def _build_final_artifacts(state) -> tuple[Path, Path]:
    outcomes = state.working.get("review_outcomes") or {}
    attribution = state.working.get("attribution") or {}
    grade = state.working.get("recall_grading") or {}
    selection = grade.get("selection_quality") or {}
    learning = state.working.get("learning_audit") or {}
    proposal = state.working.get("rule_proposal") or {}
    replay = state.working.get("replay_eval") or {}
    review_lines = [
        f"# A-share Post-close Review | {state.contract.trading_date}", "",
        f"Frozen hash verified: `{state.frozen_hash or ''}`", "",
        "## Outcome reconciliation",
        f"- Outcome records: {len(outcomes.get('outcomes') or [])}",
        f"- Pool counts: {json.dumps(outcomes.get('pool_counts') or {}, ensure_ascii=False)}", "",
        "## Research recall quality",
        f"- Knowable limit-ups: {grade.get('knowable_limit_up_total', 0)}",
        f"- U0 hits / recall: {grade.get('u0_hits', 0)} / {grade.get('u0_recall', 0)}",
        f"- U1 hits / recall: {grade.get('u1_hits', 0)} / {grade.get('u1_recall', 0)}",
        f"- Miss counts: {json.dumps(grade.get('miss_counts') or {}, ensure_ascii=False)}", "",
        "## Final-selection / execution quality",
        f"- Final slots: {selection.get('candidate_slots_total', 0)}",
        f"- Activated / not activated: {selection.get('activated_total', 0)} / {selection.get('not_activated_total', 0)}",
        f"- Activated positive rate: {selection.get('activated_positive_rate', 0)}",
        f"- Activated downside rate: {selection.get('activated_downside_rate', 0)}",
        f"- Execution feasibility rate: {selection.get('execution_feasibility_rate', 0)}",
        f"- Activated outcomes: limit_up={selection.get('activated_limit_up_hits', 0)}, strong={selection.get('activated_strong_hits', 0)}, broken={selection.get('activated_broken', 0)}, limit_down={selection.get('activated_limit_down', 0)}, other={selection.get('activated_other', 0)}", "",
        "## Attribution coverage",
        f"- Actual limit-ups attributed: {len(attribution.get('actual_limit_ups') or [])}",
        f"- Broken boards attributed: {len(attribution.get('broken_boards') or [])}",
        f"- Limit-downs attributed: {len(attribution.get('limit_downs') or [])}", "",
        "## Learning boundary",
        f"- Errors: {len(learning.get('errors') or [])}",
        f"- Repeated errors: {len(learning.get('repeated_errors') or [])}",
        f"- Candidate hypotheses: {len(learning.get('candidate_hypotheses') or [])}",
        f"- Rule proposal: {proposal.get('status', 'N/A')} {proposal.get('rule_id') or ''}",
        f"- Replay verdict: {replay.get('status', 'N/A')}", "",
        "> Review starts from the immutable premarket cassette. Post-close facts are explanatory evidence only and may not rewrite premarket reasoning.",
    ]
    review_path = _write_text(RUNS_DIR / state.contract.task_id / "REVIEW_REPORT.md", "\n".join(review_lines) + "\n")
    learning_payload = {
        "trading_date": state.contract.trading_date,
        "frozen_hash": state.frozen_hash,
        "recall_grading": grade,
        "learning_audit": learning,
        "rule_proposal": proposal,
        "replay_eval": replay,
        "stockbase_writeback_refs": state.working.get("review_writeback_refs", []),
        "stockbase_writeback_notes": state.working.get("review_writeback_notes", []),
    }
    learning_path = write_json(RUNS_DIR / state.contract.task_id / "LEARNING_REPORT.json", learning_payload)
    return review_path, learning_path


def _next_action(state) -> str:
    return {
        Stage.FREEZE: "submit freeze card before dynamic premarket research is finalized",
        Stage.SOURCE_COMPLETION: "retrieve P01-P09 directly, reconcile LINK-ALL/images, and reuse previous review five pools",
        Stage.SOURCE_AUDIT: "independently audit source completion",
        Stage.EVENT_LEDGER: "submit all-news event ledger including negative/rumor/disproved/no-trade events",
        Stage.INDUSTRY_RESEARCH: "build L0-L5+ industry graphs and exhaustive node mappings",
        Stage.STOCKBASE_RECALL: "record current StockBase READ_ONLY context and recall receipt",
        Stage.UNIVERSE_AUDIT: "audit node exhaustion and mapping omissions",
        Stage.MARKET_STRUCTURE: "submit height facts plus evidence-backed role hypotheses/rotation maps",
        Stage.RECALL_POOL: "submit U0/U1 recall-first pool without leader-based early pruning",
        Stage.EXECUTION_PLAN: "adjudicate opportunity views, risk-assess every U1 candidate, enforce hard vetoes, then submit U3/NO TRADE with assurance",
        Stage.PREMARKET_AUDIT: "run independent premarket red-team audit; PASS freezes snapshot",
        Stage.FROZEN: "premarket snapshot is immutable; after close call start_postclose_review",
        Stage.REVIEW_OUTCOMES: "submit reconciled post-close outcomes plus trigger/execution-feasibility evidence for final U3",
        Stage.ATTRIBUTION: "attribute every in-scope limit-up and key failures against the frozen snapshot",
        Stage.RECALL_GRADING: "grade research recall separately from final-selection activation/outcome/execution feasibility",
        Stage.LEARNING_AUDIT: "identify repeatable errors without changing rules yet",
        Stage.RULE_PROPOSAL: "submit one bounded rule proposal or explicit N_A",
        Stage.REPLAY_EVAL: "replay proposed rule across frozen historical cases using recall + selection + execution metrics; no one-day promotion",
        Stage.FINAL_AUDIT: "independent final audit and writeback boundary check",
        Stage.COMPLETE: "market-day loop complete",
        Stage.BLOCKED: "repair the recorded dependency/contract defect; do not silently bypass it",
        Stage.INTAKE: "initialize runtime",
    }.get(state.stage, "follow runtime stage contract")


def start_market_day(trading_date: str, prompt: str, stockbase_ref: str | None = None, prior_review_ref: str | None = None, mode: str = "LIVE_DAY") -> dict:
    state = engine.start(TaskContract(trading_date=trading_date, prompt=prompt, stockbase_ref=stockbase_ref, prior_review_ref=prior_review_ref, mode=TaskMode(mode)))
    return _summary(controller.advance(state))


def get_market_day(task_id: str, detail: bool = True) -> dict:
    return _summary(_load(task_id), detail)


def list_recent_market_days(limit: int = 20, include_complete: bool = False) -> list[dict]:
    states = store.list_recent(limit)
    if not include_complete:
        states = [s for s in states if s.stage != Stage.COMPLETE]
    return [_summary(s) for s in states]


def record_governance_context(task_id: str, refs: list[str], notes: list[str] | None = None) -> dict:
    state = _load(task_id); _require_stage(state, Stage.FREEZE)
    state.working["governance_refs"] = list(dict.fromkeys(refs))
    state.working["governance_notes"] = notes or []
    state.add_trace("GOVERNANCE_CONTEXT", f"refs={len(refs)}")
    store.save(state)
    return _summary(state)


def submit_freeze_card(task_id: str, payload: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.FREEZE)
    card = FreezeCard.model_validate(payload)
    if card.trading_date != state.contract.trading_date:
        raise ValueError("FreezeCard trading_date mismatch")
    if card.timezone != state.contract.timezone:
        raise ValueError("FreezeCard timezone mismatch")
    if card.auction_used != state.contract.auction_used:
        raise ValueError("auction_used must match TaskContract")
    state.working["freeze_card"] = card.model_dump(mode="json")
    state.set_gate("freeze_card", GateStatus.PASS, [card.max_public_info_time.isoformat(), card.max_market_data_time.isoformat()])
    return _summary(_save_advance(state))


def submit_source_completion(task_id: str, payload: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.SOURCE_COMPLETION)
    pkg = SourceCompletionPackage.model_validate(payload)
    errors = audit_source_completion(pkg)
    state.working["source_completion"] = pkg.model_dump(mode="json")
    state.set_gate("source_completion", GateStatus.PASS if not errors else GateStatus.REVISE, [f"receipts={len(pkg.receipts)}"], "; ".join(errors))
    if errors:
        store.save(state); return _summary(state)
    return _summary(_save_advance(state))


def submit_source_audit(task_id: str, decision: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.SOURCE_AUDIT)
    return _summary(_gate(state, "source_audit", GateDecision.model_validate(decision)))


def submit_event_ledger(task_id: str, payload: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.EVENT_LEDGER)
    pkg = EventLedgerPackage.model_validate(payload)
    freeze = FreezeCard.model_validate(state.working["freeze_card"])
    errors = audit_event_times(pkg, freeze.max_public_info_time)
    if errors:
        state.set_gate("event_ledger", GateStatus.REVISE, [f"events={len(pkg.events)}"], "; ".join(errors)); store.save(state); return _summary(state)
    state.working["event_ledger"] = pkg.model_dump(mode="json")
    state.set_gate("event_ledger", GateStatus.PASS, [f"events={len(pkg.events)}", f"evidence={len(pkg.evidence_ledger)}"])
    return _summary(_save_advance(state))


def submit_industry_research(task_id: str, payload: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.INDUSTRY_RESEARCH)
    pkg = IndustryResearchPackage.model_validate(payload)
    state.working["industry_research"] = pkg.model_dump(mode="json")
    state.set_gate("industry_research", GateStatus.PASS, [f"nodes={len(pkg.nodes)}", f"mappings={len(pkg.mappings)}", f"sweeps={pkg.sweeps_completed}"])
    return _summary(_save_advance(state))


def record_stockbase_context(task_id: str, payload: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.STOCKBASE_RECALL)
    ctx = StockBaseContext.model_validate(payload)
    if ctx.mode != "READ_ONLY":
        raise ValueError("premarket StockBase mode must be READ_ONLY")
    state.working["stockbase_context"] = ctx.model_dump(mode="json")
    state.set_gate("stockbase_recall", GateStatus.PASS, [ctx.ref, ctx.version, "READ_ONLY"])
    return _summary(_save_advance(state))


def submit_universe_audit(task_id: str, universe: dict, decision: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.UNIVERSE_AUDIT)
    pkg = UniversePackage.model_validate(universe)
    state.working["universe"] = pkg.model_dump(mode="json")
    d = GateDecision.model_validate(decision)
    if d.status == "PASS" and (not pkg.all_event_nodes_exhausted or pkg.omitted_known_candidates):
        raise ValueError("universe audit cannot PASS with unexhausted nodes or known omitted candidates")
    return _summary(_gate(state, "universe_audit", d, "universe_revision_target"))


def submit_market_structure(task_id: str, payload: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.MARKET_STRUCTURE)
    pkg = MarketStructurePackage.model_validate(payload)
    state.working["market_structure"] = pkg.model_dump(mode="json")
    state.set_gate("market_structure", GateStatus.PASS, [f"heights={len(pkg.heights)}", f"roles={len(pkg.roles)}"])
    return _summary(_save_advance(state))


def submit_recall_pool(task_id: str, payload: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.RECALL_POOL)
    pkg = RecallPoolPackage.model_validate(payload)
    state.working["recall_pool"] = pkg.model_dump(mode="json")
    state.set_gate("recall_pool", GateStatus.PASS, [f"u0={len(pkg.u0_tickers)}", f"u1={len(pkg.u1_candidates)}", "recall-first"])
    return _summary(_save_advance(state))


def submit_execution_plan(task_id: str, payload: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.EXECUTION_PLAN)
    plan = ExecutionPlan.model_validate(payload)
    state.working["execution_plan"] = plan.model_dump(mode="json")
    state.set_gate("execution_plan", GateStatus.PASS, [f"slots={len(plan.candidates)}", f"risk_assessments={len(plan.risk_assessments)}", f"assurance={plan.assurance}", "NO_TRADE defined"])
    return _summary(_save_advance(state))


def submit_premarket_audit(task_id: str, decision: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.PREMARKET_AUDIT)
    result = _gate(state, "premarket_audit", GateDecision.model_validate(decision), "premarket_revision_target")
    if result.stage == Stage.FROZEN:
        outdir = RUNS_DIR / task_id; outdir.mkdir(parents=True, exist_ok=True)
        snap = write_json(outdir / "PREMARKET_SNAPSHOT.json", {"contract": result.contract.model_dump(mode="json"), "working": {k: result.working.get(k) for k in result.working if k not in {"review_outcomes", "attribution", "recall_grading", "learning_audit", "rule_proposal", "replay_eval"}}, "frozen_hash": result.frozen_hash})
        _record_artifact(result, ArtifactKind.PREMARKET_SNAPSHOT_JSON, snap)
        pick_report = _build_pick_report(result)
        _record_artifact(result, ArtifactKind.PICK_REPORT_MD, pick_report)
        store.save(result)
    return _summary(result, detail=True)


def start_postclose_review(task_id: str) -> dict:
    state = _load(task_id); _require_stage(state, Stage.FROZEN)
    engine.assert_frozen_unchanged(state)
    return _summary(engine.transition(state, Stage.REVIEW_OUTCOMES, reason="post-close review started from immutable frozen snapshot"))


def submit_market_outcomes(task_id: str, payload: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.REVIEW_OUTCOMES); engine.assert_frozen_unchanged(state)
    pkg = OutcomePackage.model_validate(payload)
    state.working["review_outcomes"] = pkg.model_dump(mode="json")
    activated = sum(1 for row in pkg.outcomes if row.trigger_observed is True)
    state.set_gate("review_outcomes", GateStatus.PASS, [f"outcomes={len(pkg.outcomes)}", f"activated_u3={activated}", json.dumps(pkg.pool_counts, ensure_ascii=False)])
    return _summary(_save_advance(state))


def submit_attribution(task_id: str, payload: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.ATTRIBUTION); engine.assert_frozen_unchanged(state)
    pkg = AttributionPackage.model_validate(payload)
    state.working["attribution"] = pkg.model_dump(mode="json")
    state.set_gate("attribution", GateStatus.PASS, [f"limitups={len(pkg.actual_limit_ups)}", f"broken={len(pkg.broken_boards)}"])
    return _summary(_save_advance(state))


def submit_recall_grading(task_id: str, payload: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.RECALL_GRADING); engine.assert_frozen_unchanged(state)
    grade = RecallGrade.model_validate(payload)
    if grade.u0_hits > grade.knowable_limit_up_total or grade.u1_hits > grade.knowable_limit_up_total:
        raise ValueError("recall hits cannot exceed knowable limit-up count")
    state.working["recall_grading"] = grade.model_dump(mode="json")
    q = grade.selection_quality
    state.set_gate("recall_grading", GateStatus.PASS, [f"u0_recall={grade.u0_recall:.4f}", f"u1_recall={grade.u1_recall:.4f}", f"activated_positive_rate={q.activated_positive_rate:.4f}", f"activated_downside_rate={q.activated_downside_rate:.4f}", f"execution_feasibility_rate={q.execution_feasibility_rate:.4f}"])
    return _summary(_save_advance(state))


def submit_learning_audit(task_id: str, payload: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.LEARNING_AUDIT); engine.assert_frozen_unchanged(state)
    audit = LearningAudit.model_validate(payload)
    state.working["learning_audit"] = audit.model_dump(mode="json")
    state.set_gate("learning_audit", GateStatus.PASS, [f"errors={len(audit.errors)}", f"hypotheses={len(audit.candidate_hypotheses)}"])
    return _summary(_save_advance(state))


def submit_rule_proposal(task_id: str, payload: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.RULE_PROPOSAL); engine.assert_frozen_unchanged(state)
    proposal = RuleProposal.model_validate(payload)
    state.working["rule_proposal"] = proposal.model_dump(mode="json")
    state.set_gate("rule_proposal", GateStatus.PASS, [proposal.status, proposal.rule_id or "N_A"])
    return _summary(_save_advance(state))


def submit_replay_eval(task_id: str, payload: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.REPLAY_EVAL); engine.assert_frozen_unchanged(state)
    replay = ReplayEval.model_validate(payload)
    proposal = RuleProposal.model_validate(state.working["rule_proposal"])
    if proposal.status == "PROPOSE" and replay.status == "PASS":
        if replay.future_contamination_detected:
            raise ValueError("rule cannot pass replay with future contamination")
        if len(replay.case_refs) < 5 or len(set(replay.regimes)) < 2 or replay.positive_samples < 1 or replay.negative_samples < 1:
            raise ValueError("rule promotion replay requires >=5 cases, >=2 regimes, positive and negative samples")
        if replay.regressions:
            raise ValueError("rule promotion replay cannot PASS with regressions")
    state.working["replay_eval"] = replay.model_dump(mode="json")
    state.set_gate("replay_eval", GateStatus.PASS, [replay.status, f"cases={len(replay.case_refs)}", f"regimes={len(set(replay.regimes))}"])
    return _summary(_save_advance(state))


def record_review_writeback(task_id: str, status: str, refs: list[str] | None = None, notes: list[str] | None = None) -> dict:
    state = _load(task_id); _require_stage(state, Stage.FINAL_AUDIT); engine.assert_frozen_unchanged(state)
    if status not in {"PASS", "N_A"}:
        raise ValueError("review writeback status must be PASS or N_A")
    receipts = list(dict.fromkeys(refs or [])); note_list = notes or []
    if status == "PASS" and not receipts:
        raise ValueError("PASS review writeback requires receipt refs")
    if status == "N_A" and not note_list:
        raise ValueError("N_A review writeback requires a reason")
    state.working["review_writeback_refs"] = receipts
    state.working["review_writeback_notes"] = note_list
    state.set_gate("stockbase_writeback", GateStatus(status), receipts or ["explicit N_A"], "; ".join(note_list))
    state.add_trace("STOCKBASE_WRITEBACK", f"status={status}; refs={len(receipts)}")
    store.save(state)
    return _summary(state)


def submit_final_audit(task_id: str, decision: dict) -> dict:
    state = _load(task_id); _require_stage(state, Stage.FINAL_AUDIT); engine.assert_frozen_unchanged(state)
    d = GateDecision.model_validate(decision)
    if d.status == "PASS" and state.gates.get("stockbase_writeback", None) is None:
        raise ValueError("record_review_writeback PASS/N_A before final audit PASS")
    if d.status == "REVISE" and d.revision_target not in {"ATTRIBUTION", "LEARNING_AUDIT", "REPLAY_EVAL"}:
        raise ValueError("final audit REVISE target must be ATTRIBUTION, LEARNING_AUDIT, or REPLAY_EVAL")
    state.set_gate("final_audit", GateStatus(d.status), d.evidence, "; ".join(d.defects + d.remaining_boundaries))
    if d.revision_target:
        state.working["final_revision_target"] = d.revision_target
    if d.status == "FAIL":
        return _summary(engine.block(state, "final audit failed"))
    if d.status == "PASS":
        review_path, learning_path = _build_final_artifacts(state)
        _record_artifact(state, ArtifactKind.REVIEW_REPORT_MD, review_path)
        _record_artifact(state, ArtifactKind.LEARNING_REPORT_JSON, learning_path)
        store.save(state)
    else:
        store.save(state)
    try:
        state = controller.advance(state)
    except WorkflowError as exc:
        state = engine.block(state, str(exc))
    return _summary(state, detail=True)
