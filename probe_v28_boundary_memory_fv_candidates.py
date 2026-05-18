"""Frozen forward validator for boundary-memory FV overlays.

Research-only; no live bot changes or orders.

This probe turns the "catastrophic forgetting" metaphor into a predeclared FV
experiment. The fixed entry surface remains raw v28 p50 edge0. Candidate
overlays can only change the assigned probability, not the selected side:

    keep raw FV when the market is near-boundary and turbulent;
    retain/sharpen FV information only when geometry says the signal is durable.

The state file freezes the validation timestamp at first run so future evidence
is cleanly separated from discovery rows.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_noise_floor_shrinkage_candidates import selected_rows
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_boundary_memory_fv_candidates_state.json"
OUT_JSON = OUT_DIR / "v28_boundary_memory_fv_candidates_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_memory_fv_candidates_latest.md"

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
            "Boundary information should be forgotten when raw probability is weak, "
            "edge is thin, and recross/strike geometry is turbulent; strong raw "
            "conviction can retain or sharpen FV information."
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


def logit_sharpen(p: float, scale: float) -> float:
    p = clamp_prob(p)
    logit = math.log(p / (1.0 - p))
    return clamp_prob(1.0 / (1.0 + math.exp(-scale * logit)))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def raw_edge(row: dict[str, Any]) -> float | None:
    p = as_float(row.get("p_side") or row.get("p_eff"))
    ask = as_float(row.get("ask_prob"))
    if p is None or ask is None:
        return None
    return p - ask


def boundary_memory_retention(row: dict[str, Any]) -> float:
    """Return how much of a posterior/sharpening adjustment survives.

    This is intentionally simple and physics-declared rather than optimized:
    weak raw conviction, thin executable edge, and turbulent near-strike
    geometry each erase part of the adjustment. The base raw FV remains intact.
    """
    p = p_raw(row)
    edge = raw_edge(row)
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma")) or 999.0
    spectral = str(row.get("spectral_tag") or "")

    retention = 1.0
    if p < 0.60:
        retention *= 0.35
    if edge is not None and edge < 0.04:
        retention *= 0.55
    if recross >= 0.75 and abs_d <= 0.25:
        retention *= 0.35
    if spectral == "spectral_noise":
        retention *= 0.80
    if spectral == "spectral_dominant_factor" and p < 0.60:
        retention *= 0.80
    return max(0.0, min(1.0, retention))


def p_conditional_logit125(row: dict[str, Any]) -> float:
    p = p_raw(row)
    if p < 0.60:
        return clamp_prob(p)
    return logit_sharpen(p, 1.25)


def p_boundary_memory_logit125(row: dict[str, Any]) -> float:
    p = p_raw(row)
    sharp = logit_sharpen(p, 1.25)
    return clamp_prob(p + boundary_memory_retention(row) * (sharp - p))


def p_boundary_memory_plus05(row: dict[str, Any]) -> float:
    p = p_raw(row)
    return clamp_prob(p + 0.05 * boundary_memory_retention(row))


OVERLAYS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": p_raw,
    "conditional_logit125_p60_only": p_conditional_logit125,
    "boundary_memory_logit125": p_boundary_memory_logit125,
    "boundary_memory_plus05": p_boundary_memory_plus05,
}


def selected_base_rows() -> list[dict[str, Any]]:
    rows = enrich_state(attach_regime_rows(observation_pool()))
    picked = selected_rows(rows, "v28_raw", p_raw, 0.50, 0.00)
    return [{**row, "raw_edge_prob": raw_edge(row), "memory_retention": boundary_memory_retention(row)} for row in picked]


def score_rows(rows: list[dict[str, Any]], overlay: str, fn: Callable[[dict[str, Any]], float], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    scored = []
    for row in settled:
        p = clamp_prob(float(fn(row)))
        y = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "market": row.get("market"),
            "p": p,
            "outcome": y,
            "brier": (p - y) ** 2,
            "logloss": logloss(p, y),
        })
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled)
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
        "net_cents_after_entry_fee": net,
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def validation_blockers(row: dict[str, Any], raw: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    settled = int(as_float(row.get("settled")) or 0)
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if row.get("overlay") != "raw_probability":
        brier = as_float(row.get("avg_brier"))
        raw_brier = as_float(raw.get("avg_brier"))
        logloss_value = as_float(row.get("avg_logloss"))
        raw_logloss = as_float(raw.get("avg_logloss"))
        if brier is None or raw_brier is None or brier >= raw_brier:
            blockers.append("brier_not_better_than_raw")
        if logloss_value is None or raw_logloss is None or logloss_value >= raw_logloss:
            blockers.append("logloss_not_better_than_raw")
    return blockers


def bucket_tags(row: dict[str, Any]) -> list[str]:
    p = p_raw(row)
    edge = raw_edge(row)
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma")) or 999.0
    tags = ["all"]
    tags.append("raw_p_50_60" if p < 0.60 else "raw_p_60_plus")
    if edge is not None:
        tags.append("edge_lt_4pp" if edge < 0.04 else "edge_ge_4pp")
    tags.append("near_strike" if abs_d <= 0.25 else "away_from_strike")
    tags.append("high_recross" if recross >= 0.75 else "lower_recross")
    if p < 0.60 and edge is not None and edge < 0.04 and recross >= 0.75 and abs_d <= 0.25:
        tags.append("weak_thin_turbulent_boundary")
    return tags


def bucket_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for tag in sorted({tag for row in rows for tag in bucket_tags(row)}):
        tag_rows = [row for row in rows if tag in bucket_tags(row)]
        settled = [row for row in tag_rows if row.get("side_won") is not None]
        if not tag_rows:
            continue
        scored = []
        for name, fn in OVERLAYS.items():
            vals = []
            for row in settled:
                p = clamp_prob(float(fn(row)))
                y = 1.0 if row.get("side_won") is True else 0.0
                vals.append((p - y) ** 2)
            scored.append({"overlay": name, "avg_brier": avg(vals)})
        out.append({
            "bucket": tag,
            "entries": len(tag_rows),
            "settled": len(settled),
            "wins": sum(1 for row in settled if row.get("side_won") is True),
            "losses": sum(1 for row in settled if row.get("side_won") is False),
            "avg_retention": avg([float(row.get("memory_retention") or 0.0) for row in tag_rows]),
            "net_cents_after_entry_fee": sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled),
            "overlays": scored,
        })
    return out


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_dt = parse_ts(state["freeze_ts"])
    timing = market_timing(freeze_dt)
    forward_markets = timing["clean_forward_markets"]
    rows = selected_base_rows()
    discovery_denominator = len({str(row.get("market") or "") for row in rows if row.get("market")})
    forward_rows = [row for row in rows if str(row.get("market") or "") in forward_markets]
    forward_denominator = len(forward_markets)

    discovery = [score_rows(rows, name, fn, discovery_denominator) for name, fn in OVERLAYS.items()]
    raw_discovery = next((row for row in discovery if row.get("overlay") == "raw_probability"), {})
    ranked_discovery = []
    for row in discovery:
        raw_brier = as_float(raw_discovery.get("avg_brier"))
        raw_logloss = as_float(raw_discovery.get("avg_logloss"))
        brier = as_float(row.get("avg_brier"))
        loss = as_float(row.get("avg_logloss"))
        ranked_discovery.append({
            **row,
            "brier_delta_vs_raw": None if brier is None or raw_brier is None else brier - raw_brier,
            "logloss_delta_vs_raw": None if loss is None or raw_logloss is None else loss - raw_logloss,
        })
    ranked_discovery.sort(key=lambda row: (float(row.get("avg_brier") or 999.0), float(row.get("avg_logloss") or 999.0)))
    forward = [score_rows(forward_rows, name, fn, forward_denominator) for name, fn in OVERLAYS.items()]
    raw_forward = next((row for row in forward if row.get("overlay") == "raw_probability"), {})
    ranked_forward = []
    for row in forward:
        raw_brier = as_float(raw_forward.get("avg_brier"))
        raw_logloss = as_float(raw_forward.get("avg_logloss"))
        brier = as_float(row.get("avg_brier"))
        loss = as_float(row.get("avg_logloss"))
        ranked_forward.append({
            **row,
            "brier_delta_vs_raw": None if brier is None or raw_brier is None else brier - raw_brier,
            "logloss_delta_vs_raw": None if loss is None or raw_logloss is None else loss - raw_logloss,
            "blockers": validation_blockers(row, raw_forward),
        })
    ranked_forward.sort(key=lambda row: (float(row.get("avg_brier") or 999.0), float(row.get("avg_logloss") or 999.0)))
    return {
        "freeze_ts": state["freeze_ts"],
        "hypothesis": state.get("hypothesis"),
        "entry_policy": state.get("entry_policy"),
        "forward_denominator": forward_denominator,
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "forward_rows": detail_rows(forward_rows),
        "discovery": ranked_discovery,
        "forward": ranked_forward,
        "forward_bucket_summary": bucket_summary(forward_rows),
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
            "raw_edge_prob": row.get("raw_edge_prob"),
            "seconds_to_close": row.get("seconds_to_close"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "spectral_tag": row.get("spectral_tag"),
            "memory_retention": row.get("memory_retention"),
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
        "# v28 Boundary-Memory FV Candidates",
        "",
        "Frozen forward validator for catastrophic-forgetting-style FV overlays.",
        "",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Entry policy: `{report.get('entry_policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
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
        "Not promotion evidence. This only shows whether the predeclared memory idea is directionally sane on older rows.",
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
        "| bucket | entries | settled | W/L | avg retention | net c | raw brier | boundary logit brier | boundary +5 brier |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for bucket in report.get("forward_bucket_summary") or []:
        by_overlay = {row.get("overlay"): row for row in bucket.get("overlays") or []}
        lines.append(
            f"| {bucket.get('bucket')} | {bucket.get('entries')} | {bucket.get('settled')} | "
            f"{bucket.get('wins')}/{bucket.get('losses')} | {fmt(bucket.get('avg_retention'))} | "
            f"{fmt(bucket.get('net_cents_after_entry_fee'))} | "
            f"{fmt((by_overlay.get('raw_probability') or {}).get('avg_brier'))} | "
            f"{fmt((by_overlay.get('boundary_memory_logit125') or {}).get('avg_brier'))} | "
            f"{fmt((by_overlay.get('boundary_memory_plus05') or {}).get('avg_brier'))} |"
        )
    lines.extend([
        "",
        "## Forward Rows",
        "",
        "| market | side | p raw | ask | edge | stc | abs d | recross | spectral | retention | won | net c |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|",
    ])
    for row in report.get("forward_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | "
            f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {row.get('spectral_tag')} | "
            f"{fmt(row.get('memory_retention'))} | {row.get('side_won')} | "
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
