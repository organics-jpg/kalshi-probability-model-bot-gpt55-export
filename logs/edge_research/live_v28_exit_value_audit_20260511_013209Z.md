# Live v28 Exit Value Audit

Generated UTC: `20260511_013209Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-61.49
- Hold-to-settlement net for same entries: $-43.66
- Exit value added, all resolved exits: $-17.83
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-61.49
- Matched hold-to-settlement net: $-43.66
- Matched exit value added: $-17.83
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $12.49 | $-0.61 | $13.10 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-32.19 | $-27.07 | $-5.12 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-41.79 | $-15.98 | $-25.81 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-46.95 | $14.54 | 68/21 | $-17.75/$-22.65/$-6.55 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-52.55 | $8.94 | 38/34 | $-16.68/$-18.96/$-16.91 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-56.96 | $4.53 | 42/35 | $-22.27/$-20.92/$-13.77 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-57.69 | $3.80 | 82/34 | $-30.99/$-20.05/$-6.65 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-60.46 | $1.03 | 10/4 | $-22.82/$-23.45/$-14.19 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-61.18 | $0.31 | 21/8 | $-24.64/$-25.48/$-11.06 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-61.19 | $0.30 | 85/18 | $-21.67/$-25.45/$-14.07 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-62.79 | $-1.30 | 45/20 | $-21.04/$-25.04/$-16.71 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-65.37 | $-3.88 | 39/36 | $-33.87/$-18.25/$-13.25 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-67.42 | $-5.93 | 66/9 | $-25.49/$-28.36/$-13.57 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-67.58 | $-6.09 | 73/10 | $-25.23/$-28.05/$-14.30 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-68.67 | $-7.18 | 89/16 | $-28.19/$-26.33/$-14.15 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-69.29 | $-7.80 | 53/7 | $-26.35/$-28.67/$-14.27 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
