# v28 Frozen p50 Book-Edge Entry

Future-only validator for the closest broad entry validation lane. No live orders.

- Candidate live-ready: `False`
- Freeze timestamp: `2026-05-06T08:09:01.165913+00:00`
- Rule: `ask 1-90c, p_side >= 0.50, v28_minus_ask_prob >= 0.05, edge_cents >= 0`
- Future denominator markets: `118`
- Entries/settled/W-L: `104/104/64-40`
- Gross cents / avg gross: `660.000000/6.346154`
- Coverage: `88.135593%`
- Approved/simulated/share: `22/82/0.788462`
- Blockers: `simulated_share_gt_35pct`

## Interpretation

- Frozen p50_book_plus_05_edge_nonnegative has 104 future entries across 118 future markets.
- Settled/gross/coverage are 104/660.0c/88.13559322033898%.
- Approved/simulated rows are 22/82 with simulated share 0.7884615384615384.
- Blockers: simulated_share_gt_35pct.

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
