# arXiv Strategy Stress Validation

Research-only. These checks test whether the paper-inspired gates look stable, not whether they are ready for live promotion.

- Generated UTC: `2026-05-07T23:09:57.514181+00:00`
- Matched live trades: `632`
- Bootstrap iterations: `2000` market-block samples
- Placebo iterations: `5000` random same-coverage samples

## Verdict

| strategy | overfit read | all PnL | W/L | chrono + slices | bootstrap P(net>0) | placebo p | param + cells | split+ cells | walk-forward eval PnL | notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| conformal_consensus_winrate_gate | medium_replay_overfit_risk | $10.57 | 49/38 (+2 flat) | 5/5 | 98.7% | 0.024 | 82.8% | 34.5% | $-3.13 | does_not_reliably_beat_same_sample_live_bootstrap, limited_split_positive_neighbor_cells, purged_walk_forward_failed |
| depth_decay_fillability_gate | medium_replay_overfit_risk | $21.42 | 57/79 | 5/5 | 99.9% | 0.000 | 100.0% | 79.7% | $0.19 | current_params_near_grid_peak, thin_purged_walk_forward_margin |
| brownian_fpt_sanity_gate | medium_replay_overfit_risk | $27.37 | 146/172 (+7 flat) | 5/5 | 99.6% | 0.001 | 90.5% | 50.0% | $-1.19 | current_params_near_grid_peak, purged_walk_forward_failed |
| hybrid_fpt_depth_gate | medium_replay_overfit_risk | $15.85 | 77/85 (+1 flat) | 4/5 | 98.9% | 0.013 | 96.5% | 71.8% | $7.75 | does_not_reliably_beat_same_sample_live_bootstrap |

## Parameter Stability

| family | eligible cells | current percentile | net p10/p50/p90 | current net | current split+ | top cell net |
|---|---:|---:|---:|---:|---|---:|
| consensus_probability_gap | 29 | 79.3% | -56.0c/429.0c/1,159.0c | $10.57 | True | $13.25 |
| depth_decay_fillability | 600 | 98.8% | 927.0c/1,416.0c/1,843.0c | $21.42 | True | $22.41 |
| brownian_fpt_sanity | 400 | 100.0% | 23.0c/958.0c/1,979.0c | $27.37 | True | $27.37 |
| hybrid_fpt_depth | 6480 | 78.2% | 273.0c/1,091.0c/1,855.0c | $15.85 | True | $28.35 |

## Walk-Forward Lockout

Each family picks the best positive parameter set on prior data, purges the last 5 train markets, then scores the next chronological chunk.

| family | combined eval entries | combined eval W/L | combined eval PnL | live eval PnL | fold eval PnLs |
|---|---:|---:|---:|---:|---|
| consensus_probability_gap | 255 | 111/137 (+7 flat) | $-3.13 | $-4.99 | $-3.84, $1.09, $-0.38 |
| depth_decay_fillability | 256 | 107/144 (+5 flat) | $0.19 | $-4.99 | $-4.30, $-1.19, $5.68 |
| brownian_fpt_sanity | 311 | 128/174 (+9 flat) | $-1.19 | $-4.99 | $-4.92, $1.43, $2.30 |
| hybrid_fpt_depth | 266 | 118/141 (+7 flat) | $7.75 | $-4.99 | $1.22, $2.31, $4.22 |

## Interpretation

- `placebo p` is the fraction of random same-size trade subsets with PnL at least as high as the candidate; lower is better.
- `param + cells` means the share of nearby parameter cells with positive total PnL. `split+ cells` means train, validation, and holdout were all positive.
- This is still retrospective live-log replay. The promotion gate should remain frozen forward collection, not immediate live logic changes.
