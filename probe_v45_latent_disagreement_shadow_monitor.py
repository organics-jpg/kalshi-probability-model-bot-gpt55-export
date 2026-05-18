"""Strict-forward shadow monitor for v45 latent disagreement switch."""
from __future__ import annotations

from pathlib import Path

import numpy as np

import probe_v42_latent_hole_book_shadow_monitor as v42


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"
ORIGINAL_OPPORTUNITY_TABLE = v42.opportunity_table


v42.POLICY = "v45_latent_disagree_book_else_blend90_edge0_p65_stc0_600_prob54"
v42.REPORT_PREFIX = "v45_latent_disagreement_shadow"
v42.LATENT_POSTERIOR_MODE = "book_blend"
v42.LATENT_BOOK_WEIGHT = 0.90
v42.shadow.POLICY = v42.POLICY
v42.shadow.ENTRY_EDGE_FLOOR_CENTS = 0.0
v42.shadow.ENTRY_P_SIDE_FLOOR = 0.65
v42.shadow.ENTRY_ASK_FLOOR_CENTS = 1.0
v42.shadow.ENTRY_ASK_CAP_CENTS = 100.0
v42.shadow.ENTRY_MIN_STC = 0.0
v42.shadow.ENTRY_MAX_STC = 600.0
v42.shadow.EXIT_PROB_FLOOR = 0.54
v42.shadow.LOCK_PATH = OUT_DIR / "v45_latent_disagreement_shadow_lock.json"
v42.shadow.REGISTRY_PATH = OUT_DIR / "v45_latent_disagreement_shadow_registry_latest.csv"
v42.shadow.REPORT_MD = OUT_DIR / "v45_latent_disagreement_shadow_monitor_latest.md"
v42.shadow.REPORT_JSON = OUT_DIR / "v45_latent_disagreement_shadow_monitor_latest.json"


def opportunity_table(predictions, lock):
    out = ORIGINAL_OPPORTUNITY_TABLE(predictions, lock).copy()
    if out.empty:
        return out
    book = out["book_mid_p_yes"].clip(1e-6, 1.0 - 1e-6)
    book_yes_edge = 100.0 * book - out["yes_ask_cents"]
    book_no_edge = 100.0 * (1.0 - book) - out["no_ask_cents"]
    book_side = np.where(book_yes_edge.ge(book_no_edge), "yes", "no")
    disagree = out["latent_hole_active"].fillna(False) & out["raw_selected_side"].astype(str).ne(book_side)
    out.loc[disagree, "p_yes"] = book.loc[disagree]

    p_yes = out["p_yes"].clip(1e-6, 1.0 - 1e-6)
    out["fair_yes_cents"] = 100.0 * p_yes
    out["fair_no_cents"] = 100.0 * (1.0 - p_yes)
    out["yes_edge_cents"] = out["fair_yes_cents"] - out["yes_ask_cents"]
    out["no_edge_cents"] = out["fair_no_cents"] - out["no_ask_cents"]
    yes_better = out["yes_edge_cents"].ge(out["no_edge_cents"])
    out["selected_side"] = np.where(yes_better, "yes", "no")
    out["selected_ask_cents"] = np.where(yes_better, out["yes_ask_cents"], out["no_ask_cents"])
    out["selected_edge_cents"] = np.where(yes_better, out["yes_edge_cents"], out["no_edge_cents"])
    out["selected_p_side"] = np.where(yes_better, p_yes, 1.0 - p_yes)
    out["latent_disagreement_book_switch"] = disagree
    return out


v42.opportunity_table = opportunity_table


if __name__ == "__main__":
    raise SystemExit(v42.main())
