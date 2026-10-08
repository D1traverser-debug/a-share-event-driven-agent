from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
import tempfile
import time

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

PORT = 8766
URL = f"http://127.0.0.1:{PORT}/mcp"
REQUIRED = {
    "start_market_day","get_market_day","list_recent_market_days","record_governance_context",
    "submit_freeze_card","submit_source_completion","submit_source_audit","submit_event_ledger",
    "submit_industry_research","record_stockbase_context","submit_universe_audit","submit_market_structure",
    "submit_recall_pool","submit_execution_plan","submit_premarket_audit","start_postclose_review",
    "submit_market_outcomes","submit_attribution","submit_recall_grading","submit_learning_audit",
    "submit_rule_proposal","submit_replay_eval","record_review_writeback","submit_final_audit",
}
READ_ONLY = {"get_market_day", "list_recent_market_days"}


def wait_port(timeout=15.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", PORT), timeout=.5):
                return
        except OSError:
            time.sleep(.2)
    raise RuntimeError("MCP server did not start")


async def verify():
    async with streamable_http_client(URL) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            listed = await session.list_tools()
            tools = {t.name: t for t in listed.tools}
            if set(tools) != REQUIRED:
                raise RuntimeError(f"tool inventory mismatch missing={REQUIRED-set(tools)} extra={set(tools)-REQUIRED}")
            for name, tool in tools.items():
                d = tool.model_dump(by_alias=True, exclude_none=True)
                ann = d.get("annotations") or {}
                if ann.get("readOnlyHint") != (name in READ_ONLY):
                    raise RuntimeError(f"readOnlyHint mismatch: {name}")
                if ann.get("destructiveHint") is not False or ann.get("openWorldHint") is not False:
                    raise RuntimeError(f"unsafe annotations: {name}")
                if not d.get("title") or len((d.get("description") or "").strip()) < 50:
                    raise RuntimeError(f"weak descriptor: {name}")
                out = d.get("outputSchema")
                if not isinstance(out, dict) or out.get("type") != "object":
                    raise RuntimeError(f"missing object output schema: {name}")
            result = await session.call_tool("start_market_day", arguments={"trading_date":"2026-10-08","prompt":"smoke only"})
            if result.is_error or not isinstance(result.structured_content, dict):
                raise RuntimeError(f"start_market_day failed: {result.content}")
            if result.structured_content.get("current_stage") != "FREEZE":
                raise RuntimeError(f"unexpected start result: {result.structured_content}")
            print(f"PASS: {len(tools)} typed/annotated MCP tools and structured start result")


def main():
    env = os.environ.copy()
    env["ASHARE_EVENT_DATA_DIR"] = tempfile.mkdtemp(prefix="ashare-event-mcp-")
    env["MCP_HOST"] = "127.0.0.1"
    env["MCP_PORT"] = str(PORT)
    proc = subprocess.Popen([sys.executable, "-m", "ashare_event_agent.plugin_server"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        wait_port()
        asyncio.run(verify())
    finally:
        proc.terminate()
        try: proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill(); proc.wait(timeout=5)
        if proc.returncode not in {0, -15} and proc.stdout:
            print(proc.stdout.read())


if __name__ == "__main__":
    main()
