# RV600 Bounded Cumulative Audit

- generated_utc: 2026-05-14T03:45:00+00:00
- research_only: True
- decision: cumulative_bounded_pending_settlement_or_scoring
- collection_ok: True
- offline_v28_context_ok: True
- pipeline_ok: True
- labels_ok: False
- scored_ok: True

## Summary

- root_count: 1
- candidate_rows: 812
- settled_markets: 1
- locked_total_entries: 14
- locked_total_pnl_cents: 1167.0
- best_grid_variant: `rv600_primary_max_3_entries_base_70_420_ev2`
- best_grid_accepted_entries: 3
- best_grid_distinct_markets: 1
- best_grid_selected_pnl_cents: 291.0
- best_grid_matched_v28_delta_cents: 585.0
- best_grid_rejection: `fewer_than_25_entries;single_market_share_above_25pct`
- best_locked_variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- best_locked_accepted_entries: 3
- best_locked_selected_pnl_cents: 250.0
- best_locked_matched_v28_delta_cents: 0.0
- best_locked_rejection: `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

## Roots

| root | checkpoints | spot_ticks | offline_contexts | offline_issues | pipeline_contexts | pipeline_issues |
|---|---:|---:|---:|---:|---:|---:|
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T031420Z` | 839 | 6418 | 837 | 2 | 812 | 0 |

## Interpretation

Cumulative bounded evidence is collected, but labels or opportunity scoring are incomplete.
