# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260511_010414Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-32.41
- Hold-to-settlement net for same entries: $-27.15
- Exit value added: $-5.26
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-11.97 | $-7.75 | $-4.22 | 15/11 |
| validation | 18 | $-16.83 | $-13.96 | $-2.87 | 7/11 |
| holdout | 9 | $-3.61 | $-5.44 | $1.83 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-19.62 | $12.79 | 17/6 | $-7.23/$-11.75/$-0.64 | 10/9/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-19.72 | $12.69 | 16/5 | $-7.23/$-11.85/$-0.64 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-21.05 | $11.36 | 14/5 | $-7.83/$-11.85/$-1.37 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-22.13 | $10.28 | 14/4 | $-8.21/$-13.28/$-0.64 | 9/5/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-23.13 | $9.28 | 15/4 | $-6.38/$-16.11/$-0.64 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-23.35 | $9.06 | 15/5 | $-7.23/$-15.48/$-0.64 | 10/6/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-23.64 | $8.77 | 13/3 | $-6.16/$-16.18/$-1.30 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-23.66 | $8.75 | 13/5 | $-7.61/$-14.75/$-1.30 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-23.90 | $8.51 | 9/4 | $-11.14/$-10.62/$-2.14 | 5/6/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-24.05 | $8.36 | 5/1 | $-8.99/$-11.45/$-3.61 | 2/4/0 |
| `suppress_collapse_exit_if_exit_btc_age_ms<=100 AND entry_to_exit_loss_cents>=20` | True | 8 (15.09%) | $-24.48 | $7.93 | 6/2 | $-8.83/$-12.04/$-3.61 | 3/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-25.13 | $7.28 | 5/0 | $-10.31/$-11.21/$-3.61 | 2/3/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND exit_sigma_t_dollars>=50` | True | 9 (16.98%) | $-25.23 | $7.18 | 8/1 | $-6.39/$-16.73/$-2.11 | 5/2/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 26 (49.06%) | $-25.30 | $7.11 | 18/8 | $-6.10/$-15.83/$-3.37 | 16/3/7 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-25.33 | $7.08 | 7/0 | $-6.39/$-16.83/$-2.11 | 5/0/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-25.54 | $6.87 | 11/3 | $-7.96/$-16.21/$-1.37 | 7/4/3 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.85 | $6.56 | 8/2 | $-7.97/$-15.77/$-2.11 | 7/1/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-25.94 | $6.47 | 10/5 | $-8.88/$-13.45/$-3.61 | 8/7/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-26.01 | $6.40 | 4/2 | $-8.99/$-13.41/$-3.61 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-26.09 | $6.32 | 7/1 | $-10.32/$-15.13/$-0.64 | 2/2/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-26.23 | $6.18 | 8/2 | $-7.39/$-16.73/$-2.11 | 6/2/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-26.54 | $5.87 | 7/3 | $-10.18/$-13.52/$-2.84 | 2/7/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-26.57 | $5.84 | 4/1 | $-11.97/$-10.99/$-3.61 | 0/5/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND entry_to_exit_loss_cents>=10` | True | 6 (11.32%) | $-26.72 | $5.69 | 5/1 | $-7.05/$-16.83/$-2.84 | 5/0/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-26.85 | $5.56 | 3/0 | $-11.97/$-11.27/$-3.61 | 0/3/0 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` improves the branch by $12.79 while suppressing 17 hurtful and 6 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
