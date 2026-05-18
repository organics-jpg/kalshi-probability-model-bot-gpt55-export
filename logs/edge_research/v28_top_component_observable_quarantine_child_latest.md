# v28 Top-Component Observable Quarantine Child

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T12:56:36.283686+00:00`
- Child freeze UTC: `2026-05-07T11:23:30.150645+00:00`
- Parent diagnostic base: `diagnostic_exit_child_only_control` 1828c ($18.27), entries `66`, coverage `75.0%`
- Own strict denominator: `6`

## Interpretation

- Research-only observable quarantine child; no live bot changes or orders.
- The rule family uses only observable ask/abs-distance geometry; source labels are audit-only.
- Diagnostic/autopsy rows are pre-birth context because the child was created after seeing the strict failures.
- Own strict rows from this child freeze are the only future promotion evidence.
- Best autopsy-context rule: `weak_touch_zero` 112c ($1.12), W/L `6/0`, blockers `['diagnostic_or_prefreeze_context', 'not_strict_forward', 'settled_lt_30', 'source_gate_zero_row_margin', 'full_loss_cushion_lt_3', 'does_not_beat_refreshed_live_baseline', 'zero_size_changes_coverage']`.
- Best diagnostic rule: `observable_quarantine_control` 1828c ($18.27), W/L `61/4`, coverage `75.0%`.
- Best own-strict rule: `observable_quarantine_control` 60c ($0.60), W/L `3/0`, blockers `['settled_lt_30', 'coverage_too_low', 'full_loss_cushion_lt_3', 'does_not_beat_refreshed_live_baseline']`.

## Diagnostic Parent Rows

| rank | rule | entries | W/L | coverage | net | recon | cushion | affected | affected delta | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `observable_quarantine_control` | 66 | 61/4 | 75.0% | 1828c ($18.27) | 24.2% | 26 | 0 | 0c ($0.00) | diagnostic_or_prefreeze_context, not_strict_forward |
| 2 | `weak_touch_quarter` | 66 | 61/4 | 75.0% | 1828c ($18.27) | 24.2% | 26 | 0 | 0c ($0.00) | diagnostic_or_prefreeze_context, not_strict_forward |
| 3 | `weak_touch_half` | 66 | 61/4 | 75.0% | 1828c ($18.27) | 24.2% | 26 | 0 | 0c ($0.00) | diagnostic_or_prefreeze_context, not_strict_forward |
| 4 | `weak_touch_zero` | 66 | 61/4 | 75.0% | 1828c ($18.27) | 24.2% | 26 | 0 | 0c ($0.00) | diagnostic_or_prefreeze_context, not_strict_forward |
| 5 | `very_weak_touch_zero` | 66 | 61/4 | 75.0% | 1828c ($18.27) | 24.2% | 26 | 0 | 0c ($0.00) | diagnostic_or_prefreeze_context, not_strict_forward |
| 6 | `smooth_weak_touch` | 66 | 61/4 | 75.0% | 1813c ($18.13) | 24.2% | 25 | 4 | -15c ($-0.15) | diagnostic_or_prefreeze_context, not_strict_forward |
| 7 | `weak_boundary_quarter` | 66 | 61/4 | 75.0% | 1806c ($18.07) | 24.2% | 25 | 1 | -21c ($-0.21) | diagnostic_or_prefreeze_context, not_strict_forward |
| 8 | `low_ask_quarter` | 66 | 61/4 | 75.0% | 1803c ($18.03) | 24.2% | 25 | 1 | -25c ($-0.25) | diagnostic_or_prefreeze_context, not_strict_forward |

## Strict Autopsy Context

| rank | rule | entries | W/L | coverage | net | recon | cushion | affected | affected delta | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `weak_touch_zero` | 6 | 6/0 | 75.0% | 112c ($1.12) | 33.3% | 1 | 2 | 106c ($1.06) | diagnostic_or_prefreeze_context, not_strict_forward, settled_lt_30, source_gate_zero_row_margin, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, zero_size_changes_coverage |
| 2 | `very_weak_touch_zero` | 6 | 6/0 | 75.0% | 112c ($1.12) | 33.3% | 1 | 2 | 106c ($1.06) | diagnostic_or_prefreeze_context, not_strict_forward, settled_lt_30, source_gate_zero_row_margin, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, zero_size_changes_coverage |
| 3 | `weak_touch_quarter` | 8 | 6/2 | 100.0% | 86c ($0.85) | 50.0% | 5 | 2 | 80c ($0.80) | diagnostic_or_prefreeze_context, not_strict_forward, settled_lt_30, coverage_too_high, row_reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 4 | `low_ask_quarter` | 8 | 6/2 | 100.0% | 86c ($0.85) | 50.0% | 5 | 2 | 80c ($0.80) | diagnostic_or_prefreeze_context, not_strict_forward, settled_lt_30, coverage_too_high, row_reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 5 | `weak_boundary_quarter` | 8 | 6/2 | 100.0% | 64c ($0.65) | 50.0% | 4 | 3 | 58c ($0.58) | diagnostic_or_prefreeze_context, not_strict_forward, settled_lt_30, coverage_too_high, row_reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |
| 6 | `weak_touch_half` | 8 | 6/2 | 100.0% | 59c ($0.59) | 50.0% | 2 | 2 | 53c ($0.53) | diagnostic_or_prefreeze_context, not_strict_forward, settled_lt_30, coverage_too_high, row_reconstructed_share_gt_35pct, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| 7 | `smooth_weak_touch` | 8 | 6/2 | 100.0% | 55c ($0.55) | 50.0% | 1 | 4 | 49c ($0.49) | diagnostic_or_prefreeze_context, not_strict_forward, settled_lt_30, coverage_too_high, row_reconstructed_share_gt_35pct, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| 8 | `observable_quarantine_control` | 8 | 6/2 | 100.0% | 6c ($0.06) | 50.0% | 0 | 0 | 0c ($0.00) | diagnostic_or_prefreeze_context, not_strict_forward, settled_lt_30, coverage_too_high, row_reconstructed_share_gt_35pct, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |

## Own Strict Post-Birth Watch

| rank | rule | entries | W/L | coverage | net | recon | cushion | affected | affected delta | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `observable_quarantine_control` | 3 | 3/0 | 50.0% | 60c ($0.60) | 0.0% | 0 | 0 | 0c ($0.00) | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| 2 | `weak_touch_quarter` | 3 | 3/0 | 50.0% | 60c ($0.60) | 0.0% | 0 | 0 | 0c ($0.00) | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| 3 | `weak_touch_half` | 3 | 3/0 | 50.0% | 60c ($0.60) | 0.0% | 0 | 0 | 0c ($0.00) | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| 4 | `weak_touch_zero` | 3 | 3/0 | 50.0% | 60c ($0.60) | 0.0% | 0 | 0 | 0c ($0.00) | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| 5 | `very_weak_touch_zero` | 3 | 3/0 | 50.0% | 60c ($0.60) | 0.0% | 0 | 0 | 0c ($0.00) | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| 6 | `low_ask_quarter` | 3 | 3/0 | 50.0% | 60c ($0.60) | 0.0% | 0 | 0 | 0c ($0.00) | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| 7 | `weak_boundary_quarter` | 3 | 3/0 | 50.0% | 60c ($0.60) | 0.0% | 0 | 0 | 0c ($0.00) | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| 8 | `smooth_weak_touch` | 3 | 3/0 | 50.0% | 58c ($0.58) | 0.0% | 0 | 1 | -2c ($-0.02) | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |

## Own Strict Diagnostics

- `future_denominator`: `6`
- `future_observation_rows`: `122`
- `broad_pass_rows`: `7`
- `selected_parent_rows`: `4`
- `selected_settled_rows`: `3`
- `selected_pending_rows`: `1`
- `settled_parent_rows_with_exit_clock`: `0`
- `strict_absd_fill_rows`: `3`
