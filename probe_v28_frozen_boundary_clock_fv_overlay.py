"""Frozen forward validator for the boundary-clock FV overlay.

Research-only; no live bot changes or orders.

Frozen rule:
    On the fixed target-coverage v28 entry surface, set FV probability to 0.50
    for boundary-clock composite hazard rows; leave all other raw v28
    probabilities unchanged.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_fv_overlay import raw_prob, shrink_prob
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import (
    DEFAULT_POLICY,
    apply_policy,
    as_float,
    clamp_prob,
    logloss,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_boundary_clock_fv_overlay_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_boundary_clock_fv_overlay_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_boundary_clock_fv_overlay_latest.md"

POLICY = DEFAULT_POLICY
VARIANT = "clock_shrink_0p00"
MIN_SETTLED = 30


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
        "entry_policy": POLICY,
        "variant": VARIANT,
        "rule": "if boundary_clock_composite then p=0.50 else p=raw",
        "physics": "Early boundary-clock hazard rows are unresolved path turbulence; FV confidence should collapse to coin-flip until the path resolves.",
        "source_artifact": "v28_boundary_clock_fv_overlay_latest.json",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def future_rows(freeze_ts: str) -> tuple[list[dict[str, Any]], int]:
    freeze_dt = parse_ts(freeze_ts)
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    target = apply_policy(selected_base_rows(), POLICY)
    rows = [row for row in target if str(row.get("market") or "") in forward_markets]
    return rows, len(forward_markets)


def adjusted_prob(row: dict[str, Any]) -> float:
    return shrink_prob(row, 0.0)


def score(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    scored = []
    adjusted = 0
    for row in settled:
        try:
            raw = raw_prob(row)
            p = adjusted_prob(row)
        except (TypeError, ValueError):
            continue
        if abs(p - raw) > 1e-12:
            adjusted += 1
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "raw": raw,
            "p": p,
            "outcome": outcome,
            "brier": (p - outcome) ** 2,
            "raw_brier": (raw - outcome) ** 2,
            "logloss": logloss(p, outcome),
            "raw_logloss": logloss(raw, outcome),
        })
    brier = avg([row["brier"] for row in scored])
    raw_brier = avg([row["raw_brier"] for row in scored])
    loss = avg([row["logloss"] for row in scored])
    raw_loss = avg([row["raw_logloss"] for row in scored])
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "adjusted_rows": adjusted,
        "net_cents": sum(float(as_float(row.get("net_gross_cents_after_entry_fee")) or 0.0) for row in settled),
        "brier_mean_delta": None if brier is None or raw_brier is None else brier - raw_brier,
        "logloss_mean_delta": None if loss is None or raw_loss is None else loss - raw_loss,
        "avg_brier": brier,
        "avg_logloss": loss,
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def compact(row: dict[str, Any]) -> dict[str, Any]:
    raw = raw_prob(row)
    p = adjusted_prob(row)
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "raw_p": raw,
        "adjusted_p": p,
        "delta_p": p - raw,
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "seconds_to_close": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    rows, denominator = future_rows(str(state["freeze_ts_utc"]))
    candidate = score(rows, denominator)
    blockers = []
    if int(candidate.get("settled") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if candidate.get("brier_mean_delta") is None or float(candidate["brier_mean_delta"]) >= 0.0:
        blockers.append("brier_not_better_than_raw")
    if candidate.get("logloss_mean_delta") is None or float(candidate["logloss_mean_delta"]) >= 0.0:
        blockers.append("logloss_not_better_than_raw")
    return {
        "freeze": state,
        "future_denominator": denominator,
        "candidate": candidate,
        "hazard_rows": [compact(row) for row in rows if row.get("side_won") is not None and abs(adjusted_prob(row) - raw_prob(row)) > 1e-12],
        "blockers": blockers,
        "candidate_live_ready": not blockers,
        "interpretation": interpretation(candidate, blockers),
    }


def interpretation(candidate: dict[str, Any], blockers: list[str]) -> list[str]:
    notes = [
        f"Future candidate has {candidate.get('entries')} entries, {candidate.get('settled')} settled rows, and adjusts {candidate.get('adjusted_rows')} settled rows.",
        f"Brier/logloss deltas versus raw are {candidate.get('brier_mean_delta')}/{candidate.get('logloss_mean_delta')}.",
    ]
    if blockers:
        notes.append(f"Promotion blockers: {', '.join(blockers)}.")
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
    freeze = report.get("freeze") or {}
    candidate = report.get("candidate") or {}
    lines = [
        "# v28 Frozen Boundary-Clock FV Overlay",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Variant: `{freeze.get('variant')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Entries/settled/adjusted: `{candidate.get('entries')}/{candidate.get('settled')}/{candidate.get('adjusted_rows')}`",
        f"- Brier/logloss delta: `{fmt(candidate.get('brier_mean_delta'))}/{fmt(candidate.get('logloss_mean_delta'))}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Adjusted Rows",
        "",
        "| market | source | side | won | net c | raw p | adj p | d p | ask | edge | stc | abs d | recross |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("hazard_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_p'))} | {fmt(row.get('adjusted_p'))} | "
            f"{fmt(row.get('delta_p'))} | {fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | "
            f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
