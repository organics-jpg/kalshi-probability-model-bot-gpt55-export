# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260507_140428Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 71
- Actual collapse-exit net: $-41.46
- Hold-to-settlement net for same entries: $-40.94
- Exit value added: $-0.52
- Hurtful/helpful exits: 32 / 39

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 41 | $-23.76 | $-18.96 | $-4.80 | 22/19 |
| validation | 14 | $-11.20 | $-11.04 | $-0.16 | 4/10 |
| holdout | 16 | $-6.50 | $-10.94 | $4.44 | 6/10 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 27 (38.03%) | $-23.46 | $18.00 | 20/7 | $-16.60/$-5.96/$-0.90 | 17/4/6 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 30 (42.25%) | $-24.56 | $16.90 | 21/9 | $-15.62/$-8.04/$-0.90 | 18/6/6 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 24 (33.80%) | $-25.34 | $16.12 | 17/7 | $-17.16/$-5.96/$-2.22 | 16/4/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 17 (23.94%) | $-26.50 | $14.96 | 12/5 | $-17.62/$-5.96/$-2.92 | 10/4/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 22 (30.99%) | $-28.46 | $13.00 | 17/5 | $-22.00/$-5.56/$-0.90 | 14/2/6 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 7 (9.86%) | $-28.80 | $12.66 | 7/0 | $-16.74/$-5.56/$-6.50 | 5/2/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=15 AND exit_sigma_t_dollars>=75` | True | 11 (15.49%) | $-29.16 | $12.30 | 7/4 | $-16.70/$-5.96/$-6.50 | 7/4/0 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 24 (33.80%) | $-30.58 | $10.88 | 18/6 | $-22.04/$-7.64/$-0.90 | 14/4/6 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 7 (9.86%) | $-30.62 | $10.84 | 6/1 | $-12.92/$-11.20/$-6.50 | 7/0/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=20 AND exit_btc_age_ms<=300` | True | 11 (15.49%) | $-30.78 | $10.68 | 7/4 | $-20.52/$-3.76/$-6.50 | 5/6/0 |
| `suppress_collapse_exit_if_exit_p_hold<=0.6 AND exit_sigma_t_dollars>=75` | True | 13 (18.31%) | $-31.24 | $10.22 | 7/6 | $-16.70/$-8.04/$-6.50 | 7/6/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=20 AND exit_btc_age_ms<=100` | True | 7 (9.86%) | $-31.32 | $10.14 | 5/2 | $-18.46/$-6.36/$-6.50 | 3/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=20` | True | 12 (16.90%) | $-31.48 | $9.98 | 7/5 | $-19.02/$-5.96/$-6.50 | 8/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 19 (26.76%) | $-31.94 | $9.52 | 12/7 | $-17.40/$-8.04/$-6.50 | 13/6/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 9 (12.68%) | $-32.18 | $9.28 | 9/0 | $-18.60/$-11.20/$-2.38 | 5/0/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=15 AND exit_btc_age_ms<=300` | True | 14 (19.72%) | $-32.20 | $9.26 | 8/6 | $-21.94/$-3.76/$-6.50 | 8/6/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 35 (49.30%) | $-32.42 | $9.04 | 23/12 | $-17.32/$-8.60/$-6.50 | 21/2/12 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=15 AND exit_btc_age_ms<=100` | True | 9 (12.68%) | $-32.50 | $8.96 | 6/3 | $-19.64/$-6.36/$-6.50 | 5/4/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 7 (9.86%) | $-32.54 | $8.92 | 5/2 | $-14.84/$-11.20/$-6.50 | 7/0/0 |
| `suppress_collapse_exit_if_exit_p_hold<=0.55 AND exit_sigma_t_dollars>=75` | True | 7 (9.86%) | $-32.64 | $8.82 | 4/3 | $-20.18/$-5.96/$-6.50 | 3/4/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=18 AND exit_btc_age_ms<=300` | True | 12 (16.90%) | $-32.94 | $8.52 | 7/5 | $-22.68/$-3.76/$-6.50 | 6/6/0 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 12 (16.90%) | $-32.94 | $8.52 | 10/2 | $-19.36/$-11.20/$-2.38 | 8/0/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=18 AND exit_sigma_t_dollars>=75` | True | 9 (12.68%) | $-32.98 | $8.48 | 5/4 | $-20.52/$-5.96/$-6.50 | 5/4/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents>=20 AND exit_sigma_t_dollars>=75` | True | 9 (12.68%) | $-32.98 | $8.48 | 5/4 | $-20.52/$-5.96/$-6.50 | 5/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 4 (5.63%) | $-33.14 | $8.32 | 4/0 | $-15.44/$-11.20/$-6.50 | 4/0/0 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` improves the branch by $18.00 while suppressing 20 hurtful and 7 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
