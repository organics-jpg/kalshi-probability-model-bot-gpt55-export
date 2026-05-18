# Live v28 Exit Value Audit

Generated UTC: `20260507_201951Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 521
- Matched to `exit_signal_seen`: 483
- Unmatched resolved exits: 38
- Actual exit net, all resolved exits: $-48.50
- Hold-to-settlement net for same entries: $-32.52
- Exit value added, all resolved exits: $-15.98
- Helpful exits / hurtful exits, all resolved exits: 133 / 366

Matched feature subset:

- Actual matched exit net: $-64.98
- Matched hold-to-settlement net: $-50.56
- Matched exit value added: $-14.42
- Unmatched exit value added: $-1.56

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 167 | $23.02 | $-1.70 | $24.72 | 34/133 |
| `unmatched_exit_signal` | 38 | $16.48 | $18.04 | $-1.56 | 0/16 |
| `mushroom_v28_probability_collapse_full` | 73 | $-42.18 | $-40.34 | $-1.84 | 39/34 |
| `mushroom_v28_probability_reduce` | 243 | $-45.82 | $-8.52 | $-37.30 | 60/183 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 128 (26.50%) | $-47.08 | $17.90 | 99/29 | $-23.22/$-13.14/$-10.72 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 98 (20.29%) | $-54.21 | $10.77 | 50/48 | $-20.05/$-9.94/$-24.22 |
| `suppress_exit_if_btc_age_ms>=800` | False | 42 (8.70%) | $-60.00 | $4.98 | 32/10 | $-28.04/$-21.38/$-10.58 |
| `suppress_exit_if_p_hold<=0.72` | False | 104 (21.53%) | $-62.68 | $2.30 | 55/49 | $-23.42/$-21.40/$-17.86 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (2.90%) | $-65.02 | $-0.04 | 10/4 | $-22.40/$-24.12/$-18.50 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 110 (22.77%) | $-68.29 | $-3.31 | 59/51 | $-37.25/$-8.68/$-22.36 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 88 (18.22%) | $-71.39 | $-6.41 | 59/29 | $-25.94/$-21.43/$-24.02 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 144 (29.81%) | $-75.06 | $-10.08 | 119/25 | $-33.34/$-23.02/$-18.70 |
| `suppress_exit_if_p_hold>=0.8` | False | 106 (21.95%) | $-80.52 | $-15.54 | 93/13 | $-37.38/$-26.68/$-16.46 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 114 (23.60%) | $-81.36 | $-16.38 | 100/14 | $-37.46/$-26.16/$-17.74 |
| `suppress_exit_if_p_hold>=0.85` | False | 84 (17.39%) | $-82.22 | $-17.24 | 74/10 | $-38.40/$-27.24/$-16.58 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 145 (30.02%) | $-83.44 | $-18.46 | 123/22 | $-38.86/$-25.52/$-19.06 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
