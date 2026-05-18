# Live v28 Exit Value Audit

Generated UTC: `20260508_133153Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 334
- Matched to `exit_signal_seen`: 334
- Unmatched resolved exits: 0
- Actual exit net, all resolved exits: $-37.81
- Hold-to-settlement net for same entries: $-45.58
- Exit value added, all resolved exits: $7.77
- Helpful exits / hurtful exits, all resolved exits: 95 / 239

Matched feature subset:

- Actual matched exit net: $-37.81
- Matched hold-to-settlement net: $-45.58
- Matched exit value added: $7.77
- Unmatched exit value added: $0.00

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 120 | $18.69 | $-0.79 | $19.48 | 25/95 |
| `mushroom_v28_probability_collapse_full` | 53 | $-29.16 | $-28.22 | $-0.94 | 27/26 |
| `mushroom_v28_probability_reduce` | 161 | $-27.34 | $-16.57 | $-10.77 | 43/118 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 89 (26.65%) | $-29.80 | $8.01 | 68/21 | $-6.78/$-19.82/$-3.20 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 72 (21.56%) | $-33.68 | $4.13 | 38/34 | $-5.23/$-16.40/$-12.05 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (4.19%) | $-37.85 | $-0.04 | 10/4 | $-9.76/$-19.60/$-8.49 |
| `suppress_exit_if_p_hold<=0.72` | False | 77 (23.05%) | $-38.79 | $-0.98 | 42/35 | $-10.92/$-19.00/$-8.87 |
| `suppress_exit_if_btc_age_ms>=800` | False | 29 (8.68%) | $-39.03 | $-1.22 | 21/8 | $-11.38/$-21.76/$-5.89 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 65 (19.46%) | $-42.72 | $-4.91 | 45/20 | $-9.06/$-21.78/$-11.88 |
| `suppress_exit_if_btc_age_ms<=100` | False | 116 (34.73%) | $-44.62 | $-6.81 | 82/34 | $-23.56/$-17.95/$-3.11 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 103 (30.84%) | $-44.72 | $-6.91 | 85/18 | $-12.58/$-22.75/$-9.39 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 75 (22.46%) | $-47.39 | $-9.58 | 39/36 | $-22.25/$-16.30/$-8.84 |
| `suppress_exit_if_p_hold>=0.8` | False | 75 (22.46%) | $-47.61 | $-9.80 | 66/9 | $-13.88/$-25.20/$-8.53 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 83 (24.85%) | $-48.07 | $-10.26 | 73/10 | $-13.96/$-24.94/$-9.17 |
| `suppress_exit_if_p_hold>=0.85` | False | 60 (17.96%) | $-48.71 | $-10.90 | 53/7 | $-14.38/$-25.46/$-8.87 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 105 (31.44%) | $-50.53 | $-12.72 | 89/16 | $-17.60/$-23.42/$-9.51 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
