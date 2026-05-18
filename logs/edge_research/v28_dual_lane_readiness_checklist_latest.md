# v28 Dual-Lane Readiness Checklist

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:47:38.361843+00:00`
- Decision: `not_live_ready`
- Freeze UTC/local: `2026-05-07T13:00:17.363339+00:00` / `2026-05-07T09:00:17.363339-04:00`
- Live baseline: `-256c ($-2.56)`
- Current policy: `post_dual_union_birth_entry_cheap_penalty025_rank_only`

## Checklist

| check | status | evidence | blocker |
|---|---|---|---|
| `frozen_candidate_birth` | `pass` | freeze=2026-05-07T13:00:17.363339+00:00 local=2026-05-07T09:00:17.363339-04:00 |  |
| `shadow_collection_flowing` | `pass` | events=2842 entry_rows=26 markets=18 |  |
| `minimum_forward_sample` | `blocked` | own_freeze_settled=14/30; windows_remaining=0 | waiting_for_30_strict_rows |
| `positive_after_fees` | `pass` | own_freeze_net=49c ($0.49) |  |
| `beats_live_baseline` | `pass` | own_freeze_net=49c ($0.49) live_baseline=-256c ($-2.56) needed=0c ($0.00) |  |
| `coverage_band` | `pass` | own_freeze_coverage=77.78% target=75.0-90.0% |  |
| `source_quality` | `pass` | own_freeze_reconstructed_share=14.29% max=35.00% |  |
| `fragility_cushion` | `blocked` | own_freeze_full_loss_cushion=0/3 | full_loss_cushion_lt_3 |
| `preview_sidecar_shape` | `pass` | sidecar_preview=304c ($3.04) W/L=11/1 recon=0.00% |  |
| `primary_proxy_risk_understood` | `pass` | primary_proxy=-40c ($-0.40) source_counts={'rejected_actionable': 16} |  |
| `strict_replay_path_prechecked` | `pass` | precheck_settled=16 net=59c ($0.59) precheck_windows=59 current_windows=347 promotion_use=not_promotion_evidence_before_min_sample |  |
| `strict_precheck_freshness` | `blocked` | precheck_windows=59 current_windows=347 lag=288 | strict_replay_precheck_stale |
| `loss_bottleneck_classified` | `blocked` | tags=[] next=Test a parent-fill confidence shrink for expensive low-edge rows inside the dual-lane research scorer, then re-run strict precheck and wait for the 30-row own-freeze gate. | current_losses_not_classified_into_actionable_shape |
| `parent_shrink_repair_registered` | `pass` | repair_freeze=2026-05-07T15:19:20.874849+00:00 local=2026-05-07T11:19:20.874849-04:00 rule={'ask_prob_min': 0.78, 'component': 'strict_parent_midprice_hold_fill', 'raw_edge_max': 0.09, 'weight': 0.5} |  |
| `parent_shrink_forward_sample` | `blocked` | repair_settled=7/30; repair_windows_remaining=0 | repair_branch_waiting_for_30_strict_rows |
| `parent_shrink_frontier_registered` | `pass` | frontier_freeze=2026-05-07T15:33:12.317447+00:00 local=2026-05-07T11:33:12.317447-04:00 weights=[{'label': 'shrink25_weight075', 'weight': 0.75}, {'label': 'shrink50_weight050', 'weight': 0.5}, {'label': 'shrink75_weight025', 'weight': 0.25}] |  |
| `parent_shrink_frontier_forward_sample` | `blocked` | frontier_best=shrink25_weight075 settled=7/30; frontier_windows_remaining=0 | frontier_branch_waiting_for_30_strict_rows |
| `sidecar_safety_registered` | `pass` | safety_freeze=2026-05-07T16:16:00.768697+00:00 local=2026-05-07T12:16:00.768697-04:00 rule=sidecar_first_until_parent_lane_proves_forward_safety |  |
| `sidecar_safety_forward_sample` | `blocked` | safety_best=post_dual_sidecar_safety_entry_cheap_penalty025_rank_only settled=0/30; safety_windows_remaining=1 | sidecar_safety_waiting_for_30_strict_rows |
| `same_window_live_edge` | `blocked` | candidate_minus_live_same_markets=-181c ($-1.81) candidate=59.0c live_same=240.0c | candidate_not_beating_live_on_same_post_freeze_markets |
| `overlay_shape_classified` | `pass` | helpful_delta=439c ($4.39) harmful_delta=-464c ($-4.64) read=['Dual-lane is not currently a live-v28 replacement.'] |  |
| `overlay_filter_registered` | `pass` | filter_freeze=2026-05-07T16:34:55.927871+00:00 local=2026-05-07T12:34:55.927871-04:00 rule={'name': 'dual_lane_overlay_no_recross_le030', 'recross_hazard_score_max': 0.3, 'side': 'no', 'use': 'risk_control_overlay_only'} |  |
| `overlay_filter_forward_sample` | `blocked` | filter_best=post_dual_overlay_filter_entry_cheap_penalty025_rank_only settled=0/30; filter_windows_remaining=1 | overlay_filter_waiting_for_30_strict_rows |
| `overlay_v2_filter_registered` | `pass` | filter_v2_freeze=2026-05-07T16:50:03.875032+00:00 local=2026-05-07T12:50:03.875032-04:00 rule={'abs_d_sigma_min': 0.85, 'name': 'dual_lane_overlay_raw05_recross_le030_abs085', 'raw_edge_min': 0.05, 'recross_hazard_score_max': 0.3, 'use': 'risk_control_overlay_only'} |  |
| `overlay_v2_filter_forward_sample` | `blocked` | filter_v2_best=post_dual_overlay_filter_entry_cheap_penalty025_rank_only settled=1/30; filter_v2_windows_remaining=0 | overlay_v2_filter_waiting_for_30_strict_rows |

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

## Next Readiness Actions

- Keep collecting until strict own-freeze scorer has at least 30 settled rows.
- At the 30-window mark, run the heavy own-freeze replay and trust those rows over preview rows.
- Refresh the manual strict replay precheck if its window lag grows beyond one window before the 30-window gate.
- If source share remains unknown/high, inspect scorer joins before considering any live test.
- If sidecar stays clean but union fails because of primary source risk, isolate that as a dual-lane component issue before any promotion.
- Track the parent-shrink repair branch from its own freeze; do not use rows before that repair freeze as promotion evidence.
- Track the parent-shrink weight frontier from its own freeze; use it only to choose shrink strength after forward evidence matures.
- Track the sidecar-safety fallback from its own freeze as the clean fallback if parent-lane repairs remain unsafe.
- Use same-window live comparison as a bottleneck diagnostic; do not treat total-live-baseline comparison as the only signal.
- Track the NO-side low-recross overlay filter from its own freeze before considering it as a risk-control overlay.
- Track the raw-edge/low-recross/distance overlay v2 filter from its own freeze before considering it as a risk-control overlay.
