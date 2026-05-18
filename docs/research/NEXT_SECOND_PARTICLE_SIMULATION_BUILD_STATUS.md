# Next-Second Particle Simulation Build Status

Updated: 2026-05-12

This is a research-only status map for the active goal. It is deliberately
strict: partial infrastructure is not treated as strategy proof.

## Current Artifacts

- Plan: `docs/research/NEXT_SECOND_PARTICLE_SIMULATION_PLAN.md`
- Side-safety OOS protocol:
  `docs/research/SIDE_SAFETY_OOS_PROTOCOL.md`
- Dynamic rolling-vol OOS protocol:
  `docs/research/DYNAMIC_ROLLING_VOL_OOS_PROTOCOL.md`
- Locked OOS run plan artifact:
  `logs/particle_research/locked_oos_plans/side_safety_oos_next_locked_plan.md`
- Dynamic rolling-vol locked OOS run plan artifact:
  `logs/particle_research/locked_oos_plans/dynamic_particle_next_locked_plan.md`
- Dynamic rolling-vol 600s locked OOS run plan artifact:
  `logs/particle_research/locked_oos_plans/dynamic_particle600_next_locked_plan.md`
- Side consensus-veto locked OOS run plan artifact:
  `logs/particle_research/locked_oos_plans/side_consensus_CONSENSUSLOCK001_locked_oos_plan.md`
- Residual blend locked OOS run plan artifact:
  `logs/particle_research/locked_oos_plans/residual_blend_RESIDLOCK001_locked_oos_plan.md`
- Research package: `research_particle/`
- Synthetic test suite: `test_research_particle_synthetic.py`
- Strict candidate context normalizer:
  `research_particle/candidate_contexts.py`
- Read-only top-of-book candidate source builder:
  `research_particle/read_only_candidate_source.py`
- Passive checkpoint candidate source builder:
  `research_particle/passive_checkpoint_source.py`
- v28 context-only source builder:
  `research_particle/v28_context_source.py`
- v28 live context tailer:
  `research_particle/v28_context_tailer.py`
- Independent public spot ticker recorder:
  `research_particle/spot_ticker_recorder.py`
- Paired public REST sidecar plus independent spot capture:
  `research_particle/paired_sidecar_spot_capture.py`
- Paired sidecar packet independent-spot enrichment:
  `research_particle/paired_sidecar_spot_enrichment.py`
- Paired sidecar tick-vs-candle probability diagnostic:
  `research_particle/paired_sidecar_spot_diagnostic.py`
- Aggregate paired sidecar tick-vs-candle diagnostic:
  `research_particle/paired_sidecar_spot_aggregate.py`
- Existing paired sidecar/spot evidence refresh:
  `research_particle/paired_sidecar_spot_refresh.py`
- Paired sidecar calibration/blend failure analysis:
  `research_particle/paired_sidecar_blend_failure_analysis.py`
- Paired sidecar predeclared slice locked-plan writer:
  `research_particle/paired_sidecar_slice_locked_plan.py`
- Paired sidecar predeclared slice OOS evaluator:
  `research_particle/paired_sidecar_slice_oos.py`
- Paired sidecar predeclared slice refresh/status runner:
  `research_particle/paired_sidecar_slice_refresh.py`
- Public REST sidecar batch selector:
  `build_v28_successor_public_rest_sidecar_batch.py`
- No-future independent spot/context merger:
  `research_particle/spot_context_merge.py`
- Bounded paired passive collector:
  `research_particle/paired_passive_shadow_run.py`
- Passive recorder bounded-run support:
  `research_native_passive_ws_recorder.py --run-seconds`
- Public Kalshi result fetcher:
  `research_particle/kalshi_market_results.py`
- Selection-threshold sweep:
  `research_particle/selection_sweep.py`
- Fixed probability anchor variant evaluator:
  `research_particle/probability_variants.py`
- Rolling-volatility particle replay evaluator:
  `research_particle/dynamic_particle_replay.py`
- Fixed ensemble probability diagnostic:
  `research_particle/ensemble_particle_replay.py`
- Residual probability blend LORO diagnostic:
  `research_particle/residual_blend_loro.py`
- Predeclared residual blend OOS evaluator:
  `research_particle/residual_blend_oos.py`
- Label-gated online logit calibration diagnostic:
  `research_particle/online_logit_particle_replay.py`
- Full decision exporter for diagnostic variants:
  `research_particle/materialized_variant_replay.py`
- EV/fill threshold sweep for diagnostic variants:
  `research_particle/materialized_variant_selection_sweep.py`
- Late time/regime blend materialized variants:
  `late300_mc50_online_logit_rv600`,
  `late300_mc75_online_logit_rv600`,
  `late300_consensus_mc75_online_logit_rv600`,
  `late180_mc75_online_logit_rv600`
- Side/regime instability diagnostic:
  `research_particle/side_regime_diagnostic.py`
- EV-rank/calibration stability diagnostic:
  `research_particle/ev_rank_calibration_diagnostic.py`
- Leave-one-run-out variant selector diagnostic:
  `research_particle/variant_loro_selection_diagnostic.py`
- PnL-aware selective classification threshold LORO diagnostic:
  `research_particle/pasc_loro_threshold_diagnostic.py`
- State-bucket anchor-switch LORO diagnostic:
  `research_particle/anchor_switch_loro.py`
- Market-cluster overfit diagnostic:
  `research_particle/market_cluster_diagnostic.py`
- Simple meta-probability LORO diagnostic:
  `research_particle/meta_probability_loro.py`
- Timestamp-available state-feature LORO diagnostic:
  `research_particle/state_feature_loro.py`
- Independent-spot microfeature LORO diagnostic:
  `research_particle/spot_micro_loro.py`
- Empirical next-second particle diagnostic:
  `research_particle/empirical_next_second_particle_diagnostic.py`
- Current-anchored empirical next-second diagnostic:
  `research_particle/empirical_current_anchor_diagnostic.py`
- Empirical market-opportunity diagnostic:
  `research_particle/empirical_market_opportunity_diagnostic.py`
- Next-second spot-drift terminal diagnostic:
  `research_particle/spot_drift_terminal_diagnostic.py`
- Next-second spot-drift regime diagnostic:
  `research_particle/spot_drift_regime_diagnostic.py`
- Conservative realized-vol current-residual LORO diagnostic:
  `research_particle/spot_rv_current_residual_loro.py`
- Fixed fat-tail/jump-mixture terminal diagnostic:
  `research_particle/fat_tail_particle_diagnostic.py`
- Predeclared fixed-terminal OOS evaluator:
  `research_particle/fixed_terminal_oos.py`
- Side-conditioned failure analysis:
  `research_particle/side_failure_analysis.py`
- Predeclared side-safety OOS evaluator:
  `research_particle/side_safety_oos.py`
- Predeclared dynamic rolling-vol OOS evaluator:
  `research_particle/dynamic_particle_oos.py`
- Predeclared side consensus-veto OOS evaluator:
  `research_particle/side_consensus_oos.py`
- Locked OOS run-plan writer:
  `research_particle/locked_oos_run_plan.py`
- Dynamic rolling-vol locked OOS run-plan writer:
  `research_particle/dynamic_particle_locked_oos_plan.py`
- Side consensus-veto locked OOS run-plan writer:
  `research_particle/side_consensus_locked_oos_plan.py`
- Residual blend locked OOS run-plan writer:
  `research_particle/residual_blend_locked_oos_plan.py`
- One-command offline shadow pipeline:
  `research_particle/shadow_pipeline.py`
- Synthetic smoke fixture:
  `logs/particle_research/synthetic_fixture_20260510_smoke/`
- Side-fill/source smoke fixture:
  `logs/particle_research/synthetic_fixture_20260511_fill_source_smoke/`
- Generic smoke replay report:
  `logs/particle_research/reports/synthetic_replay_20260510_smoke.md`
- Adapter readiness audit:
  `logs/particle_research/reports/particle_adapter_readiness_latest.md`
- v28 execution-event context audit:
  `logs/particle_research/reports/v28_event_contexts_exactgate_latest.md`
- Goal completion audit:
  `logs/particle_research/reports/particle_goal_completion_audit_latest.md`
- Locked OOS stability report:
  `logs/particle_research/reports/locked_oos_stability_latest.md`
- PASC threshold LORO diagnostic:
  `logs/particle_research/reports/pasc_loro_threshold_diagnostic_20260511_eight_locked_narrow.md`
- Anchor-switch LORO diagnostic:
  `logs/particle_research/reports/anchor_switch_loro_20260511_eight_locked.md`
- First shadow-run preflight:
  `logs/particle_research/reports/particle_shadow_run_preflight_latest.md`
- First real passive candidate denominator:
  `logs/particle_research/real_shadow/particle_shadow_readonly/`
- First real passive selection sweep:
  `logs/particle_research/real_shadow/particle_shadow_readonly/reports/passive_particle_selection_sweep.md`
- v28 context tailer real-log smoke:
  `logs/particle_research/real_shadow/particle_shadow_readonly/passive_context_tailer_smoke_status.json`
- Bounded paired forward smoke with seeded context:
  `logs/particle_research/real_shadow/particle_shadow_forward_20260511T053340Z-0dc86f34/`
- Longer bounded forward shadow capture:
  `logs/particle_research/real_shadow/particle_shadow_forward_20260511T053741Z-long900/`
- Longer forward fixed-anchor variant report:
  `logs/particle_research/real_shadow/particle_shadow_forward_20260511T053741Z-long900/reports/probability_variants_full_refresh.md`
- Longer forward rolling-vol particle report:
  `logs/particle_research/real_shadow/particle_shadow_forward_20260511T053741Z-long900/reports/dynamic_particle_full_refresh.md`
- Longer forward side failure report:
  `logs/particle_research/real_shadow/particle_shadow_forward_20260511T053741Z-long900/reports/side_failure_full_refresh.md`
- Same-sample side-safety OOS diagnostic:
  `logs/particle_research/real_shadow/particle_shadow_forward_20260511T053741Z-long900/reports/side_safety_oos_same_sample.md`
- Fresh locked side-safety OOS capture and report:
  `logs/particle_research/real_shadow/particle_side_safety_oos_20260511TLOCKED/`
- Fresh locked side-safety OOS report:
  `logs/particle_research/real_shadow/particle_side_safety_oos_20260511TLOCKED/reports/side_safety_oos_locked.md`
- Fresh dynamic rolling-vol same-sample diagnostic:
  `logs/particle_research/real_shadow/particle_side_safety_oos_20260511TLOCKED/reports/dynamic_particle_oos_same_sample.md`
- Fresh locked dynamic 300s OOS capture and report:
  `logs/particle_research/real_shadow/particle_dynamic_oos_20260511TLOCKEDNEXT/`
- Fresh locked dynamic 300s OOS report:
  `logs/particle_research/real_shadow/particle_dynamic_oos_20260511TLOCKEDNEXT/reports/dynamic_particle_oos_locked.md`
- Fresh locked dynamic 600s OOS capture and report:
  `logs/particle_research/real_shadow/particle_dynamic600_oos_20260511TLOCKEDNEXT2/`
- Fresh locked dynamic 600s OOS report:
  `logs/particle_research/real_shadow/particle_dynamic600_oos_20260511TLOCKEDNEXT2/reports/dynamic_particle_oos_locked.md`
- Locked OOS ensemble diagnostics:
  `logs/particle_research/real_shadow/*/reports/ensemble_particle_locked_oos_diagnostic.md`
- Locked OOS online-logit diagnostics:
  `logs/particle_research/real_shadow/*/reports/online_logit_particle_locked_oos_diagnostic.md`
- Materialized near-miss replay diagnostics:
  `logs/particle_research/real_shadow/*/reports/diagnostics_online_logit_market_mean_rolling_vol_600s.md`
- Materialized near-miss EV-threshold sweeps:
  `logs/particle_research/real_shadow/*/reports/selection_sweep_online_logit_market_mean_rolling_vol_600s.md`
- Fresh bounded read-only live capture and labeled replay:
  `logs/particle_research/real_shadow/particle_shadow_readonly_fresh_20260511T113926Z/reports/fresh_live_particle_replay.md`
- Market/current agreement veto diagnostic:
  `logs/particle_research/reports/market_agreement_veto_diagnostic_20260511.md`
- Consolidated side/regime diagnostic:
  `logs/particle_research/reports/side_regime_diagnostic_20260511.md`
- Independent Coinbase BTC-USD spot ticker smoke:
  `logs/particle_research/real_shadow/spot_ticker_smoke_coinbase_20260511T120626Z/`
- Paired passive + independent spot merge smoke:
  `logs/particle_research/real_shadow/particle_shadow_spotmerge_smoke_20260511T120911Z/`
- Paired spot-merge labeled replay:
  `logs/particle_research/real_shadow/particle_shadow_spotmerge_smoke_20260511T120911Z/reports/spotmerge_particle_replay.md`
- Longer independent-spot OOS capture:
  `logs/particle_research/real_shadow/particle_shadow_spotmerge_oos_20260511T121730Z/`
- Longer independent-spot OOS resolved-subset replay:
  `logs/particle_research/real_shadow/particle_shadow_spotmerge_oos_20260511T121730Z/reports/spotmerge_oos_replay_resolved_subset.md`
- Longer independent-spot OOS full replay:
  `logs/particle_research/real_shadow/particle_shadow_spotmerge_oos_20260511T121730Z/reports/spotmerge_oos_replay_full.md`
- Longer independent-spot side consensus-veto same-sample report:
  `logs/particle_research/real_shadow/particle_shadow_spotmerge_oos_20260511T121730Z/reports/side_consensus_spotmerge_oos_full_same_sample.md`
- Fresh locked side consensus-veto OOS capture:
  `logs/particle_research/real_shadow/particle_side_consensus_oos_CONSENSUSLOCK001/`
- Fresh locked side consensus-veto OOS report:
  `logs/particle_research/real_shadow/particle_side_consensus_oos_CONSENSUSLOCK001/reports/side_consensus_oos_locked.md`
- Fresh locked side consensus-veto diagnostic family reports:
  `logs/particle_research/real_shadow/particle_side_consensus_oos_CONSENSUSLOCK001/reports/*_locked_oos_diagnostic.md`
- Residual blend LORO diagnostic across the four locked roots:
  `logs/particle_research/reports/residual_blend_loro_locked_oos_latest.md`
- Five-run EV-rank/calibration diagnostic:
  `logs/particle_research/reports/ev_rank_calibration_diagnostic_20260511_five_locked.md`
- Five-run variant LORO selector diagnostic:
  `logs/particle_research/reports/variant_loro_selection_diagnostic_20260511_five_locked.md`
- Five-run market-cluster diagnostic:
  `logs/particle_research/reports/market_cluster_diagnostic_20260511_five_locked.md`
- Five-run meta-probability LORO diagnostic:
  `logs/particle_research/reports/meta_probability_loro_20260511_five_locked.md`
- Five-run timestamp-available state-feature LORO diagnostic:
  `logs/particle_research/reports/state_feature_loro_20260511_five_locked.md`
- Independent-spot microfeature LORO diagnostic on eligible tick roots:
  `logs/particle_research/reports/spot_micro_loro_20260511_two_tick_roots.md`
- Expanded independent-spot microfeature LORO diagnostic after GAUSS locks:
  `logs/particle_research/reports/spot_micro_loro_20260511_seven_locked.md`
- Empirical next-second particle diagnostic:
  `logs/particle_research/reports/empirical_next_second_particle_diagnostic_20260512_nine_locked.md`
- Current-anchored empirical next-second diagnostic:
  `logs/particle_research/reports/empirical_current_anchor_diagnostic_20260512_nine_locked.md`
- Empirical market-opportunity diagnostic:
  `logs/particle_research/reports/empirical_market_opportunity_diagnostic_20260512_nine_locked.md`
- Next-second spot-drift terminal diagnostic:
  `logs/particle_research/reports/spot_drift_terminal_diagnostic_20260511_nine_locked.md`
- Next-second spot-drift regime diagnostics:
  `logs/particle_research/reports/spot_drift_regime_diagnostic_20260511_best_locked.md`
  and
  `logs/particle_research/reports/spot_drift_regime_diagnostic_20260511_all_specs_locked.md`
- Independent-spot realized-vol terminal diagnostic:
  `logs/particle_research/reports/spot_realized_vol_terminal_20260511_seven_locked.md`
- Conservative realized-vol current-residual LORO diagnostic:
  `logs/particle_research/reports/spot_rv_current_residual_loro_20260511_nine_locked.md`
- Predeclared independent-spot realized-vol terminal locked OOS plan/report:
  `logs/particle_research/locked_oos_plans/particle_spot_rv_terminal_oos_RVTERMLOCK001_locked_oos_plan.md`
  and
  `logs/particle_research/real_shadow/particle_spot_rv_terminal_oos_RVTERMLOCK001/reports/spot_realized_vol_terminal_oos_locked.md`
- Materialized independent-spot realized-vol terminal replay/diagnostic:
  `logs/particle_research/real_shadow/particle_spot_rv_terminal_oos_RVTERMLOCK001/reports/materialized_spot_realized_vol_terminal_oos_locked.md`
  and
  `logs/particle_research/real_shadow/particle_spot_rv_terminal_oos_RVTERMLOCK001/reports/replay_diagnostics_spot_realized_vol_terminal_oos_locked.md`
- Fixed fat-tail/jump-mixture terminal diagnostic:
  `logs/particle_research/reports/fat_tail_particle_diagnostic_20260511_five_locked.md`
- Fixed low-vol terminal OOS command smoke on an existing root, same-sample only:
  `logs/particle_research/real_shadow/particle_residual_blend_oos_RESIDLOCK001/reports/fixed_terminal_oos_gaussian_vol45_same_sample.md`
- Predeclared fixed low-vol terminal locked OOS run plan:
  `logs/particle_research/locked_oos_plans/fixed_terminal_GAUSS45LOCK001_locked_oos_plan.md`
- Fresh locked fixed low-vol terminal OOS capture and report:
  `logs/particle_research/real_shadow/particle_fixed_terminal_oos_GAUSS45LOCK001/`
  and
  `logs/particle_research/real_shadow/particle_fixed_terminal_oos_GAUSS45LOCK001/reports/fixed_terminal_oos_locked.md`
- Second locked fixed low-vol terminal OOS plan/report:
  `logs/particle_research/locked_oos_plans/fixed_terminal_GAUSS45LOCK002_locked_oos_plan.md`
  and
  `logs/particle_research/real_shadow/particle_fixed_terminal_oos_GAUSS45LOCK002/reports/fixed_terminal_oos_locked.md`
- Third locked fixed low-vol terminal OOS plan/report:
  `logs/particle_research/locked_oos_plans/particle_fixed_terminal_oos_GAUSS45LOCK003_locked_oos_plan.md`
  and
  `logs/particle_research/real_shadow/particle_fixed_terminal_oos_GAUSS45LOCK003/reports/fixed_terminal_oos_locked.md`
- Locked OOS stability report, now including `RVTERMLOCK001`:
  `logs/particle_research/reports/locked_oos_stability_latest.md`
- Seven-run label-gated online anchor calibration diagnostic:
  `logs/particle_research/reports/online_anchor_calibration_diagnostic_20260511_seven_locked.md`
- Seven-run anchor regime profile:
  `logs/particle_research/reports/anchor_regime_profile_20260511_seven_locked.md`
- Fresh locked residual blend OOS capture and report:
  `logs/particle_research/real_shadow/particle_residual_blend_oos_RESIDLOCK001/`
  and
  `logs/particle_research/real_shadow/particle_residual_blend_oos_RESIDLOCK001/reports/residual_blend_oos_locked.md`
- Live public REST sidecar plus independent Coinbase spot paired capture:
  `logs/particle_research/real_shadow/sidecar_spot_pairs/20260512T035542Z-7097dc7a/paired_sidecar_spot_manifest.md`
- Second live public REST sidecar plus independent Coinbase spot paired capture:
  `logs/particle_research/real_shadow/sidecar_spot_pairs/20260512T041445Z-ef98a171/paired_sidecar_spot_manifest.md`
- Tick-enriched sidecar packet rows from that capture:
  `logs/particle_research/real_shadow/sidecar_spot_pairs/20260512T035542Z-7097dc7a/sidecar_packets_independent_spot_enriched.md`
- Tick-enriched sidecar packet rows from the second capture:
  `logs/particle_research/real_shadow/sidecar_spot_pairs/20260512T041445Z-ef98a171/sidecar_packets_independent_spot_enriched.md`
- Tick-vs-candle probability diagnostic for that capture:
  `logs/particle_research/real_shadow/sidecar_spot_pairs/20260512T035542Z-7097dc7a/sidecar_spot_tick_vs_candle_diagnostic.md`
- Tick-vs-candle probability diagnostic for the second capture:
  `logs/particle_research/real_shadow/sidecar_spot_pairs/20260512T041445Z-ef98a171/sidecar_spot_tick_vs_candle_diagnostic.md`
- Aggregate paired sidecar tick-vs-candle diagnostic:
  `logs/particle_research/reports/paired_sidecar_spot_aggregate_latest.md`
- Existing paired sidecar/spot refresh report:
  `logs/particle_research/reports/paired_sidecar_spot_refresh_latest.md`
- Paired sidecar label-gated online calibration diagnostic:
  `logs/particle_research/reports/paired_sidecar_online_calibration_latest.md`
- Paired sidecar calibration/blend failure analysis:
  `logs/particle_research/reports/paired_sidecar_blend_failure_analysis_latest.md`
- Predeclared paired sidecar slice locked plan:
  `logs/particle_research/locked_oos_plans/paired_sidecar_slice_PSLICELOCK001_locked_plan.md`
- Predeclared paired sidecar slice OOS report:
  `logs/particle_research/reports/paired_sidecar_slice_oos_PSLICELOCK001_latest.md`
- Predeclared paired sidecar smaller-blend comparison plan:
  `logs/particle_research/locked_oos_plans/paired_sidecar_slice_PSLICELOCK002_locked_plan.md`
- Predeclared paired sidecar smaller-blend comparison OOS report:
  `logs/particle_research/reports/paired_sidecar_slice_oos_PSLICELOCK002_latest.md`
- Predeclared paired sidecar v28-control comparison plan:
  `logs/particle_research/locked_oos_plans/paired_sidecar_slice_PSLICELOCK003_locked_plan.md`
- Predeclared paired sidecar v28-control comparison OOS report:
  `logs/particle_research/reports/paired_sidecar_slice_oos_PSLICELOCK003_latest.md`
- Predeclared paired sidecar slice refresh/status report:
  `logs/particle_research/reports/paired_sidecar_slice_refresh_latest.md`
- Paired sidecar slice lock comparison report:
  `logs/particle_research/reports/paired_sidecar_slice_lock_comparison_latest.md`
- Paired sidecar slice market-level breakdown report:
  `logs/particle_research/reports/paired_sidecar_slice_market_breakdown_latest.md`
- Predeclared paired sidecar candidate-v28 gap-slice comparison plans:
  `logs/particle_research/locked_oos_plans/paired_sidecar_slice_PSLICELOCK004_locked_plan.md`
  and
  `logs/particle_research/locked_oos_plans/paired_sidecar_slice_PSLICELOCK005_locked_plan.md`

## Latest Live-Market Shadow Status

- Post-lock paired sidecar run `20260512T150617Z-399fae39` has settled and
  joined successfully: `18` rows, `1` market
  (`KXBTC15M-26MAY121115-15`), and `0` diagnostic issues. It is valid
  live-market shadow evidence, but it landed about nine minutes before close
  and therefore does not enter the frozen `600s_plus` slice.
- Post-lock paired sidecar run `20260512T151904Z-f37288dc` has also settled and
  entered the frozen `600s_plus` evaluator: `18` slice rows, `1` market,
  `2` selected decisions, `-43.0c` selected PnL, `-86.0c` top-EV bucket PnL,
  and `promotion_safe=False`. This is useful negative locked-forward evidence:
  the locked blend lost to `v28` and `market_side_ask` on Brier/log-loss for
  that market.
- Post-lock paired sidecar run `20260512T153417Z-08393d73` has settled and
  entered the same evaluator. The frozen slice now has `36` rows across
  `2` markets, `11` selected decisions, `-137.5c` selected PnL,
  `-106.0c` top-EV bucket PnL, and `promotion_safe=False`. The locked blend is
  still losing to `v28` and `market_side_ask` on Brier/log-loss, with negative
  EV rank.
- Post-lock paired sidecar run `20260512T154820Z-803b6b12` has settled and
  joined. The frozen slice now has `54` rows across `3` markets, `12` selected
  decisions, `-171.0c` selected PnL, `-160.5c` top-EV bucket PnL, and
  `promotion_safe=False`. The locked blend still loses to `v28` and
  `market_side_ask` on Brier/log-loss and has negative EV rank.
- Current paired sidecar aggregate after the third locked-slice label refresh:
  `978` joined rows across `44` settled markets. The locked slice reports
  `72` post-lock fresh candidate rows, `4` fresh markets, `54` slice rows, and
  `3` slice markets, with `0` pending manifests at this checkpoint.
- Two follow-up locks were frozen after the failed `w20` evidence and therefore
  start with zero eligible rows: `PSLICELOCK002` tests
  `blend_v28_online_lr010_w05` in the same `600s_plus` slice, and
  `PSLICELOCK003` is a plain `v28` control. These are comparison locks only;
  neither can use rows at or before its own `locked_after_utc`.
- The completion audit now summarizes all `PSLICELOCK*` slice OOS reports:
  `paired_sidecar_slice_oos_report_count=3`,
  `paired_sidecar_slice_oos_promotion_safe=False`, and
  `complete=False`.
- The paired sidecar slice refresh runner now refreshes all sibling
  `paired_sidecar_slice_PSLICELOCK*_locked_plan.json` files in one command.
  Latest refresh table: `PSLICELOCK001` has `54` slice rows / `3` markets /
  `-171.0c`; `PSLICELOCK002` and `PSLICELOCK003` are correctly still at
  `0` eligible rows because they were frozen after that evidence.
- Post-lock paired sidecar run `20260512T161848Z-eb90c40e` has settled and
  entered all three slice evaluators. Current multi-lock results:
  `PSLICELOCK001` has `72` slice rows / `4` markets / `20` selected /
  `+2.0c` PnL but still loses to `v28` on Brier/log-loss and fails sample,
  market-share, and baseline gates; `PSLICELOCK002` has `18` rows / `1` market
  / `+265.5c`; `PSLICELOCK003` has `18` rows / `1` market / `+265.5c`. The
  new locks are positive on their first market but far below sample floors, so
  `promotion_safe=False` for all three.
- Post-lock paired sidecar run `20260512T164622Z-173f266e` has settled and
  entered all three frozen slice evaluators. Current all-lock results after
  that label refresh:
  `PSLICELOCK001` has `90` slice rows / `5` markets / `26` selected /
  `+36.0c`; `PSLICELOCK002` has `36` rows / `2` markets / `18` selected /
  `+351.0c`; `PSLICELOCK003` has `36` rows / `2` markets / `18` selected /
  `+351.0c`. The smaller blend remains behind the v28 control on
  Brier/log-loss, so it is positive but not particle-promotable.
- Post-lock paired sidecar run `20260512T170405Z-61c026fd` has settled and
  joined all three frozen slice evaluators. Current all-lock results after that
  label refresh: `PSLICELOCK001` has `108` slice rows / `6` markets /
  `34` selected / `-160.0c`; `PSLICELOCK002` has `54` rows / `3` markets /
  `18` selected / `+351.0c`; `PSLICELOCK003` has `54` rows / `3` markets /
  `18` selected / `+351.0c`.
- Added `paired_sidecar_slice_lock_comparison_latest`: `report_count=3`,
  `particle_like_count=2`, `particle_edge_candidate_count=0`, and best selected
  PnL from `blend_v28_w05_time_gt_600s_v1` at `+351.0c`. The smaller blend is
  still not particle edge: it matches the v28 control on selected PnL but trails
  it on Brier (`+0.003837` worse), log-loss (`+0.013367` worse), and top-EV PnL
  (`40.0c` worse).
- Post-lock paired sidecar run `20260512T173058Z-3208920c` has settled and
  joined all three frozen slice evaluators. Current all-lock results after that
  label refresh: `PSLICELOCK001` has `126` slice rows / `7` markets /
  `43` selected / `-569.5c`; `PSLICELOCK002` has `72` rows / `4` markets /
  `27` selected / `-58.5c`; `PSLICELOCK003` has `72` rows / `4` markets /
  `27` selected / `-58.5c`. The comparison report now concludes:
  no slice lock has positive selected PnL, and all remain non-promotable.
- Post-lock paired sidecar run `20260512T174933Z-58caa133` has settled and
  joined all three frozen slice evaluators. Current all-lock results after that
  label refresh: `PSLICELOCK001` has `144` slice rows / `8` markets /
  `49` selected / `-698.5c`; `PSLICELOCK002` has `90` rows / `5` markets /
  `27` selected / `-58.5c`; `PSLICELOCK003` has `90` rows / `5` markets /
  `27` selected / `-58.5c`. The comparison report remains decisive:
  `particle_edge_candidate_count=0`, no slice lock has positive selected PnL,
  and all remain non-promotable.
- Added `paired_sidecar_slice_market_breakdown_latest`: `plan_count=3`,
  `row_count=18`, `particle_like_negative_market_count=7`, and worst
  particle-like market row
  `blend_v28_w20_time_gt_600s_v1` on `KXBTC15M-26MAY121345-45` at `-409.5c`
  selected PnL. The main completion audit now includes this market-level
  failure evidence so aggregate slice totals cannot hide one-market damage.
- Froze a new predeclared candidate-vs-v28 disagreement slice test after the
  post-hoc diagnostic: `PSLICELOCK004` tests
  `blend_v28_online_lr010_w15` on
  `candidate_v28_disagreement_band=05_15pp`, and `PSLICELOCK005` is the same
  slice with `v28` as control. Both share
  `locked_after_utc=2026-05-12T18:23:29+00:00`. The immediate dry refresh
  proves both start with `0` eligible rows, so no prior evidence leaks into the
  fresh gates.
- Patched the slice-lock comparison report so zero-row fresh locks cannot be
  reported as the best selected-PnL lock. After refresh, `report_count=5`,
  `particle_edge_candidate_count=0`, and the best nonempty selected-PnL lock is
  still `blend_v28_w05_time_gt_600s_v1` at `-58.5c`.
- Captured and labeled the first forward market after `PSLICELOCK004/005`:
  `20260512T183027Z-88c06e8a` / `KXBTC15M-26MAY121445-45`. It had
  `871.021s` to close and a candidate-v28 gap of about `6.74pp`, so it entered
  the new `05_15pp` gap-slice locks. Result: both the blend candidate and v28
  control have `2` rows / `1` market / `1` selected / `-45.5c`, so the
  post-hoc gap-slice idea failed its first forward market.
- Captured and labeled one more valid `600s_plus` forward market:
  `20260512T184902Z-0d41a88e` / `KXBTC15M-26MAY121500-00`. It had `656.265s`
  to close, but its candidate-v28 gap was about `16.1pp`, so it did not enter
  `PSLICELOCK004/005`. Current all-lock replay after settlement:
  `PSLICELOCK001` has `180` rows / `10` markets / `67` selected / `-509.5c`;
  `PSLICELOCK002` has `126` rows / `7` markets / `45` selected / `+130.5c`;
  `PSLICELOCK003` has the same `+130.5c`; `PSLICELOCK004` and `005` remain
  `-45.5c`. The comparison report says positive locked-slice PnL exists only
  where the particle-like lock ties v28, so `particle_edge_candidate_count=0`
  and promotion remains blocked.
- Captured and labeled `20260512T190636Z-de79eb7f` /
  `KXBTC15M-26MAY121515-15`. It had `502.904s` to close and a candidate-v28
  gap of about `2.90pp`, so it missed both the `600s_plus` and `05_15pp`
  frozen slices. Aggregate sidecar evidence increased to `1122` rows / `52`
  markets; all locked slice metrics stayed unchanged.
- Added an outcome-free pending-slice preview to
  `paired_sidecar_slice_refresh_latest`: before labels arrive, the refresh now
  counts pending fresh rows/markets and pending slice rows/markets for each
  frozen lock using only decision-time fields. A live capture at
  `20260512T193101Z-a6f364c4` proved the preview works before labels: it showed the
  pending market would enter all three broad `600s_plus` locks at `18` rows /
  `1` market, and would not enter the `05_15pp` gap-slice locks.
- Labeled that pending 15:45 ET market and replayed all locks. Aggregate
  sidecar evidence is now `1140` rows / `53` markets. The broad locks worsened:
  `PSLICELOCK001` is `198` rows / `11` markets / `76` selected / `-735.0c`;
  `PSLICELOCK002` is `144` rows / `8` markets / `52` selected / `-174.0c`;
  `PSLICELOCK003` is `144` rows / `8` markets / `54` selected / `-261.0c`.
  `PSLICELOCK004/005` remain `2` rows / `1` market / `-45.5c`. The comparison
  report is back to no positive selected-PnL lock at all:
  `particle_edge_candidate_count=0`, `promotion_safe_count=0`,
  `complete=False`.
- Added the research-only slice retirement/veto report:
  `logs/particle_research/reports/paired_sidecar_slice_retirement_latest.md`.
  It classifies particle-like locks into retire/watchlist/continue states using
  locked comparison output only, and never authorizes live trading. Current
  output after the 16:00 ET label refresh: `row_count=5`,
  `particle_like_count=3`, `retire_count=2`, `watchlist_count=1`,
  `candidate_for_broader_audit_count=0`. The broad `w20` and `w05` locks are
  now `retire_negative_forward_evidence`; the gap-slice `w15` lock remains
  `watchlist_negative_underpowered`.
- Labeled the `20260512T195142Z-049862e6` gap-slice preview sample. Aggregate sidecar
  evidence is now `1158` rows / `54` markets. `PSLICELOCK004/005` increased to
  `3` rows / `2` markets / `2` selected / `-56.7c`, with the blend candidate
  still tying the v28 control and losing on Brier. Main audit remains
  `complete=False`, with `paired_sidecar_slice_retirement_retire_count=2` and
  `particle_edge_candidate_count=0`.
- Captured and labeled one more early-window 16:15 ET market. The pending
  preview correctly predicted it would enter every frozen lock: `18` broad
  `600s_plus` rows and `2` gap-slice rows. After settlement, aggregate sidecar
  evidence is `1176` rows / `55` markets. The broad `w05` lock rebounded to
  `+523.5c`, but the v28 control is also positive at `+436.5c`; `w05` still
  loses to v28 on Brier/log-loss and ties v28 on top-EV PnL. The gap-slice
  blend now beats v28 on Brier/log-loss, but selected PnL and top-EV PnL are
  tied with v28 (`+20.8c` selected, `-11.2c` top-EV). The comparison report
  therefore still has `particle_edge_candidate_count=0`,
  `promotion_safe_count=0`, and `complete=False`. The retirement report shifted
  back to `retire_count=0`, `continue_shadow_count=3`, which shows why these
  locks remain shadow-only rather than promoted or permanently trusted.
- Verification after the pending-field/multi-lock/market-breakdown/gap-slice
  audit and pending-preview patches: `python -m unittest
  test_v28_successor_pipeline.py` passed `106` tests, and `python -m unittest
  test_research_particle_synthetic.py` passed `108` tests.
  `probe_particle_goal_completion_audit.py` remains `complete=False`; this is
  correct because the real-data probability, EV-rank, and shadow-PnL gates are
  still not cleared.

## Prompt-to-Artifact Checklist

| Requirement | Current evidence | Status |
| --- | --- | --- |
| Research-only next-second particle simulation system | `research_particle/` package is separate from live bot files and has no order placement code. `research_particle/shadow_collect.py` is a JSONL collector CLI, not an order runner. `research_particle/paired_sidecar_spot_capture.py` pairs public sidecar snapshots with independent public spot ticks and marks `promotion_allowed=False` by construction. `research_particle/paired_sidecar_spot_enrichment.py` turns that paired capture into tick-enriched packet rows without modifying frozen sidecar rows. | Partial |
| Predict terminal settlement probability | `research_particle/terminal_projection.py` has Brownian terminal probability, terminal sample simulation, weighted `P(S_T > strike)`, and shared strike probabilities. `research_particle/particle_engine.py` turns a `CandidateSnapshot` into deterministic `particle_p_yes`, Brownian baseline, market baseline, calibrated point/interval, and EV fields. | Partial |
| Calibrate probability online | `research_particle/calibrators.py` has a label-gated ACI-style interval wrapper and an `OnlineLogitCalibrator`; both update only after labels. `research_particle/replay_runner.py` has `evaluate_online_calibrated_replay`, which predicts each row before queuing its label update and applies only prior labels whose `label_available_ts_utc` is at or before the next decision timestamp. `research_particle/reports.py --online-calibrated` writes online-calibrated replay reports. `research_particle/online_logit_particle_replay.py` tests smooth online-logit point calibration across particle/current/dynamic/ensemble raw sources, with both candidate-weighted and market-clustered update modes, but remains diagnostic-only. `research_particle/online_anchor_calibration_diagnostic.py` now tests label-gated online-logit calibration of Brownian, particle, market, current, and Brownian/particle/market anchor blends; across seven locked roots it did not clear strict gates. `research_particle/paired_sidecar_online_calibration.py` now applies label-gated online logit calibration to the live paired sidecar aggregate, delaying updates until the source capture's market close; after hitting the predeclared live-shadow floor (`906` rows / `40` settled markets), it improves raw candidate Brier/log-loss (`0.293685/0.997760` to `0.258442/0.738256`) and top-EV bucket PnL (`-243.6c` to `+767.8c`), but standalone market-stability is still not enough (`18/40` positive top-EV markets and `21/40` positive selected-PnL markets). Fixed tiny blends show marginal signal (`blend_v28_online_lr010_w10` best row-weighted Brier, `blend_market_online_lr010_w15` best row-weighted log-loss, and `blend_v28_online_lr010_w25` best blend by market-equal Brier with `23/40` positive top-EV and selected-PnL markets), but the canonical aggregate still blocks promotion: `v28` wins row-weighted Brier, `market_side_ask` wins row-weighted log-loss, and `candle_brownian` wins equal-market Brier/log-loss. `research_particle/paired_sidecar_blend_failure_analysis.py` now makes that blocker explicit: best blend `blend_v28_online_lr010_w25` has better market-equal Brier than `candle_brownian` by `-0.004236`, but worse market-equal log-loss by `+0.002004`, with only `23/40` positive top-EV markets and a worst selected-PnL market of `-648.0c`. Its post-hoc slice candidates are diagnostic only and require fresh predeclared shadow validation. `research_particle/paired_sidecar_slice_locked_plan.py` froze the calibrated/blended slice `blend_v28_online_lr010_w20` with `time_to_close_band=600s_plus` under `PSLICELOCK001` at `2026-05-12T14:44:16+00:00`; `research_particle/paired_sidecar_slice_oos.py` correctly excludes all rows at or before that lock and currently reports `0` fresh rows / `0` markets, so this path is predeclared but not yet validated. `research_particle/paired_sidecar_slice_refresh.py` now refreshes the existing paired evidence, online calibration, failure analysis, and locked-slice OOS status in one research-only command; its first run did not collect (`collect_requested=False`) and still reports `0` post-lock slice rows. | Partial |
| Convert probability into fee/fill-adjusted expected PnL | `research_particle/ev_decision.py` has EV, break-even probability, realized PnL, and fill stats helpers. `CandidateSnapshot` now supports optional `yes_fill_prob` and `no_fill_prob`; `particle_engine.py` and `replay_runner.py` use side-specific fill probabilities when present and fall back to conservative `fill_prob`. `research_particle/selection_sweep.py` sweeps predeclared EV/fill thresholds on the same all-candidate denominator to expose threshold sensitivity. `research_particle/materialized_variant_selection_sweep.py` applies the same threshold sweep after materializing a diagnostic variant into the strict replay denominator. `research_particle/paired_sidecar_slice_oos.py` recomputes EV and counterfactual PnL from `p_yes`, side, ask, and predeclared `fee_cents`, `assumed_fill_probability`, and `no_fill_penalty_cents` rather than reusing softer diagnostic EV columns. | Partial |
| Validate every decision on all-candidate denominator | `research_particle/recorders.py` records candidate snapshots, including skipped/rejected/no-fill/traded states by caller-supplied reason. `research_particle/replay_runner.py` evaluates every loaded candidate row and reports `all_candidate_denominator=True`. `research_particle/read_only_candidate_source.py` converts exact read-only top-of-book observations into raw candidate rows with implied YES/NO asks and side-specific fill. `research_particle/passive_checkpoint_source.py` converts passive recorder `orderbook_checkpoint` rows plus explicit timestamped BTC/model context into the same strict candidate shape, selecting only the latest context available at or before the checkpoint timestamp and now accepting checkpoint globs. `research_particle/v28_context_source.py` extracts context-only BTC/model fields from v28 telemetry without using v28 quotes; `research_particle/v28_context_tailer.py` does the same incrementally for forward passive runs and can seed the latest timestamp-available pre-existing context per market before following fresh rows. `research_particle/paired_passive_shadow_run.py` starts/stops both passive collectors under a fresh run id. `research_particle/shadow_adapter.py` now preserves timestamp-available freshness/depth metadata such as `book_age_ms`, `btc_age_ms`, `depth_count`, and `depth_ratio` into future candidate extras for later strict analysis. `research_particle/denominator_integrity_audit.py` verifies real replay reports against their candidate files and labels: candidate file count, `source_candidate_count`, `candidate_count`, and decision count must match; `skipped_unlabeled_count=0`; `denominator_scope=all_labeled_candidates`; `all_candidate_denominator=True`; every candidate market has a label. The nine locked roots passed with `candidate_count=33205`, `market_count=51`, `issue_count=0`, and `pass_denominator_integrity=True`. | Done for locked artifacts |
| Trustworthy recorder/labeler for all candidate moments, not just fills | `CandidateSnapshotRecorder`, `SettlementLabelRecorder`, `label_candidate`, `read_only_candidate_source.py`, `passive_checkpoint_source.py`, `v28_context_source.py`, `v28_context_tailer.py`, `spot_ticker_recorder.py`, `spot_context_merge.py`, `paired_passive_shadow_run.py`, `paired_sidecar_spot_capture.py`, `paired_sidecar_spot_enrichment.py`, `kalshi_market_results.py`, `candidate_contexts.py`, `ShadowCandidateAdapter`, `shadow_collect.py`, `shadow_pipeline.py`, `selection_sweep.py`, `market_result_labels.py`, `artifact_leakage_audit.py`, and `denominator_integrity_audit.py` exist; tests verify JSONL output, label availability timing, complete context recording, strict raw-context normalization, exact implied ask construction, passive checkpoint conversion with timestamp-available context selection, side-specific fill preservation, refusal of missing/late fields, generated particle prediction recording, settlement label recording, one-command pipeline replay/manifest creation, market-result binary label context generation, passive checkpoint glob support, v28 context-only extraction/tailing/seeding, independent spot parsing, no-future spot/context merging by local receive time, sidecar/spot pairing by latest local-receive-time tick at or before sidecar bundle capture, sidecar packet enrichment by latest no-future spot tick, resolved/unresolved Kalshi result handling, selection-threshold sensitivity reporting, no-future artifact leakage auditing, and all-candidate denominator integrity auditing. The nine locked roots now pass both artifact audits: `artifact_issue_count=0`, `denominator_issue_count=0`, `candidate_count=33205`, and `market_count=51`. | Done for locked artifacts |
| Synthetic Brownian/jump tests pass before Kalshi replay | `python -m unittest test_research_particle_synthetic.py` now passes 108 tests, including Brownian CDF, jump direction, weighted/resampled, label timing, EV, no-fill, side-specific fill replay selection, shared-sample, replay leakage, particle engine determinism, strict candidate context normalization, read-only source conversion, passive checkpoint conversion with future-context leak prevention, checkpoint glob support, v28 context-only extraction/tailing/seeding, independent spot parsing/merge behavior, paired-run independent spot parser flags, Kalshi result parsing, selection-threshold sweep reporting, materialized variant replay/sweep reporting, probability-variant reporting, rolling-vol estimator/replay reporting, dynamic rolling-vol OOS promotion blocking, dynamic locked OOS plan writing, locked-run stability reporting, ensemble diagnostics, residual blend LORO diagnostics, variant LORO selector diagnostics, PASC threshold LORO diagnostics, anchor-switch LORO diagnostics, RV-aware anchor-switch LORO diagnostics, conservative RV current-residual LORO diagnostics, empirical next-second particle diagnostics, current-anchored empirical next-second diagnostics, empirical market-opportunity diagnostics, next-second spot-drift terminal diagnostics, next-second spot-drift regime diagnostics, market-cluster diagnostics, anchor-regime profiling, meta-probability LORO diagnostics, state-feature LORO diagnostics, independent-spot microfeature LORO diagnostics, fixed fat-tail/jump-mixture terminal diagnostics, fixed low-vol terminal OOS promotion blocking, fixed low-vol terminal locked OOS plan writing, independent-spot realized-vol terminal diagnostics and locked-plan writing, residual blend OOS promotion blocking/passing locked-scope gates on synthetic data, residual blend locked OOS plan writing, EV-rank/calibration diagnostics, online-logit calibration diagnostics, online anchor calibration diagnostics, side-failure counterfactual reporting, same-sample side-safety promotion blocking, side consensus-veto OOS promotion blocking/passing locked-scope gates on synthetic data, independent-spot locked side-consensus plan writing, locked OOS run-plan manifest writing, online calibration no-peek order, completion-audit promotion/stability separation, nested real-report audit detection, shadow adapter/collector strictness, shadow pipeline replay/manifest creation, v28 event adapter strictness, market-result label building, explicit resolved-subset reporting, replay diagnostics, and end-to-end synthetic JSONL replay/reporting. | Done for first synthetic layer |
| Strict replay uses only timestamp-available information | `research_particle/replay.py` refuses records with `recv_ts_utc` after decision time. `research_particle/replay_runner.py` rejects candidate snapshots received after decision timestamp and rejects settlement labels available at/before decision. Online replay applies only queued labels that became available before the next decision. `research_particle/artifact_leakage_audit.py` now verifies real candidate/label artifacts directly: candidate `recv_ts_utc <= decision_ts_utc`, labels unavailable until after decision, settlement after decision, no missing labels, and no timestamped extra fields from the future. The nine locked roots passed this audit with `run_count=9`, `candidate_count=33205`, `label_count=51`, `market_count=51`, `issue_count=0`, and `pass_no_future_leakage=True`. Unit tests cover both passing artifacts and injected leak cases. | Done for locked artifacts |
| Particle probabilities beat Brownian, market mid, and current calibrated probability on Brier/log loss | `research_particle/replay_runner.py` scores particle, Brownian, market, and current calibrated baselines. `research_particle/particle_engine.py` keeps `particle_calibrated_p_yes` separate from caller-supplied `current_calibrated_p_yes`, so the particle calibrator cannot accidentally overwrite the existing baseline. `research_particle/probability_variants.py` evaluates fixed same-sample anchor variants without marking them promotion-safe. `research_particle/dynamic_particle_replay.py` evaluates rolling-vol particle variants using only chronological spot observations at or before each decision. `research_particle/dynamic_particle_oos.py` wraps predeclared rolling-vol hypotheses with locked-OOS gates. `research_particle/ensemble_particle_replay.py` and `research_particle/online_logit_particle_replay.py` add diagnostic-only ensemble/calibration families. `research_particle/ev_rank_calibration_diagnostic.py` now summarizes probability calibration and EV-rank buckets across locked replay JSONs. `research_particle/market_cluster_diagnostic.py` equal-weights resolved markets to expose repeated-label overfitting. `research_particle/meta_probability_loro.py` tests simple market-cluster-trained logit meta-probability layers on locked holdouts. `research_particle/state_feature_loro.py` tests timestamp-available market state features on the same leave-one-run-out locked holdouts. `research_particle/spot_micro_loro.py` tests independent public spot microfeatures from ticks available before each decision where those ticks exist. `research_particle/fat_tail_particle_diagnostic.py` tests fixed non-Gaussian terminal jump-mixture assumptions and lower/higher Gaussian vol assumptions without fitting thresholds. Synthetic smoke report shows particle beats all three. Real locked evidence is mixed but still failing: `rolling_vol_300s_v1` beat all three probability baselines but missed the current-calibrated PnL gate; `rolling_vol_600s_v1` failed probability gates against market/current on its fresh lock. Candidate-weighted online logit over-updated repeated same-market labels and was unstable. Market-clustered online logit fixed that blow-up and became the best aggregate PnL row (`online_logit_market_mean_rolling_vol_600s`, `+82411c`), but still only beat market/current in 2 of 3 locked runs and had positive EV rank in 2 of 3. The five-run stability report found no stable candidate that beat Brownian/market/current on every locked run. The five-run EV-rank/calibration diagnostic across 16,931 live-shadow candidates found `current_calibrated` best by candidate-weighted Brier/log-loss (`0.165260/0.479494`), while particle was worse (`0.181858/0.540726`). The equal-market diagnostic across 27 resolved markets confirmed the same ordering: `current_calibrated=0.130024/0.414496`, `market=0.131034/0.415895`, `particle=0.166264/0.514537`. The simple meta-probability LORO failed every strict holdout gate; best summary row `logit_current` still lost `-141229c`, beat current in `0/5`, and had worse mean Brier/log-loss (`0.197074/0.556644`). The state-feature LORO also failed every strict holdout gate; best summary row `state_moneyness_time` lost `-140527c`, beat current in `0/5`, and had worse mean Brier/log-loss (`0.225548/0.664205`). The expanded independent-spot microfeature LORO now has `4` eligible roots and `3` skipped roots after the GAUSS captures; it still failed every strict holdout gate. Best row `spot_phi_returns` made only `+5532c`, beat Brownian/market/current in `0/4`, and had mean Brier/log-loss `0.429433/5.529054`. The fixed fat-tail/jump-mixture diagnostic did not support fat tails; the best row was lower-vol Gaussian `gaussian_vol45`, with `+99334c` aggregate and mean Brier/log-loss `0.171052/0.507782`, but it beat current in only `1/5` runs and cleared `0/5` strict gates. The fresh predeclared `RVTERMLOCK001` live-shadow run made the local realized-vol terminal family look useful on PnL (`+17528c`) but not on probability: Brier/log-loss `0.133252/0.430335`, weaker than `current_calibrated` at `0.122272/0.374592`, and `promotion_safe=False`. | Failing strict stability |
| EV ranking positive and top predicted EV buckets profitable | `research_particle/replay_runner.py` reports EV rank sign and top EV bucket PnL. `research_particle/ev_rank_calibration_diagnostic.py` now buckets every locked replay decision by predicted EV rank and reports whether the highest-EV bucket is positive in every run. `research_particle/market_cluster_diagnostic.py` repeats the EV-rank question after collapsing candidates to equal-weighted markets. Synthetic smoke report: `ev_rank_correlation_sign=0.600000`, `top_ev_bucket_pnl_cents=39.0000`. `rolling_vol_300s_v1` had positive EV rank/top bucket on its fresh lock. `rolling_vol_600s_v1` had positive top bucket but negative EV rank on its fresh lock. The fresh locked side consensus-veto report had positive PnL and EV rank, but failed the top-EV-bucket gate (`consensus_top_ev_bucket_pnl_cents=-6.2407`). The five-run stability report found no variant with positive EV rank, positive top bucket, and probability beats on every locked run. The five-run EV-rank/calibration diagnostic found the highest predicted EV bucket positive in only `1/5` runs (`total=+766c`, `min_run=-4192c`, `avg=+0.2261c`), while lower EV buckets did better. The equal-market diagnostic was worse: market-level EV rank was `-0.139601`, and the highest-EV market bucket averaged `-0.3545c` per candidate with only `1/6` positive markets. EV ranking itself remains untrustworthy. | Failing strict stability |
| Shadow counterfactual PnL positive after fees and predeclared no-fill assumptions | `ReplayConfig` predeclares min EV, min fill, no-fill penalty, and counterfactual fill policy. Synthetic smoke reports: `total_counterfactual_pnl_cents=141.0000`. First real passive labeled smoke, longer full replay, fresh read-only replay, paired spot-merge labeled replay, and the longer independent-spot OOS replay were negative; the spot-merge smoke replay was `-502c` on 29 all-labeled candidates, the longer independent-spot resolved subset was `-10645c` on 556 labeled candidates, and the full longer independent-spot replay was `-4638c` on 663 all-labeled candidates. The predeclared `side_safe_yes_only_v1` locked OOS run decisively failed: base particle replay was `+14916c`, but YES-only side-safe was `-13150c`, proving the same-sample side effect was unstable. The fresh locked side consensus-veto run protected against a deeply negative base replay (`-32502c`) and made `+1447c`, but it failed promotion because the top EV bucket was negative and the underlying particle probability did not beat the baselines. The predeclared residual blend OOS lock then failed badly (`-28864c`). After adding the missing residual-root ensemble diagnostic, the strongest aggregate PnL/Brier row across five locked roots is now `probability:current_particle_75_25` (`+94765c`, mean Brier `0.164645`), but it beats current in only `2/5` runs and `stable_candidate_count=0`, so there is still no promoted particle replacement. `RVTERMLOCK001` was a real live-market shadow capture with no particle trades; static particle lost `-2384c`, while current calibrated made `+28435c` and the predeclared realized-vol terminal variant made `+17528c` but failed current/probability/EV-rank/top-bucket gates. | Promising diagnostic; locked follow-up required |
| Selection threshold and side/regime sensitivity are visible before promotion | `research_particle/selection_sweep.py` evaluates a grid of EV/fill thresholds without changing the replay denominator. `research_particle/side_regime_diagnostic.py` groups strict replay decisions by side, market/current consensus, confidence, time-to-close, and predeclared keep/skip rules. `research_particle/side_consensus_oos.py` now formalizes `skip_against_market_current_consensus_10_v1` as a locked OOS hypothesis with candidate/market/selected/PnL/EV/top-bucket/all-denominator gates, and `research_particle/side_consensus_locked_oos_plan.py` writes a fresh independent-spot run plan before any collection. First real passive sweep over 50 threshold rows found `positive_nonzero_rows=0`; longer forward resolved/full sweeps also found `positive_nonzero_rows=0`. The fresh locked side-safety capture finally produced `positive_nonzero_rows=45`, with the best base static particle row at `+14916c`; this improves the plumbing evidence but still does not promote the original particle probability because it failed market/current calibration baselines. The consolidated side/regime diagnostic across five locked reports found `stable_positive_rules=0`, so simple consensus/time vetoes are not enough. The new independent-spot full sweep again found `positive_nonzero_rows=0`; single-run side/regime diagnostics surfaced `skip_against_consensus_10` as a possible locked-OOS hypothesis. The same-sample formalized report kept 183 of 649 selected trades and made `+356c`, but `promotion_safe=False` because scope was same-sample and the top EV bucket remained negative. The fresh locked consensus-veto replay kept 429 of 3,029 selected base trades and made `+1447c`, but again failed `positive_top_ev_bucket`; the base EV/fill threshold sweep still had `positive_nonzero_rows=0`. | Partial |
| No social, pinball, or neural layer promoted unless it improves locked OOS | Plan explicitly gates these layers; no such layer exists in the research package. The side-safety OOS plan is deliberately non-neural and locks one simple side overlay before collection. | Maintained |
| Live trading untouched until shadow evidence clears gates | Work so far added research-only files and tests; no live bot launcher, state, order logic, or process control was changed. | Maintained |
| Completion audit blocks premature done/promote calls | `probe_particle_goal_completion_audit.py` maps each explicit goal requirement to concrete artifact evidence and currently reports `complete=False`, `strict_real_candidate_rows=34943`, `real_replay_reports=36`, `locked_oos_stability_rows=43`, and `locked_oos_stable_candidate_count=0`. The audit marks real-data probability, EV-rank, and shadow-PnL gates as `fail` when only single-report wins exist and locked-OOS stability is still zero. | Maintained |
| First real shadow run has a launch preflight | `probe_particle_shadow_run_preflight.py` checks env/private-key presence, passive recorder script presence, v28 context tailer presence, paired runner presence, passive checkpoint rows, timestamped context rows, and market result rows, then writes command templates for recorder, context tailer, paired bounded collection, pipeline replay, and online-calibrated replay. Current workspace result: `ready_to_collect=True`, `ready_to_pipeline=True`, `context_tailer_exists=True`, `paired_runner_exists=True`, `checkpoint_row_count=72`, `context_row_count=60`, `market_results_row_count=1`. | Partial |

## Verification Run

Command:

```powershell
python -m unittest test_research_particle_synthetic.py -v
python probe_particle_shadow_run_preflight.py
python -m compileall research_particle probe_particle_v28_event_contexts.py probe_particle_adapter_readiness.py probe_particle_shadow_run_preflight.py probe_particle_goal_completion_audit.py research_native_passive_ws_recorder.py
python probe_particle_goal_completion_audit.py
python -m research_particle.v28_context_tailer --input logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\execution_events.ndjson --output logs\particle_research\real_shadow\particle_shadow_readonly\passive_contexts_tailer_smoke.ndjson --issues logs\particle_research\real_shadow\particle_shadow_readonly\passive_context_tailer_smoke_issues.ndjson --status logs\particle_research\real_shadow\particle_shadow_readonly\passive_context_tailer_smoke_status.json --market-ticker KXBTC15M-26MAY110115-15 --settlement-ts-utc 2026-05-11T05:15:00Z
python -m research_particle.paired_passive_shadow_run --run-seconds 30 --checkpoint-interval-seconds 1 --checkpoint-depth 5 --status-interval-seconds 5
python -m research_particle.shadow_pipeline --source-type passive_checkpoint --checkpoints "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\research_data\particle_shadow_forward_20260511T053340Z-0dc86f34\book_checkpoints\**\*.ndjson" --contexts "logs\particle_research\real_shadow\particle_shadow_forward_20260511T053340Z-0dc86f34\passive_contexts.ndjson" --root "logs\particle_research\real_shadow\particle_shadow_forward_20260511T053340Z-0dc86f34" --annualized-vol 0.65 --sample-count 2000 --seed 1 --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.paired_passive_shadow_run --dataset particle_shadow_forward_20260511T053741Z-long900 --run-id 20260511T053741Z-long900 --run-seconds 900 --checkpoint-interval-seconds 1 --checkpoint-depth 5 --status-interval-seconds 10
python -m research_particle.shadow_pipeline --source-type passive_checkpoint --checkpoints "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\research_data\particle_shadow_forward_20260511T053741Z-long900\book_checkpoints\**\*.ndjson" --contexts "logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\passive_contexts.ndjson" --root "logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900" --annualized-vol 0.65 --sample-count 2000 --seed 1 --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.kalshi_market_results --ticker KXBTC15M-26MAY110145-45 --ticker KXBTC15M-26MAY110200-00 --output logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\market_results.json --issues logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\market_result_issues.json
python -m research_particle.market_result_labels --candidates logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\candidate_snapshots\candidate_snapshots.ndjson --market-results logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\market_results.json --output logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\pipeline_work\label_contexts.ndjson
python -m research_particle.shadow_collect labels --input logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\pipeline_work\label_contexts.ndjson --root logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900 --source kalshi_public_markets
python -m research_particle.reports --candidates logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\settlement_labels\settlement_labels.ndjson --output-dir logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\reports --stem passive_particle_replay_resolved_subset --allow-missing-labels --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.reports --candidates logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\settlement_labels\settlement_labels.ndjson --output-dir logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\reports --stem online_calibrated_particle_replay_resolved_subset --online-calibrated --allow-missing-labels --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.selection_sweep --candidates logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\settlement_labels\settlement_labels.ndjson --output-dir logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\reports --stem passive_particle_selection_sweep_resolved_subset --allow-missing-labels --min-ev-grid 0,1,2,3,5,8,10,12,15,20 --min-fill-grid 0,0.25,0.5,0.75,1.0 --counterfactual-fill-threshold 0.5
python -m research_particle.probability_variants --candidates logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\pipeline_work\label_contexts_full_refresh.ndjson --output-dir logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\reports --stem probability_variants_full_refresh --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.dynamic_particle_replay --candidates logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\pipeline_work\label_contexts_full_refresh.ndjson --output-dir logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\reports --stem dynamic_particle_full_refresh --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.side_failure_analysis --candidates logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\pipeline_work\label_contexts_full_refresh.ndjson --output-dir logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\reports --stem side_failure_full_refresh --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.side_safety_oos --candidates logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\pipeline_work\label_contexts_full_refresh.ndjson --output-dir logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\reports --stem side_safety_oos_same_sample --evaluation-scope same_sample_diagnostic --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.locked_oos_run_plan --run-id 20260511TLOCKED-SIDESAFE --dataset particle_side_safety_oos_20260511TLOCKED --output-dir logs\particle_research\locked_oos_plans --stem side_safety_oos_next_locked_plan --run-seconds 3900 --gate-min-candidates 500 --gate-min-markets 4 --gate-min-selected 100
python -m research_particle.v28_context_source --input logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\execution_events.ndjson --output logs\particle_research\real_shadow\particle_shadow_readonly\passive_contexts.ndjson --issues logs\particle_research\real_shadow\particle_shadow_readonly\passive_context_issues.ndjson --market-ticker KXBTC15M-26MAY110115-15 --start-ts-utc 2026-05-11T05:00:00Z --end-ts-utc 2026-05-11T05:04:15Z --settlement-ts-utc 2026-05-11T05:15:00Z
python -m research_particle.shadow_pipeline --source-type passive_checkpoint --checkpoints "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\research_data\particle_shadow_readonly\book_checkpoints\**\*.ndjson" --contexts logs\particle_research\real_shadow\particle_shadow_readonly\passive_contexts.ndjson --root logs\particle_research\real_shadow\particle_shadow_readonly --annualized-vol 0.65 --sample-count 2000 --seed 1 --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.kalshi_market_results --ticker KXBTC15M-26MAY110115-15 --output logs\particle_research\real_shadow\particle_shadow_readonly\market_results.json --issues logs\particle_research\real_shadow\particle_shadow_readonly\market_result_issues.json
python -m research_particle.market_result_labels --candidates logs\particle_research\real_shadow\particle_shadow_readonly\candidate_snapshots\candidate_snapshots.ndjson --market-results logs\particle_research\real_shadow\particle_shadow_readonly\market_results.json --output logs\particle_research\real_shadow\particle_shadow_readonly\pipeline_work\label_contexts.ndjson
python -m research_particle.shadow_collect labels --input logs\particle_research\real_shadow\particle_shadow_readonly\pipeline_work\label_contexts.ndjson --root logs\particle_research\real_shadow\particle_shadow_readonly --source kalshi_public_markets
python -m research_particle.reports --candidates logs\particle_research\real_shadow\particle_shadow_readonly\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_shadow_readonly\settlement_labels\settlement_labels.ndjson --output-dir logs\particle_research\real_shadow\particle_shadow_readonly\reports --stem passive_particle_replay --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.reports --candidates logs\particle_research\real_shadow\particle_shadow_readonly\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_shadow_readonly\settlement_labels\settlement_labels.ndjson --output-dir logs\particle_research\real_shadow\particle_shadow_readonly\reports --stem online_calibrated_particle_replay --online-calibrated --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.selection_sweep --candidates logs\particle_research\real_shadow\particle_shadow_readonly\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_shadow_readonly\settlement_labels\settlement_labels.ndjson --output-dir logs\particle_research\real_shadow\particle_shadow_readonly\reports --stem passive_particle_selection_sweep --min-ev-grid 0,1,2,3,5,8,10,12,15,20 --min-fill-grid 0,0.25,0.5,0.75,1.0 --counterfactual-fill-threshold 0.5
python -m research_particle.synthetic_fixture --root logs/particle_research/synthetic_fixture_20260511_fill_source_smoke
python -m research_particle.synthetic_fixture --root logs/particle_research/synthetic_fixture_20260510_smoke
python -m research_particle.reports --candidates logs/particle_research/synthetic_fixture_20260510_smoke/candidate_snapshots/candidate_snapshots.ndjson --labels logs/particle_research/synthetic_fixture_20260510_smoke/settlement_labels/settlement_labels.ndjson --output-dir logs/particle_research/reports --stem synthetic_replay_20260510_smoke --min-ev-cents 1 --min-fill-prob 0.5 --counterfactual-fill-policy threshold --counterfactual-fill-threshold 0.5
python probe_particle_adapter_readiness.py
python probe_particle_v28_event_contexts.py --input logs/live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio/execution_events.ndjson --stem v28_event_contexts_exactgate_latest --annualized-vol 0.65
python -m research_particle.spot_ticker_recorder --output logs\particle_research\real_shadow\spot_ticker_smoke_coinbase_20260511T120626Z\spot_ticks.ndjson --issues logs\particle_research\real_shadow\spot_ticker_smoke_coinbase_20260511T120626Z\spot_issues.ndjson --status logs\particle_research\real_shadow\spot_ticker_smoke_coinbase_20260511T120626Z\spot_status.json --run-seconds 5 --max-rows 5
python -m research_particle.paired_passive_shadow_run --dataset particle_shadow_spotmerge_smoke_20260511T120911Z --run-id 20260511T120911Z --run-seconds 30 --checkpoint-interval-seconds 1 --checkpoint-depth 5 --status-interval-seconds 5 --record-independent-spot --independent-spot-feed coinbase --independent-spot-max-age-ms 5000
python -m research_particle.shadow_pipeline --source-type passive_checkpoint --checkpoints "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\research_data\particle_shadow_spotmerge_smoke_20260511T120911Z\book_checkpoints\**\*.ndjson" --contexts "logs\particle_research\real_shadow\particle_shadow_spotmerge_smoke_20260511T120911Z\passive_contexts_independent_spot.ndjson" --root "logs\particle_research\real_shadow\particle_shadow_spotmerge_smoke_20260511T120911Z" --annualized-vol 0.65 --sample-count 2000 --seed 1 --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.paired_passive_shadow_run --dataset particle_shadow_spotmerge_oos_20260511T121730Z --run-id 20260511T121730Z --run-seconds 900 --checkpoint-interval-seconds 1 --checkpoint-depth 5 --status-interval-seconds 10 --record-independent-spot --independent-spot-feed coinbase --independent-spot-max-age-ms 5000 --require-independent-spot
python -m research_particle.shadow_pipeline --source-type passive_checkpoint --checkpoints "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\research_data\particle_shadow_spotmerge_oos_20260511T121730Z\book_checkpoints\**\*.ndjson" --contexts "logs\particle_research\real_shadow\particle_shadow_spotmerge_oos_20260511T121730Z\passive_contexts_independent_spot.ndjson" --root "logs\particle_research\real_shadow\particle_shadow_spotmerge_oos_20260511T121730Z" --annualized-vol 0.65 --sample-count 2000 --seed 1 --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.reports --candidates logs\particle_research\real_shadow\particle_shadow_spotmerge_oos_20260511T121730Z\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_shadow_spotmerge_oos_20260511T121730Z\settlement_labels\settlement_labels.ndjson --output-dir logs\particle_research\real_shadow\particle_shadow_spotmerge_oos_20260511T121730Z\reports --stem spotmerge_oos_replay_resolved_subset --allow-missing-labels --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.side_consensus_oos --candidates "logs\particle_research\real_shadow\particle_shadow_spotmerge_oos_20260511T121730Z\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_shadow_spotmerge_oos_20260511T121730Z\pipeline_work\label_contexts_full.ndjson" --output-dir "logs\particle_research\real_shadow\particle_shadow_spotmerge_oos_20260511T121730Z\reports" --stem side_consensus_spotmerge_oos_full_same_sample --evaluation-scope same_sample_diagnostic --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5 --gate-min-candidates 500 --gate-min-markets 2 --gate-min-selected 100 --consensus-min-confidence 0.10
python -m research_particle.side_consensus_locked_oos_plan --run-id CONSENSUSLOCK001 --dataset particle_side_consensus_oos_CONSENSUSLOCK001 --run-seconds 3900 --gate-min-candidates 1000 --gate-min-markets 5 --gate-min-selected 100 --output-dir logs\particle_research\locked_oos_plans --stem side_consensus_CONSENSUSLOCK001_locked_oos_plan
python -m research_particle.paired_passive_shadow_run --dataset particle_side_consensus_oos_CONSENSUSLOCK001 --run-id CONSENSUSLOCK001 --run-seconds 3900 --checkpoint-interval-seconds 1 --checkpoint-depth 5 --status-interval-seconds 10 --record-independent-spot --independent-spot-feed coinbase --independent-spot-max-age-ms 5000 --require-independent-spot
python -m research_particle.shadow_pipeline --source-type passive_checkpoint --checkpoints "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\research_data\particle_side_consensus_oos_CONSENSUSLOCK001\book_checkpoints\**\*.ndjson" --contexts "logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\passive_contexts_independent_spot.ndjson" --root "logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001" --annualized-vol 0.65 --sample-count 2000 --seed 1 --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.kalshi_market_results --ticker KXBTC15M-26MAY110900-00 --ticker KXBTC15M-26MAY110915-15 --ticker KXBTC15M-26MAY110930-30 --ticker KXBTC15M-26MAY110945-45 --ticker KXBTC15M-26MAY111000-00 --ticker KXBTC15M-26MAY111015-15 --output logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\market_results_full_refresh.json --issues logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\market_result_issues_full_refresh.json
python -m research_particle.market_result_labels --candidates logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\candidate_snapshots\candidate_snapshots.ndjson --market-results logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\market_results_full_final.json --output logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\pipeline_work\label_contexts_full_refresh.ndjson
python -m research_particle.reports --candidates logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\pipeline_work\label_contexts_full_refresh.ndjson --output-dir logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\reports --stem passive_particle_replay_locked_oos --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.side_consensus_oos --candidates logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\pipeline_work\label_contexts_full_refresh.ndjson --output-dir logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\reports --stem side_consensus_oos_locked --hypothesis-id skip_against_market_current_consensus_10_v1 --evaluation-scope locked_oos_shadow --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5 --gate-min-candidates 1000 --gate-min-markets 5 --gate-min-selected 100 --consensus-min-confidence 0.1
python -m research_particle.oos_stability_report --report-root logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED --report-root logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT --report-root logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2 --report-root logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001 --report-root logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001 --output-dir logs\particle_research\reports --stem locked_oos_stability_latest --min-runs-for-stability 2
python -m research_particle.ev_rank_calibration_diagnostic --report logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\reports\passive_particle_replay_locked_oos.json --report logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT\reports\passive_particle_replay_locked_oos.json --report logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\reports\passive_particle_replay_locked_oos.json --report logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\reports\passive_particle_replay_locked_oos.json --report logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\reports\passive_particle_replay_locked_oos.json --output-dir logs\particle_research\reports --stem ev_rank_calibration_diagnostic_20260511_five_locked
python -m research_particle.market_cluster_diagnostic --report logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\reports\passive_particle_replay_locked_oos.json --report logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT\reports\passive_particle_replay_locked_oos.json --report logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\reports\passive_particle_replay_locked_oos.json --report logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001\reports\passive_particle_replay_locked_oos.json --report logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\reports\passive_particle_replay_locked_oos.json --output-dir logs\particle_research\reports --stem market_cluster_diagnostic_20260511_five_locked
python -m research_particle.variant_loro_selection_diagnostic --stability-report logs\particle_research\reports\locked_oos_stability_latest.json --output-dir logs\particle_research\reports --stem variant_loro_selection_diagnostic_20260511_five_locked
python -m research_particle.meta_probability_loro --run-root logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED --run-root logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT --run-root logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2 --run-root logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001 --run-root logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001 --output-dir logs\particle_research\reports --stem meta_probability_loro_20260511_five_locked --epochs 1200 --learning-rate 0.08 --l2 0.20 --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.residual_blend_loro --report-root logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED --report-root logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT --report-root logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2 --report-root logs\particle_research\real_shadow\particle_side_consensus_oos_CONSENSUSLOCK001 --output-dir logs\particle_research\reports --stem residual_blend_loro_locked_oos_latest --max-exact-global 5
python -m research_particle.residual_blend_locked_oos_plan --run-id RESIDLOCK001 --dataset particle_residual_blend_oos_RESIDLOCK001 --run-seconds 3900 --gate-min-candidates 1000 --gate-min-markets 5 --gate-min-selected 250 --output-dir logs\particle_research\locked_oos_plans --stem residual_blend_RESIDLOCK001_locked_oos_plan
python -m research_particle.paired_passive_shadow_run --dataset particle_residual_blend_oos_RESIDLOCK001 --run-id RESIDLOCK001 --run-seconds 3900 --checkpoint-interval-seconds 1 --checkpoint-depth 5 --status-interval-seconds 10 --record-independent-spot --independent-spot-feed coinbase --independent-spot-max-age-ms 5000 --require-independent-spot
python -m research_particle.shadow_pipeline --source-type passive_checkpoint --checkpoints "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\research_data\particle_residual_blend_oos_RESIDLOCK001\book_checkpoints\**\*.ndjson" --contexts "logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\passive_contexts_independent_spot.ndjson" --root "logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001" --annualized-vol 0.65 --sample-count 2000 --seed 1 --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.kalshi_market_results --ticker KXBTC15M-26MAY111115-15 --ticker KXBTC15M-26MAY111130-30 --ticker KXBTC15M-26MAY111145-45 --ticker KXBTC15M-26MAY111200-00 --ticker KXBTC15M-26MAY111215-15 --output logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\market_results_full_refresh.json --issues logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\market_result_issues_full_refresh.json
python -m research_particle.market_result_labels --candidates logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\candidate_snapshots\candidate_snapshots.ndjson --market-results logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\market_results_full_refresh.json --output logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\pipeline_work\label_contexts_full_refresh.ndjson
python -m research_particle.reports --candidates "logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\pipeline_work\label_contexts_full_refresh.ndjson" --output-dir "logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\reports" --stem passive_particle_replay_locked_oos --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
python -m research_particle.residual_blend_oos --candidates "logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\pipeline_work\label_contexts_full_refresh.ndjson" --output-dir "logs\particle_research\real_shadow\particle_residual_blend_oos_RESIDLOCK001\reports" --stem residual_blend_oos_locked --hypothesis-id resid_current_rv300n20_rv600p20_particle_n10_v1 --evaluation-scope locked_oos_shadow --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5 --gate-min-candidates 1000 --gate-min-markets 5 --gate-min-selected 250
```

Result on 2026-05-11:

- `Ran 80 tests ... OK`
- shadow run preflight: `ready_to_collect=True`, `ready_to_pipeline=True`,
  `context_tailer_exists=True`, `paired_runner_exists=True`,
  `checkpoint_row_count=72`, `context_row_count=60`,
  `market_results_row_count=1`
- `compileall` completed for `research_particle`,
  `probe_particle_v28_event_contexts.py`,
  `probe_particle_adapter_readiness.py`,
  `probe_particle_shadow_run_preflight.py`, and
  `probe_particle_goal_completion_audit.py`; targeted compile also covered
  `research_native_passive_ws_recorder.py`,
  `research_particle/v28_context_tailer.py`, and
  `research_particle/paired_passive_shadow_run.py`
- v28 context tailer one-shot smoke: `contexts_written=188`,
  `issue_count=13`, `skipped_other_market=4312`, `status=stopped`;
  issue rows were malformed target-market telemetry missing core v28 context
  fields.
- first bounded paired smoke before context seeding:
  `checkpoint_row_count=29`, `context_row_count=7`; pipeline produced
  `recorded_candidates=17`, `context_issues=0`, with 12 source rows skipped
  because no context had appeared yet.
- seeded bounded paired smoke:
  `dataset=particle_shadow_forward_20260511T053340Z-0dc86f34`,
  `recorder_returncode=0`, `tailer_returncode=0`,
  `checkpoint_row_count=29`, `context_row_count=34`,
  `seeded_contexts=23`, `context_issue_count=0`; strict pipeline produced
  `recorded_candidates=29`, `contexts_written=29`, `context_issues=0`,
  `labels_written=0`.
- independent spot ticker smoke:
  `dataset=spot_ticker_smoke_coinbase_20260511T120626Z`,
  `source=coinbase_btcusd_matches`, `status=max_rows_reached`,
  `ticks_written=5`, `issue_count=0`. The Binance global endpoint smoke failed
  with `HTTP 451`, so the usable default is Coinbase while Binance remains an
  explicit optional feed.
- paired passive + independent spot merge smoke:
  `dataset=particle_shadow_spotmerge_smoke_20260511T120911Z`,
  `recorder_returncode=0`, `tailer_returncode=0`,
  `independent_spot_returncode=0`, `checkpoint_row_count=29`,
  `context_row_count=58`, `independent_spot_row_count=221`,
  `merged_context_row_count=58`, `merged_context_issue_count=49`. The merge
  issues were stale/missing independent spot for seeded pre-run contexts and
  were preserved as original contexts because `--require-independent-spot` was
  not used. The generated pipeline command used
  `passive_contexts_independent_spot.ndjson` and produced
  `recorded_candidates=29`, `contexts_written=29`, `context_issues=0`;
  21 candidate contexts used `merged_independent_spot_context` and 8 retained
  `v28_context_tailer_seed`.
- paired spot-merge labeled replay:
  market `KXBTC15M-26MAY110815-15` finalized `no`; replay used
  `candidate_count=29`, `source_candidate_count=29`,
  `skipped_unlabeled_count=0`, `denominator_scope=all_labeled_candidates`,
  and `all_candidate_denominator=True`. It lost
  `total_counterfactual_pnl_cents=-502.0000`: particle beat Brownian only
  (`particle_brier=0.135131`, `brownian_brier=0.136086`) and failed market
  and current (`market_brier=0.028410`,
  `current_calibrated_brier=0.051250`). Diagnostics show all selected trades
  were YES while the market settled NO.
- longer independent-spot OOS capture:
  `dataset=particle_shadow_spotmerge_oos_20260511T121730Z`,
  `recorder_returncode=0`, `tailer_returncode=0`,
  `independent_spot_returncode=0`, `checkpoint_row_count=772`,
  `context_row_count=237`, `context_issue_count=4`,
  `independent_spot_row_count=6590`, `merged_context_row_count=187`,
  `merged_context_issue_count=50`. This run used
  `--require-independent-spot`, so only fresh local-receive-time spot contexts
  were retained in `passive_contexts_independent_spot.ndjson`.
- longer independent-spot OOS pipeline:
  `raw_written=663`, `raw_issues=109`, `contexts_written=663`,
  `context_issues=0`, `recorded_candidates=663`, with 556 candidates from
  `KXBTC15M-26MAY110830-30` and 107 candidates from
  `KXBTC15M-26MAY110845-45`.
- longer independent-spot OOS resolved-subset replay:
  first market finalized `yes`; second was still active at first refresh. The
  resolved subset had `candidate_count=556`,
  `source_candidate_count=663`, `skipped_unlabeled_count=107`,
  `denominator_scope=resolved_labeled_subset`, `selected_count=544`, and
  `total_counterfactual_pnl_cents=-10645.0000`. Particle again beat Brownian
  only and failed market/current (`particle_brier=0.141411`,
  `market_brier=0.069923`, `current_calibrated_brier=0.078148`). Selection
  sweep found `positive_nonzero_rows=0`; side/regime diagnostic found
  `stable_positive_rules=0`.
- longer independent-spot OOS full replay:
  both markets finalized (`KXBTC15M-26MAY110830-30=yes`,
  `KXBTC15M-26MAY110845-45=no`). Full replay used
  `candidate_count=663`, `source_candidate_count=663`,
  `skipped_unlabeled_count=0`, `denominator_scope=all_labeled_candidates`,
  `selected_count=649`, and `total_counterfactual_pnl_cents=-4638.0000`.
  Particle beat Brownian only (`particle_brier=0.164121`,
  `brownian_brier=0.164457`) and failed market/current
  (`market_brier=0.118342`, `current_calibrated_brier=0.122689`);
  `ev_rank_correlation_sign=-0.008592`,
  `top_ev_bucket_pnl_cents=-16.1988`.
- longer independent-spot OOS diagnostic families:
  fixed probability variants and dynamic rolling-vol variants were all
  non-promotable on the full all-labeled denominator. The best fixed variant
  by Brier/PnL was `market` (`pnl_cents=0.0000` because it mostly abstained
  under the current EV threshold). The best dynamic-vol PnL row was
  `rolling_vol_600s` with `pnl_cents=-5496.0000`. Full selection sweep found
  `positive_nonzero_rows=0`.
- longer independent-spot side/regime diagnostic:
  on this single run only, `skip_against_consensus_10` was positive
  (`selected=183`, `pnl_cents=356.0000`), as were the tiny
  `require_market_agreement`/`require_market_current_consensus_alignment`
  rules (`selected=9`, `pnl_cents=224.0000`). This is not promotion evidence;
  it is a candidate for a predeclared fresh locked OOS plan.
- longer independent-spot side consensus-veto same-sample report:
  `hypothesis_id=skip_against_market_current_consensus_10_v1`,
  `evaluation_scope=same_sample_diagnostic`, `candidate_count=663`,
  `market_count=2`, `base_selected_count=649`,
  `base_total_counterfactual_pnl_cents=-4638c`,
  `consensus_selected_count=183`,
  `consensus_total_counterfactual_pnl_cents=356c`,
  `blocked_against_consensus_count=466`, and
  `blocked_against_consensus_loss_avoided_cents=4994c`.
  It is still not promotable: `promotion_safe=False`,
  `locked_oos_scope=False`, and
  `consensus_top_ev_bucket_pnl_cents=-15.2174`.
- locked OOS run plan for fresh side consensus-veto evidence:
  `dataset=particle_side_consensus_oos_CONSENSUSLOCK001`,
  `run_id=CONSENSUSLOCK001`, `run_seconds=3900`,
  `hypothesis_id=skip_against_market_current_consensus_10_v1`,
  `evaluation_scope=locked_oos_shadow`, independent spot feed `coinbase`,
  `--require-independent-spot`, gates `1000 candidates`, `5 markets`,
  `100 selected`, positive PnL, positive EV rank/top bucket, all-candidate
  denominator, and beats-base PnL. The plan writes commands only and starts no
  process.
- fresh locked side consensus-veto capture:
  `dataset=particle_side_consensus_oos_CONSENSUSLOCK001`,
  `recorder_returncode=0`, `tailer_returncode=0`,
  `independent_spot_returncode=0`, `checkpoint_file_count=6`,
  `checkpoint_row_count=3520`, `context_row_count=892`,
  `context_issue_count=14`, `independent_spot_row_count=37344`,
  `independent_spot_issue_count=0`, `merged_context_row_count=840`,
  `merged_context_issue_count=52`, with
  `context_path_for_pipeline=passive_contexts_independent_spot.ndjson`.
- fresh locked side consensus-veto strict pipeline:
  `raw_written=3260`, `raw_issues=260`, `contexts_written=3260`,
  `context_issues=0`, `recorded_candidates=3260`. Market results were fetched
  for all six captured tickers; the final ticker initially hit a public API
  `429` and succeeded on retry, producing
  `market_results_full_final.json` with six finalized labels.
- fresh locked side consensus-veto base replay:
  `candidate_count=3260`, `source_candidate_count=3260`,
  `skipped_unlabeled_count=0`, `denominator_scope=all_labeled_candidates`,
  `selected_count=3029`, `total_counterfactual_pnl_cents=-32502c`,
  `particle_beats_brownian=False`, `particle_beats_market=False`,
  `particle_beats_current_calibrated=False`, `ev_rank_correlation_sign=-0.011048`,
  and `top_ev_bucket_pnl_cents=-6.5460`.
- fresh locked side consensus-veto OOS report:
  `hypothesis_id=skip_against_market_current_consensus_10_v1`,
  `evaluation_scope=locked_oos_shadow`, `market_count=6`,
  `consensus_selected_count=429`,
  `consensus_total_counterfactual_pnl_cents=1447c`,
  `consensus_ev_rank_correlation_sign=0.129008`,
  `blocked_against_consensus_count=2600`,
  `blocked_against_consensus_loss_avoided_cents=33949c`,
  `promotion_safe=False`. The only failed gate was
  `positive_top_ev_bucket=False`
  (`consensus_top_ev_bucket_pnl_cents=-6.2407`).
- fresh locked side consensus-veto diagnostics:
  probability variants found `best_by_brier=current_calibrated` and
  `best_by_pnl=current_calibrated`, with
  `best_by_pnl_total_counterfactual_pnl_cents=36023c`.
  Dynamic rolling-vol variants remained negative (`best_by_pnl=rolling_vol_300s_market25`,
  `-3848c`). Ensemble blend `blend_40current_30rv300_30rv600` made
  `+17149c`, and online logit `online_logit_current_calibrated` made
  `+12528c`; both are diagnostic only. Base selection sweep again found
  `positive_nonzero_rows=0`.
- longer bounded forward capture:
  `dataset=particle_shadow_forward_20260511T053741Z-long900`,
  `recorder_returncode=0`, `tailer_returncode=0`,
  `checkpoint_file_count=2`, `checkpoint_row_count=818`,
  `context_row_count=724`, `context_issue_count=185`,
  `seeded_contexts=23`
- longer forward strict pipeline:
  `raw_written=753`, `raw_issues=65`, `contexts_written=753`,
  `context_issues=0`, `recorded_candidates=753`, `labels_written=0`;
  all 65 source issues were `checkpoint missing yes_bid_prices`.
- longer forward market results:
  first market `KXBTC15M-26MAY110145-45` finalized `no`; second market
  `KXBTC15M-26MAY110200-00` was still `closed` but unresolved at refresh.
- longer forward resolved-subset replay:
  `candidate_count=333`, `source_candidate_count=753`,
  `skipped_unlabeled_count=420`,
  `denominator_scope=resolved_labeled_subset`,
  `selected_count=333`, `total_counterfactual_pnl_cents=-1487.0000`,
  `particle_beats_brownian=False`, `particle_beats_market=False`,
  `particle_beats_current_calibrated=False`,
  `ev_rank_correlation_sign=-0.310591`,
  `top_ev_bucket_pnl_cents=-4.5595`
- longer forward online-calibrated resolved-subset replay:
  `candidate_count=333`, `source_candidate_count=753`,
  `skipped_unlabeled_count=420`, `coverage_rate=0.066066`,
  `online_beats_raw_particle=False`, `online_beats_brownian=False`,
  `online_beats_market=False`,
  `online_beats_current_calibrated=False`
- longer forward resolved-subset selection sweep:
  `grid_rows=50`, `positive_nonzero_rows=0`
- longer forward full replay after both markets finalized:
  `candidate_count=753`, `source_candidate_count=753`,
  `skipped_unlabeled_count=0`, `denominator_scope=all_labeled_candidates`,
  `selected_count=676`, `total_counterfactual_pnl_cents=-4876.0000`,
  `particle_beats_brownian=False`, `particle_beats_market=False`,
  `particle_beats_current_calibrated=False`,
  `ev_rank_correlation_sign=0.016009`,
  `top_ev_bucket_pnl_cents=-4.2910`
- longer forward full online-calibrated replay:
  `candidate_count=753`, `selected_count=676`, `coverage_rate=0.029216`,
  `online_beats_raw_particle=False`, `online_beats_brownian=False`,
  `online_beats_market=False`,
  `online_beats_current_calibrated=False`
- longer forward full selection sweep:
  `grid_rows=50`, `positive_nonzero_rows=0`
- longer forward replay diagnostics:
  `particle_brier_minus_market_brier=0.048476`,
  `particle_brier_minus_current_brier=0.033415`,
  `selected_yes_pnl_cents=4193.0000`,
  `selected_no_pnl_cents=-9069.0000`; the largest failure is NO selection,
  especially in the second market where NO selections lost `-9069c`.
- longer forward fixed-anchor probability variants:
  `candidate_count=753`, `source_candidate_count=753`,
  `skipped_unlabeled_count=0`, `denominator_scope=all_labeled_candidates`,
  `best_by_brier=market`, `best_by_pnl=market`,
  `promotion_safe=False`; market had Brier/log-loss `0.120628/0.362241`
  and `0c` PnL on 36 selected rows, while the best blend by calibration
  (`market_current_50_50`) had Brier/log-loss `0.126774/0.390282` but
  lost `-3532c`.
- longer forward rolling-vol particle variants:
  `candidate_count=753`, `source_candidate_count=753`,
  `skipped_unlabeled_count=0`, `denominator_scope=all_labeled_candidates`,
  `best_by_brier=rolling_vol_300s_market25`,
  `best_by_pnl=rolling_vol_120s`, `promotion_safe=False`;
  best Brier/log-loss was `0.129443/0.380267`, but the same variant lost
  `-8781c`; best PnL was still `-8669c`. Rolling-vol improved some
  probability scores versus Brownian/current but worsened EV selection.
- longer forward side failure analysis:
  `candidate_count=753`, `source_candidate_count=753`,
  `skipped_unlabeled_count=0`, `selected_count=676`,
  `base_total_counterfactual_pnl_cents=-4876c`,
  `forced_yes_total_counterfactual_pnl_cents=4193c`,
  `forced_no_total_counterfactual_pnl_cents=-9069c`,
  `selected_yes_pnl_cents=4193c`, `selected_no_pnl_cents=-9069c`,
  `promotion_safe=False`. Same-threshold YES-only was profitable on this
  sample, but the report explicitly treats that as diagnostic only; it needs
  predeclared fresh OOS/shadow validation before it can become a rule.
- same-sample side-safety OOS diagnostic:
  `hypothesis_id=side_safe_yes_only_v1`,
  `evaluation_scope=same_sample_diagnostic`,
  `candidate_count=753`, `market_count=2`,
  `side_safe_selected_count=434`,
  `side_safe_total_counterfactual_pnl_cents=4193c`,
  `blocked_no_count=242`, `blocked_no_loss_avoided_cents=9069c`,
  `promotion_safe=False`; gate failures include `enough_markets=False`,
  `positive_ev_rank=False`, `positive_top_ev_bucket=False`, and
  `locked_oos_scope=False`.
- locked OOS run plan for the next fresh side-safety capture:
  `dataset=particle_side_safety_oos_20260511TLOCKED`,
  `run_id=20260511TLOCKED-SIDESAFE`, `run_seconds=3900`,
  `hypothesis_id=side_safe_yes_only_v1`,
  `evaluation_scope=locked_oos_shadow`, gates `500 candidates`,
  `4 markets`, `100 selected`, positive PnL, positive EV rank, positive top
  EV bucket, and beats-base PnL. The plan writes only commands/manifest and
  starts no process.
- locked side-safety capture:
  `dataset=particle_side_safety_oos_20260511TLOCKED`,
  `recorder_returncode=0`, `tailer_returncode=0`,
  `checkpoint_file_count=5`, `checkpoint_row_count=3559`,
  `context_row_count=1515`, `context_issue_count=344`; strict pipeline
  produced `candidate_count=3398`, `source_candidate_count=3398`,
  `skipped_unlabeled_count=0`, `denominator_scope=all_labeled_candidates`,
  and market-result fetch returned `written_results=5`, `issue_count=0`.
- locked side-safety OOS report:
  `hypothesis_id=side_safe_yes_only_v1`,
  `evaluation_scope=locked_oos_shadow`, `market_count=5`,
  `base_total_counterfactual_pnl_cents=14916c`,
  `side_safe_selected_count=1982`,
  `side_safe_total_counterfactual_pnl_cents=-13150c`,
  `promotion_safe=False`; failed gates include positive total/avg PnL,
  positive top EV bucket, and beats-base PnL. This invalidates the YES-only
  side-safety rule as a promotion candidate.
- locked-capture static replay:
  `candidate_count=3398`, `selected_count=3111`,
  `total_counterfactual_pnl_cents=14916c`,
  `particle_beats_brownian=True`, `particle_beats_market=False`,
  `particle_beats_current_calibrated=False`,
  `ev_rank_correlation_sign=0.074278`,
  `top_ev_bucket_pnl_cents=2.0035`.
- locked-capture fixed-anchor variants:
  `best_by_brier=current_calibrated`, `best_by_pnl=current_calibrated`,
  `current_calibrated` Brier/log-loss `0.163866/0.483483`,
  selected `2918`, PnL `+25198c`, top EV bucket `+9.7259c`.
- locked-capture dynamic rolling-vol diagnostics:
  `best_by_brier=rolling_vol_300s` with Brier/log-loss
  `0.156740/0.459442`, selected `2886`, PnL `+35150c`,
  EV rank `0.134767`, top EV bucket `+25.3435c`;
  `best_by_pnl=rolling_vol_600s`, PnL `+39574c`.
  These diagnostics beat Brownian, market, and current calibrated probability
  on this capture but are not promotion-safe because they were selected after
  inspecting the run.
- same-sample dynamic OOS report:
  `hypothesis_id=rolling_vol_300s_v1`,
  `evaluation_scope=same_sample_diagnostic`, `candidate_count=3398`,
  `market_count=5`, `selected_count=2886`, `total_counterfactual_pnl_cents=35150c`,
  `brier=0.156740`, `log_loss=0.459442`, `promotion_safe=False`.
- locked OOS run plan for the next fresh dynamic capture:
  `dataset=particle_dynamic_oos_20260511TLOCKEDNEXT`,
  `run_id=20260511TLOCKEDNEXT-DYN300`, `run_seconds=3900`,
  `hypothesis_id=rolling_vol_300s_v1`,
  `evaluation_scope=locked_oos_shadow`, gates `1000 candidates`,
  `5 markets`, `250 selected`, positive PnL, positive EV rank/top bucket,
  probability beats Brownian/market/current, and PnL beats static particle and
  current calibrated baselines. The plan writes only commands/manifest and
  starts no process.
- locked dynamic 300s capture:
  `dataset=particle_dynamic_oos_20260511TLOCKEDNEXT`,
  `recorder_returncode=0`, `tailer_returncode=0`,
  `checkpoint_file_count=5`, `checkpoint_row_count=3587`,
  `context_row_count=750`, `context_issue_count=141`; strict pipeline
  produced `candidate_count=3501`, `source_candidate_count=3501`,
  `skipped_unlabeled_count=0`, `denominator_scope=all_labeled_candidates`,
  and market-result fetch returned `written_results=5`, `issue_count=0`.
- locked dynamic 300s OOS report:
  `hypothesis_id=rolling_vol_300s_v1`,
  `evaluation_scope=locked_oos_shadow`, `market_count=5`,
  `selected_count=2852`, `total_counterfactual_pnl_cents=32406c`,
  Brier/log-loss `0.150814/0.458110`, EV rank `0.038545`,
  top EV bucket `+15.7888c`, and probability beat Brownian, market, and
  current calibrated. `promotion_safe=False` because the strict
  `beats_current_calibrated_pnl` gate failed: current calibrated made
  `+32996c` versus dynamic 300s `+32406c`.
- locked dynamic 300s diagnostic family:
  `rolling_vol_600s` was best by both Brier and PnL on the same run:
  Brier/log-loss `0.144880/0.437945`, selected `2816`,
  PnL `+38107c`, EV rank `0.075322`, top EV bucket `+20.1735c`.
  This is diagnostic only because 600s was not the predeclared hypothesis for
  that capture.
- locked OOS run plan for the next fresh dynamic 600s capture:
  `dataset=particle_dynamic600_oos_20260511TLOCKEDNEXT2`,
  `run_id=20260511TLOCKEDNEXT2-DYN600`, `run_seconds=3900`,
  `hypothesis_id=rolling_vol_600s_v1`,
  `evaluation_scope=locked_oos_shadow`, with the same strict gates as the
  300s plan. The plan writes only commands/manifest and starts no process.
- locked dynamic 600s capture:
  `dataset=particle_dynamic600_oos_20260511TLOCKEDNEXT2`,
  `recorder_returncode=0`, `tailer_returncode=0`,
  `checkpoint_file_count=6`, `checkpoint_row_count=3543`,
  `context_row_count=922`, `context_issue_count=194`; strict pipeline
  produced `candidate_count=3414`, `source_candidate_count=3414`,
  `skipped_unlabeled_count=0`, `denominator_scope=all_labeled_candidates`.
  Market-result fetch hit transient public API `429`s, then was completed by a
  finalized single-market retry and merged into six finalized labels.
- locked dynamic 600s OOS report:
  `hypothesis_id=rolling_vol_600s_v1`,
  `evaluation_scope=locked_oos_shadow`, `market_count=6`,
  `selected_count=2740`, `total_counterfactual_pnl_cents=4575c`,
  Brier/log-loss `0.202355/0.579325`, EV rank `-0.082977`,
  top EV bucket `+12.9204c`, `promotion_safe=False`. Failed gates:
  probability did not beat market/current, PnL did not beat static particle or
  current calibrated, and EV rank was negative.
- locked dynamic 600s diagnostic family:
  best dynamic PnL was `rolling_vol_300s` at `+8733c`, but all dynamic variants
  had negative EV rank and none beat current calibrated probability. The fixed
  probability variant diagnostic was stronger: `current_particle_75_25` made
  `+19064c`, but it is diagnostic only and inconsistent with the prior lock.
- locked OOS online-logit diagnostics:
  ran on all three locked captures with `candidate_count=3398`, `3501`, and
  `3414`; no report was promotion-safe. Candidate-weighted online logit showed
  the danger of overweighting repeated same-market labels: the strongest PnL
  row on the 600s lock was `online_logit_particle` at `+86280c`, but aggregate
  mean Brier/log-loss were poor at `0.341073/1.029679`. The market-clustered
  update mode corrected the calibration blow-up; its best aggregate row was
  `online_logit_market_mean_rolling_vol_600s` at `+82411c`, mean Brier/log-loss
  `0.168345/0.493215`, positive PnL in all 3 runs, and positive top EV bucket
  in all 3. It still failed promotion because it beat market/current in only
  2 of 3 runs and had positive EV rank in only 2 of 3.
- locked OOS stability report across side-safety, 300s, 600s, side-consensus, and residual-blend captures:
  `run_count=5`, `variant_row_count=164`, `stability_row_count=40`,
  `stable_candidate_count=0`, `promotion_safe=False`.
  Best aggregate PnL and best mean Brier are now both
  `probability:current_particle_75_25` (`+94765c`, mean Brier
  `0.164645`), which is useful diagnostic evidence but not a predeclared
  locked hypothesis, beats current in only `2/5` runs, and still leaves
  `stable_candidate_count=0`.
  The side-consensus row is included as `source=side_consensus`,
  `run_count=1`, `total_counterfactual_pnl_cents=1447c`, and
  `stable_all_runs=False` because it is only one run, has a negative top EV
  bucket, and the underlying particle probability failed all three baseline
  beats on that run.
  This blocks promotion and argues against selecting another fresh hypothesis
  solely from a single-window winner.
- five-run EV-rank/calibration diagnostic:
  `run_count=5`, `candidate_count=16931`, `selected_count=15689`,
  `ev_rank_correlation_sign=0.045851`, and
  `top_ev_bucket_stable_positive=False`. The highest predicted EV bucket was
  positive in only `1/5` runs (`total=+766c`, `min_run=-4192c`,
  `avg=+0.2261c`), while `ev_rank_4` had the strongest aggregate PnL
  (`+29387c`). Probability calibration also still favors the old baseline:
  best Brier/log-loss were `current_calibrated=0.165260/0.479494`, followed by
  `market=0.170081/0.490636`, while `particle=0.181858/0.540726`.
  This makes the core failure more specific: predicted EV rank is not sorting
  candidates by value, and particle probability is still not beating the
  calibrated/current baseline across locked live-shadow runs.
- five-run market-cluster diagnostic:
  `run_count=5`, `market_count=27`, `candidate_count=16931`,
  `ev_rank_correlation_sign=-0.139601`, and
  `top_ev_bucket_avg_market_candidate_pnl_cents=-0.354508`. Equal-weighted
  market calibration agrees with candidate-weighted calibration:
  `current_calibrated=0.130024/0.414496`, `market=0.131034/0.415895`,
  `particle=0.166264/0.514537`. The highest predicted EV market bucket had
  only `1/6` positive markets; the middle/lowest EV buckets were better. This
  confirms the problem is not just row duplication inside markets.
- five-run simple meta-probability LORO diagnostic:
  `promotion_safe=False`. Four market-cluster-trained logit meta models
  (`logit_current`, `logit_market_current`, `logit_market_current_particle`,
  `current_with_residuals`) were trained on all-but-one locked run and replayed
  on the held-out run. None beat current in any holdout (`0/5`) and none cleared
  strict gates (`0/5`). The least-bad row, `logit_current`, still lost
  `-141229c` with mean Brier/log-loss `0.197074/0.556644`. This blocks simple
  retrospective meta-calibration as an escape hatch.
- five-run timestamp-available state-feature LORO diagnostic:
  `promotion_safe=False`. Four small logit models using moneyness, time-to-close,
  ask/spread/fee/fill state, and optional market/current/particle residuals were
  trained on all-but-one locked run and replayed on the held-out run. None beat
  current in any holdout (`0/5`) and none cleared strict gates (`0/5`). The
  least-bad row, `state_moneyness_time`, still lost `-140527c` with mean
  Brier/log-loss `0.225548/0.664205`. This says the currently logged simple
  state features are not enough by themselves; the next improvement likely needs
  genuinely new signal or a changed terminal simulation assumption.
- independent-spot microfeature LORO diagnostic:
  `promotion_safe=False`. The original two-root diagnostic was underpowered and
  negative. After the GAUSS locks added more independent Coinbase tick streams,
  the expanded seven-root rerun had `eligible_run_count=4` and
  `skipped_run_count=3`; it was still negative. No spot-micro model beat
  Brownian/market/current in any eligible holdout (`0/4` for all three
  baselines), none cleared strict gates (`0/4`), and the least-bad row
  `spot_phi_returns` made only `+5532c` while retaining poor mean Brier/log-loss
  `0.429433/5.529054`. This blocks promoting shallow phi/spot
  momentum/volatility features from the current evidence.
- fixed fat-tail/jump-mixture terminal diagnostic:
  `promotion_safe=False`. Thirteen fixed terminal-distribution assumptions were
  replayed across the five locked roots without fitting thresholds. The result
  did not support the fat-tail premise; the best Brier and PnL row was a lower
  volatility Gaussian (`gaussian_vol45`), not a jump mixture. It made `+99334c`
  in aggregate with mean Brier/log-loss `0.171052/0.507782`, positive PnL in
  `4/5` runs, positive top EV bucket in `3/5`, and beat Brownian in `4/5`, but
  it beat current in only `1/5` and cleared strict gates in `0/5`. This is a
  useful hypothesis seed for a fresh predeclared low-vol run, not promotion
  evidence.
- fixed low-vol terminal OOS evaluator:
  `research_particle/fixed_terminal_oos.py` now formalizes
  `gaussian_vol45_terminal_v1` with locked-scope, all-candidate denominator,
  minimum sample-size, PnL, EV-rank/top-bucket, probability-baseline, and
  current/static-PnL gates. A smoke run on the existing residual root used
  `evaluation_scope=same_sample_diagnostic`, made `+48996c`, and correctly kept
  `promotion_safe=False`. This gives the next fresh capture a predeclared
  evaluator instead of an after-the-fact diagnostic.
- fixed low-vol terminal locked OOS plan:
  `fixed_terminal_GAUSS45LOCK001_locked_oos_plan` locks the next fresh shadow
  test before collection: `hypothesis_id=gaussian_vol45_terminal_v1`,
  `evaluation_scope=locked_oos_shadow`, `run_seconds=3900`, independent Coinbase
  spot required with `max_age_ms=5000`, all-labeled candidates required, baseline
  pipeline annualized volatility kept at `0.65`, and fixed terminal annualized
  volatility set to `0.45`. The plan writes the full capture, pipeline, market
  result, label join, static replay, probability variants, fat-tail diagnostic,
  and fixed terminal OOS commands. It starts no process by itself.
- fresh locked fixed low-vol terminal OOS run:
  capture `GAUSS45LOCK001` completed passively against live Kalshi BTC 15m
  markets with independent Coinbase spot required. It recorded
  `checkpoint_row_count=3537`, `context_row_count=655`,
  `independent_spot_row_count=48313`, merged `585` fresh spot contexts, and
  produced `2514` strict all-labeled candidate rows across `4` finalized
  markets. The static particle replay was strong on this short live-shadow
  window (`selected_count=2416`, `+50400c`, Brier/log-loss
  `0.226789/0.631705`, positive EV rank, positive top EV bucket, and beats
  Brownian/market/current probability baselines). The predeclared
  `gaussian_vol45_terminal_v1` report made `+47330c` with `selected_count=2330`
  and positive EV-rank/top-bucket, but it correctly kept
  `promotion_safe=False` because `market_count=4` is below the locked minimum
  of `5`, it did not beat Brownian probability, and it did not beat the static
  particle PnL baseline. This is useful forward-shadow evidence, not live
  promotion evidence.
- second locked fixed low-vol terminal OOS run:
  `GAUSS45LOCK002` reused the same frozen `gaussian_vol45_terminal_v1`
  hypothesis and gates, with a longer `run_seconds=5400` collection to avoid
  the first run's underpowered market count. Capture completed passively with
  `recorder_returncode=0`, `tailer_returncode=0`,
  `independent_spot_returncode=0`, `checkpoint_row_count=5068`,
  `context_row_count=1212`, `independent_spot_row_count=37126`, and
  `merged_context_row_count=1137`. The strict pipeline produced `4843`
  all-labeled candidates across `7` finalized markets with `context_issues=0`
  and `skipped_unlabeled_count=0`. Static particle replay made `+47336c`,
  beat market/current, and had positive EV rank/top bucket, but did not beat
  Brownian probability. The fixed `gaussian_vol45_terminal_v1` replay made
  `+49703c`, beat market/current and static particle PnL, had positive
  EV-rank/top-bucket, and met candidate/market/selection gates, but remained
  `promotion_safe=False` because it still did not beat Brownian probability.
- fixed low-vol terminal stability across `GAUSS45LOCK001` and `GAUSS45LOCK002`:
  `run_count=2`, fixed-terminal `total_counterfactual_pnl_cents=97033c`,
  positive PnL/EV-rank/top-bucket in `2/2`, beats market/current in `2/2`,
  but beats Brownian in `0/2`, so `stable_all_runs=False` and
  `stable_candidate_count=0`. This turns the low-vol result into a useful
  research clue: the EV side is promising, but the probability model is not
  better than the Brownian baseline required by the goal.
- third locked fixed low-vol terminal OOS run:
  `GAUSS45LOCK003` was predeclared with the same
  `gaussian_vol45_terminal_v1` hypothesis and strict gates, then captured
  passively against live Kalshi BTC 15m markets. It recorded `4990` Kalshi
  checkpoints, produced `4405` strict all-labeled candidate rows across `6`
  finalized markets, and joined all labels from public Kalshi results. The
  independent Coinbase spot sidecar produced `35848` ticks but ended with a
  websocket close-frame error, so the run is useful locked evidence with a spot
  sidecar caveat. Static particle replay lost `-7134c`; the locked
  fixed-terminal replay lost `-7258c`, with negative EV rank and negative top
  EV bucket. It beat Brownian probability on Brier/log-loss but failed market,
  current-calibrated, PnL, EV-rank, top-bucket, and static-particle PnL gates.
  This fresh run vetoes promotion of the low-vol terminal hypothesis as-is.
- updated locked stability after `GAUSS45LOCK003`:
  `logs/particle_research/reports/locked_oos_stability_latest.md` now covers
  `8` locked roots, `196` variant rows, and `42` stability rows, still with
  `stable_candidate_count=0`. The fixed-terminal hypothesis has `run_count=4`,
  aggregate `+138771c`, positive PnL in `3/4`, beats Brownian in only `1/4`,
  beats market/current in `3/4`, and `stable_all_runs=False`. The added live
  loss did exactly what a lock should do: it separated a promising clue from a
  promotable strategy.
- label-gated online anchor calibration diagnostic:
  `research_particle/online_anchor_calibration_diagnostic.py` evaluates fixed
  online-logit calibrators for Brownian, particle, market, current, and
  Brownian/particle/market blends using only labels whose
  `label_available_ts_utc` is at or before each decision. Across the seven
  locked roots, no spec cleared strict gates. The best strict-count row,
  `online_logit_brownian_particle75_lr003_row`, made `+237053c`, but strict
  gates were only `2/7`, it beat raw in `3/7`, Brownian in `3/7`, market in
  `2/7`, and current in `2/7`. The best mean-Brier row,
  `online_logit_market_particle75_lr003_marketlast`, had `0/7` strict gates.
  This blocks simple online calibration of existing anchors as the probability
  fix; the next improvement needs a genuinely better terminal probability
  signal, not just a label-gated logit wrapper.
- anchor regime profile:
  `research_particle/anchor_regime_profile.py` profiles Brownian, particle,
  market, and current-calibrated anchor winners by locked run, individual
  resolved market, and timestamp-available state buckets such as
  time-to-close, absolute moneyness, spread, and market-vs-Brownian
  disagreement. Across seven locked roots, no anchor dominates: run-level
  Brier winners were current `4/7`, Brownian `2/7`, particle `1/7`, market
  `0/7`; market-level winners were market `14`, current `11`, Brownian `7`,
  particle `6`; state-bucket winners were Brownian `6`, current `5`, market
  `4`, particle `1`. The conclusion is that anchor switching needs a stronger
  timestamp-available state signal before it is promotable.
- independent-spot realized-vol terminal diagnostic:
  `research_particle/spot_realized_vol_terminal_diagnostic.py` computes
  Brownian terminal probabilities using realized volatility from Coinbase ticks
  that are timestamp-available at each decision, then compares fixed local-vol
  windows and 50/50 blends against the fixed Brownian/current/market baselines.
  Across the four locked roots with independent spot ticks,
  `rv233_blend50_fixed65` was best by both Brier and PnL
  (`0.203203/0.576615`, `+86986c`), but it still had strict gates `0/4`, beat
  Brownian in only `1/4`, and beat current in `3/4`. This is hypothesis
  generation only, not promotion evidence.
- local realized-vol OOS evaluator:
  `research_particle/spot_realized_vol_terminal_oos.py` evaluates the
  `rv233_blend50_fixed65_terminal_v1` hypothesis behind locked-OOS gates. It
  blocks same-sample promotion through the same `locked_oos_shadow` and
  all-labeled-denominator checks as the fixed-terminal evaluator, and
  `research_particle/oos_stability_report.py` now includes future
  `spot_realized_vol_terminal_oos*.json` reports in stability aggregation.
- local realized-vol locked-OOS plan writer:
  `research_particle/spot_realized_vol_terminal_locked_oos_plan.py` writes a
  research-only manifest for a future fresh test of
  `rv233_blend50_fixed65_terminal_v1`, including the passive capture command,
  independent spot requirement, strict pipeline, label join, static replay,
  probability variants, and realized-vol OOS evaluator command.
- fixed-terminal locked OOS run `GAUSS45LOCK003`:
  predeclared with `hypothesis_id=gaussian_vol45_terminal_v1`,
  `dataset=particle_fixed_terminal_oos_GAUSS45LOCK003`, `run_seconds=5400`,
  independent Coinbase spot required, and unchanged strict gates. Capture and
  replay completed passively/research-only and did not touch live order
  placement or live bot logic. Final locked replay:
  `candidate_count=4405`, `market_count=6`, `selected_count=4221`,
  `total_counterfactual_pnl_cents=-7258c`, Brier/log-loss
  `0.178926/0.533517`, `promotion_safe=False`.
- five-run variant LORO selector diagnostic:
  `promotion_safe=False`. Picking the best variant by train-set PnL was a trap:
  holdout PnL was `-127077c`, positive in only `1/5` holdouts, and beat current
  in `0/5`. Picking by train-set Brier was safer but still failed strict gates:
  holdout PnL `+17019c`, positive in `3/5`, beat current in `0/5`, strict
  gates `0/5`. The best gate-score selector was the least bad:
  holdout PnL `+62814c`, positive in `4/5`, beat current in `2/5`, strict
  gates `1/5`. This confirms the aggregate winners are not ready for a fresh
  promotion plan without a real model change.
- PASC threshold LORO diagnostic:
  `research_particle/pasc_loro_threshold_diagnostic.py` now tests
  PnL-aware selective classification without same-run threshold tuning. For
  each held-out locked run, it chooses variant/EV/fill thresholds from the
  other locked runs only, caches each run/variant/threshold replay once, then
  evaluates the frozen choice on the holdout. The narrow eight-run diagnostic
  over `particle`, `brownian`, and `current_particle_75_25` with
  `min_ev in {0,3,8,15}` and `min_fill=0.5` produced
  `promotion_safe=False`. The best gate-score selector had `+117634c`
  aggregate holdout PnL and positive PnL in `7/8` holdouts, but strict gates
  were only `1/8`, it beat current in only `4/8`, and it still failed the
  Brownian/market/current probability requirements. This is useful negative
  evidence: PASC-style thresholding can improve money totals in places, but it
  does not solve the probability-quality gate.
- anchor-switch LORO diagnostic:
  `research_particle/anchor_switch_loro.py` tests the anchor-regime idea
  directly. It chooses among Brownian, market, current-calibrated, and particle
  anchors inside timestamp-available state buckets, using equal-weighted
  market/bucket clusters from the training locked runs only. On the held-out
  run it materializes the selected anchor as the particle probability and
  replays the full all-candidate denominator. Across the eight locked roots,
  `promotion_safe=False`; the best strict-count rows had `0/8` strict gates.
  The best total-PnL bucket scheme was `time_moneyness` (`+88987c`, positive
  PnL in `7/8`), but it beat current in only `4/8`, beat market in only `3/8`,
  had positive EV rank in only `3/8`, and did not clear any strict holdout.
  This blocks simple timestamp-available anchor switching as the missing
  probability model.
- residual blend LORO diagnostic across the same four locked roots:
  `coefficient_count=517`, best exact same-evidence blend
  `resid_mp00_r300n02_r600p02_pn01` uses
  `p=current + 0.0*(market-current) - 0.2*(rv300-current) + 0.2*(rv600-current) - 0.1*(particle-current)`.
  It made `+106304c`, only `+1169c` above the fixed current-calibrated
  aggregate, with `beats_current_probability_run_count=3/4`,
  `beats_current_pnl_run_count=3/4`, positive EV rank `4/4`, and positive top
  EV bucket `4/4`; `stable_all_runs=False` and `promotion_safe=False`.
  Leave-one-run-out picks were weaker: every holdout pick failed
  `holdout_beats_current_probability`, and three of four holdout picks were
  below current-calibrated PnL. This makes residual blending a fresh-OOS
  hypothesis source only, not promotion evidence.
- residual blend locked OOS plan:
  `hypothesis_id=resid_current_rv300n20_rv600p20_particle_n10_v1`,
  `dataset=particle_residual_blend_oos_RESIDLOCK001`,
  `run_seconds=3900`, `evaluation_scope=locked_oos_shadow`, independent
  Coinbase spot required, and strict gates set at `min_candidate_count=1000`,
  `min_market_count=5`, `min_selected_count=250`, with all probability,
  PnL, EV-rank, and top-bucket gates required. The plan writes only a manifest
  and commands; it starts no process and does not touch live trading.
- fresh locked residual blend OOS run:
  capture `RESIDLOCK001` completed passively with
  `recorder_returncode=0`, `tailer_returncode=0`,
  `independent_spot_returncode=0`, `checkpoint_row_count=3633`,
  `context_row_count=896`, `independent_spot_row_count=44784`,
  `merged_context_row_count=835`, and `independent_spot_issue_count=0`.
  Strict pipeline wrote `3358` all-candidate snapshots across 5 markets with
  `context_issues=0`; public Kalshi results finalized all 5 markets and label
  join wrote 5 labels. The predeclared residual blend failed decisively:
  `selected_count=2448`, `total_counterfactual_pnl_cents=-28864c`,
  Brier/log-loss `0.244988/0.660681`, EV rank `-0.060806`, top EV bucket
  `-9.2202c`, and `promotion_safe=False`. Failed gates included all baseline
  probability beats, static/current PnL beats, positive PnL, positive EV rank,
  and positive top bucket. The base static particle replay on the same fresh
  window made `+60332c`, beat market/current probability, but failed Brownian
  probability and top-EV-bucket gates (`-1.0202c`), so it also does not
  complete the goal.
- late time/regime blend materialized variants:
  four fixed blends were replayed across all three locked roots and the fresh
  read-only replay. In locked stability, none cleared promotion. The strongest
  total-PnL row, `late300_consensus_mc75_online_logit_rv600`, tied the previous
  near-miss at `+82411c` because it mostly leaves the base model unchanged; it
  still beat market/current and had positive EV rank in only `2/3` locked runs.
  On the fresh replay, all four late blends remained negative at `-1124c` and
  still failed market/current probability baselines.
- fresh bounded read-only live capture:
  `dataset=particle_shadow_readonly_fresh_20260511T113926Z`,
  `recorder_returncode=0`, `tailer_returncode=0`,
  `checkpoint_row_count=175`, `context_row_count=81`,
  `context_issue_count=13`; strict pipeline produced `recorded_candidates=175`,
  `contexts_written=175`, `context_issues=0`, `labels_written=0`.
  The recorder manifest marked the data as `native_passive_ws`,
  `passive_no_order_submission`, and `full_depth_checkpoints`.
- fresh bounded read-only market result and replay:
  `KXBTC15M-26MAY110745-45` finalized `yes`; label join wrote 1 label.
  The replay used all 175 labeled candidates, selected 174, and lost
  `-1160c` counterfactual PnL. Particle probability beat Brownian by a tiny
  amount (`0.124814` vs. `0.125449` Brier) but lost badly to market/current
  (`0.004594`/`0.007336` Brier). Diagnostics show all selected trades were NO
  (`selected_no_pnl_cents=-1160c`) while market/current were strongly YES.
- market/current agreement veto diagnostic:
  a simple agreement veto prevented the fresh late-market NO loss, but across
  the three locked OOS reports plus the fresh replay it reduced aggregate PnL
  from `+81251c` to at most `+65785c` among tested settings and did not fix the
  weak third lock. It is a warning diagnostic, not a promotable rule.
- consolidated side/regime diagnostic:
  `run_count=4`, `selected_count=8689`, base total `+81251c`,
  `stable_positive_rules=0`. The worst time-to-close buckets were `000_060s`
  (`+1227c`, `20.99%` win rate), `061_180s` (`+7296c`, `20.19%` win rate), and
  `181_300s` (`+5346c`, `23.33%` win rate), while `301_600s` and `gt_600s`
  were much healthier. However, the predeclared consensus/time rules still
  failed stability: `skip_late_300s_against_consensus_05` was positive in only
  `2/4` runs and had a `-4350c` minimum run. This points to probability-engine
  side/regime improvement, not another simple veto.
- v28 context-only extraction: `written_contexts=60`, `issue_count=0`
- passive checkpoint pipeline: `recorded_candidates=72`,
  `contexts_written=72`, `context_issues=0`, `labels_written=0`
- public Kalshi result fetch: `written_results=1`, `issue_count=0`;
  `result=yes`, `status=finalized`
- market-result label join: `written_labels=1`, `skipped_results=0`
- label recording: `recorded_labels=1`
- strict real passive replay: `candidate_count=72`, `selected_count=72`,
  `total_counterfactual_pnl_cents=-2244.0000`,
  `particle_beats_brownian=True`, `particle_beats_market=False`,
  `particle_beats_current_calibrated=False`,
  `ev_rank_correlation_sign=0.666188`,
  `top_ev_bucket_pnl_cents=-28.8889`
- online-calibrated real passive replay: `candidate_count=72`,
  `selected_count=72`, `coverage_rate=0.000000`,
  `online_beats_raw_particle=False`, `online_beats_brownian=True`,
  `online_beats_market=False`,
  `online_beats_current_calibrated=False`
- real passive selection sweep: `grid_rows=50`,
  `positive_nonzero_rows=0`, `best_positive_row=none`
- goal completion audit: `complete=False`, `strict_real_candidate_rows=26026`,
  `real_replay_reports=33`, `locked_oos_stability_rows=41`,
  `locked_oos_stable_candidate_count=0`; real-data probability, EV-rank, and
  shadow-PnL gates now correctly remain `fail` until locked-OOS stability has a
  nonzero stable candidate count. The audit now also includes the
  independent-spot realized-vol terminal diagnostic and keeps it explicitly
  non-promotable.
- refreshed goal completion audit after `GAUSS45LOCK003`: `complete=False`,
  `strict_real_candidate_rows=30431`, `real_replay_reports=34`,
  `locked_oos_stability_rows=42`, and `locked_oos_stable_candidate_count=0`.
  The new live-shadow evidence strengthens the blocker rather than clearing it.
- fresh predeclared independent-spot realized-vol terminal locked OOS run
  `RVTERMLOCK001`: live-shadow capture only, no particle order placement;
  `checkpoint_row_count=4884`, `context_row_count=1221`,
  `independent_spot_row_count=33754`, `merged_context_row_count=1126`,
  `candidate_count=4512`, `market_count=7`.
- `RVTERMLOCK001` replay results: static particle selected 4,379 candidates
  and lost `-2384c`; probability variants selected `current_calibrated` as
  best by both Brier and PnL (`Brier=0.122272`,
  `log_loss=0.374592`, `+28435c`); predeclared
  `rv233_blend50_fixed65` selected 4,108 candidates and made `+17528c`,
  but failed promotion because it did not beat current-calibrated probability
  or PnL gates and had negative EV-rank/top-bucket checks.
- materialized `rv233_blend50_fixed65` replay for `RVTERMLOCK001`:
  full decision report confirms the same issue. The realized-vol terminal
  variant had `selected_yes_pnl_cents=-33777c` and
  `selected_no_pnl_cents=+51305c`; its highest predicted EV bucket lost
  `-4222c`, while lower EV buckets were positive. This supports the blocker:
  positive PnL came from broad side exposure, not a trustworthy EV ranking.
- refreshed locked stability after `RVTERMLOCK001`: `run_count=9`,
  `variant_row_count=207`, `stable_candidate_count=0`,
  `best_by_total_pnl=probability:brownian`, and
  `best_by_mean_brier=spot_realized_vol_terminal:rv233_blend50_fixed65_terminal_v1`.
  The realized-vol family is now interesting as a calibration clue, not a
  promoted strategy.
- refreshed goal completion audit after `RVTERMLOCK001`: `complete=False`,
  `strict_real_candidate_rows=34943`, `real_replay_reports=36`,
  `locked_oos_stability_rows=43`, and `locked_oos_stable_candidate_count=0`.
- refreshed independent-spot realized-vol terminal diagnostic across all nine
  locked roots: `eligible_run_count=6`, `skipped_run_count=3`,
  `spec_count=7`, `promotion_safe=False`; `rv233_blend50_fixed65` was best by
  Brier (`mean_brier=0.187150`) and aggregate PnL (`+94618c`), but no realized
  vol spec cleared the strict eligible-run gates.
- added and ran the realized-vol-aware anchor-switch LORO diagnostic:
  `spot_rv_anchor_switch_loro_20260511_nine_locked` uses only the six locked
  roots with independent spot ticks, adds `rv_terminal` to the Brownian,
  market, current-calibrated, and particle anchors, and trains on all-but-one
  runs. Best summary row was `time_rv_disagreement` with `+102481c`,
  `beats_current=5/6`, and `strict_gates=1/6`; therefore
  `candidate_ready_for_predeclared_shadow=False` and `promotion_safe=False`.
  This is useful evidence that RV disagreement can describe some aggregate
  structure, but it is not stable enough to promote.
- extended the same RV-aware anchor-switch report with equal-market EV sanity
  fields to reduce repeated-candidate label bias. The best row
  `time_rv_disagreement` still has `+102481c`, but market-level EV rank is
  positive in only `3/6` holdouts and the top equal-market EV bucket is positive
  in only `4/6`. This supports the blocker: the aggregate PnL is interesting,
  but the EV ordering is not stable enough.
- added and ran the conservative realized-vol current-residual LORO diagnostic:
  `spot_rv_current_residual_loro_20260511_nine_locked` uses only the six locked
  roots with independent spot ticks, trains on equal-weighted market/bucket
  clusters, and defaults to `current_calibrated` whenever a bucket is too thin
  or the residual does not improve training Brier. Best strict count was only
  `1/6`; the best positive-PnL row, `time_rv_disagreement`, made `+54559c` but
  cleared `0/6` strict gates and beat current in only `2/6`. Therefore
  `candidate_ready_for_predeclared_shadow=False` and `promotion_safe=False`.
- added and ran the next-second spot-drift terminal diagnostic:
  `spot_drift_terminal_diagnostic_20260511_nine_locked` estimates a capped
  next-second log drift from only public spot ticks available before each
  decision, then combines that drift with realized/fixed terminal volatility.
  It is closer to the "predict the next second, then the next" idea than the
  earlier static terminal-vol overlays. The best row,
  `drift13_cap10_fixed65_blend25`, made `+99481c` and had positive PnL in
  `4/6` eligible locked runs, but cleared only `1/6` strict gates, beat current
  in only `3/6`, and had equal-market EV rank/top-bucket positives in only
  `2/6`. Side diagnostics show the aggregate was not a simple side bug:
  selected NO made `+69424c` and selected YES made `+30057c`, but each side was
  positive in only `3/6` runs. It is a useful clue, not a promoted candidate.
- added and ran the next-second spot-drift regime diagnostic:
  `spot_drift_regime_diagnostic_20260511_best_locked` checks whether the best
  drift spec has a simple timestamp-available bucket underneath it. It used
  `22,892` feature rows and `21,197` selected decisions across the six eligible
  locked independent-spot roots. Result: `stable_positive_rules=0`,
  `candidate_ready_for_predeclared_shadow=False`, and `promotion_safe=False`.
  The strongest near miss was `require_market_current_consensus_alignment`
  with `5/6` positive runs but a `-15686c` worst run. The most profitable
  aggregate rules still failed stability: `require_abs_drift_ge_1bps` made
  `+106976c` but was positive in only `4/6` runs, and base drift made
  `+99481c` with only `4/6` positive runs. The all-spec version,
  `spot_drift_regime_diagnostic_20260511_all_specs_locked`, also found
  `stable_positive_rules=0` across `114,460` feature rows. This makes the
  current drift clue a state descriptor or research lead, not a gate.
- added and ran the empirical next-second particle diagnostic:
  `empirical_next_second_particle_diagnostic_20260512_nine_locked` uses only
  independent spot ticks available at or before each decision. It builds a
  conservative one-second return cache whose bucket return is available only
  after that one-second bucket ends, then uses deterministic compressed
  bootstrap particles to estimate terminal probability. The first unoptimized
  run was stopped because it was too slow; after adding the no-leak return cache
  it completed across the same six eligible locked independent-spot roots.
  Best aggregate row was `emp1s_610_center_blend50_p96_d48`, with `+113066c`
  total counterfactual PnL and `4/6` positive-PnL runs. It still failed
  promotion: `strict_gate_count=0/6`, beats Brownian/market/current only
  `3/6`, EV rank positive only `2/6`, equal-market EV rank positive only
  `3/6`, and equal-market top bucket positive only `2/6`. The weak runs were
  again concentrated in `CONSENSUSLOCK001` and `GAUSS45LOCK003`. This is a real
  next-second particle benchmark, but not a promoted probability replacement.
- added and ran the current-anchored empirical next-second diagnostic:
  `empirical_current_anchor_diagnostic_20260512_nine_locked` keeps
  `current_calibrated` as the baseline and applies only a small empirical
  one-second particle nudge when independent spot evidence is fresh; stale or
  insufficient empirical rows default exactly to `current_calibrated`. This
  repaired some calibration comparisons but broke PnL: best row
  `current_emp610_w25_center` beat current in `4/6` runs and had one strict
  passing run, but total PnL was `-19237c`, positive PnL only `2/6`, EV rank
  positive only `2/6`, and `promotion_safe=False`. This confirms that a
  conservative empirical nudge is not enough; probability calibration can look
  better while EV ordering and tradability get worse.
- added and ran the empirical market-opportunity diagnostic:
  `empirical_market_opportunity_diagnostic_20260512_nine_locked` keeps the
  all-candidate replay denominator but collapses evaluation to one highest
  predicted-EV opportunity per resolved market. This tests whether the large
  candidate-row aggregate PnL is merely repeated-row inflation. It is not purely
  inflation: `emp1s_610_center_blend50_p96_d48` was positive in `6/6` runs
  after de-duplication, but only `+262c` over `35` selected markets, with
  beats-current only `2/6`, top-bucket positive only `1/6`, and `0/6` strict
  gates. The best strict count was `2/6` for
  `emp1s_987_mean25_blend25_p128_d64`, which made only `+198c` and was positive
  in `3/6` runs. This supports the current conclusion: the empirical signal has
  some market-level direction, but not enough probability/EV quality for
  promotion.
- expanded the empirical market-opportunity diagnostic to emit a compact
  per-market opportunity table, then added and ran
  `empirical_market_opportunity_loro_20260512_nine_locked`. This is the
  stricter anti-fluke test: each held-out run gets a family/spec/score transform
  chosen only from the other runs. Result: aggregate held-out market-level PnL
  was positive but tiny (`+84c`) and positive in `5/6` holdouts, yet strict
  gates were `0/6`, beats-current was only `3/6`, positive EV-rank was only
  `3/6`, and top predicted-EV bucket was positive in only `1/6`. This confirms
  the empirical next-second clue still does not create a reliable EV ordering.
- added the paired public REST sidecar plus independent spot capture:
  `paired_sidecar_spot_capture.py` starts the Coinbase spot tick recorder, runs
  one explicit sidecar collection cycle, writes the normal non-promoting
  sidecar artifacts, and records whether each sidecar bundle had an independent
  locally received spot tick at or before the bundle capture timestamp. The
  first live paired capture at
  `sidecar_spot_pairs/20260512T035542Z-7097dc7a` was
  `paired_capture_ready=True`: it selected one real Kalshi BTC15M market
  (`14` packet rows), wrote `84` Coinbase ticks, and aligned the sidecar bundle
  to a no-future spot tick `562.588ms` old. This is instrumentation evidence
  only: `promotion_allowed=False`, no labels were fetched in that pre-close
  pass, no downstream audits were refreshed, and no live bot state/orders were
  touched. After the market settled, a label/scoring refresh joined all current
  sidecar rows: `1978` frozen/joined/clean rows across `74` markets, with `0`
  promotable candidates. The boundary time-safe sidecar remains undercovered
  (`80` rows / `30` markets) and only barely better on all-row Brier/log-loss;
  other broad candidates still fail probability gates against v28.
- added sidecar packet independent-spot enrichment:
  `paired_sidecar_spot_enrichment.py` reads a paired sidecar manifest, the
  sidecar packet CSV, and the independent spot tick tape, then writes only the
  matching packet rows with the latest locally received no-future spot tick.
  The real enrichment for `20260512T035542Z-7097dc7a` read `2006` packet rows,
  matched `14`, enriched all `14`, and had `0` issues. It shows the public REST
  sidecar candle spot was `44.198s` old while the independent spot tick was
  `562.588ms` old; the tick differed from the candle spot by `-0.362805` bps.
  This is still input-quality evidence only and leaves frozen sidecar rows
  untouched.
- added the paired sidecar tick-vs-candle probability diagnostic:
  `paired_sidecar_spot_diagnostic.py` joins those enriched packet rows to the
  settled sidecar labels and compares the stale candle Brownian terminal
  probability against the fresher independent-tick Brownian terminal
  probability, plus v28, candidate, and market-side baselines. On the first
  real paired capture it joined only `14` rows from `1` market, so it is
  explicitly underpowered and `promotion_allowed=False`. The fresher tick did
  improve Brownian versus the candle by Brier (`-0.0017015`) and log loss
  (`-0.0060031`), but `v28` was still best by Brier/log loss on this tiny
  sample and the Brownian EV selections lost money. This is a useful live-input
  clue, not a promoted probability model.
- collected and scored a second live paired sidecar/spot sample at
  `20260512T041445Z-ef98a171`: one current Kalshi BTC15M market, `40`
  independent Coinbase ticks, no alignment/enrichment issues, and
  `promotion_allowed=False`. After a post-close sidecar refresh, the sidecar
  evidence pool had `2048` frozen/joined/clean rows across `75` markets and
  `0` promotable candidates. The second tick-vs-candle diagnostic again joined
  `14` rows from `1` market; fresher tick Brownian beat stale-candle Brownian
  slightly (`Brier -0.0004003`, `log loss -0.0036352`), but `v28` and
  market-side baselines were still better and Brownian selected trades lost
  money. This reinforces that independent spot freshness is real input-quality
  progress, not yet alpha.
- added the aggregate paired sidecar tick-vs-candle diagnostic:
  `paired_sidecar_spot_aggregate.py` reads every per-capture
  `sidecar_spot_tick_vs_candle_diagnostic.json`, merges the settled diagnostic
  rows, recomputes model metrics on the combined live-shadow denominator, and
  remains `promotion_allowed=False`. The main goal audit now also checks that
  the aggregate's recorded diagnostic-file count matches the actual per-capture
  diagnostic files on disk, so a stale aggregate cannot silently masquerade as
  current evidence. After adding the paired sidecar/spot refresh command, the
  current aggregate has `4/4` ready diagnostics, `0` pending diagnostics,
  `56` joined rows, `3` markets, and `0` enrichment issues. It now exposes
  explicit predeclared-shadow
  deficits: `144` more joined rows and `37` more distinct markets are needed
  before this aggregate is even eligible as a shadow candidate source.
  After the 01:15 ET post-close refresh, the aggregate has `10` ready
  diagnostics, `142` joined rows, and `5` markets. `tick_brownian` is now best
  by both Brier and log loss on this small paired aggregate, and independent
  tick Brownian beats stale-candle Brownian by `-0.0008089` Brier and
  `-0.0020364` log loss. This is a useful input-quality clue, not a promotion:
  the aggregate is still below the predeclared shadow floor (`200` rows /
  `40` markets), with `58` rows and `35` distinct markets still required.
  After the 01:30 ET post-close refresh, the row floor is now met but the market
  floor still blocks: the aggregate has `14` valid ready diagnostics, `206`
  joined rows, and `6` markets, with `1` invalid diagnostic skipped. `v28` is
  again best by both Brier and log loss, `tick_brownian` is slightly worse than
  stale-candle Brownian on the combined aggregate (`Brier delta +0.0003056`,
  `log-loss delta +0.0003527`), and `candidate_ready_for_predeclared_shadow`
  remains `False` because `34` more distinct markets are required. The paired
  aggregate now also reports equal-market metrics to reduce repeated-market
  overfitting: each market contributes one vote. On this equal-market view,
  `v28` is still best by Brier and log loss, while `tick_brownian` beats
  stale-candle Brownian within the Brownian pair (`Brier delta -0.0006413`,
  `log-loss delta -0.0018182`).
  After the 01:45 ET post-close refresh, the aggregate has `17` valid ready
  diagnostics, `254` joined rows, and `7` markets, with `1` invalid diagnostic
  skipped. Row coverage remains above floor, but `33` more distinct markets are
  still required. Candidate-weighted Brier still favors `v28`, while
  candidate-weighted log loss and the equal-market Brier/log-loss view now favor
  `market_side_ask`; this reinforces that the live market baseline is hard to
  beat on the current small paired sample.
  After the 02:00 ET post-close refresh, the aggregate has `20` valid ready
  diagnostics, `302` joined rows, and `8` markets, with `1` invalid diagnostic
  skipped. Market diversity is still the blocker: `32` more distinct markets
  are required. Both candidate-weighted and equal-market Brier/log-loss are back
  to `v28` as the best model; tick Brownian still improves over stale-candle
  Brownian inside the Brownian pair, but does not beat v28.
  After the 02:15 ET post-close refresh, the aggregate has `23` valid ready
  diagnostics, `350` joined rows, and `9` markets, with `1` invalid diagnostic
  skipped. The row floor remains met, but `31` more distinct markets are still
  required. Both candidate-weighted and equal-market Brier/log-loss favor
  `market_side_ask`, not the research candidate; the research candidate is
  negative on selected PnL and top-EV-bucket PnL in both weighting views. This
  is explicit negative evidence against promotion and a reason to keep
  collecting distinct live-shadow markets before interpreting any same-market
  row-weighted signal.
  After the 02:30 ET post-close refresh, the aggregate has `24` valid ready
  diagnostics, `366` joined rows, and `10` markets, with `1` invalid diagnostic
  skipped. Market diversity is still the blocker: `30` more distinct markets
  are required. Both candidate-weighted and equal-market Brier/log-loss favor
  `v28`, not the research candidate.
  After the 02:45 ET post-close refresh, the aggregate has `25` valid ready
  diagnostics, `384` joined rows, and `11` markets, with `1` invalid diagnostic
  skipped. Market diversity is still the blocker: `29` more distinct markets
  are required. Both candidate-weighted and equal-market Brier/log-loss still
  favor `v28`.
  After the 03:00 ET post-close refresh, the aggregate has `26` valid ready
  diagnostics, `402` joined rows, and `12` markets, with `1` invalid diagnostic
  skipped. Market diversity is still the blocker: `28` more distinct markets
  are required. Both candidate-weighted and equal-market Brier/log-loss still
  favor `v28`; the equal-market research candidate remains negative on selected
  PnL and top-EV-bucket PnL.
  After the 03:15 ET post-close refresh, the aggregate has `27` valid ready
  diagnostics, `420` joined rows, and `13` markets, with `1` invalid diagnostic
  skipped. Market diversity is still the blocker: `27` more distinct markets
  are required. Candidate-weighted Brier favors `v28`, candidate-weighted
  log loss favors `market_side_ask`, and equal-market Brier/log loss favor
  `candle_brownian`; the research candidate remains negative on equal-market
  selected PnL and top-EV-bucket PnL.
  After the 03:30 ET post-close refresh, the aggregate has `28` valid ready
  diagnostics, `438` joined rows, and `14` markets, with `1` invalid diagnostic
  skipped. Market diversity is still the blocker: `26` more distinct markets
  are required. Candidate-weighted Brier favors `v28`, candidate-weighted
  log loss favors `market_side_ask`, and equal-market Brier/log loss favor
  `candle_brownian`; the research candidate remains negative on equal-market
  selected PnL and top-EV-bucket PnL.
  After the 03:45 ET post-close refresh, the aggregate has `29` valid ready
  diagnostics, `456` joined rows, and `15` markets, with `1` invalid diagnostic
  skipped. Market diversity is still the blocker: `25` more distinct markets
  are required. Candidate-weighted Brier favors `v28`, candidate-weighted
  log loss favors `market_side_ask`, and equal-market Brier/log loss favor
  `candle_brownian`. The research candidate is finally positive on
  equal-market selected PnL, but its equal-market top-EV bucket is still
  negative and its probability scores still trail the baselines.
  After the 04:00 ET post-close refresh, the aggregate has `30` valid ready
  diagnostics, `474` joined rows, and `16` markets, with `1` invalid diagnostic
  skipped. Market diversity is still the blocker: `24` more distinct markets
  are required. Candidate-weighted Brier favors `v28`, candidate-weighted
  log loss favors `market_side_ask`, and equal-market Brier/log loss favor
  `candle_brownian`. The research candidate remains positive on equal-market
  selected PnL, but its equal-market top-EV bucket is still negative and its
  probability scores still trail the baselines.
  After the 04:15 ET post-close refresh, the aggregate has `31` valid ready
  diagnostics, `492` joined rows, and `17` markets, with `1` invalid diagnostic
  skipped. Market diversity is still the blocker: `23` more distinct markets
  are required. Candidate-weighted Brier favors `v28`, candidate-weighted
  log loss favors `market_side_ask`, and equal-market Brier/log loss favor
  `candle_brownian`. The research candidate fell back negative on equal-market
  selected PnL and remains negative on equal-market top-EV-bucket PnL.
  After the 04:30 ET post-close refresh, the aggregate has `32` valid ready
  diagnostics, `510` joined rows, and `18` markets, with `1` invalid diagnostic
  skipped. Market diversity is still the blocker: `22` more distinct markets
  are required. Candidate-weighted Brier favors `v28`, candidate-weighted
  log loss favors `market_side_ask`, and equal-market Brier/log loss favor
  `candle_brownian`. The research candidate is positive on equal-market
  selected PnL but still has a negative equal-market top-EV bucket and trails
  the probability baselines.
  After the 04:45 ET post-close refresh, the aggregate has `33` valid ready
  diagnostics, `528` joined rows, and `19` markets, with `1` invalid diagnostic
  skipped. Market diversity is still the blocker: `21` more distinct markets
  are required. Candidate-weighted Brier favors `v28`, candidate-weighted
  log loss favors `market_side_ask`, and equal-market Brier/log loss favor
  `candle_brownian`. The research candidate is again negative on equal-market
  selected PnL and top-EV-bucket PnL.
  After the 05:00 ET post-close refresh, the aggregate has `34` valid ready
  diagnostics, `546` joined rows, and `20` markets, with `1` invalid diagnostic
  skipped. Market diversity is now halfway to the predeclared floor, with `20`
  more distinct markets required. Candidate-weighted Brier favors `v28`,
  candidate-weighted log loss favors `market_side_ask`, and equal-market
  Brier/log loss favor `candle_brownian`. The research candidate is only
  slightly positive on equal-market selected PnL, but its equal-market
  top-EV-bucket PnL remains negative and its probability scores still trail
  the baselines.
- added `paired_sidecar_spot_refresh.py`, a maintenance/reporting command for
  existing paired sidecar/spot artifacts. It collects no new pre-close market
  snapshots, places no orders, and touches no live bot state. With `--write`, it
  re-enriches all paired manifests, reruns per-capture tick-vs-candle
  diagnostics, rebuilds the aggregate, and refreshes the goal audit. It now also
  has an explicit `--fetch-labels` option that runs the existing sidecar
  settlement-label refresh with `collect_mode=none` before rebuilding paired
  diagnostics, so a post-close paired refresh can advance pending captures
  without taking a new pre-close snapshot. The post-01:15 refresh used
  `--fetch-labels --label-timeout-seconds 20 --write`, saw `12` manifests,
  skipped `2` invalid/not-ready captures, made `10` diagnostics ready, left
  `0` pending diagnostics, and kept `promotion_allowed=False`.
  The post-01:30 refresh saw `16` manifests, skipped `2`, made `14`
  diagnostics ready, left `0` pending diagnostics, met the row floor, but still
  kept `promotion_allowed=False` because the market floor and model gates fail.
  The post-01:45 refresh saw `19` manifests, skipped `2`, made `17`
  diagnostics ready, left `0` pending diagnostics, and kept
  `promotion_allowed=False`.
  The post-02:00 refresh saw `22` manifests, skipped `2`, made `20`
  diagnostics ready, left `0` pending diagnostics, and kept
  `promotion_allowed=False`.
  The post-02:15 refresh saw `25` manifests, skipped `2`, made `23`
  diagnostics ready, left `0` pending diagnostics, and kept
  `promotion_allowed=False`.
  The post-02:30 refresh saw `26` manifests, skipped `2`, made `24`
  diagnostics ready, left `0` pending diagnostics, and kept
  `promotion_allowed=False`. The post-02:45 refresh saw `27` manifests,
  skipped `2`, made `25` diagnostics ready, left `0` pending diagnostics, and
  kept `promotion_allowed=False`. The post-03:00 refresh saw `28` manifests,
  skipped `2`, made `26` diagnostics ready, left `0` pending diagnostics, and
  kept `promotion_allowed=False`. After queuing the 03:15 market, the refresh
  state is `29` manifests, `2` skipped, `27` enrichment-ready, `26`
  diagnostics-ready, and `1` pending diagnostic. The post-03:15 refresh saw
  `29` manifests, skipped `2`, made `27` diagnostics ready, left `0` pending
  diagnostics, and kept `promotion_allowed=False`. After queuing the 03:30
  market, the refresh state is `30` manifests, `2` skipped, `28`
  enrichment-ready, `27` diagnostics-ready, and `1` pending diagnostic. The
  post-03:30 refresh saw `30` manifests, skipped `2`, made `28` diagnostics
  ready, left `0` pending diagnostics, and kept `promotion_allowed=False`.
  After queuing the 03:45 market, the refresh state is `31` manifests, `2`
  skipped, `29` enrichment-ready, `28` diagnostics-ready, and `1` pending
  diagnostic. The post-03:45 refresh saw `31` manifests, skipped `2`, made
  `29` diagnostics ready, left `0` pending diagnostics, and kept
  `promotion_allowed=False`. After queuing the 04:00 market, the refresh state
  is `32` manifests, `2` skipped, `30` enrichment-ready, `29`
  diagnostics-ready, and `1` pending diagnostic. The post-04:00 refresh saw
  `32` manifests, skipped `2`, made `30` diagnostics ready, left `0` pending
  diagnostics, and kept `promotion_allowed=False`. After queuing the 04:15
  market, the refresh state is `33` manifests, `2` skipped, `31`
  enrichment-ready, `30` diagnostics-ready, and `1` pending diagnostic. The
  post-04:15 refresh saw `33` manifests, skipped `2`, made `31` diagnostics
  ready, left `0` pending diagnostics, and kept `promotion_allowed=False`.
  After queuing the 04:30 market, the refresh state is `34` manifests, `2`
  skipped, `32` enrichment-ready, `31` diagnostics-ready, and `1` pending
  diagnostic. The post-04:30 refresh saw `34` manifests, skipped `2`, made
  `32` diagnostics ready, left `0` pending diagnostics, and kept
  `promotion_allowed=False`. After queuing the 04:45 market, the refresh state
  is `35` manifests, `2` skipped, `33` enrichment-ready, `32`
  diagnostics-ready, and `1` pending diagnostic. The post-04:45 refresh saw
  `35` manifests, skipped `2`, made `33` diagnostics ready, left `0` pending
  diagnostics, and kept `promotion_allowed=False`. After queuing the 05:00
  market, the refresh state is `36` manifests, `2` skipped, `34`
  enrichment-ready, `33` diagnostics-ready, and `1` pending diagnostic. The
  post-05:00 refresh saw `36` manifests, skipped `2`, made `34` diagnostics
  ready, left `0` pending diagnostics, and kept `promotion_allowed=False`.
  After queuing the 05:15 market, the refresh state is `37` manifests, `2`
  skipped, `35` enrichment-ready, `34` diagnostics-ready, and `1` pending
  diagnostic. The post-05:15 refresh saw `37` manifests, skipped `2`, made
  `35` diagnostics ready, left `0` pending diagnostics, moved the aggregate to
  `564` rows / `21` markets, and kept `promotion_allowed=False`. The
  row-weighted aggregate still had `v28` best on Brier/log-loss; equal-market
  weighting had `v28` best on Brier and `candle_brownian` best on log-loss.
  The candidate row was positive on selected PnL but still negative in the top
  predicted-EV bucket, so `candidate_ready_for_predeclared_shadow=False`.
  After queuing the 05:30 market, the refresh state is `38` manifests, `2`
  skipped, `36` enrichment-ready, `35` diagnostics-ready, and `1` pending
  diagnostic. The post-05:30 refresh saw `38` manifests, skipped `2`, made
  `36` diagnostics ready, left `0` pending diagnostics, moved the aggregate to
  `582` rows / `22` markets, and kept `promotion_allowed=False`. `v28` still
  won row-weighted Brier/log-loss and equal-market Brier; `candle_brownian`
  still won equal-market log-loss. The candidate remained
  `candidate_ready_for_predeclared_shadow=False`, with equal-market top-EV
  bucket PnL still negative. After queuing the 05:45 market, the refresh state
  is `39` manifests, `2` skipped, `37` enrichment-ready, `36`
  diagnostics-ready, and `1` pending diagnostic. The post-05:45 refresh saw
  `39` manifests, skipped `2`, made `37` diagnostics ready, left `0` pending
  diagnostics, moved the aggregate to `600` rows / `23` markets, and kept
  `promotion_allowed=False`. `v28` now wins row-weighted and equal-market
  Brier/log-loss. After queuing the 06:00 market, the refresh state is `40`
  manifests, `2` skipped, `38` enrichment-ready, `37` diagnostics-ready, and
  `1` pending diagnostic. The post-06:00 refresh saw `40` manifests, skipped
  `2`, made `38` diagnostics ready, left `0` pending diagnostics, moved the
  aggregate to `618` rows / `24` markets, and kept
  `promotion_allowed=False`. After queuing the 06:15 market, the refresh state
  is `41` manifests, `2` skipped, `39` enrichment-ready, `38`
  diagnostics-ready, and `1` pending diagnostic. The post-06:15 refresh saw
  `41` manifests, skipped `2`, made `39` diagnostics ready, left `0` pending
  diagnostics, moved the aggregate to `636` rows / `25` markets, and kept
  `promotion_allowed=False`. After queuing the 06:30 market, the refresh state
  is `42` manifests, `2` skipped, `40` enrichment-ready, `39`
  diagnostics-ready, and `1` pending diagnostic. The post-06:30 refresh saw
  `42` manifests, skipped `2`, made `40` diagnostics ready, left `0` pending
  diagnostics, moved the aggregate to `654` rows / `26` markets, and kept
  `promotion_allowed=False`. After queuing the 06:45 market, the refresh state
  is `43` manifests, `2` skipped, `41` enrichment-ready, `40`
  diagnostics-ready, and `1` pending diagnostic. The post-06:45 refresh saw
  `43` manifests, skipped `2`, made `41` diagnostics ready, left `0` pending
  diagnostics, moved the aggregate to `672` rows / `27` markets, and kept
  `promotion_allowed=False`. After queuing the 07:00 market, the refresh state
  is `44` manifests, `2` skipped, `42` enrichment-ready, `41`
  diagnostics-ready, and `1` pending diagnostic. The post-07:00 refresh saw
  `44` manifests, skipped `2`, made `42` diagnostics ready, left `0` pending
  diagnostics, moved the aggregate to `690` rows / `28` markets, and kept
  `promotion_allowed=False`. After queuing the 07:15 market, the refresh state
  is `45` manifests, `2` skipped, `43` enrichment-ready, `42`
  diagnostics-ready, and `1` pending diagnostic. The post-07:15 refresh saw
  `45` manifests, skipped `2`, made `43` diagnostics ready, left `0` pending
  diagnostics, moved the aggregate to `708` rows / `29` markets, and kept
  `promotion_allowed=False`. After queuing the 07:30 market, the refresh state
  is `46` manifests, `2` skipped, `44` enrichment-ready, `43`
  diagnostics-ready, and `1` pending diagnostic. The post-07:30 refresh saw
  `46` manifests, skipped `2`, made `44` diagnostics ready, left `0` pending
  diagnostics, moved the aggregate to `726` rows / `30` markets, and kept
  `promotion_allowed=False`; the aggregate still needs `10` more settled
  markets for the predeclared shadow floor. After queuing the 07:45 market, the
  refresh state is `47` manifests, `2` skipped, `45` enrichment-ready, `44`
  diagnostics-ready, and `1` pending diagnostic. The post-07:45 refresh saw
  `47` manifests, skipped `2`, made `45` diagnostics ready, left `0` pending
  diagnostics, moved the aggregate to `744` rows / `31` markets, and kept
  `promotion_allowed=False`; the aggregate still needs `9` more settled markets
  for the predeclared shadow floor. After queuing the 08:00 market, the refresh
  state is `48` manifests, `2` skipped, `46` enrichment-ready, `45`
  diagnostics-ready, and `1` pending diagnostic. The post-08:00 refresh printed
  a complete summary before the shell timeout and was verified on disk: `48`
  manifests, skipped `2`, `46` diagnostics ready, `0` pending diagnostics, `762`
  rows / `32` markets, and `promotion_allowed=False`; the aggregate still needs
  `8` more settled markets for the predeclared shadow floor. After queuing the
  08:15 market, the refresh state is `49` manifests, `2` skipped, `47`
  enrichment-ready, `46` diagnostics-ready, and `1` pending diagnostic. The
  post-08:15 refresh saw `49` manifests, skipped `2`, made `47` diagnostics
  ready, left `0` pending diagnostics, moved the aggregate to `780` rows / `33`
  markets, and kept `promotion_allowed=False`; the aggregate still needs `7`
  more settled markets for the predeclared shadow floor. After queuing the
  08:30 market, the refresh state is `50` manifests, `2` skipped, `48`
  enrichment-ready, `47` diagnostics-ready, and `1` pending diagnostic. The
  post-08:30 refresh saw `50` manifests, skipped `2`, made `48` diagnostics
  ready, left `0` pending diagnostics, moved the aggregate to `798` rows / `34`
  markets, and kept `promotion_allowed=False`; the aggregate still needs `6`
  more settled markets for the predeclared shadow floor. After queuing the
  08:45 market, the refresh state is `51` manifests, `2` skipped, `49`
  enrichment-ready, `48` diagnostics-ready, and `1` pending diagnostic. The
  post-08:45 refresh saw `51` manifests, skipped `2`, made `49` diagnostics
  ready, left `0` pending diagnostics, moved the aggregate to `816` rows / `35`
  markets, and kept `promotion_allowed=False`; the aggregate still needs `5`
  more settled markets for the predeclared shadow floor. After queuing the
  09:00 market, the refresh state is `52` manifests, `2` skipped, `50`
  enrichment-ready, `49` diagnostics-ready, and `1` pending diagnostic. The
  post-09:00 refresh saw `52` manifests, skipped `2`, made `50` diagnostics
  ready, left `0` pending diagnostics, moved the aggregate to `834` rows / `36`
  markets, and kept `promotion_allowed=False`; the aggregate still needs `4`
  more settled markets for the predeclared shadow floor. After queuing the
  09:15 market, the refresh state is `53` manifests, `2` skipped, `51`
  enrichment-ready, `50` diagnostics-ready, and `1` pending diagnostic. The
  post-09:15 refresh saw `53` manifests, skipped `2`, made `51` diagnostics
  ready, left `0` pending diagnostics, moved the aggregate to `852` rows / `37`
  markets, and kept `promotion_allowed=False`; the aggregate still needs `3`
  more settled markets for the predeclared shadow floor. After queuing the
  09:30 market, the refresh state is `54` manifests, `2` skipped, `52`
  enrichment-ready, `51` diagnostics-ready, and `1` pending diagnostic. The
  post-09:30 refresh saw `54` manifests, skipped `2`, made `52` diagnostics
  ready, left `0` pending diagnostics, moved the aggregate to `870` rows / `38`
  markets, and kept `promotion_allowed=False`; the aggregate still needs `2`
  more settled markets for the predeclared shadow floor. After queuing the
  09:45 market, the refresh state is `55` manifests, `2` skipped, `53`
  enrichment-ready, `52` diagnostics-ready, and `1` pending diagnostic. The
  post-09:45 refresh saw `55` manifests, skipped `2`, made `53` diagnostics
  ready, left `0` pending diagnostics, moved the aggregate to `888` rows / `39`
  markets, and kept `promotion_allowed=False`; the aggregate still needs `1`
  more settled market for the predeclared shadow floor. After queuing the
  10:00 market, the refresh state is `56` manifests, `2` skipped, `54`
  enrichment-ready, `53` diagnostics-ready, and `1` pending diagnostic. The
  post-10:00 refresh saw `56` manifests, skipped `2`, made `54` diagnostics
  ready, left `0` pending diagnostics, moved the aggregate to `906` rows / `40`
  markets, and hit the predeclared paired live-shadow floor with `0` remaining
  rows and `0` remaining markets. It still kept `promotion_allowed=False` and
  `goal_complete=False` because the model/economic gates did not clear. The
  refresh helper now routes
  aggregate output
  beside custom refresh output paths, so unit tests and temp dry runs cannot
  overwrite the real `paired_sidecar_spot_aggregate_latest.*` research reports.
  It also writes the current refresh summary before running the goal audit, so
  the audit does not read a stale pending-diagnostic count.
- captured another live paired sidecar/spot sample at
  `20260512T042831Z-c2afca25`. It used one current Kalshi BTC15M market,
  wrote `133` independent Coinbase ticks, and aligned the sidecar decision to a
  no-future spot tick only `61.769ms` old. A later post-close refresh joined
  its settlement labels, so the paired aggregate now shows `4` manifests,
  `4` enrichment-ready diagnostics, aggregate fresh `True`, aggregate deficits
  `144` rows / `37` markets, goal audit refreshed `True`, and goal complete
  `False`.
- attempted another paired capture at `20260512T043558Z-57f05abf`, but the
  sidecar collection reported `blocked_collection_error` and the sidecar batch
  timestamp was stale relative to the spot tape. `paired_capture_ready=False`
  blocked it from evidence. The paired capture code now ignores the latest
  sidecar batch after `blocked_collection_error`, and the refresh command skips
  not-ready manifests as `paired_capture_not_ready`. Current refresh state:
  `5` manifests, `1` skipped, `4` enrichment-ready, `4` diagnostics-ready,
  `0` pending, aggregate still `56` rows / `3` markets. The main goal audit
  now includes this refresh report directly so failed/latest capture attempts
  cannot obscure the clean aggregate state.
- collected four clean live paired sidecar/spot samples for the
  `KXBTC15M-26MAY120100-00` market before its `2026-05-12T05:00:00Z` close:
  `20260512T044743Z-cf2d9b77`, `20260512T045058Z-c0f3ae7e`,
  `20260512T045217Z-18f5fa9f`, and `20260512T045334Z-44ba5b16`. Each selected
  the same concrete-strike BTC15M market (`81227.97`), had `14` packet rows,
  aligned to a no-future independent Coinbase spot tick, and remained
  `promotion_allowed=False`. Running
  `python -m research_particle.paired_sidecar_spot_refresh --fetch-labels
  --label-timeout-seconds 20 --write` after close joined all four into
  diagnostics, moving the paired aggregate to `112` rows / `4` markets with
  `0` pending diagnostics.
- collected and post-close joined two clean live paired sidecar/spot samples
  for the next distinct market, `KXBTC15M-26MAY120115-15`, before its
  `2026-05-12T05:15:00Z` close: `20260512T050302Z-3f550c5a` and
  `20260512T051026Z-9ddad506`. Both selected the same concrete-strike market
  (`81201.6`), aligned to no-future independent spot ticks, and remained
  `promotion_allowed=False`.
- quarantined one bad paired capture, `20260512T050513Z-cf1aabbf`, after it
  exposed a same-window latest-batch mismatch: the paired cycle requested
  `public_rest`, but the loaded sidecar batch summary was `fixture` mode and
  contained already-expired May 11 demo markets. The paired capture helper now
  rejects batch-mode mismatches, the public REST batch builder has an extra
  non-simulated pre-close guard at bundle construction, and paired refresh skips
  existing mismatched or non-preclose manifests as research-invalid. The paired
  aggregate now also requires each diagnostic file's sibling manifest to pass
  the same readiness/mode/preclose checks before its rows enter aggregate
  metrics; invalid diagnostic files are counted as skipped instead of silently
  affecting Brier/log-loss/PnL summaries. It also writes
  `market_equal_model_rows` and top-level equal-market winners so repeated
  captures from one 15-minute market cannot masquerade as broad market
  stability.
- collected and post-close joined four clean live paired sidecar/spot samples
  for `KXBTC15M-26MAY120130-30` before its `2026-05-12T05:30:00Z` close:
  `20260512T052114Z-c1febf64`, `20260512T052213Z-eabc61c0`,
  `20260512T052252Z-4ce96717`, and `20260512T052353Z-e4df05b9`. Each selected
  the same concrete-strike market (`81195.96`), had `16` packet rows, aligned
  to a no-future independent Coinbase spot tick, and remained
  `promotion_allowed=False`.
- collected and post-close joined three clean live paired sidecar/spot samples
  for `KXBTC15M-26MAY120145-45` before its `2026-05-12T05:45:00Z` close:
  `20260512T053637Z-e578b4ea`, `20260512T053846Z-4017f148`, and
  `20260512T053949Z-cd9dea99`. Each selected the same concrete-strike market
  (`81270.06`), had `16` packet rows, aligned to a no-future independent spot
  tick, and remained `promotion_allowed=False`.
- collected and post-close joined three clean live paired sidecar/spot samples
  for `KXBTC15M-26MAY120200-00` before its `2026-05-12T06:00:00Z` close:
  `20260512T054716Z-d282f3dc`, `20260512T054948Z-93f34199`, and
  `20260512T055058Z-c750296d`. Each selected the same concrete-strike market
  (`81250.39`), had `16` packet rows, aligned to a no-future independent spot
  tick, and remained `promotion_allowed=False`.
- collected and post-close joined three clean live paired sidecar/spot samples
  for `KXBTC15M-26MAY120215-15` before its `2026-05-12T06:15:00Z` close:
  `20260512T060238Z-8f03ea16`, `20260512T060526Z-549f3a8f`, and
  `20260512T060639Z-7053f5ee`. Each selected the same concrete-strike market
  (`81232.14`), had `16` packet rows, aligned to a no-future independent spot
  tick, and remained `promotion_allowed=False`.
- collected and post-close joined one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120230-30` before its `2026-05-12T06:30:00Z` close:
  `20260512T062009Z-cbbf7244`. It selected one concrete-strike market
  (`81243.73`), had `16` packet rows, aligned to a no-future independent
  Coinbase spot tick `33.753ms` old, wrote `269` spot ticks, and remained
  `promotion_allowed=False`.
- collected and post-close joined one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120245-45` before its `2026-05-12T06:45:00Z` close:
  `20260512T063515Z-36071ae0`. It selected one concrete-strike market
  (`81205.05`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `793.15ms` old, wrote `63` spot ticks, and remained
  `promotion_allowed=False`.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120300-00` before its `2026-05-12T07:00:00Z` close:
  `20260512T064725Z-906c012d`. It selected one concrete-strike market
  (`81074.07`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `266.345ms` old, wrote `25` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120315-15` before its `2026-05-12T07:15:00Z` close:
  `20260512T070246Z-76def8cb`. It selected one concrete-strike market
  (`81010.57`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `46.417ms` old, wrote `142` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120330-30` before its `2026-05-12T07:30:00Z` close:
  `20260512T071745Z-a6d60222`. It selected one concrete-strike market
  (`81055.74`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `281.716ms` old, wrote `62` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120345-45` before its `2026-05-12T07:45:00Z` close:
  `20260512T073253Z-dc9fab1a`. It selected one concrete-strike market
  (`81020.23`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `474.591ms` old, wrote `121` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120400-00` before its `2026-05-12T08:00:00Z` close:
  `20260512T074816Z-2a7ae134`. It selected one concrete-strike market
  (`80931.23`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `240.448ms` old, wrote `58` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120415-15` before its `2026-05-12T08:15:00Z` close:
  `20260512T080307Z-761179ae`. It selected one concrete-strike market
  (`80837.14`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `776.992ms` old, wrote `166` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120430-30` before its `2026-05-12T08:30:00Z` close:
  `20260512T081801Z-8b6f7f98`. It selected one concrete-strike market
  (`80790.15`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `137.013ms` old, wrote `107` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120445-45` before its `2026-05-12T08:45:00Z` close:
  `20260512T083333Z-a3c2fc42`. It selected one concrete-strike market
  (`80846.76`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `586.543ms` old, wrote `67` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120500-00` before its `2026-05-12T09:00:00Z` close:
  `20260512T084825Z-fa7871e3`. It selected one concrete-strike market
  (`80928.16`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `571.745ms` old, wrote `87` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120515-15` before its `2026-05-12T09:15:00Z` close:
  `20260512T090316Z-bce07f24`. It selected one concrete-strike market
  (`80846.76`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `511.543ms` old, wrote `105` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120530-30` before its `2026-05-12T09:30:00Z` close:
  `20260512T091859Z-1052e828`. It selected one concrete-strike market
  (`80754.1`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `398.496ms` old, wrote `66` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120545-45` before its `2026-05-12T09:45:00Z` close:
  `20260512T093239Z-81b53b80`. It selected one concrete-strike market
  (`80707.68`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `429.384ms` old, wrote `79` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120600-00` before its `2026-05-12T10:00:00Z` close:
  `20260512T095327Z-bd73d0d6`. It selected one concrete-strike market
  (`80918.1`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `491.885ms` old, wrote `72` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120615-15` before its `2026-05-12T10:15:00Z` close:
  `20260512T100225Z-24fe2771`. It selected one concrete-strike market
  (`80806.06`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `62.594ms` old, wrote `70` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120630-30` before its `2026-05-12T10:30:00Z` close:
  `20260512T101829Z-bbb1ccc2`. It selected one concrete-strike market
  (`80784.86`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `223.653ms` old, wrote `100` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120645-45` before its `2026-05-12T10:45:00Z` close:
  `20260512T103256Z-db0f1603`. It selected one concrete-strike market
  (`80697.34`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `682.321ms` old, wrote `101` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120700-00` before its `2026-05-12T11:00:00Z` close:
  `20260512T104752Z-274342fd`. It selected one concrete-strike market
  (`80661.14`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `787.12ms` old, wrote `59` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120715-15` before its `2026-05-12T11:15:00Z` close:
  `20260512T110319Z-bcbe85a9`. It selected one concrete-strike market
  (`80642.68`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `334.104ms` old, wrote `99` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120730-30` before its `2026-05-12T11:30:00Z` close:
  `20260512T111831Z-1bf68d78`. It selected one concrete-strike market
  (`80569.34`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `718.794ms` old, wrote `111` spot ticks, and remained
  `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120745-45` before its `2026-05-12T11:45:00Z` close:
  `20260512T113635Z-6772bd84`. It selected one concrete-strike market
  (`80612.56`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `750.178ms` old at decision, wrote `72` spot ticks, and
  remained `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120800-00` before its `2026-05-12T12:00:00Z` close:
  `20260512T114939Z-f5954c53`. It selected one concrete-strike market
  (`80711.91`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `758.788ms` old at decision, wrote `252` spot ticks, and
  remained `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120815-15` before its `2026-05-12T12:15:00Z` close:
  `20260512T120500Z-368311e2`. It selected one concrete-strike market
  (`80756.58`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `731.946ms` old at decision, wrote `75` spot ticks, and
  remained `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120830-30` before its `2026-05-12T12:30:00Z` close:
  `20260512T121932Z-120fa0f9`. It selected one concrete-strike market
  (`80804.26`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `272.011ms` old at decision, wrote `534` spot ticks, and
  remained `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120845-45` before its `2026-05-12T12:45:00Z` close:
  `20260512T123357Z-21890214`. It selected one concrete-strike market
  (`80794.44`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `750.852ms` old at decision, wrote `334` spot ticks, and
  remained `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120900-00` before its `2026-05-12T13:00:00Z` close:
  `20260512T124931Z-5cb4c5dc`. It selected one concrete-strike market
  (`80871.6`), had `18` packet rows, aligned to a no-future independent Coinbase
  spot tick `63.331ms` old at decision, wrote `483` spot ticks, had the first
  spot tick after decision only `0.702ms` later, and
  remained `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120915-15` before its `2026-05-12T13:15:00Z` close:
  `20260512T130438Z-0c475a7b`. It selected one concrete-strike market
  (`80857.06`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `94.584ms` old at decision, wrote `113` spot ticks, had the
  first spot tick after decision `32.33ms` later, and
  remained `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120930-30` before its `2026-05-12T13:30:00Z` close:
  `20260512T131925Z-46dc20ac`. It selected one concrete-strike market
  (`80814.53`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `79.446ms` old at decision, wrote `539` spot ticks, had the
  first spot tick after decision `47.668ms` later, and
  remained `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY120945-45` before its `2026-05-12T13:45:00Z` close:
  `20260512T133435Z-cd2c47fa`. It selected one concrete-strike market
  (`80631.73`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `15.301ms` old at decision, wrote `503` spot ticks, had the
  first spot tick after decision `0.602ms` later, and
  remained `promotion_allowed=False` after post-close label join.
- queued one clean live paired sidecar/spot sample for
  `KXBTC15M-26MAY121000-00` before its `2026-05-12T14:00:00Z` close:
  `20260512T134957Z-6e48eced`. It selected one concrete-strike market
  (`80762.39`), had `18` packet rows, aligned to a no-future independent
  Coinbase spot tick `191.67ms` old at decision, wrote `376` spot ticks, had the
  first spot tick after decision `207.497ms` later, and
  remained `promotion_allowed=False` after post-close label join.
- added `research_particle/paired_sidecar_online_calibration.py`, a
  research-only live-paired aggregate diagnostic that applies online logit
  calibration only after each source capture's market close timestamp. On the
  current `906` joined-row / `40` joined-market aggregate, the best calibrated
  candidate (`online_logit_candidate_lr010_row`) improves raw candidate
  Brier/log-loss from `0.293685/0.997760` to `0.258442/0.738256` and improves
  row-weighted top-EV bucket PnL from `-243.6c` to `+767.8c`. The added
  market-stability view remains below promotion quality: the best calibrated
  model has positive top-EV bucket PnL in `18/40` settled markets and positive
  selected PnL in `21/40`. Fixed tiny blends remain in the same report:
  `blend_v28_online_lr010_w10` is best row-weighted Brier,
  `blend_market_online_lr010_w15` is best row-weighted log-loss, and
  `blend_v28_online_lr010_w25` is best blend by market-equal Brier. The best
  blend stability counts are `23/40` positive top-EV markets and `23/40`
  positive selected-PnL markets. The canonical paired aggregate now has
  `candidate_ready_for_predeclared_shadow=True`, but still
  `promotion_allowed=False`: `v28` remains best row-weighted Brier,
  `market_side_ask` remains best row-weighted log-loss, and `candle_brownian`
  wins equal-market Brier/log-loss. This remains
  research-only and `promotion_allowed=False`.
- hardened paired sidecar/spot capture against stale latest-batch reuse even
  without an explicit collection exception. For fresh paired collection modes,
  `paired_sidecar_spot_capture.py` now records the capture start/end timestamps
  and only accepts the loaded latest sidecar batch if its `generated_utc` falls
  inside that paired capture window, with a small tolerance. Out-of-window or
  missing timestamps produce empty non-promoting batch reports instead of
  silently pairing independent spot ticks to stale sidecar rows.
- patched the public REST batch selector so `--all-open-closes` no longer
  returns immediately after the first status bucket. Nearest-close behavior is
  unchanged, but broad mode now scans across status buckets before selecting
  eligible BTC15M rows. A live dry run still found only `1` bundle-ready market:
  the current open BTC15M row had a concrete strike, while future initialized
  rows were mostly `TBD` and are intentionally filtered from strict replay until
  a timestamp-safe strike source exists. This means the immediate market
  diversity bottleneck is the public feed/strike availability, not only the
  selector.
- added the strict artifact leakage audit:
  `artifact_leakage_audit_20260511_nine_locked` verifies candidate and label
  timestamps directly on the nine locked roots. It audited `33,205` candidate
  rows, `51` labels/markets, and found `0` issues:
  no candidate `recv_ts_utc` after decision, no label available at or before a
  decision, no settlement timestamp at or before a decision, no missing labels,
  and no timestamped extra fields from the future. The goal audit now marks
  "strict replay uses only timestamp-available information" as `pass`.
- added the denominator integrity audit:
  `denominator_integrity_audit_20260511_nine_locked` verifies that locked
  passive replay reports preserve the full all-candidate denominator. It audited
  the same nine locked roots and found `candidate_file_count`,
  `source_candidate_count`, `candidate_count`, and decision count all match,
  with `skipped_unlabeled_count=0`, `denominator_scope=all_labeled_candidates`,
  `all_candidate_denominator=True`, and `0` missing-label markets. The goal
  audit now marks both "trustworthy recorder/labeler" and
  "all-candidate denominator" as `pass`.
- refreshed goal completion audit after the RV-anchor/residual diagnostics:
  `complete=False`, `strict_real_candidate_rows=34943`,
  `real_replay_reports=36`, `locked_oos_stability_rows=43`, and
  `locked_oos_stable_candidate_count=0`. The audit now includes
  `spot_drift_regime`, `spot_rv_anchor_switch_loro`, and
  `spot_rv_current_residual_loro` in the probability, EV-rank, and shadow-PnL
  gate details.
- side-fill/source synthetic fixture CLI:
  `candidate_count=4`, `selected_count=4`,
  `total_counterfactual_pnl_cents=141.0000`,
  `particle_beats_all_baselines=True`,
  `shadow_counterfactual_positive=True`
- synthetic fixture CLI: `candidate_count=4`, `selected_count=4`,
  `total_counterfactual_pnl_cents=141.0000`,
  `particle_beats_all_baselines=True`,
  `shadow_counterfactual_positive=True`
- generic report CLI: `particle_beats_brownian=True`,
  `particle_beats_market=True`,
  `particle_beats_current_calibrated=True`,
  `ev_rank_correlation_sign=0.600000`,
  `top_ev_bucket_pnl_cents=39.0000`
- adapter readiness audit: `artifact_count=1273`, `adapter_ready_count=0`;
  no existing logs/stats/state artifact has every strict replay field.
- v28 event context audit: `adapted_count=0`, `issue_count=1042`;
  issue reasons were `missing_exact_two_sided_asks=643`,
  `unsupported_event_type=377`, and `missing_core_v28_fields=22`.
- verification after anchor-switch, RV-anchor LORO, RV-current-residual LORO,
  empirical/current-anchored/market-opportunity next-second particle
  diagnostics, market-opportunity LORO, next-second spot-drift/regime
  diagnostics, artifact-leakage audit, denominator-integrity audit, and paired
  sidecar/spot capture/online-calibration additions:
  `python -m unittest test_research_particle_synthetic.py` passed `108` tests,
  the full `python -m unittest test_v28_successor_pipeline.py` suite passed
  `97` tests, including stale-batch capture-window guards, batch-mode mismatch
  quarantine, non-preclose manifest quarantine, expired-market bundle blocking,
  equal-market aggregate metrics, invalid diagnostic exclusion, custom-output
  aggregate isolation, refresh-before-goal-audit ordering, and the research-only
  `--fetch-labels` refresh switch, plus paired-sidecar online calibration
  market-close label gating,
  and `python -m
  compileall .\research_particle\paired_sidecar_online_calibration.py
  .\test_v28_successor_pipeline.py`
  passed.

## Next Concrete Steps

1. Treat `particle_shadow_readonly` as a plumbing smoke test only. It produced a
   negative real replay and used one market, so it is not strategy evidence.
2. Do not tune thresholds on the failed full replay; the fixed
   market/current-anchored variants and rolling-vol diagnostics are now
   recorded on all-candidate denominators. The side-safety rule failed its
   locked OOS test and should not be pursued as-is.
3. The locked `rolling_vol_300s_v1`, `rolling_vol_600s_v1`, ensemble
   diagnostics, and online-logit diagnostics all failed strict promotion, for
   different reasons. Do not relax gates after the fact. The next research step
   should be model improvement with a better predeclared side/regime-state
   hypothesis, not another single-window winner chase. The fresh market/current
   agreement veto test is negative evidence: simple market-consensus gating
   saved one late-market loss but reduced locked-OOS aggregate PnL and did not
   repair the weak third lock. The consolidated side/regime diagnostic also
   found no stable-positive consensus/time rule. The residual blend LORO
   diagnostic found only a small same-evidence lift over current calibrated and
   failed holdout probability/PnL consistency. `RESIDLOCK001` then tested that
   exact residual blend fresh and failed badly (`-28864c`), so do not pursue the
   residual blend as-is. The five-run EV-rank/calibration diagnostic now shows
   the highest predicted EV bucket is positive in only `1/5` runs and
   `current_calibrated` still beats particle on aggregate Brier/log-loss. The
   best five-run aggregate row after filling the missing residual ensemble
   report is only a tiny current-anchored blend (`current_particle_75_25`) and
   it beats current in just `2/5` runs. The LORO selector diagnostic reinforces
   this: choosing by historical PnL loses `-127077c` on holdouts, and even the
   best gate-score selector clears strict gates in only `1/5` holdouts. The
   market-cluster diagnostic says the same thing after equal-weighting each
   resolved 15m market: EV rank is negative and the highest-EV market bucket is
   negative. Simple market-cluster-trained logit meta-calibration also failed
   locked LORO (`0/5` strict gates and `0/5` beats current). Timestamp-available
   state-feature LORO failed the same way (`0/5` strict gates and `0/5` beats
   current). Expanded independent-spot microfeature LORO is less underpowered
   (`4/7` eligible locked roots) but still negative (`0/4` beats Brownian,
   market, or current). `GAUSS45LOCK003` completed the fresh predeclared
   low-vol terminal-probability run and failed on live-shadow PnL/EV gates.
   The PASC threshold LORO and anchor-switch LORO also failed strict holdout
   gates. `RVTERMLOCK001` then tested the local-realized-vol terminal idea on a
   fresh predeclared live-shadow run; it made positive counterfactual PnL, but
   current-calibrated remained better on Brier/log-loss and PnL, and EV-rank/top
   bucket gates failed. Materializing that variant confirmed the positive PnL
   did not come from a reliable predicted-EV ordering. The RV-aware anchor
  switch LORO also failed (`1/6` strict gates), and its equal-market EV sanity
  checks are only mixed (`3/6` positive market EV rank, `4/6` positive market
  top bucket). A more conservative current-anchored RV residual also failed:
  best strict count `1/6`, best positive-PnL spec `+54559c` but `0/6` strict
   gates. The first capped next-second spot-drift terminal diagnostic had a
   stronger aggregate PnL clue (`+99481c`) but still only `1/6` strict gates and
  mixed equal-market EV sanity. The drift-regime diagnostic then tried to find a
  simple timestamp-safe sub-bucket under that clue and failed across both the
  best spec and all five drift specs (`stable_positive_rules=0`). The empirical
  next-second particle diagnostic is the first literal public-spot one-second
  return particle benchmark; it improved aggregate PnL (`+113066c` best row)
  but still had `0/6` strict gates and only `3/6` beats-current runs. The
  current-anchored empirical version improved the beats-current count to `4/6`
  but lost money overall (`-19237c` best row), so even conservative
  current-plus-empirical nudges are not enough. The market-opportunity
  de-duplication check shows the empirical clue is not purely repeated-row
  inflation (`6/6` positive market-level PnL for one pure empirical spec), but
  the effect is tiny and still fails current/probability/top-bucket gates. The
  LORO score-correction follow-up confirms this was not just a missing tiny EV
  penalty: held-out PnL stayed slightly positive, but strict gates were `0/6`
  and the top EV bucket was positive in only `1/6`. Local realized-vol and spot
  drift should be treated as possible state descriptors, not standalone edges.
  The useful next
  step is a better probability/EV model with genuinely new information,
   not another threshold, calibration overlay,
   shallow state-feature overlay, short-window spot-momentum overlay, or
   fat-tail/local-vol terminal overlay on the same scores.
4. Use the independent spot/context merge and the paired sidecar/spot capture in
   the next longer forward-shadow capture. The sidecar now works on Coinbase,
   and the latest paired sidecar capture proves a real public REST bundle can be
   aligned to no-future independent spot within subsecond freshness. The latest
   residual capture proved the passive path can support a full locked run; the
   blocker is model edge, not basic live-market plumbing.
   The 2026-05-12 16:45 ET labeled sidecar sample increased the paired-sidecar
   aggregate to `1212` rows across `57` markets and again kept promotion closed:
   `particle_edge_candidate_count=0`, `promotion_safe_count=0`, and goal audit
   `complete=False`. It weakened the broad particle locks rather than confirming
   them: `blend_v28_w20_time_gt_600s_v1` fell to `-168.0c` selected PnL and is
   now a retire-from-strategy-consideration row; `blend_v28_w05_time_gt_600s_v1`
   remains positive at `+480.0c`, but still loses to v28 on Brier/log-loss and
   top-EV bucket PnL. This is useful forward-shadow evidence, not a live-trading
   approval.
   The immediately following 2026-05-12 17:00 ET labeled sample pushed the
   aggregate to `1230` rows across `58` markets and rebounded the broad locks
   (`w20 +466.5c`, `w05 +1114.5c`, v28 control `+1071.0c`), so the retirement
   report moved back to `retire_count=0` and `continue_shadow_count=3`. The
   higher bar still did its job: `particle_edge_candidate_count=0`,
   `promotion_safe_count=0`, and goal audit `complete=False` because the
   particle-like locks still do not jointly beat v28 on probability quality,
   selected PnL, top-EV PnL, and promotion gates.
   The 2026-05-12 17:15 ET labeled sample then pushed the aggregate to `1248`
   rows across `59` markets and pulled the broad locks back down (`w20 +70.5c`,
   `w05 +669.0c`, v28 control `+625.5c`). The disagreement slice turned
   negative (`-78.2c` for both particle and v28 control), the worst fresh
   market-level particle row became `blend_v28_w05_time_gt_600s_v1` on
   `KXBTC15M-26MAY121715-15` at `-445.5c`, and the final audit still says
   `complete=False`. Keep all three particle-like locks in shadow-only status.
   A market-stability diagnostic now summarizes each locked hypothesis across
   markets rather than only cumulatively. On the same `1248` row / `59` market
   evidence set, it reports `particle_like_stability_screen_pass_count=0`; the
   most concentrated row is `blend_v28_w15_candidate_v28_gap_05_15pp_v1` with
   max absolute market PnL share `0.424528`. This blocks a common overfitting
   trap: treating one or two favorable markets as a stable edge.
   The 2026-05-12 17:45 ET labeled sample pushed the aggregate to `1266` rows
   across `60` markets. The broad locks stayed non-promotable (`w20 +22.0c`,
   `w05 +669.0c`, v28 control `+625.5c`), the disagreement slice stayed
   negative (`-78.2c` for particle and v28 control), and the new stability
   report still has `particle_like_stability_screen_pass_count=0`.
   `particle_edge_candidate_count=0`, `promotion_safe_count=0`, and goal audit
   `complete=False` remain the controlling state.
   The retirement report is now stability-aware, so positive cumulative PnL is
   no longer enough for a bland `continue_shadow_only` label when market-level
   evidence is underpowered, concentrated, or worse than v28. After the
   2026-05-12 18:15 ET labeled sample, the aggregate is `1284` rows across `61`
   markets; v28 control became the best selected-PnL lock (`+738.0c`), `w05`
   fell behind it (`+681.5c`), `w20` turned negative (`-97.5c`), and the
   disagreement particle remained negative (`-65.7c`). Retirement state is now
   `retire_count=1`, `stability_blocked_count=2`, `continue_shadow_count=0`;
   stability still has `particle_like_stability_screen_pass_count=0` and the
   goal audit remains `complete=False`.
   The 2026-05-12 18:45 ET labeled sample pushed the aggregate to `1302` rows
   across `62` markets. The broad particle locks rebounded in absolute PnL
   (`w20 +112.0c`, `w05 +1073.0c`), but v28 control is still better at
   `+1129.5c`; the disagreement particle remains negative (`-22.2c`) while
   its v28 control is slightly positive (`+2.8c`). Stability still reports
   `particle_like_stability_screen_pass_count=0`, retirement remains
   `retire_count=1`, `stability_blocked_count=2`, and the goal audit remains
   `complete=False`.
   A trajectory diagnostic now checks whether a lock is still working in the
   most recent markets and whether its recent PnL still beats v28. On the same
   `1302` row / `62` market evidence set, it reports
   `particle_like_trajectory_screen_pass_count=0`; the worst recent
   particle-like row is `blend_v28_w15_candidate_v28_gap_05_15pp_v1` with
   last-window selected PnL `-43.0c`. This blocks another stale-edge failure
   mode: carrying a historical burst forward after recent markets have decayed.
   The 2026-05-12 19:15 ET labeled sample pushed the aggregate to `1320` rows
   across `63` markets. Absolute PnL improved (`w20 +665.5c`, `w05 +1626.5c`,
   disagreement particle `+39.3c`), but v28 control is still the best selected
   PnL lock at `+1683.0c` and the disagreement v28 control is also better at
   `+64.3c`. The comparison report still has `particle_edge_candidate_count=0`
   and `promotion_safe_count=0`; stability and trajectory still have
   `particle_like_*_screen_pass_count=0`. Retirement moved back to
   `retire_count=0`, `stability_blocked_count=3`, and the goal audit remains
   `complete=False`.
   The retirement classifier now consumes both stability and trajectory reports.
   On the `1320` row / `63` market state, it reports `stability_blocked_count=3`
   and `trajectory_blocked_count=3`, so every particle-like lock is explicitly
   blocked by both market-level robustness and recent-trajectory diagnostics.
   The pipeline test suite is green at `111` tests and the synthetic particle
   suite remains green at `108` tests after this wiring.
   The 2026-05-12 19:45 ET labeled sample pushed the aggregate to `1338` rows
   across `64` markets. The first label-refresh command exceeded the shell
   timeout, but the Python process finished cleanly afterward and left
   `pending_manifest_count=0`. The particle-like broad locks improved
   (`w20 +1053.5c`, `w05 +2063.0c`), but v28 control is still best at
   `+2119.5c`; `w05` remains `-56.5c` behind v28 on selected PnL even though
   its top-EV bucket is `+60.0c` better. The disagreement particle is positive
   at `+87.8c` but still trails the disagreement v28 control at `+112.8c`.
   No particle edge candidate exists, all promotion-safe flags are false,
   stability/trajectory pass counts remain `0`, retirement stays
   `stability_blocked_count=3` and `trajectory_blocked_count=3`, and the goal
   audit remains `complete=False`.
   A combined promotion-readiness ledger now joins the comparison, stability,
   trajectory, and retirement reports into one diagnostic preflight. It cannot
   authorize live trading, but it makes the all-gates requirement explicit:
   positive selected/top-EV PnL, Brier/log-loss/selected/top-EV improvement vs
   v28, locked-OOS safety, stability pass, trajectory pass, and no retirement
   blocker. On the `1338` row / `64` market state it reports
   `readiness_candidate_count=0` and `hard_veto_count=3`; the goal audit remains
   `complete=False`. The pipeline test suite is green at `113` tests and the
   synthetic particle suite remains green at `108` tests after this wiring.
   The 2026-05-12 20:15 ET labeled sample pushed the aggregate to `1356` rows
   across `65` markets. The label refresh again exceeded the shell timeout but
   finished cleanly afterward with `pending_manifest_count=0`. Absolute PnL
   improved (`w20 +1643.0c`, `w05 +2652.5c`, disagreement particle `+153.3c`),
   but v28 control still leads the broad lock at `+2709.0c`; `w05` remains
   `-56.5c` behind v28 selected PnL and is worse on Brier/log-loss, while the
   disagreement particle is `-25.0c` behind its v28 control and still worse on
   log-loss despite a small Brier/top-EV clue. The combined readiness ledger
   remains `readiness_candidate_count=0`, `hard_veto_count=3`, and the goal
   audit remains `complete=False`.
   The 2026-05-12 20:45 ET labeled sample pushed the aggregate to `1374` rows
   across `66` markets. The capture and label commands both exceeded the shell
   timeout, but their Python processes finished cleanly; the refresh report now
   has `pending_manifest_count=0` and `pending_enriched_rows=0`. The new market
   was a useful stress case, not a promotion case: the broad locks all took
   `-427.5c` on the new market, dropping v28 control to `+2281.5c`, `w05` to
   `+2225.0c`, and `w20` to `+1215.5c`; the disagreement slice took `-47.5c`
   on its one selected row. `w05` still trails v28 by `-56.5c` on selected PnL
   and remains worse on Brier/log-loss, while the disagreement particle keeps a
   small Brier/top-EV clue but trails its v28 control on selected PnL and
   log-loss. The combined readiness ledger remains
   `readiness_candidate_count=0`, `hard_veto_count=3`; stability and trajectory
   pass counts remain `0`; the goal audit remains `complete=False`.
   The 2026-05-12 21:15 ET labeled sample pushed the aggregate to `1392` rows
   across `67` markets. Capture and label again exceeded the shell timeout, but
   each Python process finished cleanly and left no pending labels. This was a
   second fresh drawdown case: broad locks all selected 9 rows and took
   `-472.5c` on `KXBTC15M-26MAY122115-15`; the disagreement slice selected 2
   rows and took `-105.0c`. Aggregate selected PnL fell to v28 control
   `+1809.0c`, `w05 +1752.5c`, `w20 +743.0c`, and disagreement particle
   `+0.8c`. `w05` still trails v28 by `-56.5c` on selected PnL and remains
   worse on Brier/log-loss; the disagreement particle no longer has the small
   Brier clue it had at 20:45 ET. The readiness ledger remains
   `readiness_candidate_count=0`, `hard_veto_count=3`, with every particle-like
   lock blocked by stability, trajectory, and locked-OOS safety gates. The goal
   audit remains `complete=False`.
   A v28 transfer diagnostic now tests whether the particle/rolling-vol clue can
   safely improve v28 rather than replace it. Across ten available real-shadow
   roots, full `rv600` had the best aggregate selected-PnL delta
   (`+38929.0c`) and `v28_80_rv300_20` had the best blend delta
   (`+16528.0c`), but no strategy cleared the strict screen because run-level
   behavior was uneven. The most practical clues are low-weight rolling-vol as a
   v28 feature and a rolling-vol side-agreement veto as a coverage reducer; both
   remain research-only. Latest report:
   `logs/particle_research/reports/v28_rolling_vol_transfer_diagnostic_latest.md`.
   A deployable strategy spec was then written for the strongest projected-PnL
   clue: `docs/research/RV600_TIMED_TERMINAL_EV_STRATEGY.md`. A one-entry
   stress test showed naive first-signal rv600 loses (`-78.0c`), so the
   strategy is narrowed to first qualifying rv600 signal in the `T-420s` to
   `T-70s` window with `min_ev=10c` and max one entry per market. On the current
   ten-root retrospective sample this version selected `33`, made `+682.0c`,
   averaged `20.67c`, and was positive in `8/10` roots. This is a forward-shadow
   hypothesis, not live permission.
   The follow-up variation test plan is
   `docs/research/RV600_VARIATION_TEST_PLAN.md`. It explicitly allows repeated
   same-market entries, but only if added entries remain profitable after fees,
   fill/no-fill assumptions, market-level de-duplication, and matched v28
   timestamp controls.
5. Keep social, pinball, and neural layers out until the simple strict replay
   path has real-data evidence.
