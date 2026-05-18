# OU Mispricing Optimal-Stopping Backtest

Brand-new research lane: Brownian fair value from BTC spot/strike plus Carr-inspired OU simulation on Kalshi probability mispricing.

Audit note: this is not a paper-exact Carr/Lopez de Prado implementation. The paper optimizes exit corridors for an already-open position; this harness adds a new fair-value entry rule, Kalshi fees/spreads, and historical-tape PnL scoring.

- Generated UTC: `2026-05-14T17:44:19Z`
- Event files: `1`
- Market-results source: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api\market_results.csv`
- Snapshots after filters: `13712`
- Markets: `213`
- Trades: `139`
- Net PnL: `12.15` dollars
- Realized/settled PnL excluding open mark-to-last rows: `12.15` dollars on `139` trades
- Open mark-to-last PnL: `0.0` dollars on `0` trades
- Win rate: `0.5324`
- Sim decisions scored: `143`

## Exit Reasons

- `max_hold`: 51
- `settlement_after_tape`: 60
- `take_profit`: 28

## Rejection Counts

- `edge_or_z`: 4242
- `one_entry_per_market`: 4548
- `sim_gate`: 4
- `spread`: 317
- `time_window`: 4343
- `warming`: 119

## First Trades

| Entry | Market | Side | Entry | Exit | PnL $ | Reason |
|---|---|---:|---:|---:|---:|---|
| 2026-05-11T00:20:03.864048+00:00 | KXBTC15M-26MAY102030-30 | yes | 5.0 | 14.0 | 0.07 | max_hold |
| 2026-05-11T00:35:18.845507+00:00 | KXBTC15M-26MAY102045-45 | no | 25.0 | 50.0 | 0.21 | take_profit |
| 2026-05-11T00:50:00.120144+00:00 | KXBTC15M-26MAY102100-00 | yes | 37.0 | 36.0 | -0.05 | max_hold |
| 2026-05-11T01:20:01.572988+00:00 | KXBTC15M-26MAY102130-30 | no | 14.0 | 53.0 | 0.36 | take_profit |
| 2026-05-11T02:07:54.705925+00:00 | KXBTC15M-26MAY102215-15 | yes | 18.0 | 48.0 | 0.26 | take_profit |
| 2026-05-11T02:20:05.970997+00:00 | KXBTC15M-26MAY102230-30 | yes | 19.0 | 4.0 | -0.18 | max_hold |
| 2026-05-11T02:35:05.352063+00:00 | KXBTC15M-26MAY102245-45 | yes | 31.0 | 52.0 | 0.17 | take_profit |
| 2026-05-11T02:51:20.993409+00:00 | KXBTC15M-26MAY102300-00 | no | 34.0 | 46.0 | 0.08 | max_hold |
| 2026-05-11T03:06:16.074311+00:00 | KXBTC15M-26MAY102315-15 | yes | 18.0 | 51.0 | 0.29 | take_profit |
| 2026-05-11T03:20:45.344914+00:00 | KXBTC15M-26MAY102330-30 | yes | 27.0 | 45.0 | 0.14 | take_profit |
| 2026-05-11T03:35:51.206317+00:00 | KXBTC15M-26MAY102345-45 | yes | 38.0 | 89.0 | 0.48 | take_profit |
| 2026-05-11T04:51:15.598184+00:00 | KXBTC15M-26MAY110100-00 | yes | 32.0 | 95.0 | 0.6 | take_profit |
| 2026-05-11T05:55:37.141400+00:00 | KXBTC15M-26MAY110200-00 | no | 27.0 | 67.0 | 0.36 | take_profit |
| 2026-05-11T06:21:39.914846+00:00 | KXBTC15M-26MAY110230-30 | yes | 40.0 | 87.0 | 0.44 | take_profit |
| 2026-05-11T06:50:19.862832+00:00 | KXBTC15M-26MAY110300-00 | yes | 30.0 | 49.0 | 0.15 | take_profit |
| 2026-05-11T07:05:19.709889+00:00 | KXBTC15M-26MAY110315-15 | yes | 8.0 | 27.0 | 0.16 | take_profit |
| 2026-05-11T07:50:21.221259+00:00 | KXBTC15M-26MAY110400-00 | no | 27.0 | 42.0 | 0.11 | max_hold |
| 2026-05-11T08:50:35.361217+00:00 | KXBTC15M-26MAY110500-00 | no | 41.0 | 44.0 | -0.01 | max_hold |
| 2026-05-11T09:23:51.607036+00:00 | KXBTC15M-26MAY110530-30 | yes | 22.0 | 48.0 | 0.22 | take_profit |
| 2026-05-11T09:35:05.229446+00:00 | KXBTC15M-26MAY110545-45 | yes | 33.0 | 71.0 | 0.34 | take_profit |
| 2026-05-11T09:50:05.607925+00:00 | KXBTC15M-26MAY110600-00 | no | 28.0 | 60.0 | 0.28 | take_profit |
| 2026-05-11T10:06:00.023309+00:00 | KXBTC15M-26MAY110615-15 | no | 38.0 | 49.0 | 0.07 | max_hold |
| 2026-05-11T10:20:00.110283+00:00 | KXBTC15M-26MAY110630-30 | no | 11.0 | 60.0 | 0.46 | take_profit |
| 2026-05-11T11:05:06.875914+00:00 | KXBTC15M-26MAY110715-15 | no | 32.0 | 42.0 | 0.06 | max_hold |
| 2026-05-11T11:35:03.126980+00:00 | KXBTC15M-26MAY110745-45 | no | 26.0 | 39.0 | 0.09 | max_hold |
