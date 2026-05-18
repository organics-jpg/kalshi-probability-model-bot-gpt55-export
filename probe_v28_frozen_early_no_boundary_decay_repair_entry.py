"""Frozen forward challenger for early NO boundary decay.

Research-only; no live bot changes or orders.

Frozen rule:
    Start from the target coverage policy. Skip rows where the model is buying
    an early NO-side thesis while BTC is still close enough to the strike that
    recross/path churn can erase the apparent edge:
      - side == no, seconds_to_close >= 720, p < 0.70, abs_d <= 0.45,
        recross_hazard_score >= 0.55
      - cheap near-boundary turbulence on either side: ask < 0.55, p < 0.62,
        abs_d <= 0.25, recross_hazard_score >= 0.75
    Restore the 75% coverage floor with clean repair rows ranked by calmer
    geometry: farther from strike first, then lower recross hazard.
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
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state
from probe_v28_target_coverage_fv_overlay_validator import apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_latest.md"

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
        "candidate": "skip_early_no_boundary_decay_repair_calm_geometry",
        "coverage_floor": COVERAGE_FLOOR,
        "danger_rule": "early NO boundary decay OR cheap near-boundary turbulence",
        "repair_rule": "clean repair rows ranked by farthest abs_d_sigma, then lowest recross hazard",
        "physics": (
            "Early NO positions near the strike are fragile because there is still enough clock "
            "for BTC to recross repeatedly; cheap contracts near the boundary are often cheap "
            "because the path is unresolved, not because they are underpriced."
        ),
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def probability(row: dict[str, Any]) -> float | None:
    return as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))


def seconds_to_close(row: dict[str, Any]) -> float | None:
    for key in ("seconds_to_close", "stc", "seconds_to_expiry"):
        value = as_float(row.get(key))
        if value is not None:
            return value
    return None


def recross_score(row: dict[str, Any]) -> float:
    recross = as_float(row.get("recross_hazard_score"))
    return recross if recross is not None else 999.0


def abs_distance(row: dict[str, Any]) -> float:
    abs_d = as_float(row.get("abs_d_sigma"))
    return abs_d if abs_d is not None else 0.0


def is_early_no_boundary_decay(row: dict[str, Any]) -> bool:
    p = probability(row)
    stc = seconds_to_close(row)
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    return (
        str(row.get("side") or "").lower() == "no"
        and p is not None
        and stc is not None
        and recross is not None
        and abs_d is not None
        and stc >= 720.0
        and p < 0.70
        and abs_d <= 0.45
        and recross >= 0.55
    )


def is_cheap_boundary_turbulence(row: dict[str, Any]) -> bool:
    p = probability(row)
    ask = as_float(row.get("ask_prob"))
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    return (
        p is not None
        and ask is not None
        and recross is not None
        and abs_d is not None
        and ask < 0.55
        and p < 0.62
        and abs_d <= 0.25
        and recross >= 0.75
    )


def is_danger(row: dict[str, Any]) -> bool:
    return is_early_no_boundary_decay(row) or is_cheap_boundary_turbulence(row)


def danger_reasons(row: dict[str, Any]) -> list[str]:
    reasons = []
    if is_early_no_boundary_decay(row):
        reasons.append("early_no_boundary_decay")
    if is_cheap_boundary_turbulence(row):
        reasons.append("cheap_boundary_turbulence")
    return reasons


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def clean_rows_by_market(rows: list[dict[str, Any]], markets: set[str]) -> list[dict[str, Any]]:
    candidates = []
    for row in rows:
        market = str(row.get("market") or "")
        if market not in markets or not is_clean_repair(row):
            continue
        candidates.append(
            {
                **row,
                "raw_edge_prob": raw_edge(row),
                "net_gross_cents_after_entry_fee": row_net_after_fee(row),
                "repair_score": abs_distance(row) - recross_score(row),
            }
        )
    candidates.sort(key=lambda row: (-abs_distance(row), recross_score(row), str(row.get("ts_wall") or "")))
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
    danger = [row for row in target if is_danger(row)]
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
        "seconds_to_close": seconds_to_close(row),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "danger_reasons": danger_reasons(row),
        "repair_score": row.get("repair_score"),
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
        "delta_vs_target_cents": float(candidate_summary.get("net_cents") or 0.0)
        - float(target_summary.get("net_cents") or 0.0),
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
        f"Early/path-decay danger rows removed: {len(built['danger'])}; repair rows added: {len(built['repairs'])}.",
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


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    target = report.get("target_summary") or {}
    candidate = report.get("candidate_summary") or {}
    danger = report.get("danger_summary") or {}
    repair = report.get("repair_summary") or {}
    lines = [
        "# v28 Frozen Early NO Boundary Decay Repair Entry",
        "",
        "Research-only frozen forward validator; this does not place orders.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Base policy: `{freeze.get('base_policy')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Live ready: `{report.get('candidate_live_ready')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Summaries",
            "",
            "| surface | entries | settled | W/L | coverage | net c | avg c |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for name, row in [
        ("target", target),
        ("danger_removed", danger),
        ("repair_added", repair),
        ("candidate", candidate),
    ]:
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend(
        [
            "",
            "## Danger Rows",
            "",
            "| market | side | p | ask | stc | abs d | recross | won | net c | reasons |",
            "|---|---|---:|---:|---:|---:|---:|---|---:|---|",
        ]
    )
    for row in report.get("danger_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_side'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('seconds_to_close'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{row.get('side_won')} | {fmt(row.get('net_cents'))} | "
            f"{', '.join(row.get('danger_reasons') or [])} |"
        )
    lines.extend(
        [
            "",
            "## Repair Rows",
            "",
            "| market | side | p | ask | abs d | recross | won | net c |",
            "|---|---|---:|---:|---:|---:|---|---:|",
        ]
    )
    for row in report.get("repair_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_side'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_report(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
