# Hazard Fallback Logit55 Fresh Validation

Generated UTC: `20260504_092622Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Takes hazard-mean touch80 when it fires; otherwise falls back to thresholded logit book/RV/hazard.
- The diagnostic row used validation/holdout visibility, so live pre-resolution registry evidence is mandatory before any promotion.

## Locked Candidate

- Primary: `primary=hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; touch_loss15<=0.80`
- Fallback: `fallback=blend_logit_book_rv_hazard_mean; blend>=0.55; fair_edge>=-15c; ask<=95; 60<=sec<=480`
- Lock close time: `2026-05-04T07:30:00+00:00`
- Effective entry boundary: `2026-05-04T07:45:00+00:00`
- Lock file: `logs\edge_research\profit_hazard_fallback_logit55_wait8_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 299/305 | 226/73 | 75.59% | 71.96% | 70.41% | -0.015 | 98.03% | 1084.0c | 5.04% | 69.0c |
| fresh after lock | 6/6 | 4/2 | 66.67% | 69.17% | 30.00% | -0.392 | 100.00% | -15.0c | -3.61% | 68.5c |

## Read

- Fresh selected 6/6 markets with -15.0c net P&L.
- First strict market is determined by the effective boundary, not by the retrospective diagnostic row.
