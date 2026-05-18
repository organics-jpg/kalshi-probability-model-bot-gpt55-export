# Self-Calibrating ACI Deep Dive

Research-only focused probe for the self-calibrating / ACI probability lane. The locked candidate is selected only from rows 1-200, then evaluated forward.

- Generated UTC: `2026-05-08T02:59:46.582768+00:00`
- Matched trades: `470`
- Settled labels: `469`

## Baseline Scores

| model | window | rows | Brier | log loss | AUC |
|---|---|---:|---:|---:|---:|
| p28 | train_1_200 | 200 | 0.1835 | 0.5833 | 0.503 |
| p28 | validation_201_400 | 199 | 0.1660 | 0.5368 | 0.474 |
| p28 | holdout_401_end | 70 | 0.1867 | 0.5771 | 0.527 |
| p28 | all | 469 | 0.1766 | 0.5626 | 0.497 |
| brownian_terminal_p_side | train_1_200 | 200 | 0.1714 | 0.5271 | 0.569 |
| brownian_terminal_p_side | validation_201_400 | 199 | 0.1584 | 0.4964 | 0.560 |
| brownian_terminal_p_side | holdout_401_end | 70 | 0.1718 | 0.5249 | 0.602 |
| brownian_terminal_p_side | all | 469 | 0.1659 | 0.5137 | 0.577 |
| p22 | train_1_200 | 200 | 0.2048 | 0.5977 | 0.518 |
| p22 | validation_201_400 | 199 | 0.1899 | 0.5681 | 0.533 |
| p22 | holdout_401_end | 70 | 0.1971 | 0.5845 | 0.505 |
| p22 | all | 469 | 0.1973 | 0.5832 | 0.522 |

## Oracle Constant Context

| window | rows | hit rate | constant Brier | constant log loss |
|---|---:|---:|---:|---:|
| train_1_200 | 200 | 78.0% | 0.1716 | 0.5269 |
| validation_201_400 | 199 | 80.4% | 0.1576 | 0.4948 |
| holdout_401_end | 70 | 77.1% | 0.1763 | 0.5375 |
| all | 469 | 78.9% | 0.1665 | 0.5154 |

## Locked Calibrator

- Selection rule: `Pick capped ACI source/eta/cap by lowest log loss on rows 1-200, tie-breaker Brier.`
- Locked calibrator: `capped_aci_brownian_terminal_p_side_eta0.20_cap0.90`
- Source: `brownian_terminal_p_side`, eta `0.2`, cap `0.9`, max bias `0.25`.

| window | rows | Brier | log loss | coverage | Brier vs raw | Log loss vs raw | Brier vs Brownian | Log loss vs Brownian |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| train_1_200 | 200 | 0.1640 | 0.5094 | 89.5% | 0.0195 | 0.0739 | 0.0073 | 0.0177 |
| validation_201_400 | 199 | 0.1659 | 0.5198 | 89.4% | 0.0001 | 0.0170 | -0.0075 | -0.0234 |
| holdout_401_end | 70 | 0.1600 | 0.4926 | 91.4% | 0.0267 | 0.0846 | 0.0118 | 0.0323 |
| all_after_200 | 269 | 0.1644 | 0.5127 | 90.0% | 0.0070 | 0.0346 | -0.0025 | -0.0089 |
| first_400 | 399 | 0.1650 | 0.5146 | 89.5% | 0.0098 | 0.0455 | -0.0001 | -0.0028 |
| all | 469 | 0.1642 | 0.5113 | 89.8% | 0.0123 | 0.0513 | 0.0017 | 0.0024 |

## Top Train-Selected Candidates

| candidate | train Brier | train log loss | validation Brier | validation log loss | holdout Brier | holdout log loss | all Brier | all log loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| capped_aci_brownian_terminal_p_side_eta0.20_cap0.90 | 0.1640 | 0.5094 | 0.1659 | 0.5198 | 0.1600 | 0.4926 | 0.1642 | 0.5113 |
| capped_aci_brownian_terminal_p_side_eta0.16_cap0.90 | 0.1652 | 0.5124 | 0.1654 | 0.5182 | 0.1649 | 0.5044 | 0.1652 | 0.5137 |
| capped_aci_brownian_terminal_p_side_eta0.20_cap0.92 | 0.1647 | 0.5137 | 0.1670 | 0.5261 | 0.1601 | 0.4934 | 0.1650 | 0.5160 |
| capped_aci_p28_eta0.16_cap0.90 | 0.1662 | 0.5140 | 0.1612 | 0.5067 | 0.1682 | 0.5134 | 0.1644 | 0.5108 |
| capped_aci_p28_eta0.20_cap0.90 | 0.1664 | 0.5147 | 0.1612 | 0.5072 | 0.1639 | 0.5028 | 0.1638 | 0.5098 |
| capped_aci_brownian_terminal_p_side_eta0.16_cap0.92 | 0.1656 | 0.5151 | 0.1659 | 0.5213 | 0.1654 | 0.5075 | 0.1657 | 0.5166 |
| capped_aci_brownian_terminal_p_side_eta0.12_cap0.90 | 0.1665 | 0.5153 | 0.1636 | 0.5119 | 0.1705 | 0.5209 | 0.1659 | 0.5147 |
| capped_aci_p28_eta0.12_cap0.90 | 0.1672 | 0.5160 | 0.1607 | 0.5053 | 0.1730 | 0.5279 | 0.1653 | 0.5133 |

## Calibrated Edge Gate Check

- Baseline robust hybrid: `$16.82` from `158` rows, avg `10.6c`.

| gate | entries | W/L | PnL | avg/entry |
|---|---:|---:|---:|---:|
| min_calibrated_edge_0c | 93 | 47/45 (+1 flat) | $13.07 | 14.1c |
| min_calibrated_edge_1c | 87 | 42/44 (+1 flat) | $10.53 | 12.1c |
| min_calibrated_edge_2c | 83 | 40/42 (+1 flat) | $10.03 | 12.1c |
| min_calibrated_edge_3c | 79 | 38/40 (+1 flat) | $9.79 | 12.4c |
| min_calibrated_edge_4c | 72 | 36/35 (+1 flat) | $10.27 | 14.3c |
| min_calibrated_edge_5c | 64 | 30/33 (+1 flat) | $8.65 | 13.5c |

## Read

- Strict first-400 Truffle gate passed: `False`.
- The locked candidate does improve validation rows 201-400 to Brier `0.1659` / log loss `0.5198` and holdout rows 401-end to Brier `0.1600` / log loss `0.4926`.
- p28 has weak/negative discrimination in the hard middle slice, so the self-calibrating path should use Brownian terminal as the anchor and treat v28 as an edge/feature signal.
- The calibrated probability should be logged as `p_calibrated` in forward shadow first. Using it as a hard calibrated-edge veto reduced replay PnL, so do not wire it into live entry logic yet.
- Candidate lock JSON: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\self_calibrating_aci_candidate_lock_latest.json`.
