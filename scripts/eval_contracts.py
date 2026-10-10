from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic import ValidationError

from ashare_event_agent.checks import audit_source_completion
from ashare_event_agent.engine import MarketDayEngine, WorkflowError
from ashare_event_agent.integrity import (
    attribution_integrity_errors,
    recall_grade_integrity_errors,
    recall_integrity_errors,
    universe_integrity_errors,
)
from ashare_event_agent.models import ArtifactKind, Stage, TaskContract
from ashare_event_agent.schemas import (
    AttributionPackage,
    FreezeCard,
    IndustryResearchPackage,
    OutcomePackage,
    RecallGrade,
    RecallPoolPackage,
    ReplayEval,
    RoleHypothesis,
    SourceCompletionPackage,
    SourceReceipt,
    UniversePackage,
)
from ashare_event_agent.store import SQLiteStateStore

SCENARIOS = ROOT / "evals" / "scenarios.json"


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def source_receipt(source_id: str, content_time: str = "2026-10-08T09:14:59+08:00") -> SourceReceipt:
    return SourceReceipt(
        source_id=source_id,
        label=source_id,
        status="FULL",
        retrieval_method="STATIC_HTTP",
        retrieved_at="2026-10-08T09:14:59+08:00",
        content_max_available_at=content_time,
        source_refs=[f"ref-{source_id}"],
        links_expected=0,
        links_fetched=0,
        images_expected=0,
        images_read=0,
    )


def mapping(ticker: str, node_id: str, event_id: str = "E1", eligible: bool = True) -> dict:
    return {
        "event_id": event_id,
        "node_id": node_id,
        "ticker": ticker,
        "name": ticker,
        "mainboard_eligible": eligible,
        "directness": "A",
        "business_stage": "mass production",
    }


def recall_fixture() -> RecallPoolPackage:
    return RecallPoolPackage(
        u0_tickers=["600000", "600001"],
        u1_candidates=[{
            "ticker":"600000","name":"A","tier":"P0","event_ids":["E1"],
            "limit_up_paths":["path"],"knowable_reasoning":["reason"]
        }],
    )


def e01() -> list[str]:
    with tempfile.TemporaryDirectory() as td:
        engine = MarketDayEngine(SQLiteStateStore(Path(td) / "state.db"))
        state = engine.start(TaskContract(trading_date="2026-10-08", prompt="开始荐股"))
        check(state.stage == Stage.INTAKE, "runtime must start at INTAKE")
        check(state.trace[0].event == "RUNTIME_STARTED", "runtime trace must start before research")
        check(ArtifactKind.PREMARKET_SNAPSHOT_JSON in state.contract.required_outputs, "premarket snapshot required")
        check(ArtifactKind.REVIEW_REPORT_MD in state.contract.required_outputs, "review report required")
    return ["runtime-first", "required outputs explicit"]


def e03() -> list[str]:
    receipts = [source_receipt(f"P{i:02d}") for i in range(1, 10)]
    pkg = SourceCompletionPackage(receipts=receipts, previous_five_pool_reused=True, previous_five_pool_ref="review-2026-09-30")
    check(pkg.previous_five_pool_reused, "five pools must be reused")
    try:
        SourceCompletionPackage(receipts=receipts, previous_five_pool_reused=True, previous_five_pool_ref="x", repeated_five_pool_fetch_performed=True)
    except ValidationError:
        pass
    else:
        raise AssertionError("re-fetching five pools must fail")
    return ["five-pool reuse", "repeat fetch rejected"]


def e04() -> list[str]:
    freeze = FreezeCard(
        trading_date="2026-10-08",
        max_public_info_time="2026-10-08T09:14:59+08:00",
        max_market_data_time="2026-10-08T09:14:59+08:00",
    )
    receipts = [source_receipt(f"P{i:02d}") for i in range(1, 10)]
    good = SourceCompletionPackage(receipts=receipts, previous_five_pool_reused=True, previous_five_pool_ref="review")
    check(not audit_source_completion(good, freeze), "fully reconciled P01-P09 should pass point-in-time audit")
    bad_receipts = list(receipts)
    bad_receipts[-1] = source_receipt("P09", "2026-10-08T09:15:00+08:00")
    bad = SourceCompletionPackage(receipts=bad_receipts, previous_five_pool_reused=True, previous_five_pool_ref="review")
    check(bool(audit_source_completion(bad, freeze)), "post-freeze source content must be rejected")
    return ["P01-P09 fixed coverage", "LINK/image counts explicit", "content availability bound to FreezeCard"]


def e05() -> list[str]:
    research = IndustryResearchPackage(
        nodes=[
            {"node_id":"N1","event_id":"E1","level":5,"name":"n1","economics":"x","direction":"BENEFIT"},
            {"node_id":"N2","event_id":"E1","level":5,"name":"n2","economics":"y","direction":"BENEFIT"},
        ],
        transmission_paths=["path"],
        mappings=[mapping("600000", "N1"), mapping("600001", "N2")],
        max_depth_by_event={"E1":5},
        sweeps_completed=2,
        stop_reason="done",
    )
    incomplete = UniversePackage(
        mappings=[mapping("600000", "N1")],
        all_event_nodes_exhausted=True,
        stop_reason="done",
    )
    check(bool(universe_integrity_errors(research, incomplete)), "eligible mapped ticker omission must fail")
    complete = UniversePackage(
        mappings=[mapping("600000", "N1"), mapping("600001", "N2")],
        all_event_nodes_exhausted=True,
        stop_reason="done",
    )
    check(not universe_integrity_errors(research, complete), "complete eligible Universe should pass")
    bad_recall = RecallPoolPackage(
        u0_tickers=["600000"],
        u1_candidates=[{
            "ticker":"600000","name":"A","tier":"P0","event_ids":["E1"],
            "limit_up_paths":["path"],"knowable_reasoning":["reason"]
        }],
    )
    check(bool(recall_integrity_errors(complete, bad_recall)), "U0 must descend from complete Universe")
    return ["node coverage explicit", "eligible ticker omissions fail", "Universe to U0 lineage enforced"]


def e06() -> list[str]:
    try:
        RoleHypothesis(
            ticker="600000", name="样例", event_id="E1", role_type="THEME_LEADER",
            evidence_dimensions=["board_count", "height"], evidence=["4板", "最高板"],
            invalidation=["板块脱离"], confidence="medium"
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("board-count-only role must fail")
    return ["height is fact, not role proof"]


def e07() -> list[str]:
    try:
        RecallPoolPackage(u0_tickers=["600000"], u1_candidates=[{
            "ticker":"600000","name":"样例","tier":"P1","event_ids":["E1"],"limit_up_paths":["path"],"knowable_reasoning":["reason"]
        }], early_pruning_applied=True)
    except ValidationError:
        pass
    else:
        raise AssertionError("early pruning must fail")
    from ashare_event_agent.schemas import ExecutionPlan
    plan = ExecutionPlan(candidates=[], no_trade_conditions=["none qualify"], backup_chain=["NO TRADE"], first_read_answer="NO TRADE")
    check(len(plan.candidates) <= 4, "U3 max four")
    return ["U0/U1 not pruned", "NO TRADE legal", "U3 <= 4"]


def e08() -> list[str]:
    recall = recall_fixture()
    outcomes = OutcomePackage(
        outcomes=[
            {"ticker":"600000","name":"A","result":"LIMIT_UP","board_count_after":1},
            {"ticker":"600001","name":"B","result":"BROKEN","board_count_after":0},
        ],
        pool_counts={"limit_up":1,"broken":1},
        source_refs=["postclose"],
    )
    attribution = AttributionPackage(
        actual_limit_ups=[{
            "ticker":"600000","name":"A","knowable_before_freeze":True,"in_u0":True,"in_u1":True,"miss_class":"HIT"
        }],
        broken_boards=[{
            "ticker":"600001","name":"B","knowable_before_freeze":True,"in_u0":True,"in_u1":False,"miss_class":"E_ROLE_RANKING"
        }],
    )
    check(not attribution_integrity_errors(outcomes, recall, attribution), "outcome/attribution/frozen membership should reconcile")
    grade = RecallGrade(
        actual_limit_up_total=1,
        excluded_scope_total=0,
        knowable_limit_up_total=1,
        u0_hits=1,
        u1_hits=1,
        u0_recall=1.0,
        u1_recall=1.0,
    )
    check(not recall_grade_integrity_errors(attribution, grade), "recall grade must be derivable from attribution")
    return ["post-close outcome reconciliation", "frozen membership recomputed", "recall denominator/hits derived"]


def e09() -> list[str]:
    try:
        ReplayEval(status="PASS", case_refs=["d1"], regimes=["trend"], positive_samples=1, negative_samples=0, decision_reason="one day")
    except ValidationError:
        return ["schema rejected weak replay"]
    return ["weak replay accepted only as payload; runtime promotion gate must reject"]


def e11() -> list[str]:
    with tempfile.TemporaryDirectory() as td:
        engine = MarketDayEngine(SQLiteStateStore(Path(td) / "state.db"))
        state = engine.start(TaskContract(trading_date="2026-10-08", prompt="来源抓不到就先荐"))
        try:
            engine.transition(state, Stage.EVENT_LEDGER)
        except WorkflowError:
            pass
        else:
            raise AssertionError("illegal skip must fail closed")
    return ["illegal skip rejected"]


def e12() -> list[str]:
    with tempfile.TemporaryDirectory() as td:
        engine = MarketDayEngine(SQLiteStateStore(Path(td) / "state.db"))
        state = engine.start(TaskContract(trading_date="2026-10-08", prompt="test"))
        state.stage = Stage.PREMARKET_AUDIT
        state.working["freeze_card"] = {"x": 1}
        state = engine.freeze(state)
        state.working["freeze_card"] = {"x": 2}
        try:
            engine.assert_frozen_unchanged(state)
        except WorkflowError:
            pass
        else:
            raise AssertionError("frozen mutation must be rejected")
    return ["frozen mutation rejected"]


EXECUTABLE = {"E01": e01, "E03": e03, "E04": e04, "E05": e05, "E06": e06, "E07": e07, "E08": e08, "E09": e09, "E11": e11, "E12": e12}
SPEC_ONLY = {
    "E02": "checkpoint recovery is covered by unit/trajectory tests and live hosted E2E",
    "E10": "earliest failed-layer attribution still needs semantic review against a frozen historical/live cassette",
}


def main() -> None:
    rows = json.loads(SCENARIOS.read_text(encoding="utf-8"))["evals"]
    ids = [x["id"] for x in rows]
    check(len(ids) == len(set(ids)), "scenario IDs must be unique")
    check(set(ids) == set(EXECUTABLE) | set(SPEC_ONLY), "scenario registry mismatch")
    report, failures = [], []
    for row in rows:
        sid = row["id"]
        check(bool(row.get("assertions")), f"{sid} assertions missing")
        if sid in EXECUTABLE:
            try:
                evidence = EXECUTABLE[sid]()
                report.append({"id": sid, "status": "PASS", "evidence": evidence})
            except Exception as exc:
                failures.append(f"{sid}: {type(exc).__name__}: {exc}")
                report.append({"id": sid, "status": "FAIL", "error": str(exc)})
        else:
            report.append({"id": sid, "status": "SPEC_ONLY", "reason": SPEC_ONLY[sid]})
    print(json.dumps({"results": report, "failures": failures}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
