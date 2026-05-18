"""Forward denominator table for the 80%-coverage v38 edge-hole candidate.

Research-only. Reads live logs and the separate 80%-candidate lock/registry;
no live bot logic, process, or order path is touched.
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

import probe_v38_edge_hole_forward_denominator as denom  # noqa: E402


denom.REPORT_MD = OUT_DIR / "v38_edge_hole80_forward_denominator_latest.md"
denom.REPORT_JSON = OUT_DIR / "v38_edge_hole80_forward_denominator_latest.json"
denom.TABLE_CSV = OUT_DIR / "v38_edge_hole80_forward_denominator_latest.csv"


if __name__ == "__main__":
    raise SystemExit(denom.main())
