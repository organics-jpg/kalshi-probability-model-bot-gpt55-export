# v28 Common-Clock Live Execution Diagnostics

- Generated UTC: `2026-05-09T23:01:39.152314+00:00`
- Decision: `filled_entry_seen_continue_scoring`
- Approved/order starts/order successes: `79` / `136` / `136`
- Zero-fill attempts/events / filled events: `48` / `69` / `176`
- Latest attempt: `KXBTC15M-26MAY091630-30` `yes` trigger=`5` result=`canceled` status=`canceled` fills=`0`

## Latest Attempt

```json
{
  "actual_fee_cents": null,
  "actual_fill_price_cents": null,
  "book_age_ms": 702.9999999795109,
  "book_summary": "[5:170, 6:4900.97, 7:325, 8:713.5, 9:342.45]",
  "client_order_id": "btc15m-entry-3fb1ac42-9cd0-4fa5-866c-3ef9c59b8aeb",
  "decision_reason": "single_shot_abundant_depth",
  "event_type": "order_submit_success",
  "exchange_status": "canceled",
  "feed_age_ms": 328.255,
  "fill_count": 0,
  "local_reaction_ms": 733.9999999967404,
  "market": "KXBTC15M-26MAY091630-30",
  "order_id": "71f5b6fb-19d5-4a15-bb48-460c9789649d",
  "remaining_count": 0,
  "result": "canceled",
  "side": "yes",
  "time_in_force": "immediate_or_cancel",
  "top_of_book_limit_cents": 5,
  "trigger_price_cents": 5,
  "ts_wall": "2026-05-09T20:24:27.824243+00:00"
}
```

## Reconciliation

- Available: `True`
- Orders checked: `136`
- Markets checked for fills: `12`
