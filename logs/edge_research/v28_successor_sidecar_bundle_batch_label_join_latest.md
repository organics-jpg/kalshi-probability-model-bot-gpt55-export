# v28 Successor Sidecar Batch Label Join

Research-only post-resolution label join for sidecar batch frozen rows. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-18T20:51:34Z`
- Batch label join status: `joined_batch_labels_available`
- Promotion allowed: `False`
- Frozen rows: `16896`
- Label source markets: `197`
- Labeled rows: `16896`
- Joined rows: `16860`
- Joined markets: `195`

## Status Counts

| status | rows |
|---|---:|
| `blocked` | 36 |
| `joined_post_resolution` | 16860 |

## Blockers

| blocker | rows |
|---|---:|
| `missing_settlement_label` | 36 |

## Candidate Metrics

| candidate | rows | markets | candidate brier | v28 brier |
|---|---:|---:|---:|---:|
| `v28s_boundary_monotonic_blend_v001` | 1760 | 154 | 0.13217591463563594 | 0.12977074979238515 |
| `v28s_boundary_monotonic_light_v001` | 1754 | 152 | 0.1304247216897502 | 0.12983777073713676 |
| `v28s_boundary_monotonic_micro_time_safe_v001` | 1620 | 117 | 0.12538712637386915 | 0.12536515381828348 |
| `v28s_boundary_monotonic_time_safe_v001` | 1752 | 151 | 0.12985667632405812 | 0.12978757052176818 |
| `v28s_late_dsigma_residual_tilt_v001` | 1558 | 111 | 0.12316849545273491 | 0.12413020974622542 |
| `v28s_logistic_book_reliability_diag_v001` | 2104 | 195 | 0.37193199531550825 | 0.13346673942126036 |
| `v28s_logistic_boundary_physics_v001` | 2104 | 195 | 0.4758989785456129 | 0.13346673942126036 |
| `v28s_logistic_calibration_v001` | 2104 | 195 | 0.16999005428909847 | 0.13346673942126036 |
| `v28s_monotonic_tabular_v001` | 2104 | 195 | 0.139123022391263 | 0.13346673942126036 |

## Read

- This stage attaches labels only to rows already frozen by the sidecar batch handoff.
- Empty output is expected until real batch frozen rows exist and their markets settle.
- Joined batch labels still require source contract, coverage checks, forward evidence scoring, and the promotion verifier.
