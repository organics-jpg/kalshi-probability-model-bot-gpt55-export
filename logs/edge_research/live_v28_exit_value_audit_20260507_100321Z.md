# Live v28 Exit Value Audit

Generated UTC: `20260507_100321Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 459
- Matched to `exit_signal_seen`: 425
- Unmatched resolved exits: 34
- Actual exit net, all resolved exits: $-41.80
- Hold-to-settlement net for same entries: $-32.92
- Exit value added, all resolved exits: $-8.88
- Helpful exits / hurtful exits, all resolved exits: 115 / 324

Matched feature subset:

- Actual matched exit net: $-55.44
- Matched hold-to-settlement net: $-47.84
- Matched exit value added: $-7.60
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 153 | $22.74 | $4.58 | $18.16 | 28/125 |
| `mushroom_v28_probability_collapse_full` | 69 | $-40.82 | $-41.78 | $0.96 | 39/30 |
| `unmatched_exit_signal` | 34 | $13.64 | $14.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_reduce` | 203 | $-37.36 | $-10.64 | $-26.72 | 48/155 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 116 (27.29%) | $-39.90 | $15.54 | 89/27 | $-20.94/$-18.65/$-0.31 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 92 (21.65%) | $-50.51 | $4.93 | 44/48 | $-17.47/$-12.27/$-20.77 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (8.94%) | $-52.02 | $3.42 | 28/10 | $-22.16/$-24.29/$-5.57 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.29%) | $-55.48 | $-0.04 | 10/4 | $-17.92/$-26.25/$-11.31 |
| `suppress_exit_if_p_hold<=0.72` | False | 100 (23.53%) | $-55.94 | $-0.50 | 51/49 | $-23.16/$-19.31/$-13.47 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (17.41%) | $-56.33 | $-0.89 | 53/21 | $-21.46/$-26.49/$-8.38 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 104 (24.47%) | $-62.55 | $-7.11 | 53/51 | $-34.23/$-13.19/$-15.13 |
| `suppress_exit_if_btc_age_ms<=100` | False | 145 (34.12%) | $-62.56 | $-7.12 | 102/43 | $-41.44/$-12.93/$-8.19 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 110 (25.88%) | $-68.62 | $-13.18 | 98/12 | $-33.62/$-23.73/$-11.27 |
| `suppress_exit_if_p_hold>=0.8` | False | 100 (23.53%) | $-69.06 | $-13.62 | 89/11 | $-33.54/$-24.25/$-11.27 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 135 (31.76%) | $-69.50 | $-14.06 | 117/18 | $-35.02/$-23.73/$-10.75 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 134 (31.53%) | $-70.08 | $-14.64 | 111/23 | $-30.46/$-22.91/$-16.71 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (19.29%) | $-72.92 | $-17.48 | 72/10 | $-34.56/$-24.25/$-14.11 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
