# Live v28 Exit Value Audit

Generated UTC: `20260511_005029Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-60.77
- Hold-to-settlement net for same entries: $-43.32
- Exit value added, all resolved exits: $-17.45
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-60.77
- Matched hold-to-settlement net: $-43.32
- Matched exit value added: $-17.45
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $12.27 | $-0.59 | $12.86 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-31.45 | $-26.71 | $-4.74 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-41.59 | $-16.02 | $-25.57 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-46.53 | $14.24 | 68/21 | $-17.22/$-22.86/$-6.45 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-51.84 | $8.93 | 38/34 | $-16.00/$-19.40/$-16.44 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-56.36 | $4.41 | 42/35 | $-21.47/$-21.54/$-13.35 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-57.44 | $3.33 | 82/34 | $-30.88/$-20.35/$-6.21 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-59.81 | $0.96 | 10/4 | $-22.32/$-23.80/$-13.69 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-60.49 | $0.28 | 21/8 | $-24.22/$-25.76/$-10.51 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-60.76 | $0.01 | 85/18 | $-21.69/$-25.72/$-13.35 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-61.86 | $-1.09 | 45/20 | $-20.42/$-25.16/$-16.28 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-64.88 | $-4.11 | 39/36 | $-33.35/$-18.87/$-12.66 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-66.50 | $-5.73 | 66/9 | $-24.81/$-28.67/$-13.02 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-66.69 | $-5.92 | 73/10 | $-24.58/$-28.36/$-13.75 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-67.91 | $-7.14 | 89/16 | $-27.54/$-26.64/$-13.73 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-68.47 | $-7.70 | 53/7 | $-25.81/$-28.98/$-13.68 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
