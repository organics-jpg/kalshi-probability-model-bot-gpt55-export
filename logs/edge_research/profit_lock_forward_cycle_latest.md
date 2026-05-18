# Profit Lock Forward Cycle

Generated UTC: `20260504_075119Z`

## Scope

- Research-only one-shot cycle; no orders are submitted and no bot files or live processes are touched.
- Runs refresh and validators for existing locked EV candidates, including separate combo price-guard and path-confirmation locks.
- Does not run optimizers and does not update locks.

## Command Results

| step | return code | stdout tail | stderr tail |
|---|---:|---|---|
| `pending_signal_monitor` | 0 | Profit lock pending signal monitor complete<br>new_records=0 registered=972<br>removed_post_close_records=0<br>report=logs\edge_research\profit_lock_pending_signal_monitor_latest.md |  |
| `path_pending_monitor` | 0 | Kinetic path-confirmation pending monitor complete<br>new_records=0 registered=56<br>removed_post_close_records=0<br>report=logs\edge_research\kinetic_path_confirmation_pending_monitor_latest.md |  |
| `original_fresh` | 0 | Profit frontier fresh validation complete<br>fresh_markets=124 fresh_base=125<br>report=logs\edge_research\profit_frontier_fresh_validation_latest.md |  |
| `frontier_v2_fresh` | 0 | Profit frontier v2 fresh validation complete<br>fresh_markets=67 fresh_base=67<br>report=logs\edge_research\profit_frontier_v2_fresh_validation_latest.md |  |
| `frontier_locked_policy_validation` | 0 | frontier_v2_continuous: strict_fresh_markets=38 fresh_base=39 fresh_net=-249.0c<br>book_margin: strict_fresh_markets=37 fresh_base=38 fresh_net=132.0c<br>book_margin_early: strict_fresh_markets=33 fresh_base=34 fresh_net=102.0c<br>book_margin_gap015: strict_fresh_markets=27 fresh_base=28 fresh_net=-44.0c<br>book_margin_adverse100: strict_fresh_markets=14 fresh_base=15 fresh_net=-167.0c<br>book_margin_delayed_adv100_brownian55: strict_fresh_markets=14 fresh_base=15 fresh_net=-179.0c<br>score_min60: strict_fresh_markets=37 fresh_base=38 fresh_net=-87.0c<br>score_min60_gap020: strict_fresh_markets=26 fresh_base=27 fresh_net=-83.0c |  |
| `book_to_score_wait_validation` | 0 | Book-to-score wait forward validation complete<br>book_early_score_gap020_wait: strict_fresh_markets=23 fresh_base=24 fresh_net=-137.0c report=logs\edge_research\profit_book_early_score_gap020_wait_validation_latest.md<br>book_score_gap020_wait: strict_fresh_markets=20 fresh_base=21 fresh_net=-218.0c report=logs\edge_research\profit_book_score_gap020_wait_validation_latest.md |  |
| `book_hour04_v2_switch_validation` | 0 | Book hour04 V2 switch forward validation complete<br>strict_fresh_markets=16 fresh_base=17 fresh_net=-147.0c<br>report=logs\edge_research\profit_book_hour04_v2_switch_validation_latest.md |  |
| `book_refmargin_score_switch_validation` | 0 | Book reference-margin score switch forward validation complete<br>strict_fresh_markets=13 fresh_base=14 fresh_net=-18.0c<br>report=logs\edge_research\profit_book_refmargin_score_switch_validation_latest.md |  |
| `challenger_fresh` | 0 | Profit challenger fresh validation complete<br>fresh_markets=114 fresh_base=124<br>report=logs\edge_research\profit_challenger_fresh_validation_latest.md |  |
| `touch_hazard_fresh` | 0 | Profit touch-hazard fresh validation complete<br>fresh_markets=119 fresh_base=121<br>report=logs\edge_research\profit_touch_hazard_fresh_validation_latest.md |  |
| `touch_overlay_fresh` | 0 | Profit touch-hazard overlay fresh validation complete<br>fresh_markets=108 fresh_base=114<br>report=logs\edge_research\profit_touch_hazard_overlay_fresh_validation_latest.md |  |
| `kinetic_touch_fresh` | 0 | Profit kinetic-touch fresh validation complete<br>fresh_markets=112 fresh_base=112<br>report=logs\edge_research\profit_kinetic_touch_fresh_validation_latest.md |  |
| `hazard_mean_touch80_fresh` | 0 | Hazard-mean touch80 fresh validation complete<br>fresh_markets=4 fresh_base=4<br>report=logs\edge_research\profit_hazard_mean_touch80_fresh_validation_latest.md |  |
| `logit_blend_edge10_fresh` | 0 | Logit blend edge10 fresh validation complete<br>fresh_markets=3 fresh_base=3<br>report=logs\edge_research\profit_logit_blend_edge10_fresh_validation_latest.md |  |
| `logit_blend_thresh55_edge15_fresh` | 0 | Logit blend threshold55 edge15 fresh validation complete<br>fresh_markets=1 fresh_base=1<br>report=logs\edge_research\profit_logit_blend_thresh55_edge15_fresh_validation_latest.md |  |
| `hazard_fallback_logit55_fresh` | 0 | Hazard fallback logit55 fresh validation complete<br>fresh_markets=0 fresh_base=0<br>report=logs\edge_research\profit_hazard_fallback_logit55_fresh_validation_latest.md |  |
| `hazard_fallback_logit55_wait8_fresh` | 0 | Hazard fallback logit55 fresh validation complete<br>fresh_markets=0 fresh_base=0<br>report=logs\edge_research\profit_hazard_fallback_logit55_wait8_fresh_validation_latest.md |  |
| `hazard_fallback_score60_fresh` | 0 | Hazard fallback score60 fresh validation complete<br>fresh_markets=0 fresh_base=0<br>report=logs\edge_research\profit_hazard_fallback_score60_fresh_validation_latest.md |  |
| `kinetic_guard_fresh` | 0 | Profit kinetic-guard fresh validation complete<br>fresh_markets=111 fresh_base=111<br>report=logs\edge_research\profit_kinetic_guard_fresh_validation_latest.md |  |
| `kinetic_price_guard_fresh` | 0 | Profit kinetic price-guard fresh validation complete<br>fresh_markets=96 fresh_base=110<br>report=logs\edge_research\profit_kinetic_price_guard_fresh_validation_latest.md |  |
| `kinetic_combo_price_guard_fresh` | 0 | Profit kinetic combo price-guard fresh validation complete<br>fresh_markets=68 fresh_base=83<br>report=logs\edge_research\profit_kinetic_combo_price_guard_fresh_validation_latest.md |  |
| `kinetic_path_confirm_fresh` | 0 | Profit kinetic path-confirmation fresh validation complete<br>fresh_markets=105 fresh_base=105<br>report=logs\edge_research\profit_kinetic_path_confirm_fresh_validation_latest.md |  |
| `market_denominator_audit` | 0 | Profit lock market-denominator audit complete<br>locks=30<br>coverage_fail=11<br>report=logs\edge_research\profit_lock_market_denominator_audit_latest.md |  |
| `registered_signal_readiness` | 0 | Profit lock registered-signal readiness complete<br>ready_count=0<br>report=logs\edge_research\profit_lock_registered_signal_readiness_latest.md |  |
| `sample_size` | 0 | Profit lock sample-size requirements complete<br>ready_count=0<br>report=logs\edge_research\profit_lock_sample_size_requirements_latest.md |  |
| `bayesian_ev` | 0 | Profit lock Bayesian EV monitor complete<br>ready_count=0<br>report=logs\edge_research\profit_lock_bayesian_ev_monitor_latest.md |  |
| `registered_signal_delta` | 0 | Profit lock registered-signal delta complete<br>changed=0<br>report=logs\edge_research\profit_lock_registered_signal_delta_latest.md |  |
| `registry_recompute_divergence` | 0 | Profit lock registry/recompute divergence audit complete<br>diff_count=393<br>material_diff_count=370<br>report=logs\edge_research\profit_lock_registry_recompute_divergence_latest.md |  |
| `strict_failure_attribution` | 0 | Profit lock strict failure attribution complete<br>resolved_rows=999 blockers=522<br>report=logs\edge_research\profit_lock_strict_failure_attribution_latest.md |  |

## Lock Summary

| lock | fresh selected/base | wins/losses | net P&L | coverage | Wilson ready | Bayesian ready |
|---|---:|---:|---:|---:|---|---|
| original | 71/129 | 45/26 | -233.0c | 0.5503875968992248 | False | False |
| frontier_v2 | 47/71 | 28/19 | -202.0c | 0.6619718309859155 | False | False |
| frontier_v2_continuous | 38/38 | 22/16 | -249.0c | 1.0 | False | False |
| book_margin | 37/37 | 27/10 | 132.0c | 1.0 | False | False |
| book_margin_early | 33/33 | 24/9 | 102.0c | 1.0 | False | False |
| book_margin_gap015 | 27/31 | 18/9 | -44.0c | 0.8709677419354839 | False | False |
| book_margin_adverse100 | 14/19 | 8/6 | -167.0c | 0.7368421052631579 | False | False |
| book_margin_delayed_adv100_brownian55 | 14/14 | 8/6 | -179.0c | 1.0 | False | False |
| book_hour04_v2_switch | 16/16 | 9/7 | -147.0c | 1.0 | False | False |
| book_refmargin_score_switch | 13/13 | 9/4 | -18.0c | 1.0 | False | False |
| score_min60 | 37/37 | 26/11 | -87.0c | 1.0 | False | False |
| score_min60_gap020 | 26/26 | 18/8 | -83.0c | 1.0 | False | False |
| book_early_score_gap020_wait | 23/23 | 15/8 | -137.0c | 1.0 | False | False |
| book_score_gap020_wait | 20/20 | 12/8 | -218.0c | 1.0 | False | False |
| v2_wait_score_min60_early | 36/36 | 25/11 | -100.0c | 1.0 | False | False |
| v2_wait_score_min60_brownian70_early | 32/32 | 23/9 | -27.0c | 1.0 | False | False |
| challenger | 66/128 | 42/24 | -252.0c | 0.515625 | False | False |
| touch_hazard | 76/125 | 43/33 | -297.0c | 0.608 | False | False |
| touch_overlay | 70/118 | 40/30 | -216.0c | 0.5932203389830508 | False | False |
| kinetic_touch | 67/116 | 43/24 | -344.0c | 0.5775862068965517 | False | False |
| hazard_mean_touch80 | 8/8 | 8/0 | 220.0c | 1.0 | False | False |
| logit_blend_edge10 | 7/7 | 4/3 | -31.0c | 1.0 | False | False |
| logit_blend_thresh55_edge15 | 5/5 | 4/1 | 43.0c | 1.0 | False | False |
| hazard_fallback_logit55 | 4/4 | 3/1 | 16.0c | 1.0 | False | False |
| hazard_fallback_logit55_wait8 | 0/0 | 0/0 | 0.0c | None | False | False |
| hazard_fallback_score60 | 0/0 | 0/0 | 0.0c | None | False | False |
| kinetic_guard | 61/115 | 42/19 | -85.0c | 0.5304347826086957 | False | False |
| kinetic_price_guard | 51/114 | 32/19 | -104.0c | 0.4473684210526316 | False | False |
| kinetic_combo_price_guard | 45/87 | 28/17 | -130.0c | 0.5172413793103449 | False | False |
| kinetic_path_confirm | 55/109 | 42/13 | 92.0c | 0.5045871559633027 | False | False |

## Registered Signal Summary

| lock | registered/resolved/pending | wins/losses | net P&L | resolved coverage | registered coverage | Wilson ready | Bayesian ready |
|---|---:|---:|---:|---:|---:|---|---|
| original | 72/71/1 | 45/26 | -233.0c | 0.5503875968992248 | 0.549618320610687 | False | False |
| frontier_v2 | 48/47/1 | 28/19 | -202.0c | 0.6619718309859155 | 0.6666666666666666 | False | False |
| frontier_v2_continuous | 39/38/1 | 22/16 | -249.0c | 1.0 | 1.0 | False | False |
| book_margin | 38/37/1 | 27/10 | 132.0c | 1.0 | 1.0 | False | False |
| book_margin_early | 34/33/1 | 24/9 | 102.0c | 1.0 | 1.0 | False | False |
| book_margin_gap015 | 28/27/1 | 18/9 | -44.0c | 0.8709677419354839 | 0.875 | False | False |
| book_margin_adverse100 | 15/14/1 | 8/6 | -167.0c | 0.7368421052631579 | 0.75 | False | False |
| book_margin_delayed_adv100_brownian55 | 15/14/1 | 8/6 | -179.0c | 1.0 | 1.0 | False | False |
| book_hour04_v2_switch | 17/16/1 | 9/7 | -147.0c | 1.0 | 1.0 | False | False |
| book_refmargin_score_switch | 14/13/1 | 9/4 | -18.0c | 1.0 | 1.0 | False | False |
| score_min60 | 38/37/1 | 26/11 | -87.0c | 1.0 | 1.0 | False | False |
| score_min60_gap020 | 27/26/1 | 18/8 | -83.0c | 1.0 | 1.0 | False | False |
| book_early_score_gap020_wait | 24/23/1 | 15/8 | -137.0c | 1.0 | 1.0 | False | False |
| book_score_gap020_wait | 21/20/1 | 12/8 | -218.0c | 1.0 | 1.0 | False | False |
| v2_wait_score_min60_early | 37/36/1 | 25/11 | -100.0c | 1.0 | 1.0 | False | False |
| v2_wait_score_min60_brownian70_early | 33/32/1 | 23/9 | -27.0c | 1.0 | 1.0 | False | False |
| challenger | 67/66/1 | 42/24 | -252.0c | 0.515625 | 0.5153846153846153 | False | False |
| touch_hazard | 77/76/1 | 43/33 | -297.0c | 0.608 | 0.6062992125984252 | False | False |
| touch_overlay | 71/70/1 | 40/30 | -216.0c | 0.5932203389830508 | 0.5916666666666667 | False | False |
| kinetic_touch | 68/67/1 | 43/24 | -344.0c | 0.5775862068965517 | 0.5811965811965812 | False | False |
| hazard_mean_touch80 | 9/8/1 | 8/0 | 220.0c | 1.0 | 1.0 | False | False |
| logit_blend_edge10 | 8/7/1 | 4/3 | -31.0c | 1.0 | 1.0 | False | False |
| logit_blend_thresh55_edge15 | 6/5/1 | 4/1 | 43.0c | 1.0 | 1.0 | False | False |
| hazard_fallback_logit55 | 5/4/1 | 3/1 | 16.0c | 1.0 | 1.0 | False | False |
| hazard_fallback_logit55_wait8 | 1/0/1 | 0/0 | 0.0c | None | 1.0 | False | False |
| hazard_fallback_score60 | 0/0/0 | 0/0 | 0.0c | None | None | False | False |
| kinetic_guard | 62/61/1 | 42/19 | -85.0c | 0.5304347826086957 | 0.5344827586206896 | False | False |
| kinetic_price_guard | 52/51/1 | 32/19 | -104.0c | 0.4473684210526316 | 0.45217391304347826 | False | False |
| kinetic_combo_price_guard | 46/45/1 | 28/17 | -130.0c | 0.5172413793103449 | 0.5227272727272727 | False | False |
| kinetic_path_confirm | 56/55/1 | 42/13 | 92.0c | 0.5045871559633027 | 0.509090909090909 | False | False |

## Strict Failure Attribution

- Strict resolved rows: 999
- Diagnostic blocker rows scanned: 522
- Positive blockers retaining >=80% of strict rows: 61

## Read

- Cycle completed, but 11 locks fail the strict registered recurring-market coverage audit.
