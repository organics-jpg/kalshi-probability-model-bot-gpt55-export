# v28 Frozen Edge-Phase Edge Gate

- Freeze timestamp UTC: `2026-05-06T05:46:47.707629+00:00`
- Base entry policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- FV variant: `edge_phase_shrink`
- Adjusted edge floor: `-0.120000`
- Future denominator: `126`

## Current Read

- Frozen edge-phase edge gate has 92 entries versus 92 base entries.
- It has skipped 0 future rows so far; promotion requires forward sample size and target coverage.
- This is an adjusted-FV paid-price gate derived from the edge-phase shrink model.

## Summary

| row | entries | settled | W/L | coverage | net c | blockers |
|---|---:|---:|---:|---:|---:|---|
| base | 92 | 92 | 50/42 | 73.015873 | -695.000000 | coverage_too_low, net_not_positive |
| candidate | 92 | 92 | 50/42 | 73.015873 | -695.000000 | coverage_too_low, net_not_positive |

## Skipped Rows

| market | side | p raw | p adj | ask | adj edge | raw edge | abs d | recross | won | net c | reason |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
