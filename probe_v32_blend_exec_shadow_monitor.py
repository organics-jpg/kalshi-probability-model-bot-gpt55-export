"""Strict forward wrapper for the executable blended FV candidate.

Candidate:

    book_time_v32drift85_exec_ask65_book55_first

Definition:
- blended posterior: 15% time-aware book/v31 + 85% book/v32 drift3
- first row per market with nonnegative gross model edge
- selected ask <= 65c
- selected book-side probability >= 55%

This candidate came from the executable frontier as a higher-coverage,
cost-robust shape. It is still strict-forward shadow only: no orders are
submitted and no live bot files/processes are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

import probe_v31_calibrated_edge_shadow_monitor as base
import probe_v32_blend_edge_shadow_monitor as blend


ASK_CAP_CENTS = 65.0
BOOK_SIDE_FLOOR = 0.55


def opportunity_candidates_exec(predictions: pd.DataFrame) -> pd.DataFrame:
    out = blend.opportunity_candidates_blend(predictions)
    denom = pd.to_numeric(out["yes_mid_cents"], errors="coerce") + pd.to_numeric(out["no_mid_cents"], errors="coerce")
    book_yes = pd.to_numeric(out["yes_mid_cents"], errors="coerce") / denom
    out["selected_book_p_side"] = np.where(out["selected_side"].astype(str).eq("yes"), book_yes, 1.0 - book_yes)
    ok = out["selected_ask_cents"].le(ASK_CAP_CENTS) & out["selected_book_p_side"].ge(BOOK_SIDE_FLOOR)
    out.loc[~ok, "selected_edge_cents"] = -999.0
    return out


def load_or_create_lock_exec() -> dict:
    if base.LOCK_PATH.exists():
        try:
            payload = json.loads(base.LOCK_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass
    lock = {
        "lock_id": "v32_blend_exec_shadow_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model_defined_utc": base.model_defined_utc(),
        "mode": base.MODE,
        "policy": base.POLICY,
        "min_edge_cents": base.MIN_EDGE_CENTS,
        "ask_cap_cents": ASK_CAP_CENTS,
        "book_side_floor": BOOK_SIDE_FLOOR,
        "coefficients": {
            "book_v31_time_platt": list(blend.BOOK_V31_TIME_PLATT_COEF),
            "book_v32_drift3_platt": blend.drift.BOOK_V32_DRIFT3_MODEL,
            "time_logit_weight": blend.TIME_WEIGHT,
            "v32_drift3_logit_weight": blend.DRIFT_WEIGHT,
        },
        "purpose": "Strict forward shadow validation of executable blended FV candidate.",
    }
    base.LOCK_PATH.write_text(json.dumps(base.clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def main() -> int:
    base.POLICY = "book_time_v32drift85_exec_ask65_book55_first"
    base.MIN_EDGE_CENTS = 0.0
    base.LOCK_PATH = base.OUT_DIR / "v32_blend_exec_shadow_lock.json"
    base.REGISTRY_PATH = base.OUT_DIR / "v32_blend_exec_shadow_registry_latest.csv"
    base.REPORT_MD = base.OUT_DIR / "v32_blend_exec_shadow_monitor_latest.md"
    base.REPORT_JSON = base.OUT_DIR / "v32_blend_exec_shadow_monitor_latest.json"
    base.build_predictions = blend.drift.build_predictions_v32
    base.opportunity_candidates = opportunity_candidates_exec
    base.load_or_create_lock = load_or_create_lock_exec
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
