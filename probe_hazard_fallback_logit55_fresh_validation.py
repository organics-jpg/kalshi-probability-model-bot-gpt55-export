"""Fresh validation for hazard-primary / thresholded-logit fallback trial.

This freezes the best diagnostic hazard-fallback row as a forward-only trial.
It takes the first-passage hazard signal when available; if hazard skips a
market, it falls back to the thresholded logit book/RV/hazard blend.

Research-only: no orders are submitted and no bot files or live processes are
modified.
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
from probe_physics_probability_blend_audit import add_blend_scores
from probe_profit_lock_time_boundary import effective_lock_dt
from probe_profit_touch_hazard_fresh_validation import policy_from_record as touch_policy_from_record
from probe_profit_touch_hazard_frontier import HazardPolicy, gate_mask as touch_gate_mask


LOCK_PATH = OUT_DIR / "profit_hazard_fallback_logit55_fresh_lock.json"
REPORT_LATEST = OUT_DIR / "profit_hazard_fallback_logit55_fresh_validation_latest.md"
JSON_LATEST = OUT_DIR / "profit_hazard_fallback_logit55_fresh_validation_latest.json"
SELECTED_LATEST = OUT_DIR / "profit_hazard_fallback_logit55_selected_latest.csv"


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
        raise SystemExit(f"Missing hazard fallback lock: {LOCK_PATH}")
    return json.loads(LOCK_PATH.read_text(encoding="utf-8"))


def first_market_rows(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return rows.copy()
    return (
        rows.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )


def first_causal_rows(primary: pd.DataFrame, fallback: pd.DataFrame) -> pd.DataFrame:
    frames = []
    if not primary.empty:
        p = primary.copy()
        p["selector_priority"] = 0
        frames.append(p)
    if not fallback.empty:
        f = fallback.copy()
        f["selector_priority"] = 1
        frames.append(f)
    if not frames:
        return primary.iloc[0:0].copy()
    rows = pd.concat(frames, ignore_index=True, sort=False)
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    return (
        rows.sort_values(["market", "entry_dt", "selector_priority"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
        .drop(columns=["selector_priority"], errors="ignore")
    )


def primary_selected(rows: pd.DataFrame, policy: HazardPolicy) -> pd.DataFrame:
    chosen = choose_decision_sides(rows, policy.chooser)
    if chosen.empty:
        return chosen.copy()
    selected = chosen[touch_gate_mask(chosen, policy)].copy()
    if selected.empty:
        return selected
    selected = first_market_rows(enrich_selected(selected))
    selected["selector"] = "hazard_primary"
    selected["selector_label"] = policy.label
    return selected


def fallback_selected(rows: pd.DataFrame, fallback: Dict[str, Any]) -> pd.DataFrame:
    chooser = str(fallback["chooser"])
    chosen = choose_decision_sides(rows, chooser)
    if chosen.empty:
        return chosen.copy()
    chosen = enrich_selected(chosen)
    scores = pd.to_numeric(chosen[chooser], errors="coerce")
    chosen["fair_edge_cents"] = 100.0 * scores - pd.to_numeric(chosen["entry_cost_cents"], errors="coerce")
    selected = chosen[
        scores.ge(float(fallback.get("min_score", 0.0)))
        & pd.to_numeric(chosen["ask_cents"], errors="coerce").le(float(fallback.get("ask_max", 95.0)))
        & pd.to_numeric(chosen["seconds_to_close"], errors="coerce").ge(float(fallback.get("min_seconds_to_close", 60.0)))
        & chosen["fair_edge_cents"].ge(float(fallback.get("edge_floor_cents", -100.0)))
    ].copy()
    if fallback.get("max_seconds_to_close") is not None and not selected.empty:
        selected = selected[
            pd.to_numeric(selected["seconds_to_close"], errors="coerce").le(float(fallback["max_seconds_to_close"]))
        ].copy()
    if selected.empty:
        return selected
    selected = first_market_rows(selected)
    selected["selector"] = "fallback_logit_thresh55_edge15"
    selected["selector_label"] = fallback.get("label", "fallback")
    return selected


def select_for_lock(side_rows: pd.DataFrame, base: pd.DataFrame, lock: Dict[str, Any]) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    primary_policy = touch_policy_from_record(lock["primary_policy"])
    primary = primary_selected(rows, primary_policy)
    fallback = fallback_selected(rows, lock["fallback_policy"])
    return first_causal_rows(primary, fallback).sort_values(["entry_dt", "market"]).reset_index(drop=True)


def metric_for_scope(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metric = split_metric(base, selected, "all")
    metric["coverage_pass"] = (metric["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
    metric["positive_net"] = (metric["net_pnl_cents"] or 0.0) > 0.0
    metric["wilson_minus_break_even"] = (
        (metric["wilson95_lower"] or 0.0) - (metric["fee_aware_break_even_accuracy"] or 1.0)
    )
    return metric


def write_report(generated: str, lock: Dict[str, Any], all_metric: Dict[str, Any], fresh_metric: Dict[str, Any]) -> None:
    effective_dt = effective_lock_dt(lock)
    lines = [
        "# Hazard Fallback Logit55 Fresh Validation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only validation; no orders are submitted and no bot files or live processes are touched.",
        "- Takes hazard-mean touch80 when it fires; otherwise falls back to thresholded logit book/RV/hazard.",
        "- The diagnostic row used validation/holdout visibility, so live pre-resolution registry evidence is mandatory before any promotion.",
        "",
        "## Locked Candidate",
        "",
        f"- Primary: `{lock['primary_policy']['label']}`",
        f"- Fallback: `{lock['fallback_policy']['label']}`",
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
    lines.append("- First strict market is determined by the effective boundary, not by the retrospective diagnostic row.")
    for path in [REPORT_LATEST, OUT_DIR / f"profit_hazard_fallback_logit55_fresh_validation_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    side_rows = add_blend_scores(load_side_rows())
    base = market_base(side_rows)
    lock = load_lock()

    selected = select_for_lock(side_rows, base, lock)
    selected.to_csv(SELECTED_LATEST, index=False)
    all_metric = metric_for_scope(base, selected)

    lock_close_dt = effective_lock_dt(lock)
    if pd.isna(lock_close_dt):
        fresh_base = base.iloc[0:0].copy()
        fresh_side_rows = side_rows.iloc[0:0].copy()
    else:
        fresh_base = base[pd.to_datetime(base["close_dt"], utc=True, errors="coerce").gt(lock_close_dt)].copy()
        entry_dt = pd.to_datetime(side_rows["entry_dt"], utc=True, errors="coerce")
        fresh_side_rows = side_rows[
            entry_dt.gt(lock_close_dt) & side_rows["market"].isin(set(fresh_base["market"]))
        ].copy()
    fresh_selected = select_for_lock(fresh_side_rows, fresh_base, lock)
    fresh_metric = metric_for_scope(fresh_base, fresh_selected)

    write_report(generated, lock, all_metric, fresh_metric)
    payload = {
        "generated_utc": generated,
        "lock": lock,
        "all_metric": all_metric,
        "fresh_metric": fresh_metric,
        "selected_csv": str(SELECTED_LATEST),
    }
    for path in [JSON_LATEST, OUT_DIR / f"profit_hazard_fallback_logit55_fresh_validation_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Hazard fallback logit55 fresh validation complete")
    print(f"fresh_markets={fresh_metric['markets']} fresh_base={fresh_metric['base_markets']}")
    print(f"report={REPORT_LATEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
