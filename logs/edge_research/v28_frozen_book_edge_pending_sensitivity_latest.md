# v28 Frozen Book-Edge Pending Sensitivity

Pre-settlement sensitivity for frozen book-edge FV lanes. No live orders.

- Pending rows: `0`
- Unique pending markets: `0`

## Interpretation

- Pending sensitivity is pre-settlement only; it shows what evidence would look like under each outcome.
- A robust FV candidate should not depend on one pending row resolving in the favorable direction.
- Unique pending markets are grouped separately because related lanes may select the same market.

## Lane Summaries

| lane | denominator | entries | settled | pending | blockers |
|---|---:|---:|---:|---:|---|
| p50_book_plus_05_edge_nonnegative | 118 | 104 | 104 | 0 | simulated_share_gt_35pct |
| book_plus_05 | 117 | 113 | 113 | 0 | coverage_too_high, net_not_positive, simulated_share_gt_35pct |
| book_plus_05_no_cheap_yes_boundary | 116 | 111 | 111 | 0 | coverage_too_high, net_not_positive, simulated_share_gt_35pct |

## Unique Pending Markets


## Pending Rows

