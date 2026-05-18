# Side/Regime Diagnostic

- run_count: 4
- selected_count: 8689
- total_counterfactual_pnl_cents: 81251.0000
- stable_positive_rules: 0
- conclusion: No predeclared side/regime diagnostic rule is positive in every supplied run.

## Rule Summary

| rule | positive_runs | selected | total_pnl_cents | min_run_pnl_cents | stable_positive |
|---|---:|---:|---:|---:|---|
| base | 3/4 | 8689 | 81251.0000 | -1160.0000 | False |
| skip_late_300s_against_consensus_05 | 2/4 | 6588 | 73154.0000 | -4350.0000 | False |
| skip_against_consensus_20 | 2/4 | 5273 | 65785.0000 | -11958.0000 | False |
| skip_against_consensus_10 | 2/4 | 4343 | 52943.0000 | -17255.0000 | False |
| skip_against_consensus_05 | 2/4 | 3646 | 48188.0000 | -10098.0000 | False |
| skip_against_consensus_any | 2/4 | 2818 | 38721.0000 | -7139.0000 | False |
| require_current_agreement | 2/4 | 2785 | 37415.0000 | -7088.0000 | False |
| require_market_agreement | 2/4 | 1998 | 25808.0000 | -2733.0000 | False |
| require_market_current_consensus_alignment | 2/4 | 1965 | 24502.0000 | -2682.0000 | False |

## Buckets

| type | bucket | selected | win_rate | total_pnl_cents | avg_pnl_cents |
|---|---|---:|---:|---:|---:|
| side | no | 6567 | 0.4545 | 48358.0000 | 7.3638 |
| side | yes | 2122 | 0.4147 | 32893.0000 | 15.5009 |
| consensus | against_market_current | 5871 | 0.2848 | 42530.0000 | 7.2441 |
| consensus | aligned_with_market_current | 1965 | 0.8382 | 24502.0000 | 12.4692 |
| consensus | market_current_disagree | 853 | 0.6401 | 14219.0000 | 16.6694 |
| confidence | against_strong_05pp_consensus | 697 | 0.4405 | 4755.0000 | 6.8221 |
| confidence | against_strong_10pp_consensus | 930 | 0.4430 | 12842.0000 | 13.8086 |
| confidence | against_strong_20pp_consensus | 3416 | 0.1449 | 15466.0000 | 4.5275 |
| confidence | aligned_consensus | 1965 | 0.8382 | 24502.0000 | 12.4692 |
| confidence | mixed_or_weak | 1681 | 0.5973 | 23686.0000 | 14.0904 |
| time_to_close | 000_060s | 262 | 0.2099 | 1227.0000 | 4.6832 |
| time_to_close | 061_180s | 1050 | 0.2019 | 7296.0000 | 6.9486 |
| time_to_close | 181_300s | 1213 | 0.2333 | 5346.0000 | 4.4073 |
| time_to_close | 301_600s | 3344 | 0.5194 | 42160.0000 | 12.6077 |
| time_to_close | gt_600s | 2820 | 0.5596 | 25222.0000 | 8.9440 |

## Rule By Run

| run | rule | selected | win_rate | pnl_cents |
|---|---|---:|---:|---:|
| particle_side_safety_oos_20260511TLOCKED | base | 2941 | 0.6025 | 39779.0000 |
| particle_side_safety_oos_20260511TLOCKED | require_market_agreement | 1252 | 0.8778 | 16962.0000 |
| particle_side_safety_oos_20260511TLOCKED | require_current_agreement | 1539 | 0.8363 | 22187.0000 |
| particle_side_safety_oos_20260511TLOCKED | require_market_current_consensus_alignment | 1239 | 0.8765 | 16396.0000 |
| particle_side_safety_oos_20260511TLOCKED | skip_against_consensus_any | 1552 | 0.8376 | 22753.0000 |
| particle_side_safety_oos_20260511TLOCKED | skip_against_consensus_05 | 1812 | 0.8135 | 28998.0000 |
| particle_side_safety_oos_20260511TLOCKED | skip_against_consensus_10 | 1976 | 0.8021 | 34116.0000 |
| particle_side_safety_oos_20260511TLOCKED | skip_against_consensus_20 | 2236 | 0.7509 | 36016.0000 |
| particle_side_safety_oos_20260511TLOCKED | skip_late_300s_against_consensus_05 | 2251 | 0.7757 | 42972.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | base | 2884 | 0.4591 | 39334.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | require_market_agreement | 551 | 0.8621 | 11579.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | require_current_agreement | 814 | 0.8686 | 22316.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | require_market_current_consensus_alignment | 532 | 0.8571 | 10788.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | skip_against_consensus_any | 833 | 0.8715 | 23107.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | skip_against_consensus_05 | 1131 | 0.8143 | 29288.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | skip_against_consensus_10 | 1428 | 0.7738 | 36082.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | skip_against_consensus_20 | 1628 | 0.7543 | 41727.0000 |
| particle_dynamic_oos_20260511TLOCKEDNEXT | skip_late_300s_against_consensus_05 | 2168 | 0.5664 | 34828.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | base | 2690 | 0.2859 | 3298.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | require_market_agreement | 195 | 0.5385 | -2733.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | require_current_agreement | 432 | 0.3866 | -7088.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | require_market_current_consensus_alignment | 194 | 0.5412 | -2682.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | skip_against_consensus_any | 433 | 0.3857 | -7139.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | skip_against_consensus_05 | 703 | 0.3642 | -10098.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | skip_against_consensus_10 | 939 | 0.2854 | -17255.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | skip_against_consensus_20 | 1409 | 0.3286 | -11958.0000 |
| particle_dynamic600_oos_20260511TLOCKEDNEXT2 | skip_late_300s_against_consensus_05 | 2138 | 0.3054 | -4350.0000 |
| particle_shadow_readonly_fresh_20260511T113926Z | base | 174 | 0.0000 | -1160.0000 |
| particle_shadow_readonly_fresh_20260511T113926Z | require_market_agreement | 0 | 0.0000 | 0.0000 |
| particle_shadow_readonly_fresh_20260511T113926Z | require_current_agreement | 0 | 0.0000 | 0.0000 |
| particle_shadow_readonly_fresh_20260511T113926Z | require_market_current_consensus_alignment | 0 | 0.0000 | 0.0000 |
| particle_shadow_readonly_fresh_20260511T113926Z | skip_against_consensus_any | 0 | 0.0000 | 0.0000 |
| particle_shadow_readonly_fresh_20260511T113926Z | skip_against_consensus_05 | 0 | 0.0000 | 0.0000 |
| particle_shadow_readonly_fresh_20260511T113926Z | skip_against_consensus_10 | 0 | 0.0000 | 0.0000 |
| particle_shadow_readonly_fresh_20260511T113926Z | skip_against_consensus_20 | 0 | 0.0000 | 0.0000 |
| particle_shadow_readonly_fresh_20260511T113926Z | skip_late_300s_against_consensus_05 | 31 | 0.0000 | -296.0000 |
