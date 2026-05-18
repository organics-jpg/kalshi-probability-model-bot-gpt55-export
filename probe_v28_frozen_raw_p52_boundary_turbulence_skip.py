"""Frozen raw-p52 boundary-turbulence skip validator.

Research-only; no live bot changes or orders.

Physics hypothesis:
    The raw p52 entry surface is broad enough to hit the coverage target, but
    weak raw conviction near the strike with very high recross hazard is a
    boundary-turbulence state. In that state, the static FV estimate is less
    informative than the path's ability to recross before close.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_physics_penalty_candidates import build_report as build_raw_physics_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_raw_p52_boundary_turbulence_skip_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_raw_p52_boundary_turbulence_skip_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_raw_p52_boundary_turbulence_skip_latest.md"

BASE_POLICY = "v28_raw_p52_edge0"
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
        payload = load_json(STATE_JSON)
        if payload.get("freeze_ts_utc"):
            return payload
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "base_policy": BASE_POLICY,
        "candidate": "raw_p52_skip_weakraw_nearstrike_recross90",
        "raw_p_ceiling": 0.60,
        "abs_d_sigma_ceiling": 0.20,
        "recross_floor": 0.90,
        "rule": "Start from v28_raw_p52_edge0 and skip rows with p_raw < 0.60, abs_d_sigma <= 0.20, and recross_hazard_score >= 0.90.",
        "physics": "Near-strike weak-conviction rows with high recross hazard are boundary turbulence, not durable side information.",
        "source_artifact": "v28_raw_p52_forward_loss_cluster_latest.json",
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


def row_p(row: dict[str, Any]) -> float | None:
    return as_float(row.get("p_raw") if row.get("p_raw") is not None else row.get("p_eff"))


def should_skip(row: dict[str, Any], state: dict[str, Any]) -> bool:
    p = row_p(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    recross = as_float(row.get("recross_hazard_score"))
    if p is None or abs_d is None or recross is None:
        return False
    return (
        p < float(state["raw_p_ceiling"])
        and abs_d <= float(state["abs_d_sigma_ceiling"])
        and recross >= float(state["recross_floor"])
    )


def net_cents(rows: list[dict[str, Any]]) -> float:
    return sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in rows if row.get("side_won") is not None)


def brier(row: dict[str, Any]) -> float | None:
    p = row_p(row)
    won = row.get("side_won")
    if p is None or won is None:
        return None
    target = 1.0 if won is True else 0.0
    return (p - target) ** 2


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    briers = [value for row in settled if (value := brier(row)) is not None]
    coverage = 100.0 * len(rows) / denominator if denominator else None
    blockers = []
    if len(settled) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if net_cents(rows) <= 0.0:
        blockers.append("net_not_positive")
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": coverage,
        "net_cents": net_cents(rows),
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "blockers": blockers,
    }


def row_detail(row: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "side": row.get("side"),
        "source": row.get("source"),
        "p_raw": row_p(row),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob") if row.get("raw_edge_prob") is not None else row.get("eff_edge_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "reason": reason,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    timing = market_timing(parse_ts(state["freeze_ts_utc"]))
    forward_markets = timing["clean_forward_markets"]
    source = build_raw_physics_report()
    all_rows = source.get("rows") if isinstance(source.get("rows"), list) else []
    base = [
        row for row in all_rows
        if row.get("policy") == BASE_POLICY and str(row.get("market") or "") in forward_markets
    ]
    kept = []
    skipped = []
    for row in base:
        if should_skip(row, state):
            skipped.append(row_detail(row, "skip_boundary_turbulence"))
        else:
            kept.append(row)
    base_summary = summarize(base, len(forward_markets))
    candidate_summary = summarize(kept, len(forward_markets))
    return {
        "freeze": state,
        "future_denominator": len(forward_markets),
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "base": base_summary,
        "candidate": candidate_summary,
        "delta_net_cents": candidate_summary["net_cents"] - base_summary["net_cents"],
        "skipped_rows": skipped,
        "kept_pending_rows": [
            row_detail(row, "kept_pending")
            for row in kept
            if row.get("side_won") is None
        ],
        "candidate_live_ready": not candidate_summary["blockers"],
        "interpretation": [
            f"Frozen raw-p52 boundary-turbulence skip has {candidate_summary.get('entries')} entries versus {base_summary.get('entries')} base entries.",
            f"Delta versus base is {candidate_summary['net_cents'] - base_summary['net_cents']}c on future settled rows.",
            f"Skipped future rows so far: {len(skipped)}.",
        ],
    }


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
        "# v28 Frozen Raw-p52 Boundary-Turbulence Skip",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Base policy: `{freeze.get('base_policy')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Rule: `{freeze.get('rule')}`",
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
        "| row | entries | settled | W/L | coverage | net c | brier | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ])
    for name in ["base", "candidate"]:
        row = report.get(name) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_brier'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Skipped Rows",
        "",
        "| market | side | p raw | ask | edge | abs d | recross | won | net c | reason |",
        "|---|---|---:|---:|---:|---:|---:|---|---:|---|",
    ])
    for row in report.get("skipped_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{row.get('side_won')} | {fmt(row.get('net_cents'))} | {row.get('reason')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
