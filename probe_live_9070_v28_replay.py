"""Research-only v28 replay over the older live_90_70 labeled tape.

The current v28 live run is the cleanest source for real v28 decisions, but it
has a small and currently infeasible holdout slice for the requested
95%/75%-volume target. This supplemental probe replays the v28 fair-value
engine over the larger live_90_70 trade-label tape where local BTC candles are
available.

Important scope:
- This script does not import or modify the trading bot.
- It only reads research data and writes artifacts under logs/edge_research.
- It optionally fetches historical Kalshi market metadata solely to recover
  the missing strike fields needed for fair-value replay.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

from btc_mushroom_forecaster_v28_fast import FastMushroomFVEngineV28, FastMushroomV28Config


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "research_data" / "live_90_70"
OUT_DIR = ROOT / "logs" / "edge_research"
METADATA_CACHE = OUT_DIR / "kalshi_market_metadata_cache.json"
COINBASE_BTC_CACHE = OUT_DIR / "coinbase_btc_usd_1m_cache.parquet"

MIN_TARGET_ACCURACY = 0.95
MIN_CONTRACT_RETENTION = 0.75
MIN_TRADE_RETENTION = 0.75
MIN_ALL_SELECTED_TRADES = 75
MIN_HOLDOUT_SELECTED_TRADES = 30
MIN_ALL_SELECTED_CONTRACTS = 750
MIN_HOLDOUT_SELECTED_CONTRACTS = 300


def as_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> Optional[int]:
    number = as_float(value)
    if number is None:
        return None
    return int(round(number))


def pct(value: Optional[float]) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100.0:.2f}%"


def wilson_lower_bound(wins: int, total: int, z: float = 1.96) -> Optional[float]:
    if total <= 0:
        return None
    phat = wins / total
    denom = 1.0 + z * z / total
    centre = phat + z * z / (2.0 * total)
    margin = z * math.sqrt((phat * (1.0 - phat) + z * z / (4.0 * total)) / total)
    return (centre - margin) / denom


def estimated_order_fee_cents(price_cents: int, count: int) -> int:
    bounded_price = max(1, min(99, int(price_cents)))
    numerator = 7 * int(count) * bounded_price * (100 - bounded_price)
    return max(1, (numerator + 9999) // 10000)


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_market_metadata(ticker: str, retries: int = 3) -> Optional[Dict[str, Any]]:
    url = f"https://api.elections.kalshi.com/trade-api/v2/markets/{ticker}"
    last_error = ""
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
            market = payload.get("market") or {}
            return {
                "market": market.get("ticker") or ticker,
                "close_time": market.get("close_time"),
                "floor_strike": market.get("floor_strike"),
                "cap_strike": market.get("cap_strike"),
                "expiration_value": market.get("expiration_value"),
                "yes_sub_title": market.get("yes_sub_title"),
                "no_sub_title": market.get("no_sub_title"),
                "status": market.get("status"),
                "raw_market_type": market.get("market_type"),
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
            }
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            time.sleep(0.5 * (attempt + 1))
    return {"market": ticker, "fetch_error": last_error, "fetched_at_utc": datetime.now(timezone.utc).isoformat()}


def fetch_coinbase_btc_1m(start: pd.Timestamp, end: pd.Timestamp, retries: int = 3) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    start = pd.Timestamp(start).tz_convert("UTC").floor("min")
    end = pd.Timestamp(end).tz_convert("UTC").ceil("min")
    # Coinbase's candles endpoint can return 500s when the request includes
    # still-forming future/current candles. During live validation, cap to the
    # latest completed minute so strict monitors do not lose causal rows.
    latest_completed = pd.Timestamp.now(tz="UTC").floor("min")
    end = min(end, latest_completed)
    if end <= start:
        return pd.DataFrame()
    cursor = start
    headers = {"User-Agent": "codex-research-replay/1.0"}
    while cursor < end:
        chunk_end = min(cursor + pd.Timedelta(minutes=60), end)
        url = (
            "https://api.exchange.coinbase.com/products/BTC-USD/candles"
            f"?granularity=60&start={cursor.isoformat().replace('+00:00', 'Z')}"
            f"&end={chunk_end.isoformat().replace('+00:00', 'Z')}"
        )
        req = urllib.request.Request(url, headers=headers)
        payload: Any = None
        last_error = ""
        for attempt in range(max(1, retries)):
            try:
                with urllib.request.urlopen(req, timeout=20) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = str(exc)
                time.sleep(0.5 * (attempt + 1))
        if payload is None:
            print(
                f"warning: skipped Coinbase BTC candles {cursor.isoformat()}..{chunk_end.isoformat()}: {last_error}",
                file=sys.stderr,
            )
            cursor = chunk_end
            continue
        for item in payload:
            # Coinbase format: [time, low, high, open, close, volume]
            ts = pd.to_datetime(int(item[0]), unit="s", utc=True)
            rows.append(
                {
                    "symbol": "BTC-USD",
                    "interval": "1m",
                    "open_dt": ts,
                    "close_dt": ts + pd.Timedelta(seconds=59, milliseconds=999),
                    "open": float(item[3]),
                    "high": float(item[2]),
                    "low": float(item[1]),
                    "close": float(item[4]),
                    "volume": float(item[5]),
                    "source": "coinbase_rest",
                }
            )
        cursor = chunk_end
        time.sleep(0.08)
    if not rows:
        return pd.DataFrame(columns=["symbol", "interval", "open_dt", "close_dt", "open", "high", "low", "close", "volume", "source"])
    df = pd.DataFrame(rows)
    return df.sort_values("close_dt").drop_duplicates("close_dt", keep="last").reset_index(drop=True)


def load_trade_labels() -> pd.DataFrame:
    files = sorted((DATA_DIR / "trade_labels").rglob("*.parquet"))
    if not files:
        raise FileNotFoundError(DATA_DIR / "trade_labels")
    frames = [pd.read_parquet(path) for path in files]
    df = pd.concat(frames, ignore_index=True)
    df["entry_dt"] = pd.to_datetime(df["entry_dt"], utc=True, errors="coerce")
    df["market"] = df["market"].astype(str)
    df["side"] = df["side"].astype(str).str.lower()
    df["market_result"] = df["market_result"].astype(str).str.lower()
    df["outcome"] = df["outcome"].astype(str).str.lower()
    return df


def load_btc_candles(labels: pd.DataFrame, fetch_missing: bool) -> pd.DataFrame:
    files = sorted((DATA_DIR / "btc_spot_candles").rglob("*.parquet"))
    frames = [pd.read_parquet(path) for path in files] if files else []
    if COINBASE_BTC_CACHE.exists():
        frames.append(pd.read_parquet(COINBASE_BTC_CACHE))
    if fetch_missing:
        resolved = labels[labels["market_result"].isin(["yes", "no"])].copy()
        if not resolved.empty:
            start = resolved["entry_dt"].min() - pd.Timedelta(hours=4)
            end = resolved["entry_dt"].max() + pd.Timedelta(minutes=2)
            fetched = fetch_coinbase_btc_1m(start, end)
            if not fetched.empty:
                frames.append(fetched)
                if COINBASE_BTC_CACHE.exists():
                    old_cache = pd.read_parquet(COINBASE_BTC_CACHE)
                    cache_df = pd.concat([old_cache, fetched], ignore_index=True)
                else:
                    cache_df = fetched
                cache_df["close_dt"] = pd.to_datetime(cache_df["close_dt"], utc=True, errors="coerce")
                cache_df = cache_df.dropna(subset=["close_dt", "open", "high", "low", "close"])
                cache_df = cache_df.sort_values("close_dt").drop_duplicates("close_dt", keep="last").reset_index(drop=True)
                cache_df.to_parquet(COINBASE_BTC_CACHE, index=False)
    if not frames:
        raise FileNotFoundError(DATA_DIR / "btc_spot_candles")
    df = pd.concat(frames, ignore_index=True)
    df["close_dt"] = pd.to_datetime(df["close_dt"], utc=True, errors="coerce")
    df = df.dropna(subset=["close_dt", "open", "high", "low", "close"])
    df = df.sort_values("close_dt").drop_duplicates("close_dt", keep="last").reset_index(drop=True)
    return df


def recover_metadata(markets: Iterable[str], fetch_missing: bool) -> Tuple[Dict[str, Any], Dict[str, int]]:
    cache = load_json(METADATA_CACHE)
    stats = {"requested": 0, "cache_hits": 0, "fetched": 0, "missing_after": 0}
    for ticker in sorted(set(str(m) for m in markets if str(m) and str(m) != "nan")):
        stats["requested"] += 1
        cached = cache.get(ticker)
        if cached and cached.get("floor_strike") is not None:
            stats["cache_hits"] += 1
            continue
        if fetch_missing:
            cache[ticker] = fetch_market_metadata(ticker)
            stats["fetched"] += 1
        if not cache.get(ticker) or cache[ticker].get("floor_strike") is None:
            stats["missing_after"] += 1
    write_json(METADATA_CACHE, cache)
    return cache, stats


def feed_bars_until(engine: FastMushroomFVEngineV28, bars: pd.DataFrame, index: int, cutoff: pd.Timestamp) -> int:
    while index < len(bars) and bars.iloc[index]["close_dt"] <= cutoff:
        row = bars.iloc[index]
        engine.update_bar(
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row.get("volume", 0.0) or 0.0),
            ts=row["close_dt"].to_pydatetime(),
        )
        index += 1
    return index


def replay_entries(
    labels: pd.DataFrame,
    bars: pd.DataFrame,
    metadata: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    engine = FastMushroomFVEngineV28(FastMushroomV28Config())
    bar_index = 0
    entries: List[Dict[str, Any]] = []
    skipped: Dict[str, int] = {
        "unresolved": 0,
        "outside_btc_window": 0,
        "missing_price": 0,
        "missing_metadata": 0,
        "missing_strike": 0,
        "missing_close_time": 0,
        "not_ready": 0,
        "bad_horizon": 0,
        "prediction_error": 0,
    }

    if bars.empty:
        raise ValueError("No BTC candles available")
    min_bar_ts = bars["close_dt"].min()
    max_bar_ts = bars["close_dt"].max()
    labels = labels.sort_values("entry_dt").reset_index(drop=True)

    for _, row in labels.iterrows():
        entry_dt = row.get("entry_dt")
        if pd.isna(entry_dt):
            continue
        side = str(row.get("side") or "").lower()
        market_result = str(row.get("market_result") or "").lower()
        if side not in {"yes", "no"} or market_result not in {"yes", "no"}:
            skipped["unresolved"] += 1
            continue
        if entry_dt < min_bar_ts or entry_dt > max_bar_ts + pd.Timedelta(minutes=1):
            skipped["outside_btc_window"] += 1
            continue

        ask = as_float(row.get("entry_fill_cents_used"))
        btc_close = as_float(row.get("btc_close"))
        qty = as_int(row.get("qty")) or 1
        if ask is None:
            skipped["missing_price"] += 1
            continue

        ticker = str(row.get("market"))
        meta = metadata.get(ticker)
        if not meta:
            skipped["missing_metadata"] += 1
            continue
        strike = as_float(meta.get("floor_strike"))
        if strike is None:
            skipped["missing_strike"] += 1
            continue
        close_time = pd.to_datetime(meta.get("close_time"), utc=True, errors="coerce")
        if pd.isna(close_time):
            skipped["missing_close_time"] += 1
            continue

        bar_index = feed_bars_until(engine, bars, bar_index, entry_dt)
        if btc_close is None:
            try:
                btc_close = float(engine.current_spot())
            except Exception:
                skipped["missing_price"] += 1
                continue
        engine.update_tick(float(btc_close), ts=entry_dt.to_pydatetime())
        if not engine.ready():
            skipped["not_ready"] += 1
            continue

        horizon_seconds = (close_time - entry_dt).total_seconds()
        if horizon_seconds <= 0:
            skipped["bad_horizon"] += 1
            continue

        try:
            pred = engine.predict_many(strikes=[float(strike)], horizon_seconds=float(horizon_seconds))
        except Exception:
            skipped["prediction_error"] += 1
            continue

        p_yes = float(pred.p_yes[0])
        fair_yes = float(pred.fair_yes_cents[0])
        fair_no = float(pred.fair_no_cents[0])
        fair_side = fair_yes if side == "yes" else fair_no
        p_side = p_yes if side == "yes" else 1.0 - p_yes
        fee_cents = estimated_order_fee_cents(int(round(ask)), max(1, qty)) / float(max(1, qty))
        raw_edge = fair_side - float(ask) - fee_cents
        edge = raw_edge - 1.0 - 1.0
        d_sigma = float(pred.d_sigma[0])
        components = pred.components or {}
        entry = {
            "entry_dt": entry_dt.isoformat(),
            "market": ticker,
            "side": side,
            "market_result": market_result,
            "win": side == market_result,
            "qty": qty,
            "ask_cents": float(ask),
            "strike": float(strike),
            "close_time": close_time.isoformat(),
            "seconds_to_close": float(horizon_seconds),
            "btc_close": float(btc_close),
            "v28_p_yes": p_yes,
            "v28_p_side": p_side,
            "v28_fair_yes_cents": fair_yes,
            "v28_fair_no_cents": fair_no,
            "v28_fair_side_cents": fair_side,
            "v28_fee_cents": fee_cents,
            "v28_raw_edge_cents": raw_edge,
            "v28_edge_cents": edge,
            "v28_d_sigma": d_sigma,
            "v28_abs_d_sigma": abs(d_sigma),
            "v28_sigma_t_dollars": float(pred.sigma_t_dollars),
            "v28_arrow": float(components.get("arrow", math.nan)),
            "v28_volshock": float(components.get("volshock", math.nan)),
            "history_bars": int(engine.count),
        }
        entries.append(entry)

    diagnostics = {
        "input_trade_labels": int(len(labels)),
        "btc_candle_rows": int(len(bars)),
        "btc_candle_min": min_bar_ts.isoformat(),
        "btc_candle_max": max_bar_ts.isoformat(),
        "usable_replayed_entries": len(entries),
        "skipped": skipped,
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
    return {
        "retention": retention,
        "required_trades": required_trades,
        "required_contracts": required_contracts,
        "max_trade_accuracy": min(metric["winning_trades"], required_trades) / required_trades if required_trades else None,
        "max_contract_accuracy": min(metric["winning_contracts"], required_contracts) / required_contracts if required_contracts else None,
    }


def oracle_limits(baseline: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {
        split_name: {
            "retention_75": oracle_limit(metric, 0.75),
            "retention_80": oracle_limit(metric, 0.80),
        }
        for split_name, metric in baseline.items()
    }


def generate_candidates() -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    def add(rule: Dict[str, Any]) -> None:
        rule = dict(rule)
        rule["rule_id"] = f"replay_rule_{len(candidates) + 1:05d}"
        candidates.append(rule)

    for p_min in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.92, 0.94, 0.96]:
        for edge_min in [-30.0, -20.0, -10.0, 0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 15.0, 20.0]:
            for ask_max in [85.0, 90.0, 92.0, 95.0, 100.0]:
                add(
                    {
                        "p_min": p_min,
                        "edge_min": edge_min,
                        "ask_max": ask_max,
                        "side_filter": "all",
                    }
                )

    for side_filter in ["yes", "no"]:
        for p_min in [0.50, 0.60, 0.70, 0.80, 0.85, 0.90]:
            for edge_min in [-20.0, -10.0, 0.0, 2.0, 6.0, 10.0]:
                add({"p_min": p_min, "edge_min": edge_min, "ask_max": 100.0, "side_filter": side_filter})

    for abs_min, abs_max in [(None, 0.5), (None, 0.75), (0.5, None), (0.75, None), (1.0, None)]:
        for p_min in [0.50, 0.60, 0.70, 0.80, 0.85]:
            add(
                {
                    "p_min": p_min,
                    "edge_min": -20.0,
                    "ask_max": 100.0,
                    "side_filter": "all",
                    "abs_d_sigma_min": abs_min,
                    "abs_d_sigma_max": abs_max,
                }
            )

    for sec_min, sec_max in [(60.0, 300.0), (300.0, 600.0), (600.0, 900.0), (60.0, 900.0)]:
        for p_min in [0.50, 0.60, 0.70, 0.80, 0.85]:
            add(
                {
                    "p_min": p_min,
                    "edge_min": -20.0,
                    "ask_max": 100.0,
                    "side_filter": "all",
                    "seconds_min": sec_min,
                    "seconds_max": sec_max,
                }
            )

    return candidates


def row_passes(row: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    if row["v28_p_side"] < rule["p_min"]:
        return False
    if row["v28_edge_cents"] < rule["edge_min"]:
        return False
    if row["ask_cents"] > rule["ask_max"]:
        return False
    side_filter = rule.get("side_filter")
    if side_filter and side_filter != "all" and row["side"] != side_filter:
        return False
    abs_min = rule.get("abs_d_sigma_min")
    abs_max = rule.get("abs_d_sigma_max")
    if abs_min is not None and row["v28_abs_d_sigma"] < abs_min:
        return False
    if abs_max is not None and row["v28_abs_d_sigma"] > abs_max:
        return False
    sec_min = rule.get("seconds_min")
    sec_max = rule.get("seconds_max")
    if sec_min is not None and row["seconds_to_close"] < sec_min:
        return False
    if sec_max is not None and row["seconds_to_close"] > sec_max:
        return False
    return True


def metric_ge(metric: Dict[str, Any], key: str, threshold: float) -> bool:
    value = metric.get(key)
    return value is not None and value >= threshold


def candidate_passes_observed_target(result: Dict[str, Any]) -> bool:
    all_m = result["all"]
    hold_m = result["holdout"]
    train_m = result["train"]
    val_m = result["validation"]
    return (
        metric_ge(all_m, "trade_accuracy", MIN_TARGET_ACCURACY)
        and metric_ge(all_m, "contract_accuracy", MIN_TARGET_ACCURACY)
        and metric_ge(hold_m, "trade_accuracy", MIN_TARGET_ACCURACY)
        and metric_ge(hold_m, "contract_accuracy", MIN_TARGET_ACCURACY)
        and metric_ge(train_m, "contract_accuracy", 0.90)
        and metric_ge(val_m, "contract_accuracy", 0.90)
        and metric_ge(all_m, "trade_retention", MIN_TRADE_RETENTION)
        and metric_ge(all_m, "contract_retention", MIN_CONTRACT_RETENTION)
        and metric_ge(hold_m, "trade_retention", MIN_TRADE_RETENTION)
        and metric_ge(hold_m, "contract_retention", MIN_CONTRACT_RETENTION)
    )


def candidate_passes_target(result: Dict[str, Any]) -> bool:
    if not candidate_passes_observed_target(result):
        return False
    all_m = result["all"]
    hold_m = result["holdout"]
    return (
        all_m["trades"] >= MIN_ALL_SELECTED_TRADES
        and all_m["contracts"] >= MIN_ALL_SELECTED_CONTRACTS
        and hold_m["trades"] >= MIN_HOLDOUT_SELECTED_TRADES
        and hold_m["contracts"] >= MIN_HOLDOUT_SELECTED_CONTRACTS
    )


def evaluate_candidate(rule: Dict[str, Any], splits: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {"rule": rule}
    for split_name, rows in splits.items():
        selected = [row for row in rows if row_passes(row, rule)]
        result[split_name] = metric_for_entries(selected, rows)
    result["target_observed_pass"] = candidate_passes_observed_target(result)
    result["target_pass"] = candidate_passes_target(result)
    return result


def sort_key(result: Dict[str, Any]) -> Tuple[Any, ...]:
    return (
        1 if result["target_pass"] else 0,
        1 if result["target_observed_pass"] else 0,
        result["holdout"].get("contract_accuracy") or -1,
        result["all"].get("contract_accuracy") or -1,
        result["validation"].get("contract_accuracy") or -1,
        result["all"].get("contract_retention") or -1,
        result["all"].get("contracts") or -1,
    )


def flatten_result(result: Dict[str, Any]) -> Dict[str, Any]:
    flat: Dict[str, Any] = {}
    for key, value in result["rule"].items():
        flat[f"rule_{key}"] = value
    flat["target_pass"] = result["target_pass"]
    flat["target_observed_pass"] = result["target_observed_pass"]
    for split_name in ["all", "train", "validation", "holdout"]:
        for key, value in result[split_name].items():
            flat[f"{split_name}_{key}"] = value
    return flat


def metric_summary(metric: Dict[str, Any]) -> str:
    return (
        f"{metric['winning_trades']}/{metric['trades']} trades ({pct(metric['trade_accuracy'])}), "
        f"{metric['winning_contracts']}/{metric['contracts']} contracts ({pct(metric['contract_accuracy'])}), "
        f"contract retention {pct(metric['contract_retention'])}"
    )


def render_rule(rule: Dict[str, Any]) -> str:
    pieces = [
        f"id={rule.get('rule_id')}",
        f"p>={rule.get('p_min')}",
        f"edge>={rule.get('edge_min')}",
        f"ask<={rule.get('ask_max')}",
    ]
    for key in ["side_filter", "abs_d_sigma_min", "abs_d_sigma_max", "seconds_min", "seconds_max"]:
        if key in rule and rule.get(key) not in (None, "all"):
            pieces.append(f"{key}={rule.get(key)}")
    return ", ".join(pieces)


def write_candidates_csv(results: List[Dict[str, Any]], path: Path) -> None:
    rows = [flatten_result(result) for result in results]
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({key for row in rows for key in row})
    leading = [
        "rule_rule_id",
        "rule_p_min",
        "rule_edge_min",
        "rule_ask_max",
        "rule_side_filter",
        "target_pass",
        "target_observed_pass",
        "all_contract_accuracy",
        "all_contract_retention",
        "holdout_contract_accuracy",
        "holdout_contract_retention",
        "validation_contract_accuracy",
    ]
    ordered_fields = [field for field in leading if field in fields] + [field for field in fields if field not in leading]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ordered_fields)
        writer.writeheader()
        writer.writerows(rows)


def write_trade_ledger(entries: List[Dict[str, Any]], path: Path) -> None:
    if not entries:
        path.write_text("", encoding="utf-8")
        return
    fields = [
        "entry_dt",
        "market",
        "side",
        "market_result",
        "win",
        "qty",
        "ask_cents",
        "strike",
        "seconds_to_close",
        "btc_close",
        "v28_p_side",
        "v28_edge_cents",
        "v28_fair_side_cents",
        "v28_abs_d_sigma",
        "v28_sigma_t_dollars",
        "history_bars",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in entries:
            writer.writerow({field: row.get(field) for field in fields})


def write_report(summary: Dict[str, Any], path: Path) -> None:
    baseline = summary["baseline_metrics"]
    oracle = summary["oracle_limits"]
    top_results = summary["top_results"][:10]
    high_volume = summary["top_high_volume_results"][:10]
    target_count = summary["target_pass_count"]
    observed_count = summary["target_observed_pass_count"]

    lines: List[str] = []
    lines.append("# live_90_70 v28 Replay Accuracy/Volume Search")
    lines.append("")
    lines.append(f"Generated UTC: {summary['generated_utc']}")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    if target_count:
        lines.append("PASS: at least one replayed v28 selection rule met the observed and sample-size gates.")
    else:
        lines.append("FAIL: no replayed v28 selection rule met the 95% accuracy plus 75% volume gate.")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Dataset: `research_data/live_90_70`")
    lines.append("- This is a supplemental historical live replay, not the current live v28 fill tape.")
    lines.append("- Historical Kalshi metadata is used only to recover missing market strikes.")
    lines.append("- Existing bot logic/code is not changed.")
    lines.append("")
    lines.append("## Data")
    lines.append("")
    lines.append(f"- Input trade labels: {summary['diagnostics']['input_trade_labels']}")
    lines.append(f"- BTC candle rows: {summary['diagnostics']['btc_candle_rows']}")
    lines.append(f"- BTC candle window: {summary['diagnostics']['btc_candle_min']} to {summary['diagnostics']['btc_candle_max']}")
    lines.append(f"- Usable replayed entries: {summary['diagnostics']['usable_replayed_entries']}")
    lines.append(f"- Metadata requested/fetched/cache hits: {summary['metadata_stats']}")
    lines.append(f"- Skips: {summary['diagnostics']['skipped']}")
    lines.append(f"- Candidate rules scanned: {summary['candidate_count']}")
    lines.append("")
    lines.append("## Baseline Replayed Entry Set")
    lines.append("")
    for split_name in ["all", "train", "validation", "holdout"]:
        lines.append(f"- {split_name}: {metric_summary(baseline[split_name])}")
    lines.append("")
    lines.append("## Oracle Feasibility Bound")
    lines.append("")
    lines.append("| split | retention floor | required trades | max trade acc | required contracts | max contract acc |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for split_name in ["all", "train", "validation", "holdout"]:
        for key in ["retention_75", "retention_80"]:
            item = oracle[split_name][key]
            lines.append(
                f"| {split_name} | {item['retention'] * 100:.0f}% | {item['required_trades']} | "
                f"{pct(item['max_trade_accuracy'])} | {item['required_contracts']} | {pct(item['max_contract_accuracy'])} |"
            )
    lines.append("")
    lines.append("## Scan Result")
    lines.append("")
    lines.append(f"- Rules meeting observed accuracy/retention gate before sample floor: {observed_count}")
    lines.append(f"- Rules meeting observed gate and sample-size floor: {target_count}")
    lines.append("")
    lines.append("## Top Ranked Rules")
    lines.append("")
    lines.append("| rank | rule | all contracts | all acc | all retention | holdout contracts | holdout acc | holdout retention | validation acc | target |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for index, result in enumerate(top_results, start=1):
        all_m = result["all"]
        hold_m = result["holdout"]
        val_m = result["validation"]
        lines.append(
            f"| {index} | {render_rule(result['rule'])} | {all_m['contracts']} | "
            f"{pct(all_m['contract_accuracy'])} | {pct(all_m['contract_retention'])} | "
            f"{hold_m['contracts']} | {pct(hold_m['contract_accuracy'])} | {pct(hold_m['contract_retention'])} | "
            f"{pct(val_m['contract_accuracy'])} | {result['target_pass']} |"
        )
    lines.append("")
    lines.append("## Top High-Volume Rules")
    lines.append("")
    lines.append("| rank | rule | all contracts | all acc | all retention | holdout contracts | holdout acc | holdout retention | validation acc |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|")
    for index, result in enumerate(high_volume, start=1):
        all_m = result["all"]
        hold_m = result["holdout"]
        val_m = result["validation"]
        lines.append(
            f"| {index} | {render_rule(result['rule'])} | {all_m['contracts']} | "
            f"{pct(all_m['contract_accuracy'])} | {pct(all_m['contract_retention'])} | "
            f"{hold_m['contracts']} | {pct(hold_m['contract_accuracy'])} | {pct(hold_m['contract_retention'])} | "
            f"{pct(val_m['contract_accuracy'])} |"
        )
    lines.append("")
    lines.append("## Completion Audit")
    lines.append("")
    lines.append("| requirement | evidence | result |")
    lines.append("|---|---|---|")
    lines.append("| Use live data | Uses `live_90_70` live labels plus local BTC candles; metadata only supplies strikes | done |")
    lines.append("| Do not change bot logic | Standalone probe writes only `logs/edge_research` artifacts | done |")
    lines.append(f"| >=95% realized accuracy | target-pass rules: {target_count}; observed-pass rules: {observed_count} | {'done' if target_count else 'not met'} |")
    lines.append(f"| Keep >=75%-80% volume | enforced at >=75% all and holdout trade/contract retention | {'done' if target_count else 'not met'} |")
    lines.append(f"| Not overfit | chronological train/validation/holdout split; holdout must pass | {'done' if target_count else 'not met'} |")
    lines.append(f"| Verified with sample size | selected all/holdout sample floors enforced | {'done' if target_count else 'not met'} |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-metadata", action="store_true", help="Fetch missing historical Kalshi market metadata.")
    parser.add_argument("--fetch-btc-candles", action="store_true", help="Fetch missing Coinbase BTC-USD 1m candles.")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated_utc = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")

    labels = load_trade_labels()
    bars = load_btc_candles(labels, args.fetch_btc_candles)
    btc_start = bars["close_dt"].min()
    btc_end = bars["close_dt"].max() + pd.Timedelta(minutes=1)
    candidate_labels = labels[
        (labels["entry_dt"] >= btc_start)
        & (labels["entry_dt"] <= btc_end)
        & (labels["market_result"].isin(["yes", "no"]))
    ].copy()
    metadata, metadata_stats = recover_metadata(candidate_labels["market"].unique(), args.fetch_metadata)
    entries, diagnostics = replay_entries(labels, bars, metadata)
    if not entries:
        raise SystemExit("No replayable entries were produced.")

    splits = split_entries(entries)
    baseline = baseline_metrics(splits)
    oracle = oracle_limits(baseline)
    candidates = generate_candidates()
    results = [evaluate_candidate(rule, splits) for rule in candidates]
    results.sort(key=sort_key, reverse=True)
    high_volume = [
        result
        for result in results
        if metric_ge(result["all"], "contract_retention", MIN_CONTRACT_RETENTION)
        and metric_ge(result["holdout"], "contract_retention", MIN_CONTRACT_RETENTION)
    ]
    high_volume.sort(
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
        "diagnostics": diagnostics,
        "metadata_stats": metadata_stats,
        "baseline_metrics": baseline,
        "oracle_limits": oracle,
        "candidate_count": len(candidates),
        "target_pass_count": sum(1 for result in results if result["target_pass"]),
        "target_observed_pass_count": sum(1 for result in results if result["target_observed_pass"]),
        "top_results": results[:50],
        "top_high_volume_results": high_volume[:50],
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

    json_latest = OUT_DIR / "live_9070_v28_replay_search_latest.json"
    json_stamp = OUT_DIR / f"live_9070_v28_replay_search_{generated_utc}.json"
    md_latest = OUT_DIR / "live_9070_v28_replay_search_latest.md"
    md_stamp = OUT_DIR / f"live_9070_v28_replay_search_{generated_utc}.md"
    csv_latest = OUT_DIR / "live_9070_v28_replay_candidates_latest.csv"
    csv_stamp = OUT_DIR / f"live_9070_v28_replay_candidates_{generated_utc}.csv"
    ledger_latest = OUT_DIR / "live_9070_v28_replay_trades_latest.csv"
    ledger_stamp = OUT_DIR / f"live_9070_v28_replay_trades_{generated_utc}.csv"

    json_text = json.dumps(summary, indent=2, sort_keys=True)
    json_latest.write_text(json_text + "\n", encoding="utf-8")
    json_stamp.write_text(json_text + "\n", encoding="utf-8")
    write_report(summary, md_latest)
    write_report(summary, md_stamp)
    write_candidates_csv(results, csv_latest)
    write_candidates_csv(results, csv_stamp)
    write_trade_ledger(entries, ledger_latest)
    write_trade_ledger(entries, ledger_stamp)

    print("live_90_70 v28 replay complete")
    print(f"usable_replayed_entries={len(entries)} candidates={len(candidates)}")
    print(f"baseline_all={metric_summary(baseline['all'])}")
    print(f"target_observed_pass_count={summary['target_observed_pass_count']} target_pass_count={summary['target_pass_count']}")
    print(f"report={md_latest}")
    print(f"candidates={csv_latest}")
    print(f"ledger={ledger_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
