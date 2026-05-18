"""v68 regularized physics-logit FV strategy probe.

Research-only. Trains a tiny L2-regularized logistic probability surface on the
train split only, using causal entry-time physics/book features:

- v55 logit probability;
- book-mid logit probability;
- diffusion distance/time z-score;
- strike margin and short-horizon velocities.

The purpose is to test whether a low-dimensional calibrated probability model
can improve FV accuracy without overfitting, then verify whether that accuracy
is actually tradable at 75-80%+ coverage.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import probe_v42_edgehole_latent_fv_strategy as v42
import probe_v47_recross_hazard_fv_strategy as v47
import probe_v55_book_anchor_recross_fv_strategy as v55
from probe_market_interval_80coverage import clean_json
from probe_v31_book_calibrated_probability import logit


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v68_regularized_physics_logit_fv_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v68_regularized_physics_logit_fv_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v68_regularized_physics_logit_fv_strategy_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v68_regularized_physics_logit_fv_selected_trades_latest.csv"

BASE_MODEL = "v55_bookanchor_m10_v20_g05_book_plus2"
BASE_COL = f"{BASE_MODEL}_p_yes_candidate"
C_VALUES = [0.02, 0.05, 0.10, 0.20, 0.50, 1.00]


def model_name(c_value: float) -> str:
    return f"v68_l2_C{str(c_value).replace('.', 'p')}"


def feature_frame(ops: pd.DataFrame, base_p: pd.Series) -> pd.DataFrame:
    book = pd.to_numeric(ops["book_mid_p_yes"], errors="coerce").clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)
    seconds = pd.to_numeric(ops["seconds_to_close"], errors="coerce").fillna(30.0)
    margin = pd.to_numeric(ops["margin_per_rv_sigma_15m"], errors="coerce").fillna(0.0)
    velocity_1m = pd.to_numeric(ops["signed_velocity_dps_1m"], errors="coerce").fillna(0.0)
    velocity_3m = pd.to_numeric(ops["signed_velocity_dps_3m"], errors="coerce").fillna(0.0)
    time_fraction = np.maximum(seconds.to_numpy(dtype=float), 30.0) / 900.0
    diff_z = margin.to_numpy(dtype=float) / np.sqrt(time_fraction)
    out = pd.DataFrame(
        {
            "logit_v55": logit(base_p),
            "logit_book": logit(book),
            "diff_z": diff_z,
            "margin": margin,
            "velocity_1m": velocity_1m,
            "velocity_3m": velocity_3m,
            "sqrt_time": np.sqrt(time_fraction),
            "gap_logit": logit(base_p) - logit(book),
        },
        index=ops.index,
    )
    return out.replace([np.inf, -np.inf], np.nan).fillna(0.0)


def fit_predict(ops: pd.DataFrame, x: pd.DataFrame, c_value: float) -> np.ndarray:
    train = ops["split"].astype(str).eq("train")
    y = pd.to_numeric(ops["outcome_yes"], errors="coerce").fillna(0).astype(int)
    clf = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=c_value, solver="lbfgs", max_iter=1000),
    )
    clf.fit(x.loc[train], y.loc[train])
    return clf.predict_proba(x)[:, 1]


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    out, _, metadata = v55.build_probability_candidates(ops)
    base_p = out[BASE_COL].astype(float).clip(v42.PROB_EPS, 1.0 - v42.PROB_EPS)
    x = feature_frame(out, base_p)
    out[f"{BASE_MODEL}_p_yes_candidate"] = base_p
    candidate_cols = [f"{BASE_MODEL}_p_yes_candidate"]
    variants = []
    for c_value in C_VALUES:
        name = model_name(c_value)
        pred = fit_predict(out, x, c_value)
        col = f"{name}_p_yes_candidate"
        out[col] = np.clip(pred, v42.PROB_EPS, 1.0 - v42.PROB_EPS)
        candidate_cols.append(col)
        variants.append({"name": name, "l2_C": c_value})
    metadata.update(
        {
            "base_model": BASE_MODEL,
            "hypothesis": "low-dimensional train-only regularized logit calibration of v55/book/diffusion/velocity features",
            "features": list(x.columns),
            "variants": variants,
        }
    )
    return out, candidate_cols, metadata


def selected_by_surface(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return summary
    eligible = summary[summary["min_split_coverage"].ge(v42.MIN_SPLIT_COVERAGE)].copy()
    robust = eligible[
        eligible["all_splits_1c_entry_positive"]
        & eligible["positive_1c_days"].eq(eligible["total_days"])
        & eligible["block10_positive"].ge(7)
    ].copy()
    source = robust if not robust.empty else eligible
    return source.sort_values(
        ["all_net_after_fees_1c_entry_dollars", "min_split_net_after_fees_1c_entry_dollars", "block10_positive"],
        ascending=[False, False, False],
    ).head(40)


def write_report(
    summary: pd.DataFrame,
    selected: pd.DataFrame,
    prob_records: list[dict[str, Any]],
    metadata: dict[str, Any],
    candidate_cols: list[str],
) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    eligible = summary[summary["min_split_coverage"].ge(v42.MIN_SPLIT_COVERAGE)].copy() if not summary.empty else summary
    robust = eligible[
        eligible["all_splits_1c_entry_positive"]
        & eligible["positive_1c_days"].eq(eligible["total_days"])
        & eligible["block10_positive"].ge(7)
    ].copy() if not eligible.empty else eligible
    holdout_prob = pd.DataFrame(prob_records)
    holdout_prob = holdout_prob[holdout_prob["split"].eq("holdout")].sort_values(["brier", "logloss"])
    lines = [
        "# v68 Regularized Physics-Logit FV Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only train-split logistic calibration on top of v55/book/physics features.",
        "- Tests probability accuracy and executable 80%+ coverage P&L separately.",
        "- Live bot untouched.",
        "",
        "## Holdout Probability",
        "",
        "| candidate | Brier | logloss | side acc |",
        "|---|---:|---:|---:|",
    ]
    for _, row in holdout_prob.head(20).iterrows():
        lines.append(
            f"| `{row['candidate']}` | {float(row['brier']):.5f} | {float(row['logloss']):.5f} | "
            f"{v42.pct(row['side_accuracy'])} |"
        )
    lines += [
        "",
        "## Selected Strategy Rows",
        "",
        "| model | entry | exit | min cov | min 1c | all 1c | days | block10 | trades |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.head(30).iterrows():
        lines.append(
            f"| `{row['model']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{v42.pct(row['min_split_coverage'])} | "
            f"{v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_trades'])} |"
        )
    lines += ["", "## Read", ""]
    best_cal = holdout_prob.iloc[0] if not holdout_prob.empty else None
    if best_cal is not None:
        lines.append(
            f"- Best holdout calibration is `{best_cal['candidate']}` with Brier {float(best_cal['brier']):.5f} "
            f"and logloss {float(best_cal['logloss']):.5f}."
        )
    if robust.empty:
        lines.append("- No v68 logistic row cleared the tradable robustness gate; accuracy improved but executable edge did not.")
    else:
        best = robust.sort_values(
            ["all_net_after_fees_1c_entry_dollars", "min_split_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best robust row is `{best['model']}` with all fee+1c "
            f"{v42.dollars(best['all_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- Treat v68 as calibration evidence, not a promotion candidate.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "metadata": metadata,
                    "candidate_count": len(candidate_cols),
                    "summary_rows": int(len(summary)),
                    "robust_rows": int(len(robust)),
                    "probability_records": prob_records,
                    "selected": selected.to_dict("records"),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    rows = v47.load_rows()
    ops = v42.opportunity_table(rows)
    ops, candidate_cols, metadata = build_probability_candidates(ops)
    prob_records = v42.probability_metrics(ops, candidate_cols)
    summary, selected_trades = v42.build_strategy(rows, ops, candidate_cols)
    selected = selected_by_surface(summary)
    summary.to_csv(SUMMARY_CSV, index=False)
    if not selected_trades.empty:
        selected_trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected, prob_records, metadata, candidate_cols)
    print("v68 regularized physics-logit FV strategy complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    if not selected.empty:
        best = selected.iloc[0]
        print(
            f"best={best['model']} {best['entry_policy']} {best['exit_policy']} "
            f"min_1c={float(best['min_split_net_after_fees_1c_entry_dollars']):.2f} "
            f"all_1c={float(best['all_net_after_fees_1c_entry_dollars']):.2f} "
            f"coverage={float(best['min_split_coverage']):.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
