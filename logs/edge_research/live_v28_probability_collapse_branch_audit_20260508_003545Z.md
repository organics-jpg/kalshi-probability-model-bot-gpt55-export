# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260508_003545Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 73
- Actual collapse-exit net: $-42.18
- Hold-to-settlement net for same entries: $-40.34
- Exit value added: $-1.84
- Hurtful/helpful exits: 34 / 39

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 43 | $-24.36 | $-22.16 | $-2.20 | 22/21 |
| validation | 12 | $-10.60 | $-7.84 | $-2.76 | 4/8 |
| holdout | 18 | $-7.22 | $-10.34 | $3.12 | 8/10 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 29 (39.73%) | $-22.86 | $19.32 | 22/7 | $-17.20/$-5.36/$-0.30 | 17/4/8 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 32 (43.84%) | $-23.96 | $18.22 | 23/9 | $-16.22/$-7.44/$-0.30 | 18/6/8 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 26 (35.62%) | $-24.74 | $17.44 | 19/7 | $-17.76/$-5.36/$-1.62 | 16/4/6 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 19 (26.03%) | $-25.90 | $16.28 | 14/5 | $-18.22/$-5.36/$-2.32 | 10/4/5 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 24 (32.88%) | $-27.86 | $14.32 | 19/5 | $-22.60/$-4.96/$-0.30 | 14/2/8 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=15 AND exit_sigma_t_dollars>=75` | True | 13 (17.81%) | $-28.56 | $13.62 | 9/4 | $-17.30/$-5.36/$-5.90 | 7/4/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 7 (9.59%) | $-29.52 | $12.66 | 7/0 | $-17.34/$-4.96/$-7.22 | 5/2/0 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 26 (35.62%) | $-29.98 | $12.20 | 20/6 | $-22.64/$-7.04/$-0.30 | 14/4/8 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 7 (9.59%) | $-31.34 | $10.84 | 6/1 | $-13.52/$-10.60/$-7.22 | 7/0/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=20 AND exit_btc_age_ms<=300` | True | 11 (15.07%) | $-31.50 | $10.68 | 7/4 | $-21.12/$-3.16/$-7.22 | 5/6/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 37 (50.68%) | $-31.82 | $10.36 | 25/12 | $-17.92/$-8.00/$-5.90 | 21/2/14 |
| `suppress_collapse_exit_if_exit_p_hold<=0.6 AND exit_sigma_t_dollars>=75` | True | 13 (17.81%) | $-31.96 | $10.22 | 7/6 | $-17.30/$-7.44/$-7.22 | 7/6/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=20 AND exit_btc_age_ms<=100` | True | 7 (9.59%) | $-32.04 | $10.14 | 5/2 | $-19.06/$-5.76/$-7.22 | 3/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=20` | True | 12 (16.44%) | $-32.20 | $9.98 | 7/5 | $-19.62/$-5.36/$-7.22 | 8/4/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=18 AND exit_sigma_t_dollars>=75` | True | 11 (15.07%) | $-32.38 | $9.80 | 7/4 | $-21.12/$-5.36/$-5.90 | 5/4/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 19 (26.03%) | $-32.66 | $9.52 | 12/7 | $-18.00/$-7.44/$-7.22 | 13/6/0 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND position_seconds<=45` | True | 27 (36.99%) | $-32.80 | $9.38 | 21/6 | $-19.66/$-10.60/$-2.54 | 17/0/10 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 9 (12.33%) | $-32.90 | $9.28 | 9/0 | $-19.20/$-10.60/$-3.10 | 5/0/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=15 AND exit_btc_age_ms<=300` | True | 14 (19.18%) | $-32.92 | $9.26 | 8/6 | $-22.54/$-3.16/$-7.22 | 8/6/0 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=60 AND exit_sigma_t_dollars>=75` | True | 17 (23.29%) | $-32.94 | $9.24 | 15/2 | $-22.04/$-10.60/$-0.30 | 9/0/8 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=15 AND exit_btc_age_ms<=100` | True | 9 (12.33%) | $-33.22 | $8.96 | 6/3 | $-20.24/$-5.76/$-7.22 | 5/4/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 7 (9.59%) | $-33.26 | $8.92 | 5/2 | $-15.44/$-10.60/$-7.22 | 7/0/0 |
| `suppress_collapse_exit_if_exit_p_hold<=0.55 AND exit_sigma_t_dollars>=75` | True | 7 (9.59%) | $-33.36 | $8.82 | 4/3 | $-20.78/$-5.36/$-7.22 | 3/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 13 (17.81%) | $-33.48 | $8.70 | 11/2 | $-22.58/$-10.60/$-0.30 | 5/0/8 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=18 AND exit_btc_age_ms<=300` | True | 12 (16.44%) | $-33.66 | $8.52 | 7/5 | $-23.28/$-3.16/$-7.22 | 6/6/0 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` improves the branch by $19.32 while suppressing 22 hurtful and 7 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
