"""Fine-grained fee-aware refinement around the v38/v39 75% candidates.

Research-only. This does not modify live bot code, processes, or orders.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v39_entry_exit_strategy_projection as base
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v38_fee_refine_exit_frontier_latest.md"
REPORT_JSON = OUT_DIR / "v38_fee_refine_exit_frontier_latest.json"
SUMMARY_CSV = OUT_DIR / "v38_fee_refine_exit_frontier_summary_latest.csv"
MIN_SPLIT_COVERAGE = 0.75

MODELS = ["v38_long60_antipersist"]
EDGE_FLOORS = [-2.0, 0.0]
P_SIDE_FLOORS = [0.64, 0.65, 0.66]
MAX_STC = [570.0, 600.0, 630.0]
MIN_STC = [0.0, 120.0]
EXIT_PROB_FLOORS = [round(x, 2) for x in np.arange(0.44, 0.521, 0.01)]


def block_metrics(trades: pd.DataFrame, blocks: int = 10) -> dict[str, Any]:
    if trades.empty:
        return {"positive_blocks": 0, "blocks": blocks, "worst": None, "mean": None}
    ordered = trades.sort_values(["entry_dt", "market"]).reset_index(drop=True)
    chunks = np.array_split(ordered, blocks)
    values = [
        float((chunk["pnl_cents"] - chunk["total_fee_cents"]).sum() / 100.0)
        for chunk in chunks
        if not chunk.empty
    ]
    return {
        "positive_blocks": int(sum(value > 0 for value in values)),
        "blocks": blocks,
        "worst": float(min(values)) if values else None,
        "mean": float(np.mean(values)) if values else None,
        "values": values,
    }


def row_has_1c_entry_positive(row: pd.Series) -> bool:
    return all(
        float(row[f"{split}_net_after_fees_1c_entry_dollars"]) > 0.0
        for split in ["train", "validation", "holdout"]
    )


def build_summary() -> tuple[pd.DataFrame, dict[str, Any]]:
    old_min = base.MIN_SPLIT_COVERAGE
    base.MIN_SPLIT_COVERAGE = MIN_SPLIT_COVERAGE
    try:
        rows = base.load_rows()
        universes = base.market_universes(rows)
        records: list[dict[str, Any]] = []
        debug: dict[str, Any] = {
            "models": MODELS,
            "entry_policy_count": len(EDGE_FLOORS) * len(P_SIDE_FLOORS) * len(MAX_STC) * len(MIN_STC),
            "exit_policy_count": len(EXIT_PROB_FLOORS) + 1,
        }
        for model in MODELS:
            frame = base.model_frame(rows, model)
            best_opp = base.best_side_per_opportunity(frame)
            paths = base.quote_paths(frame)
            for edge in EDGE_FLOORS:
                for pside in P_SIDE_FLOORS:
                    for max_stc in MAX_STC:
                        for min_stc in MIN_STC:
                            if min_stc >= max_stc:
                                continue
                            entry_policy = base.EntryPolicy(edge, 100.0, pside, max_stc, min_stc)
                            entries = base.choose_entries(best_opp, entry_policy)
                            if entries.empty:
                                continue
                            min_coverage = min(
                                len(set(entries["market"].astype(str)) & universes[split]) / len(universes[split])
                                for split in ["train", "validation", "holdout"]
                            )
                            if min_coverage < MIN_SPLIT_COVERAGE:
                                continue
                            exit_policies = [base.ExitPolicy("hold")]
                            exit_policies += [
                                base.ExitPolicy(f"prob{int(round(floor * 100)):02d}", probability_floor=floor)
                                for floor in EXIT_PROB_FLOORS
                            ]
                            for exit_policy in exit_policies:
                                trades = base.simulate(entries, paths, exit_policy)
                                if trades.empty:
                                    continue
                                record = base.flatten_metrics(model, entry_policy, exit_policy, trades, universes)
                                record["exit_probability_floor"] = exit_policy.probability_floor
                                record["min_split_net_after_fees_1c_entry_dollars"] = float(
                                    min(
                                        record[f"{split}_net_after_fees_1c_entry_dollars"]
                                        for split in ["train", "validation", "holdout"]
                                    )
                                )
                                record["all_splits_1c_entry_positive"] = row_has_1c_entry_positive(pd.Series(record))
                                records.append(record)
        return pd.DataFrame(records), debug
    finally:
        base.MIN_SPLIT_COVERAGE = old_min


def selected_rows(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return summary
    eligible = summary[summary["eligible_80"]].copy()
    if eligible.empty:
        return eligible
    pieces: list[pd.DataFrame] = []
    net_stable = eligible[eligible["all_splits_net_after_fees_positive"]].copy()
    if not net_stable.empty:
        pieces.append(
            net_stable.sort_values(
                ["min_split_net_after_fees_dollars", "all_net_after_fees_dollars"],
                ascending=[False, False],
            ).head(20)
        )
    one_cent_stable = eligible[eligible["all_splits_1c_entry_positive"]].copy()
    if not one_cent_stable.empty:
        pieces.append(
            one_cent_stable.sort_values(
                ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
                ascending=[False, False],
            ).head(20)
        )
    pieces.append(
        eligible.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).head(20)
    )
    return pd.concat(pieces, ignore_index=True, sort=False).drop_duplicates(
        ["model", "entry_policy", "exit_policy"]
    )


def attach_blocks(selected: pd.DataFrame) -> list[dict[str, Any]]:
    if selected.empty:
        return []
    rows = base.load_rows()
    block_records: list[dict[str, Any]] = []
    for _, selected_row in selected.head(20).iterrows():
        model = str(selected_row["model"])
        frame = base.model_frame(rows, model)
        best_opp = base.best_side_per_opportunity(frame)
        paths = base.quote_paths(frame)
        entry_policy = base.EntryPolicy(
            float(selected_row["entry_edge_floor_cents"]),
            float(selected_row["entry_ask_cap_cents"]),
            float(selected_row["entry_min_p_side"]),
            float(selected_row["entry_max_seconds_to_close"]),
            float(selected_row["entry_min_seconds_to_close"]),
        )
        exit_floor = selected_row.get("exit_probability_floor")
        if pd.isna(exit_floor):
            exit_policy = base.ExitPolicy(str(selected_row["exit_policy"]))
        else:
            exit_policy = base.ExitPolicy(str(selected_row["exit_policy"]), probability_floor=float(exit_floor))
        entries = base.choose_entries(best_opp, entry_policy)
        trades = base.simulate(entries, paths, exit_policy)
        rec = selected_row.to_dict()
        rec["block10"] = block_metrics(trades, 10)
        rec["block20"] = block_metrics(trades, 20)
        block_records.append(rec)
    return block_records


def write_report(summary: pd.DataFrame, selected: pd.DataFrame, block_records: list[dict[str, Any]], debug: dict[str, Any]) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    eligible = summary[summary["eligible_80"]].copy() if not summary.empty else summary
    net_stable = eligible[eligible["all_splits_net_after_fees_positive"]].copy() if not eligible.empty else eligible
    one_cent_stable = eligible[eligible["all_splits_1c_entry_positive"]].copy() if not eligible.empty else eligible
    lines = [
        "# v38 Fee Refined Exit Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Fine-grained refinement around v38/v39 fee-aware 75% candidates.",
        "- Sweeps p_side, seconds-to-close windows, edge floors, and probability-exit thresholds.",
        "- Requires at least 75% coverage in train, validation, and holdout.",
        "",
        "## Search Result",
        "",
        f"- Policy rows evaluated after coverage prefilter: {len(summary)}",
        f"- Fee-positive train/validation/holdout rows: {len(net_stable)}",
        f"- Fee-positive plus 1c-entry-haircut rows: {len(one_cent_stable)}",
        "",
        "## Selected Rows",
        "",
        "| model | entry | exit | min cov | min fee net | all fee net | min 1c entry | all 1c entry | all gross | block10 + | worst block10 | block20 + | worst block20 |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in block_records[:25]:
        lines.append(
            f"| `{row['model']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{base.pct(row['min_split_coverage'])} | "
            f"{base.dollars(row['min_split_net_after_fees_dollars'])} | "
            f"{base.dollars(row['all_net_after_fees_dollars'])} | "
            f"{base.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{base.dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{base.dollars(row['all_pnl_dollars'])} | "
            f"{row['block10']['positive_blocks']}/10 | {base.dollars(row['block10']['worst'])} | "
            f"{row['block20']['positive_blocks']}/20 | {base.dollars(row['block20']['worst'])} |"
        )
    lines += ["", "## Read", ""]
    if one_cent_stable.empty:
        best = eligible.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            "- No refined row remains positive in all splits after a 1c adverse entry-fill haircut. "
            f"Closest row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min 1c-entry split {base.dollars(best['min_split_net_after_fees_1c_entry_dollars'])}."
        )
    else:
        best = one_cent_stable.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best 1c-entry robust row is `{best['model']}` / `{best['entry_policy']}` / "
            f"`{best['exit_policy']}` with min 1c-entry split "
            f"{base.dollars(best['min_split_net_after_fees_1c_entry_dollars'])}."
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "debug": debug,
                    "summary_rows": int(len(summary)),
                    "fee_positive_rows": int(len(net_stable)),
                    "one_cent_entry_positive_rows": int(len(one_cent_stable)),
                    "selected": block_records,
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    summary, debug = build_summary()
    summary.to_csv(SUMMARY_CSV, index=False)
    selected = selected_rows(summary)
    block_records = attach_blocks(selected)
    write_report(summary, selected, block_records, debug)
    print("v38 fee refined exit frontier complete")
    print(f"summary_rows={len(summary)} selected_rows={len(selected)} report={REPORT_MD}")
    eligible = summary[summary["eligible_80"]].copy() if not summary.empty else summary
    one_cent = eligible[eligible["all_splits_1c_entry_positive"]].copy() if not eligible.empty else eligible
    print(f"one_cent_entry_positive_rows={len(one_cent)}")
    if not eligible.empty:
        best = eligible.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        print(
            "best_1c_frontier "
            f"model={best['model']} entry={best['entry_policy']} exit={best['exit_policy']} "
            f"min_1c={best['min_split_net_after_fees_1c_entry_dollars']:.2f} "
            f"all_1c={best['all_net_after_fees_1c_entry_dollars']:.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
