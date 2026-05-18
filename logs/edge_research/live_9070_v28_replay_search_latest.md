# live_90_70 v28 Replay Accuracy/Volume Search

Generated UTC: 20260502_040343Z

## Status

FAIL: no replayed v28 selection rule met the 95% accuracy plus 75% volume gate.

## Scope

- Dataset: `research_data/live_90_70`
- This is a supplemental historical live replay, not the current live v28 fill tape.
- Historical Kalshi metadata is used only to recover missing market strikes.
- Existing bot logic/code is not changed.

## Data

- Input trade labels: 634
- BTC candle rows: 20958
- BTC candle window: 2026-03-24T01:28:59.999000+00:00 to 2026-04-07T14:45:59.999000+00:00
- Usable replayed entries: 509
- Metadata requested/fetched/cache hits: {'requested': 510, 'cache_hits': 100, 'fetched': 410, 'missing_after': 1}
- Skips: {'unresolved': 124, 'outside_btc_window': 0, 'missing_price': 0, 'missing_metadata': 0, 'missing_strike': 1, 'missing_close_time': 0, 'not_ready': 0, 'bad_horizon': 0, 'prediction_error': 0}
- Candidate rules scanned: 777

## Baseline Replayed Entry Set

- all: 501/509 trades (98.43%), 4903/4983 contracts (98.39%), contract retention 100.00%
- train: 305/305 trades (100.00%), 3003/3003 contracts (100.00%), contract retention 100.00%
- validation: 99/102 trades (97.06%), 964/994 contracts (96.98%), contract retention 100.00%
- holdout: 97/102 trades (95.10%), 936/986 contracts (94.93%), contract retention 100.00%

## Oracle Feasibility Bound

| split | retention floor | required trades | max trade acc | required contracts | max contract acc |
|---|---:|---:|---:|---:|---:|
| all | 75% | 382 | 100.00% | 3738 | 100.00% |
| all | 80% | 408 | 100.00% | 3987 | 100.00% |
| train | 75% | 229 | 100.00% | 2253 | 100.00% |
| train | 80% | 244 | 100.00% | 2403 | 100.00% |
| validation | 75% | 77 | 100.00% | 746 | 100.00% |
| validation | 80% | 82 | 100.00% | 796 | 100.00% |
| holdout | 75% | 77 | 100.00% | 740 | 100.00% |
| holdout | 80% | 82 | 100.00% | 789 | 100.00% |

## Scan Result

- Rules meeting observed accuracy/retention gate before sample floor: 0
- Rules meeting observed gate and sample-size floor: 0

## Top Ranked Rules

| rank | rule | all contracts | all acc | all retention | holdout contracts | holdout acc | holdout retention | validation acc | target |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | id=replay_rule_00003, p>=0.5, edge>=-30.0, ask<=92.0 | 1638 | 100.00% | 32.87% | 262 | 100.00% | 26.57% | 100.00% | False |
| 2 | id=replay_rule_00058, p>=0.55, edge>=-30.0, ask<=92.0 | 1638 | 100.00% | 32.87% | 262 | 100.00% | 26.57% | 100.00% | False |
| 3 | id=replay_rule_00113, p>=0.6, edge>=-30.0, ask<=92.0 | 1638 | 100.00% | 32.87% | 262 | 100.00% | 26.57% | 100.00% | False |
| 4 | id=replay_rule_00168, p>=0.65, edge>=-30.0, ask<=92.0 | 1528 | 100.00% | 30.66% | 242 | 100.00% | 24.54% | 100.00% | False |
| 5 | id=replay_rule_00223, p>=0.7, edge>=-30.0, ask<=92.0 | 1277 | 100.00% | 25.63% | 192 | 100.00% | 19.47% | 100.00% | False |
| 6 | id=replay_rule_00008, p>=0.5, edge>=-20.0, ask<=92.0 | 1176 | 100.00% | 23.60% | 172 | 100.00% | 17.44% | 100.00% | False |
| 7 | id=replay_rule_00063, p>=0.55, edge>=-20.0, ask<=92.0 | 1176 | 100.00% | 23.60% | 172 | 100.00% | 17.44% | 100.00% | False |
| 8 | id=replay_rule_00118, p>=0.6, edge>=-20.0, ask<=92.0 | 1176 | 100.00% | 23.60% | 172 | 100.00% | 17.44% | 100.00% | False |
| 9 | id=replay_rule_00173, p>=0.65, edge>=-20.0, ask<=92.0 | 1176 | 100.00% | 23.60% | 172 | 100.00% | 17.44% | 100.00% | False |
| 10 | id=replay_rule_00228, p>=0.7, edge>=-20.0, ask<=92.0 | 1176 | 100.00% | 23.60% | 172 | 100.00% | 17.44% | 100.00% | False |

## Top High-Volume Rules

| rank | rule | all contracts | all acc | all retention | holdout contracts | holdout acc | holdout retention | validation acc |
|---:|---|---:|---:|---:|---:|---:|---:|---:|

## Completion Audit

| requirement | evidence | result |
|---|---|---|
| Use live data | Uses `live_90_70` live labels plus local BTC candles; metadata only supplies strikes | done |
| Do not change bot logic | Standalone probe writes only `logs/edge_research` artifacts | done |
| >=95% realized accuracy | target-pass rules: 0; observed-pass rules: 0 | not met |
| Keep >=75%-80% volume | enforced at >=75% all and holdout trade/contract retention | not met |
| Not overfit | chronological train/validation/holdout split; holdout must pass | not met |
| Verified with sample size | selected all/holdout sample floors enforced | not met |
