# Side Consensus OOS Report

- hypothesis_id: skip_against_market_current_consensus_10_v1
- evaluation_scope: same_sample_diagnostic
- candidate_count: 663
- source_candidate_count: 663
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- market_count: 2
- base_selected_count: 649
- base_total_counterfactual_pnl_cents: -4638.0000
- consensus_selected_count: 183
- consensus_total_counterfactual_pnl_cents: 356.0000
- consensus_avg_counterfactual_pnl_cents_per_selected: 1.9454
- consensus_win_rate: 0.4426
- blocked_against_consensus_count: 466
- blocked_against_consensus_counterfactual_pnl_cents: -4994.0000
- blocked_against_consensus_loss_avoided_cents: 4994.0000
- consensus_ev_rank_correlation_sign: 0.261163
- consensus_top_ev_bucket_pnl_cents: -15.2174
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
- locked_oos_scope: False
- all_passed: False

## Gate Config

- min_candidate_count: 500
- min_market_count: 2
- min_selected_count: 100
- min_total_pnl_cents: 1.0
- min_avg_pnl_per_selected_cents: 0.01
- consensus_min_confidence: 0.1
- require_positive_ev_rank: True
- require_positive_top_ev_bucket: True
- require_beats_base_pnl: True
