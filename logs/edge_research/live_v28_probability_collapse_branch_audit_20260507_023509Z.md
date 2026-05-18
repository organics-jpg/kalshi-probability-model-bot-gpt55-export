# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260507_023509Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 63
- Actual collapse-exit net: $-38.26
- Hold-to-settlement net for same entries: $-33.62
- Exit value added: $-4.64
- Hurtful/helpful exits: 30 / 33

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 35 | $-18.50 | $-18.16 | $-0.34 | 18/17 |
| validation | 14 | $-13.50 | $-7.20 | $-6.30 | 6/8 |
| holdout | 14 | $-6.26 | $-8.26 | $2.00 | 6/8 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 25 (39.68%) | $-21.74 | $16.52 | 18/7 | $-15.84/$-3.76/$-2.14 | 15/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 28 (44.44%) | $-22.84 | $15.42 | 19/9 | $-14.86/$-3.76/$-4.22 | 16/6/6 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 22 (34.92%) | $-23.62 | $14.64 | 15/7 | $-16.40/$-3.76/$-3.46 | 14/6/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=5` | True | 26 (41.27%) | $-24.76 | $13.50 | 16/10 | $-8.78/$-10.72/$-5.26 | 12/6/8 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 15 (23.81%) | $-24.78 | $13.48 | 10/5 | $-16.86/$-3.76/$-4.16 | 8/6/1 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=5` | True | 24 (38.10%) | $-25.04 | $13.22 | 15/9 | $-11.14/$-10.72/$-3.18 | 12/6/6 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 7 (11.11%) | $-25.60 | $12.66 | 7/0 | $-15.98/$-3.36/$-6.26 | 3/4/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=15 AND exit_sigma_t_dollars>=75` | True | 11 (17.46%) | $-25.96 | $12.30 | 7/4 | $-15.94/$-3.76/$-6.26 | 5/6/0 |
| `suppress_collapse_exit_if_position_seconds<=45 AND fair_minus_exit_bid_cents>=5` | True | 15 (23.81%) | $-26.28 | $11.98 | 12/3 | $-12.84/$-10.50/$-2.94 | 8/1/6 |
| `suppress_collapse_exit_if_entry_to_exit_loss_cents>=10 AND fair_minus_exit_bid_cents>=5` | True | 30 (47.62%) | $-26.46 | $11.80 | 16/14 | $-12.56/$-10.72/$-3.18 | 18/6/6 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 20 (31.75%) | $-26.74 | $11.52 | 15/5 | $-16.74/$-7.86/$-2.14 | 14/2/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 29 (46.03%) | $-27.22 | $11.04 | 21/8 | $-16.34/$-9.22/$-1.66 | 18/3/8 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 7 (11.11%) | $-27.42 | $10.84 | 6/1 | $-12.16/$-9.00/$-6.26 | 5/2/0 |
| `suppress_collapse_exit_if_position_seconds<=180 AND fair_minus_exit_bid_cents>=5` | True | 29 (46.03%) | $-27.44 | $10.82 | 16/13 | $-11.46/$-10.72/$-5.26 | 15/6/8 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=90` | True | 35 (55.56%) | $-27.78 | $10.48 | 23/12 | $-15.68/$-8.12/$-3.98 | 19/6/10 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=20 AND exit_btc_age_ms<=100` | True | 7 (11.11%) | $-28.12 | $10.14 | 5/2 | $-17.70/$-4.16/$-6.26 | 1/6/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=20` | True | 12 (19.05%) | $-28.28 | $9.98 | 7/5 | $-18.26/$-3.76/$-6.26 | 6/6/0 |
| `suppress_collapse_exit_if_position_seconds<=90 AND fair_minus_exit_bid_cents>=5` | True | 21 (33.33%) | $-28.32 | $9.94 | 13/8 | $-13.66/$-9.40/$-5.26 | 9/4/8 |
| `suppress_collapse_exit_if_position_seconds<=45 AND fair_minus_exit_bid_cents>=0` | True | 31 (49.21%) | $-28.54 | $9.72 | 20/11 | $-14.78/$-10.02/$-3.74 | 16/5/10 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 23 (36.51%) | $-28.70 | $9.56 | 15/8 | $-15.08/$-9.40/$-4.22 | 13/4/6 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 22 (34.92%) | $-28.86 | $9.40 | 16/6 | $-16.78/$-7.86/$-4.22 | 14/2/6 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 9 (14.29%) | $-28.98 | $9.28 | 9/0 | $-13.34/$-13.50/$-2.14 | 5/0/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 24 (38.10%) | $-29.00 | $9.26 | 16/8 | $-15.38/$-9.40/$-4.22 | 14/4/6 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=180` | True | 42 (66.67%) | $-29.10 | $9.16 | 25/17 | $-13.48/$-9.44/$-6.18 | 22/8/12 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 14 (22.22%) | $-29.32 | $8.94 | 9/5 | $-14.38/$-9.40/$-5.54 | 6/4/4 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` improves the branch by $16.52 while suppressing 18 hurtful and 7 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
