# Profit Kinetic Combo Price-Guard Fresh Validation

Generated UTC: `20260504_075243Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- This is a separate forward lock for a combined kinetic/price/adverse challenger.
- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.

## Locked Kinetic Combo Price-Guard Candidate

- Policy: `choose=kinetic_touch_score_15; kinetic_touch_score_15>=0.55; 50<=ask<=95; sec>=120; gate=touch_loss15<=0.90`
- Overlay: `kinetic>=0.57 AND adverse15<=100 AND ask<=70`
- Lock close time: `2026-05-03T09:45:00+00:00`
- Effective entry boundary: `2026-05-03T09:45:00+00:00`
- Lock file: `logs\edge_research\profit_kinetic_combo_price_guard_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 263/295 | 179/84 | 68.06% | 65.10% | 62.20% | -0.029 | 89.15% | 780.0c | 4.56% | 64.0c |
| fresh after combo lock | 68/83 | 40/28 | 58.82% | 65.54% | 46.96% | -0.186 | 81.93% | -457.0c | -10.25% | 64.0c |

## Read

- Fresh selected 68/83 markets with -457.0c net P&L.
- Keep this separate from other kinetic locks because this guard was selected after prior outcomes.
