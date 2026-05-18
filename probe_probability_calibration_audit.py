"""Train-only calibration audit for BTC 15m probability priors.

The live policies use several probability-like scores as if they were fair
values. This probe tests that assumption directly:

- choose one side per heartbeat using each prior;
- fit a pooled current+v21 train-only logit calibration;
- choose a high-coverage EV floor using train only;
- evaluate calibration and held-to-settlement P&L on validation/holdout.

Research-only: no orders are submitted and no bot files or live processes are
modified. Any passing row is a forward-test candidate, not promotion evidence.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import estimated_order_fee_cents, fmt_cents, fmt_roi
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import OUT_DIR, choose_decision_sides, clean_json, load_side_rows, market_base, pct


REPORT_MD = OUT_DIR / "probability_calibration_audit_latest.md"
REPORT_JSON = OUT_DIR / "probability_calibration_audit_latest.json"
SUMMARY_CSV = OUT_DIR / "probability_calibration_summary_latest.csv"
CALIBRATION_CSV = OUT_DIR / "probability_calibration_fit_latest.csv"

MIN_SECONDS_TO_CLOSE = 120.0
ASK_MAX = 95.0
HIGH_COVERAGE_FLOOR = 0.75
EDGE_FLOORS = [-50.0, -40.0, -30.0, -20.0, -15.0, -10.0, -5.0, 0.0, 2.0, 5.0, 10.0]

MODEL_COLS = [
    ("book", "book_p_side"),
    ("brownian15", "brownian_p_rv_15m"),
    ("brownian30", "brownian_p_rv_30m"),
    ("mean_book_rv15", "score_mean_book_rv15"),
    ("min_book_rv15", "score_min_book_rv15"),
    ("regime_blend", "score_regime_blend"),
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def clamp_prob(values: Any) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=float), 1e-4, 1.0 - 1e-4)


def logit(values: Any) -> np.ndarray:
    p = clamp_prob(values)
    return np.log(p / (1.0 - p))


def sigmoid(values: Any) -> np.ndarray:
    z = np.asarray(values, dtype=float)
    return 1.0 / (1.0 + np.exp(-np.clip(z, -40.0, 40.0)))


def logloss(y: Any, p: Any) -> float | None:
    y_arr = np.asarray(y, dtype=float)
    if y_arr.size == 0:
        return None
    p_arr = clamp_prob(p)
    return float(-(y_arr * np.log(p_arr) + (1.0 - y_arr) * np.log(1.0 - p_arr)).mean())


def brier(y: Any, p: Any) -> float | None:
    y_arr = np.asarray(y, dtype=float)
    if y_arr.size == 0:
        return None
    p_arr = clamp_prob(p)
    return float(np.mean((p_arr - y_arr) ** 2))


def metric_value(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"{number:.{digits}f}"


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


def chosen_rows(side_rows: pd.DataFrame, base: pd.DataFrame, model_name: str, p_col: str) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, p_col)
    if chosen.empty:
        return chosen
    chosen = chosen[
        chosen[p_col].notna()
        & pd.to_numeric(chosen["ask_cents"], errors="coerce").le(ASK_MAX)
        & pd.to_numeric(chosen["seconds_to_close"], errors="coerce").ge(MIN_SECONDS_TO_CLOSE)
    ].copy()
    if chosen.empty:
        return chosen
    chosen["model"] = model_name
    chosen["p_raw"] = pd.to_numeric(chosen[p_col], errors="coerce")
    chosen = add_fee_pnl(chosen)
    return chosen.sort_values(["market", "entry_dt"]).reset_index(drop=True)


def first_market_rows(chosen: pd.DataFrame) -> pd.DataFrame:
    if chosen.empty:
        return chosen
    return (
        chosen.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )


def fit_logit_calibration(train_rows: pd.DataFrame) -> Dict[str, Any]:
    y = train_rows["win"].astype(bool).astype(float).to_numpy()
    x = logit(train_rows["p_raw"].to_numpy())
    raw_loss = logloss(y, train_rows["p_raw"].to_numpy())
    best = {"alpha": 0.0, "beta": 1.0, "train_logloss": raw_loss, "raw_train_logloss": raw_loss}
    for alpha in np.linspace(-2.0, 2.0, 81):
        for beta in np.linspace(0.25, 2.50, 91):
            p = sigmoid(alpha + beta * x)
            loss = logloss(y, p)
            if loss is not None and (best["train_logloss"] is None or loss < float(best["train_logloss"])):
                best = {
                    "alpha": float(alpha),
                    "beta": float(beta),
                    "train_logloss": float(loss),
                    "raw_train_logloss": raw_loss,
                }
    return best


def apply_calibration(rows: pd.DataFrame, calibration: Dict[str, Any]) -> pd.DataFrame:
    out = rows.copy()
    if out.empty:
        out["p_cal"] = []
        out["fair_edge_cents"] = []
        return out
    out["p_raw"] = pd.to_numeric(out["p_raw"], errors="coerce")
    out["p_cal"] = sigmoid(float(calibration["alpha"]) + float(calibration["beta"]) * logit(out["p_raw"].to_numpy()))
    out["fair_edge_cents"] = 100.0 * out["p_cal"] - out["entry_cost_cents"]
    return out


def split_summary(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"].eq(split)]
    part = selected if split == "all" else selected[selected["split"].eq(split)]
    n = int(len(part))
    wins = int(part["win"].astype(bool).sum()) if n else 0
    net = float(pd.to_numeric(part["net_pnl_cents"], errors="coerce").sum()) if n else 0.0
    cost = float(pd.to_numeric(part["entry_cost_cents"], errors="coerce").sum()) if n else 0.0
    y = part["win"].astype(bool).astype(float).to_numpy() if n else np.asarray([])
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
        "median_ask": float(pd.to_numeric(part["ask_cents"], errors="coerce").median()) if n else None,
        "raw_brier": brier(y, part["p_raw"].to_numpy()) if n else None,
        "cal_brier": brier(y, part["p_cal"].to_numpy()) if n else None,
        "raw_logloss": logloss(y, part["p_raw"].to_numpy()) if n else None,
        "cal_logloss": logloss(y, part["p_cal"].to_numpy()) if n else None,
    }


def summarize_dataset(dataset: str, model: str, edge_floor: float, base: pd.DataFrame, rows: pd.DataFrame) -> Dict[str, Any]:
    selected = first_market_rows(rows[rows["fair_edge_cents"].ge(edge_floor)].copy())
    row: Dict[str, Any] = {
        "dataset": dataset,
        "model": model,
        "edge_floor_cents": edge_floor,
    }
    for split in ["all", "train", "validation", "holdout"]:
        metrics = split_summary(base, selected, split)
        for key, value in metrics.items():
            row[f"{split}_{key}"] = value
    row["oos_positive"] = (row["validation_net_pnl_cents"] or 0.0) > 0.0 and (row["holdout_net_pnl_cents"] or 0.0) > 0.0
    row["oos_coverage_pass"] = (row["validation_coverage"] or 0.0) >= HIGH_COVERAGE_FLOOR and (row["holdout_coverage"] or 0.0) >= HIGH_COVERAGE_FLOOR
    return row


def flatten_fit(model: str, calibration: Dict[str, Any], base_rows: pd.DataFrame) -> Dict[str, Any]:
    train = base_rows[base_rows["split"].eq("train")]
    val = base_rows[base_rows["split"].eq("validation")]
    holdout = base_rows[base_rows["split"].eq("holdout")]
    out = {"model": model, **calibration}
    for split_name, frame in [("train", train), ("validation", val), ("holdout", holdout)]:
        y = frame["win"].astype(bool).astype(float).to_numpy()
        out[f"{split_name}_raw_logloss"] = logloss(y, frame["p_raw"].to_numpy())
        out[f"{split_name}_cal_logloss"] = logloss(y, frame["p_cal"].to_numpy())
        out[f"{split_name}_raw_brier"] = brier(y, frame["p_raw"].to_numpy())
        out[f"{split_name}_cal_brier"] = brier(y, frame["p_cal"].to_numpy())
        out[f"{split_name}_rows"] = int(len(frame))
    return out


def train_selected_rows(summary: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for model, part in summary.groupby("model", sort=False):
        merged = part.pivot_table(
            index="edge_floor_cents",
            columns="dataset",
            values=["train_coverage", "train_net_pnl_cents"],
            aggfunc="first",
        )
        candidates: List[Dict[str, Any]] = []
        for edge in sorted(part["edge_floor_cents"].unique()):
            cur = part[(part["edge_floor_cents"].eq(edge)) & part["dataset"].eq("current")]
            v21 = part[(part["edge_floor_cents"].eq(edge)) & part["dataset"].eq("v21")]
            if cur.empty or v21.empty:
                continue
            cur_row = cur.iloc[0]
            v21_row = v21.iloc[0]
            min_train_cov = min(float(cur_row["train_coverage"] or 0.0), float(v21_row["train_coverage"] or 0.0))
            combined_train_net = float(cur_row["train_net_pnl_cents"] or 0.0) + float(v21_row["train_net_pnl_cents"] or 0.0)
            candidates.append(
                {
                    "model": model,
                    "edge_floor_cents": float(edge),
                    "min_train_coverage": min_train_cov,
                    "combined_train_net_pnl_cents": combined_train_net,
                    "train_coverage_pass": min_train_cov >= HIGH_COVERAGE_FLOOR,
                }
            )
        if not candidates:
            continue
        eligible = [row for row in candidates if row["train_coverage_pass"]] or candidates
        chosen = max(eligible, key=lambda row: (row["combined_train_net_pnl_cents"], row["min_train_coverage"]))
        rows.append(chosen)
    return pd.DataFrame(rows)


def write_report(generated: str, fits: pd.DataFrame, summary: pd.DataFrame, train_choices: pd.DataFrame) -> None:
    choice_summary = summary.merge(train_choices[["model", "edge_floor_cents"]], on=["model", "edge_floor_cents"], how="inner")
    lines = [
        "# Probability Calibration Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only calibration audit; no orders are submitted and no bot files or live processes are touched.",
        "- Calibrations are pooled current+v21 train-only logit fits.",
        "- EV floor is selected using train rows only, then evaluated on validation/holdout.",
        "",
        "## Calibration Fits",
        "",
        "| model | alpha | beta | train raw/cal logloss | validation raw/cal logloss | holdout raw/cal logloss |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in fits.sort_values("model").iterrows():
        lines.append(
            f"| `{row['model']}` | {metric_value(row['alpha'], 3)} | {metric_value(row['beta'], 3)} | "
            f"{metric_value(row['train_raw_logloss'])}/{metric_value(row['train_cal_logloss'])} | "
            f"{metric_value(row['validation_raw_logloss'])}/{metric_value(row['validation_cal_logloss'])} | "
            f"{metric_value(row['holdout_raw_logloss'])}/{metric_value(row['holdout_cal_logloss'])} |"
        )

    lines += [
        "",
        "## Train-Selected EV Gates",
        "",
        f"Coverage floor: `{pct(HIGH_COVERAGE_FLOOR)}` on validation and holdout.",
        "",
        "| dataset | model | edge floor | val net/cov | holdout net/cov | all net/ROI | OOS pass |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for _, row in choice_summary.sort_values(["model", "dataset"]).iterrows():
        oos_pass = bool(row["oos_positive"]) and bool(row["oos_coverage_pass"])
        lines.append(
            f"| {row['dataset']} | `{row['model']}` | {fmt_cents(row['edge_floor_cents'])} | "
            f"{fmt_cents(row['validation_net_pnl_cents'])}/{pct(row['validation_coverage'])} | "
            f"{fmt_cents(row['holdout_net_pnl_cents'])}/{pct(row['holdout_coverage'])} | "
            f"{fmt_cents(row['all_net_pnl_cents'])}/{fmt_roi(row['all_net_roi_on_cost'])} | {oos_pass} |"
        )

    lines += ["", "## Read", ""]
    robust: List[str] = []
    for model in sorted(choice_summary["model"].unique()):
        part = choice_summary[choice_summary["model"].eq(model)]
        both_oos = bool((part["oos_positive"] & part["oos_coverage_pass"]).all()) if not part.empty else False
        min_val_cov = float(part["validation_coverage"].min()) if not part.empty else 0.0
        min_holdout_cov = float(part["holdout_coverage"].min()) if not part.empty else 0.0
        combined_oos_net = float(part["validation_net_pnl_cents"].sum() + part["holdout_net_pnl_cents"].sum()) if not part.empty else 0.0
        if both_oos:
            robust.append(model)
        lines.append(
            f"- `{model}` train-selected OOS pass/min val cov/min holdout cov/combined OOS net: "
            f"{both_oos}/{pct(min_val_cov)}/{pct(min_holdout_cov)}/{fmt_cents(combined_oos_net)}."
        )
    if robust:
        lines.append("- Passing calibrated rows are forward-lock candidates only; strict pre-resolution live evidence is still required.")
    else:
        lines.append("- No train-selected calibrated prior clears positive high-coverage OOS on both datasets.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    datasets = {
        "current": (load_side_rows(), None),
        "v21": (load_v21_side_rows(), None),
    }
    bases: Dict[str, pd.DataFrame] = {}
    chosen_by_model: Dict[tuple[str, str], pd.DataFrame] = {}
    for dataset, (side_rows, _) in datasets.items():
        base = market_base(side_rows)
        bases[dataset] = base
        for model_name, p_col in MODEL_COLS:
            chosen_by_model[(dataset, model_name)] = chosen_rows(side_rows, base, model_name, p_col)

    fit_rows: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []
    for model_name, _ in MODEL_COLS:
        base_first = pd.concat(
            [
                first_market_rows(chosen_by_model[(dataset, model_name)]).assign(dataset=dataset)
                for dataset in datasets
            ],
            ignore_index=True,
        )
        train = base_first[base_first["split"].eq("train")].copy()
        calibration = fit_logit_calibration(train)
        calibrated_first = apply_calibration(base_first, calibration)
        fit_rows.append(flatten_fit(model_name, calibration, calibrated_first))
        for dataset in datasets:
            calibrated_rows = apply_calibration(chosen_by_model[(dataset, model_name)], calibration)
            for edge_floor in EDGE_FLOORS:
                summary_rows.append(summarize_dataset(dataset, model_name, edge_floor, bases[dataset], calibrated_rows))

    fits = pd.DataFrame(fit_rows)
    summary = pd.DataFrame(summary_rows)
    train_choices = train_selected_rows(summary)
    fits.to_csv(CALIBRATION_CSV, index=False)
    summary.to_csv(SUMMARY_CSV, index=False)
    fit_stamp = OUT_DIR / f"probability_calibration_fit_{generated}.csv"
    summary_stamp = OUT_DIR / f"probability_calibration_summary_{generated}.csv"
    fits.to_csv(fit_stamp, index=False)
    summary.to_csv(summary_stamp, index=False)
    payload = {
        "generated_utc": generated,
        "high_coverage_floor": HIGH_COVERAGE_FLOOR,
        "min_seconds_to_close": MIN_SECONDS_TO_CLOSE,
        "ask_max": ASK_MAX,
        "fits": clean_json_local(fits.to_dict(orient="records")),
        "summary": clean_json_local(summary.to_dict(orient="records")),
        "train_choices": clean_json_local(train_choices.to_dict(orient="records")),
    }
    json_stamp = OUT_DIR / f"probability_calibration_audit_{generated}.json"
    for path in [REPORT_JSON, json_stamp]:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_report(generated, fits, summary, train_choices)
    md_stamp = OUT_DIR / f"probability_calibration_audit_{generated}.md"
    md_stamp.write_text(REPORT_MD.read_text(encoding="utf-8"), encoding="utf-8")
    print("Probability calibration audit complete")
    print(f"models={len(fits)} summary_rows={len(summary)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
