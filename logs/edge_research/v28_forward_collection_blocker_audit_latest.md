# v28 Forward Collection Blocker Audit

Research-only. No live bot logic changes, no process control, no orders.

- Generated UTC: `2026-05-07T20:58:56.565550+00:00`
- Goal achieved: `False`
- Candidate-vs-live generated UTC/live net/live-ready: `2026-05-07T18:33:06.404302+00:00` / `1361c` / `1`
- Latest hourly monitor status: `unknown`
- Latest hourly monitor line: `2026-05-07 16:57:16 -04:00 | CHECK_ONLY | restart skipped`
- Latest bot heartbeat UTC: `2026-05-07T17:22:01+00:00`
- Latest execution event: `2026-05-07T17:12:13.706367+00:00` / `exit_reconciled` / `KXBTC15M-26MAY071315-15`
- Live lock PID/tag: `4972` / `mushroom_v28_feature_gate_raw05_recross60_abs085_ask65_size1_live`
- Shadow availability generated UTC/events/trades/clocks: `2026-05-07T20:58:17.584591+00:00` / `26023` / `173` / `26`
- Exit dashboard generated UTC/status counts: `2026-05-07T18:37:46.111664+00:00` / `{'blocked_loss_control_cost': 9, 'blocked_net_not_positive': 2, 'forward_positive_under_review': 10, 'not_positive_or_under_sample': 1, 'positive_but_under_sample': 4, 'waiting_no_post_freeze_rows': 1, 'waiting_no_suppressed_exits': 2}`
- Feature-gate sidecar generated UTC/events/order-like/process: `2026-05-07T18:16:53.379016+00:00` / `{'mushroom_v28_rejected': 96}` / `0` / `True`
- Feature-gate sidecar trade detected/round trips/net: `False` / `0` / `0c`
- Blockers: `research_only, exit_watches_still_need_suppression_density_or_cushion, feature_gate_sidecar_evidence_separate_from_size2_baseline, feature_gate_sidecar_no_order_like_events_seen`

## Read

- Promotion remains blocked by strategy gates: no live-ready candidates and exit watches still need suppression density, cushion, or false-hold safety.
- Fresh frozen/live evidence collection is also operationally blocked if the latest watchdog status remains RESTART_FAILED.
- If a feature-gate size1 sidecar audit exists, keep it separate from the live_mushroom_v28_size2 baseline and do not treat it as candidate-vs-live promotion evidence.
- This report is a research status audit only; it does not restart, stop, or modify live trading.

## Closest Positive Exit Watches

| lane | status | settled | suppressed | need for 30 | delta | loss-control cost | blockers |
|---|---|---:|---:|---:|---:|---:|---|
| `book_gap_loss_guard` | `forward_positive_under_review` | 59 | 17 | 13 | 242.0c | 0.0c | `suppressed_decisions_lt_30` |
| `common_clock_strict_forward_v1` | `forward_positive_under_review` | 59 | 17 | 13 | 242.0c | 0.0c | `suppressed_decisions_lt_30` |
| `common_clock_strict_forward_v2` | `forward_positive_under_review` | 58 | 17 | 13 | 242.0c | 0.0c | `suppressed_decisions_lt_30` |
| `common_clock_strict_forward_v3` | `forward_positive_under_review` | 46 | 13 | 17 | 214.0c | 0.0c | `suppressed_decisions_lt_30` |
| `feature_gate_value_exit` | `positive_but_under_sample` | 14 | 5 | 25 | 200.00000000000006c | 0.0c | `settled_lt_30, selected_side_live_overlap_only, hold_to_settlement_assumption, not_live_bot_logic` |
| `book_gap_loss_guard_v3` | `forward_positive_under_review` | 46 | 9 | 21 | 166.0c | 0.0c | `suppressed_decisions_lt_30` |
| `book_gap_loss_guard_v2` | `forward_positive_under_review` | 58 | 5 | 25 | 152.0c | 0.0c | `suppressed_decisions_lt_30` |
| `reduce_depth_gate` | `forward_positive_under_review` | 60 | 2 | 28 | 94.0c | 0.0c | `full_loss_cushion_lt_3` |
| `reduce_loss_control_refinement` | `forward_positive_under_review` | 60 | 2 | 28 | 94.0c | 0.0c | `full_loss_cushion_lt_3` |
| `soft_frontier_midprice_delayed_recheck_exit` | `positive_but_under_sample` | 3 | 3 | 27 | 66.0c | 0.0c | `joined_rows_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3` |

## Latest Frozen Clocks

| clock | freeze UTC | post entries | settled exit rows | pending | blocker |
|---|---|---:|---:|---:|---|
| `exit_common_clock_residual_child_book_gap_guard` | `2026-05-07T15:09:26.289911+00:00` | 12 | 13 | 0 | `` |
| `top_component_parent_fill_repair_child` | `2026-05-07T10:29:46.104521+00:00` | 32 | 32 | 0 | `` |
| `top_component_false_negative_rescue_child` | `2026-05-07T10:21:56.887234+00:00` | 32 | 32 | 0 | `` |
| `top_component_mix_portfolio` | `2026-05-07T09:44:04.148307+00:00` | 32 | 32 | 0 | `` |
| `matched_unchanged_loss_guard_watch` | `2026-05-07T09:30:07.471830+00:00` | 33 | 33 | 0 | `` |
| `feature_gate_confirmed_dual_clock_fill` | `2026-05-07T09:21:53.115169+00:00` | 33 | 33 | 0 | `` |
| `feature_gate_dual_clock_recheck_rescue` | `2026-05-07T09:16:37.047947+00:00` | 33 | 33 | 0 | `` |
| `feature_gate_late_collapse_recheck_rescue` | `2026-05-07T09:09:25.393809+00:00` | 33 | 33 | 0 | `` |

## Feature-Gate Size1 Sidecar

- Lock PID/tag: `4972` / `mushroom_v28_feature_gate_raw05_recross60_abs085_ask65_size1_live`
- Process running/name: `True` / `python.exe`
- Event counts: `{'mushroom_v28_rejected': 96}`
- Order-like events: `0`
- Live trade detected/entry fills/exit fills: `False` / `0` / `0`
- Score entries/round trips/open/net: `0` / `0` / `0` / `0c`
- Sidecar blockers: `research_only, sidecar_process_running, live_readiness_artifact_false, no_order_like_events_seen`
- This sidecar state is live-state context only; it is not the size2 baseline and not promotion evidence.

## Hourly Monitor Tail

- `2026-05-07 13:22:21 -04:00 | STOP failed | pid=3356 error=Cannot find a process with the process identifier 3356.`
- `2026-05-07 13:22:21 -04:00 | START requested | launcher=C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\scripts\run_probability_lab_bot_live_size2.ps1 source_workspace=C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT`
- `2026-05-07 13:22:29 -04:00 | RESTART_FAILED | no live bot process detected after launch`
- `2026-05-07 16:57:16 -04:00 | UNHEALTHY | reason=wrong_live_lock_strategy_mushroom_v28_feature_gate_raw05_recross60_abs085_ask65_size1_live,stale_bot_log_215.26min pid=4972`
- `2026-05-07 16:57:16 -04:00 | CHECK_ONLY | restart skipped`
