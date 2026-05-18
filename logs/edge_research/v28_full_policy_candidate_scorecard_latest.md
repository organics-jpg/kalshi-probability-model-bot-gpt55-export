# v28 Full-Policy Candidate Scorecard

Research-only. This probe does not place orders or edit live bot logic.

- Generated UTC: `2026-05-07T21:43:52.279512+00:00`
- Decision: `no_live_test`
- Live baseline: `1361c`
- Candidate cards: `49`
- Live-test allowed cards: `0`

## Interpretation

- No complete policy card clears the live-test gates; continue frozen forward collection.
- Closest full policy is common_clock_strict_forward_v3 / loss_guard_value_p85_reduce_p79_gap0 with missing gates ['live_ready_false', 'suppressed_decisions_lt_30'].

## Closest Full Policies

| gate | policy | source | settled | net | delta live/current | coverage | recon | suppressions | missing gates |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `common_clock_strict_forward_v3` | `loss_guard_value_p85_reduce_p79_gap0` | exit_policy_watch_dashboard | 46 | 692c | 214c | n/a | n/a | 13 | live_ready_false, suppressed_decisions_lt_30 |
| `common_clock_strict_forward_v2` | `loss_guard_value_p85_reduce_p79_gap0` | exit_policy_watch_dashboard | 58 | 668c | 242c | n/a | n/a | 17 | live_ready_false, suppressed_decisions_lt_30 |
| `book_gap_loss_guard_v3` | `book_gap_loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0` | exit_policy_watch_dashboard | 46 | 644c | 166c | n/a | n/a | 9 | live_ready_false, suppressed_decisions_lt_30 |
| `common_clock_strict_forward_v1` | `loss_guard_value_p85_reduce_p79_gap0` | exit_policy_watch_dashboard | 59 | 582c | 242c | n/a | n/a | 17 | live_ready_false, suppressed_decisions_lt_30 |
| `exit_reduce_drift_guard` | `high_p_favorable_fv` | exit_policy_watch_dashboard | 40 | 556c | 46c | n/a | n/a | 1 | live_ready_false, suppressed_decisions_lt_30 |
| `top_component_false_negative_rescue_child` | `diagnostic_approved_union_rebound` | controlled_live_test_gate | 76 | 2102c | 742c | 75.25% | 34.21% |  | live_ready_false, not_strict_forward, diagnostic_prefreeze |
| `top_component_false_negative_rescue_child` | `diagnostic_union_rebound` | controlled_live_test_gate | 76 | 2102c | 742c | 75.25% | 34.21% |  | live_ready_false, not_strict_forward, diagnostic_prefreeze |
| `top_component_false_negative_rescue_child` | `diagnostic_low_exit_collapse_rebound` | controlled_live_test_gate | 76 | 2008c | 648c | 75.25% | 34.21% |  | live_ready_false, not_strict_forward, diagnostic_prefreeze |
| `top_component_false_negative_rescue_child` | `diagnostic_mid_recheck_value_rebound` | controlled_live_test_gate | 76 | 1926c | 566c | 75.25% | 34.21% |  | live_ready_false, not_strict_forward, diagnostic_prefreeze |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty025_rank_only` | controlled_live_test_gate | 83 | 1842c | 482c | 82.18% | 21.69% |  | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty050_rank_only` | controlled_live_test_gate | 83 | 1842c | 482c | 82.18% | 21.69% |  | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |
| `dual_lane_overlap_union` | `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty100_rank_only` | controlled_live_test_gate | 83 | 1842c | 482c | 82.18% | 21.69% |  | live_ready_false, not_strict_forward, needs_own_frozen_forward_birth |

## Policy Contracts

### `common_clock_strict_forward_v3 / loss_guard_value_p85_reduce_p79_gap0`

- entry rule: Current live v28 approved entry stream.
- exit state rule: Replace or suppress selected current v28 exits using loss_guard_value_p85_reduce_p79_gap0.
- sizing rule: Current controlled v28 size discipline unless a future live-test spec narrows to size 1.
- risk kill rule: Kill or block live testing while not live-ready; suppressed exit decisions below 30.
- live test rule: No live candidate trades. Continue frozen forward collection in separate research artifacts.
- accounting pnl rule: Score on the frozen exit-policy watch dashboard against current-window v28 exits; reconcile later with live-only scorer if promoted.
- iteration rule: Collect post-freeze suppressions until >=30 decisions, zero/controlled loss-control cost, cushion >=3, then re-review.
- missing gates: live_ready_false, suppressed_decisions_lt_30

### `common_clock_strict_forward_v2 / loss_guard_value_p85_reduce_p79_gap0`

- entry rule: Current live v28 approved entry stream.
- exit state rule: Replace or suppress selected current v28 exits using loss_guard_value_p85_reduce_p79_gap0.
- sizing rule: Current controlled v28 size discipline unless a future live-test spec narrows to size 1.
- risk kill rule: Kill or block live testing while not live-ready; suppressed exit decisions below 30.
- live test rule: No live candidate trades. Continue frozen forward collection in separate research artifacts.
- accounting pnl rule: Score on the frozen exit-policy watch dashboard against current-window v28 exits; reconcile later with live-only scorer if promoted.
- iteration rule: Collect post-freeze suppressions until >=30 decisions, zero/controlled loss-control cost, cushion >=3, then re-review.
- missing gates: live_ready_false, suppressed_decisions_lt_30

### `book_gap_loss_guard_v3 / book_gap_loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0`

- entry rule: Current live v28 approved entry stream.
- exit state rule: Replace or suppress selected current v28 exits using book_gap_loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0.
- sizing rule: Current controlled v28 size discipline unless a future live-test spec narrows to size 1.
- risk kill rule: Kill or block live testing while not live-ready; suppressed exit decisions below 30.
- live test rule: No live candidate trades. Continue frozen forward collection in separate research artifacts.
- accounting pnl rule: Score on the frozen exit-policy watch dashboard against current-window v28 exits; reconcile later with live-only scorer if promoted.
- iteration rule: Collect post-freeze suppressions until >=30 decisions, zero/controlled loss-control cost, cushion >=3, then re-review.
- missing gates: live_ready_false, suppressed_decisions_lt_30

### `common_clock_strict_forward_v1 / loss_guard_value_p85_reduce_p79_gap0`

- entry rule: Current live v28 approved entry stream.
- exit state rule: Replace or suppress selected current v28 exits using loss_guard_value_p85_reduce_p79_gap0.
- sizing rule: Current controlled v28 size discipline unless a future live-test spec narrows to size 1.
- risk kill rule: Kill or block live testing while not live-ready; suppressed exit decisions below 30.
- live test rule: No live candidate trades. Continue frozen forward collection in separate research artifacts.
- accounting pnl rule: Score on the frozen exit-policy watch dashboard against current-window v28 exits; reconcile later with live-only scorer if promoted.
- iteration rule: Collect post-freeze suppressions until >=30 decisions, zero/controlled loss-control cost, cushion >=3, then re-review.
- missing gates: live_ready_false, suppressed_decisions_lt_30

### `exit_reduce_drift_guard / high_p_favorable_fv`

- entry rule: Current live v28 approved entry stream.
- exit state rule: Replace or suppress selected current v28 exits using high_p_favorable_fv.
- sizing rule: Current controlled v28 size discipline unless a future live-test spec narrows to size 1.
- risk kill rule: Kill or block live testing while not live-ready; suppressed exit decisions below 30.
- live test rule: No live candidate trades. Continue frozen forward collection in separate research artifacts.
- accounting pnl rule: Score on the frozen exit-policy watch dashboard against current-window v28 exits; reconcile later with live-only scorer if promoted.
- iteration rule: Collect post-freeze suppressions until >=30 decisions, zero/controlled loss-control cost, cushion >=3, then re-review.
- missing gates: live_ready_false, suppressed_decisions_lt_30

### `top_component_false_negative_rescue_child / diagnostic_approved_union_rebound`

- entry rule: Existing top-component parent/fill or false-negative-rescue entry stack.
- exit state rule: Current live v28 exit/state machine.
- sizing rule: Current controlled v28 size discipline unless a future live-test spec narrows to size 1.
- risk kill rule: Kill or block live testing while not live-ready; insufficient strict-forward evidence.
- live test rule: No live candidate trades. Continue frozen forward collection in separate research artifacts.
- accounting pnl rule: Score via candidate tracker/controlled-live gate against refreshed live_mushroom_v28_size2 live-only baseline after fees.
- iteration rule: Freeze or use own-freeze rows only; diagnostic rows can seed but not promote the policy.
- missing gates: live_ready_false, not_strict_forward, diagnostic_prefreeze

### `top_component_false_negative_rescue_child / diagnostic_union_rebound`

- entry rule: Existing top-component parent/fill or false-negative-rescue entry stack.
- exit state rule: Current live v28 exit/state machine.
- sizing rule: Current controlled v28 size discipline unless a future live-test spec narrows to size 1.
- risk kill rule: Kill or block live testing while not live-ready; insufficient strict-forward evidence.
- live test rule: No live candidate trades. Continue frozen forward collection in separate research artifacts.
- accounting pnl rule: Score via candidate tracker/controlled-live gate against refreshed live_mushroom_v28_size2 live-only baseline after fees.
- iteration rule: Freeze or use own-freeze rows only; diagnostic rows can seed but not promote the policy.
- missing gates: live_ready_false, not_strict_forward, diagnostic_prefreeze

### `top_component_false_negative_rescue_child / diagnostic_low_exit_collapse_rebound`

- entry rule: Existing top-component parent/fill or false-negative-rescue entry stack.
- exit state rule: Current live v28 exit/state machine.
- sizing rule: Current controlled v28 size discipline unless a future live-test spec narrows to size 1.
- risk kill rule: Kill or block live testing while not live-ready; insufficient strict-forward evidence.
- live test rule: No live candidate trades. Continue frozen forward collection in separate research artifacts.
- accounting pnl rule: Score via candidate tracker/controlled-live gate against refreshed live_mushroom_v28_size2 live-only baseline after fees.
- iteration rule: Freeze or use own-freeze rows only; diagnostic rows can seed but not promote the policy.
- missing gates: live_ready_false, not_strict_forward, diagnostic_prefreeze

### `top_component_false_negative_rescue_child / diagnostic_mid_recheck_value_rebound`

- entry rule: Existing top-component parent/fill or false-negative-rescue entry stack.
- exit state rule: Current live v28 exit/state machine.
- sizing rule: Current controlled v28 size discipline unless a future live-test spec narrows to size 1.
- risk kill rule: Kill or block live testing while not live-ready; insufficient strict-forward evidence.
- live test rule: No live candidate trades. Continue frozen forward collection in separate research artifacts.
- accounting pnl rule: Score via candidate tracker/controlled-live gate against refreshed live_mushroom_v28_size2 live-only baseline after fees.
- iteration rule: Freeze or use own-freeze rows only; diagnostic rows can seed but not promote the policy.
- missing gates: live_ready_false, not_strict_forward, diagnostic_prefreeze

### `dual_lane_overlap_union / top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty025_rank_only`

- entry rule: Existing dual-lane overlap/portfolio entry stack from frozen dual-lane artifacts.
- exit state rule: Use the existing candidate exit stack/rescue rule from its frozen artifact; otherwise current v28 exits.
- sizing rule: Candidate-specific continuous shrink/penalty sizing from the frozen artifact.
- risk kill rule: Kill or block live testing while not live-ready; insufficient strict-forward evidence.
- live test rule: No live candidate trades. Continue frozen forward collection in separate research artifacts.
- accounting pnl rule: Score via candidate tracker/controlled-live gate against refreshed live_mushroom_v28_size2 live-only baseline after fees.
- iteration rule: Freeze or use own-freeze rows only; diagnostic rows can seed but not promote the policy.
- missing gates: live_ready_false, not_strict_forward, needs_own_frozen_forward_birth

### `dual_lane_overlap_union / top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty050_rank_only`

- entry rule: Existing dual-lane overlap/portfolio entry stack from frozen dual-lane artifacts.
- exit state rule: Use the existing candidate exit stack/rescue rule from its frozen artifact; otherwise current v28 exits.
- sizing rule: Candidate-specific continuous shrink/penalty sizing from the frozen artifact.
- risk kill rule: Kill or block live testing while not live-ready; insufficient strict-forward evidence.
- live test rule: No live candidate trades. Continue frozen forward collection in separate research artifacts.
- accounting pnl rule: Score via candidate tracker/controlled-live gate against refreshed live_mushroom_v28_size2 live-only baseline after fees.
- iteration rule: Freeze or use own-freeze rows only; diagnostic rows can seed but not promote the policy.
- missing gates: live_ready_false, not_strict_forward, needs_own_frozen_forward_birth

### `dual_lane_overlap_union / top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_bridge_cheap_penalty100_rank_only`

- entry rule: Existing dual-lane overlap/portfolio entry stack from frozen dual-lane artifacts.
- exit state rule: Use the existing candidate exit stack/rescue rule from its frozen artifact; otherwise current v28 exits.
- sizing rule: Candidate-specific continuous shrink/penalty sizing from the frozen artifact.
- risk kill rule: Kill or block live testing while not live-ready; insufficient strict-forward evidence.
- live test rule: No live candidate trades. Continue frozen forward collection in separate research artifacts.
- accounting pnl rule: Score via candidate tracker/controlled-live gate against refreshed live_mushroom_v28_size2 live-only baseline after fees.
- iteration rule: Freeze or use own-freeze rows only; diagnostic rows can seed but not promote the policy.
- missing gates: live_ready_false, not_strict_forward, needs_own_frozen_forward_birth

