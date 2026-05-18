"""Coverage-repair pool diagnostic for the target-coverage entry surface.

Research-only; no live bot changes or orders.

The current target surface cannot skip toxic rows without falling below the
75% market-coverage floor. This diagnostic tests a portfolio-style repair:
remove physically toxic target rows, then fill coverage from clean opportunities
in markets the target policy otherwise missed. This is intentionally separate
from same-market replacement, which already failed to improve PnL.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_danger_tag_replacement_diagnostic import danger_tags, row_net_after_fee
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
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
OUT_JSON = OUT_DIR / "v28_coverage_repair_pool_diagnostic_latest.json"
OUT_MD = OUT_DIR / "v28_coverage_repair_pool_diagnostic_latest.md"

POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"
COVERAGE_FLOOR = 75.0
REPAIR_MIN_RAW_P = 0.60
REPAIR_MIN_RAW_EDGE = 0.00
REPAIR_MAX_ASK = 0.82


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def raw_edge(row: dict[str, Any]) -> float | None:
    edge = as_float(row.get("raw_edge_prob"))
    if edge is not None:
        return edge
    p = as_float(row.get("p_side"))
    ask = as_float(row.get("ask_prob"))
    return None if p is None or ask is None else p - ask


def is_clean_repair(row: dict[str, Any]) -> bool:
    p = as_float(row.get("p_side"))
    edge = raw_edge(row)
    ask = as_float(row.get("ask_prob"))
    if p is None or edge is None or ask is None:
        return False
    return (
        base_tradeable(row)
        and p >= REPAIR_MIN_RAW_P
        and edge >= REPAIR_MIN_RAW_EDGE
        and ask <= REPAIR_MAX_ASK
        and not danger_tags(row)
    )


def build_surfaces() -> tuple[list[dict[str, Any]], list[dict[str, Any]], int, set[str]]:
    target_state = load_json(TARGET_STATE_JSON)
    freeze_dt = parse_ts(target_state.get("source_coverage_freeze_ts") or target_state.get("freeze_ts"))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    all_rows = [row for row in all_rows if str(row.get("market") or "") in forward_markets]
    target = apply_policy(selected_base_rows(), POLICY)
    target = [row for row in target if str(row.get("market") or "") in forward_markets]
    return all_rows, target, len(forward_markets), forward_markets


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


def first_clean_by_market(rows: list[dict[str, Any]], markets: set[str]) -> list[dict[str, Any]]:
    out = []
    seen = set()
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        market = str(row.get("market") or "")
        if market not in markets or market in seen:
            continue
        if is_clean_repair(row):
            out.append({
                **row,
                "raw_edge_prob": raw_edge(row),
                "net_gross_cents_after_entry_fee": row_net_after_fee(row),
            })
            seen.add(market)
    return out


def row_view(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "side": row.get("side"),
        "source": row.get("source"),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": raw_edge(row),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row),
        "danger_tags": danger_tags(row),
    }


def build_candidate() -> dict[str, Any]:
    all_rows, target, denominator, forward_markets = build_surfaces()
    target_markets = {str(row.get("market") or "") for row in target}
    danger = [row for row in target if danger_tags(row)]
    danger_markets = {str(row.get("market") or "") for row in danger}
    kept = [row for row in target if str(row.get("market") or "") not in danger_markets]
    kept_markets = {str(row.get("market") or "") for row in kept}

    needed_for_floor = max(0, int((COVERAGE_FLOOR * denominator + 99.999999) // 100) - len(kept))
    missed_markets = forward_markets - target_markets
    missed_repairs = first_clean_by_market(all_rows, missed_markets)
    chosen_repairs = missed_repairs[:needed_for_floor]
    if len(chosen_repairs) < needed_for_floor:
        extra_markets = forward_markets - kept_markets - {str(row.get("market") or "") for row in chosen_repairs}
        extras = first_clean_by_market(all_rows, extra_markets)
        chosen_keys = {str(row.get("market") or "") for row in chosen_repairs}
        for row in extras:
            if str(row.get("market") or "") in chosen_keys:
                continue
            chosen_repairs.append(row)
            chosen_keys.add(str(row.get("market") or ""))
            if len(chosen_repairs) >= needed_for_floor:
                break
    candidate = kept + chosen_repairs
    return {
        "all_rows": all_rows,
        "target": target,
        "danger": danger,
        "kept": kept,
        "missed_repairs": missed_repairs,
        "chosen_repairs": chosen_repairs,
        "candidate": candidate,
        "denominator": denominator,
        "needed_for_floor": needed_for_floor,
    }


def build_report() -> dict[str, Any]:
    built = build_candidate()
    target = built["target"]
    danger = built["danger"]
    kept = built["kept"]
    repairs = built["chosen_repairs"]
    candidate = built["candidate"]
    denominator = built["denominator"]
    return {
        "diagnostic": "coverage_repair_pool",
        "policy": POLICY,
        "requirements": {
            "coverage_floor": COVERAGE_FLOOR,
            "repair_min_raw_p": REPAIR_MIN_RAW_P,
            "repair_min_raw_edge": REPAIR_MIN_RAW_EDGE,
            "repair_max_ask": REPAIR_MAX_ASK,
            "repair_not_danger_tagged": True,
            "prefer_otherwise_missed_markets": True,
        },
        "forward_denominator": denominator,
        "needed_repairs_for_floor": built["needed_for_floor"],
        "available_missed_market_repairs": len(built["missed_repairs"]),
        "target_summary": summarize(target, denominator),
        "danger_summary": summarize(danger, denominator),
        "kept_summary": summarize(kept, denominator),
        "repair_summary": summarize(repairs, denominator),
        "candidate_summary": summarize(candidate, denominator),
        "danger_rows": [row_view(row) for row in danger],
        "chosen_repairs": [row_view(row) for row in repairs],
        "interpretation": interpretation(built),
    }


def interpretation(built: dict[str, Any]) -> list[str]:
    denominator = built["denominator"]
    candidate = built["candidate"]
    coverage = 100.0 * len(candidate) / denominator if denominator else None
    target_summary = summarize(built["target"], denominator)
    candidate_summary = summarize(candidate, denominator)
    notes = [
        f"Removing danger rows leaves {len(built['kept'])} entries; {built['needed_for_floor']} repairs are needed to restore the {COVERAGE_FLOOR}% floor.",
        f"Clean repairs available from otherwise missed markets: {len(built['missed_repairs'])}.",
        f"Candidate coverage {coverage}% with net {candidate_summary.get('net_cents')}c versus target net {target_summary.get('net_cents')}c.",
    ]
    if coverage is not None and coverage < COVERAGE_FLOOR:
        notes.append("Coverage repair fails the floor.")
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
        "# v28 Coverage Repair Pool Diagnostic",
        "",
        "Diagnostic-only: skip danger-tagged target rows and repair coverage from clean opportunities.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Needed repairs for floor: `{report.get('needed_repairs_for_floor')}`",
        f"- Available missed-market repairs: `{report.get('available_missed_market_repairs')}`",
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
        ("kept_after_danger_skip", "kept_summary"),
        ("repair_rows", "repair_summary"),
        ("kept_plus_repair", "candidate_summary"),
    ]:
        row = report.get(key) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend([
        "",
        "## Chosen Repairs",
        "",
        "| market | source | side | won | net c | p | ask | edge |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ])
    for row in report.get("chosen_repairs") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
