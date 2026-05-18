# RV600 Meta-Label Rescue Probe

- generated_utc: 2026-05-15T21:05:15+00:00
- research_only: True
- method_choice: Meta-label style one-feature filter over the RV600 primary signal with anchored prequential selection.
- usable_roots: 1
- filter_count: 35
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
| `meta_label_filter` | chosen | [Joubert 2022, Meta-Labeling: Theory and Framework](https://ssrn.com/abstract=4032018) | Best fit: preserves RV600 as the primary signal and learns only whether to accept or suppress a candidate. |
| `conformal_time_series_abstention` | deferred | [Xu and Xie 2020/2023, Conformal prediction for time series](https://arxiv.org/abs/2010.09107) | Useful for uncertainty bands, but current labels are sparse settled trade outcomes rather than a long residual stream. |
| `sequential_conformal_inference` | deferred | [Xu and Xie 2022, Sequential Predictive Conformal Inference for Time Series](https://arxiv.org/abs/2212.03463) | Handles non-exchangeable time series, but needs a larger sequential residual history than the current RV600 sample. |
| `post_hoc_probability_calibration` | deferred | [Guo et al. 2017, On Calibration of Modern Neural Networks](https://arxiv.org/abs/1706.04599) | Can improve probability reliability, but the immediate blocker is trade acceptance/profitability after fees and fills. |
| `online_expert_weighting` | deferred | [Freund and Schapire 1997, A Decision-Theoretic Generalization of On-Line Learning](https://doi.org/10.1006/jcss.1997.1504) | Plausible for adapting among candidate families, but every existing family is already rejected and the sample is too small. |

## Split Rows

| split | selected filter | basis | test root | entries | pnl_c | v28_delta_c |
|---:|---|---|---|---:|---:|---:|

## Method Notes

This is a research-only meta-labeling rescue attempt: RV600 remains the primary signal, while a one-feature filter is selected from prior roots only and tested on the next root.
Diagnostic selections are reported for visibility but are not promotable unless a prior-root training window already passed the same anti-overfitting gates.

References: Lopez de Prado style meta-labeling, sequential/prequential validation, and the existing RV600 anti-overfitting gates.
