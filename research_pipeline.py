from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests

try:
    import duckdb
except Exception:  # pragma: no cover - optional parquet fallback
    duckdb = None

ROOT = Path(__file__).resolve().parent
MA_TZ = ZoneInfo("America/New_York")
BINANCE_KLINES_ENDPOINT = "https://data-api.binance.vision/api/v3/klines"
BTC_SPOT_SYMBOL = "BTCUSDT"
BTC_CANDLE_INTERVAL = "1m"
BTC_CANDLE_MS = 60_000
BTC_TA_WARMUP_MINUTES = 90
FEATURE_SET_VERSION = "research-lab-features-v3-online-neighbor"
_DUCKDB_CONN = duckdb.connect(database=":memory:") if duckdb is not None else None
PIPELINE_WARNINGS: list[dict[str, Any]] = []
MONTH_ABBR_TO_NUM = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}
MARKET_TICKER_RE = re.compile(
    r"^KXBTC15M\-(?P<yy>\d{2})(?P<mon>[A-Z]{3})(?P<day>\d{2})(?P<hour>\d{2})(?P<minute>\d{2})\-(?P<bucket>\d{2})$"
)


def dataset_paths(dataset_tag: str) -> dict[str, Path]:
    return {
        "research_root": ROOT / "research_data" / dataset_tag,
        "raw_root": ROOT / "research_data" / dataset_tag / "raw_events",
        "checkpoint_root": ROOT / "research_data" / dataset_tag / "book_checkpoints",
        "normalized_root": ROOT / "research_data" / dataset_tag / "normalized_events",
        "features_root": ROOT / "research_data" / dataset_tag / "features",
        "btc_spot_root": ROOT / "research_data" / dataset_tag / "btc_spot_candles",
        "trade_labels_root": ROOT / "research_data" / dataset_tag / "trade_labels",
        "metadata_root": ROOT / "research_data" / dataset_tag / "metadata",
        "trades_path": ROOT / "stats" / dataset_tag / "trades.csv",
        "execution_events_path": ROOT / "logs" / dataset_tag / "execution_events.ndjson",
    }


def parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_local_trade_ts(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %I:%M:%S %p"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(tzinfo=MA_TZ).astimezone(timezone.utc)
        except ValueError:
            continue
    return parse_dt(text)


def parse_market_close_from_ticker(market: str) -> datetime | None:
    m = MARKET_TICKER_RE.match(str(market or "").upper())
    if not m:
        return None
    year = 2000 + int(m.group("yy"))
    month = MONTH_ABBR_TO_NUM.get(m.group("mon"))
    if month is None:
        return None
    return datetime(
        year,
        month,
        int(m.group("day")),
        int(m.group("hour")),
        int(m.group("minute")),
        tzinfo=MA_TZ,
    ).astimezone(timezone.utc)


def safe_float(value: Any) -> float | None:
    if value in {None, "", "None"}:
        return None
    try:
        return float(value)
    except Exception:
        return None


def safe_int(value: Any) -> int | None:
    if value in {None, "", "None"}:
        return None
    try:
        return int(round(float(value)))
    except Exception:
        return None


def parse_level_quantity(level: Any) -> float | None:
    if isinstance(level, dict):
        for key in ("quantity_fp", "quantity", "qty_fp", "qty", "count_fp", "count", "delta_fp", "delta"):
            if key in level:
                return safe_float(level.get(key))
    if isinstance(level, (list, tuple)) and len(level) >= 2:
        return safe_float(level[1])
    return None


def parse_level_price(level: Any) -> int | None:
    if isinstance(level, dict):
        for key in ("price_cents", "price", "price_dollars", "yes_price", "no_price"):
            if key in level:
                return safe_int(level.get(key))
    if isinstance(level, (list, tuple)) and level:
        return safe_int(level[0])
    return None


def parse_snapshot_levels(raw_levels: Any) -> list[tuple[int, float]]:
    out: list[tuple[int, float]] = []
    if not isinstance(raw_levels, list):
        return out
    for level in raw_levels:
        price = parse_level_price(level)
        qty = parse_level_quantity(level)
        if price is None or qty is None:
            continue
        out.append((price, qty))
    return out


def iter_ndjson_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not root.exists():
        return rows
    for fp in sorted(root.rglob("*.ndjson")):
        with fp.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except Exception:
                    continue
                payload["_file_path"] = str(fp)
                rows.append(payload)
    return rows


def add_partition_columns(df: pd.DataFrame, root: Path, file_path: Path) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    try:
        relative_parts = file_path.relative_to(root).parts[:-1]
    except Exception:
        relative_parts = file_path.parts[:-1]
    for part in relative_parts:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        if key and key not in out.columns:
            out[key] = value
    return out


def load_parquet_tree(root: Path) -> pd.DataFrame:
    if not root.exists():
        return pd.DataFrame()
    files = sorted(root.rglob("*.parquet"))
    if not files:
        return pd.DataFrame()
    frames: list[pd.DataFrame] = []
    for fp in files:
        try:
            frame = pd.read_parquet(fp)
        except Exception:
            if _DUCKDB_CONN is None:
                continue
            try:
                frame = _DUCKDB_CONN.execute(
                    "SELECT * FROM read_parquet(?)",
                    [str(fp.resolve())],
                ).df()
            except Exception:
                continue
        frames.append(add_partition_columns(frame, root, fp))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def load_raw_events(raw_root: Path) -> pd.DataFrame:
    rows = iter_ndjson_rows(raw_root)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if "local_recv_ts" in df.columns:
        df["local_recv_dt"] = pd.to_datetime(df["local_recv_ts"], utc=True, errors="coerce")
    else:
        df["local_recv_dt"] = pd.NaT
    return df.sort_values(["local_recv_dt", "local_recv_ns"], na_position="last").reset_index(drop=True)


def load_checkpoint_events(checkpoint_root: Path) -> pd.DataFrame:
    rows = iter_ndjson_rows(checkpoint_root)
    if not rows:
        return pd.DataFrame()
    out: list[dict[str, Any]] = []
    for rec in rows:
        yes_prices = rec.get("yes_bid_prices") if isinstance(rec.get("yes_bid_prices"), list) else []
        yes_sizes = rec.get("yes_bid_sizes") if isinstance(rec.get("yes_bid_sizes"), list) else []
        no_prices = rec.get("no_bid_prices") if isinstance(rec.get("no_bid_prices"), list) else []
        no_sizes = rec.get("no_bid_sizes") if isinstance(rec.get("no_bid_sizes"), list) else []
        yes_best = safe_int(yes_prices[0]) if yes_prices else None
        no_best = safe_int(no_prices[0]) if no_prices else None
        out.append({
            "market_ticker": str(rec.get("market_ticker") or ""),
            "local_recv_dt": pd.to_datetime(rec.get("checkpoint_ts"), utc=True, errors="coerce"),
            "trust_state": "checkpoint",
            "yes_bid_cents": yes_best,
            "no_bid_cents": no_best,
            "yes_ask_cents": 100 - no_best if no_best is not None else None,
            "no_ask_cents": 100 - yes_best if yes_best is not None else None,
            "yes_bid_size": safe_float(yes_sizes[0]) if yes_sizes else None,
            "no_bid_size": safe_float(no_sizes[0]) if no_sizes else None,
            "snapshot_yes_depth_top3": float(sum(safe_float(x) or 0.0 for x in yes_sizes[:3])) if yes_sizes else None,
            "snapshot_no_depth_top3": float(sum(safe_float(x) or 0.0 for x in no_sizes[:3])) if no_sizes else None,
        })
    return pd.DataFrame(out)


def normalize_raw_events(raw_df: pd.DataFrame) -> pd.DataFrame:
    if raw_df.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for rec in raw_df.to_dict("records"):
        payload = rec.get("payload_json") if isinstance(rec.get("payload_json"), dict) else {}
        event_type = str(rec.get("event_type") or "")
        market = str(rec.get("market_ticker") or payload.get("market_ticker") or "")
        row = {
            "dataset_tag": rec.get("dataset_tag"),
            "run_id": rec.get("run_id"),
            "connection_id": rec.get("connection_id"),
            "event_type": event_type,
            "channel": rec.get("channel"),
            "market_ticker": market,
            "sequence_number": safe_int(rec.get("sequence_number")),
            "exchange_ts": rec.get("exchange_ts"),
            "local_recv_ts": rec.get("local_recv_ts"),
            "local_recv_dt": rec.get("local_recv_dt"),
            "trust_state": rec.get("trust_state"),
            "source": rec.get("source"),
            "yes_bid_cents": safe_int(payload.get("yes_bid")),
            "yes_ask_cents": safe_int(payload.get("yes_ask")),
            "no_bid_cents": safe_int(payload.get("no_bid")),
            "no_ask_cents": safe_int(payload.get("no_ask")),
            "yes_bid_size": safe_float(payload.get("yes_bid_size_fp") or payload.get("yes_bid_size")),
            "yes_ask_size": safe_float(payload.get("yes_ask_size_fp") or payload.get("yes_ask_size")),
            "no_bid_size": safe_float(payload.get("no_bid_size_fp") or payload.get("no_bid_size")),
            "no_ask_size": safe_float(payload.get("no_ask_size_fp") or payload.get("no_ask_size")),
            "delta_side": None,
            "delta_price_cents": None,
            "delta_qty": None,
            "snapshot_yes_best_bid": None,
            "snapshot_no_best_bid": None,
            "snapshot_yes_depth_top3": None,
            "snapshot_no_depth_top3": None,
        }
        if event_type == "orderbook_delta":
            row["delta_side"] = str(payload.get("side") or "").lower() or None
            row["delta_price_cents"] = safe_int(payload.get("price") or payload.get("price_cents"))
            row["delta_qty"] = safe_float(payload.get("delta_fp") or payload.get("delta"))
        elif event_type == "orderbook_snapshot":
            yes_levels = parse_snapshot_levels(payload.get("yes_dollars_fp") or payload.get("yes_dollars") or payload.get("yes") or [])
            no_levels = parse_snapshot_levels(payload.get("no_dollars_fp") or payload.get("no_dollars") or payload.get("no") or [])
            if yes_levels:
                yes_levels = sorted(yes_levels, key=lambda item: item[0], reverse=True)
                row["snapshot_yes_best_bid"] = yes_levels[0][0]
                row["snapshot_yes_depth_top3"] = float(sum(qty for _, qty in yes_levels[:3]))
            if no_levels:
                no_levels = sorted(no_levels, key=lambda item: item[0], reverse=True)
                row["snapshot_no_best_bid"] = no_levels[0][0]
                row["snapshot_no_depth_top3"] = float(sum(qty for _, qty in no_levels[:3]))
        close_dt = parse_market_close_from_ticker(market)
        local_dt = row["local_recv_dt"]
        row["seconds_to_close"] = (close_dt - local_dt.to_pydatetime()).total_seconds() if close_dt and pd.notna(local_dt) else np.nan
        rows.append(row)
    norm = pd.DataFrame(rows)
    return norm.sort_values(["local_recv_dt", "sequence_number"], na_position="last").reset_index(drop=True)


def floor_minute_utc(value: pd.Timestamp) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").floor("min")


def ceil_minute_utc(value: pd.Timestamp) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    ts = ts.tz_convert("UTC")
    floored = ts.floor("min")
    return floored if floored == ts else floored + pd.Timedelta(minutes=1)


def bucket_rsi_state(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "unknown"
    if value >= 70:
        return "overbought"
    if value >= 60:
        return "bullish"
    if value >= 40:
        return "neutral"
    if value >= 30:
        return "bearish"
    return "oversold"


def bucket_delta_state(value: float | None, *, fast: float, slow: float) -> str:
    if value is None or pd.isna(value):
        return "unknown"
    if value >= fast:
        return "rising_fast"
    if value >= slow:
        return "rising"
    if value <= -fast:
        return "falling_fast"
    if value <= -slow:
        return "falling"
    return "flat"


def bucket_macd_state(macd_line: float | None, signal_line: float | None) -> str:
    if macd_line is None or signal_line is None or pd.isna(macd_line) or pd.isna(signal_line):
        return "unknown"
    gap = float(macd_line) - float(signal_line)
    if gap >= 8.0:
        return "bullish"
    if gap <= -8.0:
        return "bearish"
    return "neutral"


def bucket_hist_state(hist: float | None, hist_change: float | None) -> str:
    if hist is None or hist_change is None or pd.isna(hist) or pd.isna(hist_change):
        return "unknown"
    hist = float(hist)
    hist_change = float(hist_change)
    if hist >= 6.0 and hist_change >= 1.5:
        return "positive_expanding"
    if hist >= 6.0:
        return "positive_fading"
    if hist <= -6.0 and hist_change <= -1.5:
        return "negative_expanding"
    if hist <= -6.0:
        return "negative_fading"
    return "flat"


def bucket_price_vs_ema_state(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "unknown"
    value = float(value)
    if value >= 50.0:
        return "above"
    if value <= -50.0:
        return "below"
    return "near"


def bucket_bps_move(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "unknown"
    value = float(value)
    if value >= 60:
        return "up_fast"
    if value >= 20:
        return "up"
    if value <= -60:
        return "down_fast"
    if value <= -20:
        return "down"
    return "flat"


def bucket_bps_range(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "unknown"
    value = float(value)
    if value <= 20:
        return "calm"
    if value <= 60:
        return "normal"
    return "fast"


def bucket_range_location(*, distance_to_high_bps: float | None, distance_to_low_bps: float | None) -> str:
    if (
        distance_to_high_bps is None
        or distance_to_low_bps is None
        or pd.isna(distance_to_high_bps)
        or pd.isna(distance_to_low_bps)
    ):
        return "unknown"
    high = float(distance_to_high_bps)
    low = float(distance_to_low_bps)
    if abs(high - low) <= 10:
        return "mid_range"
    if high < low:
        return "upper_range"
    return "lower_range"


def load_btc_spot_candles(root: Path) -> pd.DataFrame:
    frame = load_parquet_tree(root)
    if frame.empty:
        return frame
    for col in ("open_dt", "close_dt"):
        if col in frame.columns:
            frame[col] = pd.to_datetime(frame[col], utc=True, errors="coerce")
    numeric_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "move_1m_bps",
        "move_5m_bps",
        "move_15m_bps",
        "range_15m_dollars",
        "range_15m_bps",
        "distance_to_15m_high_bps",
        "distance_to_15m_low_bps",
        "rsi14",
        "rsi14_delta_3m",
        "macd_line",
        "macd_signal",
        "macd_hist",
        "macd_hist_delta_3m",
        "price_vs_ema21",
    ]
    for col in numeric_cols:
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    if "open_dt" in frame.columns:
        frame = frame.sort_values("open_dt").drop_duplicates(subset=["open_dt"], keep="last")
    return frame.reset_index(drop=True)


def fetch_binance_btc_spot_candles(start_dt: pd.Timestamp, end_dt: pd.Timestamp) -> pd.DataFrame:
    start_utc = floor_minute_utc(start_dt)
    end_utc = ceil_minute_utc(end_dt)
    start_ms = int(start_utc.timestamp() * 1000)
    end_ms = int(end_utc.timestamp() * 1000)
    if end_ms <= start_ms:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    cursor_ms = start_ms
    while cursor_ms < end_ms:
        response = requests.get(
            BINANCE_KLINES_ENDPOINT,
            params={
                "symbol": BTC_SPOT_SYMBOL,
                "interval": BTC_CANDLE_INTERVAL,
                "startTime": cursor_ms,
                "endTime": end_ms,
                "limit": 1000,
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list) or not payload:
            break
        for item in payload:
            if not isinstance(item, list) or len(item) < 7:
                continue
            open_ms = int(item[0])
            close_ms = int(item[6])
            rows.append(
                {
                    "symbol": BTC_SPOT_SYMBOL,
                    "interval": BTC_CANDLE_INTERVAL,
                    "open_dt": pd.to_datetime(open_ms, unit="ms", utc=True),
                    "close_dt": pd.to_datetime(close_ms, unit="ms", utc=True),
                    "open": float(item[1]),
                    "high": float(item[2]),
                    "low": float(item[3]),
                    "close": float(item[4]),
                    "volume": float(item[5]),
                    "source": "Binance public market data",
                }
            )
        last_open_ms = int(payload[-1][0])
        next_cursor_ms = last_open_ms + BTC_CANDLE_MS
        if next_cursor_ms <= cursor_ms:
            break
        cursor_ms = next_cursor_ms
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows)
    out = out.sort_values("open_dt").drop_duplicates(subset=["open_dt"], keep="last").reset_index(drop=True)
    return out


def add_btc_technical_columns(candles_df: pd.DataFrame) -> pd.DataFrame:
    if candles_df.empty:
        return candles_df
    out = candles_df.copy().sort_values("open_dt").reset_index(drop=True)
    closes = pd.to_numeric(out["close"], errors="coerce").astype("float64")
    highs = pd.to_numeric(out["high"], errors="coerce").astype("float64")
    lows = pd.to_numeric(out["low"], errors="coerce").astype("float64")

    delta = closes.diff()
    gain = delta.clip(lower=0).fillna(0.0)
    loss = (-delta.clip(upper=0)).fillna(0.0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    rs = avg_gain / avg_loss.replace(0.0, float("nan"))
    rsi = (100 - (100 / (1 + rs))).clip(lower=0, upper=100).fillna(50.0)

    ema12 = closes.ewm(span=12, adjust=False, min_periods=1).mean()
    ema26 = closes.ewm(span=26, adjust=False, min_periods=1).mean()
    macd_line = ema12 - ema26
    macd_signal = macd_line.ewm(span=9, adjust=False, min_periods=1).mean()
    macd_hist = macd_line - macd_signal
    ema21 = closes.ewm(span=21, adjust=False, min_periods=1).mean()

    out["move_1m_bps"] = ((closes - closes.shift(1)) / closes.shift(1).replace(0.0, float("nan"))) * 10000.0
    out["move_5m_bps"] = ((closes - closes.shift(5)) / closes.shift(5).replace(0.0, float("nan"))) * 10000.0
    out["move_15m_bps"] = ((closes - closes.shift(15)) / closes.shift(15).replace(0.0, float("nan"))) * 10000.0
    rolling_high_15m = highs.rolling(15, min_periods=1).max()
    rolling_low_15m = lows.rolling(15, min_periods=1).min()
    out["range_15m_dollars"] = rolling_high_15m - rolling_low_15m
    out["range_15m_bps"] = (out["range_15m_dollars"] / closes.replace(0.0, float("nan"))) * 10000.0
    out["distance_to_15m_high_bps"] = ((rolling_high_15m - closes) / closes.replace(0.0, float("nan"))) * 10000.0
    out["distance_to_15m_low_bps"] = ((closes - rolling_low_15m) / closes.replace(0.0, float("nan"))) * 10000.0
    out["rsi14"] = rsi
    out["rsi14_delta_3m"] = rsi - rsi.shift(3)
    out["macd_line"] = macd_line
    out["macd_signal"] = macd_signal
    out["macd_hist"] = macd_hist
    out["macd_hist_delta_3m"] = macd_hist - macd_hist.shift(3)
    out["price_vs_ema21"] = closes - ema21
    out["price_zone_15m"] = [
        bucket_range_location(distance_to_high_bps=high_val, distance_to_low_bps=low_val)
        for high_val, low_val in zip(out["distance_to_15m_high_bps"], out["distance_to_15m_low_bps"])
    ]
    out["move_1m_state"] = out["move_1m_bps"].map(bucket_bps_move)
    out["move_5m_state"] = out["move_5m_bps"].map(bucket_bps_move)
    out["move_15m_state"] = out["move_15m_bps"].map(bucket_bps_move)
    out["range_15m_state"] = out["range_15m_bps"].map(bucket_bps_range)
    out["rsi14_state"] = out["rsi14"].map(bucket_rsi_state)
    out["rsi14_slope_state"] = out["rsi14_delta_3m"].map(lambda value: bucket_delta_state(value, fast=6.0, slow=1.5))
    out["macd_state"] = [
        bucket_macd_state(macd_val, signal_val)
        for macd_val, signal_val in zip(out["macd_line"], out["macd_signal"])
    ]
    out["macd_hist_state"] = [
        bucket_hist_state(hist_val, delta_val)
        for hist_val, delta_val in zip(out["macd_hist"], out["macd_hist_delta_3m"])
    ]
    out["price_vs_ema21_state"] = out["price_vs_ema21"].map(bucket_price_vs_ema_state)
    out["day"] = out["close_dt"].dt.strftime("%Y-%m-%d")
    return out


def build_btc_spot_feature_table(btc_spot_root: Path, features_df: pd.DataFrame) -> pd.DataFrame:
    if features_df.empty or "ts" not in features_df.columns:
        return pd.DataFrame()
    ts = pd.to_datetime(features_df["ts"], utc=True, errors="coerce")
    ts = ts[ts.notna()]
    if ts.empty:
        return pd.DataFrame()
    required_start = floor_minute_utc(ts.min() - pd.Timedelta(minutes=BTC_TA_WARMUP_MINUTES))
    required_end = ceil_minute_utc(ts.max() + pd.Timedelta(minutes=2))

    existing = load_btc_spot_candles(btc_spot_root)
    fetch_windows: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    if existing.empty:
        fetch_windows.append((required_start, required_end))
    else:
        existing_min = pd.to_datetime(existing["open_dt"], utc=True, errors="coerce").min()
        existing_max = pd.to_datetime(existing["close_dt"], utc=True, errors="coerce").max()
        if pd.isna(existing_min) or pd.isna(existing_max):
            fetch_windows.append((required_start, required_end))
        else:
            if required_start < existing_min:
                fetch_windows.append((required_start, existing_min))
            refresh_start = max(required_start, existing_max - pd.Timedelta(minutes=BTC_TA_WARMUP_MINUTES))
            if required_end > existing_max:
                fetch_windows.append((refresh_start, required_end))

    fetched_frames: list[pd.DataFrame] = []
    for start_dt, end_dt in fetch_windows:
        if end_dt <= start_dt:
            continue
        try:
            fetched = fetch_binance_btc_spot_candles(start_dt, end_dt)
        except Exception as exc:
            PIPELINE_WARNINGS.append(
                {
                    "type": "btc_spot_fetch_failed",
                    "start_dt": pd.Timestamp(start_dt).isoformat(),
                    "end_dt": pd.Timestamp(end_dt).isoformat(),
                    "error": str(exc),
                    "fallback": "using_existing_cached_btc_spot_candles",
                }
            )
            continue
        if not fetched.empty:
            fetched_frames.append(fetched)

    combined = existing
    if fetched_frames:
        combined = (
            pd.concat([existing, *fetched_frames], ignore_index=True, sort=False)
            if not existing.empty
            else pd.concat(fetched_frames, ignore_index=True, sort=False)
        )
    if combined.empty:
        return combined
    combined = combined.sort_values("open_dt").drop_duplicates(subset=["open_dt"], keep="last").reset_index(drop=True)
    return add_btc_technical_columns(combined)


def attach_btc_spot_features(features_df: pd.DataFrame, btc_df: pd.DataFrame) -> pd.DataFrame:
    if features_df.empty or btc_df.empty:
        return features_df
    out = features_df.copy()
    out["ts"] = pd.to_datetime(out["ts"], utc=True, errors="coerce").astype("datetime64[ns, UTC]")
    btc_lookup = btc_df.copy()
    btc_lookup["close_dt"] = pd.to_datetime(btc_lookup["close_dt"], utc=True, errors="coerce").astype("datetime64[ns, UTC]")
    lookup_cols = [
        "close_dt",
        "close",
        "move_1m_bps",
        "move_5m_bps",
        "move_15m_bps",
        "range_15m_dollars",
        "range_15m_bps",
        "distance_to_15m_high_bps",
        "distance_to_15m_low_bps",
        "price_zone_15m",
        "move_1m_state",
        "move_5m_state",
        "move_15m_state",
        "range_15m_state",
        "rsi14",
        "rsi14_state",
        "rsi14_slope_state",
        "macd_line",
        "macd_signal",
        "macd_hist",
        "macd_state",
        "macd_hist_state",
        "price_vs_ema21",
        "price_vs_ema21_state",
    ]
    btc_lookup = btc_lookup[[col for col in lookup_cols if col in btc_lookup.columns]].sort_values("close_dt")
    merged = pd.merge_asof(
        out.sort_values("ts"),
        btc_lookup,
        left_on="ts",
        right_on="close_dt",
        direction="backward",
        tolerance=pd.Timedelta(minutes=2),
    )
    rename_map = {
        "close": "btc_close",
        "move_1m_bps": "btc_move_1m_bps",
        "move_5m_bps": "btc_move_5m_bps",
        "move_15m_bps": "btc_move_15m_bps",
        "range_15m_dollars": "btc_range_15m_dollars",
        "range_15m_bps": "btc_range_15m_bps",
        "distance_to_15m_high_bps": "btc_distance_to_15m_high_bps",
        "distance_to_15m_low_bps": "btc_distance_to_15m_low_bps",
        "price_zone_15m": "btc_price_zone_15m",
        "move_1m_state": "btc_move_1m_state",
        "move_5m_state": "btc_move_5m_state",
        "move_15m_state": "btc_move_15m_state",
        "range_15m_state": "btc_range_15m_state",
        "rsi14": "btc_rsi14",
        "rsi14_state": "btc_rsi14_state",
        "rsi14_slope_state": "btc_rsi14_slope_state",
        "macd_line": "btc_macd_line",
        "macd_signal": "btc_macd_signal",
        "macd_hist": "btc_macd_hist",
        "macd_state": "btc_macd_state",
        "macd_hist_state": "btc_macd_hist_state",
        "price_vs_ema21": "btc_price_vs_ema21",
        "price_vs_ema21_state": "btc_price_vs_ema21_state",
    }
    return merged.rename(columns=rename_map)


ONLINE_NEIGHBOR_COLUMNS = [
    "online_neighbor_yes_history_count",
    "online_neighbor_yes_win_rate",
    "online_neighbor_yes_model_ev_cents",
    "online_neighbor_yes_lcb_cents",
    "online_neighbor_no_history_count",
    "online_neighbor_no_win_rate",
    "online_neighbor_no_model_ev_cents",
    "online_neighbor_no_lcb_cents",
]


def infer_feature_market_result(grp: pd.DataFrame, close_dt: datetime | None) -> str | None:
    if grp.empty:
        return None
    ordered = grp.sort_values("ts")
    close_ts = pd.Timestamp(close_dt) if close_dt is not None else None
    if close_ts is not None:
        after_close = ordered[ordered["ts"] >= close_ts]
        if not after_close.empty:
            ordered = after_close
    row = ordered.iloc[-1]
    yes_bid = safe_float(row.get("yes_bid_cents"))
    no_bid = safe_float(row.get("no_bid_cents"))
    yes_ask = safe_float(row.get("yes_ask_cents"))
    no_ask = safe_float(row.get("no_ask_cents"))
    if yes_bid is not None and yes_bid >= 99:
        return "yes"
    if no_bid is not None and no_bid >= 99:
        return "no"
    if yes_ask is not None and yes_ask <= 1 and no_bid is not None and no_bid >= 95:
        return "no"
    if no_ask is not None and no_ask <= 1 and yes_bid is not None and yes_bid >= 95:
        return "yes"
    if yes_bid is not None and no_bid is not None:
        return "yes" if yes_bid > no_bid else "no"
    return None


def neighbor_bucket(side: str, seconds_to_close: Any, limit: Any, pressure: Any) -> tuple[str, int, int, int] | None:
    seconds = safe_float(seconds_to_close)
    limit_cents = safe_float(limit)
    pressure_value = safe_float(pressure)
    if side not in {"yes", "no"} or seconds is None or limit_cents is None or pressure_value is None:
        return None
    if math.isnan(seconds) or math.isnan(limit_cents) or math.isnan(pressure_value):
        return None
    seconds_bucket = int(max(0, min(15, math.floor(seconds / 60.0))))
    limit_bucket = int(max(0, min(50, math.floor(limit_cents / 2.0))))
    pressure_bucket = int(max(0, min(10, math.floor(pressure_value * 10.0))))
    return side, seconds_bucket, limit_bucket, pressure_bucket


def neighbor_keys_around(bucket: tuple[str, int, int, int]) -> list[tuple[str, int, int, int]]:
    side, seconds_bucket, limit_bucket, pressure_bucket = bucket
    keys: list[tuple[str, int, int, int]] = []
    seen: set[tuple[str, int, int, int]] = set()
    for ds in (-1, 0, 1):
        for dl in (-1, 0, 1):
            for dp in (-1, 0, 1):
                key = (
                    side,
                    max(0, min(15, seconds_bucket + ds)),
                    max(0, min(50, limit_bucket + dl)),
                    max(0, min(10, pressure_bucket + dp)),
                )
                if key not in seen:
                    seen.add(key)
                    keys.append(key)
    return keys


def add_online_neighbor_features(features: pd.DataFrame) -> pd.DataFrame:
    out = features.copy()
    for col in ONLINE_NEIGHBOR_COLUMNS:
        out[col] = np.nan
    if out.empty or "market_ticker" not in out.columns or "ts" not in out.columns:
        return out

    out["ts"] = pd.to_datetime(out["ts"], utc=True, errors="coerce")
    market_closes = {market: parse_market_close_from_ticker(str(market)) for market in out["market_ticker"].dropna().unique()}
    history: dict[tuple[str, int, int, int], list[float]] = defaultdict(lambda: [0.0, 0.0])

    ordered_markets = sorted(
        [market for market in market_closes if market_closes[market] is not None],
        key=lambda market: market_closes[market] or datetime.max.replace(tzinfo=timezone.utc),
    )
    for market in ordered_markets:
        grp = out[out["market_ticker"] == market].sort_values("ts")
        if grp.empty:
            continue

        side_values: dict[str, dict[str, list[float]]] = {
            "yes": {"count": [], "win_rate": [], "model_ev": [], "lcb": []},
            "no": {"count": [], "win_rate": [], "model_ev": [], "lcb": []},
        }
        for _, row in grp.iterrows():
            for side in ("yes", "no"):
                bucket = neighbor_bucket(
                    side,
                    row.get("seconds_to_close"),
                    row.get(f"{side}_entry_limit_cents"),
                    row.get(f"{side}_opponent_pressure"),
                )
                count = 0.0
                wins = 0.0
                if bucket is not None:
                    for key in neighbor_keys_around(bucket):
                        prior = history.get(key)
                        if prior is None:
                            continue
                        count += prior[0]
                        wins += prior[1]
                limit_cents = safe_float(row.get(f"{side}_entry_limit_cents")) or 0.0
                if count > 0:
                    win_rate = wins / count
                    stderr = math.sqrt(max(0.0, win_rate * (1.0 - win_rate)) / count)
                    lcb_win_rate = max(0.0, win_rate - 0.5 * stderr)
                    model_ev = win_rate * 100.0 - limit_cents
                    lcb = lcb_win_rate * 100.0 - limit_cents
                else:
                    win_rate = np.nan
                    model_ev = np.nan
                    lcb = np.nan
                side_values[side]["count"].append(count)
                side_values[side]["win_rate"].append(win_rate)
                side_values[side]["model_ev"].append(model_ev)
                side_values[side]["lcb"].append(lcb)

        for side in ("yes", "no"):
            out.loc[grp.index, f"online_neighbor_{side}_history_count"] = side_values[side]["count"]
            out.loc[grp.index, f"online_neighbor_{side}_win_rate"] = side_values[side]["win_rate"]
            out.loc[grp.index, f"online_neighbor_{side}_model_ev_cents"] = side_values[side]["model_ev"]
            out.loc[grp.index, f"online_neighbor_{side}_lcb_cents"] = side_values[side]["lcb"]

        outcome = infer_feature_market_result(grp, market_closes.get(market))
        if outcome not in {"yes", "no"}:
            continue
        sampled = grp.iloc[::15]
        for _, row in sampled.iterrows():
            for side in ("yes", "no"):
                bucket = neighbor_bucket(
                    side,
                    row.get("seconds_to_close"),
                    row.get(f"{side}_entry_limit_cents"),
                    row.get(f"{side}_opponent_pressure"),
                )
                if bucket is None:
                    continue
                history[bucket][0] += 1.0
                history[bucket][1] += 1.0 if outcome == side else 0.0

    return out


def build_feature_table(normalized_df: pd.DataFrame, checkpoint_df: pd.DataFrame | None = None) -> pd.DataFrame:
    if normalized_df.empty and (checkpoint_df is None or checkpoint_df.empty):
        return pd.DataFrame()
    quote_frames: list[pd.DataFrame] = []
    if not normalized_df.empty:
        quote_frames.append(normalized_df.copy())
    if checkpoint_df is not None and not checkpoint_df.empty:
        quote_frames.append(checkpoint_df.copy())
    quote_df = pd.concat(quote_frames, ignore_index=True, sort=False)
    quote_df = quote_df[quote_df["market_ticker"].astype(str) != ""].copy()
    quote_df["yes_bid_cents"] = quote_df["yes_bid_cents"].fillna(quote_df["snapshot_yes_best_bid"])
    quote_df["no_bid_cents"] = quote_df["no_bid_cents"].fillna(quote_df["snapshot_no_best_bid"])
    quote_df["yes_ask_cents"] = quote_df["yes_ask_cents"].fillna(100 - quote_df["no_bid_cents"])
    quote_df["no_ask_cents"] = quote_df["no_ask_cents"].fillna(100 - quote_df["yes_bid_cents"])
    quote_df["yes_bid_size"] = quote_df["yes_bid_size"].fillna(quote_df["snapshot_yes_depth_top3"])
    quote_df["no_bid_size"] = quote_df["no_bid_size"].fillna(quote_df["snapshot_no_depth_top3"])
    quote_df = quote_df[quote_df["local_recv_dt"].notna()].copy()
    quote_df = quote_df[
        quote_df[["yes_bid_cents", "yes_ask_cents", "no_bid_cents", "no_ask_cents"]].notna().any(axis=1)
    ].copy()
    if quote_df.empty:
        return pd.DataFrame()

    feature_frames: list[pd.DataFrame] = []
    for market, grp in quote_df.groupby("market_ticker"):
        grp = grp.sort_values("local_recv_dt").copy()
        event_states = grp[
            [
                "local_recv_dt",
                "trust_state",
                "yes_bid_cents",
                "yes_ask_cents",
                "no_bid_cents",
                "no_ask_cents",
                "yes_bid_size",
                "no_bid_size",
            ]
        ].drop_duplicates(subset=["local_recv_dt"], keep="last")
        start = event_states["local_recv_dt"].min().floor("s")
        end = event_states["local_recv_dt"].max().ceil("s")
        if pd.isna(start) or pd.isna(end):
            continue
        grid = pd.DataFrame({"ts": pd.date_range(start=start, end=end, freq="1s", tz="UTC")})
        merged = pd.merge_asof(
            grid.sort_values("ts"),
            event_states.sort_values("local_recv_dt"),
            left_on="ts",
            right_on="local_recv_dt",
            direction="backward",
        )
        merged["market_ticker"] = market
        close_dt = parse_market_close_from_ticker(market)
        if close_dt is not None:
            merged["seconds_to_close"] = (pd.Timestamp(close_dt) - merged["ts"]).dt.total_seconds()
        merged["spread_yes"] = merged["yes_ask_cents"] - merged["yes_bid_cents"]
        merged["spread_no"] = merged["no_ask_cents"] - merged["no_bid_cents"]
        denom = merged["yes_bid_size"].fillna(0.0) + merged["no_bid_size"].fillna(0.0)
        merged["depth_imbalance"] = np.where(
            denom > 0,
            (merged["yes_bid_size"].fillna(0.0) - merged["no_bid_size"].fillna(0.0)) / denom,
            np.nan,
        )
        merged["feature_available_at"] = merged["ts"]
        merged["quote_age_ms"] = (merged["ts"] - merged["local_recv_dt"]).dt.total_seconds() * 1000.0
        merged["quote_age_ms"] = merged["quote_age_ms"].where(merged["quote_age_ms"] >= 0, np.nan)
        merged["bid_sum_cents"] = merged["yes_bid_cents"].astype(float) + merged["no_bid_cents"].astype(float)
        merged["yes_opponent_pressure"] = np.where(
            merged["bid_sum_cents"] > 0,
            merged["no_bid_cents"].astype(float) / merged["bid_sum_cents"],
            np.nan,
        )
        merged["no_opponent_pressure"] = np.where(
            merged["bid_sum_cents"] > 0,
            merged["yes_bid_cents"].astype(float) / merged["bid_sum_cents"],
            np.nan,
        )
        merged["yes_entry_limit_cents"] = merged["yes_ask_cents"]
        merged["no_entry_limit_cents"] = merged["no_ask_cents"]
        merged["yes_implied_ask_size"] = merged["no_bid_size"]
        merged["no_implied_ask_size"] = merged["yes_bid_size"]
        for size in (2, 5, 10):
            merged[f"yes_fillable_size{size}_at_top"] = merged["yes_implied_ask_size"].fillna(0.0) >= float(size)
            merged[f"no_fillable_size{size}_at_top"] = merged["no_implied_ask_size"].fillna(0.0) >= float(size)
        for side in ("yes", "no"):
            series = merged[f"{side}_bid_cents"].astype(float)
            merged[f"{side}_range_5s"] = series.rolling(5, min_periods=1).max() - series.rolling(5, min_periods=1).min()
            merged[f"{side}_range_30s"] = series.rolling(30, min_periods=1).max() - series.rolling(30, min_periods=1).min()
            merged[f"{side}_range_60s"] = series.rolling(60, min_periods=1).max() - series.rolling(60, min_periods=1).min()
            merged[f"{side}_move_5s"] = series - series.shift(5)
            merged[f"{side}_move_30s"] = series - series.shift(30)
            merged[f"{side}_move_60s"] = series - series.shift(60)
        feature_frames.append(merged)
    if not feature_frames:
        return pd.DataFrame()
    features = pd.concat(feature_frames, ignore_index=True)
    features = add_online_neighbor_features(features)
    features["day"] = features["ts"].dt.strftime("%Y-%m-%d")
    return features


def load_execution_events(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["ts_dt"] = pd.to_datetime(df.get("ts_wall"), utc=True, errors="coerce")
    return df.sort_values("ts_dt").reset_index(drop=True)


def build_trade_labels(trades_path: Path, execution_events_path: Path, dataset_tag: str, features_df: pd.DataFrame | None = None) -> pd.DataFrame:
    if not trades_path.exists():
        return pd.DataFrame()
    trades = pd.read_csv(trades_path)
    if trades.empty:
        return trades
    trades["entry_dt"] = trades.get("entry_ts").map(parse_local_trade_ts)
    trades["exit_dt"] = trades.get("exit_ts").map(parse_local_trade_ts)
    trades["entry_dt"] = pd.to_datetime(trades["entry_dt"], utc=True, errors="coerce")
    trades["exit_dt"] = pd.to_datetime(trades["exit_dt"], utc=True, errors="coerce")
    trades["market"] = trades.get("market", "").fillna("").astype(str)
    trades["side"] = trades.get("side", "").fillna("").astype(str)
    execution = load_execution_events(execution_events_path)
    signal_events = execution[execution.get("event_type", "") == "signal_seen"].copy() if not execution.empty else pd.DataFrame()
    submit_events = execution[execution.get("event_type", "") == "order_submit_success"].copy() if not execution.empty else pd.DataFrame()

    signal_map: dict[tuple[str, str], pd.DataFrame] = {}
    submit_map: dict[tuple[str, str], pd.DataFrame] = {}
    for frame, target in ((signal_events, signal_map), (submit_events, submit_map)):
        if frame.empty:
            continue
        frame["market"] = frame.get("market", "").fillna("").astype(str)
        frame["side"] = frame.get("side", "").fillna("").astype(str)
        for key, grp in frame.groupby(["market", "side"]):
            target[key] = grp.sort_values("ts_dt")

    labels: list[dict[str, Any]] = []
    for rec in trades.to_dict("records"):
        row = dict(rec)
        entry_dt = rec.get("entry_dt")
        market = str(rec.get("market") or "")
        side = str(rec.get("side") or "")
        key = (market, side)
        signal_match = None
        submit_match = None
        if pd.notna(entry_dt) and key in signal_map:
            grp = signal_map[key]
            window = grp[(grp["ts_dt"] >= entry_dt - pd.Timedelta(seconds=10)) & (grp["ts_dt"] <= entry_dt + pd.Timedelta(seconds=10))]
            if not window.empty:
                signal_match = window.iloc[(window["ts_dt"] - entry_dt).abs().argmin()]
        if pd.notna(entry_dt) and key in submit_map:
            grp = submit_map[key]
            window = grp[(grp["ts_dt"] >= entry_dt - pd.Timedelta(seconds=10)) & (grp["ts_dt"] <= entry_dt + pd.Timedelta(seconds=10))]
            if not window.empty:
                submit_match = window.iloc[(window["ts_dt"] - entry_dt).abs().argmin()]
        row["dataset_tag"] = dataset_tag
        row["hold_duration_s"] = (rec.get("exit_dt") - entry_dt).total_seconds() if pd.notna(rec.get("exit_dt")) and pd.notna(entry_dt) else np.nan
        row["feed_age_ms_at_entry"] = signal_match.get("feed_age_ms") if signal_match is not None else np.nan
        row["book_age_ms_at_entry"] = signal_match.get("book_age_ms") if signal_match is not None else np.nan
        row["local_reaction_ms_at_entry"] = signal_match.get("local_reaction_ms") if signal_match is not None else np.nan
        row["submit_latency_ms"] = submit_match.get("submit_latency_ms") if submit_match is not None else np.nan
        row["auth_prep_ms"] = submit_match.get("auth_prep_ms") if submit_match is not None else np.nan
        row["http_roundtrip_ms"] = submit_match.get("http_roundtrip_ms") if submit_match is not None else np.nan
        row["json_parse_ms"] = submit_match.get("json_parse_ms") if submit_match is not None else np.nan
        labels.append(row)
    out = pd.DataFrame(labels)
    if out.empty:
        return out
    if features_df is not None and not features_df.empty and "market_ticker" in features_df.columns and "ts" in features_df.columns:
        feature_cols = [
            "market_ticker",
            "ts",
            "seconds_to_close",
            "depth_imbalance",
            "yes_range_30s",
            "yes_range_60s",
            "yes_move_30s",
            "yes_move_60s",
            "no_range_30s",
            "no_range_60s",
            "no_move_30s",
            "no_move_60s",
            "btc_close",
            "btc_move_1m_bps",
            "btc_move_5m_bps",
            "btc_move_15m_bps",
            "btc_range_15m_dollars",
            "btc_range_15m_bps",
            "btc_distance_to_15m_high_bps",
            "btc_distance_to_15m_low_bps",
            "btc_price_zone_15m",
            "btc_move_1m_state",
            "btc_move_5m_state",
            "btc_move_15m_state",
            "btc_range_15m_state",
            "btc_rsi14",
            "btc_rsi14_state",
            "btc_rsi14_slope_state",
            "btc_macd_line",
            "btc_macd_signal",
            "btc_macd_hist",
            "btc_macd_state",
            "btc_macd_hist_state",
            "btc_price_vs_ema21",
            "btc_price_vs_ema21_state",
        ]
        available_cols = [col for col in feature_cols if col in features_df.columns]
        feature_lookup = features_df[available_cols].copy()
        feature_lookup = feature_lookup.sort_values(["market_ticker", "ts"])
        out = out.sort_values(["market", "entry_dt"]).copy()
        merged_frames: list[pd.DataFrame] = []
        for market, grp in out.groupby("market", dropna=False):
            chunk = grp.sort_values("entry_dt").copy()
            market_feat = feature_lookup[feature_lookup["market_ticker"] == str(market)].sort_values("ts").copy()
            if market_feat.empty:
                merged_frames.append(chunk)
                continue
            merged = pd.merge_asof(
                chunk,
                market_feat,
                left_on="entry_dt",
                right_on="ts",
                direction="backward",
                tolerance=pd.Timedelta(seconds=2),
            )
            merged_frames.append(merged)
        out = pd.concat(merged_frames, ignore_index=True) if merged_frames else out
        yes_mask = out["side"].astype(str).str.lower().eq("yes")
        out["same_side_range_30s"] = np.where(yes_mask, out.get("yes_range_30s"), out.get("no_range_30s"))
        out["same_side_range_60s"] = np.where(yes_mask, out.get("yes_range_60s"), out.get("no_range_60s"))
        out["same_side_move_30s"] = np.where(yes_mask, out.get("yes_move_30s"), out.get("no_move_30s"))
        out["same_side_move_60s"] = np.where(yes_mask, out.get("yes_move_60s"), out.get("no_move_60s"))
        out = out.drop(columns=[col for col in ["market_ticker", "ts"] if col in out.columns], errors="ignore")
    if "entry_dt" in out.columns:
        out["day"] = out["entry_dt"].dt.strftime("%Y-%m-%d")
    return out


def write_partitioned_parquet(df: pd.DataFrame, root: Path, partition_cols: list[str], stem: str) -> int:
    if df.empty:
        return 0
    count = 0
    grouped = [((), df)]
    if partition_cols:
        working = df.copy()
        for col in partition_cols:
            if col not in working.columns:
                working[col] = "unknown"
                continue
            working[col] = working[col].astype(object)
            working[col] = working[col].where(pd.notna(working[col]), "unknown")
            working[col] = working[col].replace({"": "unknown", "nan": "unknown", "NaT": "unknown", "None": "unknown"})
        grouped = list(working.groupby(partition_cols, dropna=False))
    for key, grp in grouped:
        if not isinstance(key, tuple):
            key = (key,)
        target_dir = root
        for col, value in zip(partition_cols, key):
            safe_value = "unknown" if value is None or (isinstance(value, float) and math.isnan(value)) else str(value)
            target_dir = target_dir / f"{col}={safe_value}"
        target_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{stem}.parquet"
        write_df = grp.drop(columns=[col for col in partition_cols if col in grp.columns], errors="ignore")
        table = pa.Table.from_pandas(write_df.reset_index(drop=True), preserve_index=False)
        pq.write_table(table, target_dir / file_name, compression="snappy")
        count += 1
    return count


def write_pipeline_status(
    paths: dict[str, Path],
    *,
    raw_df: pd.DataFrame,
    normalized_df: pd.DataFrame,
    features_df: pd.DataFrame,
    btc_spot_df: pd.DataFrame,
    trade_labels_df: pd.DataFrame,
    normalized_files: int,
    feature_files: int,
    btc_spot_files: int,
    trade_label_files: int,
) -> None:
    paths["metadata_root"].mkdir(parents=True, exist_ok=True)
    payload = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "raw_event_rows": int(len(raw_df)),
        "normalized_rows": int(len(normalized_df)),
        "feature_rows": int(len(features_df)),
        "btc_spot_rows": int(len(btc_spot_df)),
        "trade_label_rows": int(len(trade_labels_df)),
        "normalized_file_count": int(normalized_files),
        "feature_file_count": int(feature_files),
        "btc_spot_file_count": int(btc_spot_files),
        "trade_label_file_count": int(trade_label_files),
        "feature_set_version": FEATURE_SET_VERSION,
        "latest_raw_event_ts": raw_df["local_recv_ts"].dropna().max() if not raw_df.empty and "local_recv_ts" in raw_df.columns else None,
        "latest_feature_ts": features_df["ts"].max().isoformat() if not features_df.empty and "ts" in features_df.columns else None,
        "latest_btc_spot_close_dt": btc_spot_df["close_dt"].max().isoformat() if not btc_spot_df.empty and "close_dt" in btc_spot_df.columns else None,
        "warnings": PIPELINE_WARNINGS,
    }
    (paths["metadata_root"] / "pipeline_status.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_dataset(dataset_tag: str) -> dict[str, Any]:
    paths = dataset_paths(dataset_tag)
    paths["research_root"].mkdir(parents=True, exist_ok=True)
    raw_df = load_raw_events(paths["raw_root"])
    checkpoint_df = load_checkpoint_events(paths["checkpoint_root"])
    normalized_df = normalize_raw_events(raw_df)
    features_df = build_feature_table(normalized_df, checkpoint_df)
    btc_spot_df = build_btc_spot_feature_table(paths["btc_spot_root"], features_df)
    features_df = attach_btc_spot_features(features_df, btc_spot_df)
    trade_labels_df = build_trade_labels(paths["trades_path"], paths["execution_events_path"], dataset_tag, features_df)

    normalized_files = write_partitioned_parquet(normalized_df.assign(day=normalized_df["local_recv_dt"].dt.strftime("%Y-%m-%d")) if not normalized_df.empty else normalized_df, paths["normalized_root"], ["day"], "part-latest")
    feature_files = write_partitioned_parquet(features_df, paths["features_root"], ["day", "market_ticker"], "part-latest")
    btc_spot_files = write_partitioned_parquet(btc_spot_df, paths["btc_spot_root"], ["day"], "part-latest")
    trade_label_files = write_partitioned_parquet(trade_labels_df, paths["trade_labels_root"], ["day"], "part-latest")
    write_pipeline_status(
        paths,
        raw_df=raw_df,
        normalized_df=normalized_df,
        features_df=features_df,
        btc_spot_df=btc_spot_df,
        trade_labels_df=trade_labels_df,
        normalized_files=normalized_files,
        feature_files=feature_files,
        btc_spot_files=btc_spot_files,
        trade_label_files=trade_label_files,
    )
    return {
        "dataset_tag": dataset_tag,
        "raw_event_rows": int(len(raw_df)),
        "normalized_rows": int(len(normalized_df)),
        "feature_rows": int(len(features_df)),
        "btc_spot_rows": int(len(btc_spot_df)),
        "trade_label_rows": int(len(trade_labels_df)),
        "normalized_files": int(normalized_files),
        "feature_files": int(feature_files),
        "btc_spot_files": int(btc_spot_files),
        "trade_label_files": int(trade_label_files),
        "feature_set_version": FEATURE_SET_VERSION,
    }


def drop_existing_btc_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    drop_cols = [col for col in df.columns if str(col).startswith("btc_")]
    drop_cols.extend([col for col in ("close_dt",) if col in df.columns])
    return df.drop(columns=drop_cols, errors="ignore")


def backfill_btc_spot_from_existing_features(dataset_tag: str) -> dict[str, Any]:
    paths = dataset_paths(dataset_tag)
    features_df = load_parquet_tree(paths["features_root"])
    if features_df.empty:
        return {
            "dataset_tag": dataset_tag,
            "status": "no_existing_features",
            "feature_rows": 0,
            "btc_spot_rows": 0,
            "trade_label_rows": 0,
        }
    features_df["ts"] = pd.to_datetime(features_df.get("ts"), utc=True, errors="coerce")
    features_df = features_df[features_df["ts"].notna()].copy()
    btc_spot_df = build_btc_spot_feature_table(paths["btc_spot_root"], features_df)
    enriched_features_df = attach_btc_spot_features(drop_existing_btc_columns(features_df), btc_spot_df)
    if not enriched_features_df.empty and "ts" in enriched_features_df.columns:
        enriched_features_df["day"] = pd.to_datetime(enriched_features_df["ts"], utc=True, errors="coerce").dt.strftime("%Y-%m-%d")
    if "market_ticker" in enriched_features_df.columns:
        enriched_features_df["market_ticker"] = enriched_features_df["market_ticker"].fillna("").astype(str)
    trade_labels_df = build_trade_labels(paths["trades_path"], paths["execution_events_path"], dataset_tag, enriched_features_df)

    feature_files = write_partitioned_parquet(enriched_features_df, paths["features_root"], ["day", "market_ticker"], "part-latest")
    btc_spot_files = write_partitioned_parquet(btc_spot_df, paths["btc_spot_root"], ["day"], "part-latest")
    trade_label_files = write_partitioned_parquet(trade_labels_df, paths["trade_labels_root"], ["day"], "part-latest")
    write_pipeline_status(
        paths,
        raw_df=pd.DataFrame(),
        normalized_df=pd.DataFrame(),
        features_df=enriched_features_df,
        btc_spot_df=btc_spot_df,
        trade_labels_df=trade_labels_df,
        normalized_files=0,
        feature_files=feature_files,
        btc_spot_files=btc_spot_files,
        trade_label_files=trade_label_files,
    )
    return {
        "dataset_tag": dataset_tag,
        "status": "btc_backfill_complete",
        "feature_rows": int(len(enriched_features_df)),
        "btc_spot_rows": int(len(btc_spot_df)),
        "trade_label_rows": int(len(trade_labels_df)),
        "feature_files": int(feature_files),
        "btc_spot_files": int(btc_spot_files),
        "trade_label_files": int(trade_label_files),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Phase 2 research datasets from recorded raw events.")
    parser.add_argument("--dataset", required=True, help="Dataset tag such as live_90_70")
    parser.add_argument("--btc-backfill-only", action="store_true", help="Backfill BTC spot candles and technical columns onto the existing feature dataset.")
    args = parser.parse_args()
    result = backfill_btc_spot_from_existing_features(args.dataset) if args.btc_backfill_only else build_dataset(args.dataset)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
