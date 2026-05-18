"""Fresh validation for a guarded kinetic-touch challenger.

This freezes the best coverage-preserving blocker overlay discovered after the
first kinetic-touch forward loss. The guard starts only after the current
resolved ledger, so earlier diagnostic wins do not count as fresh evidence.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import pandas as pd

from probe_cross_dataset_profit_frontier import fmt_cents, fmt_roi, split_metric
from probe_kinetic_touch_blocker_overlays import Overlay, overlay_mask, select_with_overlay
from probe_market_interval_80coverage import MARKET_COVERAGE_FLOOR, OUT_DIR, clean_json, load_side_rows, market_base, pct
from probe_profit_kinetic_touch_fresh_validation import KINETIC_TOUCH_LOCK_PATH
from probe_profit_touch_hazard_fresh_validation import policy_from_record
from probe_profit_touch_hazard_frontier import add_touch_hazard_scores
from probe_profit_lock_time_boundary import effective_lock_dt


OVERLAY_CSV = OUT_DIR / "kinetic_touch_blocker_overlays_latest.csv"
KINETIC_GUARD_LOCK_PATH = OUT_DIR / "profit_kinetic_guard_fresh_lock.json"


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


def choose_overlay() -> Dict[str, Any]:
    if not OVERLAY_CSV.exists():
        raise SystemExit(f"Missing kinetic overlay CSV: {OVERLAY_CSV}")
    rows = pd.read_csv(OVERLAY_CSV)
    for col in ["both_coverage_pass", "both_positive_all_splits"]:
        rows[col] = bool_col(rows[col])
    eligible = rows[rows["both_coverage_pass"] & rows["both_positive_all_splits"]].copy()
    if eligible.empty:
        raise SystemExit("No all-split-positive coverage-preserving kinetic overlay found")
    return eligible.iloc[0].to_dict()


def overlay_from_lock(lock: Dict[str, Any]) -> Overlay:
    return Overlay(str(lock["overlay"]["label"]), tuple(str(lock["overlay"]["clauses"]).split(" AND ")))


def load_or_create_lock(base: pd.DataFrame) -> Dict[str, Any]:
    if KINETIC_GUARD_LOCK_PATH.exists():
        return json.loads(KINETIC_GUARD_LOCK_PATH.read_text(encoding="utf-8"))
    if not KINETIC_TOUCH_LOCK_PATH.exists():
        raise SystemExit(f"Missing kinetic touch lock: {KINETIC_TOUCH_LOCK_PATH}")
    base_lock = json.loads(KINETIC_TOUCH_LOCK_PATH.read_text(encoding="utf-8"))
    row = choose_overlay()
    lock_close_dt = pd.to_datetime(base["close_dt"], utc=True, errors="coerce").max()
    metric_keys = [
        "current_all_net_pnl_cents",
        "current_all_net_roi_on_cost",
        "current_all_accuracy",
        "current_all_coverage",
        "v21_all_net_pnl_cents",
        "v21_all_net_roi_on_cost",
        "v21_all_accuracy",
        "v21_all_coverage",
        "fresh_net_pnl_cents",
        "fresh_coverage",
        "min_oos_roi",
    ]
    lock = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "lock_close_dt": lock_close_dt.isoformat() if not pd.isna(lock_close_dt) else None,
        "base_kinetic_lock": str(KINETIC_TOUCH_LOCK_PATH),
        "source_overlay_csv": str(OVERLAY_CSV),
        "policy": base_lock["policy"],
        "overlay": {
            "label": str(row["overlay"]),
            "clauses": str(row["clauses"]),
        },
        "discovery_metrics": {key: clean_json_local(row.get(key)) for key in metric_keys},
    }
    KINETIC_GUARD_LOCK_PATH.write_text(
        json.dumps(clean_json_local(lock), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return lock


def metric_for_scope(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metric = split_metric(base, selected, "all")
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


def write_report(path, generated: str, lock: Dict[str, Any], all_metric: Dict[str, Any], fresh_metric: Dict[str, Any]) -> None:
    effective_dt = effective_lock_dt(lock)
    lines = [
        "# Profit Kinetic-Guard Fresh Validation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only validation; no orders are submitted and no bot files or live processes are touched.",
        "- This is a separate forward lock for a guarded kinetic-touch challenger.",
        "- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.",
        "",
        "## Locked Kinetic-Guard Candidate",
        "",
        f"- Policy: `{lock['policy']['label']}`",
        f"- Overlay: `{lock['overlay']['label']}`",
        f"- Lock close time: `{lock.get('lock_close_dt')}`",
        f"- Effective entry boundary: `{effective_dt.isoformat() if not pd.isna(effective_dt) else None}`",
        f"- Lock file: `{KINETIC_GUARD_LOCK_PATH}`",
        "",
        "## Metrics",
        "",
        "| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, metric in [("all current ledger", all_metric), ("fresh after guard lock", fresh_metric)]:
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
        lines.append("- Kinetic guard is now locked; no post-lock resolved markets are available yet.")
    else:
        lines.append(
            f"- Fresh selected {int(fresh_metric['markets'])}/{int(fresh_metric['base_markets'])} markets "
            f"with {fmt_cents(fresh_metric['net_pnl_cents'])} net P&L."
        )
    lines.append("- Keep this separate from kinetic-touch because the guard was selected after seeing the first kinetic loss.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    side_rows = add_touch_hazard_scores(load_side_rows())
    base = market_base(side_rows)
    lock = load_or_create_lock(base)
    policy = policy_from_record(lock["policy"])
    overlay = overlay_from_lock(lock)
    selected = select_with_overlay(side_rows, base, policy, overlay)
    all_metric = metric_for_scope(base, selected)

    lock_close_dt = effective_lock_dt(lock)
    fresh_base = base[pd.to_datetime(base["close_dt"], utc=True, errors="coerce") > lock_close_dt].copy()
    fresh_side = side_rows[
        pd.to_datetime(side_rows["entry_dt"], utc=True, errors="coerce").gt(lock_close_dt)
        & side_rows["market"].isin(set(fresh_base["market"]))
    ].copy()
    fresh_selected = select_with_overlay(fresh_side, fresh_base, policy, overlay) if not fresh_base.empty else selected.iloc[0:0].copy()
    fresh_metric = metric_for_scope(fresh_base, fresh_selected)

    md_latest = OUT_DIR / "profit_kinetic_guard_fresh_validation_latest.md"
    md_stamp = OUT_DIR / f"profit_kinetic_guard_fresh_validation_{generated}.md"
    json_latest = OUT_DIR / "profit_kinetic_guard_fresh_validation_latest.json"
    json_stamp = OUT_DIR / f"profit_kinetic_guard_fresh_validation_{generated}.json"
    selected_latest = OUT_DIR / "profit_kinetic_guard_selected_latest.csv"
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
    print("Profit kinetic-guard fresh validation complete")
    print(f"fresh_markets={fresh_metric['markets']} fresh_base={fresh_metric['base_markets']}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
