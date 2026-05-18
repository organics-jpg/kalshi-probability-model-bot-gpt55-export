# v28 Feature-Gate Promotion Gap Audit

Research-only consolidation. No live bot changes, no orders, no new candidate rule.

- Generated UTC: `2026-05-07T15:00:48.002769+00:00`
- Refreshed live-only baseline: `1147c`
- Conclusion: `watch_only_not_promotable`

## Official Post-Freeze Lanes

| candidate | entries | settled | coverage | W/L | net | delta vs live | recon share | cushion | source net | target gaps | clean rows needed | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---|
| post_feature_freeze_entry_raw05_recross60_abs085 | 47 | 36 | 65.28% | 24/12 | 294c | -853c | 27.66% | 2 | approved_entry:230c, rejected_actionable:64c | 75.0%:+7, 80.0%:+11, 90.0%:+18 | 0 | coverage_too_low, full_loss_cushion_lt_3 |
| post_feature_freeze_entry_raw03_recross70_abs075 | 54 | 42 | 75.00% | 26/16 | 274c | -873c | 37.04% | 2 | approved_entry:230c, rejected_actionable:44c | 75.0%:+0, 80.0%:+4, 90.0%:+11 | 4 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| post_feature_freeze_entry_raw07_recross60_abs085 | 33 | 25 | 45.83% | 17/8 | 239c | -908c | 24.24% | 2 | approved_entry:161c, rejected_actionable:78c | 75.0%:+21, 80.0%:+25, 90.0%:+32 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |
| post_feature_freeze_entry_raw05_recross60_abs085_ask65 | 40 | 29 | 55.56% | 26/3 | 207c | -940c | 5.00% | 2 | approved_entry:193c, rejected_actionable:14c | 75.0%:+14, 80.0%:+18, 90.0%:+25 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |

## Size-Shrink Runway

- Policy: `repair_low_absd_quarter_else_half`
- Settled / coverage: `45` / `75.41%`
- Weighted net: `369c`
- Delta versus live: `-738c`
- Row reconstructed share: `41.30%`
- Clean approved rows needed for source: `9`
- Cushion surplus after three full losses: `69c`
- Full-weight wins needed to tie live: `8`
- Blockers: `row_reconstructed_share_gt_35pct`

## Source Feasibility

- Future denominator: `71`
- Approved markets available: `37`
- Target 75.0%: required `54`, min reconstructed share `31.48%`, feasible under source gate `True`.
- Target 80.0%: required `57`, min reconstructed share `35.09%`, feasible under source gate `False`.
- Target 90.0%: required `64`, min reconstructed share `42.19%`, feasible under source gate `False`.

## Source Mechanism

- Source-only weighted net: `-36c` on `20` rows.

| tag | count | W/L | weighted net |
|---|---:|---:|---:|
| mid_ask_lt065 | 6 | 1/5 | -87c |
| moderate_p_side_lt085 | 11 | 4/7 | -74c |
| weak_boundary_distance_lt065 | 10 | 5/5 | -55c |
| source_quality_error | 20 | 12/8 | -36c |
| early_observation_stc_lt240 | 4 | 2/2 | -21c |
| thin_depth_lt100 | 6 | 4/2 | -12c |

## Promotion Gap

- No feature-gate lane is live-ready.
- Current broad post-freeze lane clears sample, coverage, positive PnL but still misses source share, full-loss cushion, live-baseline delta; it needs 0 more selected markets for 75% coverage and 4 clean approved additions to satisfy the source-share cap if all else stayed constant.
- Size-shrink remains watch-only: 369c weighted net, 75.41% coverage, 41.30% row reconstructed share, -738c versus live, blockers row_reconstructed_share_gt_35pct.
- Source feasibility artifact remains a bound, not a rule: 75% target feasible=True at minimum reconstructed share 31.48%; 80% target feasible=False.
