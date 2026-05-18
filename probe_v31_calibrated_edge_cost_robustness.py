"""Cost robustness audit for calibrated FV edge-capacity selections.

Reads the research-only edge-capacity selections and asks whether high-coverage
candidates remain positive after simple per-contract cost assumptions. This is
not live bot scoring and does not model exits; it is a viability pressure test
for the fair-value edge signal under fees/slippage/buffer.
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
SUMMARY_PATH = OUT_DIR / "v31_calibrated_fv_edge_capacity_summary_latest.csv"
SELECTIONS_PATH = OUT_DIR / "v31_calibrated_fv_edge_capacity_selections_latest.csv"
REPORT_MD = OUT_DIR / "v31_calibrated_edge_cost_robustness_latest.md"
REPORT_JSON = OUT_DIR / "v31_calibrated_edge_cost_robustness_latest.json"
SUMMARY_CSV = OUT_DIR / "v31_calibrated_edge_cost_robustness_summary_latest.csv"

COST_CENTS = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
MIN_COVERAGE = 0.75


def finite_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)


def summarize(selections: pd.DataFrame, denominators: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    keys = selections[["model", "min_edge_cents"]].drop_duplicates().sort_values(["model", "min_edge_cents"])
    for _, key in keys.iterrows():
        model = str(key["model"])
        min_edge = float(key["min_edge_cents"])
        selected_all = selections[
            selections["model"].astype(str).eq(model)
            & finite_float(selections["min_edge_cents"]).eq(min_edge)
        ].copy()
        for cost in COST_CENTS:
            for split in ["all", "train", "validation", "holdout"]:
                denom = denominators[
                    denominators["model"].astype(str).eq(model)
                    & finite_float(denominators["min_edge_cents"]).eq(min_edge)
                    & denominators["split"].astype(str).eq(split)
                ]
                if denom.empty:
                    continue
                resolved_markets = int(denom.iloc[0]["resolved_markets"])
                selected = selected_all if split == "all" else selected_all[selected_all["split"].astype(str).eq(split)]
                selected_markets = int(selected["market"].nunique()) if not selected.empty else 0
                gross = float(finite_float(selected.get("gross_net_cents", pd.Series(dtype=float))).sum()) if not selected.empty else 0.0
                cost_total = float(cost) * selected_markets
                net_after_cost = gross - cost_total
                ask_cost = float(finite_float(selected.get("selected_ask_cents", pd.Series(dtype=float))).sum()) if not selected.empty else 0.0
                rows.append(
                    {
                        "model": model,
                        "min_edge_cents": min_edge,
                        "cost_cents": float(cost),
                        "split": split,
                        "resolved_markets": resolved_markets,
                        "selected_markets": selected_markets,
                        "coverage": selected_markets / resolved_markets if resolved_markets else None,
                        "gross_net_cents": gross,
                        "cost_total_cents": cost_total,
                        "net_after_cost_cents": net_after_cost,
                        "roi_after_cost": net_after_cost / (ask_cost + cost_total) if (ask_cost + cost_total) > 0 else None,
                    }
                )
    return pd.DataFrame(rows)


def write_report(summary: pd.DataFrame) -> None:
    holdout = summary[summary["split"].eq("holdout") & summary["coverage"].ge(MIN_COVERAGE)].copy()
    holdout = holdout.sort_values(["cost_cents", "net_after_cost_cents"], ascending=[True, False])
    robust_rows = []
    for (model, edge, cost), group in summary.groupby(["model", "min_edge_cents", "cost_cents"]):
        splits = group.set_index("split")
        if not {"train", "validation", "holdout"}.issubset(set(splits.index)):
            continue
        min_cov = float(splits.loc[["train", "validation", "holdout"], "coverage"].min())
        min_net = float(splits.loc[["train", "validation", "holdout"], "net_after_cost_cents"].min())
        robust_rows.append(
            {
                "model": model,
                "min_edge_cents": edge,
                "cost_cents": cost,
                "min_split_coverage": min_cov,
                "min_split_net_after_cost_cents": min_net,
                "train_net": float(splits.loc["train", "net_after_cost_cents"]),
                "validation_net": float(splits.loc["validation", "net_after_cost_cents"]),
                "holdout_net": float(splits.loc["holdout", "net_after_cost_cents"]),
            }
        )
    robust = pd.DataFrame(robust_rows)
    robust_pass = robust[
        robust["min_split_coverage"].ge(MIN_COVERAGE)
        & robust["min_split_net_after_cost_cents"].gt(0)
    ].sort_values(["cost_cents", "min_split_net_after_cost_cents"], ascending=[False, False])

    lines = [
        "# Calibrated Edge Cost Robustness",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope",
        "",
        "- Cost pressure test for research-only FV edge-capacity selections.",
        "- No exits, no live orders, no bot changes.",
        f"- Robust pass means train/validation/holdout all have coverage >= {pct(MIN_COVERAGE)} and positive net after cost.",
        "",
        "## Robust Pass Rows",
        "",
        "| model | min edge | cost | min split coverage | min split net | train | validation | holdout |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    if robust_pass.empty:
        lines.append("| none |  |  |  |  |  |  |  |")
    else:
        for _, row in robust_pass.iterrows():
            lines.append(
                f"| `{row['model']}` | {row['min_edge_cents']:.1f} | {row['cost_cents']:.1f} | "
                f"{pct(row['min_split_coverage'])} | {row['min_split_net_after_cost_cents']:.1f}c | "
                f"{row['train_net']:.1f}c | {row['validation_net']:.1f}c | {row['holdout_net']:.1f}c |"
            )
    lines += [
        "",
        "## Holdout High-Coverage Rows",
        "",
        "| model | min edge | cost | coverage | selected/resolved | net after cost | ROI after cost |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in holdout.head(25).iterrows():
        lines.append(
            f"| `{row['model']}` | {row['min_edge_cents']:.1f} | {row['cost_cents']:.1f} | "
            f"{pct(row['coverage'])} | {int(row['selected_markets'])}/{int(row['resolved_markets'])} | "
            f"{row['net_after_cost_cents']:.1f}c | {pct(row['roi_after_cost'])} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "- Gross edge capacity is not enough; fee/slippage/buffer can erase the validation margin.",
        "- If no row survives realistic costs across splits, the model needs either stronger edge, exits, or lower-cost execution before any promotion.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not SUMMARY_PATH.exists() or not SELECTIONS_PATH.exists():
        raise SystemExit("Missing edge-capacity summary/selections. Run probe_v31_calibrated_fv_edge_capacity.py first.")
    denominators = pd.read_csv(SUMMARY_PATH, low_memory=False)
    selections = pd.read_csv(SELECTIONS_PATH, low_memory=False)
    summary = summarize(selections, denominators)
    summary.to_csv(SUMMARY_CSV, index=False)
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "cost_cents": COST_CENTS,
        "min_coverage": MIN_COVERAGE,
        "summary": summary.to_dict("records"),
    }
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(summary)
    print("v31 calibrated edge cost robustness complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
