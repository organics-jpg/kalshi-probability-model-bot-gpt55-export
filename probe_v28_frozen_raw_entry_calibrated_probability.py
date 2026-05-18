"""Frozen forward validator for raw-entry calibrated probability overlays."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_entry_conditioned_posterior_diagnostic import summarize_bucket, tag_rows
from probe_v28_noise_floor_shrinkage_candidates import selected_rows
from probe_v28_raw_entry_calibrated_probability import OVERLAYS, score_overlay
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_latest.md"

FROZEN_OVERLAYS = [
    "raw_probability",
    "entry_conditioned_plus03_probability",
    "entry_conditioned_plus05_probability",
    "entry_conditioned_logit125_probability",
    "entry_conditioned_logit125_p60_only_probability",
    "noise_shrink_light_probability",
    "book_probability",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    if STATE_JSON.exists():
        try:
            payload = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict) and payload.get("freeze_ts"):
            overlays = payload.get("overlays") if isinstance(payload.get("overlays"), list) else []
            missing = [name for name in FROZEN_OVERLAYS if name not in overlays]
            if missing:
                payload["overlays"] = overlays + missing
                STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            return payload
    payload = {
        "freeze_ts": utc_now_iso(),
        "entry_policy": "raw_v28_p50_edge0_fixed_selection",
        "overlays": FROZEN_OVERLAYS,
        "promotion_floor": {
            "min_settled": 30,
            "required_coverage_pct_min": 70.0,
            "required_coverage_pct_max": 90.0,
            "must_improve_brier_vs_raw": True,
            "bucket_min_settled_for_stability": 5,
                "must_not_worsen_brier_in_all_eligible_buckets": True,
            "must_not_reduce_entry_pnl": True,
        },
    }
    STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_dt = parse_ts(state["freeze_ts"])
    rows = enrich_state(attach_regime_rows(observation_pool()))
    picked = selected_rows(rows, "v28_raw", p_raw, 0.50, 0.00)
    timing = market_timing(freeze_dt)
    forward_markets = timing["clean_forward_markets"]
    future_rows = [row for row in picked if str(row.get("market") or "") in forward_markets]
    denominator = len(forward_markets)
    summaries = []
    for name in state.get("overlays") or FROZEN_OVERLAYS:
        fn = OVERLAYS.get(name)
        if fn is None:
            continue
        summary = score_overlay(future_rows, name, fn)
        summary["coverage_pct"] = len(future_rows) / denominator * 100.0 if denominator else None
        summary["entries"] = len(future_rows)
        summary["settled"] = summary.get("count")
        summaries.append(summary)
    raw = next((row for row in summaries if row.get("overlay") == "raw_probability"), {})
    raw_brier = raw.get("avg_brier")
    raw_logloss = raw.get("avg_logloss")
    bucket_summary = [summarize_bucket(name, bucket_rows) for name, bucket_rows in tag_rows(future_rows).items()]
    ranked = []
    for row in summaries:
        ranked.append({
            **{key: value for key, value in row.items() if key not in {"buckets", "scored_rows"}},
            "brier_delta_vs_raw": None if raw_brier is None or row.get("avg_brier") is None else float(row["avg_brier"]) - float(raw_brier),
            "logloss_delta_vs_raw": None if raw_logloss is None or row.get("avg_logloss") is None else float(row["avg_logloss"]) - float(raw_logloss),
            "bucket_stability_failures": bucket_stability_failures(str(row.get("overlay") or ""), bucket_summary),
            "blockers": validation_blockers(row, raw, bucket_summary),
        })
    ranked.sort(key=lambda row: (float(row.get("avg_brier") or 999.0), float(row.get("avg_logloss") or 999.0)))
    return {
        "freeze_ts": state["freeze_ts"],
        "entry_policy": state.get("entry_policy"),
        "forward_market_denominator": denominator,
        "forward_markets": sorted(forward_markets),
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "post_freeze_observed_markets": sorted(timing["post_freeze_observed_markets"]),
        "future_entry_rows": len(future_rows),
        "future_entry_details": entry_details(future_rows),
        "promotion_floor": state.get("promotion_floor"),
        "summaries": summaries,
        "bucket_summary": bucket_summary,
        "ranked": ranked,
    }


def entry_details(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for row in rows:
        details.append({
            "market": row.get("market"),
            "ts_wall": row.get("ts_wall"),
            "side": row.get("side"),
            "source": row.get("source"),
            "p_side": row.get("p_side"),
            "ask_prob": row.get("ask_prob"),
            "raw_edge_prob": row.get("raw_edge_prob"),
            "seconds_to_close": row.get("seconds_to_close"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "spectral_tag": row.get("spectral_tag"),
            "side_won": row.get("side_won"),
            "net_gross_cents_after_entry_fee": row.get("net_gross_cents_after_entry_fee"),
        })
    return details


def bucket_stability_failures(overlay: str, bucket_summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if overlay == "raw_probability":
        return []
    failures: list[dict[str, Any]] = []
    for bucket in bucket_summary:
        if float(bucket.get("settled") or 0.0) < 5:
            continue
        overlay_row = next((item for item in bucket.get("overlays") or [] if item.get("overlay") == overlay), {})
        delta = overlay_row.get("brier_delta_vs_raw")
        if delta is None or float(delta) > 0.0:
            failures.append({
                "bucket": bucket.get("bucket"),
                "settled": bucket.get("settled"),
                "brier_delta_vs_raw": delta,
            })
    return failures


def validation_blockers(row: dict[str, Any], raw: dict[str, Any], bucket_summary: list[dict[str, Any]]) -> list[str]:
    blockers: list[str] = []
    settled = float(row.get("count") or 0.0)
    coverage = row.get("coverage_pct")
    if settled < 30:
        blockers.append("settled_lt_30")
    if coverage is None or float(coverage) < 70.0:
        blockers.append("coverage_too_low")
    if coverage is not None and float(coverage) > 90.0:
        blockers.append("coverage_too_high")
    if row.get("overlay") != "raw_probability":
        raw_brier = raw.get("avg_brier")
        if raw_brier is None or row.get("avg_brier") is None or float(row["avg_brier"]) >= float(raw_brier):
            blockers.append("brier_not_better_than_raw")
        if bucket_stability_failures(str(row.get("overlay") or ""), bucket_summary):
            blockers.append("bucket_brier_not_better_than_raw")
    return blockers


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Frozen Raw-Entry Calibrated Probability",
        "",
        "Forward-only calibration validator. Entry selection is fixed at raw v28 p50 edge0; overlays only change the assigned probability.",
        "",
        f"- Freeze timestamp UTC: `{report['freeze_ts']}`",
        f"- Forward market denominator: `{report['forward_market_denominator']}`",
        f"- Future entry rows: `{report['future_entry_rows']}`",
        "",
        "| rank | overlay | entries | settled | coverage | brier | delta | logloss | delta | avg p | win rate | net c | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for idx, row in enumerate(report["ranked"], start=1):
        lines.append(
            f"| {idx} | {row['overlay']} | {row.get('entries')} | {row.get('settled')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} | {fmt(row.get('avg_p'))} | "
            f"{fmt(row.get('win_rate'))} | {fmt(row.get('net_cents_after_entry_fee'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend(["", "## Bucket Stability", ""])
    for row in report["ranked"]:
        failures = row.get("bucket_stability_failures") or []
        if row.get("overlay") == "raw_probability":
            continue
        if not failures:
            lines.append(f"- `{row.get('overlay')}`: no eligible bucket failures.")
            continue
        failure_text = ", ".join(
            f"{item.get('bucket')}:{fmt(item.get('brier_delta_vs_raw'))}"
            for item in failures
        )
        lines.append(f"- `{row.get('overlay')}` failures: {failure_text}")
    lines.extend(["", "## Future Entry Rows", ""])
    details = report.get("future_entry_details") or []
    if not details:
        lines.append("none")
    else:
        lines.append("| market | ts | side | source | p_raw | ask | raw edge | stc | abs d | recross | spectral | won | net c |")
        lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|---:|")
        for row in details:
            lines.append(
                f"| {row.get('market')} | {row.get('ts_wall')} | {row.get('side')} | {row.get('source')} | "
                f"{fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | "
                f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | "
                f"{row.get('spectral_tag')} | {row.get('side_won')} | {fmt(row.get('net_gross_cents_after_entry_fee'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
