# Live v28 Exit Value Audit

Generated UTC: `20260507_120059Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 469
- Matched to `exit_signal_seen`: 435
- Unmatched resolved exits: 34
- Actual exit net, all resolved exits: $-42.84
- Hold-to-settlement net for same entries: $-39.92
- Exit value added, all resolved exits: $-2.92
- Helpful exits / hurtful exits, all resolved exits: 121 / 328

Matched feature subset:

- Actual matched exit net: $-56.48
- Matched hold-to-settlement net: $-54.84
- Matched exit value added: $-1.64
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 153 | $22.74 | $4.58 | $18.16 | 28/125 |
| `mushroom_v28_probability_collapse_full` | 71 | $-41.46 | $-40.94 | $-0.52 | 39/32 |
| `unmatched_exit_signal` | 34 | $13.64 | $14.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_reduce` | 211 | $-37.76 | $-18.48 | $-19.28 | 54/157 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 120 (27.59%) | $-42.22 | $14.26 | 91/29 | $-20.04/$-20.62/$-1.56 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 94 (21.61%) | $-50.07 | $6.41 | 46/48 | $-18.45/$-12.36/$-19.26 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (8.74%) | $-53.06 | $3.42 | 28/10 | $-22.54/$-24.98/$-5.54 |
| `suppress_exit_if_p_hold<=0.72` | False | 102 (23.45%) | $-55.50 | $0.98 | 53/49 | $-22.86/$-20.68/$-11.96 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.22%) | $-56.52 | $-0.04 | 10/4 | $-18.90/$-26.34/$-11.28 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (17.01%) | $-57.37 | $-0.89 | 53/21 | $-22.44/$-22.85/$-12.08 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 106 (24.37%) | $-62.11 | $-5.63 | 55/51 | $-33.93/$-14.56/$-13.62 |
| `suppress_exit_if_btc_age_ms<=100` | False | 147 (33.79%) | $-62.52 | $-6.04 | 104/43 | $-42.42/$-12.02/$-8.08 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 110 (25.29%) | $-69.66 | $-13.18 | 98/12 | $-34.60/$-23.82/$-11.24 |
| `suppress_exit_if_p_hold>=0.8` | False | 100 (22.99%) | $-70.10 | $-13.62 | 89/11 | $-34.52/$-24.34/$-11.24 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 135 (31.03%) | $-70.54 | $-14.06 | 117/18 | $-36.00/$-23.82/$-10.72 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 136 (31.26%) | $-73.88 | $-17.40 | 111/25 | $-31.44/$-23.00/$-19.44 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (18.85%) | $-73.96 | $-17.48 | 72/10 | $-35.54/$-24.34/$-14.08 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
