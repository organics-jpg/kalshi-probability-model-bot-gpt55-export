# Self-Calibrating ACI PnL Projection

Research-only PnL projection for the locked capped-ACI probability candidate. This is replay over recorded filled v28 trades, not a live-trading change.

- Generated UTC: `2026-05-08T03:03:51.032848+00:00`
- Matched trades: `470`
- Locked calibrator: `capped_aci_brownian_terminal_p_side_eta0.20_cap0.90`
- Truffle prompt: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\truffle_arxiv_self_calibrating_aci_probability_prompt_2026-05-08.txt`

## Projection Summary

| strategy | window | entries | W/L | win rate | PnL | avg/entry | coverage | model EV sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| live_all_recorded_v28 | train_1_200 | 200 | 107/93 | 53.5% | $17.76 | 8.9c | 100.0% | $-3.75 |
| live_all_recorded_v28 | validation_201_400 | 200 | 98/100 (+2 flat) | 49.5% | $-0.15 | -0.1c | 100.0% | $-14.91 |
| live_all_recorded_v28 | holdout_401_end | 70 | 29/38 (+3 flat) | 43.3% | $4.54 | 6.5c | 100.0% | $-4.54 |
| live_all_recorded_v28 | forward_after_200 | 270 | 127/138 (+5 flat) | 47.9% | $4.39 | 1.6c | 100.0% | $-19.46 |
| live_all_recorded_v28 | all | 470 | 234/231 (+5 flat) | 50.3% | $22.15 | 4.7c | 100.0% | $-23.21 |
| robust_hybrid_base | train_1_200 | 67 | 29/38 | 43.3% | $6.24 | 9.3c | 33.5% | $5.88 |
| robust_hybrid_base | validation_201_400 | 61 | 34/26 (+1 flat) | 56.7% | $7.08 | 11.6c | 30.5% | $-3.37 |
| robust_hybrid_base | holdout_401_end | 30 | 14/16 | 46.7% | $3.50 | 11.7c | 42.9% | $0.88 |
| robust_hybrid_base | forward_after_200 | 91 | 48/42 (+1 flat) | 53.3% | $10.58 | 11.6c | 33.7% | $-2.50 |
| robust_hybrid_base | all | 158 | 77/80 (+1 flat) | 49.0% | $16.82 | 10.6c | 33.6% | $3.39 |
| robust_plus_calibrated_edge_ge_0c | train_1_200 | 41 | 17/24 | 41.5% | $4.14 | 10.1c | 20.5% | $11.84 |
| robust_plus_calibrated_edge_ge_0c | validation_201_400 | 34 | 21/12 (+1 flat) | 63.6% | $6.81 | 20.0c | 17.0% | $5.39 |
| robust_plus_calibrated_edge_ge_0c | holdout_401_end | 18 | 9/9 | 50.0% | $2.12 | 11.8c | 25.7% | $5.31 |
| robust_plus_calibrated_edge_ge_0c | forward_after_200 | 52 | 30/21 (+1 flat) | 58.8% | $8.93 | 17.2c | 19.3% | $10.69 |
| robust_plus_calibrated_edge_ge_0c | all | 93 | 47/45 (+1 flat) | 51.1% | $13.07 | 14.1c | 19.8% | $22.53 |
| robust_plus_p_cal_ge_0.80 | train_1_200 | 36 | 15/21 | 41.7% | $4.20 | 11.7c | 18.0% | $11.50 |
| robust_plus_p_cal_ge_0.80 | validation_201_400 | 34 | 22/11 (+1 flat) | 66.7% | $7.27 | 21.4c | 17.0% | $5.22 |
| robust_plus_p_cal_ge_0.80 | holdout_401_end | 18 | 10/8 | 55.6% | $3.40 | 18.9c | 25.7% | $5.28 |
| robust_plus_p_cal_ge_0.80 | forward_after_200 | 52 | 32/19 (+1 flat) | 62.7% | $10.67 | 20.5c | 19.3% | $10.51 |
| robust_plus_p_cal_ge_0.80 | all | 88 | 47/40 (+1 flat) | 54.0% | $14.87 | 16.9c | 18.7% | $22.01 |
| calibrated_edge_all_ge_0c | train_1_200 | 92 | 44/48 | 47.8% | $8.62 | 9.4c | 46.0% | $21.96 |
| calibrated_edge_all_ge_0c | validation_201_400 | 97 | 45/50 (+2 flat) | 47.4% | $-2.00 | -2.1c | 48.5% | $14.08 |
| calibrated_edge_all_ge_0c | holdout_401_end | 34 | 13/21 | 38.2% | $1.70 | 5.0c | 48.6% | $7.56 |
| calibrated_edge_all_ge_0c | forward_after_200 | 131 | 58/71 (+2 flat) | 45.0% | $-0.30 | -0.2c | 48.5% | $21.63 |
| calibrated_edge_all_ge_0c | all | 223 | 102/119 (+2 flat) | 46.2% | $8.32 | 3.7c | 47.4% | $43.59 |
| p_cal_all_ge_0.80 | train_1_200 | 105 | 58/47 | 55.2% | $12.07 | 11.5c | 52.5% | $18.85 |
| p_cal_all_ge_0.80 | validation_201_400 | 122 | 60/60 (+2 flat) | 50.0% | $0.87 | 0.7c | 61.0% | $11.62 |
| p_cal_all_ge_0.80 | holdout_401_end | 40 | 18/22 | 45.0% | $4.14 | 10.3c | 57.1% | $6.92 |
| p_cal_all_ge_0.80 | forward_after_200 | 162 | 78/82 (+2 flat) | 48.8% | $5.01 | 3.1c | 60.0% | $18.54 |
| p_cal_all_ge_0.80 | all | 267 | 136/129 (+2 flat) | 51.3% | $17.08 | 6.4c | 56.8% | $37.39 |
| train_locked_calibrated_gate | train_1_200 | 151 | 82/69 | 54.3% | $15.24 | 10.1c | 75.5% | $13.22 |
| train_locked_calibrated_gate | validation_201_400 | 159 | 78/79 (+2 flat) | 49.7% | $1.25 | 0.8c | 79.5% | $4.48 |
| train_locked_calibrated_gate | holdout_401_end | 50 | 22/28 | 44.0% | $4.58 | 9.2c | 71.4% | $5.21 |
| train_locked_calibrated_gate | forward_after_200 | 209 | 100/107 (+2 flat) | 48.3% | $5.83 | 2.8c | 77.4% | $9.70 |
| train_locked_calibrated_gate | all | 360 | 182/176 (+2 flat) | 50.8% | $21.07 | 5.9c | 76.6% | $22.91 |

## E-Process Sanity Check

Rough anytime-valid diagnostic over realized PnL cents. Threshold 20 is the loose watch level; threshold 100 is the stricter promotion-level signal.

| strategy | window | entries | best lambda | final capital | max capital | crossed 20 | crossed 100 |
|---|---|---:|---:|---:|---:|---|---|
| robust_hybrid_base | train_1_200 | 67 | 0.35 | 2.33 | 2.52 | no | no |
| robust_hybrid_base | forward_after_200 | 91 | 0.35 | 4.21 | 4.21 | no | no |
| robust_hybrid_base | all | 158 | 0.35 | 9.82 | 9.82 | no | no |
| robust_plus_p_cal_ge_0.80 | train_1_200 | 36 | 0.35 | 1.82 | 1.97 | no | no |
| robust_plus_p_cal_ge_0.80 | forward_after_200 | 52 | 0.35 | 5.44 | 5.44 | no | no |
| robust_plus_p_cal_ge_0.80 | all | 88 | 0.35 | 9.91 | 9.91 | no | no |
| train_locked_calibrated_gate | train_1_200 | 151 | 0.35 | 7.54 | 10.30 | no | no |
| train_locked_calibrated_gate | forward_after_200 | 209 | 0.35 | 1.36 | 2.16 | no | no |
| train_locked_calibrated_gate | all | 360 | 0.35 | 10.23 | 16.31 | no | no |

## Train-Locked Gate

- Selected gate: `p_cal_all_ge_0.70`
- Family: `p_cal_all`
- Params: `{"min_p_calibrated": 0.7}`
- Train subsplit nets: `[718.0, 486.0, 320.0]` cents

| candidate | train entries | train PnL | train avg | positive subsplits | min subsplit |
|---|---:|---:|---:|---:|---:|
| p_cal_all_ge_0.70 | 151 | $15.24 | 10.1c | 3 | 320.0c |
| p_cal_all_ge_0.75 | 130 | $13.16 | 10.1c | 3 | 288.0c |
| p_cal_all_ge_0.78 | 117 | $12.28 | 10.5c | 3 | 240.0c |
| p_cal_all_ge_0.80 | 105 | $12.07 | 11.5c | 3 | 234.0c |
| calibrated_edge_all_ge_-5c | 132 | $13.06 | 9.9c | 3 | 210.0c |
| p_cal_all_ge_0.82 | 104 | $11.81 | 11.4c | 3 | 208.0c |
| calibrated_edge_all_ge_4c | 69 | $9.79 | 14.2c | 3 | 152.0c |
| calibrated_edge_all_ge_5c | 59 | $8.39 | 14.2c | 3 | 138.0c |
| calibrated_edge_all_ge_1c | 89 | $8.94 | 10.0c | 3 | 90.0c |
| robust_plus_calibrated_edge_ge_5c | 29 | $3.46 | 11.9c | 3 | 60.0c |
| robust_plus_calibrated_edge_ge_4c | 34 | $3.86 | 11.4c | 3 | 60.0c |
| robust_plus_p_cal_ge_0.75_edge_ge_4c | 34 | $3.86 | 11.4c | 3 | 60.0c |

## Daily Slices For Train-Locked Gate

| day | live rows | selected | W/L | PnL | avg/entry |
|---|---:|---:|---:|---:|---:|
| 2026-04-30 | 6 | 5 | 3/2 | $0.26 | 5.2c |
| 2026-05-01 | 93 | 74 | 39/35 | $8.80 | 11.9c |
| 2026-05-02 | 20 | 14 | 11/3 | $3.72 | 26.6c |
| 2026-05-03 | 46 | 32 | 18/14 | $1.12 | 3.5c |
| 2026-05-04 | 76 | 63 | 32/31 | $5.94 | 9.4c |
| 2026-05-05 | 46 | 26 | 14/12 | $0.34 | 1.3c |
| 2026-05-06 | 123 | 106 | 47/57 (+2 flat) | $-4.07 | -3.8c |
| 2026-05-07 | 60 | 40 | 18/22 | $4.96 | 12.4c |

## Read

- The capped-ACI probability is valuable as a probability scorer: it improves Brier/log loss materially.
- As a hard edge replacement, it tends to shrink opportunity count; the best replay PnL still comes from the robust hybrid baseline.
- The train-locked calibrated gate is useful as a forward-shadow candidate only if it keeps positive PnL after row 200 without relying on the train slice.
- Do not wire this into live entries until the same locked candidate accumulates fresh shadow evidence.
