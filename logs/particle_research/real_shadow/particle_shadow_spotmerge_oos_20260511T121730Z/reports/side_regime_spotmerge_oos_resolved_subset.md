# Side/Regime Diagnostic

- run_count: 1
- selected_count: 544
- total_counterfactual_pnl_cents: -10645.0000
- stable_positive_rules: 0
- conclusion: No predeclared side/regime diagnostic rule is positive in every supplied run.

## Rule Summary

| rule | positive_runs | selected | total_pnl_cents | min_run_pnl_cents | stable_positive |
|---|---:|---:|---:|---:|---|
| require_market_agreement | 0/1 | 1 | -52.0000 | -52.0000 | False |
| require_market_current_consensus_alignment | 0/1 | 1 | -52.0000 | -52.0000 | False |
| require_current_agreement | 0/1 | 29 | -1100.0000 | -1100.0000 | False |
| skip_against_consensus_any | 0/1 | 29 | -1100.0000 | -1100.0000 | False |
| skip_against_consensus_05 | 0/1 | 49 | -1944.0000 | -1944.0000 | False |
| skip_against_consensus_10 | 0/1 | 104 | -3971.0000 | -3971.0000 | False |
| skip_against_consensus_20 | 0/1 | 209 | -7658.0000 | -7658.0000 | False |
| skip_late_300s_against_consensus_05 | 0/1 | 417 | -10558.0000 | -10558.0000 | False |
| base | 0/1 | 544 | -10645.0000 | -10645.0000 | False |

## Buckets

| type | bucket | selected | win_rate | total_pnl_cents | avg_pnl_cents |
|---|---|---:|---:|---:|---:|
| side | no | 541 | 0.0000 | -10795.0000 | -19.9538 |
| side | yes | 3 | 1.0000 | 150.0000 | 50.0000 |
| consensus | against_market_current | 515 | 0.0000 | -9545.0000 | -18.5340 |
| consensus | aligned_with_market_current | 1 | 0.0000 | -52.0000 | -52.0000 |
| consensus | market_current_disagree | 28 | 0.1071 | -1048.0000 | -37.4286 |
| confidence | against_strong_05pp_consensus | 55 | 0.0000 | -2027.0000 | -36.8545 |
| confidence | against_strong_10pp_consensus | 105 | 0.0000 | -3687.0000 | -35.1143 |
| confidence | against_strong_20pp_consensus | 335 | 0.0000 | -2987.0000 | -8.9164 |
| confidence | aligned_consensus | 1 | 0.0000 | -52.0000 | -52.0000 |
| confidence | mixed_or_weak | 48 | 0.0625 | -1892.0000 | -39.4167 |
| time_to_close | 061_180s | 23 | 0.0000 | 0.0000 | 0.0000 |
| time_to_close | 181_300s | 104 | 0.0000 | -87.0000 | -0.8365 |
| time_to_close | 301_600s | 286 | 0.0000 | -6242.0000 | -21.8252 |
| time_to_close | gt_600s | 131 | 0.0229 | -4316.0000 | -32.9466 |

## Rule By Run

| run | rule | selected | win_rate | pnl_cents |
|---|---|---:|---:|---:|
| particle_shadow_spotmerge_oos_20260511T121730Z | base | 544 | 0.0055 | -10645.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | require_market_agreement | 1 | 0.0000 | -52.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | require_current_agreement | 29 | 0.1034 | -1100.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | require_market_current_consensus_alignment | 1 | 0.0000 | -52.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | skip_against_consensus_any | 29 | 0.1034 | -1100.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | skip_against_consensus_05 | 49 | 0.0612 | -1944.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | skip_against_consensus_10 | 104 | 0.0288 | -3971.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | skip_against_consensus_20 | 209 | 0.0144 | -7658.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | skip_late_300s_against_consensus_05 | 417 | 0.0072 | -10558.0000 |
