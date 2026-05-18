"""Boundary-turbulence opposite-side opportunity diagnostic.

Research-only; no live bot changes or orders.

Physics hypothesis:
    Near-strike high-recross rows are not simply "bad"; they are unresolved
    boundary states. A profitable broad-coverage strategy should not blindly
    skip them. Instead, it should ask whether the first side's thesis decays and
    a same-market opposite-side entry becomes physically coherent later.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_rmt_forgetting_entry_bakeoff import estimate_entry_fee_cents
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable, observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state
from probe_v28_target_coverage_fv_overlay_validator import (
    STATE_JSON as TARGET_STATE_JSON,
    apply_policy,
    load_json,
)
from probe_v28_raw_entry_coverage_valve import selected_base_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_reversal_opportunity_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_reversal_opportunity_latest.md"

POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"
RECROSS_FLOOR = 0.75
ABS_D_SIGMA_CEILING = 0.30
OPP_MIN_RAW_P = 0.50
OPP_MIN_RAW_EDGE = 0.00
MAX_REPLACEMENT_DELAY_SECONDS = 360.0


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def sorted_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: str(row.get("ts_wall") or ""))


def row_net_after_fee(row: dict[str, Any]) -> float | None:
    if row.get("side_won") is None:
        return None
    ask = as_float(row.get("ask_cents"))
    if ask is None:
        ask_prob = as_float(row.get("ask_prob"))
        ask = ask_prob * 100.0 if ask_prob is not None else None
    if ask is None:
        return None
    gross = (100.0 if row.get("side_won") is True else 0.0) - ask
    return gross - estimate_entry_fee_cents(row)


def is_boundary_turbulence(row: dict[str, Any]) -> bool:
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    return (
        recross is not None
        and abs_d is not None
        and recross >= RECROSS_FLOOR
        and abs_d <= ABS_D_SIGMA_CEILING
    )


def build_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    target_state = load_json(TARGET_STATE_JSON)
    freeze_dt = parse_ts(target_state.get("source_coverage_freeze_ts") or target_state.get("freeze_ts"))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    selected = apply_policy(selected_base_rows(), POLICY)
    target = [row for row in selected if str(row.get("market") or "") in forward_markets]
    return all_rows, target, len(forward_markets)


def seconds_between(a: Any, b: Any) -> float | None:
    da = parse_ts(a)
    db = parse_ts(b)
    if da is None or db is None:
        return None
    return (db - da).total_seconds()


def opposite_replacements(all_rows: list[dict[str, Any]], target: dict[str, Any]) -> list[dict[str, Any]]:
    market = str(target.get("market") or "")
    side = str(target.get("side") or "")
    target_ts = target.get("ts_wall")
    out = []
    for row in sorted_rows(all_rows):
        if str(row.get("market") or "") != market:
            continue
        if str(row.get("side") or "") == side:
            continue
        delay = seconds_between(target_ts, row.get("ts_wall"))
        if delay is None or delay < 0.0 or delay > MAX_REPLACEMENT_DELAY_SECONDS:
            continue
        if not base_tradeable(row):
            continue
        raw_p = as_float(row.get("p_side"))
        ask = as_float(row.get("ask_prob"))
        if raw_p is None or ask is None:
            continue
        raw_edge = raw_p - ask
        if raw_p < OPP_MIN_RAW_P or raw_edge < OPP_MIN_RAW_EDGE:
            continue
        out.append({
            **row,
            "replacement_delay_seconds": delay,
            "raw_edge_prob": raw_edge,
            "net_gross_cents_after_entry_fee": row_net_after_fee(row),
        })
    return out


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row) or 0.0) for row in settled)
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "net_cents": net,
        "avg_net_cents": net / len(settled) if settled else None,
    }


def compact(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "side": row.get("side"),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "replacement_delay_seconds": row.get("replacement_delay_seconds"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row),
    }


def build_report() -> dict[str, Any]:
    all_rows, target, denominator = build_rows()
    boundary = [row for row in target if is_boundary_turbulence(row)]
    replacement_rows = []
    cases = []
    for row in boundary:
        replacements = opposite_replacements(all_rows, row)
        chosen = replacements[0] if replacements else None
        if chosen is not None:
            replacement_rows.append(chosen)
        cases.append({
            "target": compact({**row, "net_gross_cents_after_entry_fee": row_net_after_fee(row)}),
            "replacement_count": len(replacements),
            "chosen_replacement": compact(chosen),
        })
    non_boundary = [row for row in target if not is_boundary_turbulence(row)]
    replaced_strategy = non_boundary + replacement_rows
    return {
        "diagnostic": "boundary_turbulence_opposite_reversal",
        "policy": POLICY,
        "requirements": {
            "boundary_recross_floor": RECROSS_FLOOR,
            "boundary_abs_d_sigma_ceiling": ABS_D_SIGMA_CEILING,
            "opposite_min_raw_p": OPP_MIN_RAW_P,
            "opposite_min_raw_edge": OPP_MIN_RAW_EDGE,
            "max_replacement_delay_seconds": MAX_REPLACEMENT_DELAY_SECONDS,
        },
        "forward_denominator": denominator,
        "target_summary": summarize(target, denominator),
        "boundary_summary": summarize(boundary, denominator),
        "replacement_summary": summarize(replacement_rows, denominator),
        "replaced_strategy_summary": summarize(replaced_strategy, denominator),
        "boundary_rows": len(boundary),
        "boundary_with_replacement": sum(1 for case in cases if case["chosen_replacement"] is not None),
        "cases": cases,
        "interpretation": interpretation(boundary, replacement_rows, replaced_strategy, denominator),
    }


def interpretation(
    boundary: list[dict[str, Any]],
    replacement_rows: list[dict[str, Any]],
    replaced_strategy: list[dict[str, Any]],
    denominator: int,
) -> list[str]:
    notes = [
        f"Boundary turbulence rows: {len(boundary)}; rows with same-market opposite replacement: {len(replacement_rows)}.",
        f"Kept non-boundary plus replacements would cover {100.0 * len(replaced_strategy) / denominator if denominator else None}% of the forward denominator.",
    ]
    if len(replacement_rows) < len(boundary):
        notes.append("Some boundary rows have no coherent opposite replacement, so this cannot be treated as a simple replacement rule yet.")
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
    lines = [
        "# v28 Boundary Reversal Opportunity",
        "",
        "Diagnostic-only: tests whether high-recross near-strike target rows have later opposite-side replacements.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Boundary rows/replacements: `{report.get('boundary_rows')}/{report.get('boundary_with_replacement')}`",
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
        ("boundary_only", "boundary_summary"),
        ("replacement_only", "replacement_summary"),
        ("non_boundary_plus_replacement", "replaced_strategy_summary"),
    ]:
        row = report.get(key) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend([
        "",
        "## Cases",
        "",
        "| market | target side | target won | target net | recross | abs d | replacements | chosen side | chosen won | chosen net | delay s |",
        "|---|---|---|---:|---:|---:|---:|---|---|---:|---:|",
    ])
    for case in report.get("cases") or []:
        target = case.get("target") or {}
        chosen = case.get("chosen_replacement") or {}
        lines.append(
            f"| {target.get('market')} | {target.get('side')} | {target.get('side_won')} | {fmt(target.get('net_cents'))} | "
            f"{fmt(target.get('recross_hazard_score'))} | {fmt(target.get('abs_d_sigma'))} | "
            f"{case.get('replacement_count')} | {chosen.get('side')} | {chosen.get('side_won')} | "
            f"{fmt(chosen.get('net_cents'))} | {fmt(chosen.get('replacement_delay_seconds'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
