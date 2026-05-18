# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260511_015329Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-31.82
- Hold-to-settlement net for same entries: $-26.73
- Exit value added: $-5.09
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-11.86 | $-7.75 | $-4.11 | 15/11 |
| validation | 18 | $-16.61 | $-14.00 | $-2.61 | 7/11 |
| holdout | 9 | $-3.35 | $-4.98 | $1.63 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-19.35 | $12.47 | 17/6 | $-7.26/$-11.77/$-0.32 | 10/9/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-19.45 | $12.37 | 16/5 | $-7.26/$-11.87/$-0.32 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-20.78 | $11.04 | 14/5 | $-7.86/$-11.87/$-1.05 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-21.80 | $10.02 | 14/4 | $-8.24/$-13.24/$-0.32 | 9/5/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-22.80 | $9.02 | 15/4 | $-6.41/$-16.07/$-0.32 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-22.90 | $8.92 | 15/5 | $-7.26/$-15.32/$-0.32 | 10/6/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-23.19 | $8.63 | 13/3 | $-6.19/$-15.96/$-1.04 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-23.27 | $8.55 | 13/5 | $-7.64/$-14.59/$-1.04 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-23.46 | $8.36 | 5/1 | $-8.88/$-11.23/$-3.35 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-23.56 | $8.26 | 9/4 | $-11.10/$-10.64/$-1.82 | 5/6/2 |
| `suppress_collapse_exit_if_exit_btc_age_ms<=100 AND entry_to_exit_loss_cents>=20` | True | 8 (15.09%) | $-24.07 | $7.75 | 6/2 | $-8.72/$-12.00/$-3.35 | 3/5/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND exit_sigma_t_dollars>=50` | True | 9 (16.98%) | $-24.64 | $7.18 | 8/1 | $-6.28/$-16.51/$-1.85 | 5/2/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 26 (49.06%) | $-24.65 | $7.17 | 18/8 | $-6.13/$-15.61/$-2.91 | 16/3/7 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-24.74 | $7.08 | 7/0 | $-6.28/$-16.61/$-1.85 | 5/0/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-24.79 | $7.03 | 5/0 | $-10.27/$-11.17/$-3.35 | 2/3/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-25.21 | $6.61 | 11/3 | $-7.99/$-16.17/$-1.05 | 7/4/3 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.26 | $6.56 | 8/2 | $-7.86/$-15.55/$-1.85 | 7/1/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-25.37 | $6.45 | 4/2 | $-8.88/$-13.14/$-3.35 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-25.44 | $6.38 | 7/1 | $-10.21/$-14.91/$-0.32 | 2/2/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.64 | $6.18 | 8/2 | $-7.28/$-16.51/$-1.85 | 6/2/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-25.73 | $6.09 | 10/5 | $-8.91/$-13.47/$-3.35 | 8/7/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-26.08 | $5.74 | 7/3 | $-10.14/$-13.36/$-2.58 | 2/7/1 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND entry_to_exit_loss_cents>=10` | True | 6 (11.32%) | $-26.10 | $5.72 | 5/1 | $-6.91/$-16.61/$-2.58 | 5/0/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-26.16 | $5.66 | 4/1 | $-11.86/$-10.95/$-3.35 | 0/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-26.26 | $5.56 | 3/0 | $-11.86/$-11.05/$-3.35 | 0/3/0 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` improves the branch by $12.47 while suppressing 17 hurtful and 6 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
