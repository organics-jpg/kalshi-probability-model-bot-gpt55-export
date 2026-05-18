# v28 Midprice Dual-Exit Guard Runway

Research-only runway monitor. No live bot changes or orders.

- Generated UTC: `2026-05-11T02:47:52.093762+00:00`
- Guard freeze UTC: `2026-05-07T04:20:48.449946+00:00`
- Live baseline net: `-202c ($-2.02)`
- Any live-ready guard candidate: `False`
- Best policy: `diagnostic_bridge_quarter_midprice_boundary_or_reduce_p_hold80`
- Best missing gates: `['post_joined_rows+23', 'post_suppressed_rows+26', 'post_cushion_cents+60', 'guard_probe_blockers_present', 'live_ready_false']`

## Guard Variants

| rank | policy | coverage | diag rows | diag W/L | diag net | diag recon | post rows | post suppress | post W/L | post net | post recon | post cushion | live ready |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `diagnostic_bridge_quarter_midprice_boundary_or_reduce_p_hold80` | 77.8% | 57 | 49/7 | 1418c ($14.18) | 14.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 2 | `diagnostic_bridge_half_midprice_boundary_or_reduce_p_hold80` | 77.8% | 57 | 49/7 | 1418c ($14.18) | 14.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 3 | `diagnostic_bridge_control_no_shrink_or_reduce_p_hold80` | 77.8% | 57 | 49/7 | 1418c ($14.18) | 14.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 4 | `diagnostic_bridge_quarter_midprice_boundary_or_no_midprice_boundary_suppress` | 77.8% | 57 | 49/7 | 1412c ($14.12) | 14.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 5 | `diagnostic_bridge_quarter_midprice_boundary_or_reduce_p_hold80_no_midprice_boundary` | 77.8% | 57 | 49/7 | 1412c ($14.12) | 14.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 6 | `diagnostic_bridge_half_midprice_boundary_or_no_midprice_boundary_suppress` | 77.8% | 57 | 49/7 | 1405c ($14.05) | 14.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 7 | `diagnostic_bridge_half_midprice_boundary_or_reduce_p_hold80_no_midprice_boundary` | 77.8% | 57 | 49/7 | 1405c ($14.05) | 14.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 8 | `diagnostic_entry_quarter_midprice_boundary_or_reduce_p_hold80` | 78.2% | 59 | 50/8 | 1400c ($14.00) | 15.3% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 9 | `diagnostic_entry_half_midprice_boundary_or_reduce_p_hold80` | 78.2% | 59 | 50/8 | 1400c ($14.00) | 15.3% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 10 | `diagnostic_entry_control_no_shrink_or_reduce_p_hold80` | 78.2% | 59 | 50/8 | 1400c ($14.00) | 15.3% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 11 | `diagnostic_entry_quarter_midprice_boundary_or_no_midprice_boundary_suppress` | 78.2% | 59 | 50/8 | 1394c ($13.94) | 15.3% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 12 | `diagnostic_entry_quarter_midprice_boundary_or_reduce_p_hold80_no_midprice_boundary` | 78.2% | 59 | 50/8 | 1394c ($13.94) | 15.3% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 13 | `diagnostic_bridge_control_no_shrink_or_no_midprice_boundary_suppress` | 77.8% | 57 | 49/7 | 1392c ($13.92) | 14.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 14 | `diagnostic_bridge_control_no_shrink_or_reduce_p_hold80_no_midprice_boundary` | 77.8% | 57 | 49/7 | 1392c ($13.92) | 14.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 15 | `diagnostic_bridge_quarter_midprice_boundary_or_base` | 77.8% | 57 | 49/7 | 1388c ($13.88) | 14.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 16 | `diagnostic_entry_half_midprice_boundary_or_no_midprice_boundary_suppress` | 78.2% | 59 | 50/8 | 1387c ($13.87) | 15.3% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 17 | `diagnostic_entry_half_midprice_boundary_or_reduce_p_hold80_no_midprice_boundary` | 78.2% | 59 | 50/8 | 1387c ($13.87) | 15.3% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 18 | `diagnostic_entry_control_no_shrink_or_no_midprice_boundary_suppress` | 78.2% | 59 | 50/8 | 1374c ($13.74) | 15.3% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 19 | `diagnostic_entry_control_no_shrink_or_reduce_p_hold80_no_midprice_boundary` | 78.2% | 59 | 50/8 | 1374c ($13.74) | 15.3% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 20 | `diagnostic_entry_quarter_midprice_boundary_or_base` | 78.2% | 59 | 50/8 | 1370c ($13.70) | 15.3% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 21 | `diagnostic_bridge_half_midprice_boundary_or_base` | 77.8% | 57 | 49/7 | 1358c ($13.58) | 14.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 22 | `diagnostic_entry_half_midprice_boundary_or_base` | 78.2% | 59 | 50/8 | 1340c ($13.40) | 15.3% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 23 | `diagnostic_bridge_control_no_shrink_or_base` | 77.8% | 57 | 49/7 | 1298c ($12.98) | 14.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 24 | `diagnostic_entry_control_no_shrink_or_base` | 78.2% | 59 | 50/8 | 1280c ($12.80) | 15.3% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 25 | `post_midprice_shrink_birth_entry_control_no_shrink_or_reduce_p_hold80` | 80.0% | 24 | 20/3 | 590c ($5.90) | 12.5% | 21 | 10 | 18/2 | 558c ($5.58) | 9.5% | 5 | False |
| 26 | `post_midprice_shrink_birth_entry_half_midprice_boundary_or_reduce_p_hold80` | 80.0% | 24 | 20/3 | 574c ($5.74) | 12.5% | 21 | 10 | 18/2 | 558c ($5.58) | 9.5% | 5 | False |
| 27 | `post_midprice_shrink_birth_entry_quarter_midprice_boundary_or_reduce_p_hold80` | 80.0% | 24 | 20/3 | 566c ($5.66) | 12.5% | 21 | 10 | 18/2 | 558c ($5.58) | 9.5% | 5 | False |
| 28 | `post_midprice_shrink_birth_entry_control_no_shrink_or_reduce_p_hold80_no_midprice_boundary` | 80.0% | 24 | 20/3 | 564c ($5.64) | 12.5% | 21 | 10 | 18/2 | 558c ($5.58) | 9.5% | 5 | False |
| 29 | `post_midprice_shrink_birth_entry_half_midprice_boundary_or_reduce_p_hold80_no_midprice_boundary` | 80.0% | 24 | 20/3 | 561c ($5.61) | 12.5% | 21 | 10 | 18/2 | 558c ($5.58) | 9.5% | 5 | False |
| 30 | `post_midprice_shrink_birth_entry_quarter_midprice_boundary_or_reduce_p_hold80_no_midprice_boundary` | 80.0% | 24 | 20/3 | 560c ($5.59) | 12.5% | 21 | 10 | 18/2 | 558c ($5.58) | 9.5% | 5 | False |
| 31 | `post_feature_freeze_entry_quarter_midprice_boundary_or_reduce_p_hold80` | 75.8% | 30 | 24/5 | 494c ($4.94) | 6.7% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 32 | `post_feature_freeze_entry_half_midprice_boundary_or_reduce_p_hold80` | 75.8% | 30 | 24/5 | 494c ($4.94) | 6.7% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 33 | `post_feature_freeze_entry_control_no_shrink_or_reduce_p_hold80` | 75.8% | 30 | 24/5 | 494c ($4.94) | 6.7% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 34 | `post_feature_freeze_entry_quarter_midprice_boundary_or_no_midprice_boundary_suppress` | 75.8% | 30 | 24/5 | 488c ($4.88) | 6.7% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 35 | `post_feature_freeze_entry_quarter_midprice_boundary_or_reduce_p_hold80_no_midprice_boundary` | 75.8% | 30 | 24/5 | 488c ($4.88) | 6.7% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 36 | `post_midprice_shrink_birth_entry_control_no_shrink_or_base` | 80.0% | 24 | 20/3 | 486c ($4.86) | 12.5% | 21 | 12 | 18/2 | 454c ($4.54) | 9.5% | 4 | False |
| 37 | `post_feature_freeze_entry_half_midprice_boundary_or_no_midprice_boundary_suppress` | 75.8% | 30 | 24/5 | 481c ($4.81) | 6.7% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 38 | `post_feature_freeze_entry_half_midprice_boundary_or_reduce_p_hold80_no_midprice_boundary` | 75.8% | 30 | 24/5 | 481c ($4.81) | 6.7% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 39 | `post_midprice_shrink_birth_entry_half_midprice_boundary_or_base` | 80.0% | 24 | 20/3 | 470c ($4.70) | 12.5% | 21 | 12 | 18/2 | 454c ($4.54) | 9.5% | 4 | False |
| 40 | `post_feature_freeze_entry_control_no_shrink_or_no_midprice_boundary_suppress` | 75.8% | 30 | 24/5 | 468c ($4.68) | 6.7% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 41 | `post_feature_freeze_entry_control_no_shrink_or_reduce_p_hold80_no_midprice_boundary` | 75.8% | 30 | 24/5 | 468c ($4.68) | 6.7% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 42 | `post_feature_freeze_entry_quarter_midprice_boundary_or_base` | 75.8% | 30 | 24/5 | 464c ($4.64) | 6.7% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 43 | `post_midprice_shrink_birth_entry_quarter_midprice_boundary_or_base` | 80.0% | 24 | 20/3 | 462c ($4.62) | 12.5% | 21 | 12 | 18/2 | 454c ($4.54) | 9.5% | 4 | False |
| 44 | `post_midprice_shrink_birth_entry_control_no_shrink_or_no_midprice_boundary_suppress` | 80.0% | 24 | 20/3 | 460c ($4.60) | 12.5% | 21 | 12 | 18/2 | 454c ($4.54) | 9.5% | 4 | False |
| 45 | `post_midprice_shrink_birth_entry_half_midprice_boundary_or_no_midprice_boundary_suppress` | 80.0% | 24 | 20/3 | 457c ($4.57) | 12.5% | 21 | 12 | 18/2 | 454c ($4.54) | 9.5% | 4 | False |
| 46 | `post_midprice_shrink_birth_entry_quarter_midprice_boundary_or_no_midprice_boundary_suppress` | 80.0% | 24 | 20/3 | 456c ($4.55) | 12.5% | 21 | 12 | 18/2 | 454c ($4.54) | 9.5% | 4 | False |
| 47 | `post_feature_freeze_entry_half_midprice_boundary_or_base` | 75.8% | 30 | 24/5 | 434c ($4.34) | 6.7% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 48 | `post_soft_frontier_birth_entry_quarter_midprice_boundary_or_reduce_p_hold80` | 76.9% | 25 | 20/4 | 408c ($4.08) | 8.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 49 | `post_soft_frontier_birth_entry_half_midprice_boundary_or_reduce_p_hold80` | 76.9% | 25 | 20/4 | 408c ($4.08) | 8.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 50 | `post_soft_frontier_birth_entry_control_no_shrink_or_reduce_p_hold80` | 76.9% | 25 | 20/4 | 408c ($4.08) | 8.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 51 | `post_soft_frontier_birth_entry_quarter_midprice_boundary_or_no_midprice_boundary_suppress` | 76.9% | 25 | 20/4 | 402c ($4.01) | 8.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 52 | `post_soft_frontier_birth_entry_quarter_midprice_boundary_or_reduce_p_hold80_no_midprice_boundary` | 76.9% | 25 | 20/4 | 402c ($4.01) | 8.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 53 | `post_soft_frontier_birth_entry_half_midprice_boundary_or_no_midprice_boundary_suppress` | 76.9% | 25 | 20/4 | 395c ($3.95) | 8.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 54 | `post_soft_frontier_birth_entry_half_midprice_boundary_or_reduce_p_hold80_no_midprice_boundary` | 76.9% | 25 | 20/4 | 395c ($3.95) | 8.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 55 | `post_soft_frontier_birth_entry_control_no_shrink_or_no_midprice_boundary_suppress` | 76.9% | 25 | 20/4 | 382c ($3.82) | 8.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 56 | `post_soft_frontier_birth_entry_control_no_shrink_or_reduce_p_hold80_no_midprice_boundary` | 76.9% | 25 | 20/4 | 382c ($3.82) | 8.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 57 | `post_soft_frontier_birth_entry_quarter_midprice_boundary_or_base` | 76.9% | 25 | 20/4 | 378c ($3.78) | 8.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 58 | `post_feature_freeze_entry_control_no_shrink_or_base` | 75.8% | 30 | 24/5 | 374c ($3.74) | 6.7% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 59 | `post_soft_frontier_birth_entry_half_midprice_boundary_or_base` | 76.9% | 25 | 20/4 | 348c ($3.48) | 8.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |
| 60 | `post_soft_frontier_birth_entry_control_no_shrink_or_base` | 76.9% | 25 | 20/4 | 288c ($2.88) | 8.0% | 7 | 4 | 6/0 | 240c ($2.40) | 0.0% | 2 | False |

## Interpretation

- This report is a runway monitor for the current top diagnostic branch, not a promotion override.
- Pre-freeze diagnostic rows show mechanism strength; only post-freeze joined/suppressed rows count for live readiness.
- Best current policy diagnostic_bridge_quarter_midprice_boundary_or_reduce_p_hold80 has diagnostic net 1418.0c, post net 240.0c, and missing gates ['post_joined_rows+23', 'post_suppressed_rows+26', 'post_cushion_cents+60', 'guard_probe_blockers_present', 'live_ready_false'].
