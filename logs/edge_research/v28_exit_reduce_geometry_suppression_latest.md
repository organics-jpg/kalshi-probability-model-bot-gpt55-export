# v28 Exit Reduce Geometry Suppression

Research-only; no live bot changes and no orders.

## Current Read

- Best policy is side_geometry_suppress_reduce_p_hold_ge_075 with delta 625.0c on 132 settled rows.
- Geometry gate tests whether suppressing probability_reduce should require side-consistent fair-drawdown sign.
- This is diagnostic only; promotion would require frozen forward validation and source-quality checks.

## Policies

| policy | settled | candidate c | delta c | W/L | suppressed | suppressed W/L | winner recovery c | loss cost c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `side_geometry_suppress_reduce_p_hold_ge_075` | 132 | 1346.000 | 625.000 | 86/46 | 15 | 14/1 | 783.000 | -158.000 |
| `yes_only_geometry_suppress_reduce_p_hold_ge_075` | 132 | 1203.000 | 482.000 | 82/50 | 9 | 9/0 | 482.000 | 0 |
| `base_suppress_reduce_p_hold_ge_075` | 132 | 1058.000 | 337.000 | 91/41 | 25 | 20/5 | 1067.000 | -730.000 |
| `no_only_geometry_suppress_reduce_p_hold_ge_075` | 132 | 864.000 | 143.000 | 77/55 | 6 | 5/1 | 301.000 | -158.000 |
| `current_v28` | 132 | 721.000 | 0.000 | 73/59 | 0 | 0/0 | 0 | 0 |

## Suppressed Rows By Best Policy

| market | side | result | p_hold | drawdown | current c | hold c | delta c |
|---|---|---|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY060245-45` | `yes` | `yes` | 0.793 | 2.667 | -8.000 | 40.000 | 48.000 |
| `KXBTC15M-26MAY060300-00` | `yes` | `yes` | 0.780 | 2.960 | -14.000 | 38.000 | 52.000 |
| `KXBTC15M-26MAY060300-00` | `yes` | `yes` | 0.753 | 4.684 | -22.000 | 40.000 | 62.000 |
| `KXBTC15M-26MAY060630-30` | `yes` | `yes` | 0.778 | 1.223 | -12.000 | 42.000 | 54.000 |
| `KXBTC15M-26MAY060645-45` | `yes` | `yes` | 0.799 | 2.065 | -16.000 | 36.000 | 52.000 |
| `KXBTC15M-26MAY060645-45` | `yes` | `yes` | 0.780 | 0.021 | -12.000 | 44.000 | 56.000 |
| `KXBTC15M-26MAY060915-15` | `no` | `no` | 0.794 | -9.376 | 0.000 | 60.000 | 60.000 |
| `KXBTC15M-26MAY060930-30` | `no` | `no` | 0.788 | -2.761 | -14.000 | 48.000 | 62.000 |
| `KXBTC15M-26MAY060930-30` | `no` | `no` | 0.799 | -6.918 | -3.000 | 54.000 | 57.000 |
| `KXBTC15M-26MAY061015-15` | `no` | `no` | 0.800 | -9.998 | 0.000 | 60.000 | 60.000 |
| `KXBTC15M-26MAY061030-30` | `yes` | `yes` | 0.753 | 2.726 | -16.000 | 44.000 | 60.000 |
| `KXBTC15M-26MAY061045-45` | `yes` | `yes` | 0.797 | 0.305 | -6.000 | 40.000 | 46.000 |
| `KXBTC15M-26MAY071015-15` | `no` | `yes` | 0.789 | -0.913 | 2.000 | -156.000 | -158.000 |
| `KXBTC15M-26MAY071045-45` | `no` | `no` | 0.761 | -2.053 | -10.000 | 52.000 | 62.000 |
| `KXBTC15M-26MAY071315-15` | `yes` | `yes` | 0.784 | 2.583 | -14.000 | 38.000 | 52.000 |
