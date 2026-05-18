# Live v28 Exit Value Audit

Generated UTC: `20260507_042047Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 437
- Matched to `exit_signal_seen`: 403
- Unmatched resolved exits: 34
- Actual exit net, all resolved exits: $-39.64
- Hold-to-settlement net for same entries: $-35.12
- Exit value added, all resolved exits: $-4.52
- Helpful exits / hurtful exits, all resolved exits: 111 / 306

Matched feature subset:

- Actual matched exit net: $-53.28
- Matched hold-to-settlement net: $-50.04
- Matched exit value added: $-3.24
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 139 | $23.54 | $2.02 | $21.52 | 26/113 |
| `mushroom_v28_probability_collapse_full` | 67 | $-40.42 | $-39.26 | $-1.16 | 37/30 |
| `unmatched_exit_signal` | 34 | $13.64 | $14.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_reduce` | 197 | $-36.40 | $-12.80 | $-23.60 | 48/149 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 116 (28.78%) | $-37.74 | $15.54 | 89/27 | $-22.90/$-15.91/$1.07 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 90 (22.33%) | $-46.23 | $7.05 | 44/46 | $-17.91/$-12.25/$-16.07 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (9.43%) | $-49.86 | $3.42 | 28/10 | $-23.64/$-22.03/$-4.19 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.47%) | $-53.32 | $-0.04 | 10/4 | $-18.36/$-25.03/$-9.93 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (18.36%) | $-54.17 | $-0.89 | 53/21 | $-23.10/$-27.07/$-4.00 |
| `suppress_exit_if_p_hold<=0.72` | False | 96 (23.82%) | $-54.62 | $-1.34 | 49/47 | $-23.60/$-18.09/$-12.93 |
| `suppress_exit_if_btc_age_ms<=100` | False | 135 (33.50%) | $-60.20 | $-6.92 | 96/39 | $-41.94/$-14.69/$-3.57 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 100 (24.81%) | $-61.23 | $-7.95 | 51/49 | $-34.67/$-11.97/$-14.59 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 121 (30.02%) | $-68.54 | $-15.26 | 105/16 | $-36.00/$-21.99/$-10.55 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 130 (32.26%) | $-68.64 | $-15.36 | 107/23 | $-31.44/$-22.95/$-14.25 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 100 (24.81%) | $-69.34 | $-16.06 | 88/12 | $-34.60/$-21.99/$-12.75 |
| `suppress_exit_if_p_hold>=0.8` | False | 90 (22.33%) | $-69.78 | $-16.50 | 79/11 | $-34.52/$-22.51/$-12.75 |
| `suppress_exit_if_p_hold>=0.85` | False | 76 (18.86%) | $-71.84 | $-18.56 | 66/10 | $-35.54/$-22.51/$-13.79 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
