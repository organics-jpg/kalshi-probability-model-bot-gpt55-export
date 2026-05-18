# Profit Lock Signal Conflict Arbitration Audit

Generated UTC: `20260504_161802Z`

## Scope

- Research-only audit using existing pre-resolution registries.
- Tests market-level vote/consensus arbitration rules over signals already registered before outcomes.
- Stress-pass rows are diagnostic only; they are not promotion authority without a new frozen forward monitor.

## Inputs

- Registry rows read: `1896`
- Resolved market universe: `108`
- Pending market universe: `0`
- Coverage floor: `80.00%`
- Positive block-rate floor: `70.00%` with `12` markets/block

## Candidate Summary

| candidate | resolved/pending | wins/losses | acc | break-even | Wilson low | P(p>BE) | p05 edge | coverage | reg coverage | net P&L | ROI | +wins | block+cov | stress pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `majority60_path_veto` | 70/0 | 49/21 | 70.00% | 62.83% | 58.46% | 0.887 | -2.6c | 64.81% | 64.81% | 502.0c | 11.41% | 6 | 33.33% | False |
| `core_no_impulse_share70_margin8` | 69/0 | 47/22 | 68.12% | 61.94% | 56.42% | 0.846 | -3.7c | 63.89% | 63.89% | 426.0c | 9.97% | 8 | 33.33% | False |
| `all_opposition_le4` | 64/0 | 44/20 | 68.75% | 62.45% | 56.61% | 0.843 | -3.9c | 59.26% | 59.26% | 403.0c | 10.08% | 8 | 11.11% | False |
| `all_share70_margin8` | 68/0 | 46/22 | 67.65% | 62.07% | 55.84% | 0.820 | -4.4c | 62.96% | 62.96% | 379.0c | 8.98% | 9 | 33.33% | False |
| `book_hazard_agree_majority` | 32/0 | 23/9 | 71.88% | 61.28% | 54.63% | 0.881 | -4.0c | 29.63% | 29.63% | 339.0c | 17.29% | 4 | 22.22% | False |
| `all_majority` | 80/0 | 53/27 | 66.25% | 62.25% | 55.36% | 0.759 | -5.1c | 74.07% | 74.07% | 320.0c | 6.43% | 12 | 33.33% | False |
| `book_touch_agree_majority` | 43/0 | 30/13 | 69.77% | 62.65% | 54.89% | 0.818 | -5.5c | 39.81% | 39.81% | 306.0c | 11.36% | 8 | 0.00% | False |
| `all_share60_margin4` | 77/0 | 51/26 | 66.23% | 62.31% | 55.12% | 0.750 | -5.4c | 71.30% | 71.30% | 302.0c | 6.29% | 13 | 33.33% | False |
| `core_no_impulse_share60_margin4` | 77/0 | 51/26 | 66.23% | 62.31% | 55.12% | 0.750 | -5.4c | 71.30% | 71.30% | 302.0c | 6.29% | 13 | 33.33% | False |
| `majority60_hazard_veto` | 77/0 | 51/26 | 66.23% | 62.31% | 55.12% | 0.748 | -5.4c | 71.30% | 71.30% | 302.0c | 6.29% | 13 | 33.33% | False |
| `book_v2_touch_agree_majority` | 40/0 | 28/12 | 70.00% | 62.52% | 54.57% | 0.822 | -5.6c | 37.04% | 37.04% | 299.0c | 11.96% | 7 | 0.00% | False |
| `book_score_touch_agree_majority` | 40/0 | 28/12 | 70.00% | 62.78% | 54.57% | 0.813 | -5.9c | 37.04% | 37.04% | 289.0c | 11.51% | 8 | 0.00% | False |
| `core_no_path_share60_margin4` | 76/0 | 50/26 | 65.79% | 62.29% | 54.60% | 0.722 | -6.0c | 70.37% | 70.37% | 266.0c | 5.62% | 14 | 33.33% | False |
| `majority60_touch_veto` | 59/0 | 39/20 | 66.10% | 62.22% | 53.37% | 0.715 | -6.9c | 54.63% | 54.63% | 229.0c | 6.24% | 13 | 11.11% | False |
| `touch_hazard_consensus` | 97/0 | 58/39 | 59.79% | 61.15% | 49.84% | 0.380 | -9.8c | 89.81% | 89.81% | -132.0c | -2.23% | 27 | 44.44% | False |
| `book_family_consensus` | 56/0 | 36/20 | 64.29% | 67.20% | 51.19% | 0.300 | -14.0c | 51.85% | 51.85% | -163.0c | -4.33% | 27 | 33.33% | False |

## Pending Arbitration

- No currently pending markets selected by these arbitration rules.

## Read

- No arbitration rule clears the diagnostic stress checks.
