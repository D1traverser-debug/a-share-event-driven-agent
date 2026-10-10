# Source completion

P01-P09 are fixed source contracts. Direct API / official / structured market-data / static HTTP / embedded JSON / database paths outrank generic browsing. Browser automation is a last resort, not the default acquisition layer.

## Retrieval hierarchy

Use the narrowest auditable source that actually owns the fact:

1. **Primary official facts** — SSE/SZSE, CSRC, ministries/commissions, listed-company announcements and other first-party disclosures.
2. **Direct structured domain endpoints** — stable JSON/API endpoints that expose the exact business object needed.
3. **Session-proven structured market-data connector** — for trading calendar, quotes, OHLCV, market/industry state, capital-flow, depth, financials, news and anomaly cross-checks when the connector is actually available in the current session.
4. **Static HTTP / embedded JSON / database**.
5. **Web search/extraction** for discovery, corroboration and public pages that lack a better direct path.
6. **Browser interaction** only for login-gated, JS-only, interaction-only or image-bearing information that cannot be recovered through a better path.

A configured connector/app name is not evidence that it ran. Material source completion requires a current-session receipt or returned data.

## Current preferred application lanes

These are role assignments, not exclusive vendor lock-in:

- **Longbridge (when session-proven)**: preferred structured A-share market-data lane for CN trading days, quotes, historical bars, market temperature, industry ranking, anomaly/top-mover cross-checks, depth, capital flow/distribution, financials, calendars and stock/news retrieval. It is a market-data source, not the canonical definition of the five Dingpan pools.
- **选股通 / Xuangutong direct API**: preferred direct lane for the five Dingpan pools when a formal prior-review snapshot is missing and a provenance-labeled reconstruction is legally required. Pool semantics must be preserved exactly (`limit_up`, `limit_down`, `limit_up_broken`, `super_stock`, `yesterday_limit_up`) and counts must be reconciled against page/date state before acceptance.
- **Official exchange/regulator/company sources**: primary-verification lane for trading calendar boundaries, corporate hard events, regulatory/policy facts and announcement timing.
- **Native web search / token-efficient search-extraction connectors such as Parallel Search when available**: discovery and corroboration lane for public research/news pages.
- **Opera Browser Connector or another current-session browser connector**: last-resort authenticated/JS/image lane. Use only when direct/structured/static retrieval cannot satisfy the source contract.
- **Metered crawlers/extractors such as Firecrawl**: optional fallback for difficult extraction/crawl tasks; do not make a metered service a hard dependency when a direct or already-connected path exists.
- **Alpha Vantage (when useful)**: global macro/news/commodity/cross-market corroboration lane; not the default source for A-share microstructure or Dingpan pool definitions.

Task-local user constraints may disable a particular browser/extractor/app. Persist that constraint in the active task rather than silently changing the global source hierarchy.

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

For source conflicts, preserve both observations until the definitions are reconciled. Never choose the numerically convenient value and call the discrepancy solved.
