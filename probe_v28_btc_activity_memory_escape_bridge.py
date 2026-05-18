"""BTC activity-memory escape bridge for v28.

Research-only; no live bot changes and no orders.

User hypothesis:
    Recent BTC activity over roughly the last four hours should tell us how
    much to trust the current FV. This probe uses live/shadow-available path
    fields as a conservative proxy when fresh raw BTC candles are not available:
    sigma_t_dollars, recross hazard, and boundary nearness.

It does not change probability math directly. It only compares whether a fixed
phi-weighted 4h activity memory improves the escape-energy thinning used by the
current lead FV bridge.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
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
)
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_btc_activity_memory_escape_bridge_state.json"
OUT_JSON = OUT_DIR / "v28_btc_activity_memory_escape_bridge_latest.json"
OUT_MD = OUT_DIR / "v28_btc_activity_memory_escape_bridge_latest.md"

REFERENCE_FREEZE_JSON = OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_state.json"
BRIDGE_STATE_JSON = OUT_DIR / "v28_false_conviction_fv_entry_bridge_state.json"
TARGET_COVERAGE = 0.80
MIN_SETTLED = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV = 1.0 / PHI
PHI_INV2 = PHI_INV * PHI_INV


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
        "candidate": "btc_activity_memory_escape_bridge",
        "base": "first_eligible_top80_escape_energy+escape_edge6_or_p65_or_far_edge4+continuous_recross_forget",
        "memory_window_hours": 4,
        "physics": (
            "If the last few hours are high-volatility/high-recross boundary churn, current FV conviction should "
            "need stronger escape energy. This uses fixed phi weights and does not fit parameters."
        ),
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def near_boundary(row: dict[str, Any]) -> float:
    distance = as_float(row.get("abs_d_sigma"))
    if distance is None:
        return 0.0
    return max(0.0, min(1.0, (0.85 - distance) / 0.85))


def sigma_pressure(row: dict[str, Any]) -> float:
    sigma = as_float(row.get("sigma_t_dollars"))
    if sigma is None:
        return 0.0
    return max(0.0, min(1.0, sigma / 220.0))


def row_pressure(row: dict[str, Any]) -> float:
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    return max(0.0, min(1.0, PHI_INV * sigma_pressure(row) + PHI_INV2 * recross * near_boundary(row)))


def attach_activity_memory(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: str(row.get("ts_wall") or ""))
    out = []
    history: list[dict[str, Any]] = []
    for row in ordered:
        ts = parse_ts(str(row.get("ts_wall") or ""))
        cutoff = ts - timedelta(hours=4)
        recent = [past for past in history if parse_ts(str(past.get("ts_wall") or "")) >= cutoff]
        if recent:
            weights = [PHI_INV ** (idx + 1) for idx, _ in enumerate(reversed(recent))]
            pressures = [row_pressure(past) for past in reversed(recent)]
            denom = sum(weights)
            activity = sum(w * p for w, p in zip(weights, pressures)) / denom if denom else 0.0
            recross_memory = sum(w * (as_float(p.get("recross_hazard_score")) or 0.0) for w, p in zip(weights, reversed(recent))) / denom if denom else 0.0
            sigma_memory = sum(w * sigma_pressure(p) for w, p in zip(weights, reversed(recent))) / denom if denom else 0.0
        else:
            activity = 0.0
            recross_memory = 0.0
            sigma_memory = 0.0
        out.append({**row, "btc_activity_memory": activity, "recross_memory_4h": recross_memory, "sigma_memory_4h": sigma_memory})
        history.append(row)
    return out


def activity_energy(row: dict[str, Any]) -> float:
    activity = as_float(row.get("btc_activity_memory")) or 0.0
    current_pressure = row_pressure(row)
    # Fixed, gentle penalty. Strong current escape can still dominate; the
    # memory only makes marginal rows compete harder for the 80% selection.
    return escape_energy(row) - PHI_INV2 * 0.10 * activity - PHI_INV2 * 0.05 * current_pressure


def lead_rows(all_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = select_entries(all_rows, LEAD_SELECTOR, LEAD_VARIANT, VARIANTS[LEAD_VARIANT], "first_eligible")
    out = []
    for row in attach_activity_memory(selected):
        edge = adjusted_edge(row, float(row.get("p_eff")))
        out.append({**row, "eff_edge_prob": edge, "escape_energy": escape_energy({**row, "eff_edge_prob": edge}), "activity_energy": activity_energy({**row, "eff_edge_prob": edge})})
    return out


def thin(rows: list[dict[str, Any]], denominator: int, mode: str) -> list[dict[str, Any]]:
    if not rows or denominator <= 0:
        return rows
    keep_count = max(0, min(len(rows), int(math.ceil(denominator * TARGET_COVERAGE))))
    if mode == "base_escape_energy":
        key_fn = lambda row: as_float(row.get("escape_energy")) or -999.0
    elif mode == "activity_memory_escape_energy":
        key_fn = lambda row: as_float(row.get("activity_energy")) or -999.0
    else:
        raise ValueError(f"unknown mode {mode}")
    ranked = sorted(rows, key=lambda row: (-key_fn(row), str(row.get("ts_wall") or ""), str(row.get("market") or "")))
    keep = {str(row.get("market") or "") for row in ranked[:keep_count]}
    return [row for row in rows if str(row.get("market") or "") in keep]


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled)
    approved = sum(1 for row in rows if row.get("source") == "approved_entry")
    recon = len(rows) - approved
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "net_cents": net,
        "avg_net_cents": net / len(settled) if settled else None,
        "avg_escape_energy": avg(row.get("escape_energy") for row in rows),
        "avg_activity_energy": avg(row.get("activity_energy") for row in rows),
        "avg_activity_memory": avg(row.get("btc_activity_memory") for row in rows),
        "avg_recross_memory": avg(row.get("recross_memory_4h") for row in rows),
        "avg_sigma_memory": avg(row.get("sigma_memory_4h") for row in rows),
        "approved_entries": approved,
        "reconstructed_entries": recon,
        "reconstructed_share": None if not rows else recon / len(rows),
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
    if coverage is not None and coverage > COVERAGE_MAX:
        out.append("coverage_too_high")
    if net <= 0.0:
        out.append("net_not_positive")
    if recon is None or recon > 0.35:
        out.append("reconstructed_share_gt_35pct")
    return out


def score_window(name: str, freeze_ts: str) -> dict[str, Any]:
    timing = market_timing(parse_ts(freeze_ts))
    future_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    all_rows = attach_exchange_results([row for row in all_rows if str(row.get("market") or "") in future_markets])
    rows = lead_rows(all_rows)
    ranked = []
    for mode in ["base_escape_energy", "activity_memory_escape_energy"]:
        kept = thin(rows, len(future_markets), mode)
        summary = summarize(kept, len(future_markets))
        ranked.append({"mode": mode, **summary, "blockers": blockers(summary), "rows": [compact(row) for row in kept]})
    ranked.sort(key=lambda row: (bool(row.get("blockers")), as_float(row.get("net_cents")) or -999999.0), reverse=False)
    return {"window": name, "freeze_ts_utc": freeze_ts, "future_denominator": len(future_markets), "ranked": ranked}


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
        "activity_energy": row.get("activity_energy"),
        "btc_activity_memory": row.get("btc_activity_memory"),
        "recross_memory_4h": row.get("recross_memory_4h"),
        "sigma_memory_4h": row.get("sigma_memory_4h"),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    bridge_state = load_json(BRIDGE_STATE_JSON)
    reference_state = load_json(REFERENCE_FREEZE_JSON)
    reference_freeze = reference_state.get("freeze_ts_utc") or bridge_state.get("freeze_ts_utc") or state.get("freeze_ts_utc")
    windows = []
    if reference_freeze:
        windows.append(score_window("diagnostic_existing_false_conviction_freeze", str(reference_freeze)))
    if state.get("freeze_ts_utc"):
        windows.append(score_window("post_freeze_candidate", str(state["freeze_ts_utc"])))
    return {
        "state": state,
        "requirements": [
            "research-only, no live bot changes, no orders",
            "fixed phi-weighted 4h activity proxy using live/shadow available fields",
            "target roughly 80% coverage",
            "promotion requires post-freeze sample and source-quality gates",
        ],
        "interpretation": interpretation(windows),
        "windows": windows,
    }


def interpretation(windows: list[dict[str, Any]]) -> list[str]:
    notes = []
    for window in windows:
        ranked = window.get("ranked") or []
        best = ranked[0] if ranked else {}
        base = next((row for row in ranked if row.get("mode") == "base_escape_energy"), {})
        activity = next((row for row in ranked if row.get("mode") == "activity_memory_escape_energy"), {})
        notes.append(
            f"{window.get('window')}: best {best.get('mode')} entries/settled/coverage/net "
            f"{best.get('entries')}/{best.get('settled')}/{best.get('coverage_pct')}/{best.get('net_cents')}c; blockers {best.get('blockers') or []}."
        )
        if base and activity:
            notes.append(
                f"{window.get('window')}: activity memory delta vs base net "
                f"{(as_float(activity.get('net_cents')) or 0.0) - (as_float(base.get('net_cents')) or 0.0)}c."
            )
    notes.append("If activity-memory ranking fails to beat base escape-energy, keep the simpler lead.")
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
        "# v28 BTC Activity-Memory Escape Bridge",
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
            "| rank | mode | entries | settled | W/L | coverage | net c | avg escape | avg activity energy | avg activity memory | avg recross mem | avg sigma mem | approved/recon | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for idx, row in enumerate(window.get("ranked") or [], start=1):
            lines.append(
                f"| {idx} | `{row.get('mode')}` | {row.get('entries')} | {row.get('settled')} | "
                f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('avg_escape_energy'))} | "
                f"{fmt(row.get('avg_activity_energy'))} | {fmt(row.get('avg_activity_memory'))} | "
                f"{fmt(row.get('avg_recross_memory'))} | {fmt(row.get('avg_sigma_memory'))} | "
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
