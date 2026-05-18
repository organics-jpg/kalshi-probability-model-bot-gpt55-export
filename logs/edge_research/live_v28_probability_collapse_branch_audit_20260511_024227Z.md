# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260511_024227Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-31.69
- Hold-to-settlement net for same entries: $-26.73
- Exit value added: $-4.96
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-11.60 | $-7.79 | $-3.81 | 15/11 |
| validation | 18 | $-16.81 | $-13.96 | $-2.85 | 7/11 |
| holdout | 9 | $-3.28 | $-4.98 | $1.70 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-18.98 | $12.71 | 17/6 | $-7.00/$-11.73/$-0.25 | 10/9/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-19.08 | $12.61 | 16/5 | $-7.00/$-11.83/$-0.25 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-20.41 | $11.28 | 14/5 | $-7.60/$-11.83/$-0.98 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-21.49 | $10.20 | 14/4 | $-7.98/$-13.26/$-0.25 | 9/5/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-22.42 | $9.27 | 15/4 | $-6.08/$-16.09/$-0.25 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-22.71 | $8.98 | 15/5 | $-7.00/$-15.46/$-0.25 | 10/6/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-22.99 | $8.70 | 13/3 | $-5.86/$-16.16/$-0.97 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-23.08 | $8.61 | 13/5 | $-7.38/$-14.73/$-0.97 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-23.26 | $8.43 | 9/4 | $-10.91/$-10.60/$-1.75 | 5/6/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-23.33 | $8.36 | 5/1 | $-8.62/$-11.43/$-3.28 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-24.48 | $7.21 | 5/0 | $-10.01/$-11.19/$-3.28 | 2/3/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND exit_sigma_t_dollars>=50` | True | 9 (16.98%) | $-24.51 | $7.18 | 8/1 | $-6.02/$-16.71/$-1.78 | 5/2/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-24.61 | $7.08 | 7/0 | $-6.02/$-16.81/$-1.78 | 5/0/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 26 (49.06%) | $-24.71 | $6.98 | 18/8 | $-5.92/$-15.88/$-2.91 | 16/3/7 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-24.83 | $6.86 | 11/3 | $-7.66/$-16.19/$-0.98 | 7/4/3 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.13 | $6.56 | 8/2 | $-7.60/$-15.75/$-1.78 | 7/1/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-25.24 | $6.45 | 4/2 | $-8.62/$-13.34/$-3.28 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-25.31 | $6.38 | 7/1 | $-9.95/$-15.11/$-0.25 | 2/2/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-25.36 | $6.33 | 10/5 | $-8.65/$-13.43/$-3.28 | 8/7/0 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.51 | $6.18 | 8/2 | $-7.02/$-16.71/$-1.78 | 6/2/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-25.85 | $5.84 | 4/1 | $-11.60/$-10.97/$-3.28 | 0/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-25.89 | $5.80 | 7/3 | $-9.88/$-13.50/$-2.51 | 2/7/1 |
| `suppress_collapse_exit_if_exit_btc_age_ms<=100 AND entry_to_exit_loss_cents>=20` | True | 9 (16.98%) | $-25.92 | $5.77 | 6/3 | $-10.62/$-12.02/$-3.28 | 4/5/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND entry_to_exit_loss_cents>=10` | True | 6 (11.32%) | $-25.97 | $5.72 | 5/1 | $-6.65/$-16.81/$-2.51 | 5/0/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-26.13 | $5.56 | 3/0 | $-11.60/$-11.25/$-3.28 | 0/3/0 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` improves the branch by $12.71 while suppressing 17 hurtful and 6 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
