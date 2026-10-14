# A-share Event-Driven Agent

A-share domain system for current-day premarket recommendation, post-close review, replay-governed learning and evidence-preserving recovery under Universal Agent OS (UAOS).

## Current authority

- Parent control plane/common method: `D1traverser-debug/universal-agent-os@main`
- Domain entry: `UAOS_SKILL.md`
- Product requirements: `docs/product_requirements.md`
- A-share internal decision graph: `config/MARKET_DAY_ORCHESTRATION.json`
- Binding: `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`
- Hosted runtime promotion/assurance: `config/RUNTIME_AUTHORITY.json`
- Canonical business rules: `references/`, `config/`, `ashare_event_agent/`
- Public optional MCP/runtime surface: `ashare_event_agent/plugin_server.py`

When selected, this domain runs directly as `DOMAIN:ashare`. UAOS is not a mandatory proxy for each business turn and does not own per-trading-day A-share business state. Child `TaskContract.task_id` + `MarketDayState` is the domain market-day/run identity/state model; parent and child IDs are distinct.

There is no domain-level second cross-domain controller, lease/resume-epoch protocol or peer-chat debate system. The retired `continuity/` namespace and old `config/cutover_status.json` remain absent.

## Product flow

Premarket deterministic stages:
`INTAKE -> FREEZE -> SOURCE_COMPLETION -> SOURCE_AUDIT -> EVENT_LEDGER -> INDUSTRY_RESEARCH -> STOCKBASE_RECALL -> UNIVERSE_AUDIT -> MARKET_STRUCTURE -> RECALL_POOL -> EXECUTION_PLAN -> PREMARKET_AUDIT -> FROZEN`

Post-close:
`FROZEN -> REVIEW_OUTCOMES -> ATTRIBUTION -> RECALL_GRADING -> LEARNING_AUDIT -> RULE_PROPOSAL -> REPLAY_EVAL -> FINAL_AUDIT -> COMPLETE`

The outer stage machine is fail-closed. Inside stages, `MARKET_DAY_ORCHESTRATION.json` allows only explicit A-share dependencies: independent source lanes can progress in parallel; event/industry and market-structure research fan into broad recall; event-alpha and market-structure lanes independently compete on **opportunity strength**; bounded counterevidence review critiques them; an opportunity owner produces a preliminary slate; a separate all-U1 risk/execution-feasibility gate may PASS, DEGRADE or BLOCK candidates; one authorized trade-decision owner then produces U3 (max four slots) or NO TRADE.

Risk/buyability is not a third bullish opinion. A hard-veto candidate cannot be voted into U3, and missing preferred microstructure evidence must lower execution assurance rather than being hidden by stronger narrative evidence.

## A-share source hierarchy

- Official/first-party sources own hard corporate/regulatory facts.
- 同花顺 / Level-2 is the preferred market-state/microstructure lane when current-session access is proven; Level-2 evidence carries higher assurance for depth/order-flow/buyability claims than weaker quote summaries.
- 选股通 Dingpan owns the five pool definitions and count/date reconciliation.
- Longbridge or another structured connector is fallback/corroboration, not a redefinition of five-pool or official-fact semantics.
- P01-P09 remain the fixed research/news/industry set.

Configured availability is not execution evidence. Missing hard/preferred capability blocks or explicitly lowers assurance for only the dependent work unit; no silent equivalence substitution.

## Core invariants

- FreezeCard bounds all premarket information; post-close facts never backfill it.
- Research recall is broad before execution ranking narrows candidates.
- Every final U3 ticker descends from frozen U1.
- Every frozen U1 candidate receives explicit risk/buyability assessment before final U3 adjudication.
- `BLOCK` risk candidates cannot enter U3; FULL execution assurance requires preferred microstructure evidence.
- Candidate selection is comparative (`why_this` + `why_not_peers`); NO TRADE is first-class.
- Market role is not proven by board count alone.
- Five-pool and outcome counts reconcile before review acceptance.
- Post-close attribution is derived against frozen membership, not rewritten hindsight.
- Post-close grades research recall, final-selection activation/outcome quality, and execution feasibility separately.
- One market day creates evidence/hypotheses, not an automatically promoted permanent rule.
- Durable replay cannot claim improvement from recall alone while hiding worse downside or executability.
- Every detected problem requires research plus macro/assumption reflection before durable repair.
- Audit-tool invocation is not independent-review proof; assurance follows actual execution evidence.

## Runtime authority

`config/RUNTIME_AUTHORITY.json` separates **domain business ownership** from **hosted runtime assurance**. `runtime_authority_enabled=false` does not return business ownership to UAOS; it only means hosted-runtime-only certification/durable runtime resume is not yet proven. Current chat/tool execution may still perform governed A-share research, decision, review and artifacts under the repository contracts.

Notion/Google Drive are source/knowledge/artifact inputs only. They are never controller/task-state fallbacks.

## Validation

Unit/trajectory tests, contract evals, static ownership/architecture fitness checks, wheel-install smoke and current-source/runtime capability evidence protect schemas, transitions, freeze integrity, source lineage, market-day identity, U0/U1/U3 lineage, opportunity-risk separation, decision graph semantics, final-selection/execution grading, review/replay learning and packaging.
