from ashare_event_agent.models import Stage, TaskContract
from ashare_event_agent.runner import AgentRuntime


class ExplodingExecutor:
    def execute(self, state):
        raise RuntimeError("simulated failure")


def test_missing_executor_blocks_not_freeform(tmp_path):
    runtime = AgentRuntime.with_sqlite(tmp_path / "state.db", executors={})
    state = runtime.start(TaskContract(trading_date="2026-10-08", prompt="开始荐股"))
    assert state.stage == Stage.FREEZE
    state = runtime.run(state)
    assert state.stage == Stage.BLOCKED


def test_executor_error_blocks_not_freeform(tmp_path):
    runtime = AgentRuntime.with_sqlite(tmp_path / "state.db", executors={Stage.FREEZE: ExplodingExecutor()})
    state = runtime.start(TaskContract(trading_date="2026-10-08", prompt="开始荐股"))
    state = runtime.run(state)
    assert state.stage == Stage.BLOCKED
