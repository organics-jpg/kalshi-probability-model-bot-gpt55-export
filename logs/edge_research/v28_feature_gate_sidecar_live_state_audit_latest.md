# v28 Feature-Gate Sidecar Live State Audit

Research-only. No live bot logic changes, no process control, no orders.

- Generated UTC: `2026-05-07T18:16:53.379016+00:00`
- Active variant: `raw05_recross60_abs085_ask65`
- Active log dir: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\live_mushroom_v28_feature_gate_ask65_size1`
- Active stats path: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\mushroom_v28_feature_gate_raw05_recross60_abs085_ask65_size1_live\summary.json`
- Lock PID/tag: `4972` / `mushroom_v28_feature_gate_raw05_recross60_abs085_ask65_size1_live`
- Process running/name: `True` / `python.exe`
- Score entries/round trips/open: `0` / `0` / `0`
- Sidecar live trade detected: `False`
- Entry/exit/full fill counts: `0` / `0` / `0`
- Score net/cost cents: `0` / `0`
- Event counts: `{'mushroom_v28_rejected': 96}`
- Order-like events: `0`
- Live-readiness artifact any_live_ready: `False`
- Blockers: `research_only, sidecar_process_running, live_readiness_artifact_false, no_order_like_events_seen`

## Interpretation

- This is a read-only sidecar state report; it does not start, stop, or modify any process.
- Keep feature-gate size1 sidecar evidence separate from the live_mushroom_v28_size2 baseline.
- The active section follows the current live lock; historical variants remain listed below for attribution.
- A detected sidecar fill or round trip is operational context only, not promotion evidence.
- No order-like execution events were seen if order_like_count is zero.

## Filled Trade Evidence

- First entry fill: `None`
- Last exit fill: `None`
- First fill event: `None`
- Last fill event: `None`

## Variant Separation

| label | strategy tag | storage tag | entries | round trips | W/L | net c | fills | order-like | live trade? |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `raw05_recross60_abs085_no_ask_floor` | `mushroom_v28_feature_gate_raw05_recross60_abs085_size1_live` | `live_mushroom_v28_feature_gate_size1` | 1 | 1 | 0/1 | -1 | 1/1/2 | 96 | True |
| `raw05_recross60_abs085_ask65` | `mushroom_v28_feature_gate_raw05_recross60_abs085_ask65_size1_live` | `live_mushroom_v28_feature_gate_ask65_size1` | 0 | 0 | 0/0 | 0 | 0/0/0 | 0 | False |

## Hourly Monitor Tail

- `﻿2026-05-07 14:08:12 -04:00 | UNHEALTHY | reason=wrong_live_lock_strategy_mushroom_v28_feature_gate_raw05_recross60_abs085_size1_live,pid_not_running_9536,missing_bot_log pid=9536`
- `2026-05-07 14:08:12 -04:00 | STOP stale bot process | pid=9536`
- `2026-05-07 14:08:12 -04:00 | STOP failed | pid=9536 error=Cannot find a process with the process identifier 9536.`
- `2026-05-07 14:08:12 -04:00 | START requested | launcher=C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\scripts\run_v28_feature_gate_live_size1.ps1 source_workspace=C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT`
- `2026-05-07 14:08:20 -04:00 | RESTARTED | pid=4972 process=running`
- `2026-05-07 14:10:37 -04:00 | OK | pid=4972 process=running heartbeat_age_min=0.14`
- `2026-05-07 14:16:52 -04:00 | OK | pid=4972 process=running heartbeat_age_min=0.13`

## Recent Events

- `{'ts_wall': '2026-05-07T18:16:16.310478+00:00', 'event_type': 'mushroom_v28_rejected', 'market': 'KXBTC15M-26MAY071430-30', 'side': 'no', 'decision_reason': 'feature_gate', 'actual_fill_price_cents': None, 'fill_count': None, 'order_id': '', 'client_order_id': '', 'result': '', 'exchange_status': '', 'top_of_book_limit_cents': 42, 'trigger_price_cents': 42, 'position_size': 0, 'remaining_position_size': None, 'mushroom_v28_p_side': 0.440312, 'mushroom_v28_feature_gate_pass': False, 'mushroom_v28_exit_reason': None}`
- `{'ts_wall': '2026-05-07T18:16:31.435370+00:00', 'event_type': 'mushroom_v28_rejected', 'market': 'KXBTC15M-26MAY071430-30', 'side': 'yes', 'decision_reason': 'book_stale', 'actual_fill_price_cents': None, 'fill_count': None, 'order_id': '', 'client_order_id': '', 'result': '', 'exchange_status': '', 'top_of_book_limit_cents': 64, 'trigger_price_cents': 64, 'position_size': 0, 'remaining_position_size': None, 'mushroom_v28_p_side': 0.589456, 'mushroom_v28_feature_gate_pass': False, 'mushroom_v28_exit_reason': None}`
- `{'ts_wall': '2026-05-07T18:16:31.437373+00:00', 'event_type': 'mushroom_v28_rejected', 'market': 'KXBTC15M-26MAY071430-30', 'side': 'no', 'decision_reason': 'book_stale', 'actual_fill_price_cents': None, 'fill_count': None, 'order_id': '', 'client_order_id': '', 'result': '', 'exchange_status': '', 'top_of_book_limit_cents': 38, 'trigger_price_cents': 38, 'position_size': 0, 'remaining_position_size': None, 'mushroom_v28_p_side': 0.410544, 'mushroom_v28_feature_gate_pass': False, 'mushroom_v28_exit_reason': None}`
- `{'ts_wall': '2026-05-07T18:16:32.048802+00:00', 'event_type': 'mushroom_v28_rejected', 'market': 'KXBTC15M-26MAY071430-30', 'side': 'yes', 'decision_reason': 'btc_stale', 'actual_fill_price_cents': None, 'fill_count': None, 'order_id': '', 'client_order_id': '', 'result': '', 'exchange_status': '', 'top_of_book_limit_cents': 63, 'trigger_price_cents': 63, 'position_size': 0, 'remaining_position_size': None, 'mushroom_v28_p_side': 0.589491, 'mushroom_v28_feature_gate_pass': False, 'mushroom_v28_exit_reason': None}`
- `{'ts_wall': '2026-05-07T18:16:32.050811+00:00', 'event_type': 'mushroom_v28_rejected', 'market': 'KXBTC15M-26MAY071430-30', 'side': 'no', 'decision_reason': 'btc_stale', 'actual_fill_price_cents': None, 'fill_count': None, 'order_id': '', 'client_order_id': '', 'result': '', 'exchange_status': '', 'top_of_book_limit_cents': 38, 'trigger_price_cents': 38, 'position_size': 0, 'remaining_position_size': None, 'mushroom_v28_p_side': 0.410509, 'mushroom_v28_feature_gate_pass': False, 'mushroom_v28_exit_reason': None}`
- `{'ts_wall': '2026-05-07T18:16:35.406316+00:00', 'event_type': 'mushroom_v28_rejected', 'market': 'KXBTC15M-26MAY071430-30', 'side': 'yes', 'decision_reason': 'edge_below_floor', 'actual_fill_price_cents': None, 'fill_count': None, 'order_id': '', 'client_order_id': '', 'result': '', 'exchange_status': '', 'top_of_book_limit_cents': 59, 'trigger_price_cents': 59, 'position_size': 0, 'remaining_position_size': None, 'mushroom_v28_p_side': 0.539459, 'mushroom_v28_feature_gate_pass': False, 'mushroom_v28_exit_reason': None}`
- `{'ts_wall': '2026-05-07T18:16:36.317257+00:00', 'event_type': 'mushroom_v28_rejected', 'market': 'KXBTC15M-26MAY071430-30', 'side': 'no', 'decision_reason': 'feature_gate', 'actual_fill_price_cents': None, 'fill_count': None, 'order_id': '', 'client_order_id': '', 'result': '', 'exchange_status': '', 'top_of_book_limit_cents': 42, 'trigger_price_cents': 42, 'position_size': 0, 'remaining_position_size': None, 'mushroom_v28_p_side': 0.460539, 'mushroom_v28_feature_gate_pass': False, 'mushroom_v28_exit_reason': None}`
- `{'ts_wall': '2026-05-07T18:16:43.435452+00:00', 'event_type': 'mushroom_v28_rejected', 'market': 'KXBTC15M-26MAY071430-30', 'side': 'no', 'decision_reason': 'edge_below_floor', 'actual_fill_price_cents': None, 'fill_count': None, 'order_id': '', 'client_order_id': '', 'result': '', 'exchange_status': '', 'top_of_book_limit_cents': 43, 'trigger_price_cents': 43, 'position_size': 0, 'remaining_position_size': None, 'mushroom_v28_p_side': 0.447423, 'mushroom_v28_feature_gate_pass': False, 'mushroom_v28_exit_reason': None}`
