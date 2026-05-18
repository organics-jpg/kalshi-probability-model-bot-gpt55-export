# Profit Frontier Fresh Validation

Generated UTC: `20260504_075200Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- The policy is locked on first run and future runs evaluate only recurring markets closing after the lock close time.
- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.

## Locked Policy

- Label: `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.55; ask<=95; sec_to_close>=120; adverse15<=10_or_margin_rv15>=0.5`
- Lock close time: `2026-05-02T20:30:00+00:00`
- Effective entry boundary: `2026-05-02T21:30:00+00:00`
- Lock file: `logs\edge_research\profit_frontier_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 292/295 | 192/100 | 65.75% | 65.57% | 60.14% | -0.054 | 98.98% | 55.0c | 0.29% | 63.0c |
| fresh after lock | 124/125 | 80/44 | 64.52% | 67.44% | 55.77% | -0.117 | 99.20% | -363.0c | -4.34% | 65.0c |

## Read

- Fresh selected 124/125 markets (99.20%) with -363.0c net P&L.
- Fresh sample is not yet a promotion-quality proof.
