# RV600 Online Expert Rescue Probe

- generated_utc: 2026-05-15T21:05:25+00:00
- research_only: True
- method_choice: Multiplicative-weights expert selection over existing RV600 plan variants using prior-root rewards only.
- usable_roots: 1
- variant_count: 3948
- expert_count: 3948
- eta: 1.0
- reward_scale_cents: 100.0
- split_count: 0
- train_gate_selection_count: 0
- diagnostic_selection_count: 0
- test_total_entries: 0
- test_selected_pnl_cents: 0.0
- test_matched_v28_delta_cents: 0.0
- preliminary_gate_pass: False
- rejection_reason: no_train_gate_selection;fewer_than_25_test_entries;nonpositive_test_pnl;does_not_beat_matched_v28

## Modeling Choice

| method | decision | source | fit |
|---|---|---|---|
| `multiplicative_weights` | chosen | [Freund and Schapire 1997, A Decision-Theoretic Generalization of On-Line Learning](https://doi.org/10.1006/jcss.1997.1504) | Best fit: choose among existing plan variants online from prior-root rewards without inventing new strategy families. |
| `prediction_with_expert_advice` | chosen_as_validation_frame | [Cesa-Bianchi and Lugosi 2006, Prediction, Learning, and Games](https://doi.org/10.1017/CBO9780511546921) | General framework for sequentially competing with a reference class of experts; used here as an audit framing. |
| `second_order_expert_bounds` | deferred | [Cesa-Bianchi, Mansour, and Stoltz 2006, Improved Second-Order Bounds for Prediction with Expert Advice](https://arxiv.org/abs/math/0602629) | Interesting for payoff scale adaptation, but heavier than needed for the current small root count. |

## Split Rows

| split | selected variant | basis | test root | entries | pnl_c | v28_delta_c |
|---:|---|---|---|---:|---:|---:|

## Method Notes

This is a research-only expert-advice rescue: every expert is an existing RV600-derived plan variant, scored with position-capped accounting. Pure `v28_primary` variants are excluded as controls, not RV600-derived candidates.
Selections are made from prior roots only. If the selected expert did not pass prior-root anti-overfitting gates, its next-root row is diagnostic and not promotable.
