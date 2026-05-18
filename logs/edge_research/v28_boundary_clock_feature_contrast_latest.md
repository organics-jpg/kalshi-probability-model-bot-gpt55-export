# v28 Boundary-Clock Feature Contrast

Research-only; learns from approved-source rows without changing live logic.

- Generated UTC: `2026-05-07T18:06:07.932212+00:00`

## Interpretation

- boundary_clock_repair_entry: Test raw_edge floor: approved median 0.0873 > reconstructed median 0.0531.
- boundary_clock_repair_entry: Test recross_hazard_score cap: approved median 0.2337 < reconstructed median 0.5966.
- boundary_clock_repair_entry: Test abs_d_sigma floor: approved median 0.9416 > reconstructed median 0.3795.
- boundary_clock_repair_entry: Test ask_prob floor: approved median 0.7800 > reconstructed median 0.6000.
- boundary_clock_fv_entry_bridge: Test raw_edge floor: approved median 0.0840 > reconstructed median 0.0708.
- boundary_clock_fv_entry_bridge: Test recross_hazard_score cap: approved median 0.2295 < reconstructed median 0.6479.
- boundary_clock_fv_entry_bridge: Test abs_d_sigma floor: approved median 0.9289 > reconstructed median 0.3265.
- boundary_clock_fv_entry_bridge: Test ask_prob floor: approved median 0.7800 > reconstructed median 0.5200.

## boundary_clock_repair_entry

| group | rows | markets | W/L | net c | raw edge med | recross med | abs d med | stc med | ask med |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| current_candidate_approved | 26 | 26 | 23/3 | 233.000000 | 0.087270 | 0.233717 | 0.941593 | 468.179500 | 0.780000 |
| current_candidate_reconstructed | 65 | 65 | 35/30 | -465.000000 | 0.053056 | 0.596576 | 0.379541 | 689.739000 | 0.600000 |
| approved_source_raw_edge_frontier | 75 | 75 | 68/7 | 887.000000 | 0.092278 | 0.272072 | 0.965012 | 584.336000 | 0.780000 |

## boundary_clock_fv_entry_bridge

| group | rows | markets | W/L | net c | raw edge med | recross med | abs d med | stc med | ask med |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| current_candidate_approved | 19 | 19 | 15/4 | -4.000000 | 0.083962 | 0.229504 | 0.928896 | 474.481000 | 0.780000 |
| current_candidate_reconstructed | 71 | 71 | 40/31 | -109.000000 | 0.070778 | 0.647900 | 0.326478 | 771.226000 | 0.520000 |
| approved_source_raw_edge_frontier | 73 | 73 | 67/6 | 879.000000 | 0.089793 | 0.272072 | 0.951357 | 584.336000 | 0.780000 |
