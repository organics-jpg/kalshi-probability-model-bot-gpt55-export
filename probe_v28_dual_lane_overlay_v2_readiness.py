"""Overlay-specific readiness view for dual-lane overlay filter v2.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

from pathlib import Path

import probe_v28_dual_lane_overlay_readiness as readiness


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"


def main() -> None:
    readiness.FILTER_WATCH_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_v2_watch_latest.json"
    readiness.OVERLAY_SAME_WINDOW_JSON = OUT_DIR / "v28_dual_lane_overlay_v2_same_window_compare_latest.json"
    readiness.OUT_JSON = OUT_DIR / "v28_dual_lane_overlay_v2_readiness_latest.json"
    readiness.OUT_MD = OUT_DIR / "v28_dual_lane_overlay_v2_readiness_latest.md"
    report = readiness.build_report()
    readiness.write_md(report)
    print(readiness.OUT_MD)


if __name__ == "__main__":
    main()
