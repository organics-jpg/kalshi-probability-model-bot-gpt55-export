# v28 Frozen Exit Reduce Geometry Suppression

Research-only; no live bot changes and no orders.

- Freeze timestamp UTC: `2026-05-06T14:49:54.002173+00:00`
- Candidate: `side_geometry_suppress_reduce_p_hold_ge_075`
- Rule: `Suppress mushroom_v28_probability_reduce only when p_hold >= 0.75 and fair_drawdown sign agrees with held side: YES drawdown >= 0, NO drawdown <= 0.`
- Future rows/settled: `70/70`
- Current/candidate gross: `492.000c/448.000c`
- Delta vs current: `-44.000c`
- Blockers: `delta_not_positive, suppressed_losers_present`

## Interpretation

- Frozen geometry suppression has 70 settled rows after freeze.
- Delta versus current v28 exits is -44.0c.
- Suppressed exits: 3; winners 2, losers 1.
- Base p_hold suppression is included as a post-geometry-freeze counterfactual; geometry is not validated until it fires and beats that baseline on forward rows.

## Post-Freeze Counterfactual Policies

| policy | settled | candidate c | delta c | W/L | suppressed | suppressed W/L | winner recovery c | loss cost c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `base_suppress_reduce_p_hold_ge_075` | 70 | 412.000 | -80.000 | 51/19 | 10 | 7/3 | 344.000 | -424.000 |
| `side_geometry_suppress_reduce_p_hold_ge_075` | 70 | 448.000 | -44.000 | 47/23 | 3 | 2/1 | 114.000 | -158.000 |

## Rows

| market | side | result | p_hold | drawdown | current c | hold c | candidate c | delta c | suppressed |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY061100-00` | `no` | `no` | None | None | 38.000 | 38.000 | 38.000 | 0.000 | False |
| `KXBTC15M-26MAY061130-30` | `yes` | `yes` | None | None | 40.000 | 40.000 | 40.000 | 0.000 | False |
| `KXBTC15M-26MAY061200-00` | `yes` | `yes` | 0.889 | -7.930 | 16.000 | 36.000 | 16.000 | 0.000 | False |
| `KXBTC15M-26MAY061300-00` | `yes` | `no` | 0.666 | 13.357 | -30.000 | -160.000 | -30.000 | 0.000 | False |
| `KXBTC15M-26MAY061400-00` | `no` | `no` | 0.738 | 15.202 | -10.000 | 22.000 | -10.000 | 0.000 | False |
| `KXBTC15M-26MAY061415-15` | `no` | `no` | None | None | 24.000 | 24.000 | 24.000 | 0.000 | False |
| `KXBTC15M-26MAY061445-45` | `no` | `no` | 0.798 | 8.217 | -22.000 | 24.000 | -22.000 | 0.000 | False |
| `KXBTC15M-26MAY061445-45` | `no` | `no` | 0.982 | -8.199 | 18.000 | 20.000 | 18.000 | 0.000 | False |
| `KXBTC15M-26MAY061545-45` | `yes` | `yes` | 0.935 | -9.541 | 22.000 | 32.000 | 22.000 | 0.000 | False |
| `KXBTC15M-26MAY061615-15` | `yes` | `yes` | 0.931 | -3.122 | 8.000 | 20.000 | 8.000 | 0.000 | False |
| `KXBTC15M-26MAY061645-45` | `no` | `no` | None | None | 48.000 | 48.000 | 48.000 | 0.000 | False |
| `KXBTC15M-26MAY061800-00` | `no` | `no` | 0.553 | 11.739 | -86.000 | 66.000 | -86.000 | 0.000 | False |
| `KXBTC15M-26MAY061815-15` | `no` | `no` | 0.951 | -11.068 | 24.000 | 32.000 | 24.000 | 0.000 | False |
| `KXBTC15M-26MAY061830-30` | `no` | `no` | 0.977 | -8.672 | 20.000 | 22.000 | 20.000 | 0.000 | False |
| `KXBTC15M-26MAY061900-00` | `yes` | `yes` | None | None | 20.000 | 20.000 | 20.000 | 0.000 | False |
| `KXBTC15M-26MAY061915-15` | `no` | `no` | 0.982 | -11.199 | 24.000 | 26.000 | 24.000 | 0.000 | False |
| `KXBTC15M-26MAY062015-15` | `no` | `no` | 0.269 | 15.107 | -60.000 | 116.000 | -60.000 | 0.000 | False |
| `KXBTC15M-26MAY062015-15` | `yes` | `no` | 0.812 | 4.764 | 8.000 | -172.000 | 8.000 | 0.000 | False |
| `KXBTC15M-26MAY062015-15` | `yes` | `no` | None | None | -134.000 | -134.000 | -134.000 | 0.000 | False |
| `KXBTC15M-26MAY062030-30` | `no` | `no` | 0.661 | 0.852 | 32.000 | 66.000 | 32.000 | 0.000 | False |
| `KXBTC15M-26MAY062045-45` | `no` | `no` | 0.891 | -9.139 | 24.000 | 40.000 | 24.000 | 0.000 | False |
| `KXBTC15M-26MAY062100-00` | `yes` | `yes` | 0.648 | 18.241 | -4.000 | 34.000 | -4.000 | 0.000 | False |
| `KXBTC15M-26MAY062100-00` | `yes` | `yes` | 0.664 | 17.631 | -20.000 | 32.000 | -20.000 | 0.000 | False |
| `KXBTC15M-26MAY062100-00` | `yes` | `yes` | 0.489 | 12.077 | 14.000 | 78.000 | 14.000 | 0.000 | False |
| `KXBTC15M-26MAY062115-15` | `yes` | `yes` | 0.396 | 33.425 | -12.000 | 54.000 | -12.000 | 0.000 | False |
| `KXBTC15M-26MAY062115-15` | `no` | `yes` | 0.456 | 14.422 | -34.000 | -138.000 | -34.000 | 0.000 | False |
| `KXBTC15M-26MAY062115-15` | `yes` | `yes` | 0.982 | -10.246 | 22.000 | 24.000 | 22.000 | 0.000 | False |
| `KXBTC15M-26MAY062130-30` | `no` | `yes` | 0.768 | 6.159 | -32.000 | -152.000 | -32.000 | 0.000 | False |
| `KXBTC15M-26MAY062215-15` | `no` | `no` | 0.708 | -5.825 | 14.000 | 70.000 | 14.000 | 0.000 | False |
| `KXBTC15M-26MAY062215-15` | `no` | `no` | 0.861 | -2.067 | 10.000 | 32.000 | 10.000 | 0.000 | False |
| `KXBTC15M-26MAY062245-45` | `yes` | `yes` | 0.644 | 15.619 | 8.000 | 28.000 | 8.000 | 0.000 | False |
| `KXBTC15M-26MAY062300-00` | `yes` | `yes` | 0.746 | 10.363 | 16.000 | 26.000 | 16.000 | 0.000 | False |
| `KXBTC15M-26MAY062315-15` | `no` | `no` | 0.811 | 2.882 | 6.000 | 32.000 | 6.000 | 0.000 | False |
| `KXBTC15M-26MAY070000-00` | `no` | `no` | 0.727 | 5.330 | 2.000 | 44.000 | 2.000 | 0.000 | False |
| `KXBTC15M-26MAY070015-15` | `no` | `yes` | 0.597 | 10.344 | -2.000 | -140.000 | -2.000 | 0.000 | False |
| `KXBTC15M-26MAY070030-30` | `yes` | `yes` | 0.922 | -10.178 | 30.000 | 36.000 | 30.000 | 0.000 | False |
| `KXBTC15M-26MAY070115-15` | `yes` | `yes` | 0.680 | 18.038 | 0.000 | 36.000 | 0.000 | 0.000 | False |
| `KXBTC15M-26MAY070545-45` | `no` | `no` | 0.893 | -7.257 | 18.000 | 36.000 | 18.000 | 0.000 | False |
| `KXBTC15M-26MAY070645-45` | `yes` | `yes` | None | None | 38.000 | 38.000 | 38.000 | 0.000 | False |
| `KXBTC15M-26MAY070745-45` | `yes` | `yes` | 0.822 | -14.170 | 34.000 | 64.000 | 34.000 | 0.000 | False |
| `KXBTC15M-26MAY070815-15` | `yes` | `yes` | 0.890 | -1.046 | 2.000 | 20.000 | 2.000 | 0.000 | False |
| `KXBTC15M-26MAY070830-30` | `no` | `no` | 0.825 | -0.535 | 18.000 | 36.000 | 18.000 | 0.000 | False |
| `KXBTC15M-26MAY070830-30` | `no` | `no` | 0.613 | 15.700 | -14.000 | 46.000 | -14.000 | 0.000 | False |
| `KXBTC15M-26MAY070830-30` | `no` | `no` | None | None | 46.000 | 46.000 | 46.000 | 0.000 | False |
| `KXBTC15M-26MAY070915-15` | `no` | `no` | None | None | 46.000 | 46.000 | 46.000 | 0.000 | False |
| `KXBTC15M-26MAY070930-30` | `yes` | `yes` | 0.970 | -14.000 | 34.000 | 40.000 | 34.000 | 0.000 | False |
| `KXBTC15M-26MAY070945-45` | `no` | `no` | None | None | 62.000 | 62.000 | 62.000 | 0.000 | False |
| `KXBTC15M-26MAY071000-00` | `no` | `no` | 0.618 | 11.242 | -36.000 | 54.000 | -36.000 | 0.000 | False |
| `KXBTC15M-26MAY071000-00` | `no` | `no` | 0.781 | 6.864 | 16.000 | 58.000 | 16.000 | 0.000 | False |
| `KXBTC15M-26MAY071015-15` | `no` | `yes` | 0.789 | -0.913 | 2.000 | -156.000 | -156.000 | -158.000 | True |
| `KXBTC15M-26MAY071015-15` | `no` | `yes` | 0.764 | 4.602 | -16.000 | -162.000 | -16.000 | 0.000 | False |
| `KXBTC15M-26MAY071015-15` | `yes` | `yes` | 0.923 | -8.310 | 20.000 | 32.000 | 20.000 | 0.000 | False |
| `KXBTC15M-26MAY071030-30` | `no` | `no` | 0.710 | 6.017 | -24.000 | 46.000 | -24.000 | 0.000 | False |
| `KXBTC15M-26MAY071030-30` | `no` | `no` | None | None | 48.000 | 48.000 | 48.000 | 0.000 | False |
| `KXBTC15M-26MAY071045-45` | `no` | `no` | 0.761 | -2.053 | -10.000 | 52.000 | 52.000 | 62.000 | True |
| `KXBTC15M-26MAY071045-45` | `no` | `no` | None | None | 50.000 | 50.000 | 50.000 | 0.000 | False |
| `KXBTC15M-26MAY071100-00` | `yes` | `no` | 0.837 | -0.675 | 4.000 | -166.000 | 4.000 | 0.000 | False |
| `KXBTC15M-26MAY071115-15` | `yes` | `yes` | 0.889 | -4.884 | 14.000 | 32.000 | 14.000 | 0.000 | False |
| `KXBTC15M-26MAY071130-30` | `no` | `no` | None | None | 30.000 | 30.000 | 30.000 | 0.000 | False |
| `KXBTC15M-26MAY071145-45` | `yes` | `yes` | 0.982 | -17.215 | 44.000 | 46.000 | 44.000 | 0.000 | False |
| `KXBTC15M-26MAY071200-00` | `no` | `no` | 0.961 | -19.117 | 42.000 | 46.000 | 42.000 | 0.000 | False |
| `KXBTC15M-26MAY071215-15` | `no` | `no` | 0.798 | 4.234 | -16.000 | 32.000 | -16.000 | 0.000 | False |
| `KXBTC15M-26MAY071215-15` | `no` | `no` | 0.752 | 2.770 | 2.000 | 44.000 | 2.000 | 0.000 | False |
| `KXBTC15M-26MAY071215-15` | `no` | `no` | 0.766 | 3.418 | -8.000 | 40.000 | -8.000 | 0.000 | False |
| `KXBTC15M-26MAY071230-30` | `yes` | `yes` | 0.749 | 2.062 | -10.000 | 46.000 | -10.000 | 0.000 | False |
| `KXBTC15M-26MAY071230-30` | `yes` | `yes` | 0.663 | 17.710 | -38.000 | 32.000 | -38.000 | 0.000 | False |
| `KXBTC15M-26MAY071230-30` | `yes` | `yes` | None | None | 40.000 | 40.000 | 40.000 | 0.000 | False |
| `KXBTC15M-26MAY071315-15` | `yes` | `yes` | 0.798 | -0.834 | -6.000 | 40.000 | -6.000 | 0.000 | False |
| `KXBTC15M-26MAY071315-15` | `yes` | `yes` | 0.784 | 2.583 | -14.000 | 38.000 | 38.000 | 52.000 | True |
| `KXBTC15M-26MAY071315-15` | `yes` | `yes` | 0.927 | -14.750 | 32.000 | 44.000 | 32.000 | 0.000 | False |
