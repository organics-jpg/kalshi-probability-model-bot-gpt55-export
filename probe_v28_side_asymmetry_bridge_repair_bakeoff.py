"""Repair scorer bakeoff for the side-asymmetry FV entry bridge.

Research-only; no live bot changes or orders.

The side-asymmetry FV bridge removes a large loss pocket but remains slightly
negative because repair rows are weak. This diagnostic compares simple ex-ante
repair orderings while keeping the skip rule fixed.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_composite_false_conviction_repair_bakeoff import (
    first_clean_by_market_scored,
    score_farthest_boundary,
    score_highest_raw_p,
    score_lowest_recross,
    score_prob_edge_stability,
)
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, build_surfaces, summarize
from probe_v28_side_asymmetry_fv_entry_bridge import adjusted_edge, row_view


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_side_asymmetry_bridge_repair_bakeoff_latest.json"
OUT_MD = OUT_DIR / "v28_side_asymmetry_bridge_repair_bakeoff_latest.md"

EDGE_FLOOR = 0.02
SCORERS: dict[str, Callable[[dict[str, Any]], float]] = {
    "highest_raw_p": score_highest_raw_p,
    "farthest_boundary": score_farthest_boundary,
    "lowest_recross": score_lowest_recross,
    "prob_edge_stability": score_prob_edge_stability,
}


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def evaluate_scorer(name: str, scorer: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    all_rows, target, denominator, forward_markets = build_surfaces()
    all_markets = {str(row.get("market") or "") for row in all_rows if row.get("market")}
    target_markets = {str(row.get("market") or "") for row in target}
    skipped = [
        row for row in target
        if adjusted_edge(row) is not None and float(adjusted_edge(row) or 0.0) < EDGE_FLOOR
    ]
    skipped_markets = {str(row.get("market") or "") for row in skipped}
    kept = [row for row in target if str(row.get("market") or "") not in skipped_markets]
    needed = max(0, ceil_entries_for_floor(denominator) - len(kept))
    chronological = name == "chronological"
    missed_repairs = first_clean_by_market_scored(
        all_rows,
        forward_markets - target_markets,
        scorer,
        chronological,
    )
    chosen = missed_repairs[:needed]
    chosen_markets = {str(row.get("market") or "") for row in chosen}
    if len(chosen) < needed:
        kept_markets = {str(row.get("market") or "") for row in kept}
        extras = first_clean_by_market_scored(
            all_rows,
            all_markets - kept_markets - chosen_markets,
            scorer,
            chronological,
        )
        for row in extras:
            if len(chosen) >= needed:
                break
            market = str(row.get("market") or "")
            if market in chosen_markets:
                continue
            chosen.append(row)
            chosen_markets.add(market)
    candidate = kept + chosen
    target_summary = summarize(target, denominator)
    candidate_summary = summarize(candidate, denominator)
    return {
        "scorer": name,
        "edge_floor": EDGE_FLOOR,
        "needed_repairs": needed,
        "chosen_repairs": len(chosen),
        "target_summary": target_summary,
        "skipped_summary": summarize(skipped, denominator),
        "kept_summary": summarize(kept, denominator),
        "repair_summary": summarize(chosen, denominator),
        "candidate_summary": candidate_summary,
        "delta_vs_target_cents": float(candidate_summary.get("net_cents") or 0.0)
        - float(target_summary.get("net_cents") or 0.0),
        "skipped_rows": [row_view(row) for row in skipped],
        "repair_rows": [row_view(row) for row in chosen],
    }


def build_report() -> dict[str, Any]:
    ranked = [evaluate_scorer(name, fn) for name, fn in SCORERS.items()]
    ranked.sort(key=lambda row: float((row.get("candidate_summary") or {}).get("net_cents") or -999999.0), reverse=True)
    return {
        "diagnostic": "side_asymmetry_bridge_repair_bakeoff",
        "coverage_floor": COVERAGE_FLOOR,
        "edge_floor": EDGE_FLOOR,
        "ranked": ranked,
        "interpretation": interpretation(ranked),
    }


def interpretation(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["No rows available."]
    best = rows[0]
    cand = best.get("candidate_summary") or {}
    skipped = best.get("skipped_summary") or {}
    repair = best.get("repair_summary") or {}
    return [
        f"Best repair scorer is {best.get('scorer')} with net {cand.get('net_cents')}c and coverage {cand.get('coverage_pct')}%.",
        f"Skipped rows net {skipped.get('net_cents')}c; repair rows net {repair.get('net_cents')}c.",
        "This is diagnostic only; frozen future validation is required before promotion.",
    ]


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
        "# v28 Side-Asymmetry Bridge Repair Bakeoff",
        "",
        "Diagnostic-only: no live bot changes and no orders.",
        "",
        f"- Edge floor: `{report.get('edge_floor')}`",
        f"- Coverage floor: `{report.get('coverage_floor')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Ranking",
        "",
        "| rank | scorer | repairs | coverage | net c | delta c | W/L | skipped net c | repair net c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        cand = row.get("candidate_summary") or {}
        skipped = row.get("skipped_summary") or {}
        repair = row.get("repair_summary") or {}
        lines.append(
            f"| {idx} | {row.get('scorer')} | {row.get('chosen_repairs')} | {fmt(cand.get('coverage_pct'))} | "
            f"{fmt(cand.get('net_cents'))} | {fmt(row.get('delta_vs_target_cents'))} | "
            f"{cand.get('wins')}/{cand.get('losses')} | {fmt(skipped.get('net_cents'))} | {fmt(repair.get('net_cents'))} |"
        )
    best = (report.get("ranked") or [{}])[0]
    lines.extend([
        "",
        "## Best Repair Rows",
        "",
        "| market | source | side | won | net c | raw p | adj p | ask | adj edge | recross | abs d |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in best.get("repair_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_p'))} | {fmt(row.get('adjusted_p'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('adjusted_edge'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
