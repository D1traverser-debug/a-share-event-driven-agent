import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_current_skill_requires_domain_capability_and_caos_governance_contract():
    entry = (ROOT / "CAOS_ASHARE_ENTRY.md").read_text(encoding="utf-8")
    profile = load("config/DOMAIN_CAPABILITIES.json")
    governance = load("config/CAOS_GOVERNANCE.json")
    assert "config/DOMAIN_CAPABILITIES.json" in entry
    assert "DOMAIN:ashare" in entry
    assert profile["domain_id"] == "ashare"
    assert profile["policy"].startswith("CURRENT_SESSION_HANDSHAKE")
    assert profile["direct_domain_activation"] is True
    assert profile["profile_version"] == 1
    assert profile["caos_governance_ref"] == "config/CAOS_GOVERNANCE.json"
    assert profile["caos_governance_mode"] == "CHAT_GOVERNED_EXTERNAL__NO_RUNTIME_OR_API_DEPENDENCY"
    assert governance["governance"]["system"] == "CAOS"
    assert not (ROOT / ".uaos").exists()
    assert not (ROOT / "UAOS_SKILL.md").exists()
    assert not (ROOT / "continuity").exists()


def test_public_runtime_surface_is_domain_owned_not_a_cross_domain_controller():
    governance = load("config/CAOS_GOVERNANCE.json")
    assert governance["business_authority"]["identity"] == "ashare_event_agent/models.py:TaskContract.task_id"
    assert governance["business_authority"]["state"] == "ashare_event_agent/models.py:MarketDayState"
    boundary = governance["execution_boundary"]
    assert boundary["business_owner"] == "DOMAIN:ashare"
    assert boundary["direct_domain_activation"] is True
    assert boundary["parent_task_identity"] is False
    assert boundary["parent_business_state_mirror"] is False
    assert boundary["runtime_upcall"] is False
    assert boundary["caos_permission_grant"] is False
    assert (ROOT / "ashare_event_agent/plugin_server.py").is_file()
    assert (ROOT / "ashare_event_agent/task_visibility.py").is_file()
    assert not (ROOT / "ashare_event_agent/continuity.py").exists()


def test_domain_capabilities_remain_fail_closed_without_a_shadow_caos_runtime():
    profile = load("config/DOMAIN_CAPABILITIES.json")
    caps = {row["capability_id"]: row for row in profile["capabilities"]}
    assert {"premarket_research_and_freeze", "source_reconciliation", "ashare_market_day_orchestration", "preferred_market_microstructure", "runtime_execution"} <= set(caps)
    assert profile["caos_governance_mode"] == "CHAT_GOVERNED_EXTERNAL__NO_RUNTIME_OR_API_DEPENDENCY"
    assert "problem_response_floor" not in profile
    assert "problem_response_rule" not in profile
    assert all(row.get("side_channel_allowed") is False for row in caps.values())


def test_hosted_runtime_promotion_is_distinct_from_domain_business_ownership():
    authority = load("config/RUNTIME_AUTHORITY.json")
    assert authority["domain_business_identity_authority"] == "ashare_event_agent/models.py:TaskContract.task_id"
    assert authority["domain_business_ownership"].startswith("ALWAYS_ASHARE")
    assert authority["runtime_authority_enabled"] is False
    assert authority["required_promotion_gates"]["independent_audit_attestation"] != "PASS"
    assert authority["required_promotion_gates"]["preferred_level2_lane_live_validation"] != "PASS"
    assert authority["old_continuity_task_manifests_are_authority"] is False
    assert authority["external_governance_may_mirror_market_day_business_state"] is False
