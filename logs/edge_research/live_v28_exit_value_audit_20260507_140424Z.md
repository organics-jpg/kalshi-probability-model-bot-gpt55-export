# Live v28 Exit Value Audit

Generated UTC: `20260507_140424Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 483
- Matched to `exit_signal_seen`: 447
- Unmatched resolved exits: 36
- Actual exit net, all resolved exits: $-46.04
- Hold-to-settlement net for same entries: $-29.18
- Exit value added, all resolved exits: $-16.86
- Helpful exits / hurtful exits, all resolved exits: 121 / 342

Matched feature subset:

- Actual matched exit net: $-60.24
- Matched hold-to-settlement net: $-44.94
- Matched exit value added: $-15.30
- Unmatched exit value added: $-1.56

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 153 | $22.74 | $4.58 | $18.16 | 28/125 |
| `mushroom_v28_probability_collapse_full` | 71 | $-41.46 | $-40.94 | $-0.52 | 39/32 |
| `unmatched_exit_signal` | 36 | $14.20 | $15.76 | $-1.56 | 0/16 |
| `mushroom_v28_probability_reduce` | 223 | $-41.52 | $-8.58 | $-32.94 | 54/169 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 122 (27.29%) | $-44.90 | $15.34 | 93/29 | $-20.60/$-21.46/$-2.84 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 96 (21.48%) | $-52.27 | $7.97 | 48/48 | $-16.15/$-15.38/$-20.74 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (8.50%) | $-56.82 | $3.42 | 28/10 | $-24.14/$-26.82/$-5.86 |
| `suppress_exit_if_btc_age_ms<=100` | False | 151 (33.78%) | $-59.18 | $1.06 | 108/43 | $-40.12/$-15.04/$-4.02 |
| `suppress_exit_if_p_hold<=0.72` | False | 102 (22.82%) | $-59.26 | $0.98 | 53/49 | $-19.52/$-24.74/$-15.00 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 76 (17.00%) | $-59.57 | $0.67 | 55/21 | $-24.64/$-22.17/$-12.76 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.13%) | $-60.28 | $-0.04 | 10/4 | $-21.10/$-24.86/$-14.32 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 106 (23.71%) | $-65.87 | $-5.63 | 55/51 | $-30.59/$-15.94/$-19.34 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 110 (24.61%) | $-73.42 | $-13.18 | 98/12 | $-36.68/$-22.34/$-14.40 |
| `suppress_exit_if_p_hold>=0.8` | False | 100 (22.37%) | $-73.86 | $-13.62 | 89/11 | $-36.60/$-22.86/$-14.40 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 135 (30.20%) | $-74.30 | $-14.06 | 117/18 | $-38.08/$-21.70/$-14.52 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 138 (30.87%) | $-76.08 | $-15.84 | 113/25 | $-33.52/$-21.52/$-21.04 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (18.34%) | $-77.72 | $-17.48 | 72/10 | $-37.62/$-22.86/$-17.24 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
