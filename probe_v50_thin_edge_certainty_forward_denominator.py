"""Forward denominator for v50 thin-edge certainty FV."""
from __future__ import annotations

from pathlib import Path

import probe_v50_thin_edge_certainty_shadow_monitor as monitor  # noqa: F401
import probe_v42_latent_hole_book_forward_denominator as denom


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"

denom.REPORT_MD = OUT_DIR / "v50_thin_edge_certainty_forward_denominator_latest.md"
denom.REPORT_JSON = OUT_DIR / "v50_thin_edge_certainty_forward_denominator_latest.json"
denom.TABLE_CSV = OUT_DIR / "v50_thin_edge_certainty_forward_denominator_latest.csv"


if __name__ == "__main__":
    raise SystemExit(denom.main())
