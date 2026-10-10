# A股荐股｜Continuity Handoff

- task_id: `ashare:recommendation`
- display_name_zh: **A股荐股**
- task_class: USER
- status: ACTIVE
- resume_visibility: DEFAULT
- owner: A_SHARE_MARKET_AGENT
- current_stage: `CURRENT_MARKET_DAY_ROUTED_TO_2026_10_12__GITHUB_GOVERNANCE`
- contract_version: `CONTINUITY_V3_7_GITHUB_GOVERNANCE`
- continuity_protocol_version: `3.7`
- resume_epoch: `1`
- active_child_task_id: `ashare:2026-10-12`
- active_child_manifest: `continuity/tasks/2026-10-12-market-day/TASK_MANIFEST.json`
- active_child_checkpoint: `continuity/tasks/2026-10-12-market-day/HANDOFF.md`

## Purpose
这是“荐股”长期 USER 工作入口，不代表任何历史交易日正在继续。当前长期入口已在本次新聊天 takeover 后路由到 2026-10-12 market-day child；下次恢复优先继续该 child，禁止重复创建同一交易日任务。

## Current route
- 2026-10-10 为周六休市；Longbridge CN 交易日接口已在本次会话实测确认下一交易日为 2026-10-12。
- 当前 child `ashare:2026-10-12` 已完成 START Gate 初始化，并已完成控制面迁移：GitHub `main` + child Continuity checkpoint 现在是治理权威。
- 原 Notion/Drive DailyRun/FreezeCard 仅保留为 source/artifact migration mirror，不再控制 stage / next_action / QA / recovery。
- Hosted Runtime 仍为 candidate shadow，`runtime_authority_enabled=false`；这只阻塞 Runtime-dependent certification，不允许回退到 Notion/Drive 控制面。
- 当前 StockBase 指针为 v1.6，荐股权限 READ ONLY。
- 2026-10-09 正式复盘/五池资产在旧运行面未定位到，child 已授权按 owner 新规则做 provenance-labeled GAP_FILL；不得静默视为历史正式 snapshot，也不得构造历史 FrozenDecision。
- Weekend Event Ledger 已开始，但 Monday P01-P09 / live-source completion 尚处未来时间窗，因此 child 不得标 FROZEN/FINAL。
- 当前 child task-local 约束：TinyFish 不使用。

## Resume rule
- 用户说“继承：A股荐股 / 荐股 / 开始荐股 / 继续荐股”时恢复本入口，然后读取 `active_child_task_id`；若当前交易日与该 child 仍匹配，则直接恢复 child，不重新创建。
- 每个交易日的 FrozenDecision、盘前 snapshot、盘后 attribution 属于当日 child task；不得跨交易日继承。
- 历史 `ashare:2026-10-09` 继续保持 PAUSED / EXPLICIT_ONLY，不得因为恢复“荐股”而自动续跑。
- 盘后复盘只能读取对应盘前真实 FrozenDecision；不存在时必须记录为“无冻结决策”，禁止事后倒灌。
- GitHub Continuity 是恢复入口和治理 checkpoint；Runtime 只有在 promotion gate 通过后才可成为 executable market-day checkpoint authority。
- Notion/Drive 只可作为 source/knowledge/artifact/migration mirror，不能覆盖当前 GitHub task state。

## Current tool routing
- 五池：优先选股通/Xuangutong direct pool API，保持五池原始定义。
- A股交易日/行情/OHLCV/异动/行业/资金/财务/新闻交叉校验：Longbridge，当前会话已实测可用。
- 官方事实：交易所、监管部门、公司公告等第一方来源。
- 公共网页发现/补证：native web / token-efficient search-extraction。
- 登录/JS/图片：Opera Browser Connector 最后兜底。
- Firecrawl：低额度、非主路径。
- Alpha Vantage：全球宏观/新闻/跨市场补证，不做 A股五池定义源。
- TinyFish：当前 child 明确禁用。

## Next action
继续 `ashare:2026-10-12`：
1. 先在 GitHub governance 下补齐 2026-10-09 五池 + ShortTermCard/review 输入，明确标 `GAP_FILL / RECONSTRUCTED_POST_CLOSE_INPUT`，完成日期语义和数量口径对账；
2. 深化周末事件研究与 StockBase READ ONLY recall；
3. 进入 2026-10-12 盘前窗口后完成 P01-P09、官方/实时源、图片、StockBase Recall、完整 Universe、数量对账及 START/MID/FINAL QA；
4. 只有全部硬门禁通过后才允许 FROZEN/FINAL，否则保持 WORKING 或 NO TRADE。
