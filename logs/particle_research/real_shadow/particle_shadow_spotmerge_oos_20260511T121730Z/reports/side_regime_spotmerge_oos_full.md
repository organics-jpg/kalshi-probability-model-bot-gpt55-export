# Side/Regime Diagnostic

- run_count: 1
- selected_count: 649
- total_counterfactual_pnl_cents: -4638.0000
- stable_positive_rules: 3
- conclusion: At least one diagnostic rule is positive in every supplied run; treat it as a candidate for a fresh locked OOS plan, not as promotion evidence.

## Rule Summary

| rule | positive_runs | selected | total_pnl_cents | min_run_pnl_cents | stable_positive |
|---|---:|---:|---:|---:|---|
| skip_against_consensus_10 | 1/1 | 183 | 356.0000 | 356.0000 | True |
| require_market_agreement | 1/1 | 9 | 224.0000 | 224.0000 | True |
| require_market_current_consensus_alignment | 1/1 | 9 | 224.0000 | 224.0000 | True |
| skip_against_consensus_05 | 0/1 | 81 | -352.0000 | -352.0000 | False |
| require_current_agreement | 0/1 | 41 | -626.0000 | -626.0000 | False |
| skip_against_consensus_any | 0/1 | 41 | -626.0000 | -626.0000 | False |
| skip_against_consensus_20 | 0/1 | 303 | -2406.0000 | -2406.0000 | False |
| skip_late_300s_against_consensus_05 | 0/1 | 522 | -4551.0000 | -4551.0000 | False |
| base | 0/1 | 649 | -4638.0000 | -4638.0000 | False |

## Buckets

| type | bucket | selected | win_rate | total_pnl_cents | avg_pnl_cents |
|---|---|---:|---:|---:|---:|
| side | no | 645 | 0.1612 | -4735.0000 | -7.3411 |
| side | yes | 4 | 0.7500 | 97.0000 | 24.2500 |
| consensus | against_market_current | 608 | 0.1530 | -4012.0000 | -6.5987 |
| consensus | aligned_with_market_current | 9 | 0.7778 | 224.0000 | 24.8889 |
| consensus | market_current_disagree | 32 | 0.2188 | -850.0000 | -26.5625 |
| confidence | against_strong_05pp_consensus | 102 | 0.4608 | 708.0000 | 6.9412 |
| confidence | against_strong_10pp_consensus | 120 | 0.1250 | -2762.0000 | -23.0167 |
| confidence | against_strong_20pp_consensus | 346 | 0.0318 | -2232.0000 | -6.4509 |
| confidence | aligned_consensus | 9 | 0.7778 | 224.0000 | 24.8889 |
| confidence | mixed_or_weak | 72 | 0.3750 | -576.0000 | -8.0000 |
| time_to_close | 061_180s | 23 | 0.0000 | 0.0000 | 0.0000 |
| time_to_close | 181_300s | 104 | 0.0000 | -87.0000 | -0.8365 |
| time_to_close | 301_600s | 286 | 0.0000 | -6242.0000 | -21.8252 |
| time_to_close | gt_600s | 236 | 0.4534 | 1691.0000 | 7.1653 |

## Rule By Run

| run | rule | selected | win_rate | pnl_cents |
|---|---|---:|---:|---:|
| particle_shadow_spotmerge_oos_20260511T121730Z | base | 649 | 0.1649 | -4638.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | require_market_agreement | 9 | 0.7778 | 224.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | require_current_agreement | 41 | 0.3415 | -626.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | require_market_current_consensus_alignment | 9 | 0.7778 | 224.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | skip_against_consensus_any | 41 | 0.3415 | -626.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | skip_against_consensus_05 | 81 | 0.4198 | -352.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | skip_against_consensus_10 | 183 | 0.4426 | 356.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | skip_against_consensus_20 | 303 | 0.3168 | -2406.0000 |
| particle_shadow_spotmerge_oos_20260511T121730Z | skip_late_300s_against_consensus_05 | 522 | 0.2050 | -4551.0000 |
