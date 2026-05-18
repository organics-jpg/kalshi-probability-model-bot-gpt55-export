"""Frozen edge-phase adjusted-FV entry gate for v28 target coverage.

Research-only; no live bot changes or orders.

Physics hypothesis:
    The target-coverage entry surface can keep broad participation, but should
    refuse the rare row where phase-aware FV says the executable ask is far
    above fair value. This freezes one diagnostic rule:

        keep if edge_phase_shrink_probability - ask >= -12pp

The wide negative allowance is intentional. It is a safety valve for extreme
FV/ask disagreement, not a tight selectivity filter.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_recross_phase_fv_bakeoff import edge_phase_shrink
from probe_v28_exchange_result_enrichment import attach_exchange_results
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import DEFAULT_POLICY, apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_edge_phase_edge_gate_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_edge_phase_edge_gate_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_edge_phase_edge_gate_latest.md"

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
        "base_entry_policy": DEFAULT_POLICY,
        "fv_variant": "edge_phase_shrink",
        "adjusted_edge_floor": -0.12,
        "rule": "keep target-coverage row only if edge_phase_shrink_probability - ask_prob >= -0.12",
        "physics": "A wide negative adjusted-FV edge is a bad paid-price state; this is a rare safety valve, not a tight selectivity filter.",
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


def normalized(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if out.get("p_side") is None and out.get("p_raw") is not None:
        out["p_side"] = out.get("p_raw")
    return out


def adjusted_edge(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is None:
        return None
    try:
        p = float(edge_phase_shrink(normalized(row)))
    except (KeyError, TypeError, ValueError):
        return None
    return p - ask


def should_skip(row: dict[str, Any], state: dict[str, Any]) -> bool:
    edge = adjusted_edge(row)
    floor = as_float(state.get("adjusted_edge_floor"))
    if edge is None or floor is None:
        return False
    return edge < floor


def net_cents(rows: list[dict[str, Any]]) -> float:
    return sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in rows if row.get("side_won") is not None)


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    coverage = 100.0 * len(rows) / denominator if denominator else None
    net = net_cents(rows)
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
        "blockers": blockers,
    }


def row_detail(row: dict[str, Any], reason: str) -> dict[str, Any]:
    edge = adjusted_edge(row)
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "p_raw": row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"),
        "p_adjusted": None if edge is None or row.get("ask_prob") is None else edge + float(row.get("ask_prob")),
        "ask_prob": row.get("ask_prob"),
        "adjusted_edge": edge,
        "raw_edge_prob": row.get("raw_edge_prob"),
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
    base_rows = apply_policy(selected_base_rows(), str(state.get("base_entry_policy") or DEFAULT_POLICY))
    forward_base = attach_exchange_results([row for row in base_rows if str(row.get("market") or "") in forward_markets])
    kept = []
    skipped = []
    for row in forward_base:
        if should_skip(row, state):
            skipped.append(row)
        else:
            kept.append(row)
    base = summarize(forward_base, len(forward_markets))
    candidate = summarize(kept, len(forward_markets))
    return {
        "freeze": state,
        "future_denominator": len(forward_markets),
        "base": base,
        "candidate": candidate,
        "delta_net_cents": candidate["net_cents"] - base["net_cents"],
        "skipped_rows": [row_detail(row, "skip_adjusted_edge_below_floor") for row in skipped],
        "pending_kept_rows": [row_detail(row, "kept_pending") for row in kept if row.get("side_won") is None],
        "interpretation": [
            f"Frozen edge-phase edge gate has {candidate.get('entries')} entries versus {base.get('entries')} base entries.",
            f"It has skipped {len(skipped)} future rows so far; promotion requires forward sample size and target coverage.",
            "This is an adjusted-FV paid-price gate derived from the edge-phase shrink model.",
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
    lines = [
        "# v28 Frozen Edge-Phase Edge Gate",
        "",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Base entry policy: `{(report.get('freeze') or {}).get('base_entry_policy')}`",
        f"- FV variant: `{(report.get('freeze') or {}).get('fv_variant')}`",
        f"- Adjusted edge floor: `{fmt((report.get('freeze') or {}).get('adjusted_edge_floor'))}`",
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
        "| market | side | p raw | p adj | ask | adj edge | raw edge | abs d | recross | won | net c | reason |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ])
    for row in report.get("skipped_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | {fmt(row.get('p_adjusted'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('adjusted_edge'))} | {fmt(row.get('raw_edge_prob'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {row.get('reason')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
