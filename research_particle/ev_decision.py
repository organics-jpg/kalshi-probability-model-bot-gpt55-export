from __future__ import annotations

from dataclasses import dataclass


def expected_pnl_cents(
    p_win: float,
    ask_cents: float,
    fee_if_win_cents: float = 0.0,
    fee_if_loss_cents: float = 0.0,
    fill_prob: float = 1.0,
    no_fill_penalty_cents: float = 0.0,
) -> float:
    if not 0.0 <= p_win <= 1.0:
        raise ValueError("p_win must be in [0, 1]")
    if not 0.0 <= fill_prob <= 1.0:
        raise ValueError("fill_prob must be in [0, 1]")
    win_profit = 100.0 - ask_cents - fee_if_win_cents
    loss_cost = ask_cents + fee_if_loss_cents
    filled_ev = p_win * win_profit - (1.0 - p_win) * loss_cost
    return fill_prob * filled_ev - (1.0 - fill_prob) * no_fill_penalty_cents


def break_even_probability(
    ask_cents: float,
    fee_if_win_cents: float = 0.0,
    fee_if_loss_cents: float = 0.0,
) -> float:
    win_profit = 100.0 - ask_cents - fee_if_win_cents
    loss_cost = ask_cents + fee_if_loss_cents
    denom = win_profit + loss_cost
    if denom <= 0:
        raise ValueError("invalid payoff denominator")
    return loss_cost / denom


@dataclass
class FillStats:
    attempts: int = 0
    fills: int = 0
    no_fills: int = 0

    def update(self, filled: bool) -> None:
        self.attempts += 1
        if filled:
            self.fills += 1
        else:
            self.no_fills += 1

    @property
    def fill_rate(self) -> float:
        if self.attempts == 0:
            return 0.0
        return self.fills / self.attempts


def realized_trade_pnl_cents(
    filled: bool,
    won: bool,
    ask_cents: float,
    fee_if_win_cents: float = 0.0,
    fee_if_loss_cents: float = 0.0,
) -> float:
    if not filled:
        return 0.0
    if won:
        return 100.0 - ask_cents - fee_if_win_cents
    return -ask_cents - fee_if_loss_cents

