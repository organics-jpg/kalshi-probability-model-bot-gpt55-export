from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_v28_successor_live_pnl_policy_lab import estimated_taker_fee_cents


ROOT = Path(__file__).resolve().parent
RESEARCH_DATA = ROOT / "research_data"
V28_DIR = ROOT / "research_particle" / "v28_successor"
LABELED_CSV = V28_DIR / "live_pnl_labeled_decisions_latest.csv"
OUT_DIR = ROOT / "logs" / "edge_research"
SUMMARY_CSV = OUT_DIR / "touch_entry_predictor_exit_backtest_latest.csv"
TRADES_CSV = OUT_DIR / "touch_entry_predictor_exit_trades_latest.csv"
SUMMARY_JSON = OUT_DIR / "touch_entry_predictor_exit_backtest_latest.json"
SUMMARY_MD = OUT_DIR / "touch_entry_predictor_exit_backtest_latest.md"

SELECTED_CANDIDATE_ID = "v28s_boundary_monotonic_light_v001"
EPS = 1e-9


def parse_ts(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso_z(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def as_float(value: Any, default: float = math.nan) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def fmt(value: Any) -> str:
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return f"{value:.6f}"
    return str(value)


def best_bid(prices: Any) -> float | None:
    if not isinstance(prices, list) or not prices:
        return None
    values = [as_float(value) for value in prices]
    values = [value for value in values if not math.isnan(value)]
    if not values:
        return None
    return max(values)


def fee(price_cents: float) -> int:
    return estimated_taker_fee_cents(price_cents, count=1)


def load_labels() -> dict[str, dict[str, Any]]:
    labels: dict[str, dict[str, Any]] = {}
    if not LABELED_CSV.exists():
        return labels
    with LABELED_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("label_join_status") != "joined_post_resolution":
                continue
            ticker = str(row.get("market_ticker") or "")
            if not ticker or ticker in labels:
                continue
            labels[ticker] = {
                "market_ticker": ticker,
                "market_close_ts_utc": row.get("market_close_ts_utc") or "",
                "settlement_side": row.get("settlement_side") or "",
                "settlement_price": row.get("settlement_price") or "",
                "settlement_ts_utc": row.get("settlement_ts_utc") or "",
                "settlement_source": row.get("settlement_source") or "",
            }
    return labels


def load_predictor_rows() -> dict[str, dict[str, list[dict[str, Any]]]]:
    rows_by_market_side: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    if not LABELED_CSV.exists():
        return rows_by_market_side
    with LABELED_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("candidate_id") != SELECTED_CANDIDATE_ID:
                continue
            if row.get("label_join_status") != "joined_post_resolution":
                continue
            ticker = str(row.get("market_ticker") or "")
            side = str(row.get("side") or "").lower()
            ts = parse_ts(row.get("decision_ts_utc"))
            if not ticker or side not in {"yes", "no"} or ts is None:
                continue
            row["_decision_dt"] = ts
            rows_by_market_side[ticker][side].append(row)
    for sides in rows_by_market_side.values():
        for rows in sides.values():
            rows.sort(key=lambda row: row["_decision_dt"])
    return rows_by_market_side


def iter_book_checkpoints() -> list[dict[str, Any]]:
    checkpoints: list[dict[str, Any]] = []
    for path in RESEARCH_DATA.glob("**/book_checkpoints/day=*/market=*/part-*.ndjson"):
        try:
            with path.open(encoding="utf-8") as f:
                for line_no, line in enumerate(f, start=1):
                    text = line.strip()
                    if not text:
                        continue
                    try:
                        event = json.loads(text)
                    except json.JSONDecodeError:
                        continue
                    ts = parse_ts(event.get("checkpoint_ts") or event.get("ts_wall"))
                    ticker = str(event.get("market_ticker") or "")
                    if ts is None or not ticker:
                        continue
                    yes_bid = best_bid(event.get("yes_bid_prices"))
                    no_bid = best_bid(event.get("no_bid_prices"))
                    if yes_bid is None or no_bid is None:
                        continue
                    yes_ask = 100.0 - no_bid
                    no_ask = 100.0 - yes_bid
                    if not (0.0 < yes_ask < 100.0 and 0.0 < no_ask < 100.0):
                        continue
                    checkpoints.append(
                        {
                            "market_ticker": ticker,
                            "ts": ts,
                            "yes_bid_cents": yes_bid,
                            "no_bid_cents": no_bid,
                            "yes_ask_cents": yes_ask,
                            "no_ask_cents": no_ask,
                            "source_file": str(path.relative_to(ROOT)),
                            "source_line": line_no,
                            "source_event_count": event.get("source_event_count", ""),
                            "sequence_number": event.get("sequence_number", ""),
                        }
                    )
        except OSError:
            continue
    checkpoints.sort(key=lambda row: (row["market_ticker"], row["ts"]))
    return checkpoints


def side_prices(snapshot: dict[str, Any], side: str) -> tuple[float, float]:
    if side == "yes":
        return float(snapshot["yes_ask_cents"]), float(snapshot["yes_bid_cents"])
    return float(snapshot["no_ask_cents"]), float(snapshot["no_bid_cents"])


def seconds_to_close(snapshot_ts: datetime, close_ts: datetime | None) -> float:
    if close_ts is None:
        return math.nan
    return (close_ts - snapshot_ts).total_seconds()


def find_touch_entry(
    snapshots: list[dict[str, Any]],
    *,
    threshold: float,
    max_entry_ask: float,
    min_seconds_to_close: float,
    max_seconds_to_close: float,
    close_ts: datetime | None,
) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for snap in snapshots:
        sec = seconds_to_close(snap["ts"], close_ts)
        if math.isnan(sec) or sec < min_seconds_to_close or sec > max_seconds_to_close:
            continue
        candidates: list[dict[str, Any]] = []
        for side in ("yes", "no"):
            ask, bid = side_prices(snap, side)
            if threshold <= ask <= max_entry_ask:
                candidates.append(
                    {
                        "entry_side": side,
                        "entry_ts": snap["ts"],
                        "entry_ask_cents": ask,
                        "entry_bid_cents": bid,
                        "entry_seconds_to_close": sec,
                        "entry_source_file": snap["source_file"],
                        "entry_source_line": snap["source_line"],
                        "entry_sequence_number": snap.get("sequence_number", ""),
                    }
                )
        if not candidates:
            continue
        candidates.sort(key=lambda item: (-item["entry_ask_cents"], item["entry_side"]))
        best = candidates[0]
        break
    return best


def row_fair(row: dict[str, Any]) -> float:
    return as_float(row.get("candidate_fair_side_cents"))


def row_v28_fair(row: dict[str, Any]) -> float:
    return as_float(row.get("v28_fair_side_cents"))


def row_bid(row: dict[str, Any]) -> float:
    return as_float(row.get("bid_cents"))


def exit_trigger(row: dict[str, Any], gate: str, entry_ask: float) -> tuple[bool, str]:
    fair = row_fair(row)
    v28_fair = row_v28_fair(row)
    bid = row_bid(row)
    edge = as_float(row.get("candidate_net_edge_after_fees_cents"))
    if gate == "hold":
        return False, ""
    if gate == "fair_lt_70" and fair < 70.0:
        return True, f"candidate_fair_side_cents={fair:.3f}<70"
    if gate == "fair_lt_75" and fair < 75.0:
        return True, f"candidate_fair_side_cents={fair:.3f}<75"
    if gate == "fair_lt_80" and fair < 80.0:
        return True, f"candidate_fair_side_cents={fair:.3f}<80"
    if gate == "v28_fair_lt_75" and v28_fair < 75.0:
        return True, f"v28_fair_side_cents={v28_fair:.3f}<75"
    if gate == "bid_lt_entry_minus_10" and bid < entry_ask - 10.0:
        return True, f"bid_cents={bid:.3f}<entry_minus_10"
    if gate == "edge_lt_0" and edge < 0.0:
        return True, f"candidate_net_edge_after_fees_cents={edge:.3f}<0"
    if gate == "fair_lt_75_or_bid_lt_entry_minus_10" and (fair < 75.0 or bid < entry_ask - 10.0):
        return True, f"fair={fair:.3f};bid={bid:.3f}"
    return False, ""


def find_exit(
    predictor_rows: list[dict[str, Any]],
    *,
    entry_ts: datetime,
    entry_ask: float,
    gate: str,
) -> dict[str, Any] | None:
    for row in predictor_rows:
        row_ts = row["_decision_dt"]
        if row_ts <= entry_ts:
            continue
        triggered, reason = exit_trigger(row, gate, entry_ask)
        if not triggered:
            continue
        bid = row_bid(row)
        if math.isnan(bid) or bid <= 0.0:
            continue
        return {
            "exit_ts": row_ts,
            "exit_bid_cents": bid,
            "exit_reason": reason,
            "exit_candidate_fair_side_cents": row.get("candidate_fair_side_cents", ""),
            "exit_v28_fair_side_cents": row.get("v28_fair_side_cents", ""),
            "exit_seconds_to_close": row.get("seconds_to_close", ""),
        }
    return None


def score_trade(entry: dict[str, Any], label: dict[str, Any], exit_info: dict[str, Any] | None) -> dict[str, Any]:
    entry_ask = float(entry["entry_ask_cents"])
    entry_fee = fee(entry_ask)
    side = entry["entry_side"]
    settlement_side = str(label.get("settlement_side") or "")
    if exit_info:
        exit_bid = float(exit_info["exit_bid_cents"])
        pnl = exit_bid - entry_ask - entry_fee - 1.0
        outcome = "exit"
    else:
        pnl = 100.0 - entry_ask - entry_fee if side == settlement_side else -entry_ask - entry_fee
        outcome = "settlement_win" if pnl > 0 else "settlement_loss"
    result = dict(entry)
    result.update(
        {
            "settlement_side": settlement_side,
            "settlement_price": label.get("settlement_price", ""),
            "entry_fee_cents": entry_fee,
            "exit_used": bool(exit_info),
            "exit_ts": iso_z(exit_info["exit_ts"]) if exit_info else "",
            "exit_bid_cents": fmt(exit_info["exit_bid_cents"]) if exit_info else "",
            "exit_reason": exit_info["exit_reason"] if exit_info else "",
            "exit_candidate_fair_side_cents": exit_info.get("exit_candidate_fair_side_cents", "") if exit_info else "",
            "exit_v28_fair_side_cents": exit_info.get("exit_v28_fair_side_cents", "") if exit_info else "",
            "exit_seconds_to_close": exit_info.get("exit_seconds_to_close", "") if exit_info else "",
            "net_pnl_cents": pnl,
            "outcome": outcome,
            "wrong_side": side != settlement_side,
        }
    )
    result["entry_ts"] = iso_z(result["entry_ts"])
    return result


def max_drawdown(values: list[float]) -> float:
    equity = 0.0
    peak = 0.0
    worst = 0.0
    for value in values:
        equity += value
        peak = max(peak, equity)
        worst = min(worst, equity - peak)
    return -worst


def lcb(values: list[float]) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    stderr = math.sqrt(variance / len(values))
    return mean - 1.64 * stderr


def summarize(trades: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    pnls = [as_float(row.get("net_pnl_cents"), 0.0) for row in trades]
    by_market = {row["market_ticker"]: as_float(row.get("net_pnl_cents"), 0.0) for row in trades}
    wins = [pnl for pnl in pnls if pnl > 0]
    losses = [pnl for pnl in pnls if pnl < 0]
    exits = [row for row in trades if row.get("exit_used")]
    settlement_losses = [row for row in trades if row.get("outcome") == "settlement_loss"]
    market_values = list(by_market.values())
    without_best = sum(sorted(market_values, reverse=True)[1:]) if len(market_values) > 1 else 0.0
    return {
        **config,
        "entries": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": len(wins) / len(trades) if trades else math.nan,
        "wrong_side": sum(1 for row in trades if row.get("wrong_side")),
        "exits": len(exits),
        "settlement_losses": len(settlement_losses),
        "net_pnl_cents": sum(pnls),
        "avg_pnl_cents": sum(pnls) / len(trades) if trades else math.nan,
        "max_drawdown_cents": max_drawdown(pnls),
        "remove_best_market_net_cents": without_best,
        "market_lcb_cents": lcb(market_values),
        "worst_trade_cents": min(pnls) if pnls else math.nan,
        "best_trade_cents": max(pnls) if pnls else math.nan,
    }


def run() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    labels = load_labels()
    predictor_rows = load_predictor_rows()
    checkpoints = iter_book_checkpoints()
    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in checkpoints:
        if row["market_ticker"] in labels:
            by_market[row["market_ticker"]].append(row)
    for rows in by_market.values():
        rows.sort(key=lambda row: row["ts"])

    configs: list[dict[str, Any]] = []
    for threshold in (80.0, 90.0):
        for max_entry_ask in (95.0, 98.0, 99.9):
            if max_entry_ask < threshold:
                continue
            for window_name, min_sec, max_sec in (
                ("1_to_15_min", 60.0, 900.0),
                ("5_to_15_min", 300.0, 900.0),
                ("last_5_min", 0.0, 300.0),
                ("all_recorded_preclose", 0.0, 999999.0),
            ):
                for gate in (
                    "hold",
                    "fair_lt_70",
                    "fair_lt_75",
                    "fair_lt_80",
                    "v28_fair_lt_75",
                    "bid_lt_entry_minus_10",
                    "edge_lt_0",
                    "fair_lt_75_or_bid_lt_entry_minus_10",
                ):
                    configs.append(
                        {
                            "threshold_cents": threshold,
                            "max_entry_ask_cents": max_entry_ask,
                            "window": window_name,
                            "min_seconds_to_close": min_sec,
                            "max_seconds_to_close": max_sec,
                            "exit_gate": gate,
                        }
                    )

    all_trades: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    markets_with_labels = set(labels)
    markets_with_checkpoints = set(by_market)
    for config in configs:
        trades: list[dict[str, Any]] = []
        for ticker, snaps in by_market.items():
            close_ts = parse_ts(labels[ticker].get("market_close_ts_utc"))
            entry = find_touch_entry(
                snaps,
                threshold=float(config["threshold_cents"]),
                max_entry_ask=float(config["max_entry_ask_cents"]),
                min_seconds_to_close=float(config["min_seconds_to_close"]),
                max_seconds_to_close=float(config["max_seconds_to_close"]),
                close_ts=close_ts,
            )
            if entry is None:
                continue
            side_rows = predictor_rows.get(ticker, {}).get(entry["entry_side"], [])
            exit_info = find_exit(
                side_rows,
                entry_ts=entry["entry_ts"],
                entry_ask=float(entry["entry_ask_cents"]),
                gate=str(config["exit_gate"]),
            )
            trade = score_trade(entry, labels[ticker], exit_info)
            trade.update(
                {
                    "market_ticker": ticker,
                    "threshold_cents": config["threshold_cents"],
                    "max_entry_ask_cents": config["max_entry_ask_cents"],
                    "window": config["window"],
                    "exit_gate": config["exit_gate"],
                }
            )
            trades.append(trade)
        trades.sort(key=lambda row: (row["entry_ts"], row["market_ticker"], row["entry_side"]))
        all_trades.extend(trades)
        summaries.append(summarize(trades, config))

    summary_fields = [
        "threshold_cents",
        "max_entry_ask_cents",
        "window",
        "exit_gate",
        "entries",
        "wins",
        "losses",
        "win_rate",
        "wrong_side",
        "exits",
        "settlement_losses",
        "net_pnl_cents",
        "avg_pnl_cents",
        "max_drawdown_cents",
        "remove_best_market_net_cents",
        "market_lcb_cents",
        "worst_trade_cents",
        "best_trade_cents",
    ]
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary_fields)
        writer.writeheader()
        for row in summaries:
            writer.writerow({field: fmt(row.get(field, "")) for field in summary_fields})

    trade_fields = [
        "threshold_cents",
        "max_entry_ask_cents",
        "window",
        "exit_gate",
        "market_ticker",
        "entry_side",
        "entry_ts",
        "entry_seconds_to_close",
        "entry_ask_cents",
        "entry_bid_cents",
        "entry_fee_cents",
        "settlement_side",
        "settlement_price",
        "exit_used",
        "exit_ts",
        "exit_bid_cents",
        "exit_reason",
        "exit_candidate_fair_side_cents",
        "exit_v28_fair_side_cents",
        "exit_seconds_to_close",
        "net_pnl_cents",
        "outcome",
        "wrong_side",
        "entry_source_file",
        "entry_source_line",
        "entry_sequence_number",
    ]
    with TRADES_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=trade_fields)
        writer.writeheader()
        for row in all_trades:
            writer.writerow({field: fmt(row.get(field, "")) for field in trade_fields})

    def select(threshold: float, cap: float, window: str, gate: str) -> dict[str, Any] | None:
        for row in summaries:
            if (
                row["threshold_cents"] == threshold
                and row["max_entry_ask_cents"] == cap
                and row["window"] == window
                and row["exit_gate"] == gate
            ):
                return row
        return None

    key_rows = [
        row
        for row in [
            select(80.0, 95.0, "1_to_15_min", "hold"),
            select(80.0, 95.0, "1_to_15_min", "fair_lt_75"),
            select(80.0, 95.0, "last_5_min", "hold"),
            select(80.0, 95.0, "last_5_min", "fair_lt_75"),
            select(90.0, 95.0, "1_to_15_min", "hold"),
            select(90.0, 95.0, "1_to_15_min", "fair_lt_75"),
            select(90.0, 95.0, "5_to_15_min", "hold"),
            select(90.0, 95.0, "last_5_min", "hold"),
        ]
        if row is not None
    ]
    top_rows = sorted([row for row in summaries if row["entries"] >= 10], key=lambda row: row["avg_pnl_cents"], reverse=True)[:20]

    md: list[str] = []
    md.append("# Touch Entry + Predictor Exit Backtest")
    md.append("")
    md.append("Research-only. No live bot, order logic, thresholds, state, secrets, sizing, or orders are touched.")
    md.append("")
    md.append(f"- Raw book checkpoints loaded: {len(checkpoints)}")
    md.append(f"- Labeled markets available: {len(markets_with_labels)}")
    md.append(f"- Labeled markets with raw checkpoints: {len(markets_with_checkpoints)}")
    md.append(f"- Predictor carrier: `{SELECTED_CANDIDATE_ID}`")
    md.append("- Entry: first observed raw book touch on either YES or NO side.")
    md.append("- Visible asks are derived from the opposing bid ladder: YES ask = 100 - best NO bid; NO ask = 100 - best YES bid.")
    md.append("- Exit gates are evaluated only after entry using the selected FV/boundary predictor rows.")
    md.append("")
    md.append("## Key Rows")
    md.append("| threshold | cap | window | exit gate | entries | wins | wrong | exits | net c | avg c | max DD c | LCB c |")
    md.append("|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in key_rows:
        md.append(
            "| "
            + " | ".join(
                [
                    f"{row['threshold_cents']:.0f}",
                    f"{row['max_entry_ask_cents']:.0f}",
                    str(row["window"]),
                    str(row["exit_gate"]),
                    str(row["entries"]),
                    str(row["wins"]),
                    str(row["wrong_side"]),
                    str(row["exits"]),
                    f"{row['net_pnl_cents']:.1f}",
                    f"{row['avg_pnl_cents']:.2f}",
                    f"{row['max_drawdown_cents']:.1f}",
                    f"{row['market_lcb_cents']:.2f}",
                ]
            )
            + " |"
        )
    md.append("")
    md.append("## Top Configurations")
    md.append("| threshold | cap | window | exit gate | entries | wins | wrong | exits | net c | avg c | LCB c |")
    md.append("|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for row in top_rows:
        md.append(
            "| "
            + " | ".join(
                [
                    f"{row['threshold_cents']:.0f}",
                    f"{row['max_entry_ask_cents']:.0f}",
                    str(row["window"]),
                    str(row["exit_gate"]),
                    str(row["entries"]),
                    str(row["wins"]),
                    str(row["wrong_side"]),
                    str(row["exits"]),
                    f"{row['net_pnl_cents']:.1f}",
                    f"{row['avg_pnl_cents']:.2f}",
                    f"{row['market_lcb_cents']:.2f}",
                ]
            )
            + " |"
        )
    md.append("")
    md.append("## Notes")
    md.append("- This is the correct touch-entry framing, but still only on recorded checkpoints; unobserved exchange touches cannot be recovered.")
    md.append("- Exit gates are approximate because predictor rows are sampled sidecar checkpoints, not continuous tick-by-tick FV updates.")
    md.append("- A strong live-forward candidate should be frozen before using any of these diagnostics as primary evidence.")
    SUMMARY_MD.write_text("\n".join(md), encoding="utf-8")

    SUMMARY_JSON.write_text(
        json.dumps(
            {
                "raw_book_checkpoints": len(checkpoints),
                "labeled_markets": len(markets_with_labels),
                "labeled_markets_with_raw_checkpoints": len(markets_with_checkpoints),
                "summary_csv": str(SUMMARY_CSV),
                "trades_csv": str(TRADES_CSV),
                "markdown": str(SUMMARY_MD),
                "key_rows": key_rows,
                "top_rows": top_rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"raw_book_checkpoints={len(checkpoints)}")
    print(f"labeled_markets={len(markets_with_labels)}")
    print(f"labeled_markets_with_raw_checkpoints={len(markets_with_checkpoints)}")
    print(f"wrote {SUMMARY_CSV}")
    print(f"wrote {TRADES_CSV}")
    print(f"wrote {SUMMARY_MD}")
    print("KEY")
    for row in key_rows:
        print(
            row["threshold_cents"],
            row["max_entry_ask_cents"],
            row["window"],
            row["exit_gate"],
            "entries",
            row["entries"],
            "wins",
            row["wins"],
            "wrong",
            row["wrong_side"],
            "exits",
            row["exits"],
            "net",
            round(row["net_pnl_cents"], 1),
            "avg",
            round(row["avg_pnl_cents"], 2),
            "lcb",
            round(row["market_lcb_cents"], 2),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
