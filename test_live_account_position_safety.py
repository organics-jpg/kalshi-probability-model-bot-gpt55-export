from __future__ import annotations

import unittest

from kalshi_btc15m_bot_ws import (
    PositionState,
    live_account_position_conflict_reason,
    nonzero_live_positions,
    parse_order_count_decimal,
    quantity_to_number,
    summarize_exchange_fills_for_order,
)


class LiveAccountPositionSafetyTests(unittest.TestCase):
    def test_filters_zero_positions(self) -> None:
        positions = [
            {"ticker": "KXBTC15M-ZERO", "position_fp": "0.00"},
            {"ticker": "KXBTC15M-LIVE", "position_fp": "-3.00"},
        ]

        self.assertEqual(
            [pos["ticker"] for pos in nonzero_live_positions(positions)],
            ["KXBTC15M-LIVE"],
        )

    def test_blocks_exchange_position_without_local_state(self) -> None:
        reason = live_account_position_conflict_reason(
            [{"ticker": "KXBTC15M-LIVE", "position_fp": "-3.00"}],
            None,
        )

        self.assertEqual(reason, "exchange_position_without_local_state")

    def test_allows_matching_local_position(self) -> None:
        local_position = PositionState(
            market_ticker="KXBTC15M-LIVE",
            side="no",
            count=3,
            filled_at="2026-05-10T17:34:42Z",
            entry_order_id="entry-order",
            entry_limit_price_cents=75,
        )

        reason = live_account_position_conflict_reason(
            [{"ticker": "kxbtc15m-live", "position_fp": "-3.00"}],
            local_position,
        )

        self.assertIsNone(reason)

    def test_blocks_other_market_position(self) -> None:
        local_position = PositionState(
            market_ticker="KXBTC15M-LOCAL",
            side="yes",
            count=2,
            filled_at="2026-05-10T17:34:42Z",
            entry_order_id="entry-order",
            entry_limit_price_cents=80,
        )

        reason = live_account_position_conflict_reason(
            [{"ticker": "KXBTC15M-OTHER", "position_fp": "1.00"}],
            local_position,
        )

        self.assertEqual(reason, "exchange_position_other_market")

    def test_preserves_fractional_fill_count_from_order_fp(self) -> None:
        order = {"fill_count": 0, "fill_count_fp": "0.85", "remaining_count": 0}

        fill_count = quantity_to_number(parse_order_count_decimal(order, purpose="fill"))

        self.assertEqual(fill_count, 0.85)

    def test_recovers_fractional_fill_and_fee_from_exchange_fills(self) -> None:
        summary = summarize_exchange_fills_for_order(
            [
                {
                    "order_id": "order-1",
                    "fill_id": "fill-1",
                    "count_fp": "0.85",
                    "fee_cost": "0.013500",
                    "yes_price_dollars": "0.0900",
                }
            ],
            order_id="order-1",
            client_order_id="client-1",
            side="yes",
        )

        self.assertIsNotNone(summary)
        assert summary is not None
        self.assertEqual(summary["fill_count"], 0.85)
        self.assertEqual(summary["actual_fill_price_cents"], 9)
        self.assertEqual(summary["actual_fee_cents"], 1.35)


if __name__ == "__main__":
    unittest.main()
