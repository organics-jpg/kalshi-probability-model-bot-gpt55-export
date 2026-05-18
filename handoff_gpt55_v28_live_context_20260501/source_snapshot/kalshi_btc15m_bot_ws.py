from __future__ import annotations

import asyncio
import base64
import collections
import contextlib
import ctypes
import json
import logging
import math
import os
import re
import signal
import sys
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
import websockets
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv
import numpy as np
from btc_mushroom_forecaster_v22 import MushroomConfig, MushroomForecaster
from btc_mushroom_forecaster_v28_fast import (
    FastMushroomConfig as MushroomV28Config,
    FastMushroomFVEngine as MushroomV28Engine,
)
from btc_mushroom_live_fv_worker_v28 import LiveFVWorker as MushroomV28LiveFVWorker
from truffle_regime_lease import (
    ALLOW_90_78_NEXT_MARKET,
    BLOCK_NEXT_MARKET,
    DEFAULT_TRUFFLE_REASONING_TOOL_PROMPT,
    VALID_LEASE_ISSUERS,
    VALID_LEASE_MODES,
    LeaseCacheStore,
    LeaseDecision,
    LeaseEventWriter,
    MarketOutcomeStore,
    build_last_market_sequence,
    build_recent_market_summary,
    infer_session_label,
    issue_stub_lease,
    issue_truffle_http_lease,
    lease_is_stale,
    load_prompt_text,
)
from truffle_post_entry_shadow import (
    DEFAULT_POST_ENTRY_SHADOW_MAX_TOKENS,
    DEFAULT_TRUFFLE_POST_ENTRY_SHADOW_PROMPT,
    PostEntryShadowDecision,
    build_btc_spot_context,
    build_exit_supervisor_payload,
    build_post_entry_context,
    build_pre_entry_context,
    classify_exit_supervisor_slice_tags,
    current_side_bid_at,
    issue_truffle_post_entry_shadow,
)

SCRIPT_DIR = Path(__file__).resolve().parent
CENTS = Decimal("100")
ALLOWED_SERIES_TICKER = "KXBTC15M"
ALLOWED_TICKER_PREFIX = "KXBTC15M-"
PROD_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
DEMO_BASE_URL = "https://demo-api.kalshi.co/trade-api/v2"
PROD_WS_URL = "wss://api.elections.kalshi.com/trade-api/ws/v2"
DEMO_WS_URL = "wss://demo-api.kalshi.co/trade-api/ws/v2"
MUSHROOM_VERSION = "v0.22"
MUSHROOM_V21_DECISION_VERSION = "v0.21_static_boundary_field"
MUSHROOM_V28_VERSION = "v0.28_fast_fv"
COINBASE_BTC_TICKER_WS_URL = "wss://ws-feed.exchange.coinbase.com"
BINANCE_BTC_TRADE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"
BINANCE_US_BTC_TRADE_WS_URL = "wss://stream.binance.us:9443/ws/btcusdt@trade"
BINANCE_US_BTC_BOOK_TICKER_WS_URL = "wss://stream.binance.us:9443/ws/btcusdt@bookTicker"
BTC_STRIKE_MIN_DOLLARS = 20_000.0
BTC_STRIKE_MAX_DOLLARS = 250_000.0


def mushroom_v21_config() -> MushroomConfig:
    """Conservative v21-style field: range-aware anchor/static field, no v22 transport."""
    return MushroomConfig(
        transport_recent_weight=0.0,
        transport_long_weight=0.0,
        transport_temperature=1.0,
    )


def _coerce_btc_strike(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str) and value.strip() in {"", "None"}:
        return None
    try:
        number = float(str(value).replace("$", "").replace(",", "").strip())
    except (TypeError, ValueError):
        return None
    if BTC_STRIKE_MIN_DOLLARS <= number <= BTC_STRIKE_MAX_DOLLARS:
        return number
    return None


def parse_btc_strike_from_market(market: dict[str, Any] | None) -> float | None:
    if not isinstance(market, dict):
        return None
    preferred_keys = (
        "strike",
        "custom_strike",
        "floor_strike",
        "cap_strike",
        "target_strike",
        "target_price",
        "price_level",
    )
    for key in preferred_keys:
        strike = _coerce_btc_strike(market.get(key))
        if strike is not None:
            return strike
    for key, value in market.items():
        key_l = str(key).lower()
        if "strike" not in key_l and "target" not in key_l:
            continue
        strike = _coerce_btc_strike(value)
        if strike is not None:
            return strike
    text_keys = (
        "title",
        "subtitle",
        "yes_sub_title",
        "no_sub_title",
        "rules_primary",
        "rules_secondary",
    )
    for key in text_keys:
        text = str(market.get(key) or "")
        for match in re.findall(r"\$?\b\d{2,3}(?:,\d{3})+(?:\.\d+)?\b|\$?\b\d{5,6}(?:\.\d+)?\b", text):
            strike = _coerce_btc_strike(match)
            if strike is not None:
                return strike
    return None


def sanitize_strategy_tag(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "_", value.strip())
    return cleaned.strip("._-") or "default"


def build_strategy_tag(entry_cents: int, stop_cents: int) -> str:
    return f"entry_{int(entry_cents)}_stop_{int(stop_cents)}"


def resolve_strategy_paths(storage_tag: str) -> tuple[Path, Path]:
    tag = sanitize_strategy_tag(storage_tag)
    return (
        SCRIPT_DIR / "state" / tag / "bot_state.json",
        SCRIPT_DIR / "logs" / tag / "bot.log",
    )


def resolve_execution_telemetry_path(storage_tag: str) -> Path:
    tag = sanitize_strategy_tag(storage_tag)
    return SCRIPT_DIR / "logs" / tag / "execution_events.ndjson"


def resolve_truffle_regime_lease_cache_path(storage_tag: str) -> Path:
    tag = sanitize_strategy_tag(storage_tag)
    return SCRIPT_DIR / "state" / tag / "truffle_regime_lease.json"


def resolve_truffle_regime_lease_events_path(storage_tag: str) -> Path:
    tag = sanitize_strategy_tag(storage_tag)
    return SCRIPT_DIR / "logs" / tag / "lease_events.ndjson"


def resolve_recent_market_outcomes_path(storage_tag: str) -> Path:
    tag = sanitize_strategy_tag(storage_tag)
    return SCRIPT_DIR / "state" / tag / "recent_market_outcomes.json"


def resolve_truffle_post_entry_shadow_events_path(storage_tag: str) -> Path:
    tag = sanitize_strategy_tag(storage_tag)
    return SCRIPT_DIR / "logs" / tag / "truffle_post_entry_shadow.ndjson"


def recent_price_history_maxlen(config: "Config") -> int:
    baseline = max(int(config.pre_entry_stddev_lookback_points), 8) * 3
    sample_interval_seconds = 0.2
    if config.liquidity_dwell_entry_enabled:
        dwell_padding_seconds = max(30.0, float(config.liquidity_dwell_delay_seconds) * 0.25)
        baseline = max(
            baseline,
            int((float(config.liquidity_dwell_delay_seconds) + dwell_padding_seconds) / sample_interval_seconds) + 64,
        )
    if not config.truffle_post_entry_shadow_enabled:
        return baseline
    market_seconds = 15 * 60
    padding_seconds = max(120.0, float(config.truffle_post_entry_shadow_delay_seconds) + 60.0)
    required = int((market_seconds + padding_seconds) / sample_interval_seconds) + 64
    return max(baseline, required)


class GracefulExit(SystemExit):
    pass


@dataclass
class Config:
    api_key_id: str
    private_key_path: Path
    base_url: str = PROD_BASE_URL
    ws_url: str = PROD_WS_URL
    series_ticker: str = ALLOWED_SERIES_TICKER
    target_entry_odds_cents: int = 90
    exit_drop_odds_cents: int = 60
    exit_stop_loss_enabled: bool = True
    position_size: int = 2
    multi_entry_same_market_enabled: bool = False
    multi_entry_max_position_contracts: int = 2
    multi_entry_min_seconds_between_entries: float = 120.0
    post_fill_exit_delay_seconds: float = 30.0
    rest_poll_seconds: float = 1.0
    decision_loop_seconds: float = 0.05
    active_market_refresh_seconds: float = 1.0
    active_market_retry_seconds: float = 1.0
    websocket_reconnect_seconds: float = 1.0
    heartbeat_log_seconds: float = 15.0
    orderbook_depth: int = 20
    http_timeout_seconds: float = 5.0
    dry_run: bool = True
    log_level: str = "INFO"
    strategy_tag: str = "default"
    run_id: str = ""
    state_path: Path = SCRIPT_DIR / "state" / "bot_state.json"
    log_path: Path = SCRIPT_DIR / "logs" / "bot.log"
    execution_telemetry_enabled: bool = True
    execution_telemetry_path: Path = SCRIPT_DIR / "logs" / "execution_events.ndjson"
    pre_entry_stddev_filter_enabled: bool = False
    pre_entry_stddev_threshold: float = 0.0
    pre_entry_stddev_lookback_points: int = 8
    liquidity_dwell_entry_enabled: bool = False
    liquidity_dwell_delay_seconds: float = 120.0
    liquidity_dwell_max_entry_ask: int = 90
    liquidity_dwell_max_opp_pressure: float = 0.5
    liquidity_dwell_max_spread: float = 10.0
    liquidity_dwell_min_bid_sum: float = 0.0
    liquidity_dwell_min_quality_seconds: float = 10.0
    liquidity_dwell_min_quality_share: float = 0.65
    live_entry_base_book_age_ms: float = 250.0
    live_entry_final_minute_book_age_ms: float = 150.0
    live_entry_final_seconds_book_age_ms: float = 80.0
    live_entry_skip_seconds_to_close: float = 8.0
    live_entry_extreme_odds_cents: int = 89
    live_entry_allow_ioc: bool = True
    live_entry_ioc_first: bool = True
    live_entry_default_tif: str = "immediate_or_cancel"
    live_entry_allow_fok_when_full_depth: bool = True
    live_entry_min_visible_depth_for_ioc: int = 1
    live_entry_book_diagnostics_levels: int = 4
    exit_book_diagnostics_levels: int = 4
    exit_mode_selection_enabled: bool = True
    exit_max_book_age_ms: float = 150.0
    exit_confirm_checks: int = 2
    exit_confirm_seconds: float = 15.0
    exit_panic_odds_cents: int = 74
    exit_single_order_depth_multiple: float = 1.25
    exit_adaptive_slice_enabled: bool = True
    exit_adaptive_slice_alpha: float = 0.35
    exit_adaptive_slice_min_contracts: int = 2
    exit_adaptive_slice_max_contracts: int = 10
    exit_slice_delay_ms: float = 0.0
    exit_max_retry_steps: int = 2
    exit_retry_tick_step_cents: int = 1
    exit_retry_backoff_ms: float = 150.0
    exit_rebuild_on_zero_fill: bool = True
    exit_reprice_on_partial_fill: bool = True
    exit_panic_max_cross_cents: int = 3
    live_entry_slice_enabled: bool = True
    live_entry_slice_pattern: tuple[int, ...] = (2, 3)
    live_entry_slice_delay_ms: float = 0.0
    live_entry_slice_stop_on_zero_fill: bool = True
    live_entry_partial_completion_enabled: bool = True
    live_entry_partial_completion_seconds: float = 15.0
    live_entry_partial_completion_min_price_cents: int = 85
    live_entry_partial_completion_max_price_cents: int = 90
    live_entry_partial_completion_retry_delay_ms: float = 150.0
    live_entry_dead_market_suppression_ms: float = 2000.0
    live_entry_material_book_change_ticks: int = 1
    live_entry_stale_suppression_ms: float = 100.0
    live_entry_stale_depth_change_contracts: int = 5
    live_entry_blocked_suppression_ms: float = 250.0
    live_entry_single_order_depth_multiple: float = 3.0
    live_entry_adaptive_slice_enabled: bool = True
    live_entry_adaptive_slice_alpha: float = 0.2
    live_entry_adaptive_slice_min_contracts: int = 2
    live_entry_adaptive_slice_max_contracts: int = 5
    live_entry_fast_fill_gate_enabled: bool = True
    live_entry_fast_fill_min_seconds_to_close: float = 60.0
    live_entry_fast_fill_min_depth_contracts: int = 2
    live_entry_fast_fill_min_window_ms: float = 150.0
    live_entry_fast_fill_slippage_budget_cents: int = 1
    live_entry_fast_fill_min_net_edge_cents: int = 4
    live_account_state_poll_seconds: float = 1.0
    live_account_state_max_age_ms: float = 1500.0
    live_balance_min_buffer_cents: int = 300
    live_balance_fee_buffer_cents: int = 25
    btc_vol_regime_gate_enabled: bool = False
    btc_vol_regime_max_range_dollars: float = 275.0
    btc_vol_regime_poll_seconds: float = 5.0
    btc_vol_regime_lookback_minutes: int = 15
    btc_vol_regime_interval: str = "5m"
    btc_vol_regime_max_age_ms: float = 20000.0
    btc_vol_regime_fail_open: bool = True
    mushroom_shadow_enabled: bool = True
    mushroom_btc_history_minutes: int = 1800
    mushroom_min_p_side: float = 0.80
    mushroom_strict_p_side: float = 0.85
    mushroom_min_edge_cents_15m: float = 2.0
    mushroom_model_buffer_cents: float = 0.0
    mushroom_v21_decision_engine_enabled: bool = False
    mushroom_v21_min_p_side: float = 0.80
    mushroom_v21_min_edge_cents_15m: float = 2.0
    mushroom_v21_max_ask_cents: int = 90
    mushroom_v21_min_seconds_to_close: float = 240.0
    mushroom_v21_max_seconds_to_close: float = 480.0
    mushroom_v21_model_buffer_cents: float = 0.0
    mushroom_v21_slippage_cents: float = 1.0
    mushroom_v28_shadow_enabled: bool = True
    mushroom_v28_decision_engine_enabled: bool = False
    mushroom_v28_live_exit_enabled: bool = False
    mushroom_v28_min_p_side: float = 0.85
    mushroom_v28_min_edge_cents_15m: float = 2.0
    mushroom_v28_model_buffer_cents: float = 1.0
    mushroom_v28_slippage_cents: float = 1.0
    mushroom_v28_max_ask_cents: int = 90
    mushroom_v28_min_seconds_to_close: float = 70.0
    mushroom_v28_max_seconds_to_close: float = 900.0
    mushroom_v28_max_market_risk_cents: int = 200
    mushroom_v28_btc_max_age_ms: float = 1500.0
    mushroom_v28_btc_ws_enabled: bool = True
    mushroom_v28_btc_ws_url: str = COINBASE_BTC_TICKER_WS_URL
    mushroom_v28_btc_ws_fallback_urls: tuple[str, ...] = (BINANCE_US_BTC_BOOK_TICKER_WS_URL, BINANCE_US_BTC_TRADE_WS_URL)
    mushroom_v28_exit_hysteresis_cents: float = 0.25
    mushroom_v28_exit_hold_buffer_cents: float = 1.0
    mushroom_v28_exit_reduce_p_hold_floor: float = 0.80
    mushroom_v28_exit_full_p_hold_floor: float = 0.72
    mushroom_v28_exit_fair_drawdown_cents: float = 8.0
    mushroom_v28_exit_full_drawdown_cents: float = 15.0
    mushroom_v28_exit_reduce_fraction: float = 0.5
    live_approved_strategy_tag: str = ""
    live_lock_path: Path = SCRIPT_DIR / "state" / "live_trading.lock"
    truffle_regime_lease_mode: str = "disabled"
    truffle_regime_lease_issuer: str = "stub"
    truffle_regime_lease_timeout_ms: int = 2500
    truffle_regime_lease_cache_path: Path = SCRIPT_DIR / "state" / "truffle_regime_lease.json"
    truffle_regime_lease_events_path: Path = SCRIPT_DIR / "logs" / "lease_events.ndjson"
    truffle_regime_lease_outcomes_path: Path = SCRIPT_DIR / "state" / "recent_market_outcomes.json"
    truffle_regime_lease_fail_closed: bool = True
    truffle_regime_lease_prompt_path: Path = SCRIPT_DIR / "truffle_regime_lease_prompt.txt"
    truffle_regime_lease_tool_prompt_path: Path = SCRIPT_DIR / "truffle_regime_lease_tool_prompt.txt"
    truffle_regime_lease_max_staleness_seconds: float = 1800.0
    truffle_regime_lease_endpoint: str = ""
    truffle_regime_lease_model: str = ""
    truffle_regime_lease_api_key: str = ""
    truffle_regime_lease_max_tokens: int = 0
    truffle_regime_lease_reasoning_enabled: str = "auto"
    truffle_post_entry_shadow_enabled: bool = False
    truffle_post_entry_shadow_delay_seconds: float = 90.0
    truffle_post_entry_shadow_timeout_ms: int = 20000
    truffle_post_entry_shadow_events_path: Path = SCRIPT_DIR / "logs" / "truffle_post_entry_shadow.ndjson"
    truffle_post_entry_shadow_prompt_path: Path = SCRIPT_DIR / "truffle_post_entry_shadow_prompt.txt"
    truffle_post_entry_shadow_endpoint: str = ""
    truffle_post_entry_shadow_model: str = ""
    truffle_post_entry_shadow_api_key: str = ""
    truffle_post_entry_shadow_max_tokens: int = DEFAULT_POST_ENTRY_SHADOW_MAX_TOKENS
    truffle_post_entry_shadow_include_btc_spot: bool = False
    truffle_post_entry_shadow_decision_schema: str = "reversal_risk"
    truffle_post_entry_shadow_output_mode: str = "json"
    truffle_post_entry_shadow_reasoning_enabled: str = "false"
    truffle_post_entry_shadow_suspicious_only: bool = False
    truffle_post_entry_shadow_live_exit_enabled: bool = False

    @property
    def private_key_exists(self) -> bool:
        return self.private_key_path.exists()


@dataclass
class PendingOrder:
    purpose: str
    order_id: str
    client_order_id: str
    market_ticker: str
    side: str
    action: str
    count: int
    limit_price_cents: int
    submitted_at: str
    trigger_price_cents: int
    trigger_seen_at: str
    time_in_force: str = "fill_or_kill"


@dataclass
class PositionState:
    market_ticker: str
    side: str
    count: int
    filled_at: str
    entry_order_id: str
    entry_limit_price_cents: int
    entry_fill_price_cents: int | None = None
    entry_fee_cents: int = 0
    entry_trigger_price_cents: int | None = None


@dataclass
class ExitSignal:
    market_ticker: str
    side: str
    trigger_price_cents: int
    stop_price_cents: int
    position_count: int
    top_of_book_limit_cents: int | None
    executable_limit_cents: int | None
    eligible_depth: Decimal
    book_age_ms: float | None
    seconds_to_close: float | None
    book_summary: str
    bid_levels: list[dict[str, Any]] = field(default_factory=list)
    same_side_buy_levels: list[dict[str, Any]] = field(default_factory=list)
    top_bid_size: str | None = None
    executable_depth_at_limit: str | None = None
    executable_depth_one_cent_lower: str | None = None
    executable_depth_two_cents_lower: str | None = None
    yes_bid_cents: int | None = None
    yes_ask_cents: int | None = None
    no_bid_cents: int | None = None
    no_ask_cents: int | None = None
    yes_bid_size: str | None = None
    yes_ask_size: str | None = None
    no_bid_size: str | None = None
    no_ask_size: str | None = None
    detected_at_monotonic: float | None = None
    stop_tier: str = "soft"
    confirmation_count: int = 0
    confirmation_elapsed_seconds: float = 0.0
    signal_signature: str = ""
    mushroom_shadow: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExitPlan:
    market_ticker: str
    side: str
    trigger_price_cents: int
    stop_price_cents: int
    total_count: int
    top_of_book_limit_cents: int | None
    limit_price_cents: int
    eligible_depth: Decimal
    depth_required: Decimal
    book_age_ms: float
    seconds_to_close: float | None
    time_in_force: str
    reason: str
    book_summary: str
    bid_levels: list[dict[str, Any]] = field(default_factory=list)
    same_side_buy_levels: list[dict[str, Any]] = field(default_factory=list)
    top_bid_size: str | None = None
    executable_depth_at_limit: str | None = None
    executable_depth_one_cent_lower: str | None = None
    executable_depth_two_cents_lower: str | None = None
    yes_bid_cents: int | None = None
    yes_ask_cents: int | None = None
    no_bid_cents: int | None = None
    no_ask_cents: int | None = None
    yes_bid_size: str | None = None
    yes_ask_size: str | None = None
    no_bid_size: str | None = None
    no_ask_size: str | None = None
    urgency_state: str = "controlled"
    recommended_mode: str = "single_shot_ioc"
    expected_fill_ratio_at_limit: float | None = None
    expected_fill_ratio_one_cent_lower: float | None = None
    expected_fill_ratio_two_cents_lower: float | None = None
    full_size_available_at_limit: bool = False
    max_retry_steps: int = 0
    slices: list[SlicePlan] = field(default_factory=list)
    signal_signature: str = ""
    account_age_ms: float | None = None
    mushroom_shadow: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExitCapacityEstimate:
    depth_at_limit: Decimal
    depth_one_cent_lower: Decimal
    depth_two_cents_lower: Decimal
    expected_fill_ratio_at_limit: float
    expected_fill_ratio_one_cent_lower: float
    expected_fill_ratio_two_cents_lower: float
    full_size_available_at_limit: bool
    book_is_collapsing: bool
    urgency_state: str
    recommended_mode: str
    recommended_first_slice: int
    recommended_slice_ladder: list[int] = field(default_factory=list)
    max_retry_steps: int = 0
    explanation: str = ""


@dataclass
class LiveFillPlan:
    mode: str
    time_in_force: str
    limit_price_cents: int
    target_count: int
    eligible_depth: Decimal
    depth_required: Decimal
    book_age_ms: float
    seconds_to_close: float | None
    reason: str


@dataclass
class EntrySignal:
    market_ticker: str
    side: str
    trigger_price_cents: int
    cap_price_cents: int
    top_of_book_limit_cents: int | None
    executable_limit_cents: int | None
    eligible_depth: Decimal
    book_age_ms: float | None
    seconds_to_close: float | None
    book_summary: str
    yes_ask_cents: int | None
    no_ask_cents: int | None
    signal_signature: str
    first_executable_at_monotonic: float | None = None
    executable_window_ms: float | None = None
    target_count: int | None = None
    model_max_buy_price_cents: int | None = None
    mushroom_shadow: dict[str, Any] = field(default_factory=dict)


@dataclass
class FilterDecision:
    allowed: bool
    reason: str
    pre_std: float | None = None
    pre_std_threshold: float | None = None
    std_obs: int = 0


@dataclass
class SlicePlan:
    slice_index: int
    count: int
    limit_price_cents: int
    time_in_force: str
    reason: str


@dataclass
class ExecutionPlan:
    market_ticker: str
    side: str
    trigger_price_cents: int
    cap_price_cents: int
    total_count: int
    eligible_depth: Decimal
    depth_required: Decimal
    book_age_ms: float
    seconds_to_close: float | None
    time_in_force: str
    limit_price_cents: int
    mode: str
    reason: str
    top_of_book_limit_cents: int | None
    book_summary: str
    signal_signature: str
    account_age_ms: float | None
    executable_window_ms: float | None
    model_max_buy_price_cents: int | None = None
    mushroom_shadow: dict[str, Any] = field(default_factory=dict)
    slices: list[SlicePlan] = field(default_factory=list)


@dataclass
class SubmissionResult:
    purpose: str
    order_id: str
    client_order_id: str
    status: str
    fill_count: int
    remaining_count: int
    submit_latency_ms: float
    limit_price_cents: int
    time_in_force: str
    actual_fill_price_cents: int | None = None
    actual_fee_cents: int | None = None
    error_text: str = ""


@dataclass
class ExecutionTelemetryContext:
    market: str = ""
    purpose: str = ""
    side: str = ""
    trigger_price_cents: int | None = None
    cap_price_cents: int | None = None
    position_size: int | None = None
    slice_index: int | None = None
    slice_target_size: int | None = None
    book_age_ms: float | None = None
    feed_age_ms: float | None = None
    local_reaction_ms: float | None = None
    top_of_book_limit_cents: int | None = None
    eligible_depth: str | None = None
    depth_required: str | None = None
    book_summary: str = ""
    bid_levels: list[dict[str, Any]] = field(default_factory=list)
    same_side_buy_levels: list[dict[str, Any]] = field(default_factory=list)
    top_bid_size: str | None = None
    executable_depth_at_limit: str | None = None
    executable_depth_one_cent_lower: str | None = None
    executable_depth_two_cents_lower: str | None = None
    yes_bid_cents: int | None = None
    yes_ask_cents: int | None = None
    no_bid_cents: int | None = None
    no_ask_cents: int | None = None
    yes_bid_size: str | None = None
    yes_ask_size: str | None = None
    no_bid_size: str | None = None
    no_ask_size: str | None = None
    pre_std: float | None = None
    pre_std_threshold: float | None = None
    std_obs: int | None = None
    decision_reason: str = ""
    order_id: str = ""
    client_order_id: str = ""
    time_in_force: str = ""
    submit_latency_ms: float | None = None
    exchange_status: str = ""
    fill_count: int | None = None
    remaining_count: int | None = None
    actual_fill_price_cents: int | None = None
    actual_fee_cents: int | None = None
    result: str = ""
    executable_window_ms: float | None = None


@dataclass
class OrderBookTrustState:
    sequence_ok: bool = False
    last_seq_gap_ts: str | None = None
    last_resync_ts: str | None = None
    trust_state: str = "cold"


@dataclass
class MarketSideExecutionState:
    state: str = "idle"
    last_material_signature: str = ""
    cooldown_until_monotonic: float = 0.0
    last_reason: str = ""
    dead_since_monotonic: float | None = None
    last_dead_signature: str = ""
    dead_reason: str = ""
    last_transition_monotonic: float = 0.0


@dataclass
class ExecutableWindowState:
    active: bool = False
    since_monotonic: float | None = None
    max_visible_depth: Decimal = field(default_factory=lambda: Decimal("0"))
    last_limit_cents: int | None = None


@dataclass
class LiveAccountSnapshot:
    available_balance_cents: int | None = None
    resting_orders: list[dict[str, Any]] = field(default_factory=list)
    fetched_at_monotonic: float = 0.0


@dataclass
class EntryRejectionState:
    block_until_monotonic: float = 0.0
    prefer_ioc_until_monotonic: float = 0.0
    last_reason: str = ""


@dataclass
class EntrySkipState:
    block_until_monotonic: float = 0.0
    last_reason: str = ""
    last_signature: str = ""


@dataclass
class LiquidityDwellCandidate:
    market_ticker: str
    side: str
    first_seen_monotonic: float
    first_seen_wall: str
    initial_trigger_price_cents: int
    last_wait_log_monotonic: float = 0.0


@dataclass
class ExitConfirmationState:
    market_ticker: str = ""
    side: str = ""
    first_triggered_at: str = ""
    last_quote_time: str = ""
    trigger_count: int = 0
    last_trigger_price_cents: int | None = None


@dataclass
class RuntimeState:
    pending_order: PendingOrder | None = None
    position: PositionState | None = None
    exit_confirmation: ExitConfirmationState | None = None
    traded_markets: list[str] = field(default_factory=list)


@dataclass
class MarketSnapshot:
    market_ticker: str | None = None
    market_status: str | None = None
    yes_bid_cents: int | None = None
    yes_ask_cents: int | None = None
    no_bid_cents: int | None = None
    no_ask_cents: int | None = None
    yes_bid_size: Decimal | None = None
    yes_ask_size: Decimal | None = None
    no_bid_size: Decimal | None = None
    no_ask_size: Decimal | None = None
    close_time: str | None = None
    strike: float | None = None
    updated_time: str | None = None
    local_received_monotonic: float | None = None


class StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> RuntimeState:
        if not self.path.exists():
            return RuntimeState()
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        pending = raw.get("pending_order")
        position = raw.get("position")
        exit_confirmation = raw.get("exit_confirmation")
        return RuntimeState(
            pending_order=PendingOrder(**pending) if pending else None,
            position=PositionState(**position) if position else None,
            exit_confirmation=ExitConfirmationState(**exit_confirmation) if exit_confirmation else None,
            traded_markets=list(raw.get("traded_markets", [])),
        )

    def save(self, state: RuntimeState) -> None:
        payload = {
            "pending_order": asdict(state.pending_order) if state.pending_order else None,
            "position": asdict(state.position) if state.position else None,
            "exit_confirmation": asdict(state.exit_confirmation) if state.exit_confirmation else None,
            "traded_markets": state.traded_markets[-1000:],
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


class ExecutionTelemetryWriter:
    def __init__(self, path: Path, *, enabled: bool, run_id: str) -> None:
        self.path = path
        self.enabled = enabled
        self.run_id = run_id
        if self.enabled:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event_type: str, context: ExecutionTelemetryContext | None = None, **extra: Any) -> None:
        if not self.enabled:
            return
        ctx = context or ExecutionTelemetryContext()
        payload = {
            "run_id": self.run_id,
            "ts_wall": utc_now().isoformat(),
            "ts_mono": round(time.monotonic(), 6),
            "market": ctx.market,
            "side": ctx.side,
            "event_type": event_type,
            "trigger_price_cents": ctx.trigger_price_cents,
            "cap_price_cents": ctx.cap_price_cents,
            "position_size": ctx.position_size,
            "slice_index": ctx.slice_index,
            "slice_target_size": ctx.slice_target_size,
            "book_age_ms": ctx.book_age_ms,
            "feed_age_ms": ctx.feed_age_ms,
            "local_reaction_ms": ctx.local_reaction_ms,
            "top_of_book_limit_cents": ctx.top_of_book_limit_cents,
            "eligible_depth": ctx.eligible_depth,
            "depth_required": ctx.depth_required,
            "book_summary": ctx.book_summary,
            "bid_levels": ctx.bid_levels,
            "same_side_buy_levels": ctx.same_side_buy_levels,
            "top_bid_size": ctx.top_bid_size,
            "executable_depth_at_limit": ctx.executable_depth_at_limit,
            "executable_depth_one_cent_lower": ctx.executable_depth_one_cent_lower,
            "executable_depth_two_cents_lower": ctx.executable_depth_two_cents_lower,
            "yes_bid_cents": ctx.yes_bid_cents,
            "yes_ask_cents": ctx.yes_ask_cents,
            "no_bid_cents": ctx.no_bid_cents,
            "no_ask_cents": ctx.no_ask_cents,
            "yes_bid_size": ctx.yes_bid_size,
            "yes_ask_size": ctx.yes_ask_size,
            "no_bid_size": ctx.no_bid_size,
            "no_ask_size": ctx.no_ask_size,
            "pre_std": ctx.pre_std,
            "pre_std_threshold": ctx.pre_std_threshold,
            "std_obs": ctx.std_obs,
            "decision_reason": ctx.decision_reason,
            "order_id": ctx.order_id,
            "client_order_id": ctx.client_order_id,
            "time_in_force": ctx.time_in_force,
            "submit_latency_ms": ctx.submit_latency_ms,
            "exchange_status": ctx.exchange_status,
            "fill_count": ctx.fill_count,
            "remaining_count": ctx.remaining_count,
            "actual_fill_price_cents": ctx.actual_fill_price_cents,
            "actual_fee_cents": ctx.actual_fee_cents,
            "result": ctx.result,
            "executable_window_ms": ctx.executable_window_ms,
        }
        payload.update(extra)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")


@dataclass
class BTCVolatilityRegimeSnapshot:
    range_dollars: float | None = None
    source: str = ""
    fetched_at_monotonic: float | None = None
    lookback_minutes: int = 15
    interval: str = "5m"
    error: str = ""


def bucket_rsi_state(value: float | None) -> str:
    if value is None:
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
    if value is None:
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
    if macd_line is None or signal_line is None:
        return "unknown"
    gap = float(macd_line) - float(signal_line)
    if gap >= 8.0:
        return "bullish"
    if gap <= -8.0:
        return "bearish"
    return "neutral"


def bucket_hist_state(hist: float | None, hist_change: float | None) -> str:
    if hist is None or hist_change is None:
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
    if value is None:
        return "unknown"
    if value >= 50.0:
        return "above"
    if value <= -50.0:
        return "below"
    return "near"


def ema_series(values: list[float], span: int) -> list[float]:
    if not values:
        return []
    alpha = 2.0 / (float(span) + 1.0)
    ema_values: list[float] = [float(values[0])]
    for value in values[1:]:
        ema_values.append((float(value) * alpha) + (ema_values[-1] * (1.0 - alpha)))
    return ema_values


def rsi14_series(closes: list[float]) -> list[float]:
    if not closes:
        return []
    alpha = 1.0 / 14.0
    avg_gain = 0.0
    avg_loss = 0.0
    values: list[float] = [50.0]
    for idx in range(1, len(closes)):
        delta = float(closes[idx]) - float(closes[idx - 1])
        gain = max(delta, 0.0)
        loss = max(-delta, 0.0)
        avg_gain = (gain * alpha) + (avg_gain * (1.0 - alpha))
        avg_loss = (loss * alpha) + (avg_loss * (1.0 - alpha))
        if idx < 14 or avg_loss <= 0.0:
            values.append(50.0)
        else:
            rs = avg_gain / avg_loss
            values.append(max(0.0, min(100.0, 100.0 - (100.0 / (1.0 + rs)))))
    return values


def compute_btc_live_technicals(closes: list[float]) -> dict[str, float | str | None]:
    if not closes:
        return {}
    rsi_values = rsi14_series(closes)
    ema12 = ema_series(closes, 12)
    ema26 = ema_series(closes, 26)
    macd_values = [fast - slow for fast, slow in zip(ema12, ema26)]
    macd_signal = ema_series(macd_values, 9)
    macd_hist = [line - signal for line, signal in zip(macd_values, macd_signal)]
    ema21 = ema_series(closes, 21)
    rsi_delta_3m = (rsi_values[-1] - rsi_values[-4]) if len(rsi_values) >= 4 else None
    hist_delta_3m = (macd_hist[-1] - macd_hist[-4]) if len(macd_hist) >= 4 else None
    price_vs_ema21 = (float(closes[-1]) - ema21[-1]) if ema21 else None
    return {
        "rsi14": rsi_values[-1] if rsi_values else None,
        "rsi14_state": bucket_rsi_state(rsi_values[-1] if rsi_values else None),
        "rsi14_slope_state": bucket_delta_state(rsi_delta_3m, fast=6.0, slow=1.5),
        "macd_line": macd_values[-1] if macd_values else None,
        "macd_signal": macd_signal[-1] if macd_signal else None,
        "macd_hist": macd_hist[-1] if macd_hist else None,
        "macd_state": bucket_macd_state(macd_values[-1] if macd_values else None, macd_signal[-1] if macd_signal else None),
        "macd_hist_state": bucket_hist_state(macd_hist[-1] if macd_hist else None, hist_delta_3m),
        "price_vs_ema21": price_vs_ema21,
        "price_vs_ema21_state": bucket_price_vs_ema_state(price_vs_ema21),
    }


@dataclass
class BTCSpotFeatureSnapshot:
    last_price: float | None = None
    move_1m_bps: float | None = None
    move_5m_bps: float | None = None
    move_15m_bps: float | None = None
    range_15m_dollars: float | None = None
    range_15m_bps: float | None = None
    distance_to_15m_high_bps: float | None = None
    distance_to_15m_low_bps: float | None = None
    rsi14: float | None = None
    rsi14_state: str = ""
    rsi14_slope_state: str = ""
    macd_line: float | None = None
    macd_signal: float | None = None
    macd_hist: float | None = None
    macd_state: str = ""
    macd_hist_state: str = ""
    price_vs_ema21: float | None = None
    price_vs_ema21_state: str = ""
    source: str = ""
    fetched_at_monotonic: float | None = None
    error: str = ""


@dataclass
class PostEntryShadowWatch:
    market_ticker: str
    side: str
    entry_dt_iso: str
    entry_fill_cents: int
    entry_trigger_cents: int | None
    entry_limit_cents: int | None
    seconds_to_close_at_entry: float | None
    book_age_ms_at_entry: float | None
    eligible_depth_at_entry: str | None
    executable_window_ms_at_entry: float | None
    entry_origin: str
    pre_entry_context: dict[str, Any] = field(default_factory=dict)
    btc_spot_snapshot_at_entry: dict[str, Any] = field(default_factory=dict)


class LiveOrderBook:
    def __init__(self) -> None:
        self.market_ticker: str | None = None
        self.yes_bids: dict[int, Decimal] = {}
        self.no_bids: dict[int, Decimal] = {}
        self.last_seq: int | None = None
        self.snapshot_ready: bool = False
        self.last_update_monotonic: float | None = None
        self.trust = OrderBookTrustState()

    def reset(self, market_ticker: str | None = None, *, trust_state: str = "cold") -> None:
        self.market_ticker = market_ticker
        self.yes_bids = {}
        self.no_bids = {}
        self.last_seq = None
        self.snapshot_ready = False
        self.last_update_monotonic = None
        self.trust.sequence_ok = trust_state == "synced"
        self.trust.trust_state = trust_state

    def apply_snapshot(self, message: dict[str, Any], seq: int | None = None) -> None:
        self.market_ticker = str(message.get("market_ticker") or "")
        yes_raw = message.get("yes_dollars_fp")
        no_raw = message.get("no_dollars_fp")
        yes_is_fp = yes_raw is not None
        no_is_fp = no_raw is not None
        self.yes_bids = snapshot_levels_to_book(yes_raw or message.get("yes_dollars") or message.get("yes") or [], quantity_is_fp=yes_is_fp)
        self.no_bids = snapshot_levels_to_book(no_raw or message.get("no_dollars") or message.get("no") or [], quantity_is_fp=no_is_fp)
        self.last_seq = seq
        self.snapshot_ready = True
        self.last_update_monotonic = time.monotonic()
        self.trust.sequence_ok = True
        self.trust.trust_state = "synced"
        self.trust.last_resync_ts = utc_now().isoformat()

    def mark_sequence_gap(self) -> None:
        self.trust.sequence_ok = False
        self.trust.trust_state = "degraded"
        self.trust.last_seq_gap_ts = utc_now().isoformat()

    def mark_resyncing(self) -> None:
        self.reset(self.market_ticker, trust_state="resyncing")
        self.trust.last_resync_ts = utc_now().isoformat()

    def apply_delta(self, message: dict[str, Any], seq: int | None = None) -> None:
        side = str(message.get("side") or "").lower()
        if side not in {"yes", "no"}:
            return
        book = self.yes_bids if side == "yes" else self.no_bids
        price_cents = extract_price_cents(message, side_prefix="price")
        if price_cents is None:
            return
        delta_is_fp = message.get("delta_fp") not in {None, ""}
        delta_qty = parse_contract_quantity(message.get("delta_fp", message.get("delta")), fixed_point=delta_is_fp)
        current_qty = book.get(price_cents, Decimal("0"))
        new_qty = current_qty + delta_qty
        if new_qty <= 0:
            book.pop(price_cents, None)
        else:
            book[price_cents] = new_qty
        self.last_seq = seq
        self.last_update_monotonic = time.monotonic()
        self.trust.sequence_ok = True
        self.trust.trust_state = "synced"

    def telemetry_fields(self) -> dict[str, Any]:
        return {
            "trust_state": self.trust.trust_state,
            "sequence_ok": self.trust.sequence_ok,
            "last_seq": self.last_seq,
            "snapshot_ready": self.snapshot_ready,
            "last_seq_gap_ts": self.trust.last_seq_gap_ts,
            "last_resync_ts": self.trust.last_resync_ts,
        }

    def best_bid(self, side: str) -> tuple[int | None, Decimal | None]:
        book = self.yes_bids if side == "yes" else self.no_bids
        if not book:
            return None, None
        price = max(book.keys())
        return price, book[price]

    def top_of_book_buy_limit_cents(self, side: str) -> int | None:
        if side == "yes":
            no_bid, _ = self.best_bid("no")
            return None if no_bid is None else 100 - no_bid
        if side == "no":
            yes_bid, _ = self.best_bid("yes")
            return None if yes_bid is None else 100 - yes_bid
        raise ValueError(f"Invalid side: {side}")

    def executable_buy_limit_cents(self, side: str, count: int) -> int | None:
        needed = Decimal(str(count))
        filled = Decimal("0")
        if side == "yes":
            levels = sorted(self.no_bids.items(), key=lambda item: item[0], reverse=True)
            limit: int | None = None
            for no_bid_cents, qty in levels:
                if qty <= 0:
                    continue
                filled += qty
                limit = 100 - no_bid_cents
                if filled >= needed:
                    return limit
            return None
        if side == "no":
            levels = sorted(self.yes_bids.items(), key=lambda item: item[0], reverse=True)
            limit = None
            for yes_bid_cents, qty in levels:
                if qty <= 0:
                    continue
                filled += qty
                limit = 100 - yes_bid_cents
                if filled >= needed:
                    return limit
            return None
        raise ValueError(f"Invalid side: {side}")

    def executable_buy_depth(self, side: str, limit_price_cents: int) -> Decimal:
        depth = Decimal("0")
        if side == "yes":
            levels = sorted(self.no_bids.items(), key=lambda item: item[0], reverse=True)
            for no_bid_cents, qty in levels:
                if qty <= 0:
                    continue
                implied_yes_ask = 100 - no_bid_cents
                if implied_yes_ask <= limit_price_cents:
                    depth += qty
            return depth
        if side == "no":
            levels = sorted(self.yes_bids.items(), key=lambda item: item[0], reverse=True)
            for yes_bid_cents, qty in levels:
                if qty <= 0:
                    continue
                implied_no_ask = 100 - yes_bid_cents
                if implied_no_ask <= limit_price_cents:
                    depth += qty
            return depth
        raise ValueError(f"Invalid side: {side}")

    def executable_sell_limit_cents(self, side: str, count: int) -> int | None:
        needed = Decimal(str(count))
        filled = Decimal("0")
        levels = sorted((self.yes_bids if side == "yes" else self.no_bids).items(), key=lambda item: item[0], reverse=True)
        limit: int | None = None
        for bid_cents, qty in levels:
            if qty <= 0:
                continue
            filled += qty
            limit = bid_cents
            if filled >= needed:
                return limit
        return None

    def executable_sell_depth(self, side: str, limit_price_cents: int) -> Decimal:
        depth = Decimal("0")
        levels = sorted((self.yes_bids if side == "yes" else self.no_bids).items(), key=lambda item: item[0], reverse=True)
        for bid_cents, qty in levels:
            if qty <= 0:
                continue
            if bid_cents >= limit_price_cents:
                depth += qty
        return depth

    def visible_bid_levels(self, side: str, max_levels: int = 5) -> list[dict[str, Any]]:
        book = self.yes_bids if side == "yes" else self.no_bids
        levels: list[dict[str, Any]] = []
        for price_cents, qty in sorted(book.items(), key=lambda item: item[0], reverse=True)[:max_levels]:
            if qty <= 0:
                continue
            levels.append({
                "bid_cents": price_cents,
                "size": format_decimal_compact(qty),
            })
        return levels

    def visible_buy_levels(self, side: str, max_levels: int = 5) -> list[dict[str, Any]]:
        source = self.no_bids if side == "yes" else self.yes_bids
        levels: list[dict[str, Any]] = []
        for bid_cents, qty in sorted(source.items(), key=lambda item: item[0], reverse=True)[:max_levels]:
            if qty <= 0:
                continue
            levels.append({
                "ask_cents": 100 - bid_cents,
                "backing_bid_cents": bid_cents,
                "size": format_decimal_compact(qty),
            })
        return levels


class KalshiClient:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.base_url = config.base_url.rstrip("/")
        self.ws_url = config.ws_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "kalshi-btc15m-bot-ws/2.0"})
        self.private_key = self._load_private_key(config.private_key_path)

    def _load_private_key(self, path: Path):
        with path.open("rb") as fh:
            return serialization.load_pem_private_key(
                fh.read(),
                password=None,
                backend=default_backend(),
            )

    def _sign_request(self, timestamp_ms: str, method: str, path: str) -> str:
        message = f"{timestamp_ms}{method.upper()}{path.split('?')[0]}".encode("utf-8")
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH,
            ),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode("utf-8")

    def _auth_headers(self, method: str, endpoint_path: str) -> dict[str, str]:
        timestamp_ms = str(int(time.time() * 1000))
        full_url = self.base_url + endpoint_path
        path = urlparse(full_url).path
        signature = self._sign_request(timestamp_ms, method, path)
        return {
            "KALSHI-ACCESS-KEY": self.config.api_key_id,
            "KALSHI-ACCESS-TIMESTAMP": timestamp_ms,
            "KALSHI-ACCESS-SIGNATURE": signature,
        }

    def websocket_headers(self) -> dict[str, str]:
        timestamp_ms = str(int(time.time() * 1000))
        path = urlparse(self.ws_url).path
        signature = self._sign_request(timestamp_ms, "GET", path)
        return {
            "KALSHI-ACCESS-KEY": self.config.api_key_id,
            "KALSHI-ACCESS-TIMESTAMP": timestamp_ms,
            "KALSHI-ACCESS-SIGNATURE": signature,
        }

    def request(
        self,
        method: str,
        endpoint_path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        auth: bool = False,
    ) -> dict[str, Any]:
        url = self.base_url + endpoint_path
        headers: dict[str, str] = {}
        if auth:
            headers.update(self._auth_headers(method, endpoint_path))
            if json_body is not None:
                headers["Content-Type"] = "application/json"
        response = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            json=json_body,
            headers=headers,
            timeout=self.config.http_timeout_seconds,
        )
        if response.status_code >= 400:
            raise requests.HTTPError(
                f"{response.status_code} {response.reason}: {response.text}",
                response=response,
            )
        if not response.text:
            return {}
        return response.json()

    def get_active_btc15m_market(self) -> dict[str, Any] | None:
        # Current live market status is documented as "active". Keep fallbacks for compatibility.
        statuses = ["active", "open", "initialized"]
        candidates: list[dict[str, Any]] = []
        max_initialized_lead = timedelta(minutes=20)
        for status in statuses:
            try:
                data = self.request(
                    "GET",
                    "/markets",
                    params={"series_ticker": self.config.series_ticker, "status": status, "limit": 100},
                    auth=False,
                )
            except requests.HTTPError as exc:
                if "invalid status filter" in str(exc).lower():
                    continue
                raise
            markets = list(data.get("markets", []))
            for market in markets:
                ticker = normalize_ticker(str(market.get("ticker", "")))
                if not ticker.startswith(ALLOWED_TICKER_PREFIX):
                    continue
                close_time = parse_iso(str(market.get("close_time") or ""))
                if status == "initialized" and close_time is not None and close_time > utc_now() + max_initialized_lead:
                    continue
                candidates.append(market)
            if candidates:
                break
        if not candidates:
            data = self.request(
                "GET",
                "/markets",
                params={"series_ticker": self.config.series_ticker, "limit": 100},
                auth=False,
            )
            markets = list(data.get("markets", []))
            for market in markets:
                ticker = normalize_ticker(str(market.get("ticker", "")))
                if ticker.startswith(ALLOWED_TICKER_PREFIX):
                    candidates.append(market)
        if not candidates:
            return None
        now = utc_now()
        future = []
        for market in candidates:
            close_time = parse_iso(str(market.get("close_time") or ""))
            if close_time and close_time >= now - timedelta(seconds=5):
                future.append(market)
        if future:
            candidates = future
        candidates.sort(key=lambda m: parse_iso(str(m.get("close_time") or "")) or datetime.max.replace(tzinfo=timezone.utc))
        return candidates[0]

    def get_market(self, ticker: str) -> dict[str, Any] | None:
        data = self.request("GET", "/markets", params={"tickers": ticker, "limit": 10}, auth=False)
        for market in data.get("markets", []):
            if normalize_ticker(str(market.get("ticker", ""))) == normalize_ticker(ticker):
                return market
        return None

    def get_order(self, order_id: str) -> dict[str, Any]:
        data = self.request("GET", f"/portfolio/orders/{order_id}", auth=True)
        return data["order"]

    def get_positions(self, ticker: str | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"subaccount": 0}
        if ticker:
            params["ticker"] = ticker
        data = self.request("GET", "/portfolio/positions", params=params, auth=True)
        return list(data.get("market_positions", data.get("positions", [])))

    def get_balance(self) -> dict[str, Any]:
        return self.request("GET", "/portfolio/balance", params={"subaccount": 0}, auth=True)

    def get_resting_orders(self) -> list[dict[str, Any]]:
        param_candidates = (
            {"subaccount": 0, "status": "resting", "limit": 200},
            {"subaccount": 0, "status": "open", "limit": 200},
            {"subaccount": 0, "limit": 200},
        )
        last_error: Exception | None = None
        for params in param_candidates:
            try:
                data = self.request("GET", "/portfolio/orders", params=params, auth=True)
                orders = data.get("orders", data.get("portfolio_orders", []))
                return [order for order in orders if is_resting_order(order)]
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        if last_error is not None:
            raise last_error
        return []

    def create_order(
        self,
        *,
        ticker: str,
        side: str,
        action: str,
        count: int,
        limit_price_cents: int,
        reduce_only: bool = False,
        time_in_force: str = "fill_or_kill",
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "ticker": ticker,
            "side": side,
            "action": action,
            "count": count,
            "client_order_id": client_order_id or str(uuid.uuid4()),
            "cancel_order_on_pause": True,
            "self_trade_prevention_type": "taker_at_cross",
            "subaccount": 0,
            "time_in_force": time_in_force,
        }
        if side == "yes":
            body["yes_price"] = limit_price_cents
        else:
            body["no_price"] = limit_price_cents
        if action == "buy" and time_in_force == "fill_or_kill":
            body["buy_max_cost"] = limit_price_cents * count
        elif action != "buy":
            body["reduce_only"] = reduce_only
        return self.request("POST", "/portfolio/orders", json_body=body, auth=True)


class BTC15MKalshiWebSocketBot:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.client = KalshiClient(config)
        self.logger = build_logger(config.log_level, config.log_path)
        self.state_store = StateStore(config.state_path)
        self.state = self.state_store.load()
        self.orderbook = LiveOrderBook()
        self.market = MarketSnapshot()
        self.telemetry = ExecutionTelemetryWriter(
            config.execution_telemetry_path,
            enabled=config.execution_telemetry_enabled,
            run_id=config.run_id,
        )
        self.lease_cache_store = LeaseCacheStore(config.truffle_regime_lease_cache_path)
        self.lease_events = LeaseEventWriter(config.truffle_regime_lease_events_path)
        self.market_outcomes = MarketOutcomeStore(config.truffle_regime_lease_outcomes_path)
        self.post_entry_shadow_events = LeaseEventWriter(config.truffle_post_entry_shadow_events_path)
        self.current_regime_lease: LeaseDecision | None = self.lease_cache_store.load()
        self.truffle_regime_prompt_text = load_prompt_text(config.truffle_regime_lease_prompt_path)
        self.truffle_regime_tool_prompt_text = load_prompt_text(
            config.truffle_regime_lease_tool_prompt_path,
            default_text=DEFAULT_TRUFFLE_REASONING_TOOL_PROMPT,
        )
        self.truffle_post_entry_shadow_prompt_text = load_prompt_text(
            config.truffle_post_entry_shadow_prompt_path,
            default_text=DEFAULT_TRUFFLE_POST_ENTRY_SHADOW_PROMPT,
        )
        self.current_watch_ticker: str | None = None
        self.watch_close_time: str | None = None
        self.last_market_refresh_monotonic = 0.0
        self.last_rest_order_check_monotonic = 0.0
        self.last_heartbeat_monotonic = 0.0
        self.shutdown_event = asyncio.Event()
        self.ws_task: asyncio.Task[Any] | None = None
        self.account_state_task: asyncio.Task[Any] | None = None
        self.btc_regime_task: asyncio.Task[Any] | None = None
        self.mushroom_v28_btc_tick_task: asyncio.Task[Any] | None = None
        self.ws_connection_generation = 0
        self.order_inflight = False
        self.recent_price_history: collections.deque[dict[str, Any]] = collections.deque(
            maxlen=recent_price_history_maxlen(self.config)
        )
        self.last_filter_log_key: str | None = None
        self.last_filter_log_monotonic = 0.0
        self.live_account_snapshot = LiveAccountSnapshot()
        self.btc_vol_regime_snapshot = BTCVolatilityRegimeSnapshot(
            lookback_minutes=int(self.config.btc_vol_regime_lookback_minutes),
            interval=str(self.config.btc_vol_regime_interval),
        )
        self.btc_spot_snapshot = BTCSpotFeatureSnapshot()
        self.mushroom_lock = threading.Lock()
        self.mushroom_forecaster = MushroomForecaster(MushroomConfig()) if self.config.mushroom_shadow_enabled else None
        self.mushroom_v21_forecaster = (
            MushroomForecaster(mushroom_v21_config()) if self.config.mushroom_v21_decision_engine_enabled else None
        )
        self.mushroom_v28_worker = self.build_mushroom_v28_worker() if self.mushroom_v28_configured() else None
        self.mushroom_v28_last_tick_monotonic = 0.0
        self.mushroom_v28_last_tick_price: float | None = None
        self.mushroom_v28_last_tick_ts: datetime | None = None
        self.mushroom_v28_last_tick_source = ""
        self.mushroom_v28_last_error = ""
        self.mushroom_seen_bar_closes: collections.deque[int] = collections.deque(maxlen=5000)
        self.mushroom_seen_bar_close_set: set[int] = set()
        self.last_mushroom_shadow_log_key: str | None = None
        self.last_account_state_attempt_monotonic = 0.0
        self.last_ws_resync_monotonic = 0.0
        self.last_price_history_append_monotonic = 0.0
        self.market_reaction_task: asyncio.Task[Any] | None = None
        self.post_entry_shadow_task: asyncio.Task[Any] | None = None
        self.post_entry_shadow_watch: PostEntryShadowWatch | None = None
        self.post_entry_shadow_decisions: dict[str, PostEntryShadowDecision] = {}
        self.post_entry_shadow_outcome_emitted_markets: set[str] = set()
        self.post_entry_shadow_exit_memory: collections.deque[dict[str, Any]] = collections.deque(maxlen=64)
        self.load_post_entry_shadow_exit_memory_from_log()
        self.live_lock_acquired = False
        self.entry_retry_block_until_monotonic = 0.0
        self.exit_retry_block_until_monotonic = 0.0
        self.entry_rejection_state: dict[str, EntryRejectionState] = {}
        self.entry_last_attempt_monotonic: dict[str, float] = {}
        self.entry_skip_state: dict[str, EntrySkipState] = {}
        self.liquidity_dwell_candidates: dict[str, LiquidityDwellCandidate] = {}
        self.execution_state: dict[str, MarketSideExecutionState] = {}
        self.executable_windows: dict[str, ExecutableWindowState] = {}
        self.shutdown_reason = "not_requested"
        self.last_loop_monotonic = 0.0
        self.max_loop_gap_seconds = max(15.0, self.config.heartbeat_log_seconds * 2.0)

    def save_state(self) -> None:
        self.state_store.save(self.state)

    def already_traded(self, ticker: str) -> bool:
        key = normalize_ticker(ticker)
        return key in {normalize_ticker(t) for t in self.state.traded_markets}

    def mark_traded(self, ticker: str) -> None:
        if not self.already_traded(ticker):
            self.state.traded_markets.append(ticker)
        self.state.traded_markets = self.state.traded_markets[-1000:]
        self.save_state()

    def entry_block_reason(self, ticker: str, side: str | None = None, count: int | None = None) -> str | None:
        ticker_key = normalize_ticker(ticker)
        position = self.state.position
        add_count = max(1, int(count or self.config.position_size))
        if position is None:
            if self.already_traded(ticker) and not self.config.multi_entry_same_market_enabled:
                return "already_traded"
            return None
        if normalize_ticker(position.market_ticker) != ticker_key:
            return "different_open_position"
        if side is not None and position.side != side:
            return "opposite_side_position"
        if not self.config.multi_entry_same_market_enabled:
            return "position_open"
        max_contracts = max(1, int(self.config.multi_entry_max_position_contracts))
        if int(position.count) + add_count > max_contracts:
            return "max_position_contracts"
        cooldown = float(self.config.multi_entry_min_seconds_between_entries)
        if cooldown > 0:
            filled_at = parse_iso(position.filled_at)
            if filled_at is not None:
                seconds_since_fill = (utc_now() - filled_at).total_seconds()
                if seconds_since_fill < cooldown:
                    return "multi_entry_cooldown"
            if side is not None:
                last_attempt = self.entry_last_attempt_monotonic.get(f"{ticker_key}:{side}")
                if last_attempt is not None and (time.monotonic() - last_attempt) < cooldown:
                    return "multi_entry_cooldown"
        return None

    def note_entry_attempt_for_cooldown(self, ticker: str, side: str) -> None:
        position = self.state.position
        if position is None:
            return
        if normalize_ticker(position.market_ticker) != normalize_ticker(ticker) or position.side != side:
            return
        self.entry_last_attempt_monotonic[f"{normalize_ticker(ticker)}:{side}"] = time.monotonic()

    def weighted_average_cents(self, old_price: int | None, old_count: int, new_price: int | None, new_count: int) -> int | None:
        if old_price is None and new_price is None:
            return None
        if old_count <= 0:
            return int(new_price) if new_price is not None else None
        if new_count <= 0:
            return int(old_price) if old_price is not None else None
        old_value = Decimal(str(old_price if old_price is not None else new_price))
        new_value = Decimal(str(new_price if new_price is not None else old_price))
        total_count = Decimal(str(old_count + new_count))
        weighted = ((old_value * Decimal(str(old_count))) + (new_value * Decimal(str(new_count)))) / total_count
        return int(weighted.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    def apply_entry_fill_to_position(
        self,
        *,
        market_ticker: str,
        side: str,
        fill_count: int,
        entry_order_id: str,
        entry_limit_price_cents: int,
        entry_fill_price_cents: int,
        entry_fee_cents: int,
        entry_trigger_price_cents: int | None,
    ) -> PositionState:
        if fill_count <= 0:
            raise ValueError("Cannot apply an entry fill with non-positive count.")
        now_iso = utc_now().isoformat()
        existing = self.state.position
        if existing is not None:
            if normalize_ticker(existing.market_ticker) != normalize_ticker(market_ticker):
                raise ValueError("Cannot add entry fill to a different open market.")
            if existing.side != side:
                raise ValueError("Cannot add entry fill on the opposite side of an open position.")
            old_count = int(existing.count)
            old_limit_price = int(existing.entry_limit_price_cents)
            old_fill_price = (
                int(existing.entry_fill_price_cents)
                if existing.entry_fill_price_cents is not None
                else old_limit_price
            )
            existing.count = old_count + int(fill_count)
            existing.filled_at = now_iso
            existing.entry_order_id = entry_order_id or existing.entry_order_id
            existing.entry_limit_price_cents = self.weighted_average_cents(
                old_limit_price,
                old_count,
                int(entry_limit_price_cents),
                int(fill_count),
            ) or int(entry_limit_price_cents)
            existing.entry_fill_price_cents = self.weighted_average_cents(
                old_fill_price,
                old_count,
                int(entry_fill_price_cents),
                int(fill_count),
            )
            existing.entry_fee_cents = int(existing.entry_fee_cents or 0) + int(entry_fee_cents or 0)
            existing.entry_trigger_price_cents = (
                int(entry_trigger_price_cents)
                if entry_trigger_price_cents is not None
                else existing.entry_trigger_price_cents
            )
            self.state.exit_confirmation = None
            return existing
        self.state.position = PositionState(
            market_ticker=market_ticker,
            side=side,
            count=int(fill_count),
            filled_at=now_iso,
            entry_order_id=entry_order_id,
            entry_limit_price_cents=int(entry_limit_price_cents),
            entry_fill_price_cents=int(entry_fill_price_cents),
            entry_fee_cents=int(entry_fee_cents or 0),
            entry_trigger_price_cents=entry_trigger_price_cents,
        )
        self.state.exit_confirmation = None
        return self.state.position

    def ensure_market_outcome_record(self, market_ticker: str, close_time: str | None = None) -> None:
        close_dt = parse_iso(close_time) if close_time else None
        local_close_dt = close_dt.astimezone() if close_dt is not None else None
        self.market_outcomes.ensure_market(
            market_ticker,
            session=infer_session_label(local_close_dt),
            watched_at=utc_now().isoformat(),
            market_close_time=close_time or "",
        )
        self.market_outcomes.save()

    def backfill_persisted_position_outcome(self) -> None:
        position = self.state.position
        if position is None:
            return
        existing = self.market_outcomes.get(position.market_ticker)
        if existing is not None and existing.traded:
            return
        fill_price_cents = (
            int(position.entry_fill_price_cents)
            if position.entry_fill_price_cents is not None
            else int(position.entry_limit_price_cents)
        )
        fee_cents = int(position.entry_fee_cents or 0)
        if fee_cents <= 0:
            fee_cents = self.estimated_order_fee_cents(fill_price_cents, int(position.count))
        self.market_outcomes.record_entry(
            position.market_ticker,
            side=position.side,
            qty=int(position.count),
            fill_price_cents=fill_price_cents,
            fee_cents=fee_cents,
            trigger_price_cents=position.entry_trigger_price_cents,
        )

    def record_entry_fill_for_outcomes(
        self,
        *,
        market_ticker: str,
        side: str,
        fill_count: int,
        fill_price_cents: int,
        trigger_price_cents: int | None,
        actual_fee_cents: int | None,
    ) -> None:
        if fill_count <= 0 or fill_price_cents <= 0:
            return
        effective_fee_cents = (
            int(actual_fee_cents)
            if actual_fee_cents is not None and int(actual_fee_cents) >= 0
            else self.estimated_order_fee_cents(fill_price_cents, fill_count)
        )
        self.market_outcomes.record_entry(
            market_ticker,
            side=side,
            qty=fill_count,
            fill_price_cents=fill_price_cents,
            fee_cents=effective_fee_cents,
            trigger_price_cents=trigger_price_cents,
        )

    def record_exit_fill_for_outcomes(
        self,
        *,
        market_ticker: str,
        fill_count: int,
        fill_price_cents: int,
        remaining_position: int,
        actual_fee_cents: int | None,
    ) -> None:
        if fill_count <= 0 or fill_price_cents <= 0:
            return
        effective_fee_cents = (
            int(actual_fee_cents)
            if actual_fee_cents is not None and int(actual_fee_cents) >= 0
            else self.estimated_order_fee_cents(fill_price_cents, fill_count)
        )
        self.market_outcomes.record_exit_fill(
            market_ticker,
            qty=fill_count,
            fill_price_cents=fill_price_cents,
            fee_cents=effective_fee_cents,
            remaining_position=remaining_position,
            resolved_at=utc_now().isoformat(),
        )
        self.emit_post_entry_shadow_outcome_if_ready(market_ticker)

    async def maybe_finalize_market_outcome_from_exchange(self, market_ticker: str) -> None:
        record = self.market_outcomes.get(market_ticker)
        if record is None:
            return
        if record.outcome_type in {"exit", "win", "settlement_loss", "void", "no_trade"}:
            return
        if not record.traded:
            self.market_outcomes.finalize_no_trade(market_ticker, resolved_at=utc_now().isoformat())
            return
        try:
            market = await asyncio.to_thread(self.client.get_market, market_ticker)
        except Exception as exc:  # noqa: BLE001
            self.logger.debug("Lease outcome refresh skipped for %s due to market fetch error: %s", market_ticker, exc)
            return
        result = str(market.get("result") or "").strip().lower()
        status = str(market.get("status") or "").strip().lower()
        resolved_at = str(
            market.get("settlement_ts")
            or market.get("close_time")
            or market.get("expiration_time")
            or utc_now().isoformat()
        )
        if result in {"yes", "no", "void"}:
            self.market_outcomes.finalize_settlement(market_ticker, result=result, resolved_at=resolved_at)
            self.emit_post_entry_shadow_outcome_if_ready(market_ticker)
            return
        if status in {"settled", "resolved", "finalized", "final"} and result == "void":
            self.market_outcomes.finalize_settlement(market_ticker, result=result, resolved_at=resolved_at)
            self.emit_post_entry_shadow_outcome_if_ready(market_ticker)

    async def refresh_recent_market_outcomes_from_exchange(self, limit: int = 8) -> None:
        for record in self.market_outcomes.unresolved_closed_markets(as_of=utc_now(), limit=limit):
            await self.maybe_finalize_market_outcome_from_exchange(record.market)

    def serialize_btc_spot_snapshot(self) -> dict[str, Any]:
        snapshot = self.btc_spot_snapshot
        return {
            "last_price": round(float(snapshot.last_price), 4) if snapshot.last_price is not None else None,
            "move_1m_bps": round(float(snapshot.move_1m_bps), 4) if snapshot.move_1m_bps is not None else None,
            "move_5m_bps": round(float(snapshot.move_5m_bps), 4) if snapshot.move_5m_bps is not None else None,
            "move_15m_bps": round(float(snapshot.move_15m_bps), 4) if snapshot.move_15m_bps is not None else None,
            "range_15m_dollars": round(float(snapshot.range_15m_dollars), 4) if snapshot.range_15m_dollars is not None else None,
            "range_15m_bps": round(float(snapshot.range_15m_bps), 4) if snapshot.range_15m_bps is not None else None,
            "distance_to_15m_high_bps": round(float(snapshot.distance_to_15m_high_bps), 4) if snapshot.distance_to_15m_high_bps is not None else None,
            "distance_to_15m_low_bps": round(float(snapshot.distance_to_15m_low_bps), 4) if snapshot.distance_to_15m_low_bps is not None else None,
            "rsi14": round(float(snapshot.rsi14), 4) if snapshot.rsi14 is not None else None,
            "rsi14_state": snapshot.rsi14_state,
            "rsi14_slope_state": snapshot.rsi14_slope_state,
            "macd_line": round(float(snapshot.macd_line), 4) if snapshot.macd_line is not None else None,
            "macd_signal": round(float(snapshot.macd_signal), 4) if snapshot.macd_signal is not None else None,
            "macd_hist": round(float(snapshot.macd_hist), 4) if snapshot.macd_hist is not None else None,
            "macd_state": snapshot.macd_state,
            "macd_hist_state": snapshot.macd_hist_state,
            "price_vs_ema21": round(float(snapshot.price_vs_ema21), 4) if snapshot.price_vs_ema21 is not None else None,
            "price_vs_ema21_state": snapshot.price_vs_ema21_state,
            "source": snapshot.source,
            "age_ms": round(float(self.btc_spot_snapshot_age_ms()), 2) if self.btc_spot_snapshot_age_ms() is not None else None,
            "error": snapshot.error,
        }

    def resolved_post_entry_shadow_endpoint(self) -> str:
        return str(self.config.truffle_post_entry_shadow_endpoint or self.config.truffle_regime_lease_endpoint).strip()

    def resolved_post_entry_shadow_model(self) -> str:
        return str(self.config.truffle_post_entry_shadow_model or self.config.truffle_regime_lease_model).strip()

    def resolved_post_entry_shadow_api_key(self) -> str:
        return str(self.config.truffle_post_entry_shadow_api_key or self.config.truffle_regime_lease_api_key).strip()

    def load_post_entry_shadow_exit_memory_from_log(self) -> None:
        path = self.config.truffle_post_entry_shadow_events_path
        if not path.exists():
            return
        try:
            with path.open("r", encoding="utf-8") as handle:
                tail_lines = collections.deque(handle, maxlen=512)
        except Exception:
            return
        for line in tail_lines:
            try:
                event = json.loads(line)
            except Exception:
                continue
            if not isinstance(event, dict) or event.get("event_type") != "post_entry_shadow_outcome":
                continue
            shadow_exit_eval = event.get("shadow_exit_eval")
            if not isinstance(shadow_exit_eval, dict) or not shadow_exit_eval.get("available"):
                continue
            self.record_post_entry_shadow_exit_memory(
                market=str(event.get("market") or ""),
                shadow_exit_eval=shadow_exit_eval,
                issued_at=str(event.get("ts_wall") or ""),
            )

    def record_post_entry_shadow_exit_memory(
        self,
        *,
        market: str,
        shadow_exit_eval: dict[str, Any],
        issued_at: str,
    ) -> None:
        if not isinstance(shadow_exit_eval, dict) or not shadow_exit_eval.get("available"):
            return
        tags = [str(tag) for tag in list(shadow_exit_eval.get("candidate_slice_tags") or []) if str(tag)]
        try:
            delta = float(shadow_exit_eval.get("delta_vs_actual_dollars") or 0.0)
        except Exception:
            delta = 0.0
        self.post_entry_shadow_exit_memory.append(
            {
                "market": str(market or ""),
                "issued_at": str(issued_at or ""),
                "tags": tags,
                "delta_vs_actual_dollars": round(delta, 4),
                "truth_label": str(shadow_exit_eval.get("truth_label") or ""),
                "model_decision": str(shadow_exit_eval.get("model_decision") or ""),
                "decision_schema": str(shadow_exit_eval.get("decision_schema") or ""),
            }
        )

    def summarize_shadow_exit_memory_rows(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        deltas = [float(row.get("delta_vs_actual_dollars") or 0.0) for row in rows]
        last2 = deltas[-2:]
        last3 = deltas[-3:]
        last5 = deltas[-5:]
        return {
            "count": int(len(rows)),
            "last2_delta_sum": round(float(sum(last2)), 4),
            "last3_delta_sum": round(float(sum(last3)), 4),
            "last5_delta_sum": round(float(sum(last5)), 4),
            "last2_all_positive": bool(len(last2) == 2 and all(value > 0 for value in last2)),
            "last5_positive_count": int(sum(1 for value in last5 if value > 0)),
            "last5_negative_count": int(sum(1 for value in last5 if value < 0)),
            "last5_false_exit_cost_dollars": round(float(-sum(value for value in last5 if value < 0)), 4),
            "last5_oracle_exit_value_dollars": round(float(sum(value for value in last5 if value > 0)), 4),
            "last5_truth_sequence": [str(row.get("truth_label") or "") for row in rows[-5:]],
        }

    def summarize_post_entry_shadow_exit_memory(self, candidate_slice_tags: list[str]) -> dict[str, Any]:
        rows = list(self.post_entry_shadow_exit_memory)
        tags = [str(tag) for tag in candidate_slice_tags if str(tag)]
        by_tag: dict[str, Any] = {}
        for tag in tags:
            tagged = [row for row in rows if tag in list(row.get("tags") or [])]
            by_tag[tag] = self.summarize_shadow_exit_memory_rows(tagged) if tagged else {"count": 0}
        return {
            "schema_version": "shadow_exit_memory_v1",
            "source": "prior_resolved_shadow_outcomes_only",
            "global": self.summarize_shadow_exit_memory_rows(rows) if rows else {"count": 0},
            "candidate_tags": by_tag,
        }

    def emit_post_entry_shadow_outcome_if_ready(self, market_ticker: str) -> None:
        key = normalize_ticker(market_ticker)
        if key in self.post_entry_shadow_outcome_emitted_markets:
            return
        decision = self.post_entry_shadow_decisions.get(key)
        if decision is None:
            return
        outcome = self.market_outcomes.get(market_ticker)
        if outcome is None:
            return
        if outcome.outcome_type not in {"exit", "win", "settlement_loss", "void", "no_trade"}:
            return
        shadow_exit_eval = self.build_post_entry_shadow_exit_eval(decision, outcome)
        self.post_entry_shadow_events.emit(
            "post_entry_shadow_outcome",
            market=market_ticker,
            side=decision.side,
            outcome_type=outcome.outcome_type,
            pnl_dollars=outcome.pnl_dollars,
            decision=decision.to_dict(),
            outcome_record=outcome.to_dict(),
            shadow_exit_eval=shadow_exit_eval,
        )
        self.record_post_entry_shadow_exit_memory(
            market=market_ticker,
            shadow_exit_eval=shadow_exit_eval,
            issued_at=decision.issued_at,
        )
        self.post_entry_shadow_outcome_emitted_markets.add(key)

    def build_post_entry_shadow_exit_eval(
        self,
        decision: PostEntryShadowDecision,
        outcome: Any,
    ) -> dict[str, Any]:
        payload = decision.input_payload if isinstance(decision.input_payload, dict) else {}
        current_exit_bid = payload.get("current_exit_bid_cents")
        try:
            current_exit_bid_cents = float(current_exit_bid)
        except Exception:
            return {"available": False, "reason": "missing_current_exit_bid_cents"}
        entry_qty = int(getattr(outcome, "entry_qty", 0) or 0)
        entry_fill_cents = getattr(outcome, "entry_fill_cents", None)
        if entry_qty <= 0 or entry_fill_cents is None:
            return {"available": False, "reason": "missing_entry_outcome_fields"}
        entry_fee_cents = int(getattr(outcome, "entry_fee_cents", 0) or 0)
        exit_fee_cents = self.estimated_order_fee_cents(current_exit_bid_cents, entry_qty)
        hypothetical_net_pnl = (
            (entry_qty * (float(current_exit_bid_cents) - float(entry_fill_cents)) / 100.0)
            - ((entry_fee_cents + exit_fee_cents) / 100.0)
        )
        actual_pnl = float(getattr(outcome, "pnl_dollars", 0.0) or 0.0)
        delta = hypothetical_net_pnl - actual_pnl
        if delta >= 1.0:
            truth = "EXIT_NOW"
        elif delta <= -1.0:
            truth = "HOLD"
        else:
            truth = "NEUTRAL"
        return {
            "available": True,
            "schema_version": "post_entry_shadow_exit_eval_v1",
            "current_exit_bid_cents": round(float(current_exit_bid_cents), 4),
            "entry_qty": entry_qty,
            "entry_fill_cents": int(entry_fill_cents),
            "entry_fee_cents": entry_fee_cents,
            "estimated_exit_fee_cents": int(exit_fee_cents),
            "hypothetical_exit_net_pnl_dollars": round(float(hypothetical_net_pnl), 4),
            "actual_pnl_dollars": round(float(actual_pnl), 4),
            "delta_vs_actual_dollars": round(float(delta), 4),
            "truth_label": truth,
            "candidate_slice_tags": list(payload.get("candidate_slice_tags") or []),
            "model_decision": decision.decision or ("EXIT_NOW" if decision.is_red else "HOLD" if decision.is_green else "NEUTRAL"),
            "decision_schema": decision.decision_schema,
        }

    def arm_post_entry_shadow_watch(
        self,
        *,
        market_ticker: str,
        side: str,
        filled_at_iso: str,
        entry_fill_cents: int,
        entry_trigger_cents: int | None,
        entry_limit_cents: int | None,
        seconds_to_close_at_entry: float | None,
        book_age_ms_at_entry: float | None,
        eligible_depth_at_entry: Decimal | None,
        executable_window_ms_at_entry: float | None,
        entry_origin: str,
    ) -> None:
        if not self.config.truffle_post_entry_shadow_enabled:
            return
        entry_dt = parse_iso(filled_at_iso)
        if entry_dt is None:
            self.post_entry_shadow_events.emit(
                "post_entry_shadow_skipped",
                market=market_ticker,
                side=side,
                reason="missing_entry_timestamp",
                entry_origin=entry_origin,
            )
            return
        delay_seconds = max(0.0, float(self.config.truffle_post_entry_shadow_delay_seconds))
        if seconds_to_close_at_entry is not None and float(seconds_to_close_at_entry) < (delay_seconds + 5.0):
            self.post_entry_shadow_events.emit(
                "post_entry_shadow_skipped",
                market=market_ticker,
                side=side,
                reason="insufficient_time_to_shadow_delay",
                entry_origin=entry_origin,
                seconds_to_close_at_entry=seconds_to_close_at_entry,
                shadow_delay_seconds=delay_seconds,
            )
            return
        history_rows = list(self.recent_price_history)
        watch = PostEntryShadowWatch(
            market_ticker=market_ticker,
            side=side,
            entry_dt_iso=filled_at_iso,
            entry_fill_cents=int(entry_fill_cents),
            entry_trigger_cents=(int(entry_trigger_cents) if entry_trigger_cents is not None else None),
            entry_limit_cents=(int(entry_limit_cents) if entry_limit_cents is not None else None),
            seconds_to_close_at_entry=seconds_to_close_at_entry,
            book_age_ms_at_entry=book_age_ms_at_entry,
            eligible_depth_at_entry=(format_decimal_compact(eligible_depth_at_entry) if eligible_depth_at_entry is not None else None),
            executable_window_ms_at_entry=executable_window_ms_at_entry,
            entry_origin=entry_origin,
            pre_entry_context=build_pre_entry_context(
                history_rows,
                market_ticker=market_ticker,
                side=side,
                entry_dt=entry_dt,
            ),
            btc_spot_snapshot_at_entry=self.serialize_btc_spot_snapshot(),
        )
        if self.post_entry_shadow_task and not self.post_entry_shadow_task.done():
            self.post_entry_shadow_task.cancel()
        self.post_entry_shadow_watch = watch
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            self.post_entry_shadow_events.emit(
                "post_entry_shadow_skipped",
                market=market_ticker,
                side=side,
                reason="no_running_event_loop",
                entry_origin=entry_origin,
            )
            return
        self.post_entry_shadow_task = loop.create_task(self.run_post_entry_shadow_after_delay(watch))
        self.post_entry_shadow_events.emit(
            "post_entry_shadow_scheduled",
            market=market_ticker,
            side=side,
            entry_origin=entry_origin,
            entry_fill_cents=int(entry_fill_cents),
            entry_trigger_cents=(int(entry_trigger_cents) if entry_trigger_cents is not None else None),
            entry_limit_cents=(int(entry_limit_cents) if entry_limit_cents is not None else None),
            seconds_to_close_at_entry=seconds_to_close_at_entry,
            shadow_delay_seconds=delay_seconds,
            pre_entry_context=watch.pre_entry_context,
            btc_spot_snapshot_at_entry=watch.btc_spot_snapshot_at_entry,
        )

    def build_post_entry_shadow_payload(self, watch: PostEntryShadowWatch, *, as_of: datetime) -> dict[str, Any] | None:
        entry_dt = parse_iso(watch.entry_dt_iso)
        if entry_dt is None:
            return None
        history_rows = [row for row in self.recent_price_history if str(row.get("market") or "") == watch.market_ticker]
        if not history_rows:
            return None
        payload: dict[str, Any] = {
            "schema_version": "single_call_trade_context_v1",
            "market": watch.market_ticker,
            "side": str(watch.side).strip().upper(),
            "seconds_since_entry": max(0, int(round((as_of - entry_dt).total_seconds()))),
            "pre_entry": watch.pre_entry_context,
            "post_entry": build_post_entry_context(
                history_rows,
                market_ticker=watch.market_ticker,
                side=watch.side,
                entry_dt=entry_dt,
                as_of_dt=as_of,
                entry_fill_cents=float(watch.entry_fill_cents),
            ),
        }
        decision_schema = str(self.config.truffle_post_entry_shadow_decision_schema or "reversal_risk").strip().lower()
        include_btc_spot = self.config.truffle_post_entry_shadow_include_btc_spot or decision_schema == "exit_supervisor"
        btc_context: dict[str, Any] = {}
        if include_btc_spot:
            btc_context = build_btc_spot_context(self.serialize_btc_spot_snapshot())
            if btc_context:
                payload["btc_spot"] = btc_context
        if decision_schema == "exit_supervisor":
            candidate_slice_tags = classify_exit_supervisor_slice_tags(
                side=str(watch.side).strip().upper(),
                pre_entry=payload.get("pre_entry") if isinstance(payload.get("pre_entry"), dict) else {},
                post_entry=payload.get("post_entry") if isinstance(payload.get("post_entry"), dict) else {},
                btc_spot=btc_context,
            )
            exit_payload = build_exit_supervisor_payload(
                base_payload=payload,
                current_exit_bid_cents=current_side_bid_at(
                    history_rows,
                    market_ticker=watch.market_ticker,
                    side=watch.side,
                    as_of_dt=as_of,
                ),
                candidate_slice_tags=candidate_slice_tags,
                btc_spot=btc_context,
                entry_context={
                    "entry_fill_cents": watch.entry_fill_cents,
                    "entry_trigger_cents": watch.entry_trigger_cents,
                    "entry_limit_cents": watch.entry_limit_cents,
                    "seconds_to_close_at_entry": watch.seconds_to_close_at_entry,
                    "entry_origin": watch.entry_origin,
                },
                execution_health={
                    "book_age_ms_at_entry": watch.book_age_ms_at_entry,
                    "eligible_depth_at_entry": watch.eligible_depth_at_entry,
                    "executable_window_ms_at_entry": watch.executable_window_ms_at_entry,
                    "btc_spot_age_ms": self.btc_spot_snapshot_age_ms(),
                },
                recent_market_context={
                    "recent_4_markets": build_recent_market_summary(
                        self.market_outcomes.recent_records(limit=4, exclude_market=watch.market_ticker)
                    ),
                    "recent_8_markets": build_recent_market_summary(
                        self.market_outcomes.recent_records(limit=8, exclude_market=watch.market_ticker)
                    ),
                    "last_4_market_sequence": build_last_market_sequence(
                        self.market_outcomes.recent_records(limit=4, exclude_market=watch.market_ticker)
                    ),
                    "shadow_exit_memory": self.summarize_post_entry_shadow_exit_memory(candidate_slice_tags),
                },
            )
            if self.config.truffle_post_entry_shadow_suspicious_only and not candidate_slice_tags:
                exit_payload["_skip_shadow_reason"] = "not_in_exit_supervisor_suspicious_slice"
            return exit_payload
        return payload

    async def run_post_entry_shadow_after_delay(self, watch: PostEntryShadowWatch) -> None:
        try:
            entry_dt = parse_iso(watch.entry_dt_iso)
            if entry_dt is None:
                return
            elapsed_seconds = max(0.0, (utc_now() - entry_dt).total_seconds())
            delay_seconds = max(0.0, float(self.config.truffle_post_entry_shadow_delay_seconds) - elapsed_seconds)
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)
            if self.shutdown_event.is_set():
                return
            payload = self.build_post_entry_shadow_payload(watch, as_of=utc_now())
            if payload is None:
                self.post_entry_shadow_events.emit(
                    "post_entry_shadow_skipped",
                    market=watch.market_ticker,
                    side=watch.side,
                    reason="missing_market_history",
                    entry_origin=watch.entry_origin,
                )
                return
            skip_reason = str(payload.get("_skip_shadow_reason") or "").strip() if isinstance(payload, dict) else ""
            if skip_reason:
                self.post_entry_shadow_events.emit(
                    "post_entry_shadow_skipped",
                    market=watch.market_ticker,
                    side=watch.side,
                    reason=skip_reason,
                    entry_origin=watch.entry_origin,
                    candidate_slice_tags=payload.get("candidate_slice_tags") if isinstance(payload, dict) else [],
                )
                return
            decision = await asyncio.to_thread(
                issue_truffle_post_entry_shadow,
                payload,
                endpoint=self.resolved_post_entry_shadow_endpoint(),
                model=self.resolved_post_entry_shadow_model(),
                timeout_ms=int(self.config.truffle_post_entry_shadow_timeout_ms),
                prompt_text=self.truffle_post_entry_shadow_prompt_text,
                api_key=self.resolved_post_entry_shadow_api_key(),
                max_tokens=int(self.config.truffle_post_entry_shadow_max_tokens),
                decision_schema=self.config.truffle_post_entry_shadow_decision_schema,
                output_mode=self.config.truffle_post_entry_shadow_output_mode,
                reasoning_enabled=self.config.truffle_post_entry_shadow_reasoning_enabled,
            )
            market_key = normalize_ticker(watch.market_ticker)
            self.post_entry_shadow_decisions[market_key] = decision
            self.post_entry_shadow_events.emit(
                "post_entry_shadow_decision",
                market=watch.market_ticker,
                side=watch.side,
                valid=decision.is_valid,
                green_light=decision.is_green,
                red_light=decision.is_red,
                exit_supervisor_decision=decision.decision,
                effective_exit_supervisor_decision=decision.effective_exit_supervisor_decision,
                exit_now=decision.decision == "EXIT_NOW" and decision.is_valid,
                hold_decision=decision.decision == "HOLD" and decision.is_valid,
                safe_hold_fallback=decision.decision_schema == "exit_supervisor" and not decision.is_valid,
                parse_error=decision.parse_error,
                entry_origin=watch.entry_origin,
                entry_fill_cents=watch.entry_fill_cents,
                entry_trigger_cents=watch.entry_trigger_cents,
                entry_limit_cents=watch.entry_limit_cents,
                seconds_to_close_at_entry=watch.seconds_to_close_at_entry,
                book_age_ms_at_entry=watch.book_age_ms_at_entry,
                eligible_depth_at_entry=watch.eligible_depth_at_entry,
                executable_window_ms_at_entry=watch.executable_window_ms_at_entry,
                decision_schema=self.config.truffle_post_entry_shadow_decision_schema,
                output_mode=self.config.truffle_post_entry_shadow_output_mode,
                candidate_slice_tags=payload.get("candidate_slice_tags") if isinstance(payload, dict) else [],
                decision=decision.to_dict(),
                btc_spot_snapshot_at_entry=watch.btc_spot_snapshot_at_entry,
                btc_spot_snapshot_at_decision=self.serialize_btc_spot_snapshot(),
            )
            if (
                self.config.truffle_post_entry_shadow_live_exit_enabled
                and decision.decision_schema == "exit_supervisor"
                and decision.effective_exit_supervisor_decision == "EXIT_NOW"
                and decision.is_valid
            ):
                await self.maybe_check_exit()
            self.emit_post_entry_shadow_outcome_if_ready(watch.market_ticker)
        finally:
            if self.post_entry_shadow_watch is not None and (
                normalize_ticker(self.post_entry_shadow_watch.market_ticker) == normalize_ticker(watch.market_ticker)
            ):
                self.post_entry_shadow_task = None

    def current_truffle_regime_precheck_status(self) -> str:
        if self.state.pending_order or self.state.position or self.order_inflight:
            return "BLOCK"
        return "PASS"

    def build_truffle_regime_lease_payload(self, next_market_ticker: str, next_market_close: str | None) -> dict[str, Any]:
        close_dt = parse_iso(next_market_close) if next_market_close else None
        local_close_dt = close_dt.astimezone() if close_dt is not None else None
        recent_4 = self.market_outcomes.recent_records(limit=4, exclude_market=next_market_ticker)
        recent_8 = self.market_outcomes.recent_records(limit=8, exclude_market=next_market_ticker)
        return {
            "schema_version": "lease_input_v1",
            "strategy_family": "btc15m_supervisor",
            "candidate_profile_if_allowed": "90_78",
            "configured_profile": f"90_{int(self.config.exit_drop_odds_cents)}",
            "lease_scope": "next_market_only",
            "next_market_ticker": next_market_ticker,
            "next_market_session": infer_session_label(local_close_dt),
            "deterministic_precheck": self.current_truffle_regime_precheck_status(),
            "generated_at": utc_now().isoformat(),
            "recent_4_markets": build_recent_market_summary(recent_4),
            "recent_8_markets": build_recent_market_summary(recent_8),
            "last_4_market_sequence": build_last_market_sequence(recent_4),
        }

    async def issue_truffle_regime_lease_for_market(self, next_market_ticker: str, next_market_close: str | None) -> None:
        if self.config.truffle_regime_lease_mode == "disabled":
            return
        payload = self.build_truffle_regime_lease_payload(next_market_ticker, next_market_close)
        if self.config.truffle_regime_lease_issuer == "stub":
            decision = issue_stub_lease(payload)
        else:
            decision = await asyncio.to_thread(
                issue_truffle_http_lease,
                payload,
                endpoint=self.config.truffle_regime_lease_endpoint,
                model=self.config.truffle_regime_lease_model,
                timeout_ms=self.config.truffle_regime_lease_timeout_ms,
                prompt_text=self.truffle_regime_prompt_text,
                tool_prompt_text=self.truffle_regime_tool_prompt_text,
                api_key=self.config.truffle_regime_lease_api_key,
                max_tokens=self.config.truffle_regime_lease_max_tokens,
                reasoning_enabled=self.config.truffle_regime_lease_reasoning_enabled,
            )
        self.current_regime_lease = decision
        if decision.is_valid:
            self.lease_cache_store.save(decision)
        self.lease_events.emit(
            "lease_issued",
            mode=self.config.truffle_regime_lease_mode,
            issuer=self.config.truffle_regime_lease_issuer,
            market=next_market_ticker,
            decision=decision.decision,
            valid=decision.is_valid,
            parse_error=decision.parse_error,
            candidate_profile_if_allowed=decision.candidate_profile_if_allowed,
            confidence=decision.confidence,
            rationale_code=decision.rationale_code,
            summary_reason=decision.summary_reason,
            input_payload=payload,
            raw_response=decision.raw_response,
        )

    def evaluate_truffle_regime_lease(self, signal: EntrySignal) -> FilterDecision:
        mode = self.config.truffle_regime_lease_mode
        if mode == "disabled":
            return FilterDecision(True, "truffle_regime_lease_disabled")
        decision = self.current_regime_lease or self.lease_cache_store.load()
        self.current_regime_lease = decision
        if decision is None:
            self.lease_events.emit(
                "lease_cache_miss",
                mode=mode,
                market=signal.market_ticker,
                side=signal.side,
                trigger_price_cents=signal.trigger_price_cents,
            )
            if mode == "enforce_entries_only" and self.config.truffle_regime_lease_fail_closed:
                return FilterDecision(False, "truffle_regime_lease_cache_miss")
            return FilterDecision(True, "truffle_regime_lease_cache_miss_shadow")
        if not decision.is_valid:
            self.lease_events.emit(
                "lease_invalid",
                mode=mode,
                market=signal.market_ticker,
                side=signal.side,
                parse_error=decision.parse_error,
                raw_response=decision.raw_response,
            )
            if mode == "enforce_entries_only" and self.config.truffle_regime_lease_fail_closed:
                return FilterDecision(False, "truffle_regime_lease_invalid")
            return FilterDecision(True, "truffle_regime_lease_invalid_shadow")
        if decision.valid_for_market_ticker != signal.market_ticker:
            self.lease_events.emit(
                "lease_market_mismatch",
                mode=mode,
                market=signal.market_ticker,
                side=signal.side,
                lease_market=decision.valid_for_market_ticker,
                lease_decision=decision.decision,
            )
            if mode == "enforce_entries_only" and self.config.truffle_regime_lease_fail_closed:
                return FilterDecision(False, "truffle_regime_lease_market_mismatch")
            return FilterDecision(True, "truffle_regime_lease_market_mismatch_shadow")
        if lease_is_stale(decision, max_staleness_seconds=self.config.truffle_regime_lease_max_staleness_seconds):
            self.lease_events.emit(
                "lease_stale",
                mode=mode,
                market=signal.market_ticker,
                side=signal.side,
                lease_decision=decision.decision,
                issued_at=decision.issued_at,
            )
            if mode == "enforce_entries_only" and self.config.truffle_regime_lease_fail_closed:
                return FilterDecision(False, "truffle_regime_lease_stale")
            return FilterDecision(True, "truffle_regime_lease_stale_shadow")
        if decision.decision == BLOCK_NEXT_MARKET:
            self.lease_events.emit(
                "lease_shadow_block" if mode == "shadow_only" else "lease_enforced_block",
                mode=mode,
                market=signal.market_ticker,
                side=signal.side,
                lease_decision=decision.decision,
                trigger_price_cents=signal.trigger_price_cents,
                rationale_code=decision.rationale_code,
                summary_reason=decision.summary_reason,
            )
            if mode == "enforce_entries_only":
                return FilterDecision(False, "truffle_regime_lease_blocked")
            return FilterDecision(True, "truffle_regime_lease_shadow_block")
        if decision.decision == ALLOW_90_78_NEXT_MARKET and int(self.config.exit_drop_odds_cents) != 78:
            self.lease_events.emit(
                "lease_profile_mismatch",
                mode=mode,
                market=signal.market_ticker,
                side=signal.side,
                lease_decision=decision.decision,
                configured_profile=f"90_{int(self.config.exit_drop_odds_cents)}",
            )
            if mode == "enforce_entries_only" and self.config.truffle_regime_lease_fail_closed:
                return FilterDecision(False, "truffle_regime_lease_profile_mismatch")
        return FilterDecision(True, "truffle_regime_lease_allowed")

    def _request_shutdown(self, reason: str) -> None:
        if self.shutdown_event.is_set():
            return
        self.shutdown_reason = reason
        self.logger.warning("Shutdown requested | reason=%s run_id=%s", reason, self.config.run_id)
        self.shutdown_event.set()

    def _handle_signal(self, signame: str = "signal") -> None:
        self._request_shutdown(f"signal:{signame}")

    async def run(self) -> None:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            with contextlib.suppress(NotImplementedError):
                signame = signal.Signals(sig).name
                loop.add_signal_handler(sig, lambda signame=signame: self._handle_signal(signame))

        self.logger.info(
            "Starting WS bot. run_id=%s dry_run=%s base_url=%s ws_url=%s series=%s",
            self.config.run_id,
            self.config.dry_run,
            self.config.base_url,
            self.config.ws_url,
            self.config.series_ticker,
        )
        try:
            self.acquire_live_lock_if_needed()
            await self.bootstrap_safety_check()
            await self.ensure_account_state_task()
            await self.ensure_btc_regime_task()
            await self.ensure_mushroom_v28_btc_tick_task()
            self.last_loop_monotonic = time.monotonic()
            while not self.shutdown_event.is_set():
                try:
                    now_mono = time.monotonic()
                    loop_gap_seconds = now_mono - self.last_loop_monotonic
                    if loop_gap_seconds > self.max_loop_gap_seconds:
                        self.logger.warning(
                            "Loop gap detected | gap_seconds=%.2f threshold_seconds=%.2f watch=%s trust=%s run_id=%s",
                            loop_gap_seconds,
                            self.max_loop_gap_seconds,
                            self.current_watch_ticker,
                            self.orderbook.trust.trust_state,
                            self.config.run_id,
                        )
                    self.last_loop_monotonic = now_mono
                    await self.maybe_refresh_watch_market()
                    await self.ensure_ws_task()
                    await self.ensure_mushroom_v28_btc_tick_task()
                    await self.maybe_check_pending_order()
                    await self.maybe_check_entry()
                    await self.maybe_check_exit()
                    self.maybe_log_heartbeat()
                    await asyncio.sleep(self.config.decision_loop_seconds)
                except Exception as exc:  # noqa: BLE001
                    self.logger.exception(
                        "Main loop recoverable error | watch=%s trust=%s run_id=%s error=%s",
                        self.current_watch_ticker,
                        self.orderbook.trust.trust_state,
                        self.config.run_id,
                        exc,
                    )
                    await asyncio.sleep(max(self.config.decision_loop_seconds, 0.25))
            if self.shutdown_reason == "not_requested":
                self.shutdown_reason = "event_set_without_reason"
        finally:
            await self.stop_post_entry_shadow_task()
            await self.stop_account_state_task()
            await self.stop_mushroom_v28_btc_tick_task()
            await self.stop_btc_regime_task()
            await self.stop_ws_task()
            self.release_live_lock_if_needed()
            self.logger.info("Bot stopped. run_id=%s reason=%s", self.config.run_id, self.shutdown_reason)

    async def bootstrap_safety_check(self) -> None:
        if self.config.dry_run and (self.state.position or self.state.pending_order):
            self.logger.warning(
                "Clearing persisted dry run state on startup so the bot can resume on the current market."
            )
            self.state.position = None
            self.state.pending_order = None
            self.save_state()
            return

        if self.state.position:
            self.logger.warning(
                "Recovered persisted position state for %s side=%s qty=%s. The bot will stay on this market; same-side adds are allowed only if the multi-entry gate is enabled and still within limits.",
                self.state.position.market_ticker,
                self.state.position.side,
                self.state.position.count,
            )
            self.backfill_persisted_position_outcome()
        if self.state.pending_order:
            self.logger.warning(
                "Recovered persisted pending order %s for %s. The bot will resolve it before doing anything else.",
                self.state.pending_order.order_id,
                self.state.pending_order.market_ticker,
            )
        if not self.config.dry_run:
            with contextlib.suppress(Exception):
                live_positions = self.client.get_positions()
                nonzero = []
                for pos in live_positions:
                    qty = to_decimal(pos.get("position_fp", pos.get("position", 0)))
                    if qty != 0:
                        nonzero.append(pos)
                if self.state.position is not None:
                    persisted_ticker = normalize_ticker(self.state.position.market_ticker)
                    matching_live = []
                    for pos in nonzero:
                        live_ticker = normalize_ticker(str(pos.get("ticker") or pos.get("market_ticker") or ""))
                        if live_ticker == persisted_ticker:
                            matching_live.append(pos)
                    if not matching_live:
                        self.logger.warning(
                            "Clearing persisted live position state for %s because no matching live account position was found. It was likely settled or closed while the bot was offline.",
                            self.state.position.market_ticker,
                        )
                        stale_ticker = self.state.position.market_ticker
                        self.state.position = None
                        self.state.pending_order = None
                        self.save_state()
                        await self.maybe_finalize_market_outcome_from_exchange(stale_ticker)
                    elif self.live_position_is_settlement_only(self.state.position.market_ticker):
                        self.logger.warning(
                            "Clearing persisted live position state for %s because the market is already closed and only settlement remains. The bot will advance to the next market.",
                            self.state.position.market_ticker,
                        )
                        stale_ticker = self.state.position.market_ticker
                        self.state.position = None
                        self.state.pending_order = None
                        self.save_state()
                        await self.maybe_finalize_market_outcome_from_exchange(stale_ticker)
                if nonzero:
                    self.logger.warning(
                        "Live account has %s nonzero position entries. Review carefully before using live mode.",
                        len(nonzero),
                    )
            with contextlib.suppress(Exception):
                await self.maybe_refresh_live_account_state(force=True)

    async def ensure_account_state_task(self) -> None:
        if self.config.dry_run:
            return
        if self.account_state_task is None or self.account_state_task.done():
            self.account_state_task = asyncio.create_task(self.account_state_loop())

    async def stop_account_state_task(self) -> None:
        if self.account_state_task:
            self.account_state_task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await self.account_state_task
            self.account_state_task = None

    async def stop_post_entry_shadow_task(self) -> None:
        if self.post_entry_shadow_task:
            self.post_entry_shadow_task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await self.post_entry_shadow_task
            self.post_entry_shadow_task = None

    async def ensure_btc_regime_task(self) -> None:
        if not self.should_run_btc_background_task():
            return
        if self.btc_regime_task is None or self.btc_regime_task.done():
            self.btc_regime_task = asyncio.create_task(self.btc_regime_loop())

    async def stop_btc_regime_task(self) -> None:
        if self.btc_regime_task:
            self.btc_regime_task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await self.btc_regime_task
            self.btc_regime_task = None

    def mushroom_v28_configured(self) -> bool:
        return bool(
            self.config.mushroom_v28_shadow_enabled
            or self.config.mushroom_v28_decision_engine_enabled
            or self.config.mushroom_v28_live_exit_enabled
        )

    def build_mushroom_v28_worker(self) -> MushroomV28LiveFVWorker:
        config = MushroomV28Config()
        engine = MushroomV28Engine(config)
        return MushroomV28LiveFVWorker(
            engine=engine,
            max_book_age_ms=max(
                float(self.config.live_entry_base_book_age_ms),
                float(self.config.live_entry_final_minute_book_age_ms),
                float(self.config.live_entry_final_seconds_book_age_ms),
            ),
            min_edge_15m_cents=float(self.config.mushroom_v28_min_edge_cents_15m),
        )

    async def ensure_mushroom_v28_btc_tick_task(self) -> None:
        if (
            self.mushroom_v28_worker is None
            or not self.config.mushroom_v28_btc_ws_enabled
            or not self.mushroom_v28_configured()
        ):
            return
        if self.mushroom_v28_btc_tick_task is None or self.mushroom_v28_btc_tick_task.done():
            self.mushroom_v28_btc_tick_task = asyncio.create_task(self.mushroom_v28_btc_tick_loop())

    async def stop_mushroom_v28_btc_tick_task(self) -> None:
        if self.mushroom_v28_btc_tick_task:
            self.mushroom_v28_btc_tick_task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await self.mushroom_v28_btc_tick_task
            self.mushroom_v28_btc_tick_task = None

    async def mushroom_v28_btc_tick_loop(self) -> None:
        endpoints = [
            str(self.config.mushroom_v28_btc_ws_url or COINBASE_BTC_TICKER_WS_URL),
            *[str(url) for url in self.config.mushroom_v28_btc_ws_fallback_urls if str(url).strip()],
        ]
        endpoints = list(dict.fromkeys([url.strip() for url in endpoints if url.strip()]))
        if not endpoints:
            endpoints = [COINBASE_BTC_TICKER_WS_URL]
        reconnect_seconds = max(0.25, float(self.config.websocket_reconnect_seconds))
        endpoint_index = 0
        while not self.shutdown_event.is_set():
            url = endpoints[endpoint_index % len(endpoints)]
            source = self.mushroom_v28_btc_ws_source(url)
            try:
                async with websockets.connect(
                    url,
                    ping_interval=20,
                    ping_timeout=20,
                    close_timeout=5,
                    max_queue=16,
                ) as ws:
                    await self.subscribe_mushroom_v28_btc_ws(ws, source=source)
                    self.logger.info("Mushroom v28 BTC tick stream connected | source=%s url=%s", source, url)
                    async for raw in ws:
                        if self.shutdown_event.is_set():
                            return
                        self.handle_mushroom_v28_btc_ws_message(raw, source=source)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                self.mushroom_v28_last_error = str(exc)
                self.logger.warning("Mushroom v28 BTC tick stream failed. reconnect_seconds=%.2f error=%s", reconnect_seconds, exc)
                endpoint_index += 1
                await asyncio.sleep(reconnect_seconds)

    @staticmethod
    def mushroom_v28_btc_ws_source(url: str) -> str:
        lowered = str(url or "").lower()
        if "coinbase" in lowered:
            return "coinbase"
        if "binance" in lowered and "bookticker" in lowered:
            return "binance_book_ticker"
        if "binance" in lowered:
            return "binance_trade"
        return "websocket"

    async def subscribe_mushroom_v28_btc_ws(self, ws: Any, *, source: str) -> None:
        if source != "coinbase":
            return
        await ws.send(
            json.dumps(
                {
                    "type": "subscribe",
                    "product_ids": ["BTC-USD"],
                    "channels": ["ticker"],
                }
            )
        )

    @staticmethod
    def mushroom_v28_parse_btc_ts(ts_raw: Any) -> datetime | float | int | None:
        if ts_raw is None:
            return utc_now()
        if isinstance(ts_raw, datetime):
            return ts_raw if ts_raw.tzinfo else ts_raw.replace(tzinfo=timezone.utc)
        if isinstance(ts_raw, (int, float)):
            ts_float = float(ts_raw)
            return datetime.fromtimestamp(ts_float / 1000.0, tz=timezone.utc) if ts_float > 1_000_000_000_000 else ts_float
        text = str(ts_raw).strip()
        if not text:
            return utc_now()
        if text.endswith("Z"):
            text = f"{text[:-1]}+00:00"
        with contextlib.suppress(ValueError):
            parsed = datetime.fromisoformat(text)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        with contextlib.suppress(TypeError, ValueError):
            ts_float = float(text)
            return datetime.fromtimestamp(ts_float / 1000.0, tz=timezone.utc) if ts_float > 1_000_000_000_000 else ts_float
        return utc_now()

    def handle_mushroom_v28_btc_ws_message(self, raw: Any, *, source: str = "websocket") -> None:
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
            payload = data.get("data", data) if isinstance(data, dict) else {}
            if not isinstance(payload, dict):
                return
            if source == "coinbase" and payload.get("type") != "ticker":
                return
            price_raw = payload.get("p") or payload.get("price") or payload.get("c")
            if price_raw is None:
                bid_raw = payload.get("b") or payload.get("best_bid")
                ask_raw = payload.get("a") or payload.get("best_ask")
                if bid_raw is not None and ask_raw is not None:
                    price_raw = (float(bid_raw) + float(ask_raw)) / 2.0
            qty_raw = payload.get("q") or payload.get("quantity") or payload.get("last_size") or 0.0
            ts_raw = payload.get("T") or payload.get("E") or payload.get("time")
            price = float(price_raw)
            volume = float(qty_raw or 0.0)
            ts = self.mushroom_v28_parse_btc_ts(ts_raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            return
        self.update_mushroom_v28_btc_tick(price, ts=ts, volume=volume, source=source)

    async def btc_regime_loop(self) -> None:
        while not self.shutdown_event.is_set():
            try:
                vol_snapshot, spot_snapshot = await asyncio.to_thread(self.fetch_btc_market_context)
                self.btc_vol_regime_snapshot = vol_snapshot
                self.btc_spot_snapshot = spot_snapshot
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                self.btc_vol_regime_snapshot.error = str(exc)
                self.btc_spot_snapshot.error = str(exc)
                self.logger.warning("BTC market context refresh failed. error=%s", exc)
            await asyncio.sleep(max(1.0, float(self.config.btc_vol_regime_poll_seconds)))

    def should_run_btc_background_task(self) -> bool:
        return bool(
            self.config.btc_vol_regime_gate_enabled
            or self.config.mushroom_shadow_enabled
            or self.config.mushroom_v21_decision_engine_enabled
            or self.mushroom_v28_configured()
            or self.config.truffle_post_entry_shadow_enabled
            or self.config.truffle_post_entry_shadow_include_btc_spot
        )

    def mushroom_history_count(self) -> int:
        if self.mushroom_forecaster is None:
            return 0
        with self.mushroom_lock:
            return len(self.mushroom_forecaster.history)

    def mushroom_v21_history_count(self) -> int:
        if self.mushroom_v21_forecaster is None:
            return 0
        with self.mushroom_lock:
            return len(self.mushroom_v21_forecaster.history)

    def mushroom_v28_history_count(self) -> int:
        if self.mushroom_v28_worker is None:
            return 0
        with self.mushroom_lock:
            return int(getattr(self.mushroom_v28_worker.engine, "count", 0) or 0)

    def mushroom_v28_ready(self) -> bool:
        if self.mushroom_v28_worker is None:
            return False
        with self.mushroom_lock:
            return bool(self.mushroom_v28_worker.engine.ready())

    def update_mushroom_v28_btc_tick(
        self,
        price: float,
        *,
        ts: datetime | float | int | None = None,
        volume: float = 0.0,
        source: str = "",
    ) -> bool:
        if self.mushroom_v28_worker is None:
            return False
        try:
            with self.mushroom_lock:
                committed = bool(self.mushroom_v28_worker.update_btc_tick(price=price, ts=ts, volume=volume))
        except Exception as exc:  # noqa: BLE001
            self.mushroom_v28_last_error = str(exc)
            return False
        self.mushroom_v28_last_tick_monotonic = time.monotonic()
        self.mushroom_v28_last_tick_price = float(price)
        self.mushroom_v28_last_tick_source = source or "unknown"
        if isinstance(ts, datetime):
            self.mushroom_v28_last_tick_ts = ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
        elif ts is None:
            self.mushroom_v28_last_tick_ts = utc_now()
        else:
            with contextlib.suppress(TypeError, ValueError, OSError):
                self.mushroom_v28_last_tick_ts = datetime.fromtimestamp(float(ts), tz=timezone.utc)
        self.mushroom_v28_last_error = ""
        if committed:
            self.logger.debug("Mushroom v28 committed BTC minute bar | source=%s price=%.2f bars=%s", source, float(price), self.mushroom_v28_history_count())
        return committed

    def mushroom_v28_btc_age_ms(self) -> float | None:
        if self.mushroom_v28_last_tick_monotonic > 0:
            return max(0.0, (time.monotonic() - self.mushroom_v28_last_tick_monotonic) * 1000.0)
        return None

    def mushroom_needs_history_bootstrap(self) -> bool:
        if self.mushroom_forecaster is None and self.mushroom_v21_forecaster is None and self.mushroom_v28_worker is None:
            return False
        target = max(
            MushroomConfig().min_history_points,
            int(self.config.mushroom_btc_history_minutes),
        )
        if self.mushroom_forecaster is not None and self.mushroom_history_count() < min(
            target,
            self.mushroom_forecaster.config.max_history,
        ):
            return True
        if self.mushroom_v21_forecaster is not None and self.mushroom_v21_history_count() < min(
            target,
            self.mushroom_v21_forecaster.config.max_history,
        ):
            return True
        if self.mushroom_v28_worker is not None:
            engine = self.mushroom_v28_worker.engine
            v28_target = max(int(MushroomV28Config().min_bars), min(target, int(MushroomV28Config().max_bars)))
            if self.mushroom_v28_history_count() < min(v28_target, int(getattr(engine.config, "max_bars", v28_target))):
                return True
        return False

    def fetch_binance_klines(
        self,
        *,
        symbol: str,
        interval: str,
        start_utc: datetime,
        limit: int,
    ) -> list[list[Any]]:
        interval_minutes_map = {"1m": 1, "5m": 5, "15m": 15}
        interval_minutes = interval_minutes_map.get(interval, 1)
        interval_ms = interval_minutes * 60 * 1000
        remaining = max(1, int(limit))
        start_ms = int(start_utc.timestamp() * 1000)
        rows: list[list[Any]] = []
        while remaining > 0:
            page_limit = min(1000, remaining)
            resp = requests.get(
                "https://data-api.binance.vision/api/v3/klines",
                params={
                    "symbol": symbol,
                    "interval": interval,
                    "startTime": start_ms,
                    "limit": page_limit,
                },
                timeout=min(12.0, max(2.0, float(self.config.http_timeout_seconds))),
            )
            resp.raise_for_status()
            page = resp.json()
            if not isinstance(page, list) or not page:
                break
            rows.extend(page)
            remaining -= len(page)
            if len(page) < page_limit:
                break
            try:
                start_ms = int(page[-1][0]) + interval_ms
            except (TypeError, ValueError, IndexError):
                break
        return rows

    def update_mushroom_from_binance_klines(self, raw: list[Any]) -> None:
        if self.mushroom_forecaster is None and self.mushroom_v21_forecaster is None and self.mushroom_v28_worker is None:
            return
        now = utc_now()
        added = 0
        with self.mushroom_lock:
            for item in raw:
                if not isinstance(item, (list, tuple)) or len(item) < 7:
                    continue
                try:
                    close_ms = int(item[6])
                    close_ts = datetime.fromtimestamp(close_ms / 1000.0, tz=timezone.utc)
                    if close_ts > now - timedelta(seconds=1):
                        continue
                    if close_ms in self.mushroom_seen_bar_close_set:
                        continue
                    op = float(item[1])
                    hi = float(item[2])
                    lo = float(item[3])
                    close = float(item[4])
                    volume = float(item[5])
                except (TypeError, ValueError):
                    continue
                if self.mushroom_seen_bar_closes.maxlen and len(self.mushroom_seen_bar_closes) >= self.mushroom_seen_bar_closes.maxlen:
                    old = self.mushroom_seen_bar_closes.popleft()
                    self.mushroom_seen_bar_close_set.discard(old)
                if self.mushroom_forecaster is not None:
                    self.mushroom_forecaster.update_bar(
                        open=op,
                        high=hi,
                        low=lo,
                        close=close,
                        volume=volume,
                        ts=close_ts,
                    )
                if self.mushroom_v21_forecaster is not None:
                    self.mushroom_v21_forecaster.update_bar(
                        open=op,
                        high=hi,
                        low=lo,
                        close=close,
                        volume=volume,
                        ts=close_ts,
                    )
                if self.mushroom_v28_worker is not None:
                    self.mushroom_v28_worker.update_btc_bar(
                        open=op,
                        high=hi,
                        low=lo,
                        close=close,
                        volume=volume,
                        ts=close_ts,
                    )
                self.mushroom_seen_bar_closes.append(close_ms)
                self.mushroom_seen_bar_close_set.add(close_ms)
                added += 1
        if added:
            count = max(self.mushroom_history_count(), self.mushroom_v21_history_count(), self.mushroom_v28_history_count())
            key = f"mushroom-bars:{count // 100}"
            min_required = min(MushroomConfig().min_history_points, MushroomV28Config().min_bars)
            if key != self.last_mushroom_shadow_log_key and count < min_required:
                self.last_mushroom_shadow_log_key = key
                self.logger.info("Mushroom warming | bars=%s min_required=%s", count, min_required)

    def fetch_btc_market_context(self) -> tuple[BTCVolatilityRegimeSnapshot, BTCSpotFeatureSnapshot]:
        interval = str(self.config.btc_vol_regime_interval).strip().lower() or "5m"
        interval_minutes_map = {"1m": 1, "5m": 5, "15m": 15}
        interval_minutes = interval_minutes_map.get(interval, 5)
        lookback_minutes = max(15, int(self.config.btc_vol_regime_lookback_minutes))
        vol_start_utc = utc_now() - timedelta(minutes=lookback_minutes + interval_minutes)
        vol_resp = requests.get(
            "https://data-api.binance.vision/api/v3/klines",
            params={
                "symbol": "BTCUSDT",
                "interval": interval,
                "startTime": int(vol_start_utc.timestamp() * 1000),
                "limit": max(8, int((lookback_minutes / max(interval_minutes, 1)) + 4)),
            },
            timeout=min(12.0, max(2.0, float(self.config.http_timeout_seconds))),
        )
        vol_resp.raise_for_status()
        vol_raw = vol_resp.json()
        if not isinstance(vol_raw, list) or not vol_raw:
            raise RuntimeError("Binance returned no BTC candles for volatility snapshot")
        vol_cutoff = utc_now() - timedelta(minutes=lookback_minutes)
        vol_highs: list[float] = []
        vol_lows: list[float] = []
        for item in vol_raw:
            close_ts = datetime.fromtimestamp(int(item[6]) / 1000.0, tz=timezone.utc)
            if close_ts < vol_cutoff:
                continue
            vol_highs.append(float(item[2]))
            vol_lows.append(float(item[3]))
        if not vol_highs or not vol_lows:
            raise RuntimeError("No fresh BTC candles inside volatility lookback window")
        spot_history_minutes = max(60, lookback_minutes + 30)
        if self.mushroom_needs_history_bootstrap():
            spot_history_minutes = max(spot_history_minutes, int(self.config.mushroom_btc_history_minutes))
        spot_start_utc = utc_now() - timedelta(minutes=spot_history_minutes + 5)
        raw = self.fetch_binance_klines(
            symbol="BTCUSDT",
            interval="1m",
            start_utc=spot_start_utc,
            limit=max(80, int(spot_history_minutes + 8)),
        )
        if not isinstance(raw, list) or not raw:
            raise RuntimeError("Binance returned no BTC candles for spot snapshot")
        self.update_mushroom_from_binance_klines(raw)
        cutoff = utc_now() - timedelta(minutes=lookback_minutes)
        highs: list[float] = []
        lows: list[float] = []
        closes: list[float] = []
        technical_closes: list[float] = []
        for item in raw:
            close_ts = datetime.fromtimestamp(int(item[6]) / 1000.0, tz=timezone.utc)
            technical_closes.append(float(item[4]))
            if close_ts < cutoff:
                continue
            highs.append(float(item[2]))
            lows.append(float(item[3]))
            closes.append(float(item[4]))
        if not highs or not lows or not closes:
            raise RuntimeError("No fresh BTC candles inside lookback window")
        last_price = float(closes[-1])
        price_1m_ago = float(closes[-2]) if len(closes) >= 2 else last_price
        price_5m_ago = float(closes[-6]) if len(closes) >= 6 else float(closes[0])
        price_15m_ago = float(closes[0])
        high_15m = max(highs)
        low_15m = min(lows)
        range_15m_dollars = high_15m - low_15m
        vol_range_dollars = max(vol_highs) - min(vol_lows)
        technicals = compute_btc_live_technicals(technical_closes)
        fetched_at_monotonic = time.monotonic()
        source = "Binance public market data"
        return (
            BTCVolatilityRegimeSnapshot(
                range_dollars=vol_range_dollars,
                source=source,
                fetched_at_monotonic=fetched_at_monotonic,
                lookback_minutes=lookback_minutes,
                interval=interval,
                error="",
            ),
            BTCSpotFeatureSnapshot(
                last_price=last_price,
                move_1m_bps=((last_price - price_1m_ago) / max(price_1m_ago, 1e-9)) * 10000.0,
                move_5m_bps=((last_price - price_5m_ago) / max(price_5m_ago, 1e-9)) * 10000.0,
                move_15m_bps=((last_price - price_15m_ago) / max(price_15m_ago, 1e-9)) * 10000.0,
                range_15m_dollars=range_15m_dollars,
                range_15m_bps=(range_15m_dollars / max(last_price, 1e-9)) * 10000.0,
                distance_to_15m_high_bps=((high_15m - last_price) / max(last_price, 1e-9)) * 10000.0,
                distance_to_15m_low_bps=((last_price - low_15m) / max(last_price, 1e-9)) * 10000.0,
                rsi14=technicals.get("rsi14") if isinstance(technicals.get("rsi14"), (int, float)) else None,
                rsi14_state=str(technicals.get("rsi14_state") or ""),
                rsi14_slope_state=str(technicals.get("rsi14_slope_state") or ""),
                macd_line=technicals.get("macd_line") if isinstance(technicals.get("macd_line"), (int, float)) else None,
                macd_signal=technicals.get("macd_signal") if isinstance(technicals.get("macd_signal"), (int, float)) else None,
                macd_hist=technicals.get("macd_hist") if isinstance(technicals.get("macd_hist"), (int, float)) else None,
                macd_state=str(technicals.get("macd_state") or ""),
                macd_hist_state=str(technicals.get("macd_hist_state") or ""),
                price_vs_ema21=technicals.get("price_vs_ema21") if isinstance(technicals.get("price_vs_ema21"), (int, float)) else None,
                price_vs_ema21_state=str(technicals.get("price_vs_ema21_state") or ""),
                source=source,
                fetched_at_monotonic=fetched_at_monotonic,
                error="",
            ),
        )

    def fetch_btc_vol_regime_snapshot(self) -> BTCVolatilityRegimeSnapshot:
        snapshot, _ = self.fetch_btc_market_context()
        return snapshot

    def btc_vol_regime_age_ms(self) -> float | None:
        fetched = self.btc_vol_regime_snapshot.fetched_at_monotonic
        if fetched is None:
            return None
        return (time.monotonic() - fetched) * 1000.0

    def btc_spot_snapshot_age_ms(self) -> float | None:
        fetched = self.btc_spot_snapshot.fetched_at_monotonic
        if fetched is None:
            return None
        return (time.monotonic() - fetched) * 1000.0

    def evaluate_btc_vol_regime_gate(self, signal: EntrySignal) -> FilterDecision:
        if not self.config.btc_vol_regime_gate_enabled:
            return FilterDecision(True, "btc_vol_regime_disabled")
        snapshot = self.btc_vol_regime_snapshot
        age_ms = self.btc_vol_regime_age_ms()
        max_age_ms = float(self.config.btc_vol_regime_max_age_ms)
        if snapshot.range_dollars is None or age_ms is None or age_ms > max_age_ms:
            reason = "btc_vol_regime_unavailable" if snapshot.range_dollars is None else "btc_vol_regime_stale"
            if self.config.btc_vol_regime_fail_open:
                self.log_filter_decision(
                    f"btc-regime-open:{reason}",
                    "BTC volatility regime gate fail-open | reason=%s age_ms=%s source=%s error=%s",
                    reason,
                    f"{age_ms:.1f}" if age_ms is not None else "NA",
                    snapshot.source or "NA",
                    snapshot.error or "",
                )
                return FilterDecision(True, reason)
            self.note_entry_skip(
                signal.market_ticker,
                signal.side,
                reason,
                f"btc-regime:{reason}:{int(age_ms or -1)}",
                1.0,
                "Entry blocked by BTC volatility regime gate | market=%s side=%s reason=%s age_ms=%s source=%s error=%s",
                signal.market_ticker,
                signal.side,
                reason,
                f"{age_ms:.1f}" if age_ms is not None else "NA",
                snapshot.source or "NA",
                snapshot.error or "",
            )
            self.transition_execution_state(signal.market_ticker, signal.side, "blocked_filter", reason, signal.signal_signature)
            return FilterDecision(False, reason)
        threshold = float(self.config.btc_vol_regime_max_range_dollars)
        if float(snapshot.range_dollars) >= threshold:
            self.note_entry_skip(
                signal.market_ticker,
                signal.side,
                "btc_vol_regime_blocked",
                f"btc-regime:block:{int(snapshot.range_dollars)}:{int(threshold)}",
                1.0,
                "Entry blocked by BTC volatility regime gate | market=%s side=%s btc_range=$%.2f threshold=$%.2f age_ms=%.1f source=%s",
                signal.market_ticker,
                signal.side,
                float(snapshot.range_dollars),
                threshold,
                float(age_ms),
                snapshot.source or "NA",
            )
            self.transition_execution_state(signal.market_ticker, signal.side, "blocked_filter", "btc_vol_regime_blocked", signal.signal_signature)
            return FilterDecision(False, "btc_vol_regime_blocked")
        return FilterDecision(True, "btc_vol_regime_pass")

    async def account_state_loop(self) -> None:
        while not self.shutdown_event.is_set():
            try:
                await self.maybe_refresh_live_account_state(force=False)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                self.logger.warning("Background account state refresh failed: %s", exc)
            await asyncio.sleep(self.config.live_account_state_poll_seconds)

    def acquire_live_lock_if_needed(self) -> None:
        if self.config.dry_run or self.live_lock_acquired:
            return
        self.config.live_lock_path.parent.mkdir(parents=True, exist_ok=True)
        existing = read_live_lock(self.config.live_lock_path)
        if existing:
            existing_pid = safe_int(existing.get("pid"))
            existing_strategy = str(existing.get("strategy_tag") or "")
            if existing_pid and pid_is_running(existing_pid) and existing_pid != os.getpid():
                raise ValueError(
                    f"Live trading lock already held by pid={existing_pid} strategy={existing_strategy or 'unknown'}"
                )
        payload = {
            "pid": os.getpid(),
            "strategy_tag": self.config.strategy_tag,
            "run_id": self.config.run_id,
            "acquired_at": utc_now().isoformat(),
        }
        self.config.live_lock_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.live_lock_acquired = True

    def release_live_lock_if_needed(self) -> None:
        if self.config.dry_run or not self.live_lock_acquired:
            return
        existing = read_live_lock(self.config.live_lock_path)
        existing_pid = safe_int(existing.get("pid")) if existing else None
        if existing_pid == os.getpid():
            with contextlib.suppress(FileNotFoundError):
                self.config.live_lock_path.unlink()
        self.live_lock_acquired = False

    async def maybe_refresh_watch_market(self) -> None:
        now_mono = time.monotonic()

        if self.config.dry_run and self.state.position and self.current_watch_ticker == self.state.position.market_ticker:
            close_dt = parse_iso(self.watch_close_time) if self.watch_close_time else None
            if close_dt and utc_now() >= close_dt + timedelta(seconds=5):
                closing_market = self.state.position.market_ticker
                self.logger.info(
                    "Dry run market %s is closed. Clearing dry run position state and advancing to the next market.",
                    closing_market,
                )
                self.state.position = None
                self.state.pending_order = None
                self.state.exit_confirmation = None
                self.save_state()
                await self.maybe_finalize_market_outcome_from_exchange(closing_market)
                self.current_watch_ticker = None
                self.watch_close_time = None
                self.orderbook.reset(None)
                self.market = MarketSnapshot()

        if (not self.config.dry_run) and self.state.position and self.current_watch_ticker == self.state.position.market_ticker:
            close_dt = parse_iso(self.watch_close_time) if self.watch_close_time else None
            if close_dt and utc_now() >= close_dt + timedelta(seconds=5):
                closing_market = self.state.position.market_ticker
                if await self.reconcile_live_position_after_close(closing_market):
                    await self.maybe_finalize_market_outcome_from_exchange(closing_market)
                    self.current_watch_ticker = None
                    self.watch_close_time = None
                    self.orderbook.reset(None)
                    self.market = MarketSnapshot()

        if self.state.pending_order:
            desired_ticker = self.state.pending_order.market_ticker
            desired_close = None
            desired_strike = self.market.strike
        elif self.state.position:
            desired_ticker = self.state.position.market_ticker
            desired_close = self.watch_close_time or self.persisted_market_close_time(desired_ticker)
            desired_strike = self.market.strike
        else:
            refresh_interval = self.config.active_market_refresh_seconds if self.current_watch_ticker else self.config.active_market_retry_seconds
            if now_mono - self.last_market_refresh_monotonic < refresh_interval:
                return
            try:
                market = await asyncio.to_thread(self.client.get_active_btc15m_market)
            except Exception as exc:
                self.last_market_refresh_monotonic = now_mono
                self.logger.warning("Market refresh failed. Keeping current watch. Error: %s", exc)
                return
            self.last_market_refresh_monotonic = now_mono
            if not market:
                if self.current_watch_ticker is not None:
                    await self.maybe_finalize_market_outcome_from_exchange(self.current_watch_ticker)
                    self.logger.warning("No active BTC 15m market found from REST discovery. Waiting.")
                    self.current_watch_ticker = None
                    self.watch_close_time = None
                    self.orderbook.reset(None)
                    self.market = MarketSnapshot()
                    await self.stop_ws_task()
                return
            desired_ticker = str(market.get("ticker"))
            desired_close = str(market.get("close_time") or "")
            desired_strike = parse_btc_strike_from_market(market)
            if desired_strike is None:
                with contextlib.suppress(Exception):
                    full_market = await asyncio.to_thread(self.client.get_market, desired_ticker)
                    desired_strike = parse_btc_strike_from_market(full_market)
            if self.current_watch_ticker != desired_ticker:
                if desired_strike is None:
                    with contextlib.suppress(Exception):
                        full_market = await asyncio.to_thread(self.client.get_market, desired_ticker)
                        desired_strike = parse_btc_strike_from_market(full_market)
                self.logger.info(
                    "Watching market %s close_time=%s status=%s strike=%s run_id=%s",
                    desired_ticker,
                    desired_close,
                    market.get("status"),
                    f"{desired_strike:.2f}" if desired_strike is not None else "NA",
                    self.config.run_id,
                )

        if desired_ticker != self.current_watch_ticker:
            previous_ticker = self.current_watch_ticker
            if previous_ticker is not None:
                if (
                    self.post_entry_shadow_watch is not None
                    and normalize_ticker(self.post_entry_shadow_watch.market_ticker) == normalize_ticker(previous_ticker)
                    and self.post_entry_shadow_task is not None
                    and not self.post_entry_shadow_task.done()
                ):
                    self.post_entry_shadow_task.cancel()
                    self.post_entry_shadow_events.emit(
                        "post_entry_shadow_skipped",
                        market=previous_ticker,
                        side=self.post_entry_shadow_watch.side,
                        reason="market_rotated_before_shadow_fire",
                        entry_origin=self.post_entry_shadow_watch.entry_origin,
                    )
                await self.maybe_finalize_market_outcome_from_exchange(previous_ticker)
            self.current_watch_ticker = desired_ticker
            self.watch_close_time = desired_close
            self.market = MarketSnapshot(market_ticker=desired_ticker, close_time=desired_close, strike=desired_strike)
            self.orderbook.reset(desired_ticker, trust_state="cold")
            self.recent_price_history.clear()
            self.execution_state.clear()
            self.executable_windows.clear()
            self.liquidity_dwell_candidates.clear()
            self.ensure_market_outcome_record(desired_ticker, desired_close)
            await self.refresh_recent_market_outcomes_from_exchange(limit=8)
            await self.issue_truffle_regime_lease_for_market(desired_ticker, desired_close)
            await self.restart_ws_task()

    async def ensure_ws_task(self) -> None:
        if not self.current_watch_ticker:
            return
        if self.ws_task is None or self.ws_task.done():
            await self.restart_ws_task()

    async def stop_ws_task(self) -> None:
        if self.ws_task:
            self.ws_task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await self.ws_task
            self.ws_task = None

    async def restart_ws_task(self) -> None:
        self.ws_connection_generation += 1
        generation = self.ws_connection_generation
        await self.stop_ws_task()
        if self.current_watch_ticker:
            self.ws_task = asyncio.create_task(self.ws_market_loop(self.current_watch_ticker, generation))

    async def ws_market_loop(self, market_ticker: str, generation: int) -> None:
        while not self.shutdown_event.is_set() and self.current_watch_ticker == market_ticker and self.ws_connection_generation == generation:
            headers = self.client.websocket_headers()
            try:
                async with websockets.connect(
                    self.config.ws_url,
                    additional_headers=headers,
                    ping_interval=20,
                    ping_timeout=20,
                    max_size=2**20,
                ) as ws:
                    self.logger.info("WS connected for %s", market_ticker)
                    sub_msg = {
                        "id": generation,
                        "cmd": "subscribe",
                        "params": {
                            "channels": ["ticker", "orderbook_delta"],
                            "market_ticker": market_ticker,
                        },
                    }
                    await ws.send(json.dumps(sub_msg))
                    async for raw in ws:
                        if self.shutdown_event.is_set():
                            break
                        msg = json.loads(raw)
                        await self.handle_ws_message(msg, market_ticker)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                self.logger.warning("WS loop error for %s: %s", market_ticker, exc)
                await asyncio.sleep(self.config.websocket_reconnect_seconds)
            else:
                self.logger.warning("WS connection closed for %s. Reconnecting.", market_ticker)
                await asyncio.sleep(self.config.websocket_reconnect_seconds)

    async def handle_ws_message(self, payload: dict[str, Any], market_ticker: str) -> None:
        msg_type = str(payload.get("type") or "")
        if msg_type == "subscribed":
            self.logger.info("WS subscribed payload: %s", payload)
            return
        if msg_type == "error":
            self.logger.error("WS error payload: %s", payload)
            return
        if msg_type == "ticker":
            msg = payload.get("msg", {})
            self.market.market_ticker = str(msg.get("market_ticker") or market_ticker)
            self.market.yes_bid_cents = extract_price_cents(msg, "yes_bid")
            self.market.yes_ask_cents = extract_price_cents(msg, "yes_ask")
            self.market.no_bid_cents = extract_price_cents(msg, "no_bid")
            self.market.no_ask_cents = extract_price_cents(msg, "no_ask")
            self.market.yes_bid_size = to_decimal(msg.get("yes_bid_size_fp"))
            self.market.yes_ask_size = to_decimal(msg.get("yes_ask_size_fp"))
            self.market.no_bid_size = to_decimal(msg.get("no_bid_size_fp"))
            self.market.no_ask_size = to_decimal(msg.get("no_ask_size_fp"))
            self.market.updated_time = str(msg.get("time") or msg.get("ts") or "")
            self.market.local_received_monotonic = time.monotonic()
            self.record_price_history_point(force=False)
            self.request_market_reaction()
            return
        if msg_type == "orderbook_snapshot":
            seq = safe_int(payload.get("seq"))
            msg = payload.get("msg", {})
            self.orderbook.apply_snapshot(msg, seq)
            self.logger.info("Orderbook snapshot ready for %s", market_ticker)
            self.record_price_history_point(force=True)
            self.request_market_reaction()
            return
        if msg_type == "orderbook_delta":
            seq = safe_int(payload.get("seq"))
            msg = payload.get("msg", {})
            if self.orderbook.last_seq is not None and seq is not None and seq != (self.orderbook.last_seq + 1):
                self.orderbook.mark_sequence_gap()
                self.logger.warning(
                    "Orderbook seq gap detected | market=%s expected_seq=%s got_seq=%s. Forcing resync.",
                    market_ticker,
                    self.orderbook.last_seq + 1,
                    seq,
                )
                self.telemetry.emit(
                    "book_resync",
                    ExecutionTelemetryContext(market=market_ticker, decision_reason="sequence_gap"),
                    expected_seq=self.orderbook.last_seq + 1,
                    got_seq=seq,
                    **self.orderbook.telemetry_fields(),
                )
                self.request_ws_resync(market_ticker)
                return
            self.orderbook.apply_delta(msg, seq)
            self.record_price_history_point(force=False)
            self.request_market_reaction()
            return
        if msg_type == "ok":
            return
        self.logger.debug("Unhandled WS payload: %s", payload)

    async def maybe_check_pending_order(self) -> None:
        pending = self.state.pending_order
        if not pending or self.order_inflight:
            return
        now_mono = time.monotonic()
        if self.config.dry_run:
            if now_mono - self.last_rest_order_check_monotonic < 0.2:
                return
            self.last_rest_order_check_monotonic = now_mono
            if pending.purpose == "entry":
                self.record_entry_fill_for_outcomes(
                    market_ticker=pending.market_ticker,
                    side=pending.side,
                    fill_count=pending.count,
                    fill_price_cents=pending.limit_price_cents,
                    trigger_price_cents=pending.trigger_price_cents,
                    actual_fee_cents=0,
                )
                position = self.apply_entry_fill_to_position(
                    market_ticker=pending.market_ticker,
                    side=pending.side,
                    fill_count=pending.count,
                    entry_order_id=pending.order_id,
                    entry_limit_price_cents=pending.limit_price_cents,
                    entry_fill_price_cents=pending.limit_price_cents,
                    entry_fee_cents=0,
                    entry_trigger_price_cents=pending.trigger_price_cents,
                )
                self.mark_traded(pending.market_ticker)
                self.arm_post_entry_shadow_watch(
                    market_ticker=pending.market_ticker,
                    side=pending.side,
                    filled_at_iso=position.filled_at,
                    entry_fill_cents=pending.limit_price_cents,
                    entry_trigger_cents=pending.trigger_price_cents,
                    entry_limit_cents=pending.limit_price_cents,
                    seconds_to_close_at_entry=self.seconds_to_close(),
                    book_age_ms_at_entry=self.current_book_age_ms(),
                    eligible_depth_at_entry=self.orderbook.executable_buy_depth(pending.side, pending.limit_price_cents),
                    executable_window_ms_at_entry=None,
                    entry_origin="pending_order_dry_run_fill",
                )
                self.logger.info("DRY RUN: simulated filled entry %s side=%s qty=%s", pending.market_ticker, pending.side, pending.count)
            else:
                self.logger.info("DRY RUN: simulated filled exit %s side=%s qty=%s", pending.market_ticker, pending.side, pending.count)
                if self.state.position is not None:
                    remaining_position = max(0, int(self.state.position.count) - int(pending.count))
                    self.record_exit_fill_for_outcomes(
                        market_ticker=pending.market_ticker,
                        fill_count=pending.count,
                        fill_price_cents=pending.limit_price_cents,
                        remaining_position=remaining_position,
                        actual_fee_cents=0,
                    )
                self.state.position = None
            self.state.pending_order = None
            self.save_state()
            return
        if now_mono - self.last_rest_order_check_monotonic < self.config.rest_poll_seconds:
            return
        self.last_rest_order_check_monotonic = now_mono
        try:
            order = await asyncio.to_thread(self.client.get_order, pending.order_id)
        except Exception as exc:  # noqa: BLE001
            if await self.handle_pending_order_lookup_failure(pending, exc):
                return
            raise
        status = str(order.get("status") or "").lower()
        fill_count = safe_int(order.get("fill_count")) or decimal_to_int(to_decimal(order.get("fill_count_fp"))) or 0
        remaining_count = safe_int(order.get("remaining_count")) or decimal_to_int(to_decimal(order.get("remaining_count_fp"))) or 0
        actual_fill_price_cents = extract_order_fill_price_cents(order, fill_count=fill_count)
        actual_fee_cents = extract_order_fee_cents(order, fill_count=fill_count)
        self.logger.info(
            "Order status check | order_id=%s purpose=%s status=%s fill_count=%s remaining=%s",
            pending.order_id,
            pending.purpose,
            status,
            fill_count,
            remaining_count,
        )
        if fill_count > 0 and (fill_count >= pending.count or status in {"executed", "canceled"}):
            if pending.purpose == "entry":
                entry_fill_cents = actual_fill_price_cents or pending.limit_price_cents
                entry_fee_cents = actual_fee_cents if actual_fee_cents is not None else self.estimated_order_fee_cents(entry_fill_cents, fill_count)
                self.record_entry_fill_for_outcomes(
                    market_ticker=pending.market_ticker,
                    side=pending.side,
                    fill_count=fill_count,
                    fill_price_cents=entry_fill_cents,
                    trigger_price_cents=pending.trigger_price_cents,
                    actual_fee_cents=actual_fee_cents,
                )
                position = self.apply_entry_fill_to_position(
                    market_ticker=pending.market_ticker,
                    side=pending.side,
                    fill_count=fill_count,
                    entry_order_id=pending.order_id,
                    entry_limit_price_cents=pending.limit_price_cents,
                    entry_fill_price_cents=entry_fill_cents,
                    entry_fee_cents=entry_fee_cents,
                    entry_trigger_price_cents=pending.trigger_price_cents,
                )
                self.mark_traded(pending.market_ticker)
                self.arm_post_entry_shadow_watch(
                    market_ticker=pending.market_ticker,
                    side=pending.side,
                    filled_at_iso=position.filled_at,
                    entry_fill_cents=entry_fill_cents,
                    entry_trigger_cents=pending.trigger_price_cents,
                    entry_limit_cents=pending.limit_price_cents,
                    seconds_to_close_at_entry=self.seconds_to_close(),
                    book_age_ms_at_entry=self.current_book_age_ms(),
                    eligible_depth_at_entry=self.orderbook.executable_buy_depth(pending.side, pending.limit_price_cents),
                    executable_window_ms_at_entry=None,
                    entry_origin="pending_order_fill",
                )
                self.logger.info(
                    "ENTRY filled | market=%s side=%s qty=%s limit=%sc",
                    pending.market_ticker,
                    pending.side,
                    fill_count,
                    pending.limit_price_cents,
                )
            else:
                self.logger.info("EXIT filled | market=%s side=%s qty=%s", pending.market_ticker, pending.side, fill_count)
                remaining_position = max(0, (self.state.position.count if self.state.position else pending.count) - fill_count)
                if actual_fill_price_cents is not None:
                    self.record_exit_fill_for_outcomes(
                        market_ticker=pending.market_ticker,
                        fill_count=fill_count,
                        fill_price_cents=actual_fill_price_cents,
                        remaining_position=remaining_position,
                        actual_fee_cents=actual_fee_cents,
                    )
                if remaining_position > 0 and self.state.position:
                    self.state.position.count = remaining_position
                else:
                    self.state.position = None
            self.state.pending_order = None
            self.save_state()
            return
        if status == "canceled":
            self.logger.warning("Pending order canceled | order_id=%s purpose=%s", pending.order_id, pending.purpose)
            self.state.pending_order = None
            if pending.purpose == "exit":
                self.exit_retry_block_until_monotonic = time.monotonic() + 1.0
            self.save_state()

    async def maybe_check_entry(self) -> None:
        if self.state.pending_order or self.order_inflight:
            return
        if self.state.position is not None:
            ticker = self.current_watch_ticker or self.state.position.market_ticker
            entry_block_count = 1 if self.config.mushroom_v28_decision_engine_enabled else self.config.position_size
            reason = self.entry_block_reason(ticker, count=entry_block_count)
            if reason in {"different_open_position", "position_open", "max_position_contracts", "multi_entry_cooldown"}:
                return
            if reason == "opposite_side_position":
                return
        if self.current_watch_ticker is None:
            return
        if time.monotonic() < self.entry_retry_block_until_monotonic:
            return
        signal = self.detect_entry_signal()
        if signal is None:
            return
        self.attach_mushroom_shadow(signal)
        existing_market_record = self.market_outcomes.get(signal.market_ticker)
        if existing_market_record is None or existing_market_record.signal_count <= 0:
            self.market_outcomes.mark_signal_seen(signal.market_ticker)
        if self.should_suppress_stale_book(signal):
            return
        if self.should_suppress_dead_market(signal):
            return
        mushroom_fields = self.mushroom_telemetry_fields(signal)
        self.telemetry.emit("signal_seen", self.telemetry_context_from_signal(signal), **mushroom_fields, **self.orderbook.telemetry_fields())
        filter_decision = self.evaluate_pre_entry_filters(signal)
        if not filter_decision.allowed:
            self.telemetry.emit("filter_blocked", self.telemetry_context_from_signal(signal, filter_decision=filter_decision), **mushroom_fields, **self.orderbook.telemetry_fields())
            return
        regime_decision = self.evaluate_btc_vol_regime_gate(signal)
        if not regime_decision.allowed:
            self.telemetry.emit("filter_blocked", self.telemetry_context_from_signal(signal, filter_decision=regime_decision), btc_range_dollars=self.btc_vol_regime_snapshot.range_dollars, btc_range_threshold_dollars=float(self.config.btc_vol_regime_max_range_dollars), btc_regime_age_ms=self.btc_vol_regime_age_ms(), btc_regime_source=self.btc_vol_regime_snapshot.source, **mushroom_fields, **self.orderbook.telemetry_fields())
            return
        lease_decision = self.evaluate_truffle_regime_lease(signal)
        if not lease_decision.allowed:
            self.telemetry.emit(
                "filter_blocked",
                self.telemetry_context_from_signal(signal, filter_decision=lease_decision),
                lease_mode=self.config.truffle_regime_lease_mode,
                lease_decision=self.current_regime_lease.decision if self.current_regime_lease is not None else "",
                lease_issued_at=self.current_regime_lease.issued_at if self.current_regime_lease is not None else "",
                **mushroom_fields,
                **self.orderbook.telemetry_fields(),
            )
            return
        plan = self.build_execution_plan(signal, filter_decision)
        if plan is None:
            return
        self.telemetry.emit("plan_built", self.telemetry_context_from_plan(plan, filter_decision), account_age_ms=plan.account_age_ms, **self.mushroom_telemetry_fields(plan), **self.orderbook.telemetry_fields())
        await self.submit_execution_plan(plan, filter_decision)

    def current_entry_ask_cents(self, side: str) -> int | None:
        if side == "yes":
            held_ask = self.market.yes_ask_cents
            if held_ask is None:
                no_bid_book, _ = self.orderbook.best_bid("no")
                if no_bid_book is not None:
                    held_ask = 100 - no_bid_book
                elif self.market.no_bid_cents is not None:
                    held_ask = 100 - self.market.no_bid_cents
            return held_ask
        if side == "no":
            held_ask = self.market.no_ask_cents
            if held_ask is None:
                yes_bid_book, _ = self.orderbook.best_bid("yes")
                if yes_bid_book is not None:
                    held_ask = 100 - yes_bid_book
                elif self.market.yes_bid_cents is not None:
                    held_ask = 100 - self.market.yes_bid_cents
            return held_ask
        raise ValueError(f"Invalid side: {side}")

    def current_market_p_yes(self) -> float | None:
        yes_bid, yes_ask, _, _ = self.derived_quote_values()
        if yes_bid is None or yes_ask is None:
            return None
        mid = (float(yes_bid) + float(yes_ask)) / 200.0
        return max(0.001, min(0.999, mid))

    def mushroom_telemetry_fields(self, signal_or_plan: EntrySignal | ExecutionPlan | ExitSignal | ExitPlan) -> dict[str, Any]:
        shadow = getattr(signal_or_plan, "mushroom_shadow", None)
        return dict(shadow) if isinstance(shadow, dict) else {}

    def attach_mushroom_shadow(self, signal: EntrySignal) -> None:
        existing = dict(signal.mushroom_shadow) if isinstance(signal.mushroom_shadow, dict) else {}
        signal.mushroom_shadow = {
            **self.build_mushroom_shadow(signal),
            **self.build_mushroom_v28_shadow(signal),
            **existing,
        }

    @staticmethod
    def _round_or_none(value: Any, digits: int = 6) -> float | None:
        if value is None:
            return None
        try:
            if isinstance(value, Decimal):
                value = float(value)
            number = float(value)
        except (TypeError, ValueError):
            return None
        if math.isnan(number) or math.isinf(number):
            return None
        return round(number, digits)

    def build_mushroom_shadow(self, signal: EntrySignal) -> dict[str, Any]:
        fields: dict[str, Any] = {
            "mushroom_version": MUSHROOM_VERSION,
            "mushroom_status": "disabled",
            "mushroom_shadow_enabled": bool(self.config.mushroom_shadow_enabled),
        }
        if not self.config.mushroom_shadow_enabled or self.mushroom_forecaster is None:
            return fields
        strike = self.market.strike
        seconds_to_close = signal.seconds_to_close
        history_bars = self.mushroom_history_count()
        fields.update(
            {
                "mushroom_status": "warming",
                "mushroom_history_bars": history_bars,
                "strike": self._round_or_none(strike, 2),
                "seconds_to_close": self._round_or_none(seconds_to_close, 3),
                "derived_yes_ask": self.current_entry_ask_cents("yes"),
                "derived_no_ask": self.current_entry_ask_cents("no"),
            }
        )
        min_history = MushroomConfig().min_history_points
        if strike is None:
            fields["mushroom_status"] = "missing_strike"
            return fields
        if seconds_to_close is None or float(seconds_to_close) <= 0:
            fields["mushroom_status"] = "missing_horizon"
            return fields
        if history_bars < min_history:
            fields["mushroom_min_history_bars"] = min_history
            return fields

        market_p_yes = self.current_market_p_yes()
        min_edge = float(self.config.mushroom_min_edge_cents_15m)
        min_p_side = float(self.config.mushroom_min_p_side)
        strict_p_side = float(self.config.mushroom_strict_p_side)
        slippage_cents = float(self.config.live_entry_fast_fill_slippage_budget_cents)
        model_buffer_cents = float(self.config.mushroom_model_buffer_cents)
        book_age_ms = signal.book_age_ms
        max_book_age_ms = self.allowed_live_book_age_ms(seconds_to_close)
        book_ok = book_age_ms is not None and float(book_age_ms) <= float(max_book_age_ms)
        size = max(1, int(self.config.position_size))
        best_side: str | None = None
        best_edge: float | None = None
        selected_components: dict[str, float] = {}

        for side in ("yes", "no"):
            prefix = f"mushroom_{side}"
            top_limit = self.orderbook.top_of_book_buy_limit_cents(side)
            executable_limit = self.orderbook.executable_buy_limit_cents(side, size)
            ask_cents = executable_limit if executable_limit is not None else top_limit
            if ask_cents is None:
                ask_cents = self.current_entry_ask_cents(side)
            eligible_depth = Decimal("0")
            if ask_cents is not None:
                eligible_depth = self.orderbook.executable_buy_depth(side, int(ask_cents))
            try:
                with self.mushroom_lock:
                    pred = self.mushroom_forecaster.predict_physical(
                        side=side,
                        strike=float(strike),
                        horizon_seconds=float(seconds_to_close),
                        market_p_yes=market_p_yes,
                    )
            except Exception as exc:  # noqa: BLE001
                fields["mushroom_status"] = "prediction_error"
                fields["mushroom_error"] = str(exc)
                return fields
            fee_cents = None
            edge_cents = None
            if ask_cents is not None:
                fee_cents = self.estimated_order_fee_cents(int(ask_cents), size) / float(size)
                edge_cents = float(pred.fair_cents) - float(ask_cents) - fee_cents - slippage_cents - model_buffer_cents
            depth_ok = eligible_depth >= Decimal(str(size))
            broad_ok = (
                edge_cents is not None
                and edge_cents >= min_edge
                and float(pred.p_side) >= min_p_side
                and bool(book_ok)
                and bool(depth_ok)
            )
            strict_ok = (
                edge_cents is not None
                and edge_cents >= min_edge
                and float(pred.p_side) >= strict_p_side
                and bool(book_ok)
                and bool(depth_ok)
            )
            comp = pred.components
            side_components = {
                "p_yes": float(pred.p_yes),
                "p_side": float(pred.p_side),
                "fair_cents": float(pred.fair_cents),
                "edge_cents": edge_cents if edge_cents is not None else float("nan"),
                "d_sigma": float(comp.get("d_sigma", 0.0)),
                "abs_d_sigma": float(comp.get("abs_d_sigma", 0.0)),
                "p_anchor": float(comp.get("p_anchor", 0.0)),
                "p_recent_transport": float(comp.get("p_recent_transport", 0.0)),
                "p_long_transport": float(comp.get("p_long_transport", 0.0)),
                "edge_gate": float(comp.get("edge_gate", 0.0)),
                "arrow": float(comp.get("arrow", 0.0)),
                "sigma_t_dollars": float(pred.sigma_t_dollars),
                "volshock": float(comp.get("volshock", 0.0)),
                "transport_recent_n": float(comp.get("transport_recent_n", 0.0)),
                "transport_long_n": float(comp.get("transport_long_n", 0.0)),
                "market_contradiction_logit": float(comp.get("market_contradiction_logit", 0.0)),
            }
            fields.update(
                {
                    f"{prefix}_ask_cents": ask_cents,
                    f"{prefix}_top_of_book_limit_cents": top_limit,
                    f"{prefix}_executable_limit_cents": executable_limit,
                    f"{prefix}_eligible_depth": format_decimal_compact(eligible_depth),
                    f"{prefix}_fee_cents": self._round_or_none(fee_cents, 4),
                    f"{prefix}_would_enter": bool(broad_ok),
                    f"{prefix}_strict_would_enter": bool(strict_ok),
                }
            )
            for name, value in side_components.items():
                fields[f"{prefix}_{name}"] = self._round_or_none(value, 6)
            if edge_cents is not None and (best_edge is None or edge_cents > best_edge):
                best_side = side
                best_edge = edge_cents
            if side == signal.side:
                selected_components = side_components
                fields.update(
                    {
                        "mushroom_side": side,
                        "mushroom_ask_cents": ask_cents,
                        "mushroom_fee_cents": self._round_or_none(fee_cents, 4),
                        "mushroom_eligible_depth": format_decimal_compact(eligible_depth),
                        "mushroom_would_v22_enter": bool(broad_ok),
                        "mushroom_strict_would_v22_enter": bool(strict_ok),
                    }
                )

        fields.update(
            {
                "mushroom_status": "ok",
                "mushroom_best_side": best_side,
                "mushroom_best_edge_cents": self._round_or_none(best_edge, 6),
                "mushroom_min_p_side": min_p_side,
                "mushroom_strict_p_side": strict_p_side,
                "mushroom_min_edge_cents": min_edge,
                "mushroom_model_buffer_cents": model_buffer_cents,
                "mushroom_slippage_cents": slippage_cents,
                "mushroom_book_ok": bool(book_ok),
                "mushroom_max_book_age_ms": self._round_or_none(max_book_age_ms, 3),
                "mushroom_market_p_yes": self._round_or_none(market_p_yes, 6),
            }
        )
        for name, value in selected_components.items():
            fields[f"mushroom_{name}"] = self._round_or_none(value, 6)
        return fields

    def build_mushroom_v21_decision_fields(
        self,
        *,
        side: str,
        ask_cents: int | None,
        top_limit: int | None,
        executable_limit: int | None,
        eligible_depth: Decimal,
        seconds_to_close: float | None,
        book_age_ms: float | None,
    ) -> dict[str, Any]:
        fields: dict[str, Any] = {
            "mushroom_v21_version": MUSHROOM_V21_DECISION_VERSION,
            "mushroom_v21_status": "disabled",
            "mushroom_v21_side": side,
            "mushroom_v21_engine_enabled": bool(self.config.mushroom_v21_decision_engine_enabled),
            "mushroom_v21_ask_cents": ask_cents,
            "mushroom_v21_top_of_book_limit_cents": top_limit,
            "mushroom_v21_executable_limit_cents": executable_limit,
            "mushroom_v21_eligible_depth": format_decimal_compact(eligible_depth),
            "mushroom_v21_seconds_to_close": self._round_or_none(seconds_to_close, 3),
            "mushroom_v21_book_age_ms": self._round_or_none(book_age_ms, 3),
        }
        if not self.config.mushroom_v21_decision_engine_enabled or self.mushroom_v21_forecaster is None:
            return fields

        strike = self.market.strike
        history_bars = self.mushroom_v21_history_count()
        min_history = mushroom_v21_config().min_history_points
        max_book_age_ms = self.allowed_live_book_age_ms(seconds_to_close)
        book_ok = book_age_ms is not None and float(book_age_ms) <= float(max_book_age_ms)
        time_ok = (
            seconds_to_close is not None
            and float(seconds_to_close) >= float(self.config.mushroom_v21_min_seconds_to_close)
            and float(seconds_to_close) <= float(self.config.mushroom_v21_max_seconds_to_close)
        )
        ask_ok = ask_cents is not None and int(ask_cents) <= int(self.config.mushroom_v21_max_ask_cents)
        depth_ok = eligible_depth >= Decimal(str(max(1, int(self.config.position_size))))
        fields.update(
            {
                "mushroom_v21_status": "warming",
                "mushroom_v21_history_bars": history_bars,
                "mushroom_v21_min_history_bars": min_history,
                "mushroom_v21_strike": self._round_or_none(strike, 2),
                "mushroom_v21_book_ok": bool(book_ok),
                "mushroom_v21_max_book_age_ms": self._round_or_none(max_book_age_ms, 3),
                "mushroom_v21_time_ok": bool(time_ok),
                "mushroom_v21_ask_ok": bool(ask_ok),
                "mushroom_v21_depth_ok": bool(depth_ok),
                "mushroom_v21_min_p_side": float(self.config.mushroom_v21_min_p_side),
                "mushroom_v21_min_edge_cents": float(self.config.mushroom_v21_min_edge_cents_15m),
                "mushroom_v21_max_ask_cents": int(self.config.mushroom_v21_max_ask_cents),
                "mushroom_v21_min_seconds_to_close": float(self.config.mushroom_v21_min_seconds_to_close),
                "mushroom_v21_max_seconds_to_close": float(self.config.mushroom_v21_max_seconds_to_close),
                "mushroom_v21_model_buffer_cents": float(self.config.mushroom_v21_model_buffer_cents),
                "mushroom_v21_slippage_cents": float(self.config.mushroom_v21_slippage_cents),
            }
        )
        if strike is None:
            fields["mushroom_v21_status"] = "missing_strike"
            return fields
        if seconds_to_close is None or float(seconds_to_close) <= 0:
            fields["mushroom_v21_status"] = "missing_horizon"
            return fields
        if history_bars < min_history:
            return fields
        if ask_cents is None:
            fields["mushroom_v21_status"] = "missing_ask"
            return fields

        try:
            with self.mushroom_lock:
                pred = self.mushroom_v21_forecaster.predict_physical(
                    side=side,
                    strike=float(strike),
                    horizon_seconds=float(seconds_to_close),
                    market_p_yes=self.current_market_p_yes(),
                )
        except Exception as exc:  # noqa: BLE001
            fields["mushroom_v21_status"] = "prediction_error"
            fields["mushroom_v21_error"] = str(exc)
            return fields

        size = max(1, int(self.config.position_size))
        fee_cents = self.estimated_order_fee_cents(int(ask_cents), size) / float(size)
        raw_edge_cents = float(pred.fair_cents) - float(ask_cents) - fee_cents
        edge_cents = (
            raw_edge_cents
            - float(self.config.mushroom_v21_slippage_cents)
            - float(self.config.mushroom_v21_model_buffer_cents)
        )
        p_ok = float(pred.p_side) >= float(self.config.mushroom_v21_min_p_side)
        edge_ok = edge_cents >= float(self.config.mushroom_v21_min_edge_cents_15m)
        approved = bool(p_ok and edge_ok and ask_ok and depth_ok and book_ok and time_ok)
        comp = pred.components
        fields.update(
            {
                "mushroom_v21_status": "ok",
                "mushroom_v21_p_yes": self._round_or_none(pred.p_yes, 6),
                "mushroom_v21_p_side": self._round_or_none(pred.p_side, 6),
                "mushroom_v21_fair_cents": self._round_or_none(pred.fair_cents, 6),
                "mushroom_v21_fee_cents": self._round_or_none(fee_cents, 4),
                "mushroom_v21_raw_edge_cents": self._round_or_none(raw_edge_cents, 6),
                "mushroom_v21_edge_cents": self._round_or_none(edge_cents, 6),
                "mushroom_v21_sigma_t_dollars": self._round_or_none(pred.sigma_t_dollars, 6),
                "mushroom_v21_d_sigma": self._round_or_none(comp.get("d_sigma"), 6),
                "mushroom_v21_abs_d_sigma": self._round_or_none(comp.get("abs_d_sigma"), 6),
                "mushroom_v21_p_anchor": self._round_or_none(comp.get("p_anchor"), 6),
                "mushroom_v21_p_static_boundary_field": self._round_or_none(comp.get("p_static_boundary_field"), 6),
                "mushroom_v21_arrow": self._round_or_none(comp.get("arrow"), 6),
                "mushroom_v21_volshock": self._round_or_none(comp.get("volshock"), 6),
                "mushroom_v21_market_p_yes": self._round_or_none(self.current_market_p_yes(), 6),
                "mushroom_v21_p_ok": bool(p_ok),
                "mushroom_v21_edge_ok": bool(edge_ok),
                "mushroom_v21_approved": approved,
            }
        )
        return fields

    def detect_mushroom_v21_entry_signal(self) -> EntrySignal | None:
        ticker = self.current_watch_ticker
        if not ticker or not self.orderbook.snapshot_ready:
            return None
        if self.mushroom_v21_forecaster is None:
            return None
        seconds_to_close = self.seconds_to_close()
        book_age_ms = self.current_book_age_ms()
        candidates: list[tuple[float, float, EntrySignal]] = []
        for side in ("yes", "no"):
            if self.entry_block_reason(ticker, side, self.config.position_size):
                continue
            rejection_state = self.entry_rejection_state.get(f"{normalize_ticker(ticker)}:{side}")
            if rejection_state and time.monotonic() < rejection_state.block_until_monotonic:
                continue
            top_limit = self.orderbook.top_of_book_buy_limit_cents(side)
            executable_limit = self.orderbook.executable_buy_limit_cents(side, self.config.position_size)
            ask_cents = executable_limit if executable_limit is not None else top_limit
            if ask_cents is None:
                ask_cents = self.current_entry_ask_cents(side)
            eligible_depth = Decimal("0")
            if ask_cents is not None:
                eligible_depth = self.orderbook.executable_buy_depth(side, int(ask_cents))
            fields = self.build_mushroom_v21_decision_fields(
                side=side,
                ask_cents=int(ask_cents) if ask_cents is not None else None,
                top_limit=top_limit,
                executable_limit=executable_limit,
                eligible_depth=eligible_depth,
                seconds_to_close=seconds_to_close,
                book_age_ms=book_age_ms,
            )
            if not fields.get("mushroom_v21_approved"):
                continue
            edge_cents = float(fields.get("mushroom_v21_edge_cents") or 0.0)
            p_side = float(fields.get("mushroom_v21_p_side") or 0.0)
            trigger_price = int(ask_cents)
            signal_signature = "|".join(
                [
                    "mushroom_v21",
                    f"p={p_side:.6f}",
                    f"edge={edge_cents:.6f}",
                    f"ask={trigger_price}",
                    f"raw_edge={fields.get('mushroom_v21_raw_edge_cents')}",
                    f"ttc={self._round_or_none(seconds_to_close, 3)}",
                    f"trust={self.orderbook.trust.trust_state}",
                ]
            )
            signal = EntrySignal(
                market_ticker=ticker,
                side=side,
                trigger_price_cents=trigger_price,
                cap_price_cents=trigger_price,
                top_of_book_limit_cents=top_limit,
                executable_limit_cents=executable_limit,
                eligible_depth=eligible_depth,
                book_age_ms=book_age_ms,
                seconds_to_close=seconds_to_close,
                book_summary=self.describe_live_buy_book(side),
                yes_ask_cents=self.current_entry_ask_cents("yes"),
                no_ask_cents=self.current_entry_ask_cents("no"),
                signal_signature=signal_signature,
                mushroom_shadow=fields,
            )
            self.update_executable_window(signal)
            window = self.executable_windows.get(self.market_side_key(ticker, side))
            if window and window.active and window.since_monotonic is not None:
                signal.first_executable_at_monotonic = window.since_monotonic
                signal.executable_window_ms = (time.monotonic() - window.since_monotonic) * 1000.0
            candidates.append((edge_cents, p_side, signal))
        if not candidates:
            return None
        _, _, selected = max(candidates, key=lambda item: (item[0], item[1]))
        self.logger.info(
            "Mushroom v21 entry approved | market=%s side=%s ask=%sc p_side=%.4f edge=%.3fc raw_edge=%.3fc depth=%s secs_to_close=%s",
            selected.market_ticker,
            selected.side,
            selected.trigger_price_cents,
            float(selected.mushroom_shadow.get("mushroom_v21_p_side") or 0.0),
            float(selected.mushroom_shadow.get("mushroom_v21_edge_cents") or 0.0),
            float(selected.mushroom_shadow.get("mushroom_v21_raw_edge_cents") or 0.0),
            format_decimal_compact(selected.eligible_depth),
            f"{selected.seconds_to_close:.2f}" if selected.seconds_to_close is not None else "NA",
        )
        self.telemetry.emit(
            "mushroom_v21_approved",
            self.telemetry_context_from_signal(selected),
            **self.mushroom_telemetry_fields(selected),
            **self.orderbook.telemetry_fields(),
        )
        return selected

    def mushroom_v28_entry_max_count(self, ticker: str, side: str) -> tuple[int, str]:
        block = self.entry_block_reason(ticker, side, 1)
        if block is not None:
            return 0, block
        max_count = max(1, int(self.config.position_size))
        position = self.state.position
        if position is not None and normalize_ticker(position.market_ticker) == normalize_ticker(ticker):
            remaining = max(0, int(self.config.multi_entry_max_position_contracts) - int(position.count))
            max_count = min(max_count, remaining)
        return max(0, max_count), ""

    def build_mushroom_v28_shadow(self, signal: EntrySignal) -> dict[str, Any]:
        if not self.config.mushroom_v28_shadow_enabled:
            return {
                "mushroom_v28_version": MUSHROOM_V28_VERSION,
                "mushroom_v28_status": "disabled",
                "mushroom_v28_shadow_enabled": False,
            }
        side = signal.side
        ask_cents = signal.executable_limit_cents or signal.top_of_book_limit_cents or self.current_entry_ask_cents(side)
        eligible_depth = Decimal("0")
        if ask_cents is not None:
            eligible_depth = self.orderbook.executable_buy_depth(side, int(ask_cents))
        return self.build_mushroom_v28_decision_fields(
            side=side,
            ask_cents=int(ask_cents) if ask_cents is not None else None,
            top_limit=signal.top_of_book_limit_cents,
            executable_limit=signal.executable_limit_cents,
            eligible_depth=eligible_depth,
            seconds_to_close=signal.seconds_to_close,
            book_age_ms=signal.book_age_ms,
            target_count_hint=signal.target_count,
        )

    def build_mushroom_v28_decision_fields(
        self,
        *,
        side: str,
        ask_cents: int | None,
        top_limit: int | None,
        executable_limit: int | None,
        eligible_depth: Decimal,
        seconds_to_close: float | None,
        book_age_ms: float | None,
        target_count_hint: int | None = None,
    ) -> dict[str, Any]:
        ticker = self.current_watch_ticker or ""
        fields: dict[str, Any] = {
            "mushroom_v28_version": MUSHROOM_V28_VERSION,
            "mushroom_v28_status": "disabled",
            "mushroom_v28_side": side,
            "mushroom_v28_shadow_enabled": bool(self.config.mushroom_v28_shadow_enabled),
            "mushroom_v28_decision_engine_enabled": bool(self.config.mushroom_v28_decision_engine_enabled),
            "mushroom_v28_live_exit_enabled": bool(self.config.mushroom_v28_live_exit_enabled),
            "mushroom_v28_ask_cents": ask_cents,
            "mushroom_v28_top_of_book_limit_cents": top_limit,
            "mushroom_v28_executable_limit_cents": executable_limit,
            "mushroom_v28_eligible_depth": format_decimal_compact(eligible_depth),
            "mushroom_v28_seconds_to_close": self._round_or_none(seconds_to_close, 3),
            "mushroom_v28_book_age_ms": self._round_or_none(book_age_ms, 3),
            "mushroom_v28_btc_age_ms": self._round_or_none(self.mushroom_v28_btc_age_ms(), 3),
            "mushroom_v28_btc_source": self.mushroom_v28_last_tick_source,
            "mushroom_v28_btc_price": self._round_or_none(self.mushroom_v28_last_tick_price, 2),
        }
        if self.mushroom_v28_worker is None:
            return fields

        strike = self.market.strike
        history_bars = self.mushroom_v28_history_count()
        min_history = int(getattr(self.mushroom_v28_worker.engine.config, "min_bars", MushroomV28Config().min_bars))
        max_book_age_ms = self.allowed_live_book_age_ms(seconds_to_close)
        btc_age_ms = self.mushroom_v28_btc_age_ms()
        max_allowed_count, block_reason = self.mushroom_v28_entry_max_count(ticker, side) if ticker else (0, "missing_ticker")
        if target_count_hint is not None:
            max_allowed_count = min(max_allowed_count, max(0, int(target_count_hint)))
        book_ok = book_age_ms is not None and float(book_age_ms) <= float(max_book_age_ms)
        btc_ok = btc_age_ms is not None and float(btc_age_ms) <= float(self.config.mushroom_v28_btc_max_age_ms)
        time_ok = (
            seconds_to_close is not None
            and float(seconds_to_close) >= float(self.config.mushroom_v28_min_seconds_to_close)
            and float(seconds_to_close) <= float(self.config.mushroom_v28_max_seconds_to_close)
        )
        ask_ok = ask_cents is not None and int(ask_cents) <= int(self.config.mushroom_v28_max_ask_cents)
        depth_count = max(0, decimal_to_int(eligible_depth) or 0)
        fields.update(
            {
                "mushroom_v28_status": "warming",
                "mushroom_v28_history_bars": history_bars,
                "mushroom_v28_min_history_bars": min_history,
                "mushroom_v28_strike": self._round_or_none(strike, 2),
                "mushroom_v28_book_ok": bool(book_ok),
                "mushroom_v28_max_book_age_ms": self._round_or_none(max_book_age_ms, 3),
                "mushroom_v28_btc_ok": bool(btc_ok),
                "mushroom_v28_btc_max_age_ms": self._round_or_none(self.config.mushroom_v28_btc_max_age_ms, 3),
                "mushroom_v28_time_ok": bool(time_ok),
                "mushroom_v28_ask_ok": bool(ask_ok),
                "mushroom_v28_depth_count": depth_count,
                "mushroom_v28_max_allowed_count": max_allowed_count,
                "mushroom_v28_block_reason": block_reason,
                "mushroom_v28_min_p_side": float(self.config.mushroom_v28_min_p_side),
                "mushroom_v28_min_edge_cents": float(self.config.mushroom_v28_min_edge_cents_15m),
                "mushroom_v28_model_buffer_cents": float(self.config.mushroom_v28_model_buffer_cents),
                "mushroom_v28_slippage_cents": float(self.config.mushroom_v28_slippage_cents),
                "mushroom_v28_max_ask_cents": int(self.config.mushroom_v28_max_ask_cents),
                "mushroom_v28_max_market_risk_cents": int(self.config.mushroom_v28_max_market_risk_cents),
            }
        )
        if strike is None:
            fields["mushroom_v28_status"] = "missing_strike"
            return fields
        if seconds_to_close is None or float(seconds_to_close) <= 0:
            fields["mushroom_v28_status"] = "missing_horizon"
            return fields
        if ask_cents is None:
            fields["mushroom_v28_status"] = "missing_ask"
            return fields
        if history_bars < min_history or not self.mushroom_v28_ready():
            return fields

        fee_count = max(1, max_allowed_count or int(self.config.position_size))
        fee_cents = self.estimated_order_fee_cents(int(ask_cents), fee_count) / float(fee_count)
        try:
            with self.mushroom_lock:
                pred = self.mushroom_v28_worker.engine.predict_many(
                    strikes=[float(strike)],
                    horizon_seconds=float(seconds_to_close),
                )
        except Exception as exc:  # noqa: BLE001
            fields["mushroom_v28_status"] = "prediction_error"
            fields["mushroom_v28_error"] = str(exc)
            return fields

        p_yes = float(pred.p_yes[0])
        p_side = p_yes if side == "yes" else (1.0 - p_yes)
        fair_yes = float(pred.fair_yes_cents[0])
        fair_no = float(pred.fair_no_cents[0])
        fair_side = fair_yes if side == "yes" else fair_no
        raw_edge_cents = fair_side - float(ask_cents) - fee_cents
        edge_cents = raw_edge_cents - float(self.config.mushroom_v28_slippage_cents) - float(self.config.mushroom_v28_model_buffer_cents)
        model_max_buy_price = int(math.floor(
            fair_side
            - fee_cents
            - float(self.config.mushroom_v28_slippage_cents)
            - float(self.config.mushroom_v28_model_buffer_cents)
            - float(self.config.mushroom_v28_min_edge_cents_15m)
        ))
        model_max_buy_price = max(1, min(99, model_max_buy_price))
        risk_per_contract_cents = max(1.0, float(ask_cents) + fee_cents)
        risk_count = int(float(self.config.mushroom_v28_max_market_risk_cents) // risk_per_contract_cents)
        balance_count = max_allowed_count
        balance_ok = True
        account_age_ms = self.account_snapshot_age_ms()
        if not self.config.dry_run:
            if self.live_account_snapshot.available_balance_cents is None or account_age_ms is None or account_age_ms > self.config.live_account_state_max_age_ms:
                balance_ok = False
                balance_count = 0
            else:
                spendable_cents = (
                    int(self.live_account_snapshot.available_balance_cents or 0)
                    - int(self.config.live_balance_fee_buffer_cents)
                    - int(self.config.live_balance_min_buffer_cents)
                )
                balance_count = max(0, int(spendable_cents // risk_per_contract_cents))
                balance_ok = balance_count > 0
        target_count = max(0, min(max_allowed_count, depth_count, risk_count, balance_count))
        p_ok = p_side >= float(self.config.mushroom_v28_min_p_side)
        edge_ok = edge_cents >= float(self.config.mushroom_v28_min_edge_cents_15m)
        model_price_ok = int(ask_cents) <= model_max_buy_price
        risk_ok = target_count >= 1
        approved = bool(
            p_ok
            and edge_ok
            and model_price_ok
            and ask_ok
            and book_ok
            and btc_ok
            and time_ok
            and risk_ok
            and balance_ok
            and not block_reason
        )
        components = getattr(pred, "components", {}) or {}
        d_sigma = float(pred.d_sigma[0]) if len(pred.d_sigma) else math.nan
        fields.update(
            {
                "mushroom_v28_status": "ok",
                "mushroom_v28_p_yes": self._round_or_none(p_yes, 6),
                "mushroom_v28_p_side": self._round_or_none(p_side, 6),
                "mushroom_v28_fair_yes_cents": self._round_or_none(fair_yes, 6),
                "mushroom_v28_fair_no_cents": self._round_or_none(fair_no, 6),
                "mushroom_v28_fair_side_cents": self._round_or_none(fair_side, 6),
                "mushroom_v28_fee_cents": self._round_or_none(fee_cents, 4),
                "mushroom_v28_raw_edge_cents": self._round_or_none(raw_edge_cents, 6),
                "mushroom_v28_edge_cents": self._round_or_none(edge_cents, 6),
                "mushroom_v28_net_edge_cents": self._round_or_none(edge_cents, 6),
                "mushroom_v28_sigma_t_dollars": self._round_or_none(pred.sigma_t_dollars, 6),
                "mushroom_v28_d_sigma": self._round_or_none(d_sigma, 6),
                "mushroom_v28_abs_d_sigma": self._round_or_none(abs(d_sigma), 6),
                "mushroom_v28_arrow": self._round_or_none(components.get("arrow"), 6),
                "mushroom_v28_volshock": self._round_or_none(components.get("volshock"), 6),
                "mushroom_v28_effective_horizon_minutes": self._round_or_none(components.get("effective_horizon_minutes"), 6),
                "mushroom_v28_model_max_buy_price_cents": model_max_buy_price,
                "mushroom_v28_risk_per_contract_cents": self._round_or_none(risk_per_contract_cents, 4),
                "mushroom_v28_risk_count": risk_count,
                "mushroom_v28_balance_count": balance_count,
                "mushroom_v28_target_count": target_count,
                "mushroom_v28_risk_cents": self._round_or_none(float(target_count) * risk_per_contract_cents, 4),
                "mushroom_v28_p_ok": bool(p_ok),
                "mushroom_v28_edge_ok": bool(edge_ok),
                "mushroom_v28_model_price_ok": bool(model_price_ok),
                "mushroom_v28_risk_ok": bool(risk_ok),
                "mushroom_v28_balance_ok": bool(balance_ok),
                "mushroom_v28_approved": approved,
            }
        )
        return fields

    def detect_mushroom_v28_entry_signal(self) -> EntrySignal | None:
        ticker = self.current_watch_ticker
        if not ticker or not self.orderbook.snapshot_ready:
            return None
        if self.mushroom_v28_worker is None:
            return None
        seconds_to_close = self.seconds_to_close()
        book_age_ms = self.current_book_age_ms()
        candidates: list[tuple[float, float, EntrySignal]] = []
        for side in ("yes", "no"):
            max_count, block_reason = self.mushroom_v28_entry_max_count(ticker, side)
            if max_count < 1 or block_reason:
                continue
            rejection_state = self.entry_rejection_state.get(f"{normalize_ticker(ticker)}:{side}")
            if rejection_state and time.monotonic() < rejection_state.block_until_monotonic:
                continue
            top_limit = self.orderbook.top_of_book_buy_limit_cents(side)
            ask_cents = top_limit if top_limit is not None else self.current_entry_ask_cents(side)
            eligible_depth = Decimal("0")
            if ask_cents is not None:
                eligible_depth = self.orderbook.executable_buy_depth(side, int(ask_cents))
            fields = self.build_mushroom_v28_decision_fields(
                side=side,
                ask_cents=int(ask_cents) if ask_cents is not None else None,
                top_limit=top_limit,
                executable_limit=int(ask_cents) if ask_cents is not None else None,
                eligible_depth=eligible_depth,
                seconds_to_close=seconds_to_close,
                book_age_ms=book_age_ms,
            )
            if not fields.get("mushroom_v28_approved"):
                continue
            target_count = int(fields.get("mushroom_v28_target_count") or 0)
            if target_count < 1:
                continue
            edge_cents = float(fields.get("mushroom_v28_edge_cents") or 0.0)
            p_side = float(fields.get("mushroom_v28_p_side") or 0.0)
            trigger_price = int(ask_cents)
            model_max_buy_price = int(fields.get("mushroom_v28_model_max_buy_price_cents") or trigger_price)
            signal_signature = "|".join(
                [
                    "mushroom_v28",
                    f"p={p_side:.6f}",
                    f"edge={edge_cents:.6f}",
                    f"ask={trigger_price}",
                    f"max_buy={model_max_buy_price}",
                    f"qty={target_count}",
                    f"btc_age={fields.get('mushroom_v28_btc_age_ms')}",
                    f"ttc={self._round_or_none(seconds_to_close, 3)}",
                    f"trust={self.orderbook.trust.trust_state}",
                ]
            )
            signal = EntrySignal(
                market_ticker=ticker,
                side=side,
                trigger_price_cents=trigger_price,
                cap_price_cents=trigger_price,
                top_of_book_limit_cents=top_limit,
                executable_limit_cents=trigger_price,
                eligible_depth=eligible_depth,
                book_age_ms=book_age_ms,
                seconds_to_close=seconds_to_close,
                book_summary=self.describe_live_buy_book(side),
                yes_ask_cents=self.current_entry_ask_cents("yes"),
                no_ask_cents=self.current_entry_ask_cents("no"),
                signal_signature=signal_signature,
                target_count=target_count,
                model_max_buy_price_cents=model_max_buy_price,
                mushroom_shadow=fields,
            )
            self.update_executable_window(signal)
            window = self.executable_windows.get(self.market_side_key(ticker, side))
            if window and window.active and window.since_monotonic is not None:
                signal.first_executable_at_monotonic = window.since_monotonic
                signal.executable_window_ms = (time.monotonic() - window.since_monotonic) * 1000.0
            candidates.append((edge_cents, p_side, signal))
        if not candidates:
            return None
        _, _, selected = max(candidates, key=lambda item: (item[0], item[1]))
        self.logger.info(
            "Mushroom v28 entry approved | market=%s side=%s ask=%sc max_buy=%sc qty=%s p_side=%.4f edge=%.3fc depth=%s btc_age_ms=%s secs_to_close=%s",
            selected.market_ticker,
            selected.side,
            selected.trigger_price_cents,
            selected.model_max_buy_price_cents,
            selected.target_count,
            float(selected.mushroom_shadow.get("mushroom_v28_p_side") or 0.0),
            float(selected.mushroom_shadow.get("mushroom_v28_edge_cents") or 0.0),
            format_decimal_compact(selected.eligible_depth),
            selected.mushroom_shadow.get("mushroom_v28_btc_age_ms"),
            f"{selected.seconds_to_close:.2f}" if selected.seconds_to_close is not None else "NA",
        )
        self.telemetry.emit(
            "mushroom_v28_approved",
            self.telemetry_context_from_signal(selected),
            **self.mushroom_telemetry_fields(selected),
            **self.orderbook.telemetry_fields(),
        )
        return selected

    def liquidity_dwell_mushroom_fields(self, candidate: LiquidityDwellCandidate) -> dict[str, Any]:
        top_of_book_limit = self.orderbook.top_of_book_buy_limit_cents(candidate.side)
        executable_limit = self.orderbook.executable_buy_limit_cents(candidate.side, self.config.position_size)
        entry_limit = executable_limit if executable_limit is not None else top_of_book_limit
        if entry_limit is None:
            entry_limit = candidate.initial_trigger_price_cents
        eligible_depth = self.orderbook.executable_buy_depth(candidate.side, int(entry_limit))
        elapsed_ms = max(0.0, (time.monotonic() - candidate.first_seen_monotonic) * 1000.0)
        signal = EntrySignal(
            market_ticker=candidate.market_ticker,
            side=candidate.side,
            trigger_price_cents=int(entry_limit),
            cap_price_cents=int(top_of_book_limit if top_of_book_limit is not None else entry_limit),
            top_of_book_limit_cents=top_of_book_limit,
            executable_limit_cents=int(entry_limit),
            eligible_depth=eligible_depth,
            book_age_ms=self.current_book_age_ms(),
            seconds_to_close=self.seconds_to_close(),
            book_summary=self.describe_live_buy_book(candidate.side),
            yes_ask_cents=self.current_entry_ask_cents("yes"),
            no_ask_cents=self.current_entry_ask_cents("no"),
            signal_signature=f"liquidity_dwell_candidate|initial={candidate.initial_trigger_price_cents}|entry_limit={entry_limit}",
            first_executable_at_monotonic=candidate.first_seen_monotonic,
            executable_window_ms=elapsed_ms,
        )
        self.attach_mushroom_shadow(signal)
        return self.mushroom_telemetry_fields(signal)

    def liquidity_dwell_candidate_key(self, ticker: str, side: str) -> str:
        return f"{normalize_ticker(ticker)}:{side}"

    def liquidity_dwell_quote_point_from_row(
        self,
        row: dict[str, Any],
        side: str,
        first_seen_monotonic: float,
    ) -> dict[str, float] | None:
        try:
            ts_mono = float(row.get("ts_mono"))
        except (TypeError, ValueError):
            return None
        if side == "yes":
            own_bid_raw = row.get("yes_bid")
            opp_bid_raw = row.get("no_bid")
            held_ask_raw = row.get("yes_ask")
        else:
            own_bid_raw = row.get("no_bid")
            opp_bid_raw = row.get("yes_bid")
            held_ask_raw = row.get("no_ask")
        try:
            own_bid = float(own_bid_raw)
            opp_bid = float(opp_bid_raw)
            held_ask = float(held_ask_raw)
        except (TypeError, ValueError):
            return None
        if any(math.isnan(value) for value in (own_bid, opp_bid, held_ask)):
            return None
        bid_sum = own_bid + opp_bid
        pressure = opp_bid / bid_sum if bid_sum > 0 else math.nan
        return {
            "elapsed": max(0.0, ts_mono - first_seen_monotonic),
            "own_bid": own_bid,
            "opp_bid": opp_bid,
            "held_ask": held_ask,
            "bid_sum": bid_sum,
            "spread": held_ask - own_bid,
            "pressure": pressure,
        }

    def liquidity_dwell_history_points(self, candidate: LiquidityDwellCandidate) -> list[dict[str, float]]:
        rows = [
            row for row in self.recent_price_history
            if row.get("market") == candidate.market_ticker
            and row.get("ts_mono") is not None
            and float(row.get("ts_mono")) >= candidate.first_seen_monotonic
        ]
        points = [
            point for point in (
                self.liquidity_dwell_quote_point_from_row(row, candidate.side, candidate.first_seen_monotonic)
                for row in rows
            )
            if point is not None
        ]
        return sorted(points, key=lambda point: point["elapsed"])

    def liquidity_dwell_quote_gate(self, point: dict[str, float]) -> bool:
        values = (point.get("held_ask"), point.get("pressure"), point.get("bid_sum"), point.get("spread"))
        if any(value is None or math.isnan(float(value)) for value in values):
            return False
        return (
            float(point["held_ask"]) <= float(self.config.liquidity_dwell_max_entry_ask)
            and float(point["pressure"]) <= float(self.config.liquidity_dwell_max_opp_pressure)
            and float(point["bid_sum"]) >= float(self.config.liquidity_dwell_min_bid_sum)
            and float(point["spread"]) <= float(self.config.liquidity_dwell_max_spread)
        )

    def liquidity_dwell_quality_seconds(self, points: list[dict[str, float]]) -> float:
        total = 0.0
        for idx in range(1, len(points)):
            prev = points[idx - 1]
            cur = points[idx]
            dt = max(0.0, float(cur["elapsed"]) - float(prev["elapsed"]))
            if self.liquidity_dwell_quote_gate(prev):
                total += dt
        return total

    def arm_liquidity_dwell_candidates(self, ticker: str) -> None:
        target = int(self.config.target_entry_odds_cents)
        triggered: list[tuple[str, int]] = []
        for side in ("yes", "no"):
            held_ask = self.current_entry_ask_cents(side)
            if held_ask is not None and held_ask >= target:
                triggered.append((side, int(held_ask)))
        if len(triggered) != 1:
            return
        side, trigger_price = triggered[0]
        if self.entry_block_reason(ticker, side, self.config.position_size):
            return
        key = self.liquidity_dwell_candidate_key(ticker, side)
        if key in self.liquidity_dwell_candidates:
            return
        seconds_to_close = self.seconds_to_close()
        delay = float(self.config.liquidity_dwell_delay_seconds)
        if seconds_to_close is not None and seconds_to_close <= delay + float(self.config.live_entry_skip_seconds_to_close):
            return
        now_mono = time.monotonic()
        self.liquidity_dwell_candidates[key] = LiquidityDwellCandidate(
            market_ticker=ticker,
            side=side,
            first_seen_monotonic=now_mono,
            first_seen_wall=utc_now().isoformat(),
            initial_trigger_price_cents=trigger_price,
            last_wait_log_monotonic=now_mono,
        )
        self.record_price_history_point(force=True)
        self.logger.info(
            "Liquidity dwell armed | market=%s side=%s initial_trigger=%sc delay=%.1fs max_entry_ask=%sc max_opp_pressure=%.3f min_quality_share=%.3f",
            ticker,
            side,
            trigger_price,
            delay,
            int(self.config.liquidity_dwell_max_entry_ask),
            float(self.config.liquidity_dwell_max_opp_pressure),
            float(self.config.liquidity_dwell_min_quality_share),
        )

    def reject_liquidity_dwell_candidate(self, candidate: LiquidityDwellCandidate, reason: str, **extra: Any) -> None:
        key = self.liquidity_dwell_candidate_key(candidate.market_ticker, candidate.side)
        self.liquidity_dwell_candidates.pop(key, None)
        mushroom_fields = self.liquidity_dwell_mushroom_fields(candidate)
        self.logger.info(
            "Liquidity dwell rejected | market=%s side=%s reason=%s initial_trigger=%sc %s",
            candidate.market_ticker,
            candidate.side,
            reason,
            candidate.initial_trigger_price_cents,
            " ".join(f"{name}={value}" for name, value in extra.items()),
        )
        self.telemetry.emit(
            "liquidity_dwell_rejected",
            ExecutionTelemetryContext(
                market=candidate.market_ticker,
                purpose="entry",
                side=candidate.side,
                trigger_price_cents=candidate.initial_trigger_price_cents,
                position_size=self.config.position_size,
                decision_reason=reason,
            ),
            **extra,
            **mushroom_fields,
            **self.orderbook.telemetry_fields(),
        )

    def detect_liquidity_dwell_entry_signal(self) -> EntrySignal | None:
        ticker = self.current_watch_ticker
        if not ticker or not self.orderbook.snapshot_ready:
            return None
        self.arm_liquidity_dwell_candidates(ticker)
        if not self.liquidity_dwell_candidates:
            return None
        self.record_price_history_point(force=True)
        now_mono = time.monotonic()
        delay = float(self.config.liquidity_dwell_delay_seconds)
        for key, candidate in list(self.liquidity_dwell_candidates.items()):
            if normalize_ticker(candidate.market_ticker) != normalize_ticker(ticker):
                self.liquidity_dwell_candidates.pop(key, None)
                continue
            if self.entry_block_reason(ticker, candidate.side, self.config.position_size):
                self.liquidity_dwell_candidates.pop(key, None)
                continue
            elapsed = now_mono - candidate.first_seen_monotonic
            if elapsed < delay:
                if now_mono - candidate.last_wait_log_monotonic >= 15.0:
                    candidate.last_wait_log_monotonic = now_mono
                    self.logger.info(
                        "Liquidity dwell waiting | market=%s side=%s elapsed=%.1fs delay=%.1fs",
                        candidate.market_ticker,
                        candidate.side,
                        elapsed,
                        delay,
                    )
                continue
            points = self.liquidity_dwell_history_points(candidate)
            if not points or points[-1]["elapsed"] < delay:
                self.reject_liquidity_dwell_candidate(candidate, "insufficient_quote_history", points=len(points))
                continue
            final = points[-1]
            top_of_book_limit = self.orderbook.top_of_book_buy_limit_cents(candidate.side)
            executable_limit = self.orderbook.executable_buy_limit_cents(candidate.side, self.config.position_size)
            entry_limit = executable_limit if executable_limit is not None else top_of_book_limit
            if entry_limit is None:
                self.reject_liquidity_dwell_candidate(candidate, "missing_executable_limit")
                continue
            if entry_limit > int(self.config.liquidity_dwell_max_entry_ask):
                self.reject_liquidity_dwell_candidate(candidate, "entry_limit_above_dwell_max", entry_limit=entry_limit)
                continue
            if not self.liquidity_dwell_quote_gate(final):
                self.reject_liquidity_dwell_candidate(
                    candidate,
                    "final_quote_gate_failed",
                    held_ask=round(float(final["held_ask"]), 3),
                    pressure=round(float(final["pressure"]), 6),
                    bid_sum=round(float(final["bid_sum"]), 3),
                    spread=round(float(final["spread"]), 3),
                )
                continue
            dwell_seconds = self.liquidity_dwell_quality_seconds(points)
            elapsed_span = max(1.0, float(final["elapsed"]) - float(points[0]["elapsed"]))
            dwell_share = dwell_seconds / elapsed_span
            if dwell_seconds < float(self.config.liquidity_dwell_min_quality_seconds) or dwell_share < float(self.config.liquidity_dwell_min_quality_share):
                self.reject_liquidity_dwell_candidate(
                    candidate,
                    "insufficient_liquidity_dwell",
                    quality_seconds=round(dwell_seconds, 3),
                    quality_share=round(dwell_share, 6),
                    points=len(points),
                )
                continue
            rejection_state = self.entry_rejection_state.get(f"{normalize_ticker(ticker)}:{candidate.side}")
            if rejection_state and time.monotonic() < rejection_state.block_until_monotonic:
                return None
            eligible_depth = self.orderbook.executable_buy_depth(candidate.side, entry_limit)
            signal_signature = "|".join([
                "liquidity_dwell",
                f"initial={candidate.initial_trigger_price_cents}",
                f"entry_limit={entry_limit}",
                f"quality_seconds={round(dwell_seconds, 3)}",
                f"quality_share={round(dwell_share, 6)}",
                f"pressure={round(float(final['pressure']), 6)}",
                f"spread={round(float(final['spread']), 3)}",
                f"depth={format_decimal_compact(eligible_depth)}",
                f"trust={self.orderbook.trust.trust_state}",
            ])
            signal = EntrySignal(
                market_ticker=ticker,
                side=candidate.side,
                trigger_price_cents=int(entry_limit),
                cap_price_cents=int(top_of_book_limit if top_of_book_limit is not None else entry_limit),
                top_of_book_limit_cents=top_of_book_limit,
                executable_limit_cents=entry_limit,
                eligible_depth=eligible_depth,
                book_age_ms=self.current_book_age_ms(),
                seconds_to_close=self.seconds_to_close(),
                book_summary=self.describe_live_buy_book(candidate.side),
                yes_ask_cents=self.current_entry_ask_cents("yes"),
                no_ask_cents=self.current_entry_ask_cents("no"),
                signal_signature=signal_signature,
                first_executable_at_monotonic=candidate.first_seen_monotonic,
                executable_window_ms=elapsed * 1000.0,
            )
            self.liquidity_dwell_candidates.pop(key, None)
            self.attach_mushroom_shadow(signal)
            self.logger.info(
                "Liquidity dwell approved | market=%s side=%s initial_trigger=%sc entry_limit=%sc quality_seconds=%.3f quality_share=%.3f pressure=%.3f spread=%.3f depth=%s",
                ticker,
                candidate.side,
                candidate.initial_trigger_price_cents,
                entry_limit,
                dwell_seconds,
                dwell_share,
                float(final["pressure"]),
                float(final["spread"]),
                format_decimal_compact(eligible_depth),
            )
            self.telemetry.emit(
                "liquidity_dwell_approved",
                self.telemetry_context_from_signal(signal),
                initial_trigger_price_cents=candidate.initial_trigger_price_cents,
                quality_seconds=round(dwell_seconds, 3),
                quality_share=round(dwell_share, 6),
                pressure=round(float(final["pressure"]), 6),
                spread=round(float(final["spread"]), 3),
                bid_sum=round(float(final["bid_sum"]), 3),
                **self.mushroom_telemetry_fields(signal),
                **self.orderbook.telemetry_fields(),
            )
            return signal
        return None

    def detect_entry_signal(self) -> EntrySignal | None:
        if self.config.mushroom_v28_decision_engine_enabled:
            return self.detect_mushroom_v28_entry_signal()
        if self.config.mushroom_v21_decision_engine_enabled:
            return self.detect_mushroom_v21_entry_signal()
        if self.config.liquidity_dwell_entry_enabled:
            return self.detect_liquidity_dwell_entry_signal()
        ticker = self.current_watch_ticker
        if not ticker or not self.orderbook.snapshot_ready:
            return None
        yes_ask = self.market.yes_ask_cents
        no_ask = self.market.no_ask_cents
        if yes_ask is None:
            no_bid_book, _ = self.orderbook.best_bid("no")
            if no_bid_book is not None:
                yes_ask = 100 - no_bid_book
            elif self.market.no_bid_cents is not None:
                yes_ask = 100 - self.market.no_bid_cents
        if no_ask is None:
            yes_bid_book, _ = self.orderbook.best_bid("yes")
            if yes_bid_book is not None:
                no_ask = 100 - yes_bid_book
            elif self.market.yes_bid_cents is not None:
                no_ask = 100 - self.market.yes_bid_cents
        if yes_ask is None and no_ask is None:
            return None
        triggered: list[tuple[str, int]] = []
        if yes_ask is not None and yes_ask >= self.config.target_entry_odds_cents:
            triggered.append(("yes", yes_ask))
        if no_ask is not None and no_ask >= self.config.target_entry_odds_cents:
            triggered.append(("no", no_ask))
        triggered = [
            (side, ask)
            for side, ask in triggered
            if self.entry_block_reason(ticker, side, self.config.position_size) is None
        ]
        if len(triggered) != 1:
            return None
        side, trigger_price = triggered[0]
        rejection_state = self.entry_rejection_state.get(f"{normalize_ticker(ticker)}:{side}")
        if rejection_state and time.monotonic() < rejection_state.block_until_monotonic:
            return None
        top_of_book_limit = self.orderbook.top_of_book_buy_limit_cents(side)
        executable_limit = self.orderbook.executable_buy_limit_cents(side, self.config.position_size)
        eligible_limit = executable_limit if executable_limit is not None else top_of_book_limit
        eligible_depth = Decimal("0")
        if eligible_limit is not None:
            eligible_depth = self.orderbook.executable_buy_depth(side, eligible_limit)
        book_age_ms = self.current_book_age_ms()
        signal_signature = "|".join([
            f"trigger={trigger_price}",
            f"yes={yes_ask}",
            f"no={no_ask}",
            f"top={top_of_book_limit}",
            f"exec={executable_limit}",
            f"depth={format_decimal_compact(eligible_depth)}",
            f"trust={self.orderbook.trust.trust_state}",
        ])
        signal = EntrySignal(
            market_ticker=ticker,
            side=side,
            trigger_price_cents=trigger_price,
            cap_price_cents=self.config.target_entry_odds_cents,
            top_of_book_limit_cents=top_of_book_limit,
            executable_limit_cents=executable_limit,
            eligible_depth=eligible_depth,
            book_age_ms=book_age_ms,
            seconds_to_close=self.seconds_to_close(),
            book_summary=self.describe_live_buy_book(side),
            yes_ask_cents=yes_ask,
            no_ask_cents=no_ask,
            signal_signature=signal_signature,
        )
        self.update_executable_window(signal)
        window = self.executable_windows.get(self.market_side_key(ticker, side))
        if window and window.active and window.since_monotonic is not None:
            signal.first_executable_at_monotonic = window.since_monotonic
            signal.executable_window_ms = (time.monotonic() - window.since_monotonic) * 1000.0
        return signal

    def evaluate_pre_entry_filters(self, signal: EntrySignal) -> FilterDecision:
        if not self.config.pre_entry_stddev_filter_enabled:
            self.transition_execution_state(signal.market_ticker, signal.side, "eligible", "pre_filters_disabled", signal.signal_signature)
            return FilterDecision(True, "pre_filters_disabled")
        values = self.get_pre_entry_stddev_series(signal.side)
        need = int(self.config.pre_entry_stddev_lookback_points)
        if len(values) < need:
            self.note_entry_skip(
                signal.market_ticker,
                signal.side,
                "pre_stddev_insufficient_history",
                f"std:insufficient:{len(values)}:{need}:{signal.trigger_price_cents}",
                0.75,
                "Entry blocked by pre-entry std-dev filter | market=%s side=%s trigger=%s reason=insufficient_history obs=%s need=%s",
                signal.market_ticker,
                signal.side,
                signal.trigger_price_cents,
                len(values),
                need,
            )
            self.transition_execution_state(signal.market_ticker, signal.side, "blocked_filter", "pre_stddev_insufficient_history", signal.signal_signature)
            return FilterDecision(False, "pre_stddev_insufficient_history", std_obs=len(values))
        pre_std = float(np.std(np.array(values, dtype=float), ddof=0))
        if pre_std < float(self.config.pre_entry_stddev_threshold):
            self.note_entry_skip(
                signal.market_ticker,
                signal.side,
                "pre_stddev_below_threshold",
                f"std:threshold:{round(pre_std, 3)}:{len(values)}:{signal.trigger_price_cents}",
                0.75,
                "Entry blocked by pre-entry std-dev filter | market=%s side=%s trigger=%s pre_std=%.3f threshold=%.3f obs=%s",
                signal.market_ticker,
                signal.side,
                signal.trigger_price_cents,
                pre_std,
                self.config.pre_entry_stddev_threshold,
                len(values),
            )
            self.transition_execution_state(signal.market_ticker, signal.side, "blocked_filter", "pre_stddev_below_threshold", signal.signal_signature)
            return FilterDecision(False, "pre_stddev_below_threshold", pre_std=pre_std, pre_std_threshold=self.config.pre_entry_stddev_threshold, std_obs=len(values))
        self.clear_entry_skip_state(signal.market_ticker, signal.side)
        self.log_filter_decision(
            f"pass:{signal.market_ticker}:{signal.side}:{round(pre_std, 3)}",
            "Entry passed pre-entry std-dev filter | market=%s side=%s trigger=%s pre_std=%.3f threshold=%.3f obs=%s",
            signal.market_ticker,
            signal.side,
            signal.trigger_price_cents,
            pre_std,
            self.config.pre_entry_stddev_threshold,
            len(values),
        )
        self.transition_execution_state(signal.market_ticker, signal.side, "eligible", "pre_filters_passed", signal.signal_signature)
        return FilterDecision(True, "pre_filters_passed", pre_std=pre_std, pre_std_threshold=self.config.pre_entry_stddev_threshold, std_obs=len(values))

    def passes_pre_entry_filters(self, *, ticker: str, side: str, trigger_price: int) -> bool:
        signal = EntrySignal(
            market_ticker=ticker,
            side=side,
            trigger_price_cents=trigger_price,
            cap_price_cents=self.config.target_entry_odds_cents,
            top_of_book_limit_cents=self.orderbook.top_of_book_buy_limit_cents(side),
            executable_limit_cents=self.orderbook.executable_buy_limit_cents(side, self.config.position_size),
            eligible_depth=Decimal("0"),
            book_age_ms=self.current_book_age_ms(),
            seconds_to_close=self.seconds_to_close(),
            book_summary=self.describe_live_buy_book(side),
            yes_ask_cents=self.market.yes_ask_cents,
            no_ask_cents=self.market.no_ask_cents,
            signal_signature=f"compat:{ticker}:{side}:{trigger_price}",
        )
        return self.evaluate_pre_entry_filters(signal).allowed

    def get_pre_entry_stddev_series(self, side: str) -> list[float]:
        ask_key = "yes_ask" if side == "yes" else "no_ask"
        values = [
            float(row[ask_key])
            for row in self.recent_price_history
            if row.get("market") == self.current_watch_ticker and row.get(ask_key) is not None
        ]
        return values[-int(self.config.pre_entry_stddev_lookback_points):]

    def log_filter_decision(self, key: str, message: str, *args: Any) -> None:
        now_mono = time.monotonic()
        if key != self.last_filter_log_key or (now_mono - self.last_filter_log_monotonic) >= 5.0:
            self.logger.info(message, *args)
            self.last_filter_log_key = key
            self.last_filter_log_monotonic = now_mono

    def entry_skip_key(self, ticker: str, side: str) -> str:
        return f"{normalize_ticker(ticker)}:{side}"

    def clear_entry_skip_state(self, ticker: str, side: str) -> None:
        self.entry_skip_state.pop(self.entry_skip_key(ticker, side), None)

    def should_defer_entry_check(self, *, ticker: str, side: str, signature: str) -> bool:
        state = self.entry_skip_state.get(self.entry_skip_key(ticker, side))
        if state is None:
            return False
        if state.last_signature != signature:
            return False
        return time.monotonic() < state.block_until_monotonic

    def note_entry_skip(self, ticker: str, side: str, reason: str, signature: str, cooldown_seconds: float, message: str, *args: Any) -> None:
        key = self.entry_skip_key(ticker, side)
        now_mono = time.monotonic()
        state = self.entry_skip_state.get(key, EntrySkipState())
        should_log = (
            state.last_reason != reason
            or state.last_signature != signature
            or now_mono >= state.block_until_monotonic
        )
        state.last_reason = reason
        state.last_signature = signature
        state.block_until_monotonic = now_mono + max(0.0, cooldown_seconds)
        self.entry_skip_state[key] = state
        if should_log:
            self.logger.info(message, *args)

    def coarse_blocked_signal_signature(self, signal: EntrySignal, *, reason: str, extra: dict[str, Any] | None = None) -> str:
        tick = max(1, int(self.config.live_entry_material_book_change_ticks))
        depth_bucket = max(1, int(self.config.live_entry_stale_depth_change_contracts))
        top_limit = signal.top_of_book_limit_cents if signal.top_of_book_limit_cents is not None else -1
        executable_limit = signal.executable_limit_cents if signal.executable_limit_cents is not None else -1
        if top_limit >= 0:
            top_limit = (top_limit // tick) * tick
        if executable_limit >= 0:
            executable_limit = (executable_limit // tick) * tick
        depth_int = max(0, decimal_to_int(signal.eligible_depth) or 0)
        depth_int = (depth_int // depth_bucket) * depth_bucket
        parts = [
            reason,
            f"top={top_limit}",
            f"exec={executable_limit}",
            f"depth={depth_int}",
            f"trust={self.orderbook.trust.trust_state}",
        ]
        seconds_to_close = signal.seconds_to_close
        if seconds_to_close is not None:
            seconds_bucket = int(max(0.0, seconds_to_close) // 5) * 5
            parts.append(f"secs={seconds_bucket}")
        if extra:
            if "gate_executable_window_ms" in extra:
                window_bucket = int(max(0.0, float(extra["gate_executable_window_ms"])) // 100) * 100
                parts.append(f"window={window_bucket}")
            if "gate_net_edge_cents" in extra:
                parts.append(f"net={int(extra['gate_net_edge_cents'])}")
            if "gate_min_net_edge_cents" in extra:
                parts.append(f"min_net={int(extra['gate_min_net_edge_cents'])}")
        return "|".join(parts)

    def stale_book_signature(self, signal: EntrySignal) -> str:
        return self.coarse_blocked_signal_signature(signal, reason="stale_book")

    def should_suppress_stale_book(self, signal: EntrySignal) -> bool:
        if self.config.dry_run:
            return False
        max_book_age_ms = self.allowed_live_book_age_ms(signal.seconds_to_close)
        if signal.book_age_ms is None or signal.book_age_ms <= max_book_age_ms:
            self.clear_entry_skip_state(signal.market_ticker, signal.side)
            return False
        signature = self.stale_book_signature(signal)
        if self.should_defer_entry_check(ticker=signal.market_ticker, side=signal.side, signature=signature):
            return True
        cooldown_seconds = max(0.0, float(self.config.live_entry_stale_suppression_ms) / 1000.0)
        self.note_entry_skip(
            signal.market_ticker,
            signal.side,
            "stale_book",
            signature,
            cooldown_seconds,
            "Entry deferred early for stale book | market=%s side=%s trigger=%s top_of_book=%s book_age_ms=%.1f max_book_age_ms=%.1f trust=%s",
            signal.market_ticker,
            signal.side,
            signal.trigger_price_cents,
            signal.top_of_book_limit_cents,
            float(signal.book_age_ms),
            float(max_book_age_ms),
            self.orderbook.trust.trust_state,
        )
        self.market_outcomes.mark_stale_deferral(signal.market_ticker)
        self.transition_execution_state(signal.market_ticker, signal.side, "abandoned", "stale_book", signal.signal_signature)
        self.telemetry.emit(
            "execution_deferred",
            self.telemetry_context_from_signal(signal),
            result="stale_book",
            account_age_ms=self.account_snapshot_age_ms(),
            early_gate=True,
            max_book_age_ms=max_book_age_ms,
            **self.mushroom_telemetry_fields(signal),
            **self.orderbook.telemetry_fields(),
        )
        return True

    def build_execution_plan(self, signal: EntrySignal, filter_decision: FilterDecision) -> ExecutionPlan | None:
        target_count = max(1, min(int(self.config.position_size), int(signal.target_count or self.config.position_size)))
        if not self.config.dry_run and self.orderbook.trust.trust_state != "synced":
            self.defer_execution(signal, "book_untrusted", filter_decision)
            self.transition_execution_state(signal.market_ticker, signal.side, "blocked_book_untrusted", "book_untrusted", signal.signal_signature)
            return None
        if signal.top_of_book_limit_cents is None or signal.top_of_book_limit_cents < signal.cap_price_cents:
            self.defer_execution(signal, "cap_not_marketable", filter_decision)
            return None
        executable_limit = signal.executable_limit_cents
        if executable_limit is None and self.config.live_entry_allow_ioc and signal.top_of_book_limit_cents >= signal.cap_price_cents:
            executable_limit = signal.top_of_book_limit_cents
        if executable_limit is None:
            self.defer_execution(signal, "insufficient_visible_depth", filter_decision)
            return None
        if executable_limit < signal.cap_price_cents:
            self.defer_execution(signal, "executable_below_threshold", filter_decision)
            return None
        if signal.model_max_buy_price_cents is not None and executable_limit > int(signal.model_max_buy_price_cents):
            self.defer_execution(
                signal,
                "model_price_cap_exceeded",
                model_max_buy_price_cents=int(signal.model_max_buy_price_cents),
                executable_limit_cents=executable_limit,
            )
            return None
        fill_plan = self.build_live_entry_plan(signal=signal)
        if fill_plan is None:
            return None
        return ExecutionPlan(
            market_ticker=signal.market_ticker,
            side=signal.side,
            trigger_price_cents=signal.trigger_price_cents,
            cap_price_cents=signal.cap_price_cents,
            total_count=target_count,
            eligible_depth=fill_plan.eligible_depth,
            depth_required=fill_plan.depth_required,
            book_age_ms=fill_plan.book_age_ms,
            seconds_to_close=fill_plan.seconds_to_close,
            time_in_force=fill_plan.time_in_force,
            limit_price_cents=fill_plan.limit_price_cents,
            mode=fill_plan.mode,
            reason=fill_plan.reason,
            top_of_book_limit_cents=signal.top_of_book_limit_cents,
            book_summary=signal.book_summary,
            signal_signature=signal.signal_signature,
            account_age_ms=self.account_snapshot_age_ms(),
            executable_window_ms=signal.executable_window_ms,
            model_max_buy_price_cents=signal.model_max_buy_price_cents,
            mushroom_shadow=dict(signal.mushroom_shadow),
            slices=self.build_slice_plans(fill_plan),
        )

    def build_live_entry_plan(self, *, signal: EntrySignal) -> LiveFillPlan | None:
        ticker = signal.market_ticker
        side = signal.side
        target_count = max(1, min(int(self.config.position_size), int(signal.target_count or self.config.position_size)))
        book_age_ms = signal.book_age_ms
        seconds_to_close = signal.seconds_to_close
        max_book_age_ms = self.allowed_live_book_age_ms(seconds_to_close)
        if book_age_ms is None:
            self.defer_execution(signal, "missing_book_age")
            return None
        if seconds_to_close is not None and seconds_to_close <= self.config.live_entry_skip_seconds_to_close:
            self.defer_execution(signal, "too_close_to_expiry")
            return None
        if book_age_ms > max_book_age_ms:
            self.defer_execution(signal, "stale_book")
            return None
        account_age_ms = self.account_snapshot_age_ms()
        if not self.config.dry_run:
            if self.live_account_snapshot.available_balance_cents is None or account_age_ms is None:
                self.defer_execution(signal, "missing_account_state")
                return None
            if account_age_ms > self.config.live_account_state_max_age_ms:
                self.defer_execution(signal, "missing_account_state")
                return None
            worst_case_cost_cents = int(signal.executable_limit_cents or signal.top_of_book_limit_cents or signal.cap_price_cents) * target_count
            required_available_cents = (
                worst_case_cost_cents
                + int(self.config.live_balance_fee_buffer_cents)
                + int(self.config.live_balance_min_buffer_cents)
            )
            if (self.live_account_snapshot.available_balance_cents or 0) < required_available_cents:
                self.defer_execution(signal, "insufficient_balance")
                return None
            blocking_resting_orders = [
                order for order in self.live_account_snapshot.resting_orders
                if normalize_ticker(str(order.get("ticker", ""))) == normalize_ticker(ticker)
            ]
            if blocking_resting_orders:
                self.defer_execution(signal, "resting_order_conflict")
                return None
        size = Decimal(str(target_count))
        executable_limit = signal.executable_limit_cents or signal.top_of_book_limit_cents or signal.cap_price_cents
        if signal.model_max_buy_price_cents is not None and int(executable_limit) > int(signal.model_max_buy_price_cents):
            self.defer_execution(
                signal,
                "model_price_cap_exceeded",
                model_max_buy_price_cents=int(signal.model_max_buy_price_cents),
                executable_limit_cents=int(executable_limit),
            )
            return None
        eligible_depth = self.orderbook.executable_buy_depth(side, executable_limit)
        cushion = self.required_depth_cushion(
            trigger_price=signal.trigger_price_cents,
            executable_limit=executable_limit,
            seconds_to_close=seconds_to_close,
        )
        depth_required = size + Decimal(str(cushion))
        min_visible_depth = Decimal(str(max(0, int(self.config.live_entry_min_visible_depth_for_ioc))))
        if eligible_depth < min_visible_depth:
            self.defer_execution(signal, "insufficient_visible_depth")
            return None
        if self.config.live_entry_fast_fill_gate_enabled:
            gate_metrics = self.fast_fill_gate_metrics(
                signal=signal,
                executable_limit=executable_limit,
                eligible_depth=eligible_depth,
                depth_required=depth_required,
                target_count=target_count,
            )
            min_seconds_to_close = float(self.config.live_entry_fast_fill_min_seconds_to_close)
            if signal.seconds_to_close is not None and signal.seconds_to_close <= min_seconds_to_close:
                self.defer_execution(
                    signal,
                    "fast_fill_late_window",
                    gate_seconds_to_close=signal.seconds_to_close,
                    gate_min_seconds_to_close=min_seconds_to_close,
                    gate_executable_window_ms=gate_metrics["executable_window_ms"],
                )
                return None
            min_depth_contracts = Decimal(str(max(0, int(self.config.live_entry_fast_fill_min_depth_contracts))))
            if eligible_depth < min_depth_contracts:
                self.defer_execution(
                    signal,
                    "fast_fill_insufficient_depth",
                    gate_min_depth_contracts=str(min_depth_contracts),
                    gate_eligible_depth=str(eligible_depth),
                )
                return None
            min_window_ms = float(self.config.live_entry_fast_fill_min_window_ms)
            if gate_metrics["executable_window_ms"] < min_window_ms:
                self.defer_execution(
                    signal,
                    "fast_fill_window_too_short",
                    gate_executable_window_ms=gate_metrics["executable_window_ms"],
                    gate_min_window_ms=min_window_ms,
                )
                return None
            min_net_edge_cents = int(self.config.live_entry_fast_fill_min_net_edge_cents)
            if gate_metrics["net_edge_cents"] < min_net_edge_cents:
                self.defer_execution(
                    signal,
                    "fast_fill_net_edge_too_small",
                    gate_gross_edge_cents=gate_metrics["gross_edge_cents"],
                    gate_net_edge_cents=gate_metrics["net_edge_cents"],
                    gate_min_net_edge_cents=min_net_edge_cents,
                    gate_estimated_round_trip_fee_cents=gate_metrics["estimated_round_trip_fee_cents"],
                    gate_estimated_round_trip_fee_cents_per_contract=gate_metrics["estimated_round_trip_fee_cents_per_contract"],
                    gate_slippage_budget_cents=gate_metrics["slippage_budget_cents"],
                )
                return None
        default_tif = self.config.live_entry_default_tif
        if self.config.live_entry_ioc_first:
            default_tif = "immediate_or_cancel"
        if default_tif not in {"immediate_or_cancel", "fill_or_kill"}:
            default_tif = "immediate_or_cancel"
        single_order_depth_multiple = max(1.0, float(self.config.live_entry_single_order_depth_multiple))
        if default_tif == "fill_or_kill" and self.config.live_entry_allow_fok_when_full_depth and eligible_depth >= depth_required:
            tif = "fill_or_kill"
            mode = "aggressive_full"
            reason = "full_depth_fok"
        elif eligible_depth >= (size * Decimal(str(single_order_depth_multiple))):
            tif = "immediate_or_cancel"
            mode = "aggressive_full"
            reason = "single_shot_abundant_depth"
        else:
            tif = "immediate_or_cancel"
            mode = "aggressive_partial_ok"
            reason = "ioc_first" if eligible_depth >= size else "ioc_partial_visible_depth"
        self.clear_entry_skip_state(ticker, side)
        self.logger.info(
            "Live fill policy approved | market=%s side=%s trigger=%sc tif=%s limit=%sc depth=%s required=%s book_age_ms=%.1f secs_to_close=%s reason=%s",
            ticker,
            side,
            signal.trigger_price_cents,
            tif,
            executable_limit,
            str(eligible_depth),
            str(depth_required),
            book_age_ms,
            f"{seconds_to_close:.2f}" if seconds_to_close is not None else "NA",
            reason,
        )
        return LiveFillPlan(
            mode=mode,
            time_in_force=tif,
            limit_price_cents=executable_limit,
            target_count=target_count,
            eligible_depth=eligible_depth,
            depth_required=depth_required,
            book_age_ms=book_age_ms,
            seconds_to_close=seconds_to_close,
            reason=reason,
        )

    def build_slice_plans(self, fill_plan: LiveFillPlan) -> list[SlicePlan]:
        total = max(1, int(fill_plan.target_count))
        limit_price_cents = fill_plan.limit_price_cents
        time_in_force = fill_plan.time_in_force
        if total <= 1 or self.config.dry_run or (not self.config.live_entry_slice_enabled) or time_in_force == "fill_or_kill":
            return [SlicePlan(slice_index=0, count=total, limit_price_cents=limit_price_cents, time_in_force=time_in_force, reason="single_order")]
        single_order_depth_multiple = max(1.0, float(self.config.live_entry_single_order_depth_multiple))
        if fill_plan.reason == "single_shot_abundant_depth" or fill_plan.eligible_depth >= (Decimal(str(total)) * Decimal(str(single_order_depth_multiple))):
            return [SlicePlan(slice_index=0, count=total, limit_price_cents=limit_price_cents, time_in_force=time_in_force, reason="single_order")]
        if self.config.live_entry_adaptive_slice_enabled:
            alpha = min(1.0, max(0.01, float(self.config.live_entry_adaptive_slice_alpha)))
            min_slice = max(1, int(self.config.live_entry_adaptive_slice_min_contracts))
            max_slice = max(min_slice, int(self.config.live_entry_adaptive_slice_max_contracts))
            visible_depth = max(0, decimal_to_int(fill_plan.eligible_depth) or 0)
            adaptive = int(visible_depth * alpha)
            slice_size = max(min_slice, min(max_slice, adaptive if adaptive > 0 else min_slice))
            slices: list[int] = []
            remaining = total
            while remaining > 0:
                take = min(slice_size, remaining)
                slices.append(take)
                remaining -= take
            return [
                SlicePlan(slice_index=idx, count=count, limit_price_cents=limit_price_cents, time_in_force=time_in_force, reason="adaptive_slice" if len(slices) > 1 else "single_order")
                for idx, count in enumerate(slices)
            ]
        pattern = [value for value in self.config.live_entry_slice_pattern if value > 0]
        if not pattern:
            pattern = [total]
        slices: list[int] = []
        remaining = total
        for value in pattern:
            if remaining <= 0:
                break
            take = min(value, remaining)
            slices.append(take)
            remaining -= take
        if remaining > 0:
            slices.append(remaining)
        if sum(slices) != total:
            slices = [total]
        return [
            SlicePlan(slice_index=idx, count=count, limit_price_cents=limit_price_cents, time_in_force=time_in_force, reason="slice" if len(slices) > 1 else "single_order")
            for idx, count in enumerate(slices)
        ]

    def entry_completion_limit_cents(self, side: str) -> int | None:
        current_top = self.orderbook.top_of_book_buy_limit_cents(side)
        if current_top is None:
            return None
        min_price = int(self.config.live_entry_partial_completion_min_price_cents)
        max_price = int(self.config.live_entry_partial_completion_max_price_cents)
        if current_top < min_price or current_top > max_price:
            return None
        return current_top

    def partial_entry_completion_is_valid(self, plan: ExecutionPlan) -> bool:
        if not self.config.live_entry_partial_completion_enabled:
            return False
        if normalize_ticker(self.current_watch_ticker or "") != normalize_ticker(plan.market_ticker):
            return False
        if not self.orderbook.snapshot_ready or self.orderbook.trust.trust_state != "synced":
            return False
        seconds_to_close = self.seconds_to_close()
        minimum_seconds = max(float(self.config.live_entry_skip_seconds_to_close), float(self.config.post_fill_exit_delay_seconds) + 5.0)
        if seconds_to_close is not None and seconds_to_close <= minimum_seconds:
            return False
        book_age_ms = self.current_book_age_ms()
        if book_age_ms is None or book_age_ms > self.allowed_live_book_age_ms(seconds_to_close):
            return False
        limit_cents = self.entry_completion_limit_cents(plan.side)
        if limit_cents is None:
            return False
        return self.orderbook.executable_buy_depth(plan.side, limit_cents) > 0

    async def continue_partial_entry_completion(
        self,
        plan: ExecutionPlan,
        filter_decision: FilterDecision,
        *,
        total_filled: int,
        first_order_id: str,
    ) -> tuple[int, str]:
        if total_filled <= 0 or total_filled >= plan.total_count or not self.config.live_entry_partial_completion_enabled:
            return total_filled, first_order_id
        deadline = time.monotonic() + max(0.0, float(self.config.live_entry_partial_completion_seconds))
        retry_delay_seconds = max(0.0, float(self.config.live_entry_partial_completion_retry_delay_ms) / 1000.0)
        attempt = 0
        while total_filled < plan.total_count and time.monotonic() < deadline:
            remaining = max(0, int(plan.total_count) - int(total_filled))
            if remaining <= 0 or not self.partial_entry_completion_is_valid(plan):
                break
            limit_cents = self.entry_completion_limit_cents(plan.side)
            if limit_cents is None:
                break
            attempt += 1
            self.logger.info(
                "ENTRY completion retry | market=%s side=%s already_filled=%s remaining=%s limit=%sc attempt=%s",
                plan.market_ticker,
                plan.side,
                total_filled,
                remaining,
                limit_cents,
                attempt,
            )
            completion_ctx = self.telemetry_context_from_plan(plan, filter_decision)
            self.telemetry.emit(
                "entry_completion_attempt",
                completion_ctx,
                already_filled_count=total_filled,
                remaining_target_count=remaining,
                completion_attempt=attempt,
                completion_limit_cents=limit_cents,
                account_age_ms=plan.account_age_ms,
                **self.orderbook.telemetry_fields(),
            )
            submission = await self.submit_single_order(
                purpose="entry",
                market_ticker=plan.market_ticker,
                side=plan.side,
                action="buy",
                count=remaining,
                limit_price_cents=limit_cents,
                trigger_price_cents=plan.trigger_price_cents,
                reduce_only=False,
                time_in_force="immediate_or_cancel",
                telemetry_context=completion_ctx,
            )
            if submission is None:
                break
            if not first_order_id and submission.order_id:
                first_order_id = submission.order_id
            if submission.error_text:
                self.note_entry_rejection(market_ticker=plan.market_ticker, side=plan.side, time_in_force="immediate_or_cancel", exc=RuntimeError(submission.error_text))
                break
            if submission.fill_count > 0:
                entry_fill_cents = submission.actual_fill_price_cents or limit_cents
                entry_fee_cents = (
                    submission.actual_fee_cents
                    if submission.actual_fee_cents is not None
                    else self.estimated_order_fee_cents(entry_fill_cents, submission.fill_count)
                )
                self.record_entry_fill_for_outcomes(
                    market_ticker=plan.market_ticker,
                    side=plan.side,
                    fill_count=submission.fill_count,
                    fill_price_cents=entry_fill_cents,
                    trigger_price_cents=plan.trigger_price_cents,
                    actual_fee_cents=submission.actual_fee_cents,
                )
                total_filled += submission.fill_count
                position = self.apply_entry_fill_to_position(
                    market_ticker=plan.market_ticker,
                    side=plan.side,
                    fill_count=submission.fill_count,
                    entry_order_id=submission.order_id or first_order_id or f"entry-{uuid.uuid4()}",
                    entry_limit_price_cents=limit_cents,
                    entry_fill_price_cents=entry_fill_cents,
                    entry_fee_cents=entry_fee_cents,
                    entry_trigger_price_cents=plan.trigger_price_cents,
                )
                if (
                    self.post_entry_shadow_watch is not None
                    and normalize_ticker(self.post_entry_shadow_watch.market_ticker) == normalize_ticker(plan.market_ticker)
                ):
                    self.post_entry_shadow_watch.entry_fill_cents = int(position.entry_fill_price_cents or entry_fill_cents)
                    self.post_entry_shadow_watch.entry_limit_cents = int(position.entry_limit_price_cents)
                self.save_state()
                self.telemetry.emit(
                    "fill_partial" if total_filled < plan.total_count else "fill_full",
                    self.telemetry_context_from_plan(plan, filter_decision, submission=submission),
                    cumulative_fill_count=total_filled,
                    completion_attempt=attempt,
                    account_age_ms=plan.account_age_ms,
                    **self.orderbook.telemetry_fields(),
                )
                self.logger.info(
                    "ENTRY completion fill | market=%s side=%s added=%s total=%s remaining=%s limit=%sc",
                    plan.market_ticker,
                    plan.side,
                    submission.fill_count,
                    total_filled,
                    max(0, plan.total_count - total_filled),
                    limit_cents,
                )
            if retry_delay_seconds > 0 and total_filled < plan.total_count:
                await asyncio.sleep(retry_delay_seconds)
        return total_filled, first_order_id

    def build_exit_slice_plans(self, plan: ExitPlan) -> list[SlicePlan]:
        total = int(plan.total_count)
        if total <= 1 or (not self.config.exit_adaptive_slice_enabled) or plan.recommended_mode != "adaptive_ioc_slices":
            return [SlicePlan(slice_index=0, count=total, limit_price_cents=plan.limit_price_cents, time_in_force=plan.time_in_force, reason="single_order")]
        alpha = min(1.0, max(0.01, float(self.config.exit_adaptive_slice_alpha)))
        min_slice = max(1, int(self.config.exit_adaptive_slice_min_contracts))
        max_slice = max(min_slice, int(self.config.exit_adaptive_slice_max_contracts))
        visible_depth = max(0, decimal_to_int(plan.eligible_depth) or 0)
        adaptive = int(visible_depth * alpha)
        slice_size = max(min_slice, min(max_slice, adaptive if adaptive > 0 else min_slice))
        if plan.full_size_available_at_limit and visible_depth >= int(total * max(1.0, float(self.config.exit_single_order_depth_multiple))):
            return [SlicePlan(slice_index=0, count=total, limit_price_cents=plan.limit_price_cents, time_in_force=plan.time_in_force, reason="single_order")]
        slices: list[int] = []
        remaining = total
        while remaining > 0:
            take = min(slice_size, remaining)
            slices.append(take)
            remaining -= take
        return [
            SlicePlan(slice_index=idx, count=count, limit_price_cents=plan.limit_price_cents, time_in_force=plan.time_in_force, reason="adaptive_exit_slice" if len(slices) > 1 else "single_order")
            for idx, count in enumerate(slices)
        ]

    def exit_slice_continuation_is_valid(self, plan: ExitPlan, slice_plan: SlicePlan) -> bool:
        if self.orderbook.trust.trust_state != "synced":
            return False
        book_age_ms = self.current_book_age_ms()
        if book_age_ms is None:
            return False
        urgency = getattr(plan, 'urgency_state', 'controlled')
        if urgency not in {"urgent", "panic"} and book_age_ms > float(self.config.exit_max_book_age_ms):
            return False
        current_top, _ = self.orderbook.best_bid(plan.side)
        if current_top is None or current_top < slice_plan.limit_price_cents:
            return False
        current_depth = self.orderbook.executable_sell_depth(plan.side, slice_plan.limit_price_cents)
        return current_depth >= Decimal(str(slice_plan.count))

    async def submit_execution_plan(self, plan: ExecutionPlan, filter_decision: FilterDecision) -> None:
        if self.order_inflight:
            return
        self.order_inflight = True
        total_filled = 0
        first_order_id = ""
        try:
            self.run_position_safety_checks(plan.market_ticker, "entry", side=plan.side, count=plan.total_count)
            self.note_entry_attempt_for_cooldown(plan.market_ticker, plan.side)
            self.logger.info(
                "ENTRY signal | market=%s action=buy side=%s trigger=%sc limit=%sc qty=%s book_ready=%s",
                plan.market_ticker,
                plan.side,
                plan.trigger_price_cents,
                plan.limit_price_cents,
                plan.total_count,
                self.orderbook.snapshot_ready,
            )
            self.transition_execution_state(plan.market_ticker, plan.side, "submitting", plan.reason, plan.signal_signature)
            for slice_plan in plan.slices:
                if slice_plan.slice_index > 0 and not self.slice_continuation_is_valid(plan, slice_plan):
                    self.telemetry.emit("execution_deferred", self.telemetry_context_from_plan(plan, filter_decision, slice_plan=slice_plan), result="slice_aborted_after_book_change", account_age_ms=plan.account_age_ms, **self.mushroom_telemetry_fields(plan), **self.orderbook.telemetry_fields())
                    break
                submission = await self.submit_single_order(
                    purpose="entry",
                    market_ticker=plan.market_ticker,
                    side=plan.side,
                    action="buy",
                    count=slice_plan.count,
                    limit_price_cents=slice_plan.limit_price_cents,
                    trigger_price_cents=plan.trigger_price_cents,
                    reduce_only=False,
                    time_in_force=slice_plan.time_in_force,
                    telemetry_context=self.telemetry_context_from_plan(plan, filter_decision, slice_plan=slice_plan),
                )
                if submission is None:
                    break
                if not first_order_id:
                    first_order_id = submission.order_id
                total_filled += submission.fill_count
                if submission.fill_count > 0:
                    entry_fill_cents = submission.actual_fill_price_cents or slice_plan.limit_price_cents
                    entry_fee_cents = (
                        submission.actual_fee_cents
                        if submission.actual_fee_cents is not None
                        else self.estimated_order_fee_cents(entry_fill_cents, submission.fill_count)
                    )
                    self.record_entry_fill_for_outcomes(
                        market_ticker=plan.market_ticker,
                        side=plan.side,
                        fill_count=submission.fill_count,
                        fill_price_cents=entry_fill_cents,
                        trigger_price_cents=plan.trigger_price_cents,
                        actual_fee_cents=submission.actual_fee_cents,
                    )
                    self.apply_entry_fill_to_position(
                        market_ticker=plan.market_ticker,
                        side=plan.side,
                        fill_count=submission.fill_count,
                        entry_order_id=submission.order_id or first_order_id or f"entry-{uuid.uuid4()}",
                        entry_limit_price_cents=slice_plan.limit_price_cents,
                        entry_fill_price_cents=entry_fill_cents,
                        entry_fee_cents=entry_fee_cents,
                        entry_trigger_price_cents=plan.trigger_price_cents,
                    )
                    self.telemetry.emit("fill_partial" if total_filled < plan.total_count else "fill_full", self.telemetry_context_from_plan(plan, filter_decision, slice_plan=slice_plan, submission=submission), cumulative_fill_count=total_filled, account_age_ms=plan.account_age_ms, **self.mushroom_telemetry_fields(plan), **self.orderbook.telemetry_fields())
                if submission.error_text:
                    self.note_entry_rejection(market_ticker=plan.market_ticker, side=plan.side, time_in_force=slice_plan.time_in_force, exc=RuntimeError(submission.error_text))
                    break
                if submission.fill_count == 0 and self.config.live_entry_slice_stop_on_zero_fill:
                    self.telemetry.emit("execution_deferred", self.telemetry_context_from_plan(plan, filter_decision, slice_plan=slice_plan, submission=submission), result="ioc_zero_fill", account_age_ms=plan.account_age_ms, **self.mushroom_telemetry_fields(plan), **self.orderbook.telemetry_fields())
                    break
                if slice_plan.slice_index < len(plan.slices) - 1 and self.config.live_entry_slice_delay_ms > 0:
                    await asyncio.sleep(self.config.live_entry_slice_delay_ms / 1000.0)
            if total_filled > 0:
                position = self.state.position
                if position is None:
                    raise RuntimeError("Entry fill recorded but position state was not created.")
                self.mark_traded(plan.market_ticker)
                self.arm_post_entry_shadow_watch(
                    market_ticker=plan.market_ticker,
                    side=plan.side,
                    filled_at_iso=position.filled_at,
                    entry_fill_cents=(position.entry_fill_price_cents or plan.limit_price_cents),
                    entry_trigger_cents=plan.trigger_price_cents,
                    entry_limit_cents=position.entry_limit_price_cents,
                    seconds_to_close_at_entry=plan.seconds_to_close,
                    book_age_ms_at_entry=plan.book_age_ms,
                    eligible_depth_at_entry=plan.eligible_depth,
                    executable_window_ms_at_entry=plan.executable_window_ms,
                    entry_origin="submit_execution_plan",
                )
                self.save_state()
                if total_filled < plan.total_count:
                    total_filled, first_order_id = await self.continue_partial_entry_completion(
                        plan,
                        filter_decision,
                        total_filled=total_filled,
                        first_order_id=first_order_id,
                    )
                    if self.state.position is not None:
                        self.state.position.entry_order_id = first_order_id or self.state.position.entry_order_id
                        if (
                            self.post_entry_shadow_watch is not None
                            and normalize_ticker(self.post_entry_shadow_watch.market_ticker) == normalize_ticker(plan.market_ticker)
                        ):
                            self.post_entry_shadow_watch.entry_fill_cents = int(self.state.position.entry_fill_price_cents or self.state.position.entry_limit_price_cents)
                            self.post_entry_shadow_watch.entry_limit_cents = int(self.state.position.entry_limit_price_cents)
                        self.save_state()
                self.logger.info("ENTRY immediate fill | market=%s side=%s qty=%s limit=%sc", plan.market_ticker, plan.side, total_filled, plan.limit_price_cents)
                self.transition_execution_state(plan.market_ticker, plan.side, "filled" if total_filled >= plan.total_count else "partially_filled", plan.reason, plan.signal_signature)
            else:
                self.transition_execution_state(plan.market_ticker, plan.side, "abandoned", "zero_fill", plan.signal_signature)
        finally:
            self.order_inflight = False

    async def submit_single_order(
        self,
        *,
        purpose: str,
        market_ticker: str,
        side: str,
        action: str,
        count: int,
        limit_price_cents: int,
        trigger_price_cents: int,
        reduce_only: bool,
        time_in_force: str,
        telemetry_context: ExecutionTelemetryContext,
    ) -> SubmissionResult | None:
        client_order_id = f"btc15m-{purpose}-{uuid.uuid4()}"
        ctx = ExecutionTelemetryContext(**asdict(telemetry_context))
        ctx.client_order_id = client_order_id
        ctx.time_in_force = time_in_force
        self.telemetry.emit("order_submit_start", ctx, **self.orderbook.telemetry_fields())
        if self.config.dry_run:
            result = SubmissionResult(
                purpose=purpose,
                order_id=f"dry-run-{uuid.uuid4()}",
                client_order_id=client_order_id,
                status="executed",
                fill_count=count,
                remaining_count=0,
                submit_latency_ms=0.0,
                limit_price_cents=limit_price_cents,
                time_in_force=time_in_force,
                actual_fill_price_cents=limit_price_cents,
                actual_fee_cents=0,
            )
            self.telemetry.emit("order_submit_success", self.telemetry_context_from_submission(ctx, result), **self.orderbook.telemetry_fields())
            return result
        start_submit = time.monotonic()
        try:
            response = await asyncio.to_thread(
                self.client.create_order,
                ticker=market_ticker,
                side=side,
                action=action,
                count=count,
                limit_price_cents=limit_price_cents,
                reduce_only=reduce_only,
                time_in_force=time_in_force,
                client_order_id=client_order_id,
            )
        except Exception as exc:  # noqa: BLE001
            result = SubmissionResult(
                purpose=purpose,
                order_id="",
                client_order_id=client_order_id,
                status="rejected",
                fill_count=0,
                remaining_count=count,
                submit_latency_ms=(time.monotonic() - start_submit) * 1000.0,
                limit_price_cents=limit_price_cents,
                time_in_force=time_in_force,
                actual_fill_price_cents=None,
                actual_fee_cents=None,
                error_text=str(exc),
            )
            self.telemetry.emit("order_submit_reject", self.telemetry_context_from_submission(ctx, result), result="submit_error_other", **self.orderbook.telemetry_fields())
            if purpose == "entry":
                self.entry_retry_block_until_monotonic = time.monotonic() + 1.0
            return result
        order = response["order"]
        fill_count = safe_int(order.get("fill_count")) or decimal_to_int(to_decimal(order.get("fill_count_fp"))) or 0
        result = SubmissionResult(
            purpose=purpose,
            order_id=str(order.get("order_id") or ""),
            client_order_id=client_order_id,
            status=str(order.get("status") or "").lower(),
            fill_count=fill_count,
            remaining_count=safe_int(order.get("remaining_count")) or decimal_to_int(to_decimal(order.get("remaining_count_fp"))) or 0,
            submit_latency_ms=(time.monotonic() - start_submit) * 1000.0,
            limit_price_cents=limit_price_cents,
            time_in_force=time_in_force,
            actual_fill_price_cents=extract_order_fill_price_cents(order, fill_count=fill_count),
            actual_fee_cents=extract_order_fee_cents(order, fill_count=fill_count),
        )
        self.market_outcomes.mark_submit_latency(market_ticker, result.submit_latency_ms)
        if (
            purpose == "entry"
            and time_in_force == "immediate_or_cancel"
            and result.fill_count <= 0
            and result.status == "canceled"
        ):
            self.market_outcomes.mark_ioc_zero_fill(market_ticker)
        self.telemetry.emit("order_submit_success", self.telemetry_context_from_submission(ctx, result), **self.orderbook.telemetry_fields())
        return result

    def slice_continuation_is_valid(self, plan: ExecutionPlan, slice_plan: SlicePlan) -> bool:
        if self.orderbook.trust.trust_state != "synced":
            return False
        current_top = self.orderbook.top_of_book_buy_limit_cents(plan.side)
        if current_top is None or current_top < plan.cap_price_cents:
            return False
        current_depth = self.orderbook.executable_buy_depth(plan.side, min(current_top, slice_plan.limit_price_cents))
        return current_depth > 0

    def dead_market_reason(self, signal: EntrySignal) -> str | None:
        if not self.config.dry_run and self.orderbook.trust.trust_state != "synced":
            return "book_untrusted"
        if signal.top_of_book_limit_cents is None or signal.top_of_book_limit_cents < signal.cap_price_cents:
            return "cap_not_marketable"
        if signal.eligible_depth <= 0:
            return "insufficient_visible_depth"
        return None

    def dead_market_signature(self, signal: EntrySignal, reason: str) -> str:
        tick = max(1, int(self.config.live_entry_material_book_change_ticks))
        top_limit = signal.top_of_book_limit_cents if signal.top_of_book_limit_cents is not None else -1
        executable_limit = signal.executable_limit_cents if signal.executable_limit_cents is not None else -1
        if top_limit >= 0:
            top_limit = (top_limit // tick) * tick
        if executable_limit >= 0:
            executable_limit = (executable_limit // tick) * tick
        return "|".join([
            reason,
            f"top={top_limit}",
            f"exec={executable_limit}",
            f"depth={format_decimal_compact(signal.eligible_depth)}",
            f"trust={self.orderbook.trust.trust_state}",
            f"book={signal.book_summary}",
        ])

    def should_suppress_dead_market(self, signal: EntrySignal) -> bool:
        reason = self.dead_market_reason(signal)
        key = self.market_side_key(signal.market_ticker, signal.side)
        state = self.execution_state.setdefault(key, MarketSideExecutionState())
        if reason is None:
            state.dead_since_monotonic = None
            state.last_dead_signature = ""
            state.dead_reason = ""
            state.cooldown_until_monotonic = 0.0
            self.execution_state[key] = state
            return False
        now = time.monotonic()
        dead_signature = self.dead_market_signature(signal, reason)
        if state.last_dead_signature != dead_signature:
            state.dead_since_monotonic = now
            state.last_dead_signature = dead_signature
            state.dead_reason = reason
            state.cooldown_until_monotonic = now + (self.config.live_entry_dead_market_suppression_ms / 1000.0)
            self.execution_state[key] = state
            return False
        if state.state != "blocked_dead_market" or state.last_material_signature != dead_signature:
            blocked_after_ms = 0.0
            if state.dead_since_monotonic is not None:
                blocked_after_ms = max(0.0, (now - state.dead_since_monotonic) * 1000.0)
            self.transition_execution_state(signal.market_ticker, signal.side, "blocked_dead_market", reason, dead_signature)
            self.market_outcomes.mark_dead_market_deferral(signal.market_ticker)
            self.telemetry.emit(
                "skip_dead_market",
                self.telemetry_context_from_signal(signal),
                dead_reason=reason,
                suppression_ms=self.config.live_entry_dead_market_suppression_ms,
                blocked_after_ms=blocked_after_ms,
                dead_signature=dead_signature,
                **self.mushroom_telemetry_fields(signal),
                **self.orderbook.telemetry_fields(),
            )
        state.cooldown_until_monotonic = now + (self.config.live_entry_dead_market_suppression_ms / 1000.0)
        state.dead_reason = reason
        self.execution_state[key] = state
        return True

    def update_executable_window(self, signal: EntrySignal) -> None:
        key = self.market_side_key(signal.market_ticker, signal.side)
        window = self.executable_windows.setdefault(key, ExecutableWindowState())
        marketable = signal.top_of_book_limit_cents is not None and signal.top_of_book_limit_cents >= signal.cap_price_cents
        if marketable:
            if not window.active:
                window.active = True
                window.since_monotonic = time.monotonic()
                window.max_visible_depth = signal.eligible_depth
            else:
                window.max_visible_depth = max(window.max_visible_depth, signal.eligible_depth)
            window.last_limit_cents = signal.top_of_book_limit_cents
        else:
            window.active = False
            window.since_monotonic = None
            window.max_visible_depth = Decimal("0")
            window.last_limit_cents = None


    def market_side_key(self, market_ticker: str, side: str) -> str:
        return f"{normalize_ticker(market_ticker)}:{side}"

    def transition_execution_state(self, market_ticker: str, side: str, state: str, reason: str, signature: str) -> None:
        key = self.market_side_key(market_ticker, side)
        current = self.execution_state.get(key, MarketSideExecutionState())
        if current.state == state and current.last_reason == reason and current.last_material_signature == signature:
            self.execution_state[key] = current
            return
        current.state = state
        current.last_reason = reason
        current.last_material_signature = signature
        current.last_transition_monotonic = time.monotonic()
        self.execution_state[key] = current
        self.logger.info("Execution state | market=%s side=%s state=%s reason=%s trust=%s run_id=%s", market_ticker, side, state, reason, self.orderbook.trust.trust_state, self.config.run_id)

    def telemetry_context_from_signal(self, signal: EntrySignal, filter_decision: FilterDecision | None = None) -> ExecutionTelemetryContext:
        feed_age_ms, local_reaction_ms = self.current_latency_snapshot()
        return ExecutionTelemetryContext(
            market=signal.market_ticker,
            purpose="entry",
            side=signal.side,
            trigger_price_cents=signal.trigger_price_cents,
            cap_price_cents=signal.cap_price_cents,
            position_size=int(signal.target_count or self.config.position_size),
            book_age_ms=signal.book_age_ms,
            feed_age_ms=feed_age_ms,
            local_reaction_ms=local_reaction_ms,
            top_of_book_limit_cents=signal.top_of_book_limit_cents,
            eligible_depth=str(signal.eligible_depth),
            book_summary=signal.book_summary,
            pre_std=filter_decision.pre_std if filter_decision else None,
            pre_std_threshold=filter_decision.pre_std_threshold if filter_decision else None,
            std_obs=filter_decision.std_obs if filter_decision else None,
            decision_reason=filter_decision.reason if filter_decision else "",
            executable_window_ms=signal.executable_window_ms,
        )

    def telemetry_context_from_plan(self, plan: ExecutionPlan, filter_decision: FilterDecision, slice_plan: SlicePlan | None = None, submission: SubmissionResult | None = None) -> ExecutionTelemetryContext:
        feed_age_ms, local_reaction_ms = self.current_latency_snapshot()
        ctx = ExecutionTelemetryContext(
            market=plan.market_ticker,
            purpose="entry",
            side=plan.side,
            trigger_price_cents=plan.trigger_price_cents,
            cap_price_cents=plan.cap_price_cents,
            position_size=plan.total_count,
            slice_index=slice_plan.slice_index if slice_plan else None,
            slice_target_size=slice_plan.count if slice_plan else None,
            book_age_ms=plan.book_age_ms,
            feed_age_ms=feed_age_ms,
            local_reaction_ms=local_reaction_ms,
            top_of_book_limit_cents=plan.top_of_book_limit_cents,
            eligible_depth=str(plan.eligible_depth),
            depth_required=str(plan.depth_required),
            book_summary=plan.book_summary,
            pre_std=filter_decision.pre_std,
            pre_std_threshold=filter_decision.pre_std_threshold,
            std_obs=filter_decision.std_obs,
            decision_reason=plan.reason,
            time_in_force=slice_plan.time_in_force if slice_plan else plan.time_in_force,
            executable_window_ms=plan.executable_window_ms,
        )
        if submission is not None:
            ctx.order_id = submission.order_id
            ctx.client_order_id = submission.client_order_id
            ctx.submit_latency_ms = submission.submit_latency_ms
            ctx.exchange_status = submission.status
            ctx.fill_count = submission.fill_count
            ctx.remaining_count = submission.remaining_count
            ctx.result = submission.error_text or submission.status
        return ctx

    def telemetry_context_from_submission(self, ctx: ExecutionTelemetryContext, submission: SubmissionResult) -> ExecutionTelemetryContext:
        new_ctx = ExecutionTelemetryContext(**asdict(ctx))
        new_ctx.order_id = submission.order_id
        new_ctx.client_order_id = submission.client_order_id
        new_ctx.submit_latency_ms = submission.submit_latency_ms
        new_ctx.exchange_status = submission.status
        new_ctx.fill_count = submission.fill_count
        new_ctx.remaining_count = submission.remaining_count
        new_ctx.actual_fill_price_cents = submission.actual_fill_price_cents
        new_ctx.actual_fee_cents = submission.actual_fee_cents
        new_ctx.result = submission.error_text or submission.status
        return new_ctx

    def telemetry_context_from_exit_signal(self, signal: ExitSignal) -> ExecutionTelemetryContext:
        feed_age_ms, local_reaction_ms = self.current_latency_snapshot()
        return ExecutionTelemetryContext(
            market=signal.market_ticker,
            purpose="exit",
            side=signal.side,
            trigger_price_cents=signal.trigger_price_cents,
            cap_price_cents=signal.stop_price_cents,
            position_size=signal.position_count,
            book_age_ms=signal.book_age_ms,
            feed_age_ms=feed_age_ms,
            local_reaction_ms=local_reaction_ms,
            top_of_book_limit_cents=signal.top_of_book_limit_cents,
            eligible_depth=str(signal.eligible_depth),
            depth_required=str(signal.position_count),
            book_summary=signal.book_summary,
            bid_levels=signal.bid_levels,
            same_side_buy_levels=signal.same_side_buy_levels,
            top_bid_size=signal.top_bid_size,
            executable_depth_at_limit=signal.executable_depth_at_limit,
            executable_depth_one_cent_lower=signal.executable_depth_one_cent_lower,
            executable_depth_two_cents_lower=signal.executable_depth_two_cents_lower,
            yes_bid_cents=signal.yes_bid_cents,
            yes_ask_cents=signal.yes_ask_cents,
            no_bid_cents=signal.no_bid_cents,
            no_ask_cents=signal.no_ask_cents,
            yes_bid_size=signal.yes_bid_size,
            yes_ask_size=signal.yes_ask_size,
            no_bid_size=signal.no_bid_size,
            no_ask_size=signal.no_ask_size,
            decision_reason="exit_trigger",
        )

    def telemetry_context_from_exit_plan(self, plan: ExitPlan, submission: SubmissionResult | None = None, slice_plan: SlicePlan | None = None) -> ExecutionTelemetryContext:
        feed_age_ms, local_reaction_ms = self.current_latency_snapshot()
        ctx = ExecutionTelemetryContext(
            market=plan.market_ticker,
            purpose="exit",
            side=plan.side,
            trigger_price_cents=plan.trigger_price_cents,
            cap_price_cents=plan.stop_price_cents,
            position_size=plan.total_count,
            slice_index=slice_plan.slice_index if slice_plan else 0,
            slice_target_size=slice_plan.count if slice_plan else plan.total_count,
            book_age_ms=plan.book_age_ms,
            feed_age_ms=feed_age_ms,
            local_reaction_ms=local_reaction_ms,
            top_of_book_limit_cents=plan.top_of_book_limit_cents,
            eligible_depth=str(plan.eligible_depth),
            depth_required=str(plan.depth_required),
            book_summary=plan.book_summary,
            bid_levels=plan.bid_levels,
            same_side_buy_levels=plan.same_side_buy_levels,
            top_bid_size=plan.top_bid_size,
            executable_depth_at_limit=plan.executable_depth_at_limit,
            executable_depth_one_cent_lower=plan.executable_depth_one_cent_lower,
            executable_depth_two_cents_lower=plan.executable_depth_two_cents_lower,
            yes_bid_cents=plan.yes_bid_cents,
            yes_ask_cents=plan.yes_ask_cents,
            no_bid_cents=plan.no_bid_cents,
            no_ask_cents=plan.no_ask_cents,
            yes_bid_size=plan.yes_bid_size,
            yes_ask_size=plan.yes_ask_size,
            no_bid_size=plan.no_bid_size,
            no_ask_size=plan.no_ask_size,
            decision_reason=plan.reason,
            time_in_force=plan.time_in_force,
        )
        if submission is not None:
            return self.telemetry_context_from_submission(ctx, submission)
        return ctx

    def current_latency_snapshot(self) -> tuple[float | None, float | None]:
        feed_age_ms = None
        local_reaction_ms = None
        msg_time = parse_ws_time(self.market.updated_time)
        if msg_time is not None:
            feed_age_ms = (utc_now() - msg_time).total_seconds() * 1000.0
        if self.market.local_received_monotonic is not None:
            local_reaction_ms = (time.monotonic() - self.market.local_received_monotonic) * 1000.0
        return feed_age_ms, local_reaction_ms

    def account_snapshot_age_ms(self) -> float | None:
        if not self.live_account_snapshot.fetched_at_monotonic:
            return None
        return (time.monotonic() - self.live_account_snapshot.fetched_at_monotonic) * 1000.0

    def defer_execution(self, signal: EntrySignal, reason: str, filter_decision: FilterDecision | None = None, **extra: Any) -> None:
        signature = self.coarse_blocked_signal_signature(signal, reason=reason, extra=extra)
        if self.should_defer_entry_check(ticker=signal.market_ticker, side=signal.side, signature=signature):
            return
        cooldown_seconds = max(0.0, float(self.config.live_entry_blocked_suppression_ms) / 1000.0)
        self.note_entry_skip(
            signal.market_ticker,
            signal.side,
            reason,
            signature,
            cooldown_seconds,
            "Execution deferred | market=%s side=%s reason=%s trigger=%s top_of_book=%s book=%s trust=%s",
            signal.market_ticker,
            signal.side,
            reason,
            signal.trigger_price_cents,
            signal.top_of_book_limit_cents,
            signal.book_summary,
            self.orderbook.trust.trust_state,
        )
        self.transition_execution_state(signal.market_ticker, signal.side, "abandoned", reason, signal.signal_signature)
        self.telemetry.emit("execution_deferred", self.telemetry_context_from_signal(signal, filter_decision=filter_decision), result=reason, account_age_ms=self.account_snapshot_age_ms(), **self.mushroom_telemetry_fields(signal), **self.orderbook.telemetry_fields(), **extra)


    async def maybe_refresh_live_account_state(self, *, force: bool = False) -> None:
        if self.config.dry_run:
            return
        now_mono = time.monotonic()
        if not force and (now_mono - self.last_account_state_attempt_monotonic) < self.config.live_account_state_poll_seconds:
            return
        self.last_account_state_attempt_monotonic = now_mono
        try:
            balance_raw, resting_orders = await asyncio.gather(
                asyncio.to_thread(self.client.get_balance),
                asyncio.to_thread(self.client.get_resting_orders),
            )
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("Live account state refresh failed. Blocking live entries until refresh succeeds. Error: %s", exc)
            self.live_account_snapshot = LiveAccountSnapshot()
            return

        available_balance_cents = extract_available_balance_cents(balance_raw)
        self.live_account_snapshot = LiveAccountSnapshot(
            available_balance_cents=available_balance_cents,
            resting_orders=resting_orders,
            fetched_at_monotonic=time.monotonic(),
        )

    def is_not_found_error(self, exc: Exception) -> bool:
        error_text = str(exc).lower()
        return "404" in error_text or "not found" in error_text or '"code":"not_found"' in error_text or "'code': 'not_found'" in error_text

    async def handle_pending_order_lookup_failure(self, pending: PendingOrder, exc: Exception) -> bool:
        if not self.is_not_found_error(exc):
            return False
        self.logger.warning(
            "Pending order lookup returned not found | order_id=%s purpose=%s market=%s. Reconciling live state and continuing.",
            pending.order_id,
            pending.purpose,
            pending.market_ticker,
        )
        self.state.pending_order = None
        try:
            live_positions = await asyncio.to_thread(self.client.get_positions, pending.market_ticker)
            persisted_ticker = normalize_ticker(pending.market_ticker)
            matching_position = None
            for pos in live_positions:
                live_ticker = normalize_ticker(str(pos.get("ticker") or pos.get("market_ticker") or ""))
                qty = to_decimal(pos.get("position_fp", pos.get("position", 0)))
                if live_ticker == persisted_ticker and qty and qty != 0:
                    matching_position = pos
                    break
            if pending.purpose == "entry":
                if matching_position is not None:
                    live_qty = decimal_to_int(to_decimal(matching_position.get("position_fp", matching_position.get("position", 0)))) or pending.count
                    existing = self.state.position
                    existing_qty = (
                        int(existing.count)
                        if existing is not None
                        and normalize_ticker(existing.market_ticker) == normalize_ticker(pending.market_ticker)
                        and existing.side == pending.side
                        else 0
                    )
                    fill_delta = max(0, int(live_qty) - existing_qty)
                    estimated_fee_cents = self.estimated_order_fee_cents(int(pending.limit_price_cents), int(fill_delta or pending.count))
                    if fill_delta > 0:
                        self.record_entry_fill_for_outcomes(
                            market_ticker=pending.market_ticker,
                            side=pending.side,
                            fill_count=fill_delta,
                            fill_price_cents=int(pending.limit_price_cents),
                            trigger_price_cents=pending.trigger_price_cents,
                            actual_fee_cents=estimated_fee_cents,
                        )
                        self.apply_entry_fill_to_position(
                            market_ticker=pending.market_ticker,
                            side=pending.side,
                            fill_count=fill_delta,
                            entry_order_id=pending.order_id,
                            entry_limit_price_cents=pending.limit_price_cents,
                            entry_fill_price_cents=int(pending.limit_price_cents),
                            entry_fee_cents=estimated_fee_cents,
                            entry_trigger_price_cents=pending.trigger_price_cents,
                        )
                        self.mark_traded(pending.market_ticker)
                    self.arm_post_entry_shadow_watch(
                        market_ticker=pending.market_ticker,
                        side=pending.side,
                        filled_at_iso=(self.state.position.filled_at if self.state.position else utc_now().isoformat()),
                        entry_fill_cents=int(pending.limit_price_cents),
                        entry_trigger_cents=pending.trigger_price_cents,
                        entry_limit_cents=pending.limit_price_cents,
                        seconds_to_close_at_entry=self.seconds_to_close(),
                        book_age_ms_at_entry=self.current_book_age_ms(),
                        eligible_depth_at_entry=self.orderbook.executable_buy_depth(pending.side, pending.limit_price_cents),
                        executable_window_ms_at_entry=None,
                        entry_origin="pending_order_lookup_reconcile",
                    )
                else:
                    if self.state.position is None:
                        self.state.position = None
            else:
                if matching_position is None:
                    self.state.position = None
                self.exit_retry_block_until_monotonic = time.monotonic() + 1.0
        except Exception as reconcile_exc:  # noqa: BLE001
            self.logger.warning(
                "Pending order reconciliation failed | order_id=%s purpose=%s error=%s",
                pending.order_id,
                pending.purpose,
                reconcile_exc,
            )
            if pending.purpose == "exit":
                self.exit_retry_block_until_monotonic = time.monotonic() + 1.0
        self.save_state()
        return True

    async def reconcile_live_position_after_close(self, market_ticker: str) -> bool:
        try:
            live_positions = await asyncio.to_thread(self.client.get_positions, market_ticker)
        except Exception as exc:  # noqa: BLE001
            self.logger.warning(
                "Closed-market live position reconciliation failed for %s. Keeping position state until the next check. Error: %s",
                market_ticker,
                exc,
            )
            return False

        persisted_ticker = normalize_ticker(market_ticker)
        matching_live: list[dict[str, Any]] = []
        for pos in live_positions:
            live_ticker = normalize_ticker(str(pos.get("ticker") or pos.get("market_ticker") or ""))
            qty = to_decimal(pos.get("position_fp", pos.get("position", 0)))
            if live_ticker == persisted_ticker and qty != 0:
                matching_live.append(pos)

        if matching_live:
            if self.live_position_is_settlement_only(market_ticker):
                self.logger.warning(
                    "Closed market %s still reports a nonzero live account position, but the market is already past the settlement grace window. Clearing position state and advancing anyway.",
                    market_ticker,
                )
                self.state.position = None
                self.state.pending_order = None
                self.save_state()
                return True
            self.logger.info(
                "Closed market %s still has a live account position. Keeping position state until settlement fully clears.",
                market_ticker,
            )
            return False

        self.logger.warning(
            "Market %s is closed and no matching live account position remains. Clearing position state and advancing to the next market.",
            market_ticker,
        )
        self.state.position = None
        self.state.pending_order = None
        self.save_state()
        return True

    def live_position_is_settlement_only(self, market_ticker: str) -> bool:
        with contextlib.suppress(Exception):
            market = self.client.get_market(market_ticker)
            if market_is_closed_for_recovery(market):
                return True
        record = self.market_outcomes.get(market_ticker)
        close_dt = parse_iso(record.market_close_time) if record is not None else None
        if close_dt is None and normalize_ticker(self.current_watch_ticker or "") == normalize_ticker(market_ticker):
            close_dt = parse_iso(self.watch_close_time or "")
        return bool(close_dt and utc_now() >= close_dt + timedelta(seconds=SETTLEMENT_ONLY_GRACE_SECONDS))

    def persisted_market_close_time(self, market_ticker: str) -> str | None:
        with contextlib.suppress(Exception):
            market = self.client.get_market(market_ticker)
            close_time = str(market.get("close_time") or market.get("expiration_time") or "").strip()
            if close_time:
                return close_time
        record = self.market_outcomes.get(market_ticker)
        if record is not None and str(record.market_close_time or "").strip():
            return str(record.market_close_time).strip()
        return None

    def describe_live_buy_book(self, side: str, max_levels: int | None = None) -> str:
        levels = int(max_levels or self.config.live_entry_book_diagnostics_levels)
        if side == "yes":
            raw_levels = sorted(self.orderbook.no_bids.items(), key=lambda item: item[0], reverse=True)
            rendered = [f"{100 - price}:{format_decimal_compact(qty)}" for price, qty in raw_levels[:levels] if qty > 0]
        else:
            raw_levels = sorted(self.orderbook.yes_bids.items(), key=lambda item: item[0], reverse=True)
            rendered = [f"{100 - price}:{format_decimal_compact(qty)}" for price, qty in raw_levels[:levels] if qty > 0]
        return "[" + ", ".join(rendered) + "]" if rendered else "[]"

    def describe_live_sell_book(self, side: str, max_levels: int | None = None) -> str:
        levels = int(max_levels or self.config.exit_book_diagnostics_levels)
        raw_levels = sorted((self.orderbook.yes_bids if side == "yes" else self.orderbook.no_bids).items(), key=lambda item: item[0], reverse=True)
        rendered = [f"{price}:{format_decimal_compact(qty)}" for price, qty in raw_levels[:levels] if qty > 0]
        return "[" + ", ".join(rendered) + "]" if rendered else "[]"

    def build_exit_book_snapshot(self, side: str, limit_price_cents: int | None) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], str | None, str | None, str | None, str | None]:
        levels = max(1, int(self.config.exit_book_diagnostics_levels))
        top_bid_cents, top_bid_qty = self.orderbook.best_bid(side)
        depth_at_limit = None if limit_price_cents is None else format_decimal_compact(self.orderbook.executable_sell_depth(side, limit_price_cents))
        depth_one_lower = None if limit_price_cents is None else format_decimal_compact(self.orderbook.executable_sell_depth(side, max(1, limit_price_cents - 1)))
        depth_two_lower = None if limit_price_cents is None else format_decimal_compact(self.orderbook.executable_sell_depth(side, max(1, limit_price_cents - 2)))
        return (
            self.describe_live_sell_book(side, max_levels=levels),
            self.orderbook.visible_bid_levels(side, max_levels=levels),
            self.orderbook.visible_buy_levels(side, max_levels=levels),
            format_decimal_compact(top_bid_qty) if top_bid_qty is not None else None,
            depth_at_limit,
            depth_one_lower,
            depth_two_lower,
        )

    def current_quote_snapshot_fields(self) -> dict[str, Any]:
        def fmt_size(value: Decimal | None) -> str | None:
            return None if value is None else format_decimal_compact(value)
        return {
            "yes_bid_cents": self.market.yes_bid_cents,
            "yes_ask_cents": self.market.yes_ask_cents,
            "no_bid_cents": self.market.no_bid_cents,
            "no_ask_cents": self.market.no_ask_cents,
            "yes_bid_size": fmt_size(self.market.yes_bid_size),
            "yes_ask_size": fmt_size(self.market.yes_ask_size),
            "no_bid_size": fmt_size(self.market.no_bid_size),
            "no_ask_size": fmt_size(self.market.no_ask_size),
        }

    def request_ws_resync(self, market_ticker: str) -> None:
        now_mono = time.monotonic()
        if (now_mono - self.last_ws_resync_monotonic) < 0.5:
            return
        self.last_ws_resync_monotonic = now_mono
        self.orderbook.mark_resyncing()
        asyncio.create_task(self.restart_ws_task())

    def note_entry_rejection(self, *, market_ticker: str, side: str, time_in_force: str, exc: Exception) -> None:
        now_mono = time.monotonic()
        key = f"{normalize_ticker(market_ticker)}:{side}"
        state = self.entry_rejection_state.get(key, EntryRejectionState())
        error_text = str(exc).lower()
        if "fill_or_kill_insufficient_resting_volume" in error_text and time_in_force == "fill_or_kill":
            state.block_until_monotonic = now_mono + 3.0
            if self.config.live_entry_allow_ioc:
                state.prefer_ioc_until_monotonic = now_mono + 20.0
            state.last_reason = "fok_insufficient_resting_volume"
            self.logger.warning(
                "Live entry backoff armed | market=%s side=%s reason=%s block_seconds=3 prefer_ioc_seconds=%s",
                market_ticker,
                side,
                state.last_reason,
                20 if self.config.live_entry_allow_ioc else 0,
            )
        else:
            state.block_until_monotonic = now_mono + 5.0
            state.last_reason = "generic_entry_submit_error"
        self.entry_rejection_state[key] = state

    def current_book_age_ms(self) -> float | None:
        age_candidates: list[float] = []
        now_mono = time.monotonic()
        if self.market.local_received_monotonic is not None:
            age_candidates.append((now_mono - self.market.local_received_monotonic) * 1000.0)
        if self.orderbook.last_update_monotonic is not None:
            age_candidates.append((now_mono - self.orderbook.last_update_monotonic) * 1000.0)
        if not age_candidates:
            return None
        return max(age_candidates)

    def seconds_to_close(self) -> float | None:
        close_dt = parse_iso(self.watch_close_time) if self.watch_close_time else None
        if close_dt is None:
            return None
        return max(0.0, (close_dt - utc_now()).total_seconds())

    def allowed_live_book_age_ms(self, seconds_to_close: float | None) -> float:
        if seconds_to_close is not None and seconds_to_close <= 15:
            return self.config.live_entry_final_seconds_book_age_ms
        if seconds_to_close is not None and seconds_to_close <= 60:
            return self.config.live_entry_final_minute_book_age_ms
        return self.config.live_entry_base_book_age_ms

    def required_depth_cushion(
        self,
        *,
        trigger_price: int,
        executable_limit: int,
        seconds_to_close: float | None,
    ) -> int:
        signal_price = max(int(trigger_price), int(executable_limit))
        if seconds_to_close is not None and seconds_to_close <= 15:
            return 3
        if (seconds_to_close is not None and seconds_to_close <= 60) or signal_price >= self.config.live_entry_extreme_odds_cents:
            return 2
        return 1

    def estimated_order_fee_cents(self, price_cents: int, count: int) -> int:
        bounded_price = max(1, min(99, int(price_cents)))
        numerator = 7 * int(count) * bounded_price * (100 - bounded_price)
        return max(1, (numerator + 9999) // 10000)

    def estimated_round_trip_fee_cents(self, entry_price_cents: int, count: int) -> int:
        exit_price_cents = max(1, min(99, int(self.config.exit_drop_odds_cents)))
        return self.estimated_order_fee_cents(entry_price_cents, count) + self.estimated_order_fee_cents(exit_price_cents, count)

    def fast_fill_gate_metrics(
        self,
        *,
        signal: EntrySignal,
        executable_limit: int,
        eligible_depth: Decimal,
        depth_required: Decimal,
        target_count: int | None = None,
    ) -> dict[str, Any]:
        size = max(1, int(target_count or signal.target_count or self.config.position_size))
        seconds_to_close = signal.seconds_to_close
        executable_window_ms = float(signal.executable_window_ms or 0.0)
        estimated_round_trip_fee_cents = self.estimated_round_trip_fee_cents(executable_limit, size)
        estimated_round_trip_fee_cents_per_contract = (estimated_round_trip_fee_cents + max(0, size - 1)) // max(1, size)
        slippage_budget_cents = int(self.config.live_entry_fast_fill_slippage_budget_cents)
        gross_edge_cents = max(0, 100 - int(executable_limit))
        net_edge_cents = gross_edge_cents - estimated_round_trip_fee_cents_per_contract - slippage_budget_cents
        return {
            "seconds_to_close": seconds_to_close,
            "eligible_depth": eligible_depth,
            "depth_required": depth_required,
            "executable_window_ms": executable_window_ms,
            "estimated_round_trip_fee_cents": estimated_round_trip_fee_cents,
            "estimated_round_trip_fee_cents_per_contract": estimated_round_trip_fee_cents_per_contract,
            "slippage_budget_cents": slippage_budget_cents,
            "gross_edge_cents": gross_edge_cents,
            "net_edge_cents": net_edge_cents,
        }

    def clear_exit_confirmation(self, *, persist: bool = True) -> None:
        if self.state.exit_confirmation is None:
            return
        self.state.exit_confirmation = None
        if persist:
            self.save_state()

    def evaluate_exit_confirmation(self, signal: ExitSignal) -> tuple[bool, str]:
        if signal.stop_tier == "panic":
            self.clear_exit_confirmation(persist=self.state.exit_confirmation is not None)
            return True, "panic_stop"

        required_checks = max(1, int(self.config.exit_confirm_checks))
        required_seconds = max(0.0, float(self.config.exit_confirm_seconds))
        quote_time = parse_ws_time(self.market.updated_time) or utc_now()
        quote_time_iso = quote_time.isoformat()
        state = self.state.exit_confirmation
        updated = False

        if (
            state is None
            or normalize_ticker(state.market_ticker) != normalize_ticker(signal.market_ticker)
            or str(state.side).strip().lower() != signal.side
        ):
            state = ExitConfirmationState(
                market_ticker=signal.market_ticker,
                side=signal.side,
                first_triggered_at=quote_time_iso,
                last_quote_time=quote_time_iso,
                trigger_count=1,
                last_trigger_price_cents=signal.trigger_price_cents,
            )
            self.state.exit_confirmation = state
            updated = True
        else:
            if state.last_quote_time != quote_time_iso:
                state.trigger_count += 1
                state.last_quote_time = quote_time_iso
                updated = True
            if state.last_trigger_price_cents != signal.trigger_price_cents:
                state.last_trigger_price_cents = signal.trigger_price_cents
                updated = True

        first_triggered_at = parse_iso(state.first_triggered_at) or quote_time
        elapsed_seconds = max(0.0, (quote_time - first_triggered_at).total_seconds())
        signal.confirmation_count = int(state.trigger_count)
        signal.confirmation_elapsed_seconds = elapsed_seconds

        if updated:
            self.save_state()

        if state.trigger_count >= required_checks or elapsed_seconds >= required_seconds:
            self.clear_exit_confirmation(persist=self.state.exit_confirmation is not None)
            return True, "confirmed_soft_stop"
        return False, "exit_confirmation_pending"

    def detect_mushroom_v28_exit_signal(self, position: PositionState, filled_at: datetime) -> ExitSignal | None:
        if not self.config.mushroom_v28_live_exit_enabled or self.mushroom_v28_worker is None:
            return None
        if normalize_ticker(self.current_watch_ticker or "") != normalize_ticker(position.market_ticker):
            return None
        seconds_to_close = self.seconds_to_close()
        if seconds_to_close is None or float(seconds_to_close) <= float(self.config.mushroom_v28_min_seconds_to_close):
            return None
        if self.market.strike is None:
            return None
        if not self.mushroom_v28_ready():
            return None
        btc_age_ms = self.mushroom_v28_btc_age_ms()
        if btc_age_ms is None or btc_age_ms > float(self.config.mushroom_v28_btc_max_age_ms):
            return None
        book_age_ms = self.current_book_age_ms()
        if book_age_ms is None or book_age_ms > float(self.config.exit_max_book_age_ms):
            return None
        quote_time = parse_ws_time(self.market.updated_time)
        if quote_time is None or quote_time < (filled_at + timedelta(seconds=self.config.post_fill_exit_delay_seconds)):
            return None

        top_bid, _ = self.orderbook.best_bid(position.side)
        if top_bid is None:
            top_bid = self.market.yes_bid_cents if position.side == "yes" else self.market.no_bid_cents
        if top_bid is None:
            return None
        held_ask = self.current_entry_ask_cents(position.side)

        try:
            with self.mushroom_lock:
                pred = self.mushroom_v28_worker.engine.predict_many(
                    strikes=[float(self.market.strike)],
                    horizon_seconds=float(seconds_to_close),
                )
        except Exception as exc:  # noqa: BLE001
            self.mushroom_v28_last_error = str(exc)
            return None

        p_yes = float(pred.p_yes[0])
        p_hold = p_yes if position.side == "yes" else (1.0 - p_yes)
        fair_yes = float(pred.fair_yes_cents[0])
        fair_no = float(pred.fair_no_cents[0])
        fair_hold = fair_yes if position.side == "yes" else fair_no
        qty = max(1, int(position.count))
        fee_cents = self.estimated_order_fee_cents(int(top_bid), qty) / float(qty)
        exit_net = float(top_bid) - fee_cents - float(self.config.mushroom_v28_slippage_cents)
        hold_net = fair_hold - float(self.config.mushroom_v28_exit_hold_buffer_cents)
        entry_basis = int(position.entry_fill_price_cents or position.entry_limit_price_cents or 0)
        fair_drawdown = float(entry_basis) - fair_hold if entry_basis > 0 else 0.0

        reason = ""
        target_count = 0
        if exit_net >= hold_net + float(self.config.mushroom_v28_exit_hysteresis_cents):
            reason = "mushroom_v28_exit_value_over_hold"
            target_count = qty
        elif p_hold <= float(self.config.mushroom_v28_exit_full_p_hold_floor):
            reason = "mushroom_v28_probability_collapse_full"
            target_count = qty
        elif entry_basis > 0 and fair_drawdown >= float(self.config.mushroom_v28_exit_full_drawdown_cents):
            reason = "mushroom_v28_fair_drawdown_full"
            target_count = qty
        elif p_hold <= float(self.config.mushroom_v28_exit_reduce_p_hold_floor):
            reason = "mushroom_v28_probability_reduce"
            target_count = max(1, int(math.ceil(qty * float(self.config.mushroom_v28_exit_reduce_fraction))))
        elif entry_basis > 0 and fair_drawdown >= float(self.config.mushroom_v28_exit_fair_drawdown_cents):
            reason = "mushroom_v28_fair_drawdown_reduce"
            target_count = max(1, int(math.ceil(qty * float(self.config.mushroom_v28_exit_reduce_fraction))))
        if not reason or target_count <= 0:
            return None
        target_count = min(qty, target_count)
        executable_limit = self.orderbook.executable_sell_limit_cents(position.side, target_count)
        if executable_limit is None and target_count < qty:
            top_depth = max(0, decimal_to_int(self.orderbook.executable_sell_depth(position.side, int(top_bid))) or 0)
            target_count = min(target_count, top_depth)
            executable_limit = int(top_bid) if target_count > 0 else None
        eligible_depth = Decimal("0")
        if executable_limit is not None:
            eligible_depth = self.orderbook.executable_sell_depth(position.side, executable_limit)
        if target_count <= 0:
            return None

        book_summary, bid_levels, same_side_buy_levels, top_bid_size, depth_at_limit, depth_one_lower, depth_two_lower = self.build_exit_book_snapshot(position.side, executable_limit)
        quote_snapshot = self.current_quote_snapshot_fields()
        d_sigma = float(pred.d_sigma[0]) if len(pred.d_sigma) else math.nan
        shadow = {
            "mushroom_v28_version": MUSHROOM_V28_VERSION,
            "mushroom_v28_exit_reason": reason,
            "mushroom_v28_exit_target_count": target_count,
            "mushroom_v28_position_count": qty,
            "mushroom_v28_p_yes": self._round_or_none(p_yes, 6),
            "mushroom_v28_p_hold": self._round_or_none(p_hold, 6),
            "mushroom_v28_fair_yes_cents": self._round_or_none(fair_yes, 6),
            "mushroom_v28_fair_no_cents": self._round_or_none(fair_no, 6),
            "mushroom_v28_fair_hold_cents": self._round_or_none(fair_hold, 6),
            "mushroom_v28_exit_bid_cents": int(top_bid),
            "mushroom_v28_exit_fee_cents": self._round_or_none(fee_cents, 4),
            "mushroom_v28_exit_net_cents": self._round_or_none(exit_net, 6),
            "mushroom_v28_hold_net_cents": self._round_or_none(hold_net, 6),
            "mushroom_v28_exit_hysteresis_cents": self._round_or_none(self.config.mushroom_v28_exit_hysteresis_cents, 4),
            "mushroom_v28_exit_hold_buffer_cents": self._round_or_none(self.config.mushroom_v28_exit_hold_buffer_cents, 4),
            "mushroom_v28_entry_basis_cents": entry_basis,
            "mushroom_v28_fair_drawdown_cents": self._round_or_none(fair_drawdown, 6),
            "mushroom_v28_sigma_t_dollars": self._round_or_none(pred.sigma_t_dollars, 6),
            "mushroom_v28_d_sigma": self._round_or_none(d_sigma, 6),
            "mushroom_v28_btc_age_ms": self._round_or_none(btc_age_ms, 3),
            "mushroom_v28_book_age_ms": self._round_or_none(book_age_ms, 3),
        }
        signal_signature = "|".join(
            [
                reason,
                f"p_hold={p_hold:.6f}",
                f"fair={fair_hold:.6f}",
                f"exit_net={exit_net:.6f}",
                f"hold_net={hold_net:.6f}",
                f"qty={target_count}",
                f"top={top_bid}",
                f"exec={executable_limit}",
                f"btc_age={self._round_or_none(btc_age_ms, 3)}",
            ]
        )
        return ExitSignal(
            market_ticker=position.market_ticker,
            side=position.side,
            trigger_price_cents=int(top_bid),
            stop_price_cents=int(round(fair_hold)),
            position_count=target_count,
            top_of_book_limit_cents=int(top_bid),
            executable_limit_cents=executable_limit,
            eligible_depth=eligible_depth,
            book_age_ms=book_age_ms,
            seconds_to_close=seconds_to_close,
            book_summary=book_summary,
            bid_levels=bid_levels,
            same_side_buy_levels=same_side_buy_levels,
            top_bid_size=top_bid_size,
            executable_depth_at_limit=depth_at_limit,
            executable_depth_one_cent_lower=depth_one_lower,
            executable_depth_two_cents_lower=depth_two_lower,
            yes_bid_cents=quote_snapshot["yes_bid_cents"],
            yes_ask_cents=quote_snapshot["yes_ask_cents"],
            no_bid_cents=quote_snapshot["no_bid_cents"],
            no_ask_cents=quote_snapshot["no_ask_cents"],
            yes_bid_size=quote_snapshot["yes_bid_size"],
            yes_ask_size=quote_snapshot["yes_ask_size"],
            no_bid_size=quote_snapshot["no_bid_size"],
            no_ask_size=quote_snapshot["no_ask_size"],
            detected_at_monotonic=time.monotonic(),
            stop_tier=reason,
            signal_signature=signal_signature,
            mushroom_shadow=shadow,
        )

    def detect_exit_signal(self, position: PositionState, filled_at: datetime) -> ExitSignal | None:
        if not self.config.exit_stop_loss_enabled:
            return None
        if position.side == "yes":
            held_ask = self.market.yes_ask_cents
            if held_ask is None:
                no_bid_book, _ = self.orderbook.best_bid("no")
                if no_bid_book is not None:
                    held_ask = 100 - no_bid_book
                elif self.market.no_bid_cents is not None:
                    held_ask = 100 - self.market.no_bid_cents
            top_bid, _ = self.orderbook.best_bid("yes")
            if top_bid is None:
                top_bid = self.market.yes_bid_cents
        else:
            held_ask = self.market.no_ask_cents
            if held_ask is None:
                yes_bid_book, _ = self.orderbook.best_bid("yes")
                if yes_bid_book is not None:
                    held_ask = 100 - yes_bid_book
                elif self.market.yes_bid_cents is not None:
                    held_ask = 100 - self.market.yes_bid_cents
            top_bid, _ = self.orderbook.best_bid("no")
            if top_bid is None:
                top_bid = self.market.no_bid_cents
        quote_time = parse_ws_time(self.market.updated_time)
        if quote_time is None or quote_time < (filled_at + timedelta(seconds=self.config.post_fill_exit_delay_seconds)):
            return None
        if held_ask is None or held_ask > self.config.exit_drop_odds_cents:
            return None
        stop_tier = "panic" if held_ask <= int(self.config.exit_panic_odds_cents) else "soft"
        executable_limit = self.orderbook.executable_sell_limit_cents(position.side, position.count)
        eligible_depth = Decimal("0")
        if executable_limit is not None:
            eligible_depth = self.orderbook.executable_sell_depth(position.side, executable_limit)
        book_summary, bid_levels, same_side_buy_levels, top_bid_size, depth_at_limit, depth_one_lower, depth_two_lower = self.build_exit_book_snapshot(position.side, executable_limit)
        quote_snapshot = self.current_quote_snapshot_fields()
        signal_signature = "|".join([
            f"trigger={held_ask}",
            f"top={top_bid}",
            f"exec={executable_limit}",
            f"depth={format_decimal_compact(eligible_depth)}",
            f"qty={position.count}",
            f"trust={self.orderbook.trust.trust_state}",
        ])
        return ExitSignal(
            market_ticker=position.market_ticker,
            side=position.side,
            trigger_price_cents=held_ask,
            stop_price_cents=self.config.exit_drop_odds_cents,
            position_count=position.count,
            top_of_book_limit_cents=top_bid,
            executable_limit_cents=executable_limit,
            eligible_depth=eligible_depth,
            book_age_ms=self.current_book_age_ms(),
            seconds_to_close=self.seconds_to_close(),
            book_summary=book_summary,
            bid_levels=bid_levels,
            same_side_buy_levels=same_side_buy_levels,
            top_bid_size=top_bid_size,
            executable_depth_at_limit=depth_at_limit,
            executable_depth_one_cent_lower=depth_one_lower,
            executable_depth_two_cents_lower=depth_two_lower,
            yes_bid_cents=quote_snapshot["yes_bid_cents"],
            yes_ask_cents=quote_snapshot["yes_ask_cents"],
            no_bid_cents=quote_snapshot["no_bid_cents"],
            no_ask_cents=quote_snapshot["no_ask_cents"],
            yes_bid_size=quote_snapshot["yes_bid_size"],
            yes_ask_size=quote_snapshot["yes_ask_size"],
            no_bid_size=quote_snapshot["no_bid_size"],
            no_ask_size=quote_snapshot["no_ask_size"],
            detected_at_monotonic=time.monotonic(),
            stop_tier=stop_tier,
            signal_signature=signal_signature,
        )

    def detect_truffle_exit_signal(self, position: PositionState, filled_at: datetime) -> ExitSignal | None:
        if position.side == "yes":
            held_ask = self.market.yes_ask_cents
            if held_ask is None:
                no_bid_book, _ = self.orderbook.best_bid("no")
                if no_bid_book is not None:
                    held_ask = 100 - no_bid_book
                elif self.market.no_bid_cents is not None:
                    held_ask = 100 - self.market.no_bid_cents
            top_bid, _ = self.orderbook.best_bid("yes")
            if top_bid is None:
                top_bid = self.market.yes_bid_cents
        else:
            held_ask = self.market.no_ask_cents
            if held_ask is None:
                yes_bid_book, _ = self.orderbook.best_bid("yes")
                if yes_bid_book is not None:
                    held_ask = 100 - yes_bid_book
                elif self.market.yes_bid_cents is not None:
                    held_ask = 100 - self.market.yes_bid_cents
            top_bid, _ = self.orderbook.best_bid("no")
            if top_bid is None:
                top_bid = self.market.no_bid_cents
        quote_time = parse_ws_time(self.market.updated_time)
        if quote_time is None or quote_time < (filled_at + timedelta(seconds=self.config.post_fill_exit_delay_seconds)):
            return None
        if held_ask is None:
            return None
        executable_limit = self.orderbook.executable_sell_limit_cents(position.side, position.count)
        eligible_depth = Decimal("0")
        if executable_limit is not None:
            eligible_depth = self.orderbook.executable_sell_depth(position.side, executable_limit)
        book_summary, bid_levels, same_side_buy_levels, top_bid_size, depth_at_limit, depth_one_lower, depth_two_lower = self.build_exit_book_snapshot(position.side, executable_limit)
        quote_snapshot = self.current_quote_snapshot_fields()
        signal_signature = "|".join([
            "truffle_exit_now",
            f"trigger={held_ask}",
            f"top={top_bid}",
            f"exec={executable_limit}",
            f"depth={format_decimal_compact(eligible_depth)}",
            f"qty={position.count}",
            f"trust={self.orderbook.trust.trust_state}",
        ])
        return ExitSignal(
            market_ticker=position.market_ticker,
            side=position.side,
            trigger_price_cents=held_ask,
            stop_price_cents=held_ask,
            position_count=position.count,
            top_of_book_limit_cents=top_bid,
            executable_limit_cents=executable_limit,
            eligible_depth=eligible_depth,
            book_age_ms=self.current_book_age_ms(),
            seconds_to_close=self.seconds_to_close(),
            book_summary=book_summary,
            bid_levels=bid_levels,
            same_side_buy_levels=same_side_buy_levels,
            top_bid_size=top_bid_size,
            executable_depth_at_limit=depth_at_limit,
            executable_depth_one_cent_lower=depth_one_lower,
            executable_depth_two_cents_lower=depth_two_lower,
            yes_bid_cents=quote_snapshot["yes_bid_cents"],
            yes_ask_cents=quote_snapshot["yes_ask_cents"],
            no_bid_cents=quote_snapshot["no_bid_cents"],
            no_ask_cents=quote_snapshot["no_ask_cents"],
            yes_bid_size=quote_snapshot["yes_bid_size"],
            yes_ask_size=quote_snapshot["yes_ask_size"],
            no_bid_size=quote_snapshot["no_bid_size"],
            no_ask_size=quote_snapshot["no_ask_size"],
            detected_at_monotonic=time.monotonic(),
            stop_tier="truffle",
            signal_signature=signal_signature,
        )

    def estimate_exit_capacity(self, signal: ExitSignal) -> ExitCapacityEstimate:
        qty = max(1, int(signal.position_count))
        depth_at_limit = signal.eligible_depth if signal.executable_limit_cents is not None else Decimal("0")
        depth_one_cent_lower = Decimal("0")
        depth_two_cents_lower = Decimal("0")
        if signal.executable_limit_cents is not None:
            depth_one_cent_lower = self.orderbook.executable_sell_depth(signal.side, max(1, signal.executable_limit_cents - 1))
            depth_two_cent_lower = self.orderbook.executable_sell_depth(signal.side, max(1, signal.executable_limit_cents - 2))
            depth_two_cents_lower = depth_two_cent_lower
        expected_fill_ratio_at_limit = min(1.0, float(depth_at_limit) / float(qty)) if qty > 0 else 0.0
        expected_fill_ratio_one_cent_lower = min(1.0, float(depth_one_cent_lower) / float(qty)) if qty > 0 else 0.0
        expected_fill_ratio_two_cents_lower = min(1.0, float(depth_two_cents_lower) / float(qty)) if qty > 0 else 0.0
        full_size_available_at_limit = depth_at_limit >= Decimal(str(qty))
        price_gap_to_limit = 0 if signal.executable_limit_cents is None else max(0, int(signal.trigger_price_cents) - int(signal.executable_limit_cents))
        seconds_to_close = signal.seconds_to_close
        book_age_ms = float(signal.book_age_ms or 0.0)
        book_is_collapsing = (
            price_gap_to_limit >= 2
            or (signal.top_of_book_limit_cents is not None and signal.top_of_book_limit_cents < signal.trigger_price_cents - 1)
            or (depth_at_limit > 0 and depth_one_cent_lower >= (depth_at_limit * Decimal('1.5')))
        )
        if seconds_to_close is not None and seconds_to_close <= 10:
            urgency_state = 'panic'
        elif signal.executable_limit_cents is None:
            urgency_state = 'urgent'
        elif book_is_collapsing and expected_fill_ratio_at_limit < 1.0:
            urgency_state = 'urgent'
        elif full_size_available_at_limit and book_age_ms <= 150.0:
            urgency_state = 'controlled'
        else:
            urgency_state = 'elevated'
        if urgency_state == 'panic':
            recommended_mode = 'panic_liquidation'
            max_retry_steps = 1
        elif full_size_available_at_limit and urgency_state == 'controlled':
            recommended_mode = 'single_shot_ioc'
            max_retry_steps = 1
        elif expected_fill_ratio_one_cent_lower >= 1.0 or expected_fill_ratio_at_limit >= 0.5:
            recommended_mode = 'adaptive_ioc_slices'
            max_retry_steps = 2
        else:
            recommended_mode = 'reprice_retry_ioc'
            max_retry_steps = 2
        recommended_first_slice = max(1, min(qty, int(max(1.0, round(float(depth_at_limit) if depth_at_limit > 0 else 1.0)))))
        if recommended_mode == 'adaptive_ioc_slices':
            remaining = qty
            ladder = []
            slice_size = max(1, min(qty, recommended_first_slice))
            while remaining > 0:
                current = min(remaining, slice_size)
                ladder.append(current)
                remaining -= current
            recommended_slice_ladder = ladder
        else:
            recommended_slice_ladder = [qty]
        explanation = (
            f'urgency={urgency_state}; mode={recommended_mode}; '
            f'depth_at_limit={format_decimal_compact(depth_at_limit)}; '
            f'depth_one_lower={format_decimal_compact(depth_one_cent_lower)}; '
            f'price_gap_to_limit={price_gap_to_limit}; '
            f'book_age_ms={book_age_ms:.1f}'
        )
        return ExitCapacityEstimate(
            depth_at_limit=depth_at_limit,
            depth_one_cent_lower=depth_one_cent_lower,
            depth_two_cents_lower=depth_two_cents_lower,
            expected_fill_ratio_at_limit=expected_fill_ratio_at_limit,
            expected_fill_ratio_one_cent_lower=expected_fill_ratio_one_cent_lower,
            expected_fill_ratio_two_cents_lower=expected_fill_ratio_two_cents_lower,
            full_size_available_at_limit=full_size_available_at_limit,
            book_is_collapsing=book_is_collapsing,
            urgency_state=urgency_state,
            recommended_mode=recommended_mode,
            recommended_first_slice=recommended_first_slice,
            recommended_slice_ladder=recommended_slice_ladder,
            max_retry_steps=max_retry_steps,
            explanation=explanation,
        )

    def build_exit_plan(self, signal: ExitSignal, estimate: ExitCapacityEstimate | None = None) -> ExitPlan | None:
        estimate = estimate or self.estimate_exit_capacity(signal)
        if signal.executable_limit_cents is None:
            self.logger.info(
                "Exit trigger seen but insufficient visible bid liquidity | market=%s side=%s current_ask=%sc qty=%s book=%s",
                signal.market_ticker,
                signal.side,
                signal.trigger_price_cents,
                signal.position_count,
                signal.book_summary,
            )
            self.telemetry.emit(
                "exit_execution_deferred",
                self.telemetry_context_from_exit_signal(signal),
                result="insufficient_visible_bid_liquidity",
                urgency_state=estimate.urgency_state,
                recommended_mode=estimate.recommended_mode,
                account_age_ms=self.account_snapshot_age_ms(),
                **self.orderbook.telemetry_fields(),
            )
            return None
        if self.orderbook.trust.trust_state != "synced" and estimate.urgency_state not in {"urgent", "panic"}:
            self.telemetry.emit(
                "exit_execution_deferred",
                self.telemetry_context_from_exit_signal(signal),
                result="book_untrusted",
                urgency_state=estimate.urgency_state,
                recommended_mode=estimate.recommended_mode,
                account_age_ms=self.account_snapshot_age_ms(),
                **self.orderbook.telemetry_fields(),
            )
            return None
        max_book_age_ms = float(self.config.exit_max_book_age_ms)
        book_age_ms = float(signal.book_age_ms or 0.0)
        if book_age_ms > max_book_age_ms and estimate.urgency_state not in {"urgent", "panic"}:
            self.telemetry.emit(
                "exit_execution_deferred",
                self.telemetry_context_from_exit_signal(signal),
                result="stale_book",
                urgency_state=estimate.urgency_state,
                recommended_mode=estimate.recommended_mode,
                account_age_ms=self.account_snapshot_age_ms(),
                **self.orderbook.telemetry_fields(),
            )
            return None
        recommended_mode = estimate.recommended_mode if self.config.exit_mode_selection_enabled else "single_shot_ioc"
        single_order_depth_multiple = max(1.0, float(self.config.exit_single_order_depth_multiple))
        if recommended_mode == "single_shot_ioc" and signal.eligible_depth < (Decimal(str(signal.position_count)) * Decimal(str(single_order_depth_multiple))):
            recommended_mode = "adaptive_ioc_slices"
        reason_base = "single_shot_visible_depth" if recommended_mode == "single_shot_ioc" else "adaptive_visible_depth"
        reason = f"{signal.stop_tier}_{reason_base}"
        plan = ExitPlan(
            market_ticker=signal.market_ticker,
            side=signal.side,
            trigger_price_cents=signal.trigger_price_cents,
            stop_price_cents=signal.stop_price_cents,
            total_count=signal.position_count,
            top_of_book_limit_cents=signal.top_of_book_limit_cents,
            limit_price_cents=signal.executable_limit_cents,
            eligible_depth=signal.eligible_depth,
            depth_required=Decimal(str(signal.position_count)),
            book_age_ms=book_age_ms,
            seconds_to_close=signal.seconds_to_close,
            time_in_force="immediate_or_cancel",
            reason=reason,
            book_summary=signal.book_summary,
            bid_levels=signal.bid_levels,
            same_side_buy_levels=signal.same_side_buy_levels,
            top_bid_size=signal.top_bid_size,
            executable_depth_at_limit=signal.executable_depth_at_limit,
            executable_depth_one_cent_lower=signal.executable_depth_one_cent_lower,
            executable_depth_two_cents_lower=signal.executable_depth_two_cents_lower,
            yes_bid_cents=signal.yes_bid_cents,
            yes_ask_cents=signal.yes_ask_cents,
            no_bid_cents=signal.no_bid_cents,
            no_ask_cents=signal.no_ask_cents,
            yes_bid_size=signal.yes_bid_size,
            yes_ask_size=signal.yes_ask_size,
            no_bid_size=signal.no_bid_size,
            no_ask_size=signal.no_ask_size,
            urgency_state=estimate.urgency_state,
            recommended_mode=recommended_mode,
            expected_fill_ratio_at_limit=estimate.expected_fill_ratio_at_limit,
            expected_fill_ratio_one_cent_lower=estimate.expected_fill_ratio_one_cent_lower,
            expected_fill_ratio_two_cents_lower=estimate.expected_fill_ratio_two_cents_lower,
            full_size_available_at_limit=estimate.full_size_available_at_limit,
            max_retry_steps=estimate.max_retry_steps,
            signal_signature=signal.signal_signature,
            account_age_ms=self.account_snapshot_age_ms(),
            mushroom_shadow=dict(signal.mushroom_shadow),
        )
        plan.slices = self.build_exit_slice_plans(plan)
        return plan

    def build_exit_retry_plan(self, current_plan: ExitPlan, *, retry_reason: str, attempt_index: int) -> ExitPlan | None:
        position = self.state.position
        if position is None or position.count <= 0:
            return None
        filled_at = parse_iso(position.filled_at)
        if filled_at is None:
            return None
        signal = self.detect_exit_signal(position, filled_at)
        if signal is None:
            self.telemetry.emit(
                "exit_execution_deferred",
                self.telemetry_context_from_exit_plan(current_plan),
                result="retry_signal_cleared",
                retry_reason=retry_reason,
                attempt_index=attempt_index,
                account_age_ms=current_plan.account_age_ms,
                **self.orderbook.telemetry_fields(),
            )
            return None
        estimate = self.estimate_exit_capacity(signal)
        rebuilt = self.build_exit_plan(signal, estimate)
        if rebuilt is None:
            return None
        tick = max(1, int(self.config.exit_retry_tick_step_cents))
        floor_limit = max(1, int(current_plan.limit_price_cents) - max(0, int(self.config.exit_panic_max_cross_cents)))
        candidate_limit = rebuilt.limit_price_cents
        if retry_reason == "ioc_zero_fill" and self.config.exit_rebuild_on_zero_fill:
            candidate_limit = min(candidate_limit, int(current_plan.limit_price_cents) - tick)
        elif retry_reason == "partial_remaining" and self.config.exit_reprice_on_partial_fill:
            candidate_limit = min(candidate_limit, int(current_plan.limit_price_cents) - tick)
        rebuilt.limit_price_cents = max(floor_limit, int(candidate_limit))
        rebuilt.eligible_depth = self.orderbook.executable_sell_depth(rebuilt.side, rebuilt.limit_price_cents)
        rebuilt.expected_fill_ratio_at_limit = min(1.0, float(rebuilt.eligible_depth) / float(max(1, rebuilt.total_count)))
        retry_prefix = "mushroom_v28_retry" if str(current_plan.reason).startswith("mushroom_v28_") else "retry"
        rebuilt.reason = f"{retry_prefix}_{retry_reason}"
        rebuilt.max_retry_steps = min(int(self.config.exit_max_retry_steps), max(0, rebuilt.max_retry_steps))
        rebuilt.slices = self.build_exit_slice_plans(rebuilt)
        return rebuilt

    async def submit_exit_plan(self, plan: ExitPlan) -> None:
        if self.order_inflight:
            return
        self.order_inflight = True
        try:
            self.run_position_safety_checks(plan.market_ticker, "exit", side=plan.side, count=plan.total_count)
            total_filled = 0
            attempt_index = 0
            current_plan = plan
            initial_limit_price_cents = plan.limit_price_cents
            while True:
                self.logger.info(
                    "EXIT signal | market=%s action=sell side=%s trigger=%sc limit=%sc qty=%s book_ready=%s mode=%s slices=%s attempt=%s",
                    current_plan.market_ticker,
                    current_plan.side,
                    current_plan.trigger_price_cents,
                    current_plan.limit_price_cents,
                    current_plan.total_count,
                    self.orderbook.snapshot_ready,
                    current_plan.recommended_mode,
                    len(current_plan.slices) or 1,
                    attempt_index,
                )
                self.log_latency_metrics(utc_now().isoformat(), "exit")
                self.logger.info(
                    "Exit plan approved | market=%s side=%s trigger=%sc limit=%sc top_bid=%s depth=%s required=%s book_age_ms=%.1f secs_to_close=%s reason=%s mode=%s attempt=%s",
                    current_plan.market_ticker,
                    current_plan.side,
                    current_plan.trigger_price_cents,
                    current_plan.limit_price_cents,
                    current_plan.top_of_book_limit_cents,
                    str(current_plan.eligible_depth),
                    str(current_plan.depth_required),
                    current_plan.book_age_ms,
                    f"{current_plan.seconds_to_close:.2f}" if current_plan.seconds_to_close is not None else "NA",
                    current_plan.reason,
                    current_plan.recommended_mode,
                    attempt_index,
                )
                slices = current_plan.slices or [SlicePlan(slice_index=0, count=current_plan.total_count, limit_price_cents=current_plan.limit_price_cents, time_in_force=current_plan.time_in_force, reason="single_order")]
                retry_reason = None
                for slice_plan in slices:
                    if slice_plan.slice_index > 0 and float(self.config.exit_slice_delay_ms) > 0:
                        await asyncio.sleep(float(self.config.exit_slice_delay_ms) / 1000.0)
                    if slice_plan.slice_index > 0 and not self.exit_slice_continuation_is_valid(current_plan, slice_plan):
                        retry_reason = "slice_aborted_after_book_change"
                        self.telemetry.emit(
                            "exit_execution_deferred",
                            self.telemetry_context_from_exit_plan(current_plan, slice_plan=slice_plan),
                            result=retry_reason,
                            cumulative_fill_count=total_filled,
                            attempt_index=attempt_index,
                            urgency_state=current_plan.urgency_state,
                            recommended_mode=current_plan.recommended_mode,
                            account_age_ms=current_plan.account_age_ms,
                            **self.orderbook.telemetry_fields(),
                        )
                        break
                    current_remaining = self.state.position.count if self.state.position else max(0, current_plan.total_count - total_filled)
                    if current_remaining <= 0:
                        return
                    submit_count = min(slice_plan.count, current_remaining)
                    effective_slice = SlicePlan(
                        slice_index=slice_plan.slice_index,
                        count=submit_count,
                        limit_price_cents=slice_plan.limit_price_cents,
                        time_in_force=slice_plan.time_in_force,
                        reason=slice_plan.reason,
                    )
                    exit_ctx = self.telemetry_context_from_exit_plan(current_plan, slice_plan=effective_slice)
                    self.telemetry.emit(
                        "exit_submit_start",
                        exit_ctx,
                        account_age_ms=current_plan.account_age_ms,
                        attempt_index=attempt_index,
                        trigger_to_submit_ms=((time.monotonic() - self.last_exit_signal_monotonic) * 1000.0) if getattr(self, "last_exit_signal_monotonic", None) is not None else None,
                        urgency_state=current_plan.urgency_state,
                        recommended_mode=current_plan.recommended_mode,
                        **self.orderbook.telemetry_fields(),
                    )
                    submission = await self.submit_single_order(
                        purpose="exit",
                        market_ticker=current_plan.market_ticker,
                        side=current_plan.side,
                        action="sell",
                        count=effective_slice.count,
                        limit_price_cents=effective_slice.limit_price_cents,
                        trigger_price_cents=current_plan.trigger_price_cents,
                        reduce_only=True,
                        time_in_force=effective_slice.time_in_force,
                        telemetry_context=exit_ctx,
                    )
                    if submission is None:
                        return
                    if submission.error_text:
                        retry_reason = "submit_error"
                        self.telemetry.emit(
                            "exit_execution_deferred",
                            self.telemetry_context_from_exit_plan(current_plan, submission=submission, slice_plan=effective_slice),
                            result=retry_reason,
                            cumulative_fill_count=total_filled,
                            attempt_index=attempt_index,
                            urgency_state=current_plan.urgency_state,
                            recommended_mode=current_plan.recommended_mode,
                            account_age_ms=current_plan.account_age_ms,
                            **self.orderbook.telemetry_fields(),
                        )
                        break
                    if submission.fill_count <= 0 and submission.status == "canceled":
                        retry_reason = "ioc_zero_fill"
                        self.telemetry.emit(
                            "exit_submit_zero_fill",
                            self.telemetry_context_from_exit_plan(current_plan, submission=submission, slice_plan=effective_slice),
                            result=retry_reason,
                            cumulative_fill_count=total_filled,
                            attempt_index=attempt_index,
                            urgency_state=current_plan.urgency_state,
                            recommended_mode=current_plan.recommended_mode,
                            account_age_ms=current_plan.account_age_ms,
                            **self.orderbook.telemetry_fields(),
                        )
                        self.telemetry.emit(
                            "exit_execution_deferred",
                            self.telemetry_context_from_exit_plan(current_plan, submission=submission, slice_plan=effective_slice),
                            result=retry_reason,
                            cumulative_fill_count=total_filled,
                            attempt_index=attempt_index,
                            urgency_state=current_plan.urgency_state,
                            recommended_mode=current_plan.recommended_mode,
                            account_age_ms=current_plan.account_age_ms,
                            **self.orderbook.telemetry_fields(),
                        )
                        break
                    total_filled += submission.fill_count
                    if submission.fill_count > 0:
                        self.telemetry.emit(
                            "exit_submit_partial" if submission.fill_count < effective_slice.count else "exit_submit_full",
                            self.telemetry_context_from_exit_plan(current_plan, submission=submission, slice_plan=effective_slice),
                            cumulative_fill_count=total_filled,
                            slippage_vs_trigger_cents=(submission.actual_fill_price_cents - current_plan.trigger_price_cents) if submission.actual_fill_price_cents is not None else None,
                            slippage_vs_initial_limit_cents=(submission.actual_fill_price_cents - initial_limit_price_cents) if submission.actual_fill_price_cents is not None else None,
                            attempt_index=attempt_index,
                            urgency_state=current_plan.urgency_state,
                            recommended_mode=current_plan.recommended_mode,
                            account_age_ms=current_plan.account_age_ms,
                            **self.orderbook.telemetry_fields(),
                        )
                        self.telemetry.emit(
                            "fill_partial" if total_filled < plan.total_count else "fill_full",
                            self.telemetry_context_from_exit_plan(current_plan, submission=submission, slice_plan=effective_slice),
                            cumulative_fill_count=total_filled,
                            attempt_index=attempt_index,
                            account_age_ms=current_plan.account_age_ms,
                            **self.orderbook.telemetry_fields(),
                        )
                    self.telemetry.emit(
                        "exit_submit_success",
                        self.telemetry_context_from_exit_plan(current_plan, submission=submission, slice_plan=effective_slice),
                        cumulative_fill_count=total_filled,
                        attempt_index=attempt_index,
                        urgency_state=current_plan.urgency_state,
                        recommended_mode=current_plan.recommended_mode,
                        account_age_ms=current_plan.account_age_ms,
                        **self.orderbook.telemetry_fields(),
                    )
                    if submission.fill_count > 0:
                        remaining_position = max(0, (self.state.position.count if self.state.position else current_plan.total_count) - submission.fill_count)
                        self.record_exit_fill_for_outcomes(
                            market_ticker=current_plan.market_ticker,
                            fill_count=submission.fill_count,
                            fill_price_cents=submission.actual_fill_price_cents or effective_slice.limit_price_cents,
                            remaining_position=remaining_position,
                            actual_fee_cents=submission.actual_fee_cents,
                        )
                        if remaining_position > 0 and self.state.position:
                            self.state.position.count = remaining_position
                        else:
                            self.state.position = None
                        self.save_state()
                        self.telemetry.emit(
                            "exit_reconciled",
                            self.telemetry_context_from_exit_plan(current_plan, submission=submission, slice_plan=effective_slice),
                            remaining_position_size=self.state.position.count if self.state.position else 0,
                            cumulative_fill_count=total_filled,
                            attempt_index=attempt_index,
                            urgency_state=current_plan.urgency_state,
                            recommended_mode=current_plan.recommended_mode,
                            account_age_ms=current_plan.account_age_ms,
                            **self.orderbook.telemetry_fields(),
                        )
                        if submission.actual_fill_price_cents is not None:
                            self.logger.info(
                                "EXIT fill | market=%s side=%s slice=%s/%s qty=%s fill=%sc cumulative=%s/%s remaining=%s",
                                current_plan.market_ticker,
                                current_plan.side,
                                effective_slice.slice_index + 1,
                                len(slices),
                                submission.fill_count,
                                submission.actual_fill_price_cents,
                                total_filled,
                                plan.total_count,
                                self.state.position.count if self.state.position else 0,
                            )
                        else:
                            self.logger.info(
                                "EXIT fill | market=%s side=%s slice=%s/%s qty=%s cumulative=%s/%s remaining=%s",
                                current_plan.market_ticker,
                                current_plan.side,
                                effective_slice.slice_index + 1,
                                len(slices),
                                submission.fill_count,
                                total_filled,
                                plan.total_count,
                                self.state.position.count if self.state.position else 0,
                            )
                    if total_filled >= plan.total_count or self.state.position is None:
                        return
                if total_filled >= plan.total_count or self.state.position is None:
                    return
                if retry_reason is None:
                    retry_reason = "partial_remaining"
                if attempt_index >= max(0, int(current_plan.max_retry_steps)):
                    self.telemetry.emit(
                        "exit_execution_deferred",
                        self.telemetry_context_from_exit_plan(current_plan),
                        result="retry_limit_reached",
                        retry_reason=retry_reason,
                        cumulative_fill_count=total_filled,
                        remaining_position_size=self.state.position.count if self.state.position else 0,
                        attempt_index=attempt_index,
                        urgency_state=current_plan.urgency_state,
                        recommended_mode=current_plan.recommended_mode,
                        account_age_ms=current_plan.account_age_ms,
                        **self.orderbook.telemetry_fields(),
                    )
                    self.exit_retry_block_until_monotonic = time.monotonic() + max(0.0, float(self.config.exit_retry_backoff_ms) / 1000.0)
                    return
                next_attempt = attempt_index + 1
                next_plan = self.build_exit_retry_plan(current_plan, retry_reason=retry_reason, attempt_index=next_attempt)
                if next_plan is None:
                    self.exit_retry_block_until_monotonic = time.monotonic() + max(0.0, float(self.config.exit_retry_backoff_ms) / 1000.0)
                    return
                self.telemetry.emit(
                    "exit_retry_scheduled",
                    self.telemetry_context_from_exit_plan(current_plan),
                    retry_reason=retry_reason,
                    attempt_index=next_attempt,
                    from_limit_price_cents=current_plan.limit_price_cents,
                    to_limit_price_cents=next_plan.limit_price_cents,
                    from_mode=current_plan.recommended_mode,
                    to_mode=next_plan.recommended_mode,
                    remaining_position_size=self.state.position.count if self.state.position else 0,
                    backoff_ms=float(self.config.exit_retry_backoff_ms),
                    account_age_ms=current_plan.account_age_ms,
                    **self.orderbook.telemetry_fields(),
                )
                if next_plan.recommended_mode != current_plan.recommended_mode:
                    self.telemetry.emit(
                        "exit_mode_escalated",
                        self.telemetry_context_from_exit_plan(next_plan),
                        retry_reason=retry_reason,
                        attempt_index=next_attempt,
                        from_mode=current_plan.recommended_mode,
                        to_mode=next_plan.recommended_mode,
                        account_age_ms=next_plan.account_age_ms,
                        **self.orderbook.telemetry_fields(),
                    )
                if float(self.config.exit_retry_backoff_ms) > 0:
                    await asyncio.sleep(float(self.config.exit_retry_backoff_ms) / 1000.0)
                self.telemetry.emit(
                    "exit_retry_executed",
                    self.telemetry_context_from_exit_plan(next_plan),
                    retry_reason=retry_reason,
                    attempt_index=next_attempt,
                    remaining_position_size=self.state.position.count if self.state.position else 0,
                    account_age_ms=next_plan.account_age_ms,
                    **self.orderbook.telemetry_fields(),
                )
                current_plan = next_plan
                attempt_index = next_attempt
        finally:
            self.order_inflight = False

    def current_truffle_live_exit_decision(self, market_ticker: str) -> PostEntryShadowDecision | None:
        key = normalize_ticker(market_ticker)
        decision = self.post_entry_shadow_decisions.get(key)
        if decision is None:
            return None
        if decision.decision_schema != "exit_supervisor":
            return None
        if not decision.is_valid:
            return None
        if decision.effective_exit_supervisor_decision != "EXIT_NOW":
            return None
        return decision

    async def execute_exit_signal(
        self,
        signal: ExitSignal,
        *,
        exit_source: str,
        truffle_decision: PostEntryShadowDecision | None = None,
    ) -> None:
        self.last_exit_signal_monotonic = signal.detected_at_monotonic or time.monotonic()
        telemetry_extra = {
            "stop_tier": signal.stop_tier,
            "exit_source": exit_source,
            **self.mushroom_telemetry_fields(signal),
        }
        if truffle_decision is not None:
            telemetry_extra.update(
                {
                    "truffle_decision": truffle_decision.decision,
                    "truffle_confidence": round(float(truffle_decision.confidence), 4),
                    "truffle_reason_code": truffle_decision.reason_code,
                    "truffle_issued_at": truffle_decision.issued_at,
                }
            )
        self.telemetry.emit(
            "exit_signal_seen",
            self.telemetry_context_from_exit_signal(signal),
            account_age_ms=self.account_snapshot_age_ms(),
            **telemetry_extra,
            **self.orderbook.telemetry_fields(),
        )
        self.telemetry.emit(
            "exit_snapshot_built",
            self.telemetry_context_from_exit_signal(signal),
            account_age_ms=self.account_snapshot_age_ms(),
            **telemetry_extra,
            **self.orderbook.telemetry_fields(),
        )
        estimate = self.estimate_exit_capacity(signal)
        self.telemetry.emit(
            "exit_capacity_estimated",
            self.telemetry_context_from_exit_signal(signal),
            depth_at_limit=format_decimal_compact(estimate.depth_at_limit),
            depth_one_cent_lower=format_decimal_compact(estimate.depth_one_cent_lower),
            depth_two_cents_lower=format_decimal_compact(estimate.depth_two_cents_lower),
            expected_fill_ratio_at_limit=round(estimate.expected_fill_ratio_at_limit, 4),
            expected_fill_ratio_one_cent_lower=round(estimate.expected_fill_ratio_one_cent_lower, 4),
            expected_fill_ratio_two_cents_lower=round(estimate.expected_fill_ratio_two_cents_lower, 4),
            full_size_available_at_limit=estimate.full_size_available_at_limit,
            book_is_collapsing=estimate.book_is_collapsing,
            urgency_state=estimate.urgency_state,
            recommended_mode=estimate.recommended_mode,
            recommended_first_slice=estimate.recommended_first_slice,
            recommended_slice_ladder=estimate.recommended_slice_ladder,
            max_retry_steps=estimate.max_retry_steps,
            explanation=estimate.explanation,
            account_age_ms=self.account_snapshot_age_ms(),
            **telemetry_extra,
            **self.orderbook.telemetry_fields(),
        )
        plan = self.build_exit_plan(signal, estimate)
        if plan is None:
            if exit_source == "truffle_post_entry_shadow":
                self.exit_retry_block_until_monotonic = max(
                    self.exit_retry_block_until_monotonic,
                    time.monotonic() + 0.5,
                )
            return
        self.telemetry.emit(
            "exit_plan_built",
            self.telemetry_context_from_exit_plan(plan),
            urgency_state=plan.urgency_state,
            recommended_mode=plan.recommended_mode,
            expected_fill_ratio_at_limit=plan.expected_fill_ratio_at_limit,
            expected_fill_ratio_one_cent_lower=plan.expected_fill_ratio_one_cent_lower,
            expected_fill_ratio_two_cents_lower=plan.expected_fill_ratio_two_cents_lower,
            full_size_available_at_limit=plan.full_size_available_at_limit,
            max_retry_steps=plan.max_retry_steps,
            account_age_ms=plan.account_age_ms,
            **telemetry_extra,
            **self.orderbook.telemetry_fields(),
        )
        await self.submit_exit_plan(plan)

    async def maybe_check_exit(self) -> None:
        position = self.state.position
        if not position:
            self.clear_exit_confirmation(persist=self.state.exit_confirmation is not None)
            return
        if self.state.pending_order or self.order_inflight:
            return
        if time.monotonic() < self.exit_retry_block_until_monotonic:
            return
        if self.current_watch_ticker != position.market_ticker:
            self.clear_exit_confirmation(persist=self.state.exit_confirmation is not None)
            return
        filled_at = parse_iso(position.filled_at)
        if not filled_at:
            self.clear_exit_confirmation(persist=self.state.exit_confirmation is not None)
            return
        seconds_since_fill = (utc_now() - filled_at).total_seconds()
        if seconds_since_fill < self.config.post_fill_exit_delay_seconds:
            return
        if self.config.mushroom_v28_live_exit_enabled:
            signal = self.detect_mushroom_v28_exit_signal(position, filled_at)
            if signal is not None:
                await self.execute_exit_signal(signal, exit_source="mushroom_v28_ev")
                return
        if self.config.truffle_post_entry_shadow_live_exit_enabled:
            truffle_decision = self.current_truffle_live_exit_decision(position.market_ticker)
            if truffle_decision is not None:
                signal = self.detect_truffle_exit_signal(position, filled_at)
                if signal is not None:
                    await self.execute_exit_signal(
                        signal,
                        exit_source="truffle_post_entry_shadow",
                        truffle_decision=truffle_decision,
                    )
                    return
        if not self.config.exit_stop_loss_enabled:
            self.clear_exit_confirmation(persist=self.state.exit_confirmation is not None)
            return
        if str(current_plan.reason).startswith("mushroom_v28_"):
            signal = self.detect_mushroom_v28_exit_signal(position, filled_at)
        else:
            signal = self.detect_exit_signal(position, filled_at)
        if signal is None:
            self.clear_exit_confirmation(persist=self.state.exit_confirmation is not None)
            return
        exit_allowed, gate_reason = self.evaluate_exit_confirmation(signal)
        if not exit_allowed:
            self.telemetry.emit(
                "exit_execution_deferred",
                self.telemetry_context_from_exit_signal(signal),
                result=gate_reason,
                stop_tier=signal.stop_tier,
                confirmation_count=signal.confirmation_count,
                confirmation_elapsed_seconds=round(signal.confirmation_elapsed_seconds, 3),
                required_confirm_checks=int(self.config.exit_confirm_checks),
                required_confirm_seconds=float(self.config.exit_confirm_seconds),
                account_age_ms=self.account_snapshot_age_ms(),
                **self.orderbook.telemetry_fields(),
            )
            return
        await self.execute_exit_signal(signal, exit_source="hard_stop")

    async def submit_order(
        self,
        *,
        purpose: str,
        market_ticker: str,
        side: str,
        action: str,
        count: int,
        limit_price_cents: int,
        trigger_price_cents: int,
        reduce_only: bool,
        time_in_force: str = "fill_or_kill",
    ) -> None:
        if self.order_inflight:
            return
        self.order_inflight = True
        try:
            self.logger.info(
                "%s signal | market=%s action=%s side=%s trigger=%s¢ limit=%s¢ qty=%s book_ready=%s",
                purpose.upper(),
                market_ticker,
                action,
                side,
                trigger_price_cents,
                limit_price_cents,
                count,
                self.orderbook.snapshot_ready,
            )
            self.run_position_safety_checks(market_ticker, purpose, side=side, count=count)
            if purpose == "entry":
                self.note_entry_attempt_for_cooldown(market_ticker, side)
            client_order_id = f"btc15m-{purpose}-{uuid.uuid4()}"
            trigger_seen_at = utc_now().isoformat()
            self.log_latency_metrics(trigger_seen_at, purpose)
            self.logger.info("Order routing | purpose=%s tif=%s", purpose, time_in_force)
            if self.config.dry_run:
                order_id = f"dry-run-{uuid.uuid4()}"
                self.state.pending_order = PendingOrder(
                    purpose=purpose,
                    order_id=order_id,
                    client_order_id=client_order_id,
                    market_ticker=market_ticker,
                    side=side,
                    action=action,
                    count=count,
                    limit_price_cents=limit_price_cents,
                    submitted_at=utc_now().isoformat(),
                    trigger_price_cents=trigger_price_cents,
                    trigger_seen_at=trigger_seen_at,
                    time_in_force=time_in_force,
                )
                self.logger.info(
                    "DRY RUN order queued | purpose=%s market=%s action=%s side=%s qty=%s limit=%s¢ client_order_id=%s",
                    purpose,
                    market_ticker,
                    action,
                    side,
                    count,
                    limit_price_cents,
                    client_order_id,
                )
                self.save_state()
                return

            start = time.monotonic()
            try:
                response = await asyncio.to_thread(
                    self.client.create_order,
                    ticker=market_ticker,
                    side=side,
                    action=action,
                    count=count,
                    limit_price_cents=limit_price_cents,
                    reduce_only=reduce_only,
                    time_in_force=time_in_force,
                    client_order_id=client_order_id,
                )
            except Exception as exc:  # noqa: BLE001
                if purpose == "entry":
                    self.entry_retry_block_until_monotonic = time.monotonic() + 1.0
                    self.note_entry_rejection(
                        market_ticker=market_ticker,
                        side=side,
                        time_in_force=time_in_force,
                        exc=exc,
                    )
                if purpose == "exit":
                    self.exit_retry_block_until_monotonic = time.monotonic() + 1.0
                if purpose == "entry" and action == "buy":
                    self.logger.info(
                        "Entry rejection diagnostics | market=%s side=%s qty=%s limit=%s cents tif=%s book=%s",
                        market_ticker,
                        side,
                        count,
                        limit_price_cents,
                        time_in_force,
                        self.describe_live_buy_book(side),
                    )
                self.logger.exception(
                    "Order submission failed | purpose=%s market=%s action=%s side=%s qty=%s limit=%s tif=%s error=%s",
                    purpose,
                    market_ticker,
                    action,
                    side,
                    count,
                    limit_price_cents,
                    time_in_force,
                    exc,
                )
                return
            submit_latency_ms = (time.monotonic() - start) * 1000.0
            order = response["order"]
            order_id = str(order["order_id"])
            status = str(order.get("status") or "").lower()
            fill_count = safe_int(order.get("fill_count")) or decimal_to_int(to_decimal(order.get("fill_count_fp"))) or 0
            remaining_count = safe_int(order.get("remaining_count")) or decimal_to_int(to_decimal(order.get("remaining_count_fp"))) or 0
            actual_fill_price_cents = extract_order_fill_price_cents(order, fill_count=fill_count)
            actual_fee_cents = extract_order_fee_cents(order, fill_count=fill_count)
            self.market_outcomes.mark_submit_latency(market_ticker, submit_latency_ms)
            self.logger.info(
                "Order submitted | purpose=%s order_id=%s status=%s fill_count=%s remaining=%s tif=%s submit_latency_ms=%.1f actual_fill=%s",
                purpose,
                order_id,
                status,
                fill_count,
                remaining_count,
                time_in_force,
                submit_latency_ms,
                f"{actual_fill_price_cents}c" if actual_fill_price_cents is not None else "NA",
            )
            self.state.pending_order = PendingOrder(
                purpose=purpose,
                order_id=order_id,
                client_order_id=client_order_id,
                market_ticker=market_ticker,
                side=side,
                action=action,
                count=count,
                limit_price_cents=limit_price_cents,
                submitted_at=utc_now().isoformat(),
                trigger_price_cents=trigger_price_cents,
                trigger_seen_at=trigger_seen_at,
                time_in_force=time_in_force,
            )
            self.save_state()
            if fill_count <= 0 and status == "canceled":
                self.logger.warning(
                    "%s IOC returned canceled with zero fill | market=%s side=%s qty=%s limit=%sc order_id=%s",
                    purpose.upper(),
                    market_ticker,
                    side,
                    count,
                    limit_price_cents,
                    order_id,
                )
                self.state.pending_order = None
                if purpose == "exit":
                    self.exit_retry_block_until_monotonic = time.monotonic() + 1.0
                if purpose == "entry" and time_in_force == "immediate_or_cancel":
                    self.market_outcomes.mark_ioc_zero_fill(market_ticker)
                self.save_state()
                return
            if fill_count > 0 and (fill_count >= count or status in {"executed", "canceled"}):
                if purpose == "entry":
                    entry_fill_cents = actual_fill_price_cents or limit_price_cents
                    entry_fee_cents = actual_fee_cents if actual_fee_cents is not None else self.estimated_order_fee_cents(entry_fill_cents, fill_count)
                    self.record_entry_fill_for_outcomes(
                        market_ticker=market_ticker,
                        side=side,
                        fill_count=fill_count,
                        fill_price_cents=entry_fill_cents,
                        trigger_price_cents=trigger_price_cents,
                        actual_fee_cents=actual_fee_cents,
                    )
                    position = self.apply_entry_fill_to_position(
                        market_ticker=market_ticker,
                        side=side,
                        fill_count=fill_count,
                        entry_order_id=order_id,
                        entry_limit_price_cents=limit_price_cents,
                        entry_fill_price_cents=entry_fill_cents,
                        entry_fee_cents=entry_fee_cents,
                        entry_trigger_price_cents=trigger_price_cents,
                    )
                    self.mark_traded(market_ticker)
                    self.arm_post_entry_shadow_watch(
                        market_ticker=market_ticker,
                        side=side,
                        filled_at_iso=position.filled_at,
                        entry_fill_cents=entry_fill_cents,
                        entry_trigger_cents=trigger_price_cents,
                        entry_limit_cents=limit_price_cents,
                        seconds_to_close_at_entry=self.seconds_to_close(),
                        book_age_ms_at_entry=self.current_book_age_ms(),
                        eligible_depth_at_entry=self.orderbook.executable_buy_depth(side, limit_price_cents),
                        executable_window_ms_at_entry=None,
                        entry_origin="submit_order_immediate_fill",
                    )
                    if actual_fill_price_cents is not None:
                        self.logger.info(
                            "ENTRY immediate fill | market=%s side=%s qty=%s limit=%sc fill=%sc",
                            market_ticker,
                            side,
                            fill_count or count,
                            limit_price_cents,
                            actual_fill_price_cents,
                        )
                    else:
                        self.logger.info(
                            "ENTRY immediate fill | market=%s side=%s qty=%s limit=%sc",
                            market_ticker,
                            side,
                            fill_count or count,
                            limit_price_cents,
                        )
                else:
                    if actual_fill_price_cents is not None:
                        self.logger.info("EXIT immediate fill | market=%s side=%s qty=%s fill=%sc", market_ticker, side, fill_count or count, actual_fill_price_cents)
                    else:
                        self.logger.info("EXIT immediate fill | market=%s side=%s qty=%s", market_ticker, side, fill_count or count)
                    remaining_position = max(0, (self.state.position.count if self.state.position else count) - fill_count)
                    if actual_fill_price_cents is not None:
                        self.record_exit_fill_for_outcomes(
                            market_ticker=market_ticker,
                            fill_count=fill_count,
                            fill_price_cents=actual_fill_price_cents,
                            remaining_position=remaining_position,
                            actual_fee_cents=actual_fee_cents,
                        )
                    if remaining_position > 0 and self.state.position:
                        self.state.position.count = remaining_position
                    else:
                        self.state.position = None
                self.state.pending_order = None
                self.save_state()
        finally:
            self.order_inflight = False

    def log_latency_metrics(self, trigger_seen_at_iso: str, purpose: str) -> None:
        local_received = self.market.local_received_monotonic
        msg_time = parse_ws_time(self.market.updated_time)
        now = utc_now()
        feed_age_ms: float | None = None
        if msg_time:
            feed_age_ms = (now - msg_time).total_seconds() * 1000.0
        local_reaction_ms: float | None = None
        if local_received is not None:
            local_reaction_ms = (time.monotonic() - local_received) * 1000.0
        self.logger.info(
            "Latency | purpose=%s feed_age_ms=%s local_reaction_ms=%s trigger_seen_at=%s market_msg_time=%s",
            purpose,
            f"{feed_age_ms:.1f}" if feed_age_ms is not None else "?",
            f"{local_reaction_ms:.1f}" if local_reaction_ms is not None else "?",
            trigger_seen_at_iso,
            self.market.updated_time,
        )

    def run_position_safety_checks(
        self,
        market_ticker: str,
        purpose: str,
        *,
        side: str | None = None,
        count: int | None = None,
    ) -> None:
        if normalize_ticker(market_ticker).startswith(ALLOWED_TICKER_PREFIX) is False:
            raise ValueError(f"Refusing to trade non BTC15m ticker: {market_ticker}")
        if purpose == "entry":
            if self.state.pending_order is not None:
                raise ValueError("Refusing entry while pending order already exists.")
            reason = self.entry_block_reason(market_ticker, side, count)
            if reason is not None:
                raise ValueError(f"Refusing entry: {reason}.")
        if purpose == "exit":
            if self.state.position is None:
                raise ValueError("Refusing exit because no position state exists.")
            if self.state.position.market_ticker != market_ticker:
                raise ValueError("Refusing exit because position ticker does not match watch ticker.")
            if side is not None and self.state.position.side != side:
                raise ValueError("Refusing exit because position side does not match order side.")

    def maybe_log_heartbeat(self) -> None:
        now_mono = time.monotonic()
        if now_mono - self.last_heartbeat_monotonic < self.config.heartbeat_log_seconds:
            return
        self.last_heartbeat_monotonic = now_mono
        yes_bid_log, yes_ask_log, no_bid_log, no_ask_log = self.derived_quote_values()
        self.record_price_history_point(force=True)

        self.logger.info(
            "Heartbeat | watch=%s yes_bid=%s yes_ask=%s no_bid=%s no_ask=%s book_ready=%s position=%s pending=%s dry_run=%s trust=%s run_id=%s",
            self.current_watch_ticker,
            yes_bid_log,
            yes_ask_log,
            no_bid_log,
            no_ask_log,
            self.orderbook.snapshot_ready,
            bool(self.state.position),
            bool(self.state.pending_order),
            self.config.dry_run,
            self.orderbook.trust.trust_state,
            self.config.run_id,
        )

    def derived_quote_values(self) -> tuple[int | None, int | None, int | None, int | None]:
        yes_bid_log = self.market.yes_bid_cents
        yes_ask_log = self.market.yes_ask_cents
        no_bid_log = self.market.no_bid_cents
        no_ask_log = self.market.no_ask_cents
        if no_bid_log is None and yes_ask_log is not None:
            no_bid_log = 100 - yes_ask_log
        if no_ask_log is None and yes_bid_log is not None:
            no_ask_log = 100 - yes_bid_log
        if yes_ask_log is None and no_bid_log is not None:
            yes_ask_log = 100 - no_bid_log
        if yes_bid_log is None and no_ask_log is not None:
            yes_bid_log = 100 - no_ask_log
        return yes_bid_log, yes_ask_log, no_bid_log, no_ask_log

    def record_price_history_point(self, *, force: bool = False) -> None:
        now_mono = time.monotonic()
        if (not force) and (now_mono - self.last_price_history_append_monotonic) < 0.2:
            return
        yes_bid_log, yes_ask_log, no_bid_log, no_ask_log = self.derived_quote_values()
        yes_bid_size = float(self.market.yes_bid_size) if self.market.yes_bid_size is not None else 0.0
        no_bid_size = float(self.market.no_bid_size) if self.market.no_bid_size is not None else 0.0
        depth_total = yes_bid_size + no_bid_size
        depth_imbalance = ((yes_bid_size - no_bid_size) / depth_total) if depth_total > 0 else 0.0
        self.recent_price_history.append(
            {
                "market": self.current_watch_ticker,
                "yes_bid": yes_bid_log,
                "yes_ask": yes_ask_log,
                "no_bid": no_bid_log,
                "no_ask": no_ask_log,
                "yes_bid_size": yes_bid_size,
                "no_bid_size": no_bid_size,
                "depth_imbalance": round(depth_imbalance, 6),
                "seconds_to_close": self.seconds_to_close(),
                "ts_mono": now_mono,
                "ts": utc_now().isoformat(),
            }
        )
        self.last_price_history_append_monotonic = now_mono

    def request_market_reaction(self) -> None:
        if self.market_reaction_task and not self.market_reaction_task.done():
            return
        self.market_reaction_task = asyncio.create_task(self.react_to_market_update())

    async def react_to_market_update(self) -> None:
        if self.shutdown_event.is_set() or self.current_watch_ticker is None:
            return
        try:
            await self.maybe_check_pending_order()
            await self.maybe_check_entry()
            await self.maybe_check_exit()
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("Market reaction error for %s: %s", self.current_watch_ticker, exc)


def build_logger(level_name: str, log_path: Path) -> logging.Logger:
    logger = logging.getLogger("kalshi_btc15m_bot_ws")
    logger.setLevel(getattr(logging, level_name.upper(), logging.INFO))
    logger.handlers.clear()
    logger.propagate = False
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(formatter)
    logger.addHandler(stream)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def load_config() -> Config:
    load_dotenv(SCRIPT_DIR / ".env")
    api_key_id = require_env("KALSHI_API_KEY_ID")
    private_key_path = Path(require_env("KALSHI_PRIVATE_KEY_PATH"))
    if not private_key_path.is_absolute():
        private_key_path = (SCRIPT_DIR / private_key_path).resolve()
    base_url = os.getenv("KALSHI_BASE_URL", PROD_BASE_URL).strip().rstrip("/")
    ws_url = os.getenv("KALSHI_WS_URL", derive_ws_url(base_url)).strip().rstrip("/")
    target_entry_odds_cents = int(os.getenv("TARGET_ENTRY_ODDS_CENTS", "90"))
    exit_drop_odds_cents = int(os.getenv("EXIT_DROP_ODDS_CENTS", "60"))
    strategy_tag = sanitize_strategy_tag(
        os.getenv("STRATEGY_TAG", build_strategy_tag(target_entry_odds_cents, exit_drop_odds_cents))
    )
    storage_tag = sanitize_strategy_tag(os.getenv("BOT_STORAGE_TAG", strategy_tag))
    state_path, log_path = resolve_strategy_paths(storage_tag)
    execution_telemetry_path = Path(os.getenv("EXECUTION_TELEMETRY_PATH", str(resolve_execution_telemetry_path(storage_tag)))).expanduser()
    if not execution_telemetry_path.is_absolute():
        execution_telemetry_path = (SCRIPT_DIR / execution_telemetry_path).resolve()
    truffle_regime_lease_cache_path = Path(
        os.getenv("TRUFFLE_REGIME_LEASE_CACHE_PATH", str(resolve_truffle_regime_lease_cache_path(storage_tag)))
    ).expanduser()
    if not truffle_regime_lease_cache_path.is_absolute():
        truffle_regime_lease_cache_path = (SCRIPT_DIR / truffle_regime_lease_cache_path).resolve()
    truffle_regime_lease_events_path = Path(
        os.getenv("TRUFFLE_REGIME_LEASE_EVENTS_PATH", str(resolve_truffle_regime_lease_events_path(storage_tag)))
    ).expanduser()
    if not truffle_regime_lease_events_path.is_absolute():
        truffle_regime_lease_events_path = (SCRIPT_DIR / truffle_regime_lease_events_path).resolve()
    truffle_regime_lease_outcomes_path = Path(
        os.getenv("TRUFFLE_REGIME_LEASE_OUTCOMES_PATH", str(resolve_recent_market_outcomes_path(storage_tag)))
    ).expanduser()
    if not truffle_regime_lease_outcomes_path.is_absolute():
        truffle_regime_lease_outcomes_path = (SCRIPT_DIR / truffle_regime_lease_outcomes_path).resolve()
    truffle_regime_lease_prompt_path = Path(
        os.getenv("TRUFFLE_REGIME_LEASE_PROMPT_PATH", str(SCRIPT_DIR / "truffle_regime_lease_prompt.txt"))
    ).expanduser()
    if not truffle_regime_lease_prompt_path.is_absolute():
        truffle_regime_lease_prompt_path = (SCRIPT_DIR / truffle_regime_lease_prompt_path).resolve()
    truffle_regime_lease_tool_prompt_path = Path(
        os.getenv("TRUFFLE_REGIME_LEASE_TOOL_PROMPT_PATH", str(SCRIPT_DIR / "truffle_regime_lease_tool_prompt.txt"))
    ).expanduser()
    if not truffle_regime_lease_tool_prompt_path.is_absolute():
        truffle_regime_lease_tool_prompt_path = (SCRIPT_DIR / truffle_regime_lease_tool_prompt_path).resolve()
    truffle_post_entry_shadow_events_path = Path(
        os.getenv("TRUFFLE_POST_ENTRY_SHADOW_EVENTS_PATH", str(resolve_truffle_post_entry_shadow_events_path(storage_tag)))
    ).expanduser()
    if not truffle_post_entry_shadow_events_path.is_absolute():
        truffle_post_entry_shadow_events_path = (SCRIPT_DIR / truffle_post_entry_shadow_events_path).resolve()
    truffle_post_entry_shadow_prompt_path = Path(
        os.getenv("TRUFFLE_POST_ENTRY_SHADOW_PROMPT_PATH", str(SCRIPT_DIR / "truffle_post_entry_shadow_prompt.txt"))
    ).expanduser()
    if not truffle_post_entry_shadow_prompt_path.is_absolute():
        truffle_post_entry_shadow_prompt_path = (SCRIPT_DIR / truffle_post_entry_shadow_prompt_path).resolve()
    config = Config(
        api_key_id=api_key_id,
        private_key_path=private_key_path,
        base_url=base_url,
        ws_url=ws_url,
        series_ticker=os.getenv("KALSHI_SERIES_TICKER", ALLOWED_SERIES_TICKER).strip(),
        target_entry_odds_cents=target_entry_odds_cents,
        exit_drop_odds_cents=exit_drop_odds_cents,
        exit_stop_loss_enabled=parse_bool(os.getenv("EXIT_STOP_LOSS_ENABLED", "true")),
        position_size=int(os.getenv("POSITION_SIZE", "2")),
        multi_entry_same_market_enabled=parse_bool(os.getenv("MULTI_ENTRY_SAME_MARKET_ENABLED", "false")),
        multi_entry_max_position_contracts=int(os.getenv("MULTI_ENTRY_MAX_POSITION_CONTRACTS", os.getenv("POSITION_SIZE", "2"))),
        multi_entry_min_seconds_between_entries=float(os.getenv("MULTI_ENTRY_MIN_SECONDS_BETWEEN_ENTRIES", "120")),
        post_fill_exit_delay_seconds=float(os.getenv("POST_FILL_EXIT_DELAY_SECONDS", "30")),
        rest_poll_seconds=float(os.getenv("REST_ORDER_POLL_SECONDS", "1.0")),
        decision_loop_seconds=float(os.getenv("DECISION_LOOP_SECONDS", "0.05")),
        active_market_refresh_seconds=float(os.getenv("ACTIVE_MARKET_REFRESH_SECONDS", "1.0")),
        active_market_retry_seconds=float(os.getenv("ACTIVE_MARKET_RETRY_SECONDS", "1.0")),
        websocket_reconnect_seconds=float(os.getenv("WEBSOCKET_RECONNECT_SECONDS", "1.0")),
        heartbeat_log_seconds=float(os.getenv("HEARTBEAT_LOG_SECONDS", "15.0")),
        orderbook_depth=int(os.getenv("ORDERBOOK_DEPTH", "20")),
        http_timeout_seconds=float(os.getenv("HTTP_TIMEOUT_SECONDS", "5.0")),
        dry_run=parse_bool(os.getenv("DRY_RUN", "true")),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip(),
        strategy_tag=strategy_tag,
        run_id=os.getenv("RUN_ID", str(uuid.uuid4())).strip() or str(uuid.uuid4()),
        state_path=state_path,
        log_path=log_path,
        execution_telemetry_enabled=parse_bool(os.getenv("EXECUTION_TELEMETRY_ENABLED", "true")),
        execution_telemetry_path=execution_telemetry_path,
        pre_entry_stddev_filter_enabled=parse_bool(os.getenv("PRE_ENTRY_STDDEV_FILTER_ENABLED", "false")),
        pre_entry_stddev_threshold=float(os.getenv("PRE_ENTRY_STDDEV_THRESHOLD", "0")),
        pre_entry_stddev_lookback_points=int(os.getenv("PRE_ENTRY_STDDEV_LOOKBACK_POINTS", "8")),
        liquidity_dwell_entry_enabled=parse_bool(os.getenv("LIQUIDITY_DWELL_ENTRY_ENABLED", "false")),
        liquidity_dwell_delay_seconds=float(os.getenv("LIQUIDITY_DWELL_DELAY_SECONDS", "120")),
        liquidity_dwell_max_entry_ask=int(os.getenv("LIQUIDITY_DWELL_MAX_ENTRY_ASK", "90")),
        liquidity_dwell_max_opp_pressure=float(os.getenv("LIQUIDITY_DWELL_MAX_OPP_PRESSURE", "0.5")),
        liquidity_dwell_max_spread=float(os.getenv("LIQUIDITY_DWELL_MAX_SPREAD", "10")),
        liquidity_dwell_min_bid_sum=float(os.getenv("LIQUIDITY_DWELL_MIN_BID_SUM", "0")),
        liquidity_dwell_min_quality_seconds=float(os.getenv("LIQUIDITY_DWELL_MIN_QUALITY_SECONDS", "10")),
        liquidity_dwell_min_quality_share=float(os.getenv("LIQUIDITY_DWELL_MIN_QUALITY_SHARE", "0.65")),
        live_entry_base_book_age_ms=float(os.getenv("LIVE_ENTRY_BASE_BOOK_AGE_MS", "250")),
        live_entry_final_minute_book_age_ms=float(os.getenv("LIVE_ENTRY_FINAL_MINUTE_BOOK_AGE_MS", "150")),
        live_entry_final_seconds_book_age_ms=float(os.getenv("LIVE_ENTRY_FINAL_SECONDS_BOOK_AGE_MS", "80")),
        live_entry_skip_seconds_to_close=float(os.getenv("LIVE_ENTRY_SKIP_SECONDS_TO_CLOSE", "8")),
        live_entry_extreme_odds_cents=int(os.getenv("LIVE_ENTRY_EXTREME_ODDS_CENTS", "89")),
        live_entry_allow_ioc=parse_bool(os.getenv("LIVE_ENTRY_ALLOW_IOC", "true")),
        live_entry_ioc_first=parse_bool(os.getenv("LIVE_ENTRY_IOC_FIRST", "true")),
        live_entry_default_tif=os.getenv("LIVE_ENTRY_DEFAULT_TIF", "immediate_or_cancel").strip().lower(),
        live_entry_allow_fok_when_full_depth=parse_bool(os.getenv("LIVE_ENTRY_ALLOW_FOK_WHEN_FULL_DEPTH", "true")),
        live_entry_min_visible_depth_for_ioc=int(os.getenv("LIVE_ENTRY_MIN_VISIBLE_DEPTH_FOR_IOC", "1")),
        live_entry_book_diagnostics_levels=int(os.getenv("LIVE_ENTRY_BOOK_DIAGNOSTICS_LEVELS", "4")),
        exit_book_diagnostics_levels=int(os.getenv("EXIT_BOOK_DIAGNOSTICS_LEVELS", os.getenv("LIVE_ENTRY_BOOK_DIAGNOSTICS_LEVELS", "4"))),
        exit_mode_selection_enabled=parse_bool(os.getenv("EXIT_MODE_SELECTION_ENABLED", "true")),
        exit_max_book_age_ms=float(os.getenv("EXIT_MAX_BOOK_AGE_MS", "150")),
        exit_confirm_checks=int(os.getenv("EXIT_CONFIRM_CHECKS", "2")),
        exit_confirm_seconds=float(os.getenv("EXIT_CONFIRM_SECONDS", "15")),
        exit_panic_odds_cents=int(os.getenv("EXIT_PANIC_ODDS_CENTS", "74")),
        exit_single_order_depth_multiple=float(os.getenv("EXIT_SINGLE_ORDER_DEPTH_MULTIPLE", "1.25")),
        exit_adaptive_slice_enabled=parse_bool(os.getenv("EXIT_ADAPTIVE_SLICE_ENABLED", "true")),
        exit_adaptive_slice_alpha=float(os.getenv("EXIT_ADAPTIVE_SLICE_ALPHA", "0.35")),
        exit_adaptive_slice_min_contracts=int(os.getenv("EXIT_ADAPTIVE_SLICE_MIN_CONTRACTS", "2")),
        exit_adaptive_slice_max_contracts=int(os.getenv("EXIT_ADAPTIVE_SLICE_MAX_CONTRACTS", "10")),
        exit_slice_delay_ms=float(os.getenv("EXIT_SLICE_DELAY_MS", "0")),
        exit_max_retry_steps=int(os.getenv("EXIT_MAX_RETRY_STEPS", "2")),
        exit_retry_tick_step_cents=int(os.getenv("EXIT_RETRY_TICK_STEP_CENTS", "1")),
        exit_retry_backoff_ms=float(os.getenv("EXIT_RETRY_BACKOFF_MS", "150")),
        exit_rebuild_on_zero_fill=parse_bool(os.getenv("EXIT_REBUILD_ON_ZERO_FILL", "true")),
        exit_reprice_on_partial_fill=parse_bool(os.getenv("EXIT_REPRICE_ON_PARTIAL_FILL", "true")),
        exit_panic_max_cross_cents=int(os.getenv("EXIT_PANIC_MAX_CROSS_CENTS", "3")),
        live_entry_slice_enabled=parse_bool(os.getenv("LIVE_ENTRY_SLICE_ENABLED", "true")),
        live_entry_slice_pattern=parse_int_tuple(os.getenv("LIVE_ENTRY_SLICE_PATTERN", "2,3")),
        live_entry_slice_delay_ms=float(os.getenv("LIVE_ENTRY_SLICE_DELAY_MS", "0")),
        live_entry_slice_stop_on_zero_fill=parse_bool(os.getenv("LIVE_ENTRY_SLICE_STOP_ON_ZERO_FILL", "true")),
        live_entry_partial_completion_enabled=parse_bool(os.getenv("LIVE_ENTRY_PARTIAL_COMPLETION_ENABLED", "true")),
        live_entry_partial_completion_seconds=float(os.getenv("LIVE_ENTRY_PARTIAL_COMPLETION_SECONDS", "15")),
        live_entry_partial_completion_min_price_cents=int(os.getenv("LIVE_ENTRY_PARTIAL_COMPLETION_MIN_PRICE_CENTS", "85")),
        live_entry_partial_completion_max_price_cents=int(os.getenv("LIVE_ENTRY_PARTIAL_COMPLETION_MAX_PRICE_CENTS", os.getenv("TARGET_ENTRY_ODDS_CENTS", "90"))),
        live_entry_partial_completion_retry_delay_ms=float(os.getenv("LIVE_ENTRY_PARTIAL_COMPLETION_RETRY_DELAY_MS", "150")),
        live_entry_dead_market_suppression_ms=float(os.getenv("LIVE_ENTRY_DEAD_MARKET_SUPPRESSION_MS", "2000")),
        live_entry_material_book_change_ticks=int(os.getenv("LIVE_ENTRY_MATERIAL_BOOK_CHANGE_TICKS", "1")),
        live_entry_stale_suppression_ms=float(os.getenv("LIVE_ENTRY_STALE_SUPPRESSION_MS", "100")),
        live_entry_stale_depth_change_contracts=int(os.getenv("LIVE_ENTRY_STALE_DEPTH_CHANGE_CONTRACTS", "5")),
        live_entry_blocked_suppression_ms=float(os.getenv("LIVE_ENTRY_BLOCKED_SUPPRESSION_MS", "250")),
        live_entry_single_order_depth_multiple=float(os.getenv("LIVE_ENTRY_SINGLE_ORDER_DEPTH_MULTIPLE", "3.0")),
        live_entry_adaptive_slice_enabled=parse_bool(os.getenv("LIVE_ENTRY_ADAPTIVE_SLICE_ENABLED", "true")),
        live_entry_adaptive_slice_alpha=float(os.getenv("LIVE_ENTRY_ADAPTIVE_SLICE_ALPHA", "0.2")),
        live_entry_adaptive_slice_min_contracts=int(os.getenv("LIVE_ENTRY_ADAPTIVE_SLICE_MIN_CONTRACTS", "2")),
        live_entry_adaptive_slice_max_contracts=int(os.getenv("LIVE_ENTRY_ADAPTIVE_SLICE_MAX_CONTRACTS", "5")),
        live_entry_fast_fill_gate_enabled=parse_bool(os.getenv("LIVE_ENTRY_FAST_FILL_GATE_ENABLED", "true")),
        live_entry_fast_fill_min_seconds_to_close=float(os.getenv("LIVE_ENTRY_FAST_FILL_MIN_SECONDS_TO_CLOSE", "60")),
        live_entry_fast_fill_min_depth_contracts=int(os.getenv("LIVE_ENTRY_FAST_FILL_MIN_DEPTH_CONTRACTS", "2")),
        live_entry_fast_fill_min_window_ms=float(os.getenv("LIVE_ENTRY_FAST_FILL_MIN_WINDOW_MS", "150")),
        live_entry_fast_fill_slippage_budget_cents=int(os.getenv("LIVE_ENTRY_FAST_FILL_SLIPPAGE_BUDGET_CENTS", "1")),
        live_entry_fast_fill_min_net_edge_cents=int(os.getenv("LIVE_ENTRY_FAST_FILL_MIN_NET_EDGE_CENTS", "4")),
        live_account_state_poll_seconds=float(os.getenv("LIVE_ACCOUNT_STATE_POLL_SECONDS", "1.0")),
        live_account_state_max_age_ms=float(os.getenv("LIVE_ACCOUNT_STATE_MAX_AGE_MS", "1500")),
        live_balance_min_buffer_cents=int(os.getenv("LIVE_BALANCE_MIN_BUFFER_CENTS", "300")),
        live_balance_fee_buffer_cents=int(os.getenv("LIVE_BALANCE_FEE_BUFFER_CENTS", "25")),
        btc_vol_regime_gate_enabled=parse_bool(os.getenv("BTC_VOL_REGIME_GATE_ENABLED", "false")),
        btc_vol_regime_max_range_dollars=float(os.getenv("BTC_VOL_REGIME_MAX_RANGE_DOLLARS", "275")),
        btc_vol_regime_poll_seconds=float(os.getenv("BTC_VOL_REGIME_POLL_SECONDS", "5")),
        btc_vol_regime_lookback_minutes=int(os.getenv("BTC_VOL_REGIME_LOOKBACK_MINUTES", "15")),
        btc_vol_regime_interval=os.getenv("BTC_VOL_REGIME_INTERVAL", "5m").strip().lower(),
        btc_vol_regime_max_age_ms=float(os.getenv("BTC_VOL_REGIME_MAX_AGE_MS", "20000")),
        btc_vol_regime_fail_open=parse_bool(os.getenv("BTC_VOL_REGIME_FAIL_OPEN", "true")),
        mushroom_shadow_enabled=parse_bool(os.getenv("MUSHROOM_SHADOW_ENABLED", "true")),
        mushroom_btc_history_minutes=int(os.getenv("MUSHROOM_BTC_HISTORY_MINUTES", "1800")),
        mushroom_min_p_side=float(os.getenv("MUSHROOM_MIN_P_SIDE", "0.80")),
        mushroom_strict_p_side=float(os.getenv("MUSHROOM_STRICT_P_SIDE", "0.85")),
        mushroom_min_edge_cents_15m=float(os.getenv("MUSHROOM_MIN_EDGE_CENTS_15M", "2.0")),
        mushroom_model_buffer_cents=float(os.getenv("MUSHROOM_MODEL_BUFFER_CENTS", "0.0")),
        mushroom_v21_decision_engine_enabled=parse_bool(os.getenv("MUSHROOM_V21_DECISION_ENGINE_ENABLED", "false")),
        mushroom_v21_min_p_side=float(os.getenv("MUSHROOM_V21_MIN_P_SIDE", "0.80")),
        mushroom_v21_min_edge_cents_15m=float(os.getenv("MUSHROOM_V21_MIN_EDGE_CENTS_15M", "2.0")),
        mushroom_v21_max_ask_cents=int(os.getenv("MUSHROOM_V21_MAX_ASK_CENTS", "90")),
        mushroom_v21_min_seconds_to_close=float(os.getenv("MUSHROOM_V21_MIN_SECONDS_TO_CLOSE", "240")),
        mushroom_v21_max_seconds_to_close=float(os.getenv("MUSHROOM_V21_MAX_SECONDS_TO_CLOSE", "480")),
        mushroom_v21_model_buffer_cents=float(os.getenv("MUSHROOM_V21_MODEL_BUFFER_CENTS", "0.0")),
        mushroom_v21_slippage_cents=float(os.getenv("MUSHROOM_V21_SLIPPAGE_CENTS", "1.0")),
        mushroom_v28_shadow_enabled=parse_bool(os.getenv("MUSHROOM_V28_SHADOW_ENABLED", "true")),
        mushroom_v28_decision_engine_enabled=parse_bool(os.getenv("MUSHROOM_V28_DECISION_ENGINE_ENABLED", "false")),
        mushroom_v28_live_exit_enabled=parse_bool(os.getenv("MUSHROOM_V28_LIVE_EXIT_ENABLED", "false")),
        mushroom_v28_min_p_side=float(os.getenv("MUSHROOM_V28_MIN_P_SIDE", "0.85")),
        mushroom_v28_min_edge_cents_15m=float(os.getenv("MUSHROOM_V28_MIN_EDGE_CENTS_15M", "2.0")),
        mushroom_v28_model_buffer_cents=float(os.getenv("MUSHROOM_V28_MODEL_BUFFER_CENTS", "1.0")),
        mushroom_v28_slippage_cents=float(os.getenv("MUSHROOM_V28_SLIPPAGE_CENTS", "1.0")),
        mushroom_v28_max_ask_cents=int(os.getenv("MUSHROOM_V28_MAX_ASK_CENTS", "90")),
        mushroom_v28_min_seconds_to_close=float(os.getenv("MUSHROOM_V28_MIN_SECONDS_TO_CLOSE", "70")),
        mushroom_v28_max_seconds_to_close=float(os.getenv("MUSHROOM_V28_MAX_SECONDS_TO_CLOSE", "900")),
        mushroom_v28_max_market_risk_cents=int(os.getenv("MUSHROOM_V28_MAX_MARKET_RISK_CENTS", "200")),
        mushroom_v28_btc_max_age_ms=float(os.getenv("MUSHROOM_V28_BTC_MAX_AGE_MS", "1500")),
        mushroom_v28_btc_ws_enabled=parse_bool(os.getenv("MUSHROOM_V28_BTC_WS_ENABLED", "true")),
        mushroom_v28_btc_ws_url=os.getenv("MUSHROOM_V28_BTC_WS_URL", COINBASE_BTC_TICKER_WS_URL).strip() or COINBASE_BTC_TICKER_WS_URL,
        mushroom_v28_btc_ws_fallback_urls=tuple(
            part.strip()
            for part in os.getenv(
                "MUSHROOM_V28_BTC_WS_FALLBACK_URLS",
                f"{BINANCE_US_BTC_BOOK_TICKER_WS_URL},{BINANCE_US_BTC_TRADE_WS_URL}",
            ).split(",")
            if part.strip()
        ),
        mushroom_v28_exit_hysteresis_cents=float(os.getenv("MUSHROOM_V28_EXIT_HYSTERESIS_CENTS", "0.25")),
        mushroom_v28_exit_hold_buffer_cents=float(os.getenv("MUSHROOM_V28_EXIT_HOLD_BUFFER_CENTS", "1.0")),
        mushroom_v28_exit_reduce_p_hold_floor=float(os.getenv("MUSHROOM_V28_EXIT_REDUCE_P_HOLD_FLOOR", "0.80")),
        mushroom_v28_exit_full_p_hold_floor=float(os.getenv("MUSHROOM_V28_EXIT_FULL_P_HOLD_FLOOR", "0.72")),
        mushroom_v28_exit_fair_drawdown_cents=float(os.getenv("MUSHROOM_V28_EXIT_FAIR_DRAWDOWN_CENTS", "8.0")),
        mushroom_v28_exit_full_drawdown_cents=float(os.getenv("MUSHROOM_V28_EXIT_FULL_DRAWDOWN_CENTS", "15.0")),
        mushroom_v28_exit_reduce_fraction=float(os.getenv("MUSHROOM_V28_EXIT_REDUCE_FRACTION", "0.5")),
        live_approved_strategy_tag=sanitize_strategy_tag(os.getenv("LIVE_APPROVED_STRATEGY_TAG", strategy_tag)),
        live_lock_path=SCRIPT_DIR / "state" / "live_trading.lock",
        truffle_regime_lease_mode=os.getenv("TRUFFLE_REGIME_LEASE_MODE", "disabled").strip().lower(),
        truffle_regime_lease_issuer=os.getenv("TRUFFLE_REGIME_LEASE_ISSUER", "stub").strip().lower(),
        truffle_regime_lease_timeout_ms=int(os.getenv("TRUFFLE_REGIME_LEASE_TIMEOUT_MS", "2500")),
        truffle_regime_lease_cache_path=truffle_regime_lease_cache_path,
        truffle_regime_lease_events_path=truffle_regime_lease_events_path,
        truffle_regime_lease_outcomes_path=truffle_regime_lease_outcomes_path,
        truffle_regime_lease_fail_closed=parse_bool(os.getenv("TRUFFLE_REGIME_LEASE_FAIL_CLOSED", "true")),
        truffle_regime_lease_prompt_path=truffle_regime_lease_prompt_path,
        truffle_regime_lease_tool_prompt_path=truffle_regime_lease_tool_prompt_path,
        truffle_regime_lease_max_staleness_seconds=float(os.getenv("TRUFFLE_REGIME_LEASE_MAX_STALENESS_SECONDS", "1800")),
        truffle_regime_lease_endpoint=os.getenv("TRUFFLE_REGIME_LEASE_ENDPOINT", "").strip(),
        truffle_regime_lease_model=os.getenv("TRUFFLE_REGIME_LEASE_MODEL", "").strip(),
        truffle_regime_lease_api_key=os.getenv("TRUFFLE_REGIME_LEASE_API_KEY", os.getenv("OPENAI_API_KEY", "")).strip(),
        truffle_regime_lease_max_tokens=int(os.getenv("TRUFFLE_REGIME_LEASE_MAX_TOKENS", "0")),
        truffle_regime_lease_reasoning_enabled=os.getenv("TRUFFLE_REGIME_LEASE_REASONING_ENABLED", "auto").strip().lower(),
        truffle_post_entry_shadow_enabled=parse_bool(os.getenv("TRUFFLE_POST_ENTRY_SHADOW_ENABLED", "false")),
        truffle_post_entry_shadow_delay_seconds=float(os.getenv("TRUFFLE_POST_ENTRY_SHADOW_DELAY_SECONDS", "90")),
        truffle_post_entry_shadow_timeout_ms=int(os.getenv("TRUFFLE_POST_ENTRY_SHADOW_TIMEOUT_MS", "20000")),
        truffle_post_entry_shadow_events_path=truffle_post_entry_shadow_events_path,
        truffle_post_entry_shadow_prompt_path=truffle_post_entry_shadow_prompt_path,
        truffle_post_entry_shadow_endpoint=os.getenv("TRUFFLE_POST_ENTRY_SHADOW_ENDPOINT", os.getenv("TRUFFLE_REGIME_LEASE_ENDPOINT", "")).strip(),
        truffle_post_entry_shadow_model=os.getenv("TRUFFLE_POST_ENTRY_SHADOW_MODEL", "Qwen3.5-2B").strip() or "Qwen3.5-2B",
        truffle_post_entry_shadow_api_key=os.getenv("TRUFFLE_POST_ENTRY_SHADOW_API_KEY", os.getenv("TRUFFLE_REGIME_LEASE_API_KEY", os.getenv("OPENAI_API_KEY", ""))).strip(),
        truffle_post_entry_shadow_max_tokens=int(os.getenv("TRUFFLE_POST_ENTRY_SHADOW_MAX_TOKENS", str(DEFAULT_POST_ENTRY_SHADOW_MAX_TOKENS))),
        truffle_post_entry_shadow_include_btc_spot=parse_bool(os.getenv("TRUFFLE_POST_ENTRY_SHADOW_INCLUDE_BTC_SPOT", "false")),
        truffle_post_entry_shadow_decision_schema=os.getenv("TRUFFLE_POST_ENTRY_SHADOW_DECISION_SCHEMA", "reversal_risk").strip().lower(),
        truffle_post_entry_shadow_output_mode=os.getenv("TRUFFLE_POST_ENTRY_SHADOW_OUTPUT_MODE", "json").strip().lower(),
        truffle_post_entry_shadow_reasoning_enabled=os.getenv("TRUFFLE_POST_ENTRY_SHADOW_REASONING_ENABLED", "false").strip().lower(),
        truffle_post_entry_shadow_suspicious_only=parse_bool(os.getenv("TRUFFLE_POST_ENTRY_SHADOW_SUSPICIOUS_ONLY", "false")),
        truffle_post_entry_shadow_live_exit_enabled=parse_bool(os.getenv("TRUFFLE_POST_ENTRY_SHADOW_LIVE_EXIT_ENABLED", "false")),
    )
    validate_config(config)
    return config


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise ValueError(f"Missing required environment variable: {name}")
    return value.strip()


def validate_config(config: Config) -> None:
    if normalize_ticker(config.series_ticker) != ALLOWED_SERIES_TICKER:
        raise ValueError(f"KALSHI_SERIES_TICKER must remain locked to {ALLOWED_SERIES_TICKER}")
    if config.position_size <= 0:
        raise ValueError("POSITION_SIZE must be positive")
    if config.multi_entry_max_position_contracts < config.position_size:
        raise ValueError("MULTI_ENTRY_MAX_POSITION_CONTRACTS must be at least POSITION_SIZE")
    if config.multi_entry_min_seconds_between_entries < 0:
        raise ValueError("MULTI_ENTRY_MIN_SECONDS_BETWEEN_ENTRIES must be non-negative")
    if config.target_entry_odds_cents != 90:
        raise ValueError("TARGET_ENTRY_ODDS_CENTS must remain 90")
    if int(config.post_fill_exit_delay_seconds) != 30:
        raise ValueError("POST_FILL_EXIT_DELAY_SECONDS must remain 30")
    if config.pre_entry_stddev_lookback_points < 3:
        raise ValueError("PRE_ENTRY_STDDEV_LOOKBACK_POINTS must be at least 3")
    if config.liquidity_dwell_entry_enabled:
        if config.liquidity_dwell_delay_seconds <= 0:
            raise ValueError("LIQUIDITY_DWELL_DELAY_SECONDS must be > 0")
        if not (1 <= int(config.liquidity_dwell_max_entry_ask) <= 99):
            raise ValueError("LIQUIDITY_DWELL_MAX_ENTRY_ASK must be between 1 and 99")
        if not (0.0 <= float(config.liquidity_dwell_max_opp_pressure) <= 1.0):
            raise ValueError("LIQUIDITY_DWELL_MAX_OPP_PRESSURE must be between 0 and 1")
        if config.liquidity_dwell_max_spread < 0:
            raise ValueError("LIQUIDITY_DWELL_MAX_SPREAD must be non-negative")
        if config.liquidity_dwell_min_quality_seconds < 0:
            raise ValueError("LIQUIDITY_DWELL_MIN_QUALITY_SECONDS must be non-negative")
        if not (0.0 <= float(config.liquidity_dwell_min_quality_share) <= 1.0):
            raise ValueError("LIQUIDITY_DWELL_MIN_QUALITY_SHARE must be between 0 and 1")
    is_current_profile = (
        config.exit_drop_odds_cents in {70, 78}
        and not config.pre_entry_stddev_filter_enabled
    )
    is_legacy_stddev_profile = (
        config.exit_drop_odds_cents == 60
        and config.pre_entry_stddev_filter_enabled
        and config.pre_entry_stddev_threshold > 0
    )
    if not (is_current_profile or is_legacy_stddev_profile):
        raise ValueError(
            "Supported profiles are 90/70 or 90/78 without std-dev filter, or 90/60 with std-dev filter enabled."
        )
    if config.truffle_regime_lease_mode not in VALID_LEASE_MODES:
        raise ValueError(
            f"TRUFFLE_REGIME_LEASE_MODE must be one of {sorted(VALID_LEASE_MODES)}"
        )
    if config.truffle_regime_lease_issuer not in VALID_LEASE_ISSUERS:
        raise ValueError(
            f"TRUFFLE_REGIME_LEASE_ISSUER must be one of {sorted(VALID_LEASE_ISSUERS)}"
        )
    if config.truffle_regime_lease_timeout_ms <= 0:
        raise ValueError("TRUFFLE_REGIME_LEASE_TIMEOUT_MS must be > 0")
    if config.truffle_regime_lease_max_staleness_seconds <= 0:
        raise ValueError("TRUFFLE_REGIME_LEASE_MAX_STALENESS_SECONDS must be > 0")
    if config.truffle_regime_lease_mode == "enforce_entries_only" and config.exit_drop_odds_cents != 78:
        raise ValueError("Truffle regime lease enforcement currently supports only the 90/78 profile.")
    if config.truffle_regime_lease_mode != "disabled" and config.truffle_regime_lease_issuer == "truffle_http":
        if not config.truffle_regime_lease_endpoint:
            raise ValueError("TRUFFLE_REGIME_LEASE_ENDPOINT is required when TRUFFLE_REGIME_LEASE_ISSUER=truffle_http")
        if not config.truffle_regime_lease_model:
            raise ValueError("TRUFFLE_REGIME_LEASE_MODEL is required when TRUFFLE_REGIME_LEASE_ISSUER=truffle_http")
    if config.truffle_regime_lease_max_tokens < 0:
        raise ValueError("TRUFFLE_REGIME_LEASE_MAX_TOKENS must be >= 0")
    if config.truffle_regime_lease_reasoning_enabled not in {"auto", "true", "false"}:
        raise ValueError("TRUFFLE_REGIME_LEASE_REASONING_ENABLED must be auto, true, or false")
    if config.truffle_post_entry_shadow_delay_seconds < 0:
        raise ValueError("TRUFFLE_POST_ENTRY_SHADOW_DELAY_SECONDS must be non-negative")
    if config.truffle_post_entry_shadow_timeout_ms <= 0:
        raise ValueError("TRUFFLE_POST_ENTRY_SHADOW_TIMEOUT_MS must be > 0")
    if config.truffle_post_entry_shadow_max_tokens <= 0:
        raise ValueError("TRUFFLE_POST_ENTRY_SHADOW_MAX_TOKENS must be > 0")
    if config.truffle_post_entry_shadow_decision_schema not in {"reversal_risk", "exit_supervisor"}:
        raise ValueError("TRUFFLE_POST_ENTRY_SHADOW_DECISION_SCHEMA must be reversal_risk or exit_supervisor")
    if config.truffle_post_entry_shadow_output_mode not in {"json", "tool"}:
        raise ValueError("TRUFFLE_POST_ENTRY_SHADOW_OUTPUT_MODE must be json or tool")
    if config.truffle_post_entry_shadow_reasoning_enabled not in {"auto", "true", "false"}:
        raise ValueError("TRUFFLE_POST_ENTRY_SHADOW_REASONING_ENABLED must be auto, true, or false")
    if config.truffle_post_entry_shadow_output_mode == "tool" and config.truffle_post_entry_shadow_decision_schema != "exit_supervisor":
        raise ValueError("TRUFFLE_POST_ENTRY_SHADOW_OUTPUT_MODE=tool requires TRUFFLE_POST_ENTRY_SHADOW_DECISION_SCHEMA=exit_supervisor")
    if config.truffle_post_entry_shadow_enabled:
        if not config.truffle_post_entry_shadow_endpoint:
            raise ValueError("TRUFFLE_POST_ENTRY_SHADOW_ENDPOINT is required when TRUFFLE_POST_ENTRY_SHADOW_ENABLED=true")
        if not config.truffle_post_entry_shadow_model:
            raise ValueError("TRUFFLE_POST_ENTRY_SHADOW_MODEL is required when TRUFFLE_POST_ENTRY_SHADOW_ENABLED=true")
    if config.truffle_post_entry_shadow_live_exit_enabled:
        if not config.truffle_post_entry_shadow_enabled:
            raise ValueError("TRUFFLE_POST_ENTRY_SHADOW_LIVE_EXIT_ENABLED requires TRUFFLE_POST_ENTRY_SHADOW_ENABLED=true")
        if config.truffle_post_entry_shadow_decision_schema != "exit_supervisor":
            raise ValueError("TRUFFLE_POST_ENTRY_SHADOW_LIVE_EXIT_ENABLED requires TRUFFLE_POST_ENTRY_SHADOW_DECISION_SCHEMA=exit_supervisor")
    if config.exit_confirm_checks <= 0:
        raise ValueError("EXIT_CONFIRM_CHECKS must be > 0")
    if config.exit_confirm_seconds < 0:
        raise ValueError("EXIT_CONFIRM_SECONDS must be non-negative")
    if config.exit_panic_odds_cents <= 0:
        raise ValueError("EXIT_PANIC_ODDS_CENTS must be > 0")
    if config.exit_panic_odds_cents > config.exit_drop_odds_cents:
        raise ValueError("EXIT_PANIC_ODDS_CENTS must be <= EXIT_DROP_ODDS_CENTS")
    if config.live_account_state_poll_seconds <= 0:
        raise ValueError("LIVE_ACCOUNT_STATE_POLL_SECONDS must be > 0")
    if config.live_account_state_max_age_ms <= 0:
        raise ValueError("LIVE_ACCOUNT_STATE_MAX_AGE_MS must be > 0")
    if config.live_balance_min_buffer_cents < 0 or config.live_balance_fee_buffer_cents < 0:
        raise ValueError("Live balance buffers must be non-negative")
    if config.live_entry_default_tif not in {"immediate_or_cancel", "fill_or_kill"}:
        raise ValueError("LIVE_ENTRY_DEFAULT_TIF must be immediate_or_cancel or fill_or_kill")
    if config.exit_max_book_age_ms <= 0:
        raise ValueError("EXIT_MAX_BOOK_AGE_MS must be > 0")
    if config.exit_single_order_depth_multiple < 1.0:
        raise ValueError("EXIT_SINGLE_ORDER_DEPTH_MULTIPLE must be >= 1.0")
    if not (0 < config.exit_adaptive_slice_alpha <= 1.0):
        raise ValueError("EXIT_ADAPTIVE_SLICE_ALPHA must be between 0 and 1")
    if config.exit_adaptive_slice_min_contracts <= 0:
        raise ValueError("EXIT_ADAPTIVE_SLICE_MIN_CONTRACTS must be > 0")
    if config.exit_adaptive_slice_max_contracts < config.exit_adaptive_slice_min_contracts:
        raise ValueError("EXIT_ADAPTIVE_SLICE_MAX_CONTRACTS must be >= EXIT_ADAPTIVE_SLICE_MIN_CONTRACTS")
    if config.exit_slice_delay_ms < 0:
        raise ValueError("EXIT_SLICE_DELAY_MS must be non-negative")
    if config.exit_max_retry_steps < 0:
        raise ValueError("EXIT_MAX_RETRY_STEPS must be non-negative")
    if config.exit_retry_tick_step_cents <= 0:
        raise ValueError("EXIT_RETRY_TICK_STEP_CENTS must be > 0")
    if config.exit_retry_backoff_ms < 0:
        raise ValueError("EXIT_RETRY_BACKOFF_MS must be non-negative")
    if config.exit_panic_max_cross_cents < 0:
        raise ValueError("EXIT_PANIC_MAX_CROSS_CENTS must be non-negative")
    if config.live_entry_slice_delay_ms < 0:
        raise ValueError("LIVE_ENTRY_SLICE_DELAY_MS must be non-negative")
    if config.live_entry_partial_completion_seconds < 0:
        raise ValueError("LIVE_ENTRY_PARTIAL_COMPLETION_SECONDS must be non-negative")
    if config.live_entry_partial_completion_min_price_cents <= 0 or config.live_entry_partial_completion_min_price_cents > 99:
        raise ValueError("LIVE_ENTRY_PARTIAL_COMPLETION_MIN_PRICE_CENTS must be between 1 and 99")
    if config.live_entry_partial_completion_max_price_cents <= 0 or config.live_entry_partial_completion_max_price_cents > 99:
        raise ValueError("LIVE_ENTRY_PARTIAL_COMPLETION_MAX_PRICE_CENTS must be between 1 and 99")
    if config.live_entry_partial_completion_min_price_cents > config.live_entry_partial_completion_max_price_cents:
        raise ValueError("LIVE_ENTRY_PARTIAL_COMPLETION_MIN_PRICE_CENTS must be <= LIVE_ENTRY_PARTIAL_COMPLETION_MAX_PRICE_CENTS")
    if config.live_entry_partial_completion_retry_delay_ms < 0:
        raise ValueError("LIVE_ENTRY_PARTIAL_COMPLETION_RETRY_DELAY_MS must be non-negative")
    if config.live_entry_dead_market_suppression_ms < 0:
        raise ValueError("LIVE_ENTRY_DEAD_MARKET_SUPPRESSION_MS must be non-negative")
    if config.live_entry_material_book_change_ticks < 0:
        raise ValueError("LIVE_ENTRY_MATERIAL_BOOK_CHANGE_TICKS must be non-negative")
    if config.live_entry_stale_suppression_ms < 0:
        raise ValueError("LIVE_ENTRY_STALE_SUPPRESSION_MS must be non-negative")
    if config.live_entry_stale_depth_change_contracts < 0:
        raise ValueError("LIVE_ENTRY_STALE_DEPTH_CHANGE_CONTRACTS must be non-negative")
    if config.live_entry_blocked_suppression_ms < 0:
        raise ValueError("LIVE_ENTRY_BLOCKED_SUPPRESSION_MS must be non-negative")
    if config.live_entry_single_order_depth_multiple < 1.0:
        raise ValueError("LIVE_ENTRY_SINGLE_ORDER_DEPTH_MULTIPLE must be >= 1.0")
    if not (0 < config.live_entry_adaptive_slice_alpha <= 1.0):
        raise ValueError("LIVE_ENTRY_ADAPTIVE_SLICE_ALPHA must be between 0 and 1")
    if config.live_entry_adaptive_slice_min_contracts <= 0:
        raise ValueError("LIVE_ENTRY_ADAPTIVE_SLICE_MIN_CONTRACTS must be > 0")
    if config.live_entry_adaptive_slice_max_contracts < config.live_entry_adaptive_slice_min_contracts:
        raise ValueError("LIVE_ENTRY_ADAPTIVE_SLICE_MAX_CONTRACTS must be >= LIVE_ENTRY_ADAPTIVE_SLICE_MIN_CONTRACTS")
    if config.live_entry_fast_fill_min_seconds_to_close < 0:
        raise ValueError("LIVE_ENTRY_FAST_FILL_MIN_SECONDS_TO_CLOSE must be non-negative")
    if config.live_entry_fast_fill_min_depth_contracts < 0:
        raise ValueError("LIVE_ENTRY_FAST_FILL_MIN_DEPTH_CONTRACTS must be non-negative")
    if config.live_entry_fast_fill_min_window_ms < 0:
        raise ValueError("LIVE_ENTRY_FAST_FILL_MIN_WINDOW_MS must be non-negative")
    if config.live_entry_fast_fill_slippage_budget_cents < 0:
        raise ValueError("LIVE_ENTRY_FAST_FILL_SLIPPAGE_BUDGET_CENTS must be non-negative")
    if config.live_entry_fast_fill_min_net_edge_cents < 0:
        raise ValueError("LIVE_ENTRY_FAST_FILL_MIN_NET_EDGE_CENTS must be non-negative")
    if config.btc_vol_regime_max_range_dollars <= 0:
        raise ValueError("BTC_VOL_REGIME_MAX_RANGE_DOLLARS must be positive")
    if config.btc_vol_regime_poll_seconds <= 0:
        raise ValueError("BTC_VOL_REGIME_POLL_SECONDS must be positive")
    if config.btc_vol_regime_lookback_minutes <= 0:
        raise ValueError("BTC_VOL_REGIME_LOOKBACK_MINUTES must be positive")
    if config.btc_vol_regime_max_age_ms <= 0:
        raise ValueError("BTC_VOL_REGIME_MAX_AGE_MS must be positive")
    if config.mushroom_btc_history_minutes < MushroomConfig().min_history_points:
        raise ValueError("MUSHROOM_BTC_HISTORY_MINUTES must be at least the v22 minimum history length")
    if not (0.5 <= float(config.mushroom_min_p_side) <= 1.0):
        raise ValueError("MUSHROOM_MIN_P_SIDE must be between 0.5 and 1.0")
    if not (0.5 <= float(config.mushroom_strict_p_side) <= 1.0):
        raise ValueError("MUSHROOM_STRICT_P_SIDE must be between 0.5 and 1.0")
    if float(config.mushroom_min_edge_cents_15m) < 0:
        raise ValueError("MUSHROOM_MIN_EDGE_CENTS_15M must be non-negative")
    if float(config.mushroom_model_buffer_cents) < 0:
        raise ValueError("MUSHROOM_MODEL_BUFFER_CENTS must be non-negative")
    if not (0.5 <= float(config.mushroom_v21_min_p_side) <= 1.0):
        raise ValueError("MUSHROOM_V21_MIN_P_SIDE must be between 0.5 and 1.0")
    if float(config.mushroom_v21_min_edge_cents_15m) < 0:
        raise ValueError("MUSHROOM_V21_MIN_EDGE_CENTS_15M must be non-negative")
    if not (1 <= int(config.mushroom_v21_max_ask_cents) <= 99):
        raise ValueError("MUSHROOM_V21_MAX_ASK_CENTS must be between 1 and 99")
    if float(config.mushroom_v21_min_seconds_to_close) < 0:
        raise ValueError("MUSHROOM_V21_MIN_SECONDS_TO_CLOSE must be non-negative")
    if float(config.mushroom_v21_max_seconds_to_close) <= float(config.mushroom_v21_min_seconds_to_close):
        raise ValueError("MUSHROOM_V21_MAX_SECONDS_TO_CLOSE must be greater than MUSHROOM_V21_MIN_SECONDS_TO_CLOSE")
    if float(config.mushroom_v21_model_buffer_cents) < 0:
        raise ValueError("MUSHROOM_V21_MODEL_BUFFER_CENTS must be non-negative")
    if float(config.mushroom_v21_slippage_cents) < 0:
        raise ValueError("MUSHROOM_V21_SLIPPAGE_CENTS must be non-negative")
    if not (0.5 <= float(config.mushroom_v28_min_p_side) <= 1.0):
        raise ValueError("MUSHROOM_V28_MIN_P_SIDE must be between 0.5 and 1.0")
    if float(config.mushroom_v28_min_edge_cents_15m) < 0:
        raise ValueError("MUSHROOM_V28_MIN_EDGE_CENTS_15M must be non-negative")
    if float(config.mushroom_v28_model_buffer_cents) < 0:
        raise ValueError("MUSHROOM_V28_MODEL_BUFFER_CENTS must be non-negative")
    if float(config.mushroom_v28_slippage_cents) < 0:
        raise ValueError("MUSHROOM_V28_SLIPPAGE_CENTS must be non-negative")
    if not (1 <= int(config.mushroom_v28_max_ask_cents) <= 99):
        raise ValueError("MUSHROOM_V28_MAX_ASK_CENTS must be between 1 and 99")
    if float(config.mushroom_v28_min_seconds_to_close) < 0:
        raise ValueError("MUSHROOM_V28_MIN_SECONDS_TO_CLOSE must be non-negative")
    if float(config.mushroom_v28_max_seconds_to_close) <= float(config.mushroom_v28_min_seconds_to_close):
        raise ValueError("MUSHROOM_V28_MAX_SECONDS_TO_CLOSE must be greater than MUSHROOM_V28_MIN_SECONDS_TO_CLOSE")
    if int(config.mushroom_v28_max_market_risk_cents) <= 0:
        raise ValueError("MUSHROOM_V28_MAX_MARKET_RISK_CENTS must be positive")
    if float(config.mushroom_v28_btc_max_age_ms) <= 0:
        raise ValueError("MUSHROOM_V28_BTC_MAX_AGE_MS must be positive")
    if float(config.mushroom_v28_exit_hysteresis_cents) < 0:
        raise ValueError("MUSHROOM_V28_EXIT_HYSTERESIS_CENTS must be non-negative")
    if float(config.mushroom_v28_exit_hold_buffer_cents) < 0:
        raise ValueError("MUSHROOM_V28_EXIT_HOLD_BUFFER_CENTS must be non-negative")
    if not (0.0 <= float(config.mushroom_v28_exit_full_p_hold_floor) <= float(config.mushroom_v28_exit_reduce_p_hold_floor) <= 1.0):
        raise ValueError("MUSHROOM_V28_EXIT probability floors must be ordered between 0 and 1")
    if float(config.mushroom_v28_exit_fair_drawdown_cents) < 0 or float(config.mushroom_v28_exit_full_drawdown_cents) < 0:
        raise ValueError("MUSHROOM_V28_EXIT drawdown cents must be non-negative")
    if float(config.mushroom_v28_exit_full_drawdown_cents) < float(config.mushroom_v28_exit_fair_drawdown_cents):
        raise ValueError("MUSHROOM_V28_EXIT_FULL_DRAWDOWN_CENTS must be >= MUSHROOM_V28_EXIT_FAIR_DRAWDOWN_CENTS")
    if not (0.0 < float(config.mushroom_v28_exit_reduce_fraction) <= 1.0):
        raise ValueError("MUSHROOM_V28_EXIT_REDUCE_FRACTION must be between 0 and 1")
    if not config.dry_run:
        approved_live_tag = sanitize_strategy_tag(config.live_approved_strategy_tag)
        if not approved_live_tag:
            raise ValueError("LIVE_APPROVED_STRATEGY_TAG must be set when DRY_RUN=false")
        if sanitize_strategy_tag(config.strategy_tag) != approved_live_tag:
            raise ValueError(
                f"DRY_RUN=false is only allowed for strategy tag {approved_live_tag}; got {config.strategy_tag}"
            )
    if config.base_url not in {PROD_BASE_URL, DEMO_BASE_URL}:
        raise ValueError("KALSHI_BASE_URL must be the production or demo Trade API base URL")
    if config.ws_url not in {PROD_WS_URL, DEMO_WS_URL}:
        raise ValueError("KALSHI_WS_URL must be the production or demo WebSocket URL")
    if not config.private_key_exists:
        raise FileNotFoundError(f"Private key file not found at {config.private_key_path}")


def derive_ws_url(base_url: str) -> str:
    if base_url.rstrip("/") == PROD_BASE_URL:
        return PROD_WS_URL
    if base_url.rstrip("/") == DEMO_BASE_URL:
        return DEMO_WS_URL
    raise ValueError(f"Unsupported base URL for ws derivation: {base_url}")


def normalize_ticker(ticker: str) -> str:
    return ticker.strip().upper()


def parse_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def parse_int_tuple(value: str | None) -> tuple[int, ...]:
    parts = [part.strip() for part in str(value or "").split(",")]
    out: list[int] = []
    for part in parts:
        if not part:
            continue
        with contextlib.suppress(ValueError):
            parsed = int(part)
            if parsed > 0:
                out.append(parsed)
    return tuple(out)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    with contextlib.suppress(ValueError):
        return datetime.fromisoformat(text)
    return None


def parse_ws_time(value: str | None) -> datetime | None:
    if not value:
        return None
    dt = parse_iso(value)
    if dt:
        return dt
    if str(value).isdigit():
        return datetime.fromtimestamp(int(str(value)), tz=timezone.utc)
    return None


def is_resting_order(order: dict[str, Any]) -> bool:
    status = str(order.get("status") or order.get("order_status") or "").strip().lower()
    if status in {"resting", "open", "pending"}:
        return True
    if status in {"executed", "filled", "canceled", "cancelled", "rejected", "expired"}:
        return False
    remaining_count = (
        safe_int(order.get("remaining_count"))
        or decimal_to_int(to_decimal(order.get("remaining_count_fp")))
        or 0
    )
    fill_count = (
        safe_int(order.get("fill_count"))
        or decimal_to_int(to_decimal(order.get("fill_count_fp")))
        or 0
    )
    total_count = (
        safe_int(order.get("count"))
        or decimal_to_int(to_decimal(order.get("count_fp")))
        or 0
    )
    return remaining_count > 0 and fill_count < total_count


def extract_available_balance_cents(payload: dict[str, Any]) -> int | None:
    if not isinstance(payload, dict):
        return None
    candidates = [
        payload.get("available_balance"),
        payload.get("available_balance_cents"),
        payload.get("balance"),
        payload.get("cash_balance"),
    ]
    nested_candidates = (
        payload.get("balance_info"),
        payload.get("portfolio_balance"),
        payload.get("balance_data"),
    )
    for nested in nested_candidates:
        if isinstance(nested, dict):
            candidates.extend(
                [
                    nested.get("available_balance"),
                    nested.get("available_balance_cents"),
                    nested.get("balance"),
                    nested.get("cash_balance"),
                ]
            )
    for value in candidates:
        cents = normalize_balance_value_to_cents(value)
        if cents is not None:
            return cents
    return None


def normalize_balance_value_to_cents(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        with contextlib.suppress(Exception):
            return int(round(float(text)))
        return None
    if isinstance(value, Decimal):
        return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return None


def read_live_lock(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with contextlib.suppress(Exception):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            return raw
    return None


def pid_is_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        process_query_limited_information = 0x1000
        still_active = 259
        handle = ctypes.windll.kernel32.OpenProcess(process_query_limited_information, False, pid)
        if not handle:
            return False
        try:
            exit_code = ctypes.c_ulong()
            if ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)) == 0:
                return False
            return int(exit_code.value) == still_active
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    with contextlib.suppress(ProcessLookupError):
        os.kill(pid, 0)
        return True
    with contextlib.suppress(PermissionError):
        return True
    return False


SETTLEMENT_ONLY_GRACE_SECONDS = 30


def market_is_closed_for_recovery(market: dict[str, Any] | None) -> bool:
    if not isinstance(market, dict):
        return False
    status = str(market.get("status") or "").strip().lower()
    if status in {"closed", "settled", "resolved", "finalized", "final", "expired"}:
        return True
    close_dt = parse_iso(str(market.get("close_time") or market.get("expiration_time") or ""))
    if close_dt is None:
        return False
    return utc_now() >= close_dt + timedelta(seconds=SETTLEMENT_ONLY_GRACE_SECONDS)


def safe_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def to_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except Exception:  # noqa: BLE001
        return None


def decimal_to_int(value: Decimal | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:  # noqa: BLE001
        return None


def normalize_price_value_to_cents(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return dollars_to_cents(value)
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        return dollars_to_cents(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if '.' in text:
            with contextlib.suppress(Exception):
                return dollars_to_cents(text)
        with contextlib.suppress(Exception):
            return int(text)
        return None
    return None


def extract_order_fill_price_cents(order: dict[str, Any], *, fill_count: int) -> int | None:
    if fill_count <= 0:
        return None
    direct_candidates = (
        'avg_fill_price_cents',
        'average_fill_price_cents',
        'fill_price_cents',
        'filled_price_cents',
        'avg_fill_price',
        'average_fill_price',
        'fill_price',
        'filled_price',
        'avg_price',
        'average_price',
    )
    for key in direct_candidates:
        cents = normalize_price_value_to_cents(order.get(key))
        if cents is not None and 0 < cents <= 100:
            return cents

    total_cost_candidates = (
        'fill_cost_cents',
        'filled_cost_cents',
        'fill_value_cents',
        'filled_value_cents',
        'buy_filled_cost_cents',
        'cost_cents',
        'spent_cents',
        'fill_cost',
        'filled_cost',
        'fill_value',
        'filled_value',
        'buy_filled_cost',
        'cost',
        'spent',
    )
    for key in total_cost_candidates:
        total_cents = normalize_price_value_to_cents(order.get(key))
        if total_cents is None or total_cents <= 0:
            continue
        avg_cents = int(round(total_cents / fill_count))
        if 0 < avg_cents <= 100:
            return avg_cents
    return None


def extract_order_fee_cents(order: dict[str, Any], *, fill_count: int) -> int | None:
    if fill_count <= 0:
        return None
    direct_candidates = (
        "fee_cents",
        "fees_cents",
        "filled_fee_cents",
        "fill_fee_cents",
        "total_fee_cents",
        "taker_fee_cents",
        "maker_fee_cents",
        "fee",
        "fees",
        "filled_fee",
        "fill_fee",
        "total_fee",
        "taker_fee",
        "maker_fee",
    )
    for key in direct_candidates:
        cents = normalize_price_value_to_cents(order.get(key))
        if cents is not None and cents >= 0:
            return cents
    return None


def format_decimal_compact(value: Decimal | None) -> str:
    if value is None:
        return "NA"
    normalized = value.normalize()
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def parse_contract_quantity(value: Any, *, fixed_point: bool = False) -> Decimal | None:
    qty = to_decimal(value)
    if qty is None:
        return None
    if fixed_point:
        text = str(value).strip() if value is not None else ""
        if "." not in text:
            qty = qty / Decimal("100")
    return qty


def dollars_to_cents(price: str | int | float | Decimal) -> int:
    return int((Decimal(str(price)) * CENTS).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def extract_price_cents(message: dict[str, Any], side_prefix: str) -> int | None:
    dollars_key = f"{side_prefix}_dollars"
    if dollars_key in message and message.get(dollars_key) not in {None, ""}:
        return dollars_to_cents(message[dollars_key])
    if side_prefix in message and message.get(side_prefix) not in {None, ""}:
        return safe_int(message[side_prefix])
    return None


def snapshot_levels_to_book(raw_levels: Any, *, quantity_is_fp: bool = False) -> dict[int, Decimal]:
    book: dict[int, Decimal] = {}
    if not isinstance(raw_levels, list):
        return book
    for item in raw_levels:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue
        price = item[0]
        qty = parse_contract_quantity(item[1], fixed_point=quantity_is_fp)
        if qty is None or qty <= 0:
            continue
        price_cents = dollars_to_cents(price) if isinstance(price, str) and "." in price else safe_int(price)
        if price_cents is None:
            continue
        book[price_cents] = qty
    return book


async def async_main() -> int:
    try:
        config = load_config()
        bot = BTC15MKalshiWebSocketBot(config)
        await bot.run()
        return 0
    except GracefulExit:
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"Fatal error: {exc}", file=sys.stderr)
        return 1


def main() -> int:
    return asyncio.run(async_main())


if __name__ == "__main__":
    raise SystemExit(main())




