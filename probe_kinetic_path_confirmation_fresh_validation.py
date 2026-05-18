"""Forward lock validator for the kinetic path-confirmation hypothesis.

The confirmation rule was discovered after the 03:45 UTC path-flip loss, so it
must not be merged into the existing kinetic evidence. This validator freezes
one confirmation rule and evaluates only post-lock markets as fresh evidence.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_profit_frontier import fmt_cents, fmt_roi
from probe_kinetic_path_confirmation import ConfirmSpec, metric, select_confirmed
from probe_market_interval_80coverage import OUT_DIR, clean_json, load_side_rows, market_base, pct
from probe_profit_kinetic_touch_fresh_validation import KINETIC_TOUCH_LOCK_PATH
from probe_profit_lock_time_boundary import effective_lock_dt
from probe_profit_touch_hazard_fresh_validation import policy_from_record
from probe_profit_touch_hazard_frontier import add_touch_hazard_scores


PATH_CONFIRM_LOCK_PATH = OUT_DIR / "profit_kinetic_path_confirm_fresh_lock.json"
REPORT_LATEST = OUT_DIR / "profit_kinetic_path_confirm_fresh_validation_latest.md"
JSON_LATEST = OUT_DIR / "profit_kinetic_path_confirm_fresh_validation_latest.json"


FROZEN_CONFIRM_SPEC = ConfirmSpec(delay_sec=60.0, min_confirm_score=0.60)


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def ensure_lock() -> Dict[str, Any]:
    if PATH_CONFIRM_LOCK_PATH.exists():
        return json.loads(PATH_CONFIRM_LOCK_PATH.read_text(encoding="utf-8"))
    kinetic_lock = json.loads(KINETIC_TOUCH_LOCK_PATH.read_text(encoding="utf-8"))
    now = pd.Timestamp.now(tz="UTC")
    lock = {
        "created_utc": now.isoformat(),
        "lock_close_dt": now.floor("15min").isoformat(),
        "source_lock": str(KINETIC_TOUCH_LOCK_PATH),
        "source_scan": str(OUT_DIR / "kinetic_path_confirmation_latest.csv"),
        "policy": kinetic_lock["policy"],
        "confirmation": {
            "delay_sec": FROZEN_CONFIRM_SPEC.delay_sec,
            "max_ask_worse": FROZEN_CONFIRM_SPEC.max_ask_worse,
            "min_confirm_score": FROZEN_CONFIRM_SPEC.min_confirm_score,
            "min_confirm_book": FROZEN_CONFIRM_SPEC.min_confirm_book,
            "label": FROZEN_CONFIRM_SPEC.label,
        },
        "discovery_read": {
            "current_delta_vs_unconfirmed_cents": 527.0,
            "v21_delta_vs_unconfirmed_cents": -66.0,
            "reason": "Path-flip diagnostic; positive on both datasets but not v21-dominant, so forward-lock separately.",
        },
    }
    PATH_CONFIRM_LOCK_PATH.write_text(json.dumps(clean_json_local(lock), indent=2, sort_keys=True), encoding="utf-8")
    return lock


def spec_from_lock(lock: Dict[str, Any]) -> ConfirmSpec:
    row = lock["confirmation"]
    return ConfirmSpec(
        delay_sec=float(row["delay_sec"]),
        max_ask_worse=row.get("max_ask_worse"),
        min_confirm_score=row.get("min_confirm_score"),
        min_confirm_book=row.get("min_confirm_book"),
    )


def write_report(generated: str, lock: Dict[str, Any], all_metric: Dict[str, Any], fresh_metric: Dict[str, Any]) -> None:
    lines: List[str] = [
        "# Profit Kinetic Path-Confirmation Fresh Validation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only validation; no orders are submitted and no bot files or live processes are touched.",
        "- This is a separate forward lock for a delayed same-side confirmation challenger.",
        "- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.",
        "",
        "## Locked Path-Confirmation Candidate",
        "",
        f"- Policy: `{lock['policy']['label']}`",
        f"- Confirmation: `{lock['confirmation']['label']}`",
        f"- Lock close time: `{lock.get('lock_close_dt')}`",
        f"- Effective entry boundary: `{effective_lock_dt(lock)}`",
        f"- Lock file: `{PATH_CONFIRM_LOCK_PATH}`",
        "",
        "## Metrics",
        "",
        "| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, row in [("all current ledger", all_metric), ("fresh after path-confirm lock", fresh_metric)]:
        wilson_edge = (row["wilson95_lower"] or 0.0) - (row["fee_aware_break_even_accuracy"] or 1.0)
        lines.append(
            f"| {name} | {int(row['markets'])}/{int(row['base_markets'])} | "
            f"{int(row['wins'])}/{int(row['losses'])} | {pct(row['accuracy'])} | "
            f"{pct(row['fee_aware_break_even_accuracy'])} | {pct(row['wilson95_lower'])} | "
            f"{wilson_edge:.3f} | {pct(row['coverage'])} | {fmt_cents(row['net_pnl_cents'])} | "
            f"{fmt_roi(row['net_roi_on_cost'])} | {fmt_cents(row['median_ask'])} |"
        )
    lines += [
        "",
        "## Read",
        "",
        f"- Fresh selected {int(fresh_metric['markets'])}/{int(fresh_metric['base_markets'])} markets with {fmt_cents(fresh_metric['net_pnl_cents'])} net P&L.",
        "- Keep this separate from kinetic-touch because the confirmation rule was discovered after the 03:45 UTC path-flip loss.",
    ]
    REPORT_LATEST.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    lock = ensure_lock()
    policy = policy_from_record(lock["policy"])
    spec = spec_from_lock(lock)

    side_rows = add_touch_hazard_scores(load_side_rows())
    base = market_base(side_rows)
    selected = select_confirmed(side_rows, base, policy, spec)
    all_metric = metric(base, selected, "all")

    boundary = effective_lock_dt(lock)
    if pd.isna(boundary):
        fresh_base = base.iloc[0:0].copy()
    else:
        fresh_base = base[pd.to_datetime(base["close_dt"], utc=True, errors="coerce").gt(boundary)].copy()
    fresh_selected = selected[selected["market"].isin(set(fresh_base["market"]))].copy()
    fresh_metric = metric(fresh_base, fresh_selected, "all")

    JSON_LATEST.write_text(
        json.dumps(
            {
                "generated_utc": generated,
                "lock": clean_json_local(lock),
                "all_metric": clean_json_local(all_metric),
                "fresh_metric": clean_json_local(fresh_metric),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    write_report(generated, lock, all_metric, fresh_metric)
    print("Profit kinetic path-confirmation fresh validation complete")
    print(f"fresh_markets={int(fresh_metric['markets'])} fresh_base={int(fresh_metric['base_markets'])}")
    print(f"report={REPORT_LATEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
