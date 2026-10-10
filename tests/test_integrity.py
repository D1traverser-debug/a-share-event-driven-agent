from ashare_event_agent.integrity import (
    attribution_integrity_errors,
    execution_integrity_errors,
    recall_grade_integrity_errors,
    recall_integrity_errors,
    replay_coherence_errors,
    universe_integrity_errors,
)
from ashare_event_agent.schemas import (
    AttributionPackage,
    ExecutionPlan,
    IndustryResearchPackage,
    OutcomePackage,
    RecallGrade,
    RecallPoolPackage,
    ReplayEval,
    RuleProposal,
    UniversePackage,
)


def mapping(ticker: str, node_id: str = "N1", event_id: str = "E1", eligible: bool = True):
    return {
        "event_id": event_id,
        "node_id": node_id,
        "ticker": ticker,
        "name": ticker,
        "mainboard_eligible": eligible,
        "directness": "A",
        "business_stage": "mass production",
    }


def industry():
    return IndustryResearchPackage(
        nodes=[
            {"node_id":"N1","event_id":"E1","level":5,"name":"node1","economics":"x","direction":"BENEFIT"},
            {"node_id":"N2","event_id":"E1","level":5,"name":"node2","economics":"y","direction":"BENEFIT"},
        ],
        transmission_paths=["path"],
        mappings=[mapping("000001", "N1"), mapping("000002", "N2")],
        max_depth_by_event={"E1":5},
        sweeps_completed=2,
        stop_reason="done",
    )


def recall():
    return RecallPoolPackage(
        u0_tickers=["000001", "000002"],
        u1_candidates=[{
            "ticker":"000001","name":"A","tier":"P0","event_ids":["E1"],
            "limit_up_paths":["首板"],"knowable_reasoning":["known"]
        }],
    )


def test_universe_cannot_silently_omit_eligible_mapped_ticker():
    pkg = UniversePackage(
        mappings=[mapping("000001", "N1")],
        node_exclusions={},
        all_event_nodes_exhausted=True,
        stop_reason="done",
    )
    errors = universe_integrity_errors(industry(), pkg)
    assert any("000002" in error and "silently omitted" in error for error in errors)


def test_universe_can_explicitly_exclude_eligible_ticker_with_reason():
    pkg = UniversePackage(
        mappings=[mapping("000001", "N1")],
        excluded=["000002"],
        exclusion_reasons={"000002":"hard risk"},
        all_event_nodes_exhausted=True,
        stop_reason="done",
    )
    assert universe_integrity_errors(industry(), pkg) == []


def test_node_without_any_mapping_requires_explicit_node_exclusion():
    base = IndustryResearchPackage(
        nodes=[
            {"node_id":"N1","event_id":"E1","level":5,"name":"node1","economics":"x","direction":"BENEFIT"},
            {"node_id":"N2","event_id":"E1","level":5,"name":"node2","economics":"y","direction":"BENEFIT"},
        ],
        transmission_paths=["path"],
        mappings=[mapping("000001", "N1")],
        max_depth_by_event={"E1":5},
        sweeps_completed=2,
        stop_reason="done",
    )
    pkg = UniversePackage(
        mappings=[mapping("000001", "N1")],
        all_event_nodes_exhausted=True,
        stop_reason="done",
    )
    assert any("N2" in error for error in universe_integrity_errors(base, pkg))


def test_u0_must_equal_active_universe_tickers():
    universe = UniversePackage(
        mappings=[mapping("000001"), mapping("000002", "N2")],
        all_event_nodes_exhausted=True,
        stop_reason="done",
    )
    bad = RecallPoolPackage(
        u0_tickers=["000001"],
        u1_candidates=[{
            "ticker":"000001","name":"A","tier":"P0","event_ids":["E1"],
            "limit_up_paths":["首板"],"knowable_reasoning":["known"]
        }],
    )
    assert any("000002" in error for error in recall_integrity_errors(universe, bad))


def test_u3_must_descend_from_u1():
    plan = ExecutionPlan(
        candidates=[{
            "ticker":"000002","name":"B","slot":"PRIMARY_LEADER","strategy":"leader",
            "trigger":["go"],"invalidation":["stop"],"why_this":["x"],"why_not_peers":["A weaker"]
        }],
        no_trade_conditions=["bad tape"],
        backup_chain=["none"],
        first_read_answer="B",
    )
    assert any("000002" in error for error in execution_integrity_errors(recall(), plan))


def test_attribution_membership_is_recomputed_from_frozen_recall():
    outcomes = OutcomePackage(
        outcomes=[{"ticker":"000001","name":"A","result":"LIMIT_UP","board_count_after":1}],
        pool_counts={"limit_up":1},
        source_refs=["x"],
    )
    attr = AttributionPackage(actual_limit_ups=[{
        "ticker":"000001","name":"A","knowable_before_freeze":True,"in_u0":True,"in_u1":False,
        "miss_class":"HIT"
    }])
    errors = attribution_integrity_errors(outcomes, recall(), attr)
    assert any("in_u1 disagrees" in error for error in errors)


def test_attribution_outcome_sets_must_reconcile():
    outcomes = OutcomePackage(
        outcomes=[{"ticker":"000002","name":"B","result":"BROKEN","board_count_after":0}],
        pool_counts={"broken":1},
        source_refs=["x"],
    )
    attr = AttributionPackage(actual_limit_ups=[{
        "ticker":"000001","name":"A","knowable_before_freeze":True,"in_u0":True,"in_u1":True,
        "miss_class":"HIT"
    }])
    errors = attribution_integrity_errors(outcomes, recall(), attr)
    assert any("actual_limit_ups" in error for error in errors)
    assert any("broken_boards" in error for error in errors)


def test_recall_grade_is_bound_to_attribution_counts():
    attr = AttributionPackage(actual_limit_ups=[{
        "ticker":"000001","name":"A","knowable_before_freeze":True,"in_u0":True,"in_u1":True,
        "miss_class":"HIT"
    }])
    grade = RecallGrade(
        actual_limit_up_total=2,
        excluded_scope_total=1,
        knowable_limit_up_total=1,
        u0_hits=1,
        u1_hits=0,
        u0_recall=1.0,
        u1_recall=0.0,
    )
    errors = recall_grade_integrity_errors(attr, grade)
    assert any("u1_hits" in error for error in errors)


def test_replay_status_must_match_rule_proposal_status():
    proposal = RuleProposal(status="N_A", no_change_reason="no durable rule change")
    replay = ReplayEval(
        status="HOLD",
        positive_samples=0,
        negative_samples=0,
        decision_reason="no rule",
    )
    assert replay_coherence_errors(proposal, replay) == ["N_A rule proposal requires N_A replay result"]
