"""Strict-forward shadow monitor for v69: v55 entry, v66 exit.

Research-only. Registers entries from the v55 FV surface, but evaluates exit
probability with the v66 balanced NO-side book-gap FV surface.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import probe_v55_book_anchor_recross_shadow_monitor as v55_monitor
import probe_v66_no_bookgap_balanced_shadow_monitor as v66_monitor
from probe_market_interval_80coverage import clean_json


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"
v42 = v66_monitor.v42
ENTRY_OPPORTUNITY_TABLE = v55_monitor.opportunity_table
EXIT_OPPORTUNITY_TABLE = v66_monitor.opportunity_table
ORIGINAL_LOAD_OR_CREATE_LOCK = v42.load_or_create_lock

v42.POLICY = "v69_v55_entry_v66_exit_hold15_prob52_edge0_p65_stc0_600"
v42.REPORT_PREFIX = "v69_v55_entry_v66_exit_shadow"
v42.shadow.POLICY = v42.POLICY
v42.shadow.ENTRY_EDGE_FLOOR_CENTS = 0.0
v42.shadow.ENTRY_P_SIDE_FLOOR = 0.65
v42.shadow.ENTRY_ASK_FLOOR_CENTS = 1.0
v42.shadow.ENTRY_ASK_CAP_CENTS = 100.0
v42.shadow.ENTRY_MIN_STC = 0.0
v42.shadow.ENTRY_MAX_STC = 600.0
v42.shadow.EXIT_PROB_FLOOR = 0.52
v42.shadow.EXIT_MIN_HOLD_SECONDS = 15.0
v42.shadow.LOCK_PATH = OUT_DIR / "v69_v55_entry_v66_exit_shadow_lock.json"
v42.shadow.REGISTRY_PATH = OUT_DIR / "v69_v55_entry_v66_exit_shadow_registry_latest.csv"
v42.shadow.REPORT_MD = OUT_DIR / "v69_v55_entry_v66_exit_shadow_monitor_latest.md"
v42.shadow.REPORT_JSON = OUT_DIR / "v69_v55_entry_v66_exit_shadow_monitor_latest.json"


def load_or_create_lock() -> dict:
    lock = ORIGINAL_LOAD_OR_CREATE_LOCK()
    lock["lock_id"] = "v69_v55_entry_v66_exit_shadow_v1"
    lock["policy"] = v42.POLICY
    lock["entry_surface"] = "v55_bookanchor_m10_v20_g05_book_plus2"
    lock["exit_surface"] = "v66_no_bookgap_g08_blend75"
    lock["entry"] = {
        "edge_floor_cents": 0.0,
        "p_side_floor": 0.65,
        "ask_floor_cents": 1.0,
        "ask_cap_cents": 100.0,
        "min_seconds_to_close": 0.0,
        "max_seconds_to_close": 600.0,
    }
    lock["exit"] = {"probability_floor": 0.52, "min_hold_seconds": 15.0}
    lock["purpose"] = "Strict-forward shadow validation of v69 v55-entry/v66-exit robustness candidate."
    v42.shadow.LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def opportunity_table(predictions: pd.DataFrame, lock: dict) -> pd.DataFrame:
    out = ENTRY_OPPORTUNITY_TABLE(predictions, lock).copy()
    if not out.empty:
        out["v69_entry_surface"] = "v55"
        out["v69_exit_surface"] = "v66_bal"
    return out


def adjusted_prediction_rows(predictions: pd.DataFrame, lock: dict) -> pd.DataFrame:
    opps = EXIT_OPPORTUNITY_TABLE(predictions, lock)[["opportunity_key", "p_yes", "no_bookgap_shrink_active"]]
    out = predictions.merge(opps, on="opportunity_key", how="left")
    out["p_yes"] = pd.to_numeric(out["p_yes"], errors="coerce").fillna(
        pd.to_numeric(out[f"{v42.shadow.MODEL}_p_yes"], errors="coerce")
    ).clip(1e-6, 1.0 - 1e-6)
    out["entry_dt"] = pd.to_datetime(out["entry_dt"], utc=True, errors="coerce")
    out["bid_cents"] = pd.to_numeric(out["bid_cents"], errors="coerce")
    return out


v42.opportunity_table = opportunity_table
v42.adjusted_prediction_rows = adjusted_prediction_rows
v42.load_or_create_lock = load_or_create_lock


if __name__ == "__main__":
    raise SystemExit(v42.main())
