# Live v28 Exit Value Audit

Generated UTC: `20260507_161828Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 511
- Matched to `exit_signal_seen`: 473
- Unmatched resolved exits: 38
- Actual exit net, all resolved exits: $-47.72
- Hold-to-settlement net for same entries: $-37.82
- Exit value added, all resolved exits: $-9.90
- Helpful exits / hurtful exits, all resolved exits: 133 / 356

Matched feature subset:

- Actual matched exit net: $-64.20
- Matched hold-to-settlement net: $-55.86
- Matched exit value added: $-8.34
- Unmatched exit value added: $-1.56

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 165 | $22.34 | $-2.62 | $24.96 | 34/131 |
| `mushroom_v28_probability_collapse_full` | 71 | $-41.46 | $-40.94 | $-0.52 | 39/32 |
| `unmatched_exit_signal` | 38 | $16.48 | $18.04 | $-1.56 | 0/16 |
| `mushroom_v28_probability_reduce` | 237 | $-45.08 | $-12.30 | $-32.78 | 60/177 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 122 (25.79%) | $-48.86 | $15.34 | 93/29 | $-23.40/$-15.56/$-9.90 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 98 (20.72%) | $-53.43 | $10.77 | 50/48 | $-19.19/$-11.48/$-22.76 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (8.03%) | $-60.78 | $3.42 | 28/10 | $-27.18/$-22.92/$-10.68 |
| `suppress_exit_if_p_hold<=0.72` | False | 102 (21.56%) | $-63.22 | $0.98 | 53/49 | $-22.56/$-21.54/$-19.12 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (2.96%) | $-64.24 | $-0.04 | 10/4 | $-21.54/$-24.26/$-18.44 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 108 (22.83%) | $-68.83 | $-4.63 | 57/51 | $-36.39/$-8.82/$-23.62 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 88 (18.60%) | $-70.61 | $-6.41 | 59/29 | $-25.08/$-21.57/$-23.96 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 142 (30.02%) | $-74.52 | $-10.32 | 117/25 | $-32.48/$-25.24/$-16.80 |
| `suppress_exit_if_p_hold>=0.8` | False | 104 (21.99%) | $-79.98 | $-15.78 | 91/13 | $-36.52/$-26.82/$-16.64 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 112 (23.68%) | $-80.82 | $-16.62 | 98/14 | $-36.60/$-26.30/$-17.92 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (17.34%) | $-81.68 | $-17.48 | 72/10 | $-37.54/$-27.38/$-16.76 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 143 (30.23%) | $-82.90 | $-18.70 | 121/22 | $-38.00/$-25.66/$-19.24 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
