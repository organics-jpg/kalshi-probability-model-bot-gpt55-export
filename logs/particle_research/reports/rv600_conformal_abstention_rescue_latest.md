# RV600 Conformal Abstention Rescue Probe

- generated_utc: 2026-05-15T21:05:21+00:00
- research_only: True
- method_choice: Conformal abstention over RV600 probability using prior-root residual quantiles.
- usable_roots: 1
- strategy_count: 8
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
| `split_conformal_abstention` | chosen | [Xu and Xie 2020/2023, Conformal prediction for time series](https://arxiv.org/abs/2010.09107) | Use prior-root residual quantiles as a conservative RV600 probability error band before accepting EV. |
| `sequential_conformal_inference` | deferred | [Xu and Xie 2022, Sequential Predictive Conformal Inference for Time Series](https://arxiv.org/abs/2212.03463) | More adaptive, but heavier than needed for a first rescue and needs more stable residual history. |
| `meta_label_filter` | previously_rejected | [Joubert 2022, Meta-Labeling: Theory and Framework](https://ssrn.com/abstract=4032018) | Already tested; failed prequential gates on the current RV600 sample. |

## Split Rows

| split | selected conformal | selected strategy | basis | test root | entries | pnl_c | v28_delta_c |
|---:|---|---|---|---|---:|---:|---:|

## Method Notes

This is a research-only abstention check: the prior-root absolute RV600 label error sets a probability band, and trades are accepted only if worst-case EV still clears the strategy threshold.
Diagnostic selections are not promotable unless the prior-root window already passed anti-overfitting gates.
