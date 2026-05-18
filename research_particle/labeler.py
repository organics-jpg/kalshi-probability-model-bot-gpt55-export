from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .ev_decision import realized_trade_pnl_cents
from .schemas import CandidateSnapshot, SettlementLabel, Side


class LabelUnavailableError(ValueError):
    pass


class LabelMismatchError(ValueError):
    pass


@dataclass(frozen=True)
class LabeledCandidate:
    snapshot: CandidateSnapshot
    label: SettlementLabel
    side: Side
    filled: bool
    won: bool
    counterfactual_pnl_cents: float


def label_candidate(
    snapshot: CandidateSnapshot,
    label: SettlementLabel,
    *,
    side: Side,
    filled: bool,
    as_of_ts_utc: datetime,
) -> LabeledCandidate:
    if snapshot.market_ticker != label.market_ticker:
        raise LabelMismatchError("snapshot and settlement label market_ticker differ")
    if as_of_ts_utc < label.label_available_ts_utc:
        raise LabelUnavailableError("settlement label is not available at as_of_ts_utc")

    yes_won = label.result_yes
    won = yes_won if side == "yes" else not yes_won
    ask_cents = snapshot.yes_ask_cents if side == "yes" else snapshot.no_ask_cents
    pnl = realized_trade_pnl_cents(
        filled=filled,
        won=won,
        ask_cents=ask_cents,
        fee_if_win_cents=snapshot.fee_cents,
        fee_if_loss_cents=0.0,
    )
    return LabeledCandidate(
        snapshot=snapshot,
        label=label,
        side=side,
        filled=filled,
        won=won,
        counterfactual_pnl_cents=pnl,
    )

