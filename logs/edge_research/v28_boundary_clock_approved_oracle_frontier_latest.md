# v28 Boundary-Clock Approved Oracle Frontier

Research-only; source-label upper bound, not deployable live logic.

- Generated UTC: `2026-05-07T17:50:46.479275+00:00`

## Interpretation

- boundary_clock_repair_entry: approved-source frontier has 75 approved markets; best boundary_clock_repair_entry_approved_source_realized_oracle settled 75, coverage 61.98347107438016%, net 1013.0c, blockers ['coverage_too_low'].
- boundary_clock_fv_entry_bridge: approved-source frontier has 73 approved markets; best boundary_clock_fv_entry_bridge_approved_source_realized_oracle settled 73, coverage 61.34453781512605%, net 976.0c, blockers ['coverage_too_low'].
- Use this as a feature-discovery target only: source labels are evidence quality, not live entry logic.

## boundary_clock_repair_entry

- Freeze UTC: `2026-05-06T07:07:27.790042+00:00`
- Future denominator: `121`
- Approved rows/markets: `124/75`

| rank | candidate | approved markets | settled | coverage | net c | W/L | recon share | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | boundary_clock_repair_entry_approved_source_realized_oracle | 75 | 75 | 61.983471 | 1013.000000 | 70/5 | 0.000000 | 10 | coverage_too_low |
| 2 | boundary_clock_repair_entry_approved_source_raw_edge | 75 | 75 | 61.983471 | 887.000000 | 68/7 | 0.000000 | 8 | coverage_too_low |
| 3 | boundary_clock_repair_entry_approved_source_low_recross | 75 | 75 | 61.983471 | 720.000000 | 68/7 | 0.000000 | 7 | coverage_too_low |
| 4 | boundary_clock_repair_entry_approved_source_first_ts | 75 | 75 | 61.983471 | 642.000000 | 67/8 | 0.000000 | 6 | coverage_too_low |

## boundary_clock_fv_entry_bridge

- Freeze UTC: `2026-05-06T07:35:02.597585+00:00`
- Future denominator: `119`
- Approved rows/markets: `121/73`

| rank | candidate | approved markets | settled | coverage | net c | W/L | recon share | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | boundary_clock_fv_entry_bridge_approved_source_realized_oracle | 73 | 73 | 61.344538 | 976.000000 | 68/5 | 0.000000 | 9 | coverage_too_low |
| 2 | boundary_clock_fv_entry_bridge_approved_source_raw_edge | 73 | 73 | 61.344538 | 879.000000 | 67/6 | 0.000000 | 8 | coverage_too_low |
| 3 | boundary_clock_fv_entry_bridge_approved_source_low_recross | 73 | 73 | 61.344538 | 712.000000 | 67/6 | 0.000000 | 7 | coverage_too_low |
| 4 | boundary_clock_fv_entry_bridge_approved_source_first_ts | 73 | 73 | 61.344538 | 605.000000 | 65/8 | 0.000000 | 6 | coverage_too_low |
