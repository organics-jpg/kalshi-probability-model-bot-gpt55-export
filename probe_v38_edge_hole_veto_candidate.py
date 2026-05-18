"""v38 edge-hole veto candidate.

Research-only. This does not modify live bot code, processes, or orders.

Loss diagnostics on the fee-refined v38 candidate showed the 10-20c model-edge
band losing despite nominally strong FV edge. This probe tests that as a
candidate policy: skip the overconfident mid-edge band, then enter the first
later/other eligible row per market.
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
REPORT_MD = OUT_DIR / "v38_edge_hole_veto_candidate_latest.md"
REPORT_JSON = OUT_DIR / "v38_edge_hole_veto_candidate_latest.json"
TRADES_CSV = OUT_DIR / "v38_edge_hole_veto_candidate_trades_latest.csv"

MODEL = "v38_long60_antipersist"
ENTRY = base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 0.0)
EXIT = base.ExitPolicy("prob52", probability_floor=0.52)


@dataclass(frozen=True)
class Veto:
    name: str
    low: float | None
    high: float | None
    mode: str = "skip_rows"


VETOS = [
    Veto("baseline_no_veto", None, None, "none"),
    Veto("skip_rows_edge_8_18", 8.0, 18.0, "skip_rows"),
    Veto("skip_rows_edge_8_20", 8.0, 20.0, "skip_rows"),
    Veto("skip_rows_edge_10_18", 10.0, 18.0, "skip_rows"),
    Veto("skip_rows_edge_10_20", 10.0, 20.0, "skip_rows"),
    Veto("skip_rows_edge_10_22", 10.0, 22.0, "skip_rows"),
    Veto("skip_rows_edge_10_25", 10.0, 25.0, "skip_rows"),
    Veto("skip_rows_edge_12_20", 12.0, 20.0, "skip_rows"),
    Veto("block_market_first_edge_8_20", 8.0, 20.0, "block_first"),
    Veto("block_market_first_edge_10_18", 10.0, 18.0, "block_first"),
    Veto("block_market_first_edge_10_20", 10.0, 20.0, "block_first"),
    Veto("block_market_first_edge_10_22", 10.0, 22.0, "block_first"),
    Veto("block_market_first_edge_10_25", 10.0, 25.0, "block_first"),
    Veto("block_market_first_edge_12_20", 12.0, 20.0, "block_first"),
]


def choose_entries_with_veto(best_opp: pd.DataFrame, veto: Veto) -> pd.DataFrame:
    eligible = best_opp[
        best_opp["entry_edge_cents"].ge(ENTRY.edge_floor_cents)
        & best_opp["ask_cents"].le(ENTRY.ask_cap_cents)
        & best_opp["p_side"].ge(ENTRY.min_p_side)
        & best_opp["seconds_to_close"].le(ENTRY.max_seconds_to_close)
        & best_opp["seconds_to_close"].ge(ENTRY.min_seconds_to_close)
    ].copy()
    if eligible.empty:
        return eligible
    if veto.mode == "none" or veto.low is None or veto.high is None:
        return eligible.sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first").reset_index(drop=True)
    if veto.mode == "block_first":
        first = eligible.sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first").reset_index(drop=True)
        in_hole = first["entry_edge_cents"].gt(veto.low) & first["entry_edge_cents"].le(veto.high)
        return first[~in_hole].reset_index(drop=True)
    if veto.mode == "skip_rows":
        in_hole = eligible["entry_edge_cents"].gt(veto.low) & eligible["entry_edge_cents"].le(veto.high)
        eligible = eligible[~in_hole].copy()
        if eligible.empty:
            return eligible
        return eligible.sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first").reset_index(drop=True)
    raise ValueError(f"unknown veto mode: {veto.mode}")


def summarize(trades: pd.DataFrame, universes: dict[str, set[str]]) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for split, universe in universes.items():
        metrics = base.metrics_for_trades(trades, universe)
        for key, value in metrics.items():
            record[f"{split}_{key}"] = value
    record["min_split_coverage"] = float(min(record[f"{split}_coverage"] for split in ["train", "validation", "holdout"]))
    record["min_split_net_after_fees_dollars"] = float(
        min(record[f"{split}_net_after_fees_dollars"] for split in ["train", "validation", "holdout"])
    )
    record["min_split_net_after_fees_1c_entry_dollars"] = float(
        min(record[f"{split}_net_after_fees_1c_entry_dollars"] for split in ["train", "validation", "holdout"])
    )
    record["all_splits_fee_positive"] = bool(
        all(record[f"{split}_net_after_fees_dollars"] > 0 for split in ["train", "validation", "holdout"])
    )
    record["all_splits_1c_entry_positive"] = bool(
        all(record[f"{split}_net_after_fees_1c_entry_dollars"] > 0 for split in ["train", "validation", "holdout"])
    )
    return record


def block_metrics(trades: pd.DataFrame, blocks: int) -> dict[str, Any]:
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


def build() -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    rows = base.load_rows()
    universes = base.market_universes(rows)
    frame = base.model_frame(rows, MODEL)
    best_opp = base.best_side_per_opportunity(frame)
    paths = base.quote_paths(frame)
    records: list[dict[str, Any]] = []
    trade_frames: list[pd.DataFrame] = []
    for veto in VETOS:
        entries = choose_entries_with_veto(best_opp, veto)
        trades = base.simulate(entries, paths, EXIT)
        if trades.empty:
            continue
        trades["candidate"] = veto.name
        trades["entry_policy"] = ENTRY.name
        trades["exit_policy"] = EXIT.name
        trade_frames.append(trades)
        record = {
            "candidate": veto.name,
            "model": MODEL,
            "entry_policy": ENTRY.name,
            "exit_policy": EXIT.name,
            "veto_low": veto.low,
            "veto_high": veto.high,
            "veto_mode": veto.mode,
        }
        record.update(summarize(trades, universes))
        record["block10"] = block_metrics(trades, 10)
        record["block20"] = block_metrics(trades, 20)
        records.append(record)
    all_trades = pd.concat(trade_frames, ignore_index=True, sort=False) if trade_frames else pd.DataFrame()
    return all_trades, records


def write_report(trades: pd.DataFrame, records: list[dict[str, Any]]) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    selected = sorted(
        records,
        key=lambda row: (
            row["all_splits_1c_entry_positive"],
            row["min_split_net_after_fees_1c_entry_dollars"],
            row["all_net_after_fees_1c_entry_dollars"],
        ),
        reverse=True,
    )
    lines = [
        "# v38 Edge-Hole Veto Candidate",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Tests whether the v38 10-20c model-edge band is an overconfidence hole.",
        "- `skip_rows` variants skip only the bad row and may enter later; `block_market_first` variants skip the whole market if the first signal is in the edge-hole.",
        "- Uses v38 `p_side>=0.65`, `edge>=0`, `0-600s` to close, and `prob52` exit.",
        "- Research-only. No live bot logic/process/order path touched.",
        "",
        "## Rows",
        "",
        "| candidate | min cov | min fee net | all fee net | min 1c entry | all 1c entry | all gross | trades | block10 + | worst block10 | block20 + | worst block20 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in selected:
        lines.append(
            f"| `{row['candidate']}` | {base.pct(row['min_split_coverage'])} | "
            f"{base.dollars(row['min_split_net_after_fees_dollars'])} | "
            f"{base.dollars(row['all_net_after_fees_dollars'])} | "
            f"{base.dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{base.dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{base.dollars(row['all_pnl_dollars'])} | {int(row['all_trades'])} | "
            f"{row['block10']['positive_blocks']}/10 | {base.dollars(row['block10']['worst'])} | "
            f"{row['block20']['positive_blocks']}/20 | {base.dollars(row['block20']['worst'])} |"
        )
    best = selected[0]
    lines += [
        "",
        "## Read",
        "",
        f"- Best row is `{best['candidate']}` with min 1c-entry split "
        f"{base.dollars(best['min_split_net_after_fees_1c_entry_dollars'])} and all 1c-entry "
        f"{base.dollars(best['all_net_after_fees_1c_entry_dollars'])}.",
        f"- Fee-only min split is {base.dollars(best['min_split_net_after_fees_dollars'])}; all fee net is "
        f"{base.dollars(best['all_net_after_fees_dollars'])}.",
    ]
    if best["all_splits_1c_entry_positive"]:
        lines.append("- This is the first candidate in this branch to clear fees plus a 1c entry haircut across all splits.")
    else:
        lines.append(
            "- No true first-entry edge-hole veto clears fees plus a 1c entry haircut across all splits; "
            "the edge-hole remains diagnostic, not a candidate rule."
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(clean_json({"generated_utc": generated, "records": records}), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    trades.to_csv(TRADES_CSV, index=False)


def main() -> int:
    trades, records = build()
    write_report(trades, records)
    print("v38 edge-hole veto candidate complete")
    print(f"records={len(records)} trades={len(trades)} report={REPORT_MD}")
    best = sorted(
        records,
        key=lambda row: (
            row["all_splits_1c_entry_positive"],
            row["min_split_net_after_fees_1c_entry_dollars"],
            row["all_net_after_fees_1c_entry_dollars"],
        ),
        reverse=True,
    )[0]
    print(
        "best "
        f"candidate={best['candidate']} min_cov={best['min_split_coverage']:.4f} "
        f"min_1c={best['min_split_net_after_fees_1c_entry_dollars']:.2f} "
        f"all_1c={best['all_net_after_fees_1c_entry_dollars']:.2f} "
        f"block10={best['block10']['positive_blocks']}/10 "
        f"block20={best['block20']['positive_blocks']}/20"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
