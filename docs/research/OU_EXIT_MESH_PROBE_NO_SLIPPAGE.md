# OU exit mesh probe

Generated: 2026-05-14T12:43:37.071685+00:00

## Verdict

There is a real exit-shape worth studying, but not yet a profitable Carr-inspired strategy. A retrospective grid can find positive nodes on this small sample, while the simulation-selected walk-forward result does not clear the profitability gate.

## Inputs

- Trades: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api\trades.csv`
- Market results: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api\market_results.csv`
- Execution events: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\execution_events.ndjson`
- Trade rows usable after resolved/path filters: 85 of 95
- Exit model: same-side sell bid reconstructed as `100 - opposite ask`, with 0.0c slippage and 30.0s minimum hold.

## Baseline

- Actual API-reconciled net PnL on usable trades: -6.6400 dollars
- Actual wins/losses by row sign: 18 / 64

## OU Diagnostics

- BTC strike-gap AR(1): phi=0.99895424, half_life_steps=662.4671, pairs=7915
- Held-position MtM PnL AR(1): phi=1.00023539, half_life_steps=None, mu_cents=-93.776157, sigma_cents=3.823351, pairs=5423

## Best Retrospective Real-Path Grid

- Best full-sample rule by real observed paths: PT=+19c, SL=-55c
- Counterfactual net PnL: 2.67 dollars; delta vs actual: 9.31 dollars; win rate: 0.4471; exit rate: 0.3882

## Carr-Inspired Simulated Selection

- Full-sample simulation-selected rule: PT=+39c, SL=-1c, simulated Sharpe-like=-0.015019
- Walk-forward aggregate net PnL: -5.3190 dollars
- Same slices actual net PnL: -5.4100 dollars
- Walk-forward delta vs actual: 0.0910 dollars
- Historical-grid walk-forward net PnL: -1.2900 dollars; delta vs actual: 4.1200 dollars

## Walk-Forward Parts

| Test start | Rows | Selected PT | Selected SL | Test net | Actual net | Delta |
|---|---:|---:|---:|---:|---:|---:|
| 2026-05-11T02:42:31+00:00 | 15 | 39 | 1 | -1.47 | -1.58 | 0.11 |
| 2026-05-11T07:11:06+00:00 | 15 | 39 | 1 | 0.571 | 0.07 | 0.501 |
| 2026-05-11T09:42:18+00:00 | 15 | 39 | 1 | -3.38 | -2.22 | -1.16 |
| 2026-05-11T11:32:11+00:00 | 10 | 37 | 1 | -1.04 | -1.68 | 0.64 |

## Top Retrospective Nodes

| PT | SL | Net | Delta vs actual | Win rate | Exit rate | Avg hold sec |
|---:|---:|---:|---:|---:|---:|---:|
| 19 | 55 | 2.67 | 9.31 | 0.4471 | 0.3882 | 311.62 |
| 19 | 56 | 2.65 | 9.29 | 0.4471 | 0.3882 | 311.63 |
| 19 | 57 | 2.6 | 9.24 | 0.4471 | 0.3882 | 311.64 |
| 18 | 55 | 2.35 | 8.99 | 0.4471 | 0.3882 | 309.02 |
| 18 | 56 | 2.33 | 8.97 | 0.4471 | 0.3882 | 309.02 |
| 18 | 57 | 2.28 | 8.92 | 0.4471 | 0.3882 | 309.04 |
| 19 | 58 | 1.89 | 8.53 | 0.4471 | 0.3765 | 313.42 |
| 19 | 59 | 1.77 | 8.41 | 0.4471 | 0.3765 | 313.93 |
| 19 | 60 | 1.77 | 8.41 | 0.4471 | 0.3765 | 313.93 |
| 19 | 61 | 1.77 | 8.41 | 0.4471 | 0.3765 | 313.93 |
