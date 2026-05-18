"""Block-stability audit for the blended FV edge candidate.

This is a research-only overfit check. It does not score the live bot and does
not place orders. It asks whether the strongest high-coverage blended
fair-value edge candidate is spread across chronological blocks or carried by a
few lucky chunks.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from probe_market_interval_80coverage import clean_json, pct


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SELECTIONS_PATH = OUT_DIR / "v31_calibrated_fv_edge_capacity_selections_latest.csv"
PREDICTIONS_PATH = OUT_DIR / "v31_book_calibrated_probability_predictions_latest.csv"
REPORT_MD = OUT_DIR / "v32_blend_block_stability_latest.md"
REPORT_JSON = OUT_DIR / "v32_blend_block_stability_latest.json"
BLOCK_CSV = OUT_DIR / "v32_blend_block_stability_blocks_latest.csv"

MODELS = [
    ("book_time_v33drift85", 1.0),
    ("book_time_v32drift85", 1.0),
    ("book_v33_drift3_platt", 1.0),
    ("book_v31_time_platt", 1.0),
    ("book_v32_drift3_platt", 2.0),
    ("book_v33_platt", 2.5),
    ("book_v31_platt", 2.0),
]
COSTS = [0.0, 1.0, 2.0]


def market_blocks(preds: pd.DataFrame) -> pd.DataFrame:
    markets = (
        preds.groupby("market", as_index=False)
        .agg(first_entry=("entry_dt", "min"), split=("split", "first"), outcome_yes=("outcome_yes", "first"))
        .sort_values("first_entry")
        .reset_index(drop=True)
    )
    markets["block10"] = pd.qcut(np.arange(len(markets)), q=10, labels=False)
    markets["block20"] = pd.qcut(np.arange(len(markets)), q=20, labels=False)
    return markets


def build_blocks(selections: pd.DataFrame, markets: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for model, edge in MODELS:
        selected = selections[
            selections["model"].astype(str).eq(model)
            & pd.to_numeric(selections["min_edge_cents"], errors="coerce").eq(edge)
        ].copy()
        selected = selected.merge(markets[["market", "block10", "block20"]], on="market", how="left")
        for cost in COSTS:
            for block_col in ["block10", "block20"]:
                for block, block_markets in markets.groupby(block_col):
                    chosen = selected[selected[block_col].eq(block)]
                    denom = int(block_markets["market"].nunique())
                    wins = int(chosen["win"].astype(bool).sum()) if not chosen.empty else 0
                    losses = int(len(chosen) - wins)
                    gross = float(pd.to_numeric(chosen.get("gross_net_cents"), errors="coerce").sum()) if not chosen.empty else 0.0
                    net = gross - float(cost) * len(chosen)
                    rows.append(
                        {
                            "model": model,
                            "min_edge_cents": edge,
                            "cost_cents": cost,
                            "block_kind": block_col,
                            "block": int(block),
                            "denominator_markets": denom,
                            "selected_markets": int(len(chosen)),
                            "coverage": len(chosen) / denom if denom else None,
                            "wins": wins,
                            "losses": losses,
                            "gross_net_cents": gross,
                            "net_after_cost_cents": net,
                        }
                    )
    return pd.DataFrame(rows)


def write_report(blocks: pd.DataFrame) -> None:
    summary_rows: list[dict[str, Any]] = []
    for (model, edge, cost, block_kind), group in blocks.groupby(["model", "min_edge_cents", "cost_cents", "block_kind"]):
        nets = pd.to_numeric(group["net_after_cost_cents"], errors="coerce")
        cov = pd.to_numeric(group["coverage"], errors="coerce")
        summary_rows.append(
            {
                "model": model,
                "min_edge_cents": edge,
                "cost_cents": cost,
                "block_kind": block_kind,
                "positive_blocks": int(nets.gt(0).sum()),
                "blocks": int(len(group)),
                "positive_block_rate": float(nets.gt(0).mean()) if len(group) else None,
                "worst_block_net_cents": float(nets.min()) if len(group) else None,
                "min_block_coverage": float(cov.min()) if len(group) else None,
                "total_net_cents": float(nets.sum()),
            }
        )
    summary = pd.DataFrame(summary_rows).sort_values(
        ["cost_cents", "block_kind", "positive_block_rate", "worst_block_net_cents"],
        ascending=[False, True, False, False],
    )

    lines = [
        "# v32 Blend Block Stability",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope",
        "",
        "- Research-only block-stability audit for FV edge candidates.",
        "- No live bot code/process or orders are touched.",
        "- Negative blocks mean the aggregate edge may still be regime-sensitive.",
        "",
        "## Summary",
        "",
        "| model | edge | cost | block kind | positive blocks | worst block net | min block coverage | total block net |",
        "|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| `{row['model']}` | {row['min_edge_cents']:.1f} | {row['cost_cents']:.1f} | "
            f"`{row['block_kind']}` | {int(row['positive_blocks'])}/{int(row['blocks'])} | "
            f"{row['worst_block_net_cents']:.1f}c | {pct(row['min_block_coverage'])} | {row['total_net_cents']:.1f}c |"
        )
    lines += [
        "",
        "## Read",
        "",
        "- The blended candidate can be the best aggregate candidate while still failing strict block stability.",
        "- Treat this as a forward-shadow candidate until live sample size shows whether the bad blocks repeat.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": datetime.now(timezone.utc).isoformat(),
                    "models": MODELS,
                    "costs": COSTS,
                    "summary": summary.to_dict("records"),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    if not SELECTIONS_PATH.exists() or not PREDICTIONS_PATH.exists():
        raise SystemExit("Missing selections or calibrated probability predictions.")
    selections = pd.read_csv(SELECTIONS_PATH, low_memory=False)
    preds = pd.read_csv(PREDICTIONS_PATH, low_memory=False)
    blocks = build_blocks(selections, market_blocks(preds))
    blocks.to_csv(BLOCK_CSV, index=False)
    write_report(blocks)
    print("v32 blend block stability complete")
    print(f"block_rows={len(blocks)} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
