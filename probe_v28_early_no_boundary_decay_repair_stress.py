"""Stress audit for the frozen early-NO boundary decay repair entry candidate.

Research-only; no live bot changes or orders.

The runway report says this is one of the few broad-coverage positive forward
lanes. This audit asks the sharper anti-overfit question: how much of the
apparent edge comes from actual v28-approved evidence versus reconstructed
rejected-actionable rows?
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import row_net_after_fee, summarize
from probe_v28_frozen_early_no_boundary_decay_repair_entry import (
    MIN_SETTLED,
    build_candidate,
    compact,
    future_surfaces,
    load_or_create_state,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_early_no_boundary_decay_repair_stress_latest.json"
OUT_MD = OUT_DIR / "v28_early_no_boundary_decay_repair_stress_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def side(row: dict[str, Any]) -> str:
    return str(row.get("side") or "unknown").lower()


def market(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def net(row: dict[str, Any]) -> float | None:
    value = as_float(row.get("net_gross_cents_after_entry_fee"))
    if value is not None:
        return value
    return as_float(row.get("net_cents") if "net_cents" in row else row_net_after_fee(row))


def by_source(rows: list[dict[str, Any]], denominator: int) -> list[dict[str, Any]]:
    out = []
    for name in sorted({source(row) for row in rows}):
        subset = [row for row in rows if source(row) == name]
        summary = summarize(subset, denominator)
        out.append({"source": name, **summary})
    return out


def by_side(rows: list[dict[str, Any]], denominator: int) -> list[dict[str, Any]]:
    out = []
    for name in sorted({side(row) for row in rows}):
        subset = [row for row in rows if side(row) == name]
        summary = summarize(subset, denominator)
        out.append({"side": name, **summary})
    return out


def by_danger_reason(rows: list[dict[str, Any]], denominator: int) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        reasons = row.get("danger_reasons")
        if not isinstance(reasons, list) or not reasons:
            buckets["none"].append(row)
            continue
        for reason in reasons:
            buckets[str(reason)].append(row)
    return [{"reason": name, **summarize(items, denominator)} for name, items in sorted(buckets.items())]


def scenario(name: str, rows: list[dict[str, Any]], denominator: int, note: str) -> dict[str, Any]:
    return {"scenario": name, "note": note, **summarize(rows, denominator)}


def leave_one_market(rows: list[dict[str, Any]], denominator: int) -> list[dict[str, Any]]:
    base = summarize(rows, denominator)
    base_net = as_float(base.get("net_cents")) or 0.0
    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if market(row):
            by_market[market(row)].append(row)
    out = []
    for ticker, market_rows in by_market.items():
        removed_net = sum(net(row) or 0.0 for row in market_rows)
        remaining = [row for row in rows if market(row) != ticker]
        remaining_summary = summarize(remaining, denominator)
        out.append(
            {
                "market": ticker,
                "removed_rows": len(market_rows),
                "removed_net_cents": removed_net,
                "candidate_net_without_market_cents": remaining_summary.get("net_cents"),
                "delta_vs_full_cents": (as_float(remaining_summary.get("net_cents")) or 0.0) - base_net,
            }
        )
    return sorted(out, key=lambda row: float(row["candidate_net_without_market_cents"] or 0.0))[:10]


def future_loss_runway(candidate_rows: list[dict[str, Any]], denominator: int) -> list[dict[str, Any]]:
    summary = summarize(candidate_rows, denominator)
    net_cents = as_float(summary.get("net_cents")) or 0.0
    settled = int(as_float(summary.get("settled")) or 0)
    out = []
    for losses in range(1, 6):
        stressed_net = net_cents - 100.0 * losses
        stressed_settled = settled + losses
        out.append(
            {
                "added_full_losses": losses,
                "stressed_settled": stressed_settled,
                "stressed_net_cents": stressed_net,
                "still_positive": stressed_net > 0.0,
                "sample_gate_met": stressed_settled >= MIN_SETTLED,
            }
        )
    return out


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    all_rows, target, denominator = future_surfaces(str(state["freeze_ts_utc"]))
    built = build_candidate(all_rows, target, denominator)

    kept = built["kept"]
    danger = built["danger"]
    repairs = built["repairs"]
    candidate = built["candidate"]
    approved_repairs = [row for row in repairs if source(row) == "approved_entry"]
    rejected_repairs = [row for row in repairs if source(row) != "approved_entry"]
    approved_candidate_rows = [row for row in candidate if source(row) == "approved_entry"]
    rejected_candidate_rows = [row for row in candidate if source(row) != "approved_entry"]

    target_summary = summarize(target, denominator)
    candidate_summary = summarize(candidate, denominator)
    delta = (as_float(candidate_summary.get("net_cents")) or 0.0) - (as_float(target_summary.get("net_cents")) or 0.0)

    stress_scenarios = [
        scenario("target_control", target, denominator, "Original target-coverage policy surface."),
        scenario("candidate_full", candidate, denominator, "Frozen skip danger plus calm-geometry repairs."),
        scenario("skip_only_no_repairs", kept, denominator, "Remove danger rows but do not restore coverage."),
        scenario(
            "approved_repairs_only",
            kept + approved_repairs,
            denominator,
            "Remove danger rows and restore only with actual v28-approved repair rows.",
        ),
        scenario(
            "rejected_repairs_only",
            kept + rejected_repairs,
            denominator,
            "Remove danger rows and restore only with reconstructed rejected-actionable repair rows.",
        ),
        scenario(
            "approved_source_candidate_rows_only",
            approved_candidate_rows,
            denominator,
            "Not a tradable policy; source-quality view of candidate rows that were actual approved entries.",
        ),
        scenario(
            "rejected_source_candidate_rows_only",
            rejected_candidate_rows,
            denominator,
            "Not a tradable policy; source-quality view of candidate rows from rejected-actionable reconstruction.",
        ),
    ]

    danger_sources = by_source(danger, denominator)
    repair_sources = by_source(repairs, denominator)
    candidate_sources = by_source(candidate, denominator)
    all_danger_reconstructed = bool(danger) and all(source(row) != "approved_entry" for row in danger)
    rejected_repair_count = len(rejected_repairs)
    approved_repair_count = len(approved_repairs)

    warnings = []
    if all_danger_reconstructed:
        warnings.append(
            "All avoided danger rows are reconstructed rejected-actionable rows so far; this is useful physics evidence, but not enough live-approved proof."
        )
    if rejected_repair_count:
        warnings.append(
            f"{rejected_repair_count} repair rows are reconstructed; check approved-only repair performance before promotion."
        )
    if int(as_float(candidate_summary.get("settled")) or 0) < MIN_SETTLED:
        warnings.append("Sample-size gate is still open; wait for at least 30 settled candidate rows.")

    current_read = [
        f"Full candidate: {candidate_summary.get('settled')} settled, {candidate_summary.get('wins')}/{candidate_summary.get('losses')}, net {candidate_summary.get('net_cents')}c, coverage {candidate_summary.get('coverage_pct')}%.",
        f"Delta versus target: {delta}c.",
        f"Danger source mix: {Counter(source(row) for row in danger)}.",
        f"Repair source mix: {Counter(source(row) for row in repairs)}.",
    ]
    if warnings:
        current_read.extend(warnings)

    return {
        "freeze": state,
        "future_denominator": denominator,
        "target_summary": target_summary,
        "candidate_summary": candidate_summary,
        "delta_vs_target_cents": delta,
        "source_counts": {
            "target": dict(Counter(source(row) for row in target)),
            "danger": dict(Counter(source(row) for row in danger)),
            "kept": dict(Counter(source(row) for row in kept)),
            "repair": dict(Counter(source(row) for row in repairs)),
            "candidate": dict(Counter(source(row) for row in candidate)),
        },
        "side_counts": {
            "danger": dict(Counter(side(row) for row in danger)),
            "repair": dict(Counter(side(row) for row in repairs)),
            "candidate": dict(Counter(side(row) for row in candidate)),
        },
        "scenario_rows": stress_scenarios,
        "danger_source_summary": danger_sources,
        "repair_source_summary": repair_sources,
        "candidate_source_summary": candidate_sources,
        "danger_side_summary": by_side(danger, denominator),
        "repair_side_summary": by_side(repairs, denominator),
        "candidate_side_summary": by_side(candidate, denominator),
        "danger_reason_summary": by_danger_reason([compact(row) for row in danger], denominator),
        "leave_one_market_worst": leave_one_market(candidate, denominator),
        "future_loss_runway": future_loss_runway(candidate, denominator),
        "compact_rows": {
            "danger": [compact(row) for row in danger],
            "repair": [compact(row) for row in repairs],
        },
        "warnings": warnings,
        "current_read": current_read,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def summary_table(rows: list[dict[str, Any]], label_key: str) -> list[str]:
    lines = [
        f"| {label_key} | entries | settled | W/L | coverage | net c | avg c |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row.get(label_key)} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    return lines


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")

    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Early-NO Boundary Decay Repair Stress",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Delta versus target: `{fmt(report.get('delta_vs_target_cents'))}c`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("current_read") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Scenario Stress", ""])
    lines.extend(summary_table(report.get("scenario_rows") or [], "scenario"))
    lines.extend(["", "## Candidate Source Split", ""])
    lines.extend(summary_table(report.get("candidate_source_summary") or [], "source"))
    lines.extend(["", "## Danger Source Split", ""])
    lines.extend(summary_table(report.get("danger_source_summary") or [], "source"))
    lines.extend(["", "## Repair Source Split", ""])
    lines.extend(summary_table(report.get("repair_source_summary") or [], "source"))
    lines.extend(["", "## Danger Reason Split", ""])
    lines.extend(summary_table(report.get("danger_reason_summary") or [], "reason"))
    lines.extend(["", "## Future Full-Loss Runway", "", "| added full losses | stressed settled | stressed net c | still positive | sample gate met |", "|---:|---:|---:|---:|---:|"])
    for row in report.get("future_loss_runway") or []:
        lines.append(
            f"| {row.get('added_full_losses')} | {row.get('stressed_settled')} | "
            f"{fmt(row.get('stressed_net_cents'))} | {row.get('still_positive')} | {row.get('sample_gate_met')} |"
        )
    lines.extend(["", "## Worst Leave-One Market", "", "| market | removed rows | removed net c | net without market c | delta vs full c |", "|---|---:|---:|---:|---:|"])
    for row in report.get("leave_one_market_worst") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('removed_rows')} | {fmt(row.get('removed_net_cents'))} | "
            f"{fmt(row.get('candidate_net_without_market_cents'))} | {fmt(row.get('delta_vs_full_cents'))} |"
        )
    lines.extend(["", "## Warnings", ""])
    for warning in report.get("warnings") or ["none"]:
        lines.append(f"- {warning}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
