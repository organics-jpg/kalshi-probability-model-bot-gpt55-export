"""Book-dislocation-aware FV bridge for v28.

Research-only; no live bot changes and no orders.

Hypothesis:
    The book can be inefficient because some participants chase/vibe-trade, but
    the biggest FV/book gap is not automatically the best edge. Large ask spikes
    and deep discounts can be adverse-selection/chase states unless path escape
    is strong. Test a fixed dislocation-aware escape-energy penalty on top of
    the current lead continuous-recrossover forgetting bridge.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_book_dislocation_regime_attribution import (
    LEAD_SELECTOR,
    LEAD_VARIANT,
    annotate_ask_moves,
    classify_ask_move,
    classify_edge,
    classify_path,
)
from probe_v28_exchange_result_enrichment import attach_exchange_results
from probe_v28_false_conviction_fv_entry_bridge import (
    VARIANTS,
    adjusted_edge,
    as_float,
    escape_energy,
    load_json,
    select_entries,
)
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_book_dislocation_fv_bridge_state.json"
OUT_JSON = OUT_DIR / "v28_book_dislocation_fv_bridge_latest.json"
OUT_MD = OUT_DIR / "v28_book_dislocation_fv_bridge_latest.md"

REFERENCE_FREEZE_JSON = OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_state.json"
TARGET_COVERAGE = 0.80
MIN_SETTLED = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate": "book_dislocation_aware_escape_energy",
        "base": "first_eligible_top80_escape_energy+escape_edge6_or_p65_or_far_edge4+continuous_recross_forget",
        "rule": "same lead bridge, but rank the top 80% by escape energy with fixed penalties for ask_spike_ge8pp and deep discounts without strong escape",
        "physics": (
            "Gamblers can overpay/underpay during book motion, but large spikes and deep apparent discounts can be "
            "adverse selection. Keep modest dislocations unless path escape and recross geometry support the thesis."
        ),
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def dislocation_energy(row: dict[str, Any]) -> float:
    energy = escape_energy(row)
    edge = as_float(row.get("eff_edge_prob")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma")) or 0.0
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    ask_move = str(row.get("ask_move_bucket") or "")
    path = str(row.get("path_bucket") or "")

    penalty = 0.0
    if ask_move == "ask_spike_ge8pp":
        penalty += 0.055
    if edge >= 0.12 and not (abs_d >= 0.75 or path == "near_high_recross"):
        penalty += 0.050
    if edge >= 0.08 and recross >= 0.75 and abs_d < 0.45:
        penalty += 0.035
    if ask_move in {"ask_rise_4_8pp", "ask_stable"} and 0.0 <= edge < 0.08 and recross < 0.75:
        penalty -= 0.020
    return energy - penalty


def thin(rows: list[dict[str, Any]], denominator: int, mode: str) -> list[dict[str, Any]]:
    if not rows or denominator <= 0:
        return rows
    keep_count = max(0, min(len(rows), int(math.ceil(denominator * TARGET_COVERAGE))))
    if mode == "base_escape_energy":
        key_fn = escape_energy
    elif mode == "book_dislocation_escape_energy":
        key_fn = dislocation_energy
    else:
        raise ValueError(f"unknown mode {mode}")
    ranked = sorted(rows, key=lambda row: (-key_fn(row), str(row.get("ts_wall") or ""), str(row.get("market") or "")))
    keep = {str(row.get("market") or "") for row in ranked[:keep_count]}
    out = []
    for row in rows:
        if str(row.get("market") or "") in keep:
            out.append({**row, "escape_energy": escape_energy(row), "dislocation_energy": dislocation_energy(row)})
    return out


def base_rows(all_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = select_entries(
        all_rows,
        LEAD_SELECTOR,
        LEAD_VARIANT,
        VARIANTS[LEAD_VARIANT],
        "first_eligible",
    )
    annotated = []
    for row in selected:
        edge = adjusted_edge(row, float(row.get("p_eff")))
        enriched = {
            **row,
            "eff_edge_prob": edge,
            "edge_bucket": classify_edge({**row, "eff_edge_prob": edge}),
            "path_bucket": classify_path(row),
        }
        annotated.append(enriched)
    return annotate_ask_moves(all_rows, annotated)


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
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
        "avg_edge": avg(row.get("eff_edge_prob") for row in rows),
        "avg_escape_energy": avg(row.get("escape_energy") for row in rows),
        "avg_dislocation_energy": avg(row.get("dislocation_energy") for row in rows),
        "ask_spike_entries": sum(1 for row in rows if row.get("ask_move_bucket") == "ask_spike_ge8pp"),
        "deep_discount_entries": sum(1 for row in rows if row.get("edge_bucket") == "deep_discount_ge12pp"),
        "approved_entries": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "reconstructed_entries": sum(1 for row in rows if row.get("source") != "approved_entry"),
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
    total_source = (as_float(summary.get("approved_entries")) or 0.0) + (as_float(summary.get("reconstructed_entries")) or 0.0)
    recon_share = None if total_source <= 0 else (as_float(summary.get("reconstructed_entries")) or 0.0) / total_source
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_MIN:
        out.append("coverage_too_low")
    if coverage is not None and coverage > COVERAGE_MAX:
        out.append("coverage_too_high")
    if net <= 0:
        out.append("net_not_positive")
    if recon_share is None or recon_share > 0.35:
        out.append("reconstructed_share_gt_35pct")
    return out


def score_window(name: str, freeze_ts: str) -> dict[str, Any]:
    timing = market_timing(parse_ts(freeze_ts))
    future_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    all_rows = attach_exchange_results([row for row in all_rows if str(row.get("market") or "") in future_markets])
    selected = base_rows(all_rows)
    rows = []
    for mode in ["base_escape_energy", "book_dislocation_escape_energy"]:
        kept = thin(selected, len(future_markets), mode)
        summary = summarize(kept, len(future_markets))
        rows.append({"mode": mode, **summary, "blockers": blockers(summary), "rows": [compact(row) for row in kept]})
    rows.sort(key=lambda row: (bool(row.get("blockers")), as_float(row.get("net_cents")) or -999999.0), reverse=False)
    return {
        "window": name,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": len(future_markets),
        "ranked": rows,
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
        "dislocation_energy": row.get("dislocation_energy"),
        "edge_bucket": row.get("edge_bucket"),
        "ask_move_bucket": row.get("ask_move_bucket"),
        "path_bucket": row.get("path_bucket"),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    reference_state = load_json(REFERENCE_FREEZE_JSON)
    reference_freeze = reference_state.get("freeze_ts_utc") or state.get("freeze_ts_utc")
    windows = []
    if reference_freeze:
        windows.append(score_window("diagnostic_existing_false_conviction_freeze", str(reference_freeze)))
    if state.get("freeze_ts_utc"):
        windows.append(score_window("post_freeze_candidate", str(state["freeze_ts_utc"])))
    return {
        "state": state,
        "requirements": [
            "research-only, no live bot changes, no orders",
            "fixed dislocation penalties, no parameter search",
            "target roughly 80% market coverage",
            "promotion requires post-freeze sample, source quality, positive net, and coverage gates",
        ],
        "interpretation": interpretation(windows),
        "windows": windows,
    }


def interpretation(windows: list[dict[str, Any]]) -> list[str]:
    notes = []
    for window in windows:
        best = (window.get("ranked") or [{}])[0]
        notes.append(
            f"{window.get('window')}: best {best.get('mode')} entries/settled/coverage/net "
            f"{best.get('entries')}/{best.get('settled')}/{best.get('coverage_pct')}/{best.get('net_cents')}c; "
            f"ask_spikes {best.get('ask_spike_entries')}, deep_discounts {best.get('deep_discount_entries')}, blockers {best.get('blockers') or []}."
        )
    notes.append("Diagnostic results explain direction only; post-freeze rows decide whether the dislocation penalty survives.")
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
        "# v28 Book-Dislocation FV Bridge",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        f"- Candidate: `{(report.get('state') or {}).get('candidate')}`",
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
            "| rank | mode | entries | settled | W/L | coverage | net c | avg edge | avg escape | avg disloc | ask spikes | deep disc | approved/recon | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for idx, row in enumerate(window.get("ranked") or [], start=1):
            lines.append(
                f"| {idx} | `{row.get('mode')}` | {row.get('entries')} | {row.get('settled')} | "
                f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('avg_edge'))} | "
                f"{fmt(row.get('avg_escape_energy'))} | {fmt(row.get('avg_dislocation_energy'))} | "
                f"{row.get('ask_spike_entries')} | {row.get('deep_discount_entries')} | "
                f"{row.get('approved_entries')}/{row.get('reconstructed_entries')} | "
                f"{', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
