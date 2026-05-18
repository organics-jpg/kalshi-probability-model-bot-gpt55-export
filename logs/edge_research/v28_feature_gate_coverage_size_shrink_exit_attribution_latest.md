# v28 Feature-Gate Coverage Size-Shrink Exit Attribution

Research-only attribution. No live bot changes or orders.

- Generated UTC: `2026-05-11T02:06:11.518305+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- This attribution uses frozen exit artifacts as evidence only; it does not change exit logic.
- post_feature_freeze_entry repair_eighth has 12 losing rows, weighted loss -361.25c, failure classes {'no_exit_observation': 8, 'entry_or_fv_failure_exit_helped': 3, 'exit_preserved_profit': 1}.
- post_feature_freeze_bridge repair_eighth has 12 losing rows, weighted loss -361.25c, failure classes {'no_exit_observation': 8, 'entry_or_fv_failure_exit_helped': 3, 'exit_preserved_profit': 1}.

## post_feature_freeze_entry

- Policy: `repair_eighth`
- Raw/weighted loss cents: `-783.0c ($-7.83)/-361.2c ($-3.61)`
- Source counts: `{'rejected_actionable': 9, 'approved_entry': 3}`
- Failure classes: `{'no_exit_observation': 8, 'entry_or_fv_failure_exit_helped': 3, 'exit_preserved_profit': 1}`

| market | source | anchor | side | raw net | weight | weighted net | primary class | best hold-current |
|---|---|---:|---|---:|---:|---:|---|---:|
| KXBTC15M-26MAY061700-00 | rejected_actionable | False | no | -42.0c ($-0.42) | 0.125 | -5.2c ($-0.05) | no_exit_observation | n/a |
| KXBTC15M-26MAY061715-15 | rejected_actionable | False | yes | -68.0c ($-0.68) | 0.125 | -8.5c ($-0.09) | no_exit_observation | n/a |
| KXBTC15M-26MAY062130-30 | rejected_actionable | True | no | -65.0c ($-0.65) | 1.0 | -65.0c ($-0.65) | entry_or_fv_failure_exit_helped | -120.0c ($-1.20) |
| KXBTC15M-26MAY062230-30 | rejected_actionable | False | yes | -58.0c ($-0.58) | 0.125 | -7.2c ($-0.07) | no_exit_observation | n/a |
| KXBTC15M-26MAY062345-45 | rejected_actionable | False | no | -60.0c ($-0.60) | 0.125 | -7.5c ($-0.07) | no_exit_observation | n/a |
| KXBTC15M-26MAY070015-15 | approved_entry | True | no | -72.0c ($-0.72) | 1.0 | -72.0c ($-0.72) | entry_or_fv_failure_exit_helped | -138.0c ($-1.38) |
| KXBTC15M-26MAY070615-15 | rejected_actionable | False | yes | -47.0c ($-0.47) | 0.125 | -5.9c ($-0.06) | no_exit_observation | n/a |
| KXBTC15M-26MAY070630-30 | rejected_actionable | False | yes | -59.0c ($-0.59) | 0.125 | -7.4c ($-0.07) | no_exit_observation | n/a |
| KXBTC15M-26MAY070900-00 | rejected_actionable | False | no | -73.0c ($-0.73) | 0.125 | -9.1c ($-0.09) | no_exit_observation | n/a |
| KXBTC15M-26MAY071015-15 | approved_entry | True | no | -80.0c ($-0.80) | 1.0 | -80.0c ($-0.80) | entry_or_fv_failure_exit_helped | -146.0c ($-1.46) |
| KXBTC15M-26MAY071100-00 | approved_entry | True | yes | -84.0c ($-0.84) | 1.0 | -84.0c ($-0.84) | exit_preserved_profit | -170.0c ($-1.70) |
| KXBTC15M-26MAY071215-15 | rejected_actionable | False | yes | -75.0c ($-0.75) | 0.125 | -9.4c ($-0.09) | no_exit_observation | n/a |

## post_feature_freeze_bridge

- Policy: `repair_eighth`
- Raw/weighted loss cents: `-783.0c ($-7.83)/-361.2c ($-3.61)`
- Source counts: `{'rejected_actionable': 9, 'approved_entry': 3}`
- Failure classes: `{'no_exit_observation': 8, 'entry_or_fv_failure_exit_helped': 3, 'exit_preserved_profit': 1}`

| market | source | anchor | side | raw net | weight | weighted net | primary class | best hold-current |
|---|---|---:|---|---:|---:|---:|---|---:|
| KXBTC15M-26MAY061700-00 | rejected_actionable | False | no | -42.0c ($-0.42) | 0.125 | -5.2c ($-0.05) | no_exit_observation | n/a |
| KXBTC15M-26MAY061715-15 | rejected_actionable | False | yes | -68.0c ($-0.68) | 0.125 | -8.5c ($-0.09) | no_exit_observation | n/a |
| KXBTC15M-26MAY062130-30 | rejected_actionable | True | no | -65.0c ($-0.65) | 1.0 | -65.0c ($-0.65) | entry_or_fv_failure_exit_helped | -120.0c ($-1.20) |
| KXBTC15M-26MAY062230-30 | rejected_actionable | False | yes | -58.0c ($-0.58) | 0.125 | -7.2c ($-0.07) | no_exit_observation | n/a |
| KXBTC15M-26MAY062345-45 | rejected_actionable | False | no | -60.0c ($-0.60) | 0.125 | -7.5c ($-0.07) | no_exit_observation | n/a |
| KXBTC15M-26MAY070015-15 | approved_entry | True | no | -72.0c ($-0.72) | 1.0 | -72.0c ($-0.72) | entry_or_fv_failure_exit_helped | -138.0c ($-1.38) |
| KXBTC15M-26MAY070615-15 | rejected_actionable | False | yes | -47.0c ($-0.47) | 0.125 | -5.9c ($-0.06) | no_exit_observation | n/a |
| KXBTC15M-26MAY070630-30 | rejected_actionable | False | yes | -59.0c ($-0.59) | 0.125 | -7.4c ($-0.07) | no_exit_observation | n/a |
| KXBTC15M-26MAY070900-00 | rejected_actionable | False | no | -73.0c ($-0.73) | 0.125 | -9.1c ($-0.09) | no_exit_observation | n/a |
| KXBTC15M-26MAY071015-15 | approved_entry | True | no | -80.0c ($-0.80) | 1.0 | -80.0c ($-0.80) | entry_or_fv_failure_exit_helped | -146.0c ($-1.46) |
| KXBTC15M-26MAY071100-00 | approved_entry | True | yes | -84.0c ($-0.84) | 1.0 | -84.0c ($-0.84) | exit_preserved_profit | -170.0c ($-1.70) |
| KXBTC15M-26MAY071215-15 | rejected_actionable | False | yes | -75.0c ($-0.75) | 0.125 | -9.4c ($-0.09) | no_exit_observation | n/a |
