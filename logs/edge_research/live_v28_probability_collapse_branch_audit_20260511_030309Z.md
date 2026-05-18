# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260511_030309Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-31.33
- Hold-to-settlement net for same entries: $-26.77
- Exit value added: $-4.56
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-11.78 | $-7.77 | $-4.01 | 15/11 |
| validation | 18 | $-16.25 | $-14.00 | $-2.25 | 7/11 |
| holdout | 9 | $-3.30 | $-5.00 | $1.70 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-18.89 | $12.44 | 17/6 | $-7.21/$-11.41/$-0.27 | 10/9/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-18.99 | $12.34 | 16/5 | $-7.21/$-11.51/$-0.27 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-20.32 | $11.01 | 14/5 | $-7.81/$-11.51/$-1.00 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-21.34 | $9.99 | 14/4 | $-8.19/$-12.88/$-0.27 | 9/5/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-22.34 | $8.99 | 15/4 | $-6.36/$-15.71/$-0.27 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-22.44 | $8.89 | 15/5 | $-7.21/$-14.96/$-0.27 | 10/6/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-22.66 | $8.67 | 13/3 | $-6.07/$-15.60/$-0.99 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-22.74 | $8.59 | 13/5 | $-7.52/$-14.23/$-0.99 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-22.97 | $8.36 | 5/1 | $-8.80/$-10.87/$-3.30 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-23.14 | $8.19 | 9/4 | $-11.09/$-10.28/$-1.77 | 5/6/2 |
| `suppress_collapse_exit_if_exit_btc_age_ms<=100 AND entry_to_exit_loss_cents>=20` | True | 8 (15.09%) | $-23.58 | $7.75 | 6/2 | $-8.64/$-11.64/$-3.30 | 3/5/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND exit_sigma_t_dollars>=50` | True | 9 (16.98%) | $-24.15 | $7.18 | 8/1 | $-6.20/$-16.15/$-1.80 | 5/2/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-24.25 | $7.08 | 7/0 | $-6.20/$-16.25/$-1.80 | 5/0/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-24.30 | $7.03 | 5/0 | $-10.19/$-10.81/$-3.30 | 2/3/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 26 (49.06%) | $-24.62 | $6.71 | 18/8 | $-6.15/$-15.54/$-2.93 | 16/3/7 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-24.75 | $6.58 | 11/3 | $-7.94/$-15.81/$-1.00 | 7/4/3 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-24.77 | $6.56 | 8/2 | $-7.78/$-15.19/$-1.80 | 7/1/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-24.88 | $6.45 | 4/2 | $-8.80/$-12.78/$-3.30 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-24.98 | $6.35 | 7/1 | $-10.16/$-14.55/$-0.27 | 2/2/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.15 | $6.18 | 8/2 | $-7.20/$-16.15/$-1.80 | 6/2/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-25.24 | $6.09 | 10/5 | $-8.83/$-13.11/$-3.30 | 8/7/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-25.59 | $5.74 | 7/3 | $-10.06/$-13.00/$-2.53 | 2/7/1 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND entry_to_exit_loss_cents>=10` | True | 6 (11.32%) | $-25.61 | $5.72 | 5/1 | $-6.83/$-16.25/$-2.53 | 5/0/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-25.67 | $5.66 | 4/1 | $-11.78/$-10.59/$-3.30 | 0/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-25.77 | $5.56 | 3/0 | $-11.78/$-10.69/$-3.30 | 0/3/0 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` improves the branch by $12.44 while suppressing 17 hurtful and 6 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
