# v28 Feature-Gate Exit-Bid Delayed Recheck

Research-only diagnostic frontier. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:32.662760+00:00`

## Interpretation

- Research-only delayed-recheck frontier; no live bot changes or orders.
- Best diagnostic variant delay30_bid_ge60 has 24 suppressions and 754.6c candidate net.
- All rows are pre-freeze diagnostic; a frozen child would need its own post-birth evidence.

## Variants

| variant | delay | bid floor | max drop | rows | suppressed | sup H/H | live c | candidate c | delta c | recovery c | loss cost c | missing | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `delay30_bid_ge60` | 30 | 60 | None | 25 | 24 | 21/3 | -113.00 | 754.60 | 867.60 | 1969.60 | -1102.00 | 0 | diagnostic_rows_lt_30, suppressed_decisions_lt_30, suppressed_losers_present, diagnostic_prefreeze |
| `delay120_bid_ge60` | 120 | 60 | None | 25 | 21 | 19/2 | -113.00 | 746.80 | 859.80 | 1809.80 | -950.00 | 0 | diagnostic_rows_lt_30, suppressed_decisions_lt_30, suppressed_losers_present, diagnostic_prefreeze |
| `delay60_bid_ge60` | 60 | 60 | None | 25 | 21 | 19/2 | -113.00 | 726.80 | 839.80 | 1789.80 | -950.00 | 0 | diagnostic_rows_lt_30, suppressed_decisions_lt_30, suppressed_losers_present, diagnostic_prefreeze |
| `delay60_bid_ge60_drop_lte20` | 60 | 60 | 20 | 25 | 21 | 19/2 | -113.00 | 726.80 | 839.80 | 1789.80 | -950.00 | 0 | diagnostic_rows_lt_30, suppressed_decisions_lt_30, suppressed_losers_present, diagnostic_prefreeze |
| `delay30_bid_ge60_drop_lte10` | 30 | 60 | 10 | 25 | 23 | 20/3 | -113.00 | 706.60 | 819.60 | 1921.60 | -1102.00 | 0 | diagnostic_rows_lt_30, suppressed_decisions_lt_30, suppressed_losers_present, diagnostic_prefreeze |
| `delay60_bid_ge60_drop_lte10` | 60 | 60 | 10 | 25 | 19 | 17/2 | -113.00 | 610.80 | 723.80 | 1673.80 | -950.00 | 0 | diagnostic_rows_lt_30, suppressed_decisions_lt_30, suppressed_losers_present, diagnostic_prefreeze |
| `delay120_bid_ge60_drop_lte10` | 120 | 60 | 10 | 25 | 18 | 16/2 | -113.00 | 522.80 | 635.80 | 1585.80 | -950.00 | 0 | diagnostic_rows_lt_30, suppressed_decisions_lt_30, suppressed_losers_present, diagnostic_prefreeze |
| `delay60_bid_ge65_drop_lte10` | 60 | 65 | 10 | 25 | 17 | 15/2 | -113.00 | 386.80 | 499.80 | 1449.80 | -950.00 | 0 | diagnostic_rows_lt_30, suppressed_decisions_lt_30, suppressed_losers_present, diagnostic_prefreeze |
| `delay60_bid_ge70_drop_lte10` | 60 | 70 | 10 | 25 | 16 | 14/2 | -113.00 | 264.80 | 377.80 | 1327.80 | -950.00 | 0 | diagnostic_rows_lt_30, suppressed_decisions_lt_30, suppressed_losers_present, full_loss_cushion_lt_3, diagnostic_prefreeze |
