# Profit Kinetic Path-Confirmation Fresh Validation

Generated UTC: `20260504_075245Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- This is a separate forward lock for a delayed same-side confirmation challenger.
- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.

## Locked Path-Confirmation Candidate

- Policy: `choose=kinetic_touch_score_15; kinetic_touch_score_15>=0.55; 50<=ask<=95; sec>=120; gate=touch_loss15<=0.90`
- Confirmation: `same_side_for>=60s AND confirm_score>=0.6`
- Lock close time: `2026-05-03T04:00:00+00:00`
- Effective entry boundary: `2026-05-03 04:15:00+00:00`
- Lock file: `logs\edge_research\profit_kinetic_path_confirm_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 291/295 | 233/58 | 80.07% | 74.51% | 75.10% | 0.006 | 98.64% | 1619.0c | 7.47% | 73.0c |
| fresh after path-confirm lock | 105/105 | 84/21 | 80.00% | 76.08% | 71.35% | -0.047 | 100.00% | 412.0c | 5.16% | 74.0c |

## Read

- Fresh selected 105/105 markets with 412.0c net P&L.
- Keep this separate from kinetic-touch because the confirmation rule was discovered after the 03:45 UTC path-flip loss.
