# v28 Dual-Lane Same-Window Live Compare

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:47:37.865013+00:00`
- Freeze UTC: `2026-05-07T13:00:17.363339+00:00`
- Strict precheck UTC: `2026-05-08T03:51:40.155563+00:00`
- Promotion use: `same_window_research_only`
- Candidate policy: `post_dual_union_birth_entry_cheap_penalty025_rank_only`
- Future denominator: `18`
- Live post-freeze trades/markets: `31` / `14`

## Read

- This is an apples-to-apples research comparator, not a promotion gate by itself.
- Candidate rows come from the latest forced strict precheck artifact; this is complete only while the compact artifact contains all candidate rows.
- Live rows are actual scored v28 trades after the candidate freeze, aggregated by market.
- Large candidate-minus-live gaps can be exit/position-management gaps even when the candidate chose the correct settlement side.

## Summary

| scope | entries/markets | W/L | coverage | net | cushion |
|---|---:|---:|---:|---:|---:|
| candidate forced precheck | 16 | 13/3 | 88.89% | 59c ($0.59) | 0 |
| live v28 on candidate markets | 14 | 7/7 | 77.78% | 240c ($2.40) | 2 |
| live v28 all post-freeze markets | 14 | 7/7 | 77.78% | 240c ($2.40) | 2 |

- Candidate minus live on same candidate markets: `-181c ($-1.81)`

## Delta Buckets

| bucket | rows | candidate net | live net | candidate-live |
|---|---:|---:|---:|---:|
| `candidate_right_but_live_captured_more` | 6 | 136c ($1.36) | 414c ($4.14) | -278c ($-2.78) |
| `candidate_wrong_or_exit_bad_live_won` | 1 | -166c ($-1.66) | 20c ($0.20) | -186c ($-1.86) |
| `candidate_not_better_than_live` | 1 | -162c ($-1.62) | -6c ($-0.06) | -156c ($-1.56) |
| `candidate_vs_no_live_pnl` | 2 | 36c ($0.36) | 0c ($0.00) | 36c ($0.36) |
| `candidate_improves_live_loss` | 6 | 215c ($2.15) | -188c ($-1.88) | 403c ($4.03) |

## Market-Level Comparison

| market | side | component | source | bucket | candidate net | live trades | live sides | live same-side | live opposite | live net | candidate-live |
|---|---|---|---|---|---:|---:|---|---:|---:|---:|---:|
| `KXBTC15M-26MAY071100-00` | yes | strict_delayed_recheck_rescue:drop15_bid60 | approved_entry | `candidate_wrong_or_exit_bad_live_won` | -166c ($-1.66) | 4 | no,yes | -6c ($-0.06) | 26c ($0.26) | 20c ($0.20) | -186c ($-1.86) |
| `KXBTC15M-26MAY071015-15` | no | strict_delayed_recheck_rescue:drop15_bid60 | approved_entry | `candidate_not_better_than_live` | -162c ($-1.62) | 4 | no,yes | -32c ($-0.32) | 26c ($0.26) | -6c ($-0.06) | -156c ($-1.56) |
| `KXBTC15M-26MAY070945-45` | no | strict_parent_midprice_hold_fill | approved_entry | `candidate_right_but_live_captured_more` | 28c ($0.28) | 1 | no | 150c ($1.50) | 0c ($0.00) | 150c ($1.50) | -122c ($-1.22) |
| `KXBTC15M-26MAY071145-45` | yes | strict_delayed_recheck_rescue:drop15_bid60 | rejected_actionable | `candidate_right_but_live_captured_more` | 46c ($0.46) | 1 | yes | 106c ($1.06) | 0c ($0.00) | 106c ($1.06) | -60c ($-0.60) |
| `KXBTC15M-26MAY070915-15` | no | strict_parent_midprice_hold_fill | approved_entry | `candidate_right_but_live_captured_more` | 20c ($0.20) | 2 | no | 56c ($0.56) | 0c ($0.00) | 56c ($0.56) | -36c ($-0.36) |
| `KXBTC15M-26MAY071030-30` | no | strict_parent_midprice_hold_fill | rejected_actionable | `candidate_right_but_live_captured_more` | 7c ($0.07) | 2 | no | 37c ($0.37) | 0c ($0.00) | 37c ($0.37) | -30c ($-0.30) |
| `KXBTC15M-26MAY071130-30` | no | strict_parent_midprice_hold_fill | approved_entry | `candidate_right_but_live_captured_more` | 13c ($0.13) | 1 | no | 42c ($0.42) | 0c ($0.00) | 42c ($0.42) | -29c ($-0.29) |
| `KXBTC15M-26MAY071300-00` | yes | continuous_penalty:cheap_penalty025_rank_only | rejected_actionable | `candidate_vs_no_live_pnl` | -10c ($-0.10) | 0 |  | 0c ($0.00) | 0c ($0.00) | 0c ($0.00) | -10c ($-0.10) |
| `KXBTC15M-26MAY071045-45` | no | strict_parent_midprice_hold_fill | approved_entry | `candidate_right_but_live_captured_more` | 22c ($0.22) | 2 | no | 23c ($0.23) | 0c ($0.00) | 23c ($0.23) | -1c ($-0.01) |
| `KXBTC15M-26MAY071230-30` | yes | strict_parent_midprice_hold_fill | approved_entry | `candidate_improves_live_loss` | 21c ($0.21) | 3 | yes | -22c ($-0.22) | 0c ($0.00) | -22c ($-0.22) | 43c ($0.43) |
| `KXBTC15M-26MAY071115-15` | yes | strict_delayed_recheck_rescue:drop15_bid60 | approved_entry | `candidate_improves_live_loss` | 32c ($0.32) | 2 | yes | -13c ($-0.13) | 0c ($0.00) | -13c ($-0.13) | 45c ($0.45) |
| `KXBTC15M-26MAY071200-00` | no | strict_delayed_recheck_rescue:drop15_bid60 | approved_entry | `candidate_vs_no_live_pnl` | 46c ($0.46) | 0 |  | 0c ($0.00) | 0c ($0.00) | 0c ($0.00) | 46c ($0.46) |
| `KXBTC15M-26MAY071315-15` | yes | strict_delayed_recheck_rescue:drop15_bid60 | approved_entry | `candidate_improves_live_loss` | 44c ($0.44) | 3 | yes | -8c ($-0.08) | 0c ($0.00) | -8c ($-0.08) | 52c ($0.52) |
| `KXBTC15M-26MAY071215-15` | no | continuous_penalty:cheap_penalty025_rank_only | approved_entry | `candidate_improves_live_loss` | 20c ($0.20) | 2 | no | -45c ($-0.45) | 0c ($0.00) | -45c ($-0.45) | 65c ($0.65) |
| `KXBTC15M-26MAY070930-30` | yes | strict_delayed_recheck_rescue:drop15_bid60 | approved_entry | `candidate_improves_live_loss` | 40c ($0.40) | 1 | yes | -28c ($-0.28) | 0c ($0.00) | -28c ($-0.28) | 68c ($0.68) |
| `KXBTC15M-26MAY071000-00` | no | strict_delayed_recheck_rescue:drop15_bid60 | approved_entry | `candidate_improves_live_loss` | 58c ($0.58) | 3 | no | -72c ($-0.72) | 0c ($0.00) | -72c ($-0.72) | 130c ($1.30) |
