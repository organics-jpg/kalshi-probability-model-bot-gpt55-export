# Live v28 Exit Value Audit

Generated UTC: `20260511_030305Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-58.21
- Hold-to-settlement net for same entries: $-43.44
- Exit value added, all resolved exits: $-14.77
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-58.21
- Matched hold-to-settlement net: $-43.44
- Matched exit value added: $-14.77
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $12.93 | $-0.59 | $13.52 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-31.33 | $-26.77 | $-4.56 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-39.81 | $-16.08 | $-23.73 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-44.00 | $14.21 | 68/21 | $-16.55/$-22.20/$-5.25 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-49.67 | $8.54 | 38/34 | $-15.15/$-18.58/$-15.94 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-54.19 | $4.02 | 42/35 | $-20.72/$-20.79/$-12.68 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-56.20 | $2.01 | 82/34 | $-30.38/$-19.69/$-6.13 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-57.39 | $0.82 | 10/4 | $-21.60/$-22.76/$-13.03 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-57.98 | $0.23 | 21/8 | $-23.34/$-24.79/$-9.85 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-59.30 | $-1.09 | 85/18 | $-21.10/$-24.97/$-13.23 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-59.75 | $-1.54 | 45/20 | $-19.53/$-24.28/$-15.94 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-63.06 | $-4.85 | 39/36 | $-32.60/$-18.24/$-12.22 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-64.46 | $-6.25 | 66/9 | $-24.21/$-27.73/$-12.52 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-64.66 | $-6.45 | 73/10 | $-23.99/$-27.42/$-13.25 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-65.98 | $-7.77 | 89/16 | $-27.06/$-25.70/$-13.22 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-66.12 | $-7.91 | 53/7 | $-24.95/$-28.04/$-13.13 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
