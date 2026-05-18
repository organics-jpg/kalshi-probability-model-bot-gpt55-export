# RV600 Shadow Smoke Audit

- generated_utc: 2026-05-15T04:19:36+00:00
- research_only: True
- run_label: bounded_run
- decision: bounded_run_scored_with_entries
- collection_ok: True
- offline_v28_context_ok: True
- pipeline_ok: True
- labels_ok: True
- scored_ok: True

## Summary

- root: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T034820Z`
- checkpoint_row_count: 820
- context_row_count: 0
- independent_spot_row_count: 4784
- merged_context_issue_count: 0
- offline_contexts_written: 818
- offline_context_issues: 2
- pipeline_contexts_written: 789
- pipeline_context_issues: 0
- candidate_rows: 789
- settled_markets: 2
- labels_written: 2
- locked_total_entries: 2
- locked_total_pnl_cents: 27.0
- best_grid_variant: `blend_80_20_max_3_entries_broad_70_600_ev4`
- best_grid_accepted_entries: 3
- best_grid_selected_pnl_cents: 168.0
- best_grid_matched_v28_delta_cents: 0.0
- best_grid_rejection: `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

## Interpretation

The bounded read-only path is fully scored and produced accepted RV600-style entries. Locked entries=2, locked_pnl_cents=27.0, best_grid_entries=3; this is still a small fresh-shadow slice and must be judged by the objective completion gates.
