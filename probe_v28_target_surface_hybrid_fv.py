"""Hybrid FV validation on the fixed target-coverage entry surface.

Research-only; no live bot changes or orders.

The hybrid confidence-shrink overlay looked good on fixed raw p50 rows. This
probe tests it on the stricter target-coverage surface that is closest to the
active goal's 75-80% participation requirement.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_hybrid_confidence_shrink_fv import hybrid_reason, p_hybrid
from probe_v28_raw_entry_calibrated_probability import OVERLAYS
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import (
    STATE_JSON as TARGET_STATE_JSON,
    apply_policy,
    boundary_recross_shrink_probability,
    load_json,
)
from probe_v28_frozen_forward_candidates import market_timing, parse_ts


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_target_surface_hybrid_fv_state.json"
OUT_JSON = OUT_DIR / "v28_target_surface_hybrid_fv_latest.json"
OUT_MD = OUT_DIR / "v28_target_surface_hybrid_fv_latest.md"

MIN_SETTLED = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0
POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    if STATE_JSON.exists():
        payload = load_json(STATE_JSON)
        if payload.get("freeze_ts") and payload.get("policy") == POLICY:
            return payload
    payload = {
        "freeze_ts": utc_now_iso(),
        "entry_surface": "fixed_target_coverage_raw_entry_valve",
        "policy": POLICY,
        "hypothesis": "Hybrid FV should improve calibration on broad target rows without changing selected side.",
        "promotion_floor": {
            "min_settled": MIN_SETTLED,
            "coverage_min": COVERAGE_MIN,
            "coverage_max": COVERAGE_MAX,
            "must_improve_brier_vs_raw": True,
            "must_improve_logloss_vs_raw": True,
            "must_not_change_entry_selection": True,
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def p_raw(row: dict[str, Any]) -> float:
    value = as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))
    if value is None:
        raise ValueError("missing raw probability")
    return clamp_prob(value)


def p_noise_light(row: dict[str, Any]) -> float:
    return clamp_prob(float(OVERLAYS["noise_shrink_light_probability"](row)))


def p_boundary_recross(row: dict[str, Any]) -> float:
    return clamp_prob(float(boundary_recross_shrink_probability(row)))


OVERLAY_FNS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": p_raw,
    "noise_shrink_light_probability": p_noise_light,
    "boundary_recross_shrink_probability": p_boundary_recross,
    "hybrid_confidence_shrink": p_hybrid,
}


def forward_rows() -> tuple[list[dict[str, Any]], int]:
    target_state = load_json(TARGET_STATE_JSON)
    freeze_dt = parse_ts(target_state.get("source_coverage_freeze_ts") or target_state.get("freeze_ts"))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    selected = apply_policy(selected_base_rows(), POLICY)
    rows = [row for row in selected if str(row.get("market") or "") in forward_markets]
    return rows, len(forward_markets)


def score_overlay(rows: list[dict[str, Any]], denominator: int, overlay: str, fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    scored = []
    for row in settled:
        p = clamp_prob(float(fn(row)))
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "market": row.get("market"),
            "p": p,
            "outcome": outcome,
            "brier": (p - outcome) ** 2,
            "logloss": logloss(p, outcome),
            "net_cents": row.get("net_gross_cents_after_entry_fee"),
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
        "net_cents_after_entry_fee": sum(float(row.get("net_cents") or 0.0) for row in scored),
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def enrich(scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw = next((row for row in scores if row.get("overlay") == "raw_probability"), {})
    raw_brier = as_float(raw.get("avg_brier"))
    raw_logloss = as_float(raw.get("avg_logloss"))
    ranked = []
    for row in scores:
        brier = as_float(row.get("avg_brier"))
        loss = as_float(row.get("avg_logloss"))
        out = {
            **row,
            "brier_delta_vs_raw": None if brier is None or raw_brier is None else brier - raw_brier,
            "logloss_delta_vs_raw": None if loss is None or raw_logloss is None else loss - raw_logloss,
        }
        out["blockers"] = blockers(out)
        ranked.append(out)
    ranked.sort(key=lambda row: (float(row.get("avg_brier") or 999.0), float(row.get("avg_logloss") or 999.0)))
    return ranked


def blockers(row: dict[str, Any]) -> list[str]:
    out: list[str] = []
    settled = int(as_float(row.get("settled")) or 0)
    coverage = as_float(row.get("coverage_pct"))
    brier_delta = as_float(row.get("brier_delta_vs_raw"))
    logloss_delta = as_float(row.get("logloss_delta_vs_raw"))
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_MIN:
        out.append("coverage_too_low")
    if coverage is not None and coverage > COVERAGE_MAX:
        out.append("coverage_too_high")
    if row.get("overlay") != "raw_probability":
        if brier_delta is None or brier_delta >= 0.0:
            out.append("brier_not_better_than_raw")
        if logloss_delta is None or logloss_delta >= 0.0:
            out.append("logloss_not_better_than_raw")
    return out


def edge_bucket(row: dict[str, Any]) -> str:
    raw = p_raw(row)
    hybrid = p_hybrid(row)
    ask = as_float(row.get("ask_prob")) or 0.0
    raw_edge = raw - ask
    hybrid_edge = hybrid - ask
    if hybrid_edge < 0.0 <= raw_edge:
        return "hybrid_vetoes_raw_edge"
    if hybrid_edge < 0.02:
        return "hybrid_edge_lt_2pp"
    if hybrid_edge < 0.04:
        return "hybrid_edge_2_4pp"
    if hybrid_edge < 0.08:
        return "hybrid_edge_4_8pp"
    return "hybrid_edge_ge_8pp"


def summarize_group(rows: list[dict[str, Any]], name: str, denominator: int | None = None) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    return {
        "bucket": name,
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": len(rows) / denominator * 100.0 if denominator else None,
        "net_cents": sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled),
        "avg_raw_p": avg([p_raw(row) for row in settled]),
        "avg_hybrid_p": avg([p_hybrid(row) for row in settled]),
        "avg_ask": avg([float(as_float(row.get("ask_prob")) or 0.0) for row in settled]),
    }


def grouped(rows: list[dict[str, Any]], denominator: int) -> list[dict[str, Any]]:
    out = []
    for bucket in sorted({edge_bucket(row) for row in rows}):
        out.append(summarize_group([row for row in rows if edge_bucket(row) == bucket], bucket, denominator))
    for reason in sorted({hybrid_reason(row) for row in rows}):
        out.append(summarize_group([row for row in rows if hybrid_reason(row) == reason], f"reason_{reason}", denominator))
    return sorted(out, key=lambda row: (float(row.get("net_cents") or 0.0), -int(row.get("settled") or 0)))


def compact(row: dict[str, Any]) -> dict[str, Any]:
    ask = as_float(row.get("ask_prob")) or 0.0
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "source": row.get("source"),
        "p_raw": p_raw(row),
        "p_hybrid": p_hybrid(row),
        "ask_prob": ask,
        "raw_edge": p_raw(row) - ask,
        "hybrid_edge": p_hybrid(row) - ask,
        "edge_bucket": edge_bucket(row),
        "hybrid_reason": hybrid_reason(row),
        "seconds_to_close": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    rows, denominator = forward_rows()
    scores = enrich([score_overlay(rows, denominator, name, fn) for name, fn in OVERLAY_FNS.items()])
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts": state.get("freeze_ts"),
        "policy": state.get("policy"),
        "hypothesis": state.get("hypothesis"),
        "forward_denominator": denominator,
        "ranked": scores,
        "grouped": grouped(rows, denominator),
        "rows": [compact(row) for row in rows],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Target-Surface Hybrid FV",
        "",
        "Research-only validation on the fixed target-coverage entry surface.",
        "",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Policy: `{report.get('policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Hypothesis: {report.get('hypothesis')}",
        "",
        "## Ranking",
        "",
        "| rank | overlay | entries | settled | W/L | coverage | brier | d brier | logloss | d logloss | avg p | win rate | net c | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        lines.append(
            f"| {idx} | {row.get('overlay')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
            f"{fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | "
            f"{fmt(row.get('net_cents_after_entry_fee'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Groups",
        "",
        "| bucket | entries | settled | W/L | coverage | net c | avg raw p | avg hybrid p | avg ask |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("grouped") or []:
        lines.append(
            f"| {row.get('bucket')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('avg_raw_p'))} | "
            f"{fmt(row.get('avg_hybrid_p'))} | {fmt(row.get('avg_ask'))} |"
        )
    lines.extend([
        "",
        "## Rows",
        "",
        "| market | side | p raw | p hybrid | ask | raw edge | hybrid edge | edge bucket | reason | won | net c |",
        "|---|---|---:|---:|---:|---:|---:|---|---|---|---:|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | "
            f"{fmt(row.get('p_hybrid'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge'))} | {fmt(row.get('hybrid_edge'))} | "
            f"{row.get('edge_bucket')} | {row.get('hybrid_reason')} | "
            f"{row.get('side_won')} | {fmt(row.get('net_cents'))} |"
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
