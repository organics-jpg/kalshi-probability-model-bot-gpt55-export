# v28 Target-Coverage FV Bucket Reliability

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Overlay: `book_probability`
- Rows: `112`
- Raw/overlay ECE: `0.111357/0.028929`
- ECE delta overlay-minus-raw: `-0.082428`
- Flags: `some_overlay_buckets_lt_10`

## Interpretation

- Overlay improves bucket ECE versus raw in this tiny forward sample (0.028928571428571415 vs 0.1113570714285714).
- At least one non-empty bucket has fewer than 10 rows; Wilson intervals are wide.

## Raw Buckets

| bucket | count | W/L | avg p | win rate | Wilson 95% | error | brier | reliable |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| 50_60 | 36 | 17/19 | 0.549921 | 0.472222 | 0.319858-0.629943 | -0.077699 | 0.243273 | True |
| 60_70 | 45 | 21/24 | 0.634533 | 0.466667 | 0.329349-0.609228 | -0.167867 | 0.273601 | True |
| 70_80 | 18 | 13/5 | 0.749753 | 0.722222 | 0.491269-0.875004 | -0.027531 | 0.196419 | True |
| 80_90 | 9 | 9/0 | 0.850552 | 1.000000 | 0.700847-1.000000 | 0.149448 | 0.023092 | False |
| 90_100 | 4 | 4/0 | 0.929939 | 1.000000 | 0.510100-1.000000 | 0.070061 | 0.005598 | False |

## Overlay Buckets

| bucket | count | W/L | avg p | win rate | Wilson 95% | error | brier | reliable |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| 50_60 | 27 | 14/13 | 0.545185 | 0.518519 | 0.339853-0.692570 | -0.026667 | 0.252378 | True |
| 60_70 | 29 | 18/11 | 0.634483 | 0.620690 | 0.440022-0.773122 | -0.013793 | 0.227538 | True |
| 70_80 | 14 | 11/3 | 0.742857 | 0.785714 | 0.524103-0.924288 | 0.042857 | 0.171257 | True |
| 80_90 | 9 | 9/0 | 0.831111 | 1.000000 | 0.700847-1.000000 | 0.168889 | 0.029422 | False |
| 90_100 | 0 | 0/0 | None | None | None-None | None | None | False |
