"""Residual physics audit for the v31 FV probability surface.

This is a calibration diagnostic, not a trade scorer. It asks where the FV
probability surface is still miscalibrated after the settlement-average fixes:
time-to-close, distance to strike, recent signed/adverse motion, drift-projected
margin, and book/model disagreement.

No orders are submitted and no live bot files or processes are touched.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from probe_market_interval_80coverage import clean_json, pct
from probe_mushroom_v29_fv_surface import PROB_EPS, brier, logloss


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
PREDICTIONS_PATH = OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_all_heartbeats_latest.csv"
REPORT_MD = OUT_DIR / "v31_probability_residual_physics_latest.md"
REPORT_JSON = OUT_DIR / "v31_probability_residual_physics_latest.json"
BUCKET_CSV = OUT_DIR / "v31_probability_residual_physics_buckets_latest.csv"

MODELS = ["v28_live_surface", "v28_avg90", "v31_avg90_final60_exact"]
MIN_BUCKET_ROWS = 100

CUSTOM_BINS: dict[str, list[float]] = {
    "seconds_to_close": [0, 60, 90, 120, 180, 300, 600, 900],
    "margin_per_v28_sigma": [-np.inf, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, np.inf],
    "book_minus_model_p_side": [-1.0, -0.20, -0.10, -0.05, 0.0, 0.05, 0.10, 0.20, 1.0],
}

QUANTILE_FEATURES = [
    "signed_velocity_dps_1m",
    "signed_velocity_dps_3m",
    "signed_velocity_dps_5m",
    "adverse_move_1m",
    "adverse_move_3m",
    "adverse_move_5m",
    "drift_projected_margin_1m",
    "drift_projected_margin_3m",
    "drift_projected_margin_5m",
    "book_margin_cents",
    "spread_cents",
]


def bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def finite_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)


def interval_label(interval: Any) -> str:
    text = str(interval)
    return text.replace("(-inf", "[-inf").replace("inf]", "inf]")


def bucket_labels(rows: pd.DataFrame, feature: str) -> pd.Series:
    values = finite_float(rows[feature])
    if feature in CUSTOM_BINS:
        return pd.cut(values, bins=CUSTOM_BINS[feature], include_lowest=True).astype(str)
    try:
        return pd.qcut(values, q=8, duplicates="drop").astype(str)
    except ValueError:
        return pd.Series(["nan"] * len(rows), index=rows.index, dtype=object)


def metric_for(part: pd.DataFrame, model: str) -> dict[str, Any]:
    y = bool_series(part["win"]).astype(float).to_numpy()
    p = finite_float(part[f"{model}_p_side"]).to_numpy(dtype=float)
    mask = np.isfinite(p)
    if not mask.any():
        return {
            "rows": 0,
            "mean_pred": None,
            "realized": None,
            "error": None,
            "abs_error": None,
            "brier": None,
            "logloss": None,
        }
    y = y[mask]
    p = np.clip(p[mask], PROB_EPS, 1.0 - PROB_EPS)
    mean_pred = float(p.mean())
    realized = float(y.mean())
    error = mean_pred - realized
    return {
        "rows": int(len(p)),
        "mean_pred": mean_pred,
        "realized": realized,
        "error": float(error),
        "abs_error": float(abs(error)),
        "brier": brier(y, p),
        "logloss": logloss(y, p),
    }


def build_rows(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    out["book_minus_model_p_side"] = finite_float(out["book_p_side"]) - finite_float(out["v31_avg90_final60_exact_p_side"])

    features = list(CUSTOM_BINS) + [feature for feature in QUANTILE_FEATURES if feature in out.columns]
    records: list[dict[str, Any]] = []
    for feature in features:
        out["_bucket"] = bucket_labels(out, feature)
        for split in ["all", "validation", "holdout"]:
            split_rows = out if split == "all" else out[out["split"].astype(str).eq(split)]
            if split_rows.empty:
                continue
            for bucket, bucket_rows in split_rows.groupby("_bucket", dropna=False, sort=True):
                if str(bucket).lower() in {"nan", "nat"}:
                    continue
                for model in MODELS:
                    metrics = metric_for(bucket_rows, model)
                    if metrics["rows"] <= 0:
                        continue
                    records.append(
                        {
                            "feature": feature,
                            "bucket": interval_label(bucket),
                            "split": split,
                            "model": model,
                            **metrics,
                        }
                    )
    return pd.DataFrame(records)


def write_report(bucket_df: pd.DataFrame) -> None:
    holdout = bucket_df[
        bucket_df["split"].eq("holdout")
        & bucket_df["model"].eq("v31_avg90_final60_exact")
        & bucket_df["rows"].ge(MIN_BUCKET_ROWS)
    ].copy()
    worst = holdout.sort_values(["abs_error", "rows"], ascending=[False, False]).head(15)
    by_feature = (
        holdout.groupby("feature", as_index=False)
        .agg(weighted_abs_error=("abs_error", lambda s: float(np.average(s, weights=holdout.loc[s.index, "rows"]))))
        .sort_values("weighted_abs_error", ascending=False)
    )

    lines = [
        "# v31 Probability Residual Physics",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope",
        "",
        "- Calibration residual audit for FV probabilities, not trade scoring.",
        "- Uses the all-heartbeats v31 probability replay.",
        "- No live bot code/process or orders are touched.",
        "",
        "## Worst Holdout Buckets",
        "",
        f"Rows floor: `{MIN_BUCKET_ROWS}`.",
        "",
        "| feature | bucket | rows | mean pred | realized | error | Brier | logloss |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in worst.iterrows():
        lines.append(
            f"| `{row['feature']}` | `{row['bucket']}` | {int(row['rows'])} | "
            f"{pct(row['mean_pred'])} | {pct(row['realized'])} | {pct(row['error'])} | "
            f"{row['brier']:.5f} | {row['logloss']:.5f} |"
        )

    lines += [
        "",
        "## Feature Residual Ranking",
        "",
        "| feature | weighted abs error |",
        "|---|---:|",
    ]
    for _, row in by_feature.iterrows():
        lines.append(f"| `{row['feature']}` | {pct(row['weighted_abs_error'])} |")

    lines += [
        "",
        "## Read",
        "",
        "- Buckets with large residuals are candidates for the next FV-state correction.",
        "- A bucket here is not a trading rule; it is a place where the probability surface is miscalibrated.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not PREDICTIONS_PATH.exists():
        raise SystemExit(f"Missing predictions file: {PREDICTIONS_PATH}")
    rows = pd.read_csv(PREDICTIONS_PATH, low_memory=False)
    missing = [f"{model}_p_side" for model in MODELS if f"{model}_p_side" not in rows.columns]
    if missing:
        raise SystemExit(f"Missing probability columns: {missing}. Rerun probe_mushroom_v29_fv_surface.py first.")
    bucket_df = build_rows(rows)
    BUCKET_CSV.write_text(bucket_df.to_csv(index=False), encoding="utf-8")
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "predictions_path": str(PREDICTIONS_PATH),
        "models": MODELS,
        "min_bucket_rows": MIN_BUCKET_ROWS,
        "bucket_rows": bucket_df.to_dict("records"),
    }
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(bucket_df)
    print("v31 probability residual physics audit complete")
    print(f"bucket_rows={len(bucket_df)} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
