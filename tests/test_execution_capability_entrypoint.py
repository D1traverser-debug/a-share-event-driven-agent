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


def test_independent_audit_is_not_falsely_declared_executable():
    profile = json.loads((ROOT / "continuity/EXECUTION_CAPABILITIES.json").read_text(encoding="utf-8"))
    capabilities = {row["capability_id"]: row for row in profile["capabilities"]}
    auditor = capabilities["strict_isolated_auditor"]
    assert auditor["assurance_ceiling"] == "DECLARED_ONLY"
    assert auditor["executor_type"] == "UNAVAILABLE"
    assert not auditor["safe_degraded_modes"]
    assert "distinct_reviewer_execution_context" in auditor["required_tools"]
    assert "SOURCE_AUDIT" in auditor["scope"] and "FINAL_AUDIT" in auditor["scope"]


def test_cutover_requires_independent_audit_attestation():
    cutover = json.loads((ROOT / "config/cutover_status.json").read_text(encoding="utf-8"))
    assert cutover["required_gates"]["independent_audit_attestation"] != "PASS"
    assert cutover["runtime_authority_enabled"] is False
