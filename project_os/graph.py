from __future__ import annotations

import math
from collections import defaultdict
from html import escape
from typing import Iterable

import plotly.graph_objects as go

from project_os.family import EVIDENCE_RANK, STATUS_LABELS
from project_os.models import ProjectEdge, ProjectNode, ProjectRegistry
from project_os.patterns import candidate_visual_quality, node_pattern_tags, normalized_metric_snapshot


STATUS_COLORS = {
    "strong_candidate": "#22c55e",
    "worth_watching": "#84cc16",
    "needs_more_proof": "#f59e0b",
    "blocked": "#f97316",
    "rejected": "#ef4444",
    "active": "#38bdf8",
    "archived": "#94a3b8",
    "diagnostic_only": "#a78bfa",
    "unknown": "#64748b",
    "health_issue": "#f59e0b",
}

EVIDENCE_COLORS = {
    "live_forward": "#20e184",
    "forward_shadow": "#39d2ff",
    "live_stats": "#2dd4bf",
    "replay": "#c084fc",
    "backtest": "#fbbf24",
    "diagnostic": "#a3adbc",
    "metadata_only": "#718096",
    "unknown": "#4b5563",
}

FAMILY_COLORS = {
    "rv600": "#38bdf8",
    "v28_successor": "#a78bfa",
    "live_v28": "#22c55e",
    "ou_mispricing": "#f59e0b",
    "truffle": "#fb923c",
    "ninety_touch": "#2dd4bf",
    "particle_sim": "#eab308",
    "strategy_research": "#c084fc",
    "legacy_live": "#14b8a6",
    "research_os": "#60a5fa",
    "dashboard_ui": "#f472b6",
    "infrastructure": "#64748b",
    "unclassified": "#94a3b8",
}

FAMILY_CENTERS = {
    "v28_successor": (-4.4, 1.05),
    "live_v28": (-0.8, 3.15),
    "unclassified": (3.9, 1.35),
    "rv600": (3.4, -1.55),
    "ou_mispricing": (-4.6, -2.25),
    "truffle": (-0.9, -3.55),
    "ninety_touch": (2.0, -3.55),
    "particle_sim": (0.8, -1.35),
    "strategy_research": (4.7, 3.0),
    "legacy_live": (1.5, 3.65),
    "research_os": (-2.9, 4.0),
    "dashboard_ui": (4.4, -3.0),
    "infrastructure": (-5.1, 3.5),
}

KIND_SYMBOLS = {
    "family": "hexagon",
    "candidate": "star",
    "report": "square",
    "dataset": "diamond",
    "stats": "circle",
    "log": "circle-open",
    "script": "triangle-up",
    "doc": "square-open",
    "health_issue": "triangle-up",
    "secret": "diamond-open",
    "archive": "triangle-left-open",
    "artifact": "pentagon",
    "unknown": "circle-dot",
}

KIND_GLYPHS = {
    "family": "F",
    "candidate": "C",
    "report": "R",
    "dataset": "D",
    "stats": "S",
    "log": "L",
    "script": "P",
    "doc": "N",
    "health_issue": "!",
    "secret": "K",
    "archive": "A",
    "artifact": "O",
    "unknown": "?",
}

LENS_STATUS_COLORS = {
    "repeat-risk": "#ff4d6d",
    "frontier": "#39d2ff",
    "failure": "#fb7185",
    "evidence": "#20e184",
}

CANDIDATE_QUALITY_COLORS = {
    "excellent": "#22c55e",
    "positive": "#84cc16",
    "watch": "#a3e635",
    "neutral": "#f59e0b",
    "weak": "#fb923c",
    "bad": "#ef4444",
    "awful": "#b91c1c",
}

PIPELINE_LANES = {
    "doc": 0,
    "script": 0,
    "archive": 0,
    "log": 1,
    "dataset": 1,
    "stats": 1,
    "artifact": 2,
    "report": 2,
    "candidate": 3,
    "family": 4,
    "health_issue": 5,
    "secret": 5,
    "unknown": 5,
}


def _fallback_layout(nodes: list[ProjectNode], mode: str) -> dict[str, tuple[float, float]]:
    grouped: dict[str, list[ProjectNode]] = defaultdict(list)
    if mode == "pipeline":
        for node in nodes:
            grouped[str(PIPELINE_LANES.get(node.kind, 5))].append(node)
    else:
        for node in nodes:
            grouped[node.family or "unclassified"].append(node)
    positions: dict[str, tuple[float, float]] = {}
    groups = sorted(grouped)
    for gi, group in enumerate(groups):
        members = sorted(grouped[group], key=lambda n: (n.kind, n.label))
        for ni, node in enumerate(members):
            if mode == "pipeline":
                positions[node.id] = (float(int(group)), -float(ni))
            else:
                angle = 2 * math.pi * (ni / max(len(members), 1))
                radius = 0.45 + min(len(members), 60) / 80
                positions[node.id] = (gi * 3.0 + math.cos(angle) * radius, math.sin(angle) * radius)
    return positions


def _vault_layout(nodes: list[ProjectNode]) -> dict[str, tuple[float, float]]:
    grouped: dict[str, list[ProjectNode]] = defaultdict(list)
    for node in nodes:
        grouped[node.family or "unclassified"].append(node)
    families = sorted(grouped, key=lambda family: (-len(grouped[family]), family))
    if not families:
        return {}

    positions: dict[str, tuple[float, float]] = {}
    outer_radius = 4.0 + min(len(families), 10) * 0.18
    for family_index, family in enumerate(families):
        base_angle = 2 * math.pi * family_index / max(len(families), 1)
        if family in FAMILY_CENTERS:
            center_x, center_y = FAMILY_CENTERS[family]
        else:
            center_x = math.cos(base_angle) * outer_radius
            center_y = math.sin(base_angle) * outer_radius * 0.72
        members = sorted(grouped[family], key=lambda node: (node.kind != "family", node.kind, node.status, node.label.lower()))

        family_node = next((node for node in members if node.kind == "family"), None)
        if family_node:
            positions[family_node.id] = (center_x, center_y)

        satellites = [node for node in members if node.kind != "family"]
        ring_index_by_kind = {
            "candidate": 0,
            "health_issue": 0,
            "secret": 0,
            "report": 1,
            "stats": 1,
            "dataset": 2,
            "doc": 2,
            "log": 3,
            "archive": 3,
            "artifact": 3,
            "unknown": 3,
            "script": 4,
        }
        rings: dict[int, list[ProjectNode]] = defaultdict(list)
        for node in satellites:
            rings[ring_index_by_kind.get(node.kind, 3)].append(node)

        for ring, ring_nodes in rings.items():
            ring_nodes = sorted(ring_nodes, key=lambda node: (node.kind, node.status, node.label.lower()))
            radius = 0.65 + ring * 0.52 + math.sqrt(max(len(ring_nodes), 1)) * 0.055
            angle_offset = base_angle / 3 + ring * 0.37
            for node_index, node in enumerate(ring_nodes):
                theta = angle_offset + 2 * math.pi * node_index / max(len(ring_nodes), 1)
                wobble = 1 + 0.08 * math.sin((node_index + 1) * 1.7)
                positions[node.id] = (
                    center_x + math.cos(theta) * radius * wobble,
                    center_y + math.sin(theta) * radius * 0.82 * wobble,
                )
    return positions


def compute_layout(nodes: list[ProjectNode], edges: list[ProjectEdge], mode: str = "network") -> dict[str, tuple[float, float]]:
    if mode == "vault atlas":
        return _vault_layout(nodes)
    if mode in {"pipeline", "family clusters"}:
        return _fallback_layout(nodes, "pipeline" if mode == "pipeline" else "family clusters")
    try:
        import networkx as nx

        graph = nx.Graph()
        for node in nodes:
            graph.add_node(node.id)
        for edge in edges:
            if edge.source in graph and edge.target in graph:
                graph.add_edge(edge.source, edge.target, weight=1 + EVIDENCE_RANK.get(edge.evidence_level, 0))
        if not graph.nodes:
            return {}
        pos = nx.spring_layout(graph, seed=42, k=0.7, iterations=80)
        return {node_id: (float(x), float(y)) for node_id, (x, y) in pos.items()}
    except Exception:
        return _fallback_layout(nodes, "family clusters")


def _should_collapse_node(node: ProjectNode, *, lod: bool = False) -> bool:
    if node.kind == "script":
        return True
    if not lod:
        return False
    if node.kind in {"family", "candidate", "health_issue", "secret", "stats"}:
        return False
    if node.status in {"strong_candidate", "worth_watching", "blocked"}:
        return False
    if EVIDENCE_RANK.get(node.evidence_level, 0) >= EVIDENCE_RANK["live_stats"]:
        return False
    return node.kind in {"log", "dataset", "doc", "archive", "artifact", "unknown"}


def collapse_graph(nodes: list[ProjectNode], edges: list[ProjectEdge], threshold: int = 750, lod_threshold: int = 420) -> tuple[list[ProjectNode], list[ProjectEdge], dict[str, list[str]]]:
    lod = len(nodes) > lod_threshold
    if len(nodes) <= threshold and not lod:
        return nodes, edges, {}
    kept = [node for node in nodes if not _should_collapse_node(node, lod=lod)]
    collapsed: dict[str, list[str]] = defaultdict(list)
    summary_nodes: list[ProjectNode] = []
    for node in nodes:
        if not _should_collapse_node(node, lod=lod):
            continue
        key = f"artifact_summary:{node.family}:{node.kind}:{node.evidence_level if lod else 'all'}"
        collapsed[key].append(node.id)
    for key, child_ids in collapsed.items():
        _prefix, family, kind, evidence = key.split(":", 3)
        summary_nodes.append(
            ProjectNode(
                id=key,
                kind="artifact",
                label=f"{family} {kind} cluster ({len(child_ids)})",
                family=family,
                status="archived" if kind == "archive" else "diagnostic_only",
                evidence_level=evidence if evidence != "all" else "metadata_only",
                metrics={"collapsed_children": len(child_ids)},
                tags=["collapsed"],
                source_adapter="graph",
                confidence="inferred",
                summary=f"{len(child_ids)} {kind} nodes collapsed for atlas readability. Filter this family/kind to inspect children.",
            )
        )
    visible_ids = {node.id for node in [*kept, *summary_nodes]}
    replacement: dict[str, str] = {}
    for summary_id, child_ids in collapsed.items():
        for child_id in child_ids:
            replacement[child_id] = summary_id
    rewritten: dict[str, ProjectEdge] = {}
    for edge in edges:
        source = replacement.get(edge.source, edge.source)
        target = replacement.get(edge.target, edge.target)
        if source == target or source not in visible_ids or target not in visible_ids:
            continue
        new_edge = ProjectEdge(source=source, target=target, relation=edge.relation, evidence_level=edge.evidence_level, confidence=edge.confidence, reason=edge.reason)
        rewritten[new_edge.id] = new_edge
    return [*kept, *summary_nodes], list(rewritten.values()), dict(collapsed)


def _hex_to_rgba(color: str, alpha: float) -> str:
    value = color.lstrip("#")
    if len(value) != 6:
        return f"rgba(148,163,184,{alpha})"
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha})"


def _node_art_level(node: ProjectNode, degree: int, selected: bool = False, neighbor: bool = False) -> int:
    if selected:
        return 5
    if neighbor:
        return 4
    if node.kind in {"family", "candidate", "health_issue", "secret"}:
        return 3
    if node.status in {"strong_candidate", "worth_watching", "blocked"}:
        return 2
    if degree >= 8:
        return 1
    return 0


def _node_opacity(node: ProjectNode, selected_id: str, selected: bool, neighbor: bool) -> float:
    if selected:
        return 1.0
    if neighbor:
        return 0.94
    if selected_id:
        return 0.22
    if node.status in {"archived", "unknown"} or node.kind in {"archive", "unknown"}:
        return 0.54
    if node.kind in {"log", "script"}:
        return 0.70
    return 0.90


def _candidate_quality(node: ProjectNode) -> dict[str, object]:
    return candidate_visual_quality(node)


def _candidate_quality_color(node: ProjectNode) -> str | None:
    if node.kind != "candidate":
        return None
    quality = _candidate_quality(node)
    return CANDIDATE_QUALITY_COLORS.get(str(quality["label"]), CANDIDATE_QUALITY_COLORS["neutral"])


def _candidate_quality_size_delta(node: ProjectNode) -> int:
    if node.kind != "candidate":
        return 0
    score = float(_candidate_quality(node)["score"])
    if score >= 0.72:
        return 12
    if score >= 0.38:
        return 8
    if score >= 0.14:
        return 4
    if score <= -0.72:
        return -8
    if score <= -0.38:
        return -5
    if score <= -0.14:
        return -2
    return 0


def _hover_text(node: ProjectNode, degree: int) -> str:
    label = STATUS_LABELS.get(node.status, node.status)
    summary = escape((node.summary or "")[:220])
    next_action = escape((node.next_action or "")[:180])
    action_line = f"<br><b>Next:</b> {next_action}" if next_action else ""
    snapshot = normalized_metric_snapshot(node)
    metrics = []
    for key in ("pnl_7d_display", "actual_pnl_source_dollars", "pnl_observed_window_days", "net_pnl", "selected_pnl", "selected_pnl_cents", "entries", "markets", "collapsed_children"):
        value = node.metrics.get(key)
        if value not in (None, ""):
            metrics.append(f"{escape(str(key))}: {escape(str(value))}")
    metric_line = f"<br><b>Metrics:</b> {' | '.join(metrics[:4])}" if metrics else ""
    motifs = [tag.replace("_", " ").title() for tag in node_pattern_tags(node)]
    motif_line = f"<br><b>Motifs:</b> {escape(', '.join(motifs[:4]))}" if motifs else ""
    quality = _candidate_quality(node)
    quality_line = ""
    if node.kind == "candidate":
        weekly_display = quality.get("pnl_7d_display") or snapshot.get("pnl_7d_display") or "n/a"
        window_display = snapshot.get("pnl_window_display") or "window unknown"
        quality_line = (
            f"<br><b>Atlas quality:</b> {escape(str(quality['label']))} "
            f"({escape(str(quality['score']))}) | P&L/7d {escape(str(weekly_display))} | source {escape(str(quality['pnl_display']))} | {escape(str(window_display))}"
        )
    signature = _node_signature(node, motifs)
    signature_line = f"<br><b>Signature:</b> {escape(signature)}" if signature else ""
    blocker = escape(str(node.blockers[0])[:180]) if node.blockers else ""
    blocker_line = f"<br><b>Primary blocker:</b> {blocker}" if blocker else ""
    return (
        f"<b>{escape(node.label)}</b><br>"
        f"{escape(node.kind)} | {escape(node.family)}<br>"
        f"<b>{escape(label)}</b> | {escape(node.evidence_level)}<br>"
        f"{degree} links{metric_line}{motif_line}{quality_line}{signature_line}{blocker_line}{action_line}<br>"
        f"{summary}"
    )


def _node_signature(node: ProjectNode, motifs: list[str]) -> str:
    metrics = node.metrics or {}
    for key in ("repeat_signature", "strategy_signature", "signature", "decision_signature"):
        value = metrics.get(key)
        if value not in (None, ""):
            return str(value)[:120]
    pieces = [node.family.replace("_", " ")]
    pieces.extend(motif.lower() for motif in motifs[:3])
    if node.status in {"blocked", "rejected"} and node.blockers:
        pieces.append(str(node.blockers[0]).replace("_", " ")[:40])
    return " / ".join(piece for piece in pieces if piece)[:120]


def _node_size(node: ProjectNode, degree: int, selected: bool = False, neighbor: bool = False) -> int:
    if node.kind == "family":
        base = 34
    elif node.kind == "candidate":
        base = max(16, 26 + _candidate_quality_size_delta(node))
    elif node.kind == "health_issue":
        base = 24
    elif node.kind == "secret":
        base = 24
    elif node.kind == "stats":
        base = 19
    elif node.kind in {"report", "dataset"}:
        base = 16
    else:
        collapsed = int(node.metrics.get("collapsed_children", 0) or 0)
        if collapsed:
            base = min(30, 14 + collapsed // 55)
        else:
            base = min(18, 10 + degree // 5)
    if selected:
        return base + 12
    if neighbor:
        return base + 4
    return base


def _important_label(node: ProjectNode, degree: int, label_mode: str, selected: bool = False, neighbor: bool = False) -> bool:
    if label_mode == "minimal":
        return node.kind == "family" or selected
    if label_mode == "essential":
        return node.kind == "family" or selected or node.kind == "candidate" or node.sensitive
    if label_mode == "dense":
        if node.kind in {"family", "candidate", "health_issue", "secret", "stats", "report"}:
            return True
        if node.status in {"strong_candidate", "worth_watching", "blocked"}:
            return True
        return degree >= 7
    if label_mode == "balanced":
        if node.kind in {"family", "candidate", "health_issue", "secret"}:
            return True
        if selected or neighbor:
            return True
        if node.status in {"strong_candidate", "worth_watching", "blocked"}:
            return True
        if EVIDENCE_RANK.get(node.evidence_level, 0) >= EVIDENCE_RANK["live_stats"] and node.kind in {"report", "stats", "dataset"}:
            return True
        return degree >= 12
    if selected or (neighbor and node.kind in {"candidate", "health_issue", "report", "stats", "dataset"}):
        return True
    if node.kind in {"family", "candidate", "health_issue", "secret"}:
        return True
    if node.status in {"strong_candidate", "worth_watching", "blocked"}:
        return True
    if degree >= 10 and node.kind in {"report", "stats", "dataset"}:
        return True
    return False


def _short_label(label: str, limit: int = 30) -> str:
    text = str(label or "")
    return text if len(text) <= limit else text[: limit - 1].rstrip("_-. ") + "..."


def _label_position(x: float, y: float, family_center: tuple[float, float] | None) -> str:
    if not family_center:
        return "top center"
    dx = x - family_center[0]
    dy = y - family_center[1]
    if abs(dx) > abs(dy) * 1.35:
        return "middle right" if dx >= 0 else "middle left"
    return "top center" if dy >= 0 else "bottom center"


def _family_region_profile(family_nodes: list[ProjectNode]) -> tuple[float, int, str]:
    if not family_nodes:
        return 0.035, 1, ""
    blocked = sum(1 for node in family_nodes if node.status in {"blocked", "rejected"} or node.blockers)
    candidates = sum(1 for node in family_nodes if node.kind == "candidate")
    health = sum(1 for node in family_nodes if node.kind == "health_issue" or node.status == "health_issue")
    strong = sum(1 for node in family_nodes if node.status in {"strong_candidate", "worth_watching"})
    evidence = max(EVIDENCE_RANK.get(node.evidence_level, 0) for node in family_nodes)
    intensity = min(0.115, 0.026 + blocked * 0.008 + health * 0.012 + strong * 0.009 + evidence * 0.004)
    width = 1 + min(3, blocked + health + strong + candidates // 3)
    details = []
    if candidates:
        details.append(f"{candidates} cand")
    if strong:
        details.append(f"{strong} watch")
    if blocked or health:
        details.append(f"{blocked} blocked | {health} notices")
    return intensity, width, " | ".join(details[:3])


def _lens_match(node: ProjectNode, lens: str) -> bool:
    if not lens or lens == "default":
        return False
    tags = set(node_pattern_tags(node))
    if lens in {"repeat-risk", "repeat_risk"}:
        return node.status in {"blocked", "rejected"} or bool(node.blockers) or len(tags.intersection({"backtest_replay", "exit_risk", "fill_quality"})) >= 2
    if lens == "frontier":
        return node.status in {"strong_candidate", "worth_watching", "needs_more_proof"} and EVIDENCE_RANK.get(node.evidence_level, 0) >= EVIDENCE_RANK["backtest"]
    if lens == "failure":
        return node.status in {"blocked", "rejected", "health_issue"} or bool(node.blockers) or node.kind == "health_issue"
    if lens == "evidence":
        return EVIDENCE_RANK.get(node.evidence_level, 0) >= EVIDENCE_RANK["live_stats"] or node.kind == "stats"
    return False


def build_figure(nodes: list[ProjectNode], edges: list[ProjectEdge], mode: str = "network", height: int = 680, obsidian: bool = False, label_mode: str = "essential", selected_id: str = "", lens: str = "default") -> go.Figure:
    positions = compute_layout(nodes, edges, mode)
    degree = defaultdict(int)
    neighbors: set[str] = set()
    for edge in edges:
        degree[edge.source] += 1
        degree[edge.target] += 1
        if selected_id and edge.source == selected_id:
            neighbors.add(edge.target)
        if selected_id and edge.target == selected_id:
            neighbors.add(edge.source)

    edge_traces: list[go.Scatter] = []
    focus_edge_x: list[float | None] = []
    focus_edge_y: list[float | None] = []
    edges_by_strength: dict[int, list[ProjectEdge]] = defaultdict(list)
    for edge in edges:
        edges_by_strength[EVIDENCE_RANK.get(edge.evidence_level, 0)].append(edge)
    for strength, grouped_edges in sorted(edges_by_strength.items()):
        edge_x: list[float | None] = []
        edge_y: list[float | None] = []
        for edge in grouped_edges:
            if edge.source not in positions or edge.target not in positions:
                continue
            if selected_id and edge.source != selected_id and edge.target != selected_id and edge.source not in neighbors and edge.target not in neighbors:
                continue
            x0, y0 = positions[edge.source]
            x1, y1 = positions[edge.target]
            if selected_id and (edge.source == selected_id or edge.target == selected_id):
                focus_edge_x.extend([x0, x1, None])
                focus_edge_y.extend([y0, y1, None])
                continue
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        if not edge_x:
            continue
        alpha = (0.18 if selected_id else 0.10) + min(strength, 7) * 0.04
        width = (0.75 if selected_id else 0.42) + min(strength, 7) * 0.18
        edge_traces.append(
            go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                line=dict(width=width, color=f"rgba(164,176,194,{alpha})"),
                hoverinfo="skip",
                showlegend=False,
            )
        )
    if focus_edge_x:
        edge_traces.append(
            go.Scatter(
                x=focus_edge_x,
                y=focus_edge_y,
                mode="lines",
                line=dict(width=3.0, color="rgba(237,242,247,0.72)"),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    family_shapes = []
    family_label_x: list[float] = []
    family_label_y: list[float] = []
    family_label_text: list[str] = []
    family_label_colors: list[str] = []
    family_centers: dict[str, tuple[float, float]] = {}
    if mode == "vault atlas":
        grouped_positions: dict[str, list[tuple[float, float]]] = defaultdict(list)
        for node in nodes:
            if node.id in positions:
                grouped_positions[node.family].append(positions[node.id])
        for family, points in grouped_positions.items():
            if len(points) < 3:
                continue
            family_nodes = [node for node in nodes if node.family == family and node.id in positions]
            xs = [point[0] for point in points]
            ys = [point[1] for point in points]
            center_x = sum(xs) / len(xs)
            center_y = sum(ys) / len(ys)
            family_centers[family] = (center_x, center_y)
            radius = max(max(abs(x - center_x) for x in xs), max(abs(y - center_y) for y in ys)) + 0.35
            color = FAMILY_COLORS.get(family, FAMILY_COLORS["unclassified"])
            region_alpha, region_width, region_detail = _family_region_profile(family_nodes)
            family_label_x.append(center_x)
            family_label_y.append(center_y)
            detail_line = f"<br>{region_detail}" if region_detail else f"<br>{len(points)} nodes"
            family_label_text.append(f"{family.replace('_', ' ').title()}{detail_line}")
            family_label_colors.append(_hex_to_rgba(color, 0.58))
            family_shapes.append(
                dict(
                    type="circle",
                    xref="x",
                    yref="y",
                    x0=center_x - radius,
                    y0=center_y - radius,
                    x1=center_x + radius,
                    y1=center_y + radius,
                    line=dict(color=_hex_to_rgba(color, 0.28 + min(region_width, 4) * 0.045), width=region_width),
                    fillcolor=_hex_to_rgba(color, region_alpha),
                    layer="below",
                )
            )
            family_shapes.append(
                dict(
                    type="circle",
                    xref="x",
                    yref="y",
                    x0=center_x - radius * 1.08,
                    y0=center_y - radius * 1.08,
                    x1=center_x + radius * 1.08,
                    y1=center_y + radius * 1.08,
                    line=dict(color=_hex_to_rgba(color, 0.13 + min(region_width, 4) * 0.025), width=1.4),
                    fillcolor="rgba(0,0,0,0)",
                    layer="below",
                )
            )

    aura_x: list[float] = []
    aura_y: list[float] = []
    aura_colors: list[str] = []
    aura_sizes: list[int] = []
    glow_x: list[float] = []
    glow_y: list[float] = []
    glow_colors: list[str] = []
    glow_sizes: list[int] = []
    evidence_x: list[float] = []
    evidence_y: list[float] = []
    evidence_sizes: list[int] = []
    evidence_line_colors: list[str] = []
    evidence_line_widths: list[float] = []
    focus_x: list[float] = []
    focus_y: list[float] = []
    focus_sizes: list[int] = []
    focus_line_colors: list[str] = []
    focus_line_widths: list[float] = []
    node_x: list[float] = []
    node_y: list[float] = []
    colors: list[str] = []
    sizes: list[int] = []
    symbols: list[str] = []
    opacities: list[float] = []
    glyphs: list[str] = []
    glyph_colors: list[str] = []
    hovertext: list[str] = []
    customdata: list[str] = []
    label_x: list[float] = []
    label_y: list[float] = []
    label_text: list[str] = []
    label_positions: list[str] = []
    label_hovertext: list[str] = []
    label_customdata: list[str] = []
    for node in nodes:
        if node.id not in positions:
            continue
        x, y = positions[node.id]
        color = _candidate_quality_color(node) or STATUS_COLORS.get(node.status, STATUS_COLORS["unknown"])
        family_color = FAMILY_COLORS.get(node.family, FAMILY_COLORS["unclassified"])
        evidence_rank = EVIDENCE_RANK.get(node.evidence_level, 0)
        evidence_color = EVIDENCE_COLORS.get(node.evidence_level, EVIDENCE_COLORS["unknown"])
        selected = node.id == selected_id
        neighbor = node.id in neighbors
        size = _node_size(node, degree[node.id], selected=selected, neighbor=neighbor)
        art_level = _node_art_level(node, degree[node.id], selected=selected, neighbor=neighbor)
        lens_match = _lens_match(node, lens)
        if lens_match:
            art_level = max(art_level, 3)
        highlighted = selected or neighbor or not selected_id
        opacity = _node_opacity(node, selected_id, selected, neighbor)
        if lens_match and not selected_id:
            opacity = max(opacity, 0.96)
        if art_level or node.kind in {"stats", "report", "dataset"}:
            aura_x.append(x)
            aura_y.append(y)
            lens_color = LENS_STATUS_COLORS.get(lens, family_color) if lens_match else family_color
            aura_colors.append(_hex_to_rgba(lens_color, min(0.30, 0.06 + art_level * 0.04)))
            aura_sizes.append(size + 18 + art_level * 5 + (6 if lens_match else 0))
        if art_level >= 2:
            glow_x.append(x)
            glow_y.append(y)
            glow_color = LENS_STATUS_COLORS.get(lens, color) if lens_match else color
            glow_colors.append(_hex_to_rgba(glow_color, 0.38 if selected else 0.28 if neighbor or lens_match else 0.15))
            glow_sizes.append(size + 14 + art_level * 5 + (4 if lens_match else 0))
        evidence_x.append(x)
        evidence_y.append(y)
        evidence_sizes.append(size + 7 + min(evidence_rank, 7))
        evidence_line_colors.append(_hex_to_rgba(evidence_color, 0.92 if highlighted else 0.30))
        evidence_line_widths.append(0.7 + min(evidence_rank, 7) * 0.32 + (1.3 if selected else 0.45 if neighbor else 0.0) + (0.8 if lens_match else 0.0))
        if selected or neighbor:
            focus_x.append(x)
            focus_y.append(y)
            focus_sizes.append(size + (28 if selected else 18))
            focus_line_colors.append(_hex_to_rgba("#edf2f7" if selected else evidence_color, 0.95 if selected else 0.58))
            focus_line_widths.append(3.2 if selected else 1.7)
        node_x.append(x)
        node_y.append(y)
        colors.append(color)
        sizes.append(size)
        symbols.append(KIND_SYMBOLS.get(node.kind, "circle"))
        opacities.append(opacity)
        glyphs.append(KIND_GLYPHS.get(node.kind, "") if size >= 15 else "")
        glyph_colors.append("rgba(6,10,16,0.94)" if node.status not in {"archived", "unknown"} else "rgba(237,242,247,0.76)")
        hovertext.append(_hover_text(node, degree[node.id]))
        customdata.append(node.id)
        if _important_label(node, degree[node.id], label_mode, selected=selected, neighbor=neighbor):
            label_x.append(x)
            label_y.append(y)
            label_text.append(_short_label(node.label, 30))
            label_positions.append(_label_position(x, y, family_centers.get(node.family)))
            label_hovertext.append(_hover_text(node, degree[node.id]))
            label_customdata.append(node.id)
    aura_trace = go.Scatter(
        x=aura_x,
        y=aura_y,
        mode="markers",
        marker=dict(size=aura_sizes, color=aura_colors, symbol="circle", line=dict(width=0)),
        hoverinfo="skip",
        showlegend=False,
    )
    glow_trace = go.Scatter(
        x=glow_x,
        y=glow_y,
        mode="markers",
        marker=dict(size=glow_sizes, color=glow_colors, symbol="circle", line=dict(width=0)),
        hoverinfo="skip",
        showlegend=False,
    )
    evidence_trace = go.Scatter(
        x=evidence_x,
        y=evidence_y,
        mode="markers",
        marker=dict(
            size=evidence_sizes,
            color=["rgba(0,0,0,0)"] * len(evidence_x),
            symbol="circle",
            line=dict(color=evidence_line_colors, width=evidence_line_widths),
        ),
        hoverinfo="skip",
        showlegend=False,
    )
    focus_trace = go.Scatter(
        x=focus_x,
        y=focus_y,
        mode="markers",
        marker=dict(
            size=focus_sizes,
            color=["rgba(0,0,0,0)"] * len(focus_x),
            symbol="circle",
            line=dict(color=focus_line_colors, width=focus_line_widths),
        ),
        hoverinfo="skip",
        showlegend=False,
    )
    label_trace = go.Scatter(
        x=label_x,
        y=label_y,
        mode="text",
        text=label_text,
        textposition=label_positions,
        textfont=dict(size=10, color="rgba(236,244,255,0.82)", family="Inter, Segoe UI, Arial"),
        hovertext=label_hovertext,
        customdata=label_customdata,
        hovertemplate="%{hovertext}<extra></extra>",
        showlegend=False,
    )
    family_label_trace = go.Scatter(
        x=family_label_x,
        y=family_label_y,
        mode="text",
        text=family_label_text,
        textposition="middle center",
        textfont=dict(size=16, color=family_label_colors, family="Inter, Segoe UI, Arial Black"),
        hoverinfo="skip",
        showlegend=False,
    )
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        marker=dict(
            size=sizes,
            color=colors,
            symbol=symbols,
            line=dict(width=[1.9 if symbol in {"star", "hexagon", "x", "cross"} else 1.25 for symbol in symbols], color="rgba(236,244,255,0.80)" if obsidian else "rgba(15,23,42,0.8)"),
            opacity=opacities,
        ),
        text=glyphs,
        textposition="middle center",
        textfont=dict(size=[9 if size < 22 else 10 if size < 30 else 12 for size in sizes], color=glyph_colors, family="Inter, Segoe UI, Arial Black"),
        hovertext=hovertext,
        customdata=customdata,
        hovertemplate="%{hovertext}<extra></extra>",
        showlegend=False,
    )
    fig = go.Figure(data=[*edge_traces, family_label_trace, aura_trace, glow_trace, evidence_trace, focus_trace, label_trace, node_trace])
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False),
        plot_bgcolor="#080a0d" if obsidian else "#08111f",
        paper_bgcolor="#080a0d" if obsidian else "#08111f",
        dragmode="pan",
        shapes=family_shapes,
        hoverlabel=dict(
            bgcolor="rgba(10,14,20,0.96)",
            bordercolor="rgba(236,244,255,0.28)",
            font=dict(color="#edf2f7", size=12, family="Inter, Segoe UI, Arial"),
            align="left",
        ),
    )
    return fig


def registry_lookup(registry: ProjectRegistry) -> tuple[dict[str, ProjectNode], list[ProjectEdge]]:
    return {node.id: node for node in registry.nodes}, registry.edges
