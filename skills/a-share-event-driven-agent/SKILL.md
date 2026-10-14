# A-share Event-Driven Agent

Use this Skill for A-share main-board premarket recommendation, post-close review, and domain execution after UAOS has resolved the task. Do not use it for publishable financial article writing; the Financial Writing Agent owns that workflow.

Cross-domain controller: `D1traverser-debug/universal-agent-os@main`. This repository owns A-share business rules, source/data contracts, domain runtime code and business evidence; it no longer owns global cross-chat continuity.

## Product entry, authority and cutover

Normal use has one product path: `ChatGPT request → UAOS intent/task routing → A-share domain workflow`. Do not ask the user to choose owner-native, `CHAT_BRIDGED`, MCP, runtime, or another execution plane. Those are internal readiness/evidence labels selected by the system.

Before material work read `continuity/UAOS_ADAPTER.json`, `config/cutover_status.json` and `continuity/EXECUTION_CAPABILITIES.json` from current GitHub `main`.

- UAOS is authoritative for cross-domain task identity, continuation, current trading-day routing, requirements and action lineage.
- GitHub `main` in this repository is canonical A-share code/rule/data-contract and domain-evidence authority.
- `config/cutover_status.json` decides whether the owner Runtime checkpoint may additionally become executable market-day business-state authority.
- If `runtime_authority_enabled=true` and promotion evidence remains valid, Runtime checkpoint is executable market-day business-state authority; this repository remains code/rule authority and UAOS remains controller authority.
- If disabled, Runtime stays candidate/shadow. Legacy `continuity/tasks/<task>/TASK_MANIFEST.json` + `HANDOFF.md` are migration/provenance evidence and must not be written as the active cross-chat controller after UAOS cutover.
- Notion/Google Drive are source, knowledge, artifact, or migration-mirror inputs only unless a future cutover explicitly says otherwise.
- StockBase is for recommendation reads; review is the only workflow allowed to record a writeback receipt.

Capability/readiness selection is internal. For the exact next action, handshake only required capabilities; use the strongest legal binding actually available in the active UAOS host. `CHAT_BRIDGED` is allowed only where the capability manifest declares it safe. A missing hard capability waits/blocks that exact gate rather than changing the business SOP or making the whole Agent unusable. Never claim isolated execution without distinct execution/context/trace evidence.

The canonical public MCP/runtime surface is `ashare_event_agent/plugin_server.py`. `runtime_service.py`, `controller.py`, `engine.py` and `store.py` are internal. `runner.AgentRuntime` is a test/offline injected-executor harness, not live-adapter evidence. `source_contracts.py` defines source contracts, not a native P01-P09 acquisition executor.

A role description, Skill paragraph, code stub, configured tool name, `GateDecision`, or audit-tool call is not execution evidence. Owner-Runtime completion requires owner state/checkpoint evidence; controller progress requires UAOS task/action evidence to be persisted and reread.

Do not fall back to a Notion/Drive controller or the retired Universal Continuity controller. A documentation or cutover-file change is not proof that Runtime promotion gates passed.

## New task vs continuation

Apply the global rule: **inherit learning, not unfinished work**.

- New market-day work does not inherit another task's stage, freeze hash, shortlist, blockers or next action.
- `ashare:recommendation` is a routing entry: UAOS resolves the current trading day before creating or locating a market-day task.
- A historical premarket task must never resume later as if its old time window still existed; reconcile it as historical/post-close evidence first.
- Explicit continuation may recover the matching USER task only after UAOS resolves its migration disposition.
- TEST / FIXTURE / EVAL / SYSTEM_INFRA tasks must not appear in ordinary bare-`继承` candidate discovery.
- Before resuming, verify current domain/runtime compatibility and classify recovery as `COMPATIBLE`, `MIGRATABLE` or `INCOMPATIBLE`; do not restore obsolete execution semantics.

## Startup

Always recover through UAOS first:

1. Read UAOS `ENTRYPOINT.md`, `CURRENT_SYSTEM.json`, then the matching record in `state/TASK_INDEX.json` and this repository's `continuity/UAOS_ADAPTER.json`.
2. For a UAOS-native task, use its current UAOS task state. For an unimported legacy task, read the declared legacy manifest/HANDOFF exactly once as migration evidence.
3. Resolve the current trading day before any new premarket task. Do not treat a past market-day child as current merely because the legacy parent points to it.
4. Refresh this Skill + `config/cutover_status.json` + `continuity/EXECUTION_CAPABILITIES.json` and handshake only the exact capabilities required now.
5. If Runtime authority is enabled and session-proven, load/resume the owner Runtime checkpoint and bind evidence to the current UAOS task/action lineage.
6. Otherwise continue only legal research/source/evidence actions and leave Runtime-only certification WAITING/BLOCKED. Never route business control to Notion/Drive or the retired continuity repository.
7. Maintain FreezeCard boundaries before finalizing dynamic premarket data; never skip a gate.
8. Once a legacy task is imported, write continuation state only to UAOS; do not refresh old resume_epoch/lease/progress-receipt fields.

## Premarket cognition

Read canonical root `references/sources.md`, `research.md`, `industry.md`, `market_structure.md`, `execution.md`, `audit.md` progressively as stages require. Copies under `skills/a-share-event-driven-agent/references/` and `ashare_event_agent/resources/references/` are generated distribution mirrors, not additional rule owners.

Research is recall-first: build U0/U1 broadly, then role-rank U2 and narrow U3. Do not let Leader-First prune the research universe.

The research substrate is intended to evolve toward a shared A-share Intelligence Core: event/catalyst, concept/industry graph, detailed value-chain nodes, company mapping, operating/financial realization, market role/position, future events, counterevidence and provenance. Premarket and post-close may reuse this intelligence, but executable state remains the market-day task lifecycle. Future architecture is non-executable until implementation/cutover evidence exists.

## Post-close

Continue the same FROZEN market-day task when its internal execution binding is authoritative and compatible. Read `references/review.md` and `learning.md`. Grade knowable recall against the immutable premarket snapshot. Never backfill post-close facts into FrozenPremarketDecision.

Learning proposals require replay before durable promotion. A single day creates a hypothesis, not a permanent rule.

## Recovery

Read `references/recovery.md`, `config/cutover_status.json` and `continuity/UAOS_ADAPTER.json`. Never rely on deleted chat history or ask the user to repeat durably persisted facts.

UAOS is the recovery entrypoint. If an executable Runtime checkpoint or a required live capability is unavailable, surface the precise gap and continue only legal governance/research actions; never reconstruct authority from chat memory, external mirrors, or retired v3.7 continuity files.

## Maintenance and self-evolution

Read `references/maintenance.md`. A documentation edit is not proof of executed behavior; traces, tests, replay evidence and frozen artifacts are proof.

When a `PROPOSE` rule receives replay `PASS`, treat it as promotion-eligible, not silently promoted. Change only the canonical rule owner, add/update regression and replay cases, run available tests/static/contract checks, independently review the diff where real independent execution exists, and promote only while criteria remain satisfied. Mirrors never become control authority. A failed/HOLD replay must not alter durable executable policy.

System defects should be repaired at the unique owner: `detect → classify root cause → repair code/Skill/contract → add regression/replay → validate → review at the available assurance level → promote`. System-wide changes go through UAOS evolution governance. Do not solve repeated execution failures by copying more prose into Notion/Drive or creating a second harness/Skill/rule surface.
