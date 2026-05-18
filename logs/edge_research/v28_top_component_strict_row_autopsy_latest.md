# v28 Top-Component Strict Row Autopsy

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T23:35:06.845152+00:00`
- Strict unique rows: `27`
- Strict net: `-16c`
- Promotion gate passes: `0`

## Interpretation

- Research-only strict-row autopsy; no live bot changes or orders.
- Strict sample is only 27 unique rows, so this is failure classification, not promotion evidence.
- All observed strict rows are parent-fill rows without exit-clock joins; the exit-rescue component has not been forward-proven here.
- Losses are 6 rows for -582c; wins are 21 rows for 566c.
- The current strict failures point to source-quality plus FV/entry false positives, not a reason to broaden parent-fill exposure.

## Failure Tags

| tag | rows |
|---|---:|
| `strict_forward_winner` | 21 |
| `parent_fill_no_exit_clock` | 17 |
| `source_quality_error` | 11 |
| `fv_or_entry_error` | 6 |
| `moderate_recross` | 5 |
| `weak_boundary_distance` | 4 |
| `large_raw_edge_false_positive` | 2 |
| `low_or_mid_ask_touch` | 2 |

## Source Net

| source | rows | net |
|---|---:|---:|
| `approved_entry` | 16 | 117c |
| `rejected_actionable` | 11 | -133c |

## Strict Rows

| market | side | source | pnl | won | raw edge | recross | abs d | ask | tags |
|---|---|---|---:|---|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY071100-00` | `yes` | `approved_entry` | -166c | False | 0.054 | 0.305 | 1.010 | 0.830 | fv_or_entry_error, moderate_recross |
| `KXBTC15M-26MAY071015-15` | `no` | `approved_entry` | -162c | False | 0.081 | 0.418 | 0.936 | 0.780 | fv_or_entry_error, moderate_recross |
| `KXBTC15M-26MAY071215-15` | `yes` | `rejected_actionable` | -75c | False | 0.108 | 0.488 | 0.791 | 0.720 | parent_fill_no_exit_clock, source_quality_error, fv_or_entry_error, weak_boundary_distance, moderate_recross |
| `KXBTC15M-26MAY070900-00` | `no` | `rejected_actionable` | -73c | False | 0.056 | 0.457 | 0.592 | 0.700 | parent_fill_no_exit_clock, source_quality_error, fv_or_entry_error, weak_boundary_distance, moderate_recross |
| `KXBTC15M-26MAY070630-30` | `yes` | `rejected_actionable` | -59c | False | 0.238 | 0.372 | 0.658 | 0.550 | parent_fill_no_exit_clock, source_quality_error, fv_or_entry_error, low_or_mid_ask_touch, weak_boundary_distance, moderate_recross, large_raw_edge_false_positive |
| `KXBTC15M-26MAY070615-15` | `yes` | `rejected_actionable` | -47c | False | 0.345 | 0.143 | 0.631 | 0.430 | parent_fill_no_exit_clock, source_quality_error, fv_or_entry_error, low_or_mid_ask_touch, weak_boundary_distance, large_raw_edge_false_positive |
| `KXBTC15M-26MAY071030-30` | `no` | `rejected_actionable` | 7c | True | 0.057 | 0.180 | 1.626 | 0.910 | parent_fill_no_exit_clock, source_quality_error, strict_forward_winner |
| `KXBTC15M-26MAY070715-15` | `yes` | `rejected_actionable` | 8c | True | 0.081 | 0.051 | 2.281 | 0.910 | parent_fill_no_exit_clock, source_quality_error, strict_forward_winner |
| `KXBTC15M-26MAY071245-45` | `no` | `rejected_actionable` | 8c | True | 0.034 | 0.231 | 1.286 | 0.900 | parent_fill_no_exit_clock, source_quality_error, strict_forward_winner |
| `KXBTC15M-26MAY071300-00` | `no` | `rejected_actionable` | 8c | True | 0.038 | 0.062 | 1.290 | 0.900 | parent_fill_no_exit_clock, source_quality_error, strict_forward_winner |
| `KXBTC15M-26MAY071130-30` | `no` | `approved_entry` | 13c | True | 0.067 | 0.332 | 1.183 | 0.850 | parent_fill_no_exit_clock, strict_forward_winner |
| `KXBTC15M-26MAY070645-45` | `yes` | `approved_entry` | 16c | True | 0.085 | 0.369 | 1.014 | 0.810 | parent_fill_no_exit_clock, strict_forward_winner |
| `KXBTC15M-26MAY071330-30` | `no` | `rejected_actionable` | 16c | True | 0.045 | 0.392 | 0.928 | 0.820 | parent_fill_no_exit_clock, source_quality_error, strict_forward_winner |
| `KXBTC15M-26MAY070815-15` | `yes` | `approved_entry` | 20c | True | 0.051 | 0.186 | 1.397 | 0.900 | strict_forward_winner |
| `KXBTC15M-26MAY070915-15` | `no` | `approved_entry` | 20c | True | 0.107 | 0.284 | 0.951 | 0.770 | parent_fill_no_exit_clock, strict_forward_winner |
| `KXBTC15M-26MAY070830-30` | `no` | `approved_entry` | 21c | True | 0.120 | 0.127 | 1.007 | 0.770 | parent_fill_no_exit_clock, strict_forward_winner |
| `KXBTC15M-26MAY071230-30` | `yes` | `approved_entry` | 21c | True | 0.082 | 0.296 | 0.882 | 0.770 | parent_fill_no_exit_clock, strict_forward_winner |
| `KXBTC15M-26MAY071045-45` | `no` | `approved_entry` | 22c | True | 0.115 | 0.470 | 0.954 | 0.750 | parent_fill_no_exit_clock, strict_forward_winner |
| `KXBTC15M-26MAY070600-00` | `yes` | `rejected_actionable` | 28c | True | 0.122 | 0.202 | 0.734 | 0.690 | parent_fill_no_exit_clock, source_quality_error, strict_forward_winner |
| `KXBTC15M-26MAY070945-45` | `no` | `approved_entry` | 28c | True | 0.164 | 0.436 | 0.883 | 0.690 | parent_fill_no_exit_clock, strict_forward_winner |
| `KXBTC15M-26MAY071115-15` | `yes` | `approved_entry` | 32c | True | 0.052 | 0.220 | 1.053 | 0.840 | strict_forward_winner |
| `KXBTC15M-26MAY070930-30` | `yes` | `approved_entry` | 40c | True | 0.056 | 0.376 | 0.879 | 0.800 | strict_forward_winner |
| `KXBTC15M-26MAY071315-15` | `yes` | `approved_entry` | 44c | True | 0.071 | 0.132 | 0.850 | 0.780 | strict_forward_winner |
| `KXBTC15M-26MAY071145-45` | `yes` | `rejected_actionable` | 46c | True | 0.047 | 0.312 | 1.183 | 0.870 | source_quality_error, strict_forward_winner |
| `KXBTC15M-26MAY071200-00` | `no` | `approved_entry` | 46c | True | 0.089 | 0.090 | 0.919 | 0.770 | strict_forward_winner |
| `KXBTC15M-26MAY071000-00` | `no` | `approved_entry` | 58c | True | 0.142 | 0.484 | 0.895 | 0.710 | strict_forward_winner |
| `KXBTC15M-26MAY070745-45` | `yes` | `approved_entry` | 64c | True | 0.224 | 0.198 | 1.081 | 0.680 | strict_forward_winner |
