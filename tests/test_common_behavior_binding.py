import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_caos_governance_contract_and_domain_owner_boundary():
    governance = load("config/CAOS_GOVERNANCE.json")
    capabilities = load("config/DOMAIN_CAPABILITIES.json")
    authority = load("config/RUNTIME_AUTHORITY.json")
    assert governance["governance"]["system"] == "CAOS"
    assert governance["governance"]["mode"] == "CHAT_GOVERNED_EXTERNAL"
    assert governance["governance"]["runtime_dependency"] is False
    assert governance["governance"]["source_mutation"] == "FORBIDDEN"
    assert governance["business_authority"]["repository"] == "D1traverser-debug/a-share-event-driven-agent@main"
    assert governance["business_authority"]["identity"] == "ashare_event_agent/models.py:TaskContract.task_id"
    assert governance["business_authority"]["state"] == "ashare_event_agent/models.py:MarketDayState"
    assert governance["execution_boundary"]["direct_domain_activation"] is True
    assert governance["execution_boundary"]["parent_task_identity"] is False
    assert governance["execution_boundary"]["parent_business_state_mirror"] is False
    assert governance["execution_boundary"]["runtime_upcall"] is False
    assert capabilities["caos_governance_ref"] == "config/CAOS_GOVERNANCE.json"
    assert capabilities["domain_id"] == "ashare"
    assert capabilities["direct_domain_activation"] is True
    assert capabilities["owner_native_behavior_admission"] == "ashare_event_agent.behavior_assurance"
    assert capabilities["domain_evolution_evidence_entrypoint"] == "audits/EVOLUTION_INDEX.json"
    assert "LOCAL_RECOVERY_ATTEMPT" in capabilities["owner_native_behavior_semantics"]["recover_before_user_escalation"]
    assert "USER_OR_EXTERNAL_FRAMING_IS_EVIDENCE_NOT_ROOT_AUTHORITY" in capabilities["owner_native_behavior_semantics"]["root_scope_admission"]
    assert "TYPED_EVOLUTION_DISPOSITION" in capabilities["owner_native_behavior_semantics"]["evolution_before_action"]
    assert "CAOS_ACTIVE_CHAT" in capabilities["owner_native_behavior_semantics"]["caos_governance_review"]
    assert authority["caos_runtime_dependency"] is False
    assert authority["external_governance_may_mirror_market_day_business_state"] is False
    assert not (ROOT / ".uaos").exists()
    assert not (ROOT / "UAOS_SKILL.md").exists()


def test_evolution_index_records_caos_migration_without_rewriting_history():
    index = load("audits/EVOLUTION_INDEX.json")
    rows = {row["evolution_id"]: row for row in index["entries"]}
    entry = rows["EVO-20261114-CAOS-GOVERNANCE-MIGRATION"]
    assert entry["status"] == "CANDIDATE__CI_PENDING"
    assert entry["selected_architecture"] == "CAOS_CHAT_GOVERNANCE__A_SHARE_OWNS_MARKET_DAY_STATE"
    assert "business state" in entry["preserved_invariants"].lower()
