# Fixed Terminal OOS Report

- hypothesis_id: gaussian_vol45_terminal_v1
- variant_name: gaussian_vol45
- evaluation_scope: locked_oos_shadow
- candidate_count: 2514
- source_candidate_count: 2514
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- market_count: 4
- selected_count: 2330
- total_counterfactual_pnl_cents: 47330.0000
- avg_counterfactual_pnl_cents_per_selected: 20.313305
- brier: 0.239468
- log_loss: 0.654227
- ev_rank_correlation_sign: 0.112001
- top_ev_bucket_pnl_cents: 20.5914
- beats_brownian: False
- beats_market: True
- beats_current_calibrated: True
- static_particle_pnl_cents: 50400.0000
- current_calibrated_pnl_cents: -6737.0000
- promotion_safe: False
- note: Fixed terminal OOS reports are promotion-safe only when the hypothesis and gates were locked before capture, the evaluation scope is locked_oos_shadow, and every gate passes. This remains research-only and must not touch live trading.

## Gate Results

- enough_candidates: True
- enough_markets: False
- enough_selected: True
- positive_total_pnl: True
- positive_avg_pnl: True
- positive_ev_rank: True
- positive_top_ev_bucket: True
- beats_brownian_probability: False
- beats_market_probability: True
- beats_current_probability: True
- beats_static_particle_pnl: False
- beats_current_calibrated_pnl: True
- locked_oos_scope: True
- all_passed: False
