# Live v28 Exit Value Audit

Generated UTC: `20260508_020145Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 483
- Matched to `exit_signal_seen`: 483
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-66.30
- Hold-to-settlement net for same entries: $-48.60
- Exit value added, all resolved exits: $-17.70
- Helpful exits / hurtful exits, all resolved exits: 133 / 350

Matched feature subset:

- Actual matched exit net: $-66.30
- Matched hold-to-settlement net: $-48.60
- Matched exit value added: $-17.70
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 167 | $23.02 | $-1.70 | $24.72 | 34/133 |
| `mushroom_v28_probability_collapse_full` | 73 | $-42.18 | $-40.34 | $-1.84 | 39/34 |
| `mushroom_v28_probability_reduce` | 243 | $-47.14 | $-6.56 | $-40.58 | 60/183 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 128 (26.50%) | $-48.40 | $17.90 | 99/29 | $-23.86/$-11.92/$-12.62 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 98 (20.29%) | $-54.75 | $11.55 | 50/48 | $-20.69/$-9.92/$-24.14 |
| `suppress_exit_if_btc_age_ms>=800` | False | 42 (8.70%) | $-61.32 | $4.98 | 32/10 | $-28.68/$-20.16/$-12.48 |
| `suppress_exit_if_p_hold<=0.72` | False | 104 (21.53%) | $-64.00 | $2.30 | 55/49 | $-24.06/$-21.38/$-18.56 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (2.90%) | $-66.34 | $-0.04 | 10/4 | $-23.04/$-24.10/$-19.20 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 110 (22.77%) | $-69.61 | $-3.31 | 59/51 | $-37.89/$-8.66/$-23.06 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 88 (18.22%) | $-70.73 | $-4.43 | 59/29 | $-25.38/$-21.41/$-23.94 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 144 (29.81%) | $-75.30 | $-9.00 | 119/25 | $-33.98/$-21.30/$-20.02 |
| `suppress_exit_if_p_hold>=0.8` | False | 106 (21.95%) | $-81.84 | $-15.54 | 93/13 | $-38.02/$-26.46/$-17.36 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 114 (23.60%) | $-82.68 | $-16.38 | 100/14 | $-38.10/$-25.94/$-18.64 |
| `suppress_exit_if_p_hold>=0.85` | False | 84 (17.39%) | $-83.54 | $-17.24 | 74/10 | $-39.04/$-27.02/$-17.48 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 145 (30.02%) | $-84.76 | $-18.46 | 123/22 | $-39.50/$-25.30/$-19.96 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
