# Live v28 Exit Value Audit

Generated UTC: `20260511_015954Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-62.23
- Hold-to-settlement net for same entries: $-43.36
- Exit value added, all resolved exits: $-18.87
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-62.23
- Matched hold-to-settlement net: $-43.36
- Matched exit value added: $-18.87
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $12.57 | $-0.59 | $13.16 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-31.89 | $-26.71 | $-5.18 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-42.91 | $-16.06 | $-26.85 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-47.16 | $15.07 | 68/21 | $-17.42/$-23.00/$-6.74 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-52.84 | $9.39 | 38/34 | $-16.33/$-19.15/$-17.36 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-57.50 | $4.73 | 42/35 | $-21.79/$-21.44/$-14.27 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-58.44 | $3.79 | 82/34 | $-30.93/$-20.49/$-7.02 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-61.20 | $1.03 | 10/4 | $-22.67/$-23.84/$-14.69 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-61.70 | $0.53 | 21/8 | $-24.41/$-25.78/$-11.51 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-62.08 | $0.15 | 85/18 | $-21.57/$-26.13/$-14.38 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-63.38 | $-1.15 | 45/20 | $-20.76/$-25.35/$-17.27 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-65.78 | $-3.55 | 39/36 | $-33.61/$-18.53/$-13.64 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-68.25 | $-6.02 | 66/9 | $-25.35/$-28.89/$-14.01 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-68.40 | $-6.17 | 73/10 | $-25.08/$-28.58/$-14.74 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-69.66 | $-7.43 | 89/16 | $-28.10/$-26.97/$-14.59 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-70.12 | $-7.89 | 53/7 | $-26.21/$-29.20/$-14.71 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
