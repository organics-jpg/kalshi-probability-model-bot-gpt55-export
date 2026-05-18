"""Causal blocker overlays for the locked BTC 15m profit candidate.

The locked profit candidate is kept unchanged for forward validation. This
separate challenger scan asks whether simple pre-entry blockers can remove
known weak slices while preserving at least 80% recurring-market coverage on
both current and independent v21 interval datasets.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import itertools
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
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
    Policy,
    choose_decision_sides,
    clean_json,
    gate_mask,
    load_side_rows,
    market_base,
    pct,
)
from probe_profit_frontier_fresh_validation import LOCK_PATH, policy_from_record


@dataclass(frozen=True)
class Overlay:
    label: str
    clauses: tuple[str, ...]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def numeric(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series(np.nan, index=df.index)
    return pd.to_numeric(df[col], errors="coerce")


def clause_mask(chosen: pd.DataFrame, clause: str) -> pd.Series:
    if clause == "none":
        return pd.Series(True, index=chosen.index)
    if clause.startswith("ask>="):
        return numeric(chosen, "ask_cents").ge(float(clause.split(">=", 1)[1]))
    if clause.startswith("ask<="):
        return numeric(chosen, "ask_cents").le(float(clause.split("<=", 1)[1]))
    if clause.startswith("brownian15>="):
        return numeric(chosen, "brownian_p_rv_15m").ge(float(clause.split(">=", 1)[1]))
    if clause.startswith("brownian30>="):
        return numeric(chosen, "brownian_p_rv_30m").ge(float(clause.split(">=", 1)[1]))
    if clause.startswith("book>="):
        return numeric(chosen, "book_p_side").ge(float(clause.split(">=", 1)[1]))
    if clause.startswith("mean_book_rv15>="):
        return numeric(chosen, "score_mean_book_rv15").ge(float(clause.split(">=", 1)[1]))
    if clause.startswith("margin_rv15>="):
        return numeric(chosen, "margin_per_rv_sigma_15m").ge(float(clause.split(">=", 1)[1]))
    if clause.startswith("adverse15<="):
        return numeric(chosen, "adverse_move_15m").le(float(clause.split("<=", 1)[1]))
    if clause.startswith("seconds<="):
        return numeric(chosen, "seconds_to_close").le(float(clause.split("<=", 1)[1]))
    raise ValueError(f"unknown overlay clause: {clause}")


def overlay_mask(chosen: pd.DataFrame, overlay: Overlay) -> pd.Series:
    mask = pd.Series(True, index=chosen.index)
    for clause in overlay.clauses:
        mask &= clause_mask(chosen, clause)
    return mask.fillna(False)


def make_overlays() -> List[Overlay]:
    atomic = [
        "ask>=50",
        "ask>=55",
        "ask>=60",
        "ask<=80",
        "ask<=90",
        "brownian15>=0.60",
        "brownian15>=0.65",
        "brownian30>=0.55",
        "brownian30>=0.60",
        "book>=0.55",
        "book>=0.60",
        "mean_book_rv15>=0.55",
        "mean_book_rv15>=0.60",
        "margin_rv15>=0.50",
        "margin_rv15>=0.75",
        "adverse15<=10",
        "adverse15<=20",
        "seconds<=480",
        "seconds<=720",
    ]
    overlays = [Overlay("none", ("none",))]
    overlays.extend(Overlay(clause, (clause,)) for clause in atomic)
    for left, right in itertools.combinations(atomic, 2):
        if left.split(">=", 1)[0] == right.split(">=", 1)[0] and ">=" in left and ">=" in right:
            continue
        if left.split("<=", 1)[0] == right.split("<=", 1)[0] and "<=" in left and "<=" in right:
            continue
        overlays.append(Overlay(f"{left} AND {right}", (left, right)))
    return overlays


def select_with_overlay(side_rows: pd.DataFrame, base: pd.DataFrame, policy: Policy, overlay: Overlay) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    if chosen.empty:
        return enrich_selected(chosen)
    eligible = chosen[gate_mask(chosen, policy) & overlay_mask(chosen, overlay)].copy()
    if eligible.empty:
        return enrich_selected(eligible)
    selected = (
        eligible.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    return enrich_selected(selected)


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def positive_splits(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["all", "train", "validation", "holdout"])


def positive_oos(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])


def flatten(
    overlay: Overlay,
    current_metrics: Dict[str, Dict[str, Any]],
    v21_metrics: Dict[str, Dict[str, Any]],
    current_fresh_metrics: Dict[str, Any],
) -> Dict[str, Any]:
    current_cov = coverage_pass(current_metrics)
    v21_cov = coverage_pass(v21_metrics)
    current_pos = positive_splits(current_metrics)
    v21_pos = positive_splits(v21_metrics)
    current_oos = positive_oos(current_metrics)
    v21_oos = positive_oos(v21_metrics)
    row: Dict[str, Any] = {
        "overlay": overlay.label,
        "clauses": " AND ".join(overlay.clauses),
        "both_coverage_pass": current_cov and v21_cov,
        "current_coverage_pass": current_cov,
        "v21_coverage_pass": v21_cov,
        "both_positive_all_splits": current_pos and v21_pos,
        "both_positive_oos": current_oos and v21_oos,
        "combined_all_net_pnl_cents": (current_metrics["all"]["net_pnl_cents"] or 0.0)
        + (v21_metrics["all"]["net_pnl_cents"] or 0.0),
        "min_all_roi": min(current_metrics["all"]["net_roi_on_cost"] or -1.0, v21_metrics["all"]["net_roi_on_cost"] or -1.0),
        "min_oos_roi": min(
            current_metrics[split]["net_roi_on_cost"] or -1.0
            for split in ["validation", "holdout"]
        ),
        "min_train_roi": min(current_metrics["train"]["net_roi_on_cost"] or -1.0, v21_metrics["train"]["net_roi_on_cost"] or -1.0),
        "max_median_ask": max(current_metrics["all"]["median_ask"] or 0.0, v21_metrics["all"]["median_ask"] or 0.0),
    }
    row["min_oos_roi"] = min(
        row["min_oos_roi"],
        min(v21_metrics[split]["net_roi_on_cost"] or -1.0 for split in ["validation", "holdout"]),
    )
    for prefix, metrics in [("current", current_metrics), ("v21", v21_metrics)]:
        for split, metric in metrics.items():
            for key, value in metric.items():
                row[f"{prefix}_{split}_{key}"] = value
    for key, value in current_fresh_metrics.items():
        row[f"current_fresh_{key}"] = value
    return row


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["both_coverage_pass"]),
        int(row["both_positive_all_splits"]),
        int(row["both_positive_oos"]),
        row["min_train_roi"],
        row["min_oos_roi"],
        row["min_all_roi"],
        row["combined_all_net_pnl_cents"],
        -(row["max_median_ask"] or 100.0),
    )


def scan() -> tuple[pd.DataFrame, Dict[str, Any]]:
    if not LOCK_PATH.exists():
        raise SystemExit(f"Missing profit lock: {LOCK_PATH}")
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    policy = policy_from_record(lock["policy"])
    overlays = make_overlays()
    current_side = load_side_rows()
    current_base = market_base(current_side)
    v21_side = load_v21_side_rows()
    v21_base = market_base(v21_side)
    lock_close_dt = pd.to_datetime(lock.get("lock_close_dt"), utc=True, errors="coerce")
    if pd.isna(lock_close_dt):
        current_fresh_base = current_base.iloc[0:0].copy()
    else:
        current_fresh_base = current_base[
            pd.to_datetime(current_base["close_dt"], utc=True, errors="coerce") > lock_close_dt
        ].copy()
    rows: List[Dict[str, Any]] = []
    for overlay in overlays:
        current_selected = select_with_overlay(current_side, current_base, policy, overlay)
        v21_selected = select_with_overlay(v21_side, v21_base, policy, overlay)
        current_fresh_selected = current_selected[current_selected["market"].isin(set(current_fresh_base["market"]))].copy()
        rows.append(
            flatten(
                overlay,
                metrics_for(current_base, current_selected),
                metrics_for(v21_base, v21_selected),
                split_metric(current_fresh_base, current_fresh_selected, "all"),
            )
        )
    rows.sort(key=rank_key, reverse=True)
    diagnostics = {
        "current_intervals": int(len(current_base)),
        "current_side_rows": int(len(current_side)),
        "v21_intervals": int(len(v21_base)),
        "v21_side_rows": int(len(v21_side)),
        "overlays": int(len(overlays)),
        "locked_policy": lock["policy"],
        "lock_close_dt": lock.get("lock_close_dt"),
    }
    return pd.DataFrame(rows), diagnostics


def write_report(path: Path, generated: str, results: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    both_cov = results[results["both_coverage_pass"]]
    both_all = both_cov[both_cov["both_positive_all_splits"]]
    lines: List[str] = [
        "# Locked Profit Candidate Blocker Overlays",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only challenger scan; no orders are submitted and no bot files or live processes are touched.",
        "- The locked candidate itself is not changed. Overlays are candidate refinements for falsification.",
        "- Each overlay is causal and applied before first-per-market selection.",
        "- Ranking requires 80% recurring-market coverage across current and v21 before rewarding profitability.",
        "",
        "## Data",
        "",
        f"- Locked policy: `{diagnostics['locked_policy']['label']}`",
        f"- Lock close time: `{diagnostics['lock_close_dt']}`",
        f"- Current intervals: {diagnostics['current_intervals']}; rows: {diagnostics['current_side_rows']}",
        f"- V21 intervals: {diagnostics['v21_intervals']}; rows: {diagnostics['v21_side_rows']}",
        f"- Overlays scanned: {diagnostics['overlays']}",
        f"- Both-dataset 80%-coverage overlays: {len(both_cov)}",
        f"- Both-dataset 80%-coverage overlays positive on all splits: {len(both_all)}",
        "",
        "## Top Coverage-Preserving Overlays",
        "",
        "| rank | overlay | current net/ROI | current train | current acc/cov | v21 net/ROI | v21 train | v21 acc/cov | fresh net/cov | min OOS ROI | median ask |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(both_cov.head(15).to_dict("records"), start=1):
        lines.append(
            f"| {idx} | `{row['overlay']}` | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{fmt_roi(row['current_all_net_roi_on_cost'])} | "
            f"{fmt_cents(row['current_train_net_pnl_cents'])}/{fmt_roi(row['current_train_net_roi_on_cost'])} | "
            f"{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{fmt_roi(row['v21_all_net_roi_on_cost'])} | "
            f"{fmt_cents(row['v21_train_net_pnl_cents'])}/{fmt_roi(row['v21_train_net_roi_on_cost'])} | "
            f"{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_cents(row['current_fresh_net_pnl_cents'])}/{pct(row['current_fresh_coverage'])} | "
            f"{fmt_roi(row['min_oos_roi'])} | {fmt_cents(row['max_median_ask'])} |"
        )
    lines += ["", "## Read", ""]
    baseline = results[results["overlay"] == "none"]
    if not baseline.empty:
        base = baseline.iloc[0].to_dict()
        lines.append(
            f"- Baseline locked candidate: current {fmt_cents(base['current_all_net_pnl_cents'])}, "
            f"v21 {fmt_cents(base['v21_all_net_pnl_cents'])}, current train {fmt_cents(base['current_train_net_pnl_cents'])}."
        )
    if both_all.empty:
        lines.append("- No overlay preserved 80% coverage and made every train/validation/holdout split positive on both datasets.")
    else:
        best = both_all.iloc[0].to_dict()
        lines.append(
            f"- Best all-split-positive overlay: `{best['overlay']}` with current "
            f"{fmt_cents(best['current_all_net_pnl_cents'])} and v21 {fmt_cents(best['v21_all_net_pnl_cents'])}."
        )
        lines.append("- This is a challenger only; it should not replace the locked fresh validation candidate without its own forward lock.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    results, diagnostics = scan()
    csv_latest = OUT_DIR / "locked_profit_candidate_blocker_overlays_latest.csv"
    csv_stamp = OUT_DIR / f"locked_profit_candidate_blocker_overlays_{generated}.csv"
    json_latest = OUT_DIR / "locked_profit_candidate_blocker_overlays_latest.json"
    json_stamp = OUT_DIR / f"locked_profit_candidate_blocker_overlays_{generated}.json"
    md_latest = OUT_DIR / "locked_profit_candidate_blocker_overlays_latest.md"
    md_stamp = OUT_DIR / f"locked_profit_candidate_blocker_overlays_{generated}.md"
    results.to_csv(csv_latest, index=False)
    results.to_csv(csv_stamp, index=False)
    write_report(md_latest, generated, results, diagnostics)
    write_report(md_stamp, generated, results, diagnostics)
    summary = {
        "generated_utc": generated,
        "diagnostics": diagnostics,
        "both_coverage_count": int(results["both_coverage_pass"].sum()),
        "both_coverage_positive_all_splits_count": int(
            (results["both_coverage_pass"] & results["both_positive_all_splits"]).sum()
        ),
        "top_rows": results.head(25).to_dict("records"),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(summary), indent=2, sort_keys=True), encoding="utf-8")
    print("Locked profit candidate blocker overlay scan complete")
    print(f"overlays={len(results)} both_coverage={int(results['both_coverage_pass'].sum())}")
    print(f"positive_all={int((results['both_coverage_pass'] & results['both_positive_all_splits']).sum())}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
