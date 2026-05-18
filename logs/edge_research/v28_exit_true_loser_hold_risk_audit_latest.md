# v28 Exit True-Loser Hold Risk Audit

Research-only guardrail. No live bot changes or orders.

- Generated UTC: `2026-05-07T09:45:38.283921+00:00`
- Loss rows: `64`
- True-loser hold-risk rows: `21`
- Clipped-winner hold-helpful rows: `43`
- Repair-flipped rows: `12`

## Interpretation

- This audit separates exits that clipped winners from exits that prevented larger FV/entry-timing losses.
- True-loser rows have hold delta `-2158c` across `21` rows.
- Clipped-winner rows have hold delta `2855c` across `43` rows.
- Future exit watches should prove they avoid the true-loser tags under strict post-freeze evidence before broad suppression is trusted.

## Avoid Broad Hold Tags

| tag | true rows | true hold delta | clipped rows | clipped hold delta | combined hold delta | read |
|---|---:|---:|---:|---:|---:|---|
| `fv_or_entry_timing_error` | 21 | -2158c | 0 | 0c | -2158c | `avoid_broad_hold` |
| `medium_25_49c` | 8 | -902c | 7 | 542c | -360c | `avoid_broad_hold` |
| `exit_cents_lte40` | 4 | -260c | 2 | 328c | 68c | `avoid_broad_hold` |
| `thin_touch_depth` | 3 | -386c | 3 | 192c | -194c | `avoid_broad_hold` |
| `large_50_99c` | 3 | -234c | 3 | 422c | 188c | `avoid_broad_hold` |
| `ask_lt55` | 3 | -112c | 1 | 176c | 64c | `avoid_broad_hold` |

## Bucket Contrast

| tag | true rows | true hold delta | clipped rows | clipped hold delta | combined hold delta | read |
|---|---:|---:|---:|---:|---:|---|
| `fv_or_entry_timing_error` | 21 | -2158c | 0 | 0c | -2158c | `avoid_broad_hold` |
| `medium_25_49c` | 8 | -902c | 7 | 542c | -360c | `avoid_broad_hold` |
| `exit_cents_lte40` | 4 | -260c | 2 | 328c | 68c | `avoid_broad_hold` |
| `thin_touch_depth` | 3 | -386c | 3 | 192c | -194c | `avoid_broad_hold` |
| `large_50_99c` | 3 | -234c | 3 | 422c | 188c | `avoid_broad_hold` |
| `ask_lt55` | 3 | -112c | 1 | 176c | 64c | `avoid_broad_hold` |
| `p_side_gte85` | 21 | -2158c | 43 | 2855c | 697c | `possible_clip_repair_context` |
| `absd_gte085` | 20 | -2078c | 40 | 2667c | 589c | `possible_clip_repair_context` |
| `near_boundary` | 17 | -1806c | 34 | 2237c | 431c | `possible_clip_repair_context` |
| `ask_gte70` | 14 | -1738c | 38 | 2259c | 521c | `possible_clip_repair_context` |
| `depth_lte384` | 13 | -1272c | 31 | 2023c | 751c | `possible_clip_repair_context` |
| `depth_lte150` | 12 | -1182c | 22 | 1492c | 310c | `possible_clip_repair_context` |
| `exit_cents_gte60` | 11 | -1504c | 38 | 2235c | 731c | `possible_clip_repair_context` |
| `recross_hazard_high` | 11 | -1420c | 24 | 1543c | 123c | `possible_clip_repair_context` |
| `small_10_24c` | 7 | -724c | 25 | 1490c | 766c | `possible_clip_repair_context` |
| `thin_raw_edge` | 6 | -834c | 14 | 746c | -88c | `possible_clip_repair_context` |
| `rich_entry` | 5 | -634c | 16 | 840c | 206c | `possible_clip_repair_context` |
| `exit_p_hold_lt60` | 4 | -408c | 5 | 586c | 178c | `possible_clip_repair_context` |
| `exit_p_hold_gte75` | 3 | -426c | 12 | 649c | 223c | `possible_clip_repair_context` |
| `micro_lt_10c` | 2 | -298c | 8 | 401c | 103c | `possible_clip_repair_context` |
| `crowded_depth` | 2 | -290c | 5 | 342c | 52c | `possible_clip_repair_context` |
| `exit_p_hold_60_75` | 2 | -244c | 17 | 1126c | 882c | `possible_clip_repair_context` |
| `full_loss_ge_100c` | 1 | 0c | 0 | 0c | 0c | `mixed_or_sparse` |
| `exit_policy_clip_vs_hold` | 0 | 0c | 43 | 2855c | 2855c | `possible_clip_repair_context` |
| `exit_policy_cost` | 0 | 0c | 43 | 2855c | 2855c | `possible_clip_repair_context` |

## Worst True-Loser Hold Examples

| market | side/result | actual | hold | hold delta | ask | p_side | abs d | exit | p_hold | tags |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY060700-00` | no/yes | -8c | -168c | -160c | 84 | 0.890574 | 1.04212 | 80 | 0.799603 | absd_gte085, ask_gte70, crowded_depth, exit_cents_gte60, exit_p_hold_gte75, fv_or_entry_timing_error, micro_lt_10c, p_side_gte85, recross_hazard_high, rich_entry, thin_raw_edge |
| `KXBTC15M-26MAY060900-00` | yes/no | -10c | -156c | -146c | 78 | 0.856054 | 0.872054 | 73 | 0.78999 | absd_gte085, ask_gte70, exit_cents_gte60, exit_p_hold_gte75, fv_or_entry_timing_error, near_boundary, p_side_gte85, recross_hazard_high, small_10_24c |
| `KXBTC15M-26MAY052045-45` | yes/no | -18c | -158c | -140c | 79 | 0.851889 | 0.866186 | 70 | None | absd_gte085, ask_gte70, depth_lte150, depth_lte384, exit_cents_gte60, fv_or_entry_timing_error, near_boundary, p_side_gte85, recross_hazard_high, small_10_24c, thin_raw_edge |
| `KXBTC15M-26MAY060215-15` | yes/no | -26c | -166c | -140c | 83 | 0.881378 | 0.959045 | 70 | None | absd_gte085, ask_gte70, exit_cents_gte60, fv_or_entry_timing_error, medium_25_49c, near_boundary, p_side_gte85, rich_entry, thin_raw_edge |
| `KXBTC15M-26MAY060215-15` | yes/no | -16c | -154c | -138c | 77 | 0.869074 | 0.921532 | 69 | None | absd_gte085, ask_gte70, depth_lte150, depth_lte384, exit_cents_gte60, fv_or_entry_timing_error, near_boundary, p_side_gte85, recross_hazard_high, small_10_24c, thin_touch_depth |
| `KXBTC15M-26MAY070015-15` | no/yes | -2c | -140c | -138c | 70 | 0.963659 | 1.543579 | 69 | 0.596562 | absd_gte085, ask_gte70, exit_cents_gte60, exit_p_hold_lt60, fv_or_entry_timing_error, micro_lt_10c, p_side_gte85 |
| `KXBTC15M-26MAY051715-15` | yes/no | -28c | -164c | -136c | 82 | 0.877551 | 0.960247 | 68 | None | absd_gte085, ask_gte70, depth_lte150, depth_lte384, exit_cents_gte60, fv_or_entry_timing_error, medium_25_49c, near_boundary, p_side_gte85, recross_hazard_high, rich_entry, thin_raw_edge |
| `KXBTC15M-26MAY061300-00` | yes/no | -30c | -160c | -130c | 80 | 0.860906 | 0.913273 | 65 | 0.66643 | absd_gte085, ask_gte70, crowded_depth, exit_cents_gte60, exit_p_hold_60_75, fv_or_entry_timing_error, medium_25_49c, near_boundary, p_side_gte85, recross_hazard_high, rich_entry, thin_raw_edge |
| `KXBTC15M-26MAY051615-15` | no/yes | -24c | -152c | -128c | 76 | 0.855253 | 0.878092 | 64 | None | absd_gte085, ask_gte70, depth_lte150, depth_lte384, exit_cents_gte60, fv_or_entry_timing_error, near_boundary, p_side_gte85, recross_hazard_high, small_10_24c, thin_touch_depth |
| `KXBTC15M-26MAY052100-00` | no/yes | -30c | -158c | -128c | 79 | 0.852877 | 0.892507 | 64 | None | absd_gte085, ask_gte70, depth_lte150, depth_lte384, exit_cents_gte60, fv_or_entry_timing_error, medium_25_49c, near_boundary, p_side_gte85, recross_hazard_high, thin_raw_edge |
