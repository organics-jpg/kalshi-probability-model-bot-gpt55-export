# Profit Lock Registered-Signal Readiness

Generated UTC: `20260505_032034Z`

## Scope

- Research-only monitor; no orders are submitted and no bot files or live processes are touched.
- Uses pre-registered first signals captured before outcomes were known.
- This is stricter promotion evidence than recomputing first eligible rows from a later log snapshot.

## Registered Signal State

| lock | overlay | registered/resolved/pending | wins/losses | acc | break-even | Wilson low | P(p>BE) | p05 edge | resolved coverage | registered coverage | net P&L | ROI | Bayes extra wins | Wilson ready | Bayes ready |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| original | `none` | 138/138/0 | 92/46 | 66.67% | 66.35% | 58.44% | 0.516 | -6.6c | 68.66% | 67.65% | 44.0c | 0.48% | 29 | False | False |
| frontier_v2 | `none` | 116/116/0 | 72/44 | 62.07% | 63.19% | 52.99% | 0.390 | -8.8c | 81.12% | 80.00% | -130.0c | -1.77% | 30 | False | False |
| frontier_v2_continuous | `none` | 107/107/0 | 66/41 | 61.68% | 63.34% | 52.22% | 0.350 | -9.7c | 97.27% | 95.54% | -177.0c | -2.61% | 31 | False | False |
| book_margin | `none` | 106/106/0 | 73/33 | 68.87% | 68.20% | 59.52% | 0.540 | -7.2c | 97.25% | 95.50% | 71.0c | 0.98% | 26 | False | False |
| book_margin_early | `none` | 102/102/0 | 70/32 | 68.63% | 68.23% | 59.09% | 0.513 | -7.6c | 97.14% | 95.33% | 41.0c | 0.59% | 27 | False | False |
| book_margin_gap015 | `none` | 90/90/0 | 61/29 | 67.78% | 67.28% | 57.57% | 0.520 | -8.0c | 87.38% | 85.71% | 45.0c | 0.74% | 25 | False | False |
| book_margin_adverse100 | `none` | 70/70/0 | 46/24 | 65.71% | 67.66% | 54.04% | 0.344 | -11.8c | 76.92% | 75.27% | -136.0c | -2.87% | 29 | False | False |
| book_margin_delayed_adv100_brownian55 | `none` | 82/82/0 | 55/27 | 67.07% | 71.04% | 56.34% | 0.200 | -13.1c | 95.35% | 93.18% | -325.0c | -5.58% | 41 | False | False |
| book_hour04_v2_switch | `none` | 86/86/0 | 52/34 | 60.47% | 64.83% | 49.90% | 0.190 | -13.3c | 97.73% | 95.56% | -375.0c | -6.73% | 36 | False | False |
| book_refmargin_score_switch | `none` | 79/79/0 | 55/24 | 69.62% | 71.89% | 58.77% | 0.303 | -11.4c | 92.94% | 90.80% | -179.0c | -3.15% | 35 | False | False |
| score_min60 | `none` | 103/103/0 | 72/31 | 69.90% | 72.31% | 60.46% | 0.275 | -10.3c | 94.50% | 92.79% | -248.0c | -3.33% | 42 | False | False |
| score_min60_gap020 | `none` | 92/92/0 | 64/28 | 69.57% | 72.22% | 59.54% | 0.265 | -11.1c | 93.88% | 92.00% | -244.0c | -3.67% | 40 | False | False |
| book_early_score_gap020_wait | `none` | 89/89/0 | 61/28 | 68.54% | 71.89% | 58.30% | 0.224 | -12.0c | 93.68% | 91.75% | -298.0c | -4.66% | 42 | False | False |
| book_score_gap020_wait | `none` | 86/86/0 | 58/28 | 67.44% | 71.85% | 56.98% | 0.168 | -13.2c | 93.48% | 91.49% | -379.0c | -6.13% | 44 | False | False |
| v2_wait_score_min60_early | `none` | 102/102/0 | 71/31 | 69.61% | 72.15% | 60.10% | 0.265 | -10.5c | 94.44% | 92.73% | -259.0c | -3.52% | 42 | False | False |
| v2_wait_score_min60_brownian70_early | `none` | 98/98/0 | 69/29 | 70.41% | 72.15% | 60.74% | 0.327 | -9.9c | 94.23% | 92.45% | -171.0c | -2.42% | 38 | False | False |
| challenger | `ask>=50 AND ask<=80` | 129/129/0 | 87/42 | 67.44% | 66.84% | 58.95% | 0.542 | -6.5c | 64.50% | 63.55% | 78.0c | 0.90% | 27 | False | False |
| touch_hazard | `none` | 147/147/0 | 88/59 | 59.86% | 60.27% | 51.79% | 0.452 | -7.2c | 74.62% | 73.50% | -59.0c | -0.67% | 29 | False | False |
| touch_overlay | `ask>=50 AND touch_loss15>=0.80` | 139/139/0 | 85/54 | 61.15% | 60.01% | 52.85% | 0.599 | -5.8c | 73.16% | 72.02% | 158.0c | 1.89% | 22 | False | False |
| kinetic_touch | `none` | 135/135/0 | 89/46 | 65.93% | 68.51% | 57.59% | 0.247 | -9.5c | 71.81% | 71.05% | -349.0c | -3.77% | 44 | False | False |
| hazard_mean_touch80 | `none` | 70/70/0 | 50/20 | 71.43% | 72.46% | 59.95% | 0.394 | -10.7c | 87.50% | 85.37% | -72.0c | -1.42% | 30 | False | False |
| logit_blend_edge10 | `none` | 76/76/0 | 49/27 | 64.47% | 62.13% | 53.26% | 0.649 | -7.1c | 96.20% | 93.83% | 178.0c | 3.77% | 16 | False | False |
| logit_blend_thresh55_edge15 | `none` | 70/70/0 | 49/21 | 70.00% | 71.53% | 58.46% | 0.362 | -11.3c | 90.91% | 88.61% | -107.0c | -2.14% | 31 | False | False |
| hazard_fallback_logit55 | `none` | 69/69/0 | 48/21 | 69.57% | 71.51% | 57.92% | 0.334 | -11.7c | 90.79% | 88.46% | -134.0c | -2.72% | 32 | False | False |
| hazard_fallback_logit55_wait8 | `none` | 62/62/0 | 42/20 | 67.74% | 72.45% | 55.37% | 0.186 | -15.1c | 86.11% | 83.78% | -292.0c | -6.50% | 38 | False | False |
| hazard_fallback_score60 | `none` | 65/65/0 | 46/19 | 70.77% | 72.00% | 58.80% | 0.384 | -11.3c | 91.55% | 89.04% | -80.0c | -1.71% | 29 | False | False |
| impulse_reversal_book_margin_fade | `none` | 59/59/0 | 33/26 | 55.93% | 55.61% | 43.29% | 0.513 | -10.4c | 95.16% | 92.19% | 19.0c | 0.58% | 16 | False | False |
| kinetic_guard | `kinetic>=0.57 AND adverse15<=50` | 127/127/0 | 89/38 | 70.08% | 70.02% | 61.62% | 0.485 | -7.0c | 67.91% | 67.20% | 8.0c | 0.09% | 32 | False | False |
| kinetic_price_guard | `adverse15<=100 AND ask<=70` | 108/108/0 | 69/39 | 63.89% | 64.38% | 54.50% | 0.443 | -8.4c | 58.06% | 57.45% | -53.0c | -0.76% | 28 | False | False |
| kinetic_combo_price_guard | `kinetic>=0.57 AND adverse15<=100 AND ask<=70` | 101/101/0 | 67/34 | 66.34% | 65.07% | 56.67% | 0.588 | -6.8c | 63.52% | 62.73% | 128.0c | 1.95% | 22 | False | False |
| kinetic_path_confirm | `same_side_for>=60s AND confirm_score>=0.6` | 119/119/0 | 89/30 | 74.79% | 75.50% | 66.30% | 0.402 | -7.8c | 65.75% | 65.03% | -85.0c | -0.95% | 41 | False | False |
| book_p80_ask90_frontier | `none` | 41/41/0 | 34/7 | 82.93% | 84.76% | 68.74% | 0.305 | -13.8c | 78.85% | 77.36% | -75.0c | -2.16% | 42 | False | False |
| book_p80_profit_frontier | `none` | 42/42/0 | 34/8 | 80.95% | 84.98% | 66.70% | 0.188 | -16.0c | 79.25% | 77.78% | -169.0c | -4.74% | 50 | False | False |
| hazard_mean_touch80_ask76 | `none` | 54/54/0 | 37/17 | 68.52% | 71.74% | 55.26% | 0.273 | -14.5c | 81.82% | 79.41% | -174.0c | -4.49% | 31 | False | False |

## Read

- No lock clears the registered-signal Wilson gate yet.
- No lock clears the registered-signal Bayesian gate yet.
