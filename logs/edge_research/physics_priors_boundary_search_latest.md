# Physics Priors Boundary Model Search

Generated UTC: `20260502_134934Z`

## Status
OBSERVED PASS: at least one physics-prior rule met the configured gates in this exploratory scan.

This probe tests physics-first features, not another v28 threshold tune: signed spot-strike cushion, time-to-close scaling, v28 sigma, realized local volatility, and adverse short-term BTC drift.

## Candle Coverage
- coinbase_cache: C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\coinbase_btc_usd_1m_cache.parquet
- rows: 71328
- start: 2026-03-14T00:54:59.999000+00:00
- end: 2026-05-02T13:46:59.999000+00:00

## Dataset: `current_v28_live_fills`

- Rows: 127
- Contracts: 251
- Candidate rules scanned: 1286
- Observed-pass rules before sample floor: 0
- Target-pass rules: 0

### Baseline

| split | trades | trade acc | contracts | contract acc | contract retention |
|---|---:|---:|---:|---:|---:|
| all | 102/127 | 80.31% | 202/251 | 80.48% | 100.00% |
| train | 65/76 | 85.53% | 128/149 | 85.91% | 100.00% |
| validation | 21/25 | 84.00% | 42/50 | 84.00% | 100.00% |
| holdout | 16/26 | 61.54% | 32/52 | 61.54% | 100.00% |

Holdout oracle at 75% contract retention: required contracts=39, max contract accuracy=82.05%.

### Top Ranked Rules

| rank | family | rule | all acc | all ret | val acc | holdout acc | holdout ret | contracts | target |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | boundary_v28_sigma | `ask<=90; margin/v28_sigma>=1.25` | 94.74% | 15.14% | 100.00% | 100.00% | 3.85% | 38 | False |
| 2 | boundary_v28_sigma | `ask<=92; margin/v28_sigma>=1.25` | 94.74% | 15.14% | 100.00% | 100.00% | 3.85% | 38 | False |
| 3 | boundary_v28_sigma | `ask<=95; margin/v28_sigma>=1.25` | 94.74% | 15.14% | 100.00% | 100.00% | 3.85% | 38 | False |
| 4 | boundary_v28_sigma | `ask<=100; margin/v28_sigma>=1.25` | 94.74% | 15.14% | 100.00% | 100.00% | 3.85% | 38 | False |
| 5 | brownian_v28_sigma | `ask<=90; Phi(margin/v28_sigma)>=0.9` | 94.12% | 13.55% | 100.00% | 100.00% | 3.85% | 34 | False |
| 6 | brownian_v28_sigma | `ask<=92; Phi(margin/v28_sigma)>=0.9` | 94.12% | 13.55% | 100.00% | 100.00% | 3.85% | 34 | False |
| 7 | brownian_v28_sigma | `ask<=95; Phi(margin/v28_sigma)>=0.9` | 94.12% | 13.55% | 100.00% | 100.00% | 3.85% | 34 | False |
| 8 | brownian_v28_sigma | `ask<=100; Phi(margin/v28_sigma)>=0.9` | 94.12% | 13.55% | 100.00% | 100.00% | 3.85% | 34 | False |
| 9 | conservative_drift_prob | `ask<=90; min(v28_brownian, drift5/rv15)>=0.9` | 93.75% | 12.75% | 100.00% | 100.00% | 3.85% | 32 | False |
| 10 | conservative_drift_prob | `ask<=90; min(v28_brownian, drift5/rv30)>=0.9` | 93.75% | 12.75% | 100.00% | 100.00% | 3.85% | 32 | False |

### Top High-Volume Rules

| rank | family | rule | all acc | all ret | holdout acc | holdout ret | contracts |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | adverse_drift_guard | `ask<=90; block 3m adverse>25 unless v28 cushion>1` | 82.85% | 95.22% | 72.73% | 84.62% | 239 |
| 2 | adverse_drift_guard | `ask<=92; block 3m adverse>25 unless v28 cushion>1` | 82.85% | 95.22% | 72.73% | 84.62% | 239 |
| 3 | adverse_drift_guard | `ask<=95; block 3m adverse>25 unless v28 cushion>1` | 82.85% | 95.22% | 72.73% | 84.62% | 239 |
| 4 | adverse_drift_guard | `ask<=100; block 3m adverse>25 unless v28 cushion>1` | 82.85% | 95.22% | 72.73% | 84.62% | 239 |
| 5 | brownian_realized_vol | `ask<=90; Phi(margin/rv15)>=0.6` | 82.70% | 94.42% | 71.43% | 80.77% | 237 |
| 6 | realized_vol_cushion | `ask<=90; margin/rv15>=0.25` | 82.70% | 94.42% | 71.43% | 80.77% | 237 |
| 7 | brownian_realized_vol | `ask<=90; Phi(margin/rv60)>=0.6` | 82.70% | 94.42% | 71.43% | 80.77% | 237 |
| 8 | realized_vol_cushion | `ask<=90; margin/rv60>=0.25` | 82.70% | 94.42% | 71.43% | 80.77% | 237 |
| 9 | brownian_realized_vol | `ask<=92; Phi(margin/rv15)>=0.6` | 82.70% | 94.42% | 71.43% | 80.77% | 237 |
| 10 | realized_vol_cushion | `ask<=92; margin/rv15>=0.25` | 82.70% | 94.42% | 71.43% | 80.77% | 237 |

## Dataset: `live_90_70_replay`

- Rows: 509
- Contracts: 4983
- Candidate rules scanned: 1286
- Observed-pass rules before sample floor: 8
- Target-pass rules: 8

### Baseline

| split | trades | trade acc | contracts | contract acc | contract retention |
|---|---:|---:|---:|---:|---:|
| all | 501/509 | 98.43% | 4903/4983 | 98.39% | 100.00% |
| train | 305/305 | 100.00% | 3003/3003 | 100.00% | 100.00% |
| validation | 99/102 | 97.06% | 964/994 | 96.98% | 100.00% |
| holdout | 97/102 | 95.10% | 936/986 | 94.93% | 100.00% |

Holdout oracle at 75% contract retention: required contracts=740, max contract accuracy=100.00%.

### Top Ranked Rules

| rank | family | rule | all acc | all ret | val acc | holdout acc | holdout ret | contracts | target |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | adverse_drift_guard | `ask<=100; block 15m adverse>10 unless v28 cushion>0.5` | 98.37% | 86.09% | 96.40% | 95.58% | 91.89% | 4290 | True |
| 2 | adverse_drift_guard | `ask<=100; block 15m adverse>10 unless v28 cushion>0.75` | 98.31% | 82.88% | 96.27% | 95.49% | 89.86% | 4130 | True |
| 3 | adverse_drift_guard | `ask<=100; block 15m adverse>10 unless v28 cushion>1` | 98.28% | 81.68% | 96.22% | 95.43% | 88.84% | 4070 | True |
| 4 | realized_vol_cushion | `ask<=100; margin/rv30>=0.5` | 98.17% | 76.86% | 96.31% | 95.22% | 84.79% | 3830 | True |
| 5 | realized_vol_cushion | `ask<=100; margin/rv60>=0.5` | 98.13% | 75.06% | 96.31% | 95.22% | 84.79% | 3740 | True |
| 6 | realized_vol_cushion | `ask<=100; margin/rv15>=0.5` | 98.17% | 76.86% | 96.36% | 95.16% | 83.77% | 3830 | True |
| 7 | brownian_realized_vol | `ask<=100; Phi(margin/rv15)>=0.7` | 98.14% | 75.46% | 96.31% | 95.16% | 83.77% | 3760 | True |
| 8 | brownian_realized_vol | `ask<=100; Phi(margin/rv30)>=0.7` | 98.13% | 75.26% | 96.27% | 95.04% | 81.74% | 3750 | True |
| 9 | brownian_realized_vol | `ask<=100; Phi(margin/rv60)>=0.9` | 100.00% | 13.83% | 100.00% | 100.00% | 12.47% | 689 | False |
| 10 | boundary_v28_sigma | `ask<=100; margin/v28_sigma>=1` | 100.00% | 12.18% | 100.00% | 100.00% | 17.24% | 607 | False |

### Top High-Volume Rules

| rank | family | rule | all acc | all ret | holdout acc | holdout ret | contracts |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | adverse_drift_guard | `ask<=100; block 15m adverse>10 unless v28 cushion>0.5` | 98.37% | 86.09% | 95.58% | 91.89% | 4290 |
| 2 | adverse_drift_guard | `ask<=100; block 15m adverse>10 unless v28 cushion>0.75` | 98.31% | 82.88% | 95.49% | 89.86% | 4130 |
| 3 | adverse_drift_guard | `ask<=100; block 15m adverse>10 unless v28 cushion>1` | 98.28% | 81.68% | 95.43% | 88.84% | 4070 |
| 4 | realized_vol_cushion | `ask<=100; margin/rv30>=0.5` | 98.17% | 76.86% | 95.22% | 84.79% | 3830 |
| 5 | realized_vol_cushion | `ask<=100; margin/rv60>=0.5` | 98.13% | 75.06% | 95.22% | 84.79% | 3740 |
| 6 | realized_vol_cushion | `ask<=100; margin/rv15>=0.5` | 98.17% | 76.86% | 95.16% | 83.77% | 3830 |
| 7 | brownian_realized_vol | `ask<=100; Phi(margin/rv15)>=0.7` | 98.14% | 75.46% | 95.16% | 83.77% | 3760 |
| 8 | brownian_realized_vol | `ask<=100; Phi(margin/rv30)>=0.7` | 98.13% | 75.26% | 95.04% | 81.74% | 3750 |
| 9 | baseline_ask_cap | `ask<=100` | 98.39% | 100.00% | 94.93% | 100.00% | 4983 |
| 10 | boundary_margin | `ask<=100; margin>=-100` | 98.39% | 100.00% | 94.93% | 100.00% | 4983 |

## Loss Physics Summary

### `current_v28_live_fills`

- Loss trades/contracts: 25 / 49
| feature | loser median | winner median | loser range |
|---|---:|---:|---:|
| margin_dollars | 65.070 | 66.855 | -34.940 to 210.010 |
| margin_per_sqrt_sec | 3.038 | 2.901 | -1.515 to 8.726 |
| margin_per_v28_sigma | 0.835 | 0.908 | -0.603 to 2.278 |
| brownian_p_v28_sigma | 0.798 | 0.818 | 0.273 to 0.989 |
| margin_per_rv_sigma_15m | 0.675 | 0.840 | -0.444 to 1.784 |
| signed_move_3m | 30.950 | 59.755 | -58.820 to 216.390 |
| signed_move_5m | 45.130 | 75.615 | -40.710 to 220.810 |
| adverse_move_3m | 0.000 | 0.000 | 0.000 to 58.820 |
| adverse_move_5m | 0.000 | 0.000 | 0.000 to 40.710 |

### `live_90_70_replay`

- Loss trades/contracts: 8 / 80
| feature | loser median | winner median | loser range |
|---|---:|---:|---:|
| margin_dollars | 71.615 | 63.020 | 47.260 to 190.650 |
| margin_per_sqrt_sec | 3.528 | 3.388 | 1.743 to 6.907 |
| margin_per_v28_sigma | 0.476 | 0.573 | 0.292 to 0.993 |
| brownian_p_v28_sigma | 0.683 | 0.717 | 0.615 to 0.840 |
| margin_per_rv_sigma_15m | 1.003 | 0.865 | 0.493 to 1.652 |
| signed_move_3m | 69.585 | 40.550 | -34.490 to 193.120 |
| signed_move_5m | 96.685 | 50.270 | -31.910 to 204.990 |
| adverse_move_3m | 0.000 | 0.000 | 0.000 to 34.490 |
| adverse_move_5m | 0.000 | 0.000 | 0.000 to 31.910 |

## Prompt-To-Artifact Checklist

| requirement | evidence | result |
|---|---|---|
| Use live websocket data | Current ledger is rebuilt from `logs/live_mushroom_v28_size2/execution_events.ndjson`; supplemental ledger uses `live_90_70` live labels | done |
| Focus on underlying physics | Rules test signed boundary distance, time scaling, v28 sigma, realized vol, and adverse BTC drift | done |
| Question priors | v28 probability is not the only selector; zero-drift Brownian, realized-vol, and drift-conservative alternatives are tested | done |
| >=95% realized accuracy | Candidate reports include all/validation/holdout trade and contract accuracy | not met unless target-pass count is positive |
| Keep >=75%-80% volume | Candidate reports enforce >=75% trade and contract retention in all/validation/holdout | not met unless target-pass count is positive |
| Not overfit | Chronological train/validation/holdout splits are reported; holdout is not hidden | exploratory, not promotion by itself |
| Do not change bot logic/code | This probe and the live-v28 parser are standalone research artifacts; live bot files were not edited | done |

## Conclusion

The active goal is still not complete on current v28 live fills. The current holdout remains too loss-heavy for a 95% / 75% verified rule on that filled-trade sample.
The supplemental live_90_70 replay did produce observed physics-prior passes; those are hypotheses for shadow testing, not proof of current-v28 success.
