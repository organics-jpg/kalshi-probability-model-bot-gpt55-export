# Book Hour04 V2 Switch Forward Validation

Generated UTC: `20260504_075212Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Locked rule: use book_margin, but switch to frontier_v2 when the first book anchor entry is in UTC hour 04.
- This is forward-test evidence only; the regime-switch scan is not promotion evidence.

## Lock

- Label: `book_margin_switch_to_frontier_v2_if_anchor_entry_hour_utc==04`
- Effective entry boundary: `2026-05-04T03:45:00+00:00`
- Lock file: `logs\edge_research\profit_book_hour04_v2_switch_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 293/295 | 213/80 | 72.70% | 67.37% | 67.33% | -0.000 | 99.32% | 1560.0c | 7.90% | 64.0c |
| recomputed fresh after lock | 12/12 | 7/5 | 58.33% | 68.17% | 31.95% | -0.362 | 100.00% | -118.0c | -14.43% | 64.5c |
| strict registered fresh | 16/17 | 9/7 | 56.25% | 65.44% | 33.18% | -0.323 | 100.00% | -147.0c | -14.04% | 64.5c |

## Recompute Drift Check

- Compared strict and recomputed rows: 12.
- Mismatched rows: 4; missing recomputed rows: 5.
- `KXBTC15M-26MAY040045-45` strict `2026-05-04T04:34:02.948000+00:00 no 54.0c` vs recomputed `2026-05-04T04:35:03.054000+00:00 yes 69.0c`.
- `KXBTC15M-26MAY040145-45` strict `2026-05-04T05:31:08.227000+00:00 no 66.0c` vs recomputed `2026-05-04T05:30:53.210000+00:00 no 62.0c`.
- `KXBTC15M-26MAY040215-15` strict `2026-05-04T06:01:10.540000+00:00 yes 47.0c` vs recomputed `2026-05-04T06:04:40.913000+00:00 no 64.0c`.
- `KXBTC15M-26MAY040245-45` strict `2026-05-04T06:30:43.413000+00:00 yes 48.0c` vs recomputed `2026-05-04T06:31:13.416000+00:00 yes 62.0c`.

## Read

- Strict registered fresh sample is not promotion-quality proof.
- The physical hypothesis is session-dependent microstructure, not a universal replacement for book pressure.
