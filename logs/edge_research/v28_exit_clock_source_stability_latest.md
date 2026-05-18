# v28 Exit-Clock Source Stability

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-07T17:06:39.991057+00:00`
- Stable for new freeze: `False`
- Row count values: `[137, 71, 91, 88, 100]`
- Common / union keys: `15` / `169`
- Blockers: `exit_clock_source_not_stable_across_repeated_reads`

## Samples

| sample | rows | unique keys | last entry ts |
|---:|---:|---:|---|
| 0 | 137 | 137 | `2026-05-07T16:24:52.871742+00:00` |
| 1 | 71 | 71 | `2026-05-07T16:24:52.871742+00:00` |
| 2 | 91 | 91 | `2026-05-07T16:24:52.871742+00:00` |
| 3 | 88 | 88 | `2026-05-07T16:24:52.871742+00:00` |
| 4 | 100 | 100 | `2026-05-07T16:24:52.871742+00:00` |

## Read

- This checks the exit-clock source used by common-clock exit reports.
- If repeated reads differ, new watches should use a materialized snapshot or wait until the source settles before freezing a denominator-sensitive rule.
