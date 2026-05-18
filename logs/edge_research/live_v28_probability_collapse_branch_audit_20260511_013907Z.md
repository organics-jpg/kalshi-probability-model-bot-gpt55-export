# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260511_013907Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-32.19
- Hold-to-settlement net for same entries: $-27.07
- Exit value added: $-5.12
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-12.08 | $-8.11 | $-3.97 | 15/11 |
| validation | 18 | $-16.76 | $-13.98 | $-2.78 | 7/11 |
| holdout | 9 | $-3.35 | $-4.98 | $1.63 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-19.45 | $12.74 | 17/6 | $-7.38/$-11.75/$-0.32 | 10/9/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-19.55 | $12.64 | 16/5 | $-7.38/$-11.85/$-0.32 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-20.84 | $11.35 | 14/5 | $-7.94/$-11.85/$-1.05 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-21.89 | $10.30 | 14/4 | $-8.36/$-13.21/$-0.32 | 9/5/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-22.89 | $9.30 | 15/4 | $-6.53/$-16.04/$-0.32 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-23.18 | $9.01 | 15/5 | $-7.38/$-15.48/$-0.32 | 10/6/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-23.46 | $8.73 | 13/3 | $-6.31/$-16.11/$-1.04 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-23.51 | $8.68 | 13/5 | $-7.72/$-14.75/$-1.04 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-23.69 | $8.50 | 9/4 | $-11.25/$-10.62/$-1.82 | 5/6/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-23.90 | $8.29 | 5/1 | $-9.10/$-11.45/$-3.35 | 2/4/0 |
| `suppress_collapse_exit_if_exit_btc_age_ms<=100 AND entry_to_exit_loss_cents>=20` | True | 8 (15.09%) | $-24.33 | $7.86 | 6/2 | $-8.94/$-12.04/$-3.35 | 3/5/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 26 (49.06%) | $-24.92 | $7.27 | 18/8 | $-6.25/$-15.76/$-2.91 | 16/3/7 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-24.98 | $7.21 | 5/0 | $-10.42/$-11.21/$-3.35 | 2/3/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND exit_sigma_t_dollars>=50` | True | 9 (16.98%) | $-25.05 | $7.14 | 8/1 | $-6.54/$-16.66/$-1.85 | 5/2/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-25.15 | $7.04 | 7/0 | $-6.54/$-16.76/$-1.85 | 5/0/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-25.26 | $6.93 | 11/3 | $-8.07/$-16.14/$-1.05 | 7/4/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-25.81 | $6.38 | 7/1 | $-10.43/$-15.06/$-0.32 | 2/2/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-25.81 | $6.38 | 4/2 | $-9.10/$-13.36/$-3.35 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-25.83 | $6.36 | 10/5 | $-9.03/$-13.45/$-3.35 | 8/7/0 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.83 | $6.36 | 8/2 | $-8.28/$-15.70/$-1.85 | 7/1/2 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-26.13 | $6.06 | 8/2 | $-7.62/$-16.66/$-1.85 | 6/2/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-26.35 | $5.84 | 4/1 | $-12.08/$-10.92/$-3.35 | 0/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-26.39 | $5.80 | 7/3 | $-10.29/$-13.52/$-2.58 | 2/7/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-26.70 | $5.49 | 3/0 | $-12.08/$-11.27/$-3.35 | 0/3/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=4 AND exit_sigma_t_dollars>=50` | True | 7 (13.21%) | $-26.80 | $5.39 | 6/1 | $-7.52/$-16.66/$-2.62 | 4/2/1 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` improves the branch by $12.74 while suppressing 17 hurtful and 6 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
