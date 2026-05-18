# Profit Touch-Hazard Overlay Fresh Validation

Generated UTC: `20260504_075222Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- This is a separate forward lock for a touch-hazard blocker-overlay challenger.
- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.

## Locked Overlay Candidate

- Policy: `choose=book_touch_blend_15; book_touch_blend_15>=0.35; 0<=ask<=80; sec>=120; gate=none`
- Overlay: `ask>=50 AND touch_loss15>=0.80`
- Lock close time: `2026-05-03T00:00:00+00:00`
- Effective entry boundary: `2026-05-03T00:15:00+00:00`
- Lock file: `logs\edge_research\profit_touch_hazard_overlay_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 282/295 | 170/112 | 60.28% | 59.39% | 54.47% | -0.049 | 95.59% | 251.0c | 1.50% | 56.0c |
| fresh after overlay lock | 108/114 | 61/47 | 56.48% | 59.77% | 47.07% | -0.127 | 94.74% | -355.0c | -5.50% | 57.0c |

## Read

- Fresh selected 108/114 markets with -355.0c net P&L.
- Keep this separate from the base touch-hazard lock because the overlay was selected after seeing earlier fresh rows.
