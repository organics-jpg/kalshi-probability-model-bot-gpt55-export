"""Forward validation for a locked V2 conditional-wait candidate.

The conditional rule is intentionally simple and causal:

- take the existing Brownian V2 policy unless its first eligible signal appears
  very early in the market;
- if that early flag is present, wait for the first later book/Brownian
  consensus signal from the score_min60 policy.

This is research-only forward-test scaffolding. It does not submit orders and it
does not modify the live bot.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, split_metric
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    gate_mask,
    load_side_rows,
    market_base,
    pct,
)
from probe_profit_frontier_fresh_validation import policy_from_record
from probe_profit_frontier_v2_fresh_validation import FRONTIER_V2_LOCK_PATH
from probe_profit_lock_time_boundary import effective_lock_dt


CONDITIONAL_WAIT_LOCK_PATH = OUT_DIR / "profit_v2_wait_score_min60_early_lock.json"
SCORE_MIN60_LOCK_PATH = OUT_DIR / "profit_frontier_score_min60_lock.json"
SCAN_CSV = OUT_DIR / "v2_conditional_wait_scan_latest.csv"
REPORT_MD = OUT_DIR / "profit_v2_wait_score_min60_early_validation_latest.md"
REPORT_JSON = OUT_DIR / "profit_v2_wait_score_min60_early_validation_latest.json"
STRICT_REGISTRY = OUT_DIR / "profit_lock_pending_signal_registry_latest.csv"

LOCK_NAME = "v2_wait_score_min60_early"
WAIT_RULE = {
    "candidate": "score_min60",
    "feature": "seconds_to_close",
    "op": ">=",
    "threshold": 600.0,
    "label": "wait_for_score_min60_if_v2_seconds_to_close>=600",
}


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"true", "1", "yes"}


def fmt_num(value: Any) -> str:
    if value is None or pd.isna(value):
        return "NA"
    return f"{float(value):.3f}"


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
    if CONDITIONAL_WAIT_LOCK_PATH.exists():
        return load_json(CONDITIONAL_WAIT_LOCK_PATH)
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
        "combined_label": "take frontier_v2 unless first v2 seconds_to_close>=600, then wait for score_min60",
        "discovery_metrics": scan_metrics_for_rule(),
        "research_note": (
            "Forward-registered conditional wait candidate from the V2 conditional scan. "
            "Diagnostic only: the scan improved the current ledger but gave back v21 edge, "
            "so promotion requires strict pre-resolution live evidence and >=80% recurring-market coverage."
        ),
    }
    CONDITIONAL_WAIT_LOCK_PATH.write_text(
        json.dumps(clean_json_local(lock), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return lock


def policy_eligible_rows(rows: pd.DataFrame, policy: Policy) -> pd.DataFrame:
    chosen = choose_decision_sides(rows, policy.chooser)
    if chosen.empty:
        return chosen
    return chosen[gate_mask(chosen, policy)].copy()


def condition_matches(row: pd.Series, condition: Dict[str, Any]) -> bool:
    value = pd.to_numeric(pd.Series([row.get(condition["feature"])]), errors="coerce").iloc[0]
    if pd.isna(value):
        return False
    threshold = float(condition["threshold"])
    if condition["op"] == ">=":
        return bool(value >= threshold)
    if condition["op"] == "<=":
        return bool(value <= threshold)
    raise ValueError(f"unknown wait rule op: {condition['op']}")


def wait_rule_matches(row: pd.Series, rule: Dict[str, Any]) -> bool:
    conditions = rule.get("conditions")
    if conditions:
        return all(condition_matches(row, condition) for condition in conditions)
    return condition_matches(row, rule)


def select_conditional_wait_rows(rows: pd.DataFrame, lock: Dict[str, Any]) -> pd.DataFrame:
    if rows.empty:
        return rows.iloc[0:0].copy()
    v2_policy = policy_from_record(lock["v2_policy"])
    candidate_policy = policy_from_record(lock["candidate_policy"])
    rule = lock["wait_rule"]

    work = rows.copy()
    work["entry_dt"] = pd.to_datetime(work["entry_dt"], utc=True, errors="coerce")
    v2_rows = policy_eligible_rows(work, v2_policy)
    if v2_rows.empty:
        return v2_rows
    v2_first = (
        v2_rows.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    candidate_rows = policy_eligible_rows(work, candidate_policy)
    if not candidate_rows.empty:
        candidate_rows["entry_dt"] = pd.to_datetime(candidate_rows["entry_dt"], utc=True, errors="coerce")
        candidate_rows = candidate_rows.sort_values(["market", "entry_dt"]).reset_index(drop=True)
    candidate_by_market = {
        str(market): part.copy()
        for market, part in candidate_rows.groupby("market", sort=False)
    } if not candidate_rows.empty else {}

    selected: List[pd.Series] = []
    for _, v2_row in v2_first.iterrows():
        market = str(v2_row["market"])
        trigger_dt = pd.to_datetime(v2_row["entry_dt"], utc=True, errors="coerce")
        if wait_rule_matches(v2_row, rule):
            candidates = candidate_by_market.get(market)
            if candidates is None or pd.isna(trigger_dt):
                continue
            later = candidates[pd.to_datetime(candidates["entry_dt"], utc=True, errors="coerce").ge(trigger_dt)]
            if later.empty:
                continue
            row = later.iloc[0].copy()
            row["conditional_source"] = "score_min60_after_early_v2"
            row["conditional_trigger_dt"] = trigger_dt.isoformat()
            row["chooser"] = candidate_policy.chooser
            row["score_value"] = row.get(candidate_policy.chooser, np.nan)
            selected.append(row)
        else:
            row = v2_row.copy()
            row["conditional_source"] = "frontier_v2_immediate"
            row["conditional_trigger_dt"] = trigger_dt.isoformat() if not pd.isna(trigger_dt) else ""
            row["chooser"] = v2_policy.chooser
            row["score_value"] = row.get(v2_policy.chooser, np.nan)
            selected.append(row)

    if not selected:
        return v2_first.iloc[0:0].copy()
    out = pd.DataFrame(selected).drop_duplicates(subset=["market"], keep="first")
    out = out.sort_values(["entry_dt", "market"]).reset_index(drop=True)
    out["overlay"] = rule["label"]
    return out


def select_for_validation(side_rows: pd.DataFrame, base: pd.DataFrame, lock: Dict[str, Any]) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    return enrich_selected(select_conditional_wait_rows(rows, lock))


def metric_for_scope(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metric = split_metric(base, selected, "all")
    metric["coverage_pass"] = (metric["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
    metric["wilson_minus_break_even"] = (
        (metric["wilson95_lower"] or 0.0) - (metric["fee_aware_break_even_accuracy"] or 1.0)
    )
    metric["positive_net"] = (metric["net_pnl_cents"] or 0.0) > 0.0
    return metric


def strict_registry_rows(lock_name: str, fresh_base: pd.DataFrame, boundary: pd.Timestamp) -> pd.DataFrame:
    if not STRICT_REGISTRY.exists() or pd.isna(boundary):
        return pd.DataFrame()
    rows = pd.read_csv(STRICT_REGISTRY)
    if rows.empty:
        return rows
    rows = rows[rows["lock_name"].astype(str).eq(lock_name)].copy()
    if rows.empty:
        return rows
    rows["entry_dt"] = pd.to_datetime(rows.get("entry_dt"), utc=True, errors="coerce")
    rows["registered_utc"] = pd.to_datetime(rows.get("registered_utc"), utc=True, errors="coerce")
    rows["close_dt"] = pd.to_datetime(rows.get("close_dt"), utc=True, errors="coerce")
    rows = rows[
        rows["entry_dt"].gt(boundary)
        & rows["registered_utc"].notna()
        & rows["close_dt"].notna()
        & rows["registered_utc"].lt(rows["close_dt"])
    ].copy()
    if rows.empty:
        return rows
    for col in ["ask_cents", "entry_fee_cents", "net_pnl_cents"]:
        rows[col] = pd.to_numeric(rows.get(col), errors="coerce")
    rows["outcome_available_bool"] = rows["outcome_available"].map(bool_value)
    rows["win_bool"] = rows["win"].map(bool_value)
    return rows


def metric_for_strict_registry(fresh_base: pd.DataFrame, rows: pd.DataFrame) -> Dict[str, Any]:
    resolved = rows[rows["outcome_available_bool"]] if not rows.empty else rows
    n = int(len(resolved))
    wins = int(resolved["win_bool"].sum()) if n else 0
    losses = n - wins
    entry_cost = float((resolved["ask_cents"] + resolved["entry_fee_cents"].fillna(0.0)).sum()) if n else None
    net = float(resolved["net_pnl_cents"].sum()) if n else 0.0
    break_even = (entry_cost / n / 100.0) if n and entry_cost is not None else None
    wilson = wilson_lower(wins, n) if n else None
    registered_markets = set(rows["market"].astype(str)) if not rows.empty else set()
    base_markets = set(fresh_base["market"].astype(str)) if not fresh_base.empty else set()
    base_count = max(len(base_markets), len(registered_markets))
    coverage = (len(registered_markets) / base_count) if base_count else None
    return {
        "markets": n,
        "registered_markets": int(len(registered_markets)),
        "base_markets": int(base_count),
        "pending": int(len(rows) - n),
        "wins": wins,
        "losses": losses,
        "accuracy": (wins / n) if n else None,
        "fee_aware_break_even_accuracy": break_even,
        "wilson95_lower": wilson,
        "wilson_minus_break_even": (wilson - break_even) if wilson is not None and break_even is not None else None,
        "coverage": coverage,
        "coverage_pass": (coverage or 0.0) >= MARKET_COVERAGE_FLOOR,
        "net_pnl_cents": net,
        "net_roi_on_cost": (net / entry_cost) if entry_cost else None,
        "median_ask": float(resolved["ask_cents"].median()) if n else None,
        "positive_net": net > 0.0,
    }


def registry_recompute_divergence(fresh_selected: pd.DataFrame, registry_rows: pd.DataFrame) -> Dict[str, Any]:
    if registry_rows.empty:
        return {"compared": 0, "mismatches": 0, "missing_recompute": 0, "examples": []}
    if fresh_selected.empty:
        return {
            "compared": 0,
            "mismatches": 0,
            "missing_recompute": int(len(registry_rows)),
            "examples": [],
        }
    selected = fresh_selected.copy()
    selected["entry_dt"] = pd.to_datetime(selected["entry_dt"], utc=True, errors="coerce")
    selected_by_market = {str(row["market"]): row for _, row in selected.iterrows()}
    examples: list[Dict[str, Any]] = []
    compared = 0
    mismatches = 0
    missing = 0
    for _, reg in registry_rows.iterrows():
        market = str(reg["market"])
        sel = selected_by_market.get(market)
        if sel is None:
            missing += 1
            continue
        compared += 1
        reg_dt = pd.to_datetime(reg.get("entry_dt"), utc=True, errors="coerce")
        sel_dt = pd.to_datetime(sel.get("entry_dt"), utc=True, errors="coerce")
        same_dt = (not pd.isna(reg_dt)) and (not pd.isna(sel_dt)) and abs((reg_dt - sel_dt).total_seconds()) < 0.001
        same_side = str(reg.get("side")) == str(sel.get("side"))
        reg_ask = pd.to_numeric(pd.Series([reg.get("ask_cents")]), errors="coerce").iloc[0]
        sel_ask = pd.to_numeric(pd.Series([sel.get("ask_cents")]), errors="coerce").iloc[0]
        same_ask = (pd.isna(reg_ask) and pd.isna(sel_ask)) or (not pd.isna(reg_ask) and not pd.isna(sel_ask) and abs(float(reg_ask) - float(sel_ask)) < 0.001)
        if not (same_dt and same_side and same_ask):
            mismatches += 1
            if len(examples) < 5:
                examples.append(
                    {
                        "market": market,
                        "strict": f"{reg_dt.isoformat() if not pd.isna(reg_dt) else ''} {reg.get('side')} {reg.get('ask_cents')}c",
                        "recomputed": f"{sel_dt.isoformat() if not pd.isna(sel_dt) else ''} {sel.get('side')} {sel.get('ask_cents')}c",
                    }
                )
    return {"compared": compared, "mismatches": mismatches, "missing_recompute": missing, "examples": examples}


def metric_row(label: str, metric: Dict[str, Any]) -> str:
    return (
        f"| {label} | {int(metric['markets'])}/{int(metric['base_markets'])} | "
        f"{int(metric['wins'])}/{int(metric['losses'])} | {pct(metric['accuracy'])} | "
        f"{pct(metric['fee_aware_break_even_accuracy'])} | {pct(metric['wilson95_lower'])} | "
        f"{fmt_num(metric['wilson_minus_break_even'])} | {pct(metric['coverage'])} | "
        f"{fmt_cents(metric['net_pnl_cents'])} | {fmt_roi(metric['net_roi_on_cost'])} | "
        f"{fmt_cents(metric['median_ask'])} |"
    )


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
        "# V2 Conditional Wait Forward Validation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only validation; no orders are submitted and no bot files or live processes are touched.",
        "- Locked rule: take V2 unless the first V2 signal is at least 600 seconds before close, then wait for score_min60.",
        "- This is forward-test evidence only; the discovery scan is not promotion evidence.",
        "",
        "## Lock",
        "",
        f"- Label: `{lock['combined_label']}`",
        f"- Effective entry boundary: `{effective_dt.isoformat() if not pd.isna(effective_dt) else None}`",
        f"- Lock file: `{CONDITIONAL_WAIT_LOCK_PATH}`",
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
        lines.append("- Conditional wait lock is waiting for post-boundary resolved markets.")
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

    md_stamp = OUT_DIR / f"profit_v2_wait_score_min60_early_validation_{generated}.md"
    json_stamp = OUT_DIR / f"profit_v2_wait_score_min60_early_validation_{generated}.json"
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
    print("V2 conditional wait forward validation complete")
    print(f"fresh_markets={fresh_metric['markets']} fresh_base={fresh_metric['base_markets']}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
