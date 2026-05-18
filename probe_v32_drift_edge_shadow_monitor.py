"""Strict forward wrapper for the book/v32 drift3 FV edge candidate.

This reuses the calibrated edge shadow monitor machinery, but shadows a
separate candidate:

    book_v32_drift3_platt_first_edge2

The candidate is a probability-model test, not a scorer patch. It uses the
train-fit calibrated posterior from `probe_v31_book_calibrated_probability.py`:
book log-odds, v32 log-odds, and YES-oriented 3-minute drift-projected margin.
Rows are registered only while the target market close is still in the future.
No orders are submitted and no live bot files/processes are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

import probe_v31_calibrated_edge_shadow_monitor as base
from btc_mushroom_forecaster_v31_fast import FastMushroomFVEngineV31, FastMushroomV31Config
from btc_mushroom_forecaster_v32_fast import FastMushroomFVEngineV32, FastMushroomV32Config
from probe_mushroom_v29_fv_surface import EngineSpec


BOOK_V32_DRIFT3_MODEL: dict[str, Any] = {
    "beta": [0.2717895408646071, 5.7043306716703075, -0.3718806083187627, -0.01572718781922455],
    "means": [0.30602584280358985, 0.26642162798491514, 14.95702720664451],
    "scales": [4.79465805377082, 4.374104091570937, 187.65210760731622],
    "l2": 0.3,
}
ORIGINAL_OPPORTUNITY_CANDIDATES = base.opportunity_candidates


def build_predictions_v32(frame: pd.DataFrame) -> pd.DataFrame:
    engines = [
        EngineSpec(
            "v31_avg90_final60_exact",
            FastMushroomFVEngineV31(
                FastMushroomV31Config(settlement_average_seconds=90.0, exact_average_inside_seconds=60.0)
            ),
            "v31 proxy-aware final-minute exact settlement-average variance",
        ),
        EngineSpec(
            "v32_avg110_final60_exact",
            FastMushroomFVEngineV32(
                FastMushroomV32Config(settlement_average_seconds=110.0, exact_average_inside_seconds=60.0)
            ),
            "v32 110s proxy-aware final-minute exact settlement-average variance",
        ),
    ]
    return base.replay_predictions(frame, base.load_candles(), engines)


def asof_lag_close(entry_dt: pd.Series, lag_minutes: int) -> pd.Series:
    candles = base.load_candles()[["close_dt", "close"]].dropna().sort_values("close_dt")
    targets = pd.DataFrame({"_idx": np.arange(len(entry_dt)), "target_dt": entry_dt - pd.to_timedelta(lag_minutes, unit="min")})
    targets = targets.sort_values("target_dt")
    joined = pd.merge_asof(
        targets,
        candles.rename(columns={"close_dt": "target_dt", "close": "lag_close"}),
        on="target_dt",
        direction="backward",
        tolerance=pd.Timedelta(seconds=120),
    )
    return joined.sort_values("_idx")["lag_close"].reset_index(drop=True)


def predict_scaled(model: dict[str, Any], features: np.ndarray) -> np.ndarray:
    beta = np.asarray(model["beta"], dtype=float)
    means = np.asarray(model["means"], dtype=float)
    scales = np.asarray(model["scales"], dtype=float)
    z = (np.asarray(features, dtype=float) - means) / scales
    design = np.column_stack([np.ones(len(z), dtype=float), z])
    return base.sigmoid_series(pd.Series(np.clip(design @ beta, -35.0, 35.0)))


def opportunity_candidates_v32_drift(predictions: pd.DataFrame) -> pd.DataFrame:
    out = ORIGINAL_OPPORTUNITY_CANDIDATES(predictions)
    for col in [
        "entry_dt",
        "strike",
        "seconds_to_close",
        "v32_avg110_final60_exact_p_yes",
        "v32_avg110_final60_exact_sigma_t_dollars",
        "v32_avg110_final60_exact_d_sigma",
    ]:
        if col == "entry_dt":
            out[col] = pd.to_datetime(out[col], utc=True, errors="coerce")
        else:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    v32_sigma = out["v32_avg110_final60_exact_sigma_t_dollars"]
    v32_d = out["v32_avg110_final60_exact_d_sigma"]
    spot = out["strike"] - v32_d * v32_sigma
    lag_close = pd.to_numeric(asof_lag_close(out["entry_dt"], 3), errors="coerce")
    velocity_dps = (spot.reset_index(drop=True) - lag_close) / (3.0 * 60.0)
    yes_drift3 = (spot.reset_index(drop=True) - out["strike"].reset_index(drop=True)) + velocity_dps * out[
        "seconds_to_close"
    ].reset_index(drop=True)

    book_logit = base.logit_series(out["book_mid_probability_p_yes"])
    v32_logit = base.logit_series(out["v32_avg110_final60_exact_p_yes"])
    out["book_v31_platt_p_yes"] = predict_scaled(
        BOOK_V32_DRIFT3_MODEL,
        np.column_stack([book_logit, v32_logit, yes_drift3]),
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
    out["v31_p_yes"] = out["v32_avg110_final60_exact_p_yes"]
    return out


def load_or_create_lock_drift() -> dict[str, Any]:
    if base.LOCK_PATH.exists():
        try:
            payload = json.loads(base.LOCK_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass
    lock = {
        "lock_id": "v32_drift3_edge_shadow_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model_defined_utc": base.model_defined_utc(),
        "mode": base.MODE,
        "policy": base.POLICY,
        "min_edge_cents": base.MIN_EDGE_CENTS,
        "coefficients": {"book_v32_drift3_platt": BOOK_V32_DRIFT3_MODEL},
        "purpose": "Strict forward shadow validation of book/v32 drift3 FV edge capacity.",
    }
    base.LOCK_PATH.write_text(json.dumps(base.clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def main() -> int:
    base.POLICY = "book_v32_drift3_platt_first_edge2"
    base.MIN_EDGE_CENTS = 2.0
    base.LOCK_PATH = base.OUT_DIR / "v32_drift_edge_shadow_lock.json"
    base.REGISTRY_PATH = base.OUT_DIR / "v32_drift_edge_shadow_registry_latest.csv"
    base.REPORT_MD = base.OUT_DIR / "v32_drift_edge_shadow_monitor_latest.md"
    base.REPORT_JSON = base.OUT_DIR / "v32_drift_edge_shadow_monitor_latest.json"
    base.build_predictions = build_predictions_v32
    base.opportunity_candidates = opportunity_candidates_v32_drift
    base.load_or_create_lock = load_or_create_lock_drift
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
