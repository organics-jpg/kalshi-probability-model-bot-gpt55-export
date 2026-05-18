# v28 Frozen Threshold Challengers

Second-wave candidates frozen after the p60 clean-forward miss. Rows before this freeze do not count.

- Freeze timestamp UTC: `2026-05-05T22:19:18.149284+00:00`
- Forward market denominator: `156`
- Excluded in-progress post-freeze markets: `1`
- Future candidate rows: `5270`

## Forward Scorecard

| policy | entries | settled | wins/losses | coverage | net c | avg brier | actual/shadow | FV blockers | execution blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| first_side_raw_later_book_p58_edge0 | 152 | 152 | 89/63 | 97.435897 | -2557.000000 | 0.228361 | 4/148 | coverage_too_high, net_not_positive | simulated_share_gt_0.35, coverage_too_high, net_not_positive |
| rmt_repetition_forget_p58_edge0 | 152 | 152 | 88/64 | 97.435897 | -3210.000000 | 0.230127 | 4/148 | coverage_too_high, net_not_positive | simulated_share_gt_0.35, coverage_too_high, net_not_positive |

## Missed Forward Markets

- `first_side_raw_later_book_p58_edge0` missed `4`: KXBTC15M-26MAY060400-00, KXBTC15M-26MAY060430-30, KXBTC15M-26MAY062330-30, KXBTC15M-26MAY070800-00
- `rmt_repetition_forget_p58_edge0` missed `4`: KXBTC15M-26MAY060400-00, KXBTC15M-26MAY060430-30, KXBTC15M-26MAY062330-30, KXBTC15M-26MAY070800-00

## Selected Forward Rows

### first_side_raw_later_book_p58_edge0
| market | ts | side | source | obs idx | stc | p_eff | raw p | ask | edge | won | net c |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY071115-15 | 2026-05-07T15:00:56.671254+00:00 | no | rejected_actionable | 5 | 843.330000 | 0.620000 | 0.635838 | 0.620000 | 0.000000 | False | -128.000000 |
| KXBTC15M-26MAY071130-30 | 2026-05-07T15:16:35.878761+00:00 | yes | rejected_actionable | 6 | 804.123000 | 0.600000 | 0.578836 | 0.600000 | 0.000000 | False | -124.000000 |
| KXBTC15M-26MAY071145-45 | 2026-05-07T15:30:41.084707+00:00 | yes | rejected_actionable | 0 | 858.916000 | 0.645637 | 0.645637 | 0.610000 | 0.035637 | True | 74.000000 |
| KXBTC15M-26MAY071200-00 | 2026-05-07T15:46:03.341926+00:00 | yes | rejected_actionable | 2 | 836.659000 | 0.630000 | 0.617828 | 0.630000 | 0.000000 | False | -130.000000 |
| KXBTC15M-26MAY071215-15 | 2026-05-07T16:02:18.035150+00:00 | yes | rejected_actionable | 10 | 761.966000 | 0.590000 | 0.615913 | 0.590000 | 0.000000 | False | -122.000000 |
| KXBTC15M-26MAY071230-30 | 2026-05-07T16:15:36.510038+00:00 | no | rejected_actionable | 3 | 863.492000 | 0.700000 | 0.729882 | 0.700000 | 0.000000 | False | -143.000000 |
| KXBTC15M-26MAY071245-45 | 2026-05-07T16:32:35.638990+00:00 | yes | rejected_actionable | 14 | 744.362000 | 0.580000 | 0.584604 | 0.580000 | 0.000000 | False | -120.000000 |
| KXBTC15M-26MAY071300-00 | 2026-05-07T16:45:57.486009+00:00 | yes | rejected_actionable | 0 | 842.515000 | 0.636040 | 0.636040 | 0.590000 | 0.046040 | False | -122.000000 |
| KXBTC15M-26MAY071315-15 | 2026-05-07T17:03:02.531145+00:00 | yes | rejected_actionable | 14 | 717.470000 | 0.700000 | 0.743772 | 0.700000 | 0.000000 | True | 57.000000 |
| KXBTC15M-26MAY071330-30 | 2026-05-07T17:16:10.498045+00:00 | no | rejected_actionable | 5 | 829.504000 | 0.580000 | 0.535286 | 0.580000 | 0.000000 | True | 80.000000 |
### rmt_repetition_forget_p58_edge0
| market | ts | side | source | obs idx | stc | p_eff | raw p | ask | edge | won | net c |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY071115-15 | 2026-05-07T15:00:56.671254+00:00 | no | rejected_actionable | 5 | 843.330000 | 0.620000 | 0.635838 | 0.620000 | 0.000000 | False | -128.000000 |
| KXBTC15M-26MAY071130-30 | 2026-05-07T15:16:35.878761+00:00 | yes | rejected_actionable | 6 | 804.123000 | 0.600000 | 0.578836 | 0.600000 | 0.000000 | False | -124.000000 |
| KXBTC15M-26MAY071145-45 | 2026-05-07T15:30:41.084707+00:00 | yes | rejected_actionable | 0 | 858.916000 | 0.627819 | 0.645637 | 0.610000 | 0.017819 | True | 74.000000 |
| KXBTC15M-26MAY071200-00 | 2026-05-07T15:46:03.341926+00:00 | yes | rejected_actionable | 2 | 836.659000 | 0.630000 | 0.617828 | 0.630000 | 0.000000 | False | -130.000000 |
| KXBTC15M-26MAY071215-15 | 2026-05-07T16:02:18.035150+00:00 | yes | rejected_actionable | 10 | 761.966000 | 0.590000 | 0.615913 | 0.590000 | 0.000000 | False | -122.000000 |
| KXBTC15M-26MAY071230-30 | 2026-05-07T16:15:36.510038+00:00 | no | rejected_actionable | 3 | 863.492000 | 0.700000 | 0.729882 | 0.700000 | 0.000000 | False | -143.000000 |
| KXBTC15M-26MAY071245-45 | 2026-05-07T16:32:35.638990+00:00 | yes | rejected_actionable | 14 | 744.362000 | 0.580000 | 0.584604 | 0.580000 | 0.000000 | False | -120.000000 |
| KXBTC15M-26MAY071300-00 | 2026-05-07T16:45:57.486009+00:00 | yes | rejected_actionable | 0 | 842.515000 | 0.613020 | 0.636040 | 0.590000 | 0.023020 | False | -122.000000 |
| KXBTC15M-26MAY071315-15 | 2026-05-07T17:03:02.531145+00:00 | yes | rejected_actionable | 14 | 717.470000 | 0.700000 | 0.743772 | 0.700000 | 0.000000 | True | 57.000000 |
| KXBTC15M-26MAY071330-30 | 2026-05-07T17:16:10.498045+00:00 | no | rejected_actionable | 5 | 829.504000 | 0.580000 | 0.535286 | 0.580000 | 0.000000 | True | 80.000000 |
