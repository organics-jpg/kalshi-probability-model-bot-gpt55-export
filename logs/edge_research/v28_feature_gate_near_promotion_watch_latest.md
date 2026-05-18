# v28 Feature-Gate Near-Promotion Watch

Research-only watch. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:25.736096+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Any live-ready watched row: `False`
- Best candidate: `post_feature_freeze_entry_raw05_recross60_abs085`
- Best missing gates: `['coverage+7.9pp']`

## Watched Rows

| lane | candidate | settled | W/L | coverage | net | recon | cushion | rows needed | avg c/row | missing gates |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| `post_feature_freeze_entry` | `post_feature_freeze_entry_raw05_recross60_abs085` | 55 | 39/16 | 67.1% | 445c ($4.45) | 27.3% | 4 | cov 7/settle 0/clean 0/cushion 0c ($0.00) | 0c ($0.00) | coverage+7.9pp |
| `post_feature_freeze_bridge` | `post_feature_freeze_bridge_raw05_recross60_abs085` | 55 | 39/16 | 67.1% | 445c ($4.45) | 27.3% | 4 | cov 7/settle 0/clean 0/cushion 0c ($0.00) | 0c ($0.00) | coverage+7.9pp |
| `post_feature_freeze_entry` | `post_feature_freeze_entry_raw05_recross60_abs085_ask65` | 47 | 42/5 | 57.3% | 344c ($3.44) | 4.3% | 3 | cov 15/settle 0/clean 0/cushion 0c ($0.00) | 0c ($0.00) | coverage+17.7pp |
| `post_feature_freeze_bridge` | `post_feature_freeze_bridge_raw05_recross60_abs085_ask65` | 47 | 42/5 | 57.3% | 344c ($3.44) | 4.3% | 3 | cov 15/settle 0/clean 0/cushion 0c ($0.00) | 0c ($0.00) | coverage+17.7pp |
| `post_feature_freeze_entry` | `post_feature_freeze_entry_raw03_recross70_abs075` | 64 | 42/22 | 78.0% | 307c ($3.07) | 39.1% | 3 | cov 0/settle 0/clean 8/cushion 0c ($0.00) | 0c ($0.00) | clean_rows+8 |
| `post_feature_freeze_bridge` | `post_feature_freeze_bridge_raw03_recross70_abs075` | 64 | 42/22 | 78.0% | 307c ($3.07) | 39.1% | 3 | cov 0/settle 0/clean 8/cushion 0c ($0.00) | 0c ($0.00) | clean_rows+8 |

## Loss Tags

### post_feature_freeze_entry_raw05_recross60_abs085
- Source counts: `{'approved_entry': 40, 'rejected_actionable': 15}`
- Pending source counts: `{}`
- Loss tag counts: `{'source_quality': 12, 'cheap_tail': 12, 'unclassified': 4}`

| market | source | side | net | ask | abs d | recross | raw edge | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | -84c ($-0.84) | 0.83 | 1.010241 | 0.30500573389101787 | 0.054041000000000006 | unclassified |
| KXBTC15M-26MAY071015-15 | approved_entry | no | -80c ($-0.80) | 0.78 | 0.936079 | 0.41762272221317515 | 0.08109199999999994 | unclassified |
| KXBTC15M-26MAY062130-30 | approved_entry | no | -78c ($-0.78) | 0.76 | 0.999156 | 0.3038697963028121 | 0.12777700000000003 | unclassified |
| KXBTC15M-26MAY070015-15 | approved_entry | no | -72c ($-0.72) | 0.7 | 1.543579 | 0.07375286170271013 | 0.2636590000000001 | unclassified |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | -10c ($-0.10) | 0.08 | 0.932497 | 0.0838612713123607 | 0.05323499999999999 | source_quality, cheap_tail |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | -7c ($-0.07) | 0.06 | 0.967753 | 0.08357682604279555 | 0.057585 | source_quality, cheap_tail |
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | -7c ($-0.07) | 0.06 | 1.01449 | 0.0621043045893775 | 0.052022 | source_quality, cheap_tail |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -6c ($-0.06) | 0.05 | 0.997837 | 0.16075609997197524 | 0.059156 | source_quality, cheap_tail |

### post_feature_freeze_bridge_raw05_recross60_abs085
- Source counts: `{'approved_entry': 40, 'rejected_actionable': 15}`
- Pending source counts: `{}`
- Loss tag counts: `{'source_quality': 12, 'cheap_tail': 12, 'unclassified': 4}`

| market | source | side | net | ask | abs d | recross | raw edge | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | -84c ($-0.84) | 0.83 | 1.010241 | 0.30500573389101787 | 0.054041000000000006 | unclassified |
| KXBTC15M-26MAY071015-15 | approved_entry | no | -80c ($-0.80) | 0.78 | 0.936079 | 0.41762272221317515 | 0.08109199999999994 | unclassified |
| KXBTC15M-26MAY062130-30 | approved_entry | no | -78c ($-0.78) | 0.76 | 0.999156 | 0.3038697963028121 | 0.12777700000000003 | unclassified |
| KXBTC15M-26MAY070015-15 | approved_entry | no | -72c ($-0.72) | 0.7 | 1.543579 | 0.07375286170271013 | 0.2636590000000001 | unclassified |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | -10c ($-0.10) | 0.08 | 0.932497 | 0.0838612713123607 | 0.05323499999999999 | source_quality, cheap_tail |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | -7c ($-0.07) | 0.06 | 0.967753 | 0.08357682604279555 | 0.057585 | source_quality, cheap_tail |
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | -7c ($-0.07) | 0.06 | 1.01449 | 0.0621043045893775 | 0.052022 | source_quality, cheap_tail |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -6c ($-0.06) | 0.05 | 0.997837 | 0.16075609997197524 | 0.059156 | source_quality, cheap_tail |

### post_feature_freeze_entry_raw05_recross60_abs085_ask65
- Source counts: `{'approved_entry': 45, 'rejected_actionable': 2}`
- Pending source counts: `{}`
- Loss tag counts: `{'unclassified': 5}`

| market | source | side | net | ask | abs d | recross | raw edge | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | -84c ($-0.84) | 0.83 | 1.010241 | 0.30500573389101787 | 0.054041000000000006 | unclassified |
| KXBTC15M-26MAY071015-15 | approved_entry | no | -80c ($-0.80) | 0.78 | 0.936079 | 0.41762272221317515 | 0.08109199999999994 | unclassified |
| KXBTC15M-26MAY062130-30 | approved_entry | no | -78c ($-0.78) | 0.76 | 0.999156 | 0.3038697963028121 | 0.12777700000000003 | unclassified |
| KXBTC15M-26MAY070015-15 | approved_entry | no | -72c ($-0.72) | 0.7 | 1.543579 | 0.07375286170271013 | 0.2636590000000001 | unclassified |
| KXBTC15M-26MAY062015-15 | approved_entry | yes | -71c ($-0.71) | 0.67 | 0.973796 | 0.03209081623854011 | 0.215657 | unclassified |

### post_feature_freeze_bridge_raw05_recross60_abs085_ask65
- Source counts: `{'approved_entry': 45, 'rejected_actionable': 2}`
- Pending source counts: `{}`
- Loss tag counts: `{'unclassified': 5}`

| market | source | side | net | ask | abs d | recross | raw edge | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | -84c ($-0.84) | 0.83 | 1.010241 | 0.30500573389101787 | 0.054041000000000006 | unclassified |
| KXBTC15M-26MAY071015-15 | approved_entry | no | -80c ($-0.80) | 0.78 | 0.936079 | 0.41762272221317515 | 0.08109199999999994 | unclassified |
| KXBTC15M-26MAY062130-30 | approved_entry | no | -78c ($-0.78) | 0.76 | 0.999156 | 0.3038697963028121 | 0.12777700000000003 | unclassified |
| KXBTC15M-26MAY070015-15 | approved_entry | no | -72c ($-0.72) | 0.7 | 1.543579 | 0.07375286170271013 | 0.2636590000000001 | unclassified |
| KXBTC15M-26MAY062015-15 | approved_entry | yes | -71c ($-0.71) | 0.67 | 0.973796 | 0.03209081623854011 | 0.215657 | unclassified |

### post_feature_freeze_entry_raw03_recross70_abs075
- Source counts: `{'approved_entry': 39, 'rejected_actionable': 25}`
- Pending source counts: `{}`
- Loss tag counts: `{'source_quality': 18, 'cheap_tail': 16, 'thin_raw_edge': 4, 'unclassified': 4}`

| market | source | side | net | ask | abs d | recross | raw edge | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | -84c ($-0.84) | 0.83 | 1.010241 | 0.30500573389101787 | 0.054041000000000006 | unclassified |
| KXBTC15M-26MAY071015-15 | approved_entry | no | -80c ($-0.80) | 0.78 | 0.936079 | 0.41762272221317515 | 0.08109199999999994 | unclassified |
| KXBTC15M-26MAY062130-30 | approved_entry | no | -78c ($-0.78) | 0.76 | 0.999156 | 0.3038697963028121 | 0.12777700000000003 | unclassified |
| KXBTC15M-26MAY071215-15 | rejected_actionable | yes | -75c ($-0.75) | 0.72 | 0.790551 | 0.48773958548079466 | 0.10828199999999999 | source_quality |
| KXBTC15M-26MAY070015-15 | approved_entry | no | -72c ($-0.72) | 0.7 | 1.543579 | 0.07375286170271013 | 0.2636590000000001 | unclassified |
| KXBTC15M-26MAY070615-15 | rejected_actionable | yes | -68c ($-0.68) | 0.64 | 0.819952 | 0.2533484847166239 | 0.20093099999999997 | source_quality |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | -15c ($-0.15) | 0.13 | 0.784861 | 0.13225659322745886 | 0.041601 | source_quality, cheap_tail, thin_raw_edge |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | -11c ($-0.11) | 0.09 | 0.758696 | 0.12224159683597033 | 0.08693400000000001 | source_quality, cheap_tail |

### post_feature_freeze_bridge_raw03_recross70_abs075
- Source counts: `{'approved_entry': 39, 'rejected_actionable': 25}`
- Pending source counts: `{}`
- Loss tag counts: `{'source_quality': 18, 'cheap_tail': 16, 'thin_raw_edge': 4, 'unclassified': 4}`

| market | source | side | net | ask | abs d | recross | raw edge | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071100-00 | approved_entry | yes | -84c ($-0.84) | 0.83 | 1.010241 | 0.30500573389101787 | 0.054041000000000006 | unclassified |
| KXBTC15M-26MAY071015-15 | approved_entry | no | -80c ($-0.80) | 0.78 | 0.936079 | 0.41762272221317515 | 0.08109199999999994 | unclassified |
| KXBTC15M-26MAY062130-30 | approved_entry | no | -78c ($-0.78) | 0.76 | 0.999156 | 0.3038697963028121 | 0.12777700000000003 | unclassified |
| KXBTC15M-26MAY071215-15 | rejected_actionable | yes | -75c ($-0.75) | 0.72 | 0.790551 | 0.48773958548079466 | 0.10828199999999999 | source_quality |
| KXBTC15M-26MAY070015-15 | approved_entry | no | -72c ($-0.72) | 0.7 | 1.543579 | 0.07375286170271013 | 0.2636590000000001 | unclassified |
| KXBTC15M-26MAY070615-15 | rejected_actionable | yes | -68c ($-0.68) | 0.64 | 0.819952 | 0.2533484847166239 | 0.20093099999999997 | source_quality |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | -15c ($-0.15) | 0.13 | 0.784861 | 0.13225659322745886 | 0.041601 | source_quality, cheap_tail, thin_raw_edge |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | -11c ($-0.11) | 0.09 | 0.758696 | 0.12224159683597033 | 0.08693400000000001 | source_quality, cheap_tail |

## Interpretation

- This watch tracks already-frozen feature-gate rules only; it is not a new threshold search.
- Pending approved rows can close sample/source gaps, but promotion still requires settled PnL and full-loss cushion.
- Best watched row post_feature_freeze_entry_raw05_recross60_abs085 has net 445.0c, coverage 67.07317073170732%, reconstructed share 0.2727272727272727, and missing gates ['coverage+7.9pp'].
