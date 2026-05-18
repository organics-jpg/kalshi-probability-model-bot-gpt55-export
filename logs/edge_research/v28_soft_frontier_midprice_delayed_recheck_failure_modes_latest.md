# v28 Soft-Frontier Mid-Price Delayed-Recheck Failure Modes

Research-only failure-mode audit. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:55.055775+00:00`

## Interpretation

- Research-only residual failure audit; no live bot changes or orders.
- All 8 diagnostic candidate losses are unsuppressed; suppressed losses = 0.
- Residual losses are mainly source/entry/FV quality issues if source_quality_error, weak_boundary_distance, or low p_hold tags dominate; they are exit false negatives only where hold_cents would have recovered the loss.

## Summary

- Rows: `59`
- W/L: `51/8`
- Net: `1501.50c`
- Loss cents: `-340.00c`
- Suppressed/unsuppressed losses: `0/8`
- Source loss counts: `{'approved_entry': 6, 'rejected_actionable': 2}`
- Exit-reason loss counts: `{'mushroom_v28_probability_collapse_full': 5, 'mushroom_v28_exit_value_over_hold': 2, 'mushroom_v28_probability_reduce': 1}`
- Loss tag counts: `{'thin_raw_edge': 2, 'exit_signal_large_fv_drawdown': 6, 'exit_policy_correct_loss_control': 4, 'candidate_loss': 8, 'fv_error_low_p_hold_exit': 5, 'source_quality_error': 2, 'weak_boundary_distance': 2, 'thin_or_cheap_touch': 3, 'very_weak_boundary_distance': 1, 'exit_policy_error_false_negative_suppression': 4}`
- False-negative suppression losses: `4`
- False-negative recoverable cents: `522.00c`

## Loss Rows

| market | side | source | candidate c | current c | hold c | suppress | p_hold | fair dd | abs_d | ask | raw edge | recross | tags |
|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY061800-00 | no | approved_entry | -86.00 | -86.00 | 66.00 | False | 0.55 | 11.74 | 1.04 | 0.67 | 0.23 | 0.26 | fv_error_low_p_hold_exit, exit_signal_large_fv_drawdown, exit_policy_error_false_negative_suppression, candidate_loss |
| KXBTC15M-26MAY060745-45 | yes | rejected_actionable | -70.00 | -70.00 | -156.00 | False | 0.56 | 21.64 | 0.73 | 0.60 | 0.21 | 0.42 | source_quality_error, weak_boundary_distance, thin_or_cheap_touch, fv_error_low_p_hold_exit, exit_signal_large_fv_drawdown, exit_policy_correct_loss_control, candidate_loss |
| KXBTC15M-26MAY062015-15 | no | approved_entry | -60.00 | -60.00 | 116.00 | False | 0.27 | 15.11 | 0.92 | 0.42 | 0.45 | 0.09 | thin_or_cheap_touch, fv_error_low_p_hold_exit, exit_signal_large_fv_drawdown, exit_policy_error_false_negative_suppression, candidate_loss |
| KXBTC15M-26MAY060330-30 | yes | approved_entry | -52.00 | -52.00 | 42.00 | False | 0.50 | 28.91 | 1.07 | 0.79 | 0.12 | 0.15 | thin_raw_edge, fv_error_low_p_hold_exit, exit_signal_large_fv_drawdown, exit_policy_error_false_negative_suppression, candidate_loss |
| KXBTC15M-26MAY060800-00 | yes | approved_entry | -32.00 | -32.00 | 68.00 | False | 0.61 | 4.53 | 0.93 | 0.66 | 0.21 | 0.13 | exit_policy_error_false_negative_suppression, candidate_loss |
| KXBTC15M-26MAY061300-00 | yes | approved_entry | -30.00 | -30.00 | -160.00 | False | 0.67 | 13.36 | 0.91 | 0.80 | 0.06 | 0.30 | thin_raw_edge, exit_signal_large_fv_drawdown, exit_policy_correct_loss_control, candidate_loss |
| KXBTC15M-26MAY062130-30 | no | rejected_actionable | -8.00 | -32.00 | -152.00 | False | 0.77 | 6.16 | 0.62 | 0.61 | 0.16 | 0.27 | source_quality_error, weak_boundary_distance, very_weak_boundary_distance, thin_or_cheap_touch, exit_policy_correct_loss_control, candidate_loss |
| KXBTC15M-26MAY070015-15 | no | approved_entry | -2.00 | -2.00 | -140.00 | False | 0.60 | 10.34 | 1.54 | 0.70 | 0.26 | 0.07 | fv_error_low_p_hold_exit, exit_signal_large_fv_drawdown, exit_policy_correct_loss_control, candidate_loss |
