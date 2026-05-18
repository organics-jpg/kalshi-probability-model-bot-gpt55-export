"""Shadow-only RMT-style regime diagnostic for v28 BTC 15m.

The goal is not to fit a high-dimensional model. It is to test a narrower
market-physics claim: when the recent feature cloud is mostly spectral noise,
v28 geometry should be penalized or anchored to the executable book more often.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np

from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_shadow_fv_variants import (
    variant_book,
    variant_large_disagreement_book_anchor,
    variant_raw,
    variant_v28_premium_book_anchor,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_rmt_regime_diagnostic_latest.json"
OUT_CSV = OUT_DIR / "v28_rmt_regime_diagnostic_latest.csv"
OUT_MD = OUT_DIR / "v28_rmt_regime_diagnostic_latest.md"

ROLLING_WINDOW = 48
MIN_WINDOW = 24
WINSOR_Q_LOW = 0.05
WINSOR_Q_HIGH = 0.95

FEATURES = [
    "p_side",
    "ask_prob",
    "v28_minus_ask_prob",
    "edge_cents",
    "seconds_to_close",
    "sigma_t_dollars",
    "abs_d_sigma",
    "eligible_depth",
    "recross_hazard_score",
    "book_age_ms",
    "btc_age_ms",
]

VARIANTS: dict[str, Callable[[dict[str, Any]], float]] = {
    "v28_raw": variant_raw,
    "book_ask_prior": variant_book,
    "large_disagreement_book_anchor": variant_large_disagreement_book_anchor,
    "v28_premium_book_anchor": variant_v28_premium_book_anchor,
}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def robust_matrix(rows: list[dict[str, Any]], features: list[str]) -> np.ndarray | None:
    matrix: list[list[float]] = []
    for row in rows:
        values: list[float] = []
        ok = True
        for feature in features:
            value = as_float(row.get(feature))
            if value is None:
                ok = False
                break
            values.append(value)
        if ok:
            matrix.append(values)
    if len(matrix) < MIN_WINDOW:
        return None
    x = np.asarray(matrix, dtype=float)
    low = np.quantile(x, WINSOR_Q_LOW, axis=0)
    high = np.quantile(x, WINSOR_Q_HIGH, axis=0)
    x = np.clip(x, low, high)
    median = np.median(x, axis=0)
    mad = np.median(np.abs(x - median), axis=0)
    scale = np.where(mad > 1e-9, 1.4826 * mad, np.std(x, axis=0))
    scale = np.where(scale > 1e-9, scale, 1.0)
    return (x - median) / scale


def spectral_metrics(window_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    x = robust_matrix(window_rows, FEATURES)
    if x is None:
        return None
    n, p = x.shape
    if n < MIN_WINDOW or p < 2:
        return None
    cov = (x.T @ x) / float(n)
    eigvals = np.linalg.eigvalsh(cov)
    eigvals = np.maximum(eigvals, 0.0)
    q = p / float(n)
    lambda_plus = (1.0 + math.sqrt(q)) ** 2
    outliers = eigvals[eigvals > lambda_plus]
    total = float(np.sum(eigvals))
    outlier_share = float(np.sum(outliers) / total) if total > 1e-12 else 0.0
    top = float(eigvals[-1]) if eigvals.size else 0.0
    return {
        "window_n": int(n),
        "feature_count": int(p),
        "lambda_plus": float(lambda_plus),
        "top_eigenvalue": top,
        "top_over_mp_edge": top / float(lambda_plus) if lambda_plus else None,
        "outlier_count": int(outliers.size),
        "outlier_share": outlier_share,
        "spectral_tag": spectral_tag(int(outliers.size), outlier_share, top / float(lambda_plus)),
    }


def spectral_tag(outlier_count: int, outlier_share: float, top_over_edge: float) -> str:
    if outlier_count <= 0 or top_over_edge < 1.05:
        return "spectral_noise"
    if outlier_share >= 0.35 or top_over_edge >= 1.75:
        return "spectral_dominant_factor"
    return "spectral_factor"


def attach_regime_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: str(row.get("ts_wall") or ""))
    enriched: list[dict[str, Any]] = []
    history: list[dict[str, Any]] = []
    for row in ordered:
        metrics = spectral_metrics(history[-ROLLING_WINDOW:])
        enriched_row = dict(row)
        if metrics:
            enriched_row.update(metrics)
        else:
            enriched_row.update(
                {
                    "window_n": 0,
                    "feature_count": len(FEATURES),
                    "lambda_plus": None,
                    "top_eigenvalue": None,
                    "top_over_mp_edge": None,
                    "outlier_count": None,
                    "outlier_share": None,
                    "spectral_tag": "insufficient_history",
                }
            )
        enriched.append(enriched_row)
        if all(as_float(row.get(feature)) is not None for feature in FEATURES):
            history.append(row)
    return enriched


def score_probability(row: dict[str, Any], fn: Callable[[dict[str, Any]], float]) -> float | None:
    if row.get("side_won") is None:
        return None
    try:
        p = fn(row)
    except (KeyError, TypeError, ValueError):
        return None
    outcome = 1.0 if row.get("side_won") is True else 0.0
    return (p - outcome) ** 2


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    resolved = [row for row in rows if row.get("gross_cents") is not None]
    variant_scores: dict[str, dict[str, Any]] = {}
    for name, fn in VARIANTS.items():
        briers = [score_probability(row, fn) for row in settled]
        briers = [value for value in briers if value is not None]
        variant_scores[name] = {
            "count": len(briers),
            "avg_brier": (sum(briers) / len(briers)) if briers else None,
        }
    raw_brier = variant_scores.get("v28_raw", {}).get("avg_brier")
    for bucket in variant_scores.values():
        avg_brier = bucket.get("avg_brier")
        bucket["brier_minus_v28_raw"] = None if avg_brier is None or raw_brier is None else avg_brier - raw_brier
    return {
        "observations": len(rows),
        "settled": len(settled),
        "resolved": len(resolved),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "gross_cents": sum(float(row.get("gross_cents") or 0.0) for row in resolved),
        "avg_top_over_mp_edge": average(row.get("top_over_mp_edge") for row in rows),
        "avg_outlier_share": average(row.get("outlier_share") for row in rows),
        "variant_scores": variant_scores,
    }


def collapse_rows(rows: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    picked: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        key = (
            str(row.get("market") or ""),
            str(row.get("side") or ""),
            str(row.get("source") or ""),
        )
        if mode == "first":
            picked.setdefault(key, row)
        elif mode == "last":
            picked[key] = row
        else:
            raise ValueError(f"unknown collapse mode: {mode}")
    return list(picked.values())


def average(values: Any) -> float | None:
    nums = [as_float(value) for value in values]
    nums = [value for value in nums if value is not None]
    return sum(nums) / len(nums) if nums else None


def build_report() -> dict[str, Any]:
    rows = attach_regime_rows(observation_pool())
    by_tag: dict[str, dict[str, Any]] = {}
    for tag in sorted({str(row.get("spectral_tag") or "") for row in rows}):
        by_tag[tag] = summarize_group([row for row in rows if row.get("spectral_tag") == tag])
    approved = [row for row in rows if row.get("source") == "approved_entry"]
    rejected = [row for row in rows if row.get("source") == "rejected_actionable"]
    views = {
        "all_observations": summarize_group(rows),
        "approved_entries": summarize_group(approved),
        "rejected_actionable": summarize_group(rejected),
        "first_per_market_side_source": summarize_group(collapse_rows(rows, "first")),
        "last_per_market_side_source": summarize_group(collapse_rows(rows, "last")),
    }
    return {
        "settings": {
            "rolling_window": ROLLING_WINDOW,
            "min_window": MIN_WINDOW,
            "features": FEATURES,
            "winsor_quantiles": [WINSOR_Q_LOW, WINSOR_Q_HIGH],
        },
        "summary": {
            "all": summarize_group(rows),
            "approved_entries": summarize_group(approved),
            "rejected_actionable": summarize_group(rejected),
            "by_spectral_tag": by_tag,
            "views": views,
        },
        "rows": rows,
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    if not rows:
        OUT_CSV.write_text("", encoding="utf-8")
        return
    keys = [
        "ts_wall",
        "market",
        "source",
        "side",
        "p_side",
        "ask_prob",
        "v28_minus_ask_prob",
        "edge_cents",
        "seconds_to_close",
        "sigma_t_dollars",
        "abs_d_sigma",
        "eligible_depth",
        "recross_hazard_score",
        "book_age_ms",
        "btc_age_ms",
        "spectral_tag",
        "window_n",
        "lambda_plus",
        "top_eigenvalue",
        "top_over_mp_edge",
        "outlier_count",
        "outlier_share",
        "side_won",
        "gross_cents",
        "result",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# v28 RMT Regime Diagnostic",
        "",
        "Shadow-only test of whether recent feature covariance has a real spectral factor or is mostly noise.",
        "",
        f"- Rolling window: `{ROLLING_WINDOW}` actionable observations",
        f"- Minimum history: `{MIN_WINDOW}` observations",
        f"- Features: `{', '.join(FEATURES)}`",
        "",
        "## Overall",
        "",
    ]
    all_summary = summary["all"]
    lines.extend(
        [
            f"- Observations: `{all_summary['observations']}`",
            f"- Settled/resolved: `{all_summary['settled']}/{all_summary['resolved']}`",
            f"- Gross cents: `{all_summary['gross_cents']}`",
            f"- Avg top / MP edge: `{fmt(all_summary['avg_top_over_mp_edge'])}`",
            f"- Avg outlier share: `{fmt(all_summary['avg_outlier_share'])}`",
            "",
            "## By Spectral Tag",
            "",
            "| tag | obs | settled | wins | losses | gross c | top/edge | outlier share | best brier variant | best brier | best vs raw |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|",
        ]
    )
    for tag, bucket in summary["by_spectral_tag"].items():
        scores = bucket.get("variant_scores") or {}
        ranked = sorted(
            (
                {"variant": name, **score}
                for name, score in scores.items()
                if score.get("avg_brier") is not None
            ),
            key=lambda item: (item["avg_brier"], item["variant"]),
        )
        best = ranked[0] if ranked else {}
        lines.append(
            f"| {tag} | {bucket['observations']} | {bucket['settled']} | {bucket['wins']} | {bucket['losses']} | "
            f"{bucket['gross_cents']} | {fmt(bucket['avg_top_over_mp_edge'])} | {fmt(bucket['avg_outlier_share'])} | "
            f"{best.get('variant')} | {fmt(best.get('avg_brier'))} | {fmt(best.get('brier_minus_v28_raw'))} |"
        )
    lines.extend(["", "## Variant Brier By Tag", ""])
    for tag, bucket in summary["by_spectral_tag"].items():
        lines.append(f"### {tag}")
        scores = bucket.get("variant_scores") or {}
        for name, score in sorted(scores.items(), key=lambda item: item[0]):
            lines.append(
                f"- `{name}`: count `{score.get('count')}`, avg_brier `{fmt(score.get('avg_brier'))}`, "
                f"vs_raw `{fmt(score.get('brier_minus_v28_raw'))}`"
            )
        lines.append("")
    lines.extend(["## Robustness Views", ""])
    lines.append("| view | obs | settled | gross c | best variant | best brier | best vs raw |")
    lines.append("|---|---:|---:|---:|---|---:|---:|")
    for view_name, bucket in (summary.get("views") or {}).items():
        scores = bucket.get("variant_scores") or {}
        ranked = sorted(
            (
                {"variant": name, **score}
                for name, score in scores.items()
                if score.get("avg_brier") is not None
            ),
            key=lambda item: (item["avg_brier"], item["variant"]),
        )
        best = ranked[0] if ranked else {}
        lines.append(
            f"| {view_name} | {bucket['observations']} | {bucket['settled']} | {bucket['gross_cents']} | "
            f"{best.get('variant')} | {fmt(best.get('avg_brier'))} | {fmt(best.get('brier_minus_v28_raw'))} |"
        )
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(report["rows"])
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
