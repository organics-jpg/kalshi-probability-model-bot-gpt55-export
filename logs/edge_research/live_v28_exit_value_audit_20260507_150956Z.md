# Live v28 Exit Value Audit

Generated UTC: `20260507_150956Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 501
- Matched to `exit_signal_seen`: 465
- Unmatched resolved exits: 36
- Actual exit net, all resolved exits: $-49.36
- Hold-to-settlement net for same entries: $-43.46
- Exit value added, all resolved exits: $-5.90
- Helpful exits / hurtful exits, all resolved exits: 133 / 348

Matched feature subset:

- Actual matched exit net: $-63.56
- Matched hold-to-settlement net: $-59.22
- Matched exit value added: $-4.34
- Unmatched exit value added: $-1.56

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 159 | $22.78 | $-5.22 | $28.00 | 34/125 |
| `mushroom_v28_probability_collapse_full` | 71 | $-41.46 | $-40.94 | $-0.52 | 39/32 |
| `unmatched_exit_signal` | 36 | $14.20 | $15.76 | $-1.56 | 0/16 |
| `mushroom_v28_probability_reduce` | 235 | $-44.88 | $-13.06 | $-31.82 | 60/175 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 122 (26.24%) | $-48.22 | $15.34 | 93/29 | $-23.52/$-17.58/$-7.12 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 98 (21.08%) | $-52.79 | $10.77 | 50/48 | $-19.07/$-12.04/$-21.68 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (8.17%) | $-60.14 | $3.42 | 28/10 | $-27.06/$-23.48/$-9.60 |
| `suppress_exit_if_p_hold<=0.72` | False | 102 (21.94%) | $-62.58 | $0.98 | 53/49 | $-22.44/$-21.40/$-18.74 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.01%) | $-63.60 | $-0.04 | 10/4 | $-21.42/$-24.12/$-18.06 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 106 (22.80%) | $-69.19 | $-5.63 | 55/51 | $-34.89/$-11.22/$-23.08 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 88 (18.92%) | $-69.97 | $-6.41 | 59/29 | $-24.96/$-21.43/$-23.58 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 142 (30.54%) | $-73.88 | $-10.32 | 117/25 | $-32.60/$-19.46/$-21.82 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 112 (24.09%) | $-80.18 | $-16.62 | 98/14 | $-36.72/$-20.52/$-22.94 |
| `suppress_exit_if_p_hold>=0.8` | False | 102 (21.94%) | $-80.62 | $-17.06 | 89/13 | $-36.64/$-21.04/$-22.94 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (17.63%) | $-81.04 | $-17.48 | 72/10 | $-37.66/$-21.60/$-21.78 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 139 (29.89%) | $-84.30 | $-20.74 | 117/22 | $-38.12/$-19.88/$-26.30 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
