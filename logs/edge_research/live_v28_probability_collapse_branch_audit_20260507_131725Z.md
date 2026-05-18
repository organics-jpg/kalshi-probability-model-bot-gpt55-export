# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260507_131725Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 71
- Actual collapse-exit net: $-41.46
- Hold-to-settlement net for same entries: $-40.94
- Exit value added: $-0.52
- Hurtful/helpful exits: 32 / 39

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 39 | $-20.94 | $-20.64 | $-0.30 | 20/19 |
| validation | 16 | $-14.02 | $-9.36 | $-4.66 | 6/10 |
| holdout | 16 | $-6.50 | $-10.94 | $4.44 | 6/10 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 27 (38.03%) | $-23.46 | $18.00 | 20/7 | $-18.28/$-4.28/$-0.90 | 15/6/6 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 30 (42.25%) | $-24.56 | $16.90 | 21/9 | $-17.30/$-6.36/$-0.90 | 16/8/6 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 24 (33.80%) | $-25.34 | $16.12 | 17/7 | $-18.84/$-4.28/$-2.22 | 14/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 17 (23.94%) | $-26.50 | $14.96 | 12/5 | $-19.30/$-4.28/$-2.92 | 8/6/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 22 (30.99%) | $-28.46 | $13.00 | 17/5 | $-19.18/$-8.38/$-0.90 | 14/2/6 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 7 (9.86%) | $-28.80 | $12.66 | 7/0 | $-18.42/$-3.88/$-6.50 | 3/4/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=15 AND exit_sigma_t_dollars>=75` | True | 11 (15.49%) | $-29.16 | $12.30 | 7/4 | $-18.38/$-4.28/$-6.50 | 5/6/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 25 (35.21%) | $-30.42 | $11.04 | 17/8 | $-17.52/$-12.00/$-0.90 | 13/6/6 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 24 (33.80%) | $-30.58 | $10.88 | 18/6 | $-19.22/$-10.46/$-0.90 | 14/4/6 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 7 (9.86%) | $-30.62 | $10.84 | 6/1 | $-14.60/$-9.52/$-6.50 | 5/2/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 26 (36.62%) | $-30.72 | $10.74 | 18/8 | $-17.82/$-12.00/$-0.90 | 14/6/6 |
| `suppress_collapse_exit_if_exit_p_hold<=0.6 AND exit_sigma_t_dollars>=75` | True | 13 (18.31%) | $-31.24 | $10.22 | 7/6 | $-18.38/$-6.36/$-6.50 | 5/8/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=20 AND exit_btc_age_ms<=100` | True | 7 (9.86%) | $-31.32 | $10.14 | 5/2 | $-20.14/$-4.68/$-6.50 | 1/6/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=20` | True | 12 (16.90%) | $-31.48 | $9.98 | 7/5 | $-20.70/$-4.28/$-6.50 | 6/6/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 19 (26.76%) | $-31.94 | $9.52 | 12/7 | $-19.08/$-6.36/$-6.50 | 11/8/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 9 (12.68%) | $-32.18 | $9.28 | 9/0 | $-15.78/$-14.02/$-2.38 | 5/0/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 35 (49.30%) | $-32.42 | $9.04 | 23/12 | $-17.50/$-8.42/$-6.50 | 20/3/12 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 14 (19.72%) | $-32.52 | $8.94 | 9/5 | $-16.82/$-12.00/$-3.70 | 6/6/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 7 (9.86%) | $-32.54 | $8.92 | 5/2 | $-16.52/$-9.52/$-6.50 | 5/2/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=90` | True | 24 (33.80%) | $-32.68 | $8.78 | 16/8 | $-19.78/$-12.00/$-0.90 | 12/6/6 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 12 (16.90%) | $-32.94 | $8.52 | 10/2 | $-16.54/$-14.02/$-2.38 | 8/0/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 4 (5.63%) | $-33.14 | $8.32 | 4/0 | $-17.12/$-9.52/$-6.50 | 2/2/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=300` | True | 15 (21.13%) | $-33.30 | $8.16 | 10/5 | $-20.84/$-5.96/$-6.50 | 9/6/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 6 (8.45%) | $-33.34 | $8.12 | 5/1 | $-18.46/$-8.38/$-6.50 | 4/2/0 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND position_seconds<=45` | True | 25 (35.21%) | $-33.40 | $8.06 | 19/6 | $-16.24/$-14.02/$-3.14 | 17/0/8 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` improves the branch by $18.00 while suppressing 20 hurtful and 7 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
