# v28 Raw p52 Middle-Confidence Early-NO Boundary Skip

Discovery diagnostic only. Frozen validator fixes this rule before forward validation.

- Base policy: `v28_raw_p52_edge0`
- Candidate: `raw_p52_skip_midconf_early_no_boundary`
- Rule: `Start from v28_raw_p52_edge0 and skip NO rows with 0.62<=p<0.70, stc>=720, abs_d<=0.45, recross>=0.55.`
- Watched markets: `181`
- Delta vs base: `562.000000c`

## Summary

| row | entries | settled | W/L | coverage | win rate | avg p | avg ask | avg abs d | avg recross | net c | actual/sim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base | 169 | 169 | 104/65 | 93.370166 | 0.615385 | 0.644300 | 0.586036 | 0.353552 | 0.771407 | 71.000000 | 12/157 |
| candidate_summary | 156 | 156 | 99/57 | 86.187845 | 0.634615 | 0.643745 | 0.586474 | 0.353545 | 0.770455 | 633.000000 | 12/144 |
| skipped_summary | 13 | 13 | 5/8 | 7.182320 | 0.384615 | 0.650963 | 0.580769 | 0.353635 | 0.782828 | -562.000000 | 0/13 |

## Skipped Rows

| market | side | source | p | ask | stc | abs d | recross | won | net c |
|---|---|---|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY052245-45 | no | rejected_actionable | 0.643789 | 0.570000 | 752.490000 | 0.362082 | 0.663374 | False | -118.000000 |
| KXBTC15M-26MAY052345-45 | no | rejected_actionable | 0.636767 | 0.630000 | 850.023000 | 0.275785 | 0.899454 | True | 70.000000 |
| KXBTC15M-26MAY060245-45 | no | rejected_actionable | 0.660829 | 0.650000 | 868.740000 | 0.346255 | 0.663720 | False | -134.000000 |
| KXBTC15M-26MAY060330-30 | no | rejected_actionable | 0.630880 | 0.570000 | 884.146000 | 0.287388 | 0.689280 | False | -118.000000 |
| KXBTC15M-26MAY060445-45 | no | rejected_actionable | 0.636374 | 0.450000 | 864.716000 | 0.322198 | 0.666569 | False | -94.000000 |
| KXBTC15M-26MAY060500-00 | no | rejected_actionable | 0.674136 | 0.610000 | 783.254000 | 0.377919 | 0.620318 | False | -126.000000 |
| KXBTC15M-26MAY060545-45 | no | rejected_actionable | 0.626642 | 0.440000 | 807.560000 | 0.323422 | 0.689053 | False | -92.000000 |
| KXBTC15M-26MAY060630-30 | no | rejected_actionable | 0.675344 | 0.660000 | 868.927000 | 0.393798 | 0.762043 | False | -136.000000 |
| KXBTC15M-26MAY060915-15 | no | rejected_actionable | 0.672099 | 0.600000 | 869.636000 | 0.431641 | 0.831637 | True | 76.000000 |
| KXBTC15M-26MAY061000-00 | no | rejected_actionable | 0.661616 | 0.540000 | 864.383000 | 0.399973 | 0.985410 | True | 88.000000 |
| KXBTC15M-26MAY062215-15 | no | rejected_actionable | 0.661831 | 0.590000 | 850.282000 | 0.404187 | 0.669869 | True | 78.000000 |
| KXBTC15M-26MAY071030-30 | no | rejected_actionable | 0.646380 | 0.620000 | 852.539000 | 0.326478 | 1.053270 | True | 72.000000 |
| KXBTC15M-26MAY071115-15 | no | rejected_actionable | 0.635838 | 0.620000 | 843.330000 | 0.346131 | 0.982771 | False | -128.000000 |
