from __future__ import annotations
import base64
import html
import json
import math
import os
import re
import subprocess
import sys
from datetime import datetime
import time
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

ROOT = Path(__file__).resolve().parent
SCORE_SCRIPT = ROOT / "score_bot_log.py"
REFERENCE_DASHBOARD_ART_PATH = ROOT / "docs" / "dashboard_living_analytics_reference_generated_image_3.png"
USE_GENERATED_REFERENCE_ART_COCKPIT = False
SCORE_AUTO_REFRESH_MIN_INTERVAL_SECONDS = 6
SCORE_AUTO_REFRESH_STALE_GRACE_SECONDS = 2
MA_TZ = ZoneInfo("America/New_York")
BOT_ENTRY_CENTS = 90
BOT_EXIT_CENTS = 60
BOT_DELAY_SECONDS = 30
BOT_POSITION_SIZE = 2
DISPLAY_POSITION_SIZE = 10
KALSHI_TAKER_FEE_RATE = 0.07
MAX_OPTIMIZER_MARKETS = None
OPT_ENTRY_THRESHOLDS = tuple(range(90, 100))
OPT_STOP_THRESHOLDS = tuple(range(60, 90))
BTC_MAP_RANGE_OPTIONS = ("today", "yday_today", "week", "all")
EQUITY_RANGE_OPTIONS = ("1D", "1W", "1M", "3M", "YTD", "ALL")
SEED_FILTER_OPTIONS = ("ALL", "WIN", "LOSS", "FLAT")
BTC_MAP_RANGE_LABELS = {
    "today": "Today",
    "yday_today": "Yesterday + today",
    "week": "Last 7 days",
    "all": "All history",
}


@st.cache_data(show_spinner=False)
def reference_dashboard_art_data_uri(path_text: str) -> str:
    path = Path(path_text)
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def first_query_param(name: str) -> str:
    try:
        value = st.query_params.get(name, "")
    except Exception:
        return ""
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value or "")

HEARTBEAT_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+\s+\|\s+INFO\s+\|\s+Heartbeat \| "
    r"watch=(?P<watch>\S+) yes_bid=(?P<yes_bid>None|\d+) yes_ask=(?P<yes_ask>None|\d+) "
    r"no_bid=(?P<no_bid>None|\d+) no_ask=(?P<no_ask>None|\d+) book_ready=(?P<book_ready>True|False) "
    r"position=(?P<position>True|False) pending=(?P<pending>True|False) dry_run=(?P<dry_run>True|False)"
    r"(?:\s+trust=(?P<trust>\S+))?(?:\s+run_id=(?P<run_id>\S+))?$"
)
WATCH_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+\s+\|\s+INFO\s+\|\s+Watching market (?P<market>\S+) close_time=(?P<close_time>\S+) status=(?P<status>\S+)"
    r"(?:\s+run_id=(?P<run_id>\S+))?$"
)
ENTRY_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+\s+\|\s+INFO\s+\|\s+ENTRY signal \| "
    r"market=(?P<market>\S+) action=buy side=(?P<side>yes|no) trigger=(?P<trigger>\d+)c limit=(?P<limit>\d+)c qty=(?P<qty>\d+)"
)
EXIT_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+\s+\|\s+INFO\s+\|\s+EXIT signal \| "
    r"market=(?P<market>\S+) action=sell side=(?P<side>yes|no) trigger=(?P<trigger>\d+)c limit=(?P<limit>\d+)c qty=(?P<qty>\d+)"
)
LATENCY_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+\s+\|\s+INFO\s+\|\s+Latency \| purpose=(?P<purpose>\w+) feed_age_ms=(?P<feed_age_ms>[\d.]+) local_reaction_ms=(?P<local_reaction_ms>[\d.]+)"
)
LEVEL_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+\s+\|\s+(?P<level>INFO|WARNING|ERROR)\s+\|\s+(?P<msg>.*)$"
)
MARKET_TICKER_RE = re.compile(
    r"^KXBTC15M\-(?P<yy>\d{2})(?P<mon>[A-Z]{3})(?P<day>\d{2})(?P<hour>\d{2})(?P<minute>\d{2})\-(?P<bucket>\d{2})$"
)
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


def sanitize_strategy_tag(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "_", value.strip())
    return cleaned.strip("._-") or "default"


def live_dataset_tag_from_strategy_tag(tag: str) -> str:
    value = sanitize_strategy_tag(tag)
    mapping = {
        "entry_87_up_90_93_exact": "live_87_90_93_exact",
        "entry_87_ladder_hold": "live_87_77_67",
        "entry_95_late_momentum": "live_95_momentum",
        "entry_90_truffle_exit": "live_90_truffle_exit_size2",
        "entry_90_stop_70": "live_90_70",
        "entry_90_stop_78": "live_90_78",
    }
    return mapping.get(value, value)


def read_live_lock_strategy_tag() -> str | None:
    live_lock_path = ROOT / "state" / "live_trading.lock"
    if live_lock_path.exists():
        try:
            payload = json.loads(live_lock_path.read_text(encoding="utf-8", errors="ignore") or "{}")
            locked_tag = sanitize_strategy_tag(str(payload.get("strategy_tag") or ""))
            if locked_tag:
                return locked_tag
        except Exception:
            pass
    return None


def read_live_lock_payload() -> dict[str, Any]:
    live_lock_path = ROOT / "state" / "live_trading.lock"
    if not live_lock_path.exists():
        return {}
    try:
        payload = json.loads(live_lock_path.read_text(encoding="utf-8", errors="ignore") or "{}")
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def newest_live_log_source_tag() -> str | None:
    logs_root = ROOT / "logs"
    if not logs_root.exists():
        return None
    candidates = [p for p in logs_root.glob("live_*") if p.is_dir()]
    if not candidates:
        return None

    def _freshness(path: Path) -> float:
        observed = [path.stat().st_mtime]
        for child_name in ("bot.log", "execution_events.ndjson"):
            child = path / child_name
            if child.exists():
                observed.append(child.stat().st_mtime)
        return max(observed)

    return max(candidates, key=_freshness).name


def summary_log_source_tag(tag: str) -> str | None:
    summary_path = ROOT / "stats" / tag / "summary.json"
    if not summary_path.exists():
        return None
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8", errors="ignore") or "{}")
    except Exception:
        return None
    source_tag = sanitize_strategy_tag(str(payload.get("log_source_tag") or ""))
    return source_tag or None


def resolve_log_source_tag(tag: str, requested_source_tag: str | None = None) -> str:
    canonical = sanitize_strategy_tag(str(tag or "default"))
    configured_source = str(VIRTUAL_DATASET_CONFIGS.get(canonical, {}).get("source_tag", "") or "").strip()
    candidates: list[str] = []
    for value in [
        requested_source_tag,
        configured_source,
        summary_log_source_tag(canonical),
        canonical,
        f"live_{canonical}" if not canonical.startswith("live_") else None,
        canonical.removeprefix("live_") if canonical.startswith("live_") else None,
    ]:
        if not value:
            continue
        source = sanitize_strategy_tag(str(value))
        if source and source not in candidates:
            candidates.append(source)
    for source in candidates:
        log_dir = ROOT / "logs" / source
        if log_dir.exists() or (log_dir / "bot.log").exists() or (log_dir / "execution_events.ndjson").exists():
            return source
    return candidates[0] if candidates else canonical


def canonical_stats_tag_for_log_source(log_source_tag: str) -> str:
    source = sanitize_strategy_tag(log_source_tag)
    summary_matches: list[tuple[float, str]] = []
    stats_root = ROOT / "stats"
    if stats_root.exists():
        for child in stats_root.iterdir():
            if not child.is_dir():
                continue
            if child.name == source:
                return child.name
            summary_path = child / "summary.json"
            if not summary_path.exists():
                continue
            try:
                payload = json.loads(summary_path.read_text(encoding="utf-8", errors="ignore") or "{}")
            except Exception:
                continue
            if sanitize_strategy_tag(str(payload.get("log_source_tag") or "")) == source:
                summary_matches.append((summary_path.stat().st_mtime, child.name))
    if summary_matches:
        return max(summary_matches, key=lambda item: item[0])[1]
    if source.startswith("live_") and (ROOT / "stats" / source.removeprefix("live_")).exists():
        return source.removeprefix("live_")
    return source


def is_live_like_dataset(tag: str, log_source_tag: str | None = None) -> bool:
    raw_tag = sanitize_strategy_tag(str(tag or "")).lower()
    raw_source = sanitize_strategy_tag(str(log_source_tag or "")).lower()
    return raw_tag.startswith("live_") or raw_source.startswith("live_") or raw_tag.endswith("_live") or "_live_" in raw_tag


def build_dataset_record(
    tag: str,
    *,
    log_source_tag: str | None = None,
    label: str | None = None,
    score_mode: str | None = None,
    actuals_only: bool | None = None,
    is_live_default: bool = False,
) -> dict[str, Any]:
    canonical = sanitize_strategy_tag(str(tag or "default"))
    paths = dataset_paths(canonical, log_source_tag=log_source_tag)
    config = VIRTUAL_DATASET_CONFIGS.get(canonical, {})
    source = str(paths["log_source_tag"])
    resolved_score_mode = score_mode or str(config.get("score_mode") or ("live_only" if is_live_like_dataset(canonical, source) else "all"))
    if actuals_only is None:
        actuals_only = bool(config.get("actuals_only", is_live_like_dataset(canonical, source)))
    return {
        "tag": canonical,
        "label": label or str(config.get("label") or humanize_strategy_tag(canonical)),
        "log_source_tag": source,
        "source_tag": source,
        "score_mode": resolved_score_mode,
        "actuals_only": bool(actuals_only),
        "is_live_default": is_live_default,
        **paths,
    }


def resolve_current_live_dataset() -> dict[str, Any] | None:
    locked_tag = read_live_lock_strategy_tag()
    if locked_tag:
        return build_dataset_record(
            locked_tag,
            label=humanize_strategy_tag(locked_tag),
            score_mode="live_only",
            actuals_only=True,
            is_live_default=True,
        )
    newest_live_source = newest_live_log_source_tag()
    if newest_live_source:
        stats_tag = canonical_stats_tag_for_log_source(newest_live_source)
        return build_dataset_record(
            stats_tag,
            log_source_tag=newest_live_source,
            label=humanize_strategy_tag(stats_tag),
            score_mode="live_only",
            actuals_only=True,
            is_live_default=True,
        )
    env_tag_raw = str(os.getenv("STRATEGY_TAG", "")).strip()
    if env_tag_raw:
        return build_dataset_record(live_dataset_tag_from_strategy_tag(env_tag_raw))
    return None


def current_strategy_tag() -> str:
    current_dataset = resolve_current_live_dataset()
    if current_dataset:
        return str(current_dataset["tag"])
    if (ROOT / "stats" / "live_95_momentum").exists() or (ROOT / "logs" / "live_95_momentum").exists():
        return "live_95_momentum"
    if (ROOT / "stats" / "live_87_90_93_exact").exists() or (ROOT / "logs" / "live_87_90_93_exact").exists():
        return "live_87_90_93_exact"
    if (ROOT / "stats" / "live_87_77_67").exists() or (ROOT / "logs" / "live_87_77_67").exists():
        return "live_87_77_67"
    if (ROOT / "stats" / "live_90_70").exists() or (ROOT / "logs" / "live_90_70").exists():
        return "live_90_70"
    if (ROOT / "stats" / "live_90_78").exists() or (ROOT / "logs" / "live_90_78").exists():
        return "live_90_78"
    return "entry_90_stop_70"


VIRTUAL_DATASET_CONFIGS: dict[str, dict[str, Any]] = {
    "live_87_90_93_exact": {
        "label": "LIVE - 87 90 93 Up Exact",
        "source_tag": "live_87_90_93_exact",
        "score_mode": "live_only",
        "actuals_only": True,
    },
    "live_95_momentum": {
        "label": "LIVE - 95 Momentum",
        "source_tag": "live_95_momentum",
        "score_mode": "live_only",
        "actuals_only": True,
    },
    "live_87_77_67": {
        "label": "LIVE - 87 77 67 Hold",
        "source_tag": "live_87_77_67",
        "score_mode": "live_only",
        "actuals_only": True,
    },
    "live_90_70": {
        "label": "LIVE - 90 70",
        "source_tag": "live_90_70",
        "score_mode": "live_only",
        "actuals_only": True,
    },
    "live_90_truffle_exit_size2": {
        "label": "LIVE - 90 Truffle Exit Size 2",
        "source_tag": "live_90_truffle_exit_size2",
        "score_mode": "all",
        "actuals_only": True,
        "truffle_shadow": True,
    },
    "live_90_78": {
        "label": "LIVE - 90 78",
        "source_tag": "live_90_78",
        "score_mode": "live_only",
        "actuals_only": True,
    },
}

STRATEGY_PROFILE_DEFAULTS: dict[str, dict[str, Any]] = {
    "live_87_90_93_exact": {"entry": 87, "stop": 0, "position_size": 10},
    "entry_87_up_90_93_exact": {"entry": 87, "stop": 0, "position_size": 10},
    "live_95_momentum": {"entry": 95, "stop": 0, "position_size": 10},
    "entry_95_late_momentum": {"entry": 95, "stop": 0, "position_size": 10},
    "live_87_77_67": {"entry": 87, "stop": 0, "position_size": 10},
    "entry_87_ladder_hold": {"entry": 87, "stop": 0, "position_size": 10},
    "live_90_70": {"entry": 90, "stop": 70, "position_size": 10},
    "entry_90_stop_70": {"entry": 90, "stop": 70, "position_size": 10},
    "live_90_truffle_exit_size2": {"entry": 90, "stop": 78, "position_size": 2},
    "entry_90_truffle_exit": {"entry": 90, "stop": 78, "position_size": 2},
    "live_90_78": {"entry": 90, "stop": 78, "position_size": 20},
    "entry_90_stop_78": {"entry": 90, "stop": 78, "position_size": 20},
}

BOT_CONTROL_CONFIGS: dict[str, dict[str, Any]] = {
    "live_87_90_93_exact": {
        "launcher": ROOT / "run_bot_live_87_90_93_exact_size10.ps1",
        "log_path": ROOT / "logs" / "live_87_90_93_exact" / "bot.log",
        "marker": "live_87_90_93_exact",
        "label": "Live 87/90/93 Up Exact",
    },
    "live_95_momentum": {
        "launcher": ROOT / "run_bot_live_95_momentum_size10.ps1",
        "log_path": ROOT / "logs" / "live_95_momentum" / "bot.log",
        "marker": "live_95_momentum",
        "label": "Live 95 Momentum",
    },
    "live_87_77_67": {
        "launcher": ROOT / "run_bot_live_87_77_67_size10.ps1",
        "log_path": ROOT / "logs" / "live_87_77_67" / "bot.log",
        "marker": "live_87_77_67",
        "label": "Live 87/77/67 Hold",
    },
    "live_90_70": {
        "launcher": ROOT / "run_bot_live_90_70_size10.ps1",
        "log_path": ROOT / "logs" / "live_90_70" / "bot.log",
        "marker": "live_90_70",
        "label": "Live 90/70",
    },
    "live_90_78": {
        "launcher": ROOT / "run_bot_live_90_78_size5.ps1",
        "log_path": ROOT / "logs" / "live_90_78" / "bot.log",
        "marker": "live_90_78",
        "label": "Live 90/78",
    },
    "entry_90_stop_78": {
        "launcher": ROOT / "run_bot_dry_90_78.ps1",
        "log_path": ROOT / "logs" / "entry_90_stop_78" / "bot.log",
        "marker": "entry_90_stop_78",
        "label": "Dry 90/78",
    },
}


def parse_launcher_env_assignments(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    pattern = re.compile(r"^\$env:([A-Z0-9_]+)\s*=\s*'([^']*)'", re.IGNORECASE)
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = pattern.match(raw_line.strip())
        if not match:
            continue
        values[match.group(1).upper()] = match.group(2)
    return values


@st.cache_data(ttl=10)
def load_launcher_env_assignments(dataset_tag: str) -> dict[str, str]:
    config = BOT_CONTROL_CONFIGS.get(dataset_tag)
    if not config:
        return {}
    launcher = Path(config["launcher"])
    return parse_launcher_env_assignments(launcher)

def humanize_strategy_tag(tag: str) -> str:
    if tag in VIRTUAL_DATASET_CONFIGS:
        return str(VIRTUAL_DATASET_CONFIGS[tag]["label"])
    raw = sanitize_strategy_tag(str(tag or "")).lower()
    if "mushroom" in raw and "v28" in raw:
        details: list[str] = ["Mushroom V28"]
        if "common_clock" in raw:
            details.append("Common Clock")
        if "phi_reward_memory" in raw:
            details.append("Phi Memory")
        if "lifecycle" in raw:
            details.append("Lifecycle")
        if "size2" in raw or "size_2" in raw:
            details.append("Size 2")
        if raw.startswith("live_") or raw.endswith("_live") or "_live_" in raw:
            details.append("Live")
        return " - ".join(list(dict.fromkeys(details)))
    if tag == "entry_95_late_momentum":
        return "Current 95 Momentum"
    if tag == "entry_87_ladder_hold":
        return "Current 87/77/67 Hold"
    if tag == "entry_90_stop_70":
        return "Current 90/70"
    if tag == "entry_90_stop_78":
        return "Current 90/78"
    return tag.replace("_", " ").replace("-", " ").strip().title() or tag


def dataset_uses_actuals(tag: str) -> bool:
    return bool(VIRTUAL_DATASET_CONFIGS.get(tag, {}).get("actuals_only")) or is_live_like_dataset(tag)


def parse_entry_stop_from_tag(tag: str) -> tuple[int | None, int | None]:
    value = str(tag or "").strip().lower()
    patterns = [
        r"^live_(\d+)_(\d+)$",
        r"^entry_(\d+)_stop_(\d+)$",
        r"^live_(\d+)_(\d+)_",
        r"^entry_(\d+)_stop_(\d+)_",
    ]
    for pattern in patterns:
        m = re.match(pattern, value)
        if m:
            return int(m.group(1)), int(m.group(2))
    return None, None


def infer_strategy_profile(dataset_tag: str, trades_df: pd.DataFrame | None = None) -> dict[str, Any]:
    tag = str(dataset_tag or "").strip()
    source_tag = str(VIRTUAL_DATASET_CONFIGS.get(tag, {}).get("source_tag", tag))
    defaults = STRATEGY_PROFILE_DEFAULTS.get(tag) or STRATEGY_PROFILE_DEFAULTS.get(source_tag, {})
    entry_default, stop_default = parse_entry_stop_from_tag(tag)
    if entry_default is None or stop_default is None:
        entry_default, stop_default = parse_entry_stop_from_tag(source_tag)
    profile = {
        "entry": int(defaults.get("entry", entry_default or BOT_ENTRY_CENTS)),
        "stop": int(defaults.get("stop", stop_default or BOT_EXIT_CENTS)),
        "position_size": int(defaults.get("position_size", DISPLAY_POSITION_SIZE)),
        "source_tag": source_tag,
    }
    # For named live profiles, trust the configured current strategy rather than the mixed historical mode.
    if defaults:
        return profile
    if trades_df is not None and not trades_df.empty:
        if "entry_trigger_cents" in trades_df.columns:
            entry_series = pd.to_numeric(trades_df["entry_trigger_cents"], errors="coerce").dropna()
            if not entry_series.empty:
                mode_values = entry_series.mode(dropna=True)
                if not mode_values.empty:
                    profile["entry"] = int(mode_values.iloc[0])
        if "qty" in trades_df.columns:
            qty_series = pd.to_numeric(trades_df["qty"], errors="coerce")
            qty_series = qty_series[qty_series > 0].dropna()
            if not qty_series.empty:
                mode_values = qty_series.mode(dropna=True)
                if not mode_values.empty:
                    profile["position_size"] = int(mode_values.iloc[0])
    return profile


def choose_optimizer_btc_interval(start_ma: datetime, end_ma: datetime) -> str:
    span_hours = max((end_ma - start_ma).total_seconds() / 3600.0, 0.0)
    if span_hours <= 72:
        return "1m"
    if span_hours <= 336:
        return "5m"
    return "15m"


def build_trade_btc_range_features(trades_df: pd.DataFrame, market_results_df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    if trades_df is None or trades_df.empty or "market" not in trades_df.columns or "entry_ts" not in trades_df.columns:
        return pd.DataFrame(), "No scored trades with entry timestamps were available."

    work = trades_df.copy()
    work["market"] = work["market"].fillna("").astype(str).str.upper()
    work = work[work["market"] != ""].copy()
    work["entry_dt"] = pd.to_datetime(work["entry_ts"], errors="coerce")
    work = work[work["entry_dt"].notna()].copy()
    if work.empty:
        return pd.DataFrame(), "Trades did not contain usable entry timestamps."

    close_lookup = build_market_close_lookup(market_results_df)
    work["close_dt"] = work["market"].map(close_lookup)
    missing_close = work["close_dt"].isna()
    if missing_close.any():
        work.loc[missing_close, "close_dt"] = work.loc[missing_close, "market"].map(parse_market_close_from_ticker)
    work = work[work["close_dt"].notna()].copy()
    if work.empty:
        return pd.DataFrame(), "Could not infer market close times for the scored trades."

    work["market_start_dt"] = work["close_dt"] - pd.Timedelta(minutes=15)
    work["seconds_to_close_at_entry"] = (work["close_dt"] - work["entry_dt"]).dt.total_seconds()
    work = work[work["seconds_to_close_at_entry"].notna() & (work["seconds_to_close_at_entry"] >= 0)].copy()
    if work.empty:
        return pd.DataFrame(), "No trades had a valid entry time before market close."

    start_ma = pd.Timestamp(work["market_start_dt"].min()).to_pydatetime().replace(tzinfo=MA_TZ)
    end_ma = pd.Timestamp(work["entry_dt"].max()).to_pydatetime().replace(tzinfo=MA_TZ)
    interval = choose_optimizer_btc_interval(start_ma, end_ma)
    btc_df, source_label, fetch_note = load_btc_intraday_range(start_ma, end_ma, interval=interval)
    if btc_df.empty:
        return pd.DataFrame(), f"Could not load BTC candles for optimizer gating. {fetch_note}".strip()

    btc = btc_df.copy()
    btc["ts"] = pd.to_datetime(btc["ts"], errors="coerce")
    btc = btc[btc["ts"].notna()].sort_values("ts").reset_index(drop=True)
    if btc.empty:
        return pd.DataFrame(), "BTC candles were empty after parsing."

    rows: list[dict[str, Any]] = []
    for _, trade in work.iterrows():
        start_dt = pd.Timestamp(trade["market_start_dt"]).to_pydatetime()
        entry_dt = pd.Timestamp(trade["entry_dt"]).to_pydatetime()
        history = btc[(btc["ts"] >= start_dt) & (btc["ts"] <= entry_dt)].copy()
        if history.empty:
            start_idx = btc["ts"].searchsorted(start_dt, side="left")
            if start_idx >= len(btc):
                start_idx = len(btc) - 1
            if start_idx < 0:
                continue
            start_row = btc.iloc[int(start_idx)]
            history = btc[(btc["ts"] >= start_row["ts"]) & (btc["ts"] <= entry_dt)].copy()
            open_price = float(start_row["open"])
        else:
            open_price = float(history.iloc[0]["open"])

        if history.empty:
            continue

        high_so_far = max(float(history["high"].max()), open_price)
        low_so_far = min(float(history["low"].min()), open_price)
        max_excursion = max(high_so_far - open_price, open_price - low_so_far)
        total_range = high_so_far - low_so_far
        pnl = pd.to_numeric(pd.Series([trade.get("gross_pnl_dollars")]), errors="coerce").iloc[0]
        display_outcome = str(trade.get("display_outcome", trade.get("outcome", "")) or "").lower()
        rows.append({
            "market": trade.get("market"),
            "side": str(trade.get("side", "") or "").lower(),
            "entry_dt": entry_dt,
            "market_start_dt": start_dt,
            "close_dt": pd.Timestamp(trade["close_dt"]).to_pydatetime(),
            "seconds_to_close_at_entry": float(trade["seconds_to_close_at_entry"]),
            "btc_open_price": open_price,
            "btc_high_so_far": high_so_far,
            "btc_low_so_far": low_so_far,
            "btc_total_range_so_far": total_range,
            "btc_max_excursion_from_open": max_excursion,
            "gross_pnl_dollars": pnl,
            "display_outcome": display_outcome,
            "qty": pd.to_numeric(pd.Series([trade.get("qty")]), errors="coerce").iloc[0],
            "entry_trigger_cents": pd.to_numeric(pd.Series([trade.get("entry_trigger_cents")]), errors="coerce").iloc[0],
        })

    features = pd.DataFrame(rows)
    if features.empty:
        return pd.DataFrame(), "No BTC range features could be matched to the scored trades."

    features = features[features["gross_pnl_dollars"].notna()].copy()
    if features.empty:
        return pd.DataFrame(), "BTC range features were built, but no completed trades had realized P and L."

    note_parts = [f"BTC candles: {source_label}" if source_label else "", fetch_note or "", f"interval {interval}"]
    note = " | ".join([part for part in note_parts if part])
    return features.reset_index(drop=True), note


def summarize_btc_range_gate(features_df: pd.DataFrame, range_threshold: float, seconds_threshold: float) -> dict[str, Any]:
    if features_df.empty:
        return {}
    work = features_df.copy()
    work["blocked_by_gate"] = (work["btc_max_excursion_from_open"] < float(range_threshold)) & (work["seconds_to_close_at_entry"] > float(seconds_threshold))
    kept = work[~work["blocked_by_gate"]].copy()
    blocked = work[work["blocked_by_gate"]].copy()

    def _metrics(df: pd.DataFrame) -> dict[str, float]:
        if df.empty:
            return {
                "trade_count": 0,
                "win_rate": np.nan,
                "loss_rate": np.nan,
                "stop_out_rate": np.nan,
                "total_pnl": 0.0,
                "avg_pnl": np.nan,
                "median_pnl": np.nan,
            }
        pnl = pd.to_numeric(df["gross_pnl_dollars"], errors="coerce")
        return {
            "trade_count": int(len(df)),
            "win_rate": float((pnl > 0).mean() * 100.0),
            "loss_rate": float((pnl < 0).mean() * 100.0),
            "stop_out_rate": float((df["display_outcome"].astype(str).str.lower().isin(["loss", "exited_before_settlement"]).mean()) * 100.0),
            "total_pnl": float(pnl.sum()),
            "avg_pnl": float(pnl.mean()),
            "median_pnl": float(pnl.median()),
        }

    base = _metrics(work)
    kept_metrics = _metrics(kept)
    blocked_metrics = _metrics(blocked)
    return {
        "range_threshold": float(range_threshold),
        "seconds_threshold": float(seconds_threshold),
        "blocked_count": int(len(blocked)),
        "blocked_pct": float((len(blocked) / len(work)) * 100.0) if len(work) else 0.0,
        "baseline_trade_count": base["trade_count"],
        "kept_trade_count": kept_metrics["trade_count"],
        "baseline_total_pnl": base["total_pnl"],
        "kept_total_pnl": kept_metrics["total_pnl"],
        "total_pnl_delta": kept_metrics["total_pnl"] - base["total_pnl"],
        "baseline_avg_pnl": base["avg_pnl"],
        "kept_avg_pnl": kept_metrics["avg_pnl"],
        "avg_pnl_delta": (kept_metrics["avg_pnl"] - base["avg_pnl"]) if pd.notna(kept_metrics["avg_pnl"]) and pd.notna(base["avg_pnl"]) else np.nan,
        "baseline_win_rate": base["win_rate"],
        "kept_win_rate": kept_metrics["win_rate"],
        "win_rate_delta": kept_metrics["win_rate"] - base["win_rate"] if pd.notna(kept_metrics["win_rate"]) and pd.notna(base["win_rate"]) else np.nan,
        "baseline_stop_out_rate": base["stop_out_rate"],
        "kept_stop_out_rate": kept_metrics["stop_out_rate"],
        "stop_out_delta": kept_metrics["stop_out_rate"] - base["stop_out_rate"] if pd.notna(kept_metrics["stop_out_rate"]) and pd.notna(base["stop_out_rate"]) else np.nan,
        "blocked_total_pnl": blocked_metrics["total_pnl"],
        "blocked_win_rate": blocked_metrics["win_rate"],
        "blocked_stop_out_rate": blocked_metrics["stop_out_rate"],
    }


def dataset_paths(tag: str, log_source_tag: str | None = None) -> dict[str, Any]:
    source_tag = resolve_log_source_tag(tag, log_source_tag)
    stats_dir = ROOT / "stats" / tag
    return {
        "stats_dir": stats_dir,
        "log_source_tag": source_tag,
        "log_dir": ROOT / "logs" / source_tag,
        "log_path": ROOT / "logs" / source_tag / "bot.log",
        "execution_events_path": ROOT / "logs" / source_tag / "execution_events.ndjson",
        "trades_path": stats_dir / "trades.csv",
        "summary_path": stats_dir / "summary.json",
        "market_results_path": stats_dir / "market_results.csv",
        "research_root": ROOT / "research_data" / source_tag,
    }


def discover_datasets() -> list[dict[str, Any]]:
    datasets: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add_dataset(record: dict[str, Any]) -> None:
        tag = str(record["tag"])
        if tag in seen:
            return
        seen.add(tag)
        datasets.append(record)

    current_live = resolve_current_live_dataset()
    if current_live:
        add_dataset(current_live)

    current_tag = current_live["tag"] if current_live else current_strategy_tag()
    preferred = [current_tag, "live_90_truffle_exit_size2", "live_87_90_93_exact", "live_95_momentum", "live_87_77_67", "live_90_70", "live_90_78"]
    for tag in preferred:
        if tag in VIRTUAL_DATASET_CONFIGS:
            source_tag = str(VIRTUAL_DATASET_CONFIGS[tag]["source_tag"])
            source_log_path = ROOT / "logs" / source_tag / "bot.log"
            stats_dir = ROOT / "stats" / tag
            if not source_log_path.exists() and not stats_dir.exists():
                continue
        if tag not in seen:
            add_dataset(build_dataset_record(tag))
    configured_tags = list(dict.fromkeys([*VIRTUAL_DATASET_CONFIGS.keys(), *BOT_CONTROL_CONFIGS.keys()]))
    for tag in configured_tags:
        if tag in seen:
            continue
        add_dataset(build_dataset_record(tag))
    stats_root = ROOT / "stats"
    if stats_root.exists():
        for child in sorted(stats_root.iterdir(), key=lambda p: p.name):
            if child.is_dir():
                tag = child.name
                if tag in seen:
                    continue
                add_dataset(build_dataset_record(tag))
    return datasets


def read_text_forgiving(path: Path) -> str:
    if not path.exists():
        return ""
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(encoding="utf-8", errors="ignore")


def read_tail_text_forgiving(path: Path, max_bytes: int = 2_000_000) -> str:
    if not path.exists():
        return ""
    try:
        with path.open("rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            start = max(size - max_bytes, 0)
            fh.seek(start)
            data = fh.read()
    except Exception:
        return read_text_forgiving(path)
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            text = data.decode(enc)
            break
        except Exception:
            text = None
    if text is None:
        text = data.decode("utf-8", errors="ignore")
    if start > 0:
        newline = text.find("\n")
        if newline >= 0:
            text = text[newline + 1 :]
    return text


def discover_log_files(log_dir: Path) -> list[Path]:
    if not log_dir.exists():
        return []
    files = [p for p in log_dir.glob("*") if p.is_file() and p.suffix.lower() in {".log", ".txt"}]
    return sorted(files, key=lambda p: (p.stat().st_mtime, p.name))


START_RE = re.compile(r"Starting WS bot\. (?:run_id=\S+ )?dry_run=(?P<dry_run>True|False)", re.IGNORECASE)


def filter_lines_for_dataset(lines: list[str], dataset_tag: str, score_mode: str | None = None) -> list[str]:
    score_mode = str(score_mode or VIRTUAL_DATASET_CONFIGS.get(dataset_tag, {}).get("score_mode", "all"))
    if score_mode == "all":
        return lines
    keep_dry_run = score_mode == "dry_run_only"
    current_dry_run: bool | None = None
    filtered: list[str] = []
    saw_start_marker = False
    for line in lines:
        start_match = START_RE.search(line)
        if start_match:
            saw_start_marker = True
            current_dry_run = start_match.group("dry_run").lower() == "true"
        if current_dry_run is None:
            continue
        if current_dry_run == keep_dry_run:
            filtered.append(line)
    if not saw_start_marker:
        return lines
    return filtered


@st.cache_data(ttl=2)
def load_log(path: str) -> list[str]:
    return read_tail_text_forgiving(Path(path)).splitlines()


@st.cache_data(ttl=2)
def load_log_bundle(log_dir: str) -> tuple[list[str], list[str]]:
    files = discover_log_files(Path(log_dir))
    all_lines: list[str] = []
    for fp in files:
        all_lines.extend(read_tail_text_forgiving(fp).splitlines())
    return all_lines, [str(fp) for fp in files]


@st.cache_data(ttl=2)
def load_trades(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(p)
    except Exception:
        return pd.DataFrame()
    for col in [
        "qty",
        "entry_trigger_cents",
        "entry_fill_cents_assumed",
        "entry_fill_cents_actual",
        "entry_fill_cents_used",
        "exit_trigger_cents",
        "exit_fill_cents_assumed",
        "exit_fill_cents_actual",
        "exit_fill_cents_used",
        "entry_notional_dollars",
        "exit_notional_dollars",
        "total_fees_dollars",
        "gross_pnl_dollars",
        "net_pnl_dollars",
        "net_pnl_percent",
        "gross_pnl_percent",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data(ttl=2)
def load_summary(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


@st.cache_data(ttl=5, show_spinner=False)
def load_research_lab_snapshot(root_path: str) -> dict[str, Any]:
    root = Path(root_path)
    raw_root = root / "raw_events"
    checkpoint_root = root / "book_checkpoints"
    metadata_path = root / "metadata" / "schema_version.json"

    raw_files = sorted(raw_root.rglob("*.ndjson")) if raw_root.exists() else []
    checkpoint_files = sorted(checkpoint_root.rglob("*.ndjson")) if checkpoint_root.exists() else []

    event_type_counts: dict[str, int] = {}
    for fp in raw_files:
        event_type = next((part.split("=", 1)[1] for part in fp.parts if part.startswith("type=")), "unknown")
        event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

    def _rows(files: list[Path], kind: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for fp in sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:12]:
            try:
                stat = fp.stat()
            except Exception:
                continue
            rows.append({
                "kind": kind,
                "path": str(fp.relative_to(root)),
                "size_kb": round(stat.st_size / 1024.0, 1),
                "updated": datetime.fromtimestamp(stat.st_mtime, MA_TZ),
            })
        return rows

    latest_raw = max((fp.stat().st_mtime for fp in raw_files), default=0.0)
    latest_checkpoint = max((fp.stat().st_mtime for fp in checkpoint_files), default=0.0)
    metadata = {}
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except Exception:
            metadata = {}
    pipeline_status_path = root / "metadata" / "pipeline_status.json"
    pipeline_status = {}
    if pipeline_status_path.exists():
        try:
            pipeline_status = json.loads(pipeline_status_path.read_text(encoding="utf-8"))
        except Exception:
            pipeline_status = {}
    replay_status_path = root / "metadata" / "replay_status.json"
    replay_status = {}
    if replay_status_path.exists():
        try:
            replay_status = json.loads(replay_status_path.read_text(encoding="utf-8"))
        except Exception:
            replay_status = {}
    ingestion_status_path = root / "metadata" / "ingestion_status.json"
    ingestion_status = {}
    if ingestion_status_path.exists():
        try:
            ingestion_status = json.loads(ingestion_status_path.read_text(encoding="utf-8"))
        except Exception:
            ingestion_status = {}

    recent_files = _rows(raw_files, "raw") + _rows(checkpoint_files, "checkpoint")
    recent_files = sorted(recent_files, key=lambda row: row["updated"], reverse=True)[:12]

    return {
        "root_exists": root.exists(),
        "raw_file_count": len(raw_files),
        "checkpoint_file_count": len(checkpoint_files),
        "latest_raw": datetime.fromtimestamp(latest_raw, MA_TZ) if latest_raw else None,
        "latest_checkpoint": datetime.fromtimestamp(latest_checkpoint, MA_TZ) if latest_checkpoint else None,
        "event_type_counts": event_type_counts,
        "metadata": metadata,
        "pipeline_status": pipeline_status,
        "replay_status": replay_status,
        "ingestion_status": ingestion_status,
        "recent_files": recent_files,
    }


@st.cache_data(ttl=20, show_spinner=False)
def load_research_parquet(root_path: str, section: str, columns: tuple[str, ...] | None = None, max_files: int | None = None) -> pd.DataFrame:
    base = Path(root_path) / section
    if not base.exists():
        return pd.DataFrame()
    files = sorted(base.rglob("*.parquet"), key=lambda p: p.stat().st_mtime, reverse=True)
    if max_files is not None:
        files = files[:max(0, int(max_files))]
    if not files:
        return pd.DataFrame()
    frames: list[pd.DataFrame] = []
    for fp in files:
        try:
            frame = pd.read_parquet(fp, columns=list(columns) if columns else None)
        except Exception:
            continue
        try:
            relative_parts = fp.relative_to(base).parts[:-1]
        except Exception:
            relative_parts = fp.parts[:-1]
        for part in relative_parts:
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            if key and key not in frame.columns:
                frame[key] = value
        frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


@st.cache_data(ttl=20, show_spinner=False)
def load_research_market_feature_slice(root_path: str, market: str, max_files: int = 6) -> pd.DataFrame:
    market = str(market or "").strip().upper()
    if not market:
        return pd.DataFrame()
    base = Path(root_path) / "features"
    if not base.exists():
        return pd.DataFrame()
    market_dir = base / f"market_ticker={market}"
    if market_dir.exists():
        part_latest = market_dir / "part-latest.parquet"
        if part_latest.exists():
            files = [part_latest]
        else:
            files = sorted(market_dir.rglob("*.parquet"), key=lambda p: p.stat().st_mtime, reverse=True)
    else:
        files = sorted(base.rglob("*.parquet"), key=lambda p: p.stat().st_mtime, reverse=True)
        files = [fp for fp in files if f"market_ticker={market}" in str(fp)]
    files = files[:max(1, int(max_files))]
    frames: list[pd.DataFrame] = []
    cols = ["ts", "market_ticker", "yes_bid_cents", "no_bid_cents", "spread_yes", "depth_imbalance"]
    for fp in files:
        try:
            frame = pd.read_parquet(fp, columns=cols)
        except Exception:
            continue
        if "market_ticker" not in frame.columns:
            frame["market_ticker"] = market
        frames.append(frame)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["ts"] = pd.to_datetime(out.get("ts"), utc=True, errors="coerce")
    return out[out["ts"].notna()].sort_values("ts").reset_index(drop=True)


@st.cache_data(ttl=20, show_spinner=False)
def load_research_recent_normalized(root_path: str, max_files: int = 4) -> pd.DataFrame:
    return load_research_parquet(root_path, "normalized_events", columns=("local_recv_dt", "event_type"), max_files=max_files)


@st.cache_data(ttl=20, show_spinner=False)
def load_research_labels_sample(root_path: str, max_files: int = 4) -> pd.DataFrame:
    cols = ("market","side","entry_ts","net_pnl_dollars","hold_duration_s","feed_age_ms_at_entry","submit_latency_ms","auth_prep_ms","http_roundtrip_ms","json_parse_ms")
    return load_research_parquet(root_path, "trade_labels", columns=cols, max_files=max_files)


def build_research_event_flow_figure(normalized_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if normalized_df.empty or "local_recv_dt" not in normalized_df.columns:
        fig.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=20, b=20))
        return fig
    work = normalized_df.copy()
    work = work[work["local_recv_dt"].notna()].copy()
    if work.empty:
        fig.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=20, b=20))
        return fig
    work["minute"] = work["local_recv_dt"].dt.floor("min")
    grouped = work.groupby(["minute", "event_type"]).size().reset_index(name="count")
    top_types = grouped.groupby("event_type")["count"].sum().sort_values(ascending=False).head(5).index.tolist()
    grouped = grouped[grouped["event_type"].isin(top_types)]
    colors = ["#36e28f", "#6dc8ff", "#ff5c5c", "#ffb44d", "#a98bff"]
    for idx, event_type in enumerate(top_types):
        chunk = grouped[grouped["event_type"] == event_type]
        fig.add_trace(go.Scatter(
            x=chunk["minute"],
            y=chunk["count"],
            mode="lines+markers",
            name=event_type,
            line=dict(width=2.5, color=colors[idx % len(colors)]),
            marker=dict(size=5),
        ))
    fig.update_layout(template="plotly_dark", height=320, margin=dict(l=20, r=20, t=20, b=20), legend_title_text="Event type", xaxis_title="Time", yaxis_title="Events per minute")
    return fig


def build_research_latency_figure(labels_df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Submit latency", "Feed age at entry"))
    if labels_df.empty:
        fig.update_layout(template="plotly_dark", height=320, margin=dict(l=20, r=20, t=40, b=20))
        return fig
    work = labels_df.copy()
    for col in ("submit_latency_ms", "feed_age_ms_at_entry", "net_pnl_dollars"):
        if col in work.columns:
            work[col] = pd.to_numeric(work[col], errors="coerce")
    work["outcome_group"] = np.where(work.get("net_pnl_dollars", 0).fillna(0) >= 0, "positive", "negative")
    palette = {"positive": "#36e28f", "negative": "#ff5c5c"}
    for outcome_group, chunk in work.groupby("outcome_group"):
        if "submit_latency_ms" in chunk.columns:
            fig.add_trace(go.Histogram(x=chunk["submit_latency_ms"].dropna(), name=f"{outcome_group} submit", marker_color=palette[outcome_group], opacity=0.65, nbinsx=24, showlegend=True), row=1, col=1)
        if "feed_age_ms_at_entry" in chunk.columns:
            fig.add_trace(go.Histogram(x=chunk["feed_age_ms_at_entry"].dropna(), name=f"{outcome_group} feed", marker_color=palette[outcome_group], opacity=0.65, nbinsx=24, showlegend=False), row=1, col=2)
    fig.update_layout(template="plotly_dark", barmode="overlay", height=340, margin=dict(l=20, r=20, t=40, b=20))
    fig.update_xaxes(title_text="ms", row=1, col=1)
    fig.update_xaxes(title_text="ms", row=1, col=2)
    return fig


def build_research_market_tape_figure(features_df: pd.DataFrame, market: str) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, subplot_titles=("Bid tape", "Spread and imbalance"))
    if features_df.empty or not market:
        fig.update_layout(template="plotly_dark", height=460, margin=dict(l=20, r=20, t=40, b=20))
        return fig
    work = features_df.copy()
    work = work[work.get("market_ticker", "").astype(str) == str(market)].copy()
    if work.empty:
        fig.update_layout(template="plotly_dark", height=460, margin=dict(l=20, r=20, t=40, b=20))
        return fig
    work["ts"] = pd.to_datetime(work["ts"], utc=True, errors="coerce")
    work = work[work["ts"].notna()].sort_values("ts")
    fig.add_trace(go.Scatter(x=work["ts"], y=work.get("yes_bid_cents"), mode="lines", name="YES bid", line=dict(color="#36e28f", width=2.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=work["ts"], y=work.get("no_bid_cents"), mode="lines", name="NO bid", line=dict(color="#ff5c5c", width=2.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=work["ts"], y=work.get("spread_yes"), mode="lines", name="YES spread", line=dict(color="#6dc8ff", width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=work["ts"], y=work.get("depth_imbalance"), mode="lines", name="Depth imbalance", line=dict(color="#ffb44d", width=2)), row=2, col=1)
    fig.update_layout(template="plotly_dark", height=460, margin=dict(l=20, r=20, t=40, b=20), legend_title_text="Series")
    fig.update_yaxes(title_text="Cents", row=1, col=1)
    fig.update_yaxes(title_text="Spread / imbalance", row=2, col=1)
    return fig


@st.cache_data(ttl=20, show_spinner=False)
def load_latest_replay_artifact(root_path: str, filename: str) -> pd.DataFrame:
    root = Path(root_path) / "replay_runs"
    if not root.exists():
        return pd.DataFrame()
    run_dirs = sorted([p for p in root.iterdir() if p.is_dir() and p.name.startswith("run_id=")], key=lambda p: p.name, reverse=True)
    for run_dir in run_dirs:
        artifact_path = run_dir / filename
        if not artifact_path.exists():
            continue
        try:
            return pd.read_parquet(artifact_path)
        except Exception:
            continue
    return pd.DataFrame()


@st.cache_data(ttl=20, show_spinner=False)
def load_latest_replay_summary(root_path: str) -> pd.DataFrame:
    return load_latest_replay_artifact(root_path, "replay_summary.parquet")


@st.cache_data(ttl=20, show_spinner=False)
def load_latest_direct_replay_summary(root_path: str) -> pd.DataFrame:
    return load_latest_replay_artifact(root_path, "direct_replay_summary.parquet")


@st.cache_data(ttl=20, show_spinner=False)
def load_latest_direct_replay_trades(root_path: str) -> pd.DataFrame:
    return load_latest_replay_artifact(root_path, "direct_replay_trades.parquet")


@st.cache_data(ttl=20, show_spinner=False)
def load_latest_optimizer_summary(root_path: str) -> pd.DataFrame:
    return load_latest_replay_artifact(root_path, "optimizer_summary.parquet")


@st.cache_data(ttl=20, show_spinner=False)
def load_latest_optimizer_trades(root_path: str) -> pd.DataFrame:
    return load_latest_replay_artifact(root_path, "optimizer_trades.parquet")

def refresh_dashboard_caches() -> None:
    st.cache_data.clear()


def latest_existing_mtime(paths: list[Path]) -> float:
    mtimes = [p.stat().st_mtime for p in paths if p.exists()]
    return max(mtimes) if mtimes else 0.0


def score_refresh_lock_path(dataset_tag: str) -> Path:
    return ROOT / "stats" / dataset_tag / ".score_refresh.lock"


def score_refresh_process_running(lock_path: Path) -> bool:
    if not lock_path.exists():
        return False
    try:
        payload = json.loads(lock_path.read_text(encoding="utf-8"))
    except Exception:
        return False
    if not isinstance(payload, dict):
        return False
    pid = payload.get("pid")
    if not isinstance(pid, int):
        return False
    try:
        proc = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                (
                    f"$p = Get-Process -Id {pid} -ErrorAction SilentlyContinue; "
                    "if ($p) { 'running' }"
                ),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return False
    return proc.returncode == 0 and proc.stdout.strip() == "running"


def maybe_launch_auto_score_refresh(active_dataset: dict[str, Any], *, force: bool = False) -> None:
    if not SCORE_SCRIPT.exists():
        return
    dataset_tag = str(active_dataset["tag"])
    source_paths = [Path(active_dataset["log_path"]), Path(active_dataset["execution_events_path"])]
    output_paths = [Path(active_dataset["trades_path"]), Path(active_dataset["summary_path"]), Path(active_dataset["market_results_path"])]
    latest_source = latest_existing_mtime(source_paths)
    if latest_source <= 0:
        return
    latest_output = latest_existing_mtime(output_paths)
    if not force and latest_output >= latest_source - SCORE_AUTO_REFRESH_STALE_GRACE_SECONDS:
        return
    lock_path = score_refresh_lock_path(dataset_tag)
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        return
    if score_refresh_process_running(lock_path):
        return
    now = time.time()
    if not force and lock_path.exists() and now - lock_path.stat().st_mtime < SCORE_AUTO_REFRESH_MIN_INTERVAL_SECONDS:
        try:
            stale_payload = json.loads(lock_path.read_text(encoding="utf-8"))
        except Exception:
            stale_payload = None
        if stale_payload:
            return
    try:
        lock_path.write_text(
            json.dumps(
                {
                    "pid": None,
                    "dataset_tag": dataset_tag,
                    "requested_at": datetime.now().isoformat(),
                    "status": "launching",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    except Exception:
        return
    env = os.environ.copy()
    env["STRATEGY_TAG"] = dataset_tag
    env["OUTPUT_STRATEGY_TAG"] = dataset_tag
    env["LOG_SOURCE_TAG"] = str(active_dataset.get("log_source_tag") or active_dataset.get("source_tag") or dataset_tag)
    env["SCORE_MODE"] = str(active_dataset.get("score_mode") or VIRTUAL_DATASET_CONFIGS.get(dataset_tag, {}).get("score_mode") or "all")
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        subprocess.Popen([sys.executable, str(SCORE_SCRIPT)], cwd=str(ROOT), env=env, creationflags=creationflags)
    except Exception:
        try:
            lock_path.unlink(missing_ok=True)
        except Exception:
            pass


def get_bot_control_config(dataset_tag: str) -> dict[str, Any] | None:
    return BOT_CONTROL_CONFIGS.get(dataset_tag)


def ps_single_quote(value: str) -> str:
    return value.replace("'", "''")


def managed_bot_processes(dataset_tag: str) -> list[dict[str, Any]]:
    config = get_bot_control_config(dataset_tag)
    if not config:
        return []
    marker = str(config["marker"])
    query = rf"""
$marker = {json.dumps(marker)}
$procs = Get-CimInstance Win32_Process | Where-Object {{
    $_.ProcessId -ne $PID -and
    ($_.Name -ieq 'powershell.exe' -or $_.Name -ieq 'python.exe') -and
    $_.CommandLine -and
    $_.CommandLine -like "*KalshiManagedBot:{marker}*"
}}
$procs | Select-Object ProcessId, ParentProcessId, Name, CommandLine | ConvertTo-Json -Compress
"""
    proc = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", query],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return []
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, dict):
        return [parsed]
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    return []


def bot_is_running(dataset_tag: str) -> bool:
    return bool(managed_bot_processes(dataset_tag))


def launch_managed_bot(dataset_tag: str) -> tuple[bool, str]:
    config = get_bot_control_config(dataset_tag)
    if not config:
        return False, f"No launcher is configured for {dataset_tag}."
    existing = managed_bot_processes(dataset_tag)
    if existing:
        return True, f"{config['label']} is already running."
    launcher = Path(config["launcher"])
    if not launcher.exists():
        return False, f"Launcher not found: {launcher.name}"
    marker = str(config["marker"])
    env = os.environ.copy()
    env["KALSHI_MANAGED_BOT_TAG"] = f"KalshiManagedBot:{marker}"
    creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
    try:
        proc = subprocess.Popen(
            [
                "powershell.exe",
                "-NoExit",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(launcher),
            ],
            cwd=str(ROOT),
            env=env,
            creationflags=creationflags,
        )
    except Exception as exc:  # noqa: BLE001
        return False, f"Failed to launch bot window: {exc}"
    return True, f"Launched {config['label']} (pid {proc.pid})."


def stop_managed_bot(dataset_tag: str) -> tuple[bool, str]:
    config = get_bot_control_config(dataset_tag)
    if not config:
        return False, f"No launcher is configured for {dataset_tag}."
    marker = str(config["marker"])
    stop_cmd = rf"""
$marker = {json.dumps(marker)}
$targets = Get-CimInstance Win32_Process | Where-Object {{
    $_.ProcessId -ne $PID -and
    ($_.Name -ieq 'powershell.exe' -or $_.Name -ieq 'python.exe') -and
    $_.CommandLine -and
    $_.CommandLine -like "*KalshiManagedBot:{marker}*"
}} | Select-Object -ExpandProperty ProcessId -Unique
if (-not $targets) {{
    Write-Output "NO_MATCH"
    exit 0
}}
$all = New-Object 'System.Collections.Generic.HashSet[int]'
function Add-Tree([int]$targetPid) {{
    if (-not $all.Add($targetPid)) {{ return }}
    $children = Get-CimInstance Win32_Process | Where-Object {{ $_.ParentProcessId -eq $targetPid }} | Select-Object -ExpandProperty ProcessId
    foreach ($child in $children) {{ Add-Tree([int]$child) }}
}}
foreach ($targetPid in $targets) {{ Add-Tree([int]$targetPid) }}
$allIds = @($all)
$allIds | Sort-Object -Descending | ForEach-Object {{
    try {{ Stop-Process -Id $_ -Force -ErrorAction Stop }} catch {{}}
}}
Write-Output ("STOPPED:" + (($allIds | Sort-Object) -join ','))
"""
    proc = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", stop_cmd],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return False, proc.stderr.strip() or proc.stdout.strip() or "Failed to stop bot."
    output = proc.stdout.strip()
    if output == "NO_MATCH":
        return True, f"No managed process found for {config['label']}."
    return True, f"Stopped {config['label']}."





@st.cache_data(ttl=2)
def load_market_results(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(p)
    except Exception:
        return pd.DataFrame()
    if df.empty:
        return df

    if "market" not in df.columns:
        df["market"] = ""
    df["market"] = df["market"].fillna("").astype(str).str.strip().str.upper()

    if "result" not in df.columns:
        df["result"] = ""
    df["result"] = df["result"].fillna("").astype(str).str.strip().str.lower()

    if "status" not in df.columns:
        df["status"] = ""
    df["status"] = df["status"].fillna("").astype(str).str.strip().str.lower()

    if "close_time" in df.columns:
        df["close_time_dt"] = df["close_time"].apply(ensure_ma_datetime)
    else:
        df["close_time_dt"] = pd.NaT

    return df


def _json_loads_maybe(value: Any) -> Any:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return json.loads(value)
    except Exception:
        return None


def _float_or_none(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        out = float(value)
        return out if np.isfinite(out) else None
    except Exception:
        return None


def _truffle_usage_from_raw_response(raw_response: Any) -> dict[str, Any]:
    parsed = _json_loads_maybe(raw_response)
    if not isinstance(parsed, dict):
        return {}
    usage = parsed.get("usage")
    return usage if isinstance(usage, dict) else {}


@st.cache_data(ttl=2, show_spinner=False)
def load_truffle_shadow_summary(log_dir: str) -> pd.DataFrame:
    path = Path(log_dir) / "truffle_post_entry_shadow.ndjson"
    if not path.exists():
        return pd.DataFrame()

    by_market: dict[str, dict[str, Any]] = {}
    for raw in read_tail_text_forgiving(path, max_bytes=8_000_000).splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            rec = json.loads(raw)
        except Exception:
            continue
        market = str(rec.get("market") or "").strip().upper()
        if not market:
            continue
        event_type = str(rec.get("event_type") or "")
        row = by_market.setdefault(market, {"market": market})
        row["side"] = str(rec.get("side") or row.get("side") or "").upper()

        if event_type == "post_entry_shadow_scheduled":
            row["scheduled_at"] = rec.get("ts_wall")
            row["entry_fill_cents"] = _float_or_none(rec.get("entry_fill_cents"))
            row["entry_trigger_cents"] = _float_or_none(rec.get("entry_trigger_cents"))
            row["seconds_to_close_at_entry"] = _float_or_none(rec.get("seconds_to_close_at_entry"))
            row["shadow_delay_seconds"] = _float_or_none(rec.get("shadow_delay_seconds"))
            pre_entry = rec.get("pre_entry_context")
            if isinstance(pre_entry, dict):
                row["entry_timing_state"] = pre_entry.get("entry_timing_state")
                row["entry_pressure_state"] = pre_entry.get("entry_pressure_state")
                row["volatility_state"] = pre_entry.get("volatility_state")
        elif event_type == "post_entry_shadow_decision":
            decision = rec.get("decision") if isinstance(rec.get("decision"), dict) else {}
            usage = _truffle_usage_from_raw_response(decision.get("raw_response") or rec.get("raw_response"))
            row["decision_at"] = rec.get("ts_wall")
            row["model_decision"] = (
                rec.get("effective_exit_supervisor_decision")
                or rec.get("exit_supervisor_decision")
                or decision.get("decision")
                or ""
            )
            row["confidence"] = _float_or_none(decision.get("confidence") or rec.get("confidence"))
            row["reason_code"] = decision.get("reason_code") or rec.get("reason_code") or ""
            row["reversal_risk"] = decision.get("reversal_risk") or rec.get("reversal_risk") or ""
            row["settlement_bias"] = decision.get("settlement_bias") or rec.get("settlement_bias") or ""
            row["valid"] = bool(rec.get("valid")) if "valid" in rec else None
            row["parse_error"] = decision.get("parse_error") or rec.get("parse_error") or ""
            row["exit_now"] = bool(rec.get("exit_now")) if "exit_now" in rec else None
            row["red_light"] = bool(rec.get("red_light")) if "red_light" in rec else None
            row["green_light"] = bool(rec.get("green_light")) if "green_light" in rec else None
            row["current_exit_bid_cents"] = _float_or_none(rec.get("current_exit_bid_cents"))
            row["seconds_since_entry"] = _float_or_none(rec.get("seconds_since_entry") or decision.get("seconds_since_entry"))
            row["ttft_ms"] = _float_or_none(usage.get("ttft_ms"))
            row["total_tokens"] = _float_or_none(usage.get("total_tokens"))
        elif event_type == "post_entry_shadow_outcome":
            outcome = rec.get("outcome_record") if isinstance(rec.get("outcome_record"), dict) else {}
            shadow_eval = rec.get("shadow_exit_eval") if isinstance(rec.get("shadow_exit_eval"), dict) else {}
            decision = rec.get("decision") if isinstance(rec.get("decision"), dict) else {}
            row["outcome_at"] = rec.get("ts_wall")
            row["outcome_type"] = rec.get("outcome_type") or outcome.get("outcome_type") or ""
            row["pnl_dollars"] = _float_or_none(rec.get("pnl_dollars") if rec.get("pnl_dollars") is not None else outcome.get("pnl_dollars"))
            row["truth_label"] = shadow_eval.get("truth_label") or ""
            row["delta_vs_actual_dollars"] = _float_or_none(shadow_eval.get("delta_vs_actual_dollars"))
            row["hypothetical_exit_net_pnl_dollars"] = _float_or_none(shadow_eval.get("hypothetical_exit_net_pnl_dollars"))
            row["actual_pnl_dollars"] = _float_or_none(shadow_eval.get("actual_pnl_dollars"))
            row["entry_qty"] = _float_or_none(outcome.get("entry_qty"))
            if not row.get("model_decision"):
                row["model_decision"] = decision.get("decision") or ""
                row["confidence"] = _float_or_none(decision.get("confidence"))
                row["reason_code"] = decision.get("reason_code") or ""
                row["reversal_risk"] = decision.get("reversal_risk") or ""
                row["settlement_bias"] = decision.get("settlement_bias") or ""

    if not by_market:
        return pd.DataFrame()
    df = pd.DataFrame(by_market.values())
    for col in ["scheduled_at", "decision_at", "outcome_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    for col in [
        "entry_fill_cents",
        "entry_trigger_cents",
        "seconds_to_close_at_entry",
        "shadow_delay_seconds",
        "confidence",
        "current_exit_bid_cents",
        "seconds_since_entry",
        "ttft_ms",
        "total_tokens",
        "pnl_dollars",
        "delta_vs_actual_dollars",
        "hypothetical_exit_net_pnl_dollars",
        "actual_pnl_dollars",
        "entry_qty",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if {"scheduled_at", "decision_at", "shadow_delay_seconds"}.issubset(df.columns):
        df["prompt_response_seconds"] = (
            (df["decision_at"] - df["scheduled_at"]).dt.total_seconds()
            - pd.to_numeric(df["shadow_delay_seconds"], errors="coerce").fillna(0.0)
        )
    else:
        df["prompt_response_seconds"] = np.nan
    sort_col = "decision_at" if "decision_at" in df.columns else "scheduled_at"
    return df.sort_values(sort_col, ascending=False, na_position="last").reset_index(drop=True)


@st.cache_data(ttl=2, show_spinner=False)
def load_truffle_lease_summary(log_dir: str) -> pd.DataFrame:
    path = Path(log_dir) / "lease_events.ndjson"
    if not path.exists():
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for raw in read_tail_text_forgiving(path, max_bytes=4_000_000).splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            rec = json.loads(raw)
        except Exception:
            continue
        rows.append({
            "ts": rec.get("ts_wall"),
            "event_type": rec.get("event_type"),
            "market": str(rec.get("market") or "").upper(),
            "lease_decision": rec.get("decision") or rec.get("lease_decision") or "",
            "mode": rec.get("mode") or "",
            "rationale_code": rec.get("rationale_code") or "",
            "summary_reason": rec.get("summary_reason") or "",
            "side": str(rec.get("side") or "").upper(),
            "trigger_price_cents": _float_or_none(rec.get("trigger_price_cents")),
            "valid": rec.get("valid"),
        })
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["ts"] = pd.to_datetime(df["ts"], utc=True, errors="coerce")
    if "trigger_price_cents" in df.columns:
        df["trigger_price_cents"] = pd.to_numeric(df["trigger_price_cents"], errors="coerce")
    return df.sort_values("ts", ascending=False, na_position="last").reset_index(drop=True)


def parse_optimizer_signal_rows(lines: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        m = ENTRY_RE.match(line)
        if m:
            ts = parse_ts(m.group("ts"))
            if ts is not None:
                rows.append({
                    "ts": ts,
                    "market": m.group("market"),
                    "kind": "entry",
                    "side": m.group("side"),
                    "trigger": float(m.group("trigger")),
                    "limit": float(m.group("limit")),
                    "qty": float(m.group("qty")),
                })
            continue
        m = EXIT_RE.match(line)
        if m:
            ts = parse_ts(m.group("ts"))
            if ts is not None:
                rows.append({
                    "ts": ts,
                    "market": m.group("market"),
                    "kind": "exit",
                    "side": m.group("side"),
                    "trigger": float(m.group("trigger")),
                    "limit": float(m.group("limit")),
                    "qty": float(m.group("qty")),
                })
    if not rows:
        return pd.DataFrame(columns=["ts", "market", "kind", "side", "trigger", "limit", "qty"])
    out = pd.DataFrame(rows).sort_values("ts").reset_index(drop=True)
    return out


def _opt_first_true_index(mask: np.ndarray) -> int | None:
    if mask.size == 0:
        return None
    idx = int(mask.argmax())
    if not bool(mask[idx]):
        return None
    return idx


def compute_optimizer_signal_slippage(signal_df: pd.DataFrame) -> tuple[float, float]:
    if signal_df.empty:
        return 0.0, 0.0
    sig = signal_df.copy().sort_values("ts").reset_index(drop=True)
    if len(sig) > 300:
        sig = sig.tail(300).reset_index(drop=True)
    age_rank = np.arange(len(sig), dtype=float)
    half_life = max(12.0, len(sig) / 3.0)
    weights = np.power(0.5, (len(sig) - 1 - age_rank) / half_life)
    sig["w"] = weights

    entry_slip = 0.0
    entry_df = sig[sig["kind"] == "entry"].copy()
    if not entry_df.empty and float(entry_df["w"].sum()) > 0:
        delta = (entry_df["limit"] - entry_df["trigger"]).clip(lower=0.0)
        entry_slip = float(np.average(delta, weights=entry_df["w"]))

    exit_slip = 0.0
    exit_df = sig[sig["kind"] == "exit"].copy()
    if not exit_df.empty and float(exit_df["w"].sum()) > 0:
        delta = (exit_df["trigger"] - exit_df["limit"]).clip(lower=0.0)
        exit_slip = float(np.average(delta, weights=exit_df["w"]))

    return round(entry_slip, 4), round(exit_slip, 4)


@st.cache_data(show_spinner=False, ttl=120)
def optimize_entry_stop_grid(
    training_price_df: pd.DataFrame,
    resolved_results_df: pd.DataFrame,
    signal_df: pd.DataFrame,
    min_entry_seconds_to_close: int = 60,
    max_markets: int | None = MAX_OPTIMIZER_MARKETS,
    recency_weighted: bool = True,
    position_size: int = DISPLAY_POSITION_SIZE,
) -> pd.DataFrame:
    if training_price_df.empty or resolved_results_df.empty:
        return pd.DataFrame()

    if "market" not in resolved_results_df.columns or "result" not in resolved_results_df.columns:
        return pd.DataFrame()

    results = resolved_results_df.copy()
    results = results.dropna(subset=["market", "result"]).copy()
    results["market"] = results["market"].astype(str).str.strip().str.upper()
    results["result"] = results["result"].astype(str).str.strip().str.lower()
    results = results[results["market"].ne("") & results["market"].ne("NONE")]
    results = results[results["result"].isin(["yes", "no"])].copy()
    results = results.drop_duplicates(subset=["market"], keep="last").reset_index(drop=True)
    if results.empty:
        return pd.DataFrame()
    if "close_time_dt" in results.columns:
        results["close_time_dt"] = results["close_time_dt"].apply(ensure_ma_datetime)
    else:
        results["close_time_dt"] = pd.NaT

    if max_markets is not None and len(results) > max_markets:
        results = results.tail(max_markets).copy()

    price_df = training_price_df.copy()
    if price_df.empty or "market" not in price_df.columns or "ts" not in price_df.columns:
        return pd.DataFrame()

    price_df["market"] = price_df["market"].astype(str).str.strip().str.upper()
    price_df["ts"] = pd.to_datetime(price_df["ts"], errors="coerce")
    price_df = price_df[price_df["market"].ne("") & price_df["market"].ne("NONE")]
    price_df = price_df.dropna(subset=["market", "ts"]).copy()
    if price_df.empty:
        return pd.DataFrame()

    results = results[results["market"].isin(set(price_df["market"].unique()))].copy()
    if results.empty:
        return pd.DataFrame()

    n = len(results)
    half_life = max(10.0, n / 3.0)
    if recency_weighted:
        market_weights = {
            str(row["market"]): float(np.power(0.5, (n - 1 - idx) / half_life))
            for idx, (_, row) in enumerate(results.iterrows())
        }
    else:
        market_weights = {
            str(row["market"]): 1.0
            for _, row in results.iterrows()
        }

    entry_slip, exit_slip = compute_optimizer_signal_slippage(signal_df)
    entry_slip_cap = max(0.0, min(entry_slip, 1.0))
    entry_marketable_cap_floor = 0.25 if entry_slip_cap <= 0 else entry_slip_cap
    entries = np.array(sorted(OPT_ENTRY_THRESHOLDS), dtype=float)
    stops = np.array(sorted(OPT_STOP_THRESHOLDS), dtype=float)
    shape = (len(entries), len(stops))
    sample_arr = np.zeros(shape, dtype=int)
    weighted_sample_arr = np.zeros(shape, dtype=float)
    pnl_arr = np.zeros(shape, dtype=float)
    entry_fill_arr = np.zeros(shape, dtype=float)
    stop_fill_arr = np.zeros(shape, dtype=float)
    stop_fill_weight_arr = np.zeros(shape, dtype=float)
    fee_arr = np.zeros(shape, dtype=float)
    win_arr = np.zeros(shape, dtype=float)
    stop_hit_arr = np.zeros(shape, dtype=float)
    false_stop_arr = np.zeros(shape, dtype=float)
    drawdown_arr = np.zeros(shape, dtype=float)
    profit_sum_arr = np.zeros(shape, dtype=float)
    loss_sum_arr = np.zeros(shape, dtype=float)
    winner_count_arr = np.zeros(shape, dtype=float)
    loser_count_arr = np.zeros(shape, dtype=float)

    min_sample = max(2, min(8, int(len(results) * 0.08) or 2))
    provisional_min_sample = 1

    grouped_prices = {
        market: group.sort_values("ts").copy()
        for market, group in price_df.groupby("market", sort=False)
    }
    delay_ns = int(pd.Timedelta(seconds=BOT_DELAY_SECONDS).value)
    min_entry_ns = int(pd.Timedelta(seconds=max(int(min_entry_seconds_to_close), BOT_DELAY_SECONDS)).value)
    secs_to_close_arr = np.zeros(shape, dtype=float)

    for _, result_row in results.iterrows():
        market = str(result_row["market"])
        result = str(result_row["result"]).lower()
        close_time_dt = ensure_ma_datetime(result_row.get("close_time_dt"))
        market_df = grouped_prices.get(market)
        if market_df is None or market_df.empty:
            continue

        weight = float(market_weights.get(market, 1.0))
        market_df = market_df.copy()
        market_df["ts"] = pd.to_datetime(market_df["ts"], errors="coerce")
        market_df = market_df.dropna(subset=["ts"]).sort_values("ts")
        if market_df.empty:
            continue

        ts_ns = market_df["ts"].astype("int64").to_numpy()
        yes_ask = pd.to_numeric(market_df["yes_ask"], errors="coerce").to_numpy(dtype=float) if "yes_ask" in market_df.columns else np.full(len(market_df), np.nan, dtype=float)
        no_ask = pd.to_numeric(market_df["no_ask"], errors="coerce").to_numpy(dtype=float) if "no_ask" in market_df.columns else np.full(len(market_df), np.nan, dtype=float)
        yes_bid = pd.to_numeric(market_df["yes_bid"], errors="coerce").to_numpy(dtype=float) if "yes_bid" in market_df.columns else np.full(len(market_df), np.nan, dtype=float)
        no_bid = pd.to_numeric(market_df["no_bid"], errors="coerce").to_numpy(dtype=float) if "no_bid" in market_df.columns else np.full(len(market_df), np.nan, dtype=float)

        if len(ts_ns) == 0:
            continue

        if close_time_dt is not None:
            close_ts_ns = int(pd.Timestamp(close_time_dt.replace(tzinfo=None)).value)
            entry_window_mask = ts_ns <= (close_ts_ns - min_entry_ns)
        else:
            entry_window_mask = np.ones(len(ts_ns), dtype=bool)
            close_ts_ns = None
        if not bool(entry_window_mask.any()):
            continue

        for entry_idx, entry in enumerate(entries):
            yes_signal = np.where(np.isnan(yes_ask), False, (yes_ask >= entry) & (yes_ask <= (entry + entry_marketable_cap_floor))) & entry_window_mask
            no_signal = np.where(np.isnan(no_ask), False, (no_ask >= entry) & (no_ask <= (entry + entry_marketable_cap_floor))) & entry_window_mask
            exclusive_signal = yes_signal ^ no_signal
            first_idx = _opt_first_true_index(exclusive_signal)
            if first_idx is None:
                continue

            side = "yes" if bool(yes_signal[first_idx]) else "no"
            ask = yes_ask if side == "yes" else no_ask
            bid = yes_bid if side == "yes" else no_bid
            raw_entry = float(ask[first_idx])
            if np.isnan(raw_entry):
                continue

            modeled_entry = min(raw_entry, float(entry) + entry_slip_cap)
            entry_fill = float(np.clip(max(float(entry), modeled_entry), 1.0, 99.0))
            valid_future_ask = ask[first_idx:]
            valid_future_ask = valid_future_ask[~np.isnan(valid_future_ask)]
            min_after_entry = float(valid_future_ask.min()) if valid_future_ask.size else raw_entry
            delayed_idx = int(np.searchsorted(ts_ns, ts_ns[first_idx] + delay_ns, side="left"))
            settle_fill = 100.0 if result == side else 0.0
            false_stop_outcome = result == side
            secs_to_close = float((close_ts_ns - ts_ns[first_idx]) / 1_000_000_000.0) if close_ts_ns is not None else np.nan

            for stop_idx, stop in enumerate(stops):
                if stop >= entry:
                    continue

                exit_fill = settle_fill
                stopped = False
                false_stop = False

                if delayed_idx < len(ask):
                    stop_window = ask[delayed_idx:]
                    stop_mask = np.where(np.isnan(stop_window), False, stop_window <= stop)
                    stop_rel = _opt_first_true_index(stop_mask)
                    if stop_rel is not None:
                        stop_hit_index = delayed_idx + stop_rel
                        bid_value = bid[stop_hit_index]
                        if np.isnan(bid_value):
                            exit_fill = float(np.clip(float(stop) - exit_slip, 0.0, 99.0))
                        else:
                            exit_fill = float(np.clip(float(bid_value), 0.0, 99.0))
                        stopped = True
                        false_stop = false_stop_outcome

                pnl_share = float(exit_fill - entry_fill)
                estimated_trade_fees = estimate_kalshi_fee_dollars(entry_fill, position_size)
                if stopped:
                    estimated_trade_fees += estimate_kalshi_fee_dollars(exit_fill, position_size)
                sample_arr[entry_idx, stop_idx] += 1
                weighted_sample_arr[entry_idx, stop_idx] += weight
                pnl_arr[entry_idx, stop_idx] += pnl_share * weight
                fee_arr[entry_idx, stop_idx] += estimated_trade_fees * weight
                entry_fill_arr[entry_idx, stop_idx] += entry_fill * weight
                drawdown_arr[entry_idx, stop_idx] += max(entry_fill - min_after_entry, 0.0) * weight
                if not np.isnan(secs_to_close):
                    secs_to_close_arr[entry_idx, stop_idx] += secs_to_close * weight

                if pnl_share > 0:
                    win_arr[entry_idx, stop_idx] += weight
                    profit_sum_arr[entry_idx, stop_idx] += pnl_share * weight
                    winner_count_arr[entry_idx, stop_idx] += weight
                elif pnl_share < 0:
                    loss_sum_arr[entry_idx, stop_idx] += abs(pnl_share) * weight
                    loser_count_arr[entry_idx, stop_idx] += weight

                if stopped:
                    stop_hit_arr[entry_idx, stop_idx] += weight
                    stop_fill_arr[entry_idx, stop_idx] += exit_fill * weight
                    stop_fill_weight_arr[entry_idx, stop_idx] += weight
                    if false_stop:
                        false_stop_arr[entry_idx, stop_idx] += weight

    rows: list[dict[str, Any]] = []
    for entry_idx, entry in enumerate(entries):
        for stop_idx, stop in enumerate(stops):
            if stop >= entry:
                continue
            sample = int(sample_arr[entry_idx, stop_idx])
            if sample < provisional_min_sample:
                continue

            effective_weight = weighted_sample_arr[entry_idx, stop_idx] if weighted_sample_arr[entry_idx, stop_idx] > 0 else float(sample)
            exp_pnl_share = float(pnl_arr[entry_idx, stop_idx] / effective_weight)
            avg_entry_fill = float(entry_fill_arr[entry_idx, stop_idx] / effective_weight) if effective_weight > 0 else np.nan
            win_rate = float(win_arr[entry_idx, stop_idx] / effective_weight * 100.0) if effective_weight > 0 else 0.0
            stop_weight = float(stop_hit_arr[entry_idx, stop_idx])
            stop_hit_rate = float(stop_weight / effective_weight * 100.0) if effective_weight > 0 else 0.0
            false_stop_pct = float(false_stop_arr[entry_idx, stop_idx] / stop_weight * 100.0) if stop_weight > 0 else 0.0
            avg_loser = float(loss_sum_arr[entry_idx, stop_idx] / loser_count_arr[entry_idx, stop_idx]) if loser_count_arr[entry_idx, stop_idx] > 0 else 0.0
            avg_winner = float(profit_sum_arr[entry_idx, stop_idx] / winner_count_arr[entry_idx, stop_idx]) if winner_count_arr[entry_idx, stop_idx] > 0 else 0.0
            profit_factor = float(profit_sum_arr[entry_idx, stop_idx] / loss_sum_arr[entry_idx, stop_idx]) if loss_sum_arr[entry_idx, stop_idx] > 0 else (99.0 if profit_sum_arr[entry_idx, stop_idx] > 0 else 0.0)
            expected_stop_fill = float(stop_fill_arr[entry_idx, stop_idx] / stop_fill_weight_arr[entry_idx, stop_idx]) if stop_fill_weight_arr[entry_idx, stop_idx] > 0 else np.nan
            avg_drawdown = float(drawdown_arr[entry_idx, stop_idx] / effective_weight) if effective_weight > 0 else 0.0
            avg_secs_to_close = float(secs_to_close_arr[entry_idx, stop_idx] / effective_weight) if effective_weight > 0 else np.nan
            expected_return_pct = float((exp_pnl_share / avg_entry_fill) * 100.0) if avg_entry_fill and avg_entry_fill > 0 else 0.0
            estimated_fees_trade_dollars = float(fee_arr[entry_idx, stop_idx] / effective_weight) if effective_weight > 0 else 0.0
            expected_gross_trade_dollars = float(exp_pnl_share * position_size / 100.0)
            expected_net_trade_dollars = float(expected_gross_trade_dollars - estimated_fees_trade_dollars)
            deployed_trade_dollars = float(avg_entry_fill * position_size / 100.0) if avg_entry_fill and avg_entry_fill > 0 else np.nan
            expected_net_return_pct = float((expected_net_trade_dollars / deployed_trade_dollars) * 100.0) if deployed_trade_dollars and deployed_trade_dollars > 0 else np.nan
            confidence = "high" if sample >= max(min_sample, 10) else ("medium" if sample >= min_sample else "low")

            score = (
                exp_pnl_share
                + 0.018 * (win_rate - 50.0)
                - 0.015 * false_stop_pct
                - 0.010 * avg_loser
                + 0.003 * min(sample, 80)
                + 0.002 * min(profit_factor, 20.0)
                + (0.004 * min(avg_secs_to_close, 300.0) / 60.0 if not np.isnan(avg_secs_to_close) else 0.0)
                + 0.010 * min(stop_hit_rate, 25.0)
            )

            rows.append(
                {
                    "entry": int(entry),
                    "stop": int(stop),
                    "sample": sample,
                    "expected_pnl_share": round(exp_pnl_share, 4),
                    "expected_pnl_trade_dollars": round(expected_gross_trade_dollars, 4),
                    "estimated_fees_trade_dollars": round(estimated_fees_trade_dollars, 4),
                    "expected_net_pnl_trade_dollars": round(expected_net_trade_dollars, 4),
                    "expected_return_pct": round(expected_return_pct, 4),
                    "expected_net_return_pct": round(expected_net_return_pct, 4) if not np.isnan(expected_net_return_pct) else np.nan,
                    "deployed_trade_dollars": round(deployed_trade_dollars, 4) if not np.isnan(deployed_trade_dollars) else np.nan,
                    "win_rate": round(win_rate, 3),
                    "stop_hit_rate": round(stop_hit_rate, 3),
                    "false_stop_pct_of_stops": round(false_stop_pct, 3),
                    "avg_loser_share": round(avg_loser, 4),
                    "avg_winner_share": round(avg_winner, 4),
                    "profit_factor": round(profit_factor, 4),
                    "expected_stop_fill": round(expected_stop_fill, 4) if not np.isnan(expected_stop_fill) else np.nan,
                    "avg_entry_fill": round(avg_entry_fill, 4) if not np.isnan(avg_entry_fill) else np.nan,
                    "avg_drawdown_share": round(avg_drawdown, 4),
                    "avg_seconds_to_close_at_entry": round(avg_secs_to_close, 2) if not np.isnan(avg_secs_to_close) else np.nan,
                    "min_entry_seconds_to_close": int(max(int(min_entry_seconds_to_close), BOT_DELAY_SECONDS)),
                    "score": round(score, 6),
                    "confidence": confidence,
                }
            )

    if not rows:
        return pd.DataFrame()

    grid = pd.DataFrame(rows)
    strict = grid[(grid["sample"] >= min_sample) & (grid["stop_hit_rate"] >= 5.0)].copy()
    if strict.empty:
        strict = grid[grid["sample"] >= min_sample].copy()
    chosen = strict if not strict.empty else grid.copy()
    return chosen.sort_values(
        ["score", "expected_pnl_share", "stop_hit_rate", "win_rate", "sample"],
        ascending=[False, False, False, False, False],
    ).reset_index(drop=True)


def recommend_live_action_simple(latest_row: pd.Series | None, optimal_entry: float | None) -> tuple[str, str]:
    if latest_row is None or optimal_entry is None or pd.isna(optimal_entry):
        return "WAIT", "No live market reading available yet."
    yes_ask = pd.to_numeric(pd.Series([latest_row.get("yes_ask")]), errors="coerce").iloc[0]
    no_ask = pd.to_numeric(pd.Series([latest_row.get("no_ask")]), errors="coerce").iloc[0]
    if pd.notna(yes_ask) and yes_ask >= optimal_entry and (pd.isna(no_ask) or no_ask < optimal_entry):
        return "BUY YES", f"YES ask is {format_cents(yes_ask)} and NO ask is {format_cents(no_ask)}."
    if pd.notna(no_ask) and no_ask >= optimal_entry and (pd.isna(yes_ask) or yes_ask < optimal_entry):
        return "BUY NO", f"NO ask is {format_cents(no_ask)} and YES ask is {format_cents(yes_ask)}."
    visible = [v for v in [yes_ask, no_ask] if pd.notna(v)]
    if not visible:
        return "WAIT", "No valid YES or NO ask is visible right now."
    closest = max(visible)
    return "WAIT", f"Closest side is {format_cents(closest)} versus optimized entry {format_cents(optimal_entry)}."


def build_optimizer_recommendation_set(grid: pd.DataFrame) -> dict[str, pd.Series]:
    if grid.empty:
        return {}

    positive = grid[grid["expected_net_pnl_trade_dollars"] > 0].copy()
    usable = positive if not positive.empty else grid.copy()

    recommendations: dict[str, pd.Series] = {}
    recommendations["Balanced"] = usable.sort_values(
        ["score", "expected_net_pnl_trade_dollars", "stop_hit_rate", "sample"],
        ascending=[False, False, False, False],
    ).iloc[0]
    recommendations["Max expected P and L"] = usable.sort_values(
        ["expected_net_pnl_trade_dollars", "expected_pnl_trade_dollars", "profit_factor", "stop_hit_rate", "sample"],
        ascending=[False, False, False, False, False],
    ).iloc[0]
    recommendations["Best profit factor"] = usable.sort_values(
        ["profit_factor", "expected_net_pnl_trade_dollars", "stop_hit_rate", "sample"],
        ascending=[False, False, False, False],
    ).iloc[0]
    return recommendations


def find_strategy_row(grid: pd.DataFrame, entry: int | float, stop: int | float) -> pd.Series | None:
    if grid.empty:
        return None
    match = grid[(grid["entry"] == int(entry)) & (grid["stop"] == int(stop))]
    if match.empty:
        return None
    return match.iloc[0]



def resolve_research_root_for_dataset(dataset_tag: str) -> Path:
    tag = str(dataset_tag or "").strip()
    if tag in VIRTUAL_DATASET_CONFIGS:
        source_tag = str(VIRTUAL_DATASET_CONFIGS[tag].get("source_tag") or tag)
    elif tag == "entry_95_late_momentum":
        source_tag = "live_95_momentum"
    elif tag == "entry_87_ladder_hold":
        source_tag = "live_87_77_67"
    elif tag == "entry_90_stop_70":
        source_tag = "live_90_70"
    elif tag == "entry_90_stop_78":
        source_tag = "live_90_78"
    else:
        source_tag = tag
    return ROOT / "research_data" / source_tag


def render_research_backed_strategy_optimizer(
    active_dataset_tag: str,
    latest_watch: dict[str, Any] | None,
    latest_heartbeat: dict[str, Any] | None,
) -> bool:
    research_root = resolve_research_root_for_dataset(active_dataset_tag)
    replay_summary_df = load_latest_replay_summary(str(research_root))
    direct_replay_summary_df = load_latest_direct_replay_summary(str(research_root))
    direct_replay_trades_df = load_latest_direct_replay_trades(str(research_root))
    optimizer_summary_df = load_latest_optimizer_summary(str(research_root))
    optimizer_trades_df = load_latest_optimizer_trades(str(research_root))
    features_df = pd.DataFrame()
    snapshot = load_research_lab_snapshot(str(research_root))

    if replay_summary_df.empty and direct_replay_summary_df.empty and optimizer_summary_df.empty and features_df.empty:
        return False

    st.markdown("## Strategy optimizer")
    st.caption("Research-backed optimizer driven by replay summaries, direct quote replay, and the live feature store from Research Lab.")

    replay_work = replay_summary_df.copy() if not replay_summary_df.empty else pd.DataFrame()
    if not replay_work.empty:
        numeric_cols = [
            "trades_kept", "trades_blocked", "kept_net_pnl_dollars", "blocked_net_pnl_dollars",
            "baseline_net_pnl_dollars", "kept_win_rate", "baseline_win_rate", "avg_submit_latency_ms",
            "avg_feed_age_ms", "avg_same_side_range_30s",
        ]
        for col in numeric_cols:
            if col in replay_work.columns:
                replay_work[col] = pd.to_numeric(replay_work[col], errors="coerce")
        replay_work = replay_work.sort_values(["kept_net_pnl_dollars", "trades_kept"], ascending=[False, False]).reset_index(drop=True)

    direct_work = direct_replay_summary_df.copy() if not direct_replay_summary_df.empty else pd.DataFrame()
    if not direct_work.empty:
        for col in ["trades", "wins", "losses", "stopped_trades", "settled_trades", "net_pnl_dollars", "avg_pnl_dollars", "win_rate"]:
            if col in direct_work.columns:
                direct_work[col] = pd.to_numeric(direct_work[col], errors="coerce")
        direct_work = direct_work.sort_values(["net_pnl_dollars", "win_rate"], ascending=[False, False]).reset_index(drop=True)

    objective = st.radio(
        "Recommendation objective",
        ["Balanced", "Max net P and L", "Highest win rate", "Calmest entries"],
        horizontal=True,
        key=f"research_optimizer_objective_{active_dataset_tag}",
        help="This keeps the old optimizer-style objective selector, but it now ranks replay scenarios from the research database.",
    )

    baseline_replay = replay_work[replay_work["scenario"] == "baseline"].iloc[0] if (not replay_work.empty and (replay_work["scenario"] == "baseline").any()) else None
    best_replay = None
    if not replay_work.empty:
        replay_candidates = replay_work.copy()
        if objective == "Max net P and L":
            replay_candidates = replay_candidates.sort_values(["kept_net_pnl_dollars", "kept_win_rate", "trades_kept"], ascending=[False, False, False])
        elif objective == "Highest win rate":
            replay_candidates = replay_candidates.sort_values(["kept_win_rate", "kept_net_pnl_dollars", "trades_kept"], ascending=[False, False, False])
        elif objective == "Calmest entries":
            replay_candidates = replay_candidates.sort_values(["avg_same_side_range_30s", "kept_net_pnl_dollars", "kept_win_rate"], ascending=[True, False, False])
        else:
            replay_candidates = replay_candidates.sort_values(["kept_net_pnl_dollars", "kept_win_rate", "trades_blocked"], ascending=[False, False, True])
        best_replay = replay_candidates.iloc[0]
    best_direct = direct_work.iloc[0] if not direct_work.empty else None
    optimizer_work = optimizer_summary_df.copy() if not optimizer_summary_df.empty else pd.DataFrame()
    if not optimizer_work.empty:
        for col in ['entry_limit_cents', 'entry_floor_cents', 'stop_cents', 'panic_cents', 'trades', 'wins', 'losses', 'stopped_trades', 'settled_trades', 'false_stop_like_count', 'false_stop_like_rate', 'net_pnl_dollars', 'avg_pnl_dollars', 'win_rate', 'avg_win_dollars', 'avg_loss_dollars', 'worst_trade_dollars', 'score_balanced']:
            if col in optimizer_work.columns:
                optimizer_work[col] = pd.to_numeric(optimizer_work[col], errors='coerce')
        if objective == 'Max net P and L':
            optimizer_work = optimizer_work.sort_values(['net_pnl_dollars', 'win_rate', 'trades'], ascending=[False, False, False]).reset_index(drop=True)
        elif objective == 'Highest win rate':
            optimizer_work = optimizer_work.sort_values(['win_rate', 'net_pnl_dollars', 'trades'], ascending=[False, False, False]).reset_index(drop=True)
        elif objective == 'Calmest entries':
            optimizer_work = optimizer_work.sort_values(['entry_limit_cents', 'net_pnl_dollars', 'win_rate'], ascending=[True, False, False]).reset_index(drop=True)
        else:
            optimizer_work = optimizer_work.sort_values(['score_balanced', 'net_pnl_dollars', 'win_rate'], ascending=[False, False, False]).reset_index(drop=True)
    best_optimizer = optimizer_work.iloc[0] if not optimizer_work.empty else None

    current_market = None
    if latest_watch and latest_watch.get("market"):
        current_market = str(latest_watch.get("market")).strip().upper()
    elif latest_heartbeat and latest_heartbeat.get("watch"):
        current_market = str(latest_heartbeat.get("watch")).strip().upper()

    latest_feature_row = None
    if current_market:
        feat_work = load_research_market_feature_slice(str(research_root), current_market)
        if not feat_work.empty:
            latest_feature_row = feat_work.iloc[-1]

    pipeline_status = snapshot.get("pipeline_status", {}) if isinstance(snapshot, dict) else {}
    lag_delta = None
    try:
        raw_ts = pipeline_status.get("latest_raw_event_ts")
        feature_ts = pipeline_status.get("latest_feature_ts")
        if raw_ts and feature_ts:
            lag_delta = max(0.0, (pd.Timestamp(raw_ts) - pd.Timestamp(feature_ts)).total_seconds())
    except Exception:
        lag_delta = None

    top_cols = st.columns(5)
    top_cols[0].metric(
        "Best replay scenario",
        str(best_optimizer['scenario']) if best_optimizer is not None else (str(best_replay["scenario"]) if best_replay is not None else "NA"),
        delta=(
            f"vs baseline {format_money(float(best_replay.get('kept_net_pnl_dollars', 0.0)) - float(baseline_replay.get('baseline_net_pnl_dollars', 0.0)))}"
            if best_replay is not None and baseline_replay is not None
            else "research replay"
        ),
        border=True,
    )
    top_cols[1].metric(
        "Replay net P&L",
        format_money(float(best_optimizer.get('net_pnl_dollars', 0.0))) if best_optimizer is not None else (format_money(float(best_replay.get("kept_net_pnl_dollars", 0.0))) if best_replay is not None else "NA"),
        delta=(f"baseline {format_money(float(baseline_replay.get('baseline_net_pnl_dollars', 0.0)))}" if baseline_replay is not None else "NA"),
        border=True,
    )
    top_cols[2].metric(
        "Trades / false stops",
        (f"{int(best_optimizer.get('trades', 0)):,}" if best_optimizer is not None else f"{int(best_replay.get('trades_kept', 0)):,}") if (best_optimizer is not None or best_replay is not None) else "NA",
        delta=(f"false stops {int(best_optimizer.get('false_stop_like_count', 0)):,}" if best_optimizer is not None else (f"kept {int(best_replay.get('trades_kept', 0)):,}" if best_replay is not None else "NA")),
        border=True,
    )
    top_cols[3].metric(
        "Direct quote replay",
        str(best_direct["scenario"]) if best_direct is not None else "NA",
        delta=(f"{format_money(float(best_direct.get('net_pnl_dollars', 0.0)))} | {format_pct(float(best_direct.get('win_rate', np.nan)))}" if best_direct is not None else "NA"),
        border=True,
    )
    top_cols[4].metric(
        "Research lag",
        f"{lag_delta/60.0:.1f} min" if lag_delta is not None else "NA",
        delta=(format_ma_time(pipeline_status.get("latest_feature_ts")) if pipeline_status.get("latest_feature_ts") else "no features"),
        border=True,
    )

    if best_optimizer is not None:
        st.markdown(
            f"Best raw-recorder optimizer rule for **{objective}** is **{best_optimizer['scenario']}**. "
            f"It models **{int(best_optimizer['trades'])}** trades, **{format_pct(float(best_optimizer['win_rate']))}** win rate, "
            f"and **{format_money(float(best_optimizer['net_pnl_dollars']))}** net P&L with **{int(best_optimizer['false_stop_like_count'])}** false-stop-like exits."
        )
    elif best_replay is not None:
        st.markdown(
            f"Best research-backed rule for **{objective}** is **{best_replay['scenario']}**. "
            f"It keeps **{int(best_replay['trades_kept'])}** trades, blocks **{int(best_replay['trades_blocked'])}**, "
            f"and improves modeled net P&L from **{format_money(float(best_replay['baseline_net_pnl_dollars']))}** to **{format_money(float(best_replay['kept_net_pnl_dollars']))}**."
        )

    if latest_feature_row is not None:
        yes_range = pd.to_numeric(pd.Series([latest_feature_row.get("yes_range_30s")]), errors="coerce").iloc[0]
        no_range = pd.to_numeric(pd.Series([latest_feature_row.get("no_range_30s")]), errors="coerce").iloc[0]
        current_bias = "YES" if pd.notna(yes_range) and (pd.isna(no_range) or yes_range <= no_range) else "NO"
        current_range = yes_range if current_bias == "YES" else no_range
        gate_state = "Calm enough" if pd.notna(current_range) and current_range <= 8 else "Too volatile"
        if pd.notna(current_range):
            st.info(
                f"Current market feature state for {current_market}: preferred side by lower 30s range is {current_bias}. "
                f"Same-side range is {current_range:.2f}c. Research gate read: {gate_state}."
            )
        else:
            st.info(f"Current market feature state for {current_market} is available, but the 30s range fields are not populated on the latest row yet.")

    left, right = st.columns([1.2, 0.8], gap="large")
    with left:
        st.markdown("### Suggested strategy profiles")
        if not optimizer_work.empty:
            leaderboard = optimizer_work.copy()
            leaderboard['Scenario'] = leaderboard['scenario'].astype(str)
            leaderboard['Net P&L'] = leaderboard['net_pnl_dollars'].apply(format_money)
            leaderboard['Win rate'] = leaderboard['win_rate'].apply(format_pct)
            leaderboard['Avg P&L'] = leaderboard['avg_pnl_dollars'].apply(format_money)
            leaderboard['False-stop rate'] = leaderboard['false_stop_like_rate'].map(lambda v: 'NA' if pd.isna(v) else format_pct(float(v)))
            st.dataframe(leaderboard[['Scenario', 'entry_limit_cents', 'stop_cents', 'panic_cents', 'trades', 'Net P&L', 'Win rate', 'Avg P&L', 'False-stop rate', 'worst_trade_dollars']], use_container_width=True, hide_index=True)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=optimizer_work['scenario'],
                y=optimizer_work['net_pnl_dollars'],
                marker_color=['#36e28f' if best_optimizer is not None and str(s) == str(best_optimizer['scenario']) else '#6dc8ff' for s in optimizer_work['scenario']],
                customdata=np.stack([
                    optimizer_work['win_rate'].to_numpy(dtype=float),
                    optimizer_work['false_stop_like_count'].to_numpy(dtype=float),
                    optimizer_work['trades'].to_numpy(dtype=float),
                ], axis=1),
                hovertemplate='Scenario %{x}<br>Net %{y:$,.2f}<br>Win rate %{customdata[0]:.2f}%<br>False stops %{customdata[1]:.0f}<br>Trades %{customdata[2]:.0f}<extra></extra>',
            ))
            fig.update_layout(height=340, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title='Scenario', yaxis_title='Net P&L')
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.08)')
            st.plotly_chart(fig, width='stretch')

            compare_rows = []
            if best_optimizer is not None:
                compare_rows.append({
                    'View': 'Best raw-recorder optimizer',
                    'Scenario': str(best_optimizer['scenario']),
                    'Trades': int(best_optimizer.get('trades', 0)),
                    'Net P and L': format_money(float(best_optimizer.get('net_pnl_dollars', 0.0))),
                    'Win rate': format_pct(float(best_optimizer.get('win_rate', np.nan))),
                    'Blocked': int(best_optimizer.get('false_stop_like_count', 0)),
                })
            if best_direct is not None:
                compare_rows.append({
                    'View': 'Best direct quote replay',
                    'Scenario': str(best_direct['scenario']),
                    'Trades': int(best_direct.get('trades', 0)),
                    'Net P and L': format_money(float(best_direct.get('net_pnl_dollars', 0.0))),
                    'Win rate': format_pct(float(best_direct.get('win_rate', np.nan))),
                    'Blocked': int(best_direct.get('stopped_trades', 0)),
                })
            if baseline_replay is not None:
                compare_rows.append({
                    'View': 'Replay baseline',
                    'Scenario': str(baseline_replay['scenario']),
                    'Trades': int(baseline_replay.get('trades_kept', 0)),
                    'Net P and L': format_money(float(baseline_replay.get('kept_net_pnl_dollars', 0.0))),
                    'Win rate': format_pct(float(baseline_replay.get('kept_win_rate', np.nan))),
                    'Blocked': int(baseline_replay.get('trades_blocked', 0)),
                })
            if compare_rows:
                st.markdown('### Profitability cross-check')
                st.caption('This compares the new raw-recorder sweep with the older replay summaries so you can see whether the optimizer is pointing somewhere materially different.')
                st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)
        elif replay_work.empty:
            st.info("No replay summaries are available yet.")
        else:
            leaderboard = replay_work.copy()
            leaderboard["Scenario"] = leaderboard["scenario"].astype(str)
            leaderboard["Net P&L"] = leaderboard["kept_net_pnl_dollars"].apply(format_money)
            leaderboard["Baseline net"] = leaderboard["baseline_net_pnl_dollars"].apply(format_money)
            leaderboard["Win rate"] = leaderboard["kept_win_rate"].apply(format_pct)
            leaderboard["Avg feed age"] = leaderboard["avg_feed_age_ms"].map(lambda v: "NA" if pd.isna(v) else f"{float(v):.1f} ms")
            leaderboard["Avg same-side 30s range"] = leaderboard["avg_same_side_range_30s"].map(lambda v: "NA" if pd.isna(v) else f"{float(v):.2f}c")
            st.dataframe(
                leaderboard[["Scenario", "trades_kept", "trades_blocked", "Net P&L", "Baseline net", "Win rate", "Avg feed age", "Avg same-side 30s range"]],
                use_container_width=True,
                hide_index=True,
            )
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=replay_work["scenario"],
                y=replay_work["kept_net_pnl_dollars"],
                marker_color=["#36e28f" if best_replay is not None and str(s) == str(best_replay["scenario"]) else "#6dc8ff" for s in replay_work["scenario"]],
                customdata=np.stack([
                    replay_work["baseline_net_pnl_dollars"].to_numpy(dtype=float),
                    replay_work["trades_blocked"].to_numpy(dtype=float),
                    replay_work["kept_win_rate"].to_numpy(dtype=float),
                ], axis=1),
                hovertemplate="Scenario %{x}<br>Net %{y:$,.2f}<br>Baseline %{customdata[0]:$,.2f}<br>Blocked %{customdata[1]:.0f}<br>Win rate %{customdata[2]:.2f}%<extra></extra>",
            ))
            fig.update_layout(height=340, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Scenario", yaxis_title="Net P&L")
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
            st.plotly_chart(fig, width="stretch")

            compare_rows = []
            if best_replay is not None:
                compare_rows.append({
                    "View": "Selected replay scenario",
                    "Scenario": str(best_replay["scenario"]),
                    "Trades": int(best_replay.get("trades_kept", 0)),
                    "Net P and L": format_money(float(best_replay.get("kept_net_pnl_dollars", 0.0))),
                    "Win rate": format_pct(float(best_replay.get("kept_win_rate", np.nan))),
                    "Blocked": int(best_replay.get("trades_blocked", 0)),
                })
            if baseline_replay is not None:
                compare_rows.append({
                    "View": "Replay baseline",
                    "Scenario": str(baseline_replay["scenario"]),
                    "Trades": int(baseline_replay.get("trades_kept", 0)),
                    "Net P and L": format_money(float(baseline_replay.get("kept_net_pnl_dollars", 0.0))),
                    "Win rate": format_pct(float(baseline_replay.get("kept_win_rate", np.nan))),
                    "Blocked": int(baseline_replay.get("trades_blocked", 0)),
                })
            if best_direct is not None:
                compare_rows.append({
                    "View": "Best direct quote replay",
                    "Scenario": str(best_direct["scenario"]),
                    "Trades": int(best_direct.get("trades", 0)),
                    "Net P and L": format_money(float(best_direct.get("net_pnl_dollars", 0.0))),
                    "Win rate": format_pct(float(best_direct.get("win_rate", np.nan))),
                    "Blocked": int(best_direct.get("stopped_trades", 0)),
                })
            if compare_rows:
                st.markdown("### Profitability cross-check")
                st.caption("This preserves the old selected-versus-baseline workflow, but the rows now come from research replay artifacts instead of the legacy log parser.")
                st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)

    with right:
        st.markdown("### Direct quote replay")
        if direct_work.empty:
            st.info("No direct quote replay summary is available yet.")
        else:
            direct_table = direct_work.copy()
            direct_table["Scenario"] = direct_table["scenario"].astype(str)
            direct_table["Net P&L"] = direct_table["net_pnl_dollars"].apply(format_money)
            direct_table["Avg P&L"] = direct_table["avg_pnl_dollars"].apply(format_money)
            direct_table["Win rate"] = direct_table["win_rate"].apply(format_pct)
            st.dataframe(
                direct_table[["Scenario", "trades", "wins", "losses", "stopped_trades", "Net P&L", "Avg P&L", "Win rate"]],
                use_container_width=True,
                hide_index=True,
            )
            if not direct_replay_trades_df.empty:
                trades = direct_replay_trades_df.copy()
                trades["net_pnl_dollars"] = pd.to_numeric(trades.get("net_pnl_dollars"), errors="coerce")
                worst = trades.sort_values("net_pnl_dollars").head(8).copy()
                worst["entry_ts"] = pd.to_datetime(worst.get("entry_ts"), utc=True, errors="coerce")
                worst["exit_ts"] = pd.to_datetime(worst.get("exit_ts"), utc=True, errors="coerce")
                worst["Entry"] = worst["entry_ts"].map(format_ma_time)
                worst["Exit"] = worst["exit_ts"].map(format_ma_time)
                worst["Net P&L"] = worst["net_pnl_dollars"].apply(format_money)
                st.markdown("#### Worst replayed losses")
                st.dataframe(
                    worst[["scenario", "market", "side", "Entry", "Exit", "entry_price_cents", "exit_price_cents", "exit_reason", "market_result", "Net P&L"]],
                    use_container_width=True,
                    hide_index=True,
                )

    st.markdown("### Research-backed recommendation")
    recommendation_lines = []
    if best_optimizer is not None:
        recommendation_lines.append(f"Best raw-recorder sweep currently points to `{best_optimizer['scenario']}` at {format_money(float(best_optimizer['net_pnl_dollars']))}, with {format_pct(float(best_optimizer['win_rate']))} win rate and {int(best_optimizer['false_stop_like_count'])} false-stop-like exits.")
    if best_replay is not None and str(best_replay.get("scenario")) == "range30_le_8":
        recommendation_lines.append("Keep the new `same_side_range_30s <= 8c` live gate enabled. The replay summary still ranks it as the best current filter.")
    elif best_replay is not None:
        recommendation_lines.append(f"Current best replay filter is `{best_replay['scenario']}`. The live bot should be aligned to that scenario rather than the older legacy optimizer output.")
    if best_direct is not None:
        recommendation_lines.append(f"Direct quote replay is still weakest on `{best_direct['scenario']}` at {format_money(float(best_direct['net_pnl_dollars']))}, which means stop behavior remains the next bigger lever after entry gating.")
    if latest_feature_row is not None:
        recommendation_lines.append("Use the current market's 30-second range in the top-fold context: if it is already above the threshold, the bot should wait rather than chase.")
    if not recommendation_lines:
        recommendation_lines.append("Research outputs exist, but there is not enough structured replay data yet to make a stronger optimizer recommendation.")
    for line in recommendation_lines:
        st.markdown(f"- {line}")
    return True


def render_strategy_optimizer_tab(
    price_all: pd.DataFrame,
    all_lines: list[str],
    summary: dict[str, Any],
    latest_watch: dict[str, Any] | None,
    latest_heartbeat: dict[str, Any] | None,
    market_results_df: pd.DataFrame,
    trades_df: pd.DataFrame,
    active_dataset_tag: str,
) -> None:
    if render_research_backed_strategy_optimizer(active_dataset_tag, latest_watch, latest_heartbeat):
        return

    st.markdown("## Strategy optimizer")
    st.caption("Simple resolved market optimizer for BTC15M only. It recommends one evolving entry trigger and one evolving stop loss trigger based on your logged market history.")

    profile = infer_strategy_profile(active_dataset_tag, trades_df)
    baseline_entry_cents = int(profile["entry"])
    baseline_stop_cents = int(profile["stop"])
    baseline_position_size = int(profile["position_size"])

    optimizer_trades = trades_df.copy() if trades_df is not None else pd.DataFrame()
    if not optimizer_trades.empty:
        if "entry_trigger_cents" in optimizer_trades.columns:
            optimizer_trades = optimizer_trades[
                pd.to_numeric(optimizer_trades["entry_trigger_cents"], errors="coerce") == baseline_entry_cents
            ].copy()
        if "qty" in optimizer_trades.columns:
            matching_qty = optimizer_trades[
                pd.to_numeric(optimizer_trades["qty"], errors="coerce") == baseline_position_size
            ].copy()
            if not matching_qty.empty:
                optimizer_trades = matching_qty

    market_results = market_results_df.copy()
    if market_results.empty:
        st.warning("stats/market_results.csv was not found yet. Run the scorer first.")
        return

    current_market = None
    if latest_watch and latest_watch.get("market"):
        current_market = str(latest_watch.get("market")).strip().upper()
    elif latest_heartbeat and latest_heartbeat.get("watch"):
        current_market = str(latest_heartbeat.get("watch")).strip().upper()

    resolved = market_results[market_results["result"].isin(["yes", "no"])].copy()
    if current_market:
        resolved = resolved[resolved["market"] != current_market].copy()
    if resolved.empty:
        st.warning("No resolved BTC15M markets are available yet for optimization.")
        return

    if price_all.empty:
        st.warning("No heartbeat price history was found in the logs yet.")
        return

    available_markets = set(price_all["market"].dropna().astype(str).unique().tolist())
    resolved["market"] = resolved["market"].astype(str)
    resolved = resolved[resolved["market"].isin(available_markets)].copy()
    if resolved.empty:
        st.warning("Resolved outcomes exist, but there are no matching historical heartbeat paths for those markets in logs.")
        return

    resolved = resolved.drop_duplicates(subset=["market"], keep="last").copy()
    if MAX_OPTIMIZER_MARKETS is not None and len(resolved) > MAX_OPTIMIZER_MARKETS:
        resolved = resolved.tail(MAX_OPTIMIZER_MARKETS).copy()

    training_markets = resolved["market"].dropna().astype(str).str.upper().tolist()
    training_price = price_all[price_all["market"].astype(str).str.upper().isin(training_markets)].copy()
    optimizer_trade_count = int(len(optimizer_trades)) if optimizer_trades is not None else 0
    data_summary_cols = st.columns(4)
    data_summary_cols[0].metric("Resolved markets", f"{len(resolved):,}")
    data_summary_cols[1].metric("Markets with usable paths", f"{len(training_markets):,}")
    data_summary_cols[3].metric("Scored trades used", f"{optimizer_trade_count:,}", delta=humanize_strategy_tag(active_dataset_tag))
    min_entry_seconds_to_close = st.slider(
        "Minimum seconds to close at entry",
        min_value=max(BOT_DELAY_SECONDS, 30),
        max_value=300,
        value=180,
        step=15,
        help="Ignore threshold crossings that happen too close to settlement. The default favors settings that still leave enough market life for the stop logic to matter.",
    )

    signal_df = parse_optimizer_signal_rows(all_lines)
    if not signal_df.empty:
        signal_df["market"] = signal_df["market"].astype(str).str.upper()
        signal_df = signal_df[signal_df["market"].isin(training_markets)].copy()
        if "qty" in signal_df.columns:
            matching_signal_qty = signal_df[pd.to_numeric(signal_df["qty"], errors="coerce") == baseline_position_size].copy()
            if not matching_signal_qty.empty:
                signal_df = matching_signal_qty
    data_summary_cols[2].metric("Signal rows used", f"{len(signal_df):,}")

    latest_row = None
    if current_market:
        current_rows = price_all[price_all["market"].astype(str) == current_market].sort_values("ts")
        if not current_rows.empty:
            latest_row = current_rows.iloc[-1]
    if latest_row is None and latest_heartbeat:
        latest_row = pd.Series(
            {
                "market": latest_heartbeat.get("watch"),
                "yes_bid": latest_heartbeat.get("yes_bid"),
                "yes_ask": latest_heartbeat.get("yes_ask"),
                "no_bid": latest_heartbeat.get("no_bid"),
                "no_ask": latest_heartbeat.get("no_ask"),
            }
        )

    grid = optimize_entry_stop_grid(
        training_price,
        resolved[["market", "result", "close_time_dt"]].copy(),
        signal_df,
        min_entry_seconds_to_close=min_entry_seconds_to_close,
        max_markets=MAX_OPTIMIZER_MARKETS,
        recency_weighted=True,
        position_size=baseline_position_size,
    )

    if grid.empty:
        st.warning(
            f"The optimizer still found no usable parameter tests. Resolved markets with paths: {len(training_markets)} | "
            f"price rows: {len(training_price)} | signal rows: {len(signal_df)}"
        )
        return

    recommendations = build_optimizer_recommendation_set(grid)
    objective = st.radio(
        "Recommendation objective",
        ["Balanced", "Max expected P and L", "Best profit factor"],
        horizontal=True,
        help="Balanced uses the optimizer score. The other modes force the recommendation toward raw expectancy or risk-adjusted efficiency.",
    )
    best = recommendations.get(objective, grid.iloc[0])
    all_history_resolved = market_results[market_results["result"].isin(["yes", "no"])].copy()
    if current_market:
        all_history_resolved = all_history_resolved[all_history_resolved["market"] != current_market].copy()
    all_history_markets = all_history_resolved["market"].dropna().astype(str).str.upper().tolist()
    all_history_price = price_all[price_all["market"].astype(str).str.upper().isin(all_history_markets)].copy()
    all_history_signal_df = parse_optimizer_signal_rows(all_lines)
    if not all_history_signal_df.empty:
        all_history_signal_df["market"] = all_history_signal_df["market"].astype(str).str.upper()
        all_history_signal_df = all_history_signal_df[all_history_signal_df["market"].isin(all_history_markets)].copy()
        if "qty" in all_history_signal_df.columns:
            matching_all_signal_qty = all_history_signal_df[pd.to_numeric(all_history_signal_df["qty"], errors="coerce") == baseline_position_size].copy()
            if not matching_all_signal_qty.empty:
                all_history_signal_df = matching_all_signal_qty
    all_history_grid = optimize_entry_stop_grid(
        all_history_price,
        all_history_resolved[["market", "result", "close_time_dt"]].copy(),
        all_history_signal_df,
        min_entry_seconds_to_close=0,
        max_markets=None,
        recency_weighted=False,
        position_size=baseline_position_size,
    )
    baseline = grid[(grid["entry"] == baseline_entry_cents) & (grid["stop"] == baseline_stop_cents)]
    baseline_row = baseline.iloc[0] if not baseline.empty else None
    best_all_history_row = find_strategy_row(all_history_grid, best["entry"], best["stop"])
    baseline_all_history_row = find_strategy_row(all_history_grid, baseline_entry_cents, baseline_stop_cents)
    live_action, live_note = recommend_live_action_simple(latest_row, float(best["entry"]))
    stop_fill_value, stop_fill_note = describe_stop_fill(best.get("expected_stop_fill"))

    expected_trade_cost_dollars = float((pd.to_numeric(pd.Series([best.get("avg_entry_fill")]), errors="coerce").iloc[0] or baseline_entry_cents) * baseline_position_size / 100.0)
    expected_net_profit_trade_dollars = float(best.get("expected_net_pnl_trade_dollars") or 0.0)
    expected_profitability_trade_pct = (expected_net_profit_trade_dollars / expected_trade_cost_dollars * 100.0) if expected_trade_cost_dollars > 0 else np.nan

    weekly_trade_count_est = np.nan
    if not optimizer_trades.empty and "entry_ts" in optimizer_trades.columns:
        trade_times = pd.to_datetime(optimizer_trades["entry_ts"], errors="coerce").dropna().sort_values()
        if len(trade_times) >= 2:
            span_days = max((trade_times.iloc[-1] - trade_times.iloc[0]).total_seconds() / 86400.0, 1.0)
            weekly_trade_count_est = float(len(trade_times) / span_days * 7.0)
        elif len(trade_times) == 1:
            weekly_trade_count_est = 7.0
    if pd.isna(weekly_trade_count_est):
        weekly_trade_count_est = float(max(int(best.get("sample") or 0), 1))

    expected_weekly_profit_dollars = expected_net_profit_trade_dollars * weekly_trade_count_est
    expected_weekly_gain_pct = (expected_weekly_profit_dollars / expected_trade_cost_dollars * 100.0) if expected_trade_cost_dollars > 0 else np.nan

    baseline_expected_trade_cost_dollars = np.nan
    baseline_expected_net_profit_trade_dollars = np.nan
    baseline_expected_profitability_trade_pct = np.nan
    baseline_expected_weekly_profit_dollars = np.nan
    baseline_expected_weekly_gain_pct = np.nan
    if baseline_row is not None:
        baseline_expected_trade_cost_dollars = float((pd.to_numeric(pd.Series([baseline_row.get("avg_entry_fill")]), errors="coerce").iloc[0] or baseline_entry_cents) * baseline_position_size / 100.0)
        baseline_expected_net_profit_trade_dollars = float(baseline_row.get("expected_net_pnl_trade_dollars") or 0.0)
        if baseline_expected_trade_cost_dollars > 0:
            baseline_expected_profitability_trade_pct = (baseline_expected_net_profit_trade_dollars / baseline_expected_trade_cost_dollars) * 100.0
            baseline_expected_weekly_profit_dollars = baseline_expected_net_profit_trade_dollars * weekly_trade_count_est
            baseline_expected_weekly_gain_pct = (baseline_expected_weekly_profit_dollars / baseline_expected_trade_cost_dollars) * 100.0

    profitability_delta_text = (
        f"current {baseline_expected_profitability_trade_pct:+.2f}%"
        if pd.notna(baseline_expected_profitability_trade_pct)
        else f"vs {format_money(expected_trade_cost_dollars)} deployed"
    )
    net_trade_delta_text = (
        f"current {format_money(baseline_expected_net_profit_trade_dollars)} | {baseline_expected_profitability_trade_pct:+.2f}%"
        if pd.notna(baseline_expected_profitability_trade_pct)
        else f"{format_pct(expected_profitability_trade_pct)} | vs {format_money(expected_trade_cost_dollars)} deployed"
    )
    weekly_profit_delta_text = (
        f"current {format_money(baseline_expected_weekly_profit_dollars)} | {baseline_expected_weekly_gain_pct:+.2f}%"
        if pd.notna(baseline_expected_weekly_gain_pct)
        else f"{format_pct(expected_weekly_gain_pct)} | vs {format_money(expected_trade_cost_dollars)} deployed"
    )
    weekly_gain_delta_text = (
        f"current {baseline_expected_weekly_gain_pct:+.2f}%"
        if pd.notna(baseline_expected_weekly_gain_pct)
        else f"vs {format_money(expected_trade_cost_dollars)} deployed"
    )

    if str(best.get("confidence", "medium")).lower() == "low":
        st.info("Using a provisional recommendation because the current historical sample is still thin.")
    if float(best.get("avg_seconds_to_close_at_entry") or 0) < 180:
        st.warning("The current best setting is still driven by relatively late entries. If the landscape looks collapsed, increase the minimum seconds-to-close control.")

    alt_rows = []
    for label, row in recommendations.items():
        alt_rows.append(
            {
                "Profile": label,
                "Entry": format_cents(row["entry"]),
                "Stop": format_cents(row["stop"]),
                "Expected net P and L": format_money(row["expected_net_pnl_trade_dollars"]),
                "Estimated fees": format_money(row["estimated_fees_trade_dollars"]),
                "Profit factor": f"{float(row['profit_factor']):,.2f}",
                "Win rate": format_pct(row["win_rate"]),
                "Stop hit rate": format_pct(row["stop_hit_rate"]),
                "Sample": int(row["sample"]),
            }
        )
    if alt_rows:
        st.markdown("### Suggested strategy profiles")
        st.dataframe(pd.DataFrame(alt_rows), use_container_width=True, hide_index=True)

    expected_net_profit_trade_pct = expected_profitability_trade_pct

    row1 = st.columns(5)
    row1[0].metric("Current optimal entry", format_cents(best["entry"]), delta=f"bot locked at {baseline_entry_cents}c", border=True)
    row1[1].metric("Current optimal stop", format_cents(best["stop"]), delta=f"bot locked at {baseline_stop_cents}c", border=True)
    row1[2].metric("Expected profitability / trade", format_pct(expected_profitability_trade_pct), delta=profitability_delta_text, border=True)
    row1[3].metric("Expected net profit / trade", format_money(expected_net_profit_trade_dollars), delta=net_trade_delta_text, border=True)
    row1[4].metric("Win rate", format_pct(best["win_rate"]), delta=f"sample {int(best['sample'])}", border=True)

    row2 = st.columns(5)
    row2[0].metric("Expected 1 week profit", format_money(expected_weekly_profit_dollars), delta=weekly_profit_delta_text, border=True)
    row2[1].metric("Expected 1 week gain", format_pct(expected_weekly_gain_pct), delta=weekly_gain_delta_text, border=True)
    row2[2].metric("Action now", live_action, delta=live_note, border=True)
    row2[3].metric("Modeled stop fill", stop_fill_value, delta=stop_fill_note, border=True)
    row2[4].metric("Stop hit rate", format_pct(best["stop_hit_rate"]), delta=f"false stops {format_pct(best['false_stop_pct_of_stops'])}", border=True)

    row3 = st.columns(4)
    row3[0].metric("Markets scanned", f"{len(training_markets)}", delta=f"{BOT_DELAY_SECONDS}s delay modeled | min {min_entry_seconds_to_close}s to close | {str(best.get('confidence', 'medium')).title()} confidence", border=True)
    row3[1].metric("Avg seconds to close at entry", f"{float(best.get('avg_seconds_to_close_at_entry') or 0):,.0f}s", border=True)
    row3[2].metric("Baseline expected net", format_money(baseline_row["expected_net_pnl_trade_dollars"]) if baseline_row is not None else "NA", border=True)
    row3[3].metric("Baseline avg seconds to close", f"{float(baseline_row.get('avg_seconds_to_close_at_entry') or 0):,.0f}s" if baseline_row is not None else "NA", border=True)

    compare_rows = [
        {
            "View": "Selected strategy | recent weighted",
            "Entry": format_cents(best["entry"]),
            "Stop": format_cents(best["stop"]),
            "Expected net P and L": format_money(best["expected_net_pnl_trade_dollars"]),
            "Estimated fees": format_money(best["estimated_fees_trade_dollars"]),
            "Win rate": format_pct(best["win_rate"]),
            "False stop": format_pct(best["false_stop_pct_of_stops"]),
            "Sample": int(best["sample"]),
        },
        {
            "View": "Selected strategy | all history unweighted",
            "Entry": format_cents(best["entry"]),
            "Stop": format_cents(best["stop"]),
            "Expected net P and L": format_money(best_all_history_row["expected_net_pnl_trade_dollars"]) if best_all_history_row is not None else "NA",
            "Estimated fees": format_money(best_all_history_row["estimated_fees_trade_dollars"]) if best_all_history_row is not None else "NA",
            "Win rate": format_pct(best_all_history_row["win_rate"]) if best_all_history_row is not None else "NA",
            "False stop": format_pct(best_all_history_row["false_stop_pct_of_stops"]) if best_all_history_row is not None else "NA",
            "Sample": int(best_all_history_row["sample"]) if best_all_history_row is not None else 0,
        },
        {
            "View": "Locked baseline | recent weighted",
            "Entry": format_cents(baseline_entry_cents),
            "Stop": format_cents(baseline_stop_cents),
            "Expected net P and L": format_money(baseline_row["expected_net_pnl_trade_dollars"]) if baseline_row is not None else "NA",
            "Estimated fees": format_money(baseline_row["estimated_fees_trade_dollars"]) if baseline_row is not None else "NA",
            "Win rate": format_pct(baseline_row["win_rate"]) if baseline_row is not None else "NA",
            "False stop": format_pct(baseline_row["false_stop_pct_of_stops"]) if baseline_row is not None else "NA",
            "Sample": int(baseline_row["sample"]) if baseline_row is not None else 0,
        },
        {
            "View": "Locked baseline | all history unweighted",
            "Entry": format_cents(baseline_entry_cents),
            "Stop": format_cents(baseline_stop_cents),
            "Expected net P and L": format_money(baseline_all_history_row["expected_net_pnl_trade_dollars"]) if baseline_all_history_row is not None else "NA",
            "Estimated fees": format_money(baseline_all_history_row["estimated_fees_trade_dollars"]) if baseline_all_history_row is not None else "NA",
            "Win rate": format_pct(baseline_all_history_row["win_rate"]) if baseline_all_history_row is not None else "NA",
            "False stop": format_pct(baseline_all_history_row["false_stop_pct_of_stops"]) if baseline_all_history_row is not None else "NA",
            "Sample": int(baseline_all_history_row["sample"]) if baseline_all_history_row is not None else 0,
        },
    ]
    st.markdown("### Profitability cross-check")
    st.caption("The optimizer recommendation uses recent recency-weighted data. This table cross-checks the same strategy on full-history unweighted data so you can see whether the edge survives a broader sample.")
    st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)

    if baseline_row is not None:
        st.markdown(
            f"Best current setting from your resolved BTC15M history is **{int(best['entry'])}c entry** and **{int(best['stop'])}c stop**. "
            f"Versus the current bot rule of **{baseline_entry_cents}c / {baseline_stop_cents}c**, that changes expected net P and L by "
            f"**{format_money(best['expected_net_pnl_trade_dollars'] - baseline_row['expected_net_pnl_trade_dollars'])}** per {baseline_position_size} share trade, "
            f"changes false stop rate by **{best['false_stop_pct_of_stops'] - baseline_row['false_stop_pct_of_stops']:+.1f}%**, "
            f"and changes average time-to-close at entry by **{best['avg_seconds_to_close_at_entry'] - baseline_row['avg_seconds_to_close_at_entry']:+.0f}s**."
        )
    else:
        st.markdown(
            f"Best current setting from your resolved BTC15M history is **{int(best['entry'])}c entry** and **{int(best['stop'])}c stop**. "
            f"This is based only on resolved historical markets, keeps the bot's real **{BOT_DELAY_SECONDS}s** stop delay in the simulation, "
            f"and ignores entries with less than **{min_entry_seconds_to_close}s** remaining to settlement."
        )

    viz_left, viz_right = st.columns([1.25, 0.75], gap="large")
    with viz_left:
        st.markdown("### Entry/stop landscape")
        top_grid = grid.head(24).copy()
        heat = go.Figure()
        heat.add_trace(
            go.Scatter(
                x=top_grid["entry"],
                y=top_grid["stop"],
                mode="markers+text",
                text=top_grid["expected_net_pnl_trade_dollars"].map(lambda v: f"{v:.02f}"),
                textposition="top center",
                marker=dict(
                    size=np.clip(top_grid["sample"].astype(float) * 2.5 + 8.0, 10.0, 28.0),
                    color=top_grid["score"],
                    colorscale=[
                        [0.0, "#ff5a5f"],
                        [0.5, "#f5c451"],
                        [1.0, "#00c46a"],
                    ],
                    showscale=True,
                    colorbar=dict(title="Score"),
                    line=dict(color="rgba(255,255,255,0.18)", width=1),
                ),
                customdata=np.stack(
                    [
                        top_grid["win_rate"].to_numpy(dtype=float),
                        top_grid["false_stop_pct_of_stops"].to_numpy(dtype=float),
                        top_grid["sample"].to_numpy(dtype=float),
                        top_grid["expected_net_pnl_trade_dollars"].to_numpy(dtype=float),
                        top_grid["avg_seconds_to_close_at_entry"].fillna(np.nan).to_numpy(dtype=float),
                    ],
                    axis=1,
                ),
                hovertemplate=(
                    "Entry %{x}c<br>"
                    "Stop %{y}c<br>"
                    "Expected net P and L $%{customdata[3]:.4f}<br>"
                    "Win rate %{customdata[0]:.2f}%<br>"
                    "False stop %{customdata[1]:.2f}%<br>"
                    "Sample %{customdata[2]:.0f}<br>"
                    "Avg seconds to close %{customdata[4]:.0f}s<extra></extra>"
                ),
                showlegend=False,
            )
        )
        heat.add_vline(x=baseline_entry_cents, line_width=1, line_dash="dash", line_color="rgba(255,255,255,0.20)")
        heat.add_hline(y=baseline_stop_cents, line_width=1, line_dash="dash", line_color="rgba(255,255,255,0.20)")
        heat.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="entry threshold (c)",
            yaxis_title="stop threshold (c)",
        )
        heat.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        heat.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        st.plotly_chart(heat, width="stretch")

    with viz_right:
        st.markdown("### Best configurations")
        table = grid.head(12).copy()
        table["Entry"] = table["entry"].apply(format_cents)
        table["Stop"] = table["stop"].apply(format_cents)
        table["Expected net P and L"] = table["expected_net_pnl_trade_dollars"].apply(format_money)
        table["Estimated fees"] = table["estimated_fees_trade_dollars"].apply(format_money)
        table["Win rate"] = table["win_rate"].apply(format_pct)
        table["Stop hit rate"] = table["stop_hit_rate"].apply(format_pct)
        table["False stop"] = table["false_stop_pct_of_stops"].apply(format_pct)
        table["Modeled stop fill"] = table["expected_stop_fill"].apply(lambda v: describe_stop_fill(v)[0])
        table["Avg secs to close"] = table["avg_seconds_to_close_at_entry"].map(lambda v: "NA" if pd.isna(v) else f"{float(v):,.0f}s")
        table["Confidence"] = table["confidence"].astype(str).str.title()
        st.dataframe(
            table[["Entry", "Stop", "Expected net P and L", "Estimated fees", "Win rate", "Stop hit rate", "False stop", "Avg secs to close", "Modeled stop fill", "sample", "Confidence"]],
            use_container_width=True,
            hide_index=True,
        )

        if baseline_row is not None:
            st.markdown(f"### Locked bot baseline ({humanize_strategy_tag(active_dataset_tag)})")
            baseline_view = pd.DataFrame(
                [
                    {
                        "Entry": format_cents(baseline_row["entry"]),
                        "Stop": format_cents(baseline_row["stop"]),
                        "Expected net P and L": format_money(baseline_row["expected_net_pnl_trade_dollars"]),
                        "Estimated fees": format_money(baseline_row["estimated_fees_trade_dollars"]),
                        "Win rate": format_pct(baseline_row["win_rate"]),
                        "Stop hit rate": format_pct(baseline_row["stop_hit_rate"]),
                        "False stop": format_pct(baseline_row["false_stop_pct_of_stops"]),
                        "Avg secs to close": "NA" if pd.isna(baseline_row["avg_seconds_to_close_at_entry"]) else f"{float(baseline_row['avg_seconds_to_close_at_entry']):,.0f}s",
                        "Modeled stop fill": describe_stop_fill(baseline_row["expected_stop_fill"])[0],
                        "Sample": int(baseline_row["sample"]),
                    }
                ]
            )
            st.dataframe(baseline_view, use_container_width=True, hide_index=True)

    st.markdown("### BTC low-range gate study")
    st.caption("This tests the rule: if BTC has not moved far enough away from the market-start price, block early entries and only allow them once the contract is late enough. The study is filtered to the current active strategy profile when matching trades are available.")
    gate_features, gate_note = build_trade_btc_range_features(optimizer_trades, market_results_df)
    if gate_features.empty:
        st.info(gate_note or "No BTC range gate data is available yet.")
    else:
        gate_controls = st.columns(4)
        gate_range = gate_controls[0].slider(
            "Range threshold in USD",
            min_value=10,
            max_value=200,
            value=50,
            step=5,
            help="Uses max BTC excursion away from the market-start price before entry.",
        )
        gate_seconds = gate_controls[1].slider(
            "Late-entry unlock seconds",
            min_value=30,
            max_value=300,
            value=120,
            step=15,
            help="If BTC range is below the threshold, only allow entries this close to settlement or later.",
        )
        side_filter = gate_controls[2].selectbox("Side filter", ["Both", "YES only", "NO only"], index=0)
        gate_focus = gate_controls[3].radio("Gate ranking", ["Total P and L", "Win rate", "Stop-out reduction"], horizontal=False)

        gate_eval = gate_features.copy()
        if side_filter == "YES only":
            gate_eval = gate_eval[gate_eval["side"] == "yes"].copy()
        elif side_filter == "NO only":
            gate_eval = gate_eval[gate_eval["side"] == "no"].copy()

        if gate_eval.empty:
            st.info("No trades matched the selected side filter.")
        else:
            current_gate = summarize_btc_range_gate(gate_eval, gate_range, gate_seconds)
            gate_rows = []
            for range_threshold in [25, 50, 75, 100, 125]:
                for seconds_threshold in [30, 60, 90, 120, 150]:
                    gate_rows.append(summarize_btc_range_gate(gate_eval, range_threshold, seconds_threshold))
            gate_grid = pd.DataFrame([row for row in gate_rows if row])
            if not gate_grid.empty:
                if gate_focus == "Win rate":
                    gate_grid = gate_grid.sort_values(["win_rate_delta", "total_pnl_delta", "blocked_pct"], ascending=[False, False, True])
                elif gate_focus == "Stop-out reduction":
                    gate_grid = gate_grid.sort_values(["stop_out_delta", "total_pnl_delta", "blocked_pct"], ascending=[True, False, True])
                else:
                    gate_grid = gate_grid.sort_values(["total_pnl_delta", "win_rate_delta", "blocked_pct"], ascending=[False, False, True])

            gate_top = gate_grid.head(10).copy() if not gate_grid.empty else pd.DataFrame()
            gate_summary_cols = st.columns(4)
            gate_summary_cols[0].metric("Requested gate", f"<{gate_range} USD until <= {gate_seconds}s")
            gate_summary_cols[1].metric("Trades blocked", f"{int(current_gate.get('blocked_count', 0))}", delta=format_pct(current_gate.get("blocked_pct")))
            gate_summary_cols[2].metric("Win rate impact", format_pct(current_gate.get("kept_win_rate")), delta=f"{current_gate.get('win_rate_delta', float('nan')):+.1f}% vs baseline" if pd.notna(current_gate.get("win_rate_delta")) else "NA")
            gate_summary_cols[3].metric("P and L impact", format_money(current_gate.get("kept_total_pnl")), delta=f"{current_gate.get('total_pnl_delta', float('nan')):+.2f} vs baseline" if pd.notna(current_gate.get("total_pnl_delta")) else "NA")

            compare_gate_rows = [
                {
                    "View": "Baseline actual trades",
                    "Trades": int(current_gate.get("baseline_trade_count", 0)),
                    "Win rate": format_pct(current_gate.get("baseline_win_rate")),
                    "Stop-out rate": format_pct(current_gate.get("baseline_stop_out_rate")),
                    "Total P and L": format_money(current_gate.get("baseline_total_pnl")),
                    "Avg P and L": format_money(current_gate.get("baseline_avg_pnl")),
                },
                {
                    "View": f"Gate applied | <{gate_range} USD and >{gate_seconds}s blocked",
                    "Trades": int(current_gate.get("kept_trade_count", 0)),
                    "Win rate": format_pct(current_gate.get("kept_win_rate")),
                    "Stop-out rate": format_pct(current_gate.get("kept_stop_out_rate")),
                    "Total P and L": format_money(current_gate.get("kept_total_pnl")),
                    "Avg P and L": format_money(current_gate.get("kept_avg_pnl")),
                },
                {
                    "View": "Trades filtered out by gate",
                    "Trades": int(current_gate.get("blocked_count", 0)),
                    "Win rate": format_pct(current_gate.get("blocked_win_rate")),
                    "Stop-out rate": format_pct(current_gate.get("blocked_stop_out_rate")),
                    "Total P and L": format_money(current_gate.get("blocked_total_pnl")),
                    "Avg P and L": "NA",
                },
            ]
            st.dataframe(pd.DataFrame(compare_gate_rows), use_container_width=True, hide_index=True)
            if gate_note:
                st.caption(gate_note)

            if not gate_top.empty:
                gate_top["Rule"] = gate_top.apply(lambda row: f"<{int(row['range_threshold'])} USD until <= {int(row['seconds_threshold'])}s", axis=1)
                gate_top["Blocked"] = gate_top["blocked_pct"].map(format_pct)
                gate_top["Win rate delta"] = gate_top["win_rate_delta"].map(lambda v: "NA" if pd.isna(v) else f"{float(v):+.1f}%")
                gate_top["Stop-out delta"] = gate_top["stop_out_delta"].map(lambda v: "NA" if pd.isna(v) else f"{float(v):+.1f}%")
                gate_top["Total P and L delta"] = gate_top["total_pnl_delta"].map(format_money)
                gate_top["Kept P and L"] = gate_top["kept_total_pnl"].map(format_money)
                gate_top["Kept win rate"] = gate_top["kept_win_rate"].map(format_pct)
                gate_top["Kept stop-out rate"] = gate_top["kept_stop_out_rate"].map(format_pct)
                st.markdown("#### Best BTC range gates from your actual trades")
                st.dataframe(
                    gate_top[["Rule", "blocked_count", "Blocked", "kept_trade_count", "Kept P and L", "Total P and L delta", "Kept win rate", "Win rate delta", "Kept stop-out rate", "Stop-out delta"]],
                    use_container_width=True,
                    hide_index=True,
                )


def parse_ts(ts: str) -> datetime | None:
    try:
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None



def maybe_num(v: str) -> int | None:
    return None if v == "None" else int(v)



def ensure_ma_datetime(value: Any) -> datetime | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            return None
        dt = value.to_pydatetime()
    elif isinstance(value, datetime):
        dt = value
    else:
        dt = parse_ts(str(value))
        if dt is None:
            try:
                ts = pd.to_datetime(value, errors="coerce")
                if pd.isna(ts):
                    return None
                dt = ts.to_pydatetime()
            except Exception:
                return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=MA_TZ)
    return dt.astimezone(MA_TZ)



def to_ma_series(values: Any) -> pd.Series:
    ts = pd.to_datetime(values, errors="coerce")
    try:
        tz = ts.dt.tz
    except Exception:
        return ts
    if tz is None:
        return ts.dt.tz_localize(MA_TZ, ambiguous="NaT", nonexistent="shift_forward")
    return ts.dt.tz_convert(MA_TZ)


def format_ma_time(value: Any) -> str:
    dt = ensure_ma_datetime(value)
    if not dt:
        return "NA"
    return dt.strftime("%Y-%m-%d %I:%M:%S %p ET")


def display_text(value: Any, fallback: str = "NA") -> str:
    if value is None:
        return fallback
    try:
        if pd.isna(value):
            return fallback
    except Exception:
        pass
    value_str = str(value).strip()
    return value_str if value_str else fallback


def format_cents(value: Any) -> str:
    if value is None:
        return "NA"
    try:
        if pd.isna(value):
            return "NA"
    except Exception:
        pass
    try:
        num = float(value)
    except Exception:
        return "NA"
    if abs(num - round(num)) < 1e-9:
        return f"{int(round(num))}c"
    return f"{num:,.2f}c"


def describe_stop_fill(value: Any) -> tuple[str, str]:
    try:
        if value is None or pd.isna(value):
            return "No stop hits", "This configuration never hit the stop in the modeled sample."
    except Exception:
        return "NA", "Stop-fill estimate unavailable."
    return format_cents(value), "Estimated from logged bids after the stop trigger."


def format_money(v: float | int | None) -> str:
    if v is None:
        return "NA"
    try:
        if pd.isna(v):
            return "NA"
    except Exception:
        pass
    return f"${float(v):,.2f}"


def format_pct(v: float | int | None) -> str:
    if v is None:
        return "NA"
    try:
        if pd.isna(v):
            return "NA"
    except Exception:
        pass
    return f"{float(v):,.2f}%"


def render_truffle_shadow_panel(log_dir: str) -> None:
    shadow_df = load_truffle_shadow_summary(log_dir)
    lease_df = load_truffle_lease_summary(log_dir)
    if shadow_df.empty and lease_df.empty:
        return

    st.markdown("### Truffle market supervisor")
    st.caption("Live Truffle shadow calls and lease/block decisions read directly from the active log directory.")

    if not shadow_df.empty:
        outcome_series = shadow_df["outcome_type"] if "outcome_type" in shadow_df.columns else pd.Series("", index=shadow_df.index)
        decision_series = shadow_df["model_decision"] if "model_decision" in shadow_df.columns else pd.Series("", index=shadow_df.index)
        resolved = shadow_df[outcome_series.fillna("").astype(str) != ""].copy()
        decisions = shadow_df[decision_series.fillna("").astype(str) != ""].copy()
    else:
        resolved = pd.DataFrame()
        decisions = pd.DataFrame()
    valid_series = decisions.get("valid", pd.Series(dtype=object)).dropna() if not decisions.empty else pd.Series(dtype=object)
    valid_rate = (float(valid_series.astype(bool).mean()) * 100.0) if not valid_series.empty else None
    avg_response = float(pd.to_numeric(decisions.get("prompt_response_seconds"), errors="coerce").dropna().mean()) if not decisions.empty and "prompt_response_seconds" in decisions.columns else np.nan
    pnl_total = float(pd.to_numeric(resolved.get("pnl_dollars"), errors="coerce").fillna(0.0).sum()) if not resolved.empty and "pnl_dollars" in resolved.columns else 0.0

    metric_cols = st.columns(5)
    metric_cols[0].metric("Shadow markets", f"{len(shadow_df):,}", delta=f"{len(resolved):,} resolved")
    metric_cols[1].metric("Responses", f"{len(decisions):,}", delta=format_pct(valid_rate))
    metric_cols[2].metric("Avg response", f"{avg_response:.2f}s" if pd.notna(avg_response) else "NA", delta="prompt to response")
    metric_cols[3].metric("Outcome P and L", format_money(pnl_total), delta="shadow outcome log")
    metric_cols[4].metric("Lease events", f"{len(lease_df):,}", delta=f"{lease_df['market'].nunique():,} markets" if not lease_df.empty and "market" in lease_df.columns else "0 markets")

    if not shadow_df.empty:
        model_decision_series = shadow_df["model_decision"] if "model_decision" in shadow_df.columns else pd.Series("", index=shadow_df.index)
        decision_counts = (
            shadow_df.assign(model_decision=model_decision_series.fillna("").replace("", "NO_DECISION"))
            .groupby("model_decision", dropna=False)
            .size()
            .reset_index(name="markets")
            .sort_values("markets", ascending=False)
        )
        resolved_outcome_series = resolved["outcome_type"] if "outcome_type" in resolved.columns else pd.Series("", index=resolved.index)
        outcome_counts = (
            resolved.assign(outcome_type=resolved_outcome_series.fillna("").replace("", "unresolved"))
            .groupby("outcome_type", dropna=False)
            .agg(markets=("market", "count"), pnl_dollars=("pnl_dollars", "sum"))
            .reset_index()
            .sort_values("markets", ascending=False)
        ) if not resolved.empty else pd.DataFrame()

        left, right = st.columns(2)
        with left:
            st.markdown("#### Decision mix")
            st.dataframe(decision_counts, use_container_width=True, hide_index=True)
        with right:
            st.markdown("#### Outcome mix")
            if outcome_counts.empty:
                st.info("No Truffle outcome rows have landed yet.")
            else:
                outcome_view = outcome_counts.copy()
                outcome_view["pnl_dollars"] = outcome_view["pnl_dollars"].apply(format_money)
                st.dataframe(outcome_view, use_container_width=True, hide_index=True)

        recent_cols = [
            "market",
            "side",
            "decision_at",
            "model_decision",
            "confidence",
            "reason_code",
            "reversal_risk",
            "settlement_bias",
            "entry_fill_cents",
            "current_exit_bid_cents",
            "prompt_response_seconds",
            "outcome_type",
            "pnl_dollars",
            "truth_label",
            "delta_vs_actual_dollars",
        ]
        recent_cols = [col for col in recent_cols if col in shadow_df.columns]
        recent = shadow_df[recent_cols].head(120).copy()
        for col in ["decision_at"]:
            if col in recent.columns:
                recent[col] = pd.to_datetime(recent[col], utc=True, errors="coerce").dt.tz_convert(MA_TZ).dt.strftime("%Y-%m-%d %I:%M:%S %p")
        for col in ["pnl_dollars", "delta_vs_actual_dollars"]:
            if col in recent.columns:
                recent[col] = recent[col].apply(format_money)
        for col in ["entry_fill_cents", "current_exit_bid_cents"]:
            if col in recent.columns:
                recent[col] = recent[col].apply(format_cents)
        if "prompt_response_seconds" in recent.columns:
            recent["prompt_response_seconds"] = pd.to_numeric(recent["prompt_response_seconds"], errors="coerce").map(lambda v: "NA" if pd.isna(v) else f"{float(v):.2f}s")
        st.markdown("#### Recent Truffle markets")
        st.dataframe(recent, use_container_width=True, hide_index=True)

    if not lease_df.empty:
        lease_view_cols = ["ts", "market", "event_type", "lease_decision", "mode", "rationale_code", "side", "trigger_price_cents", "summary_reason"]
        lease_view_cols = [col for col in lease_view_cols if col in lease_df.columns]
        lease_view = lease_df[lease_view_cols].head(80).copy()
        if "ts" in lease_view.columns:
            lease_view["ts"] = pd.to_datetime(lease_view["ts"], utc=True, errors="coerce").dt.tz_convert(MA_TZ).dt.strftime("%Y-%m-%d %I:%M:%S %p")
        if "trigger_price_cents" in lease_view.columns:
            lease_view["trigger_price_cents"] = lease_view["trigger_price_cents"].apply(format_cents)
        st.markdown("#### Recent Truffle lease events")
        st.dataframe(lease_view, use_container_width=True, hide_index=True)


def estimate_kalshi_fee_dollars(price_cents: Any, contracts: Any) -> float:
    try:
        price = float(price_cents)
        qty = int(round(float(contracts)))
    except Exception:
        return 0.0
    if qty <= 0 or price <= 0 or price >= 100:
        return 0.0
    probability = price / 100.0
    raw_fee_dollars = KALSHI_TAKER_FEE_RATE * qty * probability * (1.0 - probability)
    return float(np.ceil(raw_fee_dollars * 100.0) / 100.0)


def outcome_badge(outcome: str) -> str:
    outcome = (outcome or "open").lower()
    cls = "badge-neutral"
    if outcome == "win":
        cls = "badge-green"
    elif outcome == "loss":
        cls = "badge-red"
    elif outcome == "void":
        cls = "badge-yellow"
    return f'<span class="badge {cls}">{html.escape(outcome.replace("_", " "))}</span>'



def pnl_class(v: float | int | None) -> str:
    if v is None or pd.isna(v):
        return "neutral"
    return "positive" if v > 0 else "negative" if v < 0 else "neutral"



def normalize_trades(df: pd.DataFrame, dataset_tag: str | None = None) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    out = df.copy()
    use_actuals = dataset_uses_actuals(str(dataset_tag or ""))
    for col in [
        "qty",
        "gross_pnl_dollars",
        "net_pnl_dollars",
        "gross_pnl_percent",
        "net_pnl_percent",
        "total_fees_dollars",
        "entry_fill_cents_assumed",
        "exit_fill_cents_assumed",
        "entry_notional_dollars",
    ]:
        if col not in out.columns:
            out[col] = pd.NA
        out[col] = pd.to_numeric(out[col], errors="coerce")

    if "entry_fill_cents_used" not in out.columns:
        out["entry_fill_cents_used"] = out.get("entry_fill_cents_actual")
        out["entry_fill_cents_used"] = pd.to_numeric(out["entry_fill_cents_used"], errors="coerce").fillna(pd.to_numeric(out.get("entry_fill_cents_assumed"), errors="coerce"))
    if "exit_fill_cents_used" not in out.columns:
        out["exit_fill_cents_used"] = out.get("exit_fill_cents_actual")
        out["exit_fill_cents_used"] = pd.to_numeric(out["exit_fill_cents_used"], errors="coerce").fillna(pd.to_numeric(out.get("exit_fill_cents_assumed"), errors="coerce"))

    def bucket(row: pd.Series) -> str:
        pnl = row.get("gross_pnl_dollars")
        raw = str(row.get("outcome", "open") or "open").lower()
        if pd.notna(pnl):
            if pnl > 0:
                return "win"
            if pnl < 0:
                return "loss"
            if raw == "void":
                return "void"
            return "flat"
        if raw == "void":
            return "void"
        return raw

    out["display_outcome"] = out.apply(bucket, axis=1)
    qty = pd.to_numeric(out.get("qty"), errors="coerce")
    valid_qty = qty.where(qty > 0)
    display_qty = valid_qty.fillna(DISPLAY_POSITION_SIZE) if use_actuals else pd.Series(DISPLAY_POSITION_SIZE, index=out.index, dtype=float)
    scale_factor = 1.0 if use_actuals else (DISPLAY_POSITION_SIZE / valid_qty)
    out["display_qty"] = display_qty
    out["scaled_gross_pnl_dollars"] = pd.to_numeric(out["gross_pnl_dollars"], errors="coerce") * scale_factor
    out["scaled_entry_notional_dollars"] = pd.to_numeric(out["entry_fill_cents_used"], errors="coerce") * display_qty / 100.0
    out["estimated_entry_fee_dollars"] = [
        estimate_kalshi_fee_dollars(entry_price, trade_qty)
        for entry_price, trade_qty in zip(pd.to_numeric(out["entry_fill_cents_used"], errors="coerce"), display_qty)
    ]
    out["estimated_exit_fee_dollars"] = [
        estimate_kalshi_fee_dollars(exit_price, trade_qty) if pd.notna(exit_price) else 0.0
        for exit_price, trade_qty in zip(pd.to_numeric(out["exit_fill_cents_used"], errors="coerce"), display_qty)
    ]
    out["estimated_total_fees_dollars"] = (
        pd.to_numeric(out["estimated_entry_fee_dollars"], errors="coerce").fillna(0.0)
        + pd.to_numeric(out["estimated_exit_fee_dollars"], errors="coerce").fillna(0.0)
    )
    out["scaled_net_pnl_dollars"] = pd.to_numeric(out["scaled_gross_pnl_dollars"], errors="coerce") - out["estimated_total_fees_dollars"]
    if use_actuals:
        actual_fees = pd.to_numeric(out.get("total_fees_dollars"), errors="coerce").fillna(out["estimated_total_fees_dollars"])
        actual_net = pd.to_numeric(out.get("net_pnl_dollars"), errors="coerce").fillna(pd.to_numeric(out["gross_pnl_dollars"], errors="coerce").fillna(0.0) - actual_fees)
        out["actual_entry_fee_dollars"] = out["estimated_entry_fee_dollars"]
        out["actual_exit_fee_dollars"] = out["estimated_exit_fee_dollars"]
        out["actual_total_fees_dollars"] = actual_fees
        out["actual_gross_pnl_dollars"] = pd.to_numeric(out["gross_pnl_dollars"], errors="coerce")
        out["actual_entry_notional_dollars"] = pd.to_numeric(out.get("entry_notional_dollars"), errors="coerce").fillna(out["scaled_entry_notional_dollars"])
        out["actual_net_pnl_dollars"] = actual_net
    else:
        out["estimated_entry_fee_dollars"] = out["estimated_entry_fee_dollars"]
        out["estimated_exit_fee_dollars"] = out["estimated_exit_fee_dollars"]
    scaled_basis = pd.to_numeric(out["scaled_entry_notional_dollars"], errors="coerce")
    out["scaled_net_pnl_percent"] = np.where(
        scaled_basis > 0,
        (pd.to_numeric(out["scaled_net_pnl_dollars"], errors="coerce") / scaled_basis) * 100.0,
        np.nan,
    )
    if use_actuals:
        out["actual_net_pnl_percent"] = pd.to_numeric(out.get("net_pnl_percent"), errors="coerce").fillna(out["scaled_net_pnl_percent"])
    out["ma_time"] = [
        format_ma_time(row.get("exit_ts") if pd.notna(row.get("exit_ts")) and str(row.get("exit_ts")) != "" else row.get("entry_ts"))
        for _, row in out.iterrows()
    ]
    return out



def enrich_trades_with_market_results(trades_df: pd.DataFrame, market_results_df: pd.DataFrame) -> pd.DataFrame:
    if trades_df.empty:
        return trades_df.copy()
    out = trades_df.copy()
    for col in ["market_result", "result"]:
        if col not in out.columns:
            out[col] = ""
        out[col] = out[col].fillna("").astype(str).str.lower()

    out["resolved_market_result"] = out["market_result"]
    out.loc[out["resolved_market_result"].eq(""), "resolved_market_result"] = out.loc[out["resolved_market_result"].eq(""), "result"]

    if market_results_df is not None and not market_results_df.empty and "market" in market_results_df.columns:
        lookup = market_results_df[["market", "result"]].copy()
        lookup["market"] = lookup["market"].fillna("").astype(str)
        lookup["result"] = lookup["result"].fillna("").astype(str).str.lower()
        lookup = lookup.drop_duplicates(subset=["market"], keep="last")
        out = out.merge(lookup.rename(columns={"result": "market_result_lookup"}), on="market", how="left")
        out["market_result_lookup"] = out["market_result_lookup"].fillna("").astype(str).str.lower()
        mask = out["resolved_market_result"].eq("")
        out.loc[mask, "resolved_market_result"] = out.loc[mask, "market_result_lookup"]
        out = out.drop(columns=["market_result_lookup"], errors="ignore")

    out["resolved_market_result_label"] = out["resolved_market_result"].replace({"yes": "YES", "no": "NO", "void": "VOID", "": "NA"})
    return out



def parse_log_state(lines: list[str]) -> dict[str, Any]:
    latest_heartbeat = None
    latest_watch = None
    latest_entry = None
    latest_exit = None
    latency_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        m = HEARTBEAT_RE.match(line)
        if m:
            latest_heartbeat = {
                "ts": m.group("ts"),
                "watch": m.group("watch"),
                "yes_bid": maybe_num(m.group("yes_bid")),
                "yes_ask": maybe_num(m.group("yes_ask")),
                "no_bid": maybe_num(m.group("no_bid")),
                "no_ask": maybe_num(m.group("no_ask")),
                "book_ready": m.group("book_ready") == "True",
                "position": m.group("position") == "True",
                "pending": m.group("pending") == "True",
                "dry_run": m.group("dry_run") == "True",
                "trust": m.group("trust") or "",
                "run_id": m.group("run_id") or "",
            }
            continue
        m = WATCH_RE.match(line)
        if m:
            latest_watch = m.groupdict()
            event_rows.append({"ts": m.group("ts"), "kind": "watch", "msg": f"Watching {m.group('market')}"})
            continue
        m = ENTRY_RE.match(line)
        if m:
            latest_entry = {
                "ts": m.group("ts"),
                "market": m.group("market"),
                "side": m.group("side"),
                "trigger": int(m.group("trigger")),
                "limit": int(m.group("limit")),
                "qty": int(m.group("qty")),
            }
            event_rows.append({"ts": m.group("ts"), "kind": "entry", "msg": f"BUY {m.group('side').upper()} {m.group('qty')} @ {m.group('limit')}c"})
            continue
        m = EXIT_RE.match(line)
        if m:
            latest_exit = {
                "ts": m.group("ts"),
                "market": m.group("market"),
                "side": m.group("side"),
                "trigger": int(m.group("trigger")),
                "limit": int(m.group("limit")),
                "qty": int(m.group("qty")),
            }
            event_rows.append({"ts": m.group("ts"), "kind": "exit", "msg": f"SELL {m.group('side').upper()} {m.group('qty')} @ {m.group('limit')}c"})
            continue
        m = LATENCY_RE.match(line)
        if m:
            latency_rows.append({
                "ts": m.group("ts"),
                "purpose": m.group("purpose"),
                "feed_age_ms": float(m.group("feed_age_ms")),
                "local_reaction_ms": float(m.group("local_reaction_ms")),
            })
            continue
        m = LEVEL_RE.match(line)
        if m and m.group("level") in {"WARNING", "ERROR"}:
            warnings.append({"ts": m.group("ts"), "level": m.group("level"), "msg": m.group("msg")})
            event_rows.append({"ts": m.group("ts"), "kind": m.group("level").lower(), "msg": m.group("msg")})

    status = "No feed"
    status_class = "pill-gray"
    if latest_heartbeat:
        hb_time = parse_ts(latest_heartbeat["ts"])
        if hb_time:
            age = (datetime.now() - hb_time).total_seconds()
            if age <= 15:
                status = "Live"
                status_class = "pill-green"
            elif age <= 60:
                status = "Stale"
                status_class = "pill-yellow"
            else:
                status = "Disconnected"
                status_class = "pill-red"

    return {
        "latest_heartbeat": latest_heartbeat,
        "latest_watch": latest_watch,
        "latest_entry": latest_entry,
        "latest_exit": latest_exit,
        "latency_rows": latency_rows,
        "warnings": warnings[-20:],
        "events": event_rows[-120:],
        "status": status,
        "status_class": status_class,
        "log_tail": lines[-200:],
    }



def trade_cards(df: pd.DataFrame, market_results_df: pd.DataFrame | None = None, max_cards: int = 8):
    if df.empty:
        st.info("No scored trades yet. Run the scorer from the sidebar after the bot has generated entries.")
        return

    enriched = enrich_trades_with_market_results(
        df,
        market_results_df if market_results_df is not None else pd.DataFrame(),
    )

    sort_cols = [c for c in ["entry_ts", "exit_ts"] if c in enriched.columns]
    recent = enriched.sort_values(by=sort_cols, ascending=False).head(max_cards) if sort_cols else enriched.head(max_cards)

    cols = st.columns(2)
    for idx, (_, row) in enumerate(recent.iterrows()):
        with cols[idx % 2]:
            pnl = row.get("gross_pnl_dollars")
            pnl_pct = row.get("gross_pnl_percent")
            side = str(row.get("side", "")).upper()

            loss_resolution_html = ""
            if str(row.get("display_outcome", "")).lower() == "loss":
                resolved = str(row.get("resolved_market_result_label", "NA"))
                if resolved and resolved != "NA":
                    loss_resolution_html = (
                        '<div class="trade-resolution">Ultimately resolved: '
                        f'<strong>{html.escape(resolved)}</strong></div>'
                    )

            html_block = (
                f'<div class="trade-card {pnl_class(pnl)}">'
                '<div class="trade-head">'
                '<div>'
                f'<div class="trade-market">{html.escape(str(row.get("market", "")))}</div>'
                f'<div class="trade-sub">{html.escape(side)} | qty {int(row.get("qty", 0) or 0)}</div>'
                '</div>'
                f'<div>{outcome_badge(str(row.get("display_outcome", "open")))}</div>'
                '</div>'
                '<div class="trade-metrics">'
                f'<div><span>Entry</span><strong>{format_cents(row.get("entry_fill_cents_used"))}</strong></div>'
                f'<div><span>Exit</span><strong>{format_cents(row.get("exit_fill_cents_used"))}</strong></div>'
                f'<div><span>P and L</span><strong>{format_money(pnl)}</strong></div>'
                f'<div><span>Return</span><strong>{format_pct(pnl_pct)}</strong></div>'
                '</div>'
                f'{loss_resolution_html}'
                f'<div class="trade-foot">{html.escape(str(row.get("ma_time", "-")))}</div>'
                '</div>'
            )

            st.markdown(html_block, unsafe_allow_html=True)


def make_equity_curve(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or ("gross_pnl_dollars" not in df.columns and "scaled_net_pnl_dollars" not in df.columns and "actual_net_pnl_dollars" not in df.columns):
        return pd.DataFrame(columns=["ts", "equity"])
    curve = df.copy()
    if "exit_ts" not in curve.columns:
        curve["exit_ts"] = pd.NA
    if "settlement_ts" not in curve.columns:
        curve["settlement_ts"] = pd.NA
    if "entry_ts" not in curve.columns:
        curve["entry_ts"] = pd.NA
    def _to_naive_ts(values: Any) -> pd.Series:
        ts = pd.to_datetime(values, errors="coerce", utc=True)
        return ts.dt.tz_convert(MA_TZ).dt.tz_localize(None)

    curve["ts"] = _to_naive_ts(curve["exit_ts"])
    settlement_ts = _to_naive_ts(curve["settlement_ts"])
    entry_ts = _to_naive_ts(curve["entry_ts"])
    curve["ts"] = curve["ts"].fillna(settlement_ts).fillna(entry_ts)
    curve = curve.dropna(subset=["ts"]).sort_values("ts")
    if "actual_net_pnl_dollars" in curve.columns:
        equity_source = "actual_net_pnl_dollars"
    elif "net_pnl_dollars" in curve.columns:
        equity_source = "net_pnl_dollars"
    elif "scaled_net_pnl_dollars" in curve.columns:
        equity_source = "scaled_net_pnl_dollars"
    else:
        equity_source = "gross_pnl_dollars"
    curve[equity_source] = pd.to_numeric(curve[equity_source], errors="coerce").fillna(0.0)
    curve["trade_pnl"] = curve[equity_source]
    curve["equity"] = curve[equity_source].cumsum()
    curve["equity_source"] = equity_source
    keep_cols = [
        "ts",
        "equity",
        "drawdown",
        "trade_pnl",
        "equity_source",
        "market",
        "side",
        "qty",
        "entry_fill_cents_used",
        "exit_fill_cents_used",
        "display_outcome",
        "entry_ts",
        "exit_ts",
        "settlement_ts",
    ]
    return curve[[c for c in keep_cols if c in curve.columns]]



def filter_equity_curve(curve: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    if curve.empty:
        return curve.copy()
    normalized = str(timeframe or "ALL").upper()
    if normalized == "ALL":
        return curve.copy()
    end_ts = curve["ts"].max()
    lookback_map = {
        "1D": pd.Timedelta(days=1),
        "1W": pd.Timedelta(days=7),
        "1M": pd.Timedelta(days=30),
        "3M": pd.Timedelta(days=90),
        "YTD": "YTD",
    }
    lookback = lookback_map.get(normalized)
    if lookback is None:
        return curve.copy()
    if lookback == "YTD":
        start_ts = pd.Timestamp(year=end_ts.year, month=1, day=1, tz=end_ts.tz) if getattr(end_ts, "tz", None) else pd.Timestamp(year=end_ts.year, month=1, day=1)
    else:
        start_ts = end_ts - lookback
    filtered = curve[curve["ts"] >= start_ts].copy()
    if filtered.empty:
        filtered = curve.tail(1).copy()
    baseline_rows = curve[curve["ts"] < filtered["ts"].iloc[0]]
    baseline = float(baseline_rows["equity"].iloc[-1]) if not baseline_rows.empty else 0.0
    filtered["equity"] = filtered["equity"] - baseline
    return filtered


def add_drawdown_to_equity_curve(curve: pd.DataFrame) -> pd.DataFrame:
    if curve.empty or "equity" not in curve.columns:
        return pd.DataFrame(columns=["ts", "equity", "drawdown"])
    out = curve.copy()
    equity = pd.to_numeric(out["equity"], errors="coerce").fillna(0.0).to_numpy(dtype=float)
    peaks = np.maximum.accumulate(np.concatenate([[0.0], equity]))[1:]
    out["drawdown"] = equity - peaks
    return out


def preferred_pnl_column(df: pd.DataFrame) -> str | None:
    if df is None or df.empty:
        return None
    for col in ["actual_net_pnl_dollars", "net_pnl_dollars", "scaled_net_pnl_dollars", "gross_pnl_dollars"]:
        if col in df.columns and pd.to_numeric(df[col], errors="coerce").notna().any():
            return col
    return None


def trade_pnl_series(df: pd.DataFrame) -> pd.Series:
    if df is None or df.empty:
        return pd.Series(dtype=float)
    pnl_col = preferred_pnl_column(df)
    if not pnl_col:
        return pd.Series(np.nan, index=df.index, dtype=float)
    return pd.to_numeric(df[pnl_col], errors="coerce")


def format_signed_money(value: float | int | None, always_sign: bool = False) -> str:
    if value is None:
        return "NA"
    try:
        if pd.isna(value):
            return "NA"
    except Exception:
        pass
    num = float(value)
    if abs(num) < 0.005:
        num = 0.0
    if num < 0:
        return f"-${abs(num):,.2f}"
    if always_sign and num > 0:
        return f"+${num:,.2f}"
    return f"${num:,.2f}"


def format_drawdown_money(value: float | int | None) -> str:
    if value is None:
        return "NA"
    try:
        if pd.isna(value):
            return "NA"
    except Exception:
        pass
    return f"-${abs(float(value)):,.2f}" if abs(float(value)) >= 0.005 else "$0.00"


def safe_float(value: Any, fallback: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return fallback
    except Exception:
        pass
    try:
        return float(value)
    except Exception:
        return fallback


def safe_int(value: Any, fallback: int = 0) -> int:
    try:
        if value is None or pd.isna(value):
            return fallback
    except Exception:
        pass
    try:
        return int(float(value))
    except Exception:
        return fallback


def format_age_seconds(seconds: float | int | None) -> str:
    if seconds is None:
        return "NA"
    try:
        if pd.isna(seconds):
            return "NA"
    except Exception:
        pass
    value = max(float(seconds), 0.0)
    if value < 60:
        return f"{value:.0f}s"
    if value < 3600:
        return f"{value / 60.0:.1f}m"
    if value < 86400:
        return f"{value / 3600.0:.1f}h"
    return f"{value / 86400.0:.1f}d"


def format_file_age(path: Path) -> str:
    try:
        if not path.exists():
            return "missing"
        return f"{format_age_seconds(time.time() - path.stat().st_mtime)} ago"
    except Exception:
        return "unknown"


def compact_market_label(value: Any) -> str:
    text = display_text(value)
    if text == "NA":
        return text
    match = MARKET_TICKER_RE.match(text)
    if not match:
        return text
    return f"{match.group('mon')} {match.group('day')} {match.group('hour')}:{match.group('minute')} {match.group('bucket')}"


def resolve_accounting_status(summary: dict[str, Any]) -> dict[str, Any]:
    accounting_raw = summary.get("accounting") if isinstance(summary.get("accounting"), dict) else {}
    api_fetch = accounting_raw.get("api_fetch") if isinstance(accounting_raw.get("api_fetch"), dict) else {}

    def accounting_int(name: str, fallback: Any = 0) -> int:
        return safe_int(summary.get(name, accounting_raw.get(name, fallback)), 0)

    enabled = bool(summary.get("kalshi_api_accounting_enabled", api_fetch.get("enabled", False)))
    authenticated = bool(summary.get("kalshi_api_accounting_authenticated", api_fetch.get("authenticated", False)))
    api_fill_count = accounting_int("kalshi_api_accounting_fill_count", api_fetch.get("normalized_api_fill_count", 0))
    entry_rows = accounting_int("rows_total", accounting_raw.get("rows_total", summary.get("entries_total", 0)))
    realized_exit_rows = accounting_int(
        "realized_exit_rows",
        accounting_raw.get("realized_exit_rows", summary.get("completed_round_trips", 0)),
    )
    entry_api = accounting_int("accounting_entry_rows_matched_api", accounting_raw.get("entry_rows_matched_api", 0))
    exit_api = accounting_int("accounting_exit_rows_matched_api", accounting_raw.get("exit_rows_matched_api", 0))
    unmatched_entries = accounting_int("accounting_unmatched_entries", accounting_raw.get("unmatched_entries", 0))
    unmatched_exits = accounting_int(
        "accounting_unmatched_realized_exits",
        accounting_raw.get("unmatched_realized_exits", 0),
    )
    unmatched_total = unmatched_entries + unmatched_exits
    matched_api_total = entry_api + exit_api
    needed_total = entry_rows + realized_exit_rows
    reconciliation_json = display_text(
        summary.get("accounting_reconciliation_json", accounting_raw.get("reconciliation_json", "")),
        "",
    )

    if enabled and authenticated and needed_total > 0 and entry_api >= entry_rows and exit_api >= realized_exit_rows and unmatched_total == 0:
        value = "Verified"
        note = f"{matched_api_total}/{needed_total} rows API matched"
        css_class = "verified"
    elif enabled and authenticated and (matched_api_total > 0 or api_fill_count > 0):
        value = "Partial"
        note = f"{matched_api_total}/{needed_total or 'NA'} API rows, {unmatched_total} unmatched"
        css_class = "partial"
    elif enabled:
        value = "Fallback"
        note = "API auth unavailable"
        css_class = "fallback"
    else:
        value = "Fallback"
        note = "API unavailable"
        css_class = "fallback"

    return {
        "label": "Kalshi API" if enabled else "Accounting",
        "value": value,
        "note": note,
        "class": css_class,
        "enabled": enabled,
        "authenticated": authenticated,
        "api_fill_count": api_fill_count,
        "matched_api_total": matched_api_total,
        "needed_total": needed_total,
        "unmatched_total": unmatched_total,
        "source": display_text(summary.get("accounting_source", accounting_raw.get("source_label", "")), "bot-log estimates"),
        "reconciliation_json": reconciliation_json,
    }


def resolve_live_lock_status(active_dataset: dict[str, Any]) -> dict[str, str]:
    payload = read_live_lock_payload()
    locked_tag = sanitize_strategy_tag(str(payload.get("strategy_tag") or "")) if payload else ""
    active_tag = sanitize_strategy_tag(str(active_dataset.get("tag") or ""))
    if locked_tag and locked_tag == active_tag:
        return {
            "label": "Live Lock",
            "value": "Synced",
            "note": f"Selected dataset follows {humanize_strategy_tag(locked_tag)}",
            "class": "verified",
        }
    if locked_tag:
        return {
            "label": "Manual Dataset",
            "value": "Unlocked View",
            "note": f"Lock points to {humanize_strategy_tag(locked_tag)}",
            "class": "partial",
        }
    return {
        "label": "Live Lock",
        "value": "No Lock",
        "note": "state/live_trading.lock missing or unusable",
        "class": "fallback",
    }


def sparkline_svg(values: Any, color: str = "#63f2b1", fill: str = "rgba(99,242,177,0.16)") -> str:
    try:
        series = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan).dropna()
    except Exception:
        series = pd.Series(dtype="float64")
    if series.empty:
        return ""
    series = series.tail(36)
    lo = float(series.min())
    hi = float(series.max())
    span = hi - lo if abs(hi - lo) > 1e-9 else 1.0
    denom = max(len(series) - 1, 1)
    points = []
    area_points = ["0,40"]
    for idx, value in enumerate(series):
        x = (idx / denom) * 110.0
        y = 35.0 - ((float(value) - lo) / span) * 30.0
        points.append(f"{x:.1f},{y:.1f}")
        area_points.append(f"{x:.1f},{y:.1f}")
    area_points.append("110,40")
    return (
        "<svg class='living-sparkline' viewBox='0 0 110 42' aria-hidden='true'>"
        f"<polygon points='{' '.join(area_points)}' fill='{html.escape(fill)}'></polygon>"
        f"<polyline points='{' '.join(points)}' fill='none' stroke='{html.escape(color)}' stroke-width='2.6' "
        "stroke-linecap='round' stroke-linejoin='round'></polyline>"
        "</svg>"
    )


def living_ring_svg(
    pct: float,
    *,
    color: str = "#9cff9f",
    track: str = "rgba(247,241,232,0.14)",
    label: str = "",
) -> str:
    try:
        pct_value = max(0.0, min(100.0, float(pct)))
    except Exception:
        pct_value = 0.0
    dash = pct_value * 1.76
    label_html = html.escape(label or f"{pct_value:.0f}%")
    return (
        "<svg class='living-sparkline' viewBox='0 0 120 44' aria-hidden='true'>"
        f"<circle cx='60' cy='22' r='17' fill='none' stroke='{html.escape(track)}' stroke-width='6'></circle>"
        f"<circle cx='60' cy='22' r='17' fill='none' stroke='{html.escape(color)}' stroke-width='6' "
        f"stroke-linecap='round' stroke-dasharray='{dash:.1f} 176' transform='rotate(-90 60 22)'></circle>"
        f"<text x='60' y='25' text-anchor='middle' fill='{html.escape(color)}' font-size='10' font-weight='800'>{label_html}</text>"
        "</svg>"
    )


def living_microbars_svg(values: Any, color: str = "#79e7ff", fill: str = "rgba(121,231,255,0.14)") -> str:
    series = pd.to_numeric(pd.Series(list(values) if not isinstance(values, pd.Series) else values), errors="coerce").dropna()
    if series.empty:
        return ""
    series = series.tail(18)
    max_abs = max(float(series.abs().max()), 1.0)
    bars = []
    step = 104.0 / max(len(series), 1)
    for idx, value in enumerate(series):
        height = 4.0 + (abs(float(value)) / max_abs) * 28.0
        x = 4.0 + idx * step
        y = 38.0 - height
        bar_color = color if float(value) >= 0 else "#ff5f73"
        bars.append(
            f"<rect x='{x:.1f}' y='{y:.1f}' width='{max(step - 1.4, 2.0):.1f}' height='{height:.1f}' "
            f"rx='1.8' fill='{html.escape(bar_color)}' opacity='0.82'></rect>"
        )
    return (
        "<svg class='living-sparkline' viewBox='0 0 112 42' aria-hidden='true'>"
        f"<rect x='1' y='3' width='110' height='36' rx='10' fill='{html.escape(fill)}'></rect>"
        + "".join(bars)
        + "</svg>"
    )


def build_orderbook_depth_svg(yes_bid: Any, yes_ask: Any, no_bid: Any, no_ask: Any, yes_spread: Any) -> str:
    prices = pd.to_numeric(pd.Series([yes_bid, yes_ask, no_bid, no_ask]), errors="coerce")
    yb, ya, nb, na = [None if pd.isna(v) else float(v) for v in prices]
    if yb is None and ya is None and nb is None and na is None:
        return "<div class='module-note'>No book snapshot</div>"
    bid_pressure = max(v for v in [yb, nb, 0.0] if v is not None)
    ask_pressure = max(100.0 - v for v in [ya, na, 100.0] if v is not None)
    scale = max(bid_pressure, ask_pressure, 1.0)
    spread_label = format_cents(yes_spread)
    pressure_total = max(bid_pressure + ask_pressure, 1.0)
    imbalance = ((bid_pressure - ask_pressure) / pressure_total) * 100.0
    bid_label = f"YES {format_cents(yb)} / NO {format_cents(nb)}"
    ask_label = f"YES {format_cents(ya)} / NO {format_cents(na)}"
    bid_bars = []
    ask_bars = []
    for idx in range(16):
        level = (idx + 1) / 16.0
        bid_h = 4.0 + (bid_pressure / scale) * (7.0 + level * 28.0)
        ask_h = 4.0 + (ask_pressure / scale) * (7.0 + level * 28.0)
        bid_bars.append(
            f"<rect x='{8 + idx * 4.8:.1f}' y='{58 - bid_h:.1f}' width='4.1' height='{bid_h:.1f}' "
            f"rx='1.2' fill='rgba(99,242,177,{0.34 + level * 0.42:.2f})'></rect>"
        )
        ask_bars.append(
            f"<rect x='{168 - idx * 4.8:.1f}' y='{58 - ask_h:.1f}' width='4.1' height='{ask_h:.1f}' "
            f"rx='1.2' fill='rgba(255,95,115,{0.34 + level * 0.42:.2f})'></rect>"
        )
    return (
        "<svg class='living-sparkline' viewBox='0 0 180 86' aria-hidden='true' style='height:86px;margin-top:0.24rem'>"
        "<defs><linearGradient id='depthGlow' x1='0' x2='1'><stop offset='0' stop-color='#63f2b1' stop-opacity='.32'/>"
        "<stop offset='.52' stop-color='#79e7ff' stop-opacity='.14'/><stop offset='1' stop-color='#ff5f73' stop-opacity='.32'/></linearGradient></defs>"
        "<rect x='2' y='5' width='176' height='60' rx='8' fill='url(#depthGlow)' opacity='.75'></rect>"
        "<line x1='8' y1='45' x2='172' y2='45' stroke='rgba(247,241,232,.13)' stroke-width='1'></line>"
        "<line x1='8' y1='30' x2='172' y2='30' stroke='rgba(247,241,232,.10)' stroke-width='1'></line>"
        + "".join(bid_bars)
        + "".join(ask_bars)
        + "<line x1='90' y1='12' x2='90' y2='62' stroke='rgba(247,241,232,0.28)' stroke-width='1'></line>"
        "<text x='14' y='16' fill='#63f2b1' font-size='8' font-weight='900'>BID</text>"
        "<text x='148' y='16' fill='#ff5f73' font-size='8' font-weight='900'>ASK</text>"
        f"<text x='90' y='29' text-anchor='middle' fill='#f7f1e8' font-size='10' font-weight='950'>{html.escape(spread_label)}</text>"
        "<text x='90' y='40' text-anchor='middle' fill='#a99bb9' font-size='7' font-weight='900'>YES SPREAD</text>"
        f"<text x='10' y='76' fill='#63f2b1' font-size='7' font-weight='850'>{html.escape(bid_label)}</text>"
        f"<text x='170' y='76' text-anchor='end' fill='#ff8a98' font-size='7' font-weight='850'>{html.escape(ask_label)}</text>"
        f"<text x='90' y='82' text-anchor='middle' fill='#d9cde7' font-size='7' font-weight='850'>IMB {imbalance:+.0f}%</text>"
        "</svg>"
    )


def outcome_spores_html(completed_pnl: pd.Series) -> str:
    pnl = pd.to_numeric(completed_pnl, errors="coerce").dropna()
    wins = int((pnl > 0).sum()) if not pnl.empty else 0
    losses = int((pnl < 0).sum()) if not pnl.empty else 0
    flats = int((pnl == 0).sum()) if not pnl.empty else 0
    total = max(wins + losses + flats, 1)
    clusters = [
        ("WIN", wins, "#9cff9f", 23, 48),
        ("LOSS", losses, "#ff5f73", 50, 48),
        ("FLAT", flats, "#d94cff", 77, 48),
    ]
    rings = []
    cores = []
    dots = []
    for cluster_idx, (_, count, color, cx, cy) in enumerate(clusters):
        intensity = min(max(int(count), 1), 120) / 120.0
        for radius in (34, 52, 70):
            rings.append(
                f"<span style='position:absolute;left:{cx:.1f}%;top:{cy:.1f}%;width:{radius}px;height:{radius}px;"
                f"border-radius:50%;border:1px solid {html.escape(color)};opacity:{0.10 + intensity * 0.22:.2f};"
                "transform:translate(-50%,-50%);'></span>"
            )
        cores.append(
            f"<span style='position:absolute;left:{cx:.1f}%;top:{cy:.1f}%;width:{8 + intensity * 9:.1f}px;height:{8 + intensity * 9:.1f}px;"
            f"border-radius:50%;background:{html.escape(color)};box-shadow:0 0 {12 + intensity * 22:.1f}px {html.escape(color)};"
            "transform:translate(-50%,-50%);opacity:.86'></span>"
        )
        visible = min(int(count), 54)
        for idx in range(visible):
            angle = idx * 2.399 + cluster_idx * 0.51
            radius = 5 + (idx % 11) * 2.35 + (idx // 11) * 1.8
            x = cx + np.cos(angle) * radius
            y = cy + np.sin(angle) * radius
            size = 2.2 + (idx % 4) * 0.38
            dots.append(
                f"<span style='position:absolute;left:{x:.1f}%;top:{y:.1f}%;width:{size:.1f}px;height:{size:.1f}px;"
                f"border-radius:50%;background:{html.escape(color)};box-shadow:0 0 8px {html.escape(color)};opacity:.82'></span>"
            )
    labels = []
    for label, count, color, cx, _ in clusters:
        pct = (count / total) * 100.0
        labels.append(
            f"<div style='text-align:center;min-width:54px'><div style='color:{html.escape(color)};font-size:.66rem;font-weight:900'>{html.escape(label)}</div>"
            f"<div style='color:#f7f1e8;font-size:1rem;font-weight:900'>{count}</div>"
            f"<div style='color:#a99bb9;font-size:.68rem;font-weight:800'>{pct:.1f}%</div></div>"
        )
    return (
        "<div style='position:relative;height:116px;margin-top:.42rem;border:1px solid rgba(121,231,255,.12);"
        "border-radius:8px;background:radial-gradient(circle at 23% 48%,rgba(99,242,177,.16),transparent 24%),"
        "radial-gradient(circle at 50% 48%,rgba(255,95,115,.14),transparent 24%),"
        "radial-gradient(circle at 77% 48%,rgba(217,76,255,.14),transparent 24%),rgba(7,6,12,.38);overflow:hidden'>"
        "<div style='position:absolute;left:8px;top:7px;color:#a99bb9;font-size:.58rem;font-weight:900;text-transform:uppercase'>"
        f"Total {wins + losses + flats}</div>"
        + "".join(rings)
        + "".join(cores)
        + "".join(dots)
        + "<div style='position:absolute;left:0;right:0;bottom:8px;display:flex;justify-content:space-around;gap:8px'>"
        + "".join(labels)
        + "</div></div>"
    )


def _series_to_svg_points(values: pd.Series, width: int, height: int, pad_x: int, pad_y: int, *, floor: float | None = None, ceiling: float | None = None) -> list[tuple[float, float]]:
    series = pd.to_numeric(values, errors="coerce").fillna(0.0)
    if series.empty:
        return []
    min_v = float(series.min()) if floor is None else min(float(series.min()), float(floor))
    max_v = float(series.max()) if ceiling is None else max(float(series.max()), float(ceiling))
    if abs(max_v - min_v) < 1e-9:
        min_v -= 1.0
        max_v += 1.0
    plot_w = max(width - pad_x * 2, 1)
    plot_h = max(height - pad_y * 2, 1)
    count = max(len(series) - 1, 1)
    points: list[tuple[float, float]] = []
    for idx, value in enumerate(series):
        x = pad_x + (idx / count) * plot_w
        y = pad_y + (1.0 - ((float(value) - min_v) / (max_v - min_v))) * plot_h
        points.append((x, y))
    return points


def _svg_path(points: list[tuple[float, float]]) -> str:
    if not points:
        return ""
    head, *tail = points
    chunks = [f"M {head[0]:.1f} {head[1]:.1f}"]
    chunks.extend(f"L {x:.1f} {y:.1f}" for x, y in tail)
    return " ".join(chunks)


def _reference_short_date(value: Any, fallback: str = "") -> str:
    dt = ensure_ma_datetime(value)
    if not dt:
        return fallback
    return f"{dt.strftime('%b').upper()} {dt.day}"


def _reference_short_clock(value: Any, fallback: str = "") -> str:
    dt = ensure_ma_datetime(value)
    if not dt:
        return fallback
    return dt.strftime("%H:%M")


def reference_equity_vine_svg(curve: pd.DataFrame) -> str:
    width = 780
    height = 392
    if curve.empty or "equity" not in curve.columns:
        return "<div class='ref-empty'>Waiting for scored equity</div>"
    work = curve.copy().tail(120).reset_index(drop=True)
    if "ts" not in work.columns:
        work["ts"] = pd.NA
    work["equity"] = pd.to_numeric(work["equity"], errors="coerce").fillna(0.0)
    work["drawdown"] = pd.to_numeric(work.get("drawdown", 0.0), errors="coerce").fillna(0.0)
    work["trade_pnl"] = pd.to_numeric(work.get("trade_pnl", 0.0), errors="coerce").fillna(0.0)
    floor = min(float(work["drawdown"].min()) * 1.18, float(work["equity"].min()) * 1.12, -0.05)
    ceiling = max(float(work["equity"].max()) * 1.16, 0.05)
    equity_points = _series_to_svg_points(work["equity"], width, height, 52, 36, floor=floor, ceiling=ceiling)
    draw_points = _series_to_svg_points(work["drawdown"], width, height, 52, 36, floor=floor, ceiling=ceiling)
    zero_y = _series_to_svg_points(pd.Series([0.0]), width, height, 52, 36, floor=floor, ceiling=ceiling)[0][1]
    equity_path = _svg_path(equity_points)
    draw_path = _svg_path(draw_points)
    area_path = ""
    if draw_points:
        area_path = f"M {draw_points[0][0]:.1f} {zero_y:.1f} " + " ".join(f"L {x:.1f} {y:.1f}" for x, y in draw_points) + f" L {draw_points[-1][0]:.1f} {zero_y:.1f} Z"
    envelope_path = ""
    if equity_points:
        top_edge = [(x, max(31.0, y - 24.0 - math.sin(idx * 0.58) * 4.0)) for idx, (x, y) in enumerate(equity_points)]
        bottom_edge = [(x, min(height - 43.0, y + 30.0 + math.cos(idx * 0.42) * 5.0)) for idx, (x, y) in enumerate(reversed(equity_points))]
        envelope_path = _svg_path(top_edge) + " " + " ".join(f"L {x:.1f} {y:.1f}" for x, y in bottom_edge) + " Z"
    contours = []
    for idx in range(9):
        y = 64 + idx * 31
        wobble = []
        for step in range(16):
            x = 52 + step * 45
            wobble.append((x, y + math.sin(step * 0.7 + idx * 0.55) * (8 + idx * 0.55)))
        contours.append(f"<path d='{_svg_path(wobble)}' class='ref-contour ref-contour-{idx % 3}'/>")
    mycelium_threads = []
    for idx in range(18):
        start_x = 40 + idx * 42
        start_y = 86 + math.sin(idx * 0.9) * 34
        mid_x = start_x + 42 + math.cos(idx * 0.7) * 18
        mid_y = start_y + 34 + math.sin(idx * 1.1) * 22
        end_x = min(width - 36, start_x + 96)
        end_y = 260 + math.cos(idx * 0.8) * 58
        color = "rgba(121,231,255,.16)" if idx % 3 == 0 else "rgba(156,255,159,.13)" if idx % 3 == 1 else "rgba(247,200,95,.12)"
        mycelium_threads.append(
            f"<path class='ref-mycelium' d='M {start_x:.1f} {start_y:.1f} C {mid_x:.1f} {mid_y:.1f}, "
            f"{end_x - 38:.1f} {end_y - 22:.1f}, {end_x:.1f} {end_y:.1f}' stroke='{color}'/>"
        )
    field_spores = []
    for idx in range(72):
        x = 48 + (idx * 67 % 690)
        y = 48 + ((idx * 41 + 17) % 284)
        size = 0.85 + (idx % 5) * 0.22
        color = "#63f2b1" if idx % 4 == 0 else "#f7c85f" if idx % 4 == 1 else "#79e7ff" if idx % 4 == 2 else "#d9cde7"
        field_spores.append(f"<circle class='ref-field-spore' cx='{x:.1f}' cy='{y:.1f}' r='{size:.2f}' fill='{color}'/>")
    roots = []
    loss_rows = work[work["trade_pnl"] < 0]
    if not loss_rows.empty and equity_points:
        for ordinal, (_, row) in enumerate(loss_rows.tail(32).iterrows()):
            idx = min(max(int(row.name) if isinstance(row.name, int) else ordinal, 0), len(equity_points) - 1)
            if idx >= len(equity_points):
                idx = ordinal % len(equity_points)
            x, y = equity_points[idx]
            root_len = 18 + min(abs(float(row.get("trade_pnl", 0.0))) * 42.0, 54.0)
            roots.append(
                f"<path class='ref-root' d='M {x:.1f} {y + 4:.1f} C {x - 8:.1f} {y + root_len * .45:.1f}, {x + 12:.1f} {y + root_len * .72:.1f}, {x + 2:.1f} {y + root_len:.1f}'/>"
            )
    branches = []
    gain_rows = work[work["trade_pnl"] > 0]
    if not gain_rows.empty and equity_points:
        for ordinal, (_, row) in enumerate(gain_rows.tail(24).iterrows()):
            idx = min(max(int(row.name) if isinstance(row.name, int) else ordinal, 0), len(equity_points) - 1)
            x, y = equity_points[idx]
            branch_len = 12 + min(abs(float(row.get("trade_pnl", 0.0))) * 20.0, 34.0)
            side = -1 if ordinal % 2 else 1
            branches.append(
                f"<path d='M {x:.1f} {y + 1:.1f} C {x + side * 10:.1f} {y - branch_len * .42:.1f}, "
                f"{x + side * 24:.1f} {y - branch_len * .56:.1f}, {x + side * 32:.1f} {y - branch_len:.1f}' "
                "fill='none' stroke='rgba(156,255,159,.26)' stroke-width='1.05'/>"
            )
    markers = []
    spore_dots = []
    marker_indices = np.linspace(0, max(len(equity_points) - 1, 0), min(13, len(equity_points)), dtype=int).tolist() if equity_points else []
    for idx in marker_indices:
        x, y = equity_points[idx]
        pnl = float(work["trade_pnl"].iloc[idx]) if idx < len(work) else 0.0
        cls = "gain" if pnl > 0 else "loss" if pnl < 0 else "flat"
        markers.append(f"<circle class='ref-node {cls}' cx='{x:.1f}' cy='{y:.1f}' r='{5.0 + min(abs(pnl) * 8.0, 5.0):.1f}'/>")
        for dot_idx in range(3 if pnl else 1):
            dot_angle = idx * 0.73 + dot_idx * 2.1
            dot_r = 9 + dot_idx * 5 + min(abs(pnl) * 3.0, 8.0)
            dot_color = "#9cff9f" if pnl > 0 else "#ff5f73" if pnl < 0 else "#d9cde7"
            spore_dots.append(
                f"<circle cx='{x + math.cos(dot_angle) * dot_r:.1f}' cy='{y + math.sin(dot_angle) * dot_r:.1f}' "
                f"r='{1.2 + dot_idx * .28:.1f}' fill='{dot_color}' opacity='.66'/>"
            )
    axis_marks = []
    if equity_points:
        axis_indices = np.linspace(0, len(equity_points) - 1, min(8, len(equity_points)), dtype=int).tolist()
        last_label = ""
        for idx in axis_indices:
            x, _ = equity_points[idx]
            label = _reference_short_date(work["ts"].iloc[idx], f"T+{idx + 1}")
            if label == last_label and len(axis_indices) > 4:
                label = _reference_short_clock(work["ts"].iloc[idx], label)
            last_label = label
            axis_marks.append(
                f"<line x1='{x:.1f}' y1='36' x2='{x:.1f}' y2='{height - 34:.1f}' stroke='rgba(247,241,232,.10)' "
                "stroke-width='1' stroke-dasharray='2 7'/>"
                f"<text x='{x:.1f}' y='{height - 15:.1f}' text-anchor='middle' fill='#a99bb9' font-size='9' font-weight='850'>"
                f"{html.escape(label)}</text>"
            )
    callouts = []
    if equity_points:
        candidate_indices = set(np.linspace(0, len(equity_points) - 1, min(6, len(equity_points)), dtype=int).tolist())
        candidate_indices.update(int(idx) for idx in work["trade_pnl"].abs().sort_values(ascending=False).head(4).index.tolist())
        candidate_indices.add(len(equity_points) - 1)
        selected_indices: list[int] = []
        for idx in sorted(candidate_indices):
            x, _ = equity_points[idx]
            if selected_indices and x - equity_points[selected_indices[-1]][0] < 72 and idx != len(equity_points) - 1:
                continue
            selected_indices.append(idx)
            if len(selected_indices) >= 7:
                break
        if (len(equity_points) - 1) not in selected_indices:
            selected_indices.append(len(equity_points) - 1)
        for ordinal, idx in enumerate(selected_indices[-7:]):
            x, y = equity_points[idx]
            box_w = 96
            box_h = 38
            box_x = max(58.0, min(x - box_w * 0.42, width - box_w - 14.0))
            prefer_above = y > 92 or ordinal % 2 == 0
            raw_box_y = y - 58.0 if prefer_above else y + 20.0
            box_y = max(16.0, min(raw_box_y, height - box_h - 34.0))
            label = _reference_short_date(work["ts"].iloc[idx], f"T+{idx + 1}")
            value = format_signed_money(float(work["equity"].iloc[idx]), always_sign=True)
            line_end_x = box_x + box_w * 0.5
            line_end_y = box_y + (box_h if box_y < y else 0)
            callouts.append(
                f"<g class='ref-callout'><line x1='{x:.1f}' y1='{y:.1f}' x2='{line_end_x:.1f}' y2='{line_end_y:.1f}'/>"
                f"<rect x='{box_x:.1f}' y='{box_y:.1f}' width='{box_w}' height='{box_h}' rx='8'/>"
                f"<text x='{box_x + box_w / 2:.1f}' y='{box_y + 14:.1f}' text-anchor='middle'>"
                f"<tspan x='{box_x + box_w / 2:.1f}' fill='#a99bb9' font-size='8'>{html.escape(label)}</tspan>"
                f"<tspan x='{box_x + box_w / 2:.1f}' dy='14'>{html.escape(value)}</tspan></text></g>"
            )
    legend = (
        "<g transform='translate(64 50)'>"
        "<rect x='-9' y='-17' width='132' height='71' rx='9' fill='rgba(7,6,12,.34)' stroke='rgba(247,241,232,.08)'/>"
        "<line x1='0' y1='0' x2='16' y2='0' stroke='url(#vineStroke)' stroke-width='3' stroke-linecap='round'/>"
        "<text x='24' y='4' fill='#f7f1e8' font-size='10' font-weight='850'>Equity path</text>"
        "<rect x='1' y='18' width='13' height='7' rx='3' fill='url(#vineEnvelope)'/>"
        "<text x='24' y='25' fill='#d9cde7' font-size='10' font-weight='850'>Trend envelope</text>"
        "<circle cx='8' cy='43' r='4' class='ref-node gain'/>"
        "<text x='24' y='47' fill='#d9cde7' font-size='10' font-weight='850'>Trade nodes</text>"
        "</g>"
    )
    return (
        "<svg class='ref-equity-svg' viewBox='0 0 780 392' aria-hidden='true'>"
        "<defs>"
        "<filter id='vineGlow'><feGaussianBlur stdDeviation='3.2' result='blur'/><feMerge><feMergeNode in='blur'/><feMergeNode in='SourceGraphic'/></feMerge></filter>"
        "<linearGradient id='vineStroke' x1='0' x2='1'><stop offset='0' stop-color='#9cff9f'/><stop offset='.58' stop-color='#f7e36f'/><stop offset='1' stop-color='#63f2b1'/></linearGradient>"
        "<linearGradient id='vineEnvelope' x1='0' x2='1'><stop offset='0' stop-color='#63f2b1' stop-opacity='.11'/><stop offset='.58' stop-color='#f7e36f' stop-opacity='.18'/><stop offset='1' stop-color='#79e7ff' stop-opacity='.12'/></linearGradient>"
        "<linearGradient id='rootFill' x1='0' x2='0' y1='0' y2='1'><stop offset='0' stop-color='#ff5f73' stop-opacity='.05'/><stop offset='1' stop-color='#d94cff' stop-opacity='.34'/></linearGradient>"
        "</defs>"
        "<rect class='ref-chart-bg' x='0' y='0' width='780' height='392' rx='22'/>"
        + "".join(axis_marks)
        + "".join(mycelium_threads)
        + "".join(field_spores)
        + "".join(contours)
        + f"<line class='ref-zero' x1='52' y1='{zero_y:.1f}' x2='748' y2='{zero_y:.1f}'/>"
        + (f"<path d='{envelope_path}' fill='url(#vineEnvelope)' stroke='rgba(121,231,255,.16)' stroke-width='1'/>" if envelope_path else "")
        + (f"<path class='ref-draw-area' d='{area_path}'/>" if area_path else "")
        + (f"<path class='ref-draw-line' d='{draw_path}'/>" if draw_path else "")
        + "".join(roots)
        + "".join(branches)
        + f"<path class='ref-vine-glow wide' d='{equity_path}'/>"
        + f"<path class='ref-vine-glow mid' d='{equity_path}'/>"
        + f"<path class='ref-vine' d='{equity_path}'/>"
        + "".join(spore_dots)
        + "".join(markers)
        + "<g class='ref-axis'><text x='20' y='62'>+20%</text><text x='28' y='{:.1f}'>0%</text><text x='18' y='330'>-20%</text></g>".format(zero_y + 4)
        + legend
        + "".join(callouts)
        + "</svg>"
    )


def reference_drawdown_roots_svg(curve: pd.DataFrame) -> str:
    width = 444
    height = 188
    if curve.empty or "drawdown" not in curve.columns:
        return "<div class='ref-empty'>Waiting for drawdown roots</div>"
    work = curve.copy().tail(90).reset_index(drop=True)
    if "ts" not in work.columns:
        work["ts"] = pd.NA
    work["drawdown"] = pd.to_numeric(work.get("drawdown", 0.0), errors="coerce").fillna(0.0)
    points = _series_to_svg_points(work["drawdown"], width, height, 28, 24, floor=min(float(work["drawdown"].min()) * 1.18, -0.05), ceiling=0.02)
    root_paths = []
    fork_paths = []
    stress_drips = []
    sparks = []
    grid = []
    for y_tick, label in [(25, "0%"), (70, "-5%"), (114, "-10%"), (158, "-20%")]:
        grid.append(
            f"<line x1='28' y1='{y_tick}' x2='416' y2='{y_tick}' stroke='rgba(247,241,232,.09)' stroke-width='1'/>"
            f"<text x='7' y='{y_tick + 4}' fill='#a99bb9' font-size='9' font-weight='850'>{label}</text>"
        )
    for idx, (x, y) in enumerate(points[:: max(1, len(points)//28)]):
        spread = 10 + (idx % 4) * 4
        root_paths.append(
            f"<path class='ref-dd-root' d='M {x:.1f} 25 C {x - spread:.1f} {max(32, y * .55):.1f}, "
            f"{x + spread * .8:.1f} {y:.1f}, {x:.1f} {height - 24:.1f}'/>"
        )
        if idx % 2 == 0:
            fork_paths.append(
                f"<path class='ref-dd-fork' d='M {x:.1f} {min(height - 34, y + 20):.1f} "
                f"C {x - spread * 1.6:.1f} {min(height - 25, y + 32):.1f}, {x - spread * 2.2:.1f} {height - 34:.1f}, "
                f"{x - spread * 2.8:.1f} {height - 22:.1f}'/>"
            )
        if idx % 4 == 1:
            stress_drips.append(
                f"<path class='ref-dd-drip' d='M {x:.1f} 26 C {x + 3:.1f} {y * .52:.1f}, {x - 5:.1f} {y * .82:.1f}, {x + 2:.1f} {y:.1f}'/>"
            )
        if idx % 3 == 0:
            sparks.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='2.2' fill='#ffb38f' opacity='.68'/>")
    date_tags = []
    if points:
        for idx in np.linspace(0, len(points) - 1, min(5, len(points)), dtype=int).tolist():
            x, _ = points[idx]
            label = _reference_short_date(work["ts"].iloc[idx], f"T+{idx + 1}")
            date_tags.append(f"<text x='{x:.1f}' y='180' text-anchor='middle' fill='#a99bb9' font-size='8' font-weight='850'>{html.escape(label)}</text>")
    trough_callout = ""
    if points:
        trough_idx = int(work["drawdown"].idxmin())
        trough_idx = min(max(trough_idx, 0), len(points) - 1)
        x, y = points[trough_idx]
        box_x = max(40.0, min(x + 10.0, width - 106.0))
        box_y = max(42.0, min(y - 22.0, height - 62.0))
        trough_callout = (
            f"<g class='ref-callout'><line x1='{x:.1f}' y1='{y:.1f}' x2='{box_x:.1f}' y2='{box_y + 18:.1f}'/>"
            f"<rect x='{box_x:.1f}' y='{box_y:.1f}' width='96' height='38' rx='8'/>"
            f"<text x='{box_x + 48:.1f}' y='{box_y + 14:.1f}' text-anchor='middle'>"
            f"<tspan x='{box_x + 48:.1f}' fill='#a99bb9' font-size='8'>{html.escape(_reference_short_date(work['ts'].iloc[trough_idx], 'LOW'))}</tspan>"
            f"<tspan x='{box_x + 48:.1f}' dy='14'>{html.escape(format_drawdown_money(work['drawdown'].iloc[trough_idx]))}</tspan></text></g>"
        )
    return (
        "<svg class='ref-roots-svg' viewBox='0 0 444 188' aria-hidden='true'>"
        "<rect x='0' y='0' width='444' height='188' rx='20' fill='rgba(7,6,12,.42)'/>"
        + "".join(grid)
        + "<line x1='28' y1='25' x2='416' y2='25' stroke='rgba(255,95,115,.65)' stroke-width='2'/>"
        + "".join(stress_drips)
        + "".join(root_paths)
        + "".join(fork_paths)
        + "".join(sparks)
        + f"<path class='ref-dd-line' d='{_svg_path(points)}'/>"
        + trough_callout
        + "".join(date_tags)
        + "</svg>"
    )


def reference_trade_seed_tape_html(df: pd.DataFrame, max_rows: int = 7, outcome_filter: str = "ALL") -> str:
    outcome_filter = str(outcome_filter or "ALL").upper()
    recent_pool = sorted_recent_trades(df, max_rows=max(max_rows * 5, max_rows))
    if recent_pool.empty:
        return "<div class='ref-seed empty'>Waiting for scored trades</div>"
    pool_pnl_values = trade_pnl_series(recent_pool)
    pool_states: list[str] = []
    for idx, (_, row) in enumerate(recent_pool.iterrows()):
        pnl_value = pool_pnl_values.iloc[idx] if idx < len(pool_pnl_values) else np.nan
        raw_state = str(row.get("display_outcome", "flat") or "flat").lower()
        state = (
            "win"
            if pd.notna(pnl_value) and pnl_value > 0
            else "loss"
            if pd.notna(pnl_value) and pnl_value < 0
            else "flat"
            if raw_state not in {"win", "loss"}
            else raw_state
        )
        pool_states.append(state)
    recent_pool = recent_pool.assign(_ref_seed_state=pool_states)
    if outcome_filter in {"WIN", "LOSS", "FLAT"}:
        recent = recent_pool[recent_pool["_ref_seed_state"].eq(outcome_filter.lower())].head(max_rows).copy()
    else:
        recent = recent_pool.head(max_rows).copy()
    tape_wins = int((recent_pool["_ref_seed_state"] == "win").sum())
    tape_losses = int((recent_pool["_ref_seed_state"] == "loss").sum())
    tape_flats = int((recent_pool["_ref_seed_state"] == "flat").sum())
    if recent.empty:
        filter_label = html.escape(outcome_filter)
        return (
            "<div class='ref-seed-meta'><span>"
            f"Filter {filter_label}</span><span>Outcome {tape_wins}W {tape_losses}L {tape_flats}F</span>"
            "</div><div class='ref-seed empty'>No matching trade seeds</div>"
        )
    pnl_values = trade_pnl_series(recent)
    if "display_qty" in recent.columns:
        qty_source = pd.to_numeric(recent["display_qty"], errors="coerce")
    elif "qty" in recent.columns:
        qty_source = pd.to_numeric(recent["qty"], errors="coerce")
    else:
        qty_source = pd.Series(dtype=float)
    qty_total = int(qty_source.dropna().sum()) if not qty_source.dropna().empty else 0
    avg_pnl = float(pnl_values.dropna().mean()) if not pnl_values.dropna().empty else np.nan
    latest_row = recent.iloc[0]
    latest_stamp = latest_row.get("exit_ts", latest_row.get("entry_ts", None))
    try:
        if pd.isna(latest_stamp) or str(latest_stamp) == "":
            latest_stamp = latest_row.get("entry_ts", None)
    except Exception:
        latest_stamp = latest_row.get("entry_ts", None)
    rail_meta = (
        "<div class='ref-seed-meta'>"
        f"<span>Filter {html.escape(outcome_filter)}</span><span>Outcome {tape_wins}W {tape_losses}L {tape_flats}F</span>"
        f"<span>Qty {qty_total if qty_total else 'NA'}</span><span>Avg {html.escape(format_signed_money(avg_pnl, always_sign=True))}</span>"
        f"<span>Latest {_reference_short_clock(latest_stamp, str(latest_row.get('ma_time', 'NA') or 'NA'))}</span>"
        "</div>"
    )
    seeds = []
    for idx, (_, row) in enumerate(recent.iterrows()):
        pnl_value = pnl_values.iloc[idx] if idx < len(pnl_values) else np.nan
        raw_state = str(row.get("display_outcome", "flat") or "flat").lower()
        state = "win" if pd.notna(pnl_value) and pnl_value > 0 else "loss" if pd.notna(pnl_value) and pnl_value < 0 else "flat" if raw_state not in {"win", "loss"} else raw_state
        side = str(row.get("side", "") or "NA").upper()
        qty = row.get("display_qty", row.get("qty", np.nan))
        try:
            qty_text = str(int(float(qty))) if pd.notna(qty) else "NA"
        except Exception:
            qty_text = "NA"
        entry_label = format_cents(row.get("entry_fill_cents_used"))
        exit_label = format_cents(row.get("exit_fill_cents_used"))
        stamp = row.get("exit_ts", row.get("entry_ts", None))
        try:
            if pd.isna(stamp) or str(stamp) == "":
                stamp = row.get("entry_ts", None)
        except Exception:
            stamp = row.get("entry_ts", None)
        time_label = _reference_short_clock(stamp, str(row.get("ma_time", "NA") or "NA"))
        title = html.escape(
            f"{str(row.get('market', 'NA') or 'NA')} | {side} qty {qty_text} | entry {entry_label} | "
            f"exit {exit_label} | PnL {format_signed_money(pnl_value, always_sign=True)}"
        )
        seeds.append(
            f"<div class='ref-seed {state}' title='{title}'>"
            f"<div class='ref-seed-time'>{html.escape(time_label)}</div>"
            f"<div class='ref-seed-market'>{html.escape(compact_market_label(row.get('market', 'NA')))}</div>"
            f"<div class='ref-seed-side'>{html.escape(side)} <span style='color:#a99bb9'>qty {html.escape(qty_text)}</span></div>"
            f"<div class='ref-seed-price'>{html.escape(entry_label)} -> {html.escape(exit_label)}</div>"
            f"<div class='ref-seed-pnl'>{html.escape(format_signed_money(pnl_value, always_sign=True))}</div>"
            "</div>"
        )
    connectors = "".join(
        f"<span style='position:absolute;left:{10 + (idx + 1) * (80 / max(len(seeds), 1)):.1f}%;bottom:52px;width:7px;height:7px;"
        "border-radius:50%;background:#f7c85f;box-shadow:0 0 10px rgba(247,200,95,.72);z-index:1'></span>"
        for idx in range(max(len(seeds) - 1, 0))
    )
    return rail_meta + "<div class='ref-seed-rail'></div>" + connectors + "<div class='ref-seeds-inner'>" + "".join(seeds) + "</div>"


def render_actual_reference_art_cockpit(
    *,
    active_dataset_label_live: str,
    active_dataset_tag: str,
    refresh_mode_label: str,
    lock_status: dict[str, str],
    accounting_status: dict[str, Any],
    current_market_label: str,
    command_sync_label: str,
    command_book: str,
    command_spread_note: str,
    command_trade_note: str,
    net_pnl_display: float,
    net_pnl_pct: float,
    max_drawdown: float,
    win_rate: float,
    wins: int,
    losses: int,
    flats: int,
    entries_total: int,
    open_positions: int,
    latest_trade_label: str,
    latest_trade_note: str,
    state_status: str,
    heartbeat_age_text: str,
    displayed_curve: pd.DataFrame,
    completed_pnl: pd.Series,
    trades: pd.DataFrame,
    watch_close_label: str,
    yes_bid: Any,
    yes_ask: Any,
    no_bid: Any,
    no_ask: Any,
    yes_spread: Any,
    market_bias: str,
    feed_age_text: str,
    reaction_text: str,
    score_age_text: str,
    telemetry_text: str,
    equity_range_label: str = "ALL",
    seed_filter_label: str = "ALL",
) -> bool:
    art_uri = reference_dashboard_art_data_uri(str(REFERENCE_DASHBOARD_ART_PATH))
    if not art_uri:
        return False

    curve_values = displayed_curve["equity"] if not displayed_curve.empty and "equity" in displayed_curve.columns else pd.Series(dtype=float)
    drawdown_values = displayed_curve["drawdown"] if not displayed_curve.empty and "drawdown" in displayed_curve.columns else pd.Series(dtype=float)
    equity_svg = reference_equity_vine_svg(displayed_curve)
    drawdown_svg = reference_drawdown_roots_svg(displayed_curve)
    spores_html = outcome_spores_html(completed_pnl)
    depth_svg = build_orderbook_depth_svg(yes_bid, yes_ask, no_bid, no_ask, yes_spread)
    pnl_class = "gain" if net_pnl_display > 0 else "loss" if net_pnl_display < 0 else "flat"
    dd_class = "loss" if max_drawdown < 0 else "flat"
    positive_sum = float(completed_pnl[completed_pnl > 0].sum()) if not completed_pnl.empty else 0.0
    negative_sum = abs(float(completed_pnl[completed_pnl < 0].sum())) if not completed_pnl.empty else 0.0
    profit_factor = positive_sum / negative_sum if negative_sum > 0 else np.nan
    expectancy = float(completed_pnl.mean()) if not completed_pnl.empty else np.nan
    api_value = str(accounting_status.get("value") or "NA")
    api_note = str(accounting_status.get("note") or "")
    api_class = html.escape(str(accounting_status.get("class") or ""))
    lock_value = str(lock_status.get("value") or "NA")
    lock_note = str(lock_status.get("note") or "")
    lock_class = html.escape(str(lock_status.get("class") or "neutral"))
    range_label = str(equity_range_label or "ALL").upper()
    seed_label = str(seed_filter_label or "ALL").upper()
    dataset_visual_label = "BTC15M Live" if "live" in str(active_dataset_tag).lower() else "BTC15M Research"
    market_label = compact_market_label(current_market_label)
    profit_factor_label = "NA" if pd.isna(profit_factor) else f"{profit_factor:.2f}x"
    expectancy_label = format_signed_money(expectancy, always_sign=True)
    latest_trade_display = latest_trade_label if latest_trade_label != "No trades" else "Waiting"
    latest_trade_note_display = latest_trade_note if latest_trade_note != "Waiting on scored fills" else command_trade_note
    seed_html = reference_trade_seed_tape_html(trades, max_rows=6, outcome_filter=seed_label)
    live_range_pills = "".join(
        f"<span class='active'>{html.escape(option)}</span>"
        if option == range_label
        else f"<span>{html.escape(option)}</span>"
        for option in EQUITY_RANGE_OPTIONS
    )
    diagnostics_rows = (
        f"<div class='ref-live-row'><span>API health</span><b>{html.escape(api_value)}</b></div>"
        f"<div class='ref-live-row'><span>Data feed</span><b>{html.escape(feed_age_text)}</b></div>"
        f"<div class='ref-live-row'><span>Latency</span><b>{html.escape(reaction_text)}</b></div>"
        f"<div class='ref-live-row'><span>Score file</span><b>{html.escape(score_age_text)}</b></div>"
        f"<div class='ref-live-row'><span>Telemetry</span><b>{html.escape(telemetry_text)}</b></div>"
    )
    live_panels_html = f"""
          <div class="ref-live-top ref-live-top-dataset"><span>Dataset</span><b>{html.escape(dataset_visual_label)}</b><em>{html.escape(active_dataset_label_live[:46])}</em></div>
          <div class="ref-live-top ref-live-top-sync"><span>Sample Sync</span><b>{html.escape(command_sync_label)}</b><em>{html.escape(feed_age_text)} | {html.escape(reaction_text)}</em></div>
          <div class="ref-live-top ref-live-top-refresh"><span>{html.escape(str(refresh_mode_label).upper())}</span><b>Refresh now</b><em>click painted button</em></div>
          <div class="ref-live-top ref-live-top-lock {lock_class}"><span>Live Lock</span><b>{html.escape(lock_value)}</b><em>{html.escape(lock_note[:38])}</em></div>
          <div class="ref-live-top ref-live-top-api {api_class}"><span>Kalshi API</span><b>{html.escape(api_value)}</b><em>{html.escape(api_note[:44])}</em></div>
          <div class="ref-live-pod ref-live-pod-pnl {pnl_class}"><span>Net P&amp;L</span><b>{html.escape(format_signed_money(net_pnl_display))}</b><em>{html.escape(format_pct(net_pnl_pct))} over {html.escape(range_label)}</em>{sparkline_svg(curve_values, "#9cff9f" if net_pnl_display >= 0 else "#ff5f73")}</div>
          <div class="ref-live-pod ref-live-pod-dd {dd_class}"><span>Max Drawdown</span><b>{html.escape(format_drawdown_money(max_drawdown))}</b><em>underwater low</em>{sparkline_svg(drawdown_values, "#ff5f73", "rgba(255,95,115,0.15)")}</div>
          <div class="ref-live-pod ref-live-pod-win"><span>Win Rate</span><b>{html.escape(format_pct(win_rate))}</b><em>{wins}W / {losses}L / {flats}F</em>{living_ring_svg(win_rate, label=f"{win_rate:.0f}%")}</div>
          <div class="ref-live-pod ref-live-pod-open"><span>Open Positions</span><b>{open_positions}</b><em>{entries_total} total entries</em>{living_ring_svg(100 if open_positions else 8, color="#79e7ff", label=str(open_positions))}</div>
          <div class="ref-live-pod ref-live-pod-pulse {html.escape(str(state_status).lower())}"><span>Performance Pulse</span><b>{html.escape(str(state_status))}</b><em>{html.escape(heartbeat_age_text)}</em>{living_microbars_svg(curve_values.diff().fillna(curve_values) if not curve_values.empty else [], "#f7c85f")}</div>
          <div class="ref-live-panel ref-live-equity-panel"><div class="ref-live-panel-head"><div><span>EQUITY VINE</span><b>Total return {html.escape(format_pct(net_pnl_pct))}</b></div><div class="ref-pills">{live_range_pills}</div></div>{equity_svg}</div>
          <div class="ref-live-panel ref-live-drawdown-panel"><div class="ref-live-panel-head tight"><div><span>DRAWDOWN ROOTS</span><b>Max DD {html.escape(format_drawdown_money(max_drawdown))}</b></div></div>{drawdown_svg}</div>
          <div class="ref-live-panel ref-live-spores-panel"><div class="ref-live-panel-head tight"><div><span>OUTCOME SPORES</span><b>Trades by outcome cluster</b></div></div>{spores_html}</div>
          <div class="ref-live-panel ref-live-vitals-panel"><div class="ref-live-title">P&amp;L VITALS</div><div class="ref-live-row"><span>Total return</span><b>{html.escape(format_pct(net_pnl_pct))}</b></div><div class="ref-live-row"><span>Avg daily P&amp;L</span><b>{html.escape(expectancy_label)}</b></div><div class="ref-live-row"><span>Profit factor</span><b>{html.escape(profit_factor_label)}</b></div><div class="ref-live-row"><span>Win rate</span><b>{html.escape(format_pct(win_rate))}</b></div>{sparkline_svg(completed_pnl.cumsum() if not completed_pnl.empty else [], "#9cff9f")}</div>
          <div class="ref-live-panel ref-live-lock-panel {lock_class}"><div class="ref-live-title">LIVE LOCK</div><div class="ref-live-lock-value">{html.escape(lock_value)}</div><div class="ref-note">{html.escape(lock_note)}</div><div class="ref-light-row"><span></span><span></span><span></span><span></span><span></span><span></span></div></div>
          <div class="ref-live-panel ref-live-market-panel"><div class="ref-live-title">MARKET PULSE <span>15M</span></div><div class="ref-live-market-value">{html.escape(market_label)}</div><div class="ref-live-row"><span>Close</span><b>{html.escape(watch_close_label)}</b></div><div class="ref-live-row"><span>YES</span><b>{html.escape(format_cents(yes_bid))} / {html.escape(format_cents(yes_ask))}</b></div><div class="ref-live-row"><span>NO</span><b>{html.escape(format_cents(no_bid))} / {html.escape(format_cents(no_ask))}</b></div><div class="ref-note">{html.escape(market_bias)}</div></div>
          <div class="ref-live-panel ref-live-depth-panel"><div class="ref-live-title">ORDERBOOK DEPTH</div>{depth_svg}</div>
          <div class="ref-live-panel ref-live-seeds-panel"><div class="ref-live-seed-title">TRADE SEEDS <span>{html.escape(seed_label)} executions</span></div>{seed_html}</div>
          <div class="ref-live-panel ref-live-diagnostics-panel"><div class="ref-live-title">DIAGNOSTICS <span>LIVE</span></div>{diagnostics_rows}</div>
    """

    def hitbox(cls: str, href: str, label: str) -> str:
        return f"<a class='ref-hit {cls}' href='{html.escape(href)}' target='_self' aria-label='{html.escape(label)}' title='{html.escape(label)}'></a>"

    range_hits = "".join(
        hitbox(f"ref-hit-range ref-hit-range-{option.lower()}", f"?dash_range={html.escape(option)}", f"Range {option}")
        for option in EQUITY_RANGE_OPTIONS
    )
    seed_hits = "".join(
        hitbox(f"ref-hit-seed ref-hit-seed-{option.lower()}", f"?dash_seed={html.escape(option)}", f"Trade seed filter {option}")
        for option in SEED_FILTER_OPTIONS
    )
    active_ranges = "".join(
        f"<span class='ref-art-active-range ref-art-active-range-{option.lower()}'></span>" if option == range_label and option != "ALL" else ""
        for option in EQUITY_RANGE_OPTIONS
    )

    st.markdown(
        f"""
        <div class="ref-art-cockpit">
          <img class="ref-art-image" src="{art_uri}" alt="BTC15M Living Analytics reference cockpit art" />
          {hitbox("ref-hit-refresh", "?dash_action=refresh", "Refresh now")}
          {range_hits}
          {seed_hits}
          {active_ranges}
          {live_panels_html}
          <div class="ref-art-live ref-art-dataset">
            <b>{html.escape(dataset_visual_label)}</b><span>{html.escape(active_dataset_label_live[:42])}</span>
          </div>
          <div class="ref-art-live ref-art-sync">
            <b>{html.escape(command_sync_label)}</b><span>{html.escape(feed_age_text)} | {html.escape(reaction_text)}</span>
          </div>
          <div class="ref-art-live ref-art-pnl {pnl_class}">
            <b>{html.escape(format_signed_money(net_pnl_display))}</b><span>{html.escape(format_pct(net_pnl_pct))} over {html.escape(range_label)}</span>
          </div>
          <div class="ref-art-live ref-art-dd {dd_class}">
            <b>{html.escape(format_drawdown_money(max_drawdown))}</b><span>max drawdown</span>
          </div>
          <div class="ref-art-live ref-art-win">
            <b>{html.escape(format_pct(win_rate))}</b><span>{wins}W / {losses}L / {flats}F</span>
          </div>
          <div class="ref-art-live ref-art-open">
            <b>{open_positions}</b><span>{entries_total} entries</span>
          </div>
          <div class="ref-art-live ref-art-pulse {html.escape(str(state_status).lower())}">
            <b>{html.escape(str(state_status))}</b><span>{html.escape(heartbeat_age_text)}</span>
          </div>
          <div class="ref-art-live ref-art-vitals">
            <span>Return <b>{html.escape(format_pct(net_pnl_pct))}</b></span>
            <span>Avg <b>{html.escape(expectancy_label)}</b></span>
            <span>PF <b>{html.escape(profit_factor_label)}</b></span>
          </div>
          <div class="ref-art-live ref-art-api {api_class}">
            <b>{html.escape(api_value)}</b><span>{html.escape(api_note[:44])}</span>
          </div>
          <div class="ref-art-live ref-art-lock {lock_class}">
            <b>{html.escape(lock_value)}</b><span>{html.escape(lock_note[:44])}</span>
          </div>
          <div class="ref-art-live ref-art-market">
            <b>{html.escape(market_label)}</b>
            <span>{html.escape(watch_close_label)} | YES {html.escape(format_cents(yes_bid))}/{html.escape(format_cents(yes_ask))}</span>
            <span>NO {html.escape(format_cents(no_bid))}/{html.escape(format_cents(no_ask))} | {html.escape(market_bias)}</span>
          </div>
          <div class="ref-art-live ref-art-seeds">
            <b>{html.escape(seed_label)} seeds</b><span>{html.escape(latest_trade_display)} | {html.escape(latest_trade_note_display[:54])}</span>
          </div>
          <div class="ref-art-live ref-art-diagnostics">
            <span>Score <b>{html.escape(score_age_text)}</b></span>
            <span>Telemetry <b>{html.escape(telemetry_text)}</b></span>
            <span>{html.escape(command_book)} | {html.escape(command_spread_note)}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return True


def render_reference_cockpit(
    *,
    active_dataset_label_live: str,
    active_dataset_tag: str,
    refresh_mode_label: str,
    lock_status: dict[str, str],
    accounting_status: dict[str, Any],
    current_market_label: str,
    command_sync_label: str,
    command_book: str,
    command_spread_note: str,
    command_trade_note: str,
    command_spark: str,
    net_pnl_display: float,
    net_pnl_pct: float,
    max_drawdown: float,
    win_rate: float,
    wins: int,
    losses: int,
    flats: int,
    entries_total: int,
    open_positions: int,
    latest_trade_label: str,
    latest_trade_note: str,
    state_status: str,
    heartbeat_age_text: str,
    displayed_curve: pd.DataFrame,
    completed_pnl: pd.Series,
    trades: pd.DataFrame,
    watch_close_label: str,
    yes_bid: Any,
    yes_ask: Any,
    no_bid: Any,
    no_ask: Any,
    yes_spread: Any,
    market_bias: str,
    hb: dict[str, Any],
    feed_age_text: str,
    reaction_text: str,
    score_age_text: str,
    telemetry_text: str,
    equity_range_label: str = "ALL",
    seed_filter_label: str = "ALL",
) -> None:
    if USE_GENERATED_REFERENCE_ART_COCKPIT and render_actual_reference_art_cockpit(
        active_dataset_label_live=active_dataset_label_live,
        active_dataset_tag=active_dataset_tag,
        refresh_mode_label=refresh_mode_label,
        lock_status=lock_status,
        accounting_status=accounting_status,
        current_market_label=current_market_label,
        command_sync_label=command_sync_label,
        command_book=command_book,
        command_spread_note=command_spread_note,
        command_trade_note=command_trade_note,
        net_pnl_display=net_pnl_display,
        net_pnl_pct=net_pnl_pct,
        max_drawdown=max_drawdown,
        win_rate=win_rate,
        wins=wins,
        losses=losses,
        flats=flats,
        entries_total=entries_total,
        open_positions=open_positions,
        latest_trade_label=latest_trade_label,
        latest_trade_note=latest_trade_note,
        state_status=state_status,
        heartbeat_age_text=heartbeat_age_text,
        displayed_curve=displayed_curve,
        completed_pnl=completed_pnl,
        trades=trades,
        watch_close_label=watch_close_label,
        yes_bid=yes_bid,
        yes_ask=yes_ask,
        no_bid=no_bid,
        no_ask=no_ask,
        yes_spread=yes_spread,
        market_bias=market_bias,
        feed_age_text=feed_age_text,
        reaction_text=reaction_text,
        score_age_text=score_age_text,
        telemetry_text=telemetry_text,
        equity_range_label=equity_range_label,
        seed_filter_label=seed_filter_label,
    ):
        return
    curve_values = displayed_curve["equity"] if not displayed_curve.empty and "equity" in displayed_curve.columns else pd.Series(dtype=float)
    drawdown_values = displayed_curve["drawdown"] if not displayed_curve.empty and "drawdown" in displayed_curve.columns else pd.Series(dtype=float)
    equity_svg = reference_equity_vine_svg(displayed_curve)
    drawdown_svg = reference_drawdown_roots_svg(displayed_curve)
    spores_html = outcome_spores_html(completed_pnl)
    depth_svg = build_orderbook_depth_svg(yes_bid, yes_ask, no_bid, no_ask, yes_spread)
    equity_range_label = str(equity_range_label or "ALL").upper()
    seed_filter_label = str(seed_filter_label or "ALL").upper()
    seed_html = reference_trade_seed_tape_html(trades, outcome_filter=seed_filter_label)
    positive_sum = float(completed_pnl[completed_pnl > 0].sum()) if not completed_pnl.empty else 0.0
    negative_sum = abs(float(completed_pnl[completed_pnl < 0].sum())) if not completed_pnl.empty else 0.0
    profit_factor = positive_sum / negative_sum if negative_sum > 0 else np.nan
    expectancy = float(completed_pnl.mean()) if not completed_pnl.empty else np.nan
    api_note = str(accounting_status.get("note") or "")
    api_meter = 100 if accounting_status.get("class") == "verified" else 58 if accounting_status.get("class") == "partial" else 24
    pnl_class = "gain" if net_pnl_display > 0 else "loss" if net_pnl_display < 0 else "flat"
    lock_class = html.escape(str(lock_status.get("class") or "neutral"))
    dataset_visual_label = "BTC15M Live" if "live" in str(active_dataset_tag).lower() else "BTC15M Research"
    dataset_detail = active_dataset_label_live if len(active_dataset_label_live) < 54 else active_dataset_label_live[:51] + "..."
    def ref_meter(label: str, value: Any, pct: float, color: str = "#9cff9f") -> str:
        pct_value = max(0.0, min(100.0, float(pct)))
        return (
            f"<div class='ref-row'><span>{html.escape(label)}</span><b>{html.escape(str(value))}</b></div>"
            "<div style='height:5px;border-radius:999px;background:rgba(247,241,232,.10);overflow:hidden;margin-top:4px'>"
            f"<span style='display:block;height:100%;width:{pct_value:.1f}%;border-radius:999px;background:{html.escape(color)};"
            f"box-shadow:0 0 9px {html.escape(color)}'></span></div>"
        )

    def ms_meter(text: str, healthy_ms: float) -> float:
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)", str(text or ""))
        if not match:
            return 18.0
        value_ms = float(match.group(1))
        return max(16.0, min(100.0, 100.0 - (value_ms / max(healthy_ms, 1.0)) * 42.0))

    score_lower = str(score_age_text or "").lower()
    score_meter = 16 if "missing" in score_lower or "unknown" in score_lower else 54 if "d" in score_lower else 72 if "h" in score_lower else 88
    telemetry_meter = 88 if str(telemetry_text).lower() == "ready" else 24
    diagnostics_html = (
        ref_meter("API health", accounting_status.get("value") or "NA", api_meter, "#9cff9f" if api_meter >= 80 else "#f7c85f")
        + ref_meter("Data feed", feed_age_text, ms_meter(feed_age_text, 1000.0), "#79e7ff")
        + ref_meter("Latency", reaction_text, ms_meter(reaction_text, 250.0), "#9cff9f")
        + ref_meter("Score file", score_age_text, score_meter, "#f7c85f")
        + ref_meter("Telemetry", telemetry_text, telemetry_meter, "#d94cff" if telemetry_meter < 50 else "#9cff9f")
    )
    chart_tools_html = """
            <div aria-hidden="true" style="position:absolute;right:18px;top:118px;display:grid;gap:8px;z-index:5">
              <div title="Focus path" style="width:31px;height:31px;border-radius:50%;border:1px solid rgba(247,241,232,.28);display:grid;place-items:center;background:rgba(7,6,12,.62);box-shadow:0 0 14px rgba(121,231,255,.16)">
                <svg viewBox="0 0 24 24" width="17" height="17"><path d="M2 12s4-6 10-6 10 6 10 6-4 6-10 6S2 12 2 12Z" fill="none" stroke="#f7f1e8" stroke-width="1.7"/><circle cx="12" cy="12" r="2.6" fill="none" stroke="#9cff9f" stroke-width="1.7"/></svg>
              </div>
              <div title="Envelope layers" style="width:31px;height:31px;border-radius:50%;border:1px solid rgba(247,241,232,.28);display:grid;place-items:center;background:rgba(7,6,12,.62);box-shadow:0 0 14px rgba(121,231,255,.16)">
                <svg viewBox="0 0 24 24" width="17" height="17"><path d="M12 4 21 9 12 14 3 9 12 4Z" fill="none" stroke="#79e7ff" stroke-width="1.6"/><path d="M5 13 12 17 19 13M5 17 12 21 19 17" fill="none" stroke="#d9cde7" stroke-width="1.4"/></svg>
              </div>
              <div title="Trade nodes" style="width:31px;height:31px;border-radius:50%;border:1px solid rgba(247,241,232,.28);display:grid;place-items:center;background:rgba(7,6,12,.62);box-shadow:0 0 14px rgba(121,231,255,.16)">
                <svg viewBox="0 0 24 24" width="17" height="17"><circle cx="12" cy="12" r="7" fill="none" stroke="#f7c85f" stroke-width="1.5"/><path d="M12 5v14M5 12h14" stroke="#f7f1e8" stroke-width="1.4"/></svg>
              </div>
              <div title="Root scan" style="width:31px;height:31px;border-radius:50%;border:1px solid rgba(247,241,232,.28);display:grid;place-items:center;background:rgba(7,6,12,.62);box-shadow:0 0 14px rgba(121,231,255,.16)">
                <svg viewBox="0 0 24 24" width="17" height="17"><path d="M4 8c4 0 4 8 8 8s4-8 8-8" fill="none" stroke="#ff6f7f" stroke-width="1.7"/><path d="M6 16h12" stroke="#a99bb9" stroke-width="1.3"/></svg>
              </div>
            </div>
    """
    range_pills = "".join(
        f"<span class='active'>{html.escape(option)}</span>"
        if option == equity_range_label
        else f"<span>{html.escape(option)}</span>"
        for option in EQUITY_RANGE_OPTIONS
    )
    st.markdown(
        f"""
        <div class="ref-cockpit">
          <div class="ref-botanical-rail" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span></div>
          <div class="ref-icon-rail" aria-hidden="true"><span title="overview"></span><span title="vitals"></span><span title="book"></span><span title="nodes"></span><span title="roots"></span><span title="diagnostics"></span><span title="sync"></span></div>
          <div class="ref-top">
            <div class="ref-brand">
              <div class="ref-orb"><span>15M</span></div>
              <div><div class="ref-brand-title">BTC15M</div><div class="ref-brand-sub">LIVING ANALYTICS</div><div class="ref-brand-micro">v3.2.7 - bot build 118</div></div>
            </div>
            <div class="ref-top-module ref-dataset">
              <div class="ref-label">Dataset</div>
              <div class="ref-select-text">{html.escape(dataset_visual_label)}</div>
              <div class="ref-command-note">{html.escape(command_trade_note)} | {html.escape(dataset_detail)}</div>
            </div>
            <div class="ref-top-module ref-sync">
              <div class="ref-label">Sample Sync</div>
              <div class="ref-main">{html.escape(command_sync_label)}</div>
              <div class="ref-command-note">{html.escape(command_book)} | {html.escape(command_spread_note)}</div>
              {command_spark}
            </div>
            <div class="ref-refresh"><div class="ref-main">{html.escape(str(refresh_mode_label).upper())}</div><div>Sync status</div><span>Use live controls</span></div>
            <div class="ref-top-module ref-lock {lock_class}">
              <div class="ref-label">Live Lock</div><div class="ref-main">{html.escape(str(lock_status.get("value") or "NA"))}</div>
              <div class="ref-command-note">{html.escape(str(lock_status.get("note") or ""))}</div>
            </div>
            <div class="ref-top-module ref-api {html.escape(str(accounting_status.get("class") or ""))}">
              <div class="ref-label">Kalshi API</div><div class="ref-main">{html.escape(str(accounting_status.get("value") or "NA"))}</div>
              <div class="ref-command-note">{html.escape(api_note)}</div><div class="ref-meter"><span style="width:{api_meter}%"></span></div>
            </div>
          </div>
          <div class="ref-left">
            <div class="ref-pod {pnl_class}"><div class="ref-label">Net P&L</div><div class="ref-pod-value">{html.escape(format_signed_money(net_pnl_display))}</div><div class="ref-note">{html.escape(format_pct(net_pnl_pct))} return</div>{sparkline_svg(curve_values, "#9cff9f" if net_pnl_display >= 0 else "#ff5f73")}</div>
            <div class="ref-pod loss"><div class="ref-label">Max Drawdown</div><div class="ref-pod-value">{html.escape(format_drawdown_money(max_drawdown))}</div><div class="ref-note">underwater low</div>{sparkline_svg(drawdown_values, "#ff5f73", "rgba(255,95,115,0.15)")}</div>
            <div class="ref-pod gain"><div class="ref-label">Win Rate</div><div class="ref-pod-value">{html.escape(format_pct(win_rate))}</div><div class="ref-note">{wins} / {wins + losses}</div>{living_ring_svg(win_rate, label=f"{win_rate:.0f}%")}</div>
            <div class="ref-pod flat"><div class="ref-label">Open Positions</div><div class="ref-pod-value">{open_positions}</div><div class="ref-note">{entries_total} total entries</div>{living_ring_svg(100 if open_positions else 8, color="#79e7ff", label=str(open_positions))}</div>
            <div class="ref-pod {html.escape(str(state_status).lower())}"><div class="ref-label">Performance Pulse</div><div class="ref-pod-value">{html.escape(str(state_status))}</div><div class="ref-note">{html.escape(heartbeat_age_text)}</div>{living_microbars_svg(curve_values.diff().fillna(curve_values) if not curve_values.empty else [], "#f7c85f")}</div>
          </div>
          <div class="ref-chart-panel">
            <div class="ref-panel-head"><div><div class="ref-title">EQUITY VINE</div><div class="ref-sub">Total return {html.escape(format_pct(net_pnl_pct))}</div></div><div class="ref-pills">{range_pills}</div></div>
            {equity_svg}
            {chart_tools_html}
          </div>
          <div class="ref-lower-left"><div class="ref-panel-head tight"><div><div class="ref-title">DRAWDOWN ROOTS</div><div class="ref-sub">Max DD {html.escape(format_drawdown_money(max_drawdown))}</div></div></div>{drawdown_svg}</div>
          <div class="ref-lower-right"><div class="ref-panel-head tight"><div><div class="ref-title">OUTCOME SPORES</div><div class="ref-sub">Trades by outcome cluster</div></div></div>{spores_html}</div>
          <div class="ref-right">
            <div class="ref-side-module"><div class="ref-title">P&L VITALS</div><div class="ref-row"><span>Total return</span><b>{html.escape(format_pct(net_pnl_pct))}</b></div><div class="ref-row"><span>Avg daily P&L</span><b>{html.escape(format_signed_money(expectancy, always_sign=True))}</b></div><div class="ref-row"><span>Profit factor</span><b>{"NA" if pd.isna(profit_factor) else f"{profit_factor:.2f}x"}</b></div><div class="ref-row"><span>Win rate</span><b>{html.escape(format_pct(win_rate))}</b></div>{sparkline_svg(completed_pnl.cumsum() if not completed_pnl.empty else [], "#9cff9f")}</div>
            <div class="ref-side-module {lock_class}"><div class="ref-title">LIVE LOCK</div><div class="ref-lock-ring">{html.escape(str(lock_status.get("value") or "NA"))}</div><div class="ref-note">{html.escape(str(lock_status.get("note") or ""))}</div><div class="ref-light-row"><span></span><span></span><span></span><span></span><span></span><span></span></div></div>
            <div class="ref-side-module"><div class="ref-title">MARKET PULSE <span>15M</span></div><div class="ref-market">{html.escape(compact_market_label(current_market_label))}</div><div class="ref-row"><span>Close</span><b>{html.escape(watch_close_label)}</b></div><div class="ref-row"><span>YES</span><b>{html.escape(format_cents(yes_bid))} / {html.escape(format_cents(yes_ask))}</b></div><div class="ref-row"><span>NO</span><b>{html.escape(format_cents(no_bid))} / {html.escape(format_cents(no_ask))}</b></div><div class="ref-note">{html.escape(market_bias)}</div></div>
            <div class="ref-side-module"><div class="ref-title">ORDERBOOK DEPTH</div>{depth_svg}</div>
          </div>
          <div class="ref-seed-tape"><div class="ref-seed-title">TRADE SEEDS <span>{html.escape(seed_filter_label)} executions</span></div>{seed_html}</div>
          <div class="ref-diagnostics"><div class="ref-title">DIAGNOSTICS <span>collapsed</span></div>{diagnostics_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dark_reference_dashboard(
    *,
    active_dataset_label_live: str,
    active_dataset_tag: str,
    refresh_mode_label: str,
    lock_status: dict[str, str],
    accounting_status: dict[str, Any],
    current_market_label: str,
    command_sync_label: str,
    command_book: str,
    command_spread_note: str,
    command_trade_note: str,
    command_spark: str,
    net_pnl_display: float,
    net_pnl_pct: float,
    max_drawdown: float,
    win_rate: float,
    wins: int,
    losses: int,
    flats: int,
    entries_total: int,
    open_positions: int,
    latest_trade_label: str,
    latest_trade_note: str,
    latest_trade_class: str,
    state_status: str,
    heartbeat_age_text: str,
    displayed_curve: pd.DataFrame,
    completed_pnl: pd.Series,
    trades: pd.DataFrame,
    watch_close_label: str,
    yes_bid: Any,
    yes_ask: Any,
    no_bid: Any,
    no_ask: Any,
    yes_spread: Any,
    market_bias: str,
    hb: dict[str, Any],
    feed_age_text: str,
    reaction_text: str,
    score_age_text: str,
    telemetry_text: str,
    equity_range_label: str = "ALL",
    seed_filter_label: str = "ALL",
) -> None:
    context = dashboard_strategy_context(active_dataset_tag)
    mode = str(context.get("mode") or "Live")
    family = str(context.get("family") or "BTC15M")
    chips = [str(chip) for chip in context.get("chips", [])][:4]
    dataset_short = active_dataset_label_live if len(active_dataset_label_live) <= 58 else active_dataset_label_live[:55] + "..."
    dataset_status = "BTC15M Live" if "live" in active_dataset_tag.lower() else "BTC15M Research"
    range_label = str(equity_range_label or "ALL").upper()
    seed_label = str(seed_filter_label or "ALL").upper()

    positive_sum = float(completed_pnl[completed_pnl > 0].sum()) if not completed_pnl.empty else 0.0
    negative_sum = abs(float(completed_pnl[completed_pnl < 0].sum())) if not completed_pnl.empty else 0.0
    profit_factor = positive_sum / negative_sum if negative_sum > 0 else np.nan
    profit_factor_label = "NA" if pd.isna(profit_factor) else f"{profit_factor:.2f}x"
    expectancy = float(completed_pnl.mean()) if not completed_pnl.empty else np.nan

    def pill_href(label: str, param: str, value: str) -> str:
        active = " active" if label.upper() == value.upper() else ""
        return f"<a class='dark-ref-pill{active}' href='?{param}={html.escape(label)}' target='_self'>{html.escape(label)}</a>"

    range_pills = "".join(pill_href(option, "dash_range", range_label) for option in EQUITY_RANGE_OPTIONS)
    seed_pills = "".join(pill_href(option, "dash_seed", seed_label) for option in SEED_FILTER_OPTIONS)
    view_tabs = "".join(
        f"<a class='{'active' if option == st.session_state.active_view else ''}' href='?dash_view={html.escape(option)}' target='_self'>{html.escape(option)}</a>"
        for option in ["Overview", "Visualizer", "Research Lab", "BTC today map", "Loss diagnostics", "Strategy optimizer"]
    )
    chip_html = "".join(f"<span>{html.escape(chip)}</span>" for chip in chips)

    seed_trades = trades
    if seed_label != "ALL" and trades is not None and not trades.empty:
        pnl = trade_pnl_series(trades)
        if seed_label == "WIN":
            seed_trades = trades.loc[pnl > 0].copy()
        elif seed_label == "LOSS":
            seed_trades = trades.loc[pnl < 0].copy()
        elif seed_label == "FLAT":
            seed_trades = trades.loc[pnl == 0].copy()

    curve_values = displayed_curve["equity"] if not displayed_curve.empty and "equity" in displayed_curve.columns else pd.Series(dtype=float)
    drawdown_values = displayed_curve["drawdown"] if not displayed_curve.empty and "drawdown" in displayed_curve.columns else pd.Series(dtype=float)
    equity_svg = reference_equity_vine_svg(displayed_curve)
    drawdown_svg = reference_drawdown_roots_svg(displayed_curve)
    spores_html = outcome_spores_html(completed_pnl)
    depth_svg = build_orderbook_depth_svg(yes_bid, yes_ask, no_bid, no_ask, yes_spread)
    seed_html = reference_trade_seed_tape_html(seed_trades, max_rows=6, outcome_filter=seed_label)
    api_meter = 100 if accounting_status.get("class") == "verified" else 58 if accounting_status.get("class") == "partial" else 24
    lock_class = html.escape(str(lock_status.get("class") or "neutral"))
    pnl_class = "gain" if net_pnl_display > 0 else "loss" if net_pnl_display < 0 else "flat"
    state_class = html.escape(str(state_status).lower())
    diagnostics_rows = (
        f"<div class='dark-canvas-row'><span>API health</span><b>{html.escape(str(accounting_status.get('value') or 'NA'))}</b></div>"
        f"<div class='dark-canvas-row'><span>Data feed</span><b>{html.escape(feed_age_text)}</b></div>"
        f"<div class='dark-canvas-row'><span>Latency</span><b>{html.escape(reaction_text)}</b></div>"
        f"<div class='dark-canvas-row'><span>Score file</span><b>{html.escape(score_age_text)}</b></div>"
        f"<div class='dark-canvas-row'><span>Telemetry</span><b>{html.escape(telemetry_text)}</b></div>"
    )
    st.markdown(
        f"""
        <div class="dark-canvas">
          <div class="dark-canvas-brand">
            <div class="dark-ref-orb"><span>15M</span></div>
            <div><b>BTC15M</b><span>Living Analytics</span></div>
          </div>
          <div class="dark-canvas-field dark-canvas-dataset"><span>Dataset</span><b>{html.escape(dataset_short)}</b></div>
          <div class="dark-canvas-field dark-canvas-refresh-mode"><span>Auto refresh</span><b>{html.escape(refresh_mode_label)}</b></div>
          <a class="dark-canvas-refresh" href="?dash_action=refresh" target="_self">Refresh now</a>
          <div class="dark-canvas-score"><span>Score mode</span><b>{html.escape(str(mode))}</b><em>{html.escape(refresh_mode_label)}</em></div>
          <div class="dark-canvas-tabs">{view_tabs}</div>

          <div class="dark-canvas-status dark-canvas-status-dataset porcelain"><span>Dataset</span><b>{html.escape(active_dataset_label_live)}</b><em>Stats tag: {html.escape(active_dataset_tag)}</em></div>
          <div class="dark-canvas-status dark-canvas-status-lock {lock_class}"><span>{html.escape(str(lock_status.get('label') or 'Live Lock'))}</span><b>{html.escape(str(lock_status.get('value') or 'NA'))}</b><em>{html.escape(str(lock_status.get('note') or ''))}</em></div>
          <div class="dark-canvas-status dark-canvas-status-api {html.escape(str(accounting_status.get('class') or ''))}"><span>{html.escape(str(accounting_status.get('label') or 'Kalshi API'))}</span><b>{html.escape(str(accounting_status.get('value') or 'NA'))}</b><em>{html.escape(str(accounting_status.get('note') or ''))}</em></div>
          <div class="dark-canvas-status dark-canvas-status-market"><span>Market</span><b>{html.escape(compact_market_label(current_market_label))}</b><em>Refresh {html.escape(refresh_mode_label)} / score {html.escape(score_age_text)}</em></div>

          <div class="dark-canvas-pod dark-canvas-pnl {pnl_class}"><span>Net P&amp;L</span><b>{html.escape(format_signed_money(net_pnl_display))}</b><em>{html.escape(format_pct(net_pnl_pct))} return</em>{sparkline_svg(curve_values, "#9cff9f" if net_pnl_display >= 0 else "#ff5f73")}</div>
          <div class="dark-canvas-pod dark-canvas-dd loss"><span>Max Drawdown</span><b>{html.escape(format_drawdown_money(max_drawdown))}</b><em>underwater low</em>{sparkline_svg(drawdown_values, "#ff5f73", "rgba(255,95,115,0.15)")}</div>
          <div class="dark-canvas-pod dark-canvas-win"><span>Win Rate</span><b>{html.escape(format_pct(win_rate))}</b><em>{wins} W / {losses} L / {flats} flat</em>{living_ring_svg(win_rate, label=f"{win_rate:.0f}%")}</div>
          <div class="dark-canvas-pod dark-canvas-open"><span>Entries / Open</span><b>{entries_total} / {open_positions}</b><em>{open_positions} currently open</em>{living_ring_svg(100 if open_positions else 8, color="#79e7ff", label=str(open_positions))}</div>
          <div class="dark-canvas-pod dark-canvas-pulse {state_class}"><span>Feed Pulse</span><b>{html.escape(str(state_status))}</b><em>{html.escape(heartbeat_age_text)}</em>{living_microbars_svg(curve_values.diff().fillna(curve_values) if not curve_values.empty else [], "#f7c85f")}</div>

          <div class="dark-canvas-chart">
            <div class="dark-canvas-chart-head"><div><span>P&amp;L Command Center</span><b>Equity Vine</b><em>{html.escape(format_signed_money(net_pnl_display))} over {html.escape(range_label)}</em></div><div class="dark-ref-range">{range_pills}</div></div>
            <div class="dark-canvas-statline"><span>Net {html.escape(format_signed_money(net_pnl_display))}</span><span>Drawdown {html.escape(format_drawdown_money(max_drawdown))}</span><span>Latest {html.escape(latest_trade_label)}</span><span>Source {html.escape(str(accounting_status.get('source') or 'kalshi_api'))}</span></div>
            {equity_svg}
          </div>
          <div class="dark-canvas-roots"><div class="dark-canvas-title">Drawdown Roots <span>Max DD {html.escape(format_drawdown_money(max_drawdown))}</span></div>{drawdown_svg}</div>
          <div class="dark-canvas-spores"><div class="dark-canvas-title">Outcome Spores <span>Trades by outcome cluster</span></div>{spores_html}</div>

          <div class="dark-canvas-side dark-canvas-side-api {html.escape(str(accounting_status.get('class') or ''))}"><span>Kalshi API</span><b>{html.escape(str(accounting_status.get('value') or 'NA'))}</b><em>{html.escape(str(accounting_status.get('note') or ''))}</em><div class="dark-canvas-meter"><i style="width:{api_meter}%"></i></div></div>
          <div class="dark-canvas-side dark-canvas-side-lock {lock_class}"><span>Live Lock</span><b>{html.escape(str(lock_status.get('value') or 'NA'))}</b><em>{html.escape(str(lock_status.get('note') or ''))}</em><div class="ref-light-row"><span></span><span></span><span></span><span></span><span></span><span></span></div></div>
          <div class="dark-canvas-side dark-canvas-side-vitals"><span>P&amp;L Vitals</span><div class="dark-canvas-row"><span>Total return</span><b>{html.escape(format_pct(net_pnl_pct))}</b></div><div class="dark-canvas-row"><span>Win rate</span><b>{html.escape(format_pct(win_rate))}</b></div><div class="dark-canvas-row"><span>Profit factor</span><b>{html.escape(profit_factor_label)}</b></div><div class="dark-canvas-row"><span>Expectancy</span><b>{html.escape(format_signed_money(expectancy, always_sign=True))}</b></div>{sparkline_svg(completed_pnl.cumsum() if not completed_pnl.empty else [], "#9cff9f")}</div>
          <div class="dark-canvas-side dark-canvas-side-market"><span>Market Pulse 15M</span><b>{html.escape(compact_market_label(current_market_label))}</b><div class="dark-canvas-row"><span>Close</span><b>{html.escape(watch_close_label)}</b></div><div class="dark-canvas-row"><span>YES</span><b>{html.escape(format_cents(yes_bid))} / {html.escape(format_cents(yes_ask))}</b></div><div class="dark-canvas-row"><span>NO</span><b>{html.escape(format_cents(no_bid))} / {html.escape(format_cents(no_ask))}</b></div><em>{html.escape(market_bias)}</em></div>
          <div class="dark-canvas-side dark-canvas-side-depth"><span>Orderbook Depth</span>{depth_svg}</div>

          <div class="dark-canvas-seeds"><div class="dark-canvas-seed-title">Trade Seeds <span>{seed_pills}</span></div>{seed_html}</div>
          <div class="dark-canvas-diagnostics"><div class="dark-canvas-title">Diagnostics <span>Live</span></div>{diagnostics_rows}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return

    st.markdown(
        f"""
        <div class="dark-ref-shell">
          <div class="dark-ref-top">
            <div class="dark-ref-brand">
              <div class="dark-ref-orb"><span>15M</span></div>
              <div><b>BTC15M</b><span>Living Analytics</span></div>
            </div>
            <div class="dark-ref-field dark-ref-dataset">
              <span>Dataset</span><b>{html.escape(dataset_short)}</b>
            </div>
            <div class="dark-ref-field">
              <span>Auto refresh</span><b>{html.escape(refresh_mode_label)}</b>
            </div>
            <a class="dark-ref-refresh" href="?dash_action=refresh" target="_self">Refresh now</a>
            <div class="dark-ref-score"><span>Score mode</span><b>{html.escape(str(mode))}</b><em>{html.escape(refresh_mode_label)}</em></div>
          </div>
          <div class="dark-ref-tabs">{view_tabs}</div>
          <div class="dark-ref-status-grid">
            <div class="dark-ref-status-card porcelain">
              <span>Dataset</span>
              <b>{html.escape(active_dataset_label_live)}</b>
              <em>Stats tag: {html.escape(active_dataset_tag)}</em>
            </div>
            <div class="dark-ref-status-card {html.escape(str(lock_status.get('class') or ''))}">
              <span>{html.escape(str(lock_status.get('label') or 'Live Lock'))}</span>
              <b>{html.escape(str(lock_status.get('value') or 'NA'))}</b>
              <em>{html.escape(str(lock_status.get('note') or ''))}</em>
            </div>
            <div class="dark-ref-status-card {html.escape(str(accounting_status.get('class') or ''))}">
              <span>{html.escape(str(accounting_status.get('label') or 'Kalshi API'))}</span>
              <b>{html.escape(str(accounting_status.get('value') or 'NA'))}</b>
              <em>{html.escape(str(accounting_status.get('note') or ''))}</em>
            </div>
            <div class="dark-ref-status-card">
              <span>Market</span>
              <b>{html.escape(compact_market_label(current_market_label))}</b>
              <em>Refresh {html.escape(refresh_mode_label)} / score {html.escape(score_age_text)}</em>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, center_col, right_col = st.columns([0.19, 0.56, 0.25], gap="large")
    with left_col:
        render_living_vital_rail(
            net_pnl_display=net_pnl_display,
            net_pnl_pct=net_pnl_pct,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            wins=wins,
            losses=losses,
            flats=flats,
            entries_total=entries_total,
            open_positions=open_positions,
            latest_trade_label=latest_trade_label,
            latest_trade_note=latest_trade_note,
            latest_trade_class=latest_trade_class,
            state_status=state_status,
            heartbeat_age_text=heartbeat_age_text,
            curve=displayed_curve,
        )
    with center_col:
        st.markdown(
            f"""
            <div class="living-chart-head dark-ref-command">
              <div class="living-chart-kicker">P&amp;L Command Center</div>
              <div class="living-chart-title">Equity Vine</div>
              <div class="living-chart-sub">{html.escape(format_signed_money(net_pnl_display))} over {html.escape(range_label)}</div>
              <div class="living-statline">
                <span>Net {html.escape(format_signed_money(net_pnl_display))}</span>
                <span>Drawdown {html.escape(format_drawdown_money(max_drawdown))}</span>
                <span>Latest {html.escape(latest_trade_label)}</span>
                <span>Source {html.escape(str(accounting_status.get('source') or 'kalshi_api'))}</span>
              </div>
              <div class="dark-ref-range">{range_pills}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            build_living_equity_figure(displayed_curve, active_dataset_tag),
            width="stretch",
            key=f"dark-reference-equity-{active_dataset_tag}-{range_label}",
        )
        st.markdown(
            f"""
            <div class="living-trade-title dark-ref-trade-title">
              <span>Trade Seeds - latest executions</span>
              <span class="dark-ref-seed-filter">{seed_pills}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_recent_trade_tape(seed_trades, max_rows=8)
    with right_col:
        render_living_inspector(
            accounting_status=accounting_status,
            lock_status=lock_status,
            current_market_label=current_market_label,
            watch_close_label=watch_close_label,
            yes_bid=yes_bid,
            yes_ask=yes_ask,
            no_bid=no_bid,
            no_ask=no_ask,
            yes_spread=yes_spread,
            market_bias=market_bias,
            hb=hb,
            feed_age_text=feed_age_text,
            reaction_text=reaction_text,
            heartbeat_age_text=heartbeat_age_text,
            score_age_text=score_age_text,
            telemetry_text=telemetry_text,
            completed_pnl=completed_pnl,
            win_rate=win_rate,
            net_pnl_pct=net_pnl_pct,
        )


def build_living_equity_figure(displayed_curve: pd.DataFrame, active_dataset_tag: str) -> go.Figure:
    fig = go.Figure()
    if displayed_curve.empty:
        fig.update_layout(
            height=500,
            margin=dict(l=18, r=18, t=16, b=32),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig

    curve = displayed_curve.copy()
    curve["trade_pnl"] = pd.to_numeric(curve.get("trade_pnl", 0.0), errors="coerce").fillna(0.0)
    curve["equity"] = pd.to_numeric(curve["equity"], errors="coerce").fillna(0.0)
    curve["drawdown"] = pd.to_numeric(curve.get("drawdown", 0.0), errors="coerce").fillna(0.0)
    hover_rows = []
    for _, row in curve.iterrows():
        side = display_text(str(row.get("side", "")).upper(), "NA")
        market = compact_market_label(row.get("market", "NA"))
        hover_rows.append(
            [
                format_signed_money(row.get("equity")),
                format_signed_money(row.get("trade_pnl"), always_sign=True),
                format_drawdown_money(row.get("drawdown")),
                market,
                side,
                format_cents(row.get("entry_fill_cents_used")),
                format_cents(row.get("exit_fill_cents_used")),
            ]
        )

    marker_colors = np.where(
        curve["trade_pnl"] > 0,
        "#9cff9f",
        np.where(curve["trade_pnl"] < 0, "#ff5f73", "#a99bb9"),
    )
    pnl_abs = curve["trade_pnl"].abs().to_numpy(dtype=float)
    marker_sizes = np.clip(10 + pnl_abs * 22.0, 10, 24)

    if len(curve) > 2:
        x_vals = curve["ts"]
        phase = np.linspace(0, np.pi * 2, len(curve))
        equity_min = float(curve["equity"].min())
        equity_max = float(curve["equity"].max())
        span = max(abs(equity_max - equity_min), abs(float(curve["drawdown"].min())), 0.25)
        contour_base = np.linspace(equity_min - span * 0.34, equity_max + span * 0.24, 11)
        for idx, base in enumerate(contour_base):
            contour = base + np.sin(phase + idx * 0.62) * span * (0.035 + idx * 0.006)
            fig.add_trace(
                go.Scatter(
                    x=x_vals,
                    y=contour,
                    mode="lines",
                    line=dict(
                        color=f"rgba({121 if idx % 2 else 247},{231 if idx % 2 else 200},{255 if idx % 2 else 95},0.16)",
                        width=1.0,
                        shape="spline",
                        smoothing=1.0,
                    ),
                    hoverinfo="skip",
                    showlegend=False,
                    name="Contour field",
                )
            )

    fig.add_trace(
        go.Scatter(
            x=curve["ts"],
            y=curve["equity"],
            mode="lines",
            line=dict(color="rgba(99,242,177,0.08)", width=0, shape="spline", smoothing=0.65),
            fill="tozeroy",
            fillcolor="rgba(99,242,177,0.13)",
            hoverinfo="skip",
            showlegend=False,
            name="Return envelope",
        )
    )
    loss_roots = curve[curve["trade_pnl"] < 0].tail(28)
    if not loss_roots.empty:
        root_x: list[Any] = []
        root_y: list[float | None] = []
        for idx, row in loss_roots.iterrows():
            equity_value = float(row.get("equity", 0.0) or 0.0)
            drawdown_value = float(row.get("drawdown", 0.0) or 0.0)
            root_x.extend([row.get("ts"), row.get("ts"), None])
            root_y.extend([equity_value, min(drawdown_value, equity_value) * 1.02, None])
        fig.add_trace(
            go.Scatter(
                x=root_x,
                y=root_y,
                mode="lines",
                line=dict(color="rgba(255,95,115,0.26)", width=1.3),
                hoverinfo="skip",
                showlegend=False,
                name="Loss roots",
            )
        )

    for width, opacity in ((22, 0.06), (12, 0.13), (5, 0.38)):
        fig.add_trace(
            go.Scatter(
                x=curve["ts"],
                y=curve["drawdown"],
                mode="lines",
                line=dict(color=f"rgba(255,95,115,{opacity})", width=width, shape="spline", smoothing=0.7),
                hoverinfo="skip",
                showlegend=False,
                name="Root glow",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=curve["ts"],
            y=curve["drawdown"],
            mode="lines",
            line=dict(color="rgba(255,95,115,0.68)", width=2.6, shape="spline", smoothing=0.7),
            fill="tozeroy",
            fillcolor="rgba(217,76,255,0.24)",
            hovertemplate="Drawdown %{customdata}<extra></extra>",
            customdata=[format_drawdown_money(v) for v in curve["drawdown"]],
            name="Root stress",
        )
    )
    for width, opacity in ((40, 0.06), (26, 0.12), (15, 0.22), (7, 0.42), (4, 0.82)):
        fig.add_trace(
            go.Scatter(
                x=curve["ts"],
                y=curve["equity"],
                mode="lines",
                line=dict(color=f"rgba(156,255,159,{opacity})", width=width, shape="spline", smoothing=0.65),
                hoverinfo="skip",
                showlegend=False,
                name="Equity glow",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=curve["ts"],
            y=curve["equity"],
            mode="lines+markers",
            line=dict(color="#f7e36f", width=3.4, shape="spline", smoothing=0.65),
            marker=dict(
                size=marker_sizes,
                color=marker_colors,
                opacity=0.92,
                line=dict(color="rgba(247,241,232,0.82)", width=1.2),
            ),
            customdata=hover_rows,
            hovertemplate=(
                "Equity %{customdata[0]}<br>"
                "Trade %{customdata[1]}<br>"
                "Drawdown %{customdata[2]}<br>"
                "%{customdata[4]} %{customdata[5]} to %{customdata[6]}<br>"
                "%{customdata[3]}<extra></extra>"
            ),
            name="Equity vine",
        )
    )
    if len(curve):
        highlight = curve.reindex(curve["trade_pnl"].abs().sort_values(ascending=False).head(5).index)
        for _, row in highlight.iterrows():
            if pd.isna(row.get("ts")):
                continue
            pnl_value = float(row.get("trade_pnl", 0.0) or 0.0)
            label_color = "#9cff9f" if pnl_value > 0 else "#ff5f73" if pnl_value < 0 else "#d9cde7"
            fig.add_annotation(
                x=row.get("ts"),
                y=row.get("equity"),
                text=format_signed_money(pnl_value, always_sign=True),
                showarrow=True,
                arrowhead=2,
                arrowsize=0.7,
                arrowwidth=1,
                arrowcolor="rgba(247,241,232,0.54)",
                ax=0,
                ay=-34 if pnl_value >= 0 else 34,
                bgcolor="rgba(7,6,12,0.78)",
                bordercolor=label_color,
                borderwidth=1,
                borderpad=4,
                font=dict(color=label_color, size=10),
            )
    fig.add_hline(y=0, line_width=1, line_color="rgba(247,241,232,0.18)")

    equity_abs_max = float(curve["equity"].abs().max()) if len(curve) else 0.0
    drawdown_floor = float(curve["drawdown"].min()) if len(curve) else 0.0
    y_min = min(drawdown_floor * 1.25, float(curve["equity"].min()) * 1.12, -0.05)
    y_max = max(float(curve["equity"].max()) * 1.12, 0.05)
    tickformat = ",.3f" if equity_abs_max < 0.1 else ",.2f"
    fig.update_layout(
        height=560,
        margin=dict(l=18, r=16, t=8, b=38),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="rgba(12,9,18,0.95)",
            bordercolor="rgba(121,231,255,0.52)",
            font=dict(color="#f7f1e8", size=12),
        ),
        showlegend=False,
        uirevision=f"living-equity-{active_dataset_tag}",
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(121,231,255,0.08)",
        zeroline=False,
        showline=False,
        tickfont=dict(color="#a99bb9", size=11),
        fixedrange=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(247,241,232,0.07)",
        zeroline=False,
        showline=False,
        tickprefix="$",
        tickformat=tickformat,
        tickfont=dict(color="#a99bb9", size=11),
        range=[y_min, y_max],
        fixedrange=True,
    )
    return fig


def sorted_recent_trades(df: pd.DataFrame, max_rows: int = 8) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    work = df.copy()
    if "exit_ts" not in work.columns:
        work["exit_ts"] = pd.NA
    if "settlement_ts" not in work.columns:
        work["settlement_ts"] = pd.NA
    if "entry_ts" not in work.columns:
        work["entry_ts"] = pd.NA
    exit_ts = pd.to_datetime(work["exit_ts"], errors="coerce", utc=True)
    settlement_ts = pd.to_datetime(work["settlement_ts"], errors="coerce", utc=True)
    entry_ts = pd.to_datetime(work["entry_ts"], errors="coerce", utc=True)
    work["_sort_ts"] = exit_ts.fillna(settlement_ts).fillna(entry_ts)
    return work.sort_values("_sort_ts", ascending=False).head(max_rows)


def render_recent_trade_tape(df: pd.DataFrame, max_rows: int = 8) -> None:
    recent = sorted_recent_trades(df, max_rows=max_rows)
    if recent.empty:
        st.markdown(
            "<div class='living-trade-tape empty'><div class='seed-empty'>Waiting for scored trades</div></div>",
            unsafe_allow_html=True,
        )
        return
    pnl_values = trade_pnl_series(recent)
    tape_wins = int((pnl_values > 0).sum()) if not pnl_values.empty else 0
    tape_losses = int((pnl_values < 0).sum()) if not pnl_values.empty else 0
    tape_flats = int((pnl_values == 0).sum()) if not pnl_values.empty else 0
    tape_header = (
        "<div style='display:flex;align-items:center;gap:.7rem;min-width:148px;padding:.2rem .2rem .2rem 0;color:#17121d'>"
        "<div style='font-weight:900;font-size:.9rem;line-height:1.08'>Outcome<br>cluster</div>"
        f"<div style='font-size:.72rem;font-weight:850;color:#0f766e'>WIN {tape_wins}</div>"
        f"<div style='font-size:.72rem;font-weight:850;color:#dc2626'>LOSS {tape_losses}</div>"
        f"<div style='font-size:.72rem;font-weight:850;color:#6b5f7a'>FLAT {tape_flats}</div>"
        "</div>"
    )
    rows: list[str] = []
    for idx, (_, row) in enumerate(recent.iterrows()):
        pnl_value = pnl_values.iloc[idx] if idx < len(pnl_values) else np.nan
        if pd.notna(pnl_value):
            state = "win" if pnl_value > 0 else "loss" if pnl_value < 0 else "flat"
        else:
            state = str(row.get("display_outcome", "open") or "open").lower()
        cls = "seed-win" if state == "win" else "seed-loss" if state == "loss" else "seed-flat" if state == "flat" else "seed-open"
        side = str(row.get("side", "") or "").upper() or "NA"
        qty = row.get("qty")
        try:
            qty_text = str(int(float(qty))) if pd.notna(qty) else "NA"
        except Exception:
            qty_text = "NA"
        market_raw = str(row.get("market", "NA") or "NA")
        market = html.escape(compact_market_label(market_raw))
        time_label = html.escape(str(row.get("ma_time", "NA") or "NA"))
        entry_label = html.escape(format_cents(row.get("entry_fill_cents_used")))
        exit_label = html.escape(format_cents(row.get("exit_fill_cents_used")))
        pnl_label = html.escape(format_signed_money(pnl_value, always_sign=True))
        title = html.escape(
            f"{market_raw} | {side} qty {qty_text} | entry {format_cents(row.get('entry_fill_cents_used'))} | "
            f"exit {format_cents(row.get('exit_fill_cents_used'))} | PnL {format_signed_money(pnl_value, always_sign=True)}"
        )
        rows.append(
            f"<div class=\"trade-seed {cls}\" title=\"{title}\">"
            f"<div class=\"seed-glow\"></div><div class=\"seed-time\">{time_label}</div>"
            f"<div class=\"seed-market\">{market}</div>"
            f"<div class=\"seed-side\">{html.escape(side)} <span>qty {html.escape(qty_text)}</span></div>"
            f"<div class=\"seed-price\">{entry_label} &rarr; {exit_label}</div>"
            f"<div class=\"seed-pnl\">{pnl_label}</div></div>"
        )
    st.markdown(
        f"<div class=\"living-trade-tape\"><div class=\"seed-rail\"></div>{tape_header}{''.join(rows)}</div>",
        unsafe_allow_html=True,
    )


def render_living_vital_rail(
    *,
    net_pnl_display: float,
    net_pnl_pct: float,
    max_drawdown: float,
    win_rate: float,
    wins: int,
    losses: int,
    flats: int,
    entries_total: int,
    open_positions: int,
    latest_trade_label: str,
    latest_trade_note: str,
    latest_trade_class: str,
    state_status: str,
    heartbeat_age_text: str,
    curve: pd.DataFrame,
) -> None:
    pnl_class = "positive" if net_pnl_display > 0 else "negative" if net_pnl_display < 0 else "neutral"
    dd_class = "negative" if max_drawdown < 0 else "neutral"
    win_class = "positive" if win_rate >= 50 and (wins + losses) else "neutral"
    open_class = "positive" if open_positions else "neutral"
    curve_values = curve["equity"] if not curve.empty and "equity" in curve.columns else pd.Series(dtype=float)
    drawdown_values = curve["drawdown"] if not curve.empty and "drawdown" in curve.columns else pd.Series(dtype=float)
    pods = [
        (
            "Net P&L",
            format_signed_money(net_pnl_display),
            f"{format_pct(net_pnl_pct)} return",
            pnl_class,
            sparkline_svg(curve_values, "#9cff9f" if net_pnl_display >= 0 else "#ff5f73"),
        ),
        (
            "Max Drawdown",
            format_drawdown_money(max_drawdown),
            "underwater low",
            dd_class,
            sparkline_svg(drawdown_values, "#ff5f73", "rgba(255,95,115,0.14)"),
        ),
        (
            "Win Rate",
            format_pct(win_rate),
            f"{wins} W / {losses} L / {flats} flat",
            win_class,
            living_ring_svg(win_rate, color="#9cff9f" if win_rate >= 50 and (wins + losses) else "#ffbf4d"),
        ),
        (
            "Entries / Open",
            f"{entries_total} / {open_positions}",
            f"{open_positions} currently open",
            open_class,
            living_ring_svg(min(open_positions * 18.0, 100.0), color="#79e7ff", label=str(open_positions)),
        ),
        (
            "Latest Trade",
            latest_trade_label,
            latest_trade_note,
            latest_trade_class,
            living_microbars_svg(curve_values.diff().fillna(curve_values) if not curve_values.empty else [], "#f7c85f"),
        ),
        (
            "Feed Pulse",
            state_status,
            heartbeat_age_text,
            "positive" if str(state_status).lower() == "live" else "warning" if str(state_status).lower() == "stale" else "negative",
            living_ring_svg(100.0 if str(state_status).lower() == "live" else 54.0 if str(state_status).lower() == "stale" else 18.0, color="#79e7ff"),
        ),
    ]
    pod_html = []
    for label, value, note, cls, spark in pods:
        pod_html.append(
            f"<div class=\"living-vital-pod {html.escape(cls)}\">"
            f"<div class=\"living-pod-label\">{html.escape(label)}</div>"
            f"<div class=\"living-pod-value\">{html.escape(str(value))}</div>"
            f"<div class=\"living-pod-note\">{html.escape(str(note))}</div>{spark}</div>"
        )
    st.markdown(f"<div class='living-vitals-rail'>{''.join(pod_html)}</div>", unsafe_allow_html=True)


def render_living_inspector(
    *,
    accounting_status: dict[str, Any],
    lock_status: dict[str, str],
    current_market_label: str,
    watch_close_label: str,
    yes_bid: Any,
    yes_ask: Any,
    no_bid: Any,
    no_ask: Any,
    yes_spread: Any,
    market_bias: str,
    hb: dict[str, Any],
    feed_age_text: str,
    reaction_text: str,
    heartbeat_age_text: str,
    score_age_text: str,
    telemetry_text: str,
    completed_pnl: pd.Series,
    win_rate: float,
    net_pnl_pct: float,
) -> None:
    positive_sum = float(completed_pnl[completed_pnl > 0].sum()) if not completed_pnl.empty else 0.0
    negative_sum = abs(float(completed_pnl[completed_pnl < 0].sum())) if not completed_pnl.empty else 0.0
    profit_factor = positive_sum / negative_sum if negative_sum > 0 else np.nan
    expectancy = float(completed_pnl.mean()) if not completed_pnl.empty else np.nan
    pnl_spark = sparkline_svg(completed_pnl.cumsum() if not completed_pnl.empty else [], "#9cff9f")
    outcome_panel = outcome_spores_html(completed_pnl)
    depth_svg = build_orderbook_depth_svg(yes_bid, yes_ask, no_bid, no_ask, yes_spread)
    api_meter = 100 if accounting_status["class"] == "verified" else 58 if accounting_status["class"] == "partial" else 24
    book_meter = 100 if bool(hb.get("book_ready")) else 30
    inspector_html = f"""
    <div class="living-inspector">
      <div class="inspector-module accounting {html.escape(str(accounting_status['class']))}">
        <div class="module-label">{html.escape(str(accounting_status['label']))}</div>
        <div class="module-value">{html.escape(str(accounting_status['value']))}</div>
        <div class="module-note">{html.escape(str(accounting_status['note']))}</div>
        <div class="status-meter"><span style="width:{api_meter}%"></span></div>
      </div>
      <div class="inspector-module {html.escape(lock_status['class'])}">
        <div class="module-label">{html.escape(lock_status['label'])}</div>
        <div class="module-value">{html.escape(lock_status['value'])}</div>
        <div class="module-note">{html.escape(lock_status['note'])}</div>
      </div>
      <div class="inspector-module">
        <div class="module-label">P&L Vitals</div>
        <div class="inspector-row"><span>Total return</span><strong>{html.escape(format_pct(net_pnl_pct))}</strong></div>
        <div class="inspector-row"><span>Win rate</span><strong>{html.escape(format_pct(win_rate))}</strong></div>
        <div class="inspector-row"><span>Profit factor</span><strong>{'NA' if pd.isna(profit_factor) else f'{profit_factor:.2f}x'}</strong></div>
        <div class="inspector-row"><span>Expectancy</span><strong>{html.escape(format_signed_money(expectancy, always_sign=True))}</strong></div>
        {pnl_spark}
      </div>
      <div class="inspector-module">
        <div class="module-label">Outcome Spores</div>
        {outcome_panel}
      </div>
      <div class="inspector-module">
        <div class="module-label">Market Pulse 15M</div>
        <div class="module-value small">{html.escape(compact_market_label(current_market_label))}</div>
        <div class="inspector-row"><span>Close</span><strong>{html.escape(watch_close_label)}</strong></div>
        <div class="inspector-row"><span>YES</span><strong>{html.escape(format_cents(yes_bid))} / {html.escape(format_cents(yes_ask))}</strong></div>
        <div class="inspector-row"><span>NO</span><strong>{html.escape(format_cents(no_bid))} / {html.escape(format_cents(no_ask))}</strong></div>
        <div class="inspector-row"><span>Bias</span><strong>{html.escape(market_bias)}</strong></div>
      </div>
      <div class="inspector-module">
        <div class="module-label">Orderbook Pulse</div>
        <div class="inspector-row"><span>Spread</span><strong>{html.escape(format_cents(yes_spread))}</strong></div>
        <div class="inspector-row"><span>Book ready</span><strong>{html.escape(display_text(hb.get('book_ready', 'NA')))}</strong></div>
        <div class="inspector-row"><span>Pending</span><strong>{html.escape(display_text(hb.get('pending', 'NA')))}</strong></div>
        <div class="inspector-row"><span>Trust</span><strong>{html.escape(display_text(hb.get('trust', 'NA')))}</strong></div>
        {depth_svg}
        <div class="status-meter"><span style="width:{book_meter}%"></span></div>
      </div>
      <div class="inspector-module">
        <div class="module-label">Freshness</div>
        <div class="inspector-row"><span>Heartbeat</span><strong>{html.escape(heartbeat_age_text)}</strong></div>
        <div class="inspector-row"><span>Feed age</span><strong>{html.escape(feed_age_text)}</strong></div>
        <div class="inspector-row"><span>Reaction</span><strong>{html.escape(reaction_text)}</strong></div>
        <div class="inspector-row"><span>Score file</span><strong>{html.escape(score_age_text)}</strong></div>
        <div class="inspector-row"><span>Telemetry</span><strong>{html.escape(telemetry_text)}</strong></div>
      </div>
    </div>
    """
    st.markdown(inspector_html, unsafe_allow_html=True)


def make_price_series(lines: list[str]) -> pd.DataFrame:
    rows = []
    for raw in lines:
        m = HEARTBEAT_RE.match(raw.strip())
        if not m:
            continue
        ts = parse_ts(m.group("ts"))
        if not ts:
            continue
        rows.append({
            "ts": ts,
            "market": m.group("watch"),
            "yes_bid": maybe_num(m.group("yes_bid")),
            "yes_ask": maybe_num(m.group("yes_ask")),
            "no_bid": maybe_num(m.group("no_bid")),
            "no_ask": maybe_num(m.group("no_ask")),
        })
    if not rows:
        return pd.DataFrame(columns=["ts", "market", "yes_bid", "yes_ask", "no_bid", "no_ask"])
    out = pd.DataFrame(rows).drop_duplicates(subset=["ts", "market"], keep="last").sort_values("ts")
    for col in ["yes_bid", "yes_ask", "no_bid", "no_ask"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


@st.cache_data(ttl=60, show_spinner=False)
def build_trade_diagnostic_df(price_df: pd.DataFrame, trades_df: pd.DataFrame, lookback_points: int = 8) -> pd.DataFrame:
    cols = [
        "market", "side", "entry_ts", "gross_pnl_dollars", "display_outcome", "loss", "win",
        "entry_ask", "entry_bid", "entry_spread", "hour",
        "pre_std", "pre_range", "pre_mean_abs_move", "pre_max_abs_move", "pre_net_move", "pre_chop_ratio", "obs",
    ]
    if price_df.empty or trades_df.empty:
        return pd.DataFrame(columns=cols)

    prices = price_df.copy()
    prices["market"] = prices["market"].astype(str).str.strip().str.upper()
    prices["ts"] = pd.to_datetime(prices["ts"], errors="coerce")
    for col in ["yes_bid", "yes_ask", "no_bid", "no_ask"]:
        if col in prices.columns:
            prices[col] = pd.to_numeric(prices[col], errors="coerce")
    prices = prices.dropna(subset=["market", "ts"]).sort_values(["market", "ts"]).reset_index(drop=True)
    if prices.empty:
        return pd.DataFrame(columns=cols)

    trades = trades_df.copy()
    trades["market"] = trades["market"].astype(str).str.strip().str.upper()
    trades["side"] = trades["side"].astype(str).str.strip().str.lower()
    trades["entry_ts"] = pd.to_datetime(trades["entry_ts"], errors="coerce")
    trades["gross_pnl_dollars"] = pd.to_numeric(trades["gross_pnl_dollars"], errors="coerce")
    if "display_outcome" not in trades.columns:
        trades = normalize_trades(trades)
    trades = trades.dropna(subset=["market", "entry_ts"]).sort_values("entry_ts").reset_index(drop=True)
    if trades.empty:
        return pd.DataFrame(columns=cols)

    grouped = {market: grp.copy() for market, grp in prices.groupby("market", sort=False)}
    rows: list[dict[str, Any]] = []
    for _, trade in trades.iterrows():
        market = str(trade["market"])
        side = str(trade["side"])
        grp = grouped.get(market)
        if grp is None or grp.empty:
            continue
        hist = grp[grp["ts"] <= trade["entry_ts"]].sort_values("ts").tail(lookback_points).copy()
        if hist.empty:
            continue

        ask_col = "yes_ask" if side == "yes" else "no_ask"
        bid_col = "yes_bid" if side == "yes" else "no_bid"
        hist["side_ask"] = pd.to_numeric(hist[ask_col], errors="coerce")
        hist["side_bid"] = pd.to_numeric(hist[bid_col], errors="coerce")
        hist = hist.dropna(subset=["side_ask"])
        if len(hist) < 3:
            continue

        vals = hist["side_ask"].to_numpy(dtype=float)
        diffs = np.diff(vals)
        abs_diffs = np.abs(diffs)
        last = hist.iloc[-1]
        entry_bid = float(last["side_bid"]) if pd.notna(last["side_bid"]) else np.nan
        entry_ask = float(last["side_ask"]) if pd.notna(last["side_ask"]) else np.nan
        entry_spread = float(entry_ask - entry_bid) if pd.notna(last["side_bid"]) and pd.notna(last["side_ask"]) else np.nan

        rows.append(
            {
                "market": market,
                "side": side,
                "entry_ts": trade["entry_ts"],
                "gross_pnl_dollars": float(trade["gross_pnl_dollars"]) if pd.notna(trade["gross_pnl_dollars"]) else np.nan,
                "display_outcome": str(trade.get("display_outcome", trade.get("outcome", ""))),
                "loss": bool(pd.notna(trade["gross_pnl_dollars"]) and trade["gross_pnl_dollars"] < 0),
                "win": bool(pd.notna(trade["gross_pnl_dollars"]) and trade["gross_pnl_dollars"] > 0),
                "entry_ask": entry_ask,
                "entry_bid": entry_bid,
                "entry_spread": entry_spread,
                "hour": int(pd.Timestamp(trade["entry_ts"]).hour),
                "pre_std": float(np.std(vals, ddof=0)),
                "pre_range": float(np.max(vals) - np.min(vals)),
                "pre_mean_abs_move": float(np.mean(abs_diffs)) if len(abs_diffs) else 0.0,
                "pre_max_abs_move": float(np.max(abs_diffs)) if len(abs_diffs) else 0.0,
                "pre_net_move": float(vals[-1] - vals[0]),
                "pre_chop_ratio": float(np.sum(abs_diffs) / max(abs(vals[-1] - vals[0]), 1.0)) if len(abs_diffs) else 0.0,
                "obs": int(len(hist)),
            }
        )

    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows).sort_values("entry_ts").reset_index(drop=True)


def build_loss_filter_candidates(diag: pd.DataFrame, metric_options: dict[str, str] | None = None) -> pd.DataFrame:
    if metric_options is None:
        metric_options = {
            "Entry spread": "entry_spread",
            "Pre-entry std dev": "pre_std",
            "Pre-entry range": "pre_range",
            "Average move before entry": "pre_mean_abs_move",
            "Largest move before entry": "pre_max_abs_move",
            "Net move before entry": "pre_net_move",
            "Chop ratio": "pre_chop_ratio",
        }
    rows: list[dict[str, Any]] = []
    if diag.empty:
        return pd.DataFrame()

    baseline_loss_rate = float(diag["loss"].mean() * 100.0)
    baseline_avg_pnl = float(pd.to_numeric(diag["gross_pnl_dollars"], errors="coerce").mean())

    for label, col in metric_options.items():
        values = pd.to_numeric(diag[col], errors="coerce")
        usable = diag[values.notna()].copy()
        if len(usable) < 6:
            continue
        usable[col] = pd.to_numeric(usable[col], errors="coerce")
        for percentile in (20, 35, 50):
            low_cut = float(usable[col].quantile(percentile / 100.0))
            high_cut = float(usable[col].quantile(1 - percentile / 100.0))
            for keep_rule, mask, cutoff in [
                ("Keep lowest", usable[col] <= low_cut, low_cut),
                ("Keep highest", usable[col] >= high_cut, high_cut),
            ]:
                sample = usable[mask].copy()
                if len(sample) < max(4, int(len(diag) * 0.12)):
                    continue
                loss_rate = float(sample["loss"].mean() * 100.0)
                avg_pnl = float(pd.to_numeric(sample["gross_pnl_dollars"], errors="coerce").mean())
                total_pnl = float(pd.to_numeric(sample["gross_pnl_dollars"], errors="coerce").sum())
                rows.append(
                    {
                        "Metric": label,
                        "Keep rule": f"{keep_rule} {percentile}%",
                        "Cutoff": cutoff,
                        "Trades kept": int(len(sample)),
                        "Keep rate %": float(len(sample) / max(len(diag), 1) * 100.0),
                        "Loss rate %": loss_rate,
                        "Loss rate delta %": loss_rate - baseline_loss_rate,
                        "Avg P and L / trade": avg_pnl,
                        "Avg P and L delta": avg_pnl - baseline_avg_pnl,
                        "Total P and L": total_pnl,
                    }
                )

    if not rows:
        return pd.DataFrame()

    out = pd.DataFrame(rows)
    return out.sort_values(
        ["Loss rate %", "Avg P and L / trade", "Trades kept"],
        ascending=[True, False, False],
    ).reset_index(drop=True)


def build_loss_strategy_recommendations(candidates: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if candidates.empty:
        return pd.DataFrame(), pd.DataFrame()

    ranked = candidates.copy()
    ranked["loss_improvement"] = -pd.to_numeric(ranked["Loss rate delta %"], errors="coerce")
    ranked["pnl_improvement"] = pd.to_numeric(ranked["Avg P and L delta"], errors="coerce")
    ranked["keep_rate"] = pd.to_numeric(ranked["Keep rate %"], errors="coerce")
    ranked["recommendation_score"] = (
        ranked["loss_improvement"].fillna(0.0) * 1.4
        + ranked["pnl_improvement"].fillna(0.0) * 8.0
        + ranked["keep_rate"].fillna(0.0) * 0.03
    )

    good = ranked[
        (ranked["loss_improvement"] > 0)
        & (ranked["pnl_improvement"] >= 0)
    ].sort_values(
        ["recommendation_score", "loss_improvement", "pnl_improvement", "Trades kept"],
        ascending=[False, False, False, False],
    )
    good = good.drop_duplicates(subset=["Metric"], keep="first").head(3).reset_index(drop=True)

    bad = ranked[
        (pd.to_numeric(ranked["Loss rate delta %"], errors="coerce") > 0)
        & (pd.to_numeric(ranked["Avg P and L delta"], errors="coerce") <= 0)
    ].sort_values(
        ["Loss rate delta %", "Avg P and L delta", "Trades kept"],
        ascending=[False, True, False],
    )
    bad = bad.drop_duplicates(subset=["Metric"], keep="first").head(3).reset_index(drop=True)
    return good, bad


def build_metric_bucket_summary(diag: pd.DataFrame, metric_col: str, bins: int = 5) -> pd.DataFrame:
    values = pd.to_numeric(diag[metric_col], errors="coerce")
    usable = diag[values.notna()].copy()
    if usable.empty:
        return pd.DataFrame()

    usable[metric_col] = pd.to_numeric(usable[metric_col], errors="coerce")
    unique_values = usable[metric_col].nunique(dropna=True)
    bucket_count = int(max(2, min(bins, unique_values)))
    if bucket_count < 2:
        return pd.DataFrame()

    try:
        usable["_bucket"] = pd.qcut(usable[metric_col], q=bucket_count, duplicates="drop")
    except ValueError:
        return pd.DataFrame()

    if usable["_bucket"].nunique(dropna=True) < 2:
        return pd.DataFrame()

    summary = (
        usable.groupby("_bucket", observed=True)
        .agg(
            trades=("market", "size"),
            losses=("loss", "sum"),
            avg_pnl=("gross_pnl_dollars", "mean"),
            total_pnl=("gross_pnl_dollars", "sum"),
            metric_min=(metric_col, "min"),
            metric_max=(metric_col, "max"),
            metric_median=(metric_col, "median"),
        )
        .reset_index(drop=True)
    )
    summary["loss_rate"] = summary["losses"] / summary["trades"] * 100.0
    summary["bucket_label"] = [
        f"Q{i + 1}: {row.metric_min:,.2f} to {row.metric_max:,.2f}"
        for i, row in enumerate(summary.itertuples(index=False))
    ]
    return summary


def build_research_trade_diagnostic_df(root_path: str) -> pd.DataFrame:
    trades = load_latest_direct_replay_trades(root_path)
    features = load_research_parquet(root_path, "features")
    if trades.empty or features.empty:
        return pd.DataFrame()
    work = trades.copy()
    work["market"] = work.get("market", "").fillna("").astype(str).str.upper()
    work["side"] = work.get("side", "").fillna("").astype(str).str.lower()
    work["entry_ts"] = pd.to_datetime(work.get("entry_ts"), utc=True, errors="coerce")
    work["gross_pnl_dollars"] = pd.to_numeric(work.get("net_pnl_dollars"), errors="coerce")
    work = work[work["market"].ne("") & work["entry_ts"].notna() & work["side"].isin(["yes", "no"])].copy()
    feat = features.copy()
    feat["market_ticker"] = feat.get("market_ticker", "").fillna("").astype(str).str.upper()
    feat["ts"] = pd.to_datetime(feat.get("ts"), utc=True, errors="coerce")
    feat = feat[feat["market_ticker"].ne("") & feat["ts"].notna()].copy()
    if work.empty or feat.empty:
        return pd.DataFrame()
    keep = [c for c in ["market_ticker","ts","yes_bid_cents","yes_ask_cents","no_bid_cents","no_ask_cents","spread_yes","spread_no","yes_range_30s","no_range_30s","yes_range_60s","no_range_60s","yes_move_30s","no_move_30s","yes_move_60s","no_move_60s","depth_imbalance","seconds_to_close"] if c in feat.columns]
    feat = feat[keep].sort_values(["market_ticker","ts"])
    frames=[]
    for market, grp in work.groupby("market", dropna=False):
        mf = feat[feat["market_ticker"] == str(market)].sort_values("ts")
        if mf.empty:
            continue
        frames.append(pd.merge_asof(grp.sort_values("entry_ts"), mf, left_on="entry_ts", right_on="ts", direction="backward", tolerance=pd.Timedelta(seconds=120)))
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out = out[out["ts"].notna()].copy()
    if out.empty:
        return pd.DataFrame()
    out["display_outcome"] = np.where(out["gross_pnl_dollars"].fillna(0.0) >= 0, "win", "loss")
    out["loss"] = out["gross_pnl_dollars"].fillna(0.0) < 0
    out["win"] = out["gross_pnl_dollars"].fillna(0.0) > 0
    out["hour"] = pd.to_datetime(out["entry_ts"], utc=True, errors="coerce").dt.tz_convert(MA_TZ).dt.hour
    out["entry_bid"] = np.where(out["side"] == "yes", pd.to_numeric(out.get("yes_bid_cents"), errors="coerce"), pd.to_numeric(out.get("no_bid_cents"), errors="coerce"))
    out["entry_ask"] = np.where(out["side"] == "yes", pd.to_numeric(out.get("yes_ask_cents"), errors="coerce"), pd.to_numeric(out.get("no_ask_cents"), errors="coerce"))
    out["entry_spread"] = np.where(out["side"] == "yes", pd.to_numeric(out.get("spread_yes"), errors="coerce"), pd.to_numeric(out.get("spread_no"), errors="coerce"))
    out["same_side_range_30s"] = np.where(out["side"] == "yes", pd.to_numeric(out.get("yes_range_30s"), errors="coerce"), pd.to_numeric(out.get("no_range_30s"), errors="coerce"))
    out["same_side_range_60s"] = np.where(out["side"] == "yes", pd.to_numeric(out.get("yes_range_60s"), errors="coerce"), pd.to_numeric(out.get("no_range_60s"), errors="coerce"))
    out["same_side_move_30s_abs"] = np.where(out["side"] == "yes", pd.to_numeric(out.get("yes_move_30s"), errors="coerce"), pd.to_numeric(out.get("no_move_30s"), errors="coerce")).astype(float)
    out["same_side_move_30s_abs"] = out["same_side_move_30s_abs"].abs()
    out["same_side_move_60s_abs"] = np.where(out["side"] == "yes", pd.to_numeric(out.get("yes_move_60s"), errors="coerce"), pd.to_numeric(out.get("no_move_60s"), errors="coerce")).astype(float)
    out["same_side_move_60s_abs"] = out["same_side_move_60s_abs"].abs()
    out["depth_imbalance_abs"] = pd.to_numeric(out.get("depth_imbalance"), errors="coerce").abs()
    out["obs"] = 1
    return out.sort_values("entry_ts").reset_index(drop=True)

def render_research_backed_loss_diagnostics(active_dataset_tag: str) -> bool:
    research_root = resolve_research_root_for_dataset(active_dataset_tag)
    diag = build_research_trade_diagnostic_df(str(research_root))
    if diag.empty:
        return False
    st.markdown("## Loss diagnostics")
    st.caption("Research-backed loss analysis using direct replay trades joined to the recorded feature store at entry time.")
    metric_options = {"Entry spread":"entry_spread","30s same-side range":"same_side_range_30s","60s same-side range":"same_side_range_60s","30s same-side move":"same_side_move_30s_abs","60s same-side move":"same_side_move_60s_abs","Depth imbalance":"depth_imbalance_abs","Seconds to close":"seconds_to_close"}
    metric_blurbs = {"Entry spread":"Wider spreads mean worse immediate fills and less forgiving entries.","30s same-side range":"This is the core calmness metric now driving the new live entry gate.","60s same-side range":"A wider 60-second range suggests the market was unstable for longer before entry.","30s same-side move":"Large surges just before entry often indicate a late chase.","60s same-side move":"Captures slower build-ups that may still be too stretched.","Depth imbalance":"Extreme one-sided depth can mean the move is crowded and vulnerable.","Seconds to close":"Late entries can behave differently, especially around stop behavior."}
    overall_loss_rate = float(diag["loss"].mean() * 100.0)
    total_pnl = float(pd.to_numeric(diag["gross_pnl_dollars"], errors="coerce").fillna(0.0).sum())
    overall_avg_pnl = float(pd.to_numeric(diag["gross_pnl_dollars"], errors="coerce").fillna(0.0).mean()) if len(diag) else 0.0
    median_loss_value = diag.loc[diag["loss"], "gross_pnl_dollars"].median() if diag["loss"].any() else None
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Replay trades used", f"{len(diag)}")
    c2.metric("Loss rate", format_pct(overall_loss_rate))
    c3.metric("Total P and L", format_money(total_pnl))
    c4.metric("Median loss", format_money(median_loss_value))
    candidates = build_loss_filter_candidates(diag, metric_options)
    best_recos, danger_recos = build_loss_strategy_recommendations(candidates)
    st.markdown("### Best loss-mitigation ideas from the current sample")
    if best_recos.empty:
        st.info("No clean single-metric mitigation rule stands out yet in the research-backed sample.")
    else:
        cols = st.columns(len(best_recos), gap="large")
        for idx, (_, row) in enumerate(best_recos.iterrows()):
            cols[idx].markdown(f"<div class='panel'><div class='small-muted'>Recommendation {idx + 1}</div><h4 style='margin:0.25rem 0 0.45rem 0;'>Keep {html.escape(str(row['Metric']))}</h4><div class='small-muted' style='margin-bottom:0.45rem;'>{html.escape(str(row['Keep rule']))} | cutoff {float(row['Cutoff']):,.2f}</div><div class='small-muted'>Loss rate improves by {float(row['Loss rate delta %']):+.1f} pts and avg P and L / trade improves by {format_money(float(row['Avg P and L delta']))} while keeping {float(row['Keep rate %']):.1f}% of replayed trades.</div></div>", unsafe_allow_html=True)
    if not danger_recos.empty:
        st.markdown("### Conditions that look most dangerous")
        cols = st.columns(len(danger_recos), gap="large")
        for idx, (_, row) in enumerate(danger_recos.iterrows()):
            cols[idx].markdown(f"<div class='panel'><div class='small-muted'>Avoid pattern {idx + 1}</div><h4 style='margin:0.25rem 0 0.45rem 0;color:var(--red);'>{html.escape(str(row['Metric']))}</h4><div class='small-muted' style='margin-bottom:0.45rem;'>{html.escape(str(row['Keep rule']))} | cutoff {float(row['Cutoff']):,.2f}</div><div class='small-muted'>Loss rate worsens by {float(row['Loss rate delta %']):+.1f} pts and avg P and L / trade changes by {format_money(float(row['Avg P and L delta']))} in this replay slice.</div></div>", unsafe_allow_html=True)
    selected_label = st.selectbox("Metric", list(metric_options.keys()), key=f"research_loss_diag_metric_{active_dataset_tag}")
    metric_col = metric_options[selected_label]
    metric_values = pd.to_numeric(diag[metric_col], errors="coerce").dropna()
    if metric_values.empty:
        st.info("No usable metric values are available for that diagnostic.")
        return True
    ctl_l, ctl_r = st.columns([1.15,0.85], gap="large")
    with ctl_l:
        filter_direction = st.radio("Keep which side?", ["Keep lowest values","Keep highest values"], horizontal=True, key=f"research_loss_diag_keep_rule_{active_dataset_tag}")
        percentile = st.slider("How much of the sample to keep", min_value=10, max_value=90, step=5, value=35, key=f"research_loss_diag_keep_pct_{active_dataset_tag}")
    with ctl_r:
        st.markdown(f"<div class='panel'><div class='small-muted'>Selected metric</div><strong>{selected_label}</strong><div class='small-muted' style='margin-top:0.35rem;'>{metric_blurbs.get(selected_label, '')}</div></div>", unsafe_allow_html=True)
    if filter_direction == "Keep highest values":
        cutoff = float(metric_values.quantile(1 - percentile / 100.0))
        filtered = diag[pd.to_numeric(diag[metric_col], errors="coerce") >= cutoff].copy()
        rule_label = f"{selected_label} >= {cutoff:,.2f}"
    else:
        cutoff = float(metric_values.quantile(percentile / 100.0))
        filtered = diag[pd.to_numeric(diag[metric_col], errors="coerce") <= cutoff].copy()
        rule_label = f"{selected_label} <= {cutoff:,.2f}"
    if filtered.empty:
        st.warning("That percentile cutoff removed all replayed trades.")
        return True
    filtered_loss_rate = float(filtered["loss"].mean() * 100.0)
    filtered_avg_pnl = float(pd.to_numeric(filtered["gross_pnl_dollars"], errors="coerce").fillna(0.0).mean()) if len(filtered) else 0.0
    kept_pct = len(filtered) / max(len(diag), 1) * 100.0
    loss_delta = filtered_loss_rate - overall_loss_rate
    avg_pnl_delta = filtered_avg_pnl - overall_avg_pnl
    direction_phrase = "best-looking tail" if loss_delta < 0 and avg_pnl_delta >= 0 else "risky tail" if loss_delta > 0 and avg_pnl_delta < 0 else "mixed tail"
    st.markdown(f"<div class='summary-band'><h4>Current rule: {html.escape(rule_label)}</h4><p>This keeps <strong>{len(filtered)}</strong> of <strong>{len(diag)}</strong> replayed trades ({kept_pct:.1f}% of the sample). Compared with all replayed trades, this slice changes loss rate by <strong>{loss_delta:+.1f} pts</strong> and average P and L per trade by <strong>{format_money(avg_pnl_delta)}</strong>. In plain English: this looks like a <strong>{direction_phrase}</strong>.</p></div>", unsafe_allow_html=True)
    s1,s2,s3,s4 = st.columns(4)
    s1.metric("Kept trades", f"{len(filtered)}", delta=f"{kept_pct:.1f}% of sample")
    s2.metric("Kept loss rate", format_pct(filtered_loss_rate), delta=f"{loss_delta:+.1f} pts vs all")
    s3.metric("Filtered total P and L", format_money(filtered["gross_pnl_dollars"].sum()))
    s4.metric("Kept avg P and L / trade", format_money(filtered_avg_pnl), delta=format_money(avg_pnl_delta))
    compare = pd.DataFrame([{"Group":"All replayed trades","Trades":len(diag),"Loss rate":format_pct(overall_loss_rate),"Total P and L":format_money(diag["gross_pnl_dollars"].sum()),"Avg P and L / trade":format_money(overall_avg_pnl)},{"Group":"Kept slice","Trades":len(filtered),"Loss rate":format_pct(filtered_loss_rate),"Total P and L":format_money(filtered["gross_pnl_dollars"].sum()),"Avg P and L / trade":format_money(filtered_avg_pnl)}])
    st.markdown("### Filter impact")
    st.dataframe(compare, use_container_width=True, hide_index=True)
    left,right = st.columns([1.2,0.8], gap="large")
    with left:
        scatter = go.Figure()
        scatter.add_trace(go.Scatter(x=diag["entry_ts"], y=diag[metric_col], mode="markers", marker=dict(size=10, color=np.where(diag["loss"], "#ff5a5f", "#00c46a"), line=dict(color="rgba(255,255,255,0.18)", width=1)), customdata=np.stack([diag["gross_pnl_dollars"].fillna(0.0).to_numpy(dtype=float), pd.to_numeric(diag.get("entry_spread"), errors="coerce").fillna(np.nan).to_numpy(dtype=float)], axis=1), hovertemplate="%{x|%Y-%m-%d %I:%M %p}<br>" + selected_label + "=%{y:.2f}<br>P and L=$%{customdata[0]:.2f}<br>Entry spread=%{customdata[1]:.2f}c<extra></extra>", showlegend=False))
        scatter.add_hline(y=cutoff, line_width=1, line_dash="dash", line_color="rgba(245,196,81,0.55)")
        scatter.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title=None, yaxis_title=selected_label.lower())
        st.plotly_chart(scatter, width="stretch")
    with right:
        bucket_summary = build_metric_bucket_summary(diag, metric_col)
        if bucket_summary.empty:
            st.info("Not enough spread in that metric to bucket the replayed sample yet.")
        else:
            bucket_fig = go.Figure()
            bucket_fig.add_trace(go.Bar(x=bucket_summary["bucket_label"], y=bucket_summary["loss_rate"], marker_color="#ff8a5b", name="Loss rate"))
            bucket_fig.add_trace(go.Scatter(x=bucket_summary["bucket_label"], y=bucket_summary["avg_pnl"], mode="lines+markers", line=dict(color="#36e28f", width=2.5), name="Avg P&L", yaxis="y2"))
            bucket_fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title=None, yaxis=dict(title="Loss rate %"), yaxis2=dict(title="Avg P&L", overlaying="y", side="right"), legend=dict(orientation="h", y=1.08, x=0))
            st.plotly_chart(bucket_fig, width="stretch")
    return True

def render_loss_diagnostics_tab(price_df: pd.DataFrame, trades_df: pd.DataFrame, active_dataset_tag: str) -> None:
    if render_research_backed_loss_diagnostics(active_dataset_tag):
        return

    st.markdown("## Loss diagnostics")
    st.caption("Use this page to answer one question: which pre-entry conditions seem to make losses more likely, and does filtering them actually improve trade quality?")
    active_dataset_tag = str(active_dataset_tag or st.session_state.get("dataset_tag", current_strategy_tag()))
    legacy_reco_active = False
    profile = infer_strategy_profile(active_dataset_tag, trades_df)
    baseline_entry_cents = int(profile["entry"])
    baseline_position_size = int(profile["position_size"])

    loss_trades = trades_df.copy() if trades_df is not None else pd.DataFrame()
    if not loss_trades.empty:
        if "entry_trigger_cents" in loss_trades.columns:
            loss_trades = loss_trades[
                pd.to_numeric(loss_trades["entry_trigger_cents"], errors="coerce") == baseline_entry_cents
            ].copy()
        if "qty" in loss_trades.columns:
            matching_qty = loss_trades[
                pd.to_numeric(loss_trades["qty"], errors="coerce") == baseline_position_size
            ].copy()
            if not matching_qty.empty:
                loss_trades = matching_qty

    diag = build_trade_diagnostic_df(price_df, loss_trades)
    if diag.empty:
        st.info("Not enough matched trade and price history exists yet to build diagnostics.")
        return

    metric_options = {
        "Entry spread": "entry_spread",
        "Pre-entry std dev": "pre_std",
        "Pre-entry range": "pre_range",
        "Average move before entry": "pre_mean_abs_move",
        "Largest move before entry": "pre_max_abs_move",
        "Net move before entry": "pre_net_move",
        "Chop ratio": "pre_chop_ratio",
    }

    overall_loss_rate = float(diag["loss"].mean() * 100.0)
    total_pnl = float(pd.to_numeric(diag["gross_pnl_dollars"], errors="coerce").fillna(0.0).sum())
    overall_avg_pnl = float(pd.to_numeric(diag["gross_pnl_dollars"], errors="coerce").fillna(0.0).mean()) if len(diag) else 0.0
    median_loss_value = diag.loc[diag["loss"], "gross_pnl_dollars"].median() if diag["loss"].any() else None
    unique_markets = int(diag["market"].astype(str).nunique()) if "market" in diag.columns else 0
    matched_price_rows = int(diag["obs"].fillna(0).sum()) if "obs" in diag.columns else 0
    loss_count = int(diag["loss"].sum()) if "loss" in diag.columns else 0
    win_count = int(diag["win"].sum()) if "win" in diag.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Matched trades", f"{len(diag)}")
    c2.metric("Loss rate", format_pct(overall_loss_rate))
    c3.metric("Total P and L", format_money(total_pnl))
    c4.metric("Median loss", format_money(median_loss_value))

    coverage_cols = st.columns(4)
    coverage_cols[0].metric("Markets covered", f"{unique_markets}")
    coverage_cols[1].metric("Wins / losses", f"{win_count} / {loss_count}")
    coverage_cols[2].metric("Price observations used", f"{matched_price_rows}")
    coverage_cols[3].metric("Lookback per trade", "8 points", delta="per matched market history")

    st.markdown(
        "<div class='panel'><div class='small-muted'>Sample coverage</div><strong>This diagnostics view uses all matched trades and all parsed heartbeat history available for the active strategy profile in the selected dataset.</strong><div class='small-muted' style='margin-top:0.35rem;'>Current profile lock: entry {baseline_entry_cents}c | size {baseline_position_size}. It is not capped at 90 markets.</div></div>",
        unsafe_allow_html=True,
    )
    if legacy_reco_active:
        st.markdown(
            "<div class='panel'><div class='small-muted'>Archived 90/60 diagnostics preset</div><strong>This view opens on recommendation strategy 1 for the archived research sample.</strong><div class='small-muted' style='margin-top:0.35rem;'>Current preset: keep the highest 35% of <strong>Pre-entry std dev</strong>. This is a diagnostics default for analysis, not a claim about the live bot unless you explicitly run that strategy separately.</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="insight-grid">
          <div class="insight-card">
            <strong>1. Pick one metric</strong>
            <span>Choose the pre-entry feature you want to test. The page will compare all trades against the kept tail of that metric.</span>
          </div>
          <div class="insight-card">
            <strong>2. Read the summary first</strong>
            <span>Start with the kept-trades summary and filter impact table. Those tell you whether the rule actually improved results.</span>
          </div>
          <div class="insight-card">
            <strong>3. Use charts as evidence</strong>
            <span>The charts below help you judge whether the effect is broad, concentrated in one tail, or just noisy sample variation.</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    candidates = build_loss_filter_candidates(diag)
    if not candidates.empty:
        preview = candidates.head(8).copy()
        preview["Cutoff"] = preview["Cutoff"].map(lambda v: f"{v:,.2f}")
        preview["Keep rate %"] = preview["Keep rate %"].map(lambda v: f"{v:,.1f}%")
        preview["Loss rate %"] = preview["Loss rate %"].map(lambda v: f"{v:,.1f}%")
        preview["Loss rate delta %"] = preview["Loss rate delta %"].map(lambda v: f"{v:+,.1f} pts")
        preview["Avg P and L / trade"] = preview["Avg P and L / trade"].map(format_money)
        preview["Avg P and L delta"] = preview["Avg P and L delta"].map(format_money)
        preview["Total P and L"] = preview["Total P and L"].map(format_money)
    best_recos, danger_recos = build_loss_strategy_recommendations(candidates)

    st.markdown("### Best loss-mitigation ideas from the current sample")
    if best_recos.empty:
        st.info("No clean single-metric mitigation rule stands out yet. The current sample either looks mixed or too noisy to support a strong recommendation.")
    else:
        reco_cols = st.columns(len(best_recos), gap="large")
        for idx, (_, row) in enumerate(best_recos.iterrows()):
            reco_cols[idx].markdown(
                f"""
                <div class="panel">
                  <div class="small-muted">Recommendation {idx + 1}</div>
                  <h4 style="margin:0.25rem 0 0.45rem 0;">Keep {html.escape(str(row['Metric']))}</h4>
                  <div class="small-muted" style="margin-bottom:0.45rem;">{html.escape(str(row['Keep rule']))} | cutoff {float(row['Cutoff']):,.2f}</div>
                  <strong style="display:block;margin-bottom:0.35rem;">Why it helps</strong>
                  <div class="small-muted">Loss rate improves by {float(row['Loss rate delta %']):+.1f} pts and average P and L / trade improves by {format_money(float(row['Avg P and L delta']))} while still keeping {float(row['Keep rate %']):.1f}% of trades.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if not danger_recos.empty:
        st.markdown("### Conditions that look most dangerous")
        st.caption("These are the tails that most consistently coincide with worse losses. If you want simple guardrails, these are the first places to avoid or downweight.")
        danger_cols = st.columns(len(danger_recos), gap="large")
        for idx, (_, row) in enumerate(danger_recos.iterrows()):
            danger_cols[idx].markdown(
                f"""
                <div class="panel">
                  <div class="small-muted">Avoid pattern {idx + 1}</div>
                  <h4 style="margin:0.25rem 0 0.45rem 0;color:var(--red);">{html.escape(str(row['Metric']))}</h4>
                  <div class="small-muted" style="margin-bottom:0.45rem;">{html.escape(str(row['Keep rule']))} | cutoff {float(row['Cutoff']):,.2f}</div>
                  <strong style="display:block;margin-bottom:0.35rem;">Why it looks risky</strong>
                  <div class="small-muted">Loss rate worsens by {float(row['Loss rate delta %']):+.1f} pts and average P and L / trade changes by {format_money(float(row['Avg P and L delta']))} in this slice.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    control_left, control_right = st.columns([1.15, 0.85], gap="large")
    with control_left:
        st.markdown("### Choose the rule to test")
        metric_labels = list(metric_options.keys())
        default_metric_label = metric_labels[0]
        default_filter_direction = "Keep lowest values"
        default_percentile = 35

        metric_state_key = "loss_diag_metric"
        direction_state_key = "loss_diag_keep_rule"
        percentile_state_key = "loss_diag_keep_pct"
        preset_state_key = "loss_diag_preset_tag"

        if st.session_state.get(preset_state_key) != active_dataset_tag:
            st.session_state[metric_state_key] = default_metric_label
            st.session_state[direction_state_key] = default_filter_direction
            st.session_state[percentile_state_key] = default_percentile
            st.session_state[preset_state_key] = active_dataset_tag

        selected_label = st.selectbox("Metric", metric_labels, key=metric_state_key)
        metric_col = metric_options[selected_label]
        metric_values = pd.to_numeric(diag[metric_col], errors="coerce").dropna()
        if metric_values.empty:
            st.info("No usable metric values are available for that diagnostic.")
            return
        filter_direction = st.radio(
            "Keep which side?",
            ["Keep lowest values", "Keep highest values"],
            horizontal=True,
            key=direction_state_key,
        )
        percentile = st.slider(
            "How much of the sample to keep",
            min_value=10,
            max_value=90,
            step=5,
            key=percentile_state_key,
        )
    with control_right:
        st.markdown("### What the metric means")
        metric_blurbs = {
            "Entry spread": "Wider spreads mean worse immediate fills and less forgiving entries.",
            "Pre-entry std dev": "Higher short-term volatility can mean unstable price action just before entry.",
            "Pre-entry range": "A large pre-entry range suggests the market was already stretching before you got in.",
            "Average move before entry": "Captures how noisy the tape was before the trigger fired.",
            "Largest move before entry": "Highlights whether one sharp move tends to precede bad entries.",
            "Net move before entry": "Shows whether directional drift before entry matters more than raw chop.",
            "Chop ratio": "Higher values imply more back-and-forth movement relative to net progress.",
        }
        st.markdown(
            f"<div class='panel'><div class='small-muted'>Selected metric</div><strong>{selected_label}</strong><div class='small-muted' style='margin-top:0.35rem;'>{metric_blurbs.get(selected_label, '')}</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='panel' style='margin-top:0.8rem;'><div class='small-muted'>Reading rule of thumb</div><strong>Prefer metrics where the kept slice lowers loss rate and improves average P and L at the same time.</strong><div class='small-muted' style='margin-top:0.35rem;'>If one improves while the other gets worse, treat it as mixed evidence instead of a clear filter candidate.</div></div>",
            unsafe_allow_html=True,
        )

    if filter_direction == "Keep highest values":
        cutoff = float(metric_values.quantile(1 - percentile / 100.0))
        filtered = diag[pd.to_numeric(diag[metric_col], errors="coerce") >= cutoff].copy()
        rule_label = f"{selected_label} >= {cutoff:,.2f}"
    else:
        cutoff = float(metric_values.quantile(percentile / 100.0))
        filtered = diag[pd.to_numeric(diag[metric_col], errors="coerce") <= cutoff].copy()
        rule_label = f"{selected_label} <= {cutoff:,.2f}"
    if filtered.empty:
        st.warning("That percentile cutoff removed all trades.")
        return

    filtered_loss_rate = float(filtered["loss"].mean() * 100.0)
    filtered_avg_pnl = float(pd.to_numeric(filtered["gross_pnl_dollars"], errors="coerce").fillna(0.0).mean()) if len(filtered) else 0.0
    kept_pct = len(filtered) / max(len(diag), 1) * 100.0
    loss_delta = filtered_loss_rate - overall_loss_rate
    avg_pnl_delta = filtered_avg_pnl - overall_avg_pnl
    direction_phrase = "best-looking tail" if loss_delta < 0 and avg_pnl_delta >= 0 else "risky tail" if loss_delta > 0 and avg_pnl_delta < 0 else "mixed tail"

    st.markdown(
        f"""
        <div class="summary-band">
          <h4>Current rule: {html.escape(rule_label)}</h4>
          <p>This keeps <strong>{len(filtered)}</strong> of <strong>{len(diag)}</strong> trades ({kept_pct:.1f}% of the sample). Compared with all trades, this slice changes loss rate by <strong>{loss_delta:+.1f} pts</strong> and average P and L per trade by <strong>{format_money(avg_pnl_delta)}</strong>. In plain English: this looks like a <strong>{direction_phrase}</strong>.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    bucket_summary = build_metric_bucket_summary(diag, metric_col)

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Kept trades", f"{len(filtered)}", delta=f"{kept_pct:.1f}% of sample")
    s2.metric("Kept loss rate", format_pct(filtered_loss_rate), delta=f"{loss_delta:+.1f} pts vs all")
    s3.metric("Filtered total P and L", format_money(filtered["gross_pnl_dollars"].sum()))
    s4.metric("Kept avg P and L / trade", format_money(filtered_avg_pnl), delta=format_money(avg_pnl_delta))

    compare = pd.DataFrame(
        [
            {
                "Group": "All trades",
                "Trades": len(diag),
                "Loss rate": format_pct(overall_loss_rate),
                "Total P and L": format_money(diag["gross_pnl_dollars"].sum()),
                "Avg P and L / trade": format_money(overall_avg_pnl),
            },
            {
                "Group": "Kept slice",
                "Trades": len(filtered),
                "Loss rate": format_pct(filtered_loss_rate),
                "Total P and L": format_money(filtered["gross_pnl_dollars"].sum()),
                "Avg P and L / trade": format_money(filtered_avg_pnl),
            },
        ]
    )
    st.markdown("### Filter impact")
    st.caption("Read this table before the charts. If the kept slice is not clearly better than all trades, the metric is probably not useful as a standalone gate.")
    st.dataframe(compare, use_container_width=True, hide_index=True)

    st.markdown("### Where the metric becomes dangerous")
    st.caption("The left chart shows the raw trade-by-trade scatter. The right chart shows whether losses cluster by entry hour, which helps separate metric effects from time-of-day effects.")
    left, right = st.columns([1.2, 0.8], gap="large")
    with left:
        scatter = go.Figure()
        scatter.add_trace(
            go.Scatter(
                x=diag["entry_ts"],
                y=diag[metric_col],
                mode="markers",
                marker=dict(
                    size=10,
                    color=np.where(diag["loss"], "#ff5a5f", "#00c46a"),
                    line=dict(color="rgba(255,255,255,0.18)", width=1),
                ),
                customdata=np.stack(
                    [
                        diag["gross_pnl_dollars"].fillna(0.0).to_numpy(dtype=float),
                        diag["entry_spread"].fillna(np.nan).to_numpy(dtype=float),
                    ],
                    axis=1,
                ),
                hovertemplate=(
                    "%{x|%Y-%m-%d %I:%M %p}<br>"
                    + selected_label + "=%{y:.2f}<br>"
                    + "P and L=$%{customdata[0]:.2f}<br>"
                    + "Entry spread=%{customdata[1]:.2f}c<extra></extra>"
                ),
                showlegend=False,
            )
        )
        scatter.add_hline(y=cutoff, line_width=1, line_dash="dash", line_color="rgba(245,196,81,0.55)")
        scatter.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title=None,
            yaxis_title=selected_label.lower(),
        )
        scatter.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        scatter.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        st.plotly_chart(scatter, width="stretch")

    with right:
        hourly = (
            diag.groupby("hour")
            .agg(trades=("market", "size"), losses=("loss", "sum"), pnl=("gross_pnl_dollars", "sum"))
            .reset_index()
        )
        hourly["loss_rate"] = hourly["losses"] / hourly["trades"] * 100.0
        fig_hour = go.Figure()
        fig_hour.add_trace(
            go.Bar(
                x=hourly["hour"],
                y=hourly["loss_rate"],
                marker_color=np.where(hourly["loss_rate"] >= overall_loss_rate, "#ff5a5f", "#00c46a"),
                customdata=np.stack([hourly["trades"], hourly["pnl"]], axis=1),
                hovertemplate="Hour %{x}:00<br>Loss rate=%{y:.1f}%<br>Trades=%{customdata[0]:.0f}<br>P and L=$%{customdata[1]:.2f}<extra></extra>",
                showlegend=False,
            )
        )
        fig_hour.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="entry hour",
            yaxis_title="loss rate %",
        )
        fig_hour.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        fig_hour.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        st.plotly_chart(fig_hour, width="stretch")

    if not bucket_summary.empty:
        st.markdown("### Does the damage sit in one tail or across the whole range?")
        st.caption("Quantile buckets are easier to read than the scatter when you want to see whether the metric gets steadily worse, only breaks in one extreme, or is mostly noise.")
        bleft, bright = st.columns(2, gap="large")
        with bleft:
            fig_bucket_loss = go.Figure()
            fig_bucket_loss.add_trace(
                go.Bar(
                    x=bucket_summary["bucket_label"],
                    y=bucket_summary["loss_rate"],
                    marker_color=np.where(bucket_summary["loss_rate"] >= overall_loss_rate, "#ff5a5f", "#00c46a"),
                    customdata=np.stack(
                        [
                            bucket_summary["trades"].to_numpy(dtype=float),
                            bucket_summary["avg_pnl"].to_numpy(dtype=float),
                        ],
                        axis=1,
                    ),
                    hovertemplate=(
                        "%{x}<br>"
                        "Loss rate=%{y:.1f}%<br>"
                        "Trades=%{customdata[0]:.0f}<br>"
                        "Avg P and L / trade=$%{customdata[1]:.2f}<extra></extra>"
                    ),
                    showlegend=False,
                )
            )
            fig_bucket_loss.add_hline(y=overall_loss_rate, line_width=1, line_dash="dash", line_color="rgba(245,196,81,0.55)")
            fig_bucket_loss.update_layout(
                height=360,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title=None,
                yaxis_title="loss rate %",
            )
            fig_bucket_loss.update_xaxes(showgrid=False)
            fig_bucket_loss.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
            st.plotly_chart(fig_bucket_loss, width="stretch")

        with bright:
            fig_bucket_pnl = go.Figure()
            fig_bucket_pnl.add_trace(
                go.Bar(
                    x=bucket_summary["bucket_label"],
                    y=bucket_summary["avg_pnl"],
                    marker_color=np.where(bucket_summary["avg_pnl"] >= 0, "#00c46a", "#ff5a5f"),
                    customdata=np.stack(
                        [
                            bucket_summary["trades"].to_numpy(dtype=float),
                            bucket_summary["loss_rate"].to_numpy(dtype=float),
                        ],
                        axis=1,
                    ),
                    hovertemplate=(
                        "%{x}<br>"
                        "Avg P and L / trade=$%{y:.2f}<br>"
                        "Trades=%{customdata[0]:.0f}<br>"
                        "Loss rate=%{customdata[1]:.1f}%<extra></extra>"
                    ),
                    showlegend=False,
                )
            )
            fig_bucket_pnl.add_hline(y=0, line_width=1, line_dash="dash", line_color="rgba(255,255,255,0.18)")
            fig_bucket_pnl.update_layout(
                height=360,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title=None,
                yaxis_title="avg P and L / trade",
            )
            fig_bucket_pnl.update_xaxes(showgrid=False)
            fig_bucket_pnl.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
            st.plotly_chart(fig_bucket_pnl, width="stretch")

        bucket_table = bucket_summary.copy()
        bucket_table["Avg P and L / trade"] = bucket_table["avg_pnl"].map(format_money)
        bucket_table["Total P and L"] = bucket_table["total_pnl"].map(format_money)
        bucket_table["Loss rate"] = bucket_table["loss_rate"].map(format_pct)
        st.dataframe(
            bucket_table[
                ["bucket_label", "trades", "Loss rate", "Avg P and L / trade", "Total P and L"]
            ].rename(columns={"bucket_label": "Bucket", "trades": "Trades"}),
            use_container_width=True,
            hide_index=True,
        )

    risk_ascending = filter_direction == "Keep highest values"
    losses = diag[diag["loss"]].copy().sort_values(metric_col, ascending=risk_ascending).head(20)
    losses["Entry time"] = losses["entry_ts"].dt.strftime("%Y-%m-%d %I:%M %p")
    losses["Side"] = losses["side"].astype(str).str.upper()
    losses["Hour"] = losses["hour"].astype("Int64")
    losses["P and L"] = losses["gross_pnl_dollars"].apply(format_money)
    losses["Entry spread"] = losses["entry_spread"].apply(format_cents)
    if not candidates.empty:
        with st.expander("Show top candidate one-variable filters", expanded=False):
            st.caption("These are the strongest simple keep rules in the current sample. Treat them as ideas to test, not as proof.")
            st.dataframe(preview, use_container_width=True, hide_index=True)
    with st.expander("Show diagnostics sample details", expanded=False):
        sample_table = (
            diag.assign(
                **{
                    "Entry time": diag["entry_ts"].dt.strftime("%Y-%m-%d %I:%M %p"),
                    "Outcome": diag["display_outcome"].astype(str).str.upper(),
                    "P and L": diag["gross_pnl_dollars"].map(format_money),
                    "Entry spread": diag["entry_spread"].map(format_cents),
                }
            )[["Entry time", "market", "side", "Outcome", "P and L", "Entry spread", "obs"]]
            .rename(columns={"market": "Market", "side": "Side", "obs": "Price points used"})
        )
        sample_table["Side"] = sample_table["Side"].astype(str).str.upper()
        st.caption("This is the matched sample feeding the diagnostics calculations for the current dataset.")
        st.dataframe(sample_table, use_container_width=True, hide_index=True)
    st.markdown("### Example losing trades from the risky side")
    st.caption("Use these rows to sanity-check the pattern. If the examples look random or contradictory, the metric may not be robust enough to trust.")
    loss_cols = ["Entry time", "market", "Side", "Hour", "P and L", "Entry spread"]
    rename_map: dict[str, str] = {}
    if metric_col != "entry_spread":
        loss_cols.append(metric_col)
        rename_map[metric_col] = selected_label
    st.dataframe(
        losses[loss_cols].rename(columns=rename_map),
        use_container_width=True,
        hide_index=True,
    )



def filter_price_series(df: pd.DataFrame, lookback: str, markets: list[str]) -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        return out
    if markets and "All markets" not in markets:
        out = out[out["market"].isin(markets)]
    if lookback != "All":
        mapping = {
            "15m": pd.Timedelta(minutes=15),
            "30m": pd.Timedelta(minutes=30),
            "1h": pd.Timedelta(hours=1),
            "3h": pd.Timedelta(hours=3),
            "6h": pd.Timedelta(hours=6),
            "12h": pd.Timedelta(hours=12),
            "24h": pd.Timedelta(hours=24),
        }
        delta = mapping.get(lookback)
        if delta is not None and not out.empty:
            cutoff = out["ts"].max() - delta
            out = out[out["ts"] >= cutoff]
    return out



def aggregate_price_series(df: pd.DataFrame, bucket: str) -> pd.DataFrame:
    if df.empty or bucket == "Raw":
        return df.copy()
    freq_map = {"15s": "15s", "30s": "30s", "1m": "1min", "2m": "2min", "5m": "5min"}
    freq = freq_map.get(bucket)
    if not freq:
        return df.copy()
    parts = []
    for market, grp in df.groupby("market", sort=False):
        g = grp.sort_values("ts").set_index("ts")
        agg = g[["yes_bid", "yes_ask", "no_bid", "no_ask"]].resample(freq).last().dropna(how="all")
        agg["market"] = market
        parts.append(agg.reset_index())
    if not parts:
        return pd.DataFrame(columns=df.columns)
    return pd.concat(parts, ignore_index=True).sort_values("ts")




def parse_close_time_local(value: Any) -> datetime | None:
    try:
        ts = pd.to_datetime(value, utc=True, errors="coerce")
        if pd.isna(ts):
            return None
        return ts.tz_convert(MA_TZ).tz_localize(None).to_pydatetime()
    except Exception:
        return None


def make_market_metadata(lines: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for raw in lines:
        m = WATCH_RE.match(raw.strip())
        if not m:
            continue
        ts = parse_ts(m.group("ts"))
        if not ts:
            continue
        rows.append(
            {
                "market": m.group("market"),
                "ts": ts,
                "close_time": parse_close_time_local(m.group("close_time")),
                "status": m.group("status"),
            }
        )
    if not rows:
        return pd.DataFrame(columns=["market", "first_seen", "last_seen", "close_time", "status"])
    df = pd.DataFrame(rows).sort_values("ts")
    out = (
        df.groupby("market", as_index=False)
        .agg(
            first_seen=("ts", "min"),
            last_seen=("ts", "max"),
            close_time=("close_time", "last"),
            status=("status", "last"),
        )
        .sort_values("last_seen", ascending=False)
    )
    return out


def enrich_price_series(price_df: pd.DataFrame, market_meta: pd.DataFrame) -> pd.DataFrame:
    if price_df.empty:
        cols = list(price_df.columns)
        for extra in ["close_time", "status", "first_seen", "last_seen", "minutes_to_expiry", "yes_mid", "no_mid", "yes_spread", "no_spread"]:
            if extra not in cols:
                cols.append(extra)
        return pd.DataFrame(columns=cols)
    out = price_df.copy()
    if not market_meta.empty:
        out = out.merge(
            market_meta[["market", "close_time", "status", "first_seen", "last_seen"]],
            on="market",
            how="left",
        )
    else:
        out["close_time"] = pd.NaT
        out["status"] = ""
        out["first_seen"] = pd.NaT
        out["last_seen"] = pd.NaT
    out["yes_mid"] = out[["yes_bid", "yes_ask"]].mean(axis=1)
    out["no_mid"] = out[["no_bid", "no_ask"]].mean(axis=1)
    out["yes_spread"] = out["yes_ask"] - out["yes_bid"]
    out["no_spread"] = out["no_ask"] - out["no_bid"]
    if "close_time" in out.columns:
        out["minutes_to_expiry"] = (pd.to_datetime(out["close_time"], errors="coerce") - pd.to_datetime(out["ts"], errors="coerce")).dt.total_seconds() / 60.0
    else:
        out["minutes_to_expiry"] = pd.NA
    out["session_minutes"] = (pd.to_datetime(out["ts"], errors="coerce") - pd.to_datetime(out["first_seen"], errors="coerce")).dt.total_seconds() / 60.0
    return out.sort_values("ts")


def build_signal_df(lines: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for raw in lines:
        line = raw.strip()
        m = ENTRY_RE.match(line)
        if m:
            ts = parse_ts(m.group("ts"))
            if ts:
                rows.append(
                    {
                        "ts": ts,
                        "market": m.group("market"),
                        "kind": "entry",
                        "side": m.group("side"),
                        "limit": int(m.group("limit")),
                        "trigger": int(m.group("trigger")),
                        "qty": int(m.group("qty")),
                    }
                )
            continue
        m = EXIT_RE.match(line)
        if m:
            ts = parse_ts(m.group("ts"))
            if ts:
                rows.append(
                    {
                        "ts": ts,
                        "market": m.group("market"),
                        "kind": "exit",
                        "side": m.group("side"),
                        "limit": int(m.group("limit")),
                        "trigger": int(m.group("trigger")),
                        "qty": int(m.group("qty")),
                    }
                )
    if not rows:
        return pd.DataFrame(columns=["ts", "market", "kind", "side", "limit", "trigger", "qty"])
    return pd.DataFrame(rows).sort_values("ts")


SERIES_CONFIG: dict[str, dict[str, str]] = {
    "YES ask": {"col": "yes_ask", "color": "#8bd0ff", "spread_col": "yes_spread", "counterpart": "NO ask"},
    "NO ask": {"col": "no_ask", "color": "#2d7cff", "spread_col": "no_spread", "counterpart": "YES ask"},
    "YES bid": {"col": "yes_bid", "color": "#52e3a4", "spread_col": "yes_spread", "counterpart": "NO bid"},
    "NO bid": {"col": "no_bid", "color": "#f5c451", "spread_col": "no_spread", "counterpart": "YES bid"},
    "YES mid": {"col": "yes_mid", "color": "#c6f1ff", "spread_col": "yes_spread", "counterpart": "NO mid"},
    "NO mid": {"col": "no_mid", "color": "#6aa5ff", "spread_col": "no_spread", "counterpart": "YES mid"},
}


def bucket_to_freq(bucket: str) -> str:
    return {
        "15s": "15s",
        "30s": "30s",
        "1m": "1min",
        "2m": "2min",
        "5m": "5min",
    }.get(bucket, "1min")


def bucket_to_seconds(bucket: str) -> int:
    return {
        "Raw": 15,
        "15s": 15,
        "30s": 30,
        "1m": 60,
        "2m": 120,
        "5m": 300,
    }.get(bucket, 60)


def resample_ohlc_for_market(df: pd.DataFrame, market: str, col: str, bucket: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["ts", "open", "high", "low", "close"])
    market_df = df[df["market"] == market].sort_values("ts").copy()
    if market_df.empty or col not in market_df.columns:
        return pd.DataFrame(columns=["ts", "open", "high", "low", "close"])
    s = pd.to_numeric(market_df[col], errors="coerce")
    market_df = market_df.assign(_primary=s).dropna(subset=["_primary"])
    if market_df.empty:
        return pd.DataFrame(columns=["ts", "open", "high", "low", "close"])
    freq = bucket_to_freq(bucket)
    ohlc = market_df.set_index("ts")["_primary"].resample(freq).ohlc().dropna(how="all").reset_index()
    return ohlc



def compute_ta_columns(df: pd.DataFrame, price_col: str, spread_col: str, threshold: int) -> pd.DataFrame:
    out = df.copy()
    base_cols = [
        "primary", "ema_9", "ema_21", "sma_5", "bb_mid", "bb_upper", "bb_lower",
        "rsi_14", "roc_3", "rolling_std_5", "spread_primary", "solve_score"
    ]

    if out.empty or price_col not in out.columns:
        for col in base_cols:
            out[col] = np.nan
        return out

    def _to_num(series: pd.Series) -> pd.Series:
        s = pd.to_numeric(series, errors="coerce").astype("float64")
        return s.replace([np.inf, -np.inf], np.nan)

    for col in [price_col, spread_col, "yes_bid", "yes_ask", "no_bid", "no_ask", "yes_mid", "no_mid", "yes_spread", "no_spread", "minutes_to_expiry"]:
        if col in out.columns:
            out[col] = _to_num(out[col])

    series = _to_num(out[price_col])
    out["primary"] = series

    if series.notna().sum() == 0:
        for col in base_cols:
            if col not in out.columns:
                out[col] = np.nan
        return out

    out["ema_9"] = series.ewm(span=9, adjust=False, min_periods=1).mean()
    out["ema_21"] = series.ewm(span=21, adjust=False, min_periods=1).mean()
    out["sma_5"] = series.rolling(5, min_periods=1).mean()
    out["bb_mid"] = series.rolling(20, min_periods=5).mean()
    bb_std = series.rolling(20, min_periods=5).std(ddof=0)
    out["bb_upper"] = out["bb_mid"] + 2 * bb_std
    out["bb_lower"] = out["bb_mid"] - 2 * bb_std

    delta = series.diff()
    gain = delta.clip(lower=0).fillna(0.0).astype("float64")
    loss = (-delta.clip(upper=0)).fillna(0.0).astype("float64")
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out["rsi_14"] = (100 - (100 / (1 + rs))).clip(0, 100).fillna(50.0)

    out["roc_3"] = series.pct_change(3).mul(100)
    out["rolling_std_5"] = series.rolling(5, min_periods=2).std(ddof=0)

    if spread_col in out.columns:
        spread = _to_num(out[spread_col])
    else:
        spread = pd.Series(np.nan, index=out.index, dtype="float64")
    out["spread_primary"] = spread

    persistence = series.ge(float(threshold)).rolling(5, min_periods=1).mean().mul(100)
    momentum = ((out["ema_9"] - out["ema_21"]) * 4 + 50).clip(0, 100)
    spread_fill = spread.fillna(spread.median() if spread.notna().any() else 6.0)
    spread_score = (100 - spread_fill * 10).clip(0, 100)
    vol_fill = out["rolling_std_5"].fillna(out["rolling_std_5"].median() if out["rolling_std_5"].notna().any() else 0.0)
    vol_score = (100 - vol_fill * 12).clip(0, 100)
    level_score = series.clip(0, 100)

    out["solve_score"] = (
        level_score * 0.45
        + persistence * 0.20
        + spread_score * 0.15
        + momentum * 0.10
        + vol_score * 0.10
    ).clip(0, 100)
    return out

def compute_threshold_snapshot(df: pd.DataFrame, price_col: str, threshold: int, exit_threshold: int) -> dict[str, Any]:
    if df.empty or price_col not in df.columns:
        return {"crossed": False}
    data = df.sort_values("ts").reset_index(drop=True).copy()
    data[price_col] = pd.to_numeric(data[price_col], errors="coerce")
    data = data.dropna(subset=[price_col])
    if data.empty:
        return {"crossed": False}

    cross_mask = data[price_col] >= threshold
    if not cross_mask.any():
        return {"crossed": False, "latest": float(data[price_col].iloc[-1])}

    cross_idx = cross_mask[cross_mask].index[0]
    after = data.loc[cross_idx:].copy()
    if after.empty:
        return {"crossed": False}

    cross_row = after.iloc[0]
    cross_price = float(cross_row[price_col])
    min_after = float(after[price_col].min())
    max_after = float(after[price_col].max())
    last_price = float(after[price_col].iloc[-1])

    hit_exit_mask = after[price_col] <= exit_threshold
    hit_exit = bool(hit_exit_mask.any())
    first_exit_ts = after.loc[hit_exit_mask, "ts"].iloc[0] if hit_exit else None
    minutes_until_exit = None
    if first_exit_ts is not None:
        minutes_until_exit = (first_exit_ts - cross_row["ts"]).total_seconds() / 60.0

    observed_span = 0.0
    if len(after) > 1:
        observed_span = (after["ts"].iloc[-1] - after["ts"].iloc[0]).total_seconds() / 60.0

    return {
        "crossed": True,
        "cross_ts": cross_row["ts"],
        "cross_price": cross_price,
        "minutes_to_expiry_at_cross": cross_row.get("minutes_to_expiry"),
        "max_adverse_cents": max(cross_price - min_after, 0.0),
        "max_favorable_cents": max(max_after - cross_price, 0.0),
        "last_price": last_price,
        "return_to_last_pct": ((last_price - cross_price) / cross_price * 100.0) if cross_price else None,
        "pct_observations_above_threshold": after[price_col].ge(threshold).mean() * 100.0,
        "observed_minutes_after_cross": observed_span,
        "minutes_above_threshold_est": observed_span * after[price_col].ge(threshold).mean(),
        "hit_exit_after_cross": hit_exit,
        "minutes_until_exit": minutes_until_exit,
    }


def build_threshold_study(df: pd.DataFrame, price_col: str, threshold: int, exit_threshold: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if df.empty or price_col not in df.columns:
        return pd.DataFrame()

    for market, grp in df.groupby("market", sort=False):
        g = grp.sort_values("ts").copy()
        g[price_col] = pd.to_numeric(g[price_col], errors="coerce")
        g = g.dropna(subset=[price_col])
        if g.empty:
            continue
        snap = compute_threshold_snapshot(g, price_col, threshold, exit_threshold)
        if not snap.get("crossed"):
            continue
        rows.append(
            {
                "market": market,
                "cross_time": snap["cross_ts"],
                "ma_time": format_ma_time(snap["cross_ts"]),
                "minutes_to_expiry_at_cross": snap.get("minutes_to_expiry_at_cross"),
                "cross_price": snap.get("cross_price"),
                "max_adverse_cents": snap.get("max_adverse_cents"),
                "max_favorable_cents": snap.get("max_favorable_cents"),
                "last_price": snap.get("last_price"),
                "return_to_last_pct": snap.get("return_to_last_pct"),
                "pct_observations_above_threshold": snap.get("pct_observations_above_threshold"),
                "minutes_above_threshold_est": snap.get("minutes_above_threshold_est"),
                "hit_exit_after_cross": snap.get("hit_exit_after_cross"),
                "minutes_until_exit": snap.get("minutes_until_exit"),
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("cross_time", ascending=False)


def style_threshold_table(df: pd.DataFrame) -> object:
    styled_df = df.copy()
    for col in ["cross_price", "max_adverse_cents", "max_favorable_cents", "last_price"]:
        if col in styled_df.columns:
            styled_df[col] = styled_df[col].apply(format_cents)
    if "minutes_to_expiry_at_cross" in styled_df.columns:
        styled_df["minutes_to_expiry_at_cross"] = styled_df["minutes_to_expiry_at_cross"].apply(lambda v: "NA" if pd.isna(v) else f"{v:,.2f}m")
    if "return_to_last_pct" in styled_df.columns:
        styled_df["return_to_last_pct"] = styled_df["return_to_last_pct"].apply(format_pct)
    if "minutes_above_threshold_est" in styled_df.columns:
        styled_df["minutes_above_threshold_est"] = styled_df["minutes_above_threshold_est"].apply(lambda v: "NA" if pd.isna(v) else f"{v:,.2f}m")
    if "minutes_until_exit" in styled_df.columns:
        styled_df["minutes_until_exit"] = styled_df["minutes_until_exit"].apply(lambda v: "NA" if pd.isna(v) else f"{v:,.2f}m")
    if "pct_observations_above_threshold" in styled_df.columns:
        styled_df["pct_observations_above_threshold"] = styled_df["pct_observations_above_threshold"].apply(format_pct)
    if "hit_exit_after_cross" in styled_df.columns:
        styled_df["hit_exit_after_cross"] = styled_df["hit_exit_after_cross"].map({True: "Yes", False: "No"})

    def row_style(row: pd.Series) -> list[str]:
        ret_text = str(row.get("return_to_last_pct", "")).replace("%", "").replace(",", "")
        color = "rgba(0,196,106,0.18)"
        border = "rgba(0,196,106,0.35)"
        try:
            if float(ret_text) < 0:
                color = "rgba(255,77,79,0.18)"
                border = "rgba(255,77,79,0.35)"
        except Exception:
            pass
        return [f"background-color:{color}; border-bottom:1px solid {border}; color:#eef7ef;" for _ in row]

    return (
        styled_df.style
        .apply(row_style, axis=1)
        .set_properties(**{"white-space": "nowrap", "font-size": "14px"})
    )


def render_wins_losses(df: pd.DataFrame, max_rows: int = 80):
    if df.empty:
        st.info("No closed trades yet.")
        return

    closed = df[df["display_outcome"].isin(["win", "loss"])].copy()
    if closed.empty:
        st.info("No winning or losing trades yet.")
        return

    exit_ts = pd.to_datetime(closed.get("exit_ts"), errors="coerce")
    entry_ts = pd.to_datetime(closed.get("entry_ts"), errors="coerce")
    closed["__sort_time"] = exit_ts.where(exit_ts.notna(), entry_ts)

    closed = closed.sort_values(
        ["__sort_time", "market", "side"],
        ascending=[False, True, True],
        na_position="last",
    ).head(max_rows).copy()

    if "__sort_time" in closed.columns:
        closed = closed.sort_values(
            ["__sort_time", "market", "side"],
            ascending=[False, True, True],
            na_position="last",
        )

    closed["Time"] = closed["ma_time"]
    closed["Market"] = closed["market"].astype(str)
    closed["Side"] = closed["side"].astype(str).str.upper()
    closed["Entry"] = closed["entry_fill_cents_used"].apply(format_cents)
    closed["Exit"] = closed["exit_fill_cents_used"].apply(format_cents)
    closed["P and L %"] = closed["gross_pnl_percent"].apply(format_pct)
    closed["P and L $"] = closed["gross_pnl_dollars"].apply(format_money)

    cols = ["Time", "Market", "Side", "Entry", "Exit", "P and L %", "P and L $"]

    header_html = "".join(
        f'<th style="padding:8px 10px;text-align:left;background:#101814;color:#aab9ae;border-bottom:1px solid rgba(255,255,255,0.08);font-size:12px;font-weight:700;white-space:nowrap;">{html.escape(c)}</th>'
        for c in cols
    )

    row_html = []
    for _, row in closed.iterrows():
        pnl = float(row.get("gross_pnl_dollars") or 0)
        bg = "#13392a" if pnl >= 0 else "#3d171c"
        fg = "#f2fff6" if pnl >= 0 else "#fff5f5"
        edge = "rgba(0,196,106,0.45)" if pnl >= 0 else "rgba(255,90,95,0.45)"

        cells = []
        for c in cols:
            cells.append(
                f'<td style="padding:7px 10px;background:{bg};color:{fg};border-top:1px solid {edge};white-space:nowrap;font-size:12px;line-height:1.1;">{html.escape(str(row[c]))}</td>'
            )
        row_html.append(f"<tr>{''.join(cells)}</tr>")

    st.markdown(
        f'''
        <div style="width:100%;border:1px solid rgba(255,255,255,0.08);border-radius:22px;overflow:hidden;background:#08110e;margin-bottom:1.25rem;">
          <div style="padding:10px 14px;color:#9fb3a2;font-size:12px;border-bottom:1px solid rgba(255,255,255,0.06);">
            Massachusetts time | chronological order using exit time with entry time fallback | positive P and L counts as a win | negative P and L counts as a loss
          </div>
          <div style="overflow-x:auto;">
            <table style="width:100%;border-collapse:collapse;">
              <thead><tr>{header_html}</tr></thead>
              <tbody>{''.join(row_html)}</tbody>
            </table>
          </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )



@st.cache_data(ttl=30, show_spinner=False)
def load_full_price_series_for_markets(log_path: str, markets: tuple[str, ...]) -> pd.DataFrame:
    if not log_path or not markets:
        return pd.DataFrame(columns=["ts", "market", "yes_bid", "yes_ask", "no_bid", "no_ask"])
    wanted = {str(m).strip().upper() for m in markets if str(m).strip()}
    if not wanted:
        return pd.DataFrame(columns=["ts", "market", "yes_bid", "yes_ask", "no_bid", "no_ask"])
    p = Path(log_path)
    if not p.exists():
        return pd.DataFrame(columns=["ts", "market", "yes_bid", "yes_ask", "no_bid", "no_ask"])

    rows: list[dict[str, Any]] = []
    with p.open("r", encoding="utf-8", errors="ignore") as fh:
        for raw in fh:
            m = HEARTBEAT_RE.match(raw.strip())
            if not m:
                continue
            market = str(m.group("watch") or "").strip().upper()
            if market not in wanted:
                continue
            ts = parse_ts(m.group("ts"))
            if not ts:
                continue
            rows.append(
                {
                    "ts": ts,
                    "market": market,
                    "yes_bid": maybe_num(m.group("yes_bid")),
                    "yes_ask": maybe_num(m.group("yes_ask")),
                    "no_bid": maybe_num(m.group("no_bid")),
                    "no_ask": maybe_num(m.group("no_ask")),
                }
            )
    if not rows:
        return pd.DataFrame(columns=["ts", "market", "yes_bid", "yes_ask", "no_bid", "no_ask"])
    out = pd.DataFrame(rows).drop_duplicates(subset=["ts", "market"], keep="last").sort_values(["market", "ts"]).reset_index(drop=True)
    for col in ["yes_bid", "yes_ask", "no_bid", "no_ask"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


@st.cache_data(ttl=30, show_spinner=False)
def build_false_stop_proxy_df(price_df: pd.DataFrame, trades_df: pd.DataFrame, rebound_floor_cents: int = 90) -> pd.DataFrame:
    cols = [
        "market", "side", "entry_ts", "exit_ts", "entry_fill_cents_used", "exit_fill_cents_used",
        "drawdown_cents", "rebound_max_cents", "rebound_seconds", "is_false_stop_proxy",
    ]
    if price_df is None or price_df.empty or trades_df is None or trades_df.empty:
        return pd.DataFrame(columns=cols)

    prices = price_df.copy()
    prices["market"] = prices["market"].astype(str).str.strip().str.upper()
    prices["ts"] = pd.to_datetime(prices["ts"], errors="coerce")
    for col in ["yes_bid", "no_bid"]:
        if col in prices.columns:
            prices[col] = pd.to_numeric(prices[col], errors="coerce")
    prices = prices.dropna(subset=["market", "ts"]).sort_values(["market", "ts"]).reset_index(drop=True)
    if prices.empty:
        return pd.DataFrame(columns=cols)

    trades = trades_df.copy()
    if "display_outcome" not in trades.columns:
        trades = normalize_trades(trades)
    trades["market"] = trades["market"].astype(str).str.strip().str.upper()
    trades["side"] = trades["side"].astype(str).str.strip().str.lower()
    trades["entry_ts"] = pd.to_datetime(trades.get("entry_ts"), errors="coerce")
    trades["exit_ts"] = pd.to_datetime(trades.get("exit_ts"), errors="coerce")
    trades["entry_fill_cents_used"] = pd.to_numeric(trades.get("entry_fill_cents_used"), errors="coerce")
    trades["exit_fill_cents_used"] = pd.to_numeric(trades.get("exit_fill_cents_used"), errors="coerce")
    trades["gross_pnl_dollars"] = pd.to_numeric(trades.get("gross_pnl_dollars"), errors="coerce")
    trades = trades[
        trades["display_outcome"].astype(str).str.lower().eq("loss")
        & trades["exit_ts"].notna()
        & trades["entry_fill_cents_used"].notna()
        & trades["exit_fill_cents_used"].notna()
    ].copy()
    if trades.empty:
        return pd.DataFrame(columns=cols)

    grouped_prices = {market: grp.copy() for market, grp in prices.groupby("market", sort=False)}
    rows: list[dict[str, Any]] = []
    for _, trade in trades.iterrows():
        market = str(trade["market"])
        side = str(trade["side"])
        bid_col = "yes_bid" if side == "yes" else "no_bid"
        market_prices = grouped_prices.get(market)
        if market_prices is None or market_prices.empty or bid_col not in market_prices.columns:
            continue
        future = market_prices[market_prices["ts"] >= trade["exit_ts"]].copy()
        if future.empty:
            continue
        future[bid_col] = pd.to_numeric(future[bid_col], errors="coerce")
        future = future.dropna(subset=[bid_col])
        if future.empty:
            continue

        rebound_max = float(future[bid_col].max())
        rebound_idx = future[bid_col].idxmax()
        rebound_ts = future.loc[rebound_idx, "ts"] if rebound_idx in future.index else pd.NaT
        rebound_seconds = (rebound_ts - trade["exit_ts"]).total_seconds() if pd.notna(rebound_ts) else np.nan
        drawdown_cents = float(trade["entry_fill_cents_used"] - trade["exit_fill_cents_used"])
        rows.append(
            {
                "market": market,
                "side": side,
                "entry_ts": trade["entry_ts"],
                "exit_ts": trade["exit_ts"],
                "entry_fill_cents_used": float(trade["entry_fill_cents_used"]),
                "exit_fill_cents_used": float(trade["exit_fill_cents_used"]),
                "drawdown_cents": drawdown_cents,
                "rebound_max_cents": rebound_max,
                "rebound_seconds": float(rebound_seconds) if pd.notna(rebound_seconds) else np.nan,
                "is_false_stop_proxy": bool(rebound_max >= float(rebound_floor_cents)),
            }
        )

    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows).sort_values(["exit_ts", "market"]).reset_index(drop=True)


def render_visualizer_tab(trades_df: pd.DataFrame, active_dataset_tag: str, price_df: pd.DataFrame | None = None, log_path: str | None = None) -> None:
    if trades_df is None or trades_df.empty:
        st.markdown("## Visualizer")
        st.info("No scored trades are available yet for visualization.")
        return

    trades = trades_df.copy()
    if "display_outcome" not in trades.columns:
        trades = normalize_trades(trades, active_dataset_tag)
    if trades.empty:
        st.markdown("## Visualizer")
        st.info("No scored trades are available yet for visualization.")
        return

    trades["entry_ts"] = pd.to_datetime(trades.get("entry_ts"), errors="coerce")
    trades["exit_ts"] = pd.to_datetime(trades.get("exit_ts"), errors="coerce")
    trades["gross_pnl_dollars"] = pd.to_numeric(trades.get("gross_pnl_dollars"), errors="coerce")
    trades["gross_pnl_percent"] = pd.to_numeric(trades.get("gross_pnl_percent"), errors="coerce")
    trades["qty"] = pd.to_numeric(trades.get("qty"), errors="coerce")
    trades["hold_seconds"] = (trades["exit_ts"] - trades["entry_ts"]).dt.total_seconds()
    trades["sort_ts"] = trades["exit_ts"].where(trades["exit_ts"].notna(), trades["entry_ts"])
    trades = trades.sort_values(["sort_ts", "market"], na_position="last").reset_index(drop=True)
    trades["trade_index"] = np.arange(1, len(trades) + 1)
    trades["result_class"] = np.where(trades["gross_pnl_dollars"] > 0, "Win", np.where(trades["gross_pnl_dollars"] < 0, "Loss", "Open"))
    trades["color"] = trades["result_class"].map({"Win": "#00c46a", "Loss": "#ff5c5c", "Open": "#7d8f86"}).fillna("#7d8f86")
    closed = trades[trades["gross_pnl_dollars"].notna()].copy()

    total_trades = int(len(trades))
    win_count = int((trades["result_class"] == "Win").sum())
    loss_count = int((trades["result_class"] == "Loss").sum())
    open_count = int((trades["result_class"] == "Open").sum())
    win_rate = (win_count / max(win_count + loss_count, 1) * 100.0) if (win_count + loss_count) else 0.0
    total_pnl = float(closed["gross_pnl_dollars"].sum()) if not closed.empty else 0.0
    avg_pnl = float(closed["gross_pnl_dollars"].mean()) if not closed.empty else 0.0
    median_pnl = float(closed["gross_pnl_dollars"].median()) if not closed.empty else 0.0
    best_trade = float(closed["gross_pnl_dollars"].max()) if not closed.empty else 0.0
    worst_trade = float(closed["gross_pnl_dollars"].min()) if not closed.empty else 0.0

    streak_labels = trades["result_class"].replace({"Open": np.nan}).dropna().tolist()
    longest_win_streak = 0
    longest_loss_streak = 0
    current_label = None
    current_len = 0
    for label in streak_labels:
        if label == current_label:
            current_len += 1
        else:
            current_label = label
            current_len = 1
        if label == "Win":
            longest_win_streak = max(longest_win_streak, current_len)
        elif label == "Loss":
            longest_loss_streak = max(longest_loss_streak, current_len)

    st.markdown("## Visualizer")
    st.markdown(
        f"""
        <div class="visualizer-hero">
          <div class="visualizer-kicker">Trade Atlas</div>
          <div class="visualizer-title">Full-history trade visualizer</div>
          <div class="visualizer-sub">All logged trades for <strong>{html.escape(humanize_strategy_tag(active_dataset_tag))}</strong> rendered as stacked visual systems. Green marks profitable trades, red marks losing trades, and neutral gray marks unresolved or open rows.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="visualizer-strip">
          <div class="visualizer-chip"><div class="visualizer-chip-label">Trades logged</div><div class="visualizer-chip-value">{total_trades}</div><div class="visualizer-chip-note">{win_count} wins | {loss_count} losses | {open_count} open</div></div>
          <div class="visualizer-chip"><div class="visualizer-chip-label">Win rate</div><div class="visualizer-chip-value">{format_pct(win_rate)}</div><div class="visualizer-chip-note">Closed-trade only</div></div>
          <div class="visualizer-chip"><div class="visualizer-chip-label">Total P and L</div><div class="visualizer-chip-value">{format_money(total_pnl)}</div><div class="visualizer-chip-note">Gross dollars across closed trades</div></div>
          <div class="visualizer-chip"><div class="visualizer-chip-label">Average trade</div><div class="visualizer-chip-value">{format_money(avg_pnl)}</div><div class="visualizer-chip-note">Median {format_money(median_pnl)}</div></div>
          <div class="visualizer-chip"><div class="visualizer-chip-label">Best / worst</div><div class="visualizer-chip-value">{format_money(best_trade)}</div><div class="visualizer-chip-note">Worst {format_money(worst_trade)}</div></div>
          <div class="visualizer-chip"><div class="visualizer-chip-label">Streaks</div><div class="visualizer-chip-value">W {longest_win_streak} / L {longest_loss_streak}</div><div class="visualizer-chip-note">Longest closed-trade runs</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="visualizer-panel">', unsafe_allow_html=True)
    st.markdown('<div class="visualizer-section-title">Bell curves and danger bands</div><div class="visualizer-section-sub">This section is tuned for loss avoidance. The false-stop drawdown view is intentionally a smaller sample because it only counts losing exits that later rebounded to 90c or higher on the same-side bid. The curves are stacked vertically so each one has full width.</div>', unsafe_allow_html=True)
    if closed.empty or closed["gross_pnl_dollars"].dropna().empty:
        st.info("Not enough closed-trade P and L data yet.")
    else:
        loss_markets = tuple(sorted({str(m).strip().upper() for m in trades.loc[trades["gross_pnl_dollars"] < 0, "market"].dropna().tolist() if str(m).strip()}))
        proxy_price_df = price_df if price_df is not None else pd.DataFrame()
        if log_path and loss_markets:
            full_history_price_df = load_full_price_series_for_markets(log_path, loss_markets)
            if not full_history_price_df.empty:
                proxy_price_df = full_history_price_df
        false_stop_proxy = build_false_stop_proxy_df(proxy_price_df, trades, rebound_floor_cents=90)
        false_stop_drawdowns = false_stop_proxy[false_stop_proxy["is_false_stop_proxy"]].copy() if not false_stop_proxy.empty else pd.DataFrame()

        value_dollars = closed["gross_pnl_dollars"].dropna().to_numpy(dtype=float)
        hold_closed = pd.to_numeric(closed["hold_seconds"], errors="coerce").dropna()
        hold_minutes = (hold_closed / 60.0).to_numpy(dtype=float) if not hold_closed.empty else np.array([])
        proxy_drawdown_values = pd.to_numeric(false_stop_drawdowns.get("drawdown_cents"), errors="coerce").dropna().to_numpy(dtype=float) if not false_stop_drawdowns.empty else np.array([])
        bins_dollars = min(28, max(10, int(np.sqrt(len(value_dollars)) * 2)))
        bins_hold = min(24, max(8, int(np.sqrt(max(len(hold_minutes), 1)) * 2)))
        bins_proxy = min(18, max(6, int(np.sqrt(max(len(proxy_drawdown_values), 1)) * 2)))
        hist_edges = np.histogram(value_dollars, bins=bins_dollars)[1]
        mu = float(np.mean(value_dollars))
        sigma = float(np.std(value_dollars, ddof=0))

        loss_only = closed[closed["gross_pnl_dollars"] < 0]["gross_pnl_dollars"].dropna().to_numpy(dtype=float)
        loss_bucket_label = "NA"
        if len(loss_only) >= 2:
            loss_hist, loss_edges = np.histogram(loss_only, bins=min(10, max(4, len(np.unique(loss_only)))))
            if len(loss_hist):
                idx = int(np.argmax(loss_hist))
                loss_bucket_label = f"{format_money(loss_edges[idx])} to {format_money(loss_edges[idx + 1])}"

        hold_bucket_label = "NA"
        loss_holds = pd.to_numeric(closed.loc[closed["gross_pnl_dollars"] < 0, "hold_seconds"], errors="coerce").dropna() / 60.0
        if len(loss_holds) >= 2:
            hold_hist, hold_edges = np.histogram(loss_holds.to_numpy(dtype=float), bins=min(10, max(4, len(np.unique(loss_holds.round(2))))))
            if len(hold_hist):
                idx = int(np.argmax(hold_hist))
                hold_bucket_label = f"{hold_edges[idx]:.1f}m to {hold_edges[idx + 1]:.1f}m"

        proxy_bucket_label = "NA"
        if len(proxy_drawdown_values) >= 2:
            proxy_hist, proxy_edges = np.histogram(proxy_drawdown_values, bins=min(10, max(4, len(np.unique(proxy_drawdown_values.round(0))))))
            if len(proxy_hist):
                idx = int(np.argmax(proxy_hist))
                proxy_bucket_label = f"{proxy_edges[idx]:.0f}c to {proxy_edges[idx + 1]:.0f}c"

        fast_fail_pct = float(((pd.to_numeric(closed["hold_seconds"], errors="coerce") <= 90) & (closed["gross_pnl_dollars"] < 0)).mean() * 100.0)
        loss_median_hold = float((pd.to_numeric(closed.loc[closed["gross_pnl_dollars"] < 0, "hold_seconds"], errors="coerce") / 60.0).median()) if (closed["gross_pnl_dollars"] < 0).any() else np.nan
        win_median_hold = float((pd.to_numeric(closed.loc[closed["gross_pnl_dollars"] > 0, "hold_seconds"], errors="coerce") / 60.0).median()) if (closed["gross_pnl_dollars"] > 0).any() else np.nan
        proxy_avg_drawdown = float(np.mean(proxy_drawdown_values)) if len(proxy_drawdown_values) else np.nan
        proxy_median_drawdown = float(np.median(proxy_drawdown_values)) if len(proxy_drawdown_values) else np.nan
        proxy_min_drawdown = float(np.min(proxy_drawdown_values)) if len(proxy_drawdown_values) else np.nan
        proxy_rebound_minutes = float((pd.to_numeric(false_stop_drawdowns.get("rebound_seconds"), errors="coerce").dropna() / 60.0).median()) if not false_stop_drawdowns.empty else np.nan
        stop_loss_sample = int(len(false_stop_proxy)) if not false_stop_proxy.empty else 0

        st.markdown(
            f"""
            <div class="visualizer-strip" style="margin-top:0.1rem; margin-bottom:0.9rem;">
              <div class="visualizer-chip"><div class="visualizer-chip-label">Loss cluster</div><div class="visualizer-chip-value">{loss_bucket_label}</div><div class="visualizer-chip-note">Most crowded dollar-loss band</div></div>
              <div class="visualizer-chip"><div class="visualizer-chip-label">Fast-fail share</div><div class="visualizer-chip-value">{format_pct(fast_fail_pct)}</div><div class="visualizer-chip-note">Closed trades that lost within 90s</div></div>
              <div class="visualizer-chip"><div class="visualizer-chip-label">Loss hold cluster</div><div class="visualizer-chip-value">{hold_bucket_label}</div><div class="visualizer-chip-note">Where losing durations pile up</div></div>
              <div class="visualizer-chip"><div class="visualizer-chip-label">False-stop drawdown</div><div class="visualizer-chip-value">{'NA' if pd.isna(proxy_avg_drawdown) else f'{proxy_avg_drawdown:.1f}c'}</div><div class="visualizer-chip-note">Median {'NA' if pd.isna(proxy_median_drawdown) else f'{proxy_median_drawdown:.1f}c'} | shallowest {'NA' if pd.isna(proxy_min_drawdown) else f'{proxy_min_drawdown:.0f}c'}</div></div>
              <div class="visualizer-chip"><div class="visualizer-chip-label">Proxy sample</div><div class="visualizer-chip-value">{len(false_stop_drawdowns):,}</div><div class="visualizer-chip-note">From {stop_loss_sample:,} stop losses | cluster {proxy_bucket_label}</div></div>
              <div class="visualizer-chip"><div class="visualizer-chip-label">Median loss hold</div><div class="visualizer-chip-value">{'NA' if pd.isna(loss_median_hold) else f'{loss_median_hold:.1f}m'}</div><div class="visualizer-chip-note">Median win {'NA' if pd.isna(win_median_hold) else f'{win_median_hold:.1f}m'} | rebound {'NA' if pd.isna(proxy_rebound_minutes) else f'{proxy_rebound_minutes:.1f}m'}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        fig_curve = make_subplots(rows=3, cols=1, vertical_spacing=0.12, subplot_titles=("Dollar outcome distribution", "Hold duration distribution", "False-stop drawdown distribution"))
        fig_curve.add_vrect(x0=min(0.0, float(np.min(value_dollars))), x1=0, fillcolor="rgba(255,92,92,0.10)", line_width=0, row=1, col=1)
        fig_curve.add_vrect(x0=0, x1=max(0.0, float(np.max(value_dollars))), fillcolor="rgba(0,196,106,0.08)", line_width=0, row=1, col=1)
        fig_curve.add_vrect(x0=0, x1=max(float(np.max(proxy_drawdown_values)), 0.0) if len(proxy_drawdown_values) else 1.0, fillcolor="rgba(255,92,92,0.09)", line_width=0, row=3, col=1)
        for series, bins, col_idx, prefix, suffix, label, color in [
            (closed.loc[closed["gross_pnl_dollars"] >= 0, "gross_pnl_dollars"], bins_dollars, 1, "$", "", "Wins", "rgba(0,196,106,0.76)"),
            (closed.loc[closed["gross_pnl_dollars"] < 0, "gross_pnl_dollars"], bins_dollars, 1, "$", "", "Losses", "rgba(255,92,92,0.76)"),
            ((pd.to_numeric(closed.loc[closed["gross_pnl_dollars"] >= 0, "hold_seconds"], errors="coerce") / 60.0), bins_hold, 2, "", "m", "Wins", "rgba(0,196,106,0.76)"),
            ((pd.to_numeric(closed.loc[closed["gross_pnl_dollars"] < 0, "hold_seconds"], errors="coerce") / 60.0), bins_hold, 2, "", "m", "Losses", "rgba(255,92,92,0.76)"),
        ]:
            clean = pd.to_numeric(series, errors="coerce").dropna()
            if clean.empty:
                continue
            fig_curve.add_trace(
                go.Histogram(
                    x=clean,
                    nbinsx=bins,
                    name=label,
                    marker=dict(color=color, line=dict(color="#e9f3ec" if label == "Wins" else "#ffd7d7", width=1)),
                    opacity=0.82,
                    legendgroup=label,
                    showlegend=(col_idx == 1),
                    hovertemplate=f"{label}<br>{prefix}%{{x:.2f}}{suffix}<br>Count %{{y}}<extra></extra>",
                ),
                row=col_idx,
                col=1,
            )
        if len(proxy_drawdown_values):
            fig_curve.add_trace(
                go.Histogram(
                    x=proxy_drawdown_values,
                    nbinsx=bins_proxy,
                    name="False-stop proxy",
                    marker=dict(color="rgba(255,140,140,0.82)", line=dict(color="#ffe5e5", width=1.1)),
                    opacity=0.9,
                    legendgroup="False-stop proxy",
                    showlegend=True,
                    hovertemplate="False-stop proxy<br>%{x:.1f}c drawdown<br>Count %{y}<extra></extra>",
                ),
                row=3,
                col=1,
            )
        if sigma > 0:
            x_line = np.linspace(float(hist_edges[0]), float(hist_edges[-1]), 240)
            bin_width = float(hist_edges[1] - hist_edges[0]) if len(hist_edges) > 1 else 1.0
            y_line = (1.0 / (sigma * np.sqrt(2.0 * np.pi))) * np.exp(-0.5 * ((x_line - mu) / sigma) ** 2)
            y_line = y_line * len(value_dollars) * bin_width
            fig_curve.add_trace(
                go.Scatter(
                    x=x_line,
                    y=y_line,
                    mode="lines",
                    name="Bell curve",
                    line=dict(color="#d8e6dc", width=3),
                    hovertemplate="Curve<br>$%{x:.2f}<br>%{y:.2f} est count<extra></extra>",
                ),
                row=1,
                col=1,
            )
        if len(proxy_drawdown_values) >= 2:
            proxy_mu = float(np.mean(proxy_drawdown_values))
            proxy_sigma = float(np.std(proxy_drawdown_values, ddof=0))
            proxy_edges = np.histogram(proxy_drawdown_values, bins=bins_proxy)[1]
            if proxy_sigma > 0:
                proxy_x = np.linspace(float(proxy_edges[0]), float(proxy_edges[-1]), 180)
                proxy_width = float(proxy_edges[1] - proxy_edges[0]) if len(proxy_edges) > 1 else 1.0
                proxy_y = (1.0 / (proxy_sigma * np.sqrt(2.0 * np.pi))) * np.exp(-0.5 * ((proxy_x - proxy_mu) / proxy_sigma) ** 2)
                proxy_y = proxy_y * len(proxy_drawdown_values) * proxy_width
                fig_curve.add_trace(
                    go.Scatter(
                        x=proxy_x,
                        y=proxy_y,
                        mode="lines",
                        name="False-stop curve",
                        line=dict(color="#ffd1d1", width=3),
                        hovertemplate="Proxy curve<br>%{x:.1f}c<br>%{y:.2f} est count<extra></extra>",
                    ),
                    row=3,
                    col=1,
                )
        fig_curve.add_vline(x=mu, line_dash="dash", line_color="#d8e6dc", line_width=1.5, row=1, col=1)
        if len(loss_holds):
            fig_curve.add_vline(x=float(loss_holds.median()), line_dash="dot", line_color="#ff9d9d", line_width=1.5, row=2, col=1)
        if len(proxy_drawdown_values):
            fig_curve.add_vline(x=float(np.mean(proxy_drawdown_values)), line_dash="dash", line_color="#ffe2e2", line_width=1.5, row=3, col=1)
            fig_curve.add_vline(x=float(np.median(proxy_drawdown_values)), line_dash="dot", line_color="#ffb2b2", line_width=1.5, row=3, col=1)
        else:
            fig_curve.add_annotation(
                text="No proxy false stops yet",
                x=0.5,
                y=0.5,
                xref="x3 domain",
                yref="y3 domain",
                showarrow=False,
                font=dict(color="#b8c8bd", size=13),
            )
        fig_curve.update_layout(
            barmode="overlay",
            height=980,
            margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", x=0, y=1.14),
            uirevision=f"visual-bell-{active_dataset_tag}",
        )
        fig_curve.update_xaxes(title_text="Gross P and L ($)", row=1, col=1)
        fig_curve.update_yaxes(title_text="Trade count", row=1, col=1)
        fig_curve.update_xaxes(title_text="Hold duration (minutes)", row=2, col=1)
        fig_curve.update_yaxes(title_text="Trade count", row=2, col=1)
        fig_curve.update_xaxes(title_text="Drawdown from entry to stop fill (cents)", row=3, col=1)
        fig_curve.update_yaxes(title_text="Proxy false-stop count", row=3, col=1)
        st.plotly_chart(fig_curve, width="stretch", key=f"visual-bell-{active_dataset_tag}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="visualizer-panel">', unsafe_allow_html=True)
    st.markdown('<div class="visualizer-section-title">Trade mosaic</div><div class="visualizer-section-sub">Each square is one logged trade. Read left to right, top to bottom across the full history. Bigger datasets naturally extend downward so the page becomes a complete visual archive.</div>', unsafe_allow_html=True)
    grid = trades.copy()
    grid_cols = 14
    grid["grid_col"] = grid.index % grid_cols
    grid["grid_row"] = grid.index // grid_cols
    grid["hover_text"] = grid.apply(
        lambda row: (
            f"#{int(row['trade_index'])}<br>{html.escape(str(row.get('market', 'NA')))}<br>"
            f"{str(row.get('side', 'NA')).upper()} | qty {int(row['qty']) if pd.notna(row['qty']) else 'NA'}<br>"
            f"Entry {format_cents(row.get('entry_fill_cents_used'))} | Exit {format_cents(row.get('exit_fill_cents_used'))}<br>"
            f"P and L {format_money(row.get('gross_pnl_dollars'))} | {format_pct(row.get('gross_pnl_percent'))}<br>{html.escape(str(row.get('result_class', 'NA')))}"
        ),
        axis=1,
    )
    fig_grid = go.Figure()
    for label, color in [("Win", "#00c46a"), ("Loss", "#ff5c5c"), ("Open", "#7d8f86")]:
        sample = grid[grid["result_class"] == label].copy()
        if sample.empty:
            continue
        fig_grid.add_trace(go.Scatter(
            x=sample["grid_col"],
            y=-sample["grid_row"],
            mode="markers",
            name=label,
            marker=dict(symbol="square", size=24, color=color, line=dict(color="rgba(255,255,255,0.14)", width=1.2)),
            customdata=sample[["hover_text"]],
            hovertemplate="%{customdata[0]}<extra></extra>",
        ))
    fig_grid.update_layout(
        height=max(340, 136 + ((len(grid) // grid_cols) + 1) * 30),
        margin=dict(l=10, r=10, t=18, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", x=0, y=1.08),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
        uirevision=f"visual-grid-{active_dataset_tag}",
    )
    st.plotly_chart(fig_grid, width="stretch", key=f"visual-grid-{active_dataset_tag}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="visualizer-panel">', unsafe_allow_html=True)
    st.markdown('<div class="visualizer-section-title">Timeline and equity path</div><div class="visualizer-section-sub">The top chart shows every trade as a sized marker by quantity. The lower chart rolls those same results into cumulative equity so regime shifts and drawdowns are easier to spot.</div>', unsafe_allow_html=True)
    timeline = trades.dropna(subset=["sort_ts"]).copy()
    if timeline.empty:
        st.info("No dated trades are available yet.")
    else:
        timeline["closed_pnl"] = timeline["gross_pnl_dollars"].fillna(0.0)
        timeline["equity"] = timeline["closed_pnl"].cumsum()
        fig_timeline = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, subplot_titles=("Trade outcomes", "Cumulative equity"))
        for label, color in [("Win", "#00c46a"), ("Loss", "#ff5c5c"), ("Open", "#7d8f86")]:
            sample = timeline[timeline["result_class"] == label].copy()
            if sample.empty:
                continue
            fig_timeline.add_trace(
                go.Scatter(
                    x=sample["sort_ts"],
                    y=sample["gross_pnl_dollars"].fillna(0.0),
                    mode="markers",
                    name=label,
                    marker=dict(size=np.clip(sample["qty"].fillna(1.0) * 1.9 + 6, 8, 26), color=color, line=dict(color="rgba(255,255,255,0.16)", width=1)),
                    customdata=sample[["market", "side", "qty", "gross_pnl_percent"]],
                    hovertemplate="%{x}<br>%{customdata[0]}<br>%{customdata[1]} qty %{customdata[2]}<br>P and L $%{y:.2f}<br>P and L %{customdata[3]:.2f}%<extra></extra>",
                    showlegend=True,
                ),
                row=1,
                col=1,
            )
        fig_timeline.add_trace(
            go.Scatter(
                x=timeline["sort_ts"],
                y=timeline["equity"],
                mode="lines+markers",
                name="Equity",
                line=dict(color="#d8e6dc", width=3),
                marker=dict(size=6, color="#7bd4ff"),
                hovertemplate="%{x}<br>Equity $%{y:.2f}<extra></extra>",
                showlegend=True,
            ),
            row=2,
            col=1,
        )
        fig_timeline.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.18)", row=1, col=1)
        fig_timeline.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.18)", row=2, col=1)
        fig_timeline.update_layout(
            height=560,
            margin=dict(l=10, r=10, t=42, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", x=0, y=1.08),
            uirevision=f"visual-timeline-{active_dataset_tag}",
        )
        fig_timeline.update_yaxes(title_text="Gross P and L ($)", row=1, col=1)
        fig_timeline.update_yaxes(title_text="Cumulative equity ($)", row=2, col=1)
        fig_timeline.update_xaxes(title_text="Trade time", row=2, col=1)
        st.plotly_chart(fig_timeline, width="stretch", key=f"visual-timeline-{active_dataset_tag}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="visualizer-panel">', unsafe_allow_html=True)
    st.markdown('<div class="visualizer-section-title">Temporal heatmaps</div><div class="visualizer-section-sub">Two dense heatmaps show when the trade log clusters and where wins or losses pile up. The left grid is by day and hour. The right grid compresses the history into weekday versus hour for pattern recognition.</div>', unsafe_allow_html=True)
    heat = trades.dropna(subset=["entry_ts"]).copy()
    if heat.empty:
        st.info("No timestamped trades are available yet.")
    else:
        heat["day"] = heat["entry_ts"].dt.strftime("%Y-%m-%d")
        heat["hour"] = heat["entry_ts"].dt.hour
        heat["weekday"] = heat["entry_ts"].dt.day_name().str.slice(0, 3)
        weekday_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        heat["weekday"] = pd.Categorical(heat["weekday"], categories=weekday_order, ordered=True)
        heat["signed_outcome"] = np.where(heat["gross_pnl_dollars"] > 0, 1, np.where(heat["gross_pnl_dollars"] < 0, -1, 0))
        pivot_day = heat.pivot_table(
            index="day",
            columns="hour",
            values="signed_outcome",
            aggfunc="sum",
            fill_value=0,
            observed=False,
        ).sort_index()
        pivot_weekday = heat.pivot_table(
            index="weekday",
            columns="hour",
            values="signed_outcome",
            aggfunc="sum",
            fill_value=0,
            observed=False,
        ).sort_index()
        fig_heat = make_subplots(rows=1, cols=2, subplot_titles=("Day x hour", "Weekday x hour"), horizontal_spacing=0.08)
        colorscale = [
            [0.0, "#5a1f28"],
            [0.35, "#ff5c5c"],
            [0.5, "#1f2623"],
            [0.65, "#1d6d47"],
            [1.0, "#00c46a"],
        ]
        fig_heat.add_trace(
            go.Heatmap(
                z=pivot_day.to_numpy(dtype=float),
                x=[f"{int(col):02d}:00" for col in pivot_day.columns],
                y=pivot_day.index.tolist(),
                colorscale=colorscale,
                zmid=0,
                colorbar=dict(title="Net wins"),
                hovertemplate="Day %{y}<br>Hour %{x}<br>Net win-loss score %{z}<extra></extra>",
            ),
            row=1,
            col=1,
        )
        fig_heat.add_trace(
            go.Heatmap(
                z=pivot_weekday.to_numpy(dtype=float),
                x=[f"{int(col):02d}:00" for col in pivot_weekday.columns],
                y=[str(v) for v in pivot_weekday.index.tolist()],
                colorscale=colorscale,
                zmid=0,
                showscale=False,
                hovertemplate="Weekday %{y}<br>Hour %{x}<br>Net win-loss score %{z}<extra></extra>",
            ),
            row=1,
            col=2,
        )
        fig_heat.update_layout(
            height=max(380, 190 + max(len(pivot_day.index), len(pivot_weekday.index)) * 24),
            margin=dict(l=10, r=10, t=42, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            uirevision=f"visual-heat-{active_dataset_tag}",
        )
        fig_heat.update_xaxes(title_text="Entry hour", row=1, col=1)
        fig_heat.update_xaxes(title_text="Entry hour", row=1, col=2)
        fig_heat.update_yaxes(title_text="Entry day", row=1, col=1)
        fig_heat.update_yaxes(title_text="Weekday", row=1, col=2)
        st.plotly_chart(fig_heat, width="stretch", key=f"visual-heat-{active_dataset_tag}")
    st.markdown('</div>', unsafe_allow_html=True)

def get_today_bounds_ma() -> tuple[datetime, datetime]:
    now_ma = datetime.now(MA_TZ)
    start_ma = now_ma.replace(hour=0, minute=0, second=0, microsecond=0)
    return start_ma, now_ma


def get_day_bounds_ma(days_ago: int = 0) -> tuple[datetime, datetime]:
    today_start, _ = get_today_bounds_ma()
    start_ma = today_start - pd.Timedelta(days=days_ago)
    end_ma = start_ma + pd.Timedelta(days=1)
    return start_ma, end_ma


def ensure_ma_naive_datetime(value: Any) -> datetime | None:
    dt = ensure_ma_datetime(value)
    if not dt:
        return None
    return dt.replace(tzinfo=None)


def parse_market_close_from_ticker(market: str) -> datetime | None:
    market_text = str(market or "").strip().upper()
    m = MARKET_TICKER_RE.match(market_text)
    if not m:
        return None
    month = MONTH_ABBR_TO_NUM.get(m.group("mon"))
    if not month:
        return None
    try:
        dt = datetime(
            2000 + int(m.group("yy")),
            month,
            int(m.group("day")),
            int(m.group("hour")),
            int(m.group("minute")),
            tzinfo=MA_TZ,
        )
    except Exception:
        return None
    return dt.replace(tzinfo=None)


def build_market_close_lookup(market_results_df: pd.DataFrame) -> dict[str, datetime]:
    lookup: dict[str, datetime] = {}
    if market_results_df is None or market_results_df.empty or "market" not in market_results_df.columns:
        return lookup
    local = market_results_df.copy()
    for _, row in local.iterrows():
        market = str(row.get("market", "")).strip().upper()
        if not market:
            continue
        close_dt = None
        for col in ["close_time", "watch_close_time", "close_time_dt"]:
            if col not in row.index:
                continue
            close_dt = ensure_ma_naive_datetime(row.get(col))
            if close_dt is not None:
                break
        if close_dt is not None:
            lookup[market] = close_dt
    return lookup


def infer_history_start_ma(trades_df: pd.DataFrame, market_results_df: pd.DataFrame) -> datetime:
    candidates: list[datetime] = []
    for df, cols in [
        (trades_df, ["entry_ts", "exit_ts"]),
        (market_results_df, ["close_time_dt", "close_time", "watch_close_time"]),
    ]:
        if df is None or df.empty:
            continue
        for col in cols:
            if col not in df.columns:
                continue
            ts = pd.to_datetime(df[col], errors="coerce").dropna()
            if len(ts):
                first_ts = pd.Timestamp(ts.min()).to_pydatetime()
                if first_ts.tzinfo is None:
                    first_ts = first_ts.replace(tzinfo=MA_TZ)
                else:
                    first_ts = first_ts.astimezone(MA_TZ)
                candidates.append(first_ts)
                break
    if candidates:
        first = min(candidates)
        return first.replace(hour=0, minute=0, second=0, microsecond=0)
    today_start, _ = get_today_bounds_ma()
    return today_start - pd.Timedelta(days=7)


def choose_btc_interval(start_ma: datetime, end_ma: datetime) -> str:
    span_hours = max((end_ma - start_ma).total_seconds() / 3600.0, 0.0)
    if span_hours <= 48:
        return "5m"
    if span_hours <= 168:
        return "15m"
    if span_hours <= 1440:
        return "1h"
    if span_hours <= 4320:
        return "4h"
    return "1d"


def normalize_btc_map_range(value: Any) -> str:
    selection = str(value or "").strip().lower()
    if selection in BTC_MAP_RANGE_OPTIONS:
        return selection
    return "today"


@st.cache_data(ttl=90, show_spinner=False)
def load_btc_intraday_range(start_ma: datetime, end_ma: datetime, interval: str = "5m") -> tuple[pd.DataFrame, str, str]:
    start_utc_ms = int(start_ma.astimezone(ZoneInfo("UTC")).timestamp() * 1000)
    end_utc_ms = int(end_ma.astimezone(ZoneInfo("UTC")).timestamp() * 1000)
    start_local_naive = start_ma.replace(tzinfo=None)
    end_local_naive = end_ma.replace(tzinfo=None)

    interval_minutes_map = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}
    binance_error = ""
    try:
        resp = requests.get(
            "https://data-api.binance.vision/api/v3/klines",
            params={
                "symbol": "BTCUSDT",
                "interval": interval,
                "startTime": start_utc_ms,
                "endTime": end_utc_ms,
                "limit": 1000,
            },
            timeout=12,
        )
        resp.raise_for_status()
        raw = resp.json()
        if isinstance(raw, list) and raw:
            rows = []
            for item in raw:
                close_ts = pd.to_datetime(int(item[6]), unit="ms", utc=True).tz_convert(MA_TZ).tz_localize(None)
                rows.append(
                    {
                        "ts": close_ts,
                        "open": float(item[1]),
                        "high": float(item[2]),
                        "low": float(item[3]),
                        "close": float(item[4]),
                        "volume": float(item[5]),
                    }
                )
            df = pd.DataFrame(rows).drop_duplicates(subset=["ts"]).sort_values("ts")
            df = df[(df["ts"] >= start_local_naive) & (df["ts"] <= end_local_naive)].reset_index(drop=True)
            if not df.empty:
                return df, "Binance public market data", ""
        binance_error = f"Binance returned no BTC candles for the requested range using interval {interval}."
    except Exception as exc:
        binance_error = f"Binance fetch failed: {exc}"

    kraken_interval = interval_minutes_map.get(interval, 5)
    try:
        resp = requests.get(
            "https://api.kraken.com/0/public/OHLC",
            params={
                "pair": "XBTUSD",
                "interval": kraken_interval,
                "since": int((start_ma - pd.Timedelta(minutes=kraken_interval)).astimezone(ZoneInfo("UTC")).timestamp()),
            },
            timeout=12,
        )
        resp.raise_for_status()
        payload = resp.json()
        errors = payload.get("error") or []
        if errors:
            raise RuntimeError("; ".join(str(x) for x in errors))
        result = payload.get("result") or {}
        pair_key = next((k for k in result.keys() if k != "last"), None)
        raw = result.get(pair_key or "", [])
        rows = []
        for item in raw:
            close_ts = pd.to_datetime(int(item[0]) + kraken_interval * 60, unit="s", utc=True).tz_convert(MA_TZ).tz_localize(None)
            rows.append(
                {
                    "ts": close_ts,
                    "open": float(item[1]),
                    "high": float(item[2]),
                    "low": float(item[3]),
                    "close": float(item[4]),
                    "volume": float(item[6]),
                }
            )
        df = pd.DataFrame(rows).drop_duplicates(subset=["ts"]).sort_values("ts")
        df = df[(df["ts"] >= start_local_naive) & (df["ts"] <= end_local_naive)].reset_index(drop=True)
        if not df.empty:
            note = f"Kraken fallback used. {binance_error}" if binance_error else "Kraken fallback used."
            return df, "Kraken public OHLC", note
        raise RuntimeError("Kraken returned no BTC candles for the requested range.")
    except Exception as exc:
        note = f"{binance_error} Kraken fetch failed: {exc}".strip()
        empty = pd.DataFrame(columns=["ts", "open", "high", "low", "close", "volume"])
        return empty, "", note


def build_trade_segments_for_window(trades_df: pd.DataFrame, market_results_df: pd.DataFrame, window_start_ma: datetime, window_end_ma: datetime) -> pd.DataFrame:
    cols = [
        "market", "side", "outcome", "gross_pnl_dollars", "segment_start", "segment_end",
        "plot_start", "plot_end", "color", "resolution_label", "display_outcome",
    ]
    if trades_df.empty or "market" not in trades_df.columns:
        return pd.DataFrame(columns=cols)

    working = trades_df.copy()
    if "display_outcome" not in working.columns:
        working = normalize_trades(working)

    window_start = window_start_ma.replace(tzinfo=None)
    window_end = window_end_ma.replace(tzinfo=None)
    close_lookup = build_market_close_lookup(market_results_df)

    rows: list[dict[str, Any]] = []
    for _, row in working.iterrows():
        market = str(row.get("market", "")).strip().upper()
        if not market:
            continue

        close_dt = close_lookup.get(market) or parse_market_close_from_ticker(market)
        if close_dt is None:
            continue

        segment_start = close_dt - pd.Timedelta(minutes=15)
        segment_end = close_dt
        plot_start = max(segment_start, window_start)
        plot_end = min(segment_end, window_end)
        if plot_end <= window_start or plot_start >= window_end or plot_end <= plot_start:
            continue

        gross_pnl = pd.to_numeric(pd.Series([row.get("gross_pnl_dollars")]), errors="coerce").iloc[0]
        display_outcome = str(row.get("display_outcome", row.get("outcome", "")) or "").strip().lower()
        if display_outcome not in {"win", "loss"} and pd.notna(gross_pnl):
            if gross_pnl > 0:
                display_outcome = "win"
            elif gross_pnl < 0:
                display_outcome = "loss"

        if display_outcome not in {"win", "loss"}:
            continue

        rows.append(
            {
                "market": market,
                "side": str(row.get("side", "")).strip().lower(),
                "outcome": display_outcome,
                "display_outcome": display_outcome,
                "gross_pnl_dollars": gross_pnl,
                "segment_start": segment_start,
                "segment_end": segment_end,
                "plot_start": plot_start,
                "plot_end": plot_end,
                "color": "#00c46a" if display_outcome == "win" else "#ff4d4f",
                "resolution_label": str(row.get("resolved_market_result_label", row.get("market_result", "")) or "").strip().upper() or "NA",
            }
        )

    if not rows:
        return pd.DataFrame(columns=cols)

    out = pd.DataFrame(rows).drop_duplicates(subset=["market"], keep="last").sort_values("segment_start").reset_index(drop=True)
    return out


def _extract_segment_points(btc_df: pd.DataFrame, plot_start: datetime, plot_end: datetime) -> pd.DataFrame:
    if btc_df.empty or "ts" not in btc_df.columns:
        return pd.DataFrame(columns=btc_df.columns)

    work = btc_df.copy()
    work["ts"] = pd.to_datetime(work["ts"], errors="coerce")
    work = work.dropna(subset=["ts"]).sort_values("ts").reset_index(drop=True)
    if work.empty:
        return work

    start_ts = pd.Timestamp(plot_start)
    end_ts = pd.Timestamp(plot_end)
    seg = work[(work["ts"] >= start_ts) & (work["ts"] <= end_ts)].copy()
    if len(seg) >= 2:
        return seg

    ts_index = pd.DatetimeIndex(work["ts"])
    left_idx = max(int(ts_index.searchsorted(start_ts, side="left")) - 1, 0)
    right_idx = min(int(ts_index.searchsorted(end_ts, side="right")), len(work))
    if right_idx - left_idx < 2:
        left_idx = max(left_idx - 1, 0)
        right_idx = min(right_idx + 1, len(work))
    return work.iloc[left_idx:right_idx].copy()


def build_btc_trade_map_figure(btc_df: pd.DataFrame, segments_df: pd.DataFrame, base_name: str, height: int = 560) -> go.Figure:
    work_btc = btc_df.copy()
    if "ts" in work_btc.columns:
        work_btc["ts"] = pd.to_datetime(work_btc["ts"], errors="coerce")
        work_btc = work_btc.dropna(subset=["ts"]).sort_values("ts").reset_index(drop=True)

    wins = int((segments_df["outcome"] == "win").sum()) if not segments_df.empty else 0
    losses = int((segments_df["outcome"] == "loss").sum()) if not segments_df.empty else 0

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=work_btc["ts"],
            y=work_btc["close"],
            mode="lines",
            name=base_name,
            line=dict(width=2.6, color="rgba(210,220,214,0.55)"),
            hovertemplate="%{x|%Y-%m-%d %I:%M %p}<br>BTC $%{y:,.2f}<extra></extra>",
        )
    )

    if wins:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="Win segment", line=dict(width=6, color="#00c46a")))
    if losses:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="Loss segment", line=dict(width=6, color="#ff4d4f")))
    if not segments_df.empty:
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                name="Trade window start",
                marker=dict(symbol="circle-open", size=10, color="#d7fce8", line=dict(width=2, color="#d7fce8")),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                name="Trade window end",
                marker=dict(symbol="diamond", size=9, color="#fff1a8", line=dict(width=1, color="#181818")),
            )
        )

    for _, seg_row in segments_df.iterrows():
        seg = _extract_segment_points(work_btc, seg_row["plot_start"], seg_row["plot_end"])
        if len(seg) < 2:
            continue

        side_text = str(seg_row.get("side", "")).upper() or "TRADE"
        pnl_text = format_money(seg_row.get("gross_pnl_dollars"))
        hover_text = (
            f"{seg_row['market']}<br>"
            f"{side_text} | {str(seg_row['outcome']).upper()}<br>"
            f"P and L {pnl_text}<br>"
            f"Window {seg_row['segment_start'].strftime('%Y-%m-%d %I:%M %p')} to {seg_row['segment_end'].strftime('%Y-%m-%d %I:%M %p')} ET"
        )

        fig.add_trace(
            go.Scatter(
                x=seg["ts"],
                y=seg["close"],
                mode="lines",
                name=seg_row["market"],
                showlegend=False,
                line=dict(width=6, color=seg_row["color"]),
                text=[hover_text] * len(seg),
                hovertemplate="%{text}<br>BTC $%{y:,.2f}<extra></extra>",
            )
        )
        start_point = seg.iloc[0]
        end_point = seg.iloc[-1]
        fig.add_trace(
            go.Scatter(
                x=[start_point["ts"]],
                y=[start_point["close"]],
                mode="markers",
                name=f"{seg_row['market']} start",
                showlegend=False,
                marker=dict(symbol="circle-open", size=10, color=seg_row["color"], line=dict(width=2, color=seg_row["color"])),
                text=[hover_text + "<br>Marker: window start"],
                hovertemplate="%{text}<br>BTC $%{y:,.2f}<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[end_point["ts"]],
                y=[end_point["close"]],
                mode="markers",
                name=f"{seg_row['market']} end",
                showlegend=False,
                marker=dict(symbol="diamond", size=9, color=seg_row["color"], line=dict(width=1, color="#0a0f0d")),
                text=[hover_text + "<br>Marker: window end"],
                hovertemplate="%{text}<br>BTC $%{y:,.2f}<extra></extra>",
            )
        )

    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.08, x=0, bgcolor="rgba(0,0,0,0)", itemsizing="constant"),
        yaxis_title="BTC price in USD",
        xaxis_title=None,
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
    return fig


def _btc_range_config(selection: str, trades_df: pd.DataFrame, market_results_df: pd.DataFrame) -> tuple[str, str, datetime, datetime, str]:
    selection = normalize_btc_map_range(selection)
    now_ma = datetime.now(MA_TZ)
    today_start, _ = get_today_bounds_ma()
    yesterday_start, _ = get_day_bounds_ma(days_ago=1)

    if selection == "yday_today":
        return (
            "Yesterday and today",
            "Full yesterday plus today so far in Eastern Time.",
            yesterday_start,
            now_ma,
            "5m",
        )
    if selection == "week":
        return (
            "Week chart",
            "Trailing seven day BTC map with your traded 15 minute windows painted over the curve.",
            now_ma - pd.Timedelta(days=7),
            now_ma,
            "15m",
        )
    if selection == "all":
        history_start = infer_history_start_ma(trades_df, market_results_df)
        interval = choose_btc_interval(history_start, now_ma)
        return (
            "All time",
            "All available bot trading history. This starts from the earliest trade or market result in your local stats files.",
            history_start,
            now_ma,
            interval,
        )
    return (
        "Today chart",
        "Today only in Eastern Time.",
        today_start,
        now_ma,
        "5m",
    )


def render_btc_day_map_tab(trades_df: pd.DataFrame, market_results_df: pd.DataFrame) -> None:
    st.markdown("## BTC trade map")
    st.caption("Switch the BTC chart range to review where your traded 15 minute markets sat on the BTC curve. Resolved wins are painted green and losses are painted red.")

    if "btc_map_range" not in st.session_state:
        st.session_state["btc_map_range"] = "today"
    st.session_state["btc_map_range"] = normalize_btc_map_range(st.session_state.get("btc_map_range"))
    st.radio(
        "BTC map range",
        options=BTC_MAP_RANGE_OPTIONS,
        key="btc_map_range",
        horizontal=True,
        label_visibility="collapsed",
        format_func=lambda value: BTC_MAP_RANGE_LABELS.get(value, str(value)),
    )

    work_trades = trades_df.copy()
    if not work_trades.empty and "display_outcome" not in work_trades.columns:
        work_trades = normalize_trades(work_trades)

    selected_range = normalize_btc_map_range(st.session_state.get("btc_map_range"))
    title, caption, start_ma, end_ma, interval = _btc_range_config(selected_range, work_trades, market_results_df)
    btc_df, source_label, fetch_note = load_btc_intraday_range(start_ma, end_ma, interval=interval)
    if btc_df.empty:
        st.warning(f"Could not load BTC data right now. {fetch_note}")
        return

    segments_df = build_trade_segments_for_window(work_trades, market_results_df, start_ma, end_ma)
    wins = int((segments_df["outcome"] == "win").sum()) if not segments_df.empty else 0
    losses = int((segments_df["outcome"] == "loss").sum()) if not segments_df.empty else 0
    painted = int(len(segments_df))
    range_start_text = format_ma_time(start_ma)
    range_end_text = format_ma_time(end_ma)

    summary_cols = st.columns(6)
    summary_cols[0].metric("Range", title)
    summary_cols[1].metric("BTC last", f"${btc_df['close'].iloc[-1]:,.2f}")
    summary_cols[2].metric("High", f"${btc_df['high'].max():,.2f}")
    summary_cols[3].metric("Low", f"${btc_df['low'].min():,.2f}")
    summary_cols[4].metric("Painted markets", f"{painted}", delta=f"{wins} wins | {losses} losses")
    summary_cols[5].metric("Window", f"{len(btc_df):,} candles", delta=f"{interval} bars")

    st.caption(caption)
    st.caption(f"Viewing {range_start_text} through {range_end_text}.")
    st.plotly_chart(build_btc_trade_map_figure(btc_df, segments_df, title, height=560), width="stretch")

    detail_parts = [part for part in [source_label, fetch_note] if part]
    if detail_parts:
        st.caption(" | ".join(detail_parts))

    if segments_df.empty:
        if work_trades.empty:
            st.info("No scored trades are available yet. Run the scorer from the sidebar and this map will paint resolved trade windows over BTC.")
        else:
            st.info(f"No resolved traded BTC15M markets were found inside {title.lower()}.")
        return

    table = segments_df.copy()
    table = table.sort_values("segment_start", ascending=False).reset_index(drop=True)
    table["Window"] = table["segment_start"].dt.strftime("%Y-%m-%d %I:%M %p") + " to " + table["segment_end"].dt.strftime("%Y-%m-%d %I:%M %p")
    table["Market"] = table["market"]
    table["Side"] = table["side"].astype(str).str.upper()
    table["Outcome"] = table["outcome"].astype(str).str.upper()
    table["P and L"] = table["gross_pnl_dollars"].apply(format_money)
    table["Resolved"] = table["resolution_label"]
    table["Plot coverage"] = table["plot_start"].dt.strftime("%Y-%m-%d %I:%M %p") + " to " + table["plot_end"].dt.strftime("%Y-%m-%d %I:%M %p")
    show_cols = ["Window", "Plot coverage", "Market", "Side", "Outcome", "P and L", "Resolved"]
    st.markdown(f"### Painted markets in {title.lower()}")
    st.dataframe(table[show_cols], use_container_width=True, hide_index=True)


st.set_page_config(page_title="Kalshi BTC15M Live Dashboard", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
:root {
  --bg: #07060c;
  --bg-accent: #180d24;
  --card: rgba(12, 18, 27, 0.76);
  --card-strong: rgba(16, 27, 38, 0.92);
  --muted: #a99bb9;
  --text: #f7f1e8;
  --green: #63f2b1;
  --green-soft: rgba(99,242,177,0.12);
  --red: #ff5f73;
  --red-soft: rgba(255,95,115,0.14);
  --yellow: #f7c85f;
  --blue: #79e7ff;
  --blue-soft: rgba(121,231,255,0.12);
  --violet: #d94cff;
  --border: rgba(247,241,232,0.16);
  --border-strong: rgba(121,231,255,0.32);
  --shadow: 0 18px 46px rgba(0,0,0,0.34);
}
html, body, [class*="css"] {
  font-family: "Inter", "Segoe UI", sans-serif;
}
.stApp {
  background:
    radial-gradient(circle at 48% 36%, rgba(99,242,177,0.10), transparent 28%),
    radial-gradient(circle at 76% 24%, rgba(217,76,255,0.10), transparent 32%),
    radial-gradient(ellipse at 16% 94%, rgba(247,200,95,0.08), transparent 34%),
    linear-gradient(135deg, #07060c 0%, #180d24 48%, #092c35 100%);
  color: var(--text);
}
.main > div {
  padding-top: 0;
}
.block-container {
  max-width: 1536px;
  min-height: 100vh;
  margin-top: 0;
  margin-bottom: 0;
  padding: 0 !important;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stHeader"] {
  display: none;
}
[data-testid="collapsedControl"] {
  display: none !important;
}
button[data-testid="stBaseButton-header"],
button[data-testid="stBaseButton-headerNoPadding"] {
  display: none !important;
}
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMain"] > div,
[data-testid="stMainBlockContainer"] {
  padding: 0 !important;
  margin: 0 auto !important;
}
[data-testid="stMainBlockContainer"] {
  max-width: 1536px !important;
}
[data-testid="stVerticalBlock"],
[data-testid="stElementContainer"] {
  gap: 0 !important;
  margin: 0 !important;
}
section[data-testid="stMain"] [data-testid="stHorizontalBlock"] {
  max-width: 1536px;
  margin-left: auto !important;
  margin-right: auto !important;
  padding-left: 24px;
  padding-right: 24px;
  box-sizing: border-box;
}
[data-testid="stSidebar"] {
  background:
    radial-gradient(circle at 30% 18%, rgba(121,231,255,0.10), transparent 28%),
    linear-gradient(180deg, rgba(7,6,12,0.98), rgba(24,13,36,0.98));
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] > div:first-child {
  padding-top: 0.8rem;
}
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"] {
  padding-top: 0.8rem !important;
}
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stCaption {
  color: var(--text);
}
.sidebar-shell {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.8rem 0.85rem;
  background: var(--card);
  box-shadow: var(--shadow);
  margin-bottom: 0.75rem;
}
.sidebar-kicker {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--blue);
  margin-bottom: 0.25rem;
}
.sidebar-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 0;
}
.sidebar-sub {
  display: none;
}
.sidebar-meta {
  margin-top: 0.25rem;
}
.sidebar-meta-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 0.38rem;
}
.sidebar-meta-row span {
  color: var(--muted);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.sidebar-meta-row strong {
  color: var(--text);
  font-size: 0.95rem;
  text-align: right;
  word-break: break-word;
}
.console-header {
  padding: 0.62rem 0.72rem;
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(255,255,255,0.98), rgba(239,246,255,0.96));
  border: 1px solid var(--border);
  margin-bottom: 0.6rem;
  box-shadow: var(--shadow);
}
.console-header-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: center;
}
.console-kicker {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--blue);
  margin-bottom: 0.25rem;
}
.console-title {
  font-size: 1.22rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: 0;
  line-height: 1.1;
}
.console-sub {
  color: var(--muted);
  margin-top: 0.22rem;
  line-height: 1.32;
  font-size: 0.86rem;
}
.console-status {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.strategy-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}
.strategy-chip {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0.25rem 0.48rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: #f8fafc;
  color: #344054;
  font-size: 0.74rem;
  font-weight: 600;
}
.strategy-chip.primary {
  color: var(--blue);
  border-color: rgba(37,99,235,0.26);
  background: var(--blue-soft);
}
.decision-label,
.kpi-label {
  color: var(--muted);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.kpi-band {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.55rem;
  margin: 0 0 0.75rem 0;
}
.kpi-card {
  min-height: 86px;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.64rem 0.72rem;
  background:
    linear-gradient(180deg, #ffffff, #fbfdff);
  box-shadow: var(--shadow);
}
.kpi-card.positive { box-shadow: inset 3px 0 0 var(--green); }
.kpi-card.negative { box-shadow: inset 3px 0 0 var(--red); }
.kpi-card.warning { box-shadow: inset 3px 0 0 var(--yellow); }
.kpi-value {
  color: var(--text);
  font-size: 1.56rem;
  font-weight: 700;
  line-height: 1.08;
  margin-top: 0.42rem;
}
.kpi-note {
  color: var(--muted);
  margin-top: 0.34rem;
  font-weight: 700;
  font-size: 0.86rem;
}
.kpi-card.negative .kpi-note { color: var(--red); }
.kpi-card.positive .kpi-note { color: var(--green); }
.guardrail-band {
  margin: 0 0 0.75rem 0;
  padding: 0.68rem 0.78rem;
  border-radius: 8px;
  border: 1px solid rgba(231,183,95,0.34);
  background: rgba(231,183,95,0.10);
  color: var(--text);
}
.guardrail-band strong {
  display: block;
  font-size: 0.95rem;
}
.guardrail-band span {
  display: block;
  color: var(--muted);
  font-size: 0.82rem;
  margin-top: 0.18rem;
}
.pill-green, .pill-red, .pill-yellow, .pill-gray {
  display: inline-block;
  padding: 0.42rem 0.78rem;
  border-radius: 8px;
  font-size: 0.86rem;
  font-weight: 700;
  border: 1px solid var(--border);
  backdrop-filter: blur(8px);
}
.pill-green { color: var(--green); background: var(--green-soft); }
.pill-red { color: var(--red); background: var(--red-soft); }
.pill-yellow { color: var(--yellow); background: rgba(245,196,81,0.12); }
.pill-gray { color: #b8c4ba; background: rgba(255,255,255,0.06); }
.metric-shell {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.22rem;
  background: var(--card);
}
.trade-card {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.9rem;
  background: var(--card);
  box-shadow: var(--shadow);
}
.trade-card.positive { box-shadow: var(--shadow), inset 3px 0 0 var(--green); }
.trade-card.negative { box-shadow: var(--shadow), inset 3px 0 0 var(--red); }
.trade-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.85rem;
}
.trade-market { font-size: 1rem; font-weight: 700; color: var(--text); }
.trade-sub, .trade-foot, .small-muted { color: var(--muted); }
.trade-resolution {
  margin-top: 0.75rem;
  padding: 0.55rem 0.7rem;
  border-radius: 8px;
  background: rgba(255,77,79,0.10);
  color: #8f2020;
  border: 1px solid rgba(214,69,69,0.22);
  font-size: 0.92rem;
}
.trade-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.7rem;
}
.trade-metrics span { display:block; color: var(--muted); }
.trade-metrics strong { font-size: 1rem; color: var(--text); }
.badge {
  border-radius: 8px;
  padding: 0.35rem 0.7rem;
  font-weight: 700;
  font-size: 0.9rem;
}
.badge-green { background: var(--green-soft); color: var(--green); }
.badge-red { background: var(--red-soft); color: var(--red); }
.badge-yellow { background: rgba(245,196,81,0.12); color: var(--yellow); }
.badge-neutral { background: rgba(255,255,255,0.06); color: #d2ddd3; }
.panel {
  background:
    linear-gradient(180deg, #ffffff, #fbfdff);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem 1.05rem;
  box-shadow: var(--shadow);
}
.overview-band {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
  margin: 0.8rem 0 1rem 0;
}
.overview-card {
  position: relative;
  overflow: hidden;
  min-height: 178px;
}
.overview-card::after {
  display: none;
}
.overview-kicker {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--blue);
  margin-bottom: 0.32rem;
}
.overview-headline {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.15;
  margin-bottom: 0.58rem;
}
.overview-subline {
  display: none;
}
.overview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.7rem;
}
.overview-stat {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.62rem 0.68rem;
  background: #f8fafc;
}
.overview-stat-label {
  font-size: 0.66rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.28rem;
}
.overview-stat-value {
  font-size: 0.96rem;
  color: var(--text);
  font-weight: 700;
  line-height: 1.15;
}
.overview-stat-note {
  margin-top: 0.18rem;
  color: var(--muted);
  font-size: 0.76rem;
}
.ops-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.28fr) minmax(320px, 0.72fr);
  gap: 0.85rem;
  margin: 0.72rem 0 0.85rem 0;
}
.operator-brief,
.watch-panel,
.health-card {
  background: linear-gradient(180deg, #ffffff, #fbfdff);
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: var(--shadow);
}
.operator-brief {
  padding: 1rem;
}
.watch-panel {
  padding: 0.9rem;
}
.brief-topline {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.8rem;
}
.brief-kicker,
.watch-kicker,
.health-kicker {
  color: var(--blue);
  font-size: 0.68rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-weight: 700;
}
.brief-title {
  color: var(--text);
  font-size: 1.42rem;
  font-weight: 750;
  line-height: 1.08;
  margin-top: 0.22rem;
}
.brief-sub {
  color: var(--muted);
  font-size: 0.9rem;
  line-height: 1.42;
  margin-top: 0.35rem;
  max-width: 58rem;
}
.status-badge {
  border-radius: 999px;
  padding: 0.35rem 0.62rem;
  font-size: 0.78rem;
  font-weight: 800;
  white-space: nowrap;
  border: 1px solid var(--border);
}
.status-badge.positive { background: var(--green-soft); color: var(--green); }
.status-badge.negative { background: var(--red-soft); color: var(--red); }
.status-badge.warning { background: rgba(183,121,31,0.12); color: var(--yellow); }
.status-badge.neutral { background: #eef2f7; color: #475467; }
.brief-metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.65rem;
}
.brief-metric {
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.72rem 0.75rem;
}
.brief-metric-label,
.quote-label,
.health-label {
  color: var(--muted);
  font-size: 0.66rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
}
.brief-metric-value {
  color: var(--text);
  font-size: 1.45rem;
  line-height: 1.04;
  font-weight: 800;
  margin-top: 0.32rem;
}
.brief-metric-note {
  color: var(--muted);
  font-size: 0.78rem;
  margin-top: 0.24rem;
  font-weight: 700;
}
.watch-market {
  color: var(--text);
  font-weight: 800;
  line-height: 1.18;
  margin-top: 0.25rem;
  word-break: break-word;
}
.quote-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.55rem;
  margin-top: 0.75rem;
}
.quote-box {
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.68rem;
}
.quote-value {
  color: var(--text);
  font-size: 1.2rem;
  font-weight: 800;
  margin-top: 0.25rem;
}
.quote-note {
  color: var(--muted);
  font-size: 0.76rem;
  margin-top: 0.18rem;
}
.health-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
  margin: 0 0 1rem 0;
}
.health-card {
  padding: 0.82rem;
}
.health-title {
  color: var(--text);
  font-size: 1rem;
  font-weight: 800;
  margin-top: 0.24rem;
}
.health-list {
  display: grid;
  gap: 0.46rem;
  margin-top: 0.72rem;
}
.health-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  color: var(--muted);
  font-size: 0.84rem;
}
.health-value {
  color: var(--text);
  font-weight: 800;
  text-align: right;
}
.pl-kpi-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0.65rem;
  margin: 0.72rem 0 0.8rem 0;
}
.pl-kpi-card {
  min-height: 112px;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.74rem 0.78rem;
  background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
  box-shadow: var(--shadow);
  position: relative;
  overflow: hidden;
}
.pl-kpi-card::before {
  content: "";
  position: absolute;
  inset: 0 0 auto 0;
  height: 3px;
  background: #94a3b8;
}
.pl-kpi-card.positive::before { background: linear-gradient(90deg, #0f766e, #22c55e); }
.pl-kpi-card.negative::before { background: linear-gradient(90deg, #dc2626, #fb7185); }
.pl-kpi-card.warning::before { background: linear-gradient(90deg, #b7791f, #f59e0b); }
.pl-kpi-card.neutral::before { background: linear-gradient(90deg, #64748b, #2563eb); }
.pl-kpi-label,
.live-strip-label,
.trade-tape-meta,
.pl-chart-kicker {
  color: var(--muted);
  font-size: 0.66rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 800;
}
.pl-kpi-value {
  color: var(--text);
  font-size: 1.48rem;
  font-weight: 850;
  line-height: 1.02;
  margin-top: 0.4rem;
  white-space: nowrap;
}
.pl-kpi-note {
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.28;
  margin-top: 0.3rem;
  font-weight: 700;
}
.pl-kpi-card.positive .pl-kpi-value { color: #0f766e; }
.pl-kpi-card.negative .pl-kpi-value { color: #c2410c; }
.pl-chart-title {
  margin: 0.2rem 0 0.3rem 0;
}
.pl-chart-headline {
  color: var(--text);
  font-size: 1.48rem;
  font-weight: 850;
  line-height: 1.08;
  margin-top: 0.18rem;
}
.pl-chart-sub {
  color: var(--muted);
  font-size: 0.9rem;
  font-weight: 700;
  margin-top: 0.22rem;
}
.pl-chart-statline {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.48rem;
}
.pl-chart-statline span {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #ffffff;
  color: var(--text);
  padding: 0.24rem 0.5rem;
  font-size: 0.78rem;
  font-weight: 800;
  box-shadow: 0 6px 16px rgba(31,44,67,0.05);
}
div[data-testid="stPlotlyChart"] {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: var(--shadow);
  padding: 0.24rem;
}
.live-strip {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0.62rem;
  margin: 0.82rem 0 0.95rem 0;
}
.live-strip-item {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.72rem 0.78rem;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  box-shadow: 0 8px 22px rgba(31,44,67,0.06);
}
.live-strip-value {
  color: var(--text);
  font-size: 0.98rem;
  font-weight: 850;
  line-height: 1.2;
  margin-top: 0.28rem;
  word-break: break-word;
}
.live-strip-note {
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.32;
  margin-top: 0.2rem;
  font-weight: 650;
}
.section-label {
  color: var(--text);
  font-size: 0.98rem;
  font-weight: 850;
  margin: 0.2rem 0 0.48rem 0;
}
.trade-tape {
  display: grid;
  gap: 0.58rem;
}
.trade-tape-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(150px, 0.42fr) auto;
  gap: 0.78rem;
  align-items: center;
  min-height: 72px;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.7rem 0.78rem;
  background: #ffffff;
  box-shadow: 0 8px 22px rgba(31,44,67,0.06);
}
.trade-tape-row.tape-win { border-left: 4px solid #0f766e; }
.trade-tape-row.tape-loss { border-left: 4px solid #dc2626; }
.trade-tape-row.tape-flat { border-left: 4px solid #64748b; }
.trade-tape-row.tape-open { border-left: 4px solid #2563eb; }
.trade-tape-market {
  color: var(--text);
  font-size: 0.92rem;
  font-weight: 850;
  line-height: 1.18;
  word-break: break-word;
}
.trade-tape-prices {
  color: var(--muted);
  display: grid;
  gap: 0.18rem;
  font-size: 0.78rem;
  font-weight: 750;
}
.trade-tape-pnl {
  color: var(--text);
  font-size: 1.05rem;
  font-weight: 900;
  text-align: right;
  white-space: nowrap;
}
.tape-win .trade-tape-pnl { color: #0f766e; }
.tape-loss .trade-tape-pnl { color: #dc2626; }
.living-topline {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 0.78rem;
  align-items: center;
  min-height: 78px;
  padding: 0.62rem 0.78rem;
  border: 1px solid rgba(247,241,232,0.68);
  border-radius: 26px 14px 24px 14px;
  color: #17121d;
  background:
    radial-gradient(circle at 8% 15%, rgba(99,242,177,0.20), transparent 30%),
    radial-gradient(ellipse at 92% 70%, rgba(217,76,255,0.10), transparent 34%),
    linear-gradient(135deg, rgba(255,250,242,0.98), rgba(231,225,214,0.92) 54%, rgba(194,184,170,0.86));
  box-shadow:
    0 18px 44px rgba(0,0,0,0.38),
    inset 0 0 0 1px rgba(255,255,255,0.54),
    inset 0 -18px 34px rgba(50,37,31,0.08);
}
.living-brand-mark {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #9cff9f;
  background:
    radial-gradient(circle at 45% 40%, rgba(156,255,159,0.26), rgba(9,44,53,0.88) 46%, #07060c 72%);
  border: 1px solid rgba(7,6,12,0.65);
  box-shadow: 0 0 24px rgba(99,242,177,0.35), inset 0 0 16px rgba(121,231,255,0.18), 0 8px 18px rgba(7,6,12,0.22);
  font-weight: 900;
  font-size: 0.82rem;
}
.living-brand-title {
  font-size: 1.34rem;
  line-height: 1.02;
  font-weight: 900;
  color: #17121d;
}
.living-brand-sub {
  margin-top: 0.16rem;
  color: rgba(23,18,29,0.72);
  font-size: 0.84rem;
  font-weight: 700;
}
.living-control-chip {
  min-height: 78px;
  padding: 0.62rem 0.76rem;
  border-radius: 24px 12px 22px 12px;
  border: 1px solid rgba(121,231,255,0.26);
  background:
    radial-gradient(circle at 20% 10%, rgba(121,231,255,0.18), transparent 34%),
    radial-gradient(circle at 78% 82%, rgba(99,242,177,0.11), transparent 30%),
    linear-gradient(180deg, rgba(8,24,31,0.96), rgba(7,6,12,0.92));
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.09), inset 0 0 26px rgba(121,231,255,0.05), 0 14px 34px rgba(0,0,0,0.32);
}
.living-control-chip .chip-label,
.living-command-label,
.living-pod-label,
.module-label,
.seed-time {
  color: #a99bb9;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0;
  font-weight: 850;
}
.living-control-chip .chip-value {
  color: #f7f1e8;
  font-size: 1rem;
  font-weight: 850;
  margin-top: 0.18rem;
  word-break: break-word;
}
.living-control-chip .chip-note {
  color: rgba(247,241,232,0.64);
  font-size: 0.76rem;
  margin-top: 0.1rem;
}
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] label {
  color: #d9cde7 !important;
  font-weight: 800 !important;
  letter-spacing: 0 !important;
}
div[data-baseweb="select"] > div {
  min-height: 48px;
  border-radius: 14px 8px 14px 8px !important;
  border: 1px solid rgba(121,231,255,0.24) !important;
  background:
    linear-gradient(180deg, rgba(8,24,31,0.96), rgba(7,6,12,0.94)) !important;
  color: #f7f1e8 !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
}
div[data-baseweb="select"] span,
div[data-baseweb="select"] svg {
  color: #f7f1e8 !important;
  fill: #f7f1e8 !important;
}
.stButton > button {
  min-height: 48px;
  border-radius: 14px 8px 14px 8px !important;
  border: 1px solid rgba(217,76,255,0.42) !important;
  color: #f7f1e8 !important;
  background:
    radial-gradient(circle at 78% 22%, rgba(99,242,177,0.22), transparent 28%),
    linear-gradient(135deg, rgba(53,19,76,0.98), rgba(12,9,18,0.96)) !important;
  box-shadow: 0 0 18px rgba(217,76,255,0.20), inset 0 1px 0 rgba(255,255,255,0.11);
  font-weight: 900 !important;
}
.ref-control-label {
  margin: 0.48rem 0 0.24rem;
  color: #b9adc9;
  font-size: .7rem;
  font-weight: 950;
  text-transform: uppercase;
}
.ref-control-label::before {
  content: "";
  display: inline-block;
  width: 9px;
  height: 9px;
  margin-right: 7px;
  border-radius: 99px;
  background: radial-gradient(circle, #9cff9f, #09353a 72%);
  box-shadow: 0 0 10px rgba(156,255,159,.54);
  vertical-align: -1px;
}
.ref-art-cockpit {
  position: relative;
  width: min(100vw, 1536px);
  aspect-ratio: 1536 / 1024;
  margin: 0 auto;
  overflow: hidden;
  border-radius: 0;
  background: #07060c;
  box-shadow: none;
}
.ref-art-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  pointer-events: none;
  user-select: none;
}
.ref-hit {
  position: absolute;
  z-index: 6;
  display: block;
  border-radius: 10px;
  opacity: 1;
  background: rgba(0,0,0,.001);
  transition: opacity .12s ease, box-shadow .12s ease, background .12s ease;
}
.ref-hit:hover {
  background: rgba(156,255,159,.08);
  box-shadow: 0 0 0 1px rgba(156,255,159,.52), 0 0 24px rgba(156,255,159,.22);
}
.ref-hit-refresh { left: 55.2%; top: 2.0%; width: 12.4%; height: 7.4%; border-radius: 26px; }
.ref-hit-range-1d { left: 54.1%; top: 13.2%; width: 2.9%; height: 3.6%; }
.ref-hit-range-1w { left: 57.4%; top: 13.2%; width: 3.0%; height: 3.6%; }
.ref-hit-range-1m { left: 60.9%; top: 13.2%; width: 3.0%; height: 3.6%; }
.ref-hit-range-3m { left: 64.3%; top: 13.2%; width: 3.0%; height: 3.6%; }
.ref-hit-range-ytd { left: 67.9%; top: 13.2%; width: 3.2%; height: 3.6%; }
.ref-hit-range-all { left: 71.6%; top: 13.2%; width: 3.0%; height: 3.6%; }
.ref-hit-seed-all { left: 24.8%; top: 80.0%; width: 6.3%; height: 3.5%; }
.ref-hit-seed-win { left: 44.6%; top: 80.3%; width: 4.0%; height: 2.4%; }
.ref-hit-seed-loss { left: 48.4%; top: 80.3%; width: 4.4%; height: 2.4%; }
.ref-hit-seed-flat { left: 52.9%; top: 80.3%; width: 4.2%; height: 2.4%; }
.ref-art-active-range {
  position: absolute;
  z-index: 5;
  top: 13.2%;
  height: 3.6%;
  border-radius: 9px;
  box-shadow: 0 0 0 2px rgba(156,255,159,.84), 0 0 18px rgba(156,255,159,.46);
  pointer-events: none;
}
.ref-art-active-range-1d { left: 54.1%; width: 2.9%; }
.ref-art-active-range-1w { left: 57.4%; width: 3.0%; }
.ref-art-active-range-1m { left: 60.9%; width: 3.0%; }
.ref-art-active-range-3m { left: 64.3%; width: 3.0%; }
.ref-art-active-range-ytd { left: 67.9%; width: 3.2%; }
.ref-art-active-range-all { left: 71.6%; width: 3.0%; }
.ref-live-top,
.ref-live-panel,
.ref-live-pod {
  position: absolute;
  z-index: 4;
  pointer-events: none;
  overflow: hidden;
  color: #f7f1e8;
  text-shadow: 0 1px 5px rgba(0,0,0,.9);
  border: 1px solid rgba(121,231,255,.25);
  background:
    radial-gradient(circle at 84% 12%, rgba(99,242,177,.12), transparent 28%),
    radial-gradient(circle at 22% 104%, rgba(217,76,255,.10), transparent 32%),
    linear-gradient(145deg, rgba(8,24,31,.93), rgba(7,6,12,.91));
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.12),
    inset 0 -12px 28px rgba(0,0,0,.32),
    0 0 18px rgba(0,0,0,.24);
}
.ref-live-top {
  display: grid;
  align-content: center;
  gap: .08vw;
  padding: .36vw .52vw;
  border-radius: 1vw .42vw 1vw .42vw;
}
.ref-live-top span,
.ref-live-pod span,
.ref-live-panel-head span,
.ref-live-title,
.ref-live-seed-title {
  color: #d9cde7;
  font-size: clamp(7px, .68vw, 11px);
  font-weight: 950;
  text-transform: uppercase;
}
.ref-live-top b,
.ref-live-pod b,
.ref-live-panel-head b,
.ref-live-market-value,
.ref-live-lock-value {
  color: #9cff9f;
  font-size: clamp(12px, 1.08vw, 20px);
  line-height: 1;
  font-weight: 950;
}
.ref-live-top em,
.ref-live-pod em,
.ref-live-panel .ref-note {
  color: #d9cde7;
  font-style: normal;
  font-size: clamp(7px, .60vw, 10px);
  font-weight: 780;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ref-live-top-dataset { left: 20.0%; top: 5.0%; width: 12.2%; height: 4.8%; }
.ref-live-top-sync { left: 34.6%; top: 4.2%; width: 16.4%; height: 5.6%; }
.ref-live-top-refresh { left: 55.2%; top: 2.2%; width: 12.3%; height: 6.9%; text-align: center; border-color: rgba(217,76,255,.42); }
.ref-live-top-lock { left: 68.3%; top: 3.2%; width: 8.8%; height: 6.1%; }
.ref-live-top-api { left: 82.4%; top: 3.1%; width: 12.4%; height: 6.2%; border-color: rgba(121,231,255,.28); }
.ref-live-pod {
  left: 3.9%;
  width: 11.6%;
  padding: .58vw .66vw;
  border-radius: 1.25vw .56vw 1.25vw .56vw;
}
.ref-live-pod-pnl { top: 12.1%; height: 12.6%; }
.ref-live-pod-dd { top: 26.2%; height: 12.3%; border-color: rgba(255,95,115,.30); }
.ref-live-pod-win { top: 39.6%; height: 11.8%; }
.ref-live-pod-open { top: 52.3%; height: 11.6%; }
.ref-live-pod-pulse { top: 65.0%; height: 13.0%; }
.ref-live-pod.loss b,
.ref-live-pod-dd b,
.ref-live-panel.fallback b {
  color: #ff6f7f;
}
.ref-live-pod .living-sparkline {
  height: 23%;
  margin-top: .3vw;
}
.ref-live-pod .living-ring {
  height: 48%;
  margin-top: .08vw;
}
.ref-live-panel {
  border-radius: 1.4vw .7vw 1.4vw .7vw;
  padding: .72vw .86vw;
}
.ref-live-equity-panel { left: 16.6%; top: 11.2%; width: 61.0%; height: 45.5%; border-radius: 1.8vw .9vw 1.8vw .9vw; }
.ref-live-drawdown-panel { left: 16.9%; top: 57.3%; width: 32.7%; height: 21.5%; }
.ref-live-spores-panel { left: 50.2%; top: 57.5%; width: 27.0%; height: 21.3%; }
.ref-live-vitals-panel { left: 79.5%; top: 10.8%; width: 14.7%; height: 22.3%; }
.ref-live-lock-panel { left: 79.3%; top: 35.1%; width: 15.1%; height: 14.0%; }
.ref-live-market-panel { left: 79.3%; top: 50.4%; width: 15.2%; height: 14.8%; }
.ref-live-depth-panel { left: 79.4%; top: 66.2%; width: 15.0%; height: 12.0%; }
.ref-live-seeds-panel { left: 3.6%; top: 80.0%; width: 64.6%; height: 18.1%; border-color: rgba(66,54,45,.34); background: linear-gradient(135deg, rgba(247,241,232,.91), rgba(222,216,205,.86)); color: #17121d; text-shadow: none; }
.ref-live-diagnostics-panel { left: 68.8%; top: 80.2%; width: 28.1%; height: 17.8%; border-color: rgba(217,76,255,.30); }
.ref-live-panel-head {
  display: flex;
  justify-content: space-between;
  align-items: start;
  gap: .7vw;
  margin-bottom: .24vw;
}
.ref-live-panel-head b {
  display: block;
  margin-top: .16vw;
  color: #d9cde7;
  font-size: clamp(8px, .74vw, 12px);
}
.ref-live-panel-head .ref-pills span {
  padding: .18vw .44vw;
  font-size: clamp(7px, .62vw, 10px);
}
.ref-live-equity-panel .ref-equity-svg,
.ref-live-drawdown-panel .ref-roots-svg {
  height: calc(100% - 2.1vw);
  margin-top: .1vw;
}
.ref-live-spores-panel > div:not(.ref-live-panel-head) {
  height: calc(100% - 2.2vw) !important;
}
.ref-live-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: .7vw;
  margin-top: .44vw;
  color: #a99bb9;
  font-size: clamp(7px, .68vw, 11px);
  font-weight: 800;
}
.ref-live-row b {
  color: #9cff9f;
  font-size: clamp(8px, .72vw, 12px);
}
.ref-live-title span {
  color: #d9cde7;
  border: 1px solid rgba(217,76,255,.34);
  border-radius: 999px;
  padding: .08vw .38vw;
  margin-left: .35vw;
}
.ref-live-vitals-panel .living-sparkline {
  height: 20%;
  margin-top: .55vw;
}
.ref-live-depth-panel .living-sparkline {
  height: calc(100% - 1.4vw);
  width: 100%;
  margin-top: .28vw !important;
}
.ref-live-seed-title {
  color: #17121d;
}
.ref-live-seed-title span {
  color: rgba(23,18,29,.56);
  margin-left: .6vw;
}
.ref-live-seeds-panel .ref-seed-meta {
  font-size: clamp(7px, .58vw, 10px);
  gap: .7vw;
}
.ref-live-seeds-panel .ref-seeds-inner {
  gap: .55vw;
  padding-top: .42vw;
}
.ref-live-seeds-panel .ref-seed {
  min-width: 0;
  max-width: none;
  min-height: 5vw;
  padding: .48vw .54vw;
}
.ref-live-seeds-panel .ref-seed-market {
  font-size: clamp(7px, .66vw, 11px);
}
.ref-live-seeds-panel .ref-seed-side,
.ref-live-seeds-panel .ref-seed-pnl {
  font-size: clamp(7px, .58vw, 10px);
}
.ref-live-diagnostics-panel .ref-live-row {
  margin-top: .46vw;
}
.ref-art-live {
  position: absolute;
  z-index: 4;
  pointer-events: none;
  display: grid;
  gap: .14vw;
  padding: .38vw .52vw;
  border: 1px solid rgba(156,255,159,.24);
  border-radius: .8vw;
  background: linear-gradient(135deg, rgba(7,6,12,.68), rgba(8,24,31,.42));
  box-shadow: 0 0 18px rgba(7,6,12,.28), inset 0 1px 0 rgba(255,255,255,.08);
  color: #d9cde7;
  font-size: clamp(8px, .74vw, 12px);
  line-height: 1.08;
  text-shadow: 0 1px 4px rgba(0,0,0,.82);
  opacity: 0;
  transform: translateY(2px);
  transition: opacity .14s ease, transform .14s ease;
}
.ref-art-cockpit:hover .ref-art-live {
  opacity: .94;
  transform: translateY(0);
}
.ref-art-live b {
  color: #9cff9f;
  font-size: clamp(12px, 1.2vw, 22px);
  line-height: 1;
}
.ref-art-live span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ref-art-live.loss b,
.ref-art-dd b {
  color: #ff6f7f;
}
.ref-art-live.flat b { color: #f7c85f; }
.ref-art-dataset { left: 20.2%; top: 4.7%; width: 11.8%; }
.ref-art-sync { left: 35.1%; top: 4.3%; width: 11.7%; }
.ref-art-pnl { left: 4.0%; top: 15.1%; width: 11.3%; }
.ref-art-dd { left: 4.0%; top: 29.6%; width: 11.2%; }
.ref-art-win { left: 4.0%; top: 41.2%; width: 9.4%; }
.ref-art-open { left: 4.0%; top: 53.3%; width: 9.2%; }
.ref-art-pulse { left: 4.0%; top: 65.7%; width: 12.0%; }
.ref-art-vitals { left: 80.3%; top: 14.0%; width: 13.0%; }
.ref-art-api { left: 84.3%; top: 4.2%; width: 11.0%; border-color: rgba(121,231,255,.28); }
.ref-art-lock { left: 80.4%; top: 37.8%; width: 11.6%; }
.ref-art-market { left: 80.2%; top: 52.1%; width: 13.4%; }
.ref-art-seeds { left: 7.6%; top: 87.0%; width: 18.0%; border-color: rgba(247,200,95,.32); }
.ref-art-diagnostics { left: 72.4%; top: 82.6%; width: 14.7%; border-color: rgba(217,76,255,.30); }
.ref-art-live {
  display: none;
}
@media (max-width: 900px) {
  .ref-art-live {
    display: none;
  }
  .ref-live-top { display: grid; }
  .ref-live-panel,
  .ref-live-pod { display: block; }
  .ref-art-cockpit {
    border-radius: 7px;
  }
}
.dark-ref-shell {
  max-width: 1536px;
  margin: 0 auto 1.28rem auto;
  padding: 24px 24px 0 24px;
  color: #f7f1e8;
}
.dark-ref-top {
  display: grid;
  grid-template-columns: minmax(250px, 344px) minmax(360px, 1fr) minmax(210px, 280px) minmax(170px, 220px) minmax(210px, 280px);
  gap: 32px;
  align-items: stretch;
}
.dark-ref-brand,
.dark-ref-field,
.dark-ref-refresh,
.dark-ref-score,
.dark-ref-status-card {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(121,231,255,.26);
  background:
    radial-gradient(circle at 83% 16%, rgba(99,242,177,.12), transparent 32%),
    linear-gradient(145deg, rgba(8,24,31,.96), rgba(7,6,12,.94));
  box-shadow: inset 0 1px 0 rgba(255,255,255,.12), 0 12px 34px rgba(0,0,0,.25);
}
.dark-ref-brand {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  align-items: center;
  gap: 18px;
  min-height: 112px;
  padding: 14px 26px;
  border-radius: 15px;
  color: #17121d;
  background:
    radial-gradient(circle at 12% 28%, rgba(156,255,159,.18), transparent 26%),
    linear-gradient(135deg, rgba(255,252,246,.98), rgba(213,207,197,.92));
  border-color: rgba(247,241,232,.72);
}
.dark-ref-orb {
  width: 64px;
  height: 64px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: radial-gradient(circle at 47% 43%, rgba(156,255,159,.55), rgba(9,44,53,.92) 48%, #07060c 76%);
  border: 2px solid rgba(7,6,12,.82);
  box-shadow: 0 0 22px rgba(99,242,177,.34), inset 0 0 16px rgba(121,231,255,.18);
}
.dark-ref-orb span {
  color: #9cff9f;
  font-weight: 950;
  font-size: 1.3rem;
}
.dark-ref-brand b {
  display: block;
  color: #17121d;
  font-size: 2rem;
  line-height: 1;
  font-weight: 950;
}
.dark-ref-brand span {
  display: block;
  margin-top: 12px;
  color: rgba(23,18,29,.72);
  font-size: 1.25rem;
  font-weight: 850;
}
.dark-ref-field,
.dark-ref-score {
  min-height: 70px;
  padding: 16px 22px;
  align-self: center;
  border-radius: 15px;
}
.dark-ref-field span,
.dark-ref-score span,
.dark-ref-status-card span {
  display: block;
  color: #b9aad0;
  font-weight: 850;
  font-size: .86rem;
  margin-bottom: 7px;
}
.dark-ref-field b,
.dark-ref-score b,
.dark-ref-status-card b {
  display: block;
  color: #f7f1e8;
  font-size: 1.55rem;
  line-height: 1.08;
  font-weight: 920;
}
.dark-ref-dataset b {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.dark-ref-refresh {
  display: grid;
  place-items: center;
  align-self: center;
  min-height: 70px;
  border-radius: 15px;
  color: #d9cde7 !important;
  text-decoration: none !important;
  font-size: 1.52rem;
  background:
    radial-gradient(circle at 76% 28%, rgba(217,76,255,.17), transparent 35%),
    linear-gradient(145deg, rgba(19,22,40,.98), rgba(13,19,30,.95));
}
.dark-ref-top a.dark-ref-refresh:visited,
.dark-ref-top a.dark-ref-refresh:active {
  color: #d9cde7 !important;
  text-decoration: none !important;
}
.dark-ref-refresh:hover,
.dark-ref-pill:hover,
.dark-ref-tabs a:hover {
  box-shadow: 0 0 0 1px rgba(156,255,159,.46), 0 0 20px rgba(156,255,159,.18);
}
.dark-ref-score {
  min-height: 112px;
}
.dark-ref-score b {
  color: #f7f1e8;
  font-size: 1.45rem;
}
.dark-ref-score em,
.dark-ref-status-card em {
  display: block;
  margin-top: 12px;
  color: #a99bb9;
  font-style: normal;
  font-weight: 720;
  line-height: 1.24;
}
.dark-ref-tabs {
  display: flex;
  width: max-content;
  max-width: 100%;
  margin-top: 38px;
  border: 1px solid rgba(121,231,255,.26);
  border-radius: 10px;
  overflow: hidden;
}
.dark-ref-tabs a {
  min-width: 118px;
  padding: 12px 18px;
  text-align: center;
  color: #d9cde7;
  text-decoration: none;
  background: rgba(8,24,31,.82);
  border-right: 1px solid rgba(121,231,255,.20);
  font-size: 1.03rem;
}
.dark-ref-tabs a:last-child {
  border-right: 0;
}
.dark-ref-tabs a.active {
  color: #f7f1e8;
  background: rgba(15,31,42,.98);
}
.dark-ref-status-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.95fr) minmax(220px, .98fr) minmax(220px, .98fr) minmax(220px, .98fr);
  gap: 22px;
  margin-top: 54px;
}
.dark-ref-status-card {
  min-height: 128px;
  padding: 22px 26px;
  border-radius: 15px;
}
.dark-ref-status-card.porcelain {
  color: #17121d;
  background:
    radial-gradient(circle at 86% 18%, rgba(9,44,53,.16), transparent 28%),
    linear-gradient(135deg, rgba(255,252,246,.96), rgba(213,207,197,.88));
  border-color: rgba(247,241,232,.72);
}
.dark-ref-status-card.porcelain span,
.dark-ref-status-card.porcelain em {
  color: rgba(23,18,29,.62);
}
.dark-ref-status-card.porcelain b {
  color: #17121d;
}
.dark-ref-status-card.verified {
  border-color: rgba(125,255,178,.42);
}
.dark-ref-status-card.fallback,
.dark-ref-status-card.error {
  border-color: rgba(255,95,115,.48);
}
.dark-ref-command {
  margin-top: 0;
}
.dark-ref-range,
.dark-ref-seed-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
  margin-top: .7rem;
}
.dark-ref-seed-filter {
  margin-top: 0;
  gap: .34rem;
  align-items: center;
}
.dark-ref-pill {
  display: inline-flex;
  min-height: 32px;
  align-items: center;
  justify-content: center;
  padding: .28rem .72rem;
  color: #d9cde7;
  text-decoration: none;
  border: 1px solid rgba(121,231,255,.24);
  background: rgba(8,24,31,.72);
  font-size: .82rem;
  font-weight: 850;
}
.dark-ref-pill:first-child {
  border-radius: 10px 0 0 10px;
}
.dark-ref-pill:last-child {
  border-radius: 0 10px 10px 0;
}
.dark-ref-pill.active {
  color: #17121d;
  background: linear-gradient(135deg, #9cff9f, #f7c85f);
}
.dark-ref-trade-title {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
}
@media (max-width: 1180px) {
  .dark-ref-shell { padding: 12px 10px 0; }
  .dark-ref-top {
    grid-template-columns: 220px minmax(240px, 1fr) minmax(170px, 220px) minmax(140px, 190px);
    gap: 10px;
  }
  .dark-ref-score { display: none; }
  .dark-ref-brand { min-height: 78px; padding: 10px 16px; grid-template-columns: 54px minmax(0,1fr); }
  .dark-ref-orb { width: 48px; height: 48px; }
  .dark-ref-brand b { font-size: 1.38rem; }
  .dark-ref-brand span { font-size: .9rem; margin-top: 5px; }
  .dark-ref-field,
  .dark-ref-refresh { min-height: 58px; padding: 10px 14px; }
  .dark-ref-field b,
  .dark-ref-refresh { font-size: 1.12rem; }
  .dark-ref-tabs { margin-top: 12px; width: 100%; }
  .dark-ref-tabs a { min-width: 0; flex: 1 1 auto; padding: 9px 8px; font-size: .85rem; }
  .dark-ref-status-grid { grid-template-columns: 1.25fr 1fr 1fr 1fr; gap: 10px; margin-top: 28px; }
  .dark-ref-status-card { min-height: 92px; padding: 12px 14px; }
  .dark-ref-status-card b { font-size: 1.05rem; }
  .dark-ref-status-card em { margin-top: 6px; font-size: .7rem; }
}
.living-command-strip {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(190px, 0.72fr) minmax(180px, 0.7fr) minmax(170px, 0.62fr);
  gap: 0.74rem;
  align-items: stretch;
  margin: 0.66rem 0 0.62rem 0;
  padding: 0.28rem;
  border: 1px solid rgba(247,241,232,0.22);
  border-radius: 24px 12px 24px 12px;
  background:
    radial-gradient(circle at 15% 40%, rgba(99,242,177,0.08), transparent 30%),
    linear-gradient(135deg, rgba(247,241,232,0.18), rgba(7,6,12,0.20));
}
.living-command-card {
  position: relative;
  overflow: hidden;
  min-height: 88px;
  padding: 0.64rem 0.78rem;
  border: 1px solid rgba(247,241,232,0.54);
  border-radius: 22px 10px 22px 10px;
  background:
    radial-gradient(circle at 88% 18%, rgba(99,242,177,0.13), transparent 34%),
    radial-gradient(ellipse at 20% 110%, rgba(7,6,12,0.10), transparent 44%),
    linear-gradient(145deg, rgba(255,250,242,0.96), rgba(220,216,208,0.84));
  color: #17121d;
  box-shadow: 0 16px 42px rgba(0,0,0,0.32), inset 0 1px 0 rgba(255,255,255,0.70), inset 0 -14px 28px rgba(45,34,28,0.08);
}
.living-command-card.dark {
  color: #f7f1e8;
  background:
    radial-gradient(circle at 74% 18%, rgba(121,231,255,0.16), transparent 34%),
    radial-gradient(circle at 18% 80%, rgba(217,76,255,0.09), transparent 32%),
    linear-gradient(145deg, rgba(8,24,31,0.96), rgba(7,6,12,0.91));
  border-color: rgba(121,231,255,0.26);
}
.living-command-card.verified { border-color: rgba(125,255,178,0.36); }
.living-command-card.partial { border-color: rgba(255,191,77,0.42); }
.living-command-card.fallback { border-color: rgba(255,95,115,0.42); }
.living-command-value {
  color: inherit;
  font-size: 1rem;
  font-weight: 900;
  margin-top: 0.18rem;
  line-height: 1.08;
}
.living-command-note {
  color: rgba(23,18,29,0.68);
  font-size: 0.78rem;
  margin-top: 0.18rem;
  font-weight: 750;
}
.living-command-card.dark .living-command-note {
  color: rgba(247,241,232,0.64);
}
.living-chart-head {
  position: relative;
  overflow: hidden;
  border-radius: 28px 28px 0 0;
  padding: 0.98rem 1.06rem 0.72rem 1.06rem;
  border: 1px solid rgba(247,241,232,0.42);
  border-bottom: 0;
  background:
    radial-gradient(circle at 72% 12%, rgba(99,242,177,0.18), transparent 28%),
    radial-gradient(circle at 25% 22%, rgba(217,76,255,0.12), transparent 28%),
    repeating-linear-gradient(90deg, rgba(121,231,255,0.035) 0 1px, transparent 1px 72px),
    linear-gradient(180deg, rgba(8,24,31,0.98), rgba(7,6,12,0.91));
  box-shadow: 0 -8px 34px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.12);
}
.living-chart-kicker {
  color: #79e7ff;
  font-size: 0.76rem;
  text-transform: uppercase;
  font-weight: 900;
}
.living-chart-title {
  color: #f7f1e8;
  font-size: 1.48rem;
  font-weight: 900;
  line-height: 1.04;
  margin-top: 0.18rem;
}
.living-chart-sub {
  color: #d9cde7;
  font-size: 0.88rem;
  margin-top: 0.2rem;
  font-weight: 700;
}
.living-statline {
  display: flex;
  flex-wrap: wrap;
  gap: 0.42rem;
  margin-top: 0.65rem;
}
.living-statline span {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0.24rem 0.52rem;
  border: 1px solid rgba(121,231,255,0.18);
  border-radius: 8px;
  background: rgba(7,6,12,0.52);
  color: #f7f1e8;
  font-size: 0.78rem;
  font-weight: 850;
}
div[data-testid="stPlotlyChart"] {
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 52% 28%, rgba(99,242,177,0.13), transparent 24%),
    radial-gradient(circle at 62% 68%, rgba(217,76,255,0.13), transparent 27%),
    radial-gradient(ellipse at 42% 38%, rgba(156,255,159,0.18), transparent 27%),
    radial-gradient(ellipse at 58% 70%, rgba(217,76,255,0.19), transparent 28%),
    repeating-linear-gradient(115deg, rgba(99,242,177,0.035) 0 1px, transparent 1px 42px),
    repeating-linear-gradient(90deg, rgba(121,231,255,0.052) 0 1px, transparent 1px 64px),
    repeating-linear-gradient(0deg, rgba(247,241,232,0.038) 0 1px, transparent 1px 54px),
    linear-gradient(145deg, rgba(7,16,22,0.99), rgba(7,6,12,0.97) 58%, rgba(24,13,36,0.92)) !important;
  border: 1px solid rgba(247,241,232,0.38) !important;
  border-radius: 0 0 28px 28px !important;
  box-shadow: 0 20px 56px rgba(0,0,0,0.48), inset 0 0 60px rgba(121,231,255,0.07), inset 0 -18px 42px rgba(217,76,255,0.07) !important;
  padding: 0.18rem !important;
}
.living-vitals-rail {
  display: grid;
  gap: 0.62rem;
  position: relative;
  padding-left: 0.06rem;
}
.living-vitals-rail::before {
  content: "";
  position: absolute;
  left: 11px;
  top: 20px;
  bottom: 20px;
  width: 8px;
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(99,242,177,0.80), rgba(247,200,95,0.62), rgba(217,76,255,0.50));
  box-shadow: 0 0 18px rgba(99,242,177,0.34), 0 0 42px rgba(217,76,255,0.12);
}
.living-vital-pod {
  position: relative;
  overflow: hidden;
  min-height: 120px;
  border-radius: 36px 18px 34px 14px;
  padding: 0.78rem 0.84rem 0.7rem 1.18rem;
  border: 1px solid rgba(247,241,232,0.34);
  background:
    radial-gradient(circle at 88% 22%, rgba(121,231,255,0.13), transparent 30%),
    radial-gradient(ellipse at 16% 100%, rgba(99,242,177,0.10), transparent 42%),
    linear-gradient(145deg, rgba(8,24,31,0.97), rgba(7,6,12,0.92));
  box-shadow: 0 15px 36px rgba(0,0,0,0.36), inset 0 1px 0 rgba(255,255,255,0.10), inset 0 -18px 34px rgba(247,241,232,0.035);
}
.living-vital-pod::after {
  content: "";
  position: absolute;
  inset: 10px 12px auto auto;
  width: 46px;
  height: 26px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(247,241,232,0.16), transparent 68%);
  transform: rotate(-18deg);
}
.living-vital-pod.positive { border-color: rgba(99,242,177,0.52); box-shadow: 0 0 28px rgba(99,242,177,0.15), inset 0 1px 0 rgba(255,255,255,0.08); }
.living-vital-pod.negative { border-color: rgba(255,95,115,0.52); box-shadow: 0 0 28px rgba(255,95,115,0.16), inset 0 1px 0 rgba(255,255,255,0.08); }
.living-vital-pod.warning { border-color: rgba(255,191,77,0.42); }
.living-pod-value {
  color: #f7f1e8;
  font-size: 1.48rem;
  font-weight: 900;
  line-height: 1.05;
  margin-top: 0.38rem;
}
.living-vital-pod.positive .living-pod-value { color: #9cff9f; }
.living-vital-pod.negative .living-pod-value { color: #ff6f7f; }
.living-pod-note {
  color: #d9cde7;
  font-size: 0.78rem;
  font-weight: 750;
  margin-top: 0.22rem;
}
.living-sparkline {
  width: 100%;
  height: 34px;
  margin-top: 0.32rem;
  filter: drop-shadow(0 0 7px rgba(99,242,177,0.32));
}
.living-inspector {
  display: grid;
  gap: 0.62rem;
}
.inspector-module {
  position: relative;
  overflow: hidden;
  min-height: 120px;
  border: 1px solid rgba(247,241,232,0.32);
  border-radius: 24px 12px 24px 12px;
  padding: 0.88rem 0.94rem;
  background:
    radial-gradient(circle at 86% 10%, rgba(217,76,255,0.10), transparent 30%),
    radial-gradient(circle at 14% 94%, rgba(121,231,255,0.08), transparent 34%),
    linear-gradient(150deg, rgba(8,24,31,0.95), rgba(7,6,12,0.91));
  box-shadow: 0 15px 36px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.09), inset 0 0 30px rgba(121,231,255,0.035);
}
.inspector-module::before {
  content: "";
  position: absolute;
  right: 0.82rem;
  top: 0.82rem;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #79e7ff;
  box-shadow: 0 0 14px rgba(121,231,255,0.66);
}
.inspector-module.verified { border-color: rgba(125,255,178,0.52); }
.inspector-module.verified::before { background: #7dffb2; box-shadow: 0 0 16px rgba(125,255,178,0.70); }
.inspector-module.partial { border-color: rgba(255,191,77,0.54); }
.inspector-module.partial::before { background: #ffbf4d; box-shadow: 0 0 16px rgba(255,191,77,0.68); }
.inspector-module.fallback { border-color: rgba(255,95,115,0.54); }
.inspector-module.fallback::before { background: #ff5f73; box-shadow: 0 0 16px rgba(255,95,115,0.68); }
.module-value {
  color: #f7f1e8;
  font-size: 1.46rem;
  line-height: 1.05;
  font-weight: 900;
  margin-top: 0.24rem;
}
.module-value.small {
  font-size: 1.02rem;
  word-break: break-word;
}
.module-note {
  color: #d9cde7;
  margin-top: 0.22rem;
  font-size: 0.76rem;
  font-weight: 700;
}
.inspector-row {
  display: flex;
  justify-content: space-between;
  gap: 0.7rem;
  align-items: baseline;
  margin-top: 0.4rem;
  color: #a99bb9;
  font-size: 0.78rem;
}
.inspector-row strong {
  color: #f7f1e8;
  text-align: right;
  font-weight: 850;
}
.status-meter {
  height: 8px;
  border-radius: 999px;
  overflow: hidden;
  margin-top: 0.62rem;
  background: rgba(247,241,232,0.10);
}
.status-meter span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #79e7ff, #63f2b1, #f7c85f);
  box-shadow: 0 0 14px rgba(99,242,177,0.38);
}
.living-trade-section {
  margin-top: 0.68rem;
  border: 1px solid rgba(247,241,232,0.26);
  border-radius: 8px;
  padding: 0.64rem 0.7rem 0.82rem 0.7rem;
  background:
    radial-gradient(circle at 24% 50%, rgba(99,242,177,0.09), transparent 30%),
    linear-gradient(135deg, rgba(247,241,232,0.90), rgba(218,214,204,0.82));
  box-shadow: 0 18px 44px rgba(0,0,0,0.30), inset 0 1px 0 rgba(255,255,255,0.62);
}
.living-trade-title {
  color: #17121d;
  font-weight: 900;
  font-size: 1.02rem;
  margin: 0.58rem 0 0 0;
  padding: 0.54rem 0.82rem 0.16rem 0.82rem;
  border: 1px solid rgba(247,241,232,0.48);
  border-bottom: 0;
  border-radius: 28px 28px 0 0;
  background:
    radial-gradient(circle at 24% 50%, rgba(99,242,177,0.13), transparent 32%),
    linear-gradient(135deg, rgba(255,250,242,0.96), rgba(218,214,204,0.86));
  box-shadow: 0 -6px 26px rgba(0,0,0,0.18), inset 0 1px 0 rgba(255,255,255,0.68);
}
.living-trade-tape {
  position: relative;
  display: flex;
  gap: 1rem;
  align-items: stretch;
  overflow-x: auto;
  padding: 0.74rem 0.86rem 0.88rem 0.86rem;
  border: 1px solid rgba(247,241,232,0.48);
  border-top: 0;
  border-radius: 0 0 28px 28px;
  background:
    radial-gradient(circle at 24% 50%, rgba(99,242,177,0.12), transparent 32%),
    radial-gradient(circle at 78% 60%, rgba(217,76,255,0.10), transparent 30%),
    linear-gradient(135deg, rgba(255,250,242,0.92), rgba(213,206,194,0.84));
  box-shadow: 0 18px 48px rgba(0,0,0,0.34), inset 0 1px 0 rgba(255,255,255,0.70), inset 0 -20px 42px rgba(7,6,12,0.06);
}
.seed-rail {
  position: absolute;
  left: 0.7rem;
  right: 0.7rem;
  top: 50%;
  height: 8px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(99,242,177,0.72), rgba(247,200,95,0.78), rgba(255,95,115,0.54));
  box-shadow: 0 0 16px rgba(99,242,177,0.34), 0 0 34px rgba(217,76,255,0.10);
  transform: translateY(-50%);
}
.trade-seed {
  position: relative;
  z-index: 1;
  flex: 0 0 152px;
  min-height: 116px;
  border-radius: 54px 32px 48px 30px;
  padding: 0.64rem 0.68rem 0.58rem 0.68rem;
  background:
    radial-gradient(circle at 48% 36%, rgba(247,241,232,0.22), transparent 58%),
    radial-gradient(circle at 78% 18%, rgba(121,231,255,0.13), transparent 34%),
    linear-gradient(145deg, rgba(8,24,31,0.94), rgba(7,6,12,0.86));
  border: 1px solid rgba(247,241,232,0.40);
  box-shadow: 0 17px 30px rgba(0,0,0,0.38), inset 0 1px 0 rgba(255,255,255,0.14), inset 0 -16px 28px rgba(247,241,232,0.06);
}
.trade-seed::before {
  content: "";
  position: absolute;
  inset: 8px 13px auto auto;
  width: 34px;
  height: 20px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(247,241,232,0.18), transparent 70%);
  transform: rotate(-20deg);
}
.trade-seed.seed-win { border-color: rgba(99,242,177,0.64); box-shadow: 0 0 28px rgba(99,242,177,0.24), 0 15px 30px rgba(0,0,0,0.30), inset 0 1px 0 rgba(255,255,255,0.12); }
.trade-seed.seed-loss { border-color: rgba(255,95,115,0.66); box-shadow: 0 0 28px rgba(255,95,115,0.26), 0 15px 30px rgba(0,0,0,0.30), inset 0 1px 0 rgba(255,255,255,0.12); }
.trade-seed.seed-flat,
.trade-seed.seed-open { border-color: rgba(169,155,185,0.48); }
.seed-market {
  color: #f7f1e8;
  font-size: 0.82rem;
  font-weight: 900;
  line-height: 1.08;
  min-height: 28px;
  margin-top: 0.16rem;
}
.seed-side,
.seed-price {
  color: #d9cde7;
  font-size: 0.74rem;
  font-weight: 760;
  margin-top: 0.18rem;
}
.seed-side span { color: #a99bb9; }
.seed-pnl {
  color: #f7f1e8;
  font-size: 0.98rem;
  font-weight: 900;
  margin-top: 0.24rem;
}
.seed-win .seed-pnl { color: #9cff9f; }
.seed-loss .seed-pnl { color: #ff6f7f; }
.seed-empty {
  color: #17121d;
  font-weight: 850;
  padding: 1rem;
}
.living-diagnostics-panel {
  border: 1px solid rgba(121,231,255,0.16);
  border-radius: 8px;
  padding: 0.8rem;
  background: rgba(7,6,12,0.72);
}
.ref-cockpit {
  position: relative;
  display: grid;
  grid-template-columns: clamp(174px, 16.4vw, 242px) minmax(0, 1fr) clamp(224px, 21vw, 300px);
  grid-template-rows: 78px 398px 186px 132px;
  gap: 7px;
  min-height: 830px;
  padding: 12px 18px 14px 22px;
  border-radius: 30px;
  border: 1px solid rgba(72,62,52,0.54);
  color: #f7f1e8;
  background:
    radial-gradient(circle at 14% 18%, rgba(65,53,44,.16) 0 1px, transparent 1.8px),
    radial-gradient(circle at 63% 28%, rgba(36,77,61,.14) 0 1px, transparent 1.7px),
    radial-gradient(circle at 77% 74%, rgba(78,47,92,.13) 0 1.2px, transparent 2px),
    repeating-linear-gradient(8deg, rgba(54,44,36,0.045) 0 1px, transparent 1px 31px),
    repeating-linear-gradient(97deg, rgba(255,255,255,0.055) 0 1px, transparent 1px 42px),
    radial-gradient(circle at 2% 6%, rgba(99,242,177,0.13), transparent 11%),
    radial-gradient(circle at 86% 8%, rgba(217,76,255,0.10), transparent 14%),
    radial-gradient(circle at 50% 62%, rgba(83,67,49,0.18), transparent 36%),
    linear-gradient(135deg, rgba(255,252,246,0.99), rgba(231,226,216,0.97) 42%, rgba(190,181,166,0.94));
  box-shadow:
    0 26px 70px rgba(0,0,0,0.36),
    inset 0 2px 0 rgba(255,255,255,0.92),
    inset 0 -3px 0 rgba(54,44,36,0.25),
    inset 0 0 0 5px rgba(255,255,255,0.22);
  overflow: hidden;
}
.ref-cockpit::before,
.ref-cockpit::after {
  content: "";
  position: absolute;
  inset: 8px;
  pointer-events: none;
  border-radius: 25px;
  z-index: 0;
  background:
    radial-gradient(circle at 1.7% 2%, #8d755f 0 2px, rgba(47,36,30,.95) 3px, transparent 4px),
    radial-gradient(circle at 98.3% 2%, #8d755f 0 2px, rgba(47,36,30,.95) 3px, transparent 4px),
    radial-gradient(circle at 1.7% 98%, #8d755f 0 2px, rgba(47,36,30,.95) 3px, transparent 4px),
    radial-gradient(circle at 98.3% 98%, #8d755f 0 2px, rgba(47,36,30,.95) 3px, transparent 4px),
    linear-gradient(116deg, transparent 0 38%, rgba(69,56,47,.18) 38.2% 38.5%, transparent 38.8% 100%),
    linear-gradient(24deg, transparent 0 71%, rgba(36,77,61,.16) 71.2% 71.45%, transparent 71.8% 100%),
    repeating-radial-gradient(circle at 44% 49%, rgba(54,44,36,.06) 0 1px, transparent 1px 13px),
    radial-gradient(circle at 18% 72%, rgba(36,77,61,.18), transparent 8%),
    radial-gradient(circle at 74% 29%, rgba(78,47,92,.13), transparent 10%),
    linear-gradient(90deg, rgba(67,56,46,.17), transparent 7%, transparent 93%, rgba(67,56,46,.17));
  opacity: .88;
}
.ref-cockpit::after {
  inset: 16px;
  border: 1px solid rgba(255,255,255,0.58);
  box-shadow:
    inset 0 0 0 1px rgba(23,18,29,0.12),
    inset 0 16px 22px rgba(255,255,255,0.24),
    inset 0 -14px 20px rgba(64,52,43,0.13);
  background: none;
  opacity: 1;
}
.ref-botanical-rail {
  position: absolute;
  left: 7px;
  top: 108px;
  bottom: 146px;
  width: 13px;
  z-index: 1;
  opacity: .68;
  pointer-events: none;
}
.ref-botanical-rail::before {
  content: "";
  position: absolute;
  left: 5px;
  top: 0;
  bottom: 0;
  width: 3px;
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(36,104,72,.84), rgba(166,130,54,.62), rgba(113,60,132,.66));
  box-shadow: 0 0 10px rgba(99,242,177,.22);
}
.ref-botanical-rail span {
  position: absolute;
  left: 0;
  width: 10px;
  height: 18px;
  border-radius: 100% 0 100% 0;
  background: radial-gradient(circle at 40% 35%, rgba(156,255,159,.72), rgba(17,77,58,.54) 60%, transparent 73%);
  box-shadow: 0 0 8px rgba(99,242,177,.18);
}
.ref-botanical-rail span:nth-child(1) { top: 6%; transform: rotate(-18deg); }
.ref-botanical-rail span:nth-child(2) { top: 26%; transform: rotate(22deg) scale(.92); }
.ref-botanical-rail span:nth-child(3) { top: 47%; transform: rotate(-24deg) scale(.86); }
.ref-botanical-rail span:nth-child(4) { top: 68%; transform: rotate(20deg) scale(.92); }
.ref-botanical-rail span:nth-child(5) { top: 86%; transform: rotate(-16deg) scale(.78); }
.ref-icon-rail {
  position: absolute;
  right: 7px;
  top: 108px;
  bottom: 146px;
  width: 17px;
  z-index: 1;
  display: grid;
  align-content: center;
  gap: 15px;
  opacity: .76;
  pointer-events: none;
}
.ref-icon-rail span {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  border: 1px solid rgba(121,231,255,.32);
  background:
    radial-gradient(circle at 50% 50%, rgba(217,76,255,.34), rgba(8,24,31,.92) 62%);
  box-shadow: 0 0 14px rgba(121,231,255,.18), inset 0 0 0 2px rgba(247,241,232,.04);
}
.ref-icon-rail span:nth-child(2n) {
  border-color: rgba(99,242,177,.34);
  background: radial-gradient(circle at 50% 50%, rgba(99,242,177,.34), rgba(8,24,31,.92) 62%);
}
.ref-top {
  grid-column: 1 / 4;
  display: grid;
  grid-template-columns:
    clamp(220px, 17.8vw, 280px)
    clamp(176px, 14.2vw, 232px)
    minmax(232px, 1fr)
    clamp(144px, 11.5vw, 186px)
    clamp(128px, 9.8vw, 166px)
    clamp(210px, 17.4vw, 286px);
  gap: 7px;
  min-width: 0;
  z-index: 3;
}
.ref-brand,
.ref-top-module,
.ref-refresh,
.ref-pod,
.ref-chart-panel,
.ref-lower-left,
.ref-lower-right,
.ref-side-module,
.ref-seed-tape,
.ref-diagnostics {
  position: relative;
  overflow: hidden;
  z-index: 2;
  border: 1px solid rgba(247,241,232,0.30);
  background:
    radial-gradient(circle at 82% 13%, rgba(121,231,255,0.12), transparent 30%),
    radial-gradient(circle at 23% 106%, rgba(217,76,255,0.08), transparent 35%),
    linear-gradient(145deg, rgba(8,24,31,0.98), rgba(7,6,12,0.95));
  box-shadow:
    0 10px 22px rgba(0,0,0,0.28),
    0 0 0 1px rgba(58,49,42,0.32),
    inset 0 1px 0 rgba(255,255,255,0.13),
    inset 0 0 0 1px rgba(3,10,14,0.92),
    inset 0 0 34px rgba(121,231,255,0.055);
}
.ref-brand::before,
.ref-top-module::before,
.ref-refresh::before,
.ref-pod::before,
.ref-chart-panel::before,
.ref-lower-left::before,
.ref-lower-right::before,
.ref-side-module::before,
.ref-seed-tape::before,
.ref-diagnostics::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(circle at 17% 23%, rgba(247,241,232,.10) 0 1px, transparent 1.8px),
    radial-gradient(circle at 71% 64%, rgba(121,231,255,.08) 0 1px, transparent 1.6px),
    repeating-linear-gradient(112deg, rgba(255,255,255,.026) 0 1px, transparent 1px 19px),
    repeating-linear-gradient(21deg, rgba(0,0,0,.05) 0 1px, transparent 1px 27px);
  opacity: .64;
}
.ref-brand::after,
.ref-top-module::after,
.ref-refresh::after,
.ref-pod::after,
.ref-chart-panel::after,
.ref-lower-left::after,
.ref-lower-right::after,
.ref-side-module::after,
.ref-seed-tape::after,
.ref-diagnostics::after {
  content: "";
  position: absolute;
  inset: 3px;
  border-radius: inherit;
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow:
    inset 0 8px 16px rgba(255,255,255,0.035),
    inset 0 -10px 18px rgba(0,0,0,0.20);
  pointer-events: none;
  z-index: 0;
}
.ref-brand > *,
.ref-top-module > *,
.ref-refresh > *,
.ref-pod > *,
.ref-chart-panel > *,
.ref-lower-left > *,
.ref-lower-right > *,
.ref-side-module > *,
.ref-seed-tape > *,
.ref-diagnostics > * {
  position: relative;
  z-index: 1;
}
.ref-brand {
  display: grid;
  grid-template-columns: 56px minmax(0, 1fr);
  gap: 9px;
  align-items: center;
  padding: 9px 12px;
  border-radius: 23px 11px 23px 11px;
  border-color: rgba(54,44,36,0.44);
  color: #17121d;
  background:
    radial-gradient(circle at 12% 24%, rgba(99,242,177,0.16), transparent 30%),
    radial-gradient(circle at 89% 34%, rgba(54,44,36,0.10), transparent 24%),
    linear-gradient(135deg, rgba(255,252,246,0.99), rgba(224,219,208,0.94));
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.84),
    inset 0 -1px 0 rgba(54,44,36,0.18),
    0 10px 18px rgba(0,0,0,0.16);
}
.ref-orb {
  width: 48px;
  height: 48px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at 50% 44%, rgba(156,255,159,0.38), rgba(9,44,53,0.90) 48%, #07060c 72%);
  border: 1px solid rgba(7,6,12,0.72);
  box-shadow: 0 0 22px rgba(99,242,177,0.38), inset 0 0 18px rgba(121,231,255,0.18);
}
.ref-orb span {
  color: #9cff9f;
  font-weight: 950;
  font-size: .82rem;
}
.ref-brand-title {
  font-size: 1.22rem;
  font-weight: 950;
  line-height: 1;
}
.ref-brand-sub,
.ref-title {
  font-size: .92rem;
  font-weight: 900;
  text-transform: uppercase;
}
.ref-brand-micro,
.ref-sub,
.ref-note,
.ref-command-note {
  color: #a99bb9;
  font-size: .64rem;
  font-weight: 760;
  line-height: 1.25;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ref-brand-micro {
  color: rgba(23,18,29,.68);
}
.ref-top-module,
.ref-refresh {
  border-radius: 20px 9px 20px 9px;
  padding: 8px 12px;
}
.ref-dataset {
  color: #f7f1e8;
}
.ref-label {
  color: #a99bb9;
  font-size: .59rem;
  font-weight: 900;
  text-transform: uppercase;
}
.ref-select-text,
.ref-main {
  color: #f7f1e8;
  font-size: .94rem;
  line-height: 1.04;
  font-weight: 900;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ref-refresh {
  display: grid;
  place-items: center;
  text-align: center;
  border-color: rgba(217,76,255,.46);
  background:
    radial-gradient(circle at 77% 30%, rgba(99,242,177,.24), transparent 32%),
    linear-gradient(135deg, rgba(58,21,82,.98), rgba(12,9,18,.96));
  box-shadow:
    0 0 24px rgba(217,76,255,.24),
    inset 0 1px 0 rgba(255,255,255,.14),
    inset 0 0 0 1px rgba(3,10,14,.86);
}
.ref-refresh div:nth-child(2),
.ref-refresh span {
  color: #d9cde7;
  font-size: .68rem;
  font-weight: 850;
  text-transform: uppercase;
}
.ref-meter {
  height: 6px;
  border-radius: 999px;
  background: rgba(247,241,232,.13);
  overflow: hidden;
  margin-top: 8px;
}
.ref-meter span {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #79e7ff, #63f2b1, #f7c85f);
  box-shadow: 0 0 14px rgba(99,242,177,.42);
}
.ref-left {
  grid-column: 1;
  grid-row: 2 / 4;
  display: grid;
  grid-template-rows: repeat(5, minmax(0, 1fr));
  gap: 7px;
  z-index: 2;
}
.ref-pod {
  min-height: 0;
  border-radius: 21px 10px 24px 10px;
  padding: 10px 12px 9px 14px;
}
.ref-pod::before {
  content: "";
  position: absolute;
  left: 7px;
  top: 13px;
  bottom: 13px;
  width: 4px;
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(99,242,177,.84), rgba(247,200,95,.58), rgba(217,76,255,.54));
  box-shadow: 0 0 12px rgba(99,242,177,.34);
}
.ref-pod-value {
  margin-top: 6px;
  color: #f7f1e8;
  font-size: 1.36rem;
  line-height: 1;
  font-weight: 950;
}
.ref-pod .living-sparkline {
  height: 28px;
  margin-top: .22rem;
}
.ref-pod.gain .ref-pod-value,
.ref-row b,
.ref-side-module.verified .ref-main {
  color: #9cff9f;
}
.ref-pod.loss .ref-pod-value,
.ref-side-module.fallback .ref-main {
  color: #ff6f7f;
}
.ref-chart-panel {
  grid-column: 2;
  grid-row: 2;
  border-radius: 31px 14px 25px 12px;
  padding: 12px 14px 10px;
  border-color: rgba(238,230,217,0.40);
  background:
    radial-gradient(circle at 28% 12%, rgba(156,255,159,.14), transparent 24%),
    radial-gradient(circle at 70% 72%, rgba(217,76,255,.14), transparent 28%),
    linear-gradient(145deg, rgba(8,24,31,.99), rgba(7,6,12,.96));
  box-shadow:
    0 12px 22px rgba(0,0,0,0.30),
    0 0 0 1px rgba(76,66,58,0.36),
    inset 0 0 0 2px rgba(3,10,14,0.74),
    inset 0 16px 28px rgba(121,231,255,0.05),
    inset 0 -18px 30px rgba(0,0,0,0.34);
}
.ref-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  position: relative;
  z-index: 2;
}
.ref-panel-head.tight {
  margin-bottom: 6px;
}
.ref-title {
  color: #f7f1e8;
  font-size: .96rem;
  letter-spacing: 0 !important;
}
.ref-pills {
  display: flex;
  gap: 6px;
}
.ref-pills span {
  border: 1px solid rgba(121,231,255,.22);
  border-radius: 8px;
  padding: 4px 9px;
  color: #d9cde7;
  background: rgba(7,6,12,.52);
  font-size: .68rem;
  font-weight: 850;
}
.ref-pills .active {
  color: #17121d;
  background: linear-gradient(135deg, #9cff9f, #f7c85f);
}
.ref-equity-svg,
.ref-roots-svg {
  display: block;
  width: 100%;
  height: calc(100% - 34px);
  margin-top: 4px;
}
.ref-chart-bg {
  fill: rgba(7,6,12,.24);
}
.ref-contour {
  fill: none;
  stroke-width: 1;
  opacity: .58;
}
.ref-contour-0 { stroke: rgba(121,231,255,.24); }
.ref-contour-1 { stroke: rgba(247,200,95,.20); }
.ref-contour-2 { stroke: rgba(217,76,255,.20); }
.ref-mycelium {
  fill: none;
  stroke-width: .9;
  stroke-linecap: round;
  stroke-dasharray: 2 8;
}
.ref-field-spore {
  opacity: .46;
  filter: drop-shadow(0 0 5px currentColor);
}
.ref-zero {
  stroke: rgba(247,241,232,.26);
  stroke-width: 1;
}
.ref-draw-area {
  fill: url(#rootFill);
}
.ref-draw-line {
  fill: none;
  stroke: rgba(255,95,115,.72);
  stroke-width: 2.2;
}
.ref-root,
.ref-dd-root {
  fill: none;
  stroke: rgba(255,95,115,.28);
  stroke-width: 1.15;
}
.ref-dd-fork {
  fill: none;
  stroke: rgba(247,200,95,.21);
  stroke-width: .95;
  stroke-linecap: round;
}
.ref-dd-drip {
  fill: none;
  stroke: rgba(255,95,115,.38);
  stroke-width: 1.25;
  stroke-linecap: round;
  filter: drop-shadow(0 0 6px rgba(255,95,115,.38));
}
.ref-vine-glow,
.ref-vine {
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.ref-vine-glow.wide {
  stroke: rgba(156,255,159,.13);
  stroke-width: 24;
  filter: url(#vineGlow);
}
.ref-vine-glow.mid {
  stroke: rgba(247,227,111,.32);
  stroke-width: 10;
}
.ref-vine {
  stroke: url(#vineStroke);
  stroke-width: 3.6;
  filter: url(#vineGlow);
}
.ref-node {
  stroke: rgba(247,241,232,.88);
  stroke-width: 1.2;
}
.ref-node.gain { fill: #9cff9f; }
.ref-node.loss { fill: #ff5f73; }
.ref-node.flat { fill: #d9cde7; }
.ref-axis text {
  fill: #a99bb9;
  font-size: 10px;
  font-weight: 800;
}
.ref-callout line {
  stroke: rgba(247,200,95,.68);
  stroke-width: 1;
}
.ref-callout rect {
  fill: rgba(8,24,31,.92);
  stroke: rgba(247,200,95,.58);
}
.ref-callout text {
  fill: #f7f1e8;
  font-size: 11px;
  font-weight: 900;
}
.ref-lower-left,
.ref-lower-right {
  grid-row: 3;
  border-radius: 26px 9px 22px 13px;
  padding: 11px 13px;
}
.ref-lower-left { grid-column: 2; width: calc(50% - 4px); }
.ref-lower-right { grid-column: 2; margin-left: calc(50% + 4px); }
.ref-dd-line {
  fill: none;
  stroke: #ff6f7f;
  stroke-width: 2.4;
  filter: drop-shadow(0 0 8px rgba(255,95,115,.58));
}
.ref-right {
  grid-column: 3;
  grid-row: 2 / 4;
  display: grid;
  grid-template-rows: 1.08fr .9fr .96fr .78fr;
  gap: 7px;
  z-index: 2;
}
.ref-side-module {
  min-height: 0;
  border-radius: 21px 10px 21px 10px;
  padding: 11px 13px;
}
.ref-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: baseline;
  margin-top: 6px;
  color: #a99bb9;
  font-size: .72rem;
  font-weight: 760;
}
.ref-market,
.ref-lock-ring {
  color: #f7f1e8;
  font-size: 1.22rem;
  font-weight: 950;
  margin-top: 5px;
}
.ref-light-row {
  display: flex;
  gap: 8px;
  margin-top: 14px;
}
.ref-light-row span {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #9cff9f;
  box-shadow: 0 0 10px rgba(156,255,159,.76);
}
.ref-seed-tape {
  grid-column: 1 / 3;
  grid-row: 4;
  border-radius: 25px 11px 25px 11px;
  color: #17121d;
  padding: 10px 16px 9px;
  border-color: rgba(66,54,45,0.36);
  background:
    radial-gradient(circle at 20% 54%, rgba(99,242,177,.14), transparent 24%),
    radial-gradient(circle at 62% 48%, rgba(247,200,95,.10), transparent 22%),
    linear-gradient(135deg, rgba(255,252,246,.97), rgba(222,216,205,.92));
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.86),
    inset 0 -1px 0 rgba(60,48,40,.20),
    0 10px 18px rgba(0,0,0,0.17);
}
.ref-seed-tape::before {
  content: "";
  position: absolute;
  left: 38px;
  right: 38px;
  top: 46px;
  bottom: 13px;
  border-radius: 999px;
  border: 1px solid rgba(54,44,36,0.18);
  background: linear-gradient(180deg, rgba(255,255,255,.24), rgba(96,82,70,.12));
  box-shadow:
    inset 0 8px 16px rgba(0,0,0,.12),
    inset 0 -8px 14px rgba(255,255,255,.20);
  pointer-events: none;
  z-index: 0;
}
.ref-seed-title {
  color: #17121d;
  position: relative;
  z-index: 2;
  font-size: .92rem;
  font-weight: 950;
  text-transform: uppercase;
}
.ref-seed-title span {
  color: rgba(23,18,29,.58);
  font-size: .66rem;
  margin-left: 12px;
}
.ref-seed-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 5px;
  color: rgba(23,18,29,.64);
  font-size: .66rem;
  font-weight: 900;
  text-transform: uppercase;
}
.ref-seed-rail {
  position: absolute;
  left: 56px;
  right: 56px;
  bottom: 43px;
  height: 5px;
  border-radius: 999px;
  background: linear-gradient(90deg, #63f2b1, #f7c85f, #ff5f73, #63f2b1);
  box-shadow: 0 0 13px rgba(99,242,177,.34);
  z-index: 1;
}
.ref-seeds-inner {
  position: relative;
  z-index: 2;
  display: flex;
  gap: 12px;
  align-items: stretch;
  overflow: hidden;
  padding: 7px 4px 0;
}
.ref-seed {
  flex: 1 1 0;
  min-width: 104px;
  max-width: 146px;
  min-height: 72px;
  border-radius: 48px 36px 44px 32px;
  padding: 8px 10px;
  text-align: center;
  color: #f7f1e8;
  border: 1px solid rgba(247,241,232,.42);
  background:
    radial-gradient(circle at 50% 44%, rgba(247,241,232,.20), transparent 62%),
    linear-gradient(145deg, rgba(8,24,31,.95), rgba(7,6,12,.90));
  box-shadow:
    0 9px 18px rgba(0,0,0,.28),
    inset 0 1px 0 rgba(255,255,255,.14),
    inset 0 -9px 16px rgba(0,0,0,.24);
}
.ref-seed.win { border-color: rgba(99,242,177,.62); box-shadow: 0 0 22px rgba(99,242,177,.25), inset 0 1px 0 rgba(255,255,255,.14), inset 0 -9px 16px rgba(0,0,0,.22); }
.ref-seed.loss { border-color: rgba(255,95,115,.62); box-shadow: 0 0 22px rgba(255,95,115,.25), inset 0 1px 0 rgba(255,255,255,.14), inset 0 -9px 16px rgba(0,0,0,.22); }
.ref-seed.flat { border-color: rgba(217,76,255,.48); box-shadow: 0 0 18px rgba(217,76,255,.22), inset 0 1px 0 rgba(255,255,255,.14), inset 0 -9px 16px rgba(0,0,0,.22); }
.ref-seed-time,
.ref-seed-price {
  color: #a99bb9;
  font-size: .58rem;
  font-weight: 800;
}
.ref-seed-market {
  margin-top: 3px;
  font-size: .70rem;
  font-weight: 950;
  line-height: 1.05;
}
.ref-seed-side {
  color: #d9cde7;
  font-size: .64rem;
  font-weight: 850;
  margin-top: 2px;
}
.ref-seed-pnl {
  color: #9cff9f;
  font-size: .76rem;
  font-weight: 950;
  margin-top: 3px;
}
.ref-seed.loss .ref-seed-pnl { color: #ff6f7f; }
.ref-diagnostics {
  grid-column: 3;
  grid-row: 4;
  border-radius: 24px 10px 24px 10px;
  padding: 11px 13px;
}
.ref-diagnostics .ref-title span,
.ref-title span {
  color: #d9cde7;
  border: 1px solid rgba(217,76,255,.34);
  border-radius: 999px;
  padding: 2px 8px;
  margin-left: 6px;
  font-size: .62rem;
}
.ref-empty {
  color: #a99bb9;
  padding: 2rem;
  font-weight: 850;
}
@media (max-height: 820px) and (min-width: 1000px) {
  .ref-cockpit {
    grid-template-rows: 68px 322px 148px 108px;
    gap: 6px;
    min-height: 710px;
    padding: 10px 16px 12px 20px;
  }
  .ref-top {
    gap: 6px;
  }
  .ref-brand {
    grid-template-columns: 48px minmax(0, 1fr);
    padding: 8px 10px;
  }
  .ref-orb {
    width: 42px;
    height: 42px;
  }
  .ref-brand-title {
    font-size: 1.08rem;
  }
  .ref-top-module,
  .ref-refresh {
    padding: 7px 10px;
  }
  .ref-select-text,
  .ref-main {
    font-size: .86rem;
    margin-top: 3px;
  }
  .ref-left,
  .ref-right {
    gap: 6px;
  }
  .ref-pod {
    padding: 8px 10px 7px 13px;
  }
  .ref-pod-value {
    font-size: 1.12rem;
    margin-top: 4px;
  }
  .ref-pod .living-sparkline {
    height: 20px;
    margin-top: .14rem;
  }
  .ref-side-module,
  .ref-lower-left,
  .ref-lower-right,
  .ref-diagnostics {
    padding: 9px 11px;
  }
  .ref-row {
    margin-top: 4px;
    font-size: .66rem;
  }
  .ref-market,
  .ref-lock-ring {
    font-size: 1.05rem;
  }
  .ref-seed-tape {
    padding: 8px 14px;
  }
  .ref-seed-tape::before {
    top: 38px;
    bottom: 10px;
  }
  .ref-seed-title {
    font-size: .82rem;
  }
  .ref-seed-rail {
    bottom: 33px;
  }
  .ref-seeds-inner {
    gap: 9px;
    padding-top: 5px;
  }
  .ref-seed {
    min-height: 58px;
    min-width: 92px;
    padding: 6px 8px;
  }
  .ref-seed-time,
  .ref-seed-price {
    font-size: .52rem;
  }
  .ref-seed-market {
    font-size: .63rem;
  }
  .ref-seed-side,
  .ref-seed-pnl {
    font-size: .58rem;
  }
}
@media (max-width: 1180px) and (min-width: 761px) {
  .ref-cockpit {
    grid-template-rows: 146px 360px 168px 126px;
  }
  .ref-top {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    grid-template-rows: repeat(2, minmax(0, 1fr));
  }
}
@media (max-height: 820px) and (min-width: 1000px) and (max-width: 1180px) {
  .ref-cockpit {
    grid-template-rows: 122px 298px 132px 96px;
    min-height: 686px;
  }
  .ref-top {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    grid-template-rows: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 760px) {
  .ref-cockpit {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    min-height: 0;
    padding: 10px;
  }
  .ref-botanical-rail,
  .ref-icon-rail {
    display: none;
  }
  .ref-top,
  .ref-left,
  .ref-chart-panel,
  .ref-lower-left,
  .ref-lower-right,
  .ref-right,
  .ref-seed-tape,
  .ref-diagnostics {
    grid-column: 1;
    grid-row: auto;
    width: auto;
    margin-left: 0;
  }
  .ref-top {
    grid-template-columns: 1fr 1fr;
  }
  .ref-left,
  .ref-right {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    grid-template-rows: none;
  }
}
* {
  letter-spacing: 0 !important;
}
.latency-strip {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.6rem;
  margin-top: 0.65rem;
}
.latency-strip div {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.68rem;
  background: #ffffff;
  box-shadow: 0 8px 22px rgba(31,44,67,0.06);
}
.latency-strip span {
  display: block;
  color: var(--muted);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 800;
}
.latency-strip strong {
  display: block;
  color: var(--text);
  font-size: 1.05rem;
  margin-top: 0.24rem;
}
.visualizer-hero {
  padding: 1.2rem 1.25rem;
  border-radius: 8px;
  border: 1px solid rgba(123,212,255,0.14);
  background: var(--card);
  box-shadow: var(--shadow);
  margin: 0.45rem 0 1rem 0;
}
.visualizer-kicker {
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: var(--blue);
  margin-bottom: 0.35rem;
}
.visualizer-title {
  font-size: 1.9rem;
  color: var(--text);
  font-weight: 700;
  letter-spacing: 0;
  line-height: 1.05;
}
.visualizer-sub {
  color: var(--muted);
  max-width: 70rem;
  line-height: 1.55;
  margin-top: 0.4rem;
}
.visualizer-strip {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0.8rem;
  margin: 0.95rem 0 1.15rem 0;
}
.visualizer-chip {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.85rem 0.9rem;
  background: var(--card);
}
.visualizer-chip-label {
  font-size: 0.74rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 0.24rem;
}
.visualizer-chip-value {
  color: var(--text);
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.1;
}
.visualizer-chip-note {
  color: var(--muted);
  font-size: 0.82rem;
  margin-top: 0.2rem;
}
.visualizer-panel {
  margin-bottom: 1.1rem;
}
.visualizer-section-title {
  font-size: 1.08rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 0.18rem;
}
.visualizer-section-sub {
  color: var(--muted);
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 0.7rem;
}
@media (max-width: 1200px) {
  .visualizer-strip {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
@media (max-width: 900px) {
  .visualizer-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
.insight-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
  margin: 0.35rem 0 1rem 0;
}
.insight-card {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.95rem 1rem;
  background: var(--card);
}
.insight-card strong {
  display: block;
  color: var(--text);
  margin-bottom: 0.35rem;
}
.insight-card span {
  color: var(--muted);
  line-height: 1.5;
  font-size: 0.93rem;
}
.summary-band {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem 1.05rem;
  background: var(--card);
  margin: 0.35rem 0 1rem 0;
}
.summary-band h4 {
  margin: 0 0 0.35rem 0;
  color: var(--text);
  font-size: 1.05rem;
}
.summary-band p {
  margin: 0;
  color: var(--muted);
  line-height: 1.55;
}
.signal-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
}
.signal-stat {
  padding: 0.8rem 0.85rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: #f8fafc;
}
.signal-stat strong {
  display: block;
  color: var(--text);
  font-size: 1rem;
  margin-top: 0.18rem;
}
.log-box {
  background: #111827;
  color: #e5e7eb;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid var(--border-strong);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
  font-family: "JetBrains Mono", Consolas, Monaco, monospace;
  font-size: 0.85rem;
  max-height: 560px;
  overflow: auto;
  white-space: pre-wrap;
}
.event-good { color: var(--green); font-weight: 600; }
.event-bad { color: var(--red); font-weight: 600; }
.event-warn { color: var(--yellow); font-weight: 600; }
.stSegmentedControl [data-baseweb="button-group"] {
  background: rgba(7,6,12,0.68) !important;
  border: 1px solid rgba(121,231,255,0.20) !important;
  border-radius: 8px !important;
  padding: 0.18rem !important;
}
.stSegmentedControl button {
  border-radius: 6px !important;
  color: #d9cde7 !important;
  background: rgba(8,24,31,0.62) !important;
  border-color: rgba(121,231,255,0.10) !important;
}
.stSegmentedControl button[aria-pressed="true"] {
  background: linear-gradient(135deg, rgba(9,44,53,0.92), rgba(53,19,76,0.82)) !important;
  border-color: rgba(99,242,177,0.38) !important;
  color: #9cff9f !important;
}
div[data-testid="stSegmentedControl"] button,
div[data-testid="stButtonGroup"] button {
  background: rgba(8,24,31,0.72) !important;
  color: #d9cde7 !important;
  border: 1px solid rgba(121,231,255,0.14) !important;
}
div[data-testid="stSegmentedControl"] button *,
div[data-testid="stButtonGroup"] button * {
  color: inherit !important;
}
div[data-testid="stSegmentedControl"] button[aria-pressed="true"],
div[data-testid="stSegmentedControl"] button[aria-selected="true"],
div[data-testid="stSegmentedControl"] button[aria-checked="true"],
div[data-testid="stButtonGroup"] button[aria-pressed="true"],
div[data-testid="stButtonGroup"] button[aria-selected="true"],
div[data-testid="stButtonGroup"] button[aria-checked="true"] {
  background: linear-gradient(135deg, rgba(9,44,53,0.94), rgba(53,19,76,0.82)) !important;
  color: #9cff9f !important;
  border-color: rgba(99,242,177,0.42) !important;
}
button[data-testid="stBaseButton-secondary"] {
  background: rgba(8,24,31,0.72) !important;
  color: #d9cde7 !important;
  border: 1px solid rgba(121,231,255,0.14) !important;
}
button[data-testid="stBaseButton-secondary"][aria-pressed="true"],
button[data-testid="stBaseButton-secondary"][aria-selected="true"] {
  background: linear-gradient(135deg, rgba(9,44,53,0.94), rgba(53,19,76,0.82)) !important;
  color: #9cff9f !important;
  border-color: rgba(99,242,177,0.42) !important;
}
.stTabs [data-baseweb="tab-list"] {
  gap: 0.55rem;
  background: var(--card);
  border: 1px solid var(--border);
  padding: 0.45rem;
  border-radius: 8px;
}
.stTabs [data-baseweb="tab"] {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  padding: 0.7rem 1.1rem;
  color: var(--muted);
  transition: all 160ms ease;
}
.stTabs [aria-selected="true"] {
  background: var(--blue-soft) !important;
  border-color: rgba(37,99,235,0.28) !important;
  color: var(--text) !important;
}
div[data-testid="stMetric"] {
  background: var(--card);
  border-radius: 18px;
  padding: 0.2rem 0.1rem;
}
div[data-testid="stMetric"] label {
  color: var(--muted) !important;
}
div[data-testid="stMetricValue"] {
  color: var(--text);
}
div[data-testid="stMetricDelta"] {
  color: var(--blue);
}
div[data-testid="stVerticalBlock"] > div:has(> div .metric-shell) {
  height: 100%;
}
h2, h3 {
  letter-spacing: 0;
}
@media (max-width: 1200px) {
  .console-header-grid,
  .kpi-band,
  .overview-band,
  .pl-kpi-grid,
  .live-strip,
  .ops-layout,
  .health-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .operator-brief {
    grid-column: 1 / -1;
  }
}
@media (max-height: 800px) and (min-width: 1000px) {
  .living-trade-title {
    margin-top: 0.55rem;
  }
  .living-trade-tape {
    max-height: 128px;
    overflow-x: auto;
    overflow-y: hidden;
  }
  .trade-seed {
    flex-basis: 124px;
    min-height: 78px;
    padding: 0.48rem 0.54rem;
  }
  .seed-market {
    font-size: 0.76rem;
    min-height: 22px;
  }
  .seed-side,
  .seed-price,
  .seed-time {
    font-size: 0.68rem;
  }
  .seed-pnl {
    font-size: 0.86rem;
  }
}
@media (max-width: 900px) {
  .console-title {
    font-size: 1.7rem;
  }
  .console-header-grid,
  .kpi-band,
  .overview-band,
  .pl-kpi-grid,
  .live-strip,
  .ops-layout,
  .brief-metric-grid,
  .health-grid {
    grid-template-columns: 1fr;
  }
  .trade-tape-row {
    grid-template-columns: 1fr;
  }
  .trade-tape-pnl {
    text-align: left;
  }
  .insight-grid {
    grid-template-columns: 1fr;
  }
  .signal-grid {
    grid-template-columns: 1fr;
  }
}
</style>
    """,
    unsafe_allow_html=True,
)

if "refresh_seconds" not in st.session_state:
    st.session_state.refresh_seconds = 0
if "dataset_tag" not in st.session_state:
    st.session_state.dataset_tag = current_strategy_tag()
if "equity_range" not in st.session_state:
    st.session_state.equity_range = "ALL"
if "seed_filter" not in st.session_state:
    st.session_state.seed_filter = "ALL"
if "active_view" not in st.session_state:
    st.session_state.active_view = "Overview"
if "dashboard_view_picker" not in st.session_state:
    st.session_state.dashboard_view_picker = st.session_state.active_view


def dashboard_strategy_context(tag: str) -> dict[str, Any]:
    raw = sanitize_strategy_tag(str(tag)).lower()
    mode = "Live" if raw.startswith("live") or "_live" in raw else "Research"
    chips: list[str] = [mode]
    if "mushroom" in raw and "v28" in raw:
        chips.append("Mushroom V28")
    elif "v28" in raw:
        chips.append("V28")
    if "common_clock" in raw:
        chips.append("Common clock")
    if "phi_reward_memory" in raw:
        chips.append("Phi reward memory")
    if "adaptive_exit" in raw:
        chips.append("Adaptive exit")
    if "exit_guard" in raw:
        chips.append("Exit guard")
    if "hybridfpt" in raw:
        chips.append("Hybrid FPT")
    if "btcrest" in raw:
        chips.append("BTC residual")
    if "sourcefix" in raw:
        chips.append("Source-fixed")
    if "size2" in raw or "size_2" in raw:
        chips.append("Size 2")
    family = "Mushroom V28" if "mushroom" in raw and "v28" in raw else "BTC15M"
    unique_chips = list(dict.fromkeys(chips))
    return {
        "mode": mode,
        "family": family,
        "chips": unique_chips[:4],
    }


dataset_options = discover_datasets()
dataset_labels = [d["tag"] for d in dataset_options]
dataset_label_map = {str(d["tag"]): str(d.get("label") or humanize_strategy_tag(str(d["tag"]))) for d in dataset_options}
if st.session_state.dataset_tag not in dataset_labels and dataset_labels:
    st.session_state.dataset_tag = dataset_labels[0]
if "dataset_tag_picker" not in st.session_state or st.session_state.dataset_tag_picker not in dataset_labels:
    st.session_state.dataset_tag_picker = st.session_state.dataset_tag

refresh_options = {
    "Manual": 0,
    "Every 10s": 10,
    "Every 30s": 30,
    "Every 60s": 60,
}
if st.session_state.refresh_seconds not in set(refresh_options.values()):
    st.session_state.refresh_seconds = 0
current_refresh_label = next(
    (label for label, seconds in refresh_options.items() if seconds == st.session_state.refresh_seconds),
    "Manual",
)
if "refresh_label_picker" not in st.session_state or st.session_state.refresh_label_picker not in refresh_options:
    st.session_state.refresh_label_picker = current_refresh_label

view_options = ["Overview", "Visualizer", "Research Lab", "BTC today map", "Loss diagnostics", "Strategy optimizer"]

with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-shell">
          <div class="sidebar-kicker">BTC15M</div>
          <div class="sidebar-title">Operational drawers</div>
          <div class="sidebar-sub">Reference cockpit controls.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    selected_dataset_tag = st.selectbox(
        "Dataset",
        dataset_labels,
        index=dataset_labels.index(st.session_state.dataset_tag) if dataset_labels else 0,
        format_func=lambda tag: dataset_label_map.get(str(tag), humanize_strategy_tag(str(tag))),
        help="Each strategy writes to its own logs, state, and scored stats. Switch here to compare the current live profile against archived research datasets without losing history.",
        key="dataset_tag_picker",
    )
if selected_dataset_tag and selected_dataset_tag != st.session_state.dataset_tag:
    st.session_state.dataset_tag = selected_dataset_tag

active_dataset = next((d for d in dataset_options if d["tag"] == st.session_state.dataset_tag), build_dataset_record(st.session_state.dataset_tag))

reference_query_handled = False
reference_action = first_query_param("dash_action").lower()
reference_range = first_query_param("dash_range").upper()
reference_seed = first_query_param("dash_seed").upper()
reference_view = first_query_param("dash_view")
if reference_range in EQUITY_RANGE_OPTIONS:
    st.session_state.equity_range = reference_range
    st.session_state[f"equity-range-{active_dataset['tag']}"] = reference_range
    reference_query_handled = True
if reference_seed in SEED_FILTER_OPTIONS:
    st.session_state.seed_filter = reference_seed
    st.session_state[f"seed-filter-{active_dataset['tag']}"] = reference_seed
    reference_query_handled = True
if reference_action == "refresh":
    refresh_dashboard_caches()
    maybe_launch_auto_score_refresh(active_dataset, force=True)
    reference_query_handled = True
if reference_view in view_options:
    st.session_state.active_view = reference_view
    reference_query_handled = True
if reference_query_handled:
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.rerun()

with st.sidebar:
    selected_refresh_label = st.selectbox(
        "Auto refresh",
        options=list(refresh_options.keys()),
        index=list(refresh_options.keys()).index(current_refresh_label),
        help="Manual mode keeps the dashboard stable. Pick an interval only when you want it to poll live data.",
        key="refresh_label_picker",
    )
    st.session_state.refresh_seconds = refresh_options[selected_refresh_label]
    if st.button("Refresh now", key="sidebar_refresh_now", use_container_width=True):
        refresh_dashboard_caches()
        maybe_launch_auto_score_refresh(active_dataset, force=True)
        st.rerun()
    selected_sidebar_view = st.radio(
        "Dashboard view",
        options=view_options,
        index=view_options.index(st.session_state.active_view) if st.session_state.active_view in view_options else 0,
        key="dashboard_view_picker",
    )
    if selected_sidebar_view:
        st.session_state.active_view = selected_sidebar_view
    selected_equity_range = st.selectbox(
        "Equity range",
        options=list(EQUITY_RANGE_OPTIONS),
        index=list(EQUITY_RANGE_OPTIONS).index(st.session_state.get("equity_range", "ALL")) if st.session_state.get("equity_range", "ALL") in EQUITY_RANGE_OPTIONS else len(EQUITY_RANGE_OPTIONS) - 1,
        key="equity_range_picker",
    )
    st.session_state.equity_range = selected_equity_range
    st.session_state[f"equity-range-{active_dataset['tag']}"] = selected_equity_range
    selected_seed_filter = st.selectbox(
        "Trade seed filter",
        options=list(SEED_FILTER_OPTIONS),
        index=list(SEED_FILTER_OPTIONS).index(st.session_state.get("seed_filter", "ALL")) if st.session_state.get("seed_filter", "ALL") in SEED_FILTER_OPTIONS else 0,
        key="seed_filter_picker",
    )
    st.session_state.seed_filter = selected_seed_filter
    st.session_state[f"seed-filter-{active_dataset['tag']}"] = selected_seed_filter
    st.caption(f"Dataset: {dataset_label_map.get(str(active_dataset['tag']), humanize_strategy_tag(str(active_dataset['tag'])))}")
    st.caption(f"Refresh: {'Manual' if int(st.session_state.refresh_seconds) <= 0 else selected_refresh_label}")
    st.caption(f"View: {st.session_state.active_view}")
    st.caption(f"Range: {st.session_state.equity_range} / Seeds: {st.session_state.seed_filter}")
    st.caption(f"Score mode: {active_dataset.get('score_mode')}")
    bot_control = get_bot_control_config(active_dataset["tag"])
    running_now = bot_is_running(active_dataset["tag"]) if bot_control else False
    if bot_control:
        st.caption(f"Bot: {'running' if running_now else 'stopped'}")
        launch_col, kill_col = st.columns(2)
        if launch_col.button("Launch bot", width="stretch", disabled=running_now):
            ok, msg = launch_managed_bot(active_dataset["tag"])
            refresh_dashboard_caches()
            (st.success if ok else st.error)(msg)
        if kill_col.button("Kill bot", width="stretch", disabled=not running_now):
            ok, msg = stop_managed_bot(active_dataset["tag"])
            refresh_dashboard_caches()
            (st.success if ok else st.error)(msg)
    with st.expander("Sources", expanded=False):
        st.caption(f"Stats tag: {active_dataset['tag']}")
        st.caption(f"Log source: {active_dataset['log_source_tag']}")
        st.caption(f"Log: {active_dataset['log_path'].relative_to(ROOT)}")
        st.caption(f"Trades: {active_dataset['trades_path'].relative_to(ROOT)}")
        st.caption(f"Summary: {active_dataset['summary_path'].relative_to(ROOT)}")

strategy_context = dashboard_strategy_context(active_dataset["tag"])
active_dataset_label = html.escape(str(active_dataset.get("label") or humanize_strategy_tag(active_dataset["tag"])))

run_every = None if int(st.session_state.refresh_seconds) <= 0 else f"{int(st.session_state.refresh_seconds)}s"


@st.fragment(run_every=run_every)
def live_dashboard():
    active_dataset = next((d for d in discover_datasets() if d["tag"] == st.session_state.dataset_tag), build_dataset_record(st.session_state.dataset_tag))
    if int(st.session_state.refresh_seconds) > 0:
        maybe_launch_auto_score_refresh(active_dataset)
    lines = load_log(str(active_dataset["log_path"]))
    all_lines, all_log_files = load_log_bundle(str(active_dataset["log_dir"]))
    lines = filter_lines_for_dataset(lines, active_dataset["tag"], str(active_dataset.get("score_mode") or "all"))
    all_lines = filter_lines_for_dataset(all_lines, active_dataset["tag"], str(active_dataset.get("score_mode") or "all"))
    if not all_lines:
        all_lines = lines
    raw_trades = load_trades(str(active_dataset["trades_path"]))
    trades = normalize_trades(raw_trades, active_dataset["tag"])
    market_results = load_market_results(str(active_dataset["market_results_path"]))
    trades = enrich_trades_with_market_results(trades, market_results)
    summary = load_summary(str(active_dataset["summary_path"]))
    state = parse_log_state(all_lines)
    hb = state["latest_heartbeat"] or {}
    watch = state["latest_watch"] or {}
    execution_events_path = active_dataset["execution_events_path"]
    execution_events_exists = Path(execution_events_path).exists()
    price_all = make_price_series(all_lines)

    pnl_values_all = trade_pnl_series(trades)
    completed_pnl = pnl_values_all.dropna()
    wins = int((completed_pnl > 0).sum()) if not completed_pnl.empty else 0
    losses = int((completed_pnl < 0).sum()) if not completed_pnl.empty else 0
    flats = int((completed_pnl == 0).sum()) if not completed_pnl.empty else 0
    open_positions = int((trades["display_outcome"] == "open").sum()) if not trades.empty else int(summary.get("open_positions", 0) or 0)
    entries_total = int(len(trades)) if not trades.empty else int(summary.get("entries_total", 0) or 0)
    use_actuals = dataset_uses_actuals(active_dataset["tag"])

    if use_actuals and not trades.empty and "actual_gross_pnl_dollars" in trades.columns:
        net_pnl_display = float(pd.to_numeric(trades["actual_net_pnl_dollars"], errors="coerce").fillna(0.0).sum())
        cost_basis_display = float(pd.to_numeric(trades.get("actual_entry_notional_dollars"), errors="coerce").fillna(0.0).sum()) if "actual_entry_notional_dollars" in trades.columns else 0.0
        net_pnl_pct = (net_pnl_display / cost_basis_display * 100.0) if cost_basis_display else 0.0
    elif not trades.empty and "scaled_gross_pnl_dollars" in trades.columns:
        net_pnl_display = float(pd.to_numeric(trades["scaled_net_pnl_dollars"], errors="coerce").fillna(0.0).sum())
        cost_basis_display = float(pd.to_numeric(trades.get("scaled_entry_notional_dollars"), errors="coerce").fillna(0.0).sum()) if "scaled_entry_notional_dollars" in trades.columns else 0.0
        net_pnl_pct = (net_pnl_display / cost_basis_display * 100.0) if cost_basis_display else float(summary.get("gross_pnl_total_percent", 0) or 0)
    else:
        gross_pnl_display = float(summary.get("gross_pnl_total_dollars", 0) or 0)
        net_pnl_display = float(summary.get("net_pnl_total_dollars", gross_pnl_display) or 0)
        net_pnl_pct = float(summary.get("net_pnl_total_percent", summary.get("gross_pnl_total_percent", 0)) or 0)

    pnl_card_label = "Net P&L" if use_actuals else f"Net P&L @ {DISPLAY_POSITION_SIZE}"
    win_rate = round((wins / max(wins + losses, 1)) * 100.0, 2) if (wins + losses) else 0.0

    active_view = st.session_state.active_view

    if active_view == "Overview":
        heartbeat_ts = parse_ts(str(hb.get("ts") or "")) if hb else None
        heartbeat_age_seconds = (datetime.now() - heartbeat_ts).total_seconds() if heartbeat_ts else None
        current_market_label = str(watch.get("market", hb.get("watch", "NA")))
        watch_close_label = format_ma_time(watch.get("close_time")) if watch else "NA"
        yes_bid = hb.get("yes_bid")
        yes_ask = hb.get("yes_ask")
        no_bid = hb.get("no_bid")
        no_ask = hb.get("no_ask")
        yes_spread = (yes_ask - yes_bid) if yes_ask is not None and yes_bid is not None else None
        no_spread = (no_ask - no_bid) if no_ask is not None and no_bid is not None else None
        market_bias = "Balanced"
        if yes_ask is not None and no_ask is not None:
            if yes_ask - no_ask >= 8:
                market_bias = "NO pressure"
            elif no_ask - yes_ask >= 8:
                market_bias = "YES pressure"
            else:
                market_bias = "Two-way"
        latency_df = pd.DataFrame(state["latency_rows"])
        latest_lat = latency_df.tail(1).iloc[0] if not latency_df.empty else None
        feed_age_text = f"{latest_lat['feed_age_ms']:.1f} ms" if latest_lat is not None else "NA"
        reaction_text = f"{latest_lat['local_reaction_ms']:.1f} ms" if latest_lat is not None else "NA"
        heartbeat_age_text = f"{heartbeat_age_seconds:.0f}s ago" if heartbeat_age_seconds is not None else "No heartbeat"

        refresh_mode_label = "Manual" if int(st.session_state.refresh_seconds) <= 0 else f"Every {int(st.session_state.refresh_seconds)}s"
        telemetry_text = "Ready" if execution_events_exists else "Missing"
        score_age_text = format_file_age(Path(active_dataset["summary_path"]))
        accounting_status = resolve_accounting_status(summary)
        lock_status = resolve_live_lock_status(active_dataset)

        curve = make_equity_curve(trades)
        range_key = f"equity-range-{active_dataset['tag']}"
        if range_key not in st.session_state or st.session_state.get(range_key) not in EQUITY_RANGE_OPTIONS:
            st.session_state[range_key] = st.session_state.get("equity_range", "ALL")
        seed_filter_key = f"seed-filter-{active_dataset['tag']}"
        if seed_filter_key not in st.session_state or st.session_state.get(seed_filter_key) not in SEED_FILTER_OPTIONS:
            st.session_state[seed_filter_key] = st.session_state.get("seed_filter", "ALL")
        st.session_state.equity_range = st.session_state.get(range_key, "ALL")
        st.session_state.seed_filter = st.session_state.get(seed_filter_key, "ALL")
        latest_trade = sorted_recent_trades(trades, max_rows=1)
        latest_trade_label = "No trades"
        latest_trade_note = "Waiting on scored fills"
        latest_trade_class = "neutral"
        if not latest_trade.empty:
            latest_pnl = trade_pnl_series(latest_trade).iloc[0]
            latest_trade_label = format_signed_money(latest_pnl, always_sign=True)
            latest_trade_class = "positive" if pd.notna(latest_pnl) and latest_pnl > 0 else "negative" if pd.notna(latest_pnl) and latest_pnl < 0 else "neutral"
            latest_row = latest_trade.iloc[0]
            latest_trade_note = f"{str(latest_row.get('side', '')).upper() or 'NA'} {format_cents(latest_row.get('entry_fill_cents_used'))} to {format_cents(latest_row.get('exit_fill_cents_used'))}"

        if curve.empty:
            displayed_curve = pd.DataFrame(columns=["ts", "equity", "drawdown"])
            ending_equity = net_pnl_display
            range_pnl_change = net_pnl_display
            max_drawdown = 0.0
        else:
            selected_range = str(st.session_state[range_key])
            displayed_curve = add_drawdown_to_equity_curve(filter_equity_curve(curve, selected_range))
            ending_equity = float(displayed_curve["equity"].iloc[-1]) if len(displayed_curve) else net_pnl_display
            starting_equity = float(displayed_curve["equity"].iloc[0]) if len(displayed_curve) else 0.0
            range_pnl_change = ending_equity - starting_equity
            max_drawdown = float(displayed_curve["drawdown"].min()) if len(displayed_curve) else 0.0

        active_dataset_label_live = str(active_dataset.get("label") or humanize_strategy_tag(active_dataset["tag"]))
        market_price_slice = price_all
        if not market_price_slice.empty and current_market_label and current_market_label != "NA":
            market_price_slice = market_price_slice[market_price_slice["market"].astype(str).eq(current_market_label)]
        price_spark_values = pd.Series(dtype=float)
        if not market_price_slice.empty:
            yes_series = pd.to_numeric(market_price_slice.get("yes_bid"), errors="coerce")
            no_series = pd.to_numeric(market_price_slice.get("no_bid"), errors="coerce")
            price_spark_values = yes_series.fillna(no_series).dropna().tail(36)
        command_spark = sparkline_svg(price_spark_values, "#79e7ff", "rgba(121,231,255,0.12)")
        command_sync_label = format_ma_time(heartbeat_ts) if heartbeat_ts else "No sample"
        command_position = "Position open" if bool(hb.get("position")) else "No position"
        command_book = "Book ready" if bool(hb.get("book_ready")) else "Book waiting"
        command_spread_note = f"YES {format_cents(yes_spread)} / NO {format_cents(no_spread)}"
        command_trade_note = f"{entries_total} entries / {wins}W {losses}L {flats}F"
        if not curve.empty:
            displayed_curve = add_drawdown_to_equity_curve(filter_equity_curve(curve, st.session_state[range_key]))
            ending_equity = float(displayed_curve["equity"].iloc[-1]) if len(displayed_curve) else net_pnl_display
            starting_equity = float(displayed_curve["equity"].iloc[0]) if len(displayed_curve) else 0.0
            range_pnl_change = ending_equity - starting_equity
            max_drawdown = float(displayed_curve["drawdown"].min()) if len(displayed_curve) else 0.0

        render_dark_reference_dashboard(
            active_dataset_label_live=active_dataset_label_live,
            active_dataset_tag=str(active_dataset["tag"]),
            refresh_mode_label=refresh_mode_label,
            lock_status=lock_status,
            accounting_status=accounting_status,
            current_market_label=current_market_label,
            command_sync_label=command_sync_label,
            command_book=command_book,
            command_spread_note=command_spread_note,
            command_trade_note=command_trade_note,
            command_spark=command_spark,
            net_pnl_display=net_pnl_display,
            net_pnl_pct=net_pnl_pct,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            wins=wins,
            losses=losses,
            flats=flats,
            entries_total=entries_total,
            open_positions=open_positions,
            latest_trade_label=latest_trade_label,
            latest_trade_note=latest_trade_note,
            latest_trade_class=latest_trade_class,
            state_status=str(state["status"]),
            heartbeat_age_text=heartbeat_age_text,
            displayed_curve=displayed_curve,
            completed_pnl=completed_pnl,
            trades=trades,
            watch_close_label=watch_close_label,
            yes_bid=yes_bid,
            yes_ask=yes_ask,
            no_bid=no_bid,
            no_ask=no_ask,
            yes_spread=yes_spread,
            market_bias=market_bias,
            hb=hb,
            feed_age_text=feed_age_text,
            reaction_text=reaction_text,
            score_age_text=score_age_text,
            telemetry_text=telemetry_text,
            equity_range_label=str(st.session_state.get(range_key, st.session_state.get("equity_range", "ALL"))),
            seed_filter_label=str(st.session_state.get(seed_filter_key, st.session_state.get("seed_filter", "ALL"))),
        )

        with st.expander("Diagnostics", expanded=False):
            st.caption(f"Stats tag: {active_dataset['tag']}")
            st.caption(f"Log source: {active_dataset['log_source_tag']}")
            st.caption(f"Score mode: {active_dataset.get('score_mode')}")
            st.caption(f"Summary: {Path(active_dataset['summary_path']).relative_to(ROOT)}")
            st.caption(f"Trades: {Path(active_dataset['trades_path']).relative_to(ROOT)}")
            st.caption(f"Reconciliation: {accounting_status.get('reconciliation_json') or 'not available'}")
            events = list(reversed(state["events"][-14:]))
            if events:
                tape = []
                for evt in events:
                    cls = "event-good" if evt["kind"] == "entry" else "event-bad" if evt["kind"] in {"exit", "error"} else "event-warn" if evt["kind"] == "warning" else ""
                    tape.append(f"<div class='{cls}'><strong>{format_ma_time(evt['ts'])}</strong> | {html.escape(evt['msg'])}</div>")
                st.markdown(f"<div class='living-diagnostics-panel'>{''.join(tape)}</div>", unsafe_allow_html=True)
            if state["warnings"]:
                warn_html = "<div class='living-diagnostics-panel'>" + "".join(
                    f"<div class='event-warn'><strong>{html.escape(w['level'])}</strong> | {format_ma_time(w['ts'])}<br>{html.escape(w['msg'])}</div><hr style='border-color:rgba(31,44,67,0.10)'>"
                    for w in state["warnings"][-10:]
                ) + "</div>"
                st.markdown(warn_html, unsafe_allow_html=True)
            else:
                st.success("No recent warnings or errors.")
            escaped_tail = [html.escape(x) for x in state["log_tail"][-70:]]
            st.markdown(f"<div class='log-box'>{'<br>'.join(escaped_tail)}</div>", unsafe_allow_html=True)

    elif active_view == "Visualizer":
        render_visualizer_tab(trades, active_dataset["tag"], price_all, str(active_dataset["log_path"]))

    elif active_view == "Research Lab":
        research = load_research_lab_snapshot(str(active_dataset["research_root"]))
        metadata = research.get("metadata", {}) if isinstance(research, dict) else {}
        pipeline_status = research.get("pipeline_status", {}) if isinstance(research, dict) else {}
        replay_status = research.get("replay_status", {}) if isinstance(research, dict) else {}
        ingestion_status = research.get("ingestion_status", {}) if isinstance(research, dict) else {}
        replay_summary_df = load_latest_replay_summary(str(active_dataset["research_root"]))
        direct_replay_summary_df = load_latest_direct_replay_summary(str(active_dataset["research_root"]))
        direct_replay_trades_df = load_latest_direct_replay_trades(str(active_dataset["research_root"]))
        optimizer_summary_df = load_latest_optimizer_summary(str(active_dataset["research_root"]))
        optimizer_trades_df = load_latest_optimizer_trades(str(active_dataset["research_root"]))
        st.markdown("## Research Lab")
        st.caption("Recorder-backed analysis over normalized event data, 1-second market features, and labeled trades. This is the first useful step before full replay/backtest infrastructure.")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Raw event files", f"{int(research.get('raw_file_count', 0))}", delta=format_ma_time(research.get('latest_raw')) if research.get('latest_raw') else "No files yet")
        c2.metric("Checkpoint files", f"{int(research.get('checkpoint_file_count', 0))}", delta=format_ma_time(research.get('latest_checkpoint')) if research.get('latest_checkpoint') else "No files yet")
        c3.metric("Schema", str(metadata.get('schema_version') or 'uninitialized'), delta=str(metadata.get('dataset_tag') or active_dataset['tag']))
        c4.metric("Recorder root", "ready" if research.get('root_exists') else "missing", delta=str(active_dataset['research_root'].relative_to(ROOT)))

        truffle_shadow_path = Path(active_dataset["log_dir"]) / "truffle_post_entry_shadow.ndjson"
        truffle_lease_path = Path(active_dataset["log_dir"]) / "lease_events.ndjson"
        if truffle_shadow_path.exists() or truffle_lease_path.exists():
            render_truffle_shadow_panel(str(active_dataset["log_dir"]))

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Normalized rows", f"{int(pipeline_status.get('normalized_rows', 0))}", delta=f"{int(pipeline_status.get('normalized_file_count', 0))} parquet")
        p2.metric("Feature rows", f"{int(pipeline_status.get('feature_rows', 0))}", delta=f"{int(pipeline_status.get('feature_file_count', 0))} parquet")
        p3.metric("Trade labels", f"{int(pipeline_status.get('trade_label_rows', 0))}", delta=f"{int(pipeline_status.get('trade_label_file_count', 0))} parquet")
        p4.metric("Last pipeline build", format_ma_time(pipeline_status.get('built_at')) if pipeline_status.get('built_at') else "Not built", delta="research_pipeline.py")
        latest_raw_dt = research.get("latest_raw")
        latest_feature_dt = parse_ts(str(pipeline_status.get("latest_feature_ts") or "")) if pipeline_status else None
        ingestion_lag_seconds = (latest_raw_dt - latest_feature_dt).total_seconds() if latest_raw_dt and latest_feature_dt else None
        ingest1, ingest2, ingest3 = st.columns(3)
        ingest1.metric("Ingestor", str(ingestion_status.get("status") or "missing"), delta=str(ingestion_status.get("mode") or "no service"))
        ingest2.metric("Last ingest build", format_ma_time(ingestion_status.get("last_build_at")) if ingestion_status.get("last_build_at") else "Never", delta=f"{int(ingestion_status.get("build_count", 0) or 0)} builds")
        ingest3.metric("Raw to feature lag", f"{ingestion_lag_seconds/60.0:.1f} min" if ingestion_lag_seconds is not None else "NA", delta=format_ma_time(pipeline_status.get("latest_feature_ts")) if pipeline_status.get("latest_feature_ts") else "no features")

        labels_df = load_research_labels_sample(str(active_dataset["research_root"]))
        if not labels_df.empty:
            for col in ["net_pnl_dollars", "submit_latency_ms", "feed_age_ms_at_entry", "hold_duration_s"]:
                if col in labels_df.columns:
                    labels_df[col] = pd.to_numeric(labels_df[col], errors="coerce")
            closed_labels = labels_df[labels_df.get("net_pnl_dollars").notna()].copy() if "net_pnl_dollars" in labels_df.columns else pd.DataFrame()
        else:
            closed_labels = pd.DataFrame()

        insight_cols = st.columns(4)
        insight_cols[0].metric("Avg submit latency", f"{closed_labels['submit_latency_ms'].dropna().mean():.1f} ms" if not closed_labels.empty and closed_labels['submit_latency_ms'].dropna().size else "NA", delta="labeled trades")
        insight_cols[1].metric("Avg feed age", f"{closed_labels['feed_age_ms_at_entry'].dropna().mean():.1f} ms" if not closed_labels.empty and closed_labels['feed_age_ms_at_entry'].dropna().size else "NA", delta="at entry")
        insight_cols[2].metric("Avg win", format_money(closed_labels.loc[closed_labels['net_pnl_dollars'] > 0, 'net_pnl_dollars'].mean()) if not closed_labels.empty and (closed_labels['net_pnl_dollars'] > 0).any() else "NA", delta="net pnl")
        insight_cols[3].metric("Avg loss", format_money(closed_labels.loc[closed_labels['net_pnl_dollars'] < 0, 'net_pnl_dollars'].mean()) if not closed_labels.empty and (closed_labels['net_pnl_dollars'] < 0).any() else "NA", delta="net pnl")

        research_subview = st.radio("Research view", ["Overview", "Latency", "Event flow", "Feature tape", "Replay"], horizontal=True, key=f"research_subview_{active_dataset['tag']}")

        if research_subview == "Event flow":
            normalized_df = load_research_recent_normalized(str(active_dataset["research_root"]), max_files=4)
            st.markdown("### Event flow")
            if normalized_df.empty:
                st.info("No normalized event data available yet.")
            else:
                st.plotly_chart(build_research_event_flow_figure(normalized_df), width="stretch")

        elif research_subview == "Latency":
            st.markdown("### Latency and outcome")
            if closed_labels.empty:
                st.info("No labeled trades with latency fields are available yet.")
            else:
                st.plotly_chart(build_research_latency_figure(closed_labels.tail(120)), width="stretch")
                summary_cols = [c for c in ["market", "side", "entry_ts", "net_pnl_dollars", "hold_duration_s", "feed_age_ms_at_entry", "submit_latency_ms", "auth_prep_ms", "http_roundtrip_ms", "json_parse_ms"] if c in closed_labels.columns]
                trade_table = closed_labels[summary_cols].sort_values("entry_ts", ascending=False).head(20).copy()
                if "entry_ts" in trade_table.columns:
                    trade_table["entry_ts"] = pd.to_datetime(trade_table["entry_ts"], errors="coerce").dt.strftime("%Y-%m-%d %I:%M:%S %p")
                st.dataframe(trade_table, use_container_width=True, hide_index=True)

        elif research_subview == "Feature tape":
            st.markdown("### Market feature tape")
            candidate_markets = []
            if not direct_replay_trades_df.empty and "market" in direct_replay_trades_df.columns:
                candidate_markets = sorted(direct_replay_trades_df["market"].dropna().astype(str).unique().tolist())
            elif latest_watch and latest_watch.get('market'):
                candidate_markets = [str(latest_watch.get('market')).strip().upper()]
            selected_market = ""
            if candidate_markets:
                default_market = candidate_markets[-1]
                selected_market = st.selectbox("Feature market", candidate_markets, index=candidate_markets.index(default_market) if default_market in candidate_markets else 0, key=f"research-market-{active_dataset['tag']}")
            features_df = load_research_market_feature_slice(str(active_dataset["research_root"]), selected_market) if selected_market else pd.DataFrame()
            if features_df.empty:
                st.info("Feature tape is not available yet for that market.")
            else:
                st.plotly_chart(build_research_market_tape_figure(features_df, selected_market), width="stretch")

        elif research_subview == "Replay":
            pass

        else:
            st.markdown("### Overview")
            st.caption("Use the subview selector above to load the heavier research charts only when you need them.")

        st.markdown("### Replay scenarios")
        if replay_summary_df.empty:
            st.info("No replay results yet. Run research_replay.py to generate scenario comparisons.")
        else:
            top_row = replay_summary_df.iloc[0]
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Replay run", str(replay_status.get('run_id') or 'latest'), delta=format_ma_time(replay_status.get('built_at')) if replay_status.get('built_at') else 'replay status')
            r2.metric("Best scenario", str(replay_status.get('best_scenario') or top_row.get('scenario') or 'NA'), delta=format_money(float(replay_status.get('best_scenario_net_pnl_dollars') or top_row.get('kept_net_pnl_dollars') or 0.0)))
            r3.metric("Scenario count", f"{int(replay_status.get('scenario_rows', len(replay_summary_df)))}", delta=f"{int(replay_status.get('trade_rows', len(labels_df)))} trades")
            baseline_row = replay_summary_df[replay_summary_df['scenario'] == 'baseline'] if 'scenario' in replay_summary_df.columns else pd.DataFrame()
            baseline_net = float(baseline_row.iloc[0]['kept_net_pnl_dollars']) if not baseline_row.empty else np.nan
            best_net = float(top_row.get('kept_net_pnl_dollars') or 0.0)
            r4.metric("Best vs baseline", format_money(best_net - baseline_net) if pd.notna(baseline_net) else 'NA', delta='counterfactual')
            replay_cols = [c for c in ['scenario', 'trades_kept', 'trades_blocked', 'kept_net_pnl_dollars', 'baseline_net_pnl_dollars', 'kept_win_rate', 'avg_feed_age_ms', 'avg_submit_latency_ms', 'avg_same_side_range_30s'] if c in replay_summary_df.columns]
            st.dataframe(replay_summary_df[replay_cols], use_container_width=True, hide_index=True)

        st.markdown("### Parameter sweep optimizer")
        if optimizer_summary_df.empty:
            st.info("No raw-recorder optimizer results yet. Run research_replay.py to build the buy/stop leaderboard.")
        else:
            top_opt = optimizer_summary_df.iloc[0]
            o1, o2, o3, o4 = st.columns(4)
            o1.metric("Optimizer scenarios", f"{int(replay_status.get('optimizer_scenario_rows', len(optimizer_summary_df)))}", delta=f"{int(replay_status.get('optimizer_trade_rows', len(optimizer_trades_df)))} simulated trades")
            o2.metric("Best optimizer rule", str(replay_status.get('best_optimizer_scenario') or top_opt.get('scenario') or 'NA'), delta=format_money(float(replay_status.get('best_optimizer_net_pnl_dollars') or top_opt.get('net_pnl_dollars') or 0.0)))
            o3.metric("Best win rate", format_pct(float(pd.to_numeric(optimizer_summary_df.get('win_rate'), errors='coerce').max())) if 'win_rate' in optimizer_summary_df.columns else 'NA', delta='raw recorder sweep')
            o4.metric("Lowest false-stop count", f"{int(pd.to_numeric(optimizer_summary_df.get('false_stop_like_count'), errors='coerce').min())}" if 'false_stop_like_count' in optimizer_summary_df.columns else 'NA', delta='stopped winners by settlement')
            opt_cols = [c for c in ['scenario', 'entry_limit_cents', 'stop_cents', 'panic_cents', 'trades', 'wins', 'losses', 'false_stop_like_count', 'false_stop_like_rate', 'net_pnl_dollars', 'avg_pnl_dollars', 'win_rate', 'worst_trade_dollars'] if c in optimizer_summary_df.columns]
            st.dataframe(optimizer_summary_df[opt_cols], use_container_width=True, hide_index=True)
            if not optimizer_trades_df.empty:
                opt_preview_cols = [c for c in ['scenario', 'market', 'side', 'entry_ts', 'exit_ts', 'entry_price_cents', 'exit_price_cents', 'exit_reason', 'market_result', 'stopped_but_resolved_entry_side', 'net_pnl_dollars'] if c in optimizer_trades_df.columns]
                opt_preview_df = optimizer_trades_df[opt_preview_cols].copy()
                for ts_col in ['entry_ts', 'exit_ts']:
                    if ts_col in opt_preview_df.columns:
                        opt_preview_df[ts_col] = pd.to_datetime(opt_preview_df[ts_col], errors='coerce').dt.strftime("%Y-%m-%d %I:%M:%S %p")
                st.dataframe(opt_preview_df.head(150), use_container_width=True, hide_index=True)

        st.markdown("### Direct quote replay")
        if direct_replay_summary_df.empty:
            st.info("No direct quote replay results yet. Run research_replay.py after feature data accumulates.")
        else:
            top_direct = direct_replay_summary_df.iloc[0]
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Direct scenarios", f"{int(replay_status.get('direct_scenario_rows', len(direct_replay_summary_df)))}", delta=f"{int(replay_status.get('direct_replay_rows', len(direct_replay_trades_df)))} simulated trades")
            d2.metric("Best direct scenario", str(replay_status.get('best_direct_scenario') or top_direct.get('scenario') or 'NA'), delta=format_money(float(replay_status.get('best_direct_net_pnl_dollars') or top_direct.get('net_pnl_dollars') or 0.0)))
            d3.metric("Stopped trades", f"{int(pd.to_numeric(direct_replay_summary_df.get('stopped_trades'), errors='coerce').fillna(0).sum())}", delta="quote-driven replay")
            d4.metric("Coverage", f"{int(len(direct_replay_trades_df))}", delta="feature-derived entries")
            direct_cols = [c for c in ['scenario', 'trades', 'wins', 'losses', 'stopped_trades', 'settled_trades', 'net_pnl_dollars', 'avg_pnl_dollars', 'win_rate'] if c in direct_replay_summary_df.columns]
            st.dataframe(direct_replay_summary_df[direct_cols], use_container_width=True, hide_index=True)
            if not direct_replay_trades_df.empty:
                preview_cols = [c for c in ['scenario', 'market', 'side', 'entry_ts', 'exit_ts', 'entry_price_cents', 'exit_price_cents', 'exit_reason', 'market_result', 'net_pnl_dollars'] if c in direct_replay_trades_df.columns]
                preview_df = direct_replay_trades_df[preview_cols].copy()
                for ts_col in ['entry_ts', 'exit_ts']:
                    if ts_col in preview_df.columns:
                        preview_df[ts_col] = pd.to_datetime(preview_df[ts_col], errors='coerce').dt.strftime("%Y-%m-%d %I:%M:%S %p")
                st.dataframe(preview_df, use_container_width=True, hide_index=True)
            st.caption("Direct quote replay is still early-stage: it is built from 1-second feature bars and the currently recorded feature window, so coverage will grow as recorder history accumulates.")

        lower_left, lower_right = st.columns([1.2, 1.0], gap="large")
        with lower_left:
            st.markdown("### Event partitions")
            counts = research.get("event_type_counts", {})
            if counts:
                counts_df = pd.DataFrame([
                    {"Event type": key, "Files": value}
                    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
                ])
                st.dataframe(counts_df, use_container_width=True, hide_index=True)
            else:
                st.info("No research event partitions have been recorded yet for this dataset.")
        with lower_right:
            st.markdown("### Recorder scope")
            st.markdown("""
- Raw websocket and control events are captured append-only under `research_data/<dataset>/raw_events`.
- Sparse full-depth checkpoints are captured under `research_data/<dataset>/book_checkpoints`.
- Phase 2 builds normalized Parquet events, 1-second feature tables, and trade labels.
- Phase 3 now writes replay scenario summaries under `research_data/<dataset>/replay_runs`.
            """)

        st.markdown("### Recent recorder files")
        recent_files = research.get("recent_files", [])
        if recent_files:
            files_df = pd.DataFrame(recent_files)
            files_df["updated"] = files_df["updated"].dt.strftime("%Y-%m-%d %I:%M:%S %p")
            st.dataframe(files_df.rename(columns={"kind": "Kind", "path": "Path", "size_kb": "KB", "updated": "Updated"}), use_container_width=True, hide_index=True)
        else:
            st.info("Recorder folders exist but no files have been written yet.")

    elif active_view == "BTC today map":
        render_btc_day_map_tab(trades, market_results)

    elif active_view == "Loss diagnostics":
        render_loss_diagnostics_tab(price_all, trades, active_dataset["tag"])

    else:
        render_strategy_optimizer_tab(price_all, all_lines, summary, watch, hb, market_results, trades, active_dataset["tag"])


live_dashboard()









