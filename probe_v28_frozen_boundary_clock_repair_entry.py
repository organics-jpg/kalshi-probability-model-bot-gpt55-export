"""Frozen forward challenger for v28 boundary-clock repair entry.

Research-only; no live bot changes or orders.

Frozen rule:
    Start from the target coverage policy. Skip rows matching the
    clock_composite boundary hazard:
      - early cheap near-boundary high-recross rows, or
      - early expensive low-edge rows.
    Restore the 75% coverage floor with clean repair rows ranked by lowest
    recross hazard, preferring otherwise missed markets first.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_hazard_repair import clock_composite, compact
from probe_v28_coverage_repair_pool_diagnostic import (
    COVERAGE_FLOOR,
    as_float,
    is_clean_repair,
    raw_edge,
    row_net_after_fee,
    summarize,
)
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state
from probe_v28_target_coverage_fv_overlay_validator import apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_boundary_clock_repair_entry_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_boundary_clock_repair_entry_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_boundary_clock_repair_entry_latest.md"

POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"
MIN_SETTLED = 30


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "base_policy": POLICY,
        "candidate": "skip_boundary_clock_composite_repair_lowest_recross",
        "coverage_floor": COVERAGE_FLOOR,
        "danger_rule": "early_boundary_cheap_recross OR expensive_low_edge_clock",
        "repair_rule": "clean repair rows ranked by lowest recross hazard, missed markets first",
        "physics": "Near the boundary, early high-recross cheapness is unresolved path turbulence; early expensive low-edge rows are paid-price fragility.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def recross_score(row: dict[str, Any]) -> float:
    recross = as_float(row.get("recross_hazard_score"))
    return recross if recross is not None else 999.0


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def clean_rows_by_market(rows: list[dict[str, Any]], markets: set[str]) -> list[dict[str, Any]]:
    candidates = []
    for row in rows:
        market = str(row.get("market") or "")
        if market not in markets or not is_clean_repair(row):
            continue
        candidates.append({
            **row,
            "raw_edge_prob": raw_edge(row),
            "net_gross_cents_after_entry_fee": row_net_after_fee(row),
            "repair_score": -recross_score(row),
        })
    candidates.sort(key=lambda row: (recross_score(row), str(row.get("ts_wall") or "")))
    out = []
    seen = set()
    for row in candidates:
        market = str(row.get("market") or "")
        if market in seen:
            continue
        out.append(row)
        seen.add(market)
    return out


def future_surfaces(freeze_ts: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    freeze_dt = parse_ts(freeze_ts)
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    all_rows = [row for row in all_rows if str(row.get("market") or "") in forward_markets]
    target = apply_policy(selected_base_rows(), POLICY)
    target = [row for row in target if str(row.get("market") or "") in forward_markets]
    return all_rows, target, len(forward_markets)


def build_candidate(all_rows: list[dict[str, Any]], target: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    all_markets = {str(row.get("market") or "") for row in all_rows if row.get("market")}
    target_markets = {str(row.get("market") or "") for row in target}
    danger = [row for row in target if clock_composite(row)]
    danger_markets = {str(row.get("market") or "") for row in danger}
    kept = [row for row in target if str(row.get("market") or "") not in danger_markets]
    needed = max(0, ceil_entries_for_floor(denominator) - len(kept))

    missed = clean_rows_by_market(all_rows, all_markets - target_markets)
    chosen = missed[:needed]
    chosen_markets = {str(row.get("market") or "") for row in chosen}
    if len(chosen) < needed:
        kept_markets = {str(row.get("market") or "") for row in kept}
        extras = clean_rows_by_market(all_rows, all_markets - kept_markets - chosen_markets)
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
        "danger": danger,
        "kept": kept,
        "repairs": chosen,
        "candidate": candidate,
        "needed_repairs": needed,
        "missed_repairs_available": len(missed),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    all_rows, target, denominator = future_surfaces(str(state["freeze_ts_utc"]))
    built = build_candidate(all_rows, target, denominator)
    target_summary = summarize(target, denominator)
    candidate_summary = summarize(built["candidate"], denominator)
    blockers = []
    if int(candidate_summary.get("settled") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if candidate_summary.get("coverage_pct") is None or float(candidate_summary["coverage_pct"]) < COVERAGE_FLOOR:
        blockers.append("coverage_too_low")
    if float(candidate_summary.get("net_cents") or 0.0) <= 0.0:
        blockers.append("net_not_positive")
    return {
        "freeze": state,
        "future_denominator": denominator,
        "target_summary": target_summary,
        "danger_summary": summarize(built["danger"], denominator),
        "kept_summary": summarize(built["kept"], denominator),
        "repair_summary": summarize(built["repairs"], denominator),
        "candidate_summary": candidate_summary,
        "delta_vs_target_cents": float(candidate_summary.get("net_cents") or 0.0) - float(target_summary.get("net_cents") or 0.0),
        "needed_repairs": built["needed_repairs"],
        "missed_repairs_available": built["missed_repairs_available"],
        "danger_rows": [compact(row) for row in built["danger"]],
        "repair_rows": [compact(row) for row in built["repairs"]],
        "candidate_live_ready": not blockers,
        "blockers": blockers,
        "interpretation": interpretation(target_summary, candidate_summary, built, blockers),
    }


def interpretation(
    target_summary: dict[str, Any],
    candidate_summary: dict[str, Any],
    built: dict[str, Any],
    blockers: list[str],
) -> list[str]:
    notes = [
        f"Future candidate has {candidate_summary.get('entries')} entries and {candidate_summary.get('settled')} settled rows.",
        f"Candidate net is {candidate_summary.get('net_cents')}c versus target {target_summary.get('net_cents')}c.",
        f"Boundary-clock rows removed: {len(built['danger'])}; repair rows added: {len(built['repairs'])}.",
    ]
    if blockers:
        notes.append(f"Promotion blockers: {', '.join(blockers)}.")
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
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen Boundary-Clock Repair Entry",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Needed/missed repairs: `{report.get('needed_repairs')}/{report.get('missed_repairs_available')}`",
        f"- Delta vs target: `{fmt(report.get('delta_vs_target_cents'))}c`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
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
        "| slice | entries | settled | W/L | coverage | net c | avg net c |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for name, key in [
        ("target", "target_summary"),
        ("danger_removed", "danger_summary"),
        ("kept", "kept_summary"),
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
        "## Removed Rows",
        "",
        "| market | source | side | won | net c | p | ask | edge | stc | abs d | recross |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("danger_rows") or []:
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
