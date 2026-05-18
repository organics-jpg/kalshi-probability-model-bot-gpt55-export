# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260511_034230Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-31.28
- Hold-to-settlement net for same entries: $-26.73
- Exit value added: $-4.55
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-11.80 | $-7.77 | $-4.03 | 15/11 |
| validation | 18 | $-16.20 | $-13.98 | $-2.22 | 7/11 |
| holdout | 9 | $-3.28 | $-4.98 | $1.70 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-18.77 | $12.51 | 17/6 | $-7.14/$-11.38/$-0.25 | 10/9/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-18.79 | $12.49 | 16/5 | $-7.14/$-11.40/$-0.25 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-20.12 | $11.16 | 14/5 | $-7.74/$-11.40/$-0.98 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-21.12 | $10.16 | 14/4 | $-8.04/$-12.83/$-0.25 | 9/5/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-22.28 | $9.00 | 15/4 | $-6.29/$-15.74/$-0.25 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-22.32 | $8.96 | 15/5 | $-7.14/$-14.93/$-0.25 | 10/6/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-22.67 | $8.61 | 13/3 | $-6.07/$-15.63/$-0.97 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-22.69 | $8.59 | 13/5 | $-7.52/$-14.20/$-0.97 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-22.89 | $8.39 | 9/4 | $-10.97/$-10.17/$-1.75 | 5/6/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-23.00 | $8.28 | 5/1 | $-8.82/$-10.90/$-3.28 | 2/4/0 |
| `suppress_collapse_exit_if_exit_btc_age_ms<=100 AND entry_to_exit_loss_cents>=20` | True | 8 (15.09%) | $-23.63 | $7.65 | 6/2 | $-8.66/$-11.69/$-3.28 | 3/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-24.18 | $7.10 | 5/0 | $-10.14/$-10.76/$-3.28 | 2/3/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND exit_sigma_t_dollars>=50` | True | 9 (16.98%) | $-24.26 | $7.02 | 8/1 | $-6.30/$-16.18/$-1.78 | 5/2/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-24.28 | $7.00 | 7/0 | $-6.30/$-16.20/$-1.78 | 5/0/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 26 (49.06%) | $-24.48 | $6.80 | 18/8 | $-6.15/$-15.42/$-2.91 | 16/3/7 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-24.53 | $6.75 | 11/3 | $-7.79/$-15.76/$-0.98 | 7/4/3 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-24.88 | $6.40 | 8/2 | $-7.88/$-15.22/$-1.78 | 7/1/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-24.98 | $6.30 | 7/1 | $-10.23/$-14.50/$-0.25 | 2/2/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-24.98 | $6.30 | 4/2 | $-8.82/$-12.88/$-3.28 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-25.07 | $6.21 | 10/5 | $-8.71/$-13.08/$-3.28 | 8/7/0 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.26 | $6.02 | 8/2 | $-7.30/$-16.18/$-1.78 | 6/2/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-25.57 | $5.71 | 7/3 | $-10.09/$-12.97/$-2.51 | 2/7/1 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND entry_to_exit_loss_cents>=10` | True | 6 (11.32%) | $-25.64 | $5.64 | 5/1 | $-6.93/$-16.20/$-2.51 | 5/0/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-25.70 | $5.58 | 4/1 | $-11.80/$-10.62/$-3.28 | 0/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-25.80 | $5.48 | 3/0 | $-11.80/$-10.72/$-3.28 | 0/3/0 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` improves the branch by $12.51 while suppressing 17 hurtful and 6 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
