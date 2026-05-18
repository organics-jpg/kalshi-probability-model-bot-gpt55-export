"""Calibrated probability overlays for raw-v28 entry selection.

The latest diagnostics show a useful split:
- raw v28 p50 is the best broad entry selector so far;
- noise-floor shrinkage improves Brier on some high-coverage rows but loses
  P&L when used directly as the entry gate.

This probe keeps the entry surface fixed at raw p50 edge0 and scores several
fair-value probability overlays on the exact same selected rows. If an overlay
improves calibration without changing selected markets, it can inform exits,
position sizing, and later FV improvements without confusing entry economics.

Research-only. Does not touch live bot logic or orders.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

from probe_v28_noise_floor_shrinkage_candidates import (
    p_full,
    p_light,
    p_rmt_recency,
    reliability_rmt_recency,
    recross_penalty,
    selected_rows,
    stale_penalty,
)
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_book, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_raw_entry_calibrated_probability_latest.json"
OUT_MD = OUT_DIR / "v28_raw_entry_calibrated_probability_latest.md"


OVERLAYS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": p_raw,
    "entry_conditioned_plus03_probability": lambda row: clamp_prob(p_raw(row) + 0.03),
    "entry_conditioned_plus05_probability": lambda row: clamp_prob(p_raw(row) + 0.05),
    "entry_conditioned_plus05_noise_attenuated_probability": lambda row: p_plus05_noise_attenuated(row),
    "entry_conditioned_logit125_probability": lambda row: logit_sharpen(p_raw(row), 1.25),
    "entry_conditioned_logit125_p60_only_probability": lambda row: p_logit125_p60_only(row),
    "book_probability": p_book,
    "noise_shrink_light_probability": p_light,
    "noise_shrink_full_probability": p_full,
    "noise_shrink_rmt_recency_probability": p_rmt_recency,
}


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logit_sharpen(p: float, scale: float) -> float:
    p = clamp_prob(p)
    logit = math.log(p / (1.0 - p))
    return clamp_prob(1.0 / (1.0 + math.exp(-scale * logit)))


def p_plus05_noise_attenuated(row: dict[str, Any]) -> float:
    """Add the entry-conditioned posterior lift, but forget it in noisy states.

    This deliberately keeps raw v28 entry selection and side intact. RMT,
    repetition, recross, and staleness can only reduce the incremental +5pp
    posterior lift; they cannot flip the side or drag the base FV toward book.
    """
    attenuation = reliability_rmt_recency(row)
    attenuation *= max(0.55, 1.0 - recross_penalty(row))
    attenuation *= max(0.70, 1.0 - 0.5 * stale_penalty(row))
    return clamp_prob(p_raw(row) + 0.05 * max(0.0, min(1.0, attenuation)))


def p_logit125_p60_only(row: dict[str, Any]) -> float:
    """Sharpen only rows where raw FV already has real conviction.

    The forward logit125 challenger improves the aggregate but fails weak
    50-60% buckets. This keeps weak rows at raw FV and applies logit sharpening
    only once raw selected-side probability reaches 60%.
    """
    p = p_raw(row)
    if p < 0.60:
        return clamp_prob(p)
    return logit_sharpen(p, 1.25)


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def bucket_key(p: float) -> str:
    lo = int(math.floor(p * 10.0)) * 10
    hi = min(100, lo + 10)
    return f"{lo:02d}-{hi:02d}"


def score_overlay(rows: list[dict[str, Any]], name: str, fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    scored: list[dict[str, Any]] = []
    for row in rows:
        if row.get("side_won") is None:
            continue
        try:
            p = clamp_prob(float(fn(row)))
        except (KeyError, TypeError, ValueError):
            continue
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "source": row.get("source"),
            "p": p,
            "outcome": outcome,
            "brier": (p - outcome) ** 2,
            "logloss": logloss(p, outcome),
            "gross_cents": row.get("gross_cents"),
            "net_gross_cents_after_entry_fee": row.get("net_gross_cents_after_entry_fee"),
            "bucket": bucket_key(p),
        })
    buckets: list[dict[str, Any]] = []
    for bucket in sorted({row["bucket"] for row in scored}):
        bucket_rows = [row for row in scored if row["bucket"] == bucket]
        probs = [float(row["p"]) for row in bucket_rows]
        outcomes = [float(row["outcome"]) for row in bucket_rows]
        buckets.append({
            "bucket": bucket,
            "count": len(bucket_rows),
            "avg_p": avg(probs),
            "win_rate": avg(outcomes),
            "abs_calibration_error": None if avg(probs) is None or avg(outcomes) is None else abs(float(avg(probs)) - float(avg(outcomes))),
            "net_cents_after_entry_fee": sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in bucket_rows),
        })
    ece = sum(
        (row["count"] / len(scored)) * float(row.get("abs_calibration_error") or 0.0)
        for row in buckets
    ) if scored else None
    return {
        "overlay": name,
        "count": len(scored),
        "avg_brier": avg([float(row["brier"]) for row in scored]),
        "avg_logloss": avg([float(row["logloss"]) for row in scored]),
        "ece_10bucket": ece,
        "avg_p": avg([float(row["p"]) for row in scored]),
        "win_rate": avg([float(row["outcome"]) for row in scored]),
        "net_cents_after_entry_fee": sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in scored),
        "buckets": buckets,
        "scored_rows": scored,
    }


def build_report() -> dict[str, Any]:
    rows = enrich_state(attach_regime_rows(observation_pool()))
    raw_selected = selected_rows(rows, "v28_raw", p_raw, 0.50, 0.00)
    summaries = [score_overlay(raw_selected, name, fn) for name, fn in OVERLAYS.items()]
    raw = next((row for row in summaries if row["overlay"] == "raw_probability"), {})
    raw_brier = raw.get("avg_brier")
    raw_logloss = raw.get("avg_logloss")
    raw_ece = raw.get("ece_10bucket")
    ranked = []
    for row in summaries:
        ranked.append({
            **{key: value for key, value in row.items() if key not in {"buckets", "scored_rows"}},
            "brier_delta_vs_raw": None if raw_brier is None or row.get("avg_brier") is None else float(row["avg_brier"]) - float(raw_brier),
            "logloss_delta_vs_raw": None if raw_logloss is None or row.get("avg_logloss") is None else float(row["avg_logloss"]) - float(raw_logloss),
            "ece_delta_vs_raw": None if raw_ece is None or row.get("ece_10bucket") is None else float(row["ece_10bucket"]) - float(raw_ece),
        })
    ranked.sort(key=lambda row: (float(row["avg_brier"] or 999.0), float(row["avg_logloss"] or 999.0)))
    return {
        "entry_policy": "raw_v28_p50_edge0_fixed_selection",
        "entry_interpretation": "P&L/coverage are fixed by the raw p50 entry selector; only FV probability accuracy changes.",
        "selected_entries": len(raw_selected),
        "settled_entries": sum(1 for row in raw_selected if row.get("side_won") is not None),
        "coverage_note": "Coverage matches the raw p50 selected row count from the active discovery slice.",
        "summaries": summaries,
        "ranked": ranked,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Raw Entry Calibrated Probability",
        "",
        "Fixed entry selector: raw v28 p50 edge0. This report changes only the FV probability assigned to the same selected rows.",
        "",
        f"- Selected entries: `{report['selected_entries']}`",
        f"- Settled entries: `{report['settled_entries']}`",
        "",
        "| rank | overlay | count | brier | delta | logloss | delta | ece | delta | avg p | win rate | net c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(report["ranked"], start=1):
        lines.append(
            f"| {idx} | {row['overlay']} | {row['count']} | {fmt(row['avg_brier'])} | "
            f"{fmt(row['brier_delta_vs_raw'])} | {fmt(row['avg_logloss'])} | {fmt(row['logloss_delta_vs_raw'])} | "
            f"{fmt(row['ece_10bucket'])} | {fmt(row['ece_delta_vs_raw'])} | {fmt(row['avg_p'])} | "
            f"{fmt(row['win_rate'])} | {fmt(row['net_cents_after_entry_fee'])} |"
        )
    lines.extend(["", "## Bucket View"])
    by_name = {row["overlay"]: row for row in report["summaries"]}
    for name in [row["overlay"] for row in report["ranked"][:3]]:
        lines.extend(["", f"### {name}", ""])
        lines.append("| bucket | count | avg p | win rate | abs err | net c |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for bucket in by_name.get(name, {}).get("buckets") or []:
            lines.append(
                f"| {bucket['bucket']} | {bucket['count']} | {fmt(bucket['avg_p'])} | "
                f"{fmt(bucket['win_rate'])} | {fmt(bucket['abs_calibration_error'])} | "
                f"{fmt(bucket['net_cents_after_entry_fee'])} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
