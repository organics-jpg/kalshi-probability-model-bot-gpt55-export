# Next-Second Particle Simulation Plan

Research-only plan for a next-second particle simulation engine for the Kalshi
BTC 15-minute binary market bot.

This plan does not propose changing live order logic directly. The intended
path is recorder -> offline replay -> shadow predictions -> locked validation
-> small live experiment only after promotion gates pass.

## 0. Review-Pass Corrections

This section was added after a logic review of the first draft.

The plan remains directionally right, but several details need to be made
explicit so the implementation does not drift into a beautiful but wrong model.

Corrections:

- Kalshi BTC 15m resolves on **terminal settlement above/below strike**, not on
  whether BTC touches or crosses the strike before expiry. Crossing probability
  is useful only as a secondary path-risk feature for exit/fill/adverse
  selection, not as the primary label.
- Current BTC price should be treated as an observed anchor. The particle cloud
  should mostly represent uncertainty over drift, volatility, jump hazard,
  regime, and microstructure state. We should not let particles wander away
  from the known current spot and then pretend that is informational.
- Particle probabilities must be **weighted** unless the particle set has just
  been resampled into equal weights.
- Calibration cannot update instantly at prediction time. A live calibrator can
  predict now, but it only updates after the market resolves and the label is
  known.
- Nested Monte Carlo is fine offline, but expensive live. The live engine should
  use vectorized shared terminal simulations and adaptive particle counts.
- Fill-adjusted EV must distinguish "no fill" from "bad trade." If an IOC does
  not fill, realized PnL is usually zero, but it still has opportunity cost and
  may indicate stale/fake liquidity.
- The all-candidate denominator is mandatory. A model trained only on filled
  rows can learn how the old bot behaved, not what it should have done.
- Kalshi market price is an observation, not a ground-truth probability. It
  should be downweighted when the book is stale, thin, wide, or lagging BTC.

Accuracy standard:

> The particle engine is only real if it improves calibrated terminal
> probability and forward EV ranking on all candidates. A replay PnL bump
> without positive EV rank correlation is not enough.

## 1. North Star

The current bot asks a hard question:

> What is the fair probability that BTC will settle above/below the Kalshi
> strike at market close, and is the executable Kalshi price attractive after
> fees, fill risk, and exit risk?

The next-second particle simulation changes the way we answer that question.
Instead of trying to predict the whole remaining 15-minute interval in one
shot, we maintain a live probability distribution over the next second, then
roll that distribution forward many times to settlement.

The engine should output, every second and for every active candidate:

- `p_yes_terminal`: probability BTC settles above strike.
- `p_side_terminal`: probability the candidate side wins.
- `p_low`, `p_mid`, `p_high`: calibrated probability interval.
- `expected_pnl_cents`: fee/fill-adjusted expected value.
- `fill_prob`: probability an IOC/limit attempt fills.
- `risk_state`: whether this is stable, stale, panic, crowded, jumpy, or unknown.
- `trade/no_trade_shadow`: what the particle engine would do in shadow.

The key idea is not "predict the next second perfectly." The key idea is:

> Maintain a live distribution of plausible next-second worlds, repeatedly
> update it with new evidence, and convert the resulting terminal distribution
> into calibrated fair value.

## 2. What This Is Not

This is not:

- A magic second-by-second deterministic predictor.
- A replacement for calibration.
- A replacement for fillability modeling.
- A reason to trust backtest-only PnL.
- A direct live-trading change.

It is:

- A probabilistic state estimator.
- A terminal fair-value engine.
- A stress-testable way to combine BTC ticks, volatility, jumps, Kalshi book
  state, market-maker staleness, and social/microstructure pressure.
- A cleaner way to let short-horizon structure influence a 15-minute decision.

## 3. Core Hypothesis

The bot may be losing edge because the 15-minute probability is too coarse.
BTC near a Kalshi boundary is path-dependent:

- A one-second burst can make the market maker stale.
- A five-second reversal can invalidate an apparent edge.
- A thirty-second volatility cluster can widen the true probability interval.
- A late-market book can look deep while being executable only on one side.

The particle engine should improve the bot if it can:

1. React to fresh BTC movement faster than a static terminal model.
2. Widen uncertainty during jumpy or stale regimes.
3. Avoid trades where the current fair value is only a stale extrapolation.
4. Preserve or improve calibrated probability scores.
5. Improve forward EV ranking on all candidate rows, not just filled trades.

## 4. System Architecture

The full system has nine layers.

1. Second-level market recorder.
2. Candidate snapshot recorder.
3. Feature bus.
4. Latent state estimator.
5. Particle transition model.
6. Observation weighting model.
7. Terminal projection model.
8. Calibration and uncertainty wrapper.
9. EV/fillability decision layer.

Data flow:

```text
BTC ticks/books + Kalshi books + candidate snapshots
    -> causal feature bus
    -> particle state update every second
    -> terminal settlement distribution
    -> calibrated p_yes / p_side interval
    -> expected PnL after fees and fill risk
    -> shadow decision registry
    -> forward validation
```

### 4.1 Correct Modeling Decomposition

The first version should use a partially anchored particle filter:

```text
observed BTC price now is known
particle uncertainty lives mostly in:
  volatility
  drift/impulse
  jump hazard
  regime
  market-maker staleness
  liquidity/fillability state
  calibration residual
```

This is safer than letting each particle maintain a wildly different current
spot price. For Kalshi terminal probability, the current BTC spot is the base
condition. The uncertainty is how the path evolves from here.

Recommended live state split:

```text
observed_state_t = {
  spot_price,
  timestamp,
  strike,
  seconds_to_close,
  kalshi_book,
  candidate_price
}

latent_particle_i_t = {
  drift,
  volatility,
  jump_hazard,
  jump_size_params,
  trend_or_reversion_state,
  stale_mm_state,
  liquidity_state,
  regime_state,
  calibration_bias
}
```

Terminal simulation starts every path from the same observed `spot_price`, but
with different latent dynamics from each particle.

## 5. Data Requirements

The particle engine cannot be validated from filled trades alone. It needs the
all-candidate denominator.

### 5.1 Required Second-Level Tables

`particle_btc_second_bars`

- `ts_utc`
- `source`
- `source_sequence`
- `open`
- `high`
- `low`
- `close`
- `vwap`
- `trade_count`
- `volume`
- `dollar_volume`
- `last_trade_size`
- `max_trade_size`
- `source_latency_ms`
- `source_gap_ms`
- `recv_ts_utc`
- `is_synthetic_bar`
- `quality_flag`

`particle_btc_ticks_optional`

- `ts_utc`
- `exchange`
- `price`
- `size`
- `side_if_available`
- `recv_ts_utc`
- `latency_ms`

`particle_kalshi_book_second`

- `ts_utc`
- `recv_ts_utc`
- `market`
- `strike`
- `market_close_ts_utc`
- `seconds_to_close`
- `yes_bid`
- `yes_ask`
- `no_bid`
- `no_ask`
- `yes_bid_depth_1`
- `yes_ask_depth_1`
- `no_bid_depth_1`
- `no_ask_depth_1`
- `yes_depth_ladder`
- `no_depth_ladder`
- `spread_yes`
- `spread_no`
- `book_age_ms`
- `last_book_update_ts_utc`
- `book_gap_ms`
- `market_status`
- `source_quality_flag`

`particle_candidate_snapshot`

- `decision_id`
- `ts_utc`
- `recv_ts_utc`
- `market`
- `side`
- `strike`
- `market_close_ts_utc`
- `seconds_to_close`
- `btc_price`
- `candidate_ask_cents`
- `candidate_bid_cents`
- `fee_cents`
- `p_current_model`
- `p_brownian_terminal`
- `p_aci`
- `edge_cents`
- `depth_ratio`
- `book_age_ms`
- `btc_age_ms`
- `current_position_contracts`
- `current_position_cost_cents`
- `candidate_generation_reason`
- `would_current_bot_trade`
- `would_particle_trade_shadow`
- `block_reason`
- `skip_reason`
- `fill_attempted`
- `order_id`
- `order_status`
- `fill_count`
- `fill_price_cents`
- `fill_delay_ms`
- `realized_pnl_cents`
- `counterfactual_settlement_pnl_cents`
- `settlement_result`
- `label_available_ts_utc`

`particle_prediction_log`

- `decision_id`
- `ts_utc`
- `market`
- `side`
- `model_version`
- `particle_count`
- `effective_sample_size`
- `p_yes_mean`
- `p_yes_median`
- `p_yes_p05`
- `p_yes_p95`
- `p_side_mean`
- `p_side_p05`
- `p_side_p95`
- `expected_pnl_cents`
- `raw_ev_cents`
- `fill_adjusted_ev_cents`
- `break_even_probability`
- `fill_prob`
- `risk_state`
- `calibration_width`
- `decision_shadow`
- `shadow_reason`
- `feature_hash`

`particle_settlement_labels`

- `market`
- `strike`
- `market_close_ts_utc`
- `settlement_ts_utc`
- `settlement_price`
- `settlement_result_yes_no`
- `data_source`
- `label_quality_flag`

### 5.2 Causal Alignment Rules

Every row must make time semantics boring and explicit.

Rules:

- `ts_utc` is the market/event timestamp.
- `recv_ts_utc` is when our process received or wrote it.
- Feature construction may use only data with `recv_ts_utc <= decision_ts_utc`
  in strict live replay.
- If event time and receive time disagree, strict replay uses receive time.
- Settlement labels are joined only after `label_available_ts_utc`.
- Any backfilled candle or book row must carry `quality_flag=backfilled` and be
  excluded from strict live-readiness scoring unless explicitly allowed.
- The candidate denominator must include both sides when both are observable,
  not only the side the current bot preferred.

### 5.3 Minimum Forward Data Before Serious Claims

Minimum before offline tuning:

- 10,000 second bars.
- 1,000 all-candidate snapshots.
- 200 resolved markets.
- At least 100 shadow trades selected by the particle engine.

Minimum before promotion:

- 2 weeks shadow.
- 1,000+ all-candidate decisions.
- 200+ selected shadow decisions.
- At least 4 non-overlapping walk-forward windows.

## 6. Particle State Vector

Each particle represents one plausible hidden market state at time `t`.

State vector:

```text
x_t = {
  drift_1s_log,
  drift_5s_log,
  vol_1s_log,
  vol_5s_log,
  vol_30s_log,
  jump_intensity_per_second,
  jump_mean_log,
  jump_scale_log,
  mean_reversion_strength,
  trend_persistence,
  boundary_pressure,
  market_maker_staleness,
  kalshi_attention,
  liquidity_trust,
  panic_state,
  regime_id,
  clock_phase,
  model_bias
}
```

Important state meanings:

- `drift_1s_log`: immediate expected one-second log return.
- `drift_5s_log`: smoothed short impulse in log-return units.
- `vol_*_log`: latent log-return volatility for the stated horizon.
- `jump_intensity_per_second`: probability of a jump in the next second.
- `mean_reversion_strength`: whether recent impulse is likely to fade.
- `trend_persistence`: whether recent impulse is likely to continue.
- `boundary_pressure`: how much the strike boundary is shaping behavior.
- `market_maker_staleness`: Kalshi price/book lag relative to BTC.
- `kalshi_attention`: whether liquidity/order book is responsive.
- `liquidity_trust`: whether displayed depth is likely real/executable.
- `panic_state`: spread/depth/vol shock state.
- `model_bias`: online correction from recent calibration residuals.

Unit discipline:

- Price simulation should happen in log-price units.
- Strike comparison should convert only at terminal evaluation:
  `terminal_yes = exp(logS_T) > strike`.
- Volatility state should be per-second or clearly annualized; never mix units
  silently.
- `drift` and `micro_pressure` must be in log-return-per-second units.
- Fee/EV computations must remain in cents per contract.

## 7. Transition Model

At each second, propagate every particle from `t` to `t+1`.

Base log-price transition:

```text
logS_{t+1} = logS_t
           + drift_1s_t
           + sigma_1s_t * eps_t
           + jump_t
           + micro_pressure_t
```

Where:

- `dt = 1 second`.
- `eps_t ~ Normal(0, 1)`.
- `sigma_1s_t` is one-second log-return volatility.
- `jump_t = 0` with probability `1 - lambda_t`.
- `jump_t ~ HeavyTail(mu_jump, scale_jump)` with probability `lambda_t`.
- `micro_pressure_t` comes from short-term order-flow and stale-market state.

Volatility transition:

```text
log_sigma_{t+1} =
  a * log_sigma_t
  + (1 - a) * log_sigma_observed
  + vol_of_vol * eta_t
```

Jump intensity transition:

```text
lambda_{t+1} =
  sigmoid(
    base_jump
    + b1 * abs_return_1s
    + b2 * abs_return_5s
    + b3 * volume_shock
    + b4 * spread_widening
    + b5 * seconds_to_close_pressure
  )
```

Trend/reversion transition:

```text
trend_persistence_{t+1} =
  decay * trend_persistence_t
  + update_from_recent_signed_returns
  - reversion_penalty_near_exhaustion
```

The model should allow both:

- continuation after real impulse;
- reversal after overextended chase.

### 7.1 First Transition Model Should Be Conservative

Do not start with the full state vector. Start with:

```text
logS_{t+1} = logS_t + sigma_1s_t * eps_t
```

Then add one component at a time:

1. stochastic volatility;
2. jump hazard;
3. short impulse drift;
4. trend/reversion mixture;
5. Kalshi stale-market micro-pressure.

Each addition must earn its place by improving OOS Brier/log loss or EV ranking.
If a component improves replay PnL but worsens calibration or rank quality, it
goes to the watchlist, not production.

## 8. Observation Model

After propagating particles, weight them by how compatible they are with the
new observations.

Observations:

```text
y_t = {
  btc_price_observed,
  btc_return_1s,
  btc_return_5s,
  btc_range_5s,
  btc_volume_5s,
  kalshi_mid_yes,
  kalshi_mid_no,
  kalshi_spread,
  kalshi_depth,
  book_age_ms,
  market_price_change,
  candidate_ask,
  current_model_probability
}
```

Observation likelihood:

```text
weight_i =
  price_likelihood
  * volatility_likelihood
  * kalshi_price_likelihood
  * liquidity_state_likelihood
  * regime_likelihood
```

For numerical stability, compute this in log space:

```text
log_weight_i =
  log_price_likelihood_i
  + log_volatility_likelihood_i
  + log_kalshi_price_likelihood_i
  + log_liquidity_state_likelihood_i
  + log_regime_likelihood_i
```

Then subtract `max(log_weight)` before exponentiating.

Do not make Kalshi market price a hard truth. It should be an observation with
noise, because market price can be stale, thin, manipulated, or slow.

Suggested Kalshi observation noise:

- Low noise when book is fresh, deep, tight, and responsive.
- High noise when book is stale, thin, wide, or near expiry.
- Very high noise during BTC jump bursts.

### 8.1 BTC Price Observation Is Special

BTC spot is not just another weak observation. It is the current anchor for the
terminal probability.

Recommended update:

1. Use the observed BTC price to compute returns, vol shocks, and jump evidence.
2. Weight latent particles according to how plausible their latent dynamics are.
3. Reset/anchor the simulation start price to observed BTC for terminal
   projection.

This avoids an error where a particle with the wrong current spot accidentally
drives terminal probability.

### 8.2 Kalshi Price Observation Noise

Kalshi price observation noise should be state-dependent:

```text
kalshi_noise =
  base_noise
  + stale_book_penalty
  + wide_spread_penalty
  + thin_depth_penalty
  + btc_jump_penalty
  + near_expiry_penalty
```

If `kalshi_noise` is large, market price should barely affect particle weights.
If `kalshi_noise` is small, market price can pull the latent fair probability
toward the market's belief.

## 9. Resampling

Track effective sample size:

```text
ESS = 1 / sum(w_i^2)
```

Resample when:

- `ESS < 0.5 * particle_count`
- or a large observation shock causes particle collapse
- or clock rolls into final 60 seconds

Use systematic resampling.

After resampling:

- add small roughening noise to volatility and drift;
- keep price anchored to observed BTC;
- avoid particle impoverishment by preserving regime diversity.

Implementation detail:

```text
ESS = 1 / sum(normalized_weight_i ** 2)
```

If particles carry log weights, normalize first. If resampling happens, reset
weights to equal values.

## 10. Terminal Projection

At every decision second, project particles forward to settlement.

For each current particle:

1. Simulate many second steps until close.
2. Use the current latent state as the starting condition.
3. Apply time-to-close-specific volatility and jump transitions.
4. Record terminal price.
5. Convert terminal price to yes/no result.

Output:

```text
p_yes = weighted_mean(terminal_price > strike)
p_no = 1 - p_yes
p_side = p_yes if side == yes else p_no
```

The engine should also output:

- terminal price quantiles;
- path max/min quantiles;
- probability of crossing strike before settlement;
- probability of ending within 1 sigma of strike;
- probability of late reversal.

Even though Kalshi resolves on terminal price, path metrics matter because they
predict adverse exits, panic states, and fill quality.

### 10.1 Live Projection vs Offline Projection

Offline research may use expensive nested simulation:

```text
2,000 particles * 50 terminal paths each
```

Live shadow should start cheaper:

```text
2,000 latent particles * 1 to 5 terminal paths each
```

Because all active Kalshi BTC 15m markets share the same underlying BTC path
distribution, generate terminal BTC samples once per second, then evaluate all
active strikes against the same terminal sample vector.

Efficient live pattern:

```text
terminal_samples = simulate_terminal_prices(latent_particles, observed_spot)
for market in active_markets:
    p_yes[market] = weighted_mean(terminal_samples > market.strike)
```

This is much cheaper than re-simulating a separate BTC universe for every
market/side.

### 10.2 Boundary Cases

Special cases:

- If `seconds_to_close <= 0`, use settlement/market status, not simulation.
- If `seconds_to_close <= 5`, increase path resolution and widen calibration
  intervals because tiny timestamp differences can flip labels.
- If BTC price is missing or stale, do not simulate a confident probability.
  Emit `risk_state=btc_stale_unknown`.
- If strike is far from spot and probability saturates near 0 or 1, report
  clipped calibrated values, not raw 0/1 certainty.

## 11. Multi-Scale Next-Second Features

The feature bus should compute three parallel families:

Standard frames:

- 1s, 5s, 15s, 60s

Log frames:

- 1s, 2s, 4s, 8s, 16s, 32s, 64s, 128s, 256s, 512s

Phi/Fibonacci frames:

- 1s, 2s, 3s, 5s, 8s, 13s, 21s, 34s, 55s, 89s, 144s, 233s, 377s, 610s

For each frame compute:

- signed return;
- side-aligned return;
- realized volatility;
- range;
- volume shock;
- direction persistence;
- reversal after impulse;
- distance-to-strike change;
- Kalshi price response lag.

The win condition for phi frames is not beauty. It is:

- lower feature redundancy;
- better OOS probability score;
- better EV ranking;
- more stable WFA PnL.

## 12. Social/Microstructure State Layer

This layer converts market behavior into state variables.

States:

- `stale_mm_state`: Kalshi price not updating after BTC move.
- `panic_state`: BTC volatility spike plus book widening/thinning.
- `crowded_state`: one side has unusually large displayed depth.
- `fake_depth_risk`: displayed depth appears but fill quality is poor.
- `chase_state`: Kalshi or BTC chasing a recent impulse.
- `late_fear_state`: last minutes where liquidity disappears.
- `disagreement_state`: BTC physics probability and Kalshi price disagree.
- `quiet_trust_state`: book fresh, depth stable, BTC movement ordinary.

Important: call this social/microstructure, not psychographics in the human
marketing sense. We are modeling behavior of the market crowd and market maker.

## 13. Pinball Peg Layer

The pinball layer represents interpretable gates the trade passes through.

Example pegs:

- `peg_p_side_ge_70`
- `peg_p_side_ge_80`
- `peg_particle_interval_narrow`
- `peg_expected_pnl_pos`
- `peg_depth_ge_required`
- `peg_book_fresh`
- `peg_btc_fresh`
- `peg_spread_tight`
- `peg_near_strike`
- `peg_late_market`
- `peg_jump_risk_high`
- `peg_stale_mm`
- `peg_chase_with_side`
- `peg_chase_against_side`
- `peg_liquidity_trust_good`
- `peg_fill_prob_good`
- `peg_model_disagreement_low`

The model should learn:

- which pegs help;
- which pegs harm;
- which peg combinations matter;
- where a trade becomes too fragile.

Preferred first implementation:

- additive Bayesian/shrinkage peg scorer;
- then shallow tree or monotone gradient model;
- avoid deep black-box models until the all-candidate table is large.

## 14. Calibration Wrapper

Particle output is not automatically calibrated. It must pass through an online
calibration layer.

Recommended layers:

1. Raw particle `p_side`.
2. Beta or temperature calibration on rolling training windows.
3. ACI/conformal probability interval.
4. Regime-specific residual correction.
5. E-process monitoring for live edge decay.

The final trade probability should be:

```text
p_trade = calibrated_particle_probability
p_low   = conformal_lower_probability
p_high  = conformal_upper_probability
```

Decision should use `p_trade`, but sizing should use `p_low`.

### 14.1 Calibration Timing

At prediction time:

```text
p_raw = particle_model.predict(...)
p_cal = calibrator.predict(p_raw, context)
interval = conformal.predict_interval(p_cal, context)
```

After settlement:

```text
calibrator.update(prediction_id, realized_label)
conformal.update(nonconformity_score)
```

Do not call an update method during live prediction unless the label is already
known. That would create leakage in replay and impossible behavior live.

### 14.2 What to Calibrate

Calibrate at least three objects:

- `p_yes_terminal`
- `p_side_terminal`
- `expected_pnl_cents` buckets

The probability can be well calibrated while EV ranking is bad. The EV model
needs its own reliability curve:

```text
predicted EV bucket -> realized average PnL
```

## 15. EV and Fillability Decision Layer

Expected PnL per candidate:

```text
win_profit = 100 - ask_cents - fee_if_win_cents
loss_cost  = ask_cents + fee_if_loss_cents

raw_ev =
  p_side * win_profit
  - (1 - p_side) * loss_cost

fill_adjusted_ev =
  fill_prob * raw_ev
  - (1 - fill_prob) * missed_opportunity_cost_cents
  - adverse_selection_cost
```

Fee caveat:

- Use the bot's actual logged fee fields when available.
- If the fee schedule depends on price, payout, or venue rules, model
  `fee_if_win_cents` and `fee_if_loss_cents` separately.
- Never hard-code a universal fee constant inside the particle model.

Break-even probability:

```text
p_break_even =
  loss_cost / (win_profit + loss_cost)
```

Trade EV gate:

```text
p_low > p_break_even
and fill_adjusted_ev > min_ev_cents
```

No-fill handling:

- An unfilled IOC usually has realized PnL of zero.
- It still matters because repeated no-fills consume time, miss alternatives,
  and indicate that displayed liquidity may be fake/stale.
- The fill model should be trained on submitted orders and all candidate
  snapshots, not settlement winners alone.

Trade only if:

- `fill_adjusted_ev > min_ev_cents`;
- `p_low` is above break-even;
- fill probability is high enough;
- particle interval is not too wide;
- no stale/panic kill state is active;
- WFA-locked strategy version allows the state.

## 16. Implementation Milestones

### Phase 0: Design Freeze

Artifacts:

- `docs/research/NEXT_SECOND_PARTICLE_SIMULATION_PLAN.md`
- `docs/research/NEXT_SECOND_PARTICLE_SCHEMA.md`
- `docs/research/NEXT_SECOND_PARTICLE_PROMOTION_GATES.md`

Acceptance:

- Clear schema.
- Clear non-live scope.
- Clear metrics and promotion gates.

### Phase 1: Recorder Upgrade

Goal:

Collect the data needed for a real test.

Build:

- second-level BTC bar recorder;
- optional tick recorder;
- Kalshi book snapshot recorder;
- all-candidate snapshot logger;
- settlement label joiner.

Acceptance:

- 24 hours continuous recording.
- No gaps above 5 seconds without explicit gap flags.
- Every candidate row has settlement label after resolution.
- Filled, skipped, rejected, and no-fill outcomes are all represented.
- Strict replay can choose `recv_ts_utc` and reproduce exactly what was known.
- Both YES and NO candidate sides are represented whenever executable quotes
  exist.

### Phase 2: Offline Replay Harness

Goal:

Replay historical second-by-second state exactly as the bot would have seen it.

Build:

- `research_particle_replay.py`
- deterministic replay clock;
- market/candidate iterator;
- as-of joiner;
- no future leakage checks.

Acceptance:

- Replays one market from open to close.
- Replays one day of markets.
- Reconstructs candidate snapshots causally.
- Produces identical output with same seed.
- Fails loudly if a feature uses future data.
- Can run in two modes:
  - `strict_live_replay`: receive-time causal only;
  - `diagnostic_backfill`: allows backfilled candles/books and labels rows as
    diagnostic-only.

### Phase 3: Brownian Particle Baseline

Goal:

Start simple.

Model:

- particles follow driftless Brownian motion;
- volatility estimated from recent 1s/5s/60s realized vol;
- no jumps;
- no Kalshi observation weighting.

Acceptance:

- Terminal probability roughly matches analytic Brownian terminal model.
- Brier/log loss not worse than existing Brownian by more than 5 percent.
- Runtime under 50 ms for one shared market update with 2,000 particles in
  vectorized mode.
- Weighted terminal probability equals analytic terminal probability within a
  small Monte Carlo tolerance on synthetic tests.

### Phase 4: Jump-Volatility Particle Model

Add:

- stochastic volatility;
- jump intensity;
- jump size distribution;
- volatility regime transitions.

Acceptance:

- Improves Brier/log loss vs Brownian particle baseline.
- Better calibration during high-vol regimes.
- No OOS collapse in low-vol regimes.

### Phase 5: Kalshi Observation Weighting

Add:

- market price as noisy observation;
- book freshness;
- depth/liquidity trust;
- stale market-maker state.

Acceptance:

- Improves ranking of candidate EV.
- Does not blindly follow stale Kalshi price.
- Improves or preserves calibration.
- Ablation confirms that stale-book rows receive lower Kalshi observation
  weight than fresh/deep/tight rows.

### Phase 6: Social/Pinball State Integration

Add:

- social/microstructure states;
- pinball pegs;
- shallow EV scorer.

Acceptance:

- Pinball features improve EV ranking on all candidates.
- Selected top quartile has positive realized PnL.
- WFA windows are not one-window dependent.

### Phase 7: Online Calibration

Add:

- rolling beta/temperature calibration;
- ACI interval;
- conformal coverage report;
- e-process edge monitor.

Acceptance:

- Coverage between 85 and 95 percent for 90 percent target.
- Calibrated particle probability improves Brier/log loss.
- E-process does not false-promote no-edge windows.

### Phase 8: Shadow Deployment

Run:

- particle engine in separate shadow process;
- no orders;
- all predictions logged;
- compare against current bot decisions.

Acceptance:

- 200+ selected shadow decisions.
- Positive net shadow counterfactual PnL after fees, using predeclared no-fill
  and missed-opportunity assumptions.
- EV rank correlation positive.
- At least 3/4 WFA windows positive.
- Shadow PnL at least 50 percent of retrospective projection.
- Particle decisions are compared against every current-bot candidate and every
  particle-only candidate, not only filled trades.

### Phase 9: Limited Live Experiment

Only after Phase 8 passes.

Rules:

- size 1;
- hard daily loss cap;
- no same-market averaging until proven;
- live mode behind explicit env flag;
- instant rollback to shadow.

Acceptance:

- 100 live trades without operational failure.
- No calibration collapse.
- No drawdown beyond cap.
- PnL and hit rate consistent with shadow confidence interval.

## 17. Validation Protocol

Probability metrics:

- Brier score.
- Log loss.
- AUC.
- Calibration curve.
- ECE.
- Coverage of conformal intervals.

Trading metrics:

- realized PnL;
- average cents per entry;
- win/loss rate;
- coverage;
- max drawdown;
- fill rate;
- no-fill rate;
- adverse selection after fill;
- EV rank correlation;
- top-quartile EV PnL.

Stability metrics:

- WFA positive windows;
- parameter stability;
- no single window contributes over 40 percent of PnL;
- CPCV median positive;
- 25th percentile path positive;
- e-process threshold behavior.

## 18. Anti-Overfit Rules

Hard rules:

- No tuning on final OOS.
- No promotion from filled-trade replay only.
- No low-count strategy promotion.
- No accepting a model with negative EV rank correlation.
- No accepting a model that improves PnL but worsens probability calibration badly.
- No accepting a model where one window explains most gains.

Recommended lockout:

- Tune on first 40 percent.
- Validate on next 30 percent.
- Lock parameters.
- Test on final 30 percent.
- Then run fresh shadow.

## 19. Performance Engineering

Initial targets:

- 2,000 latent particles for the shared BTC process.
- 50 projection paths per particle for offline research only.
- 1 to 5 projection paths per particle for first live shadow.
- Under 100 ms per full candidate update.
- Under 1 second to update all active BTC 15m markets.

Optimizations:

- vectorized NumPy arrays;
- precomputed random shocks;
- shared particle cloud for markets with same BTC spot;
- strike-specific terminal evaluation only at the final step;
- adaptive particle count near decision boundaries;
- lower particle count when strike is far away.
- common random numbers across candidate strategies so bakeoffs compare the
  model, not Monte Carlo noise.

## 20. First Prototype Algorithm

Pseudocode:

```python
for each second:
    obs = feature_bus.asof(now)

    for market in active_btc_15m_markets:
        state = particle_state[market]

        particles = propagate_particles(state.particles, obs)
        weights = observation_likelihood(particles, obs, market)
        particles = normalize_weights(particles, weights)

        if effective_sample_size(particles) < threshold:
            particles = resample_and_roughen(particles)

        terminal = simulate_to_settlement(particles, market.close_time)
        p_yes_raw = weighted_mean(terminal.price > market.strike, particles.weights)
        p_yes_cal = calibrator.predict(market, p_yes_raw)
        interval = conformal_interval(market, p_yes_cal)

        for side in ["yes", "no"]:
            p_side = p_yes_cal if side == "yes" else 1 - p_yes_cal
            ev = expected_pnl(p_side, market.ask(side), fee, fill_prob)
            log_shadow_decision(market, side, p_side, interval, ev)

after market resolution:
    for prediction in unresolved_predictions_for_market:
        label = settlement_label(prediction.market)
        calibrator.update(prediction, label)
        conformal.update(prediction, label)
```

## 21. Expected Failure Modes

Model failures:

- particle volatility too slow to adapt;
- jump intensity overfits noise;
- Kalshi price observation overtrusted;
- particle degeneracy after large BTC move;
- model becomes overconfident near settlement;
- terminal probability good but EV selection bad.

Data failures:

- second recorder gaps;
- timestamp skew;
- stale book treated as fresh;
- candidate denominator incomplete;
- settlement labels misjoined.
- event-time/receive-time leakage;
- synthetic/backfilled candles mixed into strict validation;
- only one side logged when the other side was executable.

Trading failures:

- positive fair value but no fill;
- high fill probability but adverse selection;
- fees erase tiny edges;
- too few trades after uncertainty gating;
- live market changes after shadow period.

## 22. Promotion Gates

Do not promote unless all are true:

- Brier improves over capped ACI or Brownian terminal baseline.
- Log loss does not worsen.
- EV rank correlation is positive on OOS.
- Top EV quartile is profitable on OOS.
- Robust selected strategy has positive PnL in at least 3/4 WFA windows.
- No single WFA window contributes over 40 percent of total positive PnL.
- Forward shadow has at least 200 selected decisions.
- Forward shadow PnL is positive after fees.
- Fill-adjusted EV remains positive after no-fill and slippage penalties.
- E-process does not contradict the edge.
- Strict live-replay result remains directionally similar to diagnostic
  backfill result.
- Particle model beats a cheap baseline that uses the same all-candidate
  denominator and no particle simulation.

## 23. Prototype File Layout

Suggested research-only files:

```text
research_particle/
  __init__.py
  schemas.py
  recorder_second_bars.py
  recorder_candidate_snapshots.py
  feature_bus.py
  particle_state.py
  transition_models.py
  observation_models.py
  terminal_projection.py
  calibrators.py
  ev_decision.py
  replay.py
  validation.py
  reports.py
```

Suggested artifact paths:

```text
logs/particle_research/
  btc_second_bars/
  kalshi_book_seconds/
  candidate_snapshots/
  prediction_logs/
  settlement_labels/
  reports/
```

Do not mix these artifacts into live bot state. Research artifacts should be
append-only or versioned.

## 24. Synthetic Test Suite

Before using real market data, build synthetic tests.

Tests:

- Constant-vol Brownian terminal probability matches analytic normal CDF.
- Weighted particles and resampled particles produce the same probability
  within Monte Carlo error.
- Jump hazard increases tail probability in the correct direction.
- Calibrator does not update until labels are supplied.
- Replay refuses future data.
- Terminal label uses `S_T > strike`, not path crossing.
- EV formula matches hand-computed examples.
- No-fill events produce zero realized trade PnL but still update fill model.
- Shared terminal samples produce identical probabilities to per-market
  simulation when using the same random seed.

These tests are not optional. They are what prevent a particle engine from
becoming an expensive random-number generator with a good story.

## 25. Minimal Viable Prototype

The first useful prototype should be smaller than the full dream.

MVP:

- one BTC second-bar source;
- all-candidate snapshots once per second;
- Brownian anchored particles;
- stochastic volatility only;
- no Kalshi price observation weighting;
- no live trading;
- terminal `p_yes`;
- beta/ACI calibration after settlement;
- EV report on all candidates.

MVP success:

- Replays one full day causally.
- Produces calibrated `p_yes` for every active market/second.
- Beats or matches Brownian terminal baseline on Brier/log loss.
- Shows positive EV ranking on all candidates.

Only after this passes should we add jumps, social states, pinball pegs, and
Kalshi observation weighting.

## 26. Work Breakdown

This section turns the plan into research tickets.

### WP1: Second-Level Recorder

Goal:

Build causal data capture without touching live order logic.

Deliverables:

- `research_particle/recorder_second_bars.py`
- `research_particle/recorder_candidate_snapshots.py`
- append-only parquet or ndjson writers under `logs/particle_research/`
- gap reporting script

Acceptance tests:

- 24-hour run without crashing.
- gap report identifies every BTC gap over 5 seconds.
- every row has `ts_utc`, `recv_ts_utc`, and `quality_flag`.
- recorder can run while bot is live without changing bot decisions.

Stop conditions:

- recorder changes live trading behavior;
- rows have ambiguous timestamps;
- candidate rows include only fills and omit skips.

### WP2: Settlement Labeler

Goal:

Create trustworthy labels for every candidate.

Deliverables:

- `research_particle/settlement_labeler.py`
- `particle_settlement_labels` table
- label quality audit report

Acceptance tests:

- every resolved market gets one label;
- unresolved markets remain explicitly unresolved;
- label join never uses settlement before `label_available_ts_utc`;
- labels match known Kalshi market outcomes on sampled markets.

Stop conditions:

- labels depend on future data in replay;
- settlement price source is unclear;
- one market maps to multiple conflicting labels.

### WP3: Strict Replay Clock

Goal:

Replay exactly what the model would have known at each second.

Deliverables:

- `research_particle/replay.py`
- `strict_live_replay` mode
- `diagnostic_backfill` mode
- leakage-audit report

Acceptance tests:

- deterministic output with fixed random seed;
- replay refuses features with `recv_ts_utc > decision_ts_utc`;
- strict and diagnostic modes are clearly separated in reports;
- one-day replay finishes in a reasonable time.

Stop conditions:

- replay silently backfills missing BTC/book data;
- shadow decisions are generated at times where quote data was unavailable.

### WP4: Brownian Anchored Particle Baseline

Goal:

Prove the particle machinery works before adding cleverness.

Deliverables:

- `research_particle/particle_state.py`
- `research_particle/transition_models.py`
- `research_particle/terminal_projection.py`
- synthetic Brownian validation report

Acceptance tests:

- Monte Carlo terminal probability matches analytic Brownian terminal CDF.
- weighted and resampled estimates agree within tolerance.
- terminal label is `S_T > strike`, not touch/cross.
- runtime target met for one shared BTC update.

Stop conditions:

- Brownian particle output disagrees with analytic baseline without a clear
  Monte Carlo-error explanation;
- probability saturates at 0 or 1 too often.

### WP5: Probability Calibration

Goal:

Make raw particle probabilities honest.

Deliverables:

- `research_particle/calibrators.py`
- rolling beta/temperature calibration
- ACI/conformal interval
- calibration report

Acceptance tests:

- calibrator predicts before settlement and updates only after labels.
- Brier/log loss improves or stays within tolerance.
- 90 percent interval coverage lands between 85 and 95 percent after warmup.
- calibration curves are reported by volatility and time-to-close regime.

Stop conditions:

- calibration improves aggregate Brier but destroys high-confidence decision
  quality;
- interval width fails to widen during known jump/stale regimes.

### WP6: Jump/Volatility Model

Goal:

Add realism only after baseline works.

Deliverables:

- jump hazard estimator
- stochastic volatility transition
- ablation report

Acceptance tests:

- high-vol regime calibration improves;
- low-vol regime does not degrade materially;
- jump hazard is stable across WFA windows;
- ablation shows which component earned its place.

Stop conditions:

- jump model only helps one isolated window;
- jump parameters become unstable or nonsensical;
- log loss worsens while replay PnL improves.

### WP7: Kalshi Observation Weighting

Goal:

Let Kalshi market data inform the latent state without blindly trusting it.

Deliverables:

- `research_particle/observation_models.py`
- state-dependent Kalshi observation noise
- stale/fresh ablation report

Acceptance tests:

- fresh/deep/tight books receive stronger observation weight;
- stale/thin/wide books receive weaker observation weight;
- Kalshi observation improves EV ranking without hurting calibration;
- stale-market cases do not force the particle model to follow bad prices.

Stop conditions:

- model becomes a disguised Kalshi-price follower;
- stale rows get high confidence;
- market price leakage appears in strict replay.

### WP8: Fillability and Adverse Selection

Goal:

Make EV executable, not theoretical.

Deliverables:

- fill probability model
- no-fill opportunity cost estimate
- post-fill adverse selection report

Acceptance tests:

- fill model is trained on submissions and all candidates, not fills only.
- fill probability has positive rank correlation with actual fill outcomes.
- EV report includes raw EV and fill-adjusted EV separately.
- high-fill states do not systematically have worse post-fill returns.

Stop conditions:

- fill model is just depth ratio with no forward lift;
- fill-adjusted EV is positive only by ignoring no-fills or fees.

### WP9: Social/Pinball Layer

Goal:

Add interpretable market-behavior states after the probability engine is sound.

Deliverables:

- social/microstructure state builder
- pinball peg generator
- shallow EV scorer
- peg attribution report

Acceptance tests:

- peg layer improves EV ranking on all candidates.
- top EV quartile is positive OOS.
- important pegs are stable across WFA windows.
- no single peg creates a low-sample overfit strategy.

Stop conditions:

- negative EV rank correlation;
- improvements only appear on filled-row replay;
- peg attribution changes wildly between windows.

### WP10: Shadow Runner

Goal:

Run the engine live in observation mode only.

Deliverables:

- particle shadow process
- prediction log
- daily shadow report
- e-process monitor

Acceptance tests:

- 200+ selected shadow decisions.
- positive forward PnL after fees.
- positive EV rank correlation.
- no operational interference with live bot.
- shadow output can be replayed from logs.

Stop conditions:

- shadow process lags or drops markets;
- selected decisions are too sparse;
- e-process fails to support edge;
- prediction logs cannot reconstruct decisions.

## 27. Logic Audit Checklist

Use this checklist before every claimed result.

Target correctness:

- Does the label measure terminal `BTC settlement > strike`?
- Are crossing/touch metrics separated from terminal win labels?
- Are YES and NO probabilities complements after calibration?
- Are prices clipped only for numerical stability, not to hide uncertainty?

Causality:

- Are all features available at decision receive time?
- Are settlement labels excluded until after resolution?
- Are backfilled rows marked and excluded from strict scoring?
- Is the train/validation/test split chronological?

Particle math:

- Are weights normalized before ESS?
- Is terminal probability weighted unless resampled?
- Is current spot anchored to observed BTC?
- Are drift and volatility units consistent?
- Are common random numbers used for strategy bakeoffs?

Calibration:

- Does the calibrator update only after labels?
- Is calibration evaluated separately from EV ranking?
- Does uncertainty widen during stale/jump regimes?
- Does high-confidence probability actually correspond to high hit rate?

EV:

- Are fees modeled from logged fields?
- Is break-even probability computed from ask and fees?
- Is no-fill treated separately from loss?
- Does fill-adjusted EV remain positive after adverse-selection penalties?

Validation:

- Does OOS Brier/log loss improve or hold steady?
- Is EV rank correlation positive?
- Is top predicted EV quartile profitable?
- Are at least 3/4 WFA windows positive?
- Is no single window carrying the result?
- Does fresh shadow resemble retrospective projection?

Promotion:

- Is the result based on all candidates, not filled rows only?
- Does it beat cheap baselines using the same denominator?
- Does it pass e-process monitoring?
- Is there enough sample size?
- Is live use still behind an explicit opt-in flag?

If any answer is no, the model can still be interesting, but it is not
promotable.

## 28. Accuracy Notes

These are the highest-risk accuracy points in the plan.

1. Terminal probability is the main product.

   The model can calculate crossing probability, last-exit probability, or path
   danger metrics, but Kalshi BTC 15m winner/loser labels are terminal.

2. A particle filter is not automatically better than Brownian.

   If the jump/vol/social layers do not improve OOS probability or EV ranking,
   remove them. Complexity is not edge.

3. Kalshi market price is useful but dangerous.

   Market price may be a good aggregate forecast in fresh liquid books, but it
   may be stale or distorted near fast BTC moves. Observation noise must depend
   on book state.

4. EV ranking is harder than probability calibration.

   A probability model can have good Brier score and still choose bad trades
   because ask, fees, fillability, and adverse selection matter.

5. Filled-row replay is not strategy proof.

   Filled rows have already passed the old bot's filter. The next-second engine
   needs the all-candidate surface to learn what to accept and what to reject.

6. Runtime design matters.

   Per-market nested Monte Carlo can explode. Shared BTC terminal samples across
   strikes are the live-friendly design.

7. The first production-like output should be shadow only.

   The model should be boringly reliable in logs before it is allowed to affect
   real orders.

## 29. Final Reviewer Notes

This section is the build-order lock. It exists to keep the project from
turning into a beautiful simulator that wins only because it saw the replay
too clearly.

Build in this order:

1. Recorder and labeler.

   The first real product is not a model. It is a trustworthy all-candidate
   dataset with event-time, receive-time, book freshness, executable quotes,
   fill/no-fill, and terminal settlement labels.

2. Synthetic benchmark.

   Before any Kalshi feature matters, the engine must pass Brownian and
   jump-diffusion synthetic tests where the true answer is known.

3. Strict replay baseline.

   The first Kalshi replay must use only information available at the decision
   timestamp. Diagnostic backfill can exist, but it cannot be used for
   promotion.

4. Calibration wrapper.

   Raw particle probabilities do not get trusted. They must pass rolling
   calibration, Brier/log-loss, and coverage checks before EV gates use them.

5. EV and fillability.

   Probability quality is necessary but not enough. The decision layer must
   prove that predicted EV ranks future trade quality on all candidates, not
   only on old fills.

6. Social, pinball, and neural layers.

   These are add-ons, not foundations. Each one must beat the simpler particle
   model in locked OOS or it comes back out.

Hard prohibitions:

- Do not train on settlement labels that were not available at prediction
  time.
- Do not use filled-only rows as the main denominator.
- Do not use Kalshi market price as the training label for truth.
- Do not tune no-fill penalties, fee assumptions, or EV thresholds on the test
  window.
- Do not promote a model that improves PnL only by concentrating all gains in
  one window, one market, or one volatility regime.
- Do not put neural/deep layers into the critical path until the synthetic and
  simple-particle versions are already passing.

Remaining open questions to resolve before live impact:

- Exact settlement source timing and whether the logged spot feed matches the
  exchange's resolution source closely enough.
- Exact fee formula per contract and whether fee treatment differs by side,
  price, maker/taker status, or realized payout.
- Candidate sampling cadence: every second, quote-change only, or both.
- How to score a no-fill when the shadow decision would have been executable
  for some size but not for the desired size.
- Whether YES and NO prices should be modeled as separate executable contracts
  or as a single binary probability with side-specific liquidity.
- How existing positions, exits, and same-market exposure interact with a new
  particle entry signal.

The logic check is simple: if the model cannot win against Brownian, market
mid, and current calibrated probability on the same all-candidate denominator,
it is not yet a strategy. It is still research.

## 30. Ambitious End State

The final system should feel less like a threshold bot and more like a live
probability laboratory.

It should know:

- what BTC is doing now;
- how uncertain that motion is;
- how likely the next second is to continue or reverse;
- whether the Kalshi book is awake or stale;
- whether displayed liquidity is trustworthy;
- whether the strike is in a danger zone;
- whether the model's own recent residuals are drifting;
- whether the current price is worth paying after fees and fill risk.

The ideal decision is:

> Trade only when the particle distribution, calibration layer, liquidity
> state, and EV layer all agree that the opportunity is real.

That is the target. Everything before that is scaffolding.
