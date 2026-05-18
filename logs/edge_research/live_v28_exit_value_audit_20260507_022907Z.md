# Live v28 Exit Value Audit

Generated UTC: `20260507_022907Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 407
- Matched to `exit_signal_seen`: 375
- Unmatched resolved exits: 32
- Actual exit net, all resolved exits: $-34.98
- Hold-to-settlement net for same entries: $-26.60
- Exit value added, all resolved exits: $-8.38
- Helpful exits / hurtful exits, all resolved exits: 99 / 290

Matched feature subset:

- Actual matched exit net: $-47.62
- Matched hold-to-settlement net: $-40.52
- Matched exit value added: $-7.10
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 133 | $23.50 | $-0.06 | $23.56 | 26/107 |
| `unmatched_exit_signal` | 32 | $12.64 | $13.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_collapse_full` | 61 | $-37.10 | $-30.34 | $-6.76 | 31/30 |
| `mushroom_v28_probability_reduce` | 181 | $-34.02 | $-10.12 | $-23.90 | 42/139 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 104 (27.73%) | $-32.18 | $15.44 | 81/23 | $-21.86/$-10.08/$-0.24 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 84 (22.40%) | $-34.97 | $12.65 | 44/40 | $-16.87/$-6.98/$-11.12 |
| `suppress_exit_if_p_hold<=0.72` | False | 88 (23.47%) | $-44.16 | $3.46 | 47/41 | $-22.56/$-8.86/$-12.74 |
| `suppress_exit_if_btc_age_ms>=800` | False | 36 (9.60%) | $-45.24 | $2.38 | 26/10 | $-23.92/$-14.20/$-7.12 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.73%) | $-47.66 | $-0.04 | 10/4 | $-18.64/$-17.20/$-11.82 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (19.73%) | $-48.51 | $-0.89 | 53/21 | $-20.42/$-18.00/$-10.09 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 90 (24.00%) | $-49.39 | $-1.77 | 49/41 | $-33.63/$-5.82/$-9.94 |
| `suppress_exit_if_btc_age_ms<=100` | False | 127 (33.87%) | $-56.26 | $-8.64 | 90/37 | $-28.16/$-18.74/$-9.36 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 128 (34.13%) | $-60.02 | $-12.40 | 107/21 | $-21.38/$-24.08/$-14.56 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 98 (26.13%) | $-64.16 | $-16.54 | 86/12 | $-24.54/$-24.52/$-15.10 |
| `suppress_exit_if_p_hold>=0.8` | False | 88 (23.47%) | $-64.60 | $-16.98 | 77/11 | $-24.46/$-25.04/$-15.10 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 115 (30.67%) | $-64.92 | $-17.30 | 99/16 | $-25.94/$-24.52/$-14.46 |
| `suppress_exit_if_p_hold>=0.85` | False | 76 (20.27%) | $-66.18 | $-18.56 | 66/10 | $-24.96/$-25.56/$-15.66 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
