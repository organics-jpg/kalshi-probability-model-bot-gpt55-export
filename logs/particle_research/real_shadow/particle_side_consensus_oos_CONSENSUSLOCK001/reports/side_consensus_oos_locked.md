# Side Consensus OOS Report

- hypothesis_id: skip_against_market_current_consensus_10_v1
- evaluation_scope: locked_oos_shadow
- candidate_count: 3260
- source_candidate_count: 3260
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- market_count: 6
- base_selected_count: 3029
- base_total_counterfactual_pnl_cents: -32502.0000
- consensus_selected_count: 429
- consensus_total_counterfactual_pnl_cents: 1447.0000
- consensus_avg_counterfactual_pnl_cents_per_selected: 3.3730
- consensus_win_rate: 0.4918
- blocked_against_consensus_count: 2600
- blocked_against_consensus_counterfactual_pnl_cents: -33949.0000
- blocked_against_consensus_loss_avoided_cents: 33949.0000
- consensus_ev_rank_correlation_sign: 0.129008
- consensus_top_ev_bucket_pnl_cents: -6.2407
- promotion_safe: False
- note: skip_against_market_current_consensus_10_v1 is a predeclared selection hypothesis derived from prior diagnostics. Same-sample reports are not promotion evidence. Locked OOS/shadow reports remain research-only and must not affect live trading until the broader particle goal gates pass.

## Gate Results

- enough_candidates: True
- enough_markets: True
- enough_selected: True
- positive_total_pnl: True
- positive_avg_pnl: True
- positive_ev_rank: True
- positive_top_ev_bucket: False
- beats_base_pnl: True
- all_candidate_denominator: True
- locked_oos_scope: True
- all_passed: False

## Gate Config

- min_candidate_count: 1000
- min_market_count: 5
- min_selected_count: 100
- min_total_pnl_cents: 1.0
- min_avg_pnl_per_selected_cents: 0.01
- consensus_min_confidence: 0.1
- require_positive_ev_rank: True
- require_positive_top_ev_bucket: True
- require_beats_base_pnl: True
