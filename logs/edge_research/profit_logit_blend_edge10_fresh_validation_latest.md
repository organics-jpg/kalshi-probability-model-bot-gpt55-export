# Logit Blend Edge10 Fresh Validation

Generated UTC: `20260504_075228Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Forward trial for the diagnostic logit-pooled book/RV/hazard fair-value blend.
- The diagnostic row used validation/holdout visibility, so live pre-resolution registry evidence is mandatory before any promotion.

## Locked Candidate

- Score: `blend_logit_book_rv_hazard_mean`
- Edge floor: `-10.0c`
- Lock close time: `2026-05-04T05:45:00+00:00`
- Effective entry boundary: `2026-05-04T06:00:00+00:00`
- Lock file: `logs\edge_research\profit_logit_blend_edge10_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 293/295 | 182/111 | 62.12% | 61.61% | 56.44% | -0.052 | 99.32% | 149.0c | 0.83% | 57.0c |
| fresh after lock | 3/3 | 2/1 | 66.67% | 58.00% | 20.77% | -0.372 | 100.00% | 26.0c | 14.94% | 48.0c |

## Read

- Fresh selected 3/3 markets with 26.0c net P&L.
- First strict market is determined by the effective boundary, not by the retrospective diagnostic row.
