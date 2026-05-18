"""Strict-forward shadow monitor for v66 balanced NO-side book-gap FV.

Policy:
- base FV: v55 book-anchored re-cross;
- if the selected side is NO and selected model probability exceeds the book by
  at least 8c, blend 75% back toward the selected-side book probability;
- entry: edge >= 0c, p_side >= 0.65, ask 1-100c, 0-600s to close;
- exit: adjusted p_side <= 0.54.

Research-only. No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import probe_v55_book_anchor_recross_shadow_monitor as v55_monitor
from probe_market_interval_80coverage import clean_json


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"
v42 = v55_monitor.v42
BASE_OPPORTUNITY_TABLE = v42.opportunity_table
ORIGINAL_LOAD_OR_CREATE_LOCK = v42.load_or_create_lock

GAP_THRESHOLD = 0.08
BOOK_BLEND_WEIGHT = 0.75

v42.POLICY = "v66_no_bookgap_g08_blend75_edge0_p65_stc0_600_prob54"
v42.REPORT_PREFIX = "v66_no_bookgap_balanced_shadow"
v42.shadow.POLICY = v42.POLICY
v42.shadow.ENTRY_EDGE_FLOOR_CENTS = 0.0
v42.shadow.ENTRY_P_SIDE_FLOOR = 0.65
v42.shadow.ENTRY_ASK_FLOOR_CENTS = 1.0
v42.shadow.ENTRY_ASK_CAP_CENTS = 100.0
v42.shadow.ENTRY_MIN_STC = 0.0
v42.shadow.ENTRY_MAX_STC = 600.0
v42.shadow.EXIT_PROB_FLOOR = 0.54
v42.shadow.EXIT_MIN_HOLD_SECONDS = 0.0
v42.shadow.LOCK_PATH = OUT_DIR / "v66_no_bookgap_balanced_shadow_lock.json"
v42.shadow.REGISTRY_PATH = OUT_DIR / "v66_no_bookgap_balanced_shadow_registry_latest.csv"
v42.shadow.REPORT_MD = OUT_DIR / "v66_no_bookgap_balanced_shadow_monitor_latest.md"
v42.shadow.REPORT_JSON = OUT_DIR / "v66_no_bookgap_balanced_shadow_monitor_latest.json"


def load_or_create_lock() -> dict:
    lock = ORIGINAL_LOAD_OR_CREATE_LOCK()
    lock["lock_id"] = "v66_no_bookgap_balanced_shadow_v1"
    lock["policy"] = v42.POLICY
    lock["no_bookgap_shrink"] = {
        "selected_side": "no",
        "model_minus_book_min": GAP_THRESHOLD,
        "book_blend_weight": BOOK_BLEND_WEIGHT,
    }
    lock["entry"] = {
        "edge_floor_cents": 0.0,
        "p_side_floor": 0.65,
        "ask_floor_cents": 1.0,
        "ask_cap_cents": 100.0,
        "min_seconds_to_close": 0.0,
        "max_seconds_to_close": 600.0,
    }
    lock["exit"] = {"probability_floor": 0.54, "min_hold_seconds": 0.0}
    lock["purpose"] = "Strict-forward shadow validation of v66 balanced NO-side book-gap FV candidate."
    v42.shadow.LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def opportunity_table(predictions: pd.DataFrame, lock: dict) -> pd.DataFrame:
    out = BASE_OPPORTUNITY_TABLE(predictions, lock).copy()
    if out.empty:
        return out

    p_yes = out["p_yes"].clip(1e-6, 1.0 - 1e-6)
    selected_side = out["selected_side"].astype(str)
    selected_p = pd.Series(np.where(selected_side.eq("yes"), p_yes, 1.0 - p_yes), index=out.index)
    book_p_yes = out["book_mid_p_yes"].astype(float).clip(1e-6, 1.0 - 1e-6)
    selected_book = pd.Series(np.where(selected_side.eq("yes"), book_p_yes, 1.0 - book_p_yes), index=out.index)
    model_book_gap = selected_p - selected_book
    shrink = (
        out["seconds_to_close"].between(0.0, 600.0)
        & selected_side.eq("no")
        & model_book_gap.ge(GAP_THRESHOLD)
    ).fillna(False)
    adjusted = np.where(
        shrink,
        (1.0 - BOOK_BLEND_WEIGHT) * selected_p + BOOK_BLEND_WEIGHT * selected_book,
        selected_p,
    )
    p_yes = pd.Series(np.where(selected_side.eq("yes"), adjusted, 1.0 - adjusted), index=out.index)
    out = v55_monitor.recompute_selected(out, p_yes)
    out["no_bookgap_shrink_active"] = shrink
    out["no_bookgap_model_book_gap"] = model_book_gap
    return out


v42.opportunity_table = opportunity_table
v42.load_or_create_lock = load_or_create_lock


if __name__ == "__main__":
    raise SystemExit(v42.main())
