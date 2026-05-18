# Interval Fresh Validation Requirements

Generated UTC: `20260502_184745Z`

## Scope

- Research-only report; no orders are submitted and no bot files are modified.
- Reads locked interval monitor outputs and quantifies post-lock sample-size gaps.
- Wilson lower-bound target is 95% realized accuracy.

## Requirement

- With zero fresh losses, a candidate needs 73 selected fresh wins for a 95% Wilson lower bound at 100% observed accuracy.
- The candidate must also select at least 80% of fresh recurring market intervals.

## Locked Candidate Fresh State

| source | candidate | fresh markets | acc | coverage | Wilson low | extra perfect wins needed |
|---|---|---:|---:|---:|---:|---:|
| `locked_interval_candidates` | `raw_regime_blend_high_price_20260502_1510` | 10/12 | 100.00% | 83.33% | 72.25% | 63 |
| `locked_interval_candidates` | `raw_score_min_book_rv15_existing_lock` | 10/12 | 100.00% | 83.33% | 72.25% | 63 |
| `locked_interval_candidates` | `economical_score_min_book_rv15_20260502_1511` | 10/12 | 90.00% | 83.33% | 59.58% | 100 |
| `locked_interval_candidates` | `staged_score_min_fallback_20260502_1511` | 10/12 | 100.00% | 83.33% | 72.25% | 63 |
| `locked_interval_pure_physics` | `pure_brownian_rv30_adverse15_high_price_20260502_1522` | 10/12 | 100.00% | 83.33% | 72.25% | 63 |
| `locked_interval_pure_physics` | `pure_physics_mean_rv15_rv30_high_price_20260502_1522` | 10/12 | 100.00% | 83.33% | 72.25% | 63 |
| `locked_interval_pure_physics` | `pure_brownian_rv15_spread4_best_high_coverage_20260502_1522` | 10/12 | 100.00% | 83.33% | 72.25% | 63 |
| `locked_interval_pure_physics` | `pure_brownian_rv30_economical_adverse15_20260502_1522` | 10/12 | 90.00% | 83.33% | 59.58% | 100 |
| `locked_interval_logit` | `locked_logit_book_physics_c005_p095_20260502_1512` | 10/12 | 100.00% | 83.33% | 72.25% | 63 |

## Read

- Closest locked candidate still needs 63 additional perfect selected fresh wins for the Wilson gate.
- Current post-lock evidence is monitoring evidence only; it cannot complete the live sample-size requirement.
