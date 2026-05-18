"""Frozen thin-edge high-recross mid-p entry gate for v28 target coverage.

Research-only; no live bot changes or orders.

Physics hypothesis:
When raw FV is only mid-confidence (0.60 <= p < 0.75), executable edge is
tiny, and recross hazard is high, the selected side is more likely a noisy
boundary state than durable information. This candidate preserves broad v28
coverage but skips that narrow turbulence pocket.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import DEFAULT_POLICY, apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_thin_recross_midp_entry_gate_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_thin_recross_midp_entry_gate_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_thin_recross_midp_entry_gate_latest.md"

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
        "base_entry_policy": DEFAULT_POLICY,
        "candidate": "skip_midp60_75_edge_lt2pp_recross_ge85",
        "min_mid_p": 0.60,
        "max_mid_p": 0.75,
        "edge_ceiling": 0.02,
        "recross_floor": 0.85,
        "hypothesis": "Thin-edge high-recross mid-p rows are boundary noise; skip them while preserving broad coverage.",
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


def should_skip(row: dict[str, Any], state: dict[str, Any]) -> bool:
    p = as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw")) or 0.0
    edge = as_float(row.get("raw_edge_prob"))
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    if edge is None:
        return False
    return (
        float(state["min_mid_p"]) <= p < float(state["max_mid_p"])
        and edge < float(state["edge_ceiling"])
        and recross >= float(state["recross_floor"])
    )


def net_cents(rows: list[dict[str, Any]]) -> float:
    return sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in rows if row.get("side_won") is not None)


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    blockers = []
    coverage = 100.0 * len(rows) / denominator if denominator else None
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
        "blockers": blockers,
    }


def row_detail(row: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "p_raw": row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "reason": reason,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    timing = market_timing(parse_ts(state["freeze_ts_utc"]))
    forward_markets = timing["clean_forward_markets"]
    base_rows = apply_policy(selected_base_rows(), str(state.get("base_entry_policy") or DEFAULT_POLICY))
    forward_base = [row for row in base_rows if str(row.get("market") or "") in forward_markets]
    kept = []
    skipped = []
    for row in forward_base:
        if should_skip(row, state):
            skipped.append(row_detail(row, "skip_thin_midp_high_recross"))
        else:
            kept.append(row)
    base_summary = summarize(forward_base, len(forward_markets))
    candidate_summary = summarize(kept, len(forward_markets))
    return {
        "freeze": state,
        "future_denominator": len(forward_markets),
        "base": base_summary,
        "candidate": candidate_summary,
        "delta_net_cents": candidate_summary["net_cents"] - base_summary["net_cents"],
        "skipped_rows": skipped,
        "pending_kept_rows": [
            row_detail(row, "kept_pending")
            for row in kept
            if row.get("side_won") is None
        ],
        "interpretation": interpretation(base_summary, candidate_summary, skipped),
    }


def interpretation(base: dict[str, Any], candidate: dict[str, Any], skipped: list[dict[str, Any]]) -> list[str]:
    return [
        f"Frozen thin-recross entry gate has {candidate.get('entries')} entries versus {base.get('entries')} base entries.",
        f"It has skipped {len(skipped)} future rows so far; promotion requires settled forward rows, not this setup snapshot.",
        "This is entry-policy evidence, separate from the conservative FV overlay.",
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
    lines = [
        "# v28 Frozen Thin-Recross Mid-P Entry Gate",
        "",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Candidate: `{(report.get('freeze') or {}).get('candidate')}`",
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
        "| row | entries | settled | W/L | coverage | net c | blockers |",
        "|---|---:|---:|---:|---:|---:|---|",
    ])
    for name in ["base", "candidate"]:
        row = report.get(name) or {}
        lines.append(
            f"| {name} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Skipped Rows",
        "",
        "| market | side | p raw | ask | edge | recross | won | net c | reason |",
        "|---|---|---:|---:|---:|---:|---|---:|---|",
    ])
    for row in report.get("skipped_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('recross_hazard_score'))} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {row.get('reason')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
