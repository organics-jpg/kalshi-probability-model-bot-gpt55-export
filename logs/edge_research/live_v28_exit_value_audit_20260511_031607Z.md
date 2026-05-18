# Live v28 Exit Value Audit

Generated UTC: `20260511_031607Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-57.64
- Hold-to-settlement net for same entries: $-43.44
- Exit value added, all resolved exits: $-14.20
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-57.64
- Matched hold-to-settlement net: $-43.44
- Matched exit value added: $-14.20
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $14.45 | $-0.65 | $15.10 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-31.29 | $-26.71 | $-4.58 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-40.80 | $-16.08 | $-24.72 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-44.31 | $13.33 | 68/21 | $-15.16/$-22.93/$-6.22 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-49.16 | $8.48 | 38/34 | $-13.23/$-19.20/$-16.73 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-53.81 | $3.83 | 42/35 | $-18.92/$-21.30/$-13.59 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-55.56 | $2.08 | 82/34 | $-28.78/$-20.24/$-6.54 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-56.73 | $0.91 | 10/4 | $-19.15/$-23.64/$-13.94 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-57.49 | $0.15 | 21/8 | $-20.93/$-25.75/$-10.81 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-58.75 | $-1.11 | 85/18 | $-19.21/$-25.81/$-13.73 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-58.93 | $-1.29 | 45/20 | $-17.14/$-25.27/$-16.52 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-62.24 | $-4.60 | 39/36 | $-30.63/$-18.59/$-13.02 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-65.16 | $-7.52 | 66/9 | $-23.17/$-28.64/$-13.35 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-65.35 | $-7.71 | 73/10 | $-22.94/$-28.33/$-14.08 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-66.67 | $-9.03 | 89/16 | $-26.13/$-26.61/$-13.93 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-66.84 | $-9.20 | 53/7 | $-23.88/$-28.95/$-14.01 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
