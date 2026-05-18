# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260511_023629Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-31.71
- Hold-to-settlement net for same entries: $-27.09
- Exit value added: $-4.62
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-11.75 | $-8.15 | $-3.60 | 15/11 |
| validation | 18 | $-16.69 | $-13.96 | $-2.73 | 7/11 |
| holdout | 9 | $-3.27 | $-4.98 | $1.71 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-18.93 | $12.78 | 17/6 | $-7.08/$-11.61/$-0.24 | 10/9/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-19.03 | $12.68 | 16/5 | $-7.08/$-11.71/$-0.24 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-20.36 | $11.35 | 14/5 | $-7.68/$-11.71/$-0.97 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-21.44 | $10.27 | 14/4 | $-8.06/$-13.14/$-0.24 | 9/5/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-22.44 | $9.27 | 15/4 | $-6.23/$-15.97/$-0.24 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-22.66 | $9.05 | 15/5 | $-7.08/$-15.34/$-0.24 | 10/6/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-23.01 | $8.70 | 13/3 | $-6.01/$-16.04/$-0.96 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-23.03 | $8.68 | 13/5 | $-7.46/$-14.61/$-0.96 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-23.14 | $8.57 | 9/4 | $-10.92/$-10.48/$-1.74 | 5/6/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-23.42 | $8.29 | 5/1 | $-8.84/$-11.31/$-3.27 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-24.43 | $7.28 | 5/0 | $-10.09/$-11.07/$-3.27 | 2/3/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND exit_sigma_t_dollars>=50` | True | 9 (16.98%) | $-24.53 | $7.18 | 8/1 | $-6.17/$-16.59/$-1.77 | 5/2/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-24.63 | $7.08 | 7/0 | $-6.17/$-16.69/$-1.77 | 5/0/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 26 (49.06%) | $-24.68 | $7.03 | 18/8 | $-6.16/$-15.69/$-2.83 | 16/3/7 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-24.85 | $6.86 | 11/3 | $-7.81/$-16.07/$-0.97 | 7/4/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-25.31 | $6.40 | 10/5 | $-8.73/$-13.31/$-3.27 | 8/7/0 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.31 | $6.40 | 8/2 | $-7.91/$-15.63/$-1.77 | 7/1/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-25.33 | $6.38 | 7/1 | $-10.10/$-14.99/$-0.24 | 2/2/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-25.38 | $6.33 | 4/2 | $-8.84/$-13.27/$-3.27 | 2/4/0 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.61 | $6.10 | 8/2 | $-7.25/$-16.59/$-1.77 | 6/2/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-25.84 | $5.87 | 7/3 | $-9.96/$-13.38/$-2.50 | 2/7/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-25.87 | $5.84 | 4/1 | $-11.75/$-10.85/$-3.27 | 0/5/0 |
| `suppress_collapse_exit_if_exit_btc_age_ms<=100 AND entry_to_exit_loss_cents>=20` | True | 9 (16.98%) | $-26.08 | $5.63 | 6/3 | $-10.84/$-11.97/$-3.27 | 4/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-26.15 | $5.56 | 3/0 | $-11.75/$-11.13/$-3.27 | 0/3/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=4 AND exit_sigma_t_dollars>=50` | True | 7 (13.21%) | $-26.28 | $5.43 | 6/1 | $-7.15/$-16.59/$-2.54 | 4/2/1 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` improves the branch by $12.78 while suppressing 17 hurtful and 6 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
