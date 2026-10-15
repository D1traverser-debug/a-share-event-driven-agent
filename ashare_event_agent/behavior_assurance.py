from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BehaviorAdmissionError(RuntimeError):
    pass


class ProblemDisposition(str, Enum):
    REPAIR_EXECUTED = "REPAIR_EXECUTED"
    BLOCKED_WITH_REASON = "BLOCKED_WITH_REASON"
    NO_CHANGE_WITH_EVIDENCE = "NO_CHANGE_WITH_EVIDENCE"
    PARENT_GUIDANCE_REQUIRED = "PARENT_GUIDANCE_REQUIRED"


class ProblemLayer(str, Enum):
    LOCAL_BUSINESS = "LOCAL_BUSINESS"
    DOMAIN_WORKFLOW = "DOMAIN_WORKFLOW"
    DOMAIN_ARCHITECTURE = "DOMAIN_ARCHITECTURE"
    COMMON_CAPABILITY = "COMMON_CAPABILITY"
    PARENT_CONTROL_PLANE = "PARENT_CONTROL_PLANE"
    HOST = "HOST"
    REQUIREMENT_OR_GOAL = "REQUIREMENT_OR_GOAL"


class HypothesisDisposition(str, Enum):
    PLAUSIBLE = "PLAUSIBLE"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"


class EvolutionDisposition(str, Enum):
    LOCAL_LEARNING_ONLY = "LOCAL_LEARNING_ONLY"
    NO_DURABLE_EVOLUTION_WITH_EVIDENCE = "NO_DURABLE_EVOLUTION_WITH_EVIDENCE"
    DOMAIN_EVOLUTION_CANDIDATE = "DOMAIN_EVOLUTION_CANDIDATE"
    DOMAIN_EVOLUTION_UPDATED = "DOMAIN_EVOLUTION_UPDATED"
    PARENT_OR_COMMON_UPCALL = "PARENT_OR_COMMON_UPCALL"


@dataclass(frozen=True, slots=True)
class RootScopeHypothesis:
    hypothesis_id: str
    layer: ProblemLayer
    statement: str
    disposition: HypothesisDisposition
    supporting_evidence_refs: tuple[str, ...]
    falsification_or_rejection_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip() or not self.statement.strip():
            raise ValueError("root-scope hypothesis requires identity and statement")
        if not self.supporting_evidence_refs:
            raise ValueError("root-scope hypothesis requires supporting evidence")
        if not self.falsification_or_rejection_refs:
            raise ValueError("root-scope hypothesis requires falsification/rejection evidence")


@dataclass(frozen=True, slots=True)
class RootScopeReceipt:
    selected_hypothesis_id: str
    selected_layer: ProblemLayer
    hypothesis_count: int
    compared_layers: tuple[ProblemLayer, ...]
    architecture_reassessment_performed: bool
    durable_problem_record_required: bool
    evidence_refs: tuple[str, ...]


_UPSTREAM_LAYERS = {
    ProblemLayer.DOMAIN_ARCHITECTURE,
    ProblemLayer.COMMON_CAPABILITY,
    ProblemLayer.PARENT_CONTROL_PLANE,
    ProblemLayer.HOST,
    ProblemLayer.REQUIREMENT_OR_GOAL,
}


def require_root_scope_admission(
    *,
    hypotheses: tuple[RootScopeHypothesis, ...],
    selected_hypothesis_id: str,
    material_problem: bool = False,
    repeated_failure: bool = False,
    cross_subsystem: bool = False,
    architecture_gap: bool = False,
    complexity_growth: bool = False,
    scope_expansion: bool = False,
    architecture_reassessment_refs: tuple[str, ...] = (),
    direct_user_or_external_claim_promoted_without_test: bool = False,
) -> RootScopeReceipt:
    """Owner-native Common Behavior 1.3 root-scope admission."""

    if direct_user_or_external_claim_promoted_without_test:
        raise BehaviorAdmissionError(
            "root-scope admission denied: user/external framing was promoted without falsification"
        )
    if not hypotheses:
        raise BehaviorAdmissionError("root-scope admission requires at least one hypothesis")
    if len({item.hypothesis_id for item in hypotheses}) != len(hypotheses):
        raise BehaviorAdmissionError("root-scope hypothesis ids must be unique")

    selected = [item for item in hypotheses if item.hypothesis_id == selected_hypothesis_id]
    if len(selected) != 1 or selected[0].disposition is not HypothesisDisposition.SELECTED:
        raise BehaviorAdmissionError(
            "exactly one SELECTED root-scope hypothesis must match selected_hypothesis_id"
        )
    if sum(item.disposition is HypothesisDisposition.SELECTED for item in hypotheses) != 1:
        raise BehaviorAdmissionError("exactly one root-scope hypothesis may be SELECTED")

    systemic = any(
        (
            material_problem,
            repeated_failure,
            cross_subsystem,
            architecture_gap,
            complexity_growth,
            scope_expansion,
        )
    )
    compared_layers = tuple(sorted({item.layer for item in hypotheses}, key=lambda item: item.value))
    if systemic:
        if len(hypotheses) < 2 or len(compared_layers) < 2:
            raise BehaviorAdmissionError(
                "systemic/material problem requires competing hypotheses across at least two layers"
            )
        if not any(item.disposition is HypothesisDisposition.REJECTED for item in hypotheses):
            raise BehaviorAdmissionError(
                "systemic/material problem requires at least one evidence-rejected alternative"
            )
        if not any(item.layer in _UPSTREAM_LAYERS for item in hypotheses):
            raise BehaviorAdmissionError(
                "systemic/material problem must test an architecture/upstream hypothesis"
            )
        if not architecture_reassessment_refs:
            raise BehaviorAdmissionError(
                "systemic/material problem requires architecture/upstream reassessment evidence"
            )

    selected_item = selected[0]
    evidence_refs = tuple(
        sorted(
            {
                *selected_item.supporting_evidence_refs,
                *selected_item.falsification_or_rejection_refs,
                *architecture_reassessment_refs,
            }
        )
    )
    return RootScopeReceipt(
        selected_hypothesis_id=selected_item.hypothesis_id,
        selected_layer=selected_item.layer,
        hypothesis_count=len(hypotheses),
        compared_layers=compared_layers,
        architecture_reassessment_performed=bool(architecture_reassessment_refs),
        durable_problem_record_required=systemic,
        evidence_refs=evidence_refs,
    )


@dataclass(frozen=True, slots=True)
class BehaviorProblemSignals:
    problem_id: str
    problem_detected: bool
    recoverable_dependency: bool = False
    local_recovery_attempts: tuple[str, ...] = ()
    repair_available: bool = False
    owner_authorized: bool = False
    required_user_fact_or_approval: bool = False
    safety_sensitive_choice: bool = False
    repair_attempted: bool = False
    verification_evidence: tuple[str, ...] = ()
    no_change_evidence: tuple[str, ...] = ()
    blocker: str | None = None
    parent_help_needed: bool = False
    evidence_refs: tuple[str, ...] = ()
    root_scope_receipt: RootScopeReceipt | None = None
    evolution_disposition: EvolutionDisposition | None = None
    durable_problem_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.problem_id.strip():
            raise ValueError("problem_id is required")


@dataclass(frozen=True, slots=True)
class BehaviorProblemReceipt:
    problem_id: str
    disposition: ProblemDisposition
    local_recovery_attempts: tuple[str, ...]
    verification_evidence: tuple[str, ...]
    blocker: str | None
    root_scope_layer: str | None = None
    evolution_disposition: str | None = None
    durable_problem_ref: str | None = None


def _durable_record_required(signals: BehaviorProblemSignals) -> bool:
    return bool(
        (signals.root_scope_receipt and signals.root_scope_receipt.durable_problem_record_required)
        or signals.evolution_disposition
        in {
            EvolutionDisposition.DOMAIN_EVOLUTION_CANDIDATE,
            EvolutionDisposition.DOMAIN_EVOLUTION_UPDATED,
            EvolutionDisposition.PARENT_OR_COMMON_UPCALL,
        }
    )


def _require_cognition_and_learning(signals: BehaviorProblemSignals) -> None:
    if signals.root_scope_receipt is None:
        raise BehaviorAdmissionError(
            "problem action denied: root-scope admission must precede repair, no-change, or parent guidance"
        )
    if not isinstance(signals.evolution_disposition, EvolutionDisposition):
        raise BehaviorAdmissionError(
            "problem action denied: typed evolution disposition is required before action"
        )
    if _durable_record_required(signals) and not (
        isinstance(signals.durable_problem_ref, str) and signals.durable_problem_ref.strip()
    ):
        raise BehaviorAdmissionError(
            "material/evolution-relevant problem requires durable causal evidence before action"
        )


def require_behavior_problem_closure(signals: BehaviorProblemSignals) -> BehaviorProblemReceipt:
    """Enforce A-share owner-native realization of UAOS Common Behavior 1.3."""

    if not signals.problem_detected:
        return BehaviorProblemReceipt(
            signals.problem_id,
            ProblemDisposition.NO_CHANGE_WITH_EVIDENCE,
            signals.local_recovery_attempts,
            signals.no_change_evidence,
            None,
        )

    user_dependency = signals.required_user_fact_or_approval or signals.safety_sensitive_choice

    if signals.recoverable_dependency and not signals.local_recovery_attempts and not user_dependency:
        raise BehaviorAdmissionError(
            "recoverable dependency must receive a proportionate local recovery attempt before user or parent escalation"
        )

    if user_dependency and signals.blocker:
        return BehaviorProblemReceipt(
            signals.problem_id,
            ProblemDisposition.BLOCKED_WITH_REASON,
            signals.local_recovery_attempts,
            signals.evidence_refs,
            signals.blocker,
        )

    _require_cognition_and_learning(signals)

    repair_now = signals.repair_available and signals.owner_authorized and not user_dependency
    if repair_now and not signals.repair_attempted:
        raise BehaviorAdmissionError(
            "owner-authorized available repair must be attempted after root-scope admission before finalizing or escalating"
        )

    common = {
        "root_scope_layer": signals.root_scope_receipt.selected_layer.value,
        "evolution_disposition": signals.evolution_disposition.value,
        "durable_problem_ref": signals.durable_problem_ref,
    }

    if signals.repair_attempted:
        if not signals.verification_evidence:
            raise BehaviorAdmissionError("repair attempt requires verification evidence before closure")
        return BehaviorProblemReceipt(
            signals.problem_id,
            ProblemDisposition.REPAIR_EXECUTED,
            signals.local_recovery_attempts,
            signals.verification_evidence,
            None,
            **common,
        )

    if signals.parent_help_needed:
        if signals.evolution_disposition is not EvolutionDisposition.PARENT_OR_COMMON_UPCALL:
            raise BehaviorAdmissionError(
                "parent-guidance escalation requires PARENT_OR_COMMON_UPCALL evolution disposition"
            )
        if not signals.evidence_refs:
            raise BehaviorAdmissionError("parent-guidance escalation requires evidence_refs")
        return BehaviorProblemReceipt(
            signals.problem_id,
            ProblemDisposition.PARENT_GUIDANCE_REQUIRED,
            signals.local_recovery_attempts,
            signals.evidence_refs,
            signals.blocker,
            **common,
        )

    if signals.blocker:
        return BehaviorProblemReceipt(
            signals.problem_id,
            ProblemDisposition.BLOCKED_WITH_REASON,
            signals.local_recovery_attempts,
            signals.evidence_refs,
            signals.blocker,
            **common,
        )

    if signals.no_change_evidence:
        return BehaviorProblemReceipt(
            signals.problem_id,
            ProblemDisposition.NO_CHANGE_WITH_EVIDENCE,
            signals.local_recovery_attempts,
            signals.no_change_evidence,
            None,
            **common,
        )

    raise BehaviorAdmissionError(
        "detected problem requires admitted repair evidence, a real blocker, evidence-backed no-change, or structured parent guidance"
    )


@dataclass(frozen=True, slots=True)
class ParentGuidanceUpcall:
    escalation_id: str
    domain_revision: str
    problem_ref: str
    severity: str
    impact: str
    blocking_scope: str
    suspected_layer: str
    evidence_refs: tuple[str, ...]
    local_recovery_attempts: tuple[str, ...]
    requested_parent_help: str
    can_continue_unaffected_work: bool
    failure_class: str | None = None
    capability_id: str | None = None
    conflict_keys: tuple[str, ...] = ()

    domain_id: str = "ashare"

    def __post_init__(self) -> None:
        required = (
            self.escalation_id,
            self.domain_revision,
            self.problem_ref,
            self.severity,
            self.impact,
            self.blocking_scope,
            self.suspected_layer,
            self.requested_parent_help,
        )
        if not all(value.strip() for value in required):
            raise ValueError("material parent-guidance upcall requires complete identity, impact, scope, layer and help request")
        if self.severity not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            raise ValueError("invalid severity")
        if self.suspected_layer not in {
            "DOMAIN_BUSINESS",
            "DOMAIN_ARCHITECTURE",
            "COMMON_CAPABILITY",
            "PARENT_CONTROL_PLANE",
            "HOST",
            "REQUIREMENT_OR_GOAL",
            "UNKNOWN",
        }:
            raise ValueError("invalid suspected_layer")
        if not self.evidence_refs:
            raise ValueError("evidence_refs are required")
        if len(self.conflict_keys) != len(set(self.conflict_keys)):
            raise ValueError("duplicate conflict key")

    def as_dict(self) -> dict[str, object]:
        return {
            "escalation_id": self.escalation_id,
            "domain_id": self.domain_id,
            "domain_revision": self.domain_revision,
            "problem_ref": self.problem_ref,
            "severity": self.severity,
            "impact": self.impact,
            "blocking_scope": self.blocking_scope,
            "suspected_layer": self.suspected_layer,
            "evidence_refs": list(self.evidence_refs),
            "local_recovery_attempts": list(self.local_recovery_attempts),
            "requested_parent_help": self.requested_parent_help,
            "can_continue_unaffected_work": self.can_continue_unaffected_work,
            "failure_class": self.failure_class,
            "capability_id": self.capability_id,
            "conflict_keys": list(self.conflict_keys),
        }
