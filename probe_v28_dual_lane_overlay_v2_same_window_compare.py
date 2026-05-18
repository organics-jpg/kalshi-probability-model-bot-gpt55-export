"""Same-window live comparator for dual-lane overlay filter v2.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

from pathlib import Path

import probe_v28_dual_lane_overlay_same_window_compare as compare


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"


def main() -> None:
    compare.FILTER_WATCH_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_v2_watch_latest.json"
    compare.OUT_JSON = OUT_DIR / "v28_dual_lane_overlay_v2_same_window_compare_latest.json"
    compare.OUT_MD = OUT_DIR / "v28_dual_lane_overlay_v2_same_window_compare_latest.md"
    report = compare.build_report()
    compare.write_md(report)
    print(compare.OUT_MD)


if __name__ == "__main__":
    main()
