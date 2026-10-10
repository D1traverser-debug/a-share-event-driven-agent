from datetime import datetime, timezone

from ashare_event_agent.checks import audit_event_times, audit_source_completion
from ashare_event_agent.schemas import EventLedgerPackage, FreezeCard, SourceCompletionPackage, SourceReceipt


def full_receipt(source_id: str, content_time: datetime) -> SourceReceipt:
    return SourceReceipt(
        source_id=source_id,
        label=source_id,
        status="FULL",
        retrieval_method="OFFICIAL",
        retrieved_at=datetime.now(timezone.utc),
        content_max_available_at=content_time,
        source_refs=[f"ref:{source_id}"],
        links_expected=0,
        links_fetched=0,
        images_expected=0,
        images_read=0,
    )


def test_fixed_p01_p09_are_required():
    freeze_time = datetime(2026, 10, 12, 1, 14, 59, tzinfo=timezone.utc)
    pkg = SourceCompletionPackage(
        receipts=[full_receipt("P01", freeze_time)],
        previous_five_pool_reused=True,
        previous_five_pool_ref="review-final",
    )
    errors = audit_source_completion(pkg)
    assert any("P02" in e and "P09" in e for e in errors)


def test_source_content_after_freeze_is_rejected():
    freeze = FreezeCard(
        trading_date="2026-10-12",
        max_public_info_time="2026-10-12T09:14:59+08:00",
        max_market_data_time="2026-10-12T09:14:59+08:00",
    )
    receipts = [
        full_receipt(f"P{i:02d}", datetime(2026, 10, 12, 1, 14, 59, tzinfo=timezone.utc))
        for i in range(1, 10)
    ]
    receipts[3] = full_receipt("P04", datetime(2026, 10, 12, 1, 15, 0, tzinfo=timezone.utc))
    pkg = SourceCompletionPackage(
        receipts=receipts,
        previous_five_pool_reused=True,
        previous_five_pool_ref="review-final",
    )
    errors = audit_source_completion(pkg, freeze)
    assert any("P04 contains post-freeze content" in error for error in errors)


def test_calendar_event_available_after_freeze_is_not_exempt():
    freeze = FreezeCard(
        trading_date="2026-10-12",
        max_public_info_time="2026-10-12T09:14:59+08:00",
        max_market_data_time="2026-10-12T09:14:59+08:00",
    )
    pkg = EventLedgerPackage(
        events=[{
            "event_id": "E1",
            "title": "未来日历事件",
            "classification": "CALENDAR",
            "event_type": "calendar",
            "available_at": "2026-10-12T09:15:00+08:00",
            "evidence_refs": ["official:calendar"],
            "catalyst_facts": ["scheduled event"],
        }],
        evidence_ledger=[{
            "claim": "calendar event exists",
            "source_ref": "official:calendar",
            "available_at": "2026-10-12T09:14:00+08:00",
            "evidence_type": "official",
        }],
        stop_reason="fixture",
    )
    errors = audit_event_times(pkg, freeze.max_public_info_time)
    assert any("post-freeze event availability" in error for error in errors)
