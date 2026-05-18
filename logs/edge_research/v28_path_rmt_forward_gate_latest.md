# v28 Path/RMT Fresh Forward Gate

Fresh freeze for the current best path/RMT challenger. Discovery rows before this timestamp do not count.

- Freeze timestamp UTC: `2026-05-06T00:38:39.999269+00:00`
- Forward denominator/base entries: `147/145`
- Excluded in-progress post-freeze markets: `1`
- Any promotable: `False`
- Future clean markets needed for denominator 10: `0`
- Future clean markets needed for denominator 30: `0`

## Policies

- `weakraw_rmt_memory_margin02_wait240_or_opp`: When raw v28 is below 60%, require at least 2pp RMT/book edge after 240s or follow a later opposite v28 approval.
- `weakraw_rmt_repetition_margin02_wait240_or_opp`: Same weak-raw uncertainty gate, using repetition-forgetting probability as the RMT edge check.
- `v28_raw_p50_edge0_base`: Fresh same-window baseline: first raw-v28 p>=0.50 nonnegative-edge side per clean market.
- `selective_rmt_memory_gap_wait240_rmtedge02_or_opp`: For fragile early raw-v28 rows, either require same-side RMT/book edge after 240s or follow a later opposite v28 approval.
- `selective_rmt_repetition_gap_wait240_rmtedge02_or_opp`: Same path rule, using repetition-forgetting probability as the RMT edge check.

## Forward Scorecard

| policy | entries | settled | W/L | actual/sim | sim share | coverage | net c | brier | net vs base | brier vs base | promotable | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| weakraw_rmt_memory_margin02_wait240_or_opp | 85 | 85 | 52/33 | 18/67 | 0.788235 | 57.823129 | -942.000000 | 0.237231 | -85.000000 | -0.001637 | False | simulated_share_gt_0.35, coverage_too_low, net_not_positive, brier_delta_not_negative, logloss_delta_not_negative |
| weakraw_rmt_repetition_margin02_wait240_or_opp | 85 | 85 | 52/33 | 18/67 | 0.788235 | 57.823129 | -942.000000 | 0.237231 | -85.000000 | -0.001637 | False | simulated_share_gt_0.35, coverage_too_low, net_not_positive, brier_delta_not_negative, logloss_delta_not_negative |
| v28_raw_p50_edge0_base | 145 | 145 | 81/64 | 7/138 | 0.951724 | 98.639456 | -857.000000 | 0.238868 | 0.000000 | 0.000000 | False | simulated_share_gt_0.35, coverage_too_high, net_not_positive, brier_delta_not_negative, logloss_delta_not_negative |
| selective_rmt_memory_gap_wait240_rmtedge02_or_opp | 128 | 128 | 76/52 | 12/116 | 0.906250 | 87.074830 | -456.000000 | 0.230765 | 401.000000 | -0.008102 | False | simulated_share_gt_0.35, net_not_positive, brier_delta_not_negative, logloss_delta_not_negative |
| selective_rmt_repetition_gap_wait240_rmtedge02_or_opp | 132 | 132 | 75/57 | 10/122 | 0.924242 | 89.795918 | -986.000000 | 0.237880 | -129.000000 | -0.000987 | False | simulated_share_gt_0.35, net_not_positive, brier_delta_not_negative, logloss_delta_not_negative |

## Candidate Runway

| policy | settled rows to 30 | actual entries needed for sim share <=35% |
|---|---:|---:|
| weakraw_rmt_memory_margin02_wait240_or_opp | 0 | 107 |
| weakraw_rmt_repetition_margin02_wait240_or_opp | 0 | 107 |
| v28_raw_p50_edge0_base | 0 | 250 |
| selective_rmt_memory_gap_wait240_rmtedge02_or_opp | 0 | 204 |
| selective_rmt_repetition_gap_wait240_rmtedge02_or_opp | 0 | 217 |
