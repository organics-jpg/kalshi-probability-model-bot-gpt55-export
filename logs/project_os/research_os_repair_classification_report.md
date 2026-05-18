# Research OS V2 Overnight Report

Generated UTC: 2026-05-18T11:19:34Z
Registry snapshot UTC: 2026-05-18T11:17:32Z

Scope: research-only registry report. No scorer, bot, order, threshold, secret, state, stats, or dashboard action is implied by this file.

## Executive Snapshot

- Registry nodes: 1406 across 12 families.
- Candidates: 16; reports: 63; datasets: 92; health issues: 10.
- Evidence mix: Diagnostic=905, Forward Shadow=216, Metadata Only=158, Live Stats=101, Backtest=11.
- Status mix: Diagnostic only=1033, Needs more proof=152, Active=137, Blocked=37, Worth watching=13.

## Run Metadata

- workspace: C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT
- registry_nodes: 1406
- registry_edges: 1522
- registry_issues: 10
- research_moves: 12
- positive_blocked: 36
- failure_motifs: 19
- nearest_prior: 118
- family_gaps: 12
- lineage_gaps: 0
- unclassified_nodes: 0
- research_only: True

## Files Changed

- project_os/family.py
- project_os/adapters/scripts_adapter.py
- project_os/adapters/particle_reports_adapter.py
- project_os/adapters/sensitive_adapter.py
- project_os/registry.py
- project_os/graph.py
- project_os/views/dashboard_views.py
- project_os/patterns.py
- test_project_os_registry.py
- logs/project_os/registry_latest.json
- logs/project_os/registry_20260518T111700Z.json
- logs/project_os/registry_20260518T111732Z.json
- logs/project_os/research_os_repair_classification_report.md
- logs/project_os/research_os_v2_patterns_latest.json

## Tests Run

- python -m compileall project_os project_os_dashboard.py test_project_os_registry.py test_project_os_patterns.py test_project_os_graph.py: passed
- python -m unittest test_project_os_registry.py test_project_os_patterns.py test_project_os_graph.py -v: passed, 19 tests OK
- strict secret scan over registry_latest.json: 0 hits for token/private-key patterns

## Browser QA

- URL http://127.0.0.1:8503/ loaded with title Kalshi Research OS
- error count 0; graph nonblank; point count 925
- Pattern Cartography, Research Moves, Family Research Map, and Lineage Gaps visible
- modebar visible count 0; CSS leak false
- local-only sensitive warning visible
- 8501 and 8503 verified as separate listeners

## Top Research Moves

- rv600_regime_filter_rescue_latest
  - Lane: Do Not Repeat
  - Family: rv600
  - Signal: rv600 \\| Metadata Only \\| P&L 1742c (~$17.42)
  - Evidence: Metadata Only
  - Why: Status/blockers still say this is not proof.
  - Next Action: Do not rerun as-is; change blocker mechanism or pre-register a clean variant.
  - Risk: Positive P&L is not proof while blockers remain.
  - Source Nodes: rv600_regime_filter_rescue_latest
  - Move: Do not rerun as-is; change blocker mechanism or pre-register a clean variant.
- rv600_prequential_selection_gap1_latest
  - Lane: Do Not Repeat
  - Family: rv600
  - Signal: 0.962 similar to rv600_prequential_selection_best_all_entries_latest (prior)
  - Evidence: Metadata Only
  - Why: Do not repeat unchanged
  - Next Action: Document the changed assumption before another sibling test.
  - Risk: Near-duplicate attempt can recycle a blocked prior.
  - Source Nodes: rv600_prequential_selection_gap1_latest \\| rv600_prequential_selection_best_all_entries_latest (prior)
  - Move: Do not repeat unchanged
- paired_sidecar_slice_stability_latest
  - Lane: Do Not Repeat
  - Family: v28_successor
  - Signal: v28_successor \\| Metadata Only \\| P&L 1752.5c (~$17.52)
  - Evidence: Metadata Only
  - Why: Status/blockers still say this is not proof.
  - Next Action: Do not rerun as-is; change blocker mechanism or pre-register a clean variant.
  - Risk: Positive P&L is not proof while blockers remain.
  - Source Nodes: paired_sidecar_slice_stability_latest
  - Move: Do not rerun as-is; change blocker mechanism or pre-register a clean variant.
- paired_sidecar_blend_failure_analysis_latest
  - Lane: Do Not Repeat
  - Family: v28_successor
  - Signal: v28_successor \\| Metadata Only \\| P&L 2108.1c (~$21.08)
  - Evidence: Metadata Only
  - Why: Status/blockers still say this is not proof.
  - Next Action: Do not rerun as-is; change blocker mechanism or pre-register a clean variant.
  - Risk: Positive P&L is not proof while blockers remain.
  - Source Nodes: paired_sidecar_blend_failure_analysis_latest
  - Move: Do not rerun as-is; change blocker mechanism or pre-register a clean variant.
- rv600 / unclassified_blocker
  - Lane: Repair Lineage
  - Family: rv600
  - Signal: 18 affected nodes
  - Evidence: blocker motif
  - Why: Blocked/rejected node lacks a normalized motif.
  - Next Action: Classify the blocker before another sibling run.
  - Risk: Repeating siblings without fixing this motif will blur conclusions.
  - Source Nodes: rv600_bounded_current_grid_latest, rv600_forward_futility_latest, rv600_locked_plan_forward_audit_la, rv600_market_balance_rescue_latest
  - Move: Classify the blocker before another sibling run.
- rv600 / positive_roots_below_60pct
  - Lane: Repair Lineage
  - Family: rv600
  - Signal: 10 affected nodes
  - Evidence: blocker motif
  - Why: Root-level edge is too concentrated or inconsistent.
  - Next Action: Raise positive root fraction with a pre-registered rule.
  - Risk: Repeating siblings without fixing this motif will blur conclusions.
  - Source Nodes: RV600REV001, rv600_group_dro_rescue_latest, rv600_next_evidence_shadow_smoke_o, rv600_objective_state_latest
  - Move: Raise positive root fraction with a pre-registered rule.
- rv600 / positive_markets_below_60pct
  - Lane: Repair Lineage
  - Family: rv600
  - Signal: 11 affected nodes
  - Evidence: blocker motif
  - Why: Market breadth is too weak for proof.
  - Next Action: Improve breadth before treating P&L as evidence.
  - Risk: Repeating siblings without fixing this motif will blur conclusions.
  - Source Nodes: RV600REV001, rv600_failure_pattern_audit_latest, rv600_group_dro_rescue_latest, rv600_next_evidence_shadow_smoke_o
  - Move: Improve breadth before treating P&L as evidence.
- Realized-vol / RV
  - Lane: Test Next
  - Family: particle_sim, rv600, v28_successor
  - Signal: 81 watch/active \\| Forward Shadow \\| P&L 17.42
  - Evidence: Forward Shadow
  - Why: Existing motif evidence is stronger than the surrounding alternatives.
  - Next Action: Reuse this motif, but vary one assumption and keep forward scoring strict.
  - Risk: Validate with blockers and baseline comparison visible.
  - Source Nodes: rv600_preflight_pairing_20260515T023653Z, rv600_offline_control_patch_smoke_20260515, rv600_next_evidence_shadow_smoke_20260513T
  - Move: Reuse this motif, but vary one assumption and keep forward scoring strict.
- Forward/OOS proof
  - Lane: Test Next
  - Family: dashboard_ui, live_v28, ou_mispricing, particle_sim
  - Signal: 100 watch/active \\| Forward Shadow \\| P&L 21.08
  - Evidence: Forward Shadow
  - Why: Existing motif evidence is stronger than the surrounding alternatives.
  - Next Action: Reuse this motif, but vary one assumption and keep forward scoring strict.
  - Risk: Validate with blockers and baseline comparison visible.
  - Source Nodes: mushroom_v28_common_clock_exit_guard_v1_so, mushroom_v28_common_clock_phi_reward_memor, mushroom_v28_common_clock_exit_guard_v1_so
  - Move: Reuse this motif, but vary one assumption and keep forward scoring strict.

## Reusable Motifs

| Motif | Families | Nodes | Candidates | Watch/active | Blocked/rejected | Best Evidence | Best P&L | Guidance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Forward/OOS proof | dashboard_ui, live_v28, ou_mispricing, particle_sim | 207 | 16 | 100 | 42 | Forward Shadow | 21.08 | Reuse this motif, but vary one assumption and keep forward scoring strict. |
| Fillability / source quality | infrastructure, particle_sim, rv600, v28_successor | 103 | 1 | 91 | 8 | Forward Shadow | 7.43 | Reuse this motif, but vary one assumption and keep forward scoring strict. |
| Realized-vol / RV | particle_sim, rv600, v28_successor | 134 | 7 | 81 | 30 | Forward Shadow | 17.42 | Reuse this motif, but vary one assumption and keep forward scoring strict. |
| Accounting / fee integrity | infrastructure, legacy_live, live_v28, ou_mispricing | 64 | 0 | 15 | 8 | Forward Shadow | 24.69 | Reuse this motif, but vary one assumption and keep forward scoring strict. |
| Live/stat evidence | dashboard_ui, infrastructure, legacy_live, live_v28 | 72 | 0 | 15 | 2 | Live Stats | 24.69 | Reuse this motif, but vary one assumption and keep forward scoring strict. |
| Common-clock v28 | infrastructure, live_v28, ou_mispricing, particle_sim | 103 | 14 | 13 | 31 | Forward Shadow | 21.08 | Reuse this motif, but vary one assumption and keep forward scoring strict. |
| Exit / risk control | infrastructure, live_v28, ou_mispricing, truffle | 43 | 0 | 8 | 0 | Live Stats | 0.51 | Reuse this motif, but vary one assumption and keep forward scoring strict. |
| Consensus / ensemble | particle_sim, rv600, v28_successor | 13 | 5 | 5 | 2 | Forward Shadow | 21.08 | Reuse this motif, but vary one assumption and keep forward scoring strict. |

Showing 8 of 16 rows.

## Patterns Not To Rerun Blindly

| Family | Pattern | Attempts | Watch/active | Blocked/rejected | Best Evidence | Risk | Guidance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rv600 | Forward/OOS proof + Realized-vol / RV | 12 | 0 | 8 | Forward Shadow | High repeat risk | Do not create another sibling until blocker/assumption changed. |
| v28_successor | Common-clock v28 + Forward/OOS proof + Sidecar / slice | 12 | 0 | 7 | Forward Shadow | High repeat risk | Do not create another sibling until blocker/assumption changed. |
| rv600 | Replay / backtest + Baseline comparison + Common-clock v28 + Forward/OOS proof | 7 | 0 | 7 | Forward Shadow | High repeat risk | Do not create another sibling until blocker/assumption changed. |
| rv600 | Replay / backtest + Forward/OOS proof + Realized-vol / RV | 7 | 0 | 2 | Forward Shadow | High repeat risk | Do not create another sibling until blocker/assumption changed. |
| live_v28 | Accounting / fee integrity + Common-clock v28 + Exit / risk control + Forward/OOS proof | 18 | 6 | 0 | Live Stats | Needs lineage check | Keep, but branch with a clearly different mechanism. |
| live_v28 | Accounting / fee integrity + Common-clock v28 + Live/stat evidence | 9 | 5 | 0 | Live Stats | Needs lineage check | Keep, but branch with a clearly different mechanism. |
| rv600 | Accounting / fee integrity + Replay / backtest + Baseline comparison + Common-clock v28 | 4 | 0 | 4 | Forward Shadow | Needs lineage check | Do not create another sibling until blocker/assumption changed. |
| v28_successor | Common-clock v28 + Forward/OOS proof | 4 | 0 | 0 | Forward Shadow | Needs lineage check | Do not create another sibling until blocker/assumption changed. |

Showing 8 of 11 rows.

## Positive But Blocked

| Label | Family | Kind | Status | Evidence | P&L | Primary Blocker | Do Next |
| --- | --- | --- | --- | --- | --- | --- | --- |
| paired_sidecar_blend_failure_analysis_latest | v28_successor | report | Blocked | Metadata Only | 2108.1c (~$21.08) | blocked/rejected without a structured blocker edge | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |
| paired_sidecar_slice_stability_latest | v28_successor | report | Blocked | Metadata Only | 1752.5c (~$17.52) | underpowered_markets, nonpositive_top_ev_pnl, low_positive_market_fraction, worse_or_equal_selected_vs_v28, worse_or_equal_top_ev_vs_v28 | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |
| rv600_regime_filter_rescue_latest | rv600 | report | Rejected | Metadata Only | 1742c (~$17.42) |  | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |
| paired_sidecar_slice_oos_PSLICELOCK001_latest | v28_successor | report | Blocked | Forward Shadow | 1739.7c (~$17.40) | blocked/rejected without a structured blocker edge | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |
| rv600_market_balance_rescue_latest | rv600 | report | Rejected | Metadata Only | 1700c (~$17.00) |  | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |
| paired_sidecar_slice_oos_PSLICELOCK002_latest | v28_successor | report | Blocked | Forward Shadow | 1516.5c (~$15.16) | blocked/rejected without a structured blocker edge | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |
| paired_sidecar_slice_oos_PSLICELOCK003_latest | v28_successor | report | Blocked | Forward Shadow | 1460c (~$14.60) | blocked/rejected without a structured blocker edge | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |
| rv600_group_dro_rescue_latest | rv600 | report | Rejected | Metadata Only | 1451c (~$14.51) |  | Do not rerun as-is; change blocker mechanism or pre-register a clean variant. |

Showing 8 of 36 rows.

## Failure Motifs

| Family | Failure Motif | Count | Affected Nodes | Example | Likely Meaning | Required Change |
| --- | --- | --- | --- | --- | --- | --- |
| rv600 | unclassified_blocker | 18 | rv600_bounded_current_grid_latest, rv600_forward_futility_latest, rv600_locked_plan_forward_audit_la, rv600_market_balance_rescue_latest | blocked/rejected without a structured blocker edge | Blocked/rejected node lacks a normalized motif. | Classify the blocker before another sibling run. |
| rv600 | positive_markets_below_60pct | 11 | RV600REV001, rv600_failure_pattern_audit_latest, rv600_group_dro_rescue_latest, rv600_next_evidence_shadow_smoke_o |  | Market breadth is too weak for proof. | Improve breadth before treating P&L as evidence. |
| rv600 | positive_roots_below_60pct | 10 | RV600REV001, rv600_group_dro_rescue_latest, rv600_next_evidence_shadow_smoke_o, rv600_objective_state_latest |  | Root-level edge is too concentrated or inconsistent. | Raise positive root fraction with a pre-registered rule. |
| rv600 | avg_entry_below_10c | 9 | RV600REV001, rv600_failure_pattern_audit_latest, rv600_next_evidence_shadow_smoke_o, rv600_objective_state_latest |  | Average entry count is too small. | Increase fillable entry count before comparing families. |
| v28_successor | unclassified_blocker | 8 | paired_sidecar_blend_failure_analy, paired_sidecar_slice_lock_comparis, paired_sidecar_slice_market_breakd, paired_sidecar_slice_oos_PSLICELOC | blocked/rejected without a structured blocker edge | Blocked/rejected node lacks a normalized motif. | Classify the blocker before another sibling run. |
| rv600 | nonpositive_pnl | 7 | RV600REV001, rv600_next_evidence_shadow_smoke_o, rv600_objective_state_latest, rv600_plan_family_rejection_latest |  | Profitability is not positive after the reported accounting. | Do not repeat without changing the core mechanism. |
| rv600 | last_window_nonpositive | 7 | rv600_failure_pattern_audit_latest, rv600_next_evidence_shadow_smoke_o, rv600_parameter_plateau_audit_late, rv600_plan_family_rejection_latest | blocked_not_complete | The newest evidence window did not stay positive. | Collect a cleaner forward window or change the timing rule. |
| rv600 | accounting | 7 | rv600_group_dro_rescue_latest, rv600_native_forward_opportunity_l, rv600_next_evidence_shadow_smoke_o, rv600_prequential_selection_best_a |  | Accounting or fee treatment is unresolved. | Reconcile fees/fills before treating the result as proof. |
| rv600 | fewer_than_25_entries | 6 | rv600_native_forward_opportunity_l, rv600_next_evidence_shadow_smoke_o, rv600_plan_family_rejection_latest, rv600_prequential_selection_best_a | fewer_than_25_entries;single_market_share_above_25pct  \\| market \\| decision_ts \\| secs_to_close \\| side \\| ask \\| ev \\| pnl \\| v28_side \\| v28_ev \\| v28_pnl \\| added... | Sample has too few entries. | Get a larger pre-registered sample. |
| rv600 | does_not_beat_matched_v28_by_20pct | 5 | RV600REV001, rv600_native_forward_opportunity_l, rv600_objective_state_latest, rv600_plan_family_rejection_latest |  | It did not clear the matched baseline hurdle. | Change the edge source or baseline comparison, not just parameters. |

Showing 10 of 19 rows.

## Lineage Gaps

No rows available from the current registry snapshot.

## Nearest Prior Lineage

| Label | Family | Kind | Nearest Prior | Similarity | Prior Status | Prior Evidence | Changed Assumption | Repeat Warning |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rv600_prequential_selection_gap1_latest | rv600 | report | rv600_prequential_selection_best_all_entries_latest (prior) | 0.962 | Blocked | Metadata Only | No clear assumption delta detected | Do not repeat unchanged |
| rv600_prequential_selection_best_all_entries_latest | rv600 | report | rv600_prequential_selection_gap1_latest (sibling) | 0.962 | Blocked | Metadata Only | No clear assumption delta detected | Do not repeat unchanged |
| rv600_shadow_smoke_audit_latest | rv600 | report | rv600_shadow_bounded_audit_latest (sibling) | 0.943 | Blocked | Forward Shadow | No clear assumption delta detected | Do not repeat unchanged |
| rv600_shadow_bounded_audit_latest | rv600 | report | rv600_shadow_smoke_audit_latest (prior) | 0.943 | Blocked | Forward Shadow | No clear assumption delta detected | Do not repeat unchanged |
| rv600_prequential_selection_latest | rv600 | report | rv600_prequential_selection_gap1_latest (sibling) | 0.908 | Blocked | Metadata Only | No clear assumption delta detected | Do not repeat unchanged |
| rv600_next_evidence_shadow_smoke_opportunity_latest | rv600 | report | rv600_native_forward_opportunity_latest (sibling) | 0.895 | Blocked | Forward Shadow | No clear assumption delta detected | Do not repeat unchanged |
| rv600_native_forward_opportunity_latest | rv600 | report | rv600_next_evidence_shadow_smoke_opportunity_latest (prior) | 0.895 | Blocked | Forward Shadow | No clear assumption delta detected | Do not repeat unchanged |
| score_live_mushroom_v28_size2_now | live_v28 | stats | score_live_feature_gate_ask65_now (prior) | 0.87 | Worth watching | Live Stats | No clear assumption delta detected | Do not repeat unchanged |
| score_live_feature_gate_ask65_now | live_v28 | stats | score_live_mushroom_v28_size2_now (sibling) | 0.87 | Worth watching | Live Stats | No clear assumption delta detected | Do not repeat unchanged |
| score_live_common_clock_sourcefix_size1_now | live_v28 | stats | score_live_common_clock_size1_now (prior) | 0.87 | Needs more proof | Live Stats | No clear assumption delta detected | Do not repeat unchanged |

Showing 10 of 118 rows.

## Family Gaps

| Family | Nodes | Candidates | Reports | Stats | Forward Evidence | Live Evidence | Blocked/Rejected | Watch/Active | Dominant Motifs | Gap Flags | Next Move |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v28_successor | 862 | 13 | 19 | 0 | 98 | 39 | 14 | 13 | common clock, backtest replay, forward oos, exit risk | NO_STATS, REPEAT_RISK_HIGH | Stop sibling variants until the changed assumption is explicit. |
| rv600 | 233 | 3 | 41 | 0 | 99 | 0 | 31 | 79 | rv vol, forward oos, backtest replay, fill quality | NO_STATS, REPEAT_RISK_HIGH | Stop sibling variants until the changed assumption is explicit. |
| strategy_research | 107 | 0 | 0 | 0 | 8 | 9 | 0 | 0 | backtest replay, forward oos, live stats, exit risk | NO_CANDIDATE, NO_STATS, DATA_WITHOUT_CANDIDATE | Name the strongest artifact as a candidate or archive the family. |
| live_v28 | 64 | 0 | 0 | 32 | 0 | 53 | 0 | 35 | common clock, live stats, forward oos, exit risk | NO_CANDIDATE, NO_FORWARD_EVIDENCE, DATA_WITHOUT_CANDIDATE | Name the strongest artifact as a candidate or archive the family. |
| particle_sim | 42 | 0 | 1 | 0 | 17 | 0 | 0 | 17 | forward oos, backtest replay, fill quality, rv vol | NO_CANDIDATE, NO_STATS, DATA_WITHOUT_CANDIDATE | Name the strongest artifact as a candidate or archive the family. |
| ou_mispricing | 27 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | mispricing ou, backtest replay, exit risk, live stats | NO_CANDIDATE, NO_FORWARD_EVIDENCE, NO_STATS, DATA_WITHOUT_CANDIDATE, POSITIVE_DIAGNOSTIC_NO_FREEZE | Name the strongest artifact as a candidate or archive the family. |
| truffle | 22 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | backtest replay, live stats, exit risk, truffle | NO_CANDIDATE, NO_FORWARD_EVIDENCE, DATA_WITHOUT_CANDIDATE | Name the strongest artifact as a candidate or archive the family. |
| legacy_live | 10 | 0 | 0 | 5 | 0 | 5 | 0 | 3 | live stats, accounting, backtest replay, common clock | NO_CANDIDATE, NO_FORWARD_EVIDENCE, DATA_WITHOUT_CANDIDATE | Name the strongest artifact as a candidate or archive the family. |
| ninety_touch | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | touch threshold, backtest replay, exit risk | NO_CANDIDATE, NO_FORWARD_EVIDENCE, NO_STATS | Name the strongest artifact as a candidate or archive the family. |
| infrastructure | 17 | 0 | 0 | 1 | 0 | 0 | 0 | 3 | backtest replay, live stats, infrastructure, fill quality | NONE | Monitor; no major family gap detected. |
| dashboard_ui | 13 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | backtest replay, live stats, common clock, exit risk | NONE | Monitor; no major family gap detected. |
| research_os | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | phi memory, live stats, forward oos, research os | NONE | Monitor; no major family gap detected. |

## Source Anchors

- `health_issue:rv600:logs_adapter_large_log_folder_particle_research` | large log folder: particle_research | health_issue | Health issue | Metadata Only | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\particle_research
- `health_issue:ninety_touch:logs_adapter_large_log_folder_edge_research` | large log folder: edge_research | health_issue | Health issue | Metadata Only | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research
- `health_issue:live_v28:logs_adapter_large_log_folder_live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live` | large log folder: live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live | health_issue | Health issue | Metadata Only | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live
- `health_issue:infrastructure:stats_adapter_missing_stats_summary_default` | missing stats summary: default | health_issue | Health issue | Metadata Only | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\default
- `health_issue:live_v28:logs_adapter_large_log_folder_live_mushroom_v28_common_clock_phi_reward_memory_size2_live` | large log folder: live_mushroom_v28_common_clock_phi_reward_memory_size2_live | health_issue | Health issue | Metadata Only | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\live_mushroom_v28_common_clock_phi_reward_memory_size2_live
- `health_issue:live_v28:stats_adapter_missing_stats_summary_mushroom_v28_size2_live` | missing stats summary: mushroom_v28_size2_live | health_issue | Health issue | Metadata Only | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_size2_live
- `health_issue:live_v28:stats_adapter_missing_stats_summary_mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_btcrest_size1_live` | missing stats summary: 'mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_btcrest_size1_live' | health_issue | Health issue | Metadata Only | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\'mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_btcrest_size1_live'
- `health_issue:live_v28:stats_adapter_missing_stats_summary_mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_btcrotate_size1_live` | missing stats summary: 'mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_btcrotate_size1_live' | health_issue | Health issue | Metadata Only | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\'mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_btcrotate_size1_live'
- `health_issue:infrastructure:sensitive_adapter_sensitive_file_indexed_.env` | sensitive file indexed: .env | health_issue | Health issue | Metadata Only | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\.env
- `health_issue:infrastructure:sensitive_adapter_sensitive_file_indexed_kalshi_private_key.pem` | sensitive file indexed: kalshi_private_key.pem | health_issue | Health issue | Metadata Only | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\secrets\kalshi_private_key.pem
- `stats:live_v28:mushroom_v28_common_clock_phi_reward_memory_lifecycle_score_probe` | mushroom_v28_common_clock_phi_reward_memory_lifecycle_score_probe | stats | Worth watching | Live Stats | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_phi_reward_memory_lifecycle_score_probe
- `stats:live_v28:mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_nowindow_live` | mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_nowindow_live | stats | Worth watching | Live Stats | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_nowindow_live

## Residual Risks

- unclassified nodes after repair: 0
- lineage gaps after repair: 0
- health issues remaining: 10; remaining issues are large-log metadata-only warnings, missing stats summaries, and sensitive-file path markers with raw contents omitted
- family gap rows remaining: 12; these are research evidence gaps, not classification failures
- positive-but-blocked traps remain: 36; left visible intentionally as decision warnings

## Research Guardrail

This report summarizes registry evidence and pattern pressure only. It is not a live-order, deployment, sizing, or threshold-change recommendation.
