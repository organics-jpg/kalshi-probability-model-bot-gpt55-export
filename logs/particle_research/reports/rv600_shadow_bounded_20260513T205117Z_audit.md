# RV600 Shadow Smoke Audit

- generated_utc: 2026-05-13T21:17:00+00:00
- research_only: True
- run_label: bounded_run
- decision: bounded_run_scored_with_entries
- collection_ok: True
- offline_v28_context_ok: True
- pipeline_ok: True
- labels_ok: True
- scored_ok: True

## Summary

- root: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T205117Z`
- checkpoint_row_count: 828
- context_row_count: 213
- independent_spot_row_count: 3490
- merged_context_issue_count: 213
- offline_contexts_written: 826
- offline_context_issues: 2
- pipeline_contexts_written: 817
- pipeline_context_issues: 0
- candidate_rows: 817
- settled_markets: 2
- labels_written: 2
- locked_total_entries: 14
- locked_total_pnl_cents: -126.0
- best_grid_variant: `rv600_primary_single_market_late_70_180_ev20`
- best_grid_accepted_entries: 0
- best_grid_selected_pnl_cents: 0.0
- best_grid_matched_v28_delta_cents: 0.0
- best_grid_rejection: `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive`

## Interpretation

The bounded read-only path is fully scored and produced accepted RV600-style entries. Locked entries=14, locked_pnl_cents=-126.0, best_grid_entries=0; this is still a small fresh-shadow slice and must be judged by the objective completion gates.
