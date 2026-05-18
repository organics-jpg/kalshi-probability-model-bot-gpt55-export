# RV600 Locked Candidates

Updated: 2026-05-13

This note freezes the Phase 2 RV600 candidates selected from
`RV600_VARIATION_TEST_PLAN.md`. It is research-only: no live trades, no live v28
logic changes, and no bot restart.

## Source Reports

- First candidate report:
  `logs/particle_research/reports/rv600_variation_test_latest.md`
- Phase 1 grid report:
  `logs/particle_research/reports/rv600_variation_grid_latest.md`
- Locked-candidate report:
  `logs/particle_research/reports/rv600_variation_locked_latest.md`
- Native prequential selection report:
  `logs/particle_research/reports/rv600_prequential_selection_latest.md`
- Strict native prequential locked-only report:
  `logs/particle_research/reports/rv600_prequential_selection_locked_only_latest.md`

## Frozen Candidate Set

These five candidates are locked for forward shadow scoring. Do not retune them
on the same ten-root retrospective set.

| Candidate | Window | Min EV | Entry rule |
|---|---:|---:|---|
| `rv600_primary_max_3_entries_mid_120_420_ev12` | `T-420s` to `T-120s` | `12c` | max 3 entries per market |
| `rv600_primary_max_3_entries_base_70_420_ev12` | `T-420s` to `T-70s` | `12c` | max 3 entries per market |
| `rv600_primary_risk_cap_200c_mid_120_420_ev12` | `T-420s` to `T-120s` | `12c` | max 3 entries, total ask risk <= `200c` |
| `rv600_primary_risk_cap_200c_base_70_420_ev12` | `T-420s` to `T-70s` | `12c` | max 3 entries, total ask risk <= `200c` |
| `rv600_primary_max_2_entries_mid_120_420_ev12` | `T-420s` to `T-120s` | `12c` | max 2 entries per market |

## Current Retrospective Evidence

Best locked row:

- variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- accounting: `position_capped`
- accepted entries: `70`
- distinct markets: `26`
- selected PnL after fees/fills: `+1317.0c`
- matched v28/current control PnL on the same accepted timestamps: `+1029.0c`
- matched-v28 delta: `+288.0c`
- average PnL per entry: `18.81c`
- average PnL per market: `50.65c`
- positive roots: `8/10`
- positive market/block rate: `0.62`
- max single-market PnL share: `0.20`
- last-window PnL: `+113.0c`
- average added-entry PnL: `16.55c`

The original first-candidate set did not clear the locked gates. The exhaustive
grid did find the five locked candidates above after enforcing:

- all candidate rows are retained as denominator
- repeated entries are scored as `all_entries`, `one_per_side_per_market`, and
  `position_capped`
- candidates cannot be promoted from `all_entries` alone
- matched v28/current control is scored on the same accepted timestamps
- max single-market PnL share must be <= `25%`
- root and market/block positivity must be >= `60%`

## Forward Shadow Command

Use this command to refresh the retrospective locked report:

```powershell
python -m research_particle.rv600_variation_test --phase locked --output-json logs\particle_research\reports\rv600_variation_locked_latest.json --output-md logs\particle_research\reports\rv600_variation_locked_latest.md --write
```

Use this command to score only post-lock incoming-market shadow evidence:

```powershell
python probe_rv600_forward_shadow_refresh.py --write
python probe_rv600_sidecar_shadow_root.py --write
python -m research_particle.rv600_variation_test --phase locked --output-json logs\particle_research\reports\rv600_variation_forward_latest.json --output-md logs\particle_research\reports\rv600_variation_forward_latest.md --min-decision-ts-utc 2026-05-13T05:37:07+00:00 --write
```

If the live v28 execution-event tailer is stale, use the research-only sidecar
collector for new incoming markets instead of restarting the live bot:

```powershell
python -m research_particle.paired_sidecar_spot_capture --collect-mode public-rest --spot-feed coinbase --spot-run-seconds 15 --spot-warmup-seconds 1 --spot-max-age-ms 2000 --timeout-seconds 20 --max-markets 1
```

After the captured market resolves, refresh sidecar labels/diagnostics and
rebuild the de-duplicated RV600 sidecar shadow root:

```powershell
python -m research_particle.paired_sidecar_spot_refresh --fetch-labels --write
python probe_rv600_sidecar_shadow_root.py --write
```

The sidecar converter writes at most one RV600 candidate snapshot per market and
decision timestamp. This avoids counting the sidecar packet's many model rows as
repeated RV600 opportunities.

For native/continuous forward roots where the passive orderbook recorder has
fresh checkpoints but the live v28 event tailer is stale, build a matched
research-only v28 control context by causally replaying the v28 fair-value engine
from public BTC candles and independent spot ticks:

```powershell
python probe_rv600_native_offline_v28_contexts.py
python -m research_particle.shadow_pipeline --source-type passive_checkpoint --checkpoints "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\research_data\rv600_forward_native_shadow\book_checkpoints\**\*.ndjson" --contexts "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\particle_research\real_shadow\rv600_forward_native_shadow_offline_v28_20260513T115640Z\offline_v28_contexts.ndjson" --market-results "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\particle_research\real_shadow\rv600_forward_native_shadow\market_results_full_refresh.json" --root "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\particle_research\real_shadow\rv600_forward_native_shadow_offline_v28_20260513T115640Z" --annualized-vol 0.65 --sample-count 2000 --seed 1 --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5 --decision-shadow rv600_forward_native_offline_v28_shadow --reason rv600_native_offline_v28_replay
python probe_rv600_forward_shadow_refresh.py --name-prefix rv600_forward_native_shadow --write
```

If a bounded native run crosses into the next still-active market, add
`--market-ticker <resolved-ticker>` to `probe_rv600_native_offline_v28_contexts.py`
and point `shadow_pipeline --checkpoints` at that market's checkpoint directory.
Do not score active markets with proxy labels.

Use this command to audit whether the full RV600 goal is complete:

```powershell
python probe_rv600_goal_completion_audit.py
```

Use this command to diagnose whether the native forward roots contain a real
RV600 opportunity or only a small-sample/proxy-v28 positive:

```powershell
python probe_rv600_native_forward_opportunity.py --write
```

## Native Control Modeling Choice

Blocker: the 2026-05-13 native passive recorder captured fresh orderbook and
spot data, but the live v28 event tailer only exposed stale seeded markets. The
live bot was not restarted.

Options checked:

- Wait for fresh live v28 events. This has the best live fidelity, but it was
  blocked by stale telemetry and the research guardrail against restarts.
- Causal event replay of the v28 engine from public BTC candles plus native
  independent spot ticks. This matches the event-driven backtest principle of
  acting only on market data as it arrives, avoids future spot leakage, and keeps
  the matched-control construction research-only.
- Walk-forward or time-series split validation. This remains the validation
  pattern for larger samples, but it does not by itself create missing per-second
  control contexts.
- More retrospective parameter search with covariance penalties or other
  backtest-overfit corrections. Useful for selection discipline, but not a good
  response to a missing live-context feed.
- Synthetic/bootstrap replay. Rejected for the completion gate because it would
  not be incoming-market shadow evidence.

Chosen implementation: `probe_rv600_native_offline_v28_contexts.py` causally
warms `FastMushroomFVEngineV28` with Coinbase one-minute candles ending before
the first checkpoint minute, then feeds only independent spot ticks whose local
receive time is at or before each native checkpoint. This creates matched v28
context rows without touching live bot logic, orders, secrets, or processes.

References used for this choice:

- [QuantStart event-driven backtesting](https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-I/)
- [scikit-learn TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [Carr and Lopez de Prado, Determining Optimal Trading Rules without Backtesting](https://arxiv.org/abs/1408.1159)
- [Koshiyama and Firoozye, Avoiding Backtesting Overfitting by Covariance-Penalties](https://arxiv.org/abs/1905.05023)
- [Bornschein, Li, and Hutter, Sequential Learning of Neural Networks for Prequential MDL](https://arxiv.org/abs/2210.07931)

Current forward-only status:

- report: `logs/particle_research/reports/rv600_variation_forward_latest.md`
- native post-lock root: `rv600_forward_shadow_20260513T054445Z`
- native post-lock labels: `1` settled market, `0` label-refresh issues
- sidecar post-lock roots:
  - `20260513T110825Z-39c87098`: `KXBTC15M-26MAY130715-15` at
    `2026-05-13T11:08:26.141000+00:00`
  - `20260513T113822Z-627cce28`: `KXBTC15M-26MAY130745-45` at
    `2026-05-13T11:38:23.836000+00:00`
  - `20260513T114239Z-af11cb54`: `KXBTC15M-26MAY130745-45` at
    `2026-05-13T11:42:40.806000+00:00`
  - `20260513T115332Z-b4bb216a`: `KXBTC15M-26MAY130800-00` at
    `2026-05-13T11:53:33.668000+00:00`
- all sidecar decisions are inside the frozen `T-420s` to `T-120s` window
- sidecar label status: `missing_label_rows_skipped=0` and
  `fetched_label_rows=4` at `2026-05-13T12:02:21+00:00`; score only rows with
  finalized public Kalshi `result`
- settled sidecar markets: `KXBTC15M-26MAY130715-15` resolved `no`,
  `KXBTC15M-26MAY130745-45` resolved `yes`, and
  `KXBTC15M-26MAY130800-00` resolved `no`
- current forward sidecar score: `2` accepted entries, `2` distinct markets,
  selected PnL `-6.3c`, matched v28/current control `+0.8c`
- native offline-control roots:
  - `rv600_forward_native_shadow_offline_v28_20260513T115640Z`
  - `rv600_forward_native_shadow_offline_v28_20260513T1220Z`
  - `rv600_forward_native_shadow_offline_v28_20260513T1235Z`
  - `rv600_forward_native_shadow_offline_v28_20260513T1259Z`
  - `rv600_forward_native_shadow_offline_v28_20260513T1333Z`
  - `rv600_forward_native_shadow_offline_v28_20260513T1333Z_1400`
  - `rv600_forward_native_shadow_offline_v28_20260513T1407Z`
  - `rv600_forward_native_shadow_offline_v28_20260513T1407Z_1430`
  - `rv600_forward_native_shadow_offline_v28_20260513T1439Z`
  - `rv600_forward_native_shadow_offline_v28_20260513T1439Z_1500`
  - `rv600_forward_native_shadow_offline_v28_20260513T1522Z_1530`
  - `rv600_forward_native_shadow_offline_v28_20260513T1541Z_1545`
  - `rv600_forward_native_shadow_offline_v28_20260513T1556Z_1600`
  - `rv600_forward_native_shadow_offline_v28_20260513T1610Z_1615`
  - `rv600_forward_native_shadow_offline_v28_20260513T1626Z_1630`
  - `rv600_forward_native_shadow_offline_v28_20260513T1640Z_1645`
- latest native refresh status:
  `logs/particle_research/reports/rv600_forward_shadow_refresh_latest.md`
  refreshed `16` native roots, `17` markets, `17` resolved labels, `0` label
  issues at `2026-05-13T16:51:41+00:00`
- the 12:20Z native run captured `507` checkpoints and `5350` independent spot
  ticks; offline replay wrote `505` context rows, and the mixed-market pipeline
  recorded `458` candidate snapshots once both crossed markets had labels
- the 12:36Z native run captured the locked window for
  `KXBTC15M-26MAY130845-45`; filtered offline replay wrote `380` context rows,
  and the resolved-only pipeline recorded `322` candidate snapshots with raw
  particle replay PnL `-437c`
- the 12:59Z native run captured the next full early-to-close window for
  `KXBTC15M-26MAY130915-15`; official Kalshi result was `yes`; offline v28
  replay wrote `780` pre-close context rows from `782` checkpoints, and the
  pre-close-only pipeline recorded `780` candidate snapshots with raw particle
  replay PnL `-12765c`. A first unfiltered pass was correctly rejected by the
  strict leakage guard because the source file included a post-settlement
  checkpoint at `2026-05-13T13:15:07Z`.
- the 13:33Z native run captured the early-to-close window for
  `KXBTC15M-26MAY130945-45`; official Kalshi result was `no`; offline v28
  replay wrote `641` pre-close context rows from `644` checkpoints, and the
  pre-close-only pipeline recorded `613` candidate snapshots with raw particle
  replay PnL `+697c`. This improved the broad early-window diagnostic but did
  not create any locked RV600 entries.
- the same 13:33Z capture also provided an early-only sample for
  `KXBTC15M-26MAY131000-00` through `2026-05-13T13:51:13Z`; official Kalshi
  result was `no`; offline v28 replay wrote `340` context rows and the
  pre-close-only pipeline recorded `340` candidate snapshots with raw particle
  replay PnL `-4221c`.
- the 14:07Z native run captured the 14:15Z contract's early and locked windows;
  official Kalshi result for `KXBTC15M-26MAY131015-15` was `yes`; offline v28
  replay wrote `449` pre-close context rows from `451` checkpoints, and the
  pre-close-only pipeline recorded `419` candidate snapshots with raw particle
  replay PnL `-9021c`. This was the first native forward batch to produce
  locked-window RV600 entries, but those locked entries were negative.
- the same 14:07Z capture also provided a partial early/locked sample for
  `KXBTC15M-26MAY131030-30` through `2026-05-13T14:25:15Z`; official Kalshi
  result was `yes`; offline v28 replay wrote `582` context rows and the
  pre-close-only pipeline recorded `582` candidate snapshots with raw particle
  replay PnL `-12951c`.
- the 14:39Z native run captured the 14:45Z contract's late locked window;
  official Kalshi result for `KXBTC15M-26MAY131045-45` was `no`; offline v28
  replay wrote `326` pre-close context rows from `328` checkpoints, and the
  pre-close-only pipeline recorded `305` candidate snapshots with raw particle
  replay PnL `-2154c`.
- the same 14:39Z capture also provided a partial early/locked sample for
  `KXBTC15M-26MAY131100-00` through `2026-05-13T14:57:14Z`; official Kalshi
  result was `yes`; offline v28 replay wrote `679` context rows and the
  pre-close-only pipeline recorded `679` candidate snapshots with raw particle
  replay PnL `+14311c`. This was a positive raw particle replay, but the locked
  RV600 rules still lost money after aggregate variation scoring.
- the 15:22Z native run captured the locked window for
  `KXBTC15M-26MAY131130-30`; official Kalshi result was available during the
  refresh; offline v28 replay wrote `403` pre-close context rows from `406`
  checkpoints, correctly rejecting `3` post-settlement checkpoints, and the
  pipeline recorded `343` candidate snapshots. The best locked candidate added
  one more forward entry on this market at `2026-05-13T15:24:04.448171+00:00`
  and lost `10c`.
- the 15:41Z native run captured the late locked window for
  `KXBTC15M-26MAY131145-45`; official Kalshi result was available during the
  refresh; offline v28 replay wrote `170` pre-close context rows from `172`
  checkpoints, correctly rejecting `2` post-settlement checkpoints, and the
  pipeline recorded `165` candidate snapshots. This market improved the locked
  aggregate, but not enough: it added profitable NO entries while the full
  native locked set remained negative and gate-failing.
- the 15:56Z native run captured the late locked window for
  `KXBTC15M-26MAY131200-00`; official Kalshi result was available during the
  refresh; offline v28 replay wrote `147` pre-close context rows from `149`
  checkpoints, correctly rejecting `2` post-settlement checkpoints, and the
  pipeline recorded `28` candidate snapshots. This market added native
  provenance but no locked RV600 entries.
- the 16:10Z native run captured the locked window for
  `KXBTC15M-26MAY131215-15`; official Kalshi result was available during the
  refresh; offline v28 replay wrote `239` pre-close context rows from `241`
  checkpoints, correctly rejecting `2` post-settlement checkpoints, and the
  pipeline recorded `208` candidate snapshots. This market added locked entries
  but worsened the native locked aggregate.
- the 16:26Z native run captured the locked window for
  `KXBTC15M-26MAY131230-30`; official Kalshi result was available during the
  refresh; offline v28 replay wrote `198` pre-close context rows from `200`
  checkpoints, correctly rejecting `2` post-settlement checkpoints, and the
  pipeline recorded `113` candidate snapshots. This market added one more
  forward locked sample but did not change the negative conclusion.
- the 16:40Z native run captured the locked window for
  `KXBTC15M-26MAY131245-45`; official Kalshi result was available during the
  refresh; offline v28 replay wrote `252` pre-close context rows from `254`
  checkpoints, correctly rejecting `2` post-settlement checkpoints, and the
  pipeline recorded `171` candidate snapshots. This market added another
  forward locked sample while the aggregate stayed negative.
- native-only existing-grid diagnostic:
  `logs/particle_research/reports/rv600_native_forward_opportunity_latest.md`
  found `7584` candidate rows across `24` settled native markets; the five
  locked candidates now have `170` native entries with `-2223c` PnL
- the best existing-grid native-forward row was
  `blend_80_20_max_3_entries_broad_70_600_ev20` with `+209c` PnL and `0c`
  matched-v28 delta. It is diagnostic only because it still failed sample size,
  root positivity, market positivity, single-market concentration,
  recent-window, and matched-v28 gates.
- the best RV600-primary native-forward row was
  `rv600_primary_max_3_entries_late_70_180_ev20` with `+174c` diagnostic PnL
  but not enough sample, root positivity, market positivity, concentration,
  recent-window, or matched-v28 edge to promote.
- locked RV600 rules now accept native entries, but the fresh locked-window
  evidence is negative: the forward locked report has `15` accepted entries,
  `15` markets, selected PnL `-155.3c`, and matched-v28 control `-148.2c`.
- latest native root added:
  `logs/particle_research/real_shadow/rv600_forward_native_shadow_offline_v28_20260513T1819Z_1830`
  for `KXBTC15M-26MAY131430-30`. It built `554` causal offline-v28 contexts,
  rejected `2` post-settlement checkpoints, and produced `478` labeled
  candidate rows. It increased native coverage but still did not produce a
  promotable locked RV600 result.
- previous native root added:
  `logs/particle_research/real_shadow/rv600_forward_native_shadow_offline_v28_20260513T1808Z_1815`
  for `KXBTC15M-26MAY131415-15`. It built `376` causal offline-v28 contexts,
  rejected `2` post-settlement checkpoints, and produced `339` labeled
  candidate rows. It increased native coverage and kept the locked forward PnL
  negative.
- previous native root added:
  `logs/particle_research/real_shadow/rv600_forward_native_shadow_offline_v28_20260513T1752Z_1800`
  for `KXBTC15M-26MAY131400-00`. It built `388` causal offline-v28 contexts,
  rejected `2` post-settlement checkpoints, and produced `324` labeled
  candidate rows. It increased native coverage and did not improve the locked
  completion verdict.
- previous native root added:
  `logs/particle_research/real_shadow/rv600_forward_native_shadow_offline_v28_20260513T1737Z_1745`
  for `KXBTC15M-26MAY131345-45`. It built `441` causal offline-v28
  contexts, rejected `2` post-settlement checkpoints, and produced `380`
  labeled candidate rows. It increased native coverage and made the locked
  forward PnL worse.
- previous native root added:
  `logs/particle_research/real_shadow/rv600_forward_native_shadow_offline_v28_20260513T1722Z_1730`
  for `KXBTC15M-26MAY131330-30`. It built `434` causal offline-v28
  contexts, rejected `1` post-settlement checkpoint, and produced `329`
  labeled candidate rows. It increased native coverage but did not add any
  locked RV600 entries.
- previous native root added:
  `logs/particle_research/real_shadow/rv600_forward_native_shadow_offline_v28_20260513T1712Z_1715`
  for `KXBTC15M-26MAY131315-15`. It built `101` causal offline-v28
  contexts, rejected `2` post-settlement checkpoints, and produced `16`
  labeled candidate rows. It did not improve the locked RV600 completion
  verdict.
- previous native root added:
  `logs/particle_research/real_shadow/rv600_forward_native_shadow_offline_v28_20260513T1656Z_1700`
  for `KXBTC15M-26MAY131300-00`. It built `202` causal offline-v28
  contexts, rejected `2` post-settlement checkpoints, and produced `163`
  labeled candidate rows. It did not improve the locked RV600 completion
  verdict.
- source-quality status: the audit now sees `7584` native/continuous candidate
  rows from `23` native roots plus `4` sidecar rows from `3` sidecar markets.
  This improves provenance and passes the native row-count part of the gate, but
  still fails the completion gate requiring at least `40` native markets.
- native continuous attempt: `rv600_forward_native_shadow` originally produced
  zero valid candidate contexts because the v28 context tailer only had stale
  seeded events. The offline replay root fixes the missing-context mechanism,
  but the fresh native markets did not generate locked RV600 entries.
- label-fetch choice: use exchange-published `result` only, trying live list,
  live single-market, then historical single-market endpoints. Do not infer BTC
  15m labels from off-exchange spot while `result` is empty.
- accepted entries: `15`
- distinct markets: `15`
- calendar days: `1`
- weekend days: `0`
- conclusion: the locked RV600 candidate remains research-only. Retrospective
  gates pass, but fresh forward evidence is small and negative; native
  locked-window entries have lost money after fees/fills and still fail the
  sample, positivity, and matched-control gates.

## Prequential Selection Modeling Choice

Blocker: the native-forward grid still contains a small positive existing-grid
row (`blend_80_20_max_3_entries_broad_70_600_ev20`, `+328c`), but that row was
found after looking across the same forward roots and still fails sample-size,
root-positivity, concentration, and matched-v28 gates. Treating it as a
candidate would be a selection-bias mistake.

Options checked:

- Deflated Sharpe / multiple-testing adjustment. Useful for larger return
  series, but the current native sample is too small for a stable Sharpe-style
  correction.
- CSCV / probability of backtest overfitting. Strong for estimating overfit risk
  from a return matrix, but it would reuse the scarce native roots
  combinatorially instead of mimicking the live sequence.
- Purged or embargoed time-series CV. Useful when labels overlap; the new probe
  exposes `--gap-roots` as a simple embargo, but the default next-root split is
  appropriate because these rows are already settled 15-minute market blocks.
- Anchored walk-forward / prequential selection. Chosen because it matches the
  actual research decision: choose from prior native roots only, then test the
  frozen choice on the next incoming root.
- Synthetic/bootstrap replay. Rejected for this goal gate because it is not
  incoming-market shadow evidence.

Chosen implementation: `probe_rv600_prequential_selection.py` scores every
native root once with the existing RV600 grid, then runs anchored splits with
`min_train_roots=3`. A split may promote only if prior roots already select a
locked-gate candidate. Diagnostic fallbacks are reported for visibility but are
not promotable.

References used for this choice:

- [scikit-learn TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [Dawid, The Prequential Approach](https://academic.oup.com/jrsssa/article/147/2/278/7106293)
- [Bailey and Lopez de Prado, The Deflated Sharpe Ratio](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551)
- [Bailey, Borwein, Lopez de Prado, and Zhu, The Probability of Backtest Overfitting](https://doi.org/10.21314/JCF.2016.322)
- [Carr and Lopez de Prado, Determining Optimal Trading Rules without Backtesting](https://arxiv.org/abs/1408.1159)

Latest prequential results:

- default anchored report:
  `logs/particle_research/reports/rv600_prequential_selection_latest.md`
- roots: `23`
- split count: `20`
- locked-gate selection count: `0`
- diagnostic fallback selection count: `20`
- out-of-sample fallback entries: `36`
- out-of-sample fallback PnL: `-394c`
- matched v28/control PnL on the same timestamps: `-394c`
- matched-v28 delta: `0c`
- positive split rate: `0.150`
- conclusion: no locked-gate train window existed, and the diagnostic fallback
  lost money out of sample.

Strict locked-only result:

- report:
  `logs/particle_research/reports/rv600_prequential_selection_locked_only_latest.md`
- split count: `0`
- skipped split count: `20`
- conclusion: no prior-root training window produced a locked-gate candidate.

Gap sensitivity:

- report: `logs/particle_research/reports/rv600_prequential_selection_gap1_latest.md`
- gap roots: `1`
- split count: `19`
- locked-gate selection count: `0`
- diagnostic fallback selection count: `19`
- fallback PnL: `-2c`
- matched v28/control PnL: `-2c`
- matched-v28 delta: `0c`
- rejection: diagnostic fallback, fewer than `25` entries, positive splits below
  `60%`, single-root concentration, and no `20%` edge over matched v28.

Interpretation: the apparent broad-grid positives are not RV600-specific
validated edge yet. When selection is limited to prior roots, the only available
choices are non-promotable diagnostic fallbacks, and their PnL either loses or
matches v28 exactly depending on embargo setting.

## Forward Futility Modeling Choice

Blocker: continuing to collect the same locked RV600 family is now a modeling
choice. The family is still far below the forward-shadow sample minimum, but the
available native evidence is already negative enough that blindly adding the
same family risks wasting future shadow windows.

Options checked:

- Bayesian predictive-probability futility. Chosen because this is an interim
  stop/continue decision with a pre-specified final success gate.
- Sequential probability ratio testing. Useful for binary win/loss processes,
  but less aligned with fee-adjusted PnL, matched-control delta, and market
  count gates.
- Deflated Sharpe ratio. Useful for multiple tested return series, but the
  current blocker is one frozen locked family, not a fresh parameter sweep.
- CSCV / probability of backtest overfitting. Useful for judging retrospective
  grid-selection risk; the existing prequential report is the closer
  live-order analog.
- White reality-check style data-snooping control. Useful before selecting a
  new grid winner, not needed for rejecting this frozen forward family.

Chosen implementation: `probe_rv600_forward_futility.py` reads the latest
forward locked report, native-forward opportunity report, prequential report,
and completion audit. It emits recovery math plus a bootstrap predictive
probability for reaching the Phase 3 minimum gates without changing live logic.

Latest futility result:

- report: `logs/particle_research/reports/rv600_forward_futility_latest.md`
- decision: `reject_current_locked_family_for_promotion`
- reasons:
  `forward_locked_selected_pnl_nonpositive`,
  `forward_locked_avg_entry_negative`,
  `does_not_beat_matched_v28_on_forward_timestamps`,
  `native_locked_entries_ge_100_and_negative`,
  `prequential_locked_gate_selection_count_zero`,
  `bootstrap_predictive_success_probability_below_threshold`
- bootstrap predictive success probability: `0.0000`
- current locked forward sample: `15` entries, `15` markets, `-155.3c`
  selected PnL, `-7.1c` matched-v28 delta
- native locked aggregate: `170` entries, `-2223c` PnL
- prequential locked-gate selections: `0`
- required remaining average PnL to reach the `100` entry and `10c` average
  target: `13.592c` per entry over the next `85` accepted entries

Interpretation: the current locked RV600 family should stop consuming
forward-shadow collection by itself. RV600 research can continue only by
freezing a new candidate from existing evidence and applying the same
anti-overfitting gates, not by promoting the rejected family.

## Expanded Existing-Candidate Refresh

After rejecting the current locked family, the next existing-candidate-first
check was to rerun the full RV600 grid on the expanded forward evidence.

- report: `logs/particle_research/reports/rv600_variation_forward_grid_latest.md`
- phase: `grid`
- root count: `25`
- variant count: `3948`
- best total-PnL row:
  `blend_80_20_max_3_entries_broad_70_600_ev20/all_entries`
- best total PnL: `+209c`
- locked candidates found: `none`
- promotion allowed: `False`
- reason: even the best grid rows remain sparse (`15` entries, `5` markets),
  concentrated, positive in only `2/25` roots, last-window nonpositive, and at
  `0c` matched-v28 delta.

Interpretation: no existing plan-defined RV600 candidate is currently eligible
to replace the rejected locked family. The grid positives remain diagnostic
only and should not be promoted or live-tested.

## Plan-Family Rejection Ledger

To make the existing-candidate rejection mechanical, the expanded forward grid
was grouped by every RV600 variation family in the plan.

- report: `logs/particle_research/reports/rv600_plan_family_rejection_latest.md`
- decision: `no_existing_plan_family_viable`
- grid phase: `grid`
- root count: `25`
- variant count: `3948`
- summary rows: `11844`
- promotion allowed: `False`

Family-level outcomes:

- timing windows: all rejected; best `broad_70_600`, `+209c`, `15` entries,
  `5` markets
- EV thresholds: all rejected; best `ev20`, `+209c`, `15` entries, `5` markets
- repeated-entry rules: all rejected; best `max_3_entries`, `+209c`, `15`
  entries, `5` markets
- side filters: all rejected; best `side_by_v28_disagreement`, `+6.7c`, `4`
  entries, `4` markets
- v28 transfer controls: all rejected; best `blend_80_20`, `+209c`, `15`
  entries, `5` markets
- volatility/regime filters: all rejected; best `strike_far`, `+10c`, `4`
  entries, `4` markets
- microstructure filters: all rejected; best `depth_ratio_3`, `-170c`, `15`
  entries, `15` markets
- price/payoff filters: all rejected; best `rich_tail`, `+15c`, `1` entry,
  `1` market

Interpretation: the blocker is not missing family coverage. Every defined
family either loses, is too sparse, is concentrated, lacks root/market
stability, has a nonpositive recent window, or has no matched-v28 edge.

## Objective State Audit

A stricter prompt-to-artifact audit now maps the active RV600 objective to the
current artifacts.

- report: `logs/particle_research/reports/rv600_objective_state_latest.md`
- decision: `blocked_not_complete`
- objective complete: `False`
- blocked by:
  `current_locked_family_rejected`,
  `no_existing_plan_family_viable`,
  `forward_shadow_pnl_negative`,
  `forward_shadow_sample_incomplete`,
  `meta_label_rescue_failed`,
  `probability_calibration_rescue_failed`,
  `conformal_abstention_rescue_failed`,
  `online_expert_rescue_failed`,
  `no_current_plan_revision_supported`
- prompt-to-artifact status:
  - plan exists and remains source of truth
  - research note exists and records decisions
  - `3948` plan-defined variants were built/scored
  - repeated-entry accounting has `all_entries`,
    `one_per_side_per_market`, and `position_capped`
  - matched-v28/current control is scored
  - completion audit is not green
  - forward evidence has only `15` accepted entries and `15` markets
  - forward evidence spans only `1` calendar day and `0` weekend sessions
  - forward selected PnL is `-155.3c`
  - current locked family is rejected by futility
  - no plan-defined family remains viable on the expanded forward grid
  - literature-backed meta-label rescue failed prequential gates
  - literature-backed probability-calibration rescue failed prequential gates
  - literature-backed conformal-abstention rescue failed prequential gates
  - literature-backed online-expert rescue failed prequential gates
  - failure-pattern audit supports no new plan revision from this sample

Conclusion: do not call the RV600 goal complete. Do not live-test or promote any
current RV600 family. The next RV600 attempt would need a documented plan update
or a newly frozen candidate, then a fresh locked and forward-shadow validation
cycle.

References used for this choice:

- [FDA Bayesian clinical-trial guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/guidance-use-bayesian-statistics-medical-device-clinical-trials)
- [Wald sequential testing reference](https://www.jstor.org/stable/i312742)
- [Bailey and Lopez de Prado, Deflated Sharpe Ratio](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551)
- [Bailey, Borwein, Lopez de Prado, and Zhu, Probability of Backtest Overfitting](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253)
- [White, A Reality Check for Data Snooping](https://econpapers.repec.org/RePEc%3Aecm%3Aemetrp%3Av%3A68%3Ay%3A2000%3Ai%3A5%3Ap%3A1097-1126)

## Meta-Label Rescue Probe

Because the current locked family and every plan-defined replacement family
were rejected, the next blocker was whether a small, documented modeling change
could rescue RV600 without inventing a new broad strategy family.

Plausible solutions searched:

- meta-labeling / trade-acceptance filter:
  [Joubert 2022](https://ssrn.com/abstract=4032018)
- conformal time-series abstention:
  [Xu and Xie 2020/2023](https://arxiv.org/abs/2010.09107)
- sequential conformal inference:
  [Xu and Xie 2022](https://arxiv.org/abs/2212.03463)
- post-hoc probability calibration:
  [Guo et al. 2017](https://arxiv.org/abs/1706.04599)
- online expert weighting:
  [Freund and Schapire 1997](https://doi.org/10.1006/jcss.1997.1504)

Chosen fit: meta-labeling. It keeps RV600 as the primary directional/EV signal
and learns only a small acceptance/suppression layer, which is the narrowest
intervention compatible with the existing-candidates-first constraint. The
implementation uses anchored prequential selection: filters are selected on
prior roots only and tested on the next root. Diagnostic best-train filters are
reported, but a candidate is not promotable unless the prior-root window already
passes the anti-overfitting gates.

- report: `logs/particle_research/reports/rv600_meta_label_rescue_latest.md`
- usable roots: `23`
- filter count: `35`
- split count: `18`
- train-gate selections: `0`
- diagnostic selections: `18`
- test entries: `18`
- test selected PnL: `-127c`
- matched-v28 delta: `+174c`
- preliminary gate pass: `False`
- rejection reasons:
  `no_train_gate_selection`,
  `fewer_than_25_test_entries`,
  `nonpositive_test_pnl`,
  `avg_test_entry_below_10c`,
  `positive_test_splits_below_60pct`

Interpretation: the rescue failed. RV600 beat an even worse matched-v28
diagnostic path on these selected timestamps, but it still lost money, had no
prior-root train-gate pass, and remained far below sample/stability gates. This
does not produce a newly frozen candidate.

## Probability-Calibration Rescue Probe

After meta-labeling failed, the next narrow rescue was probability calibration:
do not invent a new entry family; only recalibrate the RV600 probability and
reuse simple plan-shaped timing, EV, and repeated-entry rules under anchored
prequential selection.

Plausible solutions searched:

- Platt/logit scaling:
  [Platt 1999](https://www.researchgate.net/publication/2594015_Probabilistic_Outputs_for_Support_Vector_Machines_and_Comparisons_to_Regularized_Likelihood_Methods)
- temperature scaling:
  [Guo et al. 2017](https://arxiv.org/abs/1706.04599)
- isotonic calibration:
  [Niculescu-Mizil and Caruana 2005](https://icml.cc/Conferences/2005/proceedings/papers/079_GoodProbabilities_NiculescuMizilCaruana.pdf)
- Venn-Abers calibration:
  [Vovk and Petej 2012](https://arxiv.org/abs/1211.0025)

Chosen fit: low-complexity calibration. The probe tested fixed temperature
scales, shrinkage toward market/current probabilities, and a grid Platt fit
trained on one earliest candidate per prior-root market. Isotonic and
Venn-Abers were deferred because the current forward market count is too small
for flexible calibration without turning the branch into curve fitting.

- report:
  `logs/particle_research/reports/rv600_probability_calibration_rescue_latest.md`
- usable roots: `23`
- plan-shaped strategy rules: `8`
- split count: `18`
- train-gate selections: `0`
- diagnostic selections: `18`
- test entries: `18`
- test selected PnL: `-228c`
- matched-v28 delta: `0c`
- preliminary gate pass: `False`
- rejection reasons:
  `no_train_gate_selection`,
  `fewer_than_25_test_entries`,
  `nonpositive_test_pnl`,
  `avg_test_entry_below_10c`,
  `does_not_beat_matched_v28`,
  `positive_test_splits_below_60pct`

Interpretation: the calibration rescue failed and is worse than the
meta-labeling rescue on next-root PnL. It produces no frozen candidate and no
reason to continue collecting the rejected RV600 family.

## Conformal-Abstention Rescue Probe

The last narrow rescue tested whether RV600 could be useful only when its
prior-root error band still left positive worst-case EV. This is stricter than
calibration: it abstains unless a conservative probability interval clears fees
and the plan-shaped EV threshold.

Plausible solutions considered:

- split/conformal time-series intervals:
  [Xu and Xie 2020/2023](https://arxiv.org/abs/2010.09107)
- sequential conformal inference:
  [Xu and Xie 2022](https://arxiv.org/abs/2212.03463)
- meta-labeling as the simpler acceptance-filter comparator:
  [Joubert 2022](https://ssrn.com/abstract=4032018)

Chosen fit: split-style conformal abstention using prior-root absolute RV600
label residual quantiles. Sequential conformal inference was deferred because
the current sample has too few settled markets to justify an adaptive residual
model.

- report:
  `logs/particle_research/reports/rv600_conformal_abstention_rescue_latest.md`
- usable roots: `23`
- plan-shaped strategy rules: `8`
- split count: `18`
- train-gate selections: `0`
- diagnostic selections: `18`
- test entries: `0`
- test selected PnL: `0c`
- matched-v28 delta: `0c`
- preliminary gate pass: `False`
- rejection reasons:
  `no_train_gate_selection`,
  `fewer_than_25_test_entries`,
  `nonpositive_test_pnl`,
  `does_not_beat_matched_v28`,
  `positive_test_splits_below_60pct`

Interpretation: conservative RV600 uncertainty bands suppress every next-root
entry. The branch avoids losses only by not trading, so it cannot satisfy the
goal's profitable-strategy requirement.

## Online-Expert Rescue Probe

The final deferred literature branch tested whether the existing RV600 plan
variants could be selected online as experts rather than frozen as one static
variant. This keeps the candidate universe exactly inside the already-built
plan grid, uses only prior-root rewards for selection, and excludes pure
`v28_primary` controls because they are not RV600-derived strategies.

Plausible solutions considered:

- multiplicative weights:
  [Freund and Schapire 1997](https://doi.org/10.1006/jcss.1997.1504)
- prediction with expert advice:
  [Cesa-Bianchi and Lugosi 2006](https://doi.org/10.1017/CBO9780511546921)
- second-order expert bounds:
  [Cesa-Bianchi, Mansour, and Stoltz 2006](https://arxiv.org/abs/math/0602629)

Chosen fit: multiplicative-weights selection over existing plan variants. Each
expert is a plan-defined RV600 variant scored with `position_capped` accounting.
Prior-root rewards are bounded before weighting so a single large root cannot
dominate unchecked. A selection is not promotable unless the selected expert
already passed prior-root anti-overfitting gates.

- report:
  `logs/particle_research/reports/rv600_online_expert_rescue_latest.md`
- usable roots: `23`
- variant count: `3948`
- expert count: `3948`
- split count: `18`
- train-gate selections: `0`
- diagnostic selections: `18`
- test entries: `26`
- test selected PnL: `-416c`
- matched-v28 delta: `0c`
- preliminary gate pass: `False`
- rejection reasons:
  `no_train_gate_selection`,
  `nonpositive_test_pnl`,
  `avg_test_entry_below_10c`,
  `does_not_beat_matched_v28`,
  `positive_test_splits_below_60pct`

Interpretation: online weighting over the existing RV600 plan variants did not
rescue the family. It mostly chose broad blended repeated-entry variants that
looked good in prior roots but lost on the next roots, with no matched-v28
edge. This is another rejection, not a candidate.

## Failure-Pattern Audit

After exhausting the plan families and narrow rescue branches, a mechanical
failure-pattern audit checked whether the current artifacts support any new
plan revision at all.

- report:
  `logs/particle_research/reports/rv600_failure_pattern_audit_latest.md`
- decision: `no_current_plan_revision_supported`
- plan revision supported: `False`
- grid variants: `3948`
- grid summary rows: `11844`
- position-capped rows: `3948`
- simple position-capped rows: `630`
- positive position-capped rows: `483`
- positive matched-v28-delta rows: `819`
- support rows satisfying the revision-support gate: `0`
- rescue gate-pass rows: `0`

Dominant position-capped rejection reasons:

- `positive_roots_below_60pct`: `3948`
- `positive_markets_below_60pct`: `3945`
- `last_window_nonpositive`: `3888`
- `avg_entry_below_10c`: `3800`
- `nonpositive_pnl`: `3465`
- `fewer_than_25_entries`: `2172`
- `single_market_share_above_25pct`: `483`
- `does_not_beat_matched_v28_by_20pct`: `477`

Interpretation: this sample does not justify another RV600 plan revision. The
apparently positive rows are too sparse, too concentrated, too unstable by
root/market, or lack enough matched-v28 edge. The next valid progress requires
materially new shadow evidence or a genuinely new RV600 clue, not another
promotion attempt from the current sample.

## Next-Evidence Gate

Because the current sample is exhausted, the next valid RV600 progress is not
another parameter search. It is materially new, bounded, research-only shadow
evidence.

- report: `logs/particle_research/reports/rv600_next_evidence_gate_latest.md`
- decision: `ready_collect_new_shadow_evidence`
- ready for bounded shadow collection: `True`
- current sample exhaustion confirmed:
  `failure_decision=no_current_plan_revision_supported; support_row_count=0`
- matched v28 event source:
  `logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\execution_events.ndjson`
- passive collector:
  `research_particle\paired_passive_shadow_run.py`
- native passive recorder:
  `research_native_passive_ws_recorder.py`

The generated command is bounded, read-only, and tags the run as
`rv600_research_shadow_readonly`. It does not restart the live bot, does not
change live v28 order logic, and does not place trades. A future collection
still needs the full completion sample before the goal can close: `100`
accepted entries, `40` distinct markets, `10` calendar days, two weekend
sessions, positive fee/fill-adjusted PnL, and at least `20%` matched-v28 edge.

## Bounded Shadow Smoke Run

A short bounded smoke collection was run to verify the new-evidence path without
touching live orders, live v28 logic, or the live bot process.

- root:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_smoke_20260513T193315Z`
- paired passive manifest:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_smoke_20260513T193315Z\paired_passive_run_manifest.json`
- smoke audit:
  `logs/particle_research/reports/rv600_shadow_smoke_audit_latest.md`
- decision: `smoke_scored_no_rv600_entries`
- collection ok: `True`
- offline v28 context ok: `True`
- pipeline ok: `True`
- labels ok: `True`
- candidate rows: `115`
- settled markets: `1`
- labels written: `1`
- locked RV600 entries: `0`
- locked RV600 PnL: `0c`

Important detail: the live v28 event file was stale for fresh context tailing,
so the independent-spot merge against seeded live contexts produced stale-context
issues. The smoke used the safer research-only fallback already present in the
repo: causal offline v28 fair-value replay from public Coinbase candles plus the
independent spot ticks captured during the smoke. That produced `115` offline
v28 contexts with `0` issues.

Interpretation: the new-evidence pipeline works, but the smoke is not strategy
validation. It covered one settled market and produced zero accepted RV600
entries. The goal remains blocked until a future frozen candidate accumulates
the required multi-day forward-shadow sample with positive PnL and matched-v28
edge.

## Bounded 900-Second Shadow Run

A longer bounded read-only collection was then run against incoming markets.
This also avoided live orders, live v28 logic changes, and live bot restarts.

- root:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T195001Z`
- paired passive manifest:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T195001Z\paired_passive_run_manifest.json`
- refresh report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T195001Z_refresh.md`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T195001Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_audit_latest.md`
- objective audit:
  `logs/particle_research/reports/rv600_objective_state_latest.md`
- collection: `832` checkpoint rows, `5302` independent spot ticks
- offline v28 contexts: `830` written, `2` post-settlement checkpoint rows
  dropped
- pipeline: `776` candidate rows, `0` context issues
- labels: `2` settled markets, `0` label issues
- locked RV600 entries: `14`
- locked RV600 PnL: `-237c`
- best existing-grid row:
  `rv600_primary_max_3_entries_broad_70_600_ev2`
- best existing-grid entries: `5`
- best existing-grid PnL: `+110c`
- best existing-grid matched-v28 delta: `+397c`
- best existing-grid rejection:
  `fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct`

Interpretation: this fresh-shadow slice is useful because it finally produced
accepted RV600-style entries in the new-evidence path, but it is still not a
promotion candidate. The locked family was negative, and the only positive
grid row is too small and too concentrated to clear the anti-overfitting gates.
The active objective remains `blocked_not_complete`.

## Second Bounded 900-Second Shadow Run

A second bounded read-only collection was run immediately after the first to add
fresh incoming markets without restarting or changing the live bot.

- root:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T202034Z`
- paired passive manifest:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T202034Z\paired_passive_run_manifest.json`
- refresh report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T202034Z_refresh.md`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T202034Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260513T202034Z_audit.md`
- collection: `842` checkpoint rows, `3916` independent spot ticks
- offline v28 contexts: `840` written, `2` post-settlement checkpoint rows
  dropped
- pipeline: `810` candidate rows, `0` context issues
- labels: `2` settled markets, `0` label issues
- locked RV600 entries: `14`
- locked RV600 PnL: `+875c`
- best existing-grid row:
  `blend_95_5_max_3_entries_broad_70_600_ev10`
- best existing-grid entries: `3`
- best existing-grid PnL: `+246c`
- best existing-grid matched-v28 delta: `0c`
- best existing-grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: this second slice has positive locked and grid PnL, but the
best rows remain diagnostic only. They are concentrated in one market, have too
few entries, and do not beat the matched v28 control by the required margin.

## Cumulative Bounded Shadow Evidence

The two bounded 900-second roots were scored together to avoid judging either
slice in isolation.

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_20260513T195001Z_202034Z_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `2`
- candidate rows: `1586`
- settled markets: `4`
- locked RV600 entries: `28`
- locked RV600 PnL: `+638c`
- best existing-grid row:
  `rv600_primary_max_3_entries_broad_70_600_ev2`
- best existing-grid entries: `11`
- best existing-grid PnL: `+258c`
- best existing-grid matched-v28 delta: `+397c`
- best existing-grid rejection:
  `fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct`

Interpretation: cumulative fresh-shadow PnL is now positive, but the cumulative
evidence still fails the spec's anti-overfitting gates. It has only `4` markets,
fewer than `25` accepted entries for the best row, below-`60%` positive-market
stability, and a single-market concentration failure. This is progress, not
completion.

## Third Bounded 900-Second Shadow Run

A third bounded read-only collection was run to test whether the positive
cumulative result survived another pair of incoming markets.

- root:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T205117Z`
- paired passive manifest:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T205117Z\paired_passive_run_manifest.json`
- refresh report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T205117Z_refresh.md`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T205117Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260513T205117Z_audit.md`
- collection: `828` checkpoint rows, `3490` independent spot ticks
- offline v28 contexts: `826` written, `2` post-settlement checkpoint rows
  dropped
- pipeline: `817` candidate rows, `0` context issues
- labels: `2` settled markets, `0` label issues
- locked RV600 entries: `14`
- locked RV600 PnL: `-126c`
- best existing-grid row:
  `rv600_primary_single_market_late_70_180_ev20`
- best existing-grid entries: `0`
- best existing-grid PnL: `0c`
- best existing-grid rejection:
  `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive`

Interpretation: the third slice is negative for the locked RV600 family and
adds no positive existing-grid opportunity. It weakens the case that the prior
positive bounded evidence was stable.

## Updated Cumulative Bounded Shadow Evidence

The three bounded 900-second roots were then scored together.

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_20260513T195001Z_205117Z_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `3`
- candidate rows: `2403`
- settled markets: `6`
- locked RV600 entries: `42`
- locked RV600 PnL: `+512c`
- best existing-grid row:
  `rv600_primary_max_3_entries_broad_70_600_ev15`
- best existing-grid entries: `6`
- best existing-grid PnL: `+188c`
- best existing-grid matched-v28 delta: `0c`
- best existing-grid rejection:
  `fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct`

Interpretation: cumulative fresh-shadow PnL remains positive, but the evidence
is worse after the third slice. The best row now also fails root stability,
recent-window, and matched-v28 edge gates. RV600 is still research-only and
`blocked_not_complete`.

## Fourth Bounded 900-Second Shadow Run

A fourth bounded read-only collection was run to keep extending the incoming
market sample.

- root:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T211949Z`
- paired passive manifest:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T211949Z\paired_passive_run_manifest.json`
- refresh report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T211949Z_refresh.md`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T211949Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260513T211949Z_audit.md`
- collection: `839` checkpoint rows, `2706` independent spot ticks
- offline v28 contexts: `837` written, `2` post-settlement checkpoint rows
  dropped
- pipeline: `823` candidate rows, `0` context issues
- labels: `2` settled markets, `0` label issues
- locked RV600 entries: `5`
- locked RV600 PnL: `-65c`
- best existing-grid row:
  `rv600_primary_max_3_entries_late_70_180_ev0`
- best existing-grid PnL: `+178c`
- best existing-grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: the fourth slice again fails as a standalone candidate. It has
negative locked-family PnL and the positive grid row is too sparse,
too concentrated, and does not beat matched v28.

## Four-Root Cumulative Bounded Shadow Evidence

The four bounded 900-second roots were scored together after adding automatic
completed-root discovery to the cumulative audit helper.

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_20260513T195001Z_211949Z_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `4`
- candidate rows: `3226`
- settled markets: `8`
- locked RV600 entries: `47`
- locked RV600 PnL: `+447c`
- best existing-grid row:
  `rv600_primary_max_3_entries_late_70_180_ev0`
- best existing-grid entries: `12`
- best existing-grid PnL: `+350c`
- best existing-grid matched-v28 delta: `0c`
- best existing-grid rejection:
  `fewer_than_25_entries;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: cumulative PnL remains positive, but the result still fails
sample size, root/market stability, concentration, and matched-v28 edge. The
goal remains blocked.

## Cumulative Workflow Helper

The bounded-root cumulative workflow now has an auto-discovery wrapper so future
refreshes do not require a hand-built root list.

- helper:
  `probe_rv600_cumulative_opportunity.py`
- default output:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- cumulative audit:
  `probe_rv600_bounded_cumulative_audit.py`

The helper discovers settled bounded roots that have clean refresh labels,
offline v28 context summaries, pipeline manifests, and candidate snapshots. It
excludes smoke roots and failed/incomplete launches.

## Fifth Bounded 900-Second Shadow Run

A fifth bounded read-only collection was run after the four-root cumulative
result remained gate-rejected.

- root:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T215130Z`
- paired passive manifest:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T215130Z\paired_passive_run_manifest.json`
- refresh report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T215130Z_refresh.md`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T215130Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260513T215130Z_audit.md`
- collection: `836` checkpoint rows, `5298` independent spot ticks
- offline v28 contexts: `834` written, `2` post-settlement checkpoint rows
  dropped
- pipeline: `784` candidate rows, `0` context issues
- labels: `2` settled markets, `0` label issues
- locked RV600 entries: `10`
- locked RV600 PnL: `+740c`
- best existing-grid row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best existing-grid entries: `6`
- best existing-grid PnL: `+281c`
- best existing-grid matched-v28 delta: `+122c`
- best existing-grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct`

Interpretation: the fifth slice is positive, but standalone evidence is still
too sparse and too concentrated to pass the anti-overfitting gates.

## Five-Root Cumulative Bounded Shadow Evidence

The cumulative helper then rescored all settled bounded roots.

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `5`
- candidate rows: `4010`
- settled markets: `10`
- locked RV600 entries: `57`
- locked RV600 PnL: `+1187c`
- best existing-grid row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best existing-grid entries: `27`
- best existing-grid distinct markets: `9`
- best existing-grid PnL: `+489c`
- best existing-grid matched-v28 delta: `+701c`
- best existing-grid positive-root rate: `0.8`
- best existing-grid positive-market rate: `0.5556`
- best existing-grid max single-market PnL share: `0.4990`
- best existing-grid rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct`

Interpretation: this is the strongest fresh-shadow RV600 evidence so far. It
clears the minimum-entry, root-stability, recent-window, and matched-v28-edge
checks for the best grid row, but it still fails positive-market stability and
single-market concentration. It also remains far below the broader completion
target of `40` markets over `10` days with weekend coverage. The goal remains
`blocked_not_complete`.

## Sixth Bounded 900-Second Shadow Run

A sixth bounded read-only collection was run to keep testing whether the
five-root cumulative improvement persisted.

- root:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T222021Z`
- paired passive manifest:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T222021Z\paired_passive_run_manifest.json`
- refresh report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T222021Z_refresh.md`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T222021Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260513T222021Z_audit.md`
- collection: `819` checkpoint rows, `4341` independent spot ticks
- offline v28 contexts: `817` written, `2` post-settlement checkpoint rows
  dropped
- pipeline: `727` candidate rows, `0` context issues
- labels: `2` settled markets, `0` label issues
- locked RV600 entries: `0`
- locked RV600 PnL: `0c`
- best existing-grid row:
  `blend_95_5_max_3_entries_broad_70_600_ev0`
- best existing-grid entries: `6`
- best existing-grid PnL: `+222c`
- best existing-grid matched-v28 delta: `0c`
- best existing-grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: the sixth slice is useful as fresh evidence, but not as a
standalone candidate. Locked RV600 produced no entries, and the positive grid
row was sparse, concentrated, and lacked matched-v28 edge.

## Six-Root Cumulative Bounded Shadow Evidence

The cumulative helper rescored all settled bounded roots after the sixth slice.

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `6`
- candidate rows: `4737`
- settled markets: `12`
- locked RV600 entries: `57`
- locked RV600 PnL: `+1187c`
- best existing-grid row:
  `rv600_primary_risk_cap_100c_broad_70_600_ev0`
- best existing-grid entries: `30`
- best existing-grid distinct markets: `11`
- best existing-grid PnL: `+537c`
- best existing-grid matched-v28 delta: `+472c`
- best existing-grid positive-root rate: `0.6667`
- best existing-grid positive-market rate: `0.4545`
- best existing-grid max single-market PnL share: `0.4544`
- best existing-grid rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct`

Interpretation: cumulative RV600-derived evidence remains positive and
matched-v28-positive, but the sixth slice did not fix the main blockers.
Positive-market stability worsened to `45.45%`, and concentration remains far
above the `25%` cap. The goal remains `blocked_not_complete`.

## Seventh Bounded 900-Second Shadow Run

One attempted seventh launch root,
`rv600_next_evidence_shadow_20260513T230000Z`, failed immediately because
PowerShell `Start-Process` split the workspace path with spaces. It produced no
manifest and is excluded from all cumulative discovery.

The corrected encoded PowerShell launch produced a clean bounded read-only
slice.

- root:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T230108Z`
- paired passive manifest:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T230108Z\paired_passive_run_manifest.json`
- refresh report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T230108Z_refresh.md`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T230108Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260513T230108Z_audit.md`
- collection: `834` checkpoint rows, `3594` independent spot ticks
- offline v28 contexts: `832` written, `2` post-settlement checkpoint rows
  dropped
- pipeline: `805` candidate rows, `0` context issues
- labels: `2` settled markets, `0` label issues
- locked RV600 entries: `14`
- locked RV600 PnL: `-126c`
- best existing-grid row:
  `blend_95_5_max_3_entries_broad_70_600_ev0`
- best existing-grid entries: `3`
- best existing-grid PnL: `+71c`
- best existing-grid matched-v28 delta: `0c`
- best existing-grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: the seventh slice is a clean research-only data point but it is
bad for RV600. Locked RV600 lost money, and the best grid row is too sparse,
too concentrated, and does not beat matched v28.

## Seven-Root Cumulative Bounded Shadow Evidence

The cumulative helper rescored all seven settled bounded roots after the
seventh slice.

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `7`
- candidate rows: `5542`
- settled markets: `14`
- locked RV600 entries: `71`
- locked RV600 PnL: `+1061c`
- best existing-grid row:
  `rv600_primary_risk_cap_100c_broad_70_600_ev0`
- best existing-grid entries: `33`
- best existing-grid distinct markets: `12`
- best existing-grid PnL: `+468c`
- best existing-grid matched-v28 delta: `+343c`
- best existing-grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`

Interpretation: the seventh slice weakened the cumulative case. The best grid
still has positive PnL and positive matched-v28 delta, but root stability,
market stability, single-market concentration, and the recent-window gate all
fail. The goal remains `blocked_not_complete`.

## Seven-Root Failure-Pattern Re-Audit

The failure-pattern audit was updated to rebuild its grid from the current
settled bounded roots by default, instead of the older native/sidecar forward
grid. That makes `rv600_failure_pattern_audit_latest` reflect the same
seven-root evidence used by the cumulative and market-balance reports.

- report:
  `logs/particle_research/reports/rv600_failure_pattern_audit_latest.md`
- source roots: `7`
- variants: `3948`
- summary rows: `11844`
- position-capped positive-PnL rows: `3129`
- position-capped rows with positive matched-v28 delta: `231`
- strict support rows: `0`
- rescue gate-pass rows: `0`
- top rejection reasons:
  `positive_roots_below_60pct=3936`,
  `last_window_nonpositive=3920`,
  `positive_markets_below_60pct=3906`,
  `fewer_than_25_entries=3852`,
  `single_market_share_above_25pct=3129`,
  `does_not_beat_matched_v28_by_20pct=2959`
- best soft position-capped row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best soft entries: `36`
- best soft PnL: `+450c`
- best soft matched-v28 delta: `+513c`
- best soft positive-root rate: `71.43%`
- best soft positive-market rate: `50.00%`
- best soft max single-market PnL share: `54.22%`
- best soft last-window PnL: `-69c`
- best soft rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`

Interpretation: there is still no defensible narrow plan revision to freeze.
The strongest current rows remain profitable in aggregate, but they fail market
stability, concentration, and recent-window gates. The updated audit supports
the existing blocker `no_current_plan_revision_supported`.

## Eighth Bounded 900-Second Shadow Run

An eighth bounded read-only collection was run to add materially new incoming
market evidence after all seven-root rescue paths remained rejected.

- root:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T234759Z`
- paired passive manifest:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T234759Z\paired_passive_run_manifest.json`
- refresh report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T234759Z_refresh.md`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260513T234759Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260513T234759Z_audit.md`
- collection: `855` checkpoint rows, `2997` independent spot ticks
- offline v28 contexts: `852` written, `3` unusable/post-settlement rows
  dropped
- pipeline: `836` candidate rows, `0` context issues
- labels: `2` settled markets, `0` label issues
- locked RV600 entries: `6`
- locked RV600 PnL: `-170c`
- best existing-grid row:
  `rv600_primary_max_3_entries_base_70_420_ev6`
- best existing-grid entries: `3`
- best existing-grid PnL: `+246c`
- best existing-grid matched-v28 delta: `0c`
- best existing-grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: the eighth slice is another clean research-only data point, but
it still does not support a standalone RV600 candidate. Locked RV600 lost money,
and the best grid row was sparse, concentrated, and had no matched-v28 edge.

## Eight-Root Cumulative Bounded Shadow Evidence

The cumulative helper rescored all eight settled bounded roots after the eighth
slice.

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `8`
- candidate rows: `6378`
- settled markets: `16`
- locked RV600 entries: `77`
- locked RV600 PnL: `+891c`
- best existing-grid row:
  `rv600_primary_risk_cap_100c_broad_70_600_ev0`
- best existing-grid entries: `36`
- best existing-grid distinct markets: `13`
- best existing-grid PnL: `+663c`
- best existing-grid matched-v28 delta: `+343c`
- best existing-grid rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct`

Interpretation: the eighth root improved the best cumulative grid row and
removed the recent-window blocker, but it did not clear the anti-overfitting
gates. Positive-market stability remains below `60%`, and the largest market
still contributes more than the `25%` cap. The goal remains
`blocked_not_complete`.

## Eight-Root Failure-Pattern Refresh

The failure-pattern audit was rerun after the eighth root.

- report:
  `logs/particle_research/reports/rv600_failure_pattern_audit_latest.md`
- source roots: `8`
- variants: `3948`
- summary rows: `11844`
- position-capped positive-PnL rows: `3094`
- position-capped rows with positive matched-v28 delta: `231`
- strict support rows: `0`
- rescue gate-pass rows: `0`
- best soft position-capped row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best soft entries: `39`
- best soft PnL: `+645c`
- best soft matched-v28 delta: `+513c`
- best soft positive-root rate: `75%`
- best soft positive-market rate: `54%`
- best soft max single-market PnL share: `38%`
- best soft rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct`

Interpretation: the eighth root made the leading rows look less bad, but still
not promotable. No row clears the strict revision-support gates, and every
rescue remains rejected.

## Regime-Filter Rescue Audit

After the seven-root failure-pattern audit found no existing support row, I
searched for blocker-specific modeling options and tested a bounded
regime-filter rescue. The alternatives considered were regime/change-point
filters, adaptive conformal abstention, online expert aggregation, and stronger
concentration/cardinality constraints. Because conformal, online-expert, and
market-balance/cardinality rescues were already rejected here, I chose a
causal regime-conditioned abstention audit. It keeps the search inside the
existing RV600 grid and applies only a small predeclared set of causal
pre-decision predicates: volatility expansion/non-expansion, low/high RV600
volatility, near/far strike, market uncertainty/tail, and v28 side
agreement/disagreement. A candidate can support revision only if it produces a
cumulative support row and survives anchored forward validation.

- report:
  `logs/particle_research/reports/rv600_regime_filter_rescue_latest.md`
- decision: `regime_filter_rescue_failed`
- source roots: `8`
- predicates: `11`
- summary rows: `130284`
- positive position-capped rows: `20528`
- strict support rows: `0`
- best row:
  `rv600_primary_risk_cap_100c_broad_70_600_ev0__regime_market_tailed`
- best row entries: `33`
- best row PnL: `+713c`
- best row matched-v28 delta: `+270c`
- best row positive-root rate: `62.50%`
- best row positive-market rate: `50.00%`
- best row max single-market PnL share: `34.22%`
- best row last-window PnL: `+195c`
- best row rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct`
- anchored forward test entries: `18`
- anchored forward PnL: `+233c`
- anchored forward matched-v28 delta: `-188c`
- anchored forward positive-root rate: `60%`
- anchored forward max single-market share: `83.69%`
- anchored forward gate pass: `False`

Interpretation: a simple causal regime filter did not rescue RV600. It improved
some aggregate PnL rows and recent-window evidence, but did not solve market
stability, concentration, or matched-v28 forward validation. The objective audit
includes `regime_filter_rescue_failed` as an explicit blocker.

## Market-Balance Rescue Audit

Because the cumulative result was profitable but still concentrated, I added a
research-only market-balance rescue audit that keeps the search inside the
existing RV600 grid. The modeling choice was to rank existing rows with a
concentration- and market-stability-aware utility, then verify the selected row
with anchored forward splits. This follows return-diversification, constrained
portfolio, deflated-backtest, and purged/time-ordered validation ideas without
adding a new live strategy family or touching live v28 logic.

- report:
  `logs/particle_research/reports/rv600_market_balance_rescue_latest.md`
- decision: `market_balance_rescue_failed`
- roots: `8`
- summary rows: `11844`
- full gate-pass rows: `0`
- positive rows with single-market concentration <= `25%`: `0`
- positive rows with both concentration <= `25%` and positive-market rate >=
  `60%`: `0`
- best total-PnL row:
  `rv600_primary_risk_cap_100c_broad_70_600_ev0`
- best total-PnL entries: `36`
- best total-PnL PnL: `+663c`
- best total-PnL matched-v28 delta: `+343c`
- best total-PnL rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct`
- best market-balanced row:
  `rv600_primary_risk_cap_100c_broad_70_600_ev0`
- best market-balanced entries: `36`
- best market-balanced PnL: `+663c`
- best market-balanced matched-v28 delta: `+343c`
- best market-balanced rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct`
- anchored forward test entries: `18`
- anchored forward test PnL: `+25c`
- anchored forward matched-v28 delta: `-188c`
- anchored forward gate pass: `False`

Interpretation: the profitable cumulative evidence still looks too dependent on
market concentration to trust. The eighth root improved total and recent-window
PnL, but the existing-grid market-balance rescue still did not find a row that
preserves PnL while clearing the positive-market and concentration gates.
Anchored forward PnL is only slightly positive and still has negative
matched-v28 delta, so the main objective audit keeps
`market_balance_rescue_failed` as an explicit blocker.

## Ninth Bounded 900-Second Shadow Run

A ninth bounded read-only collection was run after the eight-root cumulative
case remained profitable but gate-rejected.

- root:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T002426Z`
- paired passive manifest:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T002426Z\paired_passive_run_manifest.json`
- refresh report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T002426Z_refresh.md`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T002426Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260514T002426Z_audit.md`
- collection: `820` checkpoint rows, `4360` independent spot ticks
- offline v28 contexts: `818` written, `2` unusable/post-settlement rows
  dropped
- pipeline: `763` candidate rows, `0` context issues
- labels: `2` settled markets, `0` label issues
- locked RV600 entries: `5`
- locked RV600 PnL: `-145c`
- best existing-grid row:
  `blend_95_5_max_3_entries_broad_70_600_ev2`
- best existing-grid entries: `6`
- best existing-grid distinct markets: `2`
- best existing-grid PnL: `+164c`
- best existing-grid matched-v28 delta: `0c`
- best existing-grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best RV600-primary row:
  `rv600_primary_max_3_entries_late_70_300_ev2`
- best RV600-primary entries: `3`
- best RV600-primary PnL: `+149c`
- best RV600-primary matched-v28 delta: `0c`
- best RV600-primary rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: the ninth slice is a clean research-only data point, but it
does not rescue RV600. Locked RV600 lost money, and the best profitable rows
were too sparse, too concentrated, and did not beat the matched v28 control.

## Nine-Root Cumulative Bounded Shadow Evidence

The cumulative helper was rerun sequentially after the ninth root so the
bounded cumulative audit read the latest nine-root opportunity file, not the
previous eight-root artifact.

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `9`
- candidate rows: `7141`
- settled markets: `18`
- locked RV600 entries: `82`
- locked RV600 PnL: `+746c`
- best existing-grid row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best existing-grid entries: `45`
- best existing-grid distinct markets: `15`
- best existing-grid PnL: `+567c`
- best existing-grid matched-v28 delta: `+513c`
- best existing-grid positive-root rate: `66.67%`
- best existing-grid positive-market rate: `53.33%`
- best existing-grid max single-market PnL share: `43.03%`
- best existing-grid last-window PnL: `-78c`
- best existing-grid rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`

Interpretation: the ninth root weakened the cumulative case. Aggregate PnL and
matched-v28 delta remain positive, but market stability is below the `60%`
gate, single-market concentration is above the `25%` gate, and the recent
window turned negative again.

## Nine-Root Failure-Pattern Refresh

The failure-pattern audit was rerun after the ninth root and after the
market-balance and regime-filter rescues had refreshed.

- report:
  `logs/particle_research/reports/rv600_failure_pattern_audit_latest.md`
- source roots: `9`
- variants: `3948`
- summary rows: `11844`
- position-capped positive-PnL rows: `2967`
- position-capped rows with positive matched-v28 delta: `231`
- strict support rows: `0`
- rescue gate-pass rows: `0`
- top rejection reasons:
  `positive_roots_below_60pct=3906`,
  `positive_markets_below_60pct=3845`,
  `last_window_nonpositive=3466`,
  `fewer_than_25_entries=3449`,
  `single_market_share_above_25pct=2967`,
  `does_not_beat_matched_v28_by_20pct=2799`
- best soft position-capped row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best soft entries: `45`
- best soft distinct markets: `15`
- best soft PnL: `+567c`
- best soft matched-v28 delta: `+513c`
- best soft positive-root rate: `66.67%`
- best soft positive-market rate: `53.33%`
- best soft max single-market PnL share: `43.03%`
- best soft last-window PnL: `-78c`
- best soft rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`

Interpretation: no current plan revision is supported. The best soft row is
profitable in aggregate, but the exact anti-overfitting gates that matter for
promotion still reject it.

## Nine-Root Regime-Filter Rescue Refresh

- report:
  `logs/particle_research/reports/rv600_regime_filter_rescue_latest.md`
- decision: `regime_filter_rescue_failed`
- source roots: `9`
- predicates: `11`
- summary rows: `130284`
- positive position-capped rows: `19759`
- strict support rows: `0`
- best row:
  `rv600_primary_max_3_entries_broad_70_600_ev0__regime_market_tailed`
- best row entries: `39`
- best row distinct markets: `13`
- best row PnL: `+588c`
- best row matched-v28 delta: `+331c`
- best row positive-root rate: `55.56%`
- best row positive-market rate: `53.85%`
- best row max single-market PnL share: `41.50%`
- best row last-window PnL: `-78c`
- best row rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`
- anchored forward test entries: `24`
- anchored forward PnL: `+133c`
- anchored forward matched-v28 delta: `-197c`
- anchored forward positive-root rate: `50.00%`
- anchored forward max single-market share: `146.62%`
- anchored forward gate pass: `False`

Interpretation: the regime-filter rescue still fails. It preserves some
positive aggregate and anchored-forward PnL, but it loses to matched v28 in the
anchored validation and remains concentrated and unstable across roots and
markets.

## Nine-Root Market-Balance Rescue Refresh

- report:
  `logs/particle_research/reports/rv600_market_balance_rescue_latest.md`
- decision: `market_balance_rescue_failed`
- roots: `9`
- summary rows: `11844`
- full gate-pass rows: `0`
- positive rows with single-market concentration <= `25%`: `0`
- positive rows with both concentration <= `25%` and positive-market rate >=
  `60%`: `0`
- best total-PnL row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best total-PnL entries: `45`
- best total-PnL distinct markets: `15`
- best total-PnL PnL: `+567c`
- best total-PnL matched-v28 delta: `+513c`
- best total-PnL positive-market rate: `53.33%`
- best total-PnL max single-market PnL share: `43.03%`
- best total-PnL last-window PnL: `-78c`
- best total-PnL rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`
- best market-balanced row:
  `rv600_primary_same_side_ev_step_3c_mid_180_420_ev0`
- best market-balanced entries: `25`
- best market-balanced distinct markets: `10`
- best market-balanced PnL: `+429c`
- best market-balanced matched-v28 delta: `+79c`
- best market-balanced positive-root rate: `44.44%`
- best market-balanced positive-market rate: `50.00%`
- best market-balanced max single-market PnL share: `51.28%`
- best market-balanced rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct`
- anchored forward test entries: `24`
- anchored forward test PnL: `-75c`
- anchored forward matched-v28 delta: `-197c`
- anchored forward positive-root rate: `33.33%`
- anchored forward gate pass: `False`

Interpretation: the market-balance rescue did not fix the core failure mode.
The ninth root pushed anchored-forward market-balance validation negative, and
no positive row clears both concentration and market-stability gates.

## Ninth-Root Objective State

The objective audit was rerun after the corrected nine-root cumulative audit
and refreshed rescue audits.

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.md`
- decision: `blocked_not_complete`
- objective_complete: `False`
*** End of File

## Latest 23-Root Forward Update After RV600NEAR001 Freeze

Collected one new read-only bounded shadow root after freezing `RV600NEAR001`.
This did not place orders, restart the bot, or modify live v28 logic.

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T045448Z`
- dataset:
  `rv600_next_evidence_shadow_20260515T045448Z`
- recorder_returncode: `0`
- matched_control_mode: `offline_v28_public_btc_replay`
- checkpoint rows: `830`
- independent spot rows: `3837`
- independent spot issues: `0`
- offline v28 contexts written: `828`
- offline v28 issues: `2` post-settlement checkpoints
- pipeline contexts written: `751`
- pipeline context issues: `0`
- labels written after delayed refresh: `2`
- label refresh issues: `0`

Root scoring:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T045448Z/rv600_native_forward_opportunity.json`
- total candidate rows: `751`
- settled markets: `2`
- best grid:
  `rv600_primary_max_3_entries_base_70_420_ev6`
- best grid selected PnL: `+201c`
- best grid rejection:
  `fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

`RV600NEAR001` on this root:

- variant:
  `rv600_primary_side_flip_only_broad_70_600_ev4`
- accepted entries: `3`
- distinct markets: `2`
- selected PnL: `+39c`
- average PnL per entry: `13.0c`
- matched-v28 delta: `0c`
- positive market rate: `0.50`
- max single-market PnL share: `1.0769`
- rejection:
  `fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: the first forward-only frozen near-miss root was positive after
fees and cleared the average-entry hurdle by itself, but it was too small,
concentrated, and did not beat matched v28. It is useful future evidence, not a
promotion signal.

## Latest Cumulative State After 23 Bounded Roots

Refreshed reports:

- `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.json`
- `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.json`
- `logs/particle_research/reports/rv600_bounded_current_grid_latest.json`
- `logs/particle_research/reports/rv600_objective_state_latest.json`

Cumulative bounded state:

- roots: `23`
- candidate rows: `18121`
- settled markets: `44`
- locked total entries: `228`
- locked total PnL: `+4760c`
- best grid variant:
  `rv600_primary_max_3_entries_base_70_420_ev6`
- best grid selected PnL: `+1358c`
- best grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`

`RV600NEAR001` cumulative diagnostic state:

- accepted entries: `44`
- distinct markets: `30`
- selected PnL: `+378c`
- matched-v28 delta: `+218c`
- average PnL per entry: `8.5909c`
- positive root rate: `0.6522`
- positive market rate: `0.6000`
- max single-market PnL share: `0.1614`
- last-window PnL: `+39c`
- rejection:
  `avg_entry_below_10c`

Interpretation: the frozen near-miss improved slightly after the first
forward-only root, but it still fails the average-entry gate. Keep collecting
only as pre-registered forward evidence; do not tune or promote it.

## Latest 23-Root Rescue Refresh

After adding the new settled root, I refreshed the rescue/stability audits so
the objective report would not mix 22-root and 23-root evidence.

Meta-label rescue:

- split_count: `18`
- train_gate_selection_count: `0`
- test_selected_pnl_cents: `+13c`
- preliminary_gate_pass: `False`

Probability-calibration rescue:

- split_count: `18`
- train_gate_selection_count: `0`
- test_selected_pnl_cents: `+813c`
- preliminary_gate_pass: `False`

Conformal-abstention rescue:

- split_count: `18`
- train_gate_selection_count: `0`
- test_selected_pnl_cents: `0c`
- preliminary_gate_pass: `False`

Online-expert rescue:

- split_count: `18`
- train_gate_selection_count: `0`
- test_selected_pnl_cents: `+321c`
- preliminary_gate_pass: `False`

Market-balance rescue:

- decision: `market_balance_rescue_failed`
- root_count: `23`
- gate_pass_rows: `0`
- positive_concentration_ok_rows: `1394`
- positive_both_balance_ok_rows: `25`
- prequential_gate_pass: `False`
- prequential_test_pnl_cents: `+298c`

Regime-filter rescue:

- decision: `regime_filter_rescue_failed`
- roots: `23`
- summary_row_count: `130284`
- support_row_count: `0`
- prequential_gate_pass: `False`
- prequential_test_pnl_cents: `+568c`

Group-DRO rescue:

- decision: `group_dro_rescue_failed`
- roots: `23`
- support_row_count: `0`
- prequential_gate_pass: `False`
- prequential_test_pnl_cents: `+782c`

PBO stability audit:

- decision: `pbo_rejects_current_grid`
- root_count: `23`
- candidate_count: `5451`
- valid_split_count: `512`
- pbo: `0.546875`
- positive_split_rate: `0.8223`
- mean_selected_test_pnl_cents: `+252.918c`

Stability-selection rescue:

- decision: `stability_selection_rescue_failed`
- root_count: `23`
- candidate_count: `1260`
- locked_selection_count: `140`
- full_support_count: `0`
- selected-test PnL: `+15197c`
- selected-test matched-v28 delta: `+4823c`
- selected-test average PnL per entry: `3.2334c`
- rejection:
  `no_full_sample_support_row;selection_rate_below_threshold;avg_test_entry_below_10c`

Objective state remains:

- decision: `blocked_not_complete`
- objective_complete: `False`

## Latest 23-Root Status Pointer

The latest RV600 state is 23 settled bounded roots after freezing and collecting
the first `RV600NEAR001` forward-only diagnostic root. Current artifacts:

- frozen plan:
  `logs/particle_research/locked_oos_plans/rv600_breadth_nearmiss_RV600NEAR001_locked_plan.json`
- newest root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T045448Z`
- cumulative opportunity:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.json`
- cumulative bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.json`
- current grid:
  `logs/particle_research/reports/rv600_bounded_current_grid_latest.json`
- objective audit:
  `logs/particle_research/reports/rv600_objective_state_latest.json`

Headline after 23 roots:

- cumulative roots: `23`
- settled markets: `44`
- locked entries: `228`
- locked PnL: `+4760c`
- best grid:
  `rv600_primary_max_3_entries_base_70_420_ev6`
- best grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`
- `RV600NEAR001` cumulative PnL: `+378c`
- `RV600NEAR001` average entry: `8.5909c`
- `RV600NEAR001` rejection: `avg_entry_below_10c`
- PBO decision: `pbo_rejects_current_grid`, `pbo=0.546875`
- stability-selection decision: `stability_selection_rescue_failed`
- objective decision: `blocked_not_complete`

The first forward-only `RV600NEAR001` root was positive (`+39c`, `13.0c`
average entry) but too small, concentrated, and did not beat matched v28. Keep
future evidence pre-registered and research-only; do not tune or promote.
- added/current blockers include:
  `pbo_stability_rejected` and `stability_selection_rescue_failed`
- cumulative bounded roots: `9`
- cumulative bounded settled markets: `18`
- cumulative bounded locked RV600 PnL: `+746c`
- cumulative bounded best-grid PnL: `+567c`
- cumulative bounded best-grid matched-v28 delta: `+513c`
- current blockers:
  `current_locked_family_rejected`,
  `no_existing_plan_family_viable`,
  `forward_shadow_pnl_negative`,
  `forward_shadow_sample_incomplete`,
  `meta_label_rescue_failed`,
  `probability_calibration_rescue_failed`,
  `conformal_abstention_rescue_failed`,
  `online_expert_rescue_failed`,
  `no_current_plan_revision_supported`,
  `fresh_shadow_smoke_insufficient`,
  `fresh_bounded_shadow_insufficient`,
  `cumulative_bounded_shadow_insufficient`,
  `market_balance_rescue_failed`,
  `regime_filter_rescue_failed`

Interpretation: RV600 remains research-only and blocked. The latest evidence
has real profitable pockets, but it still fails the spec's anti-overfitting
requirements for stability, concentration, matched-control validation, and
forward sample sufficiency.

## Tenth Bounded 900-Second Shadow Run

Two launch attempts immediately before the clean tenth root are excluded from
the evidence set:

- `rv600_next_evidence_shadow_20260514T010633Z`: failed at launch because
  PowerShell split the `--v28-events` path with spaces; no paired manifest,
  pipeline manifest, or candidate snapshots were written.
- `rv600_next_evidence_shadow_20260514T010744Z`: stopped during operator
  sanity-check after mistaking the Windows venv/base-interpreter process pair
  for duplicate collectors; no paired manifest, pipeline manifest, or candidate
  snapshots were written.

The clean tenth root was then collected with the encoded PowerShell launch path
and left to finish normally.

- root:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T010859Z`
- paired passive manifest:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T010859Z\paired_passive_run_manifest.json`
- refresh report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T010859Z_refresh.md`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T010859Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260514T010859Z_audit.md`
- collection: `836` checkpoint rows, `5994` independent spot ticks
- live-context merge: `213` stale/unusable rows, so scoring used the
  research-only offline v28 replay fallback
- offline v28 contexts: `833` written, `3` unusable rows dropped
- pipeline: `819` candidate rows, `0` context issues
- labels: `2` settled markets, `0` label issues
- locked RV600 entries: `14`
- locked RV600 PnL: `+943c`
- best existing-grid row:
  `rv600_primary_max_3_entries_broad_70_600_ev6`
- best existing-grid entries: `6`
- best existing-grid PnL: `+337c`
- best existing-grid matched-v28 delta: `0c`
- best existing-grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: the tenth slice was strongly positive for the locked RV600
ledger, but the best standalone grid row was still too sparse, concentrated,
and not better than matched v28 on the same timestamps. It is useful incoming
evidence, not completion evidence by itself.

## Ten-Root Cumulative Bounded Shadow Evidence

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `10`
- candidate rows: `7960`
- settled markets: `20`
- locked RV600 entries: `96`
- locked RV600 PnL: `+1689c`
- best existing-grid row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best existing-grid entries: `51`
- best existing-grid distinct markets: `17`
- best existing-grid PnL: `+876c`
- best existing-grid matched-v28 delta: `+513c`
- best existing-grid positive-root rate: `70.00%`
- best existing-grid positive-market rate: `58.82%`
- best existing-grid max single-market PnL share: `27.85%`
- best existing-grid last-window PnL: `+309c`
- best existing-grid rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct`

Interpretation: the tenth root materially improved cumulative PnL, recent-window
PnL, and root stability. The leading existing-grid row is now close to the
market-stability and concentration gates, but it still fails both: `58.82%`
positive markets is below `60%`, and `27.85%` single-market share is above
`25%`. The completion sample is also still short of the spec's `100` accepted
entries, `40` markets, `10` calendar days, and two weekend sessions.

## Ten-Root Failure-Pattern Refresh

- report:
  `logs/particle_research/reports/rv600_failure_pattern_audit_latest.md`
- source roots: `10`
- variants: `3948`
- summary rows: `11844`
- position-capped positive-PnL rows: `3799`
- position-capped rows with positive matched-v28 delta: `231`
- strict support rows: `0`
- rescue gate-pass rows: `0`
- top rejection reasons:
  `positive_roots_below_60pct=3796`,
  `single_market_share_above_25pct=3793`,
  `positive_markets_below_60pct=3718`,
  `does_not_beat_matched_v28_by_20pct=3619`,
  `fewer_than_25_entries=2950`,
  `avg_entry_below_10c=1432`
- best soft position-capped row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best soft entries: `51`
- best soft distinct markets: `17`
- best soft PnL: `+876c`
- best soft matched-v28 delta: `+513c`
- best soft positive-root rate: `70.00%`
- best soft positive-market rate: `58.82%`
- best soft max single-market PnL share: `27.85%`
- best soft rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct`

Interpretation: aggregate PnL improved, but the failure-pattern audit still
does not support a current plan revision. The strongest simple row misses the
same two anti-overfitting gates by a narrow margin.

## Ten-Root Regime-Filter Rescue Refresh

- report:
  `logs/particle_research/reports/rv600_regime_filter_rescue_latest.md`
- decision: `regime_filter_rescue_failed`
- source roots: `10`
- predicates: `11`
- summary rows: `130284`
- strict support rows: `1`
- support row:
  `rv600_primary_max_2_entries_broad_70_600_ev0__regime_near_strike_10bp`
- support row entries: `30`
- support row distinct markets: `15`
- support row PnL: `+683c`
- support row matched-v28 delta: `+390c`
- support row average PnL per entry: `22.77c`
- support row positive-root rate: `70.00%`
- support row positive-market rate: `60.00%`
- support row max single-market PnL share: `23.72%`
- support row last-window PnL: `+208c`
- support row rejection: none
- anchored forward test entries: `24`
- anchored forward PnL: `+133c`
- anchored forward matched-v28 delta: `-197c`
- anchored forward positive-root rate: `42.86%`
- anchored forward max single-market share: `146.62%`
- anchored forward gate pass: `False`

Interpretation: this is the first clean in-sample regime-filter support row,
but it is not a validated strategy. It failed anchored forward validation by
losing to matched v28, falling below the positive-root gate, and remaining
highly concentrated in the anchored test splits.

## Ten-Root Market-Balance Rescue Refresh

- report:
  `logs/particle_research/reports/rv600_market_balance_rescue_latest.md`
- decision: `market_balance_rescue_failed`
- roots: `10`
- summary rows: `11844`
- full gate-pass rows: `0`
- positive rows with single-market concentration <= `25%`: `18`
- positive rows with both concentration <= `25%` and positive-market rate >=
  `60%`: `0`
- best total-PnL row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best total-PnL entries: `51`
- best total-PnL distinct markets: `17`
- best total-PnL PnL: `+876c`
- best total-PnL matched-v28 delta: `+513c`
- best total-PnL positive-root rate: `70.00%`
- best total-PnL positive-market rate: `58.82%`
- best total-PnL max single-market PnL share: `27.85%`
- best total-PnL last-window PnL: `+309c`
- best total-PnL rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct`
- anchored forward test entries: `29`
- anchored forward test PnL: `-33c`
- anchored forward matched-v28 delta: `-197c`
- anchored forward positive-root rate: `42.86%`
- anchored forward gate pass: `False`

Interpretation: the market-balance rescue improved enough that some positive
rows now meet the concentration cap alone, but no row also meets the
positive-market-rate gate. Anchored forward market-balance validation remains
negative.

## Ten-Root Objective State

The objective audit was rerun after the ten-root cumulative and rescue refresh.

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.md`
- decision: `blocked_not_complete`
- objective_complete: `False`
- cumulative bounded roots: `10`
- cumulative bounded settled markets: `20`
- cumulative bounded locked RV600 entries: `96`
- cumulative bounded locked RV600 PnL: `+1689c`
- cumulative bounded best-grid entries: `51`
- cumulative bounded best-grid PnL: `+876c`
- cumulative bounded best-grid matched-v28 delta: `+513c`
- regime-filter support rows: `1`
- market-balance gate-pass rows: `0`
- current blockers:
  `current_locked_family_rejected`,
  `no_existing_plan_family_viable`,
  `forward_shadow_pnl_negative`,
  `forward_shadow_sample_incomplete`,
  `meta_label_rescue_failed`,
  `probability_calibration_rescue_failed`,
  `conformal_abstention_rescue_failed`,
  `online_expert_rescue_failed`,
  `no_current_plan_revision_supported`,
  `fresh_shadow_smoke_insufficient`,
  `fresh_bounded_shadow_insufficient`,
  `cumulative_bounded_shadow_insufficient`,
  `market_balance_rescue_failed`,
  `regime_filter_rescue_failed`

Interpretation: RV600 is closer but still blocked. The tenth root gave a real
positive signal and a plausible regime-filter clue, but the objective remains
incomplete until a candidate survives anchored/fresh validation and the full
forward-shadow sample gates.

## Eleventh Bounded 900-Second Shadow Run

The eleventh bounded read-only collection was run to test whether the tenth
root's stronger cumulative result and one in-sample regime support row persisted
on the next incoming slice.

- root:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T014324Z`
- paired passive manifest:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T014324Z\paired_passive_run_manifest.json`
- refresh report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T014324Z_refresh.md`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T014324Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260514T014324Z_audit.md`
- collection: `790` checkpoint rows, `12036` independent spot ticks
- live-context merge: `213` stale/unusable rows, so scoring used the
  research-only offline v28 replay fallback
- offline v28 contexts: `788` written, `2` unusable rows dropped
- pipeline: `716` candidate rows, `0` context issues
- labels: `1` settled candidate market, `0` label issues
- locked RV600 entries: `0`
- locked RV600 PnL: `0c`
- best existing-grid row:
  `blend_95_5_max_3_entries_base_70_420_ev0`
- best existing-grid entries: `3`
- best existing-grid PnL: `+8c`
- best existing-grid matched-v28 delta: `0c`
- best existing-grid rejection:
  `fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: the eleventh root is a clean but weak incoming slice. It added
coverage but no locked RV600 entries, and its tiny positive grid row is only a
sparse diagnostic.

## Eleven-Root Cumulative Bounded Shadow Evidence

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `11`
- candidate rows: `8676`
- settled markets: `21`
- locked RV600 entries: `96`
- locked RV600 PnL: `+1689c`
- best existing-grid row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best existing-grid entries: `54`
- best existing-grid distinct markets: `18`
- best existing-grid PnL: `+816c`
- best existing-grid matched-v28 delta: `+513c`
- best existing-grid positive-root rate: `63.64%`
- best existing-grid positive-market rate: `55.56%`
- best existing-grid max single-market PnL share: `29.90%`
- best existing-grid last-window PnL: `-60c`
- best existing-grid rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`

Interpretation: the eleventh root weakened the tenth-root improvement. Aggregate
PnL remains positive, but market stability, concentration, and recent-window
gates all fail again.

## Eleven-Root Failure-Pattern Refresh

- report:
  `logs/particle_research/reports/rv600_failure_pattern_audit_latest.md`
- source roots: `11`
- variants: `3948`
- summary rows: `11844`
- position-capped positive-PnL rows: `3796`
- position-capped rows with positive matched-v28 delta: `231`
- strict support rows: `0`
- rescue gate-pass rows: `0`
- top rejection reasons:
  `positive_roots_below_60pct=3904`,
  `single_market_share_above_25pct=3796`,
  `last_window_nonpositive=3777`,
  `positive_markets_below_60pct=3722`,
  `does_not_beat_matched_v28_by_20pct=3619`,
  `fewer_than_25_entries=2913`
- best soft position-capped row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best soft entries: `54`
- best soft distinct markets: `18`
- best soft PnL: `+816c`
- best soft matched-v28 delta: `+513c`
- best soft positive-root rate: `63.64%`
- best soft positive-market rate: `55.56%`
- best soft max single-market PnL share: `29.90%`
- best soft last-window PnL: `-60c`
- best soft rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`

Interpretation: no current plan revision is supported. The leading simple row
is profitable, but the new weak slice pulled it farther from the market and
concentration gates.

## Eleven-Root Regime-Filter Rescue Refresh

- report:
  `logs/particle_research/reports/rv600_regime_filter_rescue_latest.md`
- decision: `regime_filter_rescue_failed`
- source roots: `11`
- predicates: `11`
- summary rows: `130284`
- strict support rows: `0`
- best row:
  `rv600_primary_risk_cap_100c_broad_70_600_ev0__regime_near_strike_10bp`
- best row entries: `44`
- best row distinct markets: `16`
- best row PnL: `+847c`
- best row matched-v28 delta: `+402c`
- best row average PnL per entry: `19.25c`
- best row positive-root rate: `54.55%`
- best row positive-market rate: `50.00%`
- best row max single-market PnL share: `28.81%`
- best row last-window PnL: `-60c`
- best row rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`
- anchored forward test entries: `26`
- anchored forward PnL: `+91c`
- anchored forward matched-v28 delta: `-197c`
- anchored forward positive-root rate: `37.50%`
- anchored forward gate pass: `False`

Interpretation: the tenth-root in-sample support row did not persist. After the
eleventh root there are zero strict regime support rows, and anchored validation
still loses to matched v28.

## Eleven-Root Market-Balance Rescue Refresh

- report:
  `logs/particle_research/reports/rv600_market_balance_rescue_latest.md`
- decision: `market_balance_rescue_failed`
- roots: `11`
- summary rows: `11844`
- full gate-pass rows: `0`
- positive rows with single-market concentration <= `25%`: `0`
- positive rows with both concentration <= `25%` and positive-market rate >=
  `60%`: `0`
- best total-PnL row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best total-PnL entries: `54`
- best total-PnL distinct markets: `18`
- best total-PnL PnL: `+816c`
- best total-PnL matched-v28 delta: `+513c`
- best total-PnL positive-root rate: `63.64%`
- best total-PnL positive-market rate: `55.56%`
- best total-PnL max single-market PnL share: `29.90%`
- best total-PnL last-window PnL: `-60c`
- best total-PnL rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`
- anchored forward test entries: `32`
- anchored forward test PnL: `-93c`
- anchored forward matched-v28 delta: `-197c`
- anchored forward positive-root rate: `37.50%`
- anchored forward gate pass: `False`

Interpretation: market balance regressed after the eleventh root. No positive
row clears the concentration cap, and the anchored market-balance test remains
negative.

## Eleven-Root Objective State

The objective audit was rerun after the eleven-root cumulative and rescue
refresh.

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.md`
- decision: `blocked_not_complete`
- objective_complete: `False`
- cumulative bounded roots: `11`
- cumulative bounded settled markets: `21`
- cumulative bounded locked RV600 entries: `96`
- cumulative bounded locked RV600 PnL: `+1689c`
- cumulative bounded best-grid entries: `54`
- cumulative bounded best-grid PnL: `+816c`
- cumulative bounded best-grid matched-v28 delta: `+513c`
- regime-filter support rows: `0`
- market-balance gate-pass rows: `0`
- current blockers:
  `current_locked_family_rejected`,
  `no_existing_plan_family_viable`,
  `forward_shadow_pnl_negative`,
  `forward_shadow_sample_incomplete`,
  `meta_label_rescue_failed`,
  `probability_calibration_rescue_failed`,
  `conformal_abstention_rescue_failed`,
  `online_expert_rescue_failed`,
  `no_current_plan_revision_supported`,
  `fresh_shadow_smoke_insufficient`,
  `fresh_bounded_shadow_insufficient`,
  `cumulative_bounded_shadow_insufficient`,
  `market_balance_rescue_failed`,
  `regime_filter_rescue_failed`

Interpretation: RV600 remains research-only and blocked. The eleventh slice is
important because it tested the apparent tenth-root improvement and showed that
the regime and balance repairs are not stable yet.

## Twelfth Bounded 900-Second Shadow Run

The twelfth bounded read-only collection was run after the eleventh root
weakened the apparent tenth-root rescue.

- root:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T021209Z`
- paired passive manifest:
  `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T021209Z\paired_passive_run_manifest.json`
- refresh report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T021209Z_refresh.md`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T021209Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260514T021209Z_audit.md`
- collection: `843` checkpoint rows, `5344` independent spot ticks
- live-context merge: `213` stale/unusable rows, so scoring used the
  research-only offline v28 replay fallback
- offline v28 contexts: `842` written, `1` unusable row dropped
- pipeline: `827` candidate rows, `0` context issues
- labels: `2` settled markets, `0` label issues
- locked RV600 entries: `14`
- locked RV600 PnL: `+1144c`
- best existing-grid row:
  `rv600_primary_max_3_entries_base_70_420_ev0`
- best existing-grid entries: `6`
- best existing-grid PnL: `+287c`
- best existing-grid matched-v28 delta: `+30c`
- best existing-grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: the twelfth slice is a strong positive incoming data point for
the locked RV600 ledger, but the root-level best grid row is still too sparse
and concentrated to stand alone.

## Twelve-Root Cumulative Bounded Shadow Evidence

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `12`
- candidate rows: `9503`
- settled markets: `23`
- locked RV600 entries: `110`
- locked RV600 PnL: `+2833c`
- best existing-grid row:
  `rv600_primary_risk_cap_100c_broad_70_600_ev0`
- best existing-grid entries: `56`
- best existing-grid distinct markets: `20`
- best existing-grid PnL: `+959c`
- best existing-grid matched-v28 delta: `+334c`
- best existing-grid positive-root rate: `58.33%`
- best existing-grid positive-market rate: `45.00%`
- best existing-grid max single-market PnL share: `25.44%`
- best existing-grid last-window PnL: `+145c`
- best existing-grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct`

Interpretation: locked RV600 now clears the raw `100` accepted-entry threshold
and has strong positive cumulative PnL, but the validated strategy gate is still
not met. The best existing-grid row has only `56` accepted entries, only `20`
distinct markets, positive-root and positive-market rates below `60%`, and
single-market share still slightly above `25%`.

## Twelve-Root Failure-Pattern Refresh

- report:
  `logs/particle_research/reports/rv600_failure_pattern_audit_latest.md`
- source roots: `12`
- variants: `3948`
- summary rows: `11844`
- position-capped positive-PnL rows: `3865`
- position-capped rows with positive matched-v28 delta: `186`
- strict support rows: `0`
- rescue gate-pass rows: `0`
- top rejection reasons:
  `positive_roots_below_60pct=3908`,
  `single_market_share_above_25pct=3859`,
  `does_not_beat_matched_v28_by_20pct=3722`,
  `positive_markets_below_60pct=3398`,
  `fewer_than_25_entries=2591`,
  `avg_entry_below_10c=644`
- best soft position-capped row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best soft entries: `60`
- best soft distinct markets: `20`
- best soft PnL: `+937c`
- best soft matched-v28 delta: `+513c`
- best soft positive-root rate: `66.67%`
- best soft positive-market rate: `55.00%`
- best soft max single-market PnL share: `26.04%`
- best soft last-window PnL: `+121c`
- best soft rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct`

Interpretation: the twelfth root repaired recent-window PnL for the best soft
row, but did not repair market stability or concentration enough to support a
plan revision.

## Twelve-Root Regime-Filter Rescue Refresh

- report:
  `logs/particle_research/reports/rv600_regime_filter_rescue_latest.md`
- decision: `regime_filter_rescue_failed`
- source roots: `12`
- predicates: `11`
- summary rows: `130284`
- strict support rows: `0`
- best row:
  `rv600_primary_risk_cap_100c_broad_70_600_ev0__regime_near_strike_10bp`
- best row entries: `50`
- best row distinct markets: `18`
- best row PnL: `+992c`
- best row matched-v28 delta: `+402c`
- best row average PnL per entry: `19.84c`
- best row positive-root rate: `58.33%`
- best row positive-market rate: `50.00%`
- best row max single-market PnL share: `24.60%`
- best row last-window PnL: `+145c`
- best row rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`
- anchored forward test entries: `32`
- anchored forward PnL: `+236c`
- anchored forward matched-v28 delta: `-197c`
- anchored forward positive-root rate: `44.44%`
- anchored forward gate pass: `False`

Interpretation: the regime-filter clue is still not stable enough. It now
clears concentration in the best aggregate row, but fails root/market positivity
and still loses to matched v28 in anchored forward validation.

## Twelve-Root Market-Balance Rescue Refresh

- report:
  `logs/particle_research/reports/rv600_market_balance_rescue_latest.md`
- decision: `market_balance_rescue_failed`
- roots: `12`
- summary rows: `11844`
- full gate-pass rows: `0`
- positive rows with single-market concentration <= `25%`: `18`
- positive rows with both concentration <= `25%` and positive-market rate >=
  `60%`: `0`
- best total-PnL row:
  `rv600_primary_risk_cap_100c_broad_70_600_ev0`
- best total-PnL entries: `56`
- best total-PnL distinct markets: `20`
- best total-PnL PnL: `+959c`
- best total-PnL matched-v28 delta: `+334c`
- best total-PnL positive-root rate: `58.33%`
- best total-PnL positive-market rate: `45.00%`
- best total-PnL max single-market PnL share: `25.44%`
- best total-PnL last-window PnL: `+145c`
- best total-PnL rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct`
- best market-balanced row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best market-balanced entries: `60`
- best market-balanced distinct markets: `20`
- best market-balanced PnL: `+937c`
- best market-balanced matched-v28 delta: `+513c`
- best market-balanced positive-root rate: `66.67%`
- best market-balanced positive-market rate: `55.00%`
- best market-balanced max single-market PnL share: `26.04%`
- best market-balanced rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct`
- anchored forward test entries: `35`
- anchored forward test PnL: `-101c`
- anchored forward matched-v28 delta: `-167c`
- anchored forward positive-root rate: `33.33%`
- anchored forward gate pass: `False`

Interpretation: market-balance remains blocked. Some rows are now close to the
concentration cap, but no positive row clears both concentration and
positive-market requirements, and the anchored market-balance validation is
negative.

## Twelve-Root Objective State

The objective audit was rerun after the twelve-root cumulative and rescue
refresh.

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.md`
- decision: `blocked_not_complete`
- objective_complete: `False`
- cumulative bounded roots: `12`
- cumulative bounded settled markets: `23`
- cumulative bounded locked RV600 entries: `110`
- cumulative bounded locked RV600 PnL: `+2833c`
- cumulative bounded best-grid entries: `56`
- cumulative bounded best-grid PnL: `+959c`
- cumulative bounded best-grid matched-v28 delta: `+334c`
- regime-filter support rows: `0`
- market-balance gate-pass rows: `0`
- current blockers:
  `current_locked_family_rejected`,
  `no_existing_plan_family_viable`,
  `forward_shadow_pnl_negative`,
  `forward_shadow_sample_incomplete`,
  `meta_label_rescue_failed`,
  `probability_calibration_rescue_failed`,
  `conformal_abstention_rescue_failed`,
  `online_expert_rescue_failed`,
  `no_current_plan_revision_supported`,
  `fresh_shadow_smoke_insufficient`,
  `fresh_bounded_shadow_insufficient`,
  `cumulative_bounded_shadow_insufficient`,
  `market_balance_rescue_failed`,
  `regime_filter_rescue_failed`

Interpretation: RV600 is meaningfully stronger on cumulative PnL and raw locked
entry count, but still fails the completion audit. The missing pieces are
market coverage, time coverage, stable root/market positivity, concentration,
and anchored/fresh matched-v28 validation.

## Thirteenth Bounded Shadow Root

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260514T024042Z`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T024042Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260514T024042Z_audit.md`
- collection: recorder, tailer, and independent spot capture all exited `0`
- checkpoint rows: `807`
- independent spot rows: `4932`
- offline v28 contexts: `805` written, `2` unusable rows dropped
- pipeline: `753` candidate rows, `0` context issues
- labels: `2` settled markets, `0` label issues
- locked RV600 entries: `10`
- locked RV600 PnL: `-80c`
- best existing-grid row:
  `blend_95_5_max_3_entries_broad_70_600_ev4`
- best existing-grid entries: `4`
- best existing-grid PnL: `+7c`
- best existing-grid matched-v28 delta: `+0c`
- best existing-grid rejection:
  `fewer_than_25_entries;avg_entry_below_10c;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best RV600-primary row:
  `rv600_primary_max_2_entries_late_70_180_ev0`
- best RV600-primary entries: `2`
- best RV600-primary PnL: `+2c`
- best locked row:
  `rv600_primary_max_3_entries_mid_120_420_ev12`
- best locked entries: `2`
- best locked PnL: `-16c`

Interpretation: the thirteenth slice is a negative fresh-shadow data point for
the locked RV600 ledger. Isolated grid rows can find small positive PnL, but
they are too sparse, too low-value per entry, and still fail matched-v28 and
market-balance gates.

## Thirteen-Root Cumulative Bounded Shadow Evidence

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `13`
- candidate rows: `10256`
- settled markets: `25`
- locked RV600 entries: `120`
- locked RV600 PnL: `+2753c`
- best existing-grid row:
  `rv600_primary_risk_cap_100c_broad_70_600_ev0`
- best existing-grid entries: `62`
- best existing-grid distinct markets: `22`
- best existing-grid PnL: `+940c`
- best existing-grid matched-v28 delta: `+334c`
- best existing-grid average PnL per entry: `+15.16c`
- best existing-grid positive-root rate: `53.85%`
- best existing-grid positive-market rate: `45.45%`
- best existing-grid max single-market PnL share: `25.96%`
- best existing-grid last-window PnL: `-19c`
- best existing-grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`

Interpretation: the thirteen-root cumulative ledger remains profitable, but the
new root weakened the validation picture. The best existing-grid row still has
only `62` accepted entries and `22` distinct markets, fails root/market
positivity, remains just above the single-market concentration cap, and now has
a nonpositive last-window check.

## Thirteen-Root Failure-Pattern Refresh

- report:
  `logs/particle_research/reports/rv600_failure_pattern_audit_latest.md`
- decision: `no_current_plan_revision_supported`
- plan revision supported: `False`
- strict support rows: `0`
- rescue gate-pass rows: `0`

Interpretation: the current evidence still does not justify a narrow plan
revision or a new frozen candidate from the existing mined sample.

## Thirteen-Root Regime-Filter Rescue Refresh

- report:
  `logs/particle_research/reports/rv600_regime_filter_rescue_latest.md`
- decision: `regime_filter_rescue_failed`
- source roots: `13`
- summary rows: `130284`
- strict support rows: `0`
- best row:
  `rv600_primary_risk_cap_100c_broad_70_600_ev0__regime_near_strike_10bp`
- best row entries: `53`
- best row PnL: `+968c`
- best row matched-v28 delta: `+402c`
- best row rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`
- anchored forward test PnL: `+212c`
- anchored forward matched-v28 delta: `-197c`
- anchored forward gate pass: `False`

Interpretation: the regime filter still fails. Even with positive anchored test
PnL, it loses to matched v28 and does not clear stability/concentration gates.

## Thirteen-Root Market-Balance Rescue Refresh

- report:
  `logs/particle_research/reports/rv600_market_balance_rescue_latest.md`
- decision: `market_balance_rescue_failed`
- roots: `13`
- full gate-pass rows: `0`
- positive rows with single-market concentration <= `25%`: `18`
- positive rows with both concentration <= `25%` and positive-market rate >=
  `60%`: `0`
- best market-balanced row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best market-balanced entries: `66`
- best market-balanced PnL: `+926c`
- best market-balanced matched-v28 delta: `+513c`
- best market-balanced rejection:
  `positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`
- anchored forward test PnL: `-112c`
- anchored forward matched-v28 delta: `-167c`
- anchored forward gate pass: `False`

Interpretation: market balance remains the main practical blocker. Some rows
still look profitable in aggregate, but none clear both concentration and
market-positivity requirements, and the anchored market-balance validation is
negative.

## Thirteen-Root Objective State

The objective audit was rerun after the thirteen-root cumulative, failure, and
rescue refresh.

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.md`
- decision: `blocked_not_complete`
- objective_complete: `False`
- cumulative bounded roots: `13`
- cumulative bounded settled markets: `25`
- cumulative bounded locked RV600 entries: `120`
- cumulative bounded locked RV600 PnL: `+2753c`
- cumulative bounded best-grid entries: `62`
- cumulative bounded best-grid PnL: `+940c`
- cumulative bounded best-grid matched-v28 delta: `+334c`
- cumulative bounded best-grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`
- market-balance gate-pass rows: `0`
- regime-filter support rows: `0`
- current blockers:
  `current_locked_family_rejected`,
  `no_existing_plan_family_viable`,
  `forward_shadow_pnl_negative`,
  `forward_shadow_sample_incomplete`,
  `meta_label_rescue_failed`,
  `probability_calibration_rescue_failed`,
  `conformal_abstention_rescue_failed`,
  `online_expert_rescue_failed`,
  `no_current_plan_revision_supported`,
  `fresh_shadow_smoke_insufficient`,
  `fresh_bounded_shadow_insufficient`,
  `cumulative_bounded_shadow_insufficient`,
  `market_balance_rescue_failed`,
  `regime_filter_rescue_failed`

Interpretation: RV600 still cannot be promoted or treated as goal-complete. It
has cumulative positive PnL, but the current plan-defined families fail the
anti-overfitting gates, the newest root was negative for the locked ledger, and
the rescue probes did not produce a viable replacement.

## Fourteenth Bounded Shadow Root

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260514T031420Z`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T031420Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260514T031420Z_audit.md`
- collection: recorder, tailer, and independent spot capture all exited `0`
- checkpoint rows: `839`
- independent spot rows: `6418`
- offline v28 contexts: `837` written, `2` unusable rows dropped
- pipeline: `812` candidate rows, `0` context issues
- labels: `1` settled market, `0` label issues
- locked RV600 entries: `14`
- locked RV600 PnL: `+1167c`
- best existing-grid row:
  `rv600_primary_max_3_entries_base_70_420_ev2`
- best existing-grid entries: `3`
- best existing-grid PnL: `+291c`
- best existing-grid matched-v28 delta: `+585c`
- best existing-grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct`
- best locked row:
  `rv600_primary_max_3_entries_mid_120_420_ev12`
- best locked entries: `3`
- best locked PnL: `+250c`
- root-specific audit decision:
  `cumulative_bounded_pending_settlement_or_scoring`

Interpretation: the fourteenth slice is strongly positive, but only one market
was settled at scoring time. It improves the cumulative ledger, yet remains
single-market evidence and cannot satisfy the anti-overfitting gates alone.

## Fourteen-Root Cumulative Bounded Shadow Evidence

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `14`
- candidate rows: `11068`
- settled markets: `26`
- locked RV600 entries: `134`
- locked RV600 PnL: `+3920c`
- best existing-grid row:
  `rv600_primary_risk_cap_100c_broad_70_600_ev0`
- best existing-grid entries: `65`
- best existing-grid distinct markets: `23`
- best existing-grid PnL: `+1140c`
- best existing-grid matched-v28 delta: `+334c`
- best existing-grid average PnL per entry: `+17.54c`
- best existing-grid positive-root rate: `57.14%`
- best existing-grid positive-market rate: `47.83%`
- best existing-grid max single-market PnL share: `21.40%`
- best existing-grid last-window PnL: `+200c`
- best existing-grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`

Interpretation: the fourteenth root repaired the concentration and last-window
checks for the best existing-grid row and moved the root positivity rate closer
to the `60%` gate. The remaining blockers are still material: only `65`
accepted entries, only `23` distinct markets, positive-root rate below `60%`,
and positive-market rate well below `60%`.

## Fourteen-Root Failure-Pattern Refresh

- report:
  `logs/particle_research/reports/rv600_failure_pattern_audit_latest.md`
- decision: `no_current_plan_revision_supported`
- plan revision supported: `False`
- strict support rows: `0`
- rescue gate-pass rows: `0`

Interpretation: even after the positive fourteenth slice, the current evidence
still does not support a narrow plan revision or newly frozen candidate from the
existing mined sample.

## Fourteen-Root Regime-Filter Rescue Refresh

- report:
  `logs/particle_research/reports/rv600_regime_filter_rescue_latest.md`
- decision: `regime_filter_rescue_failed`
- source roots: `14`
- strict support rows: `0`
- best row:
  `rv600_primary_risk_cap_100c_broad_70_600_ev0__regime_near_strike_10bp`
- best row entries: `56`
- best row PnL: `+1168c`
- best row matched-v28 delta: `+402c`
- best row rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`
- anchored forward test PnL: `+412c`
- anchored forward matched-v28 delta: `-197c`
- anchored forward gate pass: `False`

Interpretation: the regime-filter clue improved on raw PnL, but still fails
root/market positivity and loses to matched v28 in anchored validation.

## Fourteen-Root Market-Balance Rescue Refresh

- report:
  `logs/particle_research/reports/rv600_market_balance_rescue_latest.md`
- decision: `market_balance_rescue_failed`
- roots: `14`
- full gate-pass rows: `0`
- positive rows with single-market concentration <= `25%`: `180`
- positive rows with both concentration <= `25%` and positive-market rate >=
  `60%`: `10`
- best market-balanced row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best market-balanced entries: `69`
- best market-balanced PnL: `+1126c`
- best market-balanced matched-v28 delta: `+513c`
- best market-balanced rejection:
  `positive_markets_below_60pct`
- anchored forward test PnL: `+88c`
- anchored forward matched-v28 delta: `-167c`
- anchored forward gate pass: `False`

Interpretation: market balance is closer than it was at thirteen roots, but it
still does not pass. Aggregate rows now clear concentration more often, yet the
prequential/anchored check still fails and remains behind matched v28.

## Fourteen-Root Objective State

The objective audit was rerun after the fourteen-root cumulative, failure, and
rescue refresh.

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.md`
- decision: `blocked_not_complete`
- objective_complete: `False`
- cumulative bounded roots: `14`
- cumulative bounded settled markets: `26`
- cumulative bounded locked RV600 entries: `134`
- cumulative bounded locked RV600 PnL: `+3920c`
- cumulative bounded best-grid entries: `65`
- cumulative bounded best-grid PnL: `+1140c`
- cumulative bounded best-grid matched-v28 delta: `+334c`
- cumulative bounded best-grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`
- market-balance gate-pass rows: `0`
- regime-filter support rows: `0`
- current blockers:
  `current_locked_family_rejected`,
  `no_existing_plan_family_viable`,
  `forward_shadow_pnl_negative`,
  `forward_shadow_sample_incomplete`,
  `meta_label_rescue_failed`,
  `probability_calibration_rescue_failed`,
  `conformal_abstention_rescue_failed`,
  `online_expert_rescue_failed`,
  `no_current_plan_revision_supported`,
  `fresh_shadow_smoke_insufficient`,
  `fresh_bounded_shadow_insufficient`,
  `cumulative_bounded_shadow_insufficient`,
  `market_balance_rescue_failed`,
  `regime_filter_rescue_failed`

Interpretation: RV600 improved materially on cumulative PnL and concentration,
but the goal is still not complete. The live-shadow sample is still too narrow
and unstable, the current locked family remains rejected, no existing
plan-defined family is viable, and no rescue path has produced a passing
prequential gate.

## Fifteenth Bounded Shadow Root

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260514T035926Z`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T035926Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260514T035926Z_audit.md`
- collection: recorder, tailer, and independent spot capture all exited `0`
- checkpoint rows: `811`
- independent spot rows: `4300`
- offline v28 contexts: `808` written, `3` unusable rows dropped
- pipeline: `767` candidate rows, `0` context issues
- labels: `2` settled markets, `0` label issues
- locked RV600 entries: `0`
- locked RV600 PnL: `+0c`
- best existing-grid row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best existing-grid entries: `3`
- best existing-grid PnL: `+104c`
- best existing-grid matched-v28 delta: `+0c`
- best existing-grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best locked row:
  `rv600_primary_max_3_entries_mid_120_420_ev12`
- best locked entries: `0`
- best locked PnL: `+0c`

Interpretation: the fifteenth slice adds useful settled market coverage, but it
does not help the locked RV600 ledger. The only positive row is an existing-grid
diagnostic with three early entries in one market and no matched-v28 edge.

## Fifteen-Root Cumulative Bounded Shadow Evidence

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `15`
- candidate rows: `11835`
- settled markets: `28`
- locked RV600 entries: `134`
- locked RV600 PnL: `+3920c`
- best existing-grid row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best existing-grid entries: `72`
- best existing-grid distinct markets: `24`
- best existing-grid PnL: `+1230c`
- best existing-grid matched-v28 delta: `+513c`
- best existing-grid average PnL per entry: `+17.08c`
- best existing-grid positive-root rate: `66.67%`
- best existing-grid positive-market rate: `58.33%`
- best existing-grid max single-market PnL share: `19.84%`
- best existing-grid last-window PnL: `+104c`
- best existing-grid rejection:
  `positive_markets_below_60pct`

Interpretation: cumulative best-grid evidence is now close to a stability pass,
but it is still not complete. The best row clears root positivity,
concentration, last-window PnL, matched-v28 delta, and average-entry checks, but
positive-market rate remains just below the `60%` gate, the sample is still only
`24` distinct markets, and the current locked family itself did not add entries.

## Fifteen-Root Failure-Pattern Refresh

- report:
  `logs/particle_research/reports/rv600_failure_pattern_audit_latest.md`
- decision: `no_current_plan_revision_supported`
- plan revision supported: `False`
- strict support rows: `0`
- rescue gate-pass rows: `0`

Interpretation: the updated evidence still does not support a narrow plan
revision or newly frozen candidate from the existing mined sample.

## Fifteen-Root Regime-Filter Rescue Refresh

- report:
  `logs/particle_research/reports/rv600_regime_filter_rescue_latest.md`
- decision: `regime_filter_rescue_failed`
- source roots: `15`
- strict support rows: `0`
- best row:
  `rv600_primary_max_3_entries_broad_70_600_ev0__regime_all`
- best row entries: `72`
- best row PnL: `+1230c`
- best row matched-v28 delta: `+513c`
- best row rejection:
  `positive_markets_below_60pct`
- anchored forward test PnL: `+448c`
- anchored forward matched-v28 delta: `-197c`
- anchored forward gate pass: `False`

Interpretation: the regime-filter result has converged back to the same broad
row and still fails the anchored matched-v28 check.

## Fifteen-Root Market-Balance Rescue Refresh

- report:
  `logs/particle_research/reports/rv600_market_balance_rescue_latest.md`
- decision: `market_balance_rescue_failed`
- roots: `15`
- full gate-pass rows: `0`
- positive rows with single-market concentration <= `25%`: `234`
- positive rows with both concentration <= `25%` and positive-market rate >=
  `60%`: `22`
- best market-balanced row:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best market-balanced entries: `72`
- best market-balanced PnL: `+1230c`
- best market-balanced matched-v28 delta: `+513c`
- best market-balanced rejection:
  `positive_markets_below_60pct`
- anchored forward test PnL: `+192c`
- anchored forward matched-v28 delta: `-167c`
- anchored forward gate pass: `False`

Interpretation: market balance is improving on aggregate support counts, but no
row clears the full gate and anchored validation still trails matched v28.

## Fifteen-Root Objective State

The objective audit was rerun after the fifteen-root cumulative, failure, and
rescue refresh.

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.md`
- decision: `blocked_not_complete`
- objective_complete: `False`
- cumulative bounded roots: `15`
- cumulative bounded settled markets: `28`
- cumulative bounded locked RV600 entries: `134`
- cumulative bounded locked RV600 PnL: `+3920c`
- cumulative bounded best-grid entries: `72`
- cumulative bounded best-grid PnL: `+1230c`
- cumulative bounded best-grid matched-v28 delta: `+513c`
- cumulative bounded best-grid rejection:
  `positive_markets_below_60pct`
- market-balance gate-pass rows: `0`
- regime-filter support rows: `0`
- current blockers:
  `current_locked_family_rejected`,
  `no_existing_plan_family_viable`,
  `forward_shadow_pnl_negative`,
  `forward_shadow_sample_incomplete`,
  `meta_label_rescue_failed`,
  `probability_calibration_rescue_failed`,
  `conformal_abstention_rescue_failed`,
  `online_expert_rescue_failed`,
  `no_current_plan_revision_supported`,
  `fresh_shadow_smoke_insufficient`,
  `fresh_bounded_shadow_insufficient`,
  `cumulative_bounded_shadow_insufficient`,
  `market_balance_rescue_failed`,
  `regime_filter_rescue_failed`

Interpretation: RV600 is closer on the broad grid than before, but the goal is
still not complete. The locked family remains rejected, the best broad grid row
still fails positive-market coverage, the native sample remains below the
required distinct-market/time/weekend evidence, and the rescue probes still do
not clear prequential matched-control validation.

## Sixteenth-Root Collection Reliability Fix

Two attempted sixteenth roots were excluded from evidence before scoring:

- `rv600_next_evidence_shadow_20260514T043118Z` was quarantined under
  `logs/particle_research/failed_collections/` because Coinbase spot capture
  ended early with `no close frame received or sent`.
- `rv600_next_evidence_shadow_20260514T043808Z` was quarantined under
  `logs/particle_research/failed_collections/` because Coinbase spot capture
  returned nonzero after a partial tape.
- A Binance spot fallback was tested as
  `rv600_next_evidence_shadow_20260514T045503Z`, but Binance rejected the
  websocket connection with `HTTP 451`, so that root was also quarantined and
  not used as evidence.

The research-only spot recorder was then patched to reconnect until the
requested passive run window expires:

- file changed:
  `research_particle/spot_ticker_recorder.py`
- smoke test:
  `logs/particle_research/recorder_smoke/coinbase_reconnect_20260514T0455Z/status.json`
- smoke result: Coinbase reached `20` ticks with `status=max_rows_reached`,
  `issue_count=0`

Sources considered for the operational choice:

- Python `websockets` exception behavior: abnormal closure can surface as
  missing close-frame errors, so reconnecting is the appropriate recorder
  behavior for transient feed closes.
- Coinbase websocket feed guidance: clients should treat market-data websocket
  sessions as reconnectable streams rather than one guaranteed permanent
  connection.
- Binance websocket docs/status: the local environment received `HTTP 451`, so
  Binance was not used for RV600 evidence.

Interpretation: this was an evidence-quality fix, not a strategy change. It
only affects passive research collection and does not touch live v28 logic or
order submission.

## Sixteenth Bounded Shadow Root

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260514T045722Z`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T045722Z_opportunity.md`
- bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260514T045722Z_audit.md`
- collection: recorder, tailer, and independent spot capture all exited `0`
- checkpoint rows: `847`
- independent spot rows: `3714`
- offline v28 contexts: `842` written, `5` unusable rows dropped
- pipeline: `823` candidate rows, `0` context issues
- labels: `2` settled markets, `0` label issues
- locked RV600 entries before the new freeze: `24`
- locked RV600 PnL before the new freeze: `+730c`
- locked RV600 entries after adding the new frozen candidate: `26`
- locked RV600 PnL after adding the new frozen candidate: `+786c`
- best existing-grid row:
  `blend_95_5_max_3_entries_late_70_300_ev10`
- best existing-grid entries: `9`
- best existing-grid PnL: `+253c`
- best existing-grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: the sixteenth clean root is a positive fresh-shadow slice, but
it is not independently sufficient. Its main contribution is that, when folded
into the cumulative corpus, it produced the first bounded cumulative gate pass.

## Sixteen-Root Cumulative Bounded Shadow Evidence

- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- cumulative audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- roots: `16`
- candidate rows: `12658`
- settled markets: `30`
- locked RV600 entries after freezing the new candidate: `188`
- locked RV600 PnL after freezing the new candidate: `+4967c`
- cumulative audit decision:
  `cumulative_bounded_gate_pass`
- best gate-passing grid row:
  `rv600_primary_side_flip_only_broad_70_600_ev4`
- best grid entries: `30`
- best grid distinct markets: `21`
- best grid PnL: `+317c`
- best grid matched-v28 delta: `+263c`
- best grid average PnL per entry: `+10.57c`
- best grid positive-root rate: `62.50%`
- best grid positive-market rate: `61.90%`
- best grid max single-market PnL share: `19.24%`
- best grid last-window PnL: `+56c`
- best grid rejection: none

Interpretation: this is the first bounded cumulative RV600-style gate pass, but
it is still discovery evidence from the same cumulative sample used to select
the row. It justifies freezing a simple candidate for fresh forward validation;
it does not complete the goal by itself.

## New Frozen Candidate For Fresh Forward Validation

The cumulative gate-passing row was frozen in the research harness after the
sixteenth-root audit:

- file changed:
  `research_particle/rv600_variation_test.py`
- frozen candidate:
  `rv600_primary_side_flip_only_broad_70_600_ev4`
- probability mode: `rv600_primary`
- timing window: `T-600s` to `T-70s`
- entry rule: `side_flip_only`
- max entries per market: `2`
- minimum EV: `4c`
- active gate count: `3`
- freeze rationale: it is simple, already in the plan-defined grid, cleared the
  cumulative bounded gates, beat matched v28 on the same timestamps, and avoided
  the single-market concentration artifact on the cumulative corpus.

Pre-freeze evidence remains diagnostic only. Future roots collected after this
freeze must validate the candidate as a locked forward-shadow candidate before
any goal-completion claim.

## Sixteen-Root Rescue Refresh

- failure-pattern report:
  `logs/particle_research/reports/rv600_failure_pattern_audit_latest.md`
- failure-pattern decision: `no_current_plan_revision_supported`
- market-balance report:
  `logs/particle_research/reports/rv600_market_balance_rescue_latest.md`
- market-balance decision: `market_balance_rescue_failed`
- market-balance gate-pass rows: `18`
- market-balance anchored forward PnL: `+349c`
- market-balance anchored matched-v28 delta: `-167c`
- market-balance prequential gate pass: `False`
- regime-filter report:
  `logs/particle_research/reports/rv600_regime_filter_rescue_latest.md`
- regime-filter decision: `regime_filter_rescue_failed`
- regime-filter support rows: `4`
- regime-filter anchored forward PnL: `+605c`
- regime-filter anchored matched-v28 delta: `-197c`
- regime-filter prequential gate pass: `False`

Interpretation: rescue evidence improved but still does not complete the goal.
The next required work is post-freeze forward shadow evidence for
`rv600_primary_side_flip_only_broad_70_600_ev4`, not promotion or live trading.

## Sixteen-Root Objective State

The objective audit was rerun after freezing the candidate and refreshing the
cumulative and rescue reports.

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.md`
- decision: `blocked_not_complete`
- objective_complete: `False`
- cumulative bounded decision:
  `cumulative_bounded_gate_pass`
- cumulative bounded roots: `16`
- cumulative bounded settled markets: `30`
- cumulative bounded locked RV600 entries: `188`
- cumulative bounded locked RV600 PnL: `+4967c`
- cumulative bounded best-grid entries: `30`
- cumulative bounded best-grid PnL: `+317c`
- cumulative bounded best-grid matched-v28 delta: `+263c`
- cumulative bounded best-grid rejection: none
- current blockers still include:
  `current_locked_family_rejected`,
  `no_existing_plan_family_viable`,
  `forward_shadow_pnl_negative`,
  `forward_shadow_sample_incomplete`,
  `market_balance_rescue_failed`,
  `regime_filter_rescue_failed`

Interpretation: the goal remains active. The work has advanced from "no
gate-passing current candidate" to "one simple frozen candidate requiring fresh
post-freeze validation."

## First Post-Freeze Bounded Shadow Root

The first bounded passive root after freezing
`rv600_primary_side_flip_only_broad_70_600_ev4` completed cleanly without live
bot changes, live trades, or a v28 restart.

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260514T053423Z`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T053423Z_opportunity.md`
- bounded root audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260514T053423Z_audit.md`
- recorder_returncode: `0`
- tailer_returncode: `0`
- independent_spot_returncode: `0`
- checkpoint_row_count: `792`
- independent_spot_row_count: `3605`
- independent_spot_issue_count: `0`
- offline v28 contexts: `790`
- offline v28 context issues: `2`
- pipeline candidate contexts: `731`
- pipeline context issues: `0`
- settled labels refreshed: `2`
- label issues: `0`

Root scoring:

- frozen candidate:
  `rv600_primary_side_flip_only_broad_70_600_ev4`
- frozen accepted entries: `2`
- frozen selected PnL: `+4c`
- frozen matched-v28 delta: `-13c`
- frozen rejection:
  `fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best root grid candidate:
  `rv600_primary_max_3_entries_broad_70_600_ev2`
- best root grid accepted entries: `3`
- best root grid PnL: `+36c`
- best root grid matched-v28 delta: `0c`
- best root grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: this root is useful post-freeze evidence because it is
positive for the frozen candidate, but it is too sparse and too concentrated to
support a completion claim.

## Seventeen-Root Cumulative Refresh

The cumulative bounded audit was refreshed after adding the first post-freeze
root.

- cumulative bounded report:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- cumulative opportunity report:
  `logs/particle_research/reports/rv600_cumulative_opportunity_latest.md`
- decision: `cumulative_bounded_gate_pass`
- roots: `17`
- settled markets: `32`
- candidate rows: `13389`
- locked RV600 entries: `190`
- locked RV600 PnL: `+4971c`
- best cumulative frozen/grid candidate:
  `rv600_primary_side_flip_only_broad_70_600_ev4`
- best cumulative accepted entries: `32`
- best cumulative PnL: `+321c`
- best cumulative matched-v28 delta: `+250c`
- best cumulative rejection: none

The refreshed rescue reports still do not pass:

- market-balance decision: `market_balance_rescue_failed`
- market-balance gate-pass rows: `12`
- market-balance anchored forward PnL: `+309c`
- market-balance anchored matched-v28 delta: `-217c`
- market-balance prequential gate pass: `False`
- regime-filter decision: `regime_filter_rescue_failed`
- regime-filter support rows: `4`
- regime-filter anchored forward PnL: `+609c`
- regime-filter anchored matched-v28 delta: `-210c`
- regime-filter prequential gate pass: `False`

Interpretation: cumulative bounded evidence now clears the bounded audit for
the frozen RV600 candidate, but the objective audit still requires more fresh,
post-freeze forward-shadow evidence and stability against the old failed
forward and prequential gates.

## Seventeen-Root Objective State

The objective audit was rerun after the post-freeze root and 17-root cumulative
refresh.

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.md`
- decision: `blocked_not_complete`
- objective_complete: `False`
- latest bounded root entries: `2`
- latest bounded root PnL: `+4c`
- cumulative bounded roots: `17`
- cumulative bounded settled markets: `32`
- cumulative bounded locked entries: `190`
- cumulative bounded locked PnL: `+4971c`
- cumulative bounded best-grid entries: `32`
- cumulative bounded best-grid PnL: `+321c`
- cumulative bounded best-grid matched-v28 delta: `+250c`
- current blockers still include:
  `current_locked_family_rejected`,
  `no_existing_plan_family_viable`,
  `forward_shadow_pnl_negative`,
  `forward_shadow_sample_incomplete`,
  `fresh_bounded_shadow_insufficient`,
  `cumulative_bounded_shadow_insufficient`,
  `market_balance_rescue_failed`,
  `regime_filter_rescue_failed`

Interpretation: the RV600 goal remains active. The first post-freeze root is
encouraging but not enough to override the sample, concentration, matched-v28,
and prequential guardrails.

## Off-Hours Collection Gate Patch

An attempted next root,
`rv600_next_evidence_shadow_20260514T061107Z`, was stopped before scoring
because it was collecting during a BTC15M no-market window. The Coinbase spot
and v28 context streams were writing, but the native passive Kalshi recorder
only emitted `market_discovery_empty` control events and wrote `0` book
checkpoints.

Live read-only API checks showed:

- `GET /markets?series_ticker=KXBTC15M&status=active` returned HTTP `400`
- `GET /markets?series_ticker=KXBTC15M&status=open` returned `0` markets
- unfiltered `GET /markets?series_ticker=KXBTC15M&limit=100` returned future
  initialized markets, with the next usable close around
  `2026-05-14T09:15:00+00:00`

Plausible responses checked:

- keep polling through the off-hours gap: rejected because it creates empty
  roots, unnecessary API load, and no book checkpoints
- switch to synthetic/backfilled shadow rows: rejected because the goal requires
  incoming live-market shadow evidence
- use far-future initialized markets immediately: rejected because a 900-second
  bounded run would end before the market window
- manually wait and rerun later: acceptable, but easy to miss and easy to
  accidentally launch too early
- add an explicit market-window readiness check to the next-evidence gate:
  chosen, because it preserves the research-only boundary and prevents empty
  off-hours collection

Implementation:

- patched `probe_rv600_next_evidence_gate.py`
- the gate now performs one public, read-only unfiltered KXBTC15M market lookup
  before printing `ready_collect_new_shadow_evidence`
- if the next BTC15M close is outside the bounded run window, the gate returns
  `not_ready_collect_new_shadow_evidence` and prints a recommended start time
- latest gate report:
  `logs/particle_research/reports/rv600_next_evidence_gate_latest.md`
- gate decision immediately after patch: `not_ready_collect_new_shadow_evidence`
- recommended start immediately after patch: `2026-05-14T09:00:00+00:00`
- objective audit after the patch still says `blocked_not_complete`

References used for this blocker:

- Kalshi Markets API docs list `GET /markets`, `GET /markets/{ticker}`, market
  orderbook, and trades endpoints:
  `https://docs.kalshi.com/python-sdk/api/MarketsApi`
- Kalshi market lifecycle docs map status filters to `unopened`, `open`,
  `paused`, `closed`, and `settled`, and say `initialized` markets become
  `active` when `open_time` passes:
  `https://docs.kalshi.com/getting_started/market_lifecycle`
- Kalshi Get Markets docs say an empty `status` filter returns markets with any
  status and supports `series_ticker`, `min_close_ts`, and `max_close_ts`:
  `https://docs.kalshi.com/api-reference/market/get-markets`
- Kalshi API environment docs list the production REST/WebSocket base URLs and
  note that the `elections` subdomain still covers all Kalshi markets:
  `https://docs.kalshi.com/getting_started/api_environments`
- The unofficial Kalshi API status page showed no active trading incidents or
  scheduled maintenance during the check:
  `https://kalshistatus.com/`

## Second Post-Freeze Bounded Shadow Root

The market-window gate later reopened and allowed a new bounded passive root.
This run collected an active incoming KXBTC15M market and rotated into the next
market without live trades, live v28 logic changes, or a bot restart.

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260514T122254Z`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T122254Z_opportunity.md`
- bounded root audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260514T122254Z_audit.md`
- refresh report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T122254Z_refresh.md`
- recorder_returncode: `0`
- tailer_returncode: `0`
- independent_spot_returncode: `0`
- checkpoint files: `2`
- checkpoint rows: `850`
- independent spot rows: `3470`
- independent spot issues: `0`
- offline v28 contexts: `844`
- offline v28 context issues: `6`
- pipeline candidate contexts: `794`
- pipeline context issues: `0`
- settled labels refreshed: `2`
- label issues: `0`

Root scoring:

- locked aggregate accepted entries: `2`
- locked aggregate PnL: `-59c`
- best root grid candidate:
  `blend_90_10_max_3_entries_base_70_420_ev2`
- best root grid accepted entries: `6`
- best root grid PnL: `+186c`
- best root grid matched-v28 delta: `0c`
- best root grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best RV600-primary candidate:
  `rv600_primary_side_flip_only_broad_70_600_ev0`
- best RV600-primary accepted entries: `4`
- best RV600-primary PnL: `+5c`
- best RV600-primary matched-v28 delta: `-9c`
- best RV600-primary rejection:
  `fewer_than_25_entries;avg_entry_below_10c;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: this second post-freeze root is valid incoming-market evidence,
but it weakens the frozen/locked RV600 evidence. The best positive row is still
too sparse, highly concentrated, and not ahead of matched v28.

## Eighteen-Root Cumulative Refresh

The cumulative bounded, rescue, failure-pattern, and objective audits were
refreshed after adding `rv600_next_evidence_shadow_20260514T122254Z`.

- cumulative bounded report:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- decision: `cumulative_bounded_scored_with_entries`
- roots: `18`
- settled markets: `34`
- candidate rows: `14183`
- locked RV600 entries: `192`
- locked RV600 PnL: `+4912c`
- best cumulative grid candidate:
  `rv600_primary_max_3_entries_broad_70_600_ev6`
- best cumulative accepted entries: `56`
- best cumulative distinct markets: `20`
- best cumulative PnL: `+1240c`
- best cumulative matched-v28 delta: `+583c`
- best cumulative rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive`
- market-balance decision: `market_balance_rescue_failed`
- market-balance gate-pass rows: `0`
- market-balance anchored forward PnL: `+173c`
- market-balance anchored matched-v28 delta: `-227c`
- regime-filter decision: `regime_filter_rescue_failed`
- regime-filter support rows: `0`
- regime-filter anchored forward PnL: `+550c`
- regime-filter anchored matched-v28 delta: `-227c`
- failure-pattern decision: `no_current_plan_revision_supported`
- objective decision: `blocked_not_complete`

Interpretation: the 18-root cumulative sample is still positive in raw PnL,
but it no longer clears the cumulative bounded gate. The newest root made the
recent-window and root/market positivity problems explicit, so the objective is
still blocked and no current RV600 family should be promoted.

## Third Post-Freeze Bounded Shadow Root

The next market-window-approved bounded passive root also completed cleanly and
was scored after both captured markets settled.

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260514T130107Z`
- opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T130107Z_opportunity.md`
- bounded root audit:
  `logs/particle_research/reports/rv600_shadow_bounded_20260514T130107Z_audit.md`
- refresh report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_20260514T130107Z_refresh.md`
- recorder_returncode: `0`
- tailer_returncode: `0`
- independent_spot_returncode: `0`
- checkpoint files: `2`
- checkpoint rows: `819`
- independent spot rows: `7400`
- independent spot issues: `0`
- offline v28 contexts: `817`
- offline v28 context issues: `2`
- pipeline candidate contexts: `781`
- pipeline context issues: `0`
- settled labels refreshed: `2`
- label issues: `0`

Root scoring:

- locked aggregate accepted entries: `15`
- locked aggregate PnL: `-388c`
- best root grid candidate:
  `blend_95_5_same_side_ev_step_3c_broad_70_600_ev0`
- best root grid accepted entries: `3`
- best root grid PnL: `+10c`
- best root grid matched-v28 delta: `0c`
- best root grid rejection:
  `fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best locked/frozen candidate:
  `rv600_primary_side_flip_only_broad_70_600_ev4`
- best locked/frozen accepted entries: `1`
- best locked/frozen PnL: `-20c`
- best locked/frozen matched-v28 delta: `0c`
- best locked/frozen rejection:
  `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive`

Interpretation: this third post-freeze root is valid incoming evidence and is
materially negative for the frozen candidate. It reinforces the conclusion that
the current RV600 family is not promotable.

## Nineteen-Root Cumulative Refresh

The cumulative bounded, rescue, failure-pattern, and objective audits were
refreshed after adding `rv600_next_evidence_shadow_20260514T130107Z`.

- cumulative bounded report:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- cumulative opportunity report:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md`
- decision: `cumulative_bounded_scored_with_entries`
- roots: `19`
- settled markets: `36`
- candidate rows: `14964`
- locked RV600 entries: `207`
- locked RV600 PnL: `+4524c`
- best cumulative grid candidate:
  `rv600_primary_max_3_entries_broad_70_600_ev6`
- best cumulative accepted entries: `59`
- best cumulative distinct markets: `21`
- best cumulative PnL: `+1179c`
- best cumulative matched-v28 delta: `+583c`
- best cumulative rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive`
- market-balance decision: `market_balance_rescue_failed`
- market-balance gate-pass rows: `0`
- market-balance anchored forward PnL: `+112c`
- market-balance anchored matched-v28 delta: `-227c`
- regime-filter decision: `regime_filter_rescue_failed`
- regime-filter support rows: `0`
- regime-filter anchored forward PnL: `+489c`
- regime-filter anchored matched-v28 delta: `-227c`
- failure-pattern decision: `no_current_plan_revision_supported`
- objective decision: `blocked_not_complete`

Interpretation: after 19 bounded roots, raw cumulative PnL is still positive
but decaying. The latest-root, recent-window, root/market positivity, and
matched-v28 stability gates are all still blocking completion.

## Partial Collection Quarantine And Audit Guard

A later attempted root,
`rv600_next_evidence_shadow_20260514T134028Z`, was excluded before scoring.
It started during a valid market window but suffered a websocket/DNS reconnect
stall after only `23` book checkpoints.

- original root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260514T134028Z`
- quarantined artifact root:
  `logs/particle_research/failed_collections/rv600_next_evidence_shadow_20260514T134028Z_dns_reconnect_stalled_partial`
- captured market: `KXBTC15M-26MAY140945-45`
- checkpoint rows: `23`
- independent spot rows: `254`
- independent spot issues: `11`
- recorder_returncode: `0`
- tailer_returncode: `0`
- independent_spot_returncode: `0`
- failure evidence:
  `no close frame received or sent`, then repeated `[Errno 11001] getaddrinfo failed`

Implementation hardening:

- patched `probe_rv600_bounded_cumulative_audit.py`
- bounded root collection is no longer considered OK unless checkpoint rows are
  at least `300` and independent spot issues are `0`
- refreshed latest bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_audit_latest.md`
- refreshed cumulative bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md`
- refreshed objective audit:
  `logs/particle_research/reports/rv600_objective_state_latest.md`

Interpretation: this partial root is not evidence for or against RV600. It is a
collection-quality failure, and future audits now reject similarly thin roots
even if the subprocess return codes are `0`.

## Group-DRO Robustness Rescue

Because every current RV600 family remained blocked by root/market stability,
recent-window weakness, and concentration gates, I ran the required literature
check for plausible modeling fixes and implemented the best narrow fit as an
offline rescue audit.

Sources considered:

- Group DRO for worst-group generalization:
  `https://arxiv.org/abs/1911.08731`
- Cardinality-constrained distributionally robust portfolio optimization:
  `https://arxiv.org/abs/2112.12454`
- Cardinality-constrained mean/CVaR portfolio optimization:
  `https://arxiv.org/abs/1810.10563`
- Online lazy portfolio updates with transaction costs:
  `https://ojs.aaai.org/index.php/AAAI/article/view/8693`
- Backtest overfitting in the machine learning era:
  `https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110`

Chosen implementation:

- added `probe_rv600_group_dro_rescue.py`
- used existing RV600 grid variants only
- ranked variants with a group-DRO/minimax utility over bounded roots
- penalized lower-tail root PnL, market concentration, recent-window loss, and
  repeated-entry churn
- required anchored forward validation before any support row could count
- changed no live trading code, no live v28 logic, and no launch/restart path

Result:

- report:
  `logs/particle_research/reports/rv600_group_dro_rescue_latest.md`
- decision: `group_dro_rescue_failed`
- roots: `19`
- support rows: `0`
- anchored forward selected PnL: `+560c`
- anchored forward matched-v28 delta: `-82c`
- anchored positive-root rate: `0.50`
- anchored max single-market share: `0.307`
- anchored lower-tail root PnL: `-63.25c`
- prequential gate pass: `False`

Best group-DRO-ranked row:

- variant: `rv600_primary_max_3_entries_late_70_180_ev2`
- accounting: `position_capped`
- accepted entries: `49`
- distinct markets: `17`
- selected PnL: `+1137c`
- matched-v28 delta: `+140c`
- lower-tail root PnL: `-32.6c`
- worst root PnL: `-77c`
- positive root rate: `0.368`
- positive market rate: `0.412`
- last-window PnL: `-6c`
- rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct`

Interpretation: the group-DRO rescue confirms the current issue is not just a
ranking problem. The best robust-looking current row is still dependent on too
few positive roots/markets, loses in the recent window, and fails anchored
matched-v28 validation. This does not support a new locked RV600 candidate from
the existing sample. The valid next step remains fresh bounded shadow evidence
or a genuinely new RV600 clue that can be frozen before forward validation.

## Next Collection Spot-Quality Guard

Before the next market-window collection, I tightened the generated
next-evidence command in `probe_rv600_next_evidence_gate.py`.

Change:

- generated bounded passive collection commands now include
  `--require-independent-spot`

Reason:

- `research_particle.spot_context_merge` otherwise writes the original context
  row through when independent spot is missing or stale
- bounded audits already reject roots with independent spot issues, so the
  generated command should make the spot dependency explicit at context-merge
  time
- this is research-only command generation; it does not touch live v28 logic,
  order logic, or restart paths

Verification:

- `python -m py_compile probe_rv600_next_evidence_gate.py`
- `python probe_rv600_next_evidence_gate.py --write`
- latest gate report still blocks collection until the BTC15M window, and the
  printed command now includes `--require-independent-spot`

## Matched-Control Source Repair

A pre-collection gate refresh showed that the generated command was selecting a
stale workspace-local v28 log:

- stale source:
  `logs/live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live/execution_events.ndjson`
- last context timestamp observed from that source:
  `2026-05-13T05:52:47Z`

The currently running matched-control family is the 90-touch v28 process in the
sibling workspace:

- fresh source:
  `C:\Users\organ\Desktop\kalshi 90 +v28\logs\v28_90_touch_bad_fair_band_veto_size2_live\execution_events.ndjson`
- latest gate mtime:
  `2026-05-15T02:29:02Z`
- compatible tail rows in the latest gate sample:
  `120`
- compatible schemas:
  `v28_90_touch_policy_eval` and legacy `mushroom_v28`

Implementation:

- added `research_particle/v28_event_sources.py`
- changed the gate and paired collector defaults to discover schema-compatible
  v28 logs across the active sibling 90-touch workspace
- extended `research_particle/v28_context_source.py` so
  `v28_90_touch_policy_eval` rows can provide matched `current_calibrated_p_yes`
- extended `research_particle/v28_context_tailer.py` so missing 90-touch strike
  is filled from public Kalshi market metadata
- kept 90-touch spot unavailable until the independent spot merge, which is now
  required by the generated command
- changed `research_particle/paired_passive_shadow_run.py` so
  `--require-independent-spot` collections do not seed stale pre-run v28 context
  rows that cannot have timestamp-valid independent spot
- changed `probe_rv600_next_evidence_gate.py` so BTC15M market discovery includes
  the `status=open` API view; this is required because the unfiltered endpoint
  can return initialized future markets while omitting the current active market
- changed `probe_rv600_next_evidence_gate.py` so matched v28 source selection
  requires a recent mtime, not just compatible historical rows
- skipped unsupported telemetry rows instead of treating recurring
  `v28_90_touch_live_stop_active` rows as context errors

Verification:

- `python -m py_compile research_particle\v28_context_source.py research_particle\v28_context_tailer.py research_particle\v28_event_sources.py research_particle\paired_passive_shadow_run.py probe_rv600_next_evidence_gate.py`
- tailer smoke test on a 90-touch live-log sample wrote `5` context rows,
  `0` issues, and marked rows as requiring independent spot
- independent-spot merge smoke test produced valid
  `PassiveCheckpointContext` rows after spot was attached
- paired collector command construction now starts the v28 context tailer at EOF
  without `--seed-last-contexts` when `--require-independent-spot` is enabled
- a 30-second preflight passive run wrote `28` book checkpoints and `426`
  independent spot ticks, but `0` v28 context rows because the matched-control
  file was not emitting new context during the pre-window period; this preflight
  artifact is diagnostic only and is not counted as validation evidence
- `python probe_rv600_next_evidence_gate.py --write` now selects the fresh
  90-touch live event source, checks its mtime age, and blocks collection unless
  the active BTC15M market window and matched-control freshness are both valid

## Still Required Before Goal Completion

The RV600 goal is not complete yet. Any future locked RV600 candidate still
needs forward shadow validation on incoming markets:

- at least `100` accepted entries
- at least `40` distinct markets
- at least `10` calendar days
- at least two weekend sessions
- positive selected PnL after fees/fills
- selected PnL at least `20%` above matched v28/current control
- average PnL per entry >= `10c`
- average PnL per market positive
- added entries positive after fees
- root/market block positivity >= `60%`
- recent last-20 accepted entries positive
- no single market contributes more than `25%` of total PnL
- fill-adjusted/no-fill-penalty PnL remains positive
- native/continuous RV600 forward evidence is present; sparse sidecar snapshots
  alone cannot complete the goal

Until those forward gates pass, RV600 remains a research-only shadow candidate.

## Offline Matched-Control Collection Path

The 90-touch v28 live process is alive, but its policy-eval telemetry is sparse:
ordinary heartbeats do not emit a continuous `current_calibrated_p_yes` stream.
Using that live event stream as the only matched-control source can produce
zero-context RV600 evidence even while passive orderbook and independent spot
capture are healthy.

Implementation:

- added `--offline-v28-control` to
  `research_particle/paired_passive_shadow_run.py`
- in this mode the collector skips the live v28 context tailer and, after
  passive collection ends, runs `probe_rv600_native_offline_v28_contexts.py`
- the matched v28/current control is rebuilt causally from:
  passive checkpoints, independent Coinbase BTC spot ticks, public Coinbase
  warmup candles, and public Kalshi market metadata
- `context_path_for_pipeline` points to `offline_v28_contexts.ndjson`
- `tailer_returncode=null` is valid only when
  `matched_control_mode=offline_v28_public_btc_replay`
- patched `probe_rv600_bounded_cumulative_audit.py` and
  `probe_rv600_shadow_smoke_audit.py` to accept that offline-mode invariant
- patched JSON loading in those audits to tolerate UTF-8 BOMs in generated
  PowerShell JSON artifacts
- changed `probe_rv600_next_evidence_gate.py` so the generated bounded
  collection command uses `--offline-v28-control` and treats live 90-touch
  telemetry as optional diagnostic evidence rather than a collection blocker

Verification:

- `python -m py_compile research_particle\paired_passive_shadow_run.py probe_rv600_next_evidence_gate.py probe_rv600_bounded_cumulative_audit.py probe_rv600_shadow_smoke_audit.py`
- 2-second read-only smoke:
  `rv600_offline_control_patch_smoke_20260515T030949Z`
- smoke result: `2` checkpoints, `25` independent spot ticks, `2` offline v28
  contexts, `0` offline context issues, `tailer_returncode=null`

Interpretation: this is not a model change or live bot change. It is a
research-side matched-control construction that preserves timestamp causality
and avoids dependency on sparse live policy rows.

## New Bounded Shadow Root: 2026-05-15T024708Z

Ran a bounded read-only collection using the offline v28 control path:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T024708Z`
- markets:
  `KXBTC15M-26MAY142300-00`, `KXBTC15M-26MAY142315-15`
- checkpoint rows: `821`
- independent spot rows: `9133`
- independent spot issues: `0`
- offline v28 contexts written: `818`
- offline v28 issues: `3` post-settlement checkpoints
- pipeline contexts written: `764`
- pipeline context issues: `0`
- labels written: `2`

Per-root opportunity result:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T024708Z/rv600_native_forward_opportunity.json`
- best grid:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best grid accepted entries: `3`
- best grid selected PnL: `+102c`
- best grid matched-v28 delta: `+213c`
- best grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct`
- best locked selected PnL: `+20c`
- best locked rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: the root is positive but too small and fully concentrated in a
single market. It is useful fresh evidence and pipeline validation, not a
passing RV600 candidate.

## Cumulative State After 20 Bounded Roots

Refreshed reports:

- `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.json`
- `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.json`
- `logs/particle_research/reports/rv600_shadow_bounded_audit_latest.json`
- `logs/particle_research/reports/rv600_objective_state_latest.json`

Cumulative bounded state:

- roots: `20`
- candidate rows: `15728`
- settled markets: `38`
- locked total entries: `209`
- locked total PnL: `+4544c`
- best grid variant:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best grid accepted entries: `93`
- best grid distinct markets: `31`
- best grid selected PnL: `+1263c`
- best grid matched-v28 delta: `+676c`
- best grid rejection:
  `positive_markets_below_60pct`

Objective state remains:

- decision: `blocked_not_complete`
- objective_complete: `False`

## 23-Root Forward Update After RV600NEAR001 Freeze

Collected one new read-only bounded shadow root after freezing `RV600NEAR001`.
This did not place orders, restart the bot, or modify live v28 logic.

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T045448Z`
- dataset:
  `rv600_next_evidence_shadow_20260515T045448Z`
- recorder_returncode: `0`
- matched_control_mode: `offline_v28_public_btc_replay`
- checkpoint rows: `830`
- independent spot rows: `3837`
- independent spot issues: `0`
- offline v28 contexts written: `828`
- offline v28 issues: `2` post-settlement checkpoints
- pipeline contexts written: `751`
- pipeline context issues: `0`
- labels written after delayed refresh: `2`
- label refresh issues: `0`

Root scoring:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T045448Z/rv600_native_forward_opportunity.json`
- total candidate rows: `751`
- settled markets: `2`
- best grid:
  `rv600_primary_max_3_entries_base_70_420_ev6`
- best grid selected PnL: `+201c`
- best grid rejection:
  `fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

`RV600NEAR001` on this root:

- variant:
  `rv600_primary_side_flip_only_broad_70_600_ev4`
- accepted entries: `3`
- distinct markets: `2`
- selected PnL: `+39c`
- average PnL per entry: `13.0c`
- matched-v28 delta: `0c`
- positive market rate: `0.50`
- max single-market PnL share: `1.0769`
- rejection:
  `fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Interpretation: the first forward-only frozen near-miss root was positive after
fees and cleared the average-entry hurdle by itself, but it was too small,
concentrated, and did not beat matched v28. It is useful future evidence, not a
promotion signal.

## Cumulative State After 23 Bounded Roots

Refreshed reports:

- `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.json`
- `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.json`
- `logs/particle_research/reports/rv600_bounded_current_grid_latest.json`
- `logs/particle_research/reports/rv600_objective_state_latest.json`

Cumulative bounded state:

- roots: `23`
- candidate rows: `18121`
- settled markets: `44`
- locked total entries: `228`
- locked total PnL: `+4760c`
- best grid variant:
  `rv600_primary_max_3_entries_base_70_420_ev6`
- best grid selected PnL: `+1358c`
- best grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`

`RV600NEAR001` cumulative diagnostic state:

- accepted entries: `44`
- distinct markets: `30`
- selected PnL: `+378c`
- matched-v28 delta: `+218c`
- average PnL per entry: `8.5909c`
- positive root rate: `0.6522`
- positive market rate: `0.6000`
- max single-market PnL share: `0.1614`
- last-window PnL: `+39c`
- rejection:
  `avg_entry_below_10c`

Interpretation: the frozen near-miss improved slightly after the first
forward-only root, but it still fails the average-entry gate. Keep collecting
only as pre-registered forward evidence; do not tune or promote it.

## 23-Root Rescue Refresh

After adding the new settled root, I refreshed the rescue/stability audits so
the objective report would not mix 22-root and 23-root evidence.

Meta-label rescue:

- split_count: `18`
- train_gate_selection_count: `0`
- test_selected_pnl_cents: `+13c`
- preliminary_gate_pass: `False`

Probability-calibration rescue:

- split_count: `18`
- train_gate_selection_count: `0`
- test_selected_pnl_cents: `+813c`
- preliminary_gate_pass: `False`

Conformal-abstention rescue:

- split_count: `18`
- train_gate_selection_count: `0`
- test_selected_pnl_cents: `0c`
- preliminary_gate_pass: `False`

Online-expert rescue:

- split_count: `18`
- train_gate_selection_count: `0`
- test_selected_pnl_cents: `+321c`
- preliminary_gate_pass: `False`

Market-balance rescue:

- decision: `market_balance_rescue_failed`
- root_count: `23`
- gate_pass_rows: `0`
- positive_concentration_ok_rows: `1394`
- positive_both_balance_ok_rows: `25`
- prequential_gate_pass: `False`
- prequential_test_pnl_cents: `+298c`

Regime-filter rescue:

- decision: `regime_filter_rescue_failed`
- roots: `23`
- summary_row_count: `130284`
- support_row_count: `0`
- prequential_gate_pass: `False`
- prequential_test_pnl_cents: `+568c`

Group-DRO rescue:

- decision: `group_dro_rescue_failed`
- roots: `23`
- support_row_count: `0`
- prequential_gate_pass: `False`
- prequential_test_pnl_cents: `+782c`

PBO stability audit:

- decision: `pbo_rejects_current_grid`
- root_count: `23`
- candidate_count: `5451`
- valid_split_count: `512`
- pbo: `0.546875`
- positive_split_rate: `0.8223`
- mean_selected_test_pnl_cents: `+252.918c`

Stability-selection rescue:

- decision: `stability_selection_rescue_failed`
- root_count: `23`
- candidate_count: `1260`
- locked_selection_count: `140`
- full_support_count: `0`
- selected-test PnL: `+15197c`
- selected-test matched-v28 delta: `+4823c`
- selected-test average PnL per entry: `3.2334c`
- rejection:
  `no_full_sample_support_row;selection_rate_below_threshold;avg_test_entry_below_10c`

Objective state remains:

- decision: `blocked_not_complete`
- objective_complete: `False`
- added/current blockers include:
  `pbo_stability_rejected` and `stability_selection_rescue_failed`

## Frozen Forward Diagnostic Near-Miss: RV600NEAR001

Because no current grid candidate is promotable, I froze one simple near-miss
for future-only diagnostic evidence rather than continuing to tune the existing
sample.

Plan artifacts:

- JSON:
  `logs/particle_research/locked_oos_plans/rv600_breadth_nearmiss_RV600NEAR001_locked_plan.json`
- markdown:
  `logs/particle_research/locked_oos_plans/rv600_breadth_nearmiss_RV600NEAR001_locked_plan.md`

Frozen candidate:

- plan_id: `RV600NEAR001`
- generated_utc: `2026-05-15T04:53:47Z`
- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- probability mode: `rv600_primary`
- window: `T-600s` to `T-70s`
- min EV: `4c`
- entry rule: `side_flip_only`
- max entries per market: `2`
- primary accounting: `position_capped`
- evidence counted only after: `2026-05-15T04:53:47Z`

Reason for freezing this one:

- it is already in the locked candidate set
- it uses only the three base gates: timing, EV threshold, entry rule
- `one_per_side_per_market` and `position_capped` are equivalent on the
  current sample, so the repeated-entry result is not replay inflation
- current diagnostic sample clears root breadth, market breadth, concentration,
  recency, and matched-v28 delta
- current diagnostic sample fails only average PnL per entry:
  `8.2683c` versus required `10c`

This is not promotion and not live trading. It is only a pre-registered
future-shadow diagnostic. If future-only evidence does not clear the average
entry, matched-v28, breadth, and concentration gates, reject the near-miss
instead of lowering gates.

## Stale Rescue Refresh And Stability Selection: 2026-05-15

The older meta-label, probability-calibration, conformal-abstention, and
online-expert reports were still pointed at
`rv600_native_forward_opportunity_latest.json`. I refreshed each one explicitly
against the current 22-root cumulative opportunity report:

- input:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.json`
- roots: `22`

Refreshed rescue results:

- meta-label:
  `logs/particle_research/reports/rv600_meta_label_rescue_latest.json`
  - preliminary_gate_pass: `False`
  - split_count: `17`
  - train_gate_selection_count: `0`
  - test_selected_pnl_cents: `+13c`
  - rejection:
    `no_train_gate_selection;avg_test_entry_below_10c;does_not_beat_matched_v28;positive_test_splits_below_60pct`
- probability calibration:
  `logs/particle_research/reports/rv600_probability_calibration_rescue_latest.json`
  - preliminary_gate_pass: `False`
  - split_count: `17`
  - train_gate_selection_count: `0`
  - test_selected_pnl_cents: `+813c`
  - rejection:
    `no_train_gate_selection;positive_test_splits_below_60pct`
- conformal abstention:
  `logs/particle_research/reports/rv600_conformal_abstention_rescue_latest.json`
  - preliminary_gate_pass: `False`
  - split_count: `17`
  - train_gate_selection_count: `0`
  - test_selected_pnl_cents: `0c`
  - rejection:
    `no_train_gate_selection;fewer_than_25_test_entries;nonpositive_test_pnl;does_not_beat_matched_v28;positive_test_splits_below_60pct`
- online expert:
  `logs/particle_research/reports/rv600_online_expert_rescue_latest.json`
  - preliminary_gate_pass: `False`
  - split_count: `17`
  - train_gate_selection_count: `0`
  - test_selected_pnl_cents: `+385c`
  - rejection:
    `no_train_gate_selection;avg_test_entry_below_10c;does_not_beat_matched_v28;positive_test_splits_below_60pct`

Interpretation: some diagnostic slices still produce positive PnL, but all four
rescues have zero train-gate selections. They are not promotable under the
spec's anti-overfitting gates.

I also generated a reproducible 22-root bounded-current grid artifact:

- report:
  `logs/particle_research/reports/rv600_bounded_current_grid_latest.json`
- markdown:
  `logs/particle_research/reports/rv600_bounded_current_grid_latest.md`
- root_count: `22`
- variant_count: `3948`
- summary_rows: `11844`
- run_rows_omitted: `260568`
- best_by_total_pnl:
  `rv600_primary_max_3_entries_broad_70_600_ev6`
- best_locked_candidate: none
- locked_candidates: `0`

Because the current blocker is not raw PnL but unstable selection and near-miss
breadth/average-entry tradeoffs, I added a stability-selection rescue probe.

Sources considered:

- Stability Selection:
  `https://arxiv.org/abs/0809.2932`
- Hansen's Superior Predictive Ability test:
  `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=264569`
- Deflated Sharpe Ratio:
  `https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2460551_code87814.pdf?abstractid=2460551&mirid=1`
- Probability of Backtest Overfitting / CSCV:
  `https://www.carmamaths.org/resources/jon/backtest2.pdf`
- Empirical Bernstein lower-confidence bounds:
  `https://arxiv.org/abs/0907.3740`

Chosen implementation:

- added `probe_rv600_stability_selection_rescue.py`
- evaluates existing RV600 grid candidates only
- excludes `all_entries` rows and candidates with more than three active gates
- samples balanced root splits with fixed seed `600`
- uses scaled entry floors for half-sample train gates
- counts only split selections that pass the prior-root train gate
- requires a full-sample support row and a stable selection rate before any
  support can be claimed

Result:

- report:
  `logs/particle_research/reports/rv600_stability_selection_rescue_latest.json`
- markdown:
  `logs/particle_research/reports/rv600_stability_selection_rescue_latest.md`
- decision: `stability_selection_rescue_failed`
- root_count: `22`
- candidate_count: `1260`
- split_count: `512`
- locked_selection_count: `161`
- full_support_count: `0`
- top gate-passing train selection:
  `rv600_primary_max_3_entries_broad_70_600_ev0|position_capped`
- top selection rate: `0.0625`
- required selection rate: `0.60`
- selected-test PnL: `+26894c`
- selected-test matched-v28 delta: `+3805c`
- selected-test average PnL per entry: `4.7718c`
- rejection:
  `no_full_sample_support_row;selection_rate_below_threshold;does_not_beat_matched_v28_by_20pct;avg_test_entry_below_10c`

Best full-sample diagnostic row:

- variant:
  `rv600_primary_same_side_ev_step_3c_broad_70_600_ev4`
- accounting_mode: `one_per_side_per_market`
- accepted_entries: `40`
- selected_pnl_cents: `+378c`
- matched_v28_delta_cents: `+218c`
- avg_pnl_per_entry_cents: `9.45c`
- positive_root_rate: `0.6364`
- positive_market_rate: `0.6071`
- max_single_market_pnl_share: `0.2540`
- rejection:
  `avg_entry_below_10c;single_market_share_above_25pct`

Interpretation: the current RV600 grid contains real positive near-misses, but
no simple candidate is both full-sample gate-passing and stable under root
subsampling. The closest diagnostic row misses the average-entry gate and is
barely above the concentration cap. The current plan remains research-only and
not deployable.

Objective audit integration:

- patched `probe_rv600_objective_state_audit.py`
- added `stability_selection_rescue_failed` to `blocked_by`
- refreshed `logs/particle_research/reports/rv600_objective_state_latest.json`

Objective state remains:

- decision: `blocked_not_complete`
- objective_complete: `False`

Interpretation: cumulative PnL is positive, but the anti-overfitting gates are
still doing their job. The best row does not yet have enough positive market
coverage, and the completion requirement still needs at least `40` distinct
markets plus stability/concentration gates. Do not call the goal complete.

## New Bounded Shadow Root: 2026-05-15T032104Z

Ran another bounded read-only collection because the next-evidence gate was
ready and the cumulative sample had only `38` distinct settled markets.

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T032104Z`
- markets:
  `KXBTC15M-26MAY142330-30`, `KXBTC15M-26MAY142345-45`
- checkpoint rows: `855`
- independent spot rows: `5314`
- independent spot issues: `0`
- offline v28 contexts written: `853`
- offline v28 issues: `2` post-settlement checkpoints
- pipeline contexts written: `853`
- pipeline context issues: `0`
- labels written: `2`

Per-root opportunity result:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T032104Z/rv600_native_forward_opportunity.json`
- best grid:
  `rv600_primary_max_3_entries_broad_70_600_ev2`
- best grid accepted entries: `6`
- best grid selected PnL: `+218c`
- best grid matched-v28 delta: `0c`
- best grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- locked total entries: `4`
- locked total PnL: `+180c`

Interpretation: the root was positive, but still too small, concentrated, and
not better than the matched v28 control by the required margin.

## Cumulative State After 21 Bounded Roots

Refreshed reports:

- `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.json`
- `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.json`
- `logs/particle_research/reports/rv600_shadow_bounded_audit_latest.json`
- `logs/particle_research/reports/rv600_objective_state_latest.json`

Cumulative bounded state:

- roots: `21`
- candidate rows: `16581`
- settled markets: `40`
- locked total entries: `213`
- locked total PnL: `+4724c`
- best grid variant:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best grid accepted entries: `99`
- best grid distinct markets: `33`
- best grid selected PnL: `+1478c`
- best grid matched-v28 delta: `+676c`
- best grid rejection:
  `positive_markets_below_60pct`

Objective state remains:

- decision: `blocked_not_complete`
- objective_complete: `False`

Interpretation: the sample now reaches the `40` settled-market minimum, and
the best grid is close to the `100` accepted-entry threshold with positive PnL.
It still fails the positive-market gate, and only `33` markets are represented
inside the best row. The goal remains active and incomplete.

## New Bounded Shadow Root: 2026-05-15T034820Z

Ran one additional bounded read-only collection because the sample had reached
the settled-market minimum but still needed more stability evidence.

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T034820Z`
- markets:
  `KXBTC15M-26MAY150000-00`, `KXBTC15M-26MAY150015-15`
- checkpoint rows: `820`
- independent spot rows: `4784`
- independent spot issues: `0`
- offline v28 contexts written: `818`
- offline v28 issues: `2` post-settlement checkpoints
- pipeline contexts written: `789`
- pipeline context issues: `0`
- labels written: `2`

Per-root opportunity result:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T034820Z/rv600_native_forward_opportunity.json`
- best grid:
  `blend_80_20_max_3_entries_broad_70_600_ev4`
- best grid accepted entries: below completion threshold
- best grid selected PnL: `+168c`
- best grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best RV600-primary:
  `rv600_primary_max_3_entries_broad_70_600_ev4`
- best RV600-primary selected PnL: `+132c`
- locked total entries: `2`
- locked total PnL: `+27c`

Interpretation: this was another positive root, but not a passing root. It was
small, concentrated, and the best row did not beat the matched v28 control by
the required margin.

## Cumulative State After 22 Bounded Roots

Refreshed reports:

- `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.json`
- `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.json`
- `logs/particle_research/reports/rv600_shadow_bounded_audit_latest.json`
- `logs/particle_research/reports/rv600_objective_state_latest.json`

Cumulative bounded state:

- roots: `22`
- candidate rows: `17370`
- settled markets: `42`
- locked total entries: `215`
- locked total PnL: `+4751c`
- best grid variant:
  `rv600_primary_max_3_entries_broad_70_600_ev6`
- best grid selected PnL: `+1427c`
- best grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`

Objective state remains:

- decision: `blocked_not_complete`
- objective_complete: `False`

Interpretation: increasing the fresh sample changed the best threshold from
`ev0` to `ev6`, but did not clear the stability gates. The core blocker is now
not raw PnL or sample size; it is root/market breadth. The current RV600 family
remains research-only and not deployable.

## Rescue Audits Refreshed On 22 Roots

Because the 22-root cumulative report still failed root/market breadth, I
refreshed the stability/rescue audits against the current sample rather than
continuing from stale 19-root conclusions.

Market-balance rescue:

- report:
  `logs/particle_research/reports/rv600_market_balance_rescue_latest.json`
- decision: `market_balance_rescue_failed`
- root_count: `22`
- gate_pass_rows: `0`
- positive_concentration_ok_rows: `1446`
- positive_both_balance_ok_rows: `32`
- prequential_gate_pass: `False`
- prequential_test_pnl_cents: `+368c`

Regime-filter rescue:

- report:
  `logs/particle_research/reports/rv600_regime_filter_rescue_latest.json`
- decision: `regime_filter_rescue_failed`
- roots: `22`
- summary_row_count: `130284`
- support_row_count: `0`
- prequential_gate_pass: `False`
- prequential_test_pnl_cents: `+638c`

Group-DRO rescue:

- report:
  `logs/particle_research/reports/rv600_group_dro_rescue_latest.json`
- decision: `group_dro_rescue_failed`
- roots: `22`
- support_row_count: `0`
- prequential_gate_pass: `False`
- prequential_test_pnl_cents: `+714c`

Interpretation: the newer data improves several anchored/prequential PnL
numbers, but none of the rescue paths produces a support row or prequential gate
pass. More of the exact same current RV600 family is unlikely to become a
complete strategy without a new frozen candidate definition that directly
improves market/root breadth.

## PBO Stability Audit

Because the post-22-root blocker is specifically "positive PnL but unstable
root/market breadth," I ran the required literature check for a better
anti-overfitting diagnostic.

Sources considered:

- Probability of Backtest Overfitting / CSCV:
  `https://core.ac.uk/display/24041876`
- Deflated Sharpe Ratio:
  `https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2460551_code87814.pdf?abstractid=2460551&mirid=1`
- Group DRO for worst-group generalization:
  `https://arxiv.org/abs/1911.08731`
- Conformal Risk Control:
  `https://arxiv.org/abs/2208.02814`

Chosen implementation:

- added `probe_rv600_pbo_stability_audit.py`
- uses the current settled bounded roots discovered by the cumulative pipeline
- evaluates existing RV600 grid candidates only
- samples balanced root splits with a fixed seed
- selects the in-sample best candidate on the train roots
- ranks that selected candidate by out-of-sample PnL on the held-out roots
- estimates PBO as the fraction of splits where the selected in-sample winner
  ranks at or below median out of sample

Result:

- report:
  `logs/particle_research/reports/rv600_pbo_stability_audit_latest.json`
- decision: `pbo_rejects_current_grid`
- root_count: `22`
- candidate_count: `5246`
- valid_split_count: `512`
- pbo: `0.4785`
- positive_split_rate: `0.8496`
- mean_selected_test_pnl_cents: `+282.2715c`

Interpretation: selected candidates often remain positive out of sample, but
the in-sample winner fails the stricter split-rank stability requirement. This
supports the existing conclusion: the current grid has real positive slices, but
not a stable enough deployable RV600-derived strategy.

Objective audit integration:

- patched `probe_rv600_objective_state_audit.py`
- added `pbo_stability_rejected` to `blocked_by`
- refreshed `logs/particle_research/reports/rv600_objective_state_latest.json`

Objective state remains:

- decision: `blocked_not_complete`
- objective_complete: `False`
