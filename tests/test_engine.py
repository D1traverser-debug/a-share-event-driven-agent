import pytest

from ashare_event_agent.engine import MarketDayEngine, WorkflowError, payload_hash, premarket_payload
from ashare_event_agent.models import GateStatus, Stage, TaskContract
from ashare_event_agent.store import SQLiteStateStore


def test_illegal_stage_skip_fails(tmp_path):
    engine = MarketDayEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = engine.start(TaskContract(trading_date="2026-10-08", prompt="开始荐股"))
    with pytest.raises(WorkflowError):
        engine.transition(state, Stage.EVENT_LEDGER)


def test_freeze_hash_detects_premarket_mutation(tmp_path):
    engine = MarketDayEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = engine.start(TaskContract(trading_date="2026-10-08", prompt="x"))
    state.stage = Stage.PREMARKET_AUDIT
    state.working["freeze_card"] = {"x": 1}
    state.working["source_completion"] = {"x": 2}
    state = engine.freeze(state)
    engine.assert_frozen_unchanged(state)
    state.working["source_completion"]["x"] = 3
    with pytest.raises(WorkflowError, match="mutated"):
        engine.assert_frozen_unchanged(state)


def test_complete_requires_all_contract_outputs(tmp_path):
    engine = MarketDayEngine(SQLiteStateStore(tmp_path / "state.db"))
    state = engine.start(TaskContract(trading_date="2026-10-08", prompt="test"))
    state.stage = Stage.FINAL_AUDIT
    state.working["freeze_card"] = {"trading_date": "2026-10-08"}
    state.frozen_hash = payload_hash(premarket_payload(state))
    state.set_gate("final_audit", GateStatus.PASS, ["ok"])
    with pytest.raises(WorkflowError, match="missing required outputs"):
        engine.complete(state)
