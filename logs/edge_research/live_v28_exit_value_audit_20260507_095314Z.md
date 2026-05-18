# Live v28 Exit Value Audit

Generated UTC: `20260507_095314Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 455
- Matched to `exit_signal_seen`: 421
- Unmatched resolved exits: 34
- Actual exit net, all resolved exits: $-41.80
- Hold-to-settlement net for same entries: $-34.36
- Exit value added, all resolved exits: $-7.44
- Helpful exits / hurtful exits, all resolved exits: 115 / 320

Matched feature subset:

- Actual matched exit net: $-55.44
- Matched hold-to-settlement net: $-49.28
- Matched exit value added: $-6.16
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 151 | $22.34 | $3.94 | $18.40 | 28/123 |
| `mushroom_v28_probability_collapse_full` | 69 | $-40.82 | $-41.78 | $0.96 | 39/30 |
| `unmatched_exit_signal` | 34 | $13.64 | $14.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_reduce` | 201 | $-36.96 | $-11.44 | $-25.52 | 48/153 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 116 (27.55%) | $-39.90 | $15.54 | 89/27 | $-20.94/$-18.57/$-0.39 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 92 (21.85%) | $-50.51 | $4.93 | 44/48 | $-17.47/$-12.19/$-20.85 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (9.03%) | $-52.02 | $3.42 | 28/10 | $-22.16/$-24.21/$-5.65 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.33%) | $-55.48 | $-0.04 | 10/4 | $-17.92/$-26.17/$-11.39 |
| `suppress_exit_if_p_hold<=0.72` | False | 100 (23.75%) | $-55.94 | $-0.50 | 51/49 | $-23.16/$-19.23/$-13.55 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (17.58%) | $-56.33 | $-0.89 | 53/21 | $-21.46/$-26.41/$-8.46 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 104 (24.70%) | $-62.55 | $-7.11 | 53/51 | $-34.23/$-13.11/$-15.21 |
| `suppress_exit_if_btc_age_ms<=100` | False | 143 (33.97%) | $-62.80 | $-7.36 | 100/43 | $-41.44/$-12.85/$-8.51 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 108 (25.65%) | $-68.86 | $-13.42 | 96/12 | $-33.62/$-23.65/$-11.59 |
| `suppress_exit_if_p_hold>=0.8` | False | 98 (23.28%) | $-69.30 | $-13.86 | 87/11 | $-33.54/$-24.17/$-11.59 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 133 (31.59%) | $-69.74 | $-14.30 | 115/18 | $-35.02/$-23.65/$-11.07 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 132 (31.35%) | $-70.32 | $-14.88 | 109/23 | $-30.46/$-22.83/$-17.03 |
| `suppress_exit_if_p_hold>=0.85` | False | 80 (19.00%) | $-73.16 | $-17.72 | 70/10 | $-34.56/$-24.17/$-14.43 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
