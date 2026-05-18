"""Train-only multifeature probability model audit for BTC 15m markets.

This probe tests whether a small regularized logistic model can improve the
fair-value prior without sacrificing recurring-market coverage. It deliberately
uses pooled current+v21 train splits only for fitting and EV-floor selection,
then evaluates validation and holdout on both datasets.

Research-only: no orders are submitted and no bot files or live processes are
modified. Any passing row is only a forward-test candidate.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import estimated_order_fee_cents, fmt_cents, fmt_roi
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import OUT_DIR, choose_decision_sides, clean_json, load_side_rows, market_base, pct
from probe_probability_calibration_audit import brier, logit, logloss


REPORT_MD = OUT_DIR / "probability_multifeature_logit_audit_latest.md"
REPORT_JSON = OUT_DIR / "probability_multifeature_logit_audit_latest.json"
SUMMARY_CSV = OUT_DIR / "probability_multifeature_logit_summary_latest.csv"
FIT_CSV = OUT_DIR / "probability_multifeature_logit_fit_latest.csv"

MIN_SECONDS_TO_CLOSE = 120.0
ASK_MAX = 95.0
HIGH_COVERAGE_FLOOR = 0.75
EDGE_FLOORS = [-30.0, -20.0, -15.0, -10.0, -5.0, 0.0, 2.0, 5.0, 10.0, 15.0, 20.0]

FEATURE_SETS = {
    "prob3": [
        ("prob", "book_p_side"),
        ("prob", "brownian_p_rv_15m"),
        ("prob", "brownian_p_rv_30m"),
    ],
    "prob_gap_margin": [
        ("prob", "book_p_side"),
        ("prob", "brownian_p_rv_15m"),
        ("prob", "brownian_p_rv_30m"),
        ("num", "abs_book_rv15_gap"),
        ("num", "margin_per_rv_sigma_15m"),
    ],
    "prob_path_compact": [
        ("prob", "book_p_side"),
        ("prob", "brownian_p_rv_15m"),
        ("prob", "brownian_p_rv_30m"),
        ("prob", "drift_p_5m_rv_15m"),
        ("num", "abs_book_rv15_gap"),
        ("num", "margin_per_rv_sigma_15m"),
        ("num", "adverse_move_15m"),
        ("num", "signed_move_5m"),
        ("num", "seconds_to_close"),
    ],
    "prob_micro_full": [
        ("prob", "book_p_side"),
        ("prob", "brownian_p_rv_15m"),
        ("prob", "brownian_p_rv_30m"),
        ("prob", "drift_p_5m_rv_15m"),
        ("prob", "drift_p_15m_rv_15m"),
        ("num", "abs_book_rv15_gap"),
        ("num", "abs_book_rv30_gap"),
        ("num", "margin_per_rv_sigma_15m"),
        ("num", "margin_per_rv_sigma_30m"),
        ("num", "adverse_move_5m"),
        ("num", "adverse_move_15m"),
        ("num", "signed_move_5m"),
        ("num", "signed_move_15m"),
        ("num", "spread_cents"),
        ("num", "seconds_to_close"),
    ],
}

C_VALUES = [0.05, 0.10, 0.25]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def add_fee_pnl(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    if out.empty:
        for col in ["entry_fee_cents", "entry_cost_cents", "net_pnl_cents", "fee_aware_break_even_p"]:
            out[col] = []
        return out
    out["ask_cents"] = pd.to_numeric(out["ask_cents"], errors="coerce")
    out["entry_fee_cents"] = [estimated_order_fee_cents(ask, 1) for ask in out["ask_cents"].fillna(100.0)]
    out["entry_cost_cents"] = out["ask_cents"] + out["entry_fee_cents"]
    out["net_pnl_cents"] = np.where(out["win"].astype(bool), 100.0 - out["ask_cents"], -out["ask_cents"]) - out["entry_fee_cents"]
    out["fee_aware_break_even_p"] = out["entry_cost_cents"] / 100.0
    return out


def first_market_rows(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return rows
    return (
        rows.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )


def attach_split(rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = market_base(rows)
    out = rows.merge(base[["market", "split"]], on="market", how="inner")
    return base, out


def feature_matrix(rows: pd.DataFrame, feature_specs: List[tuple[str, str]]) -> pd.DataFrame:
    data: Dict[str, Any] = {}
    for kind, col in feature_specs:
        if col in rows.columns:
            values = pd.to_numeric(rows[col], errors="coerce")
        else:
            values = pd.Series(np.nan, index=rows.index)
        if kind == "prob":
            data[f"logit_{col}"] = logit(values.to_numpy())
        else:
            data[col] = values.to_numpy(dtype=float)
    return pd.DataFrame(data, index=rows.index).replace([np.inf, -np.inf], np.nan)


def usable_feature_frame(train_rows: pd.DataFrame, rows: pd.DataFrame, specs: List[tuple[str, str]]) -> tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    train_x = feature_matrix(train_rows, specs)
    all_x = feature_matrix(rows, specs)
    usable = [
        col for col in train_x.columns
        if int(train_x[col].notna().sum()) >= max(20, int(0.25 * len(train_x)))
    ]
    if not usable:
        raise ValueError("no usable features after missingness filter")
    return train_x[usable], all_x[usable], usable


def fit_model(train_x: pd.DataFrame, train_y: pd.Series, c_value: float) -> Pipeline:
    model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "logit",
                LogisticRegression(
                    C=float(c_value),
                    class_weight="balanced",
                    max_iter=1000,
                    solver="lbfgs",
                ),
            ),
        ]
    )
    model.fit(train_x, train_y.astype(bool).astype(int).to_numpy())
    return model


def score_dataset(rows: pd.DataFrame, base: pd.DataFrame, model: Pipeline, x: pd.DataFrame, model_name: str) -> pd.DataFrame:
    out = rows.copy()
    out["p_model"] = model.predict_proba(x)[:, 1]
    chosen = choose_decision_sides(out, "p_model")
    if chosen.empty:
        return chosen
    chosen = chosen[
        pd.to_numeric(chosen["ask_cents"], errors="coerce").le(ASK_MAX)
        & pd.to_numeric(chosen["seconds_to_close"], errors="coerce").ge(MIN_SECONDS_TO_CLOSE)
    ].copy()
    if chosen.empty:
        return chosen
    chosen["model"] = model_name
    chosen = add_fee_pnl(chosen)
    chosen["fair_edge_cents"] = 100.0 * pd.to_numeric(chosen["p_model"], errors="coerce") - chosen["entry_cost_cents"]
    return chosen.sort_values(["market", "entry_dt"]).reset_index(drop=True)


def split_summary(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"].eq(split)]
    part = selected if split == "all" else selected[selected["split"].eq(split)]
    n = int(len(part))
    wins = int(part["win"].astype(bool).sum()) if n else 0
    net = float(pd.to_numeric(part.get("net_pnl_cents"), errors="coerce").sum()) if n else 0.0
    cost = float(pd.to_numeric(part.get("entry_cost_cents"), errors="coerce").sum()) if n else 0.0
    y = part["win"].astype(bool).astype(float).to_numpy() if n else np.asarray([])
    p = part["p_model"].to_numpy() if n else np.asarray([])
    return {
        "base_markets": int(len(base_part)),
        "markets": n,
        "wins": wins,
        "losses": n - wins,
        "accuracy": wins / n if n else None,
        "wilson95_lower": wilson_lower(wins, n),
        "coverage": n / len(base_part) if len(base_part) else None,
        "net_pnl_cents": net,
        "net_roi_on_cost": net / cost if cost else None,
        "median_ask": float(pd.to_numeric(part.get("ask_cents"), errors="coerce").median()) if n else None,
        "brier": brier(y, p) if n else None,
        "logloss": logloss(y, p) if n else None,
    }


def summarize_dataset(dataset: str, model_name: str, edge_floor: float, base: pd.DataFrame, chosen: pd.DataFrame) -> Dict[str, Any]:
    selected = first_market_rows(chosen[chosen["fair_edge_cents"].ge(edge_floor)].copy())
    row: Dict[str, Any] = {"dataset": dataset, "model": model_name, "edge_floor_cents": float(edge_floor)}
    for split in ["all", "train", "validation", "holdout"]:
        metrics = split_summary(base, selected, split)
        for key, value in metrics.items():
            row[f"{split}_{key}"] = value
    row["oos_positive"] = (row["validation_net_pnl_cents"] or 0.0) > 0.0 and (row["holdout_net_pnl_cents"] or 0.0) > 0.0
    row["oos_coverage_pass"] = (
        (row["validation_coverage"] or 0.0) >= HIGH_COVERAGE_FLOOR
        and (row["holdout_coverage"] or 0.0) >= HIGH_COVERAGE_FLOOR
    )
    return row


def choose_floor(summary: pd.DataFrame, model_name: str) -> float | None:
    candidates: List[Dict[str, Any]] = []
    part = summary[summary["model"].eq(model_name)]
    for edge_floor in sorted(part["edge_floor_cents"].unique()):
        cur = part[part["dataset"].eq("current") & part["edge_floor_cents"].eq(edge_floor)]
        v21 = part[part["dataset"].eq("v21") & part["edge_floor_cents"].eq(edge_floor)]
        if cur.empty or v21.empty:
            continue
        cur_row = cur.iloc[0]
        v21_row = v21.iloc[0]
        min_train_cov = min(float(cur_row["train_coverage"] or 0.0), float(v21_row["train_coverage"] or 0.0))
        combined_train_net = float(cur_row["train_net_pnl_cents"] or 0.0) + float(v21_row["train_net_pnl_cents"] or 0.0)
        candidates.append(
            {
                "edge_floor_cents": float(edge_floor),
                "min_train_coverage": min_train_cov,
                "combined_train_net_pnl_cents": combined_train_net,
            }
        )
    eligible = [row for row in candidates if row["min_train_coverage"] >= HIGH_COVERAGE_FLOOR]
    if not eligible:
        return None
    eligible.sort(key=lambda row: (row["combined_train_net_pnl_cents"], row["min_train_coverage"]), reverse=True)
    return float(eligible[0]["edge_floor_cents"])


def run_model(
    model_name: str,
    specs: List[tuple[str, str]],
    c_value: float,
    current_base: pd.DataFrame,
    current_rows: pd.DataFrame,
    v21_base: pd.DataFrame,
    v21_rows: pd.DataFrame,
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    train_rows = pd.concat(
        [current_rows[current_rows["split"].eq("train")], v21_rows[v21_rows["split"].eq("train")]],
        ignore_index=True,
        sort=False,
    )
    all_rows = pd.concat([current_rows.assign(dataset="current"), v21_rows.assign(dataset="v21")], ignore_index=True, sort=False)
    train_x, all_x, feature_names = usable_feature_frame(train_rows, all_rows, specs)
    model = fit_model(train_x, train_rows["win"], c_value)
    all_scored = all_rows.copy()
    all_scored["p_model"] = model.predict_proba(all_x)[:, 1]
    fit_row = {
        "model": model_name,
        "feature_set": model_name.rsplit("_C", 1)[0],
        "c_value": float(c_value),
        "features": ",".join(feature_names),
        "train_rows": int(len(train_rows)),
        "train_logloss": logloss(train_rows["win"].astype(bool).astype(float).to_numpy(), model.predict_proba(train_x)[:, 1]),
    }

    current_x = all_x[all_rows["dataset"].eq("current")].reset_index(drop=True)
    v21_x = all_x[all_rows["dataset"].eq("v21")].reset_index(drop=True)
    current_chosen = score_dataset(current_rows.reset_index(drop=True), current_base, model, current_x, model_name)
    v21_chosen = score_dataset(v21_rows.reset_index(drop=True), v21_base, model, v21_x, model_name)
    rows: List[Dict[str, Any]] = []
    for edge_floor in EDGE_FLOORS:
        rows.append(summarize_dataset("current", model_name, edge_floor, current_base, current_chosen))
        rows.append(summarize_dataset("v21", model_name, edge_floor, v21_base, v21_chosen))
    return rows, fit_row


def fmt_metric(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"{number:.{digits}f}"


def write_report(generated: str, summary: pd.DataFrame, fit_rows: pd.DataFrame, selected_rows: pd.DataFrame) -> None:
    lines = [
        "# Probability Multifeature Logit Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Fits regularized logistic models on pooled current+v21 train rows only.",
        "- Chooses EV floors using train coverage/P&L only, then evaluates validation and holdout.",
        "",
        "## Selected Train Floors",
        "",
        f"Coverage floor: `{pct(HIGH_COVERAGE_FLOOR)}` on train, validation, and holdout.",
        "",
        "| dataset | model | EV floor | val net/cov | holdout net/cov | all net/ROI | OOS pass |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for _, row in selected_rows.sort_values(["model", "dataset"]).iterrows():
        oos_pass = bool(row["oos_positive"]) and bool(row["oos_coverage_pass"])
        lines.append(
            f"| {row['dataset']} | `{row['model']}` | {fmt_cents(row['edge_floor_cents'])} | "
            f"{fmt_cents(row['validation_net_pnl_cents'])}/{pct(row['validation_coverage'])} | "
            f"{fmt_cents(row['holdout_net_pnl_cents'])}/{pct(row['holdout_coverage'])} | "
            f"{fmt_cents(row['all_net_pnl_cents'])}/{fmt_roi(row['all_net_roi_on_cost'])} | {oos_pass} |"
        )

    lines += [
        "",
        "## Fit Summary",
        "",
        "| model | C | train rows | train logloss | features |",
        "|---|---:|---:|---:|---|",
    ]
    for _, row in fit_rows.sort_values(["model"]).iterrows():
        feature_count = len(str(row["features"]).split(",")) if row.get("features") else 0
        lines.append(
            f"| `{row['model']}` | {float(row['c_value']):.2f} | {int(row['train_rows'])} | "
            f"{fmt_metric(row['train_logloss'])} | {feature_count} features |"
        )

    lines += ["", "## Read", ""]
    pass_models: List[str] = []
    for model_name, part in selected_rows.groupby("model", sort=False):
        cur = part[part["dataset"].eq("current")].iloc[0]
        v21 = part[part["dataset"].eq("v21")].iloc[0]
        combined_oos = (
            float(cur["validation_net_pnl_cents"] or 0.0)
            + float(cur["holdout_net_pnl_cents"] or 0.0)
            + float(v21["validation_net_pnl_cents"] or 0.0)
            + float(v21["holdout_net_pnl_cents"] or 0.0)
        )
        oos_pass = bool(cur["oos_positive"]) and bool(cur["oos_coverage_pass"]) and bool(v21["oos_positive"]) and bool(v21["oos_coverage_pass"])
        if oos_pass:
            pass_models.append(model_name)
        lines.append(
            f"- `{model_name}` both-dataset OOS pass/combined OOS net: {oos_pass}/{fmt_cents(combined_oos)}."
        )
    if pass_models:
        lines.append("- Passing models are diagnostic candidates only; promotion still requires strict forward registration.")
    else:
        lines.append("- No multifeature logit model clears positive high-coverage OOS on both datasets.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_base, current_rows = attach_split(load_side_rows())
    v21_base, v21_rows = attach_split(load_v21_side_rows())

    summary_rows: List[Dict[str, Any]] = []
    fit_rows: List[Dict[str, Any]] = []
    for feature_set, specs in FEATURE_SETS.items():
        for c_value in C_VALUES:
            model_name = f"{feature_set}_C{c_value:g}"
            rows, fit = run_model(model_name, specs, c_value, current_base, current_rows, v21_base, v21_rows)
            summary_rows.extend(rows)
            fit_rows.append(fit)

    summary = pd.DataFrame(summary_rows)
    fits = pd.DataFrame(fit_rows)
    selected: List[pd.DataFrame] = []
    for model_name in summary["model"].drop_duplicates():
        floor = choose_floor(summary, model_name)
        if floor is None:
            continue
        selected.append(summary[summary["model"].eq(model_name) & summary["edge_floor_cents"].eq(floor)].copy())
    selected_df = pd.concat(selected, ignore_index=True, sort=False) if selected else pd.DataFrame()

    summary.to_csv(SUMMARY_CSV, index=False)
    fits.to_csv(FIT_CSV, index=False)
    payload = {
        "generated_utc": generated,
        "summary_rows": clean_json_local(summary.to_dict(orient="records")),
        "fit_rows": clean_json_local(fits.to_dict(orient="records")),
        "selected_rows": clean_json_local(selected_df.to_dict(orient="records")),
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_report(generated, summary, fits, selected_df)
    print("Probability multifeature logit audit complete")
    print(f"models={len(fits)} summary_rows={len(summary)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
