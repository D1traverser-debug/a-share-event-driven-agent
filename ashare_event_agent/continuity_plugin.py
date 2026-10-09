from __future__ import annotations

import os

from . import runtime_service as impl
from .continuity import continuity_metadata, list_resumable_states
from .mcp_contracts import MarketDayList, MarketDaySummary, READ_ONLY_TOOL
from .plugin_server import _publicize, mcp


def _continuity_summary(state) -> MarketDaySummary:
    raw = impl._summary(state, detail=False)
    clean = _publicize(raw)
    clean.update(continuity_metadata(state))
    return MarketDaySummary.model_validate(clean)


@mcp.tool(title="List Resumable A-share Tasks", annotations=READ_ONLY_TOOL, structured_output=True)
def list_resumable_tasks(limit: int = 20) -> MarketDayList:
    """List only Continuity-v2-safe USER tasks eligible for ordinary cross-chat continuation.

    TEST, FIXTURE, EVAL, SYSTEM_INFRA, MIGRATION, hidden/explicit-only and COMPLETE
    checkpoints are excluded by construction. Explicit task-id recovery remains available through
    the ordinary get-market-day tool for migrations and historical diagnostics.
    """
    states = list_resumable_states(impl.store, limit)
    return MarketDayList(tasks=[_continuity_summary(state) for state in states])


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
