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
