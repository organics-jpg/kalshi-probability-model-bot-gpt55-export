# RV600 Shadow Smoke Audit

- generated_utc: 2026-05-14T00:55:40+00:00
- research_only: True
- run_label: bounded_run
- decision: bounded_run_scored_with_entries
- collection_ok: True
- offline_v28_context_ok: True
- pipeline_ok: True
- labels_ok: True
- scored_ok: True

## Summary

- root: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T002426Z`
- checkpoint_row_count: 820
- context_row_count: 213
- independent_spot_row_count: 4360
- merged_context_issue_count: 213
- offline_contexts_written: 818
- offline_context_issues: 2
- pipeline_contexts_written: 763
- pipeline_context_issues: 0
- candidate_rows: 763
- settled_markets: 2
- labels_written: 2
- locked_total_entries: 5
- locked_total_pnl_cents: -145.0
- best_grid_variant: `blend_95_5_max_3_entries_broad_70_600_ev2`
- best_grid_accepted_entries: 6
- best_grid_selected_pnl_cents: 164.0
- best_grid_matched_v28_delta_cents: 0.0
- best_grid_rejection: `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

## Interpretation

The bounded read-only path is fully scored and produced accepted RV600-style entries. Locked entries=5, locked_pnl_cents=-145.0, best_grid_entries=6; this is still a small fresh-shadow slice and must be judged by the objective completion gates.
