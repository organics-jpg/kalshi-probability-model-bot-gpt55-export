"""Stress audit for the Goldilocks-edge repair hypothesis.

Research-only; no live bot changes or orders.

The frozen candidate starts with no future rows. This stress report therefore
audits the diagnostic evidence separately from promotion evidence, focusing on
source mix and loss fragility so the large diagnostic delta does not fool us.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import row_net_after_fee, summarize
from probe_v28_frozen_goldilocks_edge_repair_entry import (
    MIN_SETTLED,
    build_candidate,
    compact,
    diagnostic_rows,
    load_or_create_state,
    rows_for_freeze,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_goldilocks_edge_repair_stress_latest.json"
OUT_MD = OUT_DIR / "v28_goldilocks_edge_repair_stress_latest.md"


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


def net(row: dict[str, Any]) -> float:
    direct = as_float(row.get("net_gross_cents_after_entry_fee"))
    if direct is not None:
        return direct
    compact_net = as_float(row.get("net_cents"))
    if compact_net is not None:
        return compact_net
    return as_float(row_net_after_fee(row)) or 0.0


def by_source(rows: list[dict[str, Any]], denominator: int) -> list[dict[str, Any]]:
    out = []
    for value in sorted({source(row) for row in rows}):
        subset = [row for row in rows if source(row) == value]
        out.append({"source": value, **summarize(subset, denominator)})
    return out


def by_side(rows: list[dict[str, Any]], denominator: int) -> list[dict[str, Any]]:
    out = []
    for value in sorted({side(row) for row in rows}):
        subset = [row for row in rows if side(row) == value]
        out.append({"side": value, **summarize(subset, denominator)})
    return out


def scenario(name: str, rows: list[dict[str, Any]], denominator: int, note: str) -> dict[str, Any]:
    return {"scenario": name, "note": note, **summarize(rows, denominator)}


def leave_one_market(rows: list[dict[str, Any]], denominator: int) -> list[dict[str, Any]]:
    base = summarize(rows, denominator)
    base_net = as_float(base.get("net_cents")) or 0.0
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if market(row):
            grouped[market(row)].append(row)
    out = []
    for ticker, market_rows in grouped.items():
        remaining = [row for row in rows if market(row) != ticker]
        remaining_net = as_float(summarize(remaining, denominator).get("net_cents")) or 0.0
        out.append(
            {
                "market": ticker,
                "removed_rows": len(market_rows),
                "removed_net_cents": sum(net(row) for row in market_rows),
                "candidate_net_without_market_cents": remaining_net,
                "delta_vs_full_cents": remaining_net - base_net,
            }
        )
    return sorted(out, key=lambda row: float(row["candidate_net_without_market_cents"]))[:10]


def full_loss_runway(candidate_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary = summarize(candidate_rows, 1)
    base_net = as_float(summary.get("net_cents")) or 0.0
    settled = int(as_float(summary.get("settled")) or 0)
    out = []
    for losses in range(1, 6):
        stressed_net = base_net - 100.0 * losses
        out.append(
            {
                "added_full_losses": losses,
                "stressed_settled": settled + losses,
                "stressed_net_cents": stressed_net,
                "still_positive": stressed_net > 0.0,
                "sample_gate_met": settled + losses >= MIN_SETTLED,
            }
        )
    return out


def scenario_bundle(label: str, all_rows: list[dict[str, Any]], target: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    built = build_candidate(all_rows, target, denominator)
    kept = built["kept"]
    danger = built["danger"]
    repairs = built["repairs"]
    candidate = built["candidate"]
    approved_repairs = [row for row in repairs if source(row) == "approved_entry"]
    rejected_repairs = [row for row in repairs if source(row) != "approved_entry"]
    approved_candidate = [row for row in candidate if source(row) == "approved_entry"]
    rejected_candidate = [row for row in candidate if source(row) != "approved_entry"]
    target_summary = summarize(target, denominator)
    candidate_summary = summarize(candidate, denominator)
    delta = (as_float(candidate_summary.get("net_cents")) or 0.0) - (as_float(target_summary.get("net_cents")) or 0.0)
    warnings = []
    if danger and all(source(row) != "approved_entry" for row in danger):
        warnings.append("All avoided danger rows are reconstructed rejected-actionable rows so far.")
    if rejected_repairs:
        warnings.append(f"{len(rejected_repairs)} repair rows are reconstructed.")
    if int(as_float(candidate_summary.get("settled")) or 0) < MIN_SETTLED:
        warnings.append("Sample-size gate is still open.")
    if (as_float(candidate_summary.get("net_cents")) or 0.0) - 200.0 <= 0.0:
        warnings.append("Two ordinary full losses would erase current positive net.")
    return {
        "label": label,
        "denominator": denominator,
        "target_summary": target_summary,
        "candidate_summary": candidate_summary,
        "delta_vs_target_cents": delta,
        "source_counts": {
            "target": dict(Counter(source(row) for row in target)),
            "danger": dict(Counter(source(row) for row in danger)),
            "repair": dict(Counter(source(row) for row in repairs)),
            "candidate": dict(Counter(source(row) for row in candidate)),
        },
        "scenario_rows": [
            scenario("target_control", target, denominator, "Original target-coverage surface."),
            scenario("candidate_full", candidate, denominator, "Goldilocks false-edge skip plus repairs."),
            scenario("skip_only_no_repairs", kept, denominator, "Remove false-edge rows without restoring coverage."),
            scenario("approved_repairs_only", kept + approved_repairs, denominator, "Repair only with actual approved-entry rows."),
            scenario("rejected_repairs_only", kept + rejected_repairs, denominator, "Repair only with reconstructed rows."),
            scenario("approved_source_candidate_rows_only", approved_candidate, denominator, "Source-quality view only."),
            scenario("rejected_source_candidate_rows_only", rejected_candidate, denominator, "Source-quality view only."),
        ],
        "candidate_source_summary": by_source(candidate, denominator),
        "danger_source_summary": by_source(danger, denominator),
        "repair_source_summary": by_source(repairs, denominator),
        "candidate_side_summary": by_side(candidate, denominator),
        "danger_side_summary": by_side(danger, denominator),
        "repair_side_summary": by_side(repairs, denominator),
        "leave_one_market_worst": leave_one_market(candidate, denominator),
        "full_loss_runway": full_loss_runway(candidate),
        "compact_rows": {
            "danger": [compact(row) for row in danger],
            "repair": [compact(row) for row in repairs],
        },
        "warnings": warnings,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    diag_all, diag_target, diag_denominator = diagnostic_rows()
    fut_all, fut_target, fut_denominator = rows_for_freeze(str(state["freeze_ts_utc"]))
    diagnostic = scenario_bundle("diagnostic_existing_forward", diag_all, diag_target, diag_denominator)
    future = scenario_bundle("frozen_future", fut_all, fut_target, fut_denominator)
    return {
        "freeze": state,
        "diagnostic": diagnostic,
        "frozen_future": future,
        "current_read": current_read(diagnostic, future),
    }


def current_read(diagnostic: dict[str, Any], future: dict[str, Any]) -> list[str]:
    diag_candidate = diagnostic.get("candidate_summary") or {}
    diag_target = diagnostic.get("target_summary") or {}
    return [
        f"Diagnostic candidate: {diag_candidate.get('settled')} settled, {diag_candidate.get('wins')}/{diag_candidate.get('losses')}, net {diag_candidate.get('net_cents')}c, coverage {diag_candidate.get('coverage_pct')}%.",
        f"Diagnostic delta versus target: {diagnostic.get('delta_vs_target_cents')}c versus target net {diag_target.get('net_cents')}c.",
        f"Diagnostic source counts: {diagnostic.get('source_counts')}.",
        f"Diagnostic warnings: {diagnostic.get('warnings') or []}.",
        f"Frozen future settled rows: {(future.get('candidate_summary') or {}).get('settled')}; this is the only promotion evidence.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def summary_table(rows: list[dict[str, Any]], key: str) -> list[str]:
    lines = ["| " + key + " | entries | settled | W/L | coverage | net c | avg c |", "|---|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row.get(key)} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    return lines


def write_md(report: dict[str, Any]) -> None:
    freeze = report.get("freeze") or {}
    diagnostic = report.get("diagnostic") or {}
    future = report.get("frozen_future") or {}
    lines = [
        "# v28 Goldilocks Edge Repair Stress",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("current_read") or []:
        lines.append(f"- {note}")
    for bundle in [diagnostic, future]:
        lines.extend(["", f"## {bundle.get('label')}", ""])
        lines.extend(summary_table(bundle.get("scenario_rows") or [], "scenario"))
        lines.extend(["", "### Candidate Source Split", ""])
        lines.extend(summary_table(bundle.get("candidate_source_summary") or [], "source"))
        lines.extend(["", "### Danger Source Split", ""])
        lines.extend(summary_table(bundle.get("danger_source_summary") or [], "source"))
        lines.extend(["", "### Repair Source Split", ""])
        lines.extend(summary_table(bundle.get("repair_source_summary") or [], "source"))
        lines.extend(["", "### Full-Loss Runway", "", "| added full losses | stressed settled | stressed net c | still positive | sample gate met |", "|---:|---:|---:|---:|---:|"])
        for row in bundle.get("full_loss_runway") or []:
            lines.append(
                f"| {row.get('added_full_losses')} | {row.get('stressed_settled')} | {fmt(row.get('stressed_net_cents'))} | {row.get('still_positive')} | {row.get('sample_gate_met')} |"
            )
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
