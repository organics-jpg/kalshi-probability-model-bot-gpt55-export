# Book Margin Adverse100 Locked Policy Validation

Generated UTC: `20260504_075204Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Reads an existing forward lock and evaluates the current resolved heartbeat ledger.
- Recomputed fresh metrics can drift when Brownian/RV features are refreshed; strict registered rows are the promotion authority.

## Locked Policy

- Name: `book_margin_adverse100`
- Label: `choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; adverse_move_15m<=100`
- Lock close time: `2026-05-04T03:00:00+00:00`
- Effective entry boundary: `2026-05-04T03:00:00+00:00`
- Lock file: `logs\edge_research\profit_frontier_book_margin_adverse100_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 268/295 | 193/75 | 72.01% | 67.68% | 66.36% | -0.013 | 90.85% | 1163.0c | 6.41% | 64.0c |
| recomputed fresh after lock | 11/15 | 6/5 | 54.55% | 68.45% | 28.01% | -0.404 | 73.33% | -153.0c | -20.32% | 64.0c |
| strict registered fresh | 14/15 | 8/6 | 57.14% | 69.07% | 32.59% | -0.365 | 100.00% | -167.0c | -17.27% | 65.0c |

## Recompute Drift Check

- Compared strict and recomputed rows: 11.
- Mismatched rows: 1; missing recomputed rows: 4.
- `KXBTC15M-26MAY040145-45` strict `2026-05-04T05:31:08.227000+00:00 no 66.0c` vs recomputed `2026-05-04T05:30:53.210000+00:00 no 62.0c`.

## Read

- Strict registered fresh sample is not promotion-quality proof.
- Recomputed fresh rows diverge from pre-registered rows; strict registered rows are the promotion authority.
