# v28 Frozen Soft-Frontier Mid-Price Delayed-Recheck Exit

Research-only frozen watch. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:53.134673+00:00`
- Freeze UTC: `2026-05-07T08:05:51.308715+00:00`
- Entry: `diagnostic_entry_quarter_midprice_boundary`
- Exit source: `latest`
- Recheck: `delay60_bid_ge60_drop_lte10`
- Rule: `Broad soft-frontier/mid-price entry; on latest v28 exit, wait 60s and suppress only if held bid remains >=60c with <=10c immediate drop.`

## Interpretation

- Research-only frozen broad-entry delayed-recheck exit watch; no live bot changes or orders.
- Post-birth has 3 joined rows, 3 suppressions, net 120.0c.
- Only post-birth rows count as forward evidence.

## Lanes

| lane | rows | suppressed | H/H | current c | candidate c | delta c | W/L | recon | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_prefreeze_context` | 59 | 33 | 31/0 | 1057.500000 | 1501.500000 | 444.000000 | 51/8 | 0.152542 | 15 | diagnostic_prefreeze |
| `post_delayed_recheck_birth` | 3 | 3 | 3/0 | 54.000000 | 120.000000 | 66.000000 | 3/0 | 0.000000 | 1 | joined_rows_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
