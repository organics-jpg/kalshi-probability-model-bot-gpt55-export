# Book Margin Early Locked Policy Validation

Generated UTC: `20260504_075204Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Reads an existing forward lock and evaluates the current resolved heartbeat ledger.
- Recomputed fresh metrics can drift when Brownian/RV features are refreshed; strict registered rows are the promotion authority.

## Locked Policy

- Name: `book_margin_early`
- Label: `choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=480; margin_rv15>=0`
- Lock close time: `2026-05-03T23:15:00+00:00`
- Effective entry boundary: `2026-05-03T23:30:00+00:00`
- Lock file: `logs\edge_research\profit_frontier_book_margin_early_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 285/295 | 203/82 | 71.23% | 67.66% | 65.72% | -0.019 | 96.61% | 1018.0c | 5.28% | 64.0c |
| recomputed fresh after lock | 29/29 | 21/8 | 72.41% | 68.90% | 54.28% | -0.146 | 100.00% | 102.0c | 5.11% | 65.0c |
| strict registered fresh | 33/34 | 24/9 | 72.73% | 69.64% | 55.78% | -0.139 | 100.00% | 102.0c | 4.44% | 65.0c |

## Recompute Drift Check

- Compared strict and recomputed rows: 29.
- Mismatched rows: 2; missing recomputed rows: 5.
- `KXBTC15M-26MAY032115-15` strict `2026-05-04T01:02:13.838000+00:00 no 81.0c` vs recomputed `2026-05-04T01:01:13.732000+00:00 no 69.0c`.
- `KXBTC15M-26MAY040145-45` strict `2026-05-04T05:31:08.227000+00:00 no 66.0c` vs recomputed `2026-05-04T05:30:53.210000+00:00 no 62.0c`.

## Read

- Strict registered fresh sample is positive and coverage-valid so far, but strict registered sample size is still required.
- Recomputed fresh rows diverge from pre-registered rows; strict registered rows are the promotion authority.
