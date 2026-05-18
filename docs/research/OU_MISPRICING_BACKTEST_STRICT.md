# OU Mispricing Optimal-Stopping Backtest

Brand-new research lane: Brownian fair value from BTC spot/strike plus Carr-inspired OU simulation on Kalshi probability mispricing.

Audit note: this is not a paper-exact Carr/Lopez de Prado implementation. The paper optimizes exit corridors for an already-open position; this harness adds a new fair-value entry rule, Kalshi fees/spreads, and historical-tape PnL scoring.

- Generated UTC: `2026-05-14T17:44:16Z`
- Event files: `1`
- Market-results source: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api\market_results.csv`
- Snapshots after filters: `13712`
- Markets: `213`
- Trades: `115`
- Net PnL: `8.49` dollars
- Realized/settled PnL excluding open mark-to-last rows: `8.49` dollars on `115` trades
- Open mark-to-last PnL: `0.0` dollars on `0` trades
- Win rate: `0.513`
- Sim decisions scored: `117`

## Exit Reasons

- `max_hold`: 33
- `settlement_after_tape`: 58
- `take_profit`: 24

## Rejection Counts

- `edge_or_z`: 5424
- `one_entry_per_market`: 3454
- `sim_gate`: 2
- `spread`: 207
- `time_window`: 4391
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
| 2026-05-11T02:36:19.923391+00:00 | KXBTC15M-26MAY102245-45 | yes | 28.0 | 52.0 | 0.2 | take_profit |
| 2026-05-11T02:51:20.993409+00:00 | KXBTC15M-26MAY102300-00 | no | 34.0 | 46.0 | 0.08 | max_hold |
| 2026-05-11T03:06:16.074311+00:00 | KXBTC15M-26MAY102315-15 | yes | 18.0 | 51.0 | 0.29 | take_profit |
| 2026-05-11T03:20:55.190901+00:00 | KXBTC15M-26MAY102330-30 | yes | 28.0 | 2.0 | -0.29 | max_hold |
| 2026-05-11T03:36:38.028838+00:00 | KXBTC15M-26MAY102345-45 | yes | 23.0 | 49.0 | 0.22 | take_profit |
| 2026-05-11T04:51:15.598184+00:00 | KXBTC15M-26MAY110100-00 | yes | 32.0 | 95.0 | 0.6 | take_profit |
| 2026-05-11T05:55:37.141400+00:00 | KXBTC15M-26MAY110200-00 | no | 27.0 | 67.0 | 0.36 | take_profit |
| 2026-05-11T06:09:28.590480+00:00 | KXBTC15M-26MAY110215-15 | no | 12.0 | 56.0 | 0.41 | take_profit |
| 2026-05-11T06:21:39.914846+00:00 | KXBTC15M-26MAY110230-30 | yes | 40.0 | 87.0 | 0.44 | take_profit |
| 2026-05-11T07:50:21.221259+00:00 | KXBTC15M-26MAY110400-00 | no | 27.0 | 42.0 | 0.11 | max_hold |
| 2026-05-11T08:50:44.695438+00:00 | KXBTC15M-26MAY110500-00 | no | 42.0 | 44.0 | -0.02 | max_hold |
| 2026-05-11T09:23:51.607036+00:00 | KXBTC15M-26MAY110530-30 | yes | 22.0 | 48.0 | 0.22 | take_profit |
| 2026-05-11T09:36:25.244283+00:00 | KXBTC15M-26MAY110545-45 | yes | 27.0 | 71.0 | 0.4 | take_profit |
| 2026-05-11T09:50:05.607925+00:00 | KXBTC15M-26MAY110600-00 | no | 28.0 | 60.0 | 0.28 | take_profit |
| 2026-05-11T10:20:40.112579+00:00 | KXBTC15M-26MAY110630-30 | no | 11.0 | 60.0 | 0.46 | take_profit |
| 2026-05-11T11:05:06.875914+00:00 | KXBTC15M-26MAY110715-15 | no | 32.0 | 42.0 | 0.06 | max_hold |
| 2026-05-11T11:35:03.126980+00:00 | KXBTC15M-26MAY110745-45 | no | 26.0 | 39.0 | 0.09 | max_hold |
| 2026-05-11T11:50:02.656077+00:00 | KXBTC15M-26MAY110800-00 | yes | 39.0 | 30.0 | -0.13 | max_hold |
| 2026-05-11T12:20:02.958923+00:00 | KXBTC15M-26MAY110830-30 | no | 39.0 | 41.0 | -0.02 | max_hold |
