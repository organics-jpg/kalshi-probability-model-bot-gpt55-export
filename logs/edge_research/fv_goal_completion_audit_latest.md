# FV Model Goal Completion Audit

Current authoritative update: `20260504_132554Z`. The long generated-artifacts paragraph below is retained as historical context; the 2026-05-04 13:25 UTC continuation section supersedes older figures where they conflict.

Generated from local artifacts after the current v28 live scan, the supplemental live_90_70 v28 replay, the physics-prior boundary scan, fixed-rule cross-dataset validation, the live v28 fill shadow validator, the live v28 websocket opportunity scan, the live heartbeat physics-prior audits, the 80%-retention regime classifier scan, the recurring market-interval coverage scan, the interval degeneracy audit, the interval loss-blocker scan, the interval path-physics blocker scan, the chronological interval logistic scan, the staged interval policy scan, the pure-physics interval ablation, the locked interval candidate monitor, the locked pure-physics interval monitor, the locked logistic interval monitor, the fresh validation requirement audit, the locked fresh skip audit, the prior-failure analysis, the refreshed overnight performance audit, the fresh-shadow gate projection, the v21 native passive pure-physics interval validation, the v21 native passive locked-candidate validation, the shared cross-dataset interval frontier scan, the cross-dataset learned interval model transfer probe, the cross-dataset shared loss-blocker scan, the tail-calibrated physics scan, profit-lock forward validation, touch-hazard / kinetic-touch / kinetic-guard / kinetic-price-guard profit validation, kinetic guard physics sanity, and the fresh-loss attribution diagnostic. Latest refreshed two-sided heartbeat timestamp: `20260503_031830Z`; latest profit-lock forward cycle timestamp: `20260503_031730Z`; latest pending-signal monitor timestamp: `20260503_031940Z`; latest kinetic-guard lock timestamp: `20260503_031843Z`; latest kinetic-price-guard lock timestamp: `20260503_031844Z`; latest kinetic guard sanity timestamp: `20260503_031908Z`; latest touch-hazard frontier timestamp: `20260503_022110Z`; latest kinetic-touch stability timestamp: `20260503_031907Z`; latest kinetic-touch lock timestamp: `20260503_031842Z`; latest fresh-loss attribution timestamp: `20260503_001100Z`; latest 80%-retention regime timestamp: `20260502_182712Z`; latest market-interval scan timestamp: `20260502_184735Z`; latest interval degeneracy audit timestamp: `20260502_184704Z`; latest interval blocker timestamp: `20260502_181551Z`; latest interval path-physics blocker timestamp: `20260502_181550Z`; latest interval logistic timestamp: `20260502_181733Z`; latest staged interval timestamp: `20260502_181655Z`; latest pure-physics ablation timestamp: `20260502_181630Z`; latest locked candidate monitor timestamp: `20260502_184704Z`; latest locked pure-physics monitor timestamp: `20260502_184704Z`; latest locked logistic monitor timestamp: `20260502_184705Z`; latest fresh validation requirement timestamp: `20260502_184745Z`; latest locked fresh skip audit timestamp: `20260502_184745Z`; latest overnight performance timestamp: `20260502_152443Z`; latest v21 native passive pure-physics validation timestamp: `20260502_153954Z`; latest v21 locked-candidate validation timestamp: `20260502_174526Z`; latest cross-dataset interval frontier timestamp: `20260502_184820Z`; latest cross-dataset model-transfer timestamp: `20260502_181938Z`; latest cross-dataset shared loss-blocker timestamp: `20260502_184820Z`; latest tail-calibrated physics timestamp: `20260502_184017Z`.

## 2026-05-04 13:25 UTC Continuation Update

Status: not complete. No registered lock clears the Wilson, Bayesian EV, sample-size, and >=80% recurring-market coverage gates. The current source of truth is the pre-resolution registry, not raw recompute. Latest source freshness is clean: raw recompute and registry both resolve through `2026-05-04T14:30:00Z`, with registry pending through `2026-05-04T14:45:00Z`.

Latest formal checks:

| lock | registered/resolved/pending | wins/losses | resolved coverage | net P&L | P(p>BE) | p05 edge | read |
|---|---:|---:|---:|---:|---:|---:|---|
| `book_margin` | 60/59/1 | 42/17 | 98.33% | +128.0c | 0.613 | -8.5c | best broad live baseline, still not proof |
| `book_margin_early` | 56/55/1 | 39/16 | 98.21% | +98.0c | 0.583 | -9.3c | similar but no stronger |
| `hazard_mean_touch80` | 29/28/1 | 21/7 | 90.32% | +74.0c | 0.572 | -12.9c | useful feature, volatile |
| `logit_blend_edge10` | 30/29/1 | 18/11 | 96.67% | +58.0c | 0.568 | -13.4c | edge still thin |
| `score_min60` | 60/59/1 | 41/18 | 98.33% | -186.0c | 0.269 | -13.8c | recompute attractive, live registry negative |
| `impulse_reversal_book_margin_fade` | 13/12/1 | 4/8 | 92.31% | -194.0c | 0.141 | -32.9c | fade branch rejected |
| `book_p80_ask90_frontier` | 4/3/1 | 2/1 | 100.00% | -51.0c | 0.127 | -58.8c | W/L/W but negative net |
| `book_p80_profit_frontier` | 5/4/1 | 2/2 | 100.00% | -135.0c | 0.033 | -64.8c | L/W/L/W and negative net |
| `hazard_mean_touch80_ask76` | 14/13/1 | 9/4 | 76.47% | -28.0c | 0.370 | -25.4c | coverage fail |

New focused registry/recompute audit:

- `book_margin`: registry 39/15, +163c; recompute 224/91, +1071c; 264 mismatches.
- `score_min60`: registry 38/16, -155c; recompute 238/76, +1312c; 272 mismatches, including side/win flips.
- `book_p80_profit_frontier`: registry 0/0, 0c; recompute 260/42, +179c; 302 recompute-only rows.
- Read: recomputed frontier wins are only hypothesis generation unless the same policy is captured pre-resolution. The likely physical/instrumentation issue is candle/physics-state cadence: later candle availability changes the first eligible row.

Physics frontier/falsification results:

- Near-strike breakout overlays: strict_pass=0. Weak near-strike veto/fade variants improved some blocks but failed current/v21 stability.
- Long-memory adverse-momentum overlays: strict_pass=0. Losses often have adverse 15m/30m signed moves, but causal veto/fade variants do not stay stable above the coverage floor.
- Ridge fair-value blend: strict_pass=0. It helped v21/block calibration but hurt current validation, so it is not lockable.
- Same-heartbeat disagreement switch: strict_pass=0. It mostly produced no switches and matched baseline.
- Preemptive physics switch: strict_pass=0. It fixed isolated markets but did not beat `book_margin` globally.
- Touch-book conflict frontier: strict_pass=0 across 145 policies. The 13:45 loss suggested that an early cheap opposite touch-hazard row could preempt later book confidence, but the causal scan did not generalize. Best OOS rows used only a handful of preempts and failed block stability; the recompute baseline remained stronger on combined all-P&L than most touch-preempt variants.
- P80 touch-conflict frontier: strict_pass=0 across 290 policies. The last two p80 live losses were both cases where the early opposite touch row won, but letting touch preempt p80 historically destroys the edge: the best rows are still the p80 baselines, and touch-preempt variants are negative or block-unstable. This is overfit bait, not a lock.
- Cross-dataset recompute frontier: `book_p_side>=0.8; ask<=95; sec>=120` was the best simple all-splits high-coverage row: current +167c at 95.25% coverage, v21 +299c at 86.88% coverage, median ask 85c. Because it had zero causal registry rows, it was forward-locked as research-only `book_p80_profit_frontier` with effective boundary `2026-05-04T13:30:00Z`.
- First `book_p80_profit_frontier` forward row: `KXBTC15M-26MAY040945-45`, YES 82c, registered `2026-05-04T13:35:56Z`, entry `2026-05-04T13:35:35Z`, book probability 0.815, 564 seconds to close, margin $64.79, brownian15 0.697, signed 15m move +91.51, signed 30m move +312.03. It resolved as a loss, -84c. This is an immediate warning that the p80 historical edge is thin enough for one expensive miss to matter.
- Added `probe_book_p80_failure_physics_audit.py`. Updated recompute state: current 302/317, 260/42, +179c, 95.27% coverage, 86.09% accuracy versus 85.50% break-even; v21 192/221, 170/22, +299c, 86.88% coverage, 88.54% accuracy versus 86.98% break-even. The edge is positive but thin.
- `book_p80` weak-state read: `ask>=85` is negative on both datasets (current -271c over 114 rows; v21 -288c over 99 rows), and `ask>=90` is also negative but smaller sample. A nearby historical row, `book_p_side>=0.8; ask<=90; sec>=0`, keeps the 80% recurring-market constraint (current 95.25%, v21 82.81%) and improves combined all net to +588c with all train/validation/holdout splits positive. It was forward-locked as research-only `book_p80_ask90_frontier` with effective boundary `2026-05-04T13:45:00Z`.
- Forward p80 sequence through 14:30Z: `book_p80_ask90_frontier` is W/L/W with one 14:45Z pending row, net -51c; `book_p80_profit_frontier` is L/W/L/W with the same 14:45Z pending row, net -135c. Both retain 100% observed and resolved coverage so far, but neither has credible EV evidence.

Current physical read:

- The most robust live baseline is still broad book-side confidence with margin, not the more ornate physics overlays.
- The main losing state is adverse path memory: for `book_margin`, median signed 15m move is +23.76 on wins versus -190.895 on losses. That is real, but the available filters either cut below the 80% trading target or fail block stability.
- Expensive high-confidence book (`book_p80`) may be the right physics tradeoff if terminal probability is high enough to overcome fee/ask drag. It must prove itself forward because its historical edge is thin and recompute-only.
- Goal remains open: keep collecting causal rows, reject overlays that do not survive registered evidence, and promote nothing until the formal gates clear.

Latest strict-boundary refresh: `20260503_101746Z` with pending registries refreshed at `20260503_101701Z`, physics diagnostics refreshed at `20260503_100353Z`, registered-signal readiness refreshed at `20260503_102206Z`, and registry/recompute divergence refreshed at `20260503_101916Z`. This supersedes the stale 03:18-04:03 UTC figures in the older continuation narrative below: fresh entries are counted only if the market entry could have occurred after the lock existed, using the later of the stored lock close and the next full 15-minute close after lock creation. The 10:17 UTC heartbeat/candle refresh completed with 24,936 raw rows, 24,688 physics rows, 3,183 opportunities, 214 recurring BTC 15-minute markets, and 0 target-pass rules.

## 2026-05-03 10:22 UTC Continuation Update

The current best live-forward candidates still meet the market-retention requirement, but none meets the promotion-quality proof gate. The readiness monitors now include the combo price-guard lock and the separate delayed path-confirmation lock. A stricter registered-signal readiness monitor was added because recomputed validators can change an entry when late log rows appear after settlement.

| lock | fresh selected/base | wins/losses | acc | break-even | Wilson low | coverage | net P&L | Bayesian P(p>BE) | extra perfect wins to Bayesian gate | ready |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| original | 43/44 | 29/14 | 67.44% | 64.98% | 52.52% | 97.73% | 106.0c | 0.609 | 15 | False |
| challenger | 40/43 | 25/15 | 62.50% | 65.70% | 47.03% | 93.02% | -128.0c | 0.314 | 23 | False |
| touch_hazard | 39/40 | 20/19 | 51.28% | 59.21% | 36.20% | 97.50% | -309.0c | 0.152 | 24 | False |
| touch_overlay | 32/33 | 18/14 | 56.25% | 59.69% | 39.33% | 96.97% | -110.0c | 0.332 | 17 | False |
| kinetic_touch | 31/31 | 23/8 | 74.19% | 66.42% | 56.75% | 100.00% | 241.0c | 0.797 | 8 | False |
| kinetic_guard | 30/30 | 23/7 | 76.67% | 68.37% | 59.07% | 100.00% | 249.0c | 0.813 | 8 | False |
| kinetic_price_guard | 28/29 | 20/8 | 71.43% | 64.32% | 52.94% | 96.55% | 199.0c | 0.760 | 8 | False |
| kinetic_combo_price_guard | 2/2 | 1/1 | 50.00% | 68.50% | 9.45% | 100.00% | -37.0c | 0.236 | 11 | False |
| kinetic_path_confirm | 24/24 | 19/5 | 79.17% | 75.04% | 59.53% | 100.00% | 99.0c | 0.619 | 15 | False |

Current read:

- The 10:00 UTC market was a broad falsification event: every pending candidate on `KXBTC15M-26MAY030600-00` chose NO and the outcome was YES. This hit `kinetic_touch`, `kinetic_guard`, `kinetic_price_guard`, the new combo guard, and path-confirmation.
- The 10:15 UTC market was constructive: the kinetic-family registered signals on `KXBTC15M-26MAY030615-15` chose NO at 70c and won. A new 10:30 UTC market is now pre-registered for `kinetic_touch`, `kinetic_guard`, `kinetic_price_guard`, and the combo guard.
- Registered-signal evidence is now the stricter promotion reference. On pre-outcome registered first signals, `kinetic_guard` is 30 resolved markets, 24/6, +372c, 80.00% accuracy, 67.60% break-even, Wilson low 62.69%, Bayesian P(p>break-even)=0.918, p05 edge -2.2c, and 96.77% resolved coverage. It is still not ready.
- The recomputed validator remains more pessimistic for `kinetic_guard`: 30/30, 23/7, +249c, Bayesian P=0.813. The registry/validator difference comes from a late 09:34 log row that changed the recomputed 09:45 entry from the pre-registered YES 61c win to a NO 84c loss. That makes the registry monitor more appropriate for forward proof.
- The registry/recompute divergence audit found 11 row-level differences across locks, but only one material side/win mismatch: `kinetic_guard` on `KXBTC15M-26MAY030545-45`, with a -123c selected-minus-registered net swing.
- `kinetic_touch` is now 30/30 recomputed fresh, 22/8, +213c, Bayesian P=0.768. Full-current unguarded kinetic fell to +759c on 211/213 markets, and its bootstrap risk is no longer small enough to ignore.
- `kinetic_path_confirm` has degraded from promising to mostly diagnostic. All-current path-confirmation is 209/213 markets, 167/42, 79.90% accuracy, 73.79% break-even, Wilson low 73.95%, +1278c, and 98.12% coverage. Fresh after the path-confirm lock is 23/23 markets, 18/5, +71c, Bayesian P=0.571.
- The refreshed path-confirmation scan still supports same-side persistence as a physical prior, but not as a promotion candidate. The top diagnostic row is `same_side_for>=60s AND confirm_score>=0.55`: current +1453c, +694c versus unconfirmed kinetic; v21 +611c, -249c versus unconfirmed kinetic; current/v21 coverage 98.59%/99.10%.
- The new combo lock `kinetic>=0.57 AND adverse15<=100 AND ask<=70` recovered one win after its first loss but remains weak: 2/2 recomputed fresh, 1/1, -37c, Bayesian P=0.236. It has one unresolved 10:30 UTC signal pending.

Completion status: not complete. The project has identified viable high-retention physics candidates, but no candidate yet clears the combined live-forward sample-size gate, Wilson-over-break-even gate, and Bayesian EV gate. No bot logic or live trading behavior has been changed.

## Objective Restated

Find a fair-value model version or selection rule that:

1. Optimizes fee-aware profitability and improves accuracy as far as the observed BTC 15-minute market physics allow.
2. Trades at least 75%-80% of recurring BTC 15-minute markets, using recurring markets rather than fills as the denominator.
3. Is not overfit, with chronological / cross-dataset validation and separate post-lock live validation.
4. Is verified with live data and enough forward sample size before any promotion.
5. Does not change existing bot logic/code.
6. Does not stop or interfere with the running bot.

## Artifacts Inspected

| artifact | purpose | status |
|---|---|---|
| `probe_live_v28_fv_accuracy_volume.py` | Current v28 live-fill FV selection scan | compiled and run |
| `logs/edge_research/fv_accuracy_volume_search_latest.md` | Current v28 scan report | inspected |
| `logs/edge_research/fv_accuracy_volume_search_latest.json` | Current v28 scan metrics | inspected |
| `logs/edge_research/fv_accuracy_volume_candidates_latest.csv` | Current v28 candidate grid | inspected |
| `probe_live_9070_v28_replay.py` | Supplemental v28 replay on live_90_70 labels | compiled and run |
| `logs/edge_research/live_9070_v28_replay_search_latest.md` | Supplemental replay report | inspected |
| `logs/edge_research/live_9070_v28_replay_search_latest.json` | Supplemental replay metrics | inspected |
| `logs/edge_research/live_9070_v28_replay_candidates_latest.csv` | Supplemental replay candidate grid | inspected |
| `logs/edge_research/kalshi_market_metadata_cache.json` | Historical market strike cache for replay | used for replay only |
| `logs/edge_research/coinbase_btc_usd_1m_cache.parquet` | Historical BTC 1m candle cache for replay | used for replay only |
| `probe_physics_priors_boundary_models.py` | Physics-first boundary/drift/realized-vol scan | compiled and run |
| `logs/edge_research/physics_priors_boundary_search_latest.md` | Physics-prior scan report | inspected |
| `logs/edge_research/physics_priors_boundary_search_latest.json` | Physics-prior scan metrics | inspected |
| `logs/edge_research/physics_priors_boundary_candidates_latest.csv` | Physics-prior candidate grid | inspected |
| `logs/edge_research/physics_priors_boundary_trades_latest.csv` | Physics feature ledger | inspected |
| `probe_physics_cross_dataset_validation.py` | Fixed-rule cross-dataset validator | compiled and run |
| `logs/edge_research/physics_cross_dataset_validation_latest.md` | Fixed physics rule validation report | inspected |
| `logs/edge_research/physics_cross_dataset_validation_latest.json` | Fixed physics rule validation metrics | inspected |
| `logs/edge_research/physics_cross_dataset_validation_candidates_latest.csv` | Fixed rule per-dataset candidate metrics | inspected |
| `logs/edge_research/physics_cross_dataset_validation_trades_latest.csv` | Cross-dataset physics feature ledger | inspected |
| `shadow_live_v28_physics_validator.py` | No-trade-impact current-v28 physics shadow validator | compiled and run |
| `logs/edge_research/live_v28_physics_shadow_latest.md` | Current-v28 fixed-rule shadow report | inspected |
| `logs/edge_research/live_v28_physics_shadow_latest.json` | Current-v28 fixed-rule shadow metrics | inspected |
| `logs/edge_research/live_v28_physics_shadow_latest.csv` | Current-v28 fixed-rule shadow ledger | inspected |
| `logs/edge_research/live_v28_physics_shadow_lock.json` | Fresh out-of-sample lock boundary for future v28 shadow evidence | created and inspected |
| `probe_live_v28_websocket_opportunity_physics.py` | Current-v28 live websocket opportunity physics scan | compiled and run |
| `logs/edge_research/live_v28_websocket_opportunity_physics_latest.md` | Websocket opportunity scan report | inspected |
| `logs/edge_research/live_v28_websocket_opportunity_physics_latest.json` | Websocket opportunity scan metrics | inspected |
| `logs/edge_research/live_v28_websocket_opportunity_physics_candidates_latest.csv` | Websocket opportunity candidate grid | inspected |
| `logs/edge_research/live_v28_websocket_opportunity_physics_trades_latest.csv` | Websocket opportunity physics ledger | inspected |
| `logs/edge_research/live_v28_websocket_opportunity_shadow_lock.json` | Fresh out-of-sample lock boundary for future opportunity evidence | created and inspected |
| `probe_live_heartbeat_physics_priors.py` | Broad live websocket heartbeat physics-prior audit | compiled and run |
| `logs/edge_research/live_heartbeat_physics_prior_audit_latest.md` | Heartbeat physics-prior report | inspected |
| `logs/edge_research/live_heartbeat_physics_prior_audit_latest.json` | Heartbeat physics-prior metrics | inspected |
| `logs/edge_research/live_heartbeat_physics_prior_candidates_latest.csv` | Heartbeat physics candidate grid | inspected |
| `logs/edge_research/live_heartbeat_physics_prior_ledger_latest.csv` | Heartbeat physics feature ledger | inspected |
| `probe_live_heartbeat_two_side_fv.py` | Broad two-sided heartbeat FV side-choice probe | compiled and run |
| `logs/edge_research/live_heartbeat_two_side_fv_latest.md` | Two-sided heartbeat FV report | inspected |
| `logs/edge_research/live_heartbeat_two_side_fv_latest.json` | Two-sided heartbeat FV metrics | inspected |
| `logs/edge_research/live_heartbeat_two_side_fv_candidates_latest.csv` | Two-sided heartbeat FV candidate grid | inspected |
| `logs/edge_research/live_heartbeat_two_side_fv_ledger_latest.csv` | Two-sided heartbeat FV feature ledger | inspected |
| `probe_regime_classifier_80ret.py` | 80%-retention two-sided heartbeat regime classifier scan | compiled and run |
| `logs/edge_research/regime_classifier_80ret_latest.md` | 80%-retention regime classifier report | inspected |
| `logs/edge_research/regime_classifier_80ret_latest.json` | 80%-retention regime classifier metrics | inspected |
| `logs/edge_research/regime_classifier_80ret_candidates_latest.csv` | 80%-retention regime candidate grid | inspected |
| `logs/edge_research/regime_classifier_80ret_frontier_latest.csv` | Train-threshold 80% frontier | inspected |
| `probe_market_interval_80coverage.py` | Recurring BTC 15-minute market interval coverage scan | compiled and run |
| `logs/edge_research/market_interval_80coverage_latest.md` | Market-interval coverage report | inspected |
| `logs/edge_research/market_interval_80coverage_latest.json` | Market-interval coverage metrics | inspected |
| `logs/edge_research/market_interval_80coverage_candidates_latest.csv` | Market-interval candidate grid | inspected |
| `logs/edge_research/market_interval_80coverage_selected_latest.csv` | Fixed interval policy selected-market ledger | inspected |
| `logs/edge_research/market_interval_80coverage_lock.json` | Fresh out-of-sample lock for fixed interval policy | created and inspected |
| `probe_interval_policy_degeneracy_audit.py` | Degeneracy/sample-size audit for raw interval target passes | compiled and run |
| `logs/edge_research/interval_policy_degeneracy_audit_latest.md` | Interval degeneracy audit report | inspected |
| `logs/edge_research/interval_policy_degeneracy_audit_latest.json` | Interval degeneracy metrics | inspected |
| `probe_interval_loss_blockers.py` | Focused physics blocker search around economical 80%-coverage interval frontier | compiled and run |
| `logs/edge_research/interval_loss_blockers_latest.md` | Interval loss-blocker report | inspected |
| `logs/edge_research/interval_loss_blockers_latest.json` | Interval loss-blocker metrics | inspected |
| `logs/edge_research/interval_loss_blockers_latest.csv` | Interval loss-blocker candidate grid | inspected |
| `probe_interval_path_physics_blockers.py` | Path-dependent physics blocker scan for economical interval losses | compiled and run |
| `logs/edge_research/interval_path_physics_blockers_latest.md` | Path-physics blocker report | created and inspected |
| `logs/edge_research/interval_path_physics_blockers_latest.json` | Path-physics blocker metrics | created and inspected |
| `logs/edge_research/interval_path_physics_blockers_latest.csv` | Path-physics blocker candidate grid | created and inspected |
| `probe_interval_online_logit.py` | Chronological train-only logistic interval fair-value probe | compiled and run |
| `logs/edge_research/interval_online_logit_latest.md` | Chronological logistic interval report | inspected |
| `logs/edge_research/interval_online_logit_latest.json` | Chronological logistic interval metrics | inspected |
| `logs/edge_research/interval_online_logit_latest.csv` | Chronological logistic candidate grid | inspected |
| `probe_staged_interval_policy.py` | Staged economical-then-fallback interval policy probe | compiled and run |
| `logs/edge_research/staged_interval_policy_latest.md` | Staged interval report | inspected |
| `logs/edge_research/staged_interval_policy_latest.json` | Staged interval metrics | inspected |
| `logs/edge_research/staged_interval_policy_candidates_latest.csv` | Staged interval candidate grid | inspected |
| `probe_interval_pure_physics_ablation.py` | Pure spot/vol/drift side-choice interval ablation | compiled and run |
| `logs/edge_research/interval_pure_physics_ablation_latest.md` | Pure-physics ablation report | inspected |
| `logs/edge_research/interval_pure_physics_ablation_latest.json` | Pure-physics ablation metrics | inspected |
| `logs/edge_research/interval_pure_physics_ablation_latest.csv` | Pure-physics ablation candidate grid | inspected |
| `probe_locked_interval_pure_physics.py` | Frozen pure-physics interval candidate monitor | compiled and run |
| `logs/edge_research/locked_interval_pure_physics.json` | Frozen pure-physics candidate definitions and lock close time | created and inspected |
| `logs/edge_research/locked_interval_pure_physics_latest.md` | Frozen pure-physics fresh-monitor report | inspected |
| `logs/edge_research/locked_interval_pure_physics_latest.json` | Frozen pure-physics fresh-monitor metrics | inspected |
| `logs/edge_research/locked_interval_pure_physics_selected_latest.csv` | Frozen pure-physics selected-market ledger | inspected |
| `probe_locked_interval_candidates.py` | Fixed candidate monitor with a new forward-only fresh lock | compiled and run |
| `logs/edge_research/locked_interval_candidates.json` | Frozen candidate definitions and lock close time | created and inspected |
| `logs/edge_research/locked_interval_candidates_latest.md` | Locked candidate fresh-monitor report | inspected |
| `logs/edge_research/locked_interval_candidates_latest.json` | Locked candidate fresh-monitor metrics | inspected |
| `logs/edge_research/locked_interval_candidates_selected_latest.csv` | Locked candidate selected-market ledger | inspected |
| `probe_locked_interval_logit.py` | Serialized train-only logistic candidate monitor | compiled and run |
| `logs/edge_research/locked_interval_logit_model.json` | Frozen logistic model manifest and lock close time | created and inspected |
| `logs/edge_research/locked_interval_logit_model.pkl` | Serialized frozen logistic sklearn pipeline | created and inspected |
| `logs/edge_research/locked_interval_logit_latest.md` | Frozen logistic fresh-monitor report | inspected |
| `logs/edge_research/locked_interval_logit_latest.json` | Frozen logistic fresh-monitor metrics | inspected |
| `logs/edge_research/locked_interval_logit_selected_latest.csv` | Frozen logistic selected-market ledger | inspected |
| `probe_interval_fresh_validation_requirements.py` | Locked-candidate post-lock sample-size requirement calculator | compiled and run |
| `logs/edge_research/interval_fresh_validation_requirements_latest.md` | Fresh validation requirement report | inspected |
| `logs/edge_research/interval_fresh_validation_requirements_latest.json` | Fresh validation requirement metrics | inspected |
| `logs/edge_research/interval_fresh_validation_requirements_latest.csv` | Fresh validation requirement candidate table | inspected |
| `probe_locked_interval_fresh_skips.py` | Locked-candidate fresh skip / coverage-fragility audit | compiled and run |
| `logs/edge_research/locked_interval_fresh_skips_latest.md` | Fresh skipped-market diagnostic report | created and inspected |
| `logs/edge_research/locked_interval_fresh_skips_latest.json` | Fresh skipped-market diagnostic metrics | created and inspected |
| `logs/edge_research/locked_interval_fresh_skips_latest.csv` | Fresh skipped-market diagnostic table | created and inspected |
| `logs/edge_research/locked_interval_fresh_skip_summary_latest.csv` | Fresh skipped-market coverage summary | created and inspected |
| `probe_overnight_performance.py` | Overnight live bot performance audit | compiled and run |
| `logs/edge_research/overnight_live_bot_performance_latest.md` | Overnight performance report | inspected |
| `logs/edge_research/overnight_live_bot_performance_latest.json` | Overnight performance metrics | inspected |
| `probe_current_v28_prior_failure_modes.py` | Physics-prior falsification analysis across fills/opportunities/replay | compiled and run |
| `logs/edge_research/current_v28_prior_failure_modes_latest.md` | Prior-failure report | inspected |
| `logs/edge_research/current_v28_prior_failure_modes_latest.json` | Prior-failure metrics | inspected |
| `probe_fresh_shadow_gate_projection.py` | Fresh shadow gate recovery projection | compiled and run |
| `logs/edge_research/fresh_shadow_gate_projection_latest.md` | Fresh gate projection report | inspected |
| `logs/edge_research/fresh_shadow_gate_projection_latest.json` | Fresh gate projection metrics | inspected |
| `probe_v21_native_passive_interval_validation.py` | Independent native passive websocket interval validation of locked pure-physics policies | compiled and run |
| `logs/edge_research/v21_native_passive_interval_validation_latest.md` | V21 native passive validation report | inspected |
| `logs/edge_research/v21_native_passive_interval_validation_latest.json` | V21 native passive validation metrics | inspected |
| `logs/edge_research/v21_native_passive_interval_validation_ledger_latest.csv` | V21 native passive interval decision ledger | inspected |
| `logs/edge_research/v21_native_passive_interval_validation_selected_latest.csv` | V21 native passive selected-policy ledger | inspected |
| `probe_v21_locked_interval_candidate_validation.py` | Independent native passive websocket interval validation of frozen simple/staged/logit policies | compiled and run |
| `logs/edge_research/v21_locked_interval_candidate_validation_latest.md` | V21 locked-candidate validation report | created and inspected |
| `logs/edge_research/v21_locked_interval_candidate_validation_latest.json` | V21 locked-candidate validation metrics | created and inspected |
| `logs/edge_research/v21_locked_interval_candidate_validation_ledger_latest.csv` | V21 locked-candidate interval decision ledger | created and inspected |
| `logs/edge_research/v21_locked_interval_candidate_validation_selected_latest.csv` | V21 locked-candidate selected-policy ledger | created and inspected |
| `probe_cross_dataset_interval_frontier.py` | Shared simple-policy scan across current heartbeat and v21 passive interval ledgers | compiled and run |
| `logs/edge_research/cross_dataset_interval_frontier_latest.md` | Cross-dataset interval frontier report | created and inspected |
| `logs/edge_research/cross_dataset_interval_frontier_latest.json` | Cross-dataset interval frontier metrics | created and inspected |
| `logs/edge_research/cross_dataset_interval_frontier_latest.csv` | Cross-dataset shared-policy candidate grid | created and inspected |
| `probe_cross_dataset_interval_model_transfer.py` | Train-on-one-capture / validate-on-other learned interval model transfer probe | compiled and run |
| `logs/edge_research/cross_dataset_interval_model_transfer_latest.md` | Cross-dataset learned transfer report | created and inspected |
| `logs/edge_research/cross_dataset_interval_model_transfer_latest.json` | Cross-dataset learned transfer metrics | created and inspected |
| `logs/edge_research/cross_dataset_interval_model_transfer_latest.csv` | Cross-dataset learned model/gate candidate grid | created and inspected |
| `probe_cross_dataset_shared_loss_blockers.py` | Cross-dataset physical blocker scan around the stable cheap interval policy | compiled and run |
| `logs/edge_research/cross_dataset_shared_loss_blockers_latest.md` | Cross-dataset blocker report | created and inspected |
| `logs/edge_research/cross_dataset_shared_loss_blockers_latest.json` | Cross-dataset blocker metrics | created and inspected |
| `logs/edge_research/cross_dataset_shared_loss_blockers_latest.csv` | Cross-dataset blocker candidate grid | created and inspected |
| `probe_interval_tail_calibrated_physics.py` | Tail-inflated realized-vol terminal physics scan across current and v21 interval ledgers | compiled and run |
| `logs/edge_research/interval_tail_calibrated_physics_latest.md` | Tail-calibrated physics interval report | created and inspected |
| `logs/edge_research/interval_tail_calibrated_physics_latest.json` | Tail-calibrated physics interval metrics | created and inspected |
| `logs/edge_research/interval_tail_calibrated_physics_latest.csv` | Tail-calibrated physics candidate grid | created and inspected |
| `logs/edge_research/interval_tail_calibration_bins_latest.csv` | Tail-calibration empirical probability bins | created and inspected |

## Current v28 Live-Fill Evidence

Source logs:

- `logs/live_mushroom_v28_size2/execution_events.ndjson`
- `logs/live_mushroom_v28_size2/bot.log`

Observed sample:

- Usable deduped entry orders: 127
- Contracts: 251
- Candidate rules scanned: 11,704
- Target-pass rules: 0
- Observed-pass rules before sample floor: 0

Baseline:

| split | trade accuracy | contract accuracy | contract retention |
|---|---:|---:|---:|
| all | 102/127 = 80.31% | 202/251 = 80.48% | 100.00% |
| train | 65/76 = 85.53% | 128/149 = 85.91% | 100.00% |
| validation | 21/25 = 84.00% | 42/50 = 84.00% | 100.00% |
| holdout | 16/26 = 61.54% | 32/52 = 61.54% | 100.00% |

Feasibility bound:

- At 75% holdout contract retention, at least 39 of 52 holdout contracts must be selected.
- Only 32 holdout contracts won.
- Even an oracle can reach only 32/39 = 82.05% holdout contract accuracy.
- Therefore the requested 95% / 75% holdout-verified target is impossible on the current v28 live-fill sample.

## Supplemental live_90_70 v28 Replay Evidence

Scope:

- Dataset: `research_data/live_90_70`
- Resolved live labels replayed through v28 with recovered Kalshi strikes and BTC 1m candles.
- This is supplemental historical live replay, not direct current v28 live fills.

Observed sample:

- Input trade labels: 634
- Usable replayed entries: 509
- Contracts: 4,983
- Candidate rules scanned: 777
- Target-pass rules: 0
- Observed-pass rules before sample floor: 0

Baseline replayed entry set:

| split | trade accuracy | contract accuracy | contract retention |
|---|---:|---:|---:|
| all | 501/509 = 98.43% | 4,903/4,983 = 98.39% | 100.00% |
| train | 305/305 = 100.00% | 3,003/3,003 = 100.00% | 100.00% |
| validation | 99/102 = 97.06% | 964/994 = 96.98% | 100.00% |
| holdout | 97/102 = 95.10% | 936/986 = 94.93% | 100.00% |

Best v28-positive rules:

- The highest-accuracy replayed v28 rules reached 100% accuracy but retained only about 32.87% of all contracts and 26.57% of holdout contracts.
- No replayed v28 rule retained at least 75% of all and holdout contract volume.
- The baseline 90/70 entry set is strong, but the v28 fair-value surface does not validate as the reason for keeping 75%-80% of that volume.

## Physics-Prior Boundary Evidence

Scope:

- Current v28 live fills were retested with signed spot-strike cushion, time-scaled cushion, v28 sigma cushion, and zero-drift Brownian probability.
- Supplemental live_90_70 replay was also tested with realized-vol cushion and short-window adverse BTC drift using the cached Coinbase 1-minute candles.
- This challenges the v28 priors directly; it is not another p/edge threshold-only scan.

Current v28 live-fill result:

- Rows: 127
- Contracts: 251
- Candidate physics rules scanned: 1,286
- Target-pass rules: 0
- Observed-pass rules before sample floor: 0
- Coinbase BTC 1-minute candle cache was extended through 2026-05-02T13:46:59.999Z so current-v28 drift and realized-vol fields are now populated.
- Best current high-accuracy rules kept only about 14%-16% of contract volume.
- Best current high-volume rules retained at least 75% volume but stayed near 83% all-contract accuracy and 71%-73% holdout-contract accuracy.
- Holdout oracle at 75% contract retention requires 39 holdout contracts and can reach only 32/39 = 82.05%, so current-v28 success is impossible on this holdout slice.

Supplemental live_90_70 physics result:

- Rows: 509
- Contracts: 4,983
- Candidate physics rules scanned: 1,286
- Target-pass rules: 8
- Strongest simple rule: `ask<=100; block 15m adverse>10 unless v28 cushion>0.5`
- That rule selected 4,290 contracts, retained 86.09% all-contract volume, reached 98.37% all-contract accuracy, retained 91.89% holdout-contract volume, and reached 95.58% holdout-contract accuracy.
- Other passes came from realized-vol cushion rules such as `margin/rv30>=0.5` and `Phi(margin/rv15)>=0.7`.
- These are useful shadow-test hypotheses, not completion evidence for current-v28 live fills.

## Fixed-Rule Cross-Dataset Validation

Scope:

- The fixed rules came from the live_90_70 physics-prior scan.
- Independent validation excludes live_90_70 from the pooled independent view.
- Only resolved settlement rows are included; exited-before-settlement rows are excluded.
- Public Kalshi metadata and Coinbase candles were fetched only for research backfill.

Coverage:

- Feature rows: 829
- Contracts: 6,604
- Pooled independent rows, excluding live_90_70: 320 trades / 1,621 contracts
- Metadata missing after fetch: 3 markets
- Candle cache window after fetch: 2026-03-14T00:54:59.999Z to 2026-05-02T03:44:59.999Z

Best fixed rule:

- Rule: `ask<=100; block 15m adverse>10 unless v28 cushion>0.5`
- Pooled independent contract accuracy: 1,444/1,517 = 95.12%
- Pooled independent trade accuracy: 285/296 = 96.28%
- Pooled independent contract retention: 93.58%
- Pooled independent trade retention: 92.50%
- Pooled all-data contract accuracy: 97.52%
- Pooled all-data contract retention: 93.87%

Failure modes:

- The same rule does not fix the current v28 live-fill sample; current v28 high-volume holdout remains far below 95%.
- The rule fails on some small/off-policy tapes such as `live_87_77_67` and `live_liquidity_dwell_size2`; the pooled independent pass is dominated by higher-volume 90-style ledgers.
- Therefore this is a strong physics-shadow candidate, not a bot-promotion-ready current-v28 completion.

## Current-v28 Live Physics Shadow Validator

Scope:

- Applies the fixed rule `ask<=100; block 15m adverse>10 unless v28 cushion>0.5` to every live v28 entry fill.
- Keeps unresolved rows in the ledger when present; current run had no unresolved rows.
- Uses current live v28 execution telemetry plus Coinbase BTC 1-minute candles.
- Filters quote-inferred outcomes so an active market is not treated as resolved before its close time.
- Writes only `logs/edge_research/live_v28_physics_shadow_*` artifacts.

Latest result:

- Total shadow rows: 127
- Resolved rows: 127
- Unresolved rows: 0
- Evaluable rows: 127
- Selected rows: 123
- Fresh out-of-sample lock: execution log source line 3222, created at 2026-05-02T05:08:16.423429Z
- Fresh rows after lock: 6, all resolved
- Fresh selected rows after lock: 4
- Fresh accuracy gate: true
- Fresh retention gate: false
- Fresh selected sample shortfall: 71 trades / 142 contracts
- Latest independent refresh: 2026-05-02T13:47:56Z; the 09:45 local market closed and the bot advanced to active market `KXBTC15M-26MAY021000-00`. The execution event ledger now includes post-lock entries through the `KXBTC15M-26MAY020845-45` NO exit/reconcile sequence at 2026-05-02T12:40:19Z; no newer entry fills were present at this refresh.
- Fresh baseline after lock: 10/12 contracts = 83.33%
- Fresh shadow-selected after lock: 8/8 contracts = 100.00%, retention 66.67%
- All resolved baseline: 202/251 contracts = 80.48%
- All shadow-selected: 196/243 contracts = 80.66%, retention 96.81%
- Holdout baseline: 32/52 contracts = 61.54%
- Holdout shadow-selected: 28/46 contracts = 60.87%, retention 88.46%

Interpretation:

- The fixed physics rule is now ready to accumulate fresh current-v28 shadow evidence.
- Future validation is separated from the old current-v28 sample using `live_v28_physics_shadow_lock.json`.
- It does not rescue the already-collected current v28 sample; it selects nearly all entries and preserves the poor holdout.

Fresh gate projection:

- At the 75% retention floor, the shadow needs at least 71 more selected trades and 142 more selected contracts to reach the configured fresh sample floor.
- At that minimum selected sample, it can block at most 23 future baseline trades / 46 future baseline contracts while staying at 75% retention.
- At the 80% retention floor, it can block at most 16 future baseline trades / 33 future baseline contracts at the same minimum selected sample.
- At the minimum selected sample, the selected set can absorb at most 3 additional selected losing trades or 7 additional selected losing contracts while keeping 95% accuracy.
- Current blocker: retention and sample size, not fresh selected accuracy.

## Current-v28 Websocket Opportunity Evidence

Scope:

- Reads v28-approved `signal_seen` rows from `logs/live_mushroom_v28_size2/execution_events.ndjson`.
- Dedupes the live websocket tape into first-per-market, first-per-market-side, and all-signal opportunity views.
- Uses the same cached Coinbase candles and physics rule family as the fill validator.
- This is opportunity-level live telemetry, not actual filled-entry proof.

Coverage:

- Raw v28-approved signal rows after latest refresh: 241
- Resolved raw signal rows: 241
- Unique markets: 69
- Unique market/side pairs: 75
- Fresh opportunity lock: source line 3218, created at 2026-05-02T05:18:38.157084Z
- Fresh rows after opportunity lock: 5 first-per-market rows, all resolved

Primary first-per-market view:

- Rows: 69
- Resolved rows: 69
- Contracts: 138
- Baseline all: 112/138 contracts = 81.16%
- Baseline holdout: 22/28 contracts = 78.57%
- Physics target-pass rules: 0
- First-per-market perfect-selector holdout oracle:
  - At 75% retention, required contracts = 21; max possible holdout contract accuracy = 22/21 capped at 100.00%.
  - At 80% retention, required contracts = 23; max possible holdout contract accuracy = 22/23 = 95.65%, but max trade accuracy is 11/12 = 91.67%.
- Sensitivity oracle checks:
  - First-per-market-side holdout max = 95.65% contract accuracy at 75% retention but only 91.67% trade accuracy, so the full gate still fails.
  - All-signal holdout max = 70.27% at 75% retention and 65.82% at 80% retention.

Fixed adverse-drift rule on first-per-market opportunities:

- Rule: `ask<=100; block 15m adverse>10 unless v28 cushion>0.5`
- All selected: 108/132 contracts = 81.82%, retention 95.65%
- Validation selected: 24/28 contracts = 85.71%, retention 100.00%
- Holdout selected: 18/22 contracts = 81.82%, retention 78.57%

Interpretation:

- The current-v28 weakness is visible before fills: high-volume opportunity-level physics rules remain around 82%-84% all-contract accuracy and far below 95% on selected-rule holdout.
- The updated first-per-market opportunity holdout is no longer contract-oracle-impossible at the 75% retention floor, but no scanned physics rule reaches the gate; at 80% retention, the trade side of the oracle still fails.
- This gives additional evidence against the v28 current prior, but it does not complete the active goal because it is not fresh post-lock realized fill validation.
- The latest fresh opportunity and fill rows resolved after the 2026-05-02 01:30 local market close; the sample is directionally encouraging for the shadow rule but much too small and below volume-retention gates.

## Live Heartbeat Physics-prior Audit

Scope:

- Uses broader live websocket heartbeat rows from `logs/live_mushroom_v28_size2/bot.log`, not just v28-approved signals.
- Candidate state is the book favorite at each heartbeat; the primary view buckets to one row per market per minute.
- Coinbase BTC candles were refreshed through `2026-05-02T13:46:59.999Z` for spot and realized-volatility physics.
- This is prior-falsification evidence, not filled-trade completion evidence, because heartbeat rows are correlated market states.

Coverage:

- Raw favorite heartbeat rows: 8,289
- Rows with candle physics: 8,265
- Unique markets with physics: 142
- Primary minute-bucket rows: 2,129
- Target-pass rules: 0

Primary minute-bucket view:

- Baseline all book-favorite accuracy: 1,636/2,129 = 76.84%
- Baseline holdout book-favorite accuracy: 339/426 = 79.58%
- Perfect-selector holdout oracle:
  - At 75% retention, required rows = 320; max possible accuracy = 100.00%.
  - At 80% retention, required rows = 341; max possible accuracy = 99.41%.
  - Validation is the limiting split: even a perfect selector reaches only 91.88% at 75% retention and 86.22% at 80% retention.

High-retention rules on the primary heartbeat view:

- Best high-retention rule family by primary ranking: `Phi(margin/rv30)>=0.55`
- All selected: 81.23% accuracy, 80.84% retention
- Validation selected: 74.34% accuracy
- Holdout selected: 84.35% accuracy, 80.99% retention

Calibration reads:

- `book_p_side >= 0.90`: 646/657 = 98.33%, but only 30.86% of primary minute-bucket rows.
- `brownian_p_rv_15m >= 0.90`: 571/578 = 98.79%, but only 27.15% of primary minute-bucket rows.
- At high volume, the physics and book priors are directionally useful but not close to the 95% / 75%-80% requirement.

Interpretation:

- The underlying physics is not useless: extreme book/realized-vol states are highly accurate.
- The active objective is blocked by a regime frontier rather than one split only. Accuracy rises above 95% only after cutting too much volume, and the updated primary heartbeat view now fails primarily in validation while holdout improves.
- This supports a regime-classifier direction instead of further threshold tuning on the current v28 fill/opportunity holdouts.

## Live Heartbeat Two-sided FV Probe

Scope:

- Uses the same live heartbeat stream, but each heartbeat contributes both YES and NO candidate sides.
- Simple book, realized-vol, drift, and composite score families choose one side or skip.
- This tests whether allowing contrarian side choice fixes the FV prior at high volume.

Coverage:

- Raw two-sided rows: 18,508
- Rows with candle physics: 18,396
- Unique markets with physics: 159
- Primary minute-bucket opportunities: 2,371
- Target-pass models: 0

Primary two-sided minute-bucket view:

- Perfect side-choice oracle can reach 100% by construction, so failure here is model-family/feature-separation, not label impossibility.
- Best high-retention model by primary ranking: `score_min_book_rv15>=0.55; ask<=100`
- All selected: 82.32% accuracy, 78.24% retention
- Validation selected: 80.91% accuracy
- Holdout selected: 82.67% accuracy, 78.95% retention
- High-accuracy models remain low-volume; for example `book_p_side>=0.95; ask<=100` is 99.82% all accuracy but only 23.11% all retention and 22.74% holdout retention.

Interpretation:

- Merely allowing the model to choose the contrarian side does not solve the active goal.
- The same pattern remains: extreme physics/book agreement is accurate but too sparse, while 75%-80% retention collapses below 95%.

## 80% Retention Regime Classifier Probe

Scope:

- Uses the refreshed two-sided heartbeat ledger from `logs/edge_research/live_heartbeat_two_side_fv_ledger_latest.csv`.
- Primary view is `two_side_minute_bucket`, with one selected side per opportunity.
- Candidate rules choose a side by a book/physics score, then apply one interpretable regime gate.
- The hard retention floor is 80% on all, train, validation, and holdout splits.

Coverage:

- Primary resolved opportunities: 2,323
- Chronological split: 1,393 train / 465 validation / 465 holdout
- Candidate regime rules scanned: 3,144
- Rules retaining at least 80% on every split: 1,295
- Target-pass rules at 95% accuracy and 80% retention: 0

Best 80%-retention result:

- Chooser: `score_min_book_rv15_drift5`
- Gate: `brownian_p_rv_30m>=0.55`
- Selected: 1,865/2,323 opportunities = 80.28% retention
- All accuracy: 80.64%
- Train accuracy: 81.59%
- Validation accuracy: 79.03% at 80.00% retention
- Holdout accuracy: 79.41% at 80.43% retention
- To reach 95% from this candidate without losing wins, another 63 selected validation losses and 62 selected holdout losses would need to be blocked.

Interpretation:

- The 80% floor makes the frontier stricter than the earlier 75%-80% read: many candidates preserve volume, but none is close to promotion-grade accuracy.
- Mild two-condition physics gates did not materially improve the validation bottleneck.
- This rejects the idea that a simple high-volume regime gate can rescue the current two-sided heartbeat prior.

## Recurring Market-Interval Coverage Evidence

Scope:

- Uses the refreshed two-sided heartbeat ledger from `logs/edge_research/live_heartbeat_two_side_fv_ledger_latest.csv`.
- Unit of volume is the recurring BTC 15-minute market ticker, matching the user's clarified denominator.
- A policy may fire once per resolved market; coverage is selected markets / resolved markets.
- Candidate selection is causal inside the market: the first heartbeat passing the gate becomes the trade.
- A separate degeneracy audit tests whether raw passes are just high-price/late-market settlement proximity.

Coverage scan:

- Resolved recurring BTC 15-minute market intervals: 156
- Chronological split: 93 train / 31 validation / 32 holdout
- Candidate interval policies scanned: 2,160
- Policies covering at least 80% of intervals on every split: 1,642
- Raw policies passing 95% accuracy and 80% interval coverage: 40
- Nondegenerate policies passing target: 0

Best raw interval pass:

- Policy: `choose=score_min_book_rv15; score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0`
- Selected: 137/156 intervals = 87.82% coverage
- All accuracy: 136/137 = 99.27%
- Validation accuracy: 26/26 = 100.00% at 83.87% coverage
- Holdout accuracy: 26/26 = 100.00% at 81.25% coverage
- Median ask: 98.0 cents
- Median time-to-close: 169.1 seconds
- Degeneracy flags: median ask >=95c, p75 ask >=97c, ask cap 100c, 137 selections at ask>=95c, 27 selections at 100c, and validation/holdout Wilson lower bounds only 87.13%/87.13%.
- Fresh interval lock: created after close time `2026-05-02T14:30:00+00:00`.
- Fresh selected after lock: 9/11 resolved intervals, 100.00% accuracy and 81.82% coverage; median fresh ask is 97.0c and median time-to-close is 181.8 seconds.

Best economical interval alternatives:

- Best economical 80%-coverage policy: `score_min_book_rv15>=0.8; ask<=95; sec_to_close>=60`
- That policy covered 83.97% of intervals but reached only 87.79% accuracy, with 86.21% validation accuracy and 88.00% holdout accuracy.
- Best economical >=95%-accuracy policy: `book_p_side>=0.95; ask<=95; sec_to_close>=60`
- That policy reached 100.00% realized accuracy but covered only 30.13% of intervals, with holdout sample only 6 selected markets.

Interpretation:

- On the user's corrected market-interval denominator, a raw 95% / 80% pass exists, but it is not a verified fair-value model.
- The pass is dominated by expensive, near-certain book states rather than a robust physics edge; all-sample Wilson now clears 95%, but validation and holdout Wilson lower bounds remain far below the required 95% accuracy.
- Once high-price degeneracy is blocked, the frontier reverts to the same shape seen in opportunity and fill tests: 80%+ coverage models remain around 88%-89% accuracy, while 95%+ accuracy models cover only about 31% of intervals.

## Interval Loss-blocker Search

Scope:

- Starts from the best economical 80%-coverage interval policy.
- Applies one or two simple pre-settlement physics blockers.
- Preserves the recurring BTC 15-minute market interval as the coverage denominator.
- Reports chronological train/validation/holdout results and Wilson lower bounds.

Base:

- Policy: `choose=score_min_book_rv15; score_min_book_rv15>=0.8; ask<=95; sec_to_close>=60`
- Selected: 131/156 intervals = 83.97% coverage
- All accuracy: 87.79%
- Validation accuracy: 86.21% at 93.55% coverage
- Holdout accuracy: 88.00% at 78.12% coverage

Best blocker:

- Blocker: `block drift_p_5m_rv_15m<=0.85`
- Selected: 126/156 intervals = 80.77% coverage
- All accuracy: 88.89%
- Validation accuracy: 88.89% at 87.10% coverage
- Holdout accuracy: 88.00% at 78.12% coverage
- Target-pass blocker policies: 0
- Wilson-pass blocker policies: 0

Interpretation:

- Simple physics blockers barely improve the all-sample economical frontier and still miss both target gates.
- The best blocker now keeps 80%+ coverage on validation and holdout, but validation/holdout accuracy remains well below 95%.
- This rejects the idea that one or two obvious spread/adverse/volatility filters can rescue the nondegenerate 80%-coverage interval model.

## Interval Path-Physics Blocker Scan

Scope:

- Starts from the same best economical 80%-coverage interval policy: `score_min_book_rv15>=0.8; ask<=95; sec_to_close>=60`.
- Tests the prior that some cheap losses are path-dependent fade states, not bad terminal Brownian states.
- Candidate blockers include recent side-favorable impulse divided by current margin, pre-move margin proxies, short-term deceleration, and realized-volatility ratios.
- Reports chronological train/validation/holdout results and Wilson lower bounds.

Result:

- Resolved intervals: 156.
- Candidate path-blocker rows evaluated: 14.
- Target-pass rows: 0.
- Wilson-pass rows: 0.
- Best scanned path blocker: `block decel_1v5<=-1 OR block rv_ratio_5_15>=1.5`.
- It selected 125/156 intervals = 80.13% coverage at 89.60% all accuracy.
- Validation reached 89.29% accuracy at 90.32% coverage.
- Holdout reached 91.67% accuracy at 75.00% coverage, below the 80% split coverage floor.

Interpretation:

- The path/fade prior is useful as a diagnostic because it improves validation versus the base economical policy.
- It still fails the user's 95% realized-accuracy target and does not solve the holdout frontier.
- The cheap 80%-coverage problem is not fixed by terminal probability, simple adverse-move blockers, or simple side-favorable impulse blockers.

## Chronological Interval Logistic Probe

Scope:

- Uses the refreshed two-sided heartbeat ledger.
- Trains simple L2 logistic models on the chronological train split only.
- Thresholds are chosen from train-market behavior only, then evaluated on validation and holdout.
- Candidate policies still fire once per recurring BTC 15-minute interval.

Coverage:

- Resolved intervals: 156
- Chronological split: 93 train / 31 validation / 32 holdout
- Candidate logistic policies scanned: 1,440
- Raw target-pass policies: 9
- Wilson-pass policies: 0

Best learned raw pass:

- Policy: `book_physics_price; C=0.05; p>=0.95; ask<=100; sec>=0`
- Train-picked by the script's train-only selection rule: true
- Selected: 145/156 intervals = 92.95% coverage
- All accuracy: 99.31%
- Validation accuracy: 100.00% at 93.55% coverage
- Holdout accuracy: 100.00% at 90.62% coverage
- Median ask: 98.0 cents
- Median time-to-close: 170.3 seconds
- Validation Wilson lower bound: 88.30%; holdout Wilson lower bound: 88.30%

Interpretation:

- This is the strongest non-future-leaking interval result so far, but it is still not completion evidence.
- The pass again depends on `ask<=100`, `sec>=0`, and a 98c median ask; it is the same high-price frontier in learned-model form.
- It fails the sample-size-safe Wilson gate and has not been validated on fresh post-lock intervals.
- Economical constraints such as `ask<=95` or `sec>=60` drop coverage below the recurring-market target or leave Wilson bounds far below 95%.

## Staged Interval Policy Probe

Scope:

- Tests a causal two-stage interval policy: try an economical physics/book gate first, then fall back to a high-confidence late/book gate.
- Still fires at most once per recurring BTC 15-minute market interval.
- The aim is to keep the user's 80% interval coverage requirement while reducing the raw policy's high-price/late-entry dependence.

Coverage:

- Resolved intervals: 156
- Chronological split: 93 train / 31 validation / 32 holdout
- Staged candidates scanned: 1,152
- Raw staged target-pass policies: 108
- Less-degenerate staged target-pass policies: 0

Best raw staged pass:

- Stage 1: `economical; choose=score_min_book_rv15; score_min_book_rv15>=0.9; ask<=90; sec>=60`
- Fallback: `fallback; choose=score_min_book_rv15; score_min_book_rv15>=0.9; ask<=100; sec>=0; sec<=300`
- Stage 1 selected 8 markets; fallback selected 134 markets.
- Selected: 142/156 intervals = 91.03% coverage
- All accuracy: 100.00%
- Validation accuracy: 100.00%
- Holdout accuracy: 100.00%
- Wilson lower bound: 97.37%
- Median ask: 97.0 cents
- Ask=100 selections: 22
- ROI: 3.30%

High-coverage staged frontier:

- A staged row with 9 economical markets and 144 fallback markets selected 153/156 intervals = 98.08% coverage.
- It reached 98.69% all accuracy, 96.77% validation accuracy, and 100.00% holdout accuracy.
- Median ask was still 97.0 cents, Wilson lower bound was 95.36%, and 9 entries were still at 100c.
- Rows with meaningfully lower median ask kept high coverage but fell back to roughly the economical frontier accuracy range.

Interpretation:

- Staging shows there is a real near-certain fallback state, but it does not solve the underlying physics problem.
- The only staged policies that clear the literal target still depend on expensive/high-certainty entries; no staged candidate cleared the less-degenerate target definition.
- This makes the completion test stricter, not looser: the target can be hit by settlement-proximity mechanics, but not yet by a robust fair-value model at 80% recurring-market coverage.

## Current 156-Interval Refresh (Superseded)

Scope:

- Refreshed `probe_live_heartbeat_two_side_fv.py` at `20260502_181530Z`.
- Re-ran recurring interval, degeneracy, blocker, path-blocker, staged, chronological logistic, pure-physics, locked monitor, fresh validation, and cross-dataset probes on the resulting 156 resolved-market ledger.
- This is still heartbeat-derived interval telemetry, not live filled-trade promotion evidence.

Fresh locked fixed policy:

- Fixed policy: `choose=score_min_book_rv15; score_min_book_rv15>=0.9; ask<=100; sec_to_close>=0`
- Lock close time: `2026-05-02T14:30:00+00:00`
- Fresh resolved intervals after lock: 11
- Fresh selected intervals after lock: 9
- Fresh selected accuracy: 100.00%
- Fresh interval coverage: 81.82%
- Fresh median ask: 97.0c; fresh median seconds to close: 181.8

Refreshed raw interval frontier:

- Resolved intervals: 156
- Raw target-pass interval policies: 40
- Nondegenerate target-pass interval policies: 0
- Best raw interval pass: `score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0`
- It selected 137/156 intervals = 87.82% coverage at 99.27% realized accuracy.
- Its all-sample 95% Wilson lower bound is 95.98%, but validation/holdout Wilson lower bounds are only 87.13%/87.13%.
- Median ask is 98c, with 135 selections at ask>=95c and 27 selections at 100c.

Refreshed nondegenerate/economical frontier:

- Best economical 80%-coverage policy: `score_min_book_rv15>=0.8; ask<=95; sec_to_close>=60`
- It selected 131/156 intervals = 83.97% coverage at 87.79% accuracy.
- Best focused blocker: `block adverse_move_5m>=5`
- It selected 129/156 intervals = 82.69% coverage at 88.37% accuracy.
- Path-physics blocker rows still have zero target/Wilson passes; the economical frontier remains below 90% on the limiting splits.

Refreshed learned/staged frontier:

- Chronological train-only logistic scan: 9 raw target-pass policies, 0 Wilson-pass policies.
- Best learned raw pass: `book_physics_price; C=0.05; p>=0.95; ask<=100; sec>=0`
- It selected 145/156 intervals = 92.95% coverage at 99.31% realized accuracy, but validation/holdout Wilson lower bounds are 88.30%/88.30%.
- Staged scan: 108 raw target-pass policies, 0 less-degenerate target-pass policies.
- Best staged pass selected 142/156 intervals = 91.03% coverage at 100.00% realized accuracy, but used 134 fallback markets, median ask 97c, and 22 entries at 100c.

Fresh frozen-candidate monitor:

- Fresh denominator after the 15:00 UTC lock is now 9 resolved intervals.
- All frozen interval, pure-physics, logistic, and fixed candidates selected 7/9 fresh intervals = 77.78% fresh coverage.
- At this superseded snapshot, the high-price frozen candidates were 7/7 on selected fresh intervals, but failed the user's 80% fresh coverage gate and had only a 64.57% Wilson lower bound.
- The economical frozen candidates are 6/7 = 85.71% fresh accuracy at 77.78% coverage.

Interpretation:

- The refreshed data strengthens the claim that high-price late certainty is available, but it does not complete the goal as a fair-value model.
- Fresh post-lock evidence from frozen candidates no longer clears the clarified 80% recurring-market denominator: 7/9 selected is 77.78%.
- No current refreshed artifact verifies a nondegenerate, sample-size-safe, live fair-value model at >=95% realized accuracy and >=80% recurring-market coverage.

## Current 159-Interval Refresh

Scope:

- Refreshed `probe_live_heartbeat_two_side_fv.py` at `20260503_000522Z`.
- Re-ran the recurring interval, degeneracy, locked monitor, fresh validation, fresh skip, shared cross-dataset frontier, and shared blocker probes on the resulting 159 resolved-market ledger.
- This is still heartbeat-derived interval telemetry, not live filled-trade promotion evidence.

Heartbeat/fresh data:

- Raw two-sided rows: 20,974; rows with candle physics: 20,840.
- Primary minute-bucket opportunities: 2,686; target-pass two-sided models: 0.
- Fixed fresh interval policy after the 14:30 UTC lock selected 12/14 fresh intervals = 85.71% coverage at 100.00% selected accuracy; median fresh ask improved to 94c.

Refreshed raw interval frontier:

- Resolved intervals: 159.
- Raw target-pass interval policies: 40.
- Nondegenerate target-pass interval policies: 0.
- Best raw interval pass: `score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0`.
- It selected 140/159 intervals = 88.05% coverage at 99.29% realized accuracy.
- Its all-sample 95% Wilson lower bound is 96.07%, but validation/holdout Wilson lower bounds are only 87.54%/87.54%.
- Median ask is still 98c, with 140 selections at ask>=95c and 27 selections at 100c.

Refreshed nondegenerate/economical frontier:

- Best economical 80%-coverage policy: `score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60`.
- It selected 147/159 intervals = 92.45% coverage at 87.76% accuracy.
- Best `score_min_book_rv15` economical variant selected 134/159 intervals = 84.28% coverage at 88.06% accuracy.
- Best economical >=95%-accuracy policy still covered only 31.45% of intervals.

Fresh frozen-candidate monitor:

- Fresh denominator after the 15:00 UTC lock is now 12 resolved intervals.
- All frozen interval, pure-physics, logistic, and fixed candidates selected 10/12 fresh intervals = 83.33% fresh coverage.
- The high-price frozen candidates are 10/10 on selected fresh intervals, but the Wilson lower bound is only 72.25% and they still need 63 additional perfect selected fresh wins.
- The economical frozen candidates are 9/10 = 90.00% fresh accuracy at 83.33% coverage.
- The skipped fresh markets are unchanged: `KXBTC15M-26MAY021300-00` and `KXBTC15M-26MAY021330-30`; forcing them still means either 100c near-settlement entries or cheap states that lost.

Refreshed cross-dataset checks:

- Shared simple-policy scan on 159 current intervals and 221 v21 intervals still has zero joint target passes and zero joint Wilson passes.
- Best shared simple nondegenerate policy: `book_p_side>=0.8; ask<=95; sec>=60; adverse15<=10_or_margin_rv15>=0.5`, with 85.71% current accuracy at 96.86% coverage and 87.75% v21 accuracy at 92.31% coverage.
- Shared blocker scan still has zero target passes across 341 blocker sets.
- Best blocker set: `drift_p_5m_rv_15m>=0.8 AND book_p_side>=0.8`, with 88.57% current accuracy at 88.05% coverage and 88.71% v21 accuracy at 84.16% coverage.

Interpretation:

- Fresh coverage recovered above the user's 80% denominator, but the fresh sample is still far too small and the high-price candidates remain settlement-proximity candidates.
- The current raw high-price pass strengthened slightly; the nondegenerate and cross-capture frontiers did not.
- The active goal remains incomplete.

## Pure-Physics Interval Ablation

Scope:

- Removes book probability from the side-choice score.
- Side choice uses spot/strike distance, realized-volatility Brownian probabilities, drift projections, and adverse-move features.
- Ask remains only as an execution price cap, not as a model feature or chooser.

Coverage:

- Resolved intervals: 156
- Candidate pure-physics policies scanned: 5,400
- Policies covering at least 80% of intervals on every split: 3,600
- Raw target-pass policies: 20
- Nondegenerate target-pass policies: 0
- Wilson-pass policies: 0

Best raw pure-physics pass:

- Policy: `pure=brownian_p_rv_30m; brownian_p_rv_30m>=0.95; ask<=100; sec>=0; adverse15<=10`
- Selected coverage: 90.38%
- All accuracy: 98.58%
- Validation accuracy: 96.67%
- Holdout accuracy: 100.00%
- All-sample Wilson lower bound: 94.98%
- Median ask: 98.0 cents
- Median time-to-close: 169.8 seconds

Interpretation:

- Pure physics can reproduce a raw interval target pass, so the signal is not only book-price mimicry.
- It still fails the robust completion test: no nondegenerate pass, no Wilson-safe pass, and the best raw pass has a 98c median ask.
- The underlying physics signal is real only in extreme states; at economical prices and broad 80% market coverage, the accuracy frontier remains below target.

## Locked Pure-Physics Interval Monitor

Scope:

- Freezes the pure-physics interval candidates instead of reselecting the best policy after each refresh.
- Candidate definitions live in `logs/edge_research/locked_interval_pure_physics.json`.
- Lock close time: `2026-05-02T15:00:00+00:00`.
- Side choice uses pure physics features only; book probability is not used as a chooser or model feature.

Current locked pure-physics state:

- `pure_brownian_rv30_adverse15_high_price_20260502_1522`: 98.61% accuracy, 90.57% coverage, all Wilson lower bound 95.08%, median ask 98c.
- `pure_physics_mean_rv15_rv30_high_price_20260502_1522`: 98.60% accuracy, 89.94% coverage, all Wilson lower bound 95.04%, median ask 98c.
- `pure_brownian_rv15_spread4_best_high_coverage_20260502_1522`: 94.59% accuracy, 93.08% coverage, all Wilson lower bound 89.70%, median ask 95c.
- `pure_brownian_rv30_economical_adverse15_20260502_1522`: 86.23% accuracy, 86.79% coverage, all Wilson lower bound 79.50%, median ask 85.5c.

Fresh monitor state:

- Fresh resolved intervals after the 15:00 UTC lock: 12.
- All four locked pure-physics candidates selected 10 of the 12 fresh intervals, for 83.33% fresh recurring-market coverage; the three high-price/high-coverage candidates won all selected fresh intervals, while the economical pure-physics candidate went 9/10 = 90.00%.
- Fresh median asks: 97c, 96.5c, 88.5c, and 84c respectively; the two high-price pure-physics candidates each have one fresh 100c selection.
- No locked pure-physics candidate has a Wilson-robust 95% proof across splits, and twelve fresh intervals remain far below the sample-size requirement.

## V21 Native Passive Interval Validation

Scope:

- Source dataset: `research_data/live_mushroom_v21_size2`.
- Uses the native passive ticker websocket stream, not bot fills.
- Outcomes are inferred from cached Coinbase BTC 1-minute close versus the recorded market strike.
- Candidate policies are loaded from the locked pure-physics interval manifest; no threshold search is performed on this dataset.

Observed data:

- Watch markets parsed: 217
- Markets with inferred outcomes: 216
- Minute decision rows before physics: 6,446
- Minute decision rows after candle physics: 6,446
- Resolved interval denominator: 216

Locked pure-physics validation:

- `pure_brownian_rv30_adverse15_high_price_20260502_1522`: 97.87% all accuracy, 65.28% all coverage, 93.93% all Wilson lower bound, 100.00% holdout accuracy, 61.36% holdout coverage, median ask 98c.
- `pure_physics_mean_rv15_rv30_high_price_20260502_1522`: 98.58% all accuracy, 65.28% all coverage, 94.98% all Wilson lower bound, 100.00% holdout accuracy, 61.36% holdout coverage, median ask 98c.
- `pure_brownian_rv15_spread4_best_high_coverage_20260502_1522`: 93.14% all accuracy, 81.02% all coverage, 88.40% all Wilson lower bound, 89.47% holdout accuracy, 86.36% holdout coverage, median ask 95c.
- `pure_brownian_rv30_economical_adverse15_20260502_1522`: 85.56% all accuracy, 83.33% all coverage, 79.68% all Wilson lower bound, 85.71% holdout accuracy, 79.55% holdout coverage, median ask 85c.

Interpretation:

- No locked pure-physics candidate clears the 95% accuracy / 80% recurring-market coverage target on this independent native passive live websocket dataset.
- The high-accuracy candidates collapse to about 65% coverage, and the candidates that keep roughly 80% coverage fall to 85%-93% accuracy.
- This is the cleanest current falsification of the high-price pure-physics promotion story: the physics signal is real at extremes, but it does not yet span 80% of recurring BTC 15-minute markets at the required reliability.

## V21 Locked Interval Candidate Validation

Scope:

- Source dataset: `research_data/live_mushroom_v21_size2`.
- Uses the same native passive ticker websocket stream and Coinbase-close outcome inference as the v21 pure-physics validator.
- Candidate policies are loaded from the frozen simple/staged/logit manifests; no thresholds are discovered on this dataset.
- This tests whether the non-pure high-price locks generalize to a separate live capture at the recurring-market denominator.

Observed data:

- Watch markets parsed: 223
- Markets with inferred outcomes: 221
- Minute decision rows before physics: 6,554
- Minute decision rows after candle physics: 6,554
- Resolved interval denominator: 221

Frozen non-pure validation:

- `locked_logit_book_physics_c005_p095_20260502_1512`: 95.18% all accuracy, 75.11% all coverage, 90.78% all Wilson lower bound, 93.94% holdout accuracy, 73.33% holdout coverage, median ask 98c, ROI -2.69%.
- `staged_score_min_fallback_20260502_1511`: 94.83% all accuracy, 78.73% all coverage, 90.46% all Wilson lower bound, 91.89% holdout accuracy, 82.22% holdout coverage, median ask 97c, ROI -2.01%.
- `raw_regime_blend_high_price_20260502_1510`: 94.51% all accuracy, 74.21% all coverage, 89.90% all Wilson lower bound, 96.97% holdout accuracy, 73.33% holdout coverage, median ask 97c, ROI -2.63%.
- `raw_score_min_book_rv15_existing_lock`: 93.22% all accuracy, 80.09% all coverage, 88.52% all Wilson lower bound, 89.47% holdout accuracy, 84.44% holdout coverage, median ask 96c, ROI -2.31%.
- `economical_score_min_book_rv15_20260502_1511`: 88.83% all accuracy, 81.00% all coverage, 83.37% all Wilson lower bound, 91.43% holdout accuracy, 77.78% holdout coverage, median ask 89c, ROI +0.75%.

Interpretation:

- No frozen simple, staged, or logistic candidate clears the 95% accuracy / 80% recurring-market coverage split target on this independent native passive live websocket dataset.
- The locked logit is the closest on accuracy, but it fails the user's 80% market coverage floor on all, train, validation, and holdout splits.
- The candidates that reach about 80% interval coverage fall to 88.83%-93.22% all accuracy, and the staged fallback misses both the 95% accuracy floor and the 80% all-coverage floor.
- This independently rejects promoting the current high-price locked candidates as complete goal evidence.

## Cross-Dataset Interval Frontier

Scope:

- Evaluates the same simple interval policy definitions on the current two-sided heartbeat ledger and the independent v21 passive ticker ledger.
- Uses recurring BTC 15-minute markets as the volume denominator in both datasets.
- This is a stability/falsification scan, not a promotion lock.

Coverage:

- Current intervals: 156
- Current side rows: 18,034
- V21 intervals: 221
- V21 side rows: 6,554
- Shared simple policies scanned: 2,160
- Policies passing the 95% / 80% split target on both datasets: 0
- Policies passing the Wilson gate on both datasets: 0
- Nondegenerate policies passing the target on both datasets: 0

Best shared nondegenerate frontier:

- Best ranked policy: `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60`
- Current: 87.50% all accuracy at 92.31% coverage; holdout 85.71% accuracy at 87.50% coverage; median ask 86c.
- V21: 86.91% all accuracy at 86.43% coverage; holdout 89.19% accuracy at 82.22% coverage; median ask 87c.
- Other top shared nondegenerate policies remain in the same band: roughly 83%-89% accuracy while keeping 86%-96% coverage.

Interpretation:

- The stable, nondegenerate shared frontier is well below 95% accuracy.
- The current-ledger high-price passes are not stable across an independent live capture, and the stable cheap/economical rules are not accurate enough.
- This is the strongest current evidence that the remaining gap is a model/physics frontier problem, not just a threshold selection issue.

## Cross-Dataset Learned Model Transfer

Scope:

- Trains regularized logistic models and one shallow boosted-tree model on one live websocket capture's chronological train split.
- Scores the full source capture and the other capture without retraining.
- Applies fixed probability/ask/time gates to choose at most one trade per recurring BTC 15-minute market.
- Feature sets include book/physics, book/physics/price, physics-only, and path-physics features.

Coverage:

- Current intervals: 156
- Current side rows: 18,034
- V21 intervals: 221
- V21 side rows: 6,554
- Learned model/gate rows evaluated: 2,304
- Transfer target-pass rows: 0
- Transfer Wilson-pass rows: 0
- Nondegenerate transfer target-pass rows: 0

Best learned transfer rows:

- Best ranked row: train v21 -> current, `logit_C0.1`, `path_physics`, `p>=0.95; ask<=100; sec>=0`.
- Source v21: 98.00% all accuracy but only 67.87% coverage; holdout coverage 71.11%; median ask 98.5c.
- Target current: 100.00% all accuracy at 89.10% coverage; holdout 100.00% at 81.25% coverage; median ask 99c.
- Other top rows are the same high-price pattern: excellent accuracy after buying 98c-100c states, but source or independent coverage falls below the 80% floor.

Interpretation:

- Regularized learned interactions do not rescue the objective across live captures.
- The apparent current-ledger learned passes are still high-price/late-state confirmations and do not satisfy the source/independent 80% recurring-market coverage requirement.
- This rules out a simple supervised score-and-threshold repair as the next promotion path.

## Cross-Dataset Shared Loss Blockers

Scope:

- Starts from the best stable cheap shared policy: `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60`.
- Tests physical/book/path blockers before first eligible market selection, allowing the policy to wait for a later state if an early state is blocked.
- Requires the same blocker set to work on both the current heartbeat capture and the v21 passive ticker capture.

Coverage:

- Current intervals: 156
- V21 intervals: 221
- Current chosen decision rows: 9,017
- V21 chosen decision rows: 3,277
- Single blockers generated: 87
- Candidate blocker rows evaluated: 341
- Both-dataset target passes: 0
- Both-dataset Wilson passes: 0

Best blocker result:

- Best ranked blocker set: `drift_p_5m_rv_15m>=0.8 AND book_p_side>=0.8`
- Current: 88.32% all accuracy at 87.82% coverage; holdout 85.71% at 87.50% coverage; median ask 86c.
- V21: 88.71% all accuracy at 84.16% coverage; holdout 91.89% at 82.22% coverage; median ask 87c.
- Best split accuracy bottomed out at 85.71%, far below the 95% target.

Interpretation:

- Drift confirmation is useful but not sufficient.
- The cheap, stable, cross-capture frontier remains around 89% accuracy; physical blockers do not remove enough losses without breaking coverage.

## Tail-Calibrated Physics Scan

Scope:

- Tests whether the realized-volatility Brownian terminal prior is too thin-tailed for BTC 15-minute markets.
- Inflates terminal sigma by fixed multipliers before converting current margin to a physics probability.
- Uses only physics probabilities for side choice; book probability is excluded from the chooser/model feature set.
- Applies the same policy to the current heartbeat interval ledger and the independent v21 passive websocket interval ledger.

Coverage:

- Current intervals: 156; current side rows: 18,034.
- V21 intervals: 221; v21 side rows: 6,554.
- Tail-calibrated physics policies scanned: 8,100.
- Policies preserving 80% coverage on both captures/splits: 2,159.
- Policies passing 95% accuracy and 80% coverage on both captures: 0.
- Policies with 95% Wilson lower bound on both captures: 0.
- Nondegenerate both-capture target passes: 0.

Best shared tail-calibrated result:

- Policy: `tail_p_rv_15m_300>=0.6; ask<=95; sec>=60; adverse15<=10`.
- Current: 85.51% all accuracy at 88.46% coverage.
- V21: 84.78% all accuracy at 83.26% coverage.
- Worst split accuracy: 83.33%; worst split coverage: 80.00%.
- Max median ask across captures: 86c; ask=100 count: 0.

Calibration read:

- Raw `brownian_p_rv_30m` in the 0.90-0.95 probability bin is roughly calibrated but not safe enough: 95.01% current accuracy and 94.01% v21 accuracy, with median asks around 94c.
- Tail-inflated high-probability bins become perfect in these captures, but their median asks rise to 99c-100c and their seconds-to-close collapse toward settlement.
- Inflating sigma correctly makes the model more conservative, but the 80% recurring-market frontier remains around 84%-86% realized accuracy when kept nondegenerate.

Interpretation:

- The old Brownian prior is not the only problem. Fat-tail calibration does not produce a robust 95% / 80% market-interval policy.
- The high-confidence physics state exists, but it is mostly a late/high-price settlement state. At economical prices and broad coverage, terminal physics is not discriminative enough across independent live captures.

## Locked Interval Candidate Monitor

Scope:

- Freezes the current candidate definitions instead of reselecting the best policy after each refresh.
- New forward-only lock close time: `2026-05-02T15:00:00+00:00`.
- Candidates include the raw high-price regime-blend policy, the prior raw score-min policy, the economical score-min policy, and the staged score-min fallback policy.

Locked candidate current baselines:

- `raw_regime_blend_high_price_20260502_1510`: 98.60% accuracy, 89.94% coverage, median ask 97c.
- `raw_score_min_book_rv15_existing_lock`: 97.95% accuracy, 91.82% coverage, median ask 96c.
- `economical_score_min_book_rv15_20260502_1511`: 88.06% accuracy, 84.28% coverage, median ask 88c.
- `staged_score_min_fallback_20260502_1511`: 100.00% accuracy, 91.19% coverage, median ask 97c.

Fresh monitor state:

- Fresh resolved intervals after the new 15:00 UTC lock: 12.
- All four locked candidates selected 10 of the 12 fresh intervals, for 83.33% fresh recurring-market coverage; the raw/staged high-price candidates won all selected fresh intervals, while the economical candidate went 9/10 = 90.00%.
- Fresh median asks: raw regime-blend 96.5c, raw score-min 94c, economical score-min 85c, staged score-min fallback 97c.
- This lock is the right forward validation harness, but twelve post-lock intervals are far below the sample-size requirement.

## Locked Logistic Interval Monitor

Scope:

- Freezes the strongest train-only logistic interval candidate as an actual serialized model.
- Model artifact: `logs/edge_research/locked_interval_logit_model.pkl`
- Manifest: `logs/edge_research/locked_interval_logit_model.json`
- Lock close time: `2026-05-02T15:00:00+00:00`
- Candidate: `book_physics; C=0.05; p>=0.95; ask<=100; sec>=0`

Current locked-logit state:

- Current selected markets: 145/159 = 91.19% coverage
- Current selected accuracy: 100.00%
- All-sample Wilson lower bound: 97.42%
- Validation Wilson lower bound: 88.65%
- Holdout Wilson lower bound: 87.94%
- Median ask: 98c
- Ask>=95 selections: 137
- Ask=100 selections: 17
- Fresh resolved intervals after lock: 12
- Fresh selected intervals after lock: 10
- Fresh selected accuracy: 100.00%
- Fresh selected median ask: 97c

Interpretation:

- This is now a true forward-validation candidate, not merely a re-runnable scan result.
- It still carries strong high-price degeneracy flags on the pre-lock sample.
- It has only ten post-lock selected/won intervals, so it cannot complete the live verification requirement.

## Fresh Validation Requirement Audit

Scope:

- Reads the locked interval, locked pure-physics, and locked logistic monitor outputs.
- Quantifies how much post-lock evidence is required before a locked candidate can clear the 95% Wilson lower-bound gate.
- Keeps the user's volume denominator as recurring BTC 15-minute markets.

Result:

- With zero fresh losses, a candidate needs 73 selected fresh wins for the 95% Wilson lower bound to reach 95%.
- The closest locked candidates currently have 10 selected fresh wins out of 12 fresh resolved intervals.
- The closest locked candidates therefore still need 63 additional perfect selected fresh wins.
- Fresh interval coverage is currently 83.33% for the locked candidates, above the user's 80% floor but on only 12 fresh resolved intervals.

Interpretation:

- The current post-lock sample is directionally positive but cannot satisfy the live sample-size requirement.
- Ten fresh wins have only a 72.25% Wilson lower bound, so they are not completion evidence.

## Locked Fresh Skip Audit

Scope:

- Reads the frozen interval candidate, pure-physics, logistic, and fixed market-interval selected ledgers.
- Fresh denominator is recurring BTC 15-minute markets after the 2026-05-02T15:00:00Z lock.
- The audit diagnoses skipped fresh markets instead of silently treating exact 80% coverage as robust.

Result:

- Fresh denominator: 12 resolved post-lock intervals.
- Every locked candidate selected 10/12 fresh intervals and skipped the same two intervals: `KXBTC15M-26MAY021300-00`, close `2026-05-02T17:00:00Z`, and `KXBTC15M-26MAY021330-30`, close `2026-05-02T17:30:00Z`.
- The skipped markets resolved `no` and `yes`, respectively.
- The best late high-price states in the skipped markets would have won, but only at 100c with 7.2 seconds left and 4.6 seconds left.
- The best economical diagnostic states were much weaker and both lost: `score_min_book_rv15=0.53` at 59c with 82.3 seconds left, and `score_min_book_rv15=0.72` at 73c with 79.6 seconds left.

Interpretation:

- The fresh 83.33% coverage result is back above the user's floor, but remains fragile until more post-lock markets resolve.
- Forcing coverage on the skipped markets is not a clean physics repair: it either adds 100c zero-edge near-settlement trades or lowers thresholds into cheap states that lost.

## Overnight Live Bot Performance

Scope:

- Window: 2026-05-01 18:00 ET through 2026-05-02 11:24 ET.
- Reads live bot logs and execution events only; no bot logic was changed and the live bot was not stopped.
- This measures actual filled overnight behavior, not just heartbeat policy simulation.

Observed result:

- Entry fills: 37
- Contracts filled: 74
- Settlement winners: 25/37 trades = 67.57%
- Winning contracts: 50/74 = 67.57%
- Unique traded markets: 24
- Watched market intervals in window: 71
- Filled-trade market coverage: 24/71 = 33.80%
- Settlement-only gross P&L proxy: -572.0c
- Gross cash-flow plus settlement value after parsed exits: +169.0c before fees

Interpretation:

- Overnight filled-market coverage was far below the clarified 80% recurring-market target.
- Entry accuracy was far below the 95% realized-accuracy target.
- Exits improved realized cash-flow, but the entry fair-value model did not produce a high-accuracy, high-coverage trade set overnight.

## Current-v28 Prior-Failure Analysis

Scope:

- Compares current v28 filled entries, first-per-market v28 websocket opportunities, and the supplemental live_90_70 replay.
- Tests whether physical priors separate winners from losers: v28 probability, v28 edge, boundary cushion, realized-vol cushion, projected margin, and adverse drift.

Current v28 filled entries:

- Baseline: 202/251 contracts = 80.48%
- `v28 p_side>=0.85 and ask<=90`: 202/251 contracts = 80.48%, retention 100.00%
- `margin/rv15>=0.5`: 174/207 contracts = 84.06%, retention 82.47%
- `Brownian rv15 p>=0.70`: 170/201 contracts = 84.58%, retention 80.08%
- `adverse15<10 or v28 cushion>0.5`: 196/243 contracts = 80.66%, retention 96.81%

Current v28 first websocket opportunities:

- Baseline: 112/138 contracts = 81.16%
- `v28 p_side>=0.85 and ask<=90`: 112/138 contracts = 81.16%, retention 100.00%
- `margin/rv15>=0.5`: 98/116 contracts = 84.48%, retention 84.06%
- `Brownian rv15 p>=0.70`: 92/108 contracts = 85.19%, retention 78.26%
- `adverse15<10 or v28 cushion>0.5`: 108/132 contracts = 81.82%, retention 95.65%

Supplemental live_90_70 replay contrast:

- Baseline: 4903/4983 contracts = 98.39%
- `margin/rv15>=0.5`: 3760/3830 contracts = 98.17%, retention 76.86%
- `Brownian rv15 p>=0.70`: 3690/3760 contracts = 98.14%, retention 75.46%
- `adverse15<10 or v28 cushion>0.5`: 4220/4290 contracts = 98.37%, retention 86.09%

Interpretation:

- The current-v28 prior is miscalibrated before execution: v28-approved websocket opportunities are only about 81% accurate, close to the filled-entry result.
- The issue is not merely slippage or fill selection.
- Several physical features are regime-dependent. In current v28, larger signed movement and cushion weakly help; in live_90_70, the few losses often appear at larger cushions and longer time-to-close. A monotonic cushion-only fair-value prior is not stable enough for promotion without a regime gate.
- This supports continuing fresh shadow validation and rejects further threshold tuning on the old current-v28 holdout.

## 2026-05-02 21:27 UTC Continuation Update

New research-only artifacts added after the prior audit:

- `probe_cross_dataset_path_stability_gates.py`
- `logs/edge_research/cross_dataset_path_stability_gates_latest.md`
- `probe_cross_dataset_empirical_survival.py`
- `logs/edge_research/cross_dataset_empirical_survival_latest.md`
- `probe_cross_dataset_profit_frontier.py`
- `logs/edge_research/cross_dataset_profit_frontier_latest.md`
- `probe_profit_frontier_fresh_validation.py`
- `logs/edge_research/profit_frontier_fresh_validation_latest.md`
- `logs/edge_research/profit_frontier_fresh_lock.json`
- `probe_profit_challenger_fresh_validation.py`
- `logs/edge_research/profit_challenger_fresh_validation_latest.md`
- `logs/edge_research/profit_challenger_fresh_lock.json`
- `probe_profit_lock_sample_size_requirements.py`
- `logs/edge_research/profit_lock_sample_size_requirements_latest.md`
- `probe_profit_lock_bayesian_ev_monitor.py`
- `logs/edge_research/profit_lock_bayesian_ev_monitor_latest.md`
- `probe_profit_lock_forward_cycle.py`
- `logs/edge_research/profit_lock_forward_cycle_latest.md`
- `probe_profit_lock_pending_signal_monitor.py`
- `logs/edge_research/profit_lock_pending_signal_monitor_latest.md`
- `probe_profit_touch_hazard_frontier.py`
- `logs/edge_research/profit_touch_hazard_frontier_latest.md`
- `probe_profit_touch_hazard_fresh_validation.py`
- `logs/edge_research/profit_touch_hazard_fresh_validation_latest.md`
- `logs/edge_research/profit_touch_hazard_fresh_lock.json`
- `probe_profit_fresh_loss_attribution.py`
- `logs/edge_research/profit_fresh_loss_attribution_latest.md`

Latest refreshed heartbeat and interval state:

- Two-sided heartbeat refresh: 20,974 raw rows, 20,840 rows with candle physics, 180 unique markets, 2,686 primary minute-bucket opportunities, zero target-pass models.
- Recurring-market interval scan: 169 resolved markets, 2,160 candidate policies, 1,657 coverage-pass policies, 35 raw 95%/80% target passes, zero nondegenerate target passes.
- Best refreshed raw interval pass is still high-price: `book_p_side>=0.95; ask<=100; sec_to_close>=0`, 97.59% accuracy at 98.22% coverage with 96c median ask.
- Best refreshed nondegenerate 80%-coverage accuracy frontier remains below target: `score_min_book_rv15>=0.8; ask<=95; sec_to_close>=60`, 87.41% accuracy at 84.62% coverage with 88c median ask; `score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60` covers 92.90% but only reaches 87.26% accuracy.

New falsifiers for the literal 95% accuracy / 80% recurring-market target:

- Cross-dataset path-stability gates tested 3,220 rows across 166 current intervals and 221 v21 intervals. Both-dataset target passes: zero. Best shared 80%-coverage row reached 88.00% current accuracy and 87.30% v21 accuracy.
- Empirical survival tables trained on one capture and transferred to the other tested 3,840 rows. Transfer target passes: zero. The best rows hit 100% OOS accuracy only by falling to about 53%-56% coverage with 98c-99c median asks.

Profit-frontier result:

- A separate fee-aware profit scan evaluated 2,880 simple policies on the refreshed 169-current / 221-v21 interval datasets.
- 2,068 policies met 80% recurring-market coverage on both datasets.
- 531 policies were net profitable on validation and holdout splits across both datasets.
- 24 policies were net profitable on all train/validation/holdout splits across both datasets.
- Best refreshed coverage-valid profit row: `choose=score_mean_book_rv15_drift5; score_mean_book_rv15_drift5>=0.55; ask<=95; sec_to_close>=120; brownian15>=0.55_and_brownian30>=0.55`.
- That row has current +205c net, 1.92% ROI, 64.88% accuracy, 99.41% coverage, 61.5c max median ask; v21 +833c net, 5.96% ROI, 67.58% accuracy, 99.10% coverage; minimum validation/holdout ROI across both datasets is 2.52%.

Touch-hazard profit frontier:

- `probe_profit_touch_hazard_frontier.py` added a first-passage-style touch prior: if normalized margin to strike is small, terminal Brownian probability is discounted by the probability of touching the adverse boundary before close.
- It scanned 1,440 fee-aware policies across 172 current intervals and 221 v21 intervals.
- 1,328 policies preserved at least 80% recurring-market coverage on both datasets, 444 were profitable on validation and holdout splits, and 32 were profitable on every train/validation/holdout split across both datasets.
- Best all-split-positive touch-hazard row: `choose=book_touch_blend_15; book_touch_blend_15>=0.35; 0<=ask<=80; sec>=120; gate=none`.
- That row has current +524c net, 5.20% ROI, 61.99% accuracy, 99.42% coverage; v21 +711c net, 5.56% ROI, 61.93% accuracy, 98.64% coverage; minimum validation/holdout ROI is 2.36%, max median ask is 55.5c, and ask=100 count is zero.
- A separate forward lock was created for this candidate at `2026-05-02T22:00:00+00:00`.

Locked fresh profit validation:

- The first profit-frontier candidate remains locked instead of being retuned after seeing the fresh markets.
- Locked policy: `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.55; ask<=95; sec_to_close>=120; adverse15<=10_or_margin_rv15>=0.5`.
- Lock close time: `2026-05-02T20:30:00+00:00`.
- After the latest refresh, fresh post-lock sample is 14/14 selected markets, 8 wins / 6 losses, -126c net, -13.61% ROI, 100% recurring-market coverage.
- The fresh Wilson lower bound is only 32.59%, and the fresh net remains negative, so this is not promotion-quality evidence.

Locked profit stability audit:

- `probe_locked_profit_candidate_stability.py` created a no-trade stability audit and selected-row ledgers for the locked profit candidate.
- Current full ledger: 167/169 markets selected, 111 wins / 56 losses, +400c net, 3.74% ROI, 98.82% coverage.
- V21 full ledger: 219/221 markets selected, 154 wins / 65 losses, +1,194c net, 8.40% ROI, 99.10% coverage.
- Weakness: current train split is negative at -95c; current bootstrap mean-edge p05 is -3.6c and bootstrap probability of nonpositive mean edge is 24.9%.
- V21 is stronger: bootstrap mean-edge p05 is +0.5c and probability of nonpositive mean edge is 3.5%.
- Unseen-loss stress: current aggregate profit can be erased by about 7 typical extra losses or 5 worst-case extra losses; fresh +16c can be erased by one ordinary loss.
- Weak current slices include low RV15 bin, earliest time block, adverse15>20, 70c-80c asks, and margin_rv15 0.25-0.5.

Locked profit blocker overlays:

- `probe_locked_profit_candidate_blocker_overlays.py` scanned 180 simple causal overlays on top of the locked candidate while preserving one-trade-per-market selection.
- 157 overlays preserved 80% recurring-market coverage on both current and v21.
- 15 overlays preserved 80% coverage and were positive on every train/validation/holdout split across both datasets.
- Best coverage-preserving all-split-positive overlay: `ask>=50 AND ask<=80`.
- `ask>=50 AND ask<=80` results at scan time: current +661c net, 6.21% ROI, 68.90% accuracy, 97.04% coverage; v21 +1,151c net, 8.31% ROI, 70.75% accuracy, 95.93% coverage; fresh post-lock +16c on 3/3 selected markets.
- Simpler overlay `ask>=50` is nearly as good and preserves more coverage: current +671c, 6.14% ROI, 69.46% accuracy, 98.82% coverage; v21 +1,186c, 8.17% ROI, 71.69% accuracy, 99.10% coverage; fresh post-lock +16c on 3/3 at scan time.
- Interpretation: the sub-50c entries appear structurally toxic in both datasets. This is a useful physical prior: extremely cheap apparent edges are often low-probability traps, not mispriced convexity.
- The overlay is a challenger only. It should get its own forward lock before any live-code promotion; replacing the existing lock after seeing fresh markets would contaminate forward validation.

Separate challenger forward lock:

- `probe_profit_challenger_fresh_validation.py` created a separate forward-validation lock for the best all-split-positive overlay.
- Challenger: base locked policy plus overlay `ask>=50 AND ask<=80`.
- Challenger lock close time: `2026-05-02T21:15:00+00:00`.
- Lock file: `logs/edge_research/profit_challenger_fresh_lock.json`.
- Current all-ledger challenger state after the latest refresh: 174/180 markets selected, 119 wins / 55 losses, 68.39% accuracy, 96.67% coverage, +589c net, 5.21% ROI, 62c median ask.
- Fresh after challenger lock after the latest refresh: 10/11 selected markets, 6 wins / 4 losses, -72c net, -10.71% ROI, 90.91% coverage.

Separate touch-hazard forward lock:

- `probe_profit_touch_hazard_fresh_validation.py` created a separate forward-validation lock for the first-passage/touch-hazard candidate.
- Touch-hazard policy: `choose=book_touch_blend_15; book_touch_blend_15>=0.35; 0<=ask<=80; sec>=120; gate=none`.
- Touch-hazard lock close time: `2026-05-02T22:00:00+00:00`.
- Current all-ledger touch state after the latest refresh: 179/180 markets selected, 111 wins / 68 losses, 62.01% accuracy, 99.44% coverage, +547c net, 5.18% ROI, 56c median ask.
- Fresh after touch lock after the latest refresh: 8/8 selected markets, 5 wins / 3 losses, +23c net, 4.82% ROI, 100% coverage.

Profit lock sample-size requirements:

- `probe_profit_lock_sample_size_requirements.py` created a combined EV sample-size monitor for the original, challenger, and touch-hazard forward locks.
- EV proof gate used here: positive fresh net P&L, at least 80% fresh recurring-market coverage, and fresh Wilson lower bound above average fee-aware break-even probability.
- Original lock currently fails the EV sample-size gate: 14/14 fresh selected, 8/6 wins/losses, 57.14% accuracy, 66.14% break-even, 32.59% Wilson lower, -126c net.
- Original lock needs 20 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state. If the all-ledger observed accuracy and break-even persisted, it would need about 4,079 selected fresh markets for Wilson-over-break-even proof.
- Challenger lock currently fails the EV sample-size gate: 10/11 fresh selected, 6/4 wins/losses, 60.00% accuracy, 67.20% break-even, 31.27% Wilson lower, -72c net.
- Challenger lock needs 17 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state. If the all-ledger observed accuracy and break-even persisted, it would need about 718 selected fresh markets for Wilson-over-break-even proof.
- Touch-hazard lock currently fails on sample size and posterior confidence despite positive net: 8/8 fresh selected, 5/3 wins/losses, 62.50% accuracy, 59.62% break-even, 30.57% Wilson lower, +23c net.
- Touch-hazard lock needs 10 additional perfect selected fresh wins to clear Wilson over break-even from the current fresh state. If the all-ledger observed accuracy and break-even persisted, it would need about 937 selected fresh markets for Wilson-over-break-even proof.

Bayesian/sequential EV monitor and repeatable forward cycle:

- `probe_profit_lock_bayesian_ev_monitor.py` adds a neutral Beta(1,1) posterior monitor using only fresh post-lock outcomes.
- Bayesian ready gate: at least 30 fresh selected markets, at least 80% fresh coverage, positive fresh net, posterior probability that true win rate exceeds fee-aware break-even at least 95%, and positive p05 posterior edge.
- Original lock posterior: fresh 8/6 wins/losses, posterior mean win rate 56.24%, posterior P(p>break-even) 0.215, p05 posterior edge -30.2c, mean posterior edge -9.9c. It needs 17 additional perfect fresh wins for the posterior probability gate.
- Challenger lock posterior: fresh 6/4 wins/losses, posterior mean win rate 58.29%, posterior P(p>break-even) 0.274, p05 posterior edge -32.2c, mean posterior edge -8.9c. It needs 15 additional perfect fresh wins for the posterior probability gate.
- Touch-hazard lock posterior: fresh 5/3 wins/losses, posterior mean win rate 59.97%, posterior P(p>break-even) 0.526, p05 posterior edge -25.1c, mean posterior edge +0.3c. It needs 8 additional perfect fresh wins for the posterior probability gate.
- `probe_profit_lock_forward_cycle.py` creates a one-shot refresh/validation cycle for the locked tracks. It reruns the original fresh validator, challenger fresh validator, touch-hazard fresh validator, Wilson sample-size monitor, and Bayesian EV monitor without running optimizers or updating locks.
- Latest forward cycle completed with zero failed steps and zero ready locks.

Pending signal registry:

- `probe_profit_lock_pending_signal_monitor.py` registers the first eligible post-lock signal per market from raw heartbeat rows before outcome is available, then updates outcomes on later runs.
- The pending monitor now uses closed-market-only outcomes for resolved status, so pre-close decisive quote states are not treated as settled evidence.
- Latest registry: 35 registered signals. Original has 15 registered, 1 pending, 14 resolved, 8 wins / 6 losses, -126c resolved net; challenger has 11 registered, 1 pending, 10 resolved, 6 wins / 4 losses, -72c resolved net; touch-hazard has 9 registered, 1 pending, 8 resolved, 5 wins / 3 losses, +23c resolved net.
- The current unresolved pending signal for all three locks is `KXBTC15M-26MAY022015-15`, so the next settlement will update every forward track without retuning.

Fresh loss attribution:

- `probe_profit_fresh_loss_attribution.py` summarizes the locked registry without retuning and keeps pending markets out of resolved accuracy/P&L.
- Across 32 resolved fresh lock observations, the Brownian-derived original/challenger locks are losing mainly in low normalized-margin states: original margin `(0.0, 0.25]` is 4/6 with -218c net, and challenger margin `(0.0, 0.25]` is 3/4 with -148c net.
- Touch-hazard remains the only fresh-positive lock: 5/3 with +23c net. Its negative-margin bin is 4/1 with +89c, which supports the idea that first-passage/survival pricing is capturing something terminal Brownian margin was throwing away.
- Touch-hazard losses still cluster in thin-margin / no-adverse-cushion rows: margin `(0.0, 0.25]` is 1/2 with -66c, adverse15 `<=0` is 1/2 with -71c, and the single sub-50c ask lost for both original and touch-hazard. These are hypotheses only because each bin is still tiny.

Interpretation:

- The strongest new physics read is still that the 95% hit-rate objective and the profit objective are diverging. Broad profitable policies exist because the break-even probability is near 59%-64%, not because hit rate is near 95%.
- The first-passage/touch-hazard prior remains the most useful new candidate by cross-dataset EV and is now slightly positive on fresh settled P&L, but 8 fresh markets is still far too small for promotion. The fresh-loss attribution makes this more concrete: the old terminal/rv prior is losing in low-margin states, while the touch-hazard prior is at least separating some of those boundary-risk states into profitable prices.
- For recurring BTC 15-minute markets, the better prior is now fee-aware expected value versus ask cost, with fresh locked validation, rather than trying to force every high-coverage policy into a 95% realized-accuracy frame.
- The goal remains incomplete because the original and challenger locks are negative on fresh settled P&L, the touch-hazard lock has only 8 settled fresh markets and weak posterior confidence, and the live bot logic remains unchanged by design.

## 2026-05-03 02:27 UTC Continuation Update

New research-only changes after the prior audit:

- `probe_live_9070_v28_replay.py` candle fetch helper now retries 60-minute Coinbase chunks and skips only a repeatedly failing upstream chunk, preventing transient HTTP 500 errors from killing the research refresh.
- `probe_profit_lock_pending_signal_monitor.py` now tracks the touch-overlay and kinetic-touch locks and continues to use closed-market-only settlement outcomes.
- `probe_profit_kinetic_touch_fresh_validation.py` was added as a separate forward lock for the refreshed kinetic touch candidate.
- `probe_kinetic_touch_stability_audit.py` was added to stress the kinetic-touch lock across splits, regimes, bootstrap edge, and unseen-loss scenarios.
- `probe_kinetic_touch_blocker_overlays.py` found a post-outcome diagnostic guard, and `probe_kinetic_guard_fresh_validation.py` froze it as a separate forward-only challenger.
- `probe_kinetic_guard_physics_sanity.py` tests nearby guard families to separate real physics from a one-loss scar.
- `probe_kinetic_price_guard_fresh_validation.py` froze the broader price/adverse guard `adverse15<=100 AND ask<=70` as a separate forward-only challenger.
- `probe_profit_lock_forward_cycle.py`, `probe_profit_lock_sample_size_requirements.py`, `probe_profit_lock_bayesian_ev_monitor.py`, and `probe_profit_lock_pending_signal_monitor.py` now include the kinetic-touch, kinetic-guard, and kinetic-price-guard locks.

Current refreshed evidence:

- Latest two-sided heartbeat refresh: `20260503_031830Z`; 21,678 raw two-sided rows, 21,434 rows with candle physics, 186 unique markets, 2,763 primary minute-bucket opportunities, zero target-pass models.
- Latest touch-hazard frontier: `20260503_022110Z`; 1,440 policies scanned across 182 current intervals and 221 v21 intervals. 1,328 preserved 80% coverage on both datasets; 533 were profitable on validation and holdout splits; 59 were positive on every train/validation/holdout split across both datasets.
- Updated best broad EV row: `choose=kinetic_touch_score_15; kinetic_touch_score_15>=0.55; 50<=ask<=95; sec>=120; gate=touch_loss15<=0.90`.
- Kinetic row all-ledger evidence after the first four forward signals: current 184/186 markets, 128 wins / 56 losses, 69.57% accuracy, 66.07% break-even, 98.92% coverage, +644c net, 5.30% ROI; v21 +860c net, 5.91% ROI, 70.32% accuracy, 99.10% coverage.
- Kinetic lock: `logs/edge_research/profit_kinetic_touch_fresh_lock.json`, close time `2026-05-03T02:15:00+00:00`; fresh after lock is now 4/4 selected with 3 wins / 1 loss, +33c net by the fresh validator.
- The 03:15 UTC kinetic-family signal resolved as a win for NO. Kinetic-touch is now 3/1, kinetic-guard is 3/0, and kinetic-price-guard has its first valid settled fresh win.
- Latest forward cycle: `20260503_031730Z`; zero failed steps and zero ready locks.
- Latest pending registry: 66 total signals. Resolved state: original 11/8 for about -160c, challenger 9/6 for about -106c, touch-hazard 7/6 for -69c, touch-overlay 2/3 for -92c, kinetic-touch 3/1 for +33c to +39c depending fee accounting path, kinetic-guard 3/0 for +78c, and kinetic-price-guard 1/0 for +36c. No kinetic-family signal is pending as of `20260503_031940Z`; touch-hazard and touch-overlay have a 03:30 UTC pending signal.
- Latest sample-size monitor: no lock clears the EV sample-size gate. Perfect-win requirement from current state: original 23, challenger 20, touch-hazard 14, touch-overlay 12, kinetic-touch 10, kinetic-guard 8, kinetic-price-guard 6.
- Latest Bayesian EV monitor: no lock clears the posterior gate. Posterior P(p>break-even): original 0.198, challenger 0.253, touch-hazard 0.332, touch-overlay 0.202, kinetic-touch 0.538, kinetic-guard 0.701, kinetic-price-guard 0.589.
- Kinetic stability audit: all chronological splits are still positive on current and v21, but bootstrap p05 mean edge is negative on both datasets. Current bootstrap P(mean edge <= 0) improved to 0.156; v21 is 0.098. At the observed all-ledger accuracy/break-even, Wilson-over-break-even proof would require about 713 selected current markets or 566 selected v21 markets.
- Kinetic weak slices: current adverse15 > 20 is 27/17 with -329c net; current time block 3 is 21/15 with -224c; current 80c-90c asks are 2/2 with -136c; v21 70c-80c asks are 23/11 with -289c; v21 first time block is 27/17 with -242c. These are diagnostics only, not new gates, because using them now without a separate lock would retune on known outcomes.
- Kinetic guard sanity audit: 83 nearby causal guard definitions scanned; 81 preserved 80% coverage across both datasets and 43 were all-split-positive. The first locked guard `kinetic>=0.57 AND adverse15<=50` improves current by +56c but worsens v21 by -77c, so it remains suspect as a current-specific repair.
- Broader price/adverse guard: `adverse15<=100 AND ask<=70` is the top current refreshed sanity row, with current +871c / 7.83% ROI / 69.36% accuracy / 93.01% coverage and v21 +1200c / 9.52% ROI / 70.05% accuracy / 89.14% coverage. It was frozen separately at `logs/edge_research/profit_kinetic_price_guard_fresh_lock.json`; after questioning the entry-time prior, its lock boundary was corrected to the next full 15-minute market close, `2026-05-03T03:00:00+00:00`, so the pre-lock 03:00 win is not counted as fresh evidence. Fresh after lock is now 1/1 with 1 win and +36c net.

Current physics interpretation:

- The first-passage/touch idea is still useful, but the latest forward loss falsifies treating adverse touch as a hard settlement truth. BTC can touch the adverse side and recover before the 15-minute close.
- The refreshed kinetic candidate treats touch as one uncertainty term alongside book probability, terminal Brownian probability, recent drift, and adverse velocity. That is more physically plausible than using touch survival alone.
- The improved retrospective EV surface is not promotion evidence. It was selected after new outcomes were known, so it now has its own forward-only lock and must earn fresh sample size.
- The kinetic stability audit argues for patience: the all-ledger row is profitable, but its first forward signal lost, the edge is small enough that a few ordinary losses can erase it, and several physically plausible slices remain weak.
- The first kinetic guard (`kinetic>=0.57 AND adverse15<=50`) is not a universally dominant prior: it helps the current ledger but worsens v21 versus unguarded kinetic. The broader price/adverse guard (`adverse15<=100 AND ask<=70`) is more physically coherent because it targets expensive/fee-sensitive entries and extreme adverse motion, improves both current and v21 in the sanity audit, and now has its own forward lock.

## 2026-05-03 03:35 UTC Strict-Boundary Refresh

Research-only changes since the prior continuation:

- Added `probe_profit_lock_time_boundary.py` and wired the fresh validators, pending registry, stability audit, and blocker overlays to use an effective entry boundary: max(stored lock close time, next full 15-minute market close after lock creation).
- Re-filtered the pending registry so pre-boundary rows are not counted as forward evidence. This removed retroactive/action-impossible entries and re-registered only signals that could have been taken after a lock existed.
- Added and ran `probe_kinetic_price_adverse_plateau.py` to test whether the best price/adverse guard sits on a broad physical surface or an isolated threshold.
- Added and ran `probe_kinetic_fresh_failure_attribution.py` to record the actual path physics of the new fresh kinetic loss.
- Reran the full forward cycle, kinetic-touch stability audit, kinetic-guard sanity audit, kinetic-touch blocker overlays, sample-size monitor, Bayesian EV monitor, and pending signal monitor without touching live bot logic or placing orders.

Current strict-boundary evidence:

- Latest heartbeat refresh: `20260503_040221Z`; 22,018 raw two-sided rows, 21,780 rows with candle physics, 189 recurring markets, 2,808 primary minute-bucket opportunities, and zero literal 95%-accuracy / 80%-coverage target-pass models.
- Latest forward cycle: `20260503_040119Z`; all steps succeeded and no lock is ready for promotion.
- The 04:00 UTC market settled YES. All registered locks that fired on it won, including kinetic-touch YES at 71c, kinetic-guard YES at 71c, and kinetic-price-guard YES at 70c.
- Kinetic-touch all-current ledger: 187/189 markets, 130 wins / 57 losses, 69.52% accuracy, 66.04% break-even, 98.94% coverage, +651c net, 5.27% ROI. V21 remains +860c at 99.10% coverage.
- Kinetic-touch fresh after strict lock boundary: 6/6 selected, 5/1, +105c. Wilson lower bound is only 43.65%, so this is still not sample-size proof.
- Kinetic-guard fresh after strict boundary: 5/5 selected, 4/1, +59c. The sanity audit still flags it because `kinetic>=0.57 AND adverse15<=50` improves current by +51c but worsens v21 by -77c versus unguarded kinetic.
- Kinetic price/adverse guard `adverse15<=100 AND ask<=70`: all-current 176/189 markets, 122 wins / 54 losses, 69.32% accuracy, 64.32% break-even, 93.12% coverage, +879c net, about 7.8% ROI; v21 is +1200c at 89.14% coverage. Fresh after strict boundary is 4/4, 3/1, +44c.
- Price/adverse plateau diagnostic at `20260503_040302Z`: 84 nearby guards scanned; 70 preserve 80% coverage on both datasets and 62 are all-split-positive. The exact `adverse15<=100 AND ask<=70` row remains rank 1 by combined delta, but only 3/9 local neighbors improve both current and v21 versus unguarded kinetic, so the threshold is promising but locally fragile.
- Kinetic overlay scan at `20260503_040302Z`: 36 simple causal overlays scanned, all preserve 80% coverage on both datasets, 13 are all-split-positive. The best all-split-positive overlay is now the existing locked guard `kinetic>=0.57 AND adverse15<=50`, but it still lowers v21 net versus the unguarded kinetic row, so it is diagnostic only rather than promotion evidence.
- The tempting post-loss book-floor repair is not clean: `book>=0.55` would avoid the latest kinetic loss and keeps ~99% coverage, but v21 holdout is -98c; `book>=0.60` is stronger on current and fresh but has v21 train -101c. Do not promote a book floor without a separate future lock.
- Fresh failure attribution at `20260503_040302Z`: the losing kinetic-family row entered NO at 52c with book probability only 0.515 but Brownian15 0.681 and kinetic score 0.591. Within about 60 seconds the opposite YES mid was 66c; by 5 minutes it was 92c; near close it was 100c. This is a path-flip failure, not a slow terminal miss.
- Pending registry at `20260503_040041Z`: 76 registered signals. Kinetic-family locks have no unresolved signal after the 04:00 settlement; touch-hazard and touch-overlay have a new 04:15 UTC NO signal pending.
- Strict fresh lock summary: original 10/8 for -162c, challenger 9/7 for -136c, touch-hazard 7/7 for -116c, touch-overlay 4/3 for +4c, kinetic-touch 5/1 for +105c, kinetic-guard 4/1 for +59c, kinetic-price-guard 3/1 for +44c.
- Sample-size monitor: no lock clears the Wilson EV gate. Extra perfect wins needed: original 22, challenger 20, touch-hazard 16, touch-overlay 9, kinetic-touch 7, kinetic-guard 9, kinetic-price-guard 8.
- Bayesian EV monitor: no lock clears the posterior gate. Posterior P(win rate > break-even): original 0.196, challenger 0.218, touch-hazard 0.257, touch-overlay 0.487, kinetic-touch 0.752, kinetic-guard 0.618, kinetic-price-guard 0.592.

Updated physics read:

- The timing correction matters. Counting a signal before the lock existed was not forward validation; using the next full 15-minute close is the stricter actionable prior.
- First-passage/touch is useful as hazard, not as destiny. The current better physical story is kinetic survival: book-implied side pressure, terminal diffusion, short-horizon drift, adverse velocity, and touch-loss probability all contribute, while high ask and extreme adverse movement cap the usable edge.
- The broad kinetic-touch row keeps almost all recurring markets. The price/adverse guard sacrifices some volume but still clears the user's 80% recurring-market constraint on both datasets and has the cleanest cross-dataset EV profile so far, though the local plateau is mixed enough to require forward proof rather than confidence from neighboring thresholds. A live book floor is physically plausible after the latest loss, but current cross-split evidence says it is not stable enough to freeze blindly.
- None of the forward locks is promoted. The kinetic family remains the leading hypothesis by cross-dataset EV, but the latest loss proves the fresh edge is thin and still highly path-regime dependent.

## Current Active-Goal Checklist

| requirement | current evidence | result |
|---|---|---|
| Improve fair value / selection toward profit and physical accuracy | Kinetic-touch is the broad EV surface; the first guard is fresh-positive but not cross-dataset dominant; the broader price/adverse guard improves both current and v21 sanity ledgers and recovered to 3/1 fresh for +44c after the 04:00 win | candidate found, not promoted |
| Trade at least 75%-80% of recurring BTC 15-minute markets | Kinetic-touch covers 187/189 current and 219/221 v21 markets; price/adverse guard covers 176/189 current and 197/221 v21 markets, still above the 80% recurring-market denominator | met retrospectively, pending fresh proof |
| Avoid overfit | Original, challenger, touch-hazard, touch-overlay, kinetic-touch, kinetic-guard, and kinetic-price-guard are separate locks; effective lock boundaries now prevent pre-lock markets from entering fresh proof | process met |
| Verify with live data and sample size | Fresh locked evidence is still weak or negative except tiny kinetic samples: original -162c, challenger -136c, touch-hazard -116c, touch-overlay +4c, kinetic-touch +105c on 6 settled markets, kinetic-guard +59c on 5 settled markets, price/adverse guard +44c on 4 settled markets; no Wilson or Bayesian gate is ready | not met |
| Keep bot code/process untouched | Only standalone probes and `logs/edge_research` artifacts changed; no live bot logic or orders touched | met |
| Question priors / focus on physics | New evidence rejects touch-as-hard-veto, distrusts a guard that only fixes current, enforces actionable lock timing, and shifts toward kinetic blend plus explicit price/adverse stress control | met for research |

## Historical Prompt-to-Artifact Checklist

| requirement | evidence | result |
|---|---|---|
| Find a fair-value model version / selected trade rule | Fixed physics rule `ask<=100; block 15m adverse>10 unless v28 cushion>0.5` passes pooled independent historical-live validation; refreshed raw interval policy `score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0`, locked pure-physics `brownian_p_rv_30m>=0.95; adverse15<=10`, frozen logistic policy `book_physics; C=0.05; p>=0.95; ask<=100; sec>=0`, and staged interval policies clear the literal interval target on the current ledger, but independent v21 validation rejects the frozen pure-physics, simple, staged, and logit candidates; the shared cross-dataset simple-policy scan has zero target passes; the learned cross-dataset transfer probe has zero target passes; the tail-calibrated physics scan has zero shared target passes across 8,100 physics-only policies; the new touch-hazard EV rule is cross-dataset profitable at 98.64%-99.42% coverage but only ~62% hit rate | met only as candidate hypotheses |
| At least 95% realized accuracy | Fixed rule reaches 95.12% pooled independent contract accuracy and 96.28% trade accuracy; refreshed raw interval pass reaches 99.29% on 139/140 selected intervals with all-sample Wilson lower bound 96.07%, but validation/holdout Wilson lower bounds are only 87.54%/87.54% and the median ask is 98c; locked pure-physics raw pass reaches 98.61% all accuracy but remains high-price/degenerate with median ask 98c; v21 native passive validation keeps the two highest-accuracy pure-physics candidates at 97.87%-98.58% but only at 65.28% coverage and below the Wilson gate; v21 locked-candidate validation puts the frozen logit at 95.18% all accuracy but only 93.94% holdout accuracy and 90.78% all Wilson lower bound; frozen logistic current pass is 100.00% on 145/159 intervals but validation/holdout Wilson lower bounds are 88.65%/87.94%; locked staged fallback reaches 100.00% on the current ledger but only 94.83% on v21; current v28 shadow-selected sample is 80.66% all-contract accuracy and 60.87% holdout-contract accuracy; refreshed overnight filled entries were 67.57% | partially met historically/raw, not statistically/current-live verified |
| Keep at least 75%-80% volume | User clarified the denominator as recurring BTC 15-minute markets. Refreshed raw interval pass covers 88.05% of resolved intervals but is high-price/degenerate; locked pure-physics raw pass covers 90.57% but is high-price/degenerate; v21 native passive validation pushes the high-accuracy pure-physics candidates down to 65.28% coverage, while the 81%-83% coverage pure-physics candidates reach only 85.56%-93.14% accuracy; v21 locked-candidate validation puts the frozen logit at 75.11% all coverage and the frozen staged candidate at 78.73% all coverage, while the frozen candidates that reach 80%+ coverage fall below 95% accuracy; the best refreshed shared cross-dataset nondegenerate policy covers 96.86% current and 92.31% v21 but reaches only 85.71% and 87.75% accuracy; the best learned transfer row reaches 100% current accuracy at 89.10% current coverage but only 67.87% source-v21 coverage; the best shared blocker keeps 88.05% current and 84.16% v21 coverage but reaches only 88.57% and 88.71% accuracy; the best tail-calibrated physics policy keeps 88.46% current and 83.26% v21 coverage but reaches only 85.51% and 84.78% accuracy; locked staged fallback covers 91.19% on the current ledger but is still high-price/degenerate; best economical 80%-coverage policy covers 92.45% but only reaches 87.76% accuracy; the touch-hazard EV rule covers 99.42% current and 98.64% v21; refreshed overnight filled-market coverage was 33.80% | partially met by EV simulation, not by 95%-accuracy live bot fills |
| Not overfit | Fixed rule was discovered on live_90_70 and validated on pooled independent resolved live ledgers; it still fails some off-policy tapes and current v28. Locked pure-physics and non-pure interval policies were separately tested on v21 native passive websocket data without retuning, and none passed | partially met |
| Verified with live data | Current v28 execution logs, current v28 websocket opportunities, broader live heartbeat favorite rows, two-sided heartbeat side-choice rows, live_90_70 labels, independent stats live ledgers, and v21 native passive websocket ticker data were all used with public metadata/BTC candle backfill | partially met |
| Verified with sample size | Pooled independent fixed-rule sample is 296 trades / 1,517 contracts; v21 native passive pure-physics validation has 216 resolved intervals and 6,446 minute decision rows with zero locked pure-physics target passes; v21 locked-candidate validation has 221 resolved intervals and 6,554 minute decision rows with zero frozen simple/staged/logit target passes; refreshed cross-dataset scan evaluates 2,160 shared simple policies across 159 current intervals and 221 v21 intervals with zero joint target passes; learned transfer probe evaluates 2,304 model/gate rows across the same interval datasets with zero transfer target passes; refreshed shared blocker scan evaluates 341 blocker sets across the 159/221 interval datasets with zero joint target passes; tail-calibrated physics scans 8,100 physics-only policies across the 156/221 interval datasets with zero joint target passes; current v28 shadow sample is 127 resolved trades / 251 baseline contracts and 123 selected trades / 243 selected contracts but remains holdout-infeasible; current v28 opportunity sample is 69 resolved primary markets / 138 contracts and fails scanned rules; heartbeat favorite audit has 2,129 primary minute-bucket states / 8,265 candle-backed states and fails; latest two-sided heartbeat audit has 2,686 primary opportunities and zero target-pass models; touch-hazard EV scan tests 1,440 policies and finds 32 all-split-positive 80%-coverage rows, but the touch-hazard forward lock has only 8 settled fresh markets; refreshed 80%-retention regime scan tests 3,144 candidates with zero target-pass; recurring interval scan has 159 resolved markets and raw pass has 139/140 wins, but validation/holdout Wilson lower bounds remain 87.54%/87.54%; pure-physics ablation tests 5,400 policies with 20 raw target passes, zero nondegenerate passes, and zero Wilson passes; locked pure-physics monitor has 10 selected/won post-lock intervals out of 12 resolved intervals after its 2026-05-02T15:00:00Z lock; interval blocker scan tests 47 focused policies with zero target-pass and zero Wilson-pass; path-physics blocker scan tests 14 path/fade blockers with zero target-pass and zero Wilson-pass; chronological logistic scan tests 1,440 policies with 9 raw target passes but zero Wilson-pass; frozen logistic monitor has 10 selected/won post-lock intervals out of 12 resolved intervals after its 2026-05-02T15:00:00Z lock; staged interval scan tests 1,152 policies with 108 raw target passes but zero less-degenerate target passes; fresh-after-lock fill sample remains below sample-ready | partially met, not sufficient for goal completion |
| Do not change existing bot logic/code | Only standalone research probes and `logs/edge_research` artifacts were added | met |
| Do not stop live bot | The live bot process was inspected and left running. One timed-out standalone research validator process was stopped after verifying its command line | met |
| Focus on underlying physics / question priors | Physics-prior scan, heartbeat favorite audit, two-sided side-choice probe, 80%-retention regime classifier, pure-physics ablation, interval blocker search, path-physics blocker search, staged interval probe, v21 locked-candidate validation, cross-dataset interval frontier, learned cross-dataset transfer, shared physical blocker scan, tail-calibrated Brownian terminal scan, touch-hazard first-passage scan, fresh skip audit, and prior-failure report test boundary cushion, sigma clock, realized vol, fat-tail calibration, first-passage boundary hazard, adverse drift, recent side-favorable impulse/fade risk, book probability calibration, fallback settlement mechanics, contrarian side choice, threshold-relaxation risk, cross-capture stability, supervised interaction stability, and regime-dependent feature direction rather than v28 p/edge alone | met for research, not complete for promotion |

## Conclusion

The objective is not complete. The current research has a better candidate surface, but it does not yet have enough forward evidence. The latest heartbeat refresh has 2,808 primary minute-bucket opportunities across 189 recurring BTC 15-minute markets with zero literal 95%/80% target-pass models. The kinetic-family locks are positive only on tiny strict fresh samples, while the older original/challenger/touch locks remain weak or negative.

The useful current direction is fee-aware expected value at high recurring-market coverage. The refreshed best broad row is kinetic-touch: `choose=kinetic_touch_score_15; kinetic_touch_score_15>=0.55; 50<=ask<=95; sec>=120; gate=touch_loss15<=0.90`. It is profitable on both current and v21 ledgers, covers about 99% of recurring markets, and avoids 98c-100c degeneracy. Its observed accuracy is about 69%-70%, so the edge is probability versus price, not a near-certain hit-rate model. The broader price/adverse guard `adverse15<=100 AND ask<=70` remains the cleanest narrower hypothesis because it improves both current and v21 sanity ledgers while preserving 89%-93% recurring-market coverage, and its strict post-boundary sample is 3/1 for +44c.

Forward validation is the blocker. Strict fresh evidence is now original 10/8 for -162c, challenger 9/7 for -136c, touch-hazard 7/7 for -116c, touch-overlay 4/3 for +4c, kinetic-touch 5/1 for +105c, kinetic-guard 4/1 for +59c, and kinetic-price-guard 3/1 for +44c. No lock clears the Wilson sample-size gate or Bayesian posterior gate.

The latest physics read is that first-passage risk is informative but not sufficient: adverse touches are not settlement losses by themselves, and early book/Brownian agreement can still flip violently inside a 15-minute window. The 03:45 loss was a fast path-flip failure: weak book confirmation at entry was overwhelmed by a rapid YES move. The kinetic candidate is a cleaner prior because it blends book probability, terminal Brownian probability, short-horizon drift, adverse velocity, and touch uncertainty, but the kinetic stability audit still shows fragility: current bootstrap P(mean edge <= 0) is 14.8%, v21 is 9.8%, and high-adverse / high-ask / mid-kinetic slices are weak. The price/adverse guard has the best current cross-dataset sanity profile, but its fresh edge is still far below sample-size proof. The correct next step is continued live refresh and settlement tracking without retuning or changing the live bot.

## 2026-05-03 10:37 UTC Synchronized Registry/Denominator Update

Research-only changes since the prior audit:

- Added `probe_profit_lock_market_denominator_audit.py` to check the 80% requirement against observed post-lock BTC15m market tickers from live heartbeat rows, not only validator selected/base counts.
- Wired `probe_profit_lock_pending_signal_monitor.py`, `probe_kinetic_path_confirmation_pending_monitor.py`, and the new denominator audit into `probe_profit_lock_forward_cycle.py`, so a heartbeat refresh is followed immediately by pre-resolution registration before readiness is measured.
- Patched `probe_kinetic_path_confirmation_pending_monitor.py` to avoid the remaining pandas concat warning when new rows are appended.

Latest synchronized cycle:

- Forward cycle `20260503_103437Z` completed with zero failed steps.
- Heartbeat refresh: 25,070 raw two-sided rows, 24,806 rows with candle physics, 215 unique markets, 3,198 primary minute-bucket opportunities, zero target-pass models.
- Pending registry after the heartbeat refresh registered 8 new main-lock records and 1 new path-confirmation record, including the open `KXBTC15M-26MAY030645-45` market where the kinetic family and combo guard now have pre-outcome signals.
- The denominator audit `20260503_103632Z` reports zero coverage failures. Kinetic-touch, kinetic-guard, combo guard, and path-confirmation are 100% registered on observed post-lock markets; kinetic-price guard is 30/31 observed markets, 96.77% coverage.

Registered-signal evidence after the 10:30 UTC settlement:

- The kinetic family took a fresh loss on the 10:30 UTC market. Registered kinetic-touch moved to 23/9 with +183c, kinetic-guard to 24/7 with +312c, kinetic-price guard to 20/9 with +135c, and combo guard to 1/2 with -97c.
- Path-confirmation registered a win and is now 20/5 with +133c, but its break-even is high at 74.68%; Wilson lower is only 60.87% and Bayesian P(p>BE) is 0.679.
- Kinetic-guard remains the strongest registered EV candidate by net P&L and posterior probability: 32 registered, 31 resolved, 24/7, 77.42% accuracy, 67.35% break-even, 60.19% Wilson lower, P(p>BE)=0.868, p05 edge -4.5c, +312c net. It is still not promotion-ready.
- Kinetic-touch is 33 registered, 32 resolved, 23/9, 71.88% accuracy, 66.16% break-even, +183c net, P(p>BE)=0.727, not ready.
- Combo price/adverse guard is not viable yet as forward evidence: 4 registered, 3 resolved, 1/2, -97c net, and resolved readiness coverage is only 75% while one current signal is pending.
- No lock clears the registered Wilson gate or the registered Bayesian gate.

Current completion read:

- The 80% recurring-market coverage requirement is now explicitly audited and currently satisfied by the tracked locks after synchronized registration.
- The sample-size requirement is still not met. The best registered candidate, kinetic-guard, still needs about 5 perfect wins for the registered Bayesian probability gate and materially more for Wilson-over-break-even proof.
- The physics read is stricter than before: simple kinetic/adverse guards preserve coverage, but the latest loss says the edge is still path-fragile. Delayed same-side confirmation helped this settlement, but its higher entry cost raises break-even enough that it also remains unproven.

## 2026-05-03 10:50 UTC 10:45 Settlement Refresh

Latest synchronized cycle:

- Forward cycle `20260503_104747Z` completed with zero failed steps and now includes the registered-signal delta step.
- Heartbeat refresh: 25,170 raw two-sided rows, 24,922 rows with candle physics, 3,213 primary minute-bucket opportunities, zero target-pass models.
- The 10:45 UTC settlement was a win for every pre-registered track that had the market. Delta audit `20260503_104945Z`: original +26c, challenger +26c, kinetic-touch +26c, kinetic-guard +26c, kinetic-price guard +30c, combo guard +30c, path-confirmation +24c, touch-hazard +43c, touch-overlay +43c.
- Denominator audit `20260503_104946Z`: zero coverage failures. Kinetic-touch and kinetic-guard are 100% registered on observed post-lock markets; path-confirmation is also 100%. Kinetic-price guard is 30/32 observed markets, 93.75%; combo is exactly 4/5 observed markets, 80.00%, with the 11:00 UTC market currently missing its guard condition.

Registered-signal readiness after the 10:45 win:

- Kinetic-guard: 33 registered, 32 resolved, 25/7, 78.12% accuracy, 67.56% break-even, 61.25% Wilson lower, P(p>BE)=0.886, p05 edge -3.8c, +338c net. Still not ready.
- Kinetic-touch: 34 registered, 33 resolved, 24/9, 72.73% accuracy, 66.39% break-even, P(p>BE)=0.754, +209c net. Not ready.
- Kinetic-price guard: 30 registered/resolved, 21/9, 70.00% accuracy, 64.50% break-even, P(p>BE)=0.710, +165c net. Not ready.
- Path-confirmation: 27 registered, 26 resolved, 21/5, 80.77% accuracy, 74.73% break-even, P(p>BE)=0.711, +157c net. Not ready because the entry cost/break-even is high.
- Combo guard improved to 2/2 on 4 resolved with -67c net, but it remains too small and too weak.

Current next evidence:

- The 11:00 UTC market `KXBTC15M-26MAY030700-00` is pre-registered for kinetic-touch, kinetic-guard, and path-confirmation.
- The price/adverse and combo guards did not register that market, which is a useful coverage stress: combo is exactly at the 80% observed-market floor and cannot skip many more markets without violating the user constraint.
- The 11:00 skip is price-driven rather than a data gap: the NO side only reached strong kinetic confirmation after the ask had moved above 70c, so the price/adverse guard excluded it while the broader kinetic-touch, kinetic-guard, and path-confirmation tracks accepted the high-ask path risk.
- No lock clears the registered Wilson gate or Bayesian gate; the goal remains incomplete.

## 2026-05-03 11:05 UTC 11:00 High-Ask Test Refresh

Latest synchronized cycle:

- Forward cycle `20260503_110300Z` completed with zero failed steps.
- Heartbeat refresh: 25,286 raw two-sided rows, 25,038 rows with candle physics, 3,228 primary minute-bucket opportunities, zero target-pass models.
- The 11:00 UTC market was a win for the broad kinetic tracks that accepted the high-ask NO path risk. Registered delta: kinetic-touch +20c, kinetic-guard +20c, path-confirmation +23c. Original/challenger also won; touch tracks won; price/adverse and combo did not have the 11:00 market resolved because they skipped it.

Registered-signal readiness after the 11:00 win:

- Kinetic-guard improved to 34 registered, 33 resolved, 26/7, 78.79% accuracy, 67.94% break-even, 62.25% Wilson lower, P(p>BE)=0.898, p05 edge -3.1c, +358c net. It remains the best candidate but still fails both gates.
- Kinetic-touch improved to 35 registered, 34 resolved, 25/9, 73.53% accuracy, 66.79% break-even, +229c net, P(p>BE)=0.774, not ready.
- Path-confirmation improved to 27/27 resolved, 22/5, 81.48% accuracy, 74.81% break-even, 63.30% Wilson lower, P(p>BE)=0.745, +180c net, not ready.
- Price/adverse guard remains 31 registered, 30 resolved, 21/9, +165c net, and combo is 5 registered, 4 resolved, 2/2, -67c net. Combo now has 83.33% observed coverage and 80.00% resolved coverage, barely above the user's floor.

Current next evidence:

- The 11:15 UTC market `KXBTC15M-26MAY030715-15` is pre-registered for the main kinetic family, price/adverse guard, and combo guard. Path-confirmation has not registered it yet, so the delayed confirmation rule is currently skipping that market.
- The 11:15 path-confirmation skip is because the early NO impulse did not persist: NO was eligible around 11:01 UTC, but about 60 seconds later the confirm score had fallen below 0.6, so the delayed rule abstained while the main/price/combo tracks kept the trade.
- No lock clears the registered Wilson gate or Bayesian gate. The goal remains incomplete; the next useful step is continued settlement tracking without retuning.

## 2026-05-03 11:25 UTC Pre-Resolution Integrity Correction

Critical evidence-integrity correction:

- The pending registries were correctly intended to hold only signals registered before settlement, but the monitors could also backfill a missed signal after close if the monitor had not run while that market was open.
- This contaminated registered-signal evidence. I patched `probe_profit_lock_pending_signal_monitor.py` and `probe_kinetic_path_confirmation_pending_monitor.py` so new records are added only when the market is still open and `outcome_available` is false.
- I also patched registered readiness, market-denominator audit, and registry/recompute divergence to filter out any row whose `registered_utc >= close_dt`.
- The synchronized cycle `20260503_112256Z` purged 177 non-causal rows from the main registry and 24 non-causal rows from the path-confirmation registry.

Corrected pre-resolution evidence:

- Original: 17 registered, 16 resolved, 9/7, -169c, registered observed coverage 34.00%.
- Challenger: 16 registered, 15 resolved, 8/7, -238c, registered observed coverage 32.65%.
- Touch-hazard: 19 registered, 18 resolved, 8/10, -272c, registered observed coverage 41.30%.
- Touch-overlay: 17 registered, 16 resolved, 8/8, -156c, registered observed coverage 43.59%.
- Kinetic-touch: 13 registered, 12 resolved, 7/5, -132c, registered observed coverage 36.11%.
- Kinetic-guard: 10 registered/resolved, 6/4, -104c, registered observed coverage 28.57%.
- Kinetic-price guard: 9 registered/resolved, 4/5, -184c, registered observed coverage 26.47%.
- Kinetic combo price-guard: 4 registered/resolved, 1/3, -166c, registered observed coverage 57.14%.
- Kinetic path-confirmation: 4 registered/resolved, 2/2, -108c, registered observed coverage 13.79%.

Corrected read:

- No tracked lock currently satisfies the user-level 80% registered recurring-market coverage requirement when restricted to genuinely pre-resolution records.
- No tracked lock is positive on corrected pre-resolution registered P&L except none; all are negative.
- Recomputed fresh validators still show what the policies would have selected, but they are diagnostic only because they include markets that were not registered before outcome. They cannot be used as promotion evidence.
- This materially changes the goal state: the current best action is not to promote any candidate, but to continue strict live registration from this point forward and rebuild a clean sample.
- The goal remains incomplete.

## 2026-05-03 11:36 UTC Strict Registry Follow-Up

Latest strict synchronized cycle:

- Forward cycle `20260503_113439Z` completed with zero failed steps under the new pre-resolution-only registration rules.
- No additional post-close records were removed in this run, which confirms the patched monitors are no longer backfilling closed markets.
- The 11:30 UTC refresh added clean pre-resolution pending signals for the 11:45 UTC market, while resolving the prior pending rows.

Corrected registered state after the 11:30 settlement:

- Original: 18 registered, 17 resolved, 9/8, -225c, registered observed coverage 35.29%.
- Challenger: 17 registered, 16 resolved, 8/8, -294c, registered observed coverage 34.00%.
- Touch-hazard: 20 registered, 19 resolved, 8/11, -328c, registered observed coverage 42.55%.
- Touch-overlay: 17 registered/resolved, 8/9, -212c, registered observed coverage 42.50%.
- Kinetic-touch: 14 registered, 13 resolved, 8/5, -109c, registered observed coverage 37.84%. It was the only tracked delta winner in this settlement cycle, +23c.
- Kinetic-guard: 11 registered, 10 resolved, 6/4, -104c, registered observed coverage 30.56%.
- Kinetic-price guard: 10 registered, 9 resolved, 4/5, -184c, registered observed coverage 28.57%.
- Kinetic combo price-guard: 5 registered, 4 resolved, 1/3, -166c, registered observed coverage 62.50%.
- Kinetic path-confirmation: 5 registered, 4 resolved, 2/2, -108c, registered observed coverage 16.67%.

Strict read:

- Every lock fails the 80% registered recurring-market coverage requirement under clean pre-resolution accounting.
- Every lock is negative on corrected registered P&L.
- The recomputed fresh validators remain useful for physics diagnostics but are no longer acceptable promotion evidence.
- The active work should continue as clean forward collection plus physics analysis; no current model is close to promotion.

## 2026-05-03 11:50 UTC Strict 11:45 Settlement Refresh

Research-only reporting change:

- `probe_profit_lock_forward_cycle.py` now includes a registered-signal summary table and denominator failure count, so the strict pre-resolution evidence is visible in the main cycle report instead of being hidden behind recomputed fresh metrics.

Latest strict cycle:

- Forward cycle `20260503_114800Z` completed with zero failed steps.
- Heartbeat refresh: 25,638 raw two-sided rows, 25,386 rows with candle physics, 3,273 primary minute-bucket opportunities, zero target-pass models.
- No post-close records were removed; the patched registries remained causal.
- The 11:45 UTC settlement was a win for every strict track that had a resolved row in the delta audit: original, challenger, touch-hazard, kinetic-touch, kinetic-guard, kinetic-price guard, combo guard, and path-confirmation all improved by about 44c-46c. Touch-overlay registered the 12:00 UTC market but had no settled delta.

Corrected registered state after the 11:45 win:

- Kinetic-touch: 15 registered, 14 resolved, 9/5, -63c, registered coverage 40.54%.
- Kinetic-guard: 12 registered, 11 resolved, 7/4, -58c, registered coverage 33.33%.
- Kinetic-price guard: 10 registered/resolved, 5/5, -138c, registered coverage 28.57%.
- Kinetic combo: 5 registered/resolved, 2/3, -120c, registered coverage 62.50%.
- Path-confirmation: 6 registered, 5 resolved, 3/2, -64c, registered coverage 20.00%.
- Original/challenger/touch tracks remain negative and below 50% registered coverage.

Current next evidence:

- The 12:00 UTC market `KXBTC15M-26MAY030800-00` is pre-registered for original, challenger, touch-hazard, touch-overlay, kinetic-touch, kinetic-guard, and path-confirmation. Kinetic-price and combo do not currently have a pending signal.
- Every lock still fails strict 80% registered recurring-market coverage and every lock remains negative on corrected registered P&L.
- Goal remains incomplete.

## 2026-05-03 12:05 UTC Strict 12:00 Settlement Refresh

Latest strict cycle:

- Forward cycle `20260503_120248Z` completed with zero failed steps.
- Heartbeat refresh: 25,752 raw two-sided rows, 25,504 rows with candle physics, 3,288 primary minute-bucket opportunities, zero target-pass models.
- No post-close records were removed; the strict registration patch continues to hold.
- The 12:00 UTC settlement was a loss for original, challenger, kinetic-touch, kinetic-guard, and path-confirmation. Touch-hazard and touch-overlay won. Kinetic-price and combo only registered the next 12:15 UTC market and had no settled delta.

Corrected registered state after the 12:00 loss:

- Kinetic-touch: 16 registered, 15 resolved, 9/6, -144c, registered coverage 42.11%, P(p>BE)=0.185.
- Kinetic-guard: 13 registered, 12 resolved, 7/5, -139c, registered coverage 35.14%, P(p>BE)=0.167.
- Kinetic-price guard: 11 registered, 10 resolved, 5/5, -138c, registered coverage 30.56%, P(p>BE)=0.170.
- Kinetic combo: 6 registered, 5 resolved, 2/3, -120c, registered coverage 66.67%, P(p>BE)=0.128.
- Path-confirmation: 7 registered, 6 resolved, 3/3, -154c, registered coverage 22.58%, P(p>BE)=0.064.
- Touch-hazard and touch-overlay improved but remain negative: -236c and -166c respectively.

Current next evidence:

- The 12:15 UTC market `KXBTC15M-26MAY030815-15` is pre-registered for all main locks, including price/adverse and combo. Path-confirmation is also pending from its own monitor.
- Every lock remains negative on corrected registered P&L and every lock fails the strict registered recurring-market coverage floor.
- The current kinetic prior is not promotion-safe under causal evidence. It remains useful as a diagnostic surface, but the model search must continue.

## 2026-05-03 12:22 UTC Strict 12:15 Settlement Refresh

Latest strict cycle:

- Forward cycle `20260503_121822Z` completed with zero failed steps.
- The 12:15 UTC settlement was a strict win for all registered tracks that had the market. Delta audit: original/challenger/touch/kinetic/price/combo improved by about +32c; path-confirmation improved by +16c.
- No post-close rows were removed.

Corrected registered state after the 12:15 win:

- Kinetic-touch: 17 registered, 16 resolved, 10/6, -112c, registered coverage 43.59%, P(p>BE)=0.238.
- Kinetic-guard: 14 registered, 13 resolved, 8/5, -107c, registered coverage 36.84%, P(p>BE)=0.225.
- Kinetic-price guard: 11 registered/resolved, 6/5, -106c, registered coverage 29.73%, P(p>BE)=0.232.
- Kinetic combo: 6 registered/resolved, 3/3, -88c, registered coverage 60.00%, P(p>BE)=0.205.
- Path-confirmation: 8 registered, 7 resolved, 4/3, -138c, registered coverage 25.00%, P(p>BE)=0.089.
- Touch-overlay is the least negative broad track at -134c, but still below 50% registered coverage and not viable.

Current next evidence:

- The 12:30 UTC market `KXBTC15M-26MAY030830-30` is pre-registered for original, touch-hazard, touch-overlay, kinetic-touch, kinetic-guard, and path-confirmation. Challenger, kinetic-price, and combo do not currently have pending signals.
- Strict evidence still rejects promotion: all locks are negative, all fail 80% registered-market coverage, and all fail Wilson/Bayesian readiness.

## 2026-05-03 12:36 UTC Strict 12:30 Settlement Refresh

Latest strict cycle:

- Forward cycle `20260503_123339Z` completed with zero failed steps.
- The 12:30 UTC settlement was a strict win for original, touch-hazard, touch-overlay, kinetic-touch, kinetic-guard, and path-confirmation. Challenger, kinetic-price, and combo had no settled delta from that market and registered the next 12:45 UTC market instead.
- No post-close rows were removed.

Corrected registered state after the 12:30 win:

- Kinetic-touch: 18 registered, 17 resolved, 11/6, -87c, registered coverage 45.00%, P(p>BE)=0.285.
- Kinetic-guard: 15 registered, 14 resolved, 9/5, -92c, registered coverage 38.46%, P(p>BE)=0.253.
- Kinetic-price guard: 12 registered, 11 resolved, 6/5, -106c, registered coverage 31.58%, P(p>BE)=0.232.
- Kinetic combo: 7 registered, 6 resolved, 3/3, -88c, registered coverage 63.64%, P(p>BE)=0.205.
- Path-confirmation: 9 registered, 8 resolved, 5/3, -122c, registered coverage 27.27%, P(p>BE)=0.118.
- Touch-overlay is still the least negative broad lock at -108c, with 50.00% registered coverage.

Current next evidence:

- The 12:45 UTC market `KXBTC15M-26MAY030845-45` is pre-registered for every main lock, including price/adverse and combo. Path-confirmation also has a pending row.
- The corrected evidence is improving over the last few settlements, but it is still far from the target: all locks remain negative and all fail strict 80% registered-market coverage.

## 2026-05-03 12:51 UTC Strict 12:45 Settlement Refresh

Latest strict cycle:

- Forward cycle `20260503_124800Z` completed with zero failed steps.
- The 12:45 UTC settlement split the physics families: original, challenger, kinetic-touch, kinetic-guard, kinetic-price, combo, and path-confirmation won; touch-hazard and touch-overlay lost.
- No post-close rows were removed.

Corrected registered state after the 12:45 split:

- Kinetic-touch: 19 registered, 18 resolved, 12/6, -54c, registered coverage 46.34%, P(p>BE)=0.347.
- Kinetic-guard: 16 registered, 15 resolved, 10/5, -59c, registered coverage 40.00%, P(p>BE)=0.321.
- Kinetic-price guard: 13 registered, 12 resolved, 7/5, -73c, registered coverage 33.33%, P(p>BE)=0.300.
- Kinetic combo: 8 registered, 7 resolved, 4/3, -55c, registered coverage 66.67%, P(p>BE)=0.293.
- Path-confirmation: 10 registered, 9 resolved, 6/3, -97c, registered coverage 29.41%, P(p>BE)=0.170.
- Touch-hazard fell to -232c and touch-overlay to -162c.

Current next evidence:

- The 13:00 UTC market `KXBTC15M-26MAY030900-00` is pre-registered for every main lock and path-confirmation.
- Kinetic-family strict evidence is improving but remains below zero and far below the registered 80% market-coverage floor. No lock is promotion-ready.

## 2026-05-03 13:06 UTC Strict 13:00 Settlement Refresh

Latest strict cycle:

- Forward cycle `20260503_130407Z` completed with zero failed steps.
- The 13:00 UTC settlement was a strict loss for every registered track. Delta audit: original, challenger, touch-hazard, kinetic-touch, kinetic-guard, kinetic-price, and combo each lost about 70c; touch-overlay lost 61c; path-confirmation lost 62c.
- No post-close rows were removed.

Corrected registered state after the 13:00 loss:

- Kinetic-touch: 20 registered, 19 resolved, 12/7, -124c, registered coverage 47.62%, P(p>BE)=0.238.
- Kinetic-guard: 17 registered, 16 resolved, 10/6, -129c, registered coverage 41.46%, P(p>BE)=0.209.
- Kinetic-price guard: 14 registered, 13 resolved, 7/6, -143c, registered coverage 35.00%, P(p>BE)=0.188.
- Kinetic combo: 9 registered, 8 resolved, 4/4, -125c, registered coverage 69.23%, P(p>BE)=0.160.
- Path-confirmation: 11 registered, 10 resolved, 6/4, -159c, registered coverage 31.43%, P(p>BE)=0.100.
- All broader locks remain negative; challenger is weakest at -334c.

Current next evidence:

- The 13:15 UTC market `KXBTC15M-26MAY030915-15` is pre-registered for every main lock and path-confirmation.
- The strict evidence now strongly rejects all current locks for promotion: negative P&L, low posterior confidence, and registered coverage well below 80%.

## 2026-05-03 13:22 UTC Strict 13:15 Settlement Refresh

Latest strict cycle:

- Forward cycle `20260503_131926Z` completed with zero failed steps.
- The 13:15 UTC settlement was a broad strict loss. Every registered track lost: original, challenger, touch-hazard, touch-overlay, kinetic-touch, kinetic-guard, kinetic-price, combo, and path-confirmation.
- No post-close rows were removed.

Corrected registered state after the 13:15 loss:

- Kinetic-touch: 21 registered, 20 resolved, 12/8, -189c, registered coverage 48.84%, P(p>BE)=0.160.
- Kinetic-guard: 18 registered, 17 resolved, 10/7, -194c, registered coverage 42.86%, P(p>BE)=0.135.
- Kinetic-price guard: 15 registered, 14 resolved, 7/7, -208c, registered coverage 36.59%, P(p>BE)=0.115.
- Kinetic combo: 10 registered, 9 resolved, 4/5, -190c, registered coverage 71.43%, P(p>BE)=0.088.
- Path-confirmation: 12 registered, 11 resolved, 6/5, -234c, registered coverage 33.33%, P(p>BE)=0.047.
- All broad locks are also deeply negative: original -314c, challenger -399c, touch-hazard -368c, touch-overlay -289c.

Current next evidence:

- The 13:30 UTC market `KXBTC15M-26MAY030930-30` is pre-registered for every main lock and path-confirmation.
- Strict evidence now rejects every current hypothesis for promotion. Any next iteration should be treated as fresh research, not as a near-promotion candidate.

## 2026-05-03 13:33 UTC Strict 13:30 Settlement Refresh

Latest strict cycle:

- Forward cycle `20260503_133035Z` completed with zero failed steps and now includes strict failure attribution.
- The 13:30 UTC settlement was a strict win across all registered tracks. Delta audit: touch-hazard +45c; original, challenger, kinetic-touch, kinetic-guard, kinetic-price, and combo +37c; path-confirmation +30c.
- The pending monitor registered two new pre-resolution rows for the 13:45 UTC market: touch-hazard and kinetic-touch. The other locks had not yet produced a causal signal for that interval as of the 13:31 UTC monitor pass.
- Strict failure attribution found 175 resolved rows across locks and zero diagnostic blockers that were both positive and retained at least 80% of strict rows.

Corrected registered state after the 13:30 win:

- Kinetic-touch: 22 registered, 21 resolved, 13/8, -152c, registered coverage 50.00%, P(p>BE)=0.211.
- Kinetic-guard: 18 registered, 18 resolved, 11/7, -157c, registered coverage 41.86%, P(p>BE)=0.187.
- Kinetic-price guard: 15 registered, 15 resolved, 8/7, -171c, registered coverage 35.71%, P(p>BE)=0.164.
- Kinetic combo: 10 registered, 10 resolved, 5/5, -153c, registered coverage 66.67%, P(p>BE)=0.144.
- Path-confirmation: 12 registered, 12 resolved, 7/5, -204c, registered coverage 32.43%, P(p>BE)=0.076.
- Original improved to -277c but remains negative and only 43.86% registered coverage.

Important denominator read:

- Recomputed fresh metrics are materially better than strict registered metrics, but they are diagnostic only. Current recomputed fresh state: original 56/57 markets, +13c; kinetic-touch 44/44, +136c; kinetic-guard 43/43, +134c; path-confirmation 37/37, +138c.
- The registry/recompute divergence remains large: original registered 25 vs recomputed 56, challenger 23 vs 52, kinetic-touch 21 vs 44, and path-confirmation 12 vs 37. This means the main blocker is still causal capture coverage, not just model selection.
- A research-only strict collector script was added at `probe_profit_lock_strict_signal_collector.py` to run pending monitors, readiness, delta, denominator audit, and failure attribution as a repeated causal capture loop. Detached background launch from the sandbox did not persist, so collector iterations must be run from the active session or a normal user shell to keep future market coverage above the 80% denominator floor.

## 2026-05-03 13:49 UTC V2 High-Coverage Frontier Lock

New research candidate:

- Refreshed `probe_cross_dataset_profit_frontier.py` on the latest heartbeat ledger. The top nondegenerate 80%-coverage profit row moved to the simpler policy `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.55; ask<=95; sec_to_close>=120`.
- Current capture: 225/227 markets selected, 64.44% accuracy, +535c net, 3.83% ROI, 99.12% market coverage, median ask 60c.
- Independent v21 capture: 68.04% accuracy, +1283c net, 9.42% ROI, 99.10% market coverage.
- Locked this as `frontier_v2` in `probe_profit_frontier_v2_fresh_validation.py` with created UTC `2026-05-03T13:44:59Z` and effective boundary `2026-05-03T13:45:00Z`.

Strict v2 capture:

- Added `frontier_v2` to the main pending registry, registered-signal readiness, sample-size monitor, Bayesian EV monitor, denominator audit, and forward cycle.
- A fetch-enabled pending pass at `2026-05-03 13:46 UTC` registered the first v2 causal signal for `KXBTC15M-26MAY031000-00`.
- Latest v2 registered state: 1 registered / 0 resolved / 1 pending, observed registered coverage 100% so far, no promotion read until resolved sample exists.

Important operational read:

- Fetching BTC candles is required for current-market physics rows. A no-fetch monitor pass missed the 10:00 market until the fetch-enabled pass refreshed candle coverage.
- The 13:45 UTC market settled as a loss for the two strict pending rows that existed before v2: touch-hazard -63c and kinetic-touch -75c. That worsened kinetic-touch to -227c and touch-hazard to -386c on strict registered evidence.

## 2026-05-03 14:05 UTC V2 First Resolution And 10:15 Capture

Strict 14:00 UTC settlement:

- The 14:00 UTC market `KXBTC15M-26MAY031000-00` resolved as a win for every registered track.
- V2 first strict resolved row: YES at 57c, +41c net, registered before close at `2026-05-03T13:46:54Z`.
- Other 14:00 strict deltas: challenger +18c, original/kinetic-touch/kinetic-guard +14c, kinetic-price/combo +40c, touch-hazard/touch-overlay +41c, path-confirmation +18c.

V2 state after first resolution:

- Registered readiness: 2 registered / 1 resolved / 1 pending, 1/0, +41c, registered coverage 100.00%, resolved coverage 50.00%.
- Denominator audit: v2 observed/resolved/unclosed = 2/1/1, registered observed coverage 100.00%, registered resolved coverage 100.00%, coverage pass true so far.
- Fresh recompute after v2 lock: 1/1 market, 1/0, +41c, 100% coverage. This is too small for proof; sample-size monitor estimates v2 needs 5 additional perfect fresh wins just to clear Wilson over break-even from the current state.

Next strict evidence:

- The 14:15 UTC market `KXBTC15M-26MAY031015-15` is now pre-registered for every tracked lock, including v2 and path-confirmation.
- V2 second strict pending row: YES at 64c, registered at `2026-05-03T14:04:24Z`, about 776s before close.

## 2026-05-03 14:19 UTC Strict 14:15 Settlement Refresh

Strict 14:15 UTC settlement:

- The 14:15 UTC disagreement case resolved YES.
- YES-side locks won: original, frontier_v2, challenger, kinetic-touch, kinetic-guard, kinetic-price, kinetic-combo, and path-confirmation.
- Touch-hazard and touch-overlay had registered early NO rows and both lost -61c.

V2 state:

- Registered readiness: 3 registered / 2 resolved / 1 pending, 2/0, +75c, registered coverage 100.00%, resolved coverage 66.67%.
- Denominator audit remains clean for v2: observed/resolved/unclosed = 3/2/1, registered observed coverage 100%, registered resolved coverage 100%, coverage pass true.
- Fresh recompute after v2 lock: 2/2 markets, 2/0, +75c, 100% coverage, median ask 60.5c.
- V2 is still too small for promotion: Wilson low is only 34.24% vs 62.50% break-even; sample-size monitor still estimates 5 additional perfect wins needed to clear Wilson over break-even from the current state.

Next strict evidence:

- The 14:30 UTC market `KXBTC15M-26MAY031030-30` is pre-registered for all main locks, including v2.
- V2 third strict pending row: YES at 58c, registered at `2026-05-03T14:16:24Z`.
- Path-confirmation later registered the same 14:30 market at `2026-05-03T14:23:25Z`, but on the opposite side: NO at 78c. This makes 14:30 another clean physics disagreement case between the v2 Brownian frontier and delayed path-confirmation.

## 2026-05-03 19:34 UTC Strict Registry Refresh And Metadata Gap Fix

Strict 14:30 UTC settlement:

- The 14:30 UTC market `KXBTC15M-26MAY031030-30` resolved NO.
- V2 and the main Brownian/kinetic-touch families had registered YES at 58c and lost about 60c net.
- Path-confirmation had delayed until a same-side confirmation appeared, registered NO at 78c, and won +20c.
- This is the cleanest current physics split: the early Brownian-distance prior was wrong, while delayed path confirmation caught the later boundary migration, but at an expensive 78c entry price.

Operational capture fix:

- Added `probe_refresh_watched_market_metadata.py`, a research-only public metadata refresher for watched markets.
- Patched `probe_live_v28_fv_accuracy_volume.parse_bot_log` so `strike=NA` watch lines can be filled from `logs/edge_research/kalshi_market_metadata_cache.json`.
- This matters because the live log had at least one watched market with `strike=NA`; without a strike, heartbeat physics rows are skipped and the strict registry cannot preserve 80% causal coverage.

Current strict evidence after the 19:33 UTC pending pass:

- Pending monitor registered 8 new lock rows for `KXBTC15M-26MAY031545-45`; path-confirmation registered 1 row for the same market.
- V2 state: 4 registered / 3 resolved / 1 pending, 2/1, +15c net, registered coverage 100% within its captured rows, but too small and not promotion-ready.
- The current 15:45 UTC/19:45 UTC market is a same-side YES case across v2, original, challenger, kinetic-touch, kinetic-guard, kinetic-price, touch-hazard, touch-overlay, and path-confirmation. V2 registered YES at 62c; path-confirmation registered YES at 87c.
- Registered-signal readiness still rejects promotion for every lock: no Wilson gate, no Bayesian gate, and registered denominator coverage remains below 80% on the older locks due earlier causal-capture gaps.

Physics read:

- The useful direction is not a lower-volume filter. The high-coverage target needs a side/price model that preserves the v2 80%+ denominator but detects when late path kinetics should override the initial Brownian side.
- The 14:30 split says pure Brownian RV15 is vulnerable when the path rapidly migrates across the strike after entry.
- Path confirmation is directionally better in those cases, but its current entries are often expensive; the improvement has to be expressed as a price-aware kinetic override, not simply "always wait for confirmation."

Late-resampling diagnostic:

- Added `probe_late_resampled_frontier.py` to scan the hypothesis "choose the same broad Brownian/book side, but only after the interval has evolved below a max seconds-to-close boundary."
- Scan result: 960 policies tested, 422 kept >=80% coverage on both current and v21 datasets, but zero were positive on both validation and holdout P&L.
- The 14:30 failure is explainable by timing: the v2 Brownian row selected YES at 58c with 835s left and lost; the same Brownian chooser would have flipped to NO and won if resampled at 660s/600s left.
- But the global late-resample rule is not enough. Example: `brownian_p_rv_15m>=0.55; ask<=95; 120<=sec_to_close<=600` corrected 14:30 but was negative on both datasets: current -247c, v21 -379c, despite ~97% coverage. Late correctness gets eaten by late price.
- Conclusion: do not lock this as v3. The next candidate needs conditional path-flip value: override when the kinetic flip is unusually informative and the price still clears fee-aware EV, not a blanket wait.

## 2026-05-03 19:48 UTC Strict 15:45 Settlement Refresh

Strict 15:45 UTC / 19:45 UTC settlement:

- The market `KXBTC15M-26MAY031545-45` resolved YES.
- V2 won: YES at 62c, +36c net. Strict v2 is now 4 registered / 4 resolved / 0 pending, 3/1, +51c net.
- Main YES locks also won: original +36c, challenger +36c, kinetic-touch +36c, kinetic-guard +26c, kinetic-price +36c, touch-hazard/touch-overlay +45c.
- Path-confirmation also won, but only +12c because it paid 87c. This reinforces the same lesson as 14:30 in reverse: path confirmation can be directionally useful, but late confirmation is frequently expensive.

Current strict readiness:

- No lock clears Wilson or Bayesian promotion gates.
- V2 is the only positive strict registered lock right now, but n=4 is not proof: Wilson low 30.06% vs 62.25% break-even, posterior P(p>BE)=0.623, p05 edge -28.0c.
- Registered denominator coverage still fails for the older locks because of earlier causal-capture gaps. V2 recomputed coverage is 100%, but strict denominator coverage is penalized by missed post-lock markets; only future pre-registered rows can repair that evidence.

Next pending evidence:

- The 16:00 UTC / 20:00 UTC market `KXBTC15M-26MAY031600-00` has only touch-hazard and touch-overlay pending so far, both NO at 54c.
- V2 has abstained so far on this market, which is acceptable under the >=80% target as long as abstentions remain sparse.

Path-flip override diagnostic:

- Added `probe_path_flip_override_frontier.py` to test a more targeted hypothesis than blanket waiting: keep v2 as the default, but let a strong late opposite-side Brownian flip replace the original side.
- Focused scan result: 16/16 policies preserved >=80% coverage on both datasets and all were OOS-positive under the diagnostic replacement accounting.
- Best diagnostic row: `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=none`, with current/v21 delta +2924c/+698c versus v2 and 99.20%/99.10% coverage.
- It correctly fixes the 14:30 split: replaces early YES 58c with later NO 82c and wins +16c.
- Critical prior check: this is not yet tradable P&L. The scan gives itself option value by keeping early v2 when no flip appears but replacing it when a flip does appear. A live version must either wait for the flip window, or enter early and pay exit/reverse costs. The 14:30 switch-cost intuition is harsh: buying YES 58c, later selling near the YES bid while buying NO 82c would likely turn the apparent +16c override into a net loss after the initial leg.
- Do not lock this as v3 until a switch-cost or wait-cost version remains positive across current/v21 and then gets strict forward registration.

Switch-cost falsification:

- Added `probe_path_flip_switch_cost.py` to charge the early v2 entry, exit at the contemporaneous bid, and late opposite-side entry when an override appears.
- Result: 16/16 policies preserved >=80% coverage, but 0/16 were switch-cost OOS-positive across both datasets.
- Best switch-cost row was still worse than v2: current/v21 delta -716c/-1086c.
- The 14:30 "fixed" flip from YES 58c to NO 77c had final replacement net +21c, but managed switch net -18c after unwinding the original YES.
- Conclusion: the path-flip signal is physically real as an information event, but not directly tradable as an exit/reverse overlay at current prices and fees. Do not lock the flip override.

## 2026-05-03 20:04 UTC Strict 16:00 Settlement And 16:15 Capture

Strict 16:00 UTC / 20:00 UTC settlement:

- The market `KXBTC15M-26MAY031600-00` resolved NO.
- Only touch-hazard and touch-overlay had strict rows pending; both won NO at 54c, +44c each.
- Touch-hazard improved to 34 registered / 33 resolved / 1 pending, 16/17, -374c.
- Touch-overlay improved to 30 registered / 29 resolved / 1 pending, 15/14, -232c.

Current 16:15 UTC / 20:15 UTC pending evidence:

- The market `KXBTC15M-26MAY031615-15` is pre-registered across the main locks on NO.
- V2 fifth strict row: NO at 51c, pending.
- Other pending NO rows: original 51c, challenger 51c, kinetic-touch 51c, kinetic-price 51c, kinetic-guard 56c, kinetic-combo 56c, touch-hazard 51c, touch-overlay 58c.
- Path-confirmation has no pending row yet.

Current promotion read:

- No lock clears registered-signal Wilson or Bayesian gates.
- V2 is 5 registered / 4 resolved / 1 pending, 3/1, +51c, resolved coverage 80% and registered coverage 100% inside its strict rows, but still far too small for proof.

## 2026-05-03 20:18 UTC Strict 16:15 Settlement And 16:30 Capture

Strict 16:15 UTC / 20:15 UTC settlement:

- The market `KXBTC15M-26MAY031615-15` resolved NO.
- V2 won: NO at 51c, +47c net. Strict v2 is now 6 registered / 5 resolved / 1 pending, 4/1, +98c.
- The 16:15 settlement was broadly favorable: original +47c, challenger +47c, kinetic-touch +47c, kinetic-price +47c, kinetic-guard +42c, kinetic-combo +42c, touch-hazard +47c, touch-overlay +40c.

Current 16:30 UTC / 20:30 UTC pending evidence:

- V2 sixth strict row: `KXBTC15M-26MAY031630-30`, NO at 46c, pending.
- Original also registered NO at 46c.
- Touch-hazard and touch-overlay disagree: both registered YES at 56c.
- Path-confirmation has no pending row.

Current promotion read:

- V2 is improving but still not proven: 80.00% strict accuracy on 5 resolved rows, Wilson low 37.55% vs 60.40% break-even, posterior P(p>BE)=0.761, p05 edge -18.7c.
- No lock clears registered Wilson or Bayesian gates.

## 2026-05-03 20:33 UTC Strict 16:30 Settlement And 16:45 Capture

Strict 16:30 UTC / 20:30 UTC settlement:

- The market `KXBTC15M-26MAY031630-30` resolved YES.
- This was another clean disagreement: V2/original registered NO at 46c and lost -48c; touch-hazard/touch-overlay registered YES at 56c and won +42c.
- V2 strict state fell to 7 registered / 6 resolved / 1 pending, 4/2, +50c.

Current 16:45 UTC / 20:45 UTC pending evidence:

- The market `KXBTC15M-26MAY031645-45` is pre-registered broadly on YES.
- V2 seventh strict row: YES at 50c, pending.
- Other pending YES rows: original/challenger/touch-hazard/touch-overlay at 50c, kinetic-touch/guard/price/combo at 60c.
- Path-confirmation still has no pending row.

Physics read:

- V2 has now produced two recent wrong-side cases after a good run: 14:30 YES lost, 16:30 NO lost.
- Touch-hazard/overlay caught 16:30 but are still deeply negative overall, so the useful information is not the existing touch lock itself; it is the fact that local path/touch geometry sometimes detects Brownian side failure.
- No promotion gate is close: v2 posterior P(p>BE)=0.617 and p05 edge -24.0c after the 16:30 loss.

Touch disagreement diagnostic:

- Added `probe_v2_touch_disagreement_diagnostic.py` to test whether touch-hazard disagreement with v2 is broadly informative.
- Result rejects a simple touch override/veto. On current paired markets, when v2 and touch disagree, v2 is 63.64% and +118c while touch is 36.36% and -949c. On v21 disagreements, v2 is 65.85% and +146c while touch is 34.15% and -959c.
- Touch agreement is useful mainly because both systems choose the same side; disagreement is not a reliable sign that v2 is wrong.
- Conclusion: do not use touch disagreement as a v2 override. The true failure signal must be narrower than "touch says the other side."

## 2026-05-03 20:48 UTC Strict 16:45 Settlement And 17:00 Capture

Strict 16:45 UTC / 20:45 UTC settlement:

- The market `KXBTC15M-26MAY031645-45` resolved YES.
- V2 won: YES at 50c, +48c net. Strict v2 is now 7 registered / 7 resolved / 0 pending, 5/2, +98c.
- Broad YES locks also won: original/challenger/touch-hazard/touch-overlay +48c; kinetic-touch/guard/price/combo +38c.

Current 17:00 UTC / 21:00 UTC pending evidence:

- Only touch-hazard and touch-overlay are currently pending on `KXBTC15M-26MAY031700-00`, both NO at 51c.
- V2 has no pending 17:00 row as of the 20:46 UTC monitor pass.

Current promotion read:

- V2 remains the only positive strict registered lock: 71.43% accuracy, +98c net, 100% registered coverage within its 7 strict rows.
- Still not promotion-ready: Wilson low 35.89% vs 57.43% break-even, posterior P(p>BE)=0.736, p05 edge -17.3c.
- No lock clears registered Wilson or Bayesian gates.

V2 tradeable veto scan:

- Added `probe_v2_tradeable_veto_scan.py` to test one-feature abstention rules on top of v2 while preserving >=80% coverage.
- Result: 75 rules scanned; 25 preserved >=80% coverage on both current and v21; 0 were OOS-positive on both datasets.
- Best all-sample veto was `adverse_move_15m<=75`: current +286c over v2 with 88.35% coverage; v21 +211c over v2 with 85.97% coverage.
- It is not lockable because the OOS ROI floor remained negative (-9.34%). This is useful physics but weak proof: high adverse path movement may mark risk, but a one-feature veto is not stable enough.

## 2026-05-03 21:03 UTC Strict 17:00 Settlement And 17:15 Capture

Strict 17:00 UTC / 21:00 UTC settlement:

- The market `KXBTC15M-26MAY031700-00` resolved NO.
- Only touch-hazard and touch-overlay had strict pending rows; both won NO at 51c, +47c each.
- Touch-overlay has improved materially but remains negative: 34 registered / 33 resolved / 1 pending, 19/14, -55c.
- Touch-hazard remains negative: 38 registered / 37 resolved / 1 pending, 20/17, -190c.

Current 17:15 UTC / 21:15 UTC pending evidence:

- Another split: V2/original/challenger registered NO at 59c for `KXBTC15M-26MAY031715-15`.
- Touch-hazard/touch-overlay registered YES at 50c.
- V2 strict state before this settlement remains 8 registered / 7 resolved / 1 pending, 5/2, +98c.

Current promotion read:

- No lock clears registered Wilson or Bayesian gates.
- V2 remains positive but unproven; touch-overlay is approaching break-even but still negative and below coverage/proof requirements.

## 2026-05-03 22:20 UTC Refreshed Frontier And New Forward Candidates

Strict settlements after the 21:03 UTC audit:

- `KXBTC15M-26MAY031715-15` resolved YES. V2/original/challenger had registered NO at 59c and lost -61c; touch-hazard/touch-overlay had registered YES at 50c and won +48c.
- `KXBTC15M-26MAY031815-15` resolved YES. V2 had registered YES at 89c and won only +10c.
- Current strict v2 evidence: 9 registered / 9 resolved / 0 pending, 6/3, +47c net. It is still not promotion-ready: Wilson low 35.42% vs 61.44% break-even, posterior P(p>BE)=0.581, p05 edge -22.1c.
- No registered lock clears Wilson or Bayesian readiness gates.

Broad frontier refresh:

- Refreshed `live_heartbeat_two_side_fv_ledger_latest.csv` with `probe_live_heartbeat_two_side_fv.py --fetch-btc-candles`: 29,998 physics rows.
- Reran `probe_cross_dataset_profit_frontier.py`: current intervals increased to 260; v21 remains 221.
- The old Brownian v2 no longer leads current data after the recent failures: current all +291c, 63.18% accuracy, 99.23% coverage, and current holdout -456c.
- New top OOS-robust row: `choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0`, current +916c / v21 +425c, about 99% coverage, min OOS ROI 4.31%, but v21 train is -80c so it is not promotable.
- Higher combined row: `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120`, current +1301c / v21 +534c, about 99% coverage, but min OOS ROI is only 1.25% and v21 train is -19c.
- No refreshed frontier row is profitable on every split across both datasets. This is a candidate-generation result, not completion.

Forward locks added for strict evidence only:

- Added `logs/edge_research/profit_frontier_book_margin_lock.json`.
- Added `logs/edge_research/profit_frontier_score_min60_lock.json`.
- Patched `probe_profit_lock_pending_signal_monitor.py` and `probe_profit_lock_registered_signal_readiness.py` so the strict collector tracks `book_margin` and `score_min60`.
- Compiled the patched scripts and validated both lock JSON files.
- Effective causal boundary is the next full 15m close after lock creation, so the new candidates correctly show 0 registered rows until post-boundary markets arrive.

Candidate-vs-v2 diagnostic:

- Added and ran `probe_frontier_candidate_v2_diagnostic.py`.
- `book_margin` versus v2 paired delta: current +625c, v21 -858c. It fixes current v2 failures but gives back too much historical v21 edge.
- `score_min60` versus v2 paired delta: current +1047c, v21 -703c. Its disagreement bucket is positive on both datasets, but total v21 edge is still materially below v2.
- Physics read: the current regime punishes pure Brownian side selection; book/Brownian consensus is catching real side-flip failures. The historical v21 data still says pure Brownian had a stronger cheap-entry profit profile. This needs live forward evidence, not promotion.

Refreshed falsification diagnostics:

- Reran `probe_v2_tradeable_veto_scan.py` on the refreshed ledger. Best one-feature v2 veto remains `adverse_move_15m<=75`, improving current/v21 by +277c/+211c while keeping 87.69%/85.97% coverage, but OOS ROI floor is still negative (-17.30%). Do not lock as a simple veto.
- Reran `probe_v2_touch_disagreement_diagnostic.py`. Touch disagreement remains bad: current touch-v2 disagreement delta -764c, v21 -1105c. Do not use touch disagreement as the failure signal.

Same-heartbeat hybrid test:

- Added and ran `probe_v2_consensus_override_scan.py`.
- Hypothesis: keep v2's cheap Brownian entry unless book/Brownian consensus disagrees at the same decision instant.
- Result: all 64 hybrid policies produced 0c/0c delta versus v2. The current candidate edge does not exist at the same heartbeat; it appears only after waiting for later book/price/path information.
- That explains the direct-candidate tradeoff: disagreement buckets can fix v2, but same-side markets lose edge from worse entry timing/prices.
- Updated `probe_frontier_candidate_v2_diagnostic.py` to show same-side penalty explicitly. `score_min60` same-side delta is current/v21 -1255c/-1021c, while its disagreement delta is +2302c/+318c.
- Physics read: the tradable object is not a simple instantaneous prior replacement. It is a timing problem: when to wait for consensus because Brownian is unstable, and when waiting only taxes an already-correct v2 side.

Conditional wait scan:

- Added `probe_v2_conditional_wait_scan.py`.
- Corrected the first version before relying on it: replacement candidate rows must occur at or after the v2 row that triggered the wait.
- Causal result after the fix: 60 rules scanned, 54 preserved 80% coverage on both datasets, 13 were OOS-positive on both datasets.
- Best row: `wait_for_score_min60_if_v2_seconds_to_close>=600`, current/v21 delta versus v2 +1029c/-725c, current +1320c, v21 +558c, both about 99% coverage, OOS ROI floor 1.25%.
- This is only a slight improvement over the already forward-locked direct `score_min60` candidate (+1301c current / +534c v21). The marginal gain is not large enough to justify more strict-monitor complexity before the first forward samples arrive.

First post-lock strict capture:

- After the 22:30 UTC causal boundary, ran `probe_profit_lock_pending_signal_monitor.py --fetch-btc-candles`.
- `book_margin` registered its first genuine forward row on `KXBTC15M-26MAY031845-45`: YES at 66c, registered 2026-05-03T22:31:56Z, entry 2026-05-03T22:30:29Z.
- Same row also triggered touch-hazard and touch-overlay; `score_min60` did not fire because `score_min_book_rv15` was below 0.60.
- Feature state at registration: book side 0.655, Brownian RV15 0.521, Brownian RV30 0.523, margin/RV15 +0.054, adverse15 189c, touch_loss 0.957.
- This is a clean forward test of the book-margin prior against a weak Brownian prior. It is pending until the 18:45 EDT / 22:45 UTC market resolves.

18:45 EDT / 22:45 UTC settlement:

- `KXBTC15M-26MAY031845-45` resolved YES.
- `book_margin` first forward row won: YES 66c, +32c.
- `score_min60` also fired later before close and won: YES 86c, +13c.
- V2/original/challenger/kinetic rows flipped to NO at 57c and lost -59c.
- Touch-hazard/touch-overlay stayed with the early YES 66c and won +32c.
- This is a clean first forward win for the new book-margin prior and another strict failure for v2, but it is still a 1-row sample and not proof.

Current pending 19:00 EDT / 23:00 UTC:

- `book_margin` is pending YES 64c.
- V2, original, challenger, score_min60, kinetic rows, and `v2_wait_score_min60_early` are pending YES 67c.
- Touch-hazard/touch-overlay are pending YES 56c.
- The conditional wait lock file is `logs/edge_research/profit_v2_wait_score_min60_early_lock.json`, effective at 2026-05-03T22:45:00Z. It now has its first strict pending row.

Latest strict state after 18:45 settlement:

- `book_margin`: 2 registered / 1 resolved / 1 pending, 1/0, +32c, 100% registered coverage so far.
- `score_min60`: 2/1/1, 1/0, +13c.
- `v2_wait_score_min60_early`: 1/0/1, no resolved rows yet.
- `frontier_v2`: 12/11/1, 6/5, -82c. V2 is now negative in strict registered evidence.
- No lock clears registered Wilson or Bayesian readiness gates.

19:00 EDT / 23:00 UTC settlement:

- `KXBTC15M-26MAY031900-00` resolved NO.
- The broad YES alignment failed: book_margin YES 64c lost -66c; v2/original/challenger/score_min60/kinetic rows YES 67c lost -69c; touch rows YES 56c lost -58c.
- Conditional wait first resolved row also lost: score_min60 YES 67c, -69c.
- New strict state: book_margin 3 registered / 2 resolved / 1 pending, 1/1, -34c; score_min60 3/2/1, 1/1, -56c; v2_wait_score_min60_early 2/1/1, 0/1, -69c.
- V2 strict state deteriorated further: 13/12/1, 6/6, -151c.
- Current 19:15 EDT / 23:15 UTC pending rows are mostly NO: book_margin/v2/original/challenger/score_min60/kinetic/conditional wait are NO 64c; touch rows are NO 60c.
- No lock clears registered Wilson or Bayesian readiness gates.

19:15 EDT / 23:15 UTC settlement:

- `KXBTC15M-26MAY031915-15` resolved NO.
- The broad NO alignment won: book_margin/v2/original/challenger/score_min60/kinetic/conditional wait NO 64c won +34c; touch rows NO 60c won +38c.
- New strict state: book_margin 4 registered / 3 resolved / 1 pending, 2/1, 0c net; score_min60 4/3/1, 2/1, -22c; v2_wait_score_min60_early 3/2/1, 1/1, -35c.
- V2 improved slightly but remains negative: 14/13/1, 7/6, -117c.
- Current 19:30 EDT / 23:30 UTC pending rows are again mostly NO: book_margin/v2/original/challenger/score_min60/kinetic/conditional wait are NO 68c; touch rows are NO 71c.
- No lock clears registered Wilson or Bayesian readiness gates.

Tradeable veto scan and early book-margin lock:

- Added and ran `probe_candidate_tradeable_veto_scan.py`.
- Scope: one-feature vetoes on locked high-coverage candidates while preserving at least 80% recurring BTC 15m market coverage on both current and v21 ledgers.
- Scan result: 168 rules tested, 78 kept at least 80% coverage on both datasets, 65 were OOS-positive on both datasets.
- Best interpretable row: `book_margin: seconds_to_close>=480`, current/v21 delta versus base book_margin +30c/+294c.
- Discovery metrics for that row: current +886c, 70.98% accuracy, 96.23% coverage; v21 +719c, 72.60% accuracy, 94.12% coverage; OOS ROI floor 0.83%.
- Physics read: this is a timing veto, not a new side prior. It keeps the book/Brownian consensus side but avoids late entries where the order book state is more likely to be chase/noise than useful pressure.
- Forward lock added: `logs/edge_research/profit_frontier_book_margin_early_lock.json`.
- Lock policy: `choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=480; margin_rv15>=0`.
- Created UTC: 2026-05-03T23:22:34.1319711Z. The first eligible full-market boundary is after creation, so zero strict rows before the 19:45 EDT / 23:45 UTC market is expected.
- Patched the strict pending monitor, readiness report, candidate diagnostics, and stability audit to include `book_margin_early`.
- `book_margin_early` has no resolved evidence yet and is not promotion-ready.

19:30 EDT / 23:30 UTC settlement:

- `KXBTC15M-26MAY031930-30` resolved NO.
- The broad NO alignment won. `book_margin`, `frontier_v2`, `original`, `challenger`, `score_min60`, kinetic variants, and `v2_wait_score_min60_early` were all NO 68c and won +30c.
- Touch rows were earlier NO 71c and won +27c.
- New strict state: `book_margin` 5 registered / 4 resolved / 1 pending, 3/1, +30c net; `score_min60` 4/4/0, 3/1, +8c; `v2_wait_score_min60_early` 3/3/0, 2/1, -5c.
- `frontier_v2` improved to 14/14/0, 8/6, -87c, but still fails readiness and remains negative in strict evidence.
- Current 19:45 EDT / 23:45 UTC pending row: `book_margin` and first valid `book_margin_early` are NO 63c at 2026-05-03T23:30:35.143Z, with book side 0.625, Brownian RV15 side 0.5024, and margin/RV15 0.0061.
- Touch-hazard/touch-overlay are also pending NO 63c for 19:45. `score_min60`, `frontier_v2`, and `v2_wait_score_min60_early` have no 19:45 pending row yet at the 23:30:37Z registration refresh.
- No lock clears registered Wilson or Bayesian readiness gates.

Rich conditional wait scan and lock:

- Added and ran `probe_v2_rich_conditional_wait_scan.py`.
- Scope: causal two-condition wait rules. Take V2 immediately unless the first V2 row is early and optionally matches one instability flag; if triggered, wait for the first later locked candidate row in the same market.
- Rules scanned: 324; 302 preserved at least 80% coverage on both current and v21; 36 were OOS-positive on both datasets.
- Best row: `wait_for_score_min60_if_v2_seconds_to_close>=600_AND_brownian_p_rv_15m<=0.7`.
- Broad current/v21 result for best row: current +1345c, 76.05% accuracy, 98.87% coverage; v21 +755c, 74.31% accuracy, 98.64% coverage.
- Delta versus V2: current +1178c, v21 -528c, combined +650c. This improves the earlier simple conditional wait on both current and v21 broad ledgers, but still gives back v21 edge versus pure V2.
- OOS ROI floor is only 0.15%, so this is not promotion evidence.
- Added forward lock `logs/edge_research/profit_v2_wait_score_min60_brownian70_early_lock.json`.
- Lock policy: take `frontier_v2` unless first V2 has `seconds_to_close>=600` and `brownian_p_rv_15m<=0.70`, then wait for `score_min60`.
- Created UTC: 2026-05-03T23:42:23.954125Z. Effective entry boundary: 2026-05-03T23:45:00Z, so zero strict rows before the 20:00 EDT / 00:00 UTC market is expected.
- Patched the strict pending monitor, readiness report, and candidate stability audit to track `v2_wait_score_min60_brownian70_early`.
- The new lock is research-only and has no strict resolved evidence yet.

19:45 EDT / 23:45 UTC settlement:

- `KXBTC15M-26MAY031945-45` resolved NO.
- Early book/touch NO rows won: `book_margin` and first valid `book_margin_early` were NO 63c and won +35c; touch-hazard/touch-overlay were also NO 63c and won +35c.
- Later Brownian/score rows split badly: `frontier_v2`, `frontier_v2_continuous`, `score_min60`, `kinetic_touch`, and `v2_wait_score_min60_early` were YES 66c and lost -68c.
- Challenger/original/kinetic guarded rows later moved to NO 66c and won +32c.
- New strict state after sequential denominator/readiness refresh: `book_margin` 6 registered / 5 resolved / 1 pending, 4/1, +65c; `book_margin_early` 2/1/1, 1/0, +35c; `score_min60` 6/5/1, 3/2, -60c; `v2_wait_score_min60_early` 5/4/1, 2/2, -73c; `frontier_v2` 16/15/1, 8/7, -155c.
- First strict row for `v2_wait_score_min60_brownian70_early` registered on the 20:00 EDT / 00:00 UTC market: NO 68c, entry 2026-05-03T23:46:06.411Z, book side 0.675, Brownian RV15 side 0.6867, score_min 0.675. It is pending.
- Current 20:00 EDT / 00:00 UTC pending alignment is mostly NO. Book_margin/book_margin_early are NO 69c; score_min60/V2/simple wait/rich wait are NO 68c; touch rows are earlier NO 60c.
- No lock clears registered Wilson or Bayesian readiness gates.

Coherence-gated book-margin scan and lock:

- After refreshing the broad heartbeat ledger through the 19:45 settlement, reran `probe_candidate_tradeable_veto_scan.py`, `probe_profit_lock_candidate_stability_audit.py`, `probe_frontier_candidate_v2_diagnostic.py`, and `probe_v2_rich_conditional_wait_scan.py`.
- The updated scan demoted `book_margin_early` on current validation: current +951c / v21 +719c, but current validation -61c. It remains strict-forward evidence only.
- Best high-coverage veto row became `book_margin: abs_book_rv15_gap<=0.15`: current +1292c, 72.08% accuracy, 89.89% coverage; v21 +306c, 70.56% accuracy, 96.83% coverage; OOS ROI floor 5.57%.
- Physics read: keep the book-margin side only when the book-implied side and Brownian RV15 side are coherent within 15 percentage points. This avoids treating extreme book/Brownian dislocation as reliable pressure.
- Added forward lock `logs/edge_research/profit_frontier_book_margin_gap015_lock.json`.
- Important correction before any resolved forward rows: the first implementation accidentally behaved like "wait for a later row that passes the gap," but the discovery scan was a true veto of the first book-margin row. Patched the strict monitor and diagnostics so `book_margin_gap015` now filters the first base book-margin row without replacement.
- Verified corrected broad metrics: current +1292c / 89.89% coverage; v21 +306c / 96.83% coverage.
- Effective boundary is 2026-05-04T00:00:00Z, so the first strict pending row is correctly on the 20:15 EDT / 00:15 UTC market, not the already-open 20:00 market.

20:00 EDT / 00:00 UTC settlement:

- `KXBTC15M-26MAY032000-00` resolved NO.
- The broad NO alignment won. `book_margin` NO 69c won +29c; `book_margin_early` NO 69c won +29c; V2/score/simple wait/rich wait/kinetic guarded rows NO 68c won +30c; touch rows NO 60c won +38c.
- First resolved `v2_wait_score_min60_brownian70_early` row won: NO 68c, +30c.
- New strict state after sequential refresh: `book_margin` 7 registered / 6 resolved / 1 pending, 5/1, +94c; `book_margin_early` 3/2/1, 2/0, +64c; `book_margin_gap015` 1/0/1; `score_min60` 7/6/1, 4/2, -30c; `v2_wait_score_min60_early` 6/5/1, 3/2, -43c; `v2_wait_score_min60_brownian70_early` 2/1/1, 1/0, +30c; `frontier_v2` 17/16/1, 9/7, -125c.
- Current 20:15 EDT / 00:15 UTC pending alignment is NO across most tracked locks. `book_margin_gap015` first strict row is pending NO 69c with book side 0.685, Brownian RV15 side 0.7627, and abs gap 0.0777.
- No lock clears registered Wilson or Bayesian readiness gates.

Sample-size gate refresh:

- Ran `probe_profit_lock_sample_size_requirements.py`.
- No lock meets the fresh EV sample-size gate yet.
- Current extra perfect wins needed to clear Wilson-over-break-even from fresh state: `book_margin` 9, `book_margin_early` 7, `book_margin_gap015` 8, `v2_wait_score_min60_brownian70_early` 10, `score_min60` 16, `v2_wait_score_min60_early` 15.
- This confirms the current live evidence is useful directionally but still far below promotion-quality sample size.

Strict failure attribution refresh:

- Ran `probe_profit_lock_strict_failure_attribution.py`.
- Strict resolved rows: 351.
- Best new strict summaries: `book_margin` 6 resolved, 5/1, +94c; `book_margin_early` 2 resolved, 2/0, +64c; `v2_wait_score_min60_brownian70_early` 1 resolved, 1/0, +30c.
- Existing pure/mostly Brownian locks remain negative in strict evidence: `frontier_v2` 16 resolved, 9/7, -125c; `score_min60` 6 resolved, 4/2, -30c; `v2_wait_score_min60_early` 5 resolved, 3/2, -43c.

Temporal side-flip diagnostic:

- Added and ran `probe_temporal_side_flip_diagnostic.py`.
- Purpose: test the physics story from the 19:45 market, where early book NO beat a later Brownian/score YES.
- Result: broad paired data does not support a general "early book beats later side flip" rule.
- Current `book_margin_gap015` vs V2 when book was earlier and side flipped: 6 pairs, anchor-reference -13c.
- Current `book_margin_gap015` vs score_min60 when book was earlier and side flipped: 22 pairs, anchor-reference -1064c.
- V21 `book_margin_gap015` vs V2 when book was earlier and side flipped: 2 pairs, -197c.
- V21 `book_margin_gap015` vs score_min60 when book was earlier and side flipped: 13 pairs, -381c.
- Physics read: the recent strict 19:45 row was not enough to promote an early-book-over-later-score flip rule. The better-supported idea remains coherence/timing gating, not blindly preferring the first book side after a later side flip.

20:15 EDT / 00:15 UTC settlement:

- `KXBTC15M-26MAY032015-15` resolved NO.
- Broad NO alignment won again.
- `book_margin`, `book_margin_early`, and first resolved `book_margin_gap015` were all NO 69c and won +29c.
- V2/original/challenger/score/simple wait/rich wait/kinetic rows were also NO 69c and won +29c.
- Touch rows were earlier NO 57c and won +41c.
- New strict state after sequential denominator/readiness refresh: `book_margin` 8 registered / 7 resolved / 1 pending, 6/1, +123c; `book_margin_early` 4/3/1, 3/0, +93c; `book_margin_gap015` 2/1/1, 1/0, +29c; `score_min60` 7/7/0, 5/2, -1c; `v2_wait_score_min60_early` 6/6/0, 4/2, -14c; `v2_wait_score_min60_brownian70_early` 2/2/0, 2/0, +59c; `frontier_v2` 18/17/1, 10/7, -96c.
- Current 20:30 EDT / 00:30 UTC pending: `book_margin`, `book_margin_early`, `book_margin_gap015`, `frontier_v2`, challenger, original, and V2-continuous are NO 65c around 00:17:09Z. Touch rows are YES 58c from 00:15:24Z. Score_min60 and conditional waits did not register a 20:30 row yet in the strict registry.
- No lock clears registered Wilson or Bayesian readiness gates.

20:24 EDT refreshed conditional-wait scan:

- Reran `probe_v2_conditional_wait_scan.py` and `probe_v2_rich_conditional_wait_scan.py` after the 20:15 settlement refresh.
- Simple conditional wait scan: 60 rules scanned; 53 preserved at least 80% coverage on both current and v21; 13 were OOS-positive on both datasets.
- Rich conditional wait scan: 324 rules scanned; 300 preserved at least 80% coverage on both current and v21; 35 were OOS-positive on both datasets.
- Best rich row remained the already-forward-locked `wait_for_score_min60_if_v2_seconds_to_close>=600_AND_brownian_p_rv_15m<=0.7`.
- Latest broad metrics for that row: current +1339c, 75.94% accuracy, 98.88% coverage; v21 +755c, 74.31% accuracy, 98.64% coverage.
- Delta versus V2 remains current-positive but v21-negative: +1175c current, -528c v21.
- Physics read: this still looks like a regime-repair rule for the current data rather than a universal replacement for V2. Keep it in strict forward validation; do not promote.

20:30 EDT / 00:30 UTC settlement:

- `KXBTC15M-26MAY032030-30` resolved NO.
- The coherent book/Brownian NO family won. `book_margin`, `book_margin_early`, `book_margin_gap015`, challenger, original, V2, and V2-continuous were all NO 65c from 2026-05-04T00:17:09Z and won +33c.
- Later score/conditional-wait rows also chose NO but entered worse at 77c. `score_min60`, `v2_wait_score_min60_early`, and `v2_wait_score_min60_brownian70_early` won +21c.
- Touch was the useful failed prior: `touch_hazard` and `touch_overlay` registered earlier YES 58c and lost -60c.
- Updated strict state after settlement: `book_margin` 9 registered / 8 resolved / 1 pending, 7/1, +156c; `book_margin_early` 5/4/1, 4/0, +126c; `book_margin_gap015` 3/2/1, 2/0, +62c; `score_min60` 8/8/0, 6/2, +20c; `v2_wait_score_min60_early` 7/7/0, 5/2, +7c; `v2_wait_score_min60_brownian70_early` 3/3/0, 3/0, +80c; `frontier_v2` 19/18/1, 11/7, -63c.
- Current 20:45 EDT / 00:45 UTC pending: book/V2/original/challenger/touch locks registered NO 61c at 2026-05-04T00:30:40Z. `book_margin_gap015` passed coherence with abs book-vs-RV15 gap 0.0386. Score and conditional-wait locks had not registered yet at the first post-close refresh.
- No lock clears registered Wilson or Bayesian readiness gates.

20:30 refreshed broad diagnostics:

- Refreshed heartbeat ledger: raw rows 31406; physics rows 31162; opportunities 4017.
- Stability audit still favors high-coverage book/score families over raw V2 in the current regime, but not enough for promotion: `book_margin_gap015` current +1354c, 72.31% accuracy, 89.63% coverage; v21 +306c, 70.56% accuracy, 96.83% coverage. `v2_wait_score_min60_brownian70_early` current +1360c, 76.03% accuracy, 98.89% coverage; v21 +755c, 74.31% accuracy, 98.64% coverage.
- Locked fresh validations after the refresh: `book_margin_gap015` 2/2, +62c, 100% fresh coverage; rich conditional wait 3/3, +80c, 100% fresh coverage; simple conditional wait 5/2, +10c.
- Candidate veto scan still ranks `book_margin: seconds_to_close>=480` first by balanced current/v21 improvement, but `book_margin_gap015` remains the stronger current-regime coherence rule and is already forward-locked. Neither should be promoted without strict sample-size clearance.
- Temporal side-flip diagnostic remains hostile to "early book beats later side flip": current `book_margin_gap015` vs score anchor-earlier side-flip is 22 pairs, -1064c. Keep rejecting that prior.
- Sample-size gate remains failed for every lock. Registered readiness remains failed for every lock. Goal is not complete.

20:45 EDT / 00:45 UTC settlement and verifier correction:

- `KXBTC15M-26MAY032045-45` resolved NO.
- This was a useful timing-split row. Early coherent book/Brownian/touch registered NO 61c at 2026-05-04T00:30:40Z and won +37c. Later score/rich-wait registered YES 65c at 2026-05-04T00:34:55Z and lost -67c. Kinetic rows also flipped YES 61c and lost -63c.
- Strict state after settlement: `book_margin` 10 registered / 9 resolved / 1 pending, 8/1, +193c; `book_margin_early` 6/5/1, 5/0, +163c; `book_margin_gap015` 3/3/0, 3/0, +99c; `score_min60` 10/9/1, 6/3, -47c; `v2_wait_score_min60_early` 9/8/1, 5/3, -60c; `v2_wait_score_min60_brownian70_early` 5/4/1, 3/1, +13c; `frontier_v2` 20/19/1, 12/7, -26c.
- Physics read: this row supports the coherence-gated early book side over a late weak score flip, but the broader temporal side-flip diagnostic still says not to generalize blindly. Keep this as strict evidence, not a new threshold change.
- Found and fixed a verification leak: after `--fetch-btc-candles`, recomputed Brownian/RV features can move the first eligible row. For the 20:45 rich wait, recomputation selected a later NO 78c winner at 00:38:11Z, while the strict live registry correctly held the earlier YES 65c loser at 00:34:55Z.
- Patched `probe_v2_conditional_wait_forward_validation.py`, `probe_v2_rich_conditional_wait_forward_validation.py`, and `probe_profit_frontier_locked_policy_validation.py` so reports show both recomputed fresh metrics and strict registered fresh metrics, plus row-level recompute-drift examples.
- Patched `probe_profit_lock_sample_size_requirements.py` to prefer `profit_lock_registered_signal_readiness_latest.json` for every lock. This makes the sample-size gate consistently strict instead of mixing recomputed and registered evidence.
- Recompiled patched scripts successfully with `python -m py_compile`.
- Corrected sample-size gate remains failed for every lock. Best strict high-coverage candidates now need additional perfect selected wins to clear Wilson over break-even: `book_margin_early` 3, `book_margin` 5, `book_margin_gap015` 5, rich conditional wait 13, score_min60 18. No lock clears registered Wilson or Bayesian readiness gates.
- Goal is not complete.

21:00 EDT / 01:00 UTC settlement:

- `KXBTC15M-26MAY032100-00` resolved YES.
- Broad YES alignment won. `book_margin` and `book_margin_early` registered YES 70c and won +28c. V2/original/challenger/score/rich wait registered YES 72c and won +26c. Kinetic combo/price rows registered YES 68c and won +30c.
- `book_margin_gap015` did not register for this market, so it avoided a win but also lost high-coverage eligibility for the observed denominator.
- New strict state: `book_margin` 10 registered / 10 resolved / 0 pending, 9/1, +221c, 100% resolved coverage; `book_margin_early` 6/6/0, 6/0, +191c, 100% resolved coverage; `book_margin_gap015` 3/3/0, 3/0, +99c, 75% resolved coverage; `score_min60` 10/10/0, 7/3, -21c; `v2_wait_score_min60_early` 9/9/0, 6/3, -34c; `v2_wait_score_min60_brownian70_early` 5/5/0, 4/1, +39c; `frontier_v2` 20/20/0, 13/7, flat 0c.
- Corrected registered sample-size gate still fails every lock. Current extra perfect selected wins needed to clear Wilson over break-even: `book_margin` 4, `book_margin_early` 3, `book_margin_gap015` 5, rich conditional wait 12, score_min60 18.
- Current 21:15 EDT / 01:15 UTC pending immediately after close refresh: only touch locks registered YES 53c at 2026-05-04T01:00:28Z. No book/V2/score lock had registered yet.
- Physics read: `book_margin` is now the best strict high-coverage candidate, not because it is elegant, but because it is currently the only high-coverage lock combining positive strict P&L, 90% resolved accuracy, and full recurring-market coverage. Still not promotion-ready: Wilson lower bound 59.58% remains below 67.90% fee-aware break-even.
- Goal is not complete.

21:15 EDT / 01:15 UTC settlement:

- `KXBTC15M-26MAY032115-15` resolved NO.
- This was a high-information split. Early V2/original registered cheap YES 32c and lost -34c. Touch registered YES 53c and lost -55c. Later book/score/conditional locks registered expensive but coherent NO 81c and won +17c.
- `book_margin_gap015` passed the coherence veto on this market: book side 0.805 vs Brownian RV15 side 0.7223, absolute gap 0.0827.
- New strict state: `book_margin` 12 registered / 11 resolved / 1 pending, 10/1, +238c; `book_margin_early` 8/7/1, 7/0, +208c; `book_margin_gap015` 5/4/1, 4/0, +116c and back at 80% resolved coverage; `score_min60` 11/11/0, 8/3, -4c; `v2_wait_score_min60_early` 10/10/0, 7/3, -17c; `v2_wait_score_min60_brownian70_early` 6/6/0, 5/1, +56c; `frontier_v2` 22/21/1, 13/8, -34c.
- Corrected sample-size gate still fails every lock. Current extra perfect selected wins needed to clear Wilson over break-even: `book_margin` 4, `book_margin_early` 3, `book_margin_gap015` 6, rich conditional wait 12, score_min60 18.
- Current 21:30 EDT / 01:30 UTC pending is another split: book/book_early/gap015 registered YES 62c; early V2/original registered NO 39c; touch registered YES 62c. Score/rich had not registered at first inspection.
- Physics read: the 21:15 row is strong evidence against trusting a cheap early Brownian side when the book/RV coherence later flips hard against it. It supports the current `book_margin`/`book_margin_gap015` direction, but the sample remains far too small to declare a final model.
- Goal is not complete.

21:30 EDT / 01:30 UTC settlement:

- `KXBTC15M-26MAY032130-30` resolved YES.
- This was the mirror image of 21:15. Early V2/original registered NO 39c and lost -41c. Book/book_early/gap015/touch registered YES 62c and won +36c. Score/rich wait joined later at YES 73c and won +25c.
- New strict state: `book_margin` 13 registered / 12 resolved / 1 pending, 11/1, +274c; `book_margin_early` 9/8/1, 8/0, +244c; `book_margin_gap015` 5/5/0, 5/0, +152c; `score_min60` 13/12/1, 9/3, +21c; `score_min60_gap020` 2/1/1, 1/0, +25c; `v2_wait_score_min60_early` 12/11/1, 8/3, +8c; `v2_wait_score_min60_brownian70_early` 8/7/1, 6/1, +81c; `frontier_v2` 23/22/1, 13/9, -75c.
- Corrected sample-size gate still fails every lock. Current extra perfect selected wins needed to clear Wilson over break-even: `book_margin` 3, `book_margin_early` 1, `book_margin_gap015` 4, rich conditional wait 11, score_min60 17.
- `book_margin_early` now shows positive Bayesian p05 edge in the registered readiness table, but it is still not ready because the explicit sample-size floor is nowhere near met.
- Current 21:45 EDT / 01:45 UTC pending: book/book_early/V2/original/kinetic registered YES 84c; score/rich registered later YES 91c. `book_margin_gap015` had not registered at first inspection, which likely means the coherence veto blocked the very expensive early YES row.
- Physics read: two back-to-back split rows now favor the later/book-consensus side over early V2. That is strong live evidence for the current regime, but the broad v21 comparison still says not to delete V2 as a universal prior. Keep gathering strict samples.
- Goal is not complete.

21:45 EDT / 01:45 UTC settlement and cache hardening:

- `KXBTC15M-26MAY032145-45` resolved YES.
- High-price calibration row won. Book/book_early/V2/original/kinetic registered YES 84c and won +15c. Score/rich registered later YES 91c and won only +8c. `book_margin_gap015` did not register, consistent with the coherence veto blocking the very expensive row.
- New strict state: `book_margin` 13/13/0, 12/1, +289c; `book_margin_early` 9/9/0, 9/0, +259c; `book_margin_gap015` 5/5/0, 5/0, +152c; `score_min60` 13/13/0, 10/3, +29c; `score_min60_gap020` 2/2/0, 2/0, +33c; `v2_wait_score_min60_early` 12/12/0, 9/3, +16c; `v2_wait_score_min60_brownian70_early` 8/8/0, 7/1, +89c; `frontier_v2` 23/23/0, 14/9, -60c.
- `book_margin` now has positive registered p05 edge, but still fails readiness because the explicit sample-size floor is unmet. Current sample-size gate remains failed for every lock. Extra perfect selected wins needed to clear Wilson over break-even: `book_margin` 2, `book_margin_early` 1, `book_margin_gap015` 4, rich conditional wait 12, score_min60 18.
- The denominator audit initially failed on a corrupt `coinbase_btc_usd_1m_cache.parquet`, likely due a reader seeing a concurrent partial parquet write.
- Patched `probe_physics_priors_boundary_models.py` so Coinbase candle cache writes are atomic and corrupt cache reads are quarantined instead of crashing the validation chain.
- Recompiled the patched script and reran denominator/readiness/sample-size successfully. Denominator now shows `book_margin`, `book_margin_early`, `score_min60`, simple wait, and rich wait above the 80% registered coverage floor; `book_margin_gap015` is below observed coverage after skipping 21:45 and 22:00 pending.
- Current 22:00 EDT / 02:00 UTC pending: book/book_early/gap015 YES 63c, V2 YES 68c, score/rich YES 77c, touch YES 59c.
- Goal is not complete.

22:00 EDT / 02:00 UTC settlement:

- `KXBTC15M-26MAY032200-00` resolved YES.
- Aligned YES row won. Book/book_early/gap015 registered YES 63c and won +35c. Touch registered YES 59c and won +39c. V2 registered YES 68c and won +30c. Score/rich registered YES 77c and won +21c.
- New strict state: `book_margin` 15 registered / 14 resolved / 1 pending, 13/1, +324c; `book_margin_early` 11/10/1, 10/0, +294c; `book_margin_gap015` 6/6/0, 6/0, +187c; `score_min60` 14/14/0, 11/3, +50c; `score_min60_gap020` 3/3/0, 3/0, +54c; `v2_wait_score_min60_early` 13/13/0, 10/3, +37c; `v2_wait_score_min60_brownian70_early` 9/9/0, 8/1, +110c; `frontier_v2` 25/24/1, 15/9, -30c.
- `book_margin_early` now clears the Wilson-over-break-even math in the sample-size report, but still fails readiness because the explicit sample-size floor is unmet. `book_margin` needs 1 additional perfect selected win to clear Wilson-over-break-even, but it also remains far below the 75-resolved-row floor.
- Denominator/readiness/sample-size all refreshed successfully after the atomic cache patch. No lock clears registered Wilson or Bayesian readiness gates.
- Current 22:15 EDT / 02:15 UTC pending: book/book_early/V2/original/touch registered YES 78c; kinetic combo/price registered YES 68c. `book_margin_gap015`, score, and rich wait had not registered at first inspection.
- Goal is not complete.

22:15 EDT / 02:15 UTC settlement:

- `KXBTC15M-26MAY032215-15` resolved YES.
- High-price YES alignment won again. Book/book_early/V2/original/touch registered YES 78c and won +20c. Kinetic combo/price registered YES 68c and won +30c. Score/rich and the new `book_early_score_gap020_wait` registered later YES 79c and won +19c.
- New strict state: `book_margin` 15/15/0, 14/1, +344c; `book_margin_early` 11/11/0, 11/0, +314c; `book_margin_gap015` 6/6/0, 6/0, +187c; `score_min60` 15/15/0, 12/3, +69c; `score_min60_gap020` 4/4/0, 4/0, +73c; `v2_wait_score_min60_early` 14/14/0, 11/3, +56c; `v2_wait_score_min60_brownian70_early` 10/10/0, 9/1, +129c; `frontier_v2` 25/25/0, 16/9, -10c.
- Readiness is still zero for all locks. `book_margin` and `book_margin_early` clear Wilson-over-break-even but remain blocked by the explicit 75-resolved-row sample-size floor. `book_margin_gap015` remains profitable but has only 66.67% resolved coverage after skipping recent high-gap rows.
- Current best strict candidates:
  - `book_margin`: high coverage, 14/1, +344c, Wilson lower 70.18% vs break-even 70.40%, needs 1 perfect win but far below sample-size floor.
  - `book_margin_early`: high coverage, 11/0, +314c, Wilson lower 74.12% vs break-even 71.45%, but only 11 resolved rows.
  - `book_margin_gap015`: 6/0, +187c, but below 80% observed coverage right now.
- Goal is not complete.

22:30 EDT / 02:30 UTC settlement:

- `KXBTC15M-26MAY032230-30` resolved NO.
- Broad NO alignment won. `book_margin`, `book_margin_early`, `frontier_v2`, `frontier_v2_continuous`, and `kinetic_touch` registered NO 79c at 2026-05-04T02:17:05Z and won +19c.
- Touch rows registered earlier NO 54c and won +44c. Score/score-gap and conditional-wait rows registered later NO 66c and won +32c.
- `book_margin_gap015` did not register because the early book-vs-RV15 gap was 0.211, above its 0.15 coherence ceiling. That means it skipped a winner and its coverage problem worsened.
- New strict state: `book_margin` 17 registered / 16 resolved / 1 pending, 15/1, +363c; `book_margin_early` 13/12/1, 12/0, +333c; `book_margin_gap015` 7/6/1, 6/0, +187c; `score_min60` 17/16/1, 13/3, +101c; `v2_wait_score_min60_early` 16/15/1, 12/3, +88c; `v2_wait_score_min60_brownian70_early` 12/11/1, 10/1, +161c; `frontier_v2` 27/26/1, 17/9, +9c.
- Denominator/readiness/sample-size all remain strict registered evidence. `book_margin`, `book_margin_early`, score, and conditional-wait locks still have 100% registered resolved coverage; `book_margin_gap015` is now only 60% resolved coverage and 63.64% registered observed coverage.
- `book_margin` and `book_margin_early` now clear Wilson-over-break-even and Bayesian edge math, but both remain blocked by the explicit sample-size floor. Current sample-size table: `book_margin` 16 selected fresh rows, 15/1, Wilson low 71.67% vs 71.06% break-even, +363c, not completion-ready; `book_margin_early` 12/12, Wilson low 75.75% vs 72.25% break-even, +333c, not completion-ready.
- Current 22:45 EDT / 02:45 UTC pending: `book_margin`, `book_margin_early`, and `book_margin_gap015` registered YES 61c; touch rows registered YES 57c; V2/original/challenger/score/score-gap/conditional waits registered YES 68c; kinetic guards registered YES 67c. This is a broad YES row with the book/gap/touch side entering cheaper than score/V2.
- Physics read: the profitable high-coverage signal is still the book-margin side, not the coherence-vetoed subset. The gap veto remains useful as a diagnostic of book/Brownian agreement, but as a standalone policy it is now disqualified by the user's >=75-80% recurring-market coverage requirement.
- Goal is not complete.

22:37-22:43 EDT research-only iteration:

- Refreshed `probe_book_to_score_wait_scan.py` after the 22:30 settlement. The best coverage-valid causal wait row is now `book_margin_wait_for_score_min60_gap020_enter_ref_if_seconds_to_close>=480`: current 272/277 markets, 77.21% accuracy, 98.19% coverage, +1654c; v21 219/221 markets, 73.52% accuracy, 99.10% coverage, +493c.
- This rule is physically interpretable as a coverage-preserving replacement for the failed standalone gap veto: start from the high-coverage book-margin pressure side, but if the book setup arrives early enough, wait for the later score side that also passes the <=20 percentage-point book/Brownian coherence check.
- The already locked `book_early_score_gap020_wait` remains positive in strict registered rows: 3 registered / 2 resolved / 1 pending, 2/0, +51c, 100% registered coverage, but still tiny and not promotion-ready.
- Added a separate research-only forward lock, `book_score_gap020_wait`, in `logs\edge_research\profit_book_score_gap020_wait_lock.json`. It does not replace any existing lock and does not touch live bot behavior.
- Wired `book_score_gap020_wait` through the pending registry, denominator audit, registered readiness, sample-size monitor, Bayesian monitor, and book-to-score forward validator.
- Compiled patched research monitors successfully: `probe_profit_lock_pending_signal_monitor.py`, `probe_book_to_score_wait_forward_validation.py`, `probe_profit_lock_registered_signal_readiness.py`, `probe_profit_lock_sample_size_requirements.py`, and `probe_profit_lock_bayesian_ev_monitor.py`.
- Set the new lock's effective boundary to 2026-05-04T02:45:00Z, so its strict evidence starts after the rule was selected. Current state is intentionally `waiting`: 0 registered / 0 resolved / 0 pending.
- Refreshed pending monitor, denominator audit, registered readiness, sample-size, and Bayesian EV monitor after wiring the lock. No lock clears promotion gates; `book_score_gap020_wait` is not evidence yet, only a clean forward trial.
- Physics read: this is the current best trial architecture for the user's coverage constraint. Pure coherence filtering was too selective; a wait/fallback architecture may preserve market frequency while asking the Brownian/book agreement question only when it can improve entry quality.
- Goal is not complete.

22:45 EDT / 02:45 UTC settlement:

- `KXBTC15M-26MAY032245-45` resolved YES.
- The broad YES row won. `book_margin`, `book_margin_early`, and `book_margin_gap015` registered YES 61c at 2026-05-04T02:30:36Z and won +37c.
- Touch rows registered earlier YES 57c and won +41c. V2/original/challenger/score/score-gap/conditional waits registered YES 68c and won +30c. Kinetic guard/price/combo registered YES 67c and won +31c.
- The locked `book_early_score_gap020_wait` strict row also won: YES 68c, +30c. It is now 3/3 strict fresh, +81c, 100% resolved coverage, but still far too small for promotion.
- New strict state after denominator/readiness/sample-size refresh: `book_margin` 17/17/0, 16/1, +400c; `book_margin_early` 13/13/0, 13/0, +370c; `book_margin_gap015` 7/7/0, 7/0, +224c; `score_min60` 17/17/0, 14/3, +131c; `score_min60_gap020` 6/6/0, 6/0, +135c; `v2_wait_score_min60_brownian70_early` 12/12/0, 11/1, +191c; `frontier_v2` 28/27/1, 18/9, +39c.
- `book_margin` and `book_margin_early` still clear Wilson-over-break-even and Bayesian edge math, but remain blocked by the explicit sample-size floor. `book_margin` is 17 selected fresh rows, 16/1, Wilson low 73.02% vs 70.59% break-even, +400c. `book_margin_early` is 13/13, Wilson low 77.19% vs 71.54% break-even, +370c.
- `book_margin_gap015` recovered one win but still fails coverage: 7/11 resolved post-lock markets, 63.64% resolved coverage. It remains disqualified as a standalone policy under the 75-80% recurring-market requirement.
- The new broader `book_score_gap020_wait` lock remains a clean forward trial with no strict rows yet. Boundary is 2026-05-04T02:45:00Z; denominator now sees one unclosed post-boundary market and zero registered rows, so state is still `waiting`, not evidence.
- Current 23:00 EDT / 03:00 UTC first pending snapshot is split: early V2/original/frontier rows registered YES 39c at 02:45:38Z, while touch rows registered NO 62c at the same timestamp. No `book_margin` or new `book_score_gap020_wait` row had registered at first refresh.
- Physics read: the current regime keeps rewarding book/touch-consensus YES pressure and punishing the idea that a higher price is automatically a bad trade. But the first 23:00 split also warns that cheap early Brownian/V2 can disagree with touch/book pressure; keep treating timing and source-of-probability as causal variables, not interchangeable model outputs.
- Goal is not complete.

22:51-22:55 EDT stability refresh and second research-only trial:

- Refreshed stability/veto/frontier/temporal diagnostics after the 22:45 settlement.
- Broad stability remains mixed: current data favors score/gap/wait families, while independent v21 still gives significant paired edge back to the older V2 in some buckets. This reinforces that strict forward evidence is mandatory.
- `candidate_tradeable_veto_scan_latest.md` surfaced a stronger physical veto than pure book/RV agreement: `book_margin: adverse_move_15m<=100`. It preserves high coverage on both ledgers and improves both: current 202/218 markets, 71.78% accuracy, 92.66% coverage, +901c; v21 207/221 markets, 72.46% accuracy, 93.67% coverage, +617c.
- The physical interpretation is path displacement: do not chase the book-margin side after a large adverse 15m move, because the apparent book edge may be path-stressed rather than stable pressure.
- Added another research-only forward lock, `book_margin_adverse100`, in `logs\edge_research\profit_frontier_book_margin_adverse100_lock.json`. It starts at 2026-05-04T03:00:00Z, so it does not count the current 23:00 market.
- Wired `book_margin_adverse100` through the pending registry, locked-policy validator, denominator audit, registered readiness, sample-size monitor, and Bayesian monitor. Recompiled patched research monitors successfully.
- Current `book_margin_adverse100` state is intentionally `waiting`: 0 registered / 0 resolved / 0 pending. This is a clean forward trial, not evidence yet.
- Updated 23:00 pending state after later refresh: `book_margin`, `book_margin_early`, and `book_margin_gap015` registered NO 65c at 02:46:23Z; `book_score_gap020_wait`, score/score-gap, V2 conditional waits, and kinetic_touch registered NO 72c at 02:47:08Z; touch rows remained earlier NO 62c; early V2/original/frontier stayed YES 39c. Kinetic_guard later flipped to YES 77c at 02:52:08Z.
- This 23:00 market is now a high-information split: if NO wins, the later book/touch/score consensus beats cheap early V2. If YES wins, the adverse-move veto idea gets immediate support because it would have skipped the high-adverse book NO row, though the new formal lock will not count this market due its 03:00 boundary.
- Goal is not complete.

23:00 EDT / 03:00 UTC settlement:

- `KXBTC15M-26MAY032300-00` resolved YES.
- Cheap early Brownian/V2/original YES won. `frontier_v2`, `frontier_v2_continuous`, and `original` registered YES 39c at 2026-05-04T02:45:38Z and won +59c.
- Later book/touch/score consensus NO lost. `book_margin`, `book_margin_early`, and `book_margin_gap015` were NO 65c and lost -67c; touch/challenger NO 62c lost -64c; score/score-gap/V2 wait/`book_score_gap020_wait` NO 72c lost -74c.
- `kinetic_guard` was the useful late flip winner: YES 77c at 02:52:08Z won +21c.
- This row damaged the current book thesis and strongly supports the new adverse-move veto intuition. The losing book NO row had adverse_move_15m about 302c; the losing wait/score NO row had adverse_move_15m about 289c. The `book_margin_adverse100` rule would have skipped this path-stressed setup, but its formal forward lock starts at 03:00Z and does not count this market.
- New strict state: `book_margin` 18/18/0, 16/2, +333c; `book_margin_early` 14/14/0, 13/1, +303c; `book_margin_gap015` 8/8/0, 7/1, +157c; `score_min60` 18/18/0, 14/4, +57c; `score_min60_gap020` 7/7/0, 6/1, +61c; `book_early_score_gap020_wait` 4/4/0, 3/1, +7c; `book_score_gap020_wait` 1/1/0, 0/1, -74c; `frontier_v2` 28/28/0, 19/9, +98c; `frontier_v2_continuous` 19/19/0, 13/6, +51c.
- Readiness impact: `book_margin` no longer clears Wilson-over-break-even after this loss. Registered sample-size report now shows `book_margin` 18 selected fresh rows, 16/2, Wilson low 67.20% vs 70.39% break-even, +333c, needs 3 perfect selected wins to clear Wilson again. `book_margin_early` also falls below Wilson-over-break-even and needs 2 perfect wins.
- Current 23:15 EDT / 03:15 UTC pending: broad NO alignment. `book_margin`, `book_margin_early`, `book_margin_gap015`, the new `book_margin_adverse100`, frontier_v2, touch, and kinetic guards registered NO 62c at 03:00:39Z. `book_early_score_gap020_wait`, `book_score_gap020_wait`, challenger, original, score/score-gap, and V2 conditional waits registered later NO 80c at 03:02:09Z.
- `book_margin_adverse100` has its first clean forward pending row: NO 62c with adverse_move_15m only 12.32c, book/RV gap 0.052, and 100% observed registered coverage so far. This is exactly the kind of low-path-stress book row the veto is meant to keep.
- Goal is not complete.

23:15 EDT / 03:15 UTC settlement:

- `KXBTC15M-26MAY032315-15` resolved YES.
- The broad NO alignment failed for the second consecutive market. `book_margin`, `book_margin_early`, `book_margin_gap015`, `frontier_v2`, touch, and kinetic guards registered NO 62c at 03:00:39Z and lost -64c.
- Later score/original/conditional waits and `book_score_gap020_wait` registered NO 80c at 03:02:09Z and lost -82c.
- First formal `book_margin_adverse100` row also lost: NO 62c, adverse_move_15m 12.32c, book/RV gap 0.052, -64c. This rejects the simple version of the adverse-displacement veto as an immediate fix.
- New strict state: `book_margin` 20 registered / 19 resolved / 1 pending, 16/3, +269c; `book_margin_early` 16/15/1, 13/2, +239c; `book_margin_gap015` 10/9/1, 7/2, +93c; `book_margin_adverse100` 1/1/0, 0/1, -64c; `score_min60` 19/19/0, 14/5, -25c; `score_min60_gap020` 8/8/0, 6/2, -21c; `book_early_score_gap020_wait` 5/5/0, 3/2, -75c; `book_score_gap020_wait` 2/2/0, 0/2, -156c; `v2_wait_score_min60_brownian70_early` 14/14/0, 11/3, +35c; `frontier_v2` 30/29/1, 19/10, +34c.
- Readiness/sample-size remain failed for every lock. `book_margin` is still the best high-coverage strict candidate by net P&L, but after two losses its Wilson lower bound is only 62.43% vs 70.05% break-even and it needs 7 perfect selected wins to clear Wilson again.
- `book_margin_gap015` remains below coverage floor: 9/13 resolved markets, 69.23% resolved coverage. `book_score_gap020_wait` now fails both P&L and observed coverage. `book_margin_adverse100` is 0/1 and observed coverage only 50% after missing the unclosed 23:30 market at first refresh.
- Current 23:30 EDT / 03:30 UTC pending first snapshot: early YES 51c for challenger/frontier_v2/frontier_v2_continuous/original/touch/kinetic families at 03:15:10Z. No book/score locks had registered yet at that first refresh.
- Physics read: the last two rows show a regime flip where cheap early Brownian/YES beat later book/touch/score NO, even when the book NO row had low adverse displacement and good book/RV coherence. The next hypothesis should not be a single scalar veto; it needs a regime detector for early Brownian reversion versus book-pressure continuation.
- Goal is not complete.

23:19-23:26 EDT regime-switch scan:

- Added `probe_book_v2_regime_switch_scan.py`, a research-only current/v21 scan for high-coverage switches between book-margin anchors and Brownian/score references. It does not touch live bot code or submit orders.
- Scan compiled and ran successfully: 1122 rules scanned, all preserving >=80% coverage on both datasets by switching instead of skipping; 988 were OOS-positive while coverage-valid.
- Strongest result is diagnostic, not directly tradable: `book_margin_switch_to_score_min60_gap020_if_side_disagree` produced current +1274c vs book anchor and v21 +381c, with about 99% coverage on both ledgers. This says book-vs-score side disagreement is the real fault line.
- The same top row is pair-dependent: it relies on knowing the later score disagreement while still pretending the old book entry is available when there is no disagreement. Treat it as failure-mode evidence, not a forward-lock policy.
- Best clean causal-class rows are weaker and mixed:
  - `book_margin_switch_to_frontier_v2_if_anchor_entry_hour_utc==04`: current +568c, v21 +284c, current/v21 coverage about 99%, OOS ROI floor 7.39%. This is a possible session/liquidity regime switch, but time-of-day is overfit-prone.
  - `book_margin_switch_to_score_min60_gap020_if_anchor_abs_book_rv15_gap<=0.1`: current +391c, v21 +91c, coverage about 99%, but the physical story is less clean because it waits for score when book/RV already agree.
  - `book_margin_switch_to_score_min60_gap020_if_anchor_adverse_move_15m>=100`: current +143c, v21 +233c, coverage about 99%, physically interpretable as path-stress, but the recent 23:00 high-adverse row would still have lost if switched to score.
- Current conclusion: do not forward-lock the pair oracle. The most plausible next forward test is a conservative session-regime switch around UTC hour 04, but only as research evidence and only if implemented causally from pre-resolution rows.
- Goal is not complete.

23:30 EDT / 03:30 UTC pending before close:

- `KXBTC15M-26MAY032330-30` is another direct regime-split row.
- Early V2/frontier/original/touch/kinetic families registered YES 51c at 2026-05-04T03:15:10Z.
- Later book/book_early/gap015 registered NO 61c at 03:16:10Z; score/score-gap/V2 waits and `book_score_gap020_wait` registered NO 61c at 03:18:11Z.
- Book NO row features: adverse_move_15m about 150c, book/RV gap 0.098. Score NO row features: adverse_move_15m about 208c, book/RV gap 0.039.
- This is the same fault line as 23:00 and 23:15: early Brownian/touch YES versus later book/score NO. If YES wins again, the current regime is clearly punishing later book-side flips. If NO wins, the flip is starting to mean-revert.
- Goal is not complete.

23:30 EDT / 03:30 UTC settlement:

- `KXBTC15M-26MAY032330-30` resolved NO.
- The later book/score NO side won. `book_margin`, `book_margin_early`, `book_margin_gap015`, score/score-gap, V2 waits, and `book_score_gap020_wait` were all NO 61c and won +37c. Early YES rows from frontier/original/touch/kinetic families at 51c lost -53c.
- Strict registered state after refresh: `book_margin` 20/20/0, 17/3, +306c; `book_margin_early` 16/16/0, 14/2, +276c; `book_margin_gap015` 10/10/0, 8/2, +130c; `score_min60` 20/20/0, 15/5, +12c; `score_min60_gap020` 9/9/0, 7/2, +16c; `book_early_score_gap020_wait` 6/6/0, 4/2, -38c; `book_score_gap020_wait` 3/3/0, 1/2, -119c; `v2_wait_score_min60_brownian70_early` 15/15/0, 12/3, +72c; `frontier_v2` 31/30/1, 19/11, -19c.
- No lock cleared promotion gates. `book_margin` remains the best strict high-coverage candidate by net P&L, but still fails both Wilson and Bayesian readiness: 85.00% accuracy, 69.70% break-even, Wilson low 63.96%, posterior P(p>BE) about 0.918, p05 edge -2.6c, needs additional perfect wins and far more sample size.
- Physics read: the 23:30 NO settlement breaks the one-way "cheap early Brownian beats later book pressure" story. The useful signal is not simply early-vs-late; it is regime-dependent. The next test should switch model families only under a concrete, predeclared market-state or session condition.
- Goal is not complete.

23:37-23:42 EDT / 03:37-03:42 UTC session-switch forward lock:

- Added research-only lock `book_hour04_v2_switch` in `logs\edge_research\profit_book_hour04_v2_switch_lock.json` with effective entry boundary `2026-05-04T03:45:00+00:00`.
- Rule: use `book_margin` as the anchor, but switch to locked `frontier_v2` when the first book-margin anchor entry is in UTC hour 04; if the anchor is missing, allow the frontier_v2 reference as a coverage fallback.
- Added validator `probe_book_v2_session_switch_forward_validation.py` and wired the new lock into the strict pending registry, denominator audit, registered-signal readiness, sample-size monitor, Bayesian EV monitor, and one-shot forward cycle.
- The supporting scan row was `book_margin_switch_to_frontier_v2_if_anchor_entry_hour_utc==04`: current +568c versus book anchor, v21 +284c, about 99% coverage on both ledgers, OOS ROI floor 7.39%. This is not promotion evidence; it is only a reason to start a clean forward trial.
- Initial compile and validation passed. Strict state is intentionally waiting: 0 registered / 0 resolved / 0 pending before the 03:45 UTC boundary.
- Goal is not complete.

23:49 EDT / 03:49 UTC strict-capture fix:

- The active 04:00 UTC market was visible in the live bot log, but the strict pending monitor initially did not register it because active-market candle physics were stale.
- Running `probe_profit_lock_pending_signal_monitor.py --fetch-btc-candles` attached current BTC path features and registered 19 pre-resolution records cleanly.
- Patched `probe_profit_lock_strict_signal_collector.py` so future collector starts default to `--fetch-btc-candles-every 1` instead of skipping network refresh. The already-running collector process was not stopped or restarted.
- Goal is not complete.

00:00-00:02 EDT / 04:00-04:02 UTC settlement and first real hour-04 switch:

- `KXBTC15M-26MAY040000-00` resolved YES.
- `book_hour04_v2_switch`, `book_margin`, `frontier_v2`, and most score/kinetic families registered YES 80c and won +18c after fee. Touch-only/touch-overlay had registered NO 53c and lost -55c.
- New strict state after refresh: `book_margin` 23 registered / 22 resolved / 1 pending, 18/4, +260c, 100% resolved and registered coverage; `book_margin_early` 19/18/1, 15/3, +230c; `book_hour04_v2_switch` 2/1/1, 1/0, +18c, 100% observed registered coverage.
- Readiness still rejects promotion. `book_margin` has 81.82% accuracy but Wilson low 61.48% vs 70.00% break-even, posterior P(p>BE) about 0.865, p05 edge -5.4c, and needs about 5 perfect wins just to clear Bayesian probability, plus much more sample. `book_hour04_v2_switch` has only one resolved row.
- First genuine switch row is now pending: `KXBTC15M-26MAY040015-15`. The session switch selected `frontier_v2` YES 58c at 04:00:45Z, while `book_margin` selected the same YES side later at 63c at 04:01:00Z. This is a clean forward test of whether hour-04 Brownian entry improves price without sacrificing coverage.
- Physics read: this is not evidence that V2 side beats book side yet; it is evidence that the session switch can causally get an earlier/cheaper entry when the first book anchor occurs in UTC hour 04. The outcome of 04:15 will determine whether that lower entry price carried real edge or merely cheaper exposure.
- Goal is not complete.

00:15-00:28 EDT / 04:15-04:28 UTC settlement, delayed validation, and reference-margin switch:

- `KXBTC15M-26MAY040015-15` resolved YES.
- The first genuine hour-04 switch row won: `book_hour04_v2_switch` selected `frontier_v2` YES 58c at 04:00:45Z and won +40c. `book_margin` selected the same YES side later at 63c and won +35c. This supports the cheaper earlier Brownian/V2 entry in this session, but it is not yet evidence for a side-switch advantage.
- Strict state after the 04:15 settlement: `book_hour04_v2_switch` 3 registered / 2 resolved / 1 pending, 2/0, +58c; `book_margin` 24/23/1, 19/4, +295c; `book_margin_early` 20/19/1, 16/3, +265c; `score_min60` 24/23/1, 17/6, +1c. No lock cleared Wilson or Bayesian promotion gates.
- The 04:30 pending market has `book_hour04_v2_switch` YES 68c via `frontier_v2`, `book_margin` YES 66c, and the delayed book rule YES 68c. Outcome is still pending at this audit point.
- Added strict validation support for `book_margin_delayed_adv100_brownian55`, including replay of the actual delayed-entry rule instead of treating it like a first-row veto. Its own lock note remains cautionary: retrospective P&L improved, but block stability failed. Live evidence is 1 pending / 0 resolved, so it is boxed as a trial only.
- Added a new research-only forward lock `book_refmargin_score_switch` with effective boundary `2026-05-04T04:30:00+00:00`. Rule: use `book_margin`, but switch to `score_min60_gap020` when the reference row's `margin_per_rv_sigma_15m <= 0.5`; if the book anchor is absent, allow the reference row for coverage.
- Supporting scan row: `book_margin_switch_to_score_min60_gap020_if_reference_margin_per_rv_sigma_15m<=0.5`, causal-class `reference_only`, current +645c vs book anchor, v21 +360c, current/v21 coverage about 99%, OOS ROI floor about 5.50%. This is not promotion evidence; it only justifies strict forward registration.
- Current physics read: the strongest live failure mode is not simply book vs Brownian, but book pressure becoming fragile when the later score/coherence reference says the RV-scaled margin is weak. This is a measurable pre-resolution state, so it is now under live trial.
- Goal is not complete.

00:30-00:32 EDT / 04:30-04:32 UTC settlement:

- `KXBTC15M-26MAY040030-30` resolved NO.
- The broad YES cluster lost. `book_margin` YES 66c lost -68c; `book_hour04_v2_switch`, `frontier_v2`, score/wait variants, and the delayed book rule were YES 68c and lost -70c.
- Updated strict state: `book_margin` 24/24/0, 19/5, +227c; `book_margin_early` 20/20/0, 16/4, +197c; `book_hour04_v2_switch` 3/3/0, 2/1, -12c; `book_margin_delayed_adv100_brownian55` 1/1/0, 0/1, -70c; `score_min60` 24/24/0, 17/7, -69c; `score_min60_gap020` 13/13/0, 9/4, -65c.
- Readiness worsened across the board. `book_margin` now has 79.17% accuracy, 69.71% break-even, Wilson low 59.53%, posterior P(p>BE) 0.815, and p05 edge -7.3c. `book_margin_early` is 80.00% accuracy but still fails Wilson/Bayesian gates. No lock clears a promotion gate.
- The delayed adverse/Brownian rule failed its first forward resolved row immediately, so it remains a low-priority diagnostic trial.
- The hour-04 session switch is no longer positive after three resolved rows. That does not disprove the underlying session hypothesis, but it removes any near-term promotion path for this lock.
- `book_refmargin_score_switch` is still waiting for its first post-04:30 UTC observed market and has 0 registered / 0 resolved.
- Physics read: the 04:30 loss reinforces that cheap or coherent YES exposure can still be wrong when the terminal move snaps opposite. Static confidence is not enough; the next useful evidence has to come from forward switches that react to instability in RV-scaled margin, not from simply choosing the earlier price.
- Goal is not complete.

00:35-00:38 EDT / 04:35-04:38 UTC capture repair and 04:45 pending:

- The bot was watching `KXBTC15M-26MAY040045-45`, but the watch line had `strike=NA`, so `heartbeat_two_side_rows` dropped the active market before physics attachment. This would have lost the first `book_refmargin_score_switch` forward row.
- Ran `probe_refresh_watched_market_metadata.py --latest 3`; the latest market metadata now has close `2026-05-04T04:45:00Z`, strike `80338.42`, status `active`. Rerunning the pending monitor with candle fetch registered 19 new pre-resolution records.
- Patched `probe_profit_lock_strict_signal_collector.py` so future collector starts run watched-market metadata refresh before pending monitors by default. A one-shot collector verification completed with failed_steps=0 and registered the path-confirmation row as well.
- Current 04:45 pending is a useful split row:
  - `book_margin`: YES 67c at 04:31:32Z, book side 0.660, Brownian 0.541, margin/RV sigma 0.104, adverse 128.81c.
  - `book_hour04_v2_switch`: NO 54c at 04:34:02Z via `frontier_v2`, Brownian 0.593, adverse 0c.
  - `book_refmargin_score_switch`: YES 69c at 04:35:03Z via `score_min60_gap020`, margin/RV sigma 0.336 <= 0.5, adverse 124.62c.
  - `book_margin_delayed_adv100_brownian55`: YES 72c at 04:36:03Z after adverse fell to 48.25c and Brownian rose to 0.673.
  - `kinetic_combo_price_guard`: YES 56c at 04:36:18Z, a cheaper late YES expression after the path calmed.
- This market is now the cleanest immediate test of the current hypotheses: book/score say YES after adverse displacement, V2 says NO from a calmer Brownian row, and kinetic combo gets a much better YES price later. Settlement will say which representation handled the path physics better.
- Goal is not complete.

00:40-00:43 EDT / 04:40-04:43 UTC refreshed regime scan:

- Reran `probe_book_v2_regime_switch_scan.py` after the 04:30 settlement.
- The leading diagnostic row is unchanged: `book_margin_switch_to_score_min60_gap020_if_side_disagree`, current/v21 delta +1274c/+381c at about 99% coverage. It remains pair-dependent and is still explanatory, not directly forward-lockable.
- The best causal-class row remains the one now under forward lock: `book_margin_switch_to_score_min60_gap020_if_reference_margin_per_rv_sigma_15m<=0.5`, current/v21 delta +645c/+360c, current all net +1773c, v21 all net +785c, current/v21 coverage about 99%, OOS ROI floor about 5.50%.
- The hour-04 V2 scan row remains positive retrospectively (+568c/+284c), but its strict live forward sample is now negative after the 04:30 loss. This is exactly why the retrospective scan cannot be promoted without live sample size.
- Goal is not complete.

00:45-00:48 EDT / 04:45-04:48 UTC settlement:

- `KXBTC15M-26MAY040045-45` resolved NO.
- The V2/early Brownian NO side won. `book_hour04_v2_switch` selected NO 54c and won +44c; `frontier_v2`, `frontier_v2_continuous`, `challenger`, `original`, `kinetic_touch`, and `kinetic_price_guard` also won on NO 54c. Touch-only NO 53c won +45c.
- The book/score/adverse-settled YES side lost. `book_margin`, `book_margin_early`, and `book_margin_gap015` were YES 67c and lost -69c; `book_refmargin_score_switch`, `score_min60`, `score_min60_gap020`, and both score waits were YES 69c and lost -71c; `book_margin_delayed_adv100_brownian55` was YES 72c and lost -74c; `kinetic_combo_price_guard` was YES 56c and lost -58c.
- Strict state after refresh: `book_margin` 25/25/0, 19/6, +158c; `book_margin_early` 21/21/0, 16/5, +128c; `book_hour04_v2_switch` 4/4/0, 3/1, +32c; `book_refmargin_score_switch` 1/1/0, 0/1, -71c; `book_margin_delayed_adv100_brownian55` 2/2/0, 0/2, -144c. No lock clears Wilson or Bayesian gates.
- Coverage read: high-coverage book locks still pass observed/resolved coverage, but their live edge has decayed hard. `book_hour04_v2_switch` is exactly at the 80% observed registered floor after missing the newly active 05:00 market at first refresh; `book_refmargin_score_switch` fails observed registered coverage at 50% until it either registers the 05:00 market or demonstrates it cannot preserve coverage.
- Physics read: this row directly rejects the first forward reference-margin score switch. The winning representation was the calmer Brownian/V2 NO row with adverse_move_15m = 0, while book/score YES rows carried adverse displacement above 120c. The live evidence is pushing toward a path-instability detector, but simple adverse filters do not preserve the required 80% trade rate and adverse-to-score switches are not robust in retrospective scan.
- Goal is not complete.

00:54-00:58 EDT / 04:54-04:58 UTC heartbeat refresh, scan refresh, and 05:00 pending:

- Refreshed `probe_live_heartbeat_two_side_fv.py --fetch-btc-candles` so the retrospective scan actually included the newly hydrated 04:45 market. Then reran `probe_book_v2_regime_switch_scan.py`.
- The best causal scan row remained `book_margin_switch_to_score_min60_gap020_if_reference_margin_per_rv_sigma_15m<=0.5`, but its current all net dropped from +1773c to +1669c and OOS ROI floor compressed from about 5.50% to about 3.59% after including the 04:45 loss. Its strict forward state is still 0/1, -71c.
- The hour-04 V2 scan row remains retrospectively positive: current/v21 delta +569c/+284c, current all net +1595c, coverage about 99%, OOS ROI floor about 7.82%. Its strict live state is 3/1, +32c, but sample is far too small and still fails promotion gates.
- The high-adverse-to-V2 idea still does not survive the scan: `book_margin_switch_to_frontier_v2_if_anchor_adverse_move_15m>=100` has current delta -111c and v21 delta +102c, so the recent 04:45 win is not enough to forward-lock it.
- Current 05:00 pending (`KXBTC15M-26MAY040100-00`) was captured pre-resolution. It is another split row:
  - `book_margin` / `book_margin_early` / `book_margin_gap015` / delayed book: YES 62c at 04:48:19Z.
  - `book_hour04_v2_switch`, `frontier_v2`, `challenger`, `original`: YES 59c at 04:48:04Z.
  - `book_refmargin_score_switch`, score/score-gap, score waits, and kinetic guards: NO 63c at 04:50:04Z.
  - Touch-only/touch-overlay: YES 53c at 04:45:18Z.
- Coverage recovered after the late registrations: `book_margin` 26/25/1, `book_margin_early` 22/21/1, `book_hour04_v2_switch` 5/4/1, `book_refmargin_score_switch` 2/1/1. No readiness gate is cleared.
- Physics read: 05:00 is now the inverse of 04:45 for the reference-margin switch. Book/V2 say YES, later score/refmargin says NO. This is the next direct test of whether the score switch is actually capturing instability or merely chasing late reversals.
- Goal is not complete.

01:00-01:11 EDT / 05:00-05:11 UTC settlement, causal refmargin correction, and 05:15 pending:

- `KXBTC15M-26MAY040100-00` resolved NO.
- The later score/refmargin NO side won. `book_refmargin_score_switch` selected NO 63c and won +35c; score/score-gap and the score-wait variants also won on the NO side. Book/V2/early/touch YES rows lost.
- Strict state after the 05:00 settlement and before 05:15 close: `book_margin` 27 registered / 26 resolved / 1 pending, 19/7, +94c; `book_margin_early` 23/22/1, 16/6, +64c; `book_hour04_v2_switch` 6/5/1, 3/2, -29c; `book_refmargin_score_switch` 3/2/1, 1/1, -36c; `book_margin_gap015` 17/16/1, 10/6, -82c. No lock clears Wilson, Bayesian, or sample-size promotion gates.
- Found and fixed an important causal-timing issue in `book_refmargin_score_switch`. The old legacy scan could use a later reference row to decide that the earlier book anchor should be kept, which is not executable. The live selector had been skipping those rows; it now falls forward to the first real book-margin-eligible row at or after the reference timestamp when the reference condition is false.
- The 05:15 market (`KXBTC15M-26MAY040115-15`) was registered pre-resolution for `book_refmargin_score_switch` at `2026-05-04T05:09:25Z`: YES 70c at `2026-05-04T05:01:05Z`, overlay `refmargin_score_switch:book_margin_after_reference`, reference margin/RV sigma 0.554 > 0.5. This preserves causality but gives up the stale earlier YES 65c price.
- Refreshed executability audit: legacy `book_refmargin_score_switch` current/v21 coverage remains about 99%, but executable delayed-anchor coverage is 284/287 current (98.95%) and 218/221 v21 (98.64%). Net drops materially from the non-executable view: current executable +1201c vs legacy +1557c; v21 executable +534c vs legacy +785c. This is still diagnostic only, not promotion evidence.
- Refreshed denominator audit: high-coverage research locks now pass the trade-rate constraint, including `book_margin`, `book_margin_early`, `book_margin_gap015`, `book_hour04_v2_switch`, `book_refmargin_score_switch`, score locks, and wait locks. Many older frontier/touch/kinetic registry families still fail registered coverage because they were not captured from the start of their observed denominator windows.
- Physics read: the 05:00 win says the weak-reference-margin switch can catch some late-state reversals, but the 04:45 loss says the same mechanism can also be late and wrong. The corrected causal timing shows the true cost: when the reference condition is false, the model cannot keep the cheap early anchor unless that anchor is still available after the reference information enters the light cone.
- Goal is not complete.

01:15-01:26 EDT / 05:15-05:26 UTC settlement, scan correction, and 05:30 pending:

- `KXBTC15M-26MAY040115-15` resolved NO.
- The whole YES cluster lost. `book_margin`, `book_margin_early`, `book_margin_gap015`, and `book_hour04_v2_switch` were YES 65c and lost -67c. `book_refmargin_score_switch`, score/score-gap, V2, waits, and kinetic rows were YES 70c and lost -72c. Touch rows were YES 60c and lost -62c.
- Strict state after settlement: `book_margin` 28 registered / 27 resolved / 1 pending, 19/8, +27c; `book_margin_early` 24/23/1, 16/7, -3c; `book_hour04_v2_switch` 7/6/1, 3/3, -96c; `book_refmargin_score_switch` 4/3/1, 1/2, -108c; `score_min60` 28/27/1, 18/9, -177c. No lock clears readiness, Wilson, Bayesian, or sample-size gates.
- The 05:30 market (`KXBTC15M-26MAY040130-30`) initially exposed a temporary coverage gap for score/refmargin while waiting for a later reference row. A later pre-resolution refresh registered the missing score-family rows: `book_refmargin_score_switch` is now NO 62c at `2026-05-04T05:19:06Z`, registered at `2026-05-04T05:20:53Z`, with reference margin/RV sigma 0.410 <= 0.5 and abs book/RV gap 0.044.
- Refreshed denominator audit after the 05:30 registrations: `book_refmargin_score_switch` recovered to 4 observed / 4 registered, 100% observed and resolved coverage. The model is preserving the trade-rate floor for the current forward window, but its strict P&L is deeply negative.
- Tightened `probe_book_v2_regime_switch_scan.py` so best causal rows must have positive delta on both current and v21 individually, not merely positive combined delta. The refreshed scan now ranks `book_margin_switch_to_frontier_v2_if_anchor_entry_hour_utc==04` as the best causal-class row: current/v21 delta +569c/+284c, coverage about 99%, OOS ROI floor 7.82%. Its strict forward sample is still only 3/3, -96c, so it remains a trial, not a candidate for promotion.
- The previously locked reference-margin scan row is no longer a robust causal-class winner under the stricter no-stale-anchor scan: `book_margin_switch_to_score_min60_gap020_if_reference_margin_per_rv_sigma_15m<=0.5` has current delta +757c but v21 delta -131c and current coverage 77.70% in the no-fallback version. The delayed-anchor executable audit is less negative across historical ledgers, but strict live evidence is now poor.
- Physics read: 05:15 says the immediate failure mode is not simply "late score beats book" or "weak reference margin means switch." The path flipped NO against every high-confidence YES representation. The next useful model needs a terminal-path instability or hazard component that can veto/flip late expensive YES exposure without dropping below the 80% recurring-market trade floor.
- Goal is not complete.

01:30-01:33 EDT / 05:30-05:33 UTC settlement and 05:45 pending:

- `KXBTC15M-26MAY040130-30` resolved NO.
- The full NO cluster won. Book/book-early/hour04 were NO 67c and won +31c; delayed book, frontier/V2, original, challenger, and kinetic rows were NO 66c and won +32c; `book_refmargin_score_switch`, score/score-gap, score waits, and V2 waits were NO 62c and won +36c; touch rows were NO 53c and won +45c.
- Strict state after refresh: `book_margin` 29 registered / 28 resolved / 1 pending, 20/8, +58c; `book_margin_early` 25/24/1, 17/7, +28c; `book_hour04_v2_switch` 8/7/1, 4/3, -65c; `book_refmargin_score_switch` 4/4/0, 2/2, -72c; `score_min60` 28/28/0, 19/9, -141c; `score_min60_gap020` 17/17/0, 11/6, -137c. No lock clears promotion gates.
- Bayesian gate read: `book_margin` is the only high-coverage trial still positive, but it is weak: 71.43% accuracy vs 69.36% break-even, Wilson low 52.94%, posterior P(p>BE) 0.552, p05 edge -13.7c, needs about 15 perfect additional wins to clear Bayesian probability and 19 to clear Wilson. This is not promotion-quality.
- The 05:45 market (`KXBTC15M-26MAY040145-45`) is now pending. Book/hour04/frontier/original/kinetic families are registered NO 66c at `2026-05-04T05:31:08Z`; touch registered earlier NO 60c at `2026-05-04T05:30:38Z`. Score/refmargin families have not registered yet, so `book_refmargin_score_switch` is exactly at 80% observed coverage for the current denominator, not above it.
- Physics read: 05:15 and 05:30 together are an alternating terminal flip pair: same broad confidence structure, opposite result one market apart. That is exactly the hard part of the objective. Static fair value is being asked to price a short-horizon stopping process; the next research step should treat the final minutes as a path/hazard problem, not just a cross-sectional probability ranking.
- Goal is not complete.

01:40-01:49 EDT / 05:40-05:49 UTC first-passage hazard forward lock:

- Refreshed `probe_profit_touch_hazard_frontier.py` after the recent live failures. The old kinetic row weakened; the best robust physics candidate became `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=touch_loss15<=0.80`.
- Historical diagnostic shape for this row: current +887c, 75.00% accuracy, 94.77% coverage, 4.55% ROI; v21 +804c, 75.00% accuracy, 92.31% coverage, 5.55% ROI. Minimum OOS ROI was thin but positive, about 0.10%.
- Created `logs/edge_research/profit_hazard_mean_touch80_fresh_lock.json` and wired `hazard_mean_touch80` into `probe_profit_lock_pending_signal_monitor.py`, denominator audit, readiness, Wilson sample-size, Bayesian EV, registry divergence, strict failure attribution, and forward-cycle command lists.
- Effective boundary is `2026-05-04T05:45:00Z`, not 05:30, because the lock was created while the 05:45 market was already open. This preserves strict causality: first possible resolved strict market is 06:00.
- Initial readiness before 06:00: `hazard_mean_touch80` had one pre-close pending row, NO 69c at `2026-05-04T05:48:09Z` for `KXBTC15M-26MAY040200-00`.
- Goal is not complete.

01:45-02:03 EDT / 05:45-06:03 UTC settlement, blend audit, and second forward lock:

- `KXBTC15M-26MAY040145-45` resolved YES. The registered NO cluster lost: `book_margin` NO 66c lost -68c; `book_refmargin_score_switch` and `score_min60` NO 69c lost -71c; touch NO 60c lost -62c.
- `KXBTC15M-26MAY040200-00` resolved NO. Book/score/hazard-mean NO rows won: `book_margin` NO 61c won +37c; `book_refmargin_score_switch` and `score_min60` NO 69c won +29c; `hazard_mean_touch80` won its first strict row at +29c. Touch-only was on YES 51c and lost -53c.
- Current registered readiness after refresh: `book_margin` 30/30/0, 21/9, +27c, 96.77% observed coverage, Wilson low 52.12% vs 69.10% break-even; `book_refmargin_score_switch` 6/6/0, 3/3, -114c; `score_min60` 30/30/0, 20/10, -183c; `hazard_mean_touch80` 1/1/0, 1/0, +29c but only 50% observed coverage because it did not select the open 06:15 denominator. No lock clears readiness, Wilson, Bayesian, or sample-size gates.
- Added and ran `probe_physics_probability_blend_audit.py`. It tests small fixed blends of book terminal probability, realized-vol Brownian terminal probability, first-passage/touch survival, and disagreement penalties. The EV floor is selected on train splits only, then evaluated on validation/holdout.
- Blend audit result: no train-selected blend clears positive validation/holdout P&L on both datasets at strict high coverage. However, three diagnostic strict-80 rows are positive across current and v21 validation/holdout; strongest is `logit_book_rv_hazard_mean` at edge floor -10c, combined all-ledger +1020c, current +232c at 99.31% coverage, v21 +788c at 99.10% coverage. This is diagnostic only because the row was visible after scanning OOS splits.
- Created `logs/edge_research/profit_logit_blend_edge10_fresh_lock.json` for a forward-only trial of `blend_logit_book_rv_hazard_mean` with fair edge >= -10c, ask <= 95c, seconds_to_close >= 60. Effective boundary is `2026-05-04T06:00:00Z`; it correctly did not claim the 06:00 market.
- Wired `logit_blend_edge10` into the pending monitor, denominator audit, readiness, Wilson sample-size, Bayesian EV, registry divergence, strict failure attribution, and forward-cycle command lists. It registered the first strict pending row for `KXBTC15M-26MAY040215-15`: YES 47c at `2026-05-04T06:01:10Z`, score 0.4595, fair edge -3.05c, registered at `2026-05-04T06:01:49Z`.
- After refreshing the two-sided heartbeat ledger to 33,724 physics rows, the diagnostic blend edge weakened but survived: `logit_book_rv_hazard_mean` at -10c now shows current +123c at 99.32% coverage and v21 +788c at 99.10% coverage. Fresh strict sample remains 0 resolved / 1 pending, so the lock remains evidence-seeking only.
- Physics read: raw Brownian terminal confidence is still failing as a fair value. The two forward trials now separate two ideas: (1) a stricter first-passage hazard selector that may be profitable but risks sub-80% coverage, and (2) a near-universal logit-pooled book/RV/hazard fair value that preserves coverage but must prove the retrospective OOS row was not an accident.
- Goal is not complete.

02:11-02:18 EDT / 06:11-06:18 UTC 06:15 split settlement and gate refresh:

- The 06:15 market (`KXBTC15M-26MAY040215-15`) was a clean live split. `logit_blend_edge10`, `frontier_v2`, and touch-only chose YES early; book/refmargin/score/hazard-mean chose NO later.
- It resolved NO. Book/refmargin/score/hazard-mean won; logit/V2/touch lost. Key rows: `book_margin` NO 64c +34c; `book_refmargin_score_switch` NO 64c +34c; `hazard_mean_touch80` NO 64c +34c; `logit_blend_edge10` YES 47c -49c; `frontier_v2` YES 47c -49c; `touch_hazard` YES 60c -62c.
- 06:30 pending (`KXBTC15M-26MAY040230-30`) is now registered. Most major locks are on NO. `hazard_mean_touch80` is NO 79c at `2026-05-04T06:15:26Z`, score 0.5798. `logit_blend_edge10` is NO 74c at `2026-05-04T06:15:56Z`, score 0.6648, fair edge -9.52c.
- Readiness after refresh: `book_margin` 32 registered / 31 resolved / 1 pending, 22/9, +61c, 100% coverage, Wilson low 53.41% vs 69.00% break-even; `book_refmargin_score_switch` 8/7/1, 4/3, -80c; `score_min60` 32/31/1, 21/10, -149c; `hazard_mean_touch80` 3/2/1, 2/0, +63c; `logit_blend_edge10` 2/1/1, 0/1, -49c. No Wilson, Bayesian, or sample-size gate is ready.
- Bayesian read: `book_margin` posterior P(p>BE) 0.554, p05 edge -12.98c; `hazard_mean_touch80` P(p>BE) 0.679, p05 edge -31.66c; `logit_blend_edge10` P(p>BE) 0.260, p05 edge -46.50c. These are still tiny samples, not promotion evidence.
- Physics read: the first live logit-blend test failed specifically because the logit pool trusted early Brownian/V2 YES against later book/hazard NO. Hazard-mean passed the split and preserved coverage on the next market. The immediate priority is to keep collecting hazard-mean rows and watch whether its apparent edge survives once it faces a loss; the logit blend remains useful as a high-coverage falsification trial.
- Goal is not complete.

02:19-02:25 EDT / 06:19-06:25 UTC thresholded logit-blend trial:

- Added `probe_logit_blend_threshold_frontier.py` to test whether the logit book/RV/hazard blend needs an explicit minimum physical-probability floor. This directly targets the 06:15 failure where the unthresholded logit lock bought cheap YES 47c even though its physical score was only 0.4595.
- Threshold scan result: strict positive OOS diagnostic rows exist. Best row: `blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; sec>=60`, current +1053c at 98.97% coverage and 74.05% accuracy, v21 +553c at 98.64% coverage and 72.94% accuracy, min OOS coverage 97.78%. It is diagnostic only because the scan sees validation/holdout.
- Created `logs/edge_research/profit_logit_blend_thresh55_edge15_fresh_lock.json` and `probe_logit_blend_thresh55_edge15_fresh_validation.py`. Also patched the `blend_edge` pending-monitor kind to respect `policy.min_score`; the older `logit_blend_edge10` has min_score 0.0 and is unchanged.
- Wired `logit_blend_thresh55_edge15` into the pending monitor, denominator audit, readiness, sample-size, Bayesian EV, registry divergence, strict failure attribution, and forward-cycle command list.
- Effective boundary is `2026-05-04T06:30:00Z`, so it correctly cannot claim the already-open 06:30 market. Current denominator/readiness state is waiting: 0 observed, 0 registered. First possible strict market is 06:45.
- Physics read: this is a cleaner forward test of the idea that cheap price is not enough; the physical state estimate itself must be above a confidence floor. If it holds coverage live, it is a more defensible fair-value candidate than the unthresholded logit edge trial.
- Goal is not complete.

02:30-02:34 EDT / 06:30-06:34 UTC 06:30 settlement and coverage pressure:

- `KXBTC15M-26MAY040230-30` resolved NO. The NO cluster won again: `book_margin` NO 79c +19c; `book_refmargin_score_switch` NO 79c +19c; `hazard_mean_touch80` NO 79c +19c; `logit_blend_edge10` NO 74c +24c; score/min and touch also won NO.
- Registered readiness after refresh: `book_margin` 33/32/1, 23/9, +80c, 100% coverage; `book_refmargin_score_switch` 8/8/0, 5/3, -61c; `hazard_mean_touch80` 3/3/0, 3/0, +82c; `logit_blend_edge10` 3/2/1, 1/1, -25c; `logit_blend_thresh55_edge15` 0/0/0 waiting.
- `hazard_mean_touch80` now has the attractive accuracy/EV start but fails observed coverage: 3 registered over 4 observed post-boundary markets = 75%, below the 80% recurring-market target. It skipped the open 06:45 market. Resolved coverage remains 100%, but the observed denominator matters because the user explicitly wants to trade at least 80% of new BTC 15m markets.
- `logit_blend_edge10` preserved 100% observed/resolved coverage and has one pending 06:45 row, but its forward P&L is still negative after the first loss.
- `logit_blend_thresh55_edge15` correctly stayed inactive for 06:45 because the logit blend score was only about 0.45, below its 0.55 physical-confidence floor. That protects it from the previous cheap-low-probability failure mode, but it starts with 0/1 observed coverage until a qualifying market appears. This is a coverage risk to monitor.
- Physics read: hazard-mean is currently the best accuracy/EV trial but violates the coverage requirement on observed markets; unthresholded logit preserves coverage but is weaker; thresholded logit is physically cleaner but may be too selective. The next model iteration should try to keep hazard's side choice while using a fallback for low-hazard markets so coverage stays above 80%.
- Goal is not complete.

02:35-02:40 EDT / 06:35-06:40 UTC hazard-primary fallback model:

- Added `probe_hazard_fallback_frontier.py` to test a hybrid architecture: use `hazard_mean_touch80` when it fires, otherwise fall back to a high-coverage fair-value prior.
- Best diagnostic row: `hazard_primary_else_logit_thresh55_edge15`, current +1037c at 98.97% coverage and 75.43% accuracy, v21 +922c at 98.64% coverage and 75.69% accuracy, min OOS coverage 97.78%. It is diagnostic only because the scan sees validation/holdout.
- Created `logs/edge_research/profit_hazard_fallback_logit55_fresh_lock.json` and `probe_hazard_fallback_logit55_fresh_validation.py`. Wired `hazard_fallback_logit55` into the pending monitor, denominator audit, readiness, sample-size, Bayesian EV, registry divergence, strict failure attribution, and forward-cycle command list.
- Patched the pending monitor with a new `hazard_fallback` kind. It first selects hazard rows; for markets hazard skips, it selects the thresholded logit fallback row if eligible. The lock was created during the 06:45 market, so effective boundary is `2026-05-04T06:45:00Z`; first strict market is 07:00.
- A later pre-close row repaired the immediate 06:45 coverage picture for the component trials: `hazard_mean_touch80` registered YES 71c at `2026-05-04T06:33:13Z`; `logit_blend_thresh55_edge15` also registered YES 71c at the same row with blend score 0.6156 and fair edge -11.44c. Unthresholded logit remains on the earlier cheap YES 48c row.
- Current formal state: `hazard_mean_touch80` is 4 registered / 3 resolved / 1 pending, 3/0, +82c, 100% observed coverage; `logit_blend_thresh55_edge15` is 1 registered / 0 resolved / 1 pending, 100% observed coverage; `hazard_fallback_logit55` is waiting with 0 observed because its boundary begins after 06:45.
- Physics read: the fallback architecture is the most coherent current candidate because it explicitly decomposes the target into a path-hazard primary model plus a coverage-preserving fair-value fallback. It still needs live evidence from 07:00 onward before it can be trusted.
- Goal is not complete.

02:45-02:51 EDT / 06:45-06:51 UTC 06:45 settlement and first hazard-fallback pending:

- `KXBTC15M-26MAY040245-45` resolved YES. The YES cluster won: `book_margin` YES 62c +36c; `book_refmargin_score_switch` YES 71c +27c; `hazard_mean_touch80` YES 71c +27c; `logit_blend_edge10` YES 48c +50c; `logit_blend_thresh55_edge15` YES 71c +27c; touch YES 48c +50c.
- Registered readiness after refresh: `book_margin` 34/33/1, 24/9, +116c; `hazard_mean_touch80` 5/4/1, 4/0, +109c; `logit_blend_edge10` 4/3/1, 2/1, +25c; `logit_blend_thresh55_edge15` 2/1/1, 1/0, +27c; `hazard_fallback_logit55` 1/0/1, waiting for first resolved row. No lock is promotion-ready.
- Bayesian read: `hazard_mean_touch80` posterior P(p>BE) 0.795 but p05 edge is still -17.82c because n=4; `book_margin` P(p>BE) 0.631; `logit_blend_edge10` P(p>BE) 0.553. Tiny-sample uncertainty remains large.
- First strict `hazard_fallback_logit55` pending row is `KXBTC15M-26MAY040300-00`: YES 75c at `2026-05-04T06:46:14Z`, on the primary hazard branch with hazard score 0.5929 and logit blend 0.6886. `hazard_mean_touch80`, `logit_blend_edge10`, and `logit_blend_thresh55_edge15` all also selected YES 75c at that row; touch-only selected YES 71c earlier.
- Coverage read: all current physics trials being watched are at 100% observed coverage after the later 07:00 registration, including `hazard_mean_touch80`, `logit_blend_edge10`, `logit_blend_thresh55_edge15`, and `hazard_fallback_logit55`.
- Physics read: the hazard-primary branch is now doing exactly what it was designed to do: when path/touch survival is high enough, it takes the high-confidence hazard side and does not need fallback. The important future test is the first market where hazard skips but fallback fires; that will decide whether the hybrid really solves the coverage problem without importing the unthresholded logit's low-probability errors.
- Goal is not complete.

02:51-02:53 EDT / 06:51-06:53 UTC refreshed diagnostics after 06:45:

- Refreshed the two-sided heartbeat ledger to 34,076 physics rows and reran the focused physics scans.
- `hazard_fallback_frontier_latest` strengthened: best row remains `hazard_primary_else_logit_thresh55_edge15`, now current +1113c at 98.98% coverage and 75.68% accuracy, v21 +922c at 98.64% coverage and 75.69% accuracy, combined +2035c, min OOS coverage 97.78%.
- `logit_blend_threshold_frontier_latest` also still has strict positive OOS rows. The monitored thresholded-logit family remains robust diagnostically; the best threshold row by combined net is now `blend>=0.55; fair_edge>=-10c`, but the already locked `blend>=0.55; fair_edge>=-15c` remains positive and high coverage.
- `physics_probability_blend_audit_latest` still says no train-selected blend clears positive validation/holdout P&L on both datasets, but diagnostic strict-80 blend rows remain. This keeps the epistemic status clear: the most useful rows are forward-test candidates, not completed evidence.
- Physics read: the hybrid remains the most promising architecture because it is the only one explicitly built to satisfy both constraints at once: path-aware accuracy via hazard and market coverage via thresholded fallback.
- Goal is not complete.

03:00-03:05 EDT / 07:00-07:05 UTC first resolved hazard-fallback row:

- `KXBTC15M-26MAY040300-00` resolved YES. All monitored physics trials were aligned YES and won: `book_margin` YES 75c +23c; `hazard_mean_touch80` YES 75c +23c; `hazard_fallback_logit55` YES 75c +23c on the primary hazard branch; `logit_blend_edge10` YES 75c +23c; `logit_blend_thresh55_edge15` YES 75c +23c; touch-only YES 71c +27c.
- 07:15 pending (`KXBTC15M-26MAY040315-15`) is aligned NO across the monitored physics trials. `hazard_fallback_logit55` is again on the primary hazard branch: NO 72c at `2026-05-04T07:00:31Z`, hazard score 0.4556.
- Registered readiness after refresh: `book_margin` 35/34/1, 25/9, +139c; `hazard_mean_touch80` 6/5/1, 5/0, +132c; `logit_blend_edge10` 5/4/1, 3/1, +48c; `logit_blend_thresh55_edge15` 3/2/1, 2/0, +50c; `hazard_fallback_logit55` 2/1/1, 1/0, +23c. All have 100% observed coverage in their current forward windows.
- Bayesian read: `hazard_mean_touch80` posterior P(p>BE) is now 0.842 with p05 edge -12.95c, still below readiness because n=5; `book_margin` P(p>BE) 0.664; `hazard_fallback_logit55` P(p>BE) 0.407 because its first win was expensive at 75c and sample size is 1.
- Physics read: the live evidence is increasingly favorable to the hazard branch, but it is still an all-win streak with very small n. The hybrid has not yet exercised its fallback branch live; until that happens, the claimed coverage solution is only structurally verified, not empirically stress-tested.
- Goal is not complete.

03:15-03:20 EDT / 07:15-07:20 UTC low-threshold hazard test and first fallback-branch pending:

- `KXBTC15M-26MAY040315-15` resolved NO. The low-threshold hazard row won: `hazard_mean_touch80` NO 72c +26c with hazard score 0.4556. `hazard_fallback_logit55` also won on the primary hazard branch, NO 72c +26c. Book/refmargin/score/logit/touch NO rows all won as well.
- 07:30 pending (`KXBTC15M-26MAY040330-30`) is the first live fallback-branch test for the hybrid. `hazard_fallback_logit55` selected YES 64c at `2026-05-04T07:16:02Z` via fallback `blend_logit_book_rv_hazard_mean`, blend score 0.5673, fair edge -9.27c. `hazard_mean_touch80` did not register this market, so its observed coverage is 6/7 = 85.71%, still above the 80% floor.
- Readiness after refresh: `book_margin` 36/35/1, 26/9, +165c; `hazard_mean_touch80` 6/6/0, 6/0, +158c; `logit_blend_edge10` 6/5/1, 4/1, +75c; `logit_blend_thresh55_edge15` 4/3/1, 3/0, +76c; `hazard_fallback_logit55` 3/2/1, 2/0, +49c. No promotion gate is ready.
- Bayesian read: `hazard_mean_touch80` P(p>BE) 0.884, p05 edge -8.32c; `book_margin` P(p>BE) 0.694; `hazard_fallback_logit55` P(p>BE) 0.568 because its two wins are expensive and sample size is tiny.
- Physics read: the hazard primary is surviving even near its lower threshold, which is a good sign. The 07:30 fallback row is now the important one: it will tell us whether the hybrid can add coverage without reintroducing the cheap-low-probability failure mode that hurt the unthresholded logit trial.
- Goal is not complete.

03:30-03:36 EDT / 07:30-07:36 UTC fallback branch failure:

- `KXBTC15M-26MAY040330-30` resolved NO. The fallback branch failed: `hazard_fallback_logit55` selected YES 64c via fallback and lost -66c. `logit_blend_thresh55_edge15`, score/refmargin, book, and unthresholded logit also lost on YES.
- Pure `hazard_mean_touch80` fired later on the opposite side and won: NO 69c at `2026-05-04T07:21:48Z`, hazard score 0.4529, +29c. This is the key causal fact: the fallback was too early, and a later hazard row corrected the side.
- Formal state after refresh: `hazard_mean_touch80` 7/7/0, 7/0, +187c, 87.50% observed coverage, 100% resolved coverage; `logit_blend_edge10` 7/6/1, 4/2, +21c; `logit_blend_thresh55_edge15` 4/4/0, 3/1, +10c; `hazard_fallback_logit55` 3/3/0, 2/1, -17c and 75% observed coverage. No lock is promotion-ready.
- Bayesian read: `hazard_mean_touch80` posterior P(p>BE) is now 0.916 and p05 edge -4.52c, still not ready but materially closer. It needs about 4 more perfect wins for Wilson-over-break-even. The hybrid's posterior deteriorated to P(p>BE) 0.306.
- Coverage read: pure hazard remains above the 80% observed floor at 7/8 = 87.5%; thresholded logit is exactly 80%; hybrid is below the floor at 3/4 = 75% because it missed the open 07:45 market.
- Physics read: fallback cannot be immediate. If fallback is used at all, it needs a delay/light-cone rule that gives hazard time to form. The current live evidence favors pure hazard over the hybrid until a delayed fallback is separately tested.
- Goal is not complete.

03:36-03:40 EDT / 07:36-07:40 UTC delayed fallback lock:

- Added the delayed-fallback hypothesis as a separate forward test after the 07:30 failure. The lock is `logs/edge_research/profit_hazard_fallback_logit55_wait8_fresh_lock.json`; it was created at `2026-05-04T07:36:01Z` from `hazard_fallback_frontier_latest`.
- Locked policy: primary remains `hazard_discounted_mean_15>=0.45; ask<=80; sec>=60; touch_loss15<=0.80`. Fallback is `blend_logit_book_rv_hazard_mean>=0.55; fair_edge>=-15c; ask<=95; 60<=sec<=480`. The new `sec<=480` cap is the important change: fallback can only fire inside the final 8 minutes, giving the hazard primary a chance to form first.
- Diagnostic scan row: current +1016c at 97.97% coverage and 75.43% accuracy; v21 +912c at 96.83% coverage and 75.70% accuracy; minimum OOS coverage 96.61%. This is still diagnostic only because it was selected after seeing validation/holdout.
- Effective boundary is `2026-05-04T07:45:00Z`; therefore the trial correctly has 0 registered, 0 resolved, and 0 pending rows before that boundary. The first strict resolved market can only be 08:00 UTC or later.
- Current formal denominator state: `hazard_mean_touch80` is 8 registered / 7 resolved / 1 pending with 100% observed coverage in its forward window; `hazard_fallback_logit55_wait8` is waiting with no observed denominator yet.
- Physics read: the 07:30 failure was not just "blend bad"; it exposed timing as a physical variable. A fallback that acts too early can buy before the path has enough causal information. The delayed fallback is the next falsification trial, while pure hazard remains the live leader.
- Goal is not complete.

03:43-03:46 EDT / 07:43-07:46 UTC causal arbitration audit and score fallback lock:

- Added `probe_hazard_fallback_causal_frontier.py` after finding that the earlier offline hybrid scan was optimistic: it let a later hazard signal suppress an earlier fallback signal inside the same market. That is not a physically tradable first-signal rule.
- The causal scan chooses the earliest eligible primary/fallback row by timestamp, with hazard only winning exact ties. This matches the pre-resolution registry concept better than the previous noncausal scan.
- Result: the delayed logit fallback still survives under causal arbitration, but with less edge. `logit_thresh55_edge15_wait8m` falls to combined +1761c and has a +167c old-scan optimism gap. Immediate logit has a larger +364c optimism gap. The best causal row is `hazard_primary_else_score_min60`, combined +1964c, current +1268c at 98.98% coverage, v21 +696c at 99.10% coverage, and strict positive OOS.
- Patched `probe_profit_lock_pending_signal_monitor.py` so future `hazard_fallback` registrations are timestamp-causal. Existing registry rows remain immutable; this only changes future first-signal selection.
- Created `logs/edge_research/profit_hazard_fallback_score60_fresh_lock.json` and `probe_hazard_fallback_score60_fresh_validation.py`. The score60 fallback lock uses the same hazard primary, otherwise `score_min_book_rv15>=0.60; ask<=95; sec>=60`. Effective boundary is `2026-05-04T08:00:00Z`, so its first strict resolved market can only be 08:15 UTC or later.
- Physics read: this is a stricter version of the hybrid idea. If hazard is the path/first-passage model, the fallback should be a conservative terminal prior, not a hindsight-selected replacement for a future hazard state. The score-min fallback is now a forward falsification trial, not promotion evidence.
- Goal is not complete.

03:49-03:53 EDT / 07:49-07:53 UTC 07:45 settlement and forward-cycle refresh:

- `KXBTC15M-26MAY040345-45` resolved NO. The hazard cluster won again: `hazard_mean_touch80` NO 65c at `2026-05-04T07:34:04Z`, +33c. `book_margin`, `hazard_fallback_logit55`, and `logit_blend_thresh55_edge15` also won NO 65c. The unthresholded `logit_blend_edge10` bought early YES 50c and lost -52c.
- Formal registered state after the forward cycle: `hazard_mean_touch80` is 9 registered / 8 resolved / 1 pending, 8/0, +220c, 100% registered and resolved coverage. Posterior P(p>break-even) is 0.944, p05 edge -0.8c, still below the Bayesian gate and still below the minimum sample-size gate.
- `hazard_fallback_logit55_wait8` now has its first strict pending row for `KXBTC15M-26MAY040400-00`: YES 61c at `2026-05-04T07:45:35Z`. It is on the primary hazard branch, not fallback, with hazard score 0.5075. Pure hazard and the immediate hybrid selected the same pending YES 61c row.
- `hazard_fallback_score60` is correctly waiting with 0 observed denominator because its effective boundary is 08:00 UTC. First strict resolved market is 08:15 UTC or later.
- Other monitored physics trials: `logit_blend_thresh55_edge15` is 4/1, +43c; immediate `hazard_fallback_logit55` is 3/1, +16c; unthresholded `logit_blend_edge10` deteriorated to 4/3, -31c after the 07:45 early-YES loss.
- Physics read: the live tape is strongly favoring the hazard primary. The repeated pattern is that early cheap/logit rows can be on the wrong side before the path has matured, while the hazard row waits for first-passage/touch information and has been correcting toward the winning side. This is still a tiny all-win sample, so no promotion is justified.
- Goal is not complete.

04:00-04:05 EDT / 08:00-08:05 UTC first hazard loss and primary-maturity scan:

- `KXBTC15M-26MAY040400-00` resolved NO. The hazard cluster lost: `hazard_mean_touch80` selected YES 61c at `2026-05-04T07:45:35Z`, hazard score 0.5075, and lost -63c. `book_margin`, `logit_blend_edge10`, `logit_blend_thresh55_edge15`, immediate `hazard_fallback_logit55`, and delayed `hazard_fallback_logit55_wait8` were also on YES and lost.
- Formal state after refresh: `hazard_mean_touch80` is now 9/9/0, 8/1, +157c, 88.89% accuracy, 90.00% registered coverage, 100% resolved coverage. It remains above the user's 80% trade-rate floor, but posterior P(p>break-even) fell from ~0.944 to 0.826 and p05 edge fell to -10.8c. No promotion gate is ready.
- `hazard_fallback_logit55_wait8` failed its first strict resolved row because the primary hazard branch fired early on the same losing YES 61c. It is 0/1, -63c, and only 50% registered observed coverage after missing the open 08:15 market. The delay cap only affects fallback, not the primary, so it did not protect against an immature primary signal.
- `hazard_fallback_score60` has 0 registered rows and missed its first observed post-boundary market (`KXBTC15M-26MAY040415-15`), so it is coverage-weak until proven otherwise. It cannot be treated as a coverage solution yet.
- Added `probe_hazard_primary_maturity_frontier.py` to test whether the primary hazard signal itself should wait for elapsed market time. The live loss had 864 seconds still to close, so this directly tests the "immature light cone" hypothesis.
- Maturity scan result: strict positive OOS rows exist, but the best diagnostic remains `primary=no_cap; fallback=score_min_book_rv15>=0.60`, combined +1964c, current +1268c at 98.98% coverage, v21 +696c at 99.10% coverage. A 30-second primary wait is nearly identical (+1961c). Heavier waits reduce combined edge, and wait-only pure hazard variants do not clearly improve the historical physics.
- Physics read: the first hazard loss is a real warning, but not enough to justify tightening the primary based on one row. Historically, elapsed-time caps are not a free lunch. The live-forward read is now: pure hazard remains the leader but no longer has a near-ready posterior; wait8 is damaged; score60 fallback is still unproven and may fail coverage. The next evidence target is whether hazard's first loss is isolated noise or the start of a repeated early-entry failure mode.
- Goal is not complete.

04:08-04:17 EDT / 08:08-08:17 UTC 08:15 late-hazard failure:

- Mid-market refresh registered late 08:15 signals. `hazard_mean_touch80` fired NO 79c at `2026-05-04T08:06:07Z`, hazard score 0.6935, with 532.6 seconds left. `hazard_fallback_logit55_wait8` took the same primary-hazard NO 79c. `hazard_fallback_score60`, `score_min60`, `logit_blend_thresh55_edge15`, and immediate `hazard_fallback_logit55` took earlier NO 86c at `2026-05-04T08:05:07Z`. Unthresholded `logit_blend_edge10` stayed on early YES 50c.
- `KXBTC15M-26MAY040415-15` resolved YES. The late hazard/score/logit-threshold cluster lost; unthresholded logit won the cheap YES 50c; book-margin YES 74c also won.
- Formal state after refresh: `hazard_mean_touch80` 10/10/0, 8/2, +76c, 80.00% accuracy, 90.91% registered coverage, 100% resolved coverage. Posterior P(p>break-even) fell to 0.624 and p05 edge to -19.5c. It is no longer near any promotion gate.
- `hazard_fallback_logit55` is now 3/3, -134c. `hazard_fallback_logit55_wait8` is 0/2, -144c. `hazard_fallback_score60` is 0/1, -87c. These hybrid trials are failing live so far despite attractive retrospective diagnostics.
- `book_margin` recovered somewhat: 28/11, +93c, 97.50% registered coverage, but posterior P(p>break-even) is only 0.591 and Wilson low is 56.22%, so it is also not ready.
- Physics read: 08:15 falsifies the simple "late hazard correction is enough" story. The market can keep moving through the barrier after hazard flips, and high hazard confidence at expensive prices can still be wrong. The only defensible conclusion is that no current physics candidate is promotion-ready; pure hazard remains useful as a research signal, but the next model must distinguish late path confirmation from late overreaction.
- Goal is not complete.

04:19-04:20 EDT / 08:19-08:20 UTC 08:30 pending state:

- Reports were refreshed after a background/current registry write captured `KXBTC15M-26MAY040430-30`. Pending rows: `hazard_mean_touch80` NO 72c at `2026-05-04T08:17:08Z`, hazard score 0.4767; `hazard_fallback_logit55`, `hazard_fallback_logit55_wait8`, and `hazard_fallback_score60` all take the same primary-hazard NO 72c. `logit_blend_thresh55_edge15` also takes NO 72c; unthresholded `logit_blend_edge10` took earlier NO 52c at `2026-05-04T08:15:23Z`.
- Current registered readiness before 08:30 settlement: `hazard_mean_touch80` 11 registered / 10 resolved / 1 pending, 8/2, +76c, 100% registered coverage, posterior P(p>break-even) 0.624. `book_margin` is 40/39/1, 28/11, +93c, 100% registered coverage, P(p>break-even) 0.591. No lock clears Wilson or Bayesian gates.
- Physics read: the model is now in a real stress regime. The hazard side is still getting coverage and still has positive net, but two consecutive losses sharply reduce confidence. The 08:30 pending row is another test of whether the recent late-hazard NO flips are signal or overreaction.
- Goal is not complete.

04:22-04:23 EDT / 08:22-08:23 UTC overreaction-cap scan:

- Added `probe_hazard_overreaction_frontier.py` to test whether recent losses are caused by hazard overreaction: high score, high price, or high normalized margin after an extended move.
- Result: the base hazard policy remains the best strict positive OOS row: combined +1720c, current +916c at 94.92% coverage, v21 +804c at 92.31% coverage, min OOS coverage 88.89%.
- `ask<=75` and related caps look tempting in combined P&L (`ask<=75` +1952c; `ask<=75 & margin<=0.75` +2007c), but they fail the strict 80% OOS coverage gate by a small amount: min OOS coverage 79.55% or 77.27%. Because the user explicitly wants at least 80% of BTC 15m markets, these remain diagnostic only and were not forward-locked.
- Physics read: the overreaction hypothesis is real enough to watch, but the first strict scan does not support replacing the base hazard rule. The correct move is to continue forward evidence collection, not carve out a near-miss filter after two losses.
- Goal is not complete.

04:33-04:34 EDT / 08:33-08:34 UTC 08:30 settlement:

- `KXBTC15M-26MAY040430-30` resolved NO. The hazard/book/logit-threshold cluster won: `hazard_mean_touch80` NO 72c at `2026-05-04T08:17:08Z`, +26c; `book_margin` NO 72c +26c; `logit_blend_thresh55_edge15` NO 72c +26c; unthresholded `logit_blend_edge10` NO 52c +46c.
- Pure hazard recovered to 11 registered / 11 resolved / 0 pending, 9/2, +102c, 81.82% accuracy, 100% registered coverage. Posterior P(p>break-even) is 0.682 with p05 edge -16.2c. Still not close to promotion.
- `hazard_fallback_logit55_wait8` and `hazard_fallback_score60` both won this row through the primary hazard branch, but their live records remain weak: wait8 is 1/2, -118c; score60 is 1/1, -61c.
- New 08:45 pending state: pure hazard has not fired yet. `hazard_fallback_logit55` has a fallback NO 66c at `2026-05-04T08:31:24Z`; `book_margin` has NO 65c; `logit_blend_thresh55_edge15` has NO 66c; unthresholded logit has NO 60c. This is another test of whether fallback/thresholded models can trade when pure hazard skips.
- Physics read: 08:30 says the recent stress regime is not simple collapse; hazard can still be right. But the live evidence is now ordinary noisy edge, not a breakthrough. The next useful distinction is whether fallback trades in hazard-skip markets add coverage profitably or keep importing losses.
- Goal is not complete.

04:47-04:48 EDT / 08:47-08:48 UTC 08:45 settlement:

- `KXBTC15M-26MAY040445-45` resolved NO. What first looked like a pure hazard skip became a late hazard-primary win: `hazard_mean_touch80` fired NO 66c at `2026-05-04T08:35:10Z`, hazard score 0.4596, and won +32c.
- `book_margin` won earlier NO 65c (+33c). `logit_blend_edge10` won early NO 60c (+38c). `logit_blend_thresh55_edge15` and immediate `hazard_fallback_logit55` won fallback/thresholded NO 66c (+32c). `hazard_fallback_logit55_wait8` and `hazard_fallback_score60` also won on the later primary-hazard NO 66c.
- Formal state after refresh: `hazard_mean_touch80` 12/12/0, 10/2, +134c, 83.33% accuracy, 92.31% registered coverage, posterior P(p>break-even) 0.747, p05 edge -13.2c. Coverage is healthy again, but statistical proof is still weak.
- `book_margin` is 30/11, +152c, 97.62% registered coverage, P(p>break-even) 0.665. It is a stable baseline but still not gate-ready. `logit_blend_edge10` recovered to 7/4, +38c but has weak posterior; thresholded logit remains negative.
- New 09:00 pending state: pure hazard has not fired yet; unthresholded logit has NO 49c at `2026-05-04T08:46:56Z`. The denominator audit currently marks `KXBTC15M-26MAY040500-00` as the missing observed market for hazard and most thresholded candidates.
- Physics read: base hazard recovered because the low-threshold late signal was right this time. The pattern after 08:00 is not "late hazard bad"; it is "late hazard noisy, especially when expensive/high-confidence." The model still needs a way to price path confirmation strength against reversal risk without losing the 80% market target.
- Goal is not complete.

05:03-05:12 EDT / 09:03-09:12 UTC 09:00 settlement, registry-source audit, and granular price-cap scan:

- `KXBTC15M-26MAY040500-00` resolved NO. Pure hazard fired NO 59c at `2026-05-04T08:49:11Z`, hazard score 0.4934, and won +39c. `book_margin` won NO 72c (+26c), `logit_blend_edge10` won earlier NO 49c (+49c), and score/min fallback-style rows won at later higher prices.
- Formal state after the 09:00 refresh: `hazard_mean_touch80` was 14 registered / 13 resolved / 1 pending, 11/2, +173c, 100% resolved coverage, posterior P(p>break-even) 0.812, p05 edge -9.9c. No lock cleared Wilson or Bayesian readiness.
- Added `probe_profit_lock_registry_fresh_validation.py` because the recompute validators were stale: `live_heartbeat_two_side_fv_ledger_latest.csv` only reached close `2026-05-04T06:45:00Z`, while the registered-signal registry had resolved rows through `2026-05-04T09:00:00Z` and pending rows through `09:15`. This makes registered-signal readiness the source of truth for forward evidence until the raw two-sided ledger catches up.
- Added `probe_hazard_pricecap_granular_frontier.py` to scan the 73c-80c hazard price-cap band instead of guessing at 75c. Best strict diagnostic row was `hazard>=0.45; ask<=76; sec>=60; touch_loss<=0.80`: combined historical +2129c, current +899c at 91.53% coverage, v21 +1230c at 88.24% coverage, min OOS coverage 81.82%. Live post-hoc on registered hazard rows was 10/1, +235c, 84.62% resolved coverage.
- Created research-only forward lock `logs/edge_research/profit_hazard_mean_touch80_ask76_fresh_lock.json`. It was created at `2026-05-04T09:12:51Z`, with `lock_close_dt=2026-05-04T09:00:00Z`; the effective forward boundary is `2026-05-04T09:15:00Z`. This means the seen 09:15 market cannot count for it.
- Physics read: the 09:00 win supports the idea that low/mid-priced hazard can still be useful. The granular scan says the overreaction cap may be around 76c rather than 75c/80c, but this is only a forward falsification candidate because the cap was selected after seeing some live outcomes.
- Goal is not complete.

05:16-05:19 EDT / 09:16-09:19 UTC 09:15 settlement and ask76 boundary check:

- `KXBTC15M-26MAY040515-15` resolved YES. The current hazard/book/logit cluster was short NO and lost: `hazard_mean_touch80` NO 71c -73c, `hazard_fallback_score60` NO 71c -73c, `logit_blend_thresh55_edge15` NO 71c -73c, `logit_blend_edge10` NO 68c -70c, and `book_margin` NO 66c -68c.
- The ask76 forward lock correctly did not register this market. Its denominator row is waiting with effective boundary `2026-05-04T09:15:00Z`, observed post-lock markets 1, resolved 0, registered 0. No backfill or leakage occurred.
- Formal state after 09:15: `hazard_mean_touch80` is 14/14/0, 11/3, +100c, 78.57% accuracy, 93.33% registered observed coverage, posterior P(p>break-even) 0.662, p05 edge -15.2c. `book_margin` is 43 resolved, 31/12, +110c, P(p>BE) ~0.610. `logit_blend_edge10` is 8/5, +17c with one 09:30 pending. All are not ready.
- `hazard_fallback_score60` deteriorated to 3/2, -63c; the score-min fallback branch itself remains 0/1, -87c, while hazard-primary rows inside that lock are 3/1, +24c. The fallback idea remains live-negative.
- New 09:30 pending rows after the refresh were `logit_blend_edge10` YES 48c and touch/touch-overlay YES 54c. No `hazard_mean_touch80` or `hazard_mean_touch80_ask76` signal had formed yet.
- Physics read: 09:15 weakens the simple overreaction story because 71c was inside the new 76c cap and still lost. The price cap may remove the worst expensive certainty trades, but it does not solve reversal risk by itself. The next model pressure point is path persistence/side stability after the hazard trigger, not just price.
- Goal is not complete.

05:21-05:22 EDT / 09:21-09:22 UTC trigger-persistence falsification:

- Added `probe_hazard_trigger_persistence_frontier.py` to test whether a hazard trigger should require same-side persistence for 15/30/60/120 seconds before entry.
- Result: persistence does not solve the physics. Strict positive OOS rows are only the zero-delay baselines. `ask<=76; persist>=0s` remains best with combined +2129c and min OOS coverage 81.82%. Adding 15s or 30s persistence cuts v21 coverage to about 60% and fails strict coverage; 60s/120s persistence turns combined P&L negative.
- Physics read: the data does not support "wait after the hazard trigger" as the next model. The signal is a first-passage state, and delaying it throws away too much of the state information. The better forward hypothesis remains first hazard row with a price/overreaction cap, now locked as ask<=76, while accepting that some inside-cap reversals are irreducible noise unless a different state variable is found.
- Goal is not complete.

05:25-05:28 EDT / 09:25-09:28 UTC source-cadence correction:

- Refreshed `probe_live_heartbeat_two_side_fv.py --fetch-btc-candles`, bringing the two-sided physics ledger to 35,242 rows and resolved close `2026-05-04T09:15:00Z`.
- Reran the registry-first validator. Source freshness is now clean: raw recompute ledger max resolved close and registered registry max resolved close both equal `2026-05-04T09:15:00Z`.
- Reran hazard fresh validators. Recompute validators now see post-lock fresh samples (`hazard_mean_touch80` fresh 14/14), but the divergence audit shows why promotion must still use immutable registry rows: for `KXBTC15M-26MAY040415-15`, recompute selected an earlier YES 74c winner, while the actual pre-registered monitor row was later NO 79c loser. Net recompute-minus-registry delta for `hazard_mean_touch80` is +101c.
- Instrumentation read: the strict collector is running, but its command line fetches BTC candles every 5 iterations. In fast 15m markets, stale candle/physics state can alter which row is first eligible. I am not stopping or restarting that process; for this workstream, manual `--fetch-btc-candles` refreshes and the registry/recompute divergence audit are now mandatory before interpreting fresh metrics.
- Goal is not complete.

05:31-05:34 EDT / 09:31-09:34 UTC 09:30 settlement and first ask76 forward pending:

- `KXBTC15M-26MAY040530-30` resolved YES. The non-hazard rows won: `book_margin` YES 62c +36c, `logit_blend_edge10` YES 48c +50c, `touch_hazard`/`touch_overlay` YES 54c +44c, and `hazard_fallback_score60` won via fallback score-min YES 61c +37c. Pure hazard did not register that market.
- The first true `hazard_mean_touch80_ask76` forward row is now pending for `KXBTC15M-26MAY040545-45`: NO 74c at `2026-05-04T09:31:00Z`, hazard score 0.5562, 839.95 seconds to close. Pure hazard and `hazard_fallback_score60` also selected this same pending primary-hazard row.
- Formal ask76 denominator after the refresh: effective boundary `2026-05-04T09:15:00Z`, observed post-lock markets 2, resolved 1, unclosed 1, registered 1 pending and 0 resolved. Registered observed coverage is 50% because it skipped the 09:30 market. This is too young to reject, but it must recover above 80% if it is going to satisfy the user constraint.
- `book_margin` improved to 32/12, +146c, P(p>BE) 0.651, still not ready. `hazard_mean_touch80` remains 11/3, +100c with one pending, P(p>BE) 0.662. `logit_blend_edge10` improved to 9/5, +67c with one pending. No lock is promotion-ready.
- Physics read: 09:30 is evidence that fallback/cheap models can add useful coverage in a hazard-skip market, but the broader fallback records remain weak. The ask76 cap is now in its first real forward trial; the 09:45 settlement will be the first resolved test.
- Goal is not complete.

05:45-05:47 EDT / 09:45-09:47 UTC first ask76 forward loss:

- `KXBTC15M-26MAY040545-45` resolved YES. The first true `hazard_mean_touch80_ask76` forward row lost: NO 74c at `2026-05-04T09:31:00Z`, -76c. Pure hazard, score60 hybrid primary, unthresholded logit, thresholded logit, book, and touch rows were also NO and lost.
- Formal ask76 state: 1 registered / 1 resolved / 0 pending, 0/1, -76c. Coverage is also weak: 1 registered out of 3 observed post-boundary markets, 33.33% observed coverage and 50% resolved coverage. This is not enough sample to fully reject, but it is a bad first forward result and fails the user's 80% coverage target so far.
- Pure hazard deteriorated to 15/15/0, 11/4, +24c, 73.33% accuracy, registered observed coverage 88.24%, posterior P(p>BE) 0.490. The edge is no longer compelling live.
- `book_margin` fell to 32/13, +79c, P(p>BE) 0.568. `logit_blend_edge10` fell to 9/6, -9c with one 10:00 pending. `hazard_fallback_score60` fell to 4/3, -102c. No model is ready.
- New 10:00 pending rows are cheap non-hazard/touch/logit style NO 53c rows; no pure hazard or ask76 signal has formed for that market, further pressuring the hazard coverage story.
- Physics read: the ask76 price cap is not enough. The 09:45 loss is inside the cap and resembles the 09:15 loss: moderate/high book confidence on NO, then terminal reversal to YES. Current evidence says path/touch hazard is a useful feature, but not a standalone fair value model. The next model needs a reversal/regime variable or must lean harder on broad cheap-book/logit coverage while controlling the fallback failure mode.
- Goal is not complete.

05:49-05:56 EDT / 09:49-09:56 UTC maturity retest and ledger refresh:

- Reran `probe_hazard_primary_maturity_frontier.py` after the 09:45 loss. The simple maturity/wait hypothesis is still rejected: the strongest rows remain no-wait/no-cap or score60 fallback diagnostics, while wait/window variants do not robustly improve current and v21 out-of-sample behavior at the required coverage.
- Refreshed `probe_live_heartbeat_two_side_fv.py --fetch-btc-candles`; the two-sided physics ledger increased to 35,474 physics rows, 307 unique markets with physics, and candle coverage through `2026-05-04T09:53:59.999Z`. This brought the resolved physics ledger through the 09:45 market for historical scans.
- Physics read: live failures show earlier signals lose more often, but a crude clock wait does not generalize. The failure mode is not "early is bad"; it is "fresh directional displacement can be mistaken for stable terminal distance."
- Goal is not complete.

05:56-06:06 EDT / 09:56-10:06 UTC impulse-over-margin reversal scan and forward lock:

- Added `probe_impulse_reversal_regime_frontier.py` to test a new physics state: favorable 3-5 minute impulse larger than the remaining side-specific distance to strike. The two recent reversal losses had this signature: the selected NO side's 3-5 minute favorable move exceeded its remaining margin.
- Strict scan result: 0 strict-pass rows. The hypothesis explains recent failures, but the simple veto/fade overlays do not clear current+v21 coverage, positive all-split/OOS, and block-stability gates simultaneously.
- Best diagnostic row was `book_margin` plus fade of extreme impulse state: `impulse_3_5m>=60`, `impulse_3_5m-margin>=20`, `sec>=600`, `margin_sigma<=0.75`, `score<=0.82`, opposite ask<=45. It kept about 99% coverage and scored combined historical +4141c versus +1376c for the book-margin baseline, but it failed block stability with min positive block rate 0.667 versus the 0.70 floor. Therefore it is not promotion evidence.
- Created research-only forward lock `logs/edge_research/profit_impulse_reversal_book_margin_fade_fresh_lock.json`. It was created at `2026-05-04T10:05:32Z`, with discovery through the 09:45 market; strict effective boundary is the next full 15m close, `2026-05-04T10:15:00Z`. No already-open 10:00 market can count.
- Patched the research registry to support the new `impulse_reversal_book_margin_fade` lock and to retain impulse audit fields (`margin_dollars`, `signed_move_3m`, `signed_move_5m`, `impulse_3_5m`, `impulse_3_5m_over_margin`) for future forward rows.
- Physics read: this is the first candidate that directly attacks the observed reversal mechanism while preserving broad coverage. Because it fails stability, it must be judged only by future registered rows.
- Goal is not complete.

06:06-06:11 EDT / 10:06-10:11 UTC 10:00 settlement refresh:

- `KXBTC15M-26MAY040600-00` resolved NO. The cheap non-hazard cluster won: `book_margin` NO 62c +36c, `frontier_v2`/`logit_blend_edge10` NO 53c +45c, and touch rows NO 53c +45c. Pure hazard also later fired NO 77c and won +21c; ask76 fired NO 71c and won +27c.
- Formal state after refresh: `book_margin` 46/46/0, 33/13, +115c, 71.74% accuracy, 100% resolved coverage, posterior P(p>BE)=0.612, p05 edge -9.6c. This is still the best broad live baseline, but not statistically ready.
- `hazard_mean_touch80` recovered to 16/16/0, 12/4, +45c, 75.00% accuracy, 94.12% resolved coverage, P(p>BE)=0.532, p05 edge -18.2c. Still not ready.
- `hazard_mean_touch80_ask76` is now 2/2/0, 1/1, -49c, 66.67% resolved coverage and 50.00% observed coverage. The 10:00 win helped, but coverage remains below the user target and posterior evidence is poor.
- `logit_blend_edge10` improved to 17 registered / 16 resolved / 1 pending, 10/6, +36c, 100% resolved coverage, P(p>BE)=0.541. Still not ready.
- New `impulse_reversal_book_margin_fade` row is waiting with 0 observed/0 resolved because its effective boundary is `2026-05-04T10:15:00Z`.
- Source audit: registry has resolved rows through `2026-05-04T10:00:00Z` and pending through `10:15`, while the raw recompute ledger still resolves only through `09:45`; registered-signal readiness remains the source of truth.
- Physics read: 10:00 shows the broad cheap book/logit side is resilient, but its edge remains thin. Hazard remains a volatile feature, not a promotable model. The next forward evidence should watch whether impulse-fade can preserve book coverage while improving the bad early-reversal blocks.
- Goal is not complete.

06:15-06:18 EDT / 10:15-10:18 UTC first impulse-reversal forward registration:

- Ran `probe_profit_lock_pending_signal_monitor.py --fetch-btc-candles` after the strict boundary. It registered 10 new research rows and added the first `impulse_reversal_book_margin_fade` row for `KXBTC15M-26MAY040630-30`.
- The impulse challenger selected the base side, not a fade: NO 62c at `2026-05-04T10:16:04Z`, 835.876 seconds to close, book score 0.615, margin $53.91, `impulse_3_5m=36.36`, `impulse_3_5m_over_margin=-17.55`, overlay `book_margin_base`. This is exactly what the rule should do when the fresh impulse is smaller than the remaining distance-to-strike.
- `KXBTC15M-26MAY040615-15` resolved NO. Broad book/hazard rows mostly won: `book_margin` NO 65c +33c, `hazard_mean_touch80` NO 78c +20c, and ask-expensive score/hazard rows won. Early YES rows from `frontier_v2`, `frontier_v2_continuous`, `logit_blend_edge10`, `original`, and raw `touch_hazard` lost.
- Updated registered readiness: `book_margin` 48 registered / 47 resolved / 1 pending, 34/13, +148c, P(p>BE)=0.650, p05 edge -8.8c; `hazard_mean_touch80` 17/17/0, 13/4, +65c, P(p>BE)=0.573; `logit_blend_edge10` fell to 10/7, -13c with one pending; `hazard_mean_touch80_ask76` remains 1/1 over 2 resolved, -49c and only 50% resolved coverage.
- New impulse-fade denominator: observed 1, resolved 0, unclosed 1, registered 1. Coverage is mechanically 100% so far, but with no resolved evidence yet.
- Physics read: the first impulse-forward row is a sanity check, not evidence. The rule did not over-trigger; it stayed with book when there was no impulse-over-margin overhang. The important next event is the 10:30 settlement.
- Goal is not complete.

06:30-06:33 EDT / 10:30-10:33 UTC first impulse-reversal settlement:

- `KXBTC15M-26MAY040630-30` resolved NO. The first `impulse_reversal_book_margin_fade` forward row won: base NO 62c, +36c. This validates the registration path and the non-fade branch, but it is only 1 resolved sample and does not test the actual fade branch.
- `book_margin` also won the same row and improved to 48/48/0, 35/13, +184c, 72.92% accuracy, P(p>BE)=0.690, p05 edge -7.9c. It remains the strongest broad live baseline but still does not clear posterior or Wilson proof.
- `hazard_mean_touch80` won NO 74c and improved to 18/18/0, 14/4, +89c, P(p>BE)=0.619. `hazard_mean_touch80_ask76` also won NO 74c and is now 3/3/0, 2/1, -25c, but coverage remains only 60% resolved and 50% observed.
- `logit_blend_edge10` lost a YES 50c row and fell to 10/8, -65c. This weakens the cheap-logit recovery story.
- New 10:45 pending rows are only `touch_hazard`/`touch_overlay` YES 50c. The impulse-reversal lock has not registered 10:45 yet, so its denominator is 2 observed / 1 resolved / 1 unclosed, registered 1. Coverage is not acceptable yet, but the current 10:45 market can still become eligible later before close.
- Physics read: the first impulse result says the base book component is still useful when impulse is not overextended. The real question remains whether the model can keep >=80% coverage and whether the fade branch improves the reversal blocks; neither is proven.
- Goal is not complete.

06:34-06:39 EDT / 10:34-10:39 UTC first true impulse-fade pending:

- Reran the pending monitor during the 10:45 market. The `impulse_reversal_book_margin_fade` lock registered its first actual fade-branch trade for `KXBTC15M-26MAY040645-45`: selected NO 21c at `2026-05-04T10:32:06Z`, overlay `fade_impulse_3_5m_abs60_over20`.
- Trigger audit: the faded state was an expensive YES trigger, ask 80c, book score 0.795, trigger margin $0.11, trigger `impulse_3_5m=268.09`, trigger `impulse_3_5m_over_margin=267.98`. That is the intended physics: a huge favorable 3-5 minute impulse with almost no terminal distance cushion, so the model buys cheap opposite NO rather than chasing YES.
- Patched `probe_profit_lock_pending_signal_monitor.py` so future fade rows retain explicit trigger-side fields: `fade_trigger_side`, `fade_trigger_ask_cents`, `fade_trigger_score_value`, `fade_trigger_margin_dollars`, `fade_trigger_impulse_3_5m`, and `fade_trigger_impulse_3_5m_over_margin`. The current pending fade row was backfilled with those fields.
- Formal impulse lock state: 2 registered / 1 resolved / 1 pending, 1/0, +36c, 100% registered and resolved coverage. Sample is tiny and not promotion evidence.
- Physics read: this is the first clean live test of the new reversal physics. It is exactly the kind of market the rule was invented for; the 10:45 settlement will be the first meaningful fade-branch verdict.
- Goal is not complete.

06:45-06:48 EDT / 10:45-10:48 UTC first fade-branch failure:

- `KXBTC15M-26MAY040645-45` resolved YES. The first true `impulse_reversal_book_margin_fade` fade row lost: selected NO 21c against an 80c YES trigger, -23c. The lock is now 2/2/0, 1/1, +13c overall only because the earlier base-book row won.
- This is immediate caution on the new physics. The trigger had the intended overextension signature (`fade_trigger_impulse_3_5m_over_margin=267.98`), but the impulse continued into settlement rather than mean reverting.
- Most non-fade rows in this market won by staying with YES, including `book_margin` YES 80c +18c and several later YES 93c rows +6c. `touch_hazard`/`touch_overlay` also won earlier YES 50c +48c. The failed fade was the contrarian outlier.
- Formal state after refresh: `book_margin` 49/49/0, 36/13, +202c, 73.47% accuracy, P(p>BE)=0.709, p05 edge -7.5c. `hazard_mean_touch80` remains 18/18/0, 14/4, +89c, 90% resolved coverage. `hazard_mean_touch80_ask76` is 3/3/0, 2/1, -25c, 50% resolved coverage. `logit_blend_edge10` is 19/19/0, 11/8, -59c.
- `impulse_reversal_book_margin_fade` has registered coverage of 2/3 observed post-lock markets (66.67%) because the new 11:00 market is observed and unclosed with no impulse row yet. This is below target until it registers later or future markets recover.
- Physics read: the first actual fade says the overreaction signal is not sufficient by itself. It may still be a useful low-price convex branch, but it cannot be trusted without more forward rows. For now, the broad book baseline remains better than the invented reversal overlay.
- Goal is not complete.

06:49-06:52 EDT / 10:49-10:52 UTC impulse side-asymmetry falsification:

- Added `probe_impulse_fade_side_asymmetry_frontier.py` to test whether the failed fade could be repaired by a small physics grid: fade only YES triggers, fade only NO triggers, require trigger absolute margin >=10/25/50, and cap trigger ask at 70/76/80/90/100.
- Result: 0 strict-pass rows. Several side/margin variants are historically profitable at high coverage, but none clear current+v21 positive all-split/OOS plus block-stability gates.
- Best diagnostic row was `fade_trigger_side=any; trigger_abs_margin>=10; trigger_ask<=76`, combined +2265c and combined OOS +1659c at 97.78% min split coverage, but min positive block rate was only 0.667 with worst block -411c. This is not enough to forward-lock a replacement.
- Side restriction did not honestly fix the issue. YES-trigger-only rows often rank higher than NO-trigger-only rows historically, even though the first live YES fade failed. NO-trigger-only rows have weaker v21 behavior and worse block stability. The data says the impulse fade branch is unstable, not merely wrong-sided.
- Physics read: fading fresh impulse is too blunt. Some impulses are exhaustion, some are breakout continuation, and the current features do not separate them robustly. Do not create a second impulse lock from this scan.
- Goal is not complete.

09:29-10:24 EDT / 13:29-14:24 UTC p80 terminal-book audit and touch-conflict falsification:

- Added `probe_book_p80_failure_physics_audit.py` to inspect the high-confidence book hypothesis directly. Historical p80 edge is real but thin: current data shows 302 selected / 317 observed, 260/42, +179c, 86.09% accuracy versus roughly 85.50% fee-aware break-even; v21 shows 192 selected / 221 observed, 170/22, +299c, 88.54% accuracy versus roughly 86.98% break-even.
- Price is the core physics problem. These are high-priced contracts, so one loss costs multiple wins. The audit shows ask>=85 and ask>=90 regions are not obviously safer despite higher book confidence; they often have worse or negative net in split diagnostics because the edge margin above break-even is tiny.
- Added `probe_p80_touch_conflict_frontier.py` and `probe_touch_book_conflict_frontier.py` to test whether earlier opposite touch/hazard signals should preempt later p80/book confidence. Both scans produced 0 strict-pass rows.
- The p80 touch-conflict scan ranked baseline p80 policies above the touch-preempt variants: `p80_ask90_sec0_baseline` had combined +465c, combined OOS +299c, min split coverage 81.82%, current/v21 +117c/+348c, but only 0.500 positive block rate and worst block -210c. `p80_ask95_sec120_baseline` had combined +343c, combined OOS +244c, min split coverage 84.09%, current/v21 +44c/+299c, 0.538 positive block rate, and worst block -240c. These are hypothesis rows, not promotion rows.
- Created two research-only p80 locks, `profit_book_p80_profit_frontier_fresh_lock.json` and `profit_book_p80_ask90_frontier_fresh_lock.json`, and patched the registry/readiness/audit scripts to track them as immutable forward signals.
- Physics read: p80 is not failing because touch always sees the "true" path first. The real issue is a very narrow high-price edge under terminal uncertainty. The model needs to know when book confidence is expressing genuine terminal distance and when it is just expensive continuation risk.
- Goal is not complete.

10:45-10:57 EDT / 14:45-14:57 UTC p80 live settlement, refreshed gates, and current goal state:

- Refreshed `probe_live_heartbeat_two_side_fv.py --fetch-btc-candles`; the two-sided source is now fresh through resolved close `2026-05-04T14:45:00Z` with 37,266 physics rows. Reran the pending monitor, registered readiness, denominator audit, fresh validation, Bayesian EV, sample-size requirements, key policy registry/recompute audit, and strict failure attribution.
- Source freshness is clean again: raw recompute source stale is `False`; raw recompute max resolved close and registry max resolved close both equal `2026-05-04T14:45:00Z`, with registry pending through `2026-05-04T15:00:00Z`.
- `KXBTC15M-26MAY041045-45` resolved YES. Broad book and p80 won: `book_margin` YES 63c +35c, `book_p80_ask90_frontier` YES 84c +15c, `book_p80_profit_frontier` YES 84c +15c, and `hazard_mean_touch80` YES 66c +32c. `touch_hazard` was opposite-side NO 56c and lost -58c. This directly prevents a one-way "touch beats p80" conclusion.
- Latest registered readiness: `book_margin` is 61 registered / 60 resolved / 1 pending, 43/17, +163c, 71.67% accuracy, 98.36% resolved coverage, posterior P(p>BE)=0.651, p05 edge -7.8c. It remains the best broad live baseline, but it still fails Wilson and Bayesian promotion gates.
- Latest p80 locks: `book_p80_ask90_frontier` is 5/4/1, 3/1, -36c, 100% coverage, P(p>BE)=0.184, p05 edge -49.7c. `book_p80_profit_frontier` is 6/5/1, 3/2, -120c, 100% coverage, P(p>BE)=0.055, p05 edge -56.9c. Coverage is excellent, but early registered EV is negative and the posterior is weak.
- Other key live locks: `hazard_mean_touch80` is 30/29/1, 22/7, +106c, 90.62% resolved coverage, P(p>BE)=0.623, p05 edge -11.5c. `hazard_mean_touch80_ask76` is 15/14/1, 10/4, +4c, but only 77.78% resolved coverage, below the user's 80% recurring-market floor. `impulse_reversal_book_margin_fade` is 14/13/1, 4/9, -234c, so the fade hypothesis is rejected live for now.
- Sample-size gate remains far away. `book_margin` would need about 22 additional perfect selected wins to clear Wilson over break-even and 17 to clear the Bayesian probability gate from the current state. `book_p80_ask90_frontier` needs about 28 Wilson-perfect wins and 23 Bayesian-perfect wins; `book_p80_profit_frontier` needs about 37 and 32.
- Registry/recompute audit still warns against retrospective confidence. `book_margin` is 43/17 +163c in registered rows versus 228/93 +1071c in recompute; `score_min60` is 42/18 -154c in registry versus 242/78 +1305c in recompute; p80 policies are also materially better in recompute than in pre-resolution registry. Promotion must use the immutable registry.
- Physics read: the current most useful direction is not another price cap or one-off touch veto. The live evidence says BTC 15m markets are switching between continuation and exhaustion regimes, and simple path features can explain failures after the fact without trading them reliably. The next defensible model should preserve broad book-margin coverage while classifying terminal-distance quality: distance-to-strike, velocity/acceleration, time-to-close, touch history, and order-book confidence should be treated as a state transition problem, not independent filters.
- Goal is not complete.

11:00-11:10 EDT / 15:00-15:10 UTC 11:00 settlement and clean refresh:

- After the 11:00 close, refreshed the pending registry and raw heartbeat source again. The final clean validation pass has raw recompute and registry both resolved through `2026-05-04T15:00:00Z`, with registry pending through `2026-05-04T15:15:00Z`; `raw_recompute_source_stale=False`.
- `KXBTC15M-26MAY041100-00` resolved YES. Broad book, hazard, touch, and p80 all aligned on YES and won. `book_margin` selected YES 77c at `2026-05-04T14:46:11.739Z` for +21c. `book_p80_ask90_frontier` and `book_p80_profit_frontier` selected YES 81c at `2026-05-04T14:47:26.989Z` for +17c each. `hazard_mean_touch80_ask76` selected YES 75c and won +23c. Touch selected earlier YES 57c and won +41c.
- The same market gave another live rejection for the impulse fade branch. `impulse_reversal_book_margin_fade` selected cheap opposite NO 24c on the fade overlay and lost -26c while the continuation side settled YES. This reinforces that a large recent impulse is not enough to call exhaustion.
- Latest registered readiness after 11:00: `book_margin` is 62 registered / 61 resolved / 1 pending, 44/17, +184c, 72.13% accuracy, 98.39% resolved coverage, P(p>BE)=0.669, p05 edge -7.4c. Still not Wilson/Bayes ready.
- Latest p80 state improved but remains negative: `book_p80_ask90_frontier` is 6/5/1, 4/1, -19c, 100% coverage, P(p>BE)=0.252, p05 edge -42.1c. `book_p80_profit_frontier` is 7/6/1, 4/2, -103c, 100% coverage, P(p>BE)=0.089, p05 edge -49.5c.
- `hazard_mean_touch80` is 31/30/1, 23/7, +127c, 90.91% resolved coverage, P(p>BE)=0.652. `hazard_mean_touch80_ask76` improved to 16/15/1, 11/4, +27c, but resolved coverage is still 78.95%, just below the 80% recurring-market floor.
- Sample-size proof remains distant. From the current state, `book_margin` needs about 21 additional perfect wins for the Wilson gate and 17 for the Bayesian probability gate. `book_p80_ask90_frontier` needs about 26 Wilson-perfect wins and 22 Bayesian-perfect wins; `book_p80_profit_frontier` needs about 35 and 30.
- Physics read: 11:00 is a clean continuation market, not an exhaustion market. The useful signal is that book, hazard, p80, and touch can all agree and win, while contrarian impulse-fade gets punished. The unresolved hard problem remains distinguishing this continuation regime from the earlier reversal/exhaustion failures without sacrificing the user's >=80% market coverage target.
- Goal is not complete.

11:30-11:45 EDT / 15:30-15:45 UTC continuation/exhaustion state scans:

- Added `probe_continuation_exhaustion_state_frontier.py` to test the next physics hypothesis: preserve broad book-margin coverage, reprice with earlier same-side touch when path/book agree, and/or veto opposite-touch conflict rather than fade it.
- Result: 41 rows scanned, 0 strict-pass rows. The top diagnostic `same-side touch reprice; touch>=0.4; touch_ask<=60; touch_age<=300s` had combined all-ledger +4472c, combined OOS +1994c, current/v21 +2586c/+1886c, 97.78% min split coverage, and positive all current/v21 OOS splits, but failed block stability with min positive block rate 0.688 versus the 0.70 floor and worst block -288c.
- Important correction: that top repricing row is not directly tradable as written. It uses later book confirmation to select an earlier same-side touch row, so it contains intra-market hindsight. It is useful physics because it says earlier path/book agreement can carry price advantage, but it cannot be forward-locked in that form.
- Added `probe_causal_touch_book_state_frontier.py` to remove that hindsight. The causal rule can trade touch only when touch/book alignment already exists at that row; otherwise it falls back to broad book-margin.
- Causal scan result: 49 rows scanned, 0 strict-pass rows. The best causal rows (`touch>=0.55; touch_ask<=60/65; book_at_touch>=0.55`) improved combined all-ledger net to +1732c versus +1376c baseline and combined OOS to +758c versus +697c, while keeping 97.78% min split coverage. They still failed block stability with min positive block rate 0.625 and worst block -332c.
- Physics read: the attractive same-side touch effect mostly weakens once causality is enforced. Touch/book alignment can modestly improve the broad book baseline, but it is too sparse and block-unstable to promote or even forward-lock as a primary candidate. Opposite-touch veto is also not enough. The continuation/exhaustion distinction remains real, but the current touch/book features do not solve it under the 80% market-coverage constraint.
- Goal is not complete.

11:47-11:55 EDT / 15:47-15:55 UTC 11:15-11:45 settlement damage:

- Refreshed the pending registry and raw heartbeat source again after the 11:15, 11:30, and 11:45 markets resolved. Clean freshness state: raw recompute and registered registry are both resolved through `2026-05-04T15:45:00Z`, with registry pending through `2026-05-04T16:00:00Z`; `raw_recompute_source_stale=False`.
- The last three settlements materially damaged the broad live baselines. `book_margin` moved from 44/17 +184c to 44/20 -23c. `hazard_mean_touch80` moved from 23/7 +127c to 24/9 -3c. `book_p80_ask90_frontier` moved to 8 registered / 7 resolved / 1 pending, 5/2, -87c. `book_p80_profit_frontier` moved to 10/9/1, 6/3, -167c.
- `KXBTC15M-26MAY041115-15` resolved NO. Early broad book was wrong: `book_margin` YES 61c lost -63c. Later path/book rows corrected to NO and won: touch NO 58c +40c, score/hazard NO 70c +28c, and p80 NO 83c +16c. Physics read: an early book edge can be a transient pre-correction state.
- `KXBTC15M-26MAY041130-30` resolved NO. Here broad consensus was wrong: `book_margin`, `hazard_mean_touch80`, `score_min60`, and touch all selected YES 76c and lost -78c. `book_p80_profit_frontier` later selected NO 95c and won only +4c; `book_p80_ask90_frontier` did not qualify because the useful p80 row was too expensive for the ask90 cap. The impulse-fade branch selected NO 25c and won +73c, but this is not enough to rescue its overall live record.
- `KXBTC15M-26MAY041145-45` resolved YES. Broad book, p80, hazard, score, logit, and touch were all short NO and lost. `book_margin` NO 64c lost -66c, p80 NO 83c lost -84c, hazard NO 78c lost -80c, ask76 NO 76c lost -78c, and touch NO 53c lost -55c. The impulse-fade branch selected YES 38c and won +60c, again showing it can catch some reversal markets while still being negative overall.
- Formal state after refresh: no registered lock is positive enough or statistically ready. `book_margin` is 65/64/1, 44/20, -23c, 98.46% resolved coverage, P(p>BE)=0.449, p05 edge -10.6c. `hazard_mean_touch80` is 34/33/1, 24/9, -3c, 91.67% coverage, P(p>BE)=0.449. `hazard_mean_touch80_ask76` now clears resolved coverage at 81.82%, but is 12/6, -101c. `impulse_reversal_book_margin_fade` is 18/17/1, 6/11, -190c.
- Sample-size proof got farther away. `book_margin` now needs about 30 perfect selected wins just to clear Wilson over break-even from the current fresh state. `book_p80_ask90_frontier` needs about 34; `book_p80_profit_frontier` needs about 47.
- Registry/recompute divergence remains large: `book_margin` is 44/20 -23c registered versus 229/96 +885c recomputed; `score_min60` is 44/20 -263c registered versus 244/80 +1187c recomputed. This reinforces that recompute-only improvements are not promotion evidence.
- Physics read: the last three markets are the clearest warning so far. Sometimes later path confirmation corrects early book; sometimes all path/book/touch consensus is still wrong; sometimes the contrarian impulse branch works, but not reliably enough. The underlying state is not a simple continuation/exhaustion binary with the current features. No live-trading promotion is defensible.
- Goal is not complete.

12:05-12:18 EDT / 16:05-16:18 UTC current live v28 bot audit:

- Pivoted from broad shadow locks to the actual live `live_mushroom_v28_size2` engine, because the live bot is modestly profitable even while the broad registered fair-value locks are not promotion-ready.
- Refreshed `score_bot_log.py` in live-only mode for `live_mushroom_v28_size2`: 209 entries, 175 completed round trips, 33 confirmed wins, 1 confirmed settled loss, 0 open positions, and net P&L of $6.33 on $373.67 cost basis (+1.694%). The scorer saw 329 resolved and 5 unresolved recurring markets.
- The current live v28 bot filled only 138 of 329 resolved recurring markets, or 41.95% recurring-market coverage. This is not the user's >=80% BTC 15m recurring-market solution; this strand is a current-live-engine improvement audit, separate from the broader coverage goal.
- Added `probe_live_v28_current_bot_loss_guard.py`. Best strict retrospective guard is `edge_cents>=2.1 AND eligible_depth<=1300`: 181 retained trades, 86.60% trade retention, 89.86% filled-market retention, net $10.77 versus $6.33 baseline, 15 fewer negative trades, and train/validation/holdout net $4.75/$5.82/$0.20. It is not live-promotable because it is retrospective and still only 37.69% recurring-market coverage.
- The cleaner physics cue is `btc_age_ms<=600`: 199 retained trades, 95.22% trade retention, 95.65% filled-market retention, net $9.19 (+$2.86 versus baseline), and all splits nonnegative. This points at stale BTC spot/tick state as a plausible v28 entry weakness.
- Added `probe_live_v28_exit_value_audit.py`. The current exit engine is the main reason the live bot works modestly: 149 matched resolved exits had actual exit net $-6.76 versus $-23.29 if held to settlement, adding $16.53 of value. `mushroom_v28_exit_value_over_hold` added $13.96, `mushroom_v28_probability_reduce` added $3.83, and `mushroom_v28_probability_collapse_full` lost $1.26 versus holding.
- Forward-registered a research-only high-sigma exit suppression monitor in `live_v28_exit_sigma_suppress_shadow_lock.json`: `suppress_exit_if_sigma_t_dollars>=100`, effective from `2026-05-04T16:30:00+00:00`. `probe_live_v28_exit_suppress_shadow_monitor.py` currently has 0 registered rows because the boundary is future-facing.
- Operational note: the 12:15 market entered NO at 89c, attempted a 100c exit that was rejected, then cleared nonzero internal position state after settlement grace. The scorer counts it as a settled win. This is an execution-state edge case for later audit, not current evidence of P&L failure.
- Physics read: live v28 appears to work less because its raw entries are extraordinary and more because its exit engine cuts the left tail. The best next target is the one exit branch with negative hold-relative value, `mushroom_v28_probability_collapse_full`, while keeping all work research-only until forward evidence exists.
- Goal is not complete. No live bot logic, processes, or orders were changed.

12:24-12:27 EDT / 16:24-16:27 UTC collapse-exit branch drilldown:

- Refreshed the live-only v28 score again: 210 entries, 175 completed round trips, 1 open position, 33 confirmed wins, 1 confirmed settled loss, net P&L still $6.33 on $375.29 cost basis (+1.687%). The scorer now has 333 resolved and 1 unresolved recurring markets. Current v28 filled-market coverage is 139/333 = 41.74%, still far below the broad >=80% recurring-market objective.
- Refreshed `probe_live_v28_exit_value_audit.py`: 153 matched resolved exits, actual exit net $-6.52 versus $-21.69 if held, so the exit engine is still adding $15.17. `exit_value_over_hold` is now 63 exits and +$13.34 versus holding; `probability_reduce` remains +$3.83; `probability_collapse_full` worsened to 23 exits and -$2.00 versus holding.
- Added `probe_live_v28_probability_collapse_branch_audit.py` to isolate the weak branch. Collapse exits are 13 hurtful / 10 helpful overall. Split behavior is unstable: train is -$5.78 versus hold, validation is +$7.00 versus hold, and holdout is -$3.22 versus hold. This is too small and too regime-dependent for a live change.
- Best collapse-branch diagnostic: `suppress_collapse_exit_if_exit_fair_drawdown_cents<=15 AND exit_sigma_t_dollars>=50`. Retrospectively this suppresses 13/23 collapse exits, 12 hurtful and 1 helpful, moving the branch from -$8.40 actual net to +$1.28 adjusted net (+$9.68). It improves train and holdout but suppresses zero validation rows, so it is exactly a forward-shadow candidate, not proof.
- Added `probe_live_v28_collapse_suppress_shadow_monitor.py` and locked `live_v28_collapse_sigma_drawdown_suppress_shadow_lock.json`. Effective boundary is `2026-05-04T16:30:00+00:00`; registry currently has 0 rows because it only records future qualifying collapse exits.
- Added `probe_live_v28_entry_guard_shadow_monitor.py` and locked two current-live-v28 entry skip hypotheses from the loss-guard audit, both effective from `2026-05-04T16:30:00+00:00`: the clean physics rule `skip_if_btc_age_ms_gt_600`, and the more aggressive retrospective rule `skip_if_edge_lt_2p1_or_eligible_depth_gt_1300`. The registry currently has 0 rows because it only records future live fills that these guards would have skipped.
- Physics read: the weak branch may be overreacting to transient path turbulence. A "full collapse" exit is more suspicious when terminal sigma is still high and fair drawdown is modest; that state says uncertainty remains alive, not that the terminal side has become physically impossible.
- Goal is not complete. No live bot logic, processes, or orders were changed.

12:30-12:31 EDT / 16:30-16:31 UTC first post-lock refresh:

- The 12:30 market resolved as a live v28 win. Refreshed live-only score: 210 entries, 175 completed round trips, 34 confirmed wins, 1 confirmed settled loss, 0 open positions, net P&L $6.71 on $375.29 (+1.788%), 334 resolved and 1 unresolved recurring markets.
- Refreshed current-bot loss guard after settlement. Baseline is now $6.71; top retrospective guard `edge_cents>=2.1 AND eligible_depth<=1300` remains best at $11.15 net (+$4.44), 182/210 trades retained, 125/139 filled markets retained, 0 settled losses. The clean `btc_age_ms<=600` guard remains robust at $9.57 net (+$2.86), 200/210 trades retained, 133/139 filled markets retained.
- Current v28 filled-market coverage is now 139/334 = 41.62%, still not close to the broad >=80% recurring-market goal. These guards remain current-live-engine loss controls, not broad-coverage solutions.
- Refreshed exit audit: 153 matched resolved exits still add $15.17 versus holding. `probability_collapse_full` remains the weak branch at 23 exits and -$2.00 versus holding.
- Ran both exit-suppression shadow monitors and the entry-guard shadow monitor after the 16:30Z boundary. All three registries still have 0 rows; no qualifying post-boundary exits or skipped-entry candidates have appeared yet.
- Physics read: the newest live win strengthens the view that v28's existing selective entry plus exit system is real but narrow. The next evidence has to come from registered post-boundary rows; retrospective scans are now only hypothesis generators.
- Goal is not complete. No live bot logic, processes, or orders were changed.

12:32-12:33 EDT / 16:32-16:33 UTC broad v28 opportunity refresh:

- Refreshed `probe_live_v28_fv_accuracy_volume.py`: 246 usable deduped v28 entry orders across 331 markets with inferred outcomes, 11,704 candidate rules scanned, 0 rules meeting the 95% accuracy plus 75% volume/sample gates. Baseline filled-entry accuracy is 189/246 trades (76.83%) and 376/489 contracts (76.89%). Holdout is 39/50 trades (78.00%).
- The high-volume filled-entry frontier remains around 80%, not 95%: the top high-volume rules retain about 76% of contracts and score about 79.84% all-contract accuracy, with weak validation near 65.71%. That cannot be the requested broad proof.
- Refreshed `probe_live_v28_websocket_opportunity_physics.py --fetch-btc-candles`: 482 v28-approved raw websocket signal rows, 151 unique markets under first-per-market dedupe, all resolved; primary first-per-market baseline is 117/151 trades (77.48%) and 234/302 contracts (77.48%), with 87 fresh rows after the opportunity lock.
- No opportunity physics rule clears the 95% accuracy / 75% retention gate. The best high-volume first-per-market rules are around 79.43% all accuracy and 75.86% holdout accuracy at 93.38% retention. The all-signals sensitivity has higher high-volume rows around 82.6%-82.8% all accuracy, but holdout remains around 77.6%-78.7%.
- Physics read: the present v28 feature family does not hide a 95%-accurate high-coverage classifier. The live bot's modest profitability is better explained by selective entry price, position sizing, and exits shaping the loss tail. For the broad >=80% recurring-market goal, the next model needs a P&L-aware state process, not just a stricter directional filter.
- Goal is not complete. No live bot logic, processes, or orders were changed.

12:35 EDT / 16:35 UTC exit audit correction:

- Found and fixed a material audit flaw in `probe_live_v28_exit_value_audit.py`: the previous report only counted the 153 resolved exits that matched an `exit_signal_seen` telemetry row. There are 22 additional resolved exits without a matched exit-signal feature row, and they materially change the conclusion.
- Corrected all-exit baseline: 175 resolved exits, actual exit net $-7.62 versus $-11.58 if held to settlement, so exits add $3.96 overall. The matched feature subset still adds $15.17, but the 22 unmatched exits subtract $11.21 versus holding: actual $-1.10 versus hold $10.11, with 15 hurtful and 1 helpful unmatched exits.
- This de-rates the earlier "exit engine is the main reason live v28 works" claim. More accurate read: matched v28 exits are often valuable, but unmatched/featureless exits are a major leak that offset most of that value. Overall live profitability currently comes from settled wins plus a smaller net exit contribution.
- Under the corrected audit, general `suppress_exit_if_sigma_t_dollars>=100` is no longer a strict-pass diagnostic; strict pass count is now 0. The existing forward monitor remains useful as exploratory telemetry, but it is not a promotion candidate.
- Physics read: telemetry/exit-state consistency is now part of the underlying physics. If an exit cannot be tied back to the modeled state that supposedly justified it, it should not be trusted as evidence that the model knew anything; those unmatched exits need their own failure audit.
- Goal is not complete. No live bot logic, processes, or orders were changed.

12:39 EDT / 16:39 UTC scorer stale-exit fix and corrected live score:

- Patched `score_bot_log.py`, not the live bot, to prevent a heartbeat-confirmed exit or execution-telemetry exit from using an exit signal/fill event that happened before the specific entry being scored. This was a research/scoring bug: later entries could be paired with stale earlier exit evidence.
- After the scorer fix, refreshed live-only v28 score: 210 entries, 159 completed round trips, 48 confirmed wins, 3 confirmed settled losses, 0 open positions, net P&L $17.46 on $375.29 cost basis (+4.652%). This is a much stronger live score than the stale-exit scorer showed.
- Corrected current-bot loss guard baseline is now $17.46, 99 negative trades, 3 settled losses, 139 filled markets out of 334 resolved recurring markets (41.62% coverage). Best retrospective guard remains `edge_cents>=2.1 AND eligible_depth<=1300`: $21.28 net (+$3.82), 182/210 trade retention, 125/139 filled-market retention, 2 settled losses. Clean `btc_age_ms<=600` remains useful: $20.32 net (+$2.86), 200/210 trade retention, 133/139 filled-market retention, 2 settled losses.
- Corrected exit audit: 159 resolved exits, actual exit net $-4.04 versus $-18.75 if held, so exits add $14.71 overall. Matched feature rows add $15.49; remaining unmatched heartbeat-confirmed rows are now only 9 exits and -$0.78 versus holding after the stale-pairing fix.
- Exit reason read after correction: `mushroom_v28_exit_value_over_hold` adds $13.34, `mushroom_v28_probability_reduce` adds $4.97, and `mushroom_v28_probability_collapse_full` remains weak at 22 exits and -$2.82 versus holding. The collapse-branch shadow candidate still makes sense, but its historical metrics are slightly changed by the scorer fix.
- Broad objective is still unresolved: the live v28 engine is profitable but narrow at ~41.6% resolved recurring-market coverage. The best current-live improvements are loss controls within v28, not the >=80% recurring-market model.
- Physics read: the strongest thing surfaced so far is not a new probability formula; it is state hygiene. The model looked worse because the scorer violated temporal causality. Once causality is restored, v28 is meaningfully profitable, and the remaining model work should protect that P&L shape while expanding market coverage.
- Goal is not complete. No live bot logic, processes, or orders were changed.

13:06-13:15 EDT / 17:06-17:15 UTC FV probability-surface correction:

- Refocused from scoring to the underlying FV probability model. Mapped v28's core assumptions: Brownian terminal anchor, symmetric empirical residual transport, weak boundary arrow, and default close-to-close horizon variance.
- Added `btc_mushroom_forecaster_v29_fast.py` as a research-only candidate that tests two priors directly: final-minute settlement averaging and small gated signed residual transport. The signed-transport idea did not improve calibration; it generally made the surface underconfident and worsened ECE.
- Added `probe_mushroom_v29_fv_surface.py`, a probability-quality replay that feeds Coinbase 1m candles through v28/v29 engines and evaluates Brier/logloss/ECE on resolved heartbeat states. This is model calibration, not an entry/exit scorer.
- Swept effective settlement averaging windows of 30/45/60/75/90 seconds. `v28_avg90` beat the current v28 surface most consistently. Minute-bucket holdout Brier/logloss improved to 0.151482/0.450333 versus 0.152618/0.454326. Dense all-heartbeat holdout improved to 0.147648/0.440378 versus 0.148720/0.443827.
- The useful model correction is simple physics: BTC recurring markets settle against a final averaging process, not an instantaneous point close. The best effective window is 90s on these Coinbase-candle replays, likely because the candle proxy and Kalshi settlement feed are not identical one-second instruments.
- The avg90 live-path patch was reverted to respect the active goal constraint: do not change existing bot logic/code. The currently running live process was not restarted and no orders were touched. Avg90 remains a research/shadow FV candidate.
- Physics read: the first real FV improvement is not more signed regime cleverness. It is making the stochastic horizon match the actual settlement mechanism and data proxy. Next model work should test terminal averaging plus barrier/touch survival as a probability surface, not as a skip rule.
- Goal is not complete.

13:20-13:46 EDT / 17:20-17:46 UTC exact final-average FV physics:

- Added `btc_mushroom_forecaster_v30_fast.py` as a research-only FV candidate. v30 keeps v28's Brownian anchor, boundary arrow, and symmetric transport, but fixes the inside-settlement-window variance law. Once the forecast is already inside the averaging window, Brownian average variance should scale as `h^3 / (3 * delta^2)`, not the previous `h^2 / delta` proxy.
- Added v30 candidates to `probe_mushroom_v29_fv_surface.py` and reran both probability replays. Minute-bucket holdout improved again: current v28 Brier/logloss 0.152618/0.454326, v28_avg90 0.151482/0.450333, and v30_avg90_exact_var 0.150853/0.447654.
- Dense all-heartbeat validation also improved on holdout: current v28 0.148720/0.443827, v28_avg90 0.147648/0.440378, and v30_avg90_exact_var 0.147398/0.439367. The gain is concentrated near the final averaging window, which supports the physics explanation.
- The horizon-bucket audit showed a sharper nuance: exact 90s averaging is excellent in the final minute but over-collapses uncertainty in the 60-90s band when using the Coinbase 1m proxy. That rejects the prior that the effective 90s settlement horizon and the known-average clock are the same clock.
- Added `btc_mushroom_forecaster_v31_fast.py` as a research-only proxy-aware FV candidate. v31 keeps the empirically useful 90s effective settlement horizon before the final minute, then applies exact Brownian average-collapse only inside the final 60 seconds.
- Reran the official probability-surface reports with v31. Dense all-heartbeat holdout now ranks v31 best: Brier/logloss 0.147278/0.438720 versus current v28 0.148720/0.443827 and v28_avg90 0.147648/0.440378. Minute-bucket holdout also ranks v31 best at 0.150853/0.447654.
- Temperature sweeps on v30 did not produce a stable improvement. Validation liked softer temperatures, while holdout Brier often preferred the existing sharper temperature. No global temperature change is promoted.
- Updated `probe_fv_avg90_strict_probability_monitor.py` so future rows include v30 and v31 probabilities without backfilling older rows. Latest strict registry has 16 total rows, 15 resolved and 1 pending; v31 has only 4 resolved strict-forward rows so far, far too small for a live decision.
- No existing live bot logic/code was changed and the running live process was not touched. v31 is the current best research FV probability surface, not a live patch.
- Physics read: the best current correction is two-clock settlement modeling. Use a 90s effective settlement/proxy horizon for pre-terminal uncertainty, but only let the model collapse like a known Brownian average inside the final 60 seconds. Signed residual transport remains rejected; temperature tuning remains unproven.
- Goal is not complete.

13:47-13:51 EDT / 17:47-17:51 UTC v31 residual physics and book-observation prior:

- Added `probe_v31_probability_residual_physics.py`, a calibration residual audit for v31. It does not choose trades; it buckets FV prediction residuals by physics state and asks where the probability surface is still miscalibrated.
- The largest v31 residual is book/model disagreement. On all-heartbeats holdout, when `book_minus_model_p_side` is below -20c, v31 predicts 52.52% but realizes 21.57%; when it is above +20c, v31 predicts 47.48% but realizes 78.43%. Weighted absolute residual by feature ranks `book_minus_model_p_side` worst at 7.09%, far above drift/velocity/adverse-move features.
- Added `probe_v31_book_observation_blend.py` to test the prior that the FV model should ignore the Kalshi book. This is probability calibration only, not a trade scorer and not evidence of ask-crossing edge.
- The book-observation result is decisive for raw probability quality: all-heartbeats holdout Brier/logloss is 0.136824/0.409717 for `book_mid_probability`, versus 0.147278/0.438720 for physics-only v31. Validation agrees: 0.121342/0.364868 for book mid versus materially worse physics-only probabilities.
- Logit blends between v31 and book are monotonic in this sweep: more book weight improves probability calibration, and pure book mid is best. This says the current physics model is missing information already embedded in market quotes.
- Important constraint: book-mid calibration is not tradable-edge proof because a live strategy pays the ask and crosses spread. The next FV-model question is how much book observation to trust without erasing the edge signal needed for profitable trades and the >=80% recurring-market coverage target.
- Updated the strict forward probability monitor again so future rows include `book_mid_probability` beside v28/v30/v31. Latest strict registry is 22 total rows, 15 resolved and 7 pending; book probability has 0 resolved strict-forward rows so far because it was added after the already-resolved rows.
- Physics read: the pure terminal-price process is no longer enough. The best model path is a two-layer probability surface: v31 for settlement-aware physical prior, plus a book-observation/Bayesian update layer that treats Kalshi quotes as noisy evidence, not as a direct trade rule.
- Goal is not complete. No live bot logic, processes, or orders were changed.

13:53-13:57 EDT / 17:53-17:57 UTC chronological book/v31 calibration:

- Added `probe_v31_book_calibrated_probability.py` to fit low-parameter book-observation calibrators on the chronological train split only, then evaluate validation/holdout. This is still probability calibration only, not a trading scorer.
- Train-fit coefficients: `book_platt=[-0.065579, 1.108623]`; `book_v31_platt=[-0.068883, 1.197192, -0.097481]`. The negative/small v31 coefficient means the physics prior adds little beyond book once book is observed in this sample.
- Holdout probability quality improved beyond raw book: `book_v31_platt` Brier/logloss 0.135856/0.409002, `book_platt` 0.135956/0.409099, raw book mid 0.136824/0.409717, physics-only v31 0.147278/0.438720, current v28 0.148720/0.443827.
- Validation also supports the calibrated layer: `book_v31_platt` 0.121276/0.362725, raw book 0.121342/0.364868, physics-only v31 0.135996/0.406863.
- Updated `probe_fv_avg90_strict_probability_monitor.py` to freeze the train-fit `book_platt` and `book_v31_platt` coefficients into future strict-forward rows without backfilling. Latest registry is 26 total rows, 15 resolved and 11 pending; calibrated-book rows have 0 resolved strict-forward samples so far.
- Physics read: current best probability model is no longer pure v31. It is a calibrated market-observation posterior dominated by book log-odds, with v31 retained mostly as a settlement-aware prior/residual feature. This must still be translated into a profitable ask-crossing model without losing the 75-80% market coverage target.
- Goal is not complete. No live bot logic, processes, or orders were changed.

14:00-14:05 EDT / 18:00-18:05 UTC calibrated FV edge-capacity and first forward lock:

- Added `probe_v31_calibrated_fv_edge_capacity.py` to bridge probability calibration to the user's coverage constraint. It is research-only and causal within the replay: first qualifying positive-edge heartbeat per market, hold-to-settlement gross cents, no exits, no fees, no live orders.
- The best robust high-coverage replay candidate is `book_v31_platt` with a 2c gross edge threshold. It selected 295/330 all markets (89.39%), with train/validation/holdout coverage 87.88%/89.39%/93.94% and positive gross net in all splits: +561c/+99c/+257c. Holdout was 40/22 and +6.87% gross ROI on selected asks.
- `book_platt` with 2c edge had stronger holdout net (+282c) but only 73.03% all coverage and 70.71% train coverage, below the user's 75-80% recurring-market floor. `book_v31_platt` at 3c kept 75.15% all coverage but validation was negative, so it is not the forward candidate.
- Added `probe_v31_calibrated_edge_shadow_monitor.py` and locked `book_v31_platt_first_edge2` for strict forward validation. The model definition time is the train-only calibration report timestamp, `2026-05-04T17:54:54.018002Z`; rows are registered only while market close is still future.
- First strict-forward edge selection registered: `KXBTC15M-26MAY041415-15`, entry `2026-05-04T18:00:31.066Z`, selected NO at 70c, calibrated `book_v31_platt_p_yes=0.2568`, gross edge +4.32c. It is pending.
- Refreshed the strict probability monitor after the 14:00 close. It now has 33 registered probability rows, 29 resolved and 4 pending. Calibrated-book probability rows are still tiny but perfect so far: `book_platt` 7 resolved, Brier/logloss 0.001713/0.027244; `book_v31_platt` 7 resolved, 0.001278/0.023486. This is encouraging but far below sample-size proof.
- Physics read: the first viable broad-coverage path is no longer "better Brownian alone." It is calibrated market-observation fair value: use v31 as a settlement-aware physical prior, but let the Kalshi book act as a noisy measurement, then require at least a small calibrated edge over ask. The 2c threshold is the first candidate that passes retrospective split/coverage sanity and has a strict-forward lock.
- Goal is not complete. Forward sample size is effectively zero for edge P&L, and calibrated-book probability has only 7 resolved strict-forward rows. No live bot logic, processes, or orders were changed.

14:06-14:08 EDT / 18:06-18:08 UTC cost robustness pressure test:

- Added `probe_v31_calibrated_edge_cost_robustness.py` and expanded `probe_v31_calibrated_fv_edge_capacity.py` to sweep finer gross-edge thresholds around 2-3.5c.
- Cost robustness result: `book_v31_platt` at 2c gross edge is robust through 1.5c per-contract cost across train/validation/holdout, with min split coverage 87.88% and nets +300.0c/+10.5c/+164.0c. It remains positive at 1.0c and 0.5c costs with more margin.
- No high-coverage candidate survived a full 2.0c per-contract cost across all splits. `book_v31_platt` at 2c gross edge still has strong holdout after 2c cost (+133c, 93.94% coverage) and train +213c, but validation is -19c. Finer thresholds from 2.25c to 3.5c did not fix validation while preserving coverage.
- `book_platt` at 2c gross edge is positive after 2c cost in train/holdout and exactly flat in validation, but train/validation coverage are only 70.71%/72.73%, below the user's floor.
- Physics read: the calibrated-book edge exists, but it is thin. It may be viable with low execution cost or with the live bot's exit/tail management, but as a pure hold-to-settlement fair-value edge it is not yet a 2c-cost-proof high-coverage system. The strict-forward lock remains useful, but promotion would be premature.
- Goal is not complete. No live bot logic, processes, or orders were changed.

14:10-14:20 EDT / 18:10-18:20 UTC time-aware calibration and first forward edge result:

- Expanded `probe_v31_book_calibrated_probability.py` with two additional train-only calibrators: `book_v31_time_platt` and `book_v31_micro_platt`. The time model uses book logit, v31 logit, and log time-to-close. The micro model additionally uses spread and absolute book-confidence terms.
- Probability calibration read: `book_v31_time_platt` slightly improves validation Brier/logloss to 0.121223/0.362321, but worsens holdout to 0.136047/0.409227 versus plain `book_v31_platt` at 0.135856/0.409002. `book_v31_micro_platt` is worse on holdout, so spread/abs-book terms look overfit.
- Edge-capacity read changed: despite weaker holdout probability, `book_v31_time_platt` with 1c gross edge is the first candidate to survive a full 2c per-contract cost across train/validation/holdout while keeping ~100% coverage. Nets after 2c cost are +889c/+102c/+4c with min split coverage 99.49%. Holdout margin is razor-thin, so this is a forward-shadow candidate, not proof.
- Added `probe_v31_time_edge_shadow_monitor.py` as a separate strict-forward wrapper for `book_v31_time_platt_first_edge1`. It writes its own lock/registry/report and does not contaminate the existing `book_v31_platt_first_edge2` registry.
- After the 14:15 market resolved, both forward edge monitors recorded their first resolved win. `book_v31_platt_first_edge2` is 1/0, +30c gross, with one pending next-market selection. `book_v31_time_platt_first_edge1` is 1/0, +22c gross, with one pending. Sample size is still effectively zero.
- Refreshed the strict probability monitor: 37 rows registered, 33 resolved, 4 pending. Calibrated-book probability remains much better than pure physics on this tiny strict sample: `book_v31_platt` has 11 resolved rows, Brier/logloss 0.023505/0.118075, 100% side accuracy. This is encouraging but nowhere near sample-size proof.
- Patched `probe_v31_calibrated_edge_shadow_monitor.py` registry dtype handling after pandas warnings on first resolution; no model logic changed.
- Updated `probe_fv_avg90_strict_probability_monitor.py` to add `book_v31_time_platt` to future strict probability rows. Latest strict probability registry is 40 total rows, 33 resolved and 7 pending; `book_v31_time_platt` has 0 resolved rows because it was added after the resolved rows.
- Physics read: time-to-close may be useful less as a pure probability improvement and more as an edge/cost shaper. The current candidate set is now two forward monitors: plain calibrated book/v31 at 2c gross edge for stronger holdout edge, and time-aware calibrated book/v31 at 1c gross edge for cost/coverage robustness. Both need live sample size.
- Goal is not complete. No live bot logic, processes, or orders were changed.

14:54-15:07 EDT / 18:54-19:07 UTC FV probability model v32:

- Refocused the work on FV probability quality only. No scorer, entry/exit rule, live bot logic, process, or order path was changed.
- Added `btc_mushroom_forecaster_v32_fast.py` as a research-only pure FV candidate. v32 keeps v31's exact final-60s Brownian settlement-average collapse, but lengthens the effective pre-terminal settlement/proxy horizon from 90s to 110s.
- Updated `probe_mushroom_v29_fv_surface.py` to include `v32_avg110_final60_exact` and reran both official resolved-heartbeat probability replays.
- All-heartbeats probability replay: v32 is now the best pure physical holdout surface at Brier/logloss 0.147142/0.438480, versus v31 at 0.147278/0.438720 and current v28 at 0.148720/0.443827. Validation remains essentially tied: v31 0.135996/0.406863, v32 0.136017/0.406971.
- Minute-bucket replay agrees more strongly: v32 holdout Brier/logloss 0.150618/0.446803, versus v31 0.150853/0.447654 and current v28 0.152618/0.454326.
- Expanded `probe_v31_book_calibrated_probability.py` to compare v32 and a small train-only YES-oriented 3-minute drift-projected posterior. The best holdout probability model is now `book_v31_drift3_platt` at Brier/logloss 0.135775/0.408656, slightly better than `book_v31_platt` at 0.135856/0.409002 and raw book mid at 0.136824/0.409717. Validation also improves slightly over plain `book_v31_platt`: 0.121227/0.362619 versus 0.121276/0.362725.
- The v32 calibrated posterior is close but not better than the v31 drift version: `book_v32_drift3_platt` holdout 0.135784/0.408706. The pure v32 prior helps, but once book observation is included the difference between v31 and v32 is very small.
- Updated the strict forward probability monitor to register v32 and `book_v32_platt` only on future rows. Latest registry has 50 total opportunities, 44 resolved and 6 pending. v32/book_v32 have 0 resolved strict-forward rows because they were just added, so there is no backfilled proof.
- Physics read: the physical prior is now cleaner: two-clock settlement with a slightly longer 110s proxy horizon. The dominant probability improvement remains a calibrated market-observation posterior, with a very small drift correction. The tradeoff is clear: pure physics improved modestly; book-observed FV improved materially, but still needs strict-forward sample before any live use.
- Goal is not complete. Forward proof is still tiny and no live promotion is defensible.

15:08-15:15 EDT / 19:08-19:15 UTC drift-aware FV edge capacity:

- Extended `probe_v31_calibrated_fv_edge_capacity.py` to include the new probability columns: `v32_probability`, `book_v32_platt`, `book_v31_drift3_platt`, and `book_v32_drift3_platt`. This remains a research-only fair-value consequence check, not a scorer or live-bot patch.
- Reran the gross causal first-edge capacity audit and cost robustness pressure test. The drift posterior materially improves gross high-coverage holdout capacity: `book_v31_drift3_platt` and `book_v32_drift3_platt` at 1c gross edge both select 66/66 holdout markets, 41/25 W/L, +445c gross, +12.18% ROI. The old `book_v31_platt` 2c row was 62/66 holdout markets, 40/22, +257c gross, +6.87% ROI.
- The better holdout is not enough for promotion. At a realistic 2c per-contract cost, drift candidates do not remain positive across train/validation/holdout. `book_v32_drift3_platt` at 2c gross edge is still positive through 1.5c cost across splits, with train/validation/holdout +49.5c/+28.5c/+125.0c and 86.36% min split coverage, but fails at full 2c cost with train -36c and validation flat.
- Existing `book_v31_time_platt_first_edge1` remains the only candidate that survives the full 2c cost pressure test across splits while keeping ~99.49% coverage, but its holdout margin is only +4c after 2c cost. That is still shadow-only.
- Added `probe_v32_drift_edge_shadow_monitor.py` as a separate strict-forward monitor for `book_v32_drift3_platt_first_edge2`. Its lock is `logs/edge_research/v32_drift_edge_shadow_lock.json`; registry is `logs/edge_research/v32_drift_edge_shadow_registry_latest.csv`; report is `logs/edge_research/v32_drift_edge_shadow_monitor_latest.md`.
- First v32-drift shadow run registered 0 selections: only 1 market was observed after the model definition time, and no qualifying 2c edge appeared while that market was still open. This is normal and avoids backfilled evidence.
- Physics read: the 3-minute drift term appears to improve the model's fair-value shape and holdout economics, especially by finding cheaper asks. But its train/validation cost fragility says it may be regime-sensitive. It belongs in strict-forward shadow alongside the existing time-aware posterior, not in the live bot.
- Goal is not complete. No live bot logic, processes, or orders were changed.

15:17-15:19 EDT / 19:17-19:19 UTC strict-forward refresh:

- Refreshed all strict-forward probability/edge monitors after adding v32 and drift candidates. No live bot code/process/orders were touched.
- `book_v31_platt_first_edge2` now has 4 registered selections, 3 resolved and 1 pending. Resolved record is 3/0, +105c gross, 50.00% resolved-market coverage over the post-definition observed market denominator. Still far too small for a model decision.
- `book_v31_time_platt_first_edge1` now has 3 registered selections, 2 resolved and 1 pending. Resolved record remains 2/0, +51c gross, 40.00% resolved-market coverage over its post-definition denominator.
- `book_v32_drift3_platt_first_edge2` remains at 0 registered selections. It has now observed 2 markets after model definition, with 1 resolved and 1 pending, but no qualifying 2c edge while a market was still open.
- Strict probability registry now has 53 registered opportunities, 50 resolved and 3 pending. v32-only probability has just 6 resolved strict-forward rows: Brier/logloss 0.194707/0.581588, side accuracy 83.33%, mean p_yes 43.98%, yes rate 0.00%. `book_v32_platt` also has 6 resolved rows: Brier/logloss 0.118668/0.410338, side accuracy 100%, mean p_yes 32.89%, yes rate 0.00%. Tiny sample, not proof.
- Physics read: forward evidence is still too young. The older calibrated-book monitor is directionally encouraging, but v32 and drift have essentially no forward edge sample yet. Keep collecting; do not promote.
- Goal is not complete.

15:20-15:25 EDT / 19:20-19:25 UTC blended time/drift FV posterior:

- Tested a low-complexity logit blend of the time-aware posterior and the v32 3-minute-drift posterior: 15% `book_v31_time_platt` plus 85% `book_v32_drift3_platt`.
- Probability quality is not the absolute best but remains near the top: holdout Brier/logloss 0.135811/0.408749, validation 0.121219/0.362565. Best pure probability remains `book_v31_drift3_platt` at 0.135775/0.408656 holdout.
- Edge/cost consequence is much better: `book_time_v32drift85` at 1c gross edge keeps 99.49% minimum split coverage and survives a full 2c per-contract cost across train/validation/holdout with +122c/+221c/+369c. The previous full-2c robust candidate, `book_v31_time_platt` at 1c, was only +889c/+102c/+4c; this new blend materially improves the weak holdout margin.
- Holdout gross first-edge capacity for `book_time_v32drift85` at 1c is 66/66 markets, 42/24 W/L, +501c gross, +13.54% ROI. This beats the prior drift-only 1c row at +445c and the older `book_v31_platt` 2c row at +257c.
- Added `probe_v32_blend_edge_shadow_monitor.py` as an isolated strict-forward monitor for `book_time_v32drift85_first_edge1`. Lock: `logs/edge_research/v32_blend_edge_shadow_lock.json`; registry: `logs/edge_research/v32_blend_edge_shadow_registry_latest.csv`; report: `logs/edge_research/v32_blend_edge_shadow_monitor_latest.md`.
- First strict-forward blend selection registered while market close was still future: `KXBTC15M-26MAY041530-30`, entry `2026-05-04T19:22:05.267Z`, selected NO at 87c with +2.386c gross edge, pending.
- Physics read: the blend is the best broad-coverage FV candidate so far. It says the book-observation posterior needs both a terminal-time correction and a short-drift correction; either alone is thinner. Still no live promotion: forward sample is one pending row.
- Goal is not complete. No live bot logic, processes, or orders were changed.

15:26 EDT / 19:26 UTC block stability check:

- Added `probe_v32_blend_block_stability.py` to save a chronological block-stability audit for the strongest FV edge candidates. This is an overfit check, not a scorer.
- The blended candidate remains best on aggregate economics, but it is not block-stable enough to call solved. At 2c cost, `book_time_v32drift85` edge1 has total block net +712c, 96.97% minimum block10 coverage, but only 6/10 positive block10 chunks and 10/20 positive block20 chunks; worst block10 is -157c and worst block20 is -137c.
- The time-only candidate has higher aggregate +995c at 2c cost and 7/10 positive block10 chunks, but worse weak holdout in the official split and a worse worst block20 (-208c). The old `book_v31_platt` edge2 is weaker: +327c total block net at 2c cost and only 4/10 positive block10 chunks.
- Physics read: the blend is a real improvement in the train/validation/holdout capacity framing, but the block audit rejects completion. The edge is still regime-sensitive; strict-forward sample size is mandatory.
- Goal is not complete.

15:29-15:36 EDT / 19:29-19:36 UTC executable blend frontier:

- Added `probe_v32_blend_executable_frontier.py` to test simple executable shapes around the blended FV posterior: gross edge floor, ask cap, model side-probability floor, and book side-probability floor. This is still research-only and no live bot code/process/orders were touched.
- Best high-coverage robustness rows use an ask cap and book confirmation rather than a larger model-edge floor. The most balanced candidate is `book_time_v32drift85_edge0_ask65_pside0_book0.55`: min split coverage 83.33%, train/validation/holdout net after 2c cost +965c/+281c/+352c, all net +1598c, 7/10 positive block10 chunks, worst block10 -96c.
- A higher-coverage variant `book_time_v32drift85_edge0_ask65_pside0.55_book0` keeps 85.86% min split coverage and 8/10 positive block10 chunks, but worst block is much worse at -298c. I prefer the book-confirmed ask65 row for forward shadowing because the weak-block damage is smaller while coverage stays above the 80% floor.
- Added `probe_v32_blend_exec_shadow_monitor.py` as a strict-forward monitor for `book_time_v32drift85_exec_ask65_book55_first`: nonnegative blended-model edge, selected ask <=65c, selected book-side probability >=55%. Lock: `logs/edge_research/v32_blend_exec_shadow_lock.json`; registry: `logs/edge_research/v32_blend_exec_shadow_registry_latest.csv`; report: `logs/edge_research/v32_blend_exec_shadow_monitor_latest.md`.
- First executable-blend shadow run registered 0 selections. It had observed 2 post-definition markets, one resolved and one pending, but no row meeting ask<=65/book-side>=55 while still open.
- Physics read: cost/convexity matters. The posterior can be directionally good but still overpay; the ask65/book55 shape is the first candidate that keeps the coverage floor while materially reducing block damage. It must be forward-sampled.
- Goal is not complete.

15:37 EDT / 19:37 UTC post-15:30 settlement refresh:

- Refreshed the strict-forward monitors after the 15:30 ET market resolved.
- New blended posterior shadow `book_time_v32drift85_first_edge1`: 2 registered, 1 resolved and 1 pending. First resolved selection won: `KXBTC15M-26MAY041530-30`, selected NO at 87c, outcome NO, +13c. Pending selection: `KXBTC15M-26MAY041545-45`, selected NO at 50c with +1.118c gross edge.
- Existing `book_v31_platt_first_edge2`: 4 registered, 4 resolved, 4/0, +145c gross, 57.14% resolved-market coverage over post-definition observed markets.
- Existing `book_v31_time_platt_first_edge1`: 4 registered, 3 resolved and 1 pending, 3/0, +91c gross, 50.00% resolved-market coverage.
- Executable ask65/book55 blend monitor remains at 0 registered selections after 2 observed post-definition markets; it is stricter and has not found a qualifying row yet.
- Strict probability monitor now has 60 opportunities, 53 resolved and 7 pending. New v32/book_v32 strict samples are still tiny: v32 has 9 resolved rows, book_v32_platt has 9 resolved rows.
- Physics read: the first blended edge row worked, but this is still anecdote-level. Existing calibrated-book forward rows remain clean so far but too sparse and low-coverage for completion.
- Goal is not complete.

15:40-16:11 EDT / 19:40-20:11 UTC v33 FV anti-persistence model:

- Refocused on the FV probability model itself, not scoring. No live bot logic, process, or order path was changed.
- Added `btc_mushroom_forecaster_v33_fast.py` as a research-only pure FV candidate. v33 keeps v32's 110s settlement/proxy horizon and exact final-60s collapse, then blends in a very small 3-minute anti-persistence Brownian anchor: recent 3m velocity is faded, time-damped by `(seconds_to_close / 900)^2`, and given only 5% logit weight with a mild 0.98 posterior temperature.
- Updated `probe_mushroom_v29_fv_surface.py` and reran the official probability replays. All-heartbeats: v33 is now best pure FV holdout Brier/logloss at 0.147029/0.438362, versus v32 0.147142/0.438480 and v28 live 0.148720/0.443827. Validation also improves: v33 0.135380/0.404928 versus v32 0.136017/0.406971. Train logloss is slightly worse, so v33 is a candidate, not a solved model.
- Minute-bucket replay agrees: v33 holdout Brier/logloss 0.150490/0.446548, versus v32 0.150618/0.446803 and v28 live 0.152618/0.454326. v33 is also best all-split Brier/logloss in the minute-bucket view.
- Expanded `probe_v31_book_calibrated_probability.py` to include `v33_probability`, `book_v33_platt`, `book_v33_drift3_platt`, and `book_time_v33drift85`. Pure v33 improves the physics prior, but once the book observation is included the v31/v32/v33 drift posterior family is almost tied. Best holdout remains `book_v31_drift3_platt` at 0.13578/0.40866; `book_v33_drift3_platt` is effectively tied at 0.13578/0.40867. This says v33 helps the prior more than the book-conditioned posterior.
- Updated the edge-capacity and robustness audits for v33. `book_time_v33drift85` at 1c gross edge ties the v32 blend on holdout high-coverage gross capacity: 66/66 markets, 42/24 W/L, +501c, +13.54% ROI. At 3c cost it still has positive train/validation/holdout net (+28c/+48c/+303c) with 99.49% min split coverage, but its min net is thinner than the v32 blend at 2c.
- Expanded the executable frontier to compare v32 and v33 blends. The best new v33 executable candidate is `book_time_v33drift85_edge0_ask65_pside0.6_book0`: 80.30% min split coverage, 2c-cost train/validation/holdout net +940c/+144c/+540c, all net +1624c, 8/10 positive block10 chunks, worst block10 -54c. This is the cleanest block-damage profile found so far while staying just above the 80% market coverage floor.
- Added `probe_v33_blend_exec_shadow_monitor.py` to register that executable candidate strictly forward. Initial run registered 0 selections: 1 post-definition market was observed and still pending, but no qualifying ask<=65/side-prob>=60 row appeared before the run.
- Updated `probe_fv_avg90_strict_probability_monitor.py` to register v33 and `book_v33_platt` on future rows only. Latest strict probability registry has 74 opportunities, 63 resolved and 11 pending; v33/book_v33 have 0 resolved rows because they were just added and are not backfilled.
- Forward refresh after the 15:45 ET settlement showed `book_time_v32drift85_first_edge1` fell to 1/1 and -37c on 2 resolved rows. `book_v31_platt_first_edge2` remains 5/0, +163c, but still too small and too narrow. The stricter executable monitors remain unproven.
- Physics read: the useful new prior is anti-persistence, not momentum. That questions the earlier drift prior directly. v33 improves pure FV probability in both replay denominators, but the book-conditioned edge is still regime-sensitive and forward sample is far too small for live promotion.
- Goal is not complete.

16:12-16:57 EDT / 20:12-20:57 UTC v34/v35 FV probability model:

- Stayed on FV probability quality only. No scorer, live bot logic, process, or order path was changed.
- Added `btc_mushroom_forecaster_v34_fast.py` as a materiality-gated version of v33. v34 keeps v32's 110s settlement/proxy horizon and exact final-60s collapse, but only gives the 3-minute anti-persistence anchor meaningful weight when the projected reversion shift is large enough in dollars. This fixed the broad overreaction of v33 while preserving the useful short-memory prior.
- v34 became the best aggregate pure FV surface before v35. All-heartbeats holdout Brier/logloss improved to 0.147009/0.438003 versus v33 0.147029/0.438362 and v32 0.147142/0.438480. Minute-bucket holdout Brier stayed fractionally better for v33, but v34 had better holdout logloss and better validation.
- Added `probe_v35_antipersistence_materiality_sweep.py` to question v34's fixed $40 materiality prior. The sigma-normalized materiality gate looked excellent on validation but failed holdout. No candidate beat v34 across validation and holdout in both replay denominators, so the sigma gate was rejected.
- Added `probe_v35_horizon_antipersistence_sweep.py` and `probe_v35_horizon_temperature_refine.py` to question the 110s settlement/proxy horizon. The clean winner was a longer 150s proxy horizon paired with a softer 1.02 posterior temperature: it was the only refined candidate to beat current v34 on every validation/holdout Brier and logloss cell.
- Added `btc_mushroom_forecaster_v35_fast.py` and wired `v35_h150_t102_antipersist3` into `probe_mushroom_v29_fv_surface.py`. Official replays now show v35 as the best recent-split pure FV surface: all-heartbeats validation/holdout 0.134198/0.401509 and 0.146942/0.438000; minute-bucket validation/holdout 0.137187/0.409154 and 0.150338/0.446168.
- The v35 stability audit is mixed. `probe_v35_fv_probability_stability.py` shows v35 beats v34 on validation/holdout, but loses older train rows and only improves 3/10 all-heartbeat block10 chunks and 3/10 minute-bucket block10 chunks. That points to a current-regime improvement, not universal physics.
- Expanded `probe_v31_book_calibrated_probability.py` with v35 probability/book posterior columns. Pure v35 improves the FV prior, but once Kalshi book observation is included, v34/v31/v33/v35 drift-posteriors are effectively tied. Best holdout remains `book_v34_drift3_platt` by Brier at 0.135770, with `book_v31_drift3_platt` best logloss at 0.408656.
- Updated `probe_fv_avg90_strict_probability_monitor.py` to register v34 and v35 only on future rows. Latest registry has 84 opportunities, 74 resolved and 10 pending; v34/v35 have 0 resolved strict-forward rows because they were just added and are not backfilled.
- Physics read: the best pure FV improvement found so far is v35: anti-persistence, longer proxy smoothing, and softer posterior confidence. The caveat is important: v35 is better on the recent validation/holdout regime but not broad over all chronological blocks. It is a forward-shadow candidate, not a live-bot patch.
- Goal is not complete. Need strict-forward v35 rows and more live-regime sample before promotion.

17:01 EDT / 21:01 UTC first v35 strict-forward refresh:

- Reran `probe_fv_avg90_strict_probability_monitor.py` after the 17:00 ET market closed. Registry now has 85 opportunities, 84 resolved and 1 pending.
- v34/v35 each have their first 10 resolved strict-forward probability rows. Both were 10/10 on side direction because all 10 settled YES: v34 Brier/logloss 0.180562/0.552970; v35 0.181142/0.554150. On this tiny first batch, v34 is fractionally better than v35.
- This does not invalidate v35's retrospective validation/holdout improvement, but it reinforces the main caveat: v35 needs forward sample size before any live-bot promotion.

17:02-17:20 EDT / 21:02-21:20 UTC v36 piecewise proxy-horizon model:

- Questioned the v35 prior that a 150s proxy horizon should apply uniformly near expiry. The v35 stability damage was concentrated in older short-time-to-close rows, so the new physics hypothesis is piecewise: keep v34's 110s proxy horizon near expiry, then blend toward v35's 150s proxy horizon only earlier in the market.
- Added `btc_mushroom_forecaster_v36_fast.py`. Default v36 uses the same v34/v35 anti-persistence prior, a smooth 120s-to-300s blend from 110s to 150s proxy horizon, and 1.02 posterior temperature.
- Added `probe_v36_piecewise_horizon_sweep.py`. The best compromise was `v36_s120_e300_t102`: it beat v34 on every validation/holdout Brier and logloss cell, while cutting v35's train Brier damage from +0.000237 mean to +0.000030 mean.
- Wired v36 into `probe_mushroom_v29_fv_surface.py` and reran official replays. All-heartbeats holdout: v36 0.146913/0.437782, better than v35 0.146942/0.438000 and v34 0.147009/0.438003. Minute-bucket holdout: v36 0.150424/0.446031, better than v34 0.150513/0.446279; v35 still has slightly better Brier at 0.150338 but worse logloss at 0.446168.
- Added `probe_v36_block_stability.py`. Versus v34, v36 improves 5/10 all-heartbeat block10 Brier chunks and 6/10 minute-bucket block10 chunks, with much better logloss stability: 6/10 and 9/10 block10 chunks improved. This is materially better than v35's earlier 3/10 Brier block10 result.
- Updated `probe_fv_avg90_strict_probability_monitor.py` to register v36 on future rows only. Latest registry has 90 opportunities, 85 resolved and 5 pending; v36 has 0 resolved rows because it was just added and is not backfilled.
- Physics read: v36 is now the best pure FV candidate. It preserves most of the recent v35 gain, improves logloss more cleanly, and reduces the overfit/regime-damage warning. It is still not live-promotion-ready until strict-forward rows resolve.

17:32 EDT / 21:32 UTC first v36 strict-forward refresh:

- Reran the strict probability monitor after the 17:30 ET market closed. Registry now has 92 opportunities, 90 resolved and 2 pending.
- v36 has its first 5 resolved strict-forward rows. All 5 settled YES and v36 was directionally correct on all 5, but its mean p_yes was only 54.25%, so Brier/logloss are 0.209400/0.611722. This is too small and too one-sided for a decision.
- v34/v35 now have 16 resolved strict-forward rows: v34 0.193758/0.579779, v35 0.194245/0.580766. v34 remains fractionally better on the tiny forward sample so far.
- Physics read unchanged: v36 is the best retrospective pure FV candidate, but forward proof is still essentially zero. Do not patch the live bot.

17:34-17:47 EDT / 21:34-21:47 UTC v37 dynamic-temperature model:

- Questioned the v36 prior that the softer 1.02 posterior temperature should apply near expiry. A focused replay showed v36 with 0.98 temperature fixed train/holdout Brier but gave back validation/logloss, so the new hypothesis is dynamic temperature: 0.98 near expiry, smoothly blending to 1.02 from 120s to 300s before close.
- Added `btc_mushroom_forecaster_v37_fast.py`. It keeps v36's piecewise 110s-to-150s proxy horizon and materiality-gated 3m anti-persistence, but makes posterior temperature horizon-dependent.
- Wired v37 into `probe_mushroom_v29_fv_surface.py` and reran both official replays. All-heartbeats holdout is now best at 0.146894/0.437688, beating v36 0.146913/0.437782, v35 0.146942/0.438000, and v34 0.147009/0.438003. Minute-bucket holdout: v37 0.150390/0.445819, behind v35 on Brier (0.150338) but best on logloss.
- Quick chronological block audit from refreshed prediction CSVs: versus v34, v37 improves all-heartbeat block10 Brier/logloss in 6/10 and 8/10 chunks; minute-bucket block10 in 6/10 and 9/10 chunks. Versus v36, v37 improves all-heartbeat block20 Brier/logloss in 15/20 and 14/20 chunks, and minute-bucket block20 in 15/20 and 16/20 chunks.
- Updated `probe_fv_avg90_strict_probability_monitor.py` to register v37 on future rows only. Latest registry has 93 opportunities, 92 resolved and 1 pending; v37 has 0 resolved rows because it was just added.
- Physics read: v37 is now the best pure FV research candidate. It is a cleaner physical compromise than v35/v36: dynamic proxy horizon plus dynamic confidence. Still no live promotion until strict-forward sample accumulates.

18:02 EDT / 22:02 UTC first v37 strict-forward refresh:

- Reran the strict probability monitor after the next boundary. Registry now has 95 opportunities, 93 resolved and 2 pending.
- v37 has its first resolved strict-forward row: 1/1 directionally correct, outcome YES, Brier/logloss 0.221865/0.636816 with mean p_yes 52.90%. This is only proof that the registry path works; it is not sample-size evidence.
- v36 has 8 resolved strict-forward rows, all YES and directionally correct, Brier/logloss 0.217722/0.628440. v34/v35 have 19 resolved rows and remain fractionally better on this tiny one-sided forward sample.
- Goal remains incomplete. The live-forward sample is still far too small and outcome-skewed to promote any FV candidate.

18:18 EDT / 22:18 UTC v37 strict-forward refresh:

- Reran the strict probability monitor after the 18:15 ET boundary. Registry now has 97 opportunities, 95 resolved and 2 pending.
- v37 has 3 resolved strict-forward rows, all YES and directionally correct. Brier/logloss improved to 0.175389/0.534534 with mean p_yes 59.46%.
- v36 has 10 resolved rows, all YES and directionally correct, Brier/logloss 0.204608/0.599431. v34 has 21 resolved rows, all YES and directionally correct, Brier/logloss 0.195106/0.581297.
- This is directionally okay for v37 but still not a valid decision sample. It is all YES outcomes and only 3 v37 rows.

18:33 EDT / 22:33 UTC v37 strict-forward refresh:

- Reran the strict probability monitor after the 18:30 ET boundary. Registry now has 99 opportunities, 97 resolved and 2 pending.
- v37 now has 5 resolved strict-forward rows with mixed outcomes: yes rate 60.00%, side accuracy 100.00%, mean p_yes 52.45%, Brier/logloss 0.175598/0.538211.
- v36 has 12 resolved rows with yes rate 83.33%, side accuracy 100.00%, Brier/logloss 0.199825/0.590147. v34 has 23 resolved rows with yes rate 91.30%, side accuracy 100.00%, Brier/logloss 0.193290/0.577729.
- This is the first non-all-YES v37 sample and remains favorable, but five rows is still not enough for a model decision.

18:48 EDT / 22:48 UTC v37 strict-forward refresh:

- Reran the strict probability monitor after the 18:45 ET boundary. Registry now has 101 opportunities, 99 resolved and 2 pending.
- v37 has 7 resolved strict-forward rows: yes rate 42.86%, side accuracy 71.43%, mean p_yes 53.67%, Brier/logloss 0.217319/0.623660. The two newest NO outcomes were predicted above 56% YES by v34/v36/v37, so this is a real forward miss regime to watch.
- v34 now has 25 resolved rows, Brier/logloss 0.203697/0.598779, side accuracy 92.00%; v36 has 14 resolved rows, 0.217224/0.625452, side accuracy 85.71%.
- Read: v37 still has the best retrospective physics, but the forward sample is now mixed and no longer uniformly flattering. Do not promote; keep collecting.
- Log inspection for the `KXBTC15M-26MAY041845-45` misses shows the strict rows were the first two minute-bucket observations at 18:30-18:31 ET, when v37 was around 56-57% YES. The book then rapidly moved NO: by 18:34 the live v28 bot approved NO entries, and the market settled NO. This looks like early-market state transition risk rather than a settled v37 physics failure, but it still counts against forward probability calibration.

19:11-19:16 EDT / 23:11-23:16 UTC v38 long-memory anti-persistence model:

- Continued focusing on the FV probability model, not scoring. No live bot logic, process, or order path was changed.
- Added `btc_mushroom_forecaster_v38_fast.py` as a research-only pure FV candidate. v38 keeps v37's piecewise proxy horizon, dynamic posterior temperature, and materiality-gated 3-minute anti-persistence, then adds a second conservative 60-minute anti-persistence anchor. The long-memory prior is gated by an $80 projected shift and capped at 10% logit weight; in replay its average realized weight is below 0.4%, so it is a small calibration nudge rather than a new classifier.
- Wired `v38_long60_antipersist` into `probe_mushroom_v29_fv_surface.py` and reran both official FV probability replays. All-heartbeats holdout: v38 0.146815/0.437520, better than v37 0.146894/0.437688 and live v28 0.148720/0.443827. Minute-bucket holdout: v38 0.150299/0.445625, better than v37 0.150390/0.445819 and live v28 0.152618/0.454326.
- Added `probe_v38_probability_stability.py` and saved the block audit. v38 improves v37 in every train/validation/holdout Brier and logloss cell across both replay denominators. Versus v37, v38 improves all-heartbeat block10 Brier/logloss in 7/10 and 7/10 chunks, all-heartbeat block20 in 15/20 and 14/20 chunks, minute-bucket block10 in 8/10 and 7/10 chunks, and minute-bucket block20 in 15/20 and 14/20 chunks. This is enough to make v38 the best retrospective pure FV probability candidate so far, but the edge is small.
- Added `probe_v38_fv_80coverage_projection.py` to make the broad-coverage P&L projection durable. Important correction: the earlier quick inline projection had selected the wrong side because of a descending-sort/tail mistake. The corrected probe picks the highest model edge per minute, then enters once per market at the first threshold crossing and holds to settlement.
- Corrected broad-coverage projection result: v38 does not yet prove a stable 80%+ profitable hold-to-settlement policy. At the selected 100% coverage row, v38 projects +$12.74 on $299.26 (+4.26%) over all 330 replay markets, but train is -$0.98 and holdout is -$2.06 while validation is +$15.78. No v38 threshold simultaneously gives 80%+ coverage and positive P&L across train, validation, and holdout.
- The projection failure clusters in opening-window weak-confidence trades. At the 100% coverage row, almost all entries occur around 600-900 seconds to close, with mean p_side near 52-54%. Train and holdout lose most in the 40-50c ask bucket and p_side 0.50-0.60 bucket. This points to opening-state calibration and weak-edge side selection as the next physics problem, not an exit/scorer patch.
- Updated `probe_fv_avg90_strict_probability_monitor.py` to include v38 and reran it. The strict-forward registry now has 114 opportunities, 101 resolved and 13 pending. v38 has 0 resolved rows because it was added future-only and is not backfilled; the 13 new rows are the beginning of v38's clean forward sample.
- Latest live v28 score refresh for context: 221 entries, 167 completed round trips, 2 open positions, net +$16.42 on $399.75 (+4.11%). Unique resolved-market coverage remains far below target at about 45.6%, so the live bot is profitable but still narrow.
- Physics read: v38 is the best pure FV probability surface so far. The goal is still not complete because broad 80%+ P&L is not robust under the corrected FV-only projection, and v38 has no resolved strict-forward sample yet. Next work should question the opening-window prior and weak-confidence side calibration while keeping the live bot untouched.

19:17-19:22 EDT / 23:17-23:22 UTC opening-window weak-confidence diagnostics:

- Investigated why corrected v38 broad-coverage projection is split-fragile. At the 100% coverage row, the projection picks 330 markets, wins 156 and loses 174, for +$12.74 total. The losses are not from high-confidence FV calls; they are mostly first-window trades around 600-900 seconds to close with mean p_side around 52-54%.
- Train and holdout losses cluster in the weak bucket: p_side 0.50-0.60 and ask 40-50c. Train p_side 0.50-0.60 loses -$13.92 combined; holdout p_side 0.60-0.70 loses -$2.74 despite small sample. This is weak opening-state side calibration, not a mature edge.
- Tested a targeted opening weak-confidence flattening transform on saved v38 probabilities: only rows with high seconds-to-close and low p_side were flattened toward 50/50. Some variants improved validation/holdout Brier/logloss, but none made the 80%+ projection positive in train, validation, and holdout. Rejected as v39.
- Tested simple opening path-velocity logit priors using yes-oriented 5m/15m/30m/60m velocity. The best probability variants were mostly 5-minute anti-momentum terms in the opening window; several beat v38 on validation and holdout probability loss, but they worsened train and still failed the all-split positive 80%+ projection. Rejected as v39.
- Physics read: there is likely a real opening-state effect, but current simple forms are regime-sensitive. Do not add a new live or research candidate until the opening prior improves probability and broad P&L without train/holdout damage.

19:23 EDT / 23:23 UTC constrained residual diagnostic:

- Fit a small ridge residual-logit diagnostic on top of v38 using only opening-gated physical features: moneyness, near-strike term, 5m/15m/30m/60m velocities, and the short/long anti-persistence shifts. This was used as a microscope, not as a candidate.
- Result: the diagnostic improves train Brier/logloss, but damages holdout badly. With weak regularization, holdout Brier/logloss damage is about +0.0084/+0.0192; with strong regularization the damage shrinks but remains non-improving. The best diagnostic projection at the v38 100% coverage threshold worsened from v38's +$12.74 all P&L to -$0.56, with holdout falling to -$11.82.
- Rejected. The opening miss is not explained by a simple linear residual in the obvious physical features.

19:27 EDT / 23:27 UTC first v38 strict-forward resolution:

- Refreshed `probe_fv_avg90_strict_probability_monitor.py`. Registry now has 125 opportunities, 114 resolved and 11 pending.
- v38 has its first 13 resolved strict-forward rows. All 13 are from `KXBTC15M-26MAY041915-15`, which settled NO. v38 was directionally correct on all 13: Brier/logloss 0.043153/0.185762, side accuracy 100%, mean p_yes 15.64%, yes rate 0%.
- This is a good first forward batch but only one market and one outcome class. It proves the v38 registry path works and that v38 handled this NO collapse well; it does not satisfy the live sample-size requirement.

19:31 EDT / 23:31 UTC opening maturity frontier:

- Tested whether the opening failure is just market immaturity rather than a missing probability prior. Used v38 only, selected the best side by model edge, varied minimum market age from 0 to 420 seconds, and swept edge thresholds while requiring at least 80% coverage in train/validation/holdout.
- No wait/threshold combination produced positive P&L in train, validation, and holdout while keeping 80%+ coverage. Best all-P&L rows remain the no-wait 100% coverage rows: about +$12.74 all P&L, but train -$0.98 and holdout -$2.06. Waiting 240 seconds improves train/holdout in some rows but flips validation negative.
- Rejected as a sufficient solution. The weak opening state is not solved by simply waiting a fixed amount of time if the requirement is 80%+ recurring market coverage.

19:32-19:53 EDT / 23:32-23:53 UTC v39 mid-horizon fallback probability model:

- Added `btc_mushroom_forecaster_v39_fast.py` as a research-only wrapper: v38 remains the default FV surface, but the 420-600s-to-close band uses the live-v28 FV surface. This questioned the prior that the newer pure FV model should dominate uniformly across the whole 15-minute path.
- Wired `v39_midband_v28_fallback` into `probe_mushroom_v29_fv_surface.py` and reran both official replay denominators. v39 is now the best aggregate retrospective pure FV surface: all-heartbeats holdout Brier/logloss 0.146727/0.437022 versus v38 0.146815/0.437520; minute-bucket holdout 0.150215/0.445246 versus v38 0.150299/0.445625.
- Added `probe_v39_probability_stability.py`. The gain is real but small and not universal: all-heartbeats block20 improves Brier/logloss in 9/20 and 11/20 chunks, while worst block20 damage is +0.001472 Brier and +0.004270 logloss. Minute-bucket block20 improves 9/20 and 11/20 chunks with worst damage +0.001344/+0.003852.
- Updated `probe_fv_avg90_strict_probability_monitor.py` to register v39 future-only. Latest strict registry had 131 opportunities, 125 resolved and 6 pending; v39 had 0 resolved rows because it was just added. v38 had 24 resolved rows, Brier/logloss 0.127339/0.396947 and 87.50% side accuracy, but this remains a small early sample.
- Physics read: v39 is the leading retrospective probability candidate, but it is a modest regime/timing blend, not a new high-accuracy classifier. It still needs strict-forward rows before any promotion.

20:00-20:13 EDT / 00:00-00:13 UTC entry/exit and profitability projection:

- Added `probe_v39_entry_exit_strategy_projection.py`, a research-only replay that compares v28, v38, and v39 under broad-coverage entry policies and exit policies. It uses one position per market, first eligible entry, observed ask entry, observed bid exit, quantity 2, and requires at least 80% coverage in train, validation, and holdout before ranking.
- The gross sweep evaluated 5,280 policy rows after coverage prefilter. 233 rows had positive train/validation/holdout gross P&L. Best balanced gross row: v39 `edge1_ask100_p0.60_stc0-780` with `prob50` exit, 90.91% minimum split coverage, 303 trades, gross train/validation/holdout +$5.92/+$3.16/+$2.52, all gross +$11.60 on $424.38 (+2.73%). This beats the best balanced projected v28 gross row (+$8.26 on $349.98, +2.36%) and v38 (+$10.44 on $401.20, +2.60%).
- The strongest gross P&L rows are hold-to-settlement rows around +$18, but they are train-heavy and fragile: best v38 hold row has all gross +$18.18, but holdout is only +$0.24 before fees. These should not be treated as promotion candidates.
- Added fee-adjusted metrics using the repo/dashboard Kalshi taker-fee formula. After fees, 0 rows remain positive across train, validation, and holdout at 80%+ coverage. The best balanced v39 gross row becomes -$2.91 all fee-adjusted, with train/validation/holdout fee-adjusted -$2.74/+$0.41/-$0.58. With an additional 1c adverse entry/exit fill sensitivity, that row becomes -$11.69.
- Refreshed live reference after the sweep: live v28 score is 226 entries, 168 completed round trips, 1 open position, +$19.52 on $411.39 (+4.74%), with 149 unique traded markets out of 364 resolved (~40.9% coverage). Using the same fee formula manually on logged assumed fills estimates about $12.26 in fees, reducing live to about +$7.26 (+1.76%) if those fees apply. A naive linear scale to 80% coverage would imply about +$38.1 gross, but this is not credible because the marginal extra markets are exactly where the broad-coverage projections lose robustness.
- Updated projection artifacts: `logs/edge_research/v39_entry_exit_strategy_projection_latest.md`, `logs/edge_research/v39_entry_exit_strategy_projection_summary_latest.csv`, `logs/edge_research/v39_entry_exit_strategy_projection_latest.json`, and `logs/edge_research/v39_entry_exit_strategy_projection_trades_latest.csv`.
- Read: the best candidate for probability quality is v39. The best candidate for gross broad-coverage entry/exit is v39 + p_side>=0.60, edge>=1c, enter before 780s-to-close, exit when model p_side falls to 50%. But the fee-adjusted projection says this is not live-promotion-ready. The underlying problem is still insufficient edge per trade at 80% market coverage, not merely exit logic.

20:14-20:27 EDT / 00:14-00:27 UTC fee-aware 75% frontier and candidate stability:

- Added `probe_v39_fee_aware_75coverage_frontier.py` to test the lower end of the requested 75-80% coverage band with stronger model-side confidence requirements and fee-aware ranking. It compares v28/v38/v39 across an expanded entry grid and a smaller exit set focused on hold, probability-reduce, and take-profit policies.
- The 75% fee-aware sweep evaluated 7,620 policy rows after coverage prefilter. 1,103 rows were gross-positive across train/validation/holdout, and 19 rows remained fee-adjusted positive across train/validation/holdout. This is the first retrospective path that clears fees while keeping broad market coverage.
- Best split-balanced fee row: v38 `edge-2_ask100_p0.65_stc0-600` with `prob50` exit, 95.45% minimum split coverage, 322 trades, fee-adjusted train/validation/holdout +$1.95/+$1.95/+$1.16, all fee-adjusted +$5.06 on $508.26 (+1.00% fee-adjusted ROI), gross +$16.36. This beats the best v39 fee row by split margin; v39's best comparable row is `edge-2_ask100_p0.62_stc0-600` / `prob50`, min fee-adjusted split +$0.55 and all fee-adjusted +$4.32.
- Important fragility: no 75%+ row remained positive across train/validation/holdout after adding a 1c adverse entry fill. The best v38 fee row drops to -$1.91 min split with that small haircut and -$3.20 all with a 1c adverse entry+exit roundtrip haircut.
- Added `probe_v39_fee_candidate_stability.py` for focused block stability on the top fee candidates. Best v38 p65/prob50 row is only 5/10 positive chronological deciles and 11/20 positive chronological twentieths, with worst block10 -$4.98 and worst block20 -$4.37. The row is split-positive but not block-robust.
- Artifacts: `logs/edge_research/v39_fee_aware_75coverage_frontier_latest.md`, `logs/edge_research/v39_fee_aware_75coverage_frontier_summary_latest.csv`, `logs/edge_research/v39_fee_candidate_stability_latest.md`, and `logs/edge_research/v39_fee_candidate_stability_trades_latest.csv`.
- Read: the next candidate to shadow is v38 with p_side>=0.65 in the 0-600s-to-close band and a probability-reduce exit at p_side<=50%. It is the best fee-aware broad-coverage candidate found so far, but it is not live-promotion-ready because the edge is too thin against 1c execution error and chronological blocks are mixed.

20:28-20:40 EDT / 00:28-00:40 UTC fine exit-threshold refinement:

- Added `probe_v38_fee_refine_exit_frontier.py` to refine the fee-aware v38 neighborhood instead of relying on coarse `prob45`/`prob50`/`prob55` exits. The first wider run timed out, so the grid was narrowed to the v38 p_side 0.64-0.66, edge -2/0, 570-630s-to-close neighborhood with probability exits from 44% to 52%.
- The focused refinement evaluated 360 policy rows after the 75% coverage prefilter. 44 rows were fee-positive across train/validation/holdout. Still 0 rows remained positive across train/validation/holdout after a 1c adverse entry-fill haircut.
- Best fee-only refined row by min split: v38 `edge0_ask100_p0.65_stc0-600` / `prob52`, 92.42% min split coverage, min fee-adjusted split +$1.70, all fee-adjusted +$7.23, all gross +$18.64. Block stability remains mixed: 6/10 positive deciles, 11/20 positive twentieths, worst block10 -$4.06.
- Closest 1c-entry-haircut row: v38 `edge0_ask100_p0.65_stc0-600` / `prob45`, with min 1c-entry split -$0.96 and all 1c-entry +$0.37. This is closer, but still fails the robustness gate.
- Artifact: `logs/edge_research/v38_fee_refine_exit_frontier_latest.md`.
- Read: finer exit tuning improves fee-only net from the previous `prob50` candidate, but does not solve the underlying physics/execution problem. The candidate edge is still below the 1c-noise robustness threshold.

20:41-20:48 EDT / 00:41-00:48 UTC edge-hole regime veto:

- Diagnosed losses for the refined v38 `edge0_ask100_p0.65_stc0-600` / `prob52` candidate. Losses concentrate in a non-intuitive mid-high model-edge band: entries with v38 edge 10-20c lose despite nominally strong FV edge. This questions the prior that higher model edge is monotonically safer.
- A post-hoc diagnostic removing trades whose first entry edge was 10-20c improved the candidate to 84.85% min split coverage, all fee-adjusted +$11.67, all fee+1c-entry +$5.95, and min split fee+1c-entry +$1.57. This suggested an overconfidence-hole regime, not a simple threshold problem.
- Added `probe_v38_edge_hole_veto_candidate.py` to distinguish two actual policies:
  - `skip_rows`: skip the bad row and allow a later entry in the same market.
  - `block_market_first`: if the first qualifying signal lands in the edge-hole, skip that market entirely.
- `skip_rows` failed. It often entered later in the same bad-regime market and did not clear the 1c-entry robustness gate.
- `block_market_first_edge_8_20` is now the best retrospective candidate in this branch: 78.79% minimum split coverage, 267 trades, all gross +$20.82, all fee-adjusted +$11.84, all fee+1c-entry +$6.50, and train/validation/holdout fee+1c-entry +$2.59/+$2.34/+$1.57. Block stability improved to 8/10 positive deciles and 12/20 positive twentieths, with worst block10 -$2.84.
- Coverage by split for the best row: train 80.30%, validation 78.79%, holdout 84.85%, all 80.91%. This finally sits inside the requested 75-80% recurring-market band while clearing fees and a 1c entry haircut retrospectively.
- Artifact: `logs/edge_research/v38_edge_hole_veto_candidate_latest.md`.
- Read: the best current candidate is v38 p_side>=0.65, edge>=0, 0-600s-to-close, prob52 exit, plus a market-level block when the first qualifying edge is between 8c and 20c. It is not live-promotion-ready yet because it still needs strict-forward shadow validation and larger live sample, but it is the first candidate that clears the key retrospective profitability gates.

20:51-20:54 EDT / 00:51-00:54 UTC strict-forward edge-hole shadow monitor:

- Added `probe_v38_edge_hole_shadow_monitor.py` to register the best current candidate strictly forward from a lock time. It reads live bot heartbeat/log data, replays the v38 FV surface, registers only future open markets after the lock, and tracks shadow exits at p_side<=52%; it does not submit orders or touch the live bot.
- Created lock `logs/edge_research/v38_edge_hole_shadow_lock.json` at `2026-05-05T00:51:32.357578+00:00`.
- First run completed after fixing an empty-denominator reporting bug. Registry currently has 0 shadow entries and 0 finalized rows because no qualifying post-lock candidate row was observed during the run.
- Artifacts: `logs/edge_research/v38_edge_hole_shadow_monitor_latest.md`, `logs/edge_research/v38_edge_hole_shadow_registry_latest.csv`, and `logs/edge_research/v38_edge_hole_shadow_lock.json`.
- Read: forward validation path now exists, but forward evidence is still zero. Goal remains incomplete until this candidate accumulates enough strict-forward live rows and retains fee/coverage performance.

20:55-20:57 EDT / 00:55-00:57 UTC temporal stability audit:

- Added `probe_v38_edge_hole_temporal_stability.py` to audit the primary edge-hole candidate by UTC day, split, side, and exit type using the saved candidate trades.
- Primary candidate `block_market_first_edge_8_20` is positive on 4/4 UTC days after fees plus a 1c entry haircut. Daily fee+1c-entry P&L: May 1 +$0.38, May 2 +$2.04, May 3 +$1.72, May 4 +$2.36.
- Compared with no-veto baseline: baseline has 314 trades, all fee+1c-entry +$0.95, only 2/4 positive days, and worst day -$1.41. Edge-hole candidate has 267 trades, all fee+1c-entry +$6.50, 4/4 positive days, and worst day +$0.38.
- Split detail for the primary row remains positive after fees plus 1c entry: train +$2.59, validation +$2.34, holdout +$1.57.
- Artifact: `logs/edge_research/v38_edge_hole_temporal_stability_latest.md`.
- Read: this improves the retrospective anti-overfit case, but strict-forward evidence is still required before considering promotion.

21:46-21:51 EDT / 01:46-01:51 UTC shadow funnel, late-ingest fix, and LODO audit:

- Added `probe_v38_edge_hole_shadow_funnel.py` to diagnose why the strict-forward monitor had 0 registered rows despite the bot log updating after the lock. Funnel result: 205 post-lock opportunity rows across 4 markets, 28 post-lock rows passing all entry filters across 3 markets, 3 first-eligible markets, 1 blocked by the edge-hole, and 2 after-block candidates. The previous monitor still registered 0 because both after-block candidate markets had closed by the time the one-shot monitor was run.
- Patched `probe_v38_edge_hole_shadow_monitor.py` to allow deterministic late ingestion of rows whose `entry_dt` is after the lock and whose `close_time` is after `entry_dt`, while still excluding all pre-lock backfill. This preserves model-defined-before-signal causality without requiring the monitor to be running exactly before close.
- Reran the shadow monitor. It now registered 2 post-lock forward rows and finalized both: one exited loss and one settled win. Combined gross +$0.12, fee-adjusted +$0.02, fee-adjusted with 1c entry haircut -$0.02. This is essentially flat and far too small for a model decision, but it proves the forward validation path is wired.
- Added `probe_v38_edge_hole_lodo_audit.py` for leave-one-day-out over saved retrospective candidate trades. For each UTC holdout day, the script selected the candidate with best worst-day fee+1c-entry P&L on the other three days. It selected `block_market_first_edge_8_20` every time, and the selected candidate was positive on the held-out day in 4/4 cases. The fixed primary candidate was also positive on 4/4 held-out days.
- Artifacts: `logs/edge_research/v38_edge_hole_shadow_funnel_latest.md`, `logs/edge_research/v38_edge_hole_shadow_monitor_latest.md`, and `logs/edge_research/v38_edge_hole_lodo_audit_latest.md`.
- Read: the retrospective anti-overfit case is stronger now, and the forward monitor is finally collecting post-lock rows. Goal remains incomplete because live-forward sample size is only 2 finalized shadow entries and does not verify profitability or coverage.

21:54-22:03 EDT / 01:54-02:03 UTC forward refresh and promotion gate:

- Reran `probe_v38_edge_hole_shadow_monitor.py`. The live log had grown after the lock, but the candidate row appeared during the previous monitor/funnel cycle, so a second immediate monitor pass was required to register it.
- Reran `probe_v38_edge_hole_shadow_funnel.py`. Latest funnel: 271 post-lock opportunities, 36 rows passing all entry filters, 3 first-eligible after-block candidate markets, and 0 future-close candidates after the final refresh.
- Added `probe_v38_edge_hole_promotion_gate.py` to make pass/fail explicit. Current gate requires retrospective pass, temporal pass, leave-one-day-out pass, and strict-forward pass with at least 50 finalized rows, 50 registered markets, 2 forward days, 75% forward coverage, positive fee P&L, and positive fee+1c-entry P&L.
- Latest strict-forward registry has 3 registered rows and all 3 finalized: one exited loss, two settled wins. Combined gross +$0.26, fee-adjusted +$0.15, fee-adjusted with 1c entry haircut +$0.09, fee-adjusted ROI 3.19%. The individual rows are: exited NO loss on `KXBTC15M-26MAY042115-15`, settled YES win on `KXBTC15M-26MAY042130-30`, settled YES win on `KXBTC15M-26MAY042200-00`.
- Promotion gate result: overall fail. Retrospective, temporal, and LODO gates pass; strict-forward gate fails with only 3 finalized rows vs 50 required, 3 markets vs 50 required, 1 forward day vs 2 required, and 50% forward coverage vs 75% required. Forward P&L is currently positive but far too small.
- Artifacts: `logs/edge_research/v38_edge_hole_promotion_gate_latest.md`, refreshed `logs/edge_research/v38_edge_hole_shadow_monitor_latest.md`, and refreshed `logs/edge_research/v38_edge_hole_shadow_funnel_latest.md`.
- Read: live-forward evidence is now nonzero and mildly positive, but still sample-size invalid. Continue collecting strict-forward rows; do not promote or patch the live bot.

22:30-23:00 EDT / 02:30-03:00 UTC 80% constraint, observed-FV posterior, and executable ask filter:

- Patched `probe_v38_edge_hole_promotion_gate.py` to read the fresh forward-denominator artifact instead of a stale funnel artifact for coverage. The gate now reports the same post-lock market denominator as `probe_v38_edge_hole_forward_denominator.py`.
- Added `probe_v38_edge_hole80_candidate_audit.py` to enforce the stricter 80% minimum split-coverage interpretation. The PnL-best `block_market_first_edge_8_20` row has all-market coverage 80.91% but minimum split coverage 78.79%; the best strict-80 replacement is `block_market_first_edge_10_20`, with 84.85% min split coverage, all fee+1c-entry +$5.95, and min split fee+1c-entry +$1.57.
- Important tradeoff: the strict-80 replacement is weaker temporally. `block_market_first_edge_10_20` is positive on 3/4 UTC days after fees plus 1c entry, with worst day -$0.69. The original 8-20 row remains 4/4 positive days with worst day +$0.38, but misses strict min-split 80% by 1.21 percentage points.
- Added `probe_v38_edge_hole80_exit_frontier.py` to sweep the 80%-coverage edge-hole family around entry timing, p-side, veto range, and probability/take-profit exits. It evaluated 230 rows after the 80% coverage prefilter. 40 rows were positive across train/validation/holdout after fees plus 1c entry, but 0 were positive across all splits and all UTC days. Best row: `block_first_edge_10_20` / `edge0_ask100_p0.65_stc0-600` / `prob54`, min coverage 84.85%, min split 1c +$1.68, all 1c +$5.95, 3/4 positive days.
- Added a separate strict-forward shadow for the strict-80 candidate: `probe_v38_edge_hole80_shadow_monitor.py` and `probe_v38_edge_hole80_forward_denominator.py`. Lock time is `2026-05-05T02:46:23.374949+00:00`; latest strict-80 registry has 1 open row and 0 finalized rows, so no decision is possible.
- Added `probe_v40_observed_fv_strategy_projection.py` to test a train-only book-observation posterior. The book/FV posterior improves holdout probability calibration materially: `book_v38_platt` holdout Brier/logloss 0.13590/0.40918 versus raw v38 0.14681/0.43752. But strategy projection found 0 rows that are 80%+ coverage and fee+1c positive across train/validation/holdout. Best near miss: `book85_v3815_logit_blend` / `edge-3_ask95_p0.60_stc0-600` / `prob50`, min split 1c -$0.07 and all 1c +$3.81. Read: book observation is an excellent probability sensor, but crossing the ask/spread removes most tradable edge.
- Found and fixed an executable-entry prior failure in the strict-forward shadow path: ask=0 rows existed in the heartbeat ledger and the monitor allowed them because it only had an ask cap, not an ask floor. Patched `probe_v38_edge_hole_shadow_monitor.py` and `probe_v38_edge_hole_forward_denominator.py` to require `ask >= 1c`. Rebuilt canonical registries after the patch.
- Latest PnL-first 8-20 forward shadow after the ask-floor fix: 7 registered rows, 6 finalized, 2 exited and 4 settled, settlement W/L 4/0, gross +$0.04, fee-adjusted -$0.18, fee+1c-entry -$0.30, forward coverage 7/9 = 77.78%. The sample is still far too small and now slightly negative after fees; do not promote.
- Current read: there are two viable-but-incomplete branches. The original 8-20 branch has better retrospective temporal stability and all-market 80% coverage but slightly misses strict min-split 80%. The 10-20/prob54 branch obeys strict min-split 80% but is less day-stable retrospectively and has only one open strict-forward row. The observed/book posterior improves probability accuracy but does not yet create a fee-robust high-coverage trading strategy.

23:02-23:04 EDT / 03:02-03:04 UTC forward settlement refresh:

- Reran both forward shadows after the 03:00 UTC market settled. The PnL-first 8-20 shadow now has 7 registered rows, all 7 finalized: 2 exited losses and 5 settled wins. Gross is +$0.14, fee-adjusted -$0.09, fee+1c-entry -$0.23. The two exited losses are still the reason the forward net is negative.
- The strict-80 10-20/prob54 shadow has 1 registered row and it settled as a win: gross +$0.10, fee-adjusted +$0.09, fee+1c-entry +$0.07. This is useful only as wiring evidence; sample size is 1.
- Refreshed denominators: 8-20 has 7 registered out of 10 post-lock observed markets (70.00% forward coverage), with 1 edge-hole block and 2 no-entry-filter markets. Strict-80 has 1 registered out of 2 post-lock observed markets (50.00% coverage), with the second market failing entry filters.
- Promotion gate remains fail: 7 finalized rows vs 50 required, 7 markets vs 50 required, 1 forward day vs 2 required, 70.00% forward coverage vs 75.00% required, and fee+1c-entry P&L still negative. Do not apply to the live bot.

23:33-23:53 EDT / 03:33-03:53 UTC v41 posterior and strict-80 all-day candidate:

- Verified the unused infinite trial collector was no longer running; the live bot and passive websocket recorder were left untouched.
- Added `probe_v41_physics_path_posterior_strategy.py` to test train-only posterior probability surfaces using v38/v39 plus physical path features: time-to-close, realized-vol margins, signed/adverse moves, drift margins, anti-persistence shifts, and a separately labeled book-residual variant. No live bot code/process/order path was touched.
- v41 probability read: book-residual and rich physics posteriors improve holdout calibration versus raw v38/v39, but the best tradable 80%-coverage fee+1c row remains raw v38 with edge-hole entry/exit handling. Best pure-physics posterior row reached min split fee+1c +$0.62; raw v38 strict-80 edge-hole reached +$1.68.
- Fixed warning-prone block math in `probe_v41_physics_path_posterior_strategy.py`, and fixed the same DataFrame chunking bug in `probe_v38_edge_hole80_exit_frontier.py`. The P&L/day/split metrics were correct, but the block-risk columns in the strict-80 frontier had been wrong.
- Expanded the strict-80 edge-hole frontier around the useful neighborhood: edge -2/0, p_side 0.64-0.66, min market age 0/60/120s, max close 570/600s, and the existing first-edge vetoes. The refreshed frontier has 1,440 rows after 80% coverage prefilter, 170 split-positive rows after fees plus 1c entry, and 8 rows positive across all splits and all UTC days.
- New best strict-80 all-day retrospective row: `block_first_edge_8_20` / `edge-2_ask100_p0.65_stc60-600` / `prob54`. It has min split coverage 80.30%, all coverage 81.52%, 269 trades, all gross +$21.28, all fee-adjusted +$12.06, all fee+1c-entry +$6.68, train/validation/holdout fee+1c-entry +$3.20/+$2.41/+$1.07, 4/4 positive UTC days, and 5/10 positive chronological deciles with worst decile -$3.44.
- This new row is less split-P&L-optimal than the `10_20` row but more day-stable and still satisfies the user's strict 80% recurring-market interpretation. It is now the best candidate for forward shadowing, not live promotion.
- Added separate strict-forward scripts for that exact all-day 80% policy: `probe_v38_edge_hole80_allday_shadow_monitor.py` and `probe_v38_edge_hole80_allday_forward_denominator.py`. Lock created at `2026-05-05T03:51:25.040846+00:00`; first denominator had one post-lock market and it was edge-hole blocked, so registered rows remain 0. This is only wiring evidence.
- Current read: the best FV probability model remains raw v38 for tradable high-coverage P&L. The useful improvement is not an extra logistic posterior; it is respecting the physical failure mode that v38's first mid-high edge can be an overconfidence hole, plus a small market-age constraint and a probability-reduce exit. Goal remains incomplete until the all-day strict-80 shadow collects a meaningful forward sample.

00:00-00:40 EDT / 04:00-04:40 UTC v42 latent edge-hole FV model:

- Added `probe_v42_edgehole_latent_fv_strategy.py` to test whether the edge-hole regime should be modeled as a fair-value probability correction instead of only an entry veto. The physics hypothesis is that a first qualifying raw-v38 edge in the 8-20c band is a hidden-state warning: the book is measuring a path/liquidity state missing from the pure FV prior.
- Candidate probability surfaces tested: raw v38, local band edge caps, local band book blends, market-level latent-hole flat 50/50, latent-hole book posterior, and latent-hole 80% book logit blend.
- v42 result: `v42_latent_hole_flat` with `edge0_ask100_p0.65_stc0-600` / `prob54` is the best retrospective PnL row: min split coverage 80.30%, all fee+1c-entry +$6.70, train/validation/holdout fee+1c-entry +$2.57/+$2.10/+$2.03, and 4/4 positive UTC days. But it worsens holdout Brier/logloss to 0.15231/0.45183 versus raw v38 0.14681/0.43752, so it is not the best "more accurate FV" candidate.
- The probability-clean v42 branches are better aligned with the goal. `v42_latent_hole_book` improves holdout Brier/logloss to 0.14594/0.43543 and has a high-coverage all-day-positive row: `edge0_ask100_p0.64_stc0-600` / `prob52`, min split coverage 90.91%, all fee+1c-entry +$5.47, min split fee+1c-entry +$1.15, 4/4 positive days, and 7/10 positive chronological deciles. `v42_latent_hole_bookblend80` is nearly as calibrated at 0.14603/0.43561 and has stronger block stability: min split coverage 90.91%, all fee+1c-entry +$5.50, min split +$1.23, 4/4 days, and 8/10 positive deciles.
- Added strict-forward shadow monitors for both probability-clean v42 candidates:
  - `probe_v42_latent_hole_book_shadow_monitor.py`
  - `probe_v42_latent_hole_book_forward_denominator.py`
  - `probe_v42_latent_hole_bookblend80_shadow_monitor.py`
  - `probe_v42_latent_hole_bookblend80_forward_denominator.py`
- Fixed a strict-forward causality bug in the first v42 monitor pass: for markets already in progress when the lock was created, candidate selection initially chose the first eligible row before lock and then registration discarded it. Patched v42 candidate selection to filter post-lock rows before selecting the first eligible market entry.
- v42 book strict-forward status after the fix: lock `2026-05-05T04:06:03.978229+00:00`, 1 registered, 1 finalized, settlement win on `KXBTC15M-26MAY050015-15`, gross +$1.60, fee-adjusted +$1.57, fee+1c-entry +$1.55. Denominator after refresh: 2 post-lock markets, 50% coverage. This is useful wiring evidence only; sample size is invalid.
- v42 bookblend80 strict-forward status: lock `2026-05-05T04:37:58.395568+00:00`, 0 post-lock markets so far.
- Added `probe_current_fv_candidate_comparison.py` to consolidate current candidates and avoid repeated branch confusion. Latest comparison says no candidate is promotion-ready. Best retrospective min-split PnL is the flat v42 branch, but the best probability-clean branch is v42 book/bookblend. The missing requirement for every branch is strict-forward sample size/stability.
- Current read: v42 is the first candidate that actually improves the FV probability model while keeping broad PnL plausible. The book/bookblend variants are now the lead probability-model candidates, but live-forward evidence is far too small to promote or patch the live bot.

00:40-00:53 EDT / 04:40-04:53 UTC v43 latent posterior weight sweep:

- Added `probe_v43_latent_hole_weight_sweep.py` to avoid treating the v42 80% book-blend prior as arbitrary. It sweeps latent-hole posterior weights from 35% to 100% book after the same raw-v38 edge-hole trigger, using the same 80% coverage, fees, 1c haircut, day, and block checks.
- v43 result: the best balanced row is `v43_latent_hole_bookblend90` / `edge0_ask100_p0.65_stc0-600` / `prob54`. It has min split coverage 90.91%, all fee+1c-entry +$6.82, all fee-adjusted +$13.02, gross +$23.84, train/validation/holdout fee+1c-entry +$2.49/+$2.08/+$2.25, 4/4 positive UTC days, and 7/10 positive chronological deciles. Holdout probability remains improved versus raw v38: Brier/logloss 0.14598/0.43550 vs v38 0.14681/0.43752.
- The pure book posterior (`bookblend100`) has slightly better holdout probability, but the 90% book blend is the better profit/stability compromise. Lower book weights degrade both probability and PnL. This supports the physical read that the book should be treated as a strong but not total hidden-state measurement after the edge-hole trigger.
- Added strict-forward v43 scripts:
  - `probe_v43_latent_hole_bookblend90_shadow_monitor.py`
  - `probe_v43_latent_hole_bookblend90_forward_denominator.py`
- Added/updated `probe_current_fv_candidate_comparison.py`. Latest current comparison says `v43_latent_hole_bookblend90_leader` is the best retrospective min-split PnL candidate among probability-clean branches, but it has no finalized strict-forward rows yet and is not promotion-ready.
- Forward refresh: v42 book candidate now has 2 registered / 2 finalized strict-forward rows, both settled wins, gross +$3.44, fee-adjusted +$3.39, fee+1c-entry +$3.35. Its denominator is 2 registered out of 4 post-lock observed markets (50% coverage), so this is encouraging but not valid sample evidence.
- v43 90% book-blend lock created at `2026-05-05T04:46:58.961470+00:00`. First denominator refresh saw 1 post-lock market and no entry filters passed, so v43 has 0 registered rows so far.
- Current read: v43 90% book-blend is the current best research candidate for the objective because it improves FV probability and projects stronger broad-coverage PnL without using the calibration-damaging flat transform. Goal remains incomplete because live-forward sample size and coverage are not yet verified.

01:00-01:38 EDT / 05:00-05:38 UTC v44/v45 challengers and forward failure-mode update:

- Added `probe_v44_physics_latent_hole_fv_strategy_fast.py` after the full v44 physics/latent sweep proved too slow. The fast probe reuses cached v41 physics/book predictions and tests focused latent-hole book blends. It evaluated 8,780 high-coverage policy rows across 31 probability surfaces.
- v44 result: the best robust row remained the v43 reference, but the higher-PnL challenger `v44_v41_v38_bookres_l230_holeblend100` / `edge1_ask100_p0.64_stc0-780` / `prob50` is notable: min split coverage 80.30%, all fee+1c-entry +$8.29, min split fee+1c-entry +$1.59, 4/4 positive UTC days, 7/10 positive chronological deciles, and holdout Brier/logloss 0.14093/0.42272. This is the strongest all-market PnL/probability challenger but sits right on the 80% coverage boundary and needs forward validation.
- Added strict-forward shadow setup for v44 challenger: `probe_v44_bookres_challenger_shadow_monitor.py`. Lock created at `2026-05-05T05:28:37.100066+00:00`. It starts from 0 post-lock artifact rows because the v44 replay artifact was generated before the lock; future validation requires refreshing the replay/prediction artifacts after new markets arrive.
- Refreshed live-log-backed forward shadows for v43, v42, and v38 strict-80. Current strict-forward comparison:
  - v43 90% book-blend: 2 registered, 1 finalized, 50.00% coverage, fee+1c-entry -$0.77. The finalized loss was an exit loss on `KXBTC15M-26MAY050115-15`.
  - v42 full-book clean branch: 4 registered, 3 finalized, 57.14% coverage, fee+1c-entry +$3.47.
  - v38 explicit strict-80 veto: 7 registered, 6 finalized, 58.33% coverage, fee+1c-entry +$3.51.
- The v43 forward loss is informative but not decisive: it was the same edge-hole market that the explicit v38 veto blocked, while the v42 full-book branch waited until a later YES entry and won a small amount. This questions the v43 prior that 90% book weight is always enough when raw FV and book are fighting inside the latent state.
- Added `probe_v42_latent_hole_book_p65_delayed_shadow_monitor.py` and `probe_v42_latent_hole_book_p65_delayed_forward_denominator.py` for the higher-PnL full-book delayed challenger: `v42_latent_hole_book` / `edge0_ask100_p0.65_stc120-600` / `prob52`. Retrospective: min split coverage 84.34%, all fee+1c-entry +$7.08, min split +$2.00, 3/4 UTC days, 7/10 deciles. Strict-forward lock has 0 post-lock markets so far.
- Added `probe_v45_latent_disagreement_switch_strategy.py` to test a more targeted physics rule: after the edge-hole trigger, use the v43 90% book blend normally, but switch fully to book when raw FV and book selected sides disagree. This directly targets the v43 forward-loss mode instead of blindly flattening the whole latent state.
- v45 result: `v45_latent_disagree_book_else_blend90` / `edge0_ask100_p0.65_stc0-600` / `prob54` has min split coverage 89.39%, all fee+1c-entry +$7.52, min split +$1.92, 4/4 positive UTC days, and 8/10 positive deciles. It does not beat v43 on worst split (+$1.92 vs +$2.08), but it improves all-market P&L and block stability while preserving high coverage. Holdout Brier/logloss is 0.14602/0.43566, slightly worse than v43 but still better than raw v38.
- Added strict-forward v45 scripts: `probe_v45_latent_disagreement_shadow_monitor.py` and `probe_v45_latent_disagreement_forward_denominator.py`. Lock was created after the retrospective run; it has 0 post-lock markets so far.
- Updated `probe_current_fv_candidate_comparison.py` to include v44 and v45. Latest comparison remains promotion-fail for every branch. Best worst-split retrospective branch is still v43 90% book-blend. v45 is now the best high-coverage stability/P&L challenger. v44 is the highest-PnL probability challenger but requires artifact-refresh forward validation.
- Current read: do not patch the live bot. The lead set is now v43, v45, v42 full-book delayed, and v44 book-residual. The next decisive evidence must come from strict-forward rows and coverage; current forward samples are too small and coverage is below the requested 75-80% band.

01:39-01:56 EDT / 05:39-05:56 UTC replay artifact refresh and stale-candidate correction:

- Refreshed the replay artifact chain from the live heartbeat log:
  - `probe_live_heartbeat_two_side_fv.py`
  - `probe_mushroom_v29_fv_surface.py --mode two_side_all_heartbeats`
  - `probe_v41_physics_path_posterior_strategy.py`
  - `probe_v44_physics_latent_hole_fv_strategy_fast.py`
  - `probe_v42_edgehole_latent_fv_strategy.py`
  - `probe_v43_latent_hole_weight_sweep.py`
  - `probe_v45_latent_disagreement_switch_strategy.py`
  - `probe_v38_edge_hole80_exit_frontier.py`
- Refreshed denominator: `mushroom_v29_fv_surface_predictions_two_side_all_heartbeats_latest.csv` now has 42,890 rows, 372 markets, and 21,445 opportunities. This added a fifth UTC day to the retrospective validation window.
- The new data compressed worst-split margins. The previous v43/v45/v44 rankings from the four-day window are no longer valid without qualification.
- Updated v43 read: `v43_latent_hole_bookblend90` / `edge0_ask100_p0.65_stc0-600` / `prob54` now has min split coverage 81.33%, min split fee+1c-entry +$0.45, all fee+1c-entry +$9.85, 5/5 positive UTC days, and 7/10 positive deciles. Holdout Brier/logloss improved to 0.14228/0.42787 versus raw v38 0.14318/0.43031.
- Updated v45 read: `v45_latent_disagree_book_else_blend90` / `edge0_ask100_p0.65_stc0-600` / `prob54` now has min split coverage 81.33%, min split fee+1c-entry +$0.45, all fee+1c-entry +$10.55, 5/5 positive UTC days, and 8/10 positive deciles. It ties v43 on worst split while improving all-market P&L and block stability, with nearly identical holdout probability 0.14228/0.42788.
- Updated v42 read: the full-book clean branch has the best holdout probability among latent-hole v42/v43/v45 surfaces, but its main p64 row is now split-negative after fees plus 1c entry (-$0.65 min split), despite all-market +$7.24 and 5/5 days. The delayed p65 row is also split-negative (-$0.11) and only 4/5 days.
- Updated v44 read: the prior `v44_v41_v38_bookres_l230_holeblend100` challenger is demoted. On the refreshed five-day denominator, the tracked row has min split fee+1c-entry -$3.42, 3/5 positive days, and 5/10 deciles despite all-market +$8.23. The book-residual posterior remains excellent for probability calibration, but it does not currently clear the tradable robustness gate.
- Updated v38 explicit-veto read: refreshed best is `block_first_edge_12_20` / `edge0_ask100_p0.65_stc0-600` / `prob54`, with min split coverage 81.33%, min split fee+1c-entry +$0.92, all fee+1c-entry +$7.00, but only 4/5 positive UTC days and 6/10 deciles. No v38 80%-coverage row is positive across all splits and all UTC days after fees plus 1c entry on the refreshed denominator.
- Updated `probe_current_fv_candidate_comparison.py` and regenerated `current_fv_candidate_comparison_latest.md`. It now correctly marks all candidates as not promotion-ready. Best explicit-veto worst split is v38 `12_20`, but the best probability-clean row is v45 by all-market P&L/block stability with the same worst-split margin as v43.
- Current read: refreshed evidence favors v45 over v43 as the next probability-clean candidate to watch, but the margin is thin and forward evidence is still missing. v44 is demoted. Goal remains incomplete because no candidate has strict-forward sample size, multi-day stability, or 75-80% live forward coverage.

01:57-02:04 EDT / 05:57-06:04 UTC v45 loss attribution and entry-refinement negative result:

- Audited the refreshed v45 lead trades. Current v45 lead has 334 trades, all fee+1c-entry +$10.55, gross +$28.42, and 58 losing markets. The weakest split is holdout: 61 trades, 49 wins / 12 losses, fee+1c-entry +$0.45. The weakest chronological blocks are block 2 (-$2.31) and block 7 (-$2.29).
- Loss attribution: the largest v45 losses are mostly high-ask, high-confidence reversals entered around 450-600 seconds to close and exited by probability reduction. Examples include 93c YES/NO entries with p_side around 0.94 that later collapsed to low bid exits. This suggested testing whether high ask caps or stricter confidence/edge floors could remove tail risk.
- Added `probe_v46_v45_entry_refine.py` to make that test durable. It sweeps ask caps 80-100c, p_side floors 0.64-0.68, edge floors 0-5c, max close 570/600s, and probability exits 50/52/54/56 on the v45 probability surface.
- v46 result: only 2 rows remained positive across train/validation/holdout and all UTC days after fees plus 1c entry at 80%+ coverage. The best remains the original v45 lead: `edge0_ask100_p0.65_stc0-600` / `prob54`, min split +$0.45, all +$10.55, 5/5 days, 8/10 deciles, 334 trades. Ask caps and stricter thresholds did not improve the frontier while preserving the coverage/day gates.
- Current read: the high-ask loss tail is real, but simple ask caps or stricter entry thresholds cost too much coverage or split stability. Do not refine the live bot with an ask cap based on this evidence.

02:05-02:24 EDT / 06:05-06:24 UTC v47 re-cross hazard FV candidate:

- Refreshed strict-forward monitors for v43/v45/v42 before starting the next branch. Updated forward evidence remains too small and not promotion-ready: v43 is now 4 registered / 4 finalized, coverage 66.67%, fee+1c-entry -$1.77; v45 is 1 registered / 1 finalized, coverage 33.33%, fee+1c-entry -$0.74; v42 full-book clean is 5 registered / 5 finalized, coverage 55.56%, fee+1c-entry +$2.14.
- The new forward losses reinforced the v45 loss attribution: high-confidence `NO` entries can still lose when the price looks safely below strike but then re-crosses. The physics read is that recent favorable velocity near the strike is not pure continuation evidence; it also contains snapback/re-cross hazard.
- Added `probe_v47_recross_hazard_fv_strategy.py`. It builds on the v45 FV surface and caps selected-side probability when the selected side is within 1.0 RV sigma of the strike and the 3-minute selected-side velocity is at least 0.50 dollars/second. The best durable transform caps selected-side probability at 68% in that hazard state.
- v47 result: `v47_recross_sigma1_v3cap68` / `edge0_ask100_p0.65_stc0-600` / `prob54` keeps the same 81.33% min split coverage and 334 trades as v45, but improves all fee+1c-entry from +$10.55 to +$12.10 and min split fee+1c-entry from +$0.45 to +$0.86. It stays 5/5 positive UTC days and 8/10 positive chronological deciles. Holdout probability also improves versus v45: Brier/logloss 0.14223/0.42755 vs 0.14228/0.42788.
- Added strict-forward setup for this exact v47 row: `probe_v47_recross_hazard_shadow_monitor.py` and `probe_v47_recross_hazard_forward_denominator.py`. Lock created at `2026-05-05T06:19:27.463102+00:00`. Initial denominator has 1 post-lock observed market and 0 registered entries, so there is no valid forward evidence yet.
- Updated `probe_current_fv_candidate_comparison.py` to include v47. Latest comparison still marks every candidate as not promotion-ready. Best explicit-veto worst split remains v38 `12_20`, but best probability-clean retrospective row is now v47. Goal remains incomplete until v47 or another candidate has strict-forward sample size, multi-day stability, and live forward coverage in the requested 75-80% band.

02:25-02:27 EDT / 06:25-06:27 UTC v47 exit refinement:

- Added `probe_v48_v47_exit_refine.py` to test whether the v47 probability surface wants a different exit rule. Entry is fixed at `edge0_ask100_p0.65_stc0-600`; the script sweeps probability floors, take-profit overlays, fair-value exits, stop-bid exits, and minimum-hold variants.
- v48 result: the best robust exit is `hold15_prob54`, a 15-second minimum hold before the same probability-reduce exit. It keeps 81.33% coverage, 334 trades, 5/5 positive days, and 8/10 deciles. All fee+1c-entry improves slightly from v47 `prob54` +$12.10 to +$12.34, while min split remains +$0.86.
- Current read: this is a small exit-management improvement, not the core discovery. The main edge improvement remains the v47 re-cross hazard probability cap. Do not spin another live candidate solely on `hold15_prob54` until v47 itself has forward evidence.

02:28-02:32 EDT / 06:28-06:32 UTC continuous re-cross cap check:

- Tested whether the fixed 68% v47 hazard cap is too discrete/overfit by sweeping continuous caps that rise with selected-side margin cushion and optionally fall with burst severity. This questioned the prior that a hard cap is the right physics.
- Result: no continuous cap beat fixed v47 on all-market P&L. The best all-market row remained fixed v47 at +$12.10 fee+1c-entry with min split +$0.86. The best conservative continuous row (`cap64_m10`, sigma <= 1.5, 3m velocity >= 0.50) raised min split to +$1.13 but lowered all-market P&L to +$11.31, reduced trades to 331, and worsened worst chronological block to -$3.11.
- Refreshed v47 strict-forward evidence after the check. Current v47 forward denominator has 2 post-lock observed markets, 0 registered entries, and 0 finalized rows. No promotion evidence exists yet.
- Current read: keep fixed v47 as the lead probability-clean candidate. Continuous caps are useful as a risk-averse backup idea but do not currently dominate the fixed cap.

02:33-02:47 EDT / 06:33-06:47 UTC v50 thin-edge certainty cap:

- Attributed residual v47 losses. v47 improved over v45 on only 14 markets, with the largest gain coming from delaying or flipping fragile high-confidence entries. Remaining large losses were still concentrated in high-ask, tiny-edge entries around 450-600 seconds to close.
- Tested a local probability cap for the residual failure mode: if selected ask is at least 90c, selected fair edge is <=1c, and seconds-to-close is 450-600, cap selected-side probability to 75%. This is a probability model change, not a live entry rule patch.
- Added `probe_v50_v47_thin_edge_certainty_fv_strategy.py`. Best row: `v50_thinedge_ask90_edge1_stc450_cap75` / `edge0_ask100_p0.65_stc0-600` / `prob54`, min split coverage 81.33%, 333 trades, min split fee+1c-entry +$0.99, all fee+1c-entry +$12.54, 5/5 positive days, 8/10 positive deciles, holdout Brier/logloss 0.14220/0.42718. This beats v47 (+$12.10 all, +$0.86 min split, 0.14223/0.42755).
- Quick exit check on v50: adding the same 15-second minimum hold before `prob54` improves all fee+1c-entry to +$12.78 while leaving min split at +$0.99. This is a small exit-management add-on; the v50 probability cap is the core result.
- Added strict-forward setup for v50: `probe_v50_thin_edge_certainty_shadow_monitor.py` and `probe_v50_thin_edge_certainty_forward_denominator.py`. Lock created after the retrospective run; first denominator has 0 post-lock observed markets and 0 registered rows.
- Updated `probe_current_fv_candidate_comparison.py` to include v50. Latest comparison still says no candidate is promotion-ready. Current best retrospective probability-clean row is v50, but strict-forward evidence is absent.

02:48-02:51 EDT / 06:48-06:51 UTC v50 exit artifact and first forward row:

- Added `probe_v51_v50_exit_refine.py` to make the v50 exit check durable. It confirms `hold15_prob54` is the best robust v50 exit row: min split fee+1c-entry +$0.99, all fee+1c-entry +$12.78, 5/5 days, 8/10 deciles. The base `prob54` row remains +$12.54 all and +$0.99 min split.
- Refreshed v50 strict-forward after the new lock. Current v50 forward status: 1 post-lock observed market, 1 registered shadow entry, 0 finalized rows, 100% observed coverage on that tiny denominator. Registered market is `KXBTC15M-26MAY050300-00`, selected side `no`, ask 23c, selected p_side 0.802, edge 57.18c, open until 07:00 UTC.
- Current read: the first v50 forward row shows the monitor is wired and coverage can register, but it has no settled/exited result and the denominator is only one market. This is not promotion evidence.

02:52-02:56 EDT / 06:52-06:56 UTC v44 rescue check:

- While the first v50 forward row remained open, tested whether the v50 thin-edge cap rescues the high-calibration v44 book-residual surface. This matters because v44 has excellent holdout probability but failed tradable split/day robustness.
- Result: the thin-edge cap does not rescue v44 book-residual. The best v44 book-residual-style rows still have strong all-market fee+1c-entry around +$12.7 to +$12.8, but remain split-negative (roughly -$3 min split) and only 4/5 or 3/5 positive days. Therefore they are still demoted.
- The cap does modestly improve the v43-style reference surface inside the v44 artifact (`v44_v38_holeblend90_reference_thin1`): min split +$0.58, all +$10.23, 5/5 days, 8/10 deciles, but this remains below v50's +$0.99 min split and +$12.54 all-market.
- Current read: do not chase v44 book-residual for live promotion right now. It remains a probability-calibration clue, not a tradable high-coverage strategy.

03:07-03:39 EDT / 07:07-07:39 UTC strict-forward freshness fix, weak re-cross challenger, and corrected comparison:

- Audited the first v50 strict-forward loss (`KXBTC15M-26MAY050300-00`) and found it was not valid model evidence. The strict-forward replay candle cache ended at `2026-05-05T03:22:59.999Z` while the v50 entry was at `2026-05-05T06:50:00.444Z`, so the replay engine was using BTC state more than three hours stale.
- Patched research-only replay plumbing, not the live bot:
  - `probe_physics_priors_boundary_models.py`: `normal_cdf_np` now handles empty arrays safely.
  - `probe_v38_edge_hole_shadow_monitor.py`: `build_predictions` now fetches/updates Coinbase candles for the live heartbeat window, merges fresh BTC physics columns, and drops rows without fresh BTC state. Registry rows now carry diagnostic physics columns such as spot, recross-side margin/velocity, recross hazard flag, and thin-edge flag.
- Reran strict-forward monitors/denominators on the corrected fresh-candle path. The stale v50 NO loss corrected to a YES entry at 83c that settled as a win (+30c fee+1c). The next 07:06 NO entry (`KXBTC15M-26MAY050315-15`) was a real failure: selected NO at 76c, p_side ~0.812, recross-side margin ~0.757 sigma, 3m selected-side velocity ~0.200 dps, exited at 13c, fee+1c -133c, final outcome YES.
- Corrected strict-forward comparison as of `2026-05-05T07:38:49Z`:
  - v38 legacy forward: 17 finalized, 89.47% coverage, fee+1c -$5.55.
  - v43: 10 finalized, 90.91% coverage, fee+1c -$0.94.
  - v45: 7 registered / 6 finalized, 87.50% coverage, fee+1c -$0.45.
  - v47: 5 registered / 4 finalized, 100.00% coverage, fee+1c -$1.38.
  - v50: 3 registered / 2 finalized, 100.00% coverage, fee+1c -$1.03.
  - All are still promotion-fail; sample is one UTC day and far below the 50-finalized / 2-day forward gate.
- The corrected forward failures suggest v47's re-cross hazard threshold is too strict. v47 caps only when selected-side 3m velocity >=0.50 dps; the current real failures sit near the strike with moderate favorable velocity around 0.20 dps. That is still a snapback/re-cross hazard state.
- Added `probe_v52_weak_recross_hazard_fv_strategy.py` to test lower re-cross velocity thresholds. Best v52 row is `v52_weakrecross_sigma08_v3p15_cap68 / edge0_ask100_p0.65_stc0-600 / prob54`: coverage 81.33%, min split +$0.96, all +$11.98, 5/5 days, 8/10 blocks. It likely avoids the 07:06 v50/v47 forward loss but does not beat v50 retrospectively.
- Added `probe_v53_weak_recross_thin_edge_combo_fv_strategy.py` to combine the v52 weak re-cross cap with the v50 thin-edge certainty cap. Best v53 row is `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75 / edge0_ask100_p0.65_stc0-600 / prob54`: coverage 81.33%, 332 trades, min split +$1.09, all +$12.31, 5/5 days, 8/10 blocks. This improves worst-split PnL versus v50 (+$1.09 vs +$0.99) but gives back all-market PnL (+$12.31 vs +$12.54) and worsens holdout calibration slightly.
- Added strict-forward v53 watcher:
  - `probe_v53_weak_recross_thin_edge_shadow_monitor.py`
  - `probe_v53_weak_recross_thin_edge_forward_denominator.py`
  - Fresh lock has 1 post-lock observed market, 0 registered rows, 0 finalized rows. It has no forward evidence yet.
- Updated `probe_current_fv_candidate_comparison.py` to include v52/v53. Current read: v50 remains best all-market PnL and holdout calibration; v53 is the best worst-split/risk-adjusted challenger; no candidate is promotion-ready.

03:40-03:43 EDT / 07:40-07:43 UTC latest forward refresh:

- Refreshed v47/v50/v53 after the 07:30 UTC market resolved.
- v50 improved from -$1.03 to -$0.87 fee+1c with 4 registered / 3 finalized and 100% coverage; the 07:24 YES at 90c settled YES for +16c fee+1c.
- v47 improved from -$1.38 to -$1.22 fee+1c with 6 registered / 5 finalized and 100% coverage.
- v53 now has 1 registered / 0 finalized, 100% coverage on a one-market denominator. First v53 row is `KXBTC15M-26MAY050345-45`, YES at 80c, p_side ~0.858, open until 07:45 UTC. No forward conclusion yet.
- Recompiled modified research scripts successfully. Process check shows no leftover probe/shadow/`python -` research process; live bot and passive recorder were not touched.

04:00-04:03 EDT / 08:00-08:03 UTC v55 book-anchor recross candidate:

- Added `probe_v55_book_anchor_recross_fv_strategy.py` to question the prior that a fair-value surface should keep extrapolating several cents past the book when the market is near strike and recent velocity is favorable. The physical read is that near-strike, moderate-momentum states can be recross-prone; the book may be carrying useful boundary-condition information that the FV surface should not ignore.
- Best v55 row: `v55_bookanchor_m10_v20_g05_book_plus2` / `edge0_ask100_p0.65_stc0-600` / `prob52`: min split coverage 81.33%, 333 trades, min split fee+1c-entry +$0.93, all fee+1c-entry +$13.36, 5/5 positive UTC days, 8/10 positive chronological blocks, holdout Brier/logloss 0.14176/0.42589.
- This makes v55 the current best retrospective all-market PnL row and the best holdout calibration row among the current high-coverage probability-clean candidates. v53 remains the best worst-split/risk-adjusted challenger at min split +$1.09.
- Added strict-forward setup for the exact v55 row:
  - `probe_v55_book_anchor_recross_shadow_monitor.py`
  - `probe_v55_book_anchor_recross_forward_denominator.py`
- Initial v55 strict-forward state has 1 post-lock observed market, 0 registered rows, and 0 finalized rows, so it is not promotion evidence. Latest consolidated comparison generated at `2026-05-05T08:02:33.103162+00:00`; `promotion_ready=False`.

04:07-04:25 EDT / 08:07-08:25 UTC forward refresh, v56 calibration branch, and v57 exit refinement:

- Refreshed strict-forward v47/v50/v53/v55. Current consolidated forward evidence remains promotion-fail:
  - v47: 7 registered / 7 finalized, 87.50% coverage, fee+1c-entry -$1.14.
  - v50: 6 registered / 5 finalized, 100.00% coverage, fee+1c-entry -$0.79.
  - v53: 3 registered / 2 finalized, 100.00% coverage, fee+1c-entry -$0.12.
  - v55: 1 registered / 0 finalized, 100.00% coverage, no finalized PnL.
- Forward failure diagnostics reinforced the near-strike boundary-condition idea. The 07:06 v50/v47 loss had selected-side margin 0.757 sigma, 3m selected-side velocity 0.1998 dps, model/book selected probability gap about 6.2 points, and book-selected probability below the ask. The 07:37 v53 loss had margin 0.998 sigma, selected-side velocity 0.389 dps, model/book gap about 6.3 points, and book-selected probability also below the ask.
- Added `probe_v56_book_edge_recross_fv_strategy.py` to test a stricter physical prior: near strike, if the book mid does not itself clear selected ask, model FV edge is extrapolation risk and should be anchored fully to book. Result: v56 improves holdout probability calibration to Brier/logloss 0.14129/0.42455, but it is not tradable under the robustness gate because best high-coverage v56 split PnL is negative (min split -$1.21, all +$10.25). This makes v56 a calibration clue, not a promotion candidate.
- Added `probe_v57_cross_surface_exit_strategy.py` to test whether the better-calibrated v56 surfaces are useful for exits while keeping profitable v50/v53/v55 entries. Cross-surface v56 exits did not dominate. The best row is instead v55 entry plus v55 exit with a 15-second minimum hold before `prob52`: `v57_v55_bookanchor_hold15_prob52`, coverage 81.33%, min split +$0.93, all fee+1c-entry +$13.60, 5/5 days, 8/10 blocks, 333 trades. This improves v55 all-market PnL from +$13.36 to +$13.60 without changing coverage or worst split.
- Patched research-only shadow plumbing in `probe_v42_latent_hole_book_shadow_monitor.py` to support optional `EXIT_MIN_HOLD_SECONDS` with default 0.0. Existing monitors behave unchanged unless a candidate opts in.
- Added strict-forward setup for v57:
  - `probe_v57_v55_hold15_shadow_monitor.py`
  - `probe_v57_v55_hold15_forward_denominator.py`
  Fresh v57 lock currently has 1 post-lock observed market, 0 registered rows, 0 finalized rows, and 0% coverage. This is not evidence yet.
- Updated `probe_current_fv_candidate_comparison.py` to include v56/v57. Latest comparison generated at `2026-05-05T08:25:18.129764+00:00`; `promotion_ready=False`. Current read: v57 is best retrospective all-market PnL; v53 remains best retrospective worst-split PnL; v56 is best holdout calibration but not tradable; all candidates still fail strict-forward sample/stability gates.

04:27-04:29 EDT / 08:27-08:29 UTC v55 first forward settlement:

- Refreshed v55 after the 08:15 UTC market resolved. v55 now has 2 registered / 1 finalized strict-forward rows, 100.00% coverage on 2 post-lock observed markets, and fee+1c-entry +$0.64.
- Finalized row: `KXBTC15M-26MAY050415-15`, YES at 65c, p_side 0.662, book_mid_p_yes 0.645, recross-side margin 0.500 sigma, recross-side velocity 0.067 dps, settled YES for +64c fee+1c-entry.
- Open row: `KXBTC15M-26MAY050430-30`, NO at 63c, p_side 0.651, book_mid_p_yes 0.375, recross-side margin 0.509 sigma, recross-side velocity -0.003 dps, open until 08:30 UTC.
- Rebuilt current comparison after this refresh; `promotion_ready=False`. The v55 first win is useful but still far below the forward gate of 50 finalized rows across at least 2 days.

04:32-04:35 EDT / 08:32-08:35 UTC v55 second forward settlement and v57 fresh-lock check:

- Refreshed after the 08:30 UTC close. v55 now has 2 registered / 2 finalized rows, fee+1c-entry +$1.32, but coverage fell to 2/3 observed post-lock markets (66.67%) because the new 08:45 UTC market has not produced an entry yet.
- Second finalized v55 row: `KXBTC15M-26MAY050430-30`, NO at 63c, p_side 0.651, book_mid_p_yes 0.375, recross-side margin 0.509 sigma, recross-side velocity -0.003 dps, settled NO for +68c fee+1c-entry.
- v57 fresh lock still has 0 registered rows across 2 post-lock observed markets. `KXBTC15M-26MAY050430-30` is classified as `latent_hole_shrunk_no_entry` after the v57 lock timestamp; `KXBTC15M-26MAY050445-45` is `no_entry_filters`.
- Rebuilt current comparison; `promotion_ready=False`. The positive v55 start is useful, but the strict-forward gate still fails both sample size and current tiny-window coverage.

04:36-04:54 EDT / 08:36-08:54 UTC v55/v57 live-forward coverage refresh:

- Rechecked the apparent v55 skip in `KXBTC15M-26MAY050445-45`. It was not a permanent skip; later heartbeats produced a valid v55 entry at `2026-05-05T08:40:25.268Z`: NO at 90c, p_side 0.914, edge 1.44c, 274.7 seconds to close.
- After settlement propagation, v55 now has 3 registered / 3 finalized strict-forward rows, 75.00% coverage on 4 post-lock observed markets, and fee+1c-entry +$1.48. The third row settled NO for +16c fee+1c-entry.
- v57 now has 2 registered / 1 finalized strict-forward rows, 66.67% coverage on 3 post-lock observed markets, and fee+1c-entry +$0.16. It registered the 08:40 NO 90c row and the new `KXBTC15M-26MAY050500-00` YES 88c row, which is still open.
- Rebuilt current comparison. `promotion_ready=False`: v55 is finally at the lower requested coverage edge in the tiny forward window and positive, but still only 3 finalized rows on 1 day. v57 remains too fresh and below forward coverage.

04:55-05:07 EDT / 08:55-09:07 UTC refreshed active forward branches:

- Refreshed v47/v50/v53 to keep the strict-forward comparison on the same live-log horizon:
  - v47: 11 registered / 10 finalized, 100.00% coverage, fee+1c-entry +$0.34.
  - v50: 9 registered / 8 finalized, 100.00% coverage, fee+1c-entry +$0.69.
  - v53: 6 registered / 5 finalized, 100.00% coverage, fee+1c-entry +$1.36.
- Refreshed v55/v57 after the 09:00 UTC market settlement:
  - v55: 4 registered / 4 finalized, 80.00% coverage on 5 observed post-lock markets, fee+1c-entry +$1.68. It is 4-for-4 in this tiny forward window.
  - v57: 2 registered / 2 finalized, 50.00% coverage on 4 observed post-lock markets, fee+1c-entry +$0.36.
- Rebuilt `probe_current_fv_candidate_comparison.py` read text because the prior "forward rows are negative" statement became stale. Current read: several refreshed strict-forward branches are now positive, led by v55, but the goal remains incomplete because the live-forward gate still needs 50+ finalized rows, at least 2 days, and stable 75-80%+ coverage.

05:08-05:12 EDT / 09:08-09:12 UTC open-market coverage update:

- The 09:15 UTC market initially looked like a v55/v57 coverage miss, but later heartbeats produced a qualifying entry at `2026-05-05T09:05:57.704Z`: NO at 90c, selected p_side about 0.914, edge about 1.40c, 542.3 seconds to close.
- v55 now has 5 registered rows across 5 post-lock observed markets, 100.00% coverage, 4 finalized wins, and one open row. Finalized fee+1c-entry remains +$1.68.
- v57 now has 3 registered rows across 4 post-lock observed markets, 75.00% coverage, 2 finalized wins, and one open row. Finalized fee+1c-entry remains +$0.36.
- Rebuilt the consolidated comparison. `promotion_ready=False`; the live-forward coverage requirement is currently being met by v55 and just met by v57, but the sample size/day gate remains the blocker.

05:17-05:22 EDT / 09:17-09:22 UTC v55/v57 09:15 settlement:

- The 09:15 UTC market settled as another v55/v57 win: `KXBTC15M-26MAY050515-15`, NO at 90c, p_side about 0.914, settled NO for +16c fee+1c-entry.
- v55 now has 5 registered / 5 finalized rows, 83.33% coverage on 6 post-lock observed markets, and fee+1c-entry +$1.84. It is 5-for-5 in the fresh strict-forward window.
- v57 now has 3 registered / 3 finalized rows, 60.00% coverage on 5 post-lock observed markets, and fee+1c-entry +$0.52. It is also 3-for-3, but below the coverage target because its lock started later and one post-lock market was latent-shrunk to no entry.
- Rebuilt current comparison. `promotion_ready=False`; positive forward PnL is no longer the blocker for v55, but sample size/day count remain far below the validation requirement.

05:22-05:36 EDT / 09:22-09:36 UTC one-shot refresh runner and 09:30 settlement:

- Added `probe_refresh_active_forward_candidates.py`, a research-only one-shot runner that refreshes v47/v50/v53/v55/v57 monitors and denominators serially, then rebuilds the consolidated comparison. It avoids parallel candle/cache writes and does not touch the live bot or orders.
- Ran the new refresh runner successfully. All 11 steps returned code 0 and it wrote `logs/edge_research/active_forward_refresh_latest.md`.
- The runner picked up `KXBTC15M-26MAY050530-30`: v55/v57 entered NO at 66c, p_side 0.717, edge 5.71c, 586.2 seconds to close. After settlement propagation it settled NO for +62c fee+1c-entry.
- v55 now has 6 registered / 6 finalized rows, 85.71% coverage on 7 post-lock observed markets, and fee+1c-entry +$2.46. It is 6-for-6 in the fresh forward window.
- v57 now has 4 registered / 4 finalized rows, 66.67% coverage on 6 post-lock observed markets, and fee+1c-entry +$1.14. It is 4-for-4 but below the requested coverage band.
- Rebuilt current comparison. `promotion_ready=False`; v55 now satisfies the requested forward coverage band in this tiny window, but still lacks sample size and multi-day validation.

05:36-05:51 EDT / 09:36-09:51 UTC 09:45 market late v55/v57 entry:

- Inspected the 09:45 UTC market while open. The closest early v55 state was NO p_side 0.645 with 1.5c edge after book-anchor shrink, just below the 0.65 entry floor, so no early entry was appropriate.
- Later heartbeats produced a valid but extremely late/high-ask v55/v57 entry at `2026-05-05T09:41:00.467Z`: NO at 98c, p_side 0.985, edge 0.46c, 239.5 seconds to close. It settled NO for +1c fee+1c-entry.
- v55 now has 7 registered / 7 finalized rows, 87.50% coverage on 8 post-lock observed markets, and fee+1c-entry +$2.47. It is 7-for-7 in the fresh strict-forward window.
- v57 now has 5 registered / 5 finalized rows, 71.43% coverage on 7 post-lock observed markets, and fee+1c-entry +$1.15. It remains below the requested coverage band.
- Rebuilt current comparison. `promotion_ready=False`. New watch item: v55 is winning the high-ask/tiny-edge late states so far, but the 98c entry only cleared by +1c after haircut; do not tighten or loosen until more of these appear.

05:52-06:24 EDT / 09:52-10:24 UTC v55/v57 false exit and v58 margin-gated exit candidate:

- The 10:00 UTC market `KXBTC15M-26MAY050600-00` exposed the most useful current failure mode. v55/v57 entered NO at 67c with selected p_side about 0.714 and later exited at 43c when NO-side p collapsed to about 0.414. The market ultimately resolved NO, so holding would have won. This was an exit false negative, not an entry-side error.
- Tested broad exit persistence in `probe_v58_v55_exit_persistence_refine.py`: global confirmation/dwell rules did not beat `hold15_prob52`. Example: `prob52_confirm2` dropped to all fee+1c +$11.33 and failed split/day robustness, versus v57-style `hold15_prob52` at +$13.60.
- Added conditional recross persistence to the same v58 probe. It produced some higher all-market rows, but the high-all confirmation rows failed split/day robustness. The useful physics clue was different: bad probability exits are often triggered while spot is still on the held side of the strike.
- Added and tested margin-gated exits in v58. Best row: `hold15_prob52_marginlte0p25`, which keeps v55 entry/FV unchanged and only allows probability exits after 15s when held-side spot margin is <= +0.25 sigma. Retrospective result: 81.33% min split coverage, +$0.57 min split fee+1c, +$20.45 all-market fee+1c, +$27.11 all-market fee, 5/5 positive days, 8/10 positive blocks, 333 trades. This is +$6.85 all-market fee+1c versus v57, but with a thinner holdout/min-split cushion (+$0.57 vs +$0.93), so it is not promotion-ready.
- Added strict-forward shadow setup for this candidate:
  - `probe_v58_v55_margin_exit_shadow_monitor.py`
  - `probe_v58_v55_margin_exit_forward_denominator.py`
  Fresh v58 lock intentionally registered 0 old markets and has 0 finalized rows. Future live websocket data must validate it from scratch.
- Updated `probe_current_fv_candidate_comparison.py` to include v58 and cap impossible stale-denominator coverage at 100% while retaining raw coverage in JSON. Latest comparison generated at `2026-05-05T10:24:05.847948+00:00`; `promotion_ready=False`. Current read: v58 is best retrospective all-market PnL, v53 remains best worst-split PnL, and no candidate satisfies strict-forward sample/day gates.
- Updated `probe_refresh_active_forward_candidates.py` so future active refresh runs include v58 shadow and denominator before rebuilding the consolidated comparison.
- Important correction after rechecking margin semantics: the high-PnL `marginlte0p25` v58 row is not a symmetric held-side margin law. The historical/live rows already carry side-relative margin, and the v58 transform multiplies by side sign, making it a YES-axis margin gate. A corrected held-side margin sweep was added to `probe_v58_v55_exit_persistence_refine.py`; its best robust rows improve some min-split cushions but do not beat v57 all-market PnL. Therefore v58 remains a speculative asymmetric market-structure candidate requiring strict-forward validation, not a clean physics promotion candidate.

06:25-06:36 EDT / 10:25-10:36 UTC v58 first fresh forward row:

- Replayed the 10:00 UTC false exit path through the v55 adjusted predictions. The v58 YES-axis margin gate would have skipped the original 09:55:01 exit at 43c because YES-axis margin was 0.265 sigma, just above the 0.25 ceiling, but it would have first triggered at 09:56:01 with bid 54c and margin 0.230 sigma. So v58 would have reduced that specific loss; it would not have held the trade all the way to the eventual NO settlement win. This is useful but weaker than the original story.
- Refreshed v58 after the 10:30 UTC market resolved. Fresh v58 lock now has 1 registered / 1 finalized row across 2 post-lock observed markets, 50.00% coverage, and fee+1c-entry +$0.66.
- First v58 forward row: `KXBTC15M-26MAY050630-30`, YES at 64c, p_side 0.652, edge 1.24c, settled YES for +66c fee+1c-entry. The next post-lock market `KXBTC15M-26MAY050645-45` currently has `no_entry_filters`, so coverage is below the 75-80% target in this tiny window.
- Rebuilt consolidated comparison; `promotion_ready=False`.

06:37-06:39 EDT / 10:37-10:39 UTC v58 overfit/concentration audit:

- Added `probe_v59_v58_asymmetry_audit.py` to compare v58 against v57-style `hold15_prob52` and the best symmetric held-side margin row.
- Result: v58's retrospective +$6.85 fee+1c delta versus v57 is highly concentrated. Only 8 markets have positive delta and 9 have negative delta; the top 5 positive-delta markets contribute +$7.67, which is 112% of the total net improvement. The largest positive deltas are mostly NO-side probability exits converted into settlement wins in train/validation, with holdout contribution thin.
- Side/split read: v58 improves NO-side fee+1c from +$4.47 to +$12.13, but YES-side drops from +$9.13 to +$8.32 and holdout drops from +$0.93 to +$0.57. This is not robust enough to promote. Keep v58 only as a strict-forward watched hypothesis.

06:49-06:56 EDT / 10:49-10:56 UTC v60 NO-side margin-gated forward lock:

- Created a separate strict-forward watcher for the current best retrospective exit variant instead of mutating the older v58 all-side watcher:
  - `probe_v60_v55_no_side_margin_exit_shadow_monitor.py`
  - `probe_v60_v55_no_side_margin_exit_forward_denominator.py`
- v60 policy: `v60_v55_bookanchor_hold15_prob52_noside_marginlte0p25_edge0_p65_stc0_600`. It keeps v55 entry/FV and v57 hold15/prob52 exit behavior for YES positions, but gates NO-position probability exits behind the YES-axis margin ceiling <= 0.25 sigma.
- Fresh lock created at `2026-05-05T10:49:23.268424+00:00`; it intentionally does not backfill. Current v60 strict-forward state: 0 registered / 0 finalized rows, 0.00% coverage across 1 post-lock observed market, fee+1c-entry $0.00.
- Updated `probe_refresh_active_forward_candidates.py` to refresh v60 and `probe_current_fv_candidate_comparison.py` to include v60 in the consolidated table.
- Rebuilt `current_fv_candidate_comparison_latest.md`. v60 is now the best retrospective all-market PnL row: 81.33% min split coverage, +$0.87 min split fee+1c, +$21.26 all-market fee+1c, 5/5 positive days, 8/10 positive blocks, 333 trades. It is not promotion-ready because strict-forward evidence is still absent.
- Current read remains unchanged at the goal level: the best upside candidate is v60, but the missing gate is still 50+ finalized strict-forward rows across at least 2 days with stable 75-80%+ coverage and positive fee+1c PnL.

06:57-07:04 EDT / 10:57-11:04 UTC v61 robustness compromise:

- Added `probe_v61_exit_robustness_audit.py` after mining the v58 exit sweep for less fragile alternatives to max-upside v60.
- Main challenger: `hold15_prob56_noside_marginlte0p25`. It keeps v55 entry/FV, raises the probability exit floor to 0.56, and applies the NO-side YES-axis margin gate. Retrospective result: 333 trades, 81.33% min split coverage, +$0.99 min split fee+1c, +$16.37 all-market fee+1c, 5/5 positive days, 8/10 positive blocks.
- Compared with v57 baseline `hold15_prob52`: v61-style compromise improves all-market fee+1c by +$2.77 and holdout/min-split by +$0.06. Compared with v60: it gives up $4.89 of all-market PnL but improves the holdout/min-split cushion from +$0.87 to +$0.99.
- Concentration read: v61 touches more markets than v60 (21 positive / 18 negative deltas vs baseline), but its top 5 positive deltas are still larger than total net delta because negative changes offset them. It is a robustness challenger, not a solved overfit issue.
- Added fresh strict-forward watcher and denominator:
  - `probe_v61_v55_no_side_prob56_margin_exit_shadow_monitor.py`
  - `probe_v61_v55_no_side_prob56_margin_exit_forward_denominator.py`
  Fresh lock created at `2026-05-05T11:00:45.760125+00:00`; current v61 state is 0 registered / 0 finalized rows, 0.00% coverage across 1 post-lock observed market, fee+1c-entry $0.00.
- Updated active refresh and consolidated comparison to track v61. `promotion_ready=False`; the strict-forward sample/day gate remains the blocker.

07:05-07:12 EDT / 11:05-11:12 UTC v62 diffusion-bridge FV probe:

- Added `probe_v62_diffusion_bridge_fv_strategy.py`, a research-only probability-surface test on top of v55. It blends near-strike v55 probabilities with a terminal diffusion prior based on YES-axis distance-to-strike, remaining seconds to close, and 15m realized-volatility units.
- Result: the diffusion prior improved holdout probability calibration but did not improve tradable PnL. Best holdout calibration row was `v62_diff_m100_t125_w25`: Brier 0.14096 and logloss 0.42418, better than v55's 0.14176 / 0.42589.
- The tradable strategy row for that best-calibration v62 surface failed: 84.00% min split coverage, -$0.23 min split fee+1c, +$4.00 all-market fee+1c, 4/5 positive days, 6/10 positive blocks, 342 trades.
- Best robust row in the v62 report was still the original v55 surface (`v55_bookanchor_m10_v20_g05_book_plus2`, edge0/p0.65/stc0-600/prob52): +$0.93 min split fee+1c and +$13.36 all-market fee+1c.
- Updated `probe_current_fv_candidate_comparison.py` to include `v62_diffusion_best_calibration_not_tradable`. Current consolidated read: v62 is the best holdout calibration candidate but not tradable; v60 remains best all-market PnL; no candidate is promotion-ready.

07:11-07:29 EDT / 11:11-11:29 UTC v60/v61 strict-forward refresh:

- Refreshed v60 and v61 strict-forward monitors/denominators using the live websocket-derived log.
- v60 now has 3 registered rows across 3 post-lock observed markets, 100.00% registered coverage, 2 finalized / 1 open, and fee+1c-entry -$0.43. The finalized rows are:
  - `KXBTC15M-26MAY050700-00`: NO at 97c, p_side 0.982, tiny edge 1.16c, exited at 45c for -$1.11 fee+1c-entry.
  - `KXBTC15M-26MAY050715-15`: YES at 63c, p_side 0.655, settled YES for +$0.68 fee+1c-entry.
  - `KXBTC15M-26MAY050730-30`: NO at 79c, p_side 0.805, open.
- Refreshed v57 for comparison. v57 took the same `KXBTC15M-26MAY050700-00` 97c NO exit loss, so this first v60 loss is inherited from the v55/v57 entry/FV state rather than introduced by the NO-side margin gate. v57 is now 11 registered / 11 finalized, 84.62% coverage, fee+1c-entry +$0.45.
- v61 now has 2 registered rows across 2 post-lock observed markets, 100.00% coverage, 1 finalized / 1 open, and fee+1c-entry +$0.68. Its positive read is not directly apples-to-apples with v60 because its lock started after the 11:00 UTC market that produced the 97c NO loss.
- Rebuilt `current_fv_candidate_comparison_latest.md`; `promotion_ready=False`. New watch item: expensive late high-confidence NO entries with tiny edge remain a real forward fragility. v60's retrospective edge still needs many more forward rows before it should be trusted.

07:30-07:32 EDT / 11:30-11:32 UTC v63 expensive-tail FV cap:

- Added `probe_v63_late_expensive_tail_fv_strategy.py` to test a model-side probability cap for high-ask, tiny-edge, late selected-side states. This directly targeted the fresh 97c NO / 1.16c-edge forward loss without adding an explicit entry veto.
- Retrospective result rejected the broad cap idea. Best robust row remained the unchanged v55 surface: +$0.93 min split fee+1c, +$13.36 all-market fee+1c, 81.33% min split coverage.
- v63 cap variants worsened holdout calibration and PnL. Example top v63 all-market row among 80%+ coverage variants: `v63_tail_a95_e250_s240_cap85`, edge-2/p0.65/prob54, 81.33% coverage, -$1.62 min split fee+1c, +$8.87 all-market fee+1c, 3/5 positive days, 5/10 positive blocks.
- Interpretation: the single fresh 97c NO failure is real, but a broad historical probability cap for expensive tiny-edge states is too blunt and over-blocks historically profitable tail states. Do not promote v63 or forward-track it.

07:33-07:36 EDT / 11:33-11:36 UTC v64 analog audit of the 97c NO loss:

- Added `probe_v64_forward_loss_analog_audit.py` to replay v55 entry with v57-style hold15/prob52 exit and slice historical analogs of `KXBTC15M-26MAY050700-00`.
- Historical analogs do not support a narrow veto. Under `NO_ask>=95_edge<=2_p>=95_stc120_450`, there were 18 historical trades, 18 settlement wins, 0 exits, and +$0.46 fee+1c-entry. Under the stricter `NO_ask>=97_edge<=1.5_p>=0.98_stc120_450`, there were 10 historical trades, 10 settlement wins, 0 exits, and +$0.06 fee+1c-entry.
- The fresh 11:00 UTC loss is therefore a rare path break, not a historically bad local entry class. The exit was helpful: the market ultimately went YES (`yes_bid=100` after close), so holding the NO 97c entry to settlement would have been worse than exiting at 45c.
- Interpretation: do not add a veto or cap from this one loss. The right next evidence is forward sample accumulation and possibly path-instability features, not a static high-ask/tiny-edge entry ban.

07:37-07:43 EDT / 11:37-11:43 UTC v65 exit-floor and path-instability audit:

- Refreshed strict-forward rows for v57/v60/v61 after the 11:30 UTC market resolved. v57 is now 13 registered / 12 finalized, 92.86% coverage, fee+1c-entry -$1.05. v60 is 4 registered / 3 finalized / 1 open, 100.00% coverage, fee+1c-entry -$2.06. v61 is 3 registered / 2 finalized / 1 open, 100.00% coverage, fee+1c-entry -$0.95. None pass promotion gates; v60/v61 remain especially suspect because their fresh sample is tiny and already negative.
- Added `probe_v65_exit_floor_path_instability_audit.py` to scan simple v55/v57 probability-collapse exit floors and diagnose adverse path motion without changing entry coverage.
- Exit-floor scan result: the existing v57-style `hold15_prob52` floor remains the best all-market retrospective row: 333 trades, 81.33% min split coverage, +$13.60 all-market fee+1c-entry, +$0.93 min-split fee+1c-entry. A 0.56 floor improves min split to +$1.13 but drops all-market fee+1c-entry to +$10.59; floors >=0.58 deteriorate quickly and floors >=0.62 are negative all-market.
- Path-instability read: v57-style probability exits lose -$53.10 fee+1c-entry on exited rows, but they add +$13.17 versus holding those same entries to settlement. Settlement-loser rows would be -$82.38 if held, versus -$40.89 with the exit, so the collapse exit is still doing useful loss-shaping.
- Historical high-ask/tiny-edge NO tails still do not support a static veto: `NO_tail_highask_tinyedge` has 18 trades, 18 wins, 0 exits, and +$0.46 fee+1c-entry in v65 as well.
- Current interpretation: do not replace v57's simple 0.52 exit floor based on retrospective data. v60/v61's NO-side margin gate remains an upside hypothesis, not a promotion candidate, because the latest forward row shows the gate can block a helpful exit and turn a v57 exit loss into a full settlement loss.

07:45-07:54 EDT / 11:45-11:54 UTC v66 NO-side book-gap FV surface:

- Mined v57-style entry-time diagnostics for causal features. The clearest asymmetric clue was selected-side model/book disagreement: `YES_gap_ge_05` had 26 trades, +$3.94 fee+1c-entry, while `NO_gap_ge_05` had 28 trades, -$1.94 fee+1c-entry. The stricter `NO_gap_ge_08` slice had 10 trades and -$1.58. This is causal at entry and not a scorer artifact.
- Added `probe_v66_no_bookgap_fv_strategy.py` to test an FV transform, not a veto: when selected side is NO and selected model probability exceeds selected-side book probability by a threshold, shrink the selected-side probability back toward the book.
- v66 result: it improves holdout calibration sharply but gives up all-market PnL. Best calibration/min-split row `v66_no_bookgap_g05_bookplus00` has 84.00% min split coverage, +$1.57 min-split fee+1c-entry, +$8.93 all-market fee+1c-entry, 5/5 positive days, 7/10 positive blocks, holdout Brier/logloss 0.13583/0.40894. Balanced row `v66_no_bookgap_g08_blend75` has 81.33% coverage, +$1.51 min split, +$11.45 all-market, 5/5 days, 8/10 blocks, holdout Brier/logloss 0.13705/0.41336.
- Updated `probe_current_fv_candidate_comparison.py` to include v66. Current consolidated read: v66 is now best holdout calibration and best retrospective min-split PnL, while v60 remains best all-market PnL. v66 is a robustness/calibration candidate, not the current profit leader.
- Added strict-forward watcher for the balanced v66 row:
  - `probe_v66_no_bookgap_balanced_shadow_monitor.py`
  - `probe_v66_no_bookgap_balanced_forward_denominator.py`
  Fresh lock has 0 post-lock observed markets / 0 registered rows so far; it must validate from scratch.
- Updated `probe_refresh_active_forward_candidates.py` so future active refreshes include v66 before rebuilding the consolidated comparison.

07:55-08:01 EDT / 11:55-12:01 UTC forward refresh and v66/v60 combination check:

- Tested whether v66's cleaner FV surface rescues the v60/v61 exit-gate upside. It does not. Under the fixed v55/v57 entry policy, v66 rows combined with NO-side margin exits land around +$11.67 to +$12.99 all-market fee+1c-entry, far below v60's +$21.26. So v60's high PnL remains exit-gate-specific, not explained by v66's model/book-gap correction.
- Refreshed v57/v60/v61/v66 forward monitors after the 11:45 UTC market resolved and the 12:00 UTC market opened. Current states in `current_fv_candidate_comparison_latest.md`:
  - v57: 14 registered / 13 finalized / 93.33% coverage / -$0.45 fee+1c-entry.
  - v60: 5 registered / 4 finalized / 100.00% coverage / -$1.46 fee+1c-entry.
  - v61: 4 registered / 3 finalized / 100.00% coverage / -$0.35 fee+1c-entry.
  - v66 balanced: 1 registered / 0 finalized / 100.00% coverage / $0.00 fee+1c-entry.
- Fresh v57/v60/v61 got a +$0.60 settled win on `KXBTC15M-26MAY050745-45`, but remain net negative forward because of the earlier 97c and 79c NO failures. v66 registered its first live-forward row on `KXBTC15M-26MAY050800-00`: NO 98c, p_side 0.981, edge 0.14c, open.

08:02-08:07 EDT / 12:02-12:07 UTC v67 ask-filter refinement and latest settlement:

- Tested a narrower v67 idea: only shrink large NO model/book gaps when selected ask is below 80/85/90/95c, preserving high-ask NO tails. It did not improve the frontier; the best all-market row remained unchanged v55/v57, and the best v67 rows reproduced the same tradeoff as v66. Do not promote or formalize v67 unless new forward evidence changes the diagnosis.
- Refreshed again after `KXBTC15M-26MAY050800-00` settled. It was a high-ask NO win:
  - v57: 14 registered / 14 finalized / 87.50% coverage / -$0.38 fee+1c-entry.
  - v60: 5 registered / 5 finalized / 83.33% coverage / -$1.39 fee+1c-entry.
  - v61: 4 registered / 4 finalized / 80.00% coverage / -$0.28 fee+1c-entry.
  - v66 balanced: 1 registered / 1 finalized / 50.00% coverage / +$0.01 fee+1c-entry.
- This supports the v64/v65 read that high-ask tiny-edge NO tails are not statically bad. The problem remains rare path breaks and exit handling, not a broad high-ask tail veto.
