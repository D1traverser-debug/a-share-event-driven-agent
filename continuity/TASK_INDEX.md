# A-share Continuity Task Index

Contract: Universal Continuity v3.3  
Owner: `A_SHARE_MARKET_AGENT`

## Default USER candidates

- `ashare:recommendation` — **A股荐股** — USER — ACTIVE — stage `READY_FOR_CURRENT_MARKET_DAY` — resume `DEFAULT` — manifest: `continuity/tasks/recommendation-workflow/TASK_MANIFEST.json` — checkpoint: `continuity/tasks/recommendation-workflow/HANDOFF.md`

## Non-default / historical

- `ashare:2026-10-09` — historical market day — USER — PAUSED — resume `EXPLICIT_ONLY` — checkpoint `continuity/tasks/2026-10-09-market-day/HANDOFF.md`

## Rules

- 裸“继承”只能从 `Default USER candidates` 读取候选。
- “荐股 / A股荐股 / 开始荐股 / 继续荐股”恢复 `ashare:recommendation`，然后解析当前交易日并创建或定位当天 market-day USER task。
- 历史 market-day task 不得因为恢复长期荐股入口而自动续跑，也不得把历史 FrozenDecision 带入新的交易日。
- Operational authority remains selected by the repository cutover configuration.
- No later outcome may be used to fabricate an earlier frozen decision.
