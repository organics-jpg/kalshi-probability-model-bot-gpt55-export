# v28 Candidate Registry Coverage Audit

Research-only audit of the consolidated all-candidates table.

- Generated UTC: `2026-05-11T03:08:57.386794+00:00`
- Active registry complete: `True`
- Consolidated tracker rows: `995`
- Active expected rows checked: `257`
- Active missing rows: `0`
- Diagnostic candidate-like rows outside tracker: `2653`

## Active Missing Rows

- None.

## Diagnostic Untracked Examples

These are candidate-like diagnostic rows in old scan/frontier artifacts. They are not automatically active promotion candidates.

| file | path | name | entries | settled | net c |
|---|---|---|---:|---:|---:|
| `v28_approved_entry_fv_overlay_validator_latest.json` | `ranked/0` | `book_probability` | 173 | 173 | None |
| `v28_approved_entry_fv_overlay_validator_latest.json` | `ranked/1` | `noise_shrink_light_probability` | 173 | 173 | None |
| `v28_approved_entry_fv_overlay_validator_latest.json` | `ranked/3` | `entry_conditioned_plus03_probability` | 173 | 173 | None |
| `v28_approved_entry_fv_overlay_validator_latest.json` | `ranked/4` | `entry_conditioned_logit125_probability` | 173 | 173 | None |
| `v28_approved_entry_fv_overlay_validator_latest.json` | `ranked/5` | `entry_conditioned_logit125_p60_only_probability` | 173 | 173 | None |
| `v28_approved_entry_fv_overlay_validator_latest.json` | `ranked/6` | `entry_conditioned_plus05_noise_attenuated_probability` | 173 | 173 | None |
| `v28_approved_entry_fv_overlay_validator_latest.json` | `ranked/7` | `entry_conditioned_plus05_probability` | 173 | 173 | None |
| `v28_approved_entry_state_valve_bridge_latest.json` | `rows/0` | `skip_reentry_gap15_or_gap30` | 110 | 110 | None |
| `v28_approved_entry_state_valve_bridge_latest.json` | `rows/1` | `same_side_reentry_gap_lte_15pp` | 114 | 114 | None |
| `v28_approved_entry_state_valves_latest.json` | `ranked/0` | `same_side_reentry_gap_lte_15pp` | 165 | 165 | None |
| `v28_approved_entry_state_valves_latest.json` | `ranked/1` | `same_side_reentry_gap_lte15_and_book_not_down10` | 165 | 165 | None |
| `v28_approved_entry_state_valves_latest.json` | `ranked/2` | `same_side_reentry_book_not_down_10pp` | 168 | 168 | None |
| `v28_approved_entry_state_valves_latest.json` | `ranked/3` | `raw_book_gap_lte_15pp` | 146 | 146 | None |
| `v28_approved_entry_state_valves_latest.json` | `ranked/4` | `raw_book_gap_lte_20pp` | 156 | 156 | None |
| `v28_approved_entry_state_valves_latest.json` | `ranked/5` | `current_v28_approved_all` | 173 | 173 | None |
| `v28_approved_entry_state_valves_latest.json` | `ranked/6` | `no_same_side_reentry` | 116 | 116 | None |
| `v28_approved_entry_state_valves_latest.json` | `ranked/7` | `first_entry_per_market` | 107 | 107 | None |
| `v28_book_disagreement_trajectory_fv_latest.json` | `views/0/ranked/0` | `gap15_or_drawdown10` | None | None | None |
| `v28_book_disagreement_trajectory_fv_latest.json` | `views/0/ranked/1` | `gap15_half_book` | None | None | None |
| `v28_book_disagreement_trajectory_fv_latest.json` | `views/0/ranked/2` | `gap20_half_book` | None | None | None |
| `v28_book_disagreement_trajectory_fv_latest.json` | `views/0/ranked/3` | `book_probability` | None | None | None |
| `v28_book_disagreement_trajectory_fv_latest.json` | `views/0/ranked/4` | `gap15_and_drawdown10_only` | None | None | None |
| `v28_book_disagreement_trajectory_fv_latest.json` | `views/0/ranked/5` | `book_drawdown10_heavy_book` | None | None | None |
| `v28_book_disagreement_trajectory_fv_latest.json` | `views/1/ranked/0` | `book_probability` | None | None | None |
| `v28_book_disagreement_trajectory_fv_latest.json` | `views/1/ranked/1` | `gap15_or_drawdown10` | None | None | None |
| `v28_book_disagreement_trajectory_fv_latest.json` | `views/1/ranked/2` | `gap15_half_book` | None | None | None |
| `v28_book_disagreement_trajectory_fv_latest.json` | `views/1/ranked/3` | `gap20_half_book` | None | None | None |
| `v28_book_disagreement_trajectory_fv_latest.json` | `views/1/ranked/5` | `book_drawdown10_heavy_book` | None | None | None |
| `v28_book_disagreement_trajectory_fv_latest.json` | `views/1/ranked/6` | `gap15_and_drawdown10_only` | None | None | None |
| `v28_book_disagreement_trajectory_fv_latest.json` | `views/2/ranked/0` | `book_probability` | None | None | None |

## Interpretation

- The consolidated table is complete for active tracked candidates when `active_registry_complete` is true.
- Old diagnostic scans can still contain candidate-like rows; they need explicit freezing/registration before becoming active table lanes.
