# Score Min60 Gap020 Locked Policy Validation

Generated UTC: `20260504_075204Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Reads an existing forward lock and evaluates the current resolved heartbeat ledger.
- Recomputed fresh metrics can drift when Brownian/RV features are refreshed; strict registered rows are the promotion authority.

## Locked Policy

- Name: `score_min60_gap020`
- Label: `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120; abs_book_rv15_gap<=0.20`
- Lock close time: `2026-05-04T01:15:00+00:00`
- Effective entry boundary: `2026-05-04T01:15:00+00:00`
- Lock file: `logs\edge_research\profit_frontier_score_min60_gap020_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 290/295 | 221/69 | 76.21% | 71.40% | 70.98% | -0.004 | 98.31% | 1394.0c | 6.73% | 68.0c |
| recomputed fresh after lock | 22/22 | 15/7 | 68.18% | 73.45% | 47.32% | -0.261 | 100.00% | -116.0c | -7.18% | 69.0c |
| strict registered fresh | 26/27 | 18/8 | 69.23% | 72.42% | 50.01% | -0.224 | 100.00% | -83.0c | -4.41% | 69.0c |

## Recompute Drift Check

- Compared strict and recomputed rows: 22.
- Mismatched rows: 7; missing recomputed rows: 5.
- `KXBTC15M-26MAY032130-30` strict `2026-05-04T01:17:45.202000+00:00 yes 73.0c` vs recomputed `2026-05-04T01:18:00.227000+00:00 yes 73.0c`.
- `KXBTC15M-26MAY032200-00` strict `2026-05-04T01:49:02.931000+00:00 yes 77.0c` vs recomputed `2026-05-04T01:48:02.822000+00:00 yes 68.0c`.
- `KXBTC15M-26MAY032230-30` strict `2026-05-04T02:18:05.671000+00:00 no 66.0c` vs recomputed `2026-05-04T02:17:05.641000+00:00 no 79.0c`.
- `KXBTC15M-26MAY032330-30` strict `2026-05-04T03:18:11.263000+00:00 no 61.0c` vs recomputed `2026-05-04T03:19:11.329000+00:00 no 69.0c`.
- `KXBTC15M-26MAY040130-30` strict `2026-05-04T05:19:06.925000+00:00 no 62.0c` vs recomputed `2026-05-04T05:17:06.838000+00:00 no 66.0c`.

## Read

- Strict registered fresh sample is not promotion-quality proof.
- Recomputed fresh rows diverge from pre-registered rows; strict registered rows are the promotion authority.
