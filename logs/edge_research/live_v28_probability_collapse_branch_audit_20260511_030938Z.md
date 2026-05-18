# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260511_030938Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-31.53
- Hold-to-settlement net for same entries: $-26.74
- Exit value added: $-4.79
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-11.30 | $-7.80 | $-3.50 | 15/11 |
| validation | 18 | $-16.88 | $-13.96 | $-2.92 | 7/11 |
| holdout | 9 | $-3.35 | $-4.98 | $1.63 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-19.25 | $12.28 | 17/6 | $-7.13/$-11.80/$-0.32 | 10/9/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-19.35 | $12.18 | 16/5 | $-7.13/$-11.90/$-0.32 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-20.68 | $10.85 | 14/5 | $-7.73/$-11.90/$-1.05 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-21.76 | $9.77 | 14/4 | $-8.11/$-13.33/$-0.32 | 9/5/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-22.76 | $8.77 | 15/4 | $-6.28/$-16.16/$-0.32 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-22.98 | $8.55 | 15/5 | $-7.13/$-15.53/$-0.32 | 10/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-23.17 | $8.36 | 5/1 | $-8.32/$-11.50/$-3.35 | 2/4/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-23.26 | $8.27 | 13/3 | $-5.99/$-16.23/$-1.04 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-23.28 | $8.25 | 13/5 | $-7.44/$-14.80/$-1.04 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-23.46 | $8.07 | 9/4 | $-10.97/$-10.67/$-1.82 | 5/6/2 |
| `suppress_collapse_exit_if_exit_btc_age_ms<=100 AND entry_to_exit_loss_cents>=20` | True | 8 (15.09%) | $-23.60 | $7.93 | 6/2 | $-8.16/$-12.09/$-3.35 | 3/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-24.25 | $7.28 | 5/0 | $-9.64/$-11.26/$-3.35 | 2/3/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND exit_sigma_t_dollars>=50` | True | 9 (16.98%) | $-24.43 | $7.10 | 8/1 | $-5.80/$-16.78/$-1.85 | 5/2/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 26 (49.06%) | $-24.51 | $7.02 | 18/8 | $-5.72/$-15.88/$-2.91 | 16/3/7 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-24.53 | $7.00 | 7/0 | $-5.80/$-16.88/$-1.85 | 5/0/2 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.05 | $6.48 | 8/2 | $-7.38/$-15.82/$-1.85 | 7/1/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-25.08 | $6.45 | 4/2 | $-8.32/$-13.41/$-3.35 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-25.15 | $6.38 | 7/1 | $-9.65/$-15.18/$-0.32 | 2/2/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-25.17 | $6.36 | 11/3 | $-7.86/$-16.26/$-1.05 | 7/4/3 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.43 | $6.10 | 8/2 | $-6.80/$-16.78/$-1.85 | 6/2/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-25.63 | $5.90 | 10/5 | $-8.78/$-13.50/$-3.35 | 8/7/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-25.66 | $5.87 | 7/3 | $-9.51/$-13.57/$-2.58 | 2/7/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-25.69 | $5.84 | 4/1 | $-11.30/$-11.04/$-3.35 | 0/5/0 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND entry_to_exit_loss_cents>=10` | True | 6 (11.32%) | $-25.92 | $5.61 | 5/1 | $-6.46/$-16.88/$-2.58 | 5/0/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-25.97 | $5.56 | 3/0 | $-11.30/$-11.32/$-3.35 | 0/3/0 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` improves the branch by $12.28 while suppressing 17 hurtful and 6 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
