"""Frozen forward validator for a hybrid confidence-shrink FV overlay.

Research-only; no live bot changes or orders.

Entry selection is fixed to raw v28 p50 edge0. This probe only changes the
assigned probability. The candidate uses the latest physics interpretation:
- use noise_shrink_light as the default gentle calibration shrink;
- avoid shrinking already-weak near-50 signals in heavy-noise states;
- use phi half/quarter shrink when high recross or near-strike geometry says
  raw probability magnitude is likely too hot.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_memory_fv_candidates import (
    as_float,
    avg,
    clamp_prob,
    logloss,
    raw_edge,
    selected_base_rows,
    validation_blockers,
)
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_noise_floor_shrinkage_candidates import p_light
from probe_v28_phi_forgetting_fv_candidates import phi_penalty_count, phi_retention
from probe_v28_state_aware_fv_candidates import p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_hybrid_confidence_shrink_fv_state.json"
OUT_JSON = OUT_DIR / "v28_hybrid_confidence_shrink_fv_latest.json"
OUT_MD = OUT_DIR / "v28_hybrid_confidence_shrink_fv_latest.md"
MIN_SETTLED = 30
STATE_VERSION = "hybrid_confidence_shrink_v1"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    if STATE_JSON.exists():
        try:
            payload = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict) and payload.get("freeze_ts") and payload.get("state_version") == STATE_VERSION:
            return payload
    payload = {
        "freeze_ts": utc_now_iso(),
        "state_version": STATE_VERSION,
        "entry_policy": "raw_v28_p50_edge0_fixed_selection",
        "hypothesis": (
            "FV direction is useful, but probability magnitude needs stateful "
            "humility. Combine the robust noise_shrink_light overlay with a "
            "small phi-shrink exception for high-recross/near-strike geometry."
        ),
        "promotion_floor": {
            "min_settled": MIN_SETTLED,
            "must_improve_brier_vs_raw": True,
            "must_improve_logloss_vs_raw": True,
            "must_not_change_entry_selection": True,
        },
        "rules": [
            "If p_raw < 0.60 and phi_penalty >= 2.0, keep raw probability.",
            "If p_raw >= 0.60 and recross >= 0.75, use phi_half_shrink_to50.",
            "If p_raw >= 0.60 and abs_d_sigma <= 0.25, use phi_quarter_shrink_to50.",
            "Otherwise use noise_shrink_light.",
        ],
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def phi_half(row: dict[str, Any]) -> float:
    raw = p_raw(row)
    return clamp_prob(0.50 + (raw - 0.50) * math.sqrt(phi_retention(row)))


def phi_quarter(row: dict[str, Any]) -> float:
    raw = p_raw(row)
    return clamp_prob(0.50 + (raw - 0.50) * (phi_retention(row) ** 0.25))


def p_hybrid(row: dict[str, Any]) -> float:
    raw = p_raw(row)
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma")) or 999.0
    if raw < 0.60 and phi_penalty_count(row) >= 2.0:
        return raw
    if raw >= 0.60 and recross >= 0.75:
        return phi_half(row)
    if raw >= 0.60 and abs_d <= 0.25:
        return phi_quarter(row)
    return p_light(row)


def hybrid_reason(row: dict[str, Any]) -> str:
    raw = p_raw(row)
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma")) or 999.0
    if raw < 0.60 and phi_penalty_count(row) >= 2.0:
        return "keep_raw_weak_heavy_noise"
    if raw >= 0.60 and recross >= 0.75:
        return "phi_half_high_recross"
    if raw >= 0.60 and abs_d <= 0.25:
        return "phi_quarter_near_strike"
    return "noise_shrink_light_default"


OVERLAYS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": p_raw,
    "noise_shrink_light": p_light,
    "phi_half_shrink_to50": phi_half,
    "phi_quarter_shrink_to50": phi_quarter,
    "hybrid_confidence_shrink": p_hybrid,
}


def score_rows(rows: list[dict[str, Any]], overlay: str, fn: Callable[[dict[str, Any]], float], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    scored = []
    for row in settled:
        p = clamp_prob(float(fn(row)))
        y = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "p": p,
            "outcome": y,
            "brier": (p - y) ** 2,
            "logloss": logloss(p, y),
        })
    return {
        "overlay": overlay,
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": len(rows) / denominator * 100.0 if denominator else None,
        "avg_brier": avg([float(row["brier"]) for row in scored]),
        "avg_logloss": avg([float(row["logloss"]) for row in scored]),
        "avg_p": avg([float(row["p"]) for row in scored]),
        "win_rate": avg([float(row["outcome"]) for row in scored]),
        "net_cents_after_entry_fee": sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled),
    }


def add_deltas(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw = next((row for row in rows if row.get("overlay") == "raw_probability"), {})
    out = []
    for row in rows:
        brier = as_float(row.get("avg_brier"))
        raw_brier = as_float(raw.get("avg_brier"))
        loss = as_float(row.get("avg_logloss"))
        raw_loss = as_float(raw.get("avg_logloss"))
        out.append({
            **row,
            "brier_delta_vs_raw": None if brier is None or raw_brier is None else brier - raw_brier,
            "logloss_delta_vs_raw": None if loss is None or raw_loss is None else loss - raw_loss,
            "blockers": validation_blockers(row, raw),
        })
    out.sort(key=lambda row: (float(row.get("avg_brier") or 999.0), float(row.get("avg_logloss") or 999.0)))
    return out


def reason_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for reason in sorted({hybrid_reason(row) for row in rows}):
        reason_rows = [row for row in rows if hybrid_reason(row) == reason]
        settled = [row for row in reason_rows if row.get("side_won") is not None]
        raw_briers = []
        hybrid_briers = []
        for row in settled:
            y = 1.0 if row.get("side_won") is True else 0.0
            raw_briers.append((p_raw(row) - y) ** 2)
            hybrid_briers.append((p_hybrid(row) - y) ** 2)
        out.append({
            "reason": reason,
            "entries": len(reason_rows),
            "settled": len(settled),
            "wins": sum(1 for row in settled if row.get("side_won") is True),
            "losses": sum(1 for row in settled if row.get("side_won") is False),
            "net_cents_after_entry_fee": sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled),
            "raw_brier": avg(raw_briers),
            "hybrid_brier": avg(hybrid_briers),
            "brier_delta_vs_raw": None if not raw_briers else avg(hybrid_briers) - avg(raw_briers),
        })
    return out


def detail_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "market": row.get("market"),
            "ts_wall": row.get("ts_wall"),
            "side": row.get("side"),
            "source": row.get("source"),
            "p_raw": row.get("p_side"),
            "p_hybrid": p_hybrid(row),
            "reason": hybrid_reason(row),
            "ask_prob": row.get("ask_prob"),
            "raw_edge_prob": raw_edge(row),
            "seconds_to_close": row.get("seconds_to_close"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "phi_penalty": phi_penalty_count(row),
            "side_won": row.get("side_won"),
            "net_gross_cents_after_entry_fee": row.get("net_gross_cents_after_entry_fee"),
        }
        for row in rows
    ]


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_dt = parse_ts(state["freeze_ts"])
    timing = market_timing(freeze_dt)
    rows = selected_base_rows()
    discovery_denominator = len({str(row.get("market") or "") for row in rows if row.get("market")})
    forward_markets = timing["clean_forward_markets"]
    forward_rows = [row for row in rows if str(row.get("market") or "") in forward_markets]
    forward_denominator = len(forward_markets)

    discovery = add_deltas([score_rows(rows, name, fn, discovery_denominator) for name, fn in OVERLAYS.items()])
    forward = add_deltas([score_rows(forward_rows, name, fn, forward_denominator) for name, fn in OVERLAYS.items()])
    return {
        "freeze_ts": state["freeze_ts"],
        "state_version": state.get("state_version"),
        "entry_policy": state.get("entry_policy"),
        "hypothesis": state.get("hypothesis"),
        "rules": state.get("rules"),
        "forward_denominator": forward_denominator,
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "discovery": discovery,
        "forward": forward,
        "discovery_reason_summary": reason_summary(rows),
        "forward_reason_summary": reason_summary(forward_rows),
        "forward_rows": detail_rows(forward_rows),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def table(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend([
        "",
        f"## {title}",
        "",
        "| rank | overlay | entries | settled | W/L | coverage | brier | d brier | logloss | d logloss | avg p | win rate | net c | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(rows, start=1):
        lines.append(
            f"| {idx} | {row.get('overlay')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
            f"{fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | "
            f"{fmt(row.get('net_cents_after_entry_fee'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Hybrid Confidence-Shrink FV",
        "",
        "Frozen forward validator for a fixed-entry probability overlay.",
        "",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Entry policy: `{report.get('entry_policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Hypothesis: {report.get('hypothesis')}",
        "",
        "## Rules",
        "",
    ]
    for rule in report.get("rules") or []:
        lines.append(f"- {rule}")
    table(lines, "Forward Ranking", report.get("forward") or [])
    table(lines, "Discovery Context", report.get("discovery") or [])
    lines.extend([
        "",
        "## Discovery Reason Summary",
        "",
        "| reason | entries | settled | W/L | net c | raw brier | hybrid brier | d brier |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("discovery_reason_summary") or []:
        lines.append(
            f"| {row.get('reason')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents_after_entry_fee'))} | "
            f"{fmt(row.get('raw_brier'))} | {fmt(row.get('hybrid_brier'))} | "
            f"{fmt(row.get('brier_delta_vs_raw'))} |"
        )
    lines.extend([
        "",
        "## Forward Rows",
        "",
        "| market | side | p raw | p hybrid | reason | ask | edge | stc | abs d | recross | phi penalty | won | net c |",
        "|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|---:|",
    ])
    for row in report.get("forward_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | "
            f"{fmt(row.get('p_hybrid'))} | {row.get('reason')} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('seconds_to_close'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{fmt(row.get('phi_penalty'))} | {row.get('side_won')} | "
            f"{fmt(row.get('net_gross_cents_after_entry_fee'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
