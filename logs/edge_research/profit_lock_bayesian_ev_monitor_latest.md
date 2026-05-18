# Profit Lock Bayesian EV Monitor

Generated UTC: `20260505_030330Z`

## Scope

- Research-only monitor; no orders are submitted and no bot files or live processes are touched.
- Uses strict registered-signal readiness rows when available; otherwise falls back to validator fresh metrics.
- Posterior uses neutral Beta(1, 1), Monte Carlo sampled for EV probability and edge intervals.
- Ready gate: at least 30 fresh selected markets, >=80% fresh coverage, positive fresh net, posterior P(win rate > break-even) >= 0.95, and positive p05 posterior edge.

## Posterior EV State

| lock | source | overlay | fresh | acc | break-even | net P&L | posterior mean p | P(p>BE) | p05 edge | mean edge | extra perfect wins | ready |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| original | `registered_signal_readiness` | `none` | 92/45 of 137 | 67.15% | 66.36% | 108.0c | 66.92% | 0.563 | -6.1c | 0.6c | 27 | False |
| frontier_v2 | `registered_signal_readiness` | `none` | 71/44 of 115 | 61.74% | 63.21% | -169.0c | 61.56% | 0.362 | -9.1c | -1.7c | 31 | False |
| frontier_v2_continuous | `registered_signal_readiness` | `none` | 65/41 of 106 | 61.32% | 63.36% | -216.0c | 61.11% | 0.321 | -10.0c | -2.2c | 32 | False |
| book_margin | `registered_signal_readiness` | `none` | 73/32 of 105 | 69.52% | 68.24% | 135.0c | 69.17% | 0.593 | -6.5c | 0.9c | 24 | False |
| book_margin_early | `registered_signal_readiness` | `none` | 70/31 of 101 | 69.31% | 68.27% | 105.0c | 68.94% | 0.569 | -7.0c | 0.7c | 24 | False |
| book_margin_gap015 | `registered_signal_readiness` | `none` | 61/28 of 89 | 68.54% | 67.31% | 109.0c | 68.11% | 0.575 | -7.4c | 0.8c | 22 | False |
| book_margin_adverse100 | `registered_signal_readiness` | `none` | 46/23 of 69 | 66.67% | 67.71% | -72.0c | 66.19% | 0.403 | -10.9c | -1.5c | 26 | False |
| book_margin_delayed_adv100_brownian55 | `registered_signal_readiness` | `none` | 55/26 of 81 | 67.90% | 71.12% | -261.0c | 67.47% | 0.242 | -12.3c | -3.7c | 38 | False |
| book_hour04_v2_switch | `registered_signal_readiness` | `none` | 52/33 of 85 | 61.18% | 64.84% | -311.0c | 60.93% | 0.230 | -12.6c | -3.9c | 34 | False |
| book_refmargin_score_switch | `registered_signal_readiness` | `none` | 55/23 of 78 | 70.51% | 71.99% | -115.0c | 70.01% | 0.361 | -10.6c | -2.0c | 33 | False |
| score_min60 | `registered_signal_readiness` | `none` | 72/30 of 102 | 70.59% | 72.39% | -184.0c | 70.18% | 0.320 | -9.8c | -2.2c | 39 | False |
| score_min60_gap020 | `registered_signal_readiness` | `none` | 64/27 of 91 | 70.33% | 72.31% | -180.0c | 69.90% | 0.315 | -10.5c | -2.4c | 38 | False |
| book_early_score_gap020_wait | `registered_signal_readiness` | `none` | 61/27 of 88 | 69.32% | 71.98% | -234.0c | 68.90% | 0.270 | -11.3c | -3.1c | 39 | False |
| book_score_gap020_wait | `registered_signal_readiness` | `none` | 58/27 of 85 | 68.24% | 71.94% | -315.0c | 67.83% | 0.209 | -12.6c | -4.1c | 42 | False |
| v2_wait_score_min60_early | `registered_signal_readiness` | `none` | 71/30 of 101 | 70.30% | 72.23% | -195.0c | 69.90% | 0.311 | -9.9c | -2.3c | 39 | False |
| v2_wait_score_min60_brownian70_early | `registered_signal_readiness` | `none` | 69/28 of 97 | 71.13% | 72.24% | -107.0c | 70.70% | 0.379 | -9.3c | -1.5c | 35 | False |
| challenger | `registered_signal_readiness` | `ask>=50 AND ask<=80` | 87/41 of 128 | 67.97% | 66.86% | 142.0c | 67.70% | 0.589 | -6.0c | 0.8c | 25 | False |
| touch_hazard | `registered_signal_readiness` | `none` | 87/59 of 146 | 59.59% | 60.26% | -98.0c | 59.45% | 0.424 | -7.5c | -0.8c | 30 | False |
| touch_overlay | `registered_signal_readiness` | `ask>=50 AND touch_loss15>=0.80` | 84/54 of 138 | 60.87% | 60.01% | 119.0c | 60.71% | 0.572 | -6.1c | 0.7c | 23 | False |
| kinetic_touch | `registered_signal_readiness` | `none` | 89/45 of 134 | 66.42% | 68.54% | -285.0c | 66.18% | 0.286 | -9.2c | -2.4c | 42 | False |
| hazard_mean_touch80 | `registered_signal_readiness` | `none` | 50/19 of 69 | 72.46% | 72.58% | -8.0c | 71.84% | 0.460 | -9.8c | -0.7c | 27 | False |
| logit_blend_edge10 | `registered_signal_readiness` | `none` | 48/27 of 75 | 64.00% | 62.25% | 131.0c | 63.65% | 0.608 | -7.8c | 1.4c | 17 | False |
| logit_blend_thresh55_edge15 | `registered_signal_readiness` | `none` | 49/20 of 69 | 71.01% | 71.64% | -43.0c | 70.44% | 0.425 | -10.4c | -1.2c | 28 | False |
| hazard_fallback_logit55 | `registered_signal_readiness` | `none` | 48/20 of 68 | 70.59% | 71.62% | -70.0c | 69.98% | 0.394 | -10.9c | -1.6c | 29 | False |
| hazard_fallback_logit55_wait8 | `registered_signal_readiness` | `none` | 42/19 of 61 | 68.85% | 72.59% | -228.0c | 68.24% | 0.234 | -14.3c | -4.4c | 35 | False |
| hazard_fallback_score60 | `registered_signal_readiness` | `none` | 46/18 of 64 | 71.88% | 72.12% | -16.0c | 71.21% | 0.450 | -10.4c | -0.9c | 27 | False |
| impulse_reversal_book_margin_fade | `registered_signal_readiness` | `none` | 33/25 of 58 | 56.90% | 55.47% | 83.0c | 56.67% | 0.579 | -9.3c | 1.2c | 14 | False |
| kinetic_guard | `registered_signal_readiness` | `kinetic>=0.57 AND adverse15<=50` | 89/37 of 126 | 70.63% | 70.06% | 72.0c | 70.32% | 0.536 | -6.5c | 0.3c | 30 | False |
| kinetic_price_guard | `registered_signal_readiness` | `adverse15<=100 AND ask<=70` | 69/38 of 107 | 64.49% | 64.38% | 11.0c | 64.22% | 0.493 | -7.9c | -0.2c | 26 | False |
| kinetic_combo_price_guard | `registered_signal_readiness` | `kinetic>=0.57 AND adverse15<=100 AND ask<=70` | 67/33 of 100 | 67.00% | 65.08% | 192.0c | 66.68% | 0.642 | -6.2c | 1.6c | 20 | False |
| kinetic_path_confirm | `registered_signal_readiness` | `same_side_for>=60s AND confirm_score>=0.6` | 89/29 of 118 | 75.42% | 75.48% | -7.0c | 75.01% | 0.467 | -7.2c | -0.5c | 37 | False |
| book_p80_ask90_frontier | `registered_signal_readiness` | `none` | 34/6 of 40 | 85.00% | 84.80% | 8.0c | 83.35% | 0.434 | -11.6c | -1.5c | 34 | False |
| book_p80_profit_frontier | `registered_signal_readiness` | `none` | 34/7 of 41 | 82.93% | 85.02% | -86.0c | 81.39% | 0.287 | -14.1c | -3.6c | 43 | False |
| hazard_mean_touch80_ask76 | `registered_signal_readiness` | `none` | 37/16 of 53 | 69.81% | 71.89% | -110.0c | 69.08% | 0.337 | -13.4c | -2.8c | 29 | False |

## Read

- No lock clears the Bayesian EV gate yet.
- original: posterior P(p>break-even) is 0.563; needs 27 additional perfect fresh wins to reach the posterior probability gate from the current state.
- frontier_v2: posterior P(p>break-even) is 0.362; needs 31 additional perfect fresh wins to reach the posterior probability gate from the current state.
- frontier_v2_continuous: posterior P(p>break-even) is 0.321; needs 32 additional perfect fresh wins to reach the posterior probability gate from the current state.
- book_margin: posterior P(p>break-even) is 0.593; needs 24 additional perfect fresh wins to reach the posterior probability gate from the current state.
- book_margin_early: posterior P(p>break-even) is 0.569; needs 24 additional perfect fresh wins to reach the posterior probability gate from the current state.
- book_margin_gap015: posterior P(p>break-even) is 0.575; needs 22 additional perfect fresh wins to reach the posterior probability gate from the current state.
- book_margin_adverse100: posterior P(p>break-even) is 0.403; needs 26 additional perfect fresh wins to reach the posterior probability gate from the current state.
- book_margin_delayed_adv100_brownian55: posterior P(p>break-even) is 0.242; needs 38 additional perfect fresh wins to reach the posterior probability gate from the current state.
- book_hour04_v2_switch: posterior P(p>break-even) is 0.230; needs 34 additional perfect fresh wins to reach the posterior probability gate from the current state.
- book_refmargin_score_switch: posterior P(p>break-even) is 0.361; needs 33 additional perfect fresh wins to reach the posterior probability gate from the current state.
- score_min60: posterior P(p>break-even) is 0.320; needs 39 additional perfect fresh wins to reach the posterior probability gate from the current state.
- score_min60_gap020: posterior P(p>break-even) is 0.315; needs 38 additional perfect fresh wins to reach the posterior probability gate from the current state.
- book_early_score_gap020_wait: posterior P(p>break-even) is 0.270; needs 39 additional perfect fresh wins to reach the posterior probability gate from the current state.
- book_score_gap020_wait: posterior P(p>break-even) is 0.209; needs 42 additional perfect fresh wins to reach the posterior probability gate from the current state.
- v2_wait_score_min60_early: posterior P(p>break-even) is 0.311; needs 39 additional perfect fresh wins to reach the posterior probability gate from the current state.
- v2_wait_score_min60_brownian70_early: posterior P(p>break-even) is 0.379; needs 35 additional perfect fresh wins to reach the posterior probability gate from the current state.
- challenger: posterior P(p>break-even) is 0.589; needs 25 additional perfect fresh wins to reach the posterior probability gate from the current state.
- touch_hazard: posterior P(p>break-even) is 0.424; needs 30 additional perfect fresh wins to reach the posterior probability gate from the current state.
- touch_overlay: posterior P(p>break-even) is 0.572; needs 23 additional perfect fresh wins to reach the posterior probability gate from the current state.
- kinetic_touch: posterior P(p>break-even) is 0.286; needs 42 additional perfect fresh wins to reach the posterior probability gate from the current state.
- hazard_mean_touch80: posterior P(p>break-even) is 0.460; needs 27 additional perfect fresh wins to reach the posterior probability gate from the current state.
- logit_blend_edge10: posterior P(p>break-even) is 0.608; needs 17 additional perfect fresh wins to reach the posterior probability gate from the current state.
- logit_blend_thresh55_edge15: posterior P(p>break-even) is 0.425; needs 28 additional perfect fresh wins to reach the posterior probability gate from the current state.
- hazard_fallback_logit55: posterior P(p>break-even) is 0.394; needs 29 additional perfect fresh wins to reach the posterior probability gate from the current state.
- hazard_fallback_logit55_wait8: posterior P(p>break-even) is 0.234; needs 35 additional perfect fresh wins to reach the posterior probability gate from the current state.
- hazard_fallback_score60: posterior P(p>break-even) is 0.450; needs 27 additional perfect fresh wins to reach the posterior probability gate from the current state.
- impulse_reversal_book_margin_fade: posterior P(p>break-even) is 0.579; needs 14 additional perfect fresh wins to reach the posterior probability gate from the current state.
- kinetic_guard: posterior P(p>break-even) is 0.536; needs 30 additional perfect fresh wins to reach the posterior probability gate from the current state.
- kinetic_price_guard: posterior P(p>break-even) is 0.493; needs 26 additional perfect fresh wins to reach the posterior probability gate from the current state.
- kinetic_combo_price_guard: posterior P(p>break-even) is 0.642; needs 20 additional perfect fresh wins to reach the posterior probability gate from the current state.
- kinetic_path_confirm: posterior P(p>break-even) is 0.467; needs 37 additional perfect fresh wins to reach the posterior probability gate from the current state.
- book_p80_ask90_frontier: posterior P(p>break-even) is 0.434; needs 34 additional perfect fresh wins to reach the posterior probability gate from the current state.
- book_p80_profit_frontier: posterior P(p>break-even) is 0.287; needs 43 additional perfect fresh wins to reach the posterior probability gate from the current state.
- hazard_mean_touch80_ask76: posterior P(p>break-even) is 0.337; needs 29 additional perfect fresh wins to reach the posterior probability gate from the current state.
