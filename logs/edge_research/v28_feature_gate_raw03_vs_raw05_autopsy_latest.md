# v28 Feature-Gate raw03 vs raw05 Autopsy

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T16:02:31.323096+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Refreshed live baseline: `1463.000000c`

## Interpretation

- Autopsy compares strict post-freeze raw03 broad rows to raw05 clean rows.
- post_feature_freeze_entry: raw03 adds 7 market rows versus raw05, marginal net -83.0c with W/L 2/5; raw03 net 288.0c vs raw05 355.0c and live 1463c.
- post_feature_freeze_entry: raw03 source share 0.3620689655172414 needs 3 clean rows; dropping reconstructed losses has blockers ['coverage_too_low_after_drop'].
- post_feature_freeze_bridge: raw03 adds 7 market rows versus raw05, marginal net -15.0c with W/L 2/4; raw03 net 294.0c vs raw05 293.0c and live 1463c.
- post_feature_freeze_bridge: raw03 source share 0.3620689655172414 needs 3 clean rows; dropping reconstructed losses has blockers ['coverage_too_low_after_drop'].

## post_feature_freeze_entry

| candidate | entries | settled | coverage | net c | W/L | recon share | source counts |
|---|---:|---:|---:|---:|---:|---:|---|
| raw05 | 51 | 49 | 67.105263 | 355.000000 | 34/15 | 0.274510 | {'approved_entry': 37, 'rejected_actionable': 14} |
| raw03 | 58 | 56 | 76.315789 | 288.000000 | 36/20 | 0.362069 | {'approved_entry': 37, 'rejected_actionable': 21} |
| raw03 marginal | 7 | 7 | 9.210526 | -83.000000 | 2/5 | 1.000000 | {'rejected_actionable': 7} |

- raw03 source/cushion gap: `{'rows_needed_for_75pct_coverage': 0, 'settled_needed_for_30': 0, 'clean_rows_needed_for_source_gate': 2, 'cents_needed_for_cushion3': 12.0}`
- raw03 clean rows needed for source gate: `3`
- Drop reconstructed losses scenario blockers: `coverage_too_low_after_drop`
- Drop reconstructed losses remaining summary: `{'entries': 56, 'settled': 54, 'wins': 36, 'losses': 18, 'coverage_pct': 73.6842105263158, 'net_cents': 371.0, 'avg_net_cents': 6.87037037037037, 'source_counts': {'approved_entry': 37, 'rejected_actionable': 19}, 'reconstructed_share': 0.3392857142857143, 'feature_tag_counts': {'raw_edge_ge_07': 36, 'low_recross_lte_50': 53, 'strong_abs_d_ge_115': 20, 'ask_ge_65': 39, 'realized_win': 36, 'mid_abs_d_085_115': 33, 'ask_below_65': 17, 'source_quality_risk': 19, 'realized_loss': 18, 'raw_edge_05_07': 15, 'weak_abs_d_075_085': 3, 'thin_raw_edge_03_05': 5, 'moderate_recross_50_60': 3}}`
- Marginal feature tags: `{'thin_raw_edge_03_05': 6, 'low_recross_lte_50': 7, 'strong_abs_d_ge_115': 4, 'ask_below_65': 5, 'source_quality_risk': 7, 'realized_loss': 5, 'ask_ge_65': 2, 'realized_win': 2, 'weak_abs_d_075_085': 2, 'raw_edge_ge_07': 1, 'mid_abs_d_085_115': 1}`

### Worst Marginal Rows

| market | source | side | won | net c | raw edge | recross | abs d | ask | tags |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY070615-15 | rejected_actionable | yes | False | -68.000000 | 0.200931 | 0.253348 | 0.819952 | 0.640000 | raw_edge_ge_07, low_recross_lte_50, weak_abs_d_075_085, ask_below_65, source_quality_risk, realized_loss |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -15.000000 | 0.041601 | 0.132257 | 0.784861 | 0.130000 | thin_raw_edge_03_05, low_recross_lte_50, weak_abs_d_075_085, ask_below_65, source_quality_risk, realized_loss |
| KXBTC15M-26MAY070900-00 | rejected_actionable | no | False | -6.000000 | 0.047205 | 0.073267 | 1.083550 | 0.050000 | thin_raw_edge_03_05, low_recross_lte_50, mid_abs_d_085_115, ask_below_65, source_quality_risk, realized_loss |
| KXBTC15M-26MAY070145-45 | rejected_actionable | yes | False | -3.000000 | 0.043906 | 0.028894 | 1.241798 | 0.020000 | thin_raw_edge_03_05, low_recross_lte_50, strong_abs_d_ge_115, ask_below_65, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061930-30 | rejected_actionable | no | False | -2.000000 | 0.031608 | 0.083294 | 1.513246 | 0.010000 | thin_raw_edge_03_05, low_recross_lte_50, strong_abs_d_ge_115, ask_below_65, source_quality_risk, realized_loss |
| KXBTC15M-26MAY062200-00 | rejected_actionable | no | True | 4.000000 | 0.042204 | 0.026847 | 2.370580 | 0.950000 | thin_raw_edge_03_05, low_recross_lte_50, strong_abs_d_ge_115, ask_ge_65, source_quality_risk, realized_win |
| KXBTC15M-26MAY070530-30 | rejected_actionable | no | True | 7.000000 | 0.047387 | 0.085902 | 1.454914 | 0.910000 | thin_raw_edge_03_05, low_recross_lte_50, strong_abs_d_ge_115, ask_ge_65, source_quality_risk, realized_win |

## post_feature_freeze_bridge

| candidate | entries | settled | coverage | net c | W/L | recon share | source counts |
|---|---:|---:|---:|---:|---:|---:|---|
| raw05 | 51 | 46 | 66.233766 | 293.000000 | 31/15 | 0.274510 | {'approved_entry': 37, 'rejected_actionable': 14} |
| raw03 | 58 | 52 | 75.324675 | 294.000000 | 33/19 | 0.362069 | {'approved_entry': 37, 'rejected_actionable': 21} |
| raw03 marginal | 7 | 6 | 9.090909 | -15.000000 | 2/4 | 1.000000 | {'rejected_actionable': 7} |

- raw03 source/cushion gap: `{'rows_needed_for_75pct_coverage': 0, 'settled_needed_for_30': 0, 'clean_rows_needed_for_source_gate': 2, 'cents_needed_for_cushion3': 6.0}`
- raw03 clean rows needed for source gate: `3`
- Drop reconstructed losses scenario blockers: `coverage_too_low_after_drop`
- Drop reconstructed losses remaining summary: `{'entries': 56, 'settled': 50, 'wins': 33, 'losses': 17, 'coverage_pct': 72.72727272727273, 'net_cents': 320.0, 'avg_net_cents': 6.4, 'source_counts': {'approved_entry': 37, 'rejected_actionable': 19}, 'reconstructed_share': 0.3392857142857143, 'feature_tag_counts': {'raw_edge_ge_07': 36, 'low_recross_lte_50': 53, 'strong_abs_d_ge_115': 20, 'ask_ge_65': 39, 'realized_win': 33, 'mid_abs_d_085_115': 33, 'ask_below_65': 17, 'source_quality_risk': 19, 'realized_loss': 17, 'raw_edge_05_07': 15, 'weak_abs_d_075_085': 3, 'thin_raw_edge_03_05': 5, 'moderate_recross_50_60': 3}}`
- Marginal feature tags: `{'thin_raw_edge_03_05': 6, 'low_recross_lte_50': 7, 'strong_abs_d_ge_115': 4, 'ask_below_65': 5, 'source_quality_risk': 7, 'realized_loss': 4, 'ask_ge_65': 2, 'realized_win': 2, 'weak_abs_d_075_085': 2, 'raw_edge_ge_07': 1, 'mid_abs_d_085_115': 1}`

### Worst Marginal Rows

| market | source | side | won | net c | raw edge | recross | abs d | ask | tags |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -15.000000 | 0.041601 | 0.132257 | 0.784861 | 0.130000 | thin_raw_edge_03_05, low_recross_lte_50, weak_abs_d_075_085, ask_below_65, source_quality_risk, realized_loss |
| KXBTC15M-26MAY070900-00 | rejected_actionable | no | False | -6.000000 | 0.047205 | 0.073267 | 1.083550 | 0.050000 | thin_raw_edge_03_05, low_recross_lte_50, mid_abs_d_085_115, ask_below_65, source_quality_risk, realized_loss |
| KXBTC15M-26MAY070145-45 | rejected_actionable | yes | False | -3.000000 | 0.043906 | 0.028894 | 1.241798 | 0.020000 | thin_raw_edge_03_05, low_recross_lte_50, strong_abs_d_ge_115, ask_below_65, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061930-30 | rejected_actionable | no | False | -2.000000 | 0.031608 | 0.083294 | 1.513246 | 0.010000 | thin_raw_edge_03_05, low_recross_lte_50, strong_abs_d_ge_115, ask_below_65, source_quality_risk, realized_loss |
| KXBTC15M-26MAY062200-00 | rejected_actionable | no | True | 4.000000 | 0.042204 | 0.026847 | 2.370580 | 0.950000 | thin_raw_edge_03_05, low_recross_lte_50, strong_abs_d_ge_115, ask_ge_65, source_quality_risk, realized_win |
| KXBTC15M-26MAY070530-30 | rejected_actionable | no | True | 7.000000 | 0.047387 | 0.085902 | 1.454914 | 0.910000 | thin_raw_edge_03_05, low_recross_lte_50, strong_abs_d_ge_115, ask_ge_65, source_quality_risk, realized_win |
