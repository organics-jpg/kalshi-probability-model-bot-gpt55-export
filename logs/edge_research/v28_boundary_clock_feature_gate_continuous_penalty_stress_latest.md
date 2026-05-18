# v28 Boundary-Clock Feature-Gate Continuous Penalty Stress

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:43:51.108388+00:00`
- Penalty report generated UTC: `2026-05-11T02:43:50.783408+00:00`
- Penalty freeze UTC: `2026-05-06T18:50:42.450675+00:00`

## Interpretation

- This is a source/runway/outlier stress audit of the continuous cheap-side penalty; it is not promotion evidence.
- diagnostic_entry: diagnostic_entry_cheap_penalty025_rank_only has 86 settled, coverage 71.07438016528926%, net 941.0c, recon share 0.13953488372093023; needs 19 clean selected rows for count gates and 0.0c for cushion, top win 96.0c leaves 845.0c without it, top-PnL variant diagnostic_entry_cheap_penalty025_rank_only nets 941.0c, blockers ['coverage_too_low'].
- diagnostic_bridge: diagnostic_bridge_cheap_penalty025_rank_only has 84 settled, coverage 70.58823529411765%, net 933.0c, recon share 0.14285714285714285; needs 21 clean selected rows for count gates and 0.0c for cushion, top win 96.0c leaves 837.0c without it, top-PnL variant diagnostic_bridge_cheap_penalty025_rank_only nets 933.0c, blockers ['coverage_too_low'].
- pre_penalty_birth_feature_entry: pre_penalty_birth_feature_entry_cheap_penalty025_rank_only has 55 settled, coverage 67.07317073170732%, net 527.0c, recon share 0.18181818181818182; needs 26 clean selected rows for count gates and 0.0c for cushion, top win 96.0c leaves 431.0c without it, top-PnL variant pre_penalty_birth_feature_entry_cheap_penalty025_rank_only nets 527.0c, blockers ['coverage_too_low'].
- pre_penalty_birth_feature_bridge: pre_penalty_birth_feature_bridge_cheap_penalty025_rank_only has 55 settled, coverage 67.07317073170732%, net 527.0c, recon share 0.18181818181818182; needs 26 clean selected rows for count gates and 0.0c for cushion, top win 96.0c leaves 431.0c without it, top-PnL variant pre_penalty_birth_feature_bridge_cheap_penalty025_rank_only nets 527.0c, blockers ['coverage_too_low'].
- post_penalty_birth_entry: post_penalty_birth_entry_cheap_penalty025_rank_only has 51 settled, coverage 66.23376623376623%, net 504.0c, recon share 0.17647058823529413; needs 27 clean selected rows for count gates and 0.0c for cushion, top win 96.0c leaves 408.0c without it, top-PnL variant post_penalty_birth_entry_cheap_penalty025_rank_only nets 504.0c, blockers ['coverage_too_low'].
- post_penalty_birth_bridge: post_penalty_birth_bridge_cheap_penalty025_rank_only has 51 settled, coverage 66.23376623376623%, net 504.0c, recon share 0.17647058823529413; needs 27 clean selected rows for count gates and 0.0c for cushion, top win 96.0c leaves 408.0c without it, top-PnL variant post_penalty_birth_bridge_cheap_penalty025_rank_only nets 504.0c, blockers ['coverage_too_low'].

## Lanes

| lane | candidate | selected/den | settled | W/L | coverage | net c | recon | approved net | recon net | top win | net ex top | clean rows needed | cushion c needed | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| diagnostic_entry | diagnostic_entry_cheap_penalty025_rank_only | 86/121 | 86 | 72/14 | 71.074380 | 941.000000 | 0.139535 | 858.000000 | 83.000000 | 96.000000 | 845.000000 | 19 | 0.000000 | coverage_too_low |
| diagnostic_bridge | diagnostic_bridge_cheap_penalty025_rank_only | 84/119 | 84 | 71/13 | 70.588235 | 933.000000 | 0.142857 | 850.000000 | 83.000000 | 96.000000 | 837.000000 | 21 | 0.000000 | coverage_too_low |
| pre_penalty_birth_feature_entry | pre_penalty_birth_feature_entry_cheap_penalty025_rank_only | 55/82 | 55 | 44/11 | 67.073171 | 527.000000 | 0.181818 | 457.000000 | 70.000000 | 96.000000 | 431.000000 | 26 | 0.000000 | coverage_too_low |
| pre_penalty_birth_feature_bridge | pre_penalty_birth_feature_bridge_cheap_penalty025_rank_only | 55/82 | 55 | 44/11 | 67.073171 | 527.000000 | 0.181818 | 457.000000 | 70.000000 | 96.000000 | 431.000000 | 26 | 0.000000 | coverage_too_low |
| post_penalty_birth_entry | post_penalty_birth_entry_cheap_penalty025_rank_only | 51/77 | 51 | 41/10 | 66.233766 | 504.000000 | 0.176471 | 429.000000 | 75.000000 | 96.000000 | 408.000000 | 27 | 0.000000 | coverage_too_low |
| post_penalty_birth_bridge | post_penalty_birth_bridge_cheap_penalty025_rank_only | 51/77 | 51 | 41/10 | 66.233766 | 504.000000 | 0.176471 | 429.000000 | 75.000000 | 96.000000 | 408.000000 | 27 | 0.000000 | coverage_too_low |

## diagnostic_entry Details

- Source split: `{'approved_entry': {'rows': 74, 'wins': 67, 'losses': 7, 'net_cents': 858.0, 'avg_net_cents': 11.594594594594595}, 'rejected_actionable': {'rows': 12, 'wins': 5, 'losses': 7, 'net_cents': 83.0, 'avg_net_cents': 6.916666666666667}}`
- Top win row: `{'abs_d_sigma': 0.971992, 'adjusted_edge': -0.066278, 'ask_prob': 0.03, 'cheap_gap': 0.62, 'market': 'KXBTC15M-26MAY061630-30', 'net_cents': 96.0, 'raw_edge': 0.088722, 'recross_hazard_score': 0.07161829905897715, 'side': 'no', 'side_won': True, 'source': 'rejected_actionable'}`
- Worst loss row: `{'abs_d_sigma': 1.010241, 'adjusted_edge': 0.054041000000000006, 'ask_prob': 0.83, 'cheap_gap': 0.0, 'market': 'KXBTC15M-26MAY071100-00', 'net_cents': -84.0, 'raw_edge': 0.054041000000000006, 'recross_hazard_score': 0.30500573389101787, 'side': 'yes', 'side_won': False, 'source': 'approved_entry'}`

### Variant Stress

| candidate | selected/den | coverage | net c | recon | clean rows needed | cushion c needed | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| diagnostic_entry_cheap_penalty025_rank_only | 86/121 | 71.074380 | 941.000000 | 0.139535 | 19 | 0.000000 | coverage_too_low |
| diagnostic_entry_cheap_penalty050_rank_only | 86/121 | 71.074380 | 940.000000 | 0.139535 | 19 | 0.000000 | coverage_too_low |
| diagnostic_entry_cheap_penalty100_rank_only | 86/121 | 71.074380 | 940.000000 | 0.139535 | 19 | 0.000000 | coverage_too_low |
| diagnostic_entry_cheap_penalty050_floor05 | 78/121 | 64.462810 | 885.000000 | 0.051282 | 51 | 0.000000 | coverage_too_low |

## diagnostic_bridge Details

- Source split: `{'approved_entry': {'rows': 72, 'wins': 66, 'losses': 6, 'net_cents': 850.0, 'avg_net_cents': 11.805555555555555}, 'rejected_actionable': {'rows': 12, 'wins': 5, 'losses': 7, 'net_cents': 83.0, 'avg_net_cents': 6.916666666666667}}`
- Top win row: `{'abs_d_sigma': 0.971992, 'adjusted_edge': -0.066278, 'ask_prob': 0.03, 'cheap_gap': 0.62, 'market': 'KXBTC15M-26MAY061630-30', 'net_cents': 96.0, 'raw_edge': 0.088722, 'recross_hazard_score': 0.07161829905897715, 'side': 'no', 'side_won': True, 'source': 'rejected_actionable'}`
- Worst loss row: `{'abs_d_sigma': 1.010241, 'adjusted_edge': 0.054041000000000006, 'ask_prob': 0.83, 'cheap_gap': 0.0, 'market': 'KXBTC15M-26MAY071100-00', 'net_cents': -84.0, 'raw_edge': 0.054041000000000006, 'recross_hazard_score': 0.30500573389101787, 'side': 'yes', 'side_won': False, 'source': 'approved_entry'}`

### Variant Stress

| candidate | selected/den | coverage | net c | recon | clean rows needed | cushion c needed | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| diagnostic_bridge_cheap_penalty025_rank_only | 84/119 | 70.588235 | 933.000000 | 0.142857 | 21 | 0.000000 | coverage_too_low |
| diagnostic_bridge_cheap_penalty050_rank_only | 84/119 | 70.588235 | 932.000000 | 0.142857 | 21 | 0.000000 | coverage_too_low |
| diagnostic_bridge_cheap_penalty100_rank_only | 84/119 | 70.588235 | 932.000000 | 0.142857 | 21 | 0.000000 | coverage_too_low |
| diagnostic_bridge_cheap_penalty050_floor05 | 76/119 | 63.865546 | 877.000000 | 0.052632 | 53 | 0.000000 | coverage_too_low |

## pre_penalty_birth_feature_entry Details

- Source split: `{'approved_entry': {'rows': 45, 'wins': 41, 'losses': 4, 'net_cents': 457.0, 'avg_net_cents': 10.155555555555555}, 'rejected_actionable': {'rows': 10, 'wins': 3, 'losses': 7, 'net_cents': 70.0, 'avg_net_cents': 7.0}}`
- Top win row: `{'abs_d_sigma': 0.971992, 'adjusted_edge': -0.066278, 'ask_prob': 0.03, 'cheap_gap': 0.62, 'market': 'KXBTC15M-26MAY061630-30', 'net_cents': 96.0, 'raw_edge': 0.088722, 'recross_hazard_score': 0.07161829905897715, 'side': 'no', 'side_won': True, 'source': 'rejected_actionable'}`
- Worst loss row: `{'abs_d_sigma': 1.010241, 'adjusted_edge': 0.054041000000000006, 'ask_prob': 0.83, 'cheap_gap': 0.0, 'market': 'KXBTC15M-26MAY071100-00', 'net_cents': -84.0, 'raw_edge': 0.054041000000000006, 'recross_hazard_score': 0.30500573389101787, 'side': 'yes', 'side_won': False, 'source': 'approved_entry'}`

### Variant Stress

| candidate | selected/den | coverage | net c | recon | clean rows needed | cushion c needed | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| pre_penalty_birth_feature_entry_cheap_penalty025_rank_only | 55/82 | 67.073171 | 527.000000 | 0.181818 | 26 | 0.000000 | coverage_too_low |
| pre_penalty_birth_feature_entry_cheap_penalty050_rank_only | 55/82 | 67.073171 | 526.000000 | 0.181818 | 26 | 0.000000 | coverage_too_low |
| pre_penalty_birth_feature_entry_cheap_penalty100_rank_only | 55/82 | 67.073171 | 526.000000 | 0.181818 | 26 | 0.000000 | coverage_too_low |
| pre_penalty_birth_feature_entry_cheap_penalty050_floor05 | 47/82 | 57.317073 | 471.000000 | 0.042553 | 58 | 0.000000 | coverage_too_low |

## pre_penalty_birth_feature_bridge Details

- Source split: `{'approved_entry': {'rows': 45, 'wins': 41, 'losses': 4, 'net_cents': 457.0, 'avg_net_cents': 10.155555555555555}, 'rejected_actionable': {'rows': 10, 'wins': 3, 'losses': 7, 'net_cents': 70.0, 'avg_net_cents': 7.0}}`
- Top win row: `{'abs_d_sigma': 0.971992, 'adjusted_edge': -0.066278, 'ask_prob': 0.03, 'cheap_gap': 0.62, 'market': 'KXBTC15M-26MAY061630-30', 'net_cents': 96.0, 'raw_edge': 0.088722, 'recross_hazard_score': 0.07161829905897715, 'side': 'no', 'side_won': True, 'source': 'rejected_actionable'}`
- Worst loss row: `{'abs_d_sigma': 1.010241, 'adjusted_edge': 0.054041000000000006, 'ask_prob': 0.83, 'cheap_gap': 0.0, 'market': 'KXBTC15M-26MAY071100-00', 'net_cents': -84.0, 'raw_edge': 0.054041000000000006, 'recross_hazard_score': 0.30500573389101787, 'side': 'yes', 'side_won': False, 'source': 'approved_entry'}`

### Variant Stress

| candidate | selected/den | coverage | net c | recon | clean rows needed | cushion c needed | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| pre_penalty_birth_feature_bridge_cheap_penalty025_rank_only | 55/82 | 67.073171 | 527.000000 | 0.181818 | 26 | 0.000000 | coverage_too_low |
| pre_penalty_birth_feature_bridge_cheap_penalty050_rank_only | 55/82 | 67.073171 | 526.000000 | 0.181818 | 26 | 0.000000 | coverage_too_low |
| pre_penalty_birth_feature_bridge_cheap_penalty100_rank_only | 55/82 | 67.073171 | 526.000000 | 0.181818 | 26 | 0.000000 | coverage_too_low |
| pre_penalty_birth_feature_bridge_cheap_penalty050_floor05 | 47/82 | 57.317073 | 471.000000 | 0.042553 | 58 | 0.000000 | coverage_too_low |

## post_penalty_birth_entry Details

- Source split: `{'approved_entry': {'rows': 42, 'wins': 38, 'losses': 4, 'net_cents': 429.0, 'avg_net_cents': 10.214285714285714}, 'rejected_actionable': {'rows': 9, 'wins': 3, 'losses': 6, 'net_cents': 75.0, 'avg_net_cents': 8.333333333333334}}`
- Top win row: `{'abs_d_sigma': 0.971992, 'adjusted_edge': -0.066278, 'ask_prob': 0.03, 'cheap_gap': 0.62, 'market': 'KXBTC15M-26MAY061630-30', 'net_cents': 96.0, 'raw_edge': 0.088722, 'recross_hazard_score': 0.07161829905897715, 'side': 'no', 'side_won': True, 'source': 'rejected_actionable'}`
- Worst loss row: `{'abs_d_sigma': 1.010241, 'adjusted_edge': 0.054041000000000006, 'ask_prob': 0.83, 'cheap_gap': 0.0, 'market': 'KXBTC15M-26MAY071100-00', 'net_cents': -84.0, 'raw_edge': 0.054041000000000006, 'recross_hazard_score': 0.30500573389101787, 'side': 'yes', 'side_won': False, 'source': 'approved_entry'}`

### Variant Stress

| candidate | selected/den | coverage | net c | recon | clean rows needed | cushion c needed | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| post_penalty_birth_entry_cheap_penalty025_rank_only | 51/77 | 66.233766 | 504.000000 | 0.176471 | 27 | 0.000000 | coverage_too_low |
| post_penalty_birth_entry_cheap_penalty050_rank_only | 51/77 | 66.233766 | 504.000000 | 0.176471 | 27 | 0.000000 | coverage_too_low |
| post_penalty_birth_entry_cheap_penalty100_rank_only | 51/77 | 66.233766 | 504.000000 | 0.176471 | 27 | 0.000000 | coverage_too_low |
| post_penalty_birth_entry_cheap_penalty050_floor05 | 44/77 | 57.142857 | 443.000000 | 0.045455 | 55 | 0.000000 | coverage_too_low |

## post_penalty_birth_bridge Details

- Source split: `{'approved_entry': {'rows': 42, 'wins': 38, 'losses': 4, 'net_cents': 429.0, 'avg_net_cents': 10.214285714285714}, 'rejected_actionable': {'rows': 9, 'wins': 3, 'losses': 6, 'net_cents': 75.0, 'avg_net_cents': 8.333333333333334}}`
- Top win row: `{'abs_d_sigma': 0.971992, 'adjusted_edge': -0.066278, 'ask_prob': 0.03, 'cheap_gap': 0.62, 'market': 'KXBTC15M-26MAY061630-30', 'net_cents': 96.0, 'raw_edge': 0.088722, 'recross_hazard_score': 0.07161829905897715, 'side': 'no', 'side_won': True, 'source': 'rejected_actionable'}`
- Worst loss row: `{'abs_d_sigma': 1.010241, 'adjusted_edge': 0.054041000000000006, 'ask_prob': 0.83, 'cheap_gap': 0.0, 'market': 'KXBTC15M-26MAY071100-00', 'net_cents': -84.0, 'raw_edge': 0.054041000000000006, 'recross_hazard_score': 0.30500573389101787, 'side': 'yes', 'side_won': False, 'source': 'approved_entry'}`

### Variant Stress

| candidate | selected/den | coverage | net c | recon | clean rows needed | cushion c needed | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| post_penalty_birth_bridge_cheap_penalty025_rank_only | 51/77 | 66.233766 | 504.000000 | 0.176471 | 27 | 0.000000 | coverage_too_low |
| post_penalty_birth_bridge_cheap_penalty050_rank_only | 51/77 | 66.233766 | 504.000000 | 0.176471 | 27 | 0.000000 | coverage_too_low |
| post_penalty_birth_bridge_cheap_penalty100_rank_only | 51/77 | 66.233766 | 504.000000 | 0.176471 | 27 | 0.000000 | coverage_too_low |
| post_penalty_birth_bridge_cheap_penalty050_floor05 | 44/77 | 57.142857 | 443.000000 | 0.045455 | 55 | 0.000000 | coverage_too_low |
