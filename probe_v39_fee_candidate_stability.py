"""Focused stability audit for fee-aware FV entry/exit candidates.

Research-only. This does not modify live bot code, processes, or orders.
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
REPORT_MD = OUT_DIR / "v39_fee_candidate_stability_latest.md"
REPORT_JSON = OUT_DIR / "v39_fee_candidate_stability_latest.json"
TRADES_CSV = OUT_DIR / "v39_fee_candidate_stability_trades_latest.csv"


@dataclass(frozen=True)
class Candidate:
    name: str
    model: str
    entry: base.EntryPolicy
    exit: base.ExitPolicy


CANDIDATES = [
    Candidate(
        "best_min_fee_v38_p65_prob50",
        "v38_long60_antipersist",
        base.EntryPolicy(-2.0, 100.0, 0.65, 600.0, 0.0),
        base.ExitPolicy("prob50", probability_floor=0.50),
    ),
    Candidate(
        "v38_p65_edge0_prob50",
        "v38_long60_antipersist",
        base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 0.0),
        base.ExitPolicy("prob50", probability_floor=0.50),
    ),
    Candidate(
        "v38_p65_edge0_prob45",
        "v38_long60_antipersist",
        base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 0.0),
        base.ExitPolicy("prob45", probability_floor=0.45),
    ),
    Candidate(
        "best_v39_fee_v39_p62_prob50",
        "v39_midband_v28_fallback",
        base.EntryPolicy(-2.0, 100.0, 0.62, 600.0, 0.0),
        base.ExitPolicy("prob50", probability_floor=0.50),
    ),
    Candidate(
        "best_allnet_v28_p62_hold",
        "v28_live_surface",
        base.EntryPolicy(0.0, 100.0, 0.62, 900.0, 0.0),
        base.ExitPolicy("hold"),
    ),
]


def simulate_candidate(candidate: Candidate, rows: pd.DataFrame) -> pd.DataFrame:
    frame = base.model_frame(rows, candidate.model)
    best_opp = base.best_side_per_opportunity(frame)
    paths = base.quote_paths(frame)
    entries = base.choose_entries(best_opp, candidate.entry)
    trades = base.simulate(entries, paths, candidate.exit)
    if trades.empty:
        return trades
    trades["candidate"] = candidate.name
    trades["entry_policy"] = candidate.entry.name
    trades["exit_policy"] = candidate.exit.name
    trades["fee_adjusted_pnl_cents"] = trades["pnl_cents"] - trades["total_fee_cents"]
    trades["fee_adjusted_1c_entry_pnl_cents"] = trades["fee_adjusted_pnl_cents"] - base.QTY
    trades["fee_adjusted_1c_roundtrip_pnl_cents"] = trades["fee_adjusted_1c_entry_pnl_cents"] - np.where(
        trades["settled"], 0.0, base.QTY
    )
    return trades


def summarize_trades(trades: pd.DataFrame, universe_count: int) -> dict[str, Any]:
    if trades.empty:
        return {
            "trades": 0,
            "coverage": 0.0,
            "gross_pnl_dollars": 0.0,
            "fee_net_dollars": 0.0,
            "fee_net_1c_entry_dollars": 0.0,
            "fee_net_1c_roundtrip_dollars": 0.0,
            "cost_dollars": 0.0,
            "fee_net_roi": None,
        }
    gross = float(trades["pnl_cents"].sum() / 100.0)
    fee_net = float(trades["fee_adjusted_pnl_cents"].sum() / 100.0)
    fee_net_1c_entry = float(trades["fee_adjusted_1c_entry_pnl_cents"].sum() / 100.0)
    fee_net_1c_roundtrip = float(trades["fee_adjusted_1c_roundtrip_pnl_cents"].sum() / 100.0)
    cost = float(trades["cost_cents"].sum() / 100.0)
    return {
        "trades": int(len(trades)),
        "coverage": float(len(trades) / universe_count) if universe_count else 0.0,
        "gross_pnl_dollars": gross,
        "fee_net_dollars": fee_net,
        "fee_net_1c_entry_dollars": fee_net_1c_entry,
        "fee_net_1c_roundtrip_dollars": fee_net_1c_roundtrip,
        "cost_dollars": cost,
        "fee_net_roi": float(fee_net / cost) if cost > 0 else None,
        "exits": int((~trades["settled"]).sum()),
        "settles": int(trades["settled"].sum()),
    }


def block_summary(trades: pd.DataFrame, blocks: int) -> dict[str, Any]:
    if trades.empty:
        return {"blocks": blocks, "positive_fee_blocks": 0, "worst_fee_block_dollars": None, "mean_fee_block_dollars": None}
    ordered = trades.sort_values(["entry_dt", "market"]).reset_index(drop=True)
    chunks = np.array_split(ordered, blocks)
    values = [float(chunk["fee_adjusted_pnl_cents"].sum() / 100.0) for chunk in chunks if not chunk.empty]
    return {
        "blocks": blocks,
        "positive_fee_blocks": int(sum(v > 0 for v in values)),
        "worst_fee_block_dollars": float(min(values)) if values else None,
        "mean_fee_block_dollars": float(np.mean(values)) if values else None,
        "values": values,
    }


def build() -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    rows = base.load_rows()
    universes = base.market_universes(rows)
    trade_frames: list[pd.DataFrame] = []
    records: list[dict[str, Any]] = []
    for candidate in CANDIDATES:
        trades = simulate_candidate(candidate, rows)
        trade_frames.append(trades)
        record: dict[str, Any] = {
            "candidate": candidate.name,
            "model": candidate.model,
            "entry_policy": candidate.entry.name,
            "exit_policy": candidate.exit.name,
        }
        for split in ["train", "validation", "holdout", "all"]:
            universe = universes[split]
            part = trades[trades["market"].astype(str).isin(universe)].copy()
            metrics = summarize_trades(part, len(universe))
            for key, value in metrics.items():
                record[f"{split}_{key}"] = value
        record["min_split_fee_net_dollars"] = float(
            min(record[f"{split}_fee_net_dollars"] for split in ["train", "validation", "holdout"])
        )
        record["min_split_fee_net_1c_entry_dollars"] = float(
            min(record[f"{split}_fee_net_1c_entry_dollars"] for split in ["train", "validation", "holdout"])
        )
        record["block10"] = block_summary(trades, 10)
        record["block20"] = block_summary(trades, 20)
        records.append(record)
    all_trades = pd.concat(trade_frames, ignore_index=True, sort=False) if trade_frames else pd.DataFrame()
    return all_trades, records


def write_report(trades: pd.DataFrame, records: list[dict[str, Any]]) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    lines = [
        "# v39 Fee Candidate Stability",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Focused audit of top fee-aware 75% coverage candidates.",
        "- Uses observed ask/bid replay, quantity 2, local taker-fee estimate.",
        "- Reports chronological block stability over candidate trades.",
        "",
        "## Candidates",
        "",
        "| candidate | model | entry | exit | min fee net | all fee net | 1c entry min | all gross | coverage | block10 + | worst block10 | block20 + | worst block20 |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for record in records:
        lines.append(
            f"| `{record['candidate']}` | `{record['model']}` | `{record['entry_policy']}` | "
            f"`{record['exit_policy']}` | {base.dollars(record['min_split_fee_net_dollars'])} | "
            f"{base.dollars(record['all_fee_net_dollars'])} | "
            f"{base.dollars(record['min_split_fee_net_1c_entry_dollars'])} | "
            f"{base.dollars(record['all_gross_pnl_dollars'])} | {base.pct(record['all_coverage'])} | "
            f"{record['block10']['positive_fee_blocks']}/10 | "
            f"{base.dollars(record['block10']['worst_fee_block_dollars'])} | "
            f"{record['block20']['positive_fee_blocks']}/20 | "
            f"{base.dollars(record['block20']['worst_fee_block_dollars'])} |"
        )
    best = sorted(records, key=lambda row: (row["min_split_fee_net_dollars"], row["all_fee_net_dollars"]), reverse=True)[0]
    lines += [
        "",
        "## Read",
        "",
        f"- Best split-balanced fee candidate is `{best['candidate']}` with min split fee net "
        f"{base.dollars(best['min_split_fee_net_dollars'])} and all fee net {base.dollars(best['all_fee_net_dollars'])}.",
        f"- Its 1c-entry-haircut min split value is {base.dollars(best['min_split_fee_net_1c_entry_dollars'])}, "
        f"so the edge is fee-positive but execution-fragile.",
        "- Treat this as a forward-shadow candidate, not a live-bot patch.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(clean_json({"generated_utc": generated, "records": records}), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    trades.to_csv(TRADES_CSV, index=False)


def main() -> int:
    trades, records = build()
    write_report(trades, records)
    print("v39 fee candidate stability complete")
    print(f"records={len(records)} trades={len(trades)} report={REPORT_MD}")
    best = sorted(records, key=lambda row: (row["min_split_fee_net_dollars"], row["all_fee_net_dollars"]), reverse=True)[0]
    print(
        "best "
        f"candidate={best['candidate']} min_fee_net={best['min_split_fee_net_dollars']:.2f} "
        f"all_fee_net={best['all_fee_net_dollars']:.2f} "
        f"block10={best['block10']['positive_fee_blocks']}/10 "
        f"block20={best['block20']['positive_fee_blocks']}/20"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
