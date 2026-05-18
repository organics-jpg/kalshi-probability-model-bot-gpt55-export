"""Strict forward wrapper for the executable v33 blended FV candidate.

Candidate:

    book_time_v33drift85_exec_ask65_pside60_first

Definition:
- blended posterior: 15% time-aware book/v31 + 85% book/v33 drift3
- first row per market with nonnegative gross model edge
- selected ask <= 65c
- selected model-side probability >= 60%

This candidate came from the executable frontier after adding the v33
anti-persistence FV surface. It is strict-forward shadow only: no orders are
submitted and no live bot files/processes are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

import probe_v31_calibrated_edge_shadow_monitor as base
import probe_v32_drift_edge_shadow_monitor as drift
from btc_mushroom_forecaster_v31_fast import FastMushroomFVEngineV31, FastMushroomV31Config
from btc_mushroom_forecaster_v33_fast import FastMushroomFVEngineV33, FastMushroomV33Config
from probe_mushroom_v29_fv_surface import EngineSpec


BOOK_V31_TIME_PLATT_COEF = (-0.004612015842067466, 1.1949037009646317, -0.09568923267788405, 0.10991831357346939)
BOOK_V33_DRIFT3_MODEL: dict[str, Any] = {
    "beta": [0.27162666229940724, 5.7089653104385985, -0.3732936866517675, -0.0191327801620111],
    "means": [0.30602584280358985, 0.27120764395971714, 14.95702720664451],
    "scales": [4.79465805377082, 4.424230572317068, 187.65210760731622],
    "l2": 0.3,
}
TIME_WEIGHT = 0.15
DRIFT_WEIGHT = 0.85
ASK_CAP_CENTS = 65.0
PSIDE_FLOOR = 0.60


def build_predictions_v33(frame: pd.DataFrame) -> pd.DataFrame:
    engines = [
        EngineSpec(
            "v31_avg90_final60_exact",
            FastMushroomFVEngineV31(
                FastMushroomV31Config(settlement_average_seconds=90.0, exact_average_inside_seconds=60.0)
            ),
            "v31 proxy-aware final-minute exact settlement-average variance",
        ),
        EngineSpec(
            "v33_antipersist3",
            FastMushroomFVEngineV33(
                FastMushroomV33Config(settlement_average_seconds=110.0, exact_average_inside_seconds=60.0)
            ),
            "v33 anti-persistence FV surface",
        ),
    ]
    return base.replay_predictions(frame, base.load_candles(), engines)


def opportunity_candidates_v33_exec(predictions: pd.DataFrame) -> pd.DataFrame:
    base_rows = predictions.drop_duplicates("opportunity_key", keep="first").copy()
    yes = (
        predictions[predictions["side"].astype(str).eq("yes")][["opportunity_key", "ask_cents", "book_mid_cents"]]
        .drop_duplicates("opportunity_key")
        .rename(columns={"ask_cents": "yes_ask_cents", "book_mid_cents": "yes_mid_cents"})
    )
    no = (
        predictions[predictions["side"].astype(str).eq("no")][["opportunity_key", "ask_cents", "book_mid_cents"]]
        .drop_duplicates("opportunity_key")
        .rename(columns={"ask_cents": "no_ask_cents", "book_mid_cents": "no_mid_cents"})
    )
    out = base_rows.merge(yes, on="opportunity_key", how="left").merge(no, on="opportunity_key", how="left")
    for col in [
        "yes_ask_cents",
        "no_ask_cents",
        "yes_mid_cents",
        "no_mid_cents",
        "strike",
        "seconds_to_close",
        "v31_avg90_final60_exact_p_yes",
        "v33_antipersist3_p_yes",
        "v33_antipersist3_sigma_t_dollars",
        "v33_antipersist3_d_sigma",
    ]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["entry_dt"] = pd.to_datetime(out["entry_dt"], utc=True, errors="coerce")

    denom = out["yes_mid_cents"] + out["no_mid_cents"]
    out["book_mid_probability_p_yes"] = out["yes_mid_cents"] / denom

    v33_sigma = out["v33_antipersist3_sigma_t_dollars"]
    v33_d = out["v33_antipersist3_d_sigma"]
    spot = out["strike"] - v33_d * v33_sigma
    lag_close = pd.to_numeric(drift.asof_lag_close(out["entry_dt"], 3), errors="coerce")
    velocity_dps = (spot.reset_index(drop=True) - lag_close) / (3.0 * 60.0)
    yes_drift3 = (spot.reset_index(drop=True) - out["strike"].reset_index(drop=True)) + velocity_dps * out[
        "seconds_to_close"
    ].reset_index(drop=True)

    book_logit = base.logit_series(out["book_mid_probability_p_yes"])
    v31_logit = base.logit_series(out["v31_avg90_final60_exact_p_yes"])
    v33_logit = base.logit_series(out["v33_antipersist3_p_yes"])
    log_time = np.log(np.clip(pd.to_numeric(out["seconds_to_close"], errors="coerce"), 1.0, None) / 900.0)
    time_p = base.sigmoid_series(
        BOOK_V31_TIME_PLATT_COEF[0]
        + BOOK_V31_TIME_PLATT_COEF[1] * book_logit
        + BOOK_V31_TIME_PLATT_COEF[2] * v31_logit
        + BOOK_V31_TIME_PLATT_COEF[3] * log_time
    )
    drift_p = drift.predict_scaled(
        BOOK_V33_DRIFT3_MODEL,
        np.column_stack([book_logit, v33_logit, yes_drift3]),
    )
    out["book_v31_platt_p_yes"] = base.sigmoid_series(
        TIME_WEIGHT * base.logit_series(time_p) + DRIFT_WEIGHT * base.logit_series(drift_p)
    ).to_numpy(dtype=float)

    p_yes = pd.to_numeric(out["book_v31_platt_p_yes"], errors="coerce").clip(1e-6, 1.0 - 1e-6)
    out["fair_yes_cents"] = 100.0 * p_yes
    out["fair_no_cents"] = 100.0 * (1.0 - p_yes)
    out["yes_edge_cents"] = out["fair_yes_cents"] - out["yes_ask_cents"]
    out["no_edge_cents"] = out["fair_no_cents"] - out["no_ask_cents"]
    yes_better = out["yes_edge_cents"].ge(out["no_edge_cents"])
    out["selected_side"] = np.where(yes_better, "yes", "no")
    out["selected_ask_cents"] = np.where(yes_better, out["yes_ask_cents"], out["no_ask_cents"])
    out["selected_edge_cents"] = np.where(yes_better, out["yes_edge_cents"], out["no_edge_cents"])
    out["selected_p_side"] = np.where(yes_better, p_yes, 1.0 - p_yes)
    out["v31_p_yes"] = out["v33_antipersist3_p_yes"]

    ok = out["selected_ask_cents"].le(ASK_CAP_CENTS) & out["selected_p_side"].ge(PSIDE_FLOOR)
    out.loc[~ok, "selected_edge_cents"] = -999.0
    return out.sort_values(["entry_dt", "opportunity_key"]).reset_index(drop=True)


def load_or_create_lock_v33_exec() -> dict:
    if base.LOCK_PATH.exists():
        try:
            payload = json.loads(base.LOCK_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass
    lock = {
        "lock_id": "v33_blend_exec_shadow_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model_defined_utc": base.model_defined_utc(),
        "mode": base.MODE,
        "policy": base.POLICY,
        "min_edge_cents": base.MIN_EDGE_CENTS,
        "ask_cap_cents": ASK_CAP_CENTS,
        "pside_floor": PSIDE_FLOOR,
        "coefficients": {
            "book_v31_time_platt": list(BOOK_V31_TIME_PLATT_COEF),
            "book_v33_drift3_platt": BOOK_V33_DRIFT3_MODEL,
            "time_logit_weight": TIME_WEIGHT,
            "v33_drift3_logit_weight": DRIFT_WEIGHT,
        },
        "purpose": "Strict forward shadow validation of executable v33 blended FV candidate.",
    }
    base.LOCK_PATH.write_text(json.dumps(base.clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def main() -> int:
    base.POLICY = "book_time_v33drift85_exec_ask65_pside60_first"
    base.MIN_EDGE_CENTS = 0.0
    base.LOCK_PATH = base.OUT_DIR / "v33_blend_exec_shadow_lock.json"
    base.REGISTRY_PATH = base.OUT_DIR / "v33_blend_exec_shadow_registry_latest.csv"
    base.REPORT_MD = base.OUT_DIR / "v33_blend_exec_shadow_monitor_latest.md"
    base.REPORT_JSON = base.OUT_DIR / "v33_blend_exec_shadow_monitor_latest.json"
    base.build_predictions = build_predictions_v33
    base.opportunity_candidates = opportunity_candidates_v33_exec
    base.load_or_create_lock = load_or_create_lock_v33_exec
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
