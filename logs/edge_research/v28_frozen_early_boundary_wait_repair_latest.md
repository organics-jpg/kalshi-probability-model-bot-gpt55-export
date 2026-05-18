# v28 Frozen Early-Boundary Wait Repair

Research-only; no live bot changes and no orders.

- Freeze timestamp UTC: `2026-05-06T10:48:07.385138+00:00`
- Candidate: `early_boundary_wait480_p50_any_side`
- Future denominator: `106`
- Live ready: `True`
- Blockers: `none`

## Interpretation

- Frozen forward denominator is 106; candidate has 80 settled rows and net 82.0c.
- Target net is 158.0c; candidate delta is -76.0c.
- Promotion blocked by: none.
- This is a forward validator, not live order logic.

## Summaries

| surface | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| target | 78 | 78 | 46/32 | 73.584906 | 158.000000 | 2.025641 |
| danger_removed | 35 | 35 | 19/16 | 33.018868 | -80.000000 | -2.285714 |
| wait_replacements | 1 | 1 | 1/0 | 0.943396 | 44.000000 | 44.000000 |
| repair_added | 36 | 36 | 25/11 | 33.962264 | -200.000000 | -5.555556 |
| candidate | 80 | 80 | 53/27 | 75.471698 | 82.000000 | 1.025000 |

## Danger Cases

| market | target side | target won | target net | stc | abs d | recross | repl side | repl won | repl net | delay |
|---|---|---|---:|---:|---:|---:|---|---|---:|---:|
| KXBTC15M-26MAY060730-30 | yes | True | 84.000000 | 867.397000 | 0.270357 | 0.863859 | None | None | None | None |
| KXBTC15M-26MAY060800-00 | yes | True | 102.000000 | 884.129000 | 0.027808 | 1.358871 | None | None | None | None |
| KXBTC15M-26MAY060830-30 | no | False | -122.000000 | 884.233000 | 0.286154 | 0.943700 | None | None | None | None |
| KXBTC15M-26MAY060915-15 | no | True | 76.000000 | 869.636000 | 0.431641 | 0.831637 | None | None | None | None |
| KXBTC15M-26MAY060930-30 | yes | False | -124.000000 | 864.340000 | 0.244982 | 1.150583 | None | None | None | None |
| KXBTC15M-26MAY061015-15 | no | True | 92.000000 | 883.995000 | 0.274143 | 1.130150 | None | None | None | None |
| KXBTC15M-26MAY061030-30 | yes | True | 74.000000 | 868.942000 | 0.232373 | 1.168280 | None | None | None | None |
| KXBTC15M-26MAY061045-45 | no | False | -118.000000 | 868.842000 | 0.212683 | 1.191443 | None | None | None | None |
| KXBTC15M-26MAY061130-30 | yes | True | 66.000000 | 883.089000 | 0.341283 | 1.056221 | None | None | None | None |
| KXBTC15M-26MAY061430-30 | yes | True | 62.000000 | 864.426000 | 0.424290 | 0.893555 | None | None | None | None |
| KXBTC15M-26MAY061715-15 | yes | False | -104.000000 | 804.817000 | 0.324075 | 0.683095 | None | None | None | None |
| KXBTC15M-26MAY061930-30 | yes | True | 102.000000 | 810.397000 | 0.100563 | 0.905378 | None | None | None | None |
| KXBTC15M-26MAY061945-45 | yes | False | -88.000000 | 809.092000 | 0.132650 | 0.801256 | None | None | None | None |
| KXBTC15M-26MAY062000-00 | yes | True | 96.000000 | 849.989000 | 0.192858 | 0.673972 | None | None | None | None |
| KXBTC15M-26MAY062015-15 | yes | False | -106.000000 | 869.507000 | 0.086972 | 0.736601 | None | None | None | None |
| KXBTC15M-26MAY062030-30 | yes | False | -68.000000 | 804.712000 | 0.107412 | 0.680770 | None | None | None | None |
| KXBTC15M-26MAY062045-45 | no | True | 94.000000 | 834.661000 | 0.321769 | 0.590304 | None | None | None | None |
| KXBTC15M-26MAY062145-45 | yes | True | 82.000000 | 800.015000 | 0.250555 | 0.820982 | None | None | None | None |
| KXBTC15M-26MAY062215-15 | no | True | 78.000000 | 850.282000 | 0.404187 | 0.669869 | None | None | None | None |
| KXBTC15M-26MAY062245-45 | no | False | -112.000000 | 841.408000 | 0.278629 | 0.786584 | None | None | None | None |
| KXBTC15M-26MAY070045-45 | no | True | 100.000000 | 810.351000 | 0.187292 | 0.830545 | None | None | None | None |
| KXBTC15M-26MAY070530-30 | no | True | 100.000000 | 879.618000 | 0.132673 | 0.894668 | None | None | None | None |
| KXBTC15M-26MAY070630-30 | yes | False | -98.000000 | 875.963000 | 0.230767 | 0.826469 | None | None | None | None |
| KXBTC15M-26MAY070700-00 | yes | False | -116.000000 | 869.636000 | 0.375634 | 0.760124 | None | None | None | None |
| KXBTC15M-26MAY070715-15 | yes | True | 94.000000 | 812.253000 | 0.157545 | 0.877232 | None | None | None | None |
| KXBTC15M-26MAY070730-30 | yes | False | -96.000000 | 819.643000 | 0.091964 | 0.936121 | None | None | None | None |
| KXBTC15M-26MAY070815-15 | yes | True | 108.000000 | 882.524000 | 0.024626 | 1.067161 | None | None | None | None |
| KXBTC15M-26MAY070830-30 | yes | False | -86.000000 | 811.825000 | 0.078942 | 0.952791 | None | None | None | None |
| KXBTC15M-26MAY070945-45 | no | True | 100.000000 | 860.716000 | 0.067417 | 1.088863 | None | None | None | None |
| KXBTC15M-26MAY071015-15 | no | False | -124.000000 | 864.225000 | 0.287274 | 1.102864 | None | None | None | None |
