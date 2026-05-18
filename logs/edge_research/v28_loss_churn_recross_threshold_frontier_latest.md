# v28 Loss-Churn Recross Threshold Frontier

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-07T17:12:13.059468+00:00`
- Source snapshot: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_exit_clock_materialized_snapshot_latest.json`
- Joined / scored rows: `100` / `100`
- Best clean threshold/weight: `0.45` / `1.0`
- Best clean selected/delta/net: `8` / `124c ($1.24)` / `487c ($4.87)`
- Best full-hold selected/delta/net: `8` / `124c ($1.24)` / `487c ($4.87)`
- Blockers: `research_only, not_frozen_forward, snapshot_threshold_scan_not_watch, best_clean_selected_decisions_lt_30`

## Read

- The fixed exit-clock denominator keeps the recross signal clean but sparse.
- No scanned threshold reaches the 30 selected-decision evidence floor.
- Use this as mechanism evidence only; do not freeze a recross exit watch from the snapshot scan.

## Frontier

| threshold | weight | selected | delta | candidate net | helpful/harmful/flat | flips/new losses | cushion | blockers |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 0.45 | 1.0 | 8 | 124c ($1.24) | 487c ($4.87) | 4/0/4 | 0/0 | 4 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| 0.45 | 0.75 | 8 | 93c ($0.93) | 456c ($4.56) | 4/0/4 | 0/0 | 4 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| 0.5 | 1.0 | 6 | 82c ($0.82) | 445c ($4.45) | 3/0/3 | 0/0 | 4 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| 0.55 | 1.0 | 4 | 82c ($0.82) | 445c ($4.45) | 3/0/1 | 0/0 | 4 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| 0.45 | 0.5 | 8 | 62c ($0.62) | 425c ($4.25) | 4/0/4 | 0/0 | 4 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| 0.5 | 0.75 | 6 | 62c ($0.61) | 424c ($4.25) | 3/0/3 | 0/0 | 4 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| 0.55 | 0.75 | 4 | 62c ($0.61) | 424c ($4.25) | 3/0/1 | 0/0 | 4 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| 0.5 | 0.5 | 6 | 41c ($0.41) | 404c ($4.04) | 3/0/3 | 0/0 | 4 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| 0.55 | 0.5 | 4 | 41c ($0.41) | 404c ($4.04) | 3/0/1 | 0/0 | 4 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| 0.45 | 0.25 | 8 | 31c ($0.31) | 394c ($3.94) | 4/0/4 | 0/0 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| 0.5 | 0.25 | 6 | 20c ($0.20) | 384c ($3.83) | 3/0/3 | 0/0 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| 0.55 | 0.25 | 4 | 20c ($0.20) | 384c ($3.83) | 3/0/1 | 0/0 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30 |
| 0.6 | 0.25 | 0 | 0c ($0.00) | 363c ($3.63) | 0/0/0 | 0/0 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30, delta_not_positive |
| 0.6 | 0.5 | 0 | 0c ($0.00) | 363c ($3.63) | 0/0/0 | 0/0 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30, delta_not_positive |
| 0.6 | 0.75 | 0 | 0c ($0.00) | 363c ($3.63) | 0/0/0 | 0/0 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30, delta_not_positive |
| 0.6 | 1.0 | 0 | 0c ($0.00) | 363c ($3.63) | 0/0/0 | 0/0 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30, delta_not_positive |
| 0.4 | 1.0 | 12 | 100c ($1.00) | 463c ($4.63) | 6/1/5 | 2/1 | 4 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30, harmful_hold_rows_present, new_losses_created |
| 0.4 | 0.75 | 12 | 75c ($0.75) | 438c ($4.38) | 6/1/5 | 2/1 | 4 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30, harmful_hold_rows_present, new_losses_created |
| 0.4 | 0.5 | 12 | 50c ($0.50) | 413c ($4.13) | 6/1/5 | 1/1 | 4 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30, harmful_hold_rows_present, new_losses_created |
| 0.4 | 0.25 | 12 | 25c ($0.25) | 388c ($3.88) | 6/1/5 | 0/1 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30, harmful_hold_rows_present, new_losses_created |
| 0.35 | 1.0 | 23 | 7c ($0.07) | 370c ($3.70) | 14/4/5 | 7/1 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30, harmful_hold_rows_present, new_losses_created |
| 0.35 | 0.75 | 23 | 5c ($0.05) | 368c ($3.68) | 14/4/5 | 7/1 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30, harmful_hold_rows_present, new_losses_created |
| 0.35 | 0.5 | 23 | 4c ($0.04) | 366c ($3.67) | 14/4/5 | 6/1 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30, harmful_hold_rows_present, new_losses_created |
| 0.35 | 0.25 | 23 | 2c ($0.02) | 365c ($3.65) | 14/4/5 | 4/1 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, selected_decisions_lt_30, harmful_hold_rows_present, new_losses_created |
| 0.3 | 0.25 | 41 | -13c ($-0.13) | 350c ($3.50) | 23/8/10 | 7/2 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, delta_not_positive, harmful_hold_rows_present, new_losses_created |
| 0.3 | 0.5 | 41 | -26c ($-0.27) | 336c ($3.37) | 23/8/10 | 12/2 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, delta_not_positive, harmful_hold_rows_present, new_losses_created |
| 0.3 | 0.75 | 41 | -40c ($-0.40) | 323c ($3.23) | 23/8/10 | 13/2 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, delta_not_positive, harmful_hold_rows_present, new_losses_created |
| 0.3 | 1.0 | 41 | -53c ($-0.53) | 310c ($3.10) | 23/8/10 | 13/2 | 3 | diagnostic_snapshot_frontier, not_frozen_forward, delta_not_positive, harmful_hold_rows_present, new_losses_created |
