# Live v28 Exit Value Audit

Generated UTC: `20260507_143730Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 493
- Matched to `exit_signal_seen`: 457
- Unmatched resolved exits: 36
- Actual exit net, all resolved exits: $-48.08
- Hold-to-settlement net for same entries: $-35.14
- Exit value added, all resolved exits: $-12.94
- Helpful exits / hurtful exits, all resolved exits: 127 / 346

Matched feature subset:

- Actual matched exit net: $-62.28
- Matched hold-to-settlement net: $-50.90
- Matched exit value added: $-11.38
- Unmatched exit value added: $-1.56

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 155 | $22.78 | $1.46 | $21.32 | 30/125 |
| `mushroom_v28_probability_collapse_full` | 71 | $-41.46 | $-40.94 | $-0.52 | 39/32 |
| `unmatched_exit_signal` | 36 | $14.20 | $15.76 | $-1.56 | 0/16 |
| `mushroom_v28_probability_reduce` | 231 | $-43.60 | $-11.42 | $-32.18 | 58/173 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 122 (26.70%) | $-46.94 | $15.34 | 93/29 | $-23.58/$-18.06/$-5.30 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 98 (21.44%) | $-51.51 | $10.77 | 50/48 | $-19.13/$-11.98/$-20.40 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (8.32%) | $-58.86 | $3.42 | 28/10 | $-27.12/$-23.42/$-8.32 |
| `suppress_exit_if_p_hold<=0.72` | False | 102 (22.32%) | $-61.30 | $0.98 | 53/49 | $-22.50/$-21.34/$-17.46 |
| `suppress_exit_if_btc_age_ms<=100` | False | 159 (34.79%) | $-62.18 | $0.10 | 112/47 | $-40.50/$-13.80/$-7.88 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.06%) | $-62.32 | $-0.04 | 10/4 | $-21.48/$-24.06/$-16.78 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 106 (23.19%) | $-67.91 | $-5.63 | 55/51 | $-33.57/$-12.54/$-21.80 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 84 (18.38%) | $-68.33 | $-6.05 | 57/27 | $-25.02/$-21.37/$-21.94 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 140 (30.63%) | $-75.32 | $-13.04 | 115/25 | $-32.94/$-20.04/$-22.34 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 110 (24.07%) | $-75.46 | $-13.18 | 98/12 | $-37.06/$-21.10/$-17.30 |
| `suppress_exit_if_p_hold>=0.8` | False | 100 (21.88%) | $-75.90 | $-13.62 | 89/11 | $-36.98/$-21.62/$-17.30 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 135 (29.54%) | $-76.34 | $-14.06 | 117/18 | $-38.46/$-20.46/$-17.42 |
| `suppress_exit_if_p_hold>=0.85` | False | 82 (17.94%) | $-79.76 | $-17.48 | 72/10 | $-38.00/$-21.90/$-19.86 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
