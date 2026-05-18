# v28 Successor Fair-Value Engine Spec

## 1. Purpose

Build a research-only successor to the v28 BTC 15-minute fair-value engine.

The objective is not to invent a new live trading rule first. The objective is to build a more accurate, causal, inspectable probability surface for Kalshi BTC 15-minute boundary markets:

- `P(YES settlement) = P(settlement > strike)`
- fair YES cents
- fair NO cents
- boundary and recross risk
- reliability and source-quality warnings

The successor must start from the v28 fair-value API and preserve the live bot boundary. It must use recorded BTC, Kalshi book, market metadata, and decision telemetry to build a causal labeled dataset where each row contains only information that was available before the market resolved.

The final result should be a model stack that can say:

```text
market: KXBTC15M-...
strike: 105000
seconds_to_close: 412
v28_raw_yes_probability: 0.871
successor_yes_probability: 0.824
fair_yes_cents: 82.4
fair_no_cents: 17.6
recross_hazard: elevated
reliability: medium
main_adjustments:
  - v28 overconfidence near boundary
  - short-vol regime elevated
  - book/physics disagreement present
  - source quality clean
```

This is a better FV engine only if it improves probability truth first. Trading P&L is secondary evidence.

## 2. Non-Negotiable Guardrails

This project is research-only until explicitly approved otherwise.

Do not:

- Modify live order logic.
- Modify live strategy thresholds.
- Modify secrets.
- Modify live state.
- Stop, restart, or interfere with the live bot.
- Place trades.
- Promote a candidate from recomputed-after-resolution rows.
- Treat historical P&L improvement as enough proof.
- Collapse the work into a narrow filter that merely avoids bad trades without improving FV truth.

Do:

- Keep v28 as the control baseline.
- Keep all changes in research files, reports, registries, or new research-only engine modules.
- Freeze candidate definitions before forward scoring.
- Score probability quality before fee-aware P&L.
- Separate pure physics probability from book-aware probability.
- Require source-quality accounting on every row.
- Require post-lock forward rows before promotion.

## 3. Current v28 Baseline To Preserve

The current v28 engine is a compact fair-value engine, not a full strategy.

Its public shape is:

```text
update_tick(price, ts)
update_bar(open, high, low, close, volume, ts)
predict_many(strikes, horizon_seconds)
edge_many(strikes, horizon_seconds, yes_ask_cents, no_ask_cents)
```

The live adapter computes opportunities and does not send orders by itself. The successor should keep this separation.

The v28 probability surface is broadly:

```text
Brownian terminal anchor
+ weak signed boundary/time-mirror arrow
+ empirical recent/long residual transport
+ transport temperature and edge gating
= p_yes, p_no, fair_yes_cents, fair_no_cents
```

The successor should not throw this away casually. v28 is the physics spine. The new work should identify where v28 is too confident, underconfident, stale, or blind to boundary instability.

## 4. Success Criteria

A successor candidate is successful only if it clears all of these categories.

### 4.1 Probability Quality

It must beat v28 on:

- Brier score.
- Log loss.
- Calibration error.
- Calibration slope and intercept.
- Expected calibration error.
- Bucket reliability.

The primary target is `P(YES settlement)`, not just `side_probability`.

Reason: `side_probability = max(p_yes, p_no)` hides direction and can make a model look good while flipping the YES/NO axis incorrectly.

### 4.2 Boundary Quality

It must improve or at least not degrade:

- Near-strike rows.
- High recross-risk rows.
- Late-window rows.
- High short-vol rows.
- Expensive ask rows.
- Book/physics disagreement rows.
- YES and NO side buckets separately.

The boundary is where v28 is most likely to become overconfident. A candidate that improves all-market Brier while worsening near-boundary calibration is not a true successor.

### 4.3 Source Quality

It must prove the improvement on rows that are:

- timestamped before resolution,
- not reconstructed after outcome,
- not dependent on future candles,
- not dependent on late book state,
- not mostly simulated,
- not mostly rejected/reconstructed rows if the target is broad live use.

Approved-only rows can be useful for calibration hints, but they are too narrow to prove a broad FV engine alone.

### 4.4 Coverage

Coverage should be measured over recurring BTC 15-minute markets, not just filled trades.

Targets:

- soft target: broad recurring-market coverage where possible,
- practical minimum for broad engine claims: roughly 75% to 80% recurring-market coverage,
- narrower variants allowed only if explicitly labeled narrow and if risk-adjusted improvement justifies the narrower scope.

### 4.5 Forward Evidence

Promotion requires:

- frozen candidate manifest,
- frozen feature list,
- frozen model parameters,
- lock timestamp,
- post-lock predictions recorded before settlement,
- enough forward rows for meaningful uncertainty,
- candidate-vs-v28 comparison on identical rows.
- per-candidate evidence maturity reporting: observed rows, required rows, row shortfall, observed markets, required markets, market shortfall, estimated additional markets needed, Brier delta, log-loss delta, near-boundary row count, and near-boundary Brier delta.
- default forward collection should preserve the nearest-close population unless an operator explicitly uses an auditable `--all-open-closes` research-only collection run; broader collection must still freeze rows before close and label only after resolution.

Historical discovery is only hypothesis generation.

### 4.6 Economics

After probability quality passes, score:

- fee-aware expected value,
- realized shadow P&L,
- drawdown,
- loss clusters,
- hold-to-settlement value,
- exit value versus hold,
- coverage versus v28,
- worst-split performance.

P&L cannot rescue a candidate whose probability calibration is worse.

## 5. Deliverables

The project should produce these durable artifacts.

### 5.1 Dataset Builder

Suggested file:

```text
build_v28_successor_causal_dataset.py
```

Purpose:

- Parse available logs, ledgers, market metadata, BTC candles, book snapshots, and v28 telemetry.
- Build a causal row-level dataset.
- Mark source quality.
- Mark row eligibility for training, validation, holdout, and promotion.
- Write dataset audit reports.

The current trimmed workspace may not have a root `research_data/` directory. The builder should discover available local sources first and only create a new canonical output directory if needed.

Suggested output location:

```text
research_particle/v28_successor/
logs/edge_research/v28_successor_*_latest.*
```

### 5.2 Baseline Replayer

Suggested file:

```text
replay_v28_successor_baselines.py
```

Purpose:

- Replay v28 on the causal rows.
- Recompute v28 components where possible.
- Preserve original logged v28 values when recomputation would risk drift.
- Compare recomputed and logged values.
- Flag divergence.

### 5.3 Feature Builder

Suggested file:

```text
build_v28_successor_features.py
```

Purpose:

- Convert raw causal rows into model-ready features.
- Produce pure physics features.
- Produce book-aware features.
- Produce source/reliability features.
- Include causal final-average physics proxies from the decision-time clock, v28 sigma, strike, and BTC spot. These are allowed as features only when they are computed before resolution and must not use future final-average samples.
- Produce leakage-safe feature manifests.

### 5.4 Candidate Trainer

Suggested file:

```text
train_v28_successor_fv_candidates.py
```

Purpose:

- Train simple inspectable challengers.
- Freeze model manifests.
- Produce calibration reports.
- Reject candidates that fail probability gates.

### 5.5 Forward Packet Adapter

Suggested file:

```text
build_v28_successor_forward_packet_adapter.py
```

Purpose:

- Provide a research-only sidecar adapter that converts a passive book checkpoint plus decision-time BTC history, v28 API outputs, and frozen collection-candidate manifests into complete packet-contract rows.
- Prove the packet schema can be satisfied before close without reading settlement labels.
- Keep demo/fixture rows clearly marked as synthetic and not promotion evidence.
- Give the next passive collection run a concrete implementation target for BTC state, native v28 components, and candidate prediction fields.

### 5.5.1 Sidecar Packet Collector

Suggested file:

```text
build_v28_successor_public_rest_sidecar_bundle.py
build_v28_successor_public_rest_sidecar_batch.py
collect_v28_successor_forward_packets.py
validate_v28_successor_sidecar_input_bundle.py
run_v28_successor_sidecar_bundle_freeze_handoff.py
run_v28_successor_sidecar_bundle_batch_handoff.py
fetch_v28_successor_sidecar_batch_settlement_labels.py
run_v28_successor_sidecar_batch_label_join_handoff.py
score_v28_successor_sidecar_batch_evidence.py
run_v28_successor_sidecar_collection_cycle.py
stage_v28_successor_sidecar_forward_evidence.py
run_v28_successor_market_coverage_loop.py
```

Purpose:

- Provide a research-only public REST one-shot builder that can transform current Kalshi market/orderbook snapshots plus recent BTC candles into the same sidecar input bundle schema used by the freezer path.
- Provide a research-only public REST batch builder that can capture all active nearest-close BTC15M boundary markets into separate sidecar input bundles in one explicit pre-close run.
- Provide a research-only executable bridge that can emit complete YES/NO candidate packet rows from a serialized pre-resolution input bundle.
- Provide a standalone bundle contract/template validator so malformed, future-dated, post-resolution, or label-contaminated bundles are blocked before packet collection.
- Support an input bundle containing market metadata, one book checkpoint, BTC history rows available before the checkpoint, a serialized v28 EdgeBatch, and frozen collection-candidate manifests.
- Provide a one-command bundle-to-freeze handoff that validates the input bundle, materializes packet rows, runs packet validation/preflight/freeze, and writes registry-shaped handoff artifacts without overwriting the canonical promotion registry.
- Provide a batch bundle handoff that scans a sidecar bundle directory and combines many pre-close market/checkpoint bundles into one packet/freeze handoff for broad-market coverage accounting.
- Preserve already-frozen valid pre-close sidecar batch rows when the batch handoff is rerun after close; a refresh may add new eligible open-market rows, but must never erase a frozen ledger simply because the old market is now closed.
- Provide a sidecar batch settlement-label fetcher that reads only frozen batch markets, refuses pre-close labels, fetches public Kalshi results after close, and writes a separate label CSV for the batch label joiner.
- Provide a separate batch label-join handoff that consumes only the sidecar batch frozen CSV, joins post-resolution labels into separate sidecar batch labeled artifacts, and does not overwrite the canonical promotion label ledger.
- Provide a sidecar batch evidence scorer that applies the same probability-first Brier/log-loss/calibration logic to settled sidecar batch rows while writing separate non-canonical artifacts and never granting promotion by itself.
- Provide a one-cycle sidecar runner that can optionally collect public REST bundles, preserve/freeze the batch ledger, fetch labels, join labels, score evidence, and refresh audits in a single repeatable research-only command.
- Provide a staging bridge that copies only valid pre-close sidecar frozen rows into the canonical frozen-forward input ledger, without copying labels into the frozen file and without granting promotion.
- Provide a bounded market-coverage loop runner that repeats the sidecar collection cycle plus canonical stage/registry/label/score/source/verifier/audit refresh, with public REST capture still requiring an explicit flag and promotion still blocked by downstream gates.
- The market-coverage loop report must separate global ledger floors from candidate-specific promotability. A large global ledger is not enough if the only high-sample candidates fail Brier/log-loss or near-boundary gates; the report should name the best quality-passing sample-limited candidate and its row/market shortfalls.
- Public REST collection should handle transient HTTP 429 rate limits with a small bounded backoff/retry, then report a collector blocker if the retry budget is exhausted. A preserved old frozen ledger is not a substitute for a newly captured pre-close checkpoint.
- Keep public REST fixture mode deterministic and non-evidence; real public REST collection must be explicitly requested and still must freeze before close.
- Keep default demo output synthetic and diagnostic, while making real input-bundle rows non-simulated and ready for packet validation and freeze handoff when captured before close.
- Never mark collector output as promotion evidence by itself; promotion still requires pre-close freeze, registry registration, post-resolution label join, probability scoring, source contract, and promotion verifier.
- Preserve the live bot boundary: the collector must not read or mutate live order state, thresholds, secrets, or processes.

### 5.6 Forward Registry

Suggested file:

```text
register_v28_successor_forward_predictions.py
```

Purpose:

- Record frozen candidate predictions before settlement.
- Include v28 baseline prediction on the same row.
- Include source quality.
- Include final outcome only after resolution.

### 5.7 Forward Label Joiner

Suggested file:

```text
join_v28_successor_forward_labels.py
run_v28_successor_sidecar_batch_label_join_handoff.py
```

Purpose:

- Attach settlement labels only after a prediction has already been frozen before close.
- Refuse rows where the label timestamp is missing, before close, or not after the frozen prediction.
- Produce row-level Brier/log-loss fields for candidate-vs-v28 comparison.
- Keep canonical frozen-forward label artifacts separate from sidecar batch label-join artifacts so broad collection experiments cannot masquerade as promotion-ledger evidence.
- Keep label joining necessary but not sufficient for promotion.

### 5.8 Candidate Comparator

Suggested file:

```text
score_v28_successor_candidates.py
```

Purpose:

- Compare every frozen candidate to v28.
- Produce calibration, boundary, source-quality, and economics tables.
- Output a single readiness verdict.

The forward-evidence scorer should be explicit:

```text
score_v28_successor_forward_evidence.py
```

It should read only rows that were frozen before close and labeled after resolution, score candidate-vs-v28 Brier/log loss/calibration/near-boundary slices on identical rows, and keep promotion closed unless forward probability quality clears the gates.

## 6. Data Source Discovery

The dataset builder should not assume one perfect research dataset exists. It should inspect the workspace and classify available evidence.

Likely local source categories:

- `logs/live_mushroom_v28_size2/bot.log`
- `logs/live_mushroom_v28_size2/execution_events.ndjson`
- `state/live_mushroom_v28_size2/recent_market_outcomes.json`
- `logs/edge_research/*v28*.csv`
- `logs/edge_research/*v28*.json`
- `logs/edge_research/*v28*.md`
- `handoff_gpt55_v28_live_context_20260501/*`
- shadow registries and frozen candidate ledgers
- market metadata caches if present
- BTC candle caches if present
- sidecar logs, if clearly labeled and kept separate

The builder should classify each source:

```text
approved_entry
rejected_actionable
heartbeat_snapshot
shadow_candidate
sidecar_candidate
recomputed_replay
historical_backfill
diagnostic_only
unknown
```

Rows from unknown or diagnostic-only sources may be used for exploration but not for promotion.

## 7. Causal Dataset Design

Each row should represent a decision-time market snapshot or heartbeat opportunity.

The key rule:

```text
No feature may use information that became available after decision_ts_utc.
```

### 7.1 Row Identity Columns

Required:

```text
row_id
decision_ts_utc
market_ticker
market_close_ts_utc
strike
seconds_to_close
source_file
source_line_or_offset
source_type
source_quality_tier
candidate_context
```

### 7.2 Causality Columns

Required:

```text
is_pre_resolution
is_pre_resolution_registered
is_recomputed_after_resolution
is_backfilled
is_simulated
is_sidecar
is_diagnostic_only
allowed_for_training
allowed_for_validation
allowed_for_holdout
allowed_for_forward_promotion
exclusion_reason
```

### 7.3 Market And Book Columns

Required where available:

```text
yes_bid_cents
yes_ask_cents
no_bid_cents
no_ask_cents
yes_mid_cents
no_mid_cents
yes_spread_cents
no_spread_cents
best_executable_yes_ask_cents
best_executable_no_ask_cents
yes_depth_at_ask
no_depth_at_ask
visible_depth_required
depth_ratio
book_ts_utc
book_age_ms
book_source
book_stale_flag
book_crossed_flag
book_missing_flag
```

Derived:

```text
book_yes_probability_mid
book_yes_probability_executable
book_no_probability_mid
book_no_probability_executable
book_favorite_side
book_favorite_probability
book_v28_probability_gap
book_physics_probability_gap
book_move_15s
book_move_30s
book_move_60s
book_move_180s
```

### 7.4 BTC And Feed Columns

Required where available:

```text
btc_spot
btc_source
btc_tick_ts_utc
btc_tick_age_ms
coinbase_spot
binance_spot
reference_spot
spot_feed_disagreement_dollars
spot_feed_disagreement_bps
rest_fallback_used
websocket_tick_used
btc_stale_flag
```

Recent return windows:

```text
btc_return_15s
btc_return_30s
btc_return_60s
btc_return_180s
btc_return_300s
btc_return_900s
btc_return_1800s
btc_return_3600s
```

Path windows:

```text
signed_move_1m_dollars
signed_move_3m_dollars
signed_move_5m_dollars
signed_move_15m_dollars
signed_move_30m_dollars
max_favorable_move_3m
max_favorable_move_5m
max_favorable_move_15m
max_adverse_move_3m
max_adverse_move_5m
max_adverse_move_15m
```

### 7.5 v28 Baseline Columns

Store the raw v28 YES-axis values and side-axis values.

Required:

```text
v28_p_yes
v28_p_no
v28_p_side
v28_best_side
v28_fair_yes_cents
v28_fair_no_cents
v28_best_fair_cents
v28_yes_edge_cents
v28_no_edge_cents
v28_best_edge_cents
```

Components:

```text
v28_p_anchor
v28_p_static_boundary_field
v28_p_recent_transport
v28_p_long_transport
v28_edge_gate
v28_static_gate
v28_arrow
v28_volshock
v28_transport_recent_n
v28_transport_long_n
v28_learned_horizon_minutes
v28_effective_horizon_minutes
v28_sigma_t_dollars
v28_d_sigma
```

Important:

If a row only logs side probability, reconstructing the YES-axis probability must be done carefully and labeled. Do not silently treat `p_side` as `p_yes`.

### 7.6 Settlement Label Columns

Primary label:

```text
y_yes_win
```

Settlement details:

```text
settlement_price
settlement_ts_utc
settlement_source
settlement_margin_dollars
settlement_side
```

Final-average details:

```text
final_average_window_start_utc
final_average_window_end_utc
known_final_average_samples_at_decision
known_final_average_sum_at_decision
known_final_average_count_at_decision
unknown_final_average_count_at_decision
inside_final_average_window
```

Do not use final-average samples that were not known at decision time as features.

### 7.7 Boundary And Recross Labels

Labels that are computed after outcome are allowed only as labels, not features.

Suggested labels:

```text
recross_before_close
recross_count_before_close
time_to_first_recross_seconds
time_since_last_recross_seconds_at_decision
max_adverse_excursion_to_close
max_favorable_excursion_to_close
near_boundary_duration_seconds
min_abs_margin_to_close
terminal_abs_margin
terminal_abs_margin_sigma
```

These labels let the project learn whether the candidate model is becoming more honest about unstable boundary states.

### 7.8 Trading Shadow Labels

Secondary labels:

```text
would_fill
fill_probability_estimate
entry_cost_cents
entry_fee_cents
exit_fee_cents
hold_to_settlement_pnl_cents
actual_exit_pnl_cents
best_exit_available_cents
exit_value_vs_hold_cents
max_drawdown_cents
max_unrealized_gain_cents
```

For v28 partial exits, corrected replay from raw execution events is preferred over summary JSON.

## 8. Feature Families

Every feature must be timestamp-safe.

### 8.1 Pure Physics Features

These do not use Kalshi book prices except market metadata like strike and close time.

Core:

```text
spot_minus_strike
strike_minus_spot
abs_spot_minus_strike
distance_to_strike_sigma
distance_to_strike_sqrt_time
seconds_to_close
minutes_to_close
inside_final_average_window
effective_settlement_horizon
```

Volatility:

```text
realized_vol_1m
realized_vol_3m
realized_vol_5m
realized_vol_15m
realized_vol_30m
realized_vol_60m
vol_ratio_short_long
volshock
range_vol_short
range_vol_long
```

Path:

```text
signed_drift_1m
signed_drift_3m
signed_drift_5m
signed_drift_15m
signed_drift_30m
velocity
acceleration
anti_persistence_score
trend_exhaustion_score
adverse_path_memory
favorable_path_memory
```

Boundary:

```text
recross_hazard_raw
recross_hazard_time_scaled
boundary_temperature
boundary_entropy
near_boundary_flag
ordinary_impulse_can_cross_flag
```

### 8.2 v28-Derived Features

These are model-internal baseline features.

```text
v28_logit_yes
v28_abs_logit
v28_p_anchor
v28_p_static_boundary_field
v28_p_recent_transport
v28_p_long_transport
v28_transport_delta_recent
v28_transport_delta_long
v28_arrow
v28_edge_gate
v28_static_gate
v28_sigma_t_dollars
v28_d_sigma
v28_transport_recent_n
v28_transport_long_n
```

### 8.3 Book-Aware Features

These may improve calibration, but must be labeled as book-aware rather than pure physical prediction.

```text
book_yes_probability_mid
book_yes_probability_executable
book_favorite_probability
book_spread_cents
book_depth_ratio
book_age_ms
book_move_recent
book_v28_gap
book_physics_gap
book_disagreement_abs
book_disagreement_signed
book_leads_spot_flag
book_lags_spot_flag
thin_edge_flag
expensive_ask_flag
crowded_depth_flag
```

### 8.4 Reliability Features

These should help the model know when to distrust itself.

```text
btc_tick_age_ms
book_age_ms
spot_feed_disagreement_bps
rest_fallback_used
transport_recent_n
transport_long_n
missing_feature_count
source_quality_tier
is_reconstructed
is_simulated
is_sidecar
```

Promotion-grade models should not depend heavily on low-quality source flags unless they are used only to reduce confidence or exclude rows.

## 9. Model Tracks

Use two tracks from the beginning.

### 9.1 Track A: Pure Physics FV

Purpose:

Estimate `P(YES settlement)` from BTC path, strike geometry, time, volatility, settlement-average state, and v28 physical components.

Allowed:

- BTC spot and history.
- Strike.
- Time to close.
- Volatility and path features.
- v28 physics components.
- final-average known samples as of decision time.

Not allowed:

- Kalshi bid/ask.
- Kalshi midpoint.
- Kalshi depth.
- Book-implied probability.

This track answers:

```text
What is the fair probability before looking at the market price?
```

### 9.2 Track B: Book-Aware Calibrated FV

Purpose:

Estimate calibrated market-realistic fair probability using both physical probability and Kalshi book information.

Allowed:

- all pure physics features,
- book probability,
- spread,
- depth,
- book movement,
- book/physics disagreement,
- source reliability.

This track answers:

```text
Given the physical model and the market's own price signal, what calibrated probability is most reliable?
```

Track B may be more accurate, but it must not be mislabeled as pure physics alpha.

### 9.3 Track C: Reliability And Recross Risk

Purpose:

Predict model fragility, not settlement direction directly.

Targets:

- recross before close,
- high adverse excursion,
- v28 probability error,
- book/physics disagreement persistence,
- stale feed or unreliable state.

Outputs:

```text
recross_hazard
probability_error_risk
source_reliability
confidence_shrink_factor
```

This track can temper probability confidence without becoming a hard trade filter.

## 10. Model Ladder

Start simple and inspectable.

### 10.1 Baseline 0: v28 Raw

Control:

```text
p_yes = v28_p_yes
```

All candidates must compare to this on identical rows.

### 10.2 Baseline 1: Brownian Terminal

Control:

```text
p_yes = Brownian/settlement-adjusted terminal probability
```

This tells whether v28 transport and arrow help or hurt by regime.

### 10.3 Candidate 1: Logistic Calibration

Model:

```text
logit(y_yes) ~ logit(v28_p_yes) + selected low-count feature interactions
```

Use regularization.

Candidate features:

- `logit(v28_p_yes)`
- `abs_d_sigma`
- `seconds_to_close`
- `realized_vol_15m`
- `recross_hazard_raw`
- `book_v28_gap` only in Track B

### 10.4 Candidate 2: Monotonic Tabular Correction

Model:

```text
p_successor = v28_p_yes + correction_bucket
```

Buckets:

- probability bucket,
- distance-to-strike bucket,
- time-to-close bucket,
- volatility regime,
- recross hazard bucket,
- source quality tier.

Use shrinkage toward zero correction for low-count buckets.

Boundary-gated variant:

```text
correction_weight = 1.0 when abs(d_sigma) <= 1.0
correction_weight = linear taper when 1.0 < abs(d_sigma) < 2.0
correction_weight = 0.0 when abs(d_sigma) >= 2.0

p_successor =
    v28_p_yes
  + correction_weight * (tabular_calibrated_probability - v28_p_yes)
```

This variant is useful when the plain monotonic table improves boundary calibration but damages all-row Brier/logloss. It must be frozen as its own candidate before any forward rows count for it; older rows scored with the plain table do not count as evidence for the boundary-gated version.

Conservative scaled variant:

```text
p_successor =
    v28_p_yes
  + correction_scale * correction_weight * (tabular_calibrated_probability - v28_p_yes)
```

Use a fixed, predeclared `correction_scale` such as `0.33` when the boundary correction looks directionally useful but full-strength correction is too aggressive. This must be a separate frozen manifest and must earn its own forward evidence from rows captured after the manifest exists.

Time-safe boundary variant:

```text
distance_weight = 1.0 inside abs(d_sigma) <= 1.0, tapering to 0.0 by abs(d_sigma) >= 2.0
time_weight = 0.0 inside the final no-correction window
time_weight = linear taper between the no-correction window and the full-correction window

p_successor =
    v28_p_yes
  + correction_scale * distance_weight * time_weight * (tabular_calibrated_probability - v28_p_yes)
```

Use this only as a predeclared frozen challenger when diagnostics show that a boundary correction helps non-late boundary rows but hurts very-late rows where v28 is already sharp. The time gate must use only `seconds_to_close` known at decision time, must not be tuned after forward labels arrive, and must be scored as a separate candidate. A suggested first frozen version is `v28s_boundary_monotonic_time_safe_v001`: `correction_scale=0.10`, no correction at or below 240 seconds to close, linearly fading in to full candidate strength by 600 seconds to close.

If that candidate begins to wash out on frozen forward evidence, a separately frozen micro-strength variant may be added rather than retroactively changing the old manifest. The first such variant is `v28s_boundary_monotonic_micro_time_safe_v001`: same causal distance/time gate, `correction_scale=0.03`, and zero credit for rows captured before its manifest exists.

Late `d_sigma` residual variant:

```text
late_time_weight = 1.0 at or below 240 seconds to close
late_time_weight = linear taper down to 0.0 by 600 seconds to close
late_time_weight = 0.0 at or beyond 600 seconds to close

logit(p_successor) =
    logit(v28_p_yes)
  + late_time_weight * coefficient * d_sigma
```

This variant addresses a specific final-average-settlement failure mode: very late instantaneous signed distance can be too sharp if settlement depends on a final average rather than a single last print. The first frozen version is `v28s_late_dsigma_residual_tilt_v001`: `coefficient=-0.20`, full correction inside 240 seconds, no correction at or beyond 600 seconds, and `max_abs_logit_adjustment=0.75`. It is a hand-coded physics hypothesis, not a promotion claim; rows captured before the manifest exists must not count for it.

### 10.5 Candidate 3: Small Gradient-Boosted Residual Model

Model:

```text
residual = y_yes - v28_p_yes
successor = clamp(v28_p_yes + residual_model(features))
```

Constraints:

- small depth,
- limited features,
- chronological validation,
- SHAP or feature importance report,
- monotonic constraints where appropriate if tooling supports it,
- no opaque large model.

### 10.6 Candidate 4: Book-Aware Logit Pool

Model:

```text
logit(p_successor) =
    w1 * logit(v28_p_yes)
  + w2 * logit(book_yes_probability)
  + corrections
```

This candidate should be judged as a calibrated market probability, not pure FV.

### 10.7 Candidate 5: Reliability-Weighted Ensemble

Only after individual components prove value:

```text
p_successor =
    reliability * model_probability
  + (1 - reliability) * conservative_anchor
```

The reliability score must be interpretable.

## 11. Splitting And Validation

Use chronological splits.

Suggested split ladder:

```text
discovery_train
discovery_validation
chronological_holdout
post_freeze_forward
independent_source_check
```

Rules:

- Do not random split markets.
- Do not allow rows from the same market to leak across train and holdout in ways that let later market state teach earlier prediction.
- If multiple rows per market exist, use market-level grouping for summary metrics.
- Keep first-opportunity, heartbeat, and approved-entry views separate.
- Always report row count and market count.

## 12. Metrics

### 12.1 Probability Metrics

Primary:

```text
Brier score
log loss
ECE
calibration slope
calibration intercept
mean predicted probability
realized win rate
```

By bucket:

```text
probability bucket
YES/NO side
seconds_to_close bucket
abs_d_sigma bucket
recross hazard bucket
volatility regime
book disagreement bucket
source quality tier
ask cost bucket
```

### 12.2 Boundary Metrics

```text
near-boundary Brier
near-boundary logloss
high-recross Brier
ordinary-impulse-crossing bucket calibration
time-to-first-recross calibration
terminal-margin calibration
```

### 12.3 Source Metrics

```text
approved-only performance
rejected-actionable performance
heartbeat performance
reconstructed share
simulated share
sidecar share
pre-resolution registered share
source-quality weighted score
```

### 12.4 Economics Metrics

Only after probability passes:

```text
fee-aware EV
net P&L
gross P&L
drawdown
loss streak
loss clusters
coverage
retained markets
ask cost distribution
exit value versus hold
hold-to-settlement P&L
```

## 13. Promotion Gates

A model candidate is not promotable unless all required gates pass.

### 13.1 Calibration Gate

Pass if:

- holdout Brier better than v28,
- holdout logloss better than v28,
- ECE better than v28 or not materially worse,
- no major bucket degradation,
- enough rows for meaningful interpretation.

Fail if:

- only P&L improves,
- only all-market Brier improves while near-boundary degrades,
- improvement comes from low-count buckets,
- improvement comes from post-resolution or reconstructed rows.

### 13.2 Boundary Gate

Pass if:

- near-boundary calibration improves,
- high-recross calibration improves or does not degrade,
- model reduces known v28 overconfidence pockets,
- model does not become overconfident on cheap tail or thin edge rows.

### 13.3 Source-Quality Gate

Pass if:

- low reconstructed share,
- low simulated share,
- enough approved or clean pre-resolution rows,
- explicit source mix report,
- candidate survives when low-quality rows are removed or downweighted.

### 13.4 Forward Gate

Pass if:

- candidate was frozen before rows resolved,
- forward registry exists,
- enough settled forward rows,
- candidate beats v28 on same rows,
- market coverage remains broad enough,
- promotion report lists exact per-candidate row/market shortfalls, estimated additional markets needed, and probability deltas whenever a candidate is blocked,
- no live bot changes were involved.

### 13.5 Economics Gate

Pass if:

- fee-aware shadow EV improves,
- realized shadow P&L improves or risk improves,
- drawdown does not worsen materially,
- loss clusters do not worsen,
- coverage remains within declared target.

## 14. Leakage Audit

Every dataset and model report must include a leakage audit.

Checklist:

```text
No settlement labels in features.
No future BTC candles in features.
No future book states in features.
No final-average samples not known at decision time.
No post-resolution reconstructed candidate rows in promotion score.
No market outcome merged before feature creation.
No same-market future row leaking into earlier prediction.
No feature generated from final P&L, final exit, or final settlement.
No model chosen by scanning many historical rows without forward freeze.
```

If any item fails, the candidate becomes diagnostic-only.

## 15. Red-Team Checklist

Every promising candidate must answer:

```text
Did it win because of real probability calibration, or because it copied the book?
Did it win only on reconstructed or simulated rows?
Did it improve P&L while making probability calibration worse?
Did it improve overall Brier while failing near the boundary?
Did it collapse coverage below the recurring-market target?
Did it depend on rows unavailable at decision time?
Did it survive after the exact candidate was frozen?
Did it require a threshold discovered after seeing holdout losses?
Did it work on YES but fail on NO?
Did it work only during one volatility regime?
Did it work only because of partial-exit accounting artifacts?
Did it remain useful when old diagnostic rows are removed?
```

## 16. Report Templates

### 16.1 Dataset Audit Report

Suggested file:

```text
logs/edge_research/v28_successor_dataset_audit_latest.md
```

Must include:

```text
source files used
row counts
market counts
date range
source type mix
source quality tiers
missing columns
causality exclusions
label coverage
settlement source coverage
known leakage risks
```

### 16.2 Feature Audit Report

Suggested file:

```text
logs/edge_research/v28_successor_feature_audit_latest.md
```

Must include:

```text
feature list
feature family
feature timestamp basis
missingness
allowed model tracks
leakage status
importance warning if feature is book-derived
```

### 16.3 Calibration Report

Suggested file:

```text
logs/edge_research/v28_successor_calibration_latest.md
```

Must include:

```text
candidate id
baseline v28 metrics
candidate metrics
delta metrics
probability buckets
boundary buckets
source buckets
YES/NO split
time-to-close split
verdict
```

### 16.4 Candidate Comparison Report

Suggested file:

```text
logs/edge_research/v28_successor_candidate_comparison_latest.md
```

Must include:

```text
candidate leaderboard
model track
train window
holdout window
forward rows
Brier delta
logloss delta
ECE delta
near-boundary delta
coverage
source-quality blockers
promotion verdict
```

### 16.5 Forward Registry Report

Suggested file:

```text
logs/edge_research/v28_successor_forward_registry_latest.md
```

Must include:

```text
frozen candidate id
freeze timestamp
registered rows
resolved rows
pending rows
coverage
v28 comparison
post-lock Brier/logloss
post-lock economics
source mix
candidate-specific sample floors
sample-only quality-passing candidate id
sample-only row/market shortfalls
```

## 17. Frozen Candidate Manifest

Every candidate must have a machine-readable manifest.

Suggested file pattern:

```text
logs/edge_research/v28_successor_candidate_<candidate_id>.json
```

Required fields:

```json
{
  "candidate_id": "v28s_logistic_calibration_v001",
  "model_track": "pure_physics",
  "created_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "freeze_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "training_rows": 0,
  "validation_rows": 0,
  "holdout_rows": 0,
  "feature_manifest_hash": "...",
  "dataset_hash": "...",
  "excluded_columns": [],
  "feature_columns": [],
  "model_type": "regularized_logistic",
  "hyperparameters": {},
  "baseline": "v28_raw",
  "allowed_for_forward_registry": false,
  "notes": ""
}
```

## 18. Implementation Phases

### Phase 0: Orientation And Inventory

Goal:

Understand the actual local evidence before building anything.

Actions:

- Inventory v28/FV probes.
- Inventory existing latest reports.
- Identify canonical live logs.
- Identify shadow/frozen registries.
- Identify settlement and market metadata sources.
- Identify current blockers from source-quality and readiness reports.

Output:

```text
logs/edge_research/v28_successor_inventory_latest.md
```

### Phase 1: Causal Dataset Builder

Goal:

Create the row ledger.

Actions:

- Parse source files.
- Normalize timestamps.
- Join market metadata.
- Join BTC state available at decision time.
- Join book state available at decision time.
- Join v28 logged or replayed components.
- Attach settlement labels after features are frozen.
- Mark source quality.
- Mark eligibility.

Output:

```text
research_particle/v28_successor/causal_rows.parquet
logs/edge_research/v28_successor_dataset_audit_latest.md
```

### Phase 2: v28 Baseline Reproduction

Goal:

Make sure v28 baseline values are trustworthy.

Actions:

- Compare logged v28 values to replayed v28 values.
- Flag divergence by source and time.
- Keep logged values where replay would introduce drift.
- Build a canonical baseline table.

Output:

```text
logs/edge_research/v28_successor_v28_replay_audit_latest.md
```

### Phase 3: Feature Build And Leakage Audit

Goal:

Create model-ready features and prove they are causal.

Actions:

- Build Track A pure physics features.
- Build Track B book-aware features.
- Build Track C reliability/recross features.
- Create feature manifests.
- Run leakage checks.

Output:

```text
research_particle/v28_successor/features.parquet
logs/edge_research/v28_successor_feature_audit_latest.md
```

### Phase 4: Baseline Scoring

Goal:

Establish the scoreboard before training.

Actions:

- Score v28 raw.
- Score Brownian terminal.
- Score book probability alone.
- Score simple blends only as baselines.
- Report by bucket.

Output:

```text
logs/edge_research/v28_successor_baseline_scorecard_latest.md
```

### Phase 5: Simple Candidate Training

Goal:

Train inspectable challengers only.

Actions:

- Train regularized logistic calibrator.
- Train monotonic/tabular correction.
- Train a boundary-gated monotonic/tabular correction if the plain table helps near-boundary rows but hurts all-row probability quality.
- Train a time-safe boundary monotonic/tabular correction if the boundary correction helps away from the final minutes but degrades very-late log loss.
- Freeze a fixed late-window `d_sigma` logit residual only as a predeclared physics hypothesis if diagnostics show v28 is too sensitive to instantaneous boundary distance near final-average settlement.
- Train small residual model if justified.
- Train book-aware logit pool separately.
- Reject models that fail calibration.

Output:

```text
logs/edge_research/v28_successor_candidate_comparison_latest.md
```

### Phase 6: Boundary And Reliability Scoring

Goal:

Prove the model is better where v28 is fragile.

Actions:

- Score near-boundary rows.
- Score high recross rows.
- Score high volatility rows.
- Score stale-feed rows.
- Score book-disagreement rows.
- Score YES and NO separately.

Output:

```text
logs/edge_research/v28_successor_boundary_reliability_latest.md
```

### Phase 7: Frozen Forward Registry

Goal:

Collect real post-lock evidence.

Actions:

- Freeze a candidate manifest.
- Register predictions before settlement.
- Append outcomes only after resolution.
- Compare to v28 on identical rows.
- Do not change live bot.

Output:

```text
logs/edge_research/v28_successor_forward_registry_latest.md
```

### Phase 8: Promotion Readiness Audit

Goal:

Make one clear verdict.

Actions:

- Read candidate comparison.
- Read source-quality audit.
- Read forward registry.
- Read economics report.
- Apply promotion gates.

Output:

```text
logs/edge_research/v28_successor_promotion_readiness_latest.md
```

## 19. Candidate Naming

Use explicit names:

```text
v28s_raw_control
v28s_brownian_settlement_control
v28s_logistic_physics_v001
v28s_tabular_boundary_shrink_v001
v28s_boundary_monotonic_blend_v001
v28s_boundary_monotonic_light_v001
v28s_boundary_monotonic_time_safe_v001
v28s_bookaware_logit_pool_v001
v28s_recross_reliability_v001
v28s_residual_gbm_small_v001
```

Avoid names that encode results, like:

```text
best_profit_model
winner
holdout_champion
```

Names should describe mechanism, not outcome.

## 20. What Not To Optimize For First

Do not optimize first for:

- maximum P&L,
- maximum trade count,
- a single high-confidence threshold,
- an ask-cost filter,
- a loss-avoidance filter,
- a tiny branch,
- one side only,
- one day only,
- one volatility regime only.

These can be diagnostics later. They are not the foundation of a successor FV engine.

## 21. The Correct Mental Model

The successor is not:

```text
v28 plus a better entry threshold
```

It is:

```text
v28 plus a calibrated understanding of when the probability surface is wrong,
why it is wrong, and how uncertain it should be near the boundary.
```

The desired model is allowed to say:

```text
v28 says 87%, but in this boundary/vol/book state, the calibrated probability is 82%.
```

It is also allowed to say:

```text
v28 and the book agree, source quality is clean, recross hazard is low, so confidence remains high.
```

That is the actual upgrade.

## 22. Data Contracts And Versioning

The successor project should treat datasets, features, and candidates as versioned artifacts. A probability result is not meaningful unless the exact input rows, feature logic, and model manifest can be reconstructed later.

### 22.1 Dataset Version Contract

Every canonical dataset export should include:

```text
dataset_id
dataset_version
created_utc
builder_script
builder_git_or_file_hash
source_manifest_hash
row_count
market_count
min_decision_ts_utc
max_decision_ts_utc
label_coverage_pct
source_quality_summary
```

If the workspace is not a Git checkout, use file hashes for scripts and source manifests. Do not silently rely on "latest" as a reproducibility reference.

### 22.2 Stable Row ID

Every row must have a deterministic row ID. The row ID should not depend on row order.

Recommended shape:

```text
row_id = hash(
  market_ticker,
  decision_ts_utc,
  side_or_axis,
  source_type,
  source_file,
  source_line_or_event_id
)
```

For market-level rows, use `axis=yes_probability`. For side-specific rows, use `side=yes` or `side=no`. Keep these separate so YES-axis probability calibration does not get mixed with side-selection scoring.

### 22.3 Source Manifest

Every build should write a source manifest:

```text
source_path
source_kind
file_size_bytes
last_write_time_utc
content_hash_if_feasible
rows_read
rows_accepted
rows_rejected
rejection_reasons
```

This protects against accidental drift when a log file grows or a latest report is regenerated.

### 22.4 Feature Manifest

Every feature table should write a feature manifest:

```text
feature_name
feature_family
model_track_allowed
timestamp_basis
source_columns
missing_value_policy
leakage_risk
normalization_or_transform
```

The `timestamp_basis` field is mandatory. It should say exactly why the feature was known at `decision_ts_utc`.

### 22.5 Candidate Version Contract

Every trained or hand-coded candidate must reference:

```text
dataset_id
feature_manifest_hash
train_window
validation_window
holdout_window
model_track
model_type
hyperparameters
calibration_report_path
forward_registry_path
```

If any referenced artifact is missing, the candidate is not promotable.

## 23. Clock, Market Lifecycle, And Label Rules

Most subtle FV errors come from time alignment. The project should make clock logic explicit.

### 23.1 Timestamp Normalization

All internal timestamps should be UTC ISO-8601 strings plus numeric epoch seconds where convenient.

Required normalized fields:

```text
decision_ts_utc
market_open_ts_utc
market_close_ts_utc
book_ts_utc
btc_tick_ts_utc
settlement_ts_utc
source_event_ts_utc
```

Do not mix local time and UTC in joins. Reports can display local time only as secondary context.

### 23.2 Market Lifecycle State

Each row should carry a lifecycle state:

```text
pre_open
open
inside_final_average_window
closed_pending_settlement
settled
unknown
```

Rows outside the valid prediction window should be excluded or explicitly marked diagnostic-only.

### 23.3 One Market, Many Rows

The same market may have many heartbeat rows and multiple side-specific opportunity rows. Reports must distinguish:

```text
row_count
unique_market_count
unique_market_side_count
first_opportunity_count
approved_entry_count
heartbeat_count
```

A candidate can look strong by producing many correlated rows from the same market. Market-level aggregation must always be shown next to row-level metrics.

### 23.4 Duplicate Handling

The builder must detect duplicates by:

```text
row_id
market_ticker + decision_ts_utc + side_or_axis
source event id
```

Duplicate rows should be classified:

```text
exact_duplicate
same_event_different_source
same_market_same_second_conflict
recomputed_conflict
```

Conflicts are not automatically wrong, but they must be reported. For promotion scoring, prefer the earliest clean pre-resolution row.

### 23.5 Settlement Label Validation

Settlement labels should be validated independently when possible.

Checks:

```text
settlement side matches settlement price versus strike
settlement timestamp is after market close
no label exists before market close unless it is a known partial final-average sample
market ticker strike agrees with parsed strike metadata
missing settlement rows are not treated as losses or wins
```

Rows with ambiguous settlement labels are allowed for unlabeled diagnostics but not for supervised scoring.

## 24. Test And QA Requirements

No model work should start until the dataset builder passes basic tests. A clever model on a bad ledger is worse than no model.

### 24.1 Unit Tests

Add focused tests for:

```text
market ticker parsing
strike extraction
timestamp normalization
book ask reconstruction from opposite bid
YES-axis versus side-axis conversion
v28 component extraction
settlement label attachment
final-average known-sample logic
row_id determinism
duplicate detection
source-quality classification
```

### 24.2 Golden Fixture Tests

Create a small fixture with a few known markets and expected outputs.

The fixture should include:

```text
one YES winner
one NO winner
one near-boundary market
one stale BTC row
one stale book row
one duplicate row
one missing settlement row
one final-average-window row
```

The fixture should be small enough to inspect by hand.

### 24.3 Invariant Checks

Every dataset build should assert:

```text
0 <= probabilities <= 1
fair_yes_cents + fair_no_cents approximately equals 100
seconds_to_close >= 0 for prediction rows
book_age_ms >= 0 when present
btc_tick_age_ms >= 0 when present
YES win label is binary when present
settlement margin sign agrees with YES win label
no feature column contains final P&L or settlement fields
```

### 24.4 Backtest Reproduction Checks

Before using a new dataset for training, reproduce at least one known v28 report at a coarse level:

```text
row count roughly matches source report
market count roughly matches source report
v28 average probability roughly matches source report
v28 Brier/logloss roughly matches source report
source mix roughly matches source report
```

Exact equality may not be possible when rebuilding from logs, but large differences must be explained.

### 24.5 Report Smoke Tests

Every report script should be able to run with:

```text
--limit-rows 100
--dry-run
--write-report
```

This keeps iteration fast and catches path/schema errors before long runs.

## 25. Reproducible Command Flow

The first implementation should have a boring, repeatable command sequence.

Suggested flow:

```powershell
python .\build_v28_successor_causal_dataset.py --discover-sources --write
python .\replay_v28_successor_baselines.py --write
python .\build_v28_successor_features.py --write
python .\score_v28_successor_baselines.py --write
python .\train_v28_successor_fv_candidates.py --track pure_physics --write
python .\score_v28_successor_candidates.py --write
```

Every command should:

- read from explicit input paths or a manifest,
- write deterministic output paths,
- print a short summary,
- write a markdown report,
- write a JSON machine-readable report,
- avoid touching live bot state.

If a command cannot find enough source data, it should write a blocker report instead of failing silently.

## 26. First Implementation Milestone

The first milestone should be intentionally modest. Do not start by training a model.

### 26.1 Milestone Goal

Produce a clean causal dataset and a v28 baseline scorecard for at least one source family.

Preferred first source family:

```text
logs/live_mushroom_v28_size2/bot.log
logs/live_mushroom_v28_size2/execution_events.ndjson
logs/edge_research/v28_forward_calibration_latest.*
logs/edge_research/v28_forward_shadow_registry_schema_latest.md
```

If those are unavailable or stale, use the cleanest available v28 forward/calibration ledger discovered in `logs/edge_research`.

### 26.2 Milestone Acceptance

Milestone 1 passes only if there is a report showing:

```text
source files discovered
rows parsed
rows rejected with reasons
unique markets
settlement label coverage
v28 probability columns present
YES-axis probability coverage
side-axis probability coverage
source-quality mix
leakage audit pass/fail
baseline Brier/logloss by bucket
```

No candidate training is allowed to count as progress until this exists.

### 26.3 First Candidate Milestone

Only after Milestone 1 passes, train one simple candidate:

```text
v28s_logistic_physics_v001
```

Feature limit:

```text
logit(v28_p_yes)
abs(v28_d_sigma)
seconds_to_close
v28_sigma_t_dollars
v28_arrow
v28_transport_recent_n
v28_transport_long_n
```

This first model is a calibration smoke test. It is not expected to be the final successor.

## 27. Human Review Checklist

Before believing any "better than v28" claim, the reviewer should see:

```text
Which rows were used?
Were they known before settlement?
How many unique markets?
How many approved versus rejected/actionable versus reconstructed rows?
What is the YES-axis Brier/logloss delta?
What is the near-boundary Brier/logloss delta?
What happens if book-derived features are removed?
What happens if reconstructed/simulated rows are removed?
What are the worst buckets?
What are the latest post-lock rows?
Is the result calibration improvement, P&L improvement, or both?
```

If the answer is not visible in the report, the candidate is not ready.

## 28. Risk Register

The project should track these risks explicitly.

| risk | why it matters | mitigation |
|---|---|---|
| Hidden future leakage | Makes any model look smarter than it is | timestamp basis for every feature plus leakage audit |
| Book-copying disguised as FV | Improves Brier but may not add independent edge | separate pure physics and book-aware tracks |
| Source-quality ceiling | Reconstructed rows can inflate coverage and P&L | source mix gates and clean-row stress tests |
| Market-row duplication | Many rows from one market can fake sample size | market-level metrics next to row-level metrics |
| Side-axis confusion | `p_side` hides YES/NO direction | train and score on YES-axis first |
| Partial-exit accounting artifacts | Summary files can overstate live economics | replay raw execution events for P&L |
| Overfit thresholds | Historical scans find brittle rows | freeze manifests before forward scoring |
| Calibration/P&L conflict | A profitable rule may worsen probability truth | probability gates come before economics gates |
| Stale feed artifacts | Bad BTC/book timestamps create false edges | freshness features and source-quality exclusions |
| Operational bleed-through | Research accidentally touches live bot | research-only scripts and no state/process mutation |

## 29. Final Acceptance Standard

The project is done only when there is a frozen candidate with:

- a clean causal dataset,
- a leakage audit,
- a source-quality audit,
- a v28 baseline comparison,
- better probability metrics,
- better or equal boundary metrics,
- clear reliability outputs,
- post-lock forward evidence,
- fee-aware shadow economics,
- broad enough coverage,
- and a written promotion/readiness verdict.

Until then, the correct status is:

```text
research-only, not promotable
```
