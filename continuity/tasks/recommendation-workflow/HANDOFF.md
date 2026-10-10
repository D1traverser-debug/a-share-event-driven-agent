# A股荐股｜Continuity Handoff

- task_id: `ashare:recommendation`
- display_name_zh: **A股荐股**
- task_class: USER
- status: ACTIVE
- resume_visibility: DEFAULT
- owner: A_SHARE_MARKET_AGENT
- current_stage: `CURRENT_MARKET_DAY_ROUTED_TO_2026_10_12`
- contract_version: `CONTINUITY_V3_7`
- continuity_protocol_version: `3.7`
- resume_epoch: `1`
- active_child_task_id: `ashare:2026-10-12`
- active_child_manifest: `continuity/tasks/2026-10-12-market-day/TASK_MANIFEST.json`
- active_child_checkpoint: `continuity/tasks/2026-10-12-market-day/HANDOFF.md`

## Purpose
这是“荐股”长期 USER 工作入口，不代表任何历史交易日正在继续。当前长期入口已在本次新聊天 takeover 后路由到 2026-10-12 market-day child；下次恢复优先继续该 child，禁止重复创建同一交易日任务。

## Current route
- 2026-10-10 为周六休市；下一交易日为 2026-10-12。
- 当前 child `ashare:2026-10-12` 已完成 START Gate 初始化，Notion/Drive shadow-governance DailyRun/FreezeCard 已建立并回读验证。
- 当前 StockBase 指针为 v1.6，荐股权限 READ ONLY。
- 2026-10-09 正式复盘/五池资产在当前 `30_RUNTIME` 与定向检索中未定位到，child 已标记 BOUNDARY；不得静默视为存在，也不得构造历史 FrozenDecision。
- Weekend Event Ledger 已开始，但 Monday P01-P09 / live-source completion 尚处未来时间窗，因此 child 不得标 FROZEN/FINAL。

## Resume rule
- 用户说“继承：A股荐股 / 荐股 / 开始荐股 / 继续荐股”时恢复本入口，然后读取 `active_child_task_id`；若当前交易日与该 child 仍匹配，则直接恢复 child，不重新创建。
- 每个交易日的 FrozenDecision、盘前 snapshot、盘后 attribution 属于当日 child task；不得跨交易日继承。
- 历史 `ashare:2026-10-09` 继续保持 PAUSED / EXPLICIT_ONLY，不得因为恢复“荐股”而自动续跑。
- 盘后复盘只能读取对应盘前真实 FrozenDecision；不存在时必须记录为“无冻结决策”，禁止事后倒灌。
- Operational authority 继续由 `config/cutover_status.json` 选择；当前仍为 Notion/Drive existing governance，GitHub Runtime 仅 candidate shadow。

## Next action
继续 `ashare:2026-10-12`：先解决上一交易日五池/ShortTermCard 输入缺口并深化周末事件研究；进入 2026-10-12 盘前窗口后完成 P01-P09、官方/实时源、图片、StockBase Recall、完整 Universe、数量对账及 START/MID/FINAL QA。只有全部硬门禁通过后才允许 FROZEN/FINAL，否则保持 WORKING 或 NO TRADE。
