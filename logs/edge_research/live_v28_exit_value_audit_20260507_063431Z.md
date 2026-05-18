# Live v28 Exit Value Audit

Generated UTC: `20260507_063431Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 451
- Matched to `exit_signal_seen`: 417
- Unmatched resolved exits: 34
- Actual exit net, all resolved exits: $-40.84
- Hold-to-settlement net for same entries: $-28.80
- Exit value added, all resolved exits: $-12.04
- Helpful exits / hurtful exits, all resolved exits: 111 / 320

Matched feature subset:

- Actual matched exit net: $-54.48
- Matched hold-to-settlement net: $-43.72
- Matched exit value added: $-10.76
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 149 | $22.90 | $6.98 | $15.92 | 26/123 |
| `mushroom_v28_probability_collapse_full` | 67 | $-40.42 | $-39.26 | $-1.16 | 37/30 |
| `unmatched_exit_signal` | 34 | $13.64 | $14.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_reduce` | 201 | $-36.96 | $-11.44 | $-25.52 | 48/153 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 116 (27.82%) | $-38.94 | $15.54 | 89/27 | $-20.34/$-19.03/$0.43 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 90 (21.58%) | $-47.43 | $7.05 | 44/46 | $-16.87/$-12.65/$-17.91 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (9.11%) | $-51.06 | $3.42 | 28/10 | $-21.56/$-24.67/$-4.83 |
| `suppress_exit_if_p_hold<=0.72` | False | 98 (23.50%) | $-52.86 | $1.62 | 51/47 | $-22.56/$-19.69/$-10.61 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.36%) | $-54.52 | $-0.04 | 10/4 | $-17.32/$-26.63/$-10.57 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (17.75%) | $-55.37 | $-0.89 | 53/21 | $-22.06/$-25.67/$-7.64 |
| `suppress_exit_if_btc_age_ms<=100` | False | 139 (33.33%) | $-57.24 | $-2.76 | 100/39 | $-40.84/$-13.91/$-2.49 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 102 (24.46%) | $-59.47 | $-4.99 | 53/49 | $-33.63/$-13.57/$-12.27 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 131 (31.41%) | $-66.30 | $-11.82 | 115/16 | $-34.42/$-24.11/$-7.77 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 108 (25.90%) | $-67.90 | $-13.42 | 96/12 | $-33.02/$-24.11/$-10.77 |
| `suppress_exit_if_p_hold>=0.8` | False | 98 (23.50%) | $-68.34 | $-13.86 | 87/11 | $-32.94/$-24.63/$-10.77 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 132 (31.65%) | $-69.36 | $-14.88 | 109/23 | $-29.86/$-23.89/$-15.61 |
| `suppress_exit_if_p_hold>=0.85` | False | 80 (19.18%) | $-72.20 | $-17.72 | 70/10 | $-33.96/$-24.63/$-13.61 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
