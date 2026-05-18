# v28 Frozen YES-Only Exit Reduce Suppression

Research-only: no live bot changes and no orders.

- Freeze timestamp UTC: `2026-05-06T11:04:54.847536+00:00`
- Candidate: `suppress_yes_reduce_p_hold_ge_075`
- Rule: `If exit reason is mushroom_v28_probability_reduce, side is YES, and p_hold >= 0.75, score as held to settlement; otherwise keep current v28 exit.`
- Future rows/settled: `103/103`
- Current/candidate gross: `635.0c/747.0c`
- Delta vs current: `112.0c`
- Suppressed exits: `6`
- Suppressed winners/losers: `5/1`
- Blockers: `suppressed_losers_present, suppressed_loss_control_cost_negative`

## Interpretation

- Frozen YES-only reduce-suppression candidate has 103 settled future rows.
- Delta versus current v28 exits is 112.0c.
- Suppressed exits: 6; winners/losers 5/1.
- This is narrower than the full reduce-suppression rule and intentionally excludes NO until NO has independent forward evidence.

## Rows

| market | side | result | entry | exit | reason | p_hold | drawdown | current c | hold c | candidate c | delta c | suppressed | worst hold mark |
|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY060715-15 | yes | yes | 81 | 93 | mushroom_v28_exit_value_over_hold | 0.920907 | -11.090690 | 24.0 | 38.0 | 24.0 | 0.000000 | False | 20 |
| KXBTC15M-26MAY060715-15 | yes | yes | 89 | 99 | mushroom_v28_exit_value_over_hold | 0.984061 | -8.406103 | 20.0 | 22.0 | 20.0 | 0.000000 | False | 20 |
| KXBTC15M-26MAY060730-30 | yes | yes | 84 | None |  | None | None | 32.0 | 32.0 | 32.0 | 0.000000 | False | None |
| KXBTC15M-26MAY060745-45 | yes | no | 69 | 57 | mushroom_v28_probability_collapse_full | 0.610349 | 7.965096 | -24.0 | -138.0 | -24.0 | 0.000000 | False | -156 |
| KXBTC15M-26MAY060745-45 | yes | no | 78 | 43 | mushroom_v28_probability_collapse_full | 0.563569 | 21.643115 | -70.0 | -156.0 | -70.0 | 0.000000 | False | -156 |
| KXBTC15M-26MAY060800-00 | yes | yes | 79 | 70 | mushroom_v28_probability_reduce | 0.738185 | 5.181496 | -18.0 | 42.0 | -18.0 | 0.000000 | False | -30 |
| KXBTC15M-26MAY060800-00 | yes | yes | 66 | 50 | mushroom_v28_probability_collapse_full | 0.614703 | 4.529724 | -32.0 | 68.0 | -32.0 | 0.000000 | False | -30 |
| KXBTC15M-26MAY060815-15 | no | no | 79 | None |  | None | None | 42.0 | 42.0 | 42.0 | 0.000000 | False | None |
| KXBTC15M-26MAY060830-30 | yes | yes | 76 | 100 | mushroom_v28_exit_value_over_hold | 0.992185 | -23.218487 | 48.0 | 48.0 | 48.0 | 0.000000 | False | 48 |
| KXBTC15M-26MAY060900-00 | yes | no | 78 | 73 | mushroom_v28_probability_reduce | 0.789990 | -0.998969 | -10.0 | -156.0 | -156.0 | -146.000000 | True | 34 |
| KXBTC15M-26MAY060900-00 | yes | no | 78 | 40 | mushroom_v28_probability_collapse_full | 0.397320 | 41.268037 | -76.0 | -156.0 | -76.0 | 0.000000 | False | 34 |
| KXBTC15M-26MAY060900-00 | no | no | 73 | 65 | mushroom_v28_probability_reduce | 0.721102 | 0.889760 | -16.0 | 54.0 | -16.0 | 0.000000 | False | 34 |
| KXBTC15M-26MAY060900-00 | no | no | 79 | 96 | mushroom_v28_exit_value_over_hold | 0.948348 | -15.834839 | 34.0 | 42.0 | 34.0 | 0.000000 | False | 34 |
| KXBTC15M-26MAY060915-15 | no | no | 70 | 70 | mushroom_v28_probability_reduce | 0.793762 | -9.376204 | 0.0 | 60.0 | 0.0 | 0.000000 | False | 48 |
| KXBTC15M-26MAY060915-15 | no | no | 75 | 100 | mushroom_v28_exit_value_over_hold | 0.994245 | -17.424453 | 50.0 | 50.0 | 50.0 | 0.000000 | False | 48 |
| KXBTC15M-26MAY060930-30 | no | no | 76 | 66 | mushroom_v28_probability_reduce | 0.725946 | 3.405368 | -20.0 | 48.0 | -20.0 | 0.000000 | False | -10 |
| KXBTC15M-26MAY060930-30 | no | no | 76 | 69 | mushroom_v28_probability_reduce | 0.787606 | -2.760587 | -14.0 | 48.0 | -14.0 | 0.000000 | False | -10 |
| KXBTC15M-26MAY060930-30 | no | no | 73 | 72 | mushroom_v28_probability_reduce | 0.799180 | -6.917970 | -3.0 | 54.0 | -3.0 | 0.000000 | False | -10 |
| KXBTC15M-26MAY060930-30 | no | no | 77 | None |  | None | None | 46.0 | 46.0 | 46.0 | 0.000000 | False | -10 |
| KXBTC15M-26MAY060945-45 | no | no | 59 | 51 | mushroom_v28_probability_collapse_full | 0.556556 | 3.344394 | -16.0 | 82.0 | -16.0 | 0.000000 | False | 40 |
| KXBTC15M-26MAY060945-45 | no | no | 70 | 62 | mushroom_v28_probability_collapse_full | 0.689159 | 1.084126 | -16.0 | 60.0 | -16.0 | 0.000000 | False | 40 |
| KXBTC15M-26MAY060945-45 | no | no | 71 | 65 | mushroom_v28_probability_reduce | 0.735773 | -2.577325 | -12.0 | 58.0 | -12.0 | 0.000000 | False | 40 |
| KXBTC15M-26MAY060945-45 | no | no | 72 | 96 | mushroom_v28_exit_value_over_hold | 0.950787 | -23.078686 | 48.0 | 56.0 | 48.0 | 0.000000 | False | 40 |
| KXBTC15M-26MAY061000-00 | no | no | 65 | None |  | None | None | 70.0 | 70.0 | 70.0 | 0.000000 | False | None |
| KXBTC15M-26MAY061015-15 | no | no | 68 | 65 | mushroom_v28_probability_reduce | 0.733426 | -5.342610 | -6.0 | 64.0 | -6.0 | 0.000000 | False | 4 |
| KXBTC15M-26MAY061015-15 | no | no | 70 | 70 | mushroom_v28_probability_reduce | 0.799979 | -9.997858 | 0.0 | 60.0 | 0.0 | 0.000000 | False | 4 |
| KXBTC15M-26MAY061015-15 | no | no | 73 | None |  | None | None | 54.0 | 54.0 | 54.0 | 0.000000 | False | 4 |
| KXBTC15M-26MAY061030-30 | yes | yes | 78 | 70 | mushroom_v28_probability_reduce | 0.752739 | 2.726149 | -16.0 | 44.0 | 44.0 | 60.000000 | True | -10 |
| KXBTC15M-26MAY061030-30 | yes | yes | 78 | 73 | mushroom_v28_probability_reduce | 0.796458 | -1.645773 | -10.0 | 44.0 | 44.0 | 54.000000 | True | -10 |
| KXBTC15M-26MAY061030-30 | yes | yes | 74 | None |  | None | None | 52.0 | 52.0 | 52.0 | 0.000000 | False | -10 |
| KXBTC15M-26MAY061045-45 | yes | yes | 80 | 77 | mushroom_v28_probability_reduce | 0.796949 | 0.305083 | -6.0 | 40.0 | 40.0 | 46.000000 | True | 28 |
| KXBTC15M-26MAY061045-45 | yes | yes | 84 | 98 | mushroom_v28_exit_value_over_hold | 0.975987 | -13.598681 | 28.0 | 32.0 | 28.0 | 0.000000 | False | 28 |
| KXBTC15M-26MAY061100-00 | no | no | 83 | 63 | mushroom_v28_probability_collapse_full | 0.704126 | 12.587383 | -40.0 | 34.0 | -40.0 | 0.000000 | False | -40 |
| KXBTC15M-26MAY061100-00 | no | no | 81 | None |  | None | None | 38.0 | 38.0 | 38.0 | 0.000000 | False | -40 |
| KXBTC15M-26MAY061130-30 | yes | yes | 80 | None |  | None | None | 40.0 | 40.0 | 40.0 | 0.000000 | False | None |
| KXBTC15M-26MAY061200-00 | yes | yes | 82 | 90 | mushroom_v28_exit_value_over_hold | 0.889296 | -7.929607 | 16.0 | 36.0 | 16.0 | 0.000000 | False | 14 |
| KXBTC15M-26MAY061300-00 | yes | no | 80 | 65 | mushroom_v28_probability_collapse_full | 0.666430 | 13.356971 | -30.0 | -160.0 | -30.0 | 0.000000 | False | None |
| KXBTC15M-26MAY061400-00 | no | no | 89 | 84 | mushroom_v28_exit_value_over_hold | 0.737977 | 15.202342 | -10.0 | 22.0 | -10.0 | 0.000000 | False | -16 |
| KXBTC15M-26MAY061415-15 | no | no | 88 | None |  | None | None | 24.0 | 24.0 | 24.0 | 0.000000 | False | None |
| KXBTC15M-26MAY061445-45 | no | no | 88 | 77 | mushroom_v28_probability_reduce | 0.797830 | 8.216985 | -22.0 | 24.0 | -22.0 | 0.000000 | False | 14 |
| KXBTC15M-26MAY061445-45 | no | no | 90 | 99 | mushroom_v28_exit_value_over_hold | 0.981991 | -8.199066 | 18.0 | 20.0 | 18.0 | 0.000000 | False | 14 |
| KXBTC15M-26MAY061545-45 | yes | yes | 84 | 95 | mushroom_v28_exit_value_over_hold | 0.935410 | -9.540987 | 22.0 | 32.0 | 22.0 | 0.000000 | False | 18 |
| KXBTC15M-26MAY061615-15 | yes | yes | 90 | 94 | mushroom_v28_exit_value_over_hold | 0.931218 | -3.121769 | 8.0 | 20.0 | 8.0 | 0.000000 | False | 10 |
| KXBTC15M-26MAY061645-45 | no | no | 76 | None |  | None | None | 48.0 | 48.0 | 48.0 | 0.000000 | False | None |
| KXBTC15M-26MAY061800-00 | no | no | 67 | 24 | mushroom_v28_probability_collapse_full | 0.552607 | 11.739327 | -86.0 | 66.0 | -86.0 | 0.000000 | False | -82 |
| KXBTC15M-26MAY061815-15 | no | no | 84 | 96 | mushroom_v28_exit_value_over_hold | 0.950684 | -11.068394 | 24.0 | 32.0 | 24.0 | 0.000000 | False | 24 |
| KXBTC15M-26MAY061830-30 | no | no | 89 | 99 | mushroom_v28_exit_value_over_hold | 0.976718 | -8.671753 | 20.0 | 22.0 | 20.0 | 0.000000 | False | 20 |
| KXBTC15M-26MAY061900-00 | yes | yes | 90 | None |  | None | None | 20.0 | 20.0 | 20.0 | 0.000000 | False | None |
| KXBTC15M-26MAY061915-15 | no | no | 87 | 99 | mushroom_v28_exit_value_over_hold | 0.981987 | -11.198704 | 24.0 | 26.0 | 24.0 | 0.000000 | False | 22 |
| KXBTC15M-26MAY062015-15 | no | no | 42 | 12 | mushroom_v28_probability_collapse_full | 0.268932 | 15.106811 | -60.0 | 116.0 | -60.0 | 0.000000 | False | -172 |
| KXBTC15M-26MAY062015-15 | yes | no | 86 | 90 | mushroom_v28_exit_value_over_hold | 0.812359 | 4.764109 | 8.0 | -172.0 | 8.0 | 0.000000 | False | -172 |
| KXBTC15M-26MAY062015-15 | yes | no | 67 | None |  | None | None | -134.0 | -134.0 | -134.0 | 0.000000 | False | -172 |
| KXBTC15M-26MAY062030-30 | no | no | 67 | 83 | mushroom_v28_exit_value_over_hold | 0.661475 | 0.852486 | 32.0 | 66.0 | 32.0 | 0.000000 | False | 42 |
| KXBTC15M-26MAY062045-45 | no | no | 80 | 92 | mushroom_v28_exit_value_over_hold | 0.891386 | -9.138584 | 24.0 | 40.0 | 24.0 | 0.000000 | False | 24 |
| KXBTC15M-26MAY062100-00 | yes | yes | 83 | 81 | mushroom_v28_exit_value_over_hold | 0.647591 | 18.240924 | -4.0 | 34.0 | -4.0 | 0.000000 | False | -82 |
| KXBTC15M-26MAY062100-00 | yes | yes | 84 | 74 | mushroom_v28_exit_value_over_hold | 0.663692 | 17.630840 | -20.0 | 32.0 | -20.0 | 0.000000 | False | -82 |
| KXBTC15M-26MAY062100-00 | yes | yes | 61 | 68 | mushroom_v28_exit_value_over_hold | 0.489234 | 12.076646 | 14.0 | 78.0 | 14.0 | 0.000000 | False | -82 |
| KXBTC15M-26MAY062115-15 | yes | yes | 73 | 67 | mushroom_v28_exit_value_over_hold | 0.395750 | 33.425046 | -12.0 | 54.0 | -12.0 | 0.000000 | False | 22 |
| KXBTC15M-26MAY062115-15 | no | yes | 69 | 52 | mushroom_v28_exit_value_over_hold | 0.455777 | 14.422271 | -34.0 | -138.0 | -34.0 | 0.000000 | False | 22 |
| KXBTC15M-26MAY062115-15 | yes | yes | 88 | 99 | mushroom_v28_exit_value_over_hold | 0.982461 | -10.246054 | 22.0 | 24.0 | 22.0 | 0.000000 | False | 22 |
| KXBTC15M-26MAY062130-30 | no | yes | 76 | 60 | mushroom_v28_probability_reduce | 0.768407 | 6.159273 | -32.0 | -152.0 | -32.0 | 0.000000 | False | -152 |
| KXBTC15M-26MAY062215-15 | no | no | 65 | 72 | mushroom_v28_probability_collapse_full | 0.708248 | -5.824841 | 14.0 | 70.0 | 14.0 | 0.000000 | False | 10 |
| KXBTC15M-26MAY062215-15 | no | no | 84 | 89 | mushroom_v28_exit_value_over_hold | 0.860673 | -2.067333 | 10.0 | 32.0 | 10.0 | 0.000000 | False | 10 |
| KXBTC15M-26MAY062245-45 | yes | yes | 86 | 90 | mushroom_v28_exit_value_over_hold | 0.643812 | 15.618779 | 8.0 | 28.0 | 8.0 | 0.000000 | False | 4 |
| KXBTC15M-26MAY062300-00 | yes | yes | 87 | 95 | mushroom_v28_exit_value_over_hold | 0.746374 | 10.362646 | 16.0 | 26.0 | 16.0 | 0.000000 | False | 14 |
| KXBTC15M-26MAY062315-15 | no | no | 84 | 87 | mushroom_v28_exit_value_over_hold | 0.811182 | 2.881757 | 6.0 | 32.0 | 6.0 | 0.000000 | False | -52 |
| KXBTC15M-26MAY070000-00 | no | no | 78 | 79 | mushroom_v28_exit_value_over_hold | 0.726702 | 5.329808 | 2.0 | 44.0 | 2.0 | 0.000000 | False | -14 |
| KXBTC15M-26MAY070015-15 | no | yes | 70 | 69 | mushroom_v28_exit_value_over_hold | 0.596562 | 10.343815 | -2.0 | -140.0 | -2.0 | 0.000000 | False | -140 |
| KXBTC15M-26MAY070030-30 | yes | yes | 82 | 97 | mushroom_v28_exit_value_over_hold | 0.921778 | -10.177771 | 30.0 | 36.0 | 30.0 | 0.000000 | False | 6 |
| KXBTC15M-26MAY070115-15 | yes | yes | 82 | 82 | mushroom_v28_exit_value_over_hold | 0.679619 | 18.038087 | 0.0 | 36.0 | 0.0 | 0.000000 | False | -6 |
| KXBTC15M-26MAY070545-45 | no | no | 82 | 91 | mushroom_v28_exit_value_over_hold | 0.892567 | -7.256748 | 18.0 | 36.0 | 18.0 | 0.000000 | False | -4 |
| KXBTC15M-26MAY070645-45 | yes | yes | 81 | None |  | None | None | 38.0 | 38.0 | 38.0 | 0.000000 | False | None |
| KXBTC15M-26MAY070745-45 | yes | yes | 68 | 85 | mushroom_v28_exit_value_over_hold | 0.821701 | -14.170103 | 34.0 | 64.0 | 34.0 | 0.000000 | False | 50 |
| KXBTC15M-26MAY070815-15 | yes | yes | 90 | 91 | mushroom_v28_exit_value_over_hold | 0.890464 | -1.046434 | 2.0 | 20.0 | 2.0 | 0.000000 | False | 2 |
| KXBTC15M-26MAY070830-30 | no | no | 82 | 91 | mushroom_v28_exit_value_over_hold | 0.825354 | -0.535395 | 18.0 | 36.0 | 18.0 | 0.000000 | False | -24 |
| KXBTC15M-26MAY070830-30 | no | no | 77 | 70 | mushroom_v28_exit_value_over_hold | 0.612998 | 15.700151 | -14.0 | 46.0 | -14.0 | 0.000000 | False | -24 |
| KXBTC15M-26MAY070830-30 | no | no | 77 | None |  | None | None | 46.0 | 46.0 | 46.0 | 0.000000 | False | -24 |
| KXBTC15M-26MAY070915-15 | no | no | 77 | None |  | None | None | 46.0 | 46.0 | 46.0 | 0.000000 | False | None |
| KXBTC15M-26MAY070930-30 | yes | yes | 80 | 97 | mushroom_v28_exit_value_over_hold | 0.969995 | -13.999536 | 34.0 | 40.0 | 34.0 | 0.000000 | False | -56 |
| KXBTC15M-26MAY070945-45 | no | no | 69 | None |  | None | None | 62.0 | 62.0 | 62.0 | 0.000000 | False | None |
| KXBTC15M-26MAY071000-00 | no | no | 73 | 55 | mushroom_v28_probability_collapse_full | 0.617577 | 11.242300 | -36.0 | 54.0 | -36.0 | 0.000000 | False | 12 |
| KXBTC15M-26MAY071000-00 | no | no | 71 | 79 | mushroom_v28_probability_reduce | 0.781361 | 6.863933 | 16.0 | 58.0 | 16.0 | 0.000000 | False | 12 |
| KXBTC15M-26MAY071015-15 | no | yes | 78 | 79 | mushroom_v28_probability_reduce | 0.789130 | -0.913001 | 2.0 | -156.0 | 2.0 | 0.000000 | False | 18 |
| KXBTC15M-26MAY071015-15 | no | yes | 81 | 73 | mushroom_v28_probability_reduce | 0.763980 | 4.602013 | -16.0 | -162.0 | -16.0 | 0.000000 | False | 18 |
| KXBTC15M-26MAY071015-15 | yes | yes | 84 | 94 | mushroom_v28_exit_value_over_hold | 0.923102 | -8.310249 | 20.0 | 32.0 | 20.0 | 0.000000 | False | 18 |
| KXBTC15M-26MAY071030-30 | no | no | 77 | 65 | mushroom_v28_probability_collapse_full | 0.709831 | 6.016933 | -24.0 | 46.0 | -24.0 | 0.000000 | False | -20 |
| KXBTC15M-26MAY071030-30 | no | no | 76 | None |  | None | None | 48.0 | 48.0 | 48.0 | 0.000000 | False | -20 |
| KXBTC15M-26MAY071045-45 | no | no | 74 | 69 | mushroom_v28_probability_reduce | 0.760529 | -2.052947 | -10.0 | 52.0 | -10.0 | 0.000000 | False | -14 |
| KXBTC15M-26MAY071045-45 | no | no | 75 | None |  | None | None | 50.0 | 50.0 | 50.0 | 0.000000 | False | -14 |
| KXBTC15M-26MAY071100-00 | yes | no | 83 | 85 | mushroom_v28_exit_value_over_hold | 0.836750 | -0.675039 | 4.0 | -166.0 | 4.0 | 0.000000 | False | -166 |
| KXBTC15M-26MAY071115-15 | yes | yes | 84 | 91 | mushroom_v28_exit_value_over_hold | 0.888844 | -4.884431 | 14.0 | 32.0 | 14.0 | 0.000000 | False | -112 |
| KXBTC15M-26MAY071130-30 | no | no | 85 | None |  | None | None | 30.0 | 30.0 | 30.0 | 0.000000 | False | None |
| KXBTC15M-26MAY071145-45 | yes | yes | 77 | 99 | mushroom_v28_exit_value_over_hold | 0.982146 | -17.214598 | 44.0 | 46.0 | 44.0 | 0.000000 | False | 44 |
| KXBTC15M-26MAY071200-00 | no | no | 77 | 98 | mushroom_v28_exit_value_over_hold | 0.961165 | -19.116535 | 42.0 | 46.0 | 42.0 | 0.000000 | False | 42 |
| KXBTC15M-26MAY071215-15 | no | no | 84 | 76 | mushroom_v28_probability_reduce | 0.797661 | 4.233856 | -16.0 | 32.0 | -16.0 | 0.000000 | False | -28 |
| KXBTC15M-26MAY071215-15 | no | no | 78 | 79 | mushroom_v28_exit_value_over_hold | 0.752304 | 2.769646 | 2.0 | 44.0 | 2.0 | 0.000000 | False | -28 |
| KXBTC15M-26MAY071215-15 | no | no | 80 | 76 | mushroom_v28_probability_reduce | 0.765822 | 3.417815 | -8.0 | 40.0 | -8.0 | 0.000000 | False | -28 |
| KXBTC15M-26MAY071230-30 | yes | yes | 77 | 72 | mushroom_v28_probability_reduce | 0.749378 | 2.062161 | -10.0 | 46.0 | -10.0 | 0.000000 | False | -34 |
| KXBTC15M-26MAY071230-30 | yes | yes | 84 | 65 | mushroom_v28_probability_collapse_full | 0.662903 | 17.709724 | -38.0 | 32.0 | -38.0 | 0.000000 | False | -34 |
| KXBTC15M-26MAY071230-30 | yes | yes | 80 | None |  | None | None | 40.0 | 40.0 | 40.0 | 0.000000 | False | -34 |
| KXBTC15M-26MAY071315-15 | yes | yes | 80 | 77 | mushroom_v28_probability_reduce | 0.798341 | -0.834147 | -6.0 | 40.0 | 40.0 | 46.000000 | True | 28 |
| KXBTC15M-26MAY071315-15 | yes | yes | 81 | 74 | mushroom_v28_probability_reduce | 0.784166 | 2.583397 | -14.0 | 38.0 | 38.0 | 52.000000 | True | 28 |
| KXBTC15M-26MAY071315-15 | yes | yes | 78 | 94 | mushroom_v28_exit_value_over_hold | 0.927498 | -14.749774 | 32.0 | 44.0 | 32.0 | 0.000000 | False | 28 |
