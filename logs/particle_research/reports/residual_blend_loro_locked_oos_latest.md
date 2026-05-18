# Residual Blend LORO Report

- run_count: 4
- coefficient_count: 517
- formula: `p = current + a*(market-current) + b*(rv300-current) + c*(rv600-current) + d*(particle-current)`
- promotion_safe: False
- note: Residual blends are same-evidence diagnostics. Any selected coefficient is a new hypothesis and requires a fresh predeclared locked OOS shadow run before it can count toward promotion.

## Best Exact Global Diagnostic

- name: resid_mp00_r300n02_r600p02_pn01
- total_counterfactual_pnl_cents: 106304.0000
- current_baseline_total_counterfactual_pnl_cents: 105135.0000
- pnl_delta_vs_current_cents: 1169.0000
- mean_brier: 0.145146
- mean_log_loss: 0.430498
- beats_current_probability_run_count: 3/4
- beats_current_pnl_run_count: 3/4
- positive_ev_rank_run_count: 4/4
- positive_top_bucket_run_count: 4/4
- stable_all_runs: False

## Exact Global Rows

| coefficient | pnl_cents | delta_vs_current | mean_brier | beats_current_prob | beats_current_pnl | ev_rank_pos | top_bucket_pos | stable_all_runs |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| resid_mp00_r300n02_r600p02_pn01 | 106304.0000 | 1169.0000 | 0.145146 | 3/4 | 3/4 | 4/4 | 4/4 | False |
| resid_mn01_r300n01_r600p01_pn01 | 106126.0000 | 991.0000 | 0.145110 | 3/4 | 3/4 | 4/4 | 4/4 | False |
| resid_mp00_r300p00_r600p00_pn01 | 105735.0000 | 600.0000 | 0.145253 | 3/4 | 3/4 | 4/4 | 4/4 | False |
| resid_mn02_r300p00_r600p00_pn01 | 105642.0000 | 507.0000 | 0.145222 | 3/4 | 3/4 | 4/4 | 4/4 | False |
| resid_mp01_r300p00_r600p01_pp00 | 105498.0000 | 363.0000 | 0.145464 | 3/4 | 3/4 | 3/4 | 4/4 | False |

## Leave One Run Out Picks

| holdout | selected_coefficient | train_pnl_cents | holdout_pnl_cents | holdout_delta_vs_current | holdout_beats_current_prob | holdout_ev_rank | holdout_top_bucket_pnl |
|---|---|---:|---:|---:|---|---:|---:|
| particle_side_safety_oos_20260511TLOCKED | resid_mn01_r300n02_r600p02_pp00 | 83351.0000 | 26170.0000 | 972.0000 | False | 0.013394 | 9.9565 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | resid_mp02_r300n02_r600p00_pp00 | 75269.0000 | 32950.0000 | -46.0000 | False | -0.000821 | 2.8584 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | resid_mp00_r300n02_r600p02_pn01 | 100953.0000 | 5351.0000 | -5567.0000 | False | 0.058170 | 9.3115 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | resid_mp01_r300p00_r600p01_pp00 | 71374.0000 | 34124.0000 | -1899.0000 | False | 0.428906 | 18.3264 |
