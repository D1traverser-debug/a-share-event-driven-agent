from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .schemas import EventLedgerPackage, FreezeCard, SourceCompletionPackage

FIXED_SOURCES = {f"P{i:02d}" for i in range(1, 10)}


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def audit_source_completion(pkg: SourceCompletionPackage, freeze: FreezeCard | None = None) -> list[str]:
    errors: list[str] = []
    by_id = {r.source_id for r in pkg.receipts}
    missing = sorted(FIXED_SOURCES - by_id)
    if missing:
        errors.append(f"missing fixed sources: {missing}")
    for r in pkg.receipts:
        if r.status == "FULL":
            if r.links_expected is None or r.links_fetched != r.links_expected:
                errors.append(f"{r.source_id} link reconciliation failed")
            if r.images_expected is None or r.images_read != r.images_expected:
                errors.append(f"{r.source_id} image reconciliation failed")
        if r.status != "BLOCKED" and r.content_max_available_at is None:
            errors.append(f"{r.source_id} missing content_max_available_at point-in-time binding")
        if freeze is not None and r.content_max_available_at is not None and r.content_max_available_at > freeze.max_public_info_time:
            errors.append(f"{r.source_id} contains post-freeze content: {r.content_max_available_at.isoformat()}")
        if freeze is not None and r.published_at is not None and r.published_at > freeze.max_public_info_time:
            errors.append(f"{r.source_id} receipt published_at is post-freeze: {r.published_at.isoformat()}")
    if not pkg.previous_five_pool_reused:
        errors.append("previous five-pool snapshot not reused")
    if pkg.repeated_five_pool_fetch_performed:
        errors.append("premarket repeated five-pool fetch is forbidden")
    return errors


def audit_event_times(pkg: EventLedgerPackage, max_public_info_time) -> list[str]:
    errors: list[str] = []
    for event in pkg.events:
        if event.available_at > max_public_info_time:
            errors.append(f"post-freeze event availability in premarket ledger: {event.event_id}")
    for evidence in pkg.evidence_ledger:
        if evidence.available_at > max_public_info_time:
            errors.append(f"post-freeze evidence in premarket ledger: {evidence.claim[:60]}")
    return errors


def write_json(path: str | Path, payload) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(payload, "model_dump"):
        payload = payload.model_dump(mode="json")
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return p
