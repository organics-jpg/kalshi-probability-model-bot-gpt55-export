# Live v28 Exit Value Audit

Generated UTC: `20260511_010925Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-61.76
- Hold-to-settlement net for same entries: $-43.40
- Exit value added, all resolved exits: $-18.36
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-61.76
- Matched hold-to-settlement net: $-43.40
- Matched exit value added: $-18.36
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $12.49 | $-0.65 | $13.14 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-31.93 | $-26.71 | $-5.22 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-42.32 | $-16.04 | $-26.28 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-46.92 | $14.84 | 68/21 | $-17.54/$-22.77/$-6.61 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-52.74 | $9.02 | 38/34 | $-16.42/$-19.20/$-17.12 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-57.04 | $4.72 | 42/35 | $-21.77/$-21.24/$-14.03 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-57.80 | $3.96 | 82/34 | $-30.67/$-20.40/$-6.73 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-60.73 | $1.03 | 10/4 | $-22.73/$-23.62/$-14.38 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-61.26 | $0.50 | 85/18 | $-21.41/$-25.68/$-14.17 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-61.41 | $0.35 | 21/8 | $-24.58/$-25.58/$-11.25 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-62.72 | $-0.96 | 45/20 | $-20.77/$-25.05/$-16.90 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-65.60 | $-3.84 | 39/36 | $-33.65/$-18.61/$-13.34 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-67.82 | $-6.06 | 66/9 | $-25.43/$-28.63/$-13.76 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-67.98 | $-6.22 | 73/10 | $-25.17/$-28.32/$-14.49 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-69.13 | $-7.37 | 89/16 | $-28.13/$-26.60/$-14.40 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-69.56 | $-7.80 | 53/7 | $-26.25/$-28.89/$-14.42 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
