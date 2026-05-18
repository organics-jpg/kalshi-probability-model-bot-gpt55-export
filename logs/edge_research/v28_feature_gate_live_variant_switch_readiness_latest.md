# v28 Feature-Gate Live Variant Switch Readiness

Research-only. No live bot logic changes, no process control, no orders.

- Generated UTC: `2026-05-07T18:23:12.226080+00:00`
- Decision: `ask35_is_better_watch_candidate_not_live_promoted`
- Live action recommendation: `do_not_switch_without_user_confirmation`
- Decision reasons: `ask35_has_higher_post_freeze_net_than_ask65, ask35_source_quality_is_clean, ask35_keeps_cheap_tail_floor_above_35c, coverage_still_below_75pct_so_not_promotable, active_ask65_live_test_is_not_collecting_fill_data_yet`

## Candidate Comparison

| candidate | settled | W/L | coverage | net c | recon | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| active ask65 | 47 | 42/5 | 57.317073 | 344.000000 | 0.042553 | 3 | coverage_too_low |
| broader ask35 | 52 | 48/4 | 63.414634 | 514.000000 | 0.134615 | 5 | coverage_too_low |
| no ask reference | 55 | 39/16 | 67.073171 | 445.000000 | 0.272727 | 4 | coverage_too_low |

## Live Gate Context

- no_ask: pass_count `3`, sides `{'no': 3}`, markets `['KXBTC15M-26MAY071415-15']`
- frontier_ask35: pass_count `0`, sides `{}`, markets `[]`
- frontier_ask45: pass_count `0`, sides `{}`, markets `[]`
- ask55: pass_count `0`, sides `{}`, markets `[]`
- ask65: pass_count `0`, sides `{}`, markets `[]`

## Interpretation

- ask65 is cleanest but too selective; it currently has no fills.
- ask35 is the best clean broader frontier row but remains below the broad-market coverage gate.
- The current live market had no frontier ask35 counterfactual passes, so switching would not have created a trade in the latest observed window.
