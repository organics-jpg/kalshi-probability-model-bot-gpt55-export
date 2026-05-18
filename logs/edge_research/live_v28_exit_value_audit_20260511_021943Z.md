# Live v28 Exit Value Audit

Generated UTC: `20260511_021943Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-57.79
- Hold-to-settlement net for same entries: $-43.98
- Exit value added, all resolved exits: $-13.81
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-57.79
- Matched hold-to-settlement net: $-43.98
- Matched exit value added: $-13.81
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $13.38 | $-0.63 | $14.01 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-31.51 | $-27.21 | $-4.30 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-39.66 | $-16.14 | $-23.52 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-44.39 | $13.40 | 68/21 | $-16.53/$-22.89/$-4.97 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-49.26 | $8.53 | 38/34 | $-15.32/$-19.51/$-14.43 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-54.22 | $3.57 | 42/35 | $-21.11/$-21.65/$-11.46 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-56.30 | $1.49 | 82/34 | $-30.81/$-20.67/$-4.82 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-57.01 | $0.78 | 10/4 | $-21.72/$-23.79/$-11.50 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-57.43 | $0.36 | 21/8 | $-23.26/$-25.66/$-8.51 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-58.54 | $-0.75 | 85/18 | $-21.05/$-25.87/$-11.62 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-59.68 | $-1.89 | 45/20 | $-19.80/$-25.30/$-14.58 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-62.77 | $-4.98 | 39/36 | $-32.96/$-18.97/$-10.84 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-64.13 | $-6.34 | 66/9 | $-24.24/$-28.74/$-11.15 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-64.14 | $-6.35 | 73/10 | $-23.92/$-28.43/$-11.79 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-65.75 | $-7.96 | 89/16 | $-27.04/$-26.71/$-12.00 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-65.92 | $-8.13 | 53/7 | $-25.19/$-29.05/$-11.68 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
