"""Source stress audit for frozen boundary-clock entry candidates.

Research-only; no live bot changes or orders.

Boundary-clock repair is near the 30-settled gate and broad enough, but its
current PnL cushion is thin. This report audits source mix, clean-row dilution
needs, and full-loss runway for the entry rule and FV-entry bridge.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import (
    build_candidate as build_bridge_candidate,
    future_surfaces as bridge_surfaces,
    load_json as load_bridge_json,
)
from probe_v28_frozen_boundary_clock_repair_entry import (
    build_candidate as build_entry_candidate,
    future_surfaces as entry_surfaces,
    load_json as load_entry_json,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
ENTRY_STATE_JSON = OUT_DIR / "v28_frozen_boundary_clock_repair_entry_state.json"
BRIDGE_STATE_JSON = OUT_DIR / "v28_frozen_boundary_clock_fv_entry_bridge_state.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_source_stress_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_source_stress_latest.md"

MIN_SETTLED = 30
COVERAGE_FLOOR = 75.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def row_source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(row_source(row) for row in rows))


def reconstructed_share(counts: dict[str, int]) -> float | None:
    total = sum(counts.values())
    if total <= 0:
        return None
    return (total - int(counts.get("approved_entry") or 0)) / total


def approved_needed_for_recon35(counts: dict[str, int]) -> int:
    total = sum(counts.values())
    if total <= 0:
        return 0
    approved = int(counts.get("approved_entry") or 0)
    reconstructed = total - approved
    share = reconstructed / total
    if share <= MAX_RECONSTRUCTED_SHARE:
        return 0
    return int(math.ceil((reconstructed / MAX_RECONSTRUCTED_SHARE) - total))


def full_loss_runway(net_cents: float | None, settled: int) -> list[dict[str, Any]]:
    base = float(net_cents or 0.0)
    out = []
    for losses in range(1, 6):
        stressed = base - 100.0 * losses
        out.append(
            {
                "added_full_losses": losses,
                "stressed_settled": settled + losses,
                "stressed_net_cents": stressed,
                "still_positive": stressed > 0.0,
            }
        )
    return out


def split_by_source(rows: list[dict[str, Any]], denominator: int) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row_source(row), []).append(row)
    out = []
    for source, items in grouped.items():
        row = summarize(items, denominator)
        row["source"] = source
        out.append(row)
    return sorted(out, key=lambda row: str(row.get("source") or ""))


def audit_lane(name: str, freeze_ts: str, surfaces_fn: Any, build_fn: Any, removed_key: str) -> dict[str, Any]:
    all_rows, target, denominator = surfaces_fn(freeze_ts)
    built = build_fn(all_rows, target, denominator)
    candidate = built["candidate"]
    repairs = built["repairs"]
    removed = built[removed_key]
    summary = summarize(candidate, denominator)
    counts = source_counts(candidate)
    repair_counts = source_counts(repairs)
    removed_counts = source_counts(removed)
    settled = int(as_float(summary.get("settled")) or 0)
    coverage = as_float(summary.get("coverage_pct"))
    net = as_float(summary.get("net_cents"))
    future_rows_for_sample = max(0, MIN_SETTLED - settled)
    future_rows_for_source = approved_needed_for_recon35(counts)
    future_rows_for_gate = max(future_rows_for_sample, future_rows_for_source)
    blockers = []
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_FLOOR:
        blockers.append("coverage_too_low")
    if net is None or net <= 0:
        blockers.append("net_not_positive")
    share = reconstructed_share(counts)
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    cushion = int(max(0.0, float(net or 0.0)) // 100.0)
    if cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "lane": name,
        "freeze_ts": freeze_ts,
        "future_denominator": denominator,
        "candidate_summary": summary,
        "source_counts": counts,
        "repair_source_counts": repair_counts,
        "removed_source_counts": removed_counts,
        "reconstructed_share": share,
        "full_loss_cushion_estimate": cushion,
        "future_approved_rows_for_recon35": future_rows_for_source,
        "future_clean_rows_for_sample_source_gate": future_rows_for_gate,
        "source_split": split_by_source(candidate, denominator),
        "repair_source_split": split_by_source(repairs, denominator),
        "removed_source_split": split_by_source(removed, denominator),
        "full_loss_runway": full_loss_runway(net, settled),
        "blockers": blockers,
    }


def build_report() -> dict[str, Any]:
    entry_state = load_entry_json(ENTRY_STATE_JSON)
    bridge_state = load_bridge_json(BRIDGE_STATE_JSON)
    lanes = []
    if entry_state.get("freeze_ts_utc"):
        lanes.append(
            audit_lane(
                "boundary_clock_repair_entry",
                str(entry_state["freeze_ts_utc"]),
                entry_surfaces,
                build_entry_candidate,
                "danger",
            )
        )
    if bridge_state.get("freeze_ts_utc"):
        lanes.append(
            audit_lane(
                "boundary_clock_fv_entry_bridge",
                str(bridge_state["freeze_ts_utc"]),
                bridge_surfaces,
                build_bridge_candidate,
                "skipped",
            )
        )
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Source and full-loss stress for frozen boundary-clock entry lanes.",
        "requirements": {
            "min_settled": MIN_SETTLED,
            "coverage_floor": COVERAGE_FLOOR,
            "max_reconstructed_share": MAX_RECONSTRUCTED_SHARE,
            "min_full_loss_cushion": MIN_FULL_LOSS_CUSHION,
        },
        "lanes": lanes,
        "interpretation": interpretation(lanes),
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = []
    for lane in lanes:
        summary = lane.get("candidate_summary") or {}
        notes.append(
            f"{lane.get('lane')}: {summary.get('settled')} settled, coverage {summary.get('coverage_pct')}%, net {summary.get('net_cents')}c, reconstructed share {lane.get('reconstructed_share')}, clean rows needed for sample/source gate {lane.get('future_clean_rows_for_sample_source_gate')}, blockers {lane.get('blockers')}."
        )
    if lanes and all("full_loss_cushion_lt_3" in (lane.get("blockers") or []) for lane in lanes):
        notes.append("Boundary-clock remains promising but thin: one full-loss row can erase current positive PnL.")
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
        "# v28 Boundary-Clock Source Stress",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Lane Summary",
            "",
            "| lane | settled | coverage | net c | W/L | recon share | source counts | repair counts | clean rows to gate | full-loss cushion | blockers |",
            "|---|---:|---:|---:|---:|---:|---|---|---:|---:|---|",
        ]
    )
    for lane in report.get("lanes") or []:
        summary = lane.get("candidate_summary") or {}
        lines.append(
            f"| {lane.get('lane')} | {summary.get('settled')} | {fmt(summary.get('coverage_pct'))} | "
            f"{fmt(summary.get('net_cents'))} | {summary.get('wins')}/{summary.get('losses')} | "
            f"{fmt(lane.get('reconstructed_share'))} | {lane.get('source_counts')} | {lane.get('repair_source_counts')} | "
            f"{lane.get('future_clean_rows_for_sample_source_gate')} | {lane.get('full_loss_cushion_estimate')} | "
            f"{', '.join(lane.get('blockers') or []) or 'none'} |"
        )
    for lane in report.get("lanes") or []:
        lines.extend(
            [
                "",
                f"## {lane.get('lane')} Source Split",
                "",
                "| slice | source | entries | settled | W/L | coverage | net c | avg c |",
                "|---|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for slice_name, key in [
            ("candidate", "source_split"),
            ("repairs", "repair_source_split"),
            ("removed", "removed_source_split"),
        ]:
            for row in lane.get(key) or []:
                lines.append(
                    f"| {slice_name} | {row.get('source')} | {row.get('entries')} | {row.get('settled')} | "
                    f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
                    f"{fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
                )
        lines.extend(
            [
                "",
                f"## {lane.get('lane')} Full-Loss Runway",
                "",
                "| added full losses | stressed settled | stressed net c | still positive |",
                "|---:|---:|---:|---|",
            ]
        )
        for row in lane.get("full_loss_runway") or []:
            lines.append(
                f"| {row.get('added_full_losses')} | {row.get('stressed_settled')} | "
                f"{fmt(row.get('stressed_net_cents'))} | {row.get('still_positive')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
