from __future__ import annotations

from .models import MarketDayState, ResumeVisibility, Stage, TaskClass
from .store import SQLiteStateStore


def is_default_visible_candidate(state: MarketDayState) -> bool:
    """Return True only for child market-day states safe to surface as ordinary resumable business candidates."""
    contract = state.contract
    return (
        contract.task_class == TaskClass.USER
        and contract.resume_eligible
        and contract.resume_visibility == ResumeVisibility.DEFAULT
        and state.stage != Stage.COMPLETE
    )


def list_resumable_states(store: SQLiteStateStore, limit: int = 20) -> list[MarketDayState]:
    """List child-owned market-day checkpoints eligible for domain resume selection.

    This function is not a cross-domain or parent task registry. The A-share domain
    owns these child identities; UAOS may only route the domain and retain an opaque
    selected child reference for parent continuity.
    """
    scan_limit = max(1, min(max(limit, 20) * 5, 100))
    states = store.list_recent(scan_limit)
    eligible = [state for state in states if is_default_visible_candidate(state)]
    return eligible[: max(1, min(limit, 100))]


def task_metadata(state: MarketDayState) -> dict[str, object]:
    contract = state.contract
    return {
        "task_class": contract.task_class.value,
        "resume_eligible": contract.resume_eligible,
        "resume_visibility": contract.resume_visibility.value,
        "contract_version": contract.contract_version,
        "runtime_version": contract.runtime_version,
        "skill_version": contract.skill_version,
    }
