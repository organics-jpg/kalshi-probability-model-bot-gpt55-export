# v28 Boundary-Clock Feature-Gate Residual Loss Mechanism

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:43:51.250389+00:00`
- Penalty freeze UTC: `2026-05-06T18:50:42.450675+00:00`
- Prototype source: `diagnostic_entry`
- Prototype count: `14`
- Prototype tags: `{'cheap_side_residual': 8, 'expensive_yes_near_boundary': 2, 'fv_overconfidence': 3, 'moderate_recross_reversal': 5, 'source_quality_error': 7, 'thin_edge_expensive_touch': 5, 'weak_boundary_distance': 6}`

## Interpretation

- Residual loss prototypes are the selected diagnostic losses after the continuous cheap-side penalty repair.
- Prototype tags are {'cheap_side_residual': 8, 'expensive_yes_near_boundary': 2, 'fv_overconfidence': 3, 'moderate_recross_reversal': 5, 'source_quality_error': 7, 'thin_edge_expensive_touch': 5, 'weak_boundary_distance': 6}.
- pre_penalty_birth_feature_entry: pre_penalty_birth_feature_entry_cheap_penalty025_rank_only has residual scores {'rows': 55, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 0.8141394809787905, 'tag_counts': {'cheap_side_residual': 9, 'clean_or_unclassified': 5, 'expensive_yes_near_boundary': 5, 'fv_overconfidence': 11, 'moderate_recross_reversal': 22, 'source_quality_error': 10, 'thin_edge_expensive_touch': 18, 'weak_boundary_distance': 19}} and loss scores {'rows': 11, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 1.0, 'tag_counts': {'cheap_side_residual': 7, 'fv_overconfidence': 2, 'moderate_recross_reversal': 3, 'source_quality_error': 7, 'thin_edge_expensive_touch': 4, 'weak_boundary_distance': 4}}.
- post_penalty_birth_entry: post_penalty_birth_entry_cheap_penalty025_rank_only has residual scores {'rows': 51, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 0.8212421582884395, 'tag_counts': {'cheap_side_residual': 8, 'clean_or_unclassified': 4, 'expensive_yes_near_boundary': 5, 'fv_overconfidence': 11, 'moderate_recross_reversal': 21, 'source_quality_error': 9, 'thin_edge_expensive_touch': 15, 'weak_boundary_distance': 19}} and loss scores {'rows': 10, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 1.0, 'tag_counts': {'cheap_side_residual': 6, 'fv_overconfidence': 2, 'moderate_recross_reversal': 3, 'source_quality_error': 6, 'thin_edge_expensive_touch': 3, 'weak_boundary_distance': 4}}.

## diagnostic_entry

- Candidate: `diagnostic_entry_cheap_penalty025_rank_only`
- Summary: `{'avg_net_cents': 10.94186046511628, 'coverage_pct': 71.07438016528926, 'entries': 86, 'losses': 14, 'net_cents': 941.0, 'settled': 86, 'wins': 72}`
- Residual scores: `{'rows': 86, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 0.8199184448894523, 'tag_counts': {'cheap_side_residual': 11, 'clean_or_unclassified': 5, 'expensive_yes_near_boundary': 18, 'fv_overconfidence': 21, 'moderate_recross_reversal': 40, 'source_quality_error': 12, 'thin_edge_expensive_touch': 27, 'weak_boundary_distance': 37}}`
- Loss scores: `{'rows': 14, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 1.0, 'tag_counts': {'cheap_side_residual': 8, 'expensive_yes_near_boundary': 2, 'fv_overconfidence': 3, 'moderate_recross_reversal': 5, 'source_quality_error': 7, 'thin_edge_expensive_touch': 5, 'weak_boundary_distance': 6}}`

### Top Residual Analogs

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest residual loss | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | 1.000000 | KXBTC15M-26MAY071100-00 | moderate_recross_reversal, thin_edge_expensive_touch |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.060906 | 0.301730 | 0.913273 | 0.800000 | 1.000000 | KXBTC15M-26MAY061300-00 | expensive_yes_near_boundary, moderate_recross_reversal, thin_edge_expensive_touch, weak_boundary_distance |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | 1.000000 | KXBTC15M-26MAY071015-15 | moderate_recross_reversal, weak_boundary_distance |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | 1.000000 | KXBTC15M-26MAY062130-30 | moderate_recross_reversal, fv_overconfidence |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | 1.000000 | KXBTC15M-26MAY070015-15 | fv_overconfidence |
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -71.000000 | 0.161843 | 0.303224 | 0.889718 | 0.690000 | 1.000000 | KXBTC15M-26MAY060745-45 | expensive_yes_near_boundary, moderate_recross_reversal, fv_overconfidence, weak_boundary_distance |
| KXBTC15M-26MAY060330-30 | approved_entry | no | False | -11.000000 | 0.909788 | 0.002807 | 3.991247 | 0.090000 | 1.000000 | KXBTC15M-26MAY060330-30 | cheap_side_residual |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | 1.000000 | KXBTC15M-26MAY071300-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | 1.000000 | KXBTC15M-26MAY061600-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | 1.000000 | KXBTC15M-26MAY070200-00 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | 1.000000 | KXBTC15M-26MAY061430-30 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | source_quality_error, cheap_side_residual, weak_boundary_distance |

### Loss Rows

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest residual loss | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | 1.000000 | KXBTC15M-26MAY071100-00 | moderate_recross_reversal, thin_edge_expensive_touch |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.060906 | 0.301730 | 0.913273 | 0.800000 | 1.000000 | KXBTC15M-26MAY061300-00 | expensive_yes_near_boundary, moderate_recross_reversal, thin_edge_expensive_touch, weak_boundary_distance |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | 1.000000 | KXBTC15M-26MAY071015-15 | moderate_recross_reversal, weak_boundary_distance |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | 1.000000 | KXBTC15M-26MAY062130-30 | moderate_recross_reversal, fv_overconfidence |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | 1.000000 | KXBTC15M-26MAY070015-15 | fv_overconfidence |
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -71.000000 | 0.161843 | 0.303224 | 0.889718 | 0.690000 | 1.000000 | KXBTC15M-26MAY060745-45 | expensive_yes_near_boundary, moderate_recross_reversal, fv_overconfidence, weak_boundary_distance |
| KXBTC15M-26MAY060330-30 | approved_entry | no | False | -11.000000 | 0.909788 | 0.002807 | 3.991247 | 0.090000 | 1.000000 | KXBTC15M-26MAY060330-30 | cheap_side_residual |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | 1.000000 | KXBTC15M-26MAY071300-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | 1.000000 | KXBTC15M-26MAY061600-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | 1.000000 | KXBTC15M-26MAY070200-00 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | 1.000000 | KXBTC15M-26MAY061430-30 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | 1.000000 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | 1.000000 | KXBTC15M-26MAY061530-30 | source_quality_error, cheap_side_residual |

## diagnostic_bridge

- Candidate: `diagnostic_bridge_cheap_penalty025_rank_only`
- Summary: `{'avg_net_cents': 11.107142857142858, 'coverage_pct': 70.58823529411765, 'entries': 84, 'losses': 13, 'net_cents': 933.0, 'settled': 84, 'wins': 71}`
- Residual scores: `{'rows': 84, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 0.8165340964620688, 'tag_counts': {'cheap_side_residual': 10, 'clean_or_unclassified': 5, 'expensive_yes_near_boundary': 18, 'fv_overconfidence': 21, 'moderate_recross_reversal': 39, 'source_quality_error': 12, 'thin_edge_expensive_touch': 27, 'weak_boundary_distance': 37}}`
- Loss scores: `{'rows': 13, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 1.0, 'tag_counts': {'cheap_side_residual': 7, 'expensive_yes_near_boundary': 2, 'fv_overconfidence': 3, 'moderate_recross_reversal': 5, 'source_quality_error': 7, 'thin_edge_expensive_touch': 5, 'weak_boundary_distance': 6}}`

### Top Residual Analogs

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest residual loss | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | 1.000000 | KXBTC15M-26MAY071100-00 | moderate_recross_reversal, thin_edge_expensive_touch |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.060906 | 0.301730 | 0.913273 | 0.800000 | 1.000000 | KXBTC15M-26MAY061300-00 | expensive_yes_near_boundary, moderate_recross_reversal, thin_edge_expensive_touch, weak_boundary_distance |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | 1.000000 | KXBTC15M-26MAY071015-15 | moderate_recross_reversal, weak_boundary_distance |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | 1.000000 | KXBTC15M-26MAY062130-30 | moderate_recross_reversal, fv_overconfidence |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | 1.000000 | KXBTC15M-26MAY070015-15 | fv_overconfidence |
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -71.000000 | 0.161843 | 0.303224 | 0.889718 | 0.690000 | 1.000000 | KXBTC15M-26MAY060745-45 | expensive_yes_near_boundary, moderate_recross_reversal, fv_overconfidence, weak_boundary_distance |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | 1.000000 | KXBTC15M-26MAY071300-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | 1.000000 | KXBTC15M-26MAY061600-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | 1.000000 | KXBTC15M-26MAY070200-00 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | 1.000000 | KXBTC15M-26MAY061430-30 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | 1.000000 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |

### Loss Rows

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest residual loss | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | 1.000000 | KXBTC15M-26MAY071100-00 | moderate_recross_reversal, thin_edge_expensive_touch |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.060906 | 0.301730 | 0.913273 | 0.800000 | 1.000000 | KXBTC15M-26MAY061300-00 | expensive_yes_near_boundary, moderate_recross_reversal, thin_edge_expensive_touch, weak_boundary_distance |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | 1.000000 | KXBTC15M-26MAY071015-15 | moderate_recross_reversal, weak_boundary_distance |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | 1.000000 | KXBTC15M-26MAY062130-30 | moderate_recross_reversal, fv_overconfidence |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | 1.000000 | KXBTC15M-26MAY070015-15 | fv_overconfidence |
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -71.000000 | 0.161843 | 0.303224 | 0.889718 | 0.690000 | 1.000000 | KXBTC15M-26MAY060745-45 | expensive_yes_near_boundary, moderate_recross_reversal, fv_overconfidence, weak_boundary_distance |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | 1.000000 | KXBTC15M-26MAY071300-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | 1.000000 | KXBTC15M-26MAY061600-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | 1.000000 | KXBTC15M-26MAY070200-00 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | 1.000000 | KXBTC15M-26MAY061430-30 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | 1.000000 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | 1.000000 | KXBTC15M-26MAY061530-30 | source_quality_error, cheap_side_residual |

## pre_penalty_birth_feature_entry

- Candidate: `pre_penalty_birth_feature_entry_cheap_penalty025_rank_only`
- Summary: `{'avg_net_cents': 9.581818181818182, 'coverage_pct': 67.07317073170732, 'entries': 55, 'losses': 11, 'net_cents': 527.0, 'settled': 55, 'wins': 44}`
- Residual scores: `{'rows': 55, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 0.8141394809787905, 'tag_counts': {'cheap_side_residual': 9, 'clean_or_unclassified': 5, 'expensive_yes_near_boundary': 5, 'fv_overconfidence': 11, 'moderate_recross_reversal': 22, 'source_quality_error': 10, 'thin_edge_expensive_touch': 18, 'weak_boundary_distance': 19}}`
- Loss scores: `{'rows': 11, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 1.0, 'tag_counts': {'cheap_side_residual': 7, 'fv_overconfidence': 2, 'moderate_recross_reversal': 3, 'source_quality_error': 7, 'thin_edge_expensive_touch': 4, 'weak_boundary_distance': 4}}`

### Top Residual Analogs

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest residual loss | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | 1.000000 | KXBTC15M-26MAY071100-00 | moderate_recross_reversal, thin_edge_expensive_touch |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | 1.000000 | KXBTC15M-26MAY071015-15 | moderate_recross_reversal, weak_boundary_distance |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | 1.000000 | KXBTC15M-26MAY062130-30 | moderate_recross_reversal, fv_overconfidence |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | 1.000000 | KXBTC15M-26MAY070015-15 | fv_overconfidence |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | 1.000000 | KXBTC15M-26MAY071300-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | 1.000000 | KXBTC15M-26MAY061600-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | 1.000000 | KXBTC15M-26MAY070200-00 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | 1.000000 | KXBTC15M-26MAY061430-30 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | 1.000000 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | 1.000000 | KXBTC15M-26MAY061530-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 | 0.946370 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |

### Loss Rows

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest residual loss | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | 1.000000 | KXBTC15M-26MAY071100-00 | moderate_recross_reversal, thin_edge_expensive_touch |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | 1.000000 | KXBTC15M-26MAY071015-15 | moderate_recross_reversal, weak_boundary_distance |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | 1.000000 | KXBTC15M-26MAY062130-30 | moderate_recross_reversal, fv_overconfidence |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | 1.000000 | KXBTC15M-26MAY070015-15 | fv_overconfidence |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | 1.000000 | KXBTC15M-26MAY071300-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | 1.000000 | KXBTC15M-26MAY061600-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | 1.000000 | KXBTC15M-26MAY070200-00 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | 1.000000 | KXBTC15M-26MAY061430-30 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | 1.000000 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | 1.000000 | KXBTC15M-26MAY061530-30 | source_quality_error, cheap_side_residual |

## pre_penalty_birth_feature_bridge

- Candidate: `pre_penalty_birth_feature_bridge_cheap_penalty025_rank_only`
- Summary: `{'avg_net_cents': 9.581818181818182, 'coverage_pct': 67.07317073170732, 'entries': 55, 'losses': 11, 'net_cents': 527.0, 'settled': 55, 'wins': 44}`
- Residual scores: `{'rows': 55, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 0.8141394809787905, 'tag_counts': {'cheap_side_residual': 9, 'clean_or_unclassified': 5, 'expensive_yes_near_boundary': 5, 'fv_overconfidence': 11, 'moderate_recross_reversal': 22, 'source_quality_error': 10, 'thin_edge_expensive_touch': 18, 'weak_boundary_distance': 19}}`
- Loss scores: `{'rows': 11, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 1.0, 'tag_counts': {'cheap_side_residual': 7, 'fv_overconfidence': 2, 'moderate_recross_reversal': 3, 'source_quality_error': 7, 'thin_edge_expensive_touch': 4, 'weak_boundary_distance': 4}}`

### Top Residual Analogs

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest residual loss | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | 1.000000 | KXBTC15M-26MAY071100-00 | moderate_recross_reversal, thin_edge_expensive_touch |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | 1.000000 | KXBTC15M-26MAY071015-15 | moderate_recross_reversal, weak_boundary_distance |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | 1.000000 | KXBTC15M-26MAY062130-30 | moderate_recross_reversal, fv_overconfidence |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | 1.000000 | KXBTC15M-26MAY070015-15 | fv_overconfidence |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | 1.000000 | KXBTC15M-26MAY071300-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | 1.000000 | KXBTC15M-26MAY061600-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | 1.000000 | KXBTC15M-26MAY070200-00 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | 1.000000 | KXBTC15M-26MAY061430-30 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | 1.000000 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | 1.000000 | KXBTC15M-26MAY061530-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 | 0.946370 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |

### Loss Rows

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest residual loss | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | 1.000000 | KXBTC15M-26MAY071100-00 | moderate_recross_reversal, thin_edge_expensive_touch |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | 1.000000 | KXBTC15M-26MAY071015-15 | moderate_recross_reversal, weak_boundary_distance |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | 1.000000 | KXBTC15M-26MAY062130-30 | moderate_recross_reversal, fv_overconfidence |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | 1.000000 | KXBTC15M-26MAY070015-15 | fv_overconfidence |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | 1.000000 | KXBTC15M-26MAY071300-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | 1.000000 | KXBTC15M-26MAY061600-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | 1.000000 | KXBTC15M-26MAY070200-00 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | 1.000000 | KXBTC15M-26MAY061430-30 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | 1.000000 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | 1.000000 | KXBTC15M-26MAY061530-30 | source_quality_error, cheap_side_residual |

## post_penalty_birth_entry

- Candidate: `post_penalty_birth_entry_cheap_penalty025_rank_only`
- Summary: `{'avg_net_cents': 9.882352941176471, 'coverage_pct': 66.23376623376623, 'entries': 51, 'losses': 10, 'net_cents': 504.0, 'settled': 51, 'wins': 41}`
- Residual scores: `{'rows': 51, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 0.8212421582884395, 'tag_counts': {'cheap_side_residual': 8, 'clean_or_unclassified': 4, 'expensive_yes_near_boundary': 5, 'fv_overconfidence': 11, 'moderate_recross_reversal': 21, 'source_quality_error': 9, 'thin_edge_expensive_touch': 15, 'weak_boundary_distance': 19}}`
- Loss scores: `{'rows': 10, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 1.0, 'tag_counts': {'cheap_side_residual': 6, 'fv_overconfidence': 2, 'moderate_recross_reversal': 3, 'source_quality_error': 6, 'thin_edge_expensive_touch': 3, 'weak_boundary_distance': 4}}`

### Top Residual Analogs

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest residual loss | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | 1.000000 | KXBTC15M-26MAY071100-00 | moderate_recross_reversal, thin_edge_expensive_touch |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | 1.000000 | KXBTC15M-26MAY071015-15 | moderate_recross_reversal, weak_boundary_distance |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | 1.000000 | KXBTC15M-26MAY062130-30 | moderate_recross_reversal, fv_overconfidence |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | 1.000000 | KXBTC15M-26MAY070015-15 | fv_overconfidence |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | 1.000000 | KXBTC15M-26MAY071300-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | 1.000000 | KXBTC15M-26MAY061600-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | 1.000000 | KXBTC15M-26MAY070200-00 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | 1.000000 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | 1.000000 | KXBTC15M-26MAY061530-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 | 0.946370 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY070115-15 | approved_entry | yes | True | 16.000000 | 0.059857 | 0.321409 | 0.944285 | 0.820000 | 0.945189 | KXBTC15M-26MAY061300-00 | expensive_yes_near_boundary, moderate_recross_reversal, thin_edge_expensive_touch, weak_boundary_distance |

### Loss Rows

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest residual loss | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | 1.000000 | KXBTC15M-26MAY071100-00 | moderate_recross_reversal, thin_edge_expensive_touch |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | 1.000000 | KXBTC15M-26MAY071015-15 | moderate_recross_reversal, weak_boundary_distance |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | 1.000000 | KXBTC15M-26MAY062130-30 | moderate_recross_reversal, fv_overconfidence |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | 1.000000 | KXBTC15M-26MAY070015-15 | fv_overconfidence |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | 1.000000 | KXBTC15M-26MAY071300-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | 1.000000 | KXBTC15M-26MAY061600-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | 1.000000 | KXBTC15M-26MAY070200-00 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | 1.000000 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | 1.000000 | KXBTC15M-26MAY061530-30 | source_quality_error, cheap_side_residual |

## post_penalty_birth_bridge

- Candidate: `post_penalty_birth_bridge_cheap_penalty025_rank_only`
- Summary: `{'avg_net_cents': 9.882352941176471, 'coverage_pct': 66.23376623376623, 'entries': 51, 'losses': 10, 'net_cents': 504.0, 'settled': 51, 'wins': 41}`
- Residual scores: `{'rows': 51, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 0.8212421582884395, 'tag_counts': {'cheap_side_residual': 8, 'clean_or_unclassified': 4, 'expensive_yes_near_boundary': 5, 'fv_overconfidence': 11, 'moderate_recross_reversal': 21, 'source_quality_error': 9, 'thin_edge_expensive_touch': 15, 'weak_boundary_distance': 19}}`
- Loss scores: `{'rows': 10, 'max_residual_loss_score': 1.0, 'avg_residual_loss_score': 1.0, 'tag_counts': {'cheap_side_residual': 6, 'fv_overconfidence': 2, 'moderate_recross_reversal': 3, 'source_quality_error': 6, 'thin_edge_expensive_touch': 3, 'weak_boundary_distance': 4}}`

### Top Residual Analogs

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest residual loss | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | 1.000000 | KXBTC15M-26MAY071100-00 | moderate_recross_reversal, thin_edge_expensive_touch |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | 1.000000 | KXBTC15M-26MAY071015-15 | moderate_recross_reversal, weak_boundary_distance |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | 1.000000 | KXBTC15M-26MAY062130-30 | moderate_recross_reversal, fv_overconfidence |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | 1.000000 | KXBTC15M-26MAY070015-15 | fv_overconfidence |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | 1.000000 | KXBTC15M-26MAY071300-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | 1.000000 | KXBTC15M-26MAY061600-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | 1.000000 | KXBTC15M-26MAY070200-00 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | 1.000000 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | 1.000000 | KXBTC15M-26MAY061530-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 | 0.946370 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY070115-15 | approved_entry | yes | True | 16.000000 | 0.059857 | 0.321409 | 0.944285 | 0.820000 | 0.945189 | KXBTC15M-26MAY061300-00 | expensive_yes_near_boundary, moderate_recross_reversal, thin_edge_expensive_touch, weak_boundary_distance |

### Loss Rows

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest residual loss | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | 1.000000 | KXBTC15M-26MAY071100-00 | moderate_recross_reversal, thin_edge_expensive_touch |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | 1.000000 | KXBTC15M-26MAY071015-15 | moderate_recross_reversal, weak_boundary_distance |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | 1.000000 | KXBTC15M-26MAY062130-30 | moderate_recross_reversal, fv_overconfidence |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | 1.000000 | KXBTC15M-26MAY070015-15 | fv_overconfidence |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | 1.000000 | KXBTC15M-26MAY071300-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | 1.000000 | KXBTC15M-26MAY061600-00 | source_quality_error, thin_edge_expensive_touch, cheap_side_residual |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | 1.000000 | KXBTC15M-26MAY070200-00 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | source_quality_error, cheap_side_residual, weak_boundary_distance |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | 1.000000 | KXBTC15M-26MAY070130-30 | source_quality_error, cheap_side_residual |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | 1.000000 | KXBTC15M-26MAY061530-30 | source_quality_error, cheap_side_residual |
