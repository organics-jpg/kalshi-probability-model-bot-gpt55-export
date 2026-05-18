# v28 Exit-Clock Broad Hold Neighbor Autopsy

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-07T17:23:04.676140+00:00`
- Base rule: `exit_fair_drawdown_cents <= 5 and exit_cents >= 50 and entry_ask_cents <= 80`
- Broad selected/delta/helpful-harmful-newloss: `33` / `1159c ($11.59)` / `32-1-1`
- Low-edge <7 selected/delta/helpful-harmful-newloss: `14` / `290c ($2.90)` / `13-1-1`
- High-edge >=7 selected/delta/helpful-harmful-newloss: `19` / `869c ($8.69)` / `19-0-0`
- Worst harmful row: `KXBTC15M-26MAY071015-15` / `no` / delta `-158c ($-1.58)` / raw edge `6.609185`
- Blockers: `research_only, not_frozen_forward, diagnostic_snapshot_autopsy, clean_high_edge_survivor_lt_30, low_edge_slice_contains_false_hold`

## Read

- The broad hold pocket's damage is concentrated in a single low-edge false hold, but the low-edge slice also contains useful clipped-winner recovery.
- A hard raw-edge guard removes the false hold but leaves fewer than 30 selected decisions.
- This supports mechanism research around entry confidence plus exit-state hold value, not a freezeable rule from the fixed snapshot.

## Buckets

| feature | bucket | rows | delta | helpful/harmful/new losses | cushion |
|---|---|---:|---:|---:|---:|
| `entry_raw_edge_cents` | `5_6` | 3 | 156c ($1.56) | 3/0/0 | 1 |
| `entry_raw_edge_cents` | `6_7` | 1 | -158c ($-1.58) | 0/1/1 | 0 |
| `entry_raw_edge_cents` | `7_8` | 4 | 166c ($1.66) | 4/0/0 | 1 |
| `entry_raw_edge_cents` | `8_10` | 3 | 168c ($1.68) | 3/0/0 | 1 |
| `entry_raw_edge_cents` | `gte10` | 12 | 535c ($5.35) | 12/0/0 | 7 |
| `entry_raw_edge_cents` | `lt5` | 10 | 292c ($2.92) | 10/0/0 | 4 |
| `entry_ask_cents` | `55_65` | 1 | 54c ($0.54) | 1/0/0 | 0 |
| `entry_ask_cents` | `65_75` | 10 | 471c ($4.71) | 10/0/0 | 5 |
| `entry_ask_cents` | `75_80` | 22 | 634c ($6.34) | 21/1/1 | 7 |
| `exit_cents` | `60_70` | 5 | 350c ($3.50) | 5/0/0 | 2 |
| `exit_cents` | `70_80` | 16 | 643c ($6.43) | 15/1/1 | 5 |
| `exit_cents` | `gte80` | 12 | 166c ($1.66) | 12/0/0 | 5 |
| `exit_p_hold` | `65_75` | 7 | 430c ($4.30) | 7/0/0 | 4 |
| `exit_p_hold` | `75_85` | 17 | 617c ($6.17) | 16/1/1 | 5 |
| `exit_p_hold` | `gte85` | 8 | 58c ($0.58) | 8/0/0 | 3 |
| `exit_p_hold` | `lt65` | 1 | 54c ($0.54) | 1/0/0 | 0 |

## Nearest Helpful Neighbors

| market | side | distance | delta | raw edge | ask | exit | p_hold | fair drawdown |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY061030-30` | `yes` | 0.249 | 54c ($0.54) | 5.567 | 78 | 73 | 0.796 | -1.646 |
| `KXBTC15M-26MAY060645-45` | `yes` | 0.264 | 56c ($0.56) | 7.367 | 78 | 72 | 0.780 | 0.021 |
| `KXBTC15M-26MAY060045-45` | `no` | 0.278 | 52c ($0.52) | 4.593 | 79 | 74 | 0.795 | -0.473 |
| `KXBTC15M-26MAY051745-45` | `no` | 0.291 | 56c ($0.56) | 7.646 | 77 | 72 | 0.791 | -2.111 |
| `KXBTC15M-26MAY060630-30` | `yes` | 0.355 | 54c ($0.54) | 4.750 | 79 | 73 | 0.778 | 1.223 |
| `KXBTC15M-26MAY060245-45` | `yes` | 0.393 | 52c ($0.52) | 7.797 | 77 | 74 | 0.749 | 2.061 |
| `KXBTC15M-26MAY071215-15` | `no` | 0.404 | 42c ($0.42) | 5.595 | 78 | 79 | 0.752 | 2.770 |
| `KXBTC15M-26MAY060245-45` | `yes` | 0.459 | 48c ($0.48) | 4.253 | 80 | 76 | 0.793 | 2.667 |
