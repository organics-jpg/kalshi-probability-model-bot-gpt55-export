# v28 Frozen Convex Raw-Escape Challengers

Rows before this freeze do not count. These candidates were created after the first raw-convexity frozen win.

- Freeze timestamp UTC: `2026-05-05T22:33:33.421286+00:00`
- Forward market denominator: `155`
- Excluded in-progress post-freeze markets: `1`
- Future candidate rows: `304`

## Forward Scorecard

| policy | entries | settled | wins/losses | coverage | net c | avg brier | raw escape | wait | actual/shadow | FV blockers | execution blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| raw_edge20_else_first_side_raw_later_book_p60_edge0 | 152 | 152 | 79/73 | 98.064516 | -4099.000000 | 0.248078 | 10 | 139 | 4/148 | coverage_too_high, net_not_positive | simulated_share_gt_0.35, coverage_too_high, net_not_positive |
| raw_edge20_else_rmt_repetition_forget_p60_edge0 | 152 | 152 | 83/69 | 98.064516 | -3556.000000 | 0.241077 | 10 | 139 | 4/148 | coverage_too_high, net_not_positive | simulated_share_gt_0.35, coverage_too_high, net_not_positive |

## Missed Forward Markets

- `raw_edge20_else_first_side_raw_later_book_p60_edge0` missed `3`: KXBTC15M-26MAY051930-30, KXBTC15M-26MAY060430-30, KXBTC15M-26MAY061845-45
- `raw_edge20_else_rmt_repetition_forget_p60_edge0` missed `3`: KXBTC15M-26MAY051930-30, KXBTC15M-26MAY060430-30, KXBTC15M-26MAY061845-45

## Selected Forward Rows

### raw_edge20_else_first_side_raw_later_book_p60_edge0
| market | ts | side | source | obs idx | stc | p_eff | raw p | ask | edge | won | net c |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY071115-15 | 2026-05-07T15:00:56.671254+00:00 | no | rejected_actionable | 5 | 843.330000 | 0.620000 | 0.635838 | 0.620000 | 0.000000 | False | -128.000000 |
| KXBTC15M-26MAY071130-30 | 2026-05-07T15:16:35.878761+00:00 | yes | rejected_actionable | 6 | 804.123000 | 0.600000 | 0.578836 | 0.600000 | 0.000000 | False | -124.000000 |
| KXBTC15M-26MAY071145-45 | 2026-05-07T15:30:41.084707+00:00 | yes | rejected_actionable | 0 | 858.916000 | 0.645637 | 0.645637 | 0.610000 | 0.035637 | True | 74.000000 |
| KXBTC15M-26MAY071200-00 | 2026-05-07T15:46:03.341926+00:00 | yes | rejected_actionable | 2 | 836.659000 | 0.630000 | 0.617828 | 0.630000 | 0.000000 | False | -130.000000 |
| KXBTC15M-26MAY071215-15 | 2026-05-07T16:02:38.072749+00:00 | yes | rejected_actionable | 12 | 741.928000 | 0.600000 | 0.620750 | 0.600000 | 0.000000 | False | -124.000000 |
| KXBTC15M-26MAY071230-30 | 2026-05-07T16:15:36.510038+00:00 | no | rejected_actionable | 3 | 863.492000 | 0.700000 | 0.729882 | 0.700000 | 0.000000 | False | -143.000000 |
| KXBTC15M-26MAY071245-45 | 2026-05-07T16:33:21.276114+00:00 | yes | rejected_actionable | 18 | 698.724000 | 0.650000 | 0.668302 | 0.650000 | 0.000000 | False | -134.000000 |
| KXBTC15M-26MAY071300-00 | 2026-05-07T16:45:57.486009+00:00 | yes | rejected_actionable | 0 | 842.515000 | 0.636040 | 0.636040 | 0.590000 | 0.046040 | False | -122.000000 |
| KXBTC15M-26MAY071315-15 | 2026-05-07T17:03:02.531145+00:00 | yes | rejected_actionable | 14 | 717.470000 | 0.700000 | 0.743772 | 0.700000 | 0.000000 | True | 57.000000 |
| KXBTC15M-26MAY071330-30 | 2026-05-07T17:16:51.282524+00:00 | no | rejected_actionable | 9 | 788.722000 | 0.650000 | 0.595517 | 0.650000 | 0.000000 | True | 66.000000 |
### raw_edge20_else_rmt_repetition_forget_p60_edge0
| market | ts | side | source | obs idx | stc | p_eff | raw p | ask | edge | won | net c |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY071115-15 | 2026-05-07T15:00:56.671254+00:00 | no | rejected_actionable | 5 | 843.330000 | 0.620000 | 0.635838 | 0.620000 | 0.000000 | False | -128.000000 |
| KXBTC15M-26MAY071130-30 | 2026-05-07T15:16:35.878761+00:00 | yes | rejected_actionable | 6 | 804.123000 | 0.600000 | 0.578836 | 0.600000 | 0.000000 | False | -124.000000 |
| KXBTC15M-26MAY071145-45 | 2026-05-07T15:30:41.084707+00:00 | yes | rejected_actionable | 0 | 858.916000 | 0.627819 | 0.645637 | 0.610000 | 0.017819 | True | 74.000000 |
| KXBTC15M-26MAY071200-00 | 2026-05-07T15:46:03.341926+00:00 | yes | rejected_actionable | 2 | 836.659000 | 0.630000 | 0.617828 | 0.630000 | 0.000000 | False | -130.000000 |
| KXBTC15M-26MAY071215-15 | 2026-05-07T16:02:38.072749+00:00 | yes | rejected_actionable | 12 | 741.928000 | 0.600000 | 0.620750 | 0.600000 | 0.000000 | False | -124.000000 |
| KXBTC15M-26MAY071230-30 | 2026-05-07T16:15:36.510038+00:00 | no | rejected_actionable | 3 | 863.492000 | 0.700000 | 0.729882 | 0.700000 | 0.000000 | False | -143.000000 |
| KXBTC15M-26MAY071245-45 | 2026-05-07T16:33:21.276114+00:00 | yes | rejected_actionable | 18 | 698.724000 | 0.650000 | 0.668302 | 0.650000 | 0.000000 | False | -134.000000 |
| KXBTC15M-26MAY071300-00 | 2026-05-07T16:45:57.486009+00:00 | yes | rejected_actionable | 0 | 842.515000 | 0.613020 | 0.636040 | 0.590000 | 0.023020 | False | -122.000000 |
| KXBTC15M-26MAY071315-15 | 2026-05-07T17:03:02.531145+00:00 | yes | rejected_actionable | 14 | 717.470000 | 0.700000 | 0.743772 | 0.700000 | 0.000000 | True | 57.000000 |
| KXBTC15M-26MAY071330-30 | 2026-05-07T17:16:51.282524+00:00 | no | rejected_actionable | 9 | 788.722000 | 0.650000 | 0.595517 | 0.650000 | 0.000000 | True | 66.000000 |
