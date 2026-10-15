import pytest

from ashare_event_agent.behavior_assurance import (
    BehaviorAdmissionError,
    BehaviorProblemSignals,
    EvolutionDisposition,
    HypothesisDisposition,
    ParentGuidanceUpcall,
    ProblemDisposition,
    ProblemLayer,
    RootScopeHypothesis,
    require_behavior_problem_closure,
    require_root_scope_admission,
)


def hypothesis(hypothesis_id, layer, disposition):
    return RootScopeHypothesis(
        hypothesis_id=hypothesis_id,
        layer=layer,
        statement=f"candidate root at {layer.value}",
        disposition=disposition,
        supporting_evidence_refs=(f"evidence:support:{hypothesis_id}",),
        falsification_or_rejection_refs=(f"evidence:probe:{hypothesis_id}",),
    )


def local_receipt():
    return require_root_scope_admission(
        hypotheses=(
            hypothesis("local", ProblemLayer.LOCAL_BUSINESS, HypothesisDisposition.SELECTED),
        ),
        selected_hypothesis_id="local",
    )


def systemic_receipt():
    return require_root_scope_admission(
        hypotheses=(
            hypothesis("workflow", ProblemLayer.DOMAIN_WORKFLOW, HypothesisDisposition.SELECTED),
            hypothesis("common", ProblemLayer.COMMON_CAPABILITY, HypothesisDisposition.REJECTED),
        ),
        selected_hypothesis_id="workflow",
        material_problem=True,
        architecture_reassessment_refs=("evidence:architecture:checked",),
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


def test_repairable_problem_cannot_skip_root_scope_even_when_fix_is_obvious():
    with pytest.raises(BehaviorAdmissionError, match="root-scope admission"):
        require_behavior_problem_closure(
            BehaviorProblemSignals(
                problem_id="architecture-gap",
                problem_detected=True,
                local_recovery_attempts=("reproduced",),
                repair_available=True,
                owner_authorized=True,
                repair_attempted=True,
                verification_evidence=("evidence:repair",),
            )
        )


def test_owner_authorized_repair_cannot_end_as_recommendation_only_after_admission():
    with pytest.raises(BehaviorAdmissionError, match="repair must be attempted"):
        require_behavior_problem_closure(
            BehaviorProblemSignals(
                problem_id="repairable",
                problem_detected=True,
                repair_available=True,
                owner_authorized=True,
                root_scope_receipt=local_receipt(),
                evolution_disposition=EvolutionDisposition.LOCAL_LEARNING_ONLY,
            )
        )


def test_verified_repair_is_valid_terminal_state_after_root_scope_and_evolution_admission():
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
            root_scope_receipt=local_receipt(),
            evolution_disposition=EvolutionDisposition.LOCAL_LEARNING_ONLY,
        )
    )
    assert receipt.disposition == ProblemDisposition.REPAIR_EXECUTED
    assert receipt.root_scope_layer == ProblemLayer.LOCAL_BUSINESS.value


def test_required_user_approval_is_real_blocker_without_fake_root_cause_claim():
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


def test_user_or_external_claim_cannot_be_promoted_directly_to_root_cause():
    with pytest.raises(BehaviorAdmissionError, match="promoted without falsification"):
        require_root_scope_admission(
            hypotheses=(
                hypothesis("architecture", ProblemLayer.DOMAIN_ARCHITECTURE, HypothesisDisposition.SELECTED),
            ),
            selected_hypothesis_id="architecture",
            direct_user_or_external_claim_promoted_without_test=True,
        )


def test_material_problem_requires_cross_layer_architecture_reassessment():
    with pytest.raises(BehaviorAdmissionError, match="at least two layers"):
        require_root_scope_admission(
            hypotheses=(
                hypothesis("local", ProblemLayer.LOCAL_BUSINESS, HypothesisDisposition.SELECTED),
                hypothesis("local2", ProblemLayer.LOCAL_BUSINESS, HypothesisDisposition.REJECTED),
            ),
            selected_hypothesis_id="local",
            material_problem=True,
            architecture_reassessment_refs=("evidence:architecture",),
        )


def test_material_problem_requires_durable_causal_evidence_before_repair():
    with pytest.raises(BehaviorAdmissionError, match="durable causal evidence"):
        require_behavior_problem_closure(
            BehaviorProblemSignals(
                problem_id="material",
                problem_detected=True,
                repair_available=True,
                owner_authorized=True,
                repair_attempted=True,
                verification_evidence=("evidence:repair",),
                root_scope_receipt=systemic_receipt(),
                evolution_disposition=EvolutionDisposition.DOMAIN_EVOLUTION_CANDIDATE,
            )
        )


def test_parent_guidance_requires_root_scope_upcall_disposition_and_durable_problem_ref():
    receipt = require_behavior_problem_closure(
        BehaviorProblemSignals(
            problem_id="common-gap",
            problem_detected=True,
            parent_help_needed=True,
            evidence_refs=("evidence:common-gap",),
            root_scope_receipt=systemic_receipt(),
            evolution_disposition=EvolutionDisposition.PARENT_OR_COMMON_UPCALL,
            durable_problem_ref="audits/EVOLUTION_INDEX.json#EVO-20261016-COMMON-BEHAVIOR-1-3",
        )
    )
    assert receipt.disposition == ProblemDisposition.PARENT_GUIDANCE_REQUIRED
    assert receipt.durable_problem_ref


def test_parent_guidance_envelope_preserves_unaffected_work_signal():
    upcall = ParentGuidanceUpcall(
        escalation_id="ashare-escalation-001",
        domain_revision="0.3.0/profile7@candidate",
        problem_ref="audits/EVOLUTION_INDEX.json#EVO-20261016-COMMON-BEHAVIOR-1-3",
        severity="HIGH",
        impact="child root-scope adoption",
        blocking_scope="common behavior admission only",
        suspected_layer="COMMON_CAPABILITY",
        evidence_refs=(".uaos/CAPABILITIES.json", "tests/test_behavior_assurance.py"),
        local_recovery_attempts=("owner-native root-scope admission implemented",),
        requested_parent_help="confirm common behavior 1.3 compatibility",
        can_continue_unaffected_work=True,
        failure_class="FC-COMMON-BEHAVIOR-1-3-OWNER-ADOPTION-OPEN",
        capability_id="governed_self_evolution",
        conflict_keys=("COMMON:behavior-assurance",),
    )
    payload = upcall.as_dict()
    assert payload["domain_id"] == "ashare"
    assert payload["can_continue_unaffected_work"] is True
    assert payload["suspected_layer"] == "COMMON_CAPABILITY"
    assert payload["evidence_refs"]
