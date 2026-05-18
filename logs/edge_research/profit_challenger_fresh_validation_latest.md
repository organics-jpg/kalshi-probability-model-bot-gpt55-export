# Profit Challenger Fresh Validation

Generated UTC: `20260504_075217Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- This is a separate forward lock for the blocker-overlay challenger, not a mutation of the original profit lock.
- P&L is one-contract held-to-settlement net after the local entry-only Kalshi taker fee estimate.

## Locked Challenger

- Base policy: `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.55; ask<=95; sec_to_close>=120; adverse15<=10_or_margin_rv15>=0.5`
- Overlay: `ask>=50 AND ask<=80`
- Lock close time: `2026-05-02T21:15:00+00:00`
- Effective entry boundary: `2026-05-02T21:45:00+00:00`
- Lock file: `logs\edge_research\profit_challenger_fresh_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 280/295 | 186/94 | 66.43% | 65.71% | 60.71% | -0.050 | 94.92% | 202.0c | 1.10% | 63.0c |
| fresh after challenger lock | 114/124 | 71/43 | 62.28% | 66.81% | 53.12% | -0.137 | 91.94% | -516.0c | -6.78% | 65.0c |

## Read

- Fresh selected 114/124 markets with -516.0c net P&L.
- Keep this lock separate from the original EV lock so forward evidence remains interpretable.
