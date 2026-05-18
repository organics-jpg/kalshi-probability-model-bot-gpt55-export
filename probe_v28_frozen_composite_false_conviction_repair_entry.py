"""Frozen composite false-conviction repair-entry validator.

Research-only; no live bot changes or orders.

Frozen rule:
    Start from the target coverage policy. Remove target rows in the composite
    false-conviction zone, then restore the 75% coverage floor with clean
    repair rows ranked by highest raw probability.

The rule is intentionally frozen after the diagnostic that discovered it, so
promotion can only come from future rows.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import (
    COVERAGE_FLOOR,
    as_float,
    is_clean_repair,
    raw_edge,
    row_net_after_fee,
    summarize,
)
from probe_v28_false_conviction_physics_audit import is_false_conviction_zone
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state
from probe_v28_target_coverage_fv_overlay_validator import apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_composite_false_conviction_repair_entry_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_composite_false_conviction_repair_entry_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_composite_false_conviction_repair_entry_latest.md"

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
        "candidate": "skip_composite_false_conviction_repair_highest_raw_p",
        "coverage_floor": COVERAGE_FLOOR,
        "danger_rule": "composite false-conviction zone",
        "repair_rule": "clean repairs ranked by highest raw p_side",
        "physics": (
            "Early boundary/recross states can produce false raw-model conviction. "
            "If the market still needs coverage, replace those rows with high-conviction clean rows."
        ),
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def repair_score(row: dict[str, Any]) -> tuple[float, str]:
    return (-(as_float(row.get("p_side")) or -999.0), str(row.get("ts_wall") or ""))


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
            "repair_score": as_float(row.get("p_side")),
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


def future_surfaces(freeze_ts: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    timing = market_timing(parse_ts(freeze_ts))
    forward_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    all_rows = [row for row in all_rows if str(row.get("market") or "") in forward_markets]
    target = apply_policy(selected_base_rows(), POLICY)
    target = [row for row in target if str(row.get("market") or "") in forward_markets]
    return all_rows, target, len(forward_markets)


def build_candidate(all_rows: list[dict[str, Any]], target: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    all_markets = {str(row.get("market") or "") for row in all_rows if row.get("market")}
    target_markets = {str(row.get("market") or "") for row in target}
    danger = [row for row in target if is_false_conviction_zone(row)]
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
    return {
        "danger": danger,
        "kept": kept,
        "repairs": chosen,
        "candidate": kept + chosen,
        "needed_repairs": needed,
        "missed_repairs_available": len(missed),
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
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "repair_score": row.get("repair_score"),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    all_rows, target, denominator = future_surfaces(str(state["freeze_ts_utc"]))
    built = build_candidate(all_rows, target, denominator)
    target_summary = summarize(target, denominator)
    candidate_summary = summarize(built["candidate"], denominator)
    blockers = []
    coverage = candidate_summary.get("coverage_pct")
    if int(candidate_summary.get("settled") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or float(coverage) < COVERAGE_FLOOR:
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
        "delta_vs_target_cents": float(candidate_summary.get("net_cents") or 0.0)
        - float(target_summary.get("net_cents") or 0.0),
        "needed_repairs": built["needed_repairs"],
        "missed_repairs_available": built["missed_repairs_available"],
        "danger_rows": [compact(row) for row in built["danger"]],
        "repair_rows": [compact(row) for row in built["repairs"]],
        "candidate_live_ready": not blockers,
        "blockers": blockers,
        "interpretation": [
            f"Future candidate has {candidate_summary.get('entries')} entries and {candidate_summary.get('settled')} settled rows.",
            f"Candidate net is {candidate_summary.get('net_cents')}c versus target {target_summary.get('net_cents')}c.",
            f"Composite false-conviction rows removed: {len(built['danger'])}; repair rows added: {len(built['repairs'])}.",
            f"Promotion blockers: {', '.join(blockers) if blockers else 'none'}.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    target = report.get("target_summary") or {}
    danger = report.get("danger_summary") or {}
    candidate = report.get("candidate_summary") or {}
    repair = report.get("repair_summary") or {}
    lines = [
        "# v28 Frozen Composite False-Conviction Repair Entry",
        "",
        "Research-only frozen forward validator; this does not place orders.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Base policy: `{freeze.get('base_policy')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Needed repairs: `{report.get('needed_repairs')}`",
        f"- Missed repairs available: `{report.get('missed_repairs_available')}`",
        f"- Candidate live ready: `{report.get('candidate_live_ready')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Summaries",
        "",
        "| slice | entries | settled | W/L | coverage | net c | avg net c |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, row in [
        ("target", target),
        ("danger_removed", danger),
        ("repair_rows", repair),
        ("candidate", candidate),
    ]:
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
    ])
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Repair Rows",
        "",
        "| market | source | side | won | net c | p | ask | edge | recross | abs d |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("repair_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
