import json
from pathlib import Path

from ashare_event_agent.orchestration import validate_orchestration
from ashare_event_agent.source_contracts import DINGPAN_POOL_SEMANTICS, MARKET_DATA_LANES

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


def test_policy_and_orchestration_mirrors_are_identical():
    assert (ROOT / "config/policy.json").read_bytes() == (ROOT / "ashare_event_agent/resources/policy.json").read_bytes()
    assert (ROOT / "config/MARKET_DAY_ORCHESTRATION.json").read_bytes() == (ROOT / "ashare_event_agent/resources/market_day_orchestration.json").read_bytes()
    validate_orchestration(json.loads((ROOT / "config/MARKET_DAY_ORCHESTRATION.json").read_text(encoding="utf-8")))


def test_caos_governance_binding_keeps_market_day_business_identity_domain_owned():
    governance = json.loads((ROOT / "config/CAOS_GOVERNANCE.json").read_text(encoding="utf-8"))
    capabilities = json.loads((ROOT / "config/DOMAIN_CAPABILITIES.json").read_text(encoding="utf-8"))
    authority = json.loads((ROOT / "config/RUNTIME_AUTHORITY.json").read_text(encoding="utf-8"))
    assert governance["governance"]["system"] == "CAOS"
    assert governance["governance"]["mode"] == "CHAT_GOVERNED_EXTERNAL"
    assert governance["governance"]["runtime_dependency"] is False
    assert governance["governance"]["source_mutation"] == "FORBIDDEN"
    assert governance["business_authority"]["identity"] == "ashare_event_agent/models.py:TaskContract.task_id"
    assert governance["business_authority"]["state"] == "ashare_event_agent/models.py:MarketDayState"
    assert governance["execution_boundary"]["parent_task_identity"] is False
    assert governance["execution_boundary"]["parent_business_state_mirror"] is False
    assert capabilities["caos_governance_ref"] == "config/CAOS_GOVERNANCE.json"
    assert capabilities["owner_native_behavior_admission"] == "ashare_event_agent.behavior_assurance"
    assert authority["caos_runtime_dependency"] is False
    assert authority["external_governance_may_mirror_market_day_business_state"] is False
    assert not (ROOT / ".uaos").exists()
    assert not (ROOT / "UAOS_SKILL.md").exists()
    assert not (ROOT / "continuity").exists()
    assert not (ROOT / "config/cutover_status.json").exists()


def test_specialized_market_data_lanes_are_explicit():
    assert MARKET_DATA_LANES["TONGHUASHUN_LEVEL2"].label.startswith("同花顺")
    assert tuple(MARKET_DATA_LANES["XUANGUTONG_DINGPAN"].owns) == DINGPAN_POOL_SEMANTICS
    policy = json.loads((ROOT / "config/policy.json").read_text(encoding="utf-8"))
    assert policy["sources"]["preferred_microstructure_lane"] == "TONGHUASHUN_LEVEL2"
    assert policy["sources"]["dingpan_five_pool_lane"] == "XUANGUTONG_DINGPAN"
    assert policy["sources"]["weaker_data_must_lower_assurance"] is True


def test_runtime_promotion_is_separate_from_domain_business_ownership():
    authority = json.loads((ROOT / "config/RUNTIME_AUTHORITY.json").read_text(encoding="utf-8"))
    gates = authority["required_promotion_gates"]
    assert gates
    assert authority["domain_business_ownership"].startswith("ALWAYS_ASHARE")
    if authority["runtime_authority_enabled"]:
        assert all(status == "PASS" for status in gates.values())
    entry = (ROOT / "CAOS_ASHARE_ENTRY.md").read_text(encoding="utf-8")
    assert "CAOS" in entry and "does not create a parent task ID" in entry
    assert "A-share" in entry
