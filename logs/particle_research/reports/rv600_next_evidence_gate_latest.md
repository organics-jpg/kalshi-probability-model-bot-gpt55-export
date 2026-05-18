# RV600 Next Evidence Gate

- generated_utc: 2026-05-18T13:13:49+00:00
- research_only: True
- decision: not_ready_collect_new_shadow_evidence
- ready_for_bounded_shadow_collection: False

## Checklist

| status | requirement | evidence | next action |
|---|---|---|---|
| pass | RV600 plan exists | `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\docs\research\RV600_VARIATION_TEST_PLAN.md` | Keep new evidence tied to this plan or document a new plan revision before scoring. |
| pass | Current sample is exhausted or supported revision is frozen before new collection | `failure_decision=no_current_plan_revision_supported; support_row_count=0; locked_plan=logs\particle_research\locked_oos_plans\rv600_revision_RV600REV001_locked_plan.json; plan_id=RV600REV001; plan_generated_utc=2026-05-15T07:10:45Z; revision_frozen=False` | Collect materially new shadow evidence only after unsupported samples are exhausted or a supported revision is pre-registered. |
| pass | Objective is not already complete | `objective_decision=blocked_not_complete; blocked_by=['current_locked_family_rejected', 'no_existing_plan_family_viable', 'forward_shadow_pnl_negative', 'forward_shadow_sample_incomplete', 'meta_label_rescue_failed', 'probability_calibration_rescue_failed', 'conformal_abstention_rescue_failed', 'online_expert_rescue_failed', 'no_current_plan_revision_supported', 'fresh_shadow_smoke_insufficient', 'fresh_bounded_shadow_insufficient', 'cumulative_bounded_shadow_insufficient', 'market_balance_rescue_failed', 'regime_filter_rescue_failed', 'group_dro_rescue_failed', 'pbo_stability_rejected', 'reality_check_rejected', 'spa_benchmark_rejected', 'stability_selection_rescue_failed', 'parameter_plateau_rejected', 'locked_plan_forward_audit_failed']` | Leave the goal active until fresh shadow evidence meets all gates. |
| pass | Bounded passive collector exists | `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\research_particle\paired_passive_shadow_run.py` | Use the bounded paired collector; do not restart or modify live v28. |
| pass | Native passive websocket recorder exists | `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\research_native_passive_ws_recorder.py` | Recorder is passive and tagged `passive_no_order_submission` in metadata. |
| pass | Matched v28 control can be rebuilt offline and causally | `offline_tool=C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\probe_rv600_native_offline_v28_contexts.py; engine=C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\btc_mushroom_forecaster_v28_fast.py; input=passive checkpoints + independent Coinbase spot ticks` | Use `--offline-v28-control`; do not depend on sparse live v28 policy telemetry. |
| pass | Local `.env` is available for read-only API credentials | `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\.env` | Use existing credentials only for passive market data; do not place orders. |
| fail | A BTC15M market is inside the bounded collection window | `next_market=KXBTC15M-26MAY180915-15; status=active; close_time=2026-05-18T13:15:00+00:00; seconds_to_close=70.5; run_seconds=900.0` | Wait for the BTC15M market window; recommended_start_utc=2026-05-18T13:13:49+00:00 |

## Market Window

- enabled: True
- ready: False
- evidence: `next_market=KXBTC15M-26MAY180915-15; status=active; close_time=2026-05-18T13:15:00+00:00; seconds_to_close=70.5; run_seconds=900.0`
- next_action: Wait for the BTC15M market window; recommended_start_utc=2026-05-18T13:13:49+00:00

## Optional Live V28 Source

- path: `C:\Users\organ\Desktop\kalshi 90 +v28\logs\v28_90_touch_backtest_exact_size2_live\execution_events.ndjson`
- mtime_utc: `2026-05-16T17:45:06.281929+00:00`
- age_seconds: `156522.718071`
- compatible_tail_rows: `354`
- schema_counts: `{'v28_90_touch_policy_eval': 354}`

## Matched V28 Control

- mode: `offline_v28_public_btc_replay`
- tool: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\probe_rv600_native_offline_v28_contexts.py`
- engine: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\btc_mushroom_forecaster_v28_fast.py`
- research_only: `True`
- causal_replay: `True`

## Active Locked Plan

- path: `logs\particle_research\locked_oos_plans\rv600_revision_RV600REV001_locked_plan.json`
- plan_id: `RV600REV001`
- variant: `rv600_primary_same_side_ev_step_3c_base_70_420_ev2`
- generated_utc: `2026-05-15T07:10:45Z`
- forward_evidence_starts_after_utc: `2026-05-15T07:10:45Z`
- revision_frozen: `False`

## Commands

Bounded passive collection:

```powershell
python -m research_particle.paired_passive_shadow_run --dataset rv600_next_evidence_shadow_20260518T131349Z --artifact-root "logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260518T131349Z" --run-seconds 900 --record-independent-spot --independent-spot-feed coinbase --require-independent-spot --offline-v28-control --strategy-tag rv600_research_shadow_readonly --bot-tag rv600_research_shadow_readonly
```

Post-collection pipeline:

Use the `pipeline_command` printed by paired_passive_shadow_run; in offline-v28 mode it will point at `offline_v28_contexts.ndjson` inside the generated artifact root. then refresh labels with `python probe_rv600_forward_shadow_refresh.py --write`, score with `python probe_rv600_native_forward_opportunity.py --write`, and rerun `python probe_rv600_objective_state_audit.py --write`.

## Guardrails

- Research-only: no live trades.
- Do not change live v28 order logic.
- Do not restart the live bot.
- Require independent spot for merged context rows so stale/missing spot cannot silently pass through.
- Build the matched v28/current control by causal offline v28 replay from public BTC data and captured independent spot.
- Live 90-touch v28 policy-eval telemetry is optional diagnostic evidence, not a collection blocker.
- Any future candidate must be frozen before counting fresh forward-shadow evidence.
- Do not call update_goal until the objective audit is green against fresh evidence.

## Minimum Completion Sample

- accepted_entries: 100
- distinct_markets: 40
- calendar_days: 10
- weekend_sessions: 2
- matched_v28_edge_min_percent: 20
