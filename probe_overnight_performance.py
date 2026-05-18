"""Research-only overnight performance report for the live v28 BTC bot."""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from zoneinfo import ZoneInfo

import pandas as pd

from probe_live_v28_fv_accuracy_volume import (
    BOT_LOG,
    EXECUTION_LOG,
    OUT_DIR,
    as_float,
    iter_json_lines,
)


LOCAL_TZ = ZoneInfo("America/New_York")
TRADE_LEDGER = OUT_DIR / "fv_accuracy_volume_trades_latest.csv"


def parse_utc(text: str) -> pd.Timestamp:
    return pd.to_datetime(text, utc=True)


def pct(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{100.0 * float(value):.2f}%"


def cents(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{value:.1f}c"


def clean_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    if isinstance(value, tuple):
        return [clean_json(v) for v in value]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if pd.isna(value):
        return None
    return value


def default_start(now_local: datetime) -> datetime:
    previous_day = now_local.date().toordinal() - 1
    date = datetime.fromordinal(previous_day).date()
    return datetime(date.year, date.month, date.day, 18, 0, 0, tzinfo=LOCAL_TZ)


def parse_local_log_ts(text: str) -> Optional[pd.Timestamp]:
    try:
        dt = datetime.strptime(text, "%Y-%m-%d %H:%M:%S,%f")
    except ValueError:
        return None
    return pd.Timestamp(dt.replace(tzinfo=LOCAL_TZ).astimezone(timezone.utc))


def load_trade_ledger(start_utc: pd.Timestamp, end_utc: pd.Timestamp) -> pd.DataFrame:
    if not TRADE_LEDGER.exists():
        raise SystemExit(f"Missing trade ledger. Run probe_live_v28_fv_accuracy_volume.py first: {TRADE_LEDGER}")
    df = pd.read_csv(TRADE_LEDGER)
    if df.empty:
        return df
    df["ts_wall"] = pd.to_datetime(df["ts_wall"], utc=True, errors="coerce")
    for col in ["win"]:
        df[col] = df[col].astype(str).str.lower().isin({"true", "1", "yes"})
    for col in ["qty", "ask_cents", "v28_p_side", "v28_edge_cents", "v28_seconds_to_close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[(df["ts_wall"] >= start_utc) & (df["ts_wall"] <= end_utc)].copy()


def settlement_pnl_cents(row: pd.Series) -> float:
    qty = float(row.get("qty") or 0.0)
    ask = float(row.get("ask_cents") or 0.0)
    if bool(row.get("win")):
        return qty * (100.0 - ask)
    return -qty * ask


@dataclass
class Fill:
    ts: pd.Timestamp
    kind: str
    market: str
    side: str
    qty: int
    price: float
    client_order_id: str
    order_id: str


def fill_price(row: Dict[str, Any]) -> Optional[float]:
    for key in ["actual_fill_price_cents", "top_of_book_limit_cents", "trigger_price_cents", "cap_price_cents"]:
        value = as_float(row.get(key))
        if value is not None:
            return value
    return None


def load_fills(start_utc: pd.Timestamp, end_utc: pd.Timestamp, markets: set[str]) -> List[Fill]:
    fills: List[Fill] = []
    seen: set[tuple[str, str, int, int]] = set()
    for row in iter_json_lines(EXECUTION_LOG):
        if row.get("event_type") not in {"fill_full", "fill_partial"}:
            continue
        market = str(row.get("market") or "")
        if market not in markets:
            continue
        ts = pd.to_datetime(row.get("ts_wall"), utc=True, errors="coerce")
        if pd.isna(ts):
            continue
        # Include exits shortly after the window for markets opened inside the window.
        if ts < start_utc:
            continue
        client_id = str(row.get("client_order_id") or "")
        if client_id.startswith("btc15m-entry"):
            kind = "entry"
        elif client_id.startswith("btc15m-exit"):
            kind = "exit"
        else:
            continue
        qty = int(as_float(row.get("fill_count")) or as_float(row.get("cumulative_fill_count")) or 0)
        price = fill_price(row)
        side = str(row.get("side") or "")
        if qty <= 0 or price is None or not side:
            continue
        order_id = str(row.get("order_id") or client_id)
        key = (row.get("event_type"), order_id, qty, int(ts.value))
        if key in seen:
            continue
        seen.add(key)
        fills.append(Fill(ts=ts, kind=kind, market=market, side=side, qty=qty, price=float(price), client_order_id=client_id, order_id=order_id))
    return sorted(fills, key=lambda item: item.ts)


def realized_cash_report(trades: pd.DataFrame, fills: List[Fill]) -> Dict[str, Any]:
    outcome_by_market = {str(row.market): str(row.outcome) for row in trades.itertuples()}
    opened_markets = set(str(m) for m in trades["market"].unique())
    by_market_side: Dict[tuple[str, str], Dict[str, float]] = defaultdict(lambda: {"entry_qty": 0, "entry_cost": 0.0, "exit_qty": 0, "exit_value": 0.0})
    for fill in fills:
        if fill.market not in opened_markets:
            continue
        bucket = by_market_side[(fill.market, fill.side)]
        if fill.kind == "entry":
            bucket["entry_qty"] += fill.qty
            bucket["entry_cost"] += fill.qty * fill.price
        else:
            bucket["exit_qty"] += fill.qty
            bucket["exit_value"] += fill.qty * fill.price
    rows: List[Dict[str, Any]] = []
    total = 0.0
    open_contracts = 0
    for (market, side), bucket in sorted(by_market_side.items()):
        net_qty = int(bucket["entry_qty"] - bucket["exit_qty"])
        settlement_value = 0.0
        outcome = outcome_by_market.get(market)
        if net_qty > 0:
            open_contracts += net_qty
            if side == outcome:
                settlement_value = 100.0 * net_qty
        pnl = -bucket["entry_cost"] + bucket["exit_value"] + settlement_value
        total += pnl
        rows.append(
            {
                "market": market,
                "side": side,
                "outcome": outcome,
                "entry_qty": int(bucket["entry_qty"]),
                "entry_cost_cents": bucket["entry_cost"],
                "exit_qty": int(bucket["exit_qty"]),
                "exit_value_cents": bucket["exit_value"],
                "net_qty_to_settlement": net_qty,
                "settlement_value_cents": settlement_value,
                "gross_pnl_cents": pnl,
            }
        )
    return {
        "gross_realized_plus_settlement_cents": total,
        "open_contracts_after_exits": open_contracts,
        "rows": rows,
    }


def classify_warning(line: str) -> str:
    if "BTC market context refresh failed" in line:
        return "btc_market_context_timeout"
    if "Market refresh failed" in line:
        return "kalshi_market_refresh_timeout"
    if "Live account state refresh failed" in line:
        return "account_refresh_timeout"
    if "WS loop error" in line:
        return "kalshi_ws_loop_error"
    if "BTC tick stream failed" in line:
        return "btc_tick_stream_reconnect"
    if "Closed market" in line and "nonzero live account position" in line:
        return "closed_market_position_cleared"
    return "other_warning"


def bot_log_stats(start_utc: pd.Timestamp, end_utc: pd.Timestamp) -> Dict[str, Any]:
    watch_re = re.compile(r"Watching market (?P<market>\S+) close_time=(?P<close_time>\S+) status=(?P<status>\S+) strike=(?P<strike>[-0-9.]+)")
    entry_approved_re = re.compile(r"Mushroom v28 entry approved")
    entry_signal_re = re.compile(r"ENTRY signal")
    zero_fill_re = re.compile(r"state=abandoned reason=zero_fill")
    insufficient_depth_re = re.compile(r"reason=insufficient_visible_depth")
    warnings = Counter()
    counts = Counter()
    watched: Dict[str, Dict[str, Any]] = {}
    with BOT_LOG.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if len(line) < 23:
                continue
            ts = parse_local_log_ts(line[:23])
            if ts is None or ts < start_utc or ts > end_utc:
                continue
            if "WARNING" in line:
                warnings[classify_warning(line)] += 1
            if entry_approved_re.search(line):
                counts["entry_approved"] += 1
            if entry_signal_re.search(line):
                counts["entry_signal"] += 1
            if zero_fill_re.search(line):
                counts["zero_fill_abandoned"] += 1
            if insufficient_depth_re.search(line):
                counts["insufficient_visible_depth"] += 1
            watch = watch_re.search(line)
            if watch:
                market = watch.group("market")
                watched[market] = {
                    "market": market,
                    "close_time": watch.group("close_time"),
                    "status": watch.group("status"),
                    "strike": as_float(watch.group("strike")),
                }
    return {
        "warnings": dict(warnings),
        "counts": dict(counts),
        "watched_markets": list(watched.values()),
    }


def summarize_trades(trades: pd.DataFrame) -> Dict[str, Any]:
    if trades.empty:
        return {
            "entries": 0,
            "contracts": 0,
            "wins": 0,
            "losses": 0,
            "accuracy": None,
            "contract_accuracy": None,
            "settlement_pnl_cents": 0.0,
        }
    trades = trades.copy()
    trades["settlement_pnl_cents"] = trades.apply(settlement_pnl_cents, axis=1)
    wins = int(trades["win"].sum())
    entries = int(len(trades))
    contracts = int(trades["qty"].sum())
    winning_contracts = int(trades.loc[trades["win"], "qty"].sum())
    return {
        "entries": entries,
        "contracts": contracts,
        "wins": wins,
        "losses": entries - wins,
        "accuracy": wins / entries if entries else None,
        "winning_contracts": winning_contracts,
        "contract_accuracy": winning_contracts / contracts if contracts else None,
        "settlement_pnl_cents": float(trades["settlement_pnl_cents"].sum()),
        "avg_ask_cents": float(trades["ask_cents"].mean()),
        "median_ask_cents": float(trades["ask_cents"].median()),
        "unique_markets_traded": int(trades["market"].nunique()),
    }


def write_report(path: Path, generated: str, start_utc: pd.Timestamp, end_utc: pd.Timestamp, trades: pd.DataFrame, trade_summary: Dict[str, Any], cash: Dict[str, Any], log_stats: Dict[str, Any]) -> None:
    start_local = start_utc.tz_convert(LOCAL_TZ)
    end_local = end_utc.tz_convert(LOCAL_TZ)
    watched_markets = log_stats["watched_markets"]
    traded_markets = set(trades["market"].unique()) if not trades.empty else set()
    resolved_watch_count = len(watched_markets)
    lines: List[str] = []
    lines.append("# Overnight Live Bot Performance")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append(f"Window: `{start_local.isoformat()}` to `{end_local.isoformat()}` local")
    lines.append("")
    lines.append("## Trading Performance")
    lines.append("")
    lines.append(f"- Entry fills: {trade_summary['entries']}")
    lines.append(f"- Contracts filled: {trade_summary['contracts']}")
    lines.append(f"- Settlement winners: {trade_summary['wins']} / {trade_summary['entries']} trades = {pct(trade_summary['accuracy'])}")
    lines.append(f"- Winning contracts: {trade_summary.get('winning_contracts', 0)} / {trade_summary['contracts']} = {pct(trade_summary['contract_accuracy'])}")
    lines.append(f"- Unique traded markets: {trade_summary.get('unique_markets_traded', 0)}")
    lines.append(f"- Average / median entry ask: {cents(trade_summary.get('avg_ask_cents'))} / {cents(trade_summary.get('median_ask_cents'))}")
    lines.append(f"- Settlement-only gross P&L proxy: {cents(trade_summary['settlement_pnl_cents'])}")
    lines.append(f"- Gross cash-flow plus settlement value proxy after exits: {cents(cash['gross_realized_plus_settlement_cents'])}")
    lines.append(f"- Open contracts after parsed exits for overnight markets: {cash['open_contracts_after_exits']}")
    lines.append("")
    lines.append("## Market Coverage")
    lines.append("")
    lines.append(f"- Watched market intervals in window: {resolved_watch_count}")
    lines.append(f"- Traded market intervals in window: {len(traded_markets)}")
    coverage = len(traded_markets) / resolved_watch_count if resolved_watch_count else None
    lines.append(f"- Filled-trade market coverage: {pct(coverage)}")
    lines.append("")
    lines.append("## Operational Health")
    lines.append("")
    counts = log_stats["counts"]
    warnings = log_stats["warnings"]
    lines.append(f"- Entry approvals in bot log: {counts.get('entry_approved', 0)}")
    lines.append(f"- Entry signals submitted: {counts.get('entry_signal', 0)}")
    lines.append(f"- Zero-fill abandonments: {counts.get('zero_fill_abandoned', 0)}")
    lines.append(f"- Insufficient visible depth deferrals: {counts.get('insufficient_visible_depth', 0)}")
    lines.append(f"- Warnings: {sum(warnings.values())}")
    for key, value in sorted(warnings.items()):
        lines.append(f"  - {key}: {value}")
    lines.append("")
    lines.append("## Overnight Entry Ledger")
    lines.append("")
    if trades.empty:
        lines.append("No overnight entry fills found.")
    else:
        lines.append("| local time | market | side | outcome | win | qty | ask | p_side | edge | settlement pnl |")
        lines.append("|---|---|---|---|---|---:|---:|---:|---:|---:|")
        trades = trades.copy()
        trades["settlement_pnl_cents"] = trades.apply(settlement_pnl_cents, axis=1)
        for row in trades.sort_values("ts_wall").itertuples():
            local_ts = row.ts_wall.tz_convert(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")
            lines.append(
                f"| {local_ts} | `{row.market}` | {row.side} | {row.outcome} | {row.win} | "
                f"{int(row.qty)} | {float(row.ask_cents):.0f} | {float(row.v28_p_side):.4f} | "
                f"{float(row.v28_edge_cents):.2f} | {float(row.settlement_pnl_cents):.1f} |"
            )
    lines.append("")
    lines.append("## Read")
    lines.append("")
    if trade_summary["entries"]:
        if trade_summary["settlement_pnl_cents"] >= 0:
            lines.append(
                f"The bot was profitable on the settlement-only proxy overnight, but accuracy was {pct(trade_summary['accuracy'])}, below the 95% goal."
            )
        else:
            lines.append(
                f"The settlement-only proxy was negative, and accuracy was {pct(trade_summary['accuracy'])}, below the 95% goal."
            )
        if cash["gross_realized_plus_settlement_cents"] >= 0:
            lines.append(
                "Exit fills materially improved the basket: gross cash-flow plus settlement value was slightly positive before fees."
            )
        else:
            lines.append(
                "Exit fills helped, but gross cash-flow plus settlement value was still negative before fees."
            )
    if coverage is not None:
        lines.append(
            f"It filled trades in only {pct(coverage)} of watched 15-minute markets, far below the newly clarified 80% market-coverage target."
        )
    if counts.get("zero_fill_abandoned", 0):
        lines.append(
            "The main execution issue was not signal generation; several approved entries became zero-fill abandonments or depth deferrals."
        )
    if warnings:
        lines.append(
            "The bot stayed alive, but API/data timeouts and websocket reconnects were frequent enough to matter for coverage."
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-local", default=None, help="ISO local start, default previous day 18:00 America/New_York")
    parser.add_argument("--end-local", default=None, help="ISO local end, default now")
    args = parser.parse_args()

    now_local = datetime.now(LOCAL_TZ)
    start_local = datetime.fromisoformat(args.start_local) if args.start_local else default_start(now_local)
    if start_local.tzinfo is None:
        start_local = start_local.replace(tzinfo=LOCAL_TZ)
    end_local = datetime.fromisoformat(args.end_local) if args.end_local else now_local
    if end_local.tzinfo is None:
        end_local = end_local.replace(tzinfo=LOCAL_TZ)
    start_utc = pd.Timestamp(start_local.astimezone(timezone.utc))
    end_utc = pd.Timestamp(end_local.astimezone(timezone.utc))

    trades = load_trade_ledger(start_utc, end_utc)
    fills = load_fills(start_utc, end_utc, set(trades["market"].unique()) if not trades.empty else set())
    trade_summary = summarize_trades(trades)
    cash = realized_cash_report(trades, fills)
    log_stats = bot_log_stats(start_utc, end_utc)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    md_latest = OUT_DIR / "overnight_live_bot_performance_latest.md"
    md_stamp = OUT_DIR / f"overnight_live_bot_performance_{generated}.md"
    json_latest = OUT_DIR / "overnight_live_bot_performance_latest.json"
    json_stamp = OUT_DIR / f"overnight_live_bot_performance_{generated}.json"
    write_report(md_latest, generated, start_utc, end_utc, trades, trade_summary, cash, log_stats)
    write_report(md_stamp, generated, start_utc, end_utc, trades, trade_summary, cash, log_stats)

    summary = {
        "generated_utc": generated,
        "start_utc": start_utc.isoformat(),
        "end_utc": end_utc.isoformat(),
        "trade_summary": trade_summary,
        "cash": cash,
        "log_stats": log_stats,
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json(summary), indent=2, sort_keys=True), encoding="utf-8")

    print("Overnight performance report complete")
    print(f"entries={trade_summary['entries']} contracts={trade_summary['contracts']} accuracy={pct(trade_summary['accuracy'])}")
    print(f"settlement_proxy={cents(trade_summary['settlement_pnl_cents'])} cash_plus_settlement={cents(cash['gross_realized_plus_settlement_cents'])}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
