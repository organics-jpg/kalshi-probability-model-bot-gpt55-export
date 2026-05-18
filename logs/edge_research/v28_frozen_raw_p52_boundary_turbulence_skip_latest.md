# v28 Frozen Raw-p52 Boundary-Turbulence Skip

- Freeze timestamp UTC: `2026-05-06T08:50:27.891448+00:00`
- Base policy: `v28_raw_p52_edge0`
- Candidate: `raw_p52_skip_weakraw_nearstrike_recross90`
- Rule: `Start from v28_raw_p52_edge0 and skip rows with p_raw < 0.60, abs_d_sigma <= 0.20, and recross_hazard_score >= 0.90.`
- Future denominator: `114`

## Current Read

- Frozen raw-p52 boundary-turbulence skip has 88 entries versus 112 base entries.
- Delta versus base is 524.0c on future settled rows.
- Skipped future rows so far: 24.

## Summary

| row | entries | settled | W/L | coverage | net c | brier | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| base | 112 | 112 | 66/46 | 98.245614 | -258.000000 | 0.220665 | coverage_too_high, net_not_positive |
| candidate | 88 | 88 | 56/32 | 77.192982 | 266.000000 | 0.209470 | none |

## Skipped Rows

| market | side | p raw | ask | edge | abs d | recross | won | net c | reason |
|---|---|---:|---:|---:|---:|---:|---|---:|---|
| KXBTC15M-26MAY060515-15 | yes | 0.532512 | 0.410000 | 0.122512 | 0.141500 | 0.958625 | False | -86.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY060715-15 | yes | 0.539914 | 0.530000 | 0.009914 | 0.121733 | 0.992709 | True | 90.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY060745-45 | no | 0.553279 | 0.540000 | 0.013279 | 0.063119 | 1.217111 | True | 88.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY060800-00 | yes | 0.523411 | 0.470000 | 0.053411 | 0.027808 | 1.358871 | True | 102.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY060815-15 | no | 0.540349 | 0.540000 | 0.000349 | 0.089986 | 1.015007 | True | 88.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY060845-45 | no | 0.528543 | 0.520000 | 0.008543 | 0.032503 | 1.238079 | True | 92.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY061115-15 | yes | 0.533622 | 0.520000 | 0.013622 | 0.014701 | 1.452888 | False | -108.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY061145-45 | yes | 0.544366 | 0.510000 | 0.034366 | 0.150878 | 1.229956 | False | -106.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY061215-15 | no | 0.536898 | 0.530000 | 0.006898 | 0.085521 | 1.278404 | False | -110.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY061245-45 | no | 0.555732 | 0.520000 | 0.035732 | 0.180237 | 1.211363 | False | -108.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY061300-00 | no | 0.544132 | 0.540000 | 0.004132 | 0.065489 | 1.327168 | True | 88.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY061415-15 | no | 0.521166 | 0.490000 | 0.031166 | 0.052412 | 0.972936 | True | 98.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY061500-00 | yes | 0.550910 | 0.550000 | 0.000910 | 0.111078 | 1.002871 | False | -114.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY061530-30 | no | 0.548704 | 0.530000 | 0.018704 | 0.150647 | 0.995442 | False | -110.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY061930-30 | yes | 0.551364 | 0.470000 | 0.081364 | 0.100563 | 0.905378 | True | 102.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY070030-30 | no | 0.523605 | 0.330000 | 0.193605 | 0.059362 | 0.901651 | False | -70.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY070730-30 | yes | 0.530778 | 0.460000 | 0.070778 | 0.091964 | 0.936121 | False | -96.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY070945-45 | no | 0.532085 | 0.480000 | 0.052085 | 0.067417 | 1.088863 | True | 100.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY071000-00 | yes | 0.543510 | 0.540000 | 0.003510 | 0.037031 | 1.219674 | False | -112.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY071045-45 | yes | 0.557862 | 0.550000 | 0.007862 | 0.082257 | 1.306314 | False | -114.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY071215-15 | yes | 0.543727 | 0.530000 | 0.013727 | 0.056856 | 1.272887 | False | -110.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY071245-45 | yes | 0.559979 | 0.550000 | 0.009979 | 0.168899 | 1.255835 | False | -114.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY071315-15 | yes | 0.533442 | 0.510000 | 0.023442 | 0.042710 | 1.215232 | True | 94.000000 | skip_boundary_turbulence |
| KXBTC15M-26MAY071330-30 | yes | 0.544206 | 0.520000 | 0.024206 | 0.117101 | 1.086679 | False | -108.000000 | skip_boundary_turbulence |
