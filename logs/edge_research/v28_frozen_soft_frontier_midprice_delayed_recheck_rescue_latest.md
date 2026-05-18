# v28 Frozen Soft-Frontier Mid-Price Delayed-Recheck Clean Rescue

Research-only frozen watch. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:53.582756+00:00`
- Freeze UTC: `2026-05-07T08:24:03.515891+00:00`
- Entry: `diagnostic_entry_quarter_midprice_boundary`
- Exit source: `latest`
- Recheck: `delay60_bid_ge60_drop_lte11`
- Rule: `Broad soft-frontier/mid-price entry; on latest v28 exit, wait 60s and suppress only if held bid remains >=60c with <=11c immediate drop.`

## Interpretation

- Research-only frozen clean delayed-recheck rescue watch; no live bot changes or orders.
- Post-birth has 3 joined rows, 3 suppressions, net 120.0c.
- Strict gates use MIN_ROWS=30, MIN_SUPPRESSED=30, MIN_FULL_LOSS_CUSHION=3.
- Only post-birth rows count as forward evidence.

## Lanes

| lane | rows | suppressed | H/H | current c | candidate c | delta c | W/L | recon | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_prefreeze_context` | 59 | 34 | 32/0 | 1057.500000 | 1601.500000 | 544.000000 | 52/7 | 0.152542 | 16 | diagnostic_prefreeze |
| `post_clean_rescue_birth` | 3 | 3 | 3/0 | 54.000000 | 120.000000 | 66.000000 | 3/0 | 0.000000 | 1 | joined_rows_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
