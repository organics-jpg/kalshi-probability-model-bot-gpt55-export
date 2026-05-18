# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260507_022909Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 61
- Actual collapse-exit net: $-37.10
- Hold-to-settlement net for same entries: $-30.34
- Exit value added: $-6.76
- Hurtful/helpful exits: 30 / 31

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 35 | $-18.50 | $-18.16 | $-0.34 | 18/17 |
| validation | 12 | $-11.30 | $-4.60 | $-6.70 | 6/6 |
| holdout | 14 | $-7.30 | $-7.58 | $0.28 | 6/8 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 25 (40.98%) | $-20.58 | $16.52 | 18/7 | $-15.84/$-1.16/$-3.58 | 15/4/6 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 28 (45.90%) | $-21.68 | $15.42 | 19/9 | $-14.86/$-1.16/$-5.66 | 16/4/8 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 22 (36.07%) | $-22.46 | $14.64 | 15/7 | $-16.40/$-1.16/$-4.90 | 14/4/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=5` | True | 26 (42.62%) | $-23.60 | $13.50 | 16/10 | $-8.78/$-8.12/$-6.70 | 12/4/10 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 15 (24.59%) | $-23.62 | $13.48 | 10/5 | $-16.86/$-1.16/$-5.60 | 8/4/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=5` | True | 24 (39.34%) | $-23.88 | $13.22 | 15/9 | $-11.14/$-8.12/$-4.62 | 12/4/8 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 27 (44.26%) | $-23.94 | $13.16 | 21/6 | $-16.34/$-7.02/$-0.58 | 18/3/6 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 7 (11.48%) | $-24.44 | $12.66 | 7/0 | $-15.98/$-1.16/$-7.30 | 3/4/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=90` | True | 33 (54.10%) | $-24.50 | $12.60 | 23/10 | $-15.68/$-5.52/$-3.30 | 19/4/10 |
| `suppress_collapse_exit_if_position_seconds<=45 AND fair_minus_exit_bid_cents>=5` | True | 15 (24.59%) | $-25.12 | $11.98 | 12/3 | $-12.84/$-8.30/$-3.98 | 8/1/6 |
| `suppress_collapse_exit_if_position_seconds<=45 AND fair_minus_exit_bid_cents>=0` | True | 29 (47.54%) | $-25.26 | $11.84 | 20/9 | $-14.78/$-7.82/$-2.66 | 16/5/8 |
| `suppress_collapse_exit_if_entry_to_exit_loss_cents>=10 AND fair_minus_exit_bid_cents>=5` | True | 30 (49.18%) | $-25.30 | $11.80 | 16/14 | $-12.56/$-8.12/$-4.62 | 18/4/8 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 20 (32.79%) | $-25.58 | $11.52 | 15/5 | $-16.74/$-5.66/$-3.18 | 14/2/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_p_hold<=0.6` | True | 16 (26.23%) | $-25.68 | $11.42 | 9/7 | $-18.10/$-2.48/$-5.10 | 6/6/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=180` | True | 40 (65.57%) | $-25.82 | $11.28 | 25/15 | $-13.48/$-6.84/$-5.50 | 22/6/12 |
| `suppress_collapse_exit_if_position_seconds<=45 AND entry_to_exit_loss_cents>=10` | True | 28 (45.90%) | $-26.20 | $10.90 | 19/9 | $-16.48/$-7.82/$-1.90 | 19/5/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 7 (11.48%) | $-26.26 | $10.84 | 6/1 | $-12.16/$-6.80/$-7.30 | 5/2/0 |
| `suppress_collapse_exit_if_position_seconds<=180 AND fair_minus_exit_bid_cents>=5` | True | 29 (47.54%) | $-26.28 | $10.82 | 16/13 | $-11.46/$-8.12/$-6.70 | 15/4/10 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND position_seconds<=45` | True | 31 (50.82%) | $-26.38 | $10.72 | 21/10 | $-15.90/$-7.82/$-2.66 | 18/5/8 |
| `suppress_collapse_exit_if_position_seconds<=90 AND fair_minus_exit_bid_cents>=0` | True | 36 (59.02%) | $-26.64 | $10.46 | 22/14 | $-14.94/$-6.32/$-5.38 | 18/6/12 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND position_seconds<=90` | True | 37 (60.66%) | $-26.94 | $10.16 | 23/14 | $-15.24/$-6.32/$-5.38 | 19/6/12 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=20 AND exit_btc_age_ms<=100` | True | 7 (11.48%) | $-26.96 | $10.14 | 5/2 | $-17.70/$-1.96/$-7.30 | 1/6/0 |
| `suppress_collapse_exit_if_position_seconds<=90 AND fair_minus_exit_bid_cents>=5` | True | 21 (34.43%) | $-27.16 | $9.94 | 13/8 | $-13.66/$-6.80/$-6.70 | 9/2/10 |
| `suppress_collapse_exit_if_position_seconds<=45` | True | 34 (55.74%) | $-27.48 | $9.62 | 22/12 | $-17.00/$-7.82/$-2.66 | 21/5/8 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 23 (37.70%) | $-27.54 | $9.56 | 15/8 | $-15.08/$-6.80/$-5.66 | 13/2/8 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` improves the branch by $16.52 while suppressing 18 hurtful and 7 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
