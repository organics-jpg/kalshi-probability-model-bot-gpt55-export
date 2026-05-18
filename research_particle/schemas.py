from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


Side = Literal["yes", "no"]


@dataclass(frozen=True)
class CandidateSnapshot:
    market_ticker: str
    decision_ts_utc: datetime
    recv_ts_utc: datetime
    strike: float
    spot: float
    yes_ask_cents: float
    no_ask_cents: float
    fee_cents: float
    fill_prob: float
    yes_fill_prob: float | None = None
    no_fill_prob: float | None = None


@dataclass(frozen=True)
class SettlementLabel:
    market_ticker: str
    settlement_ts_utc: datetime
    label_available_ts_utc: datetime
    settlement_price: float
    strike: float

    @property
    def result_yes(self) -> bool:
        # Kalshi BTC 15m settlement is terminal > strike, not path touch.
        return self.settlement_price > self.strike


@dataclass(frozen=True)
class TimedRecord:
    name: str
    event_ts_utc: datetime
    recv_ts_utc: datetime
    value: float
