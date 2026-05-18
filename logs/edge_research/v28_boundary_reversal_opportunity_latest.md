# v28 Boundary Reversal Opportunity

Diagnostic-only: tests whether high-recross near-strike target rows have later opposite-side replacements.

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Forward denominator: `152`
- Boundary rows/replacements: `42/24`

## Interpretation

- Boundary turbulence rows: 42; rows with same-market opposite replacement: 24.
- Kept non-boundary plus replacements would cover 61.8421052631579% of the forward denominator.
- Some boundary rows have no coherent opposite replacement, so this cannot be treated as a simple replacement rule yet.

## Summaries

| slice | entries | settled | W/L | coverage | net c | avg net c |
|---|---:|---:|---:|---:|---:|---:|
| target | 112 | 112 | 64/48 | 73.684211 | -606.000000 | -5.410714 |
| boundary_only | 42 | 42 | 21/21 | 27.631579 | -238.000000 | -5.666667 |
| replacement_only | 24 | 24 | 14/10 | 15.789474 | -106.000000 | -4.416667 |
| non_boundary_plus_replacement | 94 | 94 | 57/37 | 61.842105 | -474.000000 | -5.042553 |

## Cases

| market | target side | target won | target net | recross | abs d | replacements | chosen side | chosen won | chosen net | delay s |
|---|---|---|---:|---:|---:|---:|---|---|---:|---:|
| KXBTC15M-26MAY052015-15 | no | False | -53.000000 | 0.945709 | 0.150360 | 1 | yes | True | 13.000000 | 185.005681 |
| KXBTC15M-26MAY052030-30 | yes | False | -51.000000 | 1.053237 | 0.144729 | 1 | no | True | 60.000000 | 56.860804 |
| KXBTC15M-26MAY052100-00 | yes | True | 50.000000 | 0.915520 | 0.155800 | 4 | no | False | -77.000000 | 71.289827 |
| KXBTC15M-26MAY052115-15 | yes | True | 43.000000 | 0.945077 | 0.195783 | 0 | None | None | None | None |
| KXBTC15M-26MAY052345-45 | no | True | 33.000000 | 0.899454 | 0.275785 | 1 | yes | False | -55.000000 | 176.987712 |
| KXBTC15M-26MAY060030-30 | yes | False | -55.000000 | 0.831869 | 0.270552 | 0 | None | None | None | None |
| KXBTC15M-26MAY060130-30 | no | True | 37.000000 | 0.777744 | 0.294972 | 0 | None | None | None | None |
| KXBTC15M-26MAY060200-00 | yes | True | 36.000000 | 0.767680 | 0.248684 | 0 | None | None | None | None |
| KXBTC15M-26MAY060215-15 | yes | False | -57.000000 | 0.792609 | 0.228362 | 0 | None | None | None | None |
| KXBTC15M-26MAY060345-45 | yes | False | -42.000000 | 0.911219 | 0.064212 | 3 | no | True | 30.000000 | 120.589387 |
| KXBTC15M-26MAY060515-15 | yes | False | -45.000000 | 0.958625 | 0.141500 | 2 | no | True | 23.000000 | 20.345791 |
| KXBTC15M-26MAY060530-30 | yes | False | -58.000000 | 0.884715 | 0.202598 | 2 | no | True | 51.000000 | 209.480591 |
| KXBTC15M-26MAY060645-45 | yes | True | 37.000000 | 0.856108 | 0.277816 | 0 | None | None | None | None |
| KXBTC15M-26MAY060730-30 | yes | True | 40.000000 | 0.863859 | 0.270357 | 0 | None | None | None | None |
| KXBTC15M-26MAY060800-00 | yes | True | 49.000000 | 1.358871 | 0.027808 | 0 | None | None | None | None |
| KXBTC15M-26MAY060830-30 | no | False | -63.000000 | 0.943700 | 0.286154 | 7 | yes | True | 45.000000 | 40.003445 |
| KXBTC15M-26MAY060930-30 | yes | False | -64.000000 | 1.150583 | 0.244982 | 11 | no | True | 40.000000 | 39.994313 |
| KXBTC15M-26MAY061015-15 | no | True | 44.000000 | 1.130150 | 0.274143 | 0 | None | None | None | None |
| KXBTC15M-26MAY061030-30 | yes | True | 35.000000 | 1.168280 | 0.232373 | 7 | no | False | -54.000000 | 100.035334 |
| KXBTC15M-26MAY061045-45 | no | False | -61.000000 | 1.191443 | 0.212683 | 4 | yes | True | 25.000000 | 280.224557 |
| KXBTC15M-26MAY061700-00 | no | False | -53.000000 | 0.799916 | 0.145303 | 1 | yes | True | 67.000000 | 258.882413 |
| KXBTC15M-26MAY061900-00 | yes | True | 62.000000 | 0.794136 | 0.001392 | 2 | no | False | -49.000000 | 199.557428 |
| KXBTC15M-26MAY061930-30 | yes | True | 49.000000 | 0.905378 | 0.100563 | 1 | no | False | -28.000000 | 185.774036 |
| KXBTC15M-26MAY061945-45 | yes | False | -46.000000 | 0.801256 | 0.132650 | 2 | no | True | 36.000000 | 41.551488 |
| KXBTC15M-26MAY062130-30 | yes | True | 55.000000 | 0.800157 | 0.212967 | 1 | no | False | -78.000000 | 125.028005 |
| KXBTC15M-26MAY062145-45 | yes | True | 39.000000 | 0.820982 | 0.250555 | 0 | None | None | None | None |
| KXBTC15M-26MAY062245-45 | no | False | -58.000000 | 0.786584 | 0.278629 | 2 | yes | True | 9.000000 | 122.774223 |
| KXBTC15M-26MAY070030-30 | no | False | -37.000000 | 0.901651 | 0.059362 | 1 | yes | True | 15.000000 | 313.097001 |
| KXBTC15M-26MAY070045-45 | no | True | 48.000000 | 0.830545 | 0.187292 | 1 | yes | False | -81.000000 | 104.422902 |
| KXBTC15M-26MAY070530-30 | no | True | 48.000000 | 0.894668 | 0.132673 | 1 | yes | False | -67.000000 | 122.215913 |
| KXBTC15M-26MAY070630-30 | yes | False | -51.000000 | 0.826469 | 0.230767 | 0 | None | None | None | None |
| KXBTC15M-26MAY070715-15 | yes | True | 45.000000 | 0.877232 | 0.157545 | 0 | None | None | None | None |
| KXBTC15M-26MAY070730-30 | yes | False | -50.000000 | 0.936121 | 0.091964 | 0 | None | None | None | None |
| KXBTC15M-26MAY070800-00 | yes | False | -49.000000 | 0.865475 | 0.080069 | 0 | None | None | None | None |
| KXBTC15M-26MAY070815-15 | yes | True | 52.000000 | 1.067161 | 0.024626 | 1 | no | False | -33.000000 | 155.526452 |
| KXBTC15M-26MAY070830-30 | yes | False | -45.000000 | 0.952791 | 0.078942 | 1 | no | True | 16.000000 | 242.386234 |
| KXBTC15M-26MAY070900-00 | yes | True | 41.000000 | 0.771689 | 0.238237 | 10 | no | False | -58.000000 | 20.032774 |
| KXBTC15M-26MAY070945-45 | no | True | 48.000000 | 1.088863 | 0.067417 | 0 | None | None | None | None |
| KXBTC15M-26MAY071015-15 | no | False | -64.000000 | 1.102864 | 0.287274 | 0 | None | None | None | None |
| KXBTC15M-26MAY071145-45 | yes | True | 35.000000 | 1.101255 | 0.285653 | 0 | None | None | None | None |
| KXBTC15M-26MAY071200-00 | yes | False | -64.000000 | 1.096302 | 0.250754 | 1 | no | True | 44.000000 | 324.039866 |
| KXBTC15M-26MAY071300-00 | yes | False | -63.000000 | 1.011545 | 0.289227 | 0 | None | None | None | None |
