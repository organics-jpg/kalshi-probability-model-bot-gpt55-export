# v28 Candidate Portfolio Trial Gate

Research-only gate for whether multiple candidate strategies can be live-trialed safely and cleanly.

- Portfolio live-trial ready: `False`
- Any candidate individually live-ready: `False`
- Risk stop active: `True`
- Account balance used: `2640c`
- Current live exposure: `0c` on `None` `None` x `0`
- Remaining parallel risk budget: `924.000000c`
- Additional nominal candidate slots by risk: `5`
- Portfolio blockers: `no_candidate_live_ready, control_risk_stop_active`

## Recommendations

- Do not start live multi-candidate trading from this state.
- Keep candidate validation in shadow with distinct policy tags and actual-vs-simulated attribution.
- Closest validation lane is p50_book_plus_05_edge_nonnegative needing 172 future rows.

## Nearest Candidates

| gate | policy | settled | coverage | fit | net c | brier | blockers |
|---|---|---:|---:|---|---:|---:|---|
| raw_p52_boundary_turbulence_skip | `raw_p52_skip_weakraw_nearstrike_recross90` | 88 | 77.192982 | target | 266.000000 | 0.209470 | control_risk_stop_active |
| boundary_clock_fv_entry_bridge | `boundary_clock_adjusted_edge_floor_0p02_repair_lowest_recross` | 90 | 75.630252 | target | 229.000000 | None | control_risk_stop_active |
| early_boundary_opposite_wait_repair | `early_boundary_wait480_p50_opposite_side_delay480` | 80 | 75.471698 | target | 98.000000 | None | control_risk_stop_active |
| early_boundary_wait_repair | `early_boundary_wait480_p50_any_side` | 80 | 75.471698 | target | 82.000000 | None | control_risk_stop_active |
| early_no_boundary_decay_repair_entry | `skip_early_no_boundary_decay_repair_calm_geometry` | 85 | 75.221239 | target | 27.000000 | None | control_risk_stop_active |
| side_asymmetry_fv_overlay | `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + clock_then_side_no_midboundary_0p00` | 87 | 73.728814 | low | -321.000000 | -0.011712 | control_risk_stop_active |
| boundary_clock_fv_overlay | `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + clock_shrink_0p00` | 88 | 73.333333 | low | -401.000000 | -0.007305 | control_risk_stop_active |
| boundary_temperature_fv | `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + boundary_temp_strong` | 78 | None | unknown | None | -0.004505 | control_risk_stop_active |
| exit_reduce_suppression | `suppress_reduce_p_hold_ge_075` | 132 | None | unknown | 337.000000 | None | exit:suppressed_loss_control_cost_negative, control_risk_stop_active |
| exit_book_gap_suppression | `suppress_soft_gap15_or_p_hold75` | 120 | None | unknown | 235.000000 | None | exit:suppressed_loss_control_cost_negative, control_risk_stop_active |
| approved_entry_book_fv | `actual_approved_entries + book_probability` | 133 | None | unknown | 701.000000 | 0.006169 | fv:brier_not_better_than_raw, control_risk_stop_active |
| boundary_energy_fv_entry | `boundary_energy_fv_entry` | 73 | 70.192308 | low | 156.000000 | 0.213643 | fv_entry:coverage_too_low, control_risk_stop_active |

## Validation Lanes

| policy | coverage | gross c | sim share | future actual needed | min validation rows | blockers |
|---|---:|---:|---:|---:|---:|---|
| `p50_book_plus_05_edge_nonnegative` | 83.425414 | 890.000000 | 0.748344 | 172 | 172 | candidate_simulated_share_gt_35pct |
| `p65_book_plus_03` | 80.110497 | -1486.000000 | 0.772414 | 175 | 175 | candidate_simulated_share_gt_35pct |
| `p65_v28_premium_anchor_plus_02` | 79.558011 | -1376.000000 | 0.805556 | 188 | 188 | candidate_simulated_share_gt_35pct |
| `p65_large_disagreement_anchor_plus_02` | 80.110497 | -1198.000000 | 0.813793 | 193 | 193 | candidate_simulated_share_gt_35pct |
| `p65_book_plus_02` | 83.977901 | -1542.000000 | 0.822368 | 206 | 206 | candidate_simulated_share_gt_35pct |
| `p55_edge_nonnegative` | 83.425414 | 305.000000 | 0.834437 | 209 | 209 | candidate_simulated_share_gt_35pct |
| `book_plus_03_cheap_convex` | 50.828729 | 916.000000 | 1.000000 | 171 | 171 | candidate_simulated_share_gt_35pct, coverage_below_75pct |
| `book_plus_05_no_cheap_yes_boundary` | 90.607735 | 646.000000 | 0.810976 | 216 | 216 | candidate_simulated_share_gt_35pct, coverage_above_90pct |
