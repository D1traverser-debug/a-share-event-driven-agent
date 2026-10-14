---
name: a-share-event-driven-agent-uaos
scope: A-share main-board premarket recommendation and post-close review
---

# A-share Event-Driven Agent — UAOS Entry

Controller: `D1traverser-debug/universal-agent-os@main`.
Domain repository: `D1traverser-debug/a-share-event-driven-agent@main`.

UAOS owns intent, task identity, requirements, cross-chat continuation, current-task routing and controller action lineage. This repository owns A-share rules, data/source contracts, domain runtime code, frozen market evidence and domain QA.

## Start

After UAOS resolves the request, read only:
1. `continuity/UAOS_ADAPTER.json`;
2. `continuity/UAOS_MANIFEST.json`;
3. `continuity/EXECUTION_CAPABILITIES.json`;
4. `config/cutover_status.json`;
5. the exact domain business evidence required by the current market-day work.

A recommendation request must resolve the current China trading day before any market-day task is created or resumed. A past premarket task is historical evidence, never a current premarket task.

## Authority and time semantics

UAOS is the cross-chat controller. GitHub `main` here is canonical A-share code/rule/data-contract authority. `config/cutover_status.json` determines whether the domain runtime is promoted to executable market-day business-state authority; a shadow/candidate runtime must not impersonate promoted execution.

Point-in-time discipline is mandatory: later facts may not be inserted into an earlier frozen decision. FreezeCard/source timestamps, snapshot completeness, source reconciliation, Universe membership and downstream lineage must be preserved.

## Premarket

Load canonical references progressively as needed: `references/sources.md`, `research.md`, `industry.md`, `market_structure.md`, `execution.md`, `audit.md`.

Research is recall-first: construct the broad stock-level universe before narrowing. Preserve industry/value-chain many-to-many mappings, explicit exclusions, peer accounting and why-not-peers evidence. Required live/current inputs must come from capabilities actually available in the active session; code/config declaring a source is not proof that the data was acquired.

If a hard live-data or verification capability is absent, leave the affected gate WAITING/BLOCKED. Do not silently replace it with stale data or a weaker source and claim the original objective was met.

## Post-close

Post-close review must grade the immutable premarket snapshot against actual outcomes. Never backfill outcome knowledge into the frozen recommendation. A single market day may create a learning candidate, not a permanent system rule; promotion requires replay/regression evidence.

## Completion

Completion requires UAOS task/action state plus exact current domain evidence: required source/time/universe/freeze/QA gates must all satisfy the applicable workflow. Provider/role labels and code presence are not execution proof.

Do not create a parallel cross-chat controller, task index, lease system or continuation protocol inside this repository.
