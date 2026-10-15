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
    DOMAIN_BUSINESS = "DOMAIN_BUSINESS"
    DOMAIN_WORKFLOW = "DOMAIN_WORKFLOW"
    DOMAIN_ARCHITECTURE = "DOMAIN_ARCHITECTURE"
    COMMON_CAPABILITY = "COMMON_CAPABILITY"
    CONTROL_PLANE = "CONTROL_PLANE"
    HOST = "HOST"
    REQUIREMENT_OR_GOAL = "REQUIREMENT_OR_GOAL"


class HypothesisDisposition(str, Enum):
    PLAUSIBLE = "PLAUSIBLE"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"


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
            raise ValueError("root-scope hypothesis identity and statement are required")
        if not self.supporting_evidence_refs:
            raise ValueError("root-scope hypothesis requires supporting evidence")
        if not self.falsification_or_rejection_refs:
            raise ValueError("root-scope hypothesis requires falsification/rejection evidence")


@dataclass(frozen=True, slots=True)
class RootScopeReceipt:
    selected_hypothesis_id: str
    selected_layer: ProblemLayer
    hypothesis_ids: tuple[str, ...]
    compared_layers: tuple[ProblemLayer, ...]
    rejected_hypothesis_ids: tuple[str, ...]
    architecture_reassessment_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]


def build_root_scope_receipt(
    hypotheses: tuple[RootScopeHypothesis, ...],
    *,
    selected_hypothesis_id: str,
    systemic_signal: bool = False,
    architecture_reassessment_refs: tuple[str, ...] = (),
    direct_user_or_external_claim_promoted_without_test: bool = False,
) -> RootScopeReceipt:
    """Bind A-share problem action to evidence-tested root scope.

    User framing, an external method and the first repairable symptom may seed a
    hypothesis, but they do not become root cause without falsification evidence.
    """
    if direct_user_or_external_claim_promoted_without_test:
        raise BehaviorAdmissionError(
            "root-scope admission denied: user/external framing was promoted without falsification"
        )
    if not hypotheses:
        raise BehaviorAdmissionError("root-scope admission requires hypotheses")
    ids = [item.hypothesis_id for item in hypotheses]
    if len(ids) != len(set(ids)):
        raise BehaviorAdmissionError("root-scope hypothesis identifiers must be unique")
    selected = [item for item in hypotheses if item.hypothesis_id == selected_hypothesis_id]
    if len(selected) != 1 or selected[0].disposition is not HypothesisDisposition.SELECTED:
        raise BehaviorAdmissionError("selected_hypothesis_id must identify the one SELECTED hypothesis")
    if sum(item.disposition is HypothesisDisposition.SELECTED for item in hypotheses) != 1:
        raise BehaviorAdmissionError("exactly one root-scope hypothesis may be SELECTED")

    layers = tuple(sorted({item.layer for item in hypotheses}, key=lambda item: item.value))
    rejected = tuple(sorted(item.hypothesis_id for item in hypotheses if item.disposition is HypothesisDisposition.REJECTED))
    if systemic_signal:
        if len(hypotheses) < 2 or len(layers) < 2:
            raise BehaviorAdmissionError("systemic problem requires competing hypotheses across at least two layers")
        if not rejected:
            raise BehaviorAdmissionError("systemic problem requires an evidence-rejected alternative")
        upstream = {
            ProblemLayer.DOMAIN_ARCHITECTURE,
            ProblemLayer.COMMON_CAPABILITY,
            ProblemLayer.CONTROL_PLANE,
            ProblemLayer.HOST,
            ProblemLayer.REQUIREMENT_OR_GOAL,
        }
        if not any(item.layer in upstream for item in hypotheses):
            raise BehaviorAdmissionError("systemic problem must test an architecture/upstream hypothesis")
        if not architecture_reassessment_refs:
            raise BehaviorAdmissionError("systemic problem requires architecture reassessment evidence")

    chosen = selected[0]
    evidence_refs = tuple(sorted({
        *chosen.supporting_evidence_refs,
        *chosen.falsification_or_rejection_refs,
        *architecture_reassessment_refs,
    }))
    return RootScopeReceipt(
        selected_hypothesis_id=chosen.hypothesis_id,
        selected_layer=chosen.layer,
        hypothesis_ids=tuple(ids),
        compared_layers=layers,
        rejected_hypothesis_ids=rejected,
        architecture_reassessment_refs=architecture_reassessment_refs,
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
    evolution_disposition: str | None = None
    problem_record_required: bool = False
    problem_record_ref: str | None = None

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
    root_scope_receipt: RootScopeReceipt | None = None
    evolution_disposition: str | None = None
    problem_record_ref: str | None = None


def _present(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _require_cognition_and_learning(signals: BehaviorProblemSignals) -> None:
    if signals.root_scope_receipt is None:
        raise BehaviorAdmissionError("problem action denied: root-scope cognition receipt is missing")
    if not _present(signals.evolution_disposition):
        raise BehaviorAdmissionError("problem action denied: evolution/learning disposition is missing")
    if signals.problem_record_required and not _present(signals.problem_record_ref):
        raise BehaviorAdmissionError("material/evolution-relevant problem requires durable problem evidence")


def require_behavior_problem_closure(signals: BehaviorProblemSignals) -> BehaviorProblemReceipt:
    """Enforce A-share owner-native UAOS Common Behavior 1.3 semantics."""

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

    repair_now = signals.repair_available and signals.owner_authorized and not user_dependency
    if repair_now:
        _require_cognition_and_learning(signals)
        if not signals.repair_attempted:
            raise BehaviorAdmissionError(
                "cognitively-admitted owner repair must be attempted before finalizing or escalating"
            )

    if signals.repair_attempted:
        _require_cognition_and_learning(signals)
        if not signals.verification_evidence:
            raise BehaviorAdmissionError("repair attempt requires verification evidence before closure")
        return BehaviorProblemReceipt(
            signals.problem_id,
            ProblemDisposition.REPAIR_EXECUTED,
            signals.local_recovery_attempts,
            signals.verification_evidence,
            None,
            signals.root_scope_receipt,
            signals.evolution_disposition,
            signals.problem_record_ref,
        )

    if signals.parent_help_needed:
        if not signals.evidence_refs:
            raise BehaviorAdmissionError("parent-guidance escalation requires evidence_refs")
        if signals.problem_record_required and not _present(signals.problem_record_ref):
            raise BehaviorAdmissionError("material parent-guidance problem requires durable problem evidence")
        return BehaviorProblemReceipt(
            signals.problem_id,
            ProblemDisposition.PARENT_GUIDANCE_REQUIRED,
            signals.local_recovery_attempts,
            signals.evidence_refs,
            signals.blocker,
            signals.root_scope_receipt,
            signals.evolution_disposition or "PARENT_GUIDANCE_UPCALL",
            signals.problem_record_ref,
        )

    if signals.blocker:
        if signals.problem_record_required and not _present(signals.problem_record_ref):
            raise BehaviorAdmissionError("material blocked problem requires durable problem evidence")
        return BehaviorProblemReceipt(
            signals.problem_id,
            ProblemDisposition.BLOCKED_WITH_REASON,
            signals.local_recovery_attempts,
            signals.evidence_refs,
            signals.blocker,
            signals.root_scope_receipt,
            signals.evolution_disposition,
            signals.problem_record_ref,
        )

    if signals.no_change_evidence:
        _require_cognition_and_learning(signals)
        return BehaviorProblemReceipt(
            signals.problem_id,
            ProblemDisposition.NO_CHANGE_WITH_EVIDENCE,
            signals.local_recovery_attempts,
            signals.no_change_evidence,
            None,
            signals.root_scope_receipt,
            signals.evolution_disposition,
            signals.problem_record_ref,
        )

    raise BehaviorAdmissionError(
        "detected problem requires cognitively-admitted repair evidence, a real blocker, evidence-backed no-change, or structured parent guidance"
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
            "DOMAIN_WORKFLOW",
            "DOMAIN_ARCHITECTURE",
            "COMMON_CAPABILITY",
            "CONTROL_PLANE",
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
