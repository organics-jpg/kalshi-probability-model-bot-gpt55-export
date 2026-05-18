# Live v28 Exit Value Audit

Generated UTC: `20260511_024225Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-58.98
- Hold-to-settlement net for same entries: $-43.40
- Exit value added, all resolved exits: $-15.58
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-58.98
- Matched hold-to-settlement net: $-43.40
- Matched exit value added: $-15.58
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $12.96 | $-0.61 | $13.57 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-31.69 | $-26.73 | $-4.96 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-40.25 | $-16.06 | $-24.19 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-45.33 | $13.65 | 68/21 | $-16.24/$-22.81/$-6.28 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-49.90 | $9.08 | 38/34 | $-14.15/$-18.88/$-16.87 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-54.54 | $4.44 | 42/35 | $-19.74/$-21.02/$-13.78 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-56.39 | $2.59 | 82/34 | $-29.50/$-20.26/$-6.63 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-58.02 | $0.96 | 10/4 | $-20.27/$-23.62/$-14.13 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-58.80 | $0.18 | 21/8 | $-22.22/$-25.58/$-11.00 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-59.63 | $-0.65 | 85/18 | $-20.06/$-25.70/$-13.87 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-60.45 | $-1.47 | 45/20 | $-18.57/$-25.04/$-16.84 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-63.12 | $-4.14 | 39/36 | $-31.56/$-18.47/$-13.09 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-65.25 | $-6.27 | 66/9 | $-23.13/$-28.58/$-13.54 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-65.39 | $-6.41 | 73/10 | $-22.85/$-28.27/$-14.27 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-66.76 | $-7.78 | 89/16 | $-26.03/$-26.55/$-14.18 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-67.06 | $-8.08 | 53/7 | $-23.97/$-28.89/$-14.20 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
