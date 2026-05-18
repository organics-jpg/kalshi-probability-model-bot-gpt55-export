# OU Mispricing Optimal-Stopping Backtest

Brand-new research lane: Brownian fair value from BTC spot/strike plus Carr-inspired OU simulation on Kalshi probability mispricing.

Audit note: this is not a paper-exact Carr/Lopez de Prado implementation. The paper optimizes exit corridors for an already-open position; this harness adds a new fair-value entry rule, Kalshi fees/spreads, and historical-tape PnL scoring.

- Generated UTC: `2026-05-14T18:04:12Z`
- Event files: `26`
- Market-results source: ``
- Snapshots after filters: `39642`
- Markets: `812`
- Trades: `595`
- Net PnL: `22.15` dollars
- Realized/settled PnL excluding open mark-to-last rows: `23.26` dollars on `577` trades
- Open mark-to-last PnL: `-1.11` dollars on `18` trades
- Win rate: `0.4807`
- Sim decisions scored: `645`

## Exit Reasons

- `last_bid_after_tape`: 18
- `max_hold`: 220
- `settlement_after_tape`: 209
- `stop_loss`: 17
- `take_profit`: 131

## Rejection Counts

- `edge_or_z`: 6223
- `one_entry_per_market`: 18932
- `sim_gate`: 50
- `spread`: 843
- `time_window`: 12880
- `warming`: 119

## First Trades

| Entry | Market | Side | Entry | Exit | PnL $ | Reason |
|---|---|---:|---:|---:|---:|---|
| 2026-05-01T14:36:29.663280+00:00 | KXBTC15M-26MAY011045-45 | no | 75.0 | 69.0 | -0.1 | max_hold |
| 2026-05-01T19:36:32.795937+00:00 | KXBTC15M-26MAY011545-45 | yes | 16.0 | 4.0 | -0.14 | max_hold |
| 2026-05-01T19:51:18.243972+00:00 | KXBTC15M-26MAY011600-00 | yes | 79.0 | 90.0 | 0.08 | max_hold |
| 2026-05-02T01:36:03.286998+00:00 | KXBTC15M-26MAY012145-45 | no | 15.0 | 14.0 | -0.03 | max_hold |
| 2026-05-02T05:21:08.311750+00:00 | KXBTC15M-26MAY020130-30 | yes | 27.0 | 15.0 | -0.15 | max_hold |
| 2026-05-02T15:08:20.401074+00:00 | KXBTC15M-26MAY021115-15 | yes | 87.0 | 86.0 | -0.03 | max_hold |
| 2026-05-03T13:50:36.684791+00:00 | KXBTC15M-26MAY031000-00 | no | 23.0 | 21.0 | -0.06 | max_hold |
| 2026-05-03T15:05:20.594225+00:00 | KXBTC15M-26MAY031115-15 | yes | 77.0 | 58.0 | -0.23 | max_hold |
| 2026-05-03T19:07:21.502797+00:00 | KXBTC15M-26MAY031515-15 | yes | 63.0 | 60.0 | -0.07 | max_hold |
| 2026-05-03T20:56:22.227815+00:00 | KXBTC15M-26MAY031700-00 | yes | 1.0 | 0.0 | -0.03 | max_hold |
| 2026-05-03T21:37:19.997058+00:00 | KXBTC15M-26MAY031745-45 | no | 81.0 | 80.0 | -0.05 | max_hold |
| 2026-05-03T21:53:26.829588+00:00 | KXBTC15M-26MAY031800-00 | yes | 78.0 | 100.0 | 0.19 | max_hold |
| 2026-05-04T08:05:42.588064+00:00 | KXBTC15M-26MAY040415-15 | no | 82.0 | 81.0 | -0.05 | max_hold |
| 2026-05-04T08:51:34.297217+00:00 | KXBTC15M-26MAY040500-00 | yes | 15.0 | 75.0 | 0.57 | take_profit |
| 2026-05-04T09:10:29.371799+00:00 | KXBTC15M-26MAY040515-15 | yes | 54.0 | 83.0 | 0.26 | take_profit |
| 2026-05-04T09:26:03.580586+00:00 | KXBTC15M-26MAY040530-30 | no | 19.0 | 18.0 | -0.05 | max_hold |
| 2026-05-04T13:35:33.923536+00:00 | KXBTC15M-26MAY040945-45 | yes | 72.0 | 62.0 | -0.14 | max_hold |
| 2026-05-04T13:53:03.464813+00:00 | KXBTC15M-26MAY041000-00 | yes | 21.0 | 3.0 | -0.21 | max_hold |
| 2026-05-04T15:05:03.132059+00:00 | KXBTC15M-26MAY041115-15 | yes | 23.0 | 0.0 | -0.26 | max_hold |
| 2026-05-04T15:52:32.689995+00:00 | KXBTC15M-26MAY041200-00 | no | 86.0 | 87.0 | -0.01 | max_hold |
| 2026-05-04T16:07:50.655607+00:00 | KXBTC15M-26MAY041215-15 | yes | 22.0 | 0.0 | -0.25 | max_hold |
| 2026-05-04T21:35:36.688628+00:00 | KXBTC15M-26MAY041745-45 | no | 19.0 | 18.0 | -0.05 | max_hold |
| 2026-05-04T21:50:01.833031+00:00 | KXBTC15M-26MAY041800-00 | yes | 83.0 | 68.0 | -0.18 | max_hold |
| 2026-05-04T22:51:01.817718+00:00 | KXBTC15M-26MAY041900-00 | no | 21.0 | 21.0 | -0.04 | max_hold |
| 2026-05-05T02:06:20.233467+00:00 | KXBTC15M-26MAY042215-15 | no | 22.0 | 21.0 | -0.05 | max_hold |
