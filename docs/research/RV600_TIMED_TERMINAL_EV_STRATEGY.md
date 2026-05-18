# RV600 Timed Terminal EV Strategy

Updated: 2026-05-13

This is a research-only strategy spec for converting the high projected PnL
`rv600` rolling-vol particle clue into a deployable, forward-testable strategy.
It must not change live v28 order logic until the fresh-shadow gates below pass.

## Short Version

Use rolling 600-second BTC realized volatility to compute a terminal settlement
probability for the current Kalshi BTC 15m strike, then trade the fee/fill
adjusted side with the higher expected value.

The important constraint is timing:

- do not take every rv600 signal
- do not take the first signal of the market
- evaluate only from `T-420s` to `T-70s`
- take at most one entry per market
- require projected EV of at least `10c`

This turns the raw high-PnL clue into an actual strategy instead of a repeated
candidate-row replay artifact.

## Why This Candidate

The transfer diagnostic showed the raw `rv600` probability had the largest
aggregate projected PnL:

| Replay form | Selected | PnL | Avg/selected | Notes |
|---|---:|---:|---:|---|
| current calibrated v28, all candidates | 26808 | `+34638.0c` | `1.2921c` | baseline |
| rv600, all candidates | 26744 | `+73567.0c` | `2.7508c` | best aggregate, but unstable |
| v28 + rv600 side agreement | 18997 | `+56329.0c` | `2.9652c` | good risk clue, less coverage |
| best v28/rv blend | 26418 | `+51166.0c` | `1.9368c` | useful, but not stable enough |

But a first-entry-per-market stress test showed raw rv600 is not safe if used
naively:

| One-entry rule | Selected | PnL | Avg/entry | Positive roots |
|---|---:|---:|---:|---:|
| current, first signal per market | 53 | `+491.0c` | `9.26c` | `8/10` |
| rv600, first signal per market | 53 | `-78.0c` | `-1.47c` | `5/10` |

So the PnL is not a generic "rv600 is always better" effect. It is a timing and
selection effect.

The best deployable timing test was first qualifying signal inside the
`T-420s` to `T-70s` entry window:

| Strategy | Min EV | Selected | PnL | Avg/entry | Win rate | Positive roots |
|---|---:|---:|---:|---:|---:|---:|
| rv600 timed entry | `10c` | 33 | `+682.0c` | `20.67c` | `54.5%` | `8/10` |
| current timed entry | `10c` | 32 | `+438.0c` | `13.69c` | `56.2%` | `7/10` |
| current timed entry | `8c` | 33 | `+659.0c` | `19.97c` | `60.6%` | `7/10` |

The rv600 advantage is real enough to shadow hard, but not real enough to
promote directly.

## Core Probability

Compute `p_rv600 = P(BTC_settlement > strike)` using:

- latest timestamp-available spot price
- current market strike
- seconds to market close
- rolling realized volatility from the last `600s` of spot observations
- Brownian terminal probability, not barrier-touch probability

Volatility guardrails:

- fallback annualized vol: `0.65`
- minimum annualized vol: `0.20`
- maximum annualized vol: `2.50`
- minimum distinct observations: `3`

Those values match the current dynamic particle implementation and should be
locked for the first forward-shadow test.

## Entry Rule

For each active Kalshi BTC 15m market:

1. Only evaluate if `70 <= seconds_to_close <= 420`.
2. Skip if this strategy already entered the market.
3. Compute rv600 probability.
4. Compute fee/fill adjusted EV for both sides.
5. Select the side with larger EV.
6. Trade only if best EV is at least `10c`.
7. Require the normal execution quality checks: fresh book, executable ask,
   visible depth, and no stale-book suppression.
8. Record all skipped candidates too.

Expected value:

```text
EV_yes =
  fill_yes * (p_rv600 * (100 - yes_ask - fee) - (1 - p_rv600) * yes_ask)
  - (1 - fill_yes) * no_fill_penalty

EV_no =
  fill_no * ((1 - p_rv600) * (100 - no_ask - fee) - p_rv600 * no_ask)
  - (1 - fill_no) * no_fill_penalty
```

Use `side = YES` if `EV_yes >= EV_no`, otherwise `NO`.

Initial fixed thresholds:

| Parameter | Value |
|---|---:|
| entry window min seconds to close | `70s` |
| entry window max seconds to close | `420s` |
| minimum EV | `10c` |
| max entries per market | `1` |
| max ask | `90c` |
| default min fill probability for replay | `0.50` |

## Relationship To v28

This should start as an independent shadow strategy, not as a v28 replacement.

Log v28 beside it:

- `p_v28`
- v28 side
- v28 EV
- rv600 side
- rv600 EV
- side agreement/disagreement
- probability gap

Do not veto rv600 with v28 during the first locked shadow test. The point of the
first phase is to measure whether rv600 has independent timing edge.

After the first phase, test these transfer variants:

1. `rv600_primary`: use rv600 only.
2. `rv600_v28_agreement`: allow entry only when rv600 and v28 choose same side.
3. `rv600_v28_soft_veto`: skip only when v28 has opposite-side EV at least `6c`
   stronger than rv600.
4. `v28_95_rv600_05`: use `0.95 * p_v28 + 0.05 * p_rv600` as a conservative
   v28 probability nudge.

The current evidence says `rv600_primary` is the high-PnL candidate, while the
agreement/blend versions are risk controls.

## Exit Rule

For research scoring, use hold-to-settlement PnL. This keeps the label aligned
with the terminal probability being predicted.

For any future tiny live pilot:

- default: hold to settlement
- allow only safety exits already proven in v28 infrastructure
- log a separate hold-to-settlement counterfactual for every live exit

Do not optimize exits on the same 10-root retrospective set.

## Sizing

Shadow phase:

- score exactly one contract per accepted entry
- no Kelly sizing
- no multi-entry averaging

Tiny live pilot, only after gates pass:

- max one contract or lower than current v28 size
- max one open rv600 position per market
- no size increase until at least `100` fresh accepted entries

## Required Logs

For every candidate moment, whether accepted or skipped:

- market ticker
- decision timestamp
- seconds to close
- strike
- spot
- rv600 annualized vol
- `p_rv600`
- `p_v28`
- yes ask / no ask
- fee
- yes fill probability / no fill probability
- `EV_yes_rv600`
- `EV_no_rv600`
- selected side
- selected EV
- accepted/skipped
- skip reason
- book age
- depth ratio
- side agreement with v28
- eventual settlement
- hold-to-settlement PnL
- actual fill status if live/shadow IOC is attempted

## Fresh Shadow Promotion Gates

Minimum sample before considering any live impact:

- at least `100` accepted rv600 timed entries
- at least `40` distinct markets
- at least `10` trading days, including weekend data

Pass conditions:

- rv600 timed strategy selected PnL beats the matched v28 timed control by at
  least `20%`
- average PnL per accepted entry is at least `10c`
- no single market contributes more than `25%` of total PnL
- last `20` accepted entries are positive in aggregate
- at least `60%` of rolling market blocks are positive
- top predicted-EV bucket is positive
- no stale-book or fillability failure cluster explains most of the gains

Hard vetoes:

- any future-data leakage
- missing all-candidate denominator
- same-market repeated-entry inflation
- rv600 only wins by one outlier market
- rv600 loses to v28 over the last `20` accepted entries
- fill-adjusted PnL turns negative after actual no-fill assumptions

## Implementation Path

1. Add a research-only rv600 timed-entry evaluator that writes a stable report
   after every sidecar/label refresh.
2. Add shadow logging fields to the candidate recorder, without changing live
   order decisions.
3. Run `rv600_primary`, `rv600_v28_agreement`, `rv600_v28_soft_veto`, and
   `v28_95_rv600_05` side by side.
4. Freeze thresholds for the first forward run:
   `window=[70s, 420s]`, `min_ev=10c`, `max_entries_per_market=1`.
5. Re-evaluate after every market close, but do not tune until the minimum
   sample is reached.

## Current Decision

This is the strongest projected-PnL candidate after making it deployable, but it
is still shadow-only. The next useful work is to make the timed-entry report
first-class in the research pipeline and collect fresh forward entries under
the locked thresholds above.
