# Live v28 Exit Value Audit

Generated UTC: `20260507_154449Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 505
- Matched to `exit_signal_seen`: 469
- Unmatched resolved exits: 36
- Actual exit net, all resolved exits: $-49.36
- Hold-to-settlement net for same entries: $-41.42
- Exit value added, all resolved exits: $-7.94
- Helpful exits / hurtful exits, all resolved exits: 133 / 352

Matched feature subset:

- Actual matched exit net: $-63.56
- Matched hold-to-settlement net: $-57.18
- Matched exit value added: $-6.38
- Unmatched exit value added: $-1.56

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 163 | $22.78 | $-3.18 | $25.96 | 34/129 |
| `mushroom_v28_probability_collapse_full` | 71 | $-41.46 | $-40.94 | $-0.52 | 39/32 |
| `unmatched_exit_signal` | 36 | $14.20 | $15.76 | $-1.56 | 0/16 |
| `mushroom_v28_probability_reduce` | 235 | $-44.88 | $-13.06 | $-31.82 | 60/175 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 122 (26.01%) | $-48.22 | $15.34 | 93/29 | $-23.98/$-16.28/$-7.96 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 98 (20.90%) | $-52.79 | $10.77 | 50/48 | $-19.53/$-12.44/$-20.82 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (8.10%) | $-60.14 | $3.42 | 28/10 | $-27.52/$-23.88/$-8.74 |
| `suppress_exit_if_p_hold<=0.72` | False | 102 (21.75%) | $-62.58 | $0.98 | 53/49 | $-22.90/$-21.80/$-17.88 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (2.99%) | $-63.60 | $-0.04 | 10/4 | $-21.88/$-24.52/$-17.20 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 106 (22.60%) | $-69.19 | $-5.63 | 55/51 | $-36.73/$-9.08/$-23.38 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 88 (18.76%) | $-69.97 | $-6.41 | 59/29 | $-25.42/$-21.83/$-22.72 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 142 (30.28%) | $-73.88 | $-10.32 | 117/25 | $-33.06/$-19.86/$-20.96 |
| `suppress_exit_if_p_hold>=0.8` | False | 104 (22.17%) | $-79.34 | $-15.78 | 91/13 | $-37.10/$-21.44/$-20.80 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 112 (23.88%) | $-80.18 | $-16.62 | 98/14 | $-37.18/$-20.92/$-22.08 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (17.48%) | $-81.04 | $-17.48 | 72/10 | $-38.12/$-22.00/$-20.92 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 143 (30.49%) | $-82.26 | $-18.70 | 121/22 | $-38.58/$-20.28/$-23.40 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
