# Live v28 Exit Value Audit

Generated UTC: `20260507_024625Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 413
- Matched to `exit_signal_seen`: 381
- Unmatched resolved exits: 32
- Actual exit net, all resolved exits: $-36.52
- Hold-to-settlement net for same entries: $-27.98
- Exit value added, all resolved exits: $-8.54
- Helpful exits / hurtful exits, all resolved exits: 101 / 294

Matched feature subset:

- Actual matched exit net: $-49.16
- Matched hold-to-settlement net: $-41.90
- Matched exit value added: $-7.26
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 135 | $23.66 | $0.58 | $23.08 | 26/109 |
| `unmatched_exit_signal` | 32 | $12.64 | $13.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_collapse_full` | 63 | $-38.26 | $-33.62 | $-4.64 | 33/30 |
| `mushroom_v28_probability_reduce` | 183 | $-34.56 | $-8.86 | $-25.70 | 42/141 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 108 (28.35%) | $-35.36 | $13.80 | 83/25 | $-20.94/$-14.18/$-0.24 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 86 (22.57%) | $-38.63 | $10.53 | 44/42 | $-15.95/$-12.12/$-10.56 |
| `suppress_exit_if_btc_age_ms>=800` | False | 36 (9.45%) | $-46.78 | $2.38 | 26/10 | $-23.00/$-18.30/$-5.48 |
| `suppress_exit_if_p_hold<=0.72` | False | 90 (23.62%) | $-47.82 | $1.34 | 47/43 | $-21.64/$-14.00/$-12.18 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.67%) | $-49.20 | $-0.04 | 10/4 | $-17.72/$-21.30/$-10.18 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (19.42%) | $-50.05 | $-0.89 | 53/21 | $-19.50/$-23.50/$-7.05 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 92 (24.15%) | $-53.05 | $-3.89 | 49/43 | $-32.71/$-10.96/$-9.38 |
| `suppress_exit_if_btc_age_ms<=100` | False | 129 (33.86%) | $-56.00 | $-6.84 | 92/37 | $-30.96/$-19.12/$-5.92 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 128 (33.60%) | $-61.56 | $-12.40 | 107/21 | $-23.94/$-24.70/$-12.92 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 100 (26.25%) | $-65.22 | $-16.06 | 88/12 | $-27.10/$-25.14/$-12.98 |
| `suppress_exit_if_p_hold>=0.8` | False | 90 (23.62%) | $-65.66 | $-16.50 | 79/11 | $-27.02/$-25.66/$-12.98 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 117 (30.71%) | $-65.98 | $-16.82 | 101/16 | $-28.50/$-25.14/$-12.34 |
| `suppress_exit_if_p_hold>=0.85` | False | 76 (19.95%) | $-67.72 | $-18.56 | 66/10 | $-27.52/$-26.18/$-14.02 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
