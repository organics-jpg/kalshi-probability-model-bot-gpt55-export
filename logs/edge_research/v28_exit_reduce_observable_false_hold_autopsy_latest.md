# v28 Exit Reduce Observable False-Hold Autopsy

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T16:21:57.256456+00:00`
- Reduce freeze UTC: `2026-05-06T06:33:56.987999+00:00`
- Observable freeze UTC: `2026-05-07T00:08:36.297681+00:00`

## Interpretation

- This is a research-only autopsy; it does not freeze a candidate or change exits.
- Diagnostic p_hold>=0.75 probability-reduce denominator has 18 rows, 171.0c net, and harmful delta -610.0c.
- Post-observable-birth denominator has 7 rows, -224.0c net, and harmful delta -424.0c.
- The forward denominator itself is negative, so the observable reduce-loss-control mechanism should stay downgraded unless a new frozen guard proves it can avoid false holds.
- Best post-birth zero-harm single-feature guard is entry_depth_ge_225.99 with 2 rows and 110.0c, but this is post-hoc and not promotion evidence.

## diagnostic_from_reduce_freeze

- Freeze UTC: `2026-05-06T06:33:56.987999+00:00`
- Candidate rows: `18`
- Net/helpful/harmful delta: `171.0c` / `781.0c` / `-610.0c`
- Helpful/harmful/flat rows: `14/4/0`
- Exit reason counts: `{'mushroom_v28_probability_reduce': 18}`

### Best Single-Feature Guards

| rule | rows | net c | helpful/harmful | helpful c | harmful c | worst c |
|---|---:|---:|---:|---:|---:|---:|
| `exit_cents_le_72` | 8 | 479.0c | 8/0 | 479.0c | 0.0c | 56.0c |
| `hold_book_gap_ge_0.063164` | 7 | 417.0c | 7/0 | 417.0c | 0.0c | 54.0c |
| `entry_seconds_to_close_le_519.475` | 7 | 391.0c | 7/0 | 391.0c | 0.0c | 48.0c |
| `exit_cents_le_70` | 6 | 366.0c | 6/0 | 366.0c | 0.0c | 60.0c |
| `fair_drawdown_cents_le_-1.64577` | 6 | 355.0c | 6/0 | 355.0c | 0.0c | 54.0c |
| `hold_book_gap_ge_0.066458` | 6 | 355.0c | 6/0 | 355.0c | 0.0c | 54.0c |
| `entry_seconds_to_close_le_518.045` | 6 | 329.0c | 6/0 | 329.0c | 0.0c | 48.0c |
| `fair_drawdown_cents_le_-2.05295` | 5 | 301.0c | 5/0 | 301.0c | 0.0c | 57.0c |
| `hold_book_gap_ge_0.070529` | 5 | 301.0c | 5/0 | 301.0c | 0.0c | 57.0c |
| `entry_volshock_ge_0.673097` | 5 | 293.0c | 5/0 | 293.0c | 0.0c | 54.0c |
| `entry_book_age_ms_le_266` | 5 | 273.0c | 5/0 | 273.0c | 0.0c | 48.0c |
| `entry_seconds_to_close_le_471.76` | 5 | 269.0c | 5/0 | 269.0c | 0.0c | 48.0c |
| `fair_drawdown_cents_le_-2.76059` | 4 | 239.0c | 4/0 | 239.0c | 0.0c | 57.0c |
| `hold_book_gap_ge_0.08918` | 4 | 239.0c | 4/0 | 239.0c | 0.0c | 57.0c |
| `entry_volshock_ge_0.765794` | 4 | 233.0c | 4/0 | 233.0c | 0.0c | 54.0c |

### Candidate Rows

| market | side/result | entry | exit | p_hold | depth | stc | duration | book age | sigma | volshock | drawdown | gap | delta |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY060700-00 | no/yes | 84 | 80 | 0.799603 | 2717.890000 | 625.155000 | 113.345290 | 625.000000 | 88.671268 | 0.462915 | 4.039746 | -0.000397 | -160.0c |
| KXBTC15M-26MAY071015-15 | no/yes | 78 | 79 | 0.789130 | 29.380000 | 583.765000 | 44.557682 | 469.000000 | 127.362008 | 0.598925 | -0.913001 | -0.000870 | -158.0c |
| KXBTC15M-26MAY060900-00 | yes/no | 78 | 73 | 0.789990 | 500.000000 | 743.816000 | 56.622984 | 359.000000 | 107.892740 | 0.119273 | -0.998969 | 0.059990 | -146.0c |
| KXBTC15M-26MAY071015-15 | no/yes | 81 | 73 | 0.763980 | 55.000000 | 538.342000 | 31.096634 | 890.000000 | 123.755074 | 0.600867 | 4.602013 | 0.033980 | -146.0c |
| KXBTC15M-26MAY061445-45 | no/no | 88 | 77 | 0.797830 | 55.000000 | 714.710000 | 52.304092 | 687.000000 | 119.451977 | -0.246207 | 8.216985 | 0.027830 | 46.0c |
| KXBTC15M-26MAY071215-15 | no/no | 84 | 76 | 0.797661 | 8.000000 | 467.027000 | 73.382062 | 625.000000 | 96.827686 | 0.327917 | 4.233856 | 0.037661 | 48.0c |
| KXBTC15M-26MAY071215-15 | no/no | 80 | 76 | 0.765822 | 1329.710000 | 361.476000 | 40.806923 | 172.000000 | 88.514362 | 0.346320 | 3.417815 | 0.005822 | 48.0c |
| KXBTC15M-26MAY060645-45 | yes/yes | 82 | 74 | 0.799349 | 384.000000 | 635.374000 | 35.169843 | 828.000000 | 94.132945 | 0.420197 | 2.065125 | 0.059349 | 52.0c |
| KXBTC15M-26MAY060630-30 | yes/yes | 79 | 73 | 0.777774 | 9.000000 | 543.652000 | 42.718047 | 266.000000 | 82.308304 | 0.259503 | 1.222639 | 0.047774 | 54.0c |
| KXBTC15M-26MAY061030-30 | yes/yes | 78 | 73 | 0.796458 | 295.000000 | 471.760000 | 31.758237 | 187.000000 | 119.347449 | 0.796185 | -1.645773 | 0.066458 | 54.0c |
| KXBTC15M-26MAY060645-45 | yes/yes | 78 | 72 | 0.779789 | 99.490000 | 596.372000 | 124.166970 | 828.000000 | 85.127577 | 0.468181 | 0.021114 | 0.059789 | 56.0c |
| KXBTC15M-26MAY060930-30 | no/no | 73 | 72 | 0.799180 | 179.000000 | 470.196000 | 43.811640 | 172.000000 | 110.113616 | 0.779291 | -6.917970 | 0.089180 | 57.0c |
| KXBTC15M-26MAY060915-15 | no/no | 70 | 70 | 0.793762 | 4953.550000 | 836.982000 | 79.387528 | 672.000000 | 125.230299 | 0.375678 | -9.376204 | 0.093762 | 60.0c |
| KXBTC15M-26MAY061015-15 | no/no | 70 | 70 | 0.799979 | 2075.040000 | 778.747000 | 84.739807 | 266.000000 | 137.842477 | 0.673097 | -9.997858 | 0.099979 | 60.0c |
| KXBTC15M-26MAY061030-30 | yes/yes | 78 | 70 | 0.752739 | 221.300000 | 518.045000 | 31.089772 | 906.000000 | 125.184173 | 0.791039 | 2.726149 | 0.052739 | 60.0c |
| KXBTC15M-26MAY060300-00 | yes/yes | 80 | 69 | 0.753164 | 40.000000 | 271.516000 | 31.087884 | 875.000000 | 47.661178 | -0.498899 | 4.683642 | 0.063164 | 62.0c |
| KXBTC15M-26MAY060930-30 | no/no | 76 | 69 | 0.787606 | 655.000000 | 519.475000 | 34.125873 | 891.000000 | 117.143469 | 0.765794 | -2.760587 | 0.107606 | 62.0c |
| KXBTC15M-26MAY071045-45 | no/no | 74 | 69 | 0.760529 | 225.990000 | 822.403000 | 35.479669 | 437.000000 | 137.454980 | 0.288890 | -2.052947 | 0.070529 | 62.0c |

## post_observable_birth

- Freeze UTC: `2026-05-07T00:08:36.297681+00:00`
- Candidate rows: `7`
- Net/helpful/harmful delta: `-224.0c` / `200.0c` / `-424.0c`
- Helpful/harmful/flat rows: `4/3/0`
- Exit reason counts: `{'mushroom_v28_probability_reduce': 7}`

### Best Single-Feature Guards

| rule | rows | net c | helpful/harmful | helpful c | harmful c | worst c |
|---|---:|---:|---:|---:|---:|---:|
| `entry_depth_ge_225.99` | 2 | 110.0c | 2/0 | 110.0c | 0.0c | 48.0c |
| `entry_seconds_to_close_ge_777.523` | 2 | 104.0c | 2/0 | 104.0c | 0.0c | 42.0c |
| `entry_seconds_to_close_le_467.027` | 2 | 96.0c | 2/0 | 96.0c | 0.0c | 48.0c |
| `entry_depth_le_21` | 2 | 90.0c | 2/0 | 90.0c | 0.0c | 42.0c |
| `entry_volshock_le_0.34632` | 5 | 80.0c | 4/1 | 200.0c | -120.0c | -120.0c |
| `entry_book_age_ms_le_438` | 4 | 32.0c | 3/1 | 152.0c | -120.0c | -120.0c |
| `entry_volshock_le_0.327917` | 4 | 32.0c | 3/1 | 152.0c | -120.0c | -120.0c |
| `exit_sigma_t_dollars_le_96.8277` | 4 | 18.0c | 3/1 | 138.0c | -120.0c | -120.0c |
| `fair_drawdown_cents_le_4.23386` | 4 | 0.0c | 3/1 | 158.0c | -158.0c | -158.0c |
| `entry_book_age_ms_le_437` | 3 | -10.0c | 2/1 | 110.0c | -120.0c | -120.0c |
| `hold_book_gap_ge_0.037661` | 3 | -10.0c | 2/1 | 110.0c | -120.0c | -120.0c |
| `entry_seconds_to_close_ge_628.084` | 3 | -16.0c | 2/1 | 104.0c | -120.0c | -120.0c |
| `entry_volshock_le_0.28889` | 3 | -16.0c | 2/1 | 104.0c | -120.0c | -120.0c |
| `exit_cents_ge_76` | 4 | -20.0c | 3/1 | 138.0c | -158.0c | -158.0c |
| `entry_depth_le_24` | 3 | -30.0c | 2/1 | 90.0c | -120.0c | -120.0c |

### Candidate Rows

| market | side/result | entry | exit | p_hold | depth | stc | duration | book age | sigma | volshock | drawdown | gap | delta |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY071015-15 | no/yes | 78 | 79 | 0.789130 | 29.380000 | 583.765000 | 44.557682 | 469.000000 | 127.362008 | 0.598925 | -0.913001 | -0.000870 | -158.0c |
| KXBTC15M-26MAY071015-15 | no/yes | 81 | 73 | 0.763980 | 55.000000 | 538.342000 | 31.096634 | 890.000000 | 123.755074 | 0.600867 | 4.602013 | 0.033980 | -146.0c |
| KXBTC15M-26MAY062130-30 | no/yes | 76 | 60 | 0.768407 | 24.000000 | 628.084000 | 245.683692 | 297.000000 | 76.542004 | 0.060341 | 6.159273 | 0.168407 | -120.0c |
| KXBTC15M-26MAY071000-00 | no/no | 71 | 79 | 0.781361 | 21.000000 | 777.523000 | 618.463568 | 438.000000 | 69.298788 | 0.019548 | 6.863933 | -0.008639 | 42.0c |
| KXBTC15M-26MAY071215-15 | no/no | 84 | 76 | 0.797661 | 8.000000 | 467.027000 | 73.382062 | 625.000000 | 96.827686 | 0.327917 | 4.233856 | 0.037661 | 48.0c |
| KXBTC15M-26MAY071215-15 | no/no | 80 | 76 | 0.765822 | 1329.710000 | 361.476000 | 40.806923 | 172.000000 | 88.514362 | 0.346320 | 3.417815 | 0.005822 | 48.0c |
| KXBTC15M-26MAY071045-45 | no/no | 74 | 69 | 0.760529 | 225.990000 | 822.403000 | 35.479669 | 437.000000 | 137.454980 | 0.288890 | -2.052947 | 0.070529 | 62.0c |
