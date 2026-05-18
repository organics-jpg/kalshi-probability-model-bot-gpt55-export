"""Weak-boundary reversal strategy diagnostic.

Research-only; no live bot changes or orders.

Physics hypothesis:
    A weak near-boundary high-recross signal is often not a stable side thesis.
    The useful action may be to wait for the boundary to reveal a later
    opposite-side executable edge, rather than buying the first side or simply
    replacing with arbitrary clean rows.

This diagnostic is intentionally simple and predeclared:
    - Start from the target 75% coverage surface.
    - For high-recross, near-boundary rows with raw p <= 0.60, skip the first
      side and take the first same-market opposite-side row within 240 seconds
      that clears p>=0.50 and raw edge>=0.
    - If no opposite row appears, abstain.
    - Repair coverage from clean rows that are not weak-boundary rows.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_boundary_reversal_opportunity import opposite_replacements, row_net_after_fee
from probe_v28_composite_false_conviction_repair_bakeoff import first_clean_by_market_scored, score_farthest_boundary
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, build_surfaces, summarize


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_weak_boundary_reversal_strategy_latest.json"
OUT_MD = OUT_DIR / "v28_weak_boundary_reversal_strategy_latest.md"

P_MAX = 0.60
RECROSS_FLOOR = 0.75
ABS_D_MAX = 0.30
MAX_OPPOSITE_DELAY_SECONDS = 240.0


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def is_weak_boundary(row: dict[str, Any]) -> bool:
    p = as_float(row.get("p_side"))
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    return (
        p is not None
        and recross is not None
        and abs_d is not None
        and p <= P_MAX
        and recross >= RECROSS_FLOOR
        and abs_d <= ABS_D_MAX
    )


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def net_ready(row: dict[str, Any]) -> dict[str, Any]:
    net = row.get("net_gross_cents_after_entry_fee")
    if net is None:
        net = row_net_after_fee(row)
    return {**row, "net_gross_cents_after_entry_fee": net}


def choose_opposite(all_rows: list[dict[str, Any]], row: dict[str, Any]) -> dict[str, Any] | None:
    replacements = [
        repl for repl in opposite_replacements(all_rows, row)
        if float(repl.get("replacement_delay_seconds") or 999999.0) <= MAX_OPPOSITE_DELAY_SECONDS
    ]
    return net_ready(replacements[0]) if replacements else None


def clean_repair_candidates(all_rows: list[dict[str, Any]], markets: set[str]) -> list[dict[str, Any]]:
    rows = first_clean_by_market_scored(all_rows, markets, score_farthest_boundary, chronological=False)
    return [net_ready(row) for row in rows if not is_weak_boundary(row)]


def build_report() -> dict[str, Any]:
    all_rows, target, denominator, forward_markets = build_surfaces()
    all_markets = {str(row.get("market") or "") for row in all_rows if row.get("market")}
    target_markets = {str(row.get("market") or "") for row in target}
    weak = [net_ready(row) for row in target if is_weak_boundary(row)]
    weak_markets = {str(row.get("market") or "") for row in weak}
    kept = [net_ready(row) for row in target if str(row.get("market") or "") not in weak_markets]
    replacements: list[dict[str, Any]] = []
    cases = []
    for row in weak:
        repl = choose_opposite(all_rows, row)
        if repl is not None:
            replacements.append(repl)
        cases.append({"target": row_view(row), "replacement": row_view(repl) if repl else None})

    current = kept + replacements
    needed = max(0, ceil_entries_for_floor(denominator) - len(current))
    used_markets = {str(row.get("market") or "") for row in current if row.get("market")}
    repairs = clean_repair_candidates(all_rows, forward_markets - target_markets)[:needed]
    repair_markets = {str(row.get("market") or "") for row in repairs}
    if len(repairs) < needed:
        extras = clean_repair_candidates(all_rows, all_markets - used_markets - repair_markets)
        for row in extras:
            if len(repairs) >= needed:
                break
            market = str(row.get("market") or "")
            if market in repair_markets:
                continue
            repairs.append(row)
            repair_markets.add(market)
    candidate = current + repairs
    target_net = summarize([net_ready(row) for row in target], denominator)
    candidate_summary = summarize(candidate, denominator)
    return {
        "diagnostic": "weak_boundary_reversal_strategy",
        "requirements": {
            "p_max": P_MAX,
            "recross_floor": RECROSS_FLOOR,
            "abs_d_max": ABS_D_MAX,
            "max_opposite_delay_seconds": MAX_OPPOSITE_DELAY_SECONDS,
            "coverage_floor": COVERAGE_FLOOR,
        },
        "forward_denominator": denominator,
        "target_summary": target_net,
        "weak_summary": summarize(weak, denominator),
        "kept_summary": summarize(kept, denominator),
        "replacement_summary": summarize(replacements, denominator),
        "repair_summary": summarize(repairs, denominator),
        "candidate_summary": candidate_summary,
        "delta_vs_target_cents": float(candidate_summary.get("net_cents") or 0.0)
        - float(target_net.get("net_cents") or 0.0),
        "needed_repairs": needed,
        "chosen_repairs": len(repairs),
        "coverage_repaired": len(repairs) >= needed,
        "cases": cases,
        "interpretation": interpretation(target_net, candidate_summary, weak, replacements, repairs),
    }


def row_view(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
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


def interpretation(
    target: dict[str, Any],
    candidate: dict[str, Any],
    weak: list[dict[str, Any]],
    replacements: list[dict[str, Any]],
    repairs: list[dict[str, Any]],
) -> list[str]:
    return [
        f"Weak-boundary rows removed: {len(weak)}; opposite replacements found: {len(replacements)}.",
        f"Repair rows added: {len(repairs)}.",
        f"Target net {target.get('net_cents')}c; candidate net {candidate.get('net_cents')}c; coverage {candidate.get('coverage_pct')}%.",
        "This is diagnostic only; any viable version requires frozen forward validation.",
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
        "# v28 Weak-Boundary Reversal Strategy",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Requirements: `{report.get('requirements')}`",
        f"- Delta vs target: `{fmt(report.get('delta_vs_target_cents'))}c`",
        f"- Coverage repaired: `{report.get('coverage_repaired')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Summaries",
        "",
        "| slice | entries | settled | W/L | coverage | net c | avg c |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for name, key in [
        ("target", "target_summary"),
        ("weak_removed", "weak_summary"),
        ("kept", "kept_summary"),
        ("opposite_replacements", "replacement_summary"),
        ("repairs", "repair_summary"),
        ("candidate", "candidate_summary"),
    ]:
        row = report.get(key) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend([
        "",
        "## Reversal Cases",
        "",
        "| market | target side | target won | target net | p | recross | abs d | repl side | repl won | repl net | delay |",
        "|---|---|---|---:|---:|---:|---:|---|---|---:|---:|",
    ])
    for case in report.get("cases") or []:
        target = case.get("target") or {}
        repl = case.get("replacement") or {}
        lines.append(
            f"| {target.get('market')} | {target.get('side')} | {target.get('side_won')} | {fmt(target.get('net_cents'))} | "
            f"{fmt(target.get('p_side'))} | {fmt(target.get('recross_hazard_score'))} | {fmt(target.get('abs_d_sigma'))} | "
            f"{repl.get('side')} | {repl.get('side_won')} | {fmt(repl.get('net_cents'))} | {fmt(repl.get('replacement_delay_seconds'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
