# v28 Frozen Side-Agreement Challengers

Rows before this freeze do not count. These candidates were created after observing side-flip timing behavior.

- Freeze timestamp UTC: `2026-05-05T22:28:58.054865+00:00`
- Forward market denominator: `156`
- Excluded in-progress post-freeze markets: `0`
- Future candidate rows: `306`

## Forward Scorecard

| policy | entries | settled | wins/losses | coverage | net c | avg brier | actual/shadow | FV blockers | execution blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| raw_when_same_else_first_side_raw_later_book_p60_edge0 | 150 | 150 | 86/64 | 96.153846 | -2071.000000 | 0.229154 | 8/142 | coverage_too_high, net_not_positive | simulated_share_gt_0.35, coverage_too_high, net_not_positive |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | 150 | 150 | 89/61 | 96.153846 | -1694.000000 | 0.223355 | 8/142 | coverage_too_high, net_not_positive | simulated_share_gt_0.35, coverage_too_high, net_not_positive |

## Missed Forward Markets

- `raw_when_same_else_first_side_raw_later_book_p60_edge0` missed `6`: KXBTC15M-26MAY051930-30, KXBTC15M-26MAY060400-00, KXBTC15M-26MAY060430-30, KXBTC15M-26MAY061845-45, KXBTC15M-26MAY062330-30, KXBTC15M-26MAY070800-00
- `raw_when_same_else_rmt_repetition_forget_p60_edge0` missed `6`: KXBTC15M-26MAY051930-30, KXBTC15M-26MAY060400-00, KXBTC15M-26MAY060430-30, KXBTC15M-26MAY061845-45, KXBTC15M-26MAY062330-30, KXBTC15M-26MAY070800-00

## Selected Forward Rows

### raw_when_same_else_first_side_raw_later_book_p60_edge0
| market | ts | side | source | obs idx | stc | p_eff | raw p | ask | edge | won | net c |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY071115-15 | 2026-05-07T15:00:56.671254+00:00 | no | rejected_actionable | 5 | 843.330000 | 0.635838 | 0.635838 | 0.620000 | 0.015838 | False | -128.000000 |
| KXBTC15M-26MAY071130-30 | 2026-05-07T15:16:35.878761+00:00 | yes | rejected_actionable | 6 | 804.123000 | 0.600000 | 0.578836 | 0.600000 | 0.000000 | False | -124.000000 |
| KXBTC15M-26MAY071145-45 | 2026-05-07T15:30:41.084707+00:00 | yes | rejected_actionable | 0 | 858.916000 | 0.645637 | 0.645637 | 0.610000 | 0.035637 | True | 74.000000 |
| KXBTC15M-26MAY071200-00 | 2026-05-07T15:46:46.178909+00:00 | yes | rejected_actionable | 6 | 793.821000 | 0.606055 | 0.606055 | 0.600000 | 0.006055 | False | -124.000000 |
| KXBTC15M-26MAY071215-15 | 2026-05-07T16:00:35.776954+00:00 | yes | rejected_actionable | 0 | 864.223000 | 0.509397 | 0.509397 | 0.470000 | 0.039397 | False | -98.000000 |
| KXBTC15M-26MAY071230-30 | 2026-05-07T16:15:36.510038+00:00 | no | rejected_actionable | 3 | 863.492000 | 0.729882 | 0.729882 | 0.700000 | 0.029882 | False | -143.000000 |
| KXBTC15M-26MAY071245-45 | 2026-05-07T16:30:15.640699+00:00 | yes | rejected_actionable | 0 | 884.360000 | 0.559979 | 0.559979 | 0.550000 | 0.009979 | False | -114.000000 |
| KXBTC15M-26MAY071300-00 | 2026-05-07T16:45:57.486009+00:00 | yes | rejected_actionable | 0 | 842.515000 | 0.636040 | 0.636040 | 0.590000 | 0.046040 | False | -122.000000 |
| KXBTC15M-26MAY071315-15 | 2026-05-07T17:00:41.152188+00:00 | yes | rejected_actionable | 0 | 858.849000 | 0.533442 | 0.533442 | 0.510000 | 0.023442 | True | 94.000000 |
| KXBTC15M-26MAY071330-30 | 2026-05-07T17:16:51.282524+00:00 | no | rejected_actionable | 9 | 788.722000 | 0.650000 | 0.595517 | 0.650000 | 0.000000 | True | 66.000000 |
### raw_when_same_else_rmt_repetition_forget_p60_edge0
| market | ts | side | source | obs idx | stc | p_eff | raw p | ask | edge | won | net c |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY071115-15 | 2026-05-07T15:00:56.671254+00:00 | no | rejected_actionable | 5 | 843.330000 | 0.635838 | 0.635838 | 0.620000 | 0.015838 | False | -128.000000 |
| KXBTC15M-26MAY071130-30 | 2026-05-07T15:16:35.878761+00:00 | yes | rejected_actionable | 6 | 804.123000 | 0.600000 | 0.578836 | 0.600000 | 0.000000 | False | -124.000000 |
| KXBTC15M-26MAY071145-45 | 2026-05-07T15:30:41.084707+00:00 | yes | rejected_actionable | 0 | 858.916000 | 0.645637 | 0.645637 | 0.610000 | 0.035637 | True | 74.000000 |
| KXBTC15M-26MAY071200-00 | 2026-05-07T15:46:46.178909+00:00 | yes | rejected_actionable | 6 | 793.821000 | 0.606055 | 0.606055 | 0.600000 | 0.006055 | False | -124.000000 |
| KXBTC15M-26MAY071215-15 | 2026-05-07T16:00:35.776954+00:00 | yes | rejected_actionable | 0 | 864.223000 | 0.509397 | 0.509397 | 0.470000 | 0.039397 | False | -98.000000 |
| KXBTC15M-26MAY071230-30 | 2026-05-07T16:15:36.510038+00:00 | no | rejected_actionable | 3 | 863.492000 | 0.729882 | 0.729882 | 0.700000 | 0.029882 | False | -143.000000 |
| KXBTC15M-26MAY071245-45 | 2026-05-07T16:30:15.640699+00:00 | yes | rejected_actionable | 0 | 884.360000 | 0.559979 | 0.559979 | 0.550000 | 0.009979 | False | -114.000000 |
| KXBTC15M-26MAY071300-00 | 2026-05-07T16:45:57.486009+00:00 | yes | rejected_actionable | 0 | 842.515000 | 0.636040 | 0.636040 | 0.590000 | 0.046040 | False | -122.000000 |
| KXBTC15M-26MAY071315-15 | 2026-05-07T17:00:41.152188+00:00 | yes | rejected_actionable | 0 | 858.849000 | 0.533442 | 0.533442 | 0.510000 | 0.023442 | True | 94.000000 |
| KXBTC15M-26MAY071330-30 | 2026-05-07T17:16:51.282524+00:00 | no | rejected_actionable | 9 | 788.722000 | 0.650000 | 0.595517 | 0.650000 | 0.000000 | True | 66.000000 |
