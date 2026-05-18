"""Bakeoff for danger-tag removal plus coverage repair variants.

Research-only; no live bot changes or orders.

This does not search arbitrary thresholds. It compares a small set of named
physical danger definitions already surfaced by attribution:
    - paid-price fragility;
    - weak boundary turbulence;
    - both together.
Each variant removes matching target rows and repairs coverage from clean rows
in otherwise missed markets first.
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
    row_net_after_fee,
    summarize,
)
from probe_v28_danger_tag_replacement_diagnostic import danger_tags


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_danger_repair_bakeoff_latest.json"
OUT_MD = OUT_DIR / "v28_danger_repair_bakeoff_latest.md"


def has_tag(tag: str) -> Callable[[dict[str, Any]], bool]:
    return lambda row: tag in danger_tags(row)


VARIANTS: dict[str, Callable[[dict[str, Any]], bool]] = {
    "paid_price_fragile_only": has_tag("paid_price_fragile"),
    "weak_boundary_turbulence_only": has_tag("weak_boundary_turbulence"),
    "paid_or_weak_boundary": lambda row: bool({"paid_price_fragile", "weak_boundary_turbulence"} & set(danger_tags(row))),
}


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def net_key(row: dict[str, Any]) -> float:
    value = row.get("net_gross_cents_after_entry_fee")
    if value is None:
        value = row_net_after_fee(row)
    return float(value or 0.0)


def repair_for_variant(
    all_rows: list[dict[str, Any]],
    target: list[dict[str, Any]],
    denominator: int,
    pred: Callable[[dict[str, Any]], bool],
) -> dict[str, Any]:
    target_markets = {str(row.get("market") or "") for row in target}
    removed = [row for row in target if pred(row)]
    removed_markets = {str(row.get("market") or "") for row in removed}
    kept = [row for row in target if str(row.get("market") or "") not in removed_markets]
    kept_markets = {str(row.get("market") or "") for row in kept}
    all_markets = {str(row.get("market") or "") for row in all_rows if row.get("market")}
    needed = max(0, ceil_entries_for_floor(denominator) - len(kept))

    missed_markets = all_markets - target_markets
    missed_repairs = first_clean_by_market(all_rows, missed_markets)
    chosen = missed_repairs[:needed]

    if len(chosen) < needed:
        chosen_markets = {str(row.get("market") or "") for row in chosen}
        eligible_extra_markets = all_markets - kept_markets - chosen_markets
        extras = first_clean_by_market(all_rows, eligible_extra_markets)
        extras = [row for row in extras if str(row.get("market") or "") not in chosen_markets]
        # If we must repair from non-missed markets, prefer better realized rows in diagnostic
        # view only to expose whether opportunity exists. Frozen validation must fix timing.
        extras.sort(key=net_key, reverse=True)
        for row in extras:
            if len(chosen) >= needed:
                break
            market = str(row.get("market") or "")
            if market in chosen_markets:
                continue
            chosen.append(row)
            chosen_markets.add(market)

    candidate = kept + chosen
    return {
        "removed": removed,
        "kept": kept,
        "missed_repairs": missed_repairs,
        "chosen_repairs": chosen,
        "candidate": candidate,
        "needed_repairs": needed,
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "source": row.get("source"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "danger_tags": danger_tags(row),
    }


def build_report() -> dict[str, Any]:
    all_rows, target, denominator, _forward_markets = build_surfaces()
    target_summary = summarize(target, denominator)
    rows = []
    for name, pred in VARIANTS.items():
        result = repair_for_variant(all_rows, target, denominator, pred)
        candidate_summary = summarize(result["candidate"], denominator)
        removed_summary = summarize(result["removed"], denominator)
        repair_summary = summarize(result["chosen_repairs"], denominator)
        rows.append({
            "variant": name,
            "needed_repairs": result["needed_repairs"],
            "removed_summary": removed_summary,
            "repair_summary": repair_summary,
            "candidate_summary": candidate_summary,
            "delta_vs_target_cents": as_float(candidate_summary.get("net_cents")) - as_float(target_summary.get("net_cents")),
            "removed_rows": [compact(row) for row in result["removed"]],
            "chosen_repairs": [compact(row) for row in result["chosen_repairs"]],
        })
    rows.sort(key=lambda row: float(row.get("delta_vs_target_cents") or 0.0), reverse=True)
    return {
        "diagnostic": "danger_repair_bakeoff",
        "target_summary": target_summary,
        "forward_denominator": denominator,
        "coverage_floor": COVERAGE_FLOOR,
        "ranked": rows,
        "interpretation": interpretation(target_summary, rows),
    }


def interpretation(target_summary: dict[str, Any], rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["No variants scored."]
    best = rows[0]
    best_sum = best.get("candidate_summary") or {}
    return [
        f"Best diagnostic variant is {best.get('variant')} with net {best_sum.get('net_cents')}c versus target {target_summary.get('net_cents')}c.",
        f"Coverage for best variant is {best_sum.get('coverage_pct')}%.",
        "Rows repaired from non-missed markets use realized-net ordering only as diagnostic opportunity mapping; this is not promotion evidence.",
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
    target = report.get("target_summary") or {}
    lines = [
        "# v28 Danger Repair Bakeoff",
        "",
        "Diagnostic-only bakeoff for named physical danger removals plus coverage repair.",
        "",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Target net/coverage: `{fmt(target.get('net_cents'))}/{fmt(target.get('coverage_pct'))}`",
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
        "| rank | variant | removed | repairs | coverage | net c | delta c | W/L | repair net c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        cand = row.get("candidate_summary") or {}
        rem = row.get("removed_summary") or {}
        repairs = row.get("repair_summary") or {}
        lines.append(
            f"| {idx} | {row.get('variant')} | {rem.get('entries')} | {repairs.get('entries')} | "
            f"{fmt(cand.get('coverage_pct'))} | {fmt(cand.get('net_cents'))} | {fmt(row.get('delta_vs_target_cents'))} | "
            f"{cand.get('wins')}/{cand.get('losses')} | {fmt(repairs.get('net_cents'))} |"
        )
    best = (report.get("ranked") or [{}])[0]
    lines.extend([
        "",
        "## Best Variant Repairs",
        "",
        "| market | source | side | won | net c | p | ask | tags |",
        "|---|---|---|---|---:|---:|---:|---|",
    ])
    for row in best.get("chosen_repairs") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | "
            f"{', '.join(row.get('danger_tags') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
