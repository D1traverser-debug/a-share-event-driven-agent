from __future__ import annotations

from .models import MarketDayState, ResumeVisibility, Stage, TaskClass
from .store import SQLiteStateStore


def is_default_visible_candidate(state: MarketDayState) -> bool:
    """Return True only for domain-runtime states safe to surface as ordinary resumable business candidates."""
    contract = state.contract
    return (
        contract.task_class == TaskClass.USER
        and contract.resume_eligible
        and contract.resume_visibility == ResumeVisibility.DEFAULT
        and state.stage != Stage.COMPLETE
    )


def list_resumable_states(store: SQLiteStateStore, limit: int = 20) -> list[MarketDayState]:
    """List domain-local runtime checkpoints eligible for explicit UAOS task reconciliation.

    This function is not a cross-domain task registry. UAOS decides task identity and
    continuation; this function only exposes safe domain-runtime checkpoint candidates.
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
