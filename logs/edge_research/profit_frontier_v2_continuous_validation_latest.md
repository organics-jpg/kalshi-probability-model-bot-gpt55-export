# Frontier V2 Continuous Locked Policy Validation

Generated UTC: `20260504_075204Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Reads an existing forward lock and evaluates the current resolved heartbeat ledger.
- Recomputed fresh metrics can drift when Brownian/RV features are refreshed; strict registered rows are the promotion authority.

## Locked Policy

- Name: `frontier_v2_continuous`
- Label: `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.55; ask<=95; sec_to_close>=120`
- Lock close time: `2026-05-03T22:00:00+00:00`
- Effective entry boundary: `2026-05-03T22:15:00+00:00`
- Lock file: `logs\edge_research\profit_frontier_v2_continuous_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 293/295 | 184/109 | 62.80% | 62.73% | 57.13% | -0.056 | 99.32% | 20.0c | 0.11% | 61.0c |
| recomputed fresh after lock | 34/34 | 20/14 | 58.82% | 67.09% | 42.22% | -0.249 | 100.00% | -281.0c | -12.32% | 66.5c |
| strict registered fresh | 38/39 | 22/16 | 57.89% | 64.45% | 42.19% | -0.223 | 100.00% | -249.0c | -10.17% | 66.0c |

## Recompute Drift Check

- Compared strict and recomputed rows: 34.
- Mismatched rows: 7; missing recomputed rows: 5.
- `KXBTC15M-26MAY031945-45` strict `2026-05-03T23:32:05.265000+00:00 yes 66.0c` vs recomputed `2026-05-03T23:31:05.159000+00:00 yes 60.0c`.
- `KXBTC15M-26MAY032115-15` strict `2026-05-04T01:01:13.732000+00:00 yes 32.0c` vs recomputed `2026-05-04T01:01:13.732000+00:00 no 69.0c`.
- `KXBTC15M-26MAY032130-30` strict `2026-05-04T01:15:30.056000+00:00 no 39.0c` vs recomputed `2026-05-04T01:16:00.076000+00:00 yes 62.0c`.
- `KXBTC15M-26MAY032200-00` strict `2026-05-04T01:48:02.822000+00:00 yes 68.0c` vs recomputed `2026-05-04T01:47:02.728000+00:00 yes 63.0c`.
- `KXBTC15M-26MAY032300-00` strict `2026-05-04T02:45:38.283000+00:00 yes 39.0c` vs recomputed `2026-05-04T02:47:08.343000+00:00 no 72.0c`.

## Read

- Strict registered fresh sample is not promotion-quality proof.
- Recomputed fresh rows diverge from pre-registered rows; strict registered rows are the promotion authority.
