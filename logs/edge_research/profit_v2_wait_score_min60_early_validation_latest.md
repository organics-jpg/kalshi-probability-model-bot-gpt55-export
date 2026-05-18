# V2 Conditional Wait Forward Validation

Generated UTC: `20260504_040638Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Locked rule: take V2 unless the first V2 signal is at least 600 seconds before close, then wait for score_min60.
- This is forward-test evidence only; the discovery scan is not promotion evidence.

## Lock

- Label: `take frontier_v2 unless first v2 seconds_to_close>=600, then wait for score_min60`
- Effective entry boundary: `2026-05-03T22:45:00+00:00`
- Lock file: `logs\edge_research\profit_v2_wait_score_min60_early_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 281/284 | 214/67 | 76.16% | 71.46% | 70.84% | -0.006 | 98.94% | 1320.0c | 6.57% | 68.0c |
| recomputed fresh after lock | 21/21 | 16/5 | 76.19% | 74.14% | 54.91% | -0.192 | 100.00% | 43.0c | 2.76% | 69.0c |
| strict registered fresh | 21/22 | 15/6 | 71.43% | 73.67% | 50.04% | -0.236 | 100.00% | -47.0c | -3.04% | 69.0c |

## Recompute Drift Check

- Compared strict and recomputed rows: 21.
- Mismatched rows: 7; missing recomputed rows: 1.
- `KXBTC15M-26MAY031945-45` strict `2026-05-03T23:32:05.265000+00:00 yes 66.0c` vs recomputed `2026-05-03T23:31:35.210000+00:00 yes 63.0c`.
- `KXBTC15M-26MAY032045-45` strict `2026-05-04T00:34:55.918000+00:00 yes 65.0c` vs recomputed `2026-05-04T00:38:11.191000+00:00 no 78.0c`.
- `KXBTC15M-26MAY032115-15` strict `2026-05-04T01:02:13.838000+00:00 no 81.0c` vs recomputed `2026-05-04T01:01:13.732000+00:00 no 69.0c`.
- `KXBTC15M-26MAY032130-30` strict `2026-05-04T01:17:45.202000+00:00 yes 73.0c` vs recomputed `2026-05-04T01:18:00.227000+00:00 yes 73.0c`.
- `KXBTC15M-26MAY032200-00` strict `2026-05-04T01:49:02.931000+00:00 yes 77.0c` vs recomputed `2026-05-04T01:48:02.822000+00:00 yes 68.0c`.

## Read

- Strict registered fresh sample is not promotion-quality proof.
- Recomputed fresh rows diverge from pre-registered rows; strict registered rows are the promotion authority.
