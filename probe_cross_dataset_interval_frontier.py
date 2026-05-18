"""Cross-dataset interval frontier for shared simple policies.

This probe asks whether the same simple book/physics interval rule can clear
the user's 95% accuracy and 80% recurring-market coverage target on both:

- the current two-sided heartbeat interval ledger, and
- the independent v21 native passive ticker interval ledger.

It is research-only and does not train, submit orders, or touch live bot state.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    TARGET_ACCURACY,
    Policy,
    add_scores,
    bool_series,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    make_policies,
    market_base,
    pct,
    select_markets_from_chosen,
)


V21_LEDGER = OUT_DIR / "v21_locked_interval_candidate_validation_ledger_latest.csv"


NUMERIC_COLS = [
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
    "margin_per_sqrt_sec",
    "margin_per_sqrt_min",
    "rv_sigma_t_15m",
    "rv_sigma_t_30m",
    "rv_sigma_t_60m",
    "margin_per_rv_sigma_15m",
    "margin_per_rv_sigma_30m",
    "brownian_p_rv_15m",
    "brownian_p_rv_30m",
    "brownian_p_rv_60m",
    "signed_move_1m",
    "signed_move_3m",
    "signed_move_5m",
    "signed_move_15m",
    "adverse_move_1m",
    "adverse_move_3m",
    "adverse_move_5m",
    "adverse_move_15m",
    "drift_projected_margin_5m",
    "drift_projected_margin_15m",
    "drift_p_5m_rv_15m",
    "drift_p_15m_rv_15m",
]


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


def load_v21_side_rows() -> pd.DataFrame:
    if not V21_LEDGER.exists():
        raise SystemExit(f"Missing v21 ledger: {V21_LEDGER}")
    df = pd.read_csv(V21_LEDGER, low_memory=False)
    for col in ["entry_dt", "entry_minute", "close_dt"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    if "win" in df.columns:
        df["win"] = bool_series(df["win"])
    if "outcome_available" in df.columns:
        df["outcome_available"] = bool_series(df["outcome_available"])
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["entry_dt", "market", "side", "decision_key", "seconds_to_close"]).copy()
    df = df[df["seconds_to_close"] > 0].copy()
    for col in ["split", "split_x", "split_y"]:
        if col in df.columns:
            df = df.drop(columns=[col])
    return add_scores(df).sort_values(["entry_dt", "decision_key", "side"]).reset_index(drop=True)


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
        "ask_ge_95": int(selected_part["ask_cents"].ge(95).sum()) if n else 0,
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


def nondegenerate(policy: Policy, current_metrics: Dict[str, Dict[str, Any]], v21_metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        policy.ask_max <= 95.0
        and policy.min_seconds_to_close >= 60.0
        and (current_metrics["all"]["median_ask"] or 100.0) <= 90.0
        and (v21_metrics["all"]["median_ask"] or 100.0) <= 90.0
        and (current_metrics["all"]["ask_eq_100"] or 0) == 0
        and (v21_metrics["all"]["ask_eq_100"] or 0) == 0
    )


def evaluate_dataset(base: pd.DataFrame, side_rows: pd.DataFrame, policies: List[Policy]) -> Dict[str, Dict[str, Any]]:
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen_cache = {
        chooser: choose_decision_sides(side_rows, chooser)
        for chooser in sorted({policy.chooser for policy in policies})
    }
    out: Dict[str, Dict[str, Any]] = {}
    for policy in policies:
        selected = select_markets_from_chosen(chosen_cache.get(policy.chooser, side_rows.iloc[0:0]), policy)
        out[policy.label] = {
            "selected": selected,
            "metrics": metrics_for(base, selected),
        }
    return out


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["both_wilson_pass"]),
        int(row["both_target_pass"]),
        int(row["both_coverage_pass"]),
        int(row["nondegenerate"]),
        row["min_split_accuracy"],
        row["min_all_accuracy"],
        row["min_all_coverage"],
        row["min_all_wilson"],
        -(row["max_median_ask"] or 100.0),
    )


def flatten(policy: Policy, current_metrics: Dict[str, Dict[str, Any]], v21_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    current_target = target_pass(current_metrics)
    v21_target = target_pass(v21_metrics)
    current_wilson = wilson_pass(current_metrics)
    v21_wilson = wilson_pass(v21_metrics)
    both_coverage = all(
        (metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        for metrics in [current_metrics, v21_metrics]
        for split in ["all", "train", "validation", "holdout"]
    )
    row: Dict[str, Any] = {
        "label": policy.label,
        "chooser": policy.chooser,
        "min_score": policy.min_score,
        "ask_max": policy.ask_max,
        "min_seconds_to_close": policy.min_seconds_to_close,
        "gate": policy.gate,
        "current_target_pass": current_target,
        "v21_target_pass": v21_target,
        "both_target_pass": current_target and v21_target,
        "both_wilson_pass": current_wilson and v21_wilson,
        "both_coverage_pass": both_coverage,
        "nondegenerate": nondegenerate(policy, current_metrics, v21_metrics),
    }
    row["min_split_accuracy"] = min(
        current_metrics[split]["accuracy"] or 0.0
        for split in ["all", "train", "validation", "holdout"]
    )
    row["min_split_accuracy"] = min(
        row["min_split_accuracy"],
        min(v21_metrics[split]["accuracy"] or 0.0 for split in ["all", "train", "validation", "holdout"]),
    )
    row["min_all_accuracy"] = min(current_metrics["all"]["accuracy"] or 0.0, v21_metrics["all"]["accuracy"] or 0.0)
    row["min_all_coverage"] = min(current_metrics["all"]["coverage"] or 0.0, v21_metrics["all"]["coverage"] or 0.0)
    row["min_all_wilson"] = min(current_metrics["all"]["wilson95_lower"] or 0.0, v21_metrics["all"]["wilson95_lower"] or 0.0)
    row["max_median_ask"] = max(current_metrics["all"]["median_ask"] or 0.0, v21_metrics["all"]["median_ask"] or 0.0)
    for prefix, metrics in [("current", current_metrics), ("v21", v21_metrics)]:
        for split, metric in metrics.items():
            for key, value in metric.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def scan() -> tuple[pd.DataFrame, Dict[str, Any]]:
    policies = make_policies()
    current_side = load_side_rows()
    current_base = market_base(current_side)
    v21_side = load_v21_side_rows()
    v21_base = market_base(v21_side)
    current_eval = evaluate_dataset(current_base, current_side, policies)
    v21_eval = evaluate_dataset(v21_base, v21_side, policies)
    rows = [
        flatten(policy, current_eval[policy.label]["metrics"], v21_eval[policy.label]["metrics"])
        for policy in policies
    ]
    rows.sort(key=rank_key, reverse=True)
    diagnostics = {
        "current_intervals": int(len(current_base)),
        "current_side_rows": int(len(current_side)),
        "v21_intervals": int(len(v21_base)),
        "v21_side_rows": int(len(v21_side)),
        "policies": int(len(policies)),
    }
    return pd.DataFrame(rows), diagnostics


def write_report(path: Path, generated: str, results: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    lines: List[str] = [
        "# Cross-Dataset Interval Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- The same simple policy definitions are evaluated on the current heartbeat ledger and the independent v21 passive ticker ledger.",
        "- Volume denominator is recurring BTC 15-minute markets in each dataset.",
        "- This is a stability/falsification scan, not a promotion lock.",
        "",
        "## Data",
        "",
        f"- Current intervals: {diagnostics['current_intervals']}",
        f"- Current side rows: {diagnostics['current_side_rows']}",
        f"- V21 intervals: {diagnostics['v21_intervals']}",
        f"- V21 side rows: {diagnostics['v21_side_rows']}",
        f"- Shared policies scanned: {diagnostics['policies']}",
        f"- Policies passing target on both datasets: {int(results['both_target_pass'].sum())}",
        f"- Policies passing Wilson gate on both datasets: {int(results['both_wilson_pass'].sum())}",
        f"- Nondegenerate policies passing target on both datasets: {int((results['both_target_pass'] & results['nondegenerate']).sum())}",
        "",
        "## Best Shared Policies",
        "",
        "| rank | policy | both target | nondeg | current acc | current cov | v21 acc | v21 cov | v21 holdout acc | max median ask |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(results.head(15).to_dict("records"), start=1):
        lines.append(
            f"| {idx} | `{row['label']}` | {row['both_target_pass']} | {row['nondegenerate']} | "
            f"{pct(row['current_all_accuracy'])} | {pct(row['current_all_coverage'])} | "
            f"{pct(row['v21_all_accuracy'])} | {pct(row['v21_all_coverage'])} | "
            f"{pct(row['v21_holdout_accuracy'])} | {fmt(row['max_median_ask'])} |"
        )
    lines += ["", "## Read", ""]
    if int(results["both_target_pass"].sum()) > 0:
        lines.append("At least one simple policy clears the literal 95% / 80% split target on both datasets, but degeneracy and Wilson gates still need review.")
    else:
        lines.append("No shared simple policy clears the 95% accuracy / 80% recurring-market coverage split target on both datasets.")
    if int((results["both_target_pass"] & results["nondegenerate"]).sum()) == 0:
        lines.append("No nondegenerate shared simple policy clears the target across both datasets.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    results, diagnostics = scan()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_latest = OUT_DIR / "cross_dataset_interval_frontier_latest.csv"
    csv_stamp = OUT_DIR / f"cross_dataset_interval_frontier_{generated}.csv"
    json_latest = OUT_DIR / "cross_dataset_interval_frontier_latest.json"
    json_stamp = OUT_DIR / f"cross_dataset_interval_frontier_{generated}.json"
    md_latest = OUT_DIR / "cross_dataset_interval_frontier_latest.md"
    md_stamp = OUT_DIR / f"cross_dataset_interval_frontier_{generated}.md"
    results.to_csv(csv_latest, index=False)
    results.to_csv(csv_stamp, index=False)
    write_report(md_latest, generated, results, diagnostics)
    write_report(md_stamp, generated, results, diagnostics)
    summary = {
        "generated_utc": generated,
        "diagnostics": diagnostics,
        "both_target_pass_count": int(results["both_target_pass"].sum()),
        "both_wilson_pass_count": int(results["both_wilson_pass"].sum()),
        "both_nondegenerate_target_pass_count": int((results["both_target_pass"] & results["nondegenerate"]).sum()),
        "top_rows": results.head(25).to_dict("records"),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(summary), indent=2, sort_keys=True), encoding="utf-8")
    print("Cross-dataset interval frontier complete")
    print(f"policies={len(results)} both_target_pass={int(results['both_target_pass'].sum())}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
