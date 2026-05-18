# v28 Frozen Target-Coverage p70 Quality Registry

- Freeze timestamp UTC: `2026-05-06T04:32:03.738730+00:00`
- Future denominator/target entries/p70 rows/settled p70: `131/95/24/24`

## Current Read

- The registry has 24 p70-adjustable rows over 131 future markets; settled 24.
- Use tag rollups only as forward evidence; do not tune tag definitions from these rows.

## Tag Rollups

| tag | rows | settled | W/L | net c | avg raw p |
|---|---:|---:|---:|---:|---:|
| late_or_extreme_time | 14 | 14 | 11/3 | 165.000000 | 0.766282 |
| book_discount_ge_4pp | 13 | 13 | 11/2 | 245.000000 | 0.813594 |
| calm_recross | 10 | 10 | 8/2 | -13.000000 | 0.843456 |
| middle_time_120_720s | 10 | 10 | 8/2 | 12.000000 | 0.828375 |
| boundary_geometry | 9 | 9 | 5/4 | -206.000000 | 0.725060 |
| thin_edge_lt_3pp | 8 | 8 | 5/3 | -199.000000 | 0.753458 |
| deep_geometry | 5 | 5 | 5/0 | 78.000000 | 0.912030 |
| turbulent_recross | 4 | 4 | 2/2 | -143.000000 | 0.739078 |
| expensive_ask_ge_85c | 2 | 2 | 2/0 | 11.000000 | 0.948491 |

## Rows

| market | side | p raw | ask | edge | abs d | recross | stc | won | net c | tags |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| KXBTC15M-26MAY060100-00 | yes | 0.799928 | 0.790000 | 0.009928 | 0.694496 | 0.407561 | 684.076000 | False | -161.000000 | calm_recross, thin_edge_lt_3pp, middle_time_120_720s |
| KXBTC15M-26MAY060600-00 | no | 0.792357 | 0.750000 | 0.042357 | 0.672314 | 0.552274 | 868.886000 | True | 47.000000 | book_discount_ge_4pp, late_or_extreme_time |
| KXBTC15M-26MAY060945-45 | no | 0.761891 | 0.500000 | 0.261891 | 0.648099 | 0.777721 | 884.381000 | True | 96.000000 | turbulent_recross, book_discount_ge_4pp, late_or_extreme_time |
| KXBTC15M-26MAY061100-00 | yes | 0.740374 | 0.740000 | 0.000374 | 0.597049 | 0.809587 | 865.321000 | False | -151.000000 | turbulent_recross, boundary_geometry, thin_edge_lt_3pp, late_or_extreme_time |
| KXBTC15M-26MAY061200-00 | yes | 0.848576 | 0.810000 | 0.038576 | 0.876136 | 0.613707 | 868.928000 | True | 35.000000 | late_or_extreme_time |
| KXBTC15M-26MAY061400-00 | no | 0.973640 | 0.890000 | 0.083640 | 1.815216 | 0.051736 | 208.945000 | True | -11.000000 | calm_recross, deep_geometry, book_discount_ge_4pp, expensive_ask_ge_85c, middle_time_120_720s |
| KXBTC15M-26MAY061445-45 | no | 0.724164 | 0.710000 | 0.014164 | 0.536135 | 0.800263 | 884.401000 | True | 55.000000 | turbulent_recross, boundary_geometry, thin_edge_lt_3pp, late_or_extreme_time |
| KXBTC15M-26MAY061615-15 | yes | 0.770727 | 0.740000 | 0.030727 | 0.652892 | 0.500664 | 784.161000 | True | 49.000000 | late_or_extreme_time |
| KXBTC15M-26MAY061645-45 | no | 0.736529 | 0.710000 | 0.026529 | 0.561593 | 0.588375 | 858.442000 | True | 55.000000 | boundary_geometry, thin_edge_lt_3pp, late_or_extreme_time |
| KXBTC15M-26MAY061800-00 | no | 0.700391 | 0.680000 | 0.020391 | 0.442267 | 0.545766 | 789.738000 | True | 60.000000 | boundary_geometry, thin_edge_lt_3pp, late_or_extreme_time |
| KXBTC15M-26MAY061815-15 | no | 0.794472 | 0.720000 | 0.074472 | 0.683153 | 0.363637 | 670.498000 | True | 53.000000 | calm_recross, book_discount_ge_4pp, middle_time_120_720s |
| KXBTC15M-26MAY061915-15 | no | 0.923342 | 0.870000 | 0.053342 | 1.171707 | 0.229504 | 714.621000 | True | 22.000000 | calm_recross, deep_geometry, book_discount_ge_4pp, expensive_ask_ge_85c, middle_time_120_720s |
| KXBTC15M-26MAY062230-30 | yes | 0.718015 | 0.380000 | 0.338015 | 0.481781 | 0.349672 | 460.951000 | False | -80.000000 | calm_recross, boundary_geometry, book_discount_ge_4pp, middle_time_120_720s |
| KXBTC15M-26MAY062300-00 | yes | 0.758354 | 0.730000 | 0.028354 | 0.609402 | 0.572785 | 855.282000 | True | 51.000000 | thin_edge_lt_3pp, late_or_extreme_time |
| KXBTC15M-26MAY062315-15 | no | 0.744580 | 0.680000 | 0.064580 | 0.562923 | 0.455010 | 639.531000 | True | 60.000000 | boundary_geometry, book_discount_ge_4pp, middle_time_120_720s |
| KXBTC15M-26MAY070000-00 | no | 0.863962 | 0.780000 | 0.083962 | 0.906372 | 0.193188 | 387.203000 | True | 0.000000 | calm_recross, deep_geometry, book_discount_ge_4pp, middle_time_120_720s |
| KXBTC15M-26MAY070115-15 | yes | 0.773654 | 0.720000 | 0.053654 | 0.649457 | 0.488844 | 774.782000 | True | 53.000000 | book_discount_ge_4pp, late_or_extreme_time |
| KXBTC15M-26MAY070145-45 | no | 0.838040 | 0.810000 | 0.028040 | 0.811917 | 0.206140 | 396.525000 | True | 35.000000 | calm_recross, thin_edge_lt_3pp, middle_time_120_720s |
| KXBTC15M-26MAY070545-45 | yes | 0.707647 | 0.600000 | 0.107647 | 0.462750 | 0.622015 | 855.690000 | False | -124.000000 | boundary_geometry, book_discount_ge_4pp, late_or_extreme_time |
| KXBTC15M-26MAY070600-00 | yes | 0.723960 | 0.670000 | 0.053960 | 0.495921 | 0.394421 | 534.677000 | True | 62.000000 | calm_recross, boundary_geometry, book_discount_ge_4pp, middle_time_120_720s |
| KXBTC15M-26MAY070645-45 | yes | 0.895399 | 0.810000 | 0.085399 | 1.013529 | 0.368798 | 816.468000 | True | 35.000000 | calm_recross, deep_geometry, book_discount_ge_4pp, late_or_extreme_time |
| KXBTC15M-26MAY070745-45 | yes | 0.903807 | 0.680000 | 0.223807 | 1.081343 | 0.197594 | 474.481000 | True | 32.000000 | calm_recross, deep_geometry, book_discount_ge_4pp, middle_time_120_720s |
| KXBTC15M-26MAY070915-15 | no | 0.788001 | 0.750000 | 0.038001 | 0.676857 | 0.519751 | 819.337000 | True | 47.000000 | late_or_extreme_time |
| KXBTC15M-26MAY071230-30 | no | 0.729882 | 0.700000 | 0.029882 | 0.573733 | 0.815016 | 863.492000 | False | -143.000000 | turbulent_recross, boundary_geometry, thin_edge_lt_3pp, late_or_extreme_time |
