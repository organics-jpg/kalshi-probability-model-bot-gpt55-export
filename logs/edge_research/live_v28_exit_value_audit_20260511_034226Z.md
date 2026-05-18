# Live v28 Exit Value Audit

Generated UTC: `20260511_034226Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-59.13
- Hold-to-settlement net for same entries: $-43.60
- Exit value added, all resolved exits: $-15.53
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-59.13
- Matched hold-to-settlement net: $-43.60
- Matched exit value added: $-15.53
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $12.82 | $-0.79 | $13.61 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-31.28 | $-26.73 | $-4.55 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-40.67 | $-16.08 | $-24.59 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-44.80 | $14.33 | 68/21 | $-16.19/$-22.18/$-6.43 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-50.39 | $8.74 | 38/34 | $-14.65/$-18.84/$-16.90 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-55.19 | $3.94 | 42/35 | $-20.45/$-20.93/$-13.81 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-57.32 | $1.81 | 82/34 | $-30.88/$-19.83/$-6.61 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-58.21 | $0.92 | 10/4 | $-21.24/$-22.81/$-14.16 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-58.86 | $0.27 | 21/8 | $-23.06/$-24.82/$-10.98 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-60.23 | $-1.10 | 45/20 | $-19.17/$-24.31/$-16.75 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-60.57 | $-1.44 | 85/18 | $-21.62/$-25.01/$-13.94 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-63.93 | $-4.80 | 39/36 | $-32.30/$-18.34/$-13.29 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-65.41 | $-6.28 | 66/9 | $-23.96/$-27.80/$-13.65 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-65.54 | $-6.41 | 73/10 | $-23.67/$-27.49/$-14.38 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-66.69 | $-7.56 | 89/16 | $-26.63/$-25.77/$-14.29 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-67.17 | $-8.04 | 53/7 | $-24.79/$-28.11/$-14.27 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
