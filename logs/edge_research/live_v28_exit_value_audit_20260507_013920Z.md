# Live v28 Exit Value Audit

Generated UTC: `20260507_013920Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 401
- Matched to `exit_signal_seen`: 369
- Unmatched resolved exits: 32
- Actual exit net, all resolved exits: $-34.84
- Hold-to-settlement net for same entries: $-30.74
- Exit value added, all resolved exits: $-4.10
- Helpful exits / hurtful exits, all resolved exits: 99 / 284

Matched feature subset:

- Actual matched exit net: $-47.48
- Matched hold-to-settlement net: $-44.66
- Matched exit value added: $-2.82
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 131 | $22.30 | $-1.42 | $23.72 | 26/105 |
| `unmatched_exit_signal` | 32 | $12.64 | $13.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_collapse_full` | 57 | $-35.76 | $-33.12 | $-2.64 | 31/26 |
| `mushroom_v28_probability_reduce` | 181 | $-34.02 | $-10.12 | $-23.90 | 42/139 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 100 (27.10%) | $-36.16 | $11.32 | 77/23 | $-21.24/$-11.00/$-3.92 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 82 (22.22%) | $-37.63 | $9.85 | 42/40 | $-16.31/$-6.96/$-14.36 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.79%) | $-47.52 | $-0.04 | 10/4 | $-18.08/$-17.82/$-11.62 |
| `suppress_exit_if_p_hold<=0.72` | False | 84 (22.76%) | $-48.14 | $-0.66 | 43/41 | $-22.00/$-8.84/$-17.30 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (20.05%) | $-48.37 | $-0.89 | 53/21 | $-18.36/$-20.12/$-9.89 |
| `suppress_exit_if_btc_age_ms>=800` | False | 32 (8.67%) | $-49.22 | $-1.74 | 22/10 | $-23.36/$-14.82/$-11.04 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 90 (24.39%) | $-49.25 | $-1.77 | 49/41 | $-33.07/$-5.80/$-10.38 |
| `suppress_exit_if_btc_age_ms<=100` | False | 125 (33.88%) | $-56.28 | $-8.80 | 88/37 | $-27.60/$-19.36/$-9.32 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 126 (34.15%) | $-60.04 | $-12.56 | 105/21 | $-20.82/$-24.94/$-14.28 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 96 (26.02%) | $-64.18 | $-16.70 | 84/12 | $-23.98/$-25.90/$-14.30 |
| `suppress_exit_if_p_hold>=0.8` | False | 86 (23.31%) | $-64.62 | $-17.14 | 75/11 | $-23.90/$-25.90/$-14.82 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 113 (30.62%) | $-64.94 | $-17.46 | 97/16 | $-26.82/$-24.46/$-13.66 |
| `suppress_exit_if_p_hold>=0.85` | False | 74 (20.05%) | $-66.20 | $-18.72 | 64/10 | $-24.40/$-26.42/$-15.38 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
