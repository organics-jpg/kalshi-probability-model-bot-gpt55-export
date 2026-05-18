# v28 Frozen Target-Coverage Book-Edge Gate

Research-only; no live bot changes or orders.

- Candidate: `target_coverage_skip_raw_edge_ge_15pp`
- Freeze timestamp UTC: `2026-05-06T13:14:17.059642+00:00`
- Base policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Future denominator: `97`
- Candidate live-ready: `False`
- Blockers: `coverage_too_low, delta_not_positive`

## Current Read

- Frozen target-coverage book-edge gate has denominator 97, candidate entries/settled 60/60.
- Coverage 61.855670103092784%; candidate net -163.0c versus target -2.0c; delta -161.0c.
- Skipped rows were 6/8 for 161.0c.
- Promotion blockers: coverage_too_low, delta_not_positive.
- This is broad shadow validation only; no live bot code or order behavior changed.

## Scorecard

| surface | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| target_summary | 74 | 74 | 43/31 | 76.288660 | -2.000000 | -0.027027 |
| candidate_summary | 60 | 60 | 37/23 | 61.855670 | -163.000000 | -2.716667 |
| skipped_summary | 14 | 14 | 6/8 | 14.432990 | 161.000000 | 11.500000 |

## Skipped Rows

| market | source | side | won | net c | raw | ask | edge | stc | recross | abs d |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY060945-45` | rejected_actionable | no | True | 96.000000 | 0.761891 | 0.500000 | 0.261891 | 884.381000 | 0.777721 | 0.648099 |
| `KXBTC15M-26MAY061745-45` | rejected_actionable | no | False | -30.000000 | 0.510383 | 0.140000 | 0.370383 | 668.465000 | 0.689790 | 0.021042 |
| `KXBTC15M-26MAY061830-30` | rejected_actionable | yes | False | -49.000000 | 0.553162 | 0.230000 | 0.323162 | 653.539000 | 0.631576 | 0.098877 |
| `KXBTC15M-26MAY061900-00` | rejected_actionable | yes | True | 128.000000 | 0.501794 | 0.340000 | 0.161794 | 766.143000 | 0.794136 | 0.001392 |
| `KXBTC15M-26MAY062030-30` | rejected_actionable | yes | False | -68.000000 | 0.544418 | 0.320000 | 0.224418 | 804.712000 | 0.680770 | 0.107412 |
| `KXBTC15M-26MAY062100-00` | rejected_actionable | no | False | -47.000000 | 0.615588 | 0.220000 | 0.395588 | 683.547000 | 0.515467 | 0.321159 |
| `KXBTC15M-26MAY062130-30` | rejected_actionable | yes | True | 114.000000 | 0.586142 | 0.410000 | 0.176142 | 753.109000 | 0.800157 | 0.212967 |
| `KXBTC15M-26MAY062200-00` | rejected_actionable | no | True | 104.000000 | 0.617816 | 0.460000 | 0.157816 | 609.066000 | 0.567395 | 0.258689 |
| `KXBTC15M-26MAY062230-30` | rejected_actionable | yes | False | -80.000000 | 0.718015 | 0.380000 | 0.338015 | 460.951000 | 0.349672 | 0.481781 |
| `KXBTC15M-26MAY070030-30` | rejected_actionable | no | False | -70.000000 | 0.523605 | 0.330000 | 0.193605 | 770.113000 | 0.901651 | 0.059362 |
| `KXBTC15M-26MAY070100-00` | rejected_actionable | no | False | -47.000000 | 0.505013 | 0.220000 | 0.285013 | 543.305000 | 0.647900 | 0.032616 |
| `KXBTC15M-26MAY070200-00` | rejected_actionable | yes | False | -63.000000 | 0.505710 | 0.300000 | 0.205710 | 532.791000 | 0.602432 | 0.019784 |
| `KXBTC15M-26MAY070615-15` | rejected_actionable | no | True | 141.000000 | 0.610872 | 0.280000 | 0.330872 | 702.260000 | 0.645491 | 0.275276 |
| `KXBTC15M-26MAY070745-45` | approved_entry | yes | True | 32.000000 | 0.903807 | 0.680000 | 0.223807 | 474.481000 | 0.197594 | 1.081343 |
