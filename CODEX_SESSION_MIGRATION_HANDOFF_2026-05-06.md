# Codex Session Migration Handoff - 2026-05-06

Workspace:
`C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT`

This handoff exists because the prior Codex session became extremely long and unstable. Use this file to resume the active goal in a fresh session without relying on chat history.

## Read First

Active objective:

Improve the v28-based BTC 15-minute Kalshi strategy into a physics-backed, evidence-disciplined strategy with durable positive risk-adjusted ROI. The strategy should preserve broad market participation where possible, roughly 75-80%+ of recurring BTC 15m markets, but durable ROI and account survival override coverage.

Current status:

- Goal is **not achieved**.
- Work is currently **research-only**.
- Do **not** change live bot logic.
- Do **not** stop/restart the live bot unless the user explicitly asks.
- Do **not** place live trades from candidates while live readiness is false.
- Do **not** delete logs, research outputs, candidate ledgers, or tracking files.
- Treat old logs as diagnostic. Promotion needs fresh/frozen forward evidence.

Current best direction:

1. Validate exit/state improvements first.
2. Track hybrid confidence-shrink as the lead FV calibration overlay, but do not promote it yet.
3. Keep early-NO boundary-decay repair and boundary-clock/entry-bridge families under watch as broad-entry candidates.
4. Treat book probability as a regime/disagreement feature, not a global FV anchor.
5. Treat phi forgetting as a useful shrink-control idea, not the lead mechanism.

## Key Commands For New Session

From PowerShell:

```powershell
cd "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT"
```

Quick refresh of the central scorecards:

```powershell
python .\probe_v28_goal_completion_audit.py
python .\probe_v28_current_direction_decision.py
python .\probe_v28_target_hybrid_veto_repair.py
```

Read the current state:

```powershell
Get-Content .\logs\edge_research\v28_goal_completion_audit_latest.md -TotalCount 260
Get-Content .\logs\edge_research\v28_current_direction_decision_latest.md -TotalCount 180
Get-Content .\logs\edge_research\v28_target_hybrid_veto_repair_latest.md -TotalCount 220
```

Check the research loop log:

```powershell
Get-Content .\logs\shadow_mushroom_v28_reactivation_size2\status_loop.log -Tail 40
```

Start the research/shadow status loop if the user asks for it or if no current loop is running:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\run_v28_shadow_status_loop.ps1" -IntervalSeconds 60
```

Run it in a separate hidden process only if needed:

```powershell
Start-Process powershell -WindowStyle Hidden -ArgumentList @(
  "-ExecutionPolicy", "Bypass",
  "-File", "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\scripts\run_v28_shadow_status_loop.ps1",
  "-IntervalSeconds", "60"
)
```

If checking whether the loop is running:

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -like "*run_v28_shadow_status_loop.ps1*" } |
  Select-Object ProcessId, ParentProcessId, CommandLine
```

## Current Audit Snapshot

From `logs\edge_research\v28_goal_completion_audit_latest.md`:

- Achieved: `False`
- Objective: physics-backed profitable FV model/strategy, broad 75-80% BTC 15m coverage, no overfit, verified by forward/live evidence.
- Target-coverage surface:
  - `44` settled rows.
  - Coverage about `69.84%`, below the target floor.
  - Net `-755c`, not profitable.
  - Best target overlay: `boundary_recross_shrink_probability`.
  - Brier/logloss deltas versus raw: about `-0.0175 / -0.0390`.
- Calibration has improved, but PnL and coverage still fail.
- Live-evidence quality still fails:
  - Approved-entry rows: `2`.
  - Simulated/rejected share: about `95%`.
- Candidate integrity still fails:
  - `5` positive target-coverage lanes.
  - `0` integrity-pass lanes.
  - Common blockers: insufficient settled rows, reconstructed/share quality, full-loss fragility.
- Live readiness gate is false.

Do not call the goal complete unless the audit actually passes all material gates.

## Current Direction Ledger

From `logs\edge_research\v28_current_direction_decision_latest.md`:

### Exit Policy

Candidate:
`reduce_geometry_plus_collapse_drawdown_lte_12`

Evidence:

- Frozen reduce-suppression has `61` settled rows.
- Delta versus current exits: `+417c`.
- Frozen FV bridge plus reduce/collapse exit combo has `0` approved-only settled rows so far.

Action:

Keep monitoring forward rows. Do not promote from diagnostic-only rows.

### FV Calibration

Candidate:
`hybrid_confidence_shrink`

Evidence:

- Diagnostic best hybrid overlay improved Brier/logloss:
  - Brier delta about `-0.003156`.
  - Logloss delta about `-0.006463`.
- Fresh frozen forward rows for the hybrid overlay are still `0`.
- On the target surface, hybrid improves calibration but the selected rows still lose money.

Action:

Track as an FV calibration overlay. Do not use it as an entry selector until forward evidence matures.

### Entry Policy

Candidate:
`skip_early_no_boundary_decay_repair_calm_geometry`

Evidence:

- `17` settled.
- Coverage `75%`.
- Net `+134c`.
- Target comparison net around `-206c`.
- Blocker: `settled_lt_30`.
- Warnings: source quality/reconstructed rows and small sample.

Action:

Monitor, do not promote. Needs at least 30 settled and better approved-entry/source-quality proof.

### Book Anchor

Decision:

Downgrade to regime feature.

Evidence:

- Book can help logloss in some slices, but raw v28 dominates important approved-entry future slices.

Action:

Use book as disagreement/regime context, not a global FV anchor.

### Phi Forgetting

Decision:

Monitor as control.

Evidence:

- Phi half/quarter shrink supports the general "forget confidence toward 50" idea.
- It does not currently beat noise/hybrid shrink as the lead mechanism.

## Newest Work Completed Before Migration

Created:

`probe_v28_target_hybrid_veto_repair.py`

Outputs:

- `logs\edge_research\v28_target_hybrid_veto_repair_latest.md`
- `logs\edge_research\v28_target_hybrid_veto_repair_latest.json`
- `logs\edge_research\v28_target_hybrid_veto_repair_state.json`

Purpose:

The target surface has a bad cluster where raw v28 says the ask is favorable, but the hybrid confidence-shrink FV says fair value is below the ask. That means raw edge may be a false edge in noisy boundary conditions. The probe tests whether those rows can be skipped and replaced with cleaner missed-market rows while preserving 75% coverage.

Important result:

- Diagnostic window target net: `-755c`.
- Hybrid-veto cluster: `13` settled, net `-518c`.
- Best diagnostic repair:
  - `skip_all_hybrid_vetoes_raw_clean_repair`
  - Coverage `75%`.
  - Net `-203c`.
  - Delta versus target `+552c`.
  - Still blocked by `net_not_positive`.
- Post-repair-freeze window has `0` rows so far.

Interpretation:

The hybrid-veto idea is useful as a loss-cluster detector, but not sufficient. It cuts a large part of the loss, yet does not make the broad target surface profitable. It should be kept as a warning feature or part of a larger repair stack, not treated as solved alpha.

Next implementation step:

Wire `probe_v28_target_hybrid_veto_repair.py` into:

1. `scripts\run_v28_shadow_status_loop.ps1`
2. `probe_v28_goal_completion_audit.py`
3. `probe_v28_current_direction_decision.py`

Only do this if the new session is continuing research. This does not touch live trading logic.

## Candidate Families To Keep Tracking

Highest-priority families:

- `reduce_geometry_plus_collapse_drawdown_lte_12`
- `hybrid_confidence_shrink`
- `skip_early_no_boundary_decay_repair_calm_geometry`
- `boundary_clock_repair_entry`
- `boundary_clock_fv_entry_bridge`
- `p50_book_edge_entry` and book-plus variants, but watch coverage-too-high and book-overfit risk
- `target_hybrid_veto_repair`

Candidates with positive but not yet sufficient forward evidence from the audit:

- Frozen early NO boundary-decay repair:
  - `18` entries, `17` settled, `75%` coverage, `+134c`.
- Frozen p50 book-edge entry:
  - `25` entries, `24` settled, `89.29%` coverage, `+82c`.
- Frozen book-plus-5pp entry:
  - `25` entries, `24` settled, `92.59%` coverage, `+82c`.
- Frozen book-plus-5pp no-cheap-YES:
  - `25` entries, `24` settled, `96.15%` coverage, `+82c`.
- Frozen boundary-clock repair entry:
  - `24` entries, `24` settled, `77.42%` coverage, `+108c`.
- Frozen boundary-clock FV entry bridge:
  - `22` entries, `22` settled, `75.86%` coverage, `+114c`.

Do not promote any candidate just because it is green. Run integrity/source-quality/full-loss checks first.

## Research Principles To Preserve

- Start from v28, not v55/v60.
- Improve the full stack: exits/state first, entries second, FV third.
- Require a physical market argument plus forward evidence.
- Do not pick the best historical PnL row.
- Prefer continuous confidence penalties over brittle cutoffs unless the physical mechanism is strong.
- Classify failures into:
  - FV error
  - entry timing error
  - exit-policy error
  - execution error
  - market-regime error
- Score progress by:
  - net PnL
  - account ROI
  - max drawdown
  - loss clusters
  - trade count
  - market coverage
  - execution quality
  - FV calibration by bucket

## User Preferences And Safety Constraints

The user wants autonomous progress and fewer permission asks for harmless research. Still, preserve these constraints:

- No live candidate trades unless the user explicitly asks in the new session and readiness/risk is reviewed.
- No deletion of research logs or candidate tracking files.
- No live bot restarts unless explicitly requested or a health task requires it.
- Quiet, material updates are preferred.
- Plain-English summaries first, then evidence.
- The user cares deeply about the tracking ledger: PnL, wins/losses, coverage, and candidate comparisons must be preserved.

## Files Most Likely Needed

Core loop:

- `scripts\run_v28_shadow_status_loop.ps1`

Central status:

- `probe_v28_goal_completion_audit.py`
- `probe_v28_current_direction_decision.py`
- `probe_v28_live_trade_readiness.py`
- `probe_v28_candidate_integrity_scorecard.py`
- `probe_v28_candidate_pnl_tracker.py`
- `probe_v28_frozen_candidate_leaderboard.py`

Current FV/research files:

- `probe_v28_hybrid_confidence_shrink_fv.py`
- `probe_v28_confidence_shrink_schedule_bakeoff.py`
- `probe_v28_phi_forgetting_fv_candidates.py`
- `probe_v28_target_surface_hybrid_fv.py`
- `probe_v28_target_hybrid_veto_repair.py`
- `probe_v28_target_coverage_fv_overlay_validator.py`
- `probe_v28_target_coverage_fv_sequential_evidence.py`

Entry/repair files:

- `probe_v28_frozen_early_no_boundary_decay_repair_entry.py`
- `probe_v28_early_no_boundary_decay_repair_stress.py`
- `probe_v28_frozen_boundary_clock_repair_entry.py`
- `probe_v28_frozen_boundary_clock_fv_entry_bridge.py`
- `probe_v28_frozen_p50_book_edge_entry.py`
- `probe_v28_frozen_book_plus05_entry.py`
- `probe_v28_frozen_book_plus05_no_cheap_yes_entry.py`

Exit files:

- `probe_v28_frozen_exit_reduce_suppression.py`
- `probe_v28_exit_reduce_geometry_suppression.py`
- `probe_v28_frozen_fv_bridge_exit_combo_stack.py`
- `probe_v28_fv_bridge_exit_combo_bakeoff.py`

## Suggested First Tasks In New Session

1. Read this handoff.
2. Run the quick refresh commands.
3. Check whether the research loop is still running.
4. Wire `probe_v28_target_hybrid_veto_repair.py` into the loop/audit/direction ledger.
5. Re-run:

```powershell
python -m py_compile .\probe_v28_target_hybrid_veto_repair.py
python .\probe_v28_target_hybrid_veto_repair.py
python .\probe_v28_goal_completion_audit.py
python .\probe_v28_current_direction_decision.py
```

6. Continue from the current research question:

Can hybrid-veto warning + boundary/clock/early-NO repair be combined into a broad 75-80% coverage candidate that is positive on frozen forward rows and passes source-quality/full-loss integrity?

If yes, freeze it. If no, reject it and keep the useful features as diagnostics.

## Exact Prompt User Can Paste Into New Session

```text
We are migrating from a very long Codex session. Please read:
C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\CODEX_SESSION_MIGRATION_HANDOFF_2026-05-06.md

Then continue the v28 long-term goal from there. Keep it research-only unless I explicitly say otherwise. Do not delete logs or candidate tracking. Do not change live bot logic or place trades. First refresh the current scorecards, check whether the shadow/research loop is running, then continue from the target hybrid-veto repair / boundary-clock / early-NO repair direction.
```

