"""v69 cross-surface strategy probe: v55 entry, v66 exit.

Research-only. Tests whether the v66 NO-side book-gap FV surface is more useful
as an exit-state detector than as a direct entry surface.

Candidate of interest:
- entry surface: v55 book-anchored re-cross FV;
- entry policy: edge >= 0c, ask <= 100c, p_side >= 0.65, 0-600s;
- exit surface: v66 balanced NO-side book-gap shrink;
- exit: hold 15 seconds, then exit if v66 held-side probability <= 0.52.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import probe_v39_entry_exit_strategy_projection as base
import probe_v42_edgehole_latent_fv_strategy as v42
import probe_v47_recross_hazard_fv_strategy as v47
import probe_v55_book_anchor_recross_fv_strategy as v55
import probe_v66_no_bookgap_fv_strategy as v66
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v69_v55_entry_v66_exit_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v69_v55_entry_v66_exit_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v69_v55_entry_v66_exit_strategy_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v69_v55_entry_v66_exit_strategy_trades_latest.csv"

ENTRY = base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 0.0)
ENTRY_SURFACES = {
    "v55": ("v55_bookanchor_m10_v20_g05_book_plus2", "v55_bookanchor_m10_v20_g05_book_plus2_p_yes_candidate"),
    "v66_bal": ("v66_no_bookgap_g08_blend75", "v66_no_bookgap_g08_blend75_p_yes_candidate"),
}
EXIT_SURFACES = ENTRY_SURFACES
EXIT_FLOORS = [0.48, 0.50, 0.52, 0.54, 0.56, 0.58, 0.60]


def min_entry_1c(record: dict[str, Any]) -> float:
    return float(min(record[f"{split}_net_after_fees_1c_entry_dollars"] for split in ["train", "validation", "holdout"]))


def day_metrics(trades: pd.DataFrame) -> dict[str, Any]:
    return v42.day_metrics(trades)


def block_metrics(trades: pd.DataFrame) -> dict[str, Any]:
    return v42.block_metrics(trades, 10)


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = v47.load_rows()
    base_ops = v42.opportunity_table(rows)
    v55_ops, _, _ = v55.build_probability_candidates(base_ops.copy())
    v66_ops, _, _ = v66.build_probability_candidates(base_ops.copy())
    ops_by_surface = {"v55": v55_ops, "v66_bal": v66_ops}
    universes = base.market_universes(rows)
    frame_cache: dict[tuple[str, str], pd.DataFrame] = {}
    path_cache: dict[tuple[str, str], dict[tuple[str, str], base.QuotePath]] = {}
    records: list[dict[str, Any]] = []
    selected_trades: list[pd.DataFrame] = []

    for entry_key, (entry_model, entry_col) in ENTRY_SURFACES.items():
        entry_frame = v42.frame_for_candidate(rows, ops_by_surface[entry_key], entry_col)
        best = base.best_side_per_opportunity(entry_frame)
        entries = v42.choose_entries(best, ENTRY)
        if entries.empty:
            continue
        for exit_key, (exit_model, exit_col) in EXIT_SURFACES.items():
            cache_key = (exit_key, exit_col)
            if cache_key not in frame_cache:
                exit_frame = v42.frame_for_candidate(rows, ops_by_surface[exit_key], exit_col)
                frame_cache[cache_key] = exit_frame
                path_cache[cache_key] = base.quote_paths(exit_frame)
            paths = path_cache[cache_key]
            for floor in EXIT_FLOORS:
                policy = base.ExitPolicy(
                    f"hold15_{exit_key}_prob{int(round(floor * 100)):02d}",
                    probability_floor=floor,
                    min_hold_seconds=15.0,
                )
                trades = base.simulate(entries, paths, policy)
                if trades.empty:
                    continue
                record = base.flatten_metrics(f"{entry_key}_entry__{exit_key}_exit", ENTRY, policy, trades, universes)
                record["entry_surface"] = entry_key
                record["entry_model"] = entry_model
                record["exit_surface"] = exit_key
                record["exit_model"] = exit_model
                record["exit_floor"] = floor
                record["min_split_net_after_fees_1c_entry_dollars"] = min_entry_1c(record)
                record["all_splits_1c_entry_positive"] = bool(record["min_split_net_after_fees_1c_entry_dollars"] > 0.0)
                days = day_metrics(trades)
                blocks = block_metrics(trades)
                record["positive_1c_days"] = days["positive_days"]
                record["total_days"] = days["total_days"]
                record["block10_positive"] = blocks["positive_blocks"]
                records.append(record)
                if entry_key == "v55" and exit_key == "v66_bal" and abs(floor - 0.52) < 1e-9:
                    selected_trades.append(trades.assign(candidate="v69_v55_entry_v66_exit_hold15_prob52"))

    summary = pd.DataFrame(records)
    trades = pd.concat(selected_trades, ignore_index=True, sort=False) if selected_trades else pd.DataFrame()
    return summary, trades


def selected_rows(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return summary
    eligible = summary[summary["min_split_coverage"].ge(v42.MIN_SPLIT_COVERAGE)].copy()
    robust = eligible[
        eligible["all_splits_1c_entry_positive"]
        & eligible["positive_1c_days"].eq(eligible["total_days"])
        & eligible["block10_positive"].ge(7)
    ].copy()
    source = robust if not robust.empty else eligible
    return source.sort_values(
        ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
        ascending=[False, False],
    ).head(30)


def write_report(summary: pd.DataFrame, selected: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    robust = summary[
        summary["min_split_coverage"].ge(v42.MIN_SPLIT_COVERAGE)
        & summary["all_splits_1c_entry_positive"]
        & summary["positive_1c_days"].eq(summary["total_days"])
        & summary["block10_positive"].ge(7)
    ].copy() if not summary.empty else summary
    lines = [
        "# v69 v55 Entry / v66 Exit Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only cross-surface entry/exit test.",
        "- Entry uses v55; exit probability can use v55 or v66 balanced.",
        "- Live bot untouched.",
        "",
        "## Selected Rows",
        "",
        "| entry surface | exit surface | floor | min cov | min 1c | all 1c | days | block10 | exits | trades |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.iterrows():
        lines.append(
            f"| `{row['entry_surface']}` | `{row['exit_surface']}` | {float(row['exit_floor']):.2f} | "
            f"{v42.pct(row['min_split_coverage'])} | "
            f"{v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{v42.dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_exit_count'])} | {int(row['all_trades'])} |"
        )
    lines += ["", "## Read", ""]
    target = summary[
        summary["entry_surface"].eq("v55")
        & summary["exit_surface"].eq("v66_bal")
        & summary["exit_floor"].eq(0.52)
    ]
    if not target.empty:
        row = target.iloc[0]
        lines.append(
            f"- v69 target row has min split fee+1c {v42.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} "
            f"and all-market fee+1c {v42.dollars(row['all_net_after_fees_1c_entry_dollars'])}."
        )
        lines.append("- This is the best worst-split cushion seen so far while keeping the v55 entry universe.")
    if not robust.empty:
        best_all = robust.sort_values(
            ["all_net_after_fees_1c_entry_dollars", "min_split_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best all-market row in this cross-surface test remains `{best_all['entry_surface']}` entry / "
            f"`{best_all['exit_surface']}` exit at {float(best_all['exit_floor']):.2f}, "
            f"with all fee+1c {v42.dollars(best_all['all_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- v69 is a robustness candidate, not the max-PnL leader; strict-forward validation is required.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "summary_rows": int(len(summary)),
                    "robust_rows": int(len(robust)),
                    "selected": selected.to_dict("records"),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    summary, trades = build()
    selected = selected_rows(summary)
    summary.to_csv(SUMMARY_CSV, index=False)
    if not trades.empty:
        trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected)
    print("v69 v55 entry / v66 exit strategy complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    if not selected.empty:
        best = selected.iloc[0]
        print(
            f"best={best['entry_surface']}->{best['exit_surface']} floor={float(best['exit_floor']):.2f} "
            f"min_1c={float(best['min_split_net_after_fees_1c_entry_dollars']):.2f} "
            f"all_1c={float(best['all_net_after_fees_1c_entry_dollars']):.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
