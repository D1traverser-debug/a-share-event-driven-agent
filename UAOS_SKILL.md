---
name: a-share-event-driven-agent-uaos
scope: A-share premarket recommendation, post-close review and replay-governed learning
---

# A-share Event-Driven Agent — Current UAOS Entry

Parent control plane: `D1traverser-debug/universal-agent-os@main`.
Domain repository: `D1traverser-debug/a-share-event-driven-agent@main`.
Authority Context: `DOMAIN:ashare`.

When this domain is selected in a chat, the current work plane is **A-share**, not a live UAOS business proxy. UAOS supplies cross-domain routing, common cognition/evolution/product-governance method and optional parent guidance. This repository owns A-share product requirements, market-day/run identity, business state, trading-day workflow, source/data contracts, recommendation/review rules, internal work graph, evidence and domain learning.

UAOS router identity and A-share market-day `TaskContract.task_id` are distinct namespaces. No equality requirement exists. UAOS may retain only an opaque child reference for continuity.

## Start

Read:
1. `.uaos/ADAPTER.json`;
2. `.uaos/MANIFEST.json`;
3. `.uaos/CAPABILITIES.json`;
4. `docs/product_requirements.md` when product/architecture scope matters;
5. `config/RUNTIME_AUTHORITY.json` before making hosted-runtime assurance claims;
6. only the reference/runtime files required by the current market-day stage.

For a **new live recommendation**, the A-share domain resolves the current China trading day, creates its own child `TaskContract`/`MarketDayState`, defines the legal freeze boundary and executes the business workflow. Do not create a same-ID UAOS market-day task first.

For an **explicit historical run**, the exact child task/reference wins. Never reinterpret an old premarket run as the current trading day.

## Specialized source lanes

- Official/first-party sources own hard corporate/regulatory facts.
- 同花顺 / Level-2 is the preferred market-state and microstructure lane when current-session capability is proven; Level-2 evidence is higher-value than weaker quote summaries for depth/order-flow/buyability claims.
- 选股通 Dingpan owns the five business pool definitions (`limit_up`, `limit_down`, `limit_up_broken`, `super_stock`, `yesterday_limit_up`) with date/count reconciliation.
- Longbridge or another structured market connector is fallback/corroboration and does not redefine the five pools or override official hard facts.
- P01-P09 remain the fixed research-source set.

A configured app is not execution evidence. Missing preferred data blocks or explicitly degrades the affected claim; never silently substitute stale/weaker inputs and claim the original assurance.

## Market-day decision flow

The canonical stage machine remains fail-closed. `config/MARKET_DAY_ORCHESTRATION.json` defines A-share-specific internal work: source lanes may run in parallel; event/industry and market-structure work fan in at recall; two independent U1-bounded **opportunity** views (event/industry alpha and market structure) compete; a bounded counterevidence pass critiques them; an authorized opportunity owner forms a preliminary slate; then a separate risk/execution-feasibility gate assesses every U1 candidate and may PASS, DEGRADE or BLOCK it; one authorized trade-decision owner combines opportunity evidence with that risk layer to adjudicate U3 or NO TRADE.

Risk/buyability is a constraint and possible veto, not another bullish vote. `BLOCK` cannot be outvoted into U3. Missing preferred 同花顺/Level-2 evidence cannot support FULL execution assurance.

This is structured artifact handoff, not unbounded specialist chat. An advisory/reviewer output is not a recommendation until the authorized owner adopts it.

## Time and evidence

New premarket work must resolve the current trading day. Freeze timestamped evidence before final recommendation; post-close facts never backfill the frozen decision. Research recall remains broad before execution ranking narrows it. A final U3 candidate must descend from frozen U1.

## Post-close and evolution

Review starts from the immutable frozen snapshot. Reconcile outcomes/five pools and market/microstructure evidence, then grade three separate things:
1. research recall (U0/U1);
2. final-selection activation/outcome quality for frozen U3;
3. execution feasibility for activated recommendations.

A recommendation whose trigger never occurred is not counted as an executed win/loss. Activated recommendations require execution-feasibility evidence. Broken-board/limit-down outcomes remain visible in downside metrics rather than being hidden by recall success.

Every detected problem requires concrete diagnosis, macro workflow/goal check, governing-assumption challenge and external research/verification. Familiarity is not a waiver. A daily result creates evidence/hypotheses only; permanent rules require replay across regimes plus regression/CI evidence under `references/learning.md` and `references/maintenance.md`. Replay PASS must report recall, activated-positive, activated-downside and execution-feasibility metrics; recall improvement alone is not enough.

## Completion

Completion requires the exact A-share frozen/review evidence and outputs for the requested stage. Do not create a second controller, parent-owned per-day task registry, lease/resume epoch protocol, or peer-chat debate system.
