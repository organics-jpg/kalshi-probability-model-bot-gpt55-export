"""Forward denominator for v53 weak re-cross plus thin-edge FV."""
from __future__ import annotations

from pathlib import Path

import probe_v53_weak_recross_thin_edge_shadow_monitor as monitor  # noqa: F401
import probe_v42_latent_hole_book_forward_denominator as denom


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"

denom.REPORT_MD = OUT_DIR / "v53_weak_recross_thin_edge_forward_denominator_latest.md"
denom.REPORT_JSON = OUT_DIR / "v53_weak_recross_thin_edge_forward_denominator_latest.json"
denom.TABLE_CSV = OUT_DIR / "v53_weak_recross_thin_edge_forward_denominator_latest.csv"


if __name__ == "__main__":
    raise SystemExit(denom.main())
