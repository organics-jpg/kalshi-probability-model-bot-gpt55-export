# Profit Kinetic-Touch Fresh Validation

Generated UTC: `20260504_075224Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- This is a separate forward lock for the refreshed kinetic touch-profit candidate.
- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.

## Locked Kinetic-Touch Candidate

- Policy: `choose=kinetic_touch_score_15; kinetic_touch_score_15>=0.55; 50<=ask<=95; sec>=120; gate=touch_loss15<=0.90`
- Lock close time: `2026-05-03T02:15:00+00:00`
- Effective entry boundary: `2026-05-03T02:30:00+00:00`
- Lock file: `logs\edge_research\profit_kinetic_touch_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 293/295 | 199/94 | 67.92% | 66.93% | 62.37% | -0.046 | 99.32% | 290.0c | 1.48% | 65.0c |
| fresh after kinetic lock | 112/112 | 74/38 | 66.07% | 68.36% | 56.90% | -0.115 | 100.00% | -256.0c | -3.34% | 66.0c |

## Read

- Fresh selected 112/112 markets with -256.0c net P&L.
- Keep this lock separate because the kinetic row was selected after the previous touch-hazard lock had new losses.
