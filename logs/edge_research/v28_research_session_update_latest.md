# v28 Research Session Update

Research-only update. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T18:01:30Z`

## Latest Refresh - 2026-05-07T18:17Z

This section supersedes older intra-session counts below where they differ.

- Refreshed the live-only size2 log baseline with `score_bot_log.py`: `+1361c` / `+$13.61`, `632` entries, `521` completed round trips, W/L by sign `285/336`, `0` open positions. This is a log-derived baseline, not proof that size2 live collection is currently healthy.
- Read-only process inventory still shows the research/shadow status loop wrapper at PowerShell PID `33800` and the feature-gate size1 wrapper/Python sidecar at PIDs `26568` / `4972`. The old size2 live Python PIDs were not present in the sampled process list. No live or sidecar process was stopped, restarted, or modified.
- `v28_boundary_clock_feature_gate_candidate_latest` now has real post-feature-freeze rows. The cleanest profitable strict rows are under-covered: `post_feature_freeze_entry_raw07_recross60_abs085` and bridge both have `38` settled, `46.34%` coverage, `+454c`, reconstructed share `0.2105`, cushion `4`, blocked only by coverage. The near-broad `raw05` row has `55` settled, `67.07%` coverage, `+445c`, reconstructed share `0.2727`, cushion `4`, still blocked by coverage. The broad `raw03` row reaches `78.05%` coverage and `+307c`, but fails source quality with reconstructed share `0.3906`.
- `v28_boundary_clock_source_stress_latest` refreshed at `2026-05-07T18:16:28Z`: base boundary-clock repair is still blocked. Entry is `91` settled, `75.21%` coverage, `-151c`, reconstructed share `0.7143`, cushion `0`; FV bridge is `90` settled, `75.63%` coverage, `+229c`, reconstructed share `0.7889`, cushion `2`. The approved-source rows are good, but the rejected/reconstructed rows dominate the denominator and keep promotion blocked.
- `v28_candidate_vs_live_full_table_latest` now compares against the refreshed `+1361c` live baseline. It has `995` candidates, `807` positive, `588` positive target-coverage, and one advisory candidate-table `live_ready` row; the real live-readiness artifact remains false, so no candidate should be treated as promotable.
- Goal completion remains false. The refreshed audit reports `588` positive target-coverage lanes but `0` integrity-pass lanes; strict-forward leaderboard has `520` strict rows, `230` strict positive target-coverage rows, and `0` strict live-ready rows.
- The feature-gate sidecar audit remains an operations blocker, not promotion evidence: lock PID/tag `4972` / `mushroom_v28_feature_gate_raw05_recross60_abs085_ask65_size1_live`, `1` round trip, `0` open positions, net `-1c`, and blockers including `sidecar_live_trade_detected_while_readiness_false`.
- Two slow manual refresh attempts for `probe_v28_boundary_clock_approved_oracle_frontier.py` and `probe_v28_boundary_clock_feature_contrast.py` exceeded the command timeout without updating artifacts; the orphaned research-probe PIDs from those attempts were stopped. No live bot process was touched.

## Latest Continuation

This section supersedes older intra-session counts below where they differ.

- Read-only sidecar integrity follow-up: refreshed `live_mushroom_v28_feature_gate_size1` scoring and patched `probe_v28_feature_gate_sidecar_live_state_audit.py` so the report explicitly captures filled trade evidence, not just generic order-like events.
- The sidecar audit now reports a live sidecar trade while readiness was false: lock PID/tag `9536` / `mushroom_v28_feature_gate_raw05_recross60_abs085_size1_live`, process running `True`, `1` entry, `1` completed round trip, `0` open positions, `1` entry fill, `1` exit fill, net `-1c`, and `96` order-like events. Entry was `KXBTC15M-26MAY071400-00` NO at 8c; exit was the same market/side at 7c via `mushroom_v28_probability_collapse_full_single_shot_visible_depth`.
- Patched `probe_v28_forward_collection_blocker_audit.py` so the sidecar live trade appears as `feature_gate_sidecar_live_trade_detected_while_readiness_false` and remains separated from the `live_mushroom_v28_size2` baseline.
- Patched `probe_v28_objective_gap_checklist.py` so the research-only/no-candidate-live-trades row is blocked when the sidecar audit detects a live trade while `v28_live_trade_readiness_latest.json` says `any_live_ready=False`. The checklist is now `6` pass / `8` blocked / `0` unverified.
- Regenerated sidecar audit, forward blocker, objective checklist, next-action triage, and current-direction reports. Fresh size2 live collection remains blocked by the size2 watchdog `RESTART_FAILED` line and the shared live lock currently pointing at the feature-gate size1 sidecar; candidate-vs-live claims remain log-snapshot claims only.
- Fresh read-only process inventory showed the shadow status loop wrapper at PowerShell PID `33800` and the feature-gate sidecar Python PID `9536`. No live or sidecar process was stopped, restarted, or modified by this research continuation.
- Refreshed live-only size2 log baseline used by the latest candidate-vs-live checks: `+1361c` / `+$13.61`, `632` entries, `521` completed round trips, W/L by sign `285/336`, `0` open positions.
- Current read-only process inventory shows the shadow status loop wrapper at PowerShell PID `33800` and the feature-gate sidecar Python PID `9536`; it does not show the old size2 live Python PIDs `3356`/`19012`. No live or sidecar process was touched.
- Added `probe_v28_exit_common_clock_residual_frontier.py` plus `v28_exit_common_clock_residual_frontier_latest.md/json` to test strict-row residual exit rescues on top of the current best common-clock guard. This is research-only and does not freeze or promote an exit rule.
- Residual frontier conclusion: broad low-`p_hold` residual suppression is tempting but unsafe. In v2, `fair_drawdown_positive_low_p` adds `+642c` versus base across `17` residual rows, but has `15/2` helpful/harmful false-hold results. The clean residual is `collapse_full_any`: v2 has `5` rows for `+462c`, v3 has `4` rows for `+286c`, both with `0` harmful rows, but both remain too sparse for promotion or live use.
- Integrated the residual frontier into `probe_v28_next_action_triage.py` as action `0.8075` and into `probe_v28_current_direction_decision.py`. The new central read is: common-clock residual rescue is a child-watch/strict-collection lead, not a live exit change.
- A later read-only sidecar sample showed the external feature-gate sidecar had moved to lock PID/tag `4972` / `mushroom_v28_feature_gate_raw05_recross60_abs085_ask65_size1_live`. Refreshed sidecar audit and forward blocker now point to PID `4972`; score remains `1` round trip, `0` open, net `-1c`.
- Patched `probe_v28_feature_gate_sidecar_live_state_audit.py` so any `mushroom_v28_feature_gate_*_size1_live` lock is classified as a feature-gate sidecar. This removed the misleading `live_lock_not_feature_gate_sidecar` blocker for the ask65 sidecar variant while preserving the hard blocker `sidecar_live_trade_detected_while_readiness_false`.
- Added `probe_v28_loss_churn_observable_full_denominator_replay.py` plus `v28_loss_churn_observable_full_denominator_replay_latest.md/json` to test whether the loss-only observable frontier survives against every known continuous-scorecard row.
- Full-denominator replay result: best clean rule `recross_ge_045` selected `15` known rows, flipped `5` losses, added `+574c`, improved candidate net from `+819c` to `+1393c`, created `0` harmful holds and `0` new losses, and edges the refreshed live baseline by `+60c`.
- This is not promotable. It is still `diagnostic_full_denominator_replay`, not frozen forward evidence, and it has only `15` selected decisions versus the `>=30` evidence floor.
- Added `probe_v28_loss_churn_recross_clock_feasibility.py` plus `v28_loss_churn_recross_clock_feasibility_latest.md/json`. It confirms `recross_ge_045` is present at row/entry scope for all `15` selected rows, but the scorecard has `0` selected rows with `exit_ts` and only `10/15` selected rows with exit event fields.
- Added `probe_v28_loss_churn_recross_exit_clock_join_audit.py` plus `v28_loss_churn_recross_exit_clock_join_audit_latest.md/json`. Exact timestamp join is impossible, but a `0.5s` tolerance join was one-to-one on the materialized snapshot.
- Added `probe_v28_exit_clock_source_stability.py` plus `v28_exit_clock_source_stability_latest.md/json`. It blocks freezing the recross watch now because repeated exit-clock reads were unstable: row counts `[137, 71, 91, 88, 100]`, common/union keys `15/169`.
- Added `probe_v28_exit_clock_materialized_snapshot.py` plus `v28_exit_clock_materialized_snapshot_latest.md/json` so future denominator-sensitive audits can use a fixed exit-clock row source. The latest snapshot has `100` resolved rows, current net `+363c`, hold net `+850c`, and spans entries from `2026-05-05T16:50:05.762477+00:00` through `2026-05-07T16:24:52.871742+00:00`.
- Re-ran the recross join audit against that materialized snapshot. It matched `100/100` rows with `0` ambiguous, selected `8` recross rows, added `+124c`, and had `0` harmful / `0` new-loss rows. This materially weakens the earlier replay: the clean signal still exists, but it is too sparse and denominator-sensitive to freeze.
- Added `probe_v28_loss_churn_recross_threshold_frontier.py` plus `v28_loss_churn_recross_threshold_frontier_latest.md/json`. On the fixed snapshot, `recross >= 0.45` is the best clean point: `8` selected, `+124c`, `0` harmful, `0` new losses. Loosening to `0.40` selects `12` rows but introduces `1` harmful hold and `1` new loss; `0.35` and `0.30` degrade further. This closes the simple threshold-freeze path.
- Added `probe_v28_exit_clock_observable_hold_guard_frontier.py` plus `v28_exit_clock_observable_hold_guard_frontier_latest.md/json`. On the same fixed snapshot, the best clean simple hold rule selected only `13` rows for `+537c`, while the broad `33`-row hold pocket added `+1159c` but had `1` harmful hold and `1` new loss.
- Added `probe_v28_exit_clock_low_edge_hold_guard_tradeoff.py` plus `v28_exit_clock_low_edge_hold_guard_tradeoff_latest.md/json` to test whether the broad hold pocket can be repaired by low-edge shrink/guarding. Best clean policy `base_exit_hold_raw_edge_ge_7_else_weight_0` selected `19` rows, added `+869c`, had `19/0/0` helpful/harmful/flat, `9` loss flips, `0` new losses, and full-loss cushion `12`, but there is no clean policy with `>=30` selected decisions. Low-edge fractional shrink still leaves a harmful row unless that row is effectively excluded.
- Added `probe_v28_exit_clock_broad_hold_neighbor_autopsy.py` plus `v28_exit_clock_broad_hold_neighbor_autopsy_latest.md/json` to explain the broad hold pocket. The low-edge `<7` slice is mixed: `14` rows, `+290c`, `13/1` helpful/harmful, and the only new loss; the high-edge `>=7` survivor is clean at `19` rows, `+869c`, and `19/0` helpful/harmful, but still below the 30-decision floor.
- Integrated the replay, join audit, threshold frontier, low-edge tradeoff, neighbor autopsy, and source-stability caveat into `probe_v28_next_action_triage.py` and `probe_v28_current_direction_decision.py` as promising observable exit/state clues that should remain mechanism-only, not frozen watches.
- Read-only live-ops note: a final process resample no longer showed the old v28 live Python PIDs `3356`/`19012`. `state/live_trading.lock` still points at PID `3356`, while `logs/live_mushroom_v28_size2/hourly_monitor.log` reports `2026-05-07 13:22:29 -04:00 | RESTART_FAILED | no live bot process detected after launch`. No live bot restart, stop, or order action was performed in this research continuation.
- Added `probe_v28_forward_collection_blocker_audit.py` plus `v28_forward_collection_blocker_audit_latest.md/json` to separate strategy blockers from evidence-collection blockers. It reports `goal achieved=False`, candidate-vs-live live-ready count `0`, latest v28 watchdog status `RESTART_FAILED`, latest v28 execution event `2026-05-07T17:12:13.706367+00:00`, and the shared live lock currently pointing at PID `29032` / `mushroom_v21_physical_size1_live_test`. This is a read-only blocker report; no live process was stopped or restarted.
- Updated `probe_v28_next_action_triage.py` so action `0.79` now warns to pause fresh v28 live-collection claims until the live state is explicitly healthy again. Existing candidate-vs-live rows remain log-snapshot evidence, not fresh ongoing v28 collection.
- Added `probe_v28_objective_gap_checklist.py` plus `v28_objective_gap_checklist_latest.md/json` as an explicit prompt-to-artifact completion checklist. The checklist has `14` rows: `7` pass, `7` blocked, `0` unverified. It confirms `995` candidates, `792` positive candidates, `564` target-coverage positive candidates, but `0` live-ready candidates and `live_collection_healthy=False`. The decisive blocked row is that no candidate clears sample, net, coverage, source, cushion, live readiness, live-baseline comparison, and fresh collection health together.
- Added `probe_v28_feature_gate_joint_gate_gap_audit.py` plus `v28_feature_gate_joint_gate_gap_audit_latest.md/json` to compute current feature-gate joint gaps directly from the moving feature-gate artifact. Current raw03 post-freeze rows hit `75.00%` coverage but have reconstructed share `0.370` and cushion `2`; current raw05 rows are cleaner at reconstructed share `0.277` and bridge cushion `3`, but need `7` clean rows for coverage and still trail the stale live snapshot by `983c` bridge / `1039c` entry. Dropping risky raw03 losses fixes source only by breaking coverage. The objective checklist now cites this joint-gap audit.
- Added `probe_v28_feature_gate_gap_mechanism_synthesis.py` plus `v28_feature_gate_gap_mechanism_synthesis_latest.md/json` to classify the feature-gate gap. It concludes this is not a broad-exit-suppression repair: raw05 bridge losses are mostly `no_exit_observation`/source rows (`10` rejected-actionable losses) and the `3` approved-entry losses were helped by exits versus holding. The exit-state frontier best remains `baseline_live` with `0c` delta-live, so raw05 should be treated as a clean-core coverage/source wait rather than an exit-policy fix.
- Added `probe_v28_feature_gate_current_margin_size_proxy.py` plus `v28_feature_gate_current_margin_size_proxy_latest.md/json` to retest continuous marginal sizing on the current feature-gate denominator. Best exposure-clean bridge proxy keeps raw05 anchor rows full size and gives raw03-only marginal rows `0.05x` notional: coverage `75.00%`, weighted net `345.9c`, cushion `3`, exposure-source share `0.282`, but official row-source share remains `0.370` and it still trails the stale live snapshot by `987.1c`. Zeroing marginal rows restores row source but breaks coverage. This makes marginal sizing useful risk context, not a promotion repair.
- Integrated the current-denominator feature-gate joint-gap, mechanism synthesis, and margin-size proxy into `probe_v28_next_action_triage.py` and `probe_v28_current_direction_decision.py`, then regenerated `v28_next_action_triage_latest.md/json` and `v28_current_direction_decision_latest.md/json`.
- Central decision now says: do not repair raw05 with raw03 relaxation or broad exit suppression. raw05 bridge is the cleaner core (`47` entries, `65.28%` coverage, `+350c`, reconstructed share `0.277`, cushion `3`) but needs `7` clean rows and remains `-983c` versus the live snapshot; raw03 bridge reaches `75.00%` coverage but has reconstructed share `0.370`, cushion `2`, and `-1050c` versus the live snapshot.
- Central triage now treats marginal sizing as risk context only: current best exposure-clean bridge proxy has `75.00%` coverage, `+345.85c` weighted net, cushion `3`, exposure-source share `0.282`, but official row-source share `0.370` and live-snapshot delta `-987.15c`. Zeroing raw03-only marginal rows restores raw05 source quality but drops coverage to `65.28%`.
- Refreshed the live_mushroom_v28_size2 log baseline again: `+1361c` / `+$13.61`, `632` entries, `521` completed round trips, W/L by sign `285/336`, `0` open positions. This is a log baseline, not proof that the old size2 live process is currently healthy.
- Refreshed candidate-vs-live, forward-collection blocker, shadow availability, candidate tracker, goal audit, objective checklist, triage, and current-direction reports. Candidate-vs-live now has `995` candidates, `805` positive candidates, `574` positive target-coverage candidates, and one advisory candidate-table `live_ready` row; the live-readiness artifact still says `any_live_ready=False`.
- Patched `probe_v28_objective_gap_checklist.py` so the "Live readiness gate passes" row uses `v28_live_trade_readiness_latest.json` and the goal-audit `live_readiness_gate`, not the advisory candidate-table `live_ready_count`. The checklist is now `7` pass / `7` blocked / `0` unverified and explicitly says candidate-table live_ready flags are not sufficient.
- Refreshed the exit dashboard and queue serially. Closest strict exit row is now `common_clock_strict_forward_v2`: `58` settled, `17` suppressions, candidate net `+668c`, delta `+242c`, candidate/delta cushion `6/2`. It still needs `13` more suppressions and `58c` more delta cushion before review; no exit watch clears the queue.
- Patched `probe_v28_exit_promotion_queue_audit.py` to include its own `generated_at_utc`, then regenerated `v28_exit_promotion_queue_audit_latest.md/json`.
- Added `probe_v28_feature_gate_sidecar_live_state_audit.py` plus `v28_feature_gate_sidecar_live_state_audit_latest.md/json` after a read-only lock/process sample found a transient `live_mushroom_v28_feature_gate_size1` sidecar. The audit recorded lock tag `mushroom_v28_feature_gate_raw05_recross60_abs085_size1_live`, score `0` entries / `0` round trips / `0` open, `35` `mushroom_v28_rejected` events, `0` order-like events, and a later hourly-monitor `RESTART_FAILED`. Keep this sidecar evidence separate from the size2 live baseline.

## Latest Refresh

This section supersedes older intra-session counts below where they differ.

- Refreshed live-only baseline: `+941c` / `+$9.41`, `563` entries, `463` completed round trips, W/L by sign `263/292`, `1` open position.
- Fresh process inventory was read-only. Live bot Python PIDs remain `19012` and `3356`; active shadow status loop wrapper is PowerShell PID `33800`. A second matching PowerShell row was the inspection command itself.
- Candidate-vs-live table now has `874` candidates, `613` positive candidates, `405` positive target-coverage candidates, and `0` live-ready candidates.
- Candidate registry coverage audit checks `256` active expected rows against `874` tracker rows, with `0` missing active rows.
- Goal completion audit remains `Achieved: False`; strict-forward leaderboard still has `0` strict live-ready rows.
- Added `probe_v28_top_component_strict_gate_audit.py` plus `v28_top_component_strict_gate_audit_latest.md/json` to consolidate the top-component promotion gate against the freshly refreshed live baseline. Promotion gate passes remain `0`.
- Refreshed the top-component mix portfolio and child repair reports. The best component stack remains diagnostically strong: `rescue_drop15_plus_absd_parent_fill_to75` has `66` diagnostic rows, `75.00%` coverage, `+1539.5c`, W/L `56/10`, reconstructed share `31.82%`, full-loss cushion `15`, and `+598.5c` versus the refreshed live baseline. This is explicitly blocked as `diagnostic_prefreeze`.
- Strict top-component post-birth evidence is not promotable. The portfolio strict denominator is only `4`; it has `4` selected parent rows, `3` settled, `1` pending, and `0` settled selected rows joined to exit-clock rows. The closest strict post-birth variants have only `3` settled rows, W/L `1/2`, `75.00%` coverage, net `-78c` or `-90c`, `-1019c` to `-1031c` versus live, high reconstructed/rejected share, and blockers for sample size, source share, net, exit-clock join, cushion, and live-baseline delta.
- Refreshed the top-component parent-fill repair child. Its diagnostic best `diagnostic_observable_mid_confidence_parent_fill_quarter` scores `+2012.5c` with W/L `59/7`, but child strict evidence is only `1` settled row on a `2`-row future denominator: `+16c`, `50.00%` coverage, `-925c` versus live, and blocked by sample, coverage, source-margin/cushion, exit-clock join, and live-baseline gates.
- Added `probe_v28_top_component_strict_row_autopsy.py` plus `v28_top_component_strict_row_autopsy_latest.md/json`. It finds only `4` unique strict rows for the top-component branch, net `-62c`: `2` loss rows for `-106c` and `2` winner rows for `+44c`. All are parent-fill rows with no exit-clock join; `3/4` are rejected-actionable, and the rejected slice is `-78c` while the only approved-entry row is `+16c`.
- Strict top-component row failure tags are led by `parent_fill_no_exit_clock` (`4` rows), `source_quality_error` (`3`), `fv_or_entry_error` (`2`), `large_raw_edge_false_positive` (`2`), `low_or_mid_ask_touch` (`2`), and `weak_boundary_distance` (`2`). This argues against broadening parent-fill exposure until strict approved-source and exit-clock overlap rows accumulate.
- Refreshed the top-component loss-cluster drilldown. The diagnostic best stack still loses `-427c` across `10` rows: `3` approved-entry exit-policy false negatives for `-198c`, `3` rejected-actionable parent-fill entry/FV losses for `-119c`, and `4` true FV/entry losers for `-110c`. On losing rows with both marks, holding would worsen losses by `-52c`, so the repair target is a split of exit false negatives plus true FV/entry/source-quality losses, not broad holding.
- Boundary-clock feature-gate post-feature-freeze rows have denominator `56`. Current broad post-freeze entry lane `raw03_recross70_abs075` is `41` entries / `40` settled, `73.21%` coverage, `+232c`, W/L `24/16`, reconstructed share `43.90%`, full-loss cushion `2`, and `-709c` versus live. The matching bridge lane is `41` entries / `38` settled, `+298c`, W/L `23/15`, and `-643c` versus live. Both remain blocked by coverage, source share, cushion, and live-baseline delta.
- The current near-promotion watch is `raw05_recross60_abs085`: entry lane `35` entries / `34` settled, `62.50%` coverage, `+293c`, W/L `22/12`, reconstructed share `34.29%`, full-loss cushion `2`; bridge lane `35` entries / `32` settled, `+359c`, W/L `21/11`, reconstructed share `34.29%`, full-loss cushion `3`. It is near the source gate but far below broad coverage and still trails live by `648c` entry / `582c` bridge.
- Added `probe_v28_feature_gate_ask_floor_tradeoff_autopsy.py` plus `v28_feature_gate_ask_floor_tradeoff_autopsy_latest.md/json`. The clean `ask65` core is source-clean but too narrow: entry `28` entries / `27` settled, `50.00%` coverage, `+161c`, W/L `24/3`, reconstructed share `3.57%`, and `-780c` versus live; bridge `28` entries / `25` settled, `+226c`, W/L `23/2`, and `-715c` versus live.
- Ask-floor tradeoff autopsy: raw05 adds `12` rows versus ask65; those added rows are `2/10`, `+106c`, `91.7%` rejected/reconstructed, all below ask65 and cheap-touch, with `5` same-market side-displacements. Raw03 adds `6` rows beyond raw05; those rows are all rejected-actionable, `2/4`, `-77c`. This says raw05's coverage gain is fragile cheap-tail exposure, while raw03's extra broad coverage is source-quality-negative.
- Added `probe_v28_feature_gate_side_displacement_guard.py` plus `v28_feature_gate_side_displacement_guard_latest.md/json` to test an observable same-market guard: if a cheap selected side conflicts with a same-market opposite side passing the ask65 core at ask `>=0.85`, prefer the high-ask side. This is a settled-row replay, not a promotion candidate.
- Side-displacement guard result: best entry replay `raw05_recross60_abs085_ask85_over_cheap10_priority` improves to `35` entries / `35` settled replay rows, W/L `26/8`, `62.50%` coverage, `+354c`, settled reconstructed share `22.86%`, cushion `3`, but still `-587c` versus live. Best broad replay `raw03_recross70_abs075_ask85_over_cheap10_priority` reaches `73.21%` coverage, `+293c`, settled reconstructed share `34.15%`, but still has cushion `2` and trails live by `648c`.
- Only the central feature-gate candidate report was refreshed in this latest pass. The linked-source, size-shrink, source-feasibility, and promotion-gap paragraphs immediately below are retained as earlier intra-session detail and should be rerun before making a fresh source-feasibility or size-shrink promotion claim.
- Refreshed the feature-gate linked source runway, source denominator, source feasibility, source blocker mechanism, size-shrink runway, near-promotion, and promotion-gap reports in dependency order after a moving-artifact mismatch appeared. The consistency audit now agrees on `41` entries / `40` settled, `74.55%`, `+230c`, and `43.90%` reconstructed share for the broad post-freeze row.
- Patched `probe_v28_feature_gate_promotion_gap_audit.py` so its Promotion Gap interpretation is generated from current blockers instead of a static sentence. The latest report correctly says the broad row clears sample and positive PnL but misses coverage, source share, full-loss cushion, and live-baseline delta.
- Added `probe_v28_feature_gate_artifact_consistency_audit.py` plus `v28_feature_gate_artifact_consistency_audit_latest.md/json` to catch stale or mixed feature-gate artifacts before candidate-vs-live claims. The latest audit is `consistent_for_promotion_discussion=True` with no blockers.
- Patched `probe_v28_feature_gate_coverage_size_shrink.py` to persist selected rows for each size-shrink policy, patched `probe_v28_feature_gate_size_shrink_source_runway.py` to consume those persisted rows instead of reselecting from moving raw surfaces, and patched the promotion-gap/consistency probes to carry official `entries` separately from `settled`. The size-shrink reports now agree on `42` settled, `78.18%` coverage, `+315c` weighted net, `41.86%` row reconstructed share, and `-410c` versus live.
- Refreshed source feasibility/mechanism after the denominator update. With denominator `55`, the source gate is now infeasible even at `75%` coverage: required `42` markets need at least `35.71%` reconstructed share, above the `<=35%` gate. Source-only weighted net is `-26c` on `18` rows.
- Added and froze a research-only matched-unchanged loss guard watch from the guarded separator refinement. Freeze UTC: `2026-05-07T09:30:07.471830+00:00`; rule: `abs_d_sigma <= 0.888798`, `exit_cents >= 51`, `eligible_depth <= 326.6`, and `exit_p_hold >= 0.718799`.
- Matched-unchanged guard diagnostic parent selected `21` of `140` scored rows with `20/0/1` helpful/harmful/flat, current net `+373c`, candidate net `+1292c`, selected hold delta `+919c`, and loss count `64 -> 50`. This is mechanism context only.
- Matched-unchanged guard strict post-freeze rows are now collecting: `1` scored exit row, `0` selected rows, current/candidate net `18c`, delta `0c`, cushion `0`; blockers are `settled_lt_30`, `suppressed_decisions_lt_30`, `delta_not_positive`, and `full_loss_cushion_lt_3`.
- Shadow observation availability now sees the matched-unchanged guard clock collecting: `553` post-freeze events, `2` post-freeze entries, `2` post-freeze exit-clock rows, `1` settled row, and `1` pending row. This is a sparse-rule/settlement wait, not a wiring failure.
- Exit denominator audit now separates true join/filter risk from watch-specific overlap scarcity. It reports `0` potential join/filter denominator issues, `5` watch-specific overlap waits, `10` collecting-but-not-firing watches, `5` positive-but-immature watches, and `0` promotion-gate passes.
- Integrated the new matched-unchanged guard watch into the candidate tracker, exit-policy dashboard, shadow-observation availability clocks, active registry coverage audit, and exit dashboard coverage audit.
- Updated `probe_v28_next_action_triage.py` so action `0.823` now says `collect_matched_unchanged_loss_guard_watch_rows` instead of warning that the unguarded separator still needs a guard.
- Updated `probe_v28_current_direction_decision.py` so the exit-policy decision explicitly treats the matched-unchanged guard as a frozen strict-row wait, with diagnostic `21` selected, `20/0` helpful/harmful, `+919c` diagnostic delta, and `0` post-freeze rows.
- Added `probe_v28_exit_true_loser_hold_risk_audit.py` plus `v28_exit_true_loser_hold_risk_audit_latest.md/json` as a safety guardrail for exit work. It separates clipped-winner exits from true FV/entry-timing losers that should not be held.
- True-loser hold-risk audit: `21` true-loser rows would lose another `-2158c` if held, while `43` clipped-winner rows would gain `+2855c` if held. Avoid-broad-hold tags are `fv_or_entry_timing_error`, `medium_25_49c`, `exit_cents_lte40`, `thin_touch_depth`, `large_50_99c`, and `ask_lt55`.
- `probe_v28_next_action_triage.py` now includes action `0.824` (`use_true_loser_hold_risk_as_exit_suppression_guardrail`) so future exit suppression work does not treat all losing exits as clipped winners.
- `probe_v28_current_direction_decision.py` now carries the same true-loser safety boundary in the exit-policy decision evidence.
- Added `probe_v28_exit_false_hold_guardrail_bridge.py` plus `v28_exit_false_hold_guardrail_bridge_latest.md/json` to translate strict harmful suppressions into concrete rejection signals for future exit watches.
- False-hold bridge: the strict common-clock windows have `10` harmful suppressions for `-1440c`. Top guardrail tags are `exit_cents_gte60`, `p_hold_75_85`, `positive_fair_drawdown`, `p_hold_75_79`, `positive_book_gap_ge05`, `probability_reduce`, `exit_cents_gte80`, `negative_book_gap`, and `value_over_hold`. This says promotion review must show a candidate avoids rich/60c+ exits with mid-high p_hold and positive fair-drawdown false-hold risk before clipped-winner recovery is trusted.
- `probe_v28_next_action_triage.py` now includes action `0.825` (`require_false_hold_guardrails_in_exit_watch_review`), and `probe_v28_current_direction_decision.py` carries the same bridge in the exit-policy evidence.
- `probe_v28_exit_watch_promotion_gate_audit.py` now carries the false-hold guardrail directly. It applies only to broad-hold lanes with at least one suppressed decision, leaving zero-row watches classified as denominator waits.
- Exit dashboard coverage audit now sees `36` tracker exit-like gates, `28` dashboard lanes, `25` dashboard-covered gates, `11` intentional exclusions, and `0` active exit/state gates missing dashboard coverage.
- Exit policy dashboard status counts are now `{'blocked_loss_control_cost': 5, 'blocked_net_not_positive': 6, 'positive_but_under_sample': 3, 'waiting_no_post_freeze_rows': 10, 'waiting_no_suppressed_exits': 3, 'waiting_rule_has_not_fired': 1}`.
- Exit watch promotion-gate pass count remains `0`; primary reads are `{'blocked_false_hold_guardrail': 6, 'blocked_not_positive': 1, 'collecting_rule_not_firing': 7, 'immature_sample_or_density': 4, 'waiting_for_denominator': 10}`. Closest strict exit watch remains `common_clock_strict_forward_v2`, with `25` settled, `7` suppressions, `+34c` net, `+58c` delta, and sample/suppression/cushion blockers.
- Refreshed central scorecards after the integration: boundary-clock feature-gate candidate, boundary-clock source stress, approved-oracle frontier, feature contrast, goal completion audit, current direction decision, candidate PnL tracker, candidate-vs-live table, registry coverage audit, and next-action triage.
- Current direction remains exit/state validation first. The new guarded matched-unchanged watch is a frozen forward monitor, not promotion evidence; no live bot logic, trades, restarts, or process control were performed.

## Earlier Refresh Detail

This section supersedes older intra-session counts below where they differ.

- Refreshed live-only baseline: `+629c` / `+$6.29`, `547` entries, `451` completed round trips, W/L by sign `256/284`, `0` open positions.
- Fresh process inventory was read-only. Live bot Python PIDs remain `19012` and `3356`; active shadow status loop wrapper is PowerShell PID `33032`, currently running child Python PID `9008` on `probe_v28_raw_p52_favorite_valley_skip.py`. A second matching PowerShell row was the inspection command itself.
- Candidate-vs-live table now has `799` candidates, `562` positive candidates, `355` positive target-coverage candidates, and `0` live-ready candidates.
- Candidate registry coverage audit checks `255` active expected rows against `799` tracker rows, with `0` missing active rows and `2,265` diagnostic-like untracked rows.
- Goal completion audit remains `Achieved: False`.
- Boundary-clock feature-gate now has strict post-feature-freeze rows. Best post-freeze entry/bridge lane is `raw03_recross70_abs075`: `37` settled, `75.51%` coverage, `+275c`, W/L `22/15`, reconstructed share `43.24%`, full-loss cushion `2`. It is still blocked by `reconstructed_share_gt_35pct` and `full_loss_cushion_lt_3`, and trails the refreshed live-only baseline by `354c`.
- Refreshed shadow availability sees `21,294` events and `140` reconstructed shadow trades. Older clocks have settled exit-clock denominators. The newest exit watches still mostly have post-freeze shadow events with no reconstructed post-freeze trades, while `exit_clip_separator_watch` now has `2,069` post-freeze events, `3` post-freeze entries, `3` post-freeze exit-clock rows, `3` settled rows, and no observation blocker.
- Active zero-row watches are still denominator waits: `exit_shallow_drawdown`, `exit_shallow_duration_lte52`, `feature_gate_exit_bid_suppression`, `feature_gate_exit_bid_delayed_recheck`, `feature_gate_value_exit`, `value_exit_feature_side_guard`, `soft_frontier_midprice_delayed_recheck_exit`, `soft_frontier_midprice_delayed_recheck_rescue`, and `exit_common_clock_residual_child`.
- Added `probe_v28_exit_dashboard_coverage_audit.py` to make exit-dashboard coverage explicit. The latest audit sees `35` tracker exit-like gates, `27` dashboard lanes, `24` dashboard-covered gates, `11` intentional exclusions, and `0` active exit/state gates missing dashboard coverage.
- Fixed the remaining dashboard tracking gaps: `book_gap_loss_guard_v3`, `book_gap_value_only`, `value_reduce_depth_composite`, `reduce_observable_loss_control`, `reduce_geometry_relaxed`, and `midband_reduce_rescue` are now included in `v28_exit_policy_watch_dashboard_latest`.
- Fixed earlier dashboard tracking gaps: `feature_gate_exit_bid_delayed_recheck`, `soft_frontier_midprice_delayed_recheck_rescue`, `exit_reduce_drift_guard`, `exit_shallow_drawdown`, and `exit_shallow_duration_lte52` are included in `v28_exit_policy_watch_dashboard_latest`, so the denominator audit tracks them with the other frozen exit watches.
- Denominator audit latest generic base exit timestamp is `2026-05-07T05:07:39.410123+00:00`; no zero-row watch currently has base exit rows after its freeze, and no join/filter denominator issue is visible.
- The shadow status-loop log tail is stale at `2026-05-07 03:24:14 -04:00`, but read-only process and artifact checks show the research loop is still alive: PowerShell PID `33032` has child Python PID `9008` running `probe_v28_raw_p52_favorite_valley_skip.py`, and edge-research artifacts were written at `05:18 -04:00`.
- Added the frozen clean `soft_frontier_midprice_delayed_recheck_rescue` watch to the exit dashboard, shadow-availability clocks, and active registry coverage audit. Candidate tracker already had the row; the promotion/readiness rollups now see it too.
- Added the active `exit_reduce_drift_guard`, `exit_shallow_drawdown`, and `exit_shallow_duration_lte52` watches to the exit dashboard, shadow-availability clocks, candidate tracker, and active registry coverage audit.
- Exit dashboard status counts are now `{'blocked_loss_control_cost': 5, 'blocked_net_not_positive': 6, 'positive_but_under_sample': 3, 'waiting_no_post_freeze_rows': 9, 'waiting_no_suppressed_exits': 3, 'waiting_rule_has_not_fired': 1}`.
- Exit denominator read counts are now `{'collecting_blocked': 8, 'collecting_positive_but_immature': 3, 'denominator_collecting_rule_not_firing': 7, 'too_new_no_base_exit_rows': 9}`. The nine too-new zero-row watches are `exit_shallow_drawdown`, `exit_shallow_duration_lte52`, `common_clock_residual_child_exit70_79`, `soft_frontier_midprice_delayed_recheck_exit`, `soft_frontier_midprice_delayed_recheck_rescue`, `feature_gate_value_exit`, `feature_gate_exit_bid_suppression`, `feature_gate_exit_bid_delayed_recheck`, and `value_exit_feature_side_guard`; `exit_clip_separator_watch` is a rule-not-firing watch with `1` matched row, `0` selected/suppressed rows, and no promotion relevance yet.
- The three positive strict/active exit watches are still immature: `book_gap_loss_guard_v3` has `13` settled, `2` suppressions, `+52c` net, `+24c` delta; `common_clock_strict_forward_v2` has `25` settled, `7` suppressions, `+34c` net, `+58c` delta; `common_clock_strict_forward_v3` has `13` settled, `3` suppressions, `+58c` net, `+30c` delta. All remain blocked by sample/suppression/cushion gates.
- Added `probe_v28_exit_watch_promotion_gate_audit.py` plus `v28_exit_watch_promotion_gate_audit_latest.md/json` to join dashboard, denominator, coverage, and registry reads into one strict exit-watch gate table. Latest promotion-gate pass count is `0`; primary reads are `{'blocked_loss_control_harm': 5, 'blocked_not_positive': 3, 'collecting_rule_not_firing': 7, 'immature_sample_or_density': 3, 'waiting_for_denominator': 9}`. The closest watch remains `common_clock_strict_forward_v2`, with `25` settled, `7` suppressions, `+34c` net, `+58c` delta, and blockers `settled_lt_30`, `suppressed_decisions_lt_30`, and `full_loss_cushion_lt_3`.
- Newly dashboarded blocked watches clarify what not to chase right now: `book_gap_value_only` is `-220c` with `-180c` loss-control cost, `value_reduce_depth_composite` is `-210c` with `-120c` loss-control cost, and `reduce_geometry_relaxed` is `-68c` with `-120c` loss-control cost.
- The drift guard is collecting post-freeze denominator rows but not firing: `7` settled, `0` suppressions, `0c` delta, blockers `settled_lt_30`, `suppressed_decisions_lt_30`, `suppressed_delta_not_positive`, and `full_loss_cushion_lt_3`.
- Shallow drawdown and shallow-duration strict rows are still `0`; both look recency-limited rather than broken because no zero-row watch currently has base exit rows after its freeze.
- The clean rescue diagnostic remains diagnostic only: `54` joined rows, `31` suppressions, helpful/harmful `29/0`, weighted delta `+478c`, reconstructed share `16.67%`, but strict `post_clean_rescue_birth` rows are still `0`.
- Closest positive strict exit watch is still `common_clock_strict_forward_v2`: `25` settled, `7` suppressions, `+34c` net, `+58c` delta. It needs `5` more settled rows, `23` more suppressed decisions, and `266c` more cushion before review.
- Reduce no-fire audit still argues against widening reduce suppression: depth gate has only `1` probability-reduce row in `27` post-birth rows, and relaxing to `p_hold>=0.75` would have fired once for `-120c` harm; geometry rejected `2` base opportunities worth `-74c`.
- Refreshed the loss-churn chain: `v28_live_loss_escape_analysis_latest`, `v28_exit_policy_loss_churn_effect_latest`, `v28_exit_repair_loss_churn_impact_latest`, `v28_exit_repair_gap_classifier_latest`, and `v28_next_action_triage_latest`. The loss-count blocker remains: `64` losing control rows, `50` unresolved, `31` matched-but-unchanged, `19` no-observation rows that all predate the first exit-repair freeze, and `12` repair-flipped losses.
- Added `probe_v28_matched_unchanged_loss_separator.py` plus `v28_matched_unchanged_loss_separator_latest.md/json` to separate the `31` matched-but-unchanged loss rows by observable features. Loss-only diagnostic best is `abs_d_sigma <= 0.888798 AND exit_cents >= 51`, with `9` selected rows, `9/0` hold-helpful/harmful, and `+624c` hold delta. Full scored-exit denominator sanity check weakens it: the same rule selects `30` rows, `26/3` helpful/harmful, `+933c` hold delta, loss count `22 -> 3`, but worst harm is `-146c`. Treat this as a future-watch hypothesis only, not a freeze or promotion candidate.
- `probe_v28_next_action_triage.py` now reads `v28_matched_unchanged_loss_separator_latest` and surfaces this as action `0.823`, explicitly warning that the separator needs an additional guard before any watch freeze.

## Files Updated In This Refresh

- `probe_v28_shadow_observation_availability.py` now includes the active zero-row exit watches in its frozen-clock registry, including `soft_frontier_midprice_delayed_recheck_rescue`, `exit_shallow_drawdown`, `exit_shallow_duration_lte52`, and `exit_clip_separator_watch`.
- Refreshed reports: `v28_shadow_observation_availability_latest`, `v28_exit_policy_watch_dashboard_latest`, `v28_exit_policy_maturity_runway_latest`, `v28_exit_watch_denominator_audit_latest`, `v28_exit_reduce_no_fire_audit_latest`, `v28_exit_dashboard_coverage_audit_latest`, `v28_candidate_pnl_tracker_latest`, `v28_candidate_registry_coverage_audit_latest`, `v28_candidate_vs_live_full_table_latest`, `v28_goal_completion_audit_latest`, `v28_current_direction_decision_latest`, and `v28_next_action_triage_latest`.
- Refreshed loss-churn reports: `v28_live_loss_escape_analysis_latest`, `v28_exit_policy_loss_churn_effect_latest`, `v28_exit_repair_loss_churn_impact_latest`, and `v28_exit_repair_gap_classifier_latest`.
- Added `probe_v28_exit_dashboard_coverage_audit.py` plus `v28_exit_dashboard_coverage_audit_latest.md/json` as a dashboard-coverage guardrail.
- Added `probe_v28_exit_watch_promotion_gate_audit.py` plus `v28_exit_watch_promotion_gate_audit_latest.md/json` as a strict active-exit promotion-gate rollup.
- Added `probe_v28_matched_unchanged_loss_separator.py` plus `v28_matched_unchanged_loss_separator_latest.md/json` as a diagnostic loss-separator and full-denominator sanity check for matched-but-unchanged exit losses.
- `probe_v28_exit_policy_watch_dashboard.py` now includes `feature_gate_exit_bid_delayed_recheck`, `soft_frontier_midprice_delayed_recheck_rescue`, `exit_reduce_drift_guard`, `exit_shallow_drawdown`, `exit_shallow_duration_lte52`, `book_gap_loss_guard_v3`, `book_gap_value_only`, `value_reduce_depth_composite`, `reduce_observable_loss_control`, `reduce_geometry_relaxed`, `midband_reduce_rescue`, and `exit_clip_separator_watch`; downstream denominator reports pick them up from the dashboard.
- `probe_v28_next_action_triage.py` no longer repeats the completed `freeze_observable_exit_clip_separator_watch` action when the frozen watch artifact exists. It now prioritizes collecting strict post-freeze rows for the clip separator watch, which froze at `2026-05-07T04:04:23.876080+00:00` and currently has `1` post-freeze matched row with `0` selected rows.
- `probe_v28_next_action_triage.py` now also includes `treat_matched_unchanged_loss_separator_as_guarded_watch_hypothesis_only`, so the loss-derived separator is not mistaken for a freeze-ready exit rule.
- `probe_v28_candidate_registry_coverage_audit.py` now treats `soft_frontier_midprice_delayed_recheck_rescue`, `exit_reduce_drift_guard`, `exit_shallow_drawdown`, `exit_shallow_duration_lte52`, and `exit_clip_separator_watch` as active special-family rows. The latest rerun is complete against `799` tracker rows.
- Added `probe_v28_feature_gate_promotion_gap_audit.py` and `v28_feature_gate_promotion_gap_audit_latest.md` to consolidate the refreshed feature-gate promotion blockers.

## Feature-Gate Promotion Gap

- New consolidated conclusion: `watch_only_not_promotable`.
- Official broad post-freeze lane `post_feature_freeze_entry_raw03_recross70_abs075`: `37` settled, `75.51%` coverage, `+275c`, W/L `22/15`, reconstructed share `43.24%`, full-loss cushion `2`, delta versus live `-354c`.
- Nearer source-clean lane `raw05_recross60_abs085`: `33` settled, `67.35%` coverage, `+275c`, reconstructed share `36.36%`, full-loss cushion `2`, delta versus live `-354c`.
- Clean ask-floor lane `raw05_recross60_abs085_ask65`: `26` settled, `53.06%` coverage, `+142c`, reconstructed share `3.85%`, full-loss cushion `1`, delta versus live `-487c`.
- Size-shrink runway `repair_low_absd_quarter_else_half`: `37` settled, `73.47%` coverage, weighted net `+315c`, row reconstructed share `37.84%`, only `15c` cushion surplus after three full losses, and `-314c` versus the refreshed live baseline.
- Source feasibility bound: in the current `49`-market denominator, a `75%` source-clean target is mathematically feasible with minimum reconstructed share `32.43%`, but `80%` requires `37.50%` reconstructed share and fails the `<=35%` source gate.
- Source-only weighted slice is `-10c` on `14` rows; worst negative observable tags are `mid_ask_lt065`, `moderate_p_side_lt085`, `weak_boundary_distance_lt065`, and `thin_depth_lt100`.
- Interpretation: feature-gate source dilution is barely possible at `75%`, but the current frozen pool does not beat live, does not clear all gates, and should remain watch-only while exit/state rows mature.

## Feature-Gate Failure Priority

- Added `probe_v28_feature_gate_failure_priority_audit.py` and `v28_feature_gate_failure_priority_audit_latest.md` to consolidate selected-row losses, loss analogs, residual-loss tags, and live exit mismatch into the explicit project failure buckets.
- Current strict lane remains `post_feature_freeze_entry_raw03_recross70_abs075`: `37/49` settled/denominator, W/L `22/15`, coverage `75.51%`, net `+275c`, reconstructed share `43.24%`, cushion `2`.
- Ranked repair priority from current evidence:
  - `exit_policy_error`: `7` selected-side theory winners became live selected-side losses; settlement theory `+161c`, live selected-side PnL `-456c`, swing `+617c`. This is the clearest live-market failure evidence, but active exit watches still need strict post-freeze denominators.
  - `source_quality_error`: `13` selected losses carry source-quality tags and the broad row has `43.24%` reconstructed share.
  - `fragility_error`: selected losses total `-221c`, and the broad lane has only a `2` full-loss cushion.
  - `execution_friction_error`: `15` selected losses carry execution/friction or thin-edge tags.
  - `FV/market-regime/entry-timing`: present but secondary in this strict sample.
- Interpretation: feature-gate is not blocked by one threshold defect. Exit/state remains the first repair direction, while source quality and cushion remain hard promotion blockers.

## Feature-Gate Exit-Watch Alignment

- Added `probe_v28_feature_gate_exit_watch_alignment_audit.py` and `v28_feature_gate_exit_watch_alignment_audit_latest.md` to join the seven selected-side live exit mismatches to the frozen feature-gate exit-watch shapes.
- The seven mismatch markets have settlement theory `+161c`, live selected-side PnL `-456c`, and a `+617c` swing.
- Value-only watch catches `2/7` mismatch markets. This is narrower and better aligned with preserving probability-reduce/collapse loss-control behavior.
- High-bid watch catches `7/7` mismatch markets, but `5/7` are probability-reduce or probability-collapse rows, so the watch has broad loss-control risk and needs strict forward proof before trust.
- Delayed-recheck watch catches `6/7` mismatch markets; it rejects the `KXBTC15M-26MAY062015-15` probability-reduce case because recheck bid falls to `53c`, which is exactly the intended path-survival guard behavior.
- Strict status remains zero-row for all three aligned watches: exit-bid, delayed-recheck, and value-exit watches all have `0` strict post-freeze rows/suppressions, so this alignment is diagnostic only.

## Delayed-Recheck Survival Tradeoff

- Added `probe_v28_feature_gate_delayed_recheck_survival_tradeoff.py` and `v28_feature_gate_delayed_recheck_survival_tradeoff_latest.md` to contrast plain high-bid suppression against the frozen delayed-recheck child.
- Plain high-bid diagnostic watch catches `14` rows for `+2676c` delta, but path risk is severe: adverse `10/25/50c` rows are `5/4/3`, with worst post-exit bid excursion `-56c`.
- Frozen delayed-recheck child keeps `11` rows for `+2272c` delta and rejects `3` rows carrying `+404c` of high-bid diagnostic recovery.
- The rejected rows are not obviously mistakes: they include `2` probability-reduce rows and `1` value-over-hold row, with adverse `10/25/50c` counts `3/2/2` and worst excursion `-56c`.
- Delayed recheck still does not solve all path risk; among kept rows it still has adverse `10/25/50c` counts `2/2/1` and a worst kept excursion of `-55c`.
- Interpretation: delayed recheck is a better-shaped frozen watch than plain high-bid suppression, but it remains watch-only and still needs strict post-freeze proof plus possible future disaster-guard work if adverse paths repeat.

## Feature-Gate Delayed-Recheck Disaster Guard Scan

- Added `probe_v28_feature_gate_delayed_recheck_disaster_guard.py` and `v28_feature_gate_delayed_recheck_disaster_guard_latest.md`.
- Base delayed-recheck diagnostic row has `11` suppressed rows, `+2272c` delta, and adverse `25/50c` rows `2/1`.
- Best conservative diagnostic guard is `reject_value_over_hold_recheck_bid_lte_82`: it removes all adverse `25/50c` rows, keeps `8` suppressions, and retains `+1528c`, but gives up `744c` of diagnostic recovery.
- Lower-cost guards such as `reject_recheck_bid_lte_60`, `reject_window_drop_gte_8`, and value-over-hold equivalents only give up `176c`, but still leave `1` adverse 25c row and `1` adverse 50c row.
- Broader generic guards remove adverse paths only by rejecting too many reduce/collapse/value rows and giving up large recovery.
- Interpretation: do not freeze an additional feature-gate disaster guard from this diagnostic scan. Keep the existing delayed-recheck watch unchanged until strict post-freeze rows reveal whether the adverse-path issue repeats.

## Continuation Refresh

- Registry audit was refreshed after adding the frozen exit-bid and value-exit feature-side watches to the active special-family registry.
- Candidate registry coverage audit now checks `237` active rows against `755` tracker rows, with `0` active missing rows.
- Candidate-vs-live table now has `755` candidates, `541` positive candidates, `317` positive target-coverage candidates, and `0` live-ready candidates.
- Live-only baseline remains the refreshed `+629c` / `+$6.29` baseline used for candidate deltas.
- Broader process check shows live bot Python PIDs `19012` and `3356`, shadow bot wrapper PowerShell PID `15836`, and shadow status loop PowerShell PID `18676`.
- Fresh shadow observation availability at `2026-05-07T07:39:17Z` shows `20,745` shadow events and `140` reconstructed shadow trades.
- The frozen feature-gate exit-bid watch still has `0` strict post-birth rows after refreshing alignment, hold-counterfactual, separator, watch, tracker, registry audit, candidate-vs-live table, goal audit, and current-direction report.
- Added a frozen value-exit feature-side guard watch from the new contrast evidence. Diagnostic guard net is `+383c` versus value-only `+327c` and current `+277c`; it suppresses `10` same-side feature-gate value exits with `10/0` suppressed W/L, but strict post-birth rows are `0`.
- Candidate registry coverage audit now checks `237` active rows against `755` tracker rows, with `0` active missing rows.
- Candidate-vs-live table now has `755` candidates, `541` positive candidates, `317` positive target-coverage candidates, and `0` live-ready candidates.
- Exit policy watch dashboard now includes the newer feature-gate value-exit, high-exit-bid, and value-exit feature-side guard watches.
- Current exit dashboard status counts after adding the strict v3 common-clock window: `2` blocked by loss-control cost, `5` blocked by non-positive net, `2` positive but under sample, `3` waiting for post-freeze rows, and `1` waiting for suppressed exits.
- The only active positive strict exit watch is `common_clock_strict_forward_v2`: `25` settled, `7` suppressions, `+34c` candidate net, `+58c` delta, but still blocked by `<30` settled rows, `<30` suppressions, and full-loss cushion `<3`.
- The second positive strict exit watch is `common_clock_strict_forward_v3`: `13` settled, `3` suppressions, `+58c` candidate net, `+30c` delta, also blocked by sample, suppression density, and cushion.
- Added `v28_exit_policy_maturity_runway_latest.md`; it ranks `common_clock_strict_forward_v2` as closest to review, needing `5` settled rows, `23` suppressions, and `266c` more net cushion. The main strict-exit failure counts are `suppression_density_immature=3`, `strict_net_not_positive=5`, `strict_forward_denominator_missing=3`, and `exit_policy_loss_control_harm=2`.
- Added `v28_exit_common_clock_positive_drilldown_latest.md` to explain the two positive strict common-clock lanes. V2 has `7/0` helpful/harmful suppressions, `8` candidate losses, and `12` unsuppressed winner clips; V3 has `3/0` helpful/harmful suppressions, `4` candidate losses, and `7` unsuppressed winner clips.
- The drilldown says the positive common-clock signal is physically plausible but immature: it suppresses high-p-hold/value-over-hold exits that later settled as winners, while the remaining losses are mostly low-p-hold or probability-reduce cases the current policy does not touch.
- The residual separator scan is mixed, not promotion evidence. V2's broad `p_hold_lt_75` residual suppressor would add `+352c` but includes `2` harmful rows; V3's cleanest tiny selector is `exitable_70_79` at `2/0` helpful/harmful for `+98c`, while broader low-p-hold selectors already turn negative.
- Newer feature/value guards remain denominator waits: feature-gate value exit `0` post-birth rows, high-exit-bid suppression `0` post-birth rows, value-exit feature-side guard `0` post-birth rows.
- Goal completion remains `Achieved: False`; no candidate is live-ready.
- Fresh read-only live score remains `+629c` / `+$6.29`, `547` entries, `451` completed round trips, W/L by sign `256/284`, and `0` open positions.
- Fresh process inventory saw live bot Python PIDs `19012` and `3356`; the active shadow status loop appears to be PowerShell PID `28868`. A second matching PowerShell row was the inspection command itself.
- Added frozen exit common-clock residual child watch `parent_loss_guard_plus_residual_exit70_79`, frozen at `2026-05-07T08:06:06.929631+00:00`. It starts from the common-clock parent and only tests residual exits priced 70-79c after the parent does not suppress.
- Diagnostic-only context is clean but tiny: v2 common-clock context has `3/0` helpful/harmful child suppressions for `+150c`; v3 context has `2/0` for `+98c`. Strict `post_child_birth` rows are `0`, so this is watch-only.
- Candidate tracker now has `758` lanes, registry audit checks `238` active rows with `0` missing, candidate-vs-live still has `0` live-ready rows, and the exit dashboard counts the residual child under `waiting_no_post_freeze_rows`.
- Exit dashboard now also includes the frozen `soft_frontier_midprice_delayed_recheck_exit` lane. It is diagnostically strong (`54` joined rows, `30` suppressions, `28/0` helpful/harmful, `+378c` weighted delta, reconstructed share `16.67%`) but strict post-birth rows remain `0`.
- Registry audit now checks `239` active rows with `0` missing after adding the soft-frontier delayed-recheck post-birth lane. Exit maturity runway failure counts now include `strict_forward_denominator_missing=5`.
- Added `v28_exit_watch_denominator_audit_latest.md` to separate zero-row strict watches from possible collection problems. It finds `0` potential join/filter denominator issues.
- The latest generic base exit timestamp is `2026-05-07T04:25:51.448398+00:00`, which is before the newest zero-row watch freezes, so `common_clock_residual_child_exit70_79`, `soft_frontier_midprice_delayed_recheck_exit`, `feature_gate_value_exit`, `feature_gate_exit_bid_suppression`, and `value_exit_feature_side_guard` look time/recency-limited rather than broken.
- The denominator audit also shows `reduce_depth_gate`, `reduce_loss_control_refinement`, and `reduce_side_geometry` are collecting denominator rows but not firing suppressions, so those are rule-density problems rather than feed/wiring problems.
- Added `v28_exit_reduce_no_fire_audit_latest.md` to explain those no-fire reduce watches. Depth gate has only `1` probability-reduce row in `27` post-birth rows; the strict `p_hold>=0.79` rule fires `0` times, and loosening to `p_hold>=0.75` would fire once for `-120c`, adding loss-control harm.
- Reduce geometry saw `2` probability-reduce rows and `2` base p-hold candidates, but `0` geometry suppressions; rejected base opportunity was `-74c`. This supports keeping reduce watches running but not widening them while cleaner exit watches collect strict rows.

## Live Baseline Refreshed

- Strategy: `live_mushroom_v28_size2`
- Live-only net: `+629c` / `+$6.29`
- Entries: `547`
- Completed round trips: `451`
- W/L by sign: `256/284`
- Open positions: `0`

Process check shows live bot Python PIDs `19012` and `3356`, shadow bot wrapper PowerShell PID `15836`, and shadow status loop PowerShell PID `18676`.

## Current Gate State

- Goal completion audit remains `Achieved: False`.
- Candidate-vs-live table now has `755` candidates, `541` positive candidates, `317` positive target-coverage candidates, and `0` live-ready candidates.
- The current direction remains: validate exits/state first, keep feature-gate entry branches in frozen forward watch, and do not promote diagnostic rows.

## Feature-Gate Post-Freeze Update

The boundary-clock feature-gate post-freeze lane has enough settled rows for a first strict read, but it is not promotable.

- Best post-freeze entry row: `post_feature_freeze_entry_raw03_recross70_abs075`
- Settled: `37`
- Coverage: `75.51%`
- Net: `+275c`
- W/L: `22/15`
- Reconstructed share: `43.24%`
- Full-loss cushion: `2`
- Delta versus refreshed live-only baseline: `-354c`
- Blockers: `reconstructed_share_gt_35pct`, `full_loss_cushion_lt_3`

The nearest raw05 runway remains watch-only:

- Candidate: `post_feature_freeze_entry_raw05_recross60_abs085`
- Denominator: `49`
- Selected entries: `33`
- Settled / pending selected: `33 / 0`
- Current selected net: `+275c`
- Reconstructed share: `36.36%`
- Needs `4` more selected entries for 75% coverage.
- Needs `2` additional clean approved selected rows for the source gate, assuming no new rejected selected rows.
- Needs `25c` more for a three-full-loss cushion.
- Omitted rows are all `rejected_actionable`, currently `-77c`, mostly failing `abs_d_below_min` with some `recross_above_max`.

## Outcome Linkage Correction

The linked-outcome probes were corrected to respect stored `net_cents` on compact feature-gate rows instead of recomputing PnL from partial fields. After rerun, there are no pending rows to link and the overlay matches the official feature-gate report:

- Best linked overlay: `post_feature_freeze_entry_raw03_recross70_abs075`
- Linked settled/net: `37 / +275c`
- Coverage: `75.51%`
- Full-loss cushion: `2`
- Blockers: `reconstructed_share_gt_35pct`, `full_loss_cushion_lt_3`
- Linked-overlay live-ready rows: `0`

The corrected source-runway split for the same broad row:

- Approved-source slice: `21` entries, `19/2`, `+240c`
- Rejected-actionable slice: `16` entries, `3/13`, `+35c`
- Clean approved selected rows needed to dilute source share under 35%, assuming no new rejected selected rows: `9`

Interpretation: the approved slice is strong, but the broad coverage row still relies on too many rejected-actionable markets and lacks enough cushion. This is watch evidence, not promotion evidence.

## Rejected-Slice Mechanism

The rejected-actionable slice is not uniformly bad on dollars because three tail wins add `+106c`, but it is loss-frequent and fragile:

- Rejected slice: `16` rows, `3/13`, `+35c`
- Rejected losses: `13` rows, `-71c`
- Rejected wins: `3` rows, `+106c`
- Worst observable loss tags: `thin_depth_lt100`, `moderate_boundary_distance_65_85`, `thin_raw_edge_lt05`, `cheap_tail_ask_lt50`

The physical read is source-quality plus fragility: cheap, low-p-side rejected rows near/moderate boundary distance and thin depth produce frequent small losses, while a few tail wins keep the aggregate slightly positive. That argues for continuous exposure shrink or source-risk penalties, not a hard threshold relaxation or source-label-only cutoff.

## Source-Risk Shrink Watch

Added a new research-only watch:

- Probe: `probe_v28_feature_gate_source_risk_shrink_watch.py`
- Report: `logs\edge_research\v28_feature_gate_source_risk_shrink_watch_latest.md`
- Watch freeze UTC: `2026-05-07T06:51:18.613633+00:00`
- Rule under watch: `raw03_recross70_abs075`
- Policy family: observable notional shrink using cheap tail, low p-side, thin depth, weak/moderate boundary distance, thin raw edge, early observation, and high recross tags.

Best diagnostic feature-window policy:

- Policy: `cheap_thin_fifth`
- Entries / denominator: `37 / 49`
- Settled: `37`
- Coverage: `75.51%`
- W/L: `22/15`
- Weighted net: `+309.4c`
- Row-source share: `43.24%`
- Exposure-source share: `34.78%`
- Full-loss cushion: `3`
- Remaining diagnostic blocker: `row_source_share_gt_35pct`

Strict post-watch rows are still `0`, so this branch is frozen watch-only. The useful finding is narrow: observable notional shrink can repair exposure share and cushion in diagnostic evidence, but it does not repair the official row-count source gate.

## Live Outcome Alignment

Added `probe_v28_feature_gate_live_outcome_alignment.py` after refreshing `score_bot_log.py` in live-only mode.

For the broad post-freeze raw03 feature-gate row:

- Candidate: `post_feature_freeze_entry_raw03_recross70_abs075`
- Theory settlement net: `+275c`
- Selected markets with live trades: `26 / 37`
- Selected markets with no live trade: `11 / 37`
- Actual live total PnL on those markets: `-264c`
- Live per-contract market-sum PnL: `+19.075c`
- Selected-side per-contract market-sum PnL: `+6.325c`
- Mismatch tags: `23` live exits before settlement, `7` theory-win/live-market-loss rows, `7` theory-win/selected-side-live-loss rows, `8` opposite-side live trades.

Interpretation: the feature-gate entry surface still has theoretical signal, but live execution/exits/state dilute most of it on the same markets. This pushes the next repair question toward exit/state and execution alignment, not just entry threshold work.

## Live Exit Mismatch Drilldown

Added `probe_v28_feature_gate_live_exit_mismatch_drilldown.py` to classify the seven `theory_win_selected_side_live_loss` markets from the broad raw03 feature-gate row.

- Theory settlement net on these seven markets: `+161c`
- Live selected-side PnL on the same markets: `-456c`
- All `7 / 7` classified as `exit_policy_error`, `same_side_state_churn`, `exited_before_settlement`, and `theory_win_selected_live_loss`.
- `4 / 7` involved `mushroom_v28_probability_reduce` clipped winners.
- `2 / 7` involved `mushroom_v28_exit_value_over_hold` clipped winners.
- `1 / 7` also had opposite-side state churn.

Interpretation: this is the cleanest current failure-mode evidence. The feature-gate selection often picked the eventual settlement side, but live v28 exited or churned the same side before settlement and converted theoretical winners into live selected-side losses. That supports exit/state repair first; it does not justify promoting the entry surface or widening entry thresholds.

## Exit Hold Counterfactual

Added `probe_v28_feature_gate_live_exit_hold_counterfactual.py` to measure all broad raw03 feature-gate selected-side live trades, not only the seven worst mismatches.

- Selected-side live traded markets: `20 / 37`
- Actual selected-side live PnL: `-140c`
- Counterfactual hold-to-settlement PnL on the same live selected-side entries: `+1006c`
- Exit/state delta versus settlement hold: `-1146c`
- Settlement-winner rows: live `+252c` versus hold `+2928c`, delta `-2676c`
- Settlement-loser rows: live `-392c` versus hold `-1922c`, delta `+1530c`
- Exit hurt/help markets: `14 / 3`

Interpretation: no-exit is not the answer because exits did save large losses on settlement losers. But the current exit/state layer clipped substantially more winner value than it saved, so the useful repair target is selective exit suppression or delayed confirmation on likely transient winner clips.

## Exit Suppression Separator

Added `probe_v28_feature_gate_exit_suppression_separator.py` to search simple observable separators between exits that clipped winners and exits that saved true loser damage.

- All-exit suppression on selected-side live rows would be `+1146c`, but this mixes `14` helpful-to-suppress markets with `3` harmful-to-suppress loss-control markets.
- Best deployable-like observable separator in the retrospective sample: `exit_bid_min >= 60`.
- That selector covers `14` markets, helpful/harmful `14 / 0`, and `+2676c` suppression delta.
- Best oracle/diagnostic separator is `theory_net_cents >= 4`, which is settlement-derived and not actionable.

Interpretation: the observable clue is high exit-bid winner clipping. This is not promotion evidence and not a live rule; it is a candidate shape for a future frozen watch that must be judged only on rows after its own freeze.

## Frozen Exit-Bid Watch

Added `probe_v28_feature_gate_exit_bid_suppression_watch.py` to freeze the high-exit-bid clip shape as a strict forward watch.

- Freeze UTC: `2026-05-07T07:32:00.852069+00:00`
- Candidate: `feature_gate_exit_bid_min_ge_60_suppress`
- Diagnostic lane: `20` rows, `14` suppressions, `+2676c` delta, helpful/harmful `14 / 0`
- Post-birth lane: `0` rows, `0` suppressions, `0c` delta
- Post-birth blockers: `settled_lt_30`, `suppressed_decisions_lt_30`, `net_not_positive`, `delta_not_positive`, `full_loss_cushion_lt_3`

Interpretation: this converts a promising retrospective separator into a proper watch. It has no strict forward evidence yet, so it is not promotable and should only be evaluated on rows after the freeze timestamp.

## Exit-State Watch Update

Exit/state remains the lead research direction.

- Current-direction report favors exit-policy validation first.
- The strongest diagnostic exit stacks are still blocked by strict post-freeze joined-row and suppression-count requirements.
- Strict rows remain immature; no exit stack is live-ready.
- Exit dashboard positive active watch: `common_clock_strict_forward_v2`.
- Closest common-clock row: `loss_guard_value_p85_reduce_p79_gap0`, `25` settled, `7` suppressed decisions, `+34c` candidate net, `+58c` delta.
- Remaining common-clock needs: `5` settled rows, `23` suppressed decisions, and `266c` additional cushion.
- Depth-gate post-birth has `27` settled but `0` suppressed exits and `0c` delta, so it is still a no-op watch.
- Added `probe_v28_exit_common_clock_suppression_scarcity.py` to test whether small strict-window relaxations can solve the suppression-count problem.
- Best suppression-scarcity audit policy: `v1_like_on_v2_clock`, still only `25` settled, `7` suppressions, `+34c` candidate net, `+58c` delta, `0c` loss cost, cushion `0`.
- V2 control itself suppresses `1` row for `+22c` delta. The current exit blocker is immature suppression density and cushion, not observed harmful suppressions.
- Added `probe_v28_exit_common_clock_positive_drilldown.py` for row-level failure-mode inspection of the positive strict common-clock lanes.
- V2 drilldown: `7` suppressed exits were all helpful, but `8` candidate losses remain and `12` unsuppressed winner clips show the policy is under-catching likely transient winner exits.
- V3 drilldown: `3` suppressed exits were all helpful, with `4` candidate losses and `7` unsuppressed winner clips. It is cleaner but even less mature.
- The recurring mechanism is not a hard proof of a deployable rule yet: high p-hold/value-over-hold suppressions look good, while low-p-hold/probability-reduce losses remain the unresolved exit-policy failure mode.
- Residual separator scan: V2's best simple residual selector is positive but not loss-clean (`p_hold_lt_75`, `11/2` helpful/harmful, `+352c`), while V3 only has tiny clean residual pockets (`exitable_70_79`, `2/0`, `+98c`). This argues for continued observation or a narrower child watch, not immediate rule broadening.
- Created the narrower frozen child watch from that conclusion: `probe_v28_frozen_exit_common_clock_residual_child_watch.py`. It is tracked in the candidate table, registry audit, exit dashboard, and maturity runway, but has no post-birth evidence yet.
- Added the already-frozen `v28_frozen_soft_frontier_midprice_delayed_recheck_exit_latest.json` lane to the exit dashboard and active registry audit. It remains the top diagnostic candidate in candidate-vs-live, but dashboard/maturity now correctly classify it as a zero-row strict denominator wait.
- Added `probe_v28_exit_watch_denominator_audit.py`. Current read: zero-row watches are too new relative to the latest base exit row; no denominator wiring issue is visible yet.
- Added `probe_v28_exit_reduce_no_fire_audit.py`. Current read: reduce-watch no-fire is sparse opportunity plus loss-control protection, not an obvious missed profitable relaxation.

## Guarded Feature-Gate Coverage Repair

Added and refreshed `probe_v28_feature_gate_guarded_coverage_repair_scan.py`, then wired it into `probe_v28_current_direction_decision.py`.

- The guarded raw03 feature-gate base now has denominator `58`.
- Entry base guarded raw03: `42` entries, `72.41%` coverage, `+254c`, W/L `23/11`, reconstructed share `35.7%`, full-loss cushion `2`.
- Bridge base guarded raw03: `42` entries, `72.41%` coverage, `+308c`, W/L `24/11`, reconstructed share `35.7%`, full-loss cushion `3`.
- Base blockers: `coverage_too_low`, `reconstructed_share_gt_35pct`, and `does_not_beat_refreshed_live_baseline`; the entry base also fails `full_loss_cushion_lt_3`.
- Best one-row repair adds `KXBTC15M-26MAY061715-15 no`, source `rejected_actionable`, net `+93c`.
- Best one-row entry total: `43` entries, `74.14%` coverage, `+347c`, delta vs refreshed live baseline `-502c`, reconstructed share `37.2%`, cushion `3`.
- Best one-row bridge total: `43` entries, `74.14%` coverage, `+401c`, delta vs refreshed live baseline `-448c`, reconstructed share `37.2%`, cushion `4`.
- No one-row observable widening clears the 75% coverage gate after the denominator advanced to `58`; at least two added markets are required.

Interpretation: the same-market high-ask displacement guard is useful evidence because it improves PnL/source share without live changes, but it does not solve the broad-entry promotion problem. The easiest coverage repairs are still rejected-actionable rows, so simple threshold widening remains blocked by coverage, source quality, and live-baseline gates.

## Exit Watch Refresh and False-Hold Overlap

Refreshed the active exit/state watch stack and promotion gate:

- Refreshed top exit source watches: `probe_v28_frozen_soft_frontier_midprice_delayed_recheck_exit.py`, `probe_v28_frozen_soft_frontier_midprice_delayed_recheck_rescue.py`, `probe_v28_frozen_matched_unchanged_loss_guard_watch.py`, and `probe_v28_exit_policy_common_clock_watch.py`.
- Refreshed dashboards/gates: `probe_v28_exit_policy_watch_dashboard.py`, `probe_v28_exit_watch_denominator_audit.py`, `probe_v28_exit_dashboard_coverage_audit.py`, `probe_v28_candidate_registry_coverage_audit.py`, `probe_v28_exit_policy_maturity_runway.py`, `probe_v28_exit_watch_promotion_gate_audit.py`, and `probe_v28_current_direction_decision.py`.
- Exit promotion pass count remains `0`.
- Closest positive strict watch by maturity is `book_gap_loss_guard`: `27` settled, `8` suppressed, `+2c` candidate net, `+76c` delta, still needing `3` rows, `22` suppressions, and `298c` cushion.
- Promotion-gate closest watch remains `common_clock_strict_forward_v2`: `18` settled, `5` suppressions, `+44c` net, `+66c` delta, still blocked by sample, suppression density, and cushion.
- False-hold guardrail remains active: strict harmful suppressions `10` for `-1440c`.

Added `probe_v28_exit_false_hold_rule_overlap_audit.py` to separate actual current strict harm from prior false-hold mechanism risk.

- `book_gap_suppression`: observed current strict harm, `24` suppressions, `4` harmful, net suppression delta `-165c`, harm `-606c`.
- `dual_exit_book_gap_else_reduce`: observed current strict harm, `8` suppressions, `2` harmful, net suppression delta `-242c`, harm `-300c`.
- `book_gap_loss_guard`: no current harmful strict suppressions so far, `8 / 8` helpful suppressions, `+76c` suppression delta, but still blocked by prior false-hold risk plus immature rows/suppression density.
- `book_gap_loss_guard_v3`: current strict suppressions are clean but tiny, `2 / 2` helpful, `+24c`; it remains a watch-only immature child.

Interpretation: the false-hold blocker should not be collapsed into one generic "bad exit rule" label. The broad book-gap/dual-exit variants have observed current harm and should stay rejected. The loss-guarded book-gap variants are cleaner in their current strict samples, but they are not promotable because suppression density, sample size, cushion, and prior false-hold risk are still unresolved.

## Loss-Guard Mechanism Audit

Added `probe_v28_exit_loss_guard_mechanism_audit.py` and wired it into `probe_v28_current_direction_decision.py`.

- Broad `book_gap_suppression` has `55` strict rows, `24` suppressions, `19` helpful and `4` harmful, with net suppression delta `-165c` and harmful suppression cost `-606c`.
- `book_gap_loss_guard` has `28` strict rows, `8` suppressions, `8` helpful and `0` harmful, with suppression delta `+76c`.
- `book_gap_loss_guard_v3` has `15` strict rows, `2` suppressions, `2` helpful and `0` harmful, with suppression delta `+24c`.
- The known rich false-hold loser `KXBTC15M-26MAY062015-15 yes` was avoided by `book_gap_loss_guard` because both `value_p_hold_below_floor` and `value_gap_below_floor` blocked suppression.
- The known reduce false-hold loser `KXBTC15M-26MAY062130-30 no` was avoided because `reduce_p_hold_below_floor` blocked suppression.
- The clean helpful `book_gap_loss_guard` suppressions are still sparse, and the smallest value p-hold margin is only about `+0.0107`, so this is not a robust promotion sample yet.

Interpretation: the loss guard now has a concrete physical explanation, not just green PnL. It separates likely clipped-winner rich exits from mid-confidence/rich false holds using observable p-hold and book-gap floors. That makes it worth continued forward monitoring, but not live promotion: it still lacks row count, suppression count, cushion, and enough evidence that the threshold margin is durable.

## Loss-Guard Threshold Margin Stress

Added `probe_v28_exit_loss_guard_threshold_margin_stress.py` and wired it into `probe_v28_current_direction_decision.py`.

- Stress is research-only and replays stricter thresholds on already-frozen strict rows; it does not create or modify a live/watch rule.
- `book_gap_loss_guard` as frozen: `28` rows, `8` suppressions, `8` helpful, `0` harmful, candidate net `+22c`, delta `+76c`, cushion `0`.
- `book_gap_loss_guard` with value p-hold floor `0.86`: unchanged at `+22c` / `+76c`.
- `book_gap_loss_guard` with value p-hold floor `0.88`: drops one suppression, candidate net falls to `0c`, delta `+54c`, cushion `0`.
- `book_gap_loss_guard` with value p-hold floor `0.90`: drops three suppressions, candidate net falls to `-34c`, delta `+20c`.
- `book_gap_loss_guard_v3` as frozen: `15` rows, `2` suppressions, `2` helpful, `0` harmful, candidate net `+108c`, delta `+24c`, cushion `1`.
- `book_gap_loss_guard_v3` remains unchanged for extreme p-hold floors `0.96` and `0.97`, but tightening the fair-drawdown allowance to `0c` leaves only `1` suppression and `+2c` delta.

Interpretation: the guarded book-gap exit idea has a valid physical mechanism, but the current strict evidence is margin-thin. V1 is clean but depends on a small number of value-over-hold suppressions near the threshold; V3 is safer but too small to carry a promotion case. Keep collecting strict rows rather than freezing a new child or relaxing gates.

## Loss-Guard Path-Risk Audit

Added `probe_v28_exit_loss_guard_path_risk_audit.py` and wired it into `probe_v28_current_direction_decision.py`.

- The audit is research-only and uses the existing `worst_post_exit_hold_mark_cents` path proxy from frozen watch rows; it does not touch live logic, orders, or process state.
- `book_gap_loss_guard`: `28` strict rows, `8` suppressions, `+76c` suppression delta, worst adverse mark versus skipped exit `-24c`, average adverse mark `-6c`.
- `book_gap_loss_guard`: `2` rows required a `10c+` adverse mark after the skipped exit, `0` rows required `25c+` or `50c+` adverse survival, and `1` row printed a below-zero worst mark (`-4c`).
- `book_gap_loss_guard_v3`: `15` strict rows, `2` suppressions, `+24c` suppression delta, no adverse mark worse than the skipped-exit mark, and worst absolute mark `10c`.
- Current blockers remain sample/suppression scarcity. V1 also carries a path-survival blocker from the below-zero mark; V3 has cleaner path behavior but too little evidence.

Interpretation: path risk does not kill the loss-guard idea the way it killed broad high-exit-bid suppression, because there are no `25c+` adverse excursions in the current loss-guard sample. It does keep V1 from being a clean promotion story: the positive settlement delta required tolerating two meaningful adverse moves and one below-zero mark. V3 is physically cleaner on path risk, but with only two suppressions it is still a watch-only child.

## Feature-Gate Post-Freeze Promotion Gap Refresh

Refreshed the live-only baseline with `score_bot_log.py`, then updated `probe_v28_feature_gate_promotion_gap_audit.py` so it reads the current `v28_boundary_clock_feature_gate_candidate_latest.json` rows directly instead of relying on older linked-source snapshots. Wired the refreshed audit into `probe_v28_current_direction_decision.py`.

- Refreshed live-only baseline: `+797c`, `573` entries, `471` completed round trips, `2` open positions.
- The feature-gate branch is no longer a zero-row post-freeze wait: current post-feature-freeze entry variants have `26-43` settled rows depending on rule.
- Best current post-freeze entry by blocker ordering: `post_feature_freeze_entry_raw05_recross60_abs085`, `37` settled, `61.67%` coverage, `+345c`, W/L `25/12`, reconstructed share `35.14%`, cushion `3`, delta versus live `-452c`.
- Broadest current post-freeze entry: `post_feature_freeze_entry_raw03_recross70_abs075`, `43` settled, `71.67%` coverage, `+284c`, W/L `27/16`, reconstructed share `44.19%`, cushion `2`, delta versus live `-513c`.
- Current selected-row source attribution: raw03 gets `+302c` from approved-entry rows and `-18c` from rejected-actionable rows; raw05 gets `+281c` approved and `+64c` rejected-actionable, but misses coverage by `8` markets.
- Broad raw03 needs only `2` more selected markets to reach `75%` coverage, but would need `12` clean approved additions to satisfy the `<=35%` reconstructed-share cap if all else stayed constant.
- Refreshed source feasibility bound: current denominator `60`, approved markets available `28`, required markets for `75%` coverage `45`. Even the best possible source-clean selection under the `<=35%` reconstructed-share gate can cover only `71.67%`; `75%` coverage would require at least `37.78%` reconstructed/rejected rows.
- The ask-floor clean lane remains source-clean but too narrow: `30` settled, `50.00%` coverage, `+212c`, reconstructed share `6.67%`, cushion `2`, delta versus live `-585c`.

Interpretation: post-freeze evidence is now real enough to evaluate, and it is positive after fees, but it is not promotion-quality. The active failure is source quality plus live-baseline underperformance, not row availability. Coverage can be solved mechanically, but the broad rows that buy coverage are still source-fragile; the clean ask-floor core is not broad enough and does not have enough cushion. Under the current source-label supply, the broad 75% coverage gate and hard <=35% row-source gate are mathematically incompatible for this feature-gate pool unless future approved rows arrive or the research switches to a separate weighted-exposure source-risk argument.

## Value/Reduce-Depth Composite Suppressed-Loser Audit

Added `probe_v28_exit_value_reduce_depth_suppressed_loser_audit.py` and wired it into `probe_v28_current_direction_decision.py`.

- The audit is research-only and reads `v28_frozen_exit_value_reduce_depth_composite_latest.json`; it does not change exit logic or live behavior.
- The value/reduce-depth composite remains diagnostically important for loss-count churn, but looser p75 reduce-depth variants have suppressed losers.
- Total suppressed-loser variant/lane hits: `8`; post-composite-birth hits: `4`; unique suppressed-loser markets: `2`.
- Repeated harmful reduce row: `KXBTC15M-26MAY062130-30 no`, `probability_reduce`, `p_hold=0.768407`, `entry_depth=24`, positive book gap `0.168407`, positive fair drawdown `6.159c`, already negative at exit `-32c`, hold-to-settlement `-152c`, suppression delta `-120c`.
- Harmful value-only row: `KXBTC15M-26MAY062015-15 yes`, `value_over_hold`, `p_hold=0.812359`, negative book gap `-0.087641`, current `+8c`, hold `-172c`, suppression delta `-180c`.

Interpretation: the composite's p79 reduce floor is not cosmetic tuning. It is the guard that avoids the current repeated p75 probability-reduce false hold. Broad p75 reduce-depth suppression should stay rejected until a strict child proves it can avoid already-negative, p_hold 0.75-0.79 reduce exits that look superficially hold-favorable by book gap/fair drawdown but continue to fail.

## Reduce Current-Floor Guard Frontier

Added `probe_v28_exit_reduce_current_floor_guard_frontier.py` and wired it into `probe_v28_current_direction_decision.py`.

- The frontier is research-only and does not freeze a child or alter live/watch logic.
- Tested whether an observable current-exit floor can rescue p75/p77 reduce-depth suppression by excluding already-negative reduce exits.
- Expanded same-surface threshold controls after the first run: `v2_reduce_p78_depth384` is now the best diagnostic variant, `102` settled, candidate `+750c`, delta `+389c`, `9` suppressions, value/reduce `2/7`, suppressed W/L `9/0`, no loss-control cost.
- Diagnostic control `v2_reduce_p79_depth384`: `102` settled, candidate `+698c`, delta `+337c`, `8` suppressions, value/reduce `2/6`, suppressed W/L `8/0`, no loss-control cost.
- Diagnostic `v2_reduce_p75_depth384_current_ge_0`: no suppressed losers, but only `2` suppressions, value/reduce `2/0`, delta `+34c`; it removes the useful reduce-recovery population along with the false hold.
- Diagnostic `v2_reduce_p75_depth384_current_ge_minus10`: `6` suppressions, value/reduce `2/4`, suppressed W/L `6/0`, delta `+239c`; it also throws away useful negative-at-exit reduce recoveries.
- Post-composite-birth all guarded variants remain under-sample: `24` settled, `1` suppression, candidate `0c`, delta `+22c`.

Interpretation: a simple current-exit floor is too blunt. The false hold was already negative, but several useful diagnostic reduce suppressions were also negative at exit and recovered. The p78/p79 band is the real mechanism frontier: p78 adds one clean diagnostic recovery versus p79, while p75 reopens the known false-hold loser. Because the separating margin between `0.768` false hold and `0.78` recovery is thin, and post-birth reduce opportunities are still absent, do not freeze a current-floor child or p78 child from this evidence. Keep p79 as the safer control/watch lane and let strict rows decide whether p78 is real.

## Feature-Side Guard Reporting Fix

Refreshed the live-only baseline and corrected the frozen value-exit feature-side guard report so parent value-only suppressions are no longer mixed with actual feature-side-guard suppressions.

- Refreshed live-only baseline: `+895c`, `574` entries, `471` completed round trips, `1` open position.
- Patched `probe_v28_value_exit_feature_gate_contrast.py` to carry an explicit `feature_side_guard_suppressed` row flag.
- Patched `probe_v28_frozen_value_exit_feature_side_guard.py` so its `suppressed`, `suppressed_exits`, `suppressed_winners`, `suppressed_losers`, and `suppressed_loser_cost_cents` fields count only exits actually suppressed by the feature-side guard.
- The report now preserves separate parent diagnostics as `value_only_suppressed_*` fields.
- Diagnostic pre-freeze context: `54` rows, current `-33c`, parent value-only `-83c`, guarded `+17c`, guarded suppressions `5/0`, guarded suppressed-loser cost `0c`.
- The previously confusing `-180c` suppressed-loser cost is now correctly attributed to the parent value-only rule: `15` value-only suppressions, `1` value-only suppressed loser, value-only loser cost `-180c`.
- Post feature-side-guard birth remains immature: `1` row, `1` guarded suppression, guarded net `+36c`, no guarded suppressed losers, blockers `settled_lt_30`, `full_loss_cushion_lt_3`, `exit_overlap_only`, and `not_live_bot_logic`.
- Refreshed downstream readers: `probe_v28_exit_policy_watch_dashboard.py`, `probe_v28_candidate_pnl_tracker.py`, `probe_v28_current_direction_decision.py`, and `probe_v28_candidate_vs_live_table.py`.

Interpretation: the feature-side guard did filter the known parent value-only false hold in the diagnostic context; the guard itself has not created a suppressed loser in this sample. That is useful mechanism evidence, but it is still watch-only because strict post-birth evidence is only one row and the lane is exit-overlap research, not live bot logic.

## Matched-Unchanged Exit Loss Refresh

Refreshed the canonical matched-unchanged loss separator and frozen guard watch, then refreshed the exit dashboard, candidate tracker, next-action triage, and current-direction report.

- `probe_v28_matched_unchanged_loss_separator.py` now sees `26` matched-unchanged loss rows, split `17/7/2` hold-helpful/hold-harmful/flat.
- All-row hold-to-settlement delta is `+566c`, but broad hold suppression is still unsafe because the `7` harmful rows are true FV/entry failures.
- The current diagnostic best shifted to `abs_d_sigma >= 0.913273 AND exit_cents <= 53`, selecting `4` rows for `+522c` with `4/0` helpful/harmful. This is diagnostic only and should not replace the already frozen watch rule.
- The frozen matched-unchanged guard watch remains anchored at `2026-05-07T09:30:07.471830+00:00`, with rule `abs_d_sigma <= 0.888798`, `eligible_depth <= 326.6`, `exit_cents >= 51`, `exit_p_hold >= 0.718799`.
- Post-freeze watch evidence is still just `3` scored rows, `0` selected rows, `0c` delta, and blockers `settled_lt_30`, `suppressed_decisions_lt_30`, `delta_not_positive`, and `full_loss_cushion_lt_3`.
- The refreshed exit dashboard now reports `matched_unchanged_loss_guard_watch` as `waiting_rule_has_not_fired`, `3` settled/scored rows, `0` suppressions, current/candidate `90c/90c`.

Interpretation: matched-unchanged loss repair remains one of the right physical directions for reducing loss-count churn, but the rule is still a strict-row wait. The diagnostic surface is unstable as new loss rows arrive, so do not refreeze from the updated leaderboard; keep the frozen guard collecting and use the harmful rows as guardrails against broad exit suppression.

## Matched-Unchanged Guard Opportunity Audit

Added `probe_v28_matched_unchanged_loss_guard_opportunity.py` and wired its output into `probe_v28_next_action_triage.py`.

- The audit is research-only and reads the frozen matched-unchanged guard rule plus common-clock scored rows; it does not change live logic.
- Current post-freeze scored rows: `4`.
- Selected rows under the frozen rule: `0`.
- Near-miss rows: `3`, with combined hold delta `+66c`.
- Fail reasons: `abs_d_sigma_above_max=4`, `eligible_depth_above_max=4`, `missing_exit_cents=1`, `missing_exit_p_hold=1`.
- The three near misses all failed both the abs-distance ceiling and eligible-depth ceiling, so the watch is not failing on profitability yet; it simply has not fired.
- Refreshed the frozen matched-unchanged watch, exit dashboard, candidate tracker, next-action triage, and current-direction report after adding the opportunity audit.

Interpretation: do not relax the frozen rule from these near misses. They are favorable after the fact, but widening both abs-distance and depth would be a new rule and would reopen false-hold risk without its own freeze. Keep collecting strict post-freeze rows and treat the near misses as denominator context only.

## Exit Clip Separator Refresh

Refreshed the frozen exit-clip separator watch and replay, then refreshed the exit dashboard, candidate tracker, next-action triage, and current-direction report.

- Frozen watch rule remains `fair_drawdown_cents <= 10` and `p_hold >= 0.60`, frozen at `2026-05-07T04:04:23.876080+00:00`.
- Current post-freeze matched-unchanged denominator: `1` row.
- Selected/suppressed rows under the frozen rule: `0`.
- Known helpful/harmful/unknown under the frozen rule: `0/0/0`, with `0c` known hold delta.
- The only denominator row, `KXBTC15M-26MAY070015-15`, was rejected by both `p_hold_below_floor` and `fair_drawdown_above_ceiling`; it would have been a harmful hold (`actual -2c`, hold `-140c`, delta `-138c`) and is tagged as an `fv_or_entry_timing_error`.
- Full replay of the frozen exit-reduce denominator is stronger diagnostically after refresh: `56` rows, current W/L `27/27`, candidate W/L `44/11`, current/candidate `+123c/+1056c`, delta `+933c`, `18` suppressed, and `16` fewer losses.
- Replay remains mechanism evidence only because it is not the clip-watch forward window, has only `18` suppressed decisions, and still contains `1` suppressed loser.
- Strict post-watch replay has only `3` rows, `0` suppressions, and `0c` delta, with blockers `settled_lt_30`, `suppressed_decisions_lt_30`, `full_loss_cushion_lt_3`, and `post_clip_watch_sample_pending`.
- Refreshed exit dashboard status counts are now `{'blocked_loss_control_cost': 6, 'blocked_net_not_positive': 2, 'forward_positive_under_review': 2, 'positive_but_under_sample': 7, 'waiting_no_post_freeze_rows': 3, 'waiting_no_suppressed_exits': 6, 'waiting_rule_has_not_fired': 2}`.

Interpretation: the clip separator is behaving correctly on the one fresh denominator row by rejecting a true FV/entry-timing loser that holding would have worsened. The diagnostic replay supports the physical mechanism, but the strict watch has not fired, so this stays watch-only. Do not relax the rule from the no-fire sample; keep collecting post-freeze denominator rows.

## Live Baseline And Comparison Refresh

Refreshed the live-only scorecard and candidate-vs-live table after the exit rollup refresh.

- Live-only baseline: `+1049c` / `+$10.49`.
- Entries: `577`.
- Completed round trips: `473`.
- W/L by sign: `267/302`.
- Open positions: `1`.
- Refreshed candidate-vs-live table now has `1017` candidates, `768` positive candidates, `462` positive target-coverage candidates, and `0` live-ready candidates.
- Top table rows remain diagnostic or pre-freeze/own-freeze-blocked, so they are not promotion evidence even when they beat the live baseline on PnL.
- Process inventory confirmed the live bot Python processes are still visible at PIDs `19012` and `3356`, and the research shadow/status loop is visible at PID `33800`. No live bot processes were touched.

Interpretation: the live baseline improved since the previous `+895c` refresh, which raises the comparison hurdle. The current artifact state still says no research candidate is ready for live routing.

## Boundary-Clock Feature-Gate Refresh

Refreshed the boundary-clock feature-gate candidate, source stress, approved-oracle frontier, feature contrast, candidate tracker, goal audit, current-direction report, next-action triage, and candidate-vs-live table.

- Feature-gate freeze remains `2026-05-06T16:47:25.847566+00:00`.
- Diagnostic entry best is now `diagnostic_entry_raw03_recross70_abs075`: `80` settled, `80.20%` coverage, `+711c`, W/L `58/22`, reconstructed share `0.320988`, blockers `none`.
- Diagnostic bridge best is now `diagnostic_bridge_raw03_recross70_abs075`: `78` settled, `79.80%` coverage, `+703c`, W/L `57/21`, reconstructed share `0.329114`, blockers `none`.
- Strict post-feature-freeze entry best is `post_feature_freeze_entry_raw05_recross60_abs085`: `38` settled, `62.90%` coverage, `+354c`, W/L `26/12`, reconstructed share `0.333333`, cushion `3`, blocker `coverage_too_low`.
- Strict post-feature-freeze bridge best is the same raw05 rule with the same `38` settled, `62.90%` coverage, `+354c`, W/L `26/12`, reconstructed share `0.333333`, cushion `3`, blocker `coverage_too_low`.
- Broader strict raw03 post-feature-freeze entry reaches `44` settled and `72.58%` coverage, but only `+293c`, reconstructed share `0.422222`, cushion `2`, and blockers `coverage_too_low`, `reconstructed_share_gt_35pct`, and `full_loss_cushion_lt_3`.
- Boundary-clock base source stress remains structurally blocked: `boundary_clock_repair_entry` is `75` settled, `75.25%` coverage, `-36c`, reconstructed share `0.710526`; `boundary_clock_fv_entry_bridge` is `74` settled, `75.76%` coverage, `+140c`, reconstructed share `0.813333`.

Interpretation: post-feature-freeze rows are now real, positive, and no longer a zero-row wait, but still not close to promotion. The clean-ish raw05 lane has source share and cushion, but lacks coverage and remains far below the refreshed `+1049c` live baseline. The broader raw03 lane buys coverage by reopening source quality and cushion failures. Keep this as a frozen watch and do not widen thresholds as a standalone repair.

## Middle-Core Expansion Refresh

Refreshed the middle-distance core watch, middle-core expansion bound, middle-core exit attribution, middle-core exit-guard watch, candidate tracker, goal audit, current-direction report, next-action triage, and candidate-vs-live table.

- A later live-only refresh supersedes the earlier live snapshot: current live-only baseline is now `+971c` / `+$9.71`, with `581` entries, `477` completed round trips, W/L by sign `267/306`, and `1` open position.
- The refreshed candidate-vs-live table now has `1013` candidates, `793` positive candidates, `463` positive target-coverage candidates, and `0` live-ready candidates.
- The live bot Python processes remained visible at PIDs `19012` and `3356`, and the research shadow/status loop remained visible at PID `33800`; no processes were touched.
- The middle-core expansion-bound report was generated before the final `+971c` live refresh and uses `+1049c` for its internal live-delta math. Its structural source/coverage conclusions do not depend on that live-delta field.
- Diagnostic feature-window entry middle core: `36` entries, `21` settled, W/L `18/3`, `57.14%` coverage, `+132c`, source share `0.167`; it remains under-sample, under-covered, low-cushion, and below live.
- Diagnostic feature-window bridge middle core: `36` entries, `23` settled, W/L `21/2`, `57.14%` coverage, `+184c`, source share `0.167`; it is also under-sample, under-covered, low-cushion, and below live.
- Approved-only expansion is not a repair: the only `2` omitted approved rows are both losers, `0/2` for `-142c`, and combined coverage remains only `60.32%`.
- Best source-gated reconstructed fill is still not a broad candidate: entry reaches only `73.02%` coverage and `+1003c` while staying under the 35% source gate; bridge reaches only `73.02%` coverage and `+1055c`. Both remain below the `75%` broad-entry coverage floor.
- Strict post-middle-core freeze evidence is just `1` selected row, `1/0` for `+21c`, with `50%` coverage in a denominator of `2`; it is a watch-only sample.
- Exit attribution says the diagnostic middle core still has real exit-policy upside: entry window has `22` exit-harm rows worth `+708c` if held, but also true entry/FV loser rows that exits helped.
- The middle-core exit-guard watch remains diagnostic/prefreeze or empty strict evidence: best diagnostic entry guard is `loss_guard_v3_hold_if_suppressed` at `+425c`, but strict post-guard rows are effectively empty/immature.

Interpretation: the clean middle-distance core is a useful sidecar-quality nucleus, not a broad strategy repair. There are not enough clean approved omitted rows to fill it to 75% coverage, and the available approved additions are actively negative. The only way the current pool nears broad coverage is still reconstructed/source-gated fill, which stops short of 75% and cannot satisfy promotion gates. Keep watching strict post-middle-core rows, but do not widen the low-abs/source-fragile tail.

## Exit Clip Strict Fire Refresh

Refreshed the exit-clip diagnostic, frozen exit-clip watch, replay, matched-unchanged separator/watch/opportunity, exit dashboard, candidate tracker, next-action triage, goal audit, and current-direction report.

- The frozen exit-clip separator watch remains anchored at `2026-05-07T04:04:23.876080+00:00` with rule `fair_drawdown_cents <= 10` and `p_hold >= 0.60`.
- Strict post-freeze denominator increased to `2` matched-unchanged rows.
- The frozen rule selected `1` row, `KXBTC15M-26MAY070830-30`, a value-over-hold exit-policy-cost row where actual exit was `-14c`, hold-to-settlement was `+46c`, and hold delta was `+60c`.
- Strict selected helpful/harmful/unknown is now `1/0/0`; known hold delta is `+60c`.
- The other denominator row, `KXBTC15M-26MAY070015-15`, was not selected because it missed both `p_hold` and fair-drawdown gates; its hold result is still unknown in the refreshed watch.
- The dashboard adapter in `probe_v28_exit_policy_watch_dashboard.py` was corrected so the exit-clip watch maps `known_hold_delta_cents` into `delta_vs_current_cents`, not only `candidate_net_cents`.
- After the fix, the exit dashboard reports `exit_clip_separator_watch` as `positive_but_under_sample`: `2` settled/denominator rows, `1` suppression, current/candidate/delta `0c/60c/+60c`, blockers `post_freeze_rows_lt_30` and `known_hold_delta_lt_300c`.
- The matched-unchanged guard watch remains a no-fire rule: `7` post-freeze scored rows, `0` selected, `5` near misses, with common failures `abs_d_sigma_above_max` and `eligible_depth_above_max`.
- The moving exit-clip diagnostic now sees `29` matched-unchanged rows and shifted its best diagnostic separator to `fair_drawdown_lte_12.5`, with `12/0/4` helpful/harmful/unknown and `+908c` known hold delta. This is diagnostic only and does not replace the frozen watch.

Interpretation: this is the first useful strict fire for the exit-clip separator and supports the physical mechanism that shallow drawdown plus adequate p-hold can identify clipped-winner exits. It is still not promotable: only one selected strict row, no cushion, and far below the required settled/suppression sample. Keep collecting; do not refreeze to the new diagnostic `12.5c` drawdown separator yet.

## Exit Clip Opportunity Audit

Added `probe_v28_exit_clip_separator_opportunity.py` and wired it into `probe_v28_next_action_triage.py`.

- The probe is research-only; it does not freeze a child, change the frozen rule, touch live logic, place orders, or control processes.
- It reads the frozen exit-clip state and the live loss-escape ledger to classify selected rows, near misses, threshold margins, and small hypothetical threshold variants on post-freeze rows.
- Current post-freeze denominator rows: `2`.
- Selected rows: `1`, with selected helpful/harmful/unknown `1/0/0` and selected known hold delta `+60c`.
- Near-miss rows: `1`, with near-miss helpful/harmful/unknown `0/0/1` and known hold delta `0c`.
- The near miss is `KXBTC15M-26MAY070015-15`; it missed both gates narrowly (`p_hold=0.596562` versus `0.60`, fair drawdown `10.343815c` versus `10c`) but its hold result is unknown.
- Post-freeze threshold variants show that relaxing only drawdown to `12.5c` or only p-hold to `0.55` does not add a known row; relaxing both would add the unknown near miss only. This is not evidence for a new child freeze yet.
- `probe_v28_next_action_triage.py` now includes the opportunity audit in both the `collect_exit_clip_separator_watch_rows` recommendation and a dedicated "Exit Clip Separator Opportunity" section.

Interpretation: the frozen exit-clip rule has a clean first strict fire and one near miss, but the near miss has no known positive hold outcome. The right action is still collection, not relaxation. If future near misses become known-helpful and repeat with the same narrow margins, that would justify a separately frozen child; current evidence does not.

## Current Refresh 2026-05-07 13:33 UTC

Refreshed the live-only scorecard and the central watch/scorecard stack: boundary-clock feature gate, boundary-clock source stress, approved oracle frontier, feature contrast, exit-clip diagnostic/watch/opportunity, matched-unchanged guard watch/opportunity, exit dashboard, candidate tracker, goal audit, next-action triage, current direction, and candidate-vs-live table.

- Live-only baseline is now `+925c` / `+$9.25`, with `581` entries, `477` completed round trips, W/L by sign `267/306`, and `1` open position.
- Process inventory again showed live bot Python PIDs `19012` and `3356`, plus research shadow/status loop PID `33800`; no processes were touched.
- Candidate-vs-live table now has `1015` candidates, `802` positive candidates, `463` positive target-coverage candidates, and `0` live-ready candidates.
- Candidate tracker has `1015` unique gate/policy lanes, `978` with settled PnL, `515` target-coverage lanes, and `0` live-ready lanes.
- Goal audit still reports `Achieved: False`.

Boundary-clock feature-gate evidence is now a real strict-row sample, not a zero-row wait:

- Diagnostic entry best: `diagnostic_entry_raw03_recross70_abs075`, `82` settled, `79.81%` coverage, `+726c`, W/L `59/23`, reconstructed share `0.325`, blockers `none`.
- Diagnostic bridge best: `diagnostic_bridge_raw03_recross70_abs075`, `80` settled, `79.41%` coverage, `+718c`, W/L `58/22`, reconstructed share `0.333`, blockers `none`.
- Strict post-feature-freeze entry best: `post_feature_freeze_entry_raw05_recross60_abs085`, `30` settled, `61.54%` coverage, `+279c`, W/L `19/11`, reconstructed share `0.325`, cushion `2`, blockers `coverage_too_low` and `full_loss_cushion_lt_3`.
- Strict post-feature-freeze bridge best: `post_feature_freeze_bridge_raw05_recross60_abs085`, `31` settled, `60.61%` coverage, `+333c`, W/L `20/11`, reconstructed share `0.325`, cushion `3`, blocker `coverage_too_low`.
- The broader post-freeze raw03 lane reaches more rows but reopens source and cushion failures, so widening thresholds is still not a standalone repair.
- Current triage frames the nearest feature-gate broad repair as needing additional coverage rows and clean-source dilution; it remains far below the refreshed live baseline.

Exit-policy watches remain the cleaner physical direction but are still strict-sample waits:

- Exit dashboard status counts are `{'blocked_loss_control_cost': 4, 'blocked_net_not_positive': 6, 'positive_but_under_sample': 7, 'waiting_no_post_freeze_rows': 3, 'waiting_no_suppressed_exits': 8}`.
- Frozen exit-clip separator remains `positive_but_under_sample`: `2` post-freeze matched-unchanged rows, `1` selected row, selected helpful/harmful/unknown `1/0/0`, known hold delta `+60c`, blockers `post_freeze_rows_lt_30` and `known_hold_delta_lt_300c`.
- Exit-clip opportunity still has only one near miss, and that near miss has no known positive hold result; threshold variants do not justify a child freeze.
- Frozen matched-unchanged guard has `5` post-freeze scored rows and `1` selected row for `+6c`, with blockers `settled_lt_30`, `suppressed_decisions_lt_30`, and `full_loss_cushion_lt_3`.
- The matched-unchanged opportunity audit sees `4` opportunity-scored rows, `0` selected, and `3` near misses for `+48c`; this is denominator context only, not relaxation evidence.
- The common-clock exit runway remains positive but immature: closest strict row needs more settled rows, many more suppressions, and additional cushion before review.

The background research loop also refreshed two approved-entry-only state valves:

- Frozen danger-zone entry valve `skip_reentry_gap15_or_gap30`: future approved rows/markets `118/71`, candidate/control `+745c/+487c`, delta `+258c`, skipped `8`, blockers `none`.
- Frozen approved-entry state valve `same_side_reentry_gap_lte_15pp`: future approved rows/markets `120/73`, candidate/control `+657c/+477c`, delta `+180c`, skipped `6`, blockers `none`.
- These are actual-v28-approved-only forward validations. They do not score rejected simulated entries and were not present as comparable rows in the refreshed candidate-vs-live table.
- Treat them as a strong research lead for entry/state throttling, not a promotion candidate, until a reporting bridge compares them against live baseline, market coverage, source-quality gates, full-loss cushion, and live-readiness gates on the same basis as the other tracker lanes.

Added `probe_v28_approved_entry_state_valve_bridge.py` to make that comparison gap explicit.

- Output: `logs\edge_research\v28_approved_entry_state_valve_bridge_latest.md` and `.json`.
- The bridge reads the two frozen approved-entry state valve artifacts, the refreshed live summary, candidate-vs-live table text, and candidate tracker summary.
- It reports `2` positive approved-only frozen valves and `0` promotion-ready valves.
- Strongest row is `danger_zone_entry_valve / skip_reentry_gap15_or_gap30`: `110` settled, W/L `98/12`, approved-surface coverage `100%`, gross `+745c`, delta versus approved-entry control `+258c`, skipped `8`.
- Bridge blockers: approved-surface coverage above the broad-entry comparable range, delta full-loss cushion only `2`, not present in candidate-vs-live, approved-entry surface only, live-readiness not evaluated, and naive delta versus live `-180c`.
- `probe_v28_next_action_triage.py` now reads this bridge and adds `bridge_approved_entry_state_valves_before_live_readiness_claims` as a ranked next action.

Added `probe_v28_approved_entry_state_valve_full_surface.py` to replay those same observable valve rules on the normal broad target surfaces.

- Output: `logs\edge_research\v28_approved_entry_state_valve_full_surface_latest.md` and `.json`.
- The probe is research-only and uses each valve's own freeze timestamp; it applies the valve rules to the broad entry and FV-bridge target surfaces, then audits coverage, source share, net, cushion, and delta versus the refreshed live baseline.
- Best broad adapter is `danger_zone_entry_valve / entry_surface`: `86` settled, W/L `50/36`, coverage `71.31%`, net `-349c`, delta versus base `+65c`, reconstructed share `0.943`, and naive delta versus live `-1274c`.
- The skipped rows show the mechanism is real but narrow: it removed `5` broad-surface rows for `+65c` delta, mostly rejected-actionable high raw/book-gap losers, but one skipped row was a `+141c` winner.
- Full-surface blockers are decisive: `coverage_too_low`, `net_not_positive`, `reconstructed_share_gt_35pct`, `full_loss_cushion_lt_3`, `delta_full_loss_cushion_lt_3`, `does_not_beat_refreshed_live_baseline`, `adapter_replay_not_independently_frozen_candidate`, and `live_readiness_not_evaluated`.
- `probe_v28_next_action_triage.py` now reads this full-surface adapter and downgrades the action to `do_not_promote_approved_entry_state_valves_without_full_surface_repair`.

Interpretation: the newest forward rows improved observability but not readiness. The feature-gate branch is positive and source-clean enough in its narrow raw05 form, yet too under-covered and still below live; broader variants buy coverage by reopening source-quality and cushion failures. Exit repairs have better physical separation, especially clip/guarded matched-unchanged holds, but strict suppressions are too sparse. No candidate should be promoted or live-tested from this refresh.

## Next Action

Keep boundary-clock feature-gate, middle-core, and source-risk shrink rows in frozen forward watch, but do not widen thresholds as a standalone repair. Prioritize exit-policy forward validation because the physical mechanism is clearer, with exit-clip and matched-unchanged guard kept as strict-row waits. Also bridge the approved-entry-only danger-zone/state valves into the same research comparison framework before drawing live-readiness conclusions. The next useful work is fresh post-freeze row collection plus denominator/opportunity audits; avoid new diagnostic refreezes unless a repeated strict near-miss pattern emerges with known positive hold outcomes.

## High-Gap Valve Failure-Mode Forensics 2026-05-07 14:00 UTC

Added `probe_v28_high_gap_skipped_failure_modes.py` and refreshed the next-action triage.

- Output: `logs\edge_research\v28_high_gap_skipped_failure_modes_latest.md` and `.json`.
- The probe is research-only and reads only the saved full-surface valve adapter report; it does not rebuild surfaces, create a candidate, freeze a rule, touch live logic, place orders, or control processes.
- It deduplicates the skipped rows from the best danger-zone full-surface adapter and classifies the failure evidence.
- Unique skipped rows: `5`, W/L `1/4`, skipped-row net `-65c`.
- The four losing skipped rows sum to `-206c`; the single winning skipped row is `+141c`.
- All five skipped rows are `rejected_actionable`, all have raw/book gap above `30pp`, and all are first-touch entries rather than same-side reentries.
- Failure-mode counts: source-quality error `5`, FV/book-dislocation or overconfidence `5`, side-lost-despite-large-edge `4`, hard-cutoff right-tail miss `1`, first-touch-not-reentry `5`.
- This strengthens the physical read that high raw/book gap on rejected-actionable rows is a real source/FV confidence problem, but the `+141c` skipped winner is a clear fragility warning against promoting a hard veto.
- `probe_v28_next_action_triage.py` now includes this forensic report in the approved-entry state-valve recommendation and states that the next repair should be a soft confidence/shrinkage test with tail-winner cost accounting, not a live-test candidate.

Fresh live-only baseline was refreshed after this forensic pass:

- Live-only baseline is now `+987c` / `+$9.87`, with `589` entries, `483` completed round trips, W/L by sign `268/312`, and `2` open positions.
- Process inventory again showed live bot Python PIDs `19012` and `3356`, plus research shadow/status loop PID `33800`; no processes were touched.
- The latest live baseline only widens the naive gap versus the approved-entry valve branch. Using the fresh live score, the approved-only danger-zone valve's `+745c` gross is `-242c` versus live, and the broad full-surface adapter's `-349c` net is `-1336c` versus live.

Interpretation: the approved-entry state-valve branch remains useful mechanism evidence, not promotion evidence. The next entry-side experiment should test a continuous high-gap/source-quality shrink on the broad surface under a strict freeze, with explicit accounting for right-tail winners removed by the penalty.

## Feature-Gate High-Gap Shrink Diagnostic 2026-05-07 14:06 UTC

Refreshed the live-only baseline again, then added `probe_v28_feature_gate_high_gap_shrink_diagnostic.py`.

- Live-only baseline is now `+1157c` / `+$11.57`, with `590` entries, `485` completed round trips, W/L by sign `271/312`, and `0` open positions.
- Process inventory again showed live bot Python PIDs `19012` and `3356`, plus research shadow/status loop PID `33800`; no processes were touched.
- Output: `logs\edge_research\v28_feature_gate_high_gap_shrink_diagnostic_latest.md` and `.json`.
- The probe is research-only and diagnostic: it reads the refreshed `v28_boundary_clock_feature_gate_candidate_latest.json`, applies notional high-gap shrink policies to existing feature-gate rows, and does not freeze a new candidate or claim live readiness.
- Evaluated `6` lane/variant rows: the top variant for each feature-gate lane plus the broad raw03 variant where separate.
- Best policy across the diagnostic is `no_shrink_control`; every explicit high-gap shrink policy reduces weighted net.
- Diagnostic entry raw03 control: `+726c`; high-gap mild/linear/half/quarter shrink reduces it to `+714.75c`, `+713.02c`, `+703.5c`, and `+692.25c`.
- Strict post-feature entry raw05 control: `+279c`; shrink reduces it to `+265c`, `+257.77c`, `+251c`, and `+237c`.
- Strict post-feature bridge raw05 control: `+333c`; shrink reduces it to `+319c`, `+311.77c`, `+305c`, and `+291c`.
- The reason is specific and important: in the strict post-feature lanes, the only high-gap row is an approved-entry winner for `+56c`, so raw/book-gap shrink alone cuts right-tail profit instead of repairing the source-quality gap.
- The approved-entry valve bridge was also refreshed against the `+1157c` live baseline. The strongest approved-only valve remains `+745c`, now `-412c` versus live on naive cents comparison.
- `probe_v28_next_action_triage.py` now reads this diagnostic and adds `do_not_shrink_feature_gate_on_high_raw_book_gap_alone`.

Interpretation: the high-gap source-quality clue is real on the rejected-actionable full-surface adapter, but it does not transfer as a standalone feature-gate shrink. The next repair should not be "gap above 30pp means smaller size." It needs a compound condition that distinguishes rejected-actionable high-gap losers from approved-entry high-gap right-tail winners, or it should be deprioritized behind exit-policy validation.

## Exit Promotion Queue Audit 2026-05-07 14:10 UTC

Refreshed `probe_v28_exit_policy_watch_dashboard.py`, then added `probe_v28_exit_promotion_queue_audit.py`.

- Output: `logs\edge_research\v28_exit_promotion_queue_audit_latest.md` and `.json`.
- The probe is research-only and reads the refreshed exit dashboard; it does not create a candidate, change live exits, place orders, or control processes.
- Refreshed dashboard status counts are `{'blocked_loss_control_cost': 5, 'blocked_net_not_positive': 2, 'forward_positive_under_review': 4, 'positive_but_under_sample': 6, 'waiting_no_post_freeze_rows': 3, 'waiting_no_suppressed_exits': 8}`.
- The material change is that `book_gap_loss_guard`, `book_gap_loss_guard_v2`, `common_clock_strict_forward_v1`, and `common_clock_strict_forward_v2` now have enough settled strict rows and positive deltas to be `forward_positive_under_review`.
- The queue audit applies stricter promotion-review checks: at least `30` settled rows, at least `30` suppressed decisions, positive candidate net, positive delta, nonnegative loss-control cost, candidate full-loss cushion `>=3`, and delta full-loss cushion `>=3`.
- Review-ready rows: `0`.
- Forward-positive queue rows: `10`.
- Closest row is `common_clock_strict_forward_v2`: `37` settled, `10` suppressions, candidate `+340c`, delta `+100c`, loss-control cost `0c`, candidate/delta cushion `3/1`.
- It still needs `20` additional strict suppressions and `+200c` additional delta cushion before promotion review.
- `book_gap_loss_guard` and `common_clock_strict_forward_v1` are next: each has `38` settled, `10` suppressions, candidate `+254c`, delta `+100c`, loss cost `0c`, but candidate/delta cushion `2/1`.
- `book_gap_loss_guard_v2` has `37` settled but only `2` suppressions and `+40c` delta, so its density is much weaker despite clean loss-control cost.
- `probe_v28_next_action_triage.py` now reads this queue audit and adds `collect_exit_suppression_density_before_review` near the top of the action list.

Interpretation: exit validation is moving in the right direction, but no exit watch is review-ready. The active bottleneck is not settled-row count anymore for the top guards; it is strict suppression density plus delta cushion. Do not freeze another broad diagnostic exit rule from this evidence. Keep collecting strict suppressions and use the queue audit to decide when a real promotion review is warranted.

## Common-Clock Exit Density Refresh 2026-05-07 14:12 UTC

Refreshed `probe_v28_exit_common_clock_promotion_runway.py`, `probe_v28_exit_common_clock_suppression_scarcity.py`, `probe_v28_exit_common_clock_positive_drilldown.py`, and `probe_v28_next_action_triage.py`.

- Updated common-clock runway output: `logs\edge_research\v28_exit_common_clock_promotion_runway_latest.md` and `.json`.
- Updated suppression-scarcity output: `logs\edge_research\v28_exit_common_clock_suppression_scarcity_latest.md` and `.json`.
- Updated positive drilldown output: `logs\edge_research\v28_exit_common_clock_positive_drilldown_latest.md` and `.json`.
- The common-clock runway now agrees with the exit queue audit: closest strict exit row is `new_exit_mix_common_forward_v2 / loss_guard_value_p85_reduce_p79_gap0`.
- Current v2 state: `37` settled, `10` suppressions, current/candidate/delta `+240c/+340c/+100c`, loss-control cost `0c`.
- Runway says it needs `0` more settled rows, `20` more suppressed decisions, and `0c` more candidate-net cushion. The stricter queue audit still requires `+200c` more delta cushion before review.
- Suppression scarcity says the best audit policy on the v2 clock is `v1_like_on_v2_clock`: `37` settled, `10` suppressions, helpful/harmful `10/0`, candidate `+340c`, delta `+100c`, loss cost `0c`, blocker `suppressed_decisions_lt_30`.
- The v2-control policy is cleaner but too sparse: `2` suppressions, `+40c` delta, blocker `suppressed_decisions_lt_30` plus cushion.
- The only relaxed policy that meaningfully increases density, `value_p80_shallow5`, reintroduces harm: `5` suppressions, helpful/harmful `4/1`, candidate `+144c`, delta `-96c`, loss cost `-180c`.
- Positive drilldown confirms the residual problem: v2 best policy has `10/0` helpful/harmful suppressions, but still has `10` candidate losses and `17` unsuppressed winner clips.
- The residual separator scan is diagnostic only. It finds high theoretical deltas for `p_hold_lt_75` and collapse/exitable pockets, but those would be new child hypotheses and cannot be promoted from this strict parent window.

Interpretation: the v1-like loss guard is the cleanest current strict exit mechanism, but the data says "wait for density," not "loosen thresholds." Relaxing toward lower p-hold/shallow variants can find more suppressed rows, but it also reopens false-hold harm. Keep the common-clock watch active and judge only strict post-freeze suppressions.

## Residual Exit70-79 Child Refresh 2026-05-07 14:16 UTC

Refreshed `probe_v28_frozen_exit_common_clock_residual_child_watch.py`, then refreshed the exit dashboard, exit promotion queue, next-action triage, live-only scorecard, and process inventory.

- Residual child output: `logs\edge_research\v28_frozen_exit_common_clock_residual_child_watch_latest.md` and `.json`.
- Child freeze UTC remains `2026-05-07T08:06:06.929631+00:00`.
- Child rule: parent `loss_guard_value_p85_reduce_p79_gap0` does not suppress, and exit price is in the `70-79c` band.
- Diagnostic v2 common-clock context is now `37` settled, parent suppressed `10`, child suppressed `5`, helpful/harmful `5/0`, child delta `+252c`, candidate net `+592c`, blocker `child_suppressed_decisions_lt_30`.
- Strict post-child-birth evidence has started: `12` settled, parent suppressed `3`, child suppressed `2`, helpful/harmful `2/0`, child delta `+102c`, candidate net `+408c`, cushion `4`.
- Strict blockers remain `settled_lt_30` and `child_suppressed_decisions_lt_30`; this is not promotable.
- Refreshed exit dashboard now classifies `common_clock_residual_child_exit70_79` as `positive_but_under_sample`: `12` settled, `2` suppressions, current/candidate/delta `+264c/+408c/+144c`, cushion `4`.
- Sequentially refreshed exit promotion queue now includes this child as rank `3`: `12` settled, `2` suppressions, candidate `+408c`, delta `+144c`, candidate/delta cushion `4/1`, missing `18` settled rows, `28` suppressions, and `+156c` delta cushion.
- `probe_v28_next_action_triage.py` now reads the residual child watch and adds `collect_common_clock_residual_child_rows`.
- Fresh live-only baseline is now `+1185c` / `+$11.85`, with `597` entries, `491` completed round trips, W/L by sign `274/316`, and `0` open positions.
- Process inventory again showed live bot Python PIDs `19012` and `3356`, plus research shadow/status loop PID `33800`; no processes were touched.

Interpretation: this is the first useful strict evidence for the residual child. It supports the physical idea that some 70-79c exits are clipped winners after the parent loss guard declines to suppress, but the strict sample is tiny. Keep it as a child watch and do not fold it into the parent or live logic until it earns enough post-birth rows, suppressions, and delta cushion.

## Residual Exit70-79 Child Path-Risk Audit 2026-05-07 14:19 UTC

Added and ran `probe_v28_exit_common_clock_residual_child_path_risk.py`, then refreshed `probe_v28_next_action_triage.py`.

- Output: `logs\edge_research\v28_exit_common_clock_residual_child_path_risk_latest.md` and `.json`.
- The probe is research-only: it joins residual-child suppressed rows to `v28_post_exit_path_latest.json` and checks adverse mark-to-market exposure after the skipped exit.
- Diagnostic v2 context: `5` child suppressions, `4` matched path rows, worst adverse vs skipped exit `-108c`, adverse 10/25/50 rows `4/2/1`, below-zero marks `4`, blockers `child_suppressed_decisions_lt_30`, `post_exit_adverse_25c_present`, `post_exit_mark_below_zero_present`, and `missing_post_exit_path_rows`.
- Diagnostic v3 context: `4` child suppressions, `3` matched path rows, worst adverse `-30c`, adverse 10/25/50 rows `3/1/0`, below-zero marks `3`, blockers `settled_lt_30`, `child_suppressed_decisions_lt_30`, `post_exit_adverse_25c_present`, `post_exit_mark_below_zero_present`, and `missing_post_exit_path_rows`.
- Strict post-child-birth evidence: `2` child suppressions, `1` matched path row, worst adverse vs skipped exit `-10c`, adverse 10/25/50 rows `1/0/0`, below-zero marks `1`.
- Strict path-risk blockers are now `settled_lt_30`, `child_suppressed_decisions_lt_30`, `post_exit_mark_below_zero_present`, and `missing_post_exit_path_rows`.
- `probe_v28_next_action_triage.py` now carries this path-risk evidence inside `collect_common_clock_residual_child_rows`.

Interpretation: settlement still says the residual child is promising, but path risk says it is not clean enough for review. The strict sample has only one matched path row, and that winner still marked below zero after the skipped exit. Continue collecting residual-child rows and require path completeness plus survivable adverse marks before treating the child as more than a watch.

## Feature-Gate and Exit Queue Refresh 2026-05-07 14:39 UTC

Refreshed live-only scorecard, process inventory, `probe_v28_boundary_clock_feature_gate_candidate.py`, candidate tracker/table, goal audit, current-direction decision, exit dashboard, common-clock runway, residual-child watch, residual-child path risk, exit queue, and next-action triage. The four heavy boundary-clock source/frontier probes timed out when launched together; the leftover research-only probe PIDs were stopped after verifying they were not live bot or shadow-loop processes, and the feature-gate candidate was rerun sequentially to completion.

- Fresh live-only baseline: `+1103c` / `+$11.03`, with `600` entries, `493` completed round trips, W/L by sign `274/318`, and `1` open position.
- Process inventory showed live bot Python PIDs `19012` and `3356`, plus research shadow/status loop PID `33800`; no live process was touched.
- Feature-gate candidate output: `logs\edge_research\v28_boundary_clock_feature_gate_candidate_latest.md` and `.json`, generated `2026-05-07T14:38:16.009460+00:00`.
- Post-feature-freeze evidence is no longer zero. Best strict entry is `post_feature_freeze_entry_raw05_recross60_abs085`: `37` settled, `64.79%` coverage, `+382c`, W/L `25/12`, reconstructed share `0.2826`, cushion `3`, blocker `coverage_too_low`.
- Best strict bridge is `post_feature_freeze_bridge_raw05_recross60_abs085`: `41` settled, `64.79%` coverage, `+427c`, W/L `29/12`, reconstructed share `0.2826`, cushion `4`, blocker `coverage_too_low`.
- Broader raw03 strict entry gets near target coverage at `74.65%` and `+383c`, but reconstructed share is `0.3774`, so it fails both `coverage_too_low` and `reconstructed_share_gt_35pct`.
- Broader raw03 strict bridge similarly reaches `74.65%` and `+360c`, but reconstructed share is `0.3774`.
- Refreshed goal audit remains `Achieved: False`; candidate-vs-live table has `992` rows and still no live-ready/integrity-pass promotion candidate.
- Refreshed current direction still prioritizes exit-policy validation first, with feature-gate boundary-clock in forward watch.

Interpretation: feature-gate moved from "wait for rows" to a real strict-forward sample. The clean raw05 lane is profitable and source-acceptable but too narrow; the broader raw03 lane is near target coverage but source-stressed. This is not promotable versus the refreshed live baseline, but it gives a sharper entry-side bottleneck: repair coverage without reopening the rejected/reconstructed tail.

## Residual Exit70-79 Child False-Hold Autopsy 2026-05-07 14:41 UTC

After rerunning the exit dashboard and queue sequentially, the residual-child row was downgraded from positive-under-sample to blocked by loss-control cost. Added and ran `probe_v28_exit_common_clock_residual_child_false_hold_autopsy.py`, then refreshed next-action triage.

- Output: `logs\edge_research\v28_exit_common_clock_residual_child_false_hold_autopsy_latest.md` and `.json`.
- Ordered exit queue generated from dashboard `2026-05-07T14:39:48.660025+00:00`: review-ready rows `0`, forward-positive queue rows `10`.
- Closest exit row remains `common_clock_strict_forward_v2`: `42` settled, `11` suppressions, candidate `+382c`, delta `+112c`, candidate/delta cushion `3/1`; it still needs `19` suppressions and `188c` delta cushion.
- Residual child strict post-birth is now `17` settled, `4` child suppressions, helpful/harmful `2/2`, child delta `-202c`, candidate/current/delta `+146c/+294c/-148c`, loss-control cost `-304c`, cushion `1`.
- Residual child blockers now include `delta_vs_current_not_positive`, `child_delta_vs_parent_not_positive`, `child_loss_control_cost_negative`, and `full_loss_cushion_lt_3`.
- Path-risk audit now matches only `1/4` strict child rows; it still has `post_exit_mark_below_zero_present` and `missing_post_exit_path_rows`.
- False-hold autopsy adds durable blockers: `strict_false_holds_present`, `same_market_false_hold_cluster`, `p_hold_75_79_false_hold_risk`, and `probability_reduce_false_hold_risk`.
- The two harmful child suppressions are both `NO` rows in `KXBTC15M-26MAY071015-15`, both `mushroom_v28_probability_reduce`, both p_hold `75-79`, for combined child delta `-304c`.
- `probe_v28_next_action_triage.py` now carries the false-hold autopsy inside `collect_common_clock_residual_child_rows`.

Interpretation: the residual child is no longer just an immature clipped-winner watch. It has already found the physical false-hold trap the guardrails warned about: probability-reduce exits around p_hold 75-79 can be true FV/entry losers, especially when clustered in the same market. Do not widen or promote this child; keep the parent common-clock v2/v3 density watch, and require any child repair to explicitly avoid this false-hold state under its own freeze.

## Feature-Gate Consistency Refresh 2026-05-07 15:00 UTC

Refreshed live-only scorecard, stale feature-gate source-denominator/source-runway artifacts, the heavy `probe_v28_boundary_clock_feature_gate_candidate.py`, candidate-vs-live table, promotion-gap audit, consistency audit, and current-direction decision.

- Fresh live-only scorecard before this refresh: `+1107c` / `+$11.07`, with `603` entries, `495` completed round trips, W/L by sign `276/320`, and `0` open positions.
- Refreshed feature-gate candidate generated `2026-05-07T15:00:39.637007+00:00`.
- Strict post-feature entry best is now `post_feature_freeze_entry_raw05_recross60_abs085`: `36` settled, `65.28%` coverage, `+294c`, W/L `24/12`, reconstructed share `0.2766`, cushion `2`, blockers `coverage_too_low` and `full_loss_cushion_lt_3`.
- Strict post-feature bridge best is `post_feature_freeze_bridge_raw05_recross60_abs085`: `41` settled, `65.28%` coverage, `+350c`, W/L `28/13`, reconstructed share `0.2766`, cushion `3`, blocker `coverage_too_low`.
- Broad strict entry `post_feature_freeze_entry_raw03_recross70_abs075` now reaches `75.00%` coverage, but only with reconstructed share `0.3704`, cushion `2`, and net `+274c`, so blockers are `reconstructed_share_gt_35pct` and `full_loss_cushion_lt_3`.
- Broad strict bridge `post_feature_freeze_bridge_raw03_recross70_abs075` also reaches `75.00%` coverage, with reconstructed share `0.3704`, cushion `2`, and net `+283c`; same blockers.
- Promotion-gap audit generated `2026-05-07T15:00:48.002769+00:00` and remains `watch_only_not_promotable`. It uses a refreshed live baseline of `+1147c`, so the broad entry is `-873c` versus live and the raw05 bridge is still far below live.
- Source feasibility says `75%` target coverage is mathematically feasible under the source cap only at a thin minimum reconstructed share around `31.48%`; `80%` is not feasible under the source cap.
- Size-shrink runway remains watch-only: `45` settled, `75.41%` coverage, weighted net `+369c`, row reconstructed share `0.4130`, `9` clean approved rows needed, and `-738c` versus the refreshed live baseline.
- Artifact consistency audit still blocks promotion discussion because the broad feature-gate and size-shrink artifacts disagree on settled-row accounting and one live-delta value. Live-baseline mismatch itself was cleared.

Interpretation: feature-gate is now a real strict-forward branch, but the bottleneck is sharper and still fatal for promotion. The only broad post-freeze rows reach coverage by taking too much reconstructed/rejected-actionable exposure and lose full-loss cushion. The clean raw05 rows are profitable but under-covered. No feature-gate lane is live-ready, and stale/inconsistent auxiliary artifacts must be treated as advisory until their denominator logic is reconciled.

## Residual Child Guardrail Variants 2026-05-07 15:07 UTC

Added and ran `probe_v28_exit_common_clock_residual_child_guardrail_variants.py`, then refreshed the residual-child watch, path-risk audit, false-hold autopsy, exit dashboard, promotion queue, and next-action triage in order.

- Output: `logs\edge_research\v28_exit_common_clock_residual_child_guardrail_variants_latest.md` and `.json`.
- The probe is research-only and tests observable child-guard variants on the same frozen windows; it does not freeze a new child, alter live logic, or place orders.
- In-process verification confirmed the guard probe's `base_exit70_79` variant matches `probe_v28_frozen_exit_common_clock_residual_child_watch.py` when both score the exact same row list.
- Final ordered base residual child: strict post-birth `20` settled, `4` child suppressions, helpful/harmful `2/2`, child delta `-202c`, candidate net `+190c`, blockers `settled_lt_30`, `child_suppressed_decisions_lt_30`, `delta_vs_current_not_positive`, `child_delta_vs_parent_not_positive`, `child_loss_control_cost_negative`, and `full_loss_cushion_lt_3`.
- False-hold autopsy remains active: the harmful strict child rows are `2` rows for `-304c`, both in `KXBTC15M-26MAY071015-15`, both `mushroom_v28_probability_reduce`, both p_hold `75-79`.
- Best clean strict guard variant is `book_gap_le_neg_0_5pp`: `20` settled, `2` child suppressions, helpful/harmful `2/0`, child delta `+102c`, candidate net `+494c`, blockers `settled_lt_30` and `child_suppressed_decisions_lt_30`.
- Equivalent clean variants in this tiny strict sample are `p_hold_lt75_or_book_gap_le_neg_0_5pp` and `prob_reduce_requires_book_gap_le_neg_0_5pp`; all keep the same two winner rows and remove the same false-hold rows.
- Updated exit promotion queue still has review-ready rows `0`. Closest row is still `common_clock_strict_forward_v2`: `45` settled, `11` suppressions, candidate `+426c`, delta `+112c`, candidate/delta cushion `4/1`, missing `19` suppressions and `188c` delta cushion.
- `probe_v28_next_action_triage.py` now includes the guardrail scan under `collect_common_clock_residual_child_rows`.

Interpretation: the false-hold mechanism has a plausible observable repair: require clear negative hold-book gap before the residual child suppresses a 70-79c exit, especially for probability-reduce/p_hold 75-79 states. This is not promotion evidence. It is a child-repair hypothesis with only `2` strict suppressions and must get its own freeze before any future rows can count.

## Frozen Residual Book-Gap Guard Watch 2026-05-07 15:09 UTC

Added and ran `probe_v28_frozen_exit_common_clock_residual_child_book_gap_guard_watch.py`, then refreshed next-action triage.

- Output: `logs\edge_research\v28_frozen_exit_common_clock_residual_child_book_gap_guard_watch_latest.md` and `.json`.
- State file: `logs\edge_research\v28_frozen_exit_common_clock_residual_child_book_gap_guard_watch_state.json`.
- Guard freeze UTC: `2026-05-07T15:09:26.289911+00:00`.
- Candidate: `residual_exit70_79_book_gap_le_neg_0_5pp`.
- Rule shape: parent common-clock loss guard does not suppress, exit price is `70-79c`, and hold-book gap is `<= -0.5pp`.
- Physical reason: a 70-79c exit is more plausibly transient winner clipping when the book still leans toward holding; flat or positive hold-book gap in p_hold `75-79` probability-reduce exits is a false-hold risk.
- Diagnostic v2 common-clock context: `45` settled, `5` child suppressions, helpful/harmful `5/0`, child delta `+252c`, candidate net `+678c`, blocker `child_suppressed_decisions_lt_30`.
- Diagnostic v3 common-clock context: `33` settled, `4` child suppressions, helpful/harmful `4/0`, child delta `+200c`, candidate net `+650c`, blocker `child_suppressed_decisions_lt_30`.
- Strict post-book-gap-guard birth evidence: `0` settled, `0` child suppressions, child delta `0c`, candidate net `0c`, blockers `settled_lt_30`, `child_suppressed_decisions_lt_30`, `net_not_positive`, `delta_vs_current_not_positive`, `child_delta_vs_parent_not_positive`, and `full_loss_cushion_lt_3`.
- `probe_v28_next_action_triage.py` now adds `collect_residual_child_book_gap_guard_watch_rows`.

Interpretation: this is now a proper frozen child-repair watch. The diagnostic guard is physically coherent and repairs the observed base-child false holds in historical/current strict context, but promotion evidence is exactly zero because the guard was just born. Future evaluation must use only rows after `2026-05-07T15:09:26.289911+00:00`.

## Exit Dashboard Guard Watch Integration 2026-05-07 15:13 UTC

Refreshed the exit dashboard, promotion queue, current-direction decision, and goal-completion audit after adding the frozen residual book-gap child watch to the central exit-policy rollups.

- `probe_v28_exit_policy_watch_dashboard.py` now includes `common_clock_residual_child_book_gap_guard` from `logs\edge_research\v28_frozen_exit_common_clock_residual_child_book_gap_guard_watch_latest.json`.
- Latest dashboard generated `2026-05-07T15:11:39.387727+00:00` with review-ready/promotable exit rows still at zero.
- Dashboard status for `common_clock_residual_child_book_gap_guard` is `waiting_no_post_freeze_rows`: `0` settled, `0` child suppressions, `0c` candidate net, and the expected newborn-watch blockers.
- Dashboard keeps the base `common_clock_residual_child_exit70_79` blocked by loss-control cost: `20` settled, `4` child suppressions, candidate/current/delta `+190c/+338c/-148c`, and loss-control cost `-304c`.
- Exit queue generated from the same dashboard has review-ready rows `0`, forward-positive queue rows `11`, and blocked/waiting counts `10/7`.
- Closest queue row is still `book_gap_loss_guard`: `34` settled, `7` suppressions, candidate `+338c`, delta `+68c`, candidate/delta cushion `3/0`, missing `23` suppressions and `232c` delta cushion.
- `probe_v28_current_direction_decision.py` and `probe_v28_goal_completion_audit.py` were refreshed after dashboard integration; the long-term goal remains unachieved and exit-policy validation remains the current priority.

Interpretation: the residual child repair has been moved from an isolated probe into the active watch dashboard, but it has no strict post-freeze evidence yet. The only valid next step is to collect post-`2026-05-07T15:09:26.289911+00:00` rows while the broader exit queue continues to require suppression density and delta cushion.

## Shadow Availability for Residual Book-Gap Guard 2026-05-07 15:16 UTC

Refreshed live-only scoring, the frozen residual book-gap child watch, exit dashboard, promotion queue, next-action triage, common-clock scarcity audit, loss-churn reports, and shadow observation availability. Added the new residual book-gap child clock to `probe_v28_shadow_observation_availability.py` so future availability checks track this watch directly.

- Fresh live-only baseline: `+1147c` / `+$11.47`, with `614` entries, `505` completed round trips, and `0` open positions.
- Process inventory still showed live bot Python PIDs `19012` and `3356`, plus shadow/status loop PID `33800`; no live process was touched.
- `v28_frozen_exit_common_clock_residual_child_book_gap_guard_watch_latest.md` generated `2026-05-07T15:14:41.054074+00:00`; strict `post_book_gap_guard_birth` remains `0` settled and `0` child suppressions.
- Refreshed dashboard generated `2026-05-07T15:14:58.895173+00:00`; review-ready exit rows remain `0`, forward-positive queue rows remain `11`, and closest row is `book_gap_loss_guard` with `34` settled, `7` suppressions, candidate `+338c`, delta `+68c`, candidate/delta cushion `3/0`.
- Common-clock scarcity audit generated `2026-05-07T15:15:40.984708+00:00`; best audit policy `v1_like_on_v2_clock` has `21` settled, `7` suppressions, `+222c` candidate net, `+86c` delta, and no loss-control cost, but still fails settled, suppression-density, and cushion gates.
- Loss-churn reports still say the best strict loss-count reducer is `exit_reduce_suppression`, reducing losses `31 -> 23` with `+189c` delta, but it remains blocked by negative loss-control cost.
- Shadow availability generated `2026-05-07T15:16:49.847689+00:00` and now includes `exit_common_clock_residual_child_book_gap_guard`.
- For the new book-gap child guard clock, availability shows `93` post-freeze events, `0` post-freeze entry trades, `1` post-freeze exit-clock trade, `1` settled exit-clock row, and `0` pending rows.
- The single post-freeze exit-clock row is `KXBTC15M-26MAY071115-15` / YES: entry `2026-05-07T15:08:31.085962+00:00`, freeze `2026-05-07T15:09:26.289911+00:00`, exit `2026-05-07T15:09:47.749994+00:00`, result YES, actual `+14c`, hold `+32c`, exit reason `mushroom_v28_exit_value_over_hold`.

Interpretation: the empty strict guard lane is not a shadow-loop outage. The first qualifying exit-clock observation arrived after the freeze, but its entry was before the freeze, so the strict watch correctly excludes it. Future promotion evidence for this child must wait for entries and exits both born after `2026-05-07T15:09:26.289911+00:00`.

## Compact Feature-Gate Strict Refresh 2026-05-07 15:34 UTC

The full `probe_v28_boundary_clock_feature_gate_candidate.py` refresh timed out and left a research-only Python process, which was stopped after verifying it was not a live bot or shadow-loop process. Added `probe_v28_boundary_clock_feature_gate_quick_status.py` as a compact strict-forward refresh for the post-feature-freeze lanes only. It does not alter live logic and intentionally excludes diagnostic lanes and row payloads.

- Output: `logs\edge_research\v28_boundary_clock_feature_gate_quick_status_latest.md` and `.json`.
- Corrected the quick probe to match the canonical feature-gate row selection: one row per market selected by highest raw edge, not realized net.
- Latest quick status generated `2026-05-07T15:34:27.659312+00:00`, using feature-gate freeze `2026-05-06T16:47:25.847566+00:00`.
- Best strict entry lane is `post_feature_freeze_entry_raw05_recross60_abs085`: `32` settled, `65.33%` coverage, `+120c`, W/L `18/14`, reconstructed share `0.2857`, cushion `1`, blockers `coverage_too_low` and `full_loss_cushion_lt_3`.
- Best strict bridge lane is `post_feature_freeze_bridge_raw05_recross60_abs085`: `44` settled, `66.67%` coverage, `+323c`, W/L `30/14`, reconstructed share `0.2800`, cushion `3`, blocker `coverage_too_low`.
- Broad strict entry `post_feature_freeze_entry_raw03_recross70_abs075` is near coverage at `74.67%`, but only `+53c`, reconstructed share `0.3750`, cushion `0`, and blockers `coverage_too_low`, `reconstructed_share_gt_35pct`, and `full_loss_cushion_lt_3`.
- Broad strict bridge `post_feature_freeze_bridge_raw03_recross70_abs075` reaches `76.00%` coverage, but reconstructed share is `0.3684`, cushion is `2`, and blockers are `reconstructed_share_gt_35pct` and `full_loss_cushion_lt_3`.
- Compared with the refreshed live baseline of `+1147c`, even the best bridge lane is still `-824c` versus live-only v28.

Interpretation: feature-gate has strict-forward evidence now, but the current promotion shape is worse than the older diagnostic/early-forward snapshot. The source-clean raw05 lanes do not preserve broad participation, while the broad raw03 lanes only reach target coverage by exceeding the source-quality cap and lacking full-loss cushion. This remains watch-only and is not a live-test candidate.

## Feature-Gate raw03 vs raw05 Autopsy 2026-05-07 15:49 UTC

Added and ran `probe_v28_feature_gate_raw03_vs_raw05_autopsy.py` to explain the strict-forward coverage/source tradeoff directly. It compares the current post-feature-freeze raw03 broad rows against the cleaner raw05 rows, without using source labels for selection.

- Output: `logs\edge_research\v28_feature_gate_raw03_vs_raw05_autopsy_latest.md` and `.json`.
- The probe is research-only and does not change live bot logic.
- The autopsy generated `2026-05-07T15:49:14.960204+00:00` with embedded live baseline `+1235c`; after it completed, live-only score was refreshed again to `+1463c`, with `617` entries, `507` completed round trips, and `0` open positions.
- Strict entry raw05: `50` entries, `45` settled, `65.79%` coverage, `+456c`, W/L `32/13`, reconstructed share `0.2800`.
- Strict entry raw03: `57` entries, `52` settled, exactly `75.00%` coverage, `+389c`, W/L `34/18`, reconstructed share `0.3684`.
- Strict bridge raw05: `50` entries, `43` settled, `65.79%` coverage, `+433c`, W/L `30/13`, reconstructed share `0.2800`.
- Strict bridge raw03: `57` entries, `50` settled, exactly `75.00%` coverage, `+366c`, W/L `32/18`, reconstructed share `0.3684`.
- The seven raw03-only marginal rows are all `rejected_actionable`, W/L `2/5`, net `-83c`, and carry source-quality risk. Five of seven also have `ask_below_65`; six have `thin_raw_edge_03_05`; two have `weak_abs_d_075_085`.
- The worst marginal row is `KXBTC15M-26MAY070615-15` YES, `rejected_actionable`, `-68c`, raw edge `0.2009`, recross `0.2533`, abs_d `0.8200`, ask `0.64`.
- Dropping enough reconstructed losers to pass the source gate improves net but lowers coverage to `72.37%`, so it fixes source only by breaking the broad-participation gate.
- With the fresh live baseline at `+1463c`, strict raw05 entry is `-1007c` versus live, strict raw03 entry is `-1074c`, strict raw05 bridge is `-1030c`, and strict raw03 bridge is `-1097c`.

Interpretation: raw03 is not a clean coverage repair. The marginal coverage it adds is entirely rejected-actionable and negative in strict-forward evidence, while removing the bad reconstructed rows drops coverage below target. The feature-gate branch should not be repaired by simple raw-edge relaxation; future work should wait for clean forward rows or test a true source/quality proxy that rejects the raw03 marginal slice without destroying coverage.

## Feature-Gate raw05 Coverage-Gap Audit 2026-05-07 15:55 UTC

Added and ran `probe_v28_feature_gate_raw05_coverage_gap_audit.py` to check whether the source-cleaner raw05 feature-gate lane is under-covered because it is missing approved rows, or because the remaining denominator is source-risky rejected-actionable exposure.

- Output: `logs\edge_research\v28_feature_gate_raw05_coverage_gap_audit_latest.md` and `.json`.
- The probe is research-only. Source labels and realized outcomes are audit-only; no live rule or threshold is changed.
- Generated `2026-05-07T15:55:49.546817+00:00`, using feature-gate freeze `2026-05-06T16:47:25.847566+00:00` and refreshed live baseline `+1463c`.
- Current strict denominator is `76`; 75% coverage requires `57` entries.
- raw05 entry has `50` entries, `37` settled, `65.79%` coverage, `+336c`, W/L `24/13`, reconstructed share `0.2800`. It needs `7` entries for the 75% gate.
- raw05 bridge has `50` entries, `38` settled, `65.79%` coverage, `+147c`, W/L `23/15`, reconstructed share `0.2800`. It also needs `7` entries.
- Omitted rows for both entry and bridge are `0` approved and `26` rejected-actionable. There are no approved omitted rows available to fill the raw05 coverage gap under the current denominator.
- Omitted fail reasons are `abs_d_below_min` for all `26` omitted rows and `recross_above_max` for `9`; the missing coverage is outside the raw05 physical distance/recross gate.
- An approved-only oracle cannot add any rows, so it remains under-covered at `65.79%`.
- A best-any-source oracle can hit `75.00%` coverage, but it adds `7` rejected-actionable rows and ends with reconstructed share `0.3684`, so it fails the source-quality gate. It still remains far below live: entry `+705c` vs live `+1463c`, bridge `+468c` vs live `+1463c`.

Interpretation: raw05 under-coverage is not a hidden approved-entry opportunity. The current denominator has no approved rows outside raw05 to recover. Any coverage repair must either wait for future clean approved rows or use a new observable quality proxy that can prove, under its own freeze, that rejected-actionable exposure is safe enough. A post-hoc oracle that picks rejected winners is not promotion evidence.

## Feature-Gate Triage Integration 2026-05-07 16:04 UTC

Updated `probe_v28_next_action_triage.py` so the new feature-gate blocker evidence is not isolated in side reports.

- Added triage inputs for:
  - `logs\edge_research\v28_boundary_clock_feature_gate_quick_status_latest.json`
  - `logs\edge_research\v28_feature_gate_raw03_vs_raw05_autopsy_latest.json`
  - `logs\edge_research\v28_feature_gate_raw05_coverage_gap_audit_latest.json`
- Refreshed `logs\edge_research\v28_next_action_triage_latest.md` and `.json`.
- New recommendation: `do_not_repair_feature_gate_raw05_gap_with_raw03_relaxation`.
- The triage recommendation now uses the raw03-vs-raw05 autopsy for strict raw05/raw03 PnL and uses the raw05 coverage-gap audit for omitted-row/source availability, avoiding mixed settlement snapshots.
- Current triage read:
  - raw05 entry: `51` entries, `49` settled, `67.11%` coverage, `+355c`, reconstructed share `0.2745`.
  - raw03 entry: `58` entries, `56` settled, `76.32%` coverage, `+288c`, reconstructed share `0.3621`.
  - raw03-only entry slice: `7` rows, all `rejected_actionable`, W/L `2/5`, net `-83c`.
  - raw05 omitted entry rows: `26` `rejected_actionable`, `0` approved, with fail reasons `abs_d_below_min=26` and `recross_above_max=9`.
  - best any-source oracle reaches `75.32%` coverage only by adding `7` rejected-actionable rows, leaving reconstructed share `0.3621`.

Interpretation: the central next-action artifact now carries the same conclusion as the side audits: raw05 is under-covered because there are no approved omitted rows available, and raw03's apparent coverage repair is rejected-actionable source leakage. Future feature-gate work should not be another simple relaxation; it needs either fresh clean forward rows or an independently frozen observable source-quality proxy.

## Direction Report Integration 2026-05-07 16:12 UTC

Updated `probe_v28_current_direction_decision.py` so the high-level direction ledger now consumes the compact feature-gate quick status, raw03-vs-raw05 autopsy, and raw05 coverage-gap audit directly.

- Added a dedicated decision row: `feature_gate_raw05_gap_audit` / `do_not_repair_with_raw03_relaxation`.
- Regenerated `logs\edge_research\v28_current_direction_decision_latest.md` and `.json` at `2026-05-07T16:11:33.653438+00:00`.
- Refreshed live-only baseline before final comparisons: `+$13.99` / `+1399c`, `621` entries, `511` completed round trips, W/L by sign `282/328`, and `0` open positions.
- Refreshed `v28_candidate_vs_live_full_table_latest`, `v28_candidate_pnl_tracker_latest`, `v28_goal_completion_audit_latest`, `v28_next_action_triage_latest`, and `v28_exit_policy_watch_dashboard_latest` after the live score refresh.
- Current direction remains: objective not achieved; prioritize exit-policy validation first, keep boundary-clock/feature-gate branches in forward watch, and do not treat raw03 threshold relaxation as a real raw05 coverage repair.
- Candidate-vs-live table now uses `1399c` as the live row. The top diagnostic rows show `+2072.5c` and `+673.5c` versus live, but remain blocked by `needs_own_frozen_forward_birth` and `live_ready_false`.

Interpretation: the feature-gate evidence is now propagated into both next-action triage and the high-level direction ledger. The active entry-side conclusion did not change: raw05 lacks clean approved coverage, and raw03 buys coverage through rejected-actionable source exposure. The next productive work is still strict exit-policy validation and fresh clean-forward accumulation, not another raw threshold relaxation.

## Exit Loss-Guard V3 Residual Audit 2026-05-07 16:16 UTC

Added `probe_v28_exit_loss_guard_v3_residual_bucket_size_shrink.py` to test whether v3's rejected v1-only residual bucket should be recovered with a continuous/partial-size overlay instead of hard rejection.

- Output: `logs\edge_research\v28_exit_loss_guard_v3_residual_bucket_size_shrink_latest.md` and `.json`.
- The probe is research-only and does not freeze a candidate or change live exit logic.
- Strict v3-forward residual bucket: `3` rows, `+36c`, helpful/harmful `3/0`, harmful delta `0c`.
- All-exit diagnostic residual bucket: `16` rows, `-14c`, helpful/harmful `15/1`, harmful delta `-186c`.
- In the strict v3 window, full residual relaxation would have only `11` selected decisions, candidate/delta cushion `6/1`, and blockers `suppressed_decisions_lt_30`, `delta_full_loss_cushion_lt_3`, and `residual_policy_not_independently_frozen`.
- Updated `probe_v28_next_action_triage.py`; new recommendation `do_not_relax_v3_with_residual_bucket_yet`.
- Updated `probe_v28_current_direction_decision.py`; exit-policy evidence now includes the residual audit and the direction text says v3 hard rejection remains the safer default until a separately frozen residual/partial-size watch earns rows.

Interpretation: this closes an overfit-prone exit branch. The fresh strict residual rows are green but too sparse, and older diagnostic evidence contains a rare large false hold. The current productive exit path remains strict collection for v3/book-gap/common-clock density and cushion, not relaxing v3 on the current small residual slice.

## Exit Reduce Observable False-Hold Autopsy 2026-05-07 16:22 UTC

Added `probe_v28_exit_reduce_observable_false_hold_autopsy.py` to test whether the observable reduce-loss-control branch is a stable loss-count repair or mostly a diagnostic explanation with fresh false-hold risk.

- Output: `logs\edge_research\v28_exit_reduce_observable_false_hold_autopsy_latest.md` and `.json`.
- The probe is research-only. It does not freeze a candidate and does not change live exit logic.
- Diagnostic p_hold>=0.75 probability-reduce denominator: `18` rows, `+171c`, helpful/harmful `14/4`, harmful delta `-610c`.
- Post-observable-birth denominator: `7` rows, `-224c`, helpful/harmful `4/3`, harmful delta `-424c`.
- Best diagnostic zero-harm split was `exit_cents <= 72` with `8` rows and `+479c`, but that is not fresh proof.
- Best post-birth zero-harm split was `entry_depth >= 225.99` with only `2` rows and `+110c`, making it a post-hoc child idea rather than promotion evidence.
- Updated `probe_v28_next_action_triage.py`; new recommendation `downgrade_observable_reduce_loss_control_until_false_hold_guard_freezes`.
- Updated `probe_v28_current_direction_decision.py`; exit-policy evidence now carries the autopsy summaries and the direction text explicitly downgrades observable reduce-loss-control until a separate false-hold guard is frozen and earns rows.

Interpretation: the observable reduce branch still explains part of the loss-count churn, but current forward evidence says its p_hold reduce denominator is unsafe. Do not broaden reduce suppression from this branch. The only acceptable next step would be a physically plausible child guard with its own freeze and strict post-freeze evidence.

## Dual-Lane Same-Window Delta Autopsy 2026-05-07 16:30 UTC

Added `probe_v28_dual_lane_same_window_delta_autopsy.py` to explain why the current dual-lane forced strict precheck is trailing actual live v28 on the same post-freeze markets.

- Output: `logs\edge_research\v28_dual_lane_same_window_delta_autopsy_latest.md` and `.json`.
- The probe is research-only and does not affect live trading.
- Candidate forced precheck: `13` entries, W/L `11/2`, net `+45c`, full-loss cushion `0`.
- Live v28 on the same candidate markets: `12` markets, W/L `5/6`, net `+380c`, full-loss cushion `3`.
- Candidate minus live on the same markets: `-335c`.
- Deficit side: `5` rows totaling `-787c`; surplus side: `8` rows totaling `+452c`.
- Largest negative bucket: `candidate_positive_live_captured_more`, with `3` rows and `-555c` candidate-minus-live. These are not candidate losses; they are markets where the candidate was green but live captured much more.
- Second negative bucket: `candidate_loss_live_escape`, with `2` rows and `-232c`; live escaped both candidate losses.
- Updated `probe_v28_next_action_triage.py`; new recommendation `treat_dual_lane_same_window_delta_as_live_baseline_blocker`.
- Updated `probe_v28_current_direction_decision.py`; the `sidecar_live_test` evidence now includes the same-window delta autopsy and the direction text says the branch must prove both own-freeze gates and refreshed live-baseline superiority.

Interpretation: dual-lane remains watch-only for two independent reasons: own-freeze rows are not mature, and the current forced strict precheck is not beating live v28 on the same markets. The next checkpoint should not be framed as “does the candidate turn green?”; it must ask whether strict own-freeze evidence beats the refreshed live baseline after sample, source, coverage, and cushion gates.

## Live Baseline Refresh 2026-05-07 16:32 UTC

Refreshed the live-only v28 baseline before leaving the candidate-vs-live artifacts in their current state.

- Command environment:
  - `OUTPUT_STRATEGY_TAG=live_mushroom_v28_size2`
  - `LOG_SOURCE_TAG=live_mushroom_v28_size2`
  - `SCORE_MODE=live_only`
- Command: `python .\score_bot_log.py`
- Refreshed live result: `+$13.33` / `+1333c`, `626` entries, `515` completed round trips, W/L by sign `283/332`, `0` open positions.
- Regenerated:
  - `logs\edge_research\v28_dual_lane_same_window_live_compare_latest.md/json`
  - `logs\edge_research\v28_dual_lane_same_window_delta_autopsy_latest.md/json`
  - `logs\edge_research\v28_candidate_vs_live_full_table_latest.md/json`
  - `logs\edge_research\v28_candidate_pnl_tracker_latest.md/json`
  - `logs\edge_research\v28_goal_completion_audit_latest.md/json`
  - `logs\edge_research\v28_next_action_triage_latest.md/json`
  - `logs\edge_research\v28_current_direction_decision_latest.md/json`
  - `logs\edge_research\v28_exit_policy_watch_dashboard_latest.md/json`

Interpretation: the candidate-vs-live table now uses `1333c` as the live row. It still has `0` live-ready candidates. The top rows remain diagnostic or blocked by source/own-freeze/live-readiness gates, so the objective is not achieved.

## Dual-Lane Same-Window Sequence Mechanism 2026-05-07 16:34 UTC

Added `probe_v28_dual_lane_same_window_sequence_mechanism.py` to classify how live v28 beat the dual-lane forced precheck on the current deficit markets.

- Output: `logs\edge_research\v28_dual_lane_same_window_sequence_mechanism_latest.md` and `.json`.
- The probe is research-only and does not affect live trading.
- Largest mechanism bucket: `live_larger_terminal_exposure_same_side`, `2` rows, `-347c` candidate-minus-live. Live took larger same-side terminal winners while the candidate had small positive rows.
- Second bucket: `live_side_flip_escaped_candidate_loss`, `2` rows, `-232c` candidate-minus-live. Live took small same-side damage, then flipped/opposite-side won enough to escape the candidate loss.
- Third bucket: `live_same_side_exit_capture_scaled_better`, `1` row, `-208c` candidate-minus-live. Live captured the same side with larger size and a better exit path.
- Updated `probe_v28_next_action_triage.py` so the `treat_dual_lane_same_window_delta_as_live_baseline_blocker` recommendation includes the sequence mechanism.
- Updated `probe_v28_current_direction_decision.py` so the `sidecar_live_test` evidence carries the mechanism summary.

Interpretation: the dual-lane blocker is not just wrong direction. It is also missing live v28's stateful exposure behavior: scale on high-confidence terminal winners, repeated same-side exit capture, and side-flip escape after early damage. A repair should be tested as state/exposure sequencing, not as a post-hoc exclusion of the five deficit markets.

## Dual-Lane State/Exposure Sequence Repair 2026-05-07 16:38 UTC

Added `probe_v28_dual_lane_state_exposure_sequence_repair.py` to test simple observable exposure weights suggested by the same-window sequence mechanism.

- Output: `logs\edge_research\v28_dual_lane_state_exposure_sequence_repair_latest.md` and `.json`.
- The probe is diagnostic same-window research only; it does not freeze a candidate, change live logic, or place orders.
- Best diagnostic variant: `sequence_combo_strong2x_shrink50`.
- Best variant adjusted candidate net: `+146c`, improving baseline candidate by `+101c`.
- Same-window candidate-minus-live improves from `-335c` to `-234c`, but still trails live.
- Full-loss cushion remains `1`, below the required `>=3`.
- The best rule changes `9` weights, amplifies `0` losing rows, but shrinks `5` winning rows.
- Blockers: `diagnostic_only_same_window`, `not_frozen_forward`, `state_sequence_not_live_ready`, `still_trails_live_same_window`, `full_loss_cushion_lt_3`, `shrinks_winning_rows`, `does_not_beat_refreshed_live_baseline`.
- Updated `probe_v28_next_action_triage.py`; new recommendation `do_not_freeze_simple_dual_lane_exposure_weighting_yet`.
- Updated `probe_v28_current_direction_decision.py`; the sidecar/live-test decision now includes this exposure-repair result.

Interpretation: simple static exposure weighting is directionally useful but incomplete. It does not beat live on the same markets, does not clear cushion, and pays for loss shrinkage by shrinking winners. The repair direction should stay stateful: explicit state-transition/side-flip logic or patient own-freeze collection, not a frozen static weight from this tiny same-window diagnostic.

## Dual-Lane Side-Flip Feasibility 2026-05-07 16:42 UTC

Added `probe_v28_dual_lane_side_flip_feasibility.py` to test whether live v28's side-flip escapes are a broad repair signal or sparse hindsight.

- Output: `logs\edge_research\v28_dual_lane_side_flip_feasibility_latest.md` and `.json`.
- The probe is feasibility-only research and does not freeze a candidate, change live logic, or place orders.
- All post-freeze live markets: `13` markets, `48` trades, net `+314c`.
- All post-freeze side-flip markets: `2` of `13`, net `+68c`.
- Candidate markets: `13` markets, `43` live trades, net `+380c`.
- Candidate side-flip markets: `2`, net `+68c`.
- Candidate opposite-rescue markets: `2`, net `+68c`; both are the current candidate-loss escape examples.
- Blockers: `research_only`, `not_frozen_forward`, `side_flip_trigger_not_observable_from_static_candidate_row`, `opposite_rescue_sample_too_sparse`, `candidate_side_flip_sample_too_sparse`.
- Updated `probe_v28_next_action_triage.py`; new recommendation `do_not_freeze_side_flip_repair_without_observable_state_trigger`.
- Updated `probe_v28_current_direction_decision.py`; sidecar/live-test evidence now carries the side-flip feasibility summary.

Interpretation: side-flip escape is real in the current loss examples, but too sparse and too dependent on live sequence behavior to freeze from the current static candidate row. A future child would need an explicit observable state-transition trigger and its own forward rows.

## Loss-Churn Guarded Repair Frontier 2026-05-07 16:46 UTC

Refreshed `probe_v28_exit_repair_gap_classifier.py` first so the loss denominator matched the fresh live-loss escape audit, then added `probe_v28_loss_churn_guarded_repair_frontier.py`.

- Output: `logs\edge_research\v28_loss_churn_guarded_repair_frontier_latest.md` and `.json`.
- The probe is diagnostic loss-row research only. It does not freeze a candidate, change live logic, or place orders.
- Refreshed gap classifier now shows `73` loss rows, `56` unresolved rows, `19` no-observation rows, `37` matched-but-unchanged rows, `15` repair-flipped losses, and `2` repair-would-worsen rows.
- The clean diagnostic frontier's top row is `not_fv_entry_timing`: `34` selected loss rows, `34` loss flips, `+2426c` hold delta, `0` harmful rows. This is explanatory only because it relies on a diagnostic label, not a live-observable trigger.
- The best observable-only clean guard is `recross_ge_045`: `4` selected loss rows, `4` loss flips, `+328c` hold delta, `0` harmful rows, but it has `selected_loss_rows_lt_10`.
- Risky high-delta rules like `p_hold_ge_060` still select false holds: `20/4` helpful/harmful and `-510c` harmful delta.
- Updated `probe_v28_next_action_triage.py`; new recommendation `use_loss_churn_frontier_to_find_observable_state_trigger_not_hindsight_label`.
- Updated `probe_v28_current_direction_decision.py`; exit-policy evidence now includes both the diagnostic and observable clean frontier.

Interpretation: the loss-count blocker is now clearer. The missing repair is not "hold everything with decent p_hold"; that reopens false holds. The physical target is a live-observable state trigger that approximates the not-FV/entry-timing separation, with full-denominator replay and its own freeze before it can matter.
