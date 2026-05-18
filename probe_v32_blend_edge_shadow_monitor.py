"""Strict forward wrapper for the time/v32-drift blended FV edge candidate.

Candidate:

    book_time_v32drift85_first_edge1

This blends the train-fit time-aware book/v31 posterior with the train-fit
book/v32 3-minute-drift posterior in log-odds space:

    15% book_v31_time_platt + 85% book_v32_drift3_platt

The retrospective cost pressure test found this candidate kept about 99.5%
minimum split coverage and stayed positive after a full 2c per-contract cost.
This monitor is strict-forward only; no orders are submitted and no live bot
files/processes are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

import probe_v31_calibrated_edge_shadow_monitor as base
import probe_v32_drift_edge_shadow_monitor as drift


BOOK_V31_TIME_PLATT_COEF = (-0.004612015842067466, 1.1949037009646317, -0.09568923267788405, 0.10991831357346939)
TIME_WEIGHT = 0.15
DRIFT_WEIGHT = 0.85


def opportunity_candidates_blend(predictions: pd.DataFrame) -> pd.DataFrame:
    out = drift.opportunity_candidates_v32_drift(predictions)
    book_logit = base.logit_series(out["book_mid_probability_p_yes"])
    v31_logit = base.logit_series(out["v31_avg90_final60_exact_p_yes"])
    log_time = np.log(np.clip(pd.to_numeric(out["seconds_to_close"], errors="coerce"), 1.0, None) / 900.0)
    time_p = base.sigmoid_series(
        BOOK_V31_TIME_PLATT_COEF[0]
        + BOOK_V31_TIME_PLATT_COEF[1] * book_logit
        + BOOK_V31_TIME_PLATT_COEF[2] * v31_logit
        + BOOK_V31_TIME_PLATT_COEF[3] * log_time
    )
    drift_p = pd.to_numeric(out["book_v31_platt_p_yes"], errors="coerce").clip(1e-6, 1.0 - 1e-6)
    out["book_v31_platt_p_yes"] = base.sigmoid_series(
        TIME_WEIGHT * base.logit_series(time_p) + DRIFT_WEIGHT * base.logit_series(drift_p)
    )

    p_yes = pd.to_numeric(out["book_v31_platt_p_yes"], errors="coerce").clip(1e-6, 1.0 - 1e-6)
    out["fair_yes_cents"] = 100.0 * p_yes
    out["fair_no_cents"] = 100.0 * (1.0 - p_yes)
    out["yes_edge_cents"] = out["fair_yes_cents"] - out["yes_ask_cents"]
    out["no_edge_cents"] = out["fair_no_cents"] - out["no_ask_cents"]
    yes_better = out["yes_edge_cents"].ge(out["no_edge_cents"])
    out["selected_side"] = np.where(yes_better, "yes", "no")
    out["selected_ask_cents"] = np.where(yes_better, out["yes_ask_cents"], out["no_ask_cents"])
    out["selected_edge_cents"] = np.where(yes_better, out["yes_edge_cents"], out["no_edge_cents"])
    return out


def load_or_create_lock_blend() -> dict:
    if base.LOCK_PATH.exists():
        try:
            payload = json.loads(base.LOCK_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass
    lock = {
        "lock_id": "v32_blend_edge_shadow_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model_defined_utc": base.model_defined_utc(),
        "mode": base.MODE,
        "policy": base.POLICY,
        "min_edge_cents": base.MIN_EDGE_CENTS,
        "coefficients": {
            "book_v31_time_platt": list(BOOK_V31_TIME_PLATT_COEF),
            "book_v32_drift3_platt": drift.BOOK_V32_DRIFT3_MODEL,
            "time_logit_weight": TIME_WEIGHT,
            "v32_drift3_logit_weight": DRIFT_WEIGHT,
        },
        "purpose": "Strict forward shadow validation of blended time/v32-drift FV edge capacity.",
    }
    base.LOCK_PATH.write_text(json.dumps(base.clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def main() -> int:
    base.POLICY = "book_time_v32drift85_first_edge1"
    base.MIN_EDGE_CENTS = 1.0
    base.LOCK_PATH = base.OUT_DIR / "v32_blend_edge_shadow_lock.json"
    base.REGISTRY_PATH = base.OUT_DIR / "v32_blend_edge_shadow_registry_latest.csv"
    base.REPORT_MD = base.OUT_DIR / "v32_blend_edge_shadow_monitor_latest.md"
    base.REPORT_JSON = base.OUT_DIR / "v32_blend_edge_shadow_monitor_latest.json"
    base.build_predictions = drift.build_predictions_v32
    base.opportunity_candidates = opportunity_candidates_blend
    base.load_or_create_lock = load_or_create_lock_blend
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
