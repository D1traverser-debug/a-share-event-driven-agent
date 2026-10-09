from ashare_event_agent.continuity import is_bare_inherit_candidate, list_resumable_states
from ashare_event_agent.controller import WorkflowController
from ashare_event_agent.engine import MarketDayEngine
from ashare_event_agent.models import (
    GateStatus,
    MarketDayState,
    ResumeVisibility,
    Stage,
    TaskClass,
    TaskContract,
)
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
    assert loaded.contract.task_class == TaskClass.USER
    assert loaded.contract.resume_eligible is True
    assert loaded.contract.resume_visibility == ResumeVisibility.DEFAULT
    assert loaded.contract.contract_version == "2.0"


def test_legacy_checkpoint_missing_continuity_fields_fails_closed():
    state = MarketDayState(contract=TaskContract(trading_date="2026-10-08", prompt="legacy"))
    payload = state.model_dump(mode="json")
    for key in ["task_class", "resume_eligible", "resume_visibility", "contract_version", "runtime_version", "skill_version"]:
        payload["contract"].pop(key, None)

    loaded = MarketDayState.model_validate(payload)
    assert loaded.contract.task_class == TaskClass.MIGRATION
    assert loaded.contract.resume_eligible is False
    assert loaded.contract.resume_visibility == ResumeVisibility.EXPLICIT_ONLY
    assert is_bare_inherit_candidate(loaded) is False


def test_resumable_discovery_returns_only_default_visible_user_tasks(tmp_path):
    store = SQLiteStateStore(tmp_path / "state.db")
    engine = MarketDayEngine(store)

    user = engine.start(TaskContract(trading_date="2026-10-08", prompt="user"))
    assert is_bare_inherit_candidate(user) is True

    fixture = engine.start(TaskContract(
        trading_date="2026-10-08",
        prompt="fixture",
        task_class=TaskClass.FIXTURE,
        resume_eligible=True,
        resume_visibility=ResumeVisibility.DEFAULT,
        contract_version="2.0",
    ))
    assert is_bare_inherit_candidate(fixture) is False

    explicit_only = engine.start(TaskContract(
        trading_date="2026-10-08",
        prompt="explicit",
        task_class=TaskClass.USER,
        resume_eligible=True,
        resume_visibility=ResumeVisibility.EXPLICIT_ONLY,
        contract_version="2.0",
    ))
    assert is_bare_inherit_candidate(explicit_only) is False

    complete = engine.start(TaskContract(trading_date="2026-10-08", prompt="complete"))
    complete.stage = Stage.COMPLETE
    store.save(complete)
    assert is_bare_inherit_candidate(complete) is False

    resumable = list_resumable_states(store, limit=20)
    assert [state.contract.task_id for state in resumable] == [user.contract.task_id]


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
