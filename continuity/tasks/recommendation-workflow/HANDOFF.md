# A股荐股｜Continuity Handoff

- task_id: `ashare:recommendation`
- display_name_zh: **A股荐股**
- task_class: USER
- status: ACTIVE
- resume_visibility: DEFAULT
- owner: A_SHARE_MARKET_AGENT
- current_stage: READY_FOR_CURRENT_MARKET_DAY
- contract_version: CONTINUITY_V3_3

## Purpose
这是“荐股”长期 USER 工作入口，不代表任何历史交易日正在继续。

## Resume rule
- 用户说“继承：A股荐股 / 荐股 / 开始荐股 / 继续荐股”时恢复本入口。
- 恢复后先解析当前交易日，再创建或定位该交易日的 market-day USER task。
- 每个交易日的 FrozenDecision、盘前 snapshot、盘后 attribution 属于当日 child task；不得跨交易日继承。
- 历史 `ashare:2026-10-09` 继续保持 PAUSED / EXPLICIT_ONLY，不得因为恢复“荐股”而自动续跑。
- 盘后复盘只能读取对应盘前真实 FrozenDecision；不存在时必须记录为“无冻结决策”，禁止事后倒灌。

## Next action
恢复本入口后，读取 Market Agent 当前 authority/cutover 状态和最新市场日历，进入当天合法盘前推荐工作流。
