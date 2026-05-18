# Live v28 Exit Value Audit

Generated UTC: `20260511_004317Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-58.64
- Hold-to-settlement net for same entries: $-43.42
- Exit value added, all resolved exits: $-15.22
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-58.64
- Matched hold-to-settlement net: $-43.42
- Matched exit value added: $-15.22
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $12.55 | $-0.57 | $13.12 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-31.72 | $-26.69 | $-5.03 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-39.47 | $-16.16 | $-23.31 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-44.10 | $14.54 | 68/21 | $-16.32/$-21.78/$-6.00 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-49.71 | $8.93 | 38/34 | $-14.99/$-18.18/$-16.54 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-54.18 | $4.46 | 42/35 | $-20.60/$-20.35/$-13.23 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-56.52 | $2.12 | 82/34 | $-30.89/$-19.30/$-6.33 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-57.73 | $0.91 | 10/4 | $-21.67/$-22.48/$-13.58 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-58.45 | $0.19 | 21/8 | $-23.36/$-24.51/$-10.58 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-58.54 | $0.10 | 85/18 | $-20.23/$-24.71/$-13.60 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-59.90 | $-1.26 | 45/20 | $-19.63/$-24.03/$-16.24 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-62.74 | $-4.10 | 39/36 | $-32.44/$-17.76/$-12.54 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-64.61 | $-5.97 | 66/9 | $-24.15/$-27.47/$-12.99 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-64.71 | $-6.07 | 73/10 | $-23.83/$-27.16/$-13.72 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-65.80 | $-7.16 | 89/16 | $-26.79/$-25.44/$-13.57 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-66.53 | $-7.89 | 53/7 | $-25.15/$-27.78/$-13.60 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
