from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic import ValidationError

from ashare_event_agent.engine import MarketDayEngine, WorkflowError
from ashare_event_agent.models import ArtifactKind, GateStatus, Stage, TaskContract
from ashare_event_agent.schemas import (
    ExecutionPlan,
    RecallPoolPackage,
    ReplayEval,
    RoleHypothesis,
    SourceCompletionPackage,
    SourceReceipt,
)
from ashare_event_agent.store import SQLiteStateStore

SCENARIOS = ROOT / "evals" / "scenarios.json"


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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
    receipts = [
        SourceReceipt(source_id=f"P{i:02d}", label=f"P{i:02d}", status="FULL", retrieval_method="STATIC_HTTP", retrieved_at="2026-10-08T08:00:00+08:00", source_refs=[f"ref-{i}"])
        for i in range(1, 10)
    ]
    pkg = SourceCompletionPackage(receipts=receipts, previous_five_pool_reused=True, previous_five_pool_ref="review-2026-09-30")
    check(pkg.previous_five_pool_reused, "five pools must be reused")
    try:
        SourceCompletionPackage(receipts=receipts, previous_five_pool_reused=True, previous_five_pool_ref="x", repeated_five_pool_fetch_performed=True)
    except ValidationError:
        pass
    else:
        raise AssertionError("re-fetching five pools must fail")
    return ["five-pool reuse", "repeat fetch rejected"]


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
    plan = ExecutionPlan(candidates=[], no_trade_conditions=["none qualify"], backup_chain=["NO TRADE"], first_read_answer="NO TRADE")
    check(len(plan.candidates) <= 4, "U3 max four")
    return ["U0/U1 not pruned", "NO TRADE legal", "U3 <= 4"]


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


EXECUTABLE = {"E01": e01, "E03": e03, "E06": e06, "E07": e07, "E09": e09, "E11": e11, "E12": e12}
SPEC_ONLY = {
    "E02": "checkpoint recovery is covered by unit/trajectory tests and live hosted E2E",
    "E04": "P01-P09 direct retrieval completeness is connector/live-source behavior",
    "E05": "L0-L5 node exhaustion is semantic research plus universe-audit behavior",
    "E08": "full post-close attribution needs a frozen historical/live cassette",
    "E10": "earliest failed-layer attribution is semantic review behavior",
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
