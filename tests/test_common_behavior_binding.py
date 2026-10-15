import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_manifest_and_capability_profile_bind_current_common_behavior_contract():
    manifest = load(".uaos/MANIFEST.json")
    capabilities = load(".uaos/CAPABILITIES.json")

    assert manifest["schema_version"] == "3.1"
    assert manifest["binding"]["common_behavior_assurance_ref"].endswith("config/COMMON_BEHAVIOR_ASSURANCE.json")
    assert manifest["binding"]["common_behavior_assurance_min"] == "1.2.0"
    assert manifest["binding"]["domain_health_escalation_ref"].endswith("config/DOMAIN_HEALTH_ESCALATION_POLICY.json")
    assert manifest["domain_authority"]["behavior_assurance_ref"] == "ashare_event_agent/behavior_assurance.py"
    assert manifest["domain_authority"]["evolution_evidence_entrypoint"] == "audits/EVOLUTION_INDEX.json"

    assert capabilities["schema_version"] == "3.2"
    assert capabilities["profile_version"] == 6
    assert capabilities["uaos_common_behavior_assurance_min"] == "1.2.0"
    assert capabilities["owner_native_behavior_admission"] == "ashare_event_agent.behavior_assurance"
    semantics = capabilities["hosted_behavior_semantics"]
    assert "LOCAL_RECOVERY_ATTEMPT" in semantics["recover_before_user_escalation"]
    assert "RECOMMENDATION_ONLY_NOT_TERMINAL" in semantics["problem_to_action_closure"]
    assert "STRUCTURED_UPCALL" in semantics["parent_guidance"]


def test_skill_requires_recovery_closure_structured_parent_guidance_and_durable_problem_history():
    skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    assert "## Problem response, recovery and parent guidance" in skill
    assert "attempt proportionate local recovery" in skill
    assert "recommendation-only is not terminal" in skill
    assert "structured upcall" in skill
    assert "does not transfer A-share market-day identity" in skill
    assert "audits/EVOLUTION_INDEX.json" in skill


def test_evolution_index_exposes_current_behavior_adoption_failure_class_and_governance_basis():
    index = load("audits/EVOLUTION_INDEX.json")
    assert index["role"] == "OWNER_NATIVE_CANONICAL_EVOLUTION_EVIDENCE_ENTRYPOINT"
    entry = index["entries"][0]
    assert entry["failure_class"] == "FC-INHERITED-BEHAVIOR-DECLARATION-WITHOUT-UNIFORM-OPERATIONAL-PROOF-002"
    assert "FROZEN_REQUIREMENTS_v2.1.md" in entry["governance_basis"]
    assert "declaration-only JSON update" in "\n".join(entry["rejected_paths"])
