"""Danger-tag replacement diagnostic for the target-coverage entry surface.

Research-only; no live bot changes or orders.

Physics hypothesis:
    Two directional-loss shapes are physically different from ordinary target
    rows:
      1. paid-price fragility: expensive contracts where raw FV barely clears
         the executable ask;
      2. weak boundary turbulence: low raw probability, near-strike, high
         recross, early horizon rows.

Skipping them directly breaks the 75% coverage floor, so this diagnostic asks
whether the same market later offers a cleaner replacement row.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_rmt_forgetting_entry_bakeoff import estimate_entry_fee_cents
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable, observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state
from probe_v28_target_coverage_fv_overlay_validator import (
    STATE_JSON as TARGET_STATE_JSON,
    apply_policy,
    load_json,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_danger_tag_replacement_diagnostic_latest.json"
OUT_MD = OUT_DIR / "v28_danger_tag_replacement_diagnostic_latest.md"

POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"
MAX_REPLACEMENT_DELAY_SECONDS = 360.0
MIN_REPLACEMENT_RAW_P = 0.60
MIN_REPLACEMENT_RAW_EDGE = 0.00


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def seconds_between(a: Any, b: Any) -> float | None:
    da = parse_ts(a)
    db = parse_ts(b)
    if da is None or db is None:
        return None
    return (db - da).total_seconds()


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


def raw_edge(row: dict[str, Any]) -> float | None:
    edge = as_float(row.get("raw_edge_prob"))
    if edge is not None:
        return edge
    p = as_float(row.get("p_side"))
    ask = as_float(row.get("ask_prob"))
    return None if p is None or ask is None else p - ask


def danger_tags(row: dict[str, Any]) -> list[str]:
    p = as_float(row.get("p_side"))
    ask = as_float(row.get("ask_prob"))
    edge = raw_edge(row)
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    stc = as_float(row.get("seconds_to_close"))
    tags = []
    if ask is not None and edge is not None and ask >= 0.60 and edge < 0.02:
        tags.append("paid_price_fragile")
    if (
        p is not None
        and edge is not None
        and recross is not None
        and abs_d is not None
        and stc is not None
        and p < 0.60
        and edge >= 0.04
        and recross >= 0.75
        and abs_d <= 0.30
        and stc >= 780.0
    ):
        tags.append("weak_boundary_turbulence")
    return tags


def is_danger(row: dict[str, Any]) -> bool:
    return bool(danger_tags(row))


def build_surfaces() -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    target_state = load_json(TARGET_STATE_JSON)
    freeze_dt = parse_ts(target_state.get("source_coverage_freeze_ts") or target_state.get("freeze_ts"))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    all_rows = [row for row in all_rows if str(row.get("market") or "") in forward_markets]
    target = apply_policy(selected_base_rows(), POLICY)
    target = [row for row in target if str(row.get("market") or "") in forward_markets]
    return all_rows, target, len(forward_markets)


def replacement_candidates(all_rows: list[dict[str, Any]], skipped: dict[str, Any]) -> list[dict[str, Any]]:
    market = str(skipped.get("market") or "")
    skip_ts = skipped.get("ts_wall")
    skipped_side = str(skipped.get("side") or "")
    out = []
    for row in sorted(all_rows, key=lambda r: str(r.get("ts_wall") or "")):
        if str(row.get("market") or "") != market:
            continue
        delay = seconds_between(skip_ts, row.get("ts_wall"))
        if delay is None or delay < 0.0 or delay > MAX_REPLACEMENT_DELAY_SECONDS:
            continue
        if not base_tradeable(row):
            continue
        p = as_float(row.get("p_side"))
        edge = raw_edge(row)
        if p is None or edge is None:
            continue
        if p < MIN_REPLACEMENT_RAW_P or edge < MIN_REPLACEMENT_RAW_EDGE:
            continue
        if is_danger(row):
            continue
        out.append({
            **row,
            "replacement_delay_seconds": delay,
            "replacement_same_side": str(row.get("side") or "") == skipped_side,
            "raw_edge_prob": edge,
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
        "source": row.get("source"),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": raw_edge(row),
        "seconds_to_close": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row),
        "danger_tags": danger_tags(row),
        "replacement_delay_seconds": row.get("replacement_delay_seconds"),
        "replacement_same_side": row.get("replacement_same_side"),
    }


def build_report() -> dict[str, Any]:
    all_rows, target, denominator = build_surfaces()
    danger = [row for row in target if is_danger(row)]
    danger_markets = {str(row.get("market") or "") for row in danger}
    kept = [row for row in target if str(row.get("market") or "") not in danger_markets]
    replacements = []
    cases = []
    for row in danger:
        candidates = replacement_candidates(all_rows, row)
        chosen = candidates[0] if candidates else None
        if chosen is not None:
            replacements.append(chosen)
        cases.append({
            "skipped": compact({**row, "net_gross_cents_after_entry_fee": row_net_after_fee(row)}),
            "replacement_count": len(candidates),
            "chosen_replacement": compact(chosen),
        })
    candidate = kept + replacements
    return {
        "diagnostic": "danger_tag_same_market_replacement",
        "policy": POLICY,
        "requirements": {
            "max_replacement_delay_seconds": MAX_REPLACEMENT_DELAY_SECONDS,
            "min_replacement_raw_p": MIN_REPLACEMENT_RAW_P,
            "min_replacement_raw_edge": MIN_REPLACEMENT_RAW_EDGE,
            "replacement_must_not_have_danger_tag": True,
        },
        "forward_denominator": denominator,
        "target_summary": summarize(target, denominator),
        "danger_summary": summarize(danger, denominator),
        "kept_summary": summarize(kept, denominator),
        "replacement_summary": summarize(replacements, denominator),
        "candidate_summary": summarize(candidate, denominator),
        "danger_rows": len(danger),
        "danger_with_replacement": sum(1 for case in cases if case["chosen_replacement"] is not None),
        "cases": cases,
        "interpretation": interpretation(target, danger, replacements, candidate, denominator),
    }


def interpretation(
    target: list[dict[str, Any]],
    danger: list[dict[str, Any]],
    replacements: list[dict[str, Any]],
    candidate: list[dict[str, Any]],
    denominator: int,
) -> list[str]:
    coverage = 100.0 * len(candidate) / denominator if denominator else None
    notes = [
        f"Danger-tag rows: {len(danger)} of {len(target)} target entries.",
        f"Same-market clean replacements found for {len(replacements)} of {len(danger)} danger rows.",
        f"Kept-plus-replacement coverage would be {coverage}%.",
    ]
    if coverage is not None and coverage < 75.0:
        notes.append("This replacement concept does not currently preserve the target coverage floor.")
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
        "# v28 Danger-Tag Replacement Diagnostic",
        "",
        "Diagnostic-only: tests physical danger tags with same-market clean replacement.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Danger rows/replacements: `{report.get('danger_rows')}/{report.get('danger_with_replacement')}`",
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
        ("danger_only", "danger_summary"),
        ("kept_only", "kept_summary"),
        ("replacement_only", "replacement_summary"),
        ("kept_plus_replacement", "candidate_summary"),
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
        "| market | skipped side | tags | skipped won | skipped net | replacements | chosen side | same side | chosen won | chosen net | delay s |",
        "|---|---|---|---|---:|---:|---|---|---|---:|---:|",
    ])
    for case in report.get("cases") or []:
        skipped = case.get("skipped") or {}
        chosen = case.get("chosen_replacement") or {}
        lines.append(
            f"| {skipped.get('market')} | {skipped.get('side')} | {', '.join(skipped.get('danger_tags') or [])} | "
            f"{skipped.get('side_won')} | {fmt(skipped.get('net_cents'))} | {case.get('replacement_count')} | "
            f"{chosen.get('side')} | {chosen.get('replacement_same_side')} | {chosen.get('side_won')} | "
            f"{fmt(chosen.get('net_cents'))} | {fmt(chosen.get('replacement_delay_seconds'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
