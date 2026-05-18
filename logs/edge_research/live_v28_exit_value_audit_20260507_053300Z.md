# Live v28 Exit Value Audit

Generated UTC: `20260507_053300Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 445
- Matched to `exit_signal_seen`: 411
- Unmatched resolved exits: 34
- Actual exit net, all resolved exits: $-40.68
- Hold-to-settlement net for same entries: $-31.04
- Exit value added, all resolved exits: $-9.64
- Helpful exits / hurtful exits, all resolved exits: 111 / 314

Matched feature subset:

- Actual matched exit net: $-54.32
- Matched hold-to-settlement net: $-45.96
- Matched exit value added: $-8.36
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 147 | $22.50 | $6.10 | $16.40 | 26/121 |
| `mushroom_v28_probability_collapse_full` | 67 | $-40.42 | $-39.26 | $-1.16 | 37/30 |
| `unmatched_exit_signal` | 34 | $13.64 | $14.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_reduce` | 197 | $-36.40 | $-12.80 | $-23.60 | 48/149 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 116 (28.22%) | $-38.78 | $15.54 | 89/27 | $-22.20/$-16.96/$0.38 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 90 (21.90%) | $-47.27 | $7.05 | 44/46 | $-17.73/$-11.58/$-17.96 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (9.25%) | $-50.90 | $3.42 | 28/10 | $-22.94/$-23.08/$-4.88 |
| `suppress_exit_if_p_hold<=0.72` | False | 98 (23.84%) | $-52.70 | $1.62 | 51/47 | $-23.42/$-18.62/$-10.66 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.41%) | $-54.36 | $-0.04 | 10/4 | $-18.18/$-25.56/$-10.62 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (18.00%) | $-55.21 | $-0.89 | 53/21 | $-22.92/$-25.50/$-6.79 |
| `suppress_exit_if_btc_age_ms<=100` | False | 139 (33.82%) | $-57.08 | $-2.76 | 100/39 | $-41.70/$-13.16/$-2.22 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 102 (24.82%) | $-59.31 | $-4.99 | 53/49 | $-34.49/$-12.50/$-12.32 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 127 (30.90%) | $-67.42 | $-13.10 | 111/16 | $-35.76/$-22.56/$-9.10 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 106 (25.79%) | $-68.22 | $-13.90 | 94/12 | $-34.36/$-22.56/$-11.30 |
| `suppress_exit_if_p_hold>=0.8` | False | 96 (23.36%) | $-68.66 | $-14.34 | 85/11 | $-34.28/$-23.08/$-11.30 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 130 (31.63%) | $-69.68 | $-15.36 | 107/23 | $-31.20/$-22.94/$-15.54 |
| `suppress_exit_if_p_hold>=0.85` | False | 78 (18.98%) | $-72.52 | $-18.20 | 68/10 | $-35.30/$-23.08/$-14.14 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
