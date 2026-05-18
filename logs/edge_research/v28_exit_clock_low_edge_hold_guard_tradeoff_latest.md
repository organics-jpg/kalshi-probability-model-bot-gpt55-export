# v28 Exit-Clock Low-Edge Hold Guard Tradeoff

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-07T17:18:22.122216+00:00`
- Base rule: `exit_fair_drawdown_cents <= 5 and exit_cents >= 50 and entry_ask_cents <= 80`
- Full broad selected/delta/harm: `33` / `1159c ($11.59)` / `1`
- Best clean policy: `base_exit_hold_raw_edge_ge_7_else_weight_0`
- Best clean selected/delta/net: `19` / `869c ($8.69)` / `1232c ($12.32)`
- Best clean >=30 policy: `None`
- Best clean >=30 selected/delta/net: `None` / `0c ($0.00)` / `0c ($0.00)`
- Blockers: `research_only, not_frozen_forward, diagnostic_snapshot_tradeoff, no_clean_tradeoff_with_30_selected_decisions`

## Read

- The broad hold pocket has strong diagnostic recovery but one low-edge false hold.
- Raw-edge hard guarding removes the false hold but leaves the rule below the 30-decision floor.
- Low-edge fractional shrink still creates a new loss unless the harmful row is effectively excluded, so this is not a clean continuous-sizing candidate yet.

## Policy Frontier

| policy | selected | delta | net | helpful/harmful/flat | flips/new losses | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| `base_exit_hold_raw_edge_ge_7_else_weight_0` | 19 | 869c ($8.69) | 1232c ($12.32) | 19/0/0 | 9/0 | 12 | diagnostic_snapshot_tradeoff, not_frozen_forward, selected_decisions_lt_30 |
| `base_exit_hold_raw_edge_ge_8_else_weight_0` | 15 | 703c ($7.03) | 1066c ($10.66) | 15/0/0 | 6/0 | 10 | diagnostic_snapshot_tradeoff, not_frozen_forward, selected_decisions_lt_30 |
| `base_exit_hold_raw_edge_ge_9_else_weight_0` | 13 | 597c ($5.97) | 960c ($9.60) | 13/0/0 | 5/0 | 9 | diagnostic_snapshot_tradeoff, not_frozen_forward, selected_decisions_lt_30 |
| `base_exit_hold_raw_edge_ge_10_else_weight_0` | 12 | 535c ($5.35) | 898c ($8.98) | 12/0/0 | 4/0 | 8 | diagnostic_snapshot_tradeoff, not_frozen_forward, selected_decisions_lt_30 |
| `base_exit_hold_raw_edge_ge_12_else_weight_0` | 8 | 390c ($3.90) | 753c ($7.53) | 8/0/0 | 2/0 | 7 | diagnostic_snapshot_tradeoff, not_frozen_forward, selected_decisions_lt_30 |
| `base_exit_hold_raw_edge_ge_7_else_weight_0.01` | 33 | 872c ($8.72) | 1235c ($12.35) | 32/1/0 | 9/0 | 12 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present |
| `base_exit_hold_raw_edge_ge_8_else_weight_0.01` | 33 | 708c ($7.08) | 1071c ($10.71) | 32/1/0 | 6/0 | 10 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present |
| `base_exit_hold_raw_edge_ge_9_else_weight_0.01` | 33 | 603c ($6.03) | 966c ($9.66) | 32/1/0 | 5/0 | 9 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present |
| `base_exit_hold_raw_edge_ge_10_else_weight_0.01` | 33 | 541c ($5.41) | 904c ($9.04) | 32/1/0 | 4/0 | 9 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present |
| `base_exit_hold_raw_edge_ge_12_else_weight_0.01` | 33 | 398c ($3.98) | 761c ($7.61) | 32/1/0 | 2/0 | 7 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present |
| `base_exit_hold_raw_edge_ge_4_else_weight_0` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_4_else_weight_0.01` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_4_else_weight_0.05` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_4_else_weight_0.1` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_4_else_weight_0.25` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_4_else_weight_0.5` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_4_else_weight_1` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_5_else_weight_1` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_6_else_weight_1` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_6.5_else_weight_1` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_7_else_weight_1` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_8_else_weight_1` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_9_else_weight_1` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_10_else_weight_1` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_12_else_weight_1` | 33 | 1159c ($11.59) | 1522c ($15.22) | 32/1/0 | 16/1 | 15 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_7_else_weight_0.5` | 33 | 1014c ($10.14) | 1377c ($13.77) | 32/1/0 | 16/1 | 13 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_5_else_weight_0.5` | 33 | 1013c ($10.13) | 1376c ($13.76) | 32/1/0 | 16/1 | 13 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_7_else_weight_0.25` | 33 | 942c ($9.41) | 1304c ($13.04) | 32/1/0 | 15/1 | 13 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_5_else_weight_0.25` | 33 | 940c ($9.40) | 1303c ($13.03) | 32/1/0 | 16/1 | 13 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_6_else_weight_0.5` | 33 | 935c ($9.35) | 1298c ($12.98) | 32/1/0 | 16/1 | 12 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_6.5_else_weight_0.5` | 33 | 935c ($9.35) | 1298c ($12.98) | 32/1/0 | 16/1 | 12 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_8_else_weight_0.5` | 33 | 931c ($9.31) | 1294c ($12.94) | 32/1/0 | 16/1 | 12 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_7_else_weight_0.1` | 33 | 898c ($8.98) | 1261c ($12.61) | 32/1/0 | 9/1 | 12 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_5_else_weight_0.1` | 33 | 896c ($8.96) | 1259c ($12.59) | 32/1/0 | 11/1 | 12 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_7_else_weight_0.05` | 33 | 884c ($8.84) | 1246c ($12.46) | 32/1/0 | 9/1 | 12 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_5_else_weight_0.05` | 33 | 882c ($8.82) | 1245c ($12.45) | 32/1/0 | 11/1 | 12 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_9_else_weight_0.5` | 33 | 878c ($8.78) | 1241c ($12.41) | 32/1/0 | 16/1 | 12 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_5_else_weight_0.01` | 33 | 870c ($8.70) | 1233c ($12.33) | 32/1/0 | 11/1 | 12 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_5_else_weight_0` | 23 | 867c ($8.67) | 1230c ($12.30) | 22/1/0 | 11/1 | 12 | diagnostic_snapshot_tradeoff, not_frozen_forward, selected_decisions_lt_30, harmful_hold_rows_present, new_losses_created |
| `base_exit_hold_raw_edge_ge_10_else_weight_0.5` | 33 | 847c ($8.47) | 1210c ($12.10) | 32/1/0 | 16/1 | 12 | diagnostic_snapshot_tradeoff, not_frozen_forward, harmful_hold_rows_present, new_losses_created |
