"""Opposite-side availability diagnostic for the edge-phase FV gate.

Research-only; no live bot changes or orders.

The edge-phase adjusted-FV gate can improve P&L by skipping a paid price that
the adjusted FV no longer supports. The coverage question is whether those
skips are true abstentions or whether the market also offered a physically
coherent opposite-side entry. This probe tests that replacement idea on the
same frozen target-coverage surface without promoting it.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_boundary_recross_phase_fv_bakeoff import VARIANTS
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_rmt_forgetting_entry_bakeoff import estimate_entry_fee_cents
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable, observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw
from probe_v28_target_coverage_fv_overlay_validator import (
    STATE_JSON as TARGET_STATE_JSON,
    apply_policy,
    clamp_prob,
    load_json,
)
from probe_v28_raw_entry_coverage_valve import selected_base_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_edge_gate_opposite_side_diagnostic_latest.json"
OUT_MD = OUT_DIR / "v28_edge_gate_opposite_side_diagnostic_latest.md"

POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"
VARIANT = "edge_phase_shrink"
ADJUSTED_EDGE_FLOOR = -0.12
OPP_MIN_RAW_P = 0.50
OPP_MIN_RAW_EDGE = 0.00
OPP_MIN_ADJUSTED_EDGE = -0.02
MIN_SETTLED = 30
COVERAGE_MIN = 75.0


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out


def sorted_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: str(row.get("ts_wall") or ""))


def normalized(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if out.get("p_raw") is None:
        out["p_raw"] = out.get("p_side")
    if out.get("raw_edge_prob") is None:
        raw = as_float(out.get("p_raw"))
        ask = as_float(out.get("ask_prob"))
        if raw is not None and ask is not None:
            out["raw_edge_prob"] = raw - ask
    return out


def adjusted_probability(row: dict[str, Any]) -> float | None:
    fn = VARIANTS.get(VARIANT)
    if fn is None:
        return None
    try:
        return clamp_prob(float(fn(normalized(row))))
    except (KeyError, TypeError, ValueError):
        return None


def adjusted_edge(row: dict[str, Any]) -> float | None:
    p = adjusted_probability(row)
    ask = as_float(row.get("ask_prob"))
    if p is None or ask is None:
        return None
    return p - ask


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("market") or ""), str(row.get("side") or "")


def row_net_after_fee(row: dict[str, Any]) -> float | None:
    if row.get("side_won") is None:
        return None
    gross = row.get("gross_cents")
    if gross is None:
        ask = as_float(row.get("ask_cents"))
        if ask is None:
            return None
        gross = (100.0 if row.get("side_won") is True else 0.0) - ask
    return float(gross or 0.0) - estimate_entry_fee_cents(row)


def build_rows() -> tuple[list[dict[str, Any]], set[str], int]:
    target_state = load_json(TARGET_STATE_JSON)
    freeze_dt = parse_ts(target_state.get("source_coverage_freeze_ts") or target_state.get("freeze_ts"))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    rows = enrich_state(attach_regime_rows(observation_pool()))
    return rows, forward_markets, len(forward_markets)


def target_rows(forward_markets: set[str]) -> list[dict[str, Any]]:
    selected = apply_policy(selected_base_rows(), POLICY)
    return [row for row in selected if str(row.get("market") or "") in forward_markets]


def skipped_by_edge_gate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    skipped = []
    for row in rows:
        edge = adjusted_edge(row)
        if edge is None:
            continue
        if edge < ADJUSTED_EDGE_FLOOR:
            skipped.append({**row, "p_adjusted": adjusted_probability(row), "adjusted_edge": edge})
    return skipped


def opposite_candidates(all_rows: list[dict[str, Any]], skipped: dict[str, Any]) -> list[dict[str, Any]]:
    market, side = row_key(skipped)
    skip_ts = str(skipped.get("ts_wall") or "")
    out = []
    for row in sorted_rows(all_rows):
        if str(row.get("market") or "") != market:
            continue
        if str(row.get("side") or "") == side:
            continue
        if skip_ts and str(row.get("ts_wall") or "") < skip_ts:
            continue
        if not base_tradeable(row):
            continue
        raw = as_float(row.get("p_side"))
        ask = as_float(row.get("ask_prob"))
        adj_edge = adjusted_edge(row)
        if raw is None or ask is None or adj_edge is None:
            continue
        raw_edge = raw - ask
        if raw < OPP_MIN_RAW_P or raw_edge < OPP_MIN_RAW_EDGE or adj_edge < OPP_MIN_ADJUSTED_EDGE:
            continue
        out.append({
            **row,
            "raw_edge_prob": raw_edge,
            "p_adjusted": adjusted_probability(row),
            "adjusted_edge": adj_edge,
            "net_gross_cents_after_entry_fee": row_net_after_fee(row),
        })
    return out


def summarize_rows(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled)
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "net_cents": net,
        "avg_net_cents": net / len(settled) if settled else None,
    }


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "side": row.get("side"),
        "source": row.get("source"),
        "p_raw": row.get("p_side") or row.get("p_raw"),
        "p_adjusted": row.get("p_adjusted"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "adjusted_edge": row.get("adjusted_edge"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
    }


def build_report() -> dict[str, Any]:
    all_rows, forward_markets, denominator = build_rows()
    target = target_rows(forward_markets)
    skipped = skipped_by_edge_gate(target)
    replacements = []
    cases = []
    for skip in skipped:
        opps = opposite_candidates(all_rows, skip)
        chosen = opps[0] if opps else None
        if chosen is not None:
            replacements.append(chosen)
        cases.append({
            "skipped": compact_row(skip),
            "opposite_count": len(opps),
            "chosen_opposite": compact_row(chosen) if chosen else None,
        })
    skipped_markets = {str(row.get("market") or "") for row in skipped}
    kept = [row for row in target if str(row.get("market") or "") not in skipped_markets]
    kept_enriched = []
    for row in kept:
        kept_enriched.append({
            **row,
            "p_adjusted": adjusted_probability(row),
            "adjusted_edge": adjusted_edge(row),
            "net_gross_cents_after_entry_fee": row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row),
        })
    replaced_strategy = kept_enriched + replacements
    kept_summary = summarize_rows(kept_enriched, denominator)
    replacement_summary = summarize_rows(replacements, denominator)
    replaced_summary = summarize_rows(replaced_strategy, denominator)
    blockers = []
    if replaced_summary["settled"] < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if replaced_summary["coverage_pct"] is None or replaced_summary["coverage_pct"] < COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if replaced_summary["net_cents"] <= 0:
        blockers.append("net_not_positive")
    return {
        "diagnostic": "edge_gate_opposite_side_availability",
        "policy": POLICY,
        "variant": VARIANT,
        "adjusted_edge_floor": ADJUSTED_EDGE_FLOOR,
        "opposite_requirements": {
            "min_raw_p": OPP_MIN_RAW_P,
            "min_raw_edge": OPP_MIN_RAW_EDGE,
            "min_adjusted_edge": OPP_MIN_ADJUSTED_EDGE,
            "same_or_later_than_skipped_row": True,
        },
        "forward_denominator": denominator,
        "target_entries": len(target),
        "target_skipped": len(skipped),
        "skips_with_opposite": sum(1 for case in cases if case["chosen_opposite"] is not None),
        "kept_summary": kept_summary,
        "replacement_summary": replacement_summary,
        "replaced_strategy_summary": replaced_summary,
        "blockers": blockers,
        "cases": cases,
        "interpretation": interpretation(len(skipped), replacement_summary, replaced_summary, blockers),
        "requirements": [
            "diagnostic only; not promotion evidence",
            "opposite-side row must be same-or-later than skipped row",
            "opposite side must have executable ask, raw p >= 0.50, nonnegative raw edge, and adjusted edge >= -0.02",
            "needs at least 30 settled forward rows before any promotion discussion",
        ],
    }


def interpretation(
    skipped_count: int,
    replacement_summary: dict[str, Any],
    replaced_summary: dict[str, Any],
    blockers: list[str],
) -> list[str]:
    if skipped_count == 0:
        return ["No edge-gate skips exist yet on the frozen forward target surface."]
    notes = [
        f"{replacement_summary.get('entries')} of {skipped_count} edge-gate skips had a same-or-later opposite-side replacement under the fixed physics requirements.",
        f"Replacement-only net is {replacement_summary.get('net_cents')}c over {replacement_summary.get('settled')} settled rows.",
        f"Kept-plus-replacement coverage is {replaced_summary.get('coverage_pct')} with net {replaced_summary.get('net_cents')}c.",
    ]
    if blockers:
        notes.append(f"Still not promotable: {', '.join(blockers)}.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Edge-Gate Opposite-Side Diagnostic",
        "",
        "Research-only check: can an adjusted-FV skip become a coherent opposite-side trade instead of lost coverage?",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Variant: `{report.get('variant')}`",
        f"- Adjusted edge floor: `{report.get('adjusted_edge_floor')}`",
        f"- Target entries/skips/denominator: `{report.get('target_entries')}/{report.get('target_skipped')}/{report.get('forward_denominator')}`",
        f"- Skips with opposite replacement: `{report.get('skips_with_opposite')}`",
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
        ("kept_after_edge_gate", "kept_summary"),
        ("replacement_only", "replacement_summary"),
        ("kept_plus_replacement", "replaced_strategy_summary"),
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
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
