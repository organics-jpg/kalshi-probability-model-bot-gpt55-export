"""Fresh validation for the hazard-discounted mean touch candidate.

This freezes the refreshed touch-hazard frontier row selected after the
2026-05-04 05:30 UTC settlement. It is research-only and deliberately separate
from the older touch/kinetic locks because those earlier forward trials have
weakened.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
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
from probe_profit_lock_time_boundary import effective_lock_dt
from probe_profit_touch_hazard_fresh_validation import policy_from_record
from probe_profit_touch_hazard_frontier import HazardPolicy, add_touch_hazard_scores, select_markets


LOCK_PATH = OUT_DIR / "profit_hazard_mean_touch80_fresh_lock.json"
REPORT_LATEST = OUT_DIR / "profit_hazard_mean_touch80_fresh_validation_latest.md"
JSON_LATEST = OUT_DIR / "profit_hazard_mean_touch80_fresh_validation_latest.json"
SELECTED_LATEST = OUT_DIR / "profit_hazard_mean_touch80_selected_latest.csv"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt_num(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.3f}"


def load_lock() -> Dict[str, Any]:
    if not LOCK_PATH.exists():
        raise SystemExit(f"Missing hazard-mean touch lock: {LOCK_PATH}")
    return json.loads(LOCK_PATH.read_text(encoding="utf-8"))


def select_for_policy(side_rows: pd.DataFrame, base: pd.DataFrame, policy: HazardPolicy) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    return select_markets(chosen, policy)


def metric_for_scope(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metric = split_metric(base, enrich_selected(selected), "all")
    metric["coverage_pass"] = (metric["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
    metric["positive_net"] = (metric["net_pnl_cents"] or 0.0) > 0.0
    metric["wilson_minus_break_even"] = (
        (metric["wilson95_lower"] or 0.0) - (metric["fee_aware_break_even_accuracy"] or 1.0)
    )
    return metric


def write_report(generated: str, lock: Dict[str, Any], all_metric: Dict[str, Any], fresh_metric: Dict[str, Any]) -> None:
    effective_dt = effective_lock_dt(lock)
    lines = [
        "# Hazard-Mean Touch80 Fresh Validation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only validation; no orders are submitted and no bot files or live processes are touched.",
        "- Freezes the refreshed first-passage/touch-hazard candidate as its own forward trial.",
        "- Promotion still requires strict pre-resolution live sample size and >=75-80% recurring-market coverage.",
        "",
        "## Locked Candidate",
        "",
        f"- Policy: `{lock['policy']['label']}`",
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
        lines.append("- Candidate is locked; no post-boundary resolved markets are available yet.")
    else:
        lines.append(
            f"- Fresh selected {int(fresh_metric['markets'])}/{int(fresh_metric['base_markets'])} markets "
            f"with {fmt_cents(fresh_metric['net_pnl_cents'])} net P&L."
        )
    lines.append("- This lock was created after the 05:30 UTC settlement, so the first strict market is the 06:00 UTC cycle.")
    REPORT_LATEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT_DIR / f"profit_hazard_mean_touch80_fresh_validation_{generated}.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    side_rows = add_touch_hazard_scores(load_side_rows())
    base = market_base(side_rows)
    lock = load_lock()
    policy = policy_from_record(lock["policy"])

    selected = enrich_selected(select_for_policy(side_rows, base, policy))
    selected.to_csv(SELECTED_LATEST, index=False)
    all_metric = metric_for_scope(base, selected)

    lock_close_dt = effective_lock_dt(lock)
    if pd.isna(lock_close_dt):
        fresh_base = base.iloc[0:0].copy()
        fresh_selected = selected.iloc[0:0].copy()
    else:
        fresh_base = base[pd.to_datetime(base["close_dt"], utc=True, errors="coerce") > lock_close_dt].copy()
        entry_dt = pd.to_datetime(side_rows["entry_dt"], utc=True, errors="coerce")
        fresh_side_rows = side_rows[
            entry_dt.gt(lock_close_dt) & side_rows["market"].isin(set(fresh_base["market"]))
        ].copy()
        fresh_selected = enrich_selected(select_for_policy(fresh_side_rows, fresh_base, policy))
    fresh_metric = metric_for_scope(fresh_base, fresh_selected)

    write_report(generated, lock, all_metric, fresh_metric)
    payload = {
        "generated_utc": generated,
        "lock": lock,
        "all_metric": all_metric,
        "fresh_metric": fresh_metric,
        "selected_csv": str(SELECTED_LATEST),
    }
    for path in [JSON_LATEST, OUT_DIR / f"profit_hazard_mean_touch80_fresh_validation_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Hazard-mean touch80 fresh validation complete")
    print(f"fresh_markets={fresh_metric['markets']} fresh_base={fresh_metric['base_markets']}")
    print(f"report={REPORT_LATEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
