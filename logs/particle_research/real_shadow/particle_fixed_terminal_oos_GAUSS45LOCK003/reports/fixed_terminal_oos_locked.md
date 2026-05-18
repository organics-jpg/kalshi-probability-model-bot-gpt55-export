# Fixed Terminal OOS Report

- hypothesis_id: gaussian_vol45_terminal_v1
- variant_name: gaussian_vol45
- evaluation_scope: locked_oos_shadow
- candidate_count: 4405
- source_candidate_count: 4405
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- market_count: 6
- selected_count: 4221
- total_counterfactual_pnl_cents: -7258.0000
- avg_counterfactual_pnl_cents_per_selected: -1.719498
- brier: 0.178926
- log_loss: 0.533517
- ev_rank_correlation_sign: -0.031596
- top_ev_bucket_pnl_cents: -14.1824
- beats_brownian: True
- beats_market: False
- beats_current_calibrated: False
- static_particle_pnl_cents: -7134.0000
- current_calibrated_pnl_cents: -30603.0000
- promotion_safe: False
- note: Fixed terminal OOS reports are promotion-safe only when the hypothesis and gates were locked before capture, the evaluation scope is locked_oos_shadow, and every gate passes. This remains research-only and must not touch live trading.

## Gate Results

- enough_candidates: True
- enough_markets: True
- enough_selected: True
- positive_total_pnl: False
- positive_avg_pnl: False
- positive_ev_rank: False
- positive_top_ev_bucket: False
- beats_brownian_probability: True
- beats_market_probability: False
- beats_current_probability: False
- beats_static_particle_pnl: False
- beats_current_calibrated_pnl: True
- locked_oos_scope: True
- all_passed: False
