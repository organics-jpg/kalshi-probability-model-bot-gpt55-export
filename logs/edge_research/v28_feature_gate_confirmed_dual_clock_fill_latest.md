# v28 Feature-Gate Confirmed Dual-Clock Fill

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:20:24.577561+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Portfolio freeze UTC: `2026-05-07T09:21:53.115169+00:00`

## Interpretation

- Research-only confirmed dual-clock coverage-fill portfolio; no live bot changes or orders.
- Diagnostic best late_collapse90_only has net 611.25c, delta vs live 691.25c, W/L 52/13, coverage 80.48780487804878%, source 0.36363636363636365, blockers ['row_reconstructed_share_gt_35pct', 'diagnostic_prefreeze', 'dual_clock_rescue_not_independently_frozen', 'confirmed_dual_clock_fill_diagnostic'].

## Lanes

| lane | strict | entries | coverage | source | replacements | fillers | best variant | W/L | net | delta live | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---|
| `diagnostic_prefreeze_context` | False | 66 | 80.488% | 0.364 | 2 | 0 | `late_collapse90_only` | 52/13 | 611.250 | 691.250 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, dual_clock_rescue_not_independently_frozen, confirmed_dual_clock_fill_diagnostic |
| `post_confirmed_dual_clock_fill_birth` | True | 28 | 87.500% | 0.393 | 0 | 0 | `base_no_exit_overlay` | 23/5 | 313.750 | 393.750 | settled_lt_30, row_reconstructed_share_gt_35pct, post_birth_watch |

## diagnostic_prefreeze_context Fillers

| market | side | source | net | p_side | abs_d | ask | recross | reason |
|---|---|---|---:|---:|---:|---:|---:|---|

## post_confirmed_dual_clock_fill_birth Fillers

| market | side | source | net | p_side | abs_d | ask | recross | reason |
|---|---|---|---:|---:|---:|---:|---:|---|
