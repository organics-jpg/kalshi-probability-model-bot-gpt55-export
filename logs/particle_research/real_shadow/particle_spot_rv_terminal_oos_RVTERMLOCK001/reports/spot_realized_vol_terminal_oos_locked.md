# Spot Realized-Vol Terminal OOS Report

- hypothesis_id: rv233_blend50_fixed65_terminal_v1
- variant_name: rv233_blend50_fixed65
- evaluation_scope: locked_oos_shadow
- candidate_count: 4512
- source_candidate_count: 4512
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- market_count: 7
- spot_tick_count: 33754
- fallback_row_count: 0
- mean_annualized_vol: 0.200513
- selected_count: 4108
- total_counterfactual_pnl_cents: 17528.0000
- avg_counterfactual_pnl_cents_per_selected: 4.266796
- brier: 0.133252
- log_loss: 0.430335
- ev_rank_correlation_sign: -0.029959
- top_ev_bucket_pnl_cents: -3.3564
- beats_brownian: True
- beats_market: False
- beats_current_calibrated: False
- static_particle_pnl_cents: -2384.0000
- current_calibrated_pnl_cents: 28435.0000
- promotion_safe: False
- note: Spot realized-vol terminal OOS reports are promotion-safe only when the hypothesis and gates were locked before capture, the spot ticks are timestamp-available at decision time, the evaluation scope is locked_oos_shadow, and every gate passes. This is research-only and must not touch live trading.

## Gate Results

- enough_candidates: True
- enough_markets: True
- enough_selected: True
- positive_total_pnl: True
- positive_avg_pnl: True
- positive_ev_rank: False
- positive_top_ev_bucket: False
- beats_brownian_probability: True
- beats_market_probability: False
- beats_current_probability: False
- beats_static_particle_pnl: True
- beats_current_calibrated_pnl: False
- locked_oos_scope: True
- all_passed: False
