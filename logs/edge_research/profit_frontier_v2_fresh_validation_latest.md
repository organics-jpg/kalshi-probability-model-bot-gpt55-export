# Profit Frontier V2 Fresh Validation

Generated UTC: `20260504_075202Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- This is a separate v2 lock for the latest high-coverage fee-aware profit frontier.
- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.

## Locked Policy

- Label: `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.55; ask<=95; sec_to_close>=120`
- Lock close time: `2026-05-03T13:30:00+00:00`
- Effective entry boundary: `2026-05-03T13:45:00+00:00`
- Lock file: `logs\edge_research\profit_frontier_v2_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 293/295 | 184/109 | 62.80% | 62.73% | 57.13% | -0.056 | 99.32% | 20.0c | 0.11% | 61.0c |
| fresh after v2 lock | 67/67 | 39/28 | 58.21% | 64.96% | 46.27% | -0.187 | 100.00% | -452.0c | -10.39% | 63.0c |

## Read

- Fresh v2 sample is not yet promotion-quality proof.
