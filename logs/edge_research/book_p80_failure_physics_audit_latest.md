# Book P80 Failure Physics Audit

Generated UTC: `20260504_132943Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Explains the `book_p80_profit_frontier` forward-lock hypothesis rather than promoting it.
- Policy: `book_p_side>=0.80; ask<=95; sec_to_close>=120`.

## Summary

| dataset | selected/base | wins/losses | acc | break-even | acc-BE | coverage | net P&L | ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| current | 302/317 | 260/42 | 86.09% | 85.50% | 0.59% | 95.27% | 179.0c | 0.69% | 83.0c |
| v21 | 192/221 | 170/22 | 88.54% | 86.98% | 1.56% | 86.88% | 299.0c | 1.79% | 85.0c |

## Largest Win/Loss Separations

### current

| feature | win median | loss median | loss-win |
|---|---:|---:|---:|
| `seconds_to_close` | 544.330 | 622.803 | 78.473 |
| `signed_move_15m` | 14.895 | 38.090 | 23.195 |
| `signed_move_5m` | 25.370 | 45.850 | 20.480 |
| `rv_sigma_t_15m` | 54.569 | 65.170 | 10.602 |
| `margin_dollars` | 29.380 | 36.445 | 7.065 |
| `rv_sigma_t_30m` | 59.218 | 63.325 | 4.106 |
| `signed_move_3m` | 23.345 | 24.515 | 1.170 |
| `signed_move_30m` | 19.590 | 20.155 | 0.565 |
| `margin_per_rv_sigma_15m` | 0.539 | 0.571 | 0.032 |
| `brownian_p_rv_30m` | 0.681 | 0.709 | 0.028 |

### v21

| feature | win median | loss median | loss-win |
|---|---:|---:|---:|
| `seconds_to_close` | 539.216 | 419.593 | -119.623 |
| `signed_move_15m` | 57.345 | 43.015 | -14.330 |
| `signed_move_5m` | 61.175 | 47.140 | -14.035 |
| `margin_dollars` | 62.480 | 57.200 | -5.280 |
| `signed_move_3m` | 53.205 | 50.370 | -2.835 |
| `rv_sigma_t_30m` | 64.707 | 62.059 | -2.649 |
| `rv_sigma_t_15m` | 61.932 | 63.219 | 1.286 |
| `signed_move_30m` | 53.775 | 52.510 | -1.265 |
| `margin_per_rv_sigma_15m` | 0.972 | 0.937 | -0.035 |
| `brownian_p_rv_30m` | 0.817 | 0.808 | -0.010 |

## Weak-State Conditions

| dataset | condition | markets | retention | wins/losses | acc | net P&L | ROI |
|---|---|---:|---:|---:|---:|---:|---:|
| current | `ask>=85` | 114 | 37.75% | 98/16 | 85.96% | -271.0c | -2.69% |
| current | `seconds_to_close>=600` | 131 | 43.38% | 109/22 | 83.21% | -197.0c | -1.78% |
| current | `ask>=90` | 18 | 5.96% | 15/3 | 83.33% | -166.0c | -9.96% |
| current | `score_min<0.65` | 88 | 29.14% | 74/14 | 84.09% | -160.0c | -2.12% |
| current | `signed_move_30m<=-250` | 10 | 3.31% | 8/2 | 80.00% | -47.0c | -5.55% |
| current | `adverse30>=250` | 10 | 3.31% | 8/2 | 80.00% | -47.0c | -5.55% |
| current | `margin_rv15<=0.50` | 135 | 44.70% | 117/18 | 86.67% | 140.0c | 1.21% |
| current | `brownian15<0.55` | 21 | 6.95% | 20/1 | 95.24% | 190.0c | 10.50% |
| current | `margin_dollars<=25` | 126 | 41.72% | 113/13 | 89.68% | 499.0c | 4.62% |
| v21 | `ask>=85` | 99 | 51.56% | 86/13 | 86.87% | -288.0c | -3.24% |
| v21 | `ask>=90` | 38 | 19.79% | 34/4 | 89.47% | -127.0c | -3.60% |
| v21 | `seconds_to_close>=600` | 61 | 31.77% | 53/8 | 86.89% | 57.0c | 1.09% |

## Block Stability

| dataset | blocks | positive blocks | positive rate | worst block | median block |
|---|---:|---:|---:|---:|---:|
| current | 16 | 8 | 50.00% | -216.0c | -4.0c |
| v21 | 10 | 6 | 60.00% | -240.0c | 52.5c |

## Worst Losses

| dataset | market | side | ask | net | book p | brownian15 | score min | margin | signed15 | signed30 | sec |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| current | `KXBTC15M-26MAY012300-00` | yes | 95.0c | -96.0c | 0.945 | 0.709 | 0.709 | 36.40 | 90.37 | 74.67 | 453.1 |
| v21 | `KXBTC15M-26MAY012300-00` | yes | 95.0c | -96.0c | 0.945 | 0.882 | 0.882 | 81.62 | 131.36 | 135.22 | 419.2 |
| v21 | `KXBTC15M-26MAY010815-15` | no | 94.0c | -95.0c | 0.935 | 0.882 | 0.882 | 54.22 | 8.74 | -23.05 | 179.4 |
| v21 | `KXBTC15M-26MAY021000-00` | no | 92.0c | -93.0c | 0.915 | 0.900 | 0.900 | 41.60 | -12.79 | -9.45 | 419.2 |
| current | `KXBTC15M-26MAY010300-00` | no | 91.0c | -92.0c | 0.905 | 0.631 | 0.631 | 34.62 | 200.69 | 167.73 | 561.8 |
| current | `KXBTC15M-26MAY021000-00` | no | 90.0c | -91.0c | 0.895 | 0.763 | 0.763 | 21.64 | -36.38 | -12.13 | 466.2 |
| v21 | `KXBTC15M-26MAY010345-45` | yes | 90.0c | -91.0c | 0.895 | 0.906 | 0.895 | 34.14 | 52.60 | -28.79 | 179.1 |
| v21 | `KXBTC15M-26APR301630-30` | no | 89.0c | -90.0c | 0.885 | 0.763 | 0.763 | 87.56 | 64.48 | 56.17 | 779.8 |
| v21 | `KXBTC15M-26MAY011115-15` | no | 88.0c | -89.0c | 0.875 | 0.888 | 0.875 | 123.17 | 228.97 | -160.36 | 419.5 |
| v21 | `KXBTC15M-26MAY012200-00` | no | 88.0c | -89.0c | 0.875 | 0.824 | 0.824 | 29.63 | 26.74 | 27.01 | 179.1 |
| current | `KXBTC15M-26MAY012015-15` | yes | 87.0c | -88.0c | 0.865 | 0.611 | 0.611 | 18.08 | 94.63 | 190.00 | 693.6 |
| current | `KXBTC15M-26MAY030800-00` | yes | 87.0c | -88.0c | 0.865 | 0.366 | 0.366 | -36.11 | 155.08 | 147.25 | 758.6 |

## Read

- The `book_p80` edge is real historically but thin: current accuracy only clears fee-aware break-even by about half a percentage point.
- The model buys high-priced contracts, so individual losses are large and cannot be repaired with a small number of extra wins.
- Any blocker discovered here is diagnostic only. The forward lock must accumulate pre-resolution rows after its effective boundary before it can count.
