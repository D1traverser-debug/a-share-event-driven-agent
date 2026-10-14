# A-share Intelligence Core Architecture

Status: **future shared-research boundary / non-executable design**. This document does not create a Core, change current business authority, or promote the hosted runtime.

Current authority is defined by `.uaos/*`, `config/RUNTIME_AUTHORITY.json`, `docs/product_requirements.md` and the A-share runtime/contracts. The A-share domain owns market-day business identity/state; UAOS is the parent control plane and must not mirror per-day A-share business state.

## Purpose

Premarket recommendation, post-close review and Financial Writing may need overlapping factual company/event/industry knowledge, but they optimize different products. A future shared layer may own **research intelligence**, not consumer business workflow state.

Target relationship:

```text
UAOS common control/governance plane
        |
        +--> A-share Event-Driven Agent
        |      +-- Premarket recommendation
        |      +-- Post-close review / learning
        |
        +--> Financial Writing Agent
        |
        +--> future shared research/intelligence substrate
```

The shared substrate must not become another controller, task registry or recommendation engine.

## Reuse current A-share primitives

Current canonical schemas already contain useful research primitives:

- `EvidenceRecord` — claim/provenance/availability/confidence/negative evidence.
- `EventCard` — event/catalyst identity and tradability classification.
- `IndustryNode` — multi-level value-chain/industry node with economics and direction.
- `StockMapping` — company-to-event/node mapping, business stage, products, customers/orders/capacity, profit transmission and positive/negative evidence.
- `SourceReceipt` — source completeness and retrieval boundary.

These can evolve into a shared research substrate rather than be copied into parallel StockBase/ArticleBase/MarketBase truth stores.

## What must remain A-share market-day state

The following are time-bound recommendation/review objects and remain owned by the A-share Agent:

- `TaskContract.task_id` / `MarketDayState`
- `FreezeCard`
- `HeightRecord`
- `RoleHypothesis`
- `MarketStructurePackage`
- `RecallCandidate` / `RecallPoolPackage`
- `ExecutionCandidate` / `ExecutionPlan`
- frozen snapshot/hash
- post-close `OutcomePackage`, `AttributionPackage`, `RecallGrade`
- `config/MARKET_DAY_ORCHESTRATION.json` business decision graph

A stable company fact may be shared; a stock's current role, buyability, U1 membership or recommendation slot may not be promoted into timeless company truth.

## Knowledge classes

A future Core may distinguish:

1. stable company knowledge;
2. event/catalyst knowledge;
3. industry/concept/value-chain graph;
4. evidence ledger with availability/effective time;
5. date-scoped market observations;
6. unpromoted hypotheses;
7. promoted strategy rules only after replay/regression;
8. writing-specific learning owned by Financial Writing.

## Fact and strategy rules must never share a promotion path

Example:

- `Company X supplies product Y` can become a durable fact after evidence validation.
- `Product-Y suppliers are more likely to limit-up tomorrow` is a strategy hypothesis and must use the A-share replay/promotion path.

A single day may create a hypothesis but may not directly create a durable executable recommendation rule.

## Candidate write path

Any consumer may discover knowledge but must not directly overwrite shared truth:

`consumer -> KnowledgeCandidate -> entity/provenance/time/conflict validation -> curator -> canonical shared intelligence`.

Suggested candidate fields include claim, entity refs, knowledge class, source refs, available/effective time, confidence, positive/negative evidence, conflicts, discoverer, originating child business ref and status.

The originating A-share child task ID may be stored as provenance; it must not become a shared controller identity.

## Read path

Do not make an “all-knowing” system by loading all persistent documents into every prompt.

Read selectively:
`event/catalyst -> related graph nodes -> mapped companies -> stable facts -> evidence -> historical/event context -> task-specific market state`.

The shared store can be broad; execution context remains relevance-selected and point-in-time bounded.

## Consumer boundaries

### A-share / Premarket
Reads shared intelligence, then owns trading-day identity, freeze, recall, role ranking, buyability, candidate adjudication and execution planning.

### A-share / Post-close
Reads the immutable frozen snapshot plus actual outcomes. It may propose knowledge corrections and strategy hypotheses; strategy promotion remains A-share-owned and replay-gated.

### Financial Writing
May read shared intelligence and submit knowledge candidates. It owns article identity, workflow, writing decisions and writing-specific evolution. It must not mutate A-share recommendation rules.

## Current storage/authority roles

- **A-share GitHub `main`**: product/code/rules/tests/evals authority.
- **A-share child market-day state**: domain business identity/state.
- **Hosted runtime store**: durable executable checkpoint authority only if current promotion gates pass.
- **UAOS**: cross-domain parent governance/common capabilities/optional parent guidance, not per-day market state.
- **StockBase/current knowledge inputs**: read/review-write under their receipt boundaries.
- **Notion/Google Drive/external stores**: source/knowledge/artifact inputs only.

## Migration order if the Core is ever implemented

1. Keep current A-share product/identity boundaries intact.
2. Add explicit KnowledgeCandidate schema/tests without changing current StockBase write authority.
3. Map current event/industry/company fields into shared primitives without duplicate truth stores.
4. Build read-only query/package interface first.
5. Shadow-compare A-share and Financial consumption.
6. Add curator conflict/version/write path.
7. Migrate existing review queues only after replay/E2E evidence.
8. Cut over components independently behind machine-readable gates.

## Non-goals

- no monolithic super Skill;
- no merging of recommendation/review/writing state machines;
- no full-knowledge dump into every prompt;
- no direct consumer mutation of shared truth without validation;
- no post-close hindsight promoted into premarket facts;
- no parent/shared layer ownership of A-share market-day identities or state;
- no runtime/Core authority change merely because this document exists.
