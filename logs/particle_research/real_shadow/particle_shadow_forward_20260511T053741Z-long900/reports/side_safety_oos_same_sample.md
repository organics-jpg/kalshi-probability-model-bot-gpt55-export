# Side Safety OOS Report

- hypothesis_id: side_safe_yes_only_v1
- evaluation_scope: same_sample_diagnostic
- candidate_count: 753
- source_candidate_count: 753
- skipped_unlabeled_count: 0
- denominator_scope: all_labeled_candidates
- market_count: 2
- base_selected_count: 676
- base_total_counterfactual_pnl_cents: -4876.0000
- side_safe_selected_count: 434
- side_safe_total_counterfactual_pnl_cents: 4193.0000
- side_safe_avg_counterfactual_pnl_cents_per_selected: 9.6613
- side_safe_win_rate: 0.2327
- blocked_no_count: 242
- blocked_no_counterfactual_pnl_cents: -9069.0000
- blocked_no_loss_avoided_cents: 9069.0000
- side_safe_ev_rank_correlation_sign: -0.522630
- side_safe_top_ev_bucket_pnl_cents: -4.3486
- promotion_safe: False
- note: side_safe_yes_only_v1 is a predeclared OOS hypothesis derived from prior same-sample diagnostics. Same-sample reports must not be used for promotion. Locked OOS/shadow reports are still research-only and cannot affect live trading until all project promotion gates pass.

## Gate Results

- enough_candidates: True
- enough_markets: False
- enough_selected: True
- positive_total_pnl: True
- positive_avg_pnl: True
- positive_ev_rank: False
- positive_top_ev_bucket: False
- beats_base_pnl: True
- locked_oos_scope: False
- all_passed: False

## Gate Config

- min_candidate_count: 500
- min_market_count: 4
- min_selected_count: 100
- min_total_pnl_cents: 1.0
- min_avg_pnl_per_selected_cents: 0.01
- require_positive_ev_rank: True
- require_positive_top_ev_bucket: True
- require_beats_base_pnl: True
