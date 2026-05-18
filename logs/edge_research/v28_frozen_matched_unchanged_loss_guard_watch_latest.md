# v28 Frozen Matched-Unchanged Loss Guard Watch

Research-only frozen watch. No live bot changes or orders.

- Generated UTC: `2026-05-07T13:33:41.846668+00:00`
- Freeze UTC: `2026-05-07T09:30:07.471830+00:00`
- Rule: `{'abs_d_sigma_max': 0.888798, 'eligible_depth_max': 326.6, 'exit_cents_min': 51.0, 'exit_p_hold_min': 0.718799}`

## Interpretation

- Research-only frozen watch; no live bot logic changes or orders.
- Diagnostic parent selected 20 rows with 19/0 helpful/harmful and 817.0c selected hold delta.
- Post-freeze has 5 scored exit rows and 1 selected rows; blockers are ['settled_lt_30', 'suppressed_decisions_lt_30', 'full_loss_cushion_lt_3'].
- Only post-freeze rows count for future review. Diagnostic rows are mechanism context only.

## Summaries

| window | rows | selected | helpful/harmful/flat | current net | candidate net | delta | losses current -> candidate | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_prefreeze` | 108 | 20 | 19/0/1 | 615c | 1432c | 817c | 46 -> 34 | 14 | suppressed_decisions_lt_30, diagnostic_prefreeze |
| `post_freeze` | 5 | 1 | 1/0/0 | 114c | 120c | 6c | 1 -> 1 | 1 | settled_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |

## Post-Freeze Selected Examples

| market | side/result | current | hold | delta | exit | p_hold | fair dd | gap | p_side | raw edge | abs d | depth |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY070930-30` | yes/yes | 34c | 40c | 6c | exit_trigger@98.000000 | 0.969995 | -13.999536 | -0.010005 | 0.855936 | 4.093570 | 0.878792 | 146.030000 |
