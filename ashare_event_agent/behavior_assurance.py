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


def require_behavior_problem_closure(signals: BehaviorProblemSignals) -> BehaviorProblemReceipt:
    """Enforce A-share owner-native realization of UAOS common behavior semantics.

    This is deliberately small: UAOS owns the common outcome semantics while
    this domain owns the concrete admission path and business evidence.
    """

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
    if repair_now and not signals.repair_attempted:
        raise BehaviorAdmissionError(
            "owner-authorized available repair must be attempted before finalizing or escalating"
        )

    if signals.repair_attempted:
        if not signals.verification_evidence:
            raise BehaviorAdmissionError("repair attempt requires verification evidence before closure")
        return BehaviorProblemReceipt(
            signals.problem_id,
            ProblemDisposition.REPAIR_EXECUTED,
            signals.local_recovery_attempts,
            signals.verification_evidence,
            None,
        )

    if signals.parent_help_needed:
        if not signals.evidence_refs:
            raise BehaviorAdmissionError("parent-guidance escalation requires evidence_refs")
        return BehaviorProblemReceipt(
            signals.problem_id,
            ProblemDisposition.PARENT_GUIDANCE_REQUIRED,
            signals.local_recovery_attempts,
            signals.evidence_refs,
            signals.blocker,
        )

    if signals.blocker:
        return BehaviorProblemReceipt(
            signals.problem_id,
            ProblemDisposition.BLOCKED_WITH_REASON,
            signals.local_recovery_attempts,
            signals.evidence_refs,
            signals.blocker,
        )

    if signals.no_change_evidence:
        return BehaviorProblemReceipt(
            signals.problem_id,
            ProblemDisposition.NO_CHANGE_WITH_EVIDENCE,
            signals.local_recovery_attempts,
            signals.no_change_evidence,
            None,
        )

    raise BehaviorAdmissionError(
        "detected problem requires repair evidence, a real blocker, evidence-backed no-change, or structured parent guidance"
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
            "HOST",
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
