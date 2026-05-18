# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260507_020941Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 57
- Actual collapse-exit net: $-35.76
- Hold-to-settlement net for same entries: $-33.12
- Exit value added: $-2.64
- Hurtful/helpful exits: 26 / 31

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 35 | $-18.50 | $-18.16 | $-0.34 | 18/17 |
| validation | 12 | $-11.30 | $-4.60 | $-6.70 | 6/6 |
| holdout | 10 | $-5.96 | $-10.36 | $4.40 | 2/8 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 7 (12.28%) | $-23.10 | $12.66 | 7/0 | $-15.98/$-1.16/$-5.96 | 3/4/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_p_hold<=0.6` | True | 16 (28.07%) | $-24.34 | $11.42 | 9/7 | $-18.10/$-2.48/$-3.76 | 6/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 7 (12.28%) | $-24.92 | $10.84 | 6/1 | $-12.16/$-6.80/$-5.96 | 5/2/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=20 AND exit_btc_age_ms<=100` | True | 7 (12.28%) | $-25.62 | $10.14 | 5/2 | $-17.70/$-1.96/$-5.96 | 1/6/0 |
| `suppress_collapse_exit_if_position_seconds<=45 AND fair_minus_exit_bid_cents>=5` | True | 13 (22.81%) | $-26.58 | $9.18 | 10/3 | $-12.84/$-8.30/$-5.44 | 8/1/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 23 (40.35%) | $-26.72 | $9.04 | 17/6 | $-16.34/$-7.02/$-3.36 | 18/3/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 7 (12.28%) | $-26.84 | $8.92 | 5/2 | $-14.08/$-6.80/$-5.96 | 5/2/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 4 (7.02%) | $-27.44 | $8.32 | 4/0 | $-14.68/$-6.80/$-5.96 | 2/2/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 6 (10.53%) | $-27.64 | $8.12 | 5/1 | $-16.02/$-5.66/$-5.96 | 4/2/0 |
| `suppress_collapse_exit_if_position_seconds<=45 AND entry_to_exit_loss_cents>=10` | True | 26 (45.61%) | $-27.66 | $8.10 | 17/9 | $-16.48/$-7.82/$-3.36 | 19/5/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=80 AND exit_p_hold<=0.6` | True | 7 (12.28%) | $-28.04 | $7.72 | 5/2 | $-17.70/$-6.98/$-3.36 | 1/4/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=80 AND exit_fair_drawdown_cents>=18` | True | 7 (12.28%) | $-28.04 | $7.72 | 5/2 | $-17.70/$-6.98/$-3.36 | 1/4/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=80 AND exit_fair_drawdown_cents>=20` | True | 7 (12.28%) | $-28.04 | $7.72 | 5/2 | $-17.70/$-6.98/$-3.36 | 1/4/2 |
| `suppress_collapse_exit_if_position_seconds<=45 AND fair_minus_exit_bid_cents>=0` | True | 25 (43.86%) | $-28.04 | $7.72 | 16/9 | $-14.78/$-7.82/$-5.44 | 16/5/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_p_hold<=0.6` | True | 9 (15.79%) | $-28.20 | $7.56 | 6/3 | $-17.86/$-6.98/$-3.36 | 3/4/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 16 (28.07%) | $-28.36 | $7.40 | 11/5 | $-16.74/$-5.66/$-5.96 | 14/2/0 |
| `suppress_collapse_exit_if_position_seconds<=45 AND entry_to_exit_loss_cents>=15` | True | 14 (24.56%) | $-28.42 | $7.34 | 9/5 | $-15.96/$-9.10/$-3.36 | 9/3/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_p_hold<=0.6` | True | 12 (21.05%) | $-28.44 | $7.32 | 7/5 | $-18.10/$-6.98/$-3.36 | 6/4/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=80 AND exit_fair_drawdown_cents>=15` | True | 8 (14.04%) | $-28.62 | $7.14 | 5/3 | $-18.28/$-6.98/$-3.36 | 2/4/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_fair_drawdown_cents>=15` | True | 10 (17.54%) | $-28.78 | $6.98 | 6/4 | $-18.44/$-6.98/$-3.36 | 4/4/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_p_hold<=0.55` | True | 6 (10.53%) | $-28.84 | $6.92 | 4/2 | $-18.50/$-6.98/$-3.36 | 0/4/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=80 AND exit_p_hold<=0.55` | True | 6 (10.53%) | $-28.84 | $6.92 | 4/2 | $-18.50/$-6.98/$-3.36 | 0/4/2 |
| `suppress_collapse_exit_if_exit_exit_bid_cents<=45 AND exit_btc_age_ms<=300` | True | 9 (15.79%) | $-29.12 | $6.64 | 5/4 | $-18.16/$-7.60/$-3.36 | 3/4/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND position_seconds<=45` | True | 27 (47.37%) | $-29.16 | $6.60 | 17/10 | $-15.90/$-7.82/$-5.44 | 18/5/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=15 AND fair_minus_exit_bid_cents>=15` | True | 5 (8.77%) | $-29.24 | $6.52 | 3/2 | $-16.48/$-6.80/$-5.96 | 3/2/0 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` improves the branch by $12.66 while suppressing 7 hurtful and 0 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
