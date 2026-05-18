# v28 Common-Clock Live Execution Diagnostics

- Generated UTC: `2026-05-11T03:46:38.057642+00:00`
- Decision: `filled_entry_seen_continue_scoring`
- Approved/order starts/order successes: `30` / `46` / `46`
- Zero-fill attempts/events / filled events: `19` / `34` / `54`
- Latest attempt: `KXBTC15M-26MAY081730-30` `no` trigger=`9` result=`executed` status=`executed` fills=`2`

## Latest Attempt

```json
{
  "actual_fee_cents": null,
  "actual_fill_price_cents": null,
  "book_age_ms": 0.0,
  "book_summary": "[9:1898, 8:2747.58, 7:663.72, 6:245, 5:421.75]",
  "client_order_id": "btc15m-exit-6e9840f7-8a24-4d40-b983-33581269b90c",
  "decision_reason": "mushroom_v28_probability_collapse_full_single_shot_visible_depth",
  "event_type": "order_submit_success",
  "exchange_status": "executed",
  "feed_age_ms": 99.107,
  "fill_count": 2,
  "local_reaction_ms": 202.9999999795109,
  "market": "KXBTC15M-26MAY081730-30",
  "order_id": "be234165-04b9-4adf-aa1e-2dbc73ad8d9c",
  "remaining_count": 0,
  "result": "executed",
  "side": "no",
  "time_in_force": "immediate_or_cancel",
  "top_of_book_limit_cents": 9,
  "trigger_price_cents": 9,
  "ts_wall": "2026-05-08T21:25:19.814737+00:00"
}
```

## Reconciliation

- Available: `True`
- Orders checked: `46`
- Markets checked for fills: `4`
