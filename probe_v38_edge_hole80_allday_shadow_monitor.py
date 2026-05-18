"""Strict-forward shadow monitor for the all-day 80% v38 edge-hole candidate.

Candidate:
- v38 FV surface;
- first market signal with edge >= -2, p_side >= 0.65, ask 1-100c,
  60-600s to close;
- if that first signal has edge in (8c, 20c], block the whole market;
- otherwise shadow-enter and shadow-exit when p_side <= 0.54;
- no orders are submitted and no live bot files/processes are touched.
"""
from __future__ import annotations

from pathlib import Path

import probe_v38_edge_hole_shadow_monitor as shadow


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"

shadow.POLICY = "v38_edgehole80_allday_block_first_8_20_edge-2_p65_stc60_600_prob54"
shadow.ENTRY_EDGE_FLOOR_CENTS = -2.0
shadow.ENTRY_MIN_STC = 60.0
shadow.EDGE_HOLE_LOW = 8.0
shadow.EDGE_HOLE_HIGH = 20.0
shadow.EXIT_PROB_FLOOR = 0.54
shadow.LOCK_PATH = OUT_DIR / "v38_edge_hole80_allday_shadow_lock.json"
shadow.REGISTRY_PATH = OUT_DIR / "v38_edge_hole80_allday_shadow_registry_latest.csv"
shadow.REPORT_MD = OUT_DIR / "v38_edge_hole80_allday_shadow_monitor_latest.md"
shadow.REPORT_JSON = OUT_DIR / "v38_edge_hole80_allday_shadow_monitor_latest.json"


if __name__ == "__main__":
    raise SystemExit(shadow.main())
