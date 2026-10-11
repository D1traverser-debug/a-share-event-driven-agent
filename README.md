# A-share Event-Driven Agent v0.1

A deterministic A-share short-term research runtime for **pre-market recommendation, post-close review, learning governance, replay regression, and interruption-safe recovery**.

## Identity
- Repository: `D1traverser-debug/a-share-event-driven-agent`
- Canonical branch: `main`
- Python package: `ashare_event_agent`
- MCP command: `ashare-event-mcp`
- Canonical MCP/public runtime surface: `ashare_event_agent/plugin_server.py`
- Skill: `a-share-event-driven-agent`

`runtime_service.py`, `controller.py`, `engine.py`, and `store.py` are internal runtime components. `runner.AgentRuntime` is an offline/test injected-executor harness; it is not the hosted business entrypoint and does not prove live source executors exist. `source_contracts.py` defines P01-P09 acquisition contracts and preferred methods; live acquisition still requires a current-session external source capability and an owner receipt.

## Objective
The system optimizes two separate targets:
1. **Research recall:** maximize recall of limit-up candidates that were knowable before the freeze line.
2. **Execution precision:** only after recall, rank leader/card-position/pioneer/capacity roles and produce a narrow executable plan.

Research is deliberately wide; execution is deliberately narrow.

## Runtime
Premarket:
`INTAKE → FREEZE → SOURCE_COMPLETION → SOURCE_AUDIT → EVENT_LEDGER → INDUSTRY_RESEARCH → STOCKBASE_RECALL → UNIVERSE_AUDIT → MARKET_STRUCTURE → RECALL_POOL → EXECUTION_PLAN → PREMARKET_AUDIT → FROZEN`

Post-close, continuing the same immutable market-day task:
`FROZEN → REVIEW_OUTCOMES → ATTRIBUTION → RECALL_GRADING → LEARNING_AUDIT → RULE_PROPOSAL → REPLAY_EVAL → FINAL_AUDIT → COMPLETE`

Any illegal transition, unresolved Must-Pass gate, future-information contamination, forbidden StockBase mutation, or missing required capability routes to `BLOCKED` or revision. There is no silent free-form fallback.

An audit tool records an audit decision. It does not by itself establish reviewer independence; Source/Universe/Premarket/Final independent certification requires the separately attested isolated-review capability defined in `continuity/EXECUTION_CAPABILITIES.json`.

## Core invariants
- FreezeCard is created before dynamic premarket research can be finalized.
- Premarket frozen payload is immutable after `FROZEN`; post-close review is append-only.
- Previous trading day's five pools are reused from the formal review snapshot; premarket must not re-fetch them when a formal snapshot exists. A later gap-fill must be provenance-labeled and must never fabricate historical premarket truth.
- Recommendation is StockBase **READ_ONLY**. Review is the only workflow allowed to record a StockBase writeback receipt.
- P01-P09 source coverage is contract-owned and point-in-time/count reconciled, including image-only information and LINK-ALL expansion.
- Industry research depth for recommendation must be at least as deep as review: event → L0-L5+ → product/BOM/material/equipment/process/customer/order/capacity/price/profit transmission.
- IndustryResearch preserves many-to-many event/node/company mappings; active Universe is a stock-level main-board view with explicit exclusions.
- U0 equals active Universe; U1 is a subset of U0; U3 execution candidates descend from U1 and require comparative `why_not_peers` evidence.
- Board count is a fact, not proof of leadership. Role hypotheses require evidence and competitors.
- `Leader-First` may rank U2/U3; it may not prune U0/U1 recall.
- Post-close outcomes never rewrite premarket reasoning; attribution and RecallGrade are reconciled against the frozen cassette.
- One-day observations cannot directly promote durable rules.

## Rule and distribution surfaces
Root `references/` and `config/` are canonical rule/config authority. Copies under `skills/a-share-event-driven-agent/references/` and `ashare_event_agent/resources/references/`, plus packaged `resources/policy.json`, are generated distribution mirrors for Skill and wheel packaging. CI enforces byte equality so these mirrors cannot become independent rule owners.

## Persistent authority
- GitHub `main`: executable code/rule truth **and Continuity governance authority**.
- While `runtime_authority_enabled=false`: `continuity/tasks/<task>/TASK_MANIFEST.json` + `HANDOFF.md` are the authoritative governance checkpoint for stage intent, next action and evidence refs. They do not impersonate an executed Runtime transition.
- After promotion gates pass and `runtime_authority_enabled=true`: Hosted MCP store additionally becomes executable per-market-day checkpoint truth.
- Notion/Google Drive and other external stores: source, knowledge, artifact and migration-mirror inputs only; they are not competing task/control checkpoints.
- StockBase: shared company knowledge; recommendation reads, review writes through explicit receipt gates.

## Validation layers
Local validation covers strict schemas, legal transitions, freeze integrity, source/five-pool guards, cross-stage evidence lineage, role evidence, recall pruning, recovery, required outputs, final-audit revision routing, contract scenarios, single-MCP-surface/harness hygiene, static rule ownership and wheel packaging.

GitHub-hosted validation additionally runs MCP HTTP smoke and clean dependency/install packaging. Real market behavior still requires genuine frozen-cassette replay, independently attested audits, live P01-P09 validation, durable hosted recovery/storage, and a live premarket→post-close E2E before Runtime promotion.

See `docs/provenance_and_cutover.md` for the migration map and cutover gates.

## Status
v0.1 Runtime is still candidate, not production-proven. The **control/governance migration to GitHub is active now**; Runtime promotion remains a separate evidence-gated step. Until promotion, unavailable Runtime capability blocks only the affected Runtime-dependent gate and never routes business control back to Notion/Drive.
