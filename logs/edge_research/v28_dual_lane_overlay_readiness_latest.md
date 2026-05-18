# v28 Dual-Lane Overlay Readiness

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:47:38.104222+00:00`
- Decision: `not_live_ready`
- Promotion use: `overlay_own_freeze_required`
- Overlay freeze UTC/local: `2026-05-07T16:34:55.927871+00:00` / `2026-05-07T12:34:55.927871-04:00`
- Windows since freeze / remaining: `29` / `1`
- Earliest overlay 30-window local time: `2026-05-07T20:04:55.927871-04:00`
- Best overlay policy: `post_dual_overlay_filter_entry_cheap_penalty025_rank_only`
- Current selected settled/net/W-L: `0` / `0c ($0.00)` / `0/0`
- Diagnostic best filter: `yes_recross_le0.3` delta `130c ($1.30)`

## Checks

| check | status | evidence | blocker |
|---|---|---|---|
| `overlay_filter_frozen` | `pass` | freeze=2026-05-07T16:34:55.927871+00:00 local=2026-05-07T12:34:55.927871-04:00 rule={'name': 'dual_lane_overlay_no_recross_le030', 'recross_hazard_score_max': 0.3, 'side': 'no', 'use': 'risk_control_overlay_only'} |  |
| `strict_own_freeze_sample` | `blocked` | selected_settled=0/30; windows_remaining=1 | overlay_waiting_for_30_selected_rows |
| `positive_selected_net` | `blocked` | selected_net=0c ($0.00) | overlay_selected_net_not_positive |
| `selected_source_quality` | `blocked` | selected_reconstructed_share=n/a max=35.00% | overlay_source_share_unknown_or_gt_35pct |
| `selected_full_loss_cushion` | `blocked` | selected_full_loss_cushion=0/3 | overlay_full_loss_cushion_lt_3 |
| `same_window_parent_candidate_not_replacement` | `pass` | current_union_delta_vs_live=-181c ($-1.81) |  |
| `diagnostic_filter_shape_positive` | `pass` | best_filter=yes_recross_le0.3 rows=4 diagnostic_delta=130c ($1.30) |  |
| `diagnostic_overlay_split_understood` | `pass` | helpful_delta=439c ($4.39) harmful_delta=-464c ($-4.64) |  |
| `selected_same_window_live_edge` | `blocked` | selected_candidate_minus_live=0c ($0.00) candidate=0c ($0.00) live_same=0c ($0.00) selected_markets=0 | overlay_selected_rows_not_beating_live_same_markets |

## Blocked Checks

- `strict_own_freeze_sample`
- `positive_selected_net`
- `selected_source_quality`
- `selected_full_loss_cushion`
- `selected_same_window_live_edge`

## Next Actions

- Keep collecting strict own-freeze overlay rows; do not promote from the diagnostic filter frontier.
- At/after the overlay 30-window gate, force replay the overlay watch and compare selected markets against live v28 same-window PnL.
- If selected rows remain too sparse, keep it as a diagnostic risk flag rather than a live overlay.
- Do not let overlay-specific gates weaken the main broad dual-lane readiness gate.
