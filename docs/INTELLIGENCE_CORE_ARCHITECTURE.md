# A-share Intelligence Core Architecture

Status: architecture boundary for staged migration. This document does **not** promote the candidate Runtime to operational authority; `config/cutover_status.json` remains the only cutover switch.

## 1. Purpose

Premarket recommendation, post-close review and Financial Writing need the same factual world but optimize different objectives. The shared layer therefore owns **research intelligence**, not business workflow state.

The target architecture is:

```text
Universal Continuity Layer
        |
        +--> A-share Market Agent
        |      +-- Premarket recommendation
        |      +-- Post-close review / learning
        |
        +--> Financial Writing Agent
                   |
                   v
          A-share Intelligence Core
```

The Core must make the system broadly knowledgeable without forcing every task to load every Notion/Drive document into model context. Knowledge is comprehensive at rest and retrieved selectively at execution time.

## 2. Reuse what already exists

Current canonical schemas already contain useful Core primitives:

- `EvidenceRecord` — claim/provenance/availability/confidence/negative evidence.
- `EventCard` — event/catalyst identity and tradability classification.
- `IndustryNode` — multi-level value-chain/industry node with economics and direction.
- `StockMapping` — company-to-event/node mapping, business stage, products, customers/orders/capacity, profit transmission and positive/negative evidence.
- `SourceReceipt` — source completeness and retrieval boundary.

These should evolve into the shared research substrate rather than be duplicated into a second StockBase/ArticleBase/MarketBase implementation.

## 3. What is **not** shared durable knowledge

The following are market-day/task-state objects and remain owned by Market Agent:

- `FreezeCard`
- `HeightRecord`
- `RoleHypothesis`
- `MarketStructurePackage`
- `RecallCandidate` / `RecallPoolPackage`
- `ExecutionCandidate` / `ExecutionPlan`
- FROZEN snapshot/hash
- post-close `OutcomePackage`, `AttributionPackage`, `RecallGrade`

A company may have stable factual attributes in the Core, while its role (leader, pioneer, card leader, capacity anchor, ambush, etc.) is time-bound and must never be promoted into permanent company truth without an explicit time dimension.

## 4. Knowledge classes

The Core logically separates at least:

1. **Stable Knowledge** — company business, products, customers, capacity, ownership/relationships, value-chain position.
2. **Event Knowledge** — policy, order, price, product launch, conference, earnings, supply/demand shock, future calendar catalyst.
3. **Industry/Concept Graph** — event -> concept -> L0..Ln node -> economics -> beneficiary/damage path -> company mapping.
4. **Evidence Ledger** — source, availability time, effective time, claim, confidence, counterevidence and provenance.
5. **Market Observation** — date/time-scoped facts that may inform Market Agent but are not stable company truth.
6. **Hypothesis** — an unpromoted explanatory/strategy proposition requiring replay or repeated evidence.
7. **Promoted Rule** — executable strategy policy only after replay/regression/promotion gates.
8. **Writing Learning** — title/hook/retention/article-craft evidence owned by Financial Writing, not by Market Agent strategy rules.

## 5. Fact and strategy rule must never share a promotion path

Example:

- `Company X owns platform Y` can become a durable fact after evidence validation.
- `Platform-Y companies are more likely to limit-up tomorrow` is a strategy hypothesis, not a fact.

A single market day may create a hypothesis but may not directly create a durable executable rule. Strategy promotion remains:

`observation -> hypothesis -> frozen historical replay -> regression/counterexample audit -> promotion eligibility -> reviewed code/rule change`.

## 6. KnowledgeCandidate write path

Any consumer may discover knowledge, but consumers do not directly mutate durable truth.

Target contract:

```text
Consumer (Premarket / Review / Writing / Research)
        |
        v
KnowledgeCandidate
        |
        +-- dedupe / entity resolution
        +-- provenance & effective-time validation
        +-- conflict / counterevidence scan
        +-- freshness / expiry classification
        +-- stable-vs-event-vs-market-state classification
        v
Knowledge Curator
        |
        v
Canonical Intelligence Core
```

Minimum candidate fields should include:

- `candidate_id`
- `claim`
- `entity_refs`
- `knowledge_class`
- `source_refs`
- `available_at`
- `effective_from` / `effective_to` when known
- `confidence`
- `positive_evidence`
- `negative_evidence`
- `conflicts`
- `discovered_by`
- `discovered_in_task_id`
- `status = PENDING | ACCEPTED | REJECTED | SUPERSEDED`

This generalizes the current `StockBase_pending_updates/ReviewQueue` idea rather than letting each consumer invent a separate writeback mechanism.

## 7. Read path: broad knowledge, narrow context

Do not solve “all-knowing system” by loading all persistent documents into every prompt.

Execution should query by current task:

`event/catalyst -> related graph nodes -> mapped companies -> stable facts -> evidence -> historical/event context -> required task-specific market state`.

The Core can be large; the model context should be relevance-selected and evidence-bounded.

## 8. Consumer boundaries

### Market Agent / Premarket
Reads shared intelligence, then owns freeze, recall, role ranking, buyability, trigger/invalidation and execution planning.

### Market Agent / Post-close
Reads the immutable premarket snapshot plus actual outcomes. It may propose knowledge corrections and strategy hypotheses. It is the current controlled reviewer for StockBase-style durable company updates until the Curator path is implemented.

### Financial Writing Agent
Reads shared intelligence and may submit KnowledgeCandidates discovered during research. It owns article cognition, structure, title, hook, human voice, delivery and writing-specific learning. It must not mutate Market Agent execution rules.

## 9. Storage roles during migration

- **GitHub**: schema/code/Skill/tests/evals/rule ownership.
- **Runtime durable store**: task/checkpoint/freeze/gates/artifact identity/version.
- **Notion**: human-readable knowledge/navigation/dashboard/mirror.
- **Google Drive**: raw source documents, large artifacts, reports, historical snapshots.
- **ChatGPT Library Continuity v2**: task discovery/routing pointers, not a second A-share database.

## 10. Migration order

1. Keep existing production/shadow governance intact; no premature cutover.
2. Add explicit KnowledgeCandidate schema and tests without changing StockBase write authority.
3. Map current EventBase/IndustryBase/StockBase fields into Core primitives; do not create duplicate truth stores.
4. Build read-only Core query/package interface first.
5. Make Premarket and Writing consume the same Research/Intelligence package in shadow comparison.
6. Add Curator write path and conflict/version semantics.
7. Migrate ReviewQueue into the Curator path only after replay/E2E evidence.
8. Cut over components independently behind explicit machine-readable gates.

## 11. Non-goals

- No monolithic “super Skill”.
- No automatic merging of recommendation, review and writing state machines.
- No loading the full knowledge base into every prompt.
- No direct consumer writes to canonical durable truth without validation.
- No promotion of post-close hindsight into premarket facts.
- No Runtime authority change merely because this architecture document exists.
