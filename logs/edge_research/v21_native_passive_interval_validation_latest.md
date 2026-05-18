# V21 Native Passive Interval Validation

Generated UTC: `20260502_153954Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Source dataset: `research_data/live_mushroom_v21_size2` native passive ticker websocket stream.
- Outcomes are inferred from cached Coinbase BTC 1m close at market expiry versus recorded strike.
- Candidate policies are loaded from existing locked pure-physics interval locks; no threshold search is performed.

## Data

- Watch markets parsed: 217
- Markets with inferred outcomes: 216
- Minute decision rows before physics: 6446
- Minute decision rows after candle physics: 6446
- Resolved interval denominator: 216

## Locked Candidate Validation

| candidate | target | Wilson | all acc | all cov | all Wilson low | holdout acc | holdout cov | median ask | ask=100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `pure_brownian_rv30_adverse15_high_price_20260502_1522` | False | False | 97.87% | 65.28% | 93.93% | 100.00% | 61.36% | 98.0 | 27 |
| `pure_physics_mean_rv15_rv30_high_price_20260502_1522` | False | False | 98.58% | 65.28% | 94.98% | 100.00% | 61.36% | 98.0 | 30 |
| `pure_brownian_rv15_spread4_best_high_coverage_20260502_1522` | False | False | 93.14% | 81.02% | 88.40% | 89.47% | 86.36% | 95.0 | 12 |
| `pure_brownian_rv30_economical_adverse15_20260502_1522` | False | False | 85.56% | 83.33% | 79.68% | 85.71% | 79.55% | 85.0 | 0 |

## Read

No locked pure-physics candidate clears the 95% / 80% split target on this independent live websocket dataset.
The high-price degeneracy warning remains visible on at least one candidate.
