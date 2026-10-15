import pytest

from ashare_event_agent.behavior_assurance import (
    BehaviorAdmissionError,
    BehaviorProblemSignals,
    HypothesisDisposition,
    ParentGuidanceUpcall,
    ProblemDisposition,
    ProblemLayer,
    RootScopeHypothesis,
    build_root_scope_receipt,
    require_behavior_problem_closure,
)


def _hypothesis(hid: str, layer: ProblemLayer, disposition: HypothesisDisposition) -> RootScopeHypothesis:
    return RootScopeHypothesis(
        hypothesis_id=hid,
        layer=layer,
        statement=f"candidate cause {hid}",
        disposition=disposition,
        supporting_evidence_refs=(f"evidence:support:{hid}",),
        falsification_or_rejection_refs=(f"evidence:probe:{hid}",),
    )


def _root(*, systemic: bool = False):
    hypotheses = (
        _hypothesis("selected", ProblemLayer.DOMAIN_WORKFLOW, HypothesisDisposition.SELECTED),
    )
    architecture_refs = ()
    if systemic:
        hypotheses = (*hypotheses, _hypothesis("upstream", ProblemLayer.COMMON_CAPABILITY, HypothesisDisposition.REJECTED))
        architecture_refs = ("evidence:architecture-reassessment",)
    return build_root_scope_receipt(
        hypotheses,
        selected_hypothesis_id="selected",
        systemic_signal=systemic,
        architecture_reassessment_refs=architecture_refs,
    )


def _admitted(**kwargs):
    values = dict(
        problem_id="repairable",
        problem_detected=True,
        root_scope_receipt=_root(),
        evolution_disposition="EVIDENCE_ONLY",
    )
    values.update(kwargs)
    return BehaviorProblemSignals(**values)


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


def test_owner_authorized_repair_cannot_bypass_root_scope_cognition():
    with pytest.raises(BehaviorAdmissionError, match="root-scope cognition"):
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


def test_cognitively_admitted_owner_repair_cannot_end_as_recommendation_only():
    with pytest.raises(BehaviorAdmissionError, match="must be attempted"):
        require_behavior_problem_closure(
            _admitted(
                local_recovery_attempts=("reproduced",),
                repair_available=True,
                owner_authorized=True,
                parent_help_needed=True,
                evidence_refs=("evidence:architecture-gap",),
            )
        )


def test_verified_repair_is_valid_terminal_state_after_root_scope_and_learning_disposition():
    receipt = require_behavior_problem_closure(
        _admitted(
            recoverable_dependency=True,
            local_recovery_attempts=("retried current provider lane",),
            repair_available=True,
            owner_authorized=True,
            repair_attempted=True,
            verification_evidence=("pytest:test_behavior_assurance",),
        )
    )
    assert receipt.disposition == ProblemDisposition.REPAIR_EXECUTED
    assert receipt.root_scope_receipt is not None
    assert receipt.evolution_disposition == "EVIDENCE_ONLY"


def test_material_problem_requires_durable_problem_record_before_repair():
    with pytest.raises(BehaviorAdmissionError, match="durable problem evidence"):
        require_behavior_problem_closure(
            _admitted(
                repair_available=True,
                owner_authorized=True,
                repair_attempted=True,
                verification_evidence=("pytest",),
                problem_record_required=True,
            )
        )


def test_systemic_root_scope_requires_cross_layer_upstream_falsification():
    with pytest.raises(BehaviorAdmissionError, match="at least two layers"):
        build_root_scope_receipt(
            (
                _hypothesis("selected", ProblemLayer.DOMAIN_WORKFLOW, HypothesisDisposition.SELECTED),
                _hypothesis("same-layer", ProblemLayer.DOMAIN_WORKFLOW, HypothesisDisposition.REJECTED),
            ),
            selected_hypothesis_id="selected",
            systemic_signal=True,
            architecture_reassessment_refs=("evidence:architecture",),
        )

    receipt = _root(systemic=True)
    assert ProblemLayer.COMMON_CAPABILITY in receipt.compared_layers
    assert receipt.rejected_hypothesis_ids == ("upstream",)


def test_user_or_external_claim_cannot_be_directly_promoted_to_root_cause():
    with pytest.raises(BehaviorAdmissionError, match="promoted without falsification"):
        build_root_scope_receipt(
            (_hypothesis("selected", ProblemLayer.DOMAIN_ARCHITECTURE, HypothesisDisposition.SELECTED),),
            selected_hypothesis_id="selected",
            direct_user_or_external_claim_promoted_without_test=True,
        )


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


def test_parent_guidance_can_request_root_scope_help_without_fabricating_root_cause():
    receipt = require_behavior_problem_closure(
        BehaviorProblemSignals(
            problem_id="unknown-common-cause",
            problem_detected=True,
            parent_help_needed=True,
            evidence_refs=("evidence:repeat-across-domains",),
            local_recovery_attempts=("local hypotheses exhausted",),
            problem_record_required=True,
            problem_record_ref="audits/EVOLUTION_INDEX.json#EVO-ROOT-SCOPE-UPCALL",
        )
    )
    assert receipt.disposition == ProblemDisposition.PARENT_GUIDANCE_REQUIRED
    assert receipt.root_scope_receipt is None
    assert receipt.evolution_disposition == "PARENT_GUIDANCE_UPCALL"


def test_parent_guidance_requires_evidence_and_preserves_unaffected_work_signal():
    upcall = ParentGuidanceUpcall(
        escalation_id="ashare-escalation-001",
        domain_revision="0.3.0/profile7@candidate",
        problem_ref="audits/EVOLUTION_INDEX.json#EVO-20261016-COMMON-BEHAVIOR-1-3",
        severity="HIGH",
        impact="child cognition/action inheritance gap",
        blocking_scope="common behavior admission only",
        suspected_layer="COMMON_CAPABILITY",
        evidence_refs=(".uaos/CAPABILITIES.json", "tests/test_behavior_assurance.py"),
        local_recovery_attempts=("owner-native root-scope admission implemented",),
        requested_parent_help="confirm common behavior 1.3 compatibility",
        can_continue_unaffected_work=True,
        failure_class="FC-PREMATURE-PROBLEM-FRAMING-AND-REPAIR-BEFORE-ROOT-SCOPE-001",
        capability_id="governed_self_evolution",
        conflict_keys=("COMMON:behavior-assurance",),
    )
    payload = upcall.as_dict()
    assert payload["domain_id"] == "ashare"
    assert payload["can_continue_unaffected_work"] is True
    assert payload["suspected_layer"] == "COMMON_CAPABILITY"
    assert payload["evidence_refs"]
