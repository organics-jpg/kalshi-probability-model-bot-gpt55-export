# Live v28 Exit Value Audit

Generated UTC: `20260506_100702Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 188
- Matched to `exit_signal_seen`: 176
- Unmatched resolved exits: 12
- Actual exit net, all resolved exits: $-9.38
- Hold-to-settlement net for same entries: $-29.19
- Exit value added, all resolved exits: $19.81
- Helpful exits / hurtful exits, all resolved exits: 55 / 125

Matched feature subset:

- Actual matched exit net: $-13.10
- Matched hold-to-settlement net: $-33.79
- Matched exit value added: $20.69
- Unmatched exit value added: $-0.88

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 70 | $13.70 | $-2.52 | $16.22 | 16/54 |
| `mushroom_v28_probability_reduce` | 78 | $-13.50 | $-19.01 | $5.51 | 26/52 |
| `unmatched_exit_signal` | 12 | $3.72 | $4.60 | $-0.88 | 0/4 |
| `mushroom_v28_probability_collapse_full` | 28 | $-13.30 | $-12.26 | $-1.04 | 13/15 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_exit_bid_cents<=65` | False | 41 (23.30%) | $-10.67 | $2.43 | 23/18 | $2.09/$-5.32/$-7.44 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (7.95%) | $-13.14 | $-0.04 | 10/4 | $-2.22/$-1.16/$-9.76 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 39 (22.16%) | $-13.88 | $-0.78 | 28/11 | $-6.20/$1.04/$-8.72 |
| `suppress_exit_if_btc_age_ms>=500` | False | 47 (26.70%) | $-14.60 | $-1.50 | 35/12 | $5.12/$-7.52/$-12.20 |
| `suppress_exit_if_p_hold<=0.72` | False | 45 (25.57%) | $-16.36 | $-3.26 | 26/19 | $-2.04/$-4.56/$-9.76 |
| `suppress_exit_if_btc_age_ms>=800` | False | 15 (8.52%) | $-17.84 | $-4.74 | 10/5 | $-2.90/$-3.38/$-11.56 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 57 (32.39%) | $-17.84 | $-4.74 | 46/11 | $-1.76/$-5.26/$-10.82 |
| `suppress_exit_if_p_hold>=0.8` | False | 41 (23.30%) | $-19.14 | $-6.04 | 36/5 | $-4.80/$-2.88/$-11.46 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 49 (27.84%) | $-19.22 | $-6.12 | 43/6 | $-2.86/$-4.90/$-11.46 |
| `suppress_exit_if_p_hold>=0.85` | False | 33 (18.75%) | $-19.64 | $-6.54 | 29/4 | $-5.94/$-3.96/$-9.74 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 61 (34.66%) | $-22.86 | $-9.76 | 51/10 | $-5.98/$-3.82/$-13.06 |
| `suppress_exit_if_btc_age_ms<=100` | False | 56 (31.82%) | $-25.68 | $-12.58 | 37/19 | $-14.00/$-5.76/$-5.92 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 36 (20.45%) | $-27.69 | $-14.59 | 17/19 | $-14.03/$-2.30/$-11.36 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
