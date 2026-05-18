# Current FV Candidate Comparison

Generated UTC: `2026-05-05T12:54:43.031220+00:00`

## Scope

- Compares current v38/v42/v43/v44/v45/v47/v50/v52/v53/v55/v56/v57/v58/v60/v61/v62/v66/v68/v69/v70/v71 BTC 15m high-coverage fair-value candidates.
- Requires retrospective 80%+ coverage, fee+1c positive splits, day stability, and strict-forward sample before promotion.
- Research-only; live bot untouched.

## Retrospective

| candidate | kind | min cov | min 1c | all 1c | days | block10 | trades | holdout Brier | holdout logloss |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `v38_explicit_veto_current_best_12_20` | `explicit_entry_veto` | 81.33% | $0.92 | $7.00 | 4/5 | 6/10 | 331 |  |  |
| `v38_explicit_veto_legacy_10_20_forward` | `explicit_entry_veto_legacy_forward` | NA | NA | NA | 0/0 | 0/10 | 0 |  |  |
| `v43_latent_hole_bookblend90_leader` | `fv_latent_book_blend` | 81.33% | $0.45 | $9.85 | 5/5 | 7/10 | 339 | 0.14228 | 0.42787 |
| `v45_latent_disagree_book_else_blend90` | `fv_latent_disagreement_switch` | 81.33% | $0.45 | $10.55 | 5/5 | 8/10 | 334 | 0.14228 | 0.42788 |
| `v47_recross_sigma1_v3cap68` | `fv_recross_hazard_cap` | 81.33% | $0.86 | $12.10 | 5/5 | 8/10 | 334 | 0.14223 | 0.42755 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `fv_thin_edge_certainty_cap` | 81.33% | $0.99 | $12.54 | 5/5 | 8/10 | 333 | 0.14220 | 0.42718 |
| `v52_weakrecross_sigma08_v3p15_cap68` | `fv_weak_recross_hazard_cap` | 81.33% | $0.96 | $11.98 | 5/5 | 8/10 | 333 | 0.14274 | 0.42921 |
| `v53_weakrecross_thinedge_risk_adjusted` | `fv_weak_recross_thin_edge_combo` | 81.33% | $1.09 | $12.31 | 5/5 | 8/10 | 332 | 0.14271 | 0.42884 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `fv_book_anchor_recross` | 81.33% | $0.93 | $13.36 | 5/5 | 8/10 | 333 | 0.14176 | 0.42589 |
| `v56_bookedge_best_calibration_not_tradable` | `fv_book_edge_calibration` | 82.67% | $-1.21 | $10.25 | 5/5 | 7/10 | 334 | 0.14129 | 0.42455 |
| `v57_v55_bookanchor_hold15_prob52` | `fv_book_anchor_recross_hold15_exit` | 81.33% | $0.93 | $13.60 | 5/5 | 8/10 | 333 | 0.14176 | 0.42589 |
| `v58_v55_bookanchor_hold15_prob52_marginlte0p25` | `fv_book_anchor_recross_yes_axis_margin_exit` | 81.33% | $0.57 | $20.45 | 5/5 | 8/10 | 333 | 0.14176 | 0.42589 |
| `v60_v55_bookanchor_hold15_prob52_noside_marginlte0p25` | `fv_book_anchor_recross_no_side_yes_axis_margin_exit` | 81.33% | $0.87 | $21.26 | 5/5 | 8/10 | 333 | 0.14176 | 0.42589 |
| `v61_v55_bookanchor_hold15_prob56_noside_marginlte0p25` | `fv_book_anchor_recross_no_side_prob56_yes_axis_margin_exit` | 81.33% | $0.99 | $16.37 | 5/5 | 8/10 | 333 | 0.14176 | 0.42589 |
| `v62_diffusion_best_calibration_not_tradable` | `fv_diffusion_bridge_calibration` | 84.00% | $-0.23 | $4.00 | 4/5 | 6/10 | 342 | 0.14096 | 0.42418 |
| `v66_no_bookgap_best_calibration_robust` | `fv_no_side_book_gap_shrink` | 84.00% | $1.57 | $8.93 | 5/5 | 7/10 | 338 | 0.13583 | 0.40894 |
| `v66_no_bookgap_balanced_min_split` | `fv_no_side_book_gap_shrink` | 81.33% | $1.51 | $11.45 | 5/5 | 8/10 | 333 | 0.13705 | 0.41336 |
| `v68_regularized_physics_logit_best_calibration_not_tradable` | `fv_regularized_physics_logit_calibration` | 82.51% | $-4.14 | $20.26 | 3/5 | 8/10 | 317 | 0.13377 | 0.40353 |
| `v69_v55_entry_v66_exit_hold15_prob52` | `fv_cross_surface_v55_entry_v66_exit` | 81.33% | $2.17 | $12.81 | 5/5 | 7/10 | 333 | 0.13705 | 0.41336 |
| `v70_v55_entry_v66_bal_margin_exit_prob52_noside_marginlte0p25` | `fv_cross_surface_v55_entry_v66_exit_margin_gate` | 81.33% | $2.17 | $14.40 | 5/5 | 7/10 | 333 | 0.13705 | 0.41336 |
| `v71_v55_entry_v68_exit_best_calibrated_exit_rejected` | `fv_cross_surface_v55_entry_v68_exit_calibration_rejected` | 81.33% | $0.08 | $12.59 | 5/5 | 7/10 | 333 | 0.13384 | 0.40290 |
| `v42_latent_hole_flat_profit` | `fv_latent_flat` | NA | NA | NA | 0/0 | 0/10 | 0 | 0.14932 | 0.44606 |
| `v42_latent_hole_book_fvclean` | `fv_latent_book` | 84.00% | $-0.65 | $7.24 | 5/5 | 5/10 | 337 | 0.14222 | 0.42772 |
| `v42_latent_hole_book_p65_delayed_challenger` | `fv_latent_book` | 80.00% | $-0.11 | $9.47 | 4/5 | 6/10 | 313 | 0.14222 | 0.42772 |
| `v42_latent_hole_bookblend80_balanced` | `fv_latent_book_blend` | 81.33% | $0.45 | $8.53 | 5/5 | 8/10 | 340 | 0.14234 | 0.42804 |
| `v44_bookres_l230_holeblend100_challenger` | `fv_physics_bookres_latent_book` | 85.14% | $-3.42 | $8.23 | 3/5 | 5/10 | 323 | 0.13584 | 0.40852 |

## Strict Forward

| candidate | registered | finalized | days | coverage | fee+1c | forward pass |
|---|---:|---:|---:|---:|---:|---:|
| `v38_explicit_veto_current_best_12_20` | 0 | 0 | 0 | NA | $0.00 | `False` |
| `v38_explicit_veto_legacy_10_20_forward` | 17 | 17 | 1 | 89.47% | $-5.55 | `False` |
| `v43_latent_hole_bookblend90_leader` | 10 | 10 | 1 | 90.91% | $-0.94 | `False` |
| `v45_latent_disagree_book_else_blend90` | 7 | 6 | 1 | 87.50% | $-0.45 | `False` |
| `v47_recross_sigma1_v3cap68` | 25 | 24 | 1 | 100.00% | $1.14 | `False` |
| `v50_thinedge_ask90_edge1_stc450_cap75` | 23 | 23 | 1 | 95.83% | $1.62 | `False` |
| `v52_weakrecross_sigma08_v3p15_cap68` | 0 | 0 | 0 | NA | $0.00 | `False` |
| `v53_weakrecross_thinedge_risk_adjusted` | 20 | 20 | 1 | 95.24% | $2.16 | `False` |
| `v55_bookanchor_m10_v20_g05_book_plus2` | 8 | 8 | 1 | 100.00% | $1.89 | `False` |
| `v56_bookedge_best_calibration_not_tradable` | 0 | 0 | 0 | NA | $0.00 | `False` |
| `v57_v55_bookanchor_hold15_prob52` | 14 | 14 | 1 | 87.50% | $-0.38 | `False` |
| `v58_v55_bookanchor_hold15_prob52_marginlte0p25` | 1 | 1 | 1 | 50.00% | $0.66 | `False` |
| `v60_v55_bookanchor_hold15_prob52_noside_marginlte0p25` | 5 | 5 | 1 | 83.33% | $-1.39 | `False` |
| `v61_v55_bookanchor_hold15_prob56_noside_marginlte0p25` | 4 | 4 | 1 | 80.00% | $-0.28 | `False` |
| `v62_diffusion_best_calibration_not_tradable` | 0 | 0 | 0 | NA | $0.00 | `False` |
| `v66_no_bookgap_best_calibration_robust` | 0 | 0 | 0 | NA | $0.00 | `False` |
| `v66_no_bookgap_balanced_min_split` | 1 | 1 | 1 | 50.00% | $0.01 | `False` |
| `v68_regularized_physics_logit_best_calibration_not_tradable` | 0 | 0 | 0 | NA | $0.00 | `False` |
| `v69_v55_entry_v66_exit_hold15_prob52` | 0 | 0 | 0 | NA | $0.00 | `False` |
| `v70_v55_entry_v66_bal_margin_exit_prob52_noside_marginlte0p25` | 0 | 0 | 0 | 0.00% | $0.00 | `False` |
| `v71_v55_entry_v68_exit_best_calibrated_exit_rejected` | 0 | 0 | 0 | NA | $0.00 | `False` |
| `v42_latent_hole_flat_profit` | 0 | 0 | 0 | NA | $0.00 | `False` |
| `v42_latent_hole_book_fvclean` | 12 | 12 | 1 | 85.71% | $-4.74 | `False` |
| `v42_latent_hole_book_p65_delayed_challenger` | 6 | 6 | 1 | 75.00% | $-0.72 | `False` |
| `v42_latent_hole_bookblend80_balanced` | 11 | 11 | 1 | 91.67% | $-1.33 | `False` |
| `v44_bookres_l230_holeblend100_challenger` | 0 | 0 | 0 | NA | $0.00 | `False` |

## Read

- No candidate is promotion-ready. The missing requirement is strict-forward live sample size/stability.
- Best retrospective min-split PnL is `v70_v55_entry_v66_bal_margin_exit_prob52_noside_marginlte0p25`.
- Best all-market PnL is currently `v60_v55_bookanchor_hold15_prob52_noside_marginlte0p25`; best holdout calibration is `v68_regularized_physics_logit_best_calibration_not_tradable`.
- v68 is the best holdout probability calibration evidence so far, but its high-PnL strategy rows fail split robustness.
- v69 improves worst-split cushion by combining v55 entry with the v66 balanced exit surface, but it gives up all-market PnL versus v57/v60.
- v70 keeps v69's worst-split cushion while adding the v60 NO-side margin-gated exit; it is the current balanced cross-surface strategy to shadow forward.
- v71 shows v68's better probability calibration does not transfer into better exits for the v55 entry universe.
- v66 materially improves calibration and min-split cushion, but it gives up all-market PnL versus v55/v57, so it is a robustness lens rather than the current profit leader.
- The margin-gated v58/v60/v61 branch is overfit-prone until proven forward: the v59/v61 audits show the upside is still tied to NO-side saved exits.
- Strict-forward rows are still far below the 50+ finalized / 2+ day gate; the freshest v57/v60/v61 rows are mixed to negative, so none should be promoted.
