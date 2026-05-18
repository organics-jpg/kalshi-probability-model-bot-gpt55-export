# Research OS V2 Overnight Report

Generated UTC: 2026-05-18T18:58:24Z
Registry snapshot UTC: 2026-05-18T18:58:13Z

Scope: research-only registry report. No scorer, bot, order, threshold, secret, state, stats, or dashboard action is implied by this file.

## Executive Snapshot

- Registry nodes: 1420 across 12 families.
- Candidates: 37; reports: 64; datasets: 92; health issues: 0.
- Evidence mix: Diagnostic=907, Forward Shadow=245, Metadata Only=141, Live Stats=100, Backtest=11.
- Status mix: Diagnostic only=1039, Needs more proof=158, Active=134, Blocked=49, Worth watching=18.

## Run Metadata

- goal: candidate_readiness_reevaluation_all_nodes
- research_only: True

## Files Changed

- project_os/candidate_readiness.py
- project_os/adapters/v28_successor_candidates_adapter.py
- project_os/adapters/candidate_readiness_adapter.py
- project_os/adapters/__init__.py
- project_os/registry.py
- project_os/patterns.py
- reevaluate_project_os_candidates.py
- test_project_os_candidate_readiness.py
- test_project_os_patterns.py
- test_project_os_registry.py
- logs/project_os/candidate_readiness_reevaluation_latest.json
- logs/project_os/candidate_readiness_reevaluation_latest.md
- logs/project_os/registry_latest.json

## Tests Run

- python -m py_compile project_os/candidate_readiness.py project_os/adapters/v28_successor_candidates_adapter.py project_os/adapters/candidate_readiness_adapter.py reevaluate_project_os_candidates.py
- python -m unittest test_project_os_candidate_readiness.py test_project_os_patterns.py test_project_os_registry.py -> 43 tests OK
- python -m unittest test_project_os_candidate_readiness.py test_project_os_patterns.py test_project_os_graph.py test_project_os_registry.py test_project_os_rv_validation.py -> 55 tests OK
- python -m unittest test_v28_successor_live_pnl_policy_lab.py test_v28_successor_pipeline.py -> 128 tests OK
- python -m compileall project_os reevaluate_project_os_candidates.py
- python -m json.tool logs/project_os/candidate_readiness_reevaluation_latest.json

## Browser QA

- Not run: this turn changed registry adapters, candidate metrics, tests, and logs/project_os outputs, not 8503 layout code.

## Top Research Moves

- v28s_monotonic_tabular_v001 / seed_diagnostic
  - Lane: Do Not Repeat
  - Family: v28_successor
  - Signal: 0.973 similar to v28s_logistic_boundary_physics_v001 / seed_diagnostic (prior)
  - Evidence: Forward Shadow
  - Why: Do not repeat unchanged
  - Next Action: Document the changed assumption before another sibling test.
  - Risk: Near-duplicate attempt can recycle a blocked prior.
  - Source Nodes: v28s_monotonic_tabular_v001 / seed_diagnostic \\| v28s_logistic_boundary_physics_v001 / seed_diagnostic (prior)
  - Move: Do not repeat unchanged
- dynamic_particle_next_locked_plan
  - Lane: Do Not Repeat
  - Family: v28_successor
  - Signal: v28_successor \\| Forward Shadow \\| P&L/7d $43553.66 \\| source 32406c (~$324.06)
  - Evidence: Forward Shadow
  - Why: Status/blockers still say this is not proof.
  - Next Action: Do not rerun as-is; change blocker mechanism or pre-register a clean variant.
  - Risk: Positive P&L is not proof while blockers remain.
  - Source Nodes: dynamic_particle_next_locked_plan
  - Move: Do not rerun as-is; change blocker mechanism or pre-register a clean variant.
- GAUSS45LOCK002
  - Lane: Do Not Repeat
  - Family: v28_successor
  - Signal: v28_successor \\| Forward Shadow \\| P&L/7d $47714.88 \\| source 49703c (~$497.03)
  - Evidence: Forward Shadow
  - Why: Status/blockers still say this is not proof.
  - Next Action: Do not rerun as-is; change blocker mechanism or pre-register a clean variant.
  - Risk: Positive P&L is not proof while blockers remain.
  - Source Nodes: GAUSS45LOCK002
  - Move: Do not rerun as-is; change blocker mechanism or pre-register a clean variant.
- GAUSS45LOCK001
  - Lane: Do Not Repeat
  - Family: v28_successor
  - Signal: v28_successor \\| Forward Shadow \\| P&L/7d $79514.40 \\| source 47330c (~$473.30)
  - Evidence: Forward Shadow
  - Why: Status/blockers still say this is not proof.
  - Next Action: Do not rerun as-is; change blocker mechanism or pre-register a clean variant.
  - Risk: Positive P&L is not proof while blockers remain.
  - Source Nodes: GAUSS45LOCK001
  - Move: Do not rerun as-is; change blocker mechanism or pre-register a clean variant.
- v28_successor / beats_baseline_logloss
  - Lane: Repair Lineage
  - Family: v28_successor
  - Signal: 27 affected nodes
  - Evidence: blocker motif
  - Why: Baseline comparison depends on logloss behavior.
  - Next Action: Separate probability-quality evidence from execution evidence.
  - Risk: Repeating siblings without fixing this motif will blur conclusions.
  - Source Nodes: PSLICELOCK001, PSLICELOCK002, PSLICELOCK003, PSLICELOCK004
  - Move: Separate probability-quality evidence from execution evidence.
- v28_successor / beats_baseline_brier
  - Lane: Repair Lineage
  - Family: v28_successor
  - Signal: 26 affected nodes
  - Evidence: blocker motif
  - Why: Baseline comparison depends on Brier behavior.
  - Next Action: Separate calibration win from tradeable P&L proof.
  - Risk: Repeating siblings without fixing this motif will blur conclusions.
  - Source Nodes: PSLICELOCK001, PSLICELOCK002, PSLICELOCK003, PSLICELOCK004
  - Move: Separate calibration win from tradeable P&L proof.
- rv600 / unclassified_blocker
  - Lane: Repair Lineage
  - Family: rv600
  - Signal: 20 affected nodes
  - Evidence: blocker motif
  - Why: Blocked/rejected node lacks a normalized motif.
  - Next Action: Classify the blocker before another sibling run.
  - Risk: Repeating siblings without fixing this motif will blur conclusions.
  - Source Nodes: RESIDLOCK001, Rv600, rv600_bounded_current_grid_latest, rv600_forward_futility_latest
  - Move: Classify the blocker before another sibling run.
- Replay / backtest
  - Lane: Test Next
  - Family: dashboard_ui, infrastructure, legacy_live, live_v28
  - Signal: 109 watch/active \\| Forward Shadow \\| P&L/7d 79514.4
  - Evidence: Forward Shadow
  - Why: Existing motif evidence is stronger than the surrounding alternatives.
  - Next Action: Reuse this motif, but vary one assumption and keep forward scoring strict.
  - Risk: Validate with blockers and baseline comparison visible.
  - Source Nodes: v28s_boundary_monotonic_time_safe_v001 / l, v28s_boundary_monotonic_micro_time_safe_v0, CONSENSUSLOCK001
  - Move: Reuse this motif, but vary one assumption and keep forward scoring strict.
- Forward/OOS proof
  - Lane: Test Next
  - Family: dashboard_ui, live_v28, ou_mispricing, particle_sim
  - Signal: 104 watch/active \\| Live Forward \\| P&L/7d 79514.4
  - Evidence: Live Forward
  - Why: Existing motif evidence is stronger than the surrounding alternatives.
  - Next Action: Reuse this motif, but vary one assumption and keep forward scoring strict.
  - Risk: Validate with blockers and baseline comparison visible.
  - Source Nodes: v28s_boundary_monotonic_time_safe_v001 / l, v28s_live_pnl_midband_no_fade_yes_v019, v28s_boundary_monotonic_micro_time_safe_v0
  - Move: Reuse this motif, but vary one assumption and keep forward scoring strict.

## Reusable Motifs

| Motif | Families | Nodes | Candidates | Watch/active | Blocked/rejected | Best Evidence | Best P&L/7d | Guidance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Replay / backtest | dashboard_ui, infrastructure, legacy_live, live_v28 | 271 | 36 | 109 | 54 | Forward Shadow | 79514.4 | Reuse this motif, but vary one assumption and keep forward scoring strict. |
| Forward/OOS proof | dashboard_ui, live_v28, ou_mispricing, particle_sim | 240 | 37 | 104 | 54 | Live Forward | 79514.4 | Reuse this motif, but vary one assumption and keep forward scoring strict. |
| Fillability / source quality | infrastructure, particle_sim, rv600, v28_successor | 124 | 21 | 93 | 13 | Forward Shadow | 4704.0 | Reuse this motif, but vary one assumption and keep forward scoring strict. |
| Realized-vol / RV | ou_mispricing, particle_sim, rv600, v28_successor | 163 | 35 | 87 | 38 | Live Forward | 79514.4 | Reuse this motif, but vary one assumption and keep forward scoring strict. |
| Live/stat evidence | dashboard_ui, infrastructure, legacy_live, live_v28 | 109 | 37 | 16 | 13 | Live Forward | 79514.4 | Reuse this motif, but vary one assumption and keep forward scoring strict. |
| Common-clock v28 | infrastructure, live_v28, ou_mispricing, particle_sim | 130 | 36 | 14 | 41 | Live Forward | 79514.4 | Reuse this motif, but vary one assumption and keep forward scoring strict. |
| Accounting / fee integrity | legacy_live, live_v28, ou_mispricing, rv600 | 62 | 2 | 12 | 10 | Forward Shadow | 24.69 | Reuse this motif, but vary one assumption and keep forward scoring strict. |
| Consensus / ensemble | particle_sim, rv600, v28_successor | 21 | 7 | 8 | 8 | Forward Shadow | 79514.4 | Reuse this motif, but vary one assumption and keep forward scoring strict. |

Showing 8 of 15 rows.

## Patterns Not To Rerun Blindly

| Family | Pattern | Attempts | Watch/active | Blocked/rejected | Best Evidence | Best P&L/7d | Risk | Guidance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v28_successor | Replay / backtest + Baseline comparison + Common-clock v28 + Forward/OOS proof | 18 | 0 | 12 | Forward Shadow | 43553.66 | High repeat risk | Do not create another sibling until blocker/assumption changed. |
| v28_successor | Replay / backtest + Baseline comparison + Common-clock v28 + Fillability / source quality | 17 | 2 | 4 | Forward Shadow | 4704.0 | High repeat risk | Do not create another sibling until blocker/assumption changed. |
| rv600 | Replay / backtest + Baseline comparison + Common-clock v28 + Forward/OOS proof | 13 | 0 | 7 | Forward Shadow | 36.34 | High repeat risk | Do not create another sibling until blocker/assumption changed. |
| rv600 | Replay / backtest + Forward/OOS proof + Realized-vol / RV | 8 | 0 | 7 | Forward Shadow | 13.58 | High repeat risk | Do not create another sibling until blocker/assumption changed. |
| v28_successor | Replay / backtest + Common-clock v28 + Forward/OOS proof + Sidecar / slice | 7 | 0 | 3 | Metadata Only | 21.08 | High repeat risk | Do not create another sibling until blocker/assumption changed. |
| v28_successor | Replay / backtest + Baseline comparison + Common-clock v28 + Consensus / ensemble | 6 | 1 | 1 | Forward Shadow | 79514.4 | High repeat risk | Do not create another sibling until blocker/assumption changed. |
| rv600 | Accounting / fee integrity + Replay / backtest + Baseline comparison + Common-clock v28 | 5 | 0 | 5 | Forward Shadow | 17.42 | High repeat risk | Do not create another sibling until blocker/assumption changed. |
| live_v28 | Accounting / fee integrity + Replay / backtest + Common-clock v28 + Exit / risk control | 18 | 6 | 0 | Live Stats | 0.51 | Needs lineage check | Keep, but branch with a clearly different mechanism. |

Showing 8 of 12 rows.

## Positive But Blocked

| Label | Family | Kind | Status | Evidence | P&L/7d | P&L | Window | Primary Blocker | Do Next |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GAUSS45LOCK001 | v28_successor | candidate | Needs more proof | Forward Shadow | $79514.40 | 47330c (~$473.30) | 1h (assumed) | linked_oos_gate_failed:beats_brownian_probability | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |
| GAUSS45LOCK002 | v28_successor | candidate | Needs more proof | Forward Shadow | $47714.88 | 49703c (~$497.03) | 1.75h (assumed) | linked_oos_gate_failed:beats_brownian_probability | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |
| dynamic_particle_next_locked_plan | v28_successor | candidate | Needs more proof | Forward Shadow | $43553.66 | 32406c (~$324.06) | 1.25h (assumed) | linked_oos_gate_failed:beats_current_calibrated_pnl | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |
| RVTERMLOCK001 | v28_successor | candidate | Needs more proof | Forward Shadow | $16826.88 | 17528c (~$175.28) | 1.75h (assumed) | linked_oos_gate_failed:beats_current_calibrated_pnl | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |
| dynamic_particle600_next_locked_plan | v28_successor | candidate | Needs more proof | Forward Shadow | $5124.00 | 4575c (~$45.75) | 1.5h (assumed) | linked_oos_gate_failed:beats_current_calibrated_pnl | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |
| v28s_late_dsigma_residual_tilt_v001 / logged_events_diagnostic | v28_successor | candidate | Needs more proof | Forward Shadow | $4704.00 | 2800c (~$28.00) | 1h (assumed) | promotion_verifier_gate_failed:holdout_brier_better_than_v28 | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |
| v28s_boundary_monotonic_micro_time_safe_v001 / logged_events_diagnostic | v28_successor | candidate | Worth watching | Forward Shadow | $1881.60 | 2800c (~$28.00) | 2.5h (assumed) | promotion_verifier_gate_failed:forward_evidence_scored_and_promotable | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |
| CONSENSUSLOCK001 | v28_successor | candidate | Worth watching | Forward Shadow | $1620.64 | 1447c (~$14.47) | 1.5h (assumed) | linked_oos_gate_failed:positive_top_ev_bucket | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |

Showing 8 of 72 rows.

## Failure Motifs

| Family | Failure Motif | Count | Affected Nodes | Example | Likely Meaning | Required Change |
| --- | --- | --- | --- | --- | --- | --- |
| v28_successor | beats_baseline_logloss | 27 | PSLICELOCK001, PSLICELOCK002, PSLICELOCK003, PSLICELOCK004 | linked_oos_gate_failed:beats_baseline_brier | Baseline comparison depends on logloss behavior. | Separate probability-quality evidence from execution evidence. |
| v28_successor | beats_baseline_brier | 26 | PSLICELOCK001, PSLICELOCK002, PSLICELOCK003, PSLICELOCK004 | linked_oos_gate_failed:beats_baseline_brier | Baseline comparison depends on Brier behavior. | Separate calibration win from tradeable P&L proof. |
| rv600 | unclassified_blocker | 20 | RESIDLOCK001, Rv600, rv600_bounded_current_grid_latest, rv600_forward_futility_latest | linked_oos_gate_failed:beats_brownian_probability | Blocked/rejected node lacks a normalized motif. | Classify the blocker before another sibling run. |
| v28_successor | unclassified_blocker | 12 | GAUSS45LOCK003, V28 Successor, paired_sidecar_blend_failure_analy, paired_sidecar_slice_lock_comparis | linked_oos_gate_failed:beats_current_probability | Blocked/rejected node lacks a normalized motif. | Classify the blocker before another sibling run. |
| rv600 | positive_markets_below_60pct | 12 | RV600NEAR001, RV600REV001, rv600_failure_pattern_audit_latest, rv600_group_dro_rescue_latest | rv_forward_gate_failed:sample_accepted_entries | Market breadth is too weak for proof. | Improve breadth before treating P&L as evidence. |
| rv600 | positive_roots_below_60pct | 11 | RV600NEAR001, RV600REV001, rv600_group_dro_rescue_latest, rv600_next_evidence_shadow_smoke_o | rv_forward_gate_failed:sample_accepted_entries | Root-level edge is too concentrated or inconsistent. | Raise positive root fraction with a pre-registered rule. |
| rv600 | avg_entry_below_10c | 10 | RV600NEAR001, RV600REV001, rv600_failure_pattern_audit_latest, rv600_next_evidence_shadow_smoke_o | rv_forward_gate_failed:sample_accepted_entries | Average entry count is too small. | Increase fillable entry count before comparing families. |
| rv600 | nonpositive_pnl | 7 | RV600REV001, rv600_next_evidence_shadow_smoke_o, rv600_objective_state_latest, rv600_plan_family_rejection_latest | rv_forward_gate_failed:sample_accepted_entries | Profitability is not positive after the reported accounting. | Do not repeat without changing the core mechanism. |
| rv600 | last_window_nonpositive | 7 | rv600_failure_pattern_audit_latest, rv600_next_evidence_shadow_smoke_o, rv600_parameter_plateau_audit_late, rv600_plan_family_rejection_latest | blocked_not_complete | The newest evidence window did not stay positive. | Collect a cleaner forward window or change the timing rule. |
| rv600 | accounting | 7 | rv600_group_dro_rescue_latest, rv600_native_forward_opportunity_l, rv600_next_evidence_shadow_smoke_o, rv600_prequential_selection_best_a |  | Accounting or fee treatment is unresolved. | Reconcile fees/fills before treating the result as proof. |

Showing 10 of 19 rows.

## Lineage Gaps

No rows available from the current registry snapshot.

## Nearest Prior Lineage

| Label | Family | Kind | Nearest Prior | Similarity | Prior Status | Prior Evidence | Changed Assumption | Repeat Warning |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v28s_monotonic_tabular_v001 / seed_diagnostic | v28_successor | candidate | v28s_logistic_boundary_physics_v001 / seed_diagnostic (prior) | 0.973 | Needs more proof | Forward Shadow | No clear assumption delta detected | Do not repeat unchanged |
| v28s_monotonic_tabular_v001 / logged_events_diagnostic | v28_successor | candidate | v28s_logistic_boundary_physics_v001 / logged_events_diagnostic (prior) | 0.973 | Needs more proof | Forward Shadow | No clear assumption delta detected | Do not repeat unchanged |
| v28s_logistic_boundary_physics_v001 / seed_diagnostic | v28_successor | candidate | v28s_monotonic_tabular_v001 / seed_diagnostic (prior) | 0.973 | Needs more proof | Forward Shadow | No clear assumption delta detected | Do not repeat unchanged |
| v28s_logistic_boundary_physics_v001 / logged_events_diagnostic | v28_successor | candidate | v28s_monotonic_tabular_v001 / logged_events_diagnostic (prior) | 0.973 | Needs more proof | Forward Shadow | No clear assumption delta detected | Do not repeat unchanged |
| v28s_logistic_book_reliability_diag_v001 / logged_events_diagnostic | v28_successor | candidate | v28s_monotonic_tabular_v001 / logged_events_diagnostic (prior) | 0.973 | Needs more proof | Forward Shadow | No clear assumption delta detected | Do not repeat unchanged |
| v28s_boundary_monotonic_time_safe_v001 / seed_diagnostic | v28_successor | candidate | v28s_boundary_monotonic_light_v001 / seed_diagnostic (prior) | 0.973 | Needs more proof | Forward Shadow | No clear assumption delta detected | Do not repeat unchanged |
| v28s_boundary_monotonic_light_v001 / seed_diagnostic | v28_successor | candidate | v28s_boundary_monotonic_time_safe_v001 / seed_diagnostic (prior) | 0.973 | Needs more proof | Forward Shadow | No clear assumption delta detected | Do not repeat unchanged |
| rv600_prequential_selection_gap1_latest | rv600 | report | rv600_prequential_selection_best_all_entries_latest (prior) | 0.962 | Blocked | Metadata Only | No clear assumption delta detected | Do not repeat unchanged |
| rv600_prequential_selection_best_all_entries_latest | rv600 | report | rv600_prequential_selection_gap1_latest (sibling) | 0.962 | Blocked | Metadata Only | No clear assumption delta detected | Do not repeat unchanged |
| v28s_late_dsigma_residual_tilt_v001 / logged_events_diagnostic | v28_successor | candidate | v28s_monotonic_tabular_v001 / logged_events_diagnostic (prior) | 0.96 | Needs more proof | Forward Shadow | No clear assumption delta detected | Do not repeat unchanged |

Showing 10 of 140 rows.

## Family Gaps

| Family | Nodes | Candidates | Reports | Stats | Forward Evidence | Live Evidence | Blocked/Rejected | Watch/Active | Best P&L/7d | Dominant Motifs | Gap Flags | Next Move |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v28_successor | 886 | 34 | 20 | 0 | 127 | 40 | 48 | 17 | 79514.4 | common clock, backtest replay, forward oos, exit risk | NO_STATS, REPEAT_RISK_HIGH | Stop sibling variants until the changed assumption is explicit. |
| rv600 | 231 | 3 | 41 | 0 | 100 | 0 | 33 | 81 | 287.56 | backtest replay, rv vol, forward oos, fill quality | NO_STATS, REPEAT_RISK_HIGH | Stop sibling variants until the changed assumption is explicit. |
| strategy_research | 107 | 0 | 0 | 0 | 8 | 9 | 1 | 0 | 0.0 | backtest replay, forward oos, live stats, exit risk | NO_CANDIDATE, NO_STATS, DATA_WITHOUT_CANDIDATE | Name the strongest artifact as a candidate or archive the family. |
| live_v28 | 59 | 0 | 0 | 32 | 0 | 52 | 1 | 32 | 19.51 | backtest replay, common clock, live stats, forward oos | NO_CANDIDATE, NO_FORWARD_EVIDENCE, DATA_WITHOUT_CANDIDATE | Name the strongest artifact as a candidate or archive the family. |
| particle_sim | 42 | 0 | 1 | 0 | 17 | 0 | 1 | 17 | 0.0 | backtest replay, forward oos, fill quality, rv vol | NO_CANDIDATE, NO_STATS, DATA_WITHOUT_CANDIDATE | Name the strongest artifact as a candidate or archive the family. |
| ou_mispricing | 27 | 0 | 2 | 0 | 0 | 0 | 1 | 0 | 12.15 | backtest replay, mispricing ou, exit risk, forward oos | NO_CANDIDATE, NO_FORWARD_EVIDENCE, NO_STATS, DATA_WITHOUT_CANDIDATE, POSITIVE_DIAGNOSTIC_NO_FREEZE | Name the strongest artifact as a candidate or archive the family. |
| truffle | 22 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 0.0 | backtest replay, live stats, exit risk, baseline compare | NO_CANDIDATE, NO_FORWARD_EVIDENCE, DATA_WITHOUT_CANDIDATE | Name the strongest artifact as a candidate or archive the family. |
| legacy_live | 10 | 0 | 0 | 5 | 0 | 5 | 1 | 3 | 24.69 | backtest replay, live stats, accounting, baseline compare | NO_CANDIDATE, NO_FORWARD_EVIDENCE, DATA_WITHOUT_CANDIDATE | Name the strongest artifact as a candidate or archive the family. |
| ninety_touch | 4 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0.0 | backtest replay, touch threshold, exit risk, forward oos | NO_CANDIDATE, NO_FORWARD_EVIDENCE, NO_STATS | Name the strongest artifact as a candidate or archive the family. |
| infrastructure | 14 | 0 | 0 | 1 | 0 | 0 | 0 | 3 | 0.0 | backtest replay, live stats, fill quality, baseline compare | NONE | Monitor; no major family gap detected. |
| dashboard_ui | 13 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | backtest replay, live stats, forward oos, common clock | NONE | Monitor; no major family gap detected. |
| research_os | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | backtest replay, live stats, phi memory, forward oos | NONE | Monitor; no major family gap detected. |

## Source Anchors

- `candidate:v28_successor:v28s_boundary_monotonic_time_safe_v001_logged_events_diagnostic` | v28s_boundary_monotonic_time_safe_v001 / logged_events_diagnostic | candidate | Strong candidate | Forward Shadow | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_successor_promotion_verifier_latest.json
- `candidate:v28_successor:v28s_live_pnl_midband_no_fade_yes_v019` | v28s_live_pnl_midband_no_fade_yes_v019 | candidate | Worth watching | Live Forward | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_successor_live_pnl_policy_score_latest.json
- `candidate:v28_successor:CONSENSUSLOCK001` | CONSENSUSLOCK001 | candidate | Worth watching | Forward Shadow | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\particle_research\locked_oos_plans\side_consensus_CONSENSUSLOCK001_locked_oos_plan.json
- `candidate:v28_successor:v28s_boundary_monotonic_micro_time_safe_v001_logged_events_diagnostic` | v28s_boundary_monotonic_micro_time_safe_v001 / logged_events_diagnostic | candidate | Worth watching | Forward Shadow | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_successor_promotion_verifier_latest.json
- `report:rv600:locked_oos_stability_latest` | locked_oos_stability_latest | report | Worth watching | Forward Shadow | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\particle_research\reports\locked_oos_stability_latest.json
- `report:rv600:residual_blend_loro_locked_oos_latest` | residual_blend_loro_locked_oos_latest | report | Worth watching | Forward Shadow | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\particle_research\reports\residual_blend_loro_locked_oos_latest.json
- `stats:live_v28:mushroom_v28_common_clock_phi_reward_memory_lifecycle_score_probe` | mushroom_v28_common_clock_phi_reward_memory_lifecycle_score_probe | stats | Worth watching | Live Stats | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_score_probe
- `stats:live_v28:mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_nowindow_live` | mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_nowindow_live | stats | Worth watching | Live Stats | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_nowindow_live
- `stats:live_v28:mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size1_live` | mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size1_live | stats | Worth watching | Live Stats | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size1_live
- `stats:live_v28:mushroom_v28_common_clock_exit_guard_v1_sourcefix_featuregate_btcrest_size1_live` | mushroom_v28_common_clock_exit_guard_v1_sourcefix_featuregate_btcrest_size1_live | stats | Worth watching | Live Stats | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_exit_guard_v1_sourcefix_featuregate_btcrest_size1_live
- `stats:live_v28:mushroom_v28_common_clock_exit_guard_v1_sourcefix_broad_btcrest_size1_live` | mushroom_v28_common_clock_exit_guard_v1_sourcefix_broad_btcrest_size1_live | stats | Worth watching | Live Stats | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_exit_guard_v1_sourcefix_broad_btcrest_size1_live
- `stats:live_v28:score_live_mushroom_v28_size2_now` | score_live_mushroom_v28_size2_now | stats | Worth watching | Live Stats | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\score_live_mushroom_v28_size2_now

## Residual Risks

- Only one candidate is controlled-live-test ready under the balanced rubric; live-order readiness remains zero and intentionally requires a separate explicit gate.
- Three candidates are live-shadow ready but still below controlled-live-test criteria or Level 2 policy readiness.

## Research Guardrail

This report summarizes registry evidence and pattern pressure only. It is not a live-order, deployment, sizing, or threshold-change recommendation.
