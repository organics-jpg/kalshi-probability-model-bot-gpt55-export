"""Forward denominator for the all-day 80% v38 edge-hole candidate."""
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

import probe_v38_edge_hole_forward_denominator as denom  # noqa: E402


denom.REPORT_MD = OUT_DIR / "v38_edge_hole80_allday_forward_denominator_latest.md"
denom.REPORT_JSON = OUT_DIR / "v38_edge_hole80_allday_forward_denominator_latest.json"
denom.TABLE_CSV = OUT_DIR / "v38_edge_hole80_allday_forward_denominator_latest.csv"


if __name__ == "__main__":
    raise SystemExit(denom.main())
