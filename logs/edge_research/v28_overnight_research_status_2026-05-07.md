# v28 Overnight Research Status - 2026-05-07

Research-only. No live candidate trades placed, no live bot logic edited, and live bot processes were not stopped or restarted.

## Fresh Baseline

- Live strategy: `live_mushroom_v28_size2`
- Live-only PnL: `+629c / +$6.29`
- Entries / completed round trips: `547 / 451`
- W/L by sign: `256/284`
- Open positions: `0`
- Controlled live-test gate: `no_live_test`
- Candidate rows tracked: `755`
- Live-ready candidates: `0`
- Broad eligible / sidecar eligible: `0 / 0`

Updated after the broad delayed-recheck composition:

- Candidate rows tracked: `760`
- Positive candidates: `543`
- Positive target-coverage candidates: `319`
- Live-ready candidates: `0`
- Controlled live-test gate remains: `no_live_test`

## Top Current Candidates By PnL

| rank | gate | policy | settled | W/L | coverage | pnl | delta vs live | status |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | `soft_frontier_midprice_delayed_recheck_rescue` | `diagnostic_prefreeze_context_diagnostic_entry_quarter_midprice_boundary_latest_delay60_bid_ge60_drop_lte11` | 54 | 47/7 | 78.41% | +1398c | +768c | Top diagnostic; freshly frozen child has 0 post-birth rows |
| 2 | `soft_frontier_midprice_delayed_recheck_exit` | `diagnostic_prefreeze_context_diagnostic_entry_quarter_midprice_boundary_latest_delay60_bid_ge60_drop_lte10` | 54 | 46/8 | 78.41% | +1298c | +668c | Strong base diagnostic; freshly frozen child has 0 post-birth rows |
| 3 | `soft_frontier_midprice_boundary_dual_exit_guard` | `diagnostic_bridge_quarter_midprice_boundary_or_reduce_p_hold80` | 52 | 45/7 | 79.52% | +1214c | +585c | Watch-only; diagnostic/pre-strict stack blockers |
| 4 | `soft_frontier_midprice_boundary_dual_exit_guard` | `diagnostic_entry_quarter_midprice_boundary_or_reduce_p_hold80` | 54 | 46/8 | 80.00% | +1196c | +567c | Watch-only; diagnostic/pre-strict stack blockers |
| 5 | `soft_frontier_midprice_boundary_dual_exit_stack` | `diagnostic_bridge_quarter_midprice_boundary_book_gap_or_clip` | 45 | 39/6 | 80.28% | +1116c | +487c | Watch-only; post-stack rows/suppressions short |
| 6 | `soft_frontier_midprice_boundary_exit_stack` | `diagnostic_entry_quarter_midprice_boundary_book_gap_weighted_exit_stack` | 51 | 43/8 | 78.41% | +1066c | +437c | Watch-only; joined exit runway short |
| 7 | `frozen_feature_gate_value_exit_watch` | `diagnostic_prefreeze_context_suppress_value_over_hold` | 20 | 12/8 | n/a | +1000c | +371c | Diagnostic selected-side overlap only |
| 8 | `composite_false_conviction_fv` | `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + composite_false_conviction_full_to_50` | 56 | 35/21 | 72.73% | +388c | -241c | Sidecar-ish; does not beat live baseline |
| 9 | `phi_forgetting_fv` | `phi_forget_logit125` | 55 | 33/22 | 98.21% | +339c | -290c | Too broad / below live |
| 10 | `boundary_clock_feature_gate_continuous_penalty` | `post_penalty_birth_bridge_cheap_penalty025_rank_only` | 29 | 22/7 | 65.91% | +312c | -317c | One row short, under-covered, below live |

## New Exit-State Finding

The strongest new mechanism is still exit/state repair, not fresh entry filtering. High-exit-bid suppression looked huge diagnostically (`+2536c`, 14 helpful suppressed exits / 0 harmful), but path audit found real survival risk after the exit: worst post-exit bid mark was `-56c`, with adverse rows at 10/25/50c = `5/4/3`.

I froze the first safer child:

- Candidate: `feature_gate_exit_bid_delayed_recheck / delay60_bid_ge60_drop_lte10`
- Freeze: `2026-05-07T07:54:52.452489+00:00`
- Diagnostic prefreeze: 14 rows, 11 suppressed, 11 helpful / 0 harmful, candidate `+2236c`, delta `+2272c`, W/L `13/1`, cushion `22`
- Strict post-birth: 0 rows, 0 suppressed, 0c
- Status: good mechanism target, not live-ready

I also added and froze a broader composition:

- Candidate: `soft_frontier_midprice_delayed_recheck_exit / diagnostic_entry_quarter_midprice_boundary_latest_delay60_bid_ge60_drop_lte10`
- Freeze: `2026-05-07T08:05:51.308715+00:00`
- Diagnostic prefreeze: 54 joined rows, 30 suppressions, 28 helpful / 0 harmful, candidate `+1297.5c`, W/L `46/8`, coverage `78.41%`, reconstructed share `16.7%`, cushion `12`
- Path-risk diagnostic: 30/30 suppressed rows had post-recheck heartbeat path; worst post-exit excursion `-25c`, worst post-recheck excursion `-17c`, adverse post-recheck 10/25/50c rows `1/0/0`
- Residual diagnostic losses: all 8 losses are unsuppressed; 4 are correct loss-control exits, 4 are false-negative suppression misses worth up to `522c` of recoverable hold-vs-exit value, but they overlap low p_hold / large FV drawdown conditions.
- Rescue relax audit: `drop15_bid60` improves diagnostic net to `+1461.5c` with helpful/harmful `30/0`, but path risk worsens to worst post-recheck excursion `-54c` with adverse 10/25/50c rows `2/1/1`; do not freeze this relax without a disaster guard.
- Disaster-guard audit: after-recheck emergency stops cannot cleanly repair `drop15_bid60`. The best guarded variants give back most of the improvement and still see the same `-54c` heartbeat gap before the guard can act. The correct repair is to avoid admitting that row.
- Clean rescue frozen: `soft_frontier_midprice_delayed_recheck_rescue / delay60_bid_ge60_drop_lte11` keeps the one clean false-negative recovery, excludes the scary `drop12` row, and has diagnostic `+1397.5c`, W/L `47/7`, 31 suppressions, 29 helpful / 0 harmful, reconstructed share `16.7%`, cushion `13`.
- Clean rescue path-risk diagnostic: 31/31 suppressed rows had post-recheck path; worst post-exit excursion `-25c`, worst post-recheck excursion `-17c`, adverse post-recheck 10/25/50c rows `1/0/0`; no path-risk blockers in diagnostic context.
- Strict post-birth: 0 rows, 0 suppressions, 0c
- Status: strongest diagnostic blend so far, not live-ready until post-birth rows arrive

## Tracking Coverage

The full all-candidates table now includes the previously missing RMT/catastrophic-forgetting families and the new delayed-recheck child. Current counts:

- RMT forgetting entry lanes: `32`
- Path/RMT fresh-gate lanes: `4`
- Boundary-memory FV lanes: `3`
- Phi-forgetting FV lanes: `5`
- Reward-memory FV lanes: `4`
- Feature-gate exit-bid delayed-recheck lanes: `1`
- Soft-frontier mid-price delayed-recheck exit lanes: `2`
- Soft-frontier mid-price delayed-recheck rescue lanes: `2`

## Next Work

1. Let the frozen delayed-recheck and value-exit side guards collect post-birth rows.
2. Keep the live-test gate closed until a candidate has strict post-freeze rows, positive PnL after fees, enough suppressions/trades, full-loss cushion >=3, and beats the refreshed live baseline.
3. Continue mixing the best broad entry family (`soft_frontier_midprice_boundary_shrink`) with the safest observable exit repair family, but treat all current top rows as diagnostic until the post-stack sample catches up.
