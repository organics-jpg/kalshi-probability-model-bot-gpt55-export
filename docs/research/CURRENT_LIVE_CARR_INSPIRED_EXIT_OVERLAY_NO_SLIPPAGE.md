# OU exit mesh probe

Generated: 2026-05-14T17:29:39.169004+00:00

## Verdict

No profitable strategy is supported yet. Under the current fee/slippage/path reconstruction, neither the retrospective real-path mesh nor the Carr-inspired OU walk-forward selection clears a positive-PnL gate.

## Inputs

- Trades: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api\trades.csv`
- Market results: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api\market_results.csv`
- Execution events: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\execution_events.ndjson`
- Trade rows usable after resolved/path filters: 95 of 95
- Exit model: same-side sell bid reconstructed as `100 - opposite ask`, with 0.0c slippage and 30.0s minimum hold.

## Baseline

- Actual API-reconciled net PnL on usable trades: -7.8300 dollars
- Actual wins/losses by row sign: 18 / 73

## OU Diagnostics

- BTC strike-gap AR(1): phi=0.99895424, half_life_steps=662.4671, pairs=7915
- Held-position MtM PnL AR(1): phi=1.00144242, half_life_steps=None, mu_cents=2.794329, sigma_cents=3.495029, pairs=6968

## Best Retrospective Real-Path Grid

- Best full-sample rule by real observed paths: PT=+22c, SL=-12c
- Counterfactual net PnL: -1.95 dollars; delta vs actual: 5.88 dollars; win rate: 0.2842; exit rate: 0.4526

## Carr-Inspired Simulated Selection

- Full-sample simulation-selected rule: PT=+39c, SL=-1c, simulated Sharpe-like=-0.032093
- Walk-forward aggregate net PnL: -6.5590 dollars
- Same slices actual net PnL: -6.6000 dollars
- Walk-forward delta vs actual: 0.0410 dollars
- Historical-grid walk-forward net PnL: -7.3300 dollars; delta vs actual: -0.7300 dollars

## Walk-Forward Parts

| Test start | Rows | Selected PT | Selected SL | Test net | Actual net | Delta |
|---|---:|---:|---:|---:|---:|---:|
| 2026-05-11T02:42:31+00:00 | 15 | 39 | 1 | -1.26 | -1.21 | -0.05 |
| 2026-05-11T05:41:47+00:00 | 15 | 39 | 1 | -0.7 | -1.39 | 0.69 |
| 2026-05-11T08:26:03+00:00 | 15 | 39 | 1 | -0.469 | 0.56 | -1.029 |
| 2026-05-11T10:47:10+00:00 | 15 | 39 | 1 | -3.85 | -4.0 | 0.15 |
| 2026-05-11T16:26:57+00:00 | 5 | 39 | 1 | -0.28 | -0.56 | 0.28 |

## Top Retrospective Nodes

| PT | SL | Net | Delta vs actual | Win rate | Exit rate | Avg hold sec |
|---:|---:|---:|---:|---:|---:|---:|
| 22 | 12 | -1.95 | 5.88 | 0.2842 | 0.4526 | 250.48 |
| 19 | 28 | -2.0 | 5.83 | 0.3474 | 0.4 | 282.4 |
| 30 | 12 | -2.0 | 5.83 | 0.2737 | 0.3684 | 274.57 |
| 31 | 12 | -2.0 | 5.83 | 0.2737 | 0.3684 | 274.57 |
| 32 | 12 | -2.0 | 5.83 | 0.2737 | 0.3684 | 274.57 |
| 33 | 12 | -2.0 | 5.83 | 0.2737 | 0.3684 | 274.57 |
| 34 | 12 | -2.0 | 5.83 | 0.2737 | 0.3684 | 274.57 |
| 29 | 12 | -2.04 | 5.79 | 0.2737 | 0.3789 | 272.52 |
| 27 | 12 | -2.07 | 5.76 | 0.2737 | 0.3789 | 271.89 |
| 28 | 12 | -2.07 | 5.76 | 0.2737 | 0.3789 | 271.89 |
