"""Wrapper validation for the delayed hazard-fallback logit55 wait8 trial."""
from __future__ import annotations

from probe_market_interval_80coverage import OUT_DIR
import probe_hazard_fallback_logit55_fresh_validation as base


base.LOCK_PATH = OUT_DIR / "profit_hazard_fallback_logit55_wait8_fresh_lock.json"
base.REPORT_LATEST = OUT_DIR / "profit_hazard_fallback_logit55_wait8_fresh_validation_latest.md"
base.JSON_LATEST = OUT_DIR / "profit_hazard_fallback_logit55_wait8_fresh_validation_latest.json"
base.SELECTED_LATEST = OUT_DIR / "profit_hazard_fallback_logit55_wait8_selected_latest.csv"


if __name__ == "__main__":
    raise SystemExit(base.main())
