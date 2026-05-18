# Live v28 Exit Value Audit

Generated UTC: `20260507_033119Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 425
- Matched to `exit_signal_seen`: 393
- Unmatched resolved exits: 32
- Actual exit net, all resolved exits: $-38.32
- Hold-to-settlement net for same entries: $-22.82
- Exit value added, all resolved exits: $-15.50
- Helpful exits / hurtful exits, all resolved exits: 101 / 306

Matched feature subset:

- Actual matched exit net: $-50.96
- Matched hold-to-settlement net: $-36.74
- Matched exit value added: $-14.22
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 139 | $23.54 | $2.02 | $21.52 | 26/113 |
| `unmatched_exit_signal` | 32 | $12.64 | $13.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_collapse_full` | 63 | $-38.26 | $-33.62 | $-4.64 | 33/30 |
| `mushroom_v28_probability_reduce` | 191 | $-36.24 | $-5.14 | $-31.10 | 42/149 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 114 (29.01%) | $-34.04 | $16.92 | 89/25 | $-23.52/$-13.28/$2.76 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 86 (21.88%) | $-40.43 | $10.53 | 44/42 | $-18.53/$-11.54/$-10.36 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (9.67%) | $-47.54 | $3.42 | 28/10 | $-24.26/$-18.72/$-4.56 |
| `suppress_exit_if_p_hold<=0.72` | False | 92 (23.41%) | $-48.82 | $2.14 | 49/43 | $-24.22/$-15.18/$-9.42 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.56%) | $-51.00 | $-0.04 | 10/4 | $-18.98/$-21.72/$-10.30 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (18.83%) | $-51.85 | $-0.89 | 53/21 | $-20.76/$-27.40/$-3.69 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 94 (23.92%) | $-54.05 | $-3.09 | 51/43 | $-35.29/$-9.06/$-9.70 |
| `suppress_exit_if_btc_age_ms<=100` | False | 133 (33.84%) | $-54.92 | $-3.96 | 96/37 | $-35.94/$-15.82/$-3.16 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 128 (32.57%) | $-63.36 | $-12.40 | 107/21 | $-28.66/$-23.74/$-10.96 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 121 (30.79%) | $-66.22 | $-15.26 | 105/16 | $-33.22/$-22.10/$-10.90 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 100 (25.45%) | $-67.02 | $-16.06 | 88/12 | $-31.82/$-22.10/$-13.10 |
| `suppress_exit_if_p_hold>=0.8` | False | 90 (22.90%) | $-67.46 | $-16.50 | 79/11 | $-31.74/$-22.62/$-13.10 |
| `suppress_exit_if_p_hold>=0.85` | False | 76 (19.34%) | $-69.52 | $-18.56 | 66/10 | $-32.50/$-22.88/$-14.14 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
