import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_manifest_and_capability_profile_bind_current_common_behavior_contract():
    manifest = load(".uaos/MANIFEST.json")
    capabilities = load(".uaos/CAPABILITIES.json")
    controller = "D1traverser-debug/universal-agent-os@main"

    assert tuple(int(part) for part in manifest["schema_version"].split(".")) >= (3, 3)
    assert manifest["controller"] == controller
    assert manifest["status"] == "DIRECT_DOMAIN_WORK_PLANE_ACTIVE"
    assert manifest["binding_status"] == "UAOS_CONTROL_PLANE_ACTIVE"
    assert manifest["binding"]["controller_ref"] == f"{controller}:CURRENT_SYSTEM.json"
    assert manifest["binding"]["common_behavior_assurance_ref"].endswith("config/COMMON_BEHAVIOR_ASSURANCE.json")
    assert manifest["binding"]["common_behavior_assurance_min"] == "1.3.0"
    assert manifest["binding"]["deliberation_policy_ref"].endswith("config/DELIBERATION_POLICY.json")
    assert manifest["binding"]["domain_health_escalation_ref"].endswith("config/DOMAIN_HEALTH_ESCALATION_POLICY.json")
    assert manifest["domain_authority"]["behavior_assurance_ref"] == "ashare_event_agent/behavior_assurance.py"
    assert manifest["domain_authority"]["root_scope_admission_ref"].endswith("require_root_scope_admission")
    assert manifest["domain_authority"]["evolution_evidence_entrypoint"] == "audits/EVOLUTION_INDEX.json"

    assert tuple(int(part) for part in capabilities["schema_version"].split(".")) >= (3, 4)
    assert capabilities["profile_version"] >= 8
    assert capabilities["uaos_common_behavior_assurance_min"] == "1.3.0"
    assert capabilities["uaos_common_capabilities_min"] == "1.6.0"
    assert capabilities["uaos_deliberation_policy_ref"].endswith("config/DELIBERATION_POLICY.json")
    assert capabilities["hosted_cognition_semantics"] == {
        "source": "CURRENT_UAOS_DELIBERATION_POLICY",
        "local_overrides": "NONE",
    }
    assert capabilities["owner_native_behavior_admission"] == "ashare_event_agent.behavior_assurance"
    semantics = capabilities["hosted_behavior_semantics"]
    assert "LOCAL_RECOVERY_ATTEMPT" in semantics["recover_before_user_escalation"]
    assert "USER_OR_EXTERNAL_FRAMING_IS_EVIDENCE_NOT_ROOT_AUTHORITY" in semantics["root_scope_admission"]
    assert "TYPED_EVOLUTION_DISPOSITION" in semantics["evolution_before_action"]
    assert "ROOT_SCOPE_AND_EVOLUTION_ADMISSION_PRECEDE" in semantics["problem_to_action_closure"]
    assert "DURABLE_PROBLEM_REF" in semantics["parent_guidance"]


def test_skill_requires_root_scope_evolution_recovery_closure_and_durable_problem_history():
    skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    assert "Common Behavior Assurance 1.3" in skill
    assert "root-scope receipt" in skill
    assert "TYPED_EVOLUTION_DISPOSITION" in skill
    assert "recommendation-only is not terminal" in skill
    assert "durable causal evidence" in skill
    assert "does not transfer A-share market-day identity" in skill
    assert "audits/EVOLUTION_INDEX.json" in skill


def test_evolution_index_exposes_1_3_owner_adoption_and_rejects_declaration_only_path():
    index = load("audits/EVOLUTION_INDEX.json")
    assert index["role"] == "OWNER_NATIVE_CANONICAL_EVOLUTION_EVIDENCE_ENTRYPOINT"
    entries = {entry["evolution_id"]: entry for entry in index["entries"]}
    entry = entries["EVO-20261016-COMMON-BEHAVIOR-1-3-ROOT-SCOPE-ADOPTION"]
    assert entry["failure_class"] == "FC-COMMON-BEHAVIOR-1-3-OWNER-ADOPTION-OPEN"
    assert "declaration-only version bump" in "\n".join(entry["rejected_paths"])
    assert entry["parent_governance_ref"] == "UAOS:EVO-20261016-PROBLEM-COGNITION-ACTION-TRANSACTION"
