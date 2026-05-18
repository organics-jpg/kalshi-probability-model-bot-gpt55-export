# v28 Soft-Frontier Delayed-Recheck Disaster Guard

Research-only diagnostic scan. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:59.058350+00:00`
- Primary rescue variant: `drop15_bid60`
- Base comparison variant: `base_delay60_bid60_drop10`

## Interpretation

- Research-only disaster-guard scan; no live bot changes or orders.
- Best guard no_guard has net 1665.5c, delta vs base 164.0c, guarded exits 0, helpful/harmful 33/0, worst pre-guard excursion -54.0c, blockers ['diagnostic_prefreeze', 'large_adverse_before_guard', 'extreme_adverse_before_guard'].
- A guard is only interesting if it preserves improvement over base while removing large adverse path risk.

## Guards

| rank | guard | guarded exits | H/H | base net | no-guard net | guarded net | delta base | delta no guard | losses | worst pre-guard | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `no_guard` | 0 | 33/0 | 1501.50 | 1665.50 | 1665.50 | 164.00 | 0.00 | 7 | -54.00 | diagnostic_prefreeze, large_adverse_before_guard, extreme_adverse_before_guard |
| 2 | `drop20_only` | 1 | 32/1 | 1501.50 | 1665.50 | 1505.50 | 4.00 | -160.00 | 8 | -54.00 | diagnostic_prefreeze, guarded_harmful_vs_original_exit, large_adverse_before_guard, extreme_adverse_before_guard |
| 3 | `drop25_only` | 1 | 32/1 | 1501.50 | 1665.50 | 1505.50 | 4.00 | -160.00 | 8 | -54.00 | diagnostic_prefreeze, guarded_harmful_vs_original_exit, large_adverse_before_guard, extreme_adverse_before_guard |
| 4 | `drop30_only` | 1 | 32/1 | 1501.50 | 1665.50 | 1505.50 | 4.00 | -160.00 | 8 | -54.00 | diagnostic_prefreeze, guarded_harmful_vs_original_exit, large_adverse_before_guard, extreme_adverse_before_guard |
| 5 | `floor55_only` | 1 | 32/1 | 1501.50 | 1665.50 | 1505.50 | 4.00 | -160.00 | 8 | -54.00 | diagnostic_prefreeze, guarded_harmful_vs_original_exit, large_adverse_before_guard, extreme_adverse_before_guard |
| 6 | `floor50_only` | 1 | 32/1 | 1501.50 | 1665.50 | 1505.50 | 4.00 | -160.00 | 8 | -54.00 | diagnostic_prefreeze, guarded_harmful_vs_original_exit, large_adverse_before_guard, extreme_adverse_before_guard |
| 7 | `floor45_only` | 1 | 32/1 | 1501.50 | 1665.50 | 1505.50 | 4.00 | -160.00 | 8 | -54.00 | diagnostic_prefreeze, guarded_harmful_vs_original_exit, large_adverse_before_guard, extreme_adverse_before_guard |
| 8 | `drop20_or_floor50` | 1 | 32/1 | 1501.50 | 1665.50 | 1505.50 | 4.00 | -160.00 | 8 | -54.00 | diagnostic_prefreeze, guarded_harmful_vs_original_exit, large_adverse_before_guard, extreme_adverse_before_guard |
| 9 | `drop25_or_floor50` | 1 | 32/1 | 1501.50 | 1665.50 | 1505.50 | 4.00 | -160.00 | 8 | -54.00 | diagnostic_prefreeze, guarded_harmful_vs_original_exit, large_adverse_before_guard, extreme_adverse_before_guard |
| 10 | `drop25_or_floor45` | 1 | 32/1 | 1501.50 | 1665.50 | 1505.50 | 4.00 | -160.00 | 8 | -54.00 | diagnostic_prefreeze, guarded_harmful_vs_original_exit, large_adverse_before_guard, extreme_adverse_before_guard |
| 11 | `drop30_or_floor45` | 1 | 32/1 | 1501.50 | 1665.50 | 1505.50 | 4.00 | -160.00 | 8 | -54.00 | diagnostic_prefreeze, guarded_harmful_vs_original_exit, large_adverse_before_guard, extreme_adverse_before_guard |
| 12 | `drop30_or_floor40` | 1 | 32/1 | 1501.50 | 1665.50 | 1505.50 | 4.00 | -160.00 | 8 | -54.00 | diagnostic_prefreeze, guarded_harmful_vs_original_exit, large_adverse_before_guard, extreme_adverse_before_guard |
| 13 | `drop15_only` | 2 | 31/2 | 1501.50 | 1665.50 | 1425.50 | -76.00 | -240.00 | 9 | -54.00 | diagnostic_prefreeze, guarded_harmful_vs_original_exit, does_not_improve_base_delayed_recheck, large_adverse_before_guard, extreme_adverse_before_guard |
| 14 | `drop15_or_floor55` | 2 | 31/2 | 1501.50 | 1665.50 | 1425.50 | -76.00 | -240.00 | 9 | -54.00 | diagnostic_prefreeze, guarded_harmful_vs_original_exit, does_not_improve_base_delayed_recheck, large_adverse_before_guard, extreme_adverse_before_guard |

## Worst Rows By Best Guard

| market | side | source | reason | entry | recheck | min until guard | min after recheck | disposition | guard bid | weighted candidate | delta vs current |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|
| KXBTC15M-26MAY062100-00 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 61.00 | 74.00 | -54.00 | -54.00 | hold_to_settlement | n/a | 78.00 | 64.00 |
| KXBTC15M-26MAY060600-00 | no | approved_entry | mushroom_v28_exit_value_over_hold | 75.00 | 75.00 | -17.00 | -17.00 | hold_to_settlement | n/a | 50.00 | 38.00 |
| KXBTC15M-26MAY070030-30 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 82.00 | 91.00 | -6.00 | -6.00 | hold_to_settlement | n/a | 36.00 | 6.00 |
| KXBTC15M-26MAY062245-45 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 86.00 | 90.00 | -2.00 | -2.00 | hold_to_settlement | n/a | 28.00 | 20.00 |
| KXBTC15M-26MAY062030-30 | no | approved_entry | mushroom_v28_exit_value_over_hold | 67.00 | 94.00 | -2.00 | -2.00 | hold_to_settlement | n/a | 66.00 | 34.00 |
| KXBTC15M-26MAY060530-30 | no | approved_entry | mushroom_v28_exit_value_over_hold | 78.00 | 96.00 | -1.00 | -1.00 | hold_to_settlement | n/a | 44.00 | 10.00 |
| KXBTC15M-26MAY060445-45 | yes | rejected_actionable | mushroom_v28_exit_value_over_hold | 90.00 | 100.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 20.00 | 2.00 |
| KXBTC15M-26MAY061445-45 | no | approved_entry | mushroom_v28_exit_value_over_hold | 90.00 | 99.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 20.00 | 2.00 |
| KXBTC15M-26MAY061615-15 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 90.00 | 96.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 20.00 | 12.00 |
| KXBTC15M-26MAY061830-30 | no | approved_entry | mushroom_v28_exit_value_over_hold | 89.00 | 100.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 22.00 | 2.00 |
| KXBTC15M-26MAY070815-15 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 90.00 | 94.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 20.00 | 18.00 |
| KXBTC15M-26MAY061400-00 | no | approved_entry | mushroom_v28_exit_value_over_hold | 89.00 | 92.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 22.00 | 32.00 |
| KXBTC15M-26MAY061915-15 | no | approved_entry | mushroom_v28_exit_value_over_hold | 87.00 | 100.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 26.00 | 2.00 |
| KXBTC15M-26MAY062300-00 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 87.00 | 94.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 26.00 | 10.00 |
| KXBTC15M-26MAY061815-15 | no | approved_entry | mushroom_v28_exit_value_over_hold | 84.00 | 96.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 32.00 | 8.00 |
| KXBTC15M-26MAY061545-45 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 84.00 | 94.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 32.00 | 10.00 |
| KXBTC15M-26MAY070115-15 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 82.00 | 85.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 36.00 | 36.00 |
| KXBTC15M-26MAY070545-45 | no | approved_entry | mushroom_v28_exit_value_over_hold | 82.00 | 96.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 36.00 | 18.00 |
| KXBTC15M-26MAY061045-45 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 84.00 | 100.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 32.00 | 4.00 |
| KXBTC15M-26MAY062045-45 | no | approved_entry | mushroom_v28_exit_value_over_hold | 80.00 | 95.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 40.00 | 16.00 |
| KXBTC15M-26MAY060630-30 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 85.00 | 99.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 30.00 | 2.00 |
| KXBTC15M-26MAY060645-45 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 80.00 | 99.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 40.00 | 6.00 |
| KXBTC15M-26MAY070000-00 | no | approved_entry | mushroom_v28_exit_value_over_hold | 78.00 | 91.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 44.00 | 42.00 |
| KXBTC15M-26MAY060830-30 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 76.00 | 100.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 48.00 | 0.00 |
| KXBTC15M-26MAY060915-15 | no | approved_entry | mushroom_v28_exit_value_over_hold | 75.00 | 100.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 50.00 | 0.00 |
| KXBTC15M-26MAY060515-15 | no | approved_entry | mushroom_v28_exit_value_over_hold | 74.00 | 100.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 52.00 | 10.00 |
| KXBTC15M-26MAY060700-00 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 83.00 | 100.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 34.00 | 22.00 |
| KXBTC15M-26MAY060715-15 | yes | rejected_actionable | mushroom_v28_exit_value_over_hold | 89.00 | 100.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 22.00 | 2.00 |
| KXBTC15M-26MAY060900-00 | no | approved_entry | mushroom_v28_exit_value_over_hold | 79.00 | 100.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 42.00 | 8.00 |
| KXBTC15M-26MAY062115-15 | yes | approved_entry | mushroom_v28_exit_value_over_hold | 88.00 | 100.00 | 0.00 | 0.00 | hold_to_settlement | n/a | 24.00 | 2.00 |
