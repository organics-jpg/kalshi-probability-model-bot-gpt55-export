# v28 Early-Clock Wait Bakeoff

Research-only; no live bot changes and no orders.

- Best policy: `all_early_wait480_p50_opposite_side_delay480`
- Policy count: `576`
- Forward denominator: `152`

## Interpretation

- Best early-clock wait policy is all_early_wait480_p50_opposite_side_delay480 with net 615.0c.
- Target net was -606.0c; delta 1221.0c.
- This is discovery-only. Any viable row needs a frozen forward validator before promotion.

## Top Policies

| policy | entries | settled | W/L | coverage | net c | delta c | danger net | repl net | repair net | LOO worst | LOO neg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `all_early_wait480_p50_opposite_side_delay480` | 114 | 114 | 85/29 | 75.000000 | 615.000000 | 1221.000000 | -794.000000 | 238.000000 | 189.000000 | 1046.000000 | 0 |
| `all_early_wait480_p55_opposite_side_delay480` | 114 | 114 | 85/29 | 75.000000 | 594.000000 | 1200.000000 | -794.000000 | 217.000000 | 189.000000 | 1025.000000 | 0 |
| `all_early_wait480_p55_any_side_delay480` | 114 | 114 | 83/31 | 75.000000 | 514.000000 | 1120.000000 | -794.000000 | 352.000000 | -26.000000 | 945.000000 | 0 |
| `all_early_wait480_p50_any_side_delay480` | 114 | 114 | 82/32 | 75.000000 | 503.000000 | 1109.000000 | -794.000000 | 357.000000 | -42.000000 | 934.000000 | 0 |
| `all_early_wait660_p60_opposite_side_delay240` | 114 | 114 | 84/30 | 75.000000 | 494.000000 | 1100.000000 | -794.000000 | 121.000000 | 185.000000 | 933.000000 | 0 |
| `all_early_wait480_p60_any_side_delay480` | 114 | 114 | 84/30 | 75.000000 | 494.000000 | 1100.000000 | -794.000000 | 352.000000 | -46.000000 | 925.000000 | 0 |
| `all_early_wait480_p50_any_side_delay360` | 114 | 114 | 84/30 | 75.000000 | 493.000000 | 1099.000000 | -794.000000 | 44.000000 | 261.000000 | 931.000000 | 0 |
| `all_early_wait480_p50_opposite_side_delay360` | 114 | 114 | 84/30 | 75.000000 | 493.000000 | 1099.000000 | -794.000000 | 44.000000 | 261.000000 | 931.000000 | 0 |
| `all_early_wait480_p55_any_side_delay360` | 114 | 114 | 84/30 | 75.000000 | 493.000000 | 1099.000000 | -794.000000 | 44.000000 | 261.000000 | 931.000000 | 0 |
| `all_early_wait480_p55_opposite_side_delay360` | 114 | 114 | 84/30 | 75.000000 | 493.000000 | 1099.000000 | -794.000000 | 44.000000 | 261.000000 | 931.000000 | 0 |
| `all_early_wait660_p55_opposite_side_delay240` | 114 | 114 | 83/31 | 75.000000 | 487.000000 | 1093.000000 | -794.000000 | 183.000000 | 116.000000 | 926.000000 | 0 |
| `all_early_wait600_p50_opposite_side_delay240` | 114 | 114 | 84/30 | 75.000000 | 469.000000 | 1075.000000 | -794.000000 | 18.000000 | 263.000000 | 924.000000 | 0 |

## Best Cases

| market | target side | target won | target net | stc | abs d | recross | repl side | repl won | repl net | delay |
|---|---|---|---:|---:|---:|---:|---|---|---:|---:|
| KXBTC15M-26MAY052015-15 | no | False | -102.000000 | 873.050000 | 0.150360 | 0.945709 | None | None | None | None |
| KXBTC15M-26MAY052030-30 | yes | False | -98.000000 | 879.629000 | 0.144729 | 1.053237 | None | None | None | None |
| KXBTC15M-26MAY052100-00 | yes | True | 104.000000 | 808.178000 | 0.155800 | 0.915520 | None | None | None | None |
| KXBTC15M-26MAY052115-15 | yes | True | 90.000000 | 850.512000 | 0.195783 | 0.945077 | None | None | None | None |
| KXBTC15M-26MAY052215-15 | no | True | 43.000000 | 819.362000 | 0.740524 | 0.558639 | None | None | None | None |
| KXBTC15M-26MAY052345-45 | no | True | 70.000000 | 850.023000 | 0.275785 | 0.899454 | None | None | None | None |
| KXBTC15M-26MAY060030-30 | yes | False | -106.000000 | 853.033000 | 0.270552 | 0.831869 | no | True | 49.000000 | 403.202567 |
| KXBTC15M-26MAY060045-45 | no | True | 39.000000 | 818.779000 | 0.802399 | 0.461756 | None | None | None | None |
| KXBTC15M-26MAY060130-30 | no | True | 78.000000 | 849.758000 | 0.294972 | 0.777744 | None | None | None | None |
| KXBTC15M-26MAY060200-00 | yes | True | 76.000000 | 849.377000 | 0.248684 | 0.767680 | None | None | None | None |
| KXBTC15M-26MAY060215-15 | yes | False | -110.000000 | 884.651000 | 0.228362 | 0.792609 | no | True | 38.000000 | 458.061569 |
| KXBTC15M-26MAY060245-45 | no | False | -134.000000 | 868.740000 | 0.346255 | 0.663720 | yes | True | 20.000000 | 400.000638 |
| KXBTC15M-26MAY060300-00 | yes | True | 68.000000 | 869.393000 | 0.396112 | 0.620295 | None | None | None | None |
| KXBTC15M-26MAY060330-30 | no | False | -118.000000 | 884.146000 | 0.287388 | 0.689280 | yes | True | 15.000000 | 448.075636 |
| KXBTC15M-26MAY060345-45 | yes | False | -80.000000 | 868.842000 | 0.064212 | 0.911219 | None | None | None | None |
| KXBTC15M-26MAY060415-15 | yes | True | 62.000000 | 792.955000 | 0.394255 | 0.625830 | None | None | None | None |
| KXBTC15M-26MAY060445-45 | no | False | -94.000000 | 864.716000 | 0.322198 | 0.666569 | None | None | None | None |
| KXBTC15M-26MAY060500-00 | no | False | -126.000000 | 783.254000 | 0.377919 | 0.620318 | None | None | None | None |
| KXBTC15M-26MAY060515-15 | yes | False | -86.000000 | 825.119000 | 0.141500 | 0.958625 | None | None | None | None |
| KXBTC15M-26MAY060530-30 | yes | False | -112.000000 | 829.016000 | 0.202598 | 0.884715 | None | None | None | None |
