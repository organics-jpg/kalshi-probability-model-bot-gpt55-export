"""Boundary-clock hazard repair diagnostic for v28 target coverage.

Research-only; no live bot changes or orders.

Physics idea:
    Close to the BTC boundary, time is not neutral. Early high-recross rows can
    look cheap because the path still has many chances to cross back. This probe
    tests whether removing those unresolved clock-boundary rows and repairing
    coverage with calmer opportunities improves the broad 75%+ target surface.
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


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_clock_hazard_repair_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_hazard_repair_latest.md"


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def recross(row: dict[str, Any]) -> float | None:
    return as_float(row.get("recross_hazard_score"))


def abs_d(row: dict[str, Any]) -> float | None:
    return as_float(row.get("abs_d_sigma"))


def stc(row: dict[str, Any]) -> float | None:
    return as_float(row.get("seconds_to_close"))


def ask(row: dict[str, Any]) -> float | None:
    return as_float(row.get("ask_prob"))


def p_side(row: dict[str, Any]) -> float | None:
    return as_float(row.get("p_side"))


def early_boundary_recross(row: dict[str, Any]) -> bool:
    return (
        (stc(row) or -1.0) >= 720.0
        and (abs_d(row) or 999.0) <= 0.40
        and (recross(row) or -1.0) >= 0.65
    )


def early_boundary_cheap_recross(row: dict[str, Any]) -> bool:
    return (
        (stc(row) or -1.0) >= 720.0
        and (abs_d(row) or 999.0) <= 0.35
        and (recross(row) or -1.0) >= 0.75
        and (ask(row) or 999.0) <= 0.60
    )


def early_midprob_boundary(row: dict[str, Any]) -> bool:
    return (
        (stc(row) or -1.0) >= 720.0
        and (abs_d(row) or 999.0) <= 0.45
        and (recross(row) or -1.0) >= 0.55
        and (p_side(row) or 999.0) < 0.70
    )


def expensive_low_edge_clock(row: dict[str, Any]) -> bool:
    edge = raw_edge(row)
    return (
        (stc(row) or -1.0) >= 600.0
        and (ask(row) or -1.0) >= 0.65
        and (edge is not None and edge < 0.02)
    )


def clock_composite(row: dict[str, Any]) -> bool:
    return early_boundary_cheap_recross(row) or expensive_low_edge_clock(row)


RULES: dict[str, Callable[[dict[str, Any]], bool]] = {
    "early_boundary_recross": early_boundary_recross,
    "early_boundary_cheap_recross": early_boundary_cheap_recross,
    "early_midprob_boundary": early_midprob_boundary,
    "expensive_low_edge_clock": expensive_low_edge_clock,
    "clock_composite": clock_composite,
}


def repair_score(row: dict[str, Any]) -> tuple[float, str]:
    """Lower tuple is preferred: calm recross first, then chronological."""
    value = recross(row)
    return (value if value is not None else 999.0, str(row.get("ts_wall") or ""))


def clean_repair_rows(rows: list[dict[str, Any]], markets: set[str]) -> list[dict[str, Any]]:
    candidates = []
    for row in rows:
        market = str(row.get("market") or "")
        if market not in markets or not is_clean_repair(row):
            continue
        candidates.append({
            **row,
            "raw_edge_prob": raw_edge(row),
            "net_gross_cents_after_entry_fee": row_net_after_fee(row),
            "repair_score": -(recross(row) if recross(row) is not None else 999.0),
        })
    candidates.sort(key=repair_score)
    out = []
    seen = set()
    for row in candidates:
        market = str(row.get("market") or "")
        if market in seen:
            continue
        out.append(row)
        seen.add(market)
    return out


def evaluate_rule(name: str, rule: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    all_rows, target, denominator, _forward_markets = build_surfaces()
    all_markets = {str(row.get("market") or "") for row in all_rows if row.get("market")}
    target_markets = {str(row.get("market") or "") for row in target}
    removed = [row for row in target if rule(row)]
    removed_markets = {str(row.get("market") or "") for row in removed}
    kept = [row for row in target if str(row.get("market") or "") not in removed_markets]
    needed = max(0, ceil_entries_for_floor(denominator) - len(kept))

    missed_repairs = clean_repair_rows(all_rows, all_markets - target_markets)
    chosen = missed_repairs[:needed]
    chosen_markets = {str(row.get("market") or "") for row in chosen}
    if len(chosen) < needed:
        kept_markets = {str(row.get("market") or "") for row in kept}
        extras = clean_repair_rows(all_rows, all_markets - kept_markets - chosen_markets)
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
        "rule": name,
        "removed": len(removed),
        "needed_repairs": needed,
        "chosen_repairs": len(chosen),
        "target_summary": target_summary,
        "removed_summary": summarize(removed, denominator),
        "repair_summary": summarize(chosen, denominator),
        "candidate_summary": candidate_summary,
        "delta_vs_target_cents": float(candidate_summary.get("net_cents") or 0.0) - float(target_summary.get("net_cents") or 0.0),
        "removed_rows": [compact(row) for row in removed],
        "repair_rows": [compact(row) for row in chosen],
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": raw_edge(row),
        "seconds_to_close": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
    }


def build_report() -> dict[str, Any]:
    ranked = [evaluate_rule(name, rule) for name, rule in RULES.items()]
    ranked.sort(key=lambda row: float(row.get("delta_vs_target_cents") or 0.0), reverse=True)
    return {
        "diagnostic": "boundary_clock_hazard_repair",
        "coverage_floor": COVERAGE_FLOOR,
        "physics": "Early near-boundary high-recross rows can be unresolved path turbulence rather than durable FV edge.",
        "ranked": ranked,
        "interpretation": interpretation(ranked),
    }


def interpretation(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["No rows available."]
    best = rows[0]
    cand = best.get("candidate_summary") or {}
    removed = best.get("removed_summary") or {}
    return [
        f"Best rule is {best.get('rule')} with net {cand.get('net_cents')}c and delta {best.get('delta_vs_target_cents')}c.",
        f"Coverage is {cand.get('coverage_pct')}% after removing {best.get('removed')} target rows and adding {best.get('chosen_repairs')} repairs.",
        f"Removed rows alone had net {removed.get('net_cents')}c.",
        "This is diagnostic only; a live candidate would need a fresh frozen-forward gate.",
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
        "# v28 Boundary-Clock Hazard Repair",
        "",
        "Diagnostic-only: no live bot changes and no orders.",
        "",
        f"- Physics: {report.get('physics')}",
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
        "| rank | rule | removed | repairs | coverage | net c | delta c | W/L | removed net c | repair net c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        cand = row.get("candidate_summary") or {}
        removed = row.get("removed_summary") or {}
        repair = row.get("repair_summary") or {}
        lines.append(
            f"| {idx} | {row.get('rule')} | {row.get('removed')} | {row.get('chosen_repairs')} | "
            f"{fmt(cand.get('coverage_pct'))} | {fmt(cand.get('net_cents'))} | "
            f"{fmt(row.get('delta_vs_target_cents'))} | {cand.get('wins')}/{cand.get('losses')} | "
            f"{fmt(removed.get('net_cents'))} | {fmt(repair.get('net_cents'))} |"
        )
    best = (report.get("ranked") or [{}])[0]
    lines.extend([
        "",
        "## Best Removed Rows",
        "",
        "| market | source | side | won | net c | p | ask | edge | stc | abs d | recross |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in best.get("removed_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('seconds_to_close'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
