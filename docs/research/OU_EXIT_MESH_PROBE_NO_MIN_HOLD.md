# OU exit mesh probe

Generated: 2026-05-14T12:41:59.175276+00:00

## Verdict

There is a real exit-shape worth studying, but not yet a profitable Carr-inspired strategy. A retrospective grid can find positive nodes on this small sample, while the simulation-selected walk-forward result does not clear the profitability gate.

## Inputs

- Trades: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api\trades.csv`
- Market results: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api\market_results.csv`
- Execution events: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\execution_events.ndjson`
- Trade rows usable after resolved/path filters: 85 of 95
- Exit model: same-side sell bid reconstructed as `100 - opposite ask`, with 1.0c slippage and 0.0s minimum hold.

## Baseline

- Actual API-reconciled net PnL on usable trades: -6.6400 dollars
- Actual wins/losses by row sign: 18 / 64

## OU Diagnostics

- BTC strike-gap AR(1): phi=0.99895424, half_life_steps=662.4671, pairs=7915
- Held-position MtM PnL AR(1): phi=0.99916669, half_life_steps=831.4582, mu_cents=27.698985, sigma_cents=3.80145, pairs=5986

## Best Retrospective Real-Path Grid

- Best full-sample rule by real observed paths: PT=+18c, SL=-56c
- Counterfactual net PnL: 1.79 dollars; delta vs actual: 8.43 dollars; win rate: 0.4471; exit rate: 0.3882

## Carr-Inspired Simulated Selection

- Full-sample simulation-selected rule: PT=+39c, SL=-1c, simulated Sharpe-like=-0.127234
- Walk-forward aggregate net PnL: -8.8400 dollars
- Same slices actual net PnL: -5.4100 dollars
- Walk-forward delta vs actual: -3.4300 dollars

## Walk-Forward Parts

| Test start | Rows | Selected PT | Selected SL | Test net | Actual net | Delta |
|---|---:|---:|---:|---:|---:|---:|
| 2026-05-11T02:42:31+00:00 | 15 | 39 | 1 | -1.39 | -1.58 | 0.19 |
| 2026-05-11T07:11:06+00:00 | 15 | 39 | 1 | -2.76 | 0.07 | -2.83 |
| 2026-05-11T09:42:18+00:00 | 15 | 39 | 1 | -3.39 | -2.22 | -1.17 |
| 2026-05-11T11:32:11+00:00 | 10 | 39 | 1 | -1.3 | -1.68 | 0.38 |

## Top Retrospective Nodes

| PT | SL | Net | Delta vs actual | Win rate | Exit rate | Avg hold sec |
|---:|---:|---:|---:|---:|---:|---:|
| 18 | 56 | 1.79 | 8.43 | 0.4471 | 0.3882 | 311.62 |
| 18 | 57 | 1.76 | 8.4 | 0.4471 | 0.3882 | 311.63 |
| 18 | 58 | 1.7 | 8.34 | 0.4471 | 0.3882 | 311.64 |
| 17 | 56 | 1.48 | 8.12 | 0.4471 | 0.3882 | 309.02 |
| 17 | 57 | 1.45 | 8.09 | 0.4471 | 0.3882 | 309.02 |
| 17 | 58 | 1.39 | 8.03 | 0.4471 | 0.3882 | 309.04 |
| 18 | 59 | 1.02 | 7.66 | 0.4471 | 0.3765 | 313.42 |
| 18 | 60 | 0.9 | 7.54 | 0.4471 | 0.3765 | 313.93 |
| 18 | 61 | 0.9 | 7.54 | 0.4471 | 0.3765 | 313.93 |
| 18 | 62 | 0.9 | 7.54 | 0.4471 | 0.3765 | 313.93 |
