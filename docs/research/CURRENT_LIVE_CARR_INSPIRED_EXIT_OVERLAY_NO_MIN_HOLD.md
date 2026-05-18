# OU exit mesh probe

Generated: 2026-05-14T17:29:40.230238+00:00

## Verdict

No profitable strategy is supported yet. Under the current fee/slippage/path reconstruction, neither the retrospective real-path mesh nor the Carr-inspired OU walk-forward selection clears a positive-PnL gate.

## Inputs

- Trades: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api\trades.csv`
- Market results: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api\market_results.csv`
- Execution events: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\execution_events.ndjson`
- Trade rows usable after resolved/path filters: 95 of 95
- Exit model: same-side sell bid reconstructed as `100 - opposite ask`, with 1.0c slippage and 0.0s minimum hold.

## Baseline

- Actual API-reconciled net PnL on usable trades: -7.8300 dollars
- Actual wins/losses by row sign: 18 / 73

## OU Diagnostics

- BTC strike-gap AR(1): phi=0.99895424, half_life_steps=662.4671, pairs=7915
- Held-position MtM PnL AR(1): phi=1.00043602, half_life_steps=None, mu_cents=5.174664, sigma_cents=3.488246, pairs=7606

## Best Retrospective Real-Path Grid

- Best full-sample rule by real observed paths: PT=+29c, SL=-13c
- Counterfactual net PnL: -2.98 dollars; delta vs actual: 4.85 dollars; win rate: 0.2632; exit rate: 0.3579

## Carr-Inspired Simulated Selection

- Full-sample simulation-selected rule: PT=+39c, SL=-1c, simulated Sharpe-like=-0.132914
- Walk-forward aggregate net PnL: -10.0500 dollars
- Same slices actual net PnL: -6.6000 dollars
- Walk-forward delta vs actual: -3.4500 dollars
- Historical-grid walk-forward net PnL: -7.9900 dollars; delta vs actual: -1.3900 dollars

## Walk-Forward Parts

| Test start | Rows | Selected PT | Selected SL | Test net | Actual net | Delta |
|---|---:|---:|---:|---:|---:|---:|
| 2026-05-11T02:42:31+00:00 | 15 | 39 | 1 | -1.18 | -1.21 | 0.03 |
| 2026-05-11T05:41:47+00:00 | 15 | 39 | 1 | -2.13 | -1.39 | -0.74 |
| 2026-05-11T08:26:03+00:00 | 15 | 39 | 1 | -2.49 | 0.56 | -3.05 |
| 2026-05-11T10:47:10+00:00 | 15 | 39 | 1 | -3.87 | -4.0 | 0.13 |
| 2026-05-11T16:26:57+00:00 | 5 | 39 | 1 | -0.38 | -0.56 | 0.18 |

## Top Retrospective Nodes

| PT | SL | Net | Delta vs actual | Win rate | Exit rate | Avg hold sec |
|---:|---:|---:|---:|---:|---:|---:|
| 29 | 13 | -2.98 | 4.85 | 0.2632 | 0.3579 | 275.47 |
| 30 | 13 | -2.98 | 4.85 | 0.2632 | 0.3579 | 275.47 |
| 31 | 13 | -2.98 | 4.85 | 0.2632 | 0.3579 | 275.47 |
| 32 | 13 | -2.98 | 4.85 | 0.2632 | 0.3579 | 275.47 |
| 33 | 13 | -2.98 | 4.85 | 0.2632 | 0.3579 | 275.47 |
| 18 | 29 | -3.02 | 4.81 | 0.3474 | 0.4 | 282.4 |
| 18 | 56 | -3.03 | 4.8 | 0.4 | 0.3684 | 311.01 |
| 28 | 13 | -3.05 | 4.78 | 0.2632 | 0.3684 | 273.42 |
| 18 | 57 | -3.06 | 4.77 | 0.4 | 0.3684 | 311.02 |
| 26 | 13 | -3.08 | 4.75 | 0.2632 | 0.3684 | 272.78 |
