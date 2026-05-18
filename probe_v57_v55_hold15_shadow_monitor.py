"""Strict-forward shadow monitor for v57: v55 FV with hold15 prob52 exit."""
from __future__ import annotations

import json
from pathlib import Path

import probe_v55_book_anchor_recross_shadow_monitor as v55_monitor
from probe_market_interval_80coverage import clean_json


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"
v42 = v55_monitor.v42
ORIGINAL_LOAD_OR_CREATE_LOCK = v42.load_or_create_lock

v42.POLICY = "v57_v55_bookanchor_hold15_prob52_edge0_p65_stc0_600"
v42.REPORT_PREFIX = "v57_v55_hold15_shadow"
v42.shadow.POLICY = v42.POLICY
v42.shadow.EXIT_PROB_FLOOR = 0.52
v42.shadow.EXIT_MIN_HOLD_SECONDS = 15.0
v42.shadow.LOCK_PATH = OUT_DIR / "v57_v55_hold15_shadow_lock.json"
v42.shadow.REGISTRY_PATH = OUT_DIR / "v57_v55_hold15_shadow_registry_latest.csv"
v42.shadow.REPORT_MD = OUT_DIR / "v57_v55_hold15_shadow_monitor_latest.md"
v42.shadow.REPORT_JSON = OUT_DIR / "v57_v55_hold15_shadow_monitor_latest.json"


def load_or_create_lock() -> dict:
    lock = ORIGINAL_LOAD_OR_CREATE_LOCK()
    lock["lock_id"] = "v57_v55_hold15_shadow_v1"
    lock["policy"] = v42.POLICY
    lock["exit"] = {"probability_floor": 0.52, "min_hold_seconds": 15.0}
    lock["purpose"] = "Strict-forward shadow validation of v57 v55 FV with hold15 prob52 exit."
    v42.shadow.LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


v42.load_or_create_lock = load_or_create_lock


if __name__ == "__main__":
    raise SystemExit(v42.main())
