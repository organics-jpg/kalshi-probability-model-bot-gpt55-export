# v28 Book-Disagreement Trajectory FV

Research-only FV diagnostics using raw/book gap and same-side book trajectory.

- Surface: `all_settled_v28_approved_and_rejected_observations`
- Rows/markets/market-sides: `21031/176/350`

## Current Read

- View approved_only best variant is gap15_or_drawdown10 with Brier/logloss deltas -0.009376900694792453/-0.06120296241970963.
- View first_per_market_side best variant is book_probability with Brier/logloss deltas -0.015092992568571412/-0.05257090757616956.
- View last_per_market_side best variant is book_probability with Brier/logloss deltas -0.02403667592009142/-0.12451779896646292.
- View all_observations best variant is book_probability with Brier/logloss deltas -0.007492661082343172/-0.02034393845703447.
- Repeated observation views are diagnostic only; first/last per market-side are less autocorrelated.

## View: approved_only

- Rows: `222`

| rank | variant | rows | W/L | avg p | win rate | cal err | brier d | logloss d |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `gap15_or_drawdown10` | 222 | 190/32 | 0.873127 | 0.855856 | -0.017271 | -0.009377 | -0.061203 |
| 2 | `gap15_half_book` | 222 | 190/32 | 0.876970 | 0.855856 | -0.021114 | -0.008531 | -0.059469 |
| 3 | `gap20_half_book` | 222 | 190/32 | 0.881098 | 0.855856 | -0.025243 | -0.007566 | -0.056247 |
| 4 | `book_probability` | 222 | 190/32 | 0.792432 | 0.855856 | 0.063423 | -0.005342 | -0.042946 |
| 5 | `gap15_and_drawdown10_only` | 222 | 190/32 | 0.892940 | 0.855856 | -0.037084 | -0.002713 | -0.012361 |
| 6 | `book_drawdown10_heavy_book` | 222 | 190/32 | 0.892669 | 0.855856 | -0.036813 | -0.002436 | -0.011474 |
| 7 | `raw_probability` | 222 | 190/32 | 0.894559 | 0.855856 | -0.038704 | 0.000000 | 0.000000 |

## View: first_per_market_side

- Rows: `350`

| rank | variant | rows | W/L | avg p | win rate | cal err | brier d | logloss d |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `book_probability` | 350 | 176/174 | 0.507914 | 0.502857 | -0.005057 | -0.015093 | -0.052571 |
| 2 | `gap15_or_drawdown10` | 350 | 176/174 | 0.496640 | 0.502857 | 0.006217 | -0.004933 | -0.020705 |
| 3 | `gap15_half_book` | 350 | 176/174 | 0.497556 | 0.502857 | 0.005301 | -0.004303 | -0.019437 |
| 4 | `gap20_half_book` | 350 | 176/174 | 0.498994 | 0.502857 | 0.003863 | -0.003328 | -0.017473 |
| 5 | `raw_probability` | 350 | 176/174 | 0.502134 | 0.502857 | 0.000724 | 0.000000 | 0.000000 |
| 6 | `book_drawdown10_heavy_book` | 350 | 176/174 | 0.502134 | 0.502857 | 0.000724 | 0.000000 | 0.000000 |
| 7 | `gap15_and_drawdown10_only` | 350 | 176/174 | 0.502134 | 0.502857 | 0.000724 | 0.000000 | 0.000000 |

## View: last_per_market_side

- Rows: `350`

| rank | variant | rows | W/L | avg p | win rate | cal err | brier d | logloss d |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `book_probability` | 350 | 176/174 | 0.519886 | 0.502857 | -0.017028 | -0.024037 | -0.124518 |
| 2 | `gap15_or_drawdown10` | 350 | 176/174 | 0.508290 | 0.502857 | -0.005433 | -0.010487 | -0.055005 |
| 3 | `gap15_half_book` | 350 | 176/174 | 0.509877 | 0.502857 | -0.007020 | -0.009266 | -0.052224 |
| 4 | `gap20_half_book` | 350 | 176/174 | 0.510405 | 0.502857 | -0.007548 | -0.009119 | -0.051611 |
| 5 | `gap15_and_drawdown10_only` | 350 | 176/174 | 0.516295 | 0.502857 | -0.013438 | -0.002520 | -0.006697 |
| 6 | `book_drawdown10_heavy_book` | 350 | 176/174 | 0.516583 | 0.502857 | -0.013726 | -0.002464 | -0.006410 |
| 7 | `raw_probability` | 350 | 176/174 | 0.518435 | 0.502857 | -0.015578 | 0.000000 | 0.000000 |

## View: all_observations

- Rows: `21031`

| rank | variant | rows | W/L | avg p | win rate | cal err | brier d | logloss d |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `book_probability` | 21031 | 11438/9593 | 0.545613 | 0.543864 | -0.001749 | -0.007493 | -0.020344 |
| 2 | `gap15_or_drawdown10` | 21031 | 11438/9593 | 0.538101 | 0.543864 | 0.005763 | -0.002221 | -0.006255 |
| 3 | `gap15_half_book` | 21031 | 11438/9593 | 0.539244 | 0.543864 | 0.004620 | -0.001877 | -0.005450 |
| 4 | `gap20_half_book` | 21031 | 11438/9593 | 0.540636 | 0.543864 | 0.003227 | -0.001525 | -0.004568 |
| 5 | `book_drawdown10_heavy_book` | 21031 | 11438/9593 | 0.541459 | 0.543864 | 0.002405 | -0.000779 | -0.001901 |
| 6 | `gap15_and_drawdown10_only` | 21031 | 11438/9593 | 0.541776 | 0.543864 | 0.002088 | -0.000700 | -0.001725 |
| 7 | `raw_probability` | 21031 | 11438/9593 | 0.543192 | 0.543864 | 0.000672 | 0.000000 | 0.000000 |

## Trigger Buckets

| bucket | rows | W/L | best variant | best brier d |
|---|---:|---:|---|---:|
| `gap_gt_15pp` | 707 | 209/498 | `book_probability` | -0.078661 |
| `same_side_book_down_gt_10pp` | 771 | 270/501 | `book_probability` | -0.024750 |
| `gap_gt15_and_book_down_gt10` | 164 | 41/123 | `book_probability` | -0.102545 |
