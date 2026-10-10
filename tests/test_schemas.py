from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from ashare_event_agent.schemas import RecallGrade, RecallPoolPackage, RoleHypothesis, RuleProposal, SourceCompletionPackage, SourceReceipt


def receipt(source_id: str, **kw):
    base = dict(source_id=source_id, label=source_id, status="FULL", retrieval_method="STRUCTURED_API", retrieved_at=datetime.now(timezone.utc), source_refs=[f"ref:{source_id}"], links_expected=0, links_fetched=0, images_expected=0, images_read=0)
    base.update(kw)
    return SourceReceipt(**base)


def test_full_source_must_reconcile_images():
    with pytest.raises(ValidationError):
        receipt("P01", images_expected=3, images_read=2)


def test_premarket_must_reuse_five_pools():
    with pytest.raises(ValidationError):
        SourceCompletionPackage(receipts=[receipt("P01")], previous_five_pool_reused=False, previous_five_pool_ref="review-final")


def test_role_cannot_be_proved_by_height_only():
    with pytest.raises(ValidationError):
        RoleHypothesis(ticker="000001", name="测试", event_id="E1", role_type="THEME_LEADER", evidence_dimensions=["board_count", "height"], evidence=["4板", "最高板"], invalidation=["掉队"], confidence="high")


def test_recall_pool_rejects_leader_first_early_pruning():
    with pytest.raises(ValidationError):
        RecallPoolPackage(u0_tickers=["000001"], u1_candidates=[{"ticker":"000001","name":"测试","tier":"P0","event_ids":["E1"],"limit_up_paths":["1进2"],"knowable_reasoning":["盘前已知事件"]}], early_pruning_applied=True)


def test_u1_must_be_subset_of_u0():
    with pytest.raises(ValidationError):
        RecallPoolPackage(u0_tickers=["000001"], u1_candidates=[{"ticker":"000002","name":"测试2","tier":"P1","event_ids":["E1"],"limit_up_paths":["首板"],"knowable_reasoning":["盘前已知事件"]}])


def test_recall_grade_rejects_inconsistent_arithmetic():
    with pytest.raises(ValidationError):
        RecallGrade(actual_limit_up_total=10, excluded_scope_total=2, knowable_limit_up_total=6, u0_hits=3, u1_hits=2, u0_recall=0.9, u1_recall=2/6)


def test_recall_grade_accepts_reconciled_arithmetic():
    grade = RecallGrade(actual_limit_up_total=10, excluded_scope_total=2, knowable_limit_up_total=6, u0_hits=3, u1_hits=2, u0_recall=0.5, u1_recall=2/6)
    assert grade.u0_recall == 0.5


def test_rule_proposal_requires_regimes_counterexamples_and_replay_refs():
    with pytest.raises(ValidationError):
        RuleProposal(status="PROPOSE", rule_id="R1", owner="market_structure", hypothesis="h", detection_rule="d", prevention_rule="p")
