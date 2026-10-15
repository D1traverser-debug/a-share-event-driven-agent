import pytest

from ashare_event_agent.behavior_assurance import (
    BehaviorAdmissionError,
    BehaviorProblemSignals,
    ParentGuidanceUpcall,
    ProblemDisposition,
    require_behavior_problem_closure,
)


def test_recoverable_dependency_must_be_attempted_before_escalation():
    with pytest.raises(BehaviorAdmissionError, match="local recovery attempt"):
        require_behavior_problem_closure(
            BehaviorProblemSignals(
                problem_id="provider-gap",
                problem_detected=True,
                recoverable_dependency=True,
                parent_help_needed=True,
                evidence_refs=("evidence:provider-gap",),
            )
        )


def test_owner_authorized_repair_cannot_end_as_recommendation_only():
    with pytest.raises(BehaviorAdmissionError, match="repair must be attempted"):
        require_behavior_problem_closure(
            BehaviorProblemSignals(
                problem_id="architecture-gap",
                problem_detected=True,
                local_recovery_attempts=("reproduced",),
                repair_available=True,
                owner_authorized=True,
                parent_help_needed=True,
                evidence_refs=("evidence:architecture-gap",),
            )
        )


def test_verified_repair_is_valid_terminal_state():
    receipt = require_behavior_problem_closure(
        BehaviorProblemSignals(
            problem_id="repairable",
            problem_detected=True,
            recoverable_dependency=True,
            local_recovery_attempts=("retried current provider lane",),
            repair_available=True,
            owner_authorized=True,
            repair_attempted=True,
            verification_evidence=("pytest:test_behavior_assurance",),
        )
    )
    assert receipt.disposition == ProblemDisposition.REPAIR_EXECUTED
    assert receipt.verification_evidence == ("pytest:test_behavior_assurance",)


def test_required_user_approval_is_real_blocker_not_forced_repair():
    receipt = require_behavior_problem_closure(
        BehaviorProblemSignals(
            problem_id="approval-needed",
            problem_detected=True,
            required_user_fact_or_approval=True,
            repair_available=True,
            owner_authorized=True,
            blocker="explicit user approval is required",
            evidence_refs=("contract:approval",),
        )
    )
    assert receipt.disposition == ProblemDisposition.BLOCKED_WITH_REASON


def test_parent_guidance_requires_evidence_and_preserves_unaffected_work_signal():
    upcall = ParentGuidanceUpcall(
        escalation_id="ashare-escalation-001",
        domain_revision="0.3.0/profile6@candidate",
        problem_ref="audits/EVOLUTION_INDEX.json#EVO-20261015-COMMON-BEHAVIOR-ADOPTION",
        severity="HIGH",
        impact="child inherited-behavior gap",
        blocking_scope="common behavior admission only",
        suspected_layer="COMMON_CAPABILITY",
        evidence_refs=(".uaos/CAPABILITIES.json", "tests/test_behavior_assurance.py"),
        local_recovery_attempts=("owner-native admission implemented",),
        requested_parent_help="confirm common behavior compatibility",
        can_continue_unaffected_work=True,
        failure_class="FC-INHERITED-BEHAVIOR-DECLARATION-WITHOUT-UNIFORM-OPERATIONAL-PROOF-002",
        capability_id="governed_self_evolution",
        conflict_keys=("COMMON:behavior-assurance",),
    )
    payload = upcall.as_dict()
    assert payload["domain_id"] == "ashare"
    assert payload["can_continue_unaffected_work"] is True
    assert payload["suspected_layer"] == "COMMON_CAPABILITY"
    assert payload["evidence_refs"]
