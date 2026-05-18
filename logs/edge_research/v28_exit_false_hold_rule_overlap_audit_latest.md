# v28 Exit False-Hold Rule Overlap Audit

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T11:32:46.495012+00:00`
- Guardrail harmful example keys: `2`

## Interpretation

- Research-only audit; this does not relax the false-hold guardrail or approve any exit watch.
- A lane with zero current harmful suppressed rows can still be blocked by prior false-hold mechanism risk until it has enough strict suppressions.
- Observed current strict harm is stronger evidence than broad tag overlap; prior-risk-only lanes should keep collecting rather than be promoted.

## Lane Table

| lane | read | gate read | rows | settled | suppressed | helpful | harmful | delta c | harm c | guard overlap | harmful overlap | gate false-hold | blockers |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `book_gap_suppression` | `observed_current_strict_harm` | `blocked_false_hold_guardrail` | 55 | 55 | 24 | 19 | 4 | -165.00 | -606.00 | 2 | 2 | `True` | delta_not_positive, full_loss_cushion_lt_3, loss_control_cost_negative, net_not_positive, suppressed_decisions_lt_30, strict_false_hold_guardrail_unresolved |
| `book_gap_loss_guard` | `guardrail_prior_risk_no_current_strict_harm` | `blocked_false_hold_guardrail` | 28 | 28 | 8 | 8 | 0 | 76.00 | 0.00 | 0 | 0 | `True` | full_loss_cushion_lt_3, settled_lt_30, suppressed_decisions_lt_30, strict_false_hold_guardrail_unresolved |
| `book_gap_loss_guard_v2` | `current_strict_suppression_clean_but_immature` | `collecting_rule_not_firing` | 27 | 27 | 1 | 1 | 0 | 22.00 | 0.00 | 0 | 0 | `False` | delta_not_positive, full_loss_cushion_lt_3, net_not_positive, rule_not_firing_yet, settled_lt_30, suppressed_decisions_lt_30 |
| `book_gap_loss_guard_v3` | `current_strict_suppression_clean_but_immature` | `immature_sample_or_density` | 15 | 15 | 2 | 2 | 0 | 24.00 | 0.00 | 0 | 0 | `False` | full_loss_cushion_lt_3, settled_lt_30, suppressed_decisions_lt_30 |
| `book_gap_value_only` | `guardrail_prior_risk_no_current_strict_harm` | `blocked_false_hold_guardrail` | 0 | 0 | 0 | 0 | 0 | 0.00 | 0.00 | 0 | 0 | `True` | delta_not_positive, full_loss_cushion_lt_3, loss_control_cost_negative, net_not_positive, settled_lt_30, suppressed_decisions_lt_30, suppressed_losers_present, strict_false_hold_guardrail_unresolved |
| `dual_exit_book_gap_else_reduce` | `observed_current_strict_harm` | `blocked_false_hold_guardrail` | 25 | 25 | 8 | 6 | 2 | -242.00 | -300.00 | 2 | 2 | `True` | delta_not_positive, full_loss_cushion_lt_3, loss_control_cost_negative, net_not_positive, settled_lt_30, suppressed_decisions_lt_30, strict_false_hold_guardrail_unresolved |
| `reduce_geometry_relaxed` | `guardrail_prior_risk_no_current_strict_harm` | `blocked_false_hold_guardrail` | 0 | 0 | 0 | 0 | 0 | 0.00 | 0.00 | 0 | 0 | `True` | delta_not_positive, full_loss_cushion_lt_3, loss_control_cost_negative, net_not_positive, settled_lt_30, suppressed_decisions_lt_30, suppressed_losers_present, strict_false_hold_guardrail_unresolved |
| `exit_shallow_drawdown` | `guardrail_prior_risk_no_current_strict_harm` | `blocked_false_hold_guardrail` | 0 | 0 | 0 | 0 | 0 | 0.00 | 0.00 | 0 | 0 | `True` | full_loss_cushion_lt_3, settled_lt_30, suppressed_decisions_lt_30, strict_false_hold_guardrail_unresolved |
| `value_exit_feature_side_guard` | `guardrail_prior_risk_no_current_strict_harm` | `blocked_false_hold_guardrail` | 0 | 0 | 0 | 0 | 0 | 0.00 | 0.00 | 0 | 0 | `True` | delta_not_positive, full_loss_cushion_lt_3, settled_lt_30, suppressed_decisions_lt_30, strict_false_hold_guardrail_unresolved |

## Current Harm Examples

### book_gap_suppression
- `KXBTC15M-26MAY062015-15` `yes` -180.00c exit `mushroom_v28_exit_value_over_hold`, exit `90`, p_hold `0.812359`, book_gap `-0.08764099999999997`, fair_drawdown `4.764109`
- `KXBTC15M-26MAY060700-00` `no` -160.00c exit `mushroom_v28_probability_reduce`, exit `80`, p_hold `0.799603`, book_gap `-0.0003970000000000917`, fair_drawdown `4.039746`
- `KXBTC15M-26MAY060900-00` `yes` -146.00c exit `mushroom_v28_probability_reduce`, exit `73`, p_hold `0.78999`, book_gap `0.05998999999999999`, fair_drawdown `-0.998969`
- `KXBTC15M-26MAY062130-30` `no` -120.00c exit `mushroom_v28_probability_reduce`, exit `60`, p_hold `0.768407`, book_gap `0.16840699999999997`, fair_drawdown `6.159273`

### dual_exit_book_gap_else_reduce
- `KXBTC15M-26MAY062015-15` `yes` -180.00c exit `mushroom_v28_exit_value_over_hold`, exit `90`, p_hold `0.812359`, book_gap `-0.08764099999999997`, fair_drawdown `4.764109`
- `KXBTC15M-26MAY062130-30` `no` -120.00c exit `mushroom_v28_probability_reduce`, exit `60`, p_hold `0.768407`, book_gap `0.16840699999999997`, fair_drawdown `6.159273`

