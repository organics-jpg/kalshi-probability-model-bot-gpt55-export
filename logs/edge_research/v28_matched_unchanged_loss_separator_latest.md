# v28 Matched-Unchanged Loss Separator

Research-only diagnostic. No live bot changes or orders.

- Generated UTC: `2026-05-07T13:07:29.222728+00:00`
- Matched-unchanged rows: `21`
- Hold helpful/harmful/flat: `14/5/2`
- Actual loss total: `-780c`
- Hold delta total: `636c`

## Interpretation

- Research-only diagnostic separator; it does not freeze, promote, or change an exit rule.
- Matched-unchanged loss rows split into 14 hold-helpful, 5 hold-harmful, and 2 flat rows.
- The all-row hold delta is 636.0c, but this is not deployable because the harmful rows are true FV/entry failures.
- Best clean observable diagnostic separator is `p_side >= 0.86587` with 11 selected rows, 9/0 helpful/harmful, and 820.0c hold delta.
- On the full scored exit denominator, the best audited separator `eligible_depth >= 10.49 AND p_side >= 0.86587` selects 88 rows with 63/10 helpful/harmful and 916.0c delta.
- Use this only to decide what future frozen watch might be worth testing; old rows remain diagnostic context.

## Top Clean Observable Separators

| rule | selected | helpful/harmful/flat | actual loss c | hold net c | hold delta c | loss count reduction | worst harm c |
|---|---:|---:|---:|---:|---:|---:|---:|
| `p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `abs_d_sigma >= 0.843583 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `abs_d_sigma >= 0.872216 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `abs_d_sigma <= 3.99125 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `ask_cents >= 9 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `ask_cents <= 81 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `eligible_depth >= 10.49 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `eligible_depth <= 2840.98 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.85 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.854571 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.860865 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.86587 AND p_side <= 0.999788` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.86587 AND raw_edge_cents >= 4.08696` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.86587 AND raw_edge_cents <= 89.9788` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.86587 AND recross_hazard_score >= 0.0028072` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.86587 AND recross_hazard_score <= 0.415103` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `exit_cents >= 12 AND p_side >= 0.86587` | 9 | 9/0/0 | -302c | 518c | 820c | 9 | 0c |
| `exit_cents <= 74 AND p_side >= 0.86587` | 9 | 9/0/0 | -302c | 518c | 820c | 9 | 0c |
| `abs_d_sigma >= 0.886629 AND p_side >= 0.86587` | 10 | 8/0/2 | -424c | 328c | 752c | 8 | 0c |
| `abs_d_sigma >= 0.913273 AND p_side >= 0.86587` | 10 | 8/0/2 | -424c | 328c | 752c | 8 | 0c |

## Top Overall Observable Separators

| rule | selected | helpful/harmful/flat | actual loss c | hold net c | hold delta c | loss count reduction | worst harm c |
|---|---:|---:|---:|---:|---:|---:|---:|
| `p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `abs_d_sigma >= 0.843583 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `abs_d_sigma >= 0.872216 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `abs_d_sigma <= 3.99125 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `ask_cents >= 9 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `ask_cents <= 81 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `eligible_depth >= 10.49 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `eligible_depth <= 2840.98 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.85 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.854571 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.860865 AND p_side >= 0.86587` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.86587 AND p_side <= 0.999788` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.86587 AND raw_edge_cents >= 4.08696` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.86587 AND raw_edge_cents <= 89.9788` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.86587 AND recross_hazard_score >= 0.0028072` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `p_side >= 0.86587 AND recross_hazard_score <= 0.415103` | 11 | 9/0/2 | -454c | 366c | 820c | 9 | 0c |
| `exit_cents >= 12 AND p_side >= 0.86587` | 9 | 9/0/0 | -302c | 518c | 820c | 9 | 0c |
| `exit_cents <= 74 AND p_side >= 0.86587` | 9 | 9/0/0 | -302c | 518c | 820c | 9 | 0c |
| `abs_d_sigma >= 0.886629 AND p_side >= 0.86587` | 10 | 8/0/2 | -424c | 328c | 752c | 8 | 0c |
| `abs_d_sigma >= 0.913273 AND p_side >= 0.86587` | 10 | 8/0/2 | -424c | 328c | 752c | 8 | 0c |

## Full Exit-Denominator Sanity Check

These rows apply the loss-derived separator to all scored exit rows, not just losing rows.

| rule | selected | helpful/harmful/flat | current net c | hold net c | hold delta c | current losses -> hold losses | loss count reduction | worst harm c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `eligible_depth >= 10.49 AND p_side >= 0.86587` | 88 | 63/10/15 | 422c | 1338c | 916c | 32 -> 12 | 20 | -180c |
| `ask_cents <= 81 AND p_side >= 0.86587` | 43 | 28/6/9 | -42c | 850c | 892c | 22 -> 8 | 14 | -138c |
| `p_side >= 0.86587` | 92 | 66/11/15 | 452c | 1278c | 826c | 33 -> 13 | 20 | -180c |
| `abs_d_sigma >= 0.843583 AND p_side >= 0.86587` | 92 | 66/11/15 | 452c | 1278c | 826c | 33 -> 13 | 20 | -180c |
| `abs_d_sigma >= 0.872216 AND p_side >= 0.86587` | 92 | 66/11/15 | 452c | 1278c | 826c | 33 -> 13 | 20 | -180c |
| `abs_d_sigma <= 3.99125 AND p_side >= 0.86587` | 92 | 66/11/15 | 452c | 1278c | 826c | 33 -> 13 | 20 | -180c |
| `ask_cents >= 9 AND p_side >= 0.86587` | 92 | 66/11/15 | 452c | 1278c | 826c | 33 -> 13 | 20 | -180c |
| `eligible_depth <= 2840.98 AND p_side >= 0.86587` | 92 | 66/11/15 | 452c | 1278c | 826c | 33 -> 13 | 20 | -180c |
| `p_side >= 0.85 AND p_side >= 0.86587` | 92 | 66/11/15 | 452c | 1278c | 826c | 33 -> 13 | 20 | -180c |
| `p_side >= 0.854571 AND p_side >= 0.86587` | 92 | 66/11/15 | 452c | 1278c | 826c | 33 -> 13 | 20 | -180c |
| `p_side >= 0.860865 AND p_side >= 0.86587` | 92 | 66/11/15 | 452c | 1278c | 826c | 33 -> 13 | 20 | -180c |
| `p_side >= 0.86587 AND p_side <= 0.999788` | 92 | 66/11/15 | 452c | 1278c | 826c | 33 -> 13 | 20 | -180c |

## Largest Hold-Helpful Rows

| market | side/result | actual | hold | delta | exit | p_side | raw edge | recross | abs d | tags |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY062015-15` | no/no | -60c | 116c | 176c | exit_trigger@12.0 | 0.871622 | 43.162189 | 0.094396 | 0.916460 | large_50_99c, exit_policy_cost, exit_policy_clip_vs_hold, near_boundary |
| `KXBTC15M-26MAY061800-00` | no/no | -86c | 66c | 152c | exit_trigger@24.0 | 0.897587 | 20.758707 | 0.255101 | 1.041596 | large_50_99c, exit_policy_cost, recross_hazard_high, exit_policy_clip_vs_hold |
| `KXBTC15M-26MAY060800-00` | yes/yes | -32c | 68c | 100c | exit_trigger@50.0 | 0.874265 | 19.426542 | 0.130377 | 0.931829 | medium_25_49c, exit_policy_cost, exit_policy_clip_vs_hold, near_boundary |
| `KXBTC15M-26MAY060700-00` | yes/yes | -30c | 46c | 76c | exit_trigger@62.0 | 0.854571 | 6.957055 | 0.150915 | 0.886629 | medium_25_49c, exit_policy_cost, exit_policy_clip_vs_hold, near_boundary |
| `KXBTC15M-26MAY060700-00` | yes/yes | -22c | 50c | 72c | exit_trigger@64.0 | 0.852084 | 8.708443 | 0.192044 | 0.872216 | small_10_24c, exit_policy_cost, exit_policy_clip_vs_hold, near_boundary |
| `KXBTC15M-26MAY060900-00` | no/no | -16c | 54c | 70c | exit_trigger@65.0 | 0.855256 | 11.025574 | 0.145613 | 0.858522 | small_10_24c, exit_policy_cost, exit_policy_clip_vs_hold, near_boundary |
| `KXBTC15M-26MAY060300-00` | yes/yes | -30c | 38c | 68c | exit_trigger@66.0 | 0.865870 | 4.086960 | 0.157163 | 0.880452 | medium_25_49c, exit_policy_cost, thin_touch_depth, exit_policy_clip_vs_hold, thin_raw_edge, rich_entry, near_boundary |
| `KXBTC15M-26MAY060515-15` | no/no | -26c | 42c | 68c | exit_trigger@66.0 | 0.882737 | 7.773652 | 0.395055 | 0.970009 | medium_25_49c, exit_policy_cost, recross_hazard_high, exit_policy_clip_vs_hold, near_boundary |
| `KXBTC15M-26MAY060930-30` | no/no | -20c | 48c | 68c | exit_trigger@66.0 | 0.866835 | 9.183483 | 0.415103 | 0.920139 | small_10_24c, exit_policy_cost, recross_hazard_high, exit_policy_clip_vs_hold, near_boundary |
| `KXBTC15M-26MAY062115-15` | yes/yes | -12c | 54c | 66c | exit_trigger@67.0 | 0.942571 | 19.757121 | 0.239053 | 1.308547 | small_10_24c, exit_policy_cost, exit_policy_clip_vs_hold |

## Largest Hold-Harmful Rows

| market | side/result | actual | hold | delta | exit | p_side | raw edge | recross | abs d | tags |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY060900-00` | yes/no | -76c | -156c | -80c | exit_trigger@40.0 | 0.851503 | 5.650336 | 0.267055 | 0.847529 | large_50_99c, fv_or_entry_timing_error, recross_hazard_high, near_boundary |
| `KXBTC15M-26MAY060745-45` | yes/no | -70c | -156c | -86c | exit_trigger@43.0 | 0.850438 | 5.543807 | 0.173125 | 0.862815 | large_50_99c, fv_or_entry_timing_error, near_boundary |
| `KXBTC15M-26MAY062115-15` | no/yes | -34c | -138c | -104c | exit_trigger@52.0 | 0.860865 | 15.586452 | 0.247246 | 0.897785 | medium_25_49c, fv_or_entry_timing_error, near_boundary |
| `KXBTC15M-26MAY060745-45` | yes/no | -24c | -138c | -114c | exit_trigger@57.0 | 0.851843 | 14.684309 | 0.303224 | 0.889718 | small_10_24c, fv_or_entry_timing_error, recross_hazard_high, near_boundary |
| `KXBTC15M-26MAY061300-00` | yes/no | -30c | -160c | -130c | exit_trigger@65.0 | 0.860906 | 4.590566 | 0.301730 | 0.913273 | medium_25_49c, fv_or_entry_timing_error, recross_hazard_high, crowded_depth, thin_raw_edge, rich_entry, near_boundary |
