# v28 Successor Market Coverage Loop

Research-only repeated sidecar coverage runner. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T07:13:19Z`
- Loop status: `completed_iterations`
- Collect mode: `public_rest`
- Collection scope: `all_open_closes`
- Iterations run: `1` / `1`
- Target clean rows / markets: `200` / `40`
- Target met: `True`
- Promotion allowed: `False`

## Final Canonical State

- frozen_prediction_rows: `3108`
- frozen_prediction_markets: `87`
- joined_rows: `3018`
- joined_markets: `86`
- clean_forward_rows: `3018`
- clean_forward_markets: `86`
- promotable_candidate_count: `0`
- candidate_gate_count: `9`
- candidate_forward_sample_floor_met: `True`
- best_candidate_id_by_sample_shortfall: `v28s_boundary_monotonic_blend_v001`
- best_candidate_rows: `222`
- best_candidate_markets: `45`
- best_candidate_row_shortfall: `0`
- best_candidate_market_shortfall: `0`
- best_candidate_estimated_additional_markets_needed: `0`
- sample_only_candidate_count: `1`
- best_sample_only_candidate_id: `v28s_late_dsigma_residual_tilt_v001`
- best_sample_only_candidate_rows: `20`
- best_sample_only_candidate_markets: `2`
- best_sample_only_candidate_row_shortfall: `180`
- best_sample_only_candidate_market_shortfall: `38`
- best_sample_only_candidate_estimated_additional_markets_needed: `38`
- source_contract_verdict: `promotion_grade`
- required_forward_hard_blockers: `[]`
- promotion_verdict: `blocked`
- goal_status: `not_complete`

## Iterations

| iteration | cycle status | frozen rows | clean rows | clean markets | best candidate | addl markets needed | candidate floor met | target met |
|---:|---|---:|---:|---:|---|---:|---:|---:|
| 1 | `sidecar_evidence_scored_no_promotable_candidate` | 3108 | 3018 | 86 | `v28s_late_dsigma_residual_tilt_v001` | 38 | True | True |

## Read

- The loop is an evidence collector, not a promotion path.
- Use `--collect-mode public-rest` only when public market capture is intended.
- Use `--all-open-closes` only when intentionally broadening the forward evidence population beyond the nearest close.
- Promotion still requires source contract, market coverage, candidate evidence, and verifier approval.
