"""BTC Mushroom Forecaster v0.32 research candidate.

v32 is a probability-surface experiment, not a live-bot patch.

The v31 two-clock model fixed the most obvious settlement prior: use an
effective settlement/proxy horizon before the final minute, then switch to the
exact Brownian average-collapse law inside the final 60 seconds.

The next sweep showed the effective pre-terminal proxy horizon is probably a
little longer than v31's 90 seconds on the current live-heartbeat replay. v32
therefore keeps the exact final-60s collapse but moves the effective
settlement/proxy horizon to 110 seconds. This is deliberately a small physics
change: no new trade filters, no book scoring, and no live execution logic.
"""
from __future__ import annotations

from dataclasses import dataclass

from btc_mushroom_forecaster_v31_fast import FastMushroomFVEngineV31, FastMushroomV31Config


@dataclass
class FastMushroomV32Config(FastMushroomV31Config):
    settlement_average_seconds: float = 110.0
    exact_average_inside_seconds: float = 60.0


class FastMushroomFVEngineV32(FastMushroomFVEngineV31):
    """v0.32 FV engine with a longer proxy-aware settlement horizon."""

    def __init__(self, config: FastMushroomV32Config | None = None) -> None:
        super().__init__(config or FastMushroomV32Config())


FastMushroomConfig = FastMushroomV32Config
FastMushroomFVEngine = FastMushroomFVEngineV32
