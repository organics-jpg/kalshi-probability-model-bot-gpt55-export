# v28 Feature-Gate Live Adapter Snapshot

- Generated local: `2026-05-07 13:58 ET`
- Strategy tag: `mushroom_v28_feature_gate_raw05_recross60_abs085_size1_live`
- Storage tag: `live_mushroom_v28_feature_gate_size1`
- Live PID after repair: `9536`
- Health check: `OK | pid=9536 process=running heartbeat_age_min=0.19`

## Live Rule

This is the v28 boundary-clock feature-gate lane, using the frozen observable-entry rule:

- `raw_edge_prob >= 0.05`
- `recross_hazard_score <= 0.60`
- `abs_d_sigma >= 0.85`
- `position_size = 1`

The launcher sets `MUSHROOM_V28_MIN_P_SIDE=0.01` so cheap positive-edge contracts are not blocked by the base v28 `p_side >= 0.50` assumption.

## First Live Round Trip

Market: `KXBTC15M-26MAY071400-00`

- Entry: bought `NO`, qty `1`, at `8c`, `2026-05-07 13:55:25 ET`
- Feature evidence at entry: `p_side=0.134673`, `raw_edge_prob=0.054673`, `abs_d_sigma=1.069993`, `recross_hazard_score=0.158388`
- Exit: sold at `7c`, `2026-05-07 13:55:56 ET`
- Scored result: `-1c`, `-0.01 USD`, W/L by sign `0/1`

## Failure Classification

The first live trade exposed an exit-policy mismatch, not an entry-gate miss.

- Entry timing: acceptable according to the frozen feature gate; the entry was the intended cheap-edge shape.
- Execution/friction: one fill at `8c` after repeated IOC zero fills. The repeated zero-fill attempts were too aggressive.
- Exit-policy error: generic v28 probability-collapse exit sold at `7c` because absolute hold probability was low, even though the feature-gate lane intentionally buys cheap low-probability positive-edge contracts and the v28 fair hold was still above the entry basis.

## Repairs Applied

- Disabled generic probability-collapse exits for this live feature-gate launcher:
  - `MUSHROOM_V28_EXIT_REDUCE_P_HOLD_FLOOR=0.0`
  - `MUSHROOM_V28_EXIT_FULL_P_HOLD_FLOOR=0.0`
- Tightened fair-value drawdown exits for this lane:
  - `MUSHROOM_V28_EXIT_FAIR_DRAWDOWN_CENTS=4.0`
  - `MUSHROOM_V28_EXIT_FULL_DRAWDOWN_CENTS=7.0`
- Added zero-fill entry cooldown in `kalshi_btc15m_bot_ws.py` and set:
  - `LIVE_ENTRY_BLOCKED_SUPPRESSION_MS=2000`

## Follow-Up Check

- `2026-05-07 14:01 ET`: corrected live process still running as PID `9536`.
- The bot rolled from `KXBTC15M-26MAY071400-00` to `KXBTC15M-26MAY071415-15` cleanly.
- On the new market it has only emitted feature-gate/risk/depth rejections so far; no new filled trade after the repair yet.
- The first market later resolved `YES`; the live `NO` entry would have been a full loser if held to settlement, while the old generic exit realized `-1c`. This keeps the first trade classified as an entry/FV miss in outcome terms, with an exit-policy semantic mismatch still needing more evidence.
- `2026-05-07 14:02 ET`: patched the feature-gate watchdog `Start-Process` call to quote the launcher and source workspace paths. `-CheckOnly` now reports `OK | pid=9536 process=running heartbeat_age_min=0.00`; restart path is fixed syntactically but not force-tested while the live bot is healthy.

## Current Score

- Entries: `1`
- Completed round trips: `1`
- Net PnL: `-1c`
- W/L by sign: `0/1`
- Resolved markets: `1`
- Open positions: `0`

## Current Blockers

- The hidden watchdog start path reported `RESTART_FAILED`; foreground launcher starts correctly and health check passes afterward. Automation remains paused, but the watchdog launcher path should be repaired before unattended operation.
- Needs more live/frozen evidence after the exit repair; first round trip is diagnostic only and should not be used as proof of profitability.

## 2026-05-07 14:16 ET Update: Ask65 Variant Now Active

The no-ask-floor feature-gate lane was replaced with the stricter observable `ask65` variant after the first cheap-tail live trade showed the expected fragility.

- Active strategy tag: `mushroom_v28_feature_gate_raw05_recross60_abs085_ask65_size1_live`
- Active storage tag: `live_mushroom_v28_feature_gate_ask65_size1`
- Live PID: `4972`
- Health check: `OK | pid=4972 process=running heartbeat_age_min=0.14`
- Live score for active ask65 variant: entries `0`, round trips `0`, net `0c`, open positions `0`

The sidecar audit now separates the two live variants:

| variant | entries | round trips | W/L | net c | fills | order-like | live trade? |
|---|---:|---:|---:|---:|---:|---:|---|
| no ask floor | 1 | 1 | 0/1 | -1 | 1/1/2 | 96 | true |
| ask65 | 0 | 0 | 0/0 | 0 | 0/0/0 | 0 | false |

Active ask65 gate-rejection audit on `KXBTC15M-26MAY071415-15`:

- Feature rows observed: `84`
- Feature-gate passes: `0`
- Raw-edge pass rate: `34.52%`
- Recross pass rate: `85.71%`
- Abs-distance pass rate: `11.90%`
- Ask65 pass rate: `21.43%`
- Counterfactual no-ask passes: `3`, all `NO`
- Counterfactual ask55/ask60/ask65/ask70 passes: `0`

Interpretation: the current market did produce a few cheap no-ask opportunities, but none had the high-ask confidence profile. The active `ask65` lane is therefore blocking the same cheap/mid near-strike family that produced the first `-1c` no-ask trade. The immediate bottleneck is coverage/selectivity, not execution failure.

Current live-test classification:

- Source-quality repair: improved; active ask65 is designed to avoid the reconstructed/cheap-tail weakness.
- Entry timing/FV risk: still unresolved; no active ask65 fills yet.
- Exit-policy risk: unresolved for ask65; no active fills yet.
- Execution/friction risk: currently clean for ask65 because there have been no order-like events; old no-ask IOC spam is isolated to the retired variant.
- Promotion status: not promotable; live evidence is still zero filled ask65 trades and coverage remains below the long-term broad-market target.

## 2026-05-07 14:23 ET Update: Ask35 Frontier Watch

The clean coverage/source frontier now identifies a better watch candidate than active ask65:

- Watch rule: `raw03_recross60_abs85_ask35`
- Post-feature-freeze evidence: `52` settled, W/L `48/4`, net `+514c`
- Coverage: `63.41%`
- Reconstructed share: `13.46%`
- Full-loss cushion: `5`
- Blocker: `coverage_too_low`

Comparison:

| candidate | settled | W/L | coverage | net c | recon | cushion | blocker |
|---|---:|---:|---:|---:|---:|---:|---|
| active ask65 | 47 | 42/5 | 57.32% | 344 | 4.26% | 3 | coverage_too_low |
| watch ask35 | 52 | 48/4 | 63.41% | 514 | 13.46% | 5 | coverage_too_low |
| no-ask reference | 55 | 39/16 | 67.07% | 445 | 27.27% | 4 | coverage_too_low |

The expanded live gate audit now tracks `frontier_raw03_recross60_abs85_ask35` as a counterfactual. On the latest observed live stream, the current market produced:

- no-ask raw05 passes: `3`
- frontier ask35 passes: `0`
- frontier ask45 passes: `0`
- active ask65 passes: `0`

Interpretation: ask35 is the better research/watch branch because it improves PnL and coverage while keeping source quality clean. It is still not broad enough for promotion, and switching to it would not have created a live trade in the currently observed market window. The next bottleneck is explaining the omitted coverage rows, not simply lowering the active live threshold.
