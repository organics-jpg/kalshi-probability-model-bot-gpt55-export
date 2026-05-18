# V2 Rich Conditional Wait Forward Validation

Generated UTC: `20260504_040654Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Locked rule: take V2 unless the first V2 signal is early and Brownian RV15 confidence is <=70%, then wait for score_min60.
- This is forward-test evidence only; the discovery scan is not promotion evidence.

## Lock

- Label: `take frontier_v2 unless first v2 seconds_to_close>=600 and brownian_p_rv_15m<=0.70, then wait for score_min60`
- Effective entry boundary: `2026-05-03T23:45:00+00:00`
- Lock file: `logs\edge_research\profit_v2_wait_score_min60_brownian70_early_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 281/284 | 214/67 | 76.16% | 71.20% | 70.84% | -0.004 | 98.94% | 1393.0c | 6.96% | 68.0c |
| recomputed fresh after lock | 17/17 | 14/3 | 82.35% | 75.71% | 58.97% | -0.167 | 100.00% | 113.0c | 8.78% | 72.0c |
| strict registered fresh | 17/18 | 13/4 | 76.47% | 74.94% | 52.74% | -0.222 | 100.00% | 26.0c | 2.04% | 72.0c |

## Recompute Drift Check

- Compared strict and recomputed rows: 17.
- Mismatched rows: 6; missing recomputed rows: 1.
- `KXBTC15M-26MAY032045-45` strict `2026-05-04T00:34:55.918000+00:00 yes 65.0c` vs recomputed `2026-05-04T00:38:11.191000+00:00 no 78.0c`.
- `KXBTC15M-26MAY032115-15` strict `2026-05-04T01:02:13.838000+00:00 no 81.0c` vs recomputed `2026-05-04T01:01:13.732000+00:00 no 69.0c`.
- `KXBTC15M-26MAY032130-30` strict `2026-05-04T01:17:45.202000+00:00 yes 73.0c` vs recomputed `2026-05-04T01:18:00.227000+00:00 yes 73.0c`.
- `KXBTC15M-26MAY032200-00` strict `2026-05-04T01:49:02.931000+00:00 yes 77.0c` vs recomputed `2026-05-04T01:48:02.822000+00:00 yes 68.0c`.
- `KXBTC15M-26MAY032230-30` strict `2026-05-04T02:18:05.671000+00:00 no 66.0c` vs recomputed `2026-05-04T02:17:05.641000+00:00 no 79.0c`.

## Read

- Strict registered fresh sample is positive and coverage-valid so far, but sample size is still too small for promotion.
- Recomputed fresh rows diverge from pre-registered rows; strict registered rows are the promotion authority.
