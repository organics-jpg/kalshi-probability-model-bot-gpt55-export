"""Strict-forward shadow monitor for v42 full-book delayed entry challenger."""
from __future__ import annotations

from pathlib import Path

import probe_v42_latent_hole_book_shadow_monitor as v42


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"

v42.POLICY = "v42_latent_hole_book_edge0_p65_stc120_600_prob52"
v42.REPORT_PREFIX = "v42_latent_hole_book_p65_delayed_shadow"
v42.LATENT_POSTERIOR_MODE = "book"
v42.LATENT_BOOK_WEIGHT = 1.0
v42.shadow.POLICY = v42.POLICY
v42.shadow.ENTRY_EDGE_FLOOR_CENTS = 0.0
v42.shadow.ENTRY_P_SIDE_FLOOR = 0.65
v42.shadow.ENTRY_ASK_FLOOR_CENTS = 1.0
v42.shadow.ENTRY_ASK_CAP_CENTS = 100.0
v42.shadow.ENTRY_MIN_STC = 120.0
v42.shadow.ENTRY_MAX_STC = 600.0
v42.shadow.EXIT_PROB_FLOOR = 0.52
v42.shadow.LOCK_PATH = OUT_DIR / "v42_latent_hole_book_p65_delayed_shadow_lock.json"
v42.shadow.REGISTRY_PATH = OUT_DIR / "v42_latent_hole_book_p65_delayed_shadow_registry_latest.csv"
v42.shadow.REPORT_MD = OUT_DIR / "v42_latent_hole_book_p65_delayed_shadow_monitor_latest.md"
v42.shadow.REPORT_JSON = OUT_DIR / "v42_latent_hole_book_p65_delayed_shadow_monitor_latest.json"


if __name__ == "__main__":
    raise SystemExit(v42.main())
