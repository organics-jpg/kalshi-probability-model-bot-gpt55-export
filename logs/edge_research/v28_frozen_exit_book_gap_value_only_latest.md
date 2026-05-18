# v28 Frozen Exit Book-Gap Value-Only

Research-only frozen forward watch. No live bot changes.

- Generated UTC: `2026-05-11T03:44:19.118069+00:00`
- Freeze timestamp UTC: `2026-05-06T23:20:01.640880+00:00`
- Candidate: `value_only_gap15_or_p75`
- Rule: `Suppress only mushroom_v28_exit_value_over_hold when hold_book_gap >= 0.15 or p_hold >= 0.75; keep probability_reduce and probability_collapse_full exits unchanged.`
- Any live-ready primary: `False`
- Primary blockers: `delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3`

## Interpretation

- This is a frozen watch; diagnostic rows motivate the freeze but do not promote it.
- Probability-reduce exits stay unchanged in the primary value-only rule.
- diagnostic_from_book_gap_freeze: best value_only_gap15_only settled 120, net 727.0c, delta 0.0c, suppressed W/L 0/0, loss cost 0c, blockers ['delta_not_positive'].
- post_value_only_birth: best value_only_gap15_only settled 54, net 338.0c, delta 0.0c, suppressed W/L 0/0, loss cost 0c, blockers ['delta_not_positive'].

## diagnostic_from_book_gap_freeze

| rank | variant | settled | W/L | current c | candidate c | delta c | suppressed | suppressed W/L | recovery c | loss cost c | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `value_only_gap15_only` | 120 | 71/49 | 727.000000 | 727.000000 | 0.000000 | 0 | 0/0 | 0 | 0 | 7 | delta_not_positive |
| 2 | `both_soft_reasons_gap15_or_p79` | 120 | 76/44 | 727.000000 | 924.000000 | 197.000000 | 46 | 42/4 | 827.000000 | -630.000000 | 9 | suppressed_losers_present, suppressed_loss_control_cost_negative |
| 3 | `value_only_gap15_or_p75` | 120 | 69/51 | 727.000000 | 787.000000 | 60.000000 | 37 | 35/2 | 410.000000 | -350.000000 | 7 | suppressed_losers_present, suppressed_loss_control_cost_negative |
| 4 | `value_only_gap15_or_p79` | 120 | 69/51 | 727.000000 | 735.000000 | 8.000000 | 35 | 33/2 | 358.000000 | -350.000000 | 7 | suppressed_losers_present, suppressed_loss_control_cost_negative |

## post_value_only_birth

| rank | variant | settled | W/L | current c | candidate c | delta c | suppressed | suppressed W/L | recovery c | loss cost c | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `value_only_gap15_only` | 54 | 35/19 | 338.000000 | 338.000000 | 0.000000 | 0 | 0/0 | 0 | 0 | 3 | delta_not_positive |
| 2 | `value_only_gap15_or_p75` | 54 | 33/21 | 338.000000 | 240.000000 | -98.000000 | 18 | 16/2 | 252.000000 | -350.000000 | 2 | delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 3 | `value_only_gap15_or_p79` | 54 | 33/21 | 338.000000 | 198.000000 | -140.000000 | 17 | 15/2 | 210.000000 | -350.000000 | 1 | delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 4 | `both_soft_reasons_gap15_or_p79` | 54 | 35/19 | 338.000000 | 172.000000 | -166.000000 | 20 | 17/3 | 304.000000 | -470.000000 | 1 | delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
