# v28 Target-Coverage Sample Runway

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Overlay: `book_probability`
- Freeze timestamp UTC: `2026-05-06T02:08:01.321286+00:00`
- Entries/settled/pending/denominator: `112/112/0/152`
- Coverage: `73.684211` within `[75.0, 90.0]`
- Settled rows to 30: `0`
- Promotion ready: `False`

## Coverage Runway

- Max consecutive future missed markets before dropping below 75%: `0`
- Coverage after that many misses / one more miss: `73.684211` / `73.202614`
- Max consecutive future selected markets before rising above 90%: `248`
- Coverage after that many entries / one more entry: `90.000000` / `90.024938`

## Pending Selected Rows

| market | side | p raw | ask | edge | stc | reason |
|---|---|---:|---:|---:|---:|---|
| none |  |  |  |  |  |  |

## Interpretation

- The target-coverage candidate is currently inside the 75-90% band but sample size is still the hard blocker.
- Because the denominator is small, one or two new missed markets can materially change coverage.
- Coverage movement should be monitored, but probability promotion remains blocked until settled rows reach 30.
