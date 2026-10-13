# A-share Event-Driven Agent

Use this Skill for A-share main-board premarket recommendation, post-close review, and continuation of an existing market-day task. Do not use it for publishable financial article writing; the Financial Writing Agent owns that workflow.

## Product entry, authority and cutover

Normal use has one product path: the user gives this Agent the task in ChatGPT. Do not ask the user to choose owner-native, `CHAT_BRIDGED`, MCP, runtime, or another execution plane. Those are internal readiness/evidence labels selected by the system.

Read `config/cutover_status.json` and `continuity/EXECUTION_CAPABILITIES.json` from current GitHub `main` before material work.

- GitHub `main` is canonical code/rule and Continuity governance authority.
- `config/cutover_status.json` decides whether the owner Runtime checkpoint may additionally become executable market-day state authority.
- If `runtime_authority_enabled=true` and promotion evidence remains valid, Runtime checkpoint is executable market-day state authority; GitHub remains code/rule/Continuity authority.
- If disabled, Runtime stays candidate/shadow. GitHub `continuity/tasks/<task>/TASK_MANIFEST.json` + `HANDOFF.md` may record governance stage/next action/evidence, but must not impersonate Runtime execution.
- Notion/Google Drive are source, knowledge, artifact, or migration-mirror inputs only unless a future cutover explicitly says otherwise.
- StockBase is for recommendation reads; review is the only workflow allowed to record a writeback receipt.

Capability/readiness selection is internal. For the exact next action, handshake only required capabilities; use the strongest legal owner binding actually available. `CHAT_BRIDGED` is allowed only where the capability manifest declares it safe. A missing hard capability blocks that exact gate rather than changing the business SOP or making the whole Agent unusable. Never claim isolated execution without distinct execution/context/trace evidence.

The canonical public MCP/runtime surface is `ashare_event_agent/plugin_server.py`. `runtime_service.py`, `controller.py`, `engine.py` and `store.py` are internal. `runner.AgentRuntime` is a test/offline injected-executor harness, not live-adapter evidence. `source_contracts.py` defines source contracts, not a native P01-P09 acquisition executor.

A role description, Skill paragraph, code stub, configured tool name, `GateDecision`, or audit-tool call is not execution evidence. Owner-Runtime completion requires owner state/checkpoint evidence; governance-only progress requires the GitHub Continuity checkpoint to be written and reread.

Do not fall back to a Notion/Drive controller. A documentation or cutover-file change is not proof that Runtime promotion gates passed.

## New task vs continuation

Apply the global rule: **inherit learning, not unfinished work**.

- New market-day work does not inherit another task's stage, freeze hash, shortlist, blockers or next action.
- Explicit continuation may recover the matching USER task only.
- TEST / FIXTURE / EVAL / SYSTEM_INFRA tasks must not appear in ordinary bare-`继承` candidate discovery.
- Before resuming, verify current Agent compatibility and classify recovery as `COMPATIBLE`, `MIGRATABLE` or `INCOMPATIBLE`; do not restore obsolete execution semantics.

## Startup

Always recover through GitHub Continuity first:

1. Read matching USER `TASK_MANIFEST.json` + `HANDOFF.md` and `config/cutover_status.json`.
2. Resume a matching compatible market-day child before creating a duplicate.
3. Refresh the current Skill + `continuity/EXECUTION_CAPABILITIES.json`.
4. If Runtime authority is enabled and session-proven, load/resume the owner Runtime checkpoint and bind evidence back to GitHub Continuity.
5. Otherwise continue only legal GitHub-governed research/source/evidence actions and block Runtime-only certification. Never route business control to Notion/Drive.
6. Maintain FreezeCard boundaries before finalizing dynamic premarket data; never skip a gate.

## Premarket cognition

Read canonical root `references/sources.md`, `research.md`, `industry.md`, `market_structure.md`, `execution.md`, `audit.md` progressively as stages require. Copies under `skills/a-share-event-driven-agent/references/` and `ashare_event_agent/resources/references/` are generated distribution mirrors, not additional rule owners.

Research is recall-first: build U0/U1 broadly, then role-rank U2 and narrow U3. Do not let Leader-First prune the research universe.

The research substrate is intended to evolve toward a shared A-share Intelligence Core: event/catalyst, concept/industry graph, detailed value-chain nodes, company mapping, operating/financial realization, market role/position, future events, counterevidence and provenance. Premarket and post-close may reuse this intelligence, but executable state remains the market-day task lifecycle. Future architecture is non-executable until implementation/cutover evidence exists.

## Post-close

Continue the same FROZEN market-day task when its internal execution binding is authoritative and compatible. Read `references/review.md` and `learning.md`. Grade knowable recall against the immutable premarket snapshot. Never backfill post-close facts into FrozenPremarketDecision.

Learning proposals require replay before durable promotion. A single day creates a hypothesis, not a permanent rule.

## Recovery

Read `references/recovery.md` and `config/cutover_status.json`. Never rely on deleted chat history or ask the user to repeat durably persisted facts.

GitHub Continuity remains the recovery entrypoint. If an executable Runtime checkpoint is unavailable, surface the precise capability gap and continue only legal governance/research actions; never reconstruct authority from chat memory or external mirrors.

## Maintenance and self-evolution

Read `references/maintenance.md`. A documentation edit is not proof of executed behavior; traces, tests, replay evidence and frozen artifacts are proof.

When a `PROPOSE` rule receives replay `PASS`, treat it as promotion-eligible, not silently promoted. Change only the canonical rule owner, add/update regression and replay cases, run CI/static/contract tests, independently review the diff, and merge only while criteria remain satisfied. Mirrors never become control authority. A failed/HOLD replay must not alter durable executable policy.

System defects should be repaired at the unique owner: `detect → classify root cause → repair code/Skill/contract → add regression/replay → CI → independent review → promote`. Do not solve repeated execution failures by copying more prose into Notion/Drive or creating a second harness/Skill/rule surface.
