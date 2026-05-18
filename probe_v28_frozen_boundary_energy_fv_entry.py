"""Frozen forward validator for boundary-energy FV.

Research-only; no live bot changes or orders.

The rule tests whether apparent edge near the strike should be treated as
path energy that can evaporate before settlement. It changes only the fair
value probability used by the existing target-coverage entry policy, then
lets the unchanged policy decide whether the row still qualifies.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import row_net_after_fee
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import (
    STATE_JSON as TARGET_STATE_JSON,
    apply_policy,
    load_json,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_boundary_energy_fv_entry_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_boundary_energy_fv_entry_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_boundary_energy_fv_entry_latest.md"

POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"
MIN_SETTLED = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "base_policy": POLICY,
        "candidate": "boundary_energy_fv_entry",
        "rule": (
            "Shrink raw fair value toward 50 when recross hazard, long clock, "
            "near-strike geometry, and weak executable edge imply unresolved path energy. "
            "Apply the unchanged target-coverage policy to the adjusted FV."
        ),
        "physics": (
            "A close-to-strike BTC path with many minutes left can cross the boundary "
            "repeatedly. In that state, large apparent edge is often unstable trajectory "
            "energy, not terminal information; NO-side early boundary rows get the "
            "largest shrink because target-surface losses concentrate there."
        ),
        "source_artifact": "v28_target_coverage_price_friction_latest",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def raw_probability(row: dict[str, Any]) -> float | None:
    return as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))


def ask_prob(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is not None:
        return ask
    cents = as_float(row.get("ask_cents"))
    return None if cents is None else cents / 100.0


def raw_edge(row: dict[str, Any]) -> float | None:
    p = raw_probability(row)
    ask = ask_prob(row)
    return None if p is None or ask is None else p - ask


def seconds_to_close(row: dict[str, Any]) -> float | None:
    for key in ("seconds_to_close", "stc", "seconds_to_expiry"):
        value = as_float(row.get(key))
        if value is not None:
            return value
    return None


def heat(row: dict[str, Any]) -> float:
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma"))
    stc = seconds_to_close(row)
    edge = raw_edge(row)
    if abs_d is None or stc is None or edge is None:
        return 0.0
    near = max(0.0, min(1.0, (0.55 - abs_d) / 0.55))
    clock = max(0.0, min(1.0, (stc - 540.0) / 360.0))
    weak_edge = max(0.0, min(1.0, (0.09 - abs(edge)) / 0.09))
    side_mult = 1.25 if str(row.get("side") or "").lower() == "no" else 1.0
    cheap_mult = 1.15 if (ask_prob(row) or 1.0) < 0.55 else 1.0
    return max(0.0, min(1.0, recross * near * clock * weak_edge * side_mult * cheap_mult))


def boundary_energy_probability(row: dict[str, Any]) -> float:
    raw = raw_probability(row)
    if raw is None:
        raise ValueError("missing raw probability")
    shrink = 0.65 * heat(row)
    if raw >= 0.75 and (raw_edge(row) or 0.0) >= 0.04:
        shrink *= 0.35
    return clamp_prob(0.5 + (raw - 0.5) * (1.0 - shrink))


def adjusted_row(row: dict[str, Any]) -> dict[str, Any]:
    raw = raw_probability(row)
    ask = ask_prob(row)
    adj = boundary_energy_probability(row)
    return {
        **row,
        "p_raw_before_boundary_energy": raw,
        "p_side": adj,
        "p_eff": adj,
        "boundary_energy_heat": heat(row),
        "raw_edge_before_boundary_energy": None if raw is None or ask is None else raw - ask,
        "raw_edge_prob": None if ask is None else adj - ask,
    }


def future_market_set(freeze_ts: str) -> tuple[set[str], dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    timing = market_timing(freeze_dt)
    return set(timing["clean_forward_markets"]), timing


def target_freeze_market_set() -> tuple[set[str], dict[str, Any]]:
    target_state = load_json(TARGET_STATE_JSON)
    freeze_dt = parse_ts(target_state.get("source_coverage_freeze_ts") or target_state.get("freeze_ts"))
    timing = market_timing(freeze_dt)
    return set(timing["clean_forward_markets"]), timing


def selected_surfaces(markets: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = [row for row in selected_base_rows() if str(row.get("market") or "") in markets]
    base = apply_policy(rows, POLICY)
    adjusted = apply_policy([adjusted_row(row) for row in rows], POLICY)
    return base, adjusted


def side_won(row: dict[str, Any]) -> bool | None:
    return row.get("side_won") if isinstance(row.get("side_won"), bool) else None


def brier(p: float, won: bool) -> float:
    outcome = 1.0 if won else 0.0
    return (p - outcome) ** 2


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if side_won(row) is not None]
    wins = [row for row in settled if side_won(row) is True]
    losses = [row for row in settled if side_won(row) is False]
    nets = [float(row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row) or 0.0) for row in settled]
    briers = []
    heats = []
    for row in settled:
        p = raw_probability(row)
        if p is not None:
            briers.append(brier(clamp_prob(p), bool(side_won(row))))
        h = as_float(row.get("boundary_energy_heat"))
        if h is not None:
            heats.append(h)
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": len(wins),
        "losses": len(losses),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "net_cents": sum(nets),
        "avg_net_cents": sum(nets) / len(nets) if nets else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "avg_heat": sum(heats) / len(heats) if heats else None,
    }


def blockers(summary: dict[str, Any]) -> list[str]:
    out: list[str] = []
    settled = int(summary.get("settled") or 0)
    coverage = as_float(summary.get("coverage_pct"))
    net = as_float(summary.get("net_cents"))
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_MIN:
        out.append("coverage_too_low")
    if coverage is not None and coverage > COVERAGE_MAX:
        out.append("coverage_too_high")
    if net is None or net <= 0.0:
        out.append("net_not_positive")
    return out


def row_view(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row),
        "p_raw_before": row.get("p_raw_before_boundary_energy"),
        "p_adjusted": row.get("p_side"),
        "ask_prob": ask_prob(row),
        "raw_edge_before": row.get("raw_edge_before_boundary_energy"),
        "adjusted_edge": row.get("raw_edge_prob"),
        "heat": row.get("boundary_energy_heat"),
        "seconds_to_close": seconds_to_close(row),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    future_markets, timing = future_market_set(str(state["freeze_ts_utc"]))
    future_base, future_candidate = selected_surfaces(future_markets)
    diag_markets, _ = target_freeze_market_set()
    diag_base, diag_candidate = selected_surfaces(diag_markets)
    future_base_summary = summarize(future_base, len(future_markets))
    future_candidate_summary = summarize(future_candidate, len(future_markets))
    diag_base_summary = summarize(diag_base, len(diag_markets))
    diag_candidate_summary = summarize(diag_candidate, len(diag_markets))
    report_blockers = blockers(future_candidate_summary)
    return {
        "freeze": state,
        "excluded_in_progress_markets": sorted(timing.get("excluded_in_progress_markets") or []),
        "future_denominator": len(future_markets),
        "future_base_summary": future_base_summary,
        "future_candidate_summary": future_candidate_summary,
        "future_delta_net_cents": (
            None
            if future_candidate_summary.get("net_cents") is None or future_base_summary.get("net_cents") is None
            else float(future_candidate_summary["net_cents"]) - float(future_base_summary["net_cents"])
        ),
        "diagnostic_denominator": len(diag_markets),
        "diagnostic_base_summary": diag_base_summary,
        "diagnostic_candidate_summary": diag_candidate_summary,
        "diagnostic_delta_net_cents": float(diag_candidate_summary.get("net_cents") or 0.0) - float(diag_base_summary.get("net_cents") or 0.0),
        "blockers": report_blockers,
        "ready_for_consideration": not report_blockers,
        "future_candidate_rows": [row_view(row) for row in future_candidate[:80]],
        "diagnostic_candidate_rows": [row_view(row) for row in sorted(diag_candidate, key=lambda item: float(item.get("boundary_energy_heat") or 0.0), reverse=True)[:30]],
        "interpretation": [
            "Promotion evidence is only the post-freeze future summary; diagnostic rows are pre-freeze sanity checks.",
            f"Future candidate has {future_candidate_summary.get('entries')} entries, {future_candidate_summary.get('settled')} settled, coverage {future_candidate_summary.get('coverage_pct')}, net {future_candidate_summary.get('net_cents')}c.",
            f"Diagnostic delta versus the current target policy is {float(diag_candidate_summary.get('net_cents') or 0.0) - float(diag_base_summary.get('net_cents') or 0.0)}c.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def summary_row(name: str, row: dict[str, Any]) -> str:
    return (
        f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
        f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} | "
        f"{fmt(row.get('avg_brier'))} | {fmt(row.get('avg_heat'))} |"
    )


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen Boundary-Energy FV Entry",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Base policy: `{freeze.get('base_policy')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Ready for consideration: `{report.get('ready_for_consideration')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        f"- Future delta net cents: `{fmt(report.get('future_delta_net_cents'))}`",
        f"- Diagnostic delta net cents: `{fmt(report.get('diagnostic_delta_net_cents'))}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Summary",
        "",
        "| window | entries | settled | W/L | coverage | net c | avg c | avg brier | avg heat |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        summary_row("future_base", report.get("future_base_summary") or {}),
        summary_row("future_candidate", report.get("future_candidate_summary") or {}),
        summary_row("diagnostic_base", report.get("diagnostic_base_summary") or {}),
        summary_row("diagnostic_candidate", report.get("diagnostic_candidate_summary") or {}),
        "",
        "## Hot Diagnostic Rows",
        "",
        "| market | side | won | net c | raw p | adj p | ask | raw edge | adj edge | heat | stc | abs d | recross |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("diagnostic_candidate_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('won')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('p_raw_before'))} | {fmt(row.get('p_adjusted'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_before'))} | {fmt(row.get('adjusted_edge'))} | {fmt(row.get('heat'))} | "
            f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
