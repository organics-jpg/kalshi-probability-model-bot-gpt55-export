# Side/Regime Diagnostic

- run_count: 1
- selected_count: 3045
- total_counterfactual_pnl_cents: 60332.0000
- stable_positive_rules: 5
- conclusion: At least one diagnostic rule is positive in every supplied run; treat it as a candidate for a fresh locked OOS plan, not as promotion evidence.

## Rule Summary

| rule | positive_runs | selected | total_pnl_cents | min_run_pnl_cents | stable_positive |
|---|---:|---:|---:|---:|---|
| base | 1/1 | 3045 | 60332.0000 | 60332.0000 | True |
| skip_late_300s_against_consensus_05 | 1/1 | 2259 | 59006.0000 | 59006.0000 | True |
| skip_against_consensus_20 | 1/1 | 1407 | 46098.0000 | 46098.0000 | True |
| skip_against_consensus_10 | 1/1 | 773 | 19240.0000 | 19240.0000 | True |
| skip_against_consensus_05 | 1/1 | 431 | 5272.0000 | 5272.0000 | True |
| require_current_agreement | 0/1 | 214 | -716.0000 | -716.0000 | False |
| skip_against_consensus_any | 0/1 | 215 | -767.0000 | -767.0000 | False |
| require_market_current_consensus_alignment | 0/1 | 58 | -1022.0000 | -1022.0000 | False |
| require_market_agreement | 0/1 | 59 | -1073.0000 | -1073.0000 | False |

## Buckets

| type | bucket | selected | win_rate | total_pnl_cents | avg_pnl_cents |
|---|---|---:|---:|---:|---:|
| side | no | 948 | 0.0527 | -13796.0000 | -14.5527 |
| side | yes | 2097 | 0.6552 | 74128.0000 | 35.3495 |
| consensus | against_market_current | 2830 | 0.4693 | 61099.0000 | 21.5898 |
| consensus | aligned_with_market_current | 58 | 0.3621 | -1022.0000 | -17.6207 |
| consensus | market_current_disagree | 157 | 0.4777 | 255.0000 | 1.6242 |
| confidence | against_strong_05pp_consensus | 342 | 0.8392 | 13968.0000 | 40.8421 |
| confidence | against_strong_10pp_consensus | 634 | 0.7839 | 26858.0000 | 42.3628 |
| confidence | against_strong_20pp_consensus | 1638 | 0.2350 | 14234.0000 | 8.6899 |
| confidence | aligned_consensus | 58 | 0.3621 | -1022.0000 | -17.6207 |
| confidence | mixed_or_weak | 373 | 0.6273 | 6294.0000 | 16.8740 |
| time_to_close | 000_060s | 17 | 0.0000 | 0.0000 | 0.0000 |
| time_to_close | 061_180s | 347 | 0.0029 | -1726.0000 | -4.9741 |
| time_to_close | 181_300s | 449 | 0.2004 | 2780.0000 | 6.1915 |
| time_to_close | 301_600s | 1172 | 0.4795 | 22633.0000 | 19.3114 |
| time_to_close | gt_600s | 1060 | 0.7274 | 36645.0000 | 34.5708 |

## Rule By Run

| run | rule | selected | win_rate | pnl_cents |
|---|---|---:|---:|---:|
| particle_residual_blend_oos_RESIDLOCK001 | base | 3045 | 0.4677 | 60332.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | require_market_agreement | 59 | 0.3559 | -1073.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | require_current_agreement | 214 | 0.4486 | -716.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | require_market_current_consensus_alignment | 58 | 0.3621 | -1022.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | skip_against_consensus_any | 215 | 0.4465 | -767.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | skip_against_consensus_05 | 431 | 0.5916 | 5272.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | skip_against_consensus_10 | 773 | 0.7012 | 19240.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | skip_against_consensus_20 | 1407 | 0.7385 | 46098.0000 |
| particle_residual_blend_oos_RESIDLOCK001 | skip_late_300s_against_consensus_05 | 2259 | 0.5936 | 59006.0000 |
