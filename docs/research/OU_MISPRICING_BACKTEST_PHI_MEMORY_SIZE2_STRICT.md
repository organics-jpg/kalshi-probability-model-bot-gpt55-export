# OU Mispricing Optimal-Stopping Backtest

Brand-new research lane: Brownian fair value from BTC spot/strike plus Carr-inspired OU simulation on Kalshi probability mispricing.

Audit note: this is not a paper-exact Carr/Lopez de Prado implementation. The paper optimizes exit corridors for an already-open position; this harness adds a new fair-value entry rule, Kalshi fees/spreads, and historical-tape PnL scoring.

- Generated UTC: `2026-05-14T17:45:24Z`
- Event files: `1`
- Market-results source: `stats\mushroom_v28_common_clock_phi_reward_memory_size2_live\market_results.csv`
- Snapshots after filters: `833`
- Markets: `20`
- Trades: `14`
- Net PnL: `1.11` dollars
- Realized/settled PnL excluding open mark-to-last rows: `1.11` dollars on `14` trades
- Open mark-to-last PnL: `0.0` dollars on `0` trades
- Win rate: `0.5`
- Sim decisions scored: `21`

## Exit Reasons

- `max_hold`: 4
- `settlement_after_tape`: 8
- `take_profit`: 2

## Rejection Counts

- `edge_or_z`: 72
- `one_entry_per_market`: 381
- `sim_gate`: 7
- `spread`: 9
- `time_window`: 231
- `warming`: 119

## First Trades

| Entry | Market | Side | Entry | Exit | PnL $ | Reason |
|---|---|---:|---:|---:|---:|---|
| 2026-05-10T18:50:05.989658+00:00 | KXBTC15M-26MAY101500-00 | no | 27.0 | 44.0 | 0.13 | max_hold |
| 2026-05-10T19:05:24.311578+00:00 | KXBTC15M-26MAY101515-15 | yes | 20.0 | 96.0 | 0.73 | take_profit |
| 2026-05-10T19:20:59.053200+00:00 | KXBTC15M-26MAY101530-30 | no | 24.0 | 45.0 | 0.17 | max_hold |
| 2026-05-10T19:51:33.788963+00:00 | KXBTC15M-26MAY101600-00 | yes | 11.0 | 9.0 | -0.04 | max_hold |
| 2026-05-10T22:21:17.372081+00:00 | KXBTC15M-26MAY101830-30 | yes | 41.0 | 94.0 | 0.5 | take_profit |
| 2026-05-10T22:50:00.997399+00:00 | KXBTC15M-26MAY101900-00 | no | 35.0 | 41.0 | 0.02 | max_hold |
| 2026-05-10T18:21:57.723681+00:00 | KXBTC15M-26MAY101430-30 | yes | 38.0 | 0.0 | -0.4 | settlement_after_tape |
| 2026-05-10T18:38:00.788487+00:00 | KXBTC15M-26MAY101445-45 | yes | 34.0 | 0.0 | -0.36 | settlement_after_tape |
| 2026-05-10T19:35:01.073448+00:00 | KXBTC15M-26MAY101545-45 | yes | 29.0 | 0.0 | -0.31 | settlement_after_tape |
| 2026-05-10T20:07:46.950919+00:00 | KXBTC15M-26MAY101615-15 | no | 34.0 | 100.0 | 0.64 | settlement_after_tape |
| 2026-05-10T20:21:51.999174+00:00 | KXBTC15M-26MAY101630-30 | yes | 30.0 | 0.0 | -0.32 | settlement_after_tape |
| 2026-05-10T20:37:35.499878+00:00 | KXBTC15M-26MAY101645-45 | yes | 30.0 | 0.0 | -0.32 | settlement_after_tape |
| 2026-05-10T20:56:40.627217+00:00 | KXBTC15M-26MAY101700-00 | yes | 1.0 | 0.0 | -0.02 | settlement_after_tape |
| 2026-05-10T21:05:04.088511+00:00 | KXBTC15M-26MAY101715-15 | no | 29.0 | 100.0 | 0.69 | settlement_after_tape |
