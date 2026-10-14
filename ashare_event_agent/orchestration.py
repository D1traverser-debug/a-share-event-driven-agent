from __future__ import annotations

from collections import defaultdict, deque
from typing import Iterable


ALLOWED_COORDINATION = {
    "SERIAL_DEPENDENCY",
    "INDEPENDENT_PARALLEL",
    "FAN_OUT_FAN_IN",
    "CONSULTATIVE_ADVICE",
    "COMPETITIVE_CANDIDATES",
    "STRUCTURED_CRITIQUE_AND_REVISION",
    "OWNER_ADJUDICATION",
    "QUORUM_OR_PANEL_REVIEW",
}


class OrchestrationError(ValueError):
    pass


def _index(graph: dict) -> dict[str, dict]:
    nodes = graph.get("nodes") or []
    by_id = {row.get("id"): row for row in nodes}
    if None in by_id or len(by_id) != len(nodes):
        raise OrchestrationError("orchestration nodes require unique non-empty ids")
    return by_id


def validate_orchestration(graph: dict) -> None:
    """Validate the A-share market-day work graph without executing business work."""
    if graph.get("graph_type") != "ASHARE_MARKET_DAY_DECISION_GRAPH":
        raise OrchestrationError("unexpected graph_type")
    if graph.get("business_owner") != "DOMAIN:ashare":
        raise OrchestrationError("A-share work graph must remain domain-owned")
    decision_model = str(graph.get("decision_model", ""))
    if "NO_UNBOUNDED_PEER_CHAT" not in decision_model:
        raise OrchestrationError("decision model must forbid unbounded peer chat")

    by_id = _index(graph)
    indegree = {node_id: 0 for node_id in by_id}
    downstream: dict[str, list[str]] = defaultdict(list)
    groups: dict[str, list[str]] = defaultdict(list)

    for node_id, node in by_id.items():
        coordination = node.get("coordination")
        if coordination not in ALLOWED_COORDINATION:
            raise OrchestrationError(f"unsupported coordination pattern for {node_id}: {coordination}")
        for dep in node.get("depends_on") or []:
            if dep not in by_id:
                raise OrchestrationError(f"{node_id} depends on unknown node {dep}")
            indegree[node_id] += 1
            downstream[dep].append(node_id)
        if coordination == "COMPETITIVE_CANDIDATES":
            group = node.get("decision_group")
            if not group:
                raise OrchestrationError(f"competitive candidate {node_id} missing decision_group")
            groups[group].append(node_id)
        if coordination == "OWNER_ADJUDICATION" and not node.get("adjudicator"):
            raise OrchestrationError(f"adjudication {node_id} missing adjudicator")

    queue = deque(sorted(node_id for node_id, degree in indegree.items() if degree == 0))
    visited = 0
    degrees = dict(indegree)
    while queue:
        node_id = queue.popleft()
        visited += 1
        for child in downstream[node_id]:
            degrees[child] -= 1
            if degrees[child] == 0:
                queue.append(child)
    if visited != len(by_id):
        raise OrchestrationError("market-day orchestration dependencies must be acyclic")

    for group, candidates in groups.items():
        if len(candidates) < 2:
            raise OrchestrationError(f"decision group {group} requires at least two independent candidates")
        adjudicators = [
            (node_id, node)
            for node_id, node in by_id.items()
            if node.get("coordination") == "OWNER_ADJUDICATION" and node.get("consumes_group") == group
        ]
        if len(adjudicators) != 1:
            raise OrchestrationError(f"decision group {group} requires exactly one authorized adjudication node")
        adjudicator_id, adjudicator = adjudicators[0]
        missing = sorted(set(candidates) - set(adjudicator.get("depends_on") or []))
        if missing:
            raise OrchestrationError(f"{adjudicator_id} must depend on every candidate in {group}: {missing}")


def ready_nodes(graph: dict, completed: Iterable[str]) -> tuple[str, ...]:
    """Return nodes whose declared dependencies are complete; no hidden wave ordering is added."""
    validate_orchestration(graph)
    done = set(completed)
    by_id = _index(graph)
    unknown = done - set(by_id)
    if unknown:
        raise OrchestrationError(f"completed set contains unknown nodes: {sorted(unknown)}")
    return tuple(
        node_id
        for node_id, node in by_id.items()
        if node_id not in done and set(node.get("depends_on") or []).issubset(done)
    )


def downstream_nodes(graph: dict, changed_node: str) -> tuple[str, ...]:
    """Return only work that transitively depends on a changed node, for bounded revision."""
    validate_orchestration(graph)
    by_id = _index(graph)
    if changed_node not in by_id:
        raise OrchestrationError(f"unknown changed node: {changed_node}")
    children: dict[str, list[str]] = defaultdict(list)
    for node_id, node in by_id.items():
        for dep in node.get("depends_on") or []:
            children[dep].append(node_id)
    seen: set[str] = set()
    queue = deque(children[changed_node])
    while queue:
        node_id = queue.popleft()
        if node_id in seen:
            continue
        seen.add(node_id)
        queue.extend(children[node_id])
    return tuple(node_id for node_id in by_id if node_id in seen)
