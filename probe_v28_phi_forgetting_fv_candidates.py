"""Frozen forward validator for phi-decay FV memory overlays.

Research-only; no live bot changes or orders.

This tests the user's "catastrophic forgetting + phi" intuition in a constrained
way. Entry selection is fixed to raw v28 p50 edge0. The candidate only changes
the reported probability by retaining less of a sharpening adjustment as
boundary/noise penalties stack up.
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
    logit_sharpen,
    logloss,
    raw_edge,
    selected_base_rows,
    validation_blockers,
)
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_state_aware_fv_candidates import p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_phi_forgetting_fv_candidates_state.json"
OUT_JSON = OUT_DIR / "v28_phi_forgetting_fv_candidates_latest.json"
OUT_MD = OUT_DIR / "v28_phi_forgetting_fv_candidates_latest.md"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
MIN_SETTLED = 30
STATE_VERSION = "phi_forgetting_shrink_v2"


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
            "Phi decay is a compressible forgetting schedule: each independent "
            "noise/turbulence warning divides retained FV adjustment by phi. "
            "Durable geometry can restore one half-step, but selection cannot change."
        ),
        "phi": PHI,
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


def phi_penalty_count(row: dict[str, Any]) -> float:
    p = p_raw(row)
    edge = raw_edge(row)
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma")) or 999.0
    spectral = str(row.get("spectral_tag") or "")

    penalties = 0.0
    if p < 0.60:
        penalties += 1.0
    if edge is not None and edge < 0.04:
        penalties += 1.0
    if abs_d <= 0.25:
        penalties += 0.5
    if recross >= 0.75:
        penalties += 0.5
    if abs_d <= 0.25 and recross >= 0.75:
        penalties += 1.0
    if spectral == "spectral_noise":
        penalties += 1.0
    if spectral == "spectral_dominant_factor" and p < 0.60:
        penalties += 0.5

    durable_geometry = p >= 0.70 and edge is not None and edge >= 0.04 and abs_d > 0.25
    if durable_geometry:
        penalties -= 0.5
    return max(0.0, penalties)


def phi_retention(row: dict[str, Any]) -> float:
    return max(0.0, min(1.0, PHI ** (-phi_penalty_count(row))))


def p_phi_plus03(row: dict[str, Any]) -> float:
    return clamp_prob(p_raw(row) + 0.03 * phi_retention(row))


def p_phi_plus05(row: dict[str, Any]) -> float:
    return clamp_prob(p_raw(row) + 0.05 * phi_retention(row))


def p_phi_logit125(row: dict[str, Any]) -> float:
    raw = p_raw(row)
    sharp = logit_sharpen(raw, 1.25)
    return clamp_prob(raw + phi_retention(row) * (sharp - raw))


def p_phi_shrink_to50(row: dict[str, Any]) -> float:
    raw = p_raw(row)
    return clamp_prob(0.50 + (raw - 0.50) * phi_retention(row))


def p_phi_half_shrink_to50(row: dict[str, Any]) -> float:
    raw = p_raw(row)
    retention = math.sqrt(phi_retention(row))
    return clamp_prob(0.50 + (raw - 0.50) * retention)


OVERLAYS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": p_raw,
    "phi_shrink_to50": p_phi_shrink_to50,
    "phi_half_shrink_to50": p_phi_half_shrink_to50,
    "phi_forget_plus03": p_phi_plus03,
    "phi_forget_plus05": p_phi_plus05,
    "phi_forget_logit125": p_phi_logit125,
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


def bucket_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tags = sorted({tag for row in rows for tag in bucket_tags(row)})
    out = []
    for tag in tags:
        tag_rows = [row for row in rows if tag in bucket_tags(row)]
        settled = [row for row in tag_rows if row.get("side_won") is not None]
        overlay_briers = {}
        for name, fn in OVERLAYS.items():
            values = []
            for row in settled:
                p = clamp_prob(float(fn(row)))
                y = 1.0 if row.get("side_won") is True else 0.0
                values.append((p - y) ** 2)
            overlay_briers[name] = avg(values)
        out.append({
            "bucket": tag,
            "entries": len(tag_rows),
            "settled": len(settled),
            "wins": sum(1 for row in settled if row.get("side_won") is True),
            "losses": sum(1 for row in settled if row.get("side_won") is False),
            "avg_phi_penalty": avg([phi_penalty_count(row) for row in tag_rows]),
            "avg_phi_retention": avg([phi_retention(row) for row in tag_rows]),
            "net_cents_after_entry_fee": sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled),
            "overlay_briers": overlay_briers,
        })
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
        tags.append("phi_forget_heavy")
    if phi_penalty_count(row) <= 0.5:
        tags.append("phi_remember_high")
    return tags


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_dt = parse_ts(state["freeze_ts"])
    timing = market_timing(freeze_dt)
    rows = selected_base_rows()
    discovery_denominator = len({str(row.get("market") or "") for row in rows if row.get("market")})
    forward_markets = timing["clean_forward_markets"]
    forward_denominator = len(forward_markets)
    forward_rows = [row for row in rows if str(row.get("market") or "") in forward_markets]

    discovery = add_deltas([score_rows(rows, name, fn, discovery_denominator) for name, fn in OVERLAYS.items()])
    forward = add_deltas([score_rows(forward_rows, name, fn, forward_denominator) for name, fn in OVERLAYS.items()])
    return {
        "freeze_ts": state["freeze_ts"],
        "hypothesis": state.get("hypothesis"),
        "entry_policy": state.get("entry_policy"),
        "phi": state.get("phi"),
        "forward_denominator": forward_denominator,
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "discovery": discovery,
        "forward": forward,
        "forward_bucket_summary": bucket_summary(forward_rows),
        "forward_rows": detail_rows(forward_rows),
    }


def detail_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "market": row.get("market"),
            "ts_wall": row.get("ts_wall"),
            "side": row.get("side"),
            "source": row.get("source"),
            "p_raw": row.get("p_side"),
            "ask_prob": row.get("ask_prob"),
            "raw_edge_prob": raw_edge(row),
            "seconds_to_close": row.get("seconds_to_close"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "spectral_tag": row.get("spectral_tag"),
            "phi_penalty": phi_penalty_count(row),
            "phi_retention": phi_retention(row),
            "side_won": row.get("side_won"),
            "net_gross_cents_after_entry_fee": row.get("net_gross_cents_after_entry_fee"),
        }
        for row in rows
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Phi-Forgetting FV Candidates",
        "",
        "Frozen forward validator for phi-decay catastrophic-forgetting overlays.",
        "",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Entry policy: `{report.get('entry_policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Phi: `{report.get('phi')}`",
        f"- Hypothesis: {report.get('hypothesis')}",
        "",
        "## Forward Ranking",
        "",
        "| rank | overlay | entries | settled | W/L | coverage | brier | d brier | logloss | d logloss | avg p | win rate | net c | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for idx, row in enumerate(report.get("forward") or [], start=1):
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
        "## Discovery Context",
        "",
        "Not promotion evidence. The phi schedule must earn forward rows after its own freeze timestamp.",
        "",
        "| rank | overlay | entries | settled | W/L | brier | d brier | logloss | d logloss | avg p | win rate | net c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("discovery") or [], start=1):
        lines.append(
            f"| {idx} | {row.get('overlay')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('avg_brier'))} | "
            f"{fmt(row.get('brier_delta_vs_raw'))} | {fmt(row.get('avg_logloss'))} | "
            f"{fmt(row.get('logloss_delta_vs_raw'))} | {fmt(row.get('avg_p'))} | "
            f"{fmt(row.get('win_rate'))} | {fmt(row.get('net_cents_after_entry_fee'))} |"
        )
    lines.extend([
        "",
        "## Forward Buckets",
        "",
        "| bucket | entries | settled | W/L | avg phi penalty | avg retention | net c | raw brier | phi shrink | phi half shrink | phi +3 | phi +5 | phi logit |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for bucket in report.get("forward_bucket_summary") or []:
        briers = bucket.get("overlay_briers") or {}
        lines.append(
            f"| {bucket.get('bucket')} | {bucket.get('entries')} | {bucket.get('settled')} | "
            f"{bucket.get('wins')}/{bucket.get('losses')} | {fmt(bucket.get('avg_phi_penalty'))} | "
            f"{fmt(bucket.get('avg_phi_retention'))} | {fmt(bucket.get('net_cents_after_entry_fee'))} | "
            f"{fmt(briers.get('raw_probability'))} | {fmt(briers.get('phi_shrink_to50'))} | "
            f"{fmt(briers.get('phi_half_shrink_to50'))} | {fmt(briers.get('phi_forget_plus03'))} | "
            f"{fmt(briers.get('phi_forget_plus05'))} | {fmt(briers.get('phi_forget_logit125'))} |"
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
