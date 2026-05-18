"""Strict forward wrapper for the book_v31_time_platt edge candidate.

This reuses the v31 calibrated edge shadow monitor machinery, but shadows a
second candidate:

    book_v31_time_platt_first_edge1

The candidate passed the 2c-cost retrospective pressure test with very thin
holdout margin. It is tracked separately so it cannot contaminate the existing
book_v31_platt_first_edge2 registry.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import probe_v31_calibrated_edge_shadow_monitor as base


BOOK_V31_TIME_PLATT_COEF = (-0.004612015842067466, 1.1949037009646317, -0.09568923267788405, 0.10991831357346939)
ORIGINAL_OPPORTUNITY_CANDIDATES = base.opportunity_candidates


def opportunity_candidates_time(predictions: pd.DataFrame) -> pd.DataFrame:
    out = ORIGINAL_OPPORTUNITY_CANDIDATES(predictions)
    book_logit = base.logit_series(out["book_mid_probability_p_yes"])
    v31_logit = base.logit_series(out["v31_p_yes"])
    log_time = np.log(np.clip(pd.to_numeric(out["seconds_to_close"], errors="coerce"), 1.0, None) / 900.0)
    out["book_v31_platt_p_yes"] = base.sigmoid_series(
        BOOK_V31_TIME_PLATT_COEF[0]
        + BOOK_V31_TIME_PLATT_COEF[1] * book_logit
        + BOOK_V31_TIME_PLATT_COEF[2] * v31_logit
        + BOOK_V31_TIME_PLATT_COEF[3] * log_time
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


def main() -> int:
    base.POLICY = "book_v31_time_platt_first_edge1"
    base.MIN_EDGE_CENTS = 1.0
    base.LOCK_PATH = base.OUT_DIR / "v31_time_edge_shadow_lock.json"
    base.REGISTRY_PATH = base.OUT_DIR / "v31_time_edge_shadow_registry_latest.csv"
    base.REPORT_MD = base.OUT_DIR / "v31_time_edge_shadow_monitor_latest.md"
    base.REPORT_JSON = base.OUT_DIR / "v31_time_edge_shadow_monitor_latest.json"
    base.opportunity_candidates = opportunity_candidates_time
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
