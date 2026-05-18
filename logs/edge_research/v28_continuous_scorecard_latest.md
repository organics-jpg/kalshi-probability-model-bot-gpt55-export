# v28 Continuous Scorecard

- Goal: durable risk-adjusted ROI from the v28 BTC 15m strategy.
- Mode: quiet continuous monitoring; old logs are diagnostic only.

## Risk-Adjusted Score

- Entries: `173`
- Watched markets: `181`
- Entered markets: `107`
- Shadow coverage: `59.12%`
- Scored trades: `173`
- Settled trades: `173`
- Wins: `146`
- Gross P&L: `$8.23`
- Current account balance reference: `$26.40`
- Hold-to-settlement P&L: `$23.04`
- Exit value vs hold: `$-14.81`
- Trial ROI on start balance: `64.50%`
- Shadow P&L as % of current account: `31.17%`
- Max drawdown: `$-1.96` / `15.36%`
- Net losing trades: `75`
- Max loss streak: `6`
- Risk stop active: `True` `loss_count`
- Avg Brier: `0.13363403471027746`

## Reject / Opportunity Telemetry

- Reject events: `22578`
- Reject markets: `175`
- Near misses: `128`

### Reject Reasons

- `ask_too_high`: 1301
- `book_stale`: 3358
- `btc_stale`: 9170
- `edge_below_floor`: 297
- `missing_horizon`: 609
- `missing_strike`: 1158
- `p_below_floor`: 5431
- `risk_or_depth`: 3
- `time_window`: 1249
- `warming`: 2

## Failure Attribution

- `exit_policy_cost`: 74
- `fv_or_entry_timing_error`: 22
- `none`: 77

## Latest Rows

| market | side | result | gross c | hold c | exit value c | failure | flags |
|---|---|---|---:|---:|---:|---|---|
| KXBTC15M-26MAY071130-30 | no | no | 30 | 30 | 0 | none | h1_feed_fresh,h6_recross_hazard_high |
| KXBTC15M-26MAY071145-45 | yes | yes | 44 | 46 | -2 | none | h1_feed_fresh,h6_recross_hazard_high |
| KXBTC15M-26MAY071200-00 | no | no | 42 | 46 | -4 | none | h1_feed_fresh,h5_late_high_sigma |
| KXBTC15M-26MAY071215-15 | no | no | -16 | 32 | -48 | exit_policy_cost | h1_feed_fresh,h2_thin_touch_depth,h6_recross_hazard_high |
| KXBTC15M-26MAY071215-15 | no | no | 2 | 44 | -42 | exit_policy_cost | h1_feed_fresh,h6_recross_hazard_high |
| KXBTC15M-26MAY071215-15 | no | no | -8 | 40 | -48 | exit_policy_cost | h1_feed_fresh,h2_crowded_depth |
| KXBTC15M-26MAY071230-30 | yes | yes | -10 | 46 | -56 | exit_policy_cost | h1_feed_fresh,h2_thin_touch_depth,h6_recross_hazard_high |
| KXBTC15M-26MAY071230-30 | yes | yes | -38 | 32 | -70 | exit_policy_cost | h1_feed_fresh |
| KXBTC15M-26MAY071230-30 | yes | yes | 40 | 40 | 0 | none | h1_feed_fresh |
| KXBTC15M-26MAY071315-15 | yes | yes | -6 | 40 | -46 | exit_policy_cost | h1_feed_fresh,h6_recross_hazard_high |
| KXBTC15M-26MAY071315-15 | yes | yes | -14 | 38 | -52 | exit_policy_cost | h1_feed_fresh,h2_thin_touch_depth |
| KXBTC15M-26MAY071315-15 | yes | yes | 32 | 44 | -12 | none | h1_feed_fresh,h2_thin_touch_depth |
