# Live v28 Exit Value Audit

Generated UTC: `20260511_005720Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-60.96
- Hold-to-settlement net for same entries: $-43.74
- Exit value added, all resolved exits: $-17.22
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-60.96
- Matched hold-to-settlement net: $-43.74
- Matched exit value added: $-17.22
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $12.79 | $-0.65 | $13.44 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-32.41 | $-27.15 | $-5.26 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-41.34 | $-15.94 | $-25.40 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-47.13 | $13.83 | 68/21 | $-18.26/$-22.97/$-5.90 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-51.50 | $9.46 | 38/34 | $-16.89/$-18.84/$-15.77 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-56.33 | $4.63 | 42/35 | $-22.63/$-20.96/$-12.74 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-57.32 | $3.64 | 82/34 | $-31.44/$-20.13/$-5.75 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-60.00 | $0.96 | 10/4 | $-23.63/$-23.53/$-12.84 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-60.68 | $0.28 | 85/18 | $-22.09/$-25.71/$-12.88 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-60.72 | $0.24 | 21/8 | $-25.34/$-25.61/$-9.77 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-61.82 | $-0.86 | 45/20 | $-21.34/$-24.93/$-15.55 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-65.62 | $-4.66 | 39/36 | $-34.48/$-18.41/$-12.73 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-67.10 | $-6.14 | 66/9 | $-26.08/$-28.62/$-12.40 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-67.25 | $-6.29 | 73/10 | $-25.76/$-28.36/$-13.13 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-68.38 | $-7.42 | 89/16 | $-28.72/$-26.64/$-13.02 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-69.03 | $-8.07 | 53/7 | $-27.08/$-28.93/$-13.02 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
