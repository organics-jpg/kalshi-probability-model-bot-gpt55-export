"""Pending sensitivity for the frozen conservative target-coverage FV.

Research-only; no live bot changes or orders.

The frozen conservative validator only scores rows after settlement. This probe
keeps the forward evidence honest while making pending rows visible, including
how much the conservative FV overlay would help or hurt Brier/logloss if the
selected side wins or loses.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_frozen_target_coverage_conservative_fv import STATE_JSON, clamp_prob
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_conservative_fv_variants import (
    logit125_p60_skip_mid_loss_zone,
    raw_probability,
)
from probe_v28_target_coverage_fv_overlay_validator import DEFAULT_POLICY, apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_frozen_target_coverage_conservative_pending_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_target_coverage_conservative_pending_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def delta_for_outcome(p_raw: float, p_variant: float, outcome: float) -> dict[str, float]:
    return {
        "brier_delta": (p_variant - outcome) ** 2 - (p_raw - outcome) ** 2,
        "logloss_delta": logloss(p_variant, outcome) - logloss(p_raw, outcome),
    }


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_ts = state.get("freeze_ts_utc")
    if not freeze_ts:
        return {
            "state_path": str(STATE_JSON),
            "pending_rows": [],
            "interpretation": ["Frozen conservative FV state does not exist yet."],
        }
    timing = market_timing(parse_ts(freeze_ts))
    forward_markets = timing["clean_forward_markets"]
    rows = apply_policy(
        selected_base_rows(),
        str(state.get("entry_policy") or DEFAULT_POLICY),
    )
    forward_rows = [row for row in rows if str(row.get("market") or "") in forward_markets]
    pending = []
    for row in forward_rows:
        if row.get("side_won") is not None:
            continue
        p_raw = clamp_prob(float(raw_probability(row)))
        p_variant = clamp_prob(float(logit125_p60_skip_mid_loss_zone(row)))
        pending.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "p_raw": p_raw,
            "p_variant": p_variant,
            "ask_prob": as_float(row.get("ask_prob")),
            "raw_edge_prob": as_float(row.get("raw_edge_prob")),
            "recross_hazard_score": as_float(row.get("recross_hazard_score")),
            "reason": row.get("coverage_valve_reason"),
            "if_selected_side_wins": delta_for_outcome(p_raw, p_variant, 1.0),
            "if_selected_side_loses": delta_for_outcome(p_raw, p_variant, 0.0),
        })
    return {
        "freeze": state,
        "future_denominator": len(forward_markets),
        "entries": len(forward_rows),
        "settled": sum(1 for row in forward_rows if row.get("side_won") is not None),
        "pending_count": len(pending),
        "pending_rows": pending,
        "interpretation": interpretation(pending),
    }


def interpretation(pending: list[dict[str, Any]]) -> list[str]:
    if not pending:
        return ["No unresolved frozen conservative target-coverage rows are pending."]
    adjusted = [row for row in pending if abs(float(row["p_variant"]) - float(row["p_raw"])) > 1e-9]
    notes = [
        f"{len(pending)} unresolved frozen conservative target-coverage row(s) are pending.",
        f"{len(adjusted)} pending row(s) are actually adjusted by the conservative FV overlay.",
    ]
    if adjusted:
        win_brier = sum(float((row["if_selected_side_wins"] or {}).get("brier_delta") or 0.0) for row in adjusted)
        lose_brier = sum(float((row["if_selected_side_loses"] or {}).get("brier_delta") or 0.0) for row in adjusted)
        notes.append(f"If all adjusted pending selected sides win, aggregate Brier delta is {win_brier}.")
        notes.append(f"If all adjusted pending selected sides lose, aggregate Brier delta is {lose_brier}.")
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
        "# v28 Frozen Conservative FV Pending Sensitivity",
        "",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Entry policy: `{(report.get('freeze') or {}).get('entry_policy')}`",
        f"- Future entries/settled/denominator: `{report.get('entries')}/{report.get('settled')}/{report.get('future_denominator')}`",
        f"- Pending rows: `{report.get('pending_count')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Pending Rows",
        "",
        "| market | side | p raw | p variant | ask | edge | recross | reason | if win brier/logloss d | if loss brier/logloss d |",
        "|---|---|---:|---:|---:|---:|---:|---|---:|---:|",
    ])
    for row in report.get("pending_rows") or []:
        win = row.get("if_selected_side_wins") or {}
        loss = row.get("if_selected_side_loses") or {}
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | {fmt(row.get('p_variant'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{row.get('reason')} | {fmt(win.get('brier_delta'))}/{fmt(win.get('logloss_delta'))} | "
            f"{fmt(loss.get('brier_delta'))}/{fmt(loss.get('logloss_delta'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
