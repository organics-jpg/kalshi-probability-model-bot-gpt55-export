# v28 Source-Quality Ceiling Audit

Research-only: checks whether current broad candidates can clear source-quality without losing coverage.

- Generated UTC: `2026-05-06T20:39:40.335073+00:00`
- Goal ready: `False`
- Source-quality ceiling active: `True`
- Status: `promising_but_not_promotable`

## Conclusion

- No current observable post-freeze rule simultaneously clears broad coverage, positive net, source quality, sample size, and full-loss cushion. The nearest broad frontier is still below coverage or above the reconstructed-share ceiling, while cleaner approved-only rows are too narrow.

## Findings

### approved_only_is_profitable_but_too_narrow
- Interpretation: The cleanest currently observed source slice wins but cannot reach the 75% coverage target.
- `rule`: `raw05_recross60_abs085_ask65`
- `coverage_pct`: `45.454545`
- `net_cents`: `52.000000`
- `selected_reconstructed_share`: `0.000000`
- `approved_available_share`: `0.312500`
- `available_source_market_counts`: `{'approved_entry': 5, 'reconstructed_or_rejected': 11}`

### best_observable_broad_frontier_still_misses_gates
- Interpretation: The best post-freeze observable frontier is close but still below coverage and just above the reconstructed-share ceiling.
- `rule`: `raw03_recross50_abs50_ask35`
- `coverage_pct`: `72.727273`
- `net_cents`: `107.000000`
- `reconstructed_share`: `0.375000`
- `blockers`: `['settled_lt_30', 'coverage_too_low', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3']`
- `clean_broad_positive_exists`: `False`

### diagnostic_soft_frontier_is_promising_but_unproven
- Interpretation: The soft frontier is the most coherent repair idea, but its strict post-birth sample is basically empty.
- `diagnostic_rule`: `None`
- `diagnostic_coverage_pct`: `None`
- `diagnostic_net_cents`: `None`
- `diagnostic_reconstructed_share`: `None`
- `post_rule`: `None`
- `post_settled`: `None`
- `post_blockers`: `None`

### hybrid_boundary_stack_needs_clean_forward_dilution
- Interpretation: The combined stack can be promising, but current forward evidence is too reconstructed-heavy to trust.
- `post_candidate`: `hybrid_veto_plus_early_no_raw_clean_realized_oracle_uncapped`
- `post_coverage_pct`: `76.470588`
- `post_net_cents`: `130.000000`
- `post_reconstructed_share`: `None`
- `post_clean_rows_needed_for_source_gate`: `19`
- `diagnostic_candidate`: `hybrid_veto_plus_early_no_raw_clean_realized_oracle_uncapped`
- `diagnostic_net_cents`: `1459.000000`
- `diagnostic_clean_rows_needed_for_source_gate`: `18`

## Next

- Keep the soft-frontier and combined-stack monitors running until post-birth rows reach real sample size.
- Do not promote broad candidates while source_quality_ceiling_active is true.
- Treat approved-only profitable rows as calibration hints, not a broad strategy, until they naturally cover more markets.
- Search for observable features that explain why reconstructed-heavy rows differ: cheap ask tails, weak abs-distance, thin edge, and moderate recross are the current suspects.
