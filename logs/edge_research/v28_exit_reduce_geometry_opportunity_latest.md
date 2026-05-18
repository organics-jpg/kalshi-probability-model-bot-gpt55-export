# v28 Exit Reduce Geometry Opportunity

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:14:30.059986+00:00`
- Freeze UTC: `2026-05-06T14:49:54.002173+00:00`

## Interpretation

- This audit explains frozen geometry opportunity only; it does not change any exit rule.
- Post-freeze rows 70, probability-reduce rows 11, base p_hold candidates 10, geometry would-suppress rows 3.
- Geometry rejected 7 base p_hold candidates for -36.0c net base opportunity cost.
- Blockers ['geometry_suppressed_decisions_lt_30', 'geometry_delta_not_positive'].

## Summary

| metric | value |
|---|---:|
| post_freeze_rows | 70 |
| probability_reduce_rows | 11 |
| base_p_hold_candidates | 10 |
| geometry_would_suppress_rows | 3 |
| geometry_rejected_base_candidates | 7 |
| geometry_rejected_base_delta_cents | -36.000000 |

- Reason counts: `{'not_probability_reduce': 59, 'p_hold_missing': 14, 'fair_drawdown_missing': 14, 'yes_negative_drawdown_reject': 14, 'p_hold_below_floor': 21, 'no_positive_drawdown_reject': 18, 'would_suppress': 3}`
- Blockers: `geometry_suppressed_decisions_lt_30, geometry_delta_not_positive`

## Geometry Would-Suppress Rows

| market | side | result | p_hold | drawdown | current c | hold c | delta c |
|---|---|---|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY071015-15 | no | yes | 0.789130 | -0.913001 | 2.000000 | -156.000000 | -158.000000 |
| KXBTC15M-26MAY071045-45 | no | no | 0.760529 | -2.052947 | -10.000000 | 52.000000 | 62.000000 |
| KXBTC15M-26MAY071315-15 | yes | yes | 0.784166 | 2.583397 | -14.000000 | 38.000000 | 52.000000 |

## Rejected Base P-Hold Candidates

| market | side | result | p_hold | drawdown | current c | hold c | delta c | fail reasons |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY061445-45 | no | no | 0.797830 | 8.216985 | -22.000000 | 24.000000 | 46.000000 | no_positive_drawdown_reject |
| KXBTC15M-26MAY062130-30 | no | yes | 0.768407 | 6.159273 | -32.000000 | -152.000000 | -120.000000 | no_positive_drawdown_reject |
| KXBTC15M-26MAY071000-00 | no | no | 0.781361 | 6.863933 | 16.000000 | 58.000000 | 42.000000 | no_positive_drawdown_reject |
| KXBTC15M-26MAY071015-15 | no | yes | 0.763980 | 4.602013 | -16.000000 | -162.000000 | -146.000000 | no_positive_drawdown_reject |
| KXBTC15M-26MAY071215-15 | no | no | 0.797661 | 4.233856 | -16.000000 | 32.000000 | 48.000000 | no_positive_drawdown_reject |
| KXBTC15M-26MAY071215-15 | no | no | 0.765822 | 3.417815 | -8.000000 | 40.000000 | 48.000000 | no_positive_drawdown_reject |
| KXBTC15M-26MAY071315-15 | yes | yes | 0.798341 | -0.834147 | -6.000000 | 40.000000 | 46.000000 | yes_negative_drawdown_reject |
