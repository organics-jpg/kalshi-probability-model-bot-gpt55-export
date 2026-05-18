# v28 Anti-Overfit Freeze Audit

- All clear: `True`
- Fail/watch counts: `0/35`

## Candidate Artifacts

| family | artifact | status | freeze ts | dynamic-best risk | failures |
|---|---|---:|---|---:|---|
| target_coverage_fv | `v28_target_coverage_fv_overlay_validator` | `pass` | `2026-05-06T02:08:01.321286+00:00` | `False` | none |
| raw_entry_calibrated_fv | `v28_frozen_raw_entry_calibrated_probability` | `pass` | `2026-05-05T23:30:17.615882+00:00` | `False` | none |
| boundary_memory_fv | `v28_boundary_memory_fv_candidates` | `pass` | `2026-05-06T01:40:40.929142+00:00` | `False` | none |
| reward_memory_fv | `v28_reward_memory_fv_candidates` | `pass` | `2026-05-06T01:46:48.111889+00:00` | `False` | none |
| book_exact_entry_gate | `v28_frozen_book_exact_entry_gate` | `watch` | `2026-05-06T11:33:52.584603+00:00` | `False` | report_has_scored_rows |
| approved_entry_state_valve | `v28_frozen_approved_entry_state_valve` | `watch` | `2026-05-06T02:42:53.253731+00:00` | `False` | report_has_scored_rows |
| approved_entry_book_fv | `v28_frozen_approved_entry_book_fv` | `pass` | `2026-05-06T06:20:06.824407+00:00` | `False` | none |
| danger_zone_entry_valve | `v28_frozen_danger_zone_entry_valve` | `watch` | `2026-05-06T03:09:58.042066+00:00` | `False` | report_has_scored_rows |
| danger_zone_fv_calibration | `v28_frozen_danger_zone_fv_calibration` | `pass` | `2026-05-06T03:14:35.467881+00:00` | `False` | none |
| danger_zone_robustness | `v28_frozen_danger_zone_robustness` | `pass` | `2026-05-06T03:14:35.467881+00:00` | `False` | none |
| target_coverage_conservative_fv | `v28_frozen_target_coverage_conservative_fv` | `pass` | `2026-05-06T03:26:44.025585+00:00` | `False` | none |
| target_coverage_p70_fv | `v28_frozen_target_coverage_p70_fv` | `pass` | `2026-05-06T03:45:32.798460+00:00` | `False` | none |
| target_coverage_p70_empirical_bayes | `v28_frozen_target_coverage_p70_empirical_bayes` | `pass` | `2026-05-06T04:22:07.414318+00:00` | `False` | none |
| boundary_temperature_fv | `v28_frozen_boundary_temperature_fv` | `watch` | `2026-05-06T11:12:06.081553+00:00` | `False` | report_has_scored_rows |
| boundary_energy_fv_entry | `v28_frozen_boundary_energy_fv_entry` | `watch` | `2026-05-06T11:19:55.494948+00:00` | `False` | report_has_scored_rows |
| early_no_boundary_fv_entry | `v28_frozen_early_no_boundary_fv_entry` | `watch` | `2026-05-06T11:24:55.409912+00:00` | `False` | report_has_scored_rows |
| path_state_p70_fv | `v28_frozen_path_state_p70_fv` | `pass` | `2026-05-06T05:07:19.935392+00:00` | `False` | none |
| boundary_recross_shrink_fv | `v28_frozen_boundary_recross_shrink_fv` | `pass` | `2026-05-06T05:29:47.434585+00:00` | `False` | none |
| mid_edge_false_conviction_fv | `v28_frozen_mid_edge_false_conviction_fv` | `pass` | `2026-05-06T09:29:25.082774+00:00` | `False` | none |
| boundary_clock_fv_overlay | `v28_frozen_boundary_clock_fv_overlay` | `watch` | `2026-05-06T07:18:17.705020+00:00` | `False` | report_has_scored_rows |
| boundary_clock_residual_registry | `v28_frozen_boundary_clock_residual_registry` | `pass` | `2026-05-06T07:28:09.623811+00:00` | `False` | none |
| side_asymmetry_registry | `v28_frozen_side_asymmetry_registry` | `pass` | `2026-05-06T07:47:04.735626+00:00` | `False` | none |
| side_asymmetry_fv_overlay | `v28_frozen_side_asymmetry_fv_overlay` | `watch` | `2026-05-06T07:52:22.405861+00:00` | `False` | report_has_scored_rows |
| edge_phase_shrink_fv | `v28_frozen_edge_phase_shrink_fv` | `pass` | `2026-05-06T05:40:31.466696+00:00` | `False` | none |
| edge_phase_edge_gate | `v28_frozen_edge_phase_edge_gate` | `watch` | `2026-05-06T05:46:47.707629+00:00` | `False` | report_has_scored_rows |
| edge_gate_opposite_side | `v28_frozen_edge_gate_opposite_side` | `watch` | `2026-05-06T06:05:34.391059+00:00` | `False` | report_has_scored_rows |
| exit_reduce_suppression | `v28_frozen_exit_reduce_suppression` | `pass` | `2026-05-06T06:33:56.987999+00:00` | `False` | none |
| exit_reduce_yes_suppression | `v28_frozen_exit_reduce_yes_suppression` | `pass` | `2026-05-06T11:04:54.847536+00:00` | `False` | none |
| exit_book_gap_suppression | `v28_frozen_exit_book_gap_suppression` | `pass` | `2026-05-06T08:46:39.207330+00:00` | `False` | none |
| target_coverage_p70_quality_registry | `v28_frozen_target_coverage_p70_quality_registry` | `pass` | `2026-05-06T04:32:03.738730+00:00` | `False` | none |
| live_p70_quality_registry | `v28_live_p70_quality_registry` | `pass` | `2026-05-06T04:49:26.047798+00:00` | `False` | none |
| live_collapse_reentry_registry | `v28_live_collapse_reentry_registry` | `pass` | `2026-05-06T04:56:06.196433+00:00` | `False` | none |
| thin_recross_midp_entry_gate | `v28_frozen_thin_recross_midp_entry_gate` | `watch` | `2026-05-06T03:39:03.842700+00:00` | `False` | report_has_scored_rows |
| raw_p52_boundary_turbulence_skip | `v28_frozen_raw_p52_boundary_turbulence_skip` | `watch` | `2026-05-06T08:50:27.891448+00:00` | `False` | report_has_scored_rows |
| target_loss_tag_repair_entry | `v28_frozen_target_loss_tag_repair_entry` | `watch` | `2026-05-06T08:59:17.610337+00:00` | `False` | report_has_scored_rows |
| low_recross_repair_entry | `v28_frozen_low_recross_repair_entry` | `watch` | `2026-05-06T06:55:26.848310+00:00` | `False` | report_has_scored_rows |
| early_no_boundary_decay_repair_entry | `v28_frozen_early_no_boundary_decay_repair_entry` | `watch` | `2026-05-06T09:10:09.146392+00:00` | `False` | report_has_scored_rows |
| mid_edge_boundary_deception_repair_entry | `v28_frozen_mid_edge_boundary_deception_repair_entry` | `watch` | `2026-05-06T09:23:03.299714+00:00` | `False` | report_has_scored_rows |
| high_raw_p_repair_entry | `v28_frozen_high_raw_p_repair_entry` | `watch` | `2026-05-06T07:59:24.730118+00:00` | `False` | report_has_scored_rows |
| p50_book_edge_entry | `v28_frozen_p50_book_edge_entry` | `pass` | `2026-05-06T08:09:01.165913+00:00` | `False` | none |
| book_plus05_entry | `v28_frozen_book_plus05_entry` | `pass` | `2026-05-06T08:12:48.716932+00:00` | `False` | none |
| book_plus05_no_cheap_yes_entry | `v28_frozen_book_plus05_no_cheap_yes_entry` | `pass` | `2026-05-06T08:24:46.840351+00:00` | `False` | none |
| book_edge_fv_calibration | `v28_frozen_book_edge_fv_calibration` | `watch` | `2026-05-06T08:12:48.716932+00:00` | `False` | report_has_scored_rows |
| recross_book_shrink_fv | `v28_frozen_recross_book_shrink_fv` | `pass` | `2026-05-06T08:42:25.757266+00:00` | `False` | none |
| boundary_clock_repair_entry | `v28_frozen_boundary_clock_repair_entry` | `watch` | `2026-05-06T07:07:27.790042+00:00` | `False` | report_has_scored_rows |
| boundary_clock_fv_entry_bridge | `v28_frozen_boundary_clock_fv_entry_bridge` | `watch` | `2026-05-06T07:35:02.597585+00:00` | `False` | report_has_scored_rows |
| book_trajectory_fv | `v28_frozen_book_trajectory_fv` | `watch` | `2026-05-06T02:47:06.099693+00:00` | `False` | report_has_scored_rows |
| weak_reversal_residual_repair | `v28_frozen_weak_reversal_residual_repair` | `watch` | `2026-05-06T10:25:15.561162+00:00` | `False` | report_has_scored_rows |
| weak_reversal_residual_fv_shrink | `v28_frozen_weak_reversal_residual_fv_shrink` | `watch` | `2026-05-06T10:29:42.136727+00:00` | `False` | report_has_scored_rows |
| no_mid_edge_fv | `v28_frozen_no_mid_edge_fv` | `watch` | `2026-05-06T10:33:21.044716+00:00` | `False` | report_has_scored_rows |
| early_boundary_wait_repair | `v28_frozen_early_boundary_wait_repair` | `watch` | `2026-05-06T10:48:07.385138+00:00` | `False` | report_has_scored_rows |
| early_boundary_opposite_wait_repair | `v28_frozen_early_boundary_opposite_wait_repair` | `watch` | `2026-05-06T10:53:40.348250+00:00` | `False` | report_has_scored_rows |
| gamma_repair_entry | `v28_frozen_gamma_repair_entry` | `watch` | `2026-05-06T11:43:09.046274+00:00` | `False` | report_has_scored_rows |
| raw_entry_coverage_valve | `v28_raw_entry_coverage_valve` | `watch` | `2026-05-05T23:30:17.615882+00:00` | `True` | none |
| raw_p52_favorite_valley_skip | `v28_frozen_raw_p52_favorite_valley_skip` | `watch` | `2026-05-06T11:52:57.665782+00:00` | `False` | report_has_scored_rows |
| raw_p52_mid_edge_skip | `v28_frozen_raw_p52_mid_edge_skip` | `watch` | `2026-05-06T11:57:26.075880+00:00` | `False` | report_has_scored_rows |
| raw_p52_shadow_mid_edge_skip | `v28_frozen_raw_p52_shadow_mid_edge_skip` | `watch` | `2026-05-06T11:58:59.805901+00:00` | `False` | report_has_scored_rows |
| raw_p52_book_disagreement_skip | `v28_frozen_raw_p52_book_disagreement_skip` | `watch` | `2026-05-06T12:06:41.849306+00:00` | `False` | report_has_scored_rows |
| raw_p52_book_shrink_entry | `v28_frozen_raw_p52_book_shrink_entry` | `watch` | `2026-05-06T12:12:25.258308+00:00` | `False` | report_has_scored_rows |
| raw_p52_early_no_boundary_skip | `v28_frozen_raw_p52_early_no_boundary_skip` | `watch` | `2026-05-06T12:18:20.259368+00:00` | `False` | report_has_scored_rows |
| raw_p52_early_no_boundary_band_skip | `v28_frozen_raw_p52_early_no_boundary_band_skip` | `watch` | `2026-05-06T12:20:19.153557+00:00` | `False` | report_has_scored_rows |
| live_readiness | `v28_live_trade_readiness` | `pass` | `2026-05-05T22:07:37.064896+00:00` | `False` | none |

## Interpretation

- Pass means the artifact has a frozen state/report relationship suitable for continued forward monitoring.
- Watch means the artifact is diagnostic or dynamic-ranked and should not be treated as promotion evidence by itself.
- Fail means a report/state mismatch or missing freeze metadata needs attention before relying on the artifact.

## Notes

- `v28_target_coverage_fv_overlay_validator`: Current best target-coverage FV candidate; should remain fixed while forward rows accumulate.
- `v28_frozen_raw_entry_calibrated_probability`: Frozen FV overlays on the broad raw-v28 p50 entry surface.
- `v28_boundary_memory_fv_candidates`: Catastrophic-forgetting boundary-memory candidate; valid only as post-freeze evidence.
- `v28_reward_memory_fv_candidates`: Constrained reward-memory controller; controller weights must be frozen before forward scoring.
- `v28_frozen_book_exact_entry_gate`: Frozen book-exact entry gate; validates whether full FV collapse to book probability has forward edge rather than historical book-favorite luck.
- `v28_frozen_approved_entry_state_valve`: Frozen actual-approved same-side reentry valve; validates state/entry physics without rejected-row simulation.
- `v28_frozen_approved_entry_book_fv`: Frozen actual-approved FV calibration challenger; tests whether book probability remains better calibrated than raw v28 on future approved entries.
- `v28_frozen_danger_zone_entry_valve`: Frozen actual-approved danger-zone valve; validates raw/book overconfidence and same-side reentry risk on post-freeze v28 entries.
- `v28_frozen_danger_zone_fv_calibration`: Frozen actual-approved probability overlays for the danger-zone raw/book disagreement signal.
- `v28_frozen_danger_zone_robustness`: Frozen-only robustness check for danger-zone FV/entry lift; detects single-row future dependence.
- `v28_frozen_target_coverage_conservative_fv`: Frozen conservative target-coverage FV challenger; validates calm-mid-or-high-conviction sharpening on future rows only.
- `v28_frozen_target_coverage_p70_fv`: Frozen target-coverage p70 FV challenger; validates high-confidence-only sharpening on future rows only.
- `v28_frozen_target_coverage_p70_empirical_bayes`: Frozen empirical-Bayes p70 FV challenger; validates evidence-weighted high-confidence sharpening on future rows only.
- `v28_frozen_boundary_temperature_fv`: Frozen continuous boundary-temperature FV challenger; validates recross-heat deconfidence on future target-coverage rows.
- `v28_frozen_boundary_energy_fv_entry`: Frozen boundary-energy FV entry bridge; validates path-energy deconfidence under the unchanged target policy on future rows.
- `v28_frozen_early_no_boundary_fv_entry`: Frozen early-NO boundary FV entry bridge; validates side-asymmetric path-decay deconfidence on future rows.
- `v28_frozen_path_state_p70_fv`: Frozen path/state p70 FV challenger; sharpens only high-confidence rows with strong confirmation energy.
- `v28_frozen_boundary_recross_shrink_fv`: Frozen boundary/recross FV shrink; validates shallow high-recross confidence decay on future rows only.
- `v28_frozen_mid_edge_false_conviction_fv`: Frozen FV shrink; validates early high-recross 4-8pp edge false-conviction confidence decay on future rows only.
- `v28_frozen_boundary_clock_fv_overlay`: Frozen boundary-clock FV overlay; validates p=50 collapse for unresolved boundary-clock hazard rows on future rows only.
- `v28_frozen_boundary_clock_residual_registry`: Frozen residual registry after boundary-clock correction; watches mid-confidence NO-side boundary hesitation before any new FV knob is considered.
- `v28_frozen_side_asymmetry_registry`: Frozen side-asymmetry registry; watches NO p60-70 mid-boundary mid-recross rows before any asymmetric FV penalty is considered.
- `v28_frozen_side_asymmetry_fv_overlay`: Frozen combined boundary-clock plus side-asymmetry FV overlay; validates coin-flip collapse on future rows only.
- `v28_frozen_edge_phase_shrink_fv`: Frozen edge-phase FV shrink; validates phase-aware boundary confidence decay on future rows only.
- `v28_frozen_edge_phase_edge_gate`: Frozen adjusted-FV paid-price safety valve; validates rare extreme negative edge-phase disagreement on future rows only.
- `v28_frozen_edge_gate_opposite_side`: Frozen opposite-side replacement for edge-gate skips; validates whether bad paid-price rows can preserve coverage via coherent same-or-later opposite entries.
- `v28_frozen_exit_reduce_suppression`: Frozen exit-policy challenger; validates suppressing probability_reduce only when held-side probability remains >=75%.
- `v28_frozen_exit_reduce_yes_suppression`: Frozen exit-policy challenger; validates the side-asymmetric YES-only interpretation of probability_reduce suppression on future rows.
- `v28_frozen_exit_book_gap_suppression`: Frozen soft-exit book-gap challenger; validates suppressing spread/turbulence exits while keeping collapse exits intact.
- `v28_frozen_target_coverage_p70_quality_registry`: Frozen p70 quality-tag registry; validates physical high-confidence tags on future rows before any tag-conditioned model is considered.
- `v28_live_p70_quality_registry`: Future-only live v28 p70 quality registry; validates physical live high-confidence tags before any live candidate gets promoted.
- `v28_live_collapse_reentry_registry`: Future-only live registry for same-market reentries after probability-collapse exits; tests whether collapse should penalize FV confidence.
- `v28_frozen_thin_recross_midp_entry_gate`: Frozen entry gate for thin-edge high-recross mid-p rows; validates a narrow turbulence skip on future rows only.
- `v28_frozen_raw_p52_boundary_turbulence_skip`: Frozen raw-p52 boundary-turbulence skip; validates weak raw near-strike high-recross rows on future rows only.
- `v28_frozen_target_loss_tag_repair_entry`: Frozen target-loss tag repair candidate; skips weak-boundary and paid-thin-edge rows, then repairs coverage from low-recross clean rows.
- `v28_frozen_low_recross_repair_entry`: Frozen target-coverage repair candidate; skips paid/weak-boundary danger rows and repairs coverage with lowest-recross clean rows.
- `v28_frozen_early_no_boundary_decay_repair_entry`: Frozen target-coverage repair candidate; skips early NO boundary-decay and cheap boundary-turbulence rows, then repairs coverage with calmer geometry.
- `v28_frozen_mid_edge_boundary_deception_repair_entry`: Frozen target-coverage repair candidate; skips early high-recross 4-8pp edge rows that look like boundary false-conviction.
- `v28_frozen_high_raw_p_repair_entry`: Frozen target-coverage repair candidate; skips paid/weak-boundary danger rows and repairs coverage with highest raw-p clean rows.
- `v28_frozen_p50_book_edge_entry`: Frozen closest broad book-edge entry lane; validates p50, book-plus-5pp, nonnegative-edge rule on future rows only.
- `v28_frozen_book_plus05_entry`: Frozen broad book-plus-5pp entry lane; validates book-disagreement edge on future rows only.
- `v28_frozen_book_plus05_no_cheap_yes_entry`: Frozen broad book-plus-5pp entry lane with cheap-YES boundary-pull rows removed; validates whether the boundary-pull filter preserves broad coverage and improves PnL on future rows only.
- `v28_frozen_book_edge_fv_calibration`: Companion FV calibration report for frozen book-edge entry lanes; compares raw, book, and predeclared blends on future rows only.
- `v28_frozen_recross_book_shrink_fv`: Frozen recross/book-disagreement FV shrinkage challenger; validates future-only book anchoring in unstable path geometry.
- `v28_frozen_boundary_clock_repair_entry`: Frozen target-coverage repair candidate; skips boundary-clock hazard rows and repairs coverage with lowest-recross clean rows.
- `v28_frozen_boundary_clock_fv_entry_bridge`: Frozen entry bridge from boundary-clock adjusted FV; validates adjusted-edge skip plus low-recross repair on future rows only.
- `v28_frozen_book_trajectory_fv`: Frozen book-trajectory FV shrinkage candidate; validates fixed physics thresholds on post-freeze observations.
- `v28_frozen_weak_reversal_residual_repair`: Frozen entry repair candidate for weak-boundary reversal plus NO-side 5-8pp residual rows.
- `v28_frozen_weak_reversal_residual_fv_shrink`: Frozen calibration validator for half-to-50 residual shrink after weak-boundary reversal.
- `v28_frozen_no_mid_edge_fv`: Frozen broader NO 5-8pp book-anchor FV shrink; validates whether mid-edge NO conviction is overconfident out of sample.
- `v28_frozen_early_boundary_wait_repair`: Frozen early-boundary wait/repair candidate; validates whether very early high-recross boundary states should be aged before entry.
- `v28_frozen_early_boundary_opposite_wait_repair`: Frozen early-boundary opposite-side wait/repair candidate; validates whether the first boundary thesis should be reversed after clock decay.
- `v28_frozen_gamma_repair_entry`: Frozen gamma/recross repair bridge; tests whether cheap near-boundary optionality can repair target coverage without broad exposure.
- `v28_raw_entry_coverage_valve`: Coverage-valve artifact can rank rows, but downstream target FV must freeze the chosen policy before promotion evidence.
- `v28_frozen_raw_p52_favorite_valley_skip`: Frozen raw-p52 payoff-geometry challenger; validates whether skipping the 65-75c middle-favorite valley preserves target coverage while improving EV.
- `v28_frozen_raw_p52_mid_edge_skip`: Frozen raw-p52 false-conviction challenger; validates whether skipping the whole 5-10pp edge band improves EV without unacceptable coverage loss.
- `v28_frozen_raw_p52_shadow_mid_edge_skip`: Frozen raw-p52 expansion-surface challenger; preserves approved-entry rows and validates whether rejected-actionable 5-10pp edge rows are false-conviction traps.
- `v28_frozen_raw_p52_book_disagreement_skip`: Frozen raw-p52 crowd-prior challenger; validates whether large selected-side FV disagreement above executable book marks overconfidence.
- `v28_frozen_raw_p52_book_shrink_entry`: Frozen raw-p52 probabilistic crowd-prior shrink challenger for large selected-side FV disagreement above executable book.
- `v28_frozen_raw_p52_early_no_boundary_skip`: Frozen raw-p52 early NO boundary-decay skip; broad physics check that is likely too selective.
- `v28_frozen_raw_p52_early_no_boundary_band_skip`: Frozen raw-p52 middle-confidence early NO boundary skip; preserves target coverage in discovery while testing recross/path fragility.
- `v28_live_trade_readiness`: Gate artifact; does not itself create candidates, but must not promote anything while evidence blockers remain.
