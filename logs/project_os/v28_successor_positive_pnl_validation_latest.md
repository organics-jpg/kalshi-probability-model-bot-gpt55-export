# v28 Successor Positive-PnL Validation

Generated: 2026-05-18

Scope: research-only validation of v28_successor positive-PnL candidates. This did not touch live bot logic, order logic, scorer thresholds, secrets, live trading state, positions, or the 8501 dashboard.

## Verdict

One v28 successor research candidate cleared the strict promotion verifier:

- Candidate: `v28s_boundary_monotonic_time_safe_v001`
- Variant: `logged_events_diagnostic`
- Model hash: `9b461a310d06c06b55af2e2d`
- Verifier verdict: `promotable`
- Passed gates: holdout coverage, Brier better than v28, logloss better than v28, boundary Brier not degraded, recross Brier not degraded, shadow economics reported, source-quality forward registered, source contract promotion ready, frozen forward registry present, forward market coverage, forward evidence scored/promotable, candidate manifest frozen/inspectable.

One live-PnL policy reached bootstrap/live-shadow readiness but not controlled live-order readiness:

- Policy: `v28s_live_pnl_midband_no_fade_yes_v019`
- Policy hash: `5bf8d66dbe2b31e01d38abe8a0238e68`
- Readiness: `level_1_bootstrap_complete`
- Primary post-hash evidence: `314` paired rows, `12` markets, `3` entries
- Primary PnL: `+70.0c`
- Delta vs regular v28 on identical rows: `+762.3c`
- Level 2 controlled-live-test ready: `False`

Practical conclusion: the strongest path is not the PSLICE sidecar locks. Queue `v28s_boundary_monotonic_time_safe_v001` / `v28s_live_pnl_midband_no_fade_yes_v019` for continued no-order live-forward collection and review. Do not move to live orders from this artifact alone.

## PSLICE Lock Sweep

Reran the existing paired-sidecar validation chain after refreshing settlement labels once. The refresh wrapper updated labels, then stalled before rewriting every aggregate report; only that research refresh process was stopped. Deterministic downstream modules were then rerun directly.

Latest locked-slice OOS results:

| candidate | model | fresh rows | markets | selected | selected PnL | promotion |
|---|---|---:|---:|---:|---:|---|
| `PSLICELOCK001` | `blend_v28_online_lr010_w20` | 504 | 28 | 177 | `+450.5c` | false |
| `PSLICELOCK002` | `blend_v28_online_lr010_w05` | 432 | 24 | 144 | `+1460.0c` | false |
| `PSLICELOCK003` | `v28` control | 432 | 24 | 153 | `+1516.5c` | false |
| `PSLICELOCK004` | `blend_v28_online_lr010_w15` | 342 | 19 | 14 | `-31.7c` | false |
| `PSLICELOCK005` | `v28` control | 342 | 19 | 16 | `-6.7c` | false |

Combined PSLICE gates:

- Lock comparison: no particle-like lock beats v28 on Brier, log-loss, selected PnL, top-EV PnL, and promotion gates.
- Market breakdown: particle-like rows include `29` negative markets; worst row was `blend_v28_w20_time_gt_600s_v1` on `KXBTC15M-26MAY122115-15` at `-472.5c`.
- Stability: `0` particle-like locks pass.
- Trajectory: `0` particle-like locks pass.
- Retirement/readiness: `0` readiness candidates; `3` hard-vetoed particle-like locks.

## Canonical Live-PnL Policy Result

`run_v28_successor_live_pnl_policy_cycle.py --collect-mode none --skip-label-fetch --write` produced:

- cycle status: `profit_goal_candidate_forward_ready`
- readiness verdict: `level_1_bootstrap_complete`
- registry rows: `16302`
- diagnostic rows not primary credit: `15988`
- primary rows after policy hash: `314`
- primary markets after policy hash: `12`
- primary entered rows after policy hash: `3`
- primary net PnL: `+70.0c`
- primary v28 net PnL: `-692.3c`
- primary delta vs v28: `+762.3c`
- controlled live test authorized: `False`
- promotion allowed by cycle: `False`

Primary slice score:

- wins/losses: `3/0`
- win rate: `1.0000`
- net cents per entered contract: `23.33c`
- max drawdown: `0c`
- remove best 1 market PnL: `+41c`
- market-level LCB: `+0.715c`

All joined diagnostic score:

- rows: `16302`
- markets: `189`
- entries: `37`
- wins/losses: `30/7`
- net PnL: `+260c`
- remove best 1 market PnL: `+35c`
- market-level LCB: `-2.468c`

## Hard Verifier Result

`verify_v28_successor_promotion.py --write` produced:

- overall verdict: `promotable`
- candidate count: `20`
- promotable candidates: `1`
- blocked candidates: `19`
- hard blockers: none

The only promotable candidate was `logged_events_diagnostic / v28s_boundary_monotonic_time_safe_v001`.

Forward evidence gate for this candidate:

- rows: `226`
- markets: `44`
- required rows/markets: `200` / `40`
- delta Brier candidate minus v28: `-0.0002283605`
- delta logloss candidate minus v28: `-0.0023925328`
- near-boundary delta Brier candidate minus v28: `-0.0000820539`
- forward evidence promotable: true

## Residual Gate

This sprint validates a candidate to a live-review / continued live-shadow collection point. It does not authorize live orders.

The main residual gap is Level 2 controlled-live-test readiness. The current live-PnL readiness report intentionally keeps `level_2_controlled_live_test_ready` false, and the policy lab source hard-codes Level 2 false until a separate explicit gate is added and approved.

Recommended next research move:

1. Continue no-order public REST/live-forward collection for `v28s_live_pnl_midband_no_fade_yes_v019`.
2. Track `v28s_boundary_monotonic_time_safe_v001` as the promoted probability candidate in the same forward-review lane.
3. Require more primary entered markets and a Level 2 readiness gate before any controlled live-order decision.
