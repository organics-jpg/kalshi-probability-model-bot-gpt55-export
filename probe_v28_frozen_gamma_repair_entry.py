"""Frozen gamma/recross repair bridge for target-coverage v28.

Research-only; no live bot changes or orders.

Hypothesis:
Cheap near-boundary contracts can have recross/gamma optionality that the static
v28 terminal FV undervalues. Instead of broadly buying cheap sides, this frozen
bridge starts from the existing target-coverage policy and only uses the cheap
convex lane to fill missed markets up to the 75% coverage floor.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, as_float, row_net_after_fee, summarize
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_target_coverage_fv_overlay_validator import apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_gamma_repair_entry_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_gamma_repair_entry_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_gamma_repair_entry_latest.md"

BASE_POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"
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
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "base_policy": BASE_POLICY,
        "candidate": "target_plus_gamma_repair_to_75pct",
        "coverage_floor": COVERAGE_FLOOR,
        "repair_rule": "Fill missed markets with first cheap-convex row: 0.30 <= raw p <= 0.45, ask <= 40c, raw-book edge >= 3pp.",
        "physics": (
            "Near-boundary low-priced sides can be undercounted by static FV because the contract has gamma: "
            "small spot recrosses can move terminal probability and tradable exit value sharply."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def raw_edge(row: dict[str, Any]) -> float | None:
    p = as_float(row.get("p_side"))
    ask = as_float(row.get("ask_prob"))
    if p is None or ask is None:
        return None
    return p - ask


def is_gamma_repair(row: dict[str, Any]) -> bool:
    p = as_float(row.get("p_side"))
    ask_cents = as_float(row.get("ask_cents"))
    edge = raw_edge(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    recross = as_float(row.get("recross_hazard_score"))
    return (
        p is not None
        and ask_cents is not None
        and edge is not None
        and 0.30 <= p <= 0.45
        and ask_cents <= 40.0
        and edge >= 0.03
        and (abs_d is None or abs_d <= 0.65)
        and (recross is None or recross >= 0.20)
    )


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def first_gamma_repairs(rows: list[dict[str, Any]], allowed_markets: set[str]) -> list[dict[str, Any]]:
    picked: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        market = str(row.get("market") or "")
        if market not in allowed_markets or market in picked:
            continue
        if not is_gamma_repair(row):
            continue
        picked[market] = {
            **row,
            "net_gross_cents_after_entry_fee": row_net_after_fee(row),
            "raw_edge_prob": raw_edge(row),
        }
    return [picked[market] for market in sorted(picked)]


def future_surfaces(freeze_ts: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    freeze_dt = parse_ts(freeze_ts)
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    all_rows = [row for row in observation_pool() if str(row.get("market") or "") in forward_markets]
    target = apply_policy(selected_base_rows(), BASE_POLICY)
    target = [row for row in target if str(row.get("market") or "") in forward_markets]
    return all_rows, target, len(forward_markets)


def build_candidate(all_rows: list[dict[str, Any]], target: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    target_markets = {str(row.get("market") or "") for row in target}
    all_markets = {str(row.get("market") or "") for row in all_rows if row.get("market")}
    needed = max(0, ceil_entries_for_floor(denominator) - len(target))
    repairs = first_gamma_repairs(all_rows, all_markets - target_markets)[:needed]
    return {
        "target": target,
        "repairs": repairs,
        "candidate": target + repairs,
        "needed_repairs": needed,
        "available_repairs": len(first_gamma_repairs(all_rows, all_markets - target_markets)),
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "side": row.get("side"),
        "p_side": row.get("p_side"),
        "ask_cents": row.get("ask_cents"),
        "raw_edge_prob": raw_edge(row),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    all_rows, target, denominator = future_surfaces(str(state["freeze_ts_utc"]))
    built = build_candidate(all_rows, target, denominator)
    target_summary = summarize(target, denominator)
    candidate_summary = summarize(built["candidate"], denominator)
    repair_summary = summarize(built["repairs"], denominator)
    blockers = []
    if int(candidate_summary.get("settled") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if candidate_summary.get("coverage_pct") is None or float(candidate_summary["coverage_pct"]) < COVERAGE_FLOOR:
        blockers.append("coverage_too_low")
    if float(candidate_summary.get("net_cents") or 0.0) <= 0.0:
        blockers.append("net_not_positive")
    if built["repairs"] and sum(1 for row in built["repairs"] if row.get("source") == "approved_entry") == 0:
        blockers.append("repairs_all_simulated")
    return {
        "freeze": state,
        "future_denominator": denominator,
        "target_summary": target_summary,
        "repair_summary": repair_summary,
        "candidate_summary": candidate_summary,
        "needed_repairs": built["needed_repairs"],
        "available_repairs": built["available_repairs"],
        "delta_net_cents": float(candidate_summary.get("net_cents") or 0.0) - float(target_summary.get("net_cents") or 0.0),
        "blockers": blockers,
        "promotion_ready": not blockers,
        "repair_rows": [compact(row) for row in built["repairs"]],
        "interpretation": [
            f"Candidate has {candidate_summary.get('entries')} entries, coverage {candidate_summary.get('coverage_pct')}, net {candidate_summary.get('net_cents')}c.",
            f"Repairs used/needed/available: {len(built['repairs'])}/{built['needed_repairs']}/{built['available_repairs']}.",
            f"Delta versus target: {float(candidate_summary.get('net_cents') or 0.0) - float(target_summary.get('net_cents') or 0.0)}c.",
            f"Blockers: {', '.join(blockers) if blockers else 'none'}.",
        ],
    }


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
    target = report.get("target_summary") or {}
    repairs = report.get("repair_summary") or {}
    candidate = report.get("candidate_summary") or {}
    lines = [
        "# v28 Frozen Gamma Repair Entry",
        "",
        "Future-only target-coverage repair. No live orders.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Base policy: `{freeze.get('base_policy')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Promotion ready: `{report.get('promotion_ready')}`",
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
        "| window | entries | settled | W/L | coverage | net c |",
        "|---|---:|---:|---:|---:|---:|",
        f"| target | {target.get('entries')} | {target.get('settled')} | {target.get('wins')}/{target.get('losses')} | {fmt(target.get('coverage_pct'))} | {fmt(target.get('net_cents'))} |",
        f"| repairs | {repairs.get('entries')} | {repairs.get('settled')} | {repairs.get('wins')}/{repairs.get('losses')} | {fmt(repairs.get('coverage_pct'))} | {fmt(repairs.get('net_cents'))} |",
        f"| candidate | {candidate.get('entries')} | {candidate.get('settled')} | {candidate.get('wins')}/{candidate.get('losses')} | {fmt(candidate.get('coverage_pct'))} | {fmt(candidate.get('net_cents'))} |",
        "",
        "## Repair Rows",
        "",
    ])
    if not report.get("repair_rows"):
        lines.append("No future repair rows yet.")
    else:
        lines.append("| market | ts | side | source | p | ask | edge | abs d | recross | won | net c |")
        lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---|---:|")
        for row in report.get("repair_rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('ts_wall')} | {row.get('side')} | {row.get('source')} | "
                f"{fmt(row.get('p_side'))} | {fmt(row.get('ask_cents'))} | {fmt(row.get('raw_edge_prob'))} | "
                f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | {row.get('side_won')} | {fmt(row.get('net_cents'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
