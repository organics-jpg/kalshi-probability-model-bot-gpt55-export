"""Strict-forward shadow monitor for v50 thin-edge certainty FV."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import probe_v47_recross_hazard_shadow_monitor as v47_monitor
from probe_market_interval_80coverage import clean_json


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"
v42 = v47_monitor.v42
ORIGINAL_LOAD_OR_CREATE_LOCK = v42.load_or_create_lock


v42.POLICY = "v50_thinedge_ask90_edge1_stc450_cap75_edge0_p65_stc0_600_prob54"
v42.REPORT_PREFIX = "v50_thin_edge_certainty_shadow"
v42.shadow.POLICY = v42.POLICY
v42.shadow.ENTRY_EDGE_FLOOR_CENTS = 0.0
v42.shadow.ENTRY_P_SIDE_FLOOR = 0.65
v42.shadow.ENTRY_ASK_FLOOR_CENTS = 1.0
v42.shadow.ENTRY_ASK_CAP_CENTS = 100.0
v42.shadow.ENTRY_MIN_STC = 0.0
v42.shadow.ENTRY_MAX_STC = 600.0
v42.shadow.EXIT_PROB_FLOOR = 0.54
v42.shadow.LOCK_PATH = OUT_DIR / "v50_thin_edge_certainty_shadow_lock.json"
v42.shadow.REGISTRY_PATH = OUT_DIR / "v50_thin_edge_certainty_shadow_registry_latest.csv"
v42.shadow.REPORT_MD = OUT_DIR / "v50_thin_edge_certainty_shadow_monitor_latest.md"
v42.shadow.REPORT_JSON = OUT_DIR / "v50_thin_edge_certainty_shadow_monitor_latest.json"


def load_or_create_lock() -> dict:
    lock = ORIGINAL_LOAD_OR_CREATE_LOCK()
    lock["lock_id"] = "v50_thin_edge_certainty_shadow_v1"
    lock["policy"] = v42.POLICY
    lock["thin_edge_certainty"] = {
        "selected_ask_min_cents": 90.0,
        "selected_edge_max_cents": 1.0,
        "selected_p_side_cap": 0.75,
        "seconds_to_close_min": 450.0,
        "seconds_to_close_max": 600.0,
    }
    lock["purpose"] = "Strict-forward shadow validation of v50 thin-edge certainty FV candidate."
    v42.shadow.LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def opportunity_table(predictions: pd.DataFrame, lock: dict) -> pd.DataFrame:
    out = v47_monitor.opportunity_table(predictions, lock).copy()
    if out.empty:
        return out
    base_p = out["p_yes"].clip(1e-6, 1.0 - 1e-6)
    selected_side = out["selected_side"].astype(str)
    selected_p_side = np.where(selected_side.eq("yes"), base_p, 1.0 - base_p)
    hazard = (
        out["selected_ask_cents"].ge(90.0)
        & out["selected_edge_cents"].le(1.0)
        & out["seconds_to_close"].between(450.0, 600.0)
    ).fillna(False)
    capped_p_side = np.where(hazard, np.minimum(selected_p_side, 0.75), selected_p_side)
    p_yes = pd.Series(np.where(selected_side.eq("yes"), capped_p_side, 1.0 - capped_p_side), index=out.index).clip(
        1e-6,
        1.0 - 1e-6,
    )
    out["p_yes"] = p_yes
    out["thin_edge_certainty_active"] = hazard
    out["fair_yes_cents"] = 100.0 * p_yes
    out["fair_no_cents"] = 100.0 * (1.0 - p_yes)
    out["yes_edge_cents"] = out["fair_yes_cents"] - out["yes_ask_cents"]
    out["no_edge_cents"] = out["fair_no_cents"] - out["no_ask_cents"]
    yes_better = out["yes_edge_cents"].ge(out["no_edge_cents"])
    out["selected_side"] = np.where(yes_better, "yes", "no")
    out["selected_ask_cents"] = np.where(yes_better, out["yes_ask_cents"], out["no_ask_cents"])
    out["selected_edge_cents"] = np.where(yes_better, out["yes_edge_cents"], out["no_edge_cents"])
    out["selected_p_side"] = np.where(yes_better, p_yes, 1.0 - p_yes)
    return out


v42.opportunity_table = opportunity_table
v42.load_or_create_lock = load_or_create_lock


if __name__ == "__main__":
    raise SystemExit(v42.main())
