"""Forward denominator for v55 book-anchored re-cross FV."""
from __future__ import annotations

from pathlib import Path

import probe_v55_book_anchor_recross_shadow_monitor as monitor  # noqa: F401
import probe_v42_latent_hole_book_forward_denominator as denom


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"

denom.REPORT_MD = OUT_DIR / "v55_book_anchor_recross_forward_denominator_latest.md"
denom.REPORT_JSON = OUT_DIR / "v55_book_anchor_recross_forward_denominator_latest.json"
denom.TABLE_CSV = OUT_DIR / "v55_book_anchor_recross_forward_denominator_latest.csv"


if __name__ == "__main__":
    raise SystemExit(denom.main())
