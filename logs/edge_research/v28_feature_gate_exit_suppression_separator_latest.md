# v28 Feature-Gate Exit Suppression Separator

Research-only diagnostic. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:30.640111+00:00`

## Interpretation

- Diagnostic separator audit only; any rule must be frozen before it can count as forward evidence.
- All-exit suppression on these rows would be 493.76040000000006c, with 25 helpful-to-suppress and 6 harmful-to-suppress markets.
- Best deployable-like observable separator: exit_depth_avg le 437.36749999999995 selects 22 markets for 1348.96c, with helpful/harmful 20/2.
- Best oracle/diagnostic separator is theory_net_cents ge 4.0; treat it as an upper-bound contrast, not an actionable rule.
- Use the separator shape to design a frozen watch, not to justify live changes.

## Observable Candidate Separators

| feature | dir | threshold | selected | helpful/harmful | suppress delta c | omitted delta c | excluded helpful | excluded harmful |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| exit_depth_avg | le | 437.367500 | 22 | 20/2 | 1348.960000 | -855.199600 | 5 | 4 |
| exit_depth_avg | le | 432.640000 | 21 | 19/2 | 1219.960000 | -726.199600 | 6 | 4 |
| exit_depth_avg | le | 372.512500 | 18 | 17/1 | 1199.800000 | -706.039600 | 8 | 5 |
| exit_bid_min | le | 73.000000 | 19 | 16/3 | 1167.960000 | -674.199600 | 9 | 3 |
| entry_fill_avg_cents | ge | 75.333300 | 27 | 24/3 | 1127.600400 | -633.840000 | 1 | 3 |
| entry_fill_avg_cents | ge | 76.000000 | 26 | 23/3 | 1127.600200 | -633.839800 | 2 | 3 |
| exit_depth_min | le | 75.000000 | 20 | 17/3 | 1116.560000 | -622.799600 | 8 | 3 |
| exit_depth_min | le | 56.000000 | 16 | 14/2 | 1110.360000 | -616.599600 | 11 | 4 |
| entry_fill_avg_cents | ge | 79.333333 | 17 | 16/1 | 1072.200200 | -578.439800 | 9 | 5 |
| exit_depth_avg | le | 342.340000 | 17 | 16/1 | 1048.200000 | -554.439600 | 9 | 5 |
| exit_depth_min | le | 55.000000 | 15 | 13/2 | 1043.360000 | -549.599600 | 12 | 4 |
| exit_depth_avg | le | 427.606667 | 20 | 18/2 | 1041.960000 | -548.199600 | 7 | 4 |
| exit_depth_min | le | 71.000000 | 19 | 16/3 | 1040.360000 | -546.599600 | 9 | 3 |
| entry_fill_avg_cents | ge | 77.333333 | 22 | 20/2 | 1036.600200 | -542.839800 | 5 | 4 |
| exit_p_hold_max | ge | 0.854162 | 9 | 9/0 | 1020.600000 | -526.839600 | 16 | 6 |
| exit_hold_net_max | ge | 84.416204 | 9 | 9/0 | 1020.600000 | -526.839600 | 16 | 6 |
| exit_bid_max | ge | 87.000000 | 9 | 9/0 | 1020.600000 | -526.839600 | 16 | 6 |
| exit_depth_avg | le | 311.160000 | 16 | 15/1 | 1016.200000 | -522.439600 | 10 | 5 |
| entry_fill_avg_cents | ge | 73.500000 | 29 | 25/4 | 999.600400 | -505.840000 | 0 | 2 |
| exit_p_hold_min | le | 0.762968 | 15 | 13/2 | 988.960000 | -495.199600 | 12 | 4 |
| exit_hold_net_min | le | 75.296813 | 15 | 13/2 | 988.960000 | -495.199600 | 12 | 4 |
| exit_depth_avg | le | 1464.815000 | 27 | 23/4 | 969.760000 | -475.999600 | 2 | 2 |
| entry_fill_avg_cents | ge | 77.750000 | 21 | 19/2 | 968.600200 | -474.839800 | 6 | 4 |
| exit_bid_min | le | 75.000000 | 22 | 18/4 | 963.160000 | -469.399600 | 7 | 2 |
| exit_fair_drawdown_max | ge | 1.091627 | 19 | 16/3 | 961.160000 | -467.399600 | 9 | 3 |
| exit_bid_min | ge | 56.000000 | 27 | 23/4 | 955.600000 | -461.839600 | 2 | 2 |
| exit_bid_avg | ge | 66.000000 | 27 | 23/4 | 955.600000 | -461.839600 | 2 | 2 |
| exit_depth_min | le | 50.000000 | 14 | 12/2 | 955.360000 | -461.599600 | 13 | 4 |
| exit_depth_avg | le | 388.375000 | 19 | 17/2 | 953.960000 | -460.199600 | 8 | 4 |
| entry_fill_avg_cents | ge | 76.500000 | 24 | 21/3 | 950.600200 | -456.839800 | 4 | 3 |
| entry_fill_avg_cents | ge | 80.000000 | 16 | 15/1 | 945.200200 | -451.439800 | 10 | 5 |
| selected_side_qty | ge | 6.000000 | 19 | 17/2 | 942.200400 | -448.440000 | 8 | 4 |
| exit_depth_avg | le | 298.166667 | 15 | 14/1 | 940.000000 | -446.239600 | 11 | 5 |
| exit_bid_min | ge | 60.000000 | 25 | 22/3 | 935.600000 | -441.839600 | 3 | 3 |
| exit_p_hold_min | ge | 0.641818 | 26 | 22/4 | 930.600000 | -436.839600 | 3 | 2 |
| exit_hold_net_min | ge | 63.181766 | 26 | 22/4 | 930.600000 | -436.839600 | 3 | 2 |
| exit_bid_min | le | 70.000000 | 17 | 14/3 | 915.960000 | -422.199600 | 11 | 3 |
| exit_depth_avg | le | 1347.845000 | 26 | 22/4 | 901.760000 | -407.999600 | 3 | 2 |
| entry_fill_avg_cents | ge | 77.000000 | 23 | 20/3 | 884.600200 | -390.839800 | 5 | 3 |
| exit_p_hold_max | ge | 0.876020 | 8 | 8/0 | 876.600000 | -382.839600 | 17 | 6 |

## Oracle/Diagnostic Separators

| feature | dir | threshold | selected | helpful/harmful | suppress delta c | omitted delta c | excluded helpful | excluded harmful |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| theory_net_cents | ge | 4.000000 | 25 | 25/0 | 2317.600400 | -1823.840000 | 0 | 6 |
| theory_net_cents | ge | 9.000000 | 24 | 24/0 | 2311.200400 | -1817.440000 | 1 | 6 |
| theory_net_cents | ge | 10.000000 | 22 | 22/0 | 2303.200200 | -1809.439800 | 3 | 6 |
| theory_net_cents | ge | 14.000000 | 21 | 21/0 | 2271.200200 | -1777.439800 | 4 | 6 |
| theory_net_cents | ge | 15.000000 | 20 | 20/0 | 2205.200200 | -1711.439800 | 5 | 6 |
| theory_net_cents | ge | -15.000000 | 26 | 25/1 | 2057.600400 | -1563.840000 | 0 | 5 |
| theory_net_cents | ge | -68.000000 | 27 | 25/2 | 1905.600400 | -1411.840000 | 0 | 4 |
| theory_net_cents | ge | 16.000000 | 18 | 18/0 | 1858.200200 | -1364.439800 | 7 | 6 |
| theory_net_cents | ge | 17.000000 | 17 | 17/0 | 1782.000200 | -1288.239800 | 8 | 6 |
| theory_net_cents | ge | 18.000000 | 16 | 16/0 | 1674.000200 | -1180.239800 | 9 | 6 |
| theory_net_cents | ge | -72.000000 | 28 | 25/3 | 1659.760400 | -1166.000000 | 0 | 3 |
| theory_net_cents | ge | 20.000000 | 15 | 15/0 | 1545.000200 | -1051.239800 | 10 | 6 |

## Rows

| market | source | side | won | suppress helps | suppress delta c | theory c | entry | exit | p_hold avg | drawdown avg | hold net avg | reason shares |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | True | 280.000000 | 27.000000 | 80.000000 | 72.000000 | 0.785148 | -0.736993 | 77.514771 | {'reduce': 0.6770833333333334, 'value': 0.20833333333333334, 'collapse': 0.11458333333333333} |
| KXBTC15M-26MAY070030-30 | approved_entry | yes | True | True | 178.000000 | 15.000000 | 84.333333 | 70.333333 | 0.784403 | 7.059752 | 77.440248 | {'reduce': 0.0, 'value': 0.7380952380952381, 'collapse': 0.2619047619047619} |
| KXBTC15M-26MAY062315-15 | approved_entry | no | True | True | 169.000000 | 15.000000 | 80.666667 | 71.833333 | 0.781109 | 2.489140 | 77.110860 | {'reduce': 1.0, 'value': 0.0, 'collapse': 0.0} |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | True | 151.600000 | 20.000000 | 79.000000 | 81.050000 | 0.826012 | -3.601238 | 81.601238 | {'reduce': 0.7558139534883721, 'value': 0.2441860465116279, 'collapse': 0.0} |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | True | 144.000000 | 21.000000 | 81.666667 | 76.000000 | 0.798596 | 2.140356 | 78.859644 | {'reduce': 0.8461538461538461, 'value': 0.15384615384615385, 'collapse': 0.0} |
| KXBTC15M-26MAY062215-15 | approved_entry | no | True | True | 136.000000 | 33.000000 | 77.750000 | 66.000000 | 0.713473 | 2.319368 | 70.347298 | {'reduce': 0.0, 'value': 0.0, 'collapse': 1.0} |
| KXBTC15M-26MAY062045-45 | approved_entry | no | True | True | 129.000000 | 18.000000 | 76.000000 | 67.750000 | 0.767832 | -1.783208 | 75.783208 | {'reduce': 1.0, 'value': 0.0, 'collapse': 0.0} |
| KXBTC15M-26MAY070745-45 | approved_entry | yes | True | True | 127.000000 | 30.000000 | 79.333333 | 68.250000 | 0.788411 | 1.158860 | 77.841140 | {'reduce': 1.0, 'value': 0.0, 'collapse': 0.0} |
| KXBTC15M-26MAY071230-30 | approved_entry | yes | True | True | 122.000000 | 21.000000 | 80.666667 | 69.500000 | 0.723591 | 7.307604 | 71.359063 | {'reduce': 0.6666666666666666, 'value': 0.0, 'collapse': 0.3333333333333333} |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | True | 108.000000 | 17.000000 | 80.000000 | 73.000000 | 0.756617 | 4.338272 | 74.661728 | {'reduce': 1.0, 'value': 0.0, 'collapse': 0.0} |
| KXBTC15M-26MAY062100-00 | approved_entry | yes | True | True | 105.600000 | 37.000000 | 81.000000 | 82.400000 | 0.803171 | -0.483772 | 79.317105 | {'reduce': 0.676923076923077, 'value': 0.3230769230769231, 'collapse': 0.0} |
| KXBTC15M-26MAY061800-00 | approved_entry | no | True | True | 88.000000 | 28.000000 | 73.500000 | 78.000000 | 0.799718 | -7.638419 | 78.971752 | {'reduce': 0.6666666666666666, 'value': 0.3333333333333333, 'collapse': 0.0} |
| KXBTC15M-26MAY070115-15 | approved_entry | yes | True | True | 76.200000 | 16.000000 | 81.666667 | 87.300000 | 0.844945 | -1.494567 | 83.494567 | {'reduce': 0.0, 'value': 1.0, 'collapse': 0.0} |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | True | 70.800000 | 25.000000 | 78.333333 | 88.200000 | 0.798050 | -4.305026 | 78.805025 | {'reduce': 0.5116279069767442, 'value': 0.4883720930232558, 'collapse': 0.0} |
| KXBTC15M-26MAY062015-15 | approved_entry | no | True | True | 69.000000 | 56.000000 | 86.000000 | 65.500000 | 0.689967 | 17.003341 | 67.996659 | {'reduce': 0.5, 'value': 0.0, 'collapse': 0.5} |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | True | 68.000000 | 24.000000 | 83.000000 | 66.000000 | 0.771497 | -4.149750 | 76.149750 | {'reduce': 1.0, 'value': 0.0, 'collapse': 0.0} |
| KXBTC15M-26MAY070915-15 | approved_entry | no | True | True | 68.000000 | 20.000000 | 77.333333 | 66.000000 | 0.785310 | -5.531007 | 77.531007 | {'reduce': 1.0, 'value': 0.0, 'collapse': 0.0} |
| KXBTC15M-26MAY071030-30 | approved_entry | no | True | True | 67.000000 | 21.000000 | 80.666667 | 66.500000 | 0.773009 | -0.300900 | 76.300900 | {'reduce': 1.0, 'value': 0.0, 'collapse': 0.0} |
| KXBTC15M-26MAY061815-15 | approved_entry | no | True | True | 66.000000 | 14.000000 | 76.500000 | 67.000000 | 0.750076 | 1.992382 | 74.007618 | {'reduce': 1.0, 'value': 0.0, 'collapse': 0.0} |
| KXBTC15M-26MAY062030-30 | approved_entry | no | True | True | 48.000000 | 31.000000 | 76.000000 | 76.000000 | 0.798134 | -1.813329 | 78.813329 | {'reduce': 1.0, 'value': 0.0, 'collapse': 0.0} |
| KXBTC15M-26MAY061400-00 | approved_entry | no | True | True | 32.000000 | 10.000000 | 89.000000 | 84.000000 | 0.742300 | 14.769975 | 73.230025 | {'reduce': 0.0, 'value': 1.0, 'collapse': 0.0} |
| KXBTC15M-26MAY061615-15 | approved_entry | yes | True | True | 8.000000 | 9.000000 | 90.000000 | 96.000000 | 0.959135 | -5.913426 | 94.913426 | {'reduce': 0.0, 'value': 1.0, 'collapse': 0.0} |
| KXBTC15M-26MAY062200-00 | rejected_actionable | no | True | True | 6.400000 | 4.000000 | 82.500000 | 98.400000 | 0.969996 | -13.999555 | 95.999555 | {'reduce': 0.0, 'value': 1.0, 'collapse': 0.0} |
| KXBTC15M-26MAY070815-15 | approved_entry | yes | True | True | 0.000200 | 9.000000 | 84.333300 | None | None | None | None | {'reduce': 0.0, 'value': 0.0, 'collapse': 0.0} |
| KXBTC15M-26MAY070945-45 | approved_entry | no | True | True | 0.000200 | 28.000000 | 75.333300 | None | None | None | None | {'reduce': 0.0, 'value': 0.0, 'collapse': 0.0} |
| KXBTC15M-26MAY070615-15 | rejected_actionable | yes | False | False | -152.000000 | -68.000000 | 77.000000 | 76.000000 | 0.775618 | -0.561864 | 76.561864 | {'reduce': 1.0, 'value': 0.0, 'collapse': 0.0} |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | False | -216.000000 | -78.000000 | 73.500000 | 54.000000 | 0.787526 | -4.752593 | 77.752593 | {'reduce': 1.0, 'value': 0.0, 'collapse': 0.0} |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | False | -245.840000 | -72.000000 | 65.400000 | 57.800000 | 0.696852 | 7.064857 | 68.685143 | {'reduce': 0.75, 'value': 0.0, 'collapse': 0.25} |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | False | -260.000000 | -15.000000 | 72.500000 | 65.000000 | 0.716049 | 0.728438 | 70.604895 | {'reduce': 0.6666666666666666, 'value': 0.0, 'collapse': 0.3333333333333333} |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | False | -462.000000 | -80.000000 | 79.000000 | 77.000000 | 0.783026 | 0.897405 | 77.302595 | {'reduce': 0.8, 'value': 0.2, 'collapse': 0.0} |
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | False | -488.000000 | -84.000000 | 82.333333 | 81.333333 | 0.800165 | 1.383458 | 79.016542 | {'reduce': 0.5925925925925926, 'value': 0.4074074074074074, 'collapse': 0.0} |
