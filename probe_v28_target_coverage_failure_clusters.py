"""Mutually exclusive failure clusters for the v28 target-coverage surface.

Research-only; no live bot changes or orders.

The target-coverage loss reports use overlapping tags. This derived report
assigns each direction-wrong row to one primary physical failure cluster so the
loss budget is not double-counted.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
ATTR_JSON = OUT_DIR / "v28_target_coverage_pnl_attribution_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_failure_clusters_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_failure_clusters_latest.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def net(row: dict[str, Any]) -> float:
    return float(as_float(row.get("net_cents")) or 0.0)


def tags(row: dict[str, Any]) -> set[str]:
    return {str(item) for item in (row.get("tags") or [])}


def classify(row: dict[str, Any]) -> tuple[str, str]:
    row_tags = tags(row)
    side = str(row.get("side") or "")
    stc = as_float(row.get("seconds_to_close")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma")) or 0.0
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    edge = as_float(row.get("edge_prob")) or 0.0
    ask = as_float(row.get("ask_prob")) or 0.0
    p_side = as_float(row.get("p_side")) or 0.0

    if side == "no" and stc >= 720.0 and abs_d <= 0.40:
        return (
            "early_no_near_boundary_decay",
            "NO-side entries taken early near the strike; boundary path can decay/reverse before settlement.",
        )
    if recross >= 0.75 and abs_d <= 0.30:
        return (
            "near_boundary_high_recross",
            "Near-strike rows with high recross hazard; directional read is unstable.",
        )
    if edge < 0.02 and p_side >= 0.60:
        return (
            "thin_edge_high_confidence_price",
            "High raw probability but little actual entry edge; paying near fair value leaves no error margin.",
        )
    if ask <= 0.55 and abs_d <= 0.35:
        return (
            "cheap_boundary_tail_overconfidence",
            "Cheap-side boundary tails looked attractive but were still direction-wrong.",
        )
    if "edge_ge_4pp" in row_tags and 0.50 <= p_side < 0.65:
        return (
            "mid_probability_large_edge_wrong",
            "Mid-probability rows with apparent edge were directionally wrong, not just price-friction damaged.",
        )
    if "source:rejected_actionable" in row_tags:
        return (
            "reconstructed_directional_error",
            "Remaining directional loss rows come from rejected-actionable evidence and need approved-entry confirmation.",
        )
    return ("other_directional_error", "Direction was wrong, but no dominant physical cluster matched.")


def rollup(rows: list[dict[str, Any]]) -> dict[str, Any]:
    row_net = sum(net(row) for row in rows)
    return {
        "rows": len(rows),
        "net_cents": row_net,
        "avg_net_cents": None if not rows else row_net / len(rows),
        "markets": sorted({str(row.get("market") or "") for row in rows if row.get("market")}),
        "worst_rows": sorted(rows, key=net)[:8],
    }


def build_report() -> dict[str, Any]:
    attr = load_json(ATTR_JSON)
    direction_rows = [row for row in (attr.get("direction_wrong_rows") or []) if isinstance(row, dict)]
    side_won_negative = [row for row in (attr.get("side_won_negative_rows") or []) if isinstance(row, dict)]
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    reasons: dict[str, str] = {}
    for row in direction_rows:
        cluster, reason = classify(row)
        row = dict(row)
        row["primary_failure_cluster"] = cluster
        clusters[cluster].append(row)
        reasons[cluster] = reason
    cluster_rows = []
    for name, rows in clusters.items():
        item = rollup(rows)
        item["cluster"] = name
        item["physical_read"] = reasons.get(name)
        cluster_rows.append(item)
    cluster_rows.sort(key=lambda row: float(row.get("net_cents") or 0.0))
    total_direction_loss = sum(net(row) for row in direction_rows)
    report = {
        "generated_at_utc": utc_now_iso(),
        "source_generated_policy": attr.get("policy"),
        "forward_denominator": attr.get("forward_denominator"),
        "summary": attr.get("summary") or {},
        "class_rollups": attr.get("class_rollups") or {},
        "total_direction_wrong_rows": len(direction_rows),
        "total_direction_wrong_net_cents": total_direction_loss,
        "side_won_negative_rows": side_won_negative,
        "clusters": cluster_rows,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "Clusters are mutually exclusive and diagnostic only; they explain loss budget without defining a new promotion rule.",
        f"Direction-wrong rows explain {report.get('total_direction_wrong_net_cents')}c across {report.get('total_direction_wrong_rows')} rows.",
    ]
    for cluster in (report.get("clusters") or [])[:5]:
        notes.append(
            f"{cluster.get('cluster')}: {cluster.get('rows')} rows, net {cluster.get('net_cents')}c, "
            f"avg {cluster.get('avg_net_cents')}c; {cluster.get('physical_read')}"
        )
    if report.get("side_won_negative_rows"):
        notes.append(
            f"{len(report.get('side_won_negative_rows') or [])} side-won negative-PnL rows remain exit/execution shaped, not pure FV direction failures."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    summary = report.get("summary") or {}
    lines = [
        "# v28 Target-Coverage Failure Clusters",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Policy: `{report.get('source_generated_policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Surface entries/settled: `{summary.get('entries')}/{summary.get('settled')}`",
        f"- Surface net: `{fmt(summary.get('net_cents'))}c`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Direction-Wrong Clusters",
        "",
        "| cluster | rows | net c | avg c | physical read |",
        "|---|---:|---:|---:|---|",
    ])
    for cluster in report.get("clusters") or []:
        lines.append(
            f"| {cluster.get('cluster')} | {cluster.get('rows')} | {fmt(cluster.get('net_cents'))} | "
            f"{fmt(cluster.get('avg_net_cents'))} | {cluster.get('physical_read')} |"
        )
    for cluster in report.get("clusters") or []:
        lines.extend(["", f"## {cluster.get('cluster')} Worst Rows", ""])
        lines.extend([
            "| market | side | p | ask | edge | stc | abs d | recross | net c | source | reason |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ])
        for row in cluster.get("worst_rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_side'))} | "
                f"{fmt(row.get('ask_prob'))} | {fmt(row.get('edge_prob'))} | "
                f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | "
                f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('net_cents'))} | "
                f"{row.get('source')} | {row.get('reason')} |"
            )
    if report.get("side_won_negative_rows"):
        lines.extend(["", "## Side-Won Negative-PnL Rows", ""])
        lines.extend([
            "| market | side | p | ask | edge | net c | source | reason |",
            "|---|---|---:|---:|---:|---:|---|---|",
        ])
        for row in report.get("side_won_negative_rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_side'))} | "
                f"{fmt(row.get('ask_prob'))} | {fmt(row.get('edge_prob'))} | "
                f"{fmt(row.get('net_cents'))} | {row.get('source')} | {row.get('reason')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
