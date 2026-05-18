"""Ex-ante scoring bakeoff for coverage-repair rows.

Research-only; no live bot changes or orders.

The danger-repair diagnostic showed opportunity, but one view used realized
outcome ordering for fallback repairs. This probe replaces that with observable
ranking functions only: raw probability, raw edge, price, and simple geometry.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_coverage_repair_pool_diagnostic import (
    COVERAGE_FLOOR,
    as_float,
    build_surfaces,
    first_clean_by_market,
    is_clean_repair,
    raw_edge,
    row_net_after_fee,
    summarize,
)
from probe_v28_danger_tag_replacement_diagnostic import danger_tags


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_repair_scoring_bakeoff_latest.json"
OUT_MD = OUT_DIR / "v28_repair_scoring_bakeoff_latest.md"


def is_paid_or_weak_boundary(row: dict[str, Any]) -> bool:
    return bool({"paid_price_fragile", "weak_boundary_turbulence"} & set(danger_tags(row)))


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def score_p(row: dict[str, Any]) -> float:
    return as_float(row.get("p_side")) or -999.0


def score_edge(row: dict[str, Any]) -> float:
    return raw_edge(row) or -999.0


def score_cheap(row: dict[str, Any]) -> float:
    ask = as_float(row.get("ask_prob"))
    return -(ask if ask is not None else 999.0)


def score_edge_price(row: dict[str, Any]) -> float:
    edge = raw_edge(row) or -999.0
    ask = as_float(row.get("ask_prob"))
    return edge - 0.10 * (ask if ask is not None else 1.0)


def score_prob_edge(row: dict[str, Any]) -> float:
    return (as_float(row.get("p_side")) or 0.0) + 2.0 * (raw_edge(row) or 0.0)


def score_low_recross(row: dict[str, Any]) -> float:
    recross = as_float(row.get("recross_hazard_score"))
    return -(recross if recross is not None else 999.0)


def score_far_boundary(row: dict[str, Any]) -> float:
    return as_float(row.get("abs_d_sigma")) or -999.0


SCORERS: dict[str, Callable[[dict[str, Any]], float]] = {
    "chronological": lambda row: 0.0,
    "highest_raw_p": score_p,
    "highest_raw_edge": score_edge,
    "cheapest_ask": score_cheap,
    "edge_minus_price_friction": score_edge_price,
    "raw_p_plus_2edge": score_prob_edge,
    "lowest_recross": score_low_recross,
    "farthest_boundary": score_far_boundary,
}


def first_clean_by_market_scored(
    rows: list[dict[str, Any]],
    markets: set[str],
    scorer: Callable[[dict[str, Any]], float],
    chronological: bool = False,
) -> list[dict[str, Any]]:
    candidates = []
    for row in rows:
        market = str(row.get("market") or "")
        if market not in markets or not is_clean_repair(row):
            continue
        candidates.append({
            **row,
            "raw_edge_prob": raw_edge(row),
            "net_gross_cents_after_entry_fee": row_net_after_fee(row),
            "repair_score": scorer(row),
        })
    if chronological:
        candidates.sort(key=lambda row: str(row.get("ts_wall") or ""))
    else:
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

    chronological = name == "chronological"
    missed = first_clean_by_market_scored(all_rows, all_markets - target_markets, scorer, chronological)
    chosen = missed[:needed]
    chosen_markets = {str(row.get("market") or "") for row in chosen}
    if len(chosen) < needed:
        extras = first_clean_by_market_scored(
            all_rows,
            all_markets - {str(row.get("market") or "") for row in kept} - chosen_markets,
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
        "needed_repairs": needed,
        "missed_repairs_available": len(missed),
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
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": raw_edge(row),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "repair_score": row.get("repair_score"),
    }


def build_report() -> dict[str, Any]:
    rows = [evaluate_scorer(name, fn) for name, fn in SCORERS.items()]
    rows.sort(key=lambda row: float(row.get("delta_vs_target_cents") or 0.0), reverse=True)
    return {
        "diagnostic": "repair_scoring_bakeoff",
        "danger_rule": "paid_price_fragile OR weak_boundary_turbulence",
        "coverage_floor": COVERAGE_FLOOR,
        "ranked": rows,
        "interpretation": interpretation(rows),
    }


def interpretation(rows: list[dict[str, Any]]) -> list[str]:
    best = rows[0] if rows else {}
    cand = best.get("candidate_summary") or {}
    return [
        f"Best ex-ante scorer is {best.get('scorer')} with net {cand.get('net_cents')}c and delta {best.get('delta_vs_target_cents')}c.",
        f"Best coverage is {cand.get('coverage_pct')}%.",
        "This is still diagnostic until frozen forward validation exists.",
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
        "# v28 Repair Scoring Bakeoff",
        "",
        "Diagnostic-only: ranks repair rows by observable ex-ante scores.",
        "",
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
        "| market | source | side | won | net c | p | ask | edge | recross | abs d | score |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in best.get("chosen_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('repair_score'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
