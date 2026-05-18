# v28 Frozen Forward Candidates

Forward-only scorecard. Rows before freeze timestamp do not count.

- Freeze timestamp UTC: `2026-05-05T22:07:37.064896+00:00`
- Current watched-market denominator: `181`
- Forward market denominator: `157`
- Excluded in-progress post-freeze markets: `1`
- Future candidate rows: `5306`

## Frozen Policies

- `first_side_raw_later_book_p60_edge0` (primary_calibrated_broad_candidate): Retain raw v28 only on first market-side observation, then forget stale geometry and anchor to book. Requires effective p >= 0.60 and nonnegative effective edge.
- `rmt_repetition_forget_p60_edge0` (primary_rmt_forgetting_candidate): Use RMT regime plus repeated-side state to decide how aggressively to forget v28 and anchor to book. Requires effective p >= 0.60 and nonnegative effective edge.
- `book_ask_prior_p60_edge0` (book_favorite_control): Pure executable book favorite control. Tests whether the edge is just book favorites above 60c.
- `v28_raw_p50_edge0` (raw_broad_control): Raw v28 broad control. Kept to test whether better P&L is unstable over time despite weaker calibration.

## Forward Scorecard

| policy | entries | settled | wins/losses | coverage | net c | avg brier | actual/shadow | FV blockers | execution blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| first_side_raw_later_book_p60_edge0 | 153 | 153 | 88/65 | 97.452229 | -3318.000000 | 0.234672 | 4/149 | coverage_too_high, net_not_positive | simulated_share_gt_0.35, coverage_too_high, net_not_positive |
| rmt_repetition_forget_p60_edge0 | 153 | 153 | 91/62 | 97.452229 | -3048.000000 | 0.229999 | 4/149 | coverage_too_high, net_not_positive | simulated_share_gt_0.35, coverage_too_high, net_not_positive |
| book_ask_prior_p60_edge0 | 155 | 155 | 93/62 | 98.726115 | -2777.000000 | 0.234683 | 3/152 | coverage_too_high, net_not_positive | simulated_share_gt_0.35, coverage_too_high, net_not_positive |
| v28_raw_p50_edge0 | 154 | 154 | 87/67 | 98.089172 | -627.000000 | 0.227638 | 8/146 | coverage_too_high, net_not_positive | simulated_share_gt_0.35, coverage_too_high, net_not_positive |

## Missed Forward Markets

- `first_side_raw_later_book_p60_edge0` missed `4`: KXBTC15M-26MAY060400-00, KXBTC15M-26MAY060430-30, KXBTC15M-26MAY062330-30, KXBTC15M-26MAY070800-00
  - `KXBTC15M-26MAY060400-00` reason `unknown_selection_miss`, best side `no`, p_eff `0.990000`, ask `0.990000`, edge `0.000000`, raw_p `0.988755`
  - `KXBTC15M-26MAY060430-30` reason `edge_below_threshold`, best side `no`, p_eff `0.621335`, ask `0.680000`, edge `-0.058665`, raw_p `0.621335`
  - `KXBTC15M-26MAY062330-30` reason `unknown_selection_miss`, best side `no`, p_eff `0.960000`, ask `0.960000`, edge `0.000000`, raw_p `0.445364`
  - `KXBTC15M-26MAY070800-00` reason `unknown_selection_miss`, best side `no`, p_eff `0.990000`, ask `0.990000`, edge `0.000000`, raw_p `0.997043`
- `rmt_repetition_forget_p60_edge0` missed `4`: KXBTC15M-26MAY060400-00, KXBTC15M-26MAY060430-30, KXBTC15M-26MAY062330-30, KXBTC15M-26MAY070800-00
  - `KXBTC15M-26MAY060400-00` reason `unknown_selection_miss`, best side `no`, p_eff `0.990000`, ask `0.990000`, edge `0.000000`, raw_p `0.988755`
  - `KXBTC15M-26MAY060430-30` reason `edge_below_threshold`, best side `no`, p_eff `0.650667`, ask `0.680000`, edge `-0.029333`, raw_p `0.621335`
  - `KXBTC15M-26MAY062330-30` reason `unknown_selection_miss`, best side `no`, p_eff `0.960000`, ask `0.960000`, edge `0.000000`, raw_p `0.445364`
  - `KXBTC15M-26MAY070800-00` reason `unknown_selection_miss`, best side `no`, p_eff `0.990000`, ask `0.990000`, edge `0.000000`, raw_p `0.997043`
- `book_ask_prior_p60_edge0` missed `2`: KXBTC15M-26MAY062330-30, KXBTC15M-26MAY070800-00
  - `KXBTC15M-26MAY062330-30` reason `unknown_selection_miss`, best side `no`, p_eff `0.960000`, ask `0.960000`, edge `0.000000`, raw_p `0.445364`
  - `KXBTC15M-26MAY070800-00` reason `unknown_selection_miss`, best side `no`, p_eff `0.990000`, ask `0.990000`, edge `0.000000`, raw_p `0.997043`
- `v28_raw_p50_edge0` missed `3`: KXBTC15M-26MAY051930-30, KXBTC15M-26MAY060430-30, KXBTC15M-26MAY061845-45
  - `KXBTC15M-26MAY051930-30` reason `edge_below_threshold`, best side `no`, p_eff `0.901032`, ask `0.950000`, edge `-0.048968`, raw_p `0.901032`
  - `KXBTC15M-26MAY060430-30` reason `edge_below_threshold`, best side `no`, p_eff `0.621335`, ask `0.680000`, edge `-0.058665`, raw_p `0.621335`
  - `KXBTC15M-26MAY061845-45` reason `edge_below_threshold`, best side `yes`, p_eff `0.944524`, ask `0.960000`, edge `-0.015476`, raw_p `0.944524`

## Excluded In-Progress Markets

KXBTC15M-26MAY051815-15

## Selected Forward Rows

### first_side_raw_later_book_p60_edge0
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
### rmt_repetition_forget_p60_edge0
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
### book_ask_prior_p60_edge0
| market | ts | side | source | obs idx | stc | p_eff | raw p | ask | edge | won | net c |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY071115-15 | 2026-05-07T15:00:56.671254+00:00 | no | rejected_actionable | 5 | 843.330000 | 0.620000 | 0.635838 | 0.620000 | 0.000000 | False | -128.000000 |
| KXBTC15M-26MAY071130-30 | 2026-05-07T15:16:35.878761+00:00 | yes | rejected_actionable | 6 | 804.123000 | 0.600000 | 0.578836 | 0.600000 | 0.000000 | False | -124.000000 |
| KXBTC15M-26MAY071145-45 | 2026-05-07T15:30:41.084707+00:00 | yes | rejected_actionable | 0 | 858.916000 | 0.610000 | 0.645637 | 0.610000 | 0.000000 | True | 74.000000 |
| KXBTC15M-26MAY071200-00 | 2026-05-07T15:45:41.700197+00:00 | yes | rejected_actionable | 0 | 858.300000 | 0.620000 | 0.602725 | 0.620000 | 0.000000 | False | -128.000000 |
| KXBTC15M-26MAY071215-15 | 2026-05-07T16:02:38.072749+00:00 | yes | rejected_actionable | 12 | 741.928000 | 0.600000 | 0.620750 | 0.600000 | 0.000000 | False | -124.000000 |
| KXBTC15M-26MAY071230-30 | 2026-05-07T16:15:16.499343+00:00 | no | rejected_actionable | 1 | 883.503000 | 0.620000 | 0.595931 | 0.620000 | 0.000000 | False | -128.000000 |
| KXBTC15M-26MAY071245-45 | 2026-05-07T16:33:21.276114+00:00 | yes | rejected_actionable | 18 | 698.724000 | 0.650000 | 0.668302 | 0.650000 | 0.000000 | False | -134.000000 |
| KXBTC15M-26MAY071300-00 | 2026-05-07T16:46:17.493781+00:00 | yes | rejected_actionable | 2 | 822.506000 | 0.680000 | 0.706312 | 0.680000 | 0.000000 | False | -140.000000 |
| KXBTC15M-26MAY071315-15 | 2026-05-07T17:03:02.531145+00:00 | yes | rejected_actionable | 14 | 717.470000 | 0.700000 | 0.743772 | 0.700000 | 0.000000 | True | 57.000000 |
| KXBTC15M-26MAY071330-30 | 2026-05-07T17:15:30.496075+00:00 | no | rejected_actionable | 1 | 869.509000 | 0.600000 | 0.576763 | 0.600000 | 0.000000 | True | 76.000000 |
### v28_raw_p50_edge0
| market | ts | side | source | obs idx | stc | p_eff | raw p | ask | edge | won | net c |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY071115-15 | 2026-05-07T15:00:56.671254+00:00 | no | rejected_actionable | 5 | 843.330000 | 0.635838 | 0.635838 | 0.620000 | 0.015838 | False | -128.000000 |
| KXBTC15M-26MAY071130-30 | 2026-05-07T15:17:58.079448+00:00 | no | rejected_actionable | 15 | 721.923000 | 0.582087 | 0.582087 | 0.580000 | 0.002087 | True | 80.000000 |
| KXBTC15M-26MAY071145-45 | 2026-05-07T15:30:41.084707+00:00 | yes | rejected_actionable | 0 | 858.916000 | 0.645637 | 0.645637 | 0.610000 | 0.035637 | True | 74.000000 |
| KXBTC15M-26MAY071200-00 | 2026-05-07T15:46:46.178909+00:00 | yes | rejected_actionable | 6 | 793.821000 | 0.606055 | 0.606055 | 0.600000 | 0.006055 | False | -124.000000 |
| KXBTC15M-26MAY071215-15 | 2026-05-07T16:00:35.776954+00:00 | yes | rejected_actionable | 0 | 864.223000 | 0.509397 | 0.509397 | 0.470000 | 0.039397 | False | -98.000000 |
| KXBTC15M-26MAY071230-30 | 2026-05-07T16:15:36.510038+00:00 | no | rejected_actionable | 3 | 863.492000 | 0.729882 | 0.729882 | 0.700000 | 0.029882 | False | -143.000000 |
| KXBTC15M-26MAY071245-45 | 2026-05-07T16:30:15.640699+00:00 | yes | rejected_actionable | 0 | 884.360000 | 0.559979 | 0.559979 | 0.550000 | 0.009979 | False | -114.000000 |
| KXBTC15M-26MAY071300-00 | 2026-05-07T16:45:57.486009+00:00 | yes | rejected_actionable | 0 | 842.515000 | 0.636040 | 0.636040 | 0.590000 | 0.046040 | False | -122.000000 |
| KXBTC15M-26MAY071315-15 | 2026-05-07T17:00:41.152188+00:00 | yes | rejected_actionable | 0 | 858.849000 | 0.533442 | 0.533442 | 0.510000 | 0.023442 | True | 94.000000 |
| KXBTC15M-26MAY071330-30 | 2026-05-07T17:15:50.488414+00:00 | yes | rejected_actionable | 2 | 849.512000 | 0.544206 | 0.544206 | 0.520000 | 0.024206 | False | -108.000000 |
