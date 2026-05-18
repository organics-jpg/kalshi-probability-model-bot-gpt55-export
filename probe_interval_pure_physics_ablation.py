"""Research-only pure-physics interval ablation.

The recurring-market scans found raw 95% / 80% passes, but the strongest rows
lean heavily on book probability and high ask prices near settlement. This probe
removes book probability from the side-choice score and asks whether spot/strike,
realized volatility, and drift features alone can support the user's market
coverage target.

No orders are submitted and no bot files are modified.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

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


@dataclass(frozen=True)
class PhysicsPolicy:
    chooser: str
    min_score: float
    ask_max: float
    min_seconds_to_close: float
    gate: str = "none"

    @property
    def label(self) -> str:
        parts = [
            f"pure={self.chooser}",
            f"{self.chooser}>={self.min_score:g}",
            f"ask<={self.ask_max:g}",
            f"sec>={self.min_seconds_to_close:g}",
        ]
        if self.gate != "none":
            parts.append(self.gate)
        return "; ".join(parts)


def add_pure_physics_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    cols = [
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "brownian_p_rv_60m",
        "drift_p_5m_rv_15m",
        "drift_p_15m_rv_15m",
        "margin_per_rv_sigma_15m",
        "margin_per_rv_sigma_30m",
        "adverse_move_5m",
        "adverse_move_15m",
        "spread_cents",
    ]
    for col in cols:
        if col not in out.columns:
            out[col] = np.nan
    out["score_physics_mean_rv15_rv30"] = out[["brownian_p_rv_15m", "brownian_p_rv_30m"]].mean(axis=1)
    out["score_physics_mean_rv_drift"] = out[
        ["brownian_p_rv_15m", "brownian_p_rv_30m", "drift_p_5m_rv_15m"]
    ].mean(axis=1)
    out["score_physics_min_rv_drift"] = out[
        ["brownian_p_rv_15m", "brownian_p_rv_30m", "drift_p_5m_rv_15m"]
    ].min(axis=1)
    out["score_physics_margin_blend"] = (
        0.45 * out["brownian_p_rv_15m"]
        + 0.25 * out["brownian_p_rv_30m"]
        + 0.20 * out["drift_p_5m_rv_15m"]
        + 0.10 * out["drift_p_15m_rv_15m"]
    )
    return out


def make_policies() -> List[PhysicsPolicy]:
    choosers = [
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "brownian_p_rv_60m",
        "drift_p_5m_rv_15m",
        "drift_p_15m_rv_15m",
        "score_physics_mean_rv15_rv30",
        "score_physics_mean_rv_drift",
        "score_physics_min_rv_drift",
        "score_physics_margin_blend",
    ]
    thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
    ask_caps = [90.0, 95.0, 100.0]
    min_seconds = [0.0, 60.0, 120.0, 240.0]
    gates = ["none", "spread<=4", "adverse15<=10", "margin_rv15>=0", "margin_rv15>=0.5"]
    return [
        PhysicsPolicy(chooser, threshold, ask_max, min_sec, gate)
        for chooser in choosers
        for threshold in thresholds
        for ask_max in ask_caps
        for min_sec in min_seconds
        for gate in gates
    ]


def gate_mask(chosen: pd.DataFrame, policy: PhysicsPolicy) -> pd.Series:
    mask = (
        chosen[policy.chooser].ge(policy.min_score)
        & chosen["ask_cents"].le(policy.ask_max)
        & chosen["seconds_to_close"].ge(policy.min_seconds_to_close)
    )
    if policy.gate == "spread<=4":
        mask &= chosen["spread_cents"].le(4)
    elif policy.gate == "adverse15<=10":
        mask &= chosen["adverse_move_15m"].le(10)
    elif policy.gate == "margin_rv15>=0":
        mask &= chosen["margin_per_rv_sigma_15m"].ge(0)
    elif policy.gate == "margin_rv15>=0.5":
        mask &= chosen["margin_per_rv_sigma_15m"].ge(0.5)
    elif policy.gate != "none":
        raise ValueError(f"unknown gate: {policy.gate}")
    return mask.fillna(False)


def choose_decision_sides(side_rows: pd.DataFrame, chooser: str) -> pd.DataFrame:
    usable = side_rows[side_rows[chooser].notna()].copy()
    if usable.empty:
        return usable
    return (
        usable.sort_values(
            ["decision_key", chooser, "margin_per_rv_sigma_15m", "seconds_to_close"],
            ascending=[True, False, False, True],
        )
        .groupby("decision_key", as_index=False, sort=False)
        .first()
        .sort_values(["market", "entry_dt"])
        .reset_index(drop=True)
    )


def select_markets(chosen_cache: Dict[str, pd.DataFrame], policy: PhysicsPolicy) -> pd.DataFrame:
    chosen = chosen_cache[policy.chooser]
    eligible = chosen[gate_mask(chosen, policy)].copy()
    if eligible.empty:
        return eligible
    selected = (
        eligible.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    selected["settlement_pnl_cents"] = np.where(selected["win"], 100.0 - selected["ask_cents"], -selected["ask_cents"])
    return selected


def split_metric(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"] == split]
    selected_part = selected if split == "all" else selected[selected["split"] == split]
    rows = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if rows else 0
    return {
        "base_markets": int(len(base_part)),
        "markets": rows,
        "wins": wins,
        "losses": rows - wins,
        "accuracy": wins / rows if rows else None,
        "coverage": rows / len(base_part) if len(base_part) else None,
        "wilson95_lower": wilson_lower(wins, rows),
        "gross_pnl_cents": float(selected_part["settlement_pnl_cents"].sum()) if rows else 0.0,
        "median_ask": float(selected_part["ask_cents"].median()) if rows else None,
        "median_seconds_to_close": float(selected_part["seconds_to_close"].median()) if rows else None,
    }


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])


def target_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        coverage_pass(metrics)
        and all((metrics[split]["accuracy"] or 0.0) >= TARGET_ACCURACY for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def nondegenerate_pass(policy: PhysicsPolicy, metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        target_pass(metrics)
        and policy.ask_max <= 95.0
        and policy.min_seconds_to_close >= 60.0
        and (metrics["all"]["median_ask"] or 100.0) <= 90.0
    )


def wilson_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return target_pass(metrics) and all(
        (metrics[split]["wilson95_lower"] or 0.0) >= TARGET_ACCURACY
        for split in ["all", "train", "validation", "holdout"]
    )


def flatten(policy: PhysicsPolicy, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "label": policy.label,
        "chooser": policy.chooser,
        "min_score": policy.min_score,
        "ask_max": policy.ask_max,
        "min_seconds_to_close": policy.min_seconds_to_close,
        "gate": policy.gate,
        "coverage_pass": coverage_pass(metrics),
        "target_pass": target_pass(metrics),
        "nondegenerate_pass": nondegenerate_pass(policy, metrics),
        "wilson_pass": wilson_pass(metrics),
    }
    row["min_test_accuracy"] = min(metrics["validation"]["accuracy"] or 0.0, metrics["holdout"]["accuracy"] or 0.0)
    row["min_test_coverage"] = min(metrics["validation"]["coverage"] or 0.0, metrics["holdout"]["coverage"] or 0.0)
    row["min_test_wilson"] = min(metrics["validation"]["wilson95_lower"] or 0.0, metrics["holdout"]["wilson95_lower"] or 0.0)
    for split, metric in metrics.items():
        for key, value in metric.items():
            row[f"{split}_{key}"] = value
    return row


def rank_results(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return results
    out = results.copy()
    out["_rank"] = list(
        zip(
            out["wilson_pass"].astype(int),
            out["target_pass"].astype(int),
            out["nondegenerate_pass"].astype(int),
            out["min_test_accuracy"],
            out["all_accuracy"],
            out["min_test_coverage"],
            out["min_test_wilson"],
            -out["all_median_ask"].fillna(100.0),
            out["all_median_seconds_to_close"].fillna(0.0),
        )
    )
    return out.sort_values("_rank", ascending=False).drop(columns=["_rank"]).reset_index(drop=True)


def table_lines(title: str, rows: pd.DataFrame, limit: int = 15) -> List[str]:
    lines = ["", title, ""]
    if rows.empty:
        lines.append("No rows.")
        return lines
    lines.append("| rank | policy | all acc | all cov | val acc | holdout acc | Wilson low | median ask | median sec | target | nondeg |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---|")
    for idx, row in enumerate(rows.head(limit).to_dict("records"), start=1):
        lines.append(
            f"| {idx} | `{row['label']}` | {pct(row['all_accuracy'])} | {pct(row['all_coverage'])} | "
            f"{pct(row['validation_accuracy'])} | {pct(row['holdout_accuracy'])} | "
            f"{pct(row['all_wilson95_lower'])} | {row['all_median_ask']:.1f} | "
            f"{row['all_median_seconds_to_close']:.1f} | {row['target_pass']} | {row['nondegenerate_pass']} |"
        )
    return lines


def write_report(path, generated: str, base: pd.DataFrame, results: pd.DataFrame) -> None:
    ranked = rank_results(results)
    lines: List[str] = [
        "# Pure-Physics Interval Ablation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only probe; no orders are submitted and no bot files are modified.",
        "- Unit of volume is the recurring BTC 15-minute market interval.",
        "- Side choice uses only spot/strike, realized-volatility, drift, and adverse-move features.",
        "- Book probability is not used as a chooser or model feature; ask is only used as an execution price cap.",
        "",
        "## Coverage",
        "",
        f"- Resolved intervals: {len(base)}",
    ]
    for split in ["train", "validation", "holdout"]:
        lines.append(f"- {split.title()} intervals: {int((base['split'] == split).sum())}")
    lines += [
        f"- Candidate pure-physics policies scanned: {len(results)}",
        f"- Policies covering >=80% of intervals on every split: {int(results['coverage_pass'].sum())}",
        f"- Raw target-pass policies: {int(results['target_pass'].sum())}",
        f"- Nondegenerate target-pass policies: {int(results['nondegenerate_pass'].sum())}",
        f"- Wilson-pass policies: {int(results['wilson_pass'].sum())}",
    ]
    lines += table_lines("## Target-Passing Pure-Physics Policies", ranked[ranked["target_pass"]])
    lines += table_lines("## Best Nondegenerate 80%-Coverage Policies", ranked[ranked["coverage_pass"] & ~ranked["target_pass"]])
    lines += table_lines("## Best Overall Pure-Physics Policies", ranked)
    lines += ["", "## Read", ""]
    if int(results["nondegenerate_pass"].sum()) > 0:
        lines.append("At least one pure-physics policy cleared the nondegenerate 95% / 80% interval target. It still needs locked forward validation before promotion.")
    elif int(results["target_pass"].sum()) > 0:
        best = ranked[ranked["target_pass"]].iloc[0]
        lines.append(
            "Pure physics can reproduce a raw target pass, but the best pass still depends on high execution prices "
            f"(median ask {best['all_median_ask']:.1f}c) or weak sample bounds."
        )
    else:
        best_cov = ranked[ranked["coverage_pass"]].iloc[0] if not ranked[ranked["coverage_pass"]].empty else ranked.iloc[0]
        lines.append(
            "Pure physics alone does not clear 95% accuracy at 80% recurring-market coverage. "
            f"The best high-coverage row is {pct(best_cov['all_accuracy'])} accurate at {pct(best_cov['all_coverage'])} coverage."
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    side_rows = add_pure_physics_scores(load_side_rows())
    base = market_base(side_rows)
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    policies = make_policies()
    chosen_cache = {chooser: choose_decision_sides(side_rows, chooser) for chooser in sorted({p.chooser for p in policies})}

    rows: List[Dict[str, Any]] = []
    for policy in policies:
        selected = select_markets(chosen_cache, policy)
        rows.append(flatten(policy, metrics_for(base, selected)))
    results = rank_results(pd.DataFrame(rows))

    csv_latest = OUT_DIR / "interval_pure_physics_ablation_latest.csv"
    csv_stamp = OUT_DIR / f"interval_pure_physics_ablation_{generated}.csv"
    md_latest = OUT_DIR / "interval_pure_physics_ablation_latest.md"
    md_stamp = OUT_DIR / f"interval_pure_physics_ablation_{generated}.md"
    json_latest = OUT_DIR / "interval_pure_physics_ablation_latest.json"
    json_stamp = OUT_DIR / f"interval_pure_physics_ablation_{generated}.json"

    results.to_csv(csv_latest, index=False)
    results.to_csv(csv_stamp, index=False)
    write_report(md_latest, generated, base, results)
    write_report(md_stamp, generated, base, results)

    payload = {
        "generated_utc": generated,
        "resolved_intervals": int(len(base)),
        "candidate_count": int(len(results)),
        "coverage_pass_count": int(results["coverage_pass"].sum()),
        "target_pass_count": int(results["target_pass"].sum()),
        "nondegenerate_pass_count": int(results["nondegenerate_pass"].sum()),
        "wilson_pass_count": int(results["wilson_pass"].sum()),
        "top": clean_json(results.head(20).to_dict("records")),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("Pure-physics interval ablation complete")
    print(
        f"resolved_intervals={len(base)} candidates={len(results)} "
        f"target_pass={int(results['target_pass'].sum())} "
        f"nondegenerate_pass={int(results['nondegenerate_pass'].sum())} "
        f"wilson_pass={int(results['wilson_pass'].sum())}"
    )
    print(f"report={md_latest}")


if __name__ == "__main__":
    main()
