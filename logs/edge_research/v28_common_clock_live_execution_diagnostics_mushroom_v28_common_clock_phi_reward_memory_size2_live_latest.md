# v28 Common-Clock Live Execution Diagnostics

- Generated UTC: `2026-05-11T03:46:36.215702+00:00`
- Decision: `filled_entry_seen_continue_scoring`
- Approved/order starts/order successes: `625` / `316` / `222`
- Zero-fill attempts/events / filled events: `85` / `117` / `274`
- Latest attempt: `KXBTC15M-26MAY101915-15` `yes` trigger=`99` result=`canceled` status=`canceled` fills=`0`

## Latest Attempt

```json
{
  "actual_fee_cents": null,
  "actual_fill_price_cents": null,
  "book_age_ms": 0.0,
  "book_summary": "[99:3291.21, 98:17458, 97:2650.97, 96:2569, 95:706.87]",
  "client_order_id": "btc15m-exit-d67d607e-39fb-4866-baeb-ead4eb2492ca",
  "decision_reason": "mushroom_v28_exit_value_over_hold_single_shot_visible_depth",
  "event_type": "order_submit_success",
  "exchange_status": "canceled",
  "feed_age_ms": 406.97499999999997,
  "fill_count": 0,
  "local_reaction_ms": 16.00000000325963,
  "market": "KXBTC15M-26MAY101915-15",
  "order_id": "4a863517-ccbc-410b-bc69-806d7e00c11f",
  "remaining_count": 0,
  "result": "canceled",
  "side": "yes",
  "time_in_force": "immediate_or_cancel",
  "top_of_book_limit_cents": 99,
  "trigger_price_cents": 99,
  "ts_wall": "2026-05-10T23:10:24.411753+00:00"
}
```

## Reconciliation

- Available: `True`
- Orders checked: `222`
- Markets checked for fills: `18`
