# v28 Midprice Source-Dilution Stability

Research-only. No live bot changes or orders.

- Generated UTC: `2026-05-11T02:49:40.915491+00:00`
- Target filter: `absd_gte_055_or_ask_gte_065`

## Interpretation

- This is a parent diagnostic stability stress, not promotion evidence.
- The target dilution rule remains newly frozen; strict post-birth rows must validate it.
- post_feature_freeze_entry: kept 46 rows for 439.5c, net without top win 383.5c, dropped 1 rows for -58.0c, flags ['single_row_diagnostic_repair', 'source_share_close_to_gate', 'coverage_close_to_floor'].

## post_feature_freeze_entry

- Coverage: `74.19%`
- Reconstructed share: `39.13%`
- Source counts: `{'approved_entry': 28, 'rejected_actionable': 18}`
- Kept summary: `{'rows': 46, 'wins': 38, 'losses': 7, 'net_cents': 439.5, 'avg_net_cents': 9.554347826086957, 'full_loss_cushion': 4, 'top_win_cents': 56.0, 'worst_loss_cents': -72.0, 'net_without_top_win_cents': 383.5, 'net_without_top_two_wins_cents': 332.5, 'net_without_top_loss_saved_cents': 367.5}`
- Dropped summary: `{'rows': 1, 'wins': 0, 'losses': 1, 'net_cents': -58.0, 'avg_net_cents': -58.0, 'full_loss_cushion': 0, 'top_win_cents': -58.0, 'worst_loss_cents': -58.0, 'net_without_top_win_cents': 0.0, 'net_without_top_two_wins_cents': -58.0, 'net_without_top_loss_saved_cents': -116.0}`
- Leave-one-out: `{'min_net_after_removal_cents': 383.5, 'max_net_after_removal_cents': 511.5, 'min_cushion_after_removal': 3, 'top_win_dependency': [{'removed_market': 'KXBTC15M-26MAY062015-15', 'removed_side': 'no', 'removed_source': 'approved_entry', 'removed_net_cents': 56.0, 'net_after_removal_cents': 383.5, 'cushion_after_removal': 3}, {'removed_market': 'KXBTC15M-26MAY061945-45', 'removed_side': 'no', 'removed_source': 'rejected_actionable', 'removed_net_cents': 51.0, 'net_after_removal_cents': 388.5, 'cushion_after_removal': 3}, {'removed_market': 'KXBTC15M-26MAY062000-00', 'removed_side': 'yes', 'removed_source': 'rejected_actionable', 'removed_net_cents': 48.0, 'net_after_removal_cents': 391.5, 'cushion_after_removal': 3}, {'removed_market': 'KXBTC15M-26MAY062100-00', 'removed_side': 'yes', 'removed_source': 'approved_entry', 'removed_net_cents': 37.0, 'net_after_removal_cents': 402.5, 'cushion_after_removal': 4}, {'removed_market': 'KXBTC15M-26MAY062215-15', 'removed_side': 'no', 'removed_source': 'approved_entry', 'removed_net_cents': 33.0, 'net_after_removal_cents': 406.5, 'cushion_after_removal': 4}], 'top_loss_relief': [{'removed_market': 'KXBTC15M-26MAY070015-15', 'removed_side': 'no', 'removed_source': 'approved_entry', 'removed_net_cents': -72.0, 'net_after_removal_cents': 511.5, 'cushion_after_removal': 5}, {'removed_market': 'KXBTC15M-26MAY062345-45', 'removed_side': 'no', 'removed_source': 'rejected_actionable', 'removed_net_cents': -60.0, 'net_after_removal_cents': 499.5, 'cushion_after_removal': 4}, {'removed_market': 'KXBTC15M-26MAY070630-30', 'removed_side': 'yes', 'removed_source': 'rejected_actionable', 'removed_net_cents': -59.0, 'net_after_removal_cents': 498.5, 'cushion_after_removal': 4}, {'removed_market': 'KXBTC15M-26MAY070615-15', 'removed_side': 'yes', 'removed_source': 'rejected_actionable', 'removed_net_cents': -47.0, 'net_after_removal_cents': 486.5, 'cushion_after_removal': 4}, {'removed_market': 'KXBTC15M-26MAY061700-00', 'removed_side': 'no', 'removed_source': 'rejected_actionable', 'removed_net_cents': -42.0, 'net_after_removal_cents': 481.5, 'cushion_after_removal': 4}]}`
- Stability flags: `['single_row_diagnostic_repair', 'source_share_close_to_gate', 'coverage_close_to_floor']`

### Source Split

| source | rows | W/L | net | top win | worst loss | net ex top win | cushion |
|---|---:|---:|---:|---:|---:|---:|---:|
| `approved_entry` | 28 | 26/1 | 418.0c | 56.0c | -72.0c | 362.0c | 4 |
| `rejected_actionable` | 18 | 12/6 | 21.5c | 51.0c | -60.0c | -29.5c | 0 |

### Dropped Rows

| market | side | source | net | abs_d | ask | recross |
|---|---|---|---:|---:|---:|---:|
| `KXBTC15M-26MAY062230-30` | `yes` | `rejected_actionable` | -58.0c | 0.532659 | 0.54 | 0.24354681339147827 |

### Worst Kept Rows

| market | side | source | net | abs_d | ask | recross |
|---|---|---|---:|---:|---:|---:|
| `KXBTC15M-26MAY070015-15` | `no` | `approved_entry` | -72.0c | 1.543579 | 0.7 | 0.07375286170271013 |
| `KXBTC15M-26MAY062345-45` | `no` | `rejected_actionable` | -60.0c | 0.72697 | 0.56 | 0.2648024542283173 |
| `KXBTC15M-26MAY070630-30` | `yes` | `rejected_actionable` | -59.0c | 0.65803 | 0.55 | 0.37230392875591767 |
| `KXBTC15M-26MAY070615-15` | `yes` | `rejected_actionable` | -47.0c | 0.63149 | 0.43 | 0.1432808396397172 |
| `KXBTC15M-26MAY061700-00` | `no` | `rejected_actionable` | -42.0c | 0.665443 | 0.38 | 0.19639134370333244 |
| `KXBTC15M-26MAY061715-15` | `yes` | `rejected_actionable` | -17.0c | 0.60259 | 0.64 | 0.11475429655322977 |
| `KXBTC15M-26MAY062130-30` | `no` | `rejected_actionable` | -16.2c | 0.623877 | 0.61 | 0.2673176111866901 |
| `KXBTC15M-26MAY070830-30` | `no` | `approved_entry` | 0.0c | 0.951073 | 0.82 | 0.2815228625858157 |
| `KXBTC15M-26MAY062200-00` | `no` | `rejected_actionable` | 4.0c | 2.37058 | 0.95 | 0.026846679101237274 |
| `KXBTC15M-26MAY062145-45` | `yes` | `rejected_actionable` | 6.0c | 1.770776 | 0.92 | 0.03476117876899882 |
