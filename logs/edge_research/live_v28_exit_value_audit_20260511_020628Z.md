# Live v28 Exit Value Audit

Generated UTC: `20260511_020628Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-61.33
- Hold-to-settlement net for same entries: $-43.42
- Exit value added, all resolved exits: $-17.91
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-61.33
- Matched hold-to-settlement net: $-43.42
- Matched exit value added: $-17.91
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $12.36 | $-0.63 | $12.99 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-31.73 | $-26.73 | $-5.00 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-41.96 | $-16.06 | $-25.90 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-47.17 | $14.16 | 68/21 | $-18.43/$-22.88/$-5.86 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-52.20 | $9.13 | 38/34 | $-17.07/$-19.23/$-15.90 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-56.85 | $4.48 | 42/35 | $-22.68/$-21.42/$-12.75 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-57.90 | $3.43 | 82/34 | $-31.45/$-20.55/$-5.90 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-60.37 | $0.96 | 10/4 | $-23.81/$-23.52/$-13.04 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-60.89 | $0.44 | 85/18 | $-22.30/$-25.60/$-12.99 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-61.03 | $0.30 | 21/8 | $-25.48/$-25.63/$-9.92 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-62.37 | $-1.04 | 45/20 | $-21.59/$-24.96/$-15.82 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-65.49 | $-4.16 | 39/36 | $-34.53/$-18.80/$-12.16 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-67.12 | $-5.79 | 66/9 | $-26.29/$-28.47/$-12.36 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-67.22 | $-5.89 | 73/10 | $-25.97/$-28.16/$-13.09 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-68.35 | $-7.02 | 89/16 | $-28.93/$-26.44/$-12.98 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-69.13 | $-7.80 | 53/7 | $-27.29/$-28.78/$-13.06 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
