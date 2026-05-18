# Live v28 FV Accuracy/Volume Search

Generated UTC: 20260504_163201Z

## Status

FAIL: no scanned rule met the 95% accuracy plus 75% volume gate with live holdout/sample checks.

## Data

- Execution log: `logs\live_mushroom_v28_size2\execution_events.ndjson`
- Bot log: `logs\live_mushroom_v28_size2\bot.log`
- Usable deduped entry orders: 246
- Markets with inferred outcomes: 331
- Candidate rules scanned: 11704

## Baseline Current v28 Filled Entries

- all: 189/246 trades (76.83%), 376/489 contracts (76.89%), contract retention 100.00%
- train: 118/147 trades (80.27%), 234/291 contracts (80.41%), contract retention 100.00%
- validation: 32/49 trades (65.31%), 64/98 contracts (65.31%), contract retention 100.00%
- holdout: 39/50 trades (78.00%), 78/100 contracts (78.00%), contract retention 100.00%

## Oracle Feasibility Bound

This is the maximum possible accuracy if a rule could perfectly remove losers while still meeting the volume floor.

| split | retention floor | required trades | max trade acc | required contracts | max contract acc |
|---|---:|---:|---:|---:|---:|
| all | 75% | 185 | 100.00% | 367 | 100.00% |
| all | 80% | 197 | 95.94% | 392 | 95.92% |
| train | 75% | 111 | 100.00% | 219 | 100.00% |
| train | 80% | 118 | 100.00% | 233 | 100.00% |
| validation | 75% | 37 | 86.49% | 74 | 86.49% |
| validation | 80% | 40 | 80.00% | 79 | 81.01% |
| holdout | 75% | 38 | 100.00% | 75 | 100.00% |
| holdout | 80% | 40 | 97.50% | 80 | 97.50% |

## Minimum Future Evidence Needed

This is an optimistic lower bound for the holdout slice: it assumes every additional future observation is a winner.

| unit | retention floor | extra all-winning observations needed | future total | required selected | possible accuracy |
|---|---:|---:|---:|---:|---:|
| trades | 75% | 0 | 50 | 38 | 102.63% |
| contracts | 75% | 0 | 100 | 75 | 104.00% |
| trades | 80% | 0 | 50 | 40 | 97.50% |
| contracts | 80% | 0 | 100 | 80 | 97.50% |

## Gate

- Required realized accuracy: >= 95% trade and contract accuracy
- Required retained volume: >= 75% contracts and trades
- Sample-size floor used here: >= 75 all trades / 150 all contracts, >= 15 holdout trades / 30 holdout contracts
- Overfit controls: chronological 60/20/20 split plus five chronological fold diagnostics

## Scan Result

- Rules meeting observed accuracy/retention gate before sample floor: 0
- Rules meeting observed gate and sample-size floor: 0

## Top Ranked Rules

| rank | rule | all contracts | all acc | all retention | holdout contracts | holdout acc | holdout retention | validation acc | target |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | id=rule_09602, source=pool_v28_v22, lambda=0.5, p>=0.88, edge>=2.0, ask<=85.0, book<=750.0 | 34 | 100.00% | 6.95% | 6 | 100.00% | 6.00% | 100.00% | False |
| 2 | id=rule_09618, source=pool_v28_v22, lambda=0.5, p>=0.88, edge>=4.0, ask<=85.0, book<=750.0 | 28 | 100.00% | 5.73% | 4 | 100.00% | 4.00% | 100.00% | False |
| 3 | id=rule_09730, source=pool_v28_v22, lambda=0.5, p>=0.89, edge>=2.0, ask<=85.0, book<=750.0 | 28 | 100.00% | 5.73% | 4 | 100.00% | 4.00% | 100.00% | False |
| 4 | id=rule_10498, source=pool_v28_v22, lambda=0.75, p>=0.86, edge>=2.0, ask<=85.0, book<=750.0 | 28 | 100.00% | 5.73% | 4 | 100.00% | 4.00% | 100.00% | False |
| 5 | id=rule_10626, source=pool_v28_v22, lambda=0.75, p>=0.87, edge>=2.0, ask<=85.0, book<=750.0 | 26 | 100.00% | 5.32% | 4 | 100.00% | 4.00% | 100.00% | False |
| 6 | id=rule_09601, source=pool_v28_v22, lambda=0.5, p>=0.88, edge>=2.0, ask<=85.0, book<=500.0 | 26 | 100.00% | 5.32% | 2 | 100.00% | 2.00% | 100.00% | False |
| 7 | id=rule_08705, source=pool_v28_v22, lambda=0.25, p>=0.9, edge>=2.0, ask<=85.0, book<=500.0 | 24 | 100.00% | 4.91% | 2 | 100.00% | 2.00% | 100.00% | False |
| 8 | id=rule_10754, source=pool_v28_v22, lambda=0.75, p>=0.88, edge>=2.0, ask<=85.0, book<=750.0 | 24 | 100.00% | 4.91% | 2 | 100.00% | 2.00% | 100.00% | False |
| 9 | id=rule_09617, source=pool_v28_v22, lambda=0.5, p>=0.88, edge>=4.0, ask<=85.0, book<=500.0 | 22 | 100.00% | 4.50% | 2 | 100.00% | 2.00% | 100.00% | False |
| 10 | id=rule_09729, source=pool_v28_v22, lambda=0.5, p>=0.89, edge>=2.0, ask<=85.0, book<=500.0 | 22 | 100.00% | 4.50% | 2 | 100.00% | 2.00% | 100.00% | False |

## Top High-Volume Rules

These rules retain at least 75% of contract volume in both all-data and holdout splits, then rank by holdout accuracy.

| rank | rule | all contracts | all acc | all retention | holdout contracts | holdout acc | holdout retention | validation acc |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | id=rule_00006, source=v28, lambda=None, p>=0.85, edge>=2.0, ask<=90.0, book<=750.0 | 372 | 79.84% | 76.07% | 82 | 80.49% | 82.00% | 65.71% |
| 2 | id=rule_00010, source=v28, lambda=None, p>=0.85, edge>=2.0, ask<=95.0, book<=750.0 | 372 | 79.84% | 76.07% | 82 | 80.49% | 82.00% | 65.71% |
| 3 | id=rule_00014, source=v28, lambda=None, p>=0.85, edge>=2.0, ask<=100.0, book<=750.0 | 372 | 79.84% | 76.07% | 82 | 80.49% | 82.00% | 65.71% |
| 4 | id=rule_01158, source=v28_raw, lambda=None, p>=0.85, edge>=2.0, ask<=90.0, book<=750.0 | 372 | 79.84% | 76.07% | 82 | 80.49% | 82.00% | 65.71% |
| 5 | id=rule_01162, source=v28_raw, lambda=None, p>=0.85, edge>=2.0, ask<=95.0, book<=750.0 | 372 | 79.84% | 76.07% | 82 | 80.49% | 82.00% | 65.71% |
| 6 | id=rule_01166, source=v28_raw, lambda=None, p>=0.85, edge>=2.0, ask<=100.0, book<=750.0 | 372 | 79.84% | 76.07% | 82 | 80.49% | 82.00% | 65.71% |
| 7 | id=rule_01174, source=v28_raw, lambda=None, p>=0.85, edge>=4.0, ask<=90.0, book<=750.0 | 372 | 79.84% | 76.07% | 82 | 80.49% | 82.00% | 65.71% |
| 8 | id=rule_01178, source=v28_raw, lambda=None, p>=0.85, edge>=4.0, ask<=95.0, book<=750.0 | 372 | 79.84% | 76.07% | 82 | 80.49% | 82.00% | 65.71% |
| 9 | id=rule_01182, source=v28_raw, lambda=None, p>=0.85, edge>=4.0, ask<=100.0, book<=750.0 | 372 | 79.84% | 76.07% | 82 | 80.49% | 82.00% | 65.71% |
| 10 | id=rule_00003, source=v28, lambda=None, p>=0.85, edge>=2.0, ask<=85.0, book<=1000.0 | 409 | 75.79% | 83.64% | 92 | 78.26% | 92.00% | 63.64% |

## Completion Audit

| requirement | evidence | result |
|---|---|---|
| Use live websocket data | Parsed `logs\live_mushroom_v28_size2\bot.log` and `logs\live_mushroom_v28_size2\execution_events.ndjson` | done |
| Do not change running bot logic | This script only reads logs and writes artifacts under `logs/edge_research` | done |
| >=95% realized accuracy | target-pass rules: 0; observed-pass rules: 0 | not met |
| Keep >=75%-80% trade volume | enforced at >=75% trade and contract retention in all and holdout splits | not met |
| Not overfit | chronological train/validation/holdout and fold diagnostics included; no rule is promotable unless holdout also passes | not met |
| Verified with sample size | sample floors and Wilson lower bounds computed in CSV/JSON | not met |

Conclusion: with the current live v28 filled-trade sample, this scan did not find a fair-value selection version that satisfies the requested accuracy/volume/sample-size requirements. More live data or a materially different model family is needed before promotion.
