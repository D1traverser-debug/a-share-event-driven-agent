from __future__ import annotations

from .schemas import (
    AttributionPackage,
    ExecutionPlan,
    IndustryResearchPackage,
    OutcomePackage,
    RecallGrade,
    RecallPoolPackage,
    ReplayEval,
    RuleProposal,
    UniversePackage,
)


def universe_integrity_errors(industry: IndustryResearchPackage, universe: UniversePackage) -> list[str]:
    errors: list[str] = []

    node_ids = {node.node_id for node in industry.nodes}
    mapped_node_ids = {mapping.node_id for mapping in industry.mappings}
    accounted_nodes = mapped_node_ids | set(universe.node_exclusions)
    missing_nodes = sorted(node_ids - accounted_nodes)
    unknown_node_exclusions = sorted(set(universe.node_exclusions) - node_ids)
    if missing_nodes:
        errors.append(f"industry nodes were not stock-mapped or explicitly node-excluded: {missing_nodes}")
    if unknown_node_exclusions:
        errors.append(f"Universe node_exclusions reference unknown industry nodes: {unknown_node_exclusions}")

    eligible_tickers = {mapping.ticker for mapping in industry.mappings if mapping.mainboard_eligible}
    included_tickers = {mapping.ticker for mapping in universe.mappings}
    excluded_tickers = set(universe.excluded)

    non_mainboard_included = sorted({mapping.ticker for mapping in universe.mappings if not mapping.mainboard_eligible})
    if non_mainboard_included:
        errors.append(f"active Universe contains non-mainboard mappings: {non_mainboard_included}")

    unknown_included = sorted(included_tickers - eligible_tickers)
    if unknown_included:
        errors.append(f"Universe contains tickers not present as eligible industry mappings: {unknown_included}")

    unknown_excluded = sorted(excluded_tickers - eligible_tickers)
    if unknown_excluded:
        errors.append(f"Universe excludes tickers that were not eligible industry mappings: {unknown_excluded}")

    expected_included = eligible_tickers - excluded_tickers
    missing_tickers = sorted(expected_included - included_tickers)
    extra_tickers = sorted(included_tickers - expected_included)
    if missing_tickers:
        errors.append(f"eligible mapped tickers silently omitted from Universe: {missing_tickers}")
    if extra_tickers:
        errors.append(f"Universe includes tickers inconsistent with exclusions/eligibility: {extra_tickers}")

    industry_keys = {(m.event_id, m.node_id, m.ticker) for m in industry.mappings}
    unknown_primary_mappings = sorted(
        f"{m.event_id}:{m.node_id}:{m.ticker}"
        for m in universe.mappings
        if (m.event_id, m.node_id, m.ticker) not in industry_keys
    )
    if unknown_primary_mappings:
        errors.append(f"Universe primary mappings were not present in industry research: {unknown_primary_mappings}")

    if not universe.all_event_nodes_exhausted:
        errors.append("all_event_nodes_exhausted must be true before Universe PASS")
    if universe.omitted_known_candidates:
        errors.append(f"known omitted candidates remain: {sorted(universe.omitted_known_candidates)}")
    return errors


def recall_integrity_errors(universe: UniversePackage, recall: RecallPoolPackage) -> list[str]:
    expected_u0 = {mapping.ticker for mapping in universe.mappings}
    actual_u0 = set(recall.u0_tickers)
    errors: list[str] = []
    missing = sorted(expected_u0 - actual_u0)
    extra = sorted(actual_u0 - expected_u0)
    if missing:
        errors.append(f"U0 omitted Universe tickers: {missing}")
    if extra:
        errors.append(f"U0 contains tickers outside Universe: {extra}")
    return errors


def execution_integrity_errors(recall: RecallPoolPackage, plan: ExecutionPlan) -> list[str]:
    u1 = {candidate.ticker for candidate in recall.u1_candidates}
    execution = {candidate.ticker for candidate in plan.candidates}
    errors: list[str] = []
    outside = sorted(execution - u1)
    if outside:
        errors.append(f"U3 execution candidates must descend from U1: {outside}")

    assessed = {row.ticker for row in plan.risk_assessments}
    missing_assessments = sorted(u1 - assessed)
    unknown_assessments = sorted(assessed - u1)
    if missing_assessments:
        errors.append(f"every U1 candidate requires explicit risk/buyability assessment before U3 adjudication: {missing_assessments}")
    if unknown_assessments:
        errors.append(f"risk assessments contain tickers outside frozen U1: {unknown_assessments}")

    blocked = {row.ticker for row in plan.risk_assessments if row.decision == "BLOCK"}
    selected_blocked = sorted(execution & blocked)
    if selected_blocked:
        errors.append(f"hard-risk-veto candidates cannot enter U3: {selected_blocked}")

    risk_by_ticker = {row.ticker: row for row in plan.risk_assessments}
    selected_without_assessment = sorted(ticker for ticker in execution if ticker not in risk_by_ticker)
    if selected_without_assessment:
        errors.append(f"selected candidates missing risk assessment: {selected_without_assessment}")

    if not plan.preferred_microstructure_observed and plan.assurance != "DEGRADED":
        errors.append("missing preferred Level-2/microstructure evidence requires DEGRADED execution assurance")
    return errors


def attribution_integrity_errors(
    outcomes: OutcomePackage,
    recall: RecallPoolPackage,
    attribution: AttributionPackage,
) -> list[str]:
    errors: list[str] = []
    u0 = set(recall.u0_tickers)
    u1 = {candidate.ticker for candidate in recall.u1_candidates}

    for rows in (attribution.actual_limit_ups, attribution.broken_boards, attribution.limit_downs):
        for row in rows:
            expected_u0 = row.ticker in u0
            expected_u1 = row.ticker in u1
            if row.in_u0 != expected_u0:
                errors.append(f"attribution in_u0 disagrees with frozen U0 for {row.ticker}")
            if row.in_u1 != expected_u1:
                errors.append(f"attribution in_u1 disagrees with frozen U1 for {row.ticker}")

    expected = {
        "actual_limit_ups": {row.ticker for row in outcomes.outcomes if row.result == "LIMIT_UP"},
        "broken_boards": {row.ticker for row in outcomes.outcomes if row.result == "BROKEN"},
        "limit_downs": {row.ticker for row in outcomes.outcomes if row.result == "LIMIT_DOWN"},
    }
    observed = {
        "actual_limit_ups": {row.ticker for row in attribution.actual_limit_ups},
        "broken_boards": {row.ticker for row in attribution.broken_boards},
        "limit_downs": {row.ticker for row in attribution.limit_downs},
    }
    for label in expected:
        missing = sorted(expected[label] - observed[label])
        extra = sorted(observed[label] - expected[label])
        if missing:
            errors.append(f"{label} attribution omitted outcome tickers: {missing}")
        if extra:
            errors.append(f"{label} attribution contains tickers absent from outcomes: {extra}")
    return errors


def recall_grade_integrity_errors(
    attribution: AttributionPackage,
    grade: RecallGrade,
    plan: ExecutionPlan | None = None,
    outcomes: OutcomePackage | None = None,
) -> list[str]:
    rows = attribution.actual_limit_ups
    errors: list[str] = []
    in_scope = len(rows)
    if grade.actual_limit_up_total - grade.excluded_scope_total != in_scope:
        errors.append("RecallGrade in-scope denominator must equal the number of attributed in-scope actual limit-ups")
    knowable = sum(1 for row in rows if row.knowable_before_freeze)
    u0_hits = sum(1 for row in rows if row.knowable_before_freeze and row.in_u0)
    u1_hits = sum(1 for row in rows if row.knowable_before_freeze and row.in_u1)
    if grade.knowable_limit_up_total != knowable:
        errors.append(f"knowable_limit_up_total must equal attributed knowable count {knowable}")
    if grade.u0_hits != u0_hits:
        errors.append(f"u0_hits must equal frozen-attribution hit count {u0_hits}")
    if grade.u1_hits != u1_hits:
        errors.append(f"u1_hits must equal frozen-attribution hit count {u1_hits}")

    if plan is None or outcomes is None:
        return errors

    selected = [candidate.ticker for candidate in plan.candidates]
    outcome_by_ticker = {row.ticker: row for row in outcomes.outcomes}
    missing_outcomes = sorted(set(selected) - set(outcome_by_ticker))
    if missing_outcomes:
        errors.append(f"final U3 candidates missing post-close outcome/execution review: {missing_outcomes}")
        return errors

    activated = []
    not_activated = 0
    for ticker in selected:
        row = outcome_by_ticker[ticker]
        if row.trigger_observed is None:
            errors.append(f"final U3 candidate missing trigger_observed review: {ticker}")
            continue
        if row.trigger_observed:
            activated.append(row)
            if row.entry_feasible is None or not row.execution_evidence_refs:
                errors.append(f"activated final candidate missing execution feasibility evidence: {ticker}")
        else:
            not_activated += 1

    expected_categories = {
        "LIMIT_UP": sum(1 for row in activated if row.result == "LIMIT_UP"),
        "STRONG": sum(1 for row in activated if row.result == "STRONG"),
        "BROKEN": sum(1 for row in activated if row.result == "BROKEN"),
        "LIMIT_DOWN": sum(1 for row in activated if row.result == "LIMIT_DOWN"),
        "OTHER": sum(1 for row in activated if row.result == "OTHER"),
    }
    q = grade.selection_quality
    expected = {
        "candidate_slots_total": len(selected),
        "activated_total": len(activated),
        "not_activated_total": not_activated,
        "activated_limit_up_hits": expected_categories["LIMIT_UP"],
        "activated_strong_hits": expected_categories["STRONG"],
        "activated_broken": expected_categories["BROKEN"],
        "activated_limit_down": expected_categories["LIMIT_DOWN"],
        "activated_other": expected_categories["OTHER"],
        "execution_feasible_total": sum(1 for row in activated if row.entry_feasible is True),
        "execution_infeasible_total": sum(1 for row in activated if row.entry_feasible is False),
    }
    for field, value in expected.items():
        if getattr(q, field) != value:
            errors.append(f"selection_quality.{field} must equal frozen-plan/outcome derived count {value}")
    return errors


def replay_coherence_errors(proposal: RuleProposal, replay: ReplayEval) -> list[str]:
    if proposal.status == "N_A" and replay.status != "N_A":
        return ["N_A rule proposal requires N_A replay result"]
    if proposal.status == "PROPOSE" and replay.status == "N_A":
        return ["PROPOSE rule requires PASS, REJECT or HOLD replay result"]
    return []
