# v28 Sequential Live Candidate Selector

Operator-facing selector. It does not place orders or change live logic.

- Generated UTC: `2026-05-08T02:58:42.392399+00:00`
- Decision: `active_hybridfpt_trial_stopped_needs_next_candidate`
- Candidate rows ranked: `994`
- Live baseline: `1361.0c`
- Full-policy live-test allowed count: `0`
- Sidecar ready count: `0`
- Readiness any_live_ready: `False`

## Family Decisions

### top_component_parent_fill_repair_child

- Decision: `reject_immediate_live_test`
- Gate/policy: `top_component_parent_fill_repair_child` / `diagnostic_observable_mid_confidence_parent_fill_quarter`
- Settled/net/win-rate: `76` / `2233.0c` / `0.881578947368421`
- Blockers: `diagnostic_prefreeze, source_gate_zero_row_margin`

Why:
- raw PnL/win-rate leader is diagnostic/prefreeze, not strict-forward
- strict post-birth row does not beat refreshed live baseline
- exit-clock rescue mechanism is not forward-proven in this branch
- strict losses point to source-quality and FV/entry false positives

Minimum blocker to clear:

- `strict_rows_needed_for_30`: `9`
- `net_cents_needed_for_cushion3`: `106.0`
- `net_cents_needed_to_beat_live`: `1168.0`
- `promotion_gate_pass_count`: `0`
- `strict_unique_rows`: `27`
- `strict_net_cents`: `-16.0`

### dual_lane_overlap_union

- Decision: `reject_immediate_live_test`
- Gate/policy: `dual_lane_overlap_union` / `top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_entry_cheap_penalty025_rank_only`
- Settled/net/win-rate: `83` / `1842.5c` / `0.8192771084337349`
- Blockers: `needs_own_frozen_forward_birth, live_ready_false`

Why:
- fresh dual-lane handoff decision is no_live_test
- same-window strict candidate trails live v28
- own-freeze/overlay/parent-shrink gates are still immature

Minimum blocker to clear:

- `handoff_decision_excerpt`: `['- Decision: `no_live_test`', '- Candidate minus live on same markets: `-353c ($-3.53)`', '## Blocked Checks']`
- `required`: `needs own-freeze strict sample, positive same-window live edge, and overlay/parent-shrink forward samples`

### approved_entry_book_raw_blend_fv

- Decision: `defer_as_calibration_overlay_not_entry_policy`
- Gate/policy: `approved_entry_book_raw_blend_fv` / `book_raw_blend_alpha_0p50`
- Settled/net/win-rate: `55` / `362.0c` / `0.8545454545454545`
- Blockers: `none`

Why:
- frozen report keeps entry selection fixed and changes only FV probability calibration
- sidecar watch marks it not ready because source is unknown and it does not beat the refreshed live baseline
- using the blend as a live entry gate would be a code/logic conversion not directly validated by its current PnL row

Minimum blocker to clear:

- `live_readiness_any_live_ready`: `False`
- `book_blend_live_ready_line`: `- Candidate live ready: `True``
- `operator_requirement`: `define and score a versioned full policy using the blend for sizing/exit/FV, or pre-register a code-level entry conversion before any switch`

### active_sourcefix_hybrid_fpt_ask35_btcrest_exitdelay90_size1

- Decision: `continue_active_controlled_trial`
- Gate/policy: `hybrid_fpt_depth_gate` / `hybrid_fpt_depth_gate raw03_recross60_abs85_ask35 + Coinbase REST BTC freshness fallback + 90s post-fill v28 exit delay + common-clock exit guard`
- Settled/net/win-rate: `None` / `n/a` / `None`
- Blockers: `none`

Why:
- it is already the only live controlled v28-derived candidate process
- it has 1 scored entry and 1 scored round trip; current net after fees is $-0.26
- exchange status is flat with no resting orders
- sourcefix repaired BTC websocket staleness without opening exposure
- the trial is not profitable evidence yet, but it has not hit a kill rule
- this version maps back to the existing raw03_recross60_abs85_ask35 forward frontier after coverage review showed the extra abs-d ceiling reduced row count
- this is the versioned exit-state repair after live evidence showed a 34s probability-collapse exit sold at 42c before the market recovered and finalized YES
- this trial is stopped rather than actively collecting; status=, running=False

Minimum blocker to clear:

- `needed`: `recover from negative exchange-reconciled live PnL and build a meaningful positive after-fee sample`
- `do_not_change`: `do not lower p floors or widen thresholds solely to create coverage`

## Active Live Trial

- Strategy: `mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_ask35_btcrest_exitdelay90_size1_live`
- Log source: `live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_ask35_btcrest_exitdelay90_size1`
- Decision: `continue_active_controlled_trial`
- Score: `{'entries_total': 1, 'completed_round_trips': 1, 'net_pnl_total_dollars': -0.26, 'open_positions': 0}`
- Zero-entry decision: `entry_path_active_rescore_and_reconcile`
- Zero-entry totals: `{'approved': 10, 'edge_price_true_p_false_rows': 0, 'events': 30, 'filled': 7, 'markets': 1, 'mature_markets': 0, 'order_like': 4, 'otherwise_approved_balance': 0, 'otherwise_approved_book_stale': 0, 'otherwise_approved_btc_stale': 0, 'p_true_edge_or_price_false_rows': 0}`
- Zero-entry decision counts: `{'entry_or_order_seen': 1}`
- No-entry review due / markets until review: `False` / `8`
- Operator rule: Do not switch while this flat, healthy size-1 trial is collecting unless a higher-ranked candidate becomes launchable or the active trial hits a kill rule.

Status excerpts:
- - Status: `not_running_lock_missing_or_other_strategy`
- - Lock/process: `False` / `False`
- - Latest event: `exit_reconciled` / `mushroom_v28_probability_collapse_full_single_shot_visible_depth` at `2026-05-08T02:54:46.411495+00:00`
- - Approved/order starts/order successes: `3` / `2` / `2`
- - Zero-fill attempts/events / filled events: `0` / `0` / `4`
- - Events/rejected/approved/order-like: `30` / `6` / `10` / `4`
- - Latest-market decision: `reconcile_order_like_events`
- - Latest-market source stale: `2/6` (33.3%)
- - Max p_side / net edge: `0.891933` / `34.193313`

## Next Action

Do not relaunch the stopped hybrid-FPT ask35 BTC-REST lane without a new blocker-specific version. The stopped trial status is  with net $-0.26; select the next existing v28-derived candidate or a formally versioned repair.
