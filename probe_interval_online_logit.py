"""Research-only chronological logistic fair-value interval probe.

This tests whether a simple learned fair-value side scorer can improve the
recurring BTC 15-minute interval frontier without future leakage.

Protocol:
- Split markets chronologically into train / validation / holdout.
- Train logistic models on side rows from train markets only.
- Pick thresholds using train-market performance only.
- Apply the fixed model and thresholds to validation and holdout markets.

No bot logic is imported or modified.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
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
    "physics_no_book_price": [
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
}

CS = [0.05, 0.10, 0.30, 1.0]
PROB_THRESHOLDS = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
ASK_CAPS = [90.0, 95.0, 100.0]
MIN_SECONDS = [0.0, 60.0, 120.0, 240.0]


@dataclass(frozen=True)
class Candidate:
    feature_set: str
    c_value: float
    prob_threshold: float
    ask_cap: float
    min_seconds: float

    @property
    def label(self) -> str:
        return (
            f"{self.feature_set}; C={self.c_value:g}; p>={self.prob_threshold:g}; "
            f"ask<={self.ask_cap:g}; sec>={self.min_seconds:g}"
        )


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def build_model(c_value: float) -> Pipeline:
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "logit",
                LogisticRegression(
                    C=c_value,
                    penalty="l2",
                    solver="liblinear",
                    max_iter=1000,
                    random_state=7,
                ),
            ),
        ]
    )


def prepare_rows() -> tuple[pd.DataFrame, pd.DataFrame]:
    side_rows = load_side_rows()
    base = market_base(side_rows)
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    return base, side_rows


def predict_frame(model: Pipeline, rows: pd.DataFrame, features: List[str]) -> pd.DataFrame:
    out = rows.copy()
    for feature in features:
        if feature not in out.columns:
            out[feature] = np.nan
    out["model_p"] = model.predict_proba(out[features])[:, 1]
    return out


def select_markets(scored: pd.DataFrame, candidate: Candidate) -> pd.DataFrame:
    eligible = scored[
        scored["model_p"].ge(candidate.prob_threshold)
        & scored["ask_cents"].le(candidate.ask_cap)
        & scored["seconds_to_close"].ge(candidate.min_seconds)
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


def split_metric(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"] == split]
    selected_part = selected if split == "all" else selected[selected["split"] == split]
    rows = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if rows else 0
    losses = rows - wins
    pnl = float(selected_part["settlement_pnl_cents"].sum()) if rows else 0.0
    return {
        "base_markets": int(len(base_part)),
        "markets": rows,
        "wins": wins,
        "losses": losses,
        "accuracy": wins / rows if rows else None,
        "coverage": rows / len(base_part) if len(base_part) else None,
        "wilson95_lower": wilson_lower(wins, rows),
        "gross_pnl_cents": pnl,
        "median_ask": float(selected_part["ask_cents"].median()) if rows else None,
        "median_seconds_to_close": float(selected_part["seconds_to_close"].median()) if rows else None,
    }


def target_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all(
        (metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        and (metrics[split]["accuracy"] or 0.0) >= TARGET_ACCURACY
        for split in ["all", "train", "validation", "holdout"]
    )


def wilson_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return target_pass(metrics) and all(
        (metrics[split]["wilson95_lower"] or 0.0) >= TARGET_ACCURACY
        for split in ["all", "train", "validation", "holdout"]
    )


def flatten(candidate: Candidate, metrics: Dict[str, Dict[str, Any]], train_selected_candidate: bool) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "label": candidate.label,
        "feature_set": candidate.feature_set,
        "c_value": candidate.c_value,
        "prob_threshold": candidate.prob_threshold,
        "ask_cap": candidate.ask_cap,
        "min_seconds": candidate.min_seconds,
        "target_pass": target_pass(metrics),
        "wilson_pass": wilson_pass(metrics),
        "train_selected_candidate": train_selected_candidate,
    }
    row["min_test_accuracy"] = min(metrics["validation"]["accuracy"] or 0.0, metrics["holdout"]["accuracy"] or 0.0)
    row["min_test_coverage"] = min(metrics["validation"]["coverage"] or 0.0, metrics["holdout"]["coverage"] or 0.0)
    row["min_test_wilson"] = min(metrics["validation"]["wilson95_lower"] or 0.0, metrics["holdout"]["wilson95_lower"] or 0.0)
    for split, metric in metrics.items():
        for key, value in metric.items():
            row[f"{split}_{key}"] = value
    return row


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["wilson_pass"]),
        int(row["target_pass"]),
        int(row["train_selected_candidate"]),
        row["min_test_accuracy"],
        row["all_accuracy"] or 0.0,
        row["min_test_coverage"],
        row["min_test_wilson"],
        -(row["all_median_ask"] or 100.0),
    )


def train_pick_key(row: Dict[str, Any]) -> tuple:
    train_acc = row["train_accuracy"] or 0.0
    train_cov = row["train_coverage"] or 0.0
    return (
        int(train_cov >= MARKET_COVERAGE_FLOOR),
        train_acc,
        train_cov,
        -(row["train_median_ask"] or 100.0),
        row["train_median_seconds_to_close"] or 0.0,
    )


def scan(base: pd.DataFrame, side_rows: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    train_rows = side_rows[side_rows["split"] == "train"].copy()
    if train_rows["win"].nunique() < 2:
        raise SystemExit("Training split does not contain both classes")

    for feature_set, features in FEATURE_SETS.items():
        for c_value in CS:
            model = build_model(c_value)
            for feature in features:
                if feature not in train_rows.columns:
                    train_rows[feature] = np.nan
            model.fit(train_rows[features], train_rows["win"].astype(int))
            scored = predict_frame(model, side_rows, features)

            candidate_rows: List[Dict[str, Any]] = []
            candidate_pairs: List[tuple[Candidate, Dict[str, Dict[str, Any]]]] = []
            for threshold in PROB_THRESHOLDS:
                for ask_cap in ASK_CAPS:
                    for min_seconds in MIN_SECONDS:
                        candidate = Candidate(feature_set, c_value, threshold, ask_cap, min_seconds)
                        selected = select_markets(scored, candidate)
                        metrics = {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}
                        row = flatten(candidate, metrics, False)
                        candidate_rows.append(row)
                        candidate_pairs.append((candidate, metrics))

            train_choice = max(candidate_rows, key=train_pick_key)
            train_choice_label = train_choice["label"]
            for candidate, metrics in candidate_pairs:
                rows.append(flatten(candidate, metrics, candidate.label == train_choice_label))

    rows.sort(key=rank_key, reverse=True)
    return pd.DataFrame(rows)


def block_needed(markets: int, wins: int) -> Optional[int]:
    if markets <= 0:
        return None
    if wins / markets >= TARGET_ACCURACY:
        return 0
    max_markets_at_target = math.floor(wins / TARGET_ACCURACY)
    return max(0, markets - max_markets_at_target)


def write_report(path: OUT_DIR.__class__, generated: str, base: pd.DataFrame, results: pd.DataFrame) -> None:
    lines: List[str] = []
    lines.append("# Chronological Interval Logistic Probe")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Research-only probe; no orders are submitted and no bot files are modified.")
    lines.append("- Models train only on the chronological train split.")
    lines.append("- Thresholds are picked from train-market behavior; validation and holdout are forward checks.")
    lines.append("- Unit of volume is the recurring BTC 15-minute market interval.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Resolved intervals: {len(base)}")
    lines.append(f"- Train / validation / holdout: {int((base['split'] == 'train').sum())} / {int((base['split'] == 'validation').sum())} / {int((base['split'] == 'holdout').sum())}")
    lines.append(f"- Candidate policies scanned: {len(results)}")
    lines.append(f"- Target-pass policies: {int(results['target_pass'].sum())}")
    lines.append(f"- Wilson-pass policies: {int(results['wilson_pass'].sum())}")
    lines.append("")

    def table(title: str, frame: pd.DataFrame, n: int = 20) -> None:
        lines.append(title)
        lines.append("")
        if frame.empty:
            lines.append("_No rows._")
            lines.append("")
            return
        lines.append(
            "| rank | policy | all acc | all cov | val acc | val cov | holdout acc | holdout cov | val Wilson | holdout Wilson | train-picked | target | Wilson pass |"
        )
        lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|")
        for idx, row in enumerate(frame.head(n).to_dict("records"), start=1):
            lines.append(
                f"| {idx} | `{row['label']}` | {pct(row['all_accuracy'])} | {pct(row['all_coverage'])} | "
                f"{pct(row['validation_accuracy'])} | {pct(row['validation_coverage'])} | "
                f"{pct(row['holdout_accuracy'])} | {pct(row['holdout_coverage'])} | "
                f"{pct(row['validation_wilson95_lower'])} | {pct(row['holdout_wilson95_lower'])} | "
                f"{row['train_selected_candidate']} | {row['target_pass']} | {row['wilson_pass']} |"
            )
        lines.append("")

    table("## Top Policies", results)
    table("## Train-picked Policies", results[results["train_selected_candidate"]])
    table("## 80%-Coverage Policies", results[results["all_coverage"] >= MARKET_COVERAGE_FLOOR])

    best = results.iloc[0].to_dict()
    lines.append("## Read")
    lines.append("")
    lines.append(f"- Best forward-ranked learned policy: `{best['label']}`.")
    lines.append(
        f"- It selected {int(best['all_markets'])}/{int(best['all_base_markets'])} intervals "
        f"({pct(best['all_coverage'])}) at {pct(best['all_accuracy'])} accuracy."
    )
    for split in ["validation", "holdout"]:
        needed = block_needed(int(best[f"{split}_markets"]), int(best[f"{split}_wins"]))
        lines.append(
            f"- {split}: {pct(best[f'{split}_accuracy'])} accuracy at {pct(best[f'{split}_coverage'])} coverage; "
            f"needs {needed} additional selected losses blocked without losing wins to reach 95%."
        )
    if int(results["target_pass"].sum()) == 0:
        lines.append("- No chronological logistic policy cleared 95% accuracy with >=80% recurring-market coverage.")
    if int(results["wilson_pass"].sum()) == 0:
        lines.append("- No chronological logistic policy produced a sample-size-safe 95% Wilson lower bound across splits.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base, side_rows = prepare_rows()
    results = scan(base, side_rows)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")

    csv_latest = OUT_DIR / "interval_online_logit_latest.csv"
    csv_stamp = OUT_DIR / f"interval_online_logit_{generated}.csv"
    md_latest = OUT_DIR / "interval_online_logit_latest.md"
    md_stamp = OUT_DIR / f"interval_online_logit_{generated}.md"
    json_latest = OUT_DIR / "interval_online_logit_latest.json"
    json_stamp = OUT_DIR / f"interval_online_logit_{generated}.json"

    results.to_csv(csv_latest, index=False)
    results.to_csv(csv_stamp, index=False)
    write_report(md_latest, generated, base, results)
    write_report(md_stamp, generated, base, results)
    summary = {
        "generated_utc": generated,
        "resolved_markets": int(len(base)),
        "candidate_count": int(len(results)),
        "target_pass_count": int(results["target_pass"].sum()),
        "wilson_pass_count": int(results["wilson_pass"].sum()),
        "train_picked": results[results["train_selected_candidate"]].to_dict("records"),
        "top": results.head(20).to_dict("records"),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(summary), indent=2, sort_keys=True), encoding="utf-8")

    print("Chronological interval logistic probe complete")
    print(f"resolved_markets={len(base)} candidates={len(results)}")
    print(f"target_pass={int(results['target_pass'].sum())} wilson_pass={int(results['wilson_pass'].sum())}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
