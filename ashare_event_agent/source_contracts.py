"""A-share source contracts and preferred acquisition metadata.

P01-P09 are the fixed research-source set. Market-data/business lanes are separate
because the owner of a quote/microstructure fact is not necessarily the owner of
an event/news fact. This module does not fetch live data: current-session source
capability must execute acquisition and bind returned evidence before a source is
claimed as observed.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceContract:
    source_id: str
    label: str
    preferred_methods: tuple[str, ...]
    stable_url: str | None = None
    completion_note: str = ""


@dataclass(frozen=True)
class MarketDataLane:
    lane_id: str
    label: str
    owns: tuple[str, ...]
    assurance_rule: str
    fallback_lanes: tuple[str, ...] = ()


SOURCE_CONTRACTS: dict[str, SourceContract] = {
    "P01": SourceContract("P01", "韭研公社内容精选 / LINK-ALL", ("STRUCTURED_API", "STATIC_HTTP", "WEB", "BROWSER"), completion_note="Expand every internal research link; directory-only is not FULL."),
    "P02": SourceContract("P02", "盘前纪要", ("STATIC_HTTP", "WEB", "BROWSER"), completion_note="Read body and every information-bearing image."),
    "P03": SourceContract("P03", "开盘必读资讯", ("STATIC_HTTP", "WEB", "BROWSER"), completion_note="Read body and every information-bearing image."),
    "P04": SourceContract("P04", "韭研公社时间轴", ("STRUCTURED_API", "EMBEDDED_JSON", "STATIC_HTTP", "BROWSER"), "https://www.jiuyangongshe.com/timeline", "Freeze event availability; future calendar items are not realized facts."),
    "P05": SourceContract("P05", "选股通早知道", ("STRUCTURED_API", "STATIC_HTTP", "WEB"), completion_note="PAID_LIMITED is legal; never fabricate hidden text."),
    "P06": SourceContract("P06", "脱水研报", ("STRUCTURED_API", "STATIC_HTTP", "WEB"), "https://xuangutong.com.cn/ts/home", "Read all public pre-freeze increments, not representative samples."),
    "P07": SourceContract("P07", "韭研产业库", ("STRUCTURED_API", "STATIC_HTTP", "EMBEDDED_JSON", "BROWSER"), "https://www.jiuyangongshe.com/industryChain", "Use new/hot nodes as discovery, then verify economics/company facts."),
    "P08": SourceContract("P08", "炒谷养娃2007最新增量", ("STATIC_HTTP", "WEB", "BROWSER"), "https://www.jiuyangongshe.com/u/df1e445526de466a93f1a0b16a204fe4", "Treat community claims as hypotheses until verified."),
    "P09": SourceContract("P09", "韭研公社首页 / 研究优选", ("STRUCTURED_API", "STATIC_HTTP", "EMBEDDED_JSON", "BROWSER"), "https://www.jiuyangongshe.com/study_publish", "Only pre-freeze posts may influence premarket ranking."),
}


MARKET_DATA_LANES: dict[str, MarketDataLane] = {
    "OFFICIAL_FACTS": MarketDataLane(
        "OFFICIAL_FACTS",
        "交易所/监管/公司一手事实",
        ("trading_calendar_boundary", "corporate_hard_event", "regulatory_policy_fact", "announcement_timing"),
        "Primary authority for hard official facts; market-data vendors may corroborate but not override a conflicting first-party disclosure.",
    ),
    "TONGHUASHUN_LEVEL2": MarketDataLane(
        "TONGHUASHUN_LEVEL2",
        "同花顺 / Level-2 市场与微观结构",
        ("quote_state", "auction_context", "depth_orderflow", "turnover_board_behavior", "buyability", "close_microstructure_review"),
        "Preferred lane when current-session access is proven. Level-2 evidence outranks weaker quote summaries for microstructure/buyability claims; absence must lower or block that assurance rather than be silently substituted.",
        ("STRUCTURED_MARKET_FALLBACK",),
    ),
    "XUANGUTONG_DINGPAN": MarketDataLane(
        "XUANGUTONG_DINGPAN",
        "选股通盯盘五池",
        ("limit_up", "limit_down", "limit_up_broken", "super_stock", "yesterday_limit_up"),
        "Canonical business lane for the five Dingpan pool definitions. Exact pool semantics, trading-date state and counts must reconcile before acceptance.",
    ),
    "STRUCTURED_MARKET_FALLBACK": MarketDataLane(
        "STRUCTURED_MARKET_FALLBACK",
        "结构化行情回退/交叉验证",
        ("trading_days", "quotes", "bars", "depth_flow", "industry_state", "financials", "news_crosscheck"),
        "Use a current-session structured provider such as Longbridge for fallback/corroboration. It does not redefine Xuangutong Dingpan pools or official hard facts.",
    ),
}


DINGPAN_POOL_SEMANTICS = ("limit_up", "limit_down", "limit_up_broken", "super_stock", "yesterday_limit_up")
RETRIEVAL_PRIORITY = ("STRUCTURED_API", "OFFICIAL", "STATIC_HTTP", "EMBEDDED_JSON", "DATABASE", "WEB", "BROWSER")
