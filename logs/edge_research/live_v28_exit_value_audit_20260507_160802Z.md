# Live v28 Exit Value Audit

Generated UTC: `20260507_160802Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 507
- Matched to `exit_signal_seen`: 469
- Unmatched resolved exits: 38
- Actual exit net, all resolved exits: $-47.08
- Hold-to-settlement net for same entries: $-39.14
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
| `unmatched_exit_signal` | 38 | $16.48 | $18.04 | $-1.56 | 0/16 |
| `mushroom_v28_probability_reduce` | 235 | $-44.88 | $-13.06 | $-31.82 | 60/175 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 122 (26.01%) | $-48.22 | $15.34 | 93/29 | $-24.16/$-15.28/$-8.78 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 98 (20.90%) | $-52.79 | $10.77 | 50/48 | $-19.71/$-11.44/$-21.64 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (8.10%) | $-60.14 | $3.42 | 28/10 | $-27.70/$-22.88/$-9.56 |
| `suppress_exit_if_p_hold<=0.72` | False | 102 (21.75%) | $-62.58 | $0.98 | 53/49 | $-23.08/$-20.80/$-18.70 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (2.99%) | $-63.60 | $-0.04 | 10/4 | $-22.06/$-23.52/$-18.02 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 106 (22.60%) | $-69.19 | $-5.63 | 55/51 | $-36.91/$-8.08/$-24.20 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 88 (18.76%) | $-69.97 | $-6.41 | 59/29 | $-25.60/$-20.83/$-23.54 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 142 (30.28%) | $-73.88 | $-10.32 | 117/25 | $-33.24/$-24.26/$-16.38 |
| `suppress_exit_if_p_hold>=0.8` | False | 104 (22.17%) | $-79.34 | $-15.78 | 91/13 | $-37.28/$-25.84/$-16.22 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 112 (23.88%) | $-80.18 | $-16.62 | 98/14 | $-37.36/$-25.32/$-17.50 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (17.48%) | $-81.04 | $-17.48 | 72/10 | $-38.30/$-26.40/$-16.34 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 143 (30.49%) | $-82.26 | $-18.70 | 121/22 | $-38.76/$-24.68/$-18.82 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
