# Dynamic Particle OOS Report

- hypothesis_id: rolling_vol_300s_v1
- variant_name: rolling_vol_300s
- evaluation_scope: locked_oos_shadow
- candidate_count: 3501
- source_candidate_count: 3501
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- market_count: 5
- selected_count: 2852
- total_counterfactual_pnl_cents: 32406.0000
- avg_counterfactual_pnl_cents_per_selected: 11.3626
- brier: 0.150814
- log_loss: 0.458110
- ev_rank_correlation_sign: 0.038545
- top_ev_bucket_pnl_cents: 15.7888
- static_particle_pnl_cents: 15798.0000
- current_calibrated_pnl_cents: 32996.0000
- promotion_safe: False
- note: Dynamic rolling-vol particle OOS reports are promotion-safe only when the hypothesis and gates were locked before capture, the evaluation scope is locked_oos_shadow, and every gate passes. Same-sample diagnostics are useful for research direction only.

## Gate Results

- enough_candidates: True
- enough_markets: True
- enough_selected: True
- positive_total_pnl: True
- positive_avg_pnl: True
- positive_ev_rank: True
- positive_top_ev_bucket: True
- beats_brownian_probability: True
- beats_market_probability: True
- beats_current_probability: True
- beats_static_particle_pnl: True
- beats_current_calibrated_pnl: False
- locked_oos_scope: True
- all_passed: False

## Gate Config

- min_candidate_count: 1000
- min_market_count: 5
- min_selected_count: 250
- min_total_pnl_cents: 1.0
- min_avg_pnl_per_selected_cents: 0.01
- require_positive_ev_rank: True
- require_positive_top_ev_bucket: True
- require_beats_brownian_probability: True
- require_beats_market_probability: True
- require_beats_current_probability: True
- require_beats_static_particle_pnl: True
- require_beats_current_calibrated_pnl: True
