# A-share Event-Driven Agent

Use this Skill for A-share main-board premarket recommendation, post-close review, and continuation of an existing market-day task. Do not use it for publishable financial article writing; the Financial Writing Agent owns that workflow.

## Authority and cutover
Before choosing an execution plane, read `config/cutover_status.json` from GitHub `main`.

- GitHub `main`: canonical code/rule authority **and** Continuity governance authority.
- `config/cutover_status.json`: machine-readable cutover authority. It decides whether the owner Runtime checkpoint is additionally allowed to become executable market-day state authority.
- If `runtime_authority_enabled=true` and all promotion evidence remains valid: Runtime checkpoint is executable market-day state authority; GitHub `main` remains code/rule/Continuity authority.
- If `runtime_authority_enabled=false`: Runtime stays candidate/shadow. The operational governance checkpoint is the current GitHub `continuity/tasks/<task>/TASK_MANIFEST.json` + `HANDOFF.md`; these files may record governance stage, next action and evidence refs but must **not** impersonate an executed Runtime state transition.
- Notion/Google Drive: source, knowledge, artifact and migration-mirror inputs only unless a future explicit cutover contract says otherwise. They must not override GitHub task state, recovery pointers, QA/gate semantics or current next action.
- StockBase: recommendation reads; review is the only workflow allowed to record a writeback receipt.

Do not fall back from unavailable Runtime authority to a Notion/Drive controller. A missing Runtime capability blocks only the Runtime-dependent stage/gate; research/source/evidence work that is legal under GitHub governance may continue and must persist its authoritative governance receipt to GitHub continuity.

A documentation or cutover-file change is not proof that Runtime promotion gates passed. Runtime promotion still requires the evidence recorded in `config/cutover_status.json`.

## Execution readiness handshake
Before any material stage execution, read `continuity/EXECUTION_CAPABILITIES.json` from current GitHub `main` in addition to the cutover authority. This owner capability manifest defines the maximum assurance the repository can support; it is **not** proof that the current chat/session actually has the runtime, data source, connector, credential or modality needed now.

For the exact current stage / `next_action` only:
1. identify the required capability or capabilities;
2. observe current-session availability and assurance;
3. prefer the owner-native runtime/service when available;
4. use `CHAT_BRIDGED` only where the capability manifest explicitly lists it as a safe degraded mode, and submit the result through the owner stage/schema contract;
5. if a hard capability is unavailable, block that exact stage/gate rather than silently free-forming or declaring the whole Agent unusable;
6. never claim isolated execution unless distinct execution/context/trace evidence actually satisfies the required assurance.

A role description, Skill paragraph, code stub or configured tool name is not execution evidence. An owner-Runtime stage is complete only when the owner runtime/state/checkpoint contains the required result and evidence. Governance-only progress is complete only after the corresponding GitHub Continuity checkpoint is written and reread.

## New task vs continuation
Apply the global rule: **inherit learning, not unfinished work**.

- New market-day work does not inherit another task's stage, freeze hash, shortlist, blockers or next action.
- Explicit continuation may recover the matching USER task only.
- TEST / FIXTURE / EVAL / SYSTEM_INFRA tasks must not appear in ordinary bare-`继承` candidate discovery.
- Before resuming a persisted task, verify its contract/runtime version is compatible with the current Agent. Classify recovery as `COMPATIBLE`, `MIGRATABLE` or `INCOMPATIBLE`; do not faithfully restore obsolete execution semantics.

## Startup
Always recover through GitHub Continuity first:
1. Read the current matching USER `TASK_MANIFEST.json` + `HANDOFF.md` and `config/cutover_status.json`.
2. Resume a matching compatible market-day child before creating a duplicate.
3. Refresh the exact current Skill + `continuity/EXECUTION_CAPABILITIES.json` before material work.
4. If Runtime authority is enabled and session-proven, load/resume the owner Runtime checkpoint and bind its evidence back to GitHub Continuity.
5. If Runtime authority is disabled/unavailable, continue only the legal GitHub-governed research/source/evidence actions and block Runtime-only stage certification. Never route business control back to Notion/Drive.
6. Create/maintain FreezeCard boundaries before finalizing dynamic premarket data; never skip a gate.

## Premarket cognition
Read `references/sources.md`, `research.md`, `industry.md`, `market_structure.md`, `execution.md`, `audit.md` progressively as stages require.

Research is recall-first: build U0/U1 broadly, then role-rank U2 and narrow U3. Do not let Leader-First prune the research universe.

The research substrate is intended to evolve toward a shared A-share Intelligence Core: event/catalyst, concept/industry graph, detailed value-chain nodes, company mapping, operating/financial realization, market role/position, future events, counterevidence and provenance. Premarket and post-close may reuse this intelligence, but their executable state remains the market-day task lifecycle.

## Post-close
Continue the same FROZEN market-day task when the execution plane is authoritative and compatible. Read `references/review.md` and `learning.md`. Grade knowable recall against the immutable premarket snapshot. Never backfill post-close facts into FrozenPremarketDecision.

Learning proposals require replay before durable promotion. A single day creates a hypothesis, not a permanent rule.

## Recovery
Read `references/recovery.md` and `config/cutover_status.json`. Never rely on deleted chat history. Do not ask the user to repeat facts already durably persisted.

GitHub Continuity is the recovery entrypoint even while Runtime authority is disabled. If an executable Runtime checkpoint is unavailable, report the precise Runtime capability gap and continue only legal governance/research actions; do not reconstruct authority from chat memory or external mirrors.

## Maintenance and self-evolution
Read `references/maintenance.md`. A documentation edit is not proof of executed behavior; traces, tests, replay evidence and frozen artifacts are proof.

When a `PROPOSE` rule receives replay `PASS`, treat it as **promotion-eligible**, not silently promoted. Use the connected GitHub workflow to change only the canonical rule owner, add/update regression and replay cases, run CI/static/contract tests, independently review the diff, and merge only when the promotion criteria remain satisfied. Record/retain external mirror evidence only when useful; mirrors do not become control authority. A failed/HOLD replay must not alter durable executable policy.

System defects should be repaired at the unique owner: `detect → classify root cause → repair code/Skill/contract → add regression/replay → CI → independent review → promote`. Do not solve repeated execution failures by copying more prose into Notion/Drive.
