from __future__ import annotations

import base64
from collections import Counter, defaultdict
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from project_os import patterns as pattern_model
from project_os.family import EVIDENCE_RANK, STATUS_LABELS
from project_os.graph import build_figure, collapse_graph, registry_lookup
from project_os.models import ProjectEdge, ProjectNode, ProjectRegistry
from project_os.patterns import family_pattern_rows, frontier_cards, lineage_gap_rows, motif_summaries, node_pattern_tags, positive_blocked_rows, repetition_clusters
from project_os.registry import load_or_build_registry


STATUS_ORDER = [
    "strong_candidate",
    "worth_watching",
    "active",
    "needs_more_proof",
    "blocked",
    "diagnostic_only",
    "rejected",
    "archived",
    "unknown",
    "health_issue",
]

STATUS_PRIORITY = {
    "strong_candidate": 100,
    "worth_watching": 92,
    "active": 82,
    "needs_more_proof": 72,
    "blocked": 42,
    "diagnostic_only": 32,
    "rejected": 18,
    "archived": 10,
    "unknown": 5,
    "health_issue": 0,
}

STATUS_COLORS = {
    "strong_candidate": "#21c87a",
    "worth_watching": "#8bd450",
    "active": "#36c2ff",
    "needs_more_proof": "#f4b942",
    "blocked": "#ff6b4a",
    "diagnostic_only": "#b794f4",
    "rejected": "#ef4444",
    "archived": "#7b8794",
    "unknown": "#687385",
    "health_issue": "#f59e0b",
}

EVIDENCE_COLORS = {
    "live_forward": "#21c87a",
    "forward_shadow": "#36c2ff",
    "live_stats": "#2dd4bf",
    "replay": "#b794f4",
    "backtest": "#f4b942",
    "diagnostic": "#9aa6b2",
    "metadata_only": "#687385",
    "unknown": "#485363",
}

FAMILY_COLORS = {
    "rv600": "#36c2ff",
    "v28_successor": "#b794f4",
    "live_v28": "#21c87a",
    "ou_mispricing": "#f4b942",
    "truffle": "#ff8a4c",
    "ninety_touch": "#2dd4bf",
    "particle_sim": "#eab308",
    "strategy_research": "#c084fc",
    "legacy_live": "#14b8a6",
    "research_os": "#60a5fa",
    "dashboard_ui": "#f472b6",
    "infrastructure": "#7b8794",
    "unclassified": "#9aa6b2",
}


def _safe_metric(metrics: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in metrics and metrics[name] not in (None, ""):
            return metrics[name]
    return ""


def _safe_numeric(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    try:
        text = str(value).strip().replace(",", "").replace("$", "").replace("%", "")
        if text.startswith("(") and text.endswith(")"):
            text = "-" + text[1:-1]
        return float(text)
    except (TypeError, ValueError):
        return 0.0


def _pnl_sort_value(metrics: dict[str, Any]) -> float:
    if "net_pnl" in metrics and metrics["net_pnl"] not in (None, ""):
        value = _safe_numeric(metrics["net_pnl"])
        if "cent" in str(metrics.get("net_pnl_unit_hint") or metrics.get("net_pnl_source_key") or "").lower():
            return value / 100.0
        return value
    if "selected_pnl" in metrics and metrics["selected_pnl"] not in (None, ""):
        return _safe_numeric(metrics["selected_pnl"])
    if "selected_pnl_cents" in metrics and metrics["selected_pnl_cents"] not in (None, ""):
        return _safe_numeric(metrics["selected_pnl_cents"]) / 100.0
    return 0.0


def _pnl_7d_sort_value(metrics: dict[str, Any]) -> float:
    for key in ("pnl_7d_dollars", "projected_pnl_7d_dollars", "actual_pnl_7d_dollars"):
        if key in metrics and metrics[key] not in (None, ""):
            return _safe_numeric(metrics[key])
    return _pnl_sort_value(metrics)


def _pnl_display(metrics: dict[str, Any]) -> str:
    if "net_pnl" in metrics and metrics["net_pnl"] not in (None, ""):
        value = _safe_numeric(metrics["net_pnl"])
        unit_text = str(metrics.get("net_pnl_unit_hint") or metrics.get("net_pnl_source_key") or "").lower()
        if "cent" in unit_text:
            return f"{value:,.0f}c (~${value / 100.0:,.2f})"
        if "dollar" in unit_text or "usd" in unit_text:
            return f"${value:,.2f}"
        return f"{metrics['net_pnl']} raw"
    if "selected_pnl" in metrics and metrics["selected_pnl"] not in (None, ""):
        return str(metrics["selected_pnl"])
    if "selected_pnl_cents" in metrics and metrics["selected_pnl_cents"] not in (None, ""):
        return f"{_safe_numeric(metrics['selected_pnl_cents']) / 100.0:,.2f}"
    if metrics.get("pnl_status") or metrics.get("pnl_missing_reason"):
        return "n/a"
    return ""


def _pnl_7d_display(metrics: dict[str, Any]) -> str:
    display = str(metrics.get("pnl_7d_display") or "")
    if display:
        return display
    for key in ("pnl_7d_dollars", "projected_pnl_7d_dollars", "actual_pnl_7d_dollars"):
        if key in metrics and metrics[key] not in (None, ""):
            return f"${_safe_numeric(metrics[key]):,.2f}"
    return ""


def _pnl_window_display(metrics: dict[str, Any]) -> str:
    days = metrics.get("pnl_observed_window_days")
    if days in (None, ""):
        return ""
    numeric = _safe_numeric(days)
    label = f"{numeric:g}d" if numeric >= 1 else f"{numeric * 24:g}h"
    confidence = str(metrics.get("pnl_observed_window_confidence") or "")
    return f"{label} ({confidence})" if confidence else label


def _short(value: Any, limit: int = 140) -> str:
    text = str(value or "").replace("\n", " ").strip()
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def _format_bytes(value: int | None) -> str:
    if value is None:
        return ""
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:,.1f} {unit}" if unit != "B" else f"{int(size):,} B"
        size /= 1024
    return f"{size:,.1f} TB"


def _display_df(rows: list[dict[str, Any]] | pd.DataFrame) -> pd.DataFrame:
    df = rows.copy() if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    if df.empty:
        return df
    for column in df.columns:
        if df[column].dtype == "object":
            df[column] = df[column].map(lambda value: "" if value is None else str(value))
    return df


def _pattern_table(name: str, registry: ProjectRegistry, fallback: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    fn = getattr(pattern_model, name, None)
    if callable(fn):
        try:
            rows = fn(registry)
            return list(rows or [])
        except Exception as exc:
            return [{"Lane": "Needs Repair", "Title": name, "Signal": "Pattern function failed", "Why": _short(exc, 140), "Next Action": "Fix Research OS pattern analysis before using this row.", "Risk": "dashboard fallback"}]
    return list(fallback or [])


def _metric_snapshot(node: ProjectNode) -> dict[str, Any]:
    fn = getattr(pattern_model, "normalized_metric_snapshot", None)
    if callable(fn):
        try:
            return dict(fn(node) or {})
        except Exception:
            pass
    pnl = _pnl_sort_value(node.metrics)
    display = _pnl_display(node.metrics)
    weekly_display = _pnl_7d_display(node.metrics)
    has_any_pnl = display != "" or weekly_display != ""
    return {
        "pnl_value": pnl if has_any_pnl else None,
        "pnl_display": display,
        "pnl_7d_value": _pnl_7d_sort_value(node.metrics) if has_any_pnl else None,
        "pnl_7d_display": weekly_display,
        "pnl_window_display": _pnl_window_display(node.metrics),
        "pnl_standardization_status": node.metrics.get("pnl_standardization_status") or "",
        "pnl_unit": "unknown",
        "pnl_key": "",
        "pnl_confidence": "fallback",
        "entries": _safe_metric(node.metrics, "entries"),
        "markets": _safe_metric(node.metrics, "markets"),
        "roots": _safe_metric(node.metrics, "roots", "positive_roots"),
        "win_rate": _safe_metric(node.metrics, "win_rate"),
        "metric_warnings": ["Fallback metric display; unit provenance unavailable."] if display != "" else [],
    }


def _candidate_signature(node: ProjectNode) -> str:
    fn = getattr(pattern_model, "candidate_signature", None)
    if callable(fn):
        try:
            return str(fn(node) or "")
        except Exception:
            return ""
    motifs = "+".join(node_pattern_tags(node))
    return "|".join(part for part in [node.family, node.kind, node.evidence_level, motifs] if part)


def _nearest_prior_for(node: ProjectNode, registry: ProjectRegistry) -> dict[str, Any] | None:
    rows = _pattern_table("nearest_prior_rows", registry)
    for row in rows:
        if str(row.get("Label", "")) == node.label and str(row.get("Family", "")) == node.family and str(row.get("Kind", "")) == node.kind:
            return row
    return None


def _positive_blocked_for(node: ProjectNode, registry: ProjectRegistry) -> dict[str, Any] | None:
    for row in _pattern_table("positive_blocked_rows", registry, positive_blocked_rows(registry)):
        if str(row.get("Label", "")) == node.label and str(row.get("Family", "")) == node.family:
            return row
    return None


def _family_gap_lookup(registry: ProjectRegistry) -> dict[str, dict[str, Any]]:
    return {str(row.get("Family", "")): row for row in _pattern_table("family_gap_rows", registry, family_pattern_rows(registry))}


def _failure_motif_lookup(registry: ProjectRegistry) -> dict[str, list[dict[str, Any]]]:
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in _pattern_table("failure_motif_rows", registry):
        by_family[str(row.get("Family", ""))].append(row)
    return by_family


def _decision_summary_for(node: ProjectNode, trap: dict[str, Any] | None, nearest: dict[str, Any] | None) -> str:
    if trap:
        return "Do not repeat unchanged; resolve the blocker or pre-register a materially different assumption."
    if node.blockers or node.status in {"blocked", "rejected"}:
        return "Repair blocker lineage or archive unless a new assumption is explicit."
    if node.status == "diagnostic_only" or node.evidence_level in {"backtest", "replay", "diagnostic"}:
        return "Collect forward evidence before treating this as more than a hypothesis clue."
    if nearest and "nothing" in str(nearest.get("Repeat Warning", "")).lower():
        return "Changed assumption is unclear; compare against the nearest prior before another run."
    if node.status in {"strong_candidate", "worth_watching", "active"} and EVIDENCE_RANK.get(node.evidence_level, 0) >= EVIDENCE_RANK["forward_shadow"]:
        return "Test next in research/shadow workflow with blockers and baseline comparison visible."
    if node.kind == "candidate":
        return "Collect more forward evidence and complete lineage classification."
    if node.kind in {"report", "stats"}:
        return "Link this evidence to the candidate/family decision it supports or blocks."
    return "Classify this node before using it in a research decision."


def _snapshot_count(registry_dir: Path) -> int:
    if not registry_dir.exists():
        return 0
    return sum(1 for path in registry_dir.glob("registry_*.json") if path.name != "registry_latest.json")


def _status_label(status: str) -> str:
    return STATUS_LABELS.get(status, status.replace("_", " ").title())


def _evidence_label(evidence: str) -> str:
    return evidence.replace("_", " ").title()


def _pill(label: str, color: str, title: str | None = None) -> str:
    label_html = escape(label)
    title_attr = f' title="{escape(title)}"' if title else ""
    return f'<span class="os-pill" style="--pill:{color};"{title_attr}>{label_html}</span>'


def _status_pill(status: str) -> str:
    return _pill(_status_label(status), STATUS_COLORS.get(status, STATUS_COLORS["unknown"]))


def _evidence_pill(evidence: str) -> str:
    return _pill(_evidence_label(evidence), EVIDENCE_COLORS.get(evidence, EVIDENCE_COLORS["unknown"]))


def _family_pill(family: str) -> str:
    return _pill(family.replace("_", " ").title(), FAMILY_COLORS.get(family, "#9aa6b2"))


def _node_rows(nodes: list[ProjectNode]) -> list[dict[str, Any]]:
    rows = []
    for node in nodes:
        rows.append(
            {
                "Label": node.label,
                "Kind": node.kind,
                "Family": node.family,
                "Status": _status_label(node.status),
                "Evidence": _evidence_label(node.evidence_level),
                "P&L/7d": _pnl_7d_display(node.metrics),
                "P&L": _pnl_display(node.metrics),
                "Window": _pnl_window_display(node.metrics),
                "Entries": _safe_metric(node.metrics, "entries"),
                "Markets": _safe_metric(node.metrics, "markets"),
                "Updated": node.updated_at_utc or "",
                "Sensitive": "yes" if node.sensitive else "",
                "Path": node.path or "",
                "Summary": node.summary,
                "id": node.id,
            }
        )
    return rows


def _filter_nodes(
    nodes: list[ProjectNode],
    search: str,
    families: list[str],
    statuses: list[str],
    kinds: list[str],
    evidence: list[str],
    show_health: bool,
    show_unknown: bool,
    show_sensitive: bool,
    show_archives: bool,
) -> list[ProjectNode]:
    search_l = search.lower().strip()
    output = []
    for node in nodes:
        if families and node.family not in families:
            continue
        if statuses and node.status not in statuses:
            continue
        if kinds and node.kind not in kinds:
            continue
        if evidence and node.evidence_level not in evidence:
            continue
        if not show_health and node.kind == "health_issue":
            continue
        if not show_unknown and (node.kind == "unknown" or node.family == "unclassified" or node.status == "unknown"):
            continue
        if not show_sensitive and node.sensitive:
            continue
        if not show_archives and (node.kind == "archive" or node.status == "archived"):
            continue
        haystack = " ".join([node.id, node.label, node.family, node.kind, node.status, node.summary, node.path or ""]).lower()
        if search_l and search_l not in haystack:
            continue
        output.append(node)
    return output


def _edges_for_nodes(edges: list[ProjectEdge], visible_ids: set[str]) -> list[ProjectEdge]:
    return [edge for edge in edges if edge.source in visible_ids and edge.target in visible_ids]


def _incoming_outgoing(node_id: str, edges: list[ProjectEdge]) -> tuple[list[ProjectEdge], list[ProjectEdge]]:
    incoming = [edge for edge in edges if edge.target == node_id]
    outgoing = [edge for edge in edges if edge.source == node_id]
    return incoming, outgoing


def _select_node_from_event(event: Any) -> str | None:
    try:
        points = event.get("selection", {}).get("points", [])
    except AttributeError:
        points = getattr(getattr(event, "selection", None), "points", []) if event is not None else []
    if not points:
        return None
    point = points[0]
    if isinstance(point, dict):
        return point.get("customdata")
    return getattr(point, "customdata", None)


def _candidate_nodes(registry: ProjectRegistry) -> list[ProjectNode]:
    candidates = [node for node in registry.nodes if node.kind == "candidate"]
    return sorted(
        candidates,
        key=lambda node: (
            STATUS_PRIORITY.get(node.status, 0),
            EVIDENCE_RANK.get(node.evidence_level, 0),
            _pnl_7d_sort_value(node.metrics),
            node.updated_at_utc or "",
        ),
        reverse=True,
    )


def _decision_nodes(registry: ProjectRegistry) -> list[ProjectNode]:
    nodes = [node for node in registry.nodes if node.kind in {"candidate", "report", "stats"}]
    return sorted(
        nodes,
        key=lambda node: (
            STATUS_PRIORITY.get(node.status, 0),
            EVIDENCE_RANK.get(node.evidence_level, 0),
            _pnl_7d_sort_value(node.metrics),
            node.updated_at_utc or "",
        ),
        reverse=True,
    )


def _best_default_node(registry: ProjectRegistry) -> str:
    for node in _candidate_nodes(registry):
        if node.status in {"strong_candidate", "worth_watching", "needs_more_proof", "active"}:
            return node.id
    for node in registry.nodes:
        if node.kind == "family":
            return node.id
    return registry.nodes[0].id if registry.nodes else ""


def _family_summary_rows(registry: ProjectRegistry) -> list[dict[str, Any]]:
    by_family: dict[str, list[ProjectNode]] = defaultdict(list)
    for node in registry.nodes:
        by_family[node.family or "unclassified"].append(node)

    family_nodes = {node.family: node for node in registry.nodes if node.kind == "family"}
    rows = []
    for family, nodes in sorted(by_family.items()):
        if family == "":
            continue
        status_counts = Counter(node.status for node in nodes)
        best_evidence = max((node.evidence_level for node in nodes), key=lambda item: EVIDENCE_RANK.get(item, 0), default="unknown")
        newest = max([node.updated_at_utc for node in nodes if node.updated_at_utc] or [""])
        family_node = family_nodes.get(family)
        top_blocker = next((node.blockers[0] for node in nodes if node.blockers), "")
        rows.append(
            {
                "Family": family,
                "Status": family_node.status if family_node else status_counts.most_common(1)[0][0],
                "Nodes": len(nodes),
                "Candidates": sum(1 for node in nodes if node.kind == "candidate"),
                "Reports": sum(1 for node in nodes if node.kind == "report"),
                "Stats": sum(1 for node in nodes if node.kind == "stats"),
                "Health": sum(1 for node in nodes if node.kind == "health_issue"),
                "Best Evidence": best_evidence,
                "Latest": newest[:16].replace("T", " ") if newest else "",
                "Action": _short(top_blocker or (family_node.next_action if family_node else "Classify family evidence."), 110),
                "id": family_node.id if family_node else f"family:{family}",
            }
        )
    return sorted(rows, key=lambda row: (row["Health"], row["Candidates"], row["Nodes"]), reverse=True)


def _candidate_rows(nodes: list[ProjectNode]) -> list[dict[str, Any]]:
    rows = []
    for node in nodes:
        snapshot = _metric_snapshot(node)
        warnings = snapshot.get("metric_warnings") or []
        rows.append(
            {
                "Candidate": node.label,
                "Family": node.family,
                "Status": _status_label(node.status),
                "Evidence": _evidence_label(node.evidence_level),
                "Frozen": "yes" if node.metrics.get("frozen") else "",
                "P&L/7d": snapshot.get("pnl_7d_display") or "",
                "P&L": snapshot.get("pnl_display") or "",
                "Window": snapshot.get("pnl_window_display") or "",
                "P&L Source": snapshot.get("pnl_key") or "",
                "P&L Standardized": snapshot.get("pnl_standardization_status") or "",
                "P&L Status": snapshot.get("pnl_status") or "",
                "Confidence": snapshot.get("pnl_confidence") or "",
                "Markets": snapshot.get("markets") or "",
                "Entries": snapshot.get("entries") or "",
                "Win Rate": snapshot.get("win_rate") or "",
                "Warnings": _short("; ".join(str(item) for item in warnings), 120),
                "Blocker": _short(node.blockers[0] if node.blockers else "", 120),
                "Next Action": _short(node.next_action, 130),
                "Updated": (node.updated_at_utc or "")[:16].replace("T", " "),
                "id": node.id,
            }
        )
    return rows


def _latest_artifacts(registry: ProjectRegistry, limit: int = 18) -> list[ProjectNode]:
    artifact_kinds = {"report", "dataset", "stats", "doc", "log", "script", "artifact", "archive", "secret", "unknown"}
    nodes = [node for node in registry.nodes if node.kind in artifact_kinds and node.updated_at_utc]
    return sorted(nodes, key=lambda node: node.updated_at_utc or "", reverse=True)[:limit]


def _health_nodes(registry: ProjectRegistry) -> list[ProjectNode]:
    issue_ids = {issue.id for issue in registry.issues}
    nodes = [node for node in registry.nodes if node.kind == "health_issue" or node.id in issue_ids]
    return sorted(nodes, key=lambda node: (node.sensitive, node.updated_at_utc or "", node.label), reverse=True)


def _coverage_dataframe(registry: ProjectRegistry) -> pd.DataFrame:
    families = sorted({node.family for node in registry.nodes})
    levels = ["live_forward", "forward_shadow", "live_stats", "replay", "backtest", "diagnostic", "metadata_only", "unknown"]
    rows = []
    for family in families:
        family_nodes = [node for node in registry.nodes if node.family == family]
        row = {"Family": family}
        counts = Counter(node.evidence_level for node in family_nodes)
        for level in levels:
            row[_evidence_label(level)] = counts.get(level, 0)
        rows.append(row)
    return pd.DataFrame(rows)


def _status_dataframe(registry: ProjectRegistry) -> pd.DataFrame:
    families = sorted({node.family for node in registry.nodes})
    statuses = [status for status in STATUS_ORDER if any(node.status == status for node in registry.nodes)]
    rows = []
    for family in families:
        family_nodes = [node for node in registry.nodes if node.family == family]
        counts = Counter(node.status for node in family_nodes)
        for status in statuses:
            rows.append({"Family": family, "Status": _status_label(status), "Count": counts.get(status, 0), "Raw": status})
    return pd.DataFrame(rows)


def _evidence_figure(registry: ProjectRegistry) -> go.Figure:
    df = _coverage_dataframe(registry)
    fig = go.Figure()
    for level in ["Live Forward", "Forward Shadow", "Live Stats", "Replay", "Backtest", "Diagnostic", "Metadata Only", "Unknown"]:
        fig.add_trace(
            go.Bar(
                y=df["Family"],
                x=df[level],
                name=level,
                orientation="h",
                marker_color=EVIDENCE_COLORS.get(level.lower().replace(" ", "_"), "#687385"),
                hovertemplate="%{y}<br>" + level + ": %{x}<extra></extra>",
            )
        )
    fig.update_layout(
        barmode="stack",
        height=290,
        margin=dict(l=8, r=8, t=6, b=8),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.18, x=0, font=dict(size=10)),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, title=""),
        font=dict(color="#d6dee9", size=11),
    )
    return fig


def _status_figure(registry: ProjectRegistry) -> go.Figure:
    df = _status_dataframe(registry)
    fig = go.Figure()
    for status in [status for status in STATUS_ORDER if status in set(df["Raw"])]:
        work = df[df["Raw"] == status]
        fig.add_trace(
            go.Bar(
                y=work["Family"],
                x=work["Count"],
                name=_status_label(status),
                orientation="h",
                marker_color=STATUS_COLORS.get(status, STATUS_COLORS["unknown"]),
                hovertemplate="%{y}<br>" + _status_label(status) + ": %{x}<extra></extra>",
            )
        )
    fig.update_layout(
        barmode="stack",
        height=290,
        margin=dict(l=8, r=8, t=6, b=8),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.18, x=0, font=dict(size=10)),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, title=""),
        font=dict(color="#d6dee9", size=11),
    )
    return fig


def _render_css() -> None:
    css = """
        :root {
            --os-bg: #0b0d10;
            --os-panel: #12161d;
            --os-panel-2: #171c24;
            --os-panel-3: #0f1319;
            --os-line: rgba(164, 176, 194, 0.18);
            --os-line-strong: rgba(164, 176, 194, 0.28);
            --os-text: #edf2f7;
            --os-muted: #98a5b6;
            --os-dim: #687385;
            --os-green: #21c87a;
            --os-cyan: #36c2ff;
            --os-amber: #f4b942;
            --os-red: #ff4d6d;
            --os-violet: #b794f4;
        }
        .stApp {
            background:
                linear-gradient(rgba(164, 176, 194, 0.028) 1px, transparent 1px),
                linear-gradient(90deg, rgba(164, 176, 194, 0.022) 1px, transparent 1px),
                linear-gradient(180deg, #0a0c0f 0%, #0b0d10 48%, #101216 100%);
            background-size: 24px 24px, 24px 24px, auto;
            color: var(--os-text);
        }
        .block-container {
            max-width: 1880px;
            padding: 0.75rem 1.25rem 2rem;
        }
        #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
            visibility: hidden;
            height: 0;
        }
        .modebar, .modebar-container {
            display: none !important;
        }
        h1, h2, h3, h4, p, span, label, div {
            letter-spacing: 0;
        }
        [data-testid="stMetric"] {
            background: transparent;
            border: 0;
            padding: 0;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.1rem;
        }
        [data-testid="stDataFrame"] {
            border: 1px solid var(--os-line);
            border-radius: 8px;
            overflow: hidden;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--os-line);
            border-radius: 8px;
            background: linear-gradient(180deg, rgba(23, 28, 36, 0.94), rgba(15, 19, 25, 0.95));
            box-shadow: 0 20px 60px rgba(0,0,0,0.18);
        }
        .stButton > button {
            border-radius: 8px;
            border: 1px solid rgba(54, 194, 255, 0.42);
            background: linear-gradient(180deg, rgba(54, 194, 255, 0.20), rgba(54, 194, 255, 0.08));
            color: var(--os-text);
            font-weight: 650;
        }
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stMultiSelect div[data-baseweb="select"] > div {
            border-radius: 8px;
            background-color: rgba(18, 22, 29, 0.92);
            border-color: var(--os-line-strong);
        }
        .os-topbar {
            position: sticky;
            top: 0;
            z-index: 50;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.85rem 1rem;
            margin: -0.35rem 0 0.8rem;
            background: rgba(11, 13, 16, 0.88);
            backdrop-filter: blur(18px);
            border: 1px solid var(--os-line);
            border-radius: 8px;
            box-shadow: 0 18px 50px rgba(0,0,0,0.28);
        }
        .os-title {
            font-size: 1.35rem;
            line-height: 1.15;
            font-weight: 760;
            margin: 0;
        }
        .os-subtitle {
            margin-top: 0.2rem;
            color: var(--os-muted);
            font-size: 0.82rem;
            max-width: 68rem;
        }
        .os-chip-row {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
            align-items: center;
            justify-content: flex-end;
        }
        .os-chip {
            display: inline-flex;
            align-items: center;
            min-height: 1.65rem;
            padding: 0.22rem 0.55rem;
            border: 1px solid var(--os-line);
            border-radius: 999px;
            color: #d8e0ea;
            background: rgba(23, 28, 36, 0.86);
            font-size: 0.76rem;
            white-space: nowrap;
        }
        .os-chip strong {
            color: var(--os-text);
            font-weight: 750;
            margin-right: 0.25rem;
        }
        .os-warning {
            border: 1px solid rgba(244, 185, 66, 0.34);
            border-left: 4px solid var(--os-amber);
            border-radius: 8px;
            background: rgba(244, 185, 66, 0.08);
            padding: 0.72rem 0.85rem;
            color: #ffe6aa;
            font-size: 0.86rem;
            margin: 0.65rem 0 0.9rem;
        }
        .os-section {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 0.75rem;
            margin: 1rem 0 0.55rem;
        }
        .os-section h2 {
            margin: 0;
            font-size: 1.05rem;
            line-height: 1.18;
            font-weight: 780;
        }
        .os-section p {
            margin: 0.12rem 0 0;
            color: var(--os-muted);
            font-size: 0.78rem;
        }
        .os-section-tag {
            color: #cbd5e1;
            border: 1px solid var(--os-line);
            border-radius: 999px;
            background: rgba(18, 22, 29, 0.78);
            padding: 0.22rem 0.58rem;
            font-size: 0.72rem;
            white-space: nowrap;
        }
        .os-panel {
            border: 1px solid var(--os-line);
            border-radius: 8px;
            background: linear-gradient(180deg, rgba(23, 28, 36, 0.94), rgba(15, 19, 25, 0.95));
            padding: 0.9rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.20);
            min-height: 100%;
        }
        .os-panel-title {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 0.6rem;
            margin-bottom: 0.65rem;
        }
        .os-panel-title h3 {
            font-size: 0.98rem;
            margin: 0;
            font-weight: 740;
        }
        .os-panel-title span {
            color: var(--os-muted);
            font-size: 0.76rem;
        }
        .os-atlas-intro {
            border: 1px solid rgba(54, 194, 255, 0.22);
            border-radius: 8px;
            background: linear-gradient(90deg, rgba(54, 194, 255, 0.10), rgba(183, 148, 244, 0.07), rgba(8, 10, 13, 0.88));
            padding: 0.82rem 0.9rem;
            margin-bottom: 0.75rem;
            color: #dce7f4;
            font-size: 0.82rem;
        }
        .os-control-strip {
            border: 1px solid var(--os-line);
            border-radius: 8px;
            background: rgba(8, 10, 13, 0.58);
            padding: 0.65rem 0.7rem 0.25rem;
            margin-bottom: 0.7rem;
        }
        .os-legend-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.4rem;
            margin-top: 0.45rem;
        }
        .os-legend-item {
            display: flex;
            align-items: center;
            gap: 0.42rem;
            color: var(--os-muted);
            font-size: 0.73rem;
        }
        .os-dot {
            width: 0.72rem;
            height: 0.72rem;
            border-radius: 999px;
            background: var(--dot);
            box-shadow: 0 0 14px color-mix(in srgb, var(--dot), transparent 40%);
        }
        .os-node-demo {
            position: relative;
            width: 1rem;
            height: 1rem;
            border-radius: 999px;
            background: var(--core);
            border: 2px solid var(--ring);
            box-shadow: 0 0 0 5px color-mix(in srgb, var(--family), transparent 82%), 0 0 18px color-mix(in srgb, var(--core), transparent 52%);
            flex: 0 0 1rem;
        }
        .os-node-demo.os-star {
            clip-path: polygon(50% 0%, 61% 34%, 98% 34%, 68% 55%, 79% 91%, 50% 70%, 21% 91%, 32% 55%, 2% 34%, 39% 34%);
        }
        .os-node-demo.os-diamond {
            border-radius: 2px;
            transform: rotate(45deg);
        }
        .os-node-demo.os-open {
            background: transparent;
        }
        .os-kpi-grid {
            display: grid;
            grid-template-columns: repeat(8, minmax(0, 1fr));
            gap: 0.55rem;
            margin-bottom: 0.85rem;
        }
        .os-kpi {
            border: 1px solid var(--os-line);
            border-radius: 8px;
            background: rgba(18, 22, 29, 0.92);
            padding: 0.7rem 0.75rem;
            min-height: 5.1rem;
            transition: border-color 120ms ease, transform 120ms ease, background 120ms ease;
        }
        .os-kpi:hover {
            border-color: rgba(236, 244, 255, 0.30);
            background: rgba(23, 28, 36, 0.96);
            transform: translateY(-1px);
        }
        .os-kpi-label {
            color: var(--os-muted);
            font-size: 0.72rem;
            margin-bottom: 0.28rem;
        }
        .os-kpi-value {
            color: var(--os-text);
            font-size: 1.42rem;
            line-height: 1.05;
            font-weight: 780;
        }
        .os-kpi-note {
            color: var(--os-muted);
            font-size: 0.72rem;
            margin-top: 0.34rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .os-card-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(13rem, 1fr));
            gap: 0.55rem;
            margin-bottom: 0.85rem;
        }
        .os-card {
            border: 1px solid var(--os-line);
            border-radius: 8px;
            background: rgba(18, 22, 29, 0.76);
            padding: 0.72rem;
            min-height: 9.5rem;
            transition: border-color 120ms ease, transform 120ms ease, background 120ms ease;
        }
        .os-card:hover {
            border-color: rgba(236, 244, 255, 0.30);
            background: rgba(23, 28, 36, 0.96);
            transform: translateY(-1px);
        }
        .os-card h4 {
            margin: 0 0 0.35rem;
            font-size: 0.86rem;
            line-height: 1.24;
            font-weight: 720;
            color: var(--os-text);
            overflow-wrap: anywhere;
        }
        .os-card-meta {
            display: flex;
            gap: 0.35rem;
            flex-wrap: wrap;
            margin-bottom: 0.45rem;
        }
        .os-card-line {
            color: var(--os-muted);
            font-size: 0.74rem;
            margin-top: 0.28rem;
            overflow-wrap: anywhere;
        }
        .os-card-action {
            color: #d8e0ea;
            border-top: 1px solid var(--os-line);
            padding-top: 0.48rem;
            margin-top: 0.5rem;
            font-size: 0.76rem;
            overflow-wrap: anywhere;
        }
        .os-pattern-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.6rem;
            margin: 0.65rem 0 0.95rem;
        }
        .os-pattern-card {
            border: 1px solid color-mix(in srgb, var(--accent), transparent 62%);
            border-radius: 8px;
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--accent), transparent 88%), rgba(18, 22, 29, 0.92)),
                rgba(18, 22, 29, 0.92);
            padding: 0.75rem;
            min-height: 8.5rem;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02), 0 18px 40px rgba(0,0,0,0.16);
        }
        .os-pattern-lane {
            color: color-mix(in srgb, var(--accent), white 24%);
            font-size: 0.68rem;
            font-weight: 750;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }
        .os-pattern-title {
            color: var(--os-text);
            font-size: 0.88rem;
            font-weight: 760;
            line-height: 1.2;
            overflow-wrap: anywhere;
        }
        .os-pattern-signal {
            color: var(--os-muted);
            font-size: 0.72rem;
            margin-top: 0.42rem;
            overflow-wrap: anywhere;
        }
        .os-pattern-line {
            color: #cbd5e1;
            font-size: 0.73rem;
            margin-top: 0.4rem;
            line-height: 1.28;
            overflow-wrap: anywhere;
        }
        .os-pattern-move {
            color: #dce7f4;
            border-top: 1px solid var(--os-line);
            padding-top: 0.48rem;
            margin-top: 0.55rem;
            font-size: 0.75rem;
            line-height: 1.28;
            overflow-wrap: anywhere;
        }
        .os-now-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.55rem;
            margin: 0.75rem 0 0.95rem;
        }
        .os-now-grid.os-now-rail {
            grid-template-columns: 1fr;
            margin: 0.15rem 0 0.65rem;
        }
        .os-now-card {
            border: 1px solid var(--os-line);
            border-radius: 8px;
            background: linear-gradient(180deg, rgba(18, 22, 29, 0.90), rgba(12, 15, 20, 0.90));
            padding: 0.78rem;
            min-height: 7rem;
            border-top: 3px solid var(--accent);
        }
        .os-now-grid.os-now-rail .os-now-card {
            min-height: 0;
            padding: 0.64rem;
        }
        .os-now-label {
            color: var(--os-muted);
            font-size: 0.72rem;
            margin-bottom: 0.35rem;
        }
        .os-now-title {
            color: var(--os-text);
            font-size: 0.9rem;
            line-height: 1.2;
            font-weight: 740;
            overflow-wrap: anywhere;
        }
        .os-now-note {
            color: var(--os-muted);
            font-size: 0.73rem;
            margin-top: 0.35rem;
            overflow-wrap: anywhere;
        }
        .os-ribbon-grid {
            display: grid;
            grid-template-columns: repeat(7, minmax(0, 1fr));
            gap: 0.55rem;
            margin: 0.7rem 0 0.95rem;
        }
        .os-candidate-ribbon {
            grid-template-columns: repeat(8, minmax(0, 1fr));
        }
        .os-ribbon-card {
            border: 1px solid var(--os-line);
            border-radius: 8px;
            background: rgba(18, 22, 29, 0.82);
            padding: 0.7rem;
            min-height: 7rem;
            border-top: 3px solid var(--accent);
            transition: border-color 120ms ease, transform 120ms ease, background 120ms ease;
        }
        .os-ribbon-card:hover {
            border-color: rgba(236, 244, 255, 0.30);
            background: rgba(23, 28, 36, 0.96);
            transform: translateY(-1px);
        }
        .os-ribbon-title {
            color: var(--os-text);
            font-weight: 760;
            font-size: 0.84rem;
            line-height: 1.18;
            overflow-wrap: anywhere;
        }
        .os-ribbon-meta {
            color: var(--os-muted);
            font-size: 0.7rem;
            margin-top: 0.34rem;
            overflow-wrap: anywhere;
        }
        .os-atlas-frame {
            border: 1px solid rgba(54, 194, 255, 0.18);
            border-radius: 8px;
            background: linear-gradient(180deg, rgba(8, 10, 13, 0.92), rgba(11, 13, 16, 0.96));
            padding: 0.25rem;
        }
        .os-pill {
            display: inline-flex;
            align-items: center;
            max-width: 100%;
            min-height: 1.24rem;
            border-radius: 999px;
            border: 1px solid color-mix(in srgb, var(--pill), transparent 48%);
            background: color-mix(in srgb, var(--pill), transparent 86%);
            color: color-mix(in srgb, var(--pill), white 28%);
            padding: 0.12rem 0.42rem;
            font-size: 0.68rem;
            font-weight: 650;
            line-height: 1.05;
            white-space: nowrap;
        }
        .os-table-note {
            color: var(--os-muted);
            font-size: 0.78rem;
            margin-top: -0.25rem;
            margin-bottom: 0.55rem;
        }
        .os-inspector-title {
            font-size: 1.02rem;
            font-weight: 760;
            color: var(--os-text);
            margin-bottom: 0.35rem;
            overflow-wrap: anywhere;
        }
        .os-path {
            color: #c6d2df;
            background: rgba(0,0,0,0.20);
            border: 1px solid var(--os-line);
            border-radius: 6px;
            padding: 0.45rem;
            font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
            font-size: 0.72rem;
            overflow-wrap: anywhere;
        }
        .os-divider {
            border-top: 1px solid var(--os-line);
            margin: 0.72rem 0;
        }
@media (max-width: 1500px) {
            .os-kpi-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
            .os-card-grid { grid-template-columns: repeat(3, minmax(13rem, 1fr)); }
            .os-now-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .os-ribbon-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
            .os-candidate-ribbon { grid-template-columns: repeat(4, minmax(0, 1fr)); }
            .os-pattern-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 900px) {
            .os-topbar { align-items: flex-start; flex-direction: column; }
            .os-chip-row { justify-content: flex-start; }
            .os-kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .os-card-grid { grid-template-columns: 1fr; }
            .os-now-grid { grid-template-columns: 1fr; }
            .os-ribbon-grid, .os-candidate-ribbon { grid-template-columns: 1fr; }
            .os-pattern-grid { grid-template-columns: 1fr; }
        }
        """
    encoded_css = base64.b64encode(css.encode("utf-8")).decode("ascii")
    st.markdown(f'<link rel="stylesheet" href="data:text/css;base64,{encoded_css}">', unsafe_allow_html=True)


def _render_topbar(registry: ProjectRegistry, snapshot_count: int, sensitive_count: int) -> None:
    st.markdown(
        f"""
        <div class="os-topbar">
            <div>
                <div class="os-title">Research OS</div>
                <div class="os-subtitle">One-page project control room for candidates, proof quality, lineage, artifacts, and health.</div>
            </div>
            <div class="os-chip-row">
                <span class="os-chip"><strong>{len(registry.nodes):,}</strong> nodes</span>
                <span class="os-chip"><strong>{len(registry.edges):,}</strong> edges</span>
                <span class="os-chip"><strong>{len(registry.issues):,}</strong> health</span>
                <span class="os-chip"><strong>{snapshot_count:,}</strong> snapshots</span>
                <span class="os-chip"><strong>{sensitive_count:,}</strong> sensitive</span>
                <span class="os-chip"><strong>{escape(registry.generated_at_utc)}</strong></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_kpis(registry: ProjectRegistry) -> None:
    counts = Counter(node.kind for node in registry.nodes)
    status_counts = Counter(node.status for node in registry.nodes)
    evidence_counts = Counter(node.evidence_level for node in registry.nodes)
    family_counts = Counter(node.family for node in registry.nodes)
    newest = max([node.updated_at_utc for node in registry.nodes if node.updated_at_utc] or [""])
    unclassified_scripts = sum(1 for node in registry.nodes if node.family == "unclassified" and node.kind == "script")
    cards = [
        ("Candidates", counts.get("candidate", 0), f"{counts.get('family', 0)} families indexed", "#36c2ff"),
        ("Watch List", status_counts.get("strong_candidate", 0) + status_counts.get("worth_watching", 0), "strong + worth watching", "#21c87a"),
        ("Needs Proof", status_counts.get("needs_more_proof", 0), "collect forward/shadow rows", "#f4b942"),
        ("Blocked/Rejected", status_counts.get("blocked", 0) + status_counts.get("rejected", 0), "requires inspection or archive", "#ff6b4a"),
        ("Live Evidence", evidence_counts.get("live_forward", 0) + evidence_counts.get("live_stats", 0), "live forward + stats nodes", "#2dd4bf"),
        ("Forward Shadow", evidence_counts.get("forward_shadow", 0), "incoming proof surface", "#36c2ff"),
        ("Health Notices", counts.get("health_issue", 0), "classified graph notices", "#f59e0b"),
        ("Unclassified", family_counts.get("unclassified", 0), f"{unclassified_scripts:,} scripts need routing", "#9aa6b2"),
    ]
    html = ['<div class="os-kpi-grid">']
    for label, value, note, color in cards:
        html.append(
            f'<div class="os-kpi" style="border-top: 3px solid {color};"><div class="os-kpi-label">{escape(label)}</div><div class="os-kpi-value">{value:,}</div><div class="os-kpi-note">{escape(note)}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)
    if newest:
        st.caption(f"Newest indexed artifact: {newest} | Root: {registry.root}")


def _render_section(title: str, subtitle: str, tag: str = "") -> None:
    st.markdown(
        f"""
        <div class="os-section">
            <div>
                <h2>{escape(title)}</h2>
                <p>{escape(subtitle)}</p>
            </div>
            <div class="os-section-tag">{escape(tag)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_now_strip(registry: ProjectRegistry, compact: bool = False) -> None:
    candidates = _candidate_nodes(registry)
    decision_nodes = _decision_nodes(registry)
    health = _health_nodes(registry)
    newest = _latest_artifacts(registry, limit=1)

    best = next((node for node in decision_nodes if node.status in {"strong_candidate", "worth_watching"}), candidates[0] if candidates else None)
    blocker = health[0] if health else None
    proof_gap = next((node for node in candidates if node.status == "needs_more_proof"), None)
    latest = newest[0] if newest else None

    def node_title(node: ProjectNode | None, fallback: str) -> str:
        return node.label if node else fallback

    def node_note(node: ProjectNode | None, fallback: str) -> str:
        if not node:
            return fallback
        pnl = _pnl_7d_display(node.metrics)
        source = _pnl_display(node.metrics)
        metric = f"P&L/7d {pnl} | " if pnl != "" else ""
        if pnl and source and source != pnl:
            metric = f"{metric}source {source} | "
        return _short(f"{metric}{_status_label(node.status)} | {_evidence_label(node.evidence_level)} | {node.next_action or node.summary}", 132)

    cards = [
        ("Strongest research signal", node_title(best, "No candidate surfaced"), node_note(best, "Registry has no ranked candidate yet."), "#21c87a"),
        ("Next proof task", node_title(proof_gap, "No proof gap selected"), node_note(proof_gap, "No needs-more-proof candidate indexed."), "#f4b942"),
        ("Health notices", node_title(blocker, "No health notice surfaced"), node_note(blocker, "Health queue is currently clean."), "#f59e0b"),
        ("Freshest artifact", node_title(latest, "No timestamped artifact"), node_note(latest, "No updated artifact timestamp indexed."), "#36c2ff"),
    ]
    grid_class = "os-now-grid os-now-rail" if compact else "os-now-grid"
    html = [f'<div class="{grid_class}">']
    for label, title, note, color in cards:
        html.append(
            f'<div class="os-now-card" style="--accent:{color};"><div class="os-now-label">{escape(label)}</div><div class="os-now-title">{escape(title)}</div><div class="os-now-note">{escape(note)}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def _render_family_ribbon(registry: ProjectRegistry) -> None:
    rows = _family_summary_rows(registry)
    html = ['<div class="os-ribbon-grid">']
    for row in rows[:7]:
        family = str(row["Family"])
        color = FAMILY_COLORS.get(family, "#9aa6b2")
        html.append(
            f'<div class="os-ribbon-card" style="--accent:{color};"><div class="os-ribbon-title">{escape(family.replace("_", " ").title())}</div><div class="os-card-meta">{_status_pill(str(row["Status"]))} {_evidence_pill(str(row["Best Evidence"]))}</div><div class="os-ribbon-meta">{row["Nodes"]:,} nodes | {row["Candidates"]:,} candidates | {row["Reports"]:,} reports</div><div class="os-ribbon-meta">{row["Health"]:,} health notices | latest {escape(str(row["Latest"]) or "unknown")}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def _render_candidate_ribbon(registry: ProjectRegistry) -> None:
    nodes = _candidate_nodes(registry)[:8]
    if not nodes:
        return
    html = ['<div class="os-ribbon-grid os-candidate-ribbon">']
    for node in nodes:
        color = STATUS_COLORS.get(node.status, STATUS_COLORS["unknown"])
        pnl = _pnl_7d_display(node.metrics)
        source = _pnl_display(node.metrics)
        metric = f"P&L/7d {pnl}" if pnl != "" else node.kind
        if pnl and source and source != pnl:
            metric = f"{metric} | source {source}"
        html.append(
            f'<div class="os-ribbon-card" style="--accent:{color};"><div class="os-ribbon-title">{escape(node.label)}</div><div class="os-card-meta">{_family_pill(node.family)} {_status_pill(node.status)}</div><div class="os-ribbon-meta">{escape(metric)} | {_evidence_label(node.evidence_level)}</div><div class="os-ribbon-meta">{escape(_short(node.next_action or node.summary, 92))}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def _pattern_heatmap_figure(registry: ProjectRegistry) -> go.Figure:
    family_rows = family_pattern_rows(registry)
    motifs = motif_summaries(registry)[:10]
    families = [row["Family"] for row in family_rows[:8]]
    motif_labels = [row["Motif"] for row in motifs]
    motif_ids = [row["motif_id"] for row in motifs]
    counts = {family: Counter() for family in families}
    for node in registry.nodes:
        if node.family in counts:
            counts[node.family].update(node_pattern_tags(node))
    z = [[counts[family].get(motif_id, 0) for motif_id in motif_ids] for family in families]
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=motif_labels,
            y=[family.replace("_", " ").title() for family in families],
            colorscale=[
                [0.0, "rgba(18,22,29,0.2)"],
                [0.35, "rgba(54,194,255,0.55)"],
                [0.7, "rgba(183,148,244,0.72)"],
                [1.0, "rgba(33,200,122,0.92)"],
            ],
            hovertemplate="<b>%{y}</b><br>%{x}<br>%{z} indexed signals<extra></extra>",
        )
    )
    fig.update_layout(
        height=310,
        margin=dict(l=8, r=8, t=8, b=8),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickangle=32, tickfont=dict(size=10), side="bottom"),
        yaxis=dict(tickfont=dict(size=10)),
        coloraxis_showscale=False,
    )
    return fig


def _render_pattern_cartography(registry: ProjectRegistry) -> None:
    motif_rows = motif_summaries(registry)
    repeat_rows = repetition_clusters(registry)
    nearest_rows = _pattern_table("nearest_prior_rows", registry)
    family_rows = _pattern_table("family_gap_rows", registry, family_pattern_rows(registry))
    blocked_rows = _pattern_table("positive_blocked_rows", registry, positive_blocked_rows(registry))
    failure_rows = _pattern_table("failure_motif_rows", registry)
    lineage_rows = _pattern_table("lineage_gap_rows", registry, lineage_gap_rows(registry))
    cards = _pattern_table("research_move_cards", registry, frontier_cards(registry))
    if not motif_rows and not cards:
        st.info("Pattern cartography has no motif signals yet.")
        return

    accent = {
        "Test Next": "#21c87a",
        "Validate": "#36c2ff",
        "Do Not Repeat": "#ff4d6d",
        "Do not repeat": "#ff4d6d",
        "Repair Lineage": "#f4b942",
        "Repair": "#f4b942",
        "Frontier": "#b794f4",
        "Archive/Ignore": "#9aa6b2",
        "Exploit": "#21c87a",
        "Needs Repair": "#ff4d6d",
    }
    st.markdown('<div class="os-panel-title"><h3>Research Moves</h3><span>morning decision queue, research-only</span></div>', unsafe_allow_html=True)
    html = ['<div class="os-pattern-grid">']
    for card in cards[:6]:
        lane = str(card.get("Lane", "Pattern"))
        display_lane = "Validate" if lane == "Exploit" else lane
        color = accent.get(display_lane, "#b794f4")
        signal = str(card.get("Signal", card.get("Evidence", "")))
        why = str(card.get("Why", card.get("Move", "")))
        next_action = str(card.get("Next Action", card.get("Move", "")))
        source_nodes = card.get("Source Nodes", "")
        if isinstance(source_nodes, list):
            source_nodes = ", ".join(str(item) for item in source_nodes[:3])
        html.append(
            f'<div class="os-pattern-card" style="--accent:{color};">'
            f'<div class="os-pattern-lane">{escape(display_lane)}</div>'
            f'<div class="os-pattern-title">{escape(str(card.get("Title", "")))}</div>'
            f'<div class="os-pattern-signal">{escape(signal)}</div>'
            f'<div class="os-pattern-line">{escape(_short(why, 150))}</div>'
            f'<div class="os-pattern-move">{escape(_short(next_action, 170))}</div>'
            f'<div class="os-pattern-signal">{escape(_short(str(source_nodes), 120))}</div>'
            f"</div>"
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

    chart_col, table_col = st.columns([1.05, 1.15], gap="medium")
    with chart_col:
        with st.container(border=True):
            st.markdown('<div class="os-panel-title"><h3>Motif Heatmap</h3><span>families x recurring strategy signals</span></div>', unsafe_allow_html=True)
            st.plotly_chart(_pattern_heatmap_figure(registry), use_container_width=True, config={"displayModeBar": False, "displaylogo": False, "responsive": True})
    with table_col:
        with st.container(border=True):
            st.markdown('<div class="os-panel-title"><h3>Reusable Motifs</h3><span>what to validate carefully</span></div>', unsafe_allow_html=True)
            motif_df = _display_df(motif_rows[:8])
            keep = [column for column in ["Motif", "Families", "Nodes", "Candidates", "Watch/active", "Blocked/rejected", "Best Evidence", "Best P&L/7d", "Repeat Pressure", "Guidance"] if column in motif_df.columns]
            st.dataframe(motif_df[keep], use_container_width=True, hide_index=True, height=310)

    lower_left, lower_right = st.columns([1.1, 1.0], gap="medium")
    with lower_left:
        with st.container(border=True):
            st.markdown('<div class="os-panel-title"><h3>Do Not Repeat Blindly</h3><span>clusters that need a changed assumption</span></div>', unsafe_allow_html=True)
            if repeat_rows:
                repeat_df = _display_df(repeat_rows[:10])
                keep = [column for column in ["Family", "Pattern", "Attempts", "Watch/active", "Blocked/rejected", "Best Evidence", "Best P&L/7d", "Risk", "Guidance"] if column in repeat_df.columns]
                st.dataframe(repeat_df[keep], use_container_width=True, hide_index=True, height=285)
            else:
                st.success("No high-pressure repetition clusters surfaced.")
    with lower_right:
        with st.container(border=True):
            st.markdown('<div class="os-panel-title"><h3>Family Research Map</h3><span>where to branch or clean up</span></div>', unsafe_allow_html=True)
            family_df = _display_df(family_rows[:10])
            keep = [column for column in ["Family", "Candidates", "Reports", "Stats", "Forward Evidence", "Live Evidence", "Blocked/Rejected", "Blocked/rejected", "Watch/Active", "Watch/active", "Best Evidence", "Best P&L/7d", "Dominant Motifs", "Gap Flags", "Next Move"] if column in family_df.columns]
            st.dataframe(family_df[keep], use_container_width=True, hide_index=True, height=285)

    trap_col, lineage_col = st.columns([1.15, 0.95], gap="medium")
    with trap_col:
        with st.container(border=True):
            st.markdown('<div class="os-panel-title"><h3>Tempting But Blocked</h3><span>positive-looking traps not to rerun unchanged</span></div>', unsafe_allow_html=True)
            if blocked_rows:
                blocked_df = _display_df(blocked_rows[:12])
                keep = [column for column in ["Label", "Family", "Kind", "Status", "Evidence", "P&L/7d", "P&L", "Window", "Markets", "Entries", "Primary Blocker", "Why It Is Tempting", "Why It Is Blocked", "Do Next"] if column in blocked_df.columns]
                st.dataframe(blocked_df[keep], use_container_width=True, hide_index=True, height=300)
            else:
                st.success("No positive-but-blocked traps surfaced.")
    with lineage_col:
        with st.container(border=True):
            st.markdown('<div class="os-panel-title"><h3>Lineage Gaps</h3><span>blocked or incomplete nodes without explicit graph edges</span></div>', unsafe_allow_html=True)
            if lineage_rows:
                lineage_df = _display_df(lineage_rows[:12])
                keep = [column for column in ["Label", "Family", "Kind", "Status", "Evidence", "Motifs", "Missing Link", "Priority"] if column in lineage_df.columns]
                st.dataframe(lineage_df[keep], use_container_width=True, hide_index=True, height=300)
            else:
                st.success("Lineage blockers are structurally linked.")

    fail_col, prior_col = st.columns([1.0, 1.0], gap="medium")
    with fail_col:
        with st.container(border=True):
            st.markdown('<div class="os-panel-title"><h3>Failure Motifs</h3><span>blocker themes by family</span></div>', unsafe_allow_html=True)
            if failure_rows:
                failure_df = _display_df(failure_rows[:12])
                keep = [column for column in ["Family", "Failure Motif", "Count", "Affected Nodes", "Example", "Likely Meaning", "Required Change"] if column in failure_df.columns]
                st.dataframe(failure_df[keep], use_container_width=True, hide_index=True, height=285)
            else:
                st.info("No blocker motif summary is available yet.")
    with prior_col:
        with st.container(border=True):
            st.markdown('<div class="os-panel-title"><h3>Nearest Prior Lineage</h3><span>similar attempts and changed-assumption checks</span></div>', unsafe_allow_html=True)
            if nearest_rows:
                prior_df = _display_df(nearest_rows[:12])
                keep = [column for column in ["Label", "Family", "Kind", "Nearest Prior", "Similarity", "Prior Status", "Prior Evidence", "Prior Blocker", "Changed Assumption", "Repeat Warning"] if column in prior_df.columns]
                st.dataframe(prior_df[keep], use_container_width=True, hide_index=True, height=285)
            else:
                st.info("Nearest-prior rows are not available yet.")


def _render_decision_cards(registry: ProjectRegistry) -> None:
    buckets = [
        ("Worth Watching", {"strong_candidate", "worth_watching"}),
        ("Needs Proof", {"needs_more_proof", "active"}),
        ("Blocked", {"blocked"}),
        ("Rejected / Archived", {"rejected", "archived"}),
        ("Diagnostic", {"diagnostic_only", "unknown"}),
    ]
    nodes = _decision_nodes(registry)
    html = ['<div class="os-card-grid">']
    for title, statuses in buckets:
        bucket_nodes = [node for node in nodes if node.status in statuses][:5]
        html.append('<div class="os-panel">')
        html.append(f'<div class="os-panel-title"><h3>{escape(title)}</h3><span>{len([n for n in nodes if n.status in statuses]):,}</span></div>')
        if not bucket_nodes:
            html.append('<div class="os-card-line">No indexed items in this lane.</div>')
        for node in bucket_nodes:
            pnl = _pnl_7d_display(node.metrics)
            source = _pnl_display(node.metrics)
            markets = _safe_metric(node.metrics, "markets")
            entries = _safe_metric(node.metrics, "entries")
            detail = " | ".join(
                item
                for item in [
                    f"P&L/7d {pnl}" if pnl != "" else "",
                    f"source {source}" if pnl != "" and source != "" and source != pnl else "",
                    f"{markets} markets" if markets != "" else "",
                    f"{entries} entries" if entries != "" else "",
                ]
            )
            action = node.blockers[0] if node.blockers else node.next_action or node.summary
            html.append(
                f'<div class="os-card"><h4>{escape(node.label)}</h4><div class="os-card-meta">{_family_pill(node.family)} {_status_pill(node.status)} {_evidence_pill(node.evidence_level)}</div><div class="os-card-line">{escape(detail or node.kind)}</div><div class="os-card-line">{escape(_short(node.path or node.source_adapter, 85))}</div><div class="os-card-action">{escape(_short(action, 150))}</div></div>'
            )
        html.append("</div>")
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def _render_family_command_center(registry: ProjectRegistry, node_lookup: dict[str, ProjectNode]) -> None:
    rows = _family_summary_rows(registry)
    if not rows:
        st.info("No family nodes are indexed yet.")
        return
    st.markdown('<div class="os-panel-title"><h3>Family Command Center</h3><span>status, evidence, load, blockers</span></div>', unsafe_allow_html=True)
    display = []
    for row in rows:
        display.append(
            {
                "Family": row["Family"].replace("_", " ").title(),
                "Status": _status_label(row["Status"]),
                "Nodes": row["Nodes"],
                "Candidates": row["Candidates"],
                "Reports": row["Reports"],
                "Stats": row["Stats"],
                "Health": row["Health"],
                "Best Evidence": _evidence_label(row["Best Evidence"]),
                "Latest": row["Latest"],
                "Verdict / Next Action": row["Action"],
            }
        )
    st.dataframe(_display_df(display), use_container_width=True, hide_index=True, height=300)
    family_options = [row["id"] for row in rows if row["id"] in node_lookup]
    if family_options:
        selected = st.selectbox(
            "Inspect family",
            family_options,
            format_func=lambda node_id: node_lookup[node_id].label if node_id in node_lookup else node_id,
            key="family_inspect_select",
        )
        if selected and st.button("Focus selected family", use_container_width=True):
            st.session_state["project_os_selected_node"] = selected


def _render_candidate_queue(registry: ProjectRegistry, node_lookup: dict[str, ProjectNode]) -> None:
    candidates = _candidate_nodes(registry)
    st.markdown('<div class="os-panel-title"><h3>Candidate Queue</h3><span>sorted by verdict, evidence, then P&L/7d</span></div>', unsafe_allow_html=True)
    if not candidates:
        st.info("No candidates are indexed yet.")
        return
    rows = _candidate_rows(candidates)
    st.dataframe(_display_df(rows).drop(columns=["id"], errors="ignore"), use_container_width=True, hide_index=True, height=300)
    top_options = [node.id for node in candidates[:24] if node.id in node_lookup]
    selected = st.selectbox(
        "Inspect candidate",
        top_options,
        format_func=lambda node_id: node_lookup[node_id].label if node_id in node_lookup else node_id,
        key="candidate_inspect_select",
    )
    if selected and st.button("Focus selected candidate", use_container_width=True):
        st.session_state["project_os_selected_node"] = selected


def _render_inspector(node: ProjectNode | None, registry: ProjectRegistry) -> None:
    st.markdown('<div class="os-panel-title"><h3>Inspector</h3><span>selected node</span></div>', unsafe_allow_html=True)
    if node is None:
        st.info("Select a node from the graph, candidate queue, or family table.")
        return
    incoming, outgoing = _incoming_outgoing(node.id, registry.edges)
    snapshot = _metric_snapshot(node)
    nearest = _nearest_prior_for(node, registry) if node.kind in {"candidate", "report", "stats"} else None
    trap = _positive_blocked_for(node, registry) if node.kind in {"candidate", "report", "stats"} else None
    family_gaps = _family_gap_lookup(registry)
    failure_by_family = _failure_motif_lookup(registry)
    motifs = node_pattern_tags(node)
    signature = _candidate_signature(node) if node.kind in {"candidate", "report", "stats"} else ""
    st.markdown(f'<div class="os-inspector-title">{escape(node.label)}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="os-card-meta">{_family_pill(node.family)} {_status_pill(node.status)} {_evidence_pill(node.evidence_level)} {_pill(node.kind, "#9aa6b2")}</div>',
        unsafe_allow_html=True,
    )
    if node.sensitive:
        st.warning("Sensitive local file. Contents may be visible in this local-only dashboard.")
    if trap:
        blocker = trap.get("Why It Is Blocked") or trap.get("Primary Blocker") or "Positive P&L is blocked by status or gate evidence."
        st.error(f"Positive-but-blocked trap: {_short(blocker, 220)}")
    if node.summary:
        st.caption(node.summary)
    if node.next_action:
        st.info(f"Next action: {node.next_action}")
    if node.blockers:
        st.error(_short(node.blockers[0], 240))
    st.success(_decision_summary_for(node, trap, nearest))
    compact_cols = st.columns(3)
    compact_cols[0].metric("Inbound", len(incoming))
    compact_cols[1].metric("Outbound", len(outgoing))
    compact_cols[2].metric("Size", _format_bytes(node.size_bytes) or "NA")
    if node.kind in {"candidate", "report", "stats"}:
        st.markdown("**Proof Summary**")
        proof_row = {
            "P&L/7d": snapshot.get("pnl_7d_display") or "",
            "Window": snapshot.get("pnl_window_display") or "",
            "P&L": snapshot.get("pnl_display") or "",
            "Unit": snapshot.get("pnl_unit") or "",
            "Source Key": snapshot.get("pnl_key") or "",
            "Standardized": snapshot.get("pnl_standardization_status") or "",
            "Status": snapshot.get("pnl_status") or "",
            "Source Node": snapshot.get("pnl_source_node_id") or "",
            "Confidence": snapshot.get("pnl_confidence") or "",
            "Entries": snapshot.get("entries") or "",
            "Markets": snapshot.get("markets") or "",
            "Roots": snapshot.get("roots") or "",
            "Win Rate": snapshot.get("win_rate") or "",
            "Evidence": _evidence_label(node.evidence_level),
        }
        st.dataframe(_display_df([proof_row]), use_container_width=True, hide_index=True)
        warnings = snapshot.get("metric_warnings") or []
        if warnings:
            st.warning(_short("; ".join(str(item) for item in warnings), 280))
        st.markdown("**Strategy Memory**")
        memory_rows = [
            {"Field": "Motifs", "Value": ", ".join(tag.replace("_", " ") for tag in motifs) or "none"},
            {"Field": "Repeat Signature", "Value": signature or "none"},
        ]
        if nearest:
            memory_rows.extend(
                [
                    {"Field": "Nearest Prior", "Value": str(nearest.get("Nearest Prior", ""))},
                    {"Field": "Similarity", "Value": str(nearest.get("Similarity", ""))},
                    {"Field": "Changed Assumption", "Value": str(nearest.get("Changed Assumption", ""))},
                    {"Field": "Repeat Warning", "Value": str(nearest.get("Repeat Warning", ""))},
                ]
            )
        else:
            memory_rows.append({"Field": "Nearest Prior", "Value": "none found in current registry"})
        family_gap = family_gaps.get(node.family)
        if family_gap:
            memory_rows.append({"Field": "Family Gap Flags", "Value": str(family_gap.get("Gap Flags", ""))})
        family_failures = failure_by_family.get(node.family, [])
        if family_failures:
            memory_rows.append({"Field": "Failure Motifs", "Value": ", ".join(str(row.get("Failure Motif", "")) for row in family_failures[:4])})
        st.dataframe(_display_df(memory_rows), use_container_width=True, hide_index=True, height=245)
    if node.metrics:
        st.markdown("**Metrics**")
        st.dataframe(_display_df([node.metrics]), use_container_width=True, hide_index=True)
    if node.path:
        st.markdown(f'<div class="os-path">{escape(node.path)}</div>', unsafe_allow_html=True)
    edge_rows = []
    node_lookup, _ = registry_lookup(registry)
    for edge in incoming[:24]:
        other = node_lookup.get(edge.source)
        edge_rows.append({"Direction": "in", "Relation": edge.relation, "Other": other.label if other else edge.source, "Evidence": edge.evidence_level, "Reason": edge.reason})
    for edge in outgoing[:24]:
        other = node_lookup.get(edge.target)
        edge_rows.append({"Direction": "out", "Relation": edge.relation, "Other": other.label if other else edge.target, "Evidence": edge.evidence_level, "Reason": edge.reason})
    if edge_rows:
        st.markdown("**Linked Nodes**")
        st.dataframe(_display_df(edge_rows), use_container_width=True, hide_index=True, height=220)
    if node.raw_preview:
        with st.expander("Raw preview", expanded=False):
            st.code(node.raw_preview[:8000], language="text")


def _render_health_panel(registry: ProjectRegistry) -> None:
    issues = _health_nodes(registry)
    st.markdown('<div class="os-panel-title"><h3>Data Health Queue</h3><span>classified notices, visible by default</span></div>', unsafe_allow_html=True)
    if not issues:
        st.success("No registry health notices were found.")
        return
    rows = []
    for node in issues[:24]:
        severity = "Sensitive notice" if node.sensitive or node.source_adapter == "sensitive_adapter" else "Health notice"
        if "large" in node.summary.lower() or "too large" in node.summary.lower():
            severity = "Large artifact"
        rows.append(
            {
                "Severity": severity,
                "Family": node.family,
                "Issue": node.label,
                "Summary": _short(node.summary, 160),
                "Source": node.source_adapter,
                "Path": node.path or "",
                "Next Action": _short(node.next_action, 110),
            }
        )
    st.dataframe(_display_df(rows), use_container_width=True, hide_index=True, height=310)


def _render_artifact_panel(registry: ProjectRegistry) -> None:
    st.markdown('<div class="os-panel-title"><h3>Newest Artifacts</h3><span>latest reports, data, logs, scripts</span></div>', unsafe_allow_html=True)
    rows = _node_rows(_latest_artifacts(registry))
    if not rows:
        st.info("No timestamped artifacts indexed yet.")
        return
    df = _display_df(rows)
    keep = ["Label", "Kind", "Family", "Status", "Evidence", "Updated", "Sensitive", "Path", "Summary"]
    st.dataframe(df[keep], use_container_width=True, hide_index=True, height=310)


def _render_adapter_coverage(registry: ProjectRegistry) -> None:
    summaries = registry.adapter_summaries or {}
    rows = []
    for adapter, summary in sorted(summaries.items()):
        if isinstance(summary, dict):
            row = {"Adapter": adapter}
            for key, value in summary.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    row[str(key)] = value
            rows.append(row)
        else:
            rows.append({"Adapter": adapter, "Summary": str(summary)})
    if rows:
        st.markdown('<div class="os-panel-title"><h3>Adapter Coverage</h3><span>registry inputs</span></div>', unsafe_allow_html=True)
        st.dataframe(_display_df(rows), use_container_width=True, hide_index=True, height=210)


def _render_graph_legend(registry: ProjectRegistry) -> None:
    counts = Counter(node.kind for node in registry.nodes)
    status_counts = Counter(node.status for node in registry.nodes)
    st.markdown('<div class="os-panel-title"><h3>Vault Key</h3><span>how to read the map</span></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="os-legend-grid">
            <div class="os-legend-item"><span class="os-node-demo os-star" style="--core:#8bd450;--ring:#39d2ff;--family:#36c2ff"></span>star shape = candidate ({counts.get("candidate", 0):,})</div>
            <div class="os-legend-item"><span class="os-node-demo" style="--core:#f4b942;--ring:#fbbf24;--family:#21c87a"></span>core color = verdict ({status_counts.get("needs_more_proof", 0):,} need proof)</div>
            <div class="os-legend-item"><span class="os-node-demo os-open" style="--core:#0b0d10;--ring:#20e184;--family:#21c87a"></span>outer ring = evidence strength</div>
            <div class="os-legend-item"><span class="os-node-demo os-diamond" style="--core:#36c2ff;--ring:#c084fc;--family:#b794f4"></span>soft aura = family cluster</div>
            <div class="os-legend-item"><span class="os-node-demo" style="--core:#ff4d6d;--ring:#edf2f7;--family:#ff4d6d"></span>bright rings = selected neighborhood</div>
            <div class="os-legend-item"><span class="os-node-demo os-open" style="--core:#0b0d10;--ring:#9aa6b2;--family:#9aa6b2"></span>open/dim nodes = archive, logs, unknowns</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Node grammar: symbol shows artifact type, core fill shows plain-English status, outer ring shows proof quality, family aura shows constellation, and dimming shows nodes outside a focused neighborhood.")


def _render_project_map(registry: ProjectRegistry, node_lookup: dict[str, ProjectNode], *, height: int = 640, title: str = "Vault Atlas", subtitle: str = "Obsidian-style whole-project graph") -> None:
    st.markdown(f'<div class="os-panel-title"><h3>{escape(title)}</h3><span>{escape(subtitle)}</span></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="os-atlas-intro">Families render as constellations. Candidates, reports, stats, datasets, logs, docs, archives, health notices, and sensitive nodes all share the same visual field; high-volume scripts collapse into readable masses.</div>',
        unsafe_allow_html=True,
    )
    all_families = sorted({node.family for node in registry.nodes})
    all_statuses = [status for status in STATUS_ORDER if status in {node.status for node in registry.nodes}]
    lens_kinds = {
        "Whole vault": sorted({node.kind for node in registry.nodes}),
        "Candidates + evidence": ["family", "candidate", "report", "dataset", "stats", "health_issue", "secret"],
        "Health + blockers": ["family", "health_issue", "log", "stats", "report", "dataset", "artifact"],
        "Repeat risk": ["family", "candidate", "report", "stats", "health_issue", "artifact"],
        "Frontier gaps": ["family", "candidate", "report", "dataset", "stats", "artifact", "unknown"],
        "Failure motifs": ["family", "candidate", "report", "stats", "health_issue", "artifact"],
        "Evidence quality": ["family", "candidate", "report", "dataset", "stats", "log", "artifact"],
        "Live and stats": ["family", "candidate", "stats", "log", "health_issue", "secret"],
        "Artifacts and docs": ["family", "doc", "script", "archive", "artifact", "report", "dataset", "log", "unknown"],
    }
    graph_lens_by_label = {
        "Repeat risk": "repeat-risk",
        "Frontier gaps": "frontier",
        "Failure motifs": "failure",
        "Evidence quality": "evidence",
    }
    with st.container():
        c1, c2, c3, c4, c5 = st.columns([1.2, 0.85, 0.7, 0.95, 0.65])
        search = c1.text_input("Atlas search", value="", placeholder="candidate, report, family, path...", key="map_search")
        lens = c2.selectbox("Atlas lens", list(lens_kinds), index=0, key="map_lens")
        label_choice = c3.selectbox("Labels", ["Essential", "Balanced", "Dense", "Minimal"], index=0, key="map_labels")
        families = c4.multiselect("Families", all_families, key="map_families")
        focus_mode = c5.selectbox("Focus", ["Off", "Selected"], index=0, key="map_focus_mode")
        focus_selected = focus_mode == "Selected"
        kind_options = sorted({node.kind for node in registry.nodes})
        default_kinds = [kind for kind in lens_kinds[lens] if kind in kind_options]
        with st.expander("Atlas filters", expanded=False):
            f1, f2, f3, f4 = st.columns([0.85, 1.0, 1.0, 0.85])
            layout = f1.selectbox("Layout", ["vault atlas", "network", "family clusters", "pipeline"], index=0, key="map_layout")
            statuses = f2.multiselect("Statuses", all_statuses, format_func=_status_label, key="map_statuses")
            kinds = f3.multiselect("Node kinds", kind_options, default=default_kinds, key=f"map_kinds_{lens.lower().replace(' ', '_').replace('+', 'plus')}")
            evidence = f4.multiselect(
                "Evidence",
                sorted({node.evidence_level for node in registry.nodes}, key=lambda item: EVIDENCE_RANK.get(item, 0), reverse=True),
                key="map_evidence",
            )
            t1, t2, t3, t4 = st.columns(4)
            show_sensitive = t1.checkbox("Sensitive", value=True, key="map_sensitive")
            show_unknown = t2.checkbox("Unknowns", value=True, key="map_unknown")
            show_health = t3.checkbox("Health", value=True, key="map_health")
            show_archives = t4.checkbox("Archives", value=True, key="map_archives")

    visible_nodes = _filter_nodes(registry.nodes, search, families, statuses, kinds, evidence, show_health, show_unknown, show_sensitive, show_archives)
    visible_ids = {node.id for node in visible_nodes}
    visible_edges = _edges_for_nodes(registry.edges, visible_ids)
    graph_nodes, graph_edges, collapsed = collapse_graph(visible_nodes, visible_edges, threshold=900, lod_threshold=430)
    st.session_state["project_os_graph_nodes_lookup"] = {node.id: node for node in graph_nodes}
    if collapsed:
        st.caption(f"Collapsed {sum(len(v) for v in collapsed.values()):,} high-volume nodes into {len(collapsed):,} summaries.")
    if not graph_nodes:
        st.warning("No nodes match the map filters.")
        return
    label_mode = label_choice.lower()
    selected_for_focus = st.session_state.get("project_os_selected_node", "") if focus_selected else ""
    if selected_for_focus not in {node.id for node in graph_nodes}:
        selected_for_focus = ""
    fig = build_figure(graph_nodes, graph_edges, mode=layout, height=height, obsidian=True, label_mode=label_mode, selected_id=selected_for_focus, lens=graph_lens_by_label.get(lens, "default"))
    fig.update_layout(plot_bgcolor="#080a0d", paper_bgcolor="#080a0d")
    plot_config = {
        "displayModeBar": False,
        "displaylogo": False,
        "scrollZoom": True,
        "responsive": True,
    }
    try:
        event = st.plotly_chart(fig, use_container_width=True, key="project_os_graph", on_select="rerun", selection_mode="points", config=plot_config)
        clicked = _select_node_from_event(event)
        if clicked:
            st.session_state["project_os_selected_node"] = clicked
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, key="project_os_graph", config=plot_config)
    st.caption(f"Map showing {len(graph_nodes):,} nodes and {len(graph_edges):,} edges after filters/collapse.")


def render_dashboard(root: Path) -> None:
    st.set_page_config(page_title="Kalshi Research OS", page_icon=":material/hub:", layout="wide", initial_sidebar_state="collapsed")
    _render_css()

    registry_dir = root / "logs" / "project_os"

    top_left, top_right = st.columns([6.8, 1.2], vertical_alignment="center")
    with top_right:
        force = st.button("Refresh registry", use_container_width=True)
    registry = load_or_build_registry(root, force=force)
    snapshot_count = _snapshot_count(registry_dir)
    node_lookup, _ = registry_lookup(registry)
    sensitive_count = sum(1 for node in registry.nodes if node.sensitive or node.kind == "secret")

    with top_left:
        _render_topbar(registry, snapshot_count, sensitive_count)

    st.markdown(
        f"""
        <div class="os-warning">
            Local-only dashboard: sensitive files may be visible. Sensitive nodes indexed: <strong>{sensitive_count:,}</strong>.
            Avoid screenshots or screen sharing if secrets are in view.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "project_os_selected_node" not in st.session_state:
        st.session_state["project_os_selected_node"] = _best_default_node(registry)

    focus_options = [""] + sorted(node_lookup)
    focus_default = st.session_state.get("project_os_selected_node", "")
    focus_index = focus_options.index(focus_default) if focus_default in focus_options else 0
    focus = st.selectbox(
        "Global focus item",
        focus_options,
        index=focus_index,
        format_func=lambda node_id: node_lookup[node_id].label if node_id in node_lookup else "None",
        key="global_focus_select",
    )
    if focus:
        st.session_state["project_os_selected_node"] = focus

    _render_section("Vault Atlas", "The dashboard is now the map: use it as the primary project interface, then open supporting drawers only when you need raw tables.", "graph-first workspace")
    atlas_col, atlas_side_col = st.columns([4.2, 0.8], gap="medium")
    with atlas_col:
        with st.container(border=True):
            _render_project_map(registry, node_lookup, height=840, title="Research Vault", subtitle="whole-project knowledge graph")
    with atlas_side_col:
        with st.container(border=True):
            st.markdown('<div class="os-panel-title"><h3>Now</h3><span>current signals</span></div>', unsafe_allow_html=True)
            _render_now_strip(registry, compact=True)
        with st.container(border=True):
            _render_graph_legend(registry)
        with st.container(border=True):
            selected_id = st.session_state.get("project_os_selected_node", "")
            graph_lookup = st.session_state.get("project_os_graph_nodes_lookup", {})
            selected_node = node_lookup.get(selected_id) or graph_lookup.get(selected_id)
            _render_inspector(selected_node, registry)

    _render_section("Constellation Index", "Fast visual summaries that support the graph without turning the page back into a table dashboard.", "families and candidates")
    _render_family_ribbon(registry)
    _render_candidate_ribbon(registry)

    _render_section("Pattern Cartography", "Read the atlas as strategy memory: reuse winning motifs, avoid repeated dead ends, and spot where new branches should form.", "research map")
    _render_pattern_cartography(registry)

    with st.expander("Supporting evidence drawers", expanded=False):
        _render_section("Research Queue", "Plain-English lanes and sortable source tables.", "drawer")
        _render_decision_cards(registry)
        family_col, candidate_col = st.columns([1.0, 1.12], gap="medium")
        with family_col:
            with st.container(border=True):
                _render_family_command_center(registry, node_lookup)
        with candidate_col:
            with st.container(border=True):
                _render_candidate_queue(registry, node_lookup)

        _render_section("Evidence And Health", "Proof coverage, verdict shape, health notices, and fresh artifacts.", "drawer")
        chart_left, chart_right = st.columns(2, gap="medium")
        with chart_left:
            with st.container(border=True):
                st.markdown('<div class="os-panel-title"><h3>Evidence Coverage</h3><span>family by proof level</span></div>', unsafe_allow_html=True)
                st.plotly_chart(_evidence_figure(registry), use_container_width=True)
        with chart_right:
            with st.container(border=True):
                st.markdown('<div class="os-panel-title"><h3>Status Funnel</h3><span>family by verdict</span></div>', unsafe_allow_html=True)
                st.plotly_chart(_status_figure(registry), use_container_width=True)

        health_col, artifacts_col = st.columns(2, gap="medium")
        with health_col:
            with st.container(border=True):
                _render_health_panel(registry)
        with artifacts_col:
            with st.container(border=True):
                _render_artifact_panel(registry)

        with st.container(border=True):
            _render_adapter_coverage(registry)
