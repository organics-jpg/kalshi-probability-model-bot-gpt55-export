# v28 Target-Coverage FV Live Evidence Audit

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Overlay: `book_probability`
- Total rows/W-L/net: `112/64-48/-626.000000c`
- Approved-entry rows: `7`
- Simulated/rejected rows/share: `105/0.937500`
- Blockers: `actual_approved_rows_lt_10, simulated_share_gt_35pct`

## Interpretation

- Actual approved-entry evidence is 7 rows; the rest is actionable rejected shadow evidence.
- Simulated/rejected evidence share is 93.75%.
- Live-evidence blockers remain: actual_approved_rows_lt_10, simulated_share_gt_35pct.

## By Source

| source | rows | W/L | net c | brier d mean | logloss d mean |
|---|---:|---:|---:|---:|---:|
| approved_entry | 7 | 7/0 | 63.000000 | 0.029919 | 0.114698 |
| rejected_actionable | 105 | 57/48 | -689.000000 | -0.017902 | -0.036435 |
