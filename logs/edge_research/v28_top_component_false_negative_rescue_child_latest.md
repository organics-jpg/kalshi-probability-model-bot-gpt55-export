# v28 Top-Component False-Negative Rescue Child

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:52:54.933229+00:00`
- Child freeze UTC: `2026-05-07T10:21:56.887234+00:00`
- Parent: `rescue_drop15_plus_absd_parent_fill_to75` `1680.500c` `64/12`
- Strict rows from parent exit timestamps: `2`

## Interpretation

- Research-only false-negative rescue child; no live bot changes or orders.
- Best diagnostic child diagnostic_union_rebound changes parent by 422.0c with 3/0 helpful/harmful rescues.
- Child freeze UTC is 2026-05-07T10:21:56.887234+00:00; strict rows from this child freeze are the only promotion evidence.

## Variants

| label | settled | W/L | coverage | net | delta parent | rescues H/H | rescue delta H/H | recon | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_union_rebound` | 76 | 67/9 | 75.248% | 2102.500 | 422.000 | 3/0 | 422.000/0 | 0.342 | diagnostic_prefreeze |
| `diagnostic_approved_union_rebound` | 76 | 67/9 | 75.248% | 2102.500 | 422.000 | 3/0 | 422.000/0 | 0.342 | diagnostic_prefreeze |
| `diagnostic_low_exit_collapse_rebound` | 76 | 66/10 | 75.248% | 2008.500 | 328.000 | 2/0 | 328.000/0 | 0.342 | diagnostic_prefreeze |
| `diagnostic_mid_recheck_value_rebound` | 76 | 66/10 | 75.248% | 1926.500 | 246.000 | 2/0 | 246.000/0 | 0.342 | diagnostic_prefreeze |
| `post_child_birth_low_exit_collapse_rebound` | 2 | 2/0 | 100.000% | 84.000 | 0.000 | 0/0 | 0/0 | 0.000 | settled_lt_30, coverage_too_high, full_loss_cushion_lt_3 |
| `post_child_birth_mid_recheck_value_rebound` | 2 | 2/0 | 100.000% | 84.000 | 0.000 | 0/0 | 0/0 | 0.000 | settled_lt_30, coverage_too_high, full_loss_cushion_lt_3 |
| `post_child_birth_union_rebound` | 2 | 2/0 | 100.000% | 84.000 | 0.000 | 0/0 | 0/0 | 0.000 | settled_lt_30, coverage_too_high, full_loss_cushion_lt_3 |
| `post_child_birth_approved_union_rebound` | 2 | 2/0 | 100.000% | 84.000 | 0.000 | 0/0 | 0/0 | 0.000 | settled_lt_30, coverage_too_high, full_loss_cushion_lt_3 |

## Best Rescued Examples

| market | side | source | weighted | delta | exit | p_hold | drawdown | exit bid | recheck | drop | hold | current |
|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY062015-15 | no | approved_entry | 116.000 | 176.000 | mushroom_v28_probability_collapse_full | 0.269 | 15.107 | 17.000 | 10.000 | 8.000 | 116.000 | -60.000 |
| KXBTC15M-26MAY061800-00 | no | approved_entry | 66.000 | 152.000 | mushroom_v28_probability_collapse_full | 0.553 | 11.739 | 29.000 | 45.000 | 3.000 | 66.000 | -86.000 |
| KXBTC15M-26MAY060330-30 | yes | approved_entry | 42.000 | 94.000 | mushroom_v28_exit_value_over_hold | 0.501 | 28.914 | 51.000 | 43.000 | 7.000 | 42.000 | -52.000 |
