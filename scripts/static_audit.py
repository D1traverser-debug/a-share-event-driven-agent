from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "ashare_event_agent" / "plugin_server.py"
RUNTIME = ROOT / "ashare_event_agent" / "runtime_service.py"
RUNNER = ROOT / "ashare_event_agent" / "runner.py"
SCHEMAS = ROOT / "ashare_event_agent" / "schemas.py"
MODELS = ROOT / "ashare_event_agent" / "models.py"
CONTROLLER = ROOT / "ashare_event_agent" / "controller.py"
INTEGRITY = ROOT / "ashare_event_agent" / "integrity.py"
PYPROJECT = ROOT / "pyproject.toml"
AGENT_MANIFEST = ROOT / "continuity" / "AGENT_MANIFEST.json"
CAPABILITIES = ROOT / "continuity" / "EXECUTION_CAPABILITIES.json"


def fail(msg: str) -> None:
    raise SystemExit(msg)


ownership = json.loads((ROOT / "config" / "rule_ownership.json").read_text(encoding="utf-8"))
seen: dict[str, str] = {}
for owner, keys in ownership.items():
    for key in keys:
        if key in seen:
            fail(f"duplicate rule owner {key}: {seen[key]} / {owner}")
        seen[key] = owner

# Root references/config are canonical. Skill and wheel copies are distribution
# mirrors only; byte drift would create a second rule surface.
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

# Fail closed if test-only mocks or the retired continuity wrapper leak back into
# the production package.
if (ROOT / "ashare_event_agent/adapters/mock.py").exists():
    fail("test-only mock adapter leaked into production package")
if (ROOT / "ashare_event_agent/continuity_plugin.py").exists():
    fail("retired second MCP/continuity wrapper reappeared")

pyproject_text = PYPROJECT.read_text(encoding="utf-8")
if 'ashare-event-mcp = "ashare_event_agent.plugin_server:main"' not in pyproject_text:
    fail("package MCP entrypoint must point directly to plugin_server:main")
if "continuity_plugin" in pyproject_text:
    fail("retired continuity_plugin remains referenced by package metadata")

agent_manifest = json.loads(AGENT_MANIFEST.read_text(encoding="utf-8"))
runtime_manifest = agent_manifest.get("runtime") or {}
if runtime_manifest.get("public_entrypoint") != "ashare_event_agent/plugin_server.py":
    fail("agent manifest must declare plugin_server.py as the single public runtime entrypoint")
harness_manifest = (agent_manifest.get("harness") or {}).get("reference_executor_harness") or {}
if harness_manifest.get("ref") != "ashare_event_agent/runner.py" or harness_manifest.get("production_entrypoint") is not False:
    fail("runner.py must remain explicitly classified as non-production reference/test harness")
refs_manifest = agent_manifest.get("references") or {}
if refs_manifest.get("canonical_root") != "references":
    fail("reference authority drift: root references must remain canonical")
if set(refs_manifest.get("generated_mirrors") or []) != {
    "skills/a-share-event-driven-agent/references",
    "ashare_event_agent/resources/references",
}:
    fail("reference mirror manifest must name both Skill and wheel distribution mirrors")

cutover = json.loads((ROOT / "config" / "cutover_status.json").read_text(encoding="utf-8"))
if cutover.get("operational_governance_authority") != "GITHUB_MAIN_CONTINUITY":
    fail("cutover drift: GitHub Continuity must remain the governance authority")
if cutover.get("business_checkpoint_authority_when_runtime_disabled") != "GITHUB_CONTINUITY_TASK_MANIFEST_HANDOFF":
    fail("cutover drift: non-runtime checkpoint authority must remain GitHub Continuity")
if cutover.get("continuity", {}).get("external_mirrors_may_not_override_task_state") is not True:
    fail("cutover drift: external mirrors may not override GitHub task state")
roles = cutover.get("external_system_roles", {})
if roles.get("notion") != "SOURCE_KNOWLEDGE_MIRROR_ONLY" or roles.get("google_drive") != "SOURCE_ARTIFACT_MIRROR_ONLY":
    fail("cutover drift: Notion/Drive must remain source/mirror inputs, not control authority")
gates = cutover.get("required_gates") or {}
if not gates:
    fail("runtime promotion gates missing")
if "independent_audit_attestation" not in gates:
    fail("runtime promotion gate missing: independent_audit_attestation")
if cutover.get("runtime_authority_enabled") and any(v != "PASS" for v in gates.values()):
    fail("runtime authority enabled before all required promotion gates passed")

capability_profile = json.loads(CAPABILITIES.read_text(encoding="utf-8"))
capabilities = {row.get("capability_id"): row for row in capability_profile.get("capabilities", [])}
state_machine = capabilities.get("market_day_state_machine") or {}
if state_machine.get("executor_ref") != "ashare_event_agent/plugin_server.py":
    fail("market-day state-machine capability must bind to the canonical owner MCP surface")
if "runner.AgentRuntime" in state_machine.get("invocation_path", "") or state_machine.get("executor_ref") == "ashare_event_agent/runner.py":
    fail("reference runner must not be advertised as the production state-machine executor")
live_source = capabilities.get("live_source_acquisition") or {}
if live_source.get("executor_ref") is not None:
    fail("live source acquisition must not advertise a native executor before one exists")
if live_source.get("contract_ref") != "ashare_event_agent/source_contracts.py":
    fail("live source capability must distinguish source contract metadata from executor implementation")
if live_source.get("executor_type") != "EXTERNAL_SESSION_CONNECTORS":
    fail("live source capability must remain session-external until native adapters exist")
auditor = capabilities.get("strict_isolated_auditor")
if not auditor:
    fail("strict isolated auditor capability missing")
if auditor.get("assurance_ceiling") != "DECLARED_ONLY" or auditor.get("executor_type") != "UNAVAILABLE":
    fail("independent auditor must not be advertised as executable without attested executor evidence")
if auditor.get("safe_degraded_modes"):
    fail("independent audit must not silently degrade to same-executor chat review")
if "distinct_reviewer_execution_context" not in auditor.get("required_tools", []):
    fail("independent audit capability missing distinct reviewer execution requirement")
for stage in ["SOURCE_AUDIT", "UNIVERSE_AUDIT", "PREMARKET_AUDIT", "FINAL_AUDIT"]:
    if stage not in auditor.get("scope", ""):
        fail(f"independent audit capability scope missing {stage}")


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
if "continuity_metadata" not in plugin_text or "list_resumable_states" not in plugin_text:
    fail("canonical MCP surface must own continuity metadata and resumable discovery directly")
if "audit-tool call" not in plugin_text or "does not by itself prove reviewer independence" not in plugin_text:
    fail("MCP instructions must not overclaim independent audit assurance")

package_init = (ROOT / "ashare_event_agent/__init__.py").read_text(encoding="utf-8")
if "AgentRuntime" in package_init:
    fail("reference AgentRuntime must not be promoted through the package public API")

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
for marker in ["PREMARKET_SNAPSHOT_JSON", "PICK_REPORT_MD", "REVIEW_REPORT_MD", "LEARNING_REPORT_JSON", "required_outputs"]:
    if marker not in model_text:
        fail(f"required-output contract missing: {marker}")
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
    f"PASS: {len(seen)} unique rule keys; {len(src)} synchronized canonical-reference files across two declared distribution mirrors; "
    f"{len(tools)} typed tools on one public MCP surface; test harnesses/mocks demoted; GitHub governance + runtime-promotion/independent-audit guards + "
    "point-in-time source proof + Universe/U0/U1/U3 lineage + frozen review grading + replay/required-output guards present"
)
