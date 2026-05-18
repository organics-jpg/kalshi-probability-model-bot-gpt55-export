"""Strict-forward shadow monitor for v53 weak re-cross plus thin-edge FV."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import probe_v45_latent_disagreement_shadow_monitor as v45_monitor
from probe_market_interval_80coverage import clean_json


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"
v42 = v45_monitor.v42
BASE_OPPORTUNITY_TABLE = v42.opportunity_table
ORIGINAL_LOAD_OR_CREATE_LOCK = v42.load_or_create_lock


v42.POLICY = "v53_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75_edge0_p65_stc0_600_prob54"
v42.REPORT_PREFIX = "v53_weak_recross_thin_edge_shadow"
v42.shadow.POLICY = v42.POLICY
v42.shadow.ENTRY_EDGE_FLOOR_CENTS = 0.0
v42.shadow.ENTRY_P_SIDE_FLOOR = 0.65
v42.shadow.ENTRY_ASK_FLOOR_CENTS = 1.0
v42.shadow.ENTRY_ASK_CAP_CENTS = 100.0
v42.shadow.ENTRY_MIN_STC = 0.0
v42.shadow.ENTRY_MAX_STC = 600.0
v42.shadow.EXIT_PROB_FLOOR = 0.54
v42.shadow.LOCK_PATH = OUT_DIR / "v53_weak_recross_thin_edge_shadow_lock.json"
v42.shadow.REGISTRY_PATH = OUT_DIR / "v53_weak_recross_thin_edge_shadow_registry_latest.csv"
v42.shadow.REPORT_MD = OUT_DIR / "v53_weak_recross_thin_edge_shadow_monitor_latest.md"
v42.shadow.REPORT_JSON = OUT_DIR / "v53_weak_recross_thin_edge_shadow_monitor_latest.json"


def load_or_create_lock() -> dict:
    lock = ORIGINAL_LOAD_OR_CREATE_LOCK()
    lock["lock_id"] = "v53_weak_recross_thin_edge_shadow_v1"
    lock["policy"] = v42.POLICY
    lock["weak_recross_hazard"] = {
        "side_margin_sigma15_max": 0.8,
        "side_velocity_3m_min_dps": 0.15,
        "selected_p_side_cap": 0.68,
        "seconds_to_close_min": 0.0,
        "seconds_to_close_max": 600.0,
    }
    lock["thin_edge_certainty"] = {
        "selected_ask_min_cents": 90.0,
        "selected_edge_max_cents": 1.0,
        "selected_p_side_cap": 0.75,
        "seconds_to_close_min": 450.0,
        "seconds_to_close_max": 600.0,
    }
    lock["purpose"] = "Strict-forward shadow validation of v53 weak re-cross plus thin-edge FV candidate."
    v42.shadow.LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def yes_side_features(predictions: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "opportunity_key",
        "margin_per_rv_sigma_15m",
        "signed_velocity_dps_1m",
        "signed_velocity_dps_3m",
    ]
    available = [col for col in columns if col in predictions.columns]
    yes = predictions[predictions["side"].astype(str).eq("yes")][available].drop_duplicates("opportunity_key")
    return yes.rename(
        columns={
            "margin_per_rv_sigma_15m": "yes_margin_sigma15",
            "signed_velocity_dps_1m": "yes_velocity_1m",
            "signed_velocity_dps_3m": "yes_velocity_3m",
        }
    )


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
    features = yes_side_features(predictions)
    out = out.merge(features, on="opportunity_key", how="left")
    for col in ["yes_margin_sigma15", "yes_velocity_1m", "yes_velocity_3m"]:
        out[col] = pd.to_numeric(out.get(col), errors="coerce")

    base_p = out["p_yes"].clip(1e-6, 1.0 - 1e-6)
    selected_side = out["selected_side"].astype(str)
    sign = np.where(selected_side.eq("yes"), 1.0, -1.0)
    selected_p_side = np.where(selected_side.eq("yes"), base_p, 1.0 - base_p)
    side_margin_sigma15 = sign * out["yes_margin_sigma15"]
    side_velocity_3m = sign * out["yes_velocity_3m"]
    weak_recross = (
        out["seconds_to_close"].between(0.0, 600.0)
        & side_margin_sigma15.le(0.8)
        & side_velocity_3m.ge(0.15)
    ).fillna(False)
    capped_p_side = np.where(weak_recross, np.minimum(selected_p_side, 0.68), selected_p_side)
    p_yes = pd.Series(np.where(selected_side.eq("yes"), capped_p_side, 1.0 - capped_p_side), index=out.index)
    out = recompute_selected(out, p_yes)
    out["recross_hazard_active"] = weak_recross
    out["recross_side_margin_sigma15"] = side_margin_sigma15
    out["recross_side_velocity_3m"] = side_velocity_3m

    selected_side = out["selected_side"].astype(str)
    selected_p_side = np.where(selected_side.eq("yes"), out["p_yes"], 1.0 - out["p_yes"])
    thin_edge = (
        out["selected_ask_cents"].ge(90.0)
        & out["selected_edge_cents"].le(1.0)
        & out["seconds_to_close"].between(450.0, 600.0)
    ).fillna(False)
    capped_p_side = np.where(thin_edge, np.minimum(selected_p_side, 0.75), selected_p_side)
    p_yes = pd.Series(np.where(selected_side.eq("yes"), capped_p_side, 1.0 - capped_p_side), index=out.index)
    out = recompute_selected(out, p_yes)
    out["thin_edge_certainty_active"] = thin_edge
    return out


v42.opportunity_table = opportunity_table
v42.load_or_create_lock = load_or_create_lock


if __name__ == "__main__":
    raise SystemExit(v42.main())
