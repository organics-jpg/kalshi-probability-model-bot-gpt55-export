# v28 Next Action Triage

Research-only triage. This does not promote candidates or place orders.

## Objective Status

- achieved: `False`
- any_live_ready: `False`
- control_risk_stop: `True`
- control_entries: `173`
- control_gross_cents: `823.0`
- control_risk_stop_reason: `loss_count`
- control_risk_stop_by_loss_count/drawdown: `True/False`
- control_max_drawdown_pct: `15.360502`
- control_full_loss_events/near_full_loss_events: `1/6`

## Next Actions

0.8. `repair_loss_count_churn_before_sidecar_live_test` - The global live-readiness blocker is loss-count churn, not drawdown: 75 losing scored trades, 1 full-loss events, 6 near-full losses, and max drawdown 15.360501567398119%. The current best churn lens is observable_reduce_loss_control_diagnostic with loss-count reduction 16 and delta 523.0c. Exit repairs must reduce small/medium loss clusters before a sidecar trial.
0.801. `use_loss_churn_frontier_to_find_observable_state_trigger_not_hindsight_label` - The refreshed guarded loss-churn frontier explains the blocker but does not produce a freezeable rule. Best clean diagnostic separator is not_fv_entry_timing with 34 loss flips and 2426.000000c hold delta, but that relies on diagnostic labels. Best observable-only clean guard is recross_ge_045 with 4 flips, 4 selected loss rows, and blockers ['diagnostic_loss_rows_only', 'not_frozen_forward', 'needs_full_denominator_replay', 'selected_loss_rows_lt_10']. Next exit work should search for a pre-registered observable state trigger that approximates the diagnostic separation across the full denominator.
0.802. `freeze_or_track_recross_loss_churn_guard_only_after_strict_clock_definition` - The observable loss-churn replay passed the full-denominator harm check but is still not promotion evidence. Best clean replay is recross_ge_045 with 15 selected rows, 5 loss flips, 574.000000c delta, candidate net 1393.000000c versus live baseline 1333.000000c, and 0 harmful / 0 new-loss rows. The blocker is strict evidence: it is a diagnostic replay with fewer than 30 selected decisions. Clock feasibility blockers are ['research_only', 'not_frozen_forward', 'full_denominator_replay_not_shadow_clock', 'selected_decisions_lt_30', 'scorecard_missing_exit_ts_for_exit_clock', 'some_selected_rows_have_no_exit_event']; exit-clock join selected 8 rows; source stability is False with row counts [137, 71, 91, 88, 100]. The materialized threshold frontier best clean point is 0.45 with 8 selected rows and 124.000000c delta; looser thresholds introduce harmful/new-loss rows. The low-edge broad-hold tradeoff also blocks a simple expansion: best clean policy base_exit_hold_raw_edge_ge_7_else_weight_0 has 19 selected rows and no clean >=30 policy. The neighbor autopsy shows the low-edge slice is mixed: 13/1 helpful/harmful, while the clean high-edge survivor has 19 rows. Do not freeze this recross guard; keep it as a sparse mechanism clue.
0.806. `do_not_freeze_simple_dual_lane_exposure_weighting_yet` - The state/exposure sequencing probe confirms the mechanism is real but the simple observable repair is incomplete. Best diagnostic variant sequence_combo_strong2x_shrink50 improves candidate net by 174.500000c to 192.500000c, but still runs -131.500000c behind live on the same markets, has full-loss cushion 1, and blockers ['diagnostic_only_same_window', 'not_frozen_forward', 'state_sequence_not_live_ready', 'still_trails_live_same_window', 'full_loss_cushion_lt_3', 'shrinks_winning_rows', 'does_not_beat_refreshed_live_baseline']. Do not freeze this simple weighting as a candidate; use it as evidence that the repair needs explicit state-transition/side-flip logic or more mature own-freeze rows.
0.8065. `do_not_freeze_side_flip_repair_without_observable_state_trigger` - Side-flip escape is a real current deficit mechanism, but it is not yet an actionable candidate. Candidate side-flip markets are 2 with net 68.000000c; candidate opposite-rescue markets are 2 with net 68.000000c. Across all post-freeze live markets, side flips are 2 of 13 and net 68.000000c. Blockers are ['research_only', 'not_frozen_forward', 'side_flip_trigger_not_observable_from_static_candidate_row', 'opposite_rescue_sample_too_sparse', 'candidate_side_flip_sample_too_sparse']. A deployable repair needs an explicit observable state-transition trigger and its own freeze.
0.805. `treat_dual_lane_same_window_delta_as_live_baseline_blocker` - The dual-lane forced strict precheck is still behind actual live v28 on the same post-freeze markets: -306.000000c candidate-minus-live. The deficit side has 5 rows for -925.000000c, partly offset by 8 surplus rows for 619.000000c. The largest negative bucket is candidate_positive_live_captured_more with 3 row(s) and -529.000000c. Sequence audit tags the largest mechanism as live_larger_terminal_exposure_same_side with 2 row(s) and -347.000000c. This must be treated as a live-baseline blocker until own-freeze rows mature and the candidate beats live on refreshed evidence.
0.807. `collect_exit_suppression_density_before_review` - The refreshed exit promotion queue has zero review-ready rows. Closest is common_clock_strict_forward_v2 with 58 settled rows, 17 suppressions, candidate/delta cushion 6/2, and delta 242.0c. It still needs 13 suppressions and 58.0c of delta cushion, so the next exit work is strict-row collection and density tracking, not a new diagnostic rule.
0.8075. `treat_common_clock_residual_rescue_as_child_watch_only` - The strict residual frontier explains why the common-clock exit guard should not be broadened by low-p_hold alone. In v2, the best broad residual fair_drawdown_positive_low_p adds 642.000000c versus base across 17 residual rows, but has helpful/harmful 15/2. The best clean v2 residual collapse_full_any is 5 rows for 462.000000c, and v3 clean residual collapse_full_any is 4 rows for 286.000000c. These clean collapse-full add-ons are too sparse for promotion, so the next action is strict collection or a separately frozen child watch, not a live exit change.
0.808. `do_not_relax_v3_with_residual_bucket_yet` - The v3 loss-guard residual bucket is tempting but still physically suspect. In strict v3-forward rows, v1-only residual exposure is only 3 row(s) for 36.000000c and 0c harmful delta. Across all diagnostic exit rows, the same residual bucket is 16 row(s), -14.000000c net, and -186.000000c harmful delta. Even full residual relaxation in the strict v3 window has 11 selected decisions, delta cushion 1, and blockers ['suppressed_decisions_lt_30', 'delta_full_loss_cushion_lt_3', 'residual_policy_not_independently_frozen']. Treat v3 hard rejection as the safer default until a separately frozen residual or partial-size watch earns rows.
0.809. `downgrade_observable_reduce_loss_control_until_false_hold_guard_freezes` - Observable reduce-loss-control still explains diagnostic loss churn, but the fresh p_hold>=0.75 probability-reduce denominator is not yet safe. Diagnostic denominator: 18 rows, 171.000000c net, 14/4 helpful/harmful, and -610.000000c harmful delta. Post-observable-birth denominator: 7 rows, -224.000000c net, 4/3 helpful/harmful, and -424.000000c harmful delta. The best post-birth zero-harm split (entry_depth ge 225.99) has only 2 rows, so it is a post-hoc child idea, not evidence to broaden exit suppression.
0.815. `collect_exit_clip_separator_watch_rows` - The fair-drawdown/p_hold clip separator is now frozen as a forward watch. It froze at 2026-05-07T04:04:23.876080+00:00 and currently has 7 post-freeze matched rows and selected 3 row(s), so it needs fresh rows before any exit-stack use. Opportunity audit shows selected helpful/harmful/unknown 1/0/0 with 60.0c known delta, and 1 near-miss row(s) with 0c known delta.
0.817. `treat_exit_clip_replay_as_mechanism_until_forward_rows_arrive` - The full replay of the frozen exit-reduce rows shows the clip separator is not just a loss-subset artifact: diagnostic W/L moves from 73/56 to 104/27, net moves from 721.0c to 1908.0c, and losses fall by 29. Keep it non-deployable because post-watch rows are 36 and diagnostic replay still has 6 suppressed losers.
0.82. `separate_exit_repair_denominator_gap_from_strategy_gap` - The exit-repair gap classifier says 56 of 73 losing rows remain unresolved: 19 have no frozen exit-repair observation (19 predate the first exit-repair freeze) and 37 are matched but unchanged. The observable post-birth loss-control watch has only 8 probability-reduce row and its first would-suppress row is harmful, so new exit work should first separate pre-freeze history from true collapse/value-exit states rather than broadening suppression.
0.823. `collect_matched_unchanged_loss_guard_watch_rows` - The matched-unchanged separator now has a guarded frozen watch, so the next step is strict post-freeze collection, not another diagnostic freeze. It froze at 2026-05-07T09:30:07.471830+00:00 and currently has 5 post-freeze scored row(s), selected 1 row(s), 1/0 helpful/harmful, 6.0c delta, and blockers ['settled_lt_30', 'suppressed_decisions_lt_30', 'full_loss_cushion_lt_3']. Diagnostic context was 20 selected with 19/0 helpful/harmful and 817.0c selected hold delta, but those rows are pre-freeze only. Opportunity audit has 4 post-freeze scored rows, 0 selected rows, 3 near-miss rows, and fail reasons {'abs_d_sigma_above_max': 3, 'eligible_depth_above_max': 3, 'exit_p_hold_below_min': 1, 'missing_exit_cents': 1, 'missing_exit_p_hold': 1}.
0.826. `collect_common_clock_residual_child_rows` - The residual exit70-79 child is now producing strict post-birth evidence, but it is still a sample wait: 20 settled, 4 child suppressions, helpful/harmful 2/2, child delta -202.0c, candidate net 190.0c, and blockers ['settled_lt_30', 'child_suppressed_decisions_lt_30', 'delta_vs_current_not_positive', 'child_delta_vs_parent_not_positive', 'child_loss_control_cost_negative', 'full_loss_cushion_lt_3']. Treat it as a promising clipped-winner residual watch, not an exit change. Path-risk audit matched 1/4 strict child rows, worst adverse vs exit -10.0c, adverse 10/25/50 rows 1/0/0, below-zero marks 1, and blockers ['settled_lt_30', 'child_suppressed_decisions_lt_30', 'full_loss_cushion_lt_3', 'post_exit_mark_below_zero_present', 'missing_post_exit_path_rows']. False-hold autopsy adds blockers ['settled_lt_30', 'child_suppressed_decisions_lt_30', 'delta_vs_current_not_positive', 'child_delta_vs_parent_not_positive', 'child_loss_control_cost_negative', 'full_loss_cushion_lt_3', 'strict_false_holds_present', 'same_market_false_hold_cluster', 'p_hold_75_79_false_hold_risk', 'probability_reduce_false_hold_risk']; harmful rows are 2 rows for -304.0c, markets {'KXBTC15M-26MAY071015-15': 2}, reasons {'mushroom_v28_probability_reduce': 2}, p-hold bands {'75_79': 2}. Guardrail scan best clean strict variant is book_gap_le_neg_0_5pp with 2 child suppressions, helpful/harmful 2/0, child delta 102.0c, candidate net 494.0c, and blockers ['settled_lt_30', 'child_suppressed_decisions_lt_30']. Treat this as a child-repair hypothesis requiring its own freeze, not promotion evidence.
0.827. `collect_residual_child_book_gap_guard_watch_rows` - The book-gap residual child guard has its own freeze now, so only rows after 2026-05-07T15:09:26.289911+00:00 count. Diagnostic v2 context selected 2 child suppressions with helpful/harmful 2/0 and child delta 94.0c, but post-birth strict evidence is 0 settled, 0 child suppressions, helpful/harmful 0/0, child delta 0c, candidate net 0c, blockers ['settled_lt_30', 'child_suppressed_decisions_lt_30', 'net_not_positive', 'delta_vs_current_not_positive', 'child_delta_vs_parent_not_positive', 'full_loss_cushion_lt_3']. Treat it as an empty/immature child-repair watch, not as inherited evidence from the failed base child.
0.824. `use_true_loser_hold_risk_as_exit_suppression_guardrail` - The exit-repair denominator has a real false-hold risk, not just clipped winners. True-loser/FV-entry rows would lose -2158.0c if held across 21 rows, while clipped-winner rows would gain 2855.0c across 43 rows. Avoid broad hold rules around tags ['fv_or_entry_timing_error', 'medium_25_49c', 'exit_cents_lte40', 'thin_touch_depth', 'large_50_99c'] unless a strict post-freeze watch proves the guard avoids FV/entry losers.
0.825. `require_false_hold_guardrails_in_exit_watch_review` - Strict harmful suppressions identify the concrete false-hold states promotion reviews must reject. The strict common-clock windows show 26 harmful suppressions for -3944.0c, with top guardrail tags {'book_disagrees_with_hold_at_rich_exit': 8, 'exit_cents_gte60': 24, 'exit_cents_gte80': 8, 'negative_book_gap': 14, 'p_hold_75_79': 16, 'p_hold_75_85': 24, 'p_hold_79_85': 8, 'positive_book_gap_ge05': 4, 'positive_fair_drawdown': 14, 'probability_reduce': 16, 'rich_exit_80_plus': 8, 'value_over_hold': 8}. Candidate exit watches should show they avoid these states before clipped-winner recovery is trusted.
0.85. `do_not_broaden_collapse_exit_suppression_without_new_evidence` - The refreshed forward collapse-suppression registry says holding registered collapse exits would have hurt, with suppress delta -13.610000000000001$ over 33 registered rows.
1. `keep_collecting_exit_reduce_suppression` - It is the only frozen exit lane currently showing positive forward delta, but it has only 25 suppressed-exit decisions; keep collecting loss-control evidence.
1.08. `isolate_recent_reduce_suppression_harm_before_broadening` - The reduce-suppression aggregate is still positive, but the drift audit shows 5 harmful suppressed rows for -730.0c, with the latest suppression adding 52.0c. Treat loss-control cost as a physical failure mode, not a harmless sample artifact.
1.09. `collect_drift_guarded_reduce_suppression_forward_rows` - The frozen drift-guard watch converted the diagnostic blanket suppressor into two_regime_drift_guard with 12/1 suppressed W/L and 515.0c, but its own post-birth rows are 40 settled with 1 suppressions. Treat it as a clean mechanism watch only.
1.57. `collect_midband_reduce_rescue_forward_rows` - A frozen watch now tests the lower-p_hold probability-reduce clip mechanism. Diagnostic best midband_p60_75_exit50_75_asklt80 has delta 518.0c on 8 suppressions with 8/0 helpful/harmful, but strict post-birth rows are 42 with blockers ['suppressed_decisions_lt_30', 'full_loss_cushion_lt_3']. Treat as watch-only.
2. `watch_book_gap_soft_exit_validator` - Discovery signal was large, but the frozen validator has to earn future rows before it can inform live exits.
2.2. `collect_loss_guarded_book_gap_forward_rows` - This new frozen lane keeps the book-gap upside while requiring a real held-side book advantage before suppressing probability-reduce exits.
2.25. `collect_loss_guarded_book_gap_v2_forward_rows` - The stricter v2 lane gives up some upside but removes the current diagnostic suppressed-loss cost by rejecting deep negative-gap value-over-hold suppressions.
2.255. `collect_loss_guarded_book_gap_v3_extreme_p_forward_rows` - V3 tests the smallest creative relaxation of v2: allow only extreme p_hold>=0.95 value-exit holds while keeping the rich-exit/negative-gap protection that avoided strict-forward harm.
2.27. `track_value_only_book_gap_denominator` - The value-only freeze isolates value-over-hold clipping from probability-reduce state warnings; the opportunity denominator shows whether the zero-row strict scorecard is sample scarcity or rule scarcity.
2.28. `track_value_reduce_depth_composite_denominator` - The value/reduce-depth composite is the cleanest diagnostic exit stack so far, but it has to prove post-freeze suppressible opportunities by mechanism before promotion.
2.29. `collect_observable_reduce_loss_control_forward_rows` - Observable reduce-loss-control variants now have a separate frozen watch; the best diagnostic union removed suppressed losers, but post-birth rows have not produced suppressible probability-reduce opportunities yet.
2.3. `judge_exit_repairs_on_common_clock_window` - The common-clock report is the clean apples-to-apples promotion surface for reduce/book-gap/loss-guard/dual exits; the v1/v2/v3 strict windows have to fill before any live-test decision. The closest strict row is new_exit_mix_common_forward_v2 / loss_guard_value_p85_reduce_p79_gap0 with 58 settled, 17 suppressions, 668.000000c net, and 242.000000c delta; it still needs 13 suppressions and 0.000000c cushion.
2.5. `collect_dual_exit_book_gap_else_reduce_forward_rows` - The mix/match composite is now frozen from its own timestamp; do not rely on the diagnostic +990c union until this lane earns post-freeze rows.
3.5. `prioritize_target_coverage_loss_tags` - The next entry/FV work should explain these repeated losing physical states before adding broader exposure.
3.6. `collect_clean_cluster_penalty_forward_rows` - The continuous cluster-penalty repair is now post-birth positive at target coverage, but it is too reconstructed-heavy and fragile to promote.
3.65. `collect_source_aware_cluster_penalty_forward_rows` - The new source-aware stress almost cleans the diagnostic broad-entry cluster while staying positive, but strict post-birth evidence is still immature and the source label itself is research-only.
3.66. `watch_observable_cluster_stability_proxy_without_promotion` - The observable-only stability proxy translates the source-displacement clue into live-usable features, but diagnostic evidence still misses the source and full-loss cushion gates and strict post-birth evidence is still immature.
3.67. `collect_clean_broad_feature_gate_forward_rows` - The soft clean-broad feature-gate rule was frozen after discovery, so only new post-freeze rows count; it currently has 44 settled strict row(s) and 0 pending unsettled row(s).
3.68. `collect_soft_frontier_exit_stack_forward_rows` - This freezes the broad clean feature-gate entry rule with guarded exits from its own timestamp; it is the correct mix/match watch for target coverage, but has no post-freeze joined exits yet.
3.685. `collect_feature_gate_cheap_tail_shrink_forward_rows` - The broad feature-gate row is positive but source-fragile because cheap tail rows add coverage and depend on a large reconstructed payoff. This new watch freezes continuous notional shrinkage on cheap tails from its own timestamp; post-birth evidence is currently immature.
3.686. `collect_feature_gate_near_promotion_forward_denominator_rows` - The nearest broad feature-gate candidate is post_feature_freeze_entry_raw05_recross60_abs085 with 55 settled, 67.073171% coverage, 445.000000c net, W/L 39/16, and 0.272727 reconstructed share. It needs 7 coverage row(s), 0 clean-source dilution row(s), and 0.000000c of cushion before live testing. The denominator-gap audit says omitted rows are rejected-actionable source rows, so this should be closed by fresh qualifying forward markets, not by relaxing the frozen rule.
3.6865. `do_not_repair_feature_gate_raw05_gap_with_raw03_relaxation` - The current-denominator feature-gate gap says raw03 relaxation is not a real repair. raw05 bridge is cleaner with 47 entries, 65.277778% coverage, 350.000000c net, reconstructed share 0.276596, cushion 3, and live-snapshot gap 983.000000c. raw05 entry is similar but weaker at 47 entries, 65.277778% coverage, 294.000000c, cushion 2. raw03 bridge reaches 75.000000% coverage, but source share 0.370370, cushion 2, and live-snapshot gap 1050.000000c keep it blocked. The mechanism synthesis says raw05 bridge losses are {'entry_or_fv_failure_exit_helped': 3, 'no_exit_observation': 10} with source counts {'approved_entry': 3, 'rejected_actionable': 10}; approved losses were exit-helped, so broad exit suppression is not the missing repair. The raw03-only marginal slice adds 7 rows, all from {'rejected_actionable': 7}, with W/L 2/5 and -83.000000c. The best any-source oracle reaches 75.324675% coverage only by adding {'rejected_actionable': 7}, leaving reconstructed share 0.362069. This closes the simple-relaxation path; wait for clean forward rows or freeze a true observable quality proxy.
3.687. `do_not_promote_core_expansion_mix_yet` - The strict-core plus broad-expansion mix was tested as a physical dual strategy. Best weighted policy approved_expansion_full_reconstructed_quarter has 64 entries and 64 settled, 78.048780% coverage, 386.500000c weighted net, row/exposure source 0.390625/0.165775, and cushion 3. It is useful evidence, but not promotable.
3.688. `do_not_repair_feature_gate_coverage_by_simple_relaxation` - The coverage-repair audit found no observable relaxation that clears coverage, source quality, and full-loss cushion together. The best entry relaxation raw03_recross60_abs85_asknone reaches 75.609756% coverage but has 0.354839 reconstructed share and 469.000000c net; its added rows net 24.000000c. This says the next improvement should wait for clean forward rows or use a real continuous penalty, not a broad threshold relaxation.
3.689. `watch_feature_gate_coverage_size_shrink_source_dilution` - The historical coverage-size-shrink audit is still useful as repair shape, but the current-denominator size proxy blocks promotion. The older shrink row preserves 80.487805% coverage, reaches W/L 54/12, and lifts weighted net to 423.500000c with cushion 4. The remaining blocker is row-source share 0.393939, while exposure-source share is only 0.208333. On the current denominator, best exposure-clean bridge proxy raw05_anchor_plus_raw03_marginal_weight_0.05 reaches 75.000000% coverage, 345.850000c weighted net, cushion 3, and exposure-source share 0.281943, but official row-source share stays 0.370370 and its delta versus the live snapshot is -987.150000c. Zeroing marginal rows restores raw05 source at 0.276596 but coverage drops to 65.277778%. Exit attribution shows failure classes {'entry_or_fv_failure_exit_helped': 3, 'exit_preserved_profit': 1, 'no_exit_observation': 8}. Runway says it needs 9 clean selected rows; first viable count-gate scenario averages Nonec across None future clean rows. It is still 886.500000c versus its stored live-baseline snapshot, so exposure sizing is risk context, not an official source or live-gap repair.
3.69. `collect_soft_frontier_size_shrink_forward_rows` - A frozen size/risk overlay now tests whether broad soft-frontier entries are better handled by continuous notional shrinkage in near-boundary and mid-cheap states, instead of another hard cutoff. Diagnostic rows are strong, but post-shrink-freeze evidence is still empty.
3.695. `collect_midprice_boundary_shrink_forward_rows` - The quarter-size mid-price boundary overlay is the strongest broad-entry mix so far: it preserves 80%+ diagnostic coverage while shrinking the repeated near-boundary loss pocket. The source-stress audit shows weighted exposure can be cleaner than row-count source share, but official promotion still needs strict post-birth rows and the row-source gate.
3.697. `collect_midprice_boundary_exit_stack_forward_rows` - The new weighted entry+exit stack says the top broad diagnostic mix can beat live on matched book-gap exit rows, but the stack is newly frozen and strict combo overlap is still essentially empty. Watch overlap density before treating the entry and exit wins as additive; the runway currently needs 7 joined rows and 0.0c of weighted cushion.
3.696. `collect_midprice_boundary_dual_exit_stack_forward_rows` - The creative book-gap/clip union is now the strongest broad diagnostic stack: diagnostic_bridge_quarter_midprice_boundary_book_gap_or_clip has weighted net 1388.0c, delta 312.5c, joined rows 57, and suppressed losers 1. It is watch-only because post-stack rows are 7 and the diagnostic suppressed-loser warning is unresolved.
3.6965. `collect_midprice_boundary_dual_exit_guard_forward_rows` - The no-boundary-suppress guard repairs the new union stack's diagnostic loss-control flaw: diagnostic_bridge_quarter_midprice_boundary_or_reduce_p_hold80 has weighted net 1418.0c, delta 342.5c, and suppressed losers 0. It remains watch-only because all rows before the guard freeze are diagnostic and post-stack rows are empty.
3.699. `do_not_promote_approved_entry_state_valves_without_full_surface_repair` - Frozen approved-entry-only state valves are positive forward signals on actual v28-approved rows, with strongest policy skip_reentry_gap15_or_gap30 at 110 settled, 745.0c gross, and 258.0c versus approved-entry control. They are not promotion evidence yet because the bridge marks them as approved-entry-surface-only, absent from candidate-vs-live, not live-readiness evaluated, and below the refreshed live baseline on a naive cents comparison. The adapter result confirms this is a mechanism lead, not a live-test candidate. Full-surface replay now says best broad adapter is danger_zone_entry_valve / entry_surface with -349.0c net, 65.0c delta vs base, reconstructed share 0.9425287356321839, and blockers ['coverage_too_low', 'net_not_positive', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3', 'delta_full_loss_cushion_lt_3', 'does_not_beat_refreshed_live_baseline', 'adapter_replay_not_independently_frozen_candidate', 'live_readiness_not_evaluated']. High-gap skip forensics found 5 unique skipped rows, W/L 1/4, net -65.0c, and all skipped rows were rejected-actionable; the +141c skipped winner argues for a soft confidence penalty rather than a hard veto.
3.701. `do_not_shrink_feature_gate_on_high_raw_book_gap_alone` - The high-gap valve forensics do not transfer cleanly to feature-gate rows. Best diagnostic policy is no_shrink_control on diagnostic_entry_raw03_recross70_abs075 with delta 0.0c versus control and weighted net 726.0c. In the strict post-feature lanes the high-gap row is a +56c approved-entry winner, so shrinking raw/book gap alone cuts right-tail profit and does not repair coverage, source share, cushion, or live-baseline blockers.
3.75. `separate_directional_failure_from_price_friction` - The broad surface is losing mainly through direction-wrong rows; price/edge buckets identify where FV confidence is physically deceptive.

## Exit Policy Loss-Count Churn

| lane | rows | current W/L | candidate W/L | loss-count delta | net delta | suppressed | new losses | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| observable_reduce_loss_control_diagnostic | 132 | 76/56 | 92/40 | 16 | 523.000000 | 21 | None | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| exit_reduce_suppression | 132 | 73/56 | 91/40 | 16 | 337.000000 | 25 | 1 | suppressed_loss_control_cost_negative |
| exit_value_reduce_depth_composite_diagnostic_from_exit_freezes | 132 | 76/56 | 90/42 | 14 | 483.000000 | 23 | None | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| exit_reduce_depth_gate_diagnostic_from_reduce_freeze | 132 | 76/56 | 90/42 | 14 | 413.000000 | 19 | None | suppressed_losers_present, suppressed_loss_control_cost_negative |
| exit_value_reduce_depth_composite_diagnostic_from_exit_freezes | 132 | 76/56 | 89/43 | 13 | 431.000000 | 22 | None | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| exit_reduce_depth_gate_diagnostic_from_reduce_freeze | 132 | 76/56 | 89/43 | 13 | 361.000000 | 18 | None | suppressed_losers_present, suppressed_loss_control_cost_negative |
| exit_value_reduce_depth_composite_diagnostic_from_exit_freezes | 132 | 76/56 | 88/44 | 12 | 509.000000 | 61 | None | suppressed_losers_present, suppressed_loss_control_cost_negative |
| observable_reduce_loss_control_diagnostic | 132 | 76/56 | 88/44 | 12 | 389.000000 | 15 | None | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |

## Exit Repair Gap Classifier

- Unresolved losses: `56/73` (76.712329%)
- No frozen exit-repair observation: `19`
- No-observation pre/post first exit-repair freeze: `19/0`
- Matched but unchanged: `37`
- Repair flips/worsens losses: `15/2`
- Observable post-birth probability-reduce/would-suppress rows: `8/7`
- Observable post-birth worst suppress delta: `-304.000000c`

## Exit Clip Separator Diagnostic

- Matched unchanged rows: `37`
- Known hold helpful/harmful/unknown: `27/8/0`
- Best rule: `fair_drawdown_lte_5.0 AND raw_edge_ge_6.0`
- Best rule helpful/harmful/unknown: `10/0/0`
- Best rule known hold delta: `732.000000c`

## Frozen Exit Clip Separator Watch

- Freeze UTC: `2026-05-07T04:04:23.876080+00:00`
- Post-freeze matched unchanged rows: `7`
- Selected rows: `3`
- Known helpful/harmful/unknown: `2/1/0`
- Known hold delta: `-20.000000c`
- Blockers: `post_freeze_rows_lt_30, harmful_hold_rows_present, known_hold_delta_lt_300c`

## Exit Clip Separator Opportunity

- Post-freeze denominator rows: `2`
- Selected rows: `1`
- Selected helpful/harmful/unknown: `1/0/0`
- Selected known hold delta: `60.000000c`
- Near-miss rows: `1`
- Near-miss helpful/harmful/unknown: `0/0/1`
- Near-miss known hold delta: `0c`
- Fail reasons: `{'fair_drawdown_above_ceiling': 1, 'p_hold_below_floor': 1}`
- Blockers: `post_rows_lt_30, selected_rows_lt_30, selected_delta_lt_300c`

## Exit Clip Separator Replay

| label | rows | current W/L | candidate W/L | current net | candidate net | delta | suppressed | loss reduction | suppressed losers | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_from_exit_reduce_freeze` | 132 | 73/56 | 104/27 | 721.000000c | 1908.000000c | 1187.000000c | 40 | 29 | 6 | 19 | diagnostic_replay_not_clip_watch_forward, suppressed_losers_present |
| `post_clip_watch_freeze` | 36 | 23/12 | 29/6 | 478.000000c | 598.000000c | 120.000000c | 10 | 6 | 2 | 5 | suppressed_decisions_lt_30, suppressed_losers_present, post_clip_watch_sample_pending |

| unresolved failure class | rows | actual loss c | hold helpful | hold harmful | hold unknown |
|---|---:|---:|---:|---:|---:|
| exit_policy_cost | 34 | -772.000000 | 34 | 0 | 0 |
| exited_unsettled | 2 | -48.000000 | 0 | 0 | 2 |
| fv_or_entry_timing_error | 20 | -766.000000 | 0 | 18 | 0 |

## Frozen Matched-Unchanged Loss Guard Watch

- Freeze UTC: `2026-05-07T09:30:07.471830+00:00`
- Diagnostic selected/helpful/harmful: `20/19/0`
- Diagnostic selected hold delta: `817.000000c`
- Post-freeze scored rows: `5`
- Post-freeze selected rows: `1`
- Post-freeze helpful/harmful/flat: `1/0/0`
- Post-freeze delta/cushion: `6.000000c / 1`
- Blockers: `settled_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3`
- Opportunity post-freeze scored/selected/near-miss: `4/0/3`
- Opportunity near-miss hold delta: `48.000000c`
- Opportunity fail reasons: `{'abs_d_sigma_above_max': 3, 'eligible_depth_above_max': 3, 'exit_p_hold_below_min': 1, 'missing_exit_cents': 1, 'missing_exit_p_hold': 1}`

## Exit True-Loser Hold Risk Guardrail

- True-loser hold-risk rows: `21`
- True-loser hold delta: `-2158.000000c`
- Clipped-winner rows: `43`
- Clipped-winner hold delta: `2855.000000c`

| tag | true rows | true hold delta | clipped rows | clipped hold delta | read |
|---|---:|---:|---:|---:|---|
| `fv_or_entry_timing_error` | 21 | -2158.000000c | 0 | 0c | `avoid_broad_hold` |
| `medium_25_49c` | 8 | -902.000000c | 7 | 542.000000c | `avoid_broad_hold` |
| `exit_cents_lte40` | 4 | -260.000000c | 2 | 328.000000c | `avoid_broad_hold` |
| `thin_touch_depth` | 3 | -386.000000c | 3 | 192.000000c | `avoid_broad_hold` |
| `large_50_99c` | 3 | -234.000000c | 3 | 422.000000c | `avoid_broad_hold` |
| `ask_lt55` | 3 | -112.000000c | 1 | 176.000000c | `avoid_broad_hold` |

## Exit False-Hold Guardrail Bridge

- Strict harmful suppressions: `26`
- Strict net harm: `-3944.000000c`
- Top guardrail tags: `{'book_disagrees_with_hold_at_rich_exit': 8, 'exit_cents_gte60': 24, 'exit_cents_gte80': 8, 'negative_book_gap': 14, 'p_hold_75_79': 16, 'p_hold_75_85': 24, 'p_hold_79_85': 8, 'positive_book_gap_ge05': 4, 'positive_fair_drawdown': 14, 'probability_reduce': 16, 'rich_exit_80_plus': 8, 'value_over_hold': 8}`

| policy | harmful rows | net harm | top tags |
|---|---:|---:|---|
| `book_gap_soft_gap15_or_p_hold75` | 10 | -1548.000000c | `{'book_disagrees_with_hold_at_rich_exit': 4, 'exit_cents_gte60': 10, 'exit_cents_gte80': 4, 'negative_book_gap': 6, 'p_hold_75_79': 6, 'p_hold_75_85': 10, 'p_hold_79_85': 4, 'positive_fair_drawdown': 6, 'probability_reduce': 6, 'rich_exit_80_plus': 4}` |
| `dual_book_gap_else_reduce` | 8 | -1308.000000c | `{'book_disagrees_with_hold_at_rich_exit': 4, 'exit_cents_gte60': 8, 'exit_cents_gte80': 4, 'negative_book_gap': 6, 'p_hold_75_79': 4, 'p_hold_75_85': 8, 'p_hold_79_85': 4, 'positive_fair_drawdown': 4, 'rich_exit_80_plus': 4, 'value_over_hold': 4}` |
| `reduce_p_hold_ge_075` | 6 | -848.000000c | `{'exit_cents_gte60': 6, 'negative_book_gap': 2, 'p_hold_75_79': 6, 'p_hold_75_85': 6, 'positive_book_gap_ge05': 2, 'positive_fair_drawdown': 4, 'probability_reduce': 6}` |

## Exit Strict Failure Drilldown

- Strict harmful suppressions: `26`
- Strict net harm: `-3944.000000c`

| window | rows | harmful suppressions | net harm | avoided by v1/v2 | top tags |
|---|---:|---:|---:|---:|---|
| new_exit_mix_common_forward_v1 | 59 | 13 | -1972.000000 | 13/13 | book_disagrees_with_hold_at_rich_exit:4, negative_book_gap:7, p_hold_75_79:9, p_hold_79_85:4, positive_fair_drawdown:8 |
| new_exit_mix_common_forward_v2 | 58 | 13 | -1972.000000 | 13/13 | book_disagrees_with_hold_at_rich_exit:4, negative_book_gap:7, p_hold_75_79:9, p_hold_79_85:4, positive_fair_drawdown:8 |

## Exit Policy Watch Dashboard

- Status counts: `{'blocked_loss_control_cost': 9, 'blocked_net_not_positive': 2, 'forward_positive_under_review': 10, 'not_positive_or_under_sample': 1, 'positive_but_under_sample': 4, 'waiting_no_post_freeze_rows': 1, 'waiting_no_suppressed_exits': 2}`

| lane | status | settled | suppressed | current c | candidate c | delta c | loss cost c | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---|
| book_gap_suppression | blocked_loss_control_cost | 120 | 59 | 727.000000 | 962.000000 | 235.000000 | -1080.000000 | suppressed_loss_control_cost_negative |
| book_gap_loss_guard | forward_positive_under_review | 59 | 17 | 340.000000 | 582.000000 | 242.000000 | 0.000000 | suppressed_decisions_lt_30 |
| book_gap_loss_guard_v2 | forward_positive_under_review | 58 | 5 | 426.000000 | 578.000000 | 152.000000 | 0.000000 | suppressed_decisions_lt_30 |
| book_gap_loss_guard_v3 | forward_positive_under_review | 46 | 9 | 478.000000 | 644.000000 | 166.000000 | 0.000000 | suppressed_decisions_lt_30 |
| book_gap_value_only | blocked_loss_control_cost | 54 | 18 | 338.000000 | 240.000000 | -98.000000 | -350.000000 | delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| value_reduce_depth_composite | blocked_loss_control_cost | 54 | 11 | 338.000000 | 222.000000 | -116.000000 | -424.000000 | delta_not_positive, suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| reduce_depth_gate | forward_positive_under_review | 60 | 2 | 388.000000 | 482.000000 | 94.000000 | 0.000000 | full_loss_cushion_lt_3 |
| reduce_loss_control_refinement | forward_positive_under_review | 60 | 2 | 388.000000 | 482.000000 | 94.000000 | 0.000000 | full_loss_cushion_lt_3 |
| reduce_observable_loss_control | blocked_loss_control_cost | 54 | 2 | 338.000000 | 280.000000 | -58.000000 | -120.000000 | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| reduce_side_geometry | blocked_loss_control_cost | 70 | 3 | 492.000000 | 448.000000 | -44.000000 | -158.000000 | delta_not_positive, suppressed_losers_present |
| reduce_geometry_relaxed | blocked_loss_control_cost | 43 | 4 | 502.000000 | 338.000000 | -164.000000 | -278.000000 | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, full_loss_cushion_lt_3 |
| exit_reduce_drift_guard | forward_positive_under_review | 40 | 1 | 510.000000 | 556.000000 | 46.000000 | 0.000000 | suppressed_decisions_lt_30 |
| midband_reduce_rescue | forward_positive_under_review | 42 | 1 | 534.000000 | 590.000000 | 56.000000 | 0.000000 | suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| exit_clip_separator_watch | blocked_net_not_positive | 7 | 3 | 0.000000 | -20.000000 | -20.000000 | 0.000000 | post_freeze_rows_lt_30, harmful_hold_rows_present, known_hold_delta_lt_300c |
| matched_unchanged_loss_guard_watch | waiting_no_suppressed_exits | 5 | 0 | 114.000000 | 120.000000 | 6.000000 | 0.000000 | settled_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| exit_shallow_drawdown | positive_but_under_sample | 1 | 1 | 18.000000 | 36.000000 | 18.000000 | 0.000000 | settled_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| exit_shallow_duration_lte52 | waiting_no_suppressed_exits | 1 | 0 | 18.000000 | 18.000000 | 0.000000 | 0.000000 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| dual_exit_book_gap_else_reduce | blocked_loss_control_cost | 59 | 30 | 340.000000 | 128.000000 | -212.000000 | -774.000000 | delta_not_positive, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3, degenerates_to_book_gap_on_shared_window |
| common_clock_strict_forward_v1 | forward_positive_under_review | 59 | 17 | 340.000000 | 582.000000 | 242.000000 | 0.000000 | suppressed_decisions_lt_30 |
| common_clock_strict_forward_v2 | forward_positive_under_review | 58 | 17 | 426.000000 | 668.000000 | 242.000000 | 0.000000 | suppressed_decisions_lt_30 |
| common_clock_strict_forward_v3 | forward_positive_under_review | 46 | 13 | 478.000000 | 692.000000 | 214.000000 | 0.000000 | suppressed_decisions_lt_30 |
| common_clock_residual_child_exit70_79 | blocked_loss_control_cost | 20 | 4 | 338.000000 | 190.000000 | -148.000000 | -304.000000 | settled_lt_30, child_suppressed_decisions_lt_30, delta_vs_current_not_positive, child_delta_vs_parent_not_positive, child_loss_control_cost_negative, full_loss_cushion_lt_3 |
| common_clock_residual_child_book_gap_guard | waiting_no_post_freeze_rows | 0 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | settled_lt_30, child_suppressed_decisions_lt_30, net_not_positive, delta_vs_current_not_positive, child_delta_vs_parent_not_positive, full_loss_cushion_lt_3 |
| soft_frontier_midprice_delayed_recheck_exit | positive_but_under_sample | 3 | 3 | 54.000000 | 120.000000 | 66.000000 | 0.000000 | joined_rows_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| soft_frontier_midprice_delayed_recheck_rescue | positive_but_under_sample | 3 | 3 | 54.000000 | 120.000000 | 66.000000 | 0.000000 | joined_rows_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| feature_gate_value_exit | positive_but_under_sample | 14 | 5 | 240.000000 | 327.600000 | 87.600000 | 0.000000 | settled_lt_30, selected_side_live_overlap_only, hold_to_settlement_assumption, not_live_bot_logic |
| feature_gate_exit_bid_suppression | blocked_loss_control_cost | 13 | 11 | -56.000000 | -302.400000 | -246.400000 | -1102.000000 | settled_lt_30, suppressed_decisions_lt_30, net_not_positive, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| feature_gate_exit_bid_delayed_recheck | blocked_net_not_positive | 11 | 8 | 0.000000 | -360.400000 | -270.400000 | 0.000000 | settled_lt_30, suppressed_decisions_lt_30, net_not_positive, delta_not_positive, suppressed_losers_present, full_loss_cushion_lt_3 |
| value_exit_feature_side_guard | not_positive_or_under_sample | 33 | 9 | 450.000000 | 388.000000 | -62.000000 | 0.000000 | exit_overlap_only, not_live_bot_logic |

## Blocker Families

| family | count |
|---|---:|
| other | 2450 |
| profitability | 241 |
| sample_size | 201 |
| coverage_low | 115 |
| risk_stop | 88 |
| calibration | 84 |
| coverage_high | 55 |
| live_evidence_quality | 50 |

## Target-Coverage Loss Tags

| tag | settled | W/L | net c | avg c |
|---|---:|---:|---:|---:|
| early_stc_ge_720 | 82 | 44/38 | -856.000000 | -10.439024 |
| thin_edge_lt_3pp | 33 | 18/15 | -808.000000 | -24.484848 |
| reason_keep_p_ge_60 | 76 | 47/29 | -715.000000 | -9.407895 |
| all | 112 | 64/48 | -626.000000 | -5.589286 |
| high_recross_ge_075 | 54 | 27/27 | -625.000000 | -11.574074 |
| extreme_recross_ge_090 | 25 | 11/14 | -496.000000 | -19.840000 |
| cheap_ask_lt_55 | 47 | 19/28 | -459.000000 | -9.765957 |
| weak_raw_p_lt_58 | 26 | 9/17 | -445.000000 | -17.115385 |

## Target-Coverage Price Friction

- Entries/settled/coverage: `112/112/73.684211`
- Net cents: `-626.000000`

| tag | settled | W/L | win rate | net c | avg ask | avg edge |
|---|---:|---:|---:|---:|---:|---:|
| mid_high_recross | 47 | 21/26 | 0.446809 | -950.000000 | 0.528511 | 0.087695 |
| edge_lt_2pp | 22 | 10/12 | 0.454545 | -883.000000 | 0.635909 | 0.009213 |
| early_no_boundary_decay | 30 | 12/18 | 0.400000 | -875.000000 | 0.526333 | 0.085319 |
| early_ge_780 | 72 | 39/33 | 0.541667 | -794.000000 | 0.577639 | 0.059570 |
| ask_55_65 | 31 | 17/14 | 0.548387 | -434.000000 | 0.598387 | 0.034386 |
| ask_lt_50 | 33 | 12/21 | 0.363636 | -357.000000 | 0.398788 | 0.161557 |
| side_no | 52 | 30/22 | 0.576923 | -323.000000 | 0.582692 | 0.085011 |
| side_yes | 60 | 34/26 | 0.566667 | -303.000000 | 0.564333 | 0.077348 |

## Target Cluster-Penalty Runway

- Post-birth settled/coverage/net: `33/76.744186/-96.000000c`
- Reconstructed share: `0.909091`
- Rows/clean rows/cushion needed: `0/53/396.000000c`
- Source feasible now: `True` with `39/50` approved/required markets and minimum reconstructed share `0.220000`
- Source displacement net: selected rejected `-101.000000c`; omitted approved `94.000000c`
- Blockers: `net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3`

## Source-Aware Cluster-Penalty Watch

- Freeze UTC: `2026-05-07T00:01:16.649704+00:00`
- Diagnostic cleanest: `diagnostic_target_window_medium_src_penalty100` settled/coverage/net/recon `97/75.193798/75.000000c/0.484536`
- Strict post-birth cleanest: `post_source_aware_birth_medium_src_penalty100` settled/coverage/net/recon `25/75.757576/-175.000000c/0.760000`
- Blockers: `source_penalty_research_only_not_live_feature, settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3`

## Observable Stability Cluster-Penalty Proxy

- Freeze UTC: `2026-05-07T00:06:52.057182+00:00`
- Diagnostic best: `diagnostic_target_window_medium_paid_stable` settled/coverage/net/recon `97/75.193798/-137.000000c/0.659794`
- Diagnostic rows/clean/cushion needed: `0/86/300.000000c`
- Strict post-birth best: `post_observable_proxy_birth_heavy_far_calm` settled/coverage/net/recon `25/75.757576/-350.000000c/0.800000`
- Strict post-birth rows/clean/cushion needed: `5/33/300.000000c`
- Blockers: `settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3`

## Clean-Broad Feature-Gate Frontier Watch

- Freeze UTC: `2026-05-07T00:59:58.526374+00:00`
- Rule: `raw03_recross50_abs50_ask35`
- Diagnostic parent: `None/None/Nonec/recon None`
- Strict post-freeze: `44/83.018868/-76.000000c/recon 0.431818`
- Strict pending unsettled rows: `0`
- Blockers: `net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3`

## Near-Promotion Feature-Gate Watch

- Best candidate: `post_feature_freeze_entry_raw05_recross60_abs085`
- Settled/pending/pending approved: `55/0/0`
- W/L, coverage, net: `39/16` / `67.073171%` / `445.000000c`
- Reconstructed share/cushion: `0.272727` / `4`
- Rows/cushion needed: coverage `7`, clean `0`, settled `0`, cushion `0.000000c`, avg future `0.000000c/row`
- Missing gates: `coverage+7.9pp`
- Loss source counts: `{'approved_entry': 4, 'rejected_actionable': 12}`
- Failure classes: `{'entry_or_fv_failure_exit_helped': 3, 'exit_preserved_profit': 1, 'no_exit_observation': 12}`
- Denominator gap: omitted reasons `{'abs_d_below_min': 20, 'recross_above_max': 6}`, omitted sources `{'rejected_actionable': 20}`, counterfactual source gate `False`

## Feature-Gate raw05 Coverage Gap

- raw05 entry: `51` entries, `49` settled, `67.105263%` coverage, `355.000000c`, recon `0.274510`
- raw03 entry: `58` entries, `56` settled, `76.315789%` coverage, `288.000000c`, recon `0.362069`
- raw03-only entry slice: `7` rows, sources `{'rejected_actionable': 7}`, W/L `2/5`, net `-83.000000c`
- raw05 bridge: `51` entries, `46` settled, `66.233766%` coverage, `293.000000c`, recon `0.274510`
- raw03 bridge: `58` entries, `52` settled, `75.324675%` coverage, `294.000000c`, recon `0.362069`
- raw03-only bridge slice: `7` rows, sources `{'rejected_actionable': 7}`, W/L `2/4`, net `-15.000000c`
- raw05 omitted entry rows: sources `{'rejected_actionable': 26}`, fail reasons `{'abs_d_below_min': 26, 'recross_above_max': 9}`, best-any-source oracle blockers `reconstructed_share_gt_35pct`
- raw05 omitted bridge rows: sources `{'rejected_actionable': 26}`, fail reasons `{'abs_d_below_min': 26, 'recross_above_max': 8}`, best-any-source oracle blockers `reconstructed_share_gt_35pct`

## Feature-Gate Core/Expansion Mix

- Core: `post_feature_freeze_bridge_raw05_recross60_abs085_ask65`
- Broad parent: `post_feature_freeze_bridge_raw03_recross70_abs075`
- Any live-ready mix: `False`
- Best mix: `approved_expansion_full_reconstructed_quarter` settled/W-L/coverage/net `64 entries, 64 settled/42-22/78.048780%/386.500000c`
- Row/exposure source: `0.390625/0.165775`
- Cushion/blockers: `3` / `row_source_share_gt_35pct`

## Feature-Gate Coverage Repair

- `post_feature_freeze_entry` anchor `raw05_recross60_abs85_asknone`: `55/82` entries, W/L `39/16`, net `445.000000c`, recon `0.272727`
- nearest relaxation `raw03_recross60_abs85_asknone`: `62/82` entries, W/L `43/19`, coverage `75.609756%`, net `469.000000c`, recon `0.354839`, added net `24.000000c`, blockers `reconstructed_share_gt_35pct`
- `post_feature_freeze_bridge` anchor `raw05_recross60_abs85_asknone`: `55/82` entries, W/L `39/16`, net `445.000000c`, recon `0.272727`
- nearest relaxation `raw03_recross60_abs85_asknone`: `62/82` entries, W/L `43/19`, coverage `75.609756%`, net `469.000000c`, recon `0.354839`, added net `24.000000c`, blockers `reconstructed_share_gt_35pct`

## Feature-Gate Coverage Size Shrink

- `post_feature_freeze_entry` best `repair_eighth`: `66/82` entries, W/L `54/12`, coverage `80.487805%`, weighted net `423.500000c`, row/exposure recon `0.393939/0.208333`, cushion `4`, blockers `row_reconstructed_share_gt_35pct`, exit classes `{'entry_or_fv_failure_exit_helped': 3, 'exit_preserved_profit': 1, 'no_exit_observation': 8}`, runway clean rows `9`, delta vs live `886.500000c`, first viable `{}`
- `post_feature_freeze_bridge` best `repair_eighth`: `66/82` entries, W/L `54/12`, coverage `80.487805%`, weighted net `423.500000c`, row/exposure recon `0.393939/0.208333`, cushion `4`, blockers `row_reconstructed_share_gt_35pct`, exit classes `{'entry_or_fv_failure_exit_helped': 3, 'exit_preserved_profit': 1, 'no_exit_observation': 8}`, runway clean rows `9`, delta vs live `886.500000c`, first viable `{}`

## Best Current Candidates By Triage Score

| gate | policy | entries | settled | coverage | net c | brier | live ready | blockers |
|---|---|---:|---:|---:|---:|---:|---|---|
| boundary_clock_fv_entry_bridge | boundary_clock_adjusted_edge_floor_0p02_repair_lowest_recross | 90 | 90 | 75.630252 | 229.000000 | None | False | control_risk_stop_active, source_stress:reconstructed_share_gt_35pct, source_stress:full_loss_cushion_lt_3 |
| boundary_clock_repair_entry | skip_boundary_clock_composite_repair_lowest_recross | 91 | 91 | 75.206612 | -151.000000 | None | False | entry:net_not_positive, control_risk_stop_active, source_stress:net_not_positive, source_stress:reconstructed_share_gt_35pct, source_stress:full_loss_cushion_lt_3 |
| composite_false_conviction_repair_entry | skip_composite_false_conviction_repair_highest_raw_p | 83 | 83 | 75.454545 | -84.000000 | None | False | net_not_positive, control_risk_stop_active |
| early_boundary_opposite_wait_repair | early_boundary_wait480_p50_opposite_side_delay480 | 80 | 80 | 75.471698 | 98.000000 | None | False | control_risk_stop_active |
| early_boundary_wait_repair | early_boundary_wait480_p50_any_side | 80 | 80 | 75.471698 | 82.000000 | None | False | control_risk_stop_active |
| early_no_boundary_decay_repair_entry | skip_early_no_boundary_decay_repair_calm_geometry | 85 | 85 | 75.221239 | 27.000000 | None | False | control_risk_stop_active |
| false_conviction_approved_repair | skip_false_conviction_repair_approved_heavy | 70 | 70 | 75.268817 | -226.000000 | None | False | net_not_positive, reconstructed_share_gt_35pct, control_risk_stop_active |
| goldilocks_edge_repair_entry | skip_false_edge_phase_repair_goldilocks | 49 | 49 | 75.384615 | -159.000000 | None | False | net_not_positive, control_risk_stop_active |
| high_raw_p_repair_entry | skip_paid_or_weak_boundary_repair_highest_raw_p | 89 | 89 | 75.423729 | -274.000000 | None | False | net_not_positive, control_risk_stop_active |
| low_recross_repair_entry | skip_paid_or_weak_boundary_repair_lowest_recross | 92 | 92 | 75.409836 | -217.000000 | None | False | net_not_positive, control_risk_stop_active |
| mid_edge_boundary_deception_repair_entry | skip_mid_edge_boundary_deception_repair_stable_geometry | 84 | 84 | 75.000000 | -431.000000 | None | False | net_not_positive, control_risk_stop_active |
| p50_book_edge_entry | p50_book_plus_05_edge_nonnegative | 104 | 104 | 88.135593 | 660.000000 | None | False | simulated_share_gt_35pct, control_risk_stop_active |

## Exit Lanes

| lane | candidate | settled | delta c | suppressed | winner recovery | loss cost | blockers |
|---|---|---:|---:|---:|---:|---:|---|
| reduce_suppression | suppress_reduce_p_hold_ge_075 | 132 | 337.000000 | 25 | 1067.000000 | -730.000000 | suppressed_loss_control_cost_negative |
| book_gap_suppression | suppress_soft_gap15_or_p_hold75 | 120 | 235.000000 | 59 | 1315.000000 | -1080.000000 | suppressed_loss_control_cost_negative |
| book_gap_loss_guard | book_gap_loss_guard_value_p85_reduce_p79_gap0 | 59 | 242.000000 | 17 | 242.000000 | 0 | suppressed_decisions_lt_30 |
| book_gap_loss_guard_v2 | book_gap_loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0 | 58 | 152.000000 | 5 | 152.000000 | 0 | suppressed_decisions_lt_30 |
| book_gap_loss_guard_v3 | book_gap_loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0 | 46 | 166.000000 | 9 | 166.000000 | 0 | suppressed_decisions_lt_30 |
| book_gap_value_only | value_only_gap15_or_p75 | 54 | -98.000000 | 18 | 252.000000 | -350.000000 | delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| exit_value_reduce_depth | value_v2_reduce_depth384 | 54 | -116.000000 | 11 | 308.000000 | -424.000000 | delta_not_positive, suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| exit_reduce_observable_loss_control | post_observable_birth_reduce_suppress_p75_exit_cents_lte_72 | 54 | -58.000000 | 2 | 62.000000 | -120.000000 | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| dual_exit_book_gap_else_reduce | dual_exit_book_gap_else_reduce | 59 | -212.000000 | 30 | 562.000000 | -774.000000 | delta_not_positive, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3, degenerates_to_book_gap_on_shared_window |

## Exit Reduce Runway

- Rows needed for 30: `0`
- Current delta: `337.000000c`
- Suppressed exits: `25`
- Invalidators now: `suppressed_loss_control_cost_negative, robustness_shadow_interest_false`

## Exit Reduce Suppression Drift

- Suppressed exits/net delta: `25/337.000000c`
- Helpful/harmful delta: `1067.000000c/-730.000000c`
- Before latest suppression: `285.000000c`
- Latest suppression: `KXBTC15M-26MAY071315-15` `52.000000c` tags `helpful_winner_recovery, p_hold_075_079, moderate_fair_drawdown, positive_delta`

## Exit Reduce Drift-Guard Watch

- Freeze UTC: `2026-05-07T02:30:19.536047+00:00`
- Best diagnostic: `two_regime_drift_guard` suppressed W/L `12/1` delta `515.000000c`
- Best strict post-birth: `high_p_favorable_fv` settled/suppressed/delta `40/1/46.000000c`
- Blockers: `suppressed_decisions_lt_30`

## Exit Reduce Loss-Control Actionability

- Best overall separator: `best_post_exit_hold_mark_cents ge 44.0` (hindsight-only)
- Best observable separator: `entry_seconds_to_close le 536.526`
- Observable selected W/L and delta: `11/0 / 583.000000c`
- Existing frozen watch: `v28_frozen_exit_reduce_observable_loss_control_watch_latest.json`

## Exit Reduce Observable Loss-Control Opportunity

- Freeze UTC: `2026-05-07T00:08:36.297681+00:00`
- First rule rows/reduce/p-hold/would-suppress: `54/10/9/6`
- First rule delta if suppressed: `-110.000000c`
- First rule fail reasons: `{'entry_seconds_to_close_above_gate': 3, 'not_probability_reduce': 44, 'p_hold_below_gate': 1}`

## Exit Reduce Observable False-Hold Autopsy

- Reduce/observable freeze UTC: `2026-05-06T06:33:56.987999+00:00` / `2026-05-07T00:08:36.297681+00:00`
- Diagnostic p-hold reduce denominator rows/net/helpful-harmful/harmful: `18/171.000000c/14-4/-610.000000c`
- Post-birth p-hold reduce denominator rows/net/helpful-harmful/harmful: `7/-224.000000c/4-3/-424.000000c`
- Best post-birth zero-harm split: `entry_depth ge 225.99` rows/net `2/110.000000c`

## Exit Midband Reduce Rescue Watch

- Freeze UTC: `2026-05-07T02:01:12.356709+00:00`
- Diagnostic best: `midband_p60_75_exit50_75_asklt80` suppressed/delta/helpful-harmful `8/518.000000c/8-0`
- Strict post-birth rows/suppressed/delta: `42/1/56.000000c`
- Blockers: `suppressed_decisions_lt_30, full_loss_cushion_lt_3`

## Exit Reduce Geometry Opportunity

- Probability-reduce/base/geometry rows: `11/10/3`
- Rejected base candidates/delta: `7/-36.000000c`
- Blockers: `geometry_suppressed_decisions_lt_30, geometry_delta_not_positive`

## Exit Reduce Relaxed Geometry Watch

- Freeze UTC: `2026-05-07T01:18:56.563250+00:00`
- Diagnostic best: `side_geometry_suppress_reduce_p_hold_ge_075` delta/suppressed W-L `625.000000c/14/1`
- Strict settled/suppressed/delta: `43/4/-164.000000c`
- Blockers: `suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, full_loss_cushion_lt_3`

## Exit Book-Gap Value-Only Opportunity

- Rows/value exits/would suppress: `54/30/18`
- Suppressed W/L and delta: `16/2 / -98.000000c`
- Fail reasons: `{'collapse_kept_by_value_only_rule': 5, 'not_value_over_hold_exit': 9, 'probability_reduce_kept_by_value_only_rule': 10, 'value_gap_below_floor': 12, 'value_p_hold_below_floor': 12}`

## Exit Value + Reduce-Depth Opportunity

- Rows/value exits/reduce exits: `54/30/10`
- Would suppress value/reduce and delta: `3/8 / -116.000000c`
- Rows/suppressions/cushion needed: `0/19/78.000000c`
- Fail reasons: `{'collapse_kept_by_composite_rule': 5, 'not_value_or_reduce_exit': 9, 'reduce_entry_depth_above_ceiling': 1, 'reduce_p_hold_below_floor': 1, 'value_fair_drawdown_too_deep': 10, 'value_gap_negative': 27, 'value_p_hold_below_85': 18}`

## Exit Loss-Guard V1/V2/V3 Runway

- V2 strict settled: `58`
- V2 suppressions/delta: `5/152.000000c`
- V1-only opportunity cost after v2 freeze: `90.000000c`
- Rows/suppressions/cushion needed: `0/25/148.000000c`
- Blockers: `v2_suppressed_decisions_lt_30, full_loss_cushion_lt_3`

| variant | settled | suppressions | delta c | rows needed | suppressions needed | cushion c needed | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| v1 | 59 | 17 | 242.000000 | 0 | 13 | 58.000000 | v1_suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| v2 | 58 | 5 | 152.000000 | 0 | 25 | 148.000000 | v2_suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| v3 | 46 | 9 | 166.000000 | 0 | 21 | 134.000000 | v3_suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
