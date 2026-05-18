# Locked Profit Candidate Stability Audit

Generated UTC: `20260502_213621Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Tests the locked profit candidate without retuning it after later refreshed markets.
- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.
- Selection uses only pre-entry fields in the lock: Brownian RV15 probability, ask, seconds-to-close, 15m adverse move, and RV-normalized margin.

## Locked Policy

- Label: `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.55; ask<=95; sec_to_close>=120; adverse15<=10_or_margin_rv15>=0.5`
- Lock close time: `2026-05-02T20:30:00+00:00`
- Lock file: `logs\edge_research\profit_frontier_fresh_lock.json`

## Split Stability

| dataset | split | markets | wins/losses | acc | breakeven | Wilson low | Wilson edge | coverage | net P&L | ROI |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| current | all | 167/169 | 111/56 | 66.47% | 64.07% | 59.01% | -0.051 | 98.82% | 400.0c | 3.74% |
| current | train | 100/101 | 63/37 | 63.00% | 63.95% | 53.22% | -0.107 | 99.01% | -95.0c | -1.49% |
| current | validation | 34/34 | 25/9 | 73.53% | 63.65% | 56.88% | -0.068 | 100.00% | 336.0c | 15.53% |
| current | holdout | 33/34 | 23/10 | 69.70% | 64.88% | 52.66% | -0.122 | 97.06% | 159.0c | 7.43% |
| v21 | all | 219/221 | 154/65 | 70.32% | 64.87% | 63.96% | -0.009 | 99.10% | 1194.0c | 8.40% |
| v21 | train | 131/132 | 88/43 | 67.18% | 64.99% | 58.75% | -0.062 | 99.24% | 286.0c | 3.36% |
| v21 | validation | 44/44 | 32/12 | 72.73% | 63.86% | 58.15% | -0.057 | 100.00% | 390.0c | 13.88% |
| v21 | holdout | 44/45 | 34/10 | 77.27% | 65.50% | 63.01% | -0.025 | 97.78% | 518.0c | 17.97% |

## Fresh After Lock

- Fresh current markets: 3/3; wins/losses 2/1; net 16.0c; ROI 8.70%; Wilson edge -0.406.
- Fresh extra typical losses to wipe current fresh P&L: 1.

## Fragility

| dataset | mean edge | boot p05 mean | boot p95 mean | bootstrap P(mean<=0) | extra typical losses to zero | extra worst losses to zero | Wilson-edge n at observed acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| current | 2.4c | -3.6c | 8.2c | 0.249 | 7 | 5 | 1562 |
| v21 | 5.5c | 0.5c | 10.3c | 0.035 | 21 | 14 | 303 |

## Weakest Regime Slices: Current

| group | markets | wins/losses | acc | breakeven | edge | net P&L | ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `rv15_bin=(49.549, 71.476]` | 42 | 24/18 | 57.14% | 64.29% | -7.14% | -300.0c | -11.11% | 62.0c |
| `time_block=block1` | 34 | 19/15 | 55.88% | 64.47% | -8.59% | -292.0c | -13.32% | 59.5c |
| `adverse15_bin=(20.0, inf]` | 13 | 8/5 | 61.54% | 78.08% | -16.54% | -215.0c | -21.18% | 78.0c |
| `ask_bin=(70.0, 80.0]` | 27 | 19/8 | 70.37% | 77.41% | -7.04% | -190.0c | -9.09% | 75.0c |
| `margin_rv15_bin=(0.25, 0.5]` | 67 | 41/26 | 61.19% | 63.01% | -1.82% | -122.0c | -2.89% | 61.0c |
| `split=train` | 100 | 63/37 | 63.00% | 63.95% | -0.95% | -95.0c | -1.49% | 62.0c |
| `adverse15_bin=(10.0, 20.0]` | 5 | 3/2 | 60.00% | 78.80% | -18.80% | -94.0c | -23.86% | 76.0c |
| `brownian_bin=(0.65, 0.7]` | 34 | 22/12 | 64.71% | 67.06% | -2.35% | -80.0c | -3.51% | 65.5c |
| `seconds_bin=(480.0, 720.0]` | 28 | 19/9 | 67.86% | 70.32% | -2.46% | -69.0c | -3.50% | 68.5c |
| `ask_bin=(-inf, 50.0]` | 14 | 6/8 | 42.86% | 47.50% | -4.64% | -65.0c | -9.77% | 47.5c |
| `brownian_bin=(0.6, 0.65]` | 38 | 23/15 | 60.53% | 61.87% | -1.34% | -51.0c | -2.17% | 61.0c |
| `side=no` | 86 | 55/31 | 63.95% | 64.35% | -0.40% | -34.0c | -0.61% | 60.0c |

## Weakest Regime Slices: V21

| group | markets | wins/losses | acc | breakeven | edge | net P&L | ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `time_block=block1` | 44 | 27/17 | 61.36% | 64.00% | -2.64% | -116.0c | -4.12% | 60.5c |
| `margin_rv15_bin=(0.25, 0.5]` | 85 | 53/32 | 62.35% | 63.20% | -0.85% | -72.0c | -1.34% | 62.0c |
| `ask_bin=(-inf, 50.0]` | 18 | 8/10 | 44.44% | 46.61% | -2.17% | -39.0c | -4.65% | 45.5c |
| `adverse15_bin=(20.0, inf]` | 17 | 13/4 | 76.47% | 78.41% | -1.94% | -33.0c | -2.48% | 77.0c |
| `rv15_bin=(109.368, 299.797]` | 55 | 36/19 | 65.45% | 65.47% | -0.02% | -1.0c | -0.03% | 61.0c |
| `rv15_bin=(61.763, 83.169]` | 55 | 36/19 | 65.45% | 65.45% | -0.00% | 0.0c | 0.00% | 62.0c |
| `margin_rv15_bin=(1.5, inf]` | 1 | 1/0 | 100.00% | 93.00% | 7.00% | 7.0c | 7.53% | 92.0c |
| `margin_rv15_bin=(1.0, 1.5]` | 1 | 1/0 | 100.00% | 90.00% | 10.00% | 10.0c | 11.11% | 89.0c |
| `ask_bin=(90.0, 95.0]` | 2 | 2/0 | 100.00% | 93.50% | 6.50% | 13.0c | 6.95% | 92.5c |
| `brownian_bin=(0.6, 0.65]` | 56 | 35/21 | 62.50% | 62.00% | 0.50% | 28.0c | 0.81% | 62.0c |
| `brownian_bin=(0.8, inf]` | 4 | 4/0 | 100.00% | 90.50% | 9.50% | 38.0c | 10.50% | 90.5c |
| `ask_bin=(80.0, 90.0]` | 12 | 11/1 | 91.67% | 85.25% | 6.42% | 77.0c | 7.53% | 84.0c |

## Read

- The locked candidate remains net-positive on both full datasets after the latest refresh.
- Current train split is negative, so the edge is not uniformly stable inside the current capture.
- Fresh post-lock sample is too small for promotion-quality EV evidence.
- Keep the lock unchanged and let fresh evidence accumulate; retuning to the refreshed top row would contaminate forward validation.
