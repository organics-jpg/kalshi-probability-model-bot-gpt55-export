"""Source-quality audit for the v28 false-conviction FV bridge.

Research-only; no live bot changes and no orders.

The current lead bridge is strong diagnostically but mostly reconstructed. This
probe asks whether the same physics has support on actual v28-approved rows, or
whether it only exists in rejected-actionable/reconstructed observations.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_book_dislocation_regime_attribution import LEAD_SELECTOR, LEAD_VARIANT
from probe_v28_exchange_result_enrichment import attach_exchange_results
from probe_v28_false_conviction_fv_entry_bridge import (
    VARIANTS,
    adjusted_edge,
    as_float,
    escape_energy,
    load_json,
    select_entries,
    thin_by_escape_energy,
)
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_fv_bridge_source_quality_latest.json"
OUT_MD = OUT_DIR / "v28_fv_bridge_source_quality_latest.md"

BRIDGE_STATE_JSON = OUT_DIR / "v28_false_conviction_fv_entry_bridge_state.json"
REFERENCE_FREEZE_JSON = OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_state.json"
COVERAGE_TARGET = 0.80
COVERAGE_MIN = 75.0
MIN_SETTLED = 30


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled)
    approved = sum(1 for row in rows if row.get("source") == "approved_entry")
    reconstructed = len(rows) - approved
    recon_share = None if not rows else reconstructed / len(rows)
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "net_cents": net,
        "avg_net_cents": net / len(settled) if settled else None,
        "approved_entries": approved,
        "reconstructed_entries": reconstructed,
        "reconstructed_share": recon_share,
        "avg_edge": avg(row.get("eff_edge_prob") for row in rows),
        "avg_escape_energy": avg(row.get("escape_energy") for row in rows),
    }


def avg(values: Any) -> float | None:
    nums = [as_float(value) for value in values]
    nums = [value for value in nums if value is not None]
    return sum(nums) / len(nums) if nums else None


def blockers(summary: dict[str, Any]) -> list[str]:
    out = []
    settled = int(as_float(summary.get("settled")) or 0)
    coverage = as_float(summary.get("coverage_pct"))
    net = as_float(summary.get("net_cents")) or 0.0
    recon = as_float(summary.get("reconstructed_share"))
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_MIN:
        out.append("coverage_too_low")
    if net <= 0.0:
        out.append("net_not_positive")
    if recon is None or recon > 0.35:
        out.append("reconstructed_share_gt_35pct")
    return out


def annotate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        edge = adjusted_edge(row, float(row.get("p_eff")))
        out.append({**row, "eff_edge_prob": edge, "escape_energy": escape_energy({**row, "eff_edge_prob": edge})})
    return out


def lead_select(rows: list[dict[str, Any]], denominator: int) -> list[dict[str, Any]]:
    selected = select_entries(rows, LEAD_SELECTOR, LEAD_VARIANT, VARIANTS[LEAD_VARIANT], "first_eligible")
    selected = annotate(selected)
    return thin_by_escape_energy(selected, denominator, COVERAGE_TARGET)


def first_by_market(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    picked: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        market = str(row.get("market") or "")
        if market and market not in picked:
            picked[market] = row
    return [picked[key] for key in sorted(picked)]


def approved_preferred_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_market: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        market = str(row.get("market") or "")
        if market:
            by_market.setdefault(market, []).append(row)
    out = []
    for market_rows in by_market.values():
        ranked = sorted(
            market_rows,
            key=lambda row: (
                0 if row.get("source") == "approved_entry" else 1,
                str(row.get("ts_wall") or ""),
            ),
        )
        out.append(ranked[0])
    return out


def score_window(name: str, freeze_ts: str) -> dict[str, Any]:
    timing = market_timing(parse_ts(freeze_ts))
    future_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    all_rows = attach_exchange_results([row for row in all_rows if str(row.get("market") or "") in future_markets])
    denominator = len(future_markets)
    lead_all = lead_select(all_rows, denominator)
    lead_approved_only = lead_select([row for row in all_rows if row.get("source") == "approved_entry"], denominator)
    lead_reconstructed_only = lead_select([row for row in all_rows if row.get("source") != "approved_entry"], denominator)
    lead_first_market = first_by_market(lead_all)
    lead_approved_preferred = approved_preferred_rows(lead_all)
    scenarios = [
        ("lead_all_sources", lead_all),
        ("lead_first_market_only", lead_first_market),
        ("lead_approved_only", lead_approved_only),
        ("lead_reconstructed_only", lead_reconstructed_only),
        ("lead_approved_preferred", lead_approved_preferred),
    ]
    scored = []
    for scenario, rows in scenarios:
        summary = summarize(rows, denominator)
        scored.append({"scenario": scenario, **summary, "blockers": blockers(summary), "rows": [compact(row) for row in rows]})
    scored.sort(key=lambda row: (bool(row.get("blockers")), as_float(row.get("net_cents")) or -999999.0), reverse=False)
    return {
        "window": name,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "scenarios": scored,
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "p_eff": row.get("p_eff"),
        "ask_prob": row.get("ask_prob"),
        "eff_edge_prob": row.get("eff_edge_prob"),
        "escape_energy": row.get("escape_energy"),
    }


def build_report() -> dict[str, Any]:
    bridge_state = load_json(BRIDGE_STATE_JSON)
    reference_state = load_json(REFERENCE_FREEZE_JSON)
    reference_freeze = reference_state.get("freeze_ts_utc") or bridge_state.get("freeze_ts_utc")
    windows = []
    if reference_freeze:
        windows.append(score_window("diagnostic_existing_false_conviction_freeze", str(reference_freeze)))
    if bridge_state.get("freeze_ts_utc"):
        windows.append(score_window("post_freeze_candidate", str(bridge_state["freeze_ts_utc"])))
    return {
        "purpose": "Test whether the lead FV bridge has support in actual approved-entry source rows.",
        "lead": "first_eligible_top80_escape_energy+escape_edge6_or_p65_or_far_edge4+continuous_recross_forget",
        "requirements": [
            "research-only, no live bot changes, no orders",
            "source split between approved_entry and reconstructed rows",
            "coverage and sample gates are not waived",
        ],
        "interpretation": interpretation(windows),
        "windows": windows,
    }


def interpretation(windows: list[dict[str, Any]]) -> list[str]:
    notes = []
    for window in windows:
        scenarios = {row.get("scenario"): row for row in window.get("scenarios") or []}
        all_row = scenarios.get("lead_all_sources") or {}
        approved = scenarios.get("lead_approved_only") or {}
        notes.append(
            f"{window.get('window')}: all-source lead entries/settled/coverage/net/recon "
            f"{all_row.get('entries')}/{all_row.get('settled')}/{all_row.get('coverage_pct')}/{all_row.get('net_cents')}c/{all_row.get('reconstructed_share')}."
        )
        notes.append(
            f"{window.get('window')}: approved-only lead entries/settled/coverage/net "
            f"{approved.get('entries')}/{approved.get('settled')}/{approved.get('coverage_pct')}/{approved.get('net_cents')}c."
        )
    notes.append("If approved-only support stays thin, the bridge remains a research hypothesis, not a live candidate.")
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
        "# v28 FV Bridge Source-Quality Audit",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Lead: `{report.get('lead')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for window in report.get("windows") or []:
        lines.extend([
            "",
            f"## {window.get('window')}",
            "",
            f"- Future denominator: `{window.get('future_denominator')}`",
            "",
            "| scenario | entries | settled | W/L | coverage | net c | recon share | approved/recon | avg edge | avg escape | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for row in window.get("scenarios") or []:
            lines.append(
                f"| `{row.get('scenario')}` | {row.get('entries')} | {row.get('settled')} | "
                f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('reconstructed_share'))} | "
                f"{row.get('approved_entries')}/{row.get('reconstructed_entries')} | "
                f"{fmt(row.get('avg_edge'))} | {fmt(row.get('avg_escape_energy'))} | "
                f"{', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
