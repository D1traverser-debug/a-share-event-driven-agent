# A-share Recommendation System — Product Requirements

Version: 0.3.0
Authority: `A_SHARE_EVENT_DRIVEN_AGENT`
Parent method dependency: `UAOS COMMON_CAPABILITIES >= 1.6.0`

## Product mission

Provide an auditable A-share main-board, event-driven decision system for 1–2 trading-day horizons. The product must produce a point-in-time premarket recommendation/NO-TRADE plan, preserve the exact evidence available before the freeze boundary, distinguish opportunity strength from risk/execution feasibility, perform post-close outcome and execution attribution, and convert repeated evidence into replay-tested rule improvements without future-information leakage.

This is a recommendation/research system, not a generic multi-agent framework and not an execution broker.

## User outcomes

A user entering the A-share Agent should be able to:

1. start a new current-trading-day recommendation directly inside the A-share Agent;
2. receive a concise first-read answer plus an auditable research/evidence trail;
3. understand why selected stocks beat recalled peers, what invalidates them, what risk evidence constrains or vetoes them, and when NO TRADE is the correct result;
4. distinguish a strong opportunity that is not executable from a weaker but executable plan rather than mixing both into one opaque score;
5. resume an explicitly referenced historical A-share run without turning it into the current day;
6. run post-close review against the immutable premarket snapshot;
7. see research recall quality, final-pick selection quality and execution feasibility graded separately;
8. see misses classified by the earliest failed layer and converted into bounded learning candidates;
9. promote durable rule changes only after replay/regression evidence across multiple regimes.

## Business identity and ownership

- A-share market-day/run identity is domain-owned. `TaskContract.task_id` plus its `MarketDayState` is the business-run identity used by the domain runtime.
- `trading_date` is business time, not a UAOS task identity.
- UAOS may own one domain router and may retain an opaque child reference for continuity, but must not create/adopt a same-ID market-day business task.
- New current-day work creates a fresh child-owned run after resolving the China trading day and freeze boundary.
- Historical runs are explicit-only unless the child domain proves a unique current compatible run; a prior premarket run never silently becomes today's task.

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
- Produce independent **opportunity** views from event/industry alpha and market-structure leadership.
- Run a bounded counterevidence/red-team pass over opportunity views.
- Adjudicate a preliminary opportunity slate.
- Apply an explicit risk/execution-feasibility layer across every frozen U1 candidate using current-session market/microstructure evidence where available.
- Risk/buyability is a constraint and veto layer, not another bullish opinion. A `BLOCK` risk assessment cannot be outvoted into U3.
- Missing preferred Level-2 evidence may yield a degraded-assurance plan, but a plan may not claim FULL execution assurance without preferred microstructure evidence.
- One authorized A-share trade-decision owner combines opportunity evidence, risk assessments and counterevidence into U3 (maximum four role slots) or NO TRADE.
- Premarket audit must pass before the snapshot is frozen.

Internal competition is structured artifact comparison, not free-form peer chat. Advisory/reviewer work cannot silently become the final recommendation.

## Post-close review architecture

Post-close review must answer three different questions rather than collapse them into one hit rate:

1. **Research recall quality** — did frozen U0/U1 contain the knowable opportunities?
2. **Final selection quality** — among the frozen final recommendations, which triggers actually activated and what happened after activation?
3. **Execution feasibility quality** — when a trigger activated, was an executable entry actually available under observed market/microstructure conditions?

Required review behavior:

- Reconcile actual market outcomes, Dingpan five pools and market/Level-2 close evidence.
- Preserve the frozen premarket snapshot unchanged.
- Attribute actual limit-ups, broken boards, limit-downs and key misses against frozen U0/U1 membership.
- For every final U3 candidate, explicitly record whether its trigger occurred. If activated, record entry feasibility and execution evidence.
- Mechanically derive selection quality: activated positive rate, activated downside rate and execution feasibility rate.
- A candidate whose trigger never occurred is not counted as an executed win or loss.
- Classify the earliest failed layer: source, event, industry, mapping, role/ranking, timing, risk/execution, or genuinely unknowable.
- Produce learning hypotheses or an explicit no-change reason.

## Cognition and evolution

Every detected problem—source conflict, missed candidate, false positive, broken-board risk, execution infeasibility, repeated user correction, audit failure or regression—must trigger:

1. concrete diagnosis;
2. macro goal / market-decision architecture check;
3. governing-assumption challenge;
4. external method/fact research.

Risk determines additional depth (counterexamples, independent verification); familiarity is never a waiver from research/reflection.

A single trading day may create evidence and hypotheses but may not directly rewrite durable strategy rules. Durable promotion requires the canonical owner, applicable regimes, counterexamples, at least five frozen replay cases across at least two regimes, positive and negative samples, no future-information contamination, no material regression, and current CI evidence.

A PASS replay must report at least: `u1_recall`, `activated_positive_rate`, `activated_downside_rate`, and `execution_feasibility_rate` for both baseline and candidate. A rule may not be promoted merely because recall improved while final-selection downside or executability deteriorated.

## Core outputs

- frozen premarket snapshot;
- recommendation / NO-TRADE report with opportunity reasoning, risk/feasibility assurance, triggers and invalidations;
- post-close review report separating recall, final-selection quality and execution feasibility;
- learning/replay record;
- provenance and gate evidence sufficient to reconstruct why a decision was made with only information legally available at the time.

## Non-goals

- guaranteed returns or guaranteed limit-ups;
- filling recommendation slots when evidence does not justify them;
- using post-close facts to improve a frozen premarket thesis retrospectively;
- treating risk/buyability as a third bullish vote that can be outvoted by opportunity research;
- counting a never-triggered recommendation as if it were an executed trade;
- optimizing recall while ignoring final-selection downside or execution feasibility;
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
| Opportunity competition separate from risk | `config/MARKET_DAY_ORCHESTRATION.json`, `schemas.py`, `integrity.py` | graph/risk-veto tests |
| Every U1 risk-assessed; BLOCK excluded from U3 | `schemas.py`, `integrity.py` | execution integrity tests |
| NO TRADE legal | `schemas.py`, `references/execution.md` | execution-plan tests |
| Frozen post-close attribution | `references/review.md`, integrity guards | attribution/recall-grade tests |
| Final-selection and execution quality | `schemas.py`, `integrity.py`, `references/review.md` | selection-quality derivation tests |
| Evidence-gated learning | `references/learning.md`, replay schema/evals | replay contract eval |
| Replay covers recall + selection + execution metrics | `schemas.py`, `config/policy.json` | replay PASS validation |
| Problem research/reflection floor | `.uaos/CAPABILITIES.json`, maintenance/learning references | architecture/static tests |
