# A-share Event-Driven Agent v0.1

A deterministic A-share short-term research runtime for **pre-market recommendation, post-close review, learning governance, replay regression, and interruption-safe recovery**.

## Identity
- Repository: `D1traverser-debug/a-share-event-driven-agent`
- Canonical branch: `main`
- Python package: `ashare_event_agent`
- MCP entry point: `ashare-event-mcp`
- Skill: `a-share-event-driven-agent`

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

Any illegal transition, unresolved Must-Pass gate, future-information contamination, forbidden StockBase mutation, or missing executor routes to `BLOCKED`. There is no silent free-form fallback.

## Core invariants
- FreezeCard is created before dynamic premarket research can be finalized.
- Premarket frozen payload is immutable after `FROZEN`; post-close review is append-only.
- Previous trading day's five pools are reused from the formal review snapshot; premarket must not re-fetch them when a formal snapshot exists. A later gap-fill must be provenance-labeled and must never fabricate historical premarket truth.
- Recommendation is StockBase **READ_ONLY**. Review is the only workflow allowed to record a StockBase writeback receipt.
- P01-P09 source coverage is contract-owned and count-reconciled, including image-only information and LINK-ALL expansion.
- Industry research depth for recommendation must be at least as deep as review: event → L0-L5+ → product/BOM/material/equipment/process/customer/order/capacity/price/profit transmission.
- Board count is a fact, not proof of leadership. Role hypotheses require evidence and competitors.
- `Leader-First` may rank U2/U3; it may not prune U0/U1 recall.
- Post-close outcomes never rewrite premarket reasoning.
- One-day observations cannot directly promote durable rules.

## Persistent authority
- GitHub `main`: executable code/rule truth **and Continuity governance authority**.
- While `runtime_authority_enabled=false`: `continuity/tasks/<task>/TASK_MANIFEST.json` + `HANDOFF.md` are the authoritative governance checkpoint for stage intent, next action and evidence refs. They do not impersonate an executed Runtime transition.
- After promotion gates pass and `runtime_authority_enabled=true`: Hosted MCP store additionally becomes executable per-market-day checkpoint truth.
- Notion/Google Drive: source, knowledge, artifact and migration-mirror inputs only; they are not competing task/control checkpoints.
- StockBase: shared company knowledge; recommendation reads, review writes through explicit receipt gates.

## Validation layers
Local validation covers strict schemas, legal transitions, freeze integrity, source/five-pool guards, role evidence, recall pruning, recovery, required outputs, final-audit revision routing, contract scenarios, static rule ownership and wheel packaging.

GitHub-hosted validation additionally runs MCP HTTP smoke and clean dependency install. Real market behavior still requires historical frozen-cassette replay and live premarket→post-close E2E before Runtime promotion.

See `docs/provenance_and_cutover.md` for the migration map and cutover gates.

## Status
v0.1 Runtime is still candidate, not production-proven. The **control/governance migration to GitHub is active now**; Runtime promotion remains a separate evidence-gated step. Until promotion, unavailable Runtime capability blocks only the affected Runtime-dependent gate and never routes business control back to Notion/Drive.
