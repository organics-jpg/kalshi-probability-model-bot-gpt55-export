# Live v28 Exit Value Audit

Generated UTC: `20260507_030959Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 417
- Matched to `exit_signal_seen`: 385
- Unmatched resolved exits: 32
- Actual exit net, all resolved exits: $-37.16
- Hold-to-settlement net for same entries: $-26.62
- Exit value added, all resolved exits: $-10.54
- Helpful exits / hurtful exits, all resolved exits: 101 / 298

Matched feature subset:

- Actual matched exit net: $-49.80
- Matched hold-to-settlement net: $-40.54
- Matched exit value added: $-9.26
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 135 | $23.66 | $0.58 | $23.08 | 26/109 |
| `unmatched_exit_signal` | 32 | $12.64 | $13.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_collapse_full` | 63 | $-38.26 | $-33.62 | $-4.64 | 33/30 |
| `mushroom_v28_probability_reduce` | 187 | $-35.20 | $-7.50 | $-27.70 | 42/145 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 110 (28.57%) | $-34.96 | $14.84 | 85/25 | $-22.18/$-14.10/$1.32 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 86 (22.34%) | $-39.27 | $10.53 | 44/42 | $-17.19/$-10.28/$-11.80 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (9.87%) | $-46.38 | $3.42 | 28/10 | $-23.58/$-18.88/$-3.92 |
| `suppress_exit_if_p_hold<=0.72` | False | 90 (23.38%) | $-48.46 | $1.34 | 47/43 | $-22.88/$-13.92/$-11.66 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.64%) | $-49.84 | $-0.04 | 10/4 | $-18.30/$-21.88/$-9.66 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (19.22%) | $-50.69 | $-0.89 | 53/21 | $-20.08/$-25.48/$-5.13 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 92 (23.90%) | $-53.69 | $-3.89 | 49/43 | $-33.95/$-10.88/$-8.86 |
| `suppress_exit_if_btc_age_ms<=100` | False | 129 (33.51%) | $-56.64 | $-6.84 | 92/37 | $-35.26/$-15.98/$-5.40 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 128 (33.25%) | $-62.20 | $-12.40 | 107/21 | $-28.24/$-21.56/$-12.40 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 100 (25.97%) | $-65.86 | $-16.06 | 88/12 | $-31.40/$-22.00/$-12.46 |
| `suppress_exit_if_p_hold>=0.8` | False | 90 (23.38%) | $-66.30 | $-16.50 | 79/11 | $-31.32/$-22.52/$-12.46 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 117 (30.39%) | $-66.62 | $-16.82 | 101/16 | $-32.80/$-22.00/$-11.82 |
| `suppress_exit_if_p_hold>=0.85` | False | 76 (19.74%) | $-68.36 | $-18.56 | 66/10 | $-31.82/$-23.04/$-13.50 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
