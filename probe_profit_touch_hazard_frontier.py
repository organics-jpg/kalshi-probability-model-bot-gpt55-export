"""Touch-hazard profit frontier for BTC 15m interval policies.

Terminal Brownian probability can look acceptable while the path is close
enough to the strike that ordinary noise can repeatedly challenge the boundary.
This probe adds a first-passage-style hazard prior to the existing book and
terminal probability scores, then tests fee-aware profit while preserving at
least 80% recurring BTC 15-minute market coverage on current and v21 ledgers.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, split_metric
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)


@dataclass(frozen=True)
class HazardPolicy:
    chooser: str
    min_score: float
    ask_min: float
    ask_max: float
    min_seconds_to_close: float
    gate: str

    @property
    def label(self) -> str:
        return (
            f"choose={self.chooser}; {self.chooser}>={self.min_score:g}; "
            f"{self.ask_min:g}<=ask<={self.ask_max:g}; "
            f"sec>={self.min_seconds_to_close:g}; gate={self.gate}"
        )


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def norm_cdf(values: pd.Series) -> pd.Series:
    arr = pd.to_numeric(values, errors="coerce").astype(float)
    erf = np.vectorize(lambda x: math.erf(x / math.sqrt(2.0)) if math.isfinite(x) else np.nan)
    return pd.Series(0.5 * (1.0 + erf(arr.to_numpy())), index=arr.index)


def touch_loss_from_z(z: pd.Series) -> pd.Series:
    values = pd.to_numeric(z, errors="coerce").astype(float)
    terminal_tail = 1.0 - norm_cdf(values.clip(lower=0.0))
    # Reflection-principle approximation for crossing the adverse boundary at
    # least once before expiry under zero drift: P(touch) ~= 2 * terminal tail.
    touch = 2.0 * terminal_tail
    touch = touch.where(values > 0.0, 1.0)
    return touch.clip(lower=0.0, upper=1.0)


def add_touch_hazard_scores(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    numeric_cols = [
        "book_p_side",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "brownian_p_rv_60m",
        "drift_p_5m_rv_15m",
        "drift_p_15m_rv_15m",
        "margin_per_rv_sigma_15m",
        "margin_per_rv_sigma_30m",
        "margin_per_rv_sigma_60m",
        "adverse_move_5m",
        "adverse_move_15m",
        "ask_cents",
        "seconds_to_close",
        "spread_cents",
    ]
    for col in numeric_cols:
        if col not in out.columns:
            out[col] = np.nan
        out[col] = pd.to_numeric(out[col], errors="coerce")

    for horizon in ["15m", "30m", "60m"]:
        z_col = f"margin_per_rv_sigma_{horizon}"
        loss_col = f"touch_loss_rv_{horizon}"
        surv_col = f"touch_survival_rv_{horizon}"
        out[loss_col] = touch_loss_from_z(out[z_col])
        out[surv_col] = (1.0 - out[loss_col]).clip(lower=0.0, upper=1.0)

    out["touch_survival_min_15_30"] = out[["touch_survival_rv_15m", "touch_survival_rv_30m"]].min(axis=1)
    out["touch_loss_max_15_30"] = out[["touch_loss_rv_15m", "touch_loss_rv_30m"]].max(axis=1)
    out["adverse_norm_15m"] = (out["adverse_move_15m"] / 50.0).clip(lower=0.0, upper=1.0)

    out["touch_terminal_blend_15"] = (
        0.70 * out["brownian_p_rv_15m"] + 0.30 * out["touch_survival_rv_15m"]
    )
    out["touch_terminal_blend_30"] = (
        0.70 * out["brownian_p_rv_30m"] + 0.30 * out["touch_survival_rv_30m"]
    )
    out["book_touch_blend_15"] = (
        0.55 * out["book_p_side"]
        + 0.25 * out["brownian_p_rv_15m"]
        + 0.20 * out["touch_survival_rv_15m"]
    )
    out["book_touch_drift_15"] = (
        0.45 * out["book_p_side"]
        + 0.25 * out["brownian_p_rv_15m"]
        + 0.20 * out["touch_survival_rv_15m"]
        + 0.10 * out["drift_p_5m_rv_15m"]
    )
    out["hazard_discounted_book_15"] = out["book_p_side"] - 0.25 * out["touch_loss_rv_15m"]
    out["hazard_discounted_mean_15"] = (
        0.50 * out["book_p_side"]
        + 0.50 * out["brownian_p_rv_15m"]
        - 0.25 * out["touch_loss_rv_15m"]
    )
    out["kinetic_touch_score_15"] = (
        0.40 * out["book_p_side"]
        + 0.30 * out["brownian_p_rv_15m"]
        + 0.20 * out["drift_p_5m_rv_15m"]
        + 0.10 * out["touch_survival_rv_15m"]
        - 0.05 * out["adverse_norm_15m"]
    )
    out["touch_margin_energy_15"] = (
        out["touch_survival_rv_15m"] - 0.20 * out["adverse_norm_15m"] + 0.10 * out["drift_p_5m_rv_15m"]
    )
    return out


def make_policies() -> List[HazardPolicy]:
    choosers = [
        "touch_terminal_blend_15",
        "book_touch_blend_15",
        "book_touch_drift_15",
        "hazard_discounted_mean_15",
        "kinetic_touch_score_15",
        "touch_margin_energy_15",
    ]
    thresholds = [0.35, 0.45, 0.50, 0.55, 0.60]
    ask_mins = [0.0, 50.0]
    ask_maxes = [80.0, 95.0, 100.0]
    min_seconds = [60.0, 120.0]
    gates = [
        "none",
        "touch_loss15<=0.90",
        "touch_loss15<=0.80",
        "touch_loss15<=0.85_or_adverse15<=10",
    ]
    policies: List[HazardPolicy] = []
    for chooser in choosers:
        for threshold in thresholds:
            for ask_min in ask_mins:
                for ask_max in ask_maxes:
                    if ask_min > ask_max:
                        continue
                    for min_sec in min_seconds:
                        for gate in gates:
                            policies.append(HazardPolicy(chooser, threshold, ask_min, ask_max, min_sec, gate))
    return policies


def gate_mask(rows: pd.DataFrame, policy: HazardPolicy) -> pd.Series:
    mask = (
        rows[policy.chooser].ge(policy.min_score)
        & rows["ask_cents"].ge(policy.ask_min)
        & rows["ask_cents"].le(policy.ask_max)
        & rows["seconds_to_close"].ge(policy.min_seconds_to_close)
    )
    if policy.gate == "none":
        return mask.fillna(False)
    if policy.gate == "touch_loss15<=0.90":
        mask &= rows["touch_loss_rv_15m"].le(0.90)
    elif policy.gate == "touch_loss15<=0.80":
        mask &= rows["touch_loss_rv_15m"].le(0.80)
    elif policy.gate == "touch_loss30<=0.85":
        mask &= rows["touch_loss_rv_30m"].le(0.85)
    elif policy.gate == "touch_loss15<=0.90_or_margin15>=0.25":
        mask &= rows["touch_loss_rv_15m"].le(0.90) | rows["margin_per_rv_sigma_15m"].ge(0.25)
    elif policy.gate == "touch_loss15<=0.85_or_adverse15<=10":
        mask &= rows["touch_loss_rv_15m"].le(0.85) | rows["adverse_move_15m"].le(10.0)
    elif policy.gate == "spread<=4":
        mask &= rows["spread_cents"].le(4.0)
    else:
        raise ValueError(f"unknown gate: {policy.gate}")
    return mask.fillna(False)


def select_markets(chosen: pd.DataFrame, policy: HazardPolicy) -> pd.DataFrame:
    if chosen.empty:
        return chosen.copy()
    eligible = chosen[gate_mask(chosen, policy)].copy()
    if eligible.empty:
        return eligible
    return (
        eligible.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )


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


def nondegenerate(policy: HazardPolicy, current_metrics: Dict[str, Dict[str, Any]], v21_metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        policy.ask_max <= 95.0
        and policy.min_seconds_to_close >= 60.0
        and (current_metrics["all"]["median_ask"] or 100.0) <= 90.0
        and (v21_metrics["all"]["median_ask"] or 100.0) <= 90.0
        and (current_metrics["all"]["ask_eq_100"] or 0) == 0
        and (v21_metrics["all"]["ask_eq_100"] or 0) == 0
    )


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    enriched = enrich_selected(selected)
    return {split: split_metric(base, enriched, split) for split in ["all", "train", "validation", "holdout"]}


def evaluate_dataset(base: pd.DataFrame, side_rows: pd.DataFrame, policies: List[HazardPolicy]) -> Dict[str, Dict[str, Any]]:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen_cache = {
        chooser: choose_decision_sides(rows, chooser)
        for chooser in sorted({policy.chooser for policy in policies})
    }
    empty = rows.iloc[0:0].copy()
    out: Dict[str, Dict[str, Any]] = {}
    for policy in policies:
        selected = select_markets(chosen_cache.get(policy.chooser, empty), policy)
        out[policy.label] = {"selected": enrich_selected(selected), "metrics": metrics_for(base, selected)}
    return out


def flatten(policy: HazardPolicy, current_metrics: Dict[str, Dict[str, Any]], v21_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "label": policy.label,
        "chooser": policy.chooser,
        "min_score": policy.min_score,
        "ask_min": policy.ask_min,
        "ask_max": policy.ask_max,
        "min_seconds_to_close": policy.min_seconds_to_close,
        "gate": policy.gate,
        "current_coverage_pass": coverage_pass(current_metrics),
        "v21_coverage_pass": coverage_pass(v21_metrics),
        "current_profitable_oos": profitable_oos(current_metrics),
        "v21_profitable_oos": profitable_oos(v21_metrics),
        "current_profitable_all_splits": profitable_all(current_metrics),
        "v21_profitable_all_splits": profitable_all(v21_metrics),
        "nondegenerate": nondegenerate(policy, current_metrics, v21_metrics),
    }
    row["both_coverage_pass"] = row["current_coverage_pass"] and row["v21_coverage_pass"]
    row["both_profitable_oos"] = row["current_profitable_oos"] and row["v21_profitable_oos"]
    row["both_profitable_all_splits"] = row["current_profitable_all_splits"] and row["v21_profitable_all_splits"]
    row["combined_all_net_pnl_cents"] = (current_metrics["all"]["net_pnl_cents"] or 0.0) + (
        v21_metrics["all"]["net_pnl_cents"] or 0.0
    )
    row["min_all_net_roi"] = min(current_metrics["all"]["net_roi_on_cost"] or -1.0, v21_metrics["all"]["net_roi_on_cost"] or -1.0)
    row["min_oos_net_roi"] = min(
        min(current_metrics[split]["net_roi_on_cost"] or -1.0 for split in ["validation", "holdout"]),
        min(v21_metrics[split]["net_roi_on_cost"] or -1.0 for split in ["validation", "holdout"]),
    )
    row["min_accuracy_minus_break_even"] = min(
        min(current_metrics[split]["accuracy_minus_break_even"] or -1.0 for split in ["all", "train", "validation", "holdout"]),
        min(v21_metrics[split]["accuracy_minus_break_even"] or -1.0 for split in ["all", "train", "validation", "holdout"]),
    )
    row["min_all_coverage"] = min(current_metrics["all"]["coverage"] or 0.0, v21_metrics["all"]["coverage"] or 0.0)
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
        -(row["max_median_ask"] or 100.0),
        -int(row["max_ask_eq_100"] or 0),
    )


def scan() -> tuple[pd.DataFrame, Dict[str, Any]]:
    policies = make_policies()
    current_side = add_touch_hazard_scores(load_side_rows())
    current_base = market_base(current_side)
    v21_side = add_touch_hazard_scores(load_v21_side_rows())
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


def add_table(lines: List[str], title: str, frame: pd.DataFrame) -> None:
    lines += [title, ""]
    if frame.empty:
        lines += ["No rows.", ""]
        return
    lines.append(
        "| rank | policy | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS ROI | median ask | ask=100 |"
    )
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|")
    for idx, row in enumerate(frame.head(15).to_dict("records"), start=1):
        lines.append(
            f"| {idx} | `{row['label']}` | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{fmt_roi(row['current_all_net_roi_on_cost'])} | "
            f"{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{fmt_roi(row['v21_all_net_roi_on_cost'])} | "
            f"{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_roi(row['min_oos_net_roi'])} | {fmt_cents(row['max_median_ask'])} | "
            f"{int(row['max_ask_eq_100'])} |"
        )
    lines.append("")


def write_report(path, generated: str, results: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    both_cov = results[results["both_coverage_pass"]]
    both_cov_profit_oos = both_cov[both_cov["both_profitable_oos"]]
    both_cov_profit_all = both_cov[both_cov["both_profitable_all_splits"]]
    nondeg_cov = both_cov[both_cov["nondegenerate"]]
    lines: List[str] = [
        "# Touch-Hazard Profit Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Adds first-passage-style touch hazard to terminal Brownian/book scores.",
        "- Objective is fee-aware held-to-settlement profit while keeping at least 80% recurring-market coverage on both datasets.",
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
        "",
    ]
    add_table(lines, "## Top Both-Dataset 80%-Coverage Touch-Hazard Policies", both_cov)
    add_table(lines, "## Top Nondegenerate 80%-Coverage Touch-Hazard Policies", nondeg_cov)
    add_table(lines, "## Top 80%-Coverage Policies Profitable On Validation And Holdout", both_cov_profit_oos)
    lines += ["## Read", ""]
    if both_cov.empty:
        lines.append("- No touch-hazard policy in this grid met the 80% recurring-market coverage requirement on both datasets.")
    else:
        best = both_cov.iloc[0].to_dict()
        lines.append(f"- Best coverage-valid touch-hazard row: `{best['label']}`.")
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
        lines.append("- No 80%-coverage touch-hazard policy was profitable on both validation and holdout splits in both datasets.")
    if not both_cov_profit_all.empty:
        best_all = both_cov_profit_all.iloc[0].to_dict()
        lines.append(f"- Best all-split-positive touch-hazard row: `{best_all['label']}`.")
    lines.append("- Touch hazard is a physics falsification prior, not a live-trading promotion lock; fresh post-lock sample size remains required.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    results, diagnostics = scan()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_latest = OUT_DIR / "profit_touch_hazard_frontier_latest.csv"
    csv_stamp = OUT_DIR / f"profit_touch_hazard_frontier_{generated}.csv"
    json_latest = OUT_DIR / "profit_touch_hazard_frontier_latest.json"
    json_stamp = OUT_DIR / f"profit_touch_hazard_frontier_{generated}.json"
    md_latest = OUT_DIR / "profit_touch_hazard_frontier_latest.md"
    md_stamp = OUT_DIR / f"profit_touch_hazard_frontier_{generated}.md"
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
    for out_path in [json_latest, json_stamp]:
        out_path.write_text(json.dumps(clean_json_local(summary), indent=2, sort_keys=True), encoding="utf-8")
    print("Touch-hazard profit frontier complete")
    print(f"policies={len(results)} both_coverage={int(results['both_coverage_pass'].sum())}")
    print(f"both_coverage_profitable_oos={int((results['both_coverage_pass'] & results['both_profitable_oos']).sum())}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
