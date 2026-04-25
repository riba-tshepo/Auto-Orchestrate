#!/usr/bin/env python3
"""
Dependency Graph Analyzer — topological sort, cycle detection, critical path.

Given a JSON dependency register, builds a directed graph and returns:
- Topological ordering (or cycles if any)
- Critical path (longest path through the DAG)
- Per-node depth (parallelizable groups)

Usage:
    dep_graph.py --input INPUT.json [--output OUTPUT.json] [-o json|human]

Input format (JSON):
    [
      {"id": "dep-001", "duration_days": 14, "predecessors": []},
      {"id": "dep-002", "duration_days": 7, "predecessors": ["dep-001"]},
      ...
    ]

Exit codes:
    0  EXIT_SUCCESS
    2  EXIT_INVALID_INPUT
    50 EXIT_CYCLE_DETECTED
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SHARED_PY = SCRIPT_DIR.parent.parent / "_shared" / "python"
if SHARED_PY.exists():
    sys.path.insert(0, str(SHARED_PY))
    try:
        from layer0.exit_codes import EXIT_SUCCESS, EXIT_INVALID_INPUT  # type: ignore
    except ImportError:
        EXIT_SUCCESS = 0
        EXIT_INVALID_INPUT = 2
else:
    EXIT_SUCCESS = 0
    EXIT_INVALID_INPUT = 2

EXIT_CYCLE_DETECTED = 50


def topological_sort(nodes: dict, edges_to: dict) -> tuple[list[str] | None, list[list[str]]]:
    """Kahn's algorithm. Returns (topo_order, []) on success, (None, cycles) on cycle."""
    in_degree = {n: len(edges_to.get(n, set())) for n in nodes}
    queue = [n for n, deg in in_degree.items() if deg == 0]
    result = []

    while queue:
        n = queue.pop(0)
        result.append(n)
        for m in nodes:
            if n in edges_to.get(m, set()):
                in_degree[m] -= 1
                if in_degree[m] == 0:
                    queue.append(m)

    if len(result) == len(nodes):
        return result, []

    # Cycle exists; find SCCs via Tarjan's
    cycles = find_sccs(nodes, edges_to)
    return None, [c for c in cycles if len(c) > 1]


def find_sccs(nodes: dict, edges_to: dict) -> list[list[str]]:
    """Tarjan's SCC algorithm."""
    edges_from = defaultdict(set)
    for n in nodes:
        for pred in edges_to.get(n, set()):
            edges_from[pred].add(n)

    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = {}
    result = []

    def strongconnect(node):
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack[node] = True

        for successor in edges_from.get(node, set()):
            if successor not in index:
                strongconnect(successor)
                lowlinks[node] = min(lowlinks[node], lowlinks[successor])
            elif on_stack.get(successor):
                lowlinks[node] = min(lowlinks[node], index[successor])

        if lowlinks[node] == index[node]:
            connected_component = []
            while True:
                successor = stack.pop()
                on_stack[successor] = False
                connected_component.append(successor)
                if successor == node:
                    break
            result.append(connected_component)

    for n in nodes:
        if n not in index:
            strongconnect(n)

    return result


def compute_critical_path(nodes: dict, edges_to: dict, topo: list[str]) -> tuple[int, list[str]]:
    """
    Forward + backward pass to compute earliest finish, then walk the longest path.
    `nodes` is dict of id → {"duration_days": int}.
    `edges_to[id]` is the set of predecessor ids.
    """
    ef = {n: 0 for n in nodes}
    longest_pred = {n: None for n in nodes}
    for n in topo:
        preds = edges_to.get(n, set())
        if preds:
            best = max(preds, key=lambda p: ef[p])
            ef[n] = ef[best] + nodes[n]["duration_days"]
            longest_pred[n] = best
        else:
            ef[n] = nodes[n]["duration_days"]
            longest_pred[n] = None

    if not ef:
        return 0, []

    # Find the node with max EF — this is the project completion
    end_node = max(ef, key=lambda n: ef[n])
    project_duration = ef[end_node]

    # Walk backward from end_node via longest_pred
    path = []
    cur = end_node
    while cur is not None:
        path.append(cur)
        cur = longest_pred[cur]
    path.reverse()

    return project_duration, path


def compute_depth_groups(nodes: dict, edges_to: dict, topo: list[str]) -> dict[int, list[str]]:
    """Group nodes by their depth from sources. Same-depth nodes can run in parallel."""
    depth = {}
    for n in topo:
        preds = edges_to.get(n, set())
        depth[n] = (max((depth[p] for p in preds), default=-1) + 1)
    by_depth = defaultdict(list)
    for n, d in depth.items():
        by_depth[d].append(n)
    return dict(by_depth)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Analyze dependency graph: topo sort + cycles + critical path.")
    p.add_argument("--input", required=True, help="Path to dependencies JSON")
    p.add_argument("--output", help="Path to write analysis JSON")
    p.add_argument("-o", "--output-format", choices=("json", "human"), default="json")
    args = p.parse_args(argv)

    try:
        deps = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"error": f"failed to read input: {exc}"}))
        return EXIT_INVALID_INPUT

    nodes = {}
    edges_to = defaultdict(set)
    for d in deps:
        if "id" not in d:
            print(json.dumps({"error": "every dependency must have an id"}))
            return EXIT_INVALID_INPUT
        nodes[d["id"]] = {"duration_days": d.get("duration_days", 1)}
        for pred in d.get("predecessors", []):
            edges_to[d["id"]].add(pred)

    # Verify all predecessors exist as nodes
    missing = []
    for n in nodes:
        for pred in edges_to.get(n, set()):
            if pred not in nodes:
                missing.append((n, pred))
    if missing:
        print(json.dumps({"error": "predecessor refs missing", "missing": missing}))
        return EXIT_INVALID_INPUT

    topo, cycles = topological_sort(nodes, edges_to)

    if topo is None:
        result = {
            "ok": False,
            "cycle_detected": True,
            "cycles": cycles,
            "remediation": "cycles must be resolved before scheduling; see references/critical-path-method.md cycle-detection section",
        }
        out = json.dumps(result, indent=2)
        if args.output:
            Path(args.output).write_text(out + "\n", encoding="utf-8")
        else:
            print(out)
        return EXIT_CYCLE_DETECTED

    project_duration, critical_path = compute_critical_path(nodes, edges_to, topo)
    depth_groups = compute_depth_groups(nodes, edges_to, topo)

    result = {
        "ok": True,
        "node_count": len(nodes),
        "topological_order": topo,
        "critical_path": critical_path,
        "critical_path_duration_days": project_duration,
        "parallelizable_groups": {str(k): v for k, v in sorted(depth_groups.items())},
    }

    out = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(out + "\n", encoding="utf-8")
        if args.output_format == "human":
            print(f"Wrote analysis: {len(nodes)} nodes, critical path {project_duration} days, "
                  f"{len(critical_path)} activities on critical path")
    else:
        print(out)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
