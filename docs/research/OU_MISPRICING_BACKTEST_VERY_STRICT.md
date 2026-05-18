# OU Mispricing Optimal-Stopping Backtest

Brand-new research lane: Brownian fair value from BTC spot/strike plus Carr-inspired OU simulation on Kalshi probability mispricing.

Audit note: this is not a paper-exact Carr/Lopez de Prado implementation. The paper optimizes exit corridors for an already-open position; this harness adds a new fair-value entry rule, Kalshi fees/spreads, and historical-tape PnL scoring.

- Generated UTC: `2026-05-14T17:44:15Z`
- Event files: `1`
- Market-results source: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api\market_results.csv`
- Snapshots after filters: `13712`
- Markets: `213`
- Trades: `98`
- Net PnL: `13.76` dollars
- Realized/settled PnL excluding open mark-to-last rows: `13.76` dollars on `98` trades
- Open mark-to-last PnL: `0.0` dollars on `0` trades
- Win rate: `0.5816`
- Sim decisions scored: `99`

## Exit Reasons

- `max_hold`: 17
- `settlement_after_tape`: 54
- `take_profit`: 27

## Rejection Counts

- `edge_or_z`: 6583
- `one_entry_per_market`: 2301
- `sim_gate`: 1
- `spread`: 187
- `time_window`: 4423
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
| 2026-05-11T03:20:55.190901+00:00 | KXBTC15M-26MAY102330-30 | yes | 28.0 | 2.0 | -0.29 | max_hold |
| 2026-05-11T03:41:34.345850+00:00 | KXBTC15M-26MAY102345-45 | no | 22.0 | 49.0 | 0.23 | take_profit |
| 2026-05-11T04:51:55.632071+00:00 | KXBTC15M-26MAY110100-00 | yes | 33.0 | 95.0 | 0.59 | take_profit |
| 2026-05-11T05:55:37.141400+00:00 | KXBTC15M-26MAY110200-00 | no | 27.0 | 67.0 | 0.36 | take_profit |
| 2026-05-11T06:09:28.590480+00:00 | KXBTC15M-26MAY110215-15 | no | 12.0 | 56.0 | 0.41 | take_profit |
| 2026-05-11T07:10:54.532169+00:00 | KXBTC15M-26MAY110315-15 | yes | 2.0 | 27.0 | 0.22 | take_profit |
| 2026-05-11T07:50:21.221259+00:00 | KXBTC15M-26MAY110400-00 | no | 27.0 | 42.0 | 0.11 | max_hold |
| 2026-05-11T09:27:44.960353+00:00 | KXBTC15M-26MAY110530-30 | no | 30.0 | 50.0 | 0.16 | take_profit |
| 2026-05-11T09:36:25.244283+00:00 | KXBTC15M-26MAY110545-45 | yes | 27.0 | 71.0 | 0.4 | take_profit |
| 2026-05-11T09:50:05.607925+00:00 | KXBTC15M-26MAY110600-00 | no | 28.0 | 60.0 | 0.28 | take_profit |
| 2026-05-11T11:05:06.875914+00:00 | KXBTC15M-26MAY110715-15 | no | 32.0 | 42.0 | 0.06 | max_hold |
| 2026-05-11T11:35:03.126980+00:00 | KXBTC15M-26MAY110745-45 | no | 26.0 | 39.0 | 0.09 | max_hold |
| 2026-05-11T11:50:14.559631+00:00 | KXBTC15M-26MAY110800-00 | yes | 37.0 | 30.0 | -0.11 | max_hold |
| 2026-05-11T12:20:02.958923+00:00 | KXBTC15M-26MAY110830-30 | no | 39.0 | 41.0 | -0.02 | max_hold |
| 2026-05-11T16:27:33.944143+00:00 | KXBTC15M-26MAY111230-30 | no | 8.0 | 38.0 | 0.27 | take_profit |
| 2026-05-11T16:35:34.328454+00:00 | KXBTC15M-26MAY111245-45 | no | 22.0 | 31.0 | 0.05 | max_hold |
| 2026-05-11T19:12:34.270980+00:00 | KXBTC15M-26MAY111515-15 | no | 8.0 | 50.0 | 0.39 | take_profit |
| 2026-05-11T20:29:00.005497+00:00 | KXBTC15M-26MAY111630-30 | yes | 13.0 | 47.0 | 0.31 | take_profit |
| 2026-05-12T05:27:00.553198+00:00 | KXBTC15M-26MAY120130-30 | no | 2.0 | 31.0 | 0.26 | take_profit |
