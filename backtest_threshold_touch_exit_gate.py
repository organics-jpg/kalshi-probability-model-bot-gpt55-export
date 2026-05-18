from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from build_v28_successor_live_pnl_policy_lab import estimated_taker_fee_cents


ROOT = Path(__file__).resolve().parent
RESEARCH_DATA = ROOT / "research_data"
V28_DIR = ROOT / "research_particle" / "v28_successor"
LABELS_CSV = V28_DIR / "sidecar_bundle_batch_settlement_labels_latest.csv"
PREDICTOR_CSV = V28_DIR / "live_pnl_labeled_decisions_latest.csv"
OUT_DIR = ROOT / "logs" / "edge_research"
SUMMARY_CSV = OUT_DIR / "threshold_touch_exit_gate_backtest_latest.csv"
TRADES_CSV = OUT_DIR / "threshold_touch_exit_gate_trades_latest.csv"
SUMMARY_JSON = OUT_DIR / "threshold_touch_exit_gate_backtest_latest.json"
SUMMARY_MD = OUT_DIR / "threshold_touch_exit_gate_backtest_latest.md"

SELECTED_CANDIDATE_ID = "v28s_boundary_monotonic_light_v001"
THRESHOLDS = [80.0, 90.0]
ENTRY_MODES = ["strict_cross", "include_left_censored"]
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


def finite(value: float) -> bool:
    return not math.isnan(value) and math.isfinite(value)


def fee(price_cents: float) -> int:
    return estimated_taker_fee_cents(price_cents, count=1)


def fmt(value: Any) -> str:
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return f"{value:.6f}"
    return str(value)


def settlement_side_from_label(row: dict[str, Any]) -> str:
    direct = str(row.get("binary_result") or row.get("settlement_side") or "").strip().lower()
    if direct in {"yes", "no"}:
        return direct
    y_yes = str(row.get("y_yes_win") or "").strip()
    if y_yes == "1":
        return "yes"
    if y_yes == "0":
        return "no"
    return ""


def load_labels() -> dict[str, dict[str, Any]]:
    labels: dict[str, dict[str, Any]] = {}
    if not LABELS_CSV.exists():
        return labels
    with LABELS_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ticker = str(row.get("market_ticker") or "").strip()
            side = settlement_side_from_label(row)
            if not ticker or side not in {"yes", "no"}:
                continue
            labels[ticker] = {
                "market_ticker": ticker,
                "market_close_ts_utc": "",  # filled from predictor rows when available
                "settlement_side": side,
                "settlement_price": row.get("settlement_price") or "",
                "settlement_ts_utc": row.get("settlement_ts_utc") or "",
                "settlement_source": row.get("label_source") or "",
            }
    return labels


def row_side_bid(row: dict[str, Any]) -> float:
    return as_float(row.get("bid_cents"))


def load_predictor_rows(
    labels: dict[str, dict[str, Any]]
) -> tuple[dict[str, dict[str, list[dict[str, Any]]]], dict[str, dict[str, list[dict[str, Any]]]]]:
    selected_rows_by_market_side: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    all_v28_rows_by_market_side: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    if not PREDICTOR_CSV.exists():
        return selected_rows_by_market_side, all_v28_rows_by_market_side
    seen_row_ids: set[str] = set()
    seen_v28_time_side: set[tuple[str, str, str]] = set()
    with PREDICTOR_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ticker = str(row.get("market_ticker") or "").strip()
            if ticker in labels and not labels[ticker].get("market_close_ts_utc"):
                close_ts_for_label = parse_ts(row.get("market_close_ts_utc"))
                if close_ts_for_label is not None:
                    labels[ticker]["market_close_ts_utc"] = iso_z(close_ts_for_label)
            if row.get("label_join_status") != "joined_post_resolution":
                continue
            side = str(row.get("side") or "").strip().lower()
            ts = parse_ts(row.get("decision_ts_utc"))
            close_ts = parse_ts(row.get("market_close_ts_utc"))
            if not ticker or ticker not in labels or side not in {"yes", "no"} or ts is None:
                continue
            v28_key = (ticker, side, str(row.get("decision_ts_utc") or ""))
            if v28_key not in seen_v28_time_side:
                seen_v28_time_side.add(v28_key)
                v28_row = dict(row)
                v28_row["_decision_dt"] = ts
                v28_row["_close_dt"] = close_ts
                all_v28_rows_by_market_side[ticker][side].append(v28_row)
            if row.get("candidate_id") != SELECTED_CANDIDATE_ID:
                continue
            row_id = str(row.get("row_id") or "")
            if row_id in seen_row_ids:
                continue
            seen_row_ids.add(row_id)
            selected_row = dict(row)
            selected_row["_decision_dt"] = ts
            selected_row["_close_dt"] = close_ts
            if close_ts is not None and not labels[ticker].get("market_close_ts_utc"):
                labels[ticker]["market_close_ts_utc"] = iso_z(close_ts)
            selected_rows_by_market_side[ticker][side].append(selected_row)
    for sides in selected_rows_by_market_side.values():
        for rows in sides.values():
            rows.sort(key=lambda item: item["_decision_dt"])
    for sides in all_v28_rows_by_market_side.values():
        for rows in sides.values():
            rows.sort(key=lambda item: item["_decision_dt"])
    return selected_rows_by_market_side, all_v28_rows_by_market_side


def parse_ticker_event(obj: dict[str, Any], path: Path, line_no: int) -> dict[str, Any] | None:
    payload = obj.get("payload_json")
    if not isinstance(payload, dict):
        return None
    ticker = str(obj.get("market_ticker") or payload.get("market_ticker") or "").strip()
    ts = parse_ts(payload.get("time") or payload.get("ts") or obj.get("exchange_ts") or obj.get("local_recv_ts"))
    if ts is None:
        ts = parse_ts(obj.get("local_recv_ts") or obj.get("ts_wall"))
    if not ticker or ts is None:
        return None
    return {
        "market_ticker": ticker,
        "ts": ts,
        "yes_ask_cents": as_float(payload.get("yes_ask")),
        "no_ask_cents": as_float(payload.get("no_ask")),
        "yes_bid_cents": as_float(payload.get("yes_bid")),
        "no_bid_cents": as_float(payload.get("no_bid")),
        "yes_ask_size": as_float(payload.get("yes_ask_size_fp"), 0.0),
        "no_ask_size": as_float(payload.get("no_ask_size_fp"), 0.0),
        "yes_bid_size": as_float(payload.get("yes_bid_size_fp"), 0.0),
        "no_bid_size": as_float(payload.get("no_bid_size_fp"), 0.0),
        "source_file": str(path.relative_to(ROOT)),
        "source_line": line_no,
        "dataset_tag": obj.get("dataset_tag") or "",
        "run_id": obj.get("run_id") or "",
        "sequence_number": obj.get("sequence_number") or "",
    }


def load_ticker_events(labels: dict[str, dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], int]:
    events_by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    raw_count = 0
    for path in RESEARCH_DATA.glob("**/raw_events/type=ticker/day=*/hour=*/part-*.ndjson"):
        try:
            with path.open(encoding="utf-8") as f:
                for line_no, line in enumerate(f, start=1):
                    text = line.strip()
                    if not text:
                        continue
                    try:
                        obj = json.loads(text)
                    except json.JSONDecodeError:
                        continue
                    event = parse_ticker_event(obj, path, line_no)
                    if event is None:
                        continue
                    raw_count += 1
                    if event["market_ticker"] in labels:
                        events_by_market[event["market_ticker"]].append(event)
        except OSError:
            continue
    for events in events_by_market.values():
        events.sort(key=lambda item: item["ts"])
    return events_by_market, raw_count


def side_ask(event: dict[str, Any], side: str) -> float:
    return float(event[f"{side}_ask_cents"])


def side_bid(event: dict[str, Any], side: str) -> float:
    return float(event[f"{side}_bid_cents"])


def side_ask_size(event: dict[str, Any], side: str) -> float:
    return float(event[f"{side}_ask_size"])


def is_fillable_touch(event: dict[str, Any], side: str) -> bool:
    ask = side_ask(event, side)
    size = side_ask_size(event, side)
    # 100-cent zero-size terminal quotes are common and are not useful evidence
    # of a tradable threshold touch.
    return finite(ask) and 0.0 < ask < 100.0 and size > 0.0


def seconds_to_close(ts: datetime, close_ts: datetime | None) -> float:
    if close_ts is None:
        return math.nan
    return (close_ts - ts).total_seconds()


def find_threshold_touch(
    events: list[dict[str, Any]],
    *,
    threshold: float,
    close_ts: datetime | None,
    entry_mode: str,
) -> dict[str, Any] | None:
    seen_below = {"yes": False, "no": False}
    for event in events:
        if close_ts is not None and event["ts"] >= close_ts:
            continue
        candidates: list[dict[str, Any]] = []
        for side in ("yes", "no"):
            if not is_fillable_touch(event, side):
                continue
            ask = side_ask(event, side)
            if ask < threshold:
                seen_below[side] = True
                continue
            left_censored = not seen_below[side]
            if entry_mode == "strict_cross" and left_censored:
                continue
            candidates.append(
                {
                    "entry_side": side,
                    "entry_ts": event["ts"],
                    "entry_price_cents": threshold,
                    "entry_observed_ask_cents": ask,
                    "entry_observed_bid_cents": side_bid(event, side),
                    "entry_observed_ask_size": side_ask_size(event, side),
                    "entry_seconds_to_close": seconds_to_close(event["ts"], close_ts),
                    "entry_left_censored": left_censored,
                    "entry_same_tick_candidate_count": 0,
                    "entry_source_file": event["source_file"],
                    "entry_source_line": event["source_line"],
                    "entry_dataset_tag": event.get("dataset_tag", ""),
                    "entry_sequence_number": event.get("sequence_number", ""),
                }
            )
        if not candidates:
            continue
        candidates.sort(key=lambda item: (item["entry_left_censored"], -item["entry_observed_ask_cents"], item["entry_side"]))
        chosen = candidates[0]
        chosen["entry_same_tick_candidate_count"] = len(candidates)
        return chosen
    return None


def candidate_fair(row: dict[str, Any]) -> float:
    return as_float(row.get("candidate_fair_side_cents"))


def v28_fair(row: dict[str, Any]) -> float:
    return as_float(row.get("v28_fair_side_cents"))


def candidate_net_edge(row: dict[str, Any]) -> float:
    return as_float(row.get("candidate_net_edge_after_fees_cents"))


@dataclass(frozen=True)
class ExitGate:
    name: str
    trigger: Callable[[dict[str, Any], float], tuple[bool, str]]


def fair_lt(prefix: str, limit: float) -> ExitGate:
    def trigger(row: dict[str, Any], entry_price: float) -> tuple[bool, str]:
        value = candidate_fair(row) if prefix == "candidate" else v28_fair(row)
        if finite(value) and value < limit:
            return True, f"{prefix}_fair_side_cents={value:.3f}<{limit:.0f}"
        return False, ""

    return ExitGate(f"{prefix}_fair_lt_{int(limit)}", trigger)


def fair_lt_entry_minus(delta: float) -> ExitGate:
    def trigger(row: dict[str, Any], entry_price: float) -> tuple[bool, str]:
        value = candidate_fair(row)
        limit = entry_price - delta
        if finite(value) and value < limit:
            return True, f"candidate_fair_side_cents={value:.3f}<entry_minus_{delta:.0f}"
        return False, ""

    return ExitGate(f"candidate_fair_lt_entry_minus_{int(delta)}", trigger)


def bid_lt_entry_minus(delta: float) -> ExitGate:
    def trigger(row: dict[str, Any], entry_price: float) -> tuple[bool, str]:
        bid = row_side_bid(row)
        if finite(bid) and bid < entry_price - delta:
            return True, f"bid_cents={bid:.3f}<entry_minus_{delta:.0f}"
        return False, ""

    return ExitGate(f"bid_lt_entry_minus_{int(delta)}", trigger)


def edge_lt(limit: float) -> ExitGate:
    def trigger(row: dict[str, Any], entry_price: float) -> tuple[bool, str]:
        edge = candidate_net_edge(row)
        if finite(edge) and edge < limit:
            return True, f"candidate_net_edge_after_fees_cents={edge:.3f}<{limit:.0f}"
        return False, ""

    return ExitGate(f"candidate_net_edge_lt_{int(limit)}", trigger)


def combined_candidate_fair_or_bid(fair_limit: float, bid_delta: float) -> ExitGate:
    def trigger(row: dict[str, Any], entry_price: float) -> tuple[bool, str]:
        fair = candidate_fair(row)
        bid = row_side_bid(row)
        fair_hit = finite(fair) and fair < fair_limit
        bid_hit = finite(bid) and bid < entry_price - bid_delta
        if fair_hit or bid_hit:
            return True, f"candidate_fair={fair:.3f};bid={bid:.3f}"
        return False, ""

    return ExitGate(f"candidate_fair_lt_{int(fair_limit)}_or_bid_lt_entry_minus_{int(bid_delta)}", trigger)


EXIT_GATES: list[ExitGate] = [
    ExitGate("hold", lambda row, entry_price: (False, "")),
    fair_lt("candidate", 60.0),
    fair_lt("candidate", 70.0),
    fair_lt("candidate", 75.0),
    fair_lt("candidate", 80.0),
    fair_lt("candidate", 85.0),
    fair_lt("candidate", 90.0),
    fair_lt("v28", 60.0),
    fair_lt("v28", 70.0),
    fair_lt("v28", 75.0),
    fair_lt("v28", 80.0),
    fair_lt("v28", 85.0),
    fair_lt_entry_minus(5.0),
    fair_lt_entry_minus(10.0),
    bid_lt_entry_minus(5.0),
    bid_lt_entry_minus(10.0),
    bid_lt_entry_minus(15.0),
    edge_lt(0.0),
    combined_candidate_fair_or_bid(80.0, 10.0),
    combined_candidate_fair_or_bid(85.0, 5.0),
]


def find_exit(
    predictor_rows: list[dict[str, Any]],
    *,
    entry_ts: datetime,
    close_ts: datetime | None,
    entry_price: float,
    gate: ExitGate,
) -> tuple[dict[str, Any] | None, str]:
    if gate.name == "hold":
        return None, ""
    for row in predictor_rows:
        ts = row["_decision_dt"]
        if ts <= entry_ts:
            continue
        if close_ts is not None and ts >= close_ts:
            continue
        triggered, reason = gate.trigger(row, entry_price)
        if not triggered:
            continue
        bid = row_side_bid(row)
        if not finite(bid):
            continue
        row["_exit_reason"] = reason
        return row, reason
    return None, ""


def trade_pnl(
    *,
    entry_side: str,
    settlement_side: str,
    entry_price: float,
    exit_row: dict[str, Any] | None,
) -> tuple[float, str, float, int]:
    entry_fee = fee(entry_price)
    if exit_row is not None:
        exit_bid = max(0.0, min(100.0, row_side_bid(exit_row)))
        exit_fee = fee(exit_bid) if exit_bid > EPS else 0
        return exit_bid - entry_price - entry_fee - exit_fee, "early_exit", exit_bid, exit_fee
    if entry_side == settlement_side:
        return 100.0 - entry_price - entry_fee, "settlement_win", 100.0, 0
    return -entry_price - entry_fee, "settlement_loss", 0.0, 0


def summarize(trades: list[dict[str, Any]]) -> dict[str, Any]:
    if not trades:
        return {}
    pnl = [float(t["net_pnl_cents"]) for t in trades]
    running = 0.0
    peak = 0.0
    max_dd = 0.0
    for value in pnl:
        running += value
        peak = max(peak, running)
        max_dd = max(max_dd, peak - running)
    avg = sum(pnl) / len(pnl)
    if len(pnl) > 1:
        variance = sum((value - avg) ** 2 for value in pnl) / (len(pnl) - 1)
        stderr = math.sqrt(variance / len(pnl))
    else:
        stderr = 0.0
    wins_to_settlement = sum(1 for t in trades if t["entry_side"] == t["settlement_side"])
    settlement_losses = sum(1 for t in trades if t["entry_side"] != t["settlement_side"])
    early_exits = sum(1 for t in trades if t["outcome"] == "early_exit")
    early_exited_winners = sum(1 for t in trades if t["outcome"] == "early_exit" and t["entry_side"] == t["settlement_side"])
    early_exited_losers = sum(1 for t in trades if t["outcome"] == "early_exit" and t["entry_side"] != t["settlement_side"])
    left_censored = sum(1 for t in trades if str(t["entry_left_censored"]).lower() == "true")
    with_predictor_rows = sum(1 for t in trades if int(t["post_entry_predictor_rows"]) > 0)
    return {
        "entries": len(trades),
        "wins_if_held": wins_to_settlement,
        "losses_if_held": settlement_losses,
        "win_rate_if_held": wins_to_settlement / len(trades),
        "early_exits": early_exits,
        "early_exited_winners": early_exited_winners,
        "early_exited_losers": early_exited_losers,
        "left_censored_entries": left_censored,
        "rows_with_post_entry_predictor": with_predictor_rows,
        "net_pnl_cents": sum(pnl),
        "avg_pnl_cents": avg,
        "median_pnl_cents": sorted(pnl)[len(pnl) // 2],
        "max_drawdown_cents": max_dd,
        "lcb_avg_pnl_cents": avg - 1.96 * stderr,
        "entry_fee_cents": trades[0]["entry_fee_cents"],
    }


def run() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    labels = load_labels()
    selected_predictor_rows, all_v28_rows = load_predictor_rows(labels)
    ticker_events, raw_ticker_count = load_ticker_events(labels)

    all_trades: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    coverage = {
        "labeled_markets": len(labels),
        "raw_ticker_events_seen": raw_ticker_count,
        "labeled_markets_with_raw_ticker": len(ticker_events),
        "predictor_candidate_id": SELECTED_CANDIDATE_ID,
        "labeled_markets_with_selected_predictor_rows": sum(1 for t in labels if t in selected_predictor_rows),
        "labeled_markets_with_any_v28_rows": sum(1 for t in labels if t in all_v28_rows),
    }

    for threshold in THRESHOLDS:
        for entry_mode in ENTRY_MODES:
            entries_by_market: dict[str, dict[str, Any]] = {}
            for ticker, label in labels.items():
                close_ts = parse_ts(label.get("market_close_ts_utc"))
                if close_ts is None:
                    # Some labels only know settlement. If predictor rows exist, load_predictor_rows
                    # will have filled close time; otherwise this market cannot be timed causally.
                    continue
                entry = find_threshold_touch(
                    ticker_events.get(ticker, []),
                    threshold=threshold,
                    close_ts=close_ts,
                    entry_mode=entry_mode,
                )
                if entry is not None:
                    entries_by_market[ticker] = entry

            for gate in EXIT_GATES:
                trades: list[dict[str, Any]] = []
                for ticker, entry in entries_by_market.items():
                    label = labels[ticker]
                    close_ts = parse_ts(label.get("market_close_ts_utc"))
                    entry_side = entry["entry_side"]
                    rows_source = "selected_candidate"
                    rows = selected_predictor_rows.get(ticker, {}).get(entry_side, [])
                    if gate.name.startswith("v28_") or gate.name.startswith("bid_"):
                        rows_source = "all_v28_rows"
                        rows = all_v28_rows.get(ticker, {}).get(entry_side, [])
                    post_rows = [r for r in rows if r["_decision_dt"] > entry["entry_ts"] and (close_ts is None or r["_decision_dt"] < close_ts)]
                    exit_row, exit_reason = find_exit(
                        rows,
                        entry_ts=entry["entry_ts"],
                        close_ts=close_ts,
                        entry_price=threshold,
                        gate=gate,
                    )
                    pnl, outcome, exit_price, exit_fee = trade_pnl(
                        entry_side=entry_side,
                        settlement_side=label["settlement_side"],
                        entry_price=threshold,
                        exit_row=exit_row,
                    )
                    trade = {
                        "threshold": threshold,
                        "entry_mode": entry_mode,
                        "exit_gate": gate.name,
                        "market_ticker": ticker,
                        "entry_side": entry_side,
                        "settlement_side": label["settlement_side"],
                        "side_win_if_held": entry_side == label["settlement_side"],
                        "entry_ts_utc": iso_z(entry["entry_ts"]),
                        "market_close_ts_utc": label.get("market_close_ts_utc", ""),
                        "entry_seconds_to_close": entry["entry_seconds_to_close"],
                        "entry_price_cents": threshold,
                        "entry_fee_cents": fee(threshold),
                        "entry_observed_ask_cents": entry["entry_observed_ask_cents"],
                        "entry_observed_bid_cents": entry["entry_observed_bid_cents"],
                        "entry_observed_ask_size": entry["entry_observed_ask_size"],
                        "entry_left_censored": entry["entry_left_censored"],
                        "entry_same_tick_candidate_count": entry["entry_same_tick_candidate_count"],
                        "post_entry_predictor_rows": len(post_rows),
                        "exit_row_source": rows_source,
                        "outcome": outcome,
                        "exit_ts_utc": iso_z(exit_row["_decision_dt"]) if exit_row is not None else "",
                        "exit_price_cents": exit_price,
                        "exit_fee_cents": exit_fee,
                        "exit_reason": exit_reason,
                        "net_pnl_cents": pnl,
                        "settlement_price": label.get("settlement_price", ""),
                        "settlement_ts_utc": label.get("settlement_ts_utc", ""),
                        "entry_source_file": entry["entry_source_file"],
                        "entry_source_line": entry["entry_source_line"],
                        "entry_dataset_tag": entry.get("entry_dataset_tag", ""),
                    }
                    trades.append(trade)
                    all_trades.append(trade)
                summary = summarize(trades)
                if summary:
                    summary.update(
                        {
                            "threshold": threshold,
                            "entry_mode": entry_mode,
                            "exit_gate": gate.name,
                            "markets_considered": len(labels),
                            "markets_with_raw_ticker": len(ticker_events),
                            "markets_with_threshold_touch": len(entries_by_market),
                        }
                    )
                    summary_rows.append(summary)

    return summary_rows, all_trades, coverage


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: fmt(value) for key, value in row.items()})


def write_report(summary_rows: list[dict[str, Any]], coverage: dict[str, Any]) -> None:
    key_gate_names = {
        "hold",
        "candidate_fair_lt_75",
        "candidate_fair_lt_80",
        "candidate_fair_lt_85",
        "candidate_fair_lt_entry_minus_5",
        "candidate_fair_lt_80_or_bid_lt_entry_minus_10",
        "candidate_fair_lt_85_or_bid_lt_entry_minus_5",
    }
    key_rows = [
        row
        for row in summary_rows
        if row["entry_mode"] == "include_left_censored" and row["exit_gate"] in key_gate_names
    ]
    top_rows = sorted(summary_rows, key=lambda row: (row["net_pnl_cents"], row["entries"]), reverse=True)[:24]

    lines = [
        "# Threshold Touch + FV/Boundary Exit Gate Backtest",
        "",
        "Research-only. No live bot, order logic, thresholds, state, secrets, sizing, or orders are touched.",
        "",
        f"- Labeled finalized markets: {coverage['labeled_markets']}",
        f"- Raw ticker events scanned: {coverage['raw_ticker_events_seen']}",
        f"- Labeled markets with raw ticker events: {coverage['labeled_markets_with_raw_ticker']}",
        f"- Markets with selected predictor rows: {coverage['labeled_markets_with_selected_predictor_rows']}",
        f"- Markets with any v28 rows: {coverage['labeled_markets_with_any_v28_rows']}",
        f"- Predictor carrier: `{coverage['predictor_candidate_id']}`",
        "- Entry model: buy the first side whose raw top-of-book ask touches/crosses the threshold; entry price is fixed at the threshold.",
        "- `strict_cross` requires an observed below-threshold quote before the touch.",
        "- `include_left_censored` also includes markets where recording started after the side was already above the threshold; those rows are useful but optimistic.",
        "- Candidate exit gates use the selected carrier only; v28/book exit gates use the full deduped v28 row stream.",
        "- Exit gates are evaluated only after entry and before close using causal predictor rows.",
        "- PnL is cents per one contract, fee-aware on entry and fee-aware on early exit.",
        "",
        "## Key Include-Left-Censored Rows",
        "| threshold | gate | entries | wins if held | losses if held | exits | exited winners | exited losers | net c | avg c | LCB c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in key_rows:
        lines.append(
            "| {threshold:.0f} | {exit_gate} | {entries} | {wins_if_held} | {losses_if_held} | "
            "{early_exits} | {early_exited_winners} | {early_exited_losers} | {net_pnl_cents:.1f} | "
            "{avg_pnl_cents:.2f} | {lcb_avg_pnl_cents:.2f} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Top Configurations",
            "| threshold | mode | gate | entries | wins if held | losses if held | exits | left censored | net c | avg c | LCB c |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in top_rows:
        lines.append(
            "| {threshold:.0f} | {entry_mode} | {exit_gate} | {entries} | {wins_if_held} | {losses_if_held} | "
            "{early_exits} | {left_censored_entries} | {net_pnl_cents:.1f} | {avg_pnl_cents:.2f} | "
            "{lcb_avg_pnl_cents:.2f} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Correctness Notes",
            "- This is the intended threshold-touch framing, so 80/90 entry counts do not depend on FV approval.",
            "- Entry counts can still be below all finalized labels because not every labeled market has raw ticker coverage or a causal touch timestamp.",
            "- The include-left-censored rows answer the user's intuition that the market had already hit the threshold, but they are optimistic because the exact historical fill moment was not observed.",
            "- A promotable live strategy would freeze this policy forward and judge it on live incoming markets, not on this diagnostic alone.",
        ]
    )
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    summary_rows, trades, coverage = run()
    write_csv(SUMMARY_CSV, summary_rows)
    write_csv(TRADES_CSV, trades)
    SUMMARY_JSON.write_text(json.dumps({"coverage": coverage, "summary": summary_rows}, indent=2, default=str), encoding="utf-8")
    write_report(summary_rows, coverage)
    print(f"labeled_markets={coverage['labeled_markets']}")
    print(f"raw_ticker_events={coverage['raw_ticker_events_seen']}")
    print(f"labeled_markets_with_raw_ticker={coverage['labeled_markets_with_raw_ticker']}")
    print(f"wrote {SUMMARY_CSV}")
    print(f"wrote {TRADES_CSV}")
    print(f"wrote {SUMMARY_MD}")
    print("KEY")
    for row in summary_rows:
        if row["entry_mode"] != "include_left_censored":
            continue
        if row["exit_gate"] not in {"hold", "candidate_fair_lt_75", "candidate_fair_lt_80", "candidate_fair_lt_85"}:
            continue
        print(
            row["threshold"],
            row["entry_mode"],
            row["exit_gate"],
            "entries",
            row["entries"],
            "wins_if_held",
            row["wins_if_held"],
            "losses_if_held",
            row["losses_if_held"],
            "exits",
            row["early_exits"],
            "net",
            round(row["net_pnl_cents"], 1),
            "avg",
            round(row["avg_pnl_cents"], 2),
            "lcb",
            round(row["lcb_avg_pnl_cents"], 2),
        )


if __name__ == "__main__":
    main()
