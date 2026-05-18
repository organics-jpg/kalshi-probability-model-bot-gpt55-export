"""Strict-forward shadow monitor for v55 book-anchored re-cross FV."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import probe_v50_thin_edge_certainty_shadow_monitor as v50_monitor
from probe_market_interval_80coverage import clean_json


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"
v42 = v50_monitor.v42
BASE_OPPORTUNITY_TABLE = v42.opportunity_table
ORIGINAL_LOAD_OR_CREATE_LOCK = v42.load_or_create_lock


v42.POLICY = "v55_bookanchor_m10_v20_g05_book_plus2_edge0_p65_stc0_600_prob52"
v42.REPORT_PREFIX = "v55_book_anchor_recross_shadow"
v42.shadow.POLICY = v42.POLICY
v42.shadow.ENTRY_EDGE_FLOOR_CENTS = 0.0
v42.shadow.ENTRY_P_SIDE_FLOOR = 0.65
v42.shadow.ENTRY_ASK_FLOOR_CENTS = 1.0
v42.shadow.ENTRY_ASK_CAP_CENTS = 100.0
v42.shadow.ENTRY_MIN_STC = 0.0
v42.shadow.ENTRY_MAX_STC = 600.0
v42.shadow.EXIT_PROB_FLOOR = 0.52
v42.shadow.LOCK_PATH = OUT_DIR / "v55_book_anchor_recross_shadow_lock.json"
v42.shadow.REGISTRY_PATH = OUT_DIR / "v55_book_anchor_recross_shadow_registry_latest.csv"
v42.shadow.REPORT_MD = OUT_DIR / "v55_book_anchor_recross_shadow_monitor_latest.md"
v42.shadow.REPORT_JSON = OUT_DIR / "v55_book_anchor_recross_shadow_monitor_latest.json"


def load_or_create_lock() -> dict:
    lock = ORIGINAL_LOAD_OR_CREATE_LOCK()
    lock["lock_id"] = "v55_book_anchor_recross_shadow_v1"
    lock["policy"] = v42.POLICY
    lock["book_anchor_recross"] = {
        "side_margin_sigma15_max": 1.0,
        "side_velocity_3m_min_dps": 0.20,
        "model_minus_book_min": 0.05,
        "mode": "book_plus2",
    }
    lock["entry"] = {
        "edge_floor_cents": 0.0,
        "p_side_floor": 0.65,
        "ask_floor_cents": 1.0,
        "ask_cap_cents": 100.0,
        "min_seconds_to_close": 0.0,
        "max_seconds_to_close": 600.0,
    }
    lock["exit"] = {"probability_floor": 0.52}
    lock["purpose"] = "Strict-forward shadow validation of v55 book-anchored re-cross FV candidate."
    v42.shadow.LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def recompute_selected(out: pd.DataFrame, p_yes: pd.Series) -> pd.DataFrame:
    out["p_yes"] = p_yes.clip(1e-6, 1.0 - 1e-6)
    out["fair_yes_cents"] = 100.0 * out["p_yes"]
    out["fair_no_cents"] = 100.0 * (1.0 - out["p_yes"])
    out["yes_edge_cents"] = out["fair_yes_cents"] - out["yes_ask_cents"]
    out["no_edge_cents"] = out["fair_no_cents"] - out["no_ask_cents"]
    yes_better = out["yes_edge_cents"].ge(out["no_edge_cents"])
    out["selected_side"] = np.where(yes_better, "yes", "no")
    out["selected_ask_cents"] = np.where(yes_better, out["yes_ask_cents"], out["no_ask_cents"])
    out["selected_edge_cents"] = np.where(yes_better, out["yes_edge_cents"], out["no_edge_cents"])
    out["selected_p_side"] = np.where(yes_better, out["p_yes"], 1.0 - out["p_yes"])
    return out


def opportunity_table(predictions: pd.DataFrame, lock: dict) -> pd.DataFrame:
    out = BASE_OPPORTUNITY_TABLE(predictions, lock).copy()
    if out.empty:
        return out
    p_yes = out["p_yes"].clip(1e-6, 1.0 - 1e-6)
    selected_side = out["selected_side"].astype(str)
    selected_p = pd.Series(np.where(selected_side.eq("yes"), p_yes, 1.0 - p_yes), index=out.index)
    book_p_yes = out["book_mid_p_yes"].astype(float).clip(1e-6, 1.0 - 1e-6)
    selected_book = pd.Series(np.where(selected_side.eq("yes"), book_p_yes, 1.0 - book_p_yes), index=out.index)
    gap = selected_p - selected_book
    margin = pd.to_numeric(out.get("recross_side_margin_sigma15"), errors="coerce")
    velocity = pd.to_numeric(out.get("recross_side_velocity_3m"), errors="coerce")
    book_anchor = (
        out["seconds_to_close"].between(0.0, 600.0)
        & margin.le(1.0)
        & velocity.ge(0.20)
        & gap.ge(0.05)
    ).fillna(False)
    adjusted = np.where(book_anchor, np.minimum(selected_p, selected_book + 0.02), selected_p)
    p_yes = pd.Series(np.where(selected_side.eq("yes"), adjusted, 1.0 - adjusted), index=out.index)
    out = recompute_selected(out, p_yes)
    out["book_anchor_recross_active"] = book_anchor
    return out


v42.opportunity_table = opportunity_table
v42.load_or_create_lock = load_or_create_lock


if __name__ == "__main__":
    raise SystemExit(v42.main())
