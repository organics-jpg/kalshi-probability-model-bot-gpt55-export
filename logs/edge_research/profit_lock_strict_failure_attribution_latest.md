# Profit Lock Strict Failure Attribution

Generated UTC: `20260505_031109Z`

## Scope

- Research-only attribution; no orders are submitted and no bot files or live processes are touched.
- Uses only clean rows registered before market close and already resolved.
- Blocker rows are diagnostic only; they are not promotion evidence and do not update locks.

- Strict resolved rows: 3125

## Lock Summary

| lock | resolved | wins/losses | acc | net P&L | median ask | median score | median adverse15 |
|---|---:|---:|---:|---:|---:|---:|---:|
| book_early_score_gap020_wait | 88 | 61/27 | 69.32% | -234.0c | 69.0c | 0.6692708152488291 | 0.0c |
| book_hour04_v2_switch | 85 | 52/33 | 61.18% | -311.0c | 63.0c | 0.5711670574985338 | 0.0c |
| book_margin | 105 | 73/32 | 69.52% | 135.0c | 64.0c | 0.5874679998840884 | 0.0c |
| book_margin_adverse100 | 69 | 46/23 | 66.67% | -72.0c | 64.0c | 0.6042047917758214 | 0.0c |
| book_margin_delayed_adv100_brownian55 | 81 | 55/26 | 67.90% | -261.0c | 67.0c | 0.6418112458936883 | 0.0c |
| book_margin_early | 101 | 70/31 | 69.31% | 105.0c | 64.0c | 0.5864780457304634 | 0.0c |
| book_margin_gap015 | 89 | 61/28 | 68.54% | 109.0c | 64.0c | 0.577831203801631 | 0.0c |
| book_p80_ask90_frontier | 40 | 34/6 | 85.00% | 8.0c | 83.0c | 0.7679908752753111 | 0.0c |
| book_p80_profit_frontier | 41 | 34/7 | 82.93% | -86.0c | 83.0c | 0.7614973541267611 | 0.0c |
| book_refmargin_score_switch | 78 | 55/23 | 70.51% | -115.0c | 69.0c | 0.6692708152488291 | 0.0c |
| book_score_gap020_wait | 85 | 58/27 | 68.24% | -315.0c | 69.0c | 0.6678707785004474 | 0.0c |
| challenger | 128 | 87/41 | 67.97% | 142.0c | 64.5c | 0.6380287163443678 | 0.0c |
| frontier_v2 | 115 | 71/44 | 61.74% | -169.0c | 61.0c | 0.5859108516083694 | 0.0c |
| frontier_v2_continuous | 106 | 65/41 | 61.32% | -216.0c | 61.0c | 0.5914477145782551 | 0.0c |
| hazard_fallback_logit55 | 68 | 48/20 | 70.59% | -70.0c | 68.0c | 0.6539535189887775 | 0.0c |
| hazard_fallback_logit55_wait8 | 61 | 42/19 | 68.85% | -228.0c | 71.0c | 0.6847975942998622 | 0.0c |
| hazard_fallback_score60 | 64 | 46/18 | 71.88% | -16.0c | 69.0c | 0.6693283735914286 | 0.0c |
| hazard_mean_touch80 | 69 | 50/19 | 72.46% | -8.0c | 71.0c | 0.680627813963736 | 0.0c |
| hazard_mean_touch80_ask76 | 53 | 37/16 | 69.81% | -110.0c | 70.0c | 0.6745064658999467 | 0.0c |
| impulse_reversal_book_margin_fade | 58 | 33/25 | 56.90% | 83.0c | 62.0c | 0.4781823210798517 | 4.7c |
| kinetic_combo_price_guard | 100 | 67/33 | 67.00% | 192.0c | 63.0c | 0.6289990509896811 | 0.0c |
| kinetic_guard | 126 | 89/37 | 70.63% | 72.0c | 67.5c | 0.6455554209488715 | 0.0c |
| kinetic_path_confirm | 118 | 89/29 | 75.42% | -7.0c | 74.0c | 0.7065614988451816 | 0.0c |
| kinetic_price_guard | 107 | 69/38 | 64.49% | 11.0c | 62.0c | 0.6144818703325239 | 0.0c |
| kinetic_touch | 134 | 89/45 | 66.42% | -285.0c | 66.0c | 0.6243513380620765 | 0.0c |
| logit_blend_edge10 | 75 | 48/27 | 64.00% | 131.0c | 56.0c | 0.5748180747594641 | 0.0c |
| logit_blend_thresh55_edge15 | 69 | 49/20 | 71.01% | -43.0c | 68.0c | 0.6538130567402669 | 0.0c |
| original | 137 | 92/45 | 67.15% | 108.0c | 64.0c | 0.6320598429571216 | 0.0c |
| score_min60 | 102 | 72/30 | 70.59% | -184.0c | 69.0c | 0.6775671399318413 | 0.0c |
| score_min60_gap020 | 91 | 64/27 | 70.33% | -180.0c | 69.0c | 0.6707859686824099 | 0.0c |
| touch_hazard | 146 | 87/59 | 59.59% | -98.0c | 56.0c | 0.49854478529599544 | 2.0c |
| touch_overlay | 138 | 84/54 | 60.87% | 119.0c | 56.0c | 0.4913019103153501 | 4.5c |
| v2_wait_score_min60_brownian70_early | 97 | 69/28 | 71.13% | -107.0c | 69.0c | 0.6713269063290632 | 0.0c |
| v2_wait_score_min60_early | 101 | 71/30 | 70.30% | -195.0c | 69.0c | 0.6713269063290632 | 0.0c |

## Largest Win/Loss Feature Separations

| lock | feature | win median | loss median | loss-win |
|---|---|---:|---:|---:|
| book_p80_ask90_frontier | `signed_move_30m` | 96.455 | -57.780 | -154.235 |
| book_p80_profit_frontier | `signed_move_30m` | 89.375 | -38.630 | -128.005 |
| frontier_v2 | `signed_move_30m` | 70.060 | -34.820 | -104.880 |
| frontier_v2_continuous | `signed_move_30m` | 70.060 | -34.820 | -104.880 |
| touch_hazard | `signed_move_30m` | 8.580 | -81.400 | -89.980 |
| touch_overlay | `signed_move_15m` | 24.860 | -45.975 | -70.835 |
| kinetic_touch | `signed_move_30m` | 71.890 | 132.370 | 60.480 |
| book_margin_gap015 | `signed_move_30m` | 67.640 | 124.945 | 57.305 |
| challenger | `signed_move_30m` | 110.910 | 168.200 | 57.290 |
| logit_blend_edge10 | `signed_move_15m` | 65.920 | 9.135 | -56.785 |
| book_margin | `signed_move_30m` | 63.150 | 119.160 | 56.010 |
| book_margin_early | `signed_move_30m` | 63.150 | 119.160 | 56.010 |
| original | `seconds_to_close` | 779.079 | 834.833 | 55.754 |
| book_p80_profit_frontier | `seconds_to_close` | 662.485 | 607.230 | -55.255 |
| kinetic_guard | `seconds_to_close` | 775.095 | 827.732 | 52.637 |
| impulse_reversal_book_margin_fade | `signed_move_5m` | 5.800 | -46.530 | -52.330 |
| book_early_score_gap020_wait | `seconds_to_close` | 718.343 | 770.481 | 52.138 |
| book_refmargin_score_switch | `seconds_to_close` | 718.343 | 770.481 | 52.138 |
| book_score_gap020_wait | `seconds_to_close` | 718.369 | 770.481 | 52.112 |
| score_min60_gap020 | `seconds_to_close` | 718.369 | 770.481 | 52.112 |
| hazard_mean_touch80_ask76 | `signed_move_30m` | 69.675 | 119.160 | 49.485 |
| touch_hazard | `signed_move_15m` | 22.910 | -25.040 | -47.950 |
| original | `signed_move_30m` | 113.340 | 161.150 | 47.810 |
| book_hour04_v2_switch | `signed_move_30m` | 70.060 | 117.195 | 47.135 |
| kinetic_touch | `signed_move_15m` | 90.805 | 46.475 | -44.330 |

## Top Diagnostic Blockers

| lock | rule | kept/base | retention | wins/losses | acc | net P&L | delta vs base |
|---|---|---:|---:|---:|---:|---:|---:|
| book_margin_gap015 | `blend>=0.50` | 57/89 | 64.04% | 44/13 | 77.19% | 532.0c | 423.0c |
| book_margin | `touch_loss<=0.95` | 82/105 | 78.10% | 61/21 | 74.39% | 505.0c | 370.0c |
| book_margin_early | `touch_loss<=0.95` | 80/101 | 79.21% | 59/21 | 73.75% | 441.0c | 336.0c |
| impulse_reversal_book_margin_fade | `blend>=0.50` | 28/58 | 48.28% | 23/5 | 82.14% | 429.0c | 346.0c |
| impulse_reversal_book_margin_fade | `touch_loss<=0.95` | 30/58 | 51.72% | 24/6 | 80.00% | 415.0c | 332.0c |
| kinetic_combo_price_guard | `blend>=0.45` | 60/100 | 60.00% | 43/17 | 71.67% | 408.0c | 216.0c |
| book_margin_early | `blend>=0.50` | 63/101 | 62.38% | 47/16 | 74.60% | 382.0c | 277.0c |
| book_margin | `blend>=0.50` | 63/105 | 60.00% | 47/16 | 74.60% | 382.0c | 247.0c |
| kinetic_path_confirm | `ask<=70` | 46/118 | 38.98% | 34/12 | 73.91% | 373.0c | 380.0c |
| book_margin_gap015 | `touch_loss<=0.95` | 76/89 | 85.39% | 55/21 | 72.37% | 361.0c | 252.0c |
| book_margin | `score>=0.60` | 48/105 | 45.71% | 37/11 | 77.08% | 330.0c | 195.0c |
| kinetic_combo_price_guard | `ask<=60` | 30/100 | 30.00% | 21/9 | 70.00% | 329.0c | 137.0c |
| kinetic_price_guard | `ask<=60` | 39/107 | 36.45% | 26/13 | 66.67% | 313.0c | 302.0c |
| book_margin | `book>=0.65` | 41/105 | 39.05% | 33/8 | 80.49% | 285.0c | 150.0c |
| book_margin | `signal_score>=0.65` | 41/105 | 39.05% | 33/8 | 80.49% | 285.0c | 150.0c |
| book_margin_gap015 | `adverse15<=100` | 70/89 | 78.65% | 50/20 | 71.43% | 283.0c | 174.0c |
| book_margin_early | `adverse15<=50` | 75/101 | 74.26% | 54/21 | 72.00% | 282.0c | 177.0c |
| book_margin | `adverse15<=50` | 78/105 | 74.29% | 56/22 | 71.79% | 280.0c | 145.0c |
| kinetic_combo_price_guard | `blend>=0.50` | 57/100 | 57.00% | 40/17 | 70.18% | 277.0c | 85.0c |
| impulse_reversal_book_margin_fade | `impulse_over_margin<=20` | 50/58 | 86.21% | 30/20 | 60.00% | 274.0c | 191.0c |
| logit_blend_edge10 | `adverse15<=0` | 47/75 | 62.67% | 32/15 | 68.09% | 271.0c | 140.0c |
| book_margin_early | `score>=0.60` | 46/101 | 45.54% | 35/11 | 76.09% | 266.0c | 161.0c |
| book_margin_gap015 | `book>=0.65` | 28/89 | 31.46% | 23/5 | 82.14% | 262.0c | 153.0c |
| book_margin_gap015 | `signal_score>=0.65` | 28/89 | 31.46% | 23/5 | 82.14% | 262.0c | 153.0c |
| book_margin_gap015 | `blend>=0.45` | 69/89 | 77.53% | 49/20 | 71.01% | 258.0c | 149.0c |

## Read

- At least one diagnostic blocker is positive while retaining >=80% of that lock's strict registered rows, but sample size is too small and it must be forward-locked before use.
- Current strict evidence supports rejection of the existing locks, not promotion.
