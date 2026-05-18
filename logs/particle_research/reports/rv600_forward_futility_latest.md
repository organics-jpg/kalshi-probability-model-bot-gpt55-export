# RV600 Forward Futility Probe

- generated_utc: 2026-05-15T21:22:01+00:00
- research_only: True
- decision: reject_current_locked_family_for_promotion
- reasons: forward_locked_selected_pnl_nonpositive, forward_locked_avg_entry_negative, does_not_beat_matched_v28_on_forward_timestamps, prequential_locked_gate_selection_count_zero, bootstrap_predictive_success_probability_below_threshold

## Current Locked Family

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting_mode: `one_per_side_per_market`
- accepted_entries: 15
- distinct_markets: 15
- selected_pnl_cents: -155.3
- avg_pnl_per_entry_cents: -10.353
- matched_v28_delta_cents: -7.1

## Recovery Math

- target_entries: 100
- target_markets: 40
- target_total_pnl_cents: 1000.0
- remaining_entries_to_target: 85
- remaining_markets_to_target: 25
- required_remaining_avg_pnl_per_entry_cents: 13.592
- required_remaining_avg_to_positive_cents: 1.827

## Native And Prequential Evidence

- native_roots: 1
- native_settled_markets: 1
- native_candidate_rows: 812
- native_locked_total_entries: 14
- native_locked_total_pnl_cents: 1167.0
- prequential_split_count: 20
- prequential_locked_gate_selection_count: 0
- prequential_test_selected_pnl_cents: -394.0

## Bootstrap Predictive Check

- iterations: 20000
- usable_root_blocks: 14
- success_probability: 0.0000
- median_final_pnl_cents: -1043.5
- p90_final_pnl_cents: -786.7
- success_definition: final entries >= target, markets >= target, selected PnL >= target_entries * target_avg_entry_cents, avg entry >= target, and matched-v28 delta > 0

## Method Choice

Chosen method: pre-specified interim futility check with recovery math and bootstrap predictive probability.

Options considered:

- Bayesian predictive-probability futility: best fit for an interim stop/continue decision.
- Sequential probability ratio testing: useful for binary win-rate tests, but less aligned with fee-adjusted PnL targets.
- Deflated Sharpe ratio: useful for multiple tested strategies, but current blocker is one locked family in live-forward shadow.
- CSCV / probability of backtest overfitting: useful for retrospective grid selection risk, already addressed by prequential reports.
- White reality-check style multiple-testing control: useful before selecting a new grid winner, not needed to reject this frozen family.

References:

- FDA guidance, Bayesian statistics in medical device clinical trials: predictive probability and interim planning.
- Wald sequential probability ratio test: classic sequential decision framing.
- Bailey and Lopez de Prado, Deflated Sharpe Ratio.
- Bailey, Borwein, Lopez de Prado, and Zhu, Probability of Backtest Overfitting.
- White, A Reality Check for Data Snooping.

## Interpretation

The current locked family should be rejected for promotion and should not keep consuming forward-shadow collection by itself.
RV600 work can continue only by formally freezing a new candidate from existing evidence, then subjecting that new candidate to the same forward gates.
