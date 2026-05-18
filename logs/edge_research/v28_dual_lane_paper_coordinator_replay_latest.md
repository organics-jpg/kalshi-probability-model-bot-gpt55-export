# v28 Dual-Lane Paper Coordinator Replay

Research-only. No orders placed, no live bot stopped, no live bot logic changed.

- Generated UTC: `2026-05-11T03:47:25.578190+00:00`
- Promotion use: `paper_coordinator_replay_only`
- Same-window compare UTC: `2026-05-11T03:47:25.380810+00:00`
- Candidate policy: `post_dual_union_birth_entry_cheap_penalty025_rank_only`

## Read

- This is the ledger shape needed before live dual-lane can trade alongside v28.
- Rows are replay/paper rows, not live orders.
- Same-market same-side rows could be coordinated as shared exposure; side-flip/opposite-side rows require explicit arbitration.

## Summary

- Dual-lane W/L/net: `13/3` / `59c ($0.59)`
- Live v28 same-market W/L/net: `7/7` / `240c ($2.40)`
- Dual-lane minus live: `-181c ($-1.81)`
- Hazards: `same_market_position_attribution_conflict, dual_lane_underperforms_live_same_window, candidate_contains_reconstructed_or_rejected_rows`

## Conflict Summary

| conflict | markets | dual-lane net | live net | dual-live |
|---|---:|---:|---:|---:|
| `dual_lane_only` | 2 | 36c ($0.36) | 0c ($0.00) | 36c ($0.36) |
| `same_market_live_side_flip` | 2 | -328c ($-3.28) | 14c ($0.14) | -342c ($-3.42) |
| `same_market_same_side` | 12 | 351c ($3.51) | 226c ($2.26) | 125c ($1.25) |

## Ledger Preview

| lane | market | side | source | conflict | net | paired delta |
|---|---|---|---|---|---:|---:|
| `dual_lane` | `KXBTC15M-26MAY071100-00` | yes | approved_entry | `same_market_live_side_flip` | -166c ($-1.66) | -186c ($-1.86) |
| `live_v28` | `KXBTC15M-26MAY071100-00` | no,yes | live_execution_events | `same_market_live_side_flip` | 20c ($0.20) | -186c ($-1.86) |
| `dual_lane` | `KXBTC15M-26MAY071015-15` | no | approved_entry | `same_market_live_side_flip` | -162c ($-1.62) | -156c ($-1.56) |
| `live_v28` | `KXBTC15M-26MAY071015-15` | no,yes | live_execution_events | `same_market_live_side_flip` | -6c ($-0.06) | -156c ($-1.56) |
| `dual_lane` | `KXBTC15M-26MAY070945-45` | no | approved_entry | `same_market_same_side` | 28c ($0.28) | -122c ($-1.22) |
| `live_v28` | `KXBTC15M-26MAY070945-45` | no | live_execution_events | `same_market_same_side` | 150c ($1.50) | -122c ($-1.22) |
| `dual_lane` | `KXBTC15M-26MAY071145-45` | yes | rejected_actionable | `same_market_same_side` | 46c ($0.46) | -60c ($-0.60) |
| `live_v28` | `KXBTC15M-26MAY071145-45` | yes | live_execution_events | `same_market_same_side` | 106c ($1.06) | -60c ($-0.60) |
| `dual_lane` | `KXBTC15M-26MAY070915-15` | no | approved_entry | `same_market_same_side` | 20c ($0.20) | -36c ($-0.36) |
| `live_v28` | `KXBTC15M-26MAY070915-15` | no | live_execution_events | `same_market_same_side` | 56c ($0.56) | -36c ($-0.36) |
| `dual_lane` | `KXBTC15M-26MAY071030-30` | no | rejected_actionable | `same_market_same_side` | 7c ($0.07) | -30c ($-0.30) |
| `live_v28` | `KXBTC15M-26MAY071030-30` | no | live_execution_events | `same_market_same_side` | 37c ($0.37) | -30c ($-0.30) |
| `dual_lane` | `KXBTC15M-26MAY071130-30` | no | approved_entry | `same_market_same_side` | 13c ($0.13) | -29c ($-0.29) |
| `live_v28` | `KXBTC15M-26MAY071130-30` | no | live_execution_events | `same_market_same_side` | 42c ($0.42) | -29c ($-0.29) |
| `dual_lane` | `KXBTC15M-26MAY071300-00` | yes | rejected_actionable | `dual_lane_only` | -10c ($-0.10) | -10c ($-0.10) |
| `dual_lane` | `KXBTC15M-26MAY071045-45` | no | approved_entry | `same_market_same_side` | 22c ($0.22) | -1c ($-0.01) |
| `live_v28` | `KXBTC15M-26MAY071045-45` | no | live_execution_events | `same_market_same_side` | 23c ($0.23) | -1c ($-0.01) |
| `dual_lane` | `KXBTC15M-26MAY071230-30` | yes | approved_entry | `same_market_same_side` | 21c ($0.21) | 43c ($0.43) |
| `live_v28` | `KXBTC15M-26MAY071230-30` | yes | live_execution_events | `same_market_same_side` | -22c ($-0.22) | 43c ($0.43) |
| `dual_lane` | `KXBTC15M-26MAY071115-15` | yes | approved_entry | `same_market_same_side` | 32c ($0.32) | 45c ($0.45) |
| `live_v28` | `KXBTC15M-26MAY071115-15` | yes | live_execution_events | `same_market_same_side` | -13c ($-0.13) | 45c ($0.45) |
| `dual_lane` | `KXBTC15M-26MAY071200-00` | no | approved_entry | `dual_lane_only` | 46c ($0.46) | 46c ($0.46) |
| `dual_lane` | `KXBTC15M-26MAY071315-15` | yes | approved_entry | `same_market_same_side` | 44c ($0.44) | 52c ($0.52) |
| `live_v28` | `KXBTC15M-26MAY071315-15` | yes | live_execution_events | `same_market_same_side` | -8c ($-0.08) | 52c ($0.52) |
| `dual_lane` | `KXBTC15M-26MAY071215-15` | no | approved_entry | `same_market_same_side` | 20c ($0.20) | 65c ($0.65) |
| `live_v28` | `KXBTC15M-26MAY071215-15` | no | live_execution_events | `same_market_same_side` | -45c ($-0.45) | 65c ($0.65) |
| `dual_lane` | `KXBTC15M-26MAY070930-30` | yes | approved_entry | `same_market_same_side` | 40c ($0.40) | 68c ($0.68) |
| `live_v28` | `KXBTC15M-26MAY070930-30` | yes | live_execution_events | `same_market_same_side` | -28c ($-0.28) | 68c ($0.68) |
| `dual_lane` | `KXBTC15M-26MAY071000-00` | no | approved_entry | `same_market_same_side` | 58c ($0.58) | 130c ($1.30) |
| `live_v28` | `KXBTC15M-26MAY071000-00` | no | live_execution_events | `same_market_same_side` | -72c ($-0.72) | 130c ($1.30) |
