# Probability Multifeature Logit Audit

Generated UTC: `20260504_101006Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Fits regularized logistic models on pooled current+v21 train rows only.
- Chooses EV floors using train coverage/P&L only, then evaluates validation and holdout.

## Selected Train Floors

Coverage floor: `75.00%` on train, validation, and holdout.

| dataset | model | EV floor | val net/cov | holdout net/cov | all net/ROI | OOS pass |
|---|---|---:|---:|---:|---:|---|
| current | `prob3_C0.05` | -30.0c | -814.0c/100.00% | -283.0c/100.00% | -310.0c/-1.70% | False |
| v21 | `prob3_C0.05` | -30.0c | 32.0c/100.00% | 452.0c/97.78% | 276.0c/2.12% | True |
| current | `prob3_C0.1` | -30.0c | -915.0c/100.00% | -485.0c/100.00% | -724.0c/-3.97% | False |
| v21 | `prob3_C0.1` | -30.0c | 127.0c/100.00% | 452.0c/97.78% | 270.0c/2.07% | True |
| current | `prob3_C0.25` | -30.0c | -816.0c/100.00% | -585.0c/100.00% | -826.0c/-4.53% | False |
| v21 | `prob3_C0.25` | -30.0c | 127.0c/100.00% | 350.0c/97.78% | 263.0c/2.02% | True |
| current | `prob_gap_margin_C0.05` | -30.0c | -809.0c/100.00% | -283.0c/100.00% | -305.0c/-1.68% | False |
| v21 | `prob_gap_margin_C0.05` | -30.0c | 32.0c/100.00% | 452.0c/97.78% | 488.0c/3.75% | True |
| current | `prob_gap_margin_C0.1` | -30.0c | -814.0c/100.00% | -384.0c/100.00% | -716.0c/-3.93% | False |
| v21 | `prob_gap_margin_C0.1` | -30.0c | 32.0c/100.00% | 452.0c/97.78% | 175.0c/1.34% | True |
| current | `prob_gap_margin_C0.25` | -30.0c | -816.0c/100.00% | -585.0c/100.00% | -725.0c/-3.98% | False |
| v21 | `prob_gap_margin_C0.25` | -30.0c | 127.0c/100.00% | 452.0c/97.78% | 270.0c/2.07% | True |
| current | `prob_micro_full_C0.05` | -5.0c | -635.0c/100.00% | 200.0c/100.00% | 176.0c/0.97% | False |
| v21 | `prob_micro_full_C0.05` | -5.0c | -149.0c/100.00% | 360.0c/97.78% | 1044.0c/8.06% | False |
| current | `prob_micro_full_C0.1` | -30.0c | -590.0c/100.00% | 142.0c/100.00% | 2.0c/0.01% | False |
| v21 | `prob_micro_full_C0.1` | -30.0c | 139.0c/100.00% | 362.0c/97.78% | 1654.0c/12.78% | True |
| current | `prob_micro_full_C0.25` | -30.0c | -691.0c/100.00% | 43.0c/100.00% | 210.0c/1.16% | False |
| v21 | `prob_micro_full_C0.25` | -30.0c | 240.0c/100.00% | 362.0c/97.78% | 1644.0c/12.69% | True |
| current | `prob_path_compact_C0.05` | -30.0c | -689.0c/100.00% | 39.0c/100.00% | -20.0c/-0.11% | False |
| v21 | `prob_path_compact_C0.05` | -30.0c | -164.0c/100.00% | 564.0c/97.78% | 1258.0c/9.72% | False |
| current | `prob_path_compact_C0.1` | -5.0c | -825.0c/100.00% | -16.0c/100.00% | -363.0c/-2.00% | False |
| v21 | `prob_path_compact_C0.1` | -5.0c | -173.0c/100.00% | 766.0c/97.78% | 1272.0c/9.76% | False |
| current | `prob_path_compact_C0.25` | -5.0c | -810.0c/100.00% | -121.0c/100.00% | -137.0c/-0.76% | False |
| v21 | `prob_path_compact_C0.25` | -5.0c | -69.0c/100.00% | 661.0c/97.78% | 1150.0c/8.81% | False |

## Fit Summary

| model | C | train rows | train logloss | features |
|---|---:|---:|---:|---|
| `prob3_C0.05` | 0.05 | 25104 | 0.4282 | 3 features |
| `prob3_C0.1` | 0.10 | 25104 | 0.4275 | 3 features |
| `prob3_C0.25` | 0.25 | 25104 | 0.4272 | 3 features |
| `prob_gap_margin_C0.05` | 0.05 | 25104 | 0.4281 | 5 features |
| `prob_gap_margin_C0.1` | 0.10 | 25104 | 0.4275 | 5 features |
| `prob_gap_margin_C0.25` | 0.25 | 25104 | 0.4271 | 5 features |
| `prob_micro_full_C0.05` | 0.05 | 25104 | 0.4274 | 15 features |
| `prob_micro_full_C0.1` | 0.10 | 25104 | 0.4268 | 15 features |
| `prob_micro_full_C0.25` | 0.25 | 25104 | 0.4264 | 15 features |
| `prob_path_compact_C0.05` | 0.05 | 25104 | 0.4277 | 9 features |
| `prob_path_compact_C0.1` | 0.10 | 25104 | 0.4272 | 9 features |
| `prob_path_compact_C0.25` | 0.25 | 25104 | 0.4268 | 9 features |

## Read

- `prob3_C0.05` both-dataset OOS pass/combined OOS net: False/-613.0c.
- `prob3_C0.1` both-dataset OOS pass/combined OOS net: False/-821.0c.
- `prob3_C0.25` both-dataset OOS pass/combined OOS net: False/-924.0c.
- `prob_gap_margin_C0.05` both-dataset OOS pass/combined OOS net: False/-608.0c.
- `prob_gap_margin_C0.1` both-dataset OOS pass/combined OOS net: False/-714.0c.
- `prob_gap_margin_C0.25` both-dataset OOS pass/combined OOS net: False/-822.0c.
- `prob_path_compact_C0.05` both-dataset OOS pass/combined OOS net: False/-250.0c.
- `prob_path_compact_C0.1` both-dataset OOS pass/combined OOS net: False/-248.0c.
- `prob_path_compact_C0.25` both-dataset OOS pass/combined OOS net: False/-339.0c.
- `prob_micro_full_C0.05` both-dataset OOS pass/combined OOS net: False/-224.0c.
- `prob_micro_full_C0.1` both-dataset OOS pass/combined OOS net: False/53.0c.
- `prob_micro_full_C0.25` both-dataset OOS pass/combined OOS net: False/-46.0c.
- No multifeature logit model clears positive high-coverage OOS on both datasets.
