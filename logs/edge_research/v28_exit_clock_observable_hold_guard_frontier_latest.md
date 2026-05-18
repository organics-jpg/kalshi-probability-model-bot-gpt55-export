# v28 Exit-Clock Observable Hold-Guard Frontier

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-07T17:15:50.129117+00:00`
- Rows / rules scanned: `100` / `5661`
- Best clean rule: `exit_fair_drawdown_cents_le_5__and__exit_cents_ge_50__and__entry_raw_edge_cents_ge_10`
- Best clean selected/delta/net: `13` / `537c ($5.37)` / `900c ($9.00)`
- Best clean >=30 selected rule: `None`
- Best clean >=30 selected/delta/net: `None` / `0c ($0.00)` / `0c ($0.00)`
- Blockers: `research_only, not_frozen_forward, diagnostic_snapshot_scan, no_clean_rule_with_30_selected_decisions`

## Read

- This fixed-denominator scan is diagnostic only.
- Clean observable hold guards exist, but the clean high-delta rules are sparse.
- No clean rule clears the 30 selected-decision evidence floor.

## Top Frontier

| rule | selected | delta | candidate net | helpful/harmful/flat | flips/new losses | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| `exit_fair_drawdown_cents_le_5__and__exit_cents_ge_50__and__entry_raw_edge_cents_ge_10` | 13 | 537c ($5.37) | 900c ($9.00) | 13/0/0 | 4/0 | 9 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_5__and__exit_cents_ge_60__and__entry_raw_edge_cents_ge_10` | 13 | 537c ($5.37) | 900c ($9.00) | 13/0/0 | 4/0 | 9 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_p_hold_ge_0p6__and__exit_fair_drawdown_cents_le_5__and__entry_raw_edge_cents_ge_10` | 12 | 483c ($4.83) | 846c ($8.46) | 12/0/0 | 4/0 | 8 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_5__and__entry_raw_edge_cents_ge_10__and__entry_ask_cents_ge_60` | 12 | 483c ($4.83) | 846c ($8.46) | 12/0/0 | 4/0 | 8 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_cents_ge_70__and__entry_raw_edge_cents_ge_10` | 12 | 423c ($4.23) | 786c ($7.86) | 12/0/0 | 2/0 | 7 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_cents_ge_70__and__entry_abs_d_sigma_ge_0p85__and__entry_raw_edge_cents_ge_10` | 12 | 423c ($4.23) | 786c ($7.86) | 12/0/0 | 2/0 | 7 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_cents_ge_70__and__entry_raw_edge_cents_ge_10__and__entry_ask_cents_le_80` | 11 | 421c ($4.21) | 784c ($7.84) | 11/0/0 | 2/0 | 7 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_p_hold_ge_0p7__and__exit_fair_drawdown_cents_le_5__and__entry_raw_edge_cents_ge_10` | 10 | 373c ($3.73) | 736c ($7.36) | 10/0/0 | 3/0 | 7 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_p_hold_ge_0p6__and__exit_cents_ge_70__and__entry_raw_edge_cents_ge_10` | 11 | 369c ($3.69) | 732c ($7.32) | 11/0/0 | 2/0 | 7 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_cents_ge_70__and__entry_raw_edge_cents_ge_10__and__entry_ask_cents_ge_60` | 11 | 369c ($3.69) | 732c ($7.32) | 11/0/0 | 2/0 | 7 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `entry_abs_d_sigma_ge_1__and__entry_ask_cents_le_80` | 7 | 368c ($3.68) | 731c ($7.31) | 6/0/1 | 4/0 | 7 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `entry_abs_d_sigma_ge_1__and__entry_raw_edge_cents_ge_5__and__entry_ask_cents_le_80` | 7 | 368c ($3.68) | 731c ($7.31) | 6/0/1 | 4/0 | 7 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_cents_ge_50__and__entry_abs_d_sigma_ge_1__and__entry_ask_cents_le_80` | 6 | 368c ($3.68) | 731c ($7.31) | 6/0/0 | 4/0 | 7 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_10__and__exit_cents_ge_70__and__entry_raw_edge_cents_ge_10` | 11 | 363c ($3.63) | 726c ($7.26) | 11/0/0 | 1/0 | 7 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_15__and__exit_cents_ge_70__and__entry_raw_edge_cents_ge_10` | 11 | 363c ($3.63) | 726c ($7.26) | 11/0/0 | 1/0 | 7 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_5__and__entry_raw_edge_cents_ge_10__and__entry_ask_cents_ge_70` | 9 | 363c ($3.63) | 726c ($7.26) | 9/0/0 | 4/0 | 7 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_5__and__exit_cents_ge_70__and__entry_raw_edge_cents_ge_10` | 10 | 321c ($3.21) | 684c ($6.84) | 10/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_cents_ge_60__and__entry_ask_cents_le_70` | 6 | 310c ($3.10) | 673c ($6.73) | 6/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_5__and__exit_cents_ge_50__and__entry_ask_cents_le_70` | 6 | 310c ($3.10) | 673c ($6.73) | 6/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_5__and__exit_cents_ge_60__and__entry_ask_cents_le_70` | 6 | 310c ($3.10) | 673c ($6.73) | 6/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_10__and__exit_cents_ge_60__and__entry_ask_cents_le_70` | 6 | 310c ($3.10) | 673c ($6.73) | 6/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_15__and__exit_cents_ge_60__and__entry_ask_cents_le_70` | 6 | 310c ($3.10) | 673c ($6.73) | 6/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_cents_ge_60__and__entry_raw_edge_cents_ge_5__and__entry_ask_cents_le_70` | 6 | 310c ($3.10) | 673c ($6.73) | 6/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_cents_ge_60__and__entry_raw_edge_cents_ge_10__and__entry_ask_cents_le_70` | 6 | 310c ($3.10) | 673c ($6.73) | 6/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `entry_abs_d_sigma_ge_1__and__entry_raw_edge_cents_ge_10` | 7 | 308c ($3.08) | 671c ($6.71) | 6/0/1 | 3/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_cents_ge_50__and__entry_abs_d_sigma_ge_1__and__entry_raw_edge_cents_ge_10` | 6 | 308c ($3.08) | 671c ($6.71) | 6/0/0 | 3/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `entry_abs_d_sigma_ge_1__and__entry_raw_edge_cents_ge_10__and__entry_ask_cents_ge_60` | 6 | 308c ($3.08) | 671c ($6.71) | 6/0/0 | 3/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `entry_abs_d_sigma_ge_1__and__entry_raw_edge_cents_ge_10__and__entry_ask_cents_le_80` | 6 | 306c ($3.06) | 669c ($6.69) | 5/0/1 | 3/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_0__and__entry_raw_edge_cents_ge_10` | 9 | 303c ($3.03) | 666c ($6.66) | 9/0/0 | 2/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_p_hold_ge_0p6__and__exit_fair_drawdown_cents_le_0__and__entry_raw_edge_cents_ge_10` | 9 | 303c ($3.03) | 666c ($6.66) | 9/0/0 | 2/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_p_hold_ge_0p7__and__exit_fair_drawdown_cents_le_0__and__entry_raw_edge_cents_ge_10` | 9 | 303c ($3.03) | 666c ($6.66) | 9/0/0 | 2/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_0__and__exit_cents_ge_50__and__entry_raw_edge_cents_ge_10` | 9 | 303c ($3.03) | 666c ($6.66) | 9/0/0 | 2/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_0__and__exit_cents_ge_60__and__entry_raw_edge_cents_ge_10` | 9 | 303c ($3.03) | 666c ($6.66) | 9/0/0 | 2/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_0__and__entry_abs_d_sigma_ge_0p85__and__entry_raw_edge_cents_ge_10` | 9 | 303c ($3.03) | 666c ($6.66) | 9/0/0 | 2/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_0__and__entry_raw_edge_cents_ge_10__and__entry_ask_cents_ge_60` | 9 | 303c ($3.03) | 666c ($6.66) | 9/0/0 | 2/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_0__and__entry_raw_edge_cents_ge_10__and__entry_ask_cents_le_80` | 8 | 301c ($3.01) | 664c ($6.64) | 8/0/0 | 2/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_n5__and__entry_ask_cents_le_80` | 13 | 295c ($2.95) | 658c ($6.58) | 13/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_p_hold_ge_0p6__and__exit_fair_drawdown_cents_le_n5__and__entry_ask_cents_le_80` | 13 | 295c ($2.95) | 658c ($6.58) | 13/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_p_hold_ge_0p7__and__exit_fair_drawdown_cents_le_n5__and__entry_ask_cents_le_80` | 13 | 295c ($2.95) | 658c ($6.58) | 13/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_n5__and__exit_cents_ge_50__and__entry_ask_cents_le_80` | 13 | 295c ($2.95) | 658c ($6.58) | 13/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_n5__and__exit_cents_ge_60__and__entry_ask_cents_le_80` | 13 | 295c ($2.95) | 658c ($6.58) | 13/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_n5__and__exit_cents_ge_70__and__entry_ask_cents_le_80` | 13 | 295c ($2.95) | 658c ($6.58) | 13/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_n5__and__entry_raw_edge_cents_ge_5` | 12 | 291c ($2.91) | 654c ($6.54) | 12/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_p_hold_ge_0p6__and__exit_fair_drawdown_cents_le_n5__and__entry_raw_edge_cents_ge_5` | 12 | 291c ($2.91) | 654c ($6.54) | 12/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_p_hold_ge_0p7__and__exit_fair_drawdown_cents_le_n5__and__entry_raw_edge_cents_ge_5` | 12 | 291c ($2.91) | 654c ($6.54) | 12/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_n5__and__exit_cents_ge_50__and__entry_raw_edge_cents_ge_5` | 12 | 291c ($2.91) | 654c ($6.54) | 12/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_n5__and__exit_cents_ge_60__and__entry_raw_edge_cents_ge_5` | 12 | 291c ($2.91) | 654c ($6.54) | 12/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_n5__and__exit_cents_ge_70__and__entry_raw_edge_cents_ge_5` | 12 | 291c ($2.91) | 654c ($6.54) | 12/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_n5__and__entry_abs_d_sigma_ge_0p85__and__entry_raw_edge_cents_ge_5` | 12 | 291c ($2.91) | 654c ($6.54) | 12/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| `exit_fair_drawdown_cents_le_n5__and__entry_raw_edge_cents_ge_5__and__entry_ask_cents_ge_60` | 12 | 291c ($2.91) | 654c ($6.54) | 12/0/0 | 1/0 | 6 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
