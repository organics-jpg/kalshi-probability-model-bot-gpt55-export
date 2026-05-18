# Live v28 Exit Value Audit

Generated UTC: `20260511_030934Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-58.06
- Hold-to-settlement net for same entries: $-43.27
- Exit value added, all resolved exits: $-14.79
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-58.06
- Matched hold-to-settlement net: $-43.27
- Matched exit value added: $-14.79
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $13.89 | $-0.59 | $14.48 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-31.53 | $-26.74 | $-4.79 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-40.42 | $-15.94 | $-24.48 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-44.37 | $13.69 | 68/21 | $-14.93/$-23.37/$-6.07 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-48.85 | $9.21 | 38/34 | $-12.57/$-19.57/$-16.71 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-53.78 | $4.28 | 42/35 | $-18.72/$-21.64/$-13.42 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-56.46 | $1.60 | 82/34 | $-29.06/$-20.81/$-6.59 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-57.17 | $0.89 | 10/4 | $-19.02/$-24.31/$-13.84 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-57.85 | $0.21 | 21/8 | $-20.81/$-26.27/$-10.77 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-59.34 | $-1.28 | 45/20 | $-16.94/$-25.72/$-16.68 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-60.02 | $-1.96 | 85/18 | $-19.91/$-26.32/$-13.79 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-62.18 | $-4.12 | 39/36 | $-30.42/$-18.97/$-12.79 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-65.30 | $-7.24 | 66/9 | $-22.87/$-29.27/$-13.16 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-65.51 | $-7.45 | 73/10 | $-22.66/$-28.96/$-13.89 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-66.77 | $-8.71 | 89/16 | $-25.79/$-27.24/$-13.74 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-67.14 | $-9.08 | 53/7 | $-23.70/$-29.58/$-13.86 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
