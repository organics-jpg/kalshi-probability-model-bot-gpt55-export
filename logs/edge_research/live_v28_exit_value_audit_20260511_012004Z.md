# Live v28 Exit Value Audit

Generated UTC: `20260511_012004Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-59.48
- Hold-to-settlement net for same entries: $-44.26
- Exit value added, all resolved exits: $-15.22
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-59.48
- Matched hold-to-settlement net: $-44.26
- Matched exit value added: $-15.22
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $12.72 | $-0.63 | $13.35 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-32.42 | $-27.53 | $-4.89 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-39.78 | $-16.10 | $-23.68 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-46.59 | $12.89 | 68/21 | $-17.92/$-21.77/$-6.90 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-50.62 | $8.86 | 38/34 | $-15.64/$-17.94/$-17.04 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-55.16 | $4.32 | 42/35 | $-21.30/$-19.91/$-13.95 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-56.08 | $3.40 | 82/34 | $-29.97/$-19.44/$-6.67 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-58.67 | $0.81 | 10/4 | $-21.97/$-22.40/$-14.30 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-59.39 | $0.09 | 21/8 | $-23.84/$-24.43/$-11.12 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-59.45 | $0.03 | 85/18 | $-20.63/$-24.71/$-14.11 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-60.68 | $-1.20 | 45/20 | $-19.82/$-23.91/$-16.95 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-64.23 | $-4.75 | 39/36 | $-32.91/$-17.53/$-13.79 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-65.65 | $-6.17 | 66/9 | $-24.52/$-27.47/$-13.66 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-65.78 | $-6.30 | 73/10 | $-24.23/$-27.16/$-14.39 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-66.98 | $-7.50 | 89/16 | $-27.19/$-25.55/$-14.24 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-67.57 | $-8.09 | 53/7 | $-25.43/$-27.78/$-14.36 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
