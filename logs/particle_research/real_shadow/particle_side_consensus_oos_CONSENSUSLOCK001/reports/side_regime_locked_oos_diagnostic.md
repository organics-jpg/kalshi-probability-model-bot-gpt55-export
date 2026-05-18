# Side/Regime Diagnostic

- run_count: 1
- selected_count: 3029
- total_counterfactual_pnl_cents: -32502.0000
- stable_positive_rules: 6
- conclusion: At least one diagnostic rule is positive in every supplied run; treat it as a candidate for a fresh locked OOS plan, not as promotion evidence.

## Rule Summary

| rule | positive_runs | selected | total_pnl_cents | min_run_pnl_cents | stable_positive |
|---|---:|---:|---:|---:|---|
| skip_against_consensus_05 | 1/1 | 193 | 2769.0000 | 2769.0000 | True |
| require_current_agreement | 1/1 | 104 | 2490.0000 | 2490.0000 | True |
| skip_against_consensus_any | 1/1 | 104 | 2490.0000 | 2490.0000 | True |
| skip_against_consensus_10 | 1/1 | 429 | 1447.0000 | 1447.0000 | True |
| require_market_agreement | 1/1 | 50 | 824.0000 | 824.0000 | True |
| require_market_current_consensus_alignment | 1/1 | 50 | 824.0000 | 824.0000 | True |
| skip_against_consensus_20 | 0/1 | 932 | -10762.0000 | -10762.0000 | False |
| skip_late_300s_against_consensus_05 | 0/1 | 2235 | -29552.0000 | -29552.0000 | False |
| base | 0/1 | 3029 | -32502.0000 | -32502.0000 | False |

## Buckets

| type | bucket | selected | win_rate | total_pnl_cents | avg_pnl_cents |
|---|---|---:|---:|---:|---:|
| side | no | 1098 | 0.2450 | 3907.0000 | 3.5583 |
| side | yes | 1931 | 0.0000 | -36409.0000 | -18.8550 |
| consensus | against_market_current | 2925 | 0.0653 | -34992.0000 | -11.9631 |
| consensus | aligned_with_market_current | 50 | 0.7400 | 824.0000 | 16.4800 |
| consensus | market_current_disagree | 54 | 0.7593 | 1666.0000 | 30.8519 |
| confidence | against_strong_05pp_consensus | 236 | 0.3814 | -1322.0000 | -5.6017 |
| confidence | against_strong_10pp_consensus | 503 | 0.1054 | -12209.0000 | -24.2724 |
| confidence | against_strong_20pp_consensus | 2097 | 0.0024 | -21740.0000 | -10.3672 |
| confidence | aligned_consensus | 50 | 0.7400 | 824.0000 | 16.4800 |
| confidence | mixed_or_weak | 143 | 0.5874 | 1945.0000 | 13.6014 |
| time_to_close | 000_060s | 75 | 0.0267 | -329.0000 | -4.3867 |
| time_to_close | 061_180s | 338 | 0.1095 | -899.0000 | -2.6598 |
| time_to_close | 181_300s | 436 | 0.0000 | -1660.0000 | -3.8073 |
| time_to_close | 301_600s | 1064 | 0.0141 | -18010.0000 | -16.9267 |
| time_to_close | gt_600s | 1116 | 0.1927 | -11604.0000 | -10.3978 |

## Rule By Run

| run | rule | selected | win_rate | pnl_cents |
|---|---|---:|---:|---:|
| particle_side_consensus_oos_CONSENSUSLOCK001 | base | 3029 | 0.0888 | -32502.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | require_market_agreement | 50 | 0.7400 | 824.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | require_current_agreement | 104 | 0.7500 | 2490.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | require_market_current_consensus_alignment | 50 | 0.7400 | 824.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | skip_against_consensus_any | 104 | 0.7500 | 2490.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | skip_against_consensus_05 | 193 | 0.6269 | 2769.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | skip_against_consensus_10 | 429 | 0.4918 | 1447.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | skip_against_consensus_20 | 932 | 0.2833 | -10762.0000 |
| particle_side_consensus_oos_CONSENSUSLOCK001 | skip_late_300s_against_consensus_05 | 2235 | 0.1141 | -29552.0000 |
