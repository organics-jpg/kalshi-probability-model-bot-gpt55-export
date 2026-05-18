# 80% Retention Regime Classifier Probe

Generated UTC: `20260504_054944Z`

## Scope

- Research-only probe; no orders are submitted and no bot files are modified.
- Source: `logs\edge_research\live_heartbeat_two_side_fv_ledger_latest.csv`.
- Primary live websocket view: `two_side_minute_bucket`.
- Each candidate chooses one side per opportunity, then applies one interpretable regime gate.
- Retention floor is 80% on all, train, validation, and holdout splits.

## Coverage

- Primary opportunities: 4310
- Train opportunities: 2586
- Validation opportunities: 862
- Holdout opportunities: 862
- Candidate regime rules scanned: 3144
- Rules keeping >=80% on every split: 1321
- Target-pass rules at >=95% accuracy and >=80% retention: 0

## Best 80%-Retention Candidates

| rank | chooser | gate | all acc | all ret | train acc | val acc | val ret | holdout acc | holdout ret | selected | target |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `score_min_book_rv15_drift5` | `book_p_side>=0.55 and margin_per_rv_sigma_15m>=0` | 83.23% | 81.37% | 81.55% | 86.08% | 80.86% | 85.29% | 85.15% | 3507 | False |
| 2 | `score_mean_book_rv15_drift5` | `book_p_side>=0.55 and margin_per_rv_sigma_15m>=0` | 83.05% | 81.86% | 81.35% | 85.88% | 81.32% | 85.19% | 85.38% | 3528 | False |
| 3 | `book_p_side` | `brownian_p_rv_30m>=0.55` | 82.65% | 81.55% | 80.81% | 85.51% | 82.48% | 85.14% | 83.53% | 3515 | False |
| 4 | `book_p_side` | `brownian_p_rv_30m>=0.55 and margin_per_rv_sigma_15m>=0` | 82.65% | 81.55% | 80.81% | 85.51% | 82.48% | 85.14% | 83.53% | 3515 | False |
| 5 | `book_p_side` | `brownian_p_rv_30m>=0.55 and spread_cents<=4` | 82.63% | 81.46% | 80.79% | 85.47% | 82.25% | 85.14% | 83.53% | 3511 | False |
| 6 | `score_min_book_rv15_drift5` | `book_p_side>=0.55` | 82.89% | 82.71% | 81.11% | 85.88% | 82.13% | 85.10% | 86.43% | 3565 | False |
| 7 | `score_min_book_rv15_drift5` | `book_p_side>=0.55 and spread_cents<=4` | 82.87% | 82.62% | 81.09% | 85.84% | 81.90% | 85.10% | 86.43% | 3561 | False |
| 8 | `book_p_side` | `score_regime_blend>=0.58 and margin_per_rv_sigma_15m>=0` | 83.03% | 81.51% | 81.19% | 86.43% | 81.21% | 85.10% | 83.29% | 3513 | False |
| 9 | `book_p_side` | `brownian_p_rv_30m>=0.55 and abs_book_rv30_gap<=0.3` | 82.61% | 81.37% | 80.77% | 85.47% | 82.25% | 85.10% | 83.29% | 3507 | False |
| 10 | `book_p_side` | `brownian_p_rv_30m>=0.55 and abs_book_rv15_gap<=0.3` | 82.62% | 81.44% | 80.79% | 85.51% | 82.48% | 85.08% | 83.18% | 3510 | False |
| 11 | `score_min_book_rv15_drift5` | `book_p_side>=0.55 and abs_book_rv30_gap<=0.3` | 82.83% | 82.44% | 81.05% | 85.84% | 81.90% | 85.04% | 86.08% | 3553 | False |
| 12 | `score_mean_book_rv15_drift5` | `book_p_side>=0.55` | 82.71% | 83.18% | 80.90% | 85.67% | 82.60% | 85.01% | 86.66% | 3585 | False |
| 13 | `score_mean_book_rv15_drift5` | `book_p_side>=0.55 and spread_cents<=4` | 82.69% | 83.09% | 80.89% | 85.63% | 82.37% | 85.01% | 86.66% | 3581 | False |
| 14 | `score_min_book_rv15_drift5` | `book_p_side>=0.55 and abs_book_rv15_gap<=0.3` | 82.86% | 82.46% | 81.10% | 85.88% | 82.13% | 85.00% | 85.85% | 3554 | False |
| 15 | `score_mean_book_rv15_drift5` | `book_p_side>=0.55 and abs_book_rv30_gap<=0.3` | 82.65% | 82.90% | 80.84% | 85.63% | 82.37% | 84.95% | 86.31% | 3573 | False |

## Train-Threshold Top-80 Frontier

These rows pick the score threshold from the train split only, retaining the top 80% of train opportunities, then apply that fixed threshold forward.

| feature | threshold | all acc | all ret | val acc | val ret | holdout acc | holdout ret | target |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `brownian_p_rv_15m` | 0.56299 | 83.20% | 80.67% | 86.84% | 81.09% | 85.47% | 82.25% | False |
| `score_regime_blend` | 0.593717 | 83.26% | 80.79% | 86.41% | 81.09% | 85.57% | 82.83% | False |
| `score_min_book_rv15` | 0.544223 | 83.26% | 80.95% | 86.29% | 81.21% | 85.56% | 83.53% | False |
| `score_mean_book_rv15` | 0.567236 | 82.95% | 81.37% | 85.71% | 82.83% | 84.94% | 83.99% | False |
| `brownian_p_rv_30m` | 0.55791 | 82.61% | 81.11% | 85.45% | 82.13% | 84.98% | 83.41% | False |
| `book_p_side` | 0.575 | 83.14% | 81.88% | 85.42% | 83.53% | 85.66% | 85.73% | False |
| `drift_p_5m_rv_15m` | 0.688516 | 80.10% | 81.48% | 82.25% | 83.64% | 81.58% | 83.76% | False |

## Physics Read

- Best >=80% retained candidate by validation/holdout balance: `score_min_book_rv15_drift5` with gate `book_p_side>=0.55 and margin_per_rv_sigma_15m>=0`.
- It selected 3507/4310 opportunities (81.37%) at 83.23% all accuracy.
- Validation was 86.08% at 80.86%; holdout was 85.29% at 85.15%.
- To reach 95% on validation from this candidate without losing wins, another 66 selected losses would need to be blocked.
- To reach 95% on holdout from this candidate without losing wins, another 76 selected losses would need to be blocked.

## Conclusion

No interpretable regime candidate cleared 95% accuracy while keeping 80% of opportunities on chronological splits.
The current frontier is still an accuracy-volume problem: high-confidence book/physics states are real, but at an 80% trade-retention floor the validation split remains far below the promotion target.
