# v28 Exit Reduce Side-Split Attribution

Research-only: no live bot changes and no orders.

- Source freeze timestamp UTC: `2026-05-06T06:33:56.987999+00:00`
- Source candidate: `suppress_reduce_p_hold_ge_075`
- Rows after source freeze: `132`

## Policy Split

| policy | settled | delta c | suppressed | yes/no suppressed | W/L suppressed | winner recovery | loss cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| suppress_all_reduce_p_hold_ge_075 | 132 | 337.000000 | 25 | 12/13 | 20/5 | 1067.000000 | -730.000000 |
| suppress_yes_reduce_p_hold_ge_075 | 132 | 436.000000 | 12 | 12/0 | 11/1 | 582.000000 | -146.000000 |
| suppress_no_reduce_p_hold_ge_075 | 132 | -99.000000 | 13 | 0/13 | 9/4 | 485.000000 | -584.000000 |

## Suppressed Rows

| market | side | result | p_hold | current c | hold c | delta c |
|---|---|---|---:|---:|---:|---:|
| KXBTC15M-26MAY060245-45 | yes | yes | 0.793334 | -8.000000 | 40.000000 | 48.000000 |
| KXBTC15M-26MAY060300-00 | yes | yes | 0.780402 | -14.000000 | 38.000000 | 52.000000 |
| KXBTC15M-26MAY060300-00 | yes | yes | 0.753164 | -22.000000 | 40.000000 | 62.000000 |
| KXBTC15M-26MAY060630-30 | yes | yes | 0.777774 | -12.000000 | 42.000000 | 54.000000 |
| KXBTC15M-26MAY060645-45 | yes | yes | 0.799349 | -16.000000 | 36.000000 | 52.000000 |
| KXBTC15M-26MAY060645-45 | yes | yes | 0.779789 | -12.000000 | 44.000000 | 56.000000 |
| KXBTC15M-26MAY060700-00 | no | yes | 0.799603 | -8.000000 | -168.000000 | -160.000000 |
| KXBTC15M-26MAY060900-00 | yes | no | 0.789990 | -10.000000 | -156.000000 | -146.000000 |
| KXBTC15M-26MAY060915-15 | no | no | 0.793762 | 0.000000 | 60.000000 | 60.000000 |
| KXBTC15M-26MAY060930-30 | no | no | 0.787606 | -14.000000 | 48.000000 | 62.000000 |
| KXBTC15M-26MAY060930-30 | no | no | 0.799180 | -3.000000 | 54.000000 | 57.000000 |
| KXBTC15M-26MAY061015-15 | no | no | 0.799979 | 0.000000 | 60.000000 | 60.000000 |
| KXBTC15M-26MAY061030-30 | yes | yes | 0.752739 | -16.000000 | 44.000000 | 60.000000 |
| KXBTC15M-26MAY061030-30 | yes | yes | 0.796458 | -10.000000 | 44.000000 | 54.000000 |
| KXBTC15M-26MAY061045-45 | yes | yes | 0.796949 | -6.000000 | 40.000000 | 46.000000 |
| KXBTC15M-26MAY061445-45 | no | no | 0.797830 | -22.000000 | 24.000000 | 46.000000 |
| KXBTC15M-26MAY062130-30 | no | yes | 0.768407 | -32.000000 | -152.000000 | -120.000000 |
| KXBTC15M-26MAY071000-00 | no | no | 0.781361 | 16.000000 | 58.000000 | 42.000000 |
| KXBTC15M-26MAY071015-15 | no | yes | 0.789130 | 2.000000 | -156.000000 | -158.000000 |
| KXBTC15M-26MAY071015-15 | no | yes | 0.763980 | -16.000000 | -162.000000 | -146.000000 |
| KXBTC15M-26MAY071045-45 | no | no | 0.760529 | -10.000000 | 52.000000 | 62.000000 |
| KXBTC15M-26MAY071215-15 | no | no | 0.797661 | -16.000000 | 32.000000 | 48.000000 |
| KXBTC15M-26MAY071215-15 | no | no | 0.765822 | -8.000000 | 40.000000 | 48.000000 |
| KXBTC15M-26MAY071315-15 | yes | yes | 0.798341 | -6.000000 | 40.000000 | 46.000000 |
| KXBTC15M-26MAY071315-15 | yes | yes | 0.784166 | -14.000000 | 38.000000 | 52.000000 |

## Interpretation

- If YES-only keeps most of the positive delta while NO-only is negative, the physical mechanism is side-asymmetric.
- A side-asymmetric read means the full two-sided exit patch should not be promoted from blended PnL.
