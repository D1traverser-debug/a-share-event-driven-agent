import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_skill_and_continuity_index_require_execution_capability_handshake():
    skill = (ROOT / "skills/a-share-event-driven-agent/SKILL.md").read_text(encoding="utf-8")
    index = (ROOT / "continuity/TASK_INDEX.md").read_text(encoding="utf-8")
    profile = json.loads((ROOT / "continuity/EXECUTION_CAPABILITIES.json").read_text(encoding="utf-8"))

    assert "continuity/EXECUTION_CAPABILITIES.json" in skill
    assert "continuity/EXECUTION_CAPABILITIES.json" in index
    assert "session" in skill.lower() and "handshake" in skill.lower()
    assert profile["execution_readiness_contract"] == "1.0"
    assert profile["owner"] == "A_SHARE_MARKET_AGENT"
