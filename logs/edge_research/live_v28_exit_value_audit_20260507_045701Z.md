# Live v28 Exit Value Audit

Generated UTC: `20260507_045701Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 441
- Matched to `exit_signal_seen`: 407
- Unmatched resolved exits: 34
- Actual exit net, all resolved exits: $-41.28
- Hold-to-settlement net for same entries: $-33.20
- Exit value added, all resolved exits: $-8.08
- Helpful exits / hurtful exits, all resolved exits: 111 / 310

Matched feature subset:

- Actual matched exit net: $-54.92
- Matched hold-to-settlement net: $-48.12
- Matched exit value added: $-6.80
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 143 | $21.90 | $3.94 | $17.96 | 26/117 |
| `mushroom_v28_probability_collapse_full` | 67 | $-40.42 | $-39.26 | $-1.16 | 37/30 |
| `unmatched_exit_signal` | 34 | $13.64 | $14.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_reduce` | 197 | $-36.40 | $-12.80 | $-23.60 | 48/149 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 116 (28.50%) | $-39.38 | $15.54 | 89/27 | $-22.62/$-16.49/$-0.27 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 90 (22.11%) | $-47.87 | $7.05 | 44/46 | $-17.63/$-11.63/$-18.61 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (9.34%) | $-51.50 | $3.42 | 28/10 | $-23.36/$-22.61/$-5.53 |
| `suppress_exit_if_p_hold<=0.72` | False | 98 (24.08%) | $-53.30 | $1.62 | 51/47 | $-23.32/$-18.67/$-11.31 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.44%) | $-54.96 | $-0.04 | 10/4 | $-18.08/$-25.61/$-11.27 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (18.18%) | $-55.81 | $-0.89 | 53/21 | $-22.82/$-26.45/$-6.54 |
| `suppress_exit_if_btc_age_ms<=100` | False | 137 (33.66%) | $-58.88 | $-3.96 | 98/39 | $-41.60/$-14.11/$-3.17 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 102 (25.06%) | $-59.91 | $-4.99 | 53/49 | $-34.39/$-12.55/$-12.97 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 123 (30.22%) | $-69.58 | $-14.66 | 107/16 | $-35.66/$-22.61/$-11.31 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 130 (31.94%) | $-70.28 | $-15.36 | 107/23 | $-31.10/$-23.57/$-15.61 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 102 (25.06%) | $-70.38 | $-15.46 | 90/12 | $-34.26/$-22.61/$-13.51 |
| `suppress_exit_if_p_hold>=0.8` | False | 92 (22.60%) | $-70.82 | $-15.90 | 81/11 | $-34.18/$-23.13/$-13.51 |
| `suppress_exit_if_p_hold>=0.85` | False | 76 (18.67%) | $-73.48 | $-18.56 | 66/10 | $-35.20/$-23.13/$-15.15 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
