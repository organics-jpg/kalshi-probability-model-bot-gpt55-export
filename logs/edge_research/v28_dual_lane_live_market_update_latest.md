# v28 Dual-Lane Live Market Update

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:47:38.251064+00:00`
- Decision: `no_live_test`
- Freeze UTC/local: `2026-05-07T13:00:17.363339+00:00` / `2026-05-07T09:00:17.363339-04:00`
- Live baseline: `-256c ($-2.56)`
- Next action: Review missing score gates on the own-freeze union rows.

## Incoming-Market Status

- Possible windows since freeze: `347`
- Windows remaining to 30-row gate: `0`
- Earliest possible 30-window local time: `2026-05-07T16:30:17.363339-04:00`
- Post-freeze events / entry rows / distinct markets: `2842` / `26` / `18`
- Settled / pending exit-clock rows: `26` / `0`

## Preview Performance

| preview | entries | settled | W/L | coverage | net | recon | cushion | source counts |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| sidecar exact observable | 12 | 12 | 11/1 | 66.67% | 304c ($3.04) | 0.00% | 3 | `{'approved_entry': 12}` |
| primary sizing-pocket risk proxy | 16 | 16 | 4/12 | 88.89% | -40c ($-0.40) | 100.00% | 0 | `{'rejected_actionable': 16}` |

## Realized PnL Sign

| preview | settlement W/L | PnL W/L/flat | note |
|---|---:|---:|---|
| sidecar exact observable | 11/1 | 10/2/0 | exit PnL can differ from settlement direction |
| primary sizing-pocket risk proxy | 4/12 | 4/12/0 | risk proxy only, not actual primary selection |

## Strict Replay Precheck

- Generated UTC: `2026-05-08T03:51:40.155563+00:00`
- Promotion use: `not_promotion_evidence_before_min_sample`
- Precheck windows / current windows: `59` / `347`

| policy | settled | W/L | coverage | net | recon | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| `post_dual_union_birth_entry_cheap_penalty025_rank_only` | 16 | 13/3 | 88.89% | 59c ($0.59) | 18.75% | 0 | settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |

## Variant Contrast

- Generated UTC: `2026-05-11T03:46:05.026181+00:00`
- Current preferred immature precheck lane: `entry`
- Bridge minus entry net: `0c ($0.00)`
- Bridge minus entry coverage: `0.00%`

## Loss Bottleneck Audit

- Generated UTC: `2026-05-11T03:46:05.113250+00:00`
- Promotion use: `diagnostic_only_before_30_settled_rows`
- Baseline forced-precheck W/L/net: `13/3` / `59c ($0.59)`
- High-cost low-edge shrink stress: `122c ($1.22)` delta `63c ($0.63)`
- Loss tags: `none`

## Parent-Shrink Repair Watch

- Freeze UTC/local: `2026-05-07T15:19:20.874849+00:00` / `2026-05-07T11:19:20.874849-04:00`
- Promotion use: `own_freeze_only`
- Windows since repair freeze / remaining: `53` / `0`
- Earliest repair 30-window local time: `2026-05-07T18:49:20.874849-04:00`

| repair policy | settled | W/L | coverage | net | recon | cushion | live ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `post_dual_parent_shrink_entry_cheap_penalty025_rank_only` | 7 | 7/0 | 87.50% | 185c ($1.85) | 42.86% | 1 | `False` | settled_lt_30, full_loss_cushion_lt_3, reconstructed_share_gt_35pct, does_not_beat_refreshed_live_baseline |

## Parent-Shrink Weight Frontier

- Freeze UTC/local: `2026-05-07T15:33:12.317447+00:00` / `2026-05-07T11:33:12.317447-04:00`
- Windows since frontier freeze / remaining: `51` / `0`
- Earliest frontier 30-window local time: `2026-05-07T19:03:12.317447-04:00`
- Best current label/weight: `shrink25_weight075` / `0.75`
- Best current settled/net: `7` / `155c ($1.55)`

## Sidecar-Safety Fallback Watch

- Freeze UTC/local: `2026-05-07T16:16:00.768697+00:00` / `2026-05-07T12:16:00.768697-04:00`
- Promotion use: `own_freeze_only`
- Windows since safety freeze / remaining: `29` / `1`
- Earliest safety 30-window local time: `2026-05-07T19:46:00.768697-04:00`

| safety policy | settled | W/L | coverage | net | recon | cushion | live ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `post_dual_sidecar_safety_entry_cheap_penalty025_rank_only` | 0 | 0/0 | 0.00% | 0c ($0.00) | n/a | 0 | `False` | settled_lt_30, net_not_positive, full_loss_cushion_lt_3, coverage_lt_75pct, source_share_unknown, does_not_beat_refreshed_live_baseline |

## Same-Window Live Compare

- Generated UTC: `2026-05-11T03:47:37.865013+00:00`
- Promotion use: `same_window_research_only`
- Live post-freeze trades/markets: `31` / `14`
- Candidate minus live on same markets: `-181c ($-1.81)`

| scope | entries/markets | W/L | coverage | net | cushion |
|---|---:|---:|---:|---:|---:|
| candidate forced precheck | 16 | 13/3 | 88.89% | 59c ($0.59) | 0 |
| live v28 same candidate markets | 14 | 7/7 | 77.78% | 240c ($2.40) | 2 |

## Overlay Opportunity Audit

- Generated UTC: `2026-05-11T03:47:37.989322+00:00`
- Promotion use: `diagnostic_only_overlay_design`
- Current same-window delta: `-181c ($-1.81)`

| split | rows | candidate net | live net | candidate-live |
|---|---:|---:|---:|---:|
| helpful/no-live-pnl buckets | 8 | 251c ($2.51) | -188c ($-1.88) | 439c ($4.39) |
| harmful buckets | 7 | -30c ($-0.30) | 434c ($4.34) | -464c ($-4.64) |
- Dual-lane is not currently a live-v28 replacement.
- Its useful shape is as a possible risk-control overlay on markets where live v28 churns or loses.
- The blocker is winner capture: live v28 made large same-side gains on several markets that dual-lane clipped to small wins.
- A live-ready repair must preserve live v28's winner capture while using dual-lane only where it has forward evidence of reducing live loss clusters.

## Overlay Filter Own-Freeze Watch

- Freeze UTC/local: `2026-05-07T16:34:55.927871+00:00` / `2026-05-07T12:34:55.927871-04:00`
- Promotion use: `own_freeze_only`
- Windows since filter freeze / remaining: `29` / `1`
- Earliest filter 30-window local time: `2026-05-07T20:04:55.927871-04:00`

| filter policy | settled | W/L | coverage | net | recon | cushion | live ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `post_dual_overlay_filter_entry_cheap_penalty025_rank_only` | 0 | 0/0 | 0.00% | 0c ($0.00) | n/a | 0 | `False` | overlay_selected_settled_lt_30, overlay_net_not_positive, overlay_full_loss_cushion_lt_3, overlay_source_share_unknown |

## Overlay Same-Window Compare

- Generated UTC: `2026-05-11T03:47:37.726264+00:00`
- Promotion use: `overlay_same_window_research_only`
- Selected markets: `0`
- Candidate minus live on selected markets: `0c ($0.00)`

| scope | entries/markets | W/L | net | cushion |
|---|---:|---:|---:|---:|
| overlay selected rows | 0 | 0/0 | 0c ($0.00) | 0 |
| live v28 same selected markets | 0 | 0/0 | 0c ($0.00) | 0 |

## Overlay Readiness

- Generated UTC: `2026-05-11T03:47:38.104222+00:00`
- Decision: `not_live_ready`
- Promotion use: `overlay_own_freeze_required`
- Blocked checks: `strict_own_freeze_sample, positive_selected_net, selected_source_quality, selected_full_loss_cushion, selected_same_window_live_edge`

## Overlay V2 Filter Own-Freeze Watch

- Freeze UTC/local: `2026-05-07T16:50:03.875032+00:00` / `2026-05-07T12:50:03.875032-04:00`
- Promotion use: `own_freeze_only`
- Rule: `raw_edge >= 0.05, recross <= 0.30, abs_d_sigma >= 0.85`
- Windows since filter freeze / remaining: `331` / `0`
- Earliest filter 30-window local time: `2026-05-07T20:20:03.875032-04:00`

| filter policy | settled | W/L | coverage | net | recon | cushion | live ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `post_dual_overlay_filter_entry_cheap_penalty025_rank_only` | 1 | 1/0 | 50.00% | 44c ($0.44) | 0.00% | 0 | `False` | overlay_selected_settled_lt_30, overlay_full_loss_cushion_lt_3, overlay_source_gate_zero_row_margin |

## Overlay V2 Same-Window Compare

- Generated UTC: `2026-05-11T03:47:37.708127+00:00`
- Promotion use: `overlay_same_window_research_only`
- Selected markets: `1`
- Candidate minus live on selected markets: `52c ($0.52)`

| scope | entries/markets | W/L | net | cushion |
|---|---:|---:|---:|---:|
| overlay v2 selected rows | 1 | 1/0 | 44c ($0.44) | 0 |
| live v28 same selected markets | 1 | 0/1 | -8c ($-0.08) | 0 |

## Overlay V2 Readiness

- Generated UTC: `2026-05-11T03:47:37.858220+00:00`
- Decision: `not_live_ready`
- Promotion use: `overlay_own_freeze_required`
- Blocked checks: `strict_own_freeze_sample, selected_full_loss_cushion`

## Mechanism Read

- `sidecar_live_shadow_shape_is_constructive`
- `primary_proxy_is_all_source_quality_risk`
- `primary_proxy_is_below_sidecar_distance_band`
- `do_not_use_primary_proxy_as_live_ready_evidence`
- `own_freeze_strict_rows_remain_authoritative`

## Hard Blockers

- `own_freeze_settled_lt_30`
- `own_freeze_full_loss_cushion_lt_3`

## Own-Freeze Promotion Rows

| policy | settled | W/L | coverage | net | recon | cushion | live ready | missing gates |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `post_dual_union_birth_entry_cheap_penalty025_rank_only` | 14 | 12/2 | 77.78% | 49c ($0.49) | 14.29% | 0 | `False` | settled_lt_30, full_loss_cushion_lt_3 |
| `post_dual_union_birth_bridge_cheap_penalty025_rank_only` | 14 | 12/2 | 77.78% | 49c ($0.49) | 14.29% | 0 | `False` | settled_lt_30, full_loss_cushion_lt_3 |
