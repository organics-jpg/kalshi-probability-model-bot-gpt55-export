# Profit Lock Sample-Size Requirements

Generated UTC: `20260505_030330Z`

## Scope

- Research-only monitor; no orders are submitted and no bot files or live processes are touched.
- Fresh EV proof requires positive net P&L, >=80% recurring-market coverage, and a Wilson lower bound above average fee-aware break-even.
- Includes separate combo price-guard and path-confirmation locks as fresh forward evidence; neither is a promotion into live trading.
- Uses registered-signal readiness rows when available; otherwise falls back to strict validator metrics, then recomputed fresh metrics.
- `extra perfect wins` assumes all future selected fresh markets win at approximately the current/fallback break-even level.
- `n at all accuracy` estimates selected fresh sample size needed if the all-ledger observed accuracy and break-even persist.

## Locks

| lock | source | overlay | fresh markets | wins/losses | acc | break-even | Wilson low | coverage | net P&L | ROI | extra perfect wins | n at all accuracy | ready |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| original | `registered_signal_readiness` | `none` | 137/200 | 92/45 | 67.15% | 66.36% | 58.91% | 68.50% | 108.0c | 1.19% | 33 | NA | False |
| frontier_v2 | `registered_signal_readiness` | `none` | 115/142 | 71/44 | 61.74% | 63.21% | 52.61% | 80.99% | -169.0c | -2.32% | 37 | NA | False |
| frontier_v2_continuous | `registered_signal_readiness` | `none` | 106/109 | 65/41 | 61.32% | 63.36% | 51.81% | 97.25% | -216.0c | -3.22% | 37 | NA | False |
| book_margin | `registered_signal_readiness` | `none` | 105/108 | 73/32 | 69.52% | 68.24% | 60.16% | 97.22% | 135.0c | 1.88% | 30 | 689 | False |
| book_margin_early | `registered_signal_readiness` | `none` | 101/104 | 70/31 | 69.31% | 68.27% | 59.74% | 97.12% | 105.0c | 1.52% | 30 | 608 | False |
| book_margin_gap015 | `registered_signal_readiness` | `none` | 89/102 | 61/28 | 68.54% | 67.31% | 58.30% | 87.25% | 109.0c | 1.82% | 27 | 334 | False |
| book_margin_adverse100 | `registered_signal_readiness` | `none` | 69/90 | 46/23 | 66.67% | 67.71% | 54.93% | 76.67% | -72.0c | -1.54% | 31 | 407 | False |
| book_margin_delayed_adv100_brownian55 | `registered_signal_readiness` | `none` | 81/85 | 55/26 | 67.90% | 71.12% | 57.12% | 95.29% | -261.0c | -4.53% | 44 | 308 | False |
| book_hour04_v2_switch | `registered_signal_readiness` | `none` | 85/87 | 52/33 | 61.18% | 64.84% | 50.55% | 97.70% | -311.0c | -5.64% | 39 | 260 | False |
| book_refmargin_score_switch | `registered_signal_readiness` | `none` | 78/84 | 55/23 | 70.51% | 71.99% | 59.62% | 92.86% | -115.0c | -2.05% | 38 | 403 | False |
| score_min60 | `registered_signal_readiness` | `none` | 102/108 | 72/30 | 70.59% | 72.39% | 61.13% | 94.44% | -184.0c | -2.49% | 46 | 403 | False |
| score_min60_gap020 | `registered_signal_readiness` | `none` | 91/97 | 64/27 | 70.33% | 72.31% | 60.28% | 93.81% | -180.0c | -2.74% | 44 | 306 | False |
| book_early_score_gap020_wait | `registered_signal_readiness` | `none` | 88/94 | 61/27 | 69.32% | 71.98% | 59.04% | 93.62% | -234.0c | -3.69% | 45 | 325 | False |
| book_score_gap020_wait | `registered_signal_readiness` | `none` | 85/91 | 58/27 | 68.24% | 71.94% | 57.73% | 93.41% | -315.0c | -5.15% | 48 | 366 | False |
| v2_wait_score_min60_early | `registered_signal_readiness` | `none` | 101/107 | 71/30 | 70.30% | 72.23% | 60.77% | 94.39% | -195.0c | -2.67% | 46 | 322 | False |
| v2_wait_score_min60_brownian70_early | `registered_signal_readiness` | `none` | 97/103 | 69/28 | 71.13% | 72.24% | 61.45% | 94.17% | -107.0c | -1.53% | 41 | 285 | False |
| challenger | `registered_signal_readiness` | `ask>=50 AND ask<=80` | 128/199 | 87/41 | 67.97% | 66.86% | 59.46% | 64.32% | 142.0c | 1.66% | 31 | 16365 | False |
| touch_hazard | `registered_signal_readiness` | `none` | 146/196 | 87/59 | 59.59% | 60.26% | 51.48% | 74.49% | -98.0c | -1.11% | 35 | NA | False |
| touch_overlay | `registered_signal_readiness` | `ask>=50 AND touch_loss15>=0.80` | 138/189 | 84/54 | 60.87% | 60.01% | 52.54% | 73.02% | 119.0c | 1.44% | 28 | 11494 | False |
| kinetic_touch | `registered_signal_readiness` | `none` | 134/187 | 89/45 | 66.42% | 68.54% | 58.06% | 71.66% | -285.0c | -3.10% | 49 | 8500 | False |
| hazard_mean_touch80 | `registered_signal_readiness` | `none` | 69/79 | 50/19 | 72.46% | 72.58% | 60.95% | 87.34% | -8.0c | -0.16% | 33 | 584 | False |
| logit_blend_edge10 | `registered_signal_readiness` | `none` | 75/78 | 48/27 | 64.00% | 62.25% | 52.70% | 96.15% | 131.0c | 2.81% | 22 | NA | False |
| logit_blend_thresh55_edge15 | `registered_signal_readiness` | `none` | 69/76 | 49/20 | 71.01% | 71.64% | 59.43% | 90.79% | -43.0c | -0.87% | 33 | 486 | False |
| hazard_fallback_logit55 | `registered_signal_readiness` | `none` | 68/75 | 48/20 | 70.59% | 71.62% | 58.89% | 90.67% | -70.0c | -1.44% | 34 | 534 | False |
| hazard_fallback_logit55_wait8 | `registered_signal_readiness` | `none` | 61/71 | 42/19 | 68.85% | 72.59% | 56.41% | 85.92% | -228.0c | -5.15% | 41 | 544 | False |
| hazard_fallback_score60 | `registered_signal_readiness` | `none` | 64/70 | 46/18 | 71.88% | 72.12% | 59.87% | 91.43% | -16.0c | -0.35% | 32 | 410 | False |
| impulse_reversal_book_margin_fade | `registered_signal_readiness` | `none` | 58/61 | 33/25 | 56.90% | 55.47% | 44.12% | 95.08% | 83.0c | 2.58% | 18 | 4503 | False |
| kinetic_guard | `registered_signal_readiness` | `kinetic>=0.57 AND adverse15<=50` | 126/186 | 89/37 | 70.63% | 70.06% | 62.17% | 67.74% | 72.0c | 0.82% | 36 | 2223 | False |
| kinetic_price_guard | `registered_signal_readiness` | `adverse15<=100 AND ask<=70` | 107/185 | 69/38 | 64.49% | 64.38% | 55.06% | 57.84% | 11.0c | 0.16% | 31 | 1589 | False |
| kinetic_combo_price_guard | `registered_signal_readiness` | `kinetic>=0.57 AND adverse15<=100 AND ask<=70` | 100/158 | 67/33 | 67.00% | 65.08% | 57.31% | 63.29% | 192.0c | 2.95% | 25 | 933 | False |
| kinetic_path_confirm | `registered_signal_readiness` | `same_side_for>=60s AND confirm_score>=0.6` | 118/180 | 89/29 | 75.42% | 75.48% | 66.94% | 65.56% | -7.0c | -0.08% | 45 | 205 | False |
| book_p80_ask90_frontier | `registered_signal_readiness` | `none` | 40/51 | 34/6 | 85.00% | 84.80% | 70.93% | 78.43% | 8.0c | 0.24% | 42 | NA | False |
| book_p80_profit_frontier | `registered_signal_readiness` | `none` | 41/52 | 34/7 | 82.93% | 85.02% | 68.74% | 78.85% | -86.0c | -2.47% | 51 | NA | False |
| hazard_mean_touch80_ask76 | `registered_signal_readiness` | `none` | 53/65 | 37/16 | 69.81% | 71.89% | 56.46% | 81.54% | -110.0c | -2.89% | 33 | NA | False |

## Read

- No lock meets the fresh EV sample-size gate yet.
- original: needs 33 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- frontier_v2: needs 37 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- frontier_v2_continuous: needs 37 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- book_margin: needs 30 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- book_margin_early: needs 30 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- book_margin_gap015: needs 27 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- book_margin_adverse100: needs 31 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- book_margin_delayed_adv100_brownian55: needs 44 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- book_hour04_v2_switch: needs 39 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- book_refmargin_score_switch: needs 38 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- score_min60: needs 46 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- score_min60_gap020: needs 44 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- book_early_score_gap020_wait: needs 45 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- book_score_gap020_wait: needs 48 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- v2_wait_score_min60_early: needs 46 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- v2_wait_score_min60_brownian70_early: needs 41 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- challenger: needs 31 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- touch_hazard: needs 35 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- touch_overlay: needs 28 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- kinetic_touch: needs 49 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- hazard_mean_touch80: needs 33 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- logit_blend_edge10: needs 22 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- logit_blend_thresh55_edge15: needs 33 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- hazard_fallback_logit55: needs 34 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- hazard_fallback_logit55_wait8: needs 41 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- hazard_fallback_score60: needs 32 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- impulse_reversal_book_margin_fade: needs 18 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- kinetic_guard: needs 36 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- kinetic_price_guard: needs 31 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- kinetic_combo_price_guard: needs 25 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- kinetic_path_confirm: needs 45 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- book_p80_ask90_frontier: needs 42 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- book_p80_profit_frontier: needs 51 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
- hazard_mean_touch80_ask76: needs 33 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state.
