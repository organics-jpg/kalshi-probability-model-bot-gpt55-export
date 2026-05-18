# Book Margin Locked Policy Validation

Generated UTC: `20260504_075204Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Reads an existing forward lock and evaluates the current resolved heartbeat ledger.
- Recomputed fresh metrics can drift when Brownian/RV features are refreshed; strict registered rows are the promotion authority.

## Locked Policy

- Name: `book_margin`
- Label: `choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0`
- Lock close time: `2026-05-03T22:15:00+00:00`
- Effective entry boundary: `2026-05-03T22:30:00+00:00`
- Lock file: `logs\edge_research\profit_frontier_book_margin_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 293/295 | 208/85 | 70.99% | 67.62% | 65.55% | -0.021 | 99.32% | 988.0c | 4.99% | 64.0c |
| recomputed fresh after lock | 33/33 | 24/9 | 72.73% | 68.73% | 55.78% | -0.129 | 100.00% | 132.0c | 5.82% | 65.0c |
| strict registered fresh | 37/38 | 27/10 | 72.97% | 69.41% | 57.02% | -0.124 | 100.00% | 132.0c | 5.14% | 65.0c |

## Recompute Drift Check

- Compared strict and recomputed rows: 33.
- Mismatched rows: 2; missing recomputed rows: 5.
- `KXBTC15M-26MAY032115-15` strict `2026-05-04T01:02:13.838000+00:00 no 81.0c` vs recomputed `2026-05-04T01:01:13.732000+00:00 no 69.0c`.
- `KXBTC15M-26MAY040145-45` strict `2026-05-04T05:31:08.227000+00:00 no 66.0c` vs recomputed `2026-05-04T05:30:53.210000+00:00 no 62.0c`.

## Read

- Strict registered fresh sample is positive and coverage-valid so far, but strict registered sample size is still required.
- Recomputed fresh rows diverge from pre-registered rows; strict registered rows are the promotion authority.
