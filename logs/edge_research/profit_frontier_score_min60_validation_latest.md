# Score Min60 Locked Policy Validation

Generated UTC: `20260504_075204Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Reads an existing forward lock and evaluates the current resolved heartbeat ledger.
- Recomputed fresh metrics can drift when Brownian/RV features are refreshed; strict registered rows are the promotion authority.

## Locked Policy

- Name: `score_min60`
- Label: `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120`
- Lock close time: `2026-05-03T22:15:00+00:00`
- Effective entry boundary: `2026-05-03T22:30:00+00:00`
- Lock file: `logs\edge_research\profit_frontier_score_min60_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 292/295 | 221/71 | 75.68% | 71.48% | 70.45% | -0.010 | 98.98% | 1227.0c | 5.88% | 68.0c |
| recomputed fresh after lock | 33/33 | 24/9 | 72.73% | 73.15% | 55.78% | -0.174 | 100.00% | -14.0c | -0.58% | 69.0c |
| strict registered fresh | 37/38 | 26/11 | 70.27% | 72.62% | 54.22% | -0.184 | 100.00% | -87.0c | -3.24% | 69.0c |

## Recompute Drift Check

- Compared strict and recomputed rows: 33.
- Mismatched rows: 11; missing recomputed rows: 5.
- `KXBTC15M-26MAY031845-45` strict `2026-05-03T22:35:00.056000+00:00 yes 86.0c` vs recomputed `2026-05-03T22:34:15.030000+00:00 yes 81.0c`.
- `KXBTC15M-26MAY031945-45` strict `2026-05-03T23:32:05.265000+00:00 yes 66.0c` vs recomputed `2026-05-03T23:31:35.210000+00:00 yes 63.0c`.
- `KXBTC15M-26MAY032045-45` strict `2026-05-04T00:34:55.918000+00:00 yes 65.0c` vs recomputed `2026-05-04T00:38:11.191000+00:00 no 78.0c`.
- `KXBTC15M-26MAY032115-15` strict `2026-05-04T01:02:13.838000+00:00 no 81.0c` vs recomputed `2026-05-04T01:01:13.732000+00:00 no 69.0c`.
- `KXBTC15M-26MAY032130-30` strict `2026-05-04T01:17:45.202000+00:00 yes 73.0c` vs recomputed `2026-05-04T01:18:00.227000+00:00 yes 73.0c`.

## Read

- Strict registered fresh sample is not promotion-quality proof.
- Recomputed fresh rows diverge from pre-registered rows; strict registered rows are the promotion authority.
