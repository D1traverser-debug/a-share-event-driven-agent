from __future__ import annotations

from datetime import datetime, time
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


def _require_aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


class FreezeCard(StrictModel):
    trading_date: str
    timezone: str = "Asia/Shanghai"
    max_public_info_time: datetime
    max_market_data_time: datetime
    auction_used: bool = False
    post_freeze_data_allowed_for_premarket: bool = False

    @model_validator(mode="after")
    def guard_future_use(self):
        if self.post_freeze_data_allowed_for_premarket:
            raise ValueError("premarket research may never use post-freeze data")
        _require_aware(self.max_public_info_time, "max_public_info_time")
        _require_aware(self.max_market_data_time, "max_market_data_time")
        try:
            zone = ZoneInfo(self.timezone)
            trade_date = datetime.strptime(self.trading_date, "%Y-%m-%d").date()
        except Exception as exc:
            raise ValueError("FreezeCard requires a valid IANA timezone and YYYY-MM-DD trading_date") from exc
        public_local = self.max_public_info_time.astimezone(zone)
        market_local = self.max_market_data_time.astimezone(zone)
        if public_local.date() != trade_date or market_local.date() != trade_date:
            raise ValueError("FreezeCard cutoffs must belong to the trading date in the configured timezone")
        cutoff_clock = time(9, 24, 59) if self.auction_used else time(9, 14, 59)
        cutoff = datetime.combine(trade_date, cutoff_clock, tzinfo=zone)
        if public_local > cutoff or market_local > cutoff:
            raise ValueError(f"premarket cutoff exceeds legal freeze boundary {cutoff.isoformat()}")
        return self


SourceStatus = Literal["FULL", "PARTIAL", "PAID_LIMITED", "LOGIN_LIMITED", "BLOCKED"]
RetrievalMethod = Literal["STRUCTURED_API", "OFFICIAL", "STATIC_HTTP", "EMBEDDED_JSON", "DATABASE", "WEB", "BROWSER"]


class SourceReceipt(StrictModel):
    source_id: str
    label: str
    status: SourceStatus
    retrieval_method: RetrievalMethod
    retrieved_at: datetime
    source_refs: list[str] = Field(min_length=1)
    published_at: datetime | None = None
    content_max_available_at: datetime | None = None
    links_expected: int | None = Field(default=None, ge=0)
    links_fetched: int | None = Field(default=None, ge=0)
    images_expected: int | None = Field(default=None, ge=0)
    images_read: int | None = Field(default=None, ge=0)
    gaps: list[str] = Field(default_factory=list)
    notes: str = ""

    @model_validator(mode="after")
    def counts_reconcile(self):
        _require_aware(self.retrieved_at, "retrieved_at")
        if self.published_at is not None:
            _require_aware(self.published_at, "published_at")
        if self.content_max_available_at is not None:
            _require_aware(self.content_max_available_at, "content_max_available_at")
        if self.links_expected is not None and self.links_fetched is not None and self.links_fetched > self.links_expected:
            raise ValueError("links_fetched cannot exceed links_expected")
        if self.images_expected is not None and self.images_read is not None and self.images_read > self.images_expected:
            raise ValueError("images_read cannot exceed images_expected")
        if self.status == "FULL":
            if None in {self.links_expected, self.links_fetched, self.images_expected, self.images_read}:
                raise ValueError("FULL source requires explicit LINK-ALL and image expected/read counts; use zero when none exist")
            if self.links_fetched != self.links_expected:
                raise ValueError("FULL source must reconcile all expected links")
            if self.images_read != self.images_expected:
                raise ValueError("FULL source must reconcile all expected images")
            if self.content_max_available_at is None:
                raise ValueError("FULL source requires content_max_available_at for point-in-time freeze binding")
        if self.status != "FULL" and not self.gaps:
            raise ValueError("non-FULL source requires explicit gaps")
        return self


class SourceCompletionPackage(StrictModel):
    receipts: list[SourceReceipt] = Field(min_length=1)
    previous_five_pool_reused: bool
    previous_five_pool_ref: str = Field(min_length=1)
    repeated_five_pool_fetch_performed: bool = False

    @model_validator(mode="after")
    def five_pool_rule(self):
        if not self.previous_five_pool_reused or self.repeated_five_pool_fetch_performed:
            raise ValueError("premarket must reuse formal previous-review five-pool snapshot and must not re-fetch it")
        ids = [r.source_id for r in self.receipts]
        if len(set(ids)) != len(ids):
            raise ValueError("source completion receipts must have unique source_id values")
        return self


class EvidenceRecord(StrictModel):
    claim: str = Field(min_length=1)
    source_ref: str = Field(min_length=1)
    available_at: datetime
    evidence_type: str
    confidence: Literal["high", "medium", "low"] = "medium"
    negative: bool = False


class EventCard(StrictModel):
    event_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    classification: Literal["NEW", "CONTINUATION", "ROTATION", "BACKGROUND", "RUMOR", "NEGATIVE", "DISPROVED", "NO_TRADING_VALUE", "CALENDAR"]
    event_type: str = Field(min_length=1)
    available_at: datetime
    evidence_refs: list[str] = Field(min_length=1)
    catalyst_facts: list[str] = Field(min_length=1)
    negative_evidence: list[str] = Field(default_factory=list)
    duplicate_of: str | None = None
    tradable: bool = True


class EventLedgerPackage(StrictModel):
    events: list[EventCard] = Field(min_length=1)
    evidence_ledger: list[EvidenceRecord] = Field(min_length=1)
    omission_scan: list[str] = Field(default_factory=list)
    stop_reason: str = Field(min_length=1)


class IndustryNode(StrictModel):
    node_id: str
    event_id: str
    level: int = Field(ge=0, le=9)
    name: str = Field(min_length=1)
    parent_id: str | None = None
    economics: str = Field(min_length=1)
    direction: Literal["BENEFIT", "HURT", "MIXED", "NEUTRAL"]
    key_metrics: list[str] = Field(default_factory=list)


class StockMapping(StrictModel):
    event_id: str
    node_id: str
    ticker: str
    name: str
    mainboard_eligible: bool
    directness: Literal["A", "B", "C", "D"]
    business_stage: str
    products: list[str] = Field(default_factory=list)
    customers_orders_capacity: list[str] = Field(default_factory=list)
    profit_transmission: str = ""
    positive_evidence: list[str] = Field(default_factory=list)
    negative_evidence: list[str] = Field(default_factory=list)
    why_this: str = ""
    why_not_peers: list[str] = Field(default_factory=list)


class IndustryResearchPackage(StrictModel):
    nodes: list[IndustryNode] = Field(min_length=1)
    transmission_paths: list[str] = Field(min_length=1)
    cost_damage_paths: list[str] = Field(default_factory=list)
    mappings: list[StockMapping] = Field(min_length=1)
    max_depth_by_event: dict[str, int] = Field(default_factory=dict)
    sweeps_completed: int = Field(ge=2, le=20)
    stop_reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def depth_not_shallow(self):
        too_shallow = [event_id for event_id, depth in self.max_depth_by_event.items() if depth < 5]
        if too_shallow:
            raise ValueError(f"core industry research below L5 for events: {too_shallow}")
        return self


class StockBaseContext(StrictModel):
    ref: str = Field(min_length=1)
    version: str = Field(min_length=1)
    mode: Literal["READ_ONLY", "REVIEW_WRITE_ONLY"]
    retrieved_refs: list[str] = Field(min_length=1)
    conflicts: list[str] = Field(default_factory=list)


class UniversePackage(StrictModel):
    mappings: list[StockMapping] = Field(min_length=1)
    excluded: list[str] = Field(default_factory=list)
    exclusion_reasons: dict[str, str] = Field(default_factory=dict)
    node_exclusions: dict[str, str] = Field(default_factory=dict)
    all_event_nodes_exhausted: bool
    omitted_known_candidates: list[str] = Field(default_factory=list)
    stop_reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def exclusions_are_auditable(self):
        tickers = [m.ticker for m in self.mappings]
        if len(set(tickers)) != len(tickers):
            raise ValueError("Universe mappings must contain unique tickers")
        if len(set(self.excluded)) != len(self.excluded):
            raise ValueError("Universe excluded tickers must be unique")
        if set(self.exclusion_reasons) != set(self.excluded):
            raise ValueError("Universe exclusion_reasons must exactly cover excluded tickers")
        if any(not reason.strip() for reason in self.exclusion_reasons.values()):
            raise ValueError("Universe exclusion reasons must be non-empty")
        if any(not reason.strip() for reason in self.node_exclusions.values()):
            raise ValueError("Universe node exclusion reasons must be non-empty")
        return self


class HeightRecord(StrictModel):
    ticker: str
    name: str
    board_count: int = Field(ge=0)
    prior_pool_labels: list[str] = Field(default_factory=list)
    prior_theme: str = ""


class RoleHypothesis(StrictModel):
    ticker: str
    name: str
    event_id: str
    role_type: Literal["SPACE_LEADER", "THEME_LEADER", "NEW_THEME_PIONEER", "CARD_LEADER", "TURNOVER_LEADER", "TREND_LEADER", "CAPACITY_LEADER", "SUPPLEMENT_LEADER", "FOLLOWER", "ANCHOR", "AMBUSH"]
    evidence_dimensions: list[str] = Field(min_length=2)
    evidence: list[str] = Field(min_length=2)
    competing_candidates: list[str] = Field(default_factory=list)
    disconfirming_evidence: list[str] = Field(default_factory=list)
    invalidation: list[str] = Field(min_length=1)
    confidence: Literal["high", "medium", "low"]

    @model_validator(mode="after")
    def board_count_is_not_enough(self):
        dimensions = {x.lower() for x in self.evidence_dimensions}
        if dimensions <= {"board_count", "height", "身位"}:
            raise ValueError("board count/height alone cannot prove a market role")
        return self


class MarketStructurePackage(StrictModel):
    regime: list[str] = Field(min_length=1)
    heights: list[HeightRecord] = Field(min_length=1)
    roles: list[RoleHypothesis] = Field(min_length=1)
    same_height_competitions: list[str] = Field(default_factory=list)
    rotation_map: list[str] = Field(default_factory=list)
    high_low_map: list[str] = Field(default_factory=list)
    role_vacancies: list[str] = Field(default_factory=list)


class RecallCandidate(StrictModel):
    ticker: str
    name: str
    tier: Literal["P0", "P1", "P2"]
    event_ids: list[str] = Field(min_length=1)
    limit_up_paths: list[str] = Field(min_length=1)
    knowable_reasoning: list[str] = Field(min_length=1)
    role_hypotheses: list[str] = Field(default_factory=list)
    negative_evidence: list[str] = Field(default_factory=list)
    buyability: Literal["HIGH", "MEDIUM", "LOW", "UNKNOWN"] = "UNKNOWN"


class RecallPoolPackage(StrictModel):
    u0_tickers: list[str] = Field(min_length=1)
    u1_candidates: list[RecallCandidate] = Field(min_length=1)
    coverage_notes: list[str] = Field(default_factory=list)
    early_pruning_applied: bool = False

    @model_validator(mode="after")
    def recall_must_not_be_pruned(self):
        if self.early_pruning_applied:
            raise ValueError("Leader-First/execution preferences may not prune U0/U1 recall")
        if len(set(self.u0_tickers)) != len(self.u0_tickers):
            raise ValueError("U0 tickers must be unique")
        u1_tickers = [x.ticker for x in self.u1_candidates]
        if len(set(u1_tickers)) != len(u1_tickers):
            raise ValueError("U1 candidates must be unique")
        missing_from_u0 = sorted(set(u1_tickers) - set(self.u0_tickers))
        if missing_from_u0:
            raise ValueError(f"U1 candidates must be a subset of U0: {missing_from_u0}")
        return self


class ExecutionCandidate(StrictModel):
    ticker: str
    name: str
    slot: Literal["PRIMARY_LEADER", "BACKUP_LEADER", "NEW_THEME_PIONEER", "CAPACITY_ANCHOR"]
    strategy: str = Field(min_length=1)
    trigger: list[str] = Field(min_length=1)
    invalidation: list[str] = Field(min_length=1)
    why_this: list[str] = Field(min_length=1)
    why_not_peers: list[str] = Field(min_length=1)


class ExecutionPlan(StrictModel):
    candidates: list[ExecutionCandidate] = Field(max_length=4)
    no_trade_conditions: list[str] = Field(min_length=1)
    backup_chain: list[str] = Field(min_length=1)
    first_read_answer: str = Field(min_length=1)

    @model_validator(mode="after")
    def execution_slots_are_unique(self):
        tickers = [c.ticker for c in self.candidates]
        slots = [c.slot for c in self.candidates]
        if len(set(tickers)) != len(tickers):
            raise ValueError("Execution candidates must have unique tickers")
        if len(set(slots)) != len(slots):
            raise ValueError("Execution candidates must have unique role slots")
        return self


class GateDecision(StrictModel):
    status: Literal["PASS", "REVISE", "FAIL", "N_A"]
    evidence: list[str] = Field(min_length=1)
    defects: list[str] = Field(default_factory=list)
    revision_target: str | None = None
    remaining_boundaries: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def actionable(self):
        if self.status == "REVISE" and not self.revision_target:
            raise ValueError("REVISE requires revision_target")
        if self.status == "FAIL" and not self.defects:
            raise ValueError("FAIL requires defects")
        return self


class MarketOutcome(StrictModel):
    ticker: str
    name: str
    result: Literal["LIMIT_UP", "BROKEN", "LIMIT_DOWN", "STRONG", "OTHER"]
    board_count_after: int = Field(ge=0)
    event_labels: list[str] = Field(default_factory=list)


class OutcomePackage(StrictModel):
    outcomes: list[MarketOutcome] = Field(min_length=1)
    pool_counts: dict[str, int]
    source_refs: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def outcomes_reconcile(self):
        if any(v < 0 for v in self.pool_counts.values()):
            raise ValueError("outcome pool counts cannot be negative")
        tickers = [x.ticker for x in self.outcomes]
        if len(set(tickers)) != len(tickers):
            raise ValueError("outcome tickers must be unique")
        return self


class AttributionRecord(StrictModel):
    ticker: str
    name: str
    knowable_before_freeze: bool
    in_u0: bool
    in_u1: bool
    matched_event_ids: list[str] = Field(default_factory=list)
    miss_class: Literal["A_SOURCE", "B_EVENT", "C_INDUSTRY", "D_MAPPING", "E_ROLE_RANKING", "F_TIMING", "G_UNKNOWABLE", "HIT"]
    premarket_evidence: list[str] = Field(default_factory=list)
    postclose_facts: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def attribution_membership_consistent(self):
        if self.in_u1 and not self.in_u0:
            raise ValueError("in_u1 requires in_u0")
        if self.miss_class == "G_UNKNOWABLE" and self.knowable_before_freeze:
            raise ValueError("G_UNKNOWABLE requires knowable_before_freeze=false")
        if not self.knowable_before_freeze and self.miss_class != "G_UNKNOWABLE":
            raise ValueError("unknowable pre-freeze outcomes must use G_UNKNOWABLE")
        if self.miss_class == "HIT" and (not self.knowable_before_freeze or not self.in_u0):
            raise ValueError("HIT requires knowable_before_freeze=true and in_u0=true")
        return self


class AttributionPackage(StrictModel):
    actual_limit_ups: list[AttributionRecord] = Field(min_length=1)
    broken_boards: list[AttributionRecord] = Field(default_factory=list)
    limit_downs: list[AttributionRecord] = Field(default_factory=list)
    mention_ledger_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def attribution_sets_unique(self):
        groups = (("actual_limit_ups", self.actual_limit_ups), ("broken_boards", self.broken_boards), ("limit_downs", self.limit_downs))
        seen: set[str] = set()
        for label, rows in groups:
            tickers = [x.ticker for x in rows]
            if len(set(tickers)) != len(tickers):
                raise ValueError(f"duplicate ticker inside {label}")
            overlap = sorted(seen.intersection(tickers))
            if overlap:
                raise ValueError(f"ticker cannot appear in multiple mutually exclusive attribution outcome sets: {overlap}")
            seen.update(tickers)
        return self


class RecallGrade(StrictModel):
    actual_limit_up_total: int = Field(ge=0)
    excluded_scope_total: int = Field(ge=0)
    knowable_limit_up_total: int = Field(ge=0)
    u0_hits: int = Field(ge=0)
    u1_hits: int = Field(ge=0)
    u0_recall: float = Field(ge=0, le=1)
    u1_recall: float = Field(ge=0, le=1)
    miss_counts: dict[str, int] = Field(default_factory=dict)
    reconciliation_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def recall_arithmetic_reconciles(self):
        if self.excluded_scope_total > self.actual_limit_up_total:
            raise ValueError("excluded_scope_total cannot exceed actual_limit_up_total")
        in_scope_total = self.actual_limit_up_total - self.excluded_scope_total
        if self.knowable_limit_up_total > in_scope_total:
            raise ValueError("knowable_limit_up_total cannot exceed in-scope actual limit-ups")
        if self.u0_hits > self.knowable_limit_up_total or self.u1_hits > self.knowable_limit_up_total:
            raise ValueError("recall hits cannot exceed knowable_limit_up_total")
        if self.u1_hits > self.u0_hits:
            raise ValueError("U1 hits cannot exceed U0 hits")
        expected_u0 = self.u0_hits / self.knowable_limit_up_total if self.knowable_limit_up_total else 0.0
        expected_u1 = self.u1_hits / self.knowable_limit_up_total if self.knowable_limit_up_total else 0.0
        if abs(self.u0_recall - expected_u0) > 1e-9:
            raise ValueError("u0_recall must equal u0_hits / knowable_limit_up_total")
        if abs(self.u1_recall - expected_u1) > 1e-9:
            raise ValueError("u1_recall must equal u1_hits / knowable_limit_up_total")
        if any(v < 0 for v in self.miss_counts.values()):
            raise ValueError("miss counts cannot be negative")
        return self


class LearningAudit(StrictModel):
    errors: list[str] = Field(default_factory=list)
    repeated_errors: list[str] = Field(default_factory=list)
    candidate_hypotheses: list[str] = Field(default_factory=list)
    no_rule_change_reason: str = ""

    @model_validator(mode="after")
    def no_empty_learning_conclusion(self):
        if not self.candidate_hypotheses and not self.no_rule_change_reason:
            raise ValueError("learning audit without candidate hypotheses requires no_rule_change_reason")
        return self


class RuleProposal(StrictModel):
    status: Literal["PROPOSE", "N_A"]
    rule_id: str | None = None
    owner: str | None = None
    hypothesis: str = ""
    detection_rule: str = ""
    prevention_rule: str = ""
    applicable_regimes: list[str] = Field(default_factory=list)
    counterexamples: list[str] = Field(default_factory=list)
    replay_case_refs: list[str] = Field(default_factory=list)
    no_change_reason: str = ""

    @model_validator(mode="after")
    def validate_proposal(self):
        if self.status == "PROPOSE":
            if not all([self.rule_id, self.owner, self.hypothesis, self.detection_rule, self.prevention_rule]):
                raise ValueError("PROPOSE requires complete rule hypothesis metadata")
            if not self.applicable_regimes or not self.counterexamples or not self.replay_case_refs:
                raise ValueError("PROPOSE requires applicable regimes, counterexamples and replay case refs")
        elif not self.no_change_reason:
            raise ValueError("N_A rule proposal requires no_change_reason")
        return self


class ReplayEval(StrictModel):
    status: Literal["PASS", "REJECT", "HOLD", "N_A"]
    case_refs: list[str] = Field(default_factory=list)
    regimes: list[str] = Field(default_factory=list)
    positive_samples: int = Field(ge=0)
    negative_samples: int = Field(ge=0)
    baseline_metrics: dict[str, float] = Field(default_factory=dict)
    candidate_metrics: dict[str, float] = Field(default_factory=dict)
    regressions: list[str] = Field(default_factory=list)
    future_contamination_detected: bool = False
    decision_reason: str = Field(min_length=1)
    mechanical_evidence_refs: list[str] = Field(default_factory=list)
    cassette_hashes: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def replay_pass_requires_mechanical_evidence(self):
        if self.status != "PASS":
            return self
        if len(self.case_refs) < 5 or len(set(self.regimes)) < 2:
            raise ValueError("PASS requires at least five frozen cases across at least two regimes")
        if self.positive_samples < 1 or self.negative_samples < 1:
            raise ValueError("PASS requires positive and negative samples")
        if self.future_contamination_detected:
            raise ValueError("PASS cannot contain future-information contamination")
        if self.regressions:
            raise ValueError("PASS cannot contain material regressions")
        if not self.baseline_metrics or not self.candidate_metrics:
            raise ValueError("PASS requires baseline and candidate metrics")
        if not self.mechanical_evidence_refs:
            raise ValueError("PASS requires mechanical replay evidence refs")
        missing_hashes = sorted(set(self.case_refs) - set(self.cassette_hashes))
        if missing_hashes:
            raise ValueError(f"PASS requires cassette hashes for every case: {missing_hashes}")
        for case_ref, digest in self.cassette_hashes.items():
            if case_ref in self.case_refs and (len(digest) != 64 or any(ch not in "0123456789abcdefABCDEF" for ch in digest)):
                raise ValueError(f"invalid cassette sha256 for {case_ref}")
        return self
