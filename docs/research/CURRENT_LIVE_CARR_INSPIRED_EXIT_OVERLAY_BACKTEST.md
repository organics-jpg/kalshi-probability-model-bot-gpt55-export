# OU exit mesh probe

Generated: 2026-05-14T17:29:59.284201+00:00

## Verdict

No profitable strategy is supported yet. Under the current fee/slippage/path reconstruction, neither the retrospective real-path mesh nor the Carr-inspired OU walk-forward selection clears a positive-PnL gate.

## Inputs

- Trades: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api\trades.csv`
- Market results: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api\market_results.csv`
- Execution events: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\execution_events.ndjson`
- Trade rows usable after resolved/path filters: 95 of 95
- Exit model: same-side sell bid reconstructed as `100 - opposite ask`, with 1.0c slippage and 30.0s minimum hold.

## Baseline

- Actual API-reconciled net PnL on usable trades: -7.8300 dollars
- Actual wins/losses by row sign: 18 / 73

## OU Diagnostics

- BTC strike-gap AR(1): phi=0.99895424, half_life_steps=662.4671, pairs=7915
- Held-position MtM PnL AR(1): phi=1.00122976, half_life_steps=None, mu_cents=-1.636599, sigma_cents=3.493402, pairs=6968

## Best Retrospective Real-Path Grid

- Best full-sample rule by real observed paths: PT=+29c, SL=-13c
- Counterfactual net PnL: -2.79 dollars; delta vs actual: 5.04 dollars; win rate: 0.2737; exit rate: 0.3474

## Carr-Inspired Simulated Selection

- Full-sample simulation-selected rule: PT=+39c, SL=-1c, simulated Sharpe-like=-0.100038
- Walk-forward aggregate net PnL: -8.4755 dollars
- Same slices actual net PnL: -6.6000 dollars
- Walk-forward delta vs actual: -1.8755 dollars
- Historical-grid walk-forward net PnL: -7.9900 dollars; delta vs actual: -1.3900 dollars

## Walk-Forward Parts

| Test start | Rows | Selected PT | Selected SL | Test net | Actual net | Delta |
|---|---:|---:|---:|---:|---:|---:|
| 2026-05-11T02:42:31+00:00 | 15 | 39 | 1 | -1.27 | -1.21 | -0.06 |
| 2026-05-11T05:41:47+00:00 | 15 | 39 | 1 | -0.92 | -1.39 | 0.47 |
| 2026-05-11T08:26:03+00:00 | 15 | 39 | 1 | -1.7255 | 0.56 | -2.2855 |
| 2026-05-11T10:47:10+00:00 | 15 | 39 | 1 | -4.21 | -4.0 | -0.21 |
| 2026-05-11T16:26:57+00:00 | 5 | 39 | 1 | -0.35 | -0.56 | 0.21 |

## Top Retrospective Nodes

| PT | SL | Net | Delta vs actual | Win rate | Exit rate | Avg hold sec |
|---:|---:|---:|---:|---:|---:|---:|
| 29 | 13 | -2.79 | 5.04 | 0.2737 | 0.3474 | 277.55 |
| 30 | 13 | -2.79 | 5.04 | 0.2737 | 0.3474 | 277.55 |
| 31 | 13 | -2.79 | 5.04 | 0.2737 | 0.3474 | 277.55 |
| 32 | 13 | -2.79 | 5.04 | 0.2737 | 0.3474 | 277.55 |
| 33 | 13 | -2.79 | 5.04 | 0.2737 | 0.3474 | 277.55 |
| 28 | 13 | -2.86 | 4.97 | 0.2737 | 0.3579 | 275.5 |
| 26 | 13 | -2.89 | 4.94 | 0.2737 | 0.3579 | 274.87 |
| 27 | 13 | -2.89 | 4.94 | 0.2737 | 0.3579 | 274.87 |
| 25 | 13 | -2.95 | 4.88 | 0.2737 | 0.3579 | 274.66 |
| 21 | 13 | -2.95 | 4.88 | 0.2842 | 0.4316 | 253.46 |
