"""Frozen forward validator for the side-asymmetry FV entry bridge.

Research-only; no live bot changes and no orders.

Frozen candidate:
    Start from the target-coverage v28 entry surface. Use the
    clock-plus-side-asymmetry adjusted FV as the entry probability. Skip target
    entries whose adjusted edge versus ask is below 2pp. Restore the 75% market
    coverage floor with strict clean repair rows that also clear the same
    adjusted-edge floor, ranked by farthest boundary distance.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_hazard_repair import clean_repair_rows, compact
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, as_float, build_surfaces, summarize
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_side_asymmetry_fv_entry_bridge import adjusted_edge, adjusted_p
from probe_v28_target_coverage_fv_overlay_validator import COVERAGE_STATE_JSON, load_json
from probe_v28_boundary_clock_fv_overlay import raw_prob


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_side_asymmetry_entry_bridge_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_side_asymmetry_entry_bridge_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_side_asymmetry_entry_bridge_latest.md"

EDGE_FLOOR = 0.02
MIN_SETTLED = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    target_state = load_json(COVERAGE_STATE_JSON)
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate": "target_coverage_side_asymmetry_adjusted_edge2pp_strict_farthest_boundary_repair",
        "base_policy": "raw_p50_turbulence_valve_edge4_p60_recross75_near25",
        "edge_floor": EDGE_FLOOR,
        "repair_ranker": "farthest_boundary",
        "source_discovery": "v28_side_asymmetry_bridge_strict_repair_latest",
        "source_coverage_freeze_ts": target_state.get("source_coverage_freeze_ts") or target_state.get("freeze_ts"),
        "rule": (
            "Start from the target-coverage policy; skip target rows where adjusted_probability - ask_probability < 0.02; "
            "repair coverage with strict clean rows clearing the same adjusted-edge floor, ranked by abs_d_sigma descending."
        ),
        "physics": (
            "Boundary-clock and NO-side asymmetry states can be unresolved path states where raw v28 overstates certainty. "
            "The adjusted FV collapses those rows toward 50/50; if the adjusted edge no longer pays the ask, entry is false conviction. "
            "Repairs must be physically clean and far from the boundary, not just retrospective replacements."
        ),
        "min_settled": MIN_SETTLED,
        "coverage_floor": COVERAGE_MIN,
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def row_market(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def enrich(row: dict[str, Any]) -> dict[str, Any]:
    edge = adjusted_edge(row)
    return {
        **row,
        "raw_p": raw_prob(row),
        "adjusted_p": adjusted_p(row),
        "adjusted_edge": edge,
    }


def future_surfaces(state: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int, set[str]]:
    freeze_dt = parse_ts(str(state["freeze_ts_utc"]))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    all_rows, target, _denominator, _forward = build_surfaces()
    all_rows = [enrich(row) for row in all_rows if row_market(row) in forward_markets]
    target = [enrich(row) for row in target if row_market(row) in forward_markets]
    return all_rows, target, len(forward_markets), forward_markets


def repair_sort_key(row: dict[str, Any]) -> tuple[float, float, str]:
    abs_d = as_float(row.get("abs_d_sigma")) or -1.0
    edge = as_float(row.get("adjusted_edge")) or -99.0
    return (-abs_d, -edge, str(row.get("ts_wall") or ""))


def strict_repairs(all_rows: list[dict[str, Any]], markets: set[str]) -> list[dict[str, Any]]:
    candidates = []
    for row in clean_repair_rows(all_rows, markets):
        edge = as_float(row.get("adjusted_edge"))
        if edge is None or edge < EDGE_FLOOR:
            continue
        candidates.append(row)
    return sorted(candidates, key=repair_sort_key)


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    all_rows, target, denominator, forward_markets = future_surfaces(state)
    skipped = [row for row in target if (as_float(row.get("adjusted_edge")) is not None and float(row["adjusted_edge"]) < EDGE_FLOOR)]
    skipped_markets = {row_market(row) for row in skipped}
    kept = [row for row in target if row_market(row) not in skipped_markets]
    kept_markets = {row_market(row) for row in kept}
    target_markets = {row_market(row) for row in target}
    needed = max(0, ceil_entries_for_floor(denominator) - len(kept))

    repair_pool = strict_repairs(all_rows, forward_markets - target_markets)
    chosen_repairs = repair_pool[:needed]
    if len(chosen_repairs) < needed:
        chosen_markets = {row_market(row) for row in chosen_repairs}
        extras = strict_repairs(all_rows, forward_markets - kept_markets - chosen_markets)
        for row in extras:
            market = row_market(row)
            if market in chosen_markets:
                continue
            chosen_repairs.append(row)
            chosen_markets.add(market)
            if len(chosen_repairs) >= needed:
                break

    candidate = kept + chosen_repairs
    target_summary = summarize(target, denominator)
    candidate_summary = summarize(candidate, denominator)
    skipped_summary = summarize(skipped, denominator)
    repair_summary = summarize(chosen_repairs, denominator)
    target_net = as_float(target_summary.get("net_cents")) or 0.0
    candidate_net = as_float(candidate_summary.get("net_cents")) or 0.0
    coverage = as_float(candidate_summary.get("coverage_pct"))
    settled = int(as_float(candidate_summary.get("settled")) or 0)
    delta = candidate_net - target_net
    blockers = []
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if delta <= 0.0:
        blockers.append("delta_not_positive")
    if candidate_net <= 0.0:
        blockers.append("net_not_positive")
    if len(chosen_repairs) < needed:
        blockers.append("insufficient_strict_repairs")
    return {
        "freeze": state,
        "future_denominator": denominator,
        "needed_repairs": needed,
        "available_strict_missed_repairs": len(repair_pool),
        "target_summary": target_summary,
        "candidate_summary": candidate_summary,
        "skipped_summary": skipped_summary,
        "repair_summary": repair_summary,
        "delta_vs_target_cents": delta,
        "candidate_live_ready": not blockers,
        "blockers": blockers,
        "skipped_rows": [row_view(row) for row in skipped],
        "repair_rows": [row_view(row) for row in chosen_repairs],
        "interpretation": [
            f"Frozen side-asymmetry entry bridge has denominator {denominator}, candidate entries/settled {candidate_summary.get('entries')}/{candidate_summary.get('settled')}.",
            f"Coverage {candidate_summary.get('coverage_pct')}%; candidate net {candidate_net}c versus target {target_net}c; delta {delta}c.",
            f"Skipped rows were {skipped_summary.get('wins')}/{skipped_summary.get('losses')} for {skipped_summary.get('net_cents')}c; repairs were {repair_summary.get('wins')}/{repair_summary.get('losses')} for {repair_summary.get('net_cents')}c.",
            f"Strict repairs chosen/needed/available: {len(chosen_repairs)}/{needed}/{len(repair_pool)}.",
            f"Promotion blockers: {', '.join(blockers) if blockers else 'none'}.",
        ],
    }


def row_view(row: dict[str, Any]) -> dict[str, Any]:
    base = compact(row)
    base["raw_p"] = row.get("raw_p")
    base["adjusted_p"] = row.get("adjusted_p")
    base["adjusted_edge"] = row.get("adjusted_edge")
    return base


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen Side-Asymmetry Entry Bridge",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Edge floor: `{freeze.get('edge_floor')}`",
        f"- Repair ranker: `{freeze.get('repair_ranker')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Candidate live-ready: `{report.get('candidate_live_ready')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Scorecard",
        "",
        "| surface | entries | settled | W/L | coverage | net c | avg c |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for key in ["target_summary", "candidate_summary", "skipped_summary", "repair_summary"]:
        row = report.get(key) or {}
        lines.append(
            f"| {key} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend([
        "",
        "## Skipped Rows",
        "",
        "| market | source | side | won | net c | raw p | adj p | adj edge | ask | stc | abs d | recross |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("skipped_rows") or []:
        lines.append(row_line(row))
    lines.extend([
        "",
        "## Repair Rows",
        "",
        "| market | source | side | won | net c | raw p | adj p | adj edge | ask | stc | abs d | recross |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("repair_rows") or []:
        lines.append(row_line(row))
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def row_line(row: dict[str, Any]) -> str:
    return (
        f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
        f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_p'))} | {fmt(row.get('adjusted_p'))} | "
        f"{fmt(row.get('adjusted_edge'))} | {fmt(row.get('ask_prob'))} | "
        f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} |"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
