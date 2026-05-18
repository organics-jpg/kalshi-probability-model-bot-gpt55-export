
"""
BTC Mushroom Live FV Worker v28

A thin live-integration layer around btc_mushroom_forecaster_v28_fast.py.

This file intentionally avoids network/auth code. The existing bot already has
Kalshi/BTC websocket loops. Codex can plug those loops into this worker by calling:

    worker.update_btc_tick(price, ts)
    worker.upsert_market(...)
    opportunities = worker.compute_all(now)

The worker groups markets by horizon and computes FV/edge in vectorized batches.
It never sends orders.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, Literal
import math
import time

import numpy as np

try:
    from btc_mushroom_forecaster_v28_fast import FastMushroomFVEngine, FastMushroomConfig
except Exception:  # pragma: no cover
    # Allows direct import when files are vendored differently.
    FastMushroomFVEngine = None
    FastMushroomConfig = None

Side = Literal["yes", "no"]


@dataclass
class MarketSnapshot:
    ticker: str
    strike: float
    close_ts: float
    yes_bid_cents: float | None = None
    no_bid_cents: float | None = None
    yes_depth: float = 0.0
    no_depth: float = 0.0
    book_ts: float = 0.0
    series: str = "KXBTC"
    metadata: dict = field(default_factory=dict)

    @property
    def yes_ask_cents(self) -> float:
        if self.no_bid_cents is None:
            return float("nan")
        return 100.0 - float(self.no_bid_cents)

    @property
    def no_ask_cents(self) -> float:
        if self.yes_bid_cents is None:
            return float("nan")
        return 100.0 - float(self.yes_bid_cents)

    def seconds_to_close(self, now_ts: float | None = None) -> float:
        now_ts = float(time.time() if now_ts is None else now_ts)
        return max(0.0, float(self.close_ts) - now_ts)

    def book_age_ms(self, now_ts: float | None = None) -> float:
        now_ts = float(time.time() if now_ts is None else now_ts)
        if not self.book_ts:
            return float("inf")
        return max(0.0, 1000.0 * (now_ts - float(self.book_ts)))


@dataclass
class Opportunity:
    ticker: str
    strike: float
    seconds_to_close: float
    p_yes: float
    fair_yes_cents: float
    fair_no_cents: float
    yes_ask_cents: float
    no_ask_cents: float
    yes_edge_cents: float
    no_edge_cents: float
    best_side: str
    best_edge_cents: float
    side_probability: float
    sigma_t_dollars: float
    d_sigma: float
    book_age_ms: float
    tradeable: bool
    metadata: dict = field(default_factory=dict)


class LiveFVWorker:
    """Vectorized live fair-value worker for many Kalshi BTC markets."""

    def __init__(
        self,
        engine: FastMushroomFVEngine | None = None,
        config: FastMushroomConfig | None = None,
        *,
        max_book_age_ms: float = 1500.0,
        min_edge_15m_cents: float = 2.0,
        min_edge_60m_cents: float = 3.0,
    ) -> None:
        if engine is None:
            if FastMushroomFVEngine is None:
                raise RuntimeError("FastMushroomFVEngine import failed")
            engine = FastMushroomFVEngine(config or FastMushroomConfig())
        self.engine = engine
        self.markets: dict[str, MarketSnapshot] = {}
        self.max_book_age_ms = float(max_book_age_ms)
        self.min_edge_15m_cents = float(min_edge_15m_cents)
        self.min_edge_60m_cents = float(min_edge_60m_cents)

    @staticmethod
    def _to_ts(ts: datetime | float | int | None) -> float:
        if ts is None:
            return time.time()
        if isinstance(ts, datetime):
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            return float(ts.timestamp())
        return float(ts)

    def update_btc_tick(self, price: float, ts: datetime | float | int | None = None, volume: float = 0.0) -> bool:
        return self.engine.update_tick(price=float(price), ts=ts, volume=volume)

    def update_btc_bar(
        self,
        *,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: float = 0.0,
        ts: datetime | float | int | None = None,
    ) -> bool:
        return self.engine.update_bar(open=open, high=high, low=low, close=close, volume=volume, ts=ts)

    def upsert_market(
        self,
        *,
        ticker: str,
        strike: float,
        close_ts: datetime | float | int,
        yes_bid_cents: float | None = None,
        no_bid_cents: float | None = None,
        yes_depth: float = 0.0,
        no_depth: float = 0.0,
        book_ts: datetime | float | int | None = None,
        series: str = "KXBTC",
        metadata: dict | None = None,
    ) -> None:
        self.markets[str(ticker)] = MarketSnapshot(
            ticker=str(ticker),
            strike=float(strike),
            close_ts=self._to_ts(close_ts),
            yes_bid_cents=None if yes_bid_cents is None else float(yes_bid_cents),
            no_bid_cents=None if no_bid_cents is None else float(no_bid_cents),
            yes_depth=float(yes_depth or 0.0),
            no_depth=float(no_depth or 0.0),
            book_ts=self._to_ts(book_ts),
            series=str(series),
            metadata=dict(metadata or {}),
        )

    def remove_market(self, ticker: str) -> None:
        self.markets.pop(str(ticker), None)

    @staticmethod
    def _horizon_bucket(seconds_to_close: float) -> int:
        mins = max(1, int(round(float(seconds_to_close) / 60.0)))
        # Snap to supported research horizons.
        return min((5, 10, 15, 30, 60), key=lambda h: abs(h - mins))

    def _min_edge_for_horizon(self, h: int) -> float:
        return self.min_edge_60m_cents if h >= 45 else self.min_edge_15m_cents

    def compute_all(
        self,
        *,
        now_ts: datetime | float | int | None = None,
        fee_cents: float | None = None,
        slippage_cents: float | None = None,
        model_buffer_cents: float | None = None,
        require_fresh_book: bool = True,
    ) -> list[Opportunity]:
        if not self.engine.ready():
            return []
        now = self._to_ts(now_ts)
        valid: list[MarketSnapshot] = []
        for m in self.markets.values():
            if m.seconds_to_close(now) <= 0:
                continue
            if not (math.isfinite(m.yes_ask_cents) and math.isfinite(m.no_ask_cents)):
                continue
            if require_fresh_book and m.book_age_ms(now) > self.max_book_age_ms:
                continue
            valid.append(m)
        if not valid:
            return []

        groups: dict[int, list[MarketSnapshot]] = {}
        for m in valid:
            groups.setdefault(self._horizon_bucket(m.seconds_to_close(now)), []).append(m)

        out: list[Opportunity] = []
        for h, items in groups.items():
            strikes = np.array([m.strike for m in items], dtype=float)
            yes_asks = np.array([m.yes_ask_cents for m in items], dtype=float)
            no_asks = np.array([m.no_ask_cents for m in items], dtype=float)
            min_edge = self._min_edge_for_horizon(h)
            edge = self.engine.edge_many(
                strikes=strikes,
                horizon_seconds=float(h * 60),
                yes_ask_cents=yes_asks,
                no_ask_cents=no_asks,
                fee_cents=fee_cents,
                slippage_cents=slippage_cents,
                model_buffer_cents=model_buffer_cents,
                min_net_edge_cents=min_edge,
            )
            for i, m in enumerate(items):
                out.append(Opportunity(
                    ticker=m.ticker,
                    strike=float(m.strike),
                    seconds_to_close=m.seconds_to_close(now),
                    p_yes=float(edge.p_yes[i]),
                    fair_yes_cents=float(edge.fair_yes_cents[i]),
                    fair_no_cents=float(edge.fair_no_cents[i]),
                    yes_ask_cents=float(yes_asks[i]),
                    no_ask_cents=float(no_asks[i]),
                    yes_edge_cents=float(edge.yes_net_edge_cents[i]),
                    no_edge_cents=float(edge.no_net_edge_cents[i]),
                    best_side=str(edge.best_side[i]),
                    best_edge_cents=float(edge.best_edge_cents[i]),
                    side_probability=float(edge.side_probability[i]),
                    sigma_t_dollars=float(edge.components.get("sigma_t_dollars", np.nan)) if isinstance(edge.components.get("sigma_t_dollars", None), float) else float("nan"),
                    d_sigma=float(edge.components.get("d_sigma", np.array([np.nan]))[i]) if "d_sigma" in edge.components else float("nan"),
                    book_age_ms=float(m.book_age_ms(now)),
                    tradeable=bool(edge.tradeable[i]),
                    metadata=dict(m.metadata),
                ))
        out.sort(key=lambda x: x.best_edge_cents, reverse=True)
        return out
