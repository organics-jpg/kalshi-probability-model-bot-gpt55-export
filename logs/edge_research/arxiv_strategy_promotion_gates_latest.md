# arXiv Promotion Gates

Research-only diagnostics based on the Truffle synthesis. These tests are stricter than the earlier replay reports and should be treated as promotion blockers unless confirmed forward.

- Generated UTC: `2026-05-08T00:47:59.739316+00:00`
- Matched trades: `632`
- Settled labels for ACI: `630`
- CPCV: `5` folds, `2` test folds/path, `12` trade embargo

## Fixed Candidate Gates

| candidate | replay PnL | W/L | CPCV pass | CPCV pos paths | median path edge | p25 edge | edge CV | e max | e>=20 | ACI cov | ACI useful |
|---|---:|---:|---|---:|---:|---:|---:|---:|---|---:|---|
| brownian_fpt_current | $27.37 | 146/172 (+7 flat) | True | 10/10 | 8.7c | 6.2c | 0.21 | 9.20 | False | 88.9% | True |
| depth_decay_current | $21.42 | 57/79 | True | 10/10 | 15.9c | 12.9c | 0.21 | 6.15 | False | 95.7% | False |
| hybrid_fpt_depth_current | $15.85 | 77/85 (+1 flat) | True | 10/10 | 9.7c | 6.0c | 0.58 | 3.73 | False | 90.7% | True |
| hybrid_fpt_depth_robust_rank1 | $24.85 | 99/107 (+3 flat) | True | 10/10 | 12.6c | 9.3c | 0.34 | 8.28 | False | 90.9% | True |
| consensus_gap_robust_rank1 | $11.85 | 51/47 (+4 flat) | True | 10/10 | 12.3c | 8.7c | 0.47 | 3.05 | False | 92.1% | False |

## Dynamic Family CPCV

For each CPCV path, parameters are selected on train-only rows using the stable-subsplit rule, then evaluated on the held-out test folds.

| family | combined PnL | W/L | positive paths | beat-live paths | median path PnL | min path PnL |
|---|---:|---:|---:|---:|---:|---:|
| consensus_probability_gap | $19.65 | 400/454 (+23 flat) | 8/10 | 3/10 | 351.5c | -512.0c |
| depth_decay_fillability | $57.28 | 499/602 (+9 flat) | 8/10 | 6/10 | 757.0c | -329.0c |
| brownian_fpt_sanity | $70.44 | 491/616 (+24 flat) | 9/10 | 7/10 | 608.0c | -56.0c |
| hybrid_fpt_depth | $67.15 | 556/723 (+26 flat) | 10/10 | 6/10 | 654.5c | 357.0c |

## Feature Recording Audit

| field | rows present | share |
|---|---:|---:|
| p28 | 632 | 100.0% |
| probability_gap | 632 | 100.0% |
| conformal_score | 630 | 99.7% |
| depth_ratio | 632 | 100.0% |
| book_age_ms | 632 | 100.0% |
| seconds_to_close | 632 | 100.0% |
| abs_d_sigma | 632 | 100.0% |
| pnl_cents | 632 | 100.0% |
| side_correct | 630 | 99.7% |

Missing/not-native future validation fields: native conformal interval width, e_process_value at decision time, ACI threshold q_t at decision time, Brownian FPT probability, jump-diffusion FPT probability, order arrival/cancel/execution counts, queue position, depth decay slope per market, CPCV path ID in live shadow logs

## Interpretation

- CPCV pass here requires positive median and 25th-percentile path edge, edge CV below 0.75, and no single path contributing more than 50% of positive path PnL.
- The e-process row is an anytime-monitoring approximation over realized PnL, not a theorem-valid proof of edge yet.
- ACI uses settlement side correctness and v28 p_side; it checks whether adaptive uncertainty is calibrated and whether high uncertainty actually marks worse trades.
- Any candidate that looks good here still needs frozen forward shadow collection before live promotion.
