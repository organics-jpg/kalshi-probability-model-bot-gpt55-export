# v28 Dual-Lane Overlay Opportunity Audit

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:47:37.989322+00:00`
- Same-window compare UTC: `2026-05-11T03:47:37.865013+00:00`
- Promotion use: `diagnostic_only_overlay_design`
- Candidate policy: `post_dual_union_birth_entry_cheap_penalty025_rank_only`
- Current same-window delta: `-181c ($-1.81)`

## Read

- Dual-lane is not currently a live-v28 replacement.
- Its useful shape is as a possible risk-control overlay on markets where live v28 churns or loses.
- The blocker is winner capture: live v28 made large same-side gains on several markets that dual-lane clipped to small wins.
- A live-ready repair must preserve live v28's winner capture while using dual-lane only where it has forward evidence of reducing live loss clusters.

## Overlay Split

| split | rows | candidate net | live net | candidate-live | avg raw | avg ask | avg abs d | avg recross |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| helpful or no-live-pnl buckets | 8 | 251c ($2.51) | -188c ($-1.88) | 439c ($4.39) | 0.082 | 0.691 | 0.912 | 0.243 |
| harmful buckets | 7 | -30c ($-0.30) | 434c ($4.34) | -464c ($-4.64) | 0.087 | 0.810 | 1.113 | 0.331 |

## Bucket Summaries

| bucket | rows | candidate net | live net | candidate-live | components | sides |
|---|---:|---:|---:|---:|---|---|
| `candidate_right_but_live_captured_more` | 6 | 136c ($1.36) | 414c ($4.14) | -278c ($-2.78) | `{'strict_delayed_recheck_rescue:drop15_bid60': 1, 'strict_parent_midprice_hold_fill': 5}` | `{'no': 5, 'yes': 1}` |
| `candidate_wrong_or_exit_bad_live_won` | 1 | -166c ($-1.66) | 20c ($0.20) | -186c ($-1.86) | `{'strict_delayed_recheck_rescue:drop15_bid60': 1}` | `{'yes': 1}` |
| `candidate_not_better_than_live` | 1 | -162c ($-1.62) | -6c ($-0.06) | -156c ($-1.56) | `{'strict_delayed_recheck_rescue:drop15_bid60': 1}` | `{'no': 1}` |
| `candidate_vs_no_live_pnl` | 2 | 36c ($0.36) | 0c ($0.00) | 36c ($0.36) | `{'continuous_penalty:cheap_penalty025_rank_only': 1, 'strict_delayed_recheck_rescue:drop15_bid60': 1}` | `{'no': 1, 'yes': 1}` |
| `candidate_improves_live_loss` | 6 | 215c ($2.15) | -188c ($-1.88) | 403c ($4.03) | `{'continuous_penalty:cheap_penalty025_rank_only': 1, 'strict_delayed_recheck_rescue:drop15_bid60': 4, 'strict_parent_midprice_hold_fill': 1}` | `{'no': 2, 'yes': 4}` |

## Failure Modes

| mode | status | evidence |
|---|---|---|
| `exit_policy_error` | `active` | Three same-side winning markets show live v28 captured far more than dual-lane; dual-lane's current exit/weighting caps winners too aggressively. |
| `entry_timing_error` | `active` | Two candidate loss rows were live-positive after live v28 flipped or managed the market better. |
| `execution_friction_error` | `possible` | Candidate rows are single-row simulated/weighted fills while live v28 can scale or re-enter. |
| `source_quality_error` | `not_main_same_window_driver` | Most harmful candidate-minus-live rows are approved-entry rows, not rejected-actionable rows. |
| `fragility_error` | `active` | Candidate net remains below one full-loss cushion and same-window delta is negative. |
