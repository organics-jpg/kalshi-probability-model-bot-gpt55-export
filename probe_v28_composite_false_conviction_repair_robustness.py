"""Robustness audit for composite false-conviction repair.

Research-only; no live bot changes or orders.

The composite repair bakeoff found a positive diagnostic row by removing
false-conviction entries and repairing coverage with high raw-p clean rows.
This audit reruns the construction under leave-one-market-out exclusions to
check whether the result depends on one fragile market.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_composite_false_conviction_repair_bakeoff import (
    ceil_entries_for_floor,
    first_clean_by_market_scored,
    score_farthest_boundary,
    score_highest_raw_p,
    score_lowest_recross,
    score_prob_edge_stability,
)
from probe_v28_coverage_repair_pool_diagnostic import build_surfaces, summarize
from probe_v28_false_conviction_physics_audit import is_false_conviction_zone


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_composite_false_conviction_repair_robustness_latest.json"
OUT_MD = OUT_DIR / "v28_composite_false_conviction_repair_robustness_latest.md"

SCORERS: dict[str, Callable[[dict[str, Any]], float]] = {
    "highest_raw_p": score_highest_raw_p,
    "farthest_boundary": score_farthest_boundary,
    "lowest_recross": score_lowest_recross,
    "prob_edge_stability": score_prob_edge_stability,
}


def build_candidate(
    scorer_name: str,
    scorer: Callable[[dict[str, Any]], float],
    all_rows_base: list[dict[str, Any]],
    target_base: list[dict[str, Any]],
    denominator_base: int,
    forward_markets_base: set[str],
    exclude_market: str | None = None,
) -> dict[str, Any]:
    all_rows = all_rows_base
    target = target_base
    denominator = denominator_base
    forward_markets = forward_markets_base
    if exclude_market:
        all_rows = [row for row in all_rows if str(row.get("market") or "") != exclude_market]
        target = [row for row in target if str(row.get("market") or "") != exclude_market]
        forward_markets = {market for market in forward_markets if market != exclude_market}
        denominator = max(0, denominator - 1)

    all_markets = {str(row.get("market") or "") for row in all_rows if row.get("market")}
    target_markets = {str(row.get("market") or "") for row in target}
    danger = [row for row in target if is_false_conviction_zone(row)]
    danger_markets = {str(row.get("market") or "") for row in danger}
    kept = [row for row in target if str(row.get("market") or "") not in danger_markets]
    needed = max(0, ceil_entries_for_floor(denominator) - len(kept))
    chronological = scorer_name == "chronological"

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
        "scorer": scorer_name,
        "excluded_market": exclude_market,
        "forward_denominator": denominator,
        "needed_repairs": needed,
        "target_summary": target_summary,
        "danger_summary": summarize(danger, denominator),
        "repair_summary": summarize(chosen, denominator),
        "candidate_summary": candidate_summary,
        "delta_vs_target_cents": float(candidate_summary.get("net_cents") or 0.0)
        - float(target_summary.get("net_cents") or 0.0),
        "candidate_markets": sorted({str(row.get("market") or "") for row in candidate if row.get("market")}),
        "danger_markets": sorted(danger_markets),
        "repair_markets": sorted(chosen_markets),
    }


def robustness_for_scorer(
    name: str,
    scorer: Callable[[dict[str, Any]], float],
    all_rows: list[dict[str, Any]],
    target: list[dict[str, Any]],
    denominator: int,
    forward_markets: set[str],
) -> dict[str, Any]:
    full = build_candidate(name, scorer, all_rows, target, denominator, forward_markets)
    markets = sorted(set(full["candidate_markets"]) | set(full["danger_markets"]) | set(full["repair_markets"]))
    leaveouts = [build_candidate(name, scorer, all_rows, target, denominator, forward_markets, market) for market in markets]
    deltas = [float(row.get("delta_vs_target_cents") or 0.0) for row in leaveouts]
    nets = [float((row.get("candidate_summary") or {}).get("net_cents") or 0.0) for row in leaveouts]
    coverages = [
        float((row.get("candidate_summary") or {}).get("coverage_pct") or 0.0)
        for row in leaveouts
    ]
    negative_net = [row for row in leaveouts if float((row.get("candidate_summary") or {}).get("net_cents") or 0.0) <= 0.0]
    coverage_fail = [row for row in leaveouts if float((row.get("candidate_summary") or {}).get("coverage_pct") or 0.0) < 75.0]
    return {
        "scorer": name,
        "full": full,
        "leaveout_count": len(leaveouts),
        "worst_delta": min(deltas) if deltas else None,
        "worst_net": min(nets) if nets else None,
        "worst_coverage": min(coverages) if coverages else None,
        "negative_net_count": len(negative_net),
        "coverage_fail_count": len(coverage_fail),
        "robust_positive": not negative_net and not coverage_fail and bool(leaveouts),
        "worst_net_rows": sorted(
            leaveouts,
            key=lambda row: float((row.get("candidate_summary") or {}).get("net_cents") or 0.0),
        )[:5],
    }


def build_report() -> dict[str, Any]:
    all_rows, target, denominator, forward_markets = build_surfaces()
    rows = [
        robustness_for_scorer(name, fn, all_rows, target, denominator, forward_markets)
        for name, fn in SCORERS.items()
    ]
    rows.sort(key=lambda row: (
        not bool(row.get("robust_positive")),
        -float(((row.get("full") or {}).get("candidate_summary") or {}).get("net_cents") or 0.0),
    ))
    return {
        "audit": "composite_false_conviction_repair_robustness",
        "ranked": rows,
        "interpretation": interpretation(rows),
    }


def interpretation(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["No robustness rows were produced."]
    best = rows[0]
    full = best.get("full") or {}
    cand = full.get("candidate_summary") or {}
    return [
        f"Best robustness-ranked scorer is {best.get('scorer')} with full net {cand.get('net_cents')}c and coverage {cand.get('coverage_pct')}%.",
        f"Leave-one-market-out worst net is {best.get('worst_net')}c; negative-net exclusions {best.get('negative_net_count')}.",
        "This remains diagnostic; live use requires the frozen forward validator to mature.",
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
        "# v28 Composite False-Conviction Repair Robustness",
        "",
        "Research-only leave-one-market-out audit.",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Scorers",
        "",
        "| rank | scorer | full net c | full coverage | leaveouts | worst net c | worst delta c | worst coverage | neg net | cov fail | robust |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        full = row.get("full") or {}
        cand = full.get("candidate_summary") or {}
        lines.append(
            f"| {idx} | {row.get('scorer')} | {fmt(cand.get('net_cents'))} | {fmt(cand.get('coverage_pct'))} | "
            f"{row.get('leaveout_count')} | {fmt(row.get('worst_net'))} | {fmt(row.get('worst_delta'))} | "
            f"{fmt(row.get('worst_coverage'))} | {row.get('negative_net_count')} | "
            f"{row.get('coverage_fail_count')} | {row.get('robust_positive')} |"
        )
    best = (report.get("ranked") or [{}])[0]
    lines.extend([
        "",
        "## Best Scorer Worst Leaveouts",
        "",
        "| excluded market | candidate net c | delta c | coverage | W/L | repairs | danger |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in best.get("worst_net_rows") or []:
        cand = row.get("candidate_summary") or {}
        repair = row.get("repair_summary") or {}
        danger = row.get("danger_summary") or {}
        lines.append(
            f"| {row.get('excluded_market')} | {fmt(cand.get('net_cents'))} | "
            f"{fmt(row.get('delta_vs_target_cents'))} | {fmt(cand.get('coverage_pct'))} | "
            f"{cand.get('wins')}/{cand.get('losses')} | {repair.get('entries')} | {danger.get('entries')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
