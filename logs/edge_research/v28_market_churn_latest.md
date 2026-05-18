# v28 Market Churn

Groups v28 shadow trades by market to expose repeated entries and side flips.

- Markets entered: `107`
- Markets with multiple entries: `41`
- Markets with side flips: `9`
- Gross P&L: `$8.23`
- Hold P&L: `$23.04`
- Exit value: `$-14.81`
- Churn-market gross P&L: `$-3.07`
- Churn-market hold P&L: `$10.86`
- Churn-market exit value: `$-13.93`

## Markets

| market | trades | sides | flipped | result | gross c | hold c | exit value c |
|---|---:|---|---|---|---:|---:|---:|
| KXBTC15M-26MAY051300-00 | 1 | yes | False | yes | 36.0 | 38.0 | -2.0 |
| KXBTC15M-26MAY051330-30 | 1 | yes | False | yes | 0.0 | 36.0 | -36.0 |
| KXBTC15M-26MAY051545-45 | 1 | yes | False | yes | 16.0 | 50.0 | -34.0 |
| KXBTC15M-26MAY051615-15 | 2 | no>yes | True | yes | 8.0 | -64.0 | 72.0 |
| KXBTC15M-26MAY051715-15 | 3 | yes>yes>yes | False | no | -98.0 | -382.0 | 284.0 |
| KXBTC15M-26MAY051745-45 | 2 | no>no | False | no | -12.0 | 86.0 | -98.0 |
| KXBTC15M-26MAY051800-00 | 2 | yes>yes | False | yes | 16.0 | 84.0 | -68.0 |
| KXBTC15M-26MAY051815-15 | 1 | yes | False | no | 24.0 | -162.0 | 186.0 |
| KXBTC15M-26MAY051830-30 | 1 | no | False | yes | -92.0 | -160.0 | 68.0 |
| KXBTC15M-26MAY051845-45 | 1 | no | False | no | 42.0 | 42.0 | 0.0 |
| KXBTC15M-26MAY051900-00 | 1 | yes | False | yes | 40.0 | 40.0 | 0.0 |
| KXBTC15M-26MAY051915-15 | 1 | yes | False | yes | 34.0 | 36.0 | -2.0 |
| KXBTC15M-26MAY051945-45 | 1 | yes | False | yes | 26.0 | 52.0 | -26.0 |
| KXBTC15M-26MAY052015-15 | 1 | yes | False | yes | 30.0 | 30.0 | 0.0 |
| KXBTC15M-26MAY052045-45 | 2 | yes>yes | False | no | -4.0 | -324.0 | 320.0 |
| KXBTC15M-26MAY052100-00 | 3 | no>yes>yes | True | yes | 16.0 | -50.0 | 66.0 |
| KXBTC15M-26MAY052115-15 | 1 | yes | False | yes | 44.0 | 44.0 | 0.0 |
| KXBTC15M-26MAY052145-45 | 1 | yes | False | yes | 20.0 | 30.0 | -10.0 |
| KXBTC15M-26MAY052200-00 | 1 | yes | False | yes | 12.0 | 42.0 | -30.0 |
| KXBTC15M-26MAY052215-15 | 1 | no | False | no | -14.0 | 34.0 | -48.0 |
| KXBTC15M-26MAY052245-45 | 1 | no | False | yes | -26.0 | -80.0 | 54.0 |
| KXBTC15M-26MAY052300-00 | 1 | yes | False | yes | 28.0 | 30.0 | -2.0 |
| KXBTC15M-26MAY052315-15 | 1 | yes | False | yes | -38.0 | 38.0 | -76.0 |
| KXBTC15M-26MAY060045-45 | 2 | no>no | False | no | 10.0 | 72.0 | -62.0 |
| KXBTC15M-26MAY060100-00 | 1 | no | False | no | -4.0 | 44.0 | -48.0 |
| KXBTC15M-26MAY060145-45 | 1 | no | False | no | 22.0 | 24.0 | -2.0 |
| KXBTC15M-26MAY060200-00 | 2 | yes>yes | False | yes | -6.0 | 78.0 | -84.0 |
| KXBTC15M-26MAY060215-15 | 3 | yes>yes>no | True | no | -8.0 | -280.0 | 272.0 |
| KXBTC15M-26MAY060230-30 | 1 | yes | False | yes | -20.0 | 32.0 | -52.0 |
| KXBTC15M-26MAY060245-45 | 3 | yes>yes>yes | False | yes | 24.0 | 134.0 | -110.0 |
| KXBTC15M-26MAY060300-00 | 4 | yes>yes>yes>yes | False | yes | -38.0 | 156.0 | -194.0 |
| KXBTC15M-26MAY060315-15 | 1 | yes | False | yes | 26.0 | 28.0 | -2.0 |
| KXBTC15M-26MAY060330-30 | 2 | yes>no | True | yes | -70.0 | 24.0 | -94.0 |
| KXBTC15M-26MAY060345-45 | 1 | no | False | no | 34.0 | 44.0 | -10.0 |
| KXBTC15M-26MAY060445-45 | 1 | yes | False | yes | 18.0 | 20.0 | -2.0 |
| KXBTC15M-26MAY060500-00 | 1 | yes | False | yes | 42.0 | 42.0 | 0.0 |
| KXBTC15M-26MAY060515-15 | 2 | no>no | False | no | 16.0 | 94.0 | -78.0 |
| KXBTC15M-26MAY060530-30 | 1 | no | False | no | 34.0 | 44.0 | -10.0 |
| KXBTC15M-26MAY060545-45 | 1 | yes | False | yes | 20.0 | 20.0 | 0.0 |
| KXBTC15M-26MAY060600-00 | 1 | no | False | no | 12.0 | 50.0 | -38.0 |
| KXBTC15M-26MAY060615-15 | 2 | yes>yes | False | yes | -6.0 | 74.0 | -80.0 |
| KXBTC15M-26MAY060630-30 | 2 | yes>yes | False | yes | 16.0 | 72.0 | -56.0 |
| KXBTC15M-26MAY060645-45 | 3 | yes>yes>yes | False | yes | 6.0 | 120.0 | -114.0 |
| KXBTC15M-26MAY060700-00 | 4 | no>yes>yes>yes | True | yes | -48.0 | -38.0 | -10.0 |
| KXBTC15M-26MAY060715-15 | 2 | yes>yes | False | yes | 44.0 | 60.0 | -16.0 |
| KXBTC15M-26MAY060730-30 | 1 | yes | False | yes | 32.0 | 32.0 | 0.0 |
| KXBTC15M-26MAY060745-45 | 2 | yes>yes | False | no | -94.0 | -294.0 | 200.0 |
| KXBTC15M-26MAY060800-00 | 2 | yes>yes | False | yes | -50.0 | 110.0 | -160.0 |
| KXBTC15M-26MAY060815-15 | 1 | no | False | no | 42.0 | 42.0 | 0.0 |
| KXBTC15M-26MAY060830-30 | 1 | yes | False | yes | 48.0 | 48.0 | 0.0 |
| KXBTC15M-26MAY060900-00 | 4 | yes>yes>no>no | True | no | -68.0 | -216.0 | 148.0 |
| KXBTC15M-26MAY060915-15 | 2 | no>no | False | no | 50.0 | 110.0 | -60.0 |
| KXBTC15M-26MAY060930-30 | 4 | no>no>no>no | False | no | 9.0 | 196.0 | -187.0 |
| KXBTC15M-26MAY060945-45 | 4 | no>no>no>no | False | no | 4.0 | 256.0 | -252.0 |
| KXBTC15M-26MAY061000-00 | 1 | no | False | no | 70.0 | 70.0 | 0.0 |
| KXBTC15M-26MAY061015-15 | 3 | no>no>no | False | no | 48.0 | 178.0 | -130.0 |
| KXBTC15M-26MAY061030-30 | 3 | yes>yes>yes | False | yes | 26.0 | 140.0 | -114.0 |
| KXBTC15M-26MAY061045-45 | 2 | yes>yes | False | yes | 22.0 | 72.0 | -50.0 |
| KXBTC15M-26MAY061100-00 | 2 | no>no | False | no | -2.0 | 72.0 | -74.0 |
| KXBTC15M-26MAY061130-30 | 1 | yes | False | yes | 40.0 | 40.0 | 0.0 |
| KXBTC15M-26MAY061200-00 | 1 | yes | False | yes | 16.0 | 36.0 | -20.0 |
| KXBTC15M-26MAY061300-00 | 1 | yes | False | no | -30.0 | -160.0 | 130.0 |
| KXBTC15M-26MAY061400-00 | 1 | no | False | no | -10.0 | 22.0 | -32.0 |
| KXBTC15M-26MAY061415-15 | 1 | no | False | no | 24.0 | 24.0 | 0.0 |
| KXBTC15M-26MAY061445-45 | 2 | no>no | False | no | -4.0 | 44.0 | -48.0 |
| KXBTC15M-26MAY061545-45 | 1 | yes | False | yes | 22.0 | 32.0 | -10.0 |
| KXBTC15M-26MAY061615-15 | 1 | yes | False | yes | 8.0 | 20.0 | -12.0 |
| KXBTC15M-26MAY061645-45 | 1 | no | False | no | 48.0 | 48.0 | 0.0 |
| KXBTC15M-26MAY061800-00 | 1 | no | False | no | -86.0 | 66.0 | -152.0 |
| KXBTC15M-26MAY061815-15 | 1 | no | False | no | 24.0 | 32.0 | -8.0 |
| KXBTC15M-26MAY061830-30 | 1 | no | False | no | 20.0 | 22.0 | -2.0 |
| KXBTC15M-26MAY061900-00 | 1 | yes | False | yes | 20.0 | 20.0 | 0.0 |
| KXBTC15M-26MAY061915-15 | 1 | no | False | no | 24.0 | 26.0 | -2.0 |
| KXBTC15M-26MAY062015-15 | 3 | no>yes>yes | True | no | -186.0 | -190.0 | 4.0 |
| KXBTC15M-26MAY062030-30 | 1 | no | False | no | 32.0 | 66.0 | -34.0 |
| KXBTC15M-26MAY062045-45 | 1 | no | False | no | 24.0 | 40.0 | -16.0 |
| KXBTC15M-26MAY062100-00 | 3 | yes>yes>yes | False | yes | -10.0 | 144.0 | -154.0 |
| KXBTC15M-26MAY062115-15 | 3 | yes>no>yes | True | yes | -24.0 | -60.0 | 36.0 |
| KXBTC15M-26MAY062130-30 | 1 | no | False | yes | -32.0 | -152.0 | 120.0 |
| KXBTC15M-26MAY062215-15 | 2 | no>no | False | no | 24.0 | 102.0 | -78.0 |
| KXBTC15M-26MAY062245-45 | 1 | yes | False | yes | 8.0 | 28.0 | -20.0 |
| KXBTC15M-26MAY062300-00 | 1 | yes | False | yes | 16.0 | 26.0 | -10.0 |
| KXBTC15M-26MAY062315-15 | 1 | no | False | no | 6.0 | 32.0 | -26.0 |
| KXBTC15M-26MAY070000-00 | 1 | no | False | no | 2.0 | 44.0 | -42.0 |
| KXBTC15M-26MAY070015-15 | 1 | no | False | yes | -2.0 | -140.0 | 138.0 |
| KXBTC15M-26MAY070030-30 | 1 | yes | False | yes | 30.0 | 36.0 | -6.0 |
| KXBTC15M-26MAY070115-15 | 1 | yes | False | yes | 0.0 | 36.0 | -36.0 |
| KXBTC15M-26MAY070545-45 | 1 | no | False | no | 18.0 | 36.0 | -18.0 |
| KXBTC15M-26MAY070645-45 | 1 | yes | False | yes | 38.0 | 38.0 | 0.0 |
| KXBTC15M-26MAY070745-45 | 1 | yes | False | yes | 34.0 | 64.0 | -30.0 |
| KXBTC15M-26MAY070815-15 | 1 | yes | False | yes | 2.0 | 20.0 | -18.0 |
| KXBTC15M-26MAY070830-30 | 3 | no>no>no | False | no | 50.0 | 128.0 | -78.0 |
| KXBTC15M-26MAY070915-15 | 1 | no | False | no | 46.0 | 46.0 | 0.0 |
| KXBTC15M-26MAY070930-30 | 1 | yes | False | yes | 34.0 | 40.0 | -6.0 |
| KXBTC15M-26MAY070945-45 | 1 | no | False | no | 62.0 | 62.0 | 0.0 |
| KXBTC15M-26MAY071000-00 | 2 | no>no | False | no | -20.0 | 112.0 | -132.0 |
| KXBTC15M-26MAY071015-15 | 3 | no>no>yes | True | yes | 6.0 | -286.0 | 292.0 |
| KXBTC15M-26MAY071030-30 | 2 | no>no | False | no | 24.0 | 94.0 | -70.0 |
| KXBTC15M-26MAY071045-45 | 2 | no>no | False | no | 40.0 | 102.0 | -62.0 |
| KXBTC15M-26MAY071100-00 | 1 | yes | False | no | 4.0 | -166.0 | 170.0 |
| KXBTC15M-26MAY071115-15 | 1 | yes | False | yes | 14.0 | 32.0 | -18.0 |
| KXBTC15M-26MAY071130-30 | 1 | no | False | no | 30.0 | 30.0 | 0.0 |
| KXBTC15M-26MAY071145-45 | 1 | yes | False | yes | 44.0 | 46.0 | -2.0 |
| KXBTC15M-26MAY071200-00 | 1 | no | False | no | 42.0 | 46.0 | -4.0 |
| KXBTC15M-26MAY071215-15 | 3 | no>no>no | False | no | -22.0 | 116.0 | -138.0 |
| KXBTC15M-26MAY071230-30 | 3 | yes>yes>yes | False | yes | -8.0 | 118.0 | -126.0 |
| KXBTC15M-26MAY071315-15 | 3 | yes>yes>yes | False | yes | 12.0 | 122.0 | -110.0 |

## Trade Detail

### KXBTC15M-26MAY051615-15

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 76 | 64 | -24 | -152 | 128 | mushroom_v28_probability_collapse_full |
| yes | 56 | 72 | 32 | 88 | -56 | mushroom_v28_probability_reduce |

### KXBTC15M-26MAY051715-15

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 82 | 68 | -28 | -164 | 136 | mushroom_v28_probability_reduce |
| yes | 69 | 45 | -48 | -138 | 90 | mushroom_v28_probability_collapse_full |
| yes | 40 | 29 | -22 | -80 | 58 | mushroom_v28_probability_collapse_full |

### KXBTC15M-26MAY051745-45

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 77 | 72 | -10 | 46 | -56 | mushroom_v28_probability_reduce |
| no | 80 | 79 | -2 | 40 | -42 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY051800-00

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 78 | 66 | -24 | 44 | -68 | mushroom_v28_probability_reduce |
| yes | 80 | 100 | 40 | 40 | 0 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY052045-45

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 79 | 70 | -18 | -158 | 140 | mushroom_v28_exit_value_over_hold |
| yes | 83 | 90 | 14 | -166 | 180 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY052100-00

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 79 | 64 | -30 | -158 | 128 | mushroom_v28_probability_collapse_full |
| yes | 56 | 73 | 34 | 88 | -54 | mushroom_v28_exit_value_over_hold |
| yes | 90 | 96 | 12 | 20 | -8 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY060045-45

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 79 | 74 | -10 | 42 | -52 | mushroom_v28_probability_reduce |
| no | 85 | 95 | 20 | 30 | -10 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY060200-00

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 80 | 74 | -12 | 40 | -52 | mushroom_v28_probability_reduce |
| yes | 81 | 84 | 6 | 38 | -32 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY060215-15

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 77 | 69 | -16 | -154 | 138 | mushroom_v28_probability_collapse_full |
| yes | 83 | 70 | -26 | -166 | 140 | mushroom_v28_probability_reduce |
| no | 80 | 97 | 34 | 40 | -6 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY060245-45

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 80 | 76 | -8 | 40 | -48 | mushroom_v28_probability_reduce |
| yes | 77 | 74 | -6 | 46 | -52 | mushroom_v28_probability_reduce |
| yes | 76 | 95 | 38 | 48 | -10 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY060300-00

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 81 | 74 | -14 | 38 | -52 | mushroom_v28_probability_reduce |
| yes | 81 | 66 | -30 | 38 | -68 | mushroom_v28_probability_collapse_full |
| yes | 80 | 69 | -22 | 40 | -62 | mushroom_v28_probability_reduce |
| yes | 80 | 94 | 28 | 40 | -12 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY060330-30

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 79 | 53 | -52 | 42 | -94 | mushroom_v28_exit_value_over_hold |
| no | 9 | None | -18 | -18 | 0 |  |

### KXBTC15M-26MAY060515-15

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 79 | 66 | -26 | 42 | -68 | mushroom_v28_probability_collapse_full |
| no | 74 | 95 | 42 | 52 | -10 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY060615-15

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 75 | 60 | -30 | 50 | -80 | mushroom_v28_probability_collapse_full |
| yes | 88 | None | 24 | 24 | 0 |  |

### KXBTC15M-26MAY060630-30

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 79 | 73 | -12 | 42 | -54 | mushroom_v28_probability_reduce |
| yes | 85 | 99 | 28 | 30 | -2 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY060645-45

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 82 | 74 | -16 | 36 | -52 | mushroom_v28_probability_reduce |
| yes | 78 | 72 | -12 | 44 | -56 | mushroom_v28_probability_reduce |
| yes | 80 | 97 | 34 | 40 | -6 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY060700-00

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 84 | 80 | -8 | -168 | 160 | mushroom_v28_probability_reduce |
| yes | 75 | 64 | -22 | 50 | -72 | mushroom_v28_probability_reduce |
| yes | 77 | 62 | -30 | 46 | -76 | mushroom_v28_probability_collapse_full |
| yes | 83 | 89 | 12 | 34 | -22 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY060715-15

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 81 | 93 | 24 | 38 | -14 | mushroom_v28_exit_value_over_hold |
| yes | 89 | 99 | 20 | 22 | -2 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY060745-45

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 69 | 57 | -24 | -138 | 114 | mushroom_v28_probability_collapse_full |
| yes | 78 | 43 | -70 | -156 | 86 | mushroom_v28_probability_collapse_full |

### KXBTC15M-26MAY060800-00

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 79 | 70 | -18 | 42 | -60 | mushroom_v28_probability_reduce |
| yes | 66 | 50 | -32 | 68 | -100 | mushroom_v28_probability_collapse_full |

### KXBTC15M-26MAY060900-00

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 78 | 73 | -10 | -156 | 146 | mushroom_v28_probability_reduce |
| yes | 78 | 40 | -76 | -156 | 80 | mushroom_v28_probability_collapse_full |
| no | 73 | 65 | -16 | 54 | -70 | mushroom_v28_probability_reduce |
| no | 79 | 96 | 34 | 42 | -8 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY060915-15

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 70 | 70 | 0 | 60 | -60 | mushroom_v28_probability_reduce |
| no | 75 | 100 | 50 | 50 | 0 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY060930-30

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 76 | 66 | -20 | 48 | -68 | mushroom_v28_probability_reduce |
| no | 76 | 69 | -14 | 48 | -62 | mushroom_v28_probability_reduce |
| no | 73 | 72 | -3 | 54 | -57 | mushroom_v28_probability_reduce |
| no | 77 | None | 46 | 46 | 0 |  |

### KXBTC15M-26MAY060945-45

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 59 | 51 | -16 | 82 | -98 | mushroom_v28_probability_collapse_full |
| no | 70 | 62 | -16 | 60 | -76 | mushroom_v28_probability_collapse_full |
| no | 71 | 65 | -12 | 58 | -70 | mushroom_v28_probability_reduce |
| no | 72 | 96 | 48 | 56 | -8 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY061015-15

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 68 | 65 | -6 | 64 | -70 | mushroom_v28_probability_reduce |
| no | 70 | 70 | 0 | 60 | -60 | mushroom_v28_probability_reduce |
| no | 73 | None | 54 | 54 | 0 |  |

### KXBTC15M-26MAY061030-30

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 78 | 70 | -16 | 44 | -60 | mushroom_v28_probability_reduce |
| yes | 78 | 73 | -10 | 44 | -54 | mushroom_v28_probability_reduce |
| yes | 74 | None | 52 | 52 | 0 |  |

### KXBTC15M-26MAY061045-45

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 80 | 77 | -6 | 40 | -46 | mushroom_v28_probability_reduce |
| yes | 84 | 98 | 28 | 32 | -4 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY061100-00

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 83 | 63 | -40 | 34 | -74 | mushroom_v28_probability_collapse_full |
| no | 81 | None | 38 | 38 | 0 |  |

### KXBTC15M-26MAY061445-45

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 88 | 77 | -22 | 24 | -46 | mushroom_v28_probability_reduce |
| no | 90 | 99 | 18 | 20 | -2 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY062015-15

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 42 | 12 | -60 | 116 | -176 | mushroom_v28_probability_collapse_full |
| yes | 86 | 90 | 8 | -172 | 180 | mushroom_v28_exit_value_over_hold |
| yes | 67 | None | -134 | -134 | 0 |  |

### KXBTC15M-26MAY062100-00

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 83 | 81 | -4 | 34 | -38 | mushroom_v28_exit_value_over_hold |
| yes | 84 | 74 | -20 | 32 | -52 | mushroom_v28_exit_value_over_hold |
| yes | 61 | 68 | 14 | 78 | -64 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY062115-15

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 73 | 67 | -12 | 54 | -66 | mushroom_v28_exit_value_over_hold |
| no | 69 | 52 | -34 | -138 | 104 | mushroom_v28_exit_value_over_hold |
| yes | 88 | 99 | 22 | 24 | -2 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY062215-15

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 65 | 72 | 14 | 70 | -56 | mushroom_v28_probability_collapse_full |
| no | 84 | 89 | 10 | 32 | -22 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY070830-30

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 82 | 91 | 18 | 36 | -18 | mushroom_v28_exit_value_over_hold |
| no | 77 | 70 | -14 | 46 | -60 | mushroom_v28_exit_value_over_hold |
| no | 77 | None | 46 | 46 | 0 |  |

### KXBTC15M-26MAY071000-00

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 73 | 55 | -36 | 54 | -90 | mushroom_v28_probability_collapse_full |
| no | 71 | 79 | 16 | 58 | -42 | mushroom_v28_probability_reduce |

### KXBTC15M-26MAY071015-15

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 78 | 79 | 2 | -156 | 158 | mushroom_v28_probability_reduce |
| no | 81 | 73 | -16 | -162 | 146 | mushroom_v28_probability_reduce |
| yes | 84 | 94 | 20 | 32 | -12 | mushroom_v28_exit_value_over_hold |

### KXBTC15M-26MAY071030-30

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 77 | 65 | -24 | 46 | -70 | mushroom_v28_probability_collapse_full |
| no | 76 | None | 48 | 48 | 0 |  |

### KXBTC15M-26MAY071045-45

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 74 | 69 | -10 | 52 | -62 | mushroom_v28_probability_reduce |
| no | 75 | None | 50 | 50 | 0 |  |

### KXBTC15M-26MAY071215-15

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| no | 84 | 76 | -16 | 32 | -48 | mushroom_v28_probability_reduce |
| no | 78 | 79 | 2 | 44 | -42 | mushroom_v28_exit_value_over_hold |
| no | 80 | 76 | -8 | 40 | -48 | mushroom_v28_probability_reduce |

### KXBTC15M-26MAY071230-30

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 77 | 72 | -10 | 46 | -56 | mushroom_v28_probability_reduce |
| yes | 84 | 65 | -38 | 32 | -70 | mushroom_v28_probability_collapse_full |
| yes | 80 | None | 40 | 40 | 0 |  |

### KXBTC15M-26MAY071315-15

| side | entry | exit | gross c | hold c | exit value c | exit reason |
|---|---:|---:|---:|---:|---:|---|
| yes | 80 | 77 | -6 | 40 | -46 | mushroom_v28_probability_reduce |
| yes | 81 | 74 | -14 | 38 | -52 | mushroom_v28_probability_reduce |
| yes | 78 | 94 | 32 | 44 | -12 | mushroom_v28_exit_value_over_hold |

