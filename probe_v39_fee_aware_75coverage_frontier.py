"""Fee-aware 75% coverage frontier for v28/v38/v39 FV surfaces.

Research-only. This does not modify live bot code, processes, or orders.

The 80% entry/exit replay showed many gross-positive rows, but none that were
fee-adjusted positive across train/validation/holdout. This probe asks the next
concrete question: does the edge become robust if we use the lower end of the
user's 75-80% coverage band and require stronger model-side confidence?
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import probe_v39_entry_exit_strategy_projection as base
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v39_fee_aware_75coverage_frontier_latest.md"
REPORT_JSON = OUT_DIR / "v39_fee_aware_75coverage_frontier_latest.json"
SUMMARY_CSV = OUT_DIR / "v39_fee_aware_75coverage_frontier_summary_latest.csv"
MIN_SPLIT_COVERAGE = 0.75

EDGE_FLOORS = [-2.0, 0.0, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 12.0, 15.0]
ASK_CAPS = [100.0, 85.0, 80.0, 75.0, 70.0, 65.0]
MIN_P_SIDES = [0.55, 0.58, 0.60, 0.62, 0.65, 0.68, 0.70]
TIME_WINDOWS = [
    (900.0, 0.0),
    (780.0, 0.0),
    (660.0, 0.0),
    (600.0, 0.0),
    (540.0, 0.0),
    (600.0, 120.0),
    (450.0, 60.0),
]

ENTRY_POLICIES = [
    base.EntryPolicy(edge, ask, pside, max_stc, min_stc)
    for edge in EDGE_FLOORS
    for ask in ASK_CAPS
    for pside in MIN_P_SIDES
    for max_stc, min_stc in TIME_WINDOWS
]

EXIT_POLICIES = [
    base.ExitPolicy("hold"),
    base.ExitPolicy("prob55", probability_floor=0.55),
    base.ExitPolicy("prob50", probability_floor=0.50),
    base.ExitPolicy("prob45", probability_floor=0.45),
    base.ExitPolicy("prob40", probability_floor=0.40),
    base.ExitPolicy("take10", take_profit_cents=10.0),
    base.ExitPolicy("take15", take_profit_cents=15.0),
    base.ExitPolicy("take20", take_profit_cents=20.0),
    base.ExitPolicy("take10_or_prob45", take_profit_cents=10.0, probability_floor=0.45),
    base.ExitPolicy("take15_or_prob45", take_profit_cents=15.0, probability_floor=0.45),
]


def metrics_for_policy(
    model: str,
    entry_policy: base.EntryPolicy,
    exit_policy: base.ExitPolicy,
    trades: pd.DataFrame,
    universes: dict[str, set[str]],
) -> dict[str, Any]:
    record = base.flatten_metrics(model, entry_policy, exit_policy, trades, universes)
    record["target_min_split_coverage"] = MIN_SPLIT_COVERAGE
    return record


def build() -> pd.DataFrame:
    old_min = base.MIN_SPLIT_COVERAGE
    base.MIN_SPLIT_COVERAGE = MIN_SPLIT_COVERAGE
    try:
        rows = base.load_rows()
        universes = base.market_universes(rows)
        records: list[dict[str, Any]] = []

        for model in base.MODELS:
            frame = base.model_frame(rows, model)
            best_opp = base.best_side_per_opportunity(frame)
            paths = base.quote_paths(frame)
            for entry_policy in ENTRY_POLICIES:
                entries = base.choose_entries(best_opp, entry_policy)
                if entries.empty:
                    continue
                min_coverage = min(
                    len(set(entries["market"].astype(str)) & universes[split]) / len(universes[split])
                    for split in ["train", "validation", "holdout"]
                )
                if min_coverage < MIN_SPLIT_COVERAGE:
                    continue
                for exit_policy in EXIT_POLICIES:
                    trades = base.simulate(entries, paths, exit_policy)
                    if trades.empty:
                        continue
                    records.append(metrics_for_policy(model, entry_policy, exit_policy, trades, universes))

        return pd.DataFrame(records)
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
    pieces.append(
        eligible.sort_values(
            ["min_split_net_after_fees_dollars", "all_net_after_fees_dollars"],
            ascending=[False, False],
        ).head(20)
    )
    gross_stable = eligible[eligible["all_splits_positive"]].copy()
    if not gross_stable.empty:
        pieces.append(
            gross_stable.sort_values(
                ["min_split_pnl_dollars", "all_pnl_dollars"],
                ascending=[False, False],
            ).head(20)
        )
    for model in base.MODELS:
        part = eligible[eligible["model"].eq(model)].copy()
        if not part.empty:
            pieces.append(
                part.sort_values(
                    ["min_split_net_after_fees_dollars", "all_net_after_fees_dollars"],
                    ascending=[False, False],
                ).head(5)
            )
    return pd.concat(pieces, ignore_index=True, sort=False).drop_duplicates(
        ["model", "entry_policy", "exit_policy"]
    )


def write_report(summary: pd.DataFrame, selected: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    eligible = summary[summary["eligible_80"]].copy() if not summary.empty else summary
    gross_stable = eligible[eligible["all_splits_positive"]].copy() if not eligible.empty else eligible
    net_stable = eligible[eligible["all_splits_net_after_fees_positive"]].copy() if not eligible.empty else eligible
    lines = [
        "# v39 Fee-Aware 75% Coverage Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only replay. Live bot logic, process, and order path untouched.",
        "- Minimum coverage relaxed to 75% in train, validation, and holdout.",
        "- Entry grid adds stronger model-edge and p_side requirements than the 80% gross sweep.",
        "- Fee-adjusted columns use the local Kalshi taker-fee formula also used by the dashboard.",
        "",
        "## Search Result",
        "",
        f"- Policy rows evaluated after 75% coverage prefilter: {len(summary)}",
        f"- Rows positive across train/validation/holdout gross P&L: {len(gross_stable)}",
        f"- Rows positive across train/validation/holdout fee-adjusted P&L: {len(net_stable)}",
        "",
        "## Selected Rows",
        "",
        "| model | entry | exit | min cov | train net | val net | hold net | min net | all net | all gross | all ROI gross | trades | exits/settles |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.head(35).iterrows():
        exits = f"{int(row['all_exit_count'])}/{int(row['all_settled_count'])}"
        lines.append(
            f"| `{row['model']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{base.pct(row['min_split_coverage'])} | {base.dollars(row['train_net_after_fees_dollars'])} | "
            f"{base.dollars(row['validation_net_after_fees_dollars'])} | "
            f"{base.dollars(row['holdout_net_after_fees_dollars'])} | "
            f"{base.dollars(row['min_split_net_after_fees_dollars'])} | "
            f"{base.dollars(row['all_net_after_fees_dollars'])} | "
            f"{base.dollars(row['all_pnl_dollars'])} | {base.pct(row['all_roi'])} | "
            f"{int(row['all_trades'])} | {exits} |"
        )
    lines += ["", "## Read", ""]
    if net_stable.empty:
        best = eligible.sort_values(
            ["min_split_net_after_fees_dollars", "all_net_after_fees_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            "- No 75%+ row remains fee-adjusted positive across train, validation, and holdout. "
            f"Closest row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min fee-adjusted split P&L {base.dollars(best['min_split_net_after_fees_dollars'])} "
            f"and all fee-adjusted P&L {base.dollars(best['all_net_after_fees_dollars'])}."
        )
    else:
        best = net_stable.sort_values(
            ["min_split_net_after_fees_dollars", "all_net_after_fees_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best fee-adjusted robust row is `{best['model']}` / `{best['entry_policy']}` / "
            f"`{best['exit_policy']}` with min fee-adjusted split P&L "
            f"{base.dollars(best['min_split_net_after_fees_dollars'])} and all fee-adjusted P&L "
            f"{base.dollars(best['all_net_after_fees_dollars'])}."
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "min_split_coverage": MIN_SPLIT_COVERAGE,
                    "summary_rows": int(len(summary)),
                    "gross_stable_rows": int(len(gross_stable)),
                    "fee_adjusted_stable_rows": int(len(net_stable)),
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
    summary = build()
    summary.to_csv(SUMMARY_CSV, index=False)
    selected = selected_rows(summary)
    write_report(summary, selected)
    print("v39 fee-aware 75% coverage frontier complete")
    print(f"summary_rows={len(summary)} selected_rows={len(selected)} report={REPORT_MD}")
    eligible = summary[summary["eligible_80"]].copy() if not summary.empty else summary
    net_stable = eligible[eligible["all_splits_net_after_fees_positive"]].copy() if not eligible.empty else eligible
    print(f"fee_adjusted_stable_75_positive_rows={len(net_stable)}")
    if not eligible.empty:
        best = eligible.sort_values(
            ["min_split_net_after_fees_dollars", "all_net_after_fees_dollars"],
            ascending=[False, False],
        ).iloc[0]
        print(
            "best_fee_frontier "
            f"model={best['model']} entry={best['entry_policy']} exit={best['exit_policy']} "
            f"min_cov={best['min_split_coverage']:.4f} "
            f"all_net={best['all_net_after_fees_dollars']:.2f} "
            f"min_split_net={best['min_split_net_after_fees_dollars']:.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
