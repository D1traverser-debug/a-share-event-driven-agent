from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .controller import WorkflowController
from .engine import MarketDayEngine, WorkflowError
from .models import MarketDayState, Stage, TaskContract
from .store import SQLiteStateStore


class StageExecutor(Protocol):
    def execute(self, state: MarketDayState) -> MarketDayState: ...


class AgentRuntime:
    def __init__(self, engine: MarketDayEngine, executors: dict[Stage, StageExecutor], *, max_steps: int = 80):
        self.engine = engine
        self.controller = WorkflowController(engine)
        self.executors = executors
        self.max_steps = max_steps

    @classmethod
    def with_sqlite(cls, path: str | Path, executors: dict[Stage, StageExecutor], *, max_steps: int = 80):
        return cls(MarketDayEngine(SQLiteStateStore(path)), executors, max_steps=max_steps)

    def start(self, contract: TaskContract) -> MarketDayState:
        return self.controller.advance(self.engine.start(contract))

    def resume(self, task_id: str) -> MarketDayState:
        state = self.engine.store.load(task_id)
        if state is None:
            raise RuntimeError(f"checkpoint not found: {task_id}")
        state.add_trace("RUNTIME_RESUMED", "checkpoint loaded")
        self.engine.store.save(state)
        return state

    def run(self, state: MarketDayState) -> MarketDayState:
        steps = 0
        while state.stage not in {Stage.FROZEN, Stage.COMPLETE, Stage.BLOCKED}:
            steps += 1
            if steps > self.max_steps:
                return self.engine.block(state, "max_steps exceeded")
            executor = self.executors.get(state.stage)
            if executor is None:
                return self.engine.block(state, f"no executor for {state.stage.value}")
            try:
                state.add_trace("EXECUTOR_START", state.stage.value)
                self.engine.store.save(state)
                state = executor.execute(state)
                state.add_trace("EXECUTOR_END", state.stage.value)
                self.engine.store.save(state)
                if state.stage in {Stage.FROZEN, Stage.COMPLETE, Stage.BLOCKED}:
                    break
                state = self.controller.advance(state)
            except Exception as exc:
                return self.engine.block(state, f"executor error at {state.stage.value}: {type(exc).__name__}: {exc}")
        return state
