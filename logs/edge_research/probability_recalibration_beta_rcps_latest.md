# Probability Recalibration: Beta, Temperature, RCPS

Research-only probe over recorded v28 filled trades. No live bot logic changed.

- Generated UTC: `2026-05-08T04:44:43.139607+00:00`
- Matched trades: `470`
- Settled labels: `469`

## Calibration Scores

| model | source | window | rows | Brier | log loss | AUC | rank tau | passes Truffle score gate |
|---|---|---|---:|---:|---:|---:|---:|---|
| temperature_p28 | p28 | train_1_200 | 200 | 0.1732 | 0.5320 | 0.503 | 1.000 | False |
| temperature_p28 | p28 | validation_201_400 | 199 | 0.1599 | 0.5009 | 0.474 | 1.000 | False |
| temperature_p28 | p28 | holdout_401_end | 70 | 0.1750 | 0.5329 | 0.527 | 1.000 | False |
| temperature_p28 | p28 | forward_after_200 | 269 | 0.1638 | 0.5092 | 0.491 | 1.000 | False |
| temperature_p28 | p28 | all | 469 | 0.1678 | 0.5189 | 0.497 | 1.000 | False |
| beta2_p28 | p28 | train_1_200 | 200 | 0.1729 | 0.5307 | 0.503 | 1.000 | False |
| beta2_p28 | p28 | validation_201_400 | 199 | 0.1594 | 0.4995 | 0.474 | 1.000 | False |
| beta2_p28 | p28 | holdout_401_end | 70 | 0.1750 | 0.5331 | 0.527 | 1.000 | False |
| beta2_p28 | p28 | forward_after_200 | 269 | 0.1634 | 0.5082 | 0.491 | 1.000 | False |
| beta2_p28 | p28 | all | 469 | 0.1674 | 0.5178 | 0.497 | 1.000 | False |
| beta3_p28 | p28 | train_1_200 | 200 | 0.1718 | 0.5276 | 0.503 | 1.000 | False |
| beta3_p28 | p28 | validation_201_400 | 199 | 0.1583 | 0.4969 | 0.474 | 1.000 | False |
| beta3_p28 | p28 | holdout_401_end | 70 | 0.1756 | 0.5353 | 0.527 | 1.000 | False |
| beta3_p28 | p28 | forward_after_200 | 269 | 0.1628 | 0.5069 | 0.491 | 1.000 | False |
| beta3_p28 | p28 | all | 469 | 0.1667 | 0.5157 | 0.497 | 1.000 | False |
| temperature_brownian_terminal_p_side | brownian_terminal_p_side | train_1_200 | 200 | 0.1706 | 0.5238 | 0.569 | 1.000 | False |
| temperature_brownian_terminal_p_side | brownian_terminal_p_side | validation_201_400 | 199 | 0.1577 | 0.4932 | 0.560 | 1.000 | False |
| temperature_brownian_terminal_p_side | brownian_terminal_p_side | holdout_401_end | 70 | 0.1697 | 0.5192 | 0.602 | 1.000 | False |
| temperature_brownian_terminal_p_side | brownian_terminal_p_side | forward_after_200 | 269 | 0.1608 | 0.5000 | 0.576 | 1.000 | True |
| temperature_brownian_terminal_p_side | brownian_terminal_p_side | all | 469 | 0.1650 | 0.5102 | 0.577 | 1.000 | False |
| beta2_brownian_terminal_p_side | brownian_terminal_p_side | train_1_200 | 200 | 0.1695 | 0.5211 | 0.569 | 1.000 | False |
| beta2_brownian_terminal_p_side | brownian_terminal_p_side | validation_201_400 | 199 | 0.1568 | 0.4911 | 0.560 | 1.000 | False |
| beta2_brownian_terminal_p_side | brownian_terminal_p_side | holdout_401_end | 70 | 0.1713 | 0.5231 | 0.602 | 1.000 | False |
| beta2_brownian_terminal_p_side | brownian_terminal_p_side | forward_after_200 | 269 | 0.1606 | 0.4994 | 0.576 | 1.000 | True |
| beta2_brownian_terminal_p_side | brownian_terminal_p_side | all | 469 | 0.1644 | 0.5087 | 0.577 | 1.000 | False |
| beta3_brownian_terminal_p_side | brownian_terminal_p_side | train_1_200 | 200 | 0.1694 | 0.5208 | 0.569 | 1.000 | False |
| beta3_brownian_terminal_p_side | brownian_terminal_p_side | validation_201_400 | 199 | 0.1566 | 0.4908 | 0.560 | 1.000 | False |
| beta3_brownian_terminal_p_side | brownian_terminal_p_side | holdout_401_end | 70 | 0.1719 | 0.5249 | 0.602 | 1.000 | False |
| beta3_brownian_terminal_p_side | brownian_terminal_p_side | forward_after_200 | 269 | 0.1606 | 0.4997 | 0.576 | 1.000 | True |
| beta3_brownian_terminal_p_side | brownian_terminal_p_side | all | 469 | 0.1643 | 0.5087 | 0.577 | 1.000 | False |
| locked_capped_aci | brownian_terminal_p_side | train_1_200 | 200 | 0.1640 | 0.5094 | 0.640 | n/a | False |
| locked_capped_aci | brownian_terminal_p_side | validation_201_400 | 199 | 0.1659 | 0.5198 | 0.531 | n/a | False |
| locked_capped_aci | brownian_terminal_p_side | holdout_401_end | 70 | 0.1600 | 0.4926 | 0.696 | n/a | False |
| locked_capped_aci | brownian_terminal_p_side | forward_after_200 | 269 | 0.1644 | 0.5127 | 0.578 | n/a | False |
| locked_capped_aci | brownian_terminal_p_side | all | 469 | 0.1642 | 0.5113 | 0.606 | n/a | False |

## Best Forward Robust Overlays

| rank | strategy | train W/L | train PnL | train avg | forward W/L | forward PnL | forward avg | forward coverage |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | robust_plus_p_calibrated_ge_0.70 | 21/32 | $4.62 | 8.7c | 38/31 (+1 flat) | $11.46 | 16.4c | 25.9% |
| 2 | robust_plus_p_beta3_brownian_terminal_p_side_ge_0.70 | 25/37 | $5.18 | 8.4c | 47/40 (+1 flat) | $11.32 | 12.9c | 32.6% |
| 3 | robust_plus_p_beta2_brownian_terminal_p_side_ge_0.70 | 22/37 | $4.08 | 6.9c | 46/40 (+1 flat) | $11.12 | 12.8c | 32.2% |
| 4 | robust_plus_p_beta3_brownian_terminal_p_side_ge_0.75 | 21/34 | $4.14 | 7.5c | 45/39 (+1 flat) | $10.70 | 12.6c | 31.5% |
| 5 | robust_plus_p_temperature_brownian_terminal_p_side_ge_0.70 | 22/35 | $4.34 | 7.6c | 45/40 (+1 flat) | $10.68 | 12.4c | 31.9% |
| 6 | robust_plus_p_calibrated_ge_0.80 | 15/21 | $4.20 | 11.7c | 32/19 (+1 flat) | $10.67 | 20.5c | 19.3% |
| 7 | robust_plus_p_temperature_p28_ge_0.70 | 29/38 | $6.24 | 9.3c | 48/42 (+1 flat) | $10.58 | 11.6c | 33.7% |
| 8 | robust_plus_p_beta2_p28_ge_0.70 | 29/38 | $6.24 | 9.3c | 48/42 (+1 flat) | $10.58 | 11.6c | 33.7% |
| 9 | robust_plus_p_beta3_p28_ge_0.70 | 29/38 | $6.24 | 9.3c | 48/42 (+1 flat) | $10.58 | 11.6c | 33.7% |
| 10 | robust_plus_p_beta3_p28_ge_0.75 | 29/38 | $6.24 | 9.3c | 48/42 (+1 flat) | $10.58 | 11.6c | 33.7% |
| 11 | robust_plus_p_calibrated_ge_0.75 | 18/28 | $4.40 | 9.6c | 34/26 (+1 flat) | $10.42 | 17.1c | 22.6% |
| 12 | robust_plus_p_temperature_brownian_terminal_p_side_ge_0.75 | 20/34 | $3.92 | 7.3c | 44/38 (+1 flat) | $10.36 | 12.5c | 30.7% |
| 13 | robust_plus_p_beta2_brownian_terminal_p_side_ge_0.75 | 20/34 | $3.92 | 7.3c | 44/38 (+1 flat) | $10.36 | 12.5c | 30.7% |
| 14 | robust_plus_p_calibrated_ge_0.78 | 16/26 | $3.86 | 9.2c | 32/23 (+1 flat) | $9.86 | 17.6c | 20.7% |
| 15 | robust_plus_p_calibrated_ge_0.82 | 15/21 | $4.20 | 11.7c | 29/17 (+1 flat) | $8.97 | 19.1c | 17.4% |

## Rolling Walk-Forward Thresholds

Each split fits/calibrates on a 200-row train window, picks the robust overlay threshold from train PnL only, then evaluates the next slice.

| candidate | test entries | W/L | PnL | avg/entry | coverage | positive windows | windows with trades | locked thresholds |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| aci_p_calibrated | 70 | 38/31 (+1 flat) | $11.46 | 16.4c | 25.9% | 4/4 | 4/4 | `[0.7, 0.7, 0.7, 0.7]` |
| raw_brownian | 79 | 38/40 (+1 flat) | $7.20 | 9.1c | 29.3% | 3/4 | 4/4 | `[0.7, 0.82, 0.7, 0.7]` |
| beta2_brownian | 78 | 38/39 (+1 flat) | $7.50 | 9.6c | 28.9% | 3/4 | 4/4 | `[0.7, 0.75, 0.7, 0.7]` |
| beta3_brownian | 78 | 38/39 (+1 flat) | $7.50 | 9.6c | 28.9% | 3/4 | 4/4 | `[0.7, 0.75, 0.7, 0.7]` |
| temperature_brownian | 78 | 38/39 (+1 flat) | $7.50 | 9.6c | 28.9% | 3/4 | 4/4 | `[0.7, 0.75, 0.7, 0.7]` |

## RCPS-Style Thresholds

| variant | selected threshold | train loss | train Wilson upper | forward entries | forward W/L | forward loss | forward PnL | forward avg | passes gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| all_p_calibrated_alpha_0.20 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |
| robust_p_calibrated_alpha_0.20 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |
| all_p_calibrated_alpha_0.45 | 0.5484 | 45.0% | 50.9% | 264 | 123/136 (+5 flat) | 52.5% | $3.49 | 1.3c | False |
| all_p_calibrated_alpha_0.50 | 0.2318 | 46.5% | 52.3% | 270 | 127/138 (+5 flat) | 52.1% | $4.39 | 1.6c | False |
| all_p_calibrated_alpha_0.60 | 0.2318 | 46.5% | 52.3% | 270 | 127/138 (+5 flat) | 52.1% | $4.39 | 1.6c | False |
| robust_p_calibrated_alpha_0.60 | 0.2318 | 56.7% | 66.2% | 91 | 48/42 (+1 flat) | 46.7% | $10.58 | 11.6c | False |
| all_p_beta2_brownian_terminal_p_side_alpha_0.20 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |
| robust_p_beta2_brownian_terminal_p_side_alpha_0.20 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |
| all_p_beta2_brownian_terminal_p_side_alpha_0.35 | 0.8091 | 34.9% | 47.4% | 71 | 37/34 | 47.9% | $-0.75 | -1.1c | False |
| all_p_beta2_brownian_terminal_p_side_alpha_0.45 | 0.7792 | 45.0% | 53.2% | 203 | 97/104 (+2 flat) | 51.7% | $5.40 | 2.7c | False |
| all_p_beta2_brownian_terminal_p_side_alpha_0.50 | 0.4889 | 46.5% | 52.3% | 270 | 127/138 (+5 flat) | 52.1% | $4.39 | 1.6c | False |
| all_p_beta2_brownian_terminal_p_side_alpha_0.60 | 0.4889 | 46.5% | 52.3% | 270 | 127/138 (+5 flat) | 52.1% | $4.39 | 1.6c | False |
| robust_p_beta2_brownian_terminal_p_side_alpha_0.60 | 0.4947 | 56.7% | 66.2% | 91 | 48/42 (+1 flat) | 46.7% | $10.58 | 11.6c | False |
| all_p_beta3_brownian_terminal_p_side_alpha_0.20 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |
| robust_p_beta3_brownian_terminal_p_side_alpha_0.20 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |
| all_p_beta3_brownian_terminal_p_side_alpha_0.35 | 0.8069 | 34.9% | 47.4% | 71 | 37/34 | 47.9% | $-0.75 | -1.1c | False |
| all_p_beta3_brownian_terminal_p_side_alpha_0.45 | 0.7816 | 45.0% | 53.2% | 203 | 97/104 (+2 flat) | 51.7% | $5.40 | 2.7c | False |
| all_p_beta3_brownian_terminal_p_side_alpha_0.50 | 0.4696 | 46.5% | 52.3% | 270 | 127/138 (+5 flat) | 52.1% | $4.39 | 1.6c | False |
| all_p_beta3_brownian_terminal_p_side_alpha_0.60 | 0.4696 | 46.5% | 52.3% | 270 | 127/138 (+5 flat) | 52.1% | $4.39 | 1.6c | False |
| robust_p_beta3_brownian_terminal_p_side_alpha_0.60 | 0.4781 | 56.7% | 66.2% | 91 | 48/42 (+1 flat) | 46.7% | $10.58 | 11.6c | False |
| all_p_temperature_brownian_terminal_p_side_alpha_0.20 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |
| robust_p_temperature_brownian_terminal_p_side_alpha_0.20 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |
| all_p_temperature_brownian_terminal_p_side_alpha_0.35 | 0.8120 | 34.9% | 47.4% | 71 | 37/34 | 47.9% | $-0.75 | -1.1c | False |
| all_p_temperature_brownian_terminal_p_side_alpha_0.45 | 0.7746 | 45.0% | 53.2% | 203 | 97/104 (+2 flat) | 51.7% | $5.40 | 2.7c | False |
| all_p_temperature_brownian_terminal_p_side_alpha_0.50 | 0.2894 | 46.5% | 52.3% | 270 | 127/138 (+5 flat) | 52.1% | $4.39 | 1.6c | False |
| all_p_temperature_brownian_terminal_p_side_alpha_0.60 | 0.2894 | 46.5% | 52.3% | 270 | 127/138 (+5 flat) | 52.1% | $4.39 | 1.6c | False |
| robust_p_temperature_brownian_terminal_p_side_alpha_0.60 | 0.3007 | 56.7% | 66.2% | 91 | 48/42 (+1 flat) | 46.7% | $10.58 | 11.6c | False |
| all_p_beta2_p28_alpha_0.20 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |
| robust_p_beta2_p28_alpha_0.20 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |
| all_p_beta2_p28_alpha_0.35 | 0.7691 | 34.6% | 43.6% | 118 | 55/62 (+1 flat) | 53.0% | $-3.57 | -3.0c | False |
| all_p_beta2_p28_alpha_0.45 | 0.7458 | 44.9% | 50.9% | 256 | 121/130 (+5 flat) | 51.8% | $2.00 | 0.8c | False |
| robust_p_beta2_p28_alpha_0.45 | 0.7609 | 44.0% | 60.1% | 35 | 18/17 | 48.6% | $2.68 | 7.7c | False |
| all_p_beta2_p28_alpha_0.50 | 0.7445 | 46.5% | 52.3% | 270 | 127/138 (+5 flat) | 52.1% | $4.39 | 1.6c | False |
| robust_p_beta2_p28_alpha_0.50 | 0.7584 | 50.0% | 64.8% | 36 | 18/18 | 50.0% | $2.38 | 6.6c | False |
| all_p_beta2_p28_alpha_0.60 | 0.7445 | 46.5% | 52.3% | 270 | 127/138 (+5 flat) | 52.1% | $4.39 | 1.6c | False |
| robust_p_beta2_p28_alpha_0.60 | 0.7450 | 56.7% | 66.2% | 87 | 47/39 (+1 flat) | 45.3% | $10.91 | 12.5c | False |
| all_p_beta3_p28_alpha_0.20 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |
| robust_p_beta3_p28_alpha_0.20 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |
| all_p_beta3_p28_alpha_0.35 | 0.7759 | 34.6% | 43.6% | 118 | 55/62 (+1 flat) | 53.0% | $-3.57 | -3.0c | False |
| all_p_beta3_p28_alpha_0.45 | 0.7651 | 44.9% | 50.9% | 256 | 121/130 (+5 flat) | 51.8% | $2.00 | 0.8c | False |
| robust_p_beta3_p28_alpha_0.45 | 0.7722 | 44.0% | 60.1% | 35 | 18/17 | 48.6% | $2.68 | 7.7c | False |
| all_p_beta3_p28_alpha_0.50 | 0.7644 | 46.5% | 52.3% | 270 | 127/138 (+5 flat) | 52.1% | $4.39 | 1.6c | False |
| robust_p_beta3_p28_alpha_0.50 | 0.7710 | 50.0% | 64.8% | 36 | 18/18 | 50.0% | $2.38 | 6.6c | False |
| all_p_beta3_p28_alpha_0.60 | 0.7644 | 46.5% | 52.3% | 270 | 127/138 (+5 flat) | 52.1% | $4.39 | 1.6c | False |
| robust_p_beta3_p28_alpha_0.60 | 0.7647 | 56.7% | 66.2% | 87 | 47/39 (+1 flat) | 45.3% | $10.91 | 12.5c | False |
| all_p_temperature_p28_alpha_0.20 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |
| robust_p_temperature_p28_alpha_0.20 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |
| all_p_temperature_p28_alpha_0.35 | 0.7677 | 34.6% | 43.6% | 118 | 55/62 (+1 flat) | 53.0% | $-3.57 | -3.0c | False |
| all_p_temperature_p28_alpha_0.45 | 0.7391 | 44.9% | 50.9% | 256 | 121/130 (+5 flat) | 51.8% | $2.00 | 0.8c | False |
| robust_p_temperature_p28_alpha_0.45 | 0.7579 | 44.0% | 60.1% | 35 | 18/17 | 48.6% | $2.68 | 7.7c | False |
| all_p_temperature_p28_alpha_0.50 | 0.7375 | 46.5% | 52.3% | 270 | 127/138 (+5 flat) | 52.1% | $4.39 | 1.6c | False |
| robust_p_temperature_p28_alpha_0.50 | 0.7548 | 50.0% | 64.8% | 36 | 18/18 | 50.0% | $2.38 | 6.6c | False |
| all_p_temperature_p28_alpha_0.60 | 0.7375 | 46.5% | 52.3% | 270 | 127/138 (+5 flat) | 52.1% | $4.39 | 1.6c | False |
| robust_p_temperature_p28_alpha_0.60 | 0.7382 | 56.7% | 66.2% | 87 | 47/39 (+1 flat) | 45.3% | $10.91 | 12.5c | False |

## E-Process

| strategy | window | entries | best lambda | final capital | max capital | crossed 20 | crossed 100 |
|---|---|---:|---:|---:|---:|---|---|
| robust_hybrid_base | train_1_200 | 67 | 0.35 | 2.33 | 2.52 | no | no |
| robust_hybrid_base | forward_after_200 | 91 | 0.35 | 4.21 | 4.21 | no | no |
| robust_hybrid_base | all | 158 | 0.35 | 9.82 | 9.82 | no | no |
| aci_robust_plus_p_cal_ge_0.80 | train_1_200 | 36 | 0.35 | 1.82 | 1.97 | no | no |
| aci_robust_plus_p_cal_ge_0.80 | forward_after_200 | 52 | 0.35 | 5.44 | 5.44 | no | no |
| aci_robust_plus_p_cal_ge_0.80 | all | 88 | 0.35 | 9.91 | 9.91 | no | no |
| robust_plus_p_calibrated_ge_0.70 | train_1_200 | 53 | 0.35 | 1.92 | 2.08 | no | no |
| robust_plus_p_calibrated_ge_0.70 | forward_after_200 | 70 | 0.35 | 5.98 | 5.98 | no | no |
| robust_plus_p_calibrated_ge_0.70 | all | 123 | 0.35 | 11.50 | 11.50 | no | no |
| robust_plus_p_beta3_brownian_terminal_p_side_ge_0.70 | train_1_200 | 62 | 0.35 | 1.95 | 2.11 | no | no |
| robust_plus_p_beta3_brownian_terminal_p_side_ge_0.70 | forward_after_200 | 88 | 0.35 | 4.84 | 4.84 | no | no |
| robust_plus_p_beta3_brownian_terminal_p_side_ge_0.70 | all | 150 | 0.35 | 9.44 | 9.44 | no | no |
| robust_plus_p_beta2_brownian_terminal_p_side_ge_0.70 | train_1_200 | 59 | 0.35 | 1.62 | 1.75 | no | no |
| robust_plus_p_beta2_brownian_terminal_p_side_ge_0.70 | forward_after_200 | 87 | 0.35 | 4.68 | 4.68 | no | no |
| robust_plus_p_beta2_brownian_terminal_p_side_ge_0.70 | all | 146 | 0.35 | 7.57 | 7.57 | no | no |
| robust_plus_p_beta3_brownian_terminal_p_side_ge_0.75 | train_1_200 | 55 | 0.35 | 1.64 | 1.77 | no | no |
| robust_plus_p_beta3_brownian_terminal_p_side_ge_0.75 | forward_after_200 | 85 | 0.35 | 4.36 | 4.36 | no | no |
| robust_plus_p_beta3_brownian_terminal_p_side_ge_0.75 | all | 140 | 0.35 | 7.15 | 7.15 | no | no |
| robust_plus_p_temperature_brownian_terminal_p_side_ge_0.70 | train_1_200 | 57 | 0.35 | 1.70 | 1.83 | no | no |
| robust_plus_p_temperature_brownian_terminal_p_side_ge_0.70 | forward_after_200 | 86 | 0.35 | 4.35 | 4.35 | no | no |
| robust_plus_p_temperature_brownian_terminal_p_side_ge_0.70 | all | 143 | 0.35 | 7.37 | 7.37 | no | no |

## Read

- Beta and temperature calibration are useful comparators, but their forward score gate must beat the locked capped-ACI candidate before replacing it.
- RCPS with a strict 20% loss target is expected to be too conservative for this payoff stream; higher alpha rows are diagnostic only.
- Any attractive replay overlay still needs fresh shadow accumulation because the e-process gate is the promotion brake.
