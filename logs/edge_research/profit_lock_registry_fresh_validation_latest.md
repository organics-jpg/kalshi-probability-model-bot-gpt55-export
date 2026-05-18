# Profit Lock Registry Fresh Validation

Generated UTC: `20260504_155442Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Uses pre-resolution registry rows as the forward source of truth.
- Joins the market-denominator audit for recurring-market coverage.
- Flags when recompute validators are stale relative to the live registry.

## Source Freshness

| source | rows | max resolved close | max pending close | stale vs registry |
|---|---:|---:|---:|---|
| raw recompute ledger `logs\edge_research\live_heartbeat_two_side_fv_ledger_latest.csv` | 37692 | 2026-05-04T15:45:00+00:00 | NA | False |
| registered signal registry | 1865 | 2026-05-04T15:45:00+00:00 | 2026-05-04T16:00:00+00:00 | False |

## Key Candidates

| lock | reg/res/pend | wins/losses | acc | break-even | P(p>BE) | p05 edge | resolved cov | net P&L | ROI | median ask | extra wins | ready |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| hazard_mean_touch80 | 34/33/1 | 24/9 | 72.73% | 72.82% | 0.449 | -14.5c | 91.67% | -3.0c | -0.12% | 71.0c | 21 | False |
| book_margin | 65/64/1 | 44/20 | 68.75% | 69.11% | 0.449 | -10.6c | 98.46% | -23.0c | -0.52% | 65.0c | 25 | False |
| book_margin_early | 61/60/1 | 41/19 | 68.33% | 69.22% | 0.414 | -11.5c | 98.36% | -53.0c | -1.28% | 65.0c | 25 | False |
| book_p80_ask90_frontier | 8/7/1 | 5/2 | 71.43% | 83.86% | 0.124 | -43.8c | 87.50% | -87.0c | -14.82% | 83.0c | 29 | False |
| hazard_fallback_score60 | 27/26/1 | 18/8 | 69.23% | 72.88% | 0.297 | -20.0c | 96.30% | -95.0c | -5.01% | 70.5c | 23 | False |
| hazard_mean_touch80_ask76 | 19/18/1 | 12/6 | 66.67% | 72.28% | 0.257 | -25.4c | 81.82% | -101.0c | -7.76% | 70.0c | 21 | False |
| logit_blend_thresh55_edge15 | 32/31/1 | 21/10 | 67.74% | 72.26% | 0.256 | -19.5c | 93.94% | -140.0c | -6.25% | 69.0c | 26 | False |
| hazard_fallback_logit55 | 31/30/1 | 20/10 | 66.67% | 72.23% | 0.221 | -20.7c | 93.75% | -167.0c | -7.71% | 68.5c | 27 | False |
| book_p80_profit_frontier | 10/9/1 | 6/3 | 66.67% | 85.22% | 0.047 | -45.9c | 100.00% | -167.0c | -21.77% | 83.0c | 41 | False |
| logit_blend_edge10 | 35/34/1 | 19/15 | 55.88% | 61.06% | 0.256 | -19.1c | 97.14% | -176.0c | -8.48% | 54.0c | 20 | False |
| impulse_reversal_book_margin_fade | 18/17/1 | 6/11 | 35.29% | 46.47% | 0.190 | -26.6c | 94.44% | -190.0c | -24.05% | 39.0c | 12 | False |
| kinetic_path_confirm | 81/80/1 | 58/22 | 72.50% | 75.10% | 0.271 | -11.6c | 58.39% | -208.0c | -3.46% | 74.0c | 41 | False |
| hazard_fallback_logit55_wait8 | 26/25/1 | 16/9 | 64.00% | 72.92% | 0.139 | -25.5c | 89.29% | -223.0c | -12.23% | 71.0c | 29 | False |

## Top Registered Locks

| lock | reg/res/pend | wins/losses | acc | break-even | P(p>BE) | p05 edge | resolved cov | net P&L | ROI | median ask | extra wins | ready |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| hazard_mean_touch80 | 34/33/1 | 24/9 | 72.73% | 72.82% | 0.449 | -14.5c | 91.67% | -3.0c | -0.12% | 71.0c | 21 | False |
| book_margin | 65/64/1 | 44/20 | 68.75% | 69.11% | 0.449 | -10.6c | 98.46% | -23.0c | -0.52% | 65.0c | 25 | False |
| book_margin_early | 61/60/1 | 41/19 | 68.33% | 69.22% | 0.414 | -11.5c | 98.36% | -53.0c | -1.28% | 65.0c | 25 | False |
| book_p80_ask90_frontier | 8/7/1 | 5/2 | 71.43% | 83.86% | 0.124 | -43.8c | 87.50% | -87.0c | -14.82% | 83.0c | 29 | False |
| hazard_fallback_score60 | 27/26/1 | 18/8 | 69.23% | 72.88% | 0.297 | -20.0c | 96.30% | -95.0c | -5.01% | 70.5c | 23 | False |
| hazard_mean_touch80_ask76 | 19/18/1 | 12/6 | 66.67% | 72.28% | 0.257 | -25.4c | 81.82% | -101.0c | -7.76% | 70.0c | 21 | False |
| touch_overlay | 97/96/1 | 56/40 | 58.33% | 59.74% | 0.380 | -9.8c | 65.75% | -135.0c | -2.35% | 56.0c | 26 | False |
| logit_blend_thresh55_edge15 | 32/31/1 | 21/10 | 67.74% | 72.26% | 0.256 | -19.5c | 93.94% | -140.0c | -6.25% | 69.0c | 26 | False |
| hazard_fallback_logit55 | 31/30/1 | 20/10 | 66.67% | 72.23% | 0.221 | -20.7c | 93.75% | -167.0c | -7.71% | 68.5c | 27 | False |
| book_p80_profit_frontier | 10/9/1 | 6/3 | 66.67% | 85.22% | 0.047 | -45.9c | 100.00% | -167.0c | -21.77% | 83.0c | 41 | False |
| logit_blend_edge10 | 35/34/1 | 19/15 | 55.88% | 61.06% | 0.256 | -19.1c | 97.14% | -176.0c | -8.48% | 54.0c | 20 | False |
| kinetic_price_guard | 75/74/1 | 46/28 | 62.16% | 64.68% | 0.313 | -12.1c | 52.11% | -186.0c | -3.89% | 63.0c | 28 | False |

## Hazard Fallback Branches

| lock | chooser | resolved | wins/losses | acc | net P&L | median ask | median score |
|---|---|---:|---:|---:|---:|---:|---:|
| hazard_fallback_logit55 | `blend_logit_book_rv_hazard_mean` | 10 | 5/5 | 50.00% | -224.0c | 67.5c | 0.565 |
| hazard_fallback_logit55 | `hazard_discounted_mean_15` | 20 | 15/5 | 75.00% | 57.0c | 71.5c | 0.508 |
| hazard_fallback_logit55_wait8 | `hazard_discounted_mean_15` | 25 | 16/9 | 64.00% | -223.0c | 71.0c | 0.522 |
| hazard_fallback_score60 | `hazard_discounted_mean_15` | 20 | 14/6 | 70.00% | -56.0c | 71.5c | 0.517 |
| hazard_fallback_score60 | `score_min_book_rv15` | 6 | 4/2 | 66.67% | -39.0c | 63.0c | 0.612 |

## Read

- No registered lock clears the Bayesian promotion gate yet.
- No registered lock clears the stricter Wilson promotion gate yet.
