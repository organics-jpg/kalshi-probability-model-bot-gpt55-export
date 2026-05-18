"""Executable frontier for the blended FV posterior.

This is a research-only fair-value edge probe. It tests whether a small,
interpretable execution shape around the blended probability model can keep at
least 80% market coverage while improving cost robustness:

- models: `book_time_v32drift85_p_yes` and `book_time_v33drift85_p_yes`
- first qualifying row per market
- optional gross edge floor, ask cap, model side probability floor, and book
  side probability floor

No live bot code/process is touched and no orders are submitted.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from probe_market_interval_80coverage import clean_json, pct
from probe_v31_calibrated_fv_edge_capacity import opportunity_frame


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SURFACE_PATH = OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_all_heartbeats_latest.csv"
CALIBRATED_PATH = OUT_DIR / "v31_book_calibrated_probability_predictions_latest.csv"
REPORT_MD = OUT_DIR / "v32_blend_executable_frontier_latest.md"
REPORT_JSON = OUT_DIR / "v32_blend_executable_frontier_latest.json"
SUMMARY_CSV = OUT_DIR / "v32_blend_executable_frontier_summary_latest.csv"
SELECTIONS_CSV = OUT_DIR / "v32_blend_executable_frontier_selections_latest.csv"

EDGE_FLOORS = [0.0, 0.5, 1.0, 1.25, 1.5, 2.0]
ASK_CAPS = [60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0, 95.0, 100.0]
PSIDE_FLOORS = [0.0, 0.55, 0.60, 0.65, 0.70]
BOOK_SIDE_FLOORS = [0.0, 0.52, 0.55, 0.60, 0.65]
COST_CENTS = [0.0, 1.0, 2.0]
MIN_COVERAGE = 0.80
MODEL_CONFIGS = [
    ("book_time_v32drift85", "book_time_v32drift85_p_yes"),
    ("book_time_v33drift85", "book_time_v33drift85_p_yes"),
]


def enrich(rows: pd.DataFrame, p_col: str) -> pd.DataFrame:
    out = rows.dropna(subset=[p_col, "yes_ask_cents", "no_ask_cents", "entry_dt"]).copy()
    p_yes = pd.to_numeric(out[p_col], errors="coerce").clip(1e-6, 1.0 - 1e-6)
    out["fair_yes_cents"] = 100.0 * p_yes
    out["fair_no_cents"] = 100.0 * (1.0 - p_yes)
    out["yes_edge_cents"] = out["fair_yes_cents"] - out["yes_ask_cents"]
    out["no_edge_cents"] = out["fair_no_cents"] - out["no_ask_cents"]
    yes_better = out["yes_edge_cents"].ge(out["no_edge_cents"])
    out["selected_side"] = np.where(yes_better, "yes", "no")
    out["selected_ask_cents"] = np.where(yes_better, out["yes_ask_cents"], out["no_ask_cents"])
    out["selected_edge_cents"] = np.where(yes_better, out["yes_edge_cents"], out["no_edge_cents"])
    out["selected_p_side"] = np.where(yes_better, p_yes, 1.0 - p_yes)
    denom = out["yes_book_mid_cents"] + out["no_book_mid_cents"]
    book_yes = out["yes_book_mid_cents"] / denom
    out["selected_book_p_side"] = np.where(yes_better, book_yes, 1.0 - book_yes)
    return out.sort_values(["entry_dt", "opportunity_key"]).reset_index(drop=True)


def select_first(rows: pd.DataFrame, model: str, edge: float, ask: float, pside: float, book_side: float) -> pd.DataFrame:
    work = rows[
        rows["selected_edge_cents"].ge(edge)
        & rows["selected_ask_cents"].le(ask)
        & rows["selected_p_side"].ge(pside)
        & rows["selected_book_p_side"].ge(book_side)
    ].copy()
    if work.empty:
        return work
    first = work.groupby("market", as_index=False, sort=False).first()
    first["win"] = first["selected_side"].eq(np.where(first["outcome_yes"], "yes", "no"))
    first["gross_net_cents"] = np.where(first["win"], 100.0 - first["selected_ask_cents"], -first["selected_ask_cents"])
    first["edge_floor_cents"] = edge
    first["ask_cap_cents"] = ask
    first["pside_floor"] = pside
    first["book_side_floor"] = book_side
    first["policy"] = (
        f"{model}_edge{edge:g}_ask{ask:g}_pside{pside:g}_book{book_side:g}"
    )
    return first


def market_denoms(rows: pd.DataFrame) -> pd.DataFrame:
    markets = rows[["market", "split", "entry_dt"]].drop_duplicates("market").sort_values("entry_dt").reset_index(drop=True)
    markets["block10"] = pd.qcut(np.arange(len(markets)), q=10, labels=False)
    return markets


def summarize(selected: pd.DataFrame, markets: pd.DataFrame, cost: float) -> dict[str, Any]:
    out: dict[str, Any] = {"cost_cents": cost}
    for split in ["all", "train", "validation", "holdout"]:
        denom = markets if split == "all" else markets[markets["split"].astype(str).eq(split)]
        part = selected if split == "all" else selected[selected["split"].astype(str).eq(split)]
        selected_markets = int(part["market"].nunique()) if not part.empty else 0
        resolved_markets = int(denom["market"].nunique())
        gross = float(pd.to_numeric(part.get("gross_net_cents"), errors="coerce").sum()) if not part.empty else 0.0
        net = gross - cost * selected_markets
        out[f"{split}_coverage"] = selected_markets / resolved_markets if resolved_markets else None
        out[f"{split}_selected"] = selected_markets
        out[f"{split}_net_after_cost_cents"] = net
    block_rows = selected.merge(markets[["market", "block10"]], on="market", how="left") if not selected.empty else selected
    block_nets = []
    for block in range(10):
        block_part = block_rows[block_rows["block10"].eq(block)] if not block_rows.empty else block_rows
        block_nets.append(
            float(pd.to_numeric(block_part.get("gross_net_cents"), errors="coerce").sum()) - cost * len(block_part)
            if not block_part.empty
            else 0.0
        )
    out["block10_positive"] = int(sum(net > 0 for net in block_nets))
    out["block10_worst_net_cents"] = float(min(block_nets))
    return out


def write_report(summary: pd.DataFrame) -> None:
    robust = summary[
        summary["cost_cents"].eq(2.0)
        & summary["train_coverage"].ge(MIN_COVERAGE)
        & summary["validation_coverage"].ge(MIN_COVERAGE)
        & summary["holdout_coverage"].ge(MIN_COVERAGE)
        & summary["train_net_after_cost_cents"].gt(0)
        & summary["validation_net_after_cost_cents"].gt(0)
        & summary["holdout_net_after_cost_cents"].gt(0)
    ].copy()
    robust["min_split_coverage"] = robust[["train_coverage", "validation_coverage", "holdout_coverage"]].min(axis=1)
    robust["min_split_net_after_cost_cents"] = robust[
        ["train_net_after_cost_cents", "validation_net_after_cost_cents", "holdout_net_after_cost_cents"]
    ].min(axis=1)
    robust = robust.sort_values(
        ["block10_positive", "block10_worst_net_cents", "min_split_net_after_cost_cents", "all_net_after_cost_cents"],
        ascending=[False, False, False, False],
    )
    lines = [
        "# v32 Blend Executable Frontier",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope",
        "",
        "- Research-only executable frontier for the blended FV posterior.",
        "- First qualifying row per market; no exits; no live orders or bot changes.",
        "- Robust rows below require train/validation/holdout coverage >= 80% and positive net after 2c cost.",
        "",
        "## Robust 2c-Cost Rows",
        "",
        "| policy | split coverage min | split net min | all net | block10 positive | worst block | train/val/holdout net |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    if robust.empty:
        lines.append("| none |  |  |  |  |  |  |")
    else:
        for _, row in robust.head(20).iterrows():
            lines.append(
                f"| `{row['policy']}` | {pct(row['min_split_coverage'])} | "
                f"{row['min_split_net_after_cost_cents']:.1f}c | {row['all_net_after_cost_cents']:.1f}c | "
                f"{int(row['block10_positive'])}/10 | {row['block10_worst_net_cents']:.1f}c | "
                f"{row['train_net_after_cost_cents']:.1f}/{row['validation_net_after_cost_cents']:.1f}/{row['holdout_net_after_cost_cents']:.1f}c |"
            )
    lines += [
        "",
        "## Read",
        "",
        "- Ask/book-side shaping can improve coverage-adjusted robustness, but this is still a searched frontier.",
        "- Treat any row here as a strict-forward shadow candidate, not a promotion.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not SURFACE_PATH.exists() or not CALIBRATED_PATH.exists():
        raise SystemExit("Missing surface/calibrated predictions.")
    surface = pd.read_csv(SURFACE_PATH, low_memory=False)
    calibrated = pd.read_csv(CALIBRATED_PATH, low_memory=False)
    base_rows = opportunity_frame(surface, calibrated)
    selections: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []
    for model, p_col in MODEL_CONFIGS:
        rows = enrich(base_rows, p_col)
        markets = market_denoms(rows)
        for edge in EDGE_FLOORS:
            for ask in ASK_CAPS:
                for pside in PSIDE_FLOORS:
                    for book_side in BOOK_SIDE_FLOORS:
                        selected = select_first(rows, model, edge, ask, pside, book_side)
                        if not selected.empty:
                            selections.append(selected)
                        policy = f"{model}_edge{edge:g}_ask{ask:g}_pside{pside:g}_book{book_side:g}"
                        base = {
                            "policy": policy,
                            "model": model,
                            "edge_floor_cents": edge,
                            "ask_cap_cents": ask,
                            "pside_floor": pside,
                            "book_side_floor": book_side,
                        }
                        for cost in COST_CENTS:
                            summary_rows.append({**base, **summarize(selected, markets, cost)})
    summary = pd.DataFrame(summary_rows)
    selection_df = pd.concat(selections, ignore_index=True, sort=False) if selections else pd.DataFrame()
    summary.to_csv(SUMMARY_CSV, index=False)
    selection_df.to_csv(SELECTIONS_CSV, index=False)
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": datetime.now(timezone.utc).isoformat(),
                    "model_configs": MODEL_CONFIGS,
                    "summary": summary.to_dict("records"),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(summary)
    print("v32 blend executable frontier complete")
    print(f"summary_rows={len(summary)} selections={len(selection_df)} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
