# v28 Book Dislocation Regime Attribution

Research-only; no live bot changes and no orders.

- Lead candidate: `first_eligible_top80_escape_energy+escape_edge6_or_p65_or_far_edge4+continuous_recross_forget`

## Current Read

- diagnostic_existing_false_conviction_freeze: lead entries/settled/coverage/net 91/91/80.53097345132744/-407.0c.
- Best path bucket is near_high_recross with 6 settled and 254.0c.
- Worst edge bucket is thin_discount_0_4pp with 46 settled and -299.0c.
- post_freeze_candidate: lead entries/settled/coverage/net 75/75/80.64516129032258/-765.0c.
- Best path bucket is escaped_low_recross with 22 settled and 270.0c.
- Worst edge bucket is thin_discount_0_4pp with 37 settled and -565.0c.
- Diagnostic windows can explain direction only; post-freeze rows decide whether the idea survives.

## diagnostic_existing_false_conviction_freeze

- Freeze UTC: `2026-05-06T09:10:09.146392+00:00`
- Summary entries/settled/coverage/net: `91/91/80.530973/-407.000000c`

### Edge Buckets

| bucket | entries | settled | W/L | net c | avg net | avg edge | avg escape | approved/recon |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `deep_discount_ge12pp` | 22 | 22 | 10/12 | 86.000000 | 3.909091 | 0.257235 | 0.377058 | 3/19 |
| `discount_8_12pp` | 8 | 8 | 6/2 | -10.000000 | -1.250000 | 0.091732 | 0.406335 | 4/4 |
| `discount_4_8pp` | 15 | 15 | 10/5 | -184.000000 | -12.266667 | 0.054728 | 0.341997 | 1/14 |
| `thin_discount_0_4pp` | 46 | 46 | 34/12 | -299.000000 | -6.500000 | 0.019998 | 0.316557 | 0/46 |

### Ask-Move Buckets

| bucket | entries | settled | W/L | net c | avg net | avg edge | avg escape | approved/recon |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `ask_rise_4_8pp` | 16 | 16 | 13/3 | 109.000000 | 6.812500 | 0.036237 | 0.343821 | 2/14 |
| `ask_move_unknown` | 13 | 13 | 8/5 | 51.000000 | 3.923077 | 0.132703 | 0.338154 | 2/11 |
| `ask_stable` | 17 | 17 | 13/4 | -85.000000 | -5.000000 | 0.059125 | 0.370614 | 2/15 |
| `ask_drop_4_8pp` | 3 | 3 | 1/2 | -130.000000 | -43.333333 | 0.124654 | 0.278372 | 0/3 |
| `ask_spike_ge8pp` | 26 | 26 | 19/7 | -145.000000 | -5.576923 | 0.028900 | 0.324601 | 0/26 |
| `ask_dip_ge8pp` | 16 | 16 | 6/10 | -207.000000 | -12.937500 | 0.231152 | 0.360326 | 2/14 |

### Path Buckets

| bucket | entries | settled | W/L | net c | avg net | avg edge | avg escape | approved/recon |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `near_high_recross` | 6 | 6 | 5/1 | 254.000000 | 42.333333 | 0.087901 | 0.264667 | 0/6 |
| `escaped_low_recross` | 24 | 24 | 22/2 | 131.000000 | 5.458333 | 0.066594 | 0.492153 | 8/16 |
| `near_mid_recross` | 30 | 30 | 15/15 | -306.000000 | -10.200000 | 0.108186 | 0.241061 | 0/30 |
| `near_low_recross` | 31 | 31 | 18/13 | -486.000000 | -15.677419 | 0.089116 | 0.342130 | 0/31 |

### Combined Buckets

| bucket | entries | settled | W/L | net c | avg net | avg edge | avg escape | approved/recon |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `deep_discount_ge12pp|ask_dip_ge8pp|near_mid_recross` | 6 | 6 | 4/2 | 363.000000 | 60.500000 | 0.203552 | 0.233900 | 0/6 |
| `thin_discount_0_4pp|ask_spike_ge8pp|near_mid_recross` | 7 | 7 | 6/1 | 210.000000 | 30.000000 | 0.018362 | 0.227504 | 0/7 |
| `thin_discount_0_4pp|ask_stable|near_low_recross` | 3 | 3 | 3/0 | 164.000000 | 54.666667 | 0.033341 | 0.300491 | 0/3 |
| `thin_discount_0_4pp|ask_rise_4_8pp|near_high_recross` | 2 | 2 | 2/0 | 127.000000 | 63.500000 | 0.019196 | 0.184755 | 0/2 |
| `thin_discount_0_4pp|ask_stable|escaped_low_recross` | 4 | 4 | 4/0 | 116.000000 | 29.000000 | 0.021499 | 0.406499 | 0/4 |
| `deep_discount_ge12pp|ask_stable|near_low_recross` | 1 | 1 | 1/0 | 100.000000 | 100.000000 | 0.240466 | 0.476765 | 0/1 |
| `thin_discount_0_4pp|ask_move_unknown|near_mid_recross` | 2 | 2 | 2/0 | 98.000000 | 49.000000 | 0.014867 | 0.277903 | 0/2 |
| `deep_discount_ge12pp|ask_move_unknown|near_high_recross` | 1 | 1 | 1/0 | 96.000000 | 96.000000 | 0.230619 | 0.451948 | 0/1 |
| `discount_8_12pp|ask_rise_4_8pp|near_high_recross` | 1 | 1 | 1/0 | 76.000000 | 76.000000 | 0.085793 | 0.256236 | 0/1 |
| `discount_4_8pp|ask_rise_4_8pp|near_mid_recross` | 1 | 1 | 1/0 | 66.000000 | 66.000000 | 0.054288 | 0.253934 | 0/1 |
| `discount_4_8pp|ask_drop_4_8pp|near_low_recross` | 1 | 1 | 1/0 | 60.000000 | 60.000000 | 0.041896 | 0.282960 | 0/1 |
| `discount_4_8pp|ask_spike_ge8pp|near_mid_recross` | 1 | 1 | 1/0 | 60.000000 | 60.000000 | 0.064425 | 0.325599 | 0/1 |
| `thin_discount_0_4pp|ask_rise_4_8pp|escaped_low_recross` | 3 | 3 | 3/0 | 60.000000 | 20.000000 | 0.014395 | 0.449165 | 0/3 |
| `discount_4_8pp|ask_spike_ge8pp|near_high_recross` | 1 | 1 | 1/0 | 57.000000 | 57.000000 | 0.063446 | 0.322564 | 0/1 |
| `discount_8_12pp|ask_spike_ge8pp|escaped_low_recross` | 1 | 1 | 1/0 | 51.000000 | 51.000000 | 0.096507 | 0.445051 | 0/1 |
| `thin_discount_0_4pp|ask_move_unknown|near_low_recross` | 1 | 1 | 1/0 | 47.000000 | 47.000000 | 0.022718 | 0.311730 | 0/1 |
| `discount_8_12pp|ask_rise_4_8pp|escaped_low_recross` | 2 | 2 | 2/0 | 45.000000 | 22.500000 | 0.089763 | 0.502746 | 2/0 |
| `deep_discount_ge12pp|ask_dip_ge8pp|escaped_low_recross` | 2 | 2 | 2/0 | 44.000000 | 22.000000 | 0.231524 | 0.697278 | 2/0 |
| `discount_4_8pp|ask_rise_4_8pp|escaped_low_recross` | 1 | 1 | 1/0 | 43.000000 | 43.000000 | 0.064617 | 0.454303 | 0/1 |
| `discount_8_12pp|ask_stable|escaped_low_recross` | 1 | 1 | 1/0 | 35.000000 | 35.000000 | 0.085399 | 0.535115 | 1/0 |
| `thin_discount_0_4pp|ask_move_unknown|escaped_low_recross` | 1 | 1 | 1/0 | 35.000000 | 35.000000 | 0.038576 | 0.409841 | 0/1 |
| `discount_4_8pp|ask_stable|near_low_recross` | 4 | 4 | 3/1 | 23.000000 | 5.750000 | 0.056855 | 0.341150 | 0/4 |
| `discount_4_8pp|ask_move_unknown|escaped_low_recross` | 1 | 1 | 1/0 | 22.000000 | 22.000000 | 0.053342 | 0.555842 | 1/0 |
| `discount_8_12pp|ask_move_unknown|escaped_low_recross` | 1 | 1 | 1/0 | -11.000000 | -11.000000 | 0.083640 | 0.656319 | 1/0 |
| `deep_discount_ge12pp|ask_drop_4_8pp|near_mid_recross` | 1 | 1 | 0/1 | -47.000000 | -47.000000 | 0.282856 | 0.257032 | 0/1 |
| `thin_discount_0_4pp|ask_spike_ge8pp|escaped_low_recross` | 5 | 5 | 4/1 | -53.000000 | -10.600000 | 0.025311 | 0.444976 | 0/5 |
| `discount_4_8pp|ask_spike_ge8pp|near_low_recross` | 2 | 2 | 1/1 | -83.000000 | -41.500000 | 0.042165 | 0.293187 | 0/2 |
| `deep_discount_ge12pp|ask_stable|escaped_low_recross` | 1 | 1 | 1/0 | -91.000000 | -91.000000 | 0.227587 | 0.693177 | 1/0 |
| `discount_8_12pp|ask_dip_ge8pp|near_high_recross` | 1 | 1 | 0/1 | -102.000000 | -102.000000 | 0.109156 | 0.187742 | 0/1 |
| `discount_8_12pp|ask_dip_ge8pp|near_mid_recross` | 1 | 1 | 0/1 | -104.000000 | -104.000000 | 0.093834 | 0.164726 | 0/1 |
| `deep_discount_ge12pp|ask_move_unknown|near_mid_recross` | 5 | 5 | 1/4 | -112.000000 | -22.400000 | 0.239768 | 0.245893 | 0/5 |
| `discount_4_8pp|ask_move_unknown|near_mid_recross` | 1 | 1 | 0/1 | -124.000000 | -124.000000 | 0.067669 | 0.225047 | 0/1 |
| `thin_discount_0_4pp|ask_dip_ge8pp|near_mid_recross` | 1 | 1 | 0/1 | -141.000000 | -141.000000 | 0.016643 | 0.225856 | 0/1 |
| `discount_4_8pp|ask_drop_4_8pp|near_mid_recross` | 1 | 1 | 0/1 | -143.000000 | -143.000000 | 0.049210 | 0.295125 | 0/1 |
| `discount_4_8pp|ask_spike_ge8pp|escaped_low_recross` | 1 | 1 | 0/1 | -165.000000 | -165.000000 | 0.050281 | 0.463600 | 0/1 |
| `thin_discount_0_4pp|ask_spike_ge8pp|near_low_recross` | 8 | 8 | 5/3 | -222.000000 | -27.750000 | 0.017164 | 0.309878 | 0/8 |
| `deep_discount_ge12pp|ask_dip_ge8pp|near_low_recross` | 5 | 5 | 0/5 | -267.000000 | -53.400000 | 0.358888 | 0.477788 | 0/5 |
| `thin_discount_0_4pp|ask_rise_4_8pp|near_low_recross` | 6 | 6 | 3/3 | -308.000000 | -51.333333 | 0.019000 | 0.302360 | 0/6 |
| `thin_discount_0_4pp|ask_stable|near_mid_recross` | 3 | 3 | 0/3 | -432.000000 | -144.000000 | 0.012742 | 0.234435 | 0/3 |


## post_freeze_candidate

- Freeze UTC: `2026-05-06T14:14:08.956655+00:00`
- Summary entries/settled/coverage/net: `75/75/80.645161/-765.000000c`

### Edge Buckets

| bucket | entries | settled | W/L | net c | avg net | avg edge | avg escape | approved/recon |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `deep_discount_ge12pp` | 20 | 20 | 9/11 | 82.000000 | 4.100000 | 0.264656 | 0.382804 | 3/17 |
| `discount_8_12pp` | 7 | 7 | 5/2 | -86.000000 | -12.285714 | 0.092580 | 0.427778 | 4/3 |
| `discount_4_8pp` | 11 | 11 | 7/4 | -196.000000 | -17.818182 | 0.055603 | 0.341468 | 1/10 |
| `thin_discount_0_4pp` | 37 | 37 | 26/11 | -565.000000 | -15.270270 | 0.019727 | 0.325039 | 0/37 |

### Ask-Move Buckets

| bucket | entries | settled | W/L | net c | avg net | avg edge | avg escape | approved/recon |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `ask_stable` | 17 | 17 | 13/4 | -85.000000 | -5.000000 | 0.059125 | 0.370614 | 2/15 |
| `ask_spike_ge8pp` | 19 | 19 | 14/5 | -110.000000 | -5.789474 | 0.027064 | 0.330757 | 0/19 |
| `ask_drop_4_8pp` | 3 | 3 | 1/2 | -130.000000 | -43.333333 | 0.124654 | 0.278372 | 0/3 |
| `ask_dip_ge8pp` | 16 | 16 | 6/10 | -207.000000 | -12.937500 | 0.231152 | 0.360326 | 2/14 |
| `ask_rise_4_8pp` | 10 | 10 | 7/3 | -233.000000 | -23.300000 | 0.035567 | 0.379986 | 2/8 |
| `ask_move_unknown` | 10 | 10 | 6/4 | 0.000000 | 0.000000 | 0.133530 | 0.344808 | 2/8 |

### Path Buckets

| bucket | entries | settled | W/L | net c | avg net | avg edge | avg escape | approved/recon |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `escaped_low_recross` | 22 | 22 | 21/1 | 270.000000 | 12.272727 | 0.070267 | 0.496235 | 8/14 |
| `near_high_recross` | 3 | 3 | 2/1 | 14.000000 | 4.666667 | 0.060010 | 0.231887 | 0/3 |
| `near_mid_recross` | 24 | 24 | 10/14 | -512.000000 | -21.333333 | 0.122242 | 0.239814 | 0/24 |
| `near_low_recross` | 26 | 26 | 14/12 | -537.000000 | -20.653846 | 0.100885 | 0.348643 | 0/26 |

### Combined Buckets

| bucket | entries | settled | W/L | net c | avg net | avg edge | avg escape | approved/recon |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `deep_discount_ge12pp|ask_dip_ge8pp|near_mid_recross` | 6 | 6 | 4/2 | 363.000000 | 60.500000 | 0.203552 | 0.233900 | 0/6 |
| `thin_discount_0_4pp|ask_stable|near_low_recross` | 3 | 3 | 3/0 | 164.000000 | 54.666667 | 0.033341 | 0.300491 | 0/3 |
| `thin_discount_0_4pp|ask_stable|escaped_low_recross` | 4 | 4 | 4/0 | 116.000000 | 29.000000 | 0.021499 | 0.406499 | 0/4 |
| `deep_discount_ge12pp|ask_stable|near_low_recross` | 1 | 1 | 1/0 | 100.000000 | 100.000000 | 0.240466 | 0.476765 | 0/1 |
| `thin_discount_0_4pp|ask_spike_ge8pp|near_mid_recross` | 5 | 5 | 4/1 | 85.000000 | 17.000000 | 0.018939 | 0.238351 | 0/5 |
| `discount_4_8pp|ask_drop_4_8pp|near_low_recross` | 1 | 1 | 1/0 | 60.000000 | 60.000000 | 0.041896 | 0.282960 | 0/1 |
| `thin_discount_0_4pp|ask_rise_4_8pp|near_high_recross` | 1 | 1 | 1/0 | 59.000000 | 59.000000 | 0.007428 | 0.185354 | 0/1 |
| `discount_4_8pp|ask_spike_ge8pp|near_high_recross` | 1 | 1 | 1/0 | 57.000000 | 57.000000 | 0.063446 | 0.322564 | 0/1 |
| `discount_8_12pp|ask_spike_ge8pp|escaped_low_recross` | 1 | 1 | 1/0 | 51.000000 | 51.000000 | 0.096507 | 0.445051 | 0/1 |
| `thin_discount_0_4pp|ask_move_unknown|near_mid_recross` | 1 | 1 | 1/0 | 51.000000 | 51.000000 | 0.005946 | 0.247097 | 0/1 |
| `thin_discount_0_4pp|ask_move_unknown|near_low_recross` | 1 | 1 | 1/0 | 47.000000 | 47.000000 | 0.022718 | 0.311730 | 0/1 |
| `discount_8_12pp|ask_rise_4_8pp|escaped_low_recross` | 2 | 2 | 2/0 | 45.000000 | 22.500000 | 0.089763 | 0.502746 | 2/0 |
| `deep_discount_ge12pp|ask_dip_ge8pp|escaped_low_recross` | 2 | 2 | 2/0 | 44.000000 | 22.000000 | 0.231524 | 0.697278 | 2/0 |
| `discount_4_8pp|ask_rise_4_8pp|escaped_low_recross` | 1 | 1 | 1/0 | 43.000000 | 43.000000 | 0.064617 | 0.454303 | 0/1 |
| `discount_8_12pp|ask_stable|escaped_low_recross` | 1 | 1 | 1/0 | 35.000000 | 35.000000 | 0.085399 | 0.535115 | 1/0 |
| `thin_discount_0_4pp|ask_move_unknown|escaped_low_recross` | 1 | 1 | 1/0 | 35.000000 | 35.000000 | 0.038576 | 0.409841 | 0/1 |
| `thin_discount_0_4pp|ask_rise_4_8pp|escaped_low_recross` | 2 | 2 | 2/0 | 34.000000 | 17.000000 | 0.020539 | 0.458302 | 0/2 |
| `discount_4_8pp|ask_stable|near_low_recross` | 4 | 4 | 3/1 | 23.000000 | 5.750000 | 0.056855 | 0.341150 | 0/4 |
| `discount_4_8pp|ask_move_unknown|escaped_low_recross` | 1 | 1 | 1/0 | 22.000000 | 22.000000 | 0.053342 | 0.555842 | 1/0 |
| `discount_8_12pp|ask_move_unknown|escaped_low_recross` | 1 | 1 | 1/0 | -11.000000 | -11.000000 | 0.083640 | 0.656319 | 1/0 |
| `deep_discount_ge12pp|ask_move_unknown|near_mid_recross` | 4 | 4 | 1/3 | -20.000000 | -5.000000 | 0.265853 | 0.260550 | 0/4 |
| `deep_discount_ge12pp|ask_drop_4_8pp|near_mid_recross` | 1 | 1 | 0/1 | -47.000000 | -47.000000 | 0.282856 | 0.257032 | 0/1 |
| `thin_discount_0_4pp|ask_spike_ge8pp|escaped_low_recross` | 5 | 5 | 4/1 | -53.000000 | -10.600000 | 0.025311 | 0.444976 | 0/5 |
| `deep_discount_ge12pp|ask_stable|escaped_low_recross` | 1 | 1 | 1/0 | -91.000000 | -91.000000 | 0.227587 | 0.693177 | 1/0 |
| `discount_8_12pp|ask_dip_ge8pp|near_high_recross` | 1 | 1 | 0/1 | -102.000000 | -102.000000 | 0.109156 | 0.187742 | 0/1 |
| `discount_8_12pp|ask_dip_ge8pp|near_mid_recross` | 1 | 1 | 0/1 | -104.000000 | -104.000000 | 0.093834 | 0.164726 | 0/1 |
| `thin_discount_0_4pp|ask_spike_ge8pp|near_low_recross` | 6 | 6 | 4/2 | -116.000000 | -19.333333 | 0.014831 | 0.307405 | 0/6 |
| `discount_4_8pp|ask_move_unknown|near_mid_recross` | 1 | 1 | 0/1 | -124.000000 | -124.000000 | 0.067669 | 0.225047 | 0/1 |
| `discount_4_8pp|ask_spike_ge8pp|near_low_recross` | 1 | 1 | 0/1 | -134.000000 | -134.000000 | 0.044034 | 0.255706 | 0/1 |
| `thin_discount_0_4pp|ask_dip_ge8pp|near_mid_recross` | 1 | 1 | 0/1 | -141.000000 | -141.000000 | 0.016643 | 0.225856 | 0/1 |
| `discount_4_8pp|ask_drop_4_8pp|near_mid_recross` | 1 | 1 | 0/1 | -143.000000 | -143.000000 | 0.049210 | 0.295125 | 0/1 |
| `deep_discount_ge12pp|ask_dip_ge8pp|near_low_recross` | 5 | 5 | 0/5 | -267.000000 | -53.400000 | 0.358888 | 0.477788 | 0/5 |
| `thin_discount_0_4pp|ask_rise_4_8pp|near_low_recross` | 4 | 4 | 1/3 | -414.000000 | -103.500000 | 0.015754 | 0.309526 | 0/4 |
| `thin_discount_0_4pp|ask_stable|near_mid_recross` | 3 | 3 | 0/3 | -432.000000 | -144.000000 | 0.012742 | 0.234435 | 0/3 |

