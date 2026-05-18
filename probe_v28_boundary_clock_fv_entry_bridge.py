"""Entry bridge for the boundary-clock FV overlay.

Research-only; no live bot changes or orders.

The boundary-clock FV overlay says some rows should collapse to p=0.50. This
probe asks whether a simple adjusted-edge entry rule can use that FV directly:
skip target rows where adjusted FV no longer clears executable ask, then repair
coverage from clean low-recross opportunities.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_fv_overlay import raw_prob, shrink_prob
from probe_v28_boundary_clock_hazard_repair import clean_repair_rows, compact
from probe_v28_coverage_repair_pool_diagnostic import (
    COVERAGE_FLOOR,
    as_float,
    build_surfaces,
    summarize,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_clock_fv_entry_bridge_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_fv_entry_bridge_latest.md"

EDGE_FLOORS = [-0.02, 0.0, 0.01, 0.02, 0.04]


def adjusted_p(row: dict[str, Any]) -> float:
    return shrink_prob(row, 0.0)


def ask(row: dict[str, Any]) -> float | None:
    return as_float(row.get("ask_prob"))


def adjusted_edge(row: dict[str, Any]) -> float | None:
    a = ask(row)
    if a is None:
        return None
    return adjusted_p(row) - a


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def evaluate_floor(edge_floor: float) -> dict[str, Any]:
    all_rows, target, denominator, _forward_markets = build_surfaces()
    all_markets = {str(row.get("market") or "") for row in all_rows if row.get("market")}
    target_markets = {str(row.get("market") or "") for row in target}
    skipped = [
        row for row in target
        if adjusted_edge(row) is not None and float(adjusted_edge(row) or 0.0) < edge_floor
    ]
    skipped_markets = {str(row.get("market") or "") for row in skipped}
    kept = [row for row in target if str(row.get("market") or "") not in skipped_markets]
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
        "edge_floor": edge_floor,
        "skipped": len(skipped),
        "needed_repairs": needed,
        "chosen_repairs": len(chosen),
        "target_summary": target_summary,
        "skipped_summary": summarize(skipped, denominator),
        "repair_summary": summarize(chosen, denominator),
        "candidate_summary": candidate_summary,
        "delta_vs_target_cents": float(candidate_summary.get("net_cents") or 0.0) - float(target_summary.get("net_cents") or 0.0),
        "skipped_rows": [row_view(row) for row in skipped],
        "repair_rows": [compact(row) for row in chosen],
    }


def row_view(row: dict[str, Any]) -> dict[str, Any]:
    view = compact(row)
    view["raw_p"] = raw_prob(row)
    view["adjusted_p"] = adjusted_p(row)
    view["adjusted_edge"] = adjusted_edge(row)
    return view


def build_report() -> dict[str, Any]:
    ranked = [evaluate_floor(floor) for floor in EDGE_FLOORS]
    ranked.sort(key=lambda row: float(row.get("delta_vs_target_cents") or 0.0), reverse=True)
    return {
        "diagnostic": "boundary_clock_fv_entry_bridge",
        "coverage_floor": COVERAGE_FLOOR,
        "physics": "Use boundary-clock adjusted FV as the entry surface; if adjusted FV no longer pays for ask, skip and repair coverage.",
        "ranked": ranked,
        "interpretation": interpretation(ranked),
    }


def interpretation(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["No rows available."]
    best = rows[0]
    cand = best.get("candidate_summary") or {}
    skipped = best.get("skipped_summary") or {}
    return [
        f"Best adjusted-edge floor is {best.get('edge_floor')} with net {cand.get('net_cents')}c and delta {best.get('delta_vs_target_cents')}c.",
        f"Coverage is {cand.get('coverage_pct')}% after skipping {best.get('skipped')} rows and adding {best.get('chosen_repairs')} repairs.",
        f"Skipped rows alone had net {skipped.get('net_cents')}c.",
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
        "# v28 Boundary-Clock FV Entry Bridge",
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
        "| rank | adj edge floor | skipped | repairs | coverage | net c | delta c | W/L | skipped net c | repair net c |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        cand = row.get("candidate_summary") or {}
        skipped = row.get("skipped_summary") or {}
        repair = row.get("repair_summary") or {}
        lines.append(
            f"| {idx} | {fmt(row.get('edge_floor'))} | {row.get('skipped')} | {row.get('chosen_repairs')} | "
            f"{fmt(cand.get('coverage_pct'))} | {fmt(cand.get('net_cents'))} | {fmt(row.get('delta_vs_target_cents'))} | "
            f"{cand.get('wins')}/{cand.get('losses')} | {fmt(skipped.get('net_cents'))} | {fmt(repair.get('net_cents'))} |"
        )
    best = (report.get("ranked") or [{}])[0]
    lines.extend([
        "",
        "## Best Skipped Rows",
        "",
        "| market | source | side | won | net c | raw p | adj p | ask | adj edge | stc | abs d | recross |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in best.get("skipped_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_p'))} | {fmt(row.get('adjusted_p'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('adjusted_edge'))} | "
            f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
