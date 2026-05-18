# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260511_021947Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-31.51
- Hold-to-settlement net for same entries: $-27.21
- Exit value added: $-4.30
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-11.48 | $-7.77 | $-3.71 | 15/11 |
| validation | 18 | $-16.89 | $-14.46 | $-2.43 | 7/11 |
| holdout | 9 | $-3.14 | $-4.98 | $1.84 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-19.55 | $11.96 | 17/6 | $-7.00/$-12.23/$-0.32 | 10/9/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-19.57 | $11.94 | 16/5 | $-7.00/$-12.25/$-0.32 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-20.83 | $10.68 | 14/5 | $-7.60/$-12.25/$-0.98 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-21.85 | $9.66 | 14/4 | $-7.98/$-13.55/$-0.32 | 9/5/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-22.84 | $8.67 | 15/4 | $-6.15/$-16.37/$-0.32 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-23.07 | $8.44 | 15/5 | $-7.00/$-15.75/$-0.32 | 10/6/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-23.38 | $8.13 | 13/3 | $-5.81/$-16.53/$-1.04 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-23.38 | $8.13 | 5/1 | $-8.57/$-11.67/$-3.14 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-23.53 | $7.98 | 13/5 | $-7.26/$-15.23/$-1.04 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-23.54 | $7.97 | 9/4 | $-10.84/$-11.02/$-1.68 | 5/6/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-24.42 | $7.09 | 5/0 | $-9.94/$-11.34/$-3.14 | 2/3/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND exit_sigma_t_dollars>=50` | True | 9 (16.98%) | $-24.55 | $6.96 | 8/1 | $-5.90/$-16.87/$-1.78 | 5/2/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-24.57 | $6.94 | 7/0 | $-5.90/$-16.89/$-1.78 | 5/0/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 26 (49.06%) | $-24.79 | $6.72 | 18/8 | $-5.99/$-15.89/$-2.91 | 16/3/7 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.09 | $6.42 | 8/2 | $-7.48/$-15.83/$-1.78 | 7/1/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-25.10 | $6.41 | 11/3 | $-7.73/$-16.39/$-0.98 | 7/4/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-25.29 | $6.22 | 4/2 | $-8.57/$-13.58/$-3.14 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-25.43 | $6.08 | 7/1 | $-9.83/$-15.28/$-0.32 | 2/2/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.55 | $5.96 | 8/2 | $-6.90/$-16.87/$-1.78 | 6/2/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-25.63 | $5.88 | 10/5 | $-8.65/$-13.84/$-3.14 | 8/7/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-25.88 | $5.63 | 4/1 | $-11.48/$-11.26/$-3.14 | 0/5/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND entry_to_exit_loss_cents>=10` | True | 6 (11.32%) | $-25.89 | $5.62 | 5/1 | $-6.56/$-16.89/$-2.44 | 5/0/1 |
| `suppress_collapse_exit_if_exit_btc_age_ms<=100 AND entry_to_exit_loss_cents>=20` | True | 9 (16.98%) | $-25.93 | $5.58 | 6/3 | $-10.62/$-12.17/$-3.14 | 4/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-26.11 | $5.40 | 3/0 | $-11.48/$-11.49/$-3.14 | 0/3/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-26.20 | $5.31 | 7/3 | $-9.76/$-14.00/$-2.44 | 2/7/1 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` improves the branch by $11.96 while suppressing 17 hurtful and 6 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
