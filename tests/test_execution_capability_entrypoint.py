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
    assert profile["execution_readiness_contract"] == "1.1"
    assert profile["owner"] == "A_SHARE_MARKET_AGENT"


def test_public_runtime_surface_is_single_and_runner_is_not_production_entrypoint():
    manifest = json.loads((ROOT / "continuity/AGENT_MANIFEST.json").read_text(encoding="utf-8"))
    profile = json.loads((ROOT / "continuity/EXECUTION_CAPABILITIES.json").read_text(encoding="utf-8"))
    capabilities = {row["capability_id"]: row for row in profile["capabilities"]}

    assert manifest["runtime"]["public_entrypoint"] == "ashare_event_agent/plugin_server.py"
    harness = manifest["harness"]["reference_executor_harness"]
    assert harness["ref"] == "ashare_event_agent/runner.py"
    assert harness["production_entrypoint"] is False

    state_machine = capabilities["market_day_state_machine"]
    assert state_machine["executor_ref"] == "ashare_event_agent/plugin_server.py"
    assert "runner.AgentRuntime" not in state_machine["invocation_path"]


def test_live_source_contract_is_not_falsely_advertised_as_native_adapter():
    profile = json.loads((ROOT / "continuity/EXECUTION_CAPABILITIES.json").read_text(encoding="utf-8"))
    capabilities = {row["capability_id"]: row for row in profile["capabilities"]}
    source = capabilities["live_source_acquisition"]

    assert source["executor_type"] == "EXTERNAL_SESSION_CONNECTORS"
    assert source["executor_ref"] is None
    assert source["contract_ref"] == "ashare_event_agent/source_contracts.py"


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
