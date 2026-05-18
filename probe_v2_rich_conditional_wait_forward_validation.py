"""Forward validation for the rich V2 conditional-wait candidate.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from probe_cross_dataset_profit_frontier import fmt_cents, fmt_roi, split_metric
from probe_market_interval_80coverage import MARKET_COVERAGE_FLOOR, OUT_DIR, clean_json, load_side_rows, market_base, pct
from probe_profit_frontier_v2_fresh_validation import FRONTIER_V2_LOCK_PATH
from probe_profit_lock_time_boundary import effective_lock_dt
from probe_v2_conditional_wait_forward_validation import (
    SCORE_MIN60_LOCK_PATH,
    clean_json_local,
    load_json,
    metric_for_strict_registry,
    metric_row,
    registry_recompute_divergence,
    select_for_validation,
    strict_registry_rows,
)


RICH_CONDITIONAL_WAIT_LOCK_PATH = OUT_DIR / "profit_v2_wait_score_min60_brownian70_early_lock.json"
SCAN_CSV = OUT_DIR / "v2_rich_conditional_wait_scan_latest.csv"
REPORT_MD = OUT_DIR / "profit_v2_wait_score_min60_brownian70_early_validation_latest.md"
REPORT_JSON = OUT_DIR / "profit_v2_wait_score_min60_brownian70_early_validation_latest.json"

LOCK_NAME = "v2_wait_score_min60_brownian70_early"
WAIT_RULE = {
    "candidate": "score_min60",
    "conditions": [
        {"feature": "seconds_to_close", "op": ">=", "threshold": 600.0},
        {"feature": "brownian_p_rv_15m", "op": "<=", "threshold": 0.70},
    ],
    "label": "wait_for_score_min60_if_v2_seconds_to_close>=600_AND_brownian_p_rv_15m<=0.7",
}


def scan_metrics_for_rule() -> Dict[str, Any]:
    if not SCAN_CSV.exists():
        return {}
    rows = pd.read_csv(SCAN_CSV)
    if rows.empty or "label" not in rows.columns:
        return {}
    match = rows[rows["label"].astype(str).eq(WAIT_RULE["label"])]
    if match.empty:
        return {}
    row = match.iloc[0].to_dict()
    keys = [
        "current_all_net_pnl_cents",
        "current_all_net_roi_on_cost",
        "current_all_accuracy",
        "current_all_coverage",
        "current_holdout_net_pnl_cents",
        "current_holdout_accuracy",
        "current_holdout_coverage",
        "v21_all_net_pnl_cents",
        "v21_all_net_roi_on_cost",
        "v21_all_accuracy",
        "v21_all_coverage",
        "v21_holdout_net_pnl_cents",
        "v21_holdout_accuracy",
        "v21_holdout_coverage",
        "current_delta_vs_v2_cents",
        "v21_delta_vs_v2_cents",
        "combined_delta_vs_v2_cents",
        "min_oos_roi",
        "both_coverage_pass",
        "both_oos_positive",
    ]
    return {key: clean_json_local(row.get(key)) for key in keys if key in row}


def ensure_lock(side_rows: pd.DataFrame | None = None) -> Dict[str, Any]:
    if RICH_CONDITIONAL_WAIT_LOCK_PATH.exists():
        return load_json(RICH_CONDITIONAL_WAIT_LOCK_PATH)
    if side_rows is None:
        side_rows = load_side_rows()
    base = market_base(side_rows)
    lock_close_dt = pd.to_datetime(base["close_dt"], utc=True, errors="coerce").max()
    v2_lock = load_json(FRONTIER_V2_LOCK_PATH)
    score_lock = load_json(SCORE_MIN60_LOCK_PATH)
    lock = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "lock_close_dt": lock_close_dt.isoformat() if not pd.isna(lock_close_dt) else None,
        "source_scan_csv": str(SCAN_CSV),
        "source_v2_lock": str(FRONTIER_V2_LOCK_PATH),
        "source_candidate_lock": str(SCORE_MIN60_LOCK_PATH),
        "wait_rule": WAIT_RULE,
        "v2_policy": v2_lock["policy"],
        "candidate_policy": score_lock["policy"],
        "combined_label": (
            "take frontier_v2 unless first v2 seconds_to_close>=600 and "
            "brownian_p_rv_15m<=0.70, then wait for score_min60"
        ),
        "discovery_metrics": scan_metrics_for_rule(),
        "research_note": (
            "Forward-registered rich conditional wait candidate from the V2 rich conditional scan. "
            "Diagnostic only: it improves the prior conditional wait in broad current/v21 ledgers, "
            "but promotion requires strict pre-resolution live evidence and >=80% recurring-market coverage."
        ),
    }
    RICH_CONDITIONAL_WAIT_LOCK_PATH.write_text(
        json.dumps(clean_json_local(lock), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return lock


def metric_for_scope(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metric = split_metric(base, selected, "all")
    metric["coverage_pass"] = (metric["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
    metric["wilson_minus_break_even"] = (
        (metric["wilson95_lower"] or 0.0) - (metric["fee_aware_break_even_accuracy"] or 1.0)
    )
    metric["positive_net"] = (metric["net_pnl_cents"] or 0.0) > 0.0
    return metric


def write_report(
    path: Path,
    generated: str,
    lock: Dict[str, Any],
    all_metric: Dict[str, Any],
    fresh_metric: Dict[str, Any],
    strict_metric: Dict[str, Any],
    divergence: Dict[str, Any],
) -> None:
    effective_dt = effective_lock_dt(lock)
    lines = [
        "# V2 Rich Conditional Wait Forward Validation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only validation; no orders are submitted and no bot files or live processes are touched.",
        "- Locked rule: take V2 unless the first V2 signal is early and Brownian RV15 confidence is <=70%, then wait for score_min60.",
        "- This is forward-test evidence only; the discovery scan is not promotion evidence.",
        "",
        "## Lock",
        "",
        f"- Label: `{lock['combined_label']}`",
        f"- Effective entry boundary: `{effective_dt.isoformat() if not pd.isna(effective_dt) else None}`",
        f"- Lock file: `{RICH_CONDITIONAL_WAIT_LOCK_PATH}`",
        "",
        "## Metrics",
        "",
        "| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, metric in [
        ("all current ledger", all_metric),
        ("recomputed fresh after lock", fresh_metric),
        ("strict registered fresh", strict_metric),
    ]:
        lines.append(metric_row(name, metric))
    lines += [
        "",
        "## Recompute Drift Check",
        "",
        f"- Compared strict and recomputed rows: {divergence['compared']}.",
        f"- Mismatched rows: {divergence['mismatches']}; missing recomputed rows: {divergence['missing_recompute']}.",
    ]
    for example in divergence["examples"]:
        lines.append(f"- `{example['market']}` strict `{example['strict']}` vs recomputed `{example['recomputed']}`.")
    lines += ["", "## Read", ""]
    if strict_metric["base_markets"] == 0:
        lines.append("- Rich conditional wait lock is waiting for post-boundary resolved markets.")
    elif strict_metric["positive_net"] and strict_metric["coverage_pass"]:
        lines.append("- Strict registered fresh sample is positive and coverage-valid so far, but sample size is still too small for promotion.")
    else:
        lines.append("- Strict registered fresh sample is not promotion-quality proof.")
    if divergence["mismatches"] or divergence["missing_recompute"]:
        lines.append("- Recomputed fresh rows diverge from pre-registered rows; strict registered rows are the promotion authority.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    side_rows = load_side_rows()
    base = market_base(side_rows)
    lock = ensure_lock(side_rows)
    selected = select_for_validation(side_rows, base, lock)
    all_metric = metric_for_scope(base, selected)

    boundary = effective_lock_dt(lock)
    fresh_base = base[pd.to_datetime(base["close_dt"], utc=True, errors="coerce").gt(boundary)].copy()
    if fresh_base.empty or pd.isna(boundary):
        fresh_selected = selected.iloc[0:0].copy()
    else:
        fresh_side_rows = side_rows[
            pd.to_datetime(side_rows["entry_dt"], utc=True, errors="coerce").gt(boundary)
            & side_rows["market"].isin(set(fresh_base["market"]))
        ].copy()
        fresh_selected = select_for_validation(fresh_side_rows, fresh_base, lock)
    fresh_metric = metric_for_scope(fresh_base, fresh_selected)
    strict_rows = strict_registry_rows(LOCK_NAME, fresh_base, boundary)
    strict_metric = metric_for_strict_registry(fresh_base, strict_rows)
    divergence = registry_recompute_divergence(fresh_selected, strict_rows)

    md_stamp = OUT_DIR / f"profit_v2_wait_score_min60_brownian70_early_validation_{generated}.md"
    json_stamp = OUT_DIR / f"profit_v2_wait_score_min60_brownian70_early_validation_{generated}.json"
    for path in [REPORT_MD, md_stamp]:
        write_report(path, generated, lock, all_metric, fresh_metric, strict_metric, divergence)
    payload = {
        "generated_utc": generated,
        "lock": lock,
        "all_metric": all_metric,
        "fresh_metric": fresh_metric,
        "strict_registered_metric": strict_metric,
        "registry_recompute_divergence": divergence,
    }
    for path in [REPORT_JSON, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("V2 rich conditional wait forward validation complete")
    print(f"fresh_markets={fresh_metric['markets']} fresh_base={fresh_metric['base_markets']}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
