# A-share Market Day 2026-10-12 Continuity Handoff

- task_id: `ashare:2026-10-12`
- parent_task_id: `ashare:recommendation`
- task_class: USER
- status: ACTIVE
- resume_visibility: EXPLICIT_ONLY
- owner: A_SHARE_MARKET_AGENT
- current_stage: `GITHUB_CONTROL_PLANE_MIGRATED__START_GATE_PERSISTED__WEEKEND_EVENT_LEDGER_PARTIAL__MONDAY_LIVE_SOURCE_WINDOW_PENDING`
- operational governance authority: `GITHUB_MAIN_CONTINUITY`
- GitHub Runtime: candidate shadow only; `runtime_authority_enabled=false`
- legacy Drive run: retained only as source/artifact migration mirror; it may not override GitHub task state
- task-local constraint: **TinyFish disabled for this task by explicit user instruction**

## Authority migration result

A 2026-10-10 control-plane audit found that the repository architecture had already moved code/rules/recovery metadata to GitHub but still routed business control back to Notion/Drive whenever Runtime authority was disabled. That split was repaired.

Current authority split:
1. GitHub `main` owns code/rules and Continuity governance state.
2. This `TASK_MANIFEST.json` + `HANDOFF.md` own current governance stage / next action / evidence refs while Runtime authority is disabled.
3. Hosted Runtime may become executable market-day checkpoint authority only after its durability/replay/live-E2E promotion gates pass.
4. Notion/Drive are source/knowledge/artifact/migration mirrors only.
5. StockBase remains READ ONLY for recommendation; review writeback remains receipt-gated.

The previous Drive object remains referenced for provenance:
- folder_id: `1r9Z8ucYtkJ4f6W60ZScqu3GeBZodSQHC`
- document_id: `11bcuTt6OdJc2nXG2QFPNWtFD5A5iUs_VnAMaQy2CFI8`
- previous path: `30_RUNTIME_运行现场/2026-10-12/PICK_RUN_2026-10-12_盘前荐股状态`
- role now: `SOURCE_ARTIFACT_MIGRATION_MIRROR_ONLY`

## TaskContract / START Gate

- task_type: PREMARKET_RECOMMENDATION
- trade_date: 2026-10-12 (Monday)
- initialization_time: 2026-10-10 23:05:53 Asia/Shanghai
- freeze target: public information no later than 2026-10-12 09:14:59 Asia/Shanghai
- auction_used: false
- active recommendation universe: Shanghai/Shenzhen main board, excluding ST/*ST/delisting and hard-risk names; non-main-board names may remain research/market anchors only.
- StockBase permission: READ ONLY. Current pointer verified at v1.6 / file_id `1arMm13WlnOs_v1mo8DagXCsjsYyVkRGc`.
- historical isolation: do not inherit the 2026-10-09 FrozenDecision or fabricate one from later outcomes.

## Source / application routing after evolution audit

The owner source authority is now explicit about tool roles:

1. **Official exchanges/regulators/company disclosures** — primary verification for policy, corporate hard events, announcement timing and trading-calendar facts.
2. **Xuangutong direct pool API** — exact five-pool semantics when the missing 2026-10-09 review snapshot must be reconstructed as GAP_FILL: `limit_up`, `limit_down`, `limit_up_broken`, `super_stock`, `yesterday_limit_up`.
3. **Longbridge** — current-session structured A-share market-data lane. Session proof obtained on 2026-10-10: CN trading calendar returned 2026-10-08/09/12/13 correctly and historical 2026-10-09 CN top-mover data returned successfully. Use for market/calendar/quotes/OHLCV/industry/capital/depth/financial/news cross-checks, not to redefine Dingpan pool semantics.
4. **Native web / token-efficient public search-extraction** — discovery and corroboration.
5. **Opera Browser Connector** — login/JS/image last resort only.
6. **Firecrawl** — metered extraction fallback only; current account signaled low credits, therefore not a primary dependency.
7. **Alpha Vantage** — optional global macro/news/cross-market corroboration, not A-share five-pool authority.
8. **TinyFish** — not allowed for this active task.

## CoverageMatrix

- trading-day resolution: PASS — Longbridge CN calendar session-proven; 2026-10-10 is weekend closure and 2026-10-12 is next trading day.
- current owner Skill / cutover / capability contract: PASS — GitHub governance migration applied.
- current GitHub START Gate / task checkpoint: PASS.
- legacy Drive START Gate: retained only as historical/source mirror; not task authority.
- current StockBase pointer: PASS — v1.6, read-only for PICK.
- prior trading-day saved five-pool / ShortTermCard inputs: BOUNDARY — no formal 2026-10-09 review/five-pool asset located in the previous Drive runtime surface. Owner rule now allows provenance-labeled reconstruction only when the formal snapshot is genuinely missing.
- 2026-10-12 FreezeCard boundary: INITIALIZED / NOT_FROZEN.
- weekend pre-research Event Ledger: PARTIAL.
- prior-day count reconciliation: PENDING — the earlier `72 vs 69` issue is now treated as a definition mismatch to reconcile, not two competing truths. The direct Dingpan pool itself exposed 69 indexed limit-up rows in the page state observed on 2026-10-10; any broader 72 figure must be mapped to its own definition before use.
- P01-P09 Source Completion including required images: BOUNDARY — Monday premarket publications are not yet fully available during weekend initialization.
- all-news Event Ledger / Omission Scan: IN_PROGRESS / PARTIAL.
- Market Regime / HeightMap / RoleMap: NOT_STARTED.
- Deep Industry / U0 all-event mapping: NOT_STARTED.
- U1 knowable potential-limit-up pool: NOT_STARTED.
- U2 role-ranked pool: NOT_STARTED.
- U3 execution shortlist / NO TRADE decision: NOT_STARTED.
- MID QA: NOT_STARTED.
- FINAL Red-Team QA: NOT_STARTED.

## Weekend pre-research ledger persisted

High-priority items currently include: the top-level policy on developing new quality productive forces; CSRC public-fund operation-rule consultation and capital-market policy signal; MIIT manufacturing-digitalization centers; multi-department automobile innovation/testing governance consultation; NDRC private-enterprise symposium; and a company-hard-event candidate bucket requiring primary-announcement and materiality verification. These are preliminary evidence items, not stock recommendations.

## Session capability handshake

- GitHub Continuity governance: PASS / current-session writer.
- owner-native Runtime state machine: not session-proven and not promoted to executable authority; Runtime-only stage certification remains blocked.
- Longbridge structured CN market data: PASS / live session evidence exists.
- Xuangutong direct five-pool endpoints: endpoint discovery PASS; historical-date/page-state verification still required before reconstructing 2026-10-09 business evidence.
- browser fallback: Opera available; last resort only.
- metered crawler: Firecrawl available but low credits; non-primary.
- Monday live premarket source completion: temporally incomplete because target publication window is still in the future.

## Next exact action

1. Reconstruct the missing 2026-10-09 five pools and ShortTermCard/review input under GitHub governance, strictly as `GAP_FILL / RECONSTRUCTED_POST_CLOSE_INPUT`:
   - fetch exact Xuangutong pool objects directly;
   - prove the weekend/current page state corresponds to 2026-10-09, the last trading day;
   - capture all five pool counts and per-stock records needed for review;
   - reconcile count definitions and preserve unresolved boundaries;
   - use Longbridge/official market data only as cross-checks, not as pool-definition substitutes;
   - never fabricate a historical premarket FrozenDecision.
2. Use current StockBase read-only as needed for weekend event recall, primary-verify company hard events and deepen the policy/event branches.
3. During the 2026-10-12 premarket window refresh P01-P09 plus required official/live sources and images, merge/dedupe against the weekend ledger, and run Source Completion/Omission/Counterexample/Time scans.
4. Only after Market Regime, HeightMap/RoleMap, Deep Industry, U0/U1/U2/U3, count reconciliation and MID/FINAL QA pass may the task advance toward FROZEN/FINAL. Missing Runtime authority blocks only the Runtime-dependent certification step, not legal GitHub-governed research/evidence work.
