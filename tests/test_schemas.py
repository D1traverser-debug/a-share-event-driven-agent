from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from ashare_event_agent.schemas import (
    AttributionPackage,
    ExecutionCandidate,
    FreezeCard,
    LearningAudit,
    RecallGrade,
    RecallPoolPackage,
    RoleHypothesis,
    RuleProposal,
    SourceCompletionPackage,
    SourceReceipt,
    UniversePackage,
)


def receipt(source_id: str, **kw):
    base = dict(
        source_id=source_id,
        label=source_id,
        status="FULL",
        retrieval_method="STRUCTURED_API",
        retrieved_at=datetime.now(timezone.utc),
        content_max_available_at=datetime(2026, 10, 12, 1, 14, 59, tzinfo=timezone.utc),
        source_refs=[f"ref:{source_id}"],
        links_expected=0,
        links_fetched=0,
        images_expected=0,
        images_read=0,
    )
    base.update(kw)
    return SourceReceipt(**base)


def test_full_source_must_reconcile_images():
    with pytest.raises(ValidationError):
        receipt("P01", images_expected=3, images_read=2)


def test_full_source_requires_explicit_counts_and_point_in_time_binding():
    with pytest.raises(ValidationError):
        SourceReceipt(
            source_id="P01",
            label="P01",
            status="FULL",
            retrieval_method="STRUCTURED_API",
            retrieved_at=datetime.now(timezone.utc),
            source_refs=["ref:P01"],
        )


def test_freeze_card_rejects_post_boundary_time():
    with pytest.raises(ValidationError):
        FreezeCard(
            trading_date="2026-10-12",
            max_public_info_time="2026-10-12T09:15:00+08:00",
            max_market_data_time="2026-10-12T09:14:59+08:00",
            auction_used=False,
        )


def test_freeze_card_requires_timezone_aware_times():
    with pytest.raises(ValidationError):
        FreezeCard(
            trading_date="2026-10-12",
            max_public_info_time="2026-10-12T09:14:59",
            max_market_data_time="2026-10-12T09:14:59",
        )


def test_premarket_must_reuse_five_pools():
    with pytest.raises(ValidationError):
        SourceCompletionPackage(receipts=[receipt("P01")], previous_five_pool_reused=False, previous_five_pool_ref="review-final")


def test_source_ids_must_be_unique():
    with pytest.raises(ValidationError):
        SourceCompletionPackage(
            receipts=[receipt("P01"), receipt("P01")],
            previous_five_pool_reused=True,
            previous_five_pool_ref="review-final",
        )


def test_role_cannot_be_proved_by_height_only():
    with pytest.raises(ValidationError):
        RoleHypothesis(ticker="000001", name="测试", event_id="E1", role_type="THEME_LEADER", evidence_dimensions=["board_count", "height"], evidence=["4板", "最高板"], invalidation=["掉队"], confidence="high")


def test_recall_pool_rejects_leader_first_early_pruning():
    with pytest.raises(ValidationError):
        RecallPoolPackage(u0_tickers=["000001"], u1_candidates=[{"ticker":"000001","name":"测试","tier":"P0","event_ids":["E1"],"limit_up_paths":["1进2"],"knowable_reasoning":["盘前已知事件"]}], early_pruning_applied=True)


def test_u1_must_be_subset_of_u0():
    with pytest.raises(ValidationError):
        RecallPoolPackage(u0_tickers=["000001"], u1_candidates=[{"ticker":"000002","name":"测试2","tier":"P1","event_ids":["E1"],"limit_up_paths":["首板"],"knowable_reasoning":["盘前已知事件"]}])


def test_execution_candidate_requires_why_not_peers():
    with pytest.raises(ValidationError):
        ExecutionCandidate(
            ticker="000001",
            name="测试",
            slot="PRIMARY_LEADER",
            strategy="leader",
            trigger=["trigger"],
            invalidation=["fail"],
            why_this=["strongest"],
            why_not_peers=[],
        )


def test_universe_exclusions_require_exact_reasons():
    with pytest.raises(ValidationError):
        UniversePackage(
            mappings=[{
                "event_id":"E1","node_id":"N1","ticker":"000001","name":"测试","mainboard_eligible":True,
                "directness":"A","business_stage":"mass production"
            }],
            excluded=["000002"],
            all_event_nodes_exhausted=True,
            stop_reason="done",
        )


def test_attribution_sets_are_mutually_exclusive():
    row = {
        "ticker":"000001","name":"测试","knowable_before_freeze":True,"in_u0":True,"in_u1":True,
        "miss_class":"HIT"
    }
    with pytest.raises(ValidationError):
        AttributionPackage(actual_limit_ups=[row], broken_boards=[row])


def test_recall_grade_rejects_inconsistent_arithmetic():
    with pytest.raises(ValidationError):
        RecallGrade(actual_limit_up_total=10, excluded_scope_total=2, knowable_limit_up_total=6, u0_hits=3, u1_hits=2, u0_recall=0.9, u1_recall=2/6)


def test_recall_grade_accepts_reconciled_arithmetic():
    grade = RecallGrade(actual_limit_up_total=10, excluded_scope_total=2, knowable_limit_up_total=6, u0_hits=3, u1_hits=2, u0_recall=0.5, u1_recall=2/6)
    assert grade.u0_recall == 0.5


def test_learning_audit_requires_hypothesis_or_no_change_reason():
    with pytest.raises(ValidationError):
        LearningAudit()


def test_rule_proposal_requires_regimes_counterexamples_and_replay_refs():
    with pytest.raises(ValidationError):
        RuleProposal(status="PROPOSE", rule_id="R1", owner="market_structure", hypothesis="h", detection_rule="d", prevention_rule="p")


def test_na_rule_proposal_requires_reason():
    with pytest.raises(ValidationError):
        RuleProposal(status="N_A")
