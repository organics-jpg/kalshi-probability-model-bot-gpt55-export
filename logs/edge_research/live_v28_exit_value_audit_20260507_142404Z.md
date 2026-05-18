# Live v28 Exit Value Audit

Generated UTC: `20260507_142404Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 491
- Matched to `exit_signal_seen`: 455
- Unmatched resolved exits: 36
- Actual exit net, all resolved exits: $-47.26
- Hold-to-settlement net for same entries: $-36.80
- Exit value added, all resolved exits: $-10.46
- Helpful exits / hurtful exits, all resolved exits: 127 / 344

Matched feature subset:

- Actual matched exit net: $-61.46
- Matched hold-to-settlement net: $-52.56
- Matched exit value added: $-8.90
- Unmatched exit value added: $-1.56

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 155 | $22.78 | $1.46 | $21.32 | 30/125 |
| `mushroom_v28_probability_collapse_full` | 71 | $-41.46 | $-40.94 | $-0.52 | 39/32 |
| `unmatched_exit_signal` | 36 | $14.20 | $15.76 | $-1.56 | 0/16 |
| `mushroom_v28_probability_reduce` | 229 | $-42.78 | $-13.08 | $-29.70 | 58/171 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 122 (26.81%) | $-46.12 | $15.34 | 93/29 | $-23.40/$-18.42/$-4.30 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 98 (21.54%) | $-50.69 | $10.77 | 50/48 | $-18.95/$-12.34/$-19.40 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (8.35%) | $-58.04 | $3.42 | 28/10 | $-26.94/$-23.78/$-7.32 |
| `suppress_exit_if_p_hold<=0.72` | False | 102 (22.42%) | $-60.48 | $0.98 | 53/49 | $-22.32/$-21.70/$-16.46 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.08%) | $-61.50 | $-0.04 | 10/4 | $-21.30/$-24.42/$-15.78 |
| `suppress_exit_if_btc_age_ms<=100` | False | 157 (34.51%) | $-63.84 | $-2.38 | 110/47 | $-40.32/$-14.44/$-9.08 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 106 (23.30%) | $-67.09 | $-5.63 | 55/51 | $-33.39/$-12.90/$-20.80 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 82 (18.02%) | $-69.99 | $-8.53 | 55/27 | $-24.84/$-21.73/$-23.42 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 140 (30.77%) | $-74.50 | $-13.04 | 115/25 | $-32.76/$-20.68/$-21.06 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 110 (24.18%) | $-74.64 | $-13.18 | 98/12 | $-36.88/$-21.74/$-16.02 |
| `suppress_exit_if_p_hold>=0.8` | False | 100 (21.98%) | $-75.08 | $-13.62 | 89/11 | $-36.80/$-22.26/$-16.02 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 135 (29.67%) | $-75.52 | $-14.06 | 117/18 | $-38.28/$-21.10/$-16.14 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (18.02%) | $-78.94 | $-17.48 | 72/10 | $-37.82/$-22.26/$-18.86 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
