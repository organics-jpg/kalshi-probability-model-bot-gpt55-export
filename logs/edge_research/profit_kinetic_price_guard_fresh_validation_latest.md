# Profit Kinetic Price-Guard Fresh Validation

Generated UTC: `20260504_075241Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- This is a separate forward lock for a price/adverse guarded kinetic-touch challenger.
- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.

## Locked Kinetic Price-Guard Candidate

- Policy: `choose=kinetic_touch_score_15; kinetic_touch_score_15>=0.55; 50<=ask<=95; sec>=120; gate=touch_loss15<=0.90`
- Overlay: `adverse15<=100 AND ask<=70`
- Lock close time: `2026-05-03T03:00:00+00:00`
- Effective entry boundary: `2026-05-03T03:00:00+00:00`
- Lock file: `logs\edge_research\profit_kinetic_price_guard_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 268/295 | 179/89 | 66.79% | 64.48% | 60.95% | -0.035 | 90.85% | 619.0c | 3.58% | 63.0c |
| fresh after price-guard lock | 96/110 | 60/36 | 62.50% | 64.75% | 52.51% | -0.122 | 87.27% | -216.0c | -3.47% | 64.0c |

## Read

- Fresh selected 96/110 markets with -216.0c net P&L.
- Keep this separate from other kinetic locks because the guard was discovered after earlier forward outcomes.
