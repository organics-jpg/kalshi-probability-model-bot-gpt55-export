# Live v28 Exit Value Audit

Generated UTC: `20260507_141256Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 485
- Matched to `exit_signal_seen`: 449
- Unmatched resolved exits: 36
- Actual exit net, all resolved exits: $-46.98
- Hold-to-settlement net for same entries: $-27.32
- Exit value added, all resolved exits: $-19.66
- Helpful exits / hurtful exits, all resolved exits: 121 / 344

Matched feature subset:

- Actual matched exit net: $-61.18
- Matched hold-to-settlement net: $-43.08
- Matched exit value added: $-18.10
- Unmatched exit value added: $-1.56

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 153 | $22.74 | $4.58 | $18.16 | 28/125 |
| `mushroom_v28_probability_collapse_full` | 71 | $-41.46 | $-40.94 | $-0.52 | 39/32 |
| `unmatched_exit_signal` | 36 | $14.20 | $15.76 | $-1.56 | 0/16 |
| `mushroom_v28_probability_reduce` | 225 | $-42.46 | $-6.72 | $-35.74 | 54/171 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 122 (27.17%) | $-45.84 | $15.34 | 93/29 | $-22.20/$-19.74/$-3.90 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 98 (21.83%) | $-50.41 | $10.77 | 50/48 | $-17.75/$-13.66/$-19.00 |
| `suppress_exit_if_btc_age_ms<=100` | False | 153 (34.08%) | $-57.32 | $3.86 | 110/43 | $-40.42/$-14.54/$-2.36 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (8.46%) | $-57.76 | $3.42 | 28/10 | $-25.74/$-25.10/$-6.92 |
| `suppress_exit_if_p_hold<=0.72` | False | 102 (22.72%) | $-60.20 | $0.98 | 53/49 | $-21.12/$-23.02/$-16.06 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 76 (16.93%) | $-60.51 | $0.67 | 55/21 | $-24.94/$-21.75/$-13.82 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.12%) | $-61.22 | $-0.04 | 10/4 | $-21.40/$-24.44/$-15.38 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 106 (23.61%) | $-66.81 | $-5.63 | 55/51 | $-32.19/$-14.22/$-20.40 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 140 (31.18%) | $-74.22 | $-13.04 | 115/25 | $-33.82/$-21.02/$-19.38 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 110 (24.50%) | $-74.36 | $-13.18 | 98/12 | $-36.98/$-21.84/$-15.54 |
| `suppress_exit_if_p_hold>=0.8` | False | 100 (22.27%) | $-74.80 | $-13.62 | 89/11 | $-36.90/$-22.36/$-15.54 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 135 (30.07%) | $-75.24 | $-14.06 | 117/18 | $-38.38/$-21.20/$-15.66 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (18.26%) | $-78.66 | $-17.48 | 72/10 | $-37.92/$-22.36/$-18.38 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
