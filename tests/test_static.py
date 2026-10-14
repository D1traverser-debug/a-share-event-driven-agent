import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_rule_ownership_is_unique():
    ownership = json.loads((ROOT / "config/rule_ownership.json").read_text(encoding="utf-8"))
    seen = set()
    for keys in ownership.values():
        for key in keys:
            assert key not in seen, key
            seen.add(key)


def test_reference_mirrors_are_identical():
    source = ROOT / "references"
    skill = ROOT / "skills/a-share-event-driven-agent/references"
    package = ROOT / "ashare_event_agent/resources/references"
    names = {p.name for p in source.glob("*.md")}
    assert names == {p.name for p in skill.glob("*.md")} == {p.name for p in package.glob("*.md")}
    for name in names:
        b = (source / name).read_bytes()
        assert b == (skill / name).read_bytes() == (package / name).read_bytes()


def test_policy_mirror_is_identical():
    assert (ROOT / "config/policy.json").read_bytes() == (ROOT / "ashare_event_agent/resources/policy.json").read_bytes()


def test_current_control_binding_is_uaos_only():
    manifest = json.loads((ROOT / ".uaos/MANIFEST.json").read_text(encoding="utf-8"))
    adapter = json.loads((ROOT / ".uaos/ADAPTER.json").read_text(encoding="utf-8"))
    authority = json.loads((ROOT / "config/RUNTIME_AUTHORITY.json").read_text(encoding="utf-8"))
    assert manifest["controller"] == "D1traverser-debug/universal-agent-os@main"
    assert adapter["legacy_controller_compatibility"] == "NONE"
    assert authority["external_system_roles"]["notion"] == "SOURCE_OR_KNOWLEDGE_ONLY"
    assert authority["external_system_roles"]["google_drive"] == "SOURCE_OR_ARTIFACT_ONLY"
    assert not (ROOT / "continuity").exists()
    assert not (ROOT / "config/cutover_status.json").exists()


def test_runtime_promotion_is_separate_from_controller_authority():
    authority = json.loads((ROOT / "config/RUNTIME_AUTHORITY.json").read_text(encoding="utf-8"))
    gates = authority["required_promotion_gates"]
    assert gates
    if authority["runtime_authority_enabled"]:
        assert all(status == "PASS" for status in gates.values())
    skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    assert "UAOS owns task identity" in skill
    assert "Notion" not in skill or "controller" not in skill.lower()
