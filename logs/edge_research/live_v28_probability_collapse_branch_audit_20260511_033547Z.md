# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260511_033547Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-32.15
- Hold-to-settlement net for same entries: $-27.13
- Exit value added: $-5.02
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-12.04 | $-8.11 | $-3.93 | 15/11 |
| validation | 18 | $-16.77 | $-13.98 | $-2.79 | 7/11 |
| holdout | 9 | $-3.34 | $-5.04 | $1.70 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-19.44 | $12.71 | 17/6 | $-7.38/$-11.75/$-0.31 | 10/9/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-19.54 | $12.61 | 16/5 | $-7.38/$-11.85/$-0.31 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-20.87 | $11.28 | 14/5 | $-7.98/$-11.85/$-1.04 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-21.81 | $10.34 | 14/4 | $-8.28/$-13.22/$-0.31 | 9/5/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-22.89 | $9.26 | 15/4 | $-6.53/$-16.05/$-0.31 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-23.17 | $8.98 | 15/5 | $-7.38/$-15.48/$-0.31 | 10/6/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-23.46 | $8.69 | 13/3 | $-6.31/$-16.12/$-1.03 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-23.54 | $8.61 | 13/5 | $-7.76/$-14.75/$-1.03 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-23.64 | $8.51 | 9/4 | $-11.21/$-10.62/$-1.81 | 5/6/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-23.79 | $8.36 | 5/1 | $-9.06/$-11.39/$-3.34 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-24.87 | $7.28 | 5/0 | $-10.38/$-11.15/$-3.34 | 2/3/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 26 (49.06%) | $-24.92 | $7.23 | 18/8 | $-6.25/$-15.77/$-2.90 | 16/3/7 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND exit_sigma_t_dollars>=50` | True | 9 (16.98%) | $-25.05 | $7.10 | 8/1 | $-6.54/$-16.67/$-1.84 | 5/2/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-25.15 | $7.00 | 7/0 | $-6.54/$-16.77/$-1.84 | 5/0/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-25.22 | $6.93 | 11/3 | $-8.03/$-16.15/$-1.04 | 7/4/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-25.70 | $6.45 | 4/2 | $-9.06/$-13.30/$-3.34 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-25.74 | $6.41 | 10/5 | $-8.95/$-13.45/$-3.34 | 8/7/0 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.83 | $6.32 | 8/2 | $-8.28/$-15.71/$-1.84 | 7/1/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-25.85 | $6.30 | 7/1 | $-10.47/$-15.07/$-0.31 | 2/2/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-26.13 | $6.02 | 8/2 | $-7.62/$-16.67/$-1.84 | 6/2/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-26.31 | $5.84 | 4/1 | $-12.04/$-10.93/$-3.34 | 0/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-26.42 | $5.73 | 7/3 | $-10.33/$-13.52/$-2.57 | 2/7/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-26.59 | $5.56 | 3/0 | $-12.04/$-11.21/$-3.34 | 0/3/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=4 AND exit_sigma_t_dollars>=50` | True | 7 (13.21%) | $-26.72 | $5.43 | 6/1 | $-7.44/$-16.67/$-2.61 | 4/2/1 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=4` | True | 5 (9.43%) | $-26.82 | $5.33 | 5/0 | $-7.44/$-16.77/$-2.61 | 4/0/1 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` improves the branch by $12.71 while suppressing 17 hurtful and 6 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
