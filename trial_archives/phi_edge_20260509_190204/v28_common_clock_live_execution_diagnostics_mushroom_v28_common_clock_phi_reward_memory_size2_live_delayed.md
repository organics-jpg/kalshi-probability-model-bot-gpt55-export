# v28 Common-Clock Live Execution Diagnostics

- Generated UTC: `2026-05-09T20:14:43.183989+00:00`
- Decision: `filled_entry_seen_continue_scoring`
- Approved/order starts/order successes: `71` / `124` / `124`
- Zero-fill attempts/events / filled events: `39` / `54` / `170`
- Latest attempt: `KXBTC15M-26MAY091615-15` `yes` trigger=`5` result=`executed` status=`executed` fills=`3`

## Latest Attempt

```json
{
  "actual_fee_cents": null,
  "actual_fill_price_cents": null,
  "book_age_ms": 125.0,
  "book_summary": "[5:191.43, 4:1048.7, 3:1604.69, 2:998, 1:50]",
  "client_order_id": "btc15m-exit-b63e7fc9-1753-4ad6-862c-2181a229d71e",
  "decision_reason": "mushroom_v28_probability_collapse_full_single_shot_visible_depth",
  "event_type": "order_submit_success",
  "exchange_status": "executed",
  "feed_age_ms": -190.26100000000002,
  "fill_count": 3,
  "local_reaction_ms": 157.00000000651926,
  "market": "KXBTC15M-26MAY091615-15",
  "order_id": "212d6059-5bfa-4aaa-99dc-4e1467ba71d8",
  "remaining_count": 0,
  "result": "executed",
  "side": "yes",
  "time_in_force": "immediate_or_cancel",
  "top_of_book_limit_cents": 5,
  "trigger_price_cents": 5,
  "ts_wall": "2026-05-09T20:11:37.862560+00:00"
}
```

## Reconciliation

- Available: `True`
- Orders checked: `124`
- Markets checked for fills: `11`
