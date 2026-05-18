# v28 Successor Source Inventory

Research-only source inventory for the v28 successor FV pipeline. This report only inspects files; it does not touch live bot state or processes.

## Summary

- Existing sources: `119`
- Missing expected sources: `0`
- Generated UTC: `2026-05-12T07:29:13Z`

## By Kind

| kind | count |
|---|---:|
| calibration_report_md | 1 |
| calibration_rows_csv | 1 |
| calibration_rows_json | 1 |
| discovered_v28_report_md | 107 |
| execution_events_inventory_only | 1 |
| fv_readiness_report_json | 1 |
| fv_readiness_report_md | 1 |
| fv_sample_plan_json | 1 |
| fv_sample_plan_md | 1 |
| live_bot_log_inventory_only | 1 |
| registry_schema_md | 1 |
| source_quality_report_json | 1 |
| source_quality_report_md | 1 |

## Sources

| source | kind | exists | size | rows read | last write UTC | hash |
|---|---|---:|---:|---:|---|---|
| `logs/edge_research/v28_forward_calibration_latest.csv` | calibration_rows_csv | True | 128843 | 795 | 2026-05-11T03:16:48Z | 4f07466109ab |
| `logs/edge_research/v28_forward_calibration_latest.json` | calibration_rows_json | True | 430519 |  | 2026-05-11T03:16:48Z | d3b5960cf2df |
| `logs/edge_research/v28_forward_calibration_latest.md` | calibration_report_md | True | 4395 |  | 2026-05-11T03:16:48Z | 284ac0829ee6 |
| `logs/edge_research/v28_forward_shadow_registry_schema_latest.md` | registry_schema_md | True | 1576 |  | 2026-05-08T02:16:36Z | 622da28601a2 |
| `logs/edge_research/v28_source_quality_ceiling_audit_latest.md` | source_quality_report_md | True | 3077 |  | 2026-05-06T20:39:40Z | 1bb854b21224 |
| `logs/edge_research/v28_source_quality_ceiling_audit_latest.json` | source_quality_report_json | True | 4770 |  | 2026-05-06T20:39:40Z | 0d4846b20dd5 |
| `logs/edge_research/v28_fv_model_readiness_latest.md` | fv_readiness_report_md | True | 15890 |  | 2026-05-11T03:45:34Z | 209e9528fc5b |
| `logs/edge_research/v28_fv_model_readiness_latest.json` | fv_readiness_report_json | True | 305885 |  | 2026-05-11T03:45:34Z | 7b3c8a767cf2 |
| `logs/edge_research/v28_calibrated_fv_sample_plan_latest.md` | fv_sample_plan_md | True | 3285 |  | 2026-05-11T03:45:34Z | 533522a0a1b9 |
| `logs/edge_research/v28_calibrated_fv_sample_plan_latest.json` | fv_sample_plan_json | True | 6805 |  | 2026-05-11T03:45:34Z | d7a8f12bfae4 |
| `logs/live_mushroom_v28_size2/bot.log` | live_bot_log_inventory_only | True | 22756312 |  | 2026-05-07T17:22:01Z |  |
| `logs/live_mushroom_v28_size2/execution_events.ndjson` | execution_events_inventory_only | True | 52900527 |  | 2026-05-07T17:12:13Z |  |
| `logs/edge_research/v28_adjusted_fv_repair_bakeoff_latest.md` | discovered_v28_report_md | True | 7061 |  | 2026-05-07T01:58:13Z | 2d6a83c575c2 |
| `logs/edge_research/v28_approved_entry_book_fv_regime_attribution_latest.md` | discovered_v28_report_md | True | 3728 |  | 2026-05-11T03:37:47Z | e2a68f3a2288 |
| `logs/edge_research/v28_approved_entry_book_fv_robustness_latest.md` | discovered_v28_report_md | True | 1864 |  | 2026-05-11T03:36:51Z | 8c2091af41b2 |
| `logs/edge_research/v28_approved_entry_fv_overlay_validator_latest.md` | discovered_v28_report_md | True | 2151 |  | 2026-05-11T03:36:48Z | 8b270e011bfe |
| `logs/edge_research/v28_book_disagreement_calibration_latest.md` | discovered_v28_report_md | True | 4525 |  | 2026-05-11T03:16:54Z | eeae74ee8e93 |
| `logs/edge_research/v28_book_disagreement_trajectory_fv_latest.md` | discovered_v28_report_md | True | 4877 |  | 2026-05-11T03:39:03Z | f545ab869580 |
| `logs/edge_research/v28_book_dislocation_fv_bridge_latest.md` | discovered_v28_report_md | True | 2096 |  | 2026-05-10T02:56:16Z | 02c65c35876b |
| `logs/edge_research/v28_boundary_clock_feature_gate_coverage_source_frontier_latest.md` | discovered_v28_report_md | True | 8474 |  | 2026-05-11T02:00:46Z | b3037e082f8d |
| `logs/edge_research/v28_boundary_clock_feature_gate_soft_frontier_source_stress_latest.md` | discovered_v28_report_md | True | 2019 |  | 2026-05-07T04:16:03Z | 7488dea67638 |
| `logs/edge_research/v28_boundary_clock_feature_gate_source_denominator_audit_latest.md` | discovered_v28_report_md | True | 4464 |  | 2026-05-07T17:55:03Z | d9a4b8f03357 |
| `logs/edge_research/v28_boundary_clock_fv_entry_bridge_latest.md` | discovered_v28_report_md | True | 7060 |  | 2026-05-07T16:16:18Z | 9eb37c5c1ad2 |
| `logs/edge_research/v28_boundary_clock_fv_overlay_latest.md` | discovered_v28_report_md | True | 9566 |  | 2026-05-11T01:37:56Z | f7e49829eb16 |
| `logs/edge_research/v28_boundary_clock_fv_robustness_latest.md` | discovered_v28_report_md | True | 12050 |  | 2026-05-11T01:37:57Z | 6e05da2f6270 |
| `logs/edge_research/v28_boundary_clock_source_stress_latest.md` | discovered_v28_report_md | True | 3355 |  | 2026-05-07T18:16:28Z | 9b058cdd3140 |
| `logs/edge_research/v28_boundary_entropy_fv_latest.md` | discovered_v28_report_md | True | 1578 |  | 2026-05-11T00:50:25Z | f2f33b960d72 |
| `logs/edge_research/v28_boundary_memory_fv_candidates_latest.md` | discovered_v28_report_md | True | 26284 |  | 2026-05-11T03:03:17Z | 2890700402e2 |
| `logs/edge_research/v28_boundary_recross_phase_fv_bakeoff_latest.md` | discovered_v28_report_md | True | 1998 |  | 2026-05-11T01:17:01Z | 7961bb87f9e2 |
| `logs/edge_research/v28_broad_book_edge_source_audit_latest.md` | discovered_v28_report_md | True | 1495 |  | 2026-05-11T03:12:01Z | 45f183a2c44c |
| `logs/edge_research/v28_calibrated_fv_forward_monitor_latest.md` | discovered_v28_report_md | True | 29992 |  | 2026-05-11T03:44:39Z | c2ba977e51cc |
| `logs/edge_research/v28_calibrated_fv_path_contradiction_latest.md` | discovered_v28_report_md | True | 17483 |  | 2026-05-11T03:44:42Z | caece301deb6 |
| `logs/edge_research/v28_calibrated_fv_physics_attribution_latest.md` | discovered_v28_report_md | True | 1898 |  | 2026-05-11T03:44:41Z | 67be6d79a61b |
| `logs/edge_research/v28_calibrated_fv_sequential_evidence_latest.md` | discovered_v28_report_md | True | 17493 |  | 2026-05-11T03:44:41Z | e36185c68e4f |
| `logs/edge_research/v28_candidate_integrity_scorecard_latest.md` | discovered_v28_report_md | True | 198713 |  | 2026-05-11T03:46:20Z | 3b90bcfaad92 |
| `logs/edge_research/v28_candidate_readiness_distance_latest.md` | discovered_v28_report_md | True | 9394 |  | 2026-05-11T03:42:24Z | b6c89592529f |
| `logs/edge_research/v28_continuous_scorecard_latest.md` | discovered_v28_report_md | True | 2639 |  | 2026-05-11T03:07:50Z | accdcb08a1e5 |
| `logs/edge_research/v28_danger_zone_fv_calibration_latest.md` | discovered_v28_report_md | True | 1947 |  | 2026-05-11T03:38:36Z | 8d32bc54ccc9 |
| `logs/edge_research/v28_dual_lane_live_readiness_gate_latest.md` | discovered_v28_report_md | True | 2797 |  | 2026-05-11T03:47:38Z | 206ba0fe8c88 |
| `logs/edge_research/v28_dual_lane_live_readiness_runway_latest.md` | discovered_v28_report_md | True | 1922 |  | 2026-05-11T03:47:38Z | 7b7418b4ca5e |
| `logs/edge_research/v28_dual_lane_overlay_readiness_latest.md` | discovered_v28_report_md | True | 2645 |  | 2026-05-11T03:47:38Z | 10a45f766d08 |
| `logs/edge_research/v28_dual_lane_overlay_v2_readiness_latest.md` | discovered_v28_report_md | True | 2472 |  | 2026-05-11T03:47:37Z | d56e7a84ee8d |
| `logs/edge_research/v28_dual_lane_readiness_checklist_latest.md` | discovered_v28_report_md | True | 6323 |  | 2026-05-11T03:47:38Z | d4baadbfc33e |
| `logs/edge_research/v28_early_no_boundary_fv_jackknife_latest.md` | discovered_v28_report_md | True | 11965 |  | 2026-05-11T01:13:36Z | 8f9b3deefee2 |
| `logs/edge_research/v28_exit_clock_source_stability_latest.md` | discovered_v28_report_md | True | 930 |  | 2026-05-07T17:06:40Z | 63e317a720ce |
| `logs/edge_research/v28_false_conviction_family_scorecard_latest.md` | discovered_v28_report_md | True | 3923 |  | 2026-05-11T01:05:32Z | 6cab0e6e6fa2 |
| `logs/edge_research/v28_false_conviction_fv_entry_bridge_latest.md` | discovered_v28_report_md | True | 49873 |  | 2026-05-10T02:54:47Z | e6d2c621e41d |
| `logs/edge_research/v28_false_conviction_source_quality_repair_latest.md` | discovered_v28_report_md | True | 1345 |  | 2026-05-10T02:53:25Z | 66a129cb9785 |
| `logs/edge_research/v28_feature_gate_linked_source_runway_latest.md` | discovered_v28_report_md | True | 4280 |  | 2026-05-07T14:53:15Z | 83e52846e50c |
| `logs/edge_research/v28_feature_gate_live_variant_switch_readiness_latest.md` | discovered_v28_report_md | True | 1648 |  | 2026-05-07T18:23:12Z | 87eba15fd6dc |
| `logs/edge_research/v28_feature_gate_size_shrink_source_runway_latest.md` | discovered_v28_report_md | True | 1644 |  | 2026-05-07T14:53:15Z | 388177ae286f |
| `logs/edge_research/v28_feature_gate_size_shrink_source_slice_latest.md` | discovered_v28_report_md | True | 10980 |  | 2026-05-07T12:25:43Z | 57a44504cbbf |
| `logs/edge_research/v28_feature_gate_source_blocker_mechanism_latest.md` | discovered_v28_report_md | True | 6603 |  | 2026-05-11T02:27:37Z | 40ee73c99bfd |
| `logs/edge_research/v28_feature_gate_source_confirmation_replacement_latest.md` | discovered_v28_report_md | True | 2531 |  | 2026-05-11T02:15:14Z | daa39f7af29a |
| `logs/edge_research/v28_feature_gate_source_feasibility_bound_latest.md` | discovered_v28_report_md | True | 1862 |  | 2026-05-11T01:59:04Z | ae169bcbbaf1 |
| `logs/edge_research/v28_feature_gate_source_proxy_coverage_repair_latest.md` | discovered_v28_report_md | True | 7120 |  | 2026-05-11T02:26:00Z | 86cf434962f4 |
| `logs/edge_research/v28_feature_gate_source_proxy_strict_autopsy_latest.md` | discovered_v28_report_md | True | 8265 |  | 2026-05-07T18:24:07Z | 36043119e000 |
| `logs/edge_research/v28_feature_gate_source_quality_proxy_latest.md` | discovered_v28_report_md | True | 27065 |  | 2026-05-11T02:23:18Z | 762e094dc9b2 |
| `logs/edge_research/v28_feature_gate_source_risk_shrink_watch_latest.md` | discovered_v28_report_md | True | 19490 |  | 2026-05-07T10:28:16Z | 3b4c3ecddac2 |
| `logs/edge_research/v28_forward_collection_blocker_audit_latest.md` | discovered_v28_report_md | True | 5973 |  | 2026-05-07T20:58:56Z | 83cde4f35b33 |
| `logs/edge_research/v28_forward_coverage_pressure_audit_latest.md` | discovered_v28_report_md | True | 3745 |  | 2026-05-11T03:23:50Z | 35bef818c687 |
| `logs/edge_research/v28_forward_physics_registry_latest.md` | discovered_v28_report_md | True | 26099 |  | 2026-05-11T03:13:18Z | 396aef6d1f7f |
| `logs/edge_research/v28_frozen_approved_entry_book_fv_latest.md` | discovered_v28_report_md | True | 1176 |  | 2026-05-11T03:37:39Z | 7f225f8717e4 |
| `logs/edge_research/v28_frozen_approved_entry_conditional_book_fv_latest.md` | discovered_v28_report_md | True | 2089 |  | 2026-05-11T03:37:57Z | a0e42c2802db |
| `logs/edge_research/v28_frozen_book_edge_fv_calibration_latest.md` | discovered_v28_report_md | True | 5606 |  | 2026-05-11T03:11:22Z | 499078e79719 |
| `logs/edge_research/v28_frozen_book_trajectory_fv_latest.md` | discovered_v28_report_md | True | 1248 |  | 2026-05-11T03:39:22Z | baf27b75ba1e |
| `logs/edge_research/v28_frozen_boundary_clock_fv_entry_bridge_latest.md` | discovered_v28_report_md | True | 5512 |  | 2026-05-10T23:55:15Z | c23bb0e73ec3 |
| `logs/edge_research/v28_frozen_boundary_clock_fv_overlay_latest.md` | discovered_v28_report_md | True | 7039 |  | 2026-05-11T03:05:08Z | a0dc9bbefbd8 |
| `logs/edge_research/v28_frozen_boundary_energy_fv_entry_latest.md` | discovered_v28_report_md | True | 6161 |  | 2026-05-10T00:39:49Z | 24270c395f6d |
| `logs/edge_research/v28_frozen_boundary_recross_shrink_fv_latest.md` | discovered_v28_report_md | True | 1065 |  | 2026-05-11T01:16:03Z | ee02ec5cb31c |
| `logs/edge_research/v28_frozen_boundary_temperature_fv_latest.md` | discovered_v28_report_md | True | 1058 |  | 2026-05-11T01:11:39Z | 18af630e7dd4 |
| `logs/edge_research/v28_frozen_composite_false_conviction_fv_latest.md` | discovered_v28_report_md | True | 1565 |  | 2026-05-11T00:57:59Z | 945e929363b2 |
| `logs/edge_research/v28_frozen_danger_zone_fv_calibration_latest.md` | discovered_v28_report_md | True | 910 |  | 2026-05-11T03:38:39Z | cfde6c54d63c |
| `logs/edge_research/v28_frozen_early_no_boundary_fv_entry_latest.md` | discovered_v28_report_md | True | 6381 |  | 2026-05-10T15:23:04Z | 9401d004297d |
| `logs/edge_research/v28_frozen_edge_phase_shrink_fv_latest.md` | discovered_v28_report_md | True | 999 |  | 2026-05-10T23:56:19Z | 4264b27107ab |
| `logs/edge_research/v28_frozen_forward_candidates_latest.md` | discovered_v28_report_md | True | 12366 |  | 2026-05-10T02:21:38Z | df73a61aa1e9 |
| `logs/edge_research/v28_frozen_forward_scorecard_latest.md` | discovered_v28_report_md | True | 1401 |  | 2026-05-11T03:40:04Z | d47234da4f35 |
| `logs/edge_research/v28_frozen_fv_bridge_exit_combo_stack_latest.md` | discovered_v28_report_md | True | 2785 |  | 2026-05-11T01:04:47Z | 2aab157fefdb |
| `logs/edge_research/v28_frozen_fv_bridge_exit_geometry_stack_latest.md` | discovered_v28_report_md | True | 2792 |  | 2026-05-11T01:04:47Z | f488fe2c1e20 |
| `logs/edge_research/v28_frozen_mid_edge_false_conviction_fv_latest.md` | discovered_v28_report_md | True | 1154 |  | 2026-05-11T01:16:59Z | d023c115eec8 |
| `logs/edge_research/v28_frozen_no_mid_edge_fv_latest.md` | discovered_v28_report_md | True | 864 |  | 2026-05-11T01:21:49Z | 4d078468363b |
| `logs/edge_research/v28_frozen_path_state_p70_fv_latest.md` | discovered_v28_report_md | True | 2563 |  | 2026-05-11T01:15:42Z | c210df695595 |
| `logs/edge_research/v28_frozen_raw_entry_calibrated_probability_latest.md` | discovered_v28_report_md | True | 34785 |  | 2026-05-11T03:44:09Z | 278049dccd25 |
| `logs/edge_research/v28_frozen_recross_book_shrink_fv_latest.md` | discovered_v28_report_md | True | 734 |  | 2026-05-11T03:11:34Z | 5f88a4cd930d |
| `logs/edge_research/v28_frozen_recross_escape_probability_calibration_latest.md` | discovered_v28_report_md | True | 1350 |  | 2026-05-11T03:42:59Z | 169fe8a448c4 |
| `logs/edge_research/v28_frozen_side_asymmetry_fv_overlay_latest.md` | discovered_v28_report_md | True | 8637 |  | 2026-05-11T01:41:43Z | 4cee8cb89b76 |
| `logs/edge_research/v28_frozen_target_coverage_conservative_fv_latest.md` | discovered_v28_report_md | True | 1039 |  | 2026-05-11T01:14:32Z | f2457f22898e |
| `logs/edge_research/v28_frozen_target_coverage_p70_fv_latest.md` | discovered_v28_report_md | True | 979 |  | 2026-05-11T01:14:57Z | 40c345ac1585 |
| `logs/edge_research/v28_frozen_weak_reversal_residual_fv_shrink_latest.md` | discovered_v28_report_md | True | 990 |  | 2026-05-11T01:20:31Z | 50f84511442f |
| `logs/edge_research/v28_full_policy_candidate_scorecard_latest.md` | discovered_v28_report_md | True | 14798 |  | 2026-05-07T21:43:52Z | 7007ddd63d33 |
| `logs/edge_research/v28_fv_bridge_direction_vs_realized_latest.md` | discovered_v28_report_md | True | 12584 |  | 2026-05-11T01:04:45Z | 6148676419ba |
| `logs/edge_research/v28_fv_bridge_exit_combo_bakeoff_latest.md` | discovered_v28_report_md | True | 14685 |  | 2026-05-11T01:04:46Z | 3ee4577f9afe |
| `logs/edge_research/v28_fv_bridge_exit_geometry_stack_latest.md` | discovered_v28_report_md | True | 9804 |  | 2026-05-11T01:04:46Z | d315a9bd8509 |
| `logs/edge_research/v28_fv_bridge_source_quality_latest.md` | discovered_v28_report_md | True | 2892 |  | 2026-05-08T22:09:42Z | 7e3c02a9e5a4 |
| `logs/edge_research/v28_fv_bridge_stack_residual_exit_attribution_latest.md` | discovered_v28_report_md | True | 13053 |  | 2026-05-11T01:04:46Z | 4ebd596fd8bd |
| `logs/edge_research/v28_fv_candidate_decision_matrix_latest.md` | discovered_v28_report_md | True | 25795 |  | 2026-05-11T03:06:39Z | 70c4fbfa350c |
| `logs/edge_research/v28_fv_overlay_challenger_readiness_latest.md` | discovered_v28_report_md | True | 3380 |  | 2026-05-11T03:45:34Z | c5dd2dd71ada |
| `logs/edge_research/v28_hybrid_boundary_entry_stack_source_stress_latest.md` | discovered_v28_report_md | True | 2165 |  | 2026-05-11T00:48:30Z | fcc462c321e3 |
| `logs/edge_research/v28_hybrid_boundary_source_dilution_runway_latest.md` | discovered_v28_report_md | True | 5686 |  | 2026-05-11T00:49:16Z | 315a886961d0 |
| `logs/edge_research/v28_hybrid_boundary_source_frontier_latest.md` | discovered_v28_report_md | True | 7648 |  | 2026-05-07T11:18:57Z | b1ad16bf114b |
| `logs/edge_research/v28_hybrid_confidence_shrink_fv_latest.md` | discovered_v28_report_md | True | 18472 |  | 2026-05-11T03:36:25Z | cb2b3712e8ab |
| `logs/edge_research/v28_live_trade_readiness_latest.md` | discovered_v28_report_md | True | 30400 |  | 2026-05-11T03:07:59Z | 9eb69c56682f |
| `logs/edge_research/v28_midprice_source_dilution_mechanism_latest.md` | discovered_v28_report_md | True | 43778 |  | 2026-05-11T02:50:32Z | a1660ca204df |
| `logs/edge_research/v28_midprice_source_dilution_runway_latest.md` | discovered_v28_report_md | True | 1453 |  | 2026-05-11T02:50:33Z | e478c211454c |
| `logs/edge_research/v28_midprice_source_dilution_stability_latest.md` | discovered_v28_report_md | True | 5344 |  | 2026-05-11T02:49:40Z | 951c4bea8ade |
| `logs/edge_research/v28_midprice_source_dilution_watch_latest.md` | discovered_v28_report_md | True | 6677 |  | 2026-05-11T02:49:40Z | b7b543295ea8 |
| `logs/edge_research/v28_no_mid_edge_fv_generalization_latest.md` | discovered_v28_report_md | True | 1025 |  | 2026-05-11T01:21:09Z | ed075580e886 |
| `logs/edge_research/v28_p50_book_edge_source_failure_drilldown_latest.md` | discovered_v28_report_md | True | 6442 |  | 2026-05-11T03:10:50Z | 22886eb09bf4 |
| `logs/edge_research/v28_p50_book_edge_source_feasibility_bound_latest.md` | discovered_v28_report_md | True | 2885 |  | 2026-05-11T03:10:50Z | f6a39eb0bbd9 |
| `logs/edge_research/v28_path_rmt_forward_gate_latest.md` | discovered_v28_report_md | True | 3178 |  | 2026-05-11T03:45:33Z | b7a423364a1a |
| `logs/edge_research/v28_pending_fv_sensitivity_latest.md` | discovered_v28_report_md | True | 117 |  | 2026-05-11T03:07:45Z | b7f91cf3b408 |
| `logs/edge_research/v28_phi_forgetting_fv_candidates_latest.md` | discovered_v28_report_md | True | 4638 |  | 2026-05-11T03:03:47Z | a0c52112a477 |
| `logs/edge_research/v28_policy_fv_matrix_latest.md` | discovered_v28_report_md | True | 2586 |  | 2026-05-11T03:12:01Z | f478622e58b9 |
| `logs/edge_research/v28_promotion_readiness_latest.md` | discovered_v28_report_md | True | 3311 |  | 2026-05-11T03:12:02Z | d15a5fd76ef0 |
| `logs/edge_research/v28_raw_entry_calibrated_probability_latest.md` | discovered_v28_report_md | True | 3389 |  | 2026-05-11T03:36:43Z | 92b6d4aa4091 |
| `logs/edge_research/v28_raw_p52_forward_loss_cluster_latest.md` | discovered_v28_report_md | True | 51160 |  | 2026-05-11T03:24:31Z | 55e1c829c232 |
| `logs/edge_research/v28_recross_escape_probability_calibration_latest.md` | discovered_v28_report_md | True | 2552 |  | 2026-05-11T03:34:55Z | 5e8c89f447f2 |
| `logs/edge_research/v28_reward_memory_fv_candidates_latest.md` | discovered_v28_report_md | True | 27500 |  | 2026-05-11T03:04:17Z | 5ec8a635122c |
| `logs/edge_research/v28_shadow_fv_variants_latest.md` | discovered_v28_report_md | True | 3040 |  | 2026-05-11T03:17:01Z | 8b3c33158222 |

## Read

- `v28_forward_calibration_latest.csv` is the first parsed seed source.
- Large live bot logs are inventoried only in this milestone; they are not parsed yet.
- A source appearing here does not make its rows promotion-grade. Source quality is assigned at row-build time.
