# v28 Live Collapse Reentry Registry

- Freeze timestamp UTC: `2026-05-06T04:56:06.196433+00:00`
- Future rows/closed/open: `33/22/11`
- Future gross / skip delta: `-119.000000c / 119.000000c`
- Diagnostic all rows/closed/open: `79/54/25`

## Current Read

- Post-freeze collapse-reentry rows: 33 total, 22 closed, 11 open.
- Closed gross is -119.0c; hypothetical skip delta is 119.0c.
- This is a state/FV confidence feature, not a promotion rule until sample size and tag stability are adequate.

## Future Tag Rollups

| tag | rows | closed | W/L | gross c | skip delta c |
|---|---:|---:|---:|---:|---:|
| fast_reentry_lte_180s | 21 | 15 | 4/11 | -60.000000 | 60.000000 |
| same_side_reentry | 17 | 13 | 1/12 | -132.000000 | 132.000000 |
| thin_edge_lt_4c | 16 | 11 | 3/8 | -49.000000 | 49.000000 |
| older_book_500ms | 14 | 10 | 4/6 | -9.000000 | 9.000000 |
| opposite_side_reentry | 16 | 9 | 4/5 | 13.000000 | -13.000000 |
| high_conf_p90 | 10 | 8 | 2/6 | -46.000000 | 46.000000 |
| late_reentry_gt_360s | 6 | 5 | 0/5 | -65.000000 | 65.000000 |
| strong_edge_ge_8c | 4 | 4 | 2/2 | 10.000000 | -10.000000 |
| mid_reentry_180_360s | 6 | 2 | 1/1 | 6.000000 | -6.000000 |

## Future Rows

| market | side | entry | exit | p | edge | sec since collapse | same side | gross c | tags |
|---|---|---:|---:|---:|---:|---:|---|---:|---|
| KXBTC15M-26MAY060515-15 | no | 80 | 77 | 0.858743 | 2.374251 | 114.451956 | True | -3 | same_side_reentry, fast_reentry_lte_180s, thin_edge_lt_4c |
| KXBTC15M-26MAY060515-15 | no | 80 | 79 | 0.858743 | 2.374251 | 114.451956 | True | -1 | same_side_reentry, fast_reentry_lte_180s, thin_edge_lt_4c |
| KXBTC15M-26MAY060515-15 | no | 80 | 72 | 0.855250 | 2.025046 | 217.597951 | True | -16 | same_side_reentry, mid_reentry_180_360s, thin_edge_lt_4c, older_book_500ms |
| KXBTC15M-26MAY060700-00 | yes | 76 | None | 0.865784 | 7.078399 | 54.640030 | False | None | opposite_side_reentry, fast_reentry_lte_180s, older_book_500ms |
| KXBTC15M-26MAY060830-30 | yes | 78 | None | 0.864113 | 4.911310 | 266.973663 | False | None | opposite_side_reentry, mid_reentry_180_360s |
| KXBTC15M-26MAY060900-00 | no | 80 | 35 | 0.860341 | 2.534136 | 7.074346 | False | -45 | opposite_side_reentry, fast_reentry_lte_180s, thin_edge_lt_4c |
| KXBTC15M-26MAY060900-00 | no | 80 | None | 0.860341 | 2.534136 | 7.074346 | False | None | opposite_side_reentry, fast_reentry_lte_180s, thin_edge_lt_4c |
| KXBTC15M-26MAY062015-15 | yes | 75 | 90 | 0.916288 | 13.128835 | 149.940767 | False | 30 | opposite_side_reentry, fast_reentry_lte_180s, high_conf_p90, strong_edge_ge_8c, older_book_500ms |
| KXBTC15M-26MAY062015-15 | yes | 79 | None | 0.852842 | 2.784245 | 242.799014 | False | None | opposite_side_reentry, mid_reentry_180_360s, thin_edge_lt_4c, older_book_500ms |
| KXBTC15M-26MAY062115-15 | yes | 83 | 97 | 0.892306 | 3.230623 | 157.441071 | False | 28 | opposite_side_reentry, fast_reentry_lte_180s, thin_edge_lt_4c |
| KXBTC15M-26MAY062115-15 | yes | 86 | 97 | 0.910184 | 2.018419 | 277.534874 | False | 22 | opposite_side_reentry, mid_reentry_180_360s, high_conf_p90, thin_edge_lt_4c, older_book_500ms |
| KXBTC15M-26MAY062215-15 | no | 73 | 67 | 0.889286 | 12.428572 | 19.343803 | True | -12 | same_side_reentry, fast_reentry_lte_180s, strong_edge_ge_8c |
| KXBTC15M-26MAY062215-15 | no | 75 | None | 0.860398 | 7.539824 | 58.974580 | True | None | same_side_reentry, fast_reentry_lte_180s, older_book_500ms |
| KXBTC15M-26MAY062215-15 | no | 88 | None | 0.985127 | 7.512697 | 179.460766 | True | None | same_side_reentry, fast_reentry_lte_180s, high_conf_p90 |
| KXBTC15M-26MAY062230-30 | no | 77 | 70 | 0.853928 | 4.892788 | 132.658274 | False | -7 | opposite_side_reentry, fast_reentry_lte_180s, older_book_500ms |
| KXBTC15M-26MAY062230-30 | no | 77 | 71 | 0.853928 | 4.892788 | 132.658274 | False | -6 | opposite_side_reentry, fast_reentry_lte_180s, older_book_500ms |
| KXBTC15M-26MAY062230-30 | no | 84 | 88 | 0.894972 | 2.497154 | 178.900616 | False | 8 | opposite_side_reentry, fast_reentry_lte_180s, thin_edge_lt_4c, older_book_500ms |
| KXBTC15M-26MAY062230-30 | no | 83 | None | 0.881729 | 2.172900 | 248.340643 | False | None | opposite_side_reentry, mid_reentry_180_360s, thin_edge_lt_4c |
| KXBTC15M-26MAY070030-30 | yes | 88 | 85 | 0.971382 | 6.138247 | 166.232589 | True | -6 | same_side_reentry, fast_reentry_lte_180s, high_conf_p90 |
| KXBTC15M-26MAY070545-45 | yes | 63 | 53 | 0.920940 | 25.094043 | 1.306227 | True | -20 | same_side_reentry, fast_reentry_lte_180s, high_conf_p90, strong_edge_ge_8c |
| KXBTC15M-26MAY070545-45 | no | 82 | None | 0.877034 | 2.203434 | 83.325393 | False | None | opposite_side_reentry, fast_reentry_lte_180s, thin_edge_lt_4c |
| KXBTC15M-26MAY070545-45 | no | 89 | None | 0.962072 | 4.207224 | 232.384052 | False | None | opposite_side_reentry, mid_reentry_180_360s, high_conf_p90 |
| KXBTC15M-26MAY070730-30 | no | 80 | 73 | 0.855371 | 2.037100 | 93.150479 | True | -7 | same_side_reentry, fast_reentry_lte_180s, thin_edge_lt_4c |
| KXBTC15M-26MAY070730-30 | no | 80 | 73 | 0.855371 | 2.037100 | 93.150479 | True | -7 | same_side_reentry, fast_reentry_lte_180s, thin_edge_lt_4c |
| KXBTC15M-26MAY070730-30 | yes | 75 | 68 | 0.854408 | 6.940817 | 395.113850 | False | -7 | opposite_side_reentry, late_reentry_gt_360s |
| KXBTC15M-26MAY070730-30 | yes | 75 | 65 | 0.854408 | 6.940817 | 395.113850 | False | -10 | opposite_side_reentry, late_reentry_gt_360s |
| KXBTC15M-26MAY071000-00 | no | 69 | 75 | 0.859846 | 13.484627 | 32.786083 | True | 12 | same_side_reentry, fast_reentry_lte_180s, strong_edge_ge_8c, older_book_500ms |
| KXBTC15M-26MAY071000-00 | no | 87 | 75 | 0.975123 | 7.512292 | 152.901788 | True | -24 | same_side_reentry, fast_reentry_lte_180s, high_conf_p90, older_book_500ms |
| KXBTC15M-26MAY071000-00 | no | 85 | 75 | 0.933620 | 5.362031 | 479.484591 | True | -20 | same_side_reentry, late_reentry_gt_360s, high_conf_p90 |
| KXBTC15M-26MAY071000-00 | no | 90 | 76 | 0.951463 | 2.146330 | 601.779504 | True | -14 | same_side_reentry, late_reentry_gt_360s, high_conf_p90, thin_edge_lt_4c, older_book_500ms |
| KXBTC15M-26MAY071000-00 | no | 90 | 76 | 0.951463 | 2.146330 | 601.779504 | True | -14 | same_side_reentry, late_reentry_gt_360s, high_conf_p90, thin_edge_lt_4c, older_book_500ms |
| KXBTC15M-26MAY071000-00 | no | 79 | None | 0.865879 | 4.087902 | 664.313536 | True | None | same_side_reentry, late_reentry_gt_360s |
| KXBTC15M-26MAY071230-30 | yes | 80 | None | 0.859283 | 2.428293 | 21.015519 | True | None | same_side_reentry, fast_reentry_lte_180s, thin_edge_lt_4c, older_book_500ms |

## Diagnostic Recent Rows

These rows are not promotion evidence if they predate the freeze.

| market | side | entry | exit | p | edge | sec since collapse | same side | gross c | tags |
|---|---|---:|---:|---:|---:|---:|---|---:|---|
| KXBTC15M-26MAY070545-45 | no | 89 | None | 0.962072 | 4.207224 | 232.384052 | False | None | opposite_side_reentry, mid_reentry_180_360s, high_conf_p90 |
| KXBTC15M-26MAY070730-30 | no | 80 | 73 | 0.855371 | 2.037100 | 93.150479 | True | -7 | same_side_reentry, fast_reentry_lte_180s, thin_edge_lt_4c |
| KXBTC15M-26MAY070730-30 | no | 80 | 73 | 0.855371 | 2.037100 | 93.150479 | True | -7 | same_side_reentry, fast_reentry_lte_180s, thin_edge_lt_4c |
| KXBTC15M-26MAY070730-30 | yes | 75 | 68 | 0.854408 | 6.940817 | 395.113850 | False | -7 | opposite_side_reentry, late_reentry_gt_360s |
| KXBTC15M-26MAY070730-30 | yes | 75 | 65 | 0.854408 | 6.940817 | 395.113850 | False | -10 | opposite_side_reentry, late_reentry_gt_360s |
| KXBTC15M-26MAY071000-00 | no | 69 | 75 | 0.859846 | 13.484627 | 32.786083 | True | 12 | same_side_reentry, fast_reentry_lte_180s, strong_edge_ge_8c, older_book_500ms |
| KXBTC15M-26MAY071000-00 | no | 87 | 75 | 0.975123 | 7.512292 | 152.901788 | True | -24 | same_side_reentry, fast_reentry_lte_180s, high_conf_p90, older_book_500ms |
| KXBTC15M-26MAY071000-00 | no | 85 | 75 | 0.933620 | 5.362031 | 479.484591 | True | -20 | same_side_reentry, late_reentry_gt_360s, high_conf_p90 |
| KXBTC15M-26MAY071000-00 | no | 90 | 76 | 0.951463 | 2.146330 | 601.779504 | True | -14 | same_side_reentry, late_reentry_gt_360s, high_conf_p90, thin_edge_lt_4c, older_book_500ms |
| KXBTC15M-26MAY071000-00 | no | 90 | 76 | 0.951463 | 2.146330 | 601.779504 | True | -14 | same_side_reentry, late_reentry_gt_360s, high_conf_p90, thin_edge_lt_4c, older_book_500ms |
| KXBTC15M-26MAY071000-00 | no | 79 | None | 0.865879 | 4.087902 | 664.313536 | True | None | same_side_reentry, late_reentry_gt_360s |
| KXBTC15M-26MAY071230-30 | yes | 80 | None | 0.859283 | 2.428293 | 21.015519 | True | None | same_side_reentry, fast_reentry_lte_180s, thin_edge_lt_4c, older_book_500ms |
