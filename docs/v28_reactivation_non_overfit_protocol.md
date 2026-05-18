# v28 Reactivation Non-Overfit Protocol

## Goal

Improve the original v28-style BTC 15m strategy without repeating the v55/v60 mistake of selecting the best historical row after many probes.

Primary target: durable risk-adjusted ROI over time. The standing operating mandate is now tracked in `docs/v28_long_term_operating_goal.md`.

Current working posture:

- Run v28 in dry-run shadow under `shadow_mushroom_v28_reactivation_size2`.
- Keep the live order path untouched while we collect fresh forward evidence.
- Treat prior audits as diagnostics, not proof.
- Promote only mechanisms that make market sense before they are scored.

## Baseline To Preserve

v28 was not just an FV model. Its useful behavior came from the whole stack:

- Selective high-confidence entries.
- IOC-at-executable-ask discipline.
- BTC tick freshness and book trust gates.
- Exit/state handling that reduced passive hold damage.
- A fair-value exit branch that often sold when market bid exceeded model hold value.

The strongest prior fact is that v28 exits added value versus passive holding, even while many individual exits were hurtful. The weak branch was `mushroom_v28_probability_collapse_full`.

## Anti-Overfit Rules

1. Freeze each hypothesis before scoring future rows.
2. Do not rank many variants by historical P&L.
3. Require every candidate to have a physical argument before any numeric test.
4. Use forward shadow rows as the main evidence.
5. Score with real execution assumptions: IOC, visible depth, stale ticks, fees, and fill price.
6. Keep a candidate broad enough to preserve most of v28's natural trade stream unless the reason to narrow is overwhelming.
7. Never call a rule proven because it improves one historical split or one small branch sample.

## Hypothesis Queue

### H1: BTC Freshness As Information Quality

Physical argument: v28's FV is highly sensitive near the strike. A stale BTC tick can make the model believe the terminal geometry is favorable after the actual underlying has already moved.

Candidate behavior:

- Entry guard: skip if BTC tick age is too stale.
- Exit guard: do not fire soft model exits on stale BTC ticks unless the book itself has already repriced deeply against the position.

Forward proof required:

- Freshly registered shadow rows.
- Positive net delta versus baseline entries/exits.
- No evidence that the guard mostly removes winners.

### H2: Crowded-Depth / Book-Saturation Guard

Physical argument: unusually large visible executable depth can mean the market is inviting takers into a stale or one-sided quote, not offering free edge. The old audit showed `eligible_depth > 1300` was a loss pocket, but this is suspicious because depth is easy to overfit.

Candidate behavior:

- Do not immediately live-promote.
- Forward-shadow as a crowding/regime feature.
- Prefer a continuous penalty in FV confidence over a hard cutoff if it survives.

Forward proof required:

- Confirm with new v28 shadow rows only.
- Check whether the same effect appears across both YES and NO, and across multiple sessions.

### H3: Probability-Collapse Exit Turbulence Filter

Physical argument: a full probability-collapse exit is suspect when terminal sigma is still high and model fair-value drawdown is shallow. That state can be path turbulence rather than terminal truth.

Candidate behavior:

- Keep `exit_value_over_hold`.
- Keep strong defensive exits when fair drawdown is genuinely deep.
- Shadow-suppress only the `probability_collapse_full` branch when sigma remains high and fair drawdown is not yet deep.

Forward proof required:

- Registered collapse-branch rows only.
- Compare actual exit versus hold-to-settlement.
- Require more than a tiny branch sample before promotion.

### H4: Recross Hazard Instead Of Static Probability

Physical argument: BTC 15m markets are barrier-like near the strike. The key risk is not just terminal probability; it is whether price is likely to recross the strike before close and force a sharp contract repricing.

Candidate FV argument:

- Add a recross hazard term based on distance-to-strike in sigma units, signed velocity, short-horizon realized volatility, and time remaining.
- Penalize high-confidence FV when the side is favorable but close enough to strike that one ordinary impulse can flip the book.

Forward proof required:

- Calibration improvement first: better Brier/logloss on fresh probability rows.
- Then P&L shadow improvement.
- No direct optimization of exact cutoff values.

### H5: Venue-Consensus Spot Reliability

Physical argument: the contract settles from a reference BTC price, while v28 often consumes a single fast spot feed. If Coinbase/Binance or trade/book feeds disagree during bursts, FV can be right for the wrong venue.

Candidate FV argument:

- Track Coinbase trade, Binance US trade/book, and Kalshi implied book midpoint.
- Penalize FV confidence when spot feeds diverge or when Kalshi book is moving before spot catches up.

Forward proof required:

- First prove the feature predicts FV error direction, not just P&L.
- Then shadow entries with the reliability penalty.

### H6: Recross Hazard

Physical argument: BTC 15m markets are path-sensitive near the strike. A side can have a high terminal probability while still being vulnerable to one ordinary recross impulse that reprices the contract before close and triggers bad exits or scratch exits.

Candidate behavior:

- Track a continuous recross hazard score from absolute distance-to-strike in sigma units, time remaining, and terminal sigma.
- Use this first as a calibration and exit-policy diagnostic, not an entry cutoff.
- If it survives forward evidence, prefer using it to temper exit aggressiveness or confidence rather than deleting broad market coverage.

Forward proof required:

- Fresh v28 rows only.
- Better explanation of FV error, exit value, or scratch exits.
- No promotion from a tiny sample.

## First Concrete Work Items

- Keep `scripts/run_mushroom_v28_shadow_size2.ps1` running.
- Use `probe_v28_reactivated_shadow_status.py` to score fresh dry-run v28 trades.
- Build a forward registry for H3 probability-collapse turbulence using the new shadow storage tag.
- Build a probability-error capture table for H4/H5 before testing money rules.
- Maintain the continuous scorecard at `logs/edge_research/v28_continuous_scorecard_latest.md`.
- Track watched-market coverage versus entries so the soft broad-coverage target is measured continuously.
- Track recross hazard as a predeclared physics feature in `probe_v28_forward_physics_registry.py`.
