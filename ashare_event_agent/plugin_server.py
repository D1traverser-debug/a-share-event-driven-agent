from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

from mcp.server.mcpserver import MCPServer
from mcp.types import CallToolResult, ResourceLink, TextContent
from pydantic import Field

from . import runtime_service as impl
from .task_visibility import list_resumable_states, task_metadata
from .mcp_contracts import MarketDayList, MarketDaySummary, READ_ONLY_TOOL, STATE_WRITE_TOOL
from .models import ArtifactKind
from .schemas import (
    AttributionPackage, EventLedgerPackage, ExecutionPlan, FreezeCard, GateDecision,
    IndustryResearchPackage, LearningAudit, MarketStructurePackage, OutcomePackage,
    RecallGrade, RecallPoolPackage, ReplayEval, RuleProposal, SourceCompletionPackage,
    StockBaseContext, UniversePackage,
)

JSON_MIME = "application/json"
TEXT_MIME = "text/markdown; charset=utf-8"


def _publicize(raw: dict) -> dict:
    clean = dict(raw)
    task_id = clean.get("task_id")
    artifacts = {}
    for kind, value in (clean.get("artifacts") or {}).items():
        item = dict(value)
        path_value = item.pop("path", "")
        mime = JSON_MIME if kind in {ArtifactKind.PREMARKET_SNAPSHOT_JSON.value, ArtifactKind.LEARNING_REPORT_JSON.value} else TEXT_MIME
        item.update({"file_name": Path(path_value).name, "resource_uri": f"ashare-artifact://{task_id}/{kind}", "mime_type": mime})
        artifacts[kind] = item
    if "artifacts" in clean:
        clean["artifacts"] = artifacts
    clean.pop("contract", None)
    clean.pop("gates", None)
    return clean


def _summary(raw: dict) -> MarketDaySummary:
    clean = _publicize(raw)
    task_id = clean.get("task_id")
    if task_id:
        clean.update(task_metadata(impl._load(task_id)))
    return MarketDaySummary.model_validate(clean)


def _summary_from_state(state) -> MarketDaySummary:
    return _summary(impl._summary(state, detail=False))


def _result(raw: dict) -> CallToolResult:
    summary = _summary(raw)
    content = [TextContent(type="text", text=f"A-share market-day task {summary.task_id}: {summary.status} at {summary.current_stage}. {summary.next_action}")]
    for kind, artifact in (summary.artifacts or {}).items():
        if artifact.exists:
            content.append(ResourceLink(type="resource_link", uri=artifact.resource_uri, name=artifact.file_name, mime_type=artifact.mime_type, description=f"{kind} artifact"))
    return CallToolResult(content=content, structured_content=summary.model_dump(mode="json"))


def _artifact_bytes(task_id: str, kind: str) -> bytes:
    state = impl._load(task_id)
    ak = ArtifactKind(kind)
    artifact = state.artifacts.get(ak)
    if artifact is None or not artifact.exists:
        raise FileNotFoundError(kind)
    path = Path(artifact.path).resolve()
    root = impl.RUNS_DIR.resolve()
    if not path.is_relative_to(root):
        raise ValueError("artifact escaped configured runs directory")
    return path.read_bytes()


mcp = MCPServer(
    "A-share Event-Driven Agent",
    instructions=(
        "Use for A-share premarket stock-recommendation research, post-close review, recall grading, and replay-governed learning. "
        "UAOS owns cross-domain task identity and continuation; this runtime exposes domain-local market-day checkpoints only. "
        "Follow the current UAOS task plus domain next_action exactly after current trading-day reconciliation. "
        "The runtime owns freeze integrity, legal transitions, schemas, StockBase permission boundaries, recall/completion gates, and rule-promotion eligibility. "
        "The model owns public research, industry reasoning, role hypotheses, red-team judgments, and attribution within those contracts. "
        "An audit-tool call records an audit decision but does not by itself prove reviewer independence."
    ),
)


@mcp.resource("ashare-artifact://{task_id}/{kind}", mime_type="application/octet-stream")
def read_artifact(task_id: str, kind: str) -> bytes:
    """Read a persisted A-share agent artifact for a market-day task."""
    return _artifact_bytes(task_id, kind)


@mcp.tool(title="Start A-share Market Day", annotations=STATE_WRITE_TOOL, structured_output=True)
def start_market_day(
    trading_date: Annotated[str, Field(description="China-market trading date, YYYY-MM-DD")],
    prompt: Annotated[str, Field(description="User task/intent for this market day")],
    stockbase_ref: str | None = None,
    prior_review_ref: str | None = None,
    mode: str = "LIVE_DAY",
) -> MarketDaySummary:
    """Start a durable domain market-day runtime after UAOS resolves the current task/trading day."""
    return _summary(impl.start_market_day(trading_date, prompt, stockbase_ref, prior_review_ref, mode))


@mcp.tool(title="Get A-share Market Day", annotations=READ_ONLY_TOOL, structured_output=True)
def get_market_day(task_id: str, detail: bool = True) -> MarketDaySummary:
    """Load one persisted A-share domain checkpoint without changing state."""
    return _summary(impl.get_market_day(task_id, detail))


@mcp.tool(title="List Recent A-share Market Days", annotations=READ_ONLY_TOOL, structured_output=True)
def list_recent_market_days(limit: int = 20, include_complete: bool = False) -> MarketDayList:
    """List recent durable A-share domain checkpoints for inspection."""
    return MarketDayList(tasks=[_summary(x) for x in impl.list_recent_market_days(limit, include_complete)])


@mcp.tool(title="List Resumable A-share Tasks", annotations=READ_ONLY_TOOL, structured_output=True)
def list_resumable_tasks(limit: int = 20) -> MarketDayList:
    """List safe domain-local runtime candidates for UAOS reconciliation; this is not a cross-domain task registry."""
    states = list_resumable_states(impl.store, limit)
    return MarketDayList(tasks=[_summary_from_state(state) for state in states])


@mcp.tool(title="Record Governance Context", annotations=STATE_WRITE_TOOL, structured_output=True)
def record_governance_context(task_id: str, refs: list[str], notes: list[str] | None = None) -> MarketDaySummary:
    """Record current governance/source refs for the domain task; external mirrors never become control authority by being recorded here."""
    return _summary(impl.record_governance_context(task_id, refs, notes))


@mcp.tool(title="Submit Freeze Card", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_freeze_card(task_id: str, payload: FreezeCard) -> MarketDaySummary:
    """Record the immutable premarket information boundary. Future market or news data must not enter premarket reasoning after this cutoff."""
    return _summary(impl.submit_freeze_card(task_id, payload.model_dump(mode="json")))


@mcp.tool(title="Submit Source Completion", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_source_completion(task_id: str, payload: SourceCompletionPackage) -> MarketDaySummary:
    """Record P01-P09 source completion, LINK-ALL and image counts, retrieval methods, explicit gaps, point-in-time availability, and prior-review five-pool reuse receipts."""
    return _summary(impl.submit_source_completion(task_id, payload.model_dump(mode="json")))


@mcp.tool(title="Submit Source Audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_source_audit(task_id: str, decision: GateDecision) -> MarketDaySummary:
    """Submit a source-completion audit decision. PASS must satisfy source/image/count/time contracts; independent certification additionally requires a distinct reviewer execution receipt."""
    return _summary(impl.submit_source_audit(task_id, decision.model_dump(mode="json")))


@mcp.tool(title="Submit Event Ledger", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_event_ledger(task_id: str, payload: EventLedgerPackage) -> MarketDaySummary:
    """Submit the all-news event ledger including new/continuation/rotation/background, rumor, negative, disproved, calendar, and no-trade events."""
    return _summary(impl.submit_event_ledger(task_id, payload.model_dump(mode="json")))


@mcp.tool(title="Submit Industry Research", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_industry_research(task_id: str, payload: IndustryResearchPackage) -> MarketDaySummary:
    """Submit L0-L5+ industry graphs, product/BOM/material/equipment/process/customer/order/capacity economics, bidirectional transmission, and stock mappings."""
    return _summary(impl.submit_industry_research(task_id, payload.model_dump(mode="json")))


@mcp.tool(title="Record StockBase Context", annotations=STATE_WRITE_TOOL, structured_output=True)
def record_stockbase_context(task_id: str, payload: StockBaseContext) -> MarketDaySummary:
    """Record the exact StockBase version/read receipt used for premarket recall. Premarket mode is enforced READ_ONLY and cannot write StockBase."""
    return _summary(impl.record_stockbase_context(task_id, payload.model_dump(mode="json")))


@mcp.tool(title="Submit Universe Audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_universe_audit(task_id: str, universe: UniversePackage, decision: GateDecision) -> MarketDaySummary:
    """Submit Universe plus its audit decision. PASS is illegal while eligible mapped stocks or research nodes are silently omitted; independent certification needs separate reviewer evidence."""
    return _summary(impl.submit_universe_audit(task_id, universe.model_dump(mode="json"), decision.model_dump(mode="json")))


@mcp.tool(title="Submit Market Structure", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_market_structure(task_id: str, payload: MarketStructurePackage) -> MarketDaySummary:
    """Submit factual height ladders plus evidence-backed leader/mid-cap/card-position/pioneer/rotation hypotheses. Board count alone cannot prove a role."""
    return _summary(impl.submit_market_structure(task_id, payload.model_dump(mode="json")))


@mcp.tool(title="Submit Recall Pool", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_recall_pool(task_id: str, payload: RecallPoolPackage) -> MarketDaySummary:
    """Submit U0/U1 recall-first candidate pools. Execution preferences and Leader-First ranking may not prune the research recall universe."""
    return _summary(impl.submit_recall_pool(task_id, payload.model_dump(mode="json")))


@mcp.tool(title="Submit Execution Plan", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_execution_plan(task_id: str, payload: ExecutionPlan) -> MarketDaySummary:
    """Submit the narrow U3 plan: at most four execution roles with triggers, invalidations, comparative why-not-peers evidence, backup chain, and explicit NO TRADE conditions."""
    return _summary(impl.submit_execution_plan(task_id, payload.model_dump(mode="json")))


@mcp.tool(title="Submit Premarket Red-Team Audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_premarket_audit(task_id: str, decision: GateDecision) -> Annotated[CallToolResult, MarketDaySummary]:
    """Submit the premarket red-team decision. PASS freezes the snapshot cryptographically; the call alone does not establish independent-review assurance."""
    return _result(impl.submit_premarket_audit(task_id, decision.model_dump(mode="json")))


@mcp.tool(title="Start Post-close Review", annotations=STATE_WRITE_TOOL, structured_output=True)
def start_postclose_review(task_id: str) -> MarketDaySummary:
    """Start post-close review from an immutable FROZEN premarket checkpoint. The runtime verifies the frozen hash before opening the review stages."""
    return _summary(impl.start_postclose_review(task_id))


@mcp.tool(title="Submit Market Outcomes", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_market_outcomes(task_id: str, payload: OutcomePackage) -> MarketDaySummary:
    """Record official post-close outcome pools and reconciled counts. This data is review-only and cannot alter the frozen premarket package."""
    return _summary(impl.submit_market_outcomes(task_id, payload.model_dump(mode="json")))


@mcp.tool(title="Submit Attribution", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_attribution(task_id: str, payload: AttributionPackage) -> MarketDaySummary:
    """Attribute every in-scope limit-up and key failure against what was knowable before the freeze, preserving premarket evidence separately from post-close facts."""
    return _summary(impl.submit_attribution(task_id, payload.model_dump(mode="json")))


@mcp.tool(title="Submit Recall Grading", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_recall_grading(task_id: str, payload: RecallGrade) -> MarketDaySummary:
    """Grade knowable limit-up recall for U0/U1 and reconcile miss classes against frozen attribution rather than accepting independent self-scored hit counts."""
    return _summary(impl.submit_recall_grading(task_id, payload.model_dump(mode="json")))


@mcp.tool(title="Submit Learning Audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_learning_audit(task_id: str, payload: LearningAudit) -> MarketDaySummary:
    """Audit process errors and candidate hypotheses after review. This stage may propose learning targets but cannot directly change durable rules."""
    return _summary(impl.submit_learning_audit(task_id, payload.model_dump(mode="json")))


@mcp.tool(title="Submit Rule Proposal", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_rule_proposal(task_id: str, payload: RuleProposal) -> MarketDaySummary:
    """Record one bounded rule hypothesis with single owner, detection/prevention logic, regimes, counterexamples, or explicit reasoned N_A. One day never auto-promotes a rule."""
    return _summary(impl.submit_rule_proposal(task_id, payload.model_dump(mode="json")))


@mcp.tool(title="Submit Replay Evaluation", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_replay_eval(task_id: str, payload: ReplayEval) -> MarketDaySummary:
    """Evaluate a rule proposal across frozen historical cases. Promotion eligibility requires mechanical evidence, multiple cases/regimes, positive/negative samples, no future contamination, and no regression."""
    return _summary(impl.submit_replay_eval(task_id, payload.model_dump(mode="json")))


@mcp.tool(title="Record Review Knowledge Writeback", annotations=STATE_WRITE_TOOL, structured_output=True)
def record_review_writeback(task_id: str, status: str, refs: list[str] | None = None, notes: list[str] | None = None) -> MarketDaySummary:
    """Record the real review-side StockBase/knowledge writeback receipt, or explicit N_A. Premarket has no equivalent mutation tool by design."""
    return _summary(impl.record_review_writeback(task_id, status, refs, notes))


@mcp.tool(title="Submit Final Review Audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_final_audit(task_id: str, decision: GateDecision) -> MarketDaySummary:
    """Submit the final review decision over frozen integrity, attribution, grading and learning boundaries; independent certification still requires attested reviewer execution evidence."""
    return _summary(impl.submit_final_audit(task_id, decision.model_dump(mode="json")))


def main() -> None:
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8000"))
    mcp.run(transport="streamable-http", host=host, port=port, streamable_http_path="/mcp", stateless_http=True, json_response=True)


if __name__ == "__main__":
    main()
