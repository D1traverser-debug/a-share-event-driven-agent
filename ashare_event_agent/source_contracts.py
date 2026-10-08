from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceContract:
    source_id: str
    label: str
    preferred_methods: tuple[str, ...]
    stable_url: str | None = None
    completion_note: str = ""


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

RETRIEVAL_PRIORITY = ("STRUCTURED_API", "OFFICIAL", "STATIC_HTTP", "EMBEDDED_JSON", "DATABASE", "WEB", "BROWSER")
