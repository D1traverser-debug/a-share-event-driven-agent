# A-share Recommendation System — Product Requirements

Version: 0.2.0
Authority: `A_SHARE_EVENT_DRIVEN_AGENT`
Parent method dependency: `UAOS COMMON_CAPABILITIES >= 1.6.0`

## Product mission

Provide an auditable A-share main-board, event-driven decision system for 1–2 trading-day horizons. The product must produce a point-in-time premarket recommendation/NO-TRADE plan, preserve the exact evidence available before the freeze boundary, perform post-close outcome attribution, and convert repeated evidence into replay-tested rule improvements without future-information leakage.

This is a recommendation/research system, not a generic multi-agent framework and not an execution broker.

## User outcomes

A user entering the A-share Agent should be able to:

1. start a new current-trading-day recommendation directly inside the A-share Agent;
2. receive a concise first-read answer plus an auditable research/evidence trail;
3. understand why selected stocks beat recalled peers, what invalidates them, and when NO TRADE is the correct result;
4. resume an explicitly referenced historical A-share run without turning it into the current day;
5. run post-close review against the immutable premarket snapshot;
6. see misses classified by the earliest failed layer and converted into bounded learning candidates;
7. promote durable rule changes only after replay/regression evidence across multiple regimes.

## Business identity and ownership

- A-share market-day/run identity is domain-owned. `TaskContract.task_id` plus its `MarketDayState` is the business-run identity used by the domain runtime.
- `trading_date` is business time, not a UAOS task identity.
- UAOS may own one domain router and may retain an opaque child reference for continuity, but must not create/adopt a same-ID market-day business task.
- New current-day work creates a fresh child-owned run after resolving the China trading day and freeze boundary.
- Historical runs are explicit-only unless the child domain proves a unique current compatible run; a prior premarket run never silently becomes today’s task.

## Source architecture

Source ownership is fact-specific; one vendor is not declared universally authoritative.

1. **Official/first-party facts** — exchanges, regulators, ministries and company disclosures own hard regulatory/corporate facts and announcement timing.
2. **同花顺 / Level-2 lane (when current-session proven)** — preferred market-state and microstructure lane for quotes, auction/depth/order-flow context, turnover/board behavior and close/review cross-checks. Level-2 evidence is higher-value than weaker quote summaries for execution/buyability claims.
3. **选股通 Dingpan lane** — canonical business lane for the five review pools: `limit_up`, `limit_down`, `limit_up_broken`, `super_stock`, `yesterday_limit_up`. Counts/date semantics must reconcile before use.
4. **Structured market-data fallback/corroboration** — Longbridge or another current-session structured connector can supply calendars, bars, quotes, depth/flow and cross-checks when the preferred lane is unavailable; it does not redefine the five Dingpan pools.
5. **P01–P09 research set** — event/news/industry discovery and corroboration under point-in-time freeze rules.

Missing a preferred lane must never be silently treated as equivalent evidence. The affected claim is blocked or explicitly degraded, with the exact missing capability recorded.

## Premarket decision architecture

Canonical stage order remains deterministic and fail-closed, while work *inside* a stage may run concurrently when dependencies permit.

- Resolve current China trading day and legal freeze boundary.
- Acquire independent source lanes in parallel where possible.
- Reconcile source completeness and timestamps before admitting evidence.
- Build the all-news event ledger before prioritization.
- Research industries deeply and map every eligible stock or exclusion reason.
- Build market-structure hypotheses from evidence, not board count alone.
- Preserve broad U0/U1 recall before execution narrowing.
- Produce independent candidate views from event/industry alpha, market-structure leadership, and Level-2/buyability/execution quality.
- Run a bounded counterevidence/red-team pass.
- A single authorized A-share decision owner adjudicates the candidate views into U3 (maximum four role slots) or NO TRADE.
- Premarket audit must pass before the snapshot is frozen.

Internal competition is structured artifact comparison, not free-form peer chat. Advisory/reviewer work cannot silently become the final recommendation.

## Post-close review architecture

- Reconcile actual market outcomes, Dingpan five pools and market/Level-2 close evidence.
- Preserve the frozen premarket snapshot unchanged.
- Attribute actual limit-ups, broken boards, limit-downs and key misses against frozen U0/U1 membership.
- Measure recall, selection quality and—where evidence exists—execution feasibility separately.
- Classify the earliest failed layer: source, event, industry, mapping, role/ranking, timing, or genuinely unknowable.
- Produce learning hypotheses or an explicit no-change reason.

## Cognition and evolution

Every detected problem—source conflict, missed candidate, false positive, broken-board risk, execution infeasibility, repeated user correction, audit failure or regression—must trigger:

1. concrete diagnosis;
2. macro goal / market-decision architecture check;
3. governing-assumption challenge;
4. external method/fact research.

Risk determines additional depth (counterexamples, independent verification); familiarity is never a waiver from research/reflection.

A single trading day may create evidence and hypotheses but may not directly rewrite durable strategy rules. Durable promotion requires the canonical owner, applicable regimes, counterexamples, at least five frozen replay cases across at least two regimes, positive and negative samples, no future-information contamination, no material regression, and current CI evidence.

## Core outputs

- frozen premarket snapshot;
- recommendation / NO-TRADE report;
- post-close review report;
- learning/replay record;
- provenance and gate evidence sufficient to reconstruct why a decision was made with only information legally available at the time.

## Non-goals

- guaranteed returns or guaranteed limit-ups;
- filling recommendation slots when evidence does not justify them;
- using post-close facts to improve a frozen premarket thesis retrospectively;
- letting UAOS own per-day A-share business identities/state;
- creating persistent specialist Agents merely to simulate debate;
- silently replacing missing Level-2/preferred data with weaker data while preserving the same assurance claim.

## Acceptance map

| Requirement | Owning surface | Mechanical / audit evidence |
| --- | --- | --- |
| Child-owned market-day identity | `models.py`, `.uaos/ADAPTER.json`, `UAOS_SKILL.md` | identity-boundary tests/static audit |
| Point-in-time freeze | `schemas.py`, `engine.py`, `references/sources.md` | freeze and source tests |
| Preferred THS/Level-2 + Dingpan roles | `source_contracts.py`, `references/sources.md` | source-role contract tests |
| Broad recall before narrowing | `schemas.py`, `references/research.md`, integrity guards | U0/U1/U3 lineage tests |
| Structured candidate competition/adjudication | `config/MARKET_DAY_ORCHESTRATION.json`, `orchestration.py` | graph validation/ready-node tests |
| NO TRADE legal | `schemas.py`, `references/execution.md` | execution-plan tests |
| Frozen post-close attribution | `references/review.md`, integrity guards | attribution/recall-grade tests |
| Evidence-gated learning | `references/learning.md`, replay schema/evals | replay contract eval |
| Problem research/reflection floor | `.uaos/CAPABILITIES.json`, maintenance/learning references | architecture/static tests |
