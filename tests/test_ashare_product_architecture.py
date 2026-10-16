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
    assert "selection quality" in text.lower()
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


def test_opportunity_competition_is_separate_from_risk_gate_and_final_adjudication():
    g = graph()
    by_id = {row["id"]: row for row in g["nodes"]}
    candidates = [row for row in g["nodes"] if row.get("decision_group") == "opportunity_slate"]
    assert {row["id"] for row in candidates} == {
        "event_alpha_candidate_slate",
        "market_structure_candidate_slate",
    }
    assert all(row["depends_on"] == ["recall_pool"] for row in candidates)

    opportunity = by_id["opportunity_slate_adjudication"]
    assert opportunity["coordination"] == "OWNER_ADJUDICATION"
    assert opportunity["adjudicator"] == "opportunity_decision_owner"
    assert set(row["id"] for row in candidates) <= set(opportunity["depends_on"])

    risk = by_id["risk_feasibility_assessment"]
    assert risk["coordination"] == "FAN_OUT_FAN_IN"
    assert "opportunity_slate_adjudication" in risk["depends_on"]
    assert "tonghuashun_level2_market_lane" in risk["depends_on"]
    assert risk["owner"] == "execution_risk_owner"

    final = by_id["trade_decision_adjudication"]
    assert final["coordination"] == "OWNER_ADJUDICATION"
    assert final["adjudicator"] == "trade_decision_owner"
    assert "risk_feasibility_assessment" in final["depends_on"]
    assert by_id["candidate_counterevidence_review"]["advisory_only"] is True


def test_revision_scope_is_dependency_bounded():
    impacted = set(downstream_nodes(graph(), "tonghuashun_level2_market_lane"))
    assert "source_reconciliation" in impacted
    assert "risk_feasibility_assessment" in impacted
    assert "trade_decision_adjudication" in impacted
    assert "premarket_audit_and_freeze" in impacted
    assert "resolve_trading_day" not in impacted
    assert "stockbase_context" not in impacted


def test_specialized_source_owners_are_not_collapsed_into_one_vendor():
    assert tuple(MARKET_DATA_LANES["XUANGUTONG_DINGPAN"].owns) == DINGPAN_POOL_SEMANTICS
    assert "depth_orderflow" in MARKET_DATA_LANES["TONGHUASHUN_LEVEL2"].owns
    assert "corporate_hard_event" in MARKET_DATA_LANES["OFFICIAL_FACTS"].owns
    assert "XUANGUTONG_DINGPAN" not in MARKET_DATA_LANES["TONGHUASHUN_LEVEL2"].fallback_lanes


def test_problem_cognition_is_parent_owned_while_domain_learning_and_quality_metrics_remain_mandatory():
    profile = json.loads((ROOT / ".uaos/CAPABILITIES.json").read_text(encoding="utf-8"))
    policy = json.loads((ROOT / "config/policy.json").read_text(encoding="utf-8"))
    assert profile["uaos_deliberation_policy_ref"].endswith("config/DELIBERATION_POLICY.json")
    assert profile["hosted_cognition_semantics"] == {
        "source": "CURRENT_UAOS_DELIBERATION_POLICY",
        "local_overrides": "NONE",
    }
    assert "problem_response_floor" not in profile
    assert "problem_response_rule" not in profile
    assert policy["learning"]["problem_cognition_owner"] == "CURRENT_UAOS_DELIBERATION_POLICY"
    assert "RISK_ADAPTIVE" in policy["learning"]["problem_cognition_rule"]
    assert policy["learning"]["domain_market_research_is_separate_from_generic_problem_cognition"] is True
    assert policy["learning"]["single_day_promotion_forbidden"] is True
    assert policy["orchestration"]["risk_feasibility_is_constraint_not_candidate_vote"] is True
    assert policy["review"]["grade_recall_separately_from_final_selection"] is True
    assert set(policy["learning"]["replay_required_metrics"]) == {
        "u1_recall",
        "activated_positive_rate",
        "activated_downside_rate",
        "execution_feasibility_rate",
    }
