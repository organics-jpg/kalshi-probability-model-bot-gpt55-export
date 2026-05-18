# v28 Broad Book-Edge Source Audit

Diagnostic-only audit for the current broad book-edge lane. No live orders.

- Policy: `book_plus_05_no_cheap_yes_boundary`
- Diagnostic supported: `False`
- Entries/settled/W-L: `164/164/92-72`
- Gross / avg gross: `646.000000/3.939024`
- Simulated share: `0.810976`
- Blockers: `simulated_share_gt_35pct`

## Interpretation

- book_plus_05_no_cheap_yes_boundary is the current best broad discovery lane, but promotion depends on future rows and source balance.
- Actual-approved rows are 31 settled for 132.0c; rejected-actionable rows are 133 settled for 514.0c.
- Simulated/rejected share is 0.8109756097560976; blocker threshold is 0.35.
- Frozen future settled rows are 111; discovery evidence is not enough.

## Source Rows

| source | entries | settled | W-L | gross c | avg c |
|---|---:|---:|---:|---:|---:|
| approved_entry | 31 | 31 | 26-5 | 132.000000 | 4.258065 |
| rejected_actionable | 133 | 133 | 66-67 | 514.000000 | 3.864662 |

## Physics Rows

| bucket | entries | settled | W-L | gross c | avg c |
|---|---:|---:|---:|---:|---:|
| high_conf_p65_plus | 67 | 67 | 53-14 | 642.000000 | 9.582090 |
| mid_conf_45_65 | 82 | 82 | 35-47 | 26.000000 | 0.317073 |
| yes_side | 86 | 86 | 48-38 | 132.000000 | 1.534884 |
| no_side | 78 | 78 | 44-34 | 514.000000 | 6.589744 |
| high_recross_075_plus | 65 | 65 | 34-31 | 1086.000000 | 16.707692 |
| near_strike_sigma_lt025 | 69 | 69 | 30-39 | 550.000000 | 7.971014 |
