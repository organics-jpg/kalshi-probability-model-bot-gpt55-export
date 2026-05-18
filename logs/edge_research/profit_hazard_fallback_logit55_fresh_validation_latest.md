# Hazard Fallback Logit55 Fresh Validation

Generated UTC: `20260504_092543Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Takes hazard-mean touch80 when it fires; otherwise falls back to thresholded logit book/RV/hazard.
- The diagnostic row used validation/holdout visibility, so live pre-resolution registry evidence is mandatory before any promotion.

## Locked Candidate

- Primary: `primary=hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; touch_loss15<=0.80`
- Fallback: `fallback=blend_logit_book_rv_hazard_mean; blend>=0.55; fair_edge>=-15c; ask<=95; sec>=60`
- Lock close time: `2026-05-04T06:30:00+00:00`
- Effective entry boundary: `2026-05-04T06:45:00+00:00`
- Lock file: `logs\edge_research\profit_hazard_fallback_logit55_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 302/305 | 224/78 | 74.17% | 70.47% | 68.95% | -0.015 | 99.02% | 1119.0c | 5.26% | 68.0c |
| fresh after lock | 10/10 | 7/3 | 70.00% | 69.90% | 39.68% | -0.302 | 100.00% | 1.0c | 0.14% | 68.5c |

## Read

- Fresh selected 10/10 markets with 1.0c net P&L.
- First strict market is determined by the effective boundary, not by the retrospective diagnostic row.
