from __future__ import annotations

from .checks import audit_source_completion
from .engine import MarketDayEngine, WorkflowError
from .integrity import (
    attribution_integrity_errors,
    execution_integrity_errors,
    recall_grade_integrity_errors,
    recall_integrity_errors,
    replay_coherence_errors,
    universe_integrity_errors,
)
from .models import GateStatus, MarketDayState, Stage
from .schemas import (
    AttributionPackage,
    ExecutionPlan,
    FreezeCard,
    IndustryResearchPackage,
    OutcomePackage,
    RecallGrade,
    RecallPoolPackage,
    ReplayEval,
    RuleProposal,
    SourceCompletionPackage,
    UniversePackage,
)


class WorkflowController:
    def __init__(self, engine: MarketDayEngine):
        self.engine = engine

    @staticmethod
    def _status(state: MarketDayState, gate: str) -> GateStatus:
        return state.gates.get(gate).status if gate in state.gates else GateStatus.NOT_RUN

    def _pass(self, state: MarketDayState, gate: str) -> None:
        if self._status(state, gate) != GateStatus.PASS:
            raise WorkflowError(f"gate {gate} must PASS before leaving {state.stage.value}")

    def _revise_in_place(self, state: MarketDayState, gate: str, errors: list[str]) -> MarketDayState:
        state.set_gate(gate, GateStatus.REVISE, ["cross-stage integrity guard"], "; ".join(errors))
        state.add_trace("INTEGRITY_REVISE", f"{gate}: {'; '.join(errors)}")
        self.engine.store.save(state)
        return state

    def advance(self, state: MarketDayState) -> MarketDayState:
        s = state.stage

        if s == Stage.SOURCE_COMPLETION:
            pkg = SourceCompletionPackage.model_validate(state.working.get("source_completion"))
            freeze = FreezeCard.model_validate(state.working.get("freeze_card"))
            errors = audit_source_completion(pkg, freeze)
            if errors:
                return self._revise_in_place(state, "source_completion", errors)
            self._pass(state, "source_completion")
            return self.engine.transition(state, Stage.SOURCE_AUDIT, reason="source_completion passed with freeze-bound integrity")

        if s == Stage.RECALL_POOL:
            recall = RecallPoolPackage.model_validate(state.working.get("recall_pool"))
            universe = UniversePackage.model_validate(state.working.get("universe"))
            errors = recall_integrity_errors(universe, recall)
            if errors:
                return self._revise_in_place(state, "recall_pool", errors)
            self._pass(state, "recall_pool")
            return self.engine.transition(state, Stage.EXECUTION_PLAN, reason="recall_pool passed with Universe lineage")

        if s == Stage.EXECUTION_PLAN:
            plan = ExecutionPlan.model_validate(state.working.get("execution_plan"))
            recall = RecallPoolPackage.model_validate(state.working.get("recall_pool"))
            errors = execution_integrity_errors(recall, plan)
            if errors:
                return self._revise_in_place(state, "execution_plan", errors)
            self._pass(state, "execution_plan")
            return self.engine.transition(state, Stage.PREMARKET_AUDIT, reason="execution_plan passed U1 lineage plus risk/buyability gating")

        if s == Stage.ATTRIBUTION:
            attribution = AttributionPackage.model_validate(state.working.get("attribution"))
            outcomes = OutcomePackage.model_validate(state.working.get("review_outcomes"))
            recall = RecallPoolPackage.model_validate(state.working.get("recall_pool"))
            errors = attribution_integrity_errors(outcomes, recall, attribution)
            if errors:
                return self._revise_in_place(state, "attribution", errors)
            self._pass(state, "attribution")
            return self.engine.transition(state, Stage.RECALL_GRADING, reason="attribution passed against outcomes and frozen recall")

        if s == Stage.RECALL_GRADING:
            grade = RecallGrade.model_validate(state.working.get("recall_grading"))
            attribution = AttributionPackage.model_validate(state.working.get("attribution"))
            outcomes = OutcomePackage.model_validate(state.working.get("review_outcomes"))
            plan = ExecutionPlan.model_validate(state.working.get("execution_plan"))
            errors = recall_grade_integrity_errors(attribution, grade, plan, outcomes)
            if errors:
                return self._revise_in_place(state, "recall_grading", errors)
            self._pass(state, "recall_grading")
            return self.engine.transition(state, Stage.LEARNING_AUDIT, reason="recall and final-selection quality passed frozen-plan/outcome reconciliation")

        if s == Stage.REPLAY_EVAL:
            replay = ReplayEval.model_validate(state.working.get("replay_eval"))
            proposal = RuleProposal.model_validate(state.working.get("rule_proposal"))
            errors = replay_coherence_errors(proposal, replay)
            if errors:
                return self._revise_in_place(state, "replay_eval", errors)
            self._pass(state, "replay_eval")
            return self.engine.transition(state, Stage.FINAL_AUDIT, reason="replay_eval passed proposal/replay coherence")

        linear = {
            Stage.INTAKE: ("runtime_initialized", Stage.FREEZE),
            Stage.FREEZE: ("freeze_card", Stage.SOURCE_COMPLETION),
            Stage.EVENT_LEDGER: ("event_ledger", Stage.INDUSTRY_RESEARCH),
            Stage.INDUSTRY_RESEARCH: ("industry_research", Stage.STOCKBASE_RECALL),
            Stage.STOCKBASE_RECALL: ("stockbase_recall", Stage.UNIVERSE_AUDIT),
            Stage.MARKET_STRUCTURE: ("market_structure", Stage.RECALL_POOL),
            Stage.REVIEW_OUTCOMES: ("review_outcomes", Stage.ATTRIBUTION),
            Stage.LEARNING_AUDIT: ("learning_audit", Stage.RULE_PROPOSAL),
            Stage.RULE_PROPOSAL: ("rule_proposal", Stage.REPLAY_EVAL),
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
                industry = IndustryResearchPackage.model_validate(state.working.get("industry_research"))
                universe = UniversePackage.model_validate(state.working.get("universe"))
                errors = universe_integrity_errors(industry, universe)
                if errors:
                    state.set_gate("universe_audit", GateStatus.REVISE, ["cross-stage integrity guard"], "; ".join(errors))
                    state.working["universe_revision_target"] = "INDUSTRY_RESEARCH"
                    state.add_trace("INTEGRITY_REVISE", f"universe_audit: {'; '.join(errors)}")
                    return self.engine.transition(state, Stage.INDUSTRY_RESEARCH, reason="Universe/industry lineage failed")
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
