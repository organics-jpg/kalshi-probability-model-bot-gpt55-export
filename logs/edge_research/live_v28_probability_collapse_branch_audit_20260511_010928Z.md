# Live v28 Probability Collapse Exit Branch Audit

Generated UTC: `20260511_010928Z`

## Scope

- Research-only audit of `mushroom_v28_probability_collapse_full` exits from the current live v28 fill tape.
- Positive suppress delta means holding to settlement would have beaten the live collapse exit.
- This is not promotion evidence; the branch sample is small and must be judged by future registered rows.
- No live bot files or processes are touched and no orders are submitted.

## Branch Baseline

- Matched resolved collapse exits: 53
- Actual collapse-exit net: $-31.93
- Hold-to-settlement net for same entries: $-26.71
- Exit value added: $-5.22
- Hurtful/helpful exits: 26 / 27

## Split Baseline

| split | n | actual | hold | exit value | hurtful/helpful |
|---|---:|---:|---:|---:|---:|
| train | 26 | $-12.00 | $-7.75 | $-4.25 | 15/11 |
| validation | 18 | $-16.65 | $-13.98 | $-2.67 | 7/11 |
| holdout | 9 | $-3.28 | $-4.98 | $1.70 | 4/5 |

## Suppress-Collapse Diagnostics

| rule | pass | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted | split suppressed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` | True | 23 (43.40%) | $-19.33 | $12.60 | 17/6 | $-7.26/$-11.82/$-0.25 | 10/9/4 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_sigma_t_dollars>=75` | True | 21 (39.62%) | $-19.43 | $12.50 | 16/5 | $-7.26/$-11.92/$-0.25 | 10/7/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=10` | True | 19 (35.85%) | $-20.76 | $11.17 | 14/5 | $-7.86/$-11.92/$-0.98 | 9/7/3 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=70 AND exit_sigma_t_dollars>=75` | True | 18 (33.96%) | $-21.84 | $10.09 | 14/4 | $-8.24/$-13.35/$-0.25 | 9/5/4 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_sigma_t_dollars>=75` | True | 19 (35.85%) | $-22.84 | $9.09 | 15/4 | $-6.41/$-16.18/$-0.25 | 9/6/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds<=180` | True | 20 (37.74%) | $-22.88 | $9.05 | 15/5 | $-7.26/$-15.37/$-0.25 | 10/6/4 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=18 AND exit_sigma_t_dollars>=75` | True | 16 (30.19%) | $-23.23 | $8.70 | 13/3 | $-6.19/$-16.07/$-0.97 | 7/6/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=0` | True | 18 (33.96%) | $-23.25 | $8.68 | 13/5 | $-7.64/$-14.64/$-0.97 | 7/8/3 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=50 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-23.57 | $8.36 | 5/1 | $-9.02/$-11.27/$-3.28 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND entry_to_exit_loss_cents>=15` | True | 13 (24.53%) | $-23.61 | $8.32 | 9/4 | $-11.17/$-10.69/$-1.75 | 5/6/2 |
| `suppress_collapse_exit_if_exit_btc_age_ms<=100 AND entry_to_exit_loss_cents>=20` | True | 8 (15.09%) | $-24.25 | $7.68 | 6/2 | $-8.86/$-12.11/$-3.28 | 3/5/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND position_seconds<=45` | True | 26 (49.06%) | $-24.69 | $7.24 | 18/8 | $-6.13/$-15.65/$-2.91 | 16/3/7 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND exit_sigma_t_dollars>=50` | True | 9 (16.98%) | $-24.75 | $7.18 | 8/1 | $-6.42/$-16.55/$-1.78 | 5/2/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND exit_fair_drawdown_cents<=8` | True | 7 (13.21%) | $-24.85 | $7.08 | 7/0 | $-6.42/$-16.65/$-1.78 | 5/0/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=100` | True | 5 (9.43%) | $-24.90 | $7.03 | 5/0 | $-10.34/$-11.28/$-3.28 | 2/3/0 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=75 AND exit_sigma_t_dollars>=75` | True | 14 (26.42%) | $-25.25 | $6.68 | 11/3 | $-7.99/$-16.28/$-0.98 | 7/4/3 |
| `suppress_collapse_exit_if_exit_p_hold>=0.6 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.37 | $6.56 | 8/2 | $-8.00/$-15.59/$-1.78 | 7/1/2 |
| `suppress_collapse_exit_if_exit_entry_basis_cents>=65 AND fair_minus_exit_bid_cents>=15` | True | 6 (11.32%) | $-25.48 | $6.45 | 4/2 | $-9.02/$-13.18/$-3.28 | 2/4/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms>=500` | True | 8 (15.09%) | $-25.55 | $6.38 | 7/1 | $-10.35/$-14.95/$-0.25 | 2/2/4 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND exit_btc_age_ms<=500` | True | 15 (28.30%) | $-25.71 | $6.22 | 10/5 | $-8.91/$-13.52/$-3.28 | 8/7/0 |
| `suppress_collapse_exit_if_exit_exit_bid_cents>=50 AND exit_fair_drawdown_cents<=8` | True | 10 (18.87%) | $-25.75 | $6.18 | 8/2 | $-7.42/$-16.55/$-1.78 | 6/2/2 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=5` | True | 10 (18.87%) | $-26.13 | $5.80 | 7/3 | $-10.21/$-13.41/$-2.51 | 2/7/1 |
| `suppress_collapse_exit_if_exit_fair_drawdown_cents<=8 AND entry_to_exit_loss_cents>=10` | True | 6 (11.32%) | $-26.21 | $5.72 | 5/1 | $-7.05/$-16.65/$-2.51 | 5/0/1 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND position_seconds>=90` | True | 5 (9.43%) | $-26.34 | $5.59 | 4/1 | $-12.00/$-11.06/$-3.28 | 0/5/0 |
| `suppress_collapse_exit_if_exit_sigma_t_dollars>=75 AND fair_minus_exit_bid_cents>=15` | True | 3 (5.66%) | $-26.37 | $5.56 | 3/0 | $-12.00/$-11.09/$-3.28 | 0/3/0 |

## Read

- Best diagnostic rule: `suppress_collapse_exit_if_exit_sigma_t_dollars>=75` improves the branch by $12.60 while suppressing 17 hurtful and 6 helpful exits.
- Physical hypothesis: a full probability-collapse exit is suspect when terminal sigma is still high and fair-value drawdown is not yet deep; that looks more like temporary path turbulence than a resolved state transition.
