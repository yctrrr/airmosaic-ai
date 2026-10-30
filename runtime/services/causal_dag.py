"""Bounded DAG and total-effect adjustment checks; no causal discovery from data."""

from __future__ import annotations

from collections import deque


class DAGError(ValueError):
    """Fixed diagnostic codes, without echoing variable names or private values."""


def check_adjustment(dag: dict, treatment: str, outcome: str, adjustment: list[str]) -> dict:
    """Check the backdoor criterion using ancestral moralization.

    This validates implications of the supplied graph, not its truth. Only a
    single-treatment total-effect adjustment design is supported.
    """
    try:
        nodes, edges = dag["nodes"], dag["edges"]
        latent = set(dag.get("latent", []))
        if (not 2 <= len(nodes) <= 30 or len(nodes) != len(set(nodes)) or len(edges) > 120
                or treatment == outcome or not {treatment, outcome} <= set(nodes)
                or not set(adjustment) <= set(nodes) or len(adjustment) != len(set(adjustment))
                or not latent <= set(nodes) or latent & {treatment, outcome}
                or set(adjustment) & (latent | {treatment, outcome})):
            raise DAGError("invalid_dag_roles")
        parents = {node: set() for node in nodes}
        children = {node: set() for node in nodes}
        for edge in edges:
            if (not isinstance(edge, list) or len(edge) != 2 or edge[0] == edge[1]
                    or not set(edge) <= set(nodes) or edge[1] in children[edge[0]]):
                raise DAGError("invalid_dag_edge")
            children[edge[0]].add(edge[1])
            parents[edge[1]].add(edge[0])
        indegree = {node: len(parents[node]) for node in nodes}
        queue = deque(node for node in nodes if not indegree[node])
        ordered = []
        while queue:
            node = queue.popleft()
            ordered.append(node)
            for child in children[node]:
                indegree[child] -= 1
                if not indegree[child]:
                    queue.append(child)
        if len(ordered) != len(nodes):
            raise DAGError("dag_contains_cycle")
        descendants, queue = set(), deque(children[treatment])
        while queue:
            node = queue.popleft()
            if node not in descendants:
                descendants.add(node)
                queue.extend(children[node])
        if set(adjustment) & descendants:
            raise DAGError("total_effect_adjustment_contains_descendant")
        # Remove edges leaving treatment, then d-separate treatment and outcome.
        back_parents = {node: parents[node] - {treatment} for node in nodes}
        ancestors, queue = set(), deque([treatment, outcome, *adjustment])
        while queue:
            node = queue.popleft()
            if node not in ancestors:
                ancestors.add(node)
                queue.extend(back_parents[node])
        moral = {node: set() for node in ancestors}
        for node in ancestors:
            connected = back_parents[node] & ancestors
            for parent in connected:
                moral[node].add(parent)
                moral[parent].add(node)
                moral[parent].update(connected - {parent})
        visited, queue = set(adjustment), deque([treatment])
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            if node == outcome:
                raise DAGError("adjustment_leaves_open_backdoor_path")
            visited.add(node)
            queue.extend(moral[node] - visited)
        return {"acyclic": True, "total_effect_backdoor_criterion": "passed_for_declared_graph",
                "causal_path_declared": outcome in descendants,
                "assumptions": "not_empirically_verified", "node_count": len(nodes), "edge_count": len(edges)}
    except DAGError:
        raise
    except (KeyError, TypeError, ValueError):
        raise DAGError("invalid_dag") from None


def mermaid(dag: dict, treatment: str, outcome: str) -> str:
    """IDs/labels have already passed the task schema's identifier constraint."""
    lines = ["flowchart LR"]
    for i, node in enumerate(dag["nodes"]):
        role = "treatment" if node == treatment else "outcome" if node == outcome else "covariate"
        lines.append(f'  n{i}["{node} ({role})"]')
    indices = {node: i for i, node in enumerate(dag["nodes"])}
    lines.extend(f"  n{indices[a]} --> n{indices[b]}" for a, b in dag["edges"])
    return "\n".join(lines) + "\n"
