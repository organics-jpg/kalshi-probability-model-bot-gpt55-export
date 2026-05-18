"""Research-only live v28 fair-value selection scan.

This script does not import or modify the bot. It reads the live v28
execution log plus bot heartbeat log, infers settled outcomes from late
quotes, and searches candidate selection rules over already-filled v28 entry
trades. The goal is to test whether any fair-value rule can reach high
realized accuracy while preserving most live trade volume.
"""

from __future__ import annotations

import csv
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parent
LIVE_DIR = ROOT / "logs" / "live_mushroom_v28_size2"
EXECUTION_LOG = LIVE_DIR / "execution_events.ndjson"
BOT_LOG = LIVE_DIR / "bot.log"
OUT_DIR = ROOT / "logs" / "edge_research"
METADATA_CACHE = OUT_DIR / "kalshi_market_metadata_cache.json"

MIN_TARGET_ACCURACY = 0.95
MIN_CONTRACT_RETENTION = 0.75
MIN_TRADE_RETENTION = 0.75
MIN_ALL_SELECTED_TRADES = 75
MIN_HOLDOUT_SELECTED_TRADES = 15
MIN_ALL_SELECTED_CONTRACTS = 150
MIN_HOLDOUT_SELECTED_CONTRACTS = 30


def as_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        if math.isnan(float(value)):
            return None
        return float(value)
    text = str(value).strip()
    if not text or text.lower() in {"none", "null", "nan"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def as_int(value: Any) -> Optional[int]:
    number = as_float(value)
    if number is None:
        return None
    return int(round(number))


def as_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    return None


def first_present(row: Dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = row.get(key)
        if value is not None:
            return value
    return None


def clamp_prob(p: Optional[float]) -> Optional[float]:
    if p is None:
        return None
    return max(0.001, min(0.999, p))


def logit(p: float) -> float:
    p = max(0.001, min(0.999, p))
    return math.log(p / (1.0 - p))


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def pooled_probability(p1: Optional[float], p2: Optional[float], lam: float) -> Optional[float]:
    p1 = clamp_prob(p1)
    p2 = clamp_prob(p2)
    if p1 is None or p2 is None:
        return None
    return sigmoid((1.0 - lam) * logit(p1) + lam * logit(p2))


def wilson_lower_bound(wins: int, total: int, z: float = 1.96) -> Optional[float]:
    if total <= 0:
        return None
    phat = wins / total
    denom = 1.0 + z * z / total
    centre = phat + z * z / (2.0 * total)
    margin = z * math.sqrt((phat * (1.0 - phat) + z * z / (4.0 * total)) / total)
    return (centre - margin) / denom


def parse_quote_token(value: str) -> Optional[int]:
    parsed = as_float(value)
    if parsed is None:
        return None
    return int(round(parsed))


def infer_outcome_from_quote(quote: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    yes_bid = as_float(quote.get("yes_bid"))
    yes_ask = as_float(quote.get("yes_ask"))
    no_bid = as_float(quote.get("no_bid"))
    no_ask = as_float(quote.get("no_ask"))

    bid_candidates: List[Tuple[str, float]] = []
    if yes_bid is not None:
        bid_candidates.append(("yes", yes_bid))
    if no_bid is not None:
        bid_candidates.append(("no", no_bid))
    if bid_candidates:
        side, bid = max(bid_candidates, key=lambda item: item[1])
        if bid >= 98:
            return {"outcome": side, "method": "bid>=98", "confidence_price": bid}

    mids: List[Tuple[str, float]] = []
    if yes_bid is not None and yes_ask is not None:
        mids.append(("yes", (yes_bid + yes_ask) / 2.0))
    if no_bid is not None and no_ask is not None:
        mids.append(("no", (no_bid + no_ask) / 2.0))
    if mids:
        side, mid = max(mids, key=lambda item: item[1])
        other_mid = min((value for other_side, value in mids if other_side != side), default=None)
        if mid >= 95:
            return {"outcome": side, "method": "mid>=95", "confidence_price": mid}
        if mid >= 90 and (other_mid is None or other_mid <= 10):
            return {"outcome": side, "method": "mid>=90_other<=10", "confidence_price": mid}

    return None


def parse_bot_log(path: Path) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    watch_re = re.compile(
        r"Watching market (?P<market>\S+) close_time=(?P<close_time>\S+) "
        r"status=(?P<status>\S+) strike=(?P<strike>\S+)"
    )
    heartbeat_re = re.compile(
        r"Heartbeat \| watch=(?P<market>\S+) "
        r"yes_bid=(?P<yes_bid>\S+) yes_ask=(?P<yes_ask>\S+) "
        r"no_bid=(?P<no_bid>\S+) no_ask=(?P<no_ask>\S+)"
    )

    markets: Dict[str, Dict[str, Any]] = {}
    latest_quotes: Dict[str, Dict[str, Any]] = {}
    decisive_quotes: Dict[str, Dict[str, Any]] = {}
    metadata_cache: Dict[str, Dict[str, Any]] = {}
    if METADATA_CACHE.exists():
        try:
            metadata_cache = json.loads(METADATA_CACHE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            metadata_cache = {}

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            watch = watch_re.search(line)
            if watch:
                ticker = watch.group("market")
                cached_meta = metadata_cache.get(ticker) or {}
                strike = as_float(watch.group("strike"))
                if strike is None:
                    strike = as_float(cached_meta.get("floor_strike"))
                markets[watch.group("market")] = {
                    "market": ticker,
                    "close_time": watch.group("close_time") or cached_meta.get("close_time"),
                    "status": watch.group("status"),
                    "strike": strike,
                    "line_no": line_no,
                }
                continue

            heartbeat = heartbeat_re.search(line)
            if not heartbeat:
                continue

            market = heartbeat.group("market")
            quote = {
                "market": market,
                "yes_bid": parse_quote_token(heartbeat.group("yes_bid")),
                "yes_ask": parse_quote_token(heartbeat.group("yes_ask")),
                "no_bid": parse_quote_token(heartbeat.group("no_bid")),
                "no_ask": parse_quote_token(heartbeat.group("no_ask")),
                "line_no": line_no,
                "log_ts": line.split(" | ", 1)[0].strip(),
            }
            latest_quotes[market] = quote
            inferred = infer_outcome_from_quote(quote)
            if inferred:
                decisive_quotes[market] = {**quote, **inferred}

    outcomes: Dict[str, Dict[str, Any]] = {}
    for market, quote in latest_quotes.items():
        inferred = infer_outcome_from_quote(quote)
        if inferred:
            outcomes[market] = {**quote, **inferred, "source": "latest_quote"}
        elif market in decisive_quotes:
            outcomes[market] = {**decisive_quotes[market], "source": "last_decisive_quote"}

    return markets, outcomes


def iter_json_lines(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            row["_line_no"] = line_no
            yield row


def extract_entry_fills(path: Path, outcomes: Dict[str, Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    raw_entry_fill_events = 0
    missing_outcome_events = 0

    for event in iter_json_lines(path):
        if event.get("event_type") not in {"fill_full", "fill_partial"}:
            continue
        client_order_id = str(event.get("client_order_id") or "")
        if not client_order_id.startswith("btc15m-entry"):
            continue
        fill_count = as_int(event.get("fill_count")) or 0
        cumulative = as_int(event.get("cumulative_fill_count")) or 0
        if max(fill_count, cumulative) <= 0:
            continue
        raw_entry_fill_events += 1
        if event.get("market") not in outcomes:
            missing_outcome_events += 1
            continue
        key = str(event.get("order_id") or client_order_id)
        grouped.setdefault(key, []).append(event)

    entries: List[Dict[str, Any]] = []
    for key, events in grouped.items():
        events.sort(key=lambda row: str(row.get("ts_wall") or ""))
        source = max(events, key=lambda row: len([k for k in row if k.startswith("mushroom")]))
        cumulative_counts = [as_int(row.get("cumulative_fill_count")) for row in events]
        cumulative_counts = [value for value in cumulative_counts if value is not None]
        if cumulative_counts:
            qty = max(cumulative_counts)
        elif len(events) > 1:
            qty = sum(as_int(row.get("fill_count")) or 0 for row in events)
        else:
            qty = as_int(events[-1].get("fill_count")) or 0
        if qty <= 0:
            continue

        market = str(source.get("market"))
        side = str(source.get("side") or source.get("mushroom_v28_side") or "").lower()
        if side not in {"yes", "no"}:
            continue

        outcome = outcomes[market]["outcome"]
        ask = as_float(
            first_present(
                source,
                "mushroom_v28_ask_cents",
                "actual_fill_price_cents",
                "trigger_price_cents",
                "top_of_book_limit_cents",
                "cap_price_cents",
            )
        )
        fee_slip = (as_float(source.get("mushroom_v28_fee_cents")) or 1.5) + (
            as_float(source.get("mushroom_v28_slippage_cents")) or 1.0
        )

        v22_prefix = "mushroom_yes" if side == "yes" else "mushroom_no"
        market_p_yes = as_float(source.get("mushroom_market_p_yes"))
        market_p_side = None
        market_side = None
        if market_p_yes is not None:
            market_p_side = market_p_yes if side == "yes" else 1.0 - market_p_yes
            market_side = "yes" if market_p_yes >= 0.5 else "no"

        v22_best_side = source.get("mushroom_best_side")
        v28_btc_price = as_float(source.get("mushroom_v28_btc_price"))
        v28_strike = as_float(source.get("mushroom_v28_strike"))
        v28_sigma_t_dollars = as_float(source.get("mushroom_v28_sigma_t_dollars"))
        v28_seconds_to_close = as_float(source.get("mushroom_v28_seconds_to_close"))
        v28_margin_dollars = None
        v28_margin_per_sqrt_sec = None
        v28_margin_per_sigma = None
        if v28_btc_price is not None and v28_strike is not None:
            if side == "yes":
                v28_margin_dollars = v28_btc_price - v28_strike
            else:
                v28_margin_dollars = v28_strike - v28_btc_price
            if v28_seconds_to_close is not None and v28_seconds_to_close > 0:
                v28_margin_per_sqrt_sec = v28_margin_dollars / math.sqrt(v28_seconds_to_close)
            if v28_sigma_t_dollars is not None and v28_sigma_t_dollars > 0:
                v28_margin_per_sigma = v28_margin_dollars / v28_sigma_t_dollars

        entry = {
            "entry_key": key,
            "market": market,
            "ts_wall": source.get("ts_wall"),
            "line_no": source.get("_line_no"),
            "side": side,
            "outcome": outcome,
            "win": side == outcome,
            "qty": qty,
            "ask_cents": ask,
            "fee_slip_cents": fee_slip,
            "v28_p_side": as_float(source.get("mushroom_v28_p_side")),
            "v28_p_yes": as_float(source.get("mushroom_v28_p_yes")),
            "v28_edge_cents": as_float(source.get("mushroom_v28_edge_cents")),
            "v28_raw_edge_cents": as_float(source.get("mushroom_v28_raw_edge_cents")),
            "v28_fair_side_cents": as_float(source.get("mushroom_v28_fair_side_cents")),
            "v28_model_max_buy_price_cents": as_float(source.get("mushroom_v28_model_max_buy_price_cents")),
            "v28_book_age_ms": as_float(source.get("mushroom_v28_book_age_ms")),
            "v28_btc_age_ms": as_float(source.get("mushroom_v28_btc_age_ms")),
            "v28_seconds_to_close": v28_seconds_to_close,
            "v28_depth_count": as_float(source.get("mushroom_v28_depth_count")),
            "v28_abs_d_sigma": as_float(source.get("mushroom_v28_abs_d_sigma")),
            "v28_d_sigma": as_float(source.get("mushroom_v28_d_sigma")),
            "v28_btc_price": v28_btc_price,
            "v28_strike": v28_strike,
            "v28_sigma_t_dollars": v28_sigma_t_dollars,
            "v28_margin_dollars": v28_margin_dollars,
            "v28_margin_per_sqrt_sec": v28_margin_per_sqrt_sec,
            "v28_margin_per_sigma": v28_margin_per_sigma,
            "v28_arrow": as_float(source.get("mushroom_v28_arrow")),
            "v28_volshock": as_float(source.get("mushroom_v28_volshock")),
            "v28_balance_count": as_float(source.get("mushroom_v28_balance_count")),
            "v22_actual_p_side": as_float(source.get(f"{v22_prefix}_p_side")),
            "v22_actual_edge_cents": as_float(source.get(f"{v22_prefix}_edge_cents")),
            "v22_actual_would_enter": as_bool(source.get(f"{v22_prefix}_would_enter")),
            "v22_actual_strict_would_enter": as_bool(source.get(f"{v22_prefix}_strict_would_enter")),
            "v22_best_side": v22_best_side,
            "v22_best_side_agrees": str(v22_best_side).lower() == side,
            "v22_would_v22_enter": as_bool(source.get("mushroom_would_v22_enter")),
            "market_p_yes": market_p_yes,
            "market_p_side": market_p_side,
            "market_side": market_side,
            "market_side_agrees": market_side == side if market_side else None,
            "outcome_method": outcomes[market].get("method"),
            "outcome_source": outcomes[market].get("source"),
            "outcome_line_no": outcomes[market].get("line_no"),
        }
        entries.append(entry)

    entries.sort(key=lambda row: str(row.get("ts_wall") or ""))
    diagnostics = {
        "raw_entry_fill_events": raw_entry_fill_events,
        "missing_outcome_events": missing_outcome_events,
        "deduped_entry_orders": len(grouped),
        "usable_entries": len(entries),
    }
    return entries, diagnostics


def split_entries(entries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    n = len(entries)
    train_end = int(n * 0.60)
    val_end = int(n * 0.80)
    return {
        "train": entries[:train_end],
        "validation": entries[train_end:val_end],
        "holdout": entries[val_end:],
        "all": entries,
    }


def metric_for_entries(selected: List[Dict[str, Any]], baseline: List[Dict[str, Any]]) -> Dict[str, Any]:
    trades = len(selected)
    contracts = sum(int(row["qty"]) for row in selected)
    winning_trades = sum(1 for row in selected if row["win"])
    winning_contracts = sum(int(row["qty"]) for row in selected if row["win"])
    baseline_trades = len(baseline)
    baseline_contracts = sum(int(row["qty"]) for row in baseline)
    return {
        "trades": trades,
        "contracts": contracts,
        "winning_trades": winning_trades,
        "winning_contracts": winning_contracts,
        "trade_accuracy": winning_trades / trades if trades else None,
        "contract_accuracy": winning_contracts / contracts if contracts else None,
        "trade_retention": trades / baseline_trades if baseline_trades else None,
        "contract_retention": contracts / baseline_contracts if baseline_contracts else None,
        "trade_wilson95_lower": wilson_lower_bound(winning_trades, trades),
        "contract_wilson95_lower": wilson_lower_bound(winning_contracts, contracts),
    }


def baseline_metrics(splits: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    return {name: metric_for_entries(rows, rows) for name, rows in splits.items()}


def oracle_limit(metric: Dict[str, Any], retention: float) -> Dict[str, Any]:
    required_trades = math.ceil(metric["trades"] * retention)
    required_contracts = math.ceil(metric["contracts"] * retention)
    max_trade_wins = min(metric["winning_trades"], required_trades)
    max_contract_wins = min(metric["winning_contracts"], required_contracts)
    return {
        "retention": retention,
        "required_trades": required_trades,
        "required_contracts": required_contracts,
        "max_trade_accuracy": max_trade_wins / required_trades if required_trades else None,
        "max_contract_accuracy": max_contract_wins / required_contracts if required_contracts else None,
    }


def oracle_limits(baseline: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {
        split_name: {
            "retention_75": oracle_limit(metric, 0.75),
            "retention_80": oracle_limit(metric, 0.80),
        }
        for split_name, metric in baseline.items()
    }


def future_wins_needed(wins: int, total: int, retention: float, target_accuracy: float) -> Dict[str, Any]:
    """Minimum additional all-winning observations needed for feasibility.

    This is an optimistic lower bound: it assumes every future observation is a
    winner and the selector can still perfectly exclude all current/future losers.
    """
    for extra_wins in range(0, 10000):
        future_total = total + extra_wins
        required_selected = math.ceil(retention * future_total)
        possible_wins = wins + extra_wins
        possible_accuracy = possible_wins / required_selected if required_selected else None
        if possible_accuracy is not None and possible_accuracy >= target_accuracy:
            return {
                "retention": retention,
                "target_accuracy": target_accuracy,
                "extra_all_winning_observations_needed": extra_wins,
                "future_total": future_total,
                "required_selected": required_selected,
                "possible_wins": possible_wins,
                "possible_accuracy": possible_accuracy,
            }
    return {
        "retention": retention,
        "target_accuracy": target_accuracy,
        "extra_all_winning_observations_needed": None,
    }


def future_feasibility_requirements(baseline: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    requirements: Dict[str, Dict[str, Any]] = {}
    for split_name, metric in baseline.items():
        requirements[split_name] = {}
        for retention in [0.75, 0.80]:
            suffix = f"retention_{int(retention * 100)}"
            requirements[split_name][suffix] = {
                "trades": future_wins_needed(
                    int(metric["winning_trades"]),
                    int(metric["trades"]),
                    retention,
                    MIN_TARGET_ACCURACY,
                ),
                "contracts": future_wins_needed(
                    int(metric["winning_contracts"]),
                    int(metric["contracts"]),
                    retention,
                    MIN_TARGET_ACCURACY,
                ),
            }
    return requirements


def candidate_probability_and_edge(row: Dict[str, Any], source: str, lam: Optional[float]) -> Tuple[Optional[float], Optional[float]]:
    ask = row.get("ask_cents")
    fee_slip = row.get("fee_slip_cents") or 2.5
    if source == "v28":
        return row.get("v28_p_side"), row.get("v28_edge_cents")
    if source == "v28_raw":
        return row.get("v28_p_side"), row.get("v28_raw_edge_cents")
    if source == "v22_actual":
        return row.get("v22_actual_p_side"), row.get("v22_actual_edge_cents")
    if source == "min_v28_v22":
        p1 = row.get("v28_p_side")
        p2 = row.get("v22_actual_p_side")
        e1 = row.get("v28_edge_cents")
        e2 = row.get("v22_actual_edge_cents")
        if p1 is None or p2 is None or e1 is None or e2 is None:
            return None, None
        return min(p1, p2), min(e1, e2)
    if source == "pool_v28_market":
        p = pooled_probability(row.get("v28_p_side"), row.get("market_p_side"), lam or 0.5)
    elif source == "pool_v28_v22":
        p = pooled_probability(row.get("v28_p_side"), row.get("v22_actual_p_side"), lam or 0.5)
    else:
        return None, None
    if p is None or ask is None:
        return p, None
    return p, p * 100.0 - ask - fee_slip


def row_passes_candidate(row: Dict[str, Any], candidate: Dict[str, Any]) -> bool:
    p_side, edge = candidate_probability_and_edge(row, candidate["source"], candidate.get("lambda"))
    if p_side is None or edge is None:
        return False
    if p_side < candidate["p_min"] or edge < candidate["edge_min"]:
        return False

    side_filter = candidate.get("side_filter")
    if side_filter and side_filter != "all" and row.get("side") != side_filter:
        return False

    ask = row.get("ask_cents")
    if ask is None or ask > candidate["ask_max"]:
        return False

    book_age = row.get("v28_book_age_ms")
    if book_age is None or book_age > candidate["book_age_max_ms"]:
        return False

    btc_age = row.get("v28_btc_age_ms")
    btc_age_max = candidate.get("btc_age_max_ms")
    if btc_age_max is not None and (btc_age is None or btc_age > btc_age_max):
        return False

    seconds = row.get("v28_seconds_to_close")
    if candidate.get("seconds_min") is not None and (seconds is None or seconds < candidate["seconds_min"]):
        return False
    if candidate.get("seconds_max") is not None and (seconds is None or seconds > candidate["seconds_max"]):
        return False

    abs_d_sigma = row.get("v28_abs_d_sigma")
    if candidate.get("abs_d_sigma_min") is not None and (
        abs_d_sigma is None or abs_d_sigma < candidate["abs_d_sigma_min"]
    ):
        return False
    if candidate.get("abs_d_sigma_max") is not None and (
        abs_d_sigma is None or abs_d_sigma > candidate["abs_d_sigma_max"]
    ):
        return False

    if candidate.get("require_v22_best_agree") and not row.get("v22_best_side_agrees"):
        return False
    if candidate.get("require_v22_would_enter") and not row.get("v22_actual_would_enter"):
        return False
    if candidate.get("require_market_agree") and not row.get("market_side_agrees"):
        return False

    v22_p_min = candidate.get("v22_p_min")
    if v22_p_min is not None:
        value = row.get("v22_actual_p_side")
        if value is None or value < v22_p_min:
            return False
    v22_edge_min = candidate.get("v22_edge_min")
    if v22_edge_min is not None:
        value = row.get("v22_actual_edge_cents")
        if value is None or value < v22_edge_min:
            return False
    market_p_min = candidate.get("market_p_min")
    if market_p_min is not None:
        value = row.get("market_p_side")
        if value is None or value < market_p_min:
            return False

    return True


def generate_candidates() -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    p_mins = [0.85, 0.86, 0.87, 0.88, 0.89, 0.90, 0.92, 0.94, 0.96]
    edge_mins = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0]
    ask_maxes = [85.0, 90.0, 95.0, 100.0]
    book_age_maxes = [500.0, 750.0, 1000.0, 1500.0]
    side_filters = ["all", "yes", "no"]

    def add(base: Dict[str, Any]) -> None:
        base = dict(base)
        base["rule_id"] = f"rule_{len(candidates) + 1:05d}"
        candidates.append(base)

    source_specs: List[Tuple[str, Optional[float]]] = [
        ("v28", None),
        ("v28_raw", None),
        ("v22_actual", None),
        ("min_v28_v22", None),
        ("pool_v28_market", 0.25),
        ("pool_v28_market", 0.50),
        ("pool_v28_market", 0.75),
        ("pool_v28_v22", 0.25),
        ("pool_v28_v22", 0.50),
        ("pool_v28_v22", 0.75),
    ]

    for source, lam in source_specs:
        for p_min in p_mins:
            for edge_min in edge_mins:
                for ask_max in ask_maxes:
                    for book_age_max in book_age_maxes:
                        add(
                            {
                                "source": source,
                                "lambda": lam,
                                "p_min": p_min,
                                "edge_min": edge_min,
                                "ask_max": ask_max,
                                "book_age_max_ms": book_age_max,
                                "btc_age_max_ms": 1500.0,
                                "side_filter": "all",
                            }
                        )

    for side_filter in side_filters:
        for p_min in [0.85, 0.88, 0.90, 0.92]:
            for edge_min in [2.0, 4.0, 8.0, 12.0]:
                add(
                    {
                        "source": "v28",
                        "lambda": None,
                        "p_min": p_min,
                        "edge_min": edge_min,
                        "ask_max": 90.0,
                        "book_age_max_ms": 1000.0,
                        "btc_age_max_ms": 1500.0,
                        "side_filter": side_filter,
                    }
                )

    for v22_p_min in [0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]:
        for v22_edge_min in [-40.0, -20.0, -10.0, 0.0, 2.0, 5.0, 10.0]:
            for require_best_agree in [False, True]:
                add(
                    {
                        "source": "v28",
                        "lambda": None,
                        "p_min": 0.85,
                        "edge_min": 2.0,
                        "ask_max": 90.0,
                        "book_age_max_ms": 1000.0,
                        "btc_age_max_ms": 1500.0,
                        "side_filter": "all",
                        "v22_p_min": v22_p_min,
                        "v22_edge_min": v22_edge_min,
                        "require_v22_best_agree": require_best_agree,
                    }
                )

    for market_p_min in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]:
        add(
            {
                "source": "v28",
                "lambda": None,
                "p_min": 0.85,
                "edge_min": 2.0,
                "ask_max": 90.0,
                "book_age_max_ms": 1000.0,
                "btc_age_max_ms": 1500.0,
                "side_filter": "all",
                "market_p_min": market_p_min,
                "require_market_agree": True,
            }
        )

    for seconds_min, seconds_max in [(0.0, 300.0), (300.0, 600.0), (600.0, 900.0), (300.0, 900.0)]:
        for abs_min, abs_max in [(None, 0.50), (0.50, None), (0.75, None), (None, 1.25)]:
            add(
                {
                    "source": "v28",
                    "lambda": None,
                    "p_min": 0.85,
                    "edge_min": 2.0,
                    "ask_max": 90.0,
                    "book_age_max_ms": 1000.0,
                    "btc_age_max_ms": 1500.0,
                    "side_filter": "all",
                    "seconds_min": seconds_min,
                    "seconds_max": seconds_max,
                    "abs_d_sigma_min": abs_min,
                    "abs_d_sigma_max": abs_max,
                }
            )

    return candidates


def evaluate_candidate(
    candidate: Dict[str, Any],
    splits: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    result = {"rule": candidate}
    for split_name, rows in splits.items():
        selected = [row for row in rows if row_passes_candidate(row, candidate)]
        result[split_name] = metric_for_entries(selected, rows)

    folds: List[Dict[str, Any]] = []
    all_rows = splits["all"]
    fold_size = math.ceil(len(all_rows) / 5) if all_rows else 0
    for index in range(5):
        start = index * fold_size
        stop = min(len(all_rows), start + fold_size)
        fold_rows = all_rows[start:stop]
        selected = [row for row in fold_rows if row_passes_candidate(row, candidate)]
        folds.append(metric_for_entries(selected, fold_rows))
    result["folds"] = folds
    result["target_pass"] = candidate_passes_target(result)
    result["target_observed_pass"] = candidate_passes_observed_target(result)
    return result


def metric_ge(metric: Dict[str, Any], key: str, threshold: float) -> bool:
    value = metric.get(key)
    return value is not None and value >= threshold


def candidate_passes_observed_target(result: Dict[str, Any]) -> bool:
    all_m = result["all"]
    hold_m = result["holdout"]
    train_m = result["train"]
    val_m = result["validation"]
    return (
        metric_ge(all_m, "contract_accuracy", MIN_TARGET_ACCURACY)
        and metric_ge(all_m, "trade_accuracy", MIN_TARGET_ACCURACY)
        and metric_ge(hold_m, "contract_accuracy", MIN_TARGET_ACCURACY)
        and metric_ge(hold_m, "trade_accuracy", MIN_TARGET_ACCURACY)
        and metric_ge(train_m, "contract_accuracy", 0.90)
        and metric_ge(val_m, "contract_accuracy", 0.90)
        and metric_ge(all_m, "contract_retention", MIN_CONTRACT_RETENTION)
        and metric_ge(all_m, "trade_retention", MIN_TRADE_RETENTION)
        and metric_ge(hold_m, "contract_retention", MIN_CONTRACT_RETENTION)
        and metric_ge(hold_m, "trade_retention", MIN_TRADE_RETENTION)
    )


def candidate_passes_target(result: Dict[str, Any]) -> bool:
    all_m = result["all"]
    hold_m = result["holdout"]
    if not candidate_passes_observed_target(result):
        return False
    sample_ok = (
        all_m["trades"] >= MIN_ALL_SELECTED_TRADES
        and all_m["contracts"] >= MIN_ALL_SELECTED_CONTRACTS
        and hold_m["trades"] >= MIN_HOLDOUT_SELECTED_TRADES
        and hold_m["contracts"] >= MIN_HOLDOUT_SELECTED_CONTRACTS
    )
    if not sample_ok:
        return False
    return True


def sort_key(result: Dict[str, Any]) -> Tuple[Any, ...]:
    all_m = result["all"]
    hold_m = result["holdout"]
    val_m = result["validation"]
    train_m = result["train"]
    return (
        1 if result["target_pass"] else 0,
        1 if result["target_observed_pass"] else 0,
        hold_m.get("contract_accuracy") or -1,
        all_m.get("contract_accuracy") or -1,
        val_m.get("contract_accuracy") or -1,
        train_m.get("contract_accuracy") or -1,
        all_m.get("contract_retention") or -1,
        hold_m.get("contract_retention") or -1,
        all_m.get("contracts") or -1,
    )


def flatten_result(result: Dict[str, Any]) -> Dict[str, Any]:
    flat: Dict[str, Any] = {}
    rule = result["rule"]
    for key, value in rule.items():
        flat[f"rule_{key}"] = value
    flat["target_pass"] = result["target_pass"]
    flat["target_observed_pass"] = result["target_observed_pass"]
    for split_name in ["all", "train", "validation", "holdout"]:
        metric = result[split_name]
        for key, value in metric.items():
            flat[f"{split_name}_{key}"] = value
    fold_contract_acc = [
        fold.get("contract_accuracy")
        for fold in result["folds"]
        if fold.get("contracts", 0) > 0 and fold.get("contract_accuracy") is not None
    ]
    fold_contract_ret = [
        fold.get("contract_retention")
        for fold in result["folds"]
        if fold.get("contracts", 0) > 0 and fold.get("contract_retention") is not None
    ]
    flat["fold_min_contract_accuracy"] = min(fold_contract_acc) if fold_contract_acc else None
    flat["fold_min_contract_retention"] = min(fold_contract_ret) if fold_contract_ret else None
    return flat


def pct(value: Optional[float]) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100.0:.2f}%"


def metric_summary(metric: Dict[str, Any]) -> str:
    return (
        f"{metric['winning_trades']}/{metric['trades']} trades ({pct(metric['trade_accuracy'])}), "
        f"{metric['winning_contracts']}/{metric['contracts']} contracts ({pct(metric['contract_accuracy'])}), "
        f"contract retention {pct(metric['contract_retention'])}"
    )


def write_trade_ledger(entries: List[Dict[str, Any]], path: Path) -> None:
    if not entries:
        path.write_text("", encoding="utf-8")
        return
    fields = [
        "ts_wall",
        "market",
        "side",
        "outcome",
        "win",
        "qty",
        "ask_cents",
        "v28_p_side",
        "v28_edge_cents",
        "v22_actual_p_side",
        "v22_actual_edge_cents",
        "v22_best_side",
        "v22_best_side_agrees",
        "market_p_side",
        "market_side_agrees",
        "v28_seconds_to_close",
        "v28_book_age_ms",
        "v28_btc_age_ms",
        "v28_btc_price",
        "v28_strike",
        "v28_sigma_t_dollars",
        "v28_d_sigma",
        "v28_abs_d_sigma",
        "v28_margin_dollars",
        "v28_margin_per_sqrt_sec",
        "v28_margin_per_sigma",
        "outcome_method",
        "entry_key",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in entries:
            writer.writerow({field: row.get(field) for field in fields})


def write_candidates_csv(results: List[Dict[str, Any]], path: Path) -> None:
    rows = [flatten_result(result) for result in results]
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({key for row in rows for key in row})
    leading = [
        "rule_rule_id",
        "rule_source",
        "rule_lambda",
        "rule_p_min",
        "rule_edge_min",
        "rule_ask_max",
        "rule_book_age_max_ms",
        "rule_side_filter",
        "target_pass",
        "target_observed_pass",
        "all_trade_accuracy",
        "all_contract_accuracy",
        "all_trade_retention",
        "all_contract_retention",
        "holdout_trade_accuracy",
        "holdout_contract_accuracy",
        "holdout_trade_retention",
        "holdout_contract_retention",
        "validation_contract_accuracy",
        "fold_min_contract_accuracy",
    ]
    ordered_fields = [field for field in leading if field in fields] + [
        field for field in fields if field not in leading
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ordered_fields)
        writer.writeheader()
        writer.writerows(rows)


def render_rule(rule: Dict[str, Any]) -> str:
    pieces = [
        f"id={rule.get('rule_id')}",
        f"source={rule.get('source')}",
        f"lambda={rule.get('lambda')}",
        f"p>={rule.get('p_min')}",
        f"edge>={rule.get('edge_min')}",
        f"ask<={rule.get('ask_max')}",
        f"book<={rule.get('book_age_max_ms')}",
    ]
    optional_keys = [
        "side_filter",
        "v22_p_min",
        "v22_edge_min",
        "market_p_min",
        "require_v22_best_agree",
        "require_v22_would_enter",
        "require_market_agree",
        "seconds_min",
        "seconds_max",
        "abs_d_sigma_min",
        "abs_d_sigma_max",
    ]
    for key in optional_keys:
        if key in rule and rule.get(key) not in (None, "all", False):
            pieces.append(f"{key}={rule.get(key)}")
    return ", ".join(pieces)


def write_markdown_report(summary: Dict[str, Any], path: Path) -> None:
    baseline = summary["baseline_metrics"]
    oracle = summary["oracle_limits"]
    future_req = summary["future_feasibility_requirements"]
    best = summary["top_results"][:10]
    high_volume = summary.get("top_high_volume_results", [])[:10]
    target_count = summary["target_pass_count"]
    observed_count = summary["target_observed_pass_count"]
    status = (
        "PASS: at least one scanned rule met the observed and sample-size gates."
        if target_count
        else "FAIL: no scanned rule met the 95% accuracy plus 75% volume gate with live holdout/sample checks."
    )

    lines: List[str] = []
    lines.append("# Live v28 FV Accuracy/Volume Search")
    lines.append("")
    lines.append(f"Generated UTC: {summary['generated_utc']}")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(status)
    lines.append("")
    lines.append("## Data")
    lines.append("")
    lines.append(f"- Execution log: `{summary['execution_log']}`")
    lines.append(f"- Bot log: `{summary['bot_log']}`")
    lines.append(f"- Usable deduped entry orders: {summary['diagnostics']['usable_entries']}")
    lines.append(f"- Markets with inferred outcomes: {summary['markets_with_outcomes']}")
    lines.append(f"- Candidate rules scanned: {summary['candidate_count']}")
    lines.append("")
    lines.append("## Baseline Current v28 Filled Entries")
    lines.append("")
    for split_name in ["all", "train", "validation", "holdout"]:
        lines.append(f"- {split_name}: {metric_summary(baseline[split_name])}")
    lines.append("")
    lines.append("## Oracle Feasibility Bound")
    lines.append("")
    lines.append(
        "This is the maximum possible accuracy if a rule could perfectly remove losers while still meeting the volume floor."
    )
    lines.append("")
    lines.append("| split | retention floor | required trades | max trade acc | required contracts | max contract acc |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for split_name in ["all", "train", "validation", "holdout"]:
        for key in ["retention_75", "retention_80"]:
            item = oracle[split_name][key]
            lines.append(
                "| "
                f"{split_name} | {item['retention'] * 100:.0f}% | "
                f"{item['required_trades']} | {pct(item['max_trade_accuracy'])} | "
                f"{item['required_contracts']} | {pct(item['max_contract_accuracy'])} |"
            )
    lines.append("")
    if oracle["holdout"]["retention_75"]["max_contract_accuracy"] < MIN_TARGET_ACCURACY:
        lines.append(
            "Holdout feasibility note: with 75% holdout contract retention, even an oracle can reach only "
            f"{pct(oracle['holdout']['retention_75']['max_contract_accuracy'])}. "
            "That makes the requested 95% holdout-verified accuracy/volume target impossible on the current holdout slice."
        )
        lines.append("")
    lines.append("## Minimum Future Evidence Needed")
    lines.append("")
    lines.append(
        "This is an optimistic lower bound for the holdout slice: it assumes every additional future observation is a winner."
    )
    lines.append("")
    lines.append("| unit | retention floor | extra all-winning observations needed | future total | required selected | possible accuracy |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for key in ["retention_75", "retention_80"]:
        for unit in ["trades", "contracts"]:
            item = future_req["holdout"][key][unit]
            lines.append(
                "| "
                f"{unit} | {item['retention'] * 100:.0f}% | "
                f"{item['extra_all_winning_observations_needed']} | "
                f"{item.get('future_total')} | {item.get('required_selected')} | "
                f"{pct(item.get('possible_accuracy'))} |"
            )
    lines.append("")
    lines.append("## Gate")
    lines.append("")
    lines.append(f"- Required realized accuracy: >= {MIN_TARGET_ACCURACY * 100:.0f}% trade and contract accuracy")
    lines.append(f"- Required retained volume: >= {MIN_CONTRACT_RETENTION * 100:.0f}% contracts and trades")
    lines.append(
        "- Sample-size floor used here: "
        f">= {MIN_ALL_SELECTED_TRADES} all trades / {MIN_ALL_SELECTED_CONTRACTS} all contracts, "
        f">= {MIN_HOLDOUT_SELECTED_TRADES} holdout trades / {MIN_HOLDOUT_SELECTED_CONTRACTS} holdout contracts"
    )
    lines.append("- Overfit controls: chronological 60/20/20 split plus five chronological fold diagnostics")
    lines.append("")
    lines.append("## Scan Result")
    lines.append("")
    lines.append(f"- Rules meeting observed accuracy/retention gate before sample floor: {observed_count}")
    lines.append(f"- Rules meeting observed gate and sample-size floor: {target_count}")
    lines.append("")
    lines.append("## Top Ranked Rules")
    lines.append("")
    lines.append(
        "| rank | rule | all contracts | all acc | all retention | holdout contracts | holdout acc | holdout retention | validation acc | target |"
    )
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for index, result in enumerate(best, start=1):
        all_m = result["all"]
        hold_m = result["holdout"]
        val_m = result["validation"]
        lines.append(
            "| "
            f"{index} | {render_rule(result['rule'])} | "
            f"{all_m['contracts']} | {pct(all_m['contract_accuracy'])} | {pct(all_m['contract_retention'])} | "
            f"{hold_m['contracts']} | {pct(hold_m['contract_accuracy'])} | {pct(hold_m['contract_retention'])} | "
            f"{pct(val_m['contract_accuracy'])} | {result['target_pass']} |"
        )
    lines.append("")
    lines.append("## Top High-Volume Rules")
    lines.append("")
    lines.append(
        "These rules retain at least 75% of contract volume in both all-data and holdout splits, then rank by holdout accuracy."
    )
    lines.append("")
    if high_volume:
        lines.append(
            "| rank | rule | all contracts | all acc | all retention | holdout contracts | holdout acc | holdout retention | validation acc |"
        )
        lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|")
        for index, result in enumerate(high_volume, start=1):
            all_m = result["all"]
            hold_m = result["holdout"]
            val_m = result["validation"]
            lines.append(
                "| "
                f"{index} | {render_rule(result['rule'])} | "
                f"{all_m['contracts']} | {pct(all_m['contract_accuracy'])} | {pct(all_m['contract_retention'])} | "
                f"{hold_m['contracts']} | {pct(hold_m['contract_accuracy'])} | {pct(hold_m['contract_retention'])} | "
                f"{pct(val_m['contract_accuracy'])} |"
            )
    else:
        lines.append("No scanned rule retained at least 75% of contract volume in both all-data and holdout splits.")
    lines.append("")
    lines.append("## Completion Audit")
    lines.append("")
    lines.append("| requirement | evidence | result |")
    lines.append("|---|---|---|")
    lines.append(
        f"| Use live websocket data | Parsed `{summary['bot_log']}` and `{summary['execution_log']}` | done |"
    )
    lines.append(
        f"| Do not change running bot logic | This script only reads logs and writes artifacts under `logs/edge_research` | done |"
    )
    lines.append(
        f"| >=95% realized accuracy | target-pass rules: {target_count}; observed-pass rules: {observed_count} | "
        f"{'done' if target_count else 'not met'} |"
    )
    lines.append(
        f"| Keep >=75%-80% trade volume | enforced at >=75% trade and contract retention in all and holdout splits | "
        f"{'done' if target_count else 'not met'} |"
    )
    lines.append(
        "| Not overfit | chronological train/validation/holdout and fold diagnostics included; no rule is promotable unless holdout also passes | "
        f"{'done' if target_count else 'not met'} |"
    )
    lines.append(
        "| Verified with sample size | sample floors and Wilson lower bounds computed in CSV/JSON | "
        f"{'done' if target_count else 'not met'} |"
    )
    lines.append("")
    if not target_count:
        lines.append(
            "Conclusion: with the current live v28 filled-trade sample, this scan did not find a fair-value "
            "selection version that satisfies the requested accuracy/volume/sample-size requirements. More "
            "live data or a materially different model family is needed before promotion."
        )
    else:
        lines.append(
            "Conclusion: at least one scanned rule met the formal gate. Review the CSV/JSON before any bot change."
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated_utc = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")

    markets, outcomes = parse_bot_log(BOT_LOG)
    entries, diagnostics = extract_entry_fills(EXECUTION_LOG, outcomes)
    if not entries:
        raise SystemExit("No usable live v28 entry fills with inferred outcomes were found.")

    splits = split_entries(entries)
    baseline = baseline_metrics(splits)
    oracle = oracle_limits(baseline)
    future_req = future_feasibility_requirements(baseline)
    candidates = generate_candidates()
    results = [evaluate_candidate(candidate, splits) for candidate in candidates]
    results.sort(key=sort_key, reverse=True)

    target_pass_count = sum(1 for result in results if result["target_pass"])
    observed_pass_count = sum(1 for result in results if result["target_observed_pass"])
    high_volume_results = [
        result
        for result in results
        if metric_ge(result["all"], "contract_retention", MIN_CONTRACT_RETENTION)
        and metric_ge(result["holdout"], "contract_retention", MIN_CONTRACT_RETENTION)
    ]
    high_volume_results.sort(
        key=lambda result: (
            result["holdout"].get("contract_accuracy") or -1,
            result["all"].get("contract_accuracy") or -1,
            result["validation"].get("contract_accuracy") or -1,
            result["all"].get("contract_retention") or -1,
        ),
        reverse=True,
    )
    summary = {
        "generated_utc": generated_utc,
        "execution_log": str(EXECUTION_LOG.relative_to(ROOT)),
        "bot_log": str(BOT_LOG.relative_to(ROOT)),
        "markets_seen": len(markets),
        "markets_with_outcomes": len(outcomes),
        "diagnostics": diagnostics,
        "baseline_metrics": baseline,
        "oracle_limits": oracle,
        "future_feasibility_requirements": future_req,
        "candidate_count": len(candidates),
        "target_pass_count": target_pass_count,
        "target_observed_pass_count": observed_pass_count,
        "top_results": results[:50],
        "top_high_volume_results": high_volume_results[:50],
        "requirements": {
            "min_target_accuracy": MIN_TARGET_ACCURACY,
            "min_contract_retention": MIN_CONTRACT_RETENTION,
            "min_trade_retention": MIN_TRADE_RETENTION,
            "min_all_selected_trades": MIN_ALL_SELECTED_TRADES,
            "min_holdout_selected_trades": MIN_HOLDOUT_SELECTED_TRADES,
            "min_all_selected_contracts": MIN_ALL_SELECTED_CONTRACTS,
            "min_holdout_selected_contracts": MIN_HOLDOUT_SELECTED_CONTRACTS,
        },
    }

    json_latest = OUT_DIR / "fv_accuracy_volume_search_latest.json"
    json_stamp = OUT_DIR / f"fv_accuracy_volume_search_{generated_utc}.json"
    md_latest = OUT_DIR / "fv_accuracy_volume_search_latest.md"
    md_stamp = OUT_DIR / f"fv_accuracy_volume_search_{generated_utc}.md"
    csv_latest = OUT_DIR / "fv_accuracy_volume_candidates_latest.csv"
    csv_stamp = OUT_DIR / f"fv_accuracy_volume_candidates_{generated_utc}.csv"
    ledger_latest = OUT_DIR / "fv_accuracy_volume_trades_latest.csv"
    ledger_stamp = OUT_DIR / f"fv_accuracy_volume_trades_{generated_utc}.csv"

    json_text = json.dumps(summary, indent=2, sort_keys=True)
    json_latest.write_text(json_text + "\n", encoding="utf-8")
    json_stamp.write_text(json_text + "\n", encoding="utf-8")
    write_markdown_report(summary, md_latest)
    write_markdown_report(summary, md_stamp)
    write_candidates_csv(results, csv_latest)
    write_candidates_csv(results, csv_stamp)
    write_trade_ledger(entries, ledger_latest)
    write_trade_ledger(entries, ledger_stamp)

    print("Live v28 FV accuracy/volume search complete")
    print(f"usable_entries={len(entries)} markets_with_outcomes={len(outcomes)} candidates={len(candidates)}")
    print(f"baseline_all={metric_summary(baseline['all'])}")
    print(f"target_observed_pass_count={observed_pass_count} target_pass_count={target_pass_count}")
    print(f"report={md_latest}")
    print(f"candidates={csv_latest}")
    print(f"ledger={ledger_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
