# Fixed Terminal OOS Report

- hypothesis_id: gaussian_vol45_terminal_v1
- variant_name: gaussian_vol45
- evaluation_scope: locked_oos_shadow
- candidate_count: 4843
- source_candidate_count: 4843
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- market_count: 7
- selected_count: 4378
- total_counterfactual_pnl_cents: 49703.0000
- avg_counterfactual_pnl_cents_per_selected: 11.352901
- brier: 0.246083
- log_loss: 0.694486
- ev_rank_correlation_sign: 0.117524
- top_ev_bucket_pnl_cents: 13.0603
- beats_brownian: False
- beats_market: True
- beats_current_calibrated: True
- static_particle_pnl_cents: 47336.0000
- current_calibrated_pnl_cents: -33331.0000
- promotion_safe: False
- note: Fixed terminal OOS reports are promotion-safe only when the hypothesis and gates were locked before capture, the evaluation scope is locked_oos_shadow, and every gate passes. This remains research-only and must not touch live trading.

## Gate Results

- enough_candidates: True
- enough_markets: True
- enough_selected: True
- positive_total_pnl: True
- positive_avg_pnl: True
- positive_ev_rank: True
- positive_top_ev_bucket: True
- beats_brownian_probability: False
- beats_market_probability: True
- beats_current_probability: True
- beats_static_particle_pnl: True
- beats_current_calibrated_pnl: True
- locked_oos_scope: True
- all_passed: False
