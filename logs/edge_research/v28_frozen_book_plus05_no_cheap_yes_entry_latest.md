# v28 Frozen Book Plus 05 No Cheap YES Entry

Future-only validator for the broad book-plus-5pp entry lane with a cheap-YES boundary filter. No live orders.

- Candidate live-ready: `False`
- Freeze timestamp: `2026-05-06T08:24:46.840351+00:00`
- Rule: `ask 1-90c, v28_minus_ask_prob >= 0.05, exclude YES rows with p_side < 0.45`
- Future denominator markets: `116`
- Entries/settled/W-L: `111/111/58-53`
- Gross cents / avg gross: `-172.000000/-1.549550`
- Coverage: `95.689655%`
- Approved/simulated/share: `17/94/0.846847`
- Blockers: `coverage_too_high, net_not_positive, simulated_share_gt_35pct`

## Interpretation

- Frozen book_plus_05_no_cheap_yes_boundary has 111 future entries across 116 future markets.
- Settled/gross/coverage are 111/-172.0c/95.6896551724138%.
- Approved/simulated rows are 17/94 with simulated share 0.8468468468468469.
- Blockers: coverage_too_high, net_not_positive, simulated_share_gt_35pct.

## Sample Markets

- `KXBTC15M-26MAY060445-45`
- `KXBTC15M-26MAY060500-00`
- `KXBTC15M-26MAY060515-15`
- `KXBTC15M-26MAY060530-30`
- `KXBTC15M-26MAY060545-45`
- `KXBTC15M-26MAY060600-00`
- `KXBTC15M-26MAY060615-15`
- `KXBTC15M-26MAY060630-30`
- `KXBTC15M-26MAY060645-45`
- `KXBTC15M-26MAY060700-00`
