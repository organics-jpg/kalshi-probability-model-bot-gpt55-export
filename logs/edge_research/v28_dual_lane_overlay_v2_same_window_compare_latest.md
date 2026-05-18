# v28 Dual-Lane Overlay Same-Window Compare

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:47:37.708127+00:00`
- Filter watch UTC: `2026-05-11T03:46:02.223702+00:00`
- Freeze UTC/local: `2026-05-07T16:50:03.875032+00:00` / `2026-05-07T12:50:03.875032-04:00`
- Promotion use: `overlay_same_window_research_only`
- Overlay policy/rule: `post_dual_overlay_filter_entry_cheap_penalty025_rank_only` / `dual_lane_overlay_raw05_recross_le030_abs085`
- Selected markets: `1`
- Candidate minus live on selected markets: `52c ($0.52)`

## Read

- This is a strict selected-market comparator for the overlay filter.
- It remains empty until the overlay watch has selected own-freeze rows.
- A positive standalone overlay PnL is insufficient; selected rows should also improve live v28 on the same markets.

## Summary

| scope | entries/markets | W/L | coverage | net | cushion |
|---|---:|---:|---:|---:|---:|
| overlay selected rows | 1 | 1/0 | 100.00% | 44c ($0.44) | 0 |
| live v28 same selected markets | 1 | 0/1 | 100.00% | -8c ($-0.08) | 0 |

## Market-Level Comparison

| market | side | component | source | candidate net | live trades | live sides | live net | candidate-live |
|---|---|---|---|---:|---:|---|---:|---:|
| `KXBTC15M-26MAY071315-15` | yes | strict_delayed_recheck_rescue:drop15_bid60 | approved_entry | 44c ($0.44) | 3 | yes | -8c ($-0.08) | 52c ($0.52) |
