# Live v28 Exit Value Audit

Generated UTC: `20260507_124026Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 471
- Matched to `exit_signal_seen`: 437
- Unmatched resolved exits: 34
- Actual exit net, all resolved exits: $-43.88
- Hold-to-settlement net for same entries: $-37.86
- Exit value added, all resolved exits: $-6.02
- Helpful exits / hurtful exits, all resolved exits: 121 / 330

Matched feature subset:

- Actual matched exit net: $-57.52
- Matched hold-to-settlement net: $-52.78
- Matched exit value added: $-4.74
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 153 | $22.74 | $4.58 | $18.16 | 28/125 |
| `mushroom_v28_probability_collapse_full` | 71 | $-41.46 | $-40.94 | $-0.52 | 39/32 |
| `unmatched_exit_signal` | 34 | $13.64 | $14.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_reduce` | 213 | $-38.80 | $-16.42 | $-22.38 | 54/159 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 120 (27.46%) | $-43.26 | $14.26 | 91/29 | $-19.58/$-20.92/$-2.76 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 94 (21.51%) | $-51.11 | $6.41 | 46/48 | $-18.59/$-12.74/$-19.78 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (8.70%) | $-54.10 | $3.42 | 28/10 | $-22.08/$-25.96/$-6.06 |
| `suppress_exit_if_p_hold<=0.72` | False | 102 (23.34%) | $-56.54 | $0.98 | 53/49 | $-23.00/$-21.06/$-12.48 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.20%) | $-57.56 | $-0.04 | 10/4 | $-19.04/$-26.72/$-11.80 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (16.93%) | $-58.41 | $-0.89 | 53/21 | $-22.58/$-22.55/$-13.28 |
| `suppress_exit_if_btc_age_ms<=100` | False | 149 (34.10%) | $-60.46 | $-2.94 | 106/43 | $-42.56/$-12.40/$-5.50 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 106 (24.26%) | $-63.15 | $-5.63 | 55/51 | $-34.07/$-14.26/$-14.82 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 110 (25.17%) | $-70.70 | $-13.18 | 98/12 | $-34.74/$-24.20/$-11.76 |
| `suppress_exit_if_p_hold>=0.8` | False | 100 (22.88%) | $-71.14 | $-13.62 | 89/11 | $-34.66/$-24.72/$-11.76 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 135 (30.89%) | $-71.58 | $-14.06 | 117/18 | $-36.14/$-24.20/$-11.24 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 136 (31.12%) | $-74.92 | $-17.40 | 111/25 | $-31.58/$-23.38/$-19.96 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (18.76%) | $-75.00 | $-17.48 | 72/10 | $-35.68/$-24.72/$-14.60 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
