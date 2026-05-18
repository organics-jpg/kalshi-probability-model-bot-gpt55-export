# v28 Shadow Observation Availability

Research-only; no live bot changes and no orders.

- Generated UTC: `2026-05-11T03:46:17.097548+00:00`
- Shadow events: `26023`
- Reconstructed shadow trades: `173`

## Frozen Clocks

| clock | freeze UTC | post events | post entries | post exit-clock rows | settled exit-clock rows | pending exit-clock rows | blocker |
|---|---|---:|---:|---:|---:|---:|---|
| boundary_clock_feature_gate | `2026-05-06T16:47:25.847566+00:00` | 12593 | 67 | 67 | 67 | 0 |  |
| dual_exit_book_gap_else_reduce | `2026-05-06T21:15:42.381999+00:00` | 10358 | 59 | 59 | 59 | 0 |  |
| exit_book_gap_loss_guard | `2026-05-06T21:29:32.710906+00:00` | 10242 | 59 | 59 | 59 | 0 |  |
| exit_book_gap_loss_guard_v2 | `2026-05-06T22:01:04.415577+00:00` | 9987 | 58 | 58 | 58 | 0 |  |
| exit_book_gap_loss_guard_v3 | `2026-05-07T01:01:45.501061+00:00` | 8404 | 46 | 46 | 46 | 0 |  |
| exit_reduce_drift_guard | `2026-05-07T02:30:19.536047+00:00` | 7600 | 40 | 40 | 40 | 0 |  |
| exit_shallow_drawdown | `2026-05-07T05:50:24.685661+00:00` | 5954 | 33 | 33 | 33 | 0 |  |
| exit_shallow_duration_lte52 | `2026-05-07T05:55:14.530870+00:00` | 5920 | 33 | 33 | 33 | 0 |  |
| exit_clip_separator_watch | `2026-05-07T04:04:23.876080+00:00` | 6798 | 36 | 36 | 36 | 0 |  |
| matched_unchanged_loss_guard_watch | `2026-05-07T09:30:07.471830+00:00` | 4572 | 33 | 33 | 33 | 0 |  |
| feature_gate_exit_bid_suppression | `2026-05-07T07:32:00.852069+00:00` | 5320 | 33 | 33 | 33 | 0 |  |
| feature_gate_exit_bid_delayed_recheck | `2026-05-07T07:54:52.452489+00:00` | 5184 | 33 | 33 | 33 | 0 |  |
| feature_gate_value_exit | `2026-05-07T07:36:17.925386+00:00` | 5296 | 33 | 33 | 33 | 0 |  |
| value_exit_feature_side_guard | `2026-05-07T07:42:49.442068+00:00` | 5256 | 33 | 33 | 33 | 0 |  |
| soft_frontier_midprice_delayed_recheck_exit | `2026-05-07T08:05:51.308715+00:00` | 5118 | 33 | 33 | 33 | 0 |  |
| soft_frontier_midprice_delayed_recheck_rescue | `2026-05-07T08:24:03.515891+00:00` | 5009 | 33 | 33 | 33 | 0 |  |
| feature_gate_size_shrink_delayed_recheck_exit | `2026-05-07T08:47:54.507128+00:00` | 4866 | 33 | 33 | 33 | 0 |  |
| feature_gate_size_shrink_delayed_recheck_rescue | `2026-05-07T08:55:51.390169+00:00` | 4818 | 33 | 33 | 33 | 0 |  |
| feature_gate_late_collapse_recheck_rescue | `2026-05-07T09:09:25.393809+00:00` | 4738 | 33 | 33 | 33 | 0 |  |
| feature_gate_dual_clock_recheck_rescue | `2026-05-07T09:16:37.047947+00:00` | 4692 | 33 | 33 | 33 | 0 |  |
| feature_gate_confirmed_dual_clock_fill | `2026-05-07T09:21:53.115169+00:00` | 4650 | 33 | 33 | 33 | 0 |  |
| top_component_mix_portfolio | `2026-05-07T09:44:04.148307+00:00` | 4452 | 32 | 32 | 32 | 0 |  |
| top_component_false_negative_rescue_child | `2026-05-07T10:21:56.887234+00:00` | 4152 | 32 | 32 | 32 | 0 |  |
| top_component_parent_fill_repair_child | `2026-05-07T10:29:46.104521+00:00` | 4074 | 32 | 32 | 32 | 0 |  |
| exit_common_clock_residual_child | `2026-05-07T08:06:06.929631+00:00` | 5116 | 33 | 33 | 33 | 0 |  |
| exit_common_clock_residual_child_book_gap_guard | `2026-05-07T15:09:26.289911+00:00` | 1582 | 12 | 13 | 13 | 0 |  |

## Pending Exit-Clock Rows

## Interpretation

- Settled exit-clock rows are the denominator used by strict forward exit-policy scorecards.
- Pending rows show that the shadow loop is collecting observations but market settlement is not yet available.
- A missing or zero denominator is not promotion evidence; it is only a collection/readiness state.
