"""Cross-dataset blocker scan around the stable cheap interval frontier.

The shared simple-policy and learned-transfer scans show that high-price states
can look excellent on one capture, while the stable cheap/high-coverage frontier
is only around the high-80s accuracy. This probe starts from the best shared
nondegenerate policy and asks whether physical loss blockers can raise accuracy
on both live captures while preserving at least 80% recurring-market coverage.

Research-only: no orders, bot files, bot state, or live processes are touched.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import combinations
from typing import Any, Dict, List, Optional

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    TARGET_ACCURACY,
    Policy,
    choose_decision_sides,
    clean_json,
    gate_mask,
    load_side_rows,
    market_base,
    pct,
)


BASE_POLICY = Policy(
    chooser="score_mean_book_rv15",
    min_score=0.80,
    ask_max=95.0,
    min_seconds_to_close=60.0,
    gate="none",
)


@dataclass(frozen=True)
class Blocker:
    name: str
    column: str
    op: str
    threshold: float

    def keep(self, df: pd.DataFrame) -> pd.Series:
        if self.column not in df.columns:
            return pd.Series(False, index=df.index)
        values = pd.to_numeric(df[self.column], errors="coerce")
        if self.op == "<=":
            return values.le(self.threshold).fillna(False)
        if self.op == ">=":
            return values.ge(self.threshold).fillna(False)
        raise ValueError(f"unknown op: {self.op}")


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


def make_blockers() -> List[Blocker]:
    blockers: List[Blocker] = []
    for col, thresholds in [
        ("adverse_move_1m", [1, 2, 3, 5, 8]),
        ("adverse_move_3m", [2, 3, 5, 8, 10]),
        ("adverse_move_5m", [3, 5, 8, 10, 15]),
        ("adverse_move_15m", [5, 8, 10, 15, 20]),
        ("abs_book_rv15_gap", [0.10, 0.20, 0.30, 0.40]),
        ("abs_book_rv30_gap", [0.10, 0.20, 0.30, 0.40]),
        ("spread_cents", [2, 3, 4, 5, 8]),
        ("seconds_to_close", [300, 480, 600, 900]),
        ("ask_cents", [88, 90, 92, 95]),
    ]:
        for threshold in thresholds:
            blockers.append(Blocker(f"{col}<={threshold:g}", col, "<=", float(threshold)))
    for col, thresholds in [
        ("signed_move_1m", [-5, -2, 0, 2]),
        ("signed_move_3m", [-8, -5, 0, 3]),
        ("signed_move_5m", [-10, -5, 0, 5]),
        ("signed_move_15m", [-20, -10, -5, 0]),
        ("margin_per_rv_sigma_15m", [-0.5, 0, 0.25, 0.5, 1.0]),
        ("margin_per_rv_sigma_30m", [-0.5, 0, 0.25, 0.5, 1.0]),
        ("book_p_side", [0.70, 0.75, 0.80, 0.85, 0.90]),
        ("brownian_p_rv_15m", [0.50, 0.55, 0.60, 0.70, 0.80]),
        ("brownian_p_rv_30m", [0.50, 0.55, 0.60, 0.70, 0.80]),
        ("drift_p_5m_rv_15m", [0.50, 0.55, 0.60, 0.70, 0.80]),
    ]:
        for threshold in thresholds:
            blockers.append(Blocker(f"{col}>={threshold:g}", col, ">=", float(threshold)))
    return blockers


def select_with_blockers(chosen: pd.DataFrame, blockers: List[Blocker]) -> pd.DataFrame:
    mask = gate_mask(chosen, BASE_POLICY)
    for blocker in blockers:
        mask &= blocker.keep(chosen)
    eligible = chosen[mask.fillna(False)].copy()
    if eligible.empty:
        return eligible
    selected = (
        eligible.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    selected["settlement_pnl_cents"] = selected["win"].map({True: 1.0, False: 0.0})
    selected["settlement_pnl_cents"] = (
        (100.0 - selected["ask_cents"]) * selected["win"] - selected["ask_cents"] * (~selected["win"])
    )
    return selected


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


def wilson_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return dataset_pass(metrics) and all(
        (metrics[split]["wilson95_lower"] or 0.0) >= TARGET_ACCURACY
        for split in ["all", "train", "validation", "holdout"]
    )


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["both_wilson_pass"]),
        int(row["both_target_pass"]),
        int(row["both_coverage_pass"]),
        row["min_split_accuracy"],
        row["min_all_accuracy"],
        row["min_all_coverage"],
        row["min_all_wilson"],
        -(row["max_median_ask"] or 100.0),
        row["min_all_roi"],
    )


def flatten(name: str, current_metrics: Dict[str, Dict[str, Any]], v21_metrics: Dict[str, Dict[str, Any]], blocker_count: int) -> Dict[str, Any]:
    both_coverage = all(
        (metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        for metrics in [current_metrics, v21_metrics]
        for split in ["all", "train", "validation", "holdout"]
    )
    current_target = dataset_pass(current_metrics)
    v21_target = dataset_pass(v21_metrics)
    row: Dict[str, Any] = {
        "blockers": name,
        "blocker_count": blocker_count,
        "current_target_pass": current_target,
        "v21_target_pass": v21_target,
        "both_target_pass": current_target and v21_target,
        "both_wilson_pass": wilson_pass(current_metrics) and wilson_pass(v21_metrics),
        "both_coverage_pass": both_coverage,
    }
    row["min_split_accuracy"] = min(
        min(current_metrics[split]["accuracy"] or 0.0 for split in ["all", "train", "validation", "holdout"]),
        min(v21_metrics[split]["accuracy"] or 0.0 for split in ["all", "train", "validation", "holdout"]),
    )
    row["min_all_accuracy"] = min(current_metrics["all"]["accuracy"] or 0.0, v21_metrics["all"]["accuracy"] or 0.0)
    row["min_all_coverage"] = min(current_metrics["all"]["coverage"] or 0.0, v21_metrics["all"]["coverage"] or 0.0)
    row["min_all_wilson"] = min(current_metrics["all"]["wilson95_lower"] or 0.0, v21_metrics["all"]["wilson95_lower"] or 0.0)
    row["max_median_ask"] = max(current_metrics["all"]["median_ask"] or 0.0, v21_metrics["all"]["median_ask"] or 0.0)
    row["min_all_roi"] = min(current_metrics["all"]["gross_roi"] or -999.0, v21_metrics["all"]["gross_roi"] or -999.0)
    for prefix, metrics in [("current", current_metrics), ("v21", v21_metrics)]:
        for split, metric_row in metrics.items():
            for key, value in metric_row.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def evaluate_candidate(
    name: str,
    blockers: List[Blocker],
    current_base: pd.DataFrame,
    current_chosen: pd.DataFrame,
    v21_base: pd.DataFrame,
    v21_chosen: pd.DataFrame,
) -> Dict[str, Any]:
    current_selected = select_with_blockers(current_chosen, blockers)
    v21_selected = select_with_blockers(v21_chosen, blockers)
    return flatten(name, metrics_for(current_base, current_selected), metrics_for(v21_base, v21_selected), len(blockers))


def scan() -> tuple[pd.DataFrame, Dict[str, Any]]:
    current_base, current_rows = prepare_current()
    v21_base, v21_rows = prepare_v21()
    current_chosen = choose_decision_sides(current_rows, BASE_POLICY.chooser)
    v21_chosen = choose_decision_sides(v21_rows, BASE_POLICY.chooser)
    blockers = make_blockers()

    rows: List[Dict[str, Any]] = [
        evaluate_candidate("none", [], current_base, current_chosen, v21_base, v21_chosen)
    ]
    single_rows: List[tuple[Blocker, Dict[str, Any]]] = []
    for blocker in blockers:
        row = evaluate_candidate(blocker.name, [blocker], current_base, current_chosen, v21_base, v21_chosen)
        rows.append(row)
        single_rows.append((blocker, row))

    single_rows.sort(key=lambda item: rank_key(item[1]), reverse=True)
    pair_pool = [item[0] for item in single_rows[:24]]
    for left, right in combinations(pair_pool, 2):
        if left.column == right.column and left.op == right.op:
            continue
        rows.append(
            evaluate_candidate(
                f"{left.name} AND {right.name}",
                [left, right],
                current_base,
                current_chosen,
                v21_base,
                v21_chosen,
            )
        )
    rows.sort(key=rank_key, reverse=True)
    diagnostics = {
        "current_intervals": int(len(current_base)),
        "v21_intervals": int(len(v21_base)),
        "current_chosen_rows": int(len(current_chosen)),
        "v21_chosen_rows": int(len(v21_chosen)),
        "single_blockers": int(len(blockers)),
        "candidate_rows": int(len(rows)),
        "base_policy": BASE_POLICY.label,
    }
    return pd.DataFrame(rows), diagnostics


def write_report(path: OUT_DIR.__class__, generated: str, results: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    lines: List[str] = [
        "# Cross-Dataset Shared Loss Blockers",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only probe; no orders are submitted and no bot files or live processes are touched.",
        f"- Base policy: `{diagnostics['base_policy']}`.",
        "- Blockers are physical/book/path constraints applied before the first eligible market selection.",
        "- Volume denominator is recurring BTC 15-minute markets on both live captures.",
        "",
        "## Data",
        "",
        f"- Current intervals: {diagnostics['current_intervals']}",
        f"- V21 intervals: {diagnostics['v21_intervals']}",
        f"- Current chosen decision rows: {diagnostics['current_chosen_rows']}",
        f"- V21 chosen decision rows: {diagnostics['v21_chosen_rows']}",
        f"- Single blockers generated: {diagnostics['single_blockers']}",
        f"- Candidate blocker rows evaluated: {diagnostics['candidate_rows']}",
        f"- Both-dataset target passes: {int(results['both_target_pass'].sum()) if not results.empty else 0}",
        f"- Both-dataset Wilson passes: {int(results['both_wilson_pass'].sum()) if not results.empty else 0}",
        "",
        "## Best Blockers",
        "",
        "| rank | blockers | target | current acc/cov | v21 acc/cov | current holdout | v21 holdout | median ask |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(results.head(20).to_dict("records"), start=1):
        lines.append(
            f"| {idx} | `{row['blockers']}` | {row['both_target_pass']} | "
            f"{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{pct(row['current_holdout_accuracy'])}/{pct(row['current_holdout_coverage'])} | "
            f"{pct(row['v21_holdout_accuracy'])}/{pct(row['v21_holdout_coverage'])} | "
            f"{fmt(row['max_median_ask'])} |"
        )
    lines += ["", "## Read", ""]
    if not results.empty and int(results["both_target_pass"].sum()) > 0:
        lines.append("At least one blocker set clears the literal 95% / 80% target on both datasets.")
    else:
        lines.append("No physical blocker set clears the 95% accuracy / 80% recurring-market coverage target on both datasets.")
    if not results.empty:
        best = results.iloc[0].to_dict()
        lines.append(
            f"The best ranked blocker set still bottoms out at {pct(best['min_split_accuracy'])} split accuracy "
            f"with {pct(best['min_all_coverage'])} minimum all-dataset coverage."
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    results, diagnostics = scan()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_latest = OUT_DIR / "cross_dataset_shared_loss_blockers_latest.csv"
    csv_stamp = OUT_DIR / f"cross_dataset_shared_loss_blockers_{generated}.csv"
    json_latest = OUT_DIR / "cross_dataset_shared_loss_blockers_latest.json"
    json_stamp = OUT_DIR / f"cross_dataset_shared_loss_blockers_{generated}.json"
    md_latest = OUT_DIR / "cross_dataset_shared_loss_blockers_latest.md"
    md_stamp = OUT_DIR / f"cross_dataset_shared_loss_blockers_{generated}.md"
    results.to_csv(csv_latest, index=False)
    results.to_csv(csv_stamp, index=False)
    write_report(md_latest, generated, results, diagnostics)
    write_report(md_stamp, generated, results, diagnostics)
    summary = {
        "generated_utc": generated,
        "diagnostics": diagnostics,
        "both_target_pass_count": int(results["both_target_pass"].sum()) if not results.empty else 0,
        "both_wilson_pass_count": int(results["both_wilson_pass"].sum()) if not results.empty else 0,
        "top_rows": results.head(50).to_dict("records"),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(summary), indent=2, sort_keys=True), encoding="utf-8")
    print("Cross-dataset shared loss blockers complete")
    print(f"candidate_rows={len(results)} both_target_pass={summary['both_target_pass_count']}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
