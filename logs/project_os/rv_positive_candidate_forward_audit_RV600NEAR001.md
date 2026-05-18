# RV600 Locked Plan Forward Audit

- generated_utc: 2026-05-18T13:12:29+00:00
- research_only: True
- decision: locked_plan_forward_incomplete_or_failed
- plan_id: `RV600NEAR001`
- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- single_market_benchmark_variant: `rv600_primary_single_market_broad_70_600_ev4`
- forward_evidence_starts_after_utc: `2026-05-15T04:53:47+00:00`
- root_count: 18
- calendar_day_count: 1
- weekend_day_count: 0

## Primary Summary

- accounting_mode: `position_capped`
- accepted_entries: 31
- distinct_markets: 24
- selected_pnl_cents: 133.0
- matched_v28_delta_cents: 13.0
- avg_pnl_per_entry_cents: 4.290322580645161
- positive_root_rate: 0.5555555555555556
- positive_market_rate: 0.4166666666666667
- max_single_market_pnl_share: 0.5263157894736842
- last_window_pnl_cents: 40.0
- rejection_reason: `avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

## Single-Market Benchmark

- accounting_mode: `position_capped`
- accepted_entries: 24
- distinct_markets: 24
- selected_pnl_cents: 17.0
- matched_v28_delta_cents: -37.0
- avg_pnl_per_entry_cents: 0.7083333333333334
- rejection_reason: `fewer_than_25_entries;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

## Sample Gates

- accepted_entries: False
- distinct_markets: False
- calendar_days: False
- weekend_sessions: False

## Roots

- `rv600_next_evidence_shadow_20260515T045448Z`: candidate_rows_after_start=751; first=2026-05-15T04:55:02.429197+00:00; last=2026-05-15T05:10:00.938080+00:00
- `rv600_next_evidence_shadow_20260515T053557Z`: candidate_rows_after_start=719; first=2026-05-15T05:36:15.984489+00:00; last=2026-05-15T05:51:14.680728+00:00
- `rv600_next_evidence_shadow_20260515T063046Z`: candidate_rows_after_start=783; first=2026-05-15T06:31:13.179746+00:00; last=2026-05-15T06:46:12.199749+00:00
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
