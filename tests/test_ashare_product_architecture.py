import json
from pathlib import Path

from ashare_event_agent.orchestration import downstream_nodes, ready_nodes, validate_orchestration
from ashare_event_agent.source_contracts import DINGPAN_POOL_SEMANTICS, MARKET_DATA_LANES

ROOT = Path(__file__).resolve().parents[1]


def graph() -> dict:
    return json.loads((ROOT / "config/MARKET_DAY_ORCHESTRATION.json").read_text(encoding="utf-8"))


def test_product_requirements_define_recommendation_specific_outcomes():
    text = (ROOT / "docs/product_requirements.md").read_text(encoding="utf-8")
    assert "A-share main-board" in text
    assert "同花顺 / Level-2" in text
    assert "选股通 Dingpan" in text
    assert "NO TRADE" in text
    assert "post-close" in text
    assert "Acceptance map" in text


def test_market_day_graph_is_acyclic_child_owned_and_not_peer_chat():
    g = graph()
    validate_orchestration(g)
    assert g["business_owner"] == "DOMAIN:ashare"
    assert "NO_UNBOUNDED_PEER_CHAT" in g["decision_model"]


def test_parallel_source_lanes_are_ready_after_freeze_without_global_wave_blocking():
    g = graph()
    assert ready_nodes(g, []) == ("resolve_trading_day",)
    after_day = set(ready_nodes(g, ["resolve_trading_day"]))
    assert {"define_freeze_boundary", "previous_five_pool_snapshot", "stockbase_context"} <= after_day
    after_freeze = set(ready_nodes(g, ["resolve_trading_day", "define_freeze_boundary"]))
    assert {
        "p01_p09_research_sources",
        "official_hard_fact_lane",
        "tonghuashun_level2_market_lane",
        "previous_five_pool_snapshot",
        "stockbase_context",
    } <= after_freeze


def test_candidate_competition_is_u1_bounded_then_owned_adjudication():
    g = graph()
    by_id = {row["id"]: row for row in g["nodes"]}
    candidates = [row for row in g["nodes"] if row.get("decision_group") == "u3_candidate_slate"]
    assert {row["id"] for row in candidates} == {
        "event_alpha_candidate_slate",
        "market_structure_candidate_slate",
        "buyability_execution_candidate_slate",
    }
    assert all(row["depends_on"] == ["recall_pool"] for row in candidates)
    adjudication = by_id["trade_decision_adjudication"]
    assert adjudication["coordination"] == "OWNER_ADJUDICATION"
    assert adjudication["adjudicator"] == "trade_decision_owner"
    assert set(row["id"] for row in candidates) <= set(adjudication["depends_on"])
    assert by_id["candidate_counterevidence_review"]["advisory_only"] is True


def test_revision_scope_is_dependency_bounded():
    impacted = set(downstream_nodes(graph(), "tonghuashun_level2_market_lane"))
    assert "source_reconciliation" in impacted
    assert "buyability_execution_candidate_slate" in impacted
    assert "trade_decision_adjudication" in impacted
    assert "premarket_audit_and_freeze" in impacted
    assert "resolve_trading_day" not in impacted
    assert "stockbase_context" not in impacted


def test_specialized_source_owners_are_not_collapsed_into_one_vendor():
    assert tuple(MARKET_DATA_LANES["XUANGUTONG_DINGPAN"].owns) == DINGPAN_POOL_SEMANTICS
    assert "depth_orderflow" in MARKET_DATA_LANES["TONGHUASHUN_LEVEL2"].owns
    assert "corporate_hard_event" in MARKET_DATA_LANES["OFFICIAL_FACTS"].owns
    assert "XUANGUTONG_DINGPAN" not in MARKET_DATA_LANES["TONGHUASHUN_LEVEL2"].fallback_lanes


def test_problem_response_and_learning_are_both_mandatory_but_single_day_promotion_is_forbidden():
    profile = json.loads((ROOT / ".uaos/CAPABILITIES.json").read_text(encoding="utf-8"))
    policy = json.loads((ROOT / "config/policy.json").read_text(encoding="utf-8"))
    assert profile["problem_response_floor"] == [
        "MICRO_DIAGNOSIS",
        "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT",
        "GOVERNING_ASSUMPTION_CHALLENGE",
        "EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH",
    ]
    assert policy["learning"]["every_problem_requires_research_and_reflection"] is True
    assert policy["learning"]["single_day_promotion_forbidden"] is True
