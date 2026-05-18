"""Fresh validation for the touch-hazard profit candidate.

The touch-hazard frontier creates a new physics hypothesis, so it gets its own
forward lock. The lock freezes the best all-split-positive, 80%-coverage row
from the latest touch-hazard scan and evaluates only markets after the lock
close time on future runs.

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
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)
from probe_profit_touch_hazard_frontier import HazardPolicy, add_touch_hazard_scores, select_markets
from probe_profit_lock_time_boundary import effective_lock_dt


FRONTIER_CSV = OUT_DIR / "profit_touch_hazard_frontier_latest.csv"
TOUCH_LOCK_PATH = OUT_DIR / "profit_touch_hazard_fresh_lock.json"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def bool_col(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def choose_touch_candidate() -> Dict[str, Any]:
    if not FRONTIER_CSV.exists():
        raise SystemExit(f"Missing touch-hazard frontier CSV: {FRONTIER_CSV}")
    rows = pd.read_csv(FRONTIER_CSV)
    for col in ["both_coverage_pass", "both_profitable_all_splits", "nondegenerate"]:
        rows[col] = bool_col(rows[col])
    eligible = rows[rows["both_coverage_pass"] & rows["both_profitable_all_splits"] & rows["nondegenerate"]].copy()
    if eligible.empty:
        raise SystemExit("No nondegenerate all-split-positive touch-hazard candidate found")
    return eligible.iloc[0].to_dict()


def policy_from_record(record: Dict[str, Any]) -> HazardPolicy:
    return HazardPolicy(
        chooser=str(record["chooser"]),
        min_score=float(record["min_score"]),
        ask_min=float(record["ask_min"]),
        ask_max=float(record["ask_max"]),
        min_seconds_to_close=float(record["min_seconds_to_close"]),
        gate=str(record["gate"]),
    )


def load_or_create_lock(base: pd.DataFrame) -> Dict[str, Any]:
    if TOUCH_LOCK_PATH.exists():
        return json.loads(TOUCH_LOCK_PATH.read_text(encoding="utf-8"))
    row = choose_touch_candidate()
    lock_close_dt = pd.to_datetime(base["close_dt"], utc=True, errors="coerce").max()
    metric_keys = [
        "current_all_net_pnl_cents",
        "current_all_net_roi_on_cost",
        "current_all_accuracy",
        "current_all_coverage",
        "current_train_net_pnl_cents",
        "current_validation_net_pnl_cents",
        "current_holdout_net_pnl_cents",
        "v21_all_net_pnl_cents",
        "v21_all_net_roi_on_cost",
        "v21_all_accuracy",
        "v21_all_coverage",
        "v21_train_net_pnl_cents",
        "v21_validation_net_pnl_cents",
        "v21_holdout_net_pnl_cents",
        "min_oos_net_roi",
        "max_median_ask",
    ]
    policy = policy_from_record(row)
    lock = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "lock_close_dt": lock_close_dt.isoformat() if not pd.isna(lock_close_dt) else None,
        "source_frontier_csv": str(FRONTIER_CSV),
        "policy": {
            "label": policy.label,
            "chooser": policy.chooser,
            "min_score": policy.min_score,
            "ask_min": policy.ask_min,
            "ask_max": policy.ask_max,
            "min_seconds_to_close": policy.min_seconds_to_close,
            "gate": policy.gate,
        },
        "discovery_metrics": {key: clean_json_local(row.get(key)) for key in metric_keys},
    }
    TOUCH_LOCK_PATH.write_text(json.dumps(clean_json_local(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def metric_for_scope(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metric = split_metric(base, enrich_selected(selected), "all")
    metric["coverage_pass"] = (metric["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
    metric["positive_net"] = (metric["net_pnl_cents"] or 0.0) > 0.0
    metric["wilson_minus_break_even"] = (
        (metric["wilson95_lower"] or 0.0) - (metric["fee_aware_break_even_accuracy"] or 1.0)
    )
    return metric


def fmt_num(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.3f}"


def select_for_policy(side_rows: pd.DataFrame, base: pd.DataFrame, policy: HazardPolicy) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    return select_markets(chosen, policy)


def write_report(path: Path, generated: str, lock: Dict[str, Any], all_metric: Dict[str, Any], fresh_metric: Dict[str, Any]) -> None:
    effective_dt = effective_lock_dt(lock)
    lines = [
        "# Profit Touch-Hazard Fresh Validation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only validation; no orders are submitted and no bot files or live processes are touched.",
        "- This is a separate forward lock for the first-passage/touch-hazard profit candidate.",
        "- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.",
        "",
        "## Locked Touch-Hazard Candidate",
        "",
        f"- Policy: `{lock['policy']['label']}`",
        f"- Lock close time: `{lock.get('lock_close_dt')}`",
        f"- Effective entry boundary: `{effective_dt.isoformat() if not pd.isna(effective_dt) else None}`",
        f"- Lock file: `{TOUCH_LOCK_PATH}`",
        "",
        "## Metrics",
        "",
        "| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, metric in [("all current ledger", all_metric), ("fresh after touch lock", fresh_metric)]:
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
        lines.append("- Touch-hazard candidate is now locked; no post-lock resolved markets are available yet.")
    else:
        lines.append(
            f"- Fresh selected {int(fresh_metric['markets'])}/{int(fresh_metric['base_markets'])} markets "
            f"with {fmt_cents(fresh_metric['net_pnl_cents'])} net P&L."
        )
    lines.append("- Keep this lock separate so the new physics prior can be falsified forward without retuning.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    side_rows = add_touch_hazard_scores(load_side_rows())
    base = market_base(side_rows)
    lock = load_or_create_lock(base)
    policy = policy_from_record(lock["policy"])
    selected = enrich_selected(select_for_policy(side_rows, base, policy))
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
        fresh_selected = enrich_selected(select_for_policy(fresh_side_rows, fresh_base, policy))
    fresh_metric = metric_for_scope(fresh_base, fresh_selected)

    md_latest = OUT_DIR / "profit_touch_hazard_fresh_validation_latest.md"
    md_stamp = OUT_DIR / f"profit_touch_hazard_fresh_validation_{generated}.md"
    json_latest = OUT_DIR / "profit_touch_hazard_fresh_validation_latest.json"
    json_stamp = OUT_DIR / f"profit_touch_hazard_fresh_validation_{generated}.json"
    selected_latest = OUT_DIR / "profit_touch_hazard_selected_latest.csv"
    selected.to_csv(selected_latest, index=False)
    write_report(md_latest, generated, lock, all_metric, fresh_metric)
    write_report(md_stamp, generated, lock, all_metric, fresh_metric)
    payload = {
        "generated_utc": generated,
        "lock": lock,
        "all_metric": all_metric,
        "fresh_metric": fresh_metric,
        "selected_csv": str(selected_latest),
    }
    for out_path in [json_latest, json_stamp]:
        out_path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Profit touch-hazard fresh validation complete")
    print(f"fresh_markets={fresh_metric['markets']} fresh_base={fresh_metric['base_markets']}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
