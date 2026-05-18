# v28 Top Strict Target Source/Fragility Audit

Research-only. No live bot changes or orders.

- Generated UTC: `2026-05-11T03:10:24.737505+00:00`
- Risk stop active: `True`

## Interpretation

- These rows are strict-forward and target-coverage candidates, but promotion still needs source-quality, cushion, and risk-stop gates.
- A source share computed here replaces the earlier source_unknown label for these two reconstructed row sets.

## Candidate Gate Table

| gate | policy | settled | W/L | coverage | net | recon share | cushion | live ready | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| raw_p52_boundary_turbulence_skip | `raw_p52_skip_weakraw_nearstrike_recross90` | 88 | 56/32 | 77.192982% | 266c ($2.66) | 0.920455 | 2 | False | reconstructed_share_gt_35pct, full_loss_cushion_lt_3, control_risk_stop_active |
| early_no_boundary_decay_repair_entry | `skip_early_no_boundary_decay_repair_calm_geometry` | 85 | 56/29 | 75.221239% | 27c ($0.27) | 0.694118 | 0 | False | reconstructed_share_gt_35pct, full_loss_cushion_lt_3, control_risk_stop_active |

## raw_p52_boundary_turbulence_skip / raw_p52_skip_weakraw_nearstrike_recross90

- Freeze UTC: `2026-05-06T08:50:27.891448+00:00`
- Entry source counts: `{'rejected_actionable': 81, 'approved_entry': 7}`
- Settled source counts: `{'rejected_actionable': 81, 'approved_entry': 7}`

### Source PnL

| source | entries | settled | W/L | net |
|---|---:|---:|---:|---:|
| approved_entry | 7 | 7 | 7/0 | 95c ($0.95) |
| rejected_actionable | 81 | 81 | 49/32 | 171c ($1.71) |

### Loss Mechanisms

- Loss tag counts: `{'high_recross': 19, 'near_strike': 14, 'weak_boundary_distance': 30, 'cheap_touch': 16, 'source_not_approved': 32, 'thin_edge_lt_3pp': 14, 'extreme_recross': 7, 'razor_edge_lt_1pp': 7}`

| market | side | source | net | p | ask | edge | abs d | recross | tags |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY060530-30 | yes | rejected_actionable | -112c ($-1.12) | 0.588889 | 0.540000 | 0.048889 | 0.202598 | 0.884715 | high_recross, near_strike, weak_boundary_distance, cheap_touch, source_not_approved |
| KXBTC15M-26MAY060545-45 | no | rejected_actionable | -92c ($-0.92) | 0.626642 | 0.440000 | 0.186642 | 0.323422 | 0.689053 | weak_boundary_distance, cheap_touch, source_not_approved |
| KXBTC15M-26MAY060630-30 | no | rejected_actionable | -136c ($-1.36) | 0.675344 | 0.660000 | 0.015344 | 0.393798 | 0.762043 | high_recross, weak_boundary_distance, thin_edge_lt_3pp, source_not_approved |
| KXBTC15M-26MAY060830-30 | no | rejected_actionable | -122c ($-1.22) | 0.600730 | 0.590000 | 0.010730 | 0.286154 | 0.943700 | high_recross, extreme_recross, weak_boundary_distance, thin_edge_lt_3pp, source_not_approved |
| KXBTC15M-26MAY060930-30 | yes | rejected_actionable | -124c ($-1.24) | 0.604377 | 0.600000 | 0.004377 | 0.244982 | 1.150583 | high_recross, extreme_recross, near_strike, weak_boundary_distance, thin_edge_lt_3pp, razor_edge_lt_1pp, source_not_approved |
| KXBTC15M-26MAY061045-45 | no | rejected_actionable | -118c ($-1.18) | 0.601767 | 0.570000 | 0.031767 | 0.212683 | 1.191443 | high_recross, extreme_recross, near_strike, weak_boundary_distance, source_not_approved |
| KXBTC15M-26MAY061100-00 | yes | rejected_actionable | -151c ($-1.51) | 0.740374 | 0.740000 | 0.000374 | 0.597049 | 0.809587 | high_recross, thin_edge_lt_3pp, razor_edge_lt_1pp, source_not_approved |
| KXBTC15M-26MAY061230-30 | yes | rejected_actionable | -140c ($-1.40) | 0.681329 | 0.680000 | 0.001329 | 0.451740 | 0.862457 | high_recross, weak_boundary_distance, thin_edge_lt_3pp, razor_edge_lt_1pp, source_not_approved |
| KXBTC15M-26MAY061545-45 | no | rejected_actionable | -122c ($-1.22) | 0.599662 | 0.590000 | 0.009662 | 0.235093 | 0.729148 | near_strike, weak_boundary_distance, thin_edge_lt_3pp, razor_edge_lt_1pp, source_not_approved |
| KXBTC15M-26MAY061600-00 | no | rejected_actionable | -124c ($-1.24) | 0.610883 | 0.600000 | 0.010883 | 0.229994 | 0.723320 | near_strike, weak_boundary_distance, thin_edge_lt_3pp, source_not_approved |
| KXBTC15M-26MAY061700-00 | no | rejected_actionable | -102c ($-1.02) | 0.547299 | 0.490000 | 0.057299 | 0.145303 | 0.799916 | high_recross, near_strike, weak_boundary_distance, cheap_touch, source_not_approved |
| KXBTC15M-26MAY061715-15 | yes | rejected_actionable | -104c ($-1.04) | 0.633073 | 0.500000 | 0.133073 | 0.324075 | 0.683095 | weak_boundary_distance, cheap_touch, source_not_approved |

### Pending Rows

- Pending selected rows: `0`

## early_no_boundary_decay_repair_entry / skip_early_no_boundary_decay_repair_calm_geometry

- Freeze UTC: `2026-05-06T09:10:09.146392+00:00`
- Entry source counts: `{'rejected_actionable': 59, 'approved_entry': 26}`
- Settled source counts: `{'rejected_actionable': 59, 'approved_entry': 26}`

### Source PnL

| source | entries | settled | W/L | net |
|---|---:|---:|---:|---:|
| approved_entry | 26 | 26 | 21/5 | 35c ($0.35) |
| rejected_actionable | 59 | 59 | 35/24 | -28c ($-0.28) |

### Loss Mechanisms

- Loss tag counts: `{'high_recross': 9, 'extreme_recross': 3, 'near_strike': 9, 'weak_boundary_distance': 19, 'thin_edge_lt_3pp': 8, 'razor_edge_lt_1pp': 4, 'source_not_approved': 24, 'cheap_touch': 11, 'unclassified': 5}`

| market | side | source | net | p | ask | edge | abs d | recross | tags |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY060930-30 | yes | rejected_actionable | -124c ($-1.24) | 0.604377 | 0.600000 | 0.004377 | 0.244982 | 1.150583 | high_recross, extreme_recross, near_strike, weak_boundary_distance, thin_edge_lt_3pp, razor_edge_lt_1pp, source_not_approved |
| KXBTC15M-26MAY061100-00 | yes | rejected_actionable | -151c ($-1.51) | 0.740374 | 0.740000 | 0.000374 | 0.597049 | 0.809587 | high_recross, thin_edge_lt_3pp, razor_edge_lt_1pp, source_not_approved |
| KXBTC15M-26MAY061230-30 | yes | rejected_actionable | -140c ($-1.40) | 0.681329 | 0.680000 | 0.001329 | 0.451740 | 0.862457 | high_recross, weak_boundary_distance, thin_edge_lt_3pp, razor_edge_lt_1pp, source_not_approved |
| KXBTC15M-26MAY061600-00 | no | rejected_actionable | -124c ($-1.24) | 0.610883 | 0.600000 | 0.010883 | 0.229994 | 0.723320 | near_strike, weak_boundary_distance, thin_edge_lt_3pp, source_not_approved |
| KXBTC15M-26MAY061715-15 | yes | rejected_actionable | -104c ($-1.04) | 0.633073 | 0.500000 | 0.133073 | 0.324075 | 0.683095 | weak_boundary_distance, cheap_touch, source_not_approved |
| KXBTC15M-26MAY061745-45 | no | rejected_actionable | -30c ($-0.30) | 0.510383 | 0.140000 | 0.370383 | 0.021042 | 0.689790 | near_strike, weak_boundary_distance, cheap_touch, source_not_approved |
| KXBTC15M-26MAY061830-30 | yes | rejected_actionable | -49c ($-0.49) | 0.553162 | 0.230000 | 0.323162 | 0.098877 | 0.631576 | near_strike, weak_boundary_distance, cheap_touch, source_not_approved |
| KXBTC15M-26MAY062015-15 | yes | rejected_actionable | -106c ($-1.06) | 0.526847 | 0.510000 | 0.016847 | 0.086972 | 0.736601 | near_strike, weak_boundary_distance, cheap_touch, thin_edge_lt_3pp, source_not_approved |
| KXBTC15M-26MAY062030-30 | yes | rejected_actionable | -68c ($-0.68) | 0.544418 | 0.320000 | 0.224418 | 0.107412 | 0.680770 | near_strike, weak_boundary_distance, cheap_touch, source_not_approved |
| KXBTC15M-26MAY062100-00 | no | rejected_actionable | -47c ($-0.47) | 0.615588 | 0.220000 | 0.395588 | 0.321159 | 0.515467 | weak_boundary_distance, cheap_touch, source_not_approved |
| KXBTC15M-26MAY062230-30 | yes | rejected_actionable | -80c ($-0.80) | 0.718015 | 0.380000 | 0.338015 | 0.481781 | 0.349672 | weak_boundary_distance, cheap_touch, source_not_approved |
| KXBTC15M-26MAY062330-30 | yes | rejected_actionable | -108c ($-1.08) | 0.546903 | 0.520000 | 0.026903 | 0.093136 | 0.717935 | near_strike, weak_boundary_distance, cheap_touch, thin_edge_lt_3pp, source_not_approved |

### Pending Rows

- Pending selected rows: `0`
