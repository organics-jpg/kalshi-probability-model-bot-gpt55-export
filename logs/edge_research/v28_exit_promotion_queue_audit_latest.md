# v28 Exit Promotion Queue Audit

Research-only audit; no live bot changes or orders.

- Generated UTC: `2026-05-07T18:03:24.693946+00:00`
- Input dashboard: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_exit_policy_watch_dashboard_latest.json`
- Dashboard generated UTC: `2026-05-07T17:51:53.645709+00:00`
- Live baseline net: `1361.000000c`
- Review-ready rows: `0`
- Forward-positive queue rows: `14`
- Blocked/waiting counts: `10/4`

## Interpretation

- No exit watch clears the promotion queue audit.
- Closest row is common_clock_strict_forward_v2 with 58 settled, 17 suppressions, delta 242.0c, candidate/delta cushion 6/2, missing suppressions 13 and delta cushion cents 58.0.
- The active bottleneck is suppression density and delta cushion, not settled-row count, for the top book-gap/common-clock guards.

## Forward-Positive Queue

| rank | lane | status | settled | suppressed | candidate c | delta c | loss cost | cushion cand/delta | missing settled/supp/delta c | review ready | blockers |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `common_clock_strict_forward_v2` | `forward_positive_under_review` | 58 | 17 | 668.000000 | 242.000000 | 0.000000 | 6/2 | 0/13/58.000000 | False | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3 |
| 2 | `book_gap_loss_guard` | `forward_positive_under_review` | 59 | 17 | 582.000000 | 242.000000 | 0.000000 | 5/2 | 0/13/58.000000 | False | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3 |
| 3 | `common_clock_strict_forward_v1` | `forward_positive_under_review` | 59 | 17 | 582.000000 | 242.000000 | 0.000000 | 5/2 | 0/13/58.000000 | False | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3 |
| 4 | `common_clock_strict_forward_v3` | `forward_positive_under_review` | 46 | 13 | 692.000000 | 214.000000 | 0.000000 | 6/2 | 0/17/86.000000 | False | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3 |
| 5 | `book_gap_loss_guard_v3` | `forward_positive_under_review` | 46 | 9 | 644.000000 | 166.000000 | 0.000000 | 6/1 | 0/21/134.000000 | False | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3 |
| 6 | `book_gap_loss_guard_v2` | `forward_positive_under_review` | 58 | 5 | 578.000000 | 152.000000 | 0.000000 | 5/1 | 0/25/148.000000 | False | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3 |
| 7 | `reduce_depth_gate` | `forward_positive_under_review` | 57 | 1 | 424.000000 | 48.000000 | 0.000000 | 4/0 | 0/29/252.000000 | False | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3 |
| 8 | `reduce_loss_control_refinement` | `forward_positive_under_review` | 57 | 1 | 424.000000 | 48.000000 | 0.000000 | 4/0 | 0/29/252.000000 | False | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3 |
| 9 | `exit_reduce_drift_guard` | `positive_but_under_sample` | 16 | 2 | 316.000000 | 90.000000 | 0.000000 | 3/0 | 14/28/210.000000 | False | settled_lt_30, suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3 |
| 10 | `exit_clip_separator_watch` | `positive_but_under_sample` | 2 | 1 | 60.000000 | 60.000000 | 0.000000 | 0/0 | 28/29/240.000000 | False | settled_lt_30, suppressed_decisions_lt_30, candidate_full_loss_cushion_lt_3, delta_full_loss_cushion_lt_3 |
| 11 | `soft_frontier_midprice_delayed_recheck_exit` | `positive_but_under_sample` | 2 | 2 | 84.000000 | 48.000000 | 0.000000 | 0/0 | 28/28/252.000000 | False | settled_lt_30, suppressed_decisions_lt_30, candidate_full_loss_cushion_lt_3, delta_full_loss_cushion_lt_3 |
| 12 | `soft_frontier_midprice_delayed_recheck_rescue` | `positive_but_under_sample` | 2 | 2 | 84.000000 | 48.000000 | 0.000000 | 0/0 | 28/28/252.000000 | False | settled_lt_30, suppressed_decisions_lt_30, candidate_full_loss_cushion_lt_3, delta_full_loss_cushion_lt_3 |
| 13 | `value_exit_feature_side_guard` | `positive_but_under_sample` | 3 | 1 | 104.000000 | 18.000000 | 0.000000 | 1/0 | 27/29/282.000000 | False | settled_lt_30, suppressed_decisions_lt_30, candidate_full_loss_cushion_lt_3, delta_full_loss_cushion_lt_3 |
| 14 | `exit_shallow_drawdown` | `positive_but_under_sample` | 1 | 1 | 36.000000 | 18.000000 | 0.000000 | 0/0 | 29/29/282.000000 | False | settled_lt_30, suppressed_decisions_lt_30, candidate_full_loss_cushion_lt_3, delta_full_loss_cushion_lt_3 |

## Gate Notes

- This queue is stricter than the dashboard status: it requires both candidate and delta full-loss cushion.
- A row that clears this queue still needs the separate live-readiness gate and a no-live-change review.
- Diagnostic opportunity notes are not counted as strict evidence here.
