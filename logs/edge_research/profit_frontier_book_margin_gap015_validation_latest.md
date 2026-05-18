# Book Margin Gap015 Locked Policy Validation

Generated UTC: `20260504_075204Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Reads an existing forward lock and evaluates the current resolved heartbeat ledger.
- Recomputed fresh metrics can drift when Brownian/RV features are refreshed; strict registered rows are the promotion authority.

## Locked Policy

- Name: `book_margin_gap015`
- Label: `choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; abs_book_rv15_gap<=0.15`
- Lock close time: `2026-05-03T23:45:00+00:00`
- Effective entry boundary: `2026-05-04T00:00:00+00:00`
- Lock file: `logs\edge_research\profit_frontier_book_margin_gap015_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 264/295 | 189/75 | 71.59% | 66.79% | 65.87% | -0.009 | 89.49% | 1267.0c | 7.19% | 63.0c |
| recomputed fresh after lock | 24/27 | 16/8 | 66.67% | 67.71% | 46.71% | -0.210 | 88.89% | -25.0c | -1.54% | 63.5c |
| strict registered fresh | 27/28 | 18/9 | 66.67% | 68.30% | 47.82% | -0.205 | 100.00% | -44.0c | -2.39% | 65.0c |

## Recompute Drift Check

- Compared strict and recomputed rows: 23.
- Mismatched rows: 2; missing recomputed rows: 5.
- `KXBTC15M-26MAY032115-15` strict `2026-05-04T01:02:13.838000+00:00 no 81.0c` vs recomputed `2026-05-04T01:01:13.732000+00:00 no 69.0c`.
- `KXBTC15M-26MAY040145-45` strict `2026-05-04T05:31:08.227000+00:00 no 66.0c` vs recomputed `2026-05-04T05:30:53.210000+00:00 no 62.0c`.

## Read

- Strict registered fresh sample is not promotion-quality proof.
- Recomputed fresh rows diverge from pre-registered rows; strict registered rows are the promotion authority.
