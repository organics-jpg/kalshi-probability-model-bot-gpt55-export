# Profit Kinetic-Guard Fresh Validation

Generated UTC: `20260504_075239Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- This is a separate forward lock for a guarded kinetic-touch challenger.
- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.

## Locked Kinetic-Guard Candidate

- Policy: `choose=kinetic_touch_score_15; kinetic_touch_score_15>=0.55; 50<=ask<=95; sec>=120; gate=touch_loss15<=0.90`
- Overlay: `kinetic>=0.57 AND adverse15<=50`
- Lock close time: `2026-05-03T02:30:00+00:00`
- Effective entry boundary: `2026-05-03T02:45:00+00:00`
- Lock file: `logs\edge_research\profit_kinetic_guard_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 291/295 | 205/86 | 70.45% | 68.56% | 64.97% | -0.036 | 98.64% | 550.0c | 2.76% | 66.0c |
| fresh after guard lock | 111/111 | 77/34 | 69.37% | 70.21% | 60.27% | -0.099 | 100.00% | -93.0c | -1.19% | 68.0c |

## Read

- Fresh selected 111/111 markets with -93.0c net P&L.
- Keep this separate from kinetic-touch because the guard was selected after seeing the first kinetic loss.
