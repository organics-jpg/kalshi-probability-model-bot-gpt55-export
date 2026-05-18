# v28 Frozen Feature-Gate Exit-Bid Delayed Recheck

Research-only frozen watch. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:33.195306+00:00`
- Freeze UTC: `2026-05-07T07:54:52.452489+00:00`
- Candidate: `delay60_bid_ge60_drop_lte10`
- Rule: `Delay 60s after selected-side feature-gate exit; suppress only if held-side bid >=60c and window drop <=10c.`

## Interpretation

- Research-only frozen watch; no live bot changes or orders.
- Post-birth has 11 rows, 8 suppressions, net -360.4c.
- Only post-birth rows count as forward evidence.

## Lanes

| lane | rows | suppressed | sup H/H | live c | candidate c | delta c | recovery c | loss cost c | W/L | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_prefreeze_context` | 25 | 19 | 17/2 | -113.00 | 610.80 | 723.80 | 1673.80 | -950.00 | 20/5 | 6 | suppressed_losers_present, diagnostic_prefreeze |
| `post_delayed_recheck_birth` | 11 | 8 | 6/2 | -90.00 | -360.40 | -270.40 | 679.60 | -950.00 | 7/4 | 0 | settled_lt_30, suppressed_decisions_lt_30, net_not_positive, delta_not_positive, suppressed_losers_present, full_loss_cushion_lt_3 |
