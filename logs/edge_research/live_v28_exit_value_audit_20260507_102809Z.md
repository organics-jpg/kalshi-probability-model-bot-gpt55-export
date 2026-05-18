# Live v28 Exit Value Audit

Generated UTC: `20260507_102809Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 461
- Matched to `exit_signal_seen`: 427
- Unmatched resolved exits: 34
- Actual exit net, all resolved exits: $-41.84
- Hold-to-settlement net for same entries: $-36.00
- Exit value added, all resolved exits: $-5.84
- Helpful exits / hurtful exits, all resolved exits: 117 / 324

Matched feature subset:

- Actual matched exit net: $-55.48
- Matched hold-to-settlement net: $-50.92
- Matched exit value added: $-4.56
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 153 | $22.74 | $4.58 | $18.16 | 28/125 |
| `mushroom_v28_probability_collapse_full` | 69 | $-40.82 | $-41.78 | $0.96 | 39/30 |
| `unmatched_exit_signal` | 34 | $13.64 | $14.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_reduce` | 205 | $-37.40 | $-13.72 | $-23.68 | 50/155 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 116 (27.17%) | $-39.94 | $15.54 | 89/27 | $-21.08/$-18.65/$-0.21 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 92 (21.55%) | $-50.55 | $4.93 | 44/48 | $-17.61/$-12.27/$-20.67 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (8.90%) | $-52.06 | $3.42 | 28/10 | $-22.30/$-24.29/$-5.47 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.28%) | $-55.52 | $-0.04 | 10/4 | $-18.06/$-26.25/$-11.21 |
| `suppress_exit_if_p_hold<=0.72` | False | 100 (23.42%) | $-55.98 | $-0.50 | 51/49 | $-23.30/$-19.31/$-13.37 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (17.33%) | $-56.37 | $-0.89 | 53/21 | $-21.60/$-25.87/$-8.90 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 104 (24.36%) | $-62.59 | $-7.11 | 53/51 | $-34.37/$-13.19/$-15.03 |
| `suppress_exit_if_btc_age_ms<=100` | False | 145 (33.96%) | $-62.60 | $-7.12 | 102/43 | $-41.58/$-12.93/$-8.09 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 110 (25.76%) | $-68.66 | $-13.18 | 98/12 | $-33.76/$-23.73/$-11.17 |
| `suppress_exit_if_p_hold>=0.8` | False | 100 (23.42%) | $-69.10 | $-13.62 | 89/11 | $-33.68/$-24.25/$-11.17 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 135 (31.62%) | $-69.54 | $-14.06 | 117/18 | $-35.16/$-23.73/$-10.65 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 134 (31.38%) | $-70.12 | $-14.64 | 111/23 | $-30.60/$-22.91/$-16.61 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (19.20%) | $-72.96 | $-17.48 | 72/10 | $-34.70/$-24.25/$-14.01 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
