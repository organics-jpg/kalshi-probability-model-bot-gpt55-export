"""Forward denominator for v61 v55 prob56 NO-side margin-gated exit candidate."""
from __future__ import annotations

from pathlib import Path

import probe_v61_v55_no_side_prob56_margin_exit_shadow_monitor as monitor  # noqa: F401
import probe_v42_latent_hole_book_forward_denominator as denom


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"

denom.REPORT_MD = OUT_DIR / "v61_v55_no_side_prob56_margin_exit_forward_denominator_latest.md"
denom.REPORT_JSON = OUT_DIR / "v61_v55_no_side_prob56_margin_exit_forward_denominator_latest.json"
denom.TABLE_CSV = OUT_DIR / "v61_v55_no_side_prob56_margin_exit_forward_denominator_latest.csv"


if __name__ == "__main__":
    raise SystemExit(denom.main())
