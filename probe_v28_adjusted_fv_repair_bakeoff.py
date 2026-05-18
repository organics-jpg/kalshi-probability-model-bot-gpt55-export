"""Adjusted-FV coverage repair bakeoff for v28 target surface.

Research-only; no live bot changes or orders.

The target-coverage surface is currently below the 75% floor after the latest
forward market denominator update. Existing repair diagnostics rank candidate
repairs by raw p/edge/geometry. This probe asks whether the newer combined
boundary-clock + side-asymmetry FV overlay provides a better ex-ante repair
score while preserving the coverage floor.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_coverage_repair_pool_diagnostic import (
    COVERAGE_FLOOR,
    as_float,
    build_surfaces,
    is_clean_repair,
    raw_edge,
    row_net_after_fee,
    summarize,
)
from probe_v28_danger_tag_replacement_diagnostic import danger_tags
from probe_v28_side_asymmetry_fv_overlay import combined_prob
from probe_v28_boundary_clock_fv_overlay import raw_prob


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_adjusted_fv_repair_bakeoff_latest.json"
OUT_MD = OUT_DIR / "v28_adjusted_fv_repair_bakeoff_latest.md"


def is_paid_or_weak_boundary(row: dict[str, Any]) -> bool:
    return bool({"paid_price_fragile", "weak_boundary_turbulence"} & set(danger_tags(row)))


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def ask_prob(row: dict[str, Any]) -> float | None:
    return as_float(row.get("ask_prob"))


def adjusted_p(row: dict[str, Any]) -> float:
    try:
        return combined_prob(row, 0.0)
    except (TypeError, ValueError):
        return -999.0


def adjusted_edge(row: dict[str, Any]) -> float:
    ask = ask_prob(row)
    p = adjusted_p(row)
    if ask is None or p <= -900.0:
        return -999.0
    return p - ask


def adjustment_delta(row: dict[str, Any]) -> float:
    try:
        return adjusted_p(row) - raw_prob(row)
    except (TypeError, ValueError):
        return 0.0


def score_adjusted_p(row: dict[str, Any]) -> float:
    return adjusted_p(row)


def score_adjusted_edge(row: dict[str, Any]) -> float:
    return adjusted_edge(row)


def score_adjusted_p_plus_edge(row: dict[str, Any]) -> float:
    return adjusted_p(row) + 2.0 * adjusted_edge(row)


def score_raw_p(row: dict[str, Any]) -> float:
    return as_float(row.get("p_side")) or -999.0


def score_raw_edge(row: dict[str, Any]) -> float:
    return raw_edge(row) or -999.0


def score_low_adjustment_penalty(row: dict[str, Any]) -> float:
    return adjusted_p(row) + 2.0 * adjusted_edge(row) + adjustment_delta(row)


SCORERS: dict[str, Callable[[dict[str, Any]], float]] = {
    "highest_raw_p": score_raw_p,
    "highest_raw_edge": score_raw_edge,
    "highest_adjusted_p": score_adjusted_p,
    "highest_adjusted_edge": score_adjusted_edge,
    "adjusted_p_plus_2edge": score_adjusted_p_plus_edge,
    "adjusted_p_edge_with_penalty": score_low_adjustment_penalty,
}


def first_clean_by_market_scored(
    rows: list[dict[str, Any]],
    markets: set[str],
    scorer: Callable[[dict[str, Any]], float],
) -> list[dict[str, Any]]:
    candidates = []
    for row in rows:
        market = str(row.get("market") or "")
        if market not in markets or not is_clean_repair(row):
            continue
        try:
            raw_p = raw_prob(row)
            adj_p = adjusted_p(row)
        except (TypeError, ValueError):
            continue
        candidates.append({
            **row,
            "raw_edge_prob": raw_edge(row),
            "adjusted_p": adj_p,
            "adjusted_edge": adjusted_edge(row),
            "adjustment_delta": adj_p - raw_p,
            "net_gross_cents_after_entry_fee": row_net_after_fee(row),
            "repair_score": scorer(row),
        })
    candidates.sort(key=lambda row: (-float(row.get("repair_score") or -999.0), str(row.get("ts_wall") or "")))
    out = []
    seen = set()
    for row in candidates:
        market = str(row.get("market") or "")
        if market in seen:
            continue
        out.append(row)
        seen.add(market)
    return out


def evaluate_scorer(name: str, scorer: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    all_rows, target, denominator, _forward_markets = build_surfaces()
    all_markets = {str(row.get("market") or "") for row in all_rows if row.get("market")}
    target_markets = {str(row.get("market") or "") for row in target}
    removed = [row for row in target if is_paid_or_weak_boundary(row)]
    removed_markets = {str(row.get("market") or "") for row in removed}
    kept = [row for row in target if str(row.get("market") or "") not in removed_markets]
    needed = max(0, ceil_entries_for_floor(denominator) - len(kept))

    missed = first_clean_by_market_scored(all_rows, all_markets - target_markets, scorer)
    chosen = missed[:needed]
    chosen_markets = {str(row.get("market") or "") for row in chosen}
    if len(chosen) < needed:
        extras = first_clean_by_market_scored(
            all_rows,
            all_markets - {str(row.get("market") or "") for row in kept} - chosen_markets,
            scorer,
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
        "needed_repairs": needed,
        "chosen_repairs": len(chosen),
        "target_summary": target_summary,
        "candidate_summary": candidate_summary,
        "delta_vs_target_cents": float(candidate_summary.get("net_cents") or 0.0) - float(target_summary.get("net_cents") or 0.0),
        "repair_summary": summarize(chosen, denominator),
        "chosen_rows": [compact(row) for row in chosen],
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row),
        "raw_p": row.get("p_side"),
        "adjusted_p": row.get("adjusted_p"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": raw_edge(row),
        "adjusted_edge": row.get("adjusted_edge"),
        "adjustment_delta": row.get("adjustment_delta"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "repair_score": row.get("repair_score"),
    }


def build_report() -> dict[str, Any]:
    rows = [evaluate_scorer(name, fn) for name, fn in SCORERS.items()]
    rows.sort(key=lambda row: float(row.get("delta_vs_target_cents") or 0.0), reverse=True)
    return {
        "diagnostic": "adjusted_fv_repair_bakeoff",
        "entry_policy": "raw_p50_turbulence_valve_edge4_p60_recross75_near25",
        "fv_overlay": "clock_then_side_no_midboundary_0p00",
        "danger_rule": "paid_price_fragile OR weak_boundary_turbulence",
        "coverage_floor": COVERAGE_FLOOR,
        "ranked": rows,
        "interpretation": interpretation(rows),
    }


def interpretation(rows: list[dict[str, Any]]) -> list[str]:
    best = rows[0] if rows else {}
    cand = best.get("candidate_summary") or {}
    return [
        f"Best adjusted-FV repair scorer is {best.get('scorer')} with net {cand.get('net_cents')}c and coverage {cand.get('coverage_pct')}%.",
        f"Delta versus current target is {best.get('delta_vs_target_cents')}c.",
        "This is diagnostic only; freeze a future validator only if the rule has a clear physics explanation and non-overfit ranking.",
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
        "# v28 Adjusted-FV Repair Bakeoff",
        "",
        "Diagnostic-only: no live bot changes and no orders.",
        "",
        f"- Entry policy: `{report.get('entry_policy')}`",
        f"- FV overlay: `{report.get('fv_overlay')}`",
        f"- Danger rule: `{report.get('danger_rule')}`",
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
        "| rank | scorer | repairs | coverage | net c | delta c | W/L | repair net c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        cand = row.get("candidate_summary") or {}
        repairs = row.get("repair_summary") or {}
        lines.append(
            f"| {idx} | {row.get('scorer')} | {row.get('chosen_repairs')} | {fmt(cand.get('coverage_pct'))} | "
            f"{fmt(cand.get('net_cents'))} | {fmt(row.get('delta_vs_target_cents'))} | "
            f"{cand.get('wins')}/{cand.get('losses')} | {fmt(repairs.get('net_cents'))} |"
        )
    best = (report.get("ranked") or [{}])[0]
    lines.extend([
        "",
        "## Best Scorer Chosen Rows",
        "",
        "| market | source | side | won | net c | raw p | adj p | ask | raw edge | adj edge | adj d | recross | abs d | score |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in best.get("chosen_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_p'))} | {fmt(row.get('adjusted_p'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | {fmt(row.get('adjusted_edge'))} | "
            f"{fmt(row.get('adjustment_delta'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('repair_score'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
