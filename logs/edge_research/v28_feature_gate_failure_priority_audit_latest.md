# v28 Feature-Gate Failure Priority Audit

Research-only consolidation. No live bot changes, no orders, no new candidate rule.

- Generated UTC: `2026-05-07T08:35:39.967272+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Candidate: `post_feature_freeze_entry_raw03_recross70_abs075`
- Conclusion: `exit_state_first_but_watch_only`

## Current Strict Lane

- Settled / denominator: `37` / `49`
- W/L: `22/15`
- Coverage: `75.51%`
- Net: `275c`
- Reconstructed share: `43.24%`
- Full-loss cushion: `2`
- Blockers: `reconstructed_share_gt_35pct, full_loss_cushion_lt_3`
- Structural modes: `fragility_error, source_quality_error`

## Failure Bucket Priority

| rank | bucket | evidence | repair read |
|---:|---|---|---|
| 1 | Exit-policy error | 7 selected-side theory winners became live selected-side losses; settlement theory 161c, live selected -456c, swing 617c. | Exit/state validation remains first priority, but active exit watches still need strict post-freeze denominators. |
| 2 | Source-quality error | 13 selected losses carry source-quality tags; official broad lane reconstructed share is 43.24%. | Needs new clean approved rows or an observable source-risk shrink that clears row source, coverage, live delta, and cushion together. |
| 3 | Fragility error | Broad post-freeze lane cushion is 2; loss rows total -221c. | Current positive net cannot absorb three full losses; any repair must add cushion without reintroducing source risk. |
| 4 | Execution/friction error | 15 selected losses are tagged execution/friction or thin-edge failure. | This overlaps source/cheap-touch risk and argues for sizing/entry-quality shrink rather than wider thresholds. |
| 5 | FV error | 7 selected losses show FV/overconfidence tags, including large approved losses. | FV calibration is a later overlay here; entry/exit state currently has clearer forward blockers. |
| 6 | Market-regime error | 9 selected losses carry regime/path tags. | Use as warning context for shrink/regime overlays; do not make a brittle cutoff from this small sample. |
| 7 | Entry timing error | 1 selected loss is explicitly tagged entry timing. | Not the dominant post-freeze repair path versus exit/source/cushion blockers. |

## Supporting Signals

- Loss analog risk components: `{'expensive_touch': 16, 'moderate_recross': 5, 'none': 2, 'reconstructed_source': 16, 'thin_raw_edge': 14, 'weak_boundary_distance': 16}`
- Post-penalty residual tag counts: `{'cheap_side_residual': 5, 'fv_overconfidence': 2, 'moderate_recross_reversal': 1, 'source_quality_error': 5, 'thin_edge_expensive_touch': 1, 'weak_boundary_distance': 2}`
- Live exit mismatch class counts: `{'exit_policy_error': 7, 'value_over_hold_clipped_winner': 2, 'same_side_state_churn': 7, 'exited_before_settlement': 7, 'theory_win_selected_live_loss': 7, 'probability_reduce_clipped_winner': 4, 'opposite_side_state_churn': 1}`
- Live exit mismatch reason counts: `{'mushroom_v28_exit_value_over_hold': 16, 'mushroom_v28_exit_value_over_hold_single_shot_visible_depth': 26, 'mushroom_v28_probability_collapse_full': 24, 'mushroom_v28_probability_collapse_full_single_shot_visible_depth': 40, 'mushroom_v28_probability_reduce': 52, 'mushroom_v28_probability_reduce_single_shot_visible_depth': 90}`

## Worst Strict Loss Rows

| market | source | side | net | raw edge | recross | abs d | ask | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062130-30 | approved_entry | no | -78c | 0.12777700000000003 | 0.3038697963028121 | 0.999156 | 0.76 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| KXBTC15M-26MAY070015-15 | approved_entry | no | -72c | 0.2636590000000001 | 0.07375286170271013 | 1.543579 | 0.7 | execution_friction_error, fragility_error, fv_error |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | -15c | 0.041601 | 0.13225659322745886 | 0.784861 | 0.13 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | -11c | 0.08693400000000001 | 0.12224159683597033 | 0.758696 | 0.09 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | -7c | 0.104874 | 0.041740444036135596 | 0.791108 | 0.06 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -6c | 0.059156 | 0.16075609997197524 | 0.997837 | 0.05 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | -5c | 0.062326 | 0.08102015626960654 | 1.050761 | 0.04 | execution_friction_error, fragility_error, source_quality_error |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | -5c | 0.080622 | 0.09907383677577447 | 0.943937 | 0.04 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |

## Interpretation

- The feature-gate branch is not blocked by a single threshold defect.
- Exit/state repair has the clearest live-market failure evidence, but the frozen exit watches still need strict forward rows.
- Source quality and cushion remain hard promotion blockers even if entry-side diagnostic PnL is positive.
