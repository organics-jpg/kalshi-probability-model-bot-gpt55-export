# v28 Frozen Book-Exact Entry Gate

Shadow-only validator. A candidate row counts only when the effective FV equals executable book probability.

- Freeze timestamp UTC: `2026-05-06T11:33:52.584603+00:00`
- Forward denominator markets: `103`
- Diagnostic denominator markets: `181`
- Any promotion ready: `False`

## Scorecard

| policy | window | entries | settled | W/L | coverage | net c | avg net c | actual/sim | sim share | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| first_side_raw_later_book_p58_edge0 | diagnostic | 120 | 120 | 73/47 | 66.298343 | -1791.000000 | -14.925000 | 1/119 | 0.991667 | coverage_too_low, net_not_positive, simulated_share_gt_35pct |
| first_side_raw_later_book_p58_edge0 | future | 71 | 71 | 36/35 | 68.932039 | -2630.000000 | -37.042254 | 1/70 | 0.985915 | coverage_too_low, net_not_positive, simulated_share_gt_35pct |
| first_side_raw_later_book_p60_edge0 | diagnostic | 130 | 130 | 79/51 | 71.823204 | -2205.000000 | -16.961538 | 1/129 | 0.992308 | coverage_too_low, net_not_positive, simulated_share_gt_35pct |
| first_side_raw_later_book_p60_edge0 | future | 75 | 75 | 40/35 | 72.815534 | -2560.000000 | -34.133333 | 1/74 | 0.986667 | coverage_too_low, net_not_positive, simulated_share_gt_35pct |
| rmt_repetition_forget_p58_edge0 | diagnostic | 135 | 135 | 79/56 | 74.585635 | -2632.000000 | -19.496296 | 1/134 | 0.992593 | coverage_too_low, net_not_positive, simulated_share_gt_35pct |
| rmt_repetition_forget_p58_edge0 | future | 79 | 79 | 39/40 | 76.699029 | -3077.000000 | -38.949367 | 1/78 | 0.987342 | net_not_positive, simulated_share_gt_35pct |
| rmt_repetition_forget_p60_edge0 | diagnostic | 140 | 140 | 85/55 | 77.348066 | -2376.000000 | -16.971429 | 1/139 | 0.992857 | net_not_positive, simulated_share_gt_35pct |
| rmt_repetition_forget_p60_edge0 | future | 82 | 82 | 44/38 | 79.611650 | -2672.000000 | -32.585366 | 1/81 | 0.987805 | net_not_positive, simulated_share_gt_35pct |

## Physics

- `first_side_raw_later_book_p58_edge0`: When stale v28 geometry is fully forgotten and the effective probability equals the book, require book-favorite state to carry the trade.
- `first_side_raw_later_book_p60_edge0`: Same as p58, but only when the executable book favorite is at least 60%.
- `rmt_repetition_forget_p58_edge0`: Only accept repeated-side/RMT states after the model has fully collapsed to book probability.
- `rmt_repetition_forget_p60_edge0`: Same as p58 RMT repetition gate, with at least 60% book probability.

## Future Row Preview

### first_side_raw_later_book_p58_edge0
| market | ts | side | source | p_eff | raw p | ask | won | net c |
|---|---|---|---|---:|---:|---:|---|---:|
| KXBTC15M-26MAY070945-45 | 2026-05-07T13:31:39.502031+00:00 | no | rejected_actionable | 0.640000 | 0.705657 | 0.640000 | True | 68.000000 |
| KXBTC15M-26MAY071000-00 | 2026-05-07T13:45:51.046663+00:00 | no | rejected_actionable | 0.660000 | 0.720981 | 0.660000 | True | 64.000000 |
| KXBTC15M-26MAY071045-45 | 2026-05-07T14:31:17.155911+00:00 | no | rejected_actionable | 0.730000 | 0.826507 | 0.730000 | True | 51.000000 |
| KXBTC15M-26MAY071100-00 | 2026-05-07T14:46:42.179926+00:00 | yes | rejected_actionable | 0.590000 | 0.626780 | 0.590000 | False | -122.000000 |
| KXBTC15M-26MAY071115-15 | 2026-05-07T15:00:56.671254+00:00 | no | rejected_actionable | 0.620000 | 0.635838 | 0.620000 | False | -128.000000 |
| KXBTC15M-26MAY071130-30 | 2026-05-07T15:16:35.878761+00:00 | yes | rejected_actionable | 0.600000 | 0.578836 | 0.600000 | False | -124.000000 |
| KXBTC15M-26MAY071200-00 | 2026-05-07T15:46:03.341926+00:00 | yes | rejected_actionable | 0.630000 | 0.617828 | 0.630000 | False | -130.000000 |
| KXBTC15M-26MAY071215-15 | 2026-05-07T16:02:18.035150+00:00 | yes | rejected_actionable | 0.590000 | 0.615913 | 0.590000 | False | -122.000000 |
| KXBTC15M-26MAY071230-30 | 2026-05-07T16:15:36.510038+00:00 | no | rejected_actionable | 0.700000 | 0.729882 | 0.700000 | False | -143.000000 |
| KXBTC15M-26MAY071245-45 | 2026-05-07T16:32:35.638990+00:00 | yes | rejected_actionable | 0.580000 | 0.584604 | 0.580000 | False | -120.000000 |
| KXBTC15M-26MAY071315-15 | 2026-05-07T17:03:02.531145+00:00 | yes | rejected_actionable | 0.700000 | 0.743772 | 0.700000 | True | 57.000000 |
| KXBTC15M-26MAY071330-30 | 2026-05-07T17:16:10.498045+00:00 | no | rejected_actionable | 0.580000 | 0.535286 | 0.580000 | True | 80.000000 |
### first_side_raw_later_book_p60_edge0
| market | ts | side | source | p_eff | raw p | ask | won | net c |
|---|---|---|---|---:|---:|---:|---|---:|
| KXBTC15M-26MAY070945-45 | 2026-05-07T13:31:39.502031+00:00 | no | rejected_actionable | 0.640000 | 0.705657 | 0.640000 | True | 68.000000 |
| KXBTC15M-26MAY071000-00 | 2026-05-07T13:45:51.046663+00:00 | no | rejected_actionable | 0.660000 | 0.720981 | 0.660000 | True | 64.000000 |
| KXBTC15M-26MAY071045-45 | 2026-05-07T14:31:17.155911+00:00 | no | rejected_actionable | 0.730000 | 0.826507 | 0.730000 | True | 51.000000 |
| KXBTC15M-26MAY071100-00 | 2026-05-07T14:47:02.194123+00:00 | yes | rejected_actionable | 0.650000 | 0.678229 | 0.650000 | False | -134.000000 |
| KXBTC15M-26MAY071115-15 | 2026-05-07T15:00:56.671254+00:00 | no | rejected_actionable | 0.620000 | 0.635838 | 0.620000 | False | -128.000000 |
| KXBTC15M-26MAY071130-30 | 2026-05-07T15:16:35.878761+00:00 | yes | rejected_actionable | 0.600000 | 0.578836 | 0.600000 | False | -124.000000 |
| KXBTC15M-26MAY071200-00 | 2026-05-07T15:46:03.341926+00:00 | yes | rejected_actionable | 0.630000 | 0.617828 | 0.630000 | False | -130.000000 |
| KXBTC15M-26MAY071215-15 | 2026-05-07T16:02:38.072749+00:00 | yes | rejected_actionable | 0.600000 | 0.620750 | 0.600000 | False | -124.000000 |
| KXBTC15M-26MAY071230-30 | 2026-05-07T16:15:36.510038+00:00 | no | rejected_actionable | 0.700000 | 0.729882 | 0.700000 | False | -143.000000 |
| KXBTC15M-26MAY071245-45 | 2026-05-07T16:33:21.276114+00:00 | yes | rejected_actionable | 0.650000 | 0.668302 | 0.650000 | False | -134.000000 |
| KXBTC15M-26MAY071315-15 | 2026-05-07T17:03:02.531145+00:00 | yes | rejected_actionable | 0.700000 | 0.743772 | 0.700000 | True | 57.000000 |
| KXBTC15M-26MAY071330-30 | 2026-05-07T17:16:51.282524+00:00 | no | rejected_actionable | 0.650000 | 0.595517 | 0.650000 | True | 66.000000 |
### rmt_repetition_forget_p58_edge0
| market | ts | side | source | p_eff | raw p | ask | won | net c |
|---|---|---|---|---:|---:|---:|---|---:|
| KXBTC15M-26MAY070945-45 | 2026-05-07T13:31:39.502031+00:00 | no | rejected_actionable | 0.640000 | 0.705657 | 0.640000 | True | 68.000000 |
| KXBTC15M-26MAY071000-00 | 2026-05-07T13:45:51.046663+00:00 | no | rejected_actionable | 0.660000 | 0.720981 | 0.660000 | True | 64.000000 |
| KXBTC15M-26MAY071045-45 | 2026-05-07T14:31:17.155911+00:00 | no | rejected_actionable | 0.730000 | 0.826507 | 0.730000 | True | 51.000000 |
| KXBTC15M-26MAY071100-00 | 2026-05-07T14:46:42.179926+00:00 | yes | rejected_actionable | 0.590000 | 0.626780 | 0.590000 | False | -122.000000 |
| KXBTC15M-26MAY071115-15 | 2026-05-07T15:00:56.671254+00:00 | no | rejected_actionable | 0.620000 | 0.635838 | 0.620000 | False | -128.000000 |
| KXBTC15M-26MAY071130-30 | 2026-05-07T15:16:35.878761+00:00 | yes | rejected_actionable | 0.600000 | 0.578836 | 0.600000 | False | -124.000000 |
| KXBTC15M-26MAY071200-00 | 2026-05-07T15:46:03.341926+00:00 | yes | rejected_actionable | 0.630000 | 0.617828 | 0.630000 | False | -130.000000 |
| KXBTC15M-26MAY071215-15 | 2026-05-07T16:02:18.035150+00:00 | yes | rejected_actionable | 0.590000 | 0.615913 | 0.590000 | False | -122.000000 |
| KXBTC15M-26MAY071230-30 | 2026-05-07T16:15:36.510038+00:00 | no | rejected_actionable | 0.700000 | 0.729882 | 0.700000 | False | -143.000000 |
| KXBTC15M-26MAY071245-45 | 2026-05-07T16:32:35.638990+00:00 | yes | rejected_actionable | 0.580000 | 0.584604 | 0.580000 | False | -120.000000 |
| KXBTC15M-26MAY071315-15 | 2026-05-07T17:03:02.531145+00:00 | yes | rejected_actionable | 0.700000 | 0.743772 | 0.700000 | True | 57.000000 |
| KXBTC15M-26MAY071330-30 | 2026-05-07T17:16:10.498045+00:00 | no | rejected_actionable | 0.580000 | 0.535286 | 0.580000 | True | 80.000000 |
### rmt_repetition_forget_p60_edge0
| market | ts | side | source | p_eff | raw p | ask | won | net c |
|---|---|---|---|---:|---:|---:|---|---:|
| KXBTC15M-26MAY070945-45 | 2026-05-07T13:31:39.502031+00:00 | no | rejected_actionable | 0.640000 | 0.705657 | 0.640000 | True | 68.000000 |
| KXBTC15M-26MAY071000-00 | 2026-05-07T13:45:51.046663+00:00 | no | rejected_actionable | 0.660000 | 0.720981 | 0.660000 | True | 64.000000 |
| KXBTC15M-26MAY071045-45 | 2026-05-07T14:31:17.155911+00:00 | no | rejected_actionable | 0.730000 | 0.826507 | 0.730000 | True | 51.000000 |
| KXBTC15M-26MAY071100-00 | 2026-05-07T14:47:02.194123+00:00 | yes | rejected_actionable | 0.650000 | 0.678229 | 0.650000 | False | -134.000000 |
| KXBTC15M-26MAY071115-15 | 2026-05-07T15:00:56.671254+00:00 | no | rejected_actionable | 0.620000 | 0.635838 | 0.620000 | False | -128.000000 |
| KXBTC15M-26MAY071130-30 | 2026-05-07T15:16:35.878761+00:00 | yes | rejected_actionable | 0.600000 | 0.578836 | 0.600000 | False | -124.000000 |
| KXBTC15M-26MAY071200-00 | 2026-05-07T15:46:03.341926+00:00 | yes | rejected_actionable | 0.630000 | 0.617828 | 0.630000 | False | -130.000000 |
| KXBTC15M-26MAY071215-15 | 2026-05-07T16:02:38.072749+00:00 | yes | rejected_actionable | 0.600000 | 0.620750 | 0.600000 | False | -124.000000 |
| KXBTC15M-26MAY071230-30 | 2026-05-07T16:15:36.510038+00:00 | no | rejected_actionable | 0.700000 | 0.729882 | 0.700000 | False | -143.000000 |
| KXBTC15M-26MAY071245-45 | 2026-05-07T16:33:21.276114+00:00 | yes | rejected_actionable | 0.650000 | 0.668302 | 0.650000 | False | -134.000000 |
| KXBTC15M-26MAY071315-15 | 2026-05-07T17:03:02.531145+00:00 | yes | rejected_actionable | 0.700000 | 0.743772 | 0.700000 | True | 57.000000 |
| KXBTC15M-26MAY071330-30 | 2026-05-07T17:16:51.282524+00:00 | no | rejected_actionable | 0.650000 | 0.595517 | 0.650000 | True | 66.000000 |
