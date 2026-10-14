from __future__ import annotations

import ast
import json
from pathlib import Path

from ashare_event_agent.orchestration import validate_orchestration
from ashare_event_agent.source_contracts import DINGPAN_POOL_SEMANTICS, MARKET_DATA_LANES

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "ashare_event_agent" / "plugin_server.py"
RUNTIME = ROOT / "ashare_event_agent" / "runtime_service.py"
RUNNER = ROOT / "ashare_event_agent" / "runner.py"
SCHEMAS = ROOT / "ashare_event_agent" / "schemas.py"
MODELS = ROOT / "ashare_event_agent" / "models.py"
CONTROLLER = ROOT / "ashare_event_agent" / "controller.py"
INTEGRITY = ROOT / "ashare_event_agent" / "integrity.py"
PYPROJECT = ROOT / "pyproject.toml"


def fail(msg: str) -> None:
    raise SystemExit(msg)


# Single-owner rule surface.
ownership = json.loads((ROOT / "config" / "rule_ownership.json").read_text(encoding="utf-8"))
seen: dict[str, str] = {}
for owner, keys in ownership.items():
    for key in keys:
        if key in seen:
            fail(f"duplicate rule owner {key}: {seen[key]} / {owner}")
        seen[key] = owner

# Canonical references/config and distribution mirrors must not drift.
src = {p.name for p in (ROOT / "references").glob("*.md")}
reference_mirrors = [
    ROOT / "skills/a-share-event-driven-agent/references",
    ROOT / "ashare_event_agent/resources/references",
]
for mirror in reference_mirrors:
    if src != {p.name for p in mirror.glob("*.md")}:
        fail(f"reference set drift: {mirror}")
    for name in src:
        if (ROOT / "references" / name).read_bytes() != (mirror / name).read_bytes():
            fail(f"reference drift: {mirror}/{name}")
if (ROOT / "config/policy.json").read_bytes() != (ROOT / "ashare_event_agent/resources/policy.json").read_bytes():
    fail("policy mirror drift")
if (ROOT / "config/MARKET_DAY_ORCHESTRATION.json").read_bytes() != (ROOT / "ashare_event_agent/resources/market_day_orchestration.json").read_bytes():
    fail("market-day orchestration mirror drift")

# Current UAOS binding: parent control plane, child business identity/state.
manifest = json.loads((ROOT / ".uaos/MANIFEST.json").read_text(encoding="utf-8"))
adapter = json.loads((ROOT / ".uaos/ADAPTER.json").read_text(encoding="utf-8"))
capability_profile = json.loads((ROOT / ".uaos/CAPABILITIES.json").read_text(encoding="utf-8"))
authority = json.loads((ROOT / "config/RUNTIME_AUTHORITY.json").read_text(encoding="utf-8"))
product = (ROOT / "docs/product_requirements.md").read_text(encoding="utf-8")
graph = json.loads((ROOT / "config/MARKET_DAY_ORCHESTRATION.json").read_text(encoding="utf-8"))
validate_orchestration(graph)

if manifest.get("status") != "DIRECT_DOMAIN_WORK_PLANE_ACTIVE":
    fail("manifest must declare direct A-share work plane")
if manifest.get("binding", {}).get("common_capabilities_min") != "1.6.0":
    fail("A-share must consume UAOS common capabilities >=1.6.0")
if manifest.get("domain_authority", {}).get("market_day_identity") != "ashare_event_agent/models.py:TaskContract.task_id":
    fail("manifest market-day identity owner drift")
if manifest.get("domain_authority", {}).get("market_day_orchestration_ref") != "config/MARKET_DAY_ORCHESTRATION.json":
    fail("manifest orchestration authority drift")
if adapter.get("domain_market_day_identity_authority") != "ashare_event_agent/models.py:TaskContract.task_id":
    fail("adapter must keep market-day identity in the A-share domain")
if adapter.get("parent_child_id_equality_required") is not False:
    fail("parent/child identity equality must remain forbidden")
if "OPAQUE_CHILD" not in adapter.get("parent_reference_semantics", ""):
    fail("parent reference must remain opaque")
if capability_profile.get("profile_version") != 4:
    fail("unexpected A-share capability profile version")
if capability_profile.get("uaos_common_capabilities_min") != "1.6.0":
    fail("A-share common capability minimum drift")
if len(capability_profile.get("problem_response_floor") or []) < 4:
    fail("problem response cognition floor missing")
if "FAMILIARITY_IS_NOT_A_WAIVER" not in capability_profile.get("problem_response_rule", ""):
    fail("familiarity waiver incorrectly reintroduced")
if authority.get("domain_business_identity_authority") != "ashare_event_agent/models.py:TaskContract.task_id":
    fail("runtime authority must separate child business identity from host runtime promotion")
if authority.get("parent_may_mirror_market_day_business_state") is not False:
    fail("UAOS must not mirror A-share market-day business state")
if not (ROOT / "docs/product_requirements.md").exists() or "Acceptance map" not in product:
    fail("current A-share product requirements/acceptance map missing")
if graph.get("business_owner") != "DOMAIN:ashare":
    fail("A-share market-day graph owner drift")
if "NO_UNBOUNDED_PEER_CHAT" not in graph.get("decision_model", ""):
    fail("peer-chat debate must remain forbidden")

# Retired controller/continuity surfaces must remain physically absent.
for retired in [
    ROOT / "continuity",
    ROOT / "config/cutover_status.json",
    ROOT / "ashare_event_agent/continuity_plugin.py",
    ROOT / "ashare_event_agent/adapters/mock.py",
]:
    if retired.exists():
        fail(f"retired surface reappeared: {retired.relative_to(ROOT)}")

# Specialized market-data business roles.
if "TONGHUASHUN_LEVEL2" not in MARKET_DATA_LANES:
    fail("preferred Tonghuashun/Level-2 lane missing")
if "XUANGUTONG_DINGPAN" not in MARKET_DATA_LANES:
    fail("Xuangutong Dingpan lane missing")
if tuple(MARKET_DATA_LANES["XUANGUTONG_DINGPAN"].owns) != DINGPAN_POOL_SEMANTICS:
    fail("Dingpan five-pool semantics drift")
if "Level-2" not in (ROOT / "references/sources.md").read_text(encoding="utf-8"):
    fail("source authority must document Level-2 assurance role")

# Package/public runtime shape.
pyproject_text = PYPROJECT.read_text(encoding="utf-8")
if 'version = "0.2.0"' not in pyproject_text:
    fail("package release must be 0.2.0")
if 'ashare-event-mcp = "ashare_event_agent.plugin_server:main"' not in pyproject_text:
    fail("package MCP entrypoint must point directly to plugin_server:main")
if "continuity_plugin" in pyproject_text:
    fail("retired continuity_plugin remains referenced by package metadata")


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
    "start_market_day", "get_market_day", "list_recent_market_days", "list_resumable_tasks", "record_governance_context",
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
if tool_names(RUNNER):
    fail("runner.py reference harness must not register MCP tools")
if plugin_text.count("MCPServer(") != 1:
    fail("plugin_server.py must own exactly one MCP server")
if 'ashare-artifact://{task_id}/{kind}' not in plugin_text:
    fail("artifact resource template missing")
if 'Annotated[CallToolResult, MarketDaySummary]' not in plugin_text:
    fail("artifact-returning premarket audit must expose structured MarketDaySummary output")
if "task_metadata" not in plugin_text or "list_resumable_states" not in plugin_text or "list_resumable_tasks" not in tools:
    fail("canonical MCP surface must expose child-run resume metadata and resumable discovery directly")
if "audit-tool call" not in plugin_text or "does not by itself prove reviewer independence" not in plugin_text:
    fail("MCP instructions must not overclaim independent audit assurance")

package_init = (ROOT / "ashare_event_agent/__init__.py").read_text(encoding="utf-8")
if "AgentRuntime" in package_init:
    fail("reference AgentRuntime must not be promoted through the package public API")

# Active surfaces must not revive parent-owned per-day identity or retired continuity authority.
active_semantic_surfaces = [
    ROOT / "README.md",
    ROOT / "UAOS_SKILL.md",
    ROOT / "docs/architecture.md",
    ROOT / "docs/product_requirements.md",
    ROOT / "references/recovery.md",
    ROOT / ".uaos/ADAPTER.json",
    ROOT / ".uaos/MANIFEST.json",
    ROOT / ".uaos/CAPABILITIES.json",
]
for path in active_semantic_surfaces:
    text = path.read_text(encoding="utf-8")
    for obsolete in ["UAOS owns task identity", "UAOS resolves current task identity", "GITHUB_MAIN_CONTINUITY", "GITHUB_CONTINUITY_TASK_MANIFEST_HANDOFF"]:
        if obsolete in text:
            fail(f"obsolete parent-owned A-share identity/control semantics reappeared: {obsolete} in {path.relative_to(ROOT)}")

# Existing A-share evidence-lineage guards remain mandatory.
schema_text = SCHEMAS.read_text(encoding="utf-8")
model_text = MODELS.read_text(encoding="utf-8")
controller_text = CONTROLLER.read_text(encoding="utf-8")
integrity_text = INTEGRITY.read_text(encoding="utf-8")
for marker in [
    'ConfigDict(extra="forbid", str_strip_whitespace=True)',
    "early_pruning_applied",
    "U1 candidates must be a subset of U0",
    "board count/height alone cannot prove a market role",
    "premarket must reuse formal previous-review five-pool snapshot",
    "core industry research below L5",
    "u0_recall must equal u0_hits / knowable_limit_up_total",
    "PROPOSE requires applicable regimes, counterexamples and replay case refs",
    "PASS requires mechanical replay evidence refs",
    "cassette hashes for every case",
    "content_max_available_at",
    "FULL source requires explicit LINK-ALL and image expected/read counts",
    "premarket cutoff exceeds legal freeze boundary",
    "why_not_peers: list[str] = Field(min_length=1)",
    "Universe exclusion_reasons must exactly cover excluded tickers",
    "N_A rule proposal requires no_change_reason",
]:
    if marker not in schema_text:
        fail(f"schema guard missing: {marker}")
for marker in ["PREMARKET_SNAPSHOT_JSON", "PICK_REPORT_MD", "REVIEW_REPORT_MD", "LEARNING_REPORT_JSON", "required_outputs", 'CURRENT_RUNTIME_VERSION = "0.2.0"']:
    if marker not in model_text:
        fail(f"required-output/runtime contract missing: {marker}")
for marker in [
    "universe_integrity_errors",
    "recall_integrity_errors",
    "execution_integrity_errors",
    "attribution_integrity_errors",
    "recall_grade_integrity_errors",
    "replay_coherence_errors",
]:
    if marker not in controller_text or marker not in integrity_text:
        fail(f"cross-stage integrity guard missing or unwired: {marker}")
for marker in [
    "eligible mapped tickers silently omitted from Universe",
    "U0 omitted Universe tickers",
    "U3 execution candidates must descend from U1",
    "attribution in_u0 disagrees with frozen U0",
    "knowable_limit_up_total must equal attributed knowable count",
    "N_A rule proposal requires N_A replay result",
]:
    if marker not in integrity_text:
        fail(f"evidence-lineage guard missing: {marker}")
if "premarket snapshot mutated after freeze" not in (ROOT / "ashare_event_agent/engine.py").read_text(encoding="utf-8"):
    fail("freeze integrity guard missing")

activation = json.loads((ROOT / "evals/activation_cases.json").read_text(encoding="utf-8"))["cases"]
if len(activation) < 8 or not any(x.get("should_activate") for x in activation) or not any(not x.get("should_activate") for x in activation):
    fail("activation inventory must contain enough positive and negative cases")

print(
    f"PASS: {len(seen)} unique A-share rule keys; {len(src)} synchronized reference files; "
    f"{len(tools)} typed tools on one MCP surface; child-owned market-day identity; UAOS 1.6 cognition/orchestration inheritance; "
    "Tonghuashun/Level-2 + Dingpan source roles; explicit market-day decision graph; retired parent/continuity control surfaces absent; "
    "freeze + Universe/U0/U1/U3 + frozen-review + replay guards present"
)
