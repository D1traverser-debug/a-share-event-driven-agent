from datetime import datetime, timezone

from ashare_event_agent.checks import audit_source_completion
from ashare_event_agent.schemas import SourceCompletionPackage, SourceReceipt


def test_fixed_p01_p09_are_required():
    pkg = SourceCompletionPackage(
        receipts=[SourceReceipt(source_id="P01", label="x", status="FULL", retrieval_method="OFFICIAL", retrieved_at=datetime.now(timezone.utc), source_refs=["x"])],
        previous_five_pool_reused=True,
        previous_five_pool_ref="review-final",
    )
    errors = audit_source_completion(pkg)
    assert any("P02" in e and "P09" in e for e in errors)
