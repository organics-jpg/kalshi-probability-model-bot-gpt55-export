# Empirical Market Opportunity LORO

- source_report: `logs\particle_research\reports\empirical_market_opportunity_diagnostic_20260512_nine_locked.json`
- source_run_count: 6
- source_opportunity_row_count: 280
- transforms: raw_ev, current_gap_penalty_10, current_gap_penalty_25, market_gap_penalty_10, market_gap_penalty_25, dual_gap_penalty_10, dual_gap_penalty_25
- selector: train_strict_ev_bucket_score
- candidate_ready_for_predeclared_shadow: False
- promotion_safe: False
- conclusion: No leave-one-run-out market-opportunity transform cleared strict holdout gates.

## Summary

| selector | holdouts | pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | strict | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| train_strict_ev_bucket_score | 6 | 84.0000 | 0.168262 | 0.518666 | 5/6 | 5/6 | 3/6 | 3/6 | 3/6 | 1/6 | 0/6 | False |

## Holdouts

| holdout | family | spec | transform | train_pnl | markets | selected | holdout_pnl | brier | beats_current | ev_rank | top_bucket | strict |
|---|---|---|---|---:|---:|---:|---:|---:|---|---:|---:|---|
| particle_fixed_terminal_oos_GAUSS45LOCK001 | empirical | emp1s_610_center_blend50_p96_d48 | dual_gap_penalty_25 | 244.0000 | 4 | 4 | 18.0000 | 0.197823 | True | 0.000000 | -3.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | current_anchor | current_emp987_w10_mean25 | raw_ev | 366.0000 | 7 | 7 | -153.0000 | 0.300738 | True | 0.142857 | -16.0000 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | empirical | emp1s_610_center_blend50_p96_d48 | current_gap_penalty_10 | 230.0000 | 6 | 6 | 32.0000 | 0.148516 | False | 0.000000 | -4.0000 | False |
| particle_residual_blend_oos_RESIDLOCK001 | empirical | emp1s_610_center_blend50_p96_d48 | dual_gap_penalty_25 | 146.0000 | 5 | 5 | 116.0000 | 0.162833 | True | -0.200000 | -4.5000 | False |
| particle_side_consensus_oos_CONSENSUSLOCK001 | empirical | emp1s_610_center_blend50_p96_d48 | dual_gap_penalty_25 | 228.0000 | 6 | 6 | 34.0000 | 0.101968 | False | 0.285714 | 38.5000 | False |
| particle_spot_rv_terminal_oos_RVTERMLOCK001 | empirical | emp1s_610_center_blend50_p96_d48 | raw_ev | 225.0000 | 7 | 7 | 37.0000 | 0.097693 | False | 0.300000 | -5.0000 | False |
