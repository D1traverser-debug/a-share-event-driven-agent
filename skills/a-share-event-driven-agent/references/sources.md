# Source completion

P01-P09 are fixed research-source contracts. Market-data/business lanes are separate because quote/microstructure truth, official hard facts and research/news discovery have different owners. Direct API / official / structured market-data / static HTTP / embedded JSON / database paths outrank generic browsing. Browser automation is a last resort, not the default acquisition layer.

## Fact-owner hierarchy

Use the narrowest auditable source that actually owns the fact:

1. **Primary official facts** — SSE/SZSE, CSRC, ministries/commissions, listed-company announcements and other first-party disclosures own hard corporate/regulatory facts and announcement timing.
2. **Direct structured domain endpoints** — stable JSON/API endpoints that expose the exact business object needed.
3. **Session-proven market-data lane** — quotes, OHLCV, auction/depth/order-flow, market/industry state, capital-flow and execution/buyability evidence when the lane actually ran in the current session.
4. **Static HTTP / embedded JSON / database**.
5. **Web search/extraction** for discovery, corroboration and public pages that lack a better direct path.
6. **Browser interaction** only for login-gated, JS-only, interaction-only or image-bearing information that cannot be recovered through a better path.

A configured connector/app name is not evidence that it ran. Material source completion requires a current-session receipt or returned data.

## A-share preferred business lanes

These are business-role assignments, not universal vendor truth or exclusive lock-in:

- **同花顺 / Level-2 (when current-session proven)**: preferred A-share market-state/microstructure lane for quotes, auction context, depth/order-flow, turnover/board behavior, buyability and post-close microstructure review. For a claim that materially depends on depth/order-flow, Level-2 evidence outranks a weaker quote summary. If the preferred capability is unavailable, explicitly degrade/block that claim; do not silently substitute weaker data and keep the same assurance.
- **选股通 / Xuangutong Dingpan**: canonical business lane for the five Dingpan pools: `limit_up`, `limit_down`, `limit_up_broken`, `super_stock`, `yesterday_limit_up`. Pool definition, count and target trading date must reconcile before acceptance. Premarket normally reuses the previous formal review snapshot instead of re-fetching it.
- **Official exchange/regulator/company sources**: primary-verification lane for trading-calendar boundaries, corporate hard events, regulatory/policy facts and announcement timing. A conflicting market-data vendor cannot override a verified first-party disclosure merely because its timestamp is newer.
- **Longbridge or another current-session structured market-data connector**: fallback/corroboration lane for CN trading days, quotes, bars, market/industry state, anomaly/top-mover cross-checks, depth/flow, financials, calendars and stock/news retrieval. It does not redefine the five Dingpan pools and does not replace official hard facts.
- **P01-P09 research sources**: event/news/industry discovery and breadth. They can generate hypotheses, but hard claims must be verified by the appropriate fact owner where one exists.
- **Native web search / search-extraction connectors**: discovery/corroboration for public research and news pages.
- **Authenticated browser or metered extraction**: last-resort acquisition when a better direct/structured/static path cannot satisfy the contract.
- **Global data/news providers**: macro/commodity/cross-market corroboration only; not the default authority for A-share microstructure or Dingpan pool definitions.

Task-local user constraints may disable a particular app/source. Persist that constraint in the active child market-day run rather than silently changing the global source hierarchy.

## Five-pool rule

Premarket normally reuses the **previous formal review five-pool snapshot** and must not re-fetch those pools merely for convenience.

If that formal snapshot is genuinely missing, a later reconstruction is allowed only as an explicitly labeled **GAP_FILL / RECONSTRUCTED_POST_CLOSE_INPUT** with:
- exact source and endpoint/page identity;
- acquisition timestamp;
- target trading date and evidence that the returned pool state corresponds to that date;
- exact pool definition and count;
- per-stock records needed by review/recommendation;
- count reconciliation and any unresolved discrepancy;
- a statement that the reconstruction is **not** a historical premarket FrozenDecision.

A weekend/current page may reflect the last trading day's pool state, but this must be verified from page/API timestamps/date semantics before it is promoted into business evidence.

## P01-P09 completeness and point-in-time proof

Every source receipt records status, references, retrieval method, timestamps, LINK-ALL counts, image counts, gaps and `content_max_available_at` — the latest **knowledge-availability time** of any item actually admitted from that source.

`FULL` is not a prose judgment. It requires explicit `links_expected == links_fetched` and `images_expected == images_read`; use zero when the source contains no links/images. `FULL` also requires `content_max_available_at`. A source with unknown completeness must use a bounded non-FULL status and explicit gaps rather than guessing zero.

For premarket use, every non-blocked receipt is checked against the current FreezeCard. `content_max_available_at` and any source `published_at` used as a knowledge timestamp must be no later than the freeze boundary. Retrieval may occur later; late retrieval does not authorize late content.

`available_at` means **when the market could know the fact**, not when a future scheduled event will occur. Calendar occurrence time and information-availability time are separate concepts; a calendar fact first learned after freeze may not influence the frozen premarket decision.

Image-only tables, calendars, leaderboards, seats, and timelines are first-class source data. A text scraper that misses a material image does not satisfy FULL.

For source conflicts, preserve both observations until definitions and time semantics are reconciled. Never choose the numerically convenient value and call the discrepancy solved.
