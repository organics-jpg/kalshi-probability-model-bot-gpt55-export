# Live v28 Exit Value Audit

Generated UTC: `20260507_062217Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 449
- Matched to `exit_signal_seen`: 415
- Unmatched resolved exits: 34
- Actual exit net, all resolved exits: $-41.24
- Hold-to-settlement net for same entries: $-29.68
- Exit value added, all resolved exits: $-11.56
- Helpful exits / hurtful exits, all resolved exits: 111 / 318

Matched feature subset:

- Actual matched exit net: $-54.88
- Matched hold-to-settlement net: $-44.60
- Matched exit value added: $-10.28
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 147 | $22.50 | $6.10 | $16.40 | 26/121 |
| `mushroom_v28_probability_collapse_full` | 67 | $-40.42 | $-39.26 | $-1.16 | 37/30 |
| `unmatched_exit_signal` | 34 | $13.64 | $14.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_reduce` | 201 | $-36.96 | $-11.44 | $-25.52 | 48/153 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 116 (27.95%) | $-39.34 | $15.54 | 89/27 | $-21.06/$-18.31/$0.03 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 90 (21.69%) | $-47.83 | $7.05 | 44/46 | $-17.35/$-12.17/$-18.31 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (9.16%) | $-51.46 | $3.42 | 28/10 | $-22.04/$-24.19/$-5.23 |
| `suppress_exit_if_p_hold<=0.72` | False | 98 (23.61%) | $-53.26 | $1.62 | 51/47 | $-23.04/$-19.21/$-11.01 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.37%) | $-54.92 | $-0.04 | 10/4 | $-17.80/$-26.15/$-10.97 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (17.83%) | $-55.77 | $-0.89 | 53/21 | $-22.54/$-25.19/$-8.04 |
| `suppress_exit_if_btc_age_ms<=100` | False | 139 (33.49%) | $-57.64 | $-2.76 | 100/39 | $-41.32/$-13.43/$-2.89 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 102 (24.58%) | $-59.87 | $-4.99 | 53/49 | $-34.11/$-13.09/$-12.67 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 129 (31.08%) | $-67.18 | $-12.30 | 113/16 | $-35.14/$-23.39/$-8.65 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 106 (25.54%) | $-68.78 | $-13.90 | 94/12 | $-33.74/$-23.39/$-11.65 |
| `suppress_exit_if_p_hold>=0.8` | False | 96 (23.13%) | $-69.22 | $-14.34 | 85/11 | $-33.66/$-23.91/$-11.65 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 130 (31.33%) | $-70.24 | $-15.36 | 107/23 | $-30.58/$-23.77/$-15.89 |
| `suppress_exit_if_p_hold>=0.85` | False | 78 (18.80%) | $-73.08 | $-18.20 | 68/10 | $-34.68/$-23.91/$-14.49 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
