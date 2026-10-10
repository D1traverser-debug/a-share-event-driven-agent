# A-share Continuity Task Index

Universal protocol target: v3.7  
Owner: `A_SHARE_MARKET_AGENT`  
Adapter: `continuity/UNIVERSAL_PROTOCOL_ADAPTER.json`

## Default USER candidates

- `ashare:recommendation` — **A股荐股** — USER — ACTIVE — stage `CURRENT_MARKET_DAY_ROUTED_TO_2026_10_12` — resume `DEFAULT` — manifest: `continuity/tasks/recommendation-workflow/TASK_MANIFEST.json` — checkpoint: `continuity/tasks/recommendation-workflow/HANDOFF.md`

## Non-default / current market day

- `ashare:2026-10-12` — **A股荐股｜2026-10-12** — USER — ACTIVE — stage `START_GATE_PERSISTED__WEEKEND_EVENT_LEDGER_PARTIAL__MONDAY_LIVE_SOURCE_WINDOW_PENDING` — resume `EXPLICIT_ONLY` — manifest: `continuity/tasks/2026-10-12-market-day/TASK_MANIFEST.json` — checkpoint: `continuity/tasks/2026-10-12-market-day/HANDOFF.md`

## Non-default / historical

- `ashare:2026-10-09` — historical market day — USER — PAUSED — resume `EXPLICIT_ONLY` — checkpoint `continuity/tasks/2026-10-09-market-day/HANDOFF.md`

## Rules

- 裸“继承”只能从 `Default USER candidates` 读取候选。
- “荐股 / A股荐股 / 开始荐股 / 继续荐股”恢复 `ashare:recommendation`，然后解析当前交易日并创建或定位当天 market-day USER task；若 parent 已有 `active_child_task_id`，先恢复该 child，禁止重复创建。
- 在任何 material market-day stage/next_action 执行前，读取当前 `skills/a-share-event-driven-agent/SKILL.md`、`config/cutover_status.json` 与 `continuity/EXECUTION_CAPABILITIES.json`，只对当前步骤所需能力做 session handshake；仓库代码存在不等于本聊天已具备实时数据/runtime binding。
- 历史 market-day task 不得因为恢复长期荐股入口而自动续跑，也不得把历史 FrozenDecision 带入新的交易日。
- Operational authority由 `config/cutover_status.json` 选择；当前 Universal Continuity 不得把候选 GitHub Runtime 静默提升为运营治理权威。
- No later outcome may be used to fabricate an earlier frozen decision.
- 旧聊天/旧 task manifest 的协议适配由系统自动处理，不要求用户迁移。长期入口已由本次新聊天 takeover 到 v3.7 lease，并路由至当前 market-day child；历史 PAUSED tasks 可在明确恢复时懒迁移。
- 活跃持久任务的每次最终答复必须输出 v3.7 `进度提交` 回执，并以实际 owner authority 回读作为 `COMMITTED` 证明。
