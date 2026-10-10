import json
from pathlib import Path


def test_rule_ownership_is_unique():
    ownership = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    seen = set()
    for keys in ownership.values():
        for key in keys:
            assert key not in seen, key
            seen.add(key)


def test_reference_mirrors_are_identical():
    source = Path("references")
    skill = Path("skills/a-share-event-driven-agent/references")
    package = Path("ashare_event_agent/resources/references")
    names = {p.name for p in source.glob("*.md")}
    assert names == {p.name for p in skill.glob("*.md")} == {p.name for p in package.glob("*.md")}
    for name in names:
        b = (source / name).read_bytes()
        assert b == (skill / name).read_bytes() == (package / name).read_bytes()


def test_policy_mirror_is_identical():
    assert Path("config/policy.json").read_bytes() == Path("ashare_event_agent/resources/policy.json").read_bytes()


def test_cutover_never_reactivates_notion_drive_control_plane():
    cutover = json.loads(Path("config/cutover_status.json").read_text(encoding="utf-8"))
    assert cutover["operational_governance_authority"] == "GITHUB_MAIN_CONTINUITY"
    assert cutover["business_checkpoint_authority_when_runtime_disabled"] == "GITHUB_CONTINUITY_TASK_MANIFEST_HANDOFF"
    assert cutover["continuity"]["external_mirrors_may_not_override_task_state"] is True
    assert cutover["external_system_roles"]["notion"] == "SOURCE_KNOWLEDGE_MIRROR_ONLY"
    assert cutover["external_system_roles"]["google_drive"] == "SOURCE_ARTIFACT_MIRROR_ONLY"


def test_runtime_promotion_is_separate_from_governance_migration():
    cutover = json.loads(Path("config/cutover_status.json").read_text(encoding="utf-8"))
    gates = cutover["required_gates"]
    assert gates
    if cutover["runtime_authority_enabled"]:
        assert all(status == "PASS" for status in gates.values())
    skill = Path("skills/a-share-event-driven-agent/SKILL.md").read_text(encoding="utf-8")
    recovery = Path("references/recovery.md").read_text(encoding="utf-8")
    assert "Never route business control back to Notion/Drive" in skill
    assert "Do not fall back to Notion/Drive as an operating controller" in recovery
