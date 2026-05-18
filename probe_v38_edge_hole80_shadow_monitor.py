"""Strict-forward shadow monitor for the 80%-coverage v38 edge-hole candidate.

Candidate:
- v38 FV surface;
- first market signal with edge >= 0, p_side >= 0.65, ask <= 100, 0-600s to close;
- if that first signal has edge in (10c, 20c], block the whole market;
- otherwise shadow-enter and shadow-exit when p_side <= 0.54;
- rows may be late-ingested, but only if entry_dt is after the lock time;
- no orders are submitted and no live bot files/processes are touched.
"""
from __future__ import annotations

from pathlib import Path

import probe_v38_edge_hole_shadow_monitor as shadow


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"

shadow.POLICY = "v38_edgehole80_block_first_10_20_p65_prob54"
shadow.EDGE_HOLE_LOW = 10.0
shadow.EDGE_HOLE_HIGH = 20.0
shadow.EXIT_PROB_FLOOR = 0.54
shadow.LOCK_PATH = OUT_DIR / "v38_edge_hole80_shadow_lock.json"
shadow.REGISTRY_PATH = OUT_DIR / "v38_edge_hole80_shadow_registry_latest.csv"
shadow.REPORT_MD = OUT_DIR / "v38_edge_hole80_shadow_monitor_latest.md"
shadow.REPORT_JSON = OUT_DIR / "v38_edge_hole80_shadow_monitor_latest.json"


if __name__ == "__main__":
    raise SystemExit(shadow.main())
