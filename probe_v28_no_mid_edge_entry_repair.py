"""NO-side mid-edge entry repair diagnostic.

Research-only; no live bot changes or orders.

The broader target-coverage surface shows NO-side 5-8pp raw-edge rows are
overconfident and deeply negative in discovery. This tests the entry-policy
translation: skip those rows and repair only enough coverage with clean missed
market rows.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, build_surfaces, summarize
from probe_v28_weak_reversal_residual_repair import (
    ceil_entries_for_floor,
    edge_between,
    net_ready,
    repair_pool,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_no_mid_edge_entry_repair_latest.json"
OUT_MD = OUT_DIR / "v28_no_mid_edge_entry_repair_latest.md"


def no_mid_edge(row: dict[str, Any]) -> bool:
    return str(row.get("side")) == "no" and edge_between(row, 0.05, 0.08)


def leave_one_market_worst(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    markets = sorted({str(row.get("market") or "") for row in rows if row.get("market")})
    if not markets:
        return {"worst_net_cents": 0.0, "best_net_cents": 0.0, "negative_exclusions": 0}
    nets = []
    for market in markets:
        subset = [row for row in rows if str(row.get("market") or "") != market]
        nets.append(float(summarize(subset, denominator).get("net_cents") or 0.0))
    return {
        "worst_net_cents": min(nets),
        "best_net_cents": max(nets),
        "negative_exclusions": sum(1 for net in nets if net < 0),
    }


def row_view(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "seconds_to_close": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
    }


def build_report() -> dict[str, Any]:
    all_rows, target, denominator, forward_markets = build_surfaces()
    target = [net_ready(row) for row in target]
    skipped = [row for row in target if no_mid_edge(row)]
    skipped_markets = {str(row.get("market") or "") for row in skipped}
    kept = [row for row in target if str(row.get("market") or "") not in skipped_markets]
    needed = max(0, ceil_entries_for_floor(denominator) - len(kept))
    target_markets = {str(row.get("market") or "") for row in target}
    unavailable = {str(row.get("market") or "") for row in kept + skipped} | target_markets
    repairs = repair_pool(all_rows, unavailable, forward_markets, needed)
    candidate = kept + repairs
    target_summary = summarize(target, denominator)
    candidate_summary = summarize(candidate, denominator)
    return {
        "diagnostic": "no_mid_edge_entry_repair",
        "policy": "skip_no_edge_5_8pp_repair_farthest_boundary",
        "forward_denominator": denominator,
        "coverage_floor": COVERAGE_FLOOR,
        "target_summary": target_summary,
        "skipped_summary": summarize(skipped, denominator),
        "kept_summary": summarize(kept, denominator),
        "repair_summary": summarize(repairs, denominator),
        "candidate_summary": candidate_summary,
        "delta_vs_target_cents": float(candidate_summary.get("net_cents") or 0.0)
        - float(target_summary.get("net_cents") or 0.0),
        "needed_repairs": needed,
        "chosen_repairs": len(repairs),
        "coverage_repaired": len(repairs) >= needed,
        "loo": leave_one_market_worst(candidate, denominator),
        "skipped_rows": [row_view(row) for row in skipped],
        "repair_rows": [row_view(row) for row in repairs],
        "interpretation": interpretation(target_summary, candidate_summary, skipped, repairs, denominator),
    }


def interpretation(
    target_summary: dict[str, Any],
    candidate_summary: dict[str, Any],
    skipped: list[dict[str, Any]],
    repairs: list[dict[str, Any]],
    denominator: int,
) -> list[str]:
    notes = [
        f"Skipped NO mid-edge rows: {len(skipped)}; repair rows added: {len(repairs)}.",
        f"Target net {target_summary.get('net_cents')}c; candidate net {candidate_summary.get('net_cents')}c at {candidate_summary.get('coverage_pct')}% coverage.",
    ]
    coverage = candidate_summary.get("coverage_pct")
    if coverage is None or float(coverage) < COVERAGE_FLOOR:
        notes.append(f"Coverage is below the {COVERAGE_FLOOR}% floor for denominator {denominator}.")
    if float(candidate_summary.get("net_cents") or 0.0) <= 0:
        notes.append("Candidate is not live-promotable until net PnL is positive in frozen forward validation.")
    notes.append("Discovery-only; freeze separately if this remains useful.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 NO Mid-Edge Entry Repair",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Delta vs target: `{fmt(report.get('delta_vs_target_cents'))}c`",
        f"- Coverage repaired: `{report.get('coverage_repaired')}`",
        f"- LOO worst / negative exclusions: `{fmt((report.get('loo') or {}).get('worst_net_cents'))}/{(report.get('loo') or {}).get('negative_exclusions')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Summaries",
            "",
            "| slice | entries | settled | W/L | coverage | net c | avg c |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for name, key in [
        ("target", "target_summary"),
        ("skipped", "skipped_summary"),
        ("kept", "kept_summary"),
        ("repairs", "repair_summary"),
        ("candidate", "candidate_summary"),
    ]:
        row = report.get(key) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend(
        [
            "",
            "## Skipped Rows",
            "",
            "| market | side | won | net c | p | ask | edge | recross | abs d |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("skipped_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('side_won')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
