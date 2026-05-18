# v28 Weak-Boundary Reversal Strategy

Research-only; no live bot changes and no orders.

- Requirements: `{'p_max': 0.6, 'recross_floor': 0.75, 'abs_d_max': 0.3, 'max_opposite_delay_seconds': 240.0, 'coverage_floor': 75.0}`
- Delta vs target: `-698.000000c`
- Coverage repaired: `True`

## Interpretation

- Weak-boundary rows removed: 27; opposite replacements found: 14.
- Repair rows added: 15.
- Target net -606.0c; candidate net -1304.0c; coverage 75.0%.
- This is diagnostic only; any viable version requires frozen forward validation.

## Summaries

| slice | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| target | 112 | 112 | 64/48 | 73.684211 | -606.000000 | -5.410714 |
| weak_removed | 27 | 27 | 15/12 | 17.763158 | 358.000000 | 13.259259 |
| kept | 85 | 85 | 49/36 | 55.921053 | -964.000000 | -11.341176 |
| opposite_replacements | 14 | 14 | 6/8 | 9.210526 | -258.000000 | -18.428571 |
| repairs | 15 | 15 | 11/4 | 9.868421 | -82.000000 | -5.466667 |
| candidate | 114 | 114 | 66/48 | 75.000000 | -1304.000000 | -11.438596 |

## Reversal Cases

| market | target side | target won | target net | p | recross | abs d | repl side | repl won | repl net | delay |
|---|---|---|---:|---:|---:|---:|---|---|---:|---:|
| KXBTC15M-26MAY052015-15 | no | False | -102.000000 | 0.567861 | 0.945709 | 0.150360 | yes | True | 13.000000 | 185.005681 |
| KXBTC15M-26MAY052030-30 | yes | False | -98.000000 | 0.540780 | 1.053237 | 0.144729 | no | True | 60.000000 | 56.860804 |
| KXBTC15M-26MAY052100-00 | yes | True | 104.000000 | 0.565554 | 0.915520 | 0.155800 | no | False | -77.000000 | 71.289827 |
| KXBTC15M-26MAY052115-15 | yes | True | 90.000000 | 0.571476 | 0.945077 | 0.195783 | None | None | None | None |
| KXBTC15M-26MAY060215-15 | yes | False | -110.000000 | 0.583024 | 0.792609 | 0.228362 | None | None | None | None |
| KXBTC15M-26MAY060345-45 | yes | False | -80.000000 | 0.515105 | 0.911219 | 0.064212 | no | True | 30.000000 | 120.589387 |
| KXBTC15M-26MAY060515-15 | yes | False | -86.000000 | 0.532512 | 0.958625 | 0.141500 | no | True | 23.000000 | 20.345791 |
| KXBTC15M-26MAY060530-30 | yes | False | -112.000000 | 0.588889 | 0.884715 | 0.202598 | no | True | 51.000000 | 209.480591 |
| KXBTC15M-26MAY060645-45 | yes | True | 78.000000 | 0.598639 | 0.856108 | 0.277816 | None | None | None | None |
| KXBTC15M-26MAY060730-30 | yes | True | 84.000000 | 0.594884 | 0.863859 | 0.270357 | None | None | None | None |
| KXBTC15M-26MAY060800-00 | yes | True | 102.000000 | 0.523411 | 1.358871 | 0.027808 | None | None | None | None |
| KXBTC15M-26MAY061015-15 | no | True | 92.000000 | 0.595554 | 1.130150 | 0.274143 | None | None | None | None |
| KXBTC15M-26MAY061700-00 | no | False | -102.000000 | 0.547299 | 0.799916 | 0.145303 | None | None | None | None |
| KXBTC15M-26MAY061900-00 | yes | True | 128.000000 | 0.501794 | 0.794136 | 0.001392 | no | False | -49.000000 | 199.557428 |
| KXBTC15M-26MAY061930-30 | yes | True | 102.000000 | 0.551364 | 0.905378 | 0.100563 | no | False | -28.000000 | 185.774036 |
| KXBTC15M-26MAY061945-45 | yes | False | -88.000000 | 0.542407 | 0.801256 | 0.132650 | no | True | 36.000000 | 41.551488 |
| KXBTC15M-26MAY062130-30 | yes | True | 114.000000 | 0.586142 | 0.800157 | 0.212967 | no | False | -78.000000 | 125.028005 |
| KXBTC15M-26MAY070030-30 | no | False | -70.000000 | 0.523605 | 0.901651 | 0.059362 | None | None | None | None |
| KXBTC15M-26MAY070045-45 | no | True | 100.000000 | 0.582164 | 0.830545 | 0.187292 | yes | False | -81.000000 | 104.422902 |
| KXBTC15M-26MAY070530-30 | no | True | 100.000000 | 0.540822 | 0.894668 | 0.132673 | yes | False | -67.000000 | 122.215913 |
| KXBTC15M-26MAY070715-15 | yes | True | 94.000000 | 0.560435 | 0.877232 | 0.157545 | None | None | None | None |
| KXBTC15M-26MAY070730-30 | yes | False | -96.000000 | 0.530778 | 0.936121 | 0.091964 | None | None | None | None |
| KXBTC15M-26MAY070800-00 | yes | False | -94.000000 | 0.536385 | 0.865475 | 0.080069 | None | None | None | None |
| KXBTC15M-26MAY070815-15 | yes | True | 108.000000 | 0.501147 | 1.067161 | 0.024626 | no | False | -33.000000 | 155.526452 |
| KXBTC15M-26MAY070830-30 | yes | False | -86.000000 | 0.514492 | 0.952791 | 0.078942 | None | None | None | None |
| KXBTC15M-26MAY070900-00 | yes | True | 86.000000 | 0.597604 | 0.771689 | 0.238237 | no | False | -58.000000 | 20.032774 |
| KXBTC15M-26MAY070945-45 | no | True | 100.000000 | 0.532085 | 1.088863 | 0.067417 | None | None | None | None |
