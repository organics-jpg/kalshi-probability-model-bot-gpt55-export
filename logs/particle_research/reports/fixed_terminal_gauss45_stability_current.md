# OOS Stability Report

- run_count: 2
- runs: particle_fixed_terminal_oos_GAUSS45LOCK001, particle_fixed_terminal_oos_GAUSS45LOCK002
- min_runs_for_stability: 2
- variant_row_count: 20
- stability_row_count: 10
- stable_candidate_count: 0
- promotion_safe: False
- note: This is a locked-run stability diagnostic. It does not promote a strategy by itself; any new variant selected from this table needs a predeclared fresh OOS run.

## Stability Rows

| source | variant | runs | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | positive_ev_rank | positive_top_bucket | beats_brownian | beats_market | beats_current | stable_all_runs |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| probability | market_particle_75_25 | 2 | 102918.0000 | 0.251384 | 0.700597 | 2 | 2 | 2 | 0 | 2 | 2 | False |
| probability | brownian | 2 | 98684.0000 | 0.233510 | 0.652869 | 2 | 2 | 2 | 0 | 2 | 2 | False |
| probability | particle | 2 | 97736.0000 | 0.233582 | 0.653032 | 2 | 2 | 2 | 1 | 2 | 2 | False |
| static | particle | 2 | 97736.0000 | 0.233582 | 0.653032 | 2 | 2 | 2 | 1 | 2 | 2 | False |
| fixed_terminal | gaussian_vol45_terminal_v1 | 2 | 97033.0000 | 0.242775 | 0.674356 | 2 | 2 | 2 | 0 | 2 | 2 | False |
| probability | market_current_particle_40_40_20 | 2 | 61930.0000 | 0.256668 | 0.717612 | 2 | 0 | 2 | 0 | 2 | 2 | False |
| probability | current_particle_75_25 | 2 | 39711.0000 | 0.258478 | 0.722499 | 2 | 0 | 2 | 0 | 1 | 2 | False |
| probability | market | 2 | 0.0000 | 0.262402 | 0.746854 | 0 | 0 | 0 | 0 | 0 | 2 | False |
| probability | market_current_50_50 | 2 | -29154.0000 | 0.266146 | 0.757853 | 0 | 0 | 1 | 0 | 0 | 2 | False |
| probability | current_calibrated | 2 | -40068.0000 | 0.271314 | 0.778118 | 0 | 0 | 0 | 0 | 0 | 0 | False |
