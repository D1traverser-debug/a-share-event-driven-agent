from __future__ import annotations

import os

from . import plugin_server as base
from . import runtime_service as impl
from .continuity import continuity_metadata, list_resumable_states
from .mcp_contracts import MarketDayList, MarketDaySummary, READ_ONLY_TOOL

mcp = base.mcp


def _summary_from_state(state) -> MarketDaySummary:
    raw = impl._summary(state, detail=False)
    clean = base._publicize(raw)
    clean.update(continuity_metadata(state))
    return MarketDaySummary.model_validate(clean)


def _continuity_summary(raw: dict) -> MarketDaySummary:
    clean = base._publicize(raw)
    task_id = clean.get("task_id")
    if task_id:
        state = impl._load(task_id)
        clean.update(continuity_metadata(state))
    return MarketDaySummary.model_validate(clean)


# Existing tools in plugin_server resolve the module-level _summary symbol at
# call time. Replace that serializer once, so start/get/list/mutation results
# all expose the persisted continuity metadata rather than public-model defaults.
base._summary = _continuity_summary


@mcp.tool(title="List Resumable A-share Tasks", annotations=READ_ONLY_TOOL, structured_output=True)
def list_resumable_tasks(limit: int = 20) -> MarketDayList:
    """List only Continuity-v2-safe USER tasks eligible for ordinary cross-chat continuation.

    TEST, FIXTURE, EVAL, SYSTEM_INFRA, MIGRATION, hidden/explicit-only and COMPLETE
    checkpoints are excluded by construction. Explicit task-id recovery remains available through
    the ordinary get-market-day tool for migrations and historical diagnostics.
    """
    states = list_resumable_states(impl.store, limit)
    return MarketDayList(tasks=[_summary_from_state(state) for state in states])


def main() -> None:
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8000"))
    mcp.run(
        transport="streamable-http",
        host=host,
        port=port,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
    )


if __name__ == "__main__":
    main()
