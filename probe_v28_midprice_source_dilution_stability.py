"""Stability stress for the midprice source-dilution watch.

Research-only; no live bot changes or orders.

The source-dilution repair is attractive because it fixes a near-gate source
blocker with one observable weak-boundary rule. That also makes it fragile by
construction. This probe stress-tests whether the parent diagnostic result is
top-win dependent or merely a lucky one-row removal.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import as_float, load_json, source
from probe_v28_midprice_source_dilution_watch import (
    FILTERS,
    MIDPRICE_JSON,
    OUT_DIR,
    passes_filter,
    row_view,
    rows_from_artifact,
)


OUT_JSON = OUT_DIR / "v28_midprice_source_dilution_stability_latest.json"
OUT_MD = OUT_DIR / "v28_midprice_source_dilution_stability_latest.md"

TARGET_FILTER = "absd_gte_055_or_ask_gte_065"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def net(row: dict[str, Any]) -> float:
    return fnum(row.get("weighted_net_cents"))


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = sum(net(row) for row in rows)
    return {
        "rows": len(rows),
        "wins": sum(1 for row in rows if net(row) > 0),
        "losses": sum(1 for row in rows if net(row) < 0),
        "net_cents": total,
        "avg_net_cents": total / len(rows) if rows else 0.0,
        "full_loss_cushion": int(max(0.0, total) // 100.0),
        "top_win_cents": max((net(row) for row in rows), default=0.0),
        "worst_loss_cents": min((net(row) for row in rows), default=0.0),
        "net_without_top_win_cents": total - max((net(row) for row in rows), default=0.0),
        "net_without_top_two_wins_cents": total - sum(sorted([net(row) for row in rows if net(row) > 0], reverse=True)[:2]),
        "net_without_top_loss_saved_cents": total + min((net(row) for row in rows), default=0.0),
    }


def source_split(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[source(row)].append(row)
    return {name: summarize(items) for name, items in groups.items()}


def feature_bins(rows: list[dict[str, Any]]) -> dict[str, Any]:
    bins: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        abs_d = fnum(row.get("abs_d_sigma"))
        ask = fnum(row.get("ask_prob"))
        recross = fnum(row.get("recross_hazard_score"))
        if abs_d < 0.65:
            bins["absd_lt065"].append(row)
        elif abs_d < 0.85:
            bins["absd_065_085"].append(row)
        else:
            bins["absd_gte085"].append(row)
        if ask < 0.55:
            bins["ask_lt055"].append(row)
        elif ask < 0.65:
            bins["ask_055_065"].append(row)
        else:
            bins["ask_gte065"].append(row)
        if recross > 0.30:
            bins["recross_gt030"].append(row)
        else:
            bins["recross_lte030"].append(row)
    return {name: summarize(items) for name, items in sorted(bins.items())}


def leave_one_out(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    nets = []
    for idx, row in enumerate(rows):
        others = rows[:idx] + rows[idx + 1 :]
        nets.append({
            "removed_market": row.get("market"),
            "removed_side": row.get("side"),
            "removed_source": row.get("source"),
            "removed_net_cents": net(row),
            "net_after_removal_cents": sum(net(item) for item in others),
            "cushion_after_removal": int(max(0.0, sum(net(item) for item in others)) // 100.0),
        })
    return {
        "min_net_after_removal_cents": min(item["net_after_removal_cents"] for item in nets),
        "max_net_after_removal_cents": max(item["net_after_removal_cents"] for item in nets),
        "min_cushion_after_removal": min(item["cushion_after_removal"] for item in nets),
        "top_win_dependency": sorted(nets, key=lambda item: item["net_after_removal_cents"])[:5],
        "top_loss_relief": sorted(nets, key=lambda item: item["net_after_removal_cents"], reverse=True)[:5],
    }


def ordered_rows(lane_name: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    rows, denominator = rows_from_artifact(lane_name)
    rule = FILTERS[TARGET_FILTER]
    viewed = [row_view(row) for row in rows]
    kept = [row for row in viewed if passes_filter(row, rule)]
    dropped = [row for row in viewed if not passes_filter(row, rule)]
    return kept, dropped, denominator


def build_lane(lane_name: str) -> dict[str, Any]:
    kept, dropped, denominator = ordered_rows(lane_name)
    coverage = 100.0 * len(kept) / denominator if denominator else None
    source_counts = Counter(row.get("source") for row in kept)
    reconstructed = 1.0 - (source_counts.get("approved_entry", 0) / len(kept)) if kept else None
    return {
        "lane": lane_name,
        "target_filter": TARGET_FILTER,
        "denominator": denominator,
        "coverage_pct": coverage,
        "reconstructed_share": reconstructed,
        "source_counts": dict(source_counts),
        "kept_summary": summarize(kept),
        "dropped_summary": summarize(dropped),
        "source_split": source_split(kept),
        "feature_bins": feature_bins(kept),
        "leave_one_out": leave_one_out(kept),
        "dropped_rows": sorted(dropped, key=net),
        "worst_kept_rows": sorted(kept, key=net)[:10],
        "best_kept_rows": sorted(kept, key=net, reverse=True)[:10],
        "stability_flags": stability_flags(kept, dropped, reconstructed, coverage),
    }


def stability_flags(
    kept: list[dict[str, Any]],
    dropped: list[dict[str, Any]],
    reconstructed_share: float | None,
    coverage: float | None,
) -> list[str]:
    flags: list[str] = []
    summary = summarize(kept)
    if len(dropped) <= 1:
        flags.append("single_row_diagnostic_repair")
    if summary["net_without_top_win_cents"] < 300:
        flags.append("top_win_dependency_watch")
    if summary["net_without_top_two_wins_cents"] < 200:
        flags.append("top_two_win_dependency_watch")
    if summary["full_loss_cushion"] < 4:
        flags.append("thin_cushion_margin")
    if reconstructed_share is not None and reconstructed_share > 0.33:
        flags.append("source_share_close_to_gate")
    if coverage is not None and coverage < 77.0:
        flags.append("coverage_close_to_floor")
    return flags


def build_report() -> dict[str, Any]:
    parent = load_json(MIDPRICE_JSON)
    return {
        "generated_at_utc": utc_now_iso(),
        "source_artifact": str(MIDPRICE_JSON),
        "parent_generated_at_utc": parent.get("generated_at_utc"),
        "target_filter": TARGET_FILTER,
        "lanes": [
            build_lane("post_feature_freeze_entry"),
        ],
        "interpretation": [],
    }


def money(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number:.1f}c"


def pct(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    if number <= 1.0:
        number *= 100.0
    return f"{number:.2f}%"


def write_report(report: dict[str, Any]) -> None:
    lanes = report.get("lanes") or []
    notes = [
        "This is a parent diagnostic stability stress, not promotion evidence.",
        "The target dilution rule remains newly frozen; strict post-birth rows must validate it.",
    ]
    for lane in lanes:
        kept = lane.get("kept_summary") or {}
        dropped = lane.get("dropped_summary") or {}
        notes.append(
            f"{lane.get('lane')}: kept {kept.get('rows')} rows for {kept.get('net_cents')}c, "
            f"net without top win {kept.get('net_without_top_win_cents')}c, "
            f"dropped {dropped.get('rows')} rows for {dropped.get('net_cents')}c, "
            f"flags {lane.get('stability_flags')}."
        )
    report["interpretation"] = notes
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Midprice Source-Dilution Stability",
        "",
        "Research-only. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Target filter: `{report.get('target_filter')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in notes)
    for lane in lanes:
        kept = lane.get("kept_summary") or {}
        dropped = lane.get("dropped_summary") or {}
        loo = lane.get("leave_one_out") or {}
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            f"- Coverage: `{pct(lane.get('coverage_pct'))}`",
            f"- Reconstructed share: `{pct(lane.get('reconstructed_share'))}`",
            f"- Source counts: `{lane.get('source_counts')}`",
            f"- Kept summary: `{kept}`",
            f"- Dropped summary: `{dropped}`",
            f"- Leave-one-out: `{loo}`",
            f"- Stability flags: `{lane.get('stability_flags')}`",
            "",
            "### Source Split",
            "",
            "| source | rows | W/L | net | top win | worst loss | net ex top win | cushion |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for name, summary in (lane.get("source_split") or {}).items():
            lines.append(
                f"| `{name}` | {summary.get('rows')} | {summary.get('wins')}/{summary.get('losses')} | "
                f"{money(summary.get('net_cents'))} | {money(summary.get('top_win_cents'))} | "
                f"{money(summary.get('worst_loss_cents'))} | {money(summary.get('net_without_top_win_cents'))} | "
                f"{summary.get('full_loss_cushion')} |"
            )
        lines.extend([
            "",
            "### Dropped Rows",
            "",
            "| market | side | source | net | abs_d | ask | recross |",
            "|---|---|---|---:|---:|---:|---:|",
        ])
        for row in lane.get("dropped_rows") or []:
            lines.append(
                f"| `{row.get('market')}` | `{row.get('side')}` | `{row.get('source')}` | "
                f"{money(row.get('weighted_net_cents'))} | {row.get('abs_d_sigma')} | "
                f"{row.get('ask_prob')} | {row.get('recross_hazard_score')} |"
            )
        lines.extend([
            "",
            "### Worst Kept Rows",
            "",
            "| market | side | source | net | abs_d | ask | recross |",
            "|---|---|---|---:|---:|---:|---:|",
        ])
        for row in lane.get("worst_kept_rows") or []:
            lines.append(
                f"| `{row.get('market')}` | `{row.get('side')}` | `{row.get('source')}` | "
                f"{money(row.get('weighted_net_cents'))} | {row.get('abs_d_sigma')} | "
                f"{row.get('ask_prob')} | {row.get('recross_hazard_score')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_report(report)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
