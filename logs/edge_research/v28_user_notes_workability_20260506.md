# v28 User Notes Workability Review - 2026-05-06

Research-only. No live bot changes and no orders.

## Bottom Line

The most usable idea in the notes is:

> Kalshi BTC 15m books are not fair value; they are a noisy crowd signal. The edge is deciding when a book/FV gap is a real mispricing versus when it is correctly warning us that BTC path risk is unresolved.

That maps directly to the current best research lane:

`first_eligible_top80_escape_energy + escape_edge6_or_p65_or_far_edge4 + continuous_recross_forget`

This lane does not chase every apparent discount. It reduces conviction in fragile recross/boundary states, then keeps the roughly top 80% of opportunities by escape energy.

## Idea Assessment

### Gambler Inefficiency / Vibes In The Book

Status: usable, but only conditional.

The intuition is right in spirit: retail/vibe/liquidity-chasing flow can make Kalshi asks temporarily too high or too low versus physical fair value.

The trap is assuming every big book/FV gap is edge. Current attribution says modest dislocations have looked cleaner than the deepest apparent discounts. Deep discounts can be the market correctly pricing unresolved boundary risk.

Workable model shape:
- use book/FV gap as a candidate edge signal,
- penalize it when BTC path is still recrossing or boundary-near,
- avoid treating the book as either truth or pure noise.

### Spikes And Dips

Status: usable as a microstructure classifier, not as a raw trigger.

The most workable version is to classify a spike/dip into one of four physical states:
- stale quote,
- panic/chase flow,
- real repricing,
- unresolved boundary hazard.

Only the first two can plausibly be exploitable. The latter two should make us more cautious, not more aggressive.

### BTC Regimes / Last 4h Activity

Status: conceptually useful; current simple test was neutral.

Recent BTC activity should help estimate reliability and volatility, not directly predict the side. The right question is not "does recent volatility mean YES or NO?" The better question is "should I trust this FV estimate less because the recent path is unstable?"

The latest activity-memory escape bridge selected the same rows as the base escape-energy lead, so it added no value in the current implementation. Keep the concept, but the next version needs better actual BTC history features rather than only live/shadow proxy fields.

### Projection Drift

Status: essential.

This is not just a note; it is a core research constraint. The model can look profitable when it is scored on reconstructed or rejected-actionable rows and then disappoint live because:
- the actual executable book is worse,
- the chosen side/price was not truly available,
- live timing differs from replay timing,
- exits/state handling changes the payoff distribution,
- the market regime changed after the freeze.

Every candidate should continue to be split by approved-only, reconstructed-only, and all-source evidence.

### Catastrophic Forgetting / Phi

Status: usable only as disciplined reliability decay.

The useful idea is not phi itself. The useful idea is controlled forgetting: when the local geometry says the model's certainty is fragile, shrink the FV probability toward 50 instead of carrying stale confidence forward.

Current evidence:
- continuous recross forgetting is the current lead,
- phi boundary forgetting is a useful comparator,
- phi activity-memory forgetting over-forgot and hurt coverage.

## Direction

Keep working on:

1. False-conviction detection near boundaries and recross zones.
2. Escape-energy entry ranking around the 75-80% coverage target.
3. Book dislocation attribution, but conditional on path geometry.
4. Source-quality separation so reconstructed wins cannot fool us.
5. Better recent BTC activity features once fresh BTC history is available.

Do not promote yet. The current lead is promising but still blocked by sample size and source-quality evidence.
