# Live v28 Exit Value Audit

Generated UTC: `20260511_032859Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-57.82
- Hold-to-settlement net for same entries: $-43.98
- Exit value added, all resolved exits: $-13.84
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-57.82
- Matched hold-to-settlement net: $-43.98
- Matched exit value added: $-13.84
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $13.53 | $-0.71 | $14.24 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-32.15 | $-27.13 | $-5.02 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-39.20 | $-16.14 | $-23.06 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-43.64 | $14.18 | 68/21 | $-14.82/$-22.97/$-5.85 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-48.51 | $9.31 | 38/34 | $-12.94/$-19.12/$-16.45 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-53.52 | $4.30 | 42/35 | $-18.59/$-21.45/$-13.48 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-57.25 | $0.57 | 10/4 | $-19.64/$-23.90/$-13.71 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-57.32 | $0.50 | 82/34 | $-30.19/$-20.41/$-6.72 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-57.88 | $-0.06 | 21/8 | $-21.47/$-25.80/$-10.61 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-58.86 | $-1.04 | 85/18 | $-19.22/$-26.04/$-13.60 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-59.62 | $-1.80 | 45/20 | $-17.95/$-25.26/$-16.41 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-61.73 | $-3.91 | 39/36 | $-30.20/$-18.74/$-12.79 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-64.51 | $-6.69 | 66/9 | $-22.39/$-28.84/$-13.28 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-64.57 | $-6.75 | 73/10 | $-22.12/$-28.53/$-13.92 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-65.91 | $-8.09 | 89/16 | $-25.18/$-26.81/$-13.92 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-66.22 | $-8.40 | 53/7 | $-23.22/$-29.15/$-13.85 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
