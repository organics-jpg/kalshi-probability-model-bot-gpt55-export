# v28 User Probability Intuition Triage

Research-only; no live bot changes and no orders.

## Usable Ideas

### Gambler Inefficiency

User intuition: Kalshi BTC 15m order books are not perfectly efficient because some participants trade vibes, lottery preference, fear, or chase candles instead of calculating fair value.

Research translation:
- Treat the book as useful information, not truth.
- Look for book/FV disagreement during fast book spikes or dips.
- Separate two cases:
  - book spike above fair value: likely overpay zone, avoid buying that side or prefer opposite side if other physics agree.
  - book dip below fair value: potential entry if BTC path geometry is not unresolved/noisy.

Current evidence:
- Hard book anchors alone are not enough; broad book-plus candidates have often gone negative or too high coverage.
- The useful version appears to be conditional: book inefficiency matters only when paired with path geometry, recross risk, and time-to-close.
- Latest book-dislocation attribution on the lead FV bridge supports the conditional version:
  - largest/deepest apparent discounts are not automatically best.
  - `thin_discount_0_4pp` produced the best edge bucket in the diagnostic window: `9` entries, `8/1`, `+266c`.
  - `deep_discount_ge12pp` was mixed: `2` settled, `1/1`, only `+4c`.
  - ask spikes of `>=8pp` were mixed/negative overall, while smaller `4-8pp` ask rises were cleaner in this small diagnostic slice.
- Follow-up fixed penalty test:
  - A book-dislocation-aware escape-energy penalty reduced diagnostic PnL from `+358c` to `+325c`.
  - Treat the hand penalty as rejected for now; the simpler escape-energy score is currently better.

Next probe shape:
- Book-dislocation attribution by regime: compare FV-book gap during sudden ask jumps/dips versus calm book drift.

### Spike/Dip Fair-Value Dislocation

User intuition: edge may exist when executable ask temporarily dips below fair value, or when the ask spikes above fair value.

Research translation:
- This is a microstructure-friction model, not just a probability model.
- Need to measure whether a dislocation is a stale quote, a real panic/chase, or a correct repricing.

Current evidence:
- False-conviction work says many apparent dips are not true edge; near-boundary cheapness can mean unresolved path risk.
- The best diagnostic FV bridge currently uses continuous recross-forgetting plus escape-energy thinning, not raw gap chasing.

Next probe shape:
- classify dislocations as escaped, unresolved, stale, or chase; score forward PnL by class.

### BTC Regimes And Recent Activity Memory

User intuition: recent BTC behavior over the last 4 hours or similar may imply current volatility/path risk.

Research translation:
- Use a weighted recent-activity memory: realized volatility, directional displacement, recross count, impulse size, and range compression.
- Feed this into FV as a reliability/forgetting term, not as a direct side predictor.

Current evidence:
- This matches the current lead: continuous recross-forgetting improved diagnostic calibration and PnL when paired with escape-energy thinning.
- The strongest bridge diagnostic now is `first_eligible_top80_escape_energy + escape_edge6_or_p65_or_far_edge4 + continuous_recross_forget`.

Current diagnostic read:
- coverage `80.95%`
- settled `16`
- W/L `13/3`
- net `+358c`
- Brier delta `-0.0691`
- logloss delta `-0.1358`
- blocker: sample size below 30
- Source-quality follow-up:
  - approved-only diagnostic version kept `81.82%` coverage with `18` settled, `15/3`, `+100c`.
  - all-source/reconstructed diagnostic was stronger at `+325c`, so source quality still matters.
  - post-freeze approved-only evidence is only `1` settled row and was `-18c`, so this remains tracking-only.

Next probe shape:
- add explicit 4h weighted BTC activity terms to the escape-energy score and compare against the current simpler recross/edge/distance score.

Follow-up result:
- A fixed phi-weighted 4h activity-memory ranking using live/shadow fields selected the same rows as base escape-energy in the diagnostic window.
- Diagnostic delta versus base was `0c`, so the activity-memory ranking is neutral/rejected for now.
- The simpler escape-energy score remains the lead until fresh rows show the memory term changes selections beneficially.

### Projection Drift

User intuition: understanding why backtest/projection differs from live behavior is necessary for a better model.

Research translation:
- Every candidate must carry source-quality and execution-quality tags.
- Reject candidates that mostly win through reconstructed rejected-actionable rows.
- Compare actual approved-entry rows separately from simulated/rejected rows.

Current evidence:
- This is already a real blocker: target live-evidence quality has too few approved-entry rows and too much simulated/rejected share.
- The approved-heavy false-conviction repair has been frozen separately but has not earned post-freeze rows yet.

Next probe shape:
- keep candidate scorecards split by source: approved, rejected-actionable, reconstructed, and actual fill evidence.

### Phi-Style Forgetting

User intuition: catastrophic forgetting as a feature; phi could guide how much/often to forget because it is compressible.

Research translation:
- Do not use phi mystically.
- Use it as a fixed anti-overfit decay constant:
  - reliability multiplier around `1/phi ~= 0.618`
  - stronger forgetting around `1/phi^2 ~= 0.382`
  - memory weights decay by powers of phi over recent BTC activity windows.

Current evidence:
- The useful idea is "forget local certainty when path geometry says it is stale or unresolved."
- Continuous recross-forgetting is already the live candidate form of that idea.
- Latest bridge test:
  - `phi_boundary_forget` is competitive with continuous recross-forgetting but does not beat the best diagnostic row.
  - `phi_activity_memory_forget` currently over-forgets and collapses coverage far below the 75-80% target.
  - The usable phi idea is fixed boundary-memory decay, not a full activity-memory throttle yet.

Next probe shape:
- keep phi-boundary decay as a diagnostic comparator, but lead with simpler continuous recross-forgetting unless future rows reverse the ranking.

## Direction

The most workable combined path is:

1. Treat Kalshi book spikes/dips as possible but not sufficient edge.
2. Use BTC regime memory to decide whether apparent FV edge is trustworthy.
3. Apply catastrophic forgetting as a reliability shrink toward 50 when recross/volatility/path geometry says the current probability is fragile.
4. Thin to the target 75-80% coverage band by escape energy, not by historical PnL.
5. Promote only after post-freeze rows clear sample, source-quality, coverage, PnL, and calibration gates.

## Current Best Candidate From These Intuitions

`first_eligible_top80_escape_energy + escape_edge6_or_p65_or_far_edge4 + continuous_recross_forget`

Interpretation:
- Start from broad first-eligible opportunities.
- Adjust FV by forgetting conviction in unresolved recrossing boundary states.
- Keep the strongest roughly 80% by escape energy.
- Do not buy every apparent book dip; require path escape or stronger adjusted edge.

Status:
- Diagnostic-only positive.
- Not promotable: sample below 30 and post-freeze validation is immature.
- Family scorecard now tracks this under `false_conviction_fv_entry_bridge`; it remains blocked by post-freeze immaturity and reconstructed-source risk.
