# A-share Event-Driven Agent

Use this Skill for A-share main-board premarket recommendation, post-close review, and continuation of an existing market-day runtime. Do not use it for publishable financial article writing; the Financial Writing Agent owns that workflow.

## Authority
- Runtime checkpoint: executable market-day state authority.
- GitHub `main`: executable code/rule authority.
- Notion/Drive: governance, knowledge and source mirrors.
- StockBase: recommendation reads; review is the only workflow that may record a writeback receipt.

## Startup
1. List recent incomplete market-day tasks.
2. Resume a matching task before creating a duplicate.
3. For a new trading day start runtime before research.
4. Create FreezeCard before finalizing dynamic premarket data.
5. Follow returned `next_action`; never skip a gate.

## Premarket cognition
Read `references/sources.md`, `research.md`, `industry.md`, `market_structure.md`, `execution.md`, `audit.md` progressively as stages require.

Research is recall-first: build U0/U1 broadly, then role-rank U2 and narrow U3. Do not let Leader-First prune the research universe.

## Post-close
Continue the same FROZEN task. Read `references/review.md` and `learning.md`. Grade knowable recall against the immutable premarket snapshot. Learning proposals require replay before durable promotion.

## Recovery
Read `references/recovery.md`. Never rely on deleted chat history. If the Runtime checkpoint is unavailable, state that execution recovery is not proven; do not pretend memory reconstructed it.

## Maintenance and self-evolution
Read `references/maintenance.md`. A documentation edit is not proof of executed behavior; traces, tests, replay evidence and frozen artifacts are proof.

When a `PROPOSE` rule receives replay `PASS`, treat it as **promotion-eligible**, not silently promoted. Use the connected GitHub workflow to change only the canonical rule owner, add/update regression and replay cases, run CI/static/contract tests, independently review the diff, and merge only when the promotion criteria remain satisfied. Record/retain the PR/commit evidence in governance mirrors when available. A failed/HOLD replay must not alter durable executable policy.
