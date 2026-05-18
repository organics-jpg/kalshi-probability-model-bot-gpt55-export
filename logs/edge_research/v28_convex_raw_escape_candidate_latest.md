# v28 Convex Raw-Escape Candidate

Use raw broad only when raw edge is >= 20pp; otherwise use p60 forgetting candidate.

- Watched markets: `181`
- Raw edge escape min: `0.2`

## Summary

| policy | entries | settled | wins/losses | coverage | net c | avg net c | brier | raw escape | wait | actual/shadow |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| raw_edge20_else_first_side_p60 | 172 | 172 | 96/76 | 95.027624 | -3438.000000 | -19.988372 | 0.237947 | 11 | 158 | 7/165 |
| raw_edge20_else_rmt_p60 | 172 | 172 | 100/72 | 95.027624 | -2907.000000 | -16.901163 | 0.231586 | 11 | 158 | 7/165 |

## Recent Rows

| meta | market | reason | side | p_eff | ask | edge | won | net c |
|---|---|---|---|---:|---:|---:|---|---:|
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070730-30 | use_wait_policy | yes | 0.800000 | 0.800000 | 0.000000 | False | -163.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070745-45 | raw_high_convex_edge | yes | 0.903807 | 0.680000 | 0.223807 | True | 32.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070800-00 | wait_missing_use_raw | yes | 0.536385 | 0.450000 | 0.086385 | False | -94.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070815-15 | use_wait_policy | yes | 0.720000 | 0.720000 | 0.000000 | True | 53.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070830-30 | use_wait_policy | no | 0.660000 | 0.660000 | 0.000000 | True | 32.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070845-45 | use_wait_policy | yes | 0.650000 | 0.650000 | 0.000000 | True | 66.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070900-00 | use_wait_policy | no | 0.600000 | 0.600000 | 0.000000 | False | -124.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070915-15 | use_wait_policy | no | 0.769000 | 0.750000 | 0.019000 | True | 47.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070930-30 | use_wait_policy | no | 0.620000 | 0.620000 | 0.000000 | False | -128.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070945-45 | use_wait_policy | no | 0.640000 | 0.640000 | 0.000000 | True | 68.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071000-00 | use_wait_policy | no | 0.660000 | 0.660000 | 0.000000 | True | 64.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071015-15 | use_wait_policy | no | 0.604947 | 0.600000 | 0.004947 | False | -124.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071030-30 | use_wait_policy | no | 0.633190 | 0.620000 | 0.013190 | True | 72.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071045-45 | use_wait_policy | no | 0.730000 | 0.730000 | 0.000000 | True | 51.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071100-00 | use_wait_policy | yes | 0.650000 | 0.650000 | 0.000000 | False | -134.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071115-15 | use_wait_policy | no | 0.620000 | 0.620000 | 0.000000 | False | -128.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071130-30 | use_wait_policy | yes | 0.600000 | 0.600000 | 0.000000 | False | -124.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071145-45 | use_wait_policy | yes | 0.627819 | 0.610000 | 0.017819 | True | 74.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071200-00 | use_wait_policy | yes | 0.630000 | 0.630000 | 0.000000 | False | -130.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071215-15 | use_wait_policy | yes | 0.600000 | 0.600000 | 0.000000 | False | -124.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071230-30 | use_wait_policy | no | 0.700000 | 0.700000 | 0.000000 | False | -143.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071245-45 | use_wait_policy | yes | 0.650000 | 0.650000 | 0.000000 | False | -134.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071300-00 | use_wait_policy | yes | 0.613020 | 0.590000 | 0.023020 | False | -122.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071315-15 | use_wait_policy | yes | 0.700000 | 0.700000 | 0.000000 | True | 57.000000 |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071330-30 | use_wait_policy | no | 0.650000 | 0.650000 | 0.000000 | True | 66.000000 |
