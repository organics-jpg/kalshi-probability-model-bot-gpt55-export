# RV600 Shadow Smoke Audit

- generated_utc: 2026-05-13T20:18:24+00:00
- research_only: True
- run_label: smoke
- decision: smoke_scored_no_rv600_entries
- collection_ok: True
- offline_v28_context_ok: True
- pipeline_ok: True
- labels_ok: True
- scored_ok: True

## Summary

- root: `logs\particle_research\real_shadow\rv600_next_evidence_shadow_smoke_20260513T193315Z`
- checkpoint_row_count: 115
- context_row_count: 213
- independent_spot_row_count: 545
- merged_context_issue_count: 213
- offline_contexts_written: 115
- offline_context_issues: 0
- pipeline_contexts_written: 115
- pipeline_context_issues: 0
- candidate_rows: 115
- settled_markets: 1
- labels_written: 1
- locked_total_entries: 0
- locked_total_pnl_cents: 0.0
- best_grid_variant: `rv600_primary_single_market_late_70_180_ev0`
- best_grid_accepted_entries: 0
- best_grid_selected_pnl_cents: 0.0
- best_grid_matched_v28_delta_cents: 0.0
- best_grid_rejection: `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive`

## Interpretation

The bounded read-only path is operational and fully scored, but it produced zero accepted RV600 entries. It is pipeline validation, not strategy validation.
