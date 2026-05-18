# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260511_020632Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-31.73
- Hold-to-settlement net for same entries: $-26.73
- Exit value added: $-5.00
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-11.97 | $-7.75 | $-4.22 | 15/11 |
| validation | 18 | $-16.52 | $-13.98 | $-2.54 | 7/11 |
| holdout | 9 | $-3.24 | $-5.00 | $1.76 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-19.27 | $12.46 | 17/6 | $-7.23/$-11.77/$-0.27 | 10/9/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-19.29 | $12.44 | 16/5 | $-7.23/$-11.79/$-0.27 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-20.62 | $11.11 | 14/5 | $-7.83/$-11.79/$-1.00 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-21.70 | $10.03 | 14/4 | $-8.21/$-13.22/$-0.27 | 9/5/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-22.78 | $8.95 | 15/4 | $-6.38/$-16.13/$-0.27 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-22.82 | $8.91 | 15/5 | $-7.23/$-15.32/$-0.27 | 10/6/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-23.11 | $8.62 | 13/3 | $-6.16/$-16.02/$-0.93 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-23.13 | $8.60 | 13/5 | $-7.61/$-14.59/$-0.93 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-23.37 | $8.36 | 5/1 | $-8.99/$-11.14/$-3.24 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-23.40 | $8.33 | 9/4 | $-11.14/$-10.49/$-1.77 | 5/6/2 |
| `suppress_collapse_exit_if_exit_btc_age_ms<=100 AND entry_to_exit_loss_cents>=20` | True | 8 (15.09%) | $-23.98 | $7.75 | 6/2 | $-8.83/$-11.91/$-3.24 | 3/5/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 26 (49.06%) | $-24.62 | $7.11 | 18/8 | $-6.10/$-15.59/$-2.93 | 16/3/7 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-24.63 | $7.10 | 5/0 | $-10.31/$-11.08/$-3.24 | 2/3/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND exit_sigma_t_dollars>=50` | True | 9 (16.98%) | $-24.63 | $7.10 | 8/1 | $-6.39/$-16.50/$-1.74 | 5/2/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-24.65 | $7.08 | 7/0 | $-6.39/$-16.52/$-1.74 | 5/0/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-25.11 | $6.62 | 11/3 | $-7.96/$-16.15/$-1.00 | 7/4/3 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.17 | $6.56 | 8/2 | $-7.97/$-15.46/$-1.74 | 7/1/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-25.33 | $6.40 | 4/2 | $-8.99/$-13.10/$-3.24 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-25.48 | $6.25 | 7/1 | $-10.32/$-14.89/$-0.27 | 2/2/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-25.52 | $6.21 | 10/5 | $-8.88/$-13.40/$-3.24 | 8/7/0 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.63 | $6.10 | 8/2 | $-7.39/$-16.50/$-1.74 | 6/2/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-25.94 | $5.79 | 7/3 | $-10.18/$-13.29/$-2.47 | 2/7/1 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND entry_to_exit_loss_cents>=10` | True | 6 (11.32%) | $-26.04 | $5.69 | 5/1 | $-7.05/$-16.52/$-2.47 | 5/0/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-26.07 | $5.66 | 4/1 | $-11.97/$-10.86/$-3.24 | 0/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-26.17 | $5.56 | 3/0 | $-11.97/$-10.96/$-3.24 | 0/3/0 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` improves the branch by $12.46 while suppressing 17 hurtful and 6 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
