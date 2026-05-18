# v28 Feature-Gate Middle-Core Exit Attribution

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T12:55:32.428010+00:00`
- Feature-gate parent freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Middle-core watch freeze UTC: `2026-05-07T12:00:53.752707+00:00`

## Interpretation

- Research-only exit attribution; no live bot changes or orders.
- Entry-hold PnL uses settlement/hold rows; exit-source deltas use frozen exit artifacts and are diagnostic only.
- diagnostic_feature_window_entry: core W/L 28/3, entry-hold net 278.0c, settlement loss classes {'entry_or_fv_failure_exit_helped': 2, 'no_exit_observation': 1}, exit-harm rows 22 worth 708.0c if held.
- diagnostic_feature_window_bridge: core W/L 24/1, entry-hold net 311.0c, settlement loss classes {'entry_or_fv_failure_exit_helped': 1}, exit-harm rows 22 worth 708.0c if held.
- post_middle_core_freeze_entry: core W/L 1/0, entry-hold net 21.0c, settlement loss classes {}, exit-harm rows 0 worth 0c if held.
- post_middle_core_freeze_bridge: core W/L 1/0, entry-hold net 21.0c, settlement loss classes {}, exit-harm rows 0 worth 0c if held.

## diagnostic_feature_window_entry

- Entries / settled: `36/31`
- W/L: `28/3`
- Coverage: `57.143%`
- Entry-hold net: `278.000c`
- Source counts: `{'approved_entry': 30, 'rejected_actionable': 6}`
- Settlement loss classes: `{'entry_or_fv_failure_exit_helped': 2, 'no_exit_observation': 1}`
- Exit-harm rows/cents-if-held: `22/708.000c`
- Exit-help rows/cents-vs-hold: `2/-258.000c`

### Exit Source Rollup

| source | current c | hold c | hold-current c | classes |
|---|---:|---:|---:|---|
| `book_gap` | 82.000 | 428.000 | 346.000 | `{'exit_clipped_profit': 13, 'exit_neutral': 2, 'exit_hurt_or_clipped_winner': 2, 'exit_helped_vs_hold': 2}` |
| `loss_guard_v1` | 164.000 | 710.000 | 546.000 | `{'exit_hurt_or_clipped_winner': 2, 'exit_clipped_profit': 16, 'exit_neutral': 2, 'exit_helped_vs_hold': 1}` |
| `loss_guard_v2` | 184.000 | 230.000 | 46.000 | `{'exit_clipped_profit': 9, 'exit_neutral': 2, 'exit_helped_vs_hold': 1}` |
| `loss_guard_v3` | 172.000 | 154.000 | -18.000 | `{'exit_clipped_profit': 6, 'exit_helped_vs_hold': 1, 'exit_neutral': 2}` |
| `reduce` | 72.000 | 158.000 | 86.000 | `{'exit_neutral': 3, 'exit_clipped_profit': 8, 'exit_hurt_or_clipped_winner': 1, 'exit_helped_vs_hold': 2}` |

### Settlement Loss Rows

| market | side | source | hold net | primary class | best hold-current | abs d | ask | recross |
|---|---|---|---:|---|---:|---:|---:|---:|
| `KXBTC15M-26MAY062130-30` | no | approved_entry | -78.000 | entry_or_fv_failure_exit_helped | -120.000 | 0.999 | 0.760 | 0.304 |
| `KXBTC15M-26MAY070015-15` | no | approved_entry | -72.000 | entry_or_fv_failure_exit_helped | -138.000 | 1.544 | 0.700 | 0.074 |
| `KXBTC15M-26MAY070615-15` | yes | rejected_actionable | -68.000 | no_exit_observation |  | 0.820 | 0.640 | 0.253 |

### Largest Exit-Harm Rows

| market | side | source | hold net | best hold-current | primary class |
|---|---|---|---:|---:|---|
| `KXBTC15M-26MAY062015-15` | no | approved_entry | 56.000 | 176.000 | exit_policy_failure_candidate |
| `KXBTC15M-26MAY061800-00` | no | approved_entry | 28.000 | 152.000 | exit_policy_failure_candidate |
| `KXBTC15M-26MAY062100-00` | yes | approved_entry | 37.000 | 64.000 | exit_clipped_profit |
| `KXBTC15M-26MAY070000-00` | no | approved_entry | 0.000 | 42.000 | exit_clipped_profit |
| `KXBTC15M-26MAY070115-15` | yes | approved_entry | 0.000 | 36.000 | exit_clipped_profit |
| `KXBTC15M-26MAY062030-30` | no | approved_entry | 31.000 | 34.000 | exit_clipped_profit |
| `KXBTC15M-26MAY070745-45` | yes | approved_entry | 30.000 | 30.000 | exit_clipped_profit |
| `KXBTC15M-26MAY062315-15` | no | approved_entry | 0.000 | 26.000 | exit_clipped_profit |
| `KXBTC15M-26MAY062215-15` | no | approved_entry | 33.000 | 22.000 | exit_clipped_profit |
| `KXBTC15M-26MAY062245-45` | yes | approved_entry | 13.000 | 20.000 | exit_clipped_profit |

## diagnostic_feature_window_bridge

- Entries / settled: `36/25`
- W/L: `24/1`
- Coverage: `56.250%`
- Entry-hold net: `311.000c`
- Source counts: `{'approved_entry': 30, 'rejected_actionable': 6}`
- Settlement loss classes: `{'entry_or_fv_failure_exit_helped': 1}`
- Exit-harm rows/cents-if-held: `22/708.000c`
- Exit-help rows/cents-vs-hold: `2/-258.000c`

### Exit Source Rollup

| source | current c | hold c | hold-current c | classes |
|---|---:|---:|---:|---|
| `book_gap` | 82.000 | 428.000 | 346.000 | `{'exit_clipped_profit': 13, 'exit_neutral': 2, 'exit_hurt_or_clipped_winner': 2, 'exit_helped_vs_hold': 2}` |
| `loss_guard_v1` | 164.000 | 710.000 | 546.000 | `{'exit_hurt_or_clipped_winner': 2, 'exit_clipped_profit': 16, 'exit_neutral': 2, 'exit_helped_vs_hold': 1}` |
| `loss_guard_v2` | 184.000 | 230.000 | 46.000 | `{'exit_clipped_profit': 9, 'exit_neutral': 2, 'exit_helped_vs_hold': 1}` |
| `loss_guard_v3` | 172.000 | 154.000 | -18.000 | `{'exit_clipped_profit': 6, 'exit_helped_vs_hold': 1, 'exit_neutral': 2}` |
| `reduce` | 72.000 | 158.000 | 86.000 | `{'exit_neutral': 3, 'exit_clipped_profit': 8, 'exit_hurt_or_clipped_winner': 1, 'exit_helped_vs_hold': 2}` |

### Settlement Loss Rows

| market | side | source | hold net | primary class | best hold-current | abs d | ask | recross |
|---|---|---|---:|---|---:|---:|---:|---:|
| `KXBTC15M-26MAY062130-30` | no | approved_entry | -78.000 | entry_or_fv_failure_exit_helped | -120.000 | 0.999 | 0.760 | 0.304 |

### Largest Exit-Harm Rows

| market | side | source | hold net | best hold-current | primary class |
|---|---|---|---:|---:|---|
| `KXBTC15M-26MAY062015-15` | no | approved_entry | 56.000 | 176.000 | exit_policy_failure_candidate |
| `KXBTC15M-26MAY061800-00` | no | approved_entry | 0.000 | 152.000 | exit_policy_failure_candidate |
| `KXBTC15M-26MAY062100-00` | yes | approved_entry | 0.000 | 64.000 | exit_clipped_profit |
| `KXBTC15M-26MAY070000-00` | no | approved_entry | 20.000 | 42.000 | exit_clipped_profit |
| `KXBTC15M-26MAY070115-15` | yes | approved_entry | 16.000 | 36.000 | exit_clipped_profit |
| `KXBTC15M-26MAY062030-30` | no | approved_entry | 31.000 | 34.000 | exit_clipped_profit |
| `KXBTC15M-26MAY070745-45` | yes | approved_entry | 0.000 | 30.000 | exit_clipped_profit |
| `KXBTC15M-26MAY062315-15` | no | approved_entry | 15.000 | 26.000 | exit_clipped_profit |
| `KXBTC15M-26MAY062215-15` | no | approved_entry | 33.000 | 22.000 | exit_clipped_profit |
| `KXBTC15M-26MAY062245-45` | yes | approved_entry | 13.000 | 20.000 | exit_clipped_profit |

## post_middle_core_freeze_entry

- Entries / settled: `1/1`
- W/L: `1/0`
- Coverage: `33.333%`
- Entry-hold net: `21.000c`
- Source counts: `{'approved_entry': 1}`
- Settlement loss classes: `{}`
- Exit-harm rows/cents-if-held: `0/0c`
- Exit-help rows/cents-vs-hold: `0/0c`

### Exit Source Rollup

| source | current c | hold c | hold-current c | classes |
|---|---:|---:|---:|---|
| `loss_guard_v2` | 46.000 | 46.000 | 0.000 | `{'exit_neutral': 1}` |
| `loss_guard_v3` | 46.000 | 46.000 | 0.000 | `{'exit_neutral': 1}` |

### Settlement Loss Rows

| market | side | source | hold net | primary class | best hold-current | abs d | ask | recross |
|---|---|---|---:|---|---:|---:|---:|---:|

### Largest Exit-Harm Rows

| market | side | source | hold net | best hold-current | primary class |
|---|---|---|---:|---:|---|

## post_middle_core_freeze_bridge

- Entries / settled: `1/1`
- W/L: `1/0`
- Coverage: `33.333%`
- Entry-hold net: `21.000c`
- Source counts: `{'approved_entry': 1}`
- Settlement loss classes: `{}`
- Exit-harm rows/cents-if-held: `0/0c`
- Exit-help rows/cents-vs-hold: `0/0c`

### Exit Source Rollup

| source | current c | hold c | hold-current c | classes |
|---|---:|---:|---:|---|
| `loss_guard_v2` | 46.000 | 46.000 | 0.000 | `{'exit_neutral': 1}` |
| `loss_guard_v3` | 46.000 | 46.000 | 0.000 | `{'exit_neutral': 1}` |

### Settlement Loss Rows

| market | side | source | hold net | primary class | best hold-current | abs d | ask | recross |
|---|---|---|---:|---|---:|---:|---:|---:|

### Largest Exit-Harm Rows

| market | side | source | hold net | best hold-current | primary class |
|---|---|---|---:|---:|---|
