# v28 Boundary-Clock Feature-Gate Continuous Penalty

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:43:50.783408+00:00`
- Penalty freeze UTC: `2026-05-06T18:50:42.450675+00:00`

## Interpretation

- Continuous penalties rank eligible rows by raw_edge minus lambda times cheap-side gap max(0, 0.65 - ask_prob).
- Only post_penalty_birth lanes are strict forward evidence for this new challenger.
- diagnostic_entry: best diagnostic_entry_cheap_penalty025_rank_only settled 86, coverage 71.07438016528926%, net 941.0c, recon 0.13953488372093023, blockers ['coverage_too_low'].
- diagnostic_bridge: best diagnostic_bridge_cheap_penalty025_rank_only settled 84, coverage 70.58823529411765%, net 933.0c, recon 0.14285714285714285, blockers ['coverage_too_low'].
- pre_penalty_birth_feature_entry: best pre_penalty_birth_feature_entry_cheap_penalty025_rank_only settled 55, coverage 67.07317073170732%, net 527.0c, recon 0.18181818181818182, blockers ['coverage_too_low'].
- pre_penalty_birth_feature_bridge: best pre_penalty_birth_feature_bridge_cheap_penalty025_rank_only settled 55, coverage 67.07317073170732%, net 527.0c, recon 0.18181818181818182, blockers ['coverage_too_low'].
- post_penalty_birth_entry: best post_penalty_birth_entry_cheap_penalty025_rank_only settled 51, coverage 66.23376623376623%, net 504.0c, recon 0.17647058823529413, blockers ['coverage_too_low'].
- post_penalty_birth_bridge: best post_penalty_birth_bridge_cheap_penalty025_rank_only settled 51, coverage 66.23376623376623%, net 504.0c, recon 0.17647058823529413, blockers ['coverage_too_low'].

## diagnostic_entry

| rank | candidate | settled/den | W/L | coverage | net c | recon | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | diagnostic_entry_cheap_penalty025_rank_only | 86/121 | 72/14 | 71.074380 | 941.000000 | 0.139535 | 9 | coverage_too_low |
| 2 | diagnostic_entry_cheap_penalty050_rank_only | 86/121 | 72/14 | 71.074380 | 940.000000 | 0.139535 | 9 | coverage_too_low |
| 3 | diagnostic_entry_cheap_penalty100_rank_only | 86/121 | 72/14 | 71.074380 | 940.000000 | 0.139535 | 9 | coverage_too_low |
| 4 | diagnostic_entry_cheap_penalty050_floor05 | 78/121 | 71/7 | 64.462810 | 885.000000 | 0.051282 | 8 | coverage_too_low |

### Best-Lane Worst Rows

| market | source | side | won | net c | raw edge | cheap gap | adjusted edge | recross | abs d | ask |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.060906 | 0.000000 | 0.060906 | 0.301730 | 0.913273 | 0.800000 |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 |
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -71.000000 | 0.161843 | 0.000000 | 0.161843 | 0.303224 | 0.889718 | 0.690000 |
| KXBTC15M-26MAY060330-30 | approved_entry | no | False | -11.000000 | 0.909788 | 0.560000 | 0.769788 | 0.002807 | 3.991247 | 0.090000 |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.570000 | -0.089265 | 0.083861 | 0.932497 | 0.080000 |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.590000 | -0.089915 | 0.083577 | 0.967753 | 0.060000 |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.600000 | -0.072482 | 0.050841 | 0.913861 | 0.050000 |

## diagnostic_bridge

| rank | candidate | settled/den | W/L | coverage | net c | recon | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | diagnostic_bridge_cheap_penalty025_rank_only | 84/119 | 71/13 | 70.588235 | 933.000000 | 0.142857 | 9 | coverage_too_low |
| 2 | diagnostic_bridge_cheap_penalty050_rank_only | 84/119 | 71/13 | 70.588235 | 932.000000 | 0.142857 | 9 | coverage_too_low |
| 3 | diagnostic_bridge_cheap_penalty100_rank_only | 84/119 | 71/13 | 70.588235 | 932.000000 | 0.142857 | 9 | coverage_too_low |
| 4 | diagnostic_bridge_cheap_penalty050_floor05 | 76/119 | 70/6 | 63.865546 | 877.000000 | 0.052632 | 8 | coverage_too_low |

### Best-Lane Worst Rows

| market | source | side | won | net c | raw edge | cheap gap | adjusted edge | recross | abs d | ask |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.060906 | 0.000000 | 0.060906 | 0.301730 | 0.913273 | 0.800000 |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 |
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -71.000000 | 0.161843 | 0.000000 | 0.161843 | 0.303224 | 0.889718 | 0.690000 |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.570000 | -0.089265 | 0.083861 | 0.932497 | 0.080000 |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.590000 | -0.089915 | 0.083577 | 0.967753 | 0.060000 |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.600000 | -0.072482 | 0.050841 | 0.913861 | 0.050000 |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.610000 | -0.090174 | 0.081020 | 1.050761 | 0.040000 |

## pre_penalty_birth_feature_entry

| rank | candidate | settled/den | W/L | coverage | net c | recon | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | pre_penalty_birth_feature_entry_cheap_penalty025_rank_only | 55/82 | 44/11 | 67.073171 | 527.000000 | 0.181818 | 5 | coverage_too_low |
| 2 | pre_penalty_birth_feature_entry_cheap_penalty050_rank_only | 55/82 | 44/11 | 67.073171 | 526.000000 | 0.181818 | 5 | coverage_too_low |
| 3 | pre_penalty_birth_feature_entry_cheap_penalty100_rank_only | 55/82 | 44/11 | 67.073171 | 526.000000 | 0.181818 | 5 | coverage_too_low |
| 4 | pre_penalty_birth_feature_entry_cheap_penalty050_floor05 | 47/82 | 43/4 | 57.317073 | 471.000000 | 0.042553 | 4 | coverage_too_low |

### Best-Lane Worst Rows

| market | source | side | won | net c | raw edge | cheap gap | adjusted edge | recross | abs d | ask |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.570000 | -0.089265 | 0.083861 | 0.932497 | 0.080000 |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.590000 | -0.089915 | 0.083577 | 0.967753 | 0.060000 |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.600000 | -0.072482 | 0.050841 | 0.913861 | 0.050000 |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.610000 | -0.090174 | 0.081020 | 1.050761 | 0.040000 |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.610000 | -0.071878 | 0.099074 | 0.943937 | 0.040000 |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.620000 | -0.077115 | 0.087550 | 0.997935 | 0.030000 |

## pre_penalty_birth_feature_bridge

| rank | candidate | settled/den | W/L | coverage | net c | recon | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | pre_penalty_birth_feature_bridge_cheap_penalty025_rank_only | 55/82 | 44/11 | 67.073171 | 527.000000 | 0.181818 | 5 | coverage_too_low |
| 2 | pre_penalty_birth_feature_bridge_cheap_penalty050_rank_only | 55/82 | 44/11 | 67.073171 | 526.000000 | 0.181818 | 5 | coverage_too_low |
| 3 | pre_penalty_birth_feature_bridge_cheap_penalty100_rank_only | 55/82 | 44/11 | 67.073171 | 526.000000 | 0.181818 | 5 | coverage_too_low |
| 4 | pre_penalty_birth_feature_bridge_cheap_penalty050_floor05 | 47/82 | 43/4 | 57.317073 | 471.000000 | 0.042553 | 4 | coverage_too_low |

### Best-Lane Worst Rows

| market | source | side | won | net c | raw edge | cheap gap | adjusted edge | recross | abs d | ask |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.570000 | -0.089265 | 0.083861 | 0.932497 | 0.080000 |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.590000 | -0.089915 | 0.083577 | 0.967753 | 0.060000 |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.600000 | -0.072482 | 0.050841 | 0.913861 | 0.050000 |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.610000 | -0.090174 | 0.081020 | 1.050761 | 0.040000 |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.610000 | -0.071878 | 0.099074 | 0.943937 | 0.040000 |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.620000 | -0.077115 | 0.087550 | 0.997935 | 0.030000 |

## post_penalty_birth_entry

| rank | candidate | settled/den | W/L | coverage | net c | recon | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | post_penalty_birth_entry_cheap_penalty025_rank_only | 51/77 | 41/10 | 66.233766 | 504.000000 | 0.176471 | 5 | coverage_too_low |
| 2 | post_penalty_birth_entry_cheap_penalty050_rank_only | 51/77 | 41/10 | 66.233766 | 504.000000 | 0.176471 | 5 | coverage_too_low |
| 3 | post_penalty_birth_entry_cheap_penalty100_rank_only | 51/77 | 41/10 | 66.233766 | 504.000000 | 0.176471 | 5 | coverage_too_low |
| 4 | post_penalty_birth_entry_cheap_penalty050_floor05 | 44/77 | 40/4 | 57.142857 | 443.000000 | 0.045455 | 4 | coverage_too_low |

### Best-Lane Worst Rows

| market | source | side | won | net c | raw edge | cheap gap | adjusted edge | recross | abs d | ask |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.570000 | -0.089265 | 0.083861 | 0.932497 | 0.080000 |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.590000 | -0.089915 | 0.083577 | 0.967753 | 0.060000 |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.600000 | -0.072482 | 0.050841 | 0.913861 | 0.050000 |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.610000 | -0.071878 | 0.099074 | 0.943937 | 0.040000 |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.620000 | -0.077115 | 0.087550 | 0.997935 | 0.030000 |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.630000 | -0.081523 | 0.038855 | 1.069646 | 0.020000 |

## post_penalty_birth_bridge

| rank | candidate | settled/den | W/L | coverage | net c | recon | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | post_penalty_birth_bridge_cheap_penalty025_rank_only | 51/77 | 41/10 | 66.233766 | 504.000000 | 0.176471 | 5 | coverage_too_low |
| 2 | post_penalty_birth_bridge_cheap_penalty050_rank_only | 51/77 | 41/10 | 66.233766 | 504.000000 | 0.176471 | 5 | coverage_too_low |
| 3 | post_penalty_birth_bridge_cheap_penalty100_rank_only | 51/77 | 41/10 | 66.233766 | 504.000000 | 0.176471 | 5 | coverage_too_low |
| 4 | post_penalty_birth_bridge_cheap_penalty050_floor05 | 44/77 | 40/4 | 57.142857 | 443.000000 | 0.045455 | 4 | coverage_too_low |

### Best-Lane Worst Rows

| market | source | side | won | net c | raw edge | cheap gap | adjusted edge | recross | abs d | ask |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.570000 | -0.089265 | 0.083861 | 0.932497 | 0.080000 |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.590000 | -0.089915 | 0.083577 | 0.967753 | 0.060000 |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.600000 | -0.072482 | 0.050841 | 0.913861 | 0.050000 |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.610000 | -0.071878 | 0.099074 | 0.943937 | 0.040000 |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.620000 | -0.077115 | 0.087550 | 0.997935 | 0.030000 |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.630000 | -0.081523 | 0.038855 | 1.069646 | 0.020000 |
