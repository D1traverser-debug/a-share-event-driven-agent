# Previous-Day ShortTermCard — 2026-10-09

> Evidence class: `GAP_FILL / RECONSTRUCTED_POST_CLOSE_INPUT`
>
> Purpose: provide the missing previous-trading-day market-state input for `ashare:2026-10-12`.
>
> Boundary: this is a post-close reconstruction created on 2026-10-10. It is **not** a 2026-10-09 premarket FrozenDecision and may not be used to rewrite what was knowable before that day's freeze line.

## 1. Market tape

- Shanghai Composite: **3813.79, +0.05%**.
- Shenzhen Component: **12641.86, +0.17%**.
- ChiNext: **3043.33, +0.22%**.
- The session was a high-volatility V-shaped recovery: ChiNext had been down more than 3% intraday before all three major indices recovered into positive closes.
- Shanghai/Shenzhen turnover was about **RMB 1.90tn**, roughly **RMB 218.4bn higher** than the previous trading day.
- Breadth was positive by the broad-market convention: more than 3,200 stocks advanced.

Primary public cross-checks used for this reconstructed card:
- 财联社 2026-10-09 daily close recap: `https://www.cls.cn/detail/2500549`
- 东方财富/界面 2026-10-09 close recap: `https://finance.eastmoney.com/a/202610093891573929.html`
- 证券时报 2026-10-09 limit-up review: `https://www.stcn.com/article/detail/4210270.html`
- 选股通板块异动/收评: `https://xuangutong.com.cn/subject/35?isshare=true`

## 2. Five-pool state — Xuangutong Dingpan semantics

Authoritative reconstructed membership artifact for this card:
`continuity/tasks/2026-10-12-market-day/evidence/PREVIOUS_DAY_FIVE_POOLS_GAP_FILL_2026-10-09.json`

- raw limit-up pool: **72**.
- non-ST limit-up count: **69**; the three ST names in the raw API are `*ST四通`, `ST万邦`, `*ST沐邦`.
- main-board non-ST limit-up count: **62**.
- limit-down pool: **11**.
- Dingpan broken-board pool: **13**.
- strong-stock pool: **33**.
- previous-day limit-up pool: **44**.
- using the Dingpan pool definition, 72 sealed + 13 broken = **85 touch-limit attempts**, giving an **84.71% seal rate / 15.29% broken rate**.

### Count reconciliation

The apparent `72 vs 69` conflict is resolved, not averaged:

- the direct Dingpan `limit_up` API contains **72** records;
- exactly **3** are ST records;
- excluding those three gives **69**, matching the common non-ST close-review convention.

Different providers use different definitions for “炸板/封板未遂”. The reconstructed five-pool input therefore keeps the **Dingpan pool value 13** as its own business object instead of overwriting it with another provider's touch-limit universe.

## 3. Short-term sentiment / continuation

The previous-day feedback pool was constructive but not indiscriminate:

- yesterday-limit-up pool size: **44**.
- **12** of those 44 closed at limit-up again on 2026-10-09.
- only **1** (`彩蝶实业`) moved from the previous-day limit-up pool to the 2026-10-09 limit-down pool.
- average 2026-10-09 return of the 44-name previous-day pool: **+2.606%**.
- breadth inside that pool: **27 positive / 17 negative**.

Interpretation: short-term carry-over was positive enough to support continuation trades, but dispersion remained material. This is not an “all high-board names are safe” regime.

## 4. HeightMap

Consecutive-board height at the close:

1. **新华传媒 — 9连板**.
2. **时代万恒 — 5连板**.
3. **九阳股份 — 5连板**.
4. **紫竹高科 — 4连板**.
5. Eight 2-board names: **三柏硕、楚环科技、安泰集团、丰元股份、红豆股份、雄韬股份、华北制药、领湃科技**.

There were **12 consecutive-board names** in total. Height is a fact only; it does not by itself establish leader/card-position status for 2026-10-12.

## 5. Theme structure

The session's strongest observable clusters were:

- **影视 / 传媒 / AI视频**: the clearest late-session expansion; multiple 10% and 20% limit-ups, with `新华传媒` also carrying the market's maximum height.
- **锂电池 / 电池材料**: a second structurally important branch, with `时代万恒` 5-board, `紫竹高科` 4-board, and several 2-board or first-board names.
- **农业 / 大消费**: broad lower-height diffusion, useful as rotation evidence rather than automatic leadership evidence.
- **网络安全 / AI安全**: `绿盟科技、麒麟信安、天融信、中新赛克、格尔软件` formed a visible cluster.
- **金融 / 贵金属**: smaller but identifiable strengthening via `华鑫股份、大智慧、西部黄金`.

Weak-side observations included **PCB / parts of electronics hardware** and **wind-power equipment**, with `金安国纪` and `大金重工` among the limit-down names.

## 6. Regime reading for the next trading day

This previous-day card should enter 2026-10-12 as **input**, not as a pre-selected recommendation list.

Working priors to test on Monday morning:

1. **High emotional repair + high intraday volatility**: Friday's V-reversal supports risk appetite, but the reversal itself raises the value of Monday confirmation rather than extrapolation.
2. **Media had breadth and height simultaneously**: that gives it stronger Friday structure than a one-stock theme, but the late-session acceleration also creates a Monday divergence/兑现 risk that must be tested with fresh catalysts, premarket source completion and same-height competition.
3. **Battery had the cleaner multi-height ladder**: 5-board / 4-board / 2-board / first-board coexistence is structurally useful, but Monday must distinguish continuation from crowded carry-over.
4. **Previous-day winners retained positive expectancy in aggregate**: 12 re-limit names and +2.606% average return support continuation as a live hypothesis, not a guarantee.
5. **Weak hardware/wind branches are negative evidence**: a Monday candidate that depends on Friday's weak branch needs a genuinely new catalyst or clear reversal evidence rather than narrative carry-over.

## 7. What this card does not authorize

- It does not rank 2026-10-12 U2/U3 roles.
- It does not select buy candidates.
- It does not replace Monday P01-P09 Source Completion, event ledger, StockBase recall, universe audit, Market Regime/RoleMap or MID/FINAL QA.
- It does not authorize any StockBase write.
- It does not prove Hosted Runtime execution or FROZEN state.

## 8. Quality / provenance notes

- An LLM-structured extraction attempt on one endpoint falsely reported `limit_down exact_count=30` while outputting only 11 rows. It was rejected.
- Accepted five-pool counts and membership were obtained by direct JSON reads and mechanical `len(data[])` execution in the connected remote environment.
- Public close recaps were used as cross-checks for index/turnover/sector context and definition reconciliation, not to overwrite Dingpan's five-pool semantics.
