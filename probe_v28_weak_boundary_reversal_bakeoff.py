"""Weak-boundary reversal strategy bakeoff.

Research-only; no live bot changes or orders.

This expands the simple weak-boundary reversal diagnostic into a small
predeclared robustness check. The goal is not to find the prettiest historical
row. It is to see whether the physical idea survives conservative variants:
weak near-boundary/high-recross signals are not side theses until the boundary
has revealed itself.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_boundary_reversal_opportunity import opposite_replacements, row_net_after_fee
from probe_v28_composite_false_conviction_repair_bakeoff import (
    first_clean_by_market_scored,
    score_farthest_boundary,
)
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, build_surfaces, summarize


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_weak_boundary_reversal_bakeoff_latest.json"
OUT_MD = OUT_DIR / "v28_weak_boundary_reversal_bakeoff_latest.md"

P_MAX_VALUES = [0.55, 0.58, 0.60]
RECROSS_FLOORS = [0.75, 0.85, 0.90]
ABS_D_MAX_VALUES = [0.20, 0.25, 0.30]
MAX_DELAYS = [120.0, 180.0, 240.0]
NO_REPLACEMENT_MODES = ["abstain", "keep"]


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def net_ready(row: dict[str, Any]) -> dict[str, Any]:
    net = row.get("net_gross_cents_after_entry_fee")
    if net is None:
        net = row_net_after_fee(row)
    return {**row, "net_gross_cents_after_entry_fee": net}


def is_weak_boundary(row: dict[str, Any], p_max: float, recross_floor: float, abs_d_max: float) -> bool:
    p = as_float(row.get("p_side"))
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    return (
        p is not None
        and recross is not None
        and abs_d is not None
        and p <= p_max
        and recross >= recross_floor
        and abs_d <= abs_d_max
    )


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def choose_opposite(all_rows: list[dict[str, Any]], row: dict[str, Any], max_delay: float) -> dict[str, Any] | None:
    for repl in opposite_replacements(all_rows, row):
        delay = as_float(repl.get("replacement_delay_seconds"))
        if delay is not None and delay <= max_delay:
            return net_ready(repl)
    return None


def clean_repair_candidates(
    all_rows: list[dict[str, Any]],
    markets: set[str],
    p_max: float,
    recross_floor: float,
    abs_d_max: float,
) -> list[dict[str, Any]]:
    rows = first_clean_by_market_scored(all_rows, markets, score_farthest_boundary, chronological=False)
    return [
        net_ready(row)
        for row in rows
        if not is_weak_boundary(row, p_max=p_max, recross_floor=recross_floor, abs_d_max=abs_d_max)
    ]


def leave_one_market_worst(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    markets = sorted({str(row.get("market") or "") for row in rows if row.get("market")})
    if not markets:
        return {"worst_net_cents": 0.0, "negative_exclusions": 0}
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
        "replacement_delay_seconds": row.get("replacement_delay_seconds"),
    }


def run_variant(
    all_rows: list[dict[str, Any]],
    target: list[dict[str, Any]],
    denominator: int,
    forward_markets: set[str],
    p_max: float,
    recross_floor: float,
    abs_d_max: float,
    max_delay: float,
    no_replacement_mode: str,
) -> dict[str, Any]:
    all_markets = {str(row.get("market") or "") for row in all_rows if row.get("market")}
    target_markets = {str(row.get("market") or "") for row in target}
    weak = [
        net_ready(row)
        for row in target
        if is_weak_boundary(row, p_max=p_max, recross_floor=recross_floor, abs_d_max=abs_d_max)
    ]
    weak_markets = {str(row.get("market") or "") for row in weak}
    kept = [
        net_ready(row)
        for row in target
        if str(row.get("market") or "") not in weak_markets
    ]
    replacements: list[dict[str, Any]] = []
    no_replacement_kept: list[dict[str, Any]] = []
    for row in weak:
        repl = choose_opposite(all_rows, row, max_delay)
        if repl is not None:
            replacements.append(repl)
        elif no_replacement_mode == "keep":
            no_replacement_kept.append(row)

    current = kept + replacements + no_replacement_kept
    needed = max(0, ceil_entries_for_floor(denominator) - len(current))
    used_markets = {str(row.get("market") or "") for row in current if row.get("market")}
    repairs = clean_repair_candidates(
        all_rows,
        forward_markets - target_markets,
        p_max=p_max,
        recross_floor=recross_floor,
        abs_d_max=abs_d_max,
    )[:needed]
    repair_markets = {str(row.get("market") or "") for row in repairs}
    if len(repairs) < needed:
        extras = clean_repair_candidates(
            all_rows,
            all_markets - used_markets - repair_markets,
            p_max=p_max,
            recross_floor=recross_floor,
            abs_d_max=abs_d_max,
        )
        for row in extras:
            if len(repairs) >= needed:
                break
            market = str(row.get("market") or "")
            if market in repair_markets or market in used_markets:
                continue
            repairs.append(row)
            repair_markets.add(market)

    candidate = current + repairs
    candidate_summary = summarize(candidate, denominator)
    target_summary = summarize([net_ready(row) for row in target], denominator)
    net = float(candidate_summary.get("net_cents") or 0.0)
    return {
        "policy": (
            f"p{int(p_max*100)}_recross{int(recross_floor*100)}_near{int(abs_d_max*100)}_"
            f"delay{int(max_delay)}_{no_replacement_mode}"
        ),
        "p_max": p_max,
        "recross_floor": recross_floor,
        "abs_d_max": abs_d_max,
        "max_delay": max_delay,
        "no_replacement_mode": no_replacement_mode,
        "target_summary": target_summary,
        "weak_summary": summarize(weak, denominator),
        "replacement_summary": summarize(replacements, denominator),
        "no_replacement_kept_summary": summarize(no_replacement_kept, denominator),
        "repair_summary": summarize(repairs, denominator),
        "candidate_summary": candidate_summary,
        "delta_vs_target_cents": net - float(target_summary.get("net_cents") or 0.0),
        "coverage_repaired": len(repairs) >= needed,
        "needed_repairs": needed,
        "chosen_repairs": len(repairs),
        "loo": leave_one_market_worst(candidate, denominator),
        "candidate_rows": [row_view(row) for row in candidate],
        "loss_rows": [
            row_view(row)
            for row in candidate
            if row.get("side_won") is False
        ],
    }


def build_report() -> dict[str, Any]:
    all_rows, target, denominator, forward_markets = build_surfaces()
    variants = []
    for p_max in P_MAX_VALUES:
        for recross_floor in RECROSS_FLOORS:
            for abs_d_max in ABS_D_MAX_VALUES:
                for max_delay in MAX_DELAYS:
                    for mode in NO_REPLACEMENT_MODES:
                        variants.append(
                            run_variant(
                                all_rows=all_rows,
                                target=target,
                                denominator=denominator,
                                forward_markets=forward_markets,
                                p_max=p_max,
                                recross_floor=recross_floor,
                                abs_d_max=abs_d_max,
                                max_delay=max_delay,
                                no_replacement_mode=mode,
                            )
                        )
    variants.sort(
        key=lambda row: (
            float((row.get("candidate_summary") or {}).get("net_cents") or -999999.0),
            float((row.get("loo") or {}).get("worst_net_cents") or -999999.0),
        ),
        reverse=True,
    )
    best = variants[0] if variants else None
    return {
        "diagnostic": "weak_boundary_reversal_bakeoff",
        "forward_denominator": denominator,
        "coverage_floor": COVERAGE_FLOOR,
        "variant_count": len(variants),
        "best": best,
        "top": variants[:20],
        "interpretation": interpretation(best),
    }


def interpretation(best: dict[str, Any] | None) -> list[str]:
    if not best:
        return ["No variants produced a result."]
    summary = best.get("candidate_summary") or {}
    loo = best.get("loo") or {}
    notes = [
        f"Best variant {best.get('policy')} nets {summary.get('net_cents')}c at {summary.get('coverage_pct')}% coverage.",
        f"Leave-one-market worst net is {loo.get('worst_net_cents')}c with {loo.get('negative_exclusions')} negative exclusions.",
    ]
    if float(summary.get("net_cents") or 0.0) <= 0:
        notes.append("Even the best variant is not live-promotable because net P&L is not positive.")
    if float(loo.get("worst_net_cents") or 0.0) < 0:
        notes.append("Robustness is weak: one-market exclusions still leave negative net.")
    notes.append("This remains diagnostic until frozen forward validation earns enough future rows.")
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
        "# v28 Weak-Boundary Reversal Bakeoff",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Variants: `{report.get('variant_count')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Top Variants",
            "",
            "| policy | entries | settled | W/L | coverage | net c | delta c | weak net | repl net | no-repl keep net | repair net | LOO worst | neg excl |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("top") or []:
        cand = row.get("candidate_summary") or {}
        weak = row.get("weak_summary") or {}
        repl = row.get("replacement_summary") or {}
        no_repl = row.get("no_replacement_kept_summary") or {}
        repair = row.get("repair_summary") or {}
        loo = row.get("loo") or {}
        lines.append(
            f"| {row.get('policy')} | {cand.get('entries')} | {cand.get('settled')} | "
            f"{cand.get('wins')}/{cand.get('losses')} | {fmt(cand.get('coverage_pct'))} | "
            f"{fmt(cand.get('net_cents'))} | {fmt(row.get('delta_vs_target_cents'))} | "
            f"{fmt(weak.get('net_cents'))} | {fmt(repl.get('net_cents'))} | "
            f"{fmt(no_repl.get('net_cents'))} | {fmt(repair.get('net_cents'))} | "
            f"{fmt(loo.get('worst_net_cents'))} | {loo.get('negative_exclusions')} |"
    )
    best = report.get("best") or {}
    losses = best.get("loss_rows") or []
    if losses:
        lines.extend(
            [
                "",
                "## Best Variant Loss Rows",
                "",
                "| market | source | side | net c | p | ask | edge | stc | recross | abs d | delay |",
                "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in losses:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | "
                f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('seconds_to_close'))} | "
                f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | "
                f"{fmt(row.get('replacement_delay_seconds'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
