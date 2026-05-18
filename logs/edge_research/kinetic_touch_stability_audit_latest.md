# Kinetic-Touch Stability Audit

Generated UTC: `20260503_100351Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Tests the frozen kinetic-touch forward candidate without retuning it.
- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.

## Locked Policy

- Label: `choose=kinetic_touch_score_15; kinetic_touch_score_15>=0.55; 50<=ask<=95; sec>=120; gate=touch_loss15<=0.90`
- Lock close time: `2026-05-03T02:15:00+00:00`
- Lock file: `logs\edge_research\profit_kinetic_touch_fresh_lock.json`

## Split Stability

| dataset | split | markets | wins/losses | acc | breakeven | Wilson low | Wilson edge | coverage | net P&L | ROI |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| current | all | 211/213 | 147/64 | 69.67% | 66.07% | 63.16% | -0.029 | 99.06% | 759.0c | 5.44% |
| current | train | 127/127 | 87/40 | 68.50% | 65.57% | 59.98% | -0.056 | 100.00% | 373.0c | 4.48% |
| current | validation | 42/43 | 30/12 | 71.43% | 67.19% | 56.43% | -0.108 | 97.67% | 178.0c | 6.31% |
| current | holdout | 42/43 | 30/12 | 71.43% | 66.48% | 56.43% | -0.100 | 97.67% | 208.0c | 7.45% |
| v21 | all | 219/221 | 154/65 | 70.32% | 66.39% | 63.96% | -0.024 | 99.10% | 860.0c | 5.91% |
| v21 | train | 131/132 | 90/41 | 68.70% | 66.29% | 60.32% | -0.060 | 99.24% | 316.0c | 3.64% |
| v21 | validation | 44/44 | 32/12 | 72.73% | 66.18% | 58.15% | -0.080 | 100.00% | 288.0c | 9.89% |
| v21 | holdout | 44/45 | 32/12 | 72.73% | 66.91% | 58.15% | -0.088 | 97.78% | 256.0c | 8.70% |

## Fresh After Kinetic Lock

- Fresh current markets: 30/30; wins/losses 22/8; net 213.0c; ROI 10.72%; Wilson edge -0.107.

## Fragility

| dataset | mean edge | boot p05 mean | boot p95 mean | bootstrap P(mean<=0) | extra typical losses to zero | extra worst losses to zero | Wilson-edge n at observed acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| current | 3.6c | -1.7c | 8.8c | 0.128 | 12 | 10 | 679 |
| v21 | 3.9c | -1.0c | 9.0c | 0.098 | 14 | 11 | 566 |

## Weakest Regime Slices: Current

| group | markets | wins/losses | acc | breakeven | edge | net P&L | ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `time_block=block3` | 42 | 21/21 | 50.00% | 64.40% | -14.40% | -605.0c | -22.37% | 61.5c |
| `adverse15_bin=(20.0, inf]` | 48 | 30/18 | 62.50% | 69.08% | -6.58% | -316.0c | -9.53% | 68.0c |
| `ask_bin=(80.0, 90.0]` | 4 | 2/2 | 50.00% | 84.00% | -34.00% | -136.0c | -40.48% | 81.5c |
| `book_bin=(0.8, inf]` | 4 | 2/2 | 50.00% | 84.00% | -34.00% | -136.0c | -40.48% | 81.5c |
| `touch_loss_bin=(0.8, 0.85]` | 42 | 26/16 | 61.90% | 64.36% | -2.45% | -103.0c | -3.81% | 62.0c |
| `brownian_bin=(0.55, 0.6]` | 77 | 48/29 | 62.34% | 63.23% | -0.90% | -69.0c | -1.42% | 61.0c |
| `touch_loss_bin=(-inf, 0.5]` | 10 | 7/3 | 70.00% | 75.50% | -5.50% | -55.0c | -7.28% | 74.5c |
| `rv15_bin=(67.989, 92.884]` | 52 | 34/18 | 65.38% | 65.94% | -0.56% | -29.0c | -0.85% | 63.5c |
| `adverse15_bin=(0.0, 5.0]` | 7 | 4/3 | 57.14% | 61.00% | -3.86% | -27.0c | -6.32% | 58.0c |
| `kinetic_score_bin=(0.57, 0.6]` | 36 | 22/14 | 61.11% | 61.61% | -0.50% | -18.0c | -0.81% | 60.0c |
| `margin_rv15_bin=(0.0, 0.25]` | 73 | 46/27 | 63.01% | 63.14% | -0.12% | -9.0c | -0.20% | 61.0c |
| `brownian_bin=(0.8, inf]` | 1 | 1/0 | 100.00% | 86.00% | 14.00% | 14.0c | 16.28% | 85.0c |
| `book_bin=(0.6, 0.65]` | 47 | 31/16 | 65.96% | 65.28% | 0.68% | 32.0c | 1.04% | 63.0c |
| `touch_loss_bin=(0.85, 0.9]` | 35 | 22/13 | 62.86% | 61.89% | 0.97% | 34.0c | 1.57% | 60.0c |

## Weakest Regime Slices: V21

| group | markets | wins/losses | acc | breakeven | edge | net P&L | ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `ask_bin=(70.0, 80.0]` | 34 | 23/11 | 67.65% | 76.15% | -8.50% | -289.0c | -11.16% | 73.5c |
| `time_block=block1` | 44 | 27/17 | 61.36% | 66.86% | -5.50% | -242.0c | -8.23% | 63.0c |
| `book_bin=(-inf, 0.55]` | 24 | 11/13 | 45.83% | 55.38% | -9.54% | -229.0c | -17.23% | 54.0c |
| `book_bin=(0.7, 0.8]` | 31 | 22/9 | 70.97% | 76.45% | -5.48% | -170.0c | -7.17% | 74.0c |
| `kinetic_score_bin=(0.6, 0.65]` | 66 | 41/25 | 62.12% | 64.09% | -1.97% | -130.0c | -3.07% | 61.0c |
| `brownian_bin=(0.6, 0.65]` | 69 | 44/25 | 63.77% | 65.46% | -1.70% | -117.0c | -2.59% | 63.0c |
| `touch_loss_bin=(0.7, 0.8]` | 69 | 44/25 | 63.77% | 65.46% | -1.70% | -117.0c | -2.59% | 63.0c |
| `kinetic_score_bin=(0.55, 0.57]` | 36 | 22/14 | 61.11% | 62.42% | -1.31% | -47.0c | -2.09% | 60.5c |
| `rv15_bin=(112.836, 317.153]` | 55 | 37/18 | 67.27% | 67.62% | -0.35% | -19.0c | -0.51% | 65.0c |
| `seconds_bin=(240.0, 480.0]` | 6 | 4/2 | 66.67% | 66.83% | -0.17% | -1.0c | -0.25% | 66.0c |
| `ask_bin=(90.0, 95.0]` | 1 | 1/0 | 100.00% | 93.00% | 7.00% | 7.0c | 7.53% | 92.0c |
| `margin_rv15_bin=(1.5, inf]` | 1 | 1/0 | 100.00% | 93.00% | 7.00% | 7.0c | 7.53% | 92.0c |
| `margin_rv15_bin=(1.0, 1.5]` | 1 | 1/0 | 100.00% | 90.00% | 10.00% | 10.0c | 11.11% | 89.0c |
| `brownian_bin=(0.8, inf]` | 3 | 3/0 | 100.00% | 89.33% | 10.67% | 32.0c | 11.94% | 89.0c |

## Read

- Full-ledger EV is positive on current (759.0c) and v21 (860.0c).
- Current bootstrap still assigns nontrivial probability to nonpositive mean edge.
- Keep the kinetic lock unchanged and let pending markets settle; do not retune this row into its own fresh sample.
