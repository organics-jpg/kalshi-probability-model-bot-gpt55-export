# Live v28 Exit Value Audit

Generated UTC: `20260507_163221Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 515
- Matched to `exit_signal_seen`: 477
- Unmatched resolved exits: 38
- Actual exit net, all resolved exits: $-48.78
- Hold-to-settlement net for same entries: $-35.88
- Exit value added, all resolved exits: $-12.90
- Helpful exits / hurtful exits, all resolved exits: 133 / 360

Matched feature subset:

- Actual matched exit net: $-65.26
- Matched hold-to-settlement net: $-53.92
- Matched exit value added: $-11.34
- Unmatched exit value added: $-1.56

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 165 | $22.34 | $-2.62 | $24.96 | 34/131 |
| `unmatched_exit_signal` | 38 | $16.48 | $18.04 | $-1.56 | 0/16 |
| `mushroom_v28_probability_collapse_full` | 73 | $-42.18 | $-40.34 | $-1.84 | 39/34 |
| `mushroom_v28_probability_reduce` | 239 | $-45.42 | $-10.96 | $-34.46 | 60/179 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 124 (26.00%) | $-48.60 | $16.66 | 95/29 | $-22.56/$-15.64/$-10.40 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 98 (20.55%) | $-54.49 | $10.77 | 50/48 | $-19.39/$-10.52/$-24.58 |
| `suppress_exit_if_btc_age_ms>=800` | False | 40 (8.39%) | $-60.52 | $4.74 | 30/10 | $-27.38/$-21.96/$-11.18 |
| `suppress_exit_if_p_hold<=0.72` | False | 104 (21.80%) | $-62.96 | $2.30 | 55/49 | $-22.76/$-21.98/$-18.22 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (2.94%) | $-65.30 | $-0.04 | 10/4 | $-21.74/$-24.70/$-18.86 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 110 (23.06%) | $-68.57 | $-3.31 | 59/51 | $-36.59/$-9.26/$-22.72 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 88 (18.45%) | $-71.67 | $-6.41 | 59/29 | $-25.28/$-22.01/$-24.38 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 142 (29.77%) | $-75.58 | $-10.32 | 117/25 | $-32.68/$-24.52/$-18.38 |
| `suppress_exit_if_p_hold>=0.8` | False | 104 (21.80%) | $-81.04 | $-15.78 | 91/13 | $-36.72/$-27.26/$-17.06 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 112 (23.48%) | $-81.88 | $-16.62 | 98/14 | $-36.80/$-26.74/$-18.34 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (17.19%) | $-82.74 | $-17.48 | 72/10 | $-37.74/$-27.82/$-17.18 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 143 (29.98%) | $-83.96 | $-18.70 | 121/22 | $-38.20/$-26.10/$-19.66 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
