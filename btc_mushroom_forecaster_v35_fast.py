"""BTC Mushroom Forecaster v0.35 research candidate.

v35 is a probability-surface experiment, not a live-bot patch.

v34 established a useful short-memory anti-persistence prior, but the next
physics sweep showed the current 110-second settlement/proxy horizon was still
slightly under-accounting for the live replay's boundary smoothing. Simply
sharpening that horizon improved Brier while hurting logloss, so v35 pairs the
longer 150-second proxy horizon with a softer posterior temperature.

Interpretation:
- settlement/proxy horizon: 150s effective smoothing before the exact final
  60-second average-collapse law;
- path prior: same materiality-gated 3-minute anti-persistence as v34;
- posterior temperature: 1.02 to avoid turning the longer horizon into brittle
  overconfidence.
"""
from __future__ import annotations

from dataclasses import dataclass

from btc_mushroom_forecaster_v34_fast import FastMushroomFVEngineV34, FastMushroomV34Config


@dataclass
class FastMushroomV35Config(FastMushroomV34Config):
    settlement_average_seconds: float = 150.0
    exact_average_inside_seconds: float = 60.0
    anti_persistence_lag_minutes: int = 3
    anti_persistence_velocity_weight: float = -0.50
    anti_persistence_time_damp_power: float = 2.0
    anti_persistence_sigma_mult: float = 1.00
    anti_persistence_max_logit_weight: float = 0.10
    anti_persistence_shift_gate_center_dollars: float = 40.0
    anti_persistence_shift_gate_width_dollars: float = 5.0
    posterior_temperature: float = 1.02


class FastMushroomFVEngineV35(FastMushroomFVEngineV34):
    """v0.35 FV engine with longer proxy horizon and softer posterior."""

    def __init__(self, config: FastMushroomV35Config | None = None) -> None:
        super().__init__(config or FastMushroomV35Config())


FastMushroomConfig = FastMushroomV35Config
FastMushroomFVEngine = FastMushroomFVEngineV35
