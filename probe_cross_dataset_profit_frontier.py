"""Cross-dataset fee-aware profit frontier for BTC 15m interval policies.

The accuracy frontier can be made to look strong by buying contracts near
settlement certainty. This probe changes the objective to the user's practical
goal: maximize held-to-settlement profit while still selecting at least 80% of
recurring BTC 15-minute markets.

It evaluates the same policy grid on the current two-sided heartbeat ledger and
on the independent v21 passive websocket ledger. The fee model is the local
Kalshi taker estimate already used by the live bot, applied as an entry-only
held-to-settlement cost for one contract.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)


SUPPORTED_GATES = [
    "none",
    "adverse15<=10_or_margin_rv15>=0.5",
    "brownian15>=0.55_and_brownian30>=0.55",
    "spread<=4",
    "margin_rv15>=0",
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt_cents(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.1f}c"


def fmt_roi(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{100.0 * float(value):.2f}%"


def estimated_order_fee_cents(price_cents: float, count: int = 1) -> int:
    bounded_price = max(1, min(99, int(round(float(price_cents)))))
    numerator = 7 * int(count) * bounded_price * (100 - bounded_price)
    return max(1, (numerator + 9999) // 10000)


def make_profit_policies() -> List[Policy]:
    policies: List[Policy] = []
    choosers = [
        "book_p_side",
        "brownian_p_rv_15m",
        "score_mean_book_rv15",
        "score_mean_book_rv15_drift5",
        "score_min_book_rv15",
        "score_regime_blend",
    ]
    thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.80, 0.90, 0.95]
    ask_caps = [90.0, 95.0, 98.0, 100.0]
    min_seconds = [0.0, 60.0, 120.0]
    for chooser in choosers:
        for threshold in thresholds:
            for ask_max in ask_caps:
                for min_sec in min_seconds:
                    for gate in SUPPORTED_GATES:
                        policies.append(Policy(chooser, threshold, ask_max, min_sec, gate))
    return policies


def enrich_selected(selected: pd.DataFrame) -> pd.DataFrame:
    out = selected.copy()
    if out.empty:
        for col in [
            "entry_fee_cents",
            "entry_cost_cents",
            "gross_pnl_cents",
            "net_pnl_cents",
            "fee_aware_break_even_p",
        ]:
            out[col] = []
        return out
    out["entry_fee_cents"] = [
        estimated_order_fee_cents(ask, 1) for ask in pd.to_numeric(out["ask_cents"], errors="coerce").fillna(100.0)
    ]
    out["entry_cost_cents"] = out["ask_cents"] + out["entry_fee_cents"]
    out["gross_pnl_cents"] = np.where(out["win"], 100.0 - out["ask_cents"], -out["ask_cents"])
    out["net_pnl_cents"] = out["gross_pnl_cents"] - out["entry_fee_cents"]
    out["fee_aware_break_even_p"] = out["entry_cost_cents"] / 100.0
    return out


def split_metric(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"] == split]
    selected_part = selected if split == "all" else selected[selected["split"] == split]
    n = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if n else 0
    total = int(len(base_part))
    ask_sum = float(selected_part["ask_cents"].sum()) if n else 0.0
    cost_sum = float(selected_part["entry_cost_cents"].sum()) if n else 0.0
    gross_pnl = float(selected_part["gross_pnl_cents"].sum()) if n else 0.0
    net_pnl = float(selected_part["net_pnl_cents"].sum()) if n else 0.0
    accuracy = wins / n if n else None
    break_even = float(selected_part["fee_aware_break_even_p"].mean()) if n else None
    return {
        "base_markets": total,
        "markets": n,
        "wins": wins,
        "losses": n - wins,
        "accuracy": accuracy,
        "coverage": n / total if total else None,
        "wilson95_lower": wilson_lower(wins, n),
        "median_ask": float(selected_part["ask_cents"].median()) if n else None,
        "mean_ask": float(selected_part["ask_cents"].mean()) if n else None,
        "p75_ask": float(selected_part["ask_cents"].quantile(0.75)) if n else None,
        "ask_ge_95": int(selected_part["ask_cents"].ge(95).sum()) if n else 0,
        "ask_eq_100": int(selected_part["ask_cents"].ge(100).sum()) if n else 0,
        "median_seconds_to_close": float(selected_part["seconds_to_close"].median()) if n else None,
        "entry_fee_cents": float(selected_part["entry_fee_cents"].sum()) if n else 0.0,
        "ask_cost_cents": ask_sum,
        "entry_cost_cents": cost_sum,
        "gross_pnl_cents": gross_pnl,
        "net_pnl_cents": net_pnl,
        "gross_roi_on_ask": gross_pnl / ask_sum if ask_sum else None,
        "net_roi_on_cost": net_pnl / cost_sum if cost_sum else None,
        "net_edge_per_selected_cents": net_pnl / n if n else None,
        "net_edge_per_base_market_cents": net_pnl / total if total else None,
        "fee_aware_break_even_accuracy": break_even,
        "accuracy_minus_break_even": (accuracy - break_even) if accuracy is not None and break_even is not None else None,
    }


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def evaluate_dataset(base: pd.DataFrame, side_rows: pd.DataFrame, policies: List[Policy]) -> Dict[str, Dict[str, Any]]:
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen_cache = {
        chooser: choose_decision_sides(side_rows, chooser)
        for chooser in sorted({policy.chooser for policy in policies})
    }
    out: Dict[str, Dict[str, Any]] = {}
    empty = side_rows.iloc[0:0]
    for policy in policies:
        chosen = chosen_cache.get(policy.chooser, empty)
        selected = enrich_selected(select_markets_from_chosen(chosen, policy))
        out[policy.label] = {
            "selected": selected,
            "metrics": metrics_for(base, selected),
        }
    return out


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def profitable_all(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["all", "train", "validation", "holdout"])


def profitable_oos(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])


def nondegenerate(policy: Policy, current_metrics: Dict[str, Dict[str, Any]], v21_metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        policy.ask_max <= 95.0
        and policy.min_seconds_to_close >= 60.0
        and (current_metrics["all"]["median_ask"] or 100.0) <= 90.0
        and (v21_metrics["all"]["median_ask"] or 100.0) <= 90.0
        and (current_metrics["all"]["ask_eq_100"] or 0) == 0
        and (v21_metrics["all"]["ask_eq_100"] or 0) == 0
    )


def flatten(policy: Policy, current_metrics: Dict[str, Dict[str, Any]], v21_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    current_cov = coverage_pass(current_metrics)
    v21_cov = coverage_pass(v21_metrics)
    current_profit_all = profitable_all(current_metrics)
    v21_profit_all = profitable_all(v21_metrics)
    current_profit_oos = profitable_oos(current_metrics)
    v21_profit_oos = profitable_oos(v21_metrics)
    row: Dict[str, Any] = {
        "label": policy.label,
        "chooser": policy.chooser,
        "min_score": policy.min_score,
        "ask_max": policy.ask_max,
        "min_seconds_to_close": policy.min_seconds_to_close,
        "gate": policy.gate,
        "current_coverage_pass": current_cov,
        "v21_coverage_pass": v21_cov,
        "both_coverage_pass": current_cov and v21_cov,
        "current_profitable_all_splits": current_profit_all,
        "v21_profitable_all_splits": v21_profit_all,
        "both_profitable_all_splits": current_profit_all and v21_profit_all,
        "current_profitable_oos": current_profit_oos,
        "v21_profitable_oos": v21_profit_oos,
        "both_profitable_oos": current_profit_oos and v21_profit_oos,
        "nondegenerate": nondegenerate(policy, current_metrics, v21_metrics),
    }
    row["combined_all_net_pnl_cents"] = (current_metrics["all"]["net_pnl_cents"] or 0.0) + (
        v21_metrics["all"]["net_pnl_cents"] or 0.0
    )
    row["combined_all_gross_pnl_cents"] = (current_metrics["all"]["gross_pnl_cents"] or 0.0) + (
        v21_metrics["all"]["gross_pnl_cents"] or 0.0
    )
    row["min_all_accuracy"] = min(current_metrics["all"]["accuracy"] or 0.0, v21_metrics["all"]["accuracy"] or 0.0)
    row["min_all_coverage"] = min(current_metrics["all"]["coverage"] or 0.0, v21_metrics["all"]["coverage"] or 0.0)
    row["min_all_net_roi"] = min(current_metrics["all"]["net_roi_on_cost"] or -1.0, v21_metrics["all"]["net_roi_on_cost"] or -1.0)
    row["min_oos_net_roi"] = min(
        current_metrics[split]["net_roi_on_cost"] or -1.0
        for split in ["validation", "holdout"]
    )
    row["min_oos_net_roi"] = min(
        row["min_oos_net_roi"],
        min(v21_metrics[split]["net_roi_on_cost"] or -1.0 for split in ["validation", "holdout"]),
    )
    row["min_oos_edge_cents"] = min(
        current_metrics[split]["net_edge_per_selected_cents"] or -100.0
        for split in ["validation", "holdout"]
    )
    row["min_oos_edge_cents"] = min(
        row["min_oos_edge_cents"],
        min(v21_metrics[split]["net_edge_per_selected_cents"] or -100.0 for split in ["validation", "holdout"]),
    )
    row["min_accuracy_minus_break_even"] = min(
        current_metrics[split]["accuracy_minus_break_even"] or -1.0
        for split in ["all", "train", "validation", "holdout"]
    )
    row["min_accuracy_minus_break_even"] = min(
        row["min_accuracy_minus_break_even"],
        min(v21_metrics[split]["accuracy_minus_break_even"] or -1.0 for split in ["all", "train", "validation", "holdout"]),
    )
    row["max_median_ask"] = max(current_metrics["all"]["median_ask"] or 0.0, v21_metrics["all"]["median_ask"] or 0.0)
    row["max_ask_eq_100"] = max(current_metrics["all"]["ask_eq_100"] or 0, v21_metrics["all"]["ask_eq_100"] or 0)
    for prefix, metrics in [("current", current_metrics), ("v21", v21_metrics)]:
        for split, metric in metrics.items():
            for key, value in metric.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["both_coverage_pass"]),
        int(row["both_profitable_oos"]),
        int(row["both_profitable_all_splits"]),
        int(row["nondegenerate"]),
        row["min_oos_net_roi"],
        row["min_all_net_roi"],
        row["combined_all_net_pnl_cents"],
        row["min_accuracy_minus_break_even"],
        row["min_all_accuracy"],
        -(row["max_median_ask"] or 100.0),
        -int(row["max_ask_eq_100"] or 0),
    )


def scan() -> tuple[pd.DataFrame, Dict[str, Any]]:
    policies = make_profit_policies()
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
        "fee_model": "entry-only local Kalshi taker estimate: ceil(7*contracts*p*(100-p)/10000), min 1c",
    }
    return pd.DataFrame(rows), diagnostics


def add_table(lines: List[str], title: str, frame: pd.DataFrame) -> None:
    lines += [title, ""]
    if frame.empty:
        lines += ["No rows.", ""]
        return
    lines.append(
        "| rank | policy | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS ROI | median ask | ask=100 | oos profitable |"
    )
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for idx, row in enumerate(frame.head(15).to_dict("records"), start=1):
        lines.append(
            f"| {idx} | `{row['label']}` | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{fmt_roi(row['current_all_net_roi_on_cost'])} | "
            f"{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{fmt_roi(row['v21_all_net_roi_on_cost'])} | "
            f"{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_roi(row['min_oos_net_roi'])} | {fmt_cents(row['max_median_ask'])} | "
            f"{int(row['max_ask_eq_100'])} | {row['both_profitable_oos']} |"
        )
    lines.append("")


def write_report(path, generated: str, results: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    both_cov = results[results["both_coverage_pass"]]
    both_cov_profit_oos = both_cov[both_cov["both_profitable_oos"]]
    both_cov_profit_all = both_cov[both_cov["both_profitable_all_splits"]]
    nondeg_cov = both_cov[both_cov["nondegenerate"]]
    lines: List[str] = [
        "# Cross-Dataset Fee-Aware Profit Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Objective is fee-aware held-to-settlement profit while keeping at least 80% recurring-market coverage on both datasets.",
        "- The same policy grid is evaluated on current heartbeat data and independent v21 passive websocket data.",
        "- P&L uses one contract, logged ask as entry cost, and the local entry-only Kalshi taker fee estimate; no exit trade is assumed.",
        "",
        "## Data",
        "",
        f"- Current intervals: {diagnostics['current_intervals']}; rows: {diagnostics['current_side_rows']}",
        f"- V21 intervals: {diagnostics['v21_intervals']}; rows: {diagnostics['v21_side_rows']}",
        f"- Policies scanned: {diagnostics['policies']}",
        f"- Both-dataset 80%-coverage policies: {len(both_cov)}",
        f"- Both-dataset 80%-coverage policies profitable on validation and holdout splits: {len(both_cov_profit_oos)}",
        f"- Both-dataset 80%-coverage policies profitable on all splits: {len(both_cov_profit_all)}",
        f"- Nondegenerate both-dataset 80%-coverage policies: {len(nondeg_cov)}",
        f"- Fee model: `{diagnostics['fee_model']}`",
        "",
    ]
    add_table(lines, "## Top Both-Dataset 80%-Coverage Profit Policies", both_cov)
    add_table(lines, "## Top Nondegenerate 80%-Coverage Profit Policies", nondeg_cov)
    add_table(
        lines,
        "## Top 80%-Coverage Policies Profitable On Validation And Holdout",
        both_cov_profit_oos,
    )
    lines += ["## Read", ""]
    if both_cov.empty:
        lines.append("No policy in this grid met the 80% recurring-market coverage requirement on both datasets.")
    else:
        best = both_cov.iloc[0].to_dict()
        lines.append(f"- Best coverage-valid profit row: `{best['label']}`.")
        lines.append(
            f"- Current all split: {fmt_cents(best['current_all_net_pnl_cents'])} net, "
            f"{fmt_roi(best['current_all_net_roi_on_cost'])} ROI, "
            f"{pct(best['current_all_accuracy'])} accuracy at {pct(best['current_all_coverage'])} coverage."
        )
        lines.append(
            f"- V21 all split: {fmt_cents(best['v21_all_net_pnl_cents'])} net, "
            f"{fmt_roi(best['v21_all_net_roi_on_cost'])} ROI, "
            f"{pct(best['v21_all_accuracy'])} accuracy at {pct(best['v21_all_coverage'])} coverage."
        )
        lines.append(
            f"- Minimum validation/holdout ROI across both datasets is {fmt_roi(best['min_oos_net_roi'])}; "
            f"max median ask is {fmt_cents(best['max_median_ask'])}."
        )
    if both_cov_profit_oos.empty:
        lines.append("- No 80%-coverage policy was fee-aware profitable on both validation and holdout splits in both datasets.")
    if nondeg_cov.empty:
        lines.append("- No nondegenerate policy in this grid met the shared 80% coverage requirement.")
    elif nondeg_cov[nondeg_cov["both_profitable_oos"]].empty:
        lines.append("- Nondegenerate 80%-coverage rows exist, but none were profitable on every validation/holdout split across both datasets.")
    lines.append("- This is a profit-frontier falsification scan, not a live-trading promotion lock; fresh post-lock sample size remains required.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    results, diagnostics = scan()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_latest = OUT_DIR / "cross_dataset_profit_frontier_latest.csv"
    csv_stamp = OUT_DIR / f"cross_dataset_profit_frontier_{generated}.csv"
    json_latest = OUT_DIR / "cross_dataset_profit_frontier_latest.json"
    json_stamp = OUT_DIR / f"cross_dataset_profit_frontier_{generated}.json"
    md_latest = OUT_DIR / "cross_dataset_profit_frontier_latest.md"
    md_stamp = OUT_DIR / f"cross_dataset_profit_frontier_{generated}.md"
    results.to_csv(csv_latest, index=False)
    results.to_csv(csv_stamp, index=False)
    write_report(md_latest, generated, results, diagnostics)
    write_report(md_stamp, generated, results, diagnostics)
    both_cov = results[results["both_coverage_pass"]]
    summary = {
        "generated_utc": generated,
        "diagnostics": diagnostics,
        "both_coverage_count": int(results["both_coverage_pass"].sum()),
        "both_coverage_profitable_oos_count": int((results["both_coverage_pass"] & results["both_profitable_oos"]).sum()),
        "both_coverage_profitable_all_splits_count": int(
            (results["both_coverage_pass"] & results["both_profitable_all_splits"]).sum()
        ),
        "nondegenerate_both_coverage_count": int((results["both_coverage_pass"] & results["nondegenerate"]).sum()),
        "top_rows": results.head(25).to_dict("records"),
        "top_both_coverage_rows": both_cov.head(25).to_dict("records"),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(summary), indent=2, sort_keys=True), encoding="utf-8")
    print("Cross-dataset fee-aware profit frontier complete")
    print(f"policies={len(results)} both_coverage={int(results['both_coverage_pass'].sum())}")
    print(f"both_coverage_profitable_oos={int((results['both_coverage_pass'] & results['both_profitable_oos']).sum())}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
