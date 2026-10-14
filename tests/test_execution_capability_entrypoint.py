import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_current_skill_requires_capability_handshake_and_no_domain_controller_namespace():
    skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    profile = json.loads((ROOT / ".uaos/CAPABILITIES.json").read_text(encoding="utf-8"))
    assert ".uaos/CAPABILITIES.json" in skill
    assert "current" in skill.lower()
    assert profile["domain_id"] == "ashare"
    assert profile["policy"].startswith("CURRENT_SESSION_HANDSHAKE")
    assert not (ROOT / "continuity").exists()


def test_public_runtime_surface_is_domain_runtime_not_cross_domain_controller():
    manifest = json.loads((ROOT / ".uaos/MANIFEST.json").read_text(encoding="utf-8"))
    adapter = json.loads((ROOT / ".uaos/ADAPTER.json").read_text(encoding="utf-8"))
    assert manifest["controller"] == "D1traverser-debug/universal-agent-os@main"
    assert adapter["task_identity_authority"] == "UAOS"
    assert adapter["cross_chat_continuity_authority"] == "UAOS"
    assert (ROOT / "ashare_event_agent/plugin_server.py").is_file()
    assert (ROOT / "ashare_event_agent/task_visibility.py").is_file()
    assert not (ROOT / "ashare_event_agent/continuity.py").exists()


def test_live_source_and_audit_capability_remain_fail_closed():
    profile = json.loads((ROOT / ".uaos/CAPABILITIES.json").read_text(encoding="utf-8"))
    caps = {row["capability_id"]: row for row in profile["capabilities"]}
    assert "premarket_research_and_freeze" in caps
    assert "source_reconciliation" in caps
    assert "runtime_execution" in caps
    assert all(row.get("side_channel_allowed") is False for row in caps.values())


def test_runtime_authority_requires_current_promotion_evidence():
    authority = json.loads((ROOT / "config/RUNTIME_AUTHORITY.json").read_text(encoding="utf-8"))
    assert authority["runtime_authority_enabled"] is False
    assert authority["required_promotion_gates"]["independent_audit_attestation"] != "PASS"
    assert authority["old_continuity_task_manifests_are_authority"] is False
