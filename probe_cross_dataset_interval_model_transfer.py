"""Cross-dataset learned interval model transfer probe.

This tests whether a small supervised fair-value side model can generalize
across independent live websocket captures while keeping the user's volume
unit: recurring BTC 15-minute markets.

Protocol:
- Build interval side rows for the current heartbeat ledger and the v21 passive
  ticker ledger.
- For each direction, train on the source dataset's chronological train split.
- Score the full source dataset and the other dataset without retraining.
- Evaluate fixed probability/price/time gates; no target labels from the target
  dataset are used for fitting.

This script is research-only. It does not import live bot code, submit orders,
touch bot state, or stop the running bot.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    TARGET_ACCURACY,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)


FEATURE_SETS = {
    "book_physics": [
        "book_p_side",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "drift_p_5m_rv_15m",
        "drift_p_15m_rv_15m",
        "margin_per_rv_sigma_15m",
        "margin_per_rv_sigma_30m",
        "abs_book_rv15_gap",
        "abs_book_rv30_gap",
        "adverse_move_3m",
        "adverse_move_5m",
        "adverse_move_15m",
        "spread_cents",
        "seconds_to_close",
    ],
    "book_physics_price": [
        "book_p_side",
        "ask_cents",
        "spread_cents",
        "seconds_to_close",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "drift_p_5m_rv_15m",
        "margin_per_rv_sigma_15m",
        "adverse_move_15m",
        "abs_book_rv15_gap",
    ],
    "physics_only": [
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "drift_p_5m_rv_15m",
        "drift_p_15m_rv_15m",
        "margin_per_rv_sigma_15m",
        "margin_per_rv_sigma_30m",
        "adverse_move_3m",
        "adverse_move_5m",
        "adverse_move_15m",
        "signed_move_5m",
        "signed_move_15m",
        "seconds_to_close",
    ],
    "path_physics": [
        "book_p_side",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "margin_per_rv_sigma_15m",
        "adverse_move_1m",
        "adverse_move_3m",
        "adverse_move_5m",
        "adverse_move_15m",
        "signed_move_1m",
        "signed_move_3m",
        "signed_move_5m",
        "signed_move_15m",
        "seconds_to_close",
        "spread_cents",
    ],
}

THRESHOLDS = [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95, 0.98]
ASK_CAPS = [90.0, 95.0, 100.0]
MIN_SECONDS = [0.0, 60.0, 120.0]


@dataclass(frozen=True)
class ModelSpec:
    family: str
    param: float

    @property
    def label(self) -> str:
        if self.family == "logit":
            return f"logit_C{self.param:g}"
        return f"gb_leaf_{self.param:g}"


MODEL_SPECS = [
    ModelSpec("logit", 0.03),
    ModelSpec("logit", 0.10),
    ModelSpec("logit", 0.30),
    ModelSpec("gb", 50.00),
]


@dataclass(frozen=True)
class Gate:
    threshold: float
    ask_cap: float
    min_seconds: float

    @property
    def label(self) -> str:
        return f"p>={self.threshold:g}; ask<={self.ask_cap:g}; sec>={self.min_seconds:g}"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.1f}"


def prepare_current() -> tuple[pd.DataFrame, pd.DataFrame]:
    side_rows = load_side_rows()
    base = market_base(side_rows)
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    return base, side_rows


def prepare_v21() -> tuple[pd.DataFrame, pd.DataFrame]:
    side_rows = load_v21_side_rows()
    base = market_base(side_rows)
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    return base, side_rows


def build_model(spec: ModelSpec) -> Pipeline:
    if spec.family == "logit":
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        C=spec.param,
                        solver="liblinear",
                        max_iter=1000,
                        random_state=7,
                    ),
                ),
            ]
        )
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                GradientBoostingClassifier(
                    n_estimators=80,
                    learning_rate=0.05,
                    max_depth=2,
                    min_samples_leaf=int(spec.param),
                    subsample=0.85,
                    random_state=7,
                ),
            ),
        ]
    )


def ensure_features(df: pd.DataFrame, features: List[str]) -> pd.DataFrame:
    out = df.copy()
    for feature in features:
        if feature not in out.columns:
            out[feature] = np.nan
    return out


def score_rows(model: Pipeline, rows: pd.DataFrame, features: List[str]) -> pd.DataFrame:
    out = ensure_features(rows, features)
    out["model_p"] = model.predict_proba(out[features])[:, 1]
    return out


def select_markets(scored: pd.DataFrame, gate: Gate) -> pd.DataFrame:
    eligible = scored[
        scored["model_p"].ge(gate.threshold)
        & scored["ask_cents"].le(gate.ask_cap)
        & scored["seconds_to_close"].ge(gate.min_seconds)
    ].copy()
    if eligible.empty:
        return eligible
    chosen = (
        eligible.sort_values(["decision_key", "model_p", "book_p_side"], ascending=[True, False, False])
        .groupby("decision_key", as_index=False, sort=False)
        .first()
        .sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    chosen["settlement_pnl_cents"] = np.where(chosen["win"], 100.0 - chosen["ask_cents"], -chosen["ask_cents"])
    return chosen


def metric(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"] == split]
    selected_part = selected if split == "all" else selected[selected["split"] == split]
    n = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if n else 0
    total = int(len(base_part))
    stake = float(selected_part["ask_cents"].sum()) if n else 0.0
    pnl = float(selected_part["settlement_pnl_cents"].sum()) if n else 0.0
    return {
        "base_markets": total,
        "markets": n,
        "wins": wins,
        "losses": n - wins,
        "accuracy": wins / n if n else None,
        "coverage": n / total if total else None,
        "wilson95_lower": wilson_lower(wins, n),
        "median_ask": float(selected_part["ask_cents"].median()) if n else None,
        "ask_ge_95": int(selected_part["ask_cents"].ge(95).sum()) if n else 0,
        "ask_eq_100": int(selected_part["ask_cents"].ge(100).sum()) if n else 0,
        "median_seconds_to_close": float(selected_part["seconds_to_close"].median()) if n else None,
        "gross_pnl_cents": pnl,
        "stake_cents": stake,
        "gross_roi": pnl / stake if stake else None,
    }


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def dataset_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
        and all((metrics[split]["accuracy"] or 0.0) >= TARGET_ACCURACY for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def dataset_wilson_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return dataset_pass(metrics) and all(
        (metrics[split]["wilson95_lower"] or 0.0) >= TARGET_ACCURACY
        for split in ["all", "train", "validation", "holdout"]
    )


def source_dev_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all(
        (metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        and (metrics[split]["accuracy"] or 0.0) >= TARGET_ACCURACY
        for split in ["validation", "holdout"]
    )


def nondegenerate(source_metrics: Dict[str, Dict[str, Any]], target_metrics: Dict[str, Dict[str, Any]], gate: Gate) -> bool:
    return (
        gate.ask_cap <= 95.0
        and gate.min_seconds >= 60.0
        and (source_metrics["all"]["median_ask"] or 100.0) <= 90.0
        and (target_metrics["all"]["median_ask"] or 100.0) <= 90.0
        and (source_metrics["all"]["ask_eq_100"] or 0) == 0
        and (target_metrics["all"]["ask_eq_100"] or 0) == 0
    )


def flatten(
    direction: str,
    feature_set: str,
    spec: ModelSpec,
    gate: Gate,
    source_metrics: Dict[str, Dict[str, Any]],
    target_metrics: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    source_pass = dataset_pass(source_metrics)
    target_pass = dataset_pass(target_metrics)
    row: Dict[str, Any] = {
        "direction": direction,
        "feature_set": feature_set,
        "model": spec.label,
        "gate": gate.label,
        "threshold": gate.threshold,
        "ask_cap": gate.ask_cap,
        "min_seconds": gate.min_seconds,
        "source_dataset_pass": source_pass,
        "source_wilson_pass": dataset_wilson_pass(source_metrics),
        "source_dev_pass": source_dev_pass(source_metrics),
        "target_dataset_pass": target_pass,
        "target_wilson_pass": dataset_wilson_pass(target_metrics),
        "transfer_pass": source_pass and target_pass,
        "transfer_wilson_pass": dataset_wilson_pass(source_metrics) and dataset_wilson_pass(target_metrics),
        "nondegenerate": nondegenerate(source_metrics, target_metrics, gate),
    }
    row["min_target_split_accuracy"] = min(target_metrics[split]["accuracy"] or 0.0 for split in ["all", "train", "validation", "holdout"])
    row["min_target_split_coverage"] = min(target_metrics[split]["coverage"] or 0.0 for split in ["all", "train", "validation", "holdout"])
    row["min_source_dev_accuracy"] = min(source_metrics[split]["accuracy"] or 0.0 for split in ["validation", "holdout"])
    row["min_source_dev_coverage"] = min(source_metrics[split]["coverage"] or 0.0 for split in ["validation", "holdout"])
    row["max_all_median_ask"] = max(source_metrics["all"]["median_ask"] or 0.0, target_metrics["all"]["median_ask"] or 0.0)
    for prefix, metrics in [("source", source_metrics), ("target", target_metrics)]:
        for split, metric_row in metrics.items():
            for key, value in metric_row.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["transfer_wilson_pass"]),
        int(row["transfer_pass"]),
        int(row["target_dataset_pass"]),
        int(row["source_dev_pass"]),
        int(row["nondegenerate"]),
        row["min_target_split_accuracy"],
        row["target_all_accuracy"] or 0.0,
        row["min_target_split_coverage"],
        row["target_all_wilson95_lower"] or 0.0,
        -(row["max_all_median_ask"] or 100.0),
        row["target_all_gross_roi"] or -999.0,
    )


def run_direction(
    direction: str,
    source_base: pd.DataFrame,
    source_rows: pd.DataFrame,
    target_base: pd.DataFrame,
    target_rows: pd.DataFrame,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    train_rows = source_rows[source_rows["split"] == "train"].copy()
    if train_rows["win"].nunique() < 2:
        return rows
    gates = [Gate(threshold, ask_cap, min_seconds) for threshold in THRESHOLDS for ask_cap in ASK_CAPS for min_seconds in MIN_SECONDS]
    for feature_set, features in FEATURE_SETS.items():
        train_features = ensure_features(train_rows, features)
        for spec in MODEL_SPECS:
            model = build_model(spec)
            model.fit(train_features[features], train_features["win"].astype(int))
            source_scored = score_rows(model, source_rows, features)
            target_scored = score_rows(model, target_rows, features)
            for gate in gates:
                source_selected = select_markets(source_scored, gate)
                target_selected = select_markets(target_scored, gate)
                rows.append(
                    flatten(
                        direction,
                        feature_set,
                        spec,
                        gate,
                        metrics_for(source_base, source_selected),
                        metrics_for(target_base, target_selected),
                    )
                )
    return rows


def scan() -> tuple[pd.DataFrame, Dict[str, Any]]:
    current_base, current_rows = prepare_current()
    v21_base, v21_rows = prepare_v21()
    rows = []
    rows.extend(run_direction("current_to_v21", current_base, current_rows, v21_base, v21_rows))
    rows.extend(run_direction("v21_to_current", v21_base, v21_rows, current_base, current_rows))
    rows.sort(key=rank_key, reverse=True)
    diagnostics = {
        "current_intervals": int(len(current_base)),
        "current_side_rows": int(len(current_rows)),
        "v21_intervals": int(len(v21_base)),
        "v21_side_rows": int(len(v21_rows)),
        "candidate_rows": int(len(rows)),
        "feature_sets": sorted(FEATURE_SETS),
        "model_specs": [spec.label for spec in MODEL_SPECS],
    }
    return pd.DataFrame(rows), diagnostics


def write_report(path: OUT_DIR.__class__, generated: str, results: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    lines: List[str] = [
        "# Cross-Dataset Interval Model Transfer",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only probe; no orders are submitted and no bot files or live processes are touched.",
        "- Models train on one live websocket capture's chronological train split and are evaluated on the other capture without retraining.",
        "- Volume denominator is recurring BTC 15-minute markets.",
        "- Candidate gates are fixed probability/ask/time thresholds applied after scoring.",
        "",
        "## Data",
        "",
        f"- Current intervals: {diagnostics['current_intervals']}",
        f"- Current side rows: {diagnostics['current_side_rows']}",
        f"- V21 intervals: {diagnostics['v21_intervals']}",
        f"- V21 side rows: {diagnostics['v21_side_rows']}",
        f"- Candidate rows evaluated: {diagnostics['candidate_rows']}",
        f"- Transfer target-pass rows: {int(results['transfer_pass'].sum()) if not results.empty else 0}",
        f"- Transfer Wilson-pass rows: {int(results['transfer_wilson_pass'].sum()) if not results.empty else 0}",
        f"- Nondegenerate transfer target-pass rows: {int((results['transfer_pass'] & results['nondegenerate']).sum()) if not results.empty else 0}",
        "",
        "## Best Transfer Rows",
        "",
        "| rank | direction | model | features | gate | transfer | nondeg | source acc/cov | target acc/cov | target holdout acc/cov | median ask |",
        "|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(results.head(20).to_dict("records"), start=1):
        lines.append(
            f"| {idx} | {row['direction']} | {row['model']} | {row['feature_set']} | `{row['gate']}` | "
            f"{row['transfer_pass']} | {row['nondegenerate']} | "
            f"{pct(row['source_all_accuracy'])}/{pct(row['source_all_coverage'])} | "
            f"{pct(row['target_all_accuracy'])}/{pct(row['target_all_coverage'])} | "
            f"{pct(row['target_holdout_accuracy'])}/{pct(row['target_holdout_coverage'])} | "
            f"{fmt(row['max_all_median_ask'])} |"
        )
    lines += ["", "## Read", ""]
    if results.empty:
        lines.append("No candidate rows were evaluated.")
    elif int(results["transfer_pass"].sum()) > 0:
        lines.append("At least one learned model/gate transfers across datasets at the literal 95% / 80% split target.")
    else:
        lines.append("No learned model/gate transfers across datasets at the 95% accuracy / 80% recurring-market coverage split target.")
    if not results.empty and int((results["transfer_pass"] & results["nondegenerate"]).sum()) == 0:
        lines.append("No nondegenerate learned transfer row clears the target.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    results, diagnostics = scan()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_latest = OUT_DIR / "cross_dataset_interval_model_transfer_latest.csv"
    csv_stamp = OUT_DIR / f"cross_dataset_interval_model_transfer_{generated}.csv"
    json_latest = OUT_DIR / "cross_dataset_interval_model_transfer_latest.json"
    json_stamp = OUT_DIR / f"cross_dataset_interval_model_transfer_{generated}.json"
    md_latest = OUT_DIR / "cross_dataset_interval_model_transfer_latest.md"
    md_stamp = OUT_DIR / f"cross_dataset_interval_model_transfer_{generated}.md"
    results.to_csv(csv_latest, index=False)
    results.to_csv(csv_stamp, index=False)
    write_report(md_latest, generated, results, diagnostics)
    write_report(md_stamp, generated, results, diagnostics)
    summary = {
        "generated_utc": generated,
        "diagnostics": diagnostics,
        "transfer_pass_count": int(results["transfer_pass"].sum()) if not results.empty else 0,
        "transfer_wilson_pass_count": int(results["transfer_wilson_pass"].sum()) if not results.empty else 0,
        "nondegenerate_transfer_pass_count": int((results["transfer_pass"] & results["nondegenerate"]).sum()) if not results.empty else 0,
        "top_rows": results.head(50).to_dict("records"),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(summary), indent=2, sort_keys=True), encoding="utf-8")
    print("Cross-dataset interval model transfer complete")
    print(f"candidate_rows={len(results)} transfer_pass={summary['transfer_pass_count']}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
