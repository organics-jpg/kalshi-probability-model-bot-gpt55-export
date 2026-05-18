# RV600 Locked Plan Forward Audit

- generated_utc: 2026-05-18T13:12:20+00:00
- research_only: True
- decision: locked_plan_forward_incomplete_or_failed
- plan_id: `RV600REV001`
- variant: `rv600_primary_same_side_ev_step_3c_base_70_420_ev2`
- single_market_benchmark_variant: `rv600_primary_single_market_base_70_420_ev2`
- forward_evidence_starts_after_utc: `2026-05-15T07:10:45+00:00`
- root_count: 15
- calendar_day_count: 1
- weekend_day_count: 0

## Primary Summary

- accounting_mode: `position_capped`
- accepted_entries: 32
- distinct_markets: 15
- selected_pnl_cents: -136.0
- matched_v28_delta_cents: -166.0
- avg_pnl_per_entry_cents: -4.25
- positive_root_rate: 0.4
- positive_market_rate: 0.4
- max_single_market_pnl_share: 0.0
- last_window_pnl_cents: 12.0
- rejection_reason: `nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct;no_fill_penalty_nonpositive;does_not_beat_single_market;added_entries_nonpositive;avg_market_not_improved;market_drawdown_worse_than_25pct`

## Single-Market Benchmark

- accounting_mode: `position_capped`
- accepted_entries: 15
- distinct_markets: 15
- selected_pnl_cents: 38.0
- matched_v28_delta_cents: -166.0
- avg_pnl_per_entry_cents: 2.533333333333333
- rejection_reason: `fewer_than_25_entries;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

## Sample Gates

- accepted_entries: False
- distinct_markets: False
- calendar_days: False
- weekend_sessions: False

## Roots

- `rv600_next_evidence_shadow_20260515T071544Z`: candidate_rows_after_start=743; first=2026-05-15T07:16:01.467306+00:00; last=2026-05-15T07:31:00.303316+00:00
- `rv600_next_evidence_shadow_20260515T080148Z`: candidate_rows_after_start=706; first=2026-05-15T08:02:20.070310+00:00; last=2026-05-15T08:17:18.784467+00:00
- `rv600_next_evidence_shadow_20260515T083925Z`: candidate_rows_after_start=761; first=2026-05-15T08:39:43.880562+00:00; last=2026-05-15T08:54:42.271089+00:00
- `rv600_next_evidence_shadow_20260515T091646Z`: candidate_rows_after_start=830; first=2026-05-15T09:17:05.873120+00:00; last=2026-05-15T09:32:04.262851+00:00
- `rv600_next_evidence_shadow_20260515T100014Z`: candidate_rows_after_start=763; first=2026-05-15T10:00:32.078230+00:00; last=2026-05-15T10:15:30.319998+00:00
- `rv600_next_evidence_shadow_20260515T105111Z`: candidate_rows_after_start=665; first=2026-05-15T10:51:26.825077+00:00; last=2026-05-15T11:06:26.076529+00:00
- `rv600_next_evidence_shadow_20260515T113027Z`: candidate_rows_after_start=831; first=2026-05-15T11:30:46.625309+00:00; last=2026-05-15T11:45:44.997235+00:00
- `rv600_next_evidence_shadow_20260515T143222Z`: candidate_rows_after_start=809; first=2026-05-15T14:32:33.925510+00:00; last=2026-05-15T14:47:32.185686+00:00
- `rv600_next_evidence_shadow_20260515T151536Z`: candidate_rows_after_start=818; first=2026-05-15T15:15:53.301348+00:00; last=2026-05-15T15:30:50.675210+00:00
- `rv600_next_evidence_shadow_20260515T160221Z`: candidate_rows_after_start=824; first=2026-05-15T16:02:42.302054+00:00; last=2026-05-15T16:17:40.828232+00:00
- `rv600_next_evidence_shadow_20260515T164836Z`: candidate_rows_after_start=866; first=2026-05-15T16:48:53.069590+00:00; last=2026-05-15T17:03:51.879296+00:00
- `rv600_next_evidence_shadow_20260515T173507Z`: candidate_rows_after_start=849; first=2026-05-15T17:35:48.411937+00:00; last=2026-05-15T17:50:46.712577+00:00
- `rv600_next_evidence_shadow_20260515T182447Z`: candidate_rows_after_start=744; first=2026-05-15T18:25:27.636622+00:00; last=2026-05-15T18:40:27.003202+00:00
- `rv600_next_evidence_shadow_20260515T190705Z`: candidate_rows_after_start=795; first=2026-05-15T19:07:24.488158+00:00; last=2026-05-15T19:22:22.814704+00:00
- `rv600_next_evidence_shadow_20260515T200306Z`: candidate_rows_after_start=853; first=2026-05-15T20:03:22.916288+00:00; last=2026-05-15T20:18:21.965567+00:00
