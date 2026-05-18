"""Fresh validation harness for the locked BTC 15m profit-frontier candidate.

This locks the best cross-dataset fee-aware profit policy the first time it is
run, then evaluates only newly resolved recurring markets after that lock on
later runs. It is intended to prevent silent retuning on the same live capture.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, split_metric
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)
from probe_profit_lock_time_boundary import effective_lock_dt


FRONTIER_CSV = OUT_DIR / "cross_dataset_profit_frontier_latest.csv"
LOCK_PATH = OUT_DIR / "profit_frontier_fresh_lock.json"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def policy_from_record(record: Dict[str, Any]) -> Policy:
    return Policy(
        chooser=str(record["chooser"]),
        min_score=float(record["min_score"]),
        ask_max=float(record["ask_max"]),
        min_seconds_to_close=float(record["min_seconds_to_close"]),
        gate=str(record["gate"]),
    )


def choose_lock_policy() -> Dict[str, Any]:
    if not FRONTIER_CSV.exists():
        raise SystemExit(f"Missing profit frontier CSV: {FRONTIER_CSV}")
    rows = pd.read_csv(FRONTIER_CSV)
    for col in ["both_coverage_pass", "both_profitable_all_splits", "both_profitable_oos", "nondegenerate"]:
        rows[col] = rows[col].astype(str).str.lower().isin({"true", "1", "yes"})
    eligible = rows[
        rows["both_coverage_pass"]
        & rows["both_profitable_all_splits"]
        & rows["both_profitable_oos"]
        & rows["nondegenerate"]
    ].copy()
    if eligible.empty:
        raise SystemExit("No eligible profit frontier lock candidate found")
    return eligible.iloc[0].to_dict()


def load_or_create_lock(base: pd.DataFrame) -> Dict[str, Any]:
    if LOCK_PATH.exists():
        return json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    record = choose_lock_policy()
    lock_close_dt = pd.to_datetime(base["close_dt"], utc=True, errors="coerce").max()
    lock = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "lock_close_dt": lock_close_dt.isoformat() if not pd.isna(lock_close_dt) else None,
        "source_frontier_csv": str(FRONTIER_CSV),
        "policy": {
            "chooser": str(record["chooser"]),
            "min_score": float(record["min_score"]),
            "ask_max": float(record["ask_max"]),
            "min_seconds_to_close": float(record["min_seconds_to_close"]),
            "gate": str(record["gate"]),
            "label": str(record["label"]),
        },
        "discovery_metrics": {
            key: clean_json_local(record.get(key))
            for key in [
                "current_all_net_pnl_cents",
                "current_all_net_roi_on_cost",
                "current_all_accuracy",
                "current_all_coverage",
                "v21_all_net_pnl_cents",
                "v21_all_net_roi_on_cost",
                "v21_all_accuracy",
                "v21_all_coverage",
                "min_oos_net_roi",
                "max_median_ask",
            ]
        },
    }
    LOCK_PATH.write_text(json.dumps(clean_json_local(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def select_for_policy(side_rows: pd.DataFrame, base: pd.DataFrame, policy: Policy) -> pd.DataFrame:
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(side_rows, policy.chooser)
    selected = enrich_selected(select_markets_from_chosen(chosen, policy))
    return selected


def metric_for_scope(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metric = split_metric(base, selected, "all")
    metric["coverage_pass"] = (metric["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
    metric["wilson_minus_break_even"] = (
        (metric["wilson95_lower"] or 0.0) - (metric["fee_aware_break_even_accuracy"] or 1.0)
    )
    metric["positive_net"] = (metric["net_pnl_cents"] or 0.0) > 0.0
    return metric


def fmt_num(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.3f}"


def write_report(path: Path, generated: str, lock: Dict[str, Any], all_metric: Dict[str, Any], fresh_metric: Dict[str, Any]) -> None:
    policy = lock["policy"]
    effective_dt = effective_lock_dt(lock)
    lines = [
        "# Profit Frontier Fresh Validation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only validation; no orders are submitted and no bot files or live processes are touched.",
        "- The policy is locked on first run and future runs evaluate only recurring markets closing after the lock close time.",
        "- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.",
        "",
        "## Locked Policy",
        "",
        f"- Label: `{policy['label']}`",
        f"- Lock close time: `{lock.get('lock_close_dt')}`",
        f"- Effective entry boundary: `{effective_dt.isoformat() if not pd.isna(effective_dt) else None}`",
        f"- Lock file: `{LOCK_PATH}`",
        "",
        "## Metrics",
        "",
        "| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, metric in [("all current ledger", all_metric), ("fresh after lock", fresh_metric)]:
        lines.append(
            f"| {name} | {int(metric['markets'])}/{int(metric['base_markets'])} | "
            f"{int(metric['wins'])}/{int(metric['losses'])} | {pct(metric['accuracy'])} | "
            f"{pct(metric['fee_aware_break_even_accuracy'])} | {pct(metric['wilson95_lower'])} | "
            f"{fmt_num(metric['wilson_minus_break_even'])} | {pct(metric['coverage'])} | "
            f"{fmt_cents(metric['net_pnl_cents'])} | {fmt_roi(metric['net_roi_on_cost'])} | "
            f"{fmt_cents(metric['median_ask'])} |"
        )
    lines += ["", "## Read", ""]
    if fresh_metric["base_markets"] == 0:
        lines.append("- Fresh validation has just been locked; no post-lock resolved markets are available yet.")
    else:
        lines.append(
            f"- Fresh selected {int(fresh_metric['markets'])}/{int(fresh_metric['base_markets'])} markets "
            f"({pct(fresh_metric['coverage'])}) with {fmt_cents(fresh_metric['net_pnl_cents'])} net P&L."
        )
        if fresh_metric["positive_net"] and fresh_metric["coverage_pass"]:
            lines.append("- Fresh sample is positive and coverage-valid so far, but Wilson edge/sample size must continue accumulating.")
        else:
            lines.append("- Fresh sample is not yet a promotion-quality proof.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    side_rows = load_side_rows()
    base = market_base(side_rows)
    lock = load_or_create_lock(base)
    policy = policy_from_record(lock["policy"])
    selected = select_for_policy(side_rows, base, policy)
    all_metric = metric_for_scope(base, selected)

    lock_close_dt = effective_lock_dt(lock)
    if pd.isna(lock_close_dt):
        fresh_base = base.iloc[0:0].copy()
    else:
        fresh_base = base[pd.to_datetime(base["close_dt"], utc=True, errors="coerce") > lock_close_dt].copy()
    if fresh_base.empty or pd.isna(lock_close_dt):
        fresh_selected = selected.iloc[0:0].copy()
    else:
        entry_dt = pd.to_datetime(side_rows["entry_dt"], utc=True, errors="coerce")
        fresh_side_rows = side_rows[
            entry_dt.gt(lock_close_dt) & side_rows["market"].isin(set(fresh_base["market"]))
        ].copy()
        fresh_selected = select_for_policy(fresh_side_rows, fresh_base, policy)
    fresh_metric = metric_for_scope(fresh_base, fresh_selected)

    md_latest = OUT_DIR / "profit_frontier_fresh_validation_latest.md"
    md_stamp = OUT_DIR / f"profit_frontier_fresh_validation_{generated}.md"
    json_latest = OUT_DIR / "profit_frontier_fresh_validation_latest.json"
    json_stamp = OUT_DIR / f"profit_frontier_fresh_validation_{generated}.json"
    write_report(md_latest, generated, lock, all_metric, fresh_metric)
    write_report(md_stamp, generated, lock, all_metric, fresh_metric)
    payload = {
        "generated_utc": generated,
        "lock": lock,
        "all_metric": all_metric,
        "fresh_metric": fresh_metric,
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Profit frontier fresh validation complete")
    print(f"fresh_markets={fresh_metric['markets']} fresh_base={fresh_metric['base_markets']}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
