from ashare_event_agent.controller import WorkflowController
from ashare_event_agent.engine import MarketDayEngine
from ashare_event_agent.models import GateStatus, Stage, TaskContract
from ashare_event_agent.store import SQLiteStateStore


def test_checkpoint_survives_reload(tmp_path):
    store = SQLiteStateStore(tmp_path / "state.db")
    engine = MarketDayEngine(store)
    state = engine.start(TaskContract(trading_date="2026-10-08", prompt="开始荐股"))
    state.set_gate("custom", GateStatus.PASS, ["persisted"])
    store.save(state)
    loaded = store.load(state.contract.task_id)
    assert loaded is not None
    assert loaded.gates["custom"].status == GateStatus.PASS


def test_final_audit_revise_returns_to_declared_stage(tmp_path):
    store = SQLiteStateStore(tmp_path / "state.db")
    engine = MarketDayEngine(store)
    ctl = WorkflowController(engine)
    state = engine.start(TaskContract(trading_date="2026-10-08", prompt="test"))
    state.stage = Stage.FINAL_AUDIT
    state.set_gate("final_audit", GateStatus.REVISE, ["needs replay repair"])
    state.working["final_revision_target"] = "REPLAY_EVAL"
    state = ctl.advance(state)
    assert state.stage == Stage.REPLAY_EVAL
