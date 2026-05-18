# v28 Feature-Gate Delayed-Recheck Disaster Guard

Research-only diagnostic guard scan. No live bot changes, no orders, no new frozen rule.

- Generated UTC: `2026-05-07T08:43:54.843396+00:00`
- Base delayed rows / delta: `11` / `2272c`
- Base adverse 25/50 rows: `2` / `1`
- Best diagnostic guard by conservative sort: `reject_value_over_hold_recheck_bid_lte_82`
- Best kept delta / given up: `1528c` / `744c`
- Best adverse 25/50 kept: `0` / `0`
- Best blockers: `diagnostic_prefreeze, suppressed_decisions_lt_30, gives_up_large_recovery`

## Guard Scan

| guard | rejects | kept | kept delta | given up | adverse 25 removed/kept | adverse 50 removed/kept | rejected reasons | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|
| reject_value_over_hold_recheck_bid_lte_82 | 3 | 8 | 1528c | 744c | 2/0 | 1/0 | {'value_over_hold': 3} | diagnostic_prefreeze, suppressed_decisions_lt_30, gives_up_large_recovery |
| reject_recheck_bid_lte_85 | 6 | 5 | 450c | 1822c | 2/0 | 1/0 | {'value_over_hold': 3, 'probability_reduce': 2, 'probability_collapse': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, gives_up_large_recovery |
| reject_min_window_bid_lte_80 | 8 | 3 | 96c | 2176c | 2/0 | 1/0 | {'value_over_hold': 4, 'probability_reduce': 3, 'probability_collapse': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, gives_up_large_recovery |
| reject_recheck_bid_lte_60 | 1 | 10 | 2096c | 176c | 1/1 | 0/1 | {'value_over_hold': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, large_adverse_rows_remain |
| reject_window_drop_gte_8 | 1 | 10 | 2096c | 176c | 1/1 | 0/1 | {'value_over_hold': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, large_adverse_rows_remain |
| reject_value_over_hold_window_drop_gte_8 | 1 | 10 | 2096c | 176c | 1/1 | 0/1 | {'value_over_hold': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, large_adverse_rows_remain |
| reject_value_over_hold_min_window_lte_61 | 1 | 10 | 2096c | 176c | 1/1 | 0/1 | {'value_over_hold': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, large_adverse_rows_remain |
| reject_window_drop_gte_10 | 0 | 11 | 2272c | 0c | 0/2 | 0/1 | {} | diagnostic_prefreeze, suppressed_decisions_lt_30, no_guarded_rows, does_not_remove_large_adverse_rows, large_adverse_rows_remain |
| reject_reduce_recheck_bid_lte_76 | 1 | 10 | 1932c | 340c | 0/2 | 0/1 | {'probability_reduce': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, does_not_remove_large_adverse_rows, large_adverse_rows_remain |
| reject_recheck_bid_lte_65 | 2 | 9 | 1684c | 588c | 1/1 | 0/1 | {'value_over_hold': 1, 'probability_collapse': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, large_adverse_rows_remain, gives_up_large_recovery |
| reject_recheck_bid_lte_70 | 2 | 9 | 1684c | 588c | 1/1 | 0/1 | {'value_over_hold': 1, 'probability_collapse': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, large_adverse_rows_remain, gives_up_large_recovery |
| reject_window_drop_gte_5 | 3 | 8 | 1528c | 744c | 1/1 | 0/1 | {'value_over_hold': 2, 'probability_collapse': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, large_adverse_rows_remain, gives_up_large_recovery |
| reject_window_drop_gte_3 | 5 | 6 | 1448c | 824c | 1/1 | 0/1 | {'value_over_hold': 4, 'probability_collapse': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, large_adverse_rows_remain, gives_up_large_recovery |
| reject_min_window_bid_lte_65 | 3 | 8 | 1358c | 914c | 1/1 | 0/1 | {'value_over_hold': 1, 'probability_collapse': 1, 'probability_reduce': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, large_adverse_rows_remain, gives_up_large_recovery |
| reject_recheck_bid_lte_75 | 3 | 8 | 1328c | 944c | 1/1 | 0/1 | {'value_over_hold': 2, 'probability_collapse': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, large_adverse_rows_remain, gives_up_large_recovery |
| reject_recheck_bid_lte_80 | 4 | 7 | 988c | 1284c | 1/1 | 0/1 | {'value_over_hold': 2, 'probability_reduce': 1, 'probability_collapse': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, large_adverse_rows_remain, gives_up_large_recovery |
| reject_window_drop_gte_0 | 8 | 3 | 766c | 1506c | 1/1 | 0/1 | {'value_over_hold': 5, 'probability_reduce': 2, 'probability_collapse': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, large_adverse_rows_remain, gives_up_large_recovery |
| reject_min_window_bid_lte_70 | 6 | 5 | 464c | 1808c | 1/1 | 0/1 | {'value_over_hold': 2, 'probability_reduce': 3, 'probability_collapse': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, large_adverse_rows_remain, gives_up_large_recovery |
| reject_min_window_bid_lte_75 | 6 | 5 | 464c | 1808c | 1/1 | 0/1 | {'value_over_hold': 2, 'probability_reduce': 3, 'probability_collapse': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, large_adverse_rows_remain, gives_up_large_recovery |
| reject_min_window_bid_lte_60 | 1 | 10 | 1860c | 412c | 0/2 | 0/1 | {'probability_collapse': 1} | diagnostic_prefreeze, suppressed_decisions_lt_30, does_not_remove_large_adverse_rows, large_adverse_rows_remain, gives_up_large_recovery |
| reject_reduce_window_drop_gte_0 | 2 | 9 | 1606c | 666c | 0/2 | 0/1 | {'probability_reduce': 2} | diagnostic_prefreeze, suppressed_decisions_lt_30, does_not_remove_large_adverse_rows, large_adverse_rows_remain, gives_up_large_recovery |

## Interpretation

- All rows are diagnostic/prefreeze; this is not promotion evidence.
- A usable disaster guard should remove large adverse paths without giving back most delayed-recheck recovery.
- If every clean-looking guard either leaves large adverse rows or sacrifices too much recovery, keep the frozen delayed-recheck watch unchanged until strict rows arrive.
