# v28 Dual-Lane Live-Ready Handoff

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:47:37.807692+00:00`
- Decision: `no_live_test`
- Freeze UTC/local: `2026-05-07T13:00:17.363339+00:00` / `2026-05-07T09:00:17.363339-04:00`
- Live baseline: `-256c ($-2.56)`
- Windows since freeze / remaining: `347` / `0`
- Earliest 30-window local checkpoint: `2026-05-07T16:30:17.363339-04:00`
- Post-freeze events / entry rows / markets: `2842` / `26` / `18`

## Current Read

- The dual-lane candidate is collecting live/shadow market evidence, but is not live-ready.
- The sidecar observable preview is the constructive approved-source signal.
- The primary sizing-pocket proxy remains source-quality/FV-risk context only, not the actual primary selection.
- The corrected heavy strict replay path is verified and should be trusted over preview rows at the 30-window gate.
- The current loss bottleneck is expensive low-edge parent fills; a parent-shrink repair branch is now frozen separately.
- The broad dual-lane branch currently trails live v28 on the same post-freeze markets, so it is not merely waiting on sample size.
- The strongest current repair shape is a narrow overlay, not a replacement: avoid live-v28 loss clusters without clipping live's large winners.

## Current Metrics

| layer | entries | settled | W/L | PnL W/L | coverage | net | recon | cushion |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| sidecar preview | 12 | 12 | 11/1 | 10/2 | 66.67% | 304c ($3.04) | 0.00% | 3 |
| primary proxy | 16 | 16 | 4/12 | 4/12 | 88.89% | -40c ($-0.40) | 100.00% | 0 |
| strict precheck `post_dual_union_birth_entry_cheap_penalty025_rank_only` | n/a | 16 | 13/3 | n/a | 88.89% | 59c ($0.59) | 18.75% | 0 |

## Variant Contrast

- Current immature precheck preference: `entry`
- Bridge minus entry net: `0c ($0.00)`
- Bridge minus entry coverage: `0.00%`
- Precheck/current windows: `59` / `346`

## Loss Bottleneck And Repair

- Loss audit tags: `none`
- Original forced-precheck baseline: `13/3` / `59c ($0.59)`
- Parent-shrink stress result on diagnostic rows: `122c ($1.22)` delta `63c ($0.63)`
- Parent-shrink repair freeze: `2026-05-07T15:19:20.874849+00:00` / `2026-05-07T11:19:20.874849-04:00`
- Parent-shrink windows since freeze / remaining: `53` / `0`
- Parent-shrink best own-freeze row count/net: `7` / `185c ($1.85)`
- Frontier freeze: `2026-05-07T15:33:12.317447+00:00` / `2026-05-07T11:33:12.317447-04:00`
- Frontier best label/weight: `shrink25_weight075` / `0.75`
- Frontier best own-freeze row count/net: `7` / `155c ($1.55)`

## Same-Window Live Comparison

- Candidate policy: `post_dual_union_birth_entry_cheap_penalty025_rank_only`
- Candidate W/L/net: `13/3` / `59c ($0.59)`
- Live v28 same-market W/L/net: `7/7` / `240c ($2.40)`
- Candidate minus live on same markets: `-181c ($-1.81)`

## Overlay Branches

- Overlay split helpful/no-live rows: `8` rows, delta `439c ($4.39)`
- Overlay split harmful rows: `7` rows, delta `-464c ($-4.64)`
- Overlay v1 freeze/rule: `2026-05-07T16:34:55.927871+00:00` / `{'name': 'dual_lane_overlay_no_recross_le030', 'recross_hazard_score_max': 0.3, 'side': 'no', 'use': 'risk_control_overlay_only'}`
- Overlay v2 freeze/rule: `2026-05-07T16:50:03.875032+00:00` / `{'abs_d_sigma_min': 0.85, 'name': 'dual_lane_overlay_raw05_recross_le030_abs085', 'raw_edge_min': 0.05, 'recross_hazard_score_max': 0.3, 'use': 'risk_control_overlay_only'}`
- Overlay v2 current own-freeze selected rows/net: `1` / `44c ($0.44)`
- Overlay v2 readiness: `not_live_ready` blocked `strict_own_freeze_sample, selected_full_loss_cushion`

## Verified Tooling

- Strict replay accounting patch verified: `True`
- Score path read: `strict_replay_sidecar_net_uses_boundary_clock_feature_gate_net`
- Accounting audit UTC: `2026-05-11T03:46:04.938176+00:00`

## Passed Checks

- `beats_live_baseline`
- `coverage_band`
- `frozen_candidate_birth`
- `overlay_filter_registered`
- `overlay_shape_classified`
- `overlay_v2_filter_registered`
- `parent_shrink_frontier_registered`
- `parent_shrink_repair_registered`
- `positive_after_fees`
- `preview_sidecar_shape`
- `primary_proxy_risk_understood`
- `shadow_collection_flowing`
- `sidecar_safety_registered`
- `source_quality`
- `strict_replay_path_prechecked`

## Blocked Checks

- `minimum_forward_sample`
- `fragility_cushion`
- `strict_precheck_freshness`
- `loss_bottleneck_classified`
- `parent_shrink_forward_sample`
- `parent_shrink_frontier_forward_sample`
- `sidecar_safety_forward_sample`
- `same_window_live_edge`
- `overlay_filter_forward_sample`
- `overlay_v2_filter_forward_sample`

## Next Actions

- Do not live-test before the normal own-freeze gate reaches at least 30 settled strict-forward rows.
- At or after the 4:30pm ET 30-window checkpoint, refresh live baseline and run the normal own-freeze watch without force.
- If the normal own-freeze watch still reports zero rows after the checkpoint, debug scorer joins immediately; the forced precheck proved the heavy path can execute.
- If both entry and bridge clear sample/source/coverage/PnL gates, prefer the one with better full-loss cushion and live-baseline delta.
- If bridge remains higher PnL but entry remains higher coverage, do not collapse the choice to PnL alone; use full promotion gates.
- Refresh the manual strict precheck if its window lag exceeds one before the 30-window gate.
- Track the parent-shrink repair branch from its own freeze and do not promote it before its own 30-row gate.
- Use the parent-shrink frontier to compare shrink strengths under one freeze before choosing a live candidate weight.
- Treat the current broad dual-lane branch as blocked by same-window live underperformance until it beats live v28 on the same post-freeze markets.
- Track overlay v1 and v2 as risk-control overlays only; do not use their diagnostic green rows as promotion evidence before their own freezes mature.
- If live testing remains desired, build the paper coordinator milestone first; do not launch a second independent live bot.

## Checkpoint Command

```powershell
.\scripts\run_v28_dual_lane_30_window_checkpoint.ps1
```

Optional diagnostic precheck, not promotion evidence before sample maturity:

```powershell
.\scripts\run_v28_dual_lane_30_window_checkpoint.ps1 -RunStrictPrecheck
```

## Key Artifacts

- `checkpoint_runner`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\scripts\run_v28_dual_lane_30_window_checkpoint.ps1`
- `live_market_update`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_live_market_update_latest.json`
- `readiness_checklist`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_readiness_checklist_latest.json`
- `snapshot_ledger`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_live_market_snapshot_ledger_latest.md`
- `strict_replay_precheck`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_strict_replay_precheck_latest.md`
- `accounting_audit`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_strict_replay_accounting_audit_latest.md`
- `variant_contrast`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_variant_contrast_latest.md`
- `loss_bottleneck_audit`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_loss_bottleneck_audit_latest.md`
- `parent_shrink_watch`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_parent_shrink_watch_latest.md`
- `parent_shrink_frontier_watch`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_parent_shrink_frontier_watch_latest.md`
- `same_window_live_compare`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_same_window_live_compare_latest.md`
- `overlay_opportunity_audit`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_overlay_opportunity_audit_latest.md`
- `overlay_filter_watch`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_overlay_filter_watch_latest.md`
- `overlay_v2_filter_watch`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_overlay_filter_v2_watch_latest.md`
- `overlay_v2_readiness`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_overlay_v2_readiness_latest.md`
- `live_test_blocker_audit`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_live_test_blocker_audit_latest.md`
- `live_test_coordinator_spec`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_live_test_coordinator_spec_latest.md`
- `paper_coordinator_replay`: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_paper_coordinator_replay_latest.md`
