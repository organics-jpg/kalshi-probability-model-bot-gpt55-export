"""Residual repair candidates for weak-boundary reversal.

Research-only; no live bot changes or orders.

After weak-boundary reversal, the largest remaining loss cluster is not a
directional wipeout. It is a price-geometry cluster: mid raw edge rows can win
half the time and still lose money when the paid ask is too expensive. This
script tests a small set of predeclared residual skips plus clean repair rows
to preserve the target coverage floor.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_composite_false_conviction_repair_bakeoff import (
    first_clean_by_market_scored,
    score_farthest_boundary,
)
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, build_surfaces, summarize
from probe_v28_weak_boundary_reversal_bakeoff import (
    clean_repair_candidates,
    run_variant,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_weak_reversal_residual_repair_latest.json"
OUT_MD = OUT_DIR / "v28_weak_reversal_residual_repair_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def edge_between(row: dict[str, Any], low: float, high: float) -> bool:
    edge = as_float(row.get("raw_edge_prob"))
    return edge is not None and low <= edge < high


def recross_between(row: dict[str, Any], low: float, high: float) -> bool:
    recross = as_float(row.get("recross_hazard_score"))
    return recross is not None and low <= recross < high


def stc_gte(row: dict[str, Any], floor: float) -> bool:
    stc = as_float(row.get("seconds_to_close"))
    return stc is not None and stc >= floor


def ask_between(row: dict[str, Any], low: float, high: float) -> bool:
    ask = as_float(row.get("ask_prob"))
    return ask is not None and low <= ask < high


SKIPS: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
    ("edge_5_8pp", lambda row: edge_between(row, 0.05, 0.08)),
    ("edge_5_8pp_no", lambda row: str(row.get("side")) == "no" and edge_between(row, 0.05, 0.08)),
    ("edge_5_8pp_rejected", lambda row: str(row.get("source")) == "rejected_actionable" and edge_between(row, 0.05, 0.08)),
    ("recross_65_80", lambda row: recross_between(row, 0.65, 0.80)),
    ("stc_gte850", lambda row: stc_gte(row, 850.0)),
    ("ask_55_65", lambda row: ask_between(row, 0.55, 0.65)),
]


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def compact_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("market") or ""),
        str(row.get("side") or ""),
        str(row.get("source") or ""),
        str(row.get("seconds_to_close") or ""),
    )


def net_ready(row: dict[str, Any]) -> dict[str, Any]:
    net = row.get("net_gross_cents_after_entry_fee")
    if net is None:
        net = row.get("net_cents")
    return {**row, "net_gross_cents_after_entry_fee": net}


def repair_pool(
    all_rows: list[dict[str, Any]],
    unavailable_markets: set[str],
    forward_markets: set[str],
    needed: int,
) -> list[dict[str, Any]]:
    rows = first_clean_by_market_scored(
        all_rows,
        forward_markets - unavailable_markets,
        score_farthest_boundary,
        chronological=False,
    )
    if len(rows) >= needed:
        return [net_ready(row) for row in rows[:needed]]
    extras = first_clean_by_market_scored(
        all_rows,
        {str(row.get("market") or "") for row in all_rows if row.get("market")} - unavailable_markets,
        score_farthest_boundary,
        chronological=False,
    )
    picked = [net_ready(row) for row in rows]
    used = {str(row.get("market") or "") for row in picked}
    for row in extras:
        if len(picked) >= needed:
            break
        market = str(row.get("market") or "")
        if market in used:
            continue
        picked.append(net_ready(row))
        used.add(market)
    return picked


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


def build_report() -> dict[str, Any]:
    all_rows, target, denominator, forward_markets = build_surfaces()
    base = run_variant(
        all_rows=all_rows,
        target=target,
        denominator=denominator,
        forward_markets=forward_markets,
        p_max=0.60,
        recross_floor=0.75,
        abs_d_max=0.25,
        max_delay=240.0,
        no_replacement_mode="abstain",
    )
    base_rows = [net_ready(row) for row in base.get("candidate_rows") or []]
    target_markets = {str(row.get("market") or "") for row in target}
    variants = []
    for name, predicate in SKIPS:
        skipped = [row for row in base_rows if predicate(row)]
        skipped_keys = {compact_key(row) for row in skipped}
        kept = [row for row in base_rows if compact_key(row) not in skipped_keys]
        needed = max(0, ceil_entries_for_floor(denominator) - len(kept))
        unavailable = {str(row.get("market") or "") for row in kept}
        unavailable.update(str(row.get("market") or "") for row in skipped)
        repairs = repair_pool(all_rows, unavailable | target_markets, forward_markets, needed)
        candidate = kept + repairs
        summary = summarize(candidate, denominator)
        variants.append(
            {
                "policy": f"weak_reversal_skip_{name}_repair_farthest_boundary",
                "base_summary": base.get("candidate_summary"),
                "skipped_summary": summarize(skipped, denominator),
                "kept_summary": summarize(kept, denominator),
                "repair_summary": summarize(repairs, denominator),
                "candidate_summary": summary,
                "delta_vs_weak_reversal_cents": float(summary.get("net_cents") or 0.0)
                - float((base.get("candidate_summary") or {}).get("net_cents") or 0.0),
                "coverage_repaired": len(repairs) >= needed,
                "needed_repairs": needed,
                "chosen_repairs": len(repairs),
                "loo": leave_one_market_worst(candidate, denominator),
            }
        )
    variants.sort(
        key=lambda row: float((row.get("candidate_summary") or {}).get("net_cents") or -999999.0),
        reverse=True,
    )
    best = variants[0] if variants else {}
    return {
        "diagnostic": "weak_reversal_residual_repair",
        "forward_denominator": denominator,
        "base_policy": base.get("policy"),
        "base_summary": base.get("candidate_summary"),
        "best": best,
        "ranked": variants,
        "interpretation": interpretation(base, best),
    }


def interpretation(base: dict[str, Any], best: dict[str, Any]) -> list[str]:
    base_summary = base.get("candidate_summary") or {}
    best_summary = best.get("candidate_summary") or {}
    notes = [
        f"Weak-reversal base net is {base_summary.get('net_cents')}c at {base_summary.get('coverage_pct')}% coverage.",
        f"Best residual repair is {best.get('policy')} with net {best_summary.get('net_cents')}c at {best_summary.get('coverage_pct')}% coverage.",
    ]
    if float(best_summary.get("net_cents") or 0.0) <= 0:
        notes.append("The repair improves damage if positive delta, but is still not live-promotable unless net becomes positive and forward-robust.")
    loo = best.get("loo") or {}
    if loo:
        notes.append(
            f"Best leave-one-market worst net is {loo.get('worst_net_cents')}c with {loo.get('negative_exclusions')} negative exclusions."
        )
    notes.append("This is discovery-only; any skip tag must be frozen before promotion.")
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
        "# v28 Weak-Reversal Residual Repair",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Ranked Variants",
            "",
            "| policy | entries | settled | W/L | coverage | net c | delta c | skipped net | repair net | LOO worst | neg excl | repaired |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("ranked") or []:
        cand = row.get("candidate_summary") or {}
        skipped = row.get("skipped_summary") or {}
        repair = row.get("repair_summary") or {}
        loo = row.get("loo") or {}
        lines.append(
            f"| {row.get('policy')} | {cand.get('entries')} | {cand.get('settled')} | "
            f"{cand.get('wins')}/{cand.get('losses')} | {fmt(cand.get('coverage_pct'))} | "
            f"{fmt(cand.get('net_cents'))} | {fmt(row.get('delta_vs_weak_reversal_cents'))} | "
            f"{fmt(skipped.get('net_cents'))} | {fmt(repair.get('net_cents'))} | "
            f"{fmt(loo.get('worst_net_cents'))} | {loo.get('negative_exclusions')} | {row.get('coverage_repaired')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
