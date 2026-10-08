from __future__ import annotations

import hashlib
import json
from typing import Any

from .models import GateStatus, MarketDayState, Stage, TaskContract
from .store import SQLiteStateStore


class WorkflowError(RuntimeError):
    pass


ALLOWED_TRANSITIONS: dict[Stage, set[Stage]] = {
    Stage.INTAKE: {Stage.FREEZE, Stage.BLOCKED},
    Stage.FREEZE: {Stage.SOURCE_COMPLETION, Stage.BLOCKED},
    Stage.SOURCE_COMPLETION: {Stage.SOURCE_AUDIT, Stage.BLOCKED},
    Stage.SOURCE_AUDIT: {Stage.SOURCE_COMPLETION, Stage.EVENT_LEDGER, Stage.BLOCKED},
    Stage.EVENT_LEDGER: {Stage.INDUSTRY_RESEARCH, Stage.BLOCKED},
    Stage.INDUSTRY_RESEARCH: {Stage.STOCKBASE_RECALL, Stage.BLOCKED},
    Stage.STOCKBASE_RECALL: {Stage.UNIVERSE_AUDIT, Stage.BLOCKED},
    Stage.UNIVERSE_AUDIT: {Stage.INDUSTRY_RESEARCH, Stage.STOCKBASE_RECALL, Stage.MARKET_STRUCTURE, Stage.BLOCKED},
    Stage.MARKET_STRUCTURE: {Stage.RECALL_POOL, Stage.BLOCKED},
    Stage.RECALL_POOL: {Stage.EXECUTION_PLAN, Stage.BLOCKED},
    Stage.EXECUTION_PLAN: {Stage.PREMARKET_AUDIT, Stage.BLOCKED},
    Stage.PREMARKET_AUDIT: {Stage.SOURCE_COMPLETION, Stage.EVENT_LEDGER, Stage.INDUSTRY_RESEARCH, Stage.MARKET_STRUCTURE, Stage.RECALL_POOL, Stage.EXECUTION_PLAN, Stage.FROZEN, Stage.BLOCKED},
    Stage.FROZEN: {Stage.REVIEW_OUTCOMES, Stage.BLOCKED},
    Stage.REVIEW_OUTCOMES: {Stage.ATTRIBUTION, Stage.BLOCKED},
    Stage.ATTRIBUTION: {Stage.RECALL_GRADING, Stage.BLOCKED},
    Stage.RECALL_GRADING: {Stage.LEARNING_AUDIT, Stage.BLOCKED},
    Stage.LEARNING_AUDIT: {Stage.RULE_PROPOSAL, Stage.BLOCKED},
    Stage.RULE_PROPOSAL: {Stage.REPLAY_EVAL, Stage.BLOCKED},
    Stage.REPLAY_EVAL: {Stage.FINAL_AUDIT, Stage.BLOCKED},
    Stage.FINAL_AUDIT: {Stage.ATTRIBUTION, Stage.LEARNING_AUDIT, Stage.REPLAY_EVAL, Stage.COMPLETE, Stage.BLOCKED},
    Stage.COMPLETE: set(),
    Stage.BLOCKED: {Stage.FREEZE, Stage.SOURCE_COMPLETION, Stage.EVENT_LEDGER, Stage.INDUSTRY_RESEARCH, Stage.STOCKBASE_RECALL, Stage.MARKET_STRUCTURE, Stage.RECALL_POOL, Stage.EXECUTION_PLAN, Stage.PREMARKET_AUDIT, Stage.REVIEW_OUTCOMES, Stage.ATTRIBUTION, Stage.LEARNING_AUDIT, Stage.REPLAY_EVAL, Stage.FINAL_AUDIT},
}

PREMARKET_KEYS = [
    "freeze_card", "source_completion", "event_ledger", "industry_research", "stockbase_context",
    "universe", "market_structure", "recall_pool", "execution_plan", "premarket_audit",
]


def premarket_payload(state: MarketDayState) -> dict[str, Any]:
    return {key: state.working.get(key) for key in PREMARKET_KEYS}


def payload_hash(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class MarketDayEngine:
    def __init__(self, store: SQLiteStateStore):
        self.store = store

    def start(self, contract: TaskContract) -> MarketDayState:
        state = MarketDayState(contract=contract)
        state.add_trace("RUNTIME_STARTED", "Market-day TaskContract persisted before research")
        state.set_gate("runtime_initialized", GateStatus.PASS, ["TaskContract exists", "state store active"])
        self.store.save(state)
        return state

    def transition(self, state: MarketDayState, next_stage: Stage, *, reason: str = "") -> MarketDayState:
        if next_stage not in ALLOWED_TRANSITIONS[state.stage]:
            raise WorkflowError(f"illegal transition: {state.stage.value} -> {next_stage.value}")
        state.add_trace("STAGE_EXIT", reason)
        state.stage = next_stage
        state.add_trace("STAGE_ENTER", reason)
        self.store.save(state)
        return state

    def block(self, state: MarketDayState, reason: str) -> MarketDayState:
        state.blocked_reason = reason
        if state.stage != Stage.BLOCKED:
            self.transition(state, Stage.BLOCKED, reason=reason)
        self.store.save(state)
        return state

    def freeze(self, state: MarketDayState) -> MarketDayState:
        if state.stage != Stage.PREMARKET_AUDIT:
            raise WorkflowError("freeze is only legal from PREMARKET_AUDIT")
        state.frozen_hash = payload_hash(premarket_payload(state))
        state.set_gate("freeze_integrity", GateStatus.PASS, [f"sha256={state.frozen_hash}"])
        return self.transition(state, Stage.FROZEN, reason="premarket snapshot frozen immutably")

    def assert_frozen_unchanged(self, state: MarketDayState) -> None:
        if not state.frozen_hash:
            raise WorkflowError("missing frozen_hash")
        actual = payload_hash(premarket_payload(state))
        if actual != state.frozen_hash:
            raise WorkflowError(f"premarket snapshot mutated after freeze: expected={state.frozen_hash} actual={actual}")

    def complete(self, state: MarketDayState) -> MarketDayState:
        if state.stage != Stage.FINAL_AUDIT:
            raise WorkflowError("completion only legal from FINAL_AUDIT")
        self.assert_frozen_unchanged(state)
        unresolved = [name for name, gate in state.gates.items() if gate.status in {GateStatus.NOT_RUN, GateStatus.REVISE, GateStatus.FAIL}]
        if unresolved:
            raise WorkflowError(f"unresolved gates: {unresolved}")
        missing = []
        for kind in state.contract.required_outputs:
            artifact = state.artifacts.get(kind)
            if artifact is None or not artifact.exists:
                missing.append(kind.value)
        if missing:
            raise WorkflowError(f"missing required outputs: {missing}")
        return self.transition(state, Stage.COMPLETE, reason="all gates and required outputs passed; frozen premarket remained unchanged")
