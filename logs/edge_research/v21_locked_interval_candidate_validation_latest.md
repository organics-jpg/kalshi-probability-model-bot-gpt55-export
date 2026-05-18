# V21 Locked Interval Candidate Validation

Generated UTC: `20260502_174526Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Source dataset: `research_data/live_mushroom_v21_size2` native passive ticker websocket stream.
- Outcomes are inferred from cached Coinbase BTC 1m close at market expiry versus recorded strike.
- Candidate policies are loaded from frozen simple/staged/logit locks; no threshold search is performed.
- Volume denominator is recurring BTC 15-minute markets.

## Data

- Watch markets parsed: 223
- Markets with inferred outcomes: 221
- Minute decision rows before physics: 6554
- Minute decision rows after candle physics: 6554
- Resolved interval denominator: 221

## Frozen Candidate Validation

| candidate | kind | target | Wilson | all acc | all cov | all Wilson low | holdout acc | holdout cov | median ask | ask=100 | ROI |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `locked_logit_book_physics_c005_p095_20260502_1512` | logit | False | False | 95.18% | 75.11% | 90.78% | 93.94% | 73.33% | 98.0 | 26 | -2.69% |
| `staged_score_min_fallback_20260502_1511` | staged | False | False | 94.83% | 78.73% | 90.46% | 91.89% | 82.22% | 97.0 | 23 | -2.01% |
| `raw_regime_blend_high_price_20260502_1510` | simple | False | False | 94.51% | 74.21% | 89.90% | 96.97% | 73.33% | 97.0 | 18 | -2.63% |
| `raw_score_min_book_rv15_existing_lock` | simple | False | False | 93.22% | 80.09% | 88.52% | 89.47% | 84.44% | 96.0 | 13 | -2.31% |
| `economical_score_min_book_rv15_20260502_1511` | simple | False | False | 88.83% | 81.00% | 83.37% | 91.43% | 77.78% | 89.0 | 0 | 0.75% |

## Read

No frozen simple/staged/logit candidate clears the 95% / 80% split target on this independent live websocket dataset.
The high-price degeneracy warning remains visible on at least one candidate.
