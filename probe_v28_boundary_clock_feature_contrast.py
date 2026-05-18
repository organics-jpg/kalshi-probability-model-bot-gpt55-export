"""Feature contrast for boundary-clock approved-source frontier.

Research-only; no live bot changes or orders.

The approved-source frontier is not deployable because it uses a source label.
This report compares observable features of current approved rows, current
reconstructed rows, and the approved-source frontier to suggest pre-entry gates
worth testing.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import raw_edge, row_net_after_fee
from probe_v28_frozen_boundary_clock_fv_entry_bridge import (
    build_candidate as build_bridge_candidate,
    future_surfaces as bridge_surfaces,
    load_json as bridge_load_json,
)
from probe_v28_frozen_boundary_clock_repair_entry import (
    build_candidate as build_entry_candidate,
    future_surfaces as entry_surfaces,
    load_json as entry_load_json,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
ENTRY_STATE_JSON = OUT_DIR / "v28_frozen_boundary_clock_repair_entry_state.json"
BRIDGE_STATE_JSON = OUT_DIR / "v28_frozen_boundary_clock_fv_entry_bridge_state.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_contrast_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_contrast_latest.md"

FEATURES = ("raw_edge", "recross_hazard_score", "abs_d_sigma", "seconds_to_close", "ask_prob", "net_cents")


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def market(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def feature(row: dict[str, Any], name: str) -> float | None:
    if name == "raw_edge":
        return raw_edge(row)
    if name == "net_cents":
        return row_net_after_fee(row)
    return as_float(row.get(name))


def feature_stats(rows: list[dict[str, Any]], name: str) -> dict[str, Any]:
    values = sorted(value for row in rows if (value := feature(row, name)) is not None)
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "mean": mean(values),
        "median": median(values),
        "min": values[0],
        "p25": values[int((len(values) - 1) * 0.25)],
        "p75": values[int((len(values) - 1) * 0.75)],
        "max": values[-1],
    }


def best_approved_per_market(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if source(row) == "approved_entry" and market(row):
            grouped[market(row)].append(row)
    return [max(items, key=lambda row: feature(row, "raw_edge") or -999.0) for items in grouped.values()]


def group_summary(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    net = sum(float(feature(row, "net_cents") or 0.0) for row in rows)
    wins = sum(1 for row in rows if row.get("side_won") is True)
    losses = sum(1 for row in rows if row.get("side_won") is False)
    return {
        "group": name,
        "rows": len(rows),
        "markets": len({market(row) for row in rows}),
        "wins": wins,
        "losses": losses,
        "net_cents": net,
        "features": {feature_name: feature_stats(rows, feature_name) for feature_name in FEATURES},
    }


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Any, build_fn: Any) -> dict[str, Any]:
    all_rows, target, denominator = surfaces_fn(freeze_ts)
    built = build_fn(all_rows, target, denominator)
    candidate = built["candidate"]
    groups = [
        group_summary("current_candidate_approved", [row for row in candidate if source(row) == "approved_entry"]),
        group_summary("current_candidate_reconstructed", [row for row in candidate if source(row) != "approved_entry"]),
        group_summary("approved_source_raw_edge_frontier", best_approved_per_market(all_rows)),
    ]
    return {
        "lane": label,
        "freeze_ts": freeze_ts,
        "future_denominator": denominator,
        "groups": groups,
        "hypotheses": hypotheses(groups),
    }


def hypotheses(groups: list[dict[str, Any]]) -> list[str]:
    approved = next((row for row in groups if row.get("group") == "current_candidate_approved"), {})
    reconstructed = next((row for row in groups if row.get("group") == "current_candidate_reconstructed"), {})
    out = []
    for feature_name, direction in [
        ("raw_edge", "higher"),
        ("recross_hazard_score", "lower"),
        ("abs_d_sigma", "higher"),
        ("ask_prob", "higher"),
    ]:
        a = ((approved.get("features") or {}).get(feature_name) or {}).get("median")
        r = ((reconstructed.get("features") or {}).get(feature_name) or {}).get("median")
        if a is None or r is None:
            continue
        if direction == "higher" and a > r:
            out.append(f"Test {feature_name} floor: approved median {a:.4f} > reconstructed median {r:.4f}.")
        if direction == "lower" and a < r:
            out.append(f"Test {feature_name} cap: approved median {a:.4f} < reconstructed median {r:.4f}.")
    return out


def build_report() -> dict[str, Any]:
    entry_state = entry_load_json(ENTRY_STATE_JSON)
    bridge_state = bridge_load_json(BRIDGE_STATE_JSON)
    lanes = []
    if entry_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("boundary_clock_repair_entry", str(entry_state["freeze_ts_utc"]), entry_surfaces, build_entry_candidate))
    if bridge_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("boundary_clock_fv_entry_bridge", str(bridge_state["freeze_ts_utc"]), bridge_surfaces, build_bridge_candidate))
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Observable-feature contrast for learning from approved-source boundary-clock rows.",
        "lanes": lanes,
        "interpretation": interpretation(lanes),
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = []
    for lane in lanes:
        for note in lane.get("hypotheses") or []:
            notes.append(f"{lane.get('lane')}: {note}")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Boundary-Clock Feature Contrast",
        "",
        "Research-only; learns from approved-source rows without changing live logic.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                "| group | rows | markets | W/L | net c | raw edge med | recross med | abs d med | stc med | ask med |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for group in lane.get("groups") or []:
            features = group.get("features") or {}
            lines.append(
                f"| {group.get('group')} | {group.get('rows')} | {group.get('markets')} | "
                f"{group.get('wins')}/{group.get('losses')} | {fmt(group.get('net_cents'))} | "
                f"{fmt((features.get('raw_edge') or {}).get('median'))} | "
                f"{fmt((features.get('recross_hazard_score') or {}).get('median'))} | "
                f"{fmt((features.get('abs_d_sigma') or {}).get('median'))} | "
                f"{fmt((features.get('seconds_to_close') or {}).get('median'))} | "
                f"{fmt((features.get('ask_prob') or {}).get('median'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
