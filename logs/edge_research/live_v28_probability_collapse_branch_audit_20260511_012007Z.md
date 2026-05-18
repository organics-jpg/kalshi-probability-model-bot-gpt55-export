# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260511_012007Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-32.42
- Hold-to-settlement net for same entries: $-27.53
- Exit value added: $-4.89
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-11.87 | $-8.13 | $-3.74 | 15/11 |
| validation | 18 | $-16.81 | $-13.96 | $-2.85 | 7/11 |
| holdout | 9 | $-3.74 | $-5.44 | $1.70 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-19.71 | $12.71 | 17/6 | $-7.20/$-11.80/$-0.71 | 10/9/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-19.81 | $12.61 | 16/5 | $-7.20/$-11.90/$-0.71 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-21.14 | $11.28 | 14/5 | $-7.80/$-11.90/$-1.44 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-22.22 | $10.20 | 14/4 | $-8.18/$-13.33/$-0.71 | 9/5/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-23.22 | $9.20 | 15/4 | $-6.35/$-16.16/$-0.71 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-23.44 | $8.98 | 15/5 | $-7.20/$-15.53/$-0.71 | 10/6/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-23.79 | $8.63 | 13/3 | $-6.13/$-16.23/$-1.43 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-23.81 | $8.61 | 13/5 | $-7.58/$-14.80/$-1.43 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-23.92 | $8.50 | 9/4 | $-11.11/$-10.60/$-2.21 | 5/6/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-24.06 | $8.36 | 5/1 | $-8.89/$-11.43/$-3.74 | 2/4/0 |
| `suppress_collapse_exit_if_exit_btc_age_ms<=100 AND entry_to_exit_loss_cents>=20` | True | 8 (15.09%) | $-24.49 | $7.93 | 6/2 | $-8.73/$-12.02/$-3.74 | 3/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-25.21 | $7.21 | 5/0 | $-10.28/$-11.19/$-3.74 | 2/3/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND exit_sigma_t_dollars>=50` | True | 9 (16.98%) | $-25.24 | $7.18 | 8/1 | $-6.29/$-16.71/$-2.24 | 5/2/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-25.34 | $7.08 | 7/0 | $-6.29/$-16.81/$-2.24 | 5/0/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 26 (49.06%) | $-25.37 | $7.05 | 18/8 | $-6.12/$-15.88/$-3.37 | 16/3/7 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-25.63 | $6.79 | 11/3 | $-7.93/$-16.26/$-1.44 | 7/4/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-25.97 | $6.45 | 4/2 | $-8.89/$-13.34/$-3.74 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-26.02 | $6.40 | 10/5 | $-8.85/$-13.43/$-3.74 | 8/7/0 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-26.02 | $6.40 | 8/2 | $-8.03/$-15.75/$-2.24 | 7/1/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-26.11 | $6.31 | 7/1 | $-10.22/$-15.18/$-0.71 | 2/2/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-26.32 | $6.10 | 8/2 | $-7.37/$-16.71/$-2.24 | 6/2/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-26.58 | $5.84 | 4/1 | $-11.87/$-10.97/$-3.74 | 0/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-26.62 | $5.80 | 7/3 | $-10.15/$-13.50/$-2.97 | 2/7/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-26.86 | $5.56 | 3/0 | $-11.87/$-11.25/$-3.74 | 0/3/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=4 AND exit_sigma_t_dollars>=50` | True | 7 (13.21%) | $-26.99 | $5.43 | 6/1 | $-7.27/$-16.71/$-3.01 | 4/2/1 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` improves the branch by $12.71 while suppressing 17 hurtful and 6 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
