# Candidate Readiness Reevaluation

Generated UTC: 2026-05-18T20:13:20Z

Scope: research-only same-rubric reevaluation of every current Research OS candidate node. This file does not authorize live orders.

## Summary

- Candidate nodes evaluated: 37
- Controlled live-test ready: 0
- Live-shadow ready: 2
- Live-order ready: 0

## Rubric

- Forward-shadow evidence is acceptable for controlled live-test review; live_stats are not required at this stage.
- A controlled sample can pass with either 20 markets and 100 rows or 12 markets and 20 entries.
- Positive 7d P&L is used as a ranking rate, while source-window P&L, baseline comparison, source quality, and blockers decide readiness.
- Live-order readiness remains a separate explicit gate and is never inferred by this report.

## Candidate Results

| readiness | score | candidate | family | next action |
|---|---:|---|---|---|
| live_shadow_ready | 88.0 | `v28s_live_pnl_midband_no_fade_yes_v019` | `v28_successor` | Level 1 bootstrap is complete; continue post-hash no-order collection until Level 2 controlled-live-test criteria are explicitly met. |
| live_shadow_ready | 83.0 | `CONSENSUSLOCK001` | `v28_successor` | Continue no-order live-forward collection and resolve remaining readiness blockers before controlled live testing. |
| near_miss_review | 60.0 | `v28s_late_dsigma_residual_tilt_v001 / logged_events_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 60.0 | `v28s_late_dsigma_residual_tilt_v001 / seed_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 55.0 | `v28s_boundary_monotonic_time_safe_v001 / logged_events_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `RV600NEAR001` | `rv600` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `PSLICELOCK001` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `PSLICELOCK002` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `PSLICELOCK003` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `v28s_boundary_monotonic_blend_v001 / logged_events_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `v28s_boundary_monotonic_blend_v001 / seed_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `v28s_boundary_monotonic_light_v001 / logged_events_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `v28s_boundary_monotonic_light_v001 / seed_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `v28s_boundary_monotonic_micro_time_safe_v001 / logged_events_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `v28s_boundary_monotonic_micro_time_safe_v001 / seed_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `v28s_boundary_monotonic_time_safe_v001 / seed_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `v28s_logistic_book_reliability_diag_v001 / logged_events_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `v28s_logistic_boundary_physics_v001 / logged_events_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `v28s_logistic_boundary_physics_v001 / seed_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `v28s_monotonic_tabular_v001 / logged_events_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 50.0 | `v28s_monotonic_tabular_v001 / seed_diagnostic` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 43.0 | `dynamic_particle600_next_locked_plan` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 43.0 | `dynamic_particle_next_locked_plan` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 43.0 | `GAUSS45LOCK002` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 43.0 | `RVTERMLOCK001` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| near_miss_review | 35.0 | `GAUSS45LOCK001` | `v28_successor` | Keep under review, but fix the named sample, baseline, or source blocker before live-test review. |
| blocked_nonpositive | 28.0 | `side_safety_oos_next_locked_plan` | `v28_successor` | Do not repeat as-is; redesign the mechanism before collecting more evidence. |
| baseline_control_only | 10.0 | `v28_raw / logged_events_diagnostic` | `v28_successor` | Keep as a baseline/control row only; do not advance as a live-test candidate. |
| baseline_control_only | 10.0 | `v28_raw / seed_diagnostic` | `v28_successor` | Keep as a baseline/control row only; do not advance as a live-test candidate. |
| blocked_nonpositive | 0.0 | `RESIDLOCK001` | `rv600` | Do not repeat as-is; redesign the mechanism before collecting more evidence. |
| blocked_nonpositive | 0.0 | `RV600REV001` | `rv600` | Do not repeat as-is; redesign the mechanism before collecting more evidence. |
| blocked_nonpositive | 0.0 | `GAUSS45LOCK003` | `v28_successor` | Do not repeat as-is; redesign the mechanism before collecting more evidence. |
| blocked_nonpositive | 0.0 | `PSLICELOCK004` | `v28_successor` | Do not repeat as-is; redesign the mechanism before collecting more evidence. |
| blocked_nonpositive | 0.0 | `PSLICELOCK005` | `v28_successor` | Do not repeat as-is; redesign the mechanism before collecting more evidence. |
| blocked_nonpositive | 0.0 | `v28s_logistic_book_reliability_diag_v001 / seed_diagnostic` | `v28_successor` | Do not repeat as-is; redesign the mechanism before collecting more evidence. |
| blocked_nonpositive | 0.0 | `v28s_logistic_calibration_v001 / logged_events_diagnostic` | `v28_successor` | Do not repeat as-is; redesign the mechanism before collecting more evidence. |
| blocked_nonpositive | 0.0 | `v28s_logistic_calibration_v001 / seed_diagnostic` | `v28_successor` | Do not repeat as-is; redesign the mechanism before collecting more evidence. |

## Research Guardrail

Live-order readiness is always false in this report unless a separate explicit live-order gate is implemented and approved.
