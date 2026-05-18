# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260511_031612Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-31.29
- Hold-to-settlement net for same entries: $-26.71
- Exit value added: $-4.58
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-11.36 | $-7.77 | $-3.59 | 15/11 |
| validation | 18 | $-16.65 | $-13.96 | $-2.69 | 7/11 |
| holdout | 9 | $-3.28 | $-4.98 | $1.70 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-18.74 | $12.55 | 17/6 | $-6.84/$-11.65/$-0.25 | 10/9/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-18.76 | $12.53 | 16/5 | $-6.84/$-11.67/$-0.25 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-20.09 | $11.20 | 14/5 | $-7.44/$-11.67/$-0.98 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-21.17 | $10.12 | 14/4 | $-7.82/$-13.10/$-0.25 | 9/5/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-22.18 | $9.11 | 15/4 | $-5.92/$-16.01/$-0.25 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-22.47 | $8.82 | 15/5 | $-6.84/$-15.38/$-0.25 | 10/6/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-22.70 | $8.59 | 13/3 | $-5.65/$-16.08/$-0.97 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-22.79 | $8.50 | 13/5 | $-7.17/$-14.65/$-0.97 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-22.84 | $8.45 | 9/4 | $-10.65/$-10.44/$-1.75 | 5/6/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-23.08 | $8.21 | 5/1 | $-8.45/$-11.35/$-3.28 | 2/4/0 |
| `suppress_collapse_exit_if_exit_btc_age_ms<=100 AND entry_to_exit_loss_cents>=20` | True | 8 (15.09%) | $-23.58 | $7.71 | 6/2 | $-8.34/$-11.96/$-3.28 | 3/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-24.06 | $7.23 | 5/0 | $-9.75/$-11.03/$-3.28 | 2/3/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND exit_sigma_t_dollars>=50` | True | 9 (16.98%) | $-24.26 | $7.03 | 8/1 | $-5.85/$-16.63/$-1.78 | 5/2/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-24.28 | $7.01 | 7/0 | $-5.85/$-16.65/$-1.78 | 5/0/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-24.51 | $6.78 | 11/3 | $-7.50/$-16.03/$-0.98 | 7/4/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 26 (49.06%) | $-24.60 | $6.69 | 18/8 | $-6.04/$-15.65/$-2.91 | 16/3/7 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-24.88 | $6.41 | 8/2 | $-7.43/$-15.67/$-1.78 | 7/1/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-24.94 | $6.35 | 7/1 | $-9.74/$-14.95/$-0.25 | 2/2/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-25.06 | $6.23 | 4/2 | $-8.45/$-13.33/$-3.28 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-25.09 | $6.20 | 10/5 | $-8.46/$-13.35/$-3.28 | 8/7/0 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.26 | $6.03 | 8/2 | $-6.85/$-16.63/$-1.78 | 6/2/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-25.50 | $5.79 | 7/3 | $-9.57/$-13.42/$-2.51 | 2/7/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-25.53 | $5.76 | 4/1 | $-11.36/$-10.89/$-3.28 | 0/5/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND entry_to_exit_loss_cents>=10` | True | 6 (11.32%) | $-25.67 | $5.62 | 5/1 | $-6.51/$-16.65/$-2.51 | 5/0/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-25.81 | $5.48 | 3/0 | $-11.36/$-11.17/$-3.28 | 0/3/0 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` improves the branch by $12.55 while suppressing 17 hurtful and 6 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
