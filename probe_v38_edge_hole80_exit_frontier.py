"""80%-coverage v38 edge-hole entry/exit frontier.

Research-only. Sweeps the v38 edge-hole family under an explicit 80% minimum
coverage constraint, looking for a candidate that keeps fee+1c P&L positive by
split and by UTC day. No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v39_entry_exit_strategy_projection as base
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v38_edge_hole80_exit_frontier_latest.md"
REPORT_JSON = OUT_DIR / "v38_edge_hole80_exit_frontier_latest.json"
SUMMARY_CSV = OUT_DIR / "v38_edge_hole80_exit_frontier_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v38_edge_hole80_exit_frontier_selected_trades_latest.csv"

MODEL = "v38_long60_antipersist"
MIN_SPLIT_COVERAGE = 0.80

EDGE_FLOORS = [-2.0, 0.0]
P_SIDE_FLOORS = [0.64, 0.65, 0.66]
MAX_STC = [570.0, 600.0]
MIN_STC = [0.0, 60.0, 120.0]
VETO_RANGES = [
    ("block_first_edge_8_20", 8.0, 20.0),
    ("block_first_edge_10_18", 10.0, 18.0),
    ("block_first_edge_10_20", 10.0, 20.0),
    ("block_first_edge_10_22", 10.0, 22.0),
    ("block_first_edge_10_25", 10.0, 25.0),
    ("block_first_edge_12_20", 12.0, 20.0),
]


@dataclass(frozen=True)
class VetoPolicy:
    name: str
    low: float
    high: float


def exit_policies() -> list[base.ExitPolicy]:
    policies = [base.ExitPolicy("hold")]
    policies.extend(
        base.ExitPolicy(f"prob{int(round(floor * 100)):02d}", probability_floor=float(floor))
        for floor in np.arange(0.49, 0.541, 0.01)
    )
    for take in [8.0, 10.0, 12.0]:
        policies.append(base.ExitPolicy(f"take{int(take)}_or_prob52", take_profit_cents=take, probability_floor=0.52))
    return policies


def choose_entries_with_veto(best_opp: pd.DataFrame, entry: base.EntryPolicy, veto: VetoPolicy) -> pd.DataFrame:
    eligible = best_opp[
        best_opp["entry_edge_cents"].ge(entry.edge_floor_cents)
        & best_opp["ask_cents"].le(entry.ask_cap_cents)
        & best_opp["p_side"].ge(entry.min_p_side)
        & best_opp["seconds_to_close"].le(entry.max_seconds_to_close)
        & best_opp["seconds_to_close"].ge(entry.min_seconds_to_close)
    ].copy()
    if eligible.empty:
        return eligible
    first = eligible.sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first").reset_index(drop=True)
    in_hole = first["entry_edge_cents"].gt(veto.low) & first["entry_edge_cents"].le(veto.high)
    return first[~in_hole].reset_index(drop=True)


def block_metrics(trades: pd.DataFrame, blocks: int) -> dict[str, Any]:
    if trades.empty:
        return {"blocks": blocks, "positive_blocks": 0, "worst_cents": None, "values_cents": []}
    ordered = trades.sort_values(["entry_dt", "market"]).reset_index(drop=True)
    chunks = np.array_split(np.arange(len(ordered)), blocks)
    values = [
        float((ordered.iloc[idx]["pnl_cents"] - ordered.iloc[idx]["total_fee_cents"] - base.QTY).sum())
        for idx in chunks
        if len(idx)
    ]
    return {
        "blocks": blocks,
        "positive_blocks": int(sum(v > 0 for v in values)),
        "worst_cents": float(min(values)) if values else None,
        "values_cents": values,
    }


def day_metrics(trades: pd.DataFrame) -> dict[str, Any]:
    if trades.empty:
        return {"positive_days": 0, "total_days": 0, "worst_day_cents": None, "by_day": []}
    rows = trades.copy()
    rows["entry_day_utc"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce").dt.strftime("%Y-%m-%d")
    rows["fee_net_1c_entry_cents"] = rows["pnl_cents"] - rows["total_fee_cents"] - base.QTY
    by_day = (
        rows.groupby("entry_day_utc", as_index=False)
        .agg(
            trades=("market", "count"),
            fee_net_1c_entry_cents=("fee_net_1c_entry_cents", "sum"),
            fee_net_cents=("pnl_cents", lambda s: 0.0),
        )
        .sort_values("entry_day_utc")
    )
    # Keep the aggregate explicit; the lambda placeholder above avoids repeated
    # fee columns in groupby syntax across pandas versions.
    fee_by_day = rows.groupby("entry_day_utc")["pnl_cents"].sum() - rows.groupby("entry_day_utc")["total_fee_cents"].sum()
    by_day["fee_net_cents"] = by_day["entry_day_utc"].map(fee_by_day.to_dict()).astype(float)
    values = by_day["fee_net_1c_entry_cents"].to_numpy(dtype=float)
    return {
        "positive_days": int((values > 0).sum()),
        "total_days": int(len(values)),
        "worst_day_cents": float(values.min()) if len(values) else None,
        "by_day": by_day.to_dict("records"),
    }


def row_1c_positive(record: dict[str, Any]) -> bool:
    return all(float(record[f"{split}_net_after_fees_1c_entry_dollars"]) > 0.0 for split in ["train", "validation", "holdout"])


def build() -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, Any]]]:
    old_min = base.MIN_SPLIT_COVERAGE
    base.MIN_SPLIT_COVERAGE = MIN_SPLIT_COVERAGE
    try:
        rows = base.load_rows()
        universes = base.market_universes(rows)
        frame = base.model_frame(rows, MODEL)
        best_opp = base.best_side_per_opportunity(frame)
        paths = base.quote_paths(frame)
        records: list[dict[str, Any]] = []
        selected_trade_frames: list[pd.DataFrame] = []
        entry_policies = [
            base.EntryPolicy(edge, 100.0, pside, max_stc, min_stc)
            for edge in EDGE_FLOORS
            for pside in P_SIDE_FLOORS
            for max_stc in MAX_STC
            for min_stc in MIN_STC
            if min_stc < max_stc
        ]
        veto_policies = [VetoPolicy(name, low, high) for name, low, high in VETO_RANGES]
        exits = exit_policies()

        for entry_policy in entry_policies:
            for veto in veto_policies:
                entries = choose_entries_with_veto(best_opp, entry_policy, veto)
                if entries.empty:
                    continue
                min_coverage = min(
                    len(set(entries["market"].astype(str)) & universes[split]) / len(universes[split])
                    for split in ["train", "validation", "holdout"]
                )
                if min_coverage < MIN_SPLIT_COVERAGE:
                    continue
                for exit_policy in exits:
                    trades = base.simulate(entries, paths, exit_policy)
                    if trades.empty:
                        continue
                    record = base.flatten_metrics(MODEL, entry_policy, exit_policy, trades, universes)
                    record["veto_policy"] = veto.name
                    record["veto_low"] = veto.low
                    record["veto_high"] = veto.high
                    record["min_split_net_after_fees_1c_entry_dollars"] = float(
                        min(record[f"{split}_net_after_fees_1c_entry_dollars"] for split in ["train", "validation", "holdout"])
                    )
                    record["all_splits_1c_entry_positive"] = row_1c_positive(record)
                    days = day_metrics(trades)
                    record["positive_1c_days"] = days["positive_days"]
                    record["total_days"] = days["total_days"]
                    record["worst_1c_day_cents"] = days["worst_day_cents"]
                    block10 = block_metrics(trades, 10)
                    block20 = block_metrics(trades, 20)
                    record["block10_positive"] = block10["positive_blocks"]
                    record["block10_worst_cents"] = block10["worst_cents"]
                    record["block20_positive"] = block20["positive_blocks"]
                    record["block20_worst_cents"] = block20["worst_cents"]
                    records.append(record)

        summary = pd.DataFrame(records)
        if summary.empty:
            return summary, pd.DataFrame(), []
        selected = selected_rows(summary)
        for _, row in selected.head(10).iterrows():
            entry_policy = base.EntryPolicy(
                float(row["entry_edge_floor_cents"]),
                float(row["entry_ask_cap_cents"]),
                float(row["entry_min_p_side"]),
                float(row["entry_max_seconds_to_close"]),
                float(row["entry_min_seconds_to_close"]),
            )
            veto = VetoPolicy(str(row["veto_policy"]), float(row["veto_low"]), float(row["veto_high"]))
            exit_policy = exit_policy_from_row(row)
            entries = choose_entries_with_veto(best_opp, entry_policy, veto)
            trades = base.simulate(entries, paths, exit_policy)
            trades["frontier_row"] = f"{row['veto_policy']}|{row['entry_policy']}|{row['exit_policy']}"
            selected_trade_frames.append(trades)
        selected_trades = pd.concat(selected_trade_frames, ignore_index=True, sort=False) if selected_trade_frames else pd.DataFrame()
        return summary, selected_trades, selected.to_dict("records")
    finally:
        base.MIN_SPLIT_COVERAGE = old_min


def exit_policy_from_row(row: pd.Series) -> base.ExitPolicy:
    name = str(row["exit_policy"])
    if name == "hold":
        return base.ExitPolicy("hold")
    take = None
    prob = None
    if name.startswith("prob"):
        prob = float(name.replace("prob", "")) / 100.0
    elif name.startswith("take"):
        parts = name.split("_or_")
        take = float(parts[0].replace("take", ""))
        if len(parts) > 1 and parts[1].startswith("prob"):
            prob = float(parts[1].replace("prob", "")) / 100.0
    return base.ExitPolicy(name, take_profit_cents=take, probability_floor=prob)


def selected_rows(summary: pd.DataFrame) -> pd.DataFrame:
    eligible = summary[summary["min_split_coverage"].ge(MIN_SPLIT_COVERAGE)].copy()
    if eligible.empty:
        return eligible
    robust = eligible[
        eligible["all_splits_1c_entry_positive"]
        & eligible["positive_1c_days"].eq(eligible["total_days"])
    ].copy()
    pieces: list[pd.DataFrame] = []
    if not robust.empty:
        pieces.append(
            robust.sort_values(
                [
                    "min_split_net_after_fees_1c_entry_dollars",
                    "worst_1c_day_cents",
                    "all_net_after_fees_1c_entry_dollars",
                ],
                ascending=[False, False, False],
            ).head(25)
        )
    one_cent = eligible[eligible["all_splits_1c_entry_positive"]].copy()
    if not one_cent.empty:
        pieces.append(
            one_cent.sort_values(
                [
                    "positive_1c_days",
                    "min_split_net_after_fees_1c_entry_dollars",
                    "all_net_after_fees_1c_entry_dollars",
                ],
                ascending=[False, False, False],
            ).head(25)
        )
    pieces.append(
        eligible.sort_values(
            [
                "positive_1c_days",
                "min_split_net_after_fees_1c_entry_dollars",
                "all_net_after_fees_1c_entry_dollars",
            ],
            ascending=[False, False, False],
        ).head(25)
    )
    return pd.concat(pieces, ignore_index=True, sort=False).drop_duplicates(
        ["veto_policy", "entry_policy", "exit_policy"]
    )


def dollars(value: Any) -> str:
    try:
        return f"${float(value):.2f}"
    except (TypeError, ValueError):
        return "NA"


def dollars_cents(value: Any) -> str:
    try:
        return f"${float(value) / 100.0:.2f}"
    except (TypeError, ValueError):
        return "NA"


def write_report(summary: pd.DataFrame, selected_records: list[dict[str, Any]], selected_trades: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    eligible = summary[summary["min_split_coverage"].ge(MIN_SPLIT_COVERAGE)].copy() if not summary.empty else summary
    one_cent = eligible[eligible["all_splits_1c_entry_positive"]].copy() if not eligible.empty else eligible
    robust = one_cent[one_cent["positive_1c_days"].eq(one_cent["total_days"])].copy() if not one_cent.empty else one_cent
    lines = [
        "# v38 Edge-Hole 80% Exit Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only v38 FV entry/exit sweep.",
        "- Requires at least 80% coverage in train, validation, and holdout.",
        "- Uses fees plus a 1c adverse entry-fill haircut for split/day robustness.",
        "",
        "## Search Result",
        "",
        f"- Rows evaluated after 80% coverage prefilter: {len(summary)}",
        f"- Fee+1c positive in train/validation/holdout: {len(one_cent)}",
        f"- Fee+1c positive in all splits and all UTC days: {len(robust)}",
        "",
        "## Selected Rows",
        "",
        "| veto | entry | exit | min cov | min 1c | all 1c | days | worst day | block10 | worst block10 | trades |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in selected_records[:30]:
        lines.append(
            f"| `{row['veto_policy']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{base.pct(row['min_split_coverage'])} | "
            f"{dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{dollars_cents(row['worst_1c_day_cents'])} | "
            f"{int(row['block10_positive'])}/10 | {dollars_cents(row['block10_worst_cents'])} | "
            f"{int(row['all_trades'])} |"
        )
    lines += ["", "## Read", ""]
    if robust.empty:
        lines.append("- No 80%-coverage row is positive across all splits and all UTC days after fees plus 1c entry haircut.")
    else:
        best = robust.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "worst_1c_day_cents", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False, False],
        ).iloc[0]
        lines.append(
            f"- Best all-day 80% row is `{best['veto_policy']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min split 1c P&L {dollars(best['min_split_net_after_fees_1c_entry_dollars'])} "
            f"and all 1c P&L {dollars(best['all_net_after_fees_1c_entry_dollars'])}."
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "min_split_coverage": MIN_SPLIT_COVERAGE,
                    "summary_rows": int(len(summary)),
                    "one_cent_positive_rows": int(len(one_cent)),
                    "all_day_robust_rows": int(len(robust)),
                    "selected": selected_records,
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    selected_trades.to_csv(TRADES_CSV, index=False)


def main() -> int:
    summary, selected_trades, selected_records = build()
    summary.to_csv(SUMMARY_CSV, index=False)
    write_report(summary, selected_records, selected_trades)
    robust = summary[
        summary["all_splits_1c_entry_positive"] & summary["positive_1c_days"].eq(summary["total_days"])
    ] if not summary.empty else summary
    print("v38 edge-hole 80% exit frontier complete")
    print(f"summary_rows={len(summary)} robust_rows={len(robust)} report={REPORT_MD}")
    if selected_records:
        best = selected_records[0]
        print(
            f"best={best['veto_policy']} {best['entry_policy']} {best['exit_policy']} "
            f"min_1c={float(best['min_split_net_after_fees_1c_entry_dollars']):.2f} "
            f"all_1c={float(best['all_net_after_fees_1c_entry_dollars']):.2f} "
            f"days={int(best['positive_1c_days'])}/{int(best['total_days'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
