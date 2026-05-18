# Profit Touch-Hazard Fresh Validation

Generated UTC: `20260504_075220Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- This is a separate forward lock for the first-passage/touch-hazard profit candidate.
- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.

## Locked Touch-Hazard Candidate

- Policy: `choose=book_touch_blend_15; book_touch_blend_15>=0.35; 0<=ask<=80; sec>=120; gate=none`
- Lock close time: `2026-05-02T22:00:00+00:00`
- Effective entry boundary: `2026-05-02T22:30:00+00:00`
- Lock file: `logs\edge_research\profit_touch_hazard_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 292/295 | 173/119 | 59.25% | 59.23% | 53.53% | -0.057 | 98.98% | 5.0c | 0.03% | 56.0c |
| fresh after touch lock | 119/121 | 66/53 | 55.46% | 59.72% | 46.50% | -0.132 | 98.35% | -507.0c | -7.13% | 56.0c |

## Read

- Fresh selected 119/121 markets with -507.0c net P&L.
- Keep this lock separate so the new physics prior can be falsified forward without retuning.
