# RV600 Probability Calibration Rescue Probe

- generated_utc: 2026-05-15T21:05:16+00:00
- research_only: True
- method_choice: Low-complexity probability calibration over RV600 with anchored prequential strategy selection.
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
| `platt_scaling` | chosen_as_grid_platt | [Platt 1999, Probabilistic Outputs for Support Vector Machines](https://www.researchgate.net/publication/2594015_Probabilistic_Outputs_for_Support_Vector_Machines_and_Comparisons_to_Regularized_Likelihood_Methods) | Small parametric logit recalibration; feasible with little data if selected only from prior roots. |
| `temperature_scaling` | chosen_as_fixed_candidates | [Guo et al. 2017, On Calibration of Modern Neural Networks](https://arxiv.org/abs/1706.04599) | One-parameter confidence scaling; useful as a low-complexity RV600 shrink/expand check. |
| `isotonic_calibration` | deferred | [Niculescu-Mizil and Caruana 2005, Predicting Good Probabilities with Supervised Learning](https://icml.cc/Conferences/2005/proceedings/papers/079_GoodProbabilities_NiculescuMizilCaruana.pdf) | Flexible but too easy to overfit with the current small number of settled markets. |
| `venn_abers` | deferred | [Vovk and Petej 2012, Venn-Abers predictors](https://arxiv.org/abs/1211.0025) | Attractive calibration intervals, but assumes a larger calibration set than the current forward market count. |

## Split Rows

| split | selected calibration | selected strategy | basis | test root | entries | pnl_c | v28_delta_c |
|---:|---|---|---|---|---:|---:|---:|

## Method Notes

This is a research-only calibration rescue attempt. Each split fits or selects calibration parameters using prior roots only, then tests the selected calibration and RV600 entry rule on the next root.
Diagnostic selections are not promotable unless the prior-root window already passed anti-overfitting gates.
