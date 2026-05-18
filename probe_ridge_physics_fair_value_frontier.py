"""Ridge-calibrated physics fair-value frontier for BTC 15m markets.

The overlay scans found useful explanations but no stable rule: fading impulse
or adverse path memory can help some blocks and damage others. This probe moves
one layer closer to a fair-value model. It fits one small ridge-logistic model
on train-split side rows only, using interpretable side-relative physics:

- book probability,
- Brownian terminal probability,
- short drift probability,
- current margin in realized-volatility units,
- long-path inertia over 15m/30m.

The fitted fair value is then used causally: at each heartbeat the side with
the highest model probability is considered, a fee-aware edge/price gate is
applied, and the first eligible row per market is selected. Results are judged
on current and v21 ledgers, split stability, and block stability.

Research-only: no orders are submitted and no live bot files or processes are
modified.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_impulse_reversal_regime_frontier import BLOCK_MARKETS, MIN_BLOCK_MARKETS, POSITIVE_BLOCK_RATE_FLOOR
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    Policy,
    add_scores,
    choose_decision_sides,
    clean_json,
    gate_mask,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)


REPORT_MD = OUT_DIR / "ridge_physics_fair_value_frontier_latest.md"
REPORT_JSON = OUT_DIR / "ridge_physics_fair_value_frontier_latest.json"
CSV_LATEST = OUT_DIR / "ridge_physics_fair_value_frontier_latest.csv"
BLOCKS_LATEST = OUT_DIR / "ridge_physics_fair_value_blocks_latest.csv"

BASELINE_POLICY = Policy("book_p_side", 0.60, 95.0, 120.0, "margin_rv15>=0")
FEATURES = [
    "logit_book",
    "logit_brownian15",
    "logit_drift5",
    "margin_sigma",
    "long_path_z",
]


@dataclass(frozen=True)
class CalibratedPolicy:
    min_fair_p: float
    min_fee_edge_cents: float
    ask_max: float
    min_seconds_to_close: float

    @property
    def label(self) -> str:
        return (
            f"ridge_physics_fv; p>={self.min_fair_p:g}; "
            f"fee_edge>={self.min_fee_edge_cents:g}c; ask<={self.ask_max:g}; "
            f"sec>={self.min_seconds_to_close:g}"
        )


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt_num(value: Optional[float], digits: int = 4) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.{digits}f}"


def sigmoid(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def logit(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").clip(0.001, 0.999)
    return np.log(values / (1.0 - values))


def coerce_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def add_model_features(rows: pd.DataFrame) -> pd.DataFrame:
    out = add_scores(rows.copy())
    for col in [
        "book_p_side",
        "brownian_p_rv_15m",
        "drift_p_5m_rv_15m",
        "margin_per_rv_sigma_15m",
        "signed_move_15m",
        "signed_move_30m",
        "rv_sigma_t_15m",
        "ask_cents",
        "seconds_to_close",
    ]:
        if col not in out.columns:
            out[col] = np.nan
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["logit_book"] = logit(out["book_p_side"])
    out["logit_brownian15"] = logit(out["brownian_p_rv_15m"])
    out["logit_drift5"] = logit(out["drift_p_5m_rv_15m"])
    out["margin_sigma"] = out["margin_per_rv_sigma_15m"].clip(-5.0, 5.0)
    long_move = out[["signed_move_15m", "signed_move_30m"]].min(axis=1)
    sigma = out["rv_sigma_t_15m"].abs().clip(lower=1.0)
    out["long_path_z"] = (long_move / sigma).clip(-5.0, 5.0)
    return out


def train_frame(current_rows: pd.DataFrame, current_base: pd.DataFrame, v21_rows: pd.DataFrame, v21_base: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for dataset, rows, base in [("current", current_rows, current_base), ("v21", v21_rows, v21_base)]:
        merged = add_model_features(rows).merge(base[["market", "split"]], on="market", how="inner")
        merged["dataset"] = dataset
        frames.append(merged[merged["split"].eq("train")].copy())
    train = pd.concat(frames, ignore_index=True, sort=False)
    train = train.dropna(subset=FEATURES + ["win", "market"]).copy()
    train["y"] = coerce_bool(train["win"]).astype(float)
    market_counts = train.groupby(["dataset", "market"])["market"].transform("count").clip(lower=1)
    train["sample_weight"] = 1.0 / market_counts
    train["sample_weight"] = train["sample_weight"] / train["sample_weight"].mean()
    return train


def fit_ridge_logistic(train: pd.DataFrame, l2: float = 2.0, max_iter: int = 900, lr: float = 0.08) -> Dict[str, Any]:
    x_raw = train[FEATURES].astype(float).to_numpy()
    y = train["y"].astype(float).to_numpy()
    weights = train["sample_weight"].astype(float).to_numpy()
    mu = np.nanmean(x_raw, axis=0)
    sigma = np.nanstd(x_raw, axis=0)
    sigma = np.where(sigma < 1e-6, 1.0, sigma)
    x = (x_raw - mu) / sigma
    x = np.column_stack([np.ones(len(x)), x])
    beta = np.zeros(x.shape[1], dtype=float)
    weight_sum = max(float(weights.sum()), 1.0)
    for _ in range(max_iter):
        p = sigmoid(x @ beta)
        error = (p - y) * weights
        grad = (x.T @ error) / weight_sum
        reg = np.r_[0.0, beta[1:]] * (l2 / weight_sum)
        beta -= lr * (grad + reg)
    p = sigmoid(x @ beta)
    eps = 1e-9
    logloss = float(-(weights * (y * np.log(p + eps) + (1.0 - y) * np.log(1.0 - p + eps))).sum() / weight_sum)
    brier = float((weights * (p - y) ** 2).sum() / weight_sum)
    return {
        "features": FEATURES,
        "mu": mu.tolist(),
        "sigma": sigma.tolist(),
        "beta": beta.tolist(),
        "l2": l2,
        "train_logloss": logloss,
        "train_brier": brier,
        "train_rows": int(len(train)),
        "train_markets": int(train[["dataset", "market"]].drop_duplicates().shape[0]),
    }


def score_rows(rows: pd.DataFrame, model: Dict[str, Any]) -> pd.DataFrame:
    out = add_model_features(rows)
    x_raw = out[FEATURES].astype(float).to_numpy()
    mu = np.asarray(model["mu"], dtype=float)
    sigma = np.asarray(model["sigma"], dtype=float)
    beta = np.asarray(model["beta"], dtype=float)
    x = (x_raw - mu) / sigma
    x = np.column_stack([np.ones(len(x)), x])
    out["ridge_physics_fair_p"] = sigmoid(x @ beta)
    return out


def make_policies() -> List[CalibratedPolicy]:
    policies: List[CalibratedPolicy] = []
    for min_p in [0.50, 0.525, 0.55, 0.575, 0.60]:
        for edge in [-2.0, 0.0, 2.0, 5.0, 8.0]:
            for ask_max in [90.0, 95.0, 98.0]:
                for min_sec in [120.0, 300.0, 600.0]:
                    policies.append(CalibratedPolicy(min_p, edge, ask_max, min_sec))
    return policies


def choose_calibrated(rows: pd.DataFrame) -> pd.DataFrame:
    usable = rows[rows["ridge_physics_fair_p"].notna()].copy()
    if usable.empty:
        return usable
    return (
        usable.sort_values(["decision_key", "ridge_physics_fair_p", "book_p_side"], ascending=[True, False, False])
        .groupby("decision_key", as_index=False, sort=False)
        .first()
        .sort_values(["market", "entry_dt"])
        .reset_index(drop=True)
    )


def select_calibrated(rows: pd.DataFrame, base: pd.DataFrame, policy: CalibratedPolicy) -> pd.DataFrame:
    scored = score_rows(rows, MODEL).merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_calibrated(scored)
    if chosen.empty:
        return enrich_selected(chosen)
    chosen["model_fair_value_cents"] = 100.0 * pd.to_numeric(chosen["ridge_physics_fair_p"], errors="coerce")
    chosen["model_fee_edge_cents"] = chosen["model_fair_value_cents"] - pd.to_numeric(chosen["ask_cents"], errors="coerce") - 1.0
    eligible = chosen[
        pd.to_numeric(chosen["ridge_physics_fair_p"], errors="coerce").ge(policy.min_fair_p)
        & pd.to_numeric(chosen["model_fee_edge_cents"], errors="coerce").ge(policy.min_fee_edge_cents)
        & pd.to_numeric(chosen["ask_cents"], errors="coerce").le(policy.ask_max)
        & pd.to_numeric(chosen["seconds_to_close"], errors="coerce").ge(policy.min_seconds_to_close)
    ].copy()
    if eligible.empty:
        return enrich_selected(eligible)
    selected = (
        eligible.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    selected["candidate"] = policy.label
    selected["action_taken"] = "model"
    return enrich_selected(selected)


def select_baseline(rows: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    merged = add_model_features(rows).merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(merged, BASELINE_POLICY.chooser)
    selected = select_markets_from_chosen(chosen[gate_mask(chosen, BASELINE_POLICY)].copy(), BASELINE_POLICY)
    selected["candidate"] = "book_margin_baseline"
    selected["action_taken"] = "baseline"
    return enrich_selected(selected)


def split_row(prefix: str, metrics: Dict[str, Dict[str, Any]], row: Dict[str, Any]) -> None:
    for split, values in metrics.items():
        for key, value in values.items():
            row[f"{prefix}_{split}_{key}"] = value


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all(
        (metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        for split in ["all", "train", "validation", "holdout"]
    )


def all_splits_positive(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["all", "train", "validation", "holdout"])


def oos_positive(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])


def block_rows(dataset: str, candidate: str, base: pd.DataFrame, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    base_blocks = base.sort_values(["close_dt", "market"]).reset_index(drop=True).copy()
    base_blocks["block_index"] = base_blocks.index // BLOCK_MARKETS
    selected_blocks = selected.drop(columns=["block_index"], errors="ignore").merge(
        base_blocks[["market", "block_index"]], on="market", how="inner"
    )
    rows: List[Dict[str, Any]] = []
    for block_index, block in base_blocks.groupby("block_index", sort=True):
        part = selected_blocks[selected_blocks["block_index"].eq(block_index)]
        n = int(len(part))
        wins = int(part["win"].astype(bool).sum()) if n else 0
        net = float(pd.to_numeric(part.get("net_pnl_cents"), errors="coerce").sum()) if n else 0.0
        cost = float(pd.to_numeric(part.get("entry_cost_cents"), errors="coerce").sum()) if n else 0.0
        base_n = int(len(block))
        coverage = n / base_n if base_n else None
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "block_index": int(block_index),
                "base_markets": base_n,
                "selected_markets": n,
                "coverage": coverage,
                "wins": wins,
                "losses": n - wins,
                "accuracy": wins / n if n else None,
                "net_pnl_cents": net,
                "net_roi_on_cost": net / cost if cost else None,
                "positive_net": net > 0.0,
                "coverage_pass": (coverage or 0.0) >= MARKET_COVERAGE_FLOOR,
            }
        )
    return rows


def block_stability(blocks: pd.DataFrame) -> pd.DataFrame:
    if blocks.empty:
        return pd.DataFrame()
    supported = blocks[blocks["base_markets"].ge(MIN_BLOCK_MARKETS)].copy()
    if supported.empty:
        return pd.DataFrame()
    rows: List[Dict[str, Any]] = []
    for (dataset, candidate), part in supported.groupby(["dataset", "candidate"], sort=True):
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "blocks": int(len(part)),
                "positive_block_rate": float(part["positive_net"].mean()),
                "coverage_block_rate": float(part["coverage_pass"].mean()),
                "worst_block_net_cents": float(part["net_pnl_cents"].min()),
                "median_block_net_cents": float(part["net_pnl_cents"].median()),
            }
        )
    return pd.DataFrame(rows)


def combine(current: pd.DataFrame, v21: pd.DataFrame, stability: pd.DataFrame) -> pd.DataFrame:
    frame = current.merge(v21, on="candidate", suffixes=("_current", "_v21"))
    if not stability.empty:
        stab_rows = []
        for candidate, part in stability.groupby("candidate", sort=True):
            stab_rows.append(
                {
                    "candidate": candidate,
                    "min_positive_block_rate": float(part["positive_block_rate"].min()),
                    "min_coverage_block_rate": float(part["coverage_block_rate"].min()),
                    "worst_block_net_cents": float(part["worst_block_net_cents"].min()),
                }
            )
        frame = frame.merge(pd.DataFrame(stab_rows), on="candidate", how="left")
    else:
        frame["min_positive_block_rate"] = np.nan
        frame["min_coverage_block_rate"] = np.nan
        frame["worst_block_net_cents"] = np.nan
    frame["combined_all_net_pnl_cents"] = (
        pd.to_numeric(frame["all_net_pnl_cents_current"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["all_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
    )
    frame["combined_oos_net_pnl_cents"] = (
        pd.to_numeric(frame["validation_net_pnl_cents_current"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["holdout_net_pnl_cents_current"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["validation_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["holdout_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
    )
    frame["both_coverage_pass"] = frame["coverage_pass_current"].astype(bool) & frame["coverage_pass_v21"].astype(bool)
    frame["both_oos_positive"] = frame["oos_positive_current"].astype(bool) & frame["oos_positive_v21"].astype(bool)
    frame["both_all_splits_positive"] = (
        frame["all_splits_positive_current"].astype(bool) & frame["all_splits_positive_v21"].astype(bool)
    )
    frame["block_stability_pass"] = (
        pd.to_numeric(frame["min_positive_block_rate"], errors="coerce").fillna(0.0).ge(POSITIVE_BLOCK_RATE_FLOOR)
        & pd.to_numeric(frame["min_coverage_block_rate"], errors="coerce").fillna(0.0).ge(POSITIVE_BLOCK_RATE_FLOOR)
    )
    frame["strict_pass"] = (
        frame["both_coverage_pass"]
        & frame["both_oos_positive"]
        & frame["both_all_splits_positive"]
        & frame["block_stability_pass"]
    )
    frame["min_split_coverage"] = frame[["min_split_coverage_current", "min_split_coverage_v21"]].min(axis=1)
    frame["min_oos_edge_cents"] = frame[["min_oos_edge_cents_current", "min_oos_edge_cents_v21"]].min(axis=1)
    return frame.sort_values(
        [
            "strict_pass",
            "both_coverage_pass",
            "both_oos_positive",
            "combined_oos_net_pnl_cents",
            "combined_all_net_pnl_cents",
        ],
        ascending=[False, False, False, False, False],
    ).reset_index(drop=True)


def row_for(dataset: str, candidate: str, metrics: Dict[str, Dict[str, Any]], extra: Dict[str, Any]) -> Dict[str, Any]:
    row: Dict[str, Any] = {"dataset": dataset, "candidate": candidate, **extra}
    for split, values in metrics.items():
        for key, value in values.items():
            row[f"{split}_{key}"] = value
    row["coverage_pass"] = coverage_pass(metrics)
    row["all_splits_positive"] = all_splits_positive(metrics)
    row["oos_positive"] = oos_positive(metrics)
    row["min_split_coverage"] = min((metrics[split]["coverage"] or 0.0) for split in ["train", "validation", "holdout"])
    row["min_oos_edge_cents"] = min(
        (metrics[split]["net_edge_per_selected_cents"] or -100.0) for split in ["validation", "holdout"]
    )
    return row


MODEL: Dict[str, Any] = {}


def scan() -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    global MODEL
    current_side = load_side_rows()
    v21_side = load_v21_side_rows()
    current_base = market_base(add_model_features(current_side))
    v21_base = market_base(add_model_features(v21_side))
    train = train_frame(current_side, current_base, v21_side, v21_base)
    MODEL = fit_ridge_logistic(train)

    policies = make_policies()
    current_rows: List[Dict[str, Any]] = []
    v21_rows: List[Dict[str, Any]] = []
    block_out: List[Dict[str, Any]] = []

    current_baseline = select_baseline(current_side, current_base)
    v21_baseline = select_baseline(v21_side, v21_base)
    for dataset, base, selected, rows_out in [
        ("current", current_base, current_baseline, current_rows),
        ("v21", v21_base, v21_baseline, v21_rows),
    ]:
        rows_out.append(row_for(dataset, "book_margin_baseline", metrics_for(base, selected), {
            "label": BASELINE_POLICY.label,
            "min_fair_p": None,
            "min_fee_edge_cents": None,
            "ask_max": BASELINE_POLICY.ask_max,
            "min_seconds_to_close": BASELINE_POLICY.min_seconds_to_close,
        }))
        block_out.extend(block_rows(dataset, "book_margin_baseline", base, selected))

    for policy in policies:
        current_selected = select_calibrated(current_side, current_base, policy)
        v21_selected = select_calibrated(v21_side, v21_base, policy)
        current_rows.append(row_for("current", policy.label, metrics_for(current_base, current_selected), {
            "label": policy.label,
            "min_fair_p": policy.min_fair_p,
            "min_fee_edge_cents": policy.min_fee_edge_cents,
            "ask_max": policy.ask_max,
            "min_seconds_to_close": policy.min_seconds_to_close,
        }))
        v21_rows.append(row_for("v21", policy.label, metrics_for(v21_base, v21_selected), {
            "label": policy.label,
            "min_fair_p": policy.min_fair_p,
            "min_fee_edge_cents": policy.min_fee_edge_cents,
            "ask_max": policy.ask_max,
            "min_seconds_to_close": policy.min_seconds_to_close,
        }))
        block_out.extend(block_rows("current", policy.label, current_base, current_selected))
        block_out.extend(block_rows("v21", policy.label, v21_base, v21_selected))

    blocks = pd.DataFrame(block_out)
    stability = block_stability(blocks)
    frame = combine(pd.DataFrame(current_rows), pd.DataFrame(v21_rows), stability)
    diagnostics = {
        "current_markets": int(len(current_base)),
        "v21_markets": int(len(v21_base)),
        "policies": int(len(policies) + 1),
        "strict_pass_rows": int(frame["strict_pass"].sum()) if not frame.empty else 0,
        "model": MODEL,
    }
    return frame, blocks, diagnostics


def table_row(row: Dict[str, Any]) -> str:
    return (
        f"| `{row['label_current']}` | {row['strict_pass']} | {fmt_cents(row['combined_all_net_pnl_cents'])} | "
        f"{fmt_cents(row['combined_oos_net_pnl_cents'])} | {pct(row['min_split_coverage'])} | "
        f"{fmt_cents(row['all_net_pnl_cents_current'])}/{fmt_cents(row['all_net_pnl_cents_v21'])} | "
        f"{pct(row['all_accuracy_current'])}/{pct(row['all_accuracy_v21'])} | "
        f"{fmt_cents(row['all_median_ask_current'])}/{fmt_cents(row['all_median_ask_v21'])} | "
        f"{fmt_num(row['min_positive_block_rate'])} | {fmt_cents(row['worst_block_net_cents'])} |"
    )


def write_report(generated: str, frame: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    strict = frame[frame["strict_pass"]]
    model = diagnostics["model"]
    coef_lines = []
    beta = model["beta"]
    for feature, coef in zip(model["features"], beta[1:]):
        coef_lines.append(f"- `{feature}`: {fmt_num(coef)}")
    lines = [
        "# Ridge Physics Fair-Value Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Fits one ridge-logistic fair-value model using only train-split side rows from current+v21.",
        "- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.",
        "",
        "## Diagnostics",
        "",
        f"- Current markets: {diagnostics['current_markets']}",
        f"- V21 markets: {diagnostics['v21_markets']}",
        f"- Candidate policies: {diagnostics['policies']}",
        f"- Strict pass rows: {diagnostics['strict_pass_rows']}",
        f"- Train rows/markets: {model['train_rows']}/{model['train_markets']}",
        f"- Train logloss/Brier: {fmt_num(model['train_logloss'])}/{fmt_num(model['train_brier'])}",
        "",
        "## Model Coefficients",
        "",
        f"- `intercept`: {fmt_num(beta[0])}",
        *coef_lines,
        "",
        "## Top Rows",
        "",
        "| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | median ask current/v21 | min block+ | worst block |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in frame.head(30).iterrows():
        lines.append(table_row(row.to_dict()))
    lines += ["", "## Read", ""]
    if strict.empty:
        lines.append("- No ridge-calibrated fair-value policy clears the strict gate.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict diagnostic row is `{best['label_current']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])}."
        )
        lines.append("- This is post-hoc research and must be forward-locked before any live use.")
    for path in [REPORT_MD, OUT_DIR / f"ridge_physics_fair_value_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, blocks, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    frame.to_csv(OUT_DIR / f"ridge_physics_fair_value_frontier_{generated}.csv", index=False)
    blocks.to_csv(BLOCKS_LATEST, index=False)
    blocks.to_csv(OUT_DIR / f"ridge_physics_fair_value_blocks_{generated}.csv", index=False)
    write_report(generated, frame, diagnostics)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "rows": frame.to_dict("records")}
    for path in [REPORT_JSON, OUT_DIR / f"ridge_physics_fair_value_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Ridge physics fair-value frontier complete")
    print(f"rows={len(frame)}")
    print(f"strict_pass={diagnostics['strict_pass_rows']}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
