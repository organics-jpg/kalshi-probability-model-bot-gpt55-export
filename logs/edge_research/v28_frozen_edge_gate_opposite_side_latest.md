# v28 Frozen Edge-Gate Opposite-Side Replacement

- Freeze timestamp UTC: `2026-05-06T06:05:34.391059+00:00`
- Base entry policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- FV variant: `edge_phase_shrink`
- Adjusted edge floor: `-0.120000`
- Opposite requirements: raw p >= `0.500000`, raw edge >= `0.000000`, adjusted edge >= `-0.020000`
- Future denominator: `125`

## Current Read

- Frozen edge-gate opposite replacement has 91 entries versus 91 base entries.
- It has replaced 0 of 0 future edge-gate skips so far.
- Net delta versus base is 0.0c; promotion still requires >=30 settled rows and coverage inside the target band.

## Summary

| row | entries | settled | W/L | coverage | net c | avg net c | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| base | 91 | 91 | 50/41 | 72.800000 | -585.000000 | -6.428571 | coverage_too_low, net_not_positive |
| kept_after_edge_gate | 91 | 91 | 50/41 | 72.800000 | -585.000000 | -6.428571 | coverage_too_low, net_not_positive |
| replacement_only | 0 | 0 | 0/0 | 0.000000 | 0 | None | settled_lt_30, coverage_too_low, net_not_positive |
| candidate | 91 | 91 | 50/41 | 72.800000 | -585.000000 | -6.428571 | coverage_too_low, net_not_positive |

## Replacement Cases

| market | skipped side | skipped adj edge | opposite side | opposite raw edge | opposite adj edge | opposite won | opposite net c |
|---|---|---:|---|---:|---:|---|---:|
