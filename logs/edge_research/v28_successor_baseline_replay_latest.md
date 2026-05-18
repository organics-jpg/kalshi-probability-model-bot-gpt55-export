# v28 Successor Baseline Replay Audit

Research-only baseline audit. This streamed recorded execution events and seed rows only; live bot code, state, orders, thresholds, and processes were not touched.

## Summary

- Generated UTC: `2026-05-12T07:29:14Z`
- Seed rows: `795` across `176` markets
- Logged v28 events scanned: `4233`
- Matched seed rows to logged v28 outputs: `67`
- Unmatched seed rows: `728`
- Match tolerance seconds: `2.0`
- Verdict: `logged_baseline_audited_true_api_recompute_blocked`

## Seed Source Quality

- Posthoc seed rows: `795`
- Forward-promotion seed rows: `0`

| missing seed field | rows |
|---|---:|
| `strike` | 795 |
| `decision_ts_utc` | 0 |
| `v28_p_yes` | 0 |
| `sigma_t_dollars` | 0 |

## Logged Component Coverage On Matches

| logged field | missing matched rows |
|---|---:|
| `p_anchor` | 67 |
| `p_static_boundary_field` | 67 |
| `p_recent_transport` | 67 |
| `p_long_transport` | 67 |
| `transport_recent_n` | 67 |
| `transport_long_n` | 67 |

## Seed Minus Logged Delta

| field | count | mean abs | max abs |
|---|---:|---:|---:|
| `p_yes` | 67 | 0.02066034 | 0.49582100 |
| `p_side` | 67 | 0.02066034 | 0.49582100 |
| `fair_yes_cents` | 67 | 2.06603127 | 49.58207200 |
| `sigma_t_dollars` | 67 | 4.54589582 | 19.73580100 |
| `ask_cents` | 67 | 0.94029851 | 8.00000000 |
| `edge_cents` | 67 | 2.17188963 | 50.58203400 |

## Blockers

- current seed rows are posthoc calibration rows.
- current seed rows have zero allowed_for_forward_promotion rows.
- seed rows are missing strike.
- true v28 API recomputation requires predecision BTC/bar sequence and serialized engine transport state.

## Read

- A matching logged v28 row is useful baseline evidence, but it is not the same as a true v28 API replay.
- True API replay still needs the exact predecision BTC/bar history and v28 engine state that existed before the row decision.
- This audit keeps the promotion gate closed because the current seed remains posthoc and has no frozen-forward rows.

## Outputs

- Replay audit CSV: `research_particle/v28_successor/v28_baseline_replay_audit_latest.csv`
- Replay audit JSON: `research_particle/v28_successor/v28_baseline_replay_audit_latest.json`
- Machine summary: `logs/edge_research/v28_successor_baseline_replay_latest.json`
