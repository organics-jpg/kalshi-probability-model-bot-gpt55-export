# v28 Target-Coverage FV Edge Gate Diagnostic

Diagnostic-only view of adjusted FV edge versus executable ask.

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Target freeze timestamp UTC: `2026-05-06T02:08:01.321286+00:00`
- Base entries/coverage/denominator: `112/73.684211/152`

## Interpretation

- No adjusted-edge diagnostic row clears sample, coverage, and positive-net blockers yet.
- Best positive-net row is confidence_leak_shrink floor 0.02 with coverage 42.10526315789474 and blockers ['coverage_too_low'].

## Ranking

| rank | variant | edge floor | entries | settled | W/L | coverage | net c | skipped | skipped net c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | confidence_leak_shrink | 0.020000 | 64 | 64 | 40/24 | 42.105263 | 689.000000 | 48 | -1315.000000 | coverage_too_low |
| 2 | boundary_recross_shrink_probability | 0.020000 | 63 | 63 | 39/24 | 41.447368 | 629.000000 | 49 | -1255.000000 | coverage_too_low |
| 3 | edge_phase_shrink | 0.020000 | 69 | 69 | 43/26 | 45.394737 | 573.000000 | 43 | -1199.000000 | coverage_too_low |
| 4 | edge_phase_shrink | -0.020000 | 85 | 85 | 51/34 | 55.921053 | 315.000000 | 27 | -941.000000 | coverage_too_low |
| 5 | raw_probability | 0.020000 | 90 | 90 | 54/36 | 59.210526 | 257.000000 | 22 | -883.000000 | coverage_too_low |
| 6 | confidence_leak_shrink | -0.020000 | 82 | 82 | 48/34 | 53.947368 | 175.000000 | 30 | -801.000000 | coverage_too_low |
| 7 | edge_phase_shrink | 0.000000 | 78 | 78 | 46/32 | 51.315789 | 145.000000 | 34 | -771.000000 | coverage_too_low |
| 8 | boundary_recross_shrink_probability | -0.020000 | 78 | 78 | 45/33 | 51.315789 | 107.000000 | 34 | -733.000000 | coverage_too_low |
| 9 | edge_phase_shrink | -0.040000 | 90 | 90 | 53/37 | 59.210526 | 97.000000 | 22 | -723.000000 | coverage_too_low |
| 10 | confidence_leak_shrink | 0.000000 | 75 | 75 | 43/32 | 49.342105 | 5.000000 | 37 | -631.000000 | coverage_too_low |
| 11 | boundary_recross_shrink_probability | -0.040000 | 84 | 84 | 48/36 | 55.263158 | -33.000000 | 28 | -593.000000 | coverage_too_low, net_not_positive |
| 12 | confidence_leak_shrink | -0.040000 | 87 | 87 | 50/37 | 57.236842 | -43.000000 | 25 | -583.000000 | coverage_too_low, net_not_positive |
| 13 | boundary_recross_shrink_probability | 0.000000 | 71 | 71 | 40/31 | 46.710526 | -63.000000 | 41 | -563.000000 | coverage_too_low, net_not_positive |
| 14 | edge_phase_shrink | -0.060000 | 102 | 102 | 59/43 | 67.105263 | -219.000000 | 10 | -407.000000 | coverage_too_low, net_not_positive |
| 15 | edge_phase_shrink | -0.100000 | 110 | 110 | 64/46 | 72.368421 | -314.000000 | 2 | -312.000000 | coverage_too_low, net_not_positive |
| 16 | boundary_recross_shrink_probability | -0.060000 | 96 | 96 | 54/42 | 63.157895 | -349.000000 | 16 | -277.000000 | coverage_too_low, net_not_positive |
| 17 | edge_phase_shrink | -0.080000 | 106 | 106 | 61/45 | 69.736842 | -353.000000 | 6 | -273.000000 | coverage_too_low, net_not_positive |
| 18 | boundary_recross_shrink_probability | -0.080000 | 102 | 102 | 58/44 | 67.105263 | -353.000000 | 10 | -273.000000 | coverage_too_low, net_not_positive |
| 19 | confidence_leak_shrink | -0.060000 | 99 | 99 | 56/43 | 65.131579 | -359.000000 | 13 | -267.000000 | coverage_too_low, net_not_positive |
| 20 | boundary_recross_shrink_probability | -0.100000 | 108 | 108 | 62/46 | 71.052632 | -402.000000 | 4 | -224.000000 | coverage_too_low, net_not_positive |
| 21 | confidence_leak_shrink | -0.100000 | 108 | 108 | 62/46 | 71.052632 | -402.000000 | 4 | -224.000000 | coverage_too_low, net_not_positive |
| 22 | edge_phase_shrink | -0.120000 | 111 | 111 | 64/47 | 73.026316 | -465.000000 | 1 | -161.000000 | coverage_too_low, net_not_positive |
| 23 | confidence_leak_shrink | -0.080000 | 103 | 103 | 58/45 | 67.763158 | -493.000000 | 9 | -133.000000 | coverage_too_low, net_not_positive |
| 24 | boundary_recross_shrink_probability | -0.120000 | 110 | 110 | 63/47 | 72.368421 | -502.000000 | 2 | -124.000000 | coverage_too_low, net_not_positive |
| 25 | confidence_leak_shrink | -0.150000 | 110 | 110 | 63/47 | 72.368421 | -502.000000 | 2 | -124.000000 | coverage_too_low, net_not_positive |
| 26 | confidence_leak_shrink | -0.120000 | 109 | 109 | 62/47 | 71.710526 | -553.000000 | 3 | -73.000000 | coverage_too_low, net_not_positive |
| 27 | raw_probability | -0.150000 | 112 | 112 | 64/48 | 73.684211 | -626.000000 | 0 | 0 | coverage_too_low, net_not_positive |
| 28 | raw_probability | -0.120000 | 112 | 112 | 64/48 | 73.684211 | -626.000000 | 0 | 0 | coverage_too_low, net_not_positive |
| 29 | raw_probability | -0.100000 | 112 | 112 | 64/48 | 73.684211 | -626.000000 | 0 | 0 | coverage_too_low, net_not_positive |
| 30 | raw_probability | -0.080000 | 112 | 112 | 64/48 | 73.684211 | -626.000000 | 0 | 0 | coverage_too_low, net_not_positive |
| 31 | raw_probability | -0.060000 | 112 | 112 | 64/48 | 73.684211 | -626.000000 | 0 | 0 | coverage_too_low, net_not_positive |
| 32 | raw_probability | -0.040000 | 112 | 112 | 64/48 | 73.684211 | -626.000000 | 0 | 0 | coverage_too_low, net_not_positive |
| 33 | raw_probability | -0.020000 | 112 | 112 | 64/48 | 73.684211 | -626.000000 | 0 | 0 | coverage_too_low, net_not_positive |
| 34 | raw_probability | 0.000000 | 112 | 112 | 64/48 | 73.684211 | -626.000000 | 0 | 0 | coverage_too_low, net_not_positive |
| 35 | boundary_recross_shrink_probability | -0.150000 | 112 | 112 | 64/48 | 73.684211 | -626.000000 | 0 | 0 | coverage_too_low, net_not_positive |
| 36 | edge_phase_shrink | -0.150000 | 112 | 112 | 64/48 | 73.684211 | -626.000000 | 0 | 0 | coverage_too_low, net_not_positive |
