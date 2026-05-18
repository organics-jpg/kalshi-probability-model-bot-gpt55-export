"""Chronological book/FV probability calibration probe.

This is a fair-value probability model probe, not a trade scorer. It tests
simple low-parameter Bayesian-observation layers:

- book_mid_probability: raw Kalshi book mid as P(YES),
- book_bias_only: train-set intercept correction to book log-odds,
- book_platt: train-set intercept + slope on book log-odds,
- book_v31_platt: train-set logistic calibration using book and v31 log-odds.
- book_v32_drift3_platt: train-set logistic calibration using book, v32, and
  a YES-oriented 3-minute drift-projected margin.
- book_v33_drift3_platt: train-set logistic calibration using book, v33, and
  a YES-oriented 3-minute drift-projected margin.
- book_v34_drift3_platt: train-set logistic calibration using book, v34, and
  a YES-oriented 3-minute drift-projected margin.
- book_v35_drift3_platt: train-set logistic calibration using book, v35, and
  a YES-oriented 3-minute drift-projected margin.

All calibrators are fit only on the chronological train split and then evaluated
on validation/holdout. No live bot files/processes are touched and no orders are
submitted.
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
from probe_mushroom_v29_fv_surface import PROB_EPS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
PREDICTIONS_PATH = OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_all_heartbeats_latest.csv"
REPORT_MD = OUT_DIR / "v31_book_calibrated_probability_latest.md"
REPORT_JSON = OUT_DIR / "v31_book_calibrated_probability_latest.json"
SUMMARY_CSV = OUT_DIR / "v31_book_calibrated_probability_summary_latest.csv"
PREDICTIONS_CSV = OUT_DIR / "v31_book_calibrated_probability_predictions_latest.csv"
SCALED_FEATURE_EPS = 1e-9


def logit(p: Any) -> np.ndarray:
    p_arr = np.clip(np.asarray(p, dtype=float), PROB_EPS, 1.0 - PROB_EPS)
    return np.log(p_arr / (1.0 - p_arr))


def sigmoid(x: Any) -> np.ndarray:
    x_arr = np.asarray(x, dtype=float)
    pos = x_arr >= 0
    out = np.empty_like(x_arr, dtype=float)
    out[pos] = 1.0 / (1.0 + np.exp(-x_arr[pos]))
    ex = np.exp(x_arr[~pos])
    out[~pos] = ex / (1.0 + ex)
    return out


def metrics(y: np.ndarray, p: np.ndarray) -> dict[str, Any]:
    mask = np.isfinite(p)
    y = np.asarray(y, dtype=float)[mask]
    p = np.clip(np.asarray(p, dtype=float)[mask], PROB_EPS, 1.0 - PROB_EPS)
    if len(p) == 0:
        return {"n": 0, "brier": None, "logloss": None, "side_accuracy": None, "mean_p_yes": None, "yes_rate": None}
    return {
        "n": int(len(p)),
        "brier": float(np.mean((p - y) ** 2)),
        "logloss": float(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)).mean()),
        "side_accuracy": float(((p >= 0.5) == (y >= 0.5)).mean()),
        "mean_p_yes": float(p.mean()),
        "yes_rate": float(y.mean()),
    }


def fit_logistic(x: np.ndarray, y: np.ndarray, *, l2: float = 1.0, fit_slope: bool = True) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    if not fit_slope:
        x = np.zeros((len(y), 0), dtype=float)
    design = np.column_stack([np.ones(len(y), dtype=float), x])
    beta = np.zeros(design.shape[1], dtype=float)
    for _ in range(80):
        z = np.clip(design @ beta, -35.0, 35.0)
        p = sigmoid(z)
        w = np.clip(p * (1.0 - p), 1e-8, None)
        grad = design.T @ (p - y)
        hess = (design.T * w) @ design
        if len(beta) > 1 and l2 > 0:
            grad[1:] += l2 * beta[1:]
            hess[1:, 1:] += l2 * np.eye(len(beta) - 1)
        try:
            step = np.linalg.solve(hess, grad)
        except np.linalg.LinAlgError:
            step = np.linalg.pinv(hess) @ grad
        beta -= step
        if float(np.max(np.abs(step))) < 1e-8:
            break
    return beta


def predict_logistic(beta: np.ndarray, x: np.ndarray, *, fit_slope: bool = True) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    if not fit_slope:
        x = np.zeros((len(x), 0), dtype=float)
    design = np.column_stack([np.ones(len(x), dtype=float), x])
    return sigmoid(np.clip(design @ beta, -35.0, 35.0))


def fit_scaled_logistic(x: np.ndarray, y: np.ndarray, *, l2: float = 1.0) -> dict[str, Any]:
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    means = np.nanmean(x, axis=0)
    scales = np.nanstd(x, axis=0)
    scales = np.where(scales > SCALED_FEATURE_EPS, scales, 1.0)
    z = (x - means) / scales
    beta = fit_logistic(z, y, l2=l2)
    return {"beta": beta.tolist(), "means": means.tolist(), "scales": scales.tolist(), "l2": float(l2)}


def predict_scaled_logistic(model: dict[str, Any], x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    means = np.asarray(model["means"], dtype=float)
    scales = np.asarray(model["scales"], dtype=float)
    beta = np.asarray(model["beta"], dtype=float)
    z = (x - means) / scales
    return predict_logistic(beta, z)


def opportunity_rows(rows: pd.DataFrame) -> pd.DataFrame:
    base = rows.drop_duplicates("opportunity_key").copy()
    piv = rows.pivot_table(
        index="opportunity_key",
        columns="side",
        values=["ask_cents", "bid_cents", "book_mid_cents"],
        aggfunc="first",
    )
    piv.columns = [f"{side}_{field}" for field, side in piv.columns]
    base = base.merge(piv, left_on="opportunity_key", right_index=True, how="left")
    rename = {
        "yes_book_mid_cents": "yes_mid",
        "no_book_mid_cents": "no_mid",
    }
    base = base.rename(columns=rename)
    for col in [
        "yes_mid",
        "no_mid",
        "yes_ask_cents",
        "no_ask_cents",
        "yes_bid_cents",
        "no_bid_cents",
        "seconds_to_close",
        "v31_avg90_final60_exact_p_yes",
        "v32_avg110_final60_exact_p_yes",
        "v33_antipersist3_p_yes",
        "v34_material_antipersist3_p_yes",
        "v35_h150_t102_antipersist3_p_yes",
        "v28_live_surface_p_yes",
        "side_sign",
        "drift_projected_margin_3m",
    ]:
        if col in base.columns:
            base[col] = pd.to_numeric(base[col], errors="coerce")
    denom = base["yes_mid"] + base["no_mid"]
    base["book_p_yes"] = base["yes_mid"] / denom
    base["v31_p_yes"] = base["v31_avg90_final60_exact_p_yes"]
    base["v32_p_yes"] = base["v32_avg110_final60_exact_p_yes"]
    base["v33_p_yes"] = base["v33_antipersist3_p_yes"]
    base["v34_p_yes"] = base["v34_material_antipersist3_p_yes"]
    base["v35_p_yes"] = base["v35_h150_t102_antipersist3_p_yes"]
    base["v28_p_yes"] = base["v28_live_surface_p_yes"]
    base["yes_drift_projected_margin_3m"] = base["drift_projected_margin_3m"] * base["side_sign"]
    base["spread_sum_cents"] = (base["yes_ask_cents"] - base["yes_bid_cents"]) + (base["no_ask_cents"] - base["no_bid_cents"])
    base["log_time_to_close"] = np.log(np.clip(base["seconds_to_close"], 1.0, None) / 900.0)
    base["outcome_yes"] = base["outcome"].astype(str).str.lower().eq("yes").astype(float)
    base = base.dropna(
        subset=[
            "book_p_yes",
            "v31_p_yes",
            "v32_p_yes",
            "v33_p_yes",
            "v34_p_yes",
            "v35_p_yes",
            "v28_p_yes",
            "outcome_yes",
            "split",
            "spread_sum_cents",
            "log_time_to_close",
            "yes_drift_projected_margin_3m",
        ]
    ).copy()
    return base.reset_index(drop=True)


def build_models(ops: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    train = ops[ops["split"].astype(str).eq("train")].copy()
    if train.empty:
        raise SystemExit("No train rows available for calibrated probability probe.")

    train_y = train["outcome_yes"].to_numpy(dtype=float)
    train_book_logit = logit(train["book_p_yes"])
    train_v31_logit = logit(train["v31_p_yes"])
    train_v32_logit = logit(train["v32_p_yes"])
    train_v33_logit = logit(train["v33_p_yes"])
    train_v34_logit = logit(train["v34_p_yes"])
    train_v35_logit = logit(train["v35_p_yes"])
    train_log_time = train["log_time_to_close"].to_numpy(dtype=float)
    train_spread = (train["spread_sum_cents"].to_numpy(dtype=float) / 100.0)
    train_abs_book = np.abs(train_book_logit)
    train_yes_drift3 = train["yes_drift_projected_margin_3m"].to_numpy(dtype=float)

    coefs = {
        "book_bias_only": fit_logistic(train_book_logit, train_y, fit_slope=False).tolist(),
        "book_platt": fit_logistic(train_book_logit, train_y, l2=1.0).tolist(),
        "book_v31_platt": fit_logistic(np.column_stack([train_book_logit, train_v31_logit]), train_y, l2=1.0).tolist(),
        "book_v32_platt": fit_logistic(np.column_stack([train_book_logit, train_v32_logit]), train_y, l2=1.0).tolist(),
        "book_v33_platt": fit_logistic(np.column_stack([train_book_logit, train_v33_logit]), train_y, l2=1.0).tolist(),
        "book_v34_platt": fit_logistic(np.column_stack([train_book_logit, train_v34_logit]), train_y, l2=1.0).tolist(),
        "book_v35_platt": fit_logistic(np.column_stack([train_book_logit, train_v35_logit]), train_y, l2=1.0).tolist(),
        "book_v31_time_platt": fit_logistic(
            np.column_stack([train_book_logit, train_v31_logit, train_log_time]),
            train_y,
            l2=3.0,
        ).tolist(),
        "book_v31_drift3_platt": fit_scaled_logistic(
            np.column_stack([train_book_logit, train_v31_logit, train_yes_drift3]),
            train_y,
            l2=0.3,
        ),
        "book_v32_drift3_platt": fit_scaled_logistic(
            np.column_stack([train_book_logit, train_v32_logit, train_yes_drift3]),
            train_y,
            l2=0.3,
        ),
        "book_v33_drift3_platt": fit_scaled_logistic(
            np.column_stack([train_book_logit, train_v33_logit, train_yes_drift3]),
            train_y,
            l2=0.3,
        ),
        "book_v34_drift3_platt": fit_scaled_logistic(
            np.column_stack([train_book_logit, train_v34_logit, train_yes_drift3]),
            train_y,
            l2=0.3,
        ),
        "book_v35_drift3_platt": fit_scaled_logistic(
            np.column_stack([train_book_logit, train_v35_logit, train_yes_drift3]),
            train_y,
            l2=0.3,
        ),
        "book_time_v32drift85": {
            "book_v31_time_platt_logit_weight": 0.15,
            "book_v32_drift3_platt_logit_weight": 0.85,
        },
        "book_time_v33drift85": {
            "book_v31_time_platt_logit_weight": 0.15,
            "book_v33_drift3_platt_logit_weight": 0.85,
        },
        "book_time_v34drift85": {
            "book_v31_time_platt_logit_weight": 0.15,
            "book_v34_drift3_platt_logit_weight": 0.85,
        },
        "book_time_v35drift85": {
            "book_v31_time_platt_logit_weight": 0.15,
            "book_v35_drift3_platt_logit_weight": 0.85,
        },
        "book_v31_micro_platt": fit_logistic(
            np.column_stack([train_book_logit, train_v31_logit, train_log_time, train_spread, train_abs_book]),
            train_y,
            l2=10.0,
        ).tolist(),
    }

    out = ops.copy()
    book_logit_all = logit(out["book_p_yes"])
    v31_logit_all = logit(out["v31_p_yes"])
    v32_logit_all = logit(out["v32_p_yes"])
    v33_logit_all = logit(out["v33_p_yes"])
    v34_logit_all = logit(out["v34_p_yes"])
    v35_logit_all = logit(out["v35_p_yes"])
    log_time_all = out["log_time_to_close"].to_numpy(dtype=float)
    spread_all = out["spread_sum_cents"].to_numpy(dtype=float) / 100.0
    abs_book_all = np.abs(book_logit_all)
    yes_drift3_all = out["yes_drift_projected_margin_3m"].to_numpy(dtype=float)
    out["book_mid_probability_p_yes"] = out["book_p_yes"]
    out["v31_probability_p_yes"] = out["v31_p_yes"]
    out["v32_probability_p_yes"] = out["v32_p_yes"]
    out["v33_probability_p_yes"] = out["v33_p_yes"]
    out["v34_probability_p_yes"] = out["v34_p_yes"]
    out["v35_probability_p_yes"] = out["v35_p_yes"]
    out["v28_live_surface_p_yes_copy"] = out["v28_p_yes"]
    out["book_bias_only_p_yes"] = predict_logistic(np.asarray(coefs["book_bias_only"], dtype=float), book_logit_all, fit_slope=False)
    out["book_platt_p_yes"] = predict_logistic(np.asarray(coefs["book_platt"], dtype=float), book_logit_all)
    out["book_v31_platt_p_yes"] = predict_logistic(
        np.asarray(coefs["book_v31_platt"], dtype=float),
        np.column_stack([book_logit_all, v31_logit_all]),
    )
    out["book_v32_platt_p_yes"] = predict_logistic(
        np.asarray(coefs["book_v32_platt"], dtype=float),
        np.column_stack([book_logit_all, v32_logit_all]),
    )
    out["book_v33_platt_p_yes"] = predict_logistic(
        np.asarray(coefs["book_v33_platt"], dtype=float),
        np.column_stack([book_logit_all, v33_logit_all]),
    )
    out["book_v34_platt_p_yes"] = predict_logistic(
        np.asarray(coefs["book_v34_platt"], dtype=float),
        np.column_stack([book_logit_all, v34_logit_all]),
    )
    out["book_v35_platt_p_yes"] = predict_logistic(
        np.asarray(coefs["book_v35_platt"], dtype=float),
        np.column_stack([book_logit_all, v35_logit_all]),
    )
    out["book_v31_time_platt_p_yes"] = predict_logistic(
        np.asarray(coefs["book_v31_time_platt"], dtype=float),
        np.column_stack([book_logit_all, v31_logit_all, log_time_all]),
    )
    out["book_v31_drift3_platt_p_yes"] = predict_scaled_logistic(
        coefs["book_v31_drift3_platt"],
        np.column_stack([book_logit_all, v31_logit_all, yes_drift3_all]),
    )
    out["book_v32_drift3_platt_p_yes"] = predict_scaled_logistic(
        coefs["book_v32_drift3_platt"],
        np.column_stack([book_logit_all, v32_logit_all, yes_drift3_all]),
    )
    out["book_v33_drift3_platt_p_yes"] = predict_scaled_logistic(
        coefs["book_v33_drift3_platt"],
        np.column_stack([book_logit_all, v33_logit_all, yes_drift3_all]),
    )
    out["book_v34_drift3_platt_p_yes"] = predict_scaled_logistic(
        coefs["book_v34_drift3_platt"],
        np.column_stack([book_logit_all, v34_logit_all, yes_drift3_all]),
    )
    out["book_v35_drift3_platt_p_yes"] = predict_scaled_logistic(
        coefs["book_v35_drift3_platt"],
        np.column_stack([book_logit_all, v35_logit_all, yes_drift3_all]),
    )
    blend = coefs["book_time_v32drift85"]
    out["book_time_v32drift85_p_yes"] = sigmoid(
        blend["book_v31_time_platt_logit_weight"] * logit(out["book_v31_time_platt_p_yes"])
        + blend["book_v32_drift3_platt_logit_weight"] * logit(out["book_v32_drift3_platt_p_yes"])
    )
    blend = coefs["book_time_v33drift85"]
    out["book_time_v33drift85_p_yes"] = sigmoid(
        blend["book_v31_time_platt_logit_weight"] * logit(out["book_v31_time_platt_p_yes"])
        + blend["book_v33_drift3_platt_logit_weight"] * logit(out["book_v33_drift3_platt_p_yes"])
    )
    blend = coefs["book_time_v34drift85"]
    out["book_time_v34drift85_p_yes"] = sigmoid(
        blend["book_v31_time_platt_logit_weight"] * logit(out["book_v31_time_platt_p_yes"])
        + blend["book_v34_drift3_platt_logit_weight"] * logit(out["book_v34_drift3_platt_p_yes"])
    )
    blend = coefs["book_time_v35drift85"]
    out["book_time_v35drift85_p_yes"] = sigmoid(
        blend["book_v31_time_platt_logit_weight"] * logit(out["book_v31_time_platt_p_yes"])
        + blend["book_v35_drift3_platt_logit_weight"] * logit(out["book_v35_drift3_platt_p_yes"])
    )
    out["book_v31_micro_platt_p_yes"] = predict_logistic(
        np.asarray(coefs["book_v31_micro_platt"], dtype=float),
        np.column_stack([book_logit_all, v31_logit_all, log_time_all, spread_all, abs_book_all]),
    )
    return out, coefs


def summarize(preds: pd.DataFrame) -> pd.DataFrame:
    models = [
        ("v28_live_surface", "v28_live_surface_p_yes_copy"),
        ("v31_probability", "v31_probability_p_yes"),
        ("v32_probability", "v32_probability_p_yes"),
        ("v33_probability", "v33_probability_p_yes"),
        ("v34_probability", "v34_probability_p_yes"),
        ("v35_probability", "v35_probability_p_yes"),
        ("book_mid_probability", "book_mid_probability_p_yes"),
        ("book_bias_only", "book_bias_only_p_yes"),
        ("book_platt", "book_platt_p_yes"),
        ("book_v31_platt", "book_v31_platt_p_yes"),
        ("book_v32_platt", "book_v32_platt_p_yes"),
        ("book_v33_platt", "book_v33_platt_p_yes"),
        ("book_v34_platt", "book_v34_platt_p_yes"),
        ("book_v35_platt", "book_v35_platt_p_yes"),
        ("book_v31_time_platt", "book_v31_time_platt_p_yes"),
        ("book_v31_drift3_platt", "book_v31_drift3_platt_p_yes"),
        ("book_v32_drift3_platt", "book_v32_drift3_platt_p_yes"),
        ("book_v33_drift3_platt", "book_v33_drift3_platt_p_yes"),
        ("book_v34_drift3_platt", "book_v34_drift3_platt_p_yes"),
        ("book_v35_drift3_platt", "book_v35_drift3_platt_p_yes"),
        ("book_time_v32drift85", "book_time_v32drift85_p_yes"),
        ("book_time_v33drift85", "book_time_v33drift85_p_yes"),
        ("book_time_v34drift85", "book_time_v34drift85_p_yes"),
        ("book_time_v35drift85", "book_time_v35drift85_p_yes"),
        ("book_v31_micro_platt", "book_v31_micro_platt_p_yes"),
    ]
    rows: list[dict[str, Any]] = []
    y_all = preds["outcome_yes"].to_numpy(dtype=float)
    for name, col in models:
        p_all = preds[col].to_numpy(dtype=float)
        for split in ["all", "train", "validation", "holdout"]:
            mask = np.ones(len(preds), dtype=bool) if split == "all" else preds["split"].astype(str).eq(split).to_numpy()
            rows.append({"model": name, "split": split, **metrics(y_all[mask], p_all[mask])})
    return pd.DataFrame(rows)


def write_report(summary: pd.DataFrame, coefs: dict[str, Any]) -> None:
    holdout = summary[summary["split"].eq("holdout")].sort_values("brier")
    validation = summary[summary["split"].eq("validation")].sort_values("brier")
    best = holdout.iloc[0]
    lines = [
        "# Book/FV Calibrated Probability",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope",
        "",
        "- Chronological train-only calibration of book/FV probability layers.",
        "- Probability quality only; not a trade scorer and not ask-crossing edge proof.",
        "- No live bot code/process or orders are touched.",
        "",
        "## Coefficients",
        "",
    ]
    for name, beta in coefs.items():
        if isinstance(beta, dict):
            rounded = {
                key: [round(float(x), 6) for x in value]
                if isinstance(value, list)
                else round(float(value), 6)
                for key, value in beta.items()
            }
            lines.append(f"- `{name}`: `{rounded}`")
        else:
            lines.append(f"- `{name}`: `{[round(float(x), 6) for x in beta]}`")
    lines += [
        "",
        "## Holdout",
        "",
        "| model | n | Brier | logloss | side acc | mean p_yes | yes rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in holdout.iterrows():
        lines.append(
            f"| `{row['model']}` | {int(row['n'])} | {row['brier']:.5f} | {row['logloss']:.5f} | "
            f"{pct(row['side_accuracy'])} | {pct(row['mean_p_yes'])} | {pct(row['yes_rate'])} |"
        )
    lines += [
        "",
        "## Validation",
        "",
        "| model | n | Brier | logloss | side acc | mean p_yes | yes rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in validation.iterrows():
        lines.append(
            f"| `{row['model']}` | {int(row['n'])} | {row['brier']:.5f} | {row['logloss']:.5f} | "
            f"{pct(row['side_accuracy'])} | {pct(row['mean_p_yes'])} | {pct(row['yes_rate'])} |"
        )
    lines += [
        "",
        "## Read",
        "",
        f"- Best holdout model: `{best['model']}` at Brier/logloss {best['brier']:.5f}/{best['logloss']:.5f}.",
        "- If calibrated book beats raw book on validation but not holdout, treat it as unstable and do not promote.",
        "- If the physics coefficient is small or negative in a book/FV posterior, current physics adds little beyond book once book is observed.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not PREDICTIONS_PATH.exists():
        raise SystemExit(f"Missing predictions file: {PREDICTIONS_PATH}")
    rows = pd.read_csv(PREDICTIONS_PATH, low_memory=False)
    ops = opportunity_rows(rows)
    preds, coefs = build_models(ops)
    summary = summarize(preds)
    preds.to_csv(PREDICTIONS_CSV, index=False)
    summary.to_csv(SUMMARY_CSV, index=False)
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "predictions_path": str(PREDICTIONS_PATH),
        "coefficients": coefs,
        "summary": summary.to_dict("records"),
    }
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(summary, coefs)
    print("v31 book calibrated probability complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
