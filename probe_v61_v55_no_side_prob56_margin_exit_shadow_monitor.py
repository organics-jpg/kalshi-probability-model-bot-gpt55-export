"""Strict-forward shadow monitor for v61: v55 FV with prob56 NO-side margin-gated exit.

Research-only. This tracks the robustness compromise from the v61 audit:
v55 entry/FV, 15s minimum hold, p_side <= 0.56 exit floor, and the same
NO-position YES-axis margin gate used by v60.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import probe_v60_v55_no_side_margin_exit_shadow_monitor as base
from probe_market_interval_80coverage import clean_json


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"
PROBABILITY_FLOOR = 0.56
POLICY = "v61_v55_bookanchor_hold15_prob56_noside_marginlte0p25_edge0_p65_stc0_600"

base.v42.POLICY = POLICY
base.v42.REPORT_PREFIX = "v61_v55_no_side_prob56_margin_exit_shadow"
base.shadow.POLICY = POLICY
base.shadow.EXIT_PROB_FLOOR = PROBABILITY_FLOOR
base.shadow.EXIT_MIN_HOLD_SECONDS = 15.0
base.shadow.LOCK_PATH = OUT_DIR / "v61_v55_no_side_prob56_margin_exit_shadow_lock.json"
base.shadow.REGISTRY_PATH = OUT_DIR / "v61_v55_no_side_prob56_margin_exit_shadow_registry_latest.csv"
base.shadow.REPORT_MD = OUT_DIR / "v61_v55_no_side_prob56_margin_exit_shadow_monitor_latest.md"
base.shadow.REPORT_JSON = OUT_DIR / "v61_v55_no_side_prob56_margin_exit_shadow_monitor_latest.json"


def load_or_create_lock() -> dict[str, Any]:
    lock = base.ORIGINAL_LOAD_OR_CREATE_LOCK()
    lock["lock_id"] = "v61_v55_no_side_prob56_margin_exit_shadow_v1"
    lock["policy"] = POLICY
    lock["exit"] = {
        "probability_floor": PROBABILITY_FLOOR,
        "min_hold_seconds": 15.0,
        "exit_yes_axis_margin_ceiling_sigma15": base.EXIT_YES_AXIS_MARGIN_CEILING_SIGMA15,
        "exit_rule": (
            "YES positions use hold15/prob56; NO positions exit only when p_side <= floor "
            "and YES-axis spot margin <= ceiling"
        ),
    }
    lock["purpose"] = (
        "Strict-forward shadow validation of v61 v55 FV with prob56 asymmetric "
        "NO-side YES-axis margin-gated probability exit."
    )
    base.shadow.LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def write_report(lock: dict[str, Any], registry, denom: dict[str, Any], new_count: int) -> None:
    base.write_report(lock, registry, denom, new_count)
    text = base.shadow.REPORT_MD.read_text(encoding="utf-8")
    text = text.replace("# v60 v55 NO-Side Margin Exit Shadow Monitor", "# v61 v55 NO-Side Prob56 Margin Exit Shadow Monitor")
    text = text.replace(
        "v60 v55 FV NO-side YES-axis margin-gated exit candidate",
        "v61 v55 FV prob56 NO-side YES-axis margin-gated exit candidate",
    )
    base.shadow.REPORT_MD.write_text(text, encoding="utf-8")


base.v42.load_or_create_lock = load_or_create_lock
base.v42.update_exits_and_outcomes = base.update_exits_and_outcomes
base.shadow.write_report = write_report


if __name__ == "__main__":
    raise SystemExit(base.v42.main())
