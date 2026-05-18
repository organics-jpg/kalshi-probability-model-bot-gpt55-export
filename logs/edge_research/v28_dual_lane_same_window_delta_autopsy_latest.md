# v28 Dual-Lane Same-Window Delta Autopsy

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-07T16:50:58.051172+00:00`
- Compare UTC: `2026-05-07T16:50:52.438302+00:00`
- Freeze UTC: `2026-05-07T13:00:17.363339+00:00`
- Candidate policy: `post_dual_union_birth_bridge_cheap_penalty025_rank_only`
- Promotion use: `same_window_research_only`

## Read

- Same-window evidence is research-only and cannot promote the dual lane before own-freeze rows mature.
- The current strict precheck is behind actual live v28 on the same markets; this is a live-baseline blocker, not just a sample-size blocker.
- Largest negative bucket is candidate_positive_live_captured_more with 3 rows and -529c ($-5.29) candidate-minus-live.
- Top deficits should be treated as failure-mode examples for entry/exposure/exit-clock repair, not as rows to hand-pick away.

## Same-Window Summary

- Candidate: `13` entries, W/L `11/2`, net `18c ($0.18)`, cushion `0`.
- Live on candidate markets: `12` markets, W/L `5/6`, net `324c ($3.24)`, cushion `3`.
- Candidate minus live: `-306c ($-3.06)`.
- Deficit/surplus split: `5` deficit rows for `-925c ($-9.25)`, `8` surplus rows for `619c ($6.19)`.

## Classification Summary

| class | rows | candidate net | live net | candidate-live | candidate W/L | live W/L |
|---|---:|---:|---:|---:|---:|---:|
| `candidate_positive_live_captured_more` | 3 | 87c ($0.87) | 616c ($6.16) | -529c ($-5.29) | 3/0 | 3/0 |
| `candidate_loss_live_escape` | 2 | -328c ($-3.28) | 68c ($0.68) | -396c ($-3.96) | 0/2 | 2/0 |
| `candidate_captures_more_than_live` | 2 | 78c ($0.78) | 0c ($0.00) | 78c ($0.78) | 2/0 | 0/0 |
| `candidate_avoids_live_loss` | 6 | 181c ($1.81) | -360c ($-3.60) | 541c ($5.41) | 6/0 | 0/6 |

## Top Deficits

| market | class | side | component | source | candidate | live | delta | live trades | live side net |
|---|---|---|---|---|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY070945-45` | `candidate_positive_live_captured_more` | no | strict_parent_midprice_hold_fill | approved_entry | 28c ($0.28) | 300c ($3.00) | -272c ($-2.72) | 1 | `{'no': 300.0}` |
| `KXBTC15M-26MAY071100-00` | `candidate_loss_live_escape` | yes | strict_delayed_recheck_rescue:drop15_bid60 | approved_entry | -166c ($-1.66) | 40c ($0.40) | -206c ($-2.06) | 7 | `{'yes': -12.0, 'no': 52.0}` |
| `KXBTC15M-26MAY071015-15` | `candidate_loss_live_escape` | no | strict_delayed_recheck_rescue:drop15_bid60 | approved_entry | -162c ($-1.62) | 28c ($0.28) | -190c ($-1.90) | 7 | `{'no': -28.0, 'yes': 56.0}` |
| `KXBTC15M-26MAY071145-45` | `candidate_positive_live_captured_more` | yes | strict_delayed_recheck_rescue:drop15_bid60 | rejected_actionable | 46c ($0.46) | 228c ($2.28) | -182c ($-1.82) | 2 | `{'yes': 228.0}` |
| `KXBTC15M-26MAY071130-30` | `candidate_positive_live_captured_more` | no | strict_parent_midprice_hold_fill | approved_entry | 13c ($0.13) | 88c ($0.88) | -75c ($-0.75) | 1 | `{'no': 88.0}` |

## Top Surpluses

| market | class | side | component | source | candidate | live | delta | live trades |
|---|---|---|---|---|---:|---:|---:|---:|
| `KXBTC15M-26MAY071000-00` | `candidate_avoids_live_loss` | no | strict_delayed_recheck_rescue:drop15_bid60 | approved_entry | 58c ($0.58) | -92c ($-0.92) | 150c ($1.50) | 6 |
| `KXBTC15M-26MAY070930-30` | `candidate_avoids_live_loss` | yes | strict_delayed_recheck_rescue:drop15_bid60 | approved_entry | 40c ($0.40) | -56c ($-0.56) | 96c ($0.96) | 2 |
| `KXBTC15M-26MAY071045-45` | `candidate_avoids_live_loss` | no | strict_parent_midprice_hold_fill | approved_entry | 22c ($0.22) | -68c ($-0.68) | 90c ($0.90) | 3 |
| `KXBTC15M-26MAY071230-30` | `candidate_avoids_live_loss` | yes | strict_parent_midprice_hold_fill | approved_entry | 21c ($0.21) | -66c ($-0.66) | 87c ($0.87) | 5 |
| `KXBTC15M-26MAY071215-15` | `candidate_avoids_live_loss` | no | continuous_penalty:cheap_penalty025_rank_only | approved_entry | 20c ($0.20) | -64c ($-0.64) | 84c ($0.84) | 4 |
| `KXBTC15M-26MAY071200-00` | `candidate_captures_more_than_live` | no | strict_delayed_recheck_rescue:drop15_bid60 | approved_entry | 46c ($0.46) | 0c ($0.00) | 46c ($0.46) | 0 |
| `KXBTC15M-26MAY070915-15` | `candidate_avoids_live_loss` | no | strict_parent_midprice_hold_fill | approved_entry | 20c ($0.20) | -14c ($-0.14) | 34c ($0.34) | 3 |
| `KXBTC15M-26MAY071115-15` | `candidate_captures_more_than_live` | yes | strict_delayed_recheck_rescue:drop15_bid60 | approved_entry | 32c ($0.32) | 0c ($0.00) | 32c ($0.32) | 4 |
