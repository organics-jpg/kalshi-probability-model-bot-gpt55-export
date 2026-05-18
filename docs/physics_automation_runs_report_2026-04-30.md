# Physics Automation Runs Report - 2026-04-30

Scope: every persisted run/report artifact I found for `fringe-researcher`, `new-physics-builder`, and `hard-physics-validator` under `C:\Users\organ\.codex\automations`, plus the current memory/result logs for those automations. All three automations were paused when reviewed. No live trading behavior was changed by these runs.

## Executive Findings

1. v22 remains the recommended probability baseline. v21 remains useful as a conservative fallback/reference. No run produced enough evidence to change live model code, thresholds, or trading behavior.
2. The most promising predictive lift is not a mystical physics formula. It is the combination of market microstructure with v22: market-mid/logit pooling and stricter quote freshness. These showed the clearest proper-score and edge-zone improvements, but still need native resolved labels and common-key validation before promotion.
3. The strongest "new physics" family is an abstention/buffer layer, not a probability transform. Geodesic risk, recursive residual gauntlets, volatility thermocline, time-mirror curvature, conformal alarms, Hawkes jump echo, and tail fragility repeatedly found risky high-p_side slices. They should be tested as model_buffer/skip diagnostics only.
4. Direct probability transforms mostly failed. Probability temperature maps, settlement gravity, probability shrink/flatten, raw Fisher-Rao temperature, possibility conservation, transport lag, and pressure caps tended to overfit, worsen log loss, skip winners, or create fake certainty.
5. Base phi/base pi ideas are not dead, but the current versions are not good. Base phi residual-sequence screens had small positive slices, but base 2 controls were comparable and base pi was often harmful. Treat irrational-base work as low priority until a larger native-label panel exists.
6. The repeated blocker is data. `live_mushroom_v21_size2` had growing feature/book data but 0 resolved trade-label rows through the latest reviewed runs. Most positive results came from the reused 350-row `live_liquidity_dwell_size2` panel, which is heavily mined and too small for promotion.

## Breakthrough Watchlist

These are the ideas with real predictive potential, ordered by practical strength.

| Rank | Idea | Evidence | Current verdict |
|---:|---|---|---|
| 1 | Market-mid logit pool with v22 | On actual-strike rows, logit pooling with Kalshi midpoint improved clustered bootstrap metrics strongly. In raw edge>=2c rows, v22 had n=104, accuracy 0.721, Brier 0.229, log loss 0.744; logit pool lambda 0.5 had n=60, accuracy 0.817, Brier 0.147, log loss 0.462. Bootstrap deltas versus v22 were strongly positive for Brier/log loss/AUC/calibration. | Highest priority retest. Not a v22 replacement yet. Needs native labels, spread/depth bins, and common-key quote freshness controls. |
| 2 | Quote freshness <=500 ms | Paired common-key retest versus <=1000 ms improved accuracy, Brier, log loss, AUC, p80 Brier, and p85 Brier. Latest paired result: 786 common keys, delta accuracy +0.0038, Brier -0.00413, log loss -0.01197, AUC +0.00686, p85 Brier -0.00588. Non-overlap also improved. | Very practical data-quality candidate. Keep <=1000 ms baseline for now; retest <=500 ms once native labels exist. |
| 3 | Probability geodesic hard abstention | On the 350-row panel, p>=0.80 edge rows improved from 34/4, +166c to 33/2, +355c; skipped rows were 1/2, -189c. p>=0.85 win rate improved but PnL slipped from +190c to +168c. | Promising buffer/skip diagnostic. No probability shrink. Retest fresh. |
| 4 | Recursive residual gauntlet | Combines geodesic, time-mirror, and gauge residuals. Adaptive walk-forward improved p>=0.80 log loss 0.266 -> 0.222 and PnL +166c -> +229c; p>=0.85 log loss 0.229 -> 0.207 and PnL +190c -> +193c. Best fixed p85 rule kept 21/21 winners, +430c. | Tempting but mined. Pre-register on fresh native labels only. |
| 5 | Volatility thermocline | q90 walk-forward kept p>=0.80 rows at 27/2, +393c versus base 34/4, +166c; p>=0.85 kept 23/1, +396c versus base +190c. | Strong aggregate signal, but one day fold inverted. Freeze and retest. |
| 6 | Conformal martingale / tail fragility / Hawkes composite | Conformal strict holdout clear rows were 12/1, +244c while flagged rows were 5/2, -257c. Tail fragility flagged all 3 holdout strict losses in one test. Hawkes q75 hard veto was the best Hawkes form. | Good candidate composite. Too sparse individually. |
| 7 | First-passage cushion risk | Reflection first-passage improved path-risk calibration versus terminal-loss anchor, especially as a touch/cushion-collapse measure. | Use as path-risk/exit-risk diagnostic, not terminal P(S_T > K). |
| 8 | Hybrid sigma gate | Synthetic robust-vol hybrid slightly improved all-row Brier/log loss/calibration, but p80/p85 Brier and log loss degraded slightly. | Research queue only; must survive actual-strike/non-overlap with no tail damage. |

## Most Important Pattern

The useful candidates all say roughly the same thing:

High p_side is trustworthy only when physical probability, market microstructure, transport geometry, short-horizon volatility heat, and recent path direction agree. When the model is confident but the quote tape, geometry, or path process is stressed, the safer use is to demand more edge or abstain.

That is a coherent research direction. It points to a future "reliability layer" around v22, not a replacement of v22.

## Fringe Researcher Runs

Persistent status: mostly diagnostics. No live-use candidate. The best direction is a composite alarm: conformal martingale + tail fragility + Hawkes/Fisher-Rao shift.

| Run / artifact | Idea | Result and verdict |
|---|---|---|
| 2026-04-29/30 Fisher-Rao edge temperature | Fisher-Rao distance as edge-zone temperature | Modify, do not promote. Reject unconstrained heating; keep cooling/buffer idea for native-label retest. |
| 04:54 Fisher-Rao transport alarm | FR veto/temperature | Rejected. Hurt holdout probability quality and conservative PnL. Coverage was only 35/350 rows. |
| 05:56 stale probability acceleration | Stale market / physical probability acceleration | Rejected standalone. Strict sample only 4 rows and no PnL improvement. Modify toward directional adverse acceleration. |
| 07:10 tail fragility score | Adverse curvature / TFS | Promising diagnostic. Top TFS concentrated losses; holdout threshold flagged all 3 strict losses, but sample tiny and soft penalty did not validate. |
| 08:04 entropy production alarm | Irreversibility/adverse entropy | Modify only. Standalone entropy alarm not validated; combine with tail fragility. |
| 09:57 tail fragility x entropy | Product/overlap alarm | Modify only. Too sparse on actual decisions. Use as calibration covariate on a bigger exact-horizon panel. |
| 11:03 horizon transport geometry | Nearest/interpolated transport | Rejected as direct model change. All-row calibration was interesting, p>=0.85 edge zone safer under default v22. |
| 12:04 conformal martingale alarm | E-process/CUSUM on residuals | One of the best fringe signals. Holdout clear rows 12/1, +244c after vetoing 7 rows that went 5/2, -257c. Diagnostic only due tiny strict set. |
| 13:09 Hawkes jump echo | Adverse jump self-excitation | Modify only. Synthetic strict rows separated risk, but soft penalty was not robust. |
| 14:09 multifractal cascade sigma | Horizon sigma multiplier | Mixed. Actual strict holdout improved from 17/3, -13c to 20/2, +137c, but synthetic exact-horizon evidence was not strong. Keep cascade score, reject direct sigma correction. |
| 15:05 Fisher-Rao residual shift temperature | FR shift as strict-zone reliability | Modify. High-shift strict holdout was negative; +2c buffer too weak. Retest hard veto/stronger temperature fresh. |
| 16:02 Fisher-Rao residual shift | FR distance edge detector | Modify. Useful separation signal, but tested buffer hurt holdout PnL. |
| 17:07 Hawkes jump echo rerun | q75 hard veto variants | Keep/modify. q75 hard veto was the only promising form; q90/share/net/temp variants weaker. |
| 18:06 probability temperature small harness | Edge-zone temperature map | Rejected. Train split had no strict losses, causing overfit sharpening. |
| 18:10 probability temperature 350-row harness | Guarded temperature map | Rejected again. Did not beat v22 strict holdout economics; naive map overfit high-confidence cells. |
| 19:11 path-integral least-action | Least-action route to strike | Rejected as veto. q75 flagged rows were winners while clear rows held losses; soft cooling chose lambda 0. Keep only as confirmation score. |
| 2026-04-30 Fisher-Rao transport report | FR transport stability | Modify, not promote. Use D_FR as reliability/buffer diagnostic, not nearest-horizon bridge. |
| FR-008 probability acceleration v0 | Directionless acceleration | Rejected standalone. Top-quartile PAS flagged winners; modify to directional adverse acceleration with official labels only. |
| Memory-only FR-004/FR-009 notes | Multifractal cascade and tail fragility on first-fill outcomes | Both are research candidates only. Current samples are traded-only and too small, but TFS/adverse arrow correlations with loss are interesting. |

## New Physics Builder Runs

Persistent status: inventiveness is high, but the useful ideas are abstention diagnostics. Probability transforms are mostly rejected.

| Run / artifact | Idea | Result and verdict |
|---|---|---|
| 04:55 phi cushion fragility | Base-phi digit motif | Rejected. No valid out-of-sample red-flag rule fired. |
| 05:58 probability pressure residual | Probability pressure gradient | Rejected as predictive filter; non-monotonic bins and no valid day-forward rule. |
| 06:55 pressure-temperature cap | Temperature cap from pressure residual | Rejected. Brier/log loss slightly worsened and edge win rate unchanged. |
| 08:00 settlement gravity field | Final-window gravity/sharpening | Rejected. Gravity60 worsened p>=0.85 log loss 0.07598 -> 0.13490 and created overconfidence. |
| 08:57 possibility conservation law | No-boost ATM contradiction shrink | Modify only. Small in-sample p80 lift failed walk-forward and p85 worsened. |
| 10:01 probability geodesic curvature | Probability shrink via geodesic risk | Reject shrink, keep risk flag. Fixed risk separated fail rates but probability shrink hurt edge metrics. |
| 11:03 base phi/base pi edge screen | Radial phase of boundary distance | Rejected. Base phi harmed p80 and only trivial p85 lift; base pi harmful or inactive. |
| 12:05 probability geodesic buffer | Hard abstention by geodesic risk | Best new-physics single diagnostic. p80 PnL +166c -> +355c; p85 win rate improved but PnL fell slightly. Retest fresh. |
| 13:01 nomenal latent field | Hidden field flattening/abstention | Rejected. Skipped profitable rows; p80 PnL +166c -> -193c kept, p85 +190c -> -27c kept. Flattening harmed log loss. |
| 14:02 time-mirror curvature | Side-signed curvature risk | Modify only. p85 kept 15/0, +262c versus base +190c, but p80 PnL fell from +166c to +146c. |
| 15:05 boundary relativity residual gauge | Volatility-gauge disagreement | Rejected. Residual gauge kept too few rows and underperformed geodesic in p80/p85. |
| 16:07 recursive residual gauntlet | Geodesic + time mirror + gauge residual | Strong but mined. Adaptive p80 and p85 improved log loss and PnL; fixed p85 geo_or_tm_q90 kept 21/21 winners. Pre-register only. |
| 17:09 irrational phase lattice residuals | Residual phases in bases phi/pi/2/e/10 | Modify/pre-register only. Base phi improved small slices, but base 2 was comparable and base pi was harmful. |
| 18:08 least-action boundary tunneling | Kinetic/action barrier score | Modify/pre-register only. Aggregate p85 improved, but 2026-04-27 fold failed and geodesic/recursive was stronger. |
| 19:09 volatility thermocline | Short-scale volatility heat | Strong aggregate but fold-unstable. p80 kept +393c, p85 kept +396c, but one fold skipped profitable rows. Freeze for fresh labels. |
| 20:09 hyperbolic rapidity overhang | Non-Euclidean certainty overhang | Reject as candidate but keep audit. p80 looked strong, p85 PnL underperformed stronger diagnostics. |
| 21:12 Kelvin pressure-curl | Quote-motion circulation | Rejected. Log loss improved but retained conservative PnL fell in p80 and p85. |
| 22:11 possibility conservation flux v2 | Entropy/collapse flux | Rejected. Skipped winners and worsened retained p80/p85 log loss/PnL. |
| 23:12 probability transport lag | Rapidity overhang plus boundary transport | Rejected. Skipped two profitable high-cushion rows and worsened retained metrics. |
| Base phase compact artifact | Fold summary for base screens | Supports rejection of radial phase screen; several selected folds were harmful. |
| Result log / memory updates | Ledger and queue | Confirms strongest future direction: fresh-label residual gauntlet, geodesic buffer, thermocline, time-mirror only inside geodesic-kept rows. |

## Hard Physics Validator Runs

Persistent status: validation discipline is good. The strongest practical candidates are quote freshness and market-mid/logit pooling. Most established math candidates are diagnostic-only or rejected as replacements.

| Run / artifact | Idea | Result and verdict |
|---|---|---|
| 02:57 volatility gauge digital boundary | Close RV, Parkinson, Garman-Klass, bipower, MAD, blends | Keep v22 blend. Some gauges helped all-row or near-boundary, but none cleared tail/all-row rules. |
| 03:54 actual-strike settlement-average | Future average sigma transform | Rejected. Candidate delta: accuracy -0.0011, Brier +0.00083, log loss +0.01273, AUC -0.00073. |
| 03:55 actual-strike settlement-average rerun | Same | Same rejection. Duplicate confirmation. |
| 04:56 digital CDF isotonic | Monotonicity repair across strikes | Rejected. Raw v22 had 0 CDF inversions, so isotonic made no meaningful change. |
| 05:55 Brownian bridge first-passage | Treat no-touch survival as terminal probability | Rejected as terminal P. Delta accuracy -0.1058, Brier +0.0597, log loss +0.1497. Keep path-risk math separately. |
| 07:06 Student-t transport | Student-t residual CDF | Modify/retest only. Tiny Brier/log/AUC/calibration gains; tail not degraded, but actual non-overlap only 23 rows. |
| 08:02 Student-t shrinkage | Low-weight Student-t prior | Modify/retest only. Even smaller gains; later robustness audit rejected as replacement. |
| 09:08 hour seasonality | Prior-day hourly sigma multipliers | Rejected. Core improvements 0 and strict-tail degradation. |
| 09:57 jump mixture CDF | Rolling jump-diffusion prior | Modify/retest only. Tiny gains, no tail degradation, insufficient evidence. |
| 10:58 transport horizon coverage | Sparse v22 vs dense 1-15 transport | Keep current sparse v22. Dense-minute variant worsened AUC and p85/edge-zone proper scores. |
| 12:04 actual-strike vol gauge | Actual Kalshi strike labels | Keep v22 terminal. Baseline remained best by all-row Brier/log loss. |
| 12:07 actual-strike vol gauge rerun | v21/reference comparison | Reject v21/static as v22 replacement under two-metric/tail gates. |
| 12:08 actual-strike vol gauge final | Close_rv_600/reference screen | Keep v22 terminal. No vol-gauge replacement cleared rules. |
| 13:00 walk-forward temperature calibration | Day-level temperature shrink | Keep v22 terminal. Did not clear two-improvement rule without tail/all-row concerns. |
| 14:04 beta-smoothed transport | Beta-binomial smoothing toward anchor | Modify/retest only. Microscopic gains, not promotion-grade. |
| 15:07 quote staleness | Strict quote-age gates | Modify/retest only. <=250 ms looked good in raw labelled panel but coverage/selection risk remained. |
| 16:05 paired quote staleness | Common-key retest | Modify/retest only. <=500 ms improved paired common-key metrics without tail Brier degradation. |
| 17:09 Student-t robustness audit | Robustness by horizon/month/non-overlap | Rejected as v22 replacement. Tiny gains failed robustness; 30m/60m and p80/p85 mixed degradation. |
| 18:09 first-passage cushion risk | Reflection first-passage path risk | Keep as path-risk diagnostic only. Improved path-risk Brier/log/ece versus terminal-loss anchor, not a terminal probability. |
| 19:06 non-overlap validation audit | Anti-duplicate acceptance screen | Keep v22 validation baseline. Pooled winners did not remain dominant under non-overlap/bootstrap. |
| 20:11 market-mid logit pool | v22 plus Kalshi midpoint | Strongest practical candidate. Modify/retest, not v22 replacement. Needs native labels, spread/depth bins, and fee-aware edge checks. |
| 21:21 robust volatility memory run | Median/robust blend synthetic panel | Modify only. Median blend improved all-row, but p80/p85 cushion ranking favored current v22/bipower. Motivated hybrid. |
| 22:11 hybrid sigma gate | Median near boundary, v22/bipower in tails | Research queue only. All-row Brier/log/cal improved slightly, but p80/p85 Brier/log degraded slightly. |
| 23:09 paired quote staleness rerun | Latest common-key quote freshness | Best staleness result: <=500 ms improved common-key and non-overlap metrics. Retest once native labels exist; keep <=1000 ms baseline for now. |

## Rejected Ideas Worth Remembering

- Settlement gravity failed because it sharpened confidence exactly where cushion calibration was already delicate.
- Probability conservation and transport-lag formulas repeatedly skipped profitable high-cushion rows.
- Direct geodesic, temperature, and nomenal probability transforms made log loss worse. The same raw signals are more plausible as abstention or buffer features.
- Brownian bridge/no-touch survival is not terminal Kalshi payout probability. It belongs in cushion-collapse/path-risk monitoring.
- Base pi is currently a negative control. Base phi is only worth revisiting as a residual-sequence transform, not boundary-distance radial phase.

## Recommended Next Test Plan

1. Build the native resolved-label panel first. Until `live_mushroom_v21_size2` has settlement labels and metadata, do not promote anything from the reused 350-row panel.
2. Run a frozen candidate gauntlet with no retuning:
   - raw v22, v21 fallback, anchor
   - quote_age <=1000 ms, <=500 ms, <=250 ms common-key
   - market-mid logit pool lambdas 0.25, 0.5, 0.75
   - geodesic q90 hard abstention
   - recursive residual gauntlet fixed rules
   - volatility thermocline q90
   - conformal + tail-fragility + Hawkes composite
3. Score by all rows, non-overlap first-per-market, cluster bootstrap, by day/month, by offset, p_side>=0.80, p_side>=0.85, and edge>=2c/3c.
4. Promotion rule: require at least two core metric improvements, no p80/p85 Brier/log degradation, no edge-zone PnL degradation, and stability across more than one day.
5. Use accepted physics-style signals as `model_buffer_cents` or abstention flags before trying probability changes. The current evidence says "make v22 more selective," not "replace v22."

## Bottom Line

The potential breakthrough is a reliability layer around v22:

`enter only when v22 edge is strong AND quote freshness/microstructure is clean AND geometry/path/volatility diagnostics do not flag cushion fragility.`

That layer has more evidence than any single new probability formula. The best immediate research target is to validate a combined `v22 + market-mid/quote-freshness + geodesic/thermocline/conformal fragility` gate on fresh native labels.
