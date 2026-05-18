# Logit Blend Threshold55 Edge15 Fresh Validation

Generated UTC: `20260504_075230Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Forward trial for the logit-pooled book/RV/hazard blend with an explicit physical-probability floor.
- The diagnostic row used validation/holdout visibility, so live pre-resolution registry evidence is mandatory before any promotion.

## Locked Candidate

- Score: `blend_logit_book_rv_hazard_mean`
- Minimum score: `0.55`
- Edge floor: `-15.0c`
- Lock close time: `2026-05-04T06:15:00+00:00`
- Effective entry boundary: `2026-05-04T06:30:00+00:00`
- Lock file: `logs\edge_research\profit_logit_blend_thresh55_edge15_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 292/295 | 217/75 | 74.32% | 70.42% | 69.01% | -0.014 | 98.98% | 1136.0c | 5.52% | 68.0c |
| fresh after lock | 1/1 | 1/0 | 100.00% | 76.00% | 20.65% | -0.553 | 100.00% | 24.0c | 31.58% | 74.0c |

## Read

- Fresh selected 1/1 markets with 24.0c net P&L.
- First strict market is determined by the effective boundary, not by the retrospective diagnostic row.
