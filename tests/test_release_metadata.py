import json
from pathlib import Path

from ashare_event_agent.models import CURRENT_CONTRACT_VERSION, CURRENT_RUNTIME_VERSION

ROOT = Path(__file__).resolve().parents[1]


def test_release_metadata_matches_runtime_contract():
    plugin = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert plugin["version"] == CURRENT_RUNTIME_VERSION == "0.3.0"
    assert 'version = "0.3.0"' in pyproject
    assert CURRENT_CONTRACT_VERSION == "2.1"


def test_user_facing_entries_describe_risk_as_gate_not_competing_vote():
    text = "\n".join([
        (ROOT / "README.md").read_text(encoding="utf-8"),
        (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8"),
    ]).lower()
    assert "risk/buyability is not a third bullish opinion" in text
    assert "block" in text and "cannot" in text and "u3" in text
    assert "three independent u1-bounded candidate views" not in text
