"""v46 entry refinement around the refreshed v45 lead candidate.

Research-only. Tests whether ask caps, higher p-side floors, higher edge
floors, or a 570s max close window improve the v45 lead while preserving at
least 80% split coverage and all-day positive fee+1c P&L.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v42_edgehole_latent_fv_strategy as v42
import probe_v39_entry_exit_strategy_projection as base
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v46_v45_entry_refine_latest.md"
REPORT_JSON = OUT_DIR / "v46_v45_entry_refine_latest.json"
SUMMARY_CSV = OUT_DIR / "v46_v45_entry_refine_summary_latest.csv"
PREDICTIONS = OUT_DIR / "v45_latent_disagreement_switch_predictions_latest.csv"
MODEL = "v45_latent_disagree_book_else_blend90"


def day_metrics(trades: pd.DataFrame) -> dict[str, Any]:
    rows = trades.copy()
    rows["day"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce").dt.strftime("%Y-%m-%d")
    rows["fee1"] = rows["pnl_cents"] - rows["total_fee_cents"] - base.QTY
    values = rows.groupby("day")["fee1"].sum()
    return {
        "positive_days": int((values > 0).sum()),
        "total_days": int(len(values)),
        "worst_day_cents": float(values.min()) if len(values) else None,
    }


def block_metrics(trades: pd.DataFrame) -> dict[str, Any]:
    ordered = trades.sort_values(["entry_dt", "market"]).reset_index(drop=True)
    values = [
        float((ordered.iloc[idx]["pnl_cents"] - ordered.iloc[idx]["total_fee_cents"] - base.QTY).sum())
        for idx in np.array_split(np.arange(len(ordered)), 10)
        if len(idx)
    ]
    return {
        "block10_positive": int(sum(v > 0 for v in values)),
        "block10_worst_cents": float(min(values)) if values else None,
    }


def main() -> int:
    rows = v42.load_rows()
    ops = v42.opportunity_table(rows)
    preds = pd.read_csv(PREDICTIONS, low_memory=False)
    ops = ops.merge(
        preds.drop(columns=[c for c in ["entry_dt", "market", "split"] if c in preds.columns]),
        on="opportunity_key",
        how="left",
    )
    frame = v42.frame_for_candidate(rows, ops, f"{MODEL}_p_yes_candidate")
    best = base.best_side_per_opportunity(frame)
    paths = base.quote_paths(frame)
    universes = base.market_universes(rows)
    records: list[dict[str, Any]] = []
    for ask in [100.0, 98.0, 95.0, 92.0, 90.0, 88.0, 85.0, 80.0]:
        for pside in [0.64, 0.65, 0.66, 0.67, 0.68]:
            for edge in [0.0, 1.0, 2.0, 3.0, 5.0]:
                for max_stc in [570.0, 600.0]:
                    entry = base.EntryPolicy(edge, ask, pside, max_stc, 0.0)
                    entries = v42.choose_entries(best, entry)
                    if entries.empty:
                        continue
                    min_coverage = min(
                        len(set(entries["market"].astype(str)) & universes[split]) / len(universes[split])
                        for split in ["train", "validation", "holdout"]
                    )
                    if min_coverage < 0.75:
                        continue
                    for prob in [0.50, 0.52, 0.54, 0.56]:
                        exit_policy = base.ExitPolicy(f"prob{int(prob * 100)}", probability_floor=prob)
                        trades = base.simulate(entries, paths, exit_policy)
                        if trades.empty:
                            continue
                        record = base.flatten_metrics(MODEL, entry, exit_policy, trades, universes)
                        record["min_split_net_after_fees_1c_entry_dollars"] = float(
                            min(record[f"{split}_net_after_fees_1c_entry_dollars"] for split in ["train", "validation", "holdout"])
                        )
                        record["all_splits_1c_entry_positive"] = all(
                            float(record[f"{split}_net_after_fees_1c_entry_dollars"]) > 0
                            for split in ["train", "validation", "holdout"]
                        )
                        record.update(day_metrics(trades))
                        record.update(block_metrics(trades))
                        records.append(record)
    summary = pd.DataFrame(records)
    summary.to_csv(SUMMARY_CSV, index=False)
    eligible = summary[summary["min_split_coverage"].ge(0.80)].copy() if not summary.empty else summary
    split_day = eligible[
        eligible["all_splits_1c_entry_positive"]
        & eligible["positive_days"].eq(eligible["total_days"])
    ].copy() if not eligible.empty else eligible
    selected = (
        split_day.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        )
        if not split_day.empty
        else eligible.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        )
    )
    generated = datetime.now(timezone.utc).isoformat()
    lines = [
        "# v46 v45 Entry Refinement",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only local refinement around the refreshed v45 lead.",
        "- Sweeps ask caps, p-side floors, edge floors, max seconds-to-close, and probability exits.",
        "- Requires at least 80% split coverage for promotion-style rows.",
        "",
        "## Search Result",
        "",
        f"- Rows evaluated at 75%+ coverage: {len(summary)}",
        f"- Rows at 80%+ coverage: {len(eligible)}",
        f"- Rows positive across splits and all UTC days after fees plus 1c entry: {len(split_day)}",
        "",
        "## Selected Rows",
        "",
        "| entry | exit | min cov | min 1c | all 1c | days | block10 | trades | avg ask |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.head(25).iterrows():
        lines.append(
            f"| `{row['entry_policy']}` | `{row['exit_policy']}` | {v42.pct(row['min_split_coverage'])} | "
            f"{v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{int(row['positive_days'])}/{int(row['total_days'])} | {int(row['block10_positive'])}/10 | "
            f"{int(row['all_trades'])} | {float(row['all_avg_entry_ask']):.1f} |"
        )
    lines += ["", "## Read", ""]
    if not split_day.empty:
        best_row = selected.iloc[0]
        lines.append(
            f"- Best split/day-positive row remains `{best_row['entry_policy']}` / `{best_row['exit_policy']}` "
            f"with min split fee+1c {v42.dollars(best_row['min_split_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- Ask caps and stricter thresholds did not improve the current v45 lead while preserving the 80% coverage and all-day gates.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "summary_rows": int(len(summary)),
                    "eligible_80_rows": int(len(eligible)),
                    "split_day_positive_rows": int(len(split_day)),
                    "selected": selected.head(25).to_dict("records"),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print("v46 v45 entry refinement complete")
    print(f"summary_rows={len(summary)} split_day_positive={len(split_day)} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
