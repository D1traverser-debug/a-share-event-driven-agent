from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "ashare_event_agent" / "plugin_server.py"
RUNTIME = ROOT / "ashare_event_agent" / "runtime_service.py"
SCHEMAS = ROOT / "ashare_event_agent" / "schemas.py"
MODELS = ROOT / "ashare_event_agent" / "models.py"


def fail(msg: str) -> None:
    raise SystemExit(msg)

ownership = json.loads((ROOT / "config" / "rule_ownership.json").read_text(encoding="utf-8"))
seen: dict[str, str] = {}
for owner, keys in ownership.items():
    for key in keys:
        if key in seen:
            fail(f"duplicate rule owner {key}: {seen[key]} / {owner}")
        seen[key] = owner

src = {p.name for p in (ROOT / "references").glob("*.md")}
for mirror in [ROOT / "skills/a-share-event-driven-agent/references", ROOT / "ashare_event_agent/resources/references"]:
    if src != {p.name for p in mirror.glob("*.md")}:
        fail("reference set drift")
    for name in src:
        if (ROOT / "references" / name).read_bytes() != (mirror / name).read_bytes():
            fail(f"reference drift: {name}")
if (ROOT / "config/policy.json").read_bytes() != (ROOT / "ashare_event_agent/resources/policy.json").read_bytes():
    fail("policy mirror drift")

cutover = json.loads((ROOT / "config/cutover_status.json").read_text(encoding="utf-8"))
if cutover.get("operational_governance_authority") != "GITHUB_MAIN_CONTINUITY":
    fail("cutover drift: GitHub Continuity must remain the governance authority")
if cutover.get("business_checkpoint_authority_when_runtime_disabled") != "GITHUB_CONTINUITY_TASK_MANIFEST_HANDOFF":
    fail("cutover drift: non-runtime checkpoint authority must remain GitHub Continuity")
if cutover.get("continuity", {}).get("external_mirrors_may_not_override_task_state") is not True:
    fail("cutover drift: external mirrors may not override GitHub task state")
roles = cutover.get("external_system_roles", {})
if roles.get("notion") != "SOURCE_KNOWLEDGE_MIRROR_ONLY" or roles.get("google_drive") != "SOURCE_ARTIFACT_MIRROR_ONLY":
    fail("cutover drift: Notion/Drive must remain source/mirror inputs, not control authority")
if cutover.get("runtime_authority_enabled") is not False:
    fail("runtime promotion must not be enabled without independently evidenced promotion gates")
if not cutover.get("required_gates") or any(v != "PENDING" for v in cutover["required_gates"].values()):
    fail("runtime promotion gate status changed without validated cutover evidence")


def is_tool_decorator(dec: ast.expr) -> bool:
    target = dec.func if isinstance(dec, ast.Call) else dec
    return isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "mcp" and target.attr == "tool"


def tool_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(is_tool_decorator(dec) for dec in node.decorator_list):
            names.add(node.name)
    return names

plugin_text = PLUGIN.read_text(encoding="utf-8")
tree = ast.parse(plugin_text)
tools: list[str] = []
for node in tree.body:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        continue
    decorators = [dec for dec in node.decorator_list if is_tool_decorator(dec)]
    if not decorators:
        continue
    if len(decorators) != 1:
        fail(f"duplicate tool decorators: {node.name}")
    dec = decorators[0]
    tools.append(node.name)
    doc = ast.get_docstring(node) or ""
    if len(doc.strip()) < 50:
        fail(f"tool description too short: {node.name}")
    if not isinstance(dec, ast.Call):
        fail(f"tool decorator missing metadata: {node.name}")
    kws = {k.arg for k in dec.keywords if k.arg}
    if not {"title", "annotations", "structured_output"} <= kws:
        fail(f"missing MCP metadata: {node.name}")
    if node.returns is None:
        fail(f"missing output type: {node.name}")
    rendered = ast.unparse(node.returns)
    if rendered.startswith("dict[") or rendered == "dict" or "Any" in rendered:
        fail(f"weak public output type: {node.name} -> {rendered}")

required = {
    "start_market_day", "get_market_day", "list_recent_market_days", "record_governance_context",
    "submit_freeze_card", "submit_source_completion", "submit_source_audit", "submit_event_ledger",
    "submit_industry_research", "record_stockbase_context", "submit_universe_audit", "submit_market_structure",
    "submit_recall_pool", "submit_execution_plan", "submit_premarket_audit", "start_postclose_review",
    "submit_market_outcomes", "submit_attribution", "submit_recall_grading", "submit_learning_audit",
    "submit_rule_proposal", "submit_replay_eval", "record_review_writeback", "submit_final_audit",
}
if set(tools) != required:
    fail(f"MCP inventory mismatch missing={required-set(tools)} extra={set(tools)-required}")
if tool_names(RUNTIME):
    fail("runtime_service.py must not register MCP tools")
if plugin_text.count("MCPServer(") != 1:
    fail("plugin_server.py must own exactly one MCP server")
if 'ashare-artifact://{task_id}/{kind}' not in plugin_text:
    fail("artifact resource template missing")
if 'Annotated[CallToolResult, MarketDaySummary]' not in plugin_text:
    fail("artifact-returning premarket audit must expose structured MarketDaySummary output")

schema_text = SCHEMAS.read_text(encoding="utf-8")
model_text = MODELS.read_text(encoding="utf-8")
for marker in ['ConfigDict(extra="forbid", str_strip_whitespace=True)', "early_pruning_applied", "board count/height alone cannot prove a market role", "premarket must reuse formal previous-review five-pool snapshot", "core industry research below L5"]:
    if marker not in schema_text:
        fail(f"schema guard missing: {marker}")
for marker in ["PREMARKET_SNAPSHOT_JSON", "PICK_REPORT_MD", "REVIEW_REPORT_MD", "LEARNING_REPORT_JSON", "required_outputs"]:
    if marker not in model_text:
        fail(f"required-output contract missing: {marker}")
if "premarket snapshot mutated after freeze" not in (ROOT / "ashare_event_agent/engine.py").read_text(encoding="utf-8"):
    fail("freeze integrity guard missing")

activation = json.loads((ROOT / "evals/activation_cases.json").read_text(encoding="utf-8"))["cases"]
if len(activation) < 8 or not any(x.get("should_activate") for x in activation) or not any(not x.get("should_activate") for x in activation):
    fail("activation inventory must contain enough positive and negative cases")

print(f"PASS: {len(seen)} unique rule keys; {len(src)} synchronized references; {len(tools)} typed MCP tools; one public MCP surface; GitHub governance cutover + strict freeze/recall/role/required-output guards present")
