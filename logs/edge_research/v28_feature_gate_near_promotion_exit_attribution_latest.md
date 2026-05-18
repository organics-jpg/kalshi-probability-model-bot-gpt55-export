# v28 Feature-Gate Near-Promotion Exit Attribution

Research-only attribution. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:25.991747+00:00`
- Candidate: `post_feature_freeze_entry_raw05_recross60_abs085`
- Candidate net: `445c ($4.45)`
- Candidate settled: `55`
- Candidate missing gates: `['coverage+7.9pp']`
- Loss rows: `16`
- Loss source counts: `{'rejected_actionable': 12, 'approved_entry': 4}`
- Failure class counts: `{'no_exit_observation': 12, 'entry_or_fv_failure_exit_helped': 3, 'exit_preserved_profit': 1}`

## Loss Rows

| market | source | side | entry net | primary class | best hold-current | exit summaries |
|---|---|---|---:|---|---:|---|
| KXBTC15M-26MAY061415-15 | rejected_actionable | yes | -3c ($-0.03) | no_exit_observation | n/a | no match |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | -5c ($-0.05) | no_exit_observation | n/a | no match |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | -3c ($-0.03) | no_exit_observation | n/a | no match |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | -7c ($-0.07) | no_exit_observation | n/a | no match |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | -5c ($-0.05) | no_exit_observation | n/a | no match |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -6c ($-0.06) | no_exit_observation | n/a | no match |
| KXBTC15M-26MAY062130-30 | approved_entry | no | -78c ($-0.78) | entry_or_fv_failure_exit_helped | -120c ($-1.20) | reduce: exit_helped_vs_hold current=-32c ($-0.32) hold=-152c ($-1.52) reason=mushroom_v28_probability_reduce; book_gap: exit_helped_vs_hold current=-32c ($-0.32) hold=-152c ($-1.52) reason=mushroom_v28_probability_reduce; loss_guard_v1: exit_helped_vs_hold current=-32c ($-0.32) hold=-152c ($-1.52) reason=mushroom_v28_probability_reduce; loss_guard_v2: exit_helped_vs_hold current=-32c ($-0.32) hold=-152c ($-1.52) reason=mushroom_v28_probability_reduce; loss_guard_v3: exit_helped_vs_hold current=-32c ($-0.32) hold=-152c ($-1.52) reason=mushroom_v28_probability_reduce |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | -5c ($-0.05) | no_exit_observation | n/a | no match |
| KXBTC15M-26MAY062300-00 | rejected_actionable | no | -2c ($-0.02) | no_exit_observation | n/a | no match |
| KXBTC15M-26MAY070015-15 | approved_entry | no | -72c ($-0.72) | entry_or_fv_failure_exit_helped | -138c ($-1.38) | reduce: exit_helped_vs_hold current=-2c ($-0.02) hold=-140c ($-1.40) reason=mushroom_v28_exit_value_over_hold; book_gap: exit_helped_vs_hold current=-2c ($-0.02) hold=-140c ($-1.40) reason=mushroom_v28_exit_value_over_hold; loss_guard_v1: exit_helped_vs_hold current=-2c ($-0.02) hold=-140c ($-1.40) reason=mushroom_v28_exit_value_over_hold; loss_guard_v2: exit_helped_vs_hold current=-2c ($-0.02) hold=-140c ($-1.40) reason=mushroom_v28_exit_value_over_hold; loss_guard_v3: exit_helped_vs_hold current=-2c ($-0.02) hold=-140c ($-1.40) reason=mushroom_v28_exit_value_over_hold |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | -4c ($-0.04) | no_exit_observation | n/a | no match |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | -6c ($-0.06) | no_exit_observation | n/a | no match |
| KXBTC15M-26MAY071015-15 | approved_entry | no | -80c ($-0.80) | entry_or_fv_failure_exit_helped | -146c ($-1.46) | reduce: exit_helped_vs_hold current=-16c ($-0.16) hold=-162c ($-1.62) reason=mushroom_v28_probability_reduce; book_gap: exit_helped_vs_hold current=-16c ($-0.16) hold=-162c ($-1.62) reason=mushroom_v28_probability_reduce; loss_guard_v1: exit_helped_vs_hold current=-16c ($-0.16) hold=-162c ($-1.62) reason=mushroom_v28_probability_reduce; loss_guard_v2: exit_helped_vs_hold current=-16c ($-0.16) hold=-162c ($-1.62) reason=mushroom_v28_probability_reduce; loss_guard_v3: exit_helped_vs_hold current=-16c ($-0.16) hold=-162c ($-1.62) reason=mushroom_v28_probability_reduce |
| KXBTC15M-26MAY071100-00 | approved_entry | yes | -84c ($-0.84) | exit_preserved_profit | -170c ($-1.70) | reduce: exit_preserved_profit current=4c ($0.04) hold=-166c ($-1.66) reason=mushroom_v28_exit_value_over_hold; book_gap: exit_preserved_profit current=4c ($0.04) hold=-166c ($-1.66) reason=mushroom_v28_exit_value_over_hold; loss_guard_v1: exit_preserved_profit current=4c ($0.04) hold=-166c ($-1.66) reason=mushroom_v28_exit_value_over_hold; loss_guard_v2: exit_preserved_profit current=4c ($0.04) hold=-166c ($-1.66) reason=mushroom_v28_exit_value_over_hold; loss_guard_v3: exit_preserved_profit current=4c ($0.04) hold=-166c ($-1.66) reason=mushroom_v28_exit_value_over_hold |
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | -7c ($-0.07) | no_exit_observation | n/a | no match |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | -10c ($-0.10) | no_exit_observation | n/a | no match |

## Interpretation

- This attribution uses frozen exit artifacts as evidence only; it does not change exit logic.
- If losses are mostly exit_helped_vs_hold, the remaining failure is entry/FV/source quality rather than clipped exits.
- post_feature_freeze_entry_raw05_recross60_abs085 has failure classes {'no_exit_observation': 12, 'entry_or_fv_failure_exit_helped': 3, 'exit_preserved_profit': 1} across 16 losing rows.
