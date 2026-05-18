"""Confidence-shrink schedule bakeoff for fixed v28 entry rows.

Research-only; no live bot changes or orders.

This answers a narrow question from the phi-forgetting probe: did phi help
because of the constant itself, or because the current raw FV is overconfident
and needs a shrink-to-50 controller?
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
from probe_v28_noise_floor_shrinkage_candidates import p_full, p_light, p_rmt_recency
from probe_v28_phi_forgetting_fv_candidates import phi_penalty_count, phi_retention
from probe_v28_state_aware_fv_candidates import p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_confidence_shrink_schedule_bakeoff_state.json"
OUT_JSON = OUT_DIR / "v28_confidence_shrink_schedule_bakeoff_latest.json"
OUT_MD = OUT_DIR / "v28_confidence_shrink_schedule_bakeoff_latest.md"
MIN_SETTLED = 30


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    if STATE_JSON.exists():
        try:
            payload = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict) and payload.get("freeze_ts"):
            return payload
    payload = {
        "freeze_ts": utc_now_iso(),
        "entry_policy": "raw_v28_p50_edge0_fixed_selection",
        "hypothesis": (
            "Raw v28 direction may be useful while its probability magnitude is "
            "too hot. Compare non-fitted shrink schedules before promoting any "
            "new FV overlay."
        ),
        "promotion_floor": {
            "min_settled": MIN_SETTLED,
            "must_improve_brier_vs_raw": True,
            "must_improve_logloss_vs_raw": True,
            "must_not_change_entry_selection": True,
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def shrink_const(retention: float) -> Callable[[dict[str, Any]], float]:
    def _fn(row: dict[str, Any]) -> float:
        raw = p_raw(row)
        return clamp_prob(0.50 + (raw - 0.50) * retention)

    return _fn


def p_phi_half(row: dict[str, Any]) -> float:
    raw = p_raw(row)
    return clamp_prob(0.50 + (raw - 0.50) * math.sqrt(phi_retention(row)))


def p_phi_quarter(row: dict[str, Any]) -> float:
    raw = p_raw(row)
    return clamp_prob(0.50 + (raw - 0.50) * (phi_retention(row) ** 0.25))


OVERLAYS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": p_raw,
    "const_shrink_070": shrink_const(0.70),
    "const_shrink_080": shrink_const(0.80),
    "const_shrink_090": shrink_const(0.90),
    "phi_half_shrink_to50": p_phi_half,
    "phi_quarter_shrink_to50": p_phi_quarter,
    "noise_shrink_light": p_light,
    "noise_shrink_full": p_full,
    "noise_shrink_rmt_recency": p_rmt_recency,
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


def bucket_tags(row: dict[str, Any]) -> list[str]:
    p = p_raw(row)
    edge = raw_edge(row)
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma")) or 999.0
    tags = ["all", "raw_p_50_60" if p < 0.60 else "raw_p_60_plus"]
    if edge is not None:
        tags.append("edge_lt_4pp" if edge < 0.04 else "edge_ge_4pp")
    tags.append("near_strike" if abs_d <= 0.25 else "away_from_strike")
    tags.append("high_recross" if recross >= 0.75 else "lower_recross")
    if phi_penalty_count(row) >= 2.0:
        tags.append("phi_heavy_noise")
    return tags


def bucket_summary(rows: list[dict[str, Any]], overlays: list[str]) -> list[dict[str, Any]]:
    out = []
    for tag in sorted({tag for row in rows for tag in bucket_tags(row)}):
        tag_rows = [row for row in rows if tag in bucket_tags(row)]
        settled = [row for row in tag_rows if row.get("side_won") is not None]
        briers = {}
        for overlay in overlays:
            fn = OVERLAYS[overlay]
            values = []
            for row in settled:
                p = clamp_prob(float(fn(row)))
                y = 1.0 if row.get("side_won") is True else 0.0
                values.append((p - y) ** 2)
            briers[overlay] = avg(values)
        out.append({
            "bucket": tag,
            "entries": len(tag_rows),
            "settled": len(settled),
            "wins": sum(1 for row in settled if row.get("side_won") is True),
            "losses": sum(1 for row in settled if row.get("side_won") is False),
            "net_cents_after_entry_fee": sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled),
            "avg_phi_penalty": avg([phi_penalty_count(row) for row in tag_rows]),
            "briers": briers,
        })
    return out


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
    top_names = ["raw_probability"]
    for row in discovery[:4]:
        name = str(row["overlay"])
        if name not in top_names:
            top_names.append(name)
    return {
        "freeze_ts": state["freeze_ts"],
        "entry_policy": state.get("entry_policy"),
        "hypothesis": state.get("hypothesis"),
        "forward_denominator": forward_denominator,
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "discovery": discovery,
        "forward": forward,
        "discovery_bucket_summary": bucket_summary(rows, top_names),
        "forward_bucket_summary": bucket_summary(forward_rows, top_names),
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
        "# v28 Confidence-Shrink Schedule Bakeoff",
        "",
        "Research-only fixed-entry FV calibration check.",
        "",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Entry policy: `{report.get('entry_policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Hypothesis: {report.get('hypothesis')}",
    ]
    table(lines, "Forward Ranking", report.get("forward") or [])
    table(lines, "Discovery Context", report.get("discovery") or [])
    lines.extend([
        "",
        "## Discovery Buckets",
        "",
        "| bucket | entries | settled | W/L | net c | phi penalty | raw brier | best brier | best overlay |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("discovery_bucket_summary") or []:
        briers = row.get("briers") or {}
        best_overlay = min(briers, key=lambda name: float(briers.get(name) or 999.0)) if briers else None
        lines.append(
            f"| {row.get('bucket')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents_after_entry_fee'))} | "
            f"{fmt(row.get('avg_phi_penalty'))} | {fmt(briers.get('raw_probability'))} | "
            f"{fmt(briers.get(best_overlay))} | {best_overlay} |"
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
