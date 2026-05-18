"""Audit profit-lock coverage against observed BTC 15m market denominators.

The promotion target is recurring-market coverage, not only selected-row or
validator coverage. This probe independently rebuilds the post-lock BTC 15m
market universe from live heartbeat rows, then compares it with pre-registered
signals and recomputed candidate selections.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from probe_kinetic_path_confirmation import select_confirmed
from probe_kinetic_path_confirmation_fresh_validation import ensure_lock as ensure_path_lock
from probe_kinetic_path_confirmation_fresh_validation import spec_from_lock as path_spec_from_lock
from probe_market_interval_80coverage import MARKET_COVERAGE_FLOOR, OUT_DIR, clean_json, market_base, pct
from probe_profit_lock_pending_signal_monitor import (
    LOCK_SPECS,
    REGISTRY_PATH as MAIN_REGISTRY_PATH,
    bool_value,
    load_lock,
    raw_side_rows,
    select_signals,
)
from probe_profit_lock_time_boundary import effective_lock_dt
from probe_profit_touch_hazard_fresh_validation import policy_from_record
from probe_profit_touch_hazard_frontier import add_touch_hazard_scores


PATH_REGISTRY_PATH = OUT_DIR / "kinetic_path_confirmation_pending_registry_latest.csv"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt_num(value: Any, digits: int = 3) -> str:
    if value is None:
        return "NA"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(numeric):
        return "NA"
    return f"{numeric:.{digits}f}"


def read_registry(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    rows = pd.read_csv(path)
    if rows.empty:
        return rows
    rows["lock_name"] = rows["lock_name"].astype(str)
    rows["market"] = rows["market"].astype(str)
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    rows["close_dt"] = pd.to_datetime(rows["close_dt"], utc=True, errors="coerce")
    registered_dt = pd.to_datetime(rows["registered_utc"], utc=True, errors="coerce")
    rows = rows[registered_dt.notna() & rows["close_dt"].notna() & registered_dt.lt(rows["close_dt"])].copy()
    if rows.empty:
        return rows
    rows["outcome_available_bool"] = rows["outcome_available"].map(bool_value)
    return rows


def combined_registry() -> pd.DataFrame:
    frames = [read_registry(MAIN_REGISTRY_PATH), read_registry(PATH_REGISTRY_PATH)]
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True, sort=False)


def market_universe(rows: pd.DataFrame, boundary: pd.Timestamp, now: pd.Timestamp) -> pd.DataFrame:
    if rows.empty or pd.isna(boundary):
        return pd.DataFrame(
            columns=[
                "market",
                "first_entry_dt",
                "close_dt",
                "outcome_available",
                "is_unclosed",
                "is_outcome_lag",
            ]
        )
    work = rows.copy()
    work["entry_dt"] = pd.to_datetime(work["entry_dt"], utc=True, errors="coerce")
    work["close_dt"] = pd.to_datetime(work["close_dt"], utc=True, errors="coerce")
    work["outcome_available_bool"] = work["outcome_available"].map(bool_value)
    work = work[
        work["entry_dt"].gt(boundary)
        & work["close_dt"].gt(boundary)
        & pd.to_numeric(work["seconds_to_close"], errors="coerce").gt(0)
    ].copy()
    if work.empty:
        return work.iloc[0:0].copy()

    base = (
        work.sort_values(["entry_dt", "market"])
        .groupby("market", as_index=False, sort=False)
        .agg(
            first_entry_dt=("entry_dt", "min"),
            close_dt=("close_dt", "max"),
            outcome_available=("outcome_available_bool", "max"),
        )
        .sort_values(["close_dt", "market"])
        .reset_index(drop=True)
    )
    base["is_unclosed"] = pd.to_datetime(base["close_dt"], utc=True, errors="coerce").gt(now)
    base["is_outcome_lag"] = ~base["outcome_available"].astype(bool) & ~base["is_unclosed"].astype(bool)
    return base


def coverage(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator


def coverage_pass_value(value: float | None, denominator: int) -> bool | None:
    if denominator <= 0 or value is None:
        return None
    return value >= MARKET_COVERAGE_FLOOR


def lock_registry_rows(registry: pd.DataFrame, name: str, boundary: pd.Timestamp) -> pd.DataFrame:
    if registry.empty:
        return pd.DataFrame()
    rows = registry[registry["lock_name"].eq(name)].copy()
    if rows.empty or pd.isna(boundary):
        return rows
    rows = rows[rows["entry_dt"].gt(boundary)].copy()
    return rows


def summarize_lock(
    name: str,
    boundary: pd.Timestamp,
    universe: pd.DataFrame,
    registry: pd.DataFrame,
    selected: pd.DataFrame,
) -> Tuple[Dict[str, Any], Dict[str, List[str]]]:
    observed_markets = set(universe["market"].astype(str)) if not universe.empty else set()
    resolved_universe = universe[universe["outcome_available"].astype(bool)] if not universe.empty else universe
    resolved_markets = set(resolved_universe["market"].astype(str)) if not resolved_universe.empty else set()

    registry_rows = lock_registry_rows(registry, name, boundary)
    registered_markets = set(registry_rows["market"].astype(str)) if not registry_rows.empty else set()
    registered_resolved_rows = (
        registry_rows[registry_rows["outcome_available_bool"].astype(bool)] if not registry_rows.empty else registry_rows
    )
    registered_resolved_markets = set(registered_resolved_rows["market"].astype(str)) if not registered_resolved_rows.empty else set()

    selected_markets = set(selected["market"].astype(str)) if not selected.empty else set()
    observed_den = max(len(observed_markets), len(registered_markets))
    resolved_den = max(len(resolved_markets), len(registered_resolved_markets))
    reg_observed_cov = coverage(len(registered_markets), observed_den)
    reg_resolved_cov = coverage(len(registered_resolved_markets), resolved_den)
    selected_observed_cov = coverage(len(selected_markets), max(len(observed_markets), len(selected_markets)))
    reg_observed_pass = coverage_pass_value(reg_observed_cov, observed_den)
    reg_resolved_pass = coverage_pass_value(reg_resolved_cov, resolved_den)
    recomputed_pass = coverage_pass_value(selected_observed_cov, max(len(observed_markets), len(selected_markets)))
    if reg_observed_pass is None or reg_resolved_pass is None:
        coverage_state = "waiting"
    elif reg_observed_pass and reg_resolved_pass:
        coverage_state = "pass"
    else:
        coverage_state = "fail"

    missing_observed = sorted(observed_markets - registered_markets)
    missing_resolved = sorted(resolved_markets - registered_resolved_markets)
    registry_only = sorted(registered_markets - observed_markets)
    row = {
        "name": name,
        "effective_boundary": boundary.isoformat() if not pd.isna(boundary) else None,
        "observed_post_lock_markets": len(observed_markets),
        "resolved_post_lock_markets": len(resolved_markets),
        "unclosed_post_lock_markets": int(universe["is_unclosed"].sum()) if not universe.empty else 0,
        "outcome_lag_markets": int(universe["is_outcome_lag"].sum()) if not universe.empty else 0,
        "registered_markets": len(registered_markets),
        "registered_resolved_markets": len(registered_resolved_markets),
        "registered_pending_markets": max(0, len(registered_markets) - len(registered_resolved_markets)),
        "registered_observed_coverage": reg_observed_cov,
        "registered_resolved_coverage": reg_resolved_cov,
        "registered_observed_coverage_pass": reg_observed_pass,
        "registered_resolved_coverage_pass": reg_resolved_pass,
        "recomputed_selected_markets": len(selected_markets),
        "recomputed_observed_coverage": selected_observed_cov,
        "recomputed_observed_coverage_pass": recomputed_pass,
        "coverage_state": coverage_state,
        "missing_observed_markets": len(missing_observed),
        "missing_resolved_markets": len(missing_resolved),
        "registry_only_markets": len(registry_only),
    }
    detail = {
        "missing_observed_sample": missing_observed[:10],
        "missing_resolved_sample": missing_resolved[:10],
        "registry_only_sample": registry_only[:10],
    }
    return row, detail


def path_selected(rows: pd.DataFrame, boundary: pd.Timestamp) -> pd.DataFrame:
    lock = ensure_path_lock()
    policy = policy_from_record(lock["policy"])
    spec = path_spec_from_lock(lock)
    scored = add_touch_hazard_scores(rows)
    base = market_base(scored)
    selected = select_confirmed(scored, base, policy, spec)
    if selected.empty or pd.isna(boundary):
        return selected
    selected["entry_dt"] = pd.to_datetime(selected["entry_dt"], utc=True, errors="coerce")
    selected["close_dt"] = pd.to_datetime(selected["close_dt"], utc=True, errors="coerce")
    return selected[selected["entry_dt"].gt(boundary) & selected["close_dt"].gt(boundary)].copy()


def write_report(generated: str, rows: List[Dict[str, Any]], details: Dict[str, Dict[str, List[str]]]) -> None:
    lines = [
        "# Profit Lock Market-Denominator Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Denominator is observed post-lock BTC 15m market tickers from live heartbeat rows.",
        "- Registered coverage uses pre-resolution signal registries; recomputed coverage is diagnostic only.",
        "",
        "## Denominator Coverage",
        "",
        "| lock | observed/resolved/unclosed/lag | registered/resolved/pending | reg observed cov | reg resolved cov | recomputed cov | missing observed | coverage pass |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['name']} | "
            f"{row['observed_post_lock_markets']}/{row['resolved_post_lock_markets']}/"
            f"{row['unclosed_post_lock_markets']}/{row['outcome_lag_markets']} | "
            f"{row['registered_markets']}/{row['registered_resolved_markets']}/{row['registered_pending_markets']} | "
            f"{pct(row['registered_observed_coverage'])} | {pct(row['registered_resolved_coverage'])} | "
            f"{pct(row['recomputed_observed_coverage'])} | {row['missing_observed_markets']} | {row['coverage_state']} |"
        )

    lines += ["", "## Read", ""]
    failing = [row for row in rows if row["coverage_state"] == "fail"]
    waiting = [row for row in rows if row["coverage_state"] == "waiting"]
    if failing:
        lines.append("- At least one lock is below the 80% registered recurring-market coverage floor.")
    else:
        lines.append("- All tracked locks are above the 80% registered recurring-market coverage floor on observed and resolved denominators.")
    if waiting:
        names = ", ".join(f"`{row['name']}`" for row in waiting)
        lines.append(f"- Waiting for a nonzero observed/resolved denominator for: {names}.")
    for row in rows:
        detail = details.get(row["name"], {})
        if row["missing_observed_markets"]:
            sample = ", ".join(f"`{item}`" for item in detail.get("missing_observed_sample", []))
            lines.append(f"- {row['name']} missing observed sample: {sample}")
        if row["registry_only_markets"]:
            sample = ", ".join(f"`{item}`" for item in detail.get("registry_only_sample", []))
            lines.append(f"- {row['name']} registry-only sample: {sample}")

    md_latest = OUT_DIR / "profit_lock_market_denominator_audit_latest.md"
    md_stamp = OUT_DIR / f"profit_lock_market_denominator_audit_{generated}.md"
    csv_latest = OUT_DIR / "profit_lock_market_denominator_audit_latest.csv"
    csv_stamp = OUT_DIR / f"profit_lock_market_denominator_audit_{generated}.csv"
    json_latest = OUT_DIR / "profit_lock_market_denominator_audit_latest.json"
    json_stamp = OUT_DIR / f"profit_lock_market_denominator_audit_{generated}.json"

    for path in [md_latest, md_stamp]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    pd.DataFrame(rows).to_csv(csv_latest, index=False)
    pd.DataFrame(rows).to_csv(csv_stamp, index=False)
    payload = {
        "generated_utc": generated,
        "market_coverage_floor": MARKET_COVERAGE_FLOOR,
        "rows": rows,
        "details": details,
        "registered_coverage_fail_count": len(failing),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-btc-candles", action="store_true")
    args = parser.parse_args()

    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    now = pd.Timestamp.now(tz="UTC")
    rows = raw_side_rows(fetch_btc_candles=args.fetch_btc_candles)
    registry = combined_registry()

    report_rows: List[Dict[str, Any]] = []
    details: Dict[str, Dict[str, List[str]]] = {}

    for name, path, kind in LOCK_SPECS:
        spec = load_lock(name, path, kind)
        boundary = effective_lock_dt(spec["lock"])
        universe = market_universe(rows, boundary, now)
        selected = select_signals(rows, spec)
        summary, detail = summarize_lock(name, boundary, universe, registry, selected)
        report_rows.append(summary)
        details[name] = detail

    path_lock = ensure_path_lock()
    path_boundary = effective_lock_dt(path_lock)
    path_universe = market_universe(rows, path_boundary, now)
    path_selection = path_selected(rows, path_boundary)
    summary, detail = summarize_lock("kinetic_path_confirm", path_boundary, path_universe, registry, path_selection)
    report_rows.append(summary)
    details["kinetic_path_confirm"] = detail

    write_report(generated, report_rows, details)
    print("Profit lock market-denominator audit complete")
    print(f"locks={len(report_rows)}")
    print(f"coverage_fail={sum(row['coverage_state'] == 'fail' for row in report_rows)}")
    print(f"report={OUT_DIR / 'profit_lock_market_denominator_audit_latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
