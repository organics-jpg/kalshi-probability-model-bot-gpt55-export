"""Autopsy the broad fixed-snapshot exit-hold pocket.

Research-only; no live bot changes or orders.

This explains the one harmful row in the broad observable hold rule by
comparing it with nearby selected rows and simple observable buckets.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SNAPSHOT_JSON = OUT_DIR / "v28_exit_clock_materialized_snapshot_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_clock_broad_hold_neighbor_autopsy_latest.json"
OUT_MD = OUT_DIR / "v28_exit_clock_broad_hold_neighbor_autopsy_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def base_rule(row: dict[str, Any]) -> bool:
    return (
        row.get("exit_fair_drawdown_cents") not in (None, "")
        and row.get("exit_cents") not in (None, "")
        and row.get("entry_ask_cents") not in (None, "")
        and fnum(row.get("exit_fair_drawdown_cents")) <= 5.0
        and fnum(row.get("exit_cents")) >= 50.0
        and fnum(row.get("entry_ask_cents")) <= 80.0
    )


def row_delta(row: dict[str, Any]) -> float:
    return fnum(row.get("hold_gross_cents")) - fnum(row.get("actual_gross_cents"))


def selected_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    helpful = [row for row in rows if row_delta(row) > 0]
    harmful = [row for row in rows if row_delta(row) < 0]
    flat = [row for row in rows if row_delta(row) == 0]
    new_losses = [row for row in rows if fnum(row.get("actual_gross_cents")) >= 0 > fnum(row.get("hold_gross_cents"))]
    loss_flips = [row for row in rows if fnum(row.get("actual_gross_cents")) < 0 <= fnum(row.get("hold_gross_cents"))]
    return {
        "rows": len(rows),
        "current_net_cents": sum(fnum(row.get("actual_gross_cents")) for row in rows),
        "hold_net_cents": sum(fnum(row.get("hold_gross_cents")) for row in rows),
        "delta_cents": sum(row_delta(row) for row in rows),
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "flat_rows": len(flat),
        "loss_flips": len(loss_flips),
        "new_losses": len(new_losses),
        "full_loss_cushion": int(max(0.0, sum(fnum(row.get("hold_gross_cents")) for row in rows)) // 100.0),
    }


def bucket_label(value: float, cuts: list[float], labels: list[str]) -> str:
    for cut, label in zip(cuts, labels):
        if value < cut:
            return label
    return labels[-1]


def bucket_rows(rows: list[dict[str, Any]], name: str, get_label) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(str(get_label(row)), []).append(row)
    out = []
    for label, members in sorted(groups.items()):
        summary = selected_summary(members)
        summary["bucket"] = label
        summary["feature"] = name
        out.append(summary)
    return out


def feature_distance(a: dict[str, Any], b: dict[str, Any]) -> float:
    specs = [
        ("entry_raw_edge_cents", 10.0),
        ("entry_ask_cents", 20.0),
        ("entry_abs_d_sigma", 1.0),
        ("exit_cents", 30.0),
        ("exit_p_hold", 0.3),
        ("exit_fair_drawdown_cents", 10.0),
    ]
    total = 0.0
    for key, scale in specs:
        total += ((fnum(a.get(key)) - fnum(b.get(key))) / scale) ** 2
    return math.sqrt(total)


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "entry_ts": row.get("entry_ts"),
        "actual_gross_cents": row.get("actual_gross_cents"),
        "hold_gross_cents": row.get("hold_gross_cents"),
        "delta_cents": row_delta(row),
        "entry_raw_edge_cents": row.get("entry_raw_edge_cents"),
        "entry_ask_cents": row.get("entry_ask_cents"),
        "entry_abs_d_sigma": row.get("entry_abs_d_sigma"),
        "exit_cents": row.get("exit_cents"),
        "exit_p_hold": row.get("exit_p_hold"),
        "exit_fair_drawdown_cents": row.get("exit_fair_drawdown_cents"),
        "exit_reason": row.get("exit_reason"),
    }


def build_report() -> dict[str, Any]:
    snapshot = load_json(SNAPSHOT_JSON)
    rows = [
        row for row in snapshot.get("rows") or []
        if isinstance(row, dict)
        and row.get("actual_gross_cents") is not None
        and row.get("hold_gross_cents") is not None
    ]
    selected = [row for row in rows if base_rule(row)]
    harmful = sorted([row for row in selected if row_delta(row) < 0], key=row_delta)
    worst = harmful[0] if harmful else {}
    helpful = [row for row in selected if row_delta(row) > 0]
    neighbors = []
    if worst:
        for row in sorted(helpful, key=lambda item: feature_distance(worst, item))[:8]:
            neighbor = compact_row(row)
            neighbor["distance"] = feature_distance(worst, row)
            neighbors.append(neighbor)
    low_edge = [row for row in selected if fnum(row.get("entry_raw_edge_cents")) < 7.0]
    high_edge = [row for row in selected if fnum(row.get("entry_raw_edge_cents")) >= 7.0]
    buckets = []
    buckets.extend(bucket_rows(
        selected,
        "entry_raw_edge_cents",
        lambda row: bucket_label(
            fnum(row.get("entry_raw_edge_cents")),
            [5.0, 6.0, 7.0, 8.0, 10.0],
            ["lt5", "5_6", "6_7", "7_8", "8_10", "gte10"],
        ),
    ))
    buckets.extend(bucket_rows(
        selected,
        "entry_ask_cents",
        lambda row: bucket_label(
            fnum(row.get("entry_ask_cents")),
            [55.0, 65.0, 75.0, 81.0],
            ["lt55", "55_65", "65_75", "75_80", "gte81"],
        ),
    ))
    buckets.extend(bucket_rows(
        selected,
        "exit_cents",
        lambda row: bucket_label(
            fnum(row.get("exit_cents")),
            [60.0, 70.0, 80.0],
            ["50_60", "60_70", "70_80", "gte80"],
        ),
    ))
    buckets.extend(bucket_rows(
        selected,
        "exit_p_hold",
        lambda row: bucket_label(
            fnum(row.get("exit_p_hold")),
            [0.65, 0.75, 0.85],
            ["lt65", "65_75", "75_85", "gte85"],
        ),
    ))
    blockers = ["research_only", "not_frozen_forward", "diagnostic_snapshot_autopsy"]
    if selected_summary(high_edge).get("rows", 0) < 30:
        blockers.append("clean_high_edge_survivor_lt_30")
    if selected_summary(low_edge).get("harmful_rows"):
        blockers.append("low_edge_slice_contains_false_hold")
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_snapshot": str(SNAPSHOT_JSON),
        "snapshot_generated_at_utc": snapshot.get("generated_at_utc"),
        "base_rule": "exit_fair_drawdown_cents <= 5 and exit_cents >= 50 and entry_ask_cents <= 80",
        "all_selected_summary": selected_summary(selected),
        "low_edge_lt7_summary": selected_summary(low_edge),
        "high_edge_ge7_summary": selected_summary(high_edge),
        "worst_harmful_row": compact_row(worst) if worst else {},
        "nearest_helpful_neighbors": neighbors,
        "buckets": buckets,
        "blockers": blockers,
        "interpretation": [
            "The broad hold pocket's damage is concentrated in a single low-edge false hold, but the low-edge slice also contains useful clipped-winner recovery.",
            "A hard raw-edge guard removes the false hold but leaves fewer than 30 selected decisions.",
            "This supports mechanism research around entry confidence plus exit-state hold value, not a freezeable rule from the fixed snapshot.",
        ],
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    all_summary = report.get("all_selected_summary") or {}
    low = report.get("low_edge_lt7_summary") or {}
    high = report.get("high_edge_ge7_summary") or {}
    worst = report.get("worst_harmful_row") or {}
    lines = [
        "# v28 Exit-Clock Broad Hold Neighbor Autopsy",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Base rule: `{report.get('base_rule')}`",
        f"- Broad selected/delta/helpful-harmful-newloss: `{all_summary.get('rows')}` / `{money(all_summary.get('delta_cents'))}` / `{all_summary.get('helpful_rows')}-{all_summary.get('harmful_rows')}-{all_summary.get('new_losses')}`",
        f"- Low-edge <7 selected/delta/helpful-harmful-newloss: `{low.get('rows')}` / `{money(low.get('delta_cents'))}` / `{low.get('helpful_rows')}-{low.get('harmful_rows')}-{low.get('new_losses')}`",
        f"- High-edge >=7 selected/delta/helpful-harmful-newloss: `{high.get('rows')}` / `{money(high.get('delta_cents'))}` / `{high.get('helpful_rows')}-{high.get('harmful_rows')}-{high.get('new_losses')}`",
        f"- Worst harmful row: `{worst.get('market')}` / `{worst.get('side')}` / delta `{money(worst.get('delta_cents'))}` / raw edge `{worst.get('entry_raw_edge_cents')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or [])}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Buckets",
        "",
        "| feature | bucket | rows | delta | helpful/harmful/new losses | cushion |",
        "|---|---|---:|---:|---:|---:|",
    ])
    for row in report.get("buckets") or []:
        lines.append(
            f"| `{row.get('feature')}` | `{row.get('bucket')}` | {row.get('rows')} | "
            f"{money(row.get('delta_cents'))} | {row.get('helpful_rows')}/{row.get('harmful_rows')}/{row.get('new_losses')} | "
            f"{row.get('full_loss_cushion')} |"
        )
    lines.extend([
        "",
        "## Nearest Helpful Neighbors",
        "",
        "| market | side | distance | delta | raw edge | ask | exit | p_hold | fair drawdown |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("nearest_helpful_neighbors") or []:
        lines.append(
            f"| `{row.get('market')}` | `{row.get('side')}` | {fnum(row.get('distance')):.3f} | "
            f"{money(row.get('delta_cents'))} | {fnum(row.get('entry_raw_edge_cents')):.3f} | "
            f"{fnum(row.get('entry_ask_cents')):.0f} | {fnum(row.get('exit_cents')):.0f} | "
            f"{fnum(row.get('exit_p_hold')):.3f} | {fnum(row.get('exit_fair_drawdown_cents')):.3f} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
