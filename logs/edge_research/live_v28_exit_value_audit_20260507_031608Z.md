# Live v28 Exit Value Audit

Generated UTC: `20260507_031608Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 421
- Matched to `exit_signal_seen`: 389
- Unmatched resolved exits: 32
- Actual exit net, all resolved exits: $-37.28
- Hold-to-settlement net for same entries: $-25.18
- Exit value added, all resolved exits: $-12.10
- Helpful exits / hurtful exits, all resolved exits: 101 / 302

Matched feature subset:

- Actual matched exit net: $-49.92
- Matched hold-to-settlement net: $-39.10
- Matched exit value added: $-10.82
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 139 | $23.54 | $2.02 | $21.52 | 26/113 |
| `unmatched_exit_signal` | 32 | $12.64 | $13.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_collapse_full` | 63 | $-38.26 | $-33.62 | $-4.64 | 33/30 |
| `mushroom_v28_probability_reduce` | 187 | $-35.20 | $-7.50 | $-27.70 | 42/145 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 112 (28.79%) | $-34.32 | $15.60 | 87/25 | $-23.78/$-12.90/$2.36 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 86 (22.11%) | $-39.39 | $10.53 | 44/42 | $-18.79/$-9.08/$-11.52 |
| `suppress_exit_if_btc_age_ms>=800` | False | 38 (9.77%) | $-46.50 | $3.42 | 28/10 | $-24.52/$-18.34/$-3.64 |
| `suppress_exit_if_p_hold<=0.72` | False | 92 (23.65%) | $-47.78 | $2.14 | 49/43 | $-24.48/$-12.72/$-10.58 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.60%) | $-49.96 | $-0.04 | 10/4 | $-19.24/$-21.34/$-9.38 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (19.02%) | $-50.81 | $-0.89 | 53/21 | $-21.02/$-24.94/$-4.85 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 94 (24.16%) | $-53.01 | $-3.09 | 51/43 | $-35.55/$-8.68/$-8.78 |
| `suppress_exit_if_btc_age_ms<=100` | False | 131 (33.68%) | $-55.96 | $-6.04 | 94/37 | $-36.20/$-15.44/$-4.32 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 128 (32.90%) | $-62.32 | $-12.40 | 107/21 | $-29.18/$-21.02/$-12.12 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 121 (31.11%) | $-65.18 | $-15.26 | 105/16 | $-33.74/$-21.46/$-9.98 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 100 (25.71%) | $-65.98 | $-16.06 | 88/12 | $-32.34/$-21.46/$-12.18 |
| `suppress_exit_if_p_hold>=0.8` | False | 90 (23.14%) | $-66.42 | $-16.50 | 79/11 | $-32.26/$-21.98/$-12.18 |
| `suppress_exit_if_p_hold>=0.85` | False | 76 (19.54%) | $-68.48 | $-18.56 | 66/10 | $-32.76/$-22.50/$-13.22 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
