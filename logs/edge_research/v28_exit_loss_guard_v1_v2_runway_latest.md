# v28 Exit Loss-Guard V1/V2/V3 Runway

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:15:44.940185+00:00`
- V1 freeze UTC: `2026-05-06T21:29:32.710906+00:00`
- V2 freeze UTC: `2026-05-06T22:01:04.415577+00:00`
- V3 freeze UTC: `2026-05-07T01:01:45.501061+00:00`

## Interpretation

- This runway is research-only and does not change any live exit rule.
- V2 strict-forward has 58 settled rows, 5 v2 suppressions, 152.0c v2 delta, and blockers ['v2_suppressed_decisions_lt_30', 'full_loss_cushion_lt_3'].
- V1-only opportunity cost after the v2 freeze is 90.0c over 12 rows; this is the current cost of v2 strictness.
- V2 opportunity denominator has 43 soft exits and 5 would-suppress rows; fail reasons {'not_soft_exit': 15, 'reduce_gap_below_floor': 2, 'reduce_p_hold_below_floor': 8, 'value_fair_drawdown_too_deep': 13, 'value_gap_below_floor': 30, 'value_p_hold_below_floor': 18}.
- For promotion review, v2 still needs 0 settled rows, 25 v2 suppressions, and 148.0c additional cushion.
- V3 strict-forward has 46 settled rows, 9 v3 suppressions, 166.0c v3 delta, and blockers ['v3_suppressed_decisions_lt_30', 'full_loss_cushion_lt_3'].
- V1 strict-forward remains an alternate watch: 59 settled rows, 5 v2-equivalent suppressions, and 90.0c v1-only cost.

## Strict Runways

| window | settled | v2 suppressions | v2 delta c | v2 harmful c | v1-only rows | v1-only cost c | rows needed | suppressions needed | cushion c needed | absorbable losses | ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| v1_strict_forward | 59 | 5 | 152.000000 | 0.000000 | 12 | 90.000000 | 0 | 25 | 148.000000 | 1 | False | v2_suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| v2_strict_forward | 58 | 5 | 152.000000 | 0.000000 | 12 | 90.000000 | 0 | 25 | 148.000000 | 1 | False | v2_suppressed_decisions_lt_30, full_loss_cushion_lt_3 |

## Strict Variant Runways

| variant | window | settled | suppressed | delta c | harmful c | rows needed | suppressions needed | cushion c needed | absorbable losses | ready | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| v1 | v1_strict_forward | 59 | 17 | 242.000000 | 0.000000 | 0 | 13 | 58.000000 | 2 | False | v1_suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| v2 | v2_strict_forward | 58 | 5 | 152.000000 | 0.000000 | 0 | 25 | 148.000000 | 1 | False | v2_suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| v3 | v3_strict_forward | 46 | 9 | 166.000000 | 0.000000 | 0 | 21 | 134.000000 | 1 | False | v3_suppressed_decisions_lt_30, full_loss_cushion_lt_3 |

## V2 Opportunity

- `{'total_rows': 58, 'soft_exit_rows': 43, 'value_over_hold_rows': 33, 'probability_reduce_rows': 10, 'would_suppress_rows': 5, 'fail_reason_counts': {'not_soft_exit': 15, 'reduce_gap_below_floor': 2, 'reduce_p_hold_below_floor': 8, 'value_fair_drawdown_too_deep': 13, 'value_gap_below_floor': 30, 'value_p_hold_below_floor': 18}}`
