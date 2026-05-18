from __future__ import annotations

import unittest

from probe_v28_common_clock_live_trial_status import exchange_accounting_summary


class ProbeExchangeAccountingTests(unittest.TestCase):
    def test_closed_round_trip_uses_fill_notional_when_position_pnl_absent(self) -> None:
        summary = exchange_accounting_summary(
            exchange={"available": True, "balance": {"balance": 950, "portfolio_value": 0}, "positions": []},
            candidate_fills=[
                {
                    "action": "buy",
                    "side": "yes",
                    "count_fp": "2.00",
                    "market_ticker": "KXBTC15M-TEST",
                    "fee_cost": "0.020000",
                    "yes_price_dollars": "0.1400",
                    "no_price_dollars": "0.8600",
                },
                {
                    "action": "sell",
                    "side": "no",
                    "count_fp": "2.00",
                    "market_ticker": "KXBTC15M-TEST",
                    "fee_cost": "0.020000",
                    "yes_price_dollars": "0.1600",
                    "no_price_dollars": "0.8400",
                },
            ],
        )

        row = summary["by_market"]["KXBTC15M-TEST"]
        self.assertAlmostEqual(row["buy_notional_dollars"], 0.28)
        self.assertAlmostEqual(row["sell_notional_dollars"], 0.32)
        self.assertAlmostEqual(row["exchange_gross_realized_pnl_dollars"], 0.04)
        self.assertEqual(row["exchange_gross_realized_source"], "fills_matched_notional")
        self.assertAlmostEqual(row["exchange_fees_paid_dollars"], 0.04)
        self.assertAlmostEqual(row["exchange_net_realized_pnl_after_fees_dollars"], 0.0)
        self.assertAlmostEqual(summary["totals"]["exchange_net_realized_pnl_after_fees_dollars"], 0.0)


if __name__ == "__main__":
    unittest.main()
