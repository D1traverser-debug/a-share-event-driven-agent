# Architecture

## Design thesis

Use a **deterministic market-day outer runtime + model-driven research/judgment + explicit evidence gates**.

The model is useful for public research, deep industry reasoning, event synthesis, market-role hypotheses, counterfactual comparison and semantic red-team review. It is not trusted to decide whether a stage may be skipped, whether future data is legal, whether source counts reconcile, whether the frozen premarket snapshot changed, whether an unrecalled stock may enter U3, or whether a one-day lesson deserves durable promotion.

This repository is an A-share recommendation/review product, not a generic orchestration framework. UAOS contributes common cognition/evolution/product-governance method; A-share owns the concrete market-day graph and all business state.

## Authority layers

1. **A-share GitHub `main`** — executable code, product requirements and business-rule truth.
2. **Child market-day identity/state** — `TaskContract.task_id` + `MarketDayState`; this is distinct from the UAOS parent router identity.
3. **Hosted MCP state store** — durable executable checkpoint authority only after the gates in `config/RUNTIME_AUTHORITY.json` pass and `runtime_authority_enabled=true`.
4. **Frozen premarket artifact/cassette** — immutable decision evidence for later review/replay.
5. **StockBase/Event knowledge** — shared cognition/knowledge input; premarket read, review write receipt only.
6. **Notion/Google Drive** — source/knowledge/artifact inputs only; never task/control authority.

When hosted runtime is not promoted, A-share business ownership does not revert to UAOS. Only hosted-runtime-specific claims/resume are blocked.

## Market-day internal orchestration

`config/MARKET_DAY_ORCHESTRATION.json` is the business work graph. It specializes UAOS common orchestration semantics for A-share:

- trading day and freeze boundary are serial roots;
- P01-P09, official facts, 同花顺/Level-2 market data, prior five-pool snapshot and StockBase context are independent source lanes when their dependencies permit;
- source reconciliation gates evidence admission;
- event/industry and market-structure work progress on their declared dependencies rather than a single global wave;
- U0/U1 recall is a hard precursor to all final-candidate views;
- event-alpha, market-structure and buyability/execution lanes create independent U1-bounded candidate slates;
- structured counterevidence is advisory;
- one authorized trade-decision owner adjudicates U3 or NO TRADE;
- post-close outcomes, Level-2 close review and execution-feasibility review may proceed independently before reconciliation/attribution.

No persistent specialist is allowed to transfer authority through free-form peer debate. Decisions are explicit artifacts with an owner/adjudicator.

## Source architecture

Fact ownership is separated by business semantics:

- official first-party sources own hard facts;
- 同花顺/Level-2 is the preferred microstructure/buyability lane when session-proven;
- 选股通 Dingpan owns the five pool definitions and date/count reconciliation;
- structured market connectors are fallback/corroboration;
- P01-P09 supply broad event/news/industry discovery.

The system preserves both sides of unresolved source conflicts instead of selecting the convenient value.

## Self-evolution

A daily review produces error records and candidate hypotheses. Every detected problem first enters mandatory research/reflection: concrete diagnosis, macro workflow/product check, governing-assumption challenge and external research/verification.

Durable change is separate:
`problem evidence -> candidate hypothesis -> rule proposal -> frozen historical replay -> regression audit -> GitHub change/PR -> CI -> promotion`.

The current day's winning/losing outcome is never enough to directly change permanent behavior.

## Hosted runtime promotion

Hosted Runtime promotion is evidence-gated and distinct from domain ownership. Remaining gates cover multi-regime replay, real P01-P09/live-market adapters, preferred Level-2 lane evidence, durable checkpoint/artifact storage, fresh-session runtime recovery, real premarket-to-postclose learning E2E and independent audit attestation.

Until those pass, runtime-specific certification is bounded; the domain may still perform governed A-share research/recommendation/review work with honest capability labels.
