# v28 Overnight Research Update

Research-only; no live bot logic changes and no candidate orders.

- Generated UTC: `2026-05-07T11:30:02Z`
- Live baseline: `live_mushroom_v28_size2`, `+821c / +$8.21`
- Live entries: `569`
- Live completed round trips: `469`
- Live W/L by sign: `263/298`
- Open live positions: `1`
- Controlled live-test gate: `no_live_test`
- Broad eligible candidates: `0`
- Sidecar eligible candidates: `0`

## Top Stack

The current best diagnostic branch is now:

1. `top_component_mix_portfolio / rescue_drop15_plus_absd_parent_fill_to75`
   - Base mix: soft-frontier delayed-recheck rescue plus abs-d ranked parent fill to 75% coverage.
   - Diagnostic: `+1539.5c`, `56/10`, `75.00%` coverage, `31.8%` reconstructed/rejected share.

2. `top_component_false_negative_rescue_child / diagnostic_approved_union_rebound`
   - Repairs three approved-entry missed exit rescues.
   - Diagnostic: `+1961.5c`, `59/7`, `75.00%` coverage, `31.8%` reconstructed/rejected share.

3. `top_component_parent_fill_repair_child / diagnostic_observable_mid_confidence_parent_fill_quarter`
   - Adds observable-only quarter sizing for the remaining parent-fill mid-confidence pocket.
   - Diagnostic: `+2012.5c`, `59/7`, `75.00%` coverage, `31.8%` reconstructed/rejected share.
   - Current best top-row delta versus refreshed live baseline: `+1191.5c`.

4. `top_component_observable_quarantine_child / weak_touch_zero`
   - New watch-only child frozen at `2026-05-07T11:23:30.150645+00:00`.
   - It tests a source-free low-ask/weak-boundary quarantine for the strict parent-fill loss pocket.
   - Autopsy context: turns the tiny 5-row strict context from `-54c`, `3/2` into `+52c`, `3/0`, but drops coverage to `60%`.
   - Diagnostic parent rows: zeroing weak-touch rows costs coverage, so this is a failure-mechanism watch, not a broad replacement.
   - Own strict post-birth rows: `0`.

## Original Feature-Gate Branch

The boundary-clock feature-gate branch from the handoff has now collected strict post-freeze rows, but remains below promotion shape:

- Best strict entry/bridge row: `post_feature_freeze_entry_raw05_recross60_abs085` / `post_feature_freeze_bridge_raw05_recross60_abs085`
- Settled: `35/36` entry/bridge context, depending lane
- W/L: `23/12` entry raw05 context
- Coverage: `62.50%`
- Net: about `+299c` entry raw05 and `+315c` bridge raw05
- Reconstructed/rejected share: about `34.29-36.11%`
- Full-loss cushion: `3`
- Blocker: `coverage_too_low`
- It also does not beat the refreshed live-only baseline of `+821c`.

## Top PnL + Top Win Mix

The refreshed dual-lane overlap probe now includes the latest top-component stack.

- Best diagnostic union that stays under the reconstructed-share line: `top_component_mix_portfolio / rescue_drop15_plus_ask_parent_fill_to75` plus `post_penalty_birth_entry_cheap_penalty025_rank_only`
  - `68` entries, W/L `56/12`, coverage `77.27%`, net `+1470.5c`, reconstructed share `33.82%`
  - Still blocked by `needs_own_frozen_forward_birth` and `live_ready_false`.
- The true top parent-fill child plus the high-win sidecar is worse as a promotion shape:
  - `70` entries, W/L `59/11`, net about `+1993.5c`, reconstructed share `35.71%`
  - It crosses the source-quality limit, and the sidecar adds `-19c` of non-overlap rows.
- Read: the high-win sidecar does not currently strengthen the top PnL branch; it mostly adds losing non-overlap rows and can break the source gate.
- As a confirmation/veto filter, the high-win lane is cleaner but too narrow:
  - Best diagnostic confirmation keeps `41` top parent-fill rows, W/L `35/6`, net `+1104.5c`, reconstructed share `34.1%`
  - Coverage falls to `46.59%`, while omitted top-stack rows still net `+908c`
  - Read: useful as a future narrow sidecar diagnostic, not a broad v28 replacement.

## Evidence Discipline

- The source-label parent-fill variants are explicitly blocked with `source_label_diagnostic`.
- The best ranked row is now the observable-only parent-fill rule, not the source-label shortcut.
- Strict scoreable rows from the parent-fill child freeze are `2`.
- Current strict post-freeze score: `+24c`, W/L `2/0`, coverage `50.00%`.
- Rows still needed for the sample gate: `28`.
- Strict net still needed to beat refreshed live baseline: `+797c`.
- Strict net still needed for a three-full-loss cushion: `+276c`.
- Strict runway from the parent-fill child freeze:
  - Future denominator: `4`
  - Future observation rows: `37`
  - Broad pass rows: `3`
  - Selected parent rows: `2`
  - Settled selected rows: `2`
  - Pending selected rows: `0`
  - Settled selected rows with exit-clock join: `0`

## Why No Live Test Yet

The top diagnostic stack clears the broad-shape desiderata historically/diagnostically, but it fails the actual promotion gates:

- `live_ready_false`
- `not_strict_forward`
- `diagnostic_prefreeze`
- only two settled parent-fill child scoreable rows so far
- zero settled observable-quarantine child post-birth rows so far

The controlled gate remains `no_live_test` with open live positions at `1`, because the strict-forward and live-readiness gates still fail.

## Current Failure Map

- Exit-policy error: approved-entry false-negative exits remain the cleanest repaired mechanism.
- Source-quality error: parent-fill rows still depend on reconstructed/rejected evidence, though within the 35% row-share threshold diagnostically.
- Entry/FV error: remaining true losers and parent-fill losses are not fixed by broad holding.
- Fragility: diagnostic cushion is high, but promotion cushion is zero until strict rows settle.

## Next Watch

Track the parent-fill repair child from `2026-05-07T10:29:46.104521+00:00`.

Promotion discussion should stay blocked until the strict child variants have:

- `>=30` settled post-child rows
- `75-90%` broad coverage
- `<=35%` reconstructed/rejected row share
- positive PnL after fees
- full-loss cushion `>=3`
- refreshed live-baseline win
- controlled live-test gate eligible
