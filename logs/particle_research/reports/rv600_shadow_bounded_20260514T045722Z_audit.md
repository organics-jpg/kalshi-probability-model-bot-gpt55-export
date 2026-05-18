# RV600 Bounded Cumulative Audit

- generated_utc: 2026-05-14T05:18:33+00:00
- research_only: True
- decision: cumulative_bounded_scored_with_entries
- collection_ok: True
- offline_v28_context_ok: True
- pipeline_ok: True
- labels_ok: True
- scored_ok: True

## Summary

- root_count: 1
- candidate_rows: 823
- settled_markets: 2
- locked_total_entries: 24
- locked_total_pnl_cents: 730.0
- best_grid_variant: `blend_95_5_max_3_entries_late_70_300_ev10`
- best_grid_accepted_entries: 3
- best_grid_distinct_markets: 1
- best_grid_selected_pnl_cents: 253.0
- best_grid_matched_v28_delta_cents: 0.0
- best_grid_rejection: `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best_locked_variant: `rv600_primary_max_2_entries_mid_120_420_ev12`
- best_locked_accepted_entries: 4
- best_locked_selected_pnl_cents: 150.0
- best_locked_matched_v28_delta_cents: 0.0
- best_locked_rejection: `fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

## Roots

| root | checkpoints | spot_ticks | offline_contexts | offline_issues | pipeline_contexts | pipeline_issues |
|---|---:|---:|---:|---:|---:|---:|
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T045722Z` | 847 | 3714 | 842 | 5 | 823 | 0 |

## Interpretation

Cumulative bounded read-only evidence has accepted RV600-style entries (locked_pnl_cents=730.0, best_grid_pnl_cents=253.0), but the best row is still gate-rejected: fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct.
