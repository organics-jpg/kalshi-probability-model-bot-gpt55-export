# v28 Dual-Lane Overlay Readiness

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:47:37.858220+00:00`
- Decision: `not_live_ready`
- Promotion use: `overlay_own_freeze_required`
- Overlay freeze UTC/local: `2026-05-07T16:50:03.875032+00:00` / `2026-05-07T12:50:03.875032-04:00`
- Windows since freeze / remaining: `331` / `0`
- Earliest overlay 30-window local time: `2026-05-07T20:20:03.875032-04:00`
- Best overlay policy: `post_dual_overlay_filter_entry_cheap_penalty025_rank_only`
- Current selected settled/net/W-L: `1` / `44c ($0.44)` / `1/0`
- Diagnostic best filter: `yes_recross_le0.3` delta `130c ($1.30)`

## Checks

| check | status | evidence | blocker |
|---|---|---|---|
| `overlay_filter_frozen` | `pass` | freeze=2026-05-07T16:50:03.875032+00:00 local=2026-05-07T12:50:03.875032-04:00 rule={'abs_d_sigma_min': 0.85, 'name': 'dual_lane_overlay_raw05_recross_le030_abs085', 'raw_edge_min': 0.05, 'recross_hazard_score_max': 0.3, 'use': 'risk_control_overlay_only'} |  |
| `strict_own_freeze_sample` | `blocked` | selected_settled=1/30; windows_remaining=0 | overlay_waiting_for_30_selected_rows |
| `positive_selected_net` | `pass` | selected_net=44c ($0.44) |  |
| `selected_source_quality` | `pass` | selected_reconstructed_share=0.00% max=35.00% |  |
| `selected_full_loss_cushion` | `blocked` | selected_full_loss_cushion=0/3 | overlay_full_loss_cushion_lt_3 |
| `same_window_parent_candidate_not_replacement` | `pass` | current_union_delta_vs_live=-181c ($-1.81) |  |
| `diagnostic_filter_shape_positive` | `pass` | best_filter=yes_recross_le0.3 rows=4 diagnostic_delta=130c ($1.30) |  |
| `diagnostic_overlay_split_understood` | `pass` | helpful_delta=439c ($4.39) harmful_delta=-464c ($-4.64) |  |
| `selected_same_window_live_edge` | `pass` | selected_candidate_minus_live=52c ($0.52) candidate=44c ($0.44) live_same=-8c ($-0.08) selected_markets=1 |  |

## Blocked Checks

- `strict_own_freeze_sample`
- `selected_full_loss_cushion`

## Next Actions

- Keep collecting strict own-freeze overlay rows; do not promote from the diagnostic filter frontier.
- At/after the overlay 30-window gate, force replay the overlay watch and compare selected markets against live v28 same-window PnL.
- If selected rows remain too sparse, keep it as a diagnostic risk flag rather than a live overlay.
- Do not let overlay-specific gates weaken the main broad dual-lane readiness gate.
