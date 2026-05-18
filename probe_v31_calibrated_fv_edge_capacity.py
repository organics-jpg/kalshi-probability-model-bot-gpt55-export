"""Edge-capacity audit for calibrated FV probabilities.

This is a research-only bridge from probability quality to the user's coverage
constraint. It is not live bot scoring and it does not model exits. It asks a
minimal fair-value question:

If the calibrated probability model supplies fair YES/NO values, can a causal
"first qualifying positive edge per market" rule find enough ask-crossing edge
to cover 75-80% of BTC 15m markets?

Rows are walked chronologically. At most one opportunity per market is selected,
using only that row's quotes and probabilities. No live bot code/processes are
touched and no orders are submitted.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from probe_market_interval_80coverage import clean_json, pct


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SURFACE_PATH = OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_all_heartbeats_latest.csv"
CALIBRATED_PATH = OUT_DIR / "v31_book_calibrated_probability_predictions_latest.csv"
REPORT_MD = OUT_DIR / "v31_calibrated_fv_edge_capacity_latest.md"
REPORT_JSON = OUT_DIR / "v31_calibrated_fv_edge_capacity_latest.json"
SUMMARY_CSV = OUT_DIR / "v31_calibrated_fv_edge_capacity_summary_latest.csv"
SELECTIONS_CSV = OUT_DIR / "v31_calibrated_fv_edge_capacity_selections_latest.csv"

MIN_EDGE_CENTS = [0.0, 1.0, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 5.0, 7.0, 10.0]
MODELS = [
    ("v31_probability", "v31_probability_p_yes"),
    ("v32_probability", "v32_probability_p_yes"),
    ("v33_probability", "v33_probability_p_yes"),
    ("book_mid_probability", "book_mid_probability_p_yes"),
    ("book_platt", "book_platt_p_yes"),
    ("book_v31_platt", "book_v31_platt_p_yes"),
    ("book_v32_platt", "book_v32_platt_p_yes"),
    ("book_v33_platt", "book_v33_platt_p_yes"),
    ("book_v31_time_platt", "book_v31_time_platt_p_yes"),
    ("book_v31_drift3_platt", "book_v31_drift3_platt_p_yes"),
    ("book_v32_drift3_platt", "book_v32_drift3_platt_p_yes"),
    ("book_v33_drift3_platt", "book_v33_drift3_platt_p_yes"),
    ("book_time_v32drift85", "book_time_v32drift85_p_yes"),
    ("book_time_v33drift85", "book_time_v33drift85_p_yes"),
    ("book_v31_micro_platt", "book_v31_micro_platt_p_yes"),
]


def opportunity_frame(surface: pd.DataFrame, calibrated: pd.DataFrame) -> pd.DataFrame:
    quote_cols = [
        "yes_ask_cents",
        "no_ask_cents",
        "yes_bid_cents",
        "no_bid_cents",
        "yes_book_mid_cents",
        "no_book_mid_cents",
    ]
    base = calibrated.drop(columns=[col for col in quote_cols if col in calibrated.columns], errors="ignore").copy()
    quote_pivot = surface.pivot_table(
        index="opportunity_key",
        columns="side",
        values=["ask_cents", "bid_cents", "book_mid_cents"],
        aggfunc="first",
    )
    quote_pivot.columns = [f"{side}_{field}" for field, side in quote_pivot.columns]
    base = base.merge(quote_pivot, left_on="opportunity_key", right_index=True, how="left")
    for col in [
        "yes_ask_cents",
        "no_ask_cents",
        "yes_bid_cents",
        "no_bid_cents",
        "yes_book_mid_cents",
        "no_book_mid_cents",
    ]:
        if col in base:
            base[col] = pd.to_numeric(base[col], errors="coerce")
    base["entry_dt"] = pd.to_datetime(base["entry_dt"], utc=True, errors="coerce")
    base["outcome_yes"] = base["outcome"].astype(str).str.lower().eq("yes")
    return base.sort_values(["entry_dt", "opportunity_key"]).reset_index(drop=True)


def select_first_edges(rows: pd.DataFrame, model: str, p_col: str, min_edge: float) -> pd.DataFrame:
    work = rows.dropna(subset=[p_col, "yes_ask_cents", "no_ask_cents", "entry_dt"]).copy()
    p_yes = pd.to_numeric(work[p_col], errors="coerce").clip(1e-6, 1.0 - 1e-6)
    work["fair_yes_cents"] = 100.0 * p_yes
    work["fair_no_cents"] = 100.0 * (1.0 - p_yes)
    work["yes_edge_cents"] = work["fair_yes_cents"] - work["yes_ask_cents"]
    work["no_edge_cents"] = work["fair_no_cents"] - work["no_ask_cents"]
    yes_better = work["yes_edge_cents"].ge(work["no_edge_cents"])
    work["selected_side"] = np.where(yes_better, "yes", "no")
    work["selected_ask_cents"] = np.where(yes_better, work["yes_ask_cents"], work["no_ask_cents"])
    work["selected_edge_cents"] = np.where(yes_better, work["yes_edge_cents"], work["no_edge_cents"])
    work = work[work["selected_edge_cents"].ge(float(min_edge))].copy()
    if work.empty:
        return work
    first = work.sort_values(["entry_dt", "opportunity_key"]).groupby("market", as_index=False, sort=False).first()
    first["model"] = model
    first["min_edge_cents"] = float(min_edge)
    first["win"] = first["selected_side"].eq(np.where(first["outcome_yes"], "yes", "no"))
    first["gross_net_cents"] = np.where(first["win"], 100.0 - first["selected_ask_cents"], -first["selected_ask_cents"])
    return first


def summarize(selections: pd.DataFrame, all_markets: pd.DataFrame, model: str, min_edge: float, split: str) -> dict[str, Any]:
    market_part = all_markets if split == "all" else all_markets[all_markets["split"].astype(str).eq(split)]
    sel = selections if split == "all" else selections[selections["split"].astype(str).eq(split)]
    resolved_markets = int(market_part["market"].nunique())
    selected_markets = int(sel["market"].nunique()) if not sel.empty else 0
    wins = int(sel["win"].sum()) if not sel.empty else 0
    losses = int(len(sel) - wins) if not sel.empty else 0
    net = float(sel["gross_net_cents"].sum()) if not sel.empty else 0.0
    cost = float(sel["selected_ask_cents"].sum()) if not sel.empty else 0.0
    return {
        "model": model,
        "min_edge_cents": float(min_edge),
        "split": split,
        "resolved_markets": resolved_markets,
        "selected_markets": selected_markets,
        "coverage": selected_markets / resolved_markets if resolved_markets else None,
        "wins": wins,
        "losses": losses,
        "accuracy": wins / selected_markets if selected_markets else None,
        "gross_net_cents": net,
        "cost_cents": cost,
        "roi": net / cost if cost > 0 else None,
        "avg_selected_edge_cents": float(sel["selected_edge_cents"].mean()) if not sel.empty else None,
        "avg_ask_cents": float(sel["selected_ask_cents"].mean()) if not sel.empty else None,
    }


def write_report(summary: pd.DataFrame) -> None:
    holdout = summary[summary["split"].eq("holdout")].copy()
    high_cov = holdout[pd.to_numeric(holdout["coverage"], errors="coerce").ge(0.75)].copy()
    high_cov = high_cov.sort_values(["gross_net_cents", "coverage"], ascending=[False, False])
    best = holdout.sort_values(["gross_net_cents", "coverage"], ascending=[False, False]).head(12)
    lines = [
        "# Calibrated FV Edge Capacity",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope",
        "",
        "- Research-only fair-value edge-capacity audit.",
        "- Causal first qualifying positive-edge row per market; no exit model.",
        "- Gross hold-to-settlement cents only; no live orders or bot changes.",
        "",
        "## Holdout High-Coverage Rows",
        "",
        "| model | min edge | coverage | selected/resolved | W/L | gross net | ROI | avg edge | avg ask |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in high_cov.head(15).iterrows():
        lines.append(
            f"| `{row['model']}` | {row['min_edge_cents']:.1f} | {pct(row['coverage'])} | "
            f"{int(row['selected_markets'])}/{int(row['resolved_markets'])} | {int(row['wins'])}/{int(row['losses'])} | "
            f"{row['gross_net_cents']:.1f}c | {pct(row['roi'])} | {row['avg_selected_edge_cents']:.2f}c | {row['avg_ask_cents']:.2f}c |"
        )
    lines += [
        "",
        "## Best Holdout Net Rows",
        "",
        "| model | min edge | coverage | selected/resolved | W/L | gross net | ROI | avg edge | avg ask |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in best.iterrows():
        lines.append(
            f"| `{row['model']}` | {row['min_edge_cents']:.1f} | {pct(row['coverage'])} | "
            f"{int(row['selected_markets'])}/{int(row['resolved_markets'])} | {int(row['wins'])}/{int(row['losses'])} | "
            f"{row['gross_net_cents']:.1f}c | {pct(row['roi'])} | {row['avg_selected_edge_cents']:.2f}c | {row['avg_ask_cents']:.2f}c |"
        )
    lines += [
        "",
        "## Read",
        "",
        "- This is not a live-trading proof because it ignores exits, fees, position limits, and forward sample size.",
        "- Passing rows here only prove the calibrated FV model has enough gross ask-crossing edge capacity to investigate under the coverage constraint.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not SURFACE_PATH.exists() or not CALIBRATED_PATH.exists():
        raise SystemExit("Missing surface or calibrated probability predictions.")
    surface = pd.read_csv(SURFACE_PATH, low_memory=False)
    calibrated = pd.read_csv(CALIBRATED_PATH, low_memory=False)
    rows = opportunity_frame(surface, calibrated)
    all_markets = rows[["market", "split"]].drop_duplicates("market").copy()
    selections_all: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []
    for model, p_col in MODELS:
        for min_edge in MIN_EDGE_CENTS:
            selected = select_first_edges(rows, model, p_col, min_edge)
            if not selected.empty:
                selections_all.append(selected)
            for split in ["all", "train", "validation", "holdout"]:
                summary_rows.append(summarize(selected, all_markets, model, min_edge, split))
    selections = pd.concat(selections_all, ignore_index=True, sort=False) if selections_all else pd.DataFrame()
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(SUMMARY_CSV, index=False)
    selections.to_csv(SELECTIONS_CSV, index=False)
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "surface_path": str(SURFACE_PATH),
        "calibrated_path": str(CALIBRATED_PATH),
        "summary": summary.to_dict("records"),
    }
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(summary)
    print("v31 calibrated FV edge capacity complete")
    print(f"summary_rows={len(summary)} selections={len(selections)} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
