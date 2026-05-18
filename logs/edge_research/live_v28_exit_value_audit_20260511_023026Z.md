# Live v28 Exit Value Audit

Generated UTC: `20260511_023026Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-60.44
- Hold-to-settlement net for same entries: $-43.74
- Exit value added, all resolved exits: $-16.70
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-60.44
- Matched hold-to-settlement net: $-43.74
- Matched exit value added: $-16.70
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $12.99 | $-0.63 | $13.62 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-31.71 | $-27.09 | $-4.62 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-41.72 | $-16.02 | $-25.70 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-46.13 | $14.31 | 68/21 | $-17.47/$-22.52/$-6.14 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-51.70 | $8.74 | 38/34 | $-16.39/$-18.70/$-16.61 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-56.22 | $4.22 | 42/35 | $-22.00/$-20.70/$-13.52 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-57.22 | $3.22 | 82/34 | $-31.02/$-19.82/$-6.38 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-59.67 | $0.77 | 10/4 | $-22.63/$-23.18/$-13.86 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-60.36 | $0.08 | 21/8 | $-24.42/$-25.19/$-10.75 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-60.53 | $-0.09 | 85/18 | $-21.57/$-25.26/$-13.70 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-61.97 | $-1.53 | 45/20 | $-20.64/$-24.81/$-16.52 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-64.50 | $-4.06 | 39/36 | $-33.64/$-18.03/$-12.83 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-66.72 | $-6.28 | 66/9 | $-25.40/$-28.10/$-13.22 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-66.91 | $-6.47 | 73/10 | $-25.17/$-27.79/$-13.95 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-68.38 | $-7.94 | 89/16 | $-28.18/$-26.27/$-13.93 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-68.43 | $-7.99 | 53/7 | $-26.14/$-28.41/$-13.88 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
