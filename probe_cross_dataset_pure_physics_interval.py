"""Cross-dataset pure-physics BTC 15m interval scan.

This probe evaluates the same pure-physics policy grid on two live websocket
interval datasets:

1. The current two-sided heartbeat interval ledger.
2. The independent native passive v21 ticker interval ledger.

The goal is not to promote a policy found on one tape. A policy must clear the
95% accuracy / 80% recurring-market coverage gate on both datasets and their
chronological splits to count as a cross-dataset pass.

No orders are submitted and no live bot code or state is touched.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_interval_pure_physics_ablation import (
    PhysicsPolicy,
    add_pure_physics_scores,
    choose_decision_sides,
    make_policies,
    select_markets,
)
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    TARGET_ACCURACY,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)


OUT_DIR = Path("logs/edge_research")
V21_LEDGER = OUT_DIR / "v21_native_passive_interval_validation_ledger_latest.csv"
DATASETS = ["current_two_side_heartbeat", "v21_native_passive"]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def load_current_dataset() -> pd.DataFrame:
    return add_pure_physics_scores(load_side_rows()).drop(columns=["split"], errors="ignore")


def load_v21_dataset() -> pd.DataFrame:
    if not V21_LEDGER.exists():
        raise SystemExit(f"Missing v21 validation ledger. Run probe_v21_native_passive_interval_validation.py first: {V21_LEDGER}")
    df = pd.read_csv(V21_LEDGER, low_memory=False)
    if df.empty:
        return df
    df["entry_dt"] = pd.to_datetime(df["entry_dt"], utc=True, errors="coerce")
    df["entry_minute"] = pd.to_datetime(df["entry_minute"], utc=True, errors="coerce")
    for col in ["win", "outcome_available"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().isin({"true", "1", "yes"})
    numeric_cols = [
        "ask_cents",
        "bid_cents",
        "book_mid_cents",
        "book_p_side",
        "book_other_mid_cents",
        "book_margin_cents",
        "spread_cents",
        "spot",
        "strike",
        "seconds_to_close",
        "margin_dollars",
        "margin_per_rv_sigma_15m",
        "margin_per_rv_sigma_30m",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "brownian_p_rv_60m",
        "drift_p_5m_rv_15m",
        "drift_p_15m_rv_15m",
        "adverse_move_15m",
        "source_line_no",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["entry_dt", "market", "side", "outcome", "win", "ask_cents", "seconds_to_close"]).copy()
    df = df[df["outcome_available"]].copy()
    return add_pure_physics_scores(df).drop(columns=["split"], errors="ignore")


def split_metric(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"] == split]
    selected_part = selected if split == "all" else selected[selected["split"] == split]
    n = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if n else 0
    total = int(len(base_part))
    return {
        "base_markets": total,
        "markets": n,
        "wins": wins,
        "losses": n - wins,
        "accuracy": wins / n if n else None,
        "coverage": n / total if total else None,
        "wilson95_lower": wilson_lower(wins, n),
        "median_ask": float(selected_part["ask_cents"].median()) if n else None,
        "ask_eq_100": int(selected_part["ask_cents"].ge(100).sum()) if n else 0,
        "median_seconds_to_close": float(selected_part["seconds_to_close"].median()) if n else None,
    }


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def target_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
        and all((metrics[split]["accuracy"] or 0.0) >= TARGET_ACCURACY for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def wilson_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return target_pass(metrics) and all(
        (metrics[split]["wilson95_lower"] or 0.0) >= TARGET_ACCURACY
        for split in ["all", "train", "validation", "holdout"]
    )


def nondegenerate_pass(policy: PhysicsPolicy, metrics_by_dataset: Dict[str, Dict[str, Dict[str, Any]]]) -> bool:
    return (
        policy.ask_max <= 95.0
        and policy.min_seconds_to_close >= 60.0
        and all((metrics["all"]["median_ask"] or 100.0) <= 90.0 for metrics in metrics_by_dataset.values())
    )


def evaluate_dataset(name: str, side_rows: pd.DataFrame, policies: List[PhysicsPolicy]) -> tuple[pd.DataFrame, Dict[str, Dict[str, Dict[str, Any]]]]:
    base = market_base(side_rows)
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen_cache = {chooser: choose_decision_sides(rows, chooser) for chooser in sorted({policy.chooser for policy in policies})}
    metrics_by_label: Dict[str, Dict[str, Dict[str, Any]]] = {}
    selected_frames: List[pd.DataFrame] = []
    for policy in policies:
        selected = select_markets(chosen_cache, policy).copy()
        selected["dataset_name"] = name
        selected["policy"] = policy.label
        selected_frames.append(selected)
        metrics_by_label[policy.label] = metrics_for(base, selected)
    selected_all = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    return selected_all, metrics_by_label


def flatten(policy: PhysicsPolicy, metrics_by_dataset: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "label": policy.label,
        "chooser": policy.chooser,
        "min_score": policy.min_score,
        "ask_max": policy.ask_max,
        "min_seconds_to_close": policy.min_seconds_to_close,
        "gate": policy.gate,
    }
    dataset_targets: List[bool] = []
    dataset_wilsons: List[bool] = []
    min_acc = 1.0
    min_cov = 1.0
    min_wilson = 1.0
    max_median_ask = 0.0
    for dataset in DATASETS:
        metrics = metrics_by_dataset[dataset]
        dataset_targets.append(target_pass(metrics))
        dataset_wilsons.append(wilson_pass(metrics))
        for split in ["all", "train", "validation", "holdout"]:
            metric = metrics[split]
            prefix = f"{dataset}_{split}"
            for key, value in metric.items():
                row[f"{prefix}_{key}"] = value
            min_acc = min(min_acc, metric["accuracy"] or 0.0)
            min_cov = min(min_cov, metric["coverage"] or 0.0)
            min_wilson = min(min_wilson, metric["wilson95_lower"] or 0.0)
        max_median_ask = max(max_median_ask, metrics["all"]["median_ask"] or 0.0)
    row["current_target_pass"] = dataset_targets[0]
    row["v21_target_pass"] = dataset_targets[1]
    row["cross_target_pass"] = all(dataset_targets)
    row["cross_wilson_pass"] = all(dataset_wilsons)
    row["cross_nondegenerate_pass"] = row["cross_target_pass"] and nondegenerate_pass(policy, metrics_by_dataset)
    row["min_split_accuracy"] = min_acc
    row["min_split_coverage"] = min_cov
    row["min_split_wilson"] = min_wilson
    row["max_all_median_ask"] = max_median_ask
    return row


def rank_results(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return results
    out = results.copy()
    out["_rank"] = list(
        zip(
            out["cross_wilson_pass"].astype(int),
            out["cross_target_pass"].astype(int),
            out["cross_nondegenerate_pass"].astype(int),
            out["current_target_pass"].astype(int) + out["v21_target_pass"].astype(int),
            out["min_split_accuracy"],
            out["min_split_coverage"],
            out["min_split_wilson"],
            -out["max_all_median_ask"].fillna(100.0),
        )
    )
    return out.sort_values("_rank", ascending=False).drop(columns=["_rank"]).reset_index(drop=True)


def fmt(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.1f}"


def write_report(path: Path, generated: str, dataset_sizes: Dict[str, int], results: pd.DataFrame) -> None:
    ranked = rank_results(results)
    lines: List[str] = [
        "# Cross-Dataset Pure-Physics Interval Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no live bot files or processes are touched.",
        "- A policy must clear 95% accuracy and 80% recurring-market coverage on both current heartbeat intervals and v21 native passive intervals to count as a cross-dataset pass.",
        "- Policy family is pure physics: spot/strike, realized volatility, drift, adverse move, and spread gates. Book probability is not used as the side chooser.",
        "",
        "## Data",
        "",
        f"- Current two-sided heartbeat intervals: {dataset_sizes.get('current_two_side_heartbeat', 0)}",
        f"- V21 native passive intervals: {dataset_sizes.get('v21_native_passive', 0)}",
        f"- Pure-physics policies scanned: {len(results)}",
        f"- Current-only target passes: {int(results['current_target_pass'].sum())}",
        f"- V21-only target passes: {int(results['v21_target_pass'].sum())}",
        f"- Cross-dataset target passes: {int(results['cross_target_pass'].sum())}",
        f"- Cross-dataset Wilson passes: {int(results['cross_wilson_pass'].sum())}",
        f"- Cross-dataset nondegenerate passes: {int(results['cross_nondegenerate_pass'].sum())}",
        "",
        "## Top Policies",
        "",
        "| rank | policy | cross target | current acc/cov | v21 acc/cov | min split acc | min split cov | max median ask |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(ranked.head(20).to_dict("records"), start=1):
        lines.append(
            f"| {idx} | `{row['label']}` | {row['cross_target_pass']} | "
            f"{pct(row['current_two_side_heartbeat_all_accuracy'])}/{pct(row['current_two_side_heartbeat_all_coverage'])} | "
            f"{pct(row['v21_native_passive_all_accuracy'])}/{pct(row['v21_native_passive_all_coverage'])} | "
            f"{pct(row['min_split_accuracy'])} | {pct(row['min_split_coverage'])} | {fmt(row['max_all_median_ask'])} |"
        )
    lines += ["", "## Read", ""]
    if int(results["cross_wilson_pass"].sum()) > 0:
        lines.append("At least one pure-physics policy cleared the cross-dataset Wilson-robust goal.")
    elif int(results["cross_target_pass"].sum()) > 0:
        lines.append("At least one pure-physics policy cleared the literal cross-dataset goal, but not the Wilson-robust proof.")
    else:
        lines.append("No pure-physics policy in this grid cleared the 95% / 80% recurring-market target on both live websocket datasets.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    policies = make_policies()
    datasets = {
        "current_two_side_heartbeat": load_current_dataset(),
        "v21_native_passive": load_v21_dataset(),
    }
    dataset_sizes: Dict[str, int] = {}
    metrics_by_dataset: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}
    selected_frames: List[pd.DataFrame] = []
    for name, rows in datasets.items():
        base = market_base(rows)
        dataset_sizes[name] = int(len(base))
        selected, metrics = evaluate_dataset(name, rows, policies)
        selected_frames.append(selected)
        metrics_by_dataset[name] = metrics

    flat_rows = []
    for policy in policies:
        flat_rows.append(flatten(policy, {dataset: metrics_by_dataset[dataset][policy.label] for dataset in DATASETS}))
    results = rank_results(pd.DataFrame(flat_rows))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    selected_all = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    csv_latest = OUT_DIR / "cross_dataset_pure_physics_interval_latest.csv"
    csv_stamp = OUT_DIR / f"cross_dataset_pure_physics_interval_{generated}.csv"
    selected_latest = OUT_DIR / "cross_dataset_pure_physics_interval_selected_latest.csv"
    selected_stamp = OUT_DIR / f"cross_dataset_pure_physics_interval_selected_{generated}.csv"
    md_latest = OUT_DIR / "cross_dataset_pure_physics_interval_latest.md"
    md_stamp = OUT_DIR / f"cross_dataset_pure_physics_interval_{generated}.md"
    json_latest = OUT_DIR / "cross_dataset_pure_physics_interval_latest.json"
    json_stamp = OUT_DIR / f"cross_dataset_pure_physics_interval_{generated}.json"

    results.to_csv(csv_latest, index=False)
    results.to_csv(csv_stamp, index=False)
    selected_all.to_csv(selected_latest, index=False)
    selected_all.to_csv(selected_stamp, index=False)
    write_report(md_latest, generated, dataset_sizes, results)
    write_report(md_stamp, generated, dataset_sizes, results)
    payload = {
        "generated_utc": generated,
        "dataset_sizes": dataset_sizes,
        "policy_count": int(len(results)),
        "current_target_pass_count": int(results["current_target_pass"].sum()),
        "v21_target_pass_count": int(results["v21_target_pass"].sum()),
        "cross_target_pass_count": int(results["cross_target_pass"].sum()),
        "cross_wilson_pass_count": int(results["cross_wilson_pass"].sum()),
        "cross_nondegenerate_pass_count": int(results["cross_nondegenerate_pass"].sum()),
        "top": clean_json_local(results.head(25).to_dict("records")),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("Cross-dataset pure-physics interval scan complete")
    print(f"current_intervals={dataset_sizes.get('current_two_side_heartbeat')} v21_intervals={dataset_sizes.get('v21_native_passive')}")
    print(
        f"policies={len(results)} current_pass={int(results['current_target_pass'].sum())} "
        f"v21_pass={int(results['v21_target_pass'].sum())} cross_pass={int(results['cross_target_pass'].sum())} "
        f"cross_wilson={int(results['cross_wilson_pass'].sum())}"
    )
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
