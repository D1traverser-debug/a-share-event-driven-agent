import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_current_skill_requires_capability_handshake_and_no_second_controller_namespace():
    skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    profile = json.loads((ROOT / ".uaos/CAPABILITIES.json").read_text(encoding="utf-8"))
    assert ".uaos/CAPABILITIES.json" in skill
    assert "DOMAIN:ashare" in skill
    assert profile["domain_id"] == "ashare"
    assert profile["policy"].startswith("CURRENT_SESSION_HANDSHAKE")
    assert profile["direct_domain_activation"] is True
    assert profile["uaos_common_capabilities_min"] == "1.6.0"
    assert profile["uaos_deliberation_policy_ref"].endswith("config/DELIBERATION_POLICY.json")
    assert not (ROOT / "continuity").exists()


def test_public_runtime_surface_is_child_business_runtime_not_cross_domain_controller():
    manifest = json.loads((ROOT / ".uaos/MANIFEST.json").read_text(encoding="utf-8"))
    adapter = json.loads((ROOT / ".uaos/ADAPTER.json").read_text(encoding="utf-8"))
    assert manifest["parent_control_plane"] == "D1traverser-debug/universal-agent-os@main"
    assert manifest["domain_authority"]["market_day_identity"] == "ashare_event_agent/models.py:TaskContract.task_id"
    assert adapter["parent_router_identity_authority"] == "UAOS"
    assert adapter["domain_market_day_identity_authority"] == "ashare_event_agent/models.py:TaskContract.task_id"
    assert adapter["parent_child_id_equality_required"] is False
    assert "OPAQUE_CHILD" in adapter["parent_reference_semantics"]
    assert (ROOT / "ashare_event_agent/plugin_server.py").is_file()
    assert (ROOT / "ashare_event_agent/task_visibility.py").is_file()
    assert not (ROOT / "ashare_event_agent/continuity.py").exists()


def test_live_source_cognition_and_runtime_capability_remain_fail_closed_without_shadow_parent_algorithm():
    profile = json.loads((ROOT / ".uaos/CAPABILITIES.json").read_text(encoding="utf-8"))
    caps = {row["capability_id"]: row for row in profile["capabilities"]}
    assert "premarket_research_and_freeze" in caps
    assert "source_reconciliation" in caps
    assert "ashare_market_day_orchestration" in caps
    assert "preferred_market_microstructure" in caps
    assert "runtime_execution" in caps
    assert profile["hosted_cognition_semantics"] == {
        "source": "CURRENT_UAOS_DELIBERATION_POLICY",
        "local_overrides": "NONE",
    }
    assert "problem_response_floor" not in profile
    assert "problem_response_rule" not in profile
    assert all(row.get("side_channel_allowed") is False for row in caps.values())


def test_hosted_runtime_promotion_is_distinct_from_domain_business_ownership():
    authority = json.loads((ROOT / "config/RUNTIME_AUTHORITY.json").read_text(encoding="utf-8"))
    assert authority["domain_business_identity_authority"] == "ashare_event_agent/models.py:TaskContract.task_id"
    assert authority["domain_business_ownership"].startswith("ALWAYS_ASHARE")
    assert authority["runtime_authority_enabled"] is False
    assert authority["required_promotion_gates"]["independent_audit_attestation"] != "PASS"
    assert authority["required_promotion_gates"]["preferred_level2_lane_live_validation"] != "PASS"
    assert authority["old_continuity_task_manifests_are_authority"] is False
    assert authority["parent_may_mirror_market_day_business_state"] is False
