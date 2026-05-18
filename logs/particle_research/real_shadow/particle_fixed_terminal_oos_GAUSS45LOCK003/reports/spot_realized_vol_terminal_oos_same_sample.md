# Spot Realized-Vol Terminal OOS Report

- hypothesis_id: rv233_blend50_fixed65_terminal_v1
- variant_name: rv233_blend50_fixed65
- evaluation_scope: same_sample_diagnostic
- candidate_count: 4405
- source_candidate_count: 4405
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- market_count: 6
- spot_tick_count: 35848
- fallback_row_count: 557
- mean_annualized_vol: 0.256983
- selected_count: 3989
- total_counterfactual_pnl_cents: -9896.0000
- avg_counterfactual_pnl_cents_per_selected: -2.480822
- brier: 0.176837
- log_loss: 0.525552
- ev_rank_correlation_sign: -0.128930
- top_ev_bucket_pnl_cents: -13.7613
- beats_brownian: True
- beats_market: False
- beats_current_calibrated: False
- static_particle_pnl_cents: -7134.0000
- current_calibrated_pnl_cents: -30603.0000
- promotion_safe: False
- note: Spot realized-vol terminal OOS reports are promotion-safe only when the hypothesis and gates were locked before capture, the spot ticks are timestamp-available at decision time, the evaluation scope is locked_oos_shadow, and every gate passes. This is research-only and must not touch live trading.

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
- locked_oos_scope: False
- all_passed: False
