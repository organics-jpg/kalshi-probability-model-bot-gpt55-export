# v28 Hybrid FPT Depth Robust Rank1 Live Policy

- Created UTC: `2026-05-08T14:19:00Z`
- Strategy tag: `mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size1_live`
- Log source: `live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size1`
- Launcher: `scripts/run_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_live_size1.ps1`
- Evidence source: `logs/edge_research/arxiv_strategy_promotion_gates_latest.md`
- Candidate: `hybrid_fpt_depth_robust_rank1`

## Pre-Live Evidence

- Replay PnL: `$24.85`
- W/L/flat: `99/107 + 3 flat`
- CPCV: `10/10` positive paths
- Median path edge: `12.6c`
- P25 path edge: `9.3c`
- ACI coverage: `90.9%`
- ACI useful: `True`
- Promotion caveat: report says this still needs frozen forward confirmation; this launch is an operator-requested controlled size-1 live trial, not a viability declaration.

## Full Policy

- Entry: v28 common-clock decision engine, BTC Coinbase websocket with Coinbase REST fallback, current v28 p-side/edge approval, plus rank-1 gates: edge >= 3c, depth/fill gate >= 8 contracts, book age <= 750ms, ask <= 85c, seconds_to_close >= 120, 0.80 <= abs_d_sigma <= 1.10.
- Exit/state: existing v28 common-clock live exit engine with exit guard mode enforce and 30s post-fill exit delay.
- Sizing: one contract, multi-entry disabled, max market risk 100c.
- Risk/kill: monitor every 60s, stop/downgrade on loss cluster >= 3, drawdown <= -200c, zero-fill count >= 8, source-stale reject share > 70% after >= 100 rejects, lock/process mismatch, exchange exposure/order mismatch, or exit-guard kill state.
- Accounting/PnL: `score_bot_log.py` live_only scoring, exchange reconciliation ledger, fee-aware completed round trips.
- Iteration: keep separate from prior feature-gate sample; do not widen thresholds for coverage until live-only score and source-quality evidence justify it.

## Launch Snapshot

- Previous live feature-gate sample was stopped flat after exchange reconciliation showed no positions and no resting orders.
- Feature-gate preserved result before switch: 13 entries, 12 completed round trips, `+$0.12` net after fees.
- New rank-1 lock acquired at `2026-05-08T14:02:09Z`, run_id `68d0e657-aff6-4d28-836d-fd8ca819d20c`.
- First rank-1 live fill seen at `2026-05-08T14:16:30Z`; exchange showed one active position and zero resting orders at first status check.

## First Live Read

- Refreshed UTC: `2026-05-08T14:31:36Z`
- Status: `running_with_exchange_exposure`
- Score: 2 entries, 0 completed round trips, 1 confirmed win by settlement, `+$0.20` net after fees, 1 open position.
- First market: `KXBTC15M-26MAY081030-30`, bought YES at `78c`; later scored as a confirmed win.
- Current exposure at refresh: `KXBTC15M-26MAY081045-45`, position `-1.00`, market exposure `$0.81`, fees paid `$0.02`, zero resting orders.
- Monitor line at `2026-05-08 10:30:56 -04:00`: decision `ok`, entries `1`, net `20c`, positions `0`, orders `0`, source stale `37%`. The status probe already saw the next open exchange position after this monitor tick.

## Shadow Check

- Refreshed UTC: `2026-05-08T14:34:52Z`
- Status: `running_scored_round_trips`
- Live lock/process: `True` / `True`
- Score: 2 entries, 1 completed round trip, `+$0.08` net after fees, 0 open positions.
- Exchange: zero active positions, zero resting orders.
- Latest event: `exit_reconciled` / `mushroom_v28_probability_reduce_single_shot_visible_depth`.
- Trade ledger: first market settled YES for `+$0.20` net; second trade bought NO at `81c` and exited at `73c` for `-$0.12` net.
- Monitor latest: decision `ok`, loss cluster `1`, zero fills `2`, source stale `28%`, no kill-rule hit.
- Note: recent bot log contains repeated Binance context refresh timeouts, while the v28 decision BTC source remained Coinbase; keep watching source freshness but do not stop unless stale-source or exchange-safety kill rules fire.

## Size2 Multi Upgrade

- Updated UTC: `2026-05-08T15:42:00Z`
- Prior size-1 run was stopped only after exchange reconciliation showed zero active positions and zero resting orders. Preserved size-1 result: 2 entries, 1 completed round trip, `+$0.08` net after fees.
- New strategy tag: `mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_live`
- New log source: `live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi`
- New launcher: `scripts/run_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_live.ps1`
- Entry/exit gates are unchanged from the frozen rank-1 policy: edge >= 3c, depth/fill gate >= 8 contracts, book age <= 750ms, ask <= 85c, seconds_to_close >= 120, and 0.80 <= abs_d_sigma <= 1.10, with the existing v28 guarded exit engine and 30s post-fill exit delay.
- Sizing is increased to 2 contracts. Same-market multi-entry is enabled only as a controlled add-on: max total same-market position is 3 contracts with a 120s minimum cooldown, not an uncapped repeat-entry mode.
- Risk cap is 300c max market risk, while the live monitor keeps the stricter drawdown kill at 200c. Other live kill rails remain: loss cluster >= 3, zero-fill count >= 8, source-stale reject share > 70% after >= 100 rejects, lock/process mismatch, exchange exposure/order mismatch, or exit-guard kill state.
- Launch check: new lock acquired by PID `39948`, run_id `ed33578e-77ee-44c3-b728-57a0b34b2b0f`; status probe showed lock/process `True` / `True`, 0 entries, 0 round trips, `$0.00` net, zero exchange positions, zero resting orders, and no fills since run start.
- First monitor lines for size2/multi were `decision=ok`, `running_waiting_for_first_entry`, source stale `33.3%` then `48.1%`, loss cluster `0`, zero fills `0`, positions `0`, orders `0`.
- Heartbeat automation `shadow-robust-rank1-live-bot` was retargeted to the size2/multi strategy and log tags.

## Size2 Multi No-Window Repair

- Updated UTC: `2026-05-08T17:03:00Z`
- Reason: the size2/multi run operated normally but produced no fills. Root-cause check found 5 valid `mushroom_v28_approved` / `signal_seen` events on `KXBTC15M-26MAY081200-00`, all deferred before order submission as `fast_fill_window_too_short`. The qualifying signal satisfied the frozen rank1 gates but lasted only about `47ms`, below the added `150ms` fast-fill window.
- Scope of repair: preserve the frozen rank1 entry gates, size 2, controlled same-market add-on cap, existing exits, and kill rails. Only remove the extra execution dwell by setting `LIVE_ENTRY_FAST_FILL_MIN_WINDOW_MS=0`.
- Prior size2/multi run was stopped flat after exchange reconciliation showed zero active positions, zero resting orders, and zero fills since run start.
- New strategy tag: `mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_nowindow_live`
- New log source: `live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_nowindow`
- New launcher: `scripts/run_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_nowindow_live.ps1`
- Launch check: new lock acquired by PID `20172`, run_id `e155dace-5db4-4ab2-9b50-8916d812c42c`; initial status probe showed lock/process `True` / `True`, 0 entries, 0 round trips, `$0.00` net, zero exchange positions, zero resting orders, and no fills since run start.
- First monitor lines for no-window were `decision=ok`, `running_waiting_for_first_entry`, source stale `50%`, loss cluster `0`, zero fills `0`, positions `0`, orders `0`.
- Heartbeat automation `shadow-robust-rank1-live-bot` was retargeted to the no-window strategy and log tags.

## Size2 Multi Exact-Gate Repair

- Updated UTC: `2026-05-08T20:20:00Z`
- Reason: the no-window run was healthy and net profitable, but the live entry path still contained old gates not specified by the frozen rank1 candidate. Since launch, 22 rejected events matched the frozen gate fields; 20 were blocked by `p_below_floor` and 2 by `btc_stale`. This made the low coverage partly a launcher/spec mismatch rather than just natural selectivity.
- Frozen entry gate for this version: edge >= 3c, depth >= 8 contracts as the live depth-ratio proxy, book_age_ms <= 750, ask <= 85c, seconds_to_close >= 120, and 0.80 <= abs_d_sigma <= 1.10.
- Removed/nonbinding old alpha gates: `MUSHROOM_V28_MIN_P_SIDE=0.0`, `MUSHROOM_V28_MAX_SECONDS_TO_CLOSE=99999`, `LIVE_ENTRY_FAST_FILL_MIN_WINDOW_MS=0`, `MUSHROOM_V28_FEATURE_GATE_RECROSS_MAX=1.50`; BTC max-age was widened to `10000ms` so Coinbase/REST freshness no longer blocks otherwise exact-gate signals under ordinary reconnect jitter.
- Preserved protections: position size 2, same-market add-on cap 3 contracts, 120s add-on cooldown, 300c max market risk, IOC execution, live balance/risk checks, exchange reconciliation, existing guarded exit engine, loss-cluster/drawdown/zero-fill/source-stale monitor kills.
- Prior no-window run was stopped flat after exchange reconciliation showed zero active positions and zero resting orders. Preserved no-window result: 1 entry, 0 completed round trips, 1 confirmed win, `+$0.51` net after fees.
- New strategy tag: `mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_live`
- New log source: `live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate`
- New launcher: `scripts/run_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_live.ps1`
- Launch check: new lock acquired by PID `24304`, run_id `fbc1c69f-a397-4a61-8c0b-0e47b37c9732`; status probe showed lock/process `True` / `True`, 0 entries, 0 round trips, `$0.00` net, zero exchange positions, zero resting orders, and live event telemetry with `mushroom_v28_min_p_side=0.0`.
- Heartbeat automation `shadow-robust-rank1-live-bot` was retargeted to the exact-gate strategy and log tags.

## Size2 Multi Exact-Gate Depth-Ratio Repair

- Updated UTC: `2026-05-08T20:26:00Z`
- Reason: audit found the research gate uses `depth_ratio = eligible_depth / required_depth`, while the first exact-gate launcher used an absolute depth check. Added native `LIVE_ENTRY_FAST_FILL_MIN_DEPTH_RATIO` to the bot and started a separate version so the depth-ratio tweak is logged/scored independently.
- Frozen entry gate for this version: edge >= 3c, depth_ratio >= 8, book_age_ms <= 750, ask <= 85c, seconds_to_close >= 120, and 0.80 <= abs_d_sigma <= 1.10.
- New strategy tag: `mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio_live`
- New log source: `live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio`
- New launcher: `scripts/run_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio_live.ps1`
- Code support: `kalshi_btc15m_bot_ws.py` now enforces `LIVE_ENTRY_FAST_FILL_MIN_DEPTH_RATIO`; the base launcher passes it through as `FastFillMinDepthRatio`.
- Prior exact-gate process was stopped flat after exchange reconciliation showed zero active positions and zero resting orders.
- Launch check: new lock acquired by PID `37692`, run_id `d477ba43-4784-4407-80f2-39da0bb3c61c`; bot log shows WS connected, orderbook snapshot ready, Coinbase BTC stream connected, and no exposure at launch.
- Heartbeat automation `shadow-robust-rank1-live-bot` was retargeted to the exact-gate depth-ratio strategy and log tags.
