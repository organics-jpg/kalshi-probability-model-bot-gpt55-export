from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from score_bot_log import apply_exchange_fill_overrides, normalize_exchange_fill


class ScoreBotLogAccountingTests(unittest.TestCase):
    def test_settled_trade_without_exit_does_not_borrow_exchange_sell_fill(self) -> None:
        root = Path(tempfile.mkdtemp())
        log_dir = root / "logs"
        log_dir.mkdir()
        (log_dir / "exchange_reconciliation.ndjson").write_text(
            json.dumps(
                {
                    "candidate_recent_fills_since_run": [
                        {
                            "action": "buy",
                            "side": "no",
                            "market_ticker": "KXBTC15M-TEST",
                            "created_time": "2026-05-10T15:12:30Z",
                            "fee_cost": "0.030000",
                            "yes_price_dollars": "0.8800",
                            "no_price_dollars": "0.1200",
                            "fill_id": "buy-no",
                        },
                        {
                            "action": "sell",
                            "side": "yes",
                            "market_ticker": "KXBTC15M-TEST",
                            "created_time": "2026-05-10T15:10:55Z",
                            "fee_cost": "0.050000",
                            "yes_price_dollars": "0.7200",
                            "no_price_dollars": "0.2800",
                            "fill_id": "sell-yes",
                        },
                    ]
                }
            )
            + "\n",
            encoding="utf-8",
        )
        rows = [
            {
                "entry_ts": "2026-05-10 11:12:30",
                "market": "KXBTC15M-TEST",
                "side": "no",
                "qty": 3,
                "entry_fill_cents_assumed": 12,
                "entry_fill_cents_actual": "",
                "entry_fill_cents_used": 12,
                "entry_fee_cents": 0,
                "exit_ts": "",
                "exit_fill_cents_assumed": "",
                "exit_fill_cents_actual": "",
                "exit_fill_cents_used": "",
                "exit_fee_cents": 0,
                "entry_notional_dollars": 0.36,
                "exit_notional_dollars": "",
                "outcome": "loss",
                "result": "yes",
                "market_result": "yes",
                "gross_pnl_dollars": -0.36,
                "net_pnl_dollars": -0.36,
                "gross_pnl_percent": -100.0,
                "net_pnl_percent": -100.0,
            }
        ]

        apply_exchange_fill_overrides(rows, log_dir)

        self.assertEqual(rows[0]["exit_fill_cents_actual"], "")
        self.assertEqual(rows[0]["exit_fill_cents_used"], "")
        self.assertAlmostEqual(rows[0]["gross_pnl_dollars"], -0.36)
        self.assertAlmostEqual(rows[0]["net_pnl_dollars"], -0.39)

    def test_exchange_overrides_aggregate_split_fills_and_sell_opposite_side(self) -> None:
        root = Path(tempfile.mkdtemp())
        log_dir = root / "logs"
        log_dir.mkdir()
        fills = [
            {
                "action": "buy",
                "side": "yes",
                "count_fp": "2.00",
                "market_ticker": "KXBTC15M-TEST",
                "created_time": "2026-05-10T17:22:15.100000Z",
                "fee_cost": "0.030000",
                "yes_price_dollars": "0.7500",
                "no_price_dollars": "0.2500",
                "fill_id": "buy-yes-2",
            },
            {
                "action": "buy",
                "side": "yes",
                "count_fp": "1.00",
                "market_ticker": "KXBTC15M-TEST",
                "created_time": "2026-05-10T17:22:15.200000Z",
                "fee_cost": "0.020000",
                "yes_price_dollars": "0.7500",
                "no_price_dollars": "0.2500",
                "fill_id": "buy-yes-1",
            },
            {
                "action": "sell",
                "side": "no",
                "count_fp": "3.00",
                "market_ticker": "KXBTC15M-TEST",
                "created_time": "2026-05-10T17:24:07.700000Z",
                "fee_cost": "0.026000",
                "yes_price_dollars": "0.9020",
                "no_price_dollars": "0.0980",
                "fill_id": "sell-yes-opposite",
            },
        ]
        (log_dir / "exchange_reconciliation.ndjson").write_text(
            json.dumps({"candidate_recent_fills_since_run": fills}) + "\n",
            encoding="utf-8",
        )
        rows = [
            {
                "entry_ts": "2026-05-10 13:22:15",
                "market": "KXBTC15M-TEST",
                "side": "yes",
                "qty": 3,
                "entry_fill_cents_assumed": 75,
                "entry_fill_cents_actual": "",
                "entry_fill_cents_used": 75,
                "entry_fee_cents": 0,
                "exit_ts": "2026-05-10 13:24:07",
                "exit_fill_cents_assumed": 90,
                "exit_fill_cents_actual": "",
                "exit_fill_cents_used": 90,
                "exit_fee_cents": 0,
                "entry_notional_dollars": 2.25,
                "exit_notional_dollars": 2.70,
                "outcome": "exited_before_settlement",
                "result": "",
                "market_result": "",
                "gross_pnl_dollars": 0.45,
                "net_pnl_dollars": 0.45,
                "gross_pnl_percent": 20.0,
                "net_pnl_percent": 20.0,
            }
        ]

        apply_exchange_fill_overrides(rows, log_dir)

        self.assertEqual(rows[0]["entry_exchange_qty"], 3.0)
        self.assertEqual(rows[0]["exit_exchange_qty"], 3.0)
        self.assertAlmostEqual(rows[0]["entry_notional_dollars"], 2.25)
        self.assertAlmostEqual(rows[0]["exit_notional_dollars"], 2.706)
        self.assertAlmostEqual(rows[0]["entry_fee_cents"], 5.0)
        self.assertAlmostEqual(rows[0]["exit_fee_cents"], 2.6)
        self.assertAlmostEqual(rows[0]["gross_pnl_dollars"], 0.456)
        self.assertAlmostEqual(rows[0]["net_pnl_dollars"], 0.38)

    def test_kalshi_api_fill_preferred_over_reconciliation_log(self) -> None:
        root = Path(tempfile.mkdtemp())
        log_dir = root / "logs"
        log_dir.mkdir()
        (log_dir / "exchange_reconciliation.ndjson").write_text(
            json.dumps(
                {
                    "candidate_recent_fills_since_run": [
                        {
                            "action": "buy",
                            "side": "yes",
                            "count_fp": "1.00",
                            "market_ticker": "KXBTC15M-API",
                            "created_time": "2026-05-10T15:00:00Z",
                            "fee_cost": "0.010000",
                            "yes_price_dollars": "0.1000",
                            "no_price_dollars": "0.9000",
                            "fill_id": "log-buy",
                        }
                    ]
                }
            )
            + "\n",
            encoding="utf-8",
        )
        api_fill = normalize_exchange_fill(
            {
                "action": "buy",
                "side": "yes",
                "count_fp": "1.00",
                "market_ticker": "KXBTC15M-API",
                "created_time": "2026-05-10T15:00:00Z",
                "fee_cost": "0.020000",
                "yes_price_dollars": "0.1500",
                "no_price_dollars": "0.8500",
                "fill_id": "api-buy",
            },
            source="kalshi_api",
            endpoint="/portfolio/fills",
        )
        rows = [
            {
                "entry_ts": "2026-05-10 11:00:00",
                "market": "KXBTC15M-API",
                "side": "yes",
                "qty": 1,
                "entry_fill_cents_assumed": 10,
                "entry_fill_cents_actual": "",
                "entry_fill_cents_used": 10,
                "entry_fee_cents": 0,
                "exit_ts": "",
                "exit_fill_cents_assumed": "",
                "exit_fill_cents_actual": "",
                "exit_fill_cents_used": "",
                "exit_fee_cents": 0,
                "entry_notional_dollars": 0.10,
                "exit_notional_dollars": "",
                "outcome": "win",
                "result": "yes",
                "market_result": "yes",
                "gross_pnl_dollars": 0.90,
                "net_pnl_dollars": 0.90,
                "gross_pnl_percent": 900.0,
                "net_pnl_percent": 900.0,
            }
        ]

        summary = apply_exchange_fill_overrides(rows, log_dir, [api_fill] if api_fill else [])

        self.assertEqual(rows[0]["entry_api_fill_ids"], "api-buy")
        self.assertEqual(rows[0]["entry_accounting_source"], "kalshi_api")
        self.assertEqual(rows[0]["accounting_source"], "kalshi_api_fills+market_result")
        self.assertAlmostEqual(rows[0]["entry_fill_cents_used"], 15.0)
        self.assertAlmostEqual(rows[0]["gross_pnl_dollars"], 0.85)
        self.assertAlmostEqual(rows[0]["net_pnl_dollars"], 0.83)
        self.assertEqual(summary["entry_rows_matched_api"], 1)

    def test_entry_fill_timestamp_list_matches_later_addon_api_fill(self) -> None:
        root = Path(tempfile.mkdtemp())
        log_dir = root / "logs"
        log_dir.mkdir()
        fills = [
            normalize_exchange_fill(
                {
                    "action": "buy",
                    "side": "yes",
                    "count_fp": "1.00",
                    "market_ticker": "KXBTC15M-ADDON",
                    "created_time": "2026-05-10T15:00:00Z",
                    "fee_cost": "0.010000",
                    "yes_price_dollars": "0.4000",
                    "no_price_dollars": "0.6000",
                    "fill_id": "api-buy-first",
                },
                source="kalshi_api",
                endpoint="/portfolio/fills",
            ),
            normalize_exchange_fill(
                {
                    "action": "buy",
                    "side": "yes",
                    "count_fp": "1.00",
                    "market_ticker": "KXBTC15M-ADDON",
                    "created_time": "2026-05-10T15:05:00Z",
                    "fee_cost": "0.010000",
                    "yes_price_dollars": "0.6000",
                    "no_price_dollars": "0.4000",
                    "fill_id": "api-buy-addon",
                },
                source="kalshi_api",
                endpoint="/portfolio/fills",
            ),
        ]
        rows = [
            {
                "entry_ts": "2026-05-10 11:00:00",
                "entry_fill_event_ts_list": "2026-05-10 11:00:00|2026-05-10 11:05:00",
                "market": "KXBTC15M-ADDON",
                "side": "yes",
                "qty": 2,
                "entry_fill_cents_assumed": 50,
                "entry_fill_cents_actual": "",
                "entry_fill_cents_used": 50,
                "entry_fee_cents": 0,
                "exit_ts": "",
                "exit_fill_cents_assumed": "",
                "exit_fill_cents_actual": "",
                "exit_fill_cents_used": "",
                "exit_fee_cents": 0,
                "entry_notional_dollars": 1.0,
                "exit_notional_dollars": "",
                "outcome": "win",
                "result": "yes",
                "market_result": "yes",
                "gross_pnl_dollars": 1.0,
                "net_pnl_dollars": 1.0,
                "gross_pnl_percent": 100.0,
                "net_pnl_percent": 100.0,
            }
        ]

        apply_exchange_fill_overrides(rows, log_dir, [fill for fill in fills if fill])

        self.assertEqual(rows[0]["entry_exchange_qty"], 2.0)
        self.assertEqual(set(rows[0]["entry_api_fill_ids"].split("|")), {"api-buy-first", "api-buy-addon"})
        self.assertAlmostEqual(rows[0]["entry_fill_cents_used"], 50.0)
        self.assertAlmostEqual(rows[0]["entry_notional_dollars"], 1.0)
        self.assertAlmostEqual(rows[0]["net_pnl_dollars"], 0.98)


if __name__ == "__main__":
    unittest.main()
