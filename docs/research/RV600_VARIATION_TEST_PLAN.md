# RV600 Variation Test Plan

Updated: 2026-05-13

This spec defines how to test whether the rv600 rolling-vol probability clue can
become a profitable Kalshi BTC 15m strategy after fees, fills, and repeated
entries are accounted for.

The strategy does not need to trade only once per market. It only needs to prove
that every allowed extra entry adds real, fee-adjusted edge rather than replay
inflation from repeated near-identical candidate rows.

## Objective

Find the best deployable rv600-derived strategy family that:

- is profitable after fees
- survives market-level and recent-window stress tests
- beats a matched v28/current-calibrated control
- remains profitable when repeated same-market entries are penalized correctly
- can be run in forward shadow without touching live v28 order logic

## Starting Point

Current evidence:

- raw all-candidate `rv600` had the largest projected PnL: `+73567.0c`
- current/v28 all-candidate baseline: `+34638.0c`
- naive first rv600 signal per market lost: `-78.0c`
- timed rv600 with one entry per market, `T-420s` to `T-70s`, `min_ev=10c`:
  `33` entries, `+682.0c`, `20.67c` avg/entry, positive in `8/10` roots

Interpretation:

The edge is probably not "rv600 is always better." It is more likely a
combination of:

- timing inside the market lifecycle
- sufficiently high projected EV
- side selection
- avoiding early weak signals
- possibly allowing repeated entries only when the signal refreshes enough

## Core Formula

For every candidate moment:

```text
p = rv600 terminal probability of YES

EV_yes =
  fill_yes * (p * (100 - yes_ask - fee) - (1 - p) * yes_ask)
  - (1 - fill_yes) * no_fill_penalty

EV_no =
  fill_no * ((1 - p) * (100 - no_ask - fee) - p * no_ask)
  - (1 - fill_no) * no_fill_penalty
```

Selected side is the side with larger EV. A trade is accepted only if all active
gates pass.

## Accounting Rules

Every variant must report:

- all candidate rows
- accepted entries
- distinct markets
- entries per market distribution
- selected PnL after fees
- average PnL per entry
- average PnL per market
- win/loss count
- fill-adjusted PnL
- no-fill penalty PnL
- max single-market PnL share
- last-window PnL
- matched v28/current control PnL on the same accepted timestamps

Repeated entries must be scored three ways:

1. `all_entries`: every accepted row counts
2. `one_per_side_per_market`: at most one YES and one NO per market
3. `position_capped`: multiple entries allowed up to a declared max risk cap

A variant cannot pass if it is only profitable under `all_entries`.

## Variant Families

### A. Timing Windows

Test first because timing changed rv600 from bad to promising.

| Variant | Min seconds to close | Max seconds to close |
|---|---:|---:|
| late_70_180 | 70 | 180 |
| late_70_240 | 70 | 240 |
| late_70_300 | 70 | 300 |
| base_70_420 | 70 | 420 |
| mid_120_420 | 120 | 420 |
| mid_180_420 | 180 | 420 |
| broad_70_600 | 70 | 600 |

Initial favorite:

- `base_70_420`

Reason:

- it produced the best current deployable rv600 clue when paired with `min_ev=10c`

### B. EV Thresholds

Test fixed thresholds:

```text
min_ev_cents in [0, 2, 4, 6, 8, 10, 12, 15, 20]
```

Initial favorite:

- `10c`

Why:

- on the current stress cut, rv600 at `min_ev=10c` had better PnL than current
  control and stayed positive in `8/10` roots

Promotion-eligible thresholds should avoid extremes:

- reject if entries are too sparse: fewer than `25` retrospective accepted
  entries across the 10-root test
- reject if average PnL is below `10c`
- reject if less than `60%` of roots are positive

### C. Repeated Entry Rules

This is the main new test. The strategy can trade more than once per market, but
only when extra entries have independent value.

Test:

| Variant | Rule |
|---|---|
| single_market | max 1 entry per market |
| side_flip_only | second entry allowed only if side changes |
| same_side_refresh_60s | same side allowed after 60s |
| same_side_refresh_120s | same side allowed after 120s |
| same_side_ev_step_3c | same side allowed only if EV improves by 3c |
| same_side_ev_step_5c | same side allowed only if EV improves by 5c |
| max_2_entries | max 2 entries per market |
| max_3_entries | max 3 entries per market |
| risk_cap_100c | total ask risk per market <= 100c |
| risk_cap_200c | total ask risk per market <= 200c |

Hard requirements for repeated-entry variants:

- total PnL must beat `single_market`
- average PnL per added entry must be positive
- average PnL per market must improve
- no single market may contribute more than `25%` of total PnL
- max drawdown by market cannot worsen by more than `25%` versus `single_market`

### D. Side Filters

Earlier huge PnL often came from one side dominating repeated rows, especially
NO-heavy slices. Test side behavior explicitly.

| Variant | Rule |
|---|---|
| both_sides | no side filter |
| yes_only | YES only |
| no_only | NO only |
| side_by_rv_gap | trade side only if rv600 probability gap > threshold |
| side_by_v28_agreement | rv600 and v28 must choose same side |
| side_by_v28_disagreement | only trade disagreement moments |

Gap thresholds:

```text
abs(p_rv600 - break_even_side_probability) in [0.05, 0.08, 0.10, 0.15]
```

Pass condition:

- if one side is profitable and the other is not, split the strategy rather than
  averaging the loser into the winner

### E. v28 Transfer Controls

These test whether rv600 should be independent or a v28 overlay.

| Variant | Probability / Decision |
|---|---|
| rv600_primary | use rv600 only |
| v28_primary | matched v28/current control |
| blend_95_5 | `0.95 * p_v28 + 0.05 * p_rv600` |
| blend_90_10 | `0.90 * p_v28 + 0.10 * p_rv600` |
| blend_80_20 | `0.80 * p_v28 + 0.20 * p_rv600` |
| agreement_veto | v28 and rv600 must choose same side |
| soft_veto_6c | skip if v28 opposite-side EV exceeds rv600 by 6c |
| soft_veto_10c | skip if v28 opposite-side EV exceeds rv600 by 10c |

Use matched timestamps for controls:

- If rv600 accepts at time `t`, compute what v28 would have done at that same
  time using the same fee/fill assumptions.

### F. Volatility Regime Filters

rv600 is a volatility model, so test whether it only works in specific vol
states.

Regime features:

- rv600 annualized vol
- rv300 annualized vol
- rv300 / rv600 ratio
- spot move over last 60s
- spot move over last 180s
- distance to strike in sigma units

Candidate filters:

| Variant | Rule |
|---|---|
| vol_mid | rv600 vol between 0.4 and 1.5 |
| vol_high | rv600 vol above 1.5 |
| vol_low | rv600 vol below 0.4 |
| vol_accel | rv300 / rv600 > 1.2 |
| vol_decel | rv300 / rv600 < 0.8 |
| strike_near | abs distance to strike <= 1.25 sigma |
| strike_far | abs distance to strike > 1.25 sigma |

Pass condition:

- a regime filter must improve both average PnL per entry and root-level
  stability, not just reduce coverage

### G. Market Microstructure Filters

Test whether book quality explains when rv600 is executable.

Filters:

| Variant | Rule |
|---|---|
| book_age_250 | book age <= 250ms |
| book_age_500 | book age <= 500ms |
| depth_ratio_3 | visible depth / size >= 3 |
| depth_ratio_6 | visible depth / size >= 6 |
| spread_3c | effective spread <= 3c |
| spread_5c | effective spread <= 5c |
| fill_prob_50 | selected-side fill probability >= 0.50 |
| fill_prob_70 | selected-side fill probability >= 0.70 |

Pass condition:

- filter must improve fill-adjusted PnL, not only theoretical PnL

### H. Price Caps And Payoff Shape

Test whether rv600 only works at cheap or rich prices.

| Variant | Rule |
|---|---|
| ask_le_90 | selected ask <= 90c |
| ask_le_85 | selected ask <= 85c |
| ask_40_85 | selected ask between 40c and 85c |
| cheap_tail | selected ask <= 30c |
| rich_tail | selected ask >= 80c |

Pass condition:

- no variant with very high win rate but negative expectancy passes
- no variant with huge payout but poor stability passes

## Evaluation Phases

### Phase 1: Retrospective Exhaustive Grid

Run all variant combinations on the ten current real-shadow roots.

Keep this phase as discovery only.

Output:

- top 20 by total PnL
- top 20 by average PnL per entry
- top 20 by root stability
- top 20 by matched-v28 delta
- rejected high-PnL variants with reason

Do not promote from this phase.

### Phase 2: Locked Retrospective Simplification

Choose at most five simple candidates from Phase 1.

Rules:

- prefer simpler variants over complex variants
- no candidate may use more than three active gates
- repeated-entry rule counts as one gate
- timing window counts as one gate
- EV threshold counts as one gate

Example candidate:

```text
rv600_primary
window = 70s to 420s
min_ev = 10c
entry_rule = same_side_refresh_120s
max_entries_per_market = 2
```

### Phase 3: Forward Shadow

Run the locked candidates beside live v28 without changing live v28.

Minimum sample:

- 100 accepted entries
- 40 distinct markets
- 10 calendar days
- at least two weekend sessions

Score every candidate moment, not just accepted entries.

### Phase 4: Tiny Live Pilot

Only after forward-shadow passes.

Initial live pilot:

- one contract max
- max two entries per market
- no Kelly sizing
- no automatic threshold tuning
- preserve hold-to-settlement counterfactual even if an exit is taken

## Promotion Gates

A variant can move from forward shadow to tiny live only if:

- selected PnL after fees is positive
- selected PnL beats matched v28 control by at least `20%`
- average PnL per entry >= `10c`
- average PnL per market is positive
- added entries are positive after fees
- root/market block positivity >= `60%`
- recent last-20 accepted entries are positive
- no single market contributes > `25%` of total PnL
- no side contributes all of the profit while the other side loses materially
- fill-adjusted PnL remains positive under conservative no-fill assumptions

Hard fail:

- any future leakage
- any denominator gap
- repeated-entry PnL disappears under market-level de-duplication
- variant only wins in one market or one root
- variant loses to v28 in fresh shadow

## First Candidate Set To Build

Build these first:

1. `rv600_single_70_420_ev10`
   - max one entry per market
   - current best clean benchmark

2. `rv600_max2_refresh120_70_420_ev10`
   - repeated entries allowed after 120s
   - max two entries per market

3. `rv600_max2_evstep5_70_420_ev10`
   - repeated entry only if same-side EV improves by at least 5c
   - max two entries per market

4. `rv600_max3_risk200_70_420_ev10`
   - max three entries per market
   - total ask risk cap 200c

5. `rv600_v28_softveto6_max2_70_420_ev8`
   - rv600 primary
   - repeated entries allowed
   - skip when v28 strongly prefers the opposite side

6. `v28_95_rv600_05_70_420_ev8`
   - conservative v28 probability nudge
   - lower EV threshold because probability is less aggressive

## Answer To "Can We Make This Work?"

Maybe, but only if repeated entries pass the added-entry test.

The current evidence says:

- naive rv600 is too unstable
- timed high-EV rv600 is promising
- repeated all-candidate PnL is probably inflated unless proven otherwise
- the next unlock is not a fancier probability formula; it is correct repeated
  entry accounting after fees and fills

The most likely successful version is:

```text
rv600 primary
T-420s to T-70s
min EV 8c to 10c
max 2 entries per market
same-side re-entry only after 120s or after EV improves by 5c
strict fee/fill accounting
matched v28 control on same timestamps
```

That is the first thing to build and shadow.
