# Live v28 Exit Value Audit

Generated UTC: `20260507_104440Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 463
- Matched to `exit_signal_seen`: 429
- Unmatched resolved exits: 34
- Actual exit net, all resolved exits: $-41.64
- Hold-to-settlement net for same entries: $-38.56
- Exit value added, all resolved exits: $-3.08
- Helpful exits / hurtful exits, all resolved exits: 119 / 324

Matched feature subset:

- Actual matched exit net: $-55.28
- Matched hold-to-settlement net: $-53.48
- Matched exit value added: $-1.80
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 153 | $22.74 | $4.58 | $18.16 | 28/125 |
| `mushroom_v28_probability_collapse_full` | 69 | $-40.82 | $-41.78 | $0.96 | 39/30 |
| `unmatched_exit_signal` | 34 | $13.64 | $14.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_reduce` | 207 | $-37.20 | $-16.28 | $-20.92 | 52/155 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 118 (27.51%) | $-42.50 | $12.78 | 89/29 | $-21.22/$-18.74/$-2.54 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 92 (21.45%) | $-50.35 | $4.93 | 44/48 | $-17.75/$-12.36/$-20.24 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (8.86%) | $-51.86 | $3.42 | 28/10 | $-22.44/$-24.38/$-5.04 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.26%) | $-55.32 | $-0.04 | 10/4 | $-18.20/$-26.34/$-10.78 |
| `suppress_exit_if_p_hold<=0.72` | False | 100 (23.31%) | $-55.78 | $-0.50 | 51/49 | $-23.44/$-19.40/$-12.94 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (17.25%) | $-56.17 | $-0.89 | 53/21 | $-21.74/$-25.05/$-9.38 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 104 (24.24%) | $-62.39 | $-7.11 | 53/51 | $-34.51/$-13.28/$-14.60 |
| `suppress_exit_if_btc_age_ms<=100` | False | 145 (33.80%) | $-62.40 | $-7.12 | 102/43 | $-41.72/$-13.02/$-7.66 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 110 (25.64%) | $-68.46 | $-13.18 | 98/12 | $-33.90/$-23.82/$-10.74 |
| `suppress_exit_if_p_hold>=0.8` | False | 100 (23.31%) | $-68.90 | $-13.62 | 89/11 | $-33.82/$-24.34/$-10.74 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 135 (31.47%) | $-69.34 | $-14.06 | 117/18 | $-35.30/$-23.82/$-10.22 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 136 (31.70%) | $-72.68 | $-17.40 | 111/25 | $-30.74/$-23.00/$-18.94 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (19.11%) | $-72.76 | $-17.48 | 72/10 | $-34.84/$-24.34/$-13.58 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
