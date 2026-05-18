# Hazard-Mean Touch80 Fresh Validation

Generated UTC: `20260504_092543Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Freezes the refreshed first-passage/touch-hazard candidate as its own forward trial.
- Promotion still requires strict pre-resolution live sample size and >=75-80% recurring-market coverage.

## Locked Candidate

- Policy: `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=touch_loss15<=0.80`
- Lock close time: `2026-05-04T05:30:00+00:00`
- Effective entry boundary: `2026-05-04T05:45:00+00:00`
- Lock file: `logs\edge_research\profit_hazard_mean_touch80_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 290/305 | 218/72 | 75.17% | 71.68% | 69.89% | -0.018 | 95.08% | 1012.0c | 4.87% | 69.0c |
| fresh after lock | 14/14 | 12/2 | 85.71% | 71.36% | 60.06% | -0.113 | 100.00% | 201.0c | 20.12% | 70.0c |

## Read

- Fresh selected 14/14 markets with 201.0c net P&L.
- This lock was created after the 05:30 UTC settlement, so the first strict market is the 06:00 UTC cycle.
