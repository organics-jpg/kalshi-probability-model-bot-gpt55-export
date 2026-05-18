"""Robustness diagnostic for entry-conditioned FV posterior lift.

This tests whether the +3/+5pp posterior overlays are a broad selection effect
or just an aggregate artifact. Entry selection stays fixed at raw v28 p50 edge0.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_noise_floor_shrinkage_candidates import selected_rows
from probe_v28_raw_entry_calibrated_probability import OVERLAYS, score_overlay
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_entry_conditioned_posterior_diagnostic_latest.json"
OUT_MD = OUT_DIR / "v28_entry_conditioned_posterior_diagnostic_latest.md"

OVERLAY_NAMES = [
    "raw_probability",
    "entry_conditioned_plus03_probability",
    "entry_conditioned_plus05_probability",
    "entry_conditioned_plus05_noise_attenuated_probability",
    "entry_conditioned_logit125_probability",
    "entry_conditioned_logit125_p60_only_probability",
    "noise_shrink_light_probability",
    "book_probability",
]


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def tag_rows(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {"all": rows}
    markets = sorted({str(row.get("market") or "") for row in rows})
    split_at = max(1, len(markets) // 2)
    early = set(markets[:split_at])
    late = set(markets[split_at:])
    buckets["early_markets"] = [row for row in rows if str(row.get("market") or "") in early]
    buckets["late_markets"] = [row for row in rows if str(row.get("market") or "") in late]
    buckets["approved_entries"] = [row for row in rows if row.get("source") == "approved_entry"]
    buckets["shadow_rejected_actionable"] = [row for row in rows if row.get("source") == "rejected_actionable"]
    buckets["near_strike_abs_d_lte_025"] = [row for row in rows if (as_float(row.get("abs_d_sigma")) or 999.0) <= 0.25]
    buckets["away_from_strike_abs_d_gt_025"] = [row for row in rows if (as_float(row.get("abs_d_sigma")) or 0.0) > 0.25]
    buckets["high_recross"] = [row for row in rows if row.get("h6_recross_hazard_high") is True or (as_float(row.get("recross_hazard_score")) or 0.0) >= 0.75]
    buckets["lower_recross"] = [row for row in rows if not (row.get("h6_recross_hazard_high") is True or (as_float(row.get("recross_hazard_score")) or 0.0) >= 0.75)]
    buckets["spectral_dominant_factor"] = [row for row in rows if str(row.get("spectral_tag") or "") == "spectral_dominant_factor"]
    buckets["insufficient_or_other_spectral"] = [row for row in rows if str(row.get("spectral_tag") or "") != "spectral_dominant_factor"]
    buckets["raw_p_50_60"] = [row for row in rows if 0.50 <= float(row.get("p_side") or 0.0) < 0.60]
    buckets["raw_p_60_plus"] = [row for row in rows if float(row.get("p_side") or 0.0) >= 0.60]
    buckets["ask_lte_60"] = [row for row in rows if (as_float(row.get("ask_prob")) or 999.0) <= 0.60]
    buckets["ask_gt_60"] = [row for row in rows if (as_float(row.get("ask_prob")) or 0.0) > 0.60]
    return {name: bucket for name, bucket in buckets.items() if bucket}


def summarize_bucket(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    overlay_scores = []
    raw_score = None
    for overlay in OVERLAY_NAMES:
        fn = OVERLAYS[overlay]
        score = score_overlay(rows, overlay, fn)
        compact = {key: value for key, value in score.items() if key not in {"buckets", "scored_rows"}}
        if overlay == "raw_probability":
            raw_score = compact
        overlay_scores.append(compact)
    raw_brier = None if raw_score is None else raw_score.get("avg_brier")
    raw_logloss = None if raw_score is None else raw_score.get("avg_logloss")
    for score in overlay_scores:
        score["brier_delta_vs_raw"] = None if raw_brier is None or score.get("avg_brier") is None else float(score["avg_brier"]) - float(raw_brier)
        score["logloss_delta_vs_raw"] = None if raw_logloss is None or score.get("avg_logloss") is None else float(score["avg_logloss"]) - float(raw_logloss)
    ranked = sorted(overlay_scores, key=lambda row: (float(row.get("avg_brier") or 999.0), float(row.get("avg_logloss") or 999.0)))
    plus05 = next((row for row in overlay_scores if row["overlay"] == "entry_conditioned_plus05_probability"), {})
    return {
        "bucket": name,
        "rows": len(rows),
        "settled": sum(1 for row in rows if row.get("side_won") is not None),
        "wins": sum(1 for row in rows if row.get("side_won") is True),
        "losses": sum(1 for row in rows if row.get("side_won") is False),
        "net_cents_after_entry_fee": sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in rows if row.get("gross_cents") is not None),
        "best_overlay": ranked[0] if ranked else None,
        "plus05": plus05,
        "overlays": ranked,
    }


def build_report() -> dict[str, Any]:
    rows = enrich_state(attach_regime_rows(observation_pool()))
    picked = selected_rows(rows, "v28_raw", p_raw, 0.50, 0.00)
    buckets = tag_rows(picked)
    summary = [summarize_bucket(name, bucket_rows) for name, bucket_rows in buckets.items()]
    weak = [
        row for row in summary
        if row["settled"] >= 5
        and row.get("plus05", {}).get("brier_delta_vs_raw") is not None
        and float(row["plus05"]["brier_delta_vs_raw"]) >= 0.0
    ]
    strong = [
        row for row in summary
        if row["settled"] >= 5
        and row.get("plus05", {}).get("brier_delta_vs_raw") is not None
        and float(row["plus05"]["brier_delta_vs_raw"]) < 0.0
    ]
    return {
        "entry_policy": "raw_v28_p50_edge0_fixed_selection",
        "selected_entries": len(picked),
        "settled_entries": sum(1 for row in picked if row.get("side_won") is not None),
        "summary": summary,
        "plus05_supporting_buckets": [{"bucket": row["bucket"], "settled": row["settled"], "delta": row["plus05"]["brier_delta_vs_raw"]} for row in strong],
        "plus05_weak_buckets": [{"bucket": row["bucket"], "settled": row["settled"], "delta": row["plus05"]["brier_delta_vs_raw"]} for row in weak],
        "interpretation": "Bucket support is diagnostic only. Forward validator must decide promotion.",
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
        "# v28 Entry-Conditioned Posterior Diagnostic",
        "",
        "Fixed entry selector: raw v28 p50 edge0. Tests whether posterior lift improves calibration across physical buckets.",
        "",
        f"- Selected entries: `{report['selected_entries']}`",
        f"- Settled entries: `{report['settled_entries']}`",
        "",
        "| bucket | rows | settled | W/L | net c | best overlay | best brier | plus05 brier delta | plus05 logloss delta |",
        "|---|---:|---:|---:|---:|---|---:|---:|---:|",
    ]
    for row in report["summary"]:
        best = row.get("best_overlay") or {}
        plus05 = row.get("plus05") or {}
        lines.append(
            f"| {row['bucket']} | {row['rows']} | {row['settled']} | {row['wins']}/{row['losses']} | "
            f"{fmt(row['net_cents_after_entry_fee'])} | {best.get('overlay')} | {fmt(best.get('avg_brier'))} | "
            f"{fmt(plus05.get('brier_delta_vs_raw'))} | {fmt(plus05.get('logloss_delta_vs_raw'))} |"
        )
    lines.extend(["", "## Interpretation", ""])
    weak = report.get("plus05_weak_buckets") or []
    if weak:
        lines.append("- Buckets where +5pp failed to improve Brier with at least 5 settled rows:")
        for row in weak:
            lines.append(f"  - `{row['bucket']}` settled `{row['settled']}`, delta `{fmt(row['delta'])}`")
    else:
        lines.append("- +5pp improved Brier in every bucket with at least 5 settled rows.")
    lines.append("- This remains discovery-only until the frozen forward validator accumulates sample.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
