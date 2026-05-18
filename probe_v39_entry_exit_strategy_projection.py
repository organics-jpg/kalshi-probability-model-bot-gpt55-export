"""Entry/exit strategy projection for FV probability surfaces.

Research-only. This probe does not modify the live bot, stop processes, or
submit orders.

Purpose:
- move beyond hold-to-settlement FV projections;
- use observed post-entry bid paths to estimate exit-aware P&L;
- keep the denominator honest by requiring broad market coverage;
- compare current live-v28 actual performance with v28/v38/v39 simulated
  entry/exit policies.

The simulation is intentionally simple and auditable:
- one position per market;
- entry uses the first heartbeat in a configured time window where model edge,
  ask cap, and model probability constraints pass;
- exit scans later same-side quotes and exits at the first trigger;
- otherwise settlement is used.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
INPUT = OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_all_heartbeats_latest.csv"
REPORT_MD = OUT_DIR / "v39_entry_exit_strategy_projection_latest.md"
REPORT_JSON = OUT_DIR / "v39_entry_exit_strategy_projection_latest.json"
SUMMARY_CSV = OUT_DIR / "v39_entry_exit_strategy_projection_summary_latest.csv"
TRADES_CSV = OUT_DIR / "v39_entry_exit_strategy_projection_trades_latest.csv"
LIVE_SUMMARY = ROOT / "stats" / "live_mushroom_v28_size2_latest_score" / "summary.json"

MODELS = [
    "v28_live_surface",
    "v38_long60_antipersist",
    "v39_midband_v28_fallback",
]
QTY = 2
MIN_SPLIT_COVERAGE = 0.80
KALSHI_TAKER_FEE_RATE = 0.07


@dataclass(frozen=True)
class EntryPolicy:
    edge_floor_cents: float
    ask_cap_cents: float
    min_p_side: float
    max_seconds_to_close: float
    min_seconds_to_close: float

    @property
    def name(self) -> str:
        return (
            f"edge{self.edge_floor_cents:g}_ask{self.ask_cap_cents:g}_"
            f"p{self.min_p_side:.2f}_stc{self.min_seconds_to_close:g}-{self.max_seconds_to_close:g}"
        )


@dataclass(frozen=True)
class ExitPolicy:
    name: str
    take_profit_cents: float | None = None
    fair_edge_ceiling_cents: float | None = None
    probability_floor: float | None = None
    stop_bid_cents: float | None = None
    min_hold_seconds: float = 0.0


@dataclass(frozen=True)
class QuotePath:
    entry_ns: np.ndarray
    entry_dt: list[pd.Timestamp]
    bid_cents: np.ndarray
    p_side: np.ndarray
    seconds_to_close: np.ndarray


ENTRY_POLICIES = [
    EntryPolicy(edge, ask, pside, max_stc, min_stc)
    for edge in [-2.0, 0.0, 1.0, 2.0, 3.0, 5.0]
    for ask in [100.0, 80.0, 70.0, 65.0]
    for pside in [0.50, 0.52, 0.55, 0.60]
    for max_stc, min_stc in [
        (900.0, 0.0),
        (780.0, 0.0),
        (660.0, 0.0),
        (600.0, 0.0),
        (540.0, 0.0),
        (600.0, 120.0),
        (450.0, 60.0),
    ]
]

EXIT_POLICIES = [
    ExitPolicy("hold"),
    ExitPolicy("take5", take_profit_cents=5.0),
    ExitPolicy("take10", take_profit_cents=10.0),
    ExitPolicy("take15", take_profit_cents=15.0),
    ExitPolicy("fair_bid_ge_fair", fair_edge_ceiling_cents=0.0),
    ExitPolicy("fair_bid_within2", fair_edge_ceiling_cents=2.0),
    ExitPolicy("take10_or_fair0", take_profit_cents=10.0, fair_edge_ceiling_cents=0.0),
    ExitPolicy("take10_or_prob50", take_profit_cents=10.0, probability_floor=0.50),
    ExitPolicy("prob50", probability_floor=0.50),
    ExitPolicy("prob45", probability_floor=0.45),
    ExitPolicy("stop35_or_take10", take_profit_cents=10.0, stop_bid_cents=35.0),
]


def pct(value: Any) -> str:
    if value is None:
        return "NA"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"{100.0 * number:.2f}%"


def dollars(value: Any) -> str:
    if value is None:
        return "NA"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"${number:.2f}"


def estimate_kalshi_fee_cents(price_cents: Any, contracts: int = QTY) -> float:
    try:
        price = float(price_cents)
        qty = int(round(float(contracts)))
    except (TypeError, ValueError):
        return 0.0
    if qty <= 0 or price <= 0.0 or price >= 100.0:
        return 0.0
    probability = price / 100.0
    raw_fee_dollars = KALSHI_TAKER_FEE_RATE * qty * probability * (1.0 - probability)
    return float(np.ceil(raw_fee_dollars * 100.0))


def load_rows() -> pd.DataFrame:
    usecols = {
        "opportunity_key",
        "entry_dt",
        "market",
        "side",
        "outcome",
        "win",
        "ask_cents",
        "bid_cents",
        "seconds_to_close",
        "split",
    }
    for model in MODELS:
        usecols.add(f"{model}_p_yes")
        usecols.add(f"{model}_p_side")
    rows = pd.read_csv(INPUT, usecols=lambda col: col in usecols, low_memory=False)
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    for col in ["ask_cents", "bid_cents", "seconds_to_close"]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce")
    if rows["win"].dtype == bool:
        rows["win_bool"] = rows["win"]
    else:
        rows["win_bool"] = rows["win"].astype(str).str.lower().isin({"true", "1", "yes"})
    rows = rows.dropna(subset=["entry_dt", "market", "side", "ask_cents", "seconds_to_close", "split"]).copy()
    return rows.sort_values(["market", "entry_dt", "side"]).reset_index(drop=True)


def market_universes(rows: pd.DataFrame) -> dict[str, set[str]]:
    return {
        "train": set(rows.loc[rows["split"].eq("train"), "market"].astype(str).unique()),
        "validation": set(rows.loc[rows["split"].eq("validation"), "market"].astype(str).unique()),
        "holdout": set(rows.loc[rows["split"].eq("holdout"), "market"].astype(str).unique()),
        "all": set(rows["market"].astype(str).unique()),
    }


def model_frame(rows: pd.DataFrame, model: str) -> pd.DataFrame:
    frame = rows[
        [
            "opportunity_key",
            "entry_dt",
            "market",
            "side",
            "outcome",
            "win_bool",
            "ask_cents",
            "bid_cents",
            "seconds_to_close",
            "split",
            f"{model}_p_yes",
            f"{model}_p_side",
        ]
    ].copy()
    frame["model"] = model
    frame["p_yes"] = pd.to_numeric(frame[f"{model}_p_yes"], errors="coerce")
    frame["p_side"] = pd.to_numeric(frame[f"{model}_p_side"], errors="coerce")
    frame["entry_edge_cents"] = 100.0 * frame["p_side"] - frame["ask_cents"]
    frame["fair_side_cents"] = 100.0 * frame["p_side"]
    return frame.dropna(subset=["p_yes", "p_side", "entry_edge_cents"]).copy()


def best_side_per_opportunity(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.sort_values(["opportunity_key", "entry_edge_cents"], ascending=[True, False])
        .groupby("opportunity_key", as_index=False)
        .head(1)
        .sort_values(["market", "entry_dt"])
        .reset_index(drop=True)
    )


def quote_paths(frame: pd.DataFrame) -> dict[tuple[str, str], QuotePath]:
    paths: dict[tuple[str, str], QuotePath] = {}
    for key, group in frame.sort_values(["market", "side", "entry_dt"]).groupby(["market", "side"]):
        clean = group[
            pd.to_numeric(group["bid_cents"], errors="coerce").notna()
            & group["bid_cents"].ge(1.0)
            & pd.to_numeric(group["p_side"], errors="coerce").notna()
        ].copy()
        if clean.empty:
            continue
        paths[(str(key[0]), str(key[1]))] = QuotePath(
            entry_ns=clean["entry_dt"].astype("int64").to_numpy(dtype=np.int64),
            entry_dt=list(clean["entry_dt"]),
            bid_cents=clean["bid_cents"].to_numpy(dtype=float),
            p_side=clean["p_side"].to_numpy(dtype=float),
            seconds_to_close=clean["seconds_to_close"].to_numpy(dtype=float),
        )
    return paths


def choose_entries(best_opp: pd.DataFrame, policy: EntryPolicy) -> pd.DataFrame:
    eligible = best_opp[
        best_opp["entry_edge_cents"].ge(policy.edge_floor_cents)
        & best_opp["ask_cents"].le(policy.ask_cap_cents)
        & best_opp["p_side"].ge(policy.min_p_side)
        & best_opp["seconds_to_close"].le(policy.max_seconds_to_close)
        & best_opp["seconds_to_close"].ge(policy.min_seconds_to_close)
    ].copy()
    if eligible.empty:
        return eligible
    return eligible.sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first").reset_index(drop=True)


def exit_for_entry(entry: Any, path: QuotePath, policy: ExitPolicy) -> dict[str, Any]:
    entry_dt = pd.Timestamp(entry.entry_dt)
    entry_ask = float(entry.ask_cents)
    entry_ns = entry_dt.value
    if policy.min_hold_seconds > 0:
        min_exit_ns = entry_ns + int(policy.min_hold_seconds * 1_000_000_000)
        start_idx = int(np.searchsorted(path.entry_ns, min_exit_ns, side="left"))
    else:
        start_idx = int(np.searchsorted(path.entry_ns, entry_ns, side="right"))

    if start_idx < len(path.entry_ns):
        bid = path.bid_cents[start_idx:]
        p_side = path.p_side[start_idx:]
        fair_edge_to_bid = 100.0 * p_side - bid
        trigger_mask = np.zeros(len(bid), dtype=bool)
        if policy.take_profit_cents is not None:
            trigger_mask |= bid >= entry_ask + policy.take_profit_cents
        if policy.fair_edge_ceiling_cents is not None:
            trigger_mask |= fair_edge_to_bid <= policy.fair_edge_ceiling_cents
        if policy.probability_floor is not None:
            trigger_mask |= p_side <= policy.probability_floor
        if policy.stop_bid_cents is not None:
            trigger_mask |= bid <= policy.stop_bid_cents

        if bool(trigger_mask.any()):
            rel_idx = int(np.flatnonzero(trigger_mask)[0])
            idx = start_idx + rel_idx
            exit_bid = float(path.bid_cents[idx])
            exit_p_side = float(path.p_side[idx])
            exit_fair_edge_to_bid = 100.0 * exit_p_side - exit_bid
            triggers: list[str] = []
            if policy.take_profit_cents is not None and exit_bid >= entry_ask + policy.take_profit_cents:
                triggers.append("take_profit")
            if policy.fair_edge_ceiling_cents is not None and exit_fair_edge_to_bid <= policy.fair_edge_ceiling_cents:
                triggers.append("fair_value_exit")
            if policy.probability_floor is not None and exit_p_side <= policy.probability_floor:
                triggers.append("probability_reduce")
            if policy.stop_bid_cents is not None and exit_bid <= policy.stop_bid_cents:
                triggers.append("stop_bid")
            pnl_cents = (exit_bid - entry_ask) * QTY
            return {
                "exit_type": "+".join(triggers),
                "exit_dt": path.entry_dt[idx],
                "exit_seconds_to_close": float(path.seconds_to_close[idx]),
                "exit_bid_cents": exit_bid,
                "exit_p_side": exit_p_side,
                "exit_fair_edge_to_bid_cents": exit_fair_edge_to_bid,
                "pnl_cents": pnl_cents,
                "settled": False,
            }

    win = bool(entry.win_bool)
    settlement_value = 100.0 if win else 0.0
    pnl_cents = (settlement_value - entry_ask) * QTY
    return {
        "exit_type": "settlement_win" if win else "settlement_loss",
        "exit_dt": pd.NaT,
        "exit_seconds_to_close": np.nan,
        "exit_bid_cents": np.nan,
        "exit_p_side": np.nan,
        "exit_fair_edge_to_bid_cents": np.nan,
        "pnl_cents": pnl_cents,
        "settled": True,
    }


def simulate(entries: pd.DataFrame, paths: dict[tuple[str, str], QuotePath], exit_policy: ExitPolicy) -> pd.DataFrame:
    trades: list[dict[str, Any]] = []
    for entry in entries.itertuples(index=False):
        path = paths.get((str(entry.market), str(entry.side)))
        if path is None:
            continue
        exit_info = exit_for_entry(entry, path, exit_policy)
        trade = {
            "model": entry.model,
            "market": entry.market,
            "split": entry.split,
            "entry_dt": entry.entry_dt,
            "side": entry.side,
            "outcome": entry.outcome,
            "win": bool(entry.win_bool),
            "entry_ask_cents": float(entry.ask_cents),
            "entry_bid_cents": float(entry.bid_cents) if pd.notna(entry.bid_cents) else np.nan,
            "entry_p_side": float(entry.p_side),
            "entry_p_yes": float(entry.p_yes),
            "entry_edge_cents": float(entry.entry_edge_cents),
            "entry_seconds_to_close": float(entry.seconds_to_close),
            **exit_info,
        }
        trade["cost_cents"] = float(entry.ask_cents) * QTY
        trade["entry_fee_cents"] = estimate_kalshi_fee_cents(entry.ask_cents)
        trade["exit_fee_cents"] = (
            estimate_kalshi_fee_cents(trade["exit_bid_cents"])
            if not bool(trade["settled"]) and pd.notna(trade["exit_bid_cents"])
            else 0.0
        )
        trade["total_fee_cents"] = trade["entry_fee_cents"] + trade["exit_fee_cents"]
        trades.append(trade)
    return pd.DataFrame(trades)


def metrics_for_trades(trades: pd.DataFrame, universe: set[str]) -> dict[str, Any]:
    part = trades[trades["market"].astype(str).isin(universe)].copy()
    markets = len(universe)
    if markets == 0 or part.empty:
        return {
            "markets": markets,
            "trades": 0,
            "coverage": 0.0,
            "pnl_dollars": 0.0,
            "cost_dollars": 0.0,
            "roi": None,
            "wins": 0,
            "losses": 0,
            "settled_count": 0,
            "exit_count": 0,
            "avg_entry_ask": None,
            "avg_entry_edge": None,
            "avg_entry_p_side": None,
            "avg_entry_seconds_to_close": None,
        }
    pnl = float(part["pnl_cents"].sum() / 100.0)
    cost = float(part["cost_cents"].sum() / 100.0)
    fee = float(part["total_fee_cents"].sum() / 100.0) if "total_fee_cents" in part.columns else 0.0
    net_after_fees = pnl - fee
    one_cent_entry_slip = float(len(part) * QTY / 100.0)
    one_cent_exit_slip = float((~part["settled"]).sum() * QTY / 100.0)
    net_after_fees_1c_entry = net_after_fees - one_cent_entry_slip
    net_after_fees_1c_roundtrip = net_after_fees - one_cent_entry_slip - one_cent_exit_slip
    return {
        "markets": markets,
        "trades": int(len(part)),
        "coverage": float(len(part) / markets),
        "pnl_dollars": pnl,
        "cost_dollars": cost,
        "roi": float(pnl / cost) if cost > 0 else None,
        "fee_dollars": fee,
        "net_after_fees_dollars": net_after_fees,
        "net_roi_after_fees": float(net_after_fees / cost) if cost > 0 else None,
        "net_after_fees_1c_entry_dollars": net_after_fees_1c_entry,
        "net_after_fees_1c_roundtrip_dollars": net_after_fees_1c_roundtrip,
        "wins": int(part["win"].sum()),
        "losses": int((~part["win"]).sum()),
        "settled_count": int(part["settled"].sum()),
        "exit_count": int((~part["settled"]).sum()),
        "avg_entry_ask": float(part["entry_ask_cents"].mean()),
        "avg_entry_edge": float(part["entry_edge_cents"].mean()),
        "avg_entry_p_side": float(part["entry_p_side"].mean()),
        "avg_entry_seconds_to_close": float(part["entry_seconds_to_close"].mean()),
    }


def flatten_metrics(
    model: str,
    entry_policy: EntryPolicy,
    exit_policy: ExitPolicy,
    trades: pd.DataFrame,
    universes: dict[str, set[str]],
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "model": model,
        "entry_policy": entry_policy.name,
        "exit_policy": exit_policy.name,
        "entry_edge_floor_cents": entry_policy.edge_floor_cents,
        "entry_ask_cap_cents": entry_policy.ask_cap_cents,
        "entry_min_p_side": entry_policy.min_p_side,
        "entry_max_seconds_to_close": entry_policy.max_seconds_to_close,
        "entry_min_seconds_to_close": entry_policy.min_seconds_to_close,
    }
    for split, universe in universes.items():
        metrics = metrics_for_trades(trades, universe)
        for key, value in metrics.items():
            record[f"{split}_{key}"] = value
    record["min_split_coverage"] = float(min(record[f"{split}_coverage"] for split in ["train", "validation", "holdout"]))
    record["min_split_pnl_dollars"] = float(min(record[f"{split}_pnl_dollars"] for split in ["train", "validation", "holdout"]))
    record["min_split_net_after_fees_dollars"] = float(
        min(record[f"{split}_net_after_fees_dollars"] for split in ["train", "validation", "holdout"])
    )
    record["min_split_net_after_fees_1c_roundtrip_dollars"] = float(
        min(record[f"{split}_net_after_fees_1c_roundtrip_dollars"] for split in ["train", "validation", "holdout"])
    )
    record["all_splits_positive"] = bool(all(record[f"{split}_pnl_dollars"] > 0 for split in ["train", "validation", "holdout"]))
    record["all_splits_net_after_fees_positive"] = bool(
        all(record[f"{split}_net_after_fees_dollars"] > 0 for split in ["train", "validation", "holdout"])
    )
    record["all_splits_net_after_fees_1c_roundtrip_positive"] = bool(
        all(record[f"{split}_net_after_fees_1c_roundtrip_dollars"] > 0 for split in ["train", "validation", "holdout"])
    )
    record["eligible_80"] = bool(record["min_split_coverage"] >= MIN_SPLIT_COVERAGE)
    return record


def load_live_summary() -> dict[str, Any]:
    if not LIVE_SUMMARY.exists():
        return {}
    try:
        return json.loads(LIVE_SUMMARY.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = load_rows()
    universes = market_universes(rows)
    records: list[dict[str, Any]] = []
    trade_frames: list[pd.DataFrame] = []

    for model in MODELS:
        frame = model_frame(rows, model)
        best_opp = best_side_per_opportunity(frame)
        paths = quote_paths(frame)
        entry_cache: dict[str, pd.DataFrame] = {}
        for entry_policy in ENTRY_POLICIES:
            entries = choose_entries(best_opp, entry_policy)
            if entries.empty:
                continue
            min_coverage = min(
                len(set(entries["market"].astype(str)) & universes[split]) / len(universes[split])
                for split in ["train", "validation", "holdout"]
            )
            if min_coverage < MIN_SPLIT_COVERAGE:
                continue
            entry_cache[entry_policy.name] = entries
            for exit_policy in EXIT_POLICIES:
                trades = simulate(entries, paths, exit_policy)
                if trades.empty:
                    continue
                trades["entry_policy"] = entry_policy.name
                trades["exit_policy"] = exit_policy.name
                records.append(flatten_metrics(model, entry_policy, exit_policy, trades, universes))
                # Keep only potentially useful detailed trades to keep artifact size modest.
                if len(trade_frames) < 60:
                    trade_frames.append(trades)
    summary = pd.DataFrame(records)
    trades = pd.concat(trade_frames, ignore_index=True, sort=False) if trade_frames else pd.DataFrame()
    return summary, trades


def selected_rows(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return summary
    eligible = summary[summary["eligible_80"]].copy()
    stable = eligible[eligible["all_splits_positive"]].copy()
    net_stable = eligible[eligible["all_splits_net_after_fees_positive"]].copy()
    selected_parts: list[pd.DataFrame] = []
    if not net_stable.empty:
        selected_parts.append(
            net_stable.sort_values(
                ["min_split_net_after_fees_dollars", "all_net_after_fees_dollars", "all_roi"],
                ascending=[False, False, False],
            ).head(15)
        )
    if not stable.empty:
        selected_parts.append(
            stable.sort_values(
                ["min_split_pnl_dollars", "all_pnl_dollars", "all_roi"],
                ascending=[False, False, False],
            ).head(15)
        )
    selected_parts.append(
        eligible.sort_values(
            ["all_pnl_dollars", "min_split_pnl_dollars", "all_roi"],
            ascending=[False, False, False],
        ).head(15)
    )
    for model in MODELS:
        part = eligible[eligible["model"].eq(model)].copy()
        if not part.empty:
            selected_parts.append(
                part.sort_values(
                    ["min_split_pnl_dollars", "all_pnl_dollars", "all_roi"],
                    ascending=[False, False, False],
                ).head(5)
            )
    return pd.concat(selected_parts, ignore_index=True, sort=False).drop_duplicates(
        ["model", "entry_policy", "exit_policy"]
    )


def write_report(summary: pd.DataFrame, selected: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    live = load_live_summary()
    lines = [
        "# v39 Entry/Exit Strategy Projection",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only entry/exit replay using observed heartbeat bid/ask paths.",
        "- One entry per market; no live bot code/process/order path is touched.",
        "- Entry candidates must keep at least 80% coverage in train, validation, and holdout before exit policies are ranked.",
        "- Gross P&L assumes fills at observed ask for entry and observed bid for exit, quantity 2.",
        "- Fee-adjusted columns use the local Kalshi taker-fee formula also used by the dashboard.",
        "",
        "## Live Reference",
        "",
    ]
    if live:
        lines += [
            f"- Entries: {live.get('entries_total')}",
            f"- Completed round trips: {live.get('completed_round_trips')}",
            f"- Open positions: {live.get('open_positions')}",
            f"- Net P&L: {dollars(live.get('net_pnl_total_dollars'))} on {dollars(live.get('gross_cost_basis_dollars'))} ({pct((live.get('net_pnl_total_percent') or 0) / 100.0)})",
            "",
        ]
    stable = summary[summary["eligible_80"] & summary["all_splits_positive"]] if not summary.empty else summary
    net_stable = summary[summary["eligible_80"] & summary["all_splits_net_after_fees_positive"]] if not summary.empty else summary
    lines += [
        "## Search Result",
        "",
        f"- Policy rows evaluated after coverage prefilter: {len(summary)}",
        f"- 80%+ rows with positive train/validation/holdout gross P&L: {len(stable)}",
        f"- 80%+ rows with positive train/validation/holdout fee-adjusted P&L: {len(net_stable)}",
        "",
        "## Selected Rows",
        "",
        "| model | entry | exit | min cov | train gross | val gross | hold gross | all gross | all fee net | min fee net | all ROI | exits/settles | avg entry stc |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.head(30).iterrows():
        exits = f"{int(row['all_exit_count'])}/{int(row['all_settled_count'])}"
        lines.append(
            f"| `{row['model']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{pct(row['min_split_coverage'])} | {dollars(row['train_pnl_dollars'])} | "
            f"{dollars(row['validation_pnl_dollars'])} | {dollars(row['holdout_pnl_dollars'])} | "
            f"{dollars(row['all_pnl_dollars'])} | {dollars(row['all_net_after_fees_dollars'])} | "
            f"{dollars(row['min_split_net_after_fees_dollars'])} | {pct(row['all_roi'])} | {exits} | "
            f"{row['all_avg_entry_seconds_to_close']:.1f}s |"
        )
    lines += [
        "",
        "## Read",
        "",
    ]
    if stable.empty:
        lines.append("- No researched entry/exit policy currently proves robust 80%+ profitability across train, validation, and holdout.")
    else:
        best = stable.sort_values(["min_split_pnl_dollars", "all_pnl_dollars"], ascending=[False, False]).iloc[0]
        lines.append(
            f"- Best robust row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min split P&L {dollars(best['min_split_pnl_dollars'])} and all P&L {dollars(best['all_pnl_dollars'])}."
        )
    if net_stable.empty:
        lines.append("- After the repo's local Kalshi taker-fee estimate, no 80%+ row remains positive across train, validation, and holdout.")
    else:
        best_net = net_stable.sort_values(
            ["min_split_net_after_fees_dollars", "all_net_after_fees_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best fee-adjusted robust row is `{best_net['model']}` / `{best_net['entry_policy']}` / "
            f"`{best_net['exit_policy']}` with min fee-adjusted split P&L "
            f"{dollars(best_net['min_split_net_after_fees_dollars'])} and all fee-adjusted P&L "
            f"{dollars(best_net['all_net_after_fees_dollars'])}."
        )
    lines.append("- This is a projection from observed quotes, not a live patch; forward shadowing is still required before promotion.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "input": str(INPUT),
                    "models": MODELS,
                    "min_split_coverage": MIN_SPLIT_COVERAGE,
                    "qty": QTY,
                    "live_summary": live,
                    "selected": selected.to_dict("records"),
                    "stable_count": int(len(stable)),
                    "fee_adjusted_stable_count": int(len(net_stable)),
                    "summary_rows": int(len(summary)),
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
    summary.to_csv(SUMMARY_CSV, index=False)
    trades.to_csv(TRADES_CSV, index=False)
    selected = selected_rows(summary)
    write_report(summary, selected)
    print("v39 entry/exit strategy projection complete")
    print(f"summary_rows={len(summary)} selected_rows={len(selected)} report={REPORT_MD}")
    stable = summary[summary["eligible_80"] & summary["all_splits_positive"]] if not summary.empty else summary
    net_stable = summary[summary["eligible_80"] & summary["all_splits_net_after_fees_positive"]] if not summary.empty else summary
    print(f"stable_80_positive_rows={len(stable)}")
    print(f"fee_adjusted_stable_80_positive_rows={len(net_stable)}")
    if not stable.empty:
        best = stable.sort_values(["min_split_pnl_dollars", "all_pnl_dollars"], ascending=[False, False]).iloc[0]
        print(
            "best_stable "
            f"model={best['model']} entry={best['entry_policy']} exit={best['exit_policy']} "
            f"min_cov={best['min_split_coverage']:.4f} all_pnl={best['all_pnl_dollars']:.2f} "
            f"min_split_pnl={best['min_split_pnl_dollars']:.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
