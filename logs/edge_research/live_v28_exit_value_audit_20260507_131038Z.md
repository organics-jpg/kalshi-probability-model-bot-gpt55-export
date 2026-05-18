# Live v28 Exit Value Audit

Generated UTC: `20260507_131038Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 475
- Matched to `exit_signal_seen`: 441
- Unmatched resolved exits: 34
- Actual exit net, all resolved exits: $-44.56
- Hold-to-settlement net for same entries: $-35.70
- Exit value added, all resolved exits: $-8.86
- Helpful exits / hurtful exits, all resolved exits: 121 / 334

Matched feature subset:

- Actual matched exit net: $-58.20
- Matched hold-to-settlement net: $-50.62
- Matched exit value added: $-7.58
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 153 | $22.74 | $4.58 | $18.16 | 28/125 |
| `mushroom_v28_probability_collapse_full` | 71 | $-41.46 | $-40.94 | $-0.52 | 39/32 |
| `unmatched_exit_signal` | 34 | $13.64 | $14.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_reduce` | 217 | $-39.48 | $-14.26 | $-25.22 | 54/163 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 122 (27.66%) | $-42.86 | $15.34 | 93/29 | $-18.50/$-20.20/$-4.16 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 94 (21.32%) | $-51.79 | $6.41 | 46/48 | $-18.55/$-12.46/$-20.78 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (8.62%) | $-54.78 | $3.42 | 28/10 | $-22.04/$-25.56/$-7.18 |
| `suppress_exit_if_p_hold<=0.72` | False | 102 (23.13%) | $-57.22 | $0.98 | 53/49 | $-21.92/$-21.82/$-13.48 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.17%) | $-58.24 | $-0.04 | 10/4 | $-19.00/$-26.44/$-12.80 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (16.78%) | $-59.09 | $-0.89 | 53/21 | $-22.54/$-20.91/$-15.64 |
| `suppress_exit_if_btc_age_ms<=100` | False | 149 (33.79%) | $-61.14 | $-2.94 | 106/43 | $-42.52/$-12.12/$-6.50 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 106 (24.04%) | $-63.83 | $-5.63 | 55/51 | $-32.99/$-13.66/$-17.18 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 110 (24.94%) | $-71.38 | $-13.18 | 98/12 | $-34.70/$-23.80/$-12.88 |
| `suppress_exit_if_p_hold>=0.8` | False | 100 (22.68%) | $-71.82 | $-13.62 | 89/11 | $-34.62/$-24.32/$-12.88 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 135 (30.61%) | $-72.26 | $-14.06 | 117/18 | $-36.10/$-23.80/$-12.36 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 136 (30.84%) | $-75.60 | $-17.40 | 111/25 | $-31.54/$-22.98/$-21.08 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (18.59%) | $-75.68 | $-17.48 | 72/10 | $-35.64/$-24.32/$-15.72 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
