# Residual Blend OOS Report

- hypothesis_id: resid_current_rv300n20_rv600p20_particle_n10_v1
- coefficient: resid_mp00_r300n02_r600p02_pn01
- evaluation_scope: locked_oos_shadow
- candidate_count: 3358
- source_candidate_count: 3358
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- market_count: 5
- selected_count: 2448
- total_counterfactual_pnl_cents: -28864.0000
- avg_counterfactual_pnl_cents_per_selected: -11.7908
- brier: 0.244988
- log_loss: 0.660681
- ev_rank_correlation_sign: -0.060806
- top_ev_bucket_pnl_cents: -9.2202
- static_particle_pnl_cents: 60332.0000
- current_calibrated_pnl_cents: -24387.0000
- promotion_safe: False
- note: Residual blend OOS reports are promotion-safe only when this exact coefficient and all gates were locked before capture, the scope is locked_oos_shadow, and every gate passes. Same-sample reports are research direction only.

## Coefficients

- market_residual: 0
- rv300_residual: -0.2
- rv600_residual: 0.2
- particle_residual: -0.1

## Gate Results

- enough_candidates: True
- enough_markets: True
- enough_selected: True
- positive_total_pnl: False
- positive_avg_pnl: False
- positive_ev_rank: False
- positive_top_ev_bucket: False
- beats_brownian_probability: False
- beats_market_probability: False
- beats_current_probability: False
- beats_static_particle_pnl: False
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
