from __future__ import annotations

import math
from statistics import mean
from typing import Iterable, Sequence


def brier_score(probabilities: Sequence[float], labels: Sequence[int]) -> float:
    if len(probabilities) != len(labels):
        raise ValueError("probabilities and labels must have same length")
    if not probabilities:
        raise ValueError("at least one probability is required")
    return mean((p - y) ** 2 for p, y in zip(probabilities, labels))


def log_loss(probabilities: Sequence[float], labels: Sequence[int], eps: float = 1e-12) -> float:
    if len(probabilities) != len(labels):
        raise ValueError("probabilities and labels must have same length")
    if not probabilities:
        raise ValueError("at least one probability is required")
    total = 0.0
    for p, y in zip(probabilities, labels):
        p = min(1.0 - eps, max(eps, p))
        total += -(y * math.log(p) + (1 - y) * math.log(1.0 - p))
    return total / len(probabilities)


def top_bucket_mean_pnl(
    predicted_ev_cents: Sequence[float],
    realized_pnl_cents: Sequence[float],
    top_fraction: float = 0.25,
) -> float:
    if len(predicted_ev_cents) != len(realized_pnl_cents):
        raise ValueError("predicted and realized sequences must have same length")
    if not predicted_ev_cents:
        raise ValueError("at least one row is required")
    if not 0.0 < top_fraction <= 1.0:
        raise ValueError("top_fraction must be in (0, 1]")
    count = max(1, math.ceil(len(predicted_ev_cents) * top_fraction))
    order = sorted(range(len(predicted_ev_cents)), key=lambda i: predicted_ev_cents[i], reverse=True)
    top = order[:count]
    return mean(realized_pnl_cents[i] for i in top)


def pairwise_rank_correlation_sign(
    predicted_ev_cents: Sequence[float],
    realized_pnl_cents: Sequence[float],
) -> float:
    """Return a simple Kendall-like pairwise agreement score in [-1, 1]."""
    if len(predicted_ev_cents) != len(realized_pnl_cents):
        raise ValueError("predicted and realized sequences must have same length")
    concordant = 0
    discordant = 0
    for i in range(len(predicted_ev_cents)):
        for j in range(i + 1, len(predicted_ev_cents)):
            pred_delta = predicted_ev_cents[i] - predicted_ev_cents[j]
            pnl_delta = realized_pnl_cents[i] - realized_pnl_cents[j]
            product = pred_delta * pnl_delta
            if product > 0:
                concordant += 1
            elif product < 0:
                discordant += 1
    total = concordant + discordant
    if total == 0:
        return 0.0
    return (concordant - discordant) / total

