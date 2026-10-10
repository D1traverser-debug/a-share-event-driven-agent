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
    outside = sorted(execution - u1)
    return [f"U3 execution candidates must descend from U1: {outside}"] if outside else []


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


def recall_grade_integrity_errors(attribution: AttributionPackage, grade: RecallGrade) -> list[str]:
    rows = attribution.actual_limit_ups
    errors: list[str] = []
    in_scope = len(rows)
    if grade.actual_limit_up_total - grade.excluded_scope_total != in_scope:
        errors.append(
            "RecallGrade in-scope denominator must equal the number of attributed in-scope actual limit-ups"
        )
    knowable = sum(1 for row in rows if row.knowable_before_freeze)
    u0_hits = sum(1 for row in rows if row.knowable_before_freeze and row.in_u0)
    u1_hits = sum(1 for row in rows if row.knowable_before_freeze and row.in_u1)
    if grade.knowable_limit_up_total != knowable:
        errors.append(f"knowable_limit_up_total must equal attributed knowable count {knowable}")
    if grade.u0_hits != u0_hits:
        errors.append(f"u0_hits must equal frozen-attribution hit count {u0_hits}")
    if grade.u1_hits != u1_hits:
        errors.append(f"u1_hits must equal frozen-attribution hit count {u1_hits}")
    return errors


def replay_coherence_errors(proposal: RuleProposal, replay: ReplayEval) -> list[str]:
    if proposal.status == "N_A" and replay.status != "N_A":
        return ["N_A rule proposal requires N_A replay result"]
    if proposal.status == "PROPOSE" and replay.status == "N_A":
        return ["PROPOSE rule requires PASS, REJECT or HOLD replay result"]
    return []
