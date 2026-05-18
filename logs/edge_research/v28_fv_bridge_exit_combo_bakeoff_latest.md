# v28 FV Bridge Exit Combo Bakeoff

Research-only; no live bot changes and no orders.

## Current Read

- Approved-only diagnostic best policy is reduce_geometry_plus_collapse_drawdown_lte_18 with candidate net 1049.0c.
- Collapse suppress rules here use available matched exit fields; the older sigma-aware rule remains a separate hypothesis.

## diagnostic_existing_false_conviction_freeze


### lead_reconstructed_only

| rank | policy | settled | coverage | dir W/L | candidate c | delta c | hold c | matched | suppressed | neg winners |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `reduce_geometry_plus_collapse_drawdown_lte_12` | 91 | 80.531 | 56/35 | -171.000 | 340.000 | -91.000 | 37 | 11 | 0 |
| 2 | `reduce_geometry_plus_collapse_drawdown_lte_15` | 91 | 80.531 | 56/35 | -171.000 | 340.000 | -91.000 | 37 | 11 | 0 |
| 3 | `reduce_geometry_plus_collapse_drawdown_lte_18` | 91 | 80.531 | 56/35 | -171.000 | 340.000 | -91.000 | 37 | 11 | 0 |
| 4 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_055` | 91 | 80.531 | 56/35 | -171.000 | 340.000 | -91.000 | 37 | 11 | 0 |
| 5 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_060` | 91 | 80.531 | 56/35 | -269.000 | 242.000 | -91.000 | 37 | 10 | 0 |
| 6 | `reduce_geometry_plus_collapse_drawdown_lte_18_p_hold_ge_060` | 91 | 80.531 | 56/35 | -269.000 | 242.000 | -91.000 | 37 | 10 | 0 |
| 7 | `reduce_geometry_plus_collapse_drawdown_lte_8` | 91 | 80.531 | 56/35 | -341.000 | 170.000 | -91.000 | 37 | 9 | 0 |
| 8 | `reduce_geometry_plus_collapse_drawdown_lte_10` | 91 | 80.531 | 56/35 | -341.000 | 170.000 | -91.000 | 37 | 9 | 0 |
| 9 | `reduce_geometry_only` | 91 | 80.531 | 56/35 | -395.000 | 116.000 | -91.000 | 37 | 6 | 0 |
| 10 | `current_exit_policy` | 91 | 80.531 | 56/35 | -511.000 | 0.000 | -91.000 | 37 | 0 | 0 |

### lead_all_sources

| rank | policy | settled | coverage | dir W/L | candidate c | delta c | hold c | matched | suppressed | neg winners |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `reduce_geometry_plus_collapse_drawdown_lte_12` | 91 | 80.531 | 60/31 | 203.000 | 610.000 | 113.000 | 42 | 11 | 1 |
| 2 | `reduce_geometry_plus_collapse_drawdown_lte_15` | 91 | 80.531 | 60/31 | 203.000 | 610.000 | 113.000 | 42 | 11 | 1 |
| 3 | `reduce_geometry_plus_collapse_drawdown_lte_18` | 91 | 80.531 | 60/31 | 203.000 | 610.000 | 113.000 | 42 | 11 | 1 |
| 4 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_055` | 91 | 80.531 | 60/31 | 203.000 | 610.000 | 113.000 | 42 | 11 | 1 |
| 5 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_060` | 91 | 80.531 | 60/31 | -47.000 | 360.000 | 113.000 | 42 | 9 | 2 |
| 6 | `reduce_geometry_plus_collapse_drawdown_lte_18_p_hold_ge_060` | 91 | 80.531 | 60/31 | -47.000 | 360.000 | 113.000 | 42 | 9 | 2 |
| 7 | `reduce_geometry_plus_collapse_drawdown_lte_8` | 91 | 80.531 | 60/31 | -119.000 | 288.000 | 113.000 | 42 | 8 | 2 |
| 8 | `reduce_geometry_plus_collapse_drawdown_lte_10` | 91 | 80.531 | 60/31 | -119.000 | 288.000 | 113.000 | 42 | 8 | 2 |
| 9 | `reduce_geometry_only` | 91 | 80.531 | 60/31 | -343.000 | 64.000 | 113.000 | 42 | 5 | 2 |
| 10 | `current_exit_policy` | 91 | 80.531 | 60/31 | -407.000 | 0.000 | 113.000 | 42 | 0 | 2 |

### lead_first_market_only

| rank | policy | settled | coverage | dir W/L | candidate c | delta c | hold c | matched | suppressed | neg winners |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `reduce_geometry_plus_collapse_drawdown_lte_12` | 91 | 80.531 | 60/31 | 203.000 | 610.000 | 113.000 | 42 | 11 | 1 |
| 2 | `reduce_geometry_plus_collapse_drawdown_lte_15` | 91 | 80.531 | 60/31 | 203.000 | 610.000 | 113.000 | 42 | 11 | 1 |
| 3 | `reduce_geometry_plus_collapse_drawdown_lte_18` | 91 | 80.531 | 60/31 | 203.000 | 610.000 | 113.000 | 42 | 11 | 1 |
| 4 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_055` | 91 | 80.531 | 60/31 | 203.000 | 610.000 | 113.000 | 42 | 11 | 1 |
| 5 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_060` | 91 | 80.531 | 60/31 | -47.000 | 360.000 | 113.000 | 42 | 9 | 2 |
| 6 | `reduce_geometry_plus_collapse_drawdown_lte_18_p_hold_ge_060` | 91 | 80.531 | 60/31 | -47.000 | 360.000 | 113.000 | 42 | 9 | 2 |
| 7 | `reduce_geometry_plus_collapse_drawdown_lte_8` | 91 | 80.531 | 60/31 | -119.000 | 288.000 | 113.000 | 42 | 8 | 2 |
| 8 | `reduce_geometry_plus_collapse_drawdown_lte_10` | 91 | 80.531 | 60/31 | -119.000 | 288.000 | 113.000 | 42 | 8 | 2 |
| 9 | `reduce_geometry_only` | 91 | 80.531 | 60/31 | -343.000 | 64.000 | 113.000 | 42 | 5 | 2 |
| 10 | `current_exit_policy` | 91 | 80.531 | 60/31 | -407.000 | 0.000 | 113.000 | 42 | 0 | 2 |

### lead_approved_preferred

| rank | policy | settled | coverage | dir W/L | candidate c | delta c | hold c | matched | suppressed | neg winners |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `reduce_geometry_plus_collapse_drawdown_lte_12` | 91 | 80.531 | 60/31 | 203.000 | 610.000 | 113.000 | 42 | 11 | 1 |
| 2 | `reduce_geometry_plus_collapse_drawdown_lte_15` | 91 | 80.531 | 60/31 | 203.000 | 610.000 | 113.000 | 42 | 11 | 1 |
| 3 | `reduce_geometry_plus_collapse_drawdown_lte_18` | 91 | 80.531 | 60/31 | 203.000 | 610.000 | 113.000 | 42 | 11 | 1 |
| 4 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_055` | 91 | 80.531 | 60/31 | 203.000 | 610.000 | 113.000 | 42 | 11 | 1 |
| 5 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_060` | 91 | 80.531 | 60/31 | -47.000 | 360.000 | 113.000 | 42 | 9 | 2 |
| 6 | `reduce_geometry_plus_collapse_drawdown_lte_18_p_hold_ge_060` | 91 | 80.531 | 60/31 | -47.000 | 360.000 | 113.000 | 42 | 9 | 2 |
| 7 | `reduce_geometry_plus_collapse_drawdown_lte_8` | 91 | 80.531 | 60/31 | -119.000 | 288.000 | 113.000 | 42 | 8 | 2 |
| 8 | `reduce_geometry_plus_collapse_drawdown_lte_10` | 91 | 80.531 | 60/31 | -119.000 | 288.000 | 113.000 | 42 | 8 | 2 |
| 9 | `reduce_geometry_only` | 91 | 80.531 | 60/31 | -343.000 | 64.000 | 113.000 | 42 | 5 | 2 |
| 10 | `current_exit_policy` | 91 | 80.531 | 60/31 | -407.000 | 0.000 | 113.000 | 42 | 0 | 2 |

### lead_approved_only

| rank | policy | settled | coverage | dir W/L | candidate c | delta c | hold c | matched | suppressed | neg winners |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `reduce_geometry_plus_collapse_drawdown_lte_18` | 70 | 61.947 | 62/8 | 1049.000 | 728.000 | 705.000 | 70 | 17 | 11 |
| 2 | `reduce_geometry_plus_collapse_drawdown_lte_12` | 70 | 61.947 | 62/8 | 929.000 | 608.000 | 705.000 | 70 | 14 | 13 |
| 3 | `reduce_geometry_plus_collapse_drawdown_lte_15` | 70 | 61.947 | 62/8 | 873.000 | 552.000 | 705.000 | 70 | 16 | 12 |
| 4 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_055` | 70 | 61.947 | 62/8 | 873.000 | 552.000 | 705.000 | 70 | 16 | 12 |
| 5 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_060` | 70 | 61.947 | 62/8 | 623.000 | 302.000 | 705.000 | 70 | 14 | 14 |
| 6 | `reduce_geometry_plus_collapse_drawdown_lte_18_p_hold_ge_060` | 70 | 61.947 | 62/8 | 623.000 | 302.000 | 705.000 | 70 | 14 | 14 |
| 7 | `reduce_geometry_plus_collapse_drawdown_lte_8` | 70 | 61.947 | 62/8 | 607.000 | 286.000 | 705.000 | 70 | 11 | 16 |
| 8 | `reduce_geometry_plus_collapse_drawdown_lte_10` | 70 | 61.947 | 62/8 | 607.000 | 286.000 | 705.000 | 70 | 11 | 16 |
| 9 | `reduce_geometry_only` | 70 | 61.947 | 62/8 | 497.000 | 176.000 | 705.000 | 70 | 7 | 18 |
| 10 | `current_exit_policy` | 70 | 61.947 | 62/8 | 321.000 | 0.000 | 705.000 | 70 | 0 | 24 |

## post_freeze_candidate


### lead_all_sources

| rank | policy | settled | coverage | dir W/L | candidate c | delta c | hold c | matched | suppressed | neg winners |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `reduce_geometry_plus_collapse_drawdown_lte_12` | 75 | 80.645 | 47/28 | -447.000 | 318.000 | -93.000 | 29 | 7 | 1 |
| 2 | `reduce_geometry_plus_collapse_drawdown_lte_15` | 75 | 80.645 | 47/28 | -447.000 | 318.000 | -93.000 | 29 | 7 | 1 |
| 3 | `reduce_geometry_plus_collapse_drawdown_lte_18` | 75 | 80.645 | 47/28 | -447.000 | 318.000 | -93.000 | 29 | 7 | 1 |
| 4 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_055` | 75 | 80.645 | 47/28 | -447.000 | 318.000 | -93.000 | 29 | 7 | 1 |
| 5 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_060` | 75 | 80.645 | 47/28 | -599.000 | 166.000 | -93.000 | 29 | 6 | 2 |
| 6 | `reduce_geometry_plus_collapse_drawdown_lte_18_p_hold_ge_060` | 75 | 80.645 | 47/28 | -599.000 | 166.000 | -93.000 | 29 | 6 | 2 |
| 7 | `reduce_geometry_plus_collapse_drawdown_lte_8` | 75 | 80.645 | 47/28 | -689.000 | 76.000 | -93.000 | 29 | 5 | 2 |
| 8 | `reduce_geometry_plus_collapse_drawdown_lte_10` | 75 | 80.645 | 47/28 | -689.000 | 76.000 | -93.000 | 29 | 5 | 2 |
| 9 | `current_exit_policy` | 75 | 80.645 | 47/28 | -765.000 | 0.000 | -93.000 | 29 | 0 | 2 |
| 10 | `reduce_geometry_only` | 75 | 80.645 | 47/28 | -815.000 | -50.000 | -93.000 | 29 | 3 | 2 |

### lead_first_market_only

| rank | policy | settled | coverage | dir W/L | candidate c | delta c | hold c | matched | suppressed | neg winners |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `reduce_geometry_plus_collapse_drawdown_lte_12` | 75 | 80.645 | 47/28 | -447.000 | 318.000 | -93.000 | 29 | 7 | 1 |
| 2 | `reduce_geometry_plus_collapse_drawdown_lte_15` | 75 | 80.645 | 47/28 | -447.000 | 318.000 | -93.000 | 29 | 7 | 1 |
| 3 | `reduce_geometry_plus_collapse_drawdown_lte_18` | 75 | 80.645 | 47/28 | -447.000 | 318.000 | -93.000 | 29 | 7 | 1 |
| 4 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_055` | 75 | 80.645 | 47/28 | -447.000 | 318.000 | -93.000 | 29 | 7 | 1 |
| 5 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_060` | 75 | 80.645 | 47/28 | -599.000 | 166.000 | -93.000 | 29 | 6 | 2 |
| 6 | `reduce_geometry_plus_collapse_drawdown_lte_18_p_hold_ge_060` | 75 | 80.645 | 47/28 | -599.000 | 166.000 | -93.000 | 29 | 6 | 2 |
| 7 | `reduce_geometry_plus_collapse_drawdown_lte_8` | 75 | 80.645 | 47/28 | -689.000 | 76.000 | -93.000 | 29 | 5 | 2 |
| 8 | `reduce_geometry_plus_collapse_drawdown_lte_10` | 75 | 80.645 | 47/28 | -689.000 | 76.000 | -93.000 | 29 | 5 | 2 |
| 9 | `current_exit_policy` | 75 | 80.645 | 47/28 | -765.000 | 0.000 | -93.000 | 29 | 0 | 2 |
| 10 | `reduce_geometry_only` | 75 | 80.645 | 47/28 | -815.000 | -50.000 | -93.000 | 29 | 3 | 2 |

### lead_approved_preferred

| rank | policy | settled | coverage | dir W/L | candidate c | delta c | hold c | matched | suppressed | neg winners |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `reduce_geometry_plus_collapse_drawdown_lte_12` | 75 | 80.645 | 47/28 | -447.000 | 318.000 | -93.000 | 29 | 7 | 1 |
| 2 | `reduce_geometry_plus_collapse_drawdown_lte_15` | 75 | 80.645 | 47/28 | -447.000 | 318.000 | -93.000 | 29 | 7 | 1 |
| 3 | `reduce_geometry_plus_collapse_drawdown_lte_18` | 75 | 80.645 | 47/28 | -447.000 | 318.000 | -93.000 | 29 | 7 | 1 |
| 4 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_055` | 75 | 80.645 | 47/28 | -447.000 | 318.000 | -93.000 | 29 | 7 | 1 |
| 5 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_060` | 75 | 80.645 | 47/28 | -599.000 | 166.000 | -93.000 | 29 | 6 | 2 |
| 6 | `reduce_geometry_plus_collapse_drawdown_lte_18_p_hold_ge_060` | 75 | 80.645 | 47/28 | -599.000 | 166.000 | -93.000 | 29 | 6 | 2 |
| 7 | `reduce_geometry_plus_collapse_drawdown_lte_8` | 75 | 80.645 | 47/28 | -689.000 | 76.000 | -93.000 | 29 | 5 | 2 |
| 8 | `reduce_geometry_plus_collapse_drawdown_lte_10` | 75 | 80.645 | 47/28 | -689.000 | 76.000 | -93.000 | 29 | 5 | 2 |
| 9 | `current_exit_policy` | 75 | 80.645 | 47/28 | -765.000 | 0.000 | -93.000 | 29 | 0 | 2 |
| 10 | `reduce_geometry_only` | 75 | 80.645 | 47/28 | -815.000 | -50.000 | -93.000 | 29 | 3 | 2 |

### lead_reconstructed_only

| rank | policy | settled | coverage | dir W/L | candidate c | delta c | hold c | matched | suppressed | neg winners |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `reduce_geometry_plus_collapse_drawdown_lte_12` | 75 | 80.645 | 44/31 | -435.000 | 110.000 | -135.000 | 23 | 5 | 0 |
| 2 | `reduce_geometry_plus_collapse_drawdown_lte_15` | 75 | 80.645 | 44/31 | -435.000 | 110.000 | -135.000 | 23 | 5 | 0 |
| 3 | `reduce_geometry_plus_collapse_drawdown_lte_18` | 75 | 80.645 | 44/31 | -435.000 | 110.000 | -135.000 | 23 | 5 | 0 |
| 4 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_055` | 75 | 80.645 | 44/31 | -435.000 | 110.000 | -135.000 | 23 | 5 | 0 |
| 5 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_060` | 75 | 80.645 | 44/31 | -435.000 | 110.000 | -135.000 | 23 | 5 | 0 |
| 6 | `reduce_geometry_plus_collapse_drawdown_lte_18_p_hold_ge_060` | 75 | 80.645 | 44/31 | -435.000 | 110.000 | -135.000 | 23 | 5 | 0 |
| 7 | `reduce_geometry_plus_collapse_drawdown_lte_8` | 75 | 80.645 | 44/31 | -525.000 | 20.000 | -135.000 | 23 | 4 | 0 |
| 8 | `reduce_geometry_plus_collapse_drawdown_lte_10` | 75 | 80.645 | 44/31 | -525.000 | 20.000 | -135.000 | 23 | 4 | 0 |
| 9 | `current_exit_policy` | 75 | 80.645 | 44/31 | -545.000 | 0.000 | -135.000 | 23 | 0 | 0 |
| 10 | `reduce_geometry_only` | 75 | 80.645 | 44/31 | -595.000 | -50.000 | -135.000 | 23 | 3 | 0 |

### lead_approved_only

| rank | policy | settled | coverage | dir W/L | candidate c | delta c | hold c | matched | suppressed | neg winners |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `reduce_geometry_plus_collapse_drawdown_lte_18` | 51 | 54.839 | 46/5 | 739.000 | 498.000 | 552.000 | 51 | 11 | 8 |
| 2 | `reduce_geometry_plus_collapse_drawdown_lte_12` | 51 | 54.839 | 46/5 | 619.000 | 378.000 | 552.000 | 51 | 8 | 10 |
| 3 | `reduce_geometry_plus_collapse_drawdown_lte_15` | 51 | 54.839 | 46/5 | 563.000 | 322.000 | 552.000 | 51 | 10 | 9 |
| 4 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_055` | 51 | 54.839 | 46/5 | 563.000 | 322.000 | 552.000 | 51 | 10 | 9 |
| 5 | `reduce_geometry_plus_collapse_drawdown_lte_15_p_hold_ge_060` | 51 | 54.839 | 46/5 | 411.000 | 170.000 | 552.000 | 51 | 9 | 10 |
| 6 | `reduce_geometry_plus_collapse_drawdown_lte_18_p_hold_ge_060` | 51 | 54.839 | 46/5 | 411.000 | 170.000 | 552.000 | 51 | 9 | 10 |
| 7 | `reduce_geometry_plus_collapse_drawdown_lte_8` | 51 | 54.839 | 46/5 | 377.000 | 136.000 | 552.000 | 51 | 6 | 12 |
| 8 | `reduce_geometry_plus_collapse_drawdown_lte_10` | 51 | 54.839 | 46/5 | 377.000 | 136.000 | 552.000 | 51 | 6 | 12 |
| 9 | `reduce_geometry_only` | 51 | 54.839 | 46/5 | 251.000 | 10.000 | 552.000 | 51 | 4 | 13 |
| 10 | `current_exit_policy` | 51 | 54.839 | 46/5 | 241.000 | 0.000 | 552.000 | 51 | 0 | 16 |
