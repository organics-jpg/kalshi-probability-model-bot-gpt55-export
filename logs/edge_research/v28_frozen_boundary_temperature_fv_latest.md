# v28 Frozen Boundary-Temperature FV

Research-only; no live bot changes and no orders.

- Freeze timestamp UTC: `2026-05-06T11:12:06.081553+00:00`
- Entry policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Variant: `boundary_temp_strong`
- Future entries/settled/denominator: `78/78/105`
- Ready for consideration: `True`
- Blockers: `none`
- Brier/logloss delta vs raw: `-0.004505/-0.013417`

## Interpretation

- Frozen boundary-temperature FV has 78 future entries and 78 settled/scored rows.
- Candidate Brier/logloss mean deltas versus raw are -0.004505350022369005/-0.013416897536084207.
- This is probability calibration only; it does not change entries, exits, or live order logic.

## Metrics

| slice | rows | adjusted | W/L | avg p | brier mean d | brier p95 | logloss mean d | logloss p95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| raw | 78 | 0 | 46/32 | 0.646068 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| candidate | 78 | 45 | 46/32 | 0.652083 | -0.004505 | -0.001539 | -0.013417 | -0.006001 |
