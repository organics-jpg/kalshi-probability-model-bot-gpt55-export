# Live v28 Websocket Opportunity Physics Scan

Generated UTC: `20260504_163240Z`

## Scope

- Research-only probe; no orders are submitted and no bot files are modified.
- Source: v28-approved `signal_seen` rows from `logs/live_mushroom_v28_size2/execution_events.ndjson`.
- Outcomes are inferred from resolved market quotes in `logs/live_mushroom_v28_size2/bot.log`.
- Primary dedupe mode is first v28-approved opportunity per market; all-signal counts are sensitivity only.
- Fresh evidence starts after source line `3218` / `2026-05-02T05:18:38.157084+00:00`.

## Raw Coverage

- Raw v28-approved signal rows: 482
- Resolved raw signal rows: 482
- Unique markets: 151
- Unique market/side pairs: 163

## Mode Results

### `first_per_market`

- Rows after dedupe: 151
- Resolved rows: 151
- Contracts: 302
- Fresh rows after opportunity lock: 87 rows / 87 resolved / 174 contracts
- Baseline all: 234/302 contracts (77.48%), 117/151 trades (77.48%)
- Baseline holdout: 46/62 contracts (74.19%), 23/31 trades (74.19%)
- Physics target-pass rules: 0

Perfect-selector oracle bounds:

| split | retention floor | required contracts | max contract acc | required trades | max trade acc | 95% possible |
|---|---:|---:|---:|---:|---:|---|
| all | 75.00% | 227 | 100.00% | 114 | 100.00% | True |
| all | 80.00% | 242 | 96.69% | 121 | 96.69% | True |
| validation | 75.00% | 45 | 93.33% | 23 | 91.30% | False |
| validation | 80.00% | 48 | 87.50% | 24 | 87.50% | False |
| holdout | 75.00% | 47 | 97.87% | 24 | 95.83% | True |
| holdout | 80.00% | 50 | 92.00% | 25 | 92.00% | False |

Fixed adverse-drift rule:

| split | contracts | contract acc | contract ret | trades | trade acc |
|---|---:|---:|---:|---:|---:|
| all | 226/286 | 79.02% | 94.70% | 113/143 | 79.02% |
| validation | 40/54 | 74.07% | 90.00% | 20/27 | 74.07% |
| holdout | 44/60 | 73.33% | 96.77% | 22/30 | 73.33% |

Fixed-rule read: all contracts 79.02% at 94.70% retention; holdout contracts 73.33% at 96.77% retention.

Top high-volume physics rules:

| rank | family | rule | all acc | all ret | holdout acc | holdout ret | contracts | target |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | boundary_margin | `ask<=90; margin>=25` | 79.43% | 93.38% | 75.86% | 93.55% | 282 | False |
| 2 | boundary_margin | `ask<=92; margin>=25` | 79.43% | 93.38% | 75.86% | 93.55% | 282 | False |
| 3 | boundary_margin | `ask<=95; margin>=25` | 79.43% | 93.38% | 75.86% | 93.55% | 282 | False |
| 4 | boundary_margin | `ask<=100; margin>=25` | 79.43% | 93.38% | 75.86% | 93.55% | 282 | False |
| 5 | realized_vol_cushion | `ask<=90; margin/rv60>=0.5` | 79.20% | 82.78% | 75.00% | 90.32% | 250 | False |
| 6 | realized_vol_cushion | `ask<=92; margin/rv60>=0.5` | 79.20% | 82.78% | 75.00% | 90.32% | 250 | False |
| 7 | realized_vol_cushion | `ask<=95; margin/rv60>=0.5` | 79.20% | 82.78% | 75.00% | 90.32% | 250 | False |
| 8 | realized_vol_cushion | `ask<=100; margin/rv60>=0.5` | 79.20% | 82.78% | 75.00% | 90.32% | 250 | False |
| 9 | brownian_realized_vol | `ask<=90; Phi(margin/rv60)>=0.7` | 79.84% | 82.12% | 75.00% | 90.32% | 248 | False |
| 10 | brownian_realized_vol | `ask<=92; Phi(margin/rv60)>=0.7` | 79.84% | 82.12% | 75.00% | 90.32% | 248 | False |

### `first_per_market_side`

- Rows after dedupe: 163
- Resolved rows: 163
- Contracts: 326
- Fresh rows after opportunity lock: 94 rows / 94 resolved / 188 contracts
- Baseline all: 254/326 contracts (77.91%), 127/163 trades (77.91%)
- Baseline holdout: 50/66 contracts (75.76%), 25/33 trades (75.76%)
- Physics target-pass rules: 0

Perfect-selector oracle bounds:

| split | retention floor | required contracts | max contract acc | required trades | max trade acc | 95% possible |
|---|---:|---:|---:|---:|---:|---|
| all | 75.00% | 245 | 100.00% | 123 | 100.00% | True |
| all | 80.00% | 261 | 97.32% | 131 | 96.95% | True |
| validation | 75.00% | 50 | 96.00% | 25 | 96.00% | True |
| validation | 80.00% | 53 | 90.57% | 27 | 88.89% | False |
| holdout | 75.00% | 50 | 100.00% | 25 | 100.00% | True |
| holdout | 80.00% | 53 | 94.34% | 27 | 92.59% | False |

Fixed adverse-drift rule:

| split | contracts | contract acc | contract ret | trades | trade acc |
|---|---:|---:|---:|---:|---:|
| all | 246/310 | 79.35% | 95.09% | 123/155 | 79.35% |
| validation | 46/62 | 74.19% | 93.94% | 23/31 | 74.19% |
| holdout | 48/64 | 75.00% | 96.97% | 24/32 | 75.00% |

Fixed-rule read: all contracts 79.35% at 95.09% retention; holdout contracts 75.00% at 96.97% retention.

Top high-volume physics rules:

| rank | family | rule | all acc | all ret | holdout acc | holdout ret | contracts | target |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | boundary_margin | `ask<=90; margin>=25` | 80.13% | 92.64% | 77.42% | 93.94% | 302 | False |
| 2 | boundary_margin | `ask<=92; margin>=25` | 80.13% | 92.64% | 77.42% | 93.94% | 302 | False |
| 3 | boundary_margin | `ask<=95; margin>=25` | 80.13% | 92.64% | 77.42% | 93.94% | 302 | False |
| 4 | boundary_margin | `ask<=100; margin>=25` | 80.13% | 92.64% | 77.42% | 93.94% | 302 | False |
| 5 | adverse_drift_guard | `ask<=90; block 15m adverse>25 unless v28 cushion>0.25` | 79.38% | 98.16% | 75.76% | 100.00% | 320 | False |
| 6 | adverse_drift_guard | `ask<=92; block 15m adverse>25 unless v28 cushion>0.25` | 79.38% | 98.16% | 75.76% | 100.00% | 320 | False |
| 7 | adverse_drift_guard | `ask<=95; block 15m adverse>25 unless v28 cushion>0.25` | 79.38% | 98.16% | 75.76% | 100.00% | 320 | False |
| 8 | adverse_drift_guard | `ask<=100; block 15m adverse>25 unless v28 cushion>0.25` | 79.38% | 98.16% | 75.76% | 100.00% | 320 | False |
| 9 | adverse_drift_guard | `ask<=90; block 15m adverse>10 unless v28 cushion>0.25` | 79.25% | 97.55% | 75.76% | 100.00% | 318 | False |
| 10 | adverse_drift_guard | `ask<=92; block 15m adverse>10 unless v28 cushion>0.25` | 79.25% | 97.55% | 75.76% | 100.00% | 318 | False |

### `all_signals`

- Rows after dedupe: 482
- Resolved rows: 482
- Contracts: 954
- Fresh rows after opportunity lock: 247 rows / 247 resolved / 489 contracts
- Baseline all: 762/954 contracts (79.87%), 386/482 trades (80.08%)
- Baseline holdout: 150/192 contracts (78.12%), 76/97 trades (78.35%)
- Physics target-pass rules: 0

Perfect-selector oracle bounds:

| split | retention floor | required contracts | max contract acc | required trades | max trade acc | 95% possible |
|---|---:|---:|---:|---:|---:|---|
| all | 75.00% | 716 | 100.00% | 362 | 100.00% | True |
| all | 80.00% | 764 | 99.74% | 386 | 100.00% | True |
| validation | 75.00% | 144 | 95.14% | 72 | 95.83% | True |
| validation | 80.00% | 153 | 89.54% | 77 | 89.61% | False |
| holdout | 75.00% | 144 | 100.00% | 73 | 100.00% | True |
| holdout | 80.00% | 154 | 97.40% | 78 | 97.44% | True |

Fixed adverse-drift rule:

| split | contracts | contract acc | contract ret | trades | trade acc |
|---|---:|---:|---:|---:|---:|
| all | 752/936 | 80.34% | 98.11% | 381/473 | 80.55% |
| validation | 135/183 | 73.77% | 95.81% | 68/92 | 73.91% |
| holdout | 148/190 | 77.89% | 98.96% | 75/96 | 78.12% |

Fixed-rule read: all contracts 80.34% at 98.11% retention; holdout contracts 77.89% at 98.96% retention.

Top high-volume physics rules:

| rank | family | rule | all acc | all ret | holdout acc | holdout ret | contracts | target |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | brownian_v28_sigma | `ask<=90; Phi(margin/v28_sigma)>=0.8` | 82.68% | 75.05% | 77.63% | 79.17% | 716 | False |
| 2 | brownian_v28_sigma | `ask<=92; Phi(margin/v28_sigma)>=0.8` | 82.68% | 75.05% | 77.63% | 79.17% | 716 | False |
| 3 | brownian_v28_sigma | `ask<=95; Phi(margin/v28_sigma)>=0.8` | 82.68% | 75.05% | 77.63% | 79.17% | 716 | False |
| 4 | brownian_v28_sigma | `ask<=100; Phi(margin/v28_sigma)>=0.8` | 82.68% | 75.05% | 77.63% | 79.17% | 716 | False |
| 5 | boundary_sqrt_time | `ask<=90; margin/sqrt(sec)>=2` | 82.77% | 86.37% | 78.72% | 97.92% | 824 | False |
| 6 | boundary_sqrt_time | `ask<=92; margin/sqrt(sec)>=2` | 82.77% | 86.37% | 78.72% | 97.92% | 824 | False |
| 7 | boundary_sqrt_time | `ask<=95; margin/sqrt(sec)>=2` | 82.77% | 86.37% | 78.72% | 97.92% | 824 | False |
| 8 | boundary_sqrt_time | `ask<=100; margin/sqrt(sec)>=2` | 82.77% | 86.37% | 78.72% | 97.92% | 824 | False |
| 9 | drift_projection | `ask<=90; projected_margin_5m>=50` | 82.61% | 86.79% | 78.26% | 95.83% | 828 | False |
| 10 | drift_projection | `ask<=92; projected_margin_5m>=50` | 82.61% | 86.79% | 78.26% | 95.83% | 828 | False |

## Completion Read

The primary opportunity tape does not have a physics rule that clears the configured 95% accuracy and 75% retention gates with sample floors.
This opportunity scan is not by itself completion evidence for the active goal: it is live websocket telemetry, but it is not the locked fresh fill sample. It is useful for questioning v28 priors while the live bot has no post-lock fills.
