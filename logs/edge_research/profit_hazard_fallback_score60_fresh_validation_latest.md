# Hazard Fallback Score60 Fresh Validation

Generated UTC: `20260504_092543Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Takes the earliest eligible row by timestamp: hazard primary or score-min fallback.
- The diagnostic row used validation/holdout visibility, so live pre-resolution registry evidence is mandatory before any promotion.

## Locked Candidate

- Primary: `primary=hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; touch_loss15<=0.80`
- Fallback: `fallback=score_min_book_rv15; score>=0.60; ask<=95; sec>=60`
- Lock close time: `2026-05-04T07:45:00+00:00`
- Effective entry boundary: `2026-05-04T08:00:00+00:00`
- Lock file: `logs\edge_research\profit_hazard_fallback_score60_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 302/305 | 227/75 | 75.17% | 70.96% | 70.00% | -0.010 | 99.02% | 1269.0c | 5.92% | 68.0c |
| fresh after lock | 5/5 | 4/1 | 80.00% | 70.40% | 37.55% | -0.328 | 100.00% | 48.0c | 13.64% | 71.0c |

## Read

- Fresh selected 5/5 markets with 48.0c net P&L.
- First strict market is determined by the effective boundary, not by the retrospective diagnostic row.
