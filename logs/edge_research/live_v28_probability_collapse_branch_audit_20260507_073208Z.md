# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260507_073208Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 67
- Actual collapse-exit net: $-40.42
- Hold-to-settlement net for same entries: $-39.26
- Exit value added: $-1.16
- Hurtful/helpful exits: 30 / 37

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 37 | $-20.38 | $-21.36 | $0.98 | 18/19 |
| validation | 18 | $-14.58 | $-8.64 | $-5.94 | 8/10 |
| holdout | 12 | $-5.46 | $-9.26 | $3.80 | 4/8 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 25 (37.31%) | $-23.90 | $16.52 | 18/7 | $-17.72/$-4.84/$-1.34 | 15/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 28 (41.79%) | $-25.00 | $15.42 | 19/9 | $-16.74/$-6.92/$-1.34 | 16/8/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 22 (32.84%) | $-25.78 | $14.64 | 15/7 | $-18.28/$-4.84/$-2.66 | 14/6/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 15 (22.39%) | $-26.94 | $13.48 | 10/5 | $-18.74/$-4.84/$-3.36 | 8/6/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 7 (10.45%) | $-27.76 | $12.66 | 7/0 | $-17.86/$-4.44/$-5.46 | 3/4/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=15 AND exit_sigma_t_dollars>=75` | True | 11 (16.42%) | $-28.12 | $12.30 | 7/4 | $-17.82/$-4.84/$-5.46 | 5/6/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 20 (29.85%) | $-28.90 | $11.52 | 15/5 | $-18.62/$-8.94/$-1.34 | 14/2/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 7 (10.45%) | $-29.58 | $10.84 | 6/1 | $-14.04/$-10.08/$-5.46 | 5/2/0 |
| `suppress_collapse_exit_if_exit_p_hold<=0.6 AND exit_sigma_t_dollars>=75` | True | 13 (19.40%) | $-30.20 | $10.22 | 7/6 | $-17.82/$-6.92/$-5.46 | 5/8/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=20 AND exit_btc_age_ms<=100` | True | 7 (10.45%) | $-30.28 | $10.14 | 5/2 | $-19.58/$-5.24/$-5.46 | 1/6/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=20` | True | 12 (17.91%) | $-30.44 | $9.98 | 7/5 | $-20.14/$-4.84/$-5.46 | 6/6/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 23 (34.33%) | $-30.86 | $9.56 | 15/8 | $-16.96/$-12.56/$-1.34 | 13/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 19 (28.36%) | $-30.90 | $9.52 | 12/7 | $-18.52/$-6.92/$-5.46 | 11/8/0 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 22 (32.84%) | $-31.02 | $9.40 | 16/6 | $-18.66/$-11.02/$-1.34 | 14/4/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 9 (13.43%) | $-31.14 | $9.28 | 9/0 | $-15.22/$-14.58/$-1.34 | 5/0/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 24 (35.82%) | $-31.16 | $9.26 | 16/8 | $-17.26/$-12.56/$-1.34 | 14/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 14 (20.90%) | $-31.48 | $8.94 | 9/5 | $-16.26/$-12.56/$-2.66 | 6/6/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 7 (10.45%) | $-31.50 | $8.92 | 5/2 | $-15.96/$-10.08/$-5.46 | 5/2/0 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 12 (17.91%) | $-31.90 | $8.52 | 10/2 | $-15.98/$-14.58/$-1.34 | 8/0/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 4 (5.97%) | $-32.10 | $8.32 | 4/0 | $-16.56/$-10.08/$-5.46 | 2/2/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=300` | True | 15 (22.39%) | $-32.26 | $8.16 | 10/5 | $-20.28/$-6.52/$-5.46 | 9/6/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 6 (8.96%) | $-32.30 | $8.12 | 5/1 | $-17.90/$-8.94/$-5.46 | 4/2/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents<=70 AND exit_sigma_t_dollars>=50` | True | 15 (22.39%) | $-32.68 | $7.74 | 8/7 | $-13.86/$-13.36/$-5.46 | 7/8/0 |
| `suppress_collapse_exit_if_exit_p_hold>=0.65 AND exit_fair_drawdown_cents<=8` | True | 9 (13.43%) | $-32.84 | $7.58 | 8/1 | $-16.92/$-14.58/$-1.34 | 5/0/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=55 AND exit_fair_drawdown_cents<=8` | True | 7 (10.45%) | $-33.04 | $7.38 | 7/0 | $-17.12/$-14.58/$-1.34 | 3/0/4 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` improves the branch by $16.52 while suppressing 18 hurtful and 7 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
