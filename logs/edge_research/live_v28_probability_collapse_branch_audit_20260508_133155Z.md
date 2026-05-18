# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260508_133155Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-29.16
- Hold-to-settlement net for same entries: $-28.22
- Exit value added: $-0.94
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-10.10 | $-8.22 | $-1.88 | 15/11 |
| validation | 18 | $-15.80 | $-14.48 | $-1.32 | 7/11 |
| holdout | 9 | $-3.26 | $-5.52 | $2.26 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-18.32 | $10.84 | 16/5 | $-6.34/$-11.48/$-0.50 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-18.38 | $10.78 | 17/6 | $-6.34/$-11.54/$-0.50 | 10/9/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-19.54 | $9.62 | 14/5 | $-6.90/$-11.48/$-1.16 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-20.52 | $8.64 | 14/4 | $-7.24/$-12.78/$-0.50 | 9/5/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-21.32 | $7.84 | 5/1 | $-7.34/$-10.72/$-3.26 | 2/4/0 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-21.60 | $7.56 | 15/4 | $-5.42/$-15.68/$-0.50 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-21.72 | $7.44 | 15/5 | $-6.34/$-14.88/$-0.50 | 10/6/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-21.90 | $7.26 | 13/3 | $-5.08/$-15.66/$-1.16 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-22.00 | $7.16 | 9/4 | $-9.96/$-10.18/$-1.86 | 5/6/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-22.08 | $7.08 | 13/5 | $-6.56/$-14.36/$-1.16 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-22.32 | $6.84 | 5/0 | $-8.56/$-10.50/$-3.26 | 2/3/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-22.64 | $6.52 | 7/0 | $-4.94/$-15.80/$-1.90 | 5/0/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-23.24 | $5.92 | 4/2 | $-7.34/$-12.64/$-3.26 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-23.32 | $5.84 | 7/1 | $-8.56/$-14.26/$-0.50 | 2/2/4 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-23.40 | $5.76 | 8/2 | $-6.68/$-14.82/$-1.90 | 7/1/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-23.66 | $5.50 | 11/3 | $-6.88/$-15.62/$-1.16 | 7/4/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-23.84 | $5.32 | 3/0 | $-10.10/$-10.48/$-3.26 | 0/3/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-23.86 | $5.30 | 4/1 | $-10.10/$-10.50/$-3.26 | 0/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-24.08 | $5.08 | 7/3 | $-8.46/$-13.06/$-2.56 | 2/7/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-24.22 | $4.94 | 10/5 | $-7.88/$-13.08/$-3.26 | 8/7/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=4` | True | 5 (9.43%) | $-24.24 | $4.92 | 5/0 | $-5.84/$-15.80/$-2.60 | 4/0/1 |
| `suppress_collapse_exit_if_exit_p_hold>=0.65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-24.34 | $4.82 | 6/1 | $-7.62/$-14.82/$-1.90 | 4/1/2 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=20 AND exit_btc_age_ms<=100` | True | 4 (7.55%) | $-24.44 | $4.72 | 3/1 | $-9.30/$-11.88/$-3.26 | 1/3/0 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=55 AND exit_fair_drawdown_cents<=8` | True | 5 (9.43%) | $-24.54 | $4.62 | 5/0 | $-6.84/$-15.80/$-1.90 | 3/0/2 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_sigma_t_dollars>=100` | True | 6 (11.32%) | $-24.56 | $4.60 | 6/0 | $-6.48/$-14.82/$-3.26 | 5/1/0 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` improves the branch by $10.84 while suppressing 16 hurtful and 5 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
