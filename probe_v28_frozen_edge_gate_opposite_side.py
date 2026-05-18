"""Frozen edge-gate opposite-side replacement challenger.

Research-only; no live bot changes or orders.

Physics hypothesis:
    A rare edge-phase adjusted-FV skip can mean "the selected side is badly
    overpriced", not merely "do nothing". If the same market later offers an
    opposite side with coherent raw and adjusted edge, replacing the skipped
    row may preserve 75-80% coverage without paying the bad side.

This freezes the rule. All rows scored here are future-only after freeze.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_edge_gate_opposite_side_diagnostic import (
    ADJUSTED_EDGE_FLOOR,
    OPP_MIN_ADJUSTED_EDGE,
    OPP_MIN_RAW_EDGE,
    OPP_MIN_RAW_P,
    POLICY,
    VARIANT,
    adjusted_edge,
    adjusted_probability,
    compact_row,
    opposite_candidates,
    row_net_after_fee,
)
from probe_v28_exchange_result_enrichment import attach_exchange_results
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state
from probe_v28_target_coverage_fv_overlay_validator import apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_edge_gate_opposite_side_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_edge_gate_opposite_side_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_edge_gate_opposite_side_latest.md"

MIN_SETTLED = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0


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
        "base_entry_policy": POLICY,
        "fv_variant": VARIANT,
        "adjusted_edge_floor": ADJUSTED_EDGE_FLOOR,
        "opposite_min_raw_p": OPP_MIN_RAW_P,
        "opposite_min_raw_edge": OPP_MIN_RAW_EDGE,
        "opposite_min_adjusted_edge": OPP_MIN_ADJUSTED_EDGE,
        "rule": "If edge-phase adjusted-FV skips the target row, replace with the first same-or-later opposite row that clears fixed raw/FV edge requirements.",
        "physics": "A strongly overpriced selected side near a boundary can imply local side mispricing; opposite replacement is allowed only when later executable information agrees.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def should_skip(row: dict[str, Any], floor: float) -> bool:
    edge = adjusted_edge(row)
    return edge is not None and edge < floor


def enrich_candidate_row(row: dict[str, Any], reason: str) -> dict[str, Any]:
    net = row.get("net_gross_cents_after_entry_fee")
    if net is None:
        net = row_net_after_fee(row)
    return {
        **row,
        "p_adjusted": adjusted_probability(row),
        "adjusted_edge": adjusted_edge(row),
        "net_gross_cents_after_entry_fee": net,
        "candidate_reason": reason,
    }


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    coverage = 100.0 * len(rows) / denominator if denominator else None
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled)
    blockers = []
    if len(settled) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if net <= 0.0:
        blockers.append("net_not_positive")
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": coverage,
        "net_cents": net,
        "avg_net_cents": net / len(settled) if settled else None,
        "blockers": blockers,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    timing = market_timing(parse_ts(state["freeze_ts_utc"]))
    forward_markets = timing["clean_forward_markets"]
    denominator = len(forward_markets)
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    base_rows = apply_policy(selected_base_rows(), str(state.get("base_entry_policy") or POLICY))
    forward_base = attach_exchange_results([row for row in base_rows if str(row.get("market") or "") in forward_markets])
    kept: list[dict[str, Any]] = []
    replacements: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    cases: list[dict[str, Any]] = []
    floor = float(state["adjusted_edge_floor"])
    for row in forward_base:
        enriched = enrich_candidate_row(row, "kept_base")
        if not should_skip(row, floor):
            kept.append(enriched)
            continue
        skipped.append(enriched)
        opps = opposite_candidates(all_rows, enriched)
        chosen = enrich_candidate_row(opps[0], "opposite_replacement") if opps else None
        if chosen is not None:
            replacements.append(chosen)
        cases.append({
            "skipped": compact_row(enriched),
            "opposite_count": len(opps),
            "chosen_opposite": compact_row(chosen) if chosen else None,
        })
    candidate_rows = kept + replacements
    base_summary = summarize([enrich_candidate_row(row, "base") for row in forward_base], denominator)
    kept_summary = summarize(kept, denominator)
    replacement_summary = summarize(replacements, denominator)
    candidate_summary = summarize(candidate_rows, denominator)
    return {
        "freeze": state,
        "future_denominator": denominator,
        "base": base_summary,
        "kept_after_edge_gate": kept_summary,
        "replacement_only": replacement_summary,
        "candidate": candidate_summary,
        "delta_net_cents": candidate_summary["net_cents"] - base_summary["net_cents"],
        "target_skipped": len(skipped),
        "skips_with_opposite": len(replacements),
        "cases": cases,
        "pending_rows": [compact_row(row) for row in candidate_rows if row.get("side_won") is None],
        "interpretation": interpretation(base_summary, candidate_summary, len(skipped), len(replacements)),
    }


def interpretation(base: dict[str, Any], candidate: dict[str, Any], skipped: int, replacements: int) -> list[str]:
    return [
        f"Frozen edge-gate opposite replacement has {candidate.get('entries')} entries versus {base.get('entries')} base entries.",
        f"It has replaced {replacements} of {skipped} future edge-gate skips so far.",
        f"Net delta versus base is {candidate.get('net_cents') - base.get('net_cents')}c; promotion still requires >=30 settled rows and coverage inside the target band.",
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
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen Edge-Gate Opposite-Side Replacement",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Base entry policy: `{freeze.get('base_entry_policy')}`",
        f"- FV variant: `{freeze.get('fv_variant')}`",
        f"- Adjusted edge floor: `{fmt(freeze.get('adjusted_edge_floor'))}`",
        f"- Opposite requirements: raw p >= `{fmt(freeze.get('opposite_min_raw_p'))}`, raw edge >= `{fmt(freeze.get('opposite_min_raw_edge'))}`, adjusted edge >= `{fmt(freeze.get('opposite_min_adjusted_edge'))}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Summary",
        "",
        "| row | entries | settled | W/L | coverage | net c | avg net c | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ])
    for name in ["base", "kept_after_edge_gate", "replacement_only", "candidate"]:
        row = report.get(name) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Replacement Cases",
        "",
        "| market | skipped side | skipped adj edge | opposite side | opposite raw edge | opposite adj edge | opposite won | opposite net c |",
        "|---|---|---:|---|---:|---:|---|---:|",
    ])
    for case in report.get("cases") or []:
        skipped = case.get("skipped") or {}
        opp = case.get("chosen_opposite") or {}
        lines.append(
            f"| {skipped.get('market')} | {skipped.get('side')} | {fmt(skipped.get('adjusted_edge'))} | "
            f"{opp.get('side')} | {fmt(opp.get('raw_edge_prob'))} | {fmt(opp.get('adjusted_edge'))} | "
            f"{opp.get('side_won')} | {fmt(opp.get('net_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
