# v28 Top-Component Strict Gate Audit

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T23:35:06.698842+00:00`
- Live baseline: `1361c`
- Promotion gate passes: `0`

## Interpretation

- Research-only top-component gate audit; no live bot changes or orders.
- Live baseline used for deltas is 1361c from the refreshed live summary.
- The top-component stack remains diagnostic only: strict post-birth evidence is too small and does not beat live.
- The parent portfolio has no settled strict selected rows joined to exit-clock rows, so the exit-rescue mechanism has not been forward-proven in this branch.
- The loss drilldown argues against broad holding: on losses with both marks, holding would worsen losses by -52c.

## Diagnostic Blueprint

- Mix best: `rescue_drop15_plus_ask_parent_fill_to75` with `76` entries, 75.25% coverage, `1716c`, W/L `65/11`, reconstructed share `0.342`, cushion `17`. This is diagnostic/prefreeze only.
- Parent-fill child best: `diagnostic_observable_mid_confidence_parent_fill_quarter` with `76` entries, 75.25% coverage, `2233c`, W/L `67/9`, reconstructed share `0.342`, cushion `22`. This is diagnostic/prefreeze only.

## Strict Forward Denominators

- Mix portfolio: denominator `31`, selected `27`, settled `27`, pending `0`, exit-clock joined `10`, strict scored `27`.
- Parent-fill child: denominator `28`, selected `24`, settled `24`, pending `0`, exit-clock joined `10`, strict absd-fill rows `21`.

## Closest Strict Row

| label | settled | W/L | coverage | net | delta live | recon | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `post_parent_fill_child_birth_exit_child_only_control` | 21 | 19/2 | 75.00% | 194c | -1167c | 0.238 | 1 | does_not_beat_refreshed_live_baseline, exit_clock_join_missing, full_loss_cushion_lt_3, settled_lt_30 |

## Strict Rows

| label | settled | W/L | coverage | net | delta live | recon | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `post_parent_fill_child_birth_exit_child_only_control` | 21 | 19/2 | 75.00% | 194c | -1167c | 0.238 | 1 | does_not_beat_refreshed_live_baseline, exit_clock_join_missing, full_loss_cushion_lt_3, settled_lt_30 |
| `post_parent_fill_child_birth_observable_mid_confidence_parent_fill_half` | 21 | 19/2 | 75.00% | 194c | -1167c | 0.238 | 1 | does_not_beat_refreshed_live_baseline, exit_clock_join_missing, full_loss_cushion_lt_3, settled_lt_30 |
| `post_parent_fill_child_birth_observable_mid_confidence_parent_fill_quarter` | 21 | 19/2 | 75.00% | 194c | -1167c | 0.238 | 1 | does_not_beat_refreshed_live_baseline, exit_clock_join_missing, full_loss_cushion_lt_3, settled_lt_30 |
| `post_parent_fill_child_birth_parent_fill_mid_absd_ask_notch` | 21 | 19/2 | 75.00% | 194c | -1167c | 0.238 | 1 | does_not_beat_refreshed_live_baseline, exit_clock_join_missing, full_loss_cushion_lt_3, settled_lt_30 |
| `post_parent_fill_child_birth_parent_fill_wide_mid_absd_ask_notch` | 21 | 19/2 | 75.00% | 194c | -1167c | 0.238 | 1 | does_not_beat_refreshed_live_baseline, exit_clock_join_missing, full_loss_cushion_lt_3, settled_lt_30 |
| `post_birth_rescue_drop15_plus_absd_parent_fill_to75` | 23 | 20/3 | 76.67% | 135c | -1226c | 0.304 | 1 | does_not_beat_refreshed_live_baseline, full_loss_cushion_lt_3, harmful_suppression_present, settled_lt_30, source_gate_margin_lt_2 |
| `post_birth_rescue_drop15_plus_ask_parent_fill_to75` | 23 | 20/3 | 76.67% | 135c | -1226c | 0.304 | 1 | does_not_beat_refreshed_live_baseline, full_loss_cushion_lt_3, harmful_suppression_present, settled_lt_30, source_gate_margin_lt_2 |
| `post_birth_rescue_drop15_plus_recross_parent_fill_to75` | 23 | 19/4 | 76.67% | 88c | -1273c | 0.304 | 0 | does_not_beat_refreshed_live_baseline, full_loss_cushion_lt_3, harmful_suppression_present, settled_lt_30, source_gate_margin_lt_2 |
| `post_parent_fill_child_birth_parent_fill_all_rejected_half` | 21 | 19/2 | 75.00% | 194c | -1167c | 0.238 | 1 | does_not_beat_refreshed_live_baseline, exit_clock_join_missing, full_loss_cushion_lt_3, settled_lt_30, source_label_diagnostic |
| `post_parent_fill_child_birth_parent_fill_all_rejected_quarter` | 21 | 19/2 | 75.00% | 194c | -1167c | 0.238 | 1 | does_not_beat_refreshed_live_baseline, exit_clock_join_missing, full_loss_cushion_lt_3, settled_lt_30, source_label_diagnostic |
| `post_parent_fill_child_birth_mid_confidence_parent_fill_half` | 21 | 19/2 | 75.00% | 194c | -1167c | 0.238 | 1 | does_not_beat_refreshed_live_baseline, exit_clock_join_missing, full_loss_cushion_lt_3, settled_lt_30, source_label_diagnostic |
| `post_parent_fill_child_birth_mid_confidence_parent_fill_quarter` | 21 | 19/2 | 75.00% | 194c | -1167c | 0.238 | 1 | does_not_beat_refreshed_live_baseline, exit_clock_join_missing, full_loss_cushion_lt_3, settled_lt_30, source_label_diagnostic |

## Loss Modes

- Diagnostic best loss net: `-533c` across `12` rows.
- Hold counterfactual on losses with both marks: `-52c`.

| mode | rows | net |
|---|---:|---:|
| `missed_exit_rescue_false_negative` | 3 | -198c |
| `parent_fill_entry_or_fv_loss` | 5 | -225c |
| `true_loser_entry_or_fv_loss` | 4 | -110c |
