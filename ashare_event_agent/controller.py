from __future__ import annotations

from .engine import MarketDayEngine, WorkflowError
from .models import GateStatus, MarketDayState, Stage


class WorkflowController:
    def __init__(self, engine: MarketDayEngine):
        self.engine = engine

    @staticmethod
    def _status(state: MarketDayState, gate: str) -> GateStatus:
        return state.gates.get(gate).status if gate in state.gates else GateStatus.NOT_RUN

    def _pass(self, state: MarketDayState, gate: str) -> None:
        if self._status(state, gate) != GateStatus.PASS:
            raise WorkflowError(f"gate {gate} must PASS before leaving {state.stage.value}")

    def advance(self, state: MarketDayState) -> MarketDayState:
        s = state.stage
        linear = {
            Stage.INTAKE: ("runtime_initialized", Stage.FREEZE),
            Stage.FREEZE: ("freeze_card", Stage.SOURCE_COMPLETION),
            Stage.SOURCE_COMPLETION: ("source_completion", Stage.SOURCE_AUDIT),
            Stage.EVENT_LEDGER: ("event_ledger", Stage.INDUSTRY_RESEARCH),
            Stage.INDUSTRY_RESEARCH: ("industry_research", Stage.STOCKBASE_RECALL),
            Stage.STOCKBASE_RECALL: ("stockbase_recall", Stage.UNIVERSE_AUDIT),
            Stage.MARKET_STRUCTURE: ("market_structure", Stage.RECALL_POOL),
            Stage.RECALL_POOL: ("recall_pool", Stage.EXECUTION_PLAN),
            Stage.EXECUTION_PLAN: ("execution_plan", Stage.PREMARKET_AUDIT),
            Stage.REVIEW_OUTCOMES: ("review_outcomes", Stage.ATTRIBUTION),
            Stage.ATTRIBUTION: ("attribution", Stage.RECALL_GRADING),
            Stage.RECALL_GRADING: ("recall_grading", Stage.LEARNING_AUDIT),
            Stage.LEARNING_AUDIT: ("learning_audit", Stage.RULE_PROPOSAL),
            Stage.RULE_PROPOSAL: ("rule_proposal", Stage.REPLAY_EVAL),
            Stage.REPLAY_EVAL: ("replay_eval", Stage.FINAL_AUDIT),
        }
        if s in linear:
            gate, nxt = linear[s]
            self._pass(state, gate)
            return self.engine.transition(state, nxt, reason=f"{gate} passed")
        if s == Stage.SOURCE_AUDIT:
            st = self._status(state, "source_audit")
            if st == GateStatus.PASS:
                return self.engine.transition(state, Stage.EVENT_LEDGER, reason="source audit passed")
            if st == GateStatus.REVISE:
                return self.engine.transition(state, Stage.SOURCE_COMPLETION, reason="source gaps remain")
            raise WorkflowError("source_audit must PASS or REVISE")
        if s == Stage.UNIVERSE_AUDIT:
            st = self._status(state, "universe_audit")
            if st == GateStatus.PASS:
                return self.engine.transition(state, Stage.MARKET_STRUCTURE, reason="universe audit passed")
            if st == GateStatus.REVISE:
                target = state.working.get("universe_revision_target", "INDUSTRY_RESEARCH")
                return self.engine.transition(state, Stage.STOCKBASE_RECALL if target == "STOCKBASE_RECALL" else Stage.INDUSTRY_RESEARCH, reason="universe revision")
            raise WorkflowError("universe_audit must PASS or REVISE")
        if s == Stage.PREMARKET_AUDIT:
            st = self._status(state, "premarket_audit")
            if st == GateStatus.PASS:
                return self.engine.freeze(state)
            if st == GateStatus.REVISE:
                target = state.working.get("premarket_revision_target", "EXECUTION_PLAN")
                mapping = {
                    "SOURCE_COMPLETION": Stage.SOURCE_COMPLETION,
                    "EVENT_LEDGER": Stage.EVENT_LEDGER,
                    "INDUSTRY_RESEARCH": Stage.INDUSTRY_RESEARCH,
                    "MARKET_STRUCTURE": Stage.MARKET_STRUCTURE,
                    "RECALL_POOL": Stage.RECALL_POOL,
                    "EXECUTION_PLAN": Stage.EXECUTION_PLAN,
                }
                return self.engine.transition(state, mapping.get(target, Stage.EXECUTION_PLAN), reason="premarket red-team revision")
            raise WorkflowError("premarket_audit must PASS or REVISE")
        if s == Stage.FINAL_AUDIT:
            st = self._status(state, "final_audit")
            if st == GateStatus.PASS:
                return self.engine.complete(state)
            if st == GateStatus.REVISE:
                target = state.working.get("final_revision_target", "ATTRIBUTION")
                mapping = {
                    "ATTRIBUTION": Stage.ATTRIBUTION,
                    "LEARNING_AUDIT": Stage.LEARNING_AUDIT,
                    "REPLAY_EVAL": Stage.REPLAY_EVAL,
                }
                return self.engine.transition(state, mapping.get(target, Stage.ATTRIBUTION), reason=f"final audit revision target={target}")
            raise WorkflowError("final_audit must PASS or REVISE before advancing")
        raise WorkflowError(f"no automatic advance from {s.value}")
