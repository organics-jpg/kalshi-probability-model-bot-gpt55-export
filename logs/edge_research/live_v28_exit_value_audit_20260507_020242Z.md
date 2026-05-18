# Live v28 Exit Value Audit

Generated UTC: `20260507_020242Z`

## Scope

- Research-only audit of current live v28 exits versus holding the same entries to settlement.
- Suppression rules are diagnostic only; the replay cannot model position interactions after a skipped exit.
- No live bot files or processes are touched and no orders are submitted.

## Baseline Exit Value

- Resolved exits: 403
- Matched to `exit_signal_seen`: 371
- Unmatched resolved exits: 32
- Actual exit net, all resolved exits: $-33.64
- Hold-to-settlement net for same entries: $-29.38
- Exit value added, all resolved exits: $-4.26
- Helpful exits / hurtful exits, all resolved exits: 99 / 286

Matched feature subset:

- Actual matched exit net: $-46.28
- Matched hold-to-settlement net: $-43.30
- Matched exit value added: $-2.98
- Unmatched exit value added: $-1.28

## By Exit Reason

| reason | n | actual | hold | delta | helped/hurt |
|---|---:|---:|---:|---:|---:|
| `mushroom_v28_exit_value_over_hold` | 133 | $23.50 | $-0.06 | $23.56 | 26/107 |
| `unmatched_exit_signal` | 32 | $12.64 | $13.92 | $-1.28 | 0/14 |
| `mushroom_v28_probability_collapse_full` | 57 | $-35.76 | $-33.12 | $-2.64 | 31/26 |
| `mushroom_v28_probability_reduce` | 181 | $-34.02 | $-10.12 | $-23.90 | 42/139 |

## Suppress-Exit Diagnostics

- Diagnostics below only apply to matched feature rows.

| rule | strict | suppressed | adjusted net | delta | hurtful/helpful suppressed | train/val/holdout adjusted |
|---|---:|---:|---:|---:|---:|---:|
| `suppress_exit_if_btc_age_ms>=500` | False | 100 (26.95%) | $-34.96 | $11.32 | 77/23 | $-22.90/$-8.98/$-3.08 |
| `suppress_exit_if_exit_bid_cents<=65` | False | 82 (22.10%) | $-36.43 | $9.85 | 42/40 | $-16.47/$-6.44/$-13.52 |
| `suppress_exit_if_sigma_t_dollars>=150` | False | 14 (3.77%) | $-46.32 | $-0.04 | 10/4 | $-18.24/$-17.30/$-10.78 |
| `suppress_exit_if_p_hold<=0.72` | False | 84 (22.64%) | $-46.94 | $-0.66 | 43/41 | $-22.16/$-8.32/$-16.46 |
| `suppress_exit_if_sigma_t_dollars>=100` | False | 74 (19.95%) | $-47.17 | $-0.89 | 53/21 | $-20.02/$-18.10/$-9.05 |
| `suppress_exit_if_btc_age_ms>=800` | False | 32 (8.63%) | $-48.02 | $-1.74 | 22/10 | $-23.52/$-14.30/$-10.20 |
| `suppress_exit_if_fair_drawdown_cents>=8` | False | 90 (24.26%) | $-48.05 | $-1.77 | 49/41 | $-33.23/$-5.28/$-9.54 |
| `suppress_exit_if_btc_age_ms<=100` | False | 127 (34.23%) | $-54.92 | $-8.64 | 90/37 | $-27.76/$-18.84/$-8.32 |
| `suppress_exit_if_fair_drawdown_cents<=-2` | False | 128 (34.50%) | $-58.68 | $-12.40 | 107/21 | $-20.98/$-24.42/$-13.28 |
| `suppress_exit_if_exit_bid_cents>=85` | False | 98 (26.42%) | $-62.82 | $-16.54 | 86/12 | $-24.14/$-24.86/$-13.82 |
| `suppress_exit_if_p_hold>=0.8` | False | 88 (23.72%) | $-63.26 | $-16.98 | 77/11 | $-24.06/$-25.38/$-13.82 |
| `suppress_exit_if_exit_bid_cents>=80` | False | 115 (31.00%) | $-63.58 | $-17.30 | 99/16 | $-26.98/$-23.42/$-13.18 |
| `suppress_exit_if_p_hold>=0.85` | False | 76 (20.49%) | $-64.84 | $-18.56 | 66/10 | $-24.56/$-25.90/$-14.38 |

## Read

- The current exit engine is adding material value versus passive holding after all resolved exits are included.
- No matched-feature suppression rule passes the split gates after the scorer causality fix.
- Low exit bids and stale BTC ticks remain diagnostic pockets, but they are not promotion evidence without future forward registration.
- Unmatched heartbeat-confirmed exits are now small after stale pre-entry exit signals are rejected by the scorer, but they remain tracked separately.
