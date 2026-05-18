# v28 FV Candidate Decision Matrix

Evidence-ranked FV candidate comparison. This does not promote or trade.

- Target: More accurate FV while preserving roughly 75-80%+ BTC 15m coverage.

## Current Read

- Discovery best by Brier is conditional_book_no_late_discount (-0.025583191549724993); this is not promotion evidence.
- 34 candidate rows have at least one post-freeze forward entry; 34 have at least 30 settled rows.
- Reward-memory +5pp is robust but discovery Brier delta (0.004831451270001064) is weaker than simple +5pp (0.006406016572098855).
- Best coverage valve is raw_p50_turbulence_valve_edge4_p60_recross90_near20 with forward coverage 82.23684210526315 and net -333.0c.
- Cleanest actual-approved FV evidence is book_probability: 133 settled rows, Brier/logloss deltas 0.006168655138428583/-0.025019035845109228.
- Approved-entry book-edge actionability best is skip_discount15_book_edge_lt_5pp: retained coverage 84.21052631578948, net 927.0c, delta 226.0c versus keeping all actual v28-approved entries.
- Frozen approved-entry book-edge gate now has future entries/settled 88/71; delta 152.0c and blockers [].
- Frozen target-coverage book-edge gate has denominator/entries/settled 97/60/60; coverage 61.855670103092784, delta -161.0c, blockers ['coverage_too_low', 'delta_not_positive'].
- Conditional approved-entry book FV is now frozen for future validation: future settled 93, pre-freeze Brier/logloss deltas -0.025583191549724993/-0.1425133634906126.
- On the target-coverage surface, best FV overlay is book_probability with coverage 73.68421052631578, Brier delta -0.014912731593232115, and logloss delta -0.026989299326773852.
- Raw-p52 crowd-prior skip discovery keeps coverage 85.6353591160221 versus base 93.37016574585635, net 43.0c versus 71.0c; skipped rows are 6/8 for 28.0c.
- Frozen raw-p52 crowd-prior skip has denominator 101, settled 88, and blockers ['net_not_positive', 'simulated_share_gt_35pct']; it is watch-only.
- Book-disagreement shrink is not currently stronger than raw: raw p52 net 71.0c, 50% shrink -263.0c, 75% shrink -136.0c.
- Shrink underperformance is partly entry-order interaction: 50% shrink replacement delta is -334.0c across 7 replacements, so hard abstention is cleaner than side-search replacement.
- Raw-p52 middle-confidence early-NO boundary skip is the strongest discovery row right now: coverage 86.1878453038674 versus base 93.37016574585635, net 633.0c versus 71.0c; skipped bucket 5/8 for -562.0c.
- Early-NO band robustness pass is True; canonical coverage/net 86.1878453038674/633.0c and worst leave-one-skipped delta 426.0c.
- Frozen early-NO boundary band skip has denominator 100, settled 93, and blockers ['coverage_too_high', 'net_not_positive', 'simulated_share_gt_35pct']; it needs fresh forward rows before use.
- Early-NO boundary band runway ready=False with checks [{'name': 'settled_rows_ge_30', 'needed': 0, 'passed': True, 'value': 93}, {'name': 'coverage_75_to_90', 'needed': '75.0-90.0', 'passed': False, 'value': 93.0}, {'name': 'candidate_net_positive', 'needed': '>0', 'passed': False, 'value': -604.0}, {'name': 'delta_vs_raw_positive', 'needed': '>0', 'passed': False, 'value': -186.0}, {'name': 'simulated_share_lte_35pct', 'needed': '<=0.35', 'passed': False, 'value': 0.9247311827956989}]; pending skipped rows 0 and stressed delta -186.0c.
- Early-NO boundary decay repair runway has entries/settled/net 85/85/27.0c at coverage 75.22123893805309; rows needed 0 and full-loss cushion 0.
- Target-coverage paired evidence has 112 settled rows; Brier mean/p95 -0.014912731593232144/0.0006431900556874973, logloss mean/p95 -0.026989299326773745/0.005780956177999605.
- Strong raw-p>=60 rows drive brier sum -0.7798092966370004 over 76 rows.
- Weak raw 50-60 rows contribute brier sum -0.8904166418049997 over 36 rows.
- Weak-but-edge-kept rows are mostly unadjusted by the selected overlay; brier sum -0.8807363632099998.
- Strong-raw thin-edge rows still benefited from sharpening; brier sum 0.09700876493399982.
- Target-coverage PnL attribution: direction-wrong rows are 48 rows for -5007.0c; side-won negative-PnL rows are 2 rows for -52.0c.
- Boundary-entropy FV diagnostic best is entropy_book_s100 with Brier/logloss -0.011616674934007004/-0.02398221407513712; best target-coverage bridge None net Nonec, so entropy shrink is diagnostic rather than stronger than book-anchor right now.
- Danger-zone entry valve has 322.0c discovery P&L lift but entry robustness pass is True; treat it as watched, not promotable.
- Danger-zone FV shrink has Brier/logloss deltas -0.011340997078595372/-0.0661185329043299 and FV robustness pass True.
- Target-coverage conservative FV best diagnostic variant is logit125_p60_calm_mid_or_p75 with Brier/logloss mean deltas -0.0022095221651635597/-0.008271439367388467; frozen forward evidence starts separately.
- P70 diagnostic jackknife pass is True with 0 failures; full Brier/logloss -0.0003773633313270222/-0.003571990138160214, worst Brier leave-out -0.00016725015284209776.
- P70 paired interval has 112 settled rows and 31 adjusted rows; Brier/logloss p95 0.0024900748554538173/0.004755180402661384.
- Confidence-temperature bakeoff best is hard_logit125_p72 with Brier/logloss -0.0013255736275738735/-0.006030666765288752; hard p70 is -0.0003773633313270222/-0.003571990138160214.
- P70 fragility stress: one adverse p75 row breaks interval evidence at count 1; one adverse p80 row breaks mean at count 1.
- P70 scale bakeoff best robustness-ranked scale is 1.05 with first adverse p80 break count 1; scale tuning has not solved fragility.
- P70 empirical-Bayes throttle best is p70_empirical_bayes_prior48 scale 1.0981012658227849 with Brier/logloss p95 0.0008474887950797044/0.0013279133000561657 and first adverse p80 break 1.
- P70 source split all best logit125_p75 over 112 rows with Brier/logloss -0.0015769093300218757/-0.00675303480588537.
- P70 source split approved_entry best logit125_p70 over 7 rows with Brier/logloss -0.005753117335864851/-0.03925202238843982.
- P70 source split rejected_actionable best logit125_p75 over 105 rows with Brier/logloss -0.0012984954629656775/-0.004586435633715074.
- Frozen p70 runway has denominator/selected/base-seen 135/97/133; current zero rows are explained by target-policy abstention if selected remains 0.
- Frozen p70 empirical-Bayes runway has denominator/selected/base-seen 132/96/130.
- Frozen p70 quality registry has denominator/target-entries/p70-rows 131/95/24.
- hard_p70 pending sensitivity: pending-adjusted 0, settled-adjusted 25, raw-only losses 39.
- empirical_bayes_p70 pending sensitivity: pending-adjusted 0, settled-adjusted 25, raw-only losses 38.
- Approved-entry book FV robustness has 173 actual rows; full Brier/logloss deltas -0.004816693669815029/-0.048654430823182764, bootstrap p95 0.010699206867728323/0.02821750921046068, blockers ['leave_one_market_failure', 'bootstrap_brier_p95_not_negative', 'bootstrap_logloss_p95_not_negative'].
- Approved-entry book/raw blend best alpha is 0.35; Brier/logloss deltas -0.007791697570985245/-0.057993896385894306, bootstrap p95 0.0035903825386584265/0.009404569721470635.
- Frozen approved-entry book FV has entries/settled 133/133; Brier/logloss deltas 0.006168655138428583/-0.025019035845109228.
- Frozen path-state p70 has denominator/entries/settled 129/94/94; path_state_guarded_p70_logit125 Brier/logloss -0.00021098173948253023/-0.002381742406517639.
- Frozen boundary-recross shrink has denominator/entries/settled 128/93/93; boundary_recross_shrink_probability Brier/logloss -0.006721901187172044/-0.014189908647494757.
- Boundary reversal diagnostic found 24/42 boundary rows with opposite replacements; replacement-only net -106.0c and non-boundary-plus-replacement coverage 61.8421052631579.
- Danger-tag replacement diagnostic found 33/37 replacements; target net -606.0c versus replacement net -271.0c.
- Coverage-repair diagnostic removes toxic rows and repairs from missed markets: target net -606.0c versus candidate net -513.0c at coverage 75.0.
- Danger-repair bakeoff best diagnostic variant is paid_price_fragile_only with net -140.0c and coverage 75.0; realized-order repair rows make this diagnostic only.
- Ex-ante repair scoring best is highest_raw_edge with net -170.0c, coverage 75.29411764705883, and delta 674.0c; it is frozen separately as low-recross repair.
- Boundary-clock hazard repair best diagnostic rule is early_boundary_recross with net 541.0c, coverage 75.177304964539, and removed-row net -1014.0c; it is frozen separately for future-only validation.
- Boundary-clock robustness pass is True; worst leave-one delta 685.0c and pending-adverse delta 819.0c.
- Boundary-clock FV diagnostic best overlay is clock_shrink_0p00 with Brier/logloss deltas -0.010892657298312514/-0.02374336772308172 over 112 settled rows.
- Boundary-clock FV robustness pass is True; worst leave-one Brier/logloss means -0.007478313623666667/-0.01570564313807691.
- Boundary-clock residual attribution: clock hazard explains 26 direction-wrong rows for -2896.0c; residual non-clock errors are 22 rows for -2111.0c.
- Frozen boundary-clock residual registry has denominator/entries/settled/net 120/9/9/-167.0c; registry only, not a candidate.
- Side-asymmetry diagnostic top bucket is side:no|p60_70 with settled 27, net -888.0c, avg p 0.632525037037037, and win rate 0.4074074074074074; registry-only until future rows validate it.
- Frozen side-asymmetry registry has denominator/bucket/non-clock settled 118/6/6; net -187.0c, registry only.
- Side-asymmetry FV overlay diagnostic best is clock_then_side_no_midboundary_0p00 with Brier/logloss deltas -0.016270297254624977/-0.03486722952707222 and adjusted rows 57.
- Frozen side-asymmetry FV overlay has denominator/entries/settled/adjusted 118/87/87/43; Brier/logloss -0.011711620895563213/-0.024525492188571918, blockers [].
- Boundary-clock promotion runway ready=False with 3 frozen promotion blockers; FV/entry robustness True/True.
- Boundary-clock FV entry bridge diagnostic best floor 0.02 has net 425.0c, coverage 75.0, and delta 766.0c.
- Frozen edge-phase shrink has denominator/entries/settled 127/93/93; edge_phase_shrink Brier/logloss -0.005422811682086021/-0.01160240490360638.
- Adjusted-FV edge gate diagnostic best positive row is confidence_leak_shrink floor 0.02 with coverage 42.10526315789474, net 689.0c, blockers ['coverage_too_low'].
- Edge-gate opposite-side diagnostic found 1/1 skips with a same-or-later opposite replacement; kept-plus-replacement coverage 73.6842105263158 and net -424.0c, blockers ['coverage_too_low', 'net_not_positive'].
- Frozen edge-phase edge gate has denominator/base/candidate 126/92/92; coverage 73.01587301587301, net -695.0c.
- Frozen edge-gate opposite replacement has denominator/entries/replacements 125/91/0; coverage 72.8, net -585.0c.
- Frozen low-recross repair entry has denominator/entries/settled 122/92/92; coverage 75.40983606557377, net -217.0c, blockers ['net_not_positive'].
- Frozen high-raw-p repair entry has denominator/entries/settled 118/89/89; coverage 75.42372881355932, net -274.0c, blockers ['net_not_positive'].
- Frozen boundary-clock repair entry has denominator/entries/settled 121/91/91; coverage 75.20661157024793, net -151.0c, blockers ['net_not_positive'].
- Frozen boundary-clock FV overlay has denominator/entries/settled/adjusted 120/88/88/38; Brier/logloss -0.007305008905659105/-0.015397418335031166, blockers [].
- Frozen boundary-clock FV entry bridge has denominator/entries/settled/net 119/90/90/229.0c, blockers [].

## Candidates

| family | candidate | complexity | fwd entries | fwd settled | coverage | fit | fwd brier d | fwd logloss d | disc brier d | jackknife | blockers |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|---|
| book_anchor | book_probability | 1 | 150 | 150 | 98.684211 | high | -0.012290 | -0.022481 | -0.006549 | None | forward_coverage_too_high, forward_bucket_failure, forward_path_contradiction_loss |
| side_asymmetry_fv_overlay | clock_then_side_no_midboundary_0p00 | 5 | 87 | 87 | 73.728814 | low | -0.011712 | -0.024525 | None | None | settled_lt_30 |
| approved_entry_book_raw_blend | book_plus_alpha_raw_memory_alpha_0.35 | 2 | 173 | 173 | None | actual-approved-diagnostic | -0.007792 | -0.057994 | -0.007792 | True | bootstrap_brier_p95_not_negative, bootstrap_logloss_p95_not_negative |
| boundary_clock_fv_overlay | clock_shrink_0p00 | 4 | 88 | 88 | 73.333333 | low | -0.007305 | -0.015397 | None | None | settled_lt_30 |
| boundary_recross_shrink_fv | boundary_recross_shrink_probability | 3 | 93 | 93 | 72.656250 | low | -0.006722 | -0.014190 | -0.007141 | None | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| edge_phase_shrink_fv | edge_phase_shrink | 4 | 93 | 93 | 73.228346 | low | -0.005423 | -0.011602 | -0.006876 | None | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| danger_zone_fv | danger_to_book | 2 | 142 | 142 | None | approved-entry-only | -0.004052 | -0.052748 | -0.011341 | True | settled_lt_30 |
| rmt_shrink | noise_shrink_light_probability | 2 | 150 | 150 | 98.684211 | high | -0.002682 | -0.005112 | -0.001502 | None | forward_coverage_too_high, forward_bucket_failure, forward_path_contradiction_loss |
| target_coverage_conservative_fv | logit125_p60_calm_mid_or_p75 | 3 | 98 | 98 | 72.058824 | low | -0.001999 | -0.006824 | -0.002210 | None | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| path_state_p70_fv | path_state_guarded_p70_logit125 | 3 | 94 | 94 | 72.868217 | low | -0.000211 | -0.002382 | None | None | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| target_coverage_p70_fv | logit125_p70 | 2 | 97 | 97 | 71.851852 | low | 0.000357 | -0.000877 | -0.000377 | True | mean_brier_not_better, brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| reward_memory | reward_memory_logit125 | 4 | 140 | 140 | 98.591549 | high | 0.002598 | 0.004289 | 0.001503 | False | brier_not_better_than_raw, logloss_not_better_than_raw |
| boundary_memory | boundary_memory_logit125 | 3 | 141 | 141 | 98.601399 | high | 0.002722 | 0.004142 | 0.001589 | None | brier_not_better_than_raw, logloss_not_better_than_raw |
| selective_memory | entry_conditioned_logit125_p60_only_probability | 2 | 150 | 150 | 98.684211 | high | 0.002981 | 0.004515 | 0.002341 | None | forward_coverage_too_high, forward_brier_not_better_than_raw, forward_logloss_not_better_than_raw, discovery_brier_not_better_than_raw, discovery_logloss_not_better_than_raw, forward_bucket_failure, forward_path_contradiction_loss |
| selective_memory | entry_conditioned_logit125_probability | 2 | 150 | 150 | 98.684211 | high | 0.003344 | 0.005195 | 0.002276 | None | forward_coverage_too_high, forward_brier_not_better_than_raw, forward_logloss_not_better_than_raw, discovery_brier_not_better_than_raw, discovery_logloss_not_better_than_raw, forward_bucket_failure, forward_path_contradiction_loss |
| boundary_memory | conditional_logit125_p60_only | 2 | 141 | 141 | 98.601399 | high | 0.003660 | 0.006272 | 0.002341 | None | brier_not_better_than_raw, logloss_not_better_than_raw |
| reward_memory | logit125_probability | 2 | 140 | 140 | 98.591549 | high | 0.003772 | 0.006422 | 0.002276 | False | brier_not_better_than_raw, logloss_not_better_than_raw |
| danger_zone_fv | book_probability | 1 | 142 | 142 | None | approved-entry-only | 0.004996 | -0.026165 | -0.004817 | True | brier_not_better_than_raw |
| boundary_memory | boundary_memory_plus05 | 3 | 141 | 141 | 98.601399 | high | 0.005380 | 0.009566 | 0.003419 | None | brier_not_better_than_raw, logloss_not_better_than_raw |
| approved_entry_book_fv | book_probability_on_actual_approved_entries | 1 | 133 | 133 | None | actual-approved-only | 0.006169 | -0.025019 | None | None | brier_not_better_than_raw |
| reward_memory | reward_memory_plus05 | 4 | 140 | 140 | 98.591549 | high | 0.007700 | 0.014561 | 0.004831 | False | brier_not_better_than_raw, logloss_not_better_than_raw |
| simple_posterior | entry_conditioned_plus05_probability | 1 | 150 | 150 | 98.684211 | high | 0.009704 | 0.018232 | 0.006406 | None | forward_coverage_too_high, forward_brier_not_better_than_raw, forward_logloss_not_better_than_raw, discovery_brier_not_better_than_raw, discovery_logloss_not_better_than_raw, forward_bucket_failure, forward_path_contradiction_loss |
| reward_memory | plus05_probability | 1 | 140 | 140 | 98.591549 | high | 0.009964 | 0.019161 | 0.006406 | False | brier_not_better_than_raw, logloss_not_better_than_raw |
| approved_entry_conditional_book_fv | conditional_book_no_late_discount | 3 | 93 | 93 | None | actual-approved-only | 0.013952 | 0.030692 | -0.025583 | None | brier_not_better_than_raw, logloss_not_better_than_raw |
| approved_entry_book_edge_actionability | skip_discount15_book_edge_lt_5pp | 2 | 112 | 112 | 84.210526 | target | None | None | None | None | entry_actionability_not_fv_calibration |
| frozen_approved_entry_book_edge_gate | skip_discount15_book_edge_lt_5pp | 2 | 88 | 71 | 80.681818 | target | None | None | None | None | settled_lt_30 |
| frozen_target_coverage_book_edge_gate | target_coverage_skip_raw_edge_ge_15pp | 2 | 60 | 60 | 61.855670 | low | None | None | None | None | coverage_too_low, delta_not_positive |
| edge_phase_edge_gate | edge_phase_shrink_floor_-0.12 | 4 | 92 | 92 | 73.015873 | low | None | None | None | None | coverage_too_low, net_not_positive |
| edge_gate_opposite_side | edge_phase_skip_then_same_or_later_opposite | 5 | 91 | 91 | 72.800000 | low | None | None | None | None | coverage_too_low, net_not_positive |
| low_recross_repair_entry | skip_paid_or_weak_boundary_repair_lowest_recross | 5 | 92 | 92 | 75.409836 | target | None | None | None | None | net_not_positive |
| boundary_clock_repair_entry | skip_boundary_clock_composite_repair_lowest_recross | 5 | 91 | 91 | 75.206612 | target | None | None | None | None | net_not_positive |
| high_raw_p_repair_entry | skip_paid_or_weak_boundary_repair_highest_raw_p | 5 | 89 | 89 | 75.423729 | target | None | None | None | None | net_not_positive |
| boundary_clock_fv_entry_bridge | boundary_clock_adjusted_edge_floor_0p02_repair_lowest_recross | 5 | 90 | 90 | 75.630252 | target | None | None | None | None | settled_lt_30 |
| side_asymmetry_fv_entry_bridge | target_coverage_side_asymmetry_adjusted_edge2pp_strict_farthest_boundary_repair | 6 | 72 | 72 | 75.000000 | target | None | None | None | None | settled_lt_30 |

## Target-Coverage FV View

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Forward denominator: `152`

| overlay | entries | settled | coverage | W/L | brier d | logloss d | net c | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| book_probability | 112 | 112 | 73.684211 | 64/48 | -0.014913 | -0.026989 | -626.000000 | coverage_too_low |
| boundary_recross_shrink_probability | 112 | 112 | 73.684211 | 64/48 | -0.007141 | -0.015609 | -626.000000 | coverage_too_low |
| noise_shrink_light_probability | 112 | 112 | 73.684211 | 64/48 | -0.002909 | -0.005475 | -626.000000 | coverage_too_low |
| raw_probability | 112 | 112 | 73.684211 | 64/48 | 0.000000 | 0.000000 | -626.000000 | coverage_too_low |
| entry_conditioned_logit125_probability | 112 | 112 | 73.684211 | 64/48 | 0.003823 | 0.005634 | -626.000000 | coverage_too_low, brier_not_better_than_raw, logloss_not_better_than_raw |
| entry_conditioned_logit125_p60_only_probability | 112 | 112 | 73.684211 | 64/48 | 0.003992 | 0.006047 | -626.000000 | coverage_too_low, brier_not_better_than_raw, logloss_not_better_than_raw |
| entry_conditioned_plus03_probability | 112 | 112 | 73.684211 | 64/48 | 0.005840 | 0.010292 | -626.000000 | coverage_too_low, brier_not_better_than_raw, logloss_not_better_than_raw |

## Target-Coverage Sequential Evidence

- Overlay: `book_probability`
- Settled rows: `112`
- Brier mean/p95/prob-negative: `-0.014913/0.000643/0.942200`
- Logloss mean/p95/prob-negative: `-0.026989/0.005781/0.914000`
- Blockers: `brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative, coverage_below_75`

## Target-Coverage p70 Sequential Evidence

- Variant: `logit125_p70`
- Settled/adjusted rows: `112/31`
- Brier mean/p95/prob-negative: `-0.000377/0.002490/0.602200`
- Logloss mean/p95/prob-negative: `-0.003572/0.004755/0.763000`
- Blockers: `brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative, coverage_below_75`

## Confidence Temperature Bakeoff

- Best variant: `hard_logit125_p72`

| variant | rows | adjusted | brier mean | brier p95 | logloss mean | logloss p95 | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| hard_logit125_p72 | 112 | 28 | -0.001326 | 0.001015 | -0.006031 | 0.001355 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| smooth_logit_ramp_70_90 | 112 | 31 | -0.000899 | 0.000026 | -0.004506 | -0.001260 | brier_interval_not_strictly_negative |
| smooth_logit_ramp_65_85 | 112 | 45 | -0.000802 | 0.000731 | -0.004616 | 0.000340 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| heat_gated_hard_p70 | 112 | 31 | -0.000409 | 0.002279 | -0.003671 | 0.004465 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| hard_logit125_p70 | 112 | 31 | -0.000377 | 0.002389 | -0.003572 | 0.004690 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| heat_gated_smooth_60_80 | 112 | 76 | -0.000165 | 0.002008 | -0.003238 | 0.003634 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |

## p70 Fragility Stress

- Base rows/adjusted rows: `112/31`
- First breaks: `{'0.7': {'first_interval_break_count': 1, 'first_mean_break_count': 1}, '0.75': {'first_interval_break_count': 1, 'first_mean_break_count': 1}, '0.8': {'first_interval_break_count': 1, 'first_mean_break_count': 1}, '0.85': {'first_interval_break_count': 1, 'first_mean_break_count': 1}, '0.9': {'first_interval_break_count': 1, 'first_mean_break_count': 1}}`

## p70 Scale Bakeoff

- Best scale: `1.05`

| scale | brier mean | brier p95 | logloss mean | logloss p95 | first any break |
|---:|---:|---:|---:|---:|---:|
| 1.050000 | -0.000197 | 0.000387 | -0.001079 | 0.000611 | 1 |
| 1.100000 | -0.000326 | 0.000853 | -0.001965 | 0.001417 | 1 |
| 1.150000 | -0.000395 | 0.001330 | -0.002670 | 0.002337 | 1 |
| 1.200000 | -0.000409 | 0.001736 | -0.003202 | 0.003215 | 1 |
| 1.250000 | -0.000377 | 0.002438 | -0.003572 | 0.004708 | 1 |
| 1.300000 | -0.000304 | 0.002915 | -0.003789 | 0.005962 | 1 |

## p70 Empirical Bayes

- Best variant: `p70_empirical_bayes_prior48`

| variant | scale | brier mean | brier p95 | logloss mean | logloss p95 | first break |
|---|---:|---:|---:|---:|---:|---:|
| p70_empirical_bayes_prior48 | 1.098101 | -0.000322 | 0.000847 | -0.001935 | 0.001328 | 1 |
| p70_empirical_bayes_prior24 | 1.140909 | -0.000386 | 0.001251 | -0.002555 | 0.002246 | 1 |
| p70_empirical_bayes_prior12 | 1.180233 | -0.000410 | 0.001674 | -0.003011 | 0.003017 | 1 |
| p70_empirical_bayes_prior6 | 1.209459 | -0.000407 | 0.001904 | -0.003284 | 0.003747 | 1 |

## p70 Empirical Bayes Runway

- Future denominator/selected/base-seen: `132/96/130`
- Coverage: `72.727273`
- Base opportunity summary: `{'base_rows': 130, 'eb_adjustable_unselected': 0, 'high_recross_miss_ge_75': 82, 'missing_raw': 0, 'near_edge_miss_lt_2pp': 45, 'raw_60_70_boundary': 39, 'raw_ge_70_eb_adjustable': 25, 'raw_lt_60': 66, 'selected_rows': 96}`
- Frozen empirical-Bayes p70 has 96 selected markets, 34 markets with base rows that failed the target policy, and 2 markets with no target base row.
- Base rows by raw-probability bucket: <60=66, 60-70 boundary=39, >=70 EB-adjustable=25.
- Unselected EB-adjustable rows: 0; if this stays 0, the blocker is opportunity, not EB probability scoring.

## p70 Quality Registry

- Future denominator/target entries/p70 rows/settled p70: `131/95/24/24`

| tag | rows | settled | W/L | net c | avg raw p |
|---|---:|---:|---:|---:|---:|
| late_or_extreme_time | 14 | 14 | 11/3 | 165.000000 | 0.766282 |
| book_discount_ge_4pp | 13 | 13 | 11/2 | 245.000000 | 0.813594 |
| calm_recross | 10 | 10 | 8/2 | -13.000000 | 0.843456 |
| middle_time_120_720s | 10 | 10 | 8/2 | 12.000000 | 0.828375 |
| boundary_geometry | 9 | 9 | 5/4 | -206.000000 | 0.725060 |
| thin_edge_lt_3pp | 8 | 8 | 5/3 | -199.000000 | 0.753458 |
| deep_geometry | 5 | 5 | 5/0 | 78.000000 | 0.912030 |
| turbulent_recross | 4 | 4 | 2/2 | -143.000000 | 0.739078 |
| expensive_ask_ge_85c | 2 | 2 | 2/0 | 11.000000 | 0.948491 |

## p70 Pending Sensitivity

| validator | entries | pending adjusted | settled adjusted | raw-only losses |
|---|---:|---:|---:|---:|
| hard_p70 | 97 | 0 | 25 | 39 |
| empirical_bayes_p70 | 96 | 0 | 25 | 38 |

## Target-Coverage Attribution

- Strong raw-p>=60 rows drive brier sum -0.7798092966370004 over 76 rows.
- Weak raw 50-60 rows contribute brier sum -0.8904166418049997 over 36 rows.
- Weak-but-edge-kept rows are mostly unadjusted by the selected overlay; brier sum -0.8807363632099998.
- Strong-raw thin-edge rows still benefited from sharpening; brier sum 0.09700876493399982.

## Requirements

- fixed raw-v28 p50 entry comparison for FV-only overlays
- future-only validation after each freeze timestamp
- at least 30 settled forward rows before promotion
- target coverage 75-90% in broad-entry strategy views
- Brier and logloss improvement versus raw
- prefer simpler candidate when evidence is comparable
