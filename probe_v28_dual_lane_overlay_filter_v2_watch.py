"""Own-freeze watch for the second dual-lane overlay filter.

Research-only; no live bot changes or orders.

This wrapper registers the current best observable same-window overlay shape as
its own forward branch: raw edge >= 0.05, recross hazard <= 0.30, and
absolute distance >= 0.85. It intentionally does not overwrite the earlier
NO-side overlay watch.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_v28_dual_lane_overlay_filter_watch as watch


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_v2_watch_state.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_v2_watch_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_overlay_filter_v2_watch_latest.md"

OVERLAY_NAME = "dual_lane_overlay_raw05_recross_le030_abs085"
RAW_EDGE_MIN = 0.05
RECROSS_MAX = 0.30
ABS_D_MIN = 0.85


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def load_or_create_state() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    if state.get("freeze_ts_utc"):
        return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "dual_lane_overlay_filter_v2_watch",
        "base_candidate": "dual_lane_overlap_union",
        "overlay_rule": {
            "name": OVERLAY_NAME,
            "raw_edge_min": RAW_EDGE_MIN,
            "recross_hazard_score_max": RECROSS_MAX,
            "abs_d_sigma_min": ABS_D_MIN,
            "use": "risk_control_overlay_only",
        },
        "note": (
            "Born after the refreshed same-window frontier preferred an observable "
            "raw-edge plus low-recross plus distance filter over the earlier NO-only rule."
        ),
    }
    write_json(STATE_JSON, state)
    return state


def should_keep(row: dict[str, Any]) -> bool:
    return (
        watch.base.fnum(row.get("raw_edge"), -math.inf) >= RAW_EDGE_MIN
        and watch.base.fnum(row.get("recross_hazard_score"), math.inf) <= RECROSS_MAX
        and watch.base.fnum(row.get("abs_d_sigma"), -math.inf) >= ABS_D_MIN
    )


def main() -> None:
    watch.STATE_JSON = STATE_JSON
    watch.OUT_JSON = OUT_JSON
    watch.OUT_MD = OUT_MD
    watch.OVERLAY_NAME = OVERLAY_NAME
    watch.OVERLAY_SIDE = ""
    watch.OVERLAY_RECROSS_MAX = RECROSS_MAX
    watch.load_or_create_state = load_or_create_state
    watch.should_keep = should_keep
    report = watch.build_report()
    report["read"] = [
        "Research-only own-freeze dual-lane overlay filter v2; no live bot changes or orders.",
        "This is an overlay-only branch, not a replacement for live v28.",
        "The rule is observable: raw edge >= 0.05, recross hazard <= 0.30, and abs distance >= 0.85.",
        "Rows before this freeze are diagnostic only and cannot promote this branch.",
    ]
    watch.write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
