# v28 Dual-Lane Strict Replay Precheck

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-08T03:51:40.155563+00:00`
- Promotion use: `not_promotion_evidence_before_min_sample`
- Freeze UTC/local: `2026-05-07T13:00:17.363339+00:00` / `2026-05-07T09:00:17.363339-04:00`
- Live baseline: `2215c ($22.15)`
- Possible windows / remaining: `59` / `0`
- Earliest 30-window local time: `2026-05-07T16:30:17.363339-04:00`
- Force replay: `True`
- Pre-sample short-circuit: `False`

## Read

- Heavy strict replay path executed successfully.
- Rows are diagnostic precheck only until the 30-settled-row own-freeze gate is available.
- Use this to detect scorer/join failures early, not to approve live testing.

## Best Forced-Replay Union

| policy | settled | W/L | coverage | net | recon | cushion | source counts | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `post_dual_union_birth_entry_cheap_penalty025_rank_only` | 16 | 13/3 | 88.89% | 59c ($0.59) | 18.75% | 0 | `{'approved_entry': 13, 'rejected_actionable': 3}` | settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |

## All Forced-Replay Unions

| sidecar | settled | W/L | coverage | net | recon | shared | add net | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `post_dual_union_birth_entry_cheap_penalty025_rank_only` | 16 | 13/3 | 88.89% | 59c ($0.59) | 18.75% | 14 | 10c ($0.10) | settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `post_dual_union_birth_bridge_cheap_penalty025_rank_only` | 16 | 13/3 | 88.89% | 59c ($0.59) | 18.75% | 14 | 10c ($0.10) | settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |

## Worst Rows

| market | side | source | component | net | raw edge | recross | abs d | ask |
|---|---|---|---|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY071100-00` | yes | approved_entry | strict_delayed_recheck_rescue:drop15_bid60 | -166c ($-1.66) | 0.054041000000000006 | 0.30500573389101787 | 1.010241 | 0.83 |
| `KXBTC15M-26MAY071015-15` | no | approved_entry | strict_delayed_recheck_rescue:drop15_bid60 | -162c ($-1.62) | 0.08109199999999994 | 0.41762272221317515 | 0.936079 | 0.78 |
| `KXBTC15M-26MAY071300-00` | yes | rejected_actionable | continuous_penalty:cheap_penalty025_rank_only | -10c ($-0.10) | None | 0.0838612713123607 | 0.932497 | 0.08 |
| `KXBTC15M-26MAY071030-30` | no | rejected_actionable | strict_parent_midprice_hold_fill | 7c ($0.07) | 0.05652999999999997 | 0.17951837352707734 | 1.625821 | 0.91 |
| `KXBTC15M-26MAY071130-30` | no | approved_entry | strict_parent_midprice_hold_fill | 13c ($0.13) | 0.06660100000000002 | 0.33188369997953837 | 1.183451 | 0.85 |
| `KXBTC15M-26MAY070915-15` | no | approved_entry | strict_parent_midprice_hold_fill | 20c ($0.20) | 0.10667300000000002 | 0.28381172517459047 | 0.951089 | 0.77 |
| `KXBTC15M-26MAY071215-15` | no | approved_entry | continuous_penalty:cheap_penalty025_rank_only | 20c ($0.20) | None | 0.2624012891254945 | 0.887915 | 0.78 |
| `KXBTC15M-26MAY071230-30` | yes | approved_entry | strict_parent_midprice_hold_fill | 21c ($0.21) | 0.08241900000000002 | 0.2960374313658712 | 0.882196 | 0.77 |
| `KXBTC15M-26MAY071045-45` | no | approved_entry | strict_parent_midprice_hold_fill | 22c ($0.22) | 0.11526000000000003 | 0.4699176077596592 | 0.953688 | 0.75 |
| `KXBTC15M-26MAY070945-45` | no | approved_entry | strict_parent_midprice_hold_fill | 28c ($0.28) | 0.16369900000000004 | 0.43642658262493145 | 0.882733 | 0.69 |
