# Paired Sidecar Slice Promotion Readiness

- generated_utc: `2026-05-18T18:30:30+00:00`
- promotion_allowed: `False`
- row_count: `5`
- particle_like_count: `3`
- readiness_candidate_count: `0`
- hard_veto_count: `3`

## Rows

| hypothesis | model | pnl c | top EV c | dBrier | dLogloss | dPnL | dTopEV | safe | stability | trajectory | retirement | blockers | ready |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `blend_v28_w20_time_gt_600s_v1` | `blend_v28_online_lr010_w20` | `450.5` | `448.5` | `0.003889` | `0.014658` | `-1289.200000` | `-504.000000` | `False` | `False` | `False` | `trajectory_blocked_shadow_only` | `does_not_beat_v28_brier, does_not_beat_v28_logloss, does_not_beat_v28_selected_pnl, does_not_beat_v28_top_ev_pnl, locked_oos_promotion_safe_false, stability_screen_not_passed, trajectory_screen_not_passed, retirement_trajectory_blocked_shadow_only` | `False` |
| `blend_v28_w05_time_gt_600s_v1` | `blend_v28_online_lr010_w05` | `1460.0` | `355.0` | `0.000368` | `0.001691` | `-56.500000` | `-393.000000` | `False` | `False` | `False` | `trajectory_blocked_shadow_only` | `does_not_beat_v28_brier, does_not_beat_v28_logloss, does_not_beat_v28_selected_pnl, does_not_beat_v28_top_ev_pnl, locked_oos_promotion_safe_false, stability_screen_not_passed, trajectory_screen_not_passed, retirement_trajectory_blocked_shadow_only` | `False` |
| `v28_control_time_gt_600s_v1` | `v28` | `1516.5` | `748.0` | `` | `` | `` | `` | `False` | `False` | `False` | `control_reference_only` | `control_not_particle_like` | `False` |
| `blend_v28_w15_candidate_v28_gap_05_15pp_v1` | `blend_v28_online_lr010_w15` | `-31.7` | `67.8` | `0.001253` | `0.004535` | `-25.000000` | `132.000000` | `False` | `False` | `False` | `trajectory_blocked_shadow_only` | `nonpositive_selected_pnl, does_not_beat_v28_brier, does_not_beat_v28_logloss, does_not_beat_v28_selected_pnl, locked_oos_promotion_safe_false, stability_screen_not_passed, trajectory_screen_not_passed, retirement_trajectory_blocked_shadow_only` | `False` |
| `v28_control_candidate_v28_gap_05_15pp_v1` | `v28` | `-6.7` | `-64.2` | `0.000000` | `0.000000` | `0.000000` | `0.000000` | `False` | `False` | `False` | `control_reference_only` | `control_not_particle_like` | `False` |

## Conclusion

No particle-like lock clears the combined readiness screen; keep all locks shadow-only.

This report is diagnostic only and never authorizes live trading.
