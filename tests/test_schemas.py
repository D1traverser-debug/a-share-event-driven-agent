from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from ashare_event_agent.schemas import RecallPoolPackage, RoleHypothesis, SourceCompletionPackage, SourceReceipt


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
