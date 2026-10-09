# A-share Event-Driven Agent

Use this Skill for A-share main-board premarket recommendation, post-close review, and continuation of an existing market-day task. Do not use it for publishable financial article writing; the Financial Writing Agent owns that workflow.

## Authority and cutover
Before choosing an execution plane, read `config/cutover_status.json` from GitHub `main`.

- GitHub `main`: executable code/rule authority for the candidate Agent.
- `config/cutover_status.json`: machine-readable cutover authority. It decides whether the Runtime checkpoint is allowed to be the operational execution authority.
- If `runtime_authority_enabled=true` and all promotion evidence remains valid: Runtime checkpoint is executable market-day state authority.
- If `runtime_authority_enabled=false`: the Agent is still in shadow/candidate validation. Do **not** silently promote Runtime state over the current operational governance plane merely because Runtime tools exist.
- Notion/Drive: governance, knowledge, source and migration mirrors according to the current cutover status; they are not code/rule owners.
- StockBase: recommendation reads; review is the only workflow that may record a writeback receipt.

A change to documentation or to the cutover flag is not proof of production readiness. Promotion requires the evidence gates recorded in `config/cutover_status.json`.

## New task vs continuation
Apply the global rule: **inherit learning, not unfinished work**.

- New market-day work does not inherit another task's stage, freeze hash, shortlist, blockers or next action.
- Explicit continuation may recover the matching USER task only.
- TEST / FIXTURE / EVAL / SYSTEM_INFRA tasks must not appear in ordinary bare-`继承` candidate discovery.
- Before resuming a persisted task, verify its contract/runtime version is compatible with the current Agent. Classify recovery as `COMPATIBLE`, `MIGRATABLE` or `INCOMPATIBLE`; do not faithfully restore obsolete execution semantics.

## Startup
When cutover status permits Runtime authority:
1. List recent incomplete **USER** market-day tasks only.
2. Resume a matching compatible task before creating a duplicate.
3. For a genuinely new trading day start runtime before research.
4. Create FreezeCard before finalizing dynamic premarket data.
5. Follow returned `next_action`; never skip a gate.

When cutover status does not yet permit Runtime authority, operate under the current shadow-validation/governance path and use Runtime only as a candidate plane whose outputs are compared, not silently promoted.

## Premarket cognition
Read `references/sources.md`, `research.md`, `industry.md`, `market_structure.md`, `execution.md`, `audit.md` progressively as stages require.

Research is recall-first: build U0/U1 broadly, then role-rank U2 and narrow U3. Do not let Leader-First prune the research universe.

The research substrate is intended to evolve toward a shared A-share Intelligence Core: event/catalyst, concept/industry graph, detailed value-chain nodes, company mapping, operating/financial realization, market role/position, future events, counterevidence and provenance. Premarket and post-close may reuse this intelligence, but their executable state remains the market-day task lifecycle.

## Post-close
Continue the same FROZEN market-day task when the execution plane is authoritative and compatible. Read `references/review.md` and `learning.md`. Grade knowable recall against the immutable premarket snapshot. Never backfill post-close facts into FrozenPremarketDecision.

Learning proposals require replay before durable promotion. A single day creates a hypothesis, not a permanent rule.

## Recovery
Read `references/recovery.md` and `config/cutover_status.json`. Never rely on deleted chat history. Do not ask the user to repeat facts already durably persisted.

If authoritative task recovery is unavailable or cutover is not proven, say so in system state; do not pretend chat memory reconstructed an executable checkpoint.

## Maintenance and self-evolution
Read `references/maintenance.md`. A documentation edit is not proof of executed behavior; traces, tests, replay evidence and frozen artifacts are proof.

When a `PROPOSE` rule receives replay `PASS`, treat it as **promotion-eligible**, not silently promoted. Use the connected GitHub workflow to change only the canonical rule owner, add/update regression and replay cases, run CI/static/contract tests, independently review the diff, and merge only when the promotion criteria remain satisfied. Record/retain the PR/commit evidence in governance mirrors when available. A failed/HOLD replay must not alter durable executable policy.

System defects should be repaired at the unique owner: `detect → classify root cause → repair code/Skill/contract → add regression/replay → CI → independent review → promote`. Do not solve repeated execution failures by copying more prose into Notion/Drive.
