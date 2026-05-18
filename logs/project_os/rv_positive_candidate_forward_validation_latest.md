# RV Positive Candidate Forward Validation

- generated_utc: 2026-05-18T18:32:46Z
- research_only: True
- registry_generated_at_utc: 2026-05-18T18:32:31Z
- positive_rv_candidate_count: 2
- overall_decision: `positive_pnl_candidates_remain_blocked_or_underpowered`

Scope: reads registry, locked-plan, and OOS/shadow artifacts only. This report does not change live bot logic, order logic, scorer behavior, thresholds, secrets, live trading state, or the 8501 dashboard.

## Candidate Summary

| Candidate | Family | Registry P&L/7d | Source P&L | Window | Forward/OOS P&L | Entries | Markets | Verdict | Blocking Gates |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `RVTERMLOCK001` | v28_successor | $16826.88 | 17528c (~$175.28) | 1.75h (assumed) | 17528.00c | 4108 | 7 | `blocked_oos_robustness_failed` | beats_current_calibrated_pnl, beats_current_probability, beats_market_probability, positive_ev_rank, positive_top_ev_bucket, all_terminal_oos_gates_passed |
| `RV600NEAR001` | rv600 | $9.31 | 133c (~$1.33) | 1d (exact) | 133.00c | 31 | 24 | `blocked_forward_failed_and_underpowered` | prior_avg_entry_at_least_10c, forward_entries_at_least_target, forward_markets_at_least_target, forward_calendar_days_at_least_target, forward_weekend_sessions_at_least_target, forward_avg_entry_at_least_10c, forward_positive_roots_at_least_60pct, forward_positive_markets_at_least_60pct, forward_concentration_at_most_25pct, forward_repeated_entry_gate_pass, matched_v28_beaten_by_20pct, forward_gate_bundle_clean |

## RVTERMLOCK001

- family: `v28_successor`
- source_path: `logs\particle_research\locked_oos_plans\particle_spot_rv_terminal_oos_RVTERMLOCK001_locked_oos_plan.json`
- validation_source: `logs\particle_research\real_shadow\particle_spot_rv_terminal_oos_RVTERMLOCK001\reports\spot_realized_vol_terminal_oos_locked.json`
- verdict: `blocked_oos_robustness_failed`
- recommendation: Do not promote RVTERMLOCK001; headline P&L is positive, but the linked OOS robustness gates still fail.

| Gate | Status | Value | Threshold | Source |
|---|---|---|---|---|
| `registry_pnl_positive` | `pass` | $16826.88 | > 0 | Research OS registry normalized 7-day metric |
| `locked_oos_scope` | `pass` | True | true | OOS report |
| `enough_candidates` | `pass` | 4512 | >= 1000 | OOS report |
| `enough_markets` | `pass` | 7 | >= 5 | OOS report |
| `enough_selected` | `pass` | 4108 | >= 250 | OOS report |
| `positive_total_pnl` | `pass` | 17528 | > 0c | OOS report |
| `positive_avg_pnl` | `pass` | 4.2668 | >= 0.01c | OOS report |
| `beats_static_particle_pnl` | `pass` | True | true | OOS report |
| `beats_current_calibrated_pnl` | `fail` | False | true | OOS report |
| `beats_current_probability` | `fail` | False | true | OOS report |
| `beats_market_probability` | `fail` | False | true | OOS report |
| `beats_brownian_probability` | `pass` | True | true | OOS report |
| `positive_ev_rank` | `fail` | -0.0299586 | true | OOS report |
| `positive_top_ev_bucket` | `fail` | -3.35638 | > 0c | OOS report |
| `all_terminal_oos_gates_passed` | `fail` | False | true | OOS report |

## RV600NEAR001

- family: `rv600`
- source_path: `logs\particle_research\locked_oos_plans\rv600_breadth_nearmiss_RV600NEAR001_locked_plan.json`
- validation_source: `logs\project_os\rv_positive_candidate_forward_audit_RV600NEAR001.json`
- verdict: `blocked_forward_failed_and_underpowered`
- recommendation: Keep RV600NEAR001 frozen as diagnostic-only; positive P&L is not enough until breadth, matched-v28, concentration, and sample gates clear together.

| Gate | Status | Value | Threshold | Source |
|---|---|---|---|---|
| `registry_pnl_positive` | `pass` | $9.31 | > 0 | Research OS registry normalized 7-day metric |
| `prior_selected_pnl_positive` | `pass` | 339 | > 0c | locked plan prior diagnostic |
| `prior_avg_entry_at_least_10c` | `fail` | 8.26829 | >= 10c | locked plan prior diagnostic |
| `prior_positive_roots_at_least_60pct` | `pass` | 0.636364 | >= 0.60 | locked plan prior diagnostic |
| `prior_positive_markets_at_least_60pct` | `pass` | 0.607143 | >= 0.60 | locked plan prior diagnostic |
| `prior_concentration_at_most_25pct` | `pass` | 0.179941 | <= 0.25 | locked plan prior diagnostic |
| `prior_last_window_positive` | `pass` | 27 | > 0c | locked plan prior diagnostic |
| `forward_audit_available` | `pass` | locked_plan_forward_incomplete_or_failed | report exists | logs\particle_research\locked_oos_plans\rv600_breadth_nearmiss_RV600NEAR001_locked_plan.json |
| `forward_entries_at_least_target` | `fail` | 31 | >= 100 | locked-plan forward audit |
| `forward_markets_at_least_target` | `fail` | 24 | >= 40 | locked-plan forward audit |
| `forward_calendar_days_at_least_target` | `fail` | 1 | >= 10 | locked-plan forward audit |
| `forward_weekend_sessions_at_least_target` | `fail` | 0 | >= 2 | locked-plan forward audit |
| `forward_selected_pnl_positive` | `pass` | 133 | > 0c | locked-plan forward audit |
| `forward_avg_entry_at_least_10c` | `fail` | 4.29032 | >= 10.0c | locked-plan forward audit |
| `forward_positive_roots_at_least_60pct` | `fail` | 0.555556 | >= 0.6 | locked-plan forward audit |
| `forward_positive_markets_at_least_60pct` | `fail` | 0.416667 | >= 0.6 | locked-plan forward audit |
| `forward_concentration_at_most_25pct` | `fail` | 0.526316 | <= 0.25 | locked-plan forward audit |
| `forward_last_window_positive` | `pass` | 40 | > 0c | locked-plan forward audit |
| `forward_no_fill_penalty_positive` | `pass` | 133 | > 0c | locked-plan forward audit |
| `forward_repeated_entry_gate_pass` | `fail` | False | true | locked-plan forward audit |
| `matched_v28_beaten_by_20pct` | `fail` | selected_pnl_cents=133; matched_v28_control_pnl_cents=120; matched_v28_delta_cents=13 | selected >= matched v28 + 20% | locked-plan forward audit |
| `all_required_accounting_modes_present` | `pass` | all_entries, one_per_side_per_market, position_capped | all_entries, one_per_side_per_market, position_capped | locked-plan forward audit |
| `forward_gate_bundle_clean` | `fail` | avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct | no rejection reasons | locked-plan forward audit |
