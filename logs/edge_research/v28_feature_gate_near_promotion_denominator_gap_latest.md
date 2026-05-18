# v28 Feature-Gate Near-Promotion Denominator Gap

Research-only denominator audit. No live bot changes or orders.

- Generated UTC: `2026-05-07T10:34:09.100219+00:00`
- Candidate: `post_feature_freeze_entry_raw05_recross60_abs085`
- Rule: `raw05_recross60_abs085`
- Freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- This is a denominator audit of an already-frozen watch row, not a threshold search.
- post_feature_freeze_entry_raw05_recross60_abs085 has 35 selected denominator markets, 34 settled, 1 pending, and needs 7 more selected denominator markets for 75% coverage.
- It also needs 0 additional clean approved selected row(s), assuming no new rejected selected rows, to dilute reconstructed/share quality back under 35%.
- Omitted markets are mainly blocked by {'abs_d_below_min': 20, 'recross_above_max': 6} with source mix {'rejected_actionable': 20}.
- Pending selected rows can help sample/cushion if they settle well, but they are already counted in coverage.
- Best-settled omitted-row counterfactual for the coverage gap would bring coverage to 76.36363636363636%, net to 529.0c, source gate False, cushion gate True; this is diagnostic only and cannot promote a relaxation.

## Gate Snapshot

- Future denominator: `55`
- Selected entries / coverage-needed entries: `35` / `7`
- Clean approved selected rows needed for source gate: `0`
- Settled selected / pending selected: `34` / `1`
- Cushion cents needed: `9.000000`
- Selected summary: `{'rows': 35, 'settled': 34, 'wins': 22, 'losses': 12, 'net_cents': 291.0, 'source_counts': {'approved_entry': 23, 'rejected_actionable': 12}, 'reconstructed_share': 0.34285714285714286}`
- Pending selected summary: `{'rows': 1, 'settled': 0, 'wins': 0, 'losses': 0, 'net_cents': 0, 'source_counts': {'approved_entry': 1}, 'reconstructed_share': 0.0}`
- Omitted summary: `{'rows': 20, 'settled': 20, 'wins': 5, 'losses': 15, 'net_cents': -76.0, 'source_counts': {'rejected_actionable': 20}, 'reconstructed_share': 1.0}`

## Pending Selected Rows

| market | source | side | edge | recross | abs d | ask |
|---|---|---|---:|---:|---:|---:|
| KXBTC15M-26MAY070645-45 | approved_entry | yes | 0.085399 | 0.368798 | 1.013529 | 0.810000 |

## Omitted Fail Reasons

- By reason: `{'abs_d_below_min': 20, 'recross_above_max': 6}`
- By source: `{'rejected_actionable': 20}`
- By reason/source: `{'abs_d_below_min::rejected_actionable': 20, 'recross_above_max::rejected_actionable': 6}`

## Best Settled Omitted-Row Counterfactual

- Summary: `{'rows': 42, 'settled': 41, 'wins': 27, 'losses': 14, 'net_cents': 529.0, 'source_counts': {'approved_entry': 23, 'rejected_actionable': 19}, 'reconstructed_share': 0.4523809523809524, 'added_rows': [{'market': 'KXBTC15M-26MAY062345-45', 'source': 'rejected_actionable', 'side': 'yes', 'net_cents': 67.0, 'fail_reasons': ['recross_above_max', 'abs_d_below_min']}, {'market': 'KXBTC15M-26MAY061945-45', 'source': 'rejected_actionable', 'side': 'no', 'net_cents': 51.0, 'fail_reasons': ['abs_d_below_min']}, {'market': 'KXBTC15M-26MAY062000-00', 'source': 'rejected_actionable', 'side': 'yes', 'net_cents': 48.0, 'fail_reasons': ['abs_d_below_min']}, {'market': 'KXBTC15M-26MAY070045-45', 'source': 'rejected_actionable', 'side': 'no', 'net_cents': 48.0, 'fail_reasons': ['recross_above_max', 'abs_d_below_min']}, {'market': 'KXBTC15M-26MAY070600-00', 'source': 'rejected_actionable', 'side': 'yes', 'net_cents': 28.0, 'fail_reasons': ['abs_d_below_min']}, {'market': 'KXBTC15M-26MAY061715-15', 'source': 'rejected_actionable', 'side': 'yes', 'net_cents': -2.0, 'fail_reasons': ['abs_d_below_min']}, {'market': 'KXBTC15M-26MAY070615-15', 'source': 'rejected_actionable', 'side': 'yes', 'net_cents': -2.0, 'fail_reasons': ['abs_d_below_min']}], 'coverage_pct_if_added_to_current_denominator': 76.36363636363636, 'source_gate_if_added': False, 'cushion_gate_if_added': True}`

## Omitted Rows

| market | source | side | settled | net c | edge | recross | abs d | ask | fail reasons |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY061500-00 | rejected_actionable | yes | True | -13.000000 | 0.316725 | 0.094209 | 0.183718 | 0.110000 | abs_d_below_min |
| KXBTC15M-26MAY061515-15 | rejected_actionable | yes | True | -30.000000 | 0.109251 | 0.413930 | 0.289927 | 0.270000 | abs_d_below_min |
| KXBTC15M-26MAY061700-00 | rejected_actionable | no | True | -42.000000 | 0.408347 | 0.196391 | 0.665443 | 0.380000 | abs_d_below_min |
| KXBTC15M-26MAY061715-15 | rejected_actionable | yes | True | -2.000000 | 0.250844 | 0.072090 | 0.552786 | 0.010000 | abs_d_below_min |
| KXBTC15M-26MAY061745-45 | rejected_actionable | no | True | -16.000000 | 0.370383 | 0.689790 | 0.021042 | 0.140000 | recross_above_max, abs_d_below_min |
| KXBTC15M-26MAY061845-45 | rejected_actionable | no | True | -26.000000 | 0.111076 | 0.613171 | 0.335691 | 0.230000 | recross_above_max, abs_d_below_min |
| KXBTC15M-26MAY061930-30 | rejected_actionable | no | True | -28.000000 | 0.301840 | 0.688823 | 0.118494 | 0.250000 | recross_above_max, abs_d_below_min |
| KXBTC15M-26MAY061945-45 | rejected_actionable | no | True | 51.000000 | 0.348947 | 0.396347 | 0.680058 | 0.450000 | abs_d_below_min |
| KXBTC15M-26MAY062000-00 | rejected_actionable | yes | True | 48.000000 | 0.259489 | 0.419801 | 0.552158 | 0.480000 | abs_d_below_min |
| KXBTC15M-26MAY062200-00 | rejected_actionable | yes | True | -43.000000 | 0.188877 | 0.564940 | 0.199550 | 0.390000 | abs_d_below_min |
| KXBTC15M-26MAY062230-30 | rejected_actionable | yes | True | -42.000000 | 0.338015 | 0.349672 | 0.481781 | 0.380000 | abs_d_below_min |
| KXBTC15M-26MAY062330-30 | rejected_actionable | yes | True | -5.000000 | 0.514636 | 0.307484 | 0.121467 | 0.040000 | abs_d_below_min |
| KXBTC15M-26MAY062345-45 | rejected_actionable | yes | True | 67.000000 | 0.298111 | 0.639973 | 0.214573 | 0.300000 | recross_above_max, abs_d_below_min |
| KXBTC15M-26MAY070045-45 | rejected_actionable | no | True | 48.000000 | 0.102164 | 0.830545 | 0.187292 | 0.480000 | recross_above_max, abs_d_below_min |
| KXBTC15M-26MAY070100-00 | rejected_actionable | no | True | -25.000000 | 0.285013 | 0.647900 | 0.032616 | 0.220000 | recross_above_max, abs_d_below_min |
| KXBTC15M-26MAY070145-45 | rejected_actionable | yes | True | -19.000000 | 0.174262 | 0.357178 | 0.363444 | 0.170000 | abs_d_below_min |
| KXBTC15M-26MAY070530-30 | rejected_actionable | yes | True | -19.000000 | 0.287215 | 0.543382 | 0.114612 | 0.170000 | abs_d_below_min |
| KXBTC15M-26MAY070600-00 | rejected_actionable | yes | True | 28.000000 | 0.122029 | 0.201732 | 0.734324 | 0.690000 | abs_d_below_min |
| KXBTC15M-26MAY070615-15 | rejected_actionable | yes | True | -2.000000 | 0.568996 | 0.142600 | 0.170925 | 0.010000 | abs_d_below_min |
| KXBTC15M-26MAY070630-30 | rejected_actionable | yes | True | -6.000000 | 0.474276 | 0.335538 | 0.025583 | 0.050000 | abs_d_below_min |
