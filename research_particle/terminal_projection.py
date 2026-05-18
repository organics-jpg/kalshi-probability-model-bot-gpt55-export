from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


SQRT_TWO = math.sqrt(2.0)


@dataclass(frozen=True)
class WeightedTerminalSample:
    terminal_spot: float
    weight: float = 1.0


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / SQRT_TWO))


def brownian_terminal_probability(
    spot: float,
    strike: float,
    seconds_to_close: float,
    annualized_vol: float,
    drift_per_second: float = 0.0,
    seconds_per_year: float = 365.0 * 24.0 * 60.0 * 60.0,
) -> float:
    """Return P(S_T > strike) for log-price Brownian terminal settlement.

    This is terminal probability only. It is not a first-touch/crossing
    probability.
    """
    if spot <= 0:
        raise ValueError("spot must be positive")
    if strike <= 0:
        raise ValueError("strike must be positive")
    if seconds_to_close <= 0:
        return 1.0 if spot > strike else 0.0
    if annualized_vol < 0:
        raise ValueError("annualized_vol must be non-negative")

    log_moneyness = math.log(spot / strike)
    sigma_per_sqrt_second = annualized_vol / math.sqrt(seconds_per_year)
    stdev = sigma_per_sqrt_second * math.sqrt(seconds_to_close)
    mean = log_moneyness + drift_per_second * seconds_to_close
    if stdev == 0:
        return 1.0 if mean > 0 else 0.0
    return normal_cdf(mean / stdev)


def simulate_terminal_samples(
    spot: float,
    seconds_to_close: int,
    annualized_vol: float,
    sample_count: int,
    seed: int = 0,
    drift_per_second: float = 0.0,
    jump_intensity_per_second: float = 0.0,
    jump_mean_log_return: float = 0.0,
    jump_std_log_return: float = 0.0,
    seconds_per_year: float = 365.0 * 24.0 * 60.0 * 60.0,
) -> list[WeightedTerminalSample]:
    if sample_count <= 0:
        raise ValueError("sample_count must be positive")
    if seconds_to_close < 0:
        raise ValueError("seconds_to_close must be non-negative")
    if spot <= 0:
        raise ValueError("spot must be positive")
    if annualized_vol < 0:
        raise ValueError("annualized_vol must be non-negative")
    if jump_intensity_per_second < 0:
        raise ValueError("jump_intensity_per_second must be non-negative")

    rng = random.Random(seed)
    sigma_per_sqrt_second = annualized_vol / math.sqrt(seconds_per_year)
    samples: list[WeightedTerminalSample] = []
    for _ in range(sample_count):
        log_price = math.log(spot)
        for _second in range(seconds_to_close):
            log_price += drift_per_second
            if sigma_per_sqrt_second:
                log_price += rng.gauss(0.0, sigma_per_sqrt_second)
            if jump_intensity_per_second and rng.random() < jump_intensity_per_second:
                log_price += rng.gauss(jump_mean_log_return, jump_std_log_return)
        samples.append(WeightedTerminalSample(terminal_spot=math.exp(log_price), weight=1.0))
    return samples


def weighted_probability_yes(samples: Iterable[WeightedTerminalSample], strike: float) -> float:
    total_weight = 0.0
    yes_weight = 0.0
    for sample in samples:
        if sample.weight < 0:
            raise ValueError("sample weights must be non-negative")
        total_weight += sample.weight
        if sample.terminal_spot > strike:
            yes_weight += sample.weight
    if total_weight <= 0:
        raise ValueError("total sample weight must be positive")
    return yes_weight / total_weight


def effective_sample_size(weights: Sequence[float]) -> float:
    total = sum(weights)
    if total <= 0:
        raise ValueError("total weight must be positive")
    normalized = [w / total for w in weights]
    return 1.0 / sum(w * w for w in normalized)


def systematic_resample(
    samples: Sequence[WeightedTerminalSample],
    seed: int = 0,
) -> list[WeightedTerminalSample]:
    if not samples:
        raise ValueError("samples must not be empty")
    weights = [sample.weight for sample in samples]
    total = sum(weights)
    if total <= 0:
        raise ValueError("total weight must be positive")

    rng = random.Random(seed)
    n = len(samples)
    step = total / n
    start = rng.random() * step
    targets = [start + i * step for i in range(n)]

    resampled: list[WeightedTerminalSample] = []
    cumulative = 0.0
    idx = 0
    for target in targets:
        while idx < n - 1 and cumulative + samples[idx].weight < target:
            cumulative += samples[idx].weight
            idx += 1
        resampled.append(WeightedTerminalSample(samples[idx].terminal_spot, 1.0))
    return resampled


def terminal_label_yes(settlement_price: float, strike: float) -> bool:
    return settlement_price > strike


def shared_terminal_probabilities(
    samples: Sequence[WeightedTerminalSample],
    strikes: Sequence[float],
) -> Mapping[float, float]:
    return {strike: weighted_probability_yes(samples, strike) for strike in strikes}

