# v28 Successor Live P&L Improvement Goal Plan

## Current Success Definition

Success means a frozen v28 successor policy proves, on post-policy-hash live incoming BTC 15m boundary-market rows, that it makes positive fee-aware one-contract net P&L and beats regular v28 on the same paired opportunities. It must also preserve source quality, fillability, broad enough coverage, boundary accuracy, and robustness across multiple live close windows, so the result is not just one lucky market, one slice, or retrospective tuning.

## Current Full Goal

```text
Goal: Follow docs/v28_successor_live_pnl_improvement_goal_plan.md to use the completed research-only live-P&L lab to find, freeze, and forward-prove a genuinely profitable v28 successor policy for BTC 15m boundary markets. Keep live trading, order logic, thresholds, secrets, state, sizing, and bot processes untouched unless separately approved. Treat v002 as unproven and currently not profitable unless future post-hash live evidence reverses that.

Use only frozen pre-resolution, post-policy-hash, labeled live incoming market rows as primary evidence. Diagnostic/replay/pre-policy rows may generate hypotheses, reject bad ideas, or guide feature design, but they cannot prove profitability. Compare every candidate on the same paired opportunities against regular v28, successor-FV-only, book-only, and always-skip baselines using fee-aware one-contract economics.

Use incoming live-market behavior as the main teacher: what the policy entered, skipped, avoided, lost, won, and misunderstood. Retire or replace any candidate that fails early live-forward P&L or merely matches regular v28. Search the codebase for existing strong candidates first; when blocked by a modeling, statistical, execution, or engineering problem, search the internet/arXiv for 3-5 plausible solutions, compare them, and implement the simplest robust option.

Completion requires a frozen inspectable candidate with at least 5 finalized live close windows and at least 75 post-hash labeled primary opportunities, positive net P&L after fees, positive delta versus regular v28, acceptable drawdown/loss clustering, broad enough market coverage, clean source-quality and fillability evidence, and proof the result is not driven by one market, one slice, or retroactive tuning. Advance nothing toward controlled live use unless those forward P&L, coverage, boundary, source, and risk gates all pass.
```

## One-Line Goal

Build a live-incoming-market P&L improvement layer on top of the v28 successor FV engine that materially improves fee-adjusted net P&L versus regular v28 across BTC 15m boundary markets, while keeping live order logic untouched until a separate explicit approval is given.

## Core Thesis

The v28 successor FV work proved that a simple, inspectable calibration layer can beat regular v28 on probability quality. That is useful, but it is not enough. A tiny improvement in Brier score does not automatically produce a meaningful trading edge after Kalshi fees, spread, fill risk, stale books, recross noise, drawdown clusters, and bad timing.

The next objective is therefore not "make the probability prettier." It is:

```text
Use the better FV engine as a decision ingredient, then learn when to enter, skip, exit, resize, or stand down so the strategy makes materially more money than regular v28 on live incoming markets.
```

The most important data source is not the old replay table. The best friend of this project is the strategy's own behavior against incoming live markets:

- what it would have entered,
- what regular v28 would have entered,
- what it skipped,
- what the book was showing at the decision moment,
- what the market did after that,
- how fees changed the economics,
- where wins and losses clustered,
- which regimes broke the model,
- and which simple rules would have avoided the bad states without throwing away all coverage.

Historical replay is allowed for design, debugging, and hypothesis generation. It is not the final judge. The final judge is pre-registered, pre-resolution, live-incoming market evidence.

## Evidence Hierarchy

When evidence conflicts, use this order of trust:

1. Frozen live-incoming policy rows captured before resolution, labeled after settlement, with complete book/FV/source fields.
2. Frozen live-incoming FV rows that can be converted into policy rows without adding post-resolution information.
3. Recent live logs that were recorded before resolution but were not originally shaped for the P&L policy.
4. Historical replay and reconstructed rows.
5. Synthetic fixtures and demos.

Rows from levels `3` through `5` can help generate ideas, debug code, and reject obviously bad policies. They cannot prove a P&L policy is ready. A candidate that wins on replay but fails live-incoming rows is not a winner. A candidate that wins live-incoming rows but fails replay should be inspected carefully, but the live-incoming evidence is the better teacher if source quality is clean.

## Clock, Settlement, And Market Definition Discipline

BTC 15m boundary markets are timing-sensitive. A few seconds of timestamp drift can turn a causal row into accidental hindsight.

Every live-forward artifact must preserve:

- UTC decision timestamp,
- local wall-clock timestamp if available,
- market close timestamp,
- row freeze timestamp,
- settlement label timestamp,
- data-source timestamps for BTC, book, and market metadata,
- clock age fields for BTC, book, and policy decision,
- and whether the row was frozen strictly before market close.

The market definition must be captured before scoring:

- market ticker,
- strike,
- YES/NO semantics,
- close time,
- settlement source,
- settlement price,
- status lifecycle,
- and any relevant market rule text or source reference available from the exchange API.

If market metadata, close time, strike, or settlement semantics are missing or inconsistent, the row is unscorable for primary P&L. Do not infer settlement rules after seeing the outcome.

All reports should explicitly distinguish:

- decision-time BTC/reference price,
- book-implied price,
- settlement price,
- final-average proxy where used,
- and any exchange-reported settlement value.

## Non-Negotiable Guardrails

1. Keep live bot/order logic untouched unless the user explicitly approves a controlled live change.
2. Do not place trades as part of this research goal.
3. Do not stop or restart the live bot unless the user explicitly asks for operational intervention.
4. Do not mutate live thresholds, secrets, state files, order sizing, or execution behavior.
5. Keep all P&L-layer work in research scripts, shadow registries, reports, and docs until separately approved.
6. Every row used for live-forward validation must be frozen before market close.
7. Settlement labels must be joined only after resolution.
8. Any row reconstructed after the fact is diagnostic only.
9. Any candidate that wins by cherry-picking tiny coverage is not a solution.
10. Any candidate that wins gross P&L but loses after fees is not a solution.
11. Any candidate that improves average return but creates unacceptable drawdown or loss clustering is not a solution.
12. Any candidate whose result disappears under source-quality, fillability, or freshness filters is not a solution.
13. Do not count position sizing as a P&L improvement during research. Score unit-normalized one-contract economics first; size can be a later risk-control layer only after the unit edge is real.
14. Do not tune a policy on a settled live-forward market and then count that same market as proof for the tuned policy.
15. Controlled live use requires a separate written approval, rollback plan, monitoring plan, and max-loss limit. This plan alone does not authorize live orders.
16. If exchange/account data is needed for fee or fill reconciliation, use read-only access only unless the user explicitly approves otherwise.
17. Research recorders must be sidecars. They should not share mutable live state, block the live bot, consume order credentials, or degrade live bot CPU/network reliability.

## Why This Goal Is Different From The FV Goal

The completed FV goal was about calibrated probability:

- `P(settlement > strike)`,
- fair YES/NO cents,
- boundary accuracy,
- v28 component preservation,
- causal rows,
- simple challengers,
- source-quality gates.

This new goal is about trading decisions:

- should we enter,
- which side should we prefer,
- what minimum edge is real after fees,
- when is the book too stale,
- when is the boundary too unstable,
- when should we avoid a market entirely,
- when should we use the successor FV instead of regular v28,
- when should we hold,
- when should we exit,
- and how much coverage can we preserve while improving net P&L materially.

The probability engine remains a guardrail and input. Net P&L becomes the primary target.

## Baselines

Every experiment must compare against these baselines on identical live-forward markets and timestamps.

All comparisons must use a paired opportunity ledger. For each opportunity, the ledger should hold the regular v28 baseline, successor FV-only baseline, candidate policy decision, book state, settlement label, and fee/fill assumptions on the same market, side, strike, and decision timestamp. If a row cannot be paired, it belongs in a diagnostic table, not the primary P&L leaderboard.

### Baseline A: Regular v28

This is the main benchmark. It answers:

```text
What would the existing v28 logic have believed and done at this exact decision moment?
```

Required fields:

- market ticker,
- decision timestamp,
- market close timestamp,
- side,
- strike,
- ask cents,
- bid/ask/top book where available,
- v28 YES probability,
- v28 NO probability,
- v28 fair YES cents,
- v28 fair NO cents,
- v28 side fair cents,
- v28 side edge after fees,
- v28 entry decision under the reference shadow rule,
- settlement label,
- fee-adjusted realized P&L.

### Baseline B: v28 Successor FV Only

This is the probability upgrade without new trade policy. It answers:

```text
If we only replace regular v28 fair value with the successor FV, does P&L improve?
```

This baseline prevents us from confusing a policy improvement with a pure FV improvement.

### Baseline C: Book-Only Naive Rules

Examples:

- book implied probability,
- simple mid/ask threshold,
- no-trade if spread too wide,
- no-trade if book stale.

These are sanity checks. A clever model that cannot beat simple book-aware heuristics is probably not clever enough.

### Baseline D: Always-Skip

Always-skip has zero P&L and zero drawdown. It is a useful reference because a strategy that makes tiny positive expected value with ugly risk may not be worth operating.

## Candidate Policy Shape

Start simple and inspectable. The first real P&L layer should be easy to explain in English.

A candidate policy may include:

- entry threshold,
- skip filters,
- dynamic edge threshold,
- side selection,
- time-to-close gating,
- boundary-distance gating,
- book freshness gating,
- spread gating,
- fillability gating,
- recross hazard gating,
- adverse path memory gating,
- book/FV disagreement gating,
- volatility-regime gating,
- exit or hold-to-settlement policy,
- partial profit lock or loss avoidance rule,
- size recommendation for later controlled testing.

The first versions should be rule-based, monotonic, or small regularized surfaces. Avoid opaque models until the simple families are exhausted.

## Primary Live-Forward Validation Loop

Live incoming markets are the main teacher. The research loop should continuously ask:

```text
What did regular v28 want to do?
What did the successor FV want to do?
What did the candidate P&L policy want to do?
What actually happened?
Was the miss caused by probability, timing, book quality, fees, fillability, volatility, recross, or path behavior?
What is the simplest rule that would have improved this without overfitting?
```

For every open BTC 15m boundary market, capture pre-resolution rows at repeated decision checkpoints:

- early window,
- mid window,
- late-but-not-final window,
- final few minutes where allowed for shadow scoring,
- all available strikes where reasonable,
- YES and NO side views,
- book state,
- v28 state,
- successor FV state,
- candidate policy decision,
- skip reason if skipped,
- hypothetical entry/exit decision if entered,
- frozen candidate version.

Use a predeclared sampling cadence. Do not change the capture cadence inside a market because it looks favorable or scary. If adaptive extra captures are added for diagnostics, mark them separately and do not let them dominate the primary proof.

After settlement, join labels and score the candidate policy.

The core report should show:

- live markets observed,
- markets eligible,
- markets skipped,
- markets entered in shadow,
- entry count,
- skip count by reason,
- fillability assumptions,
- gross P&L,
- fees,
- net P&L,
- expected EV,
- realized EV error,
- net cents per contract,
- net cents per market,
- win rate,
- average win,
- average loss,
- largest loss,
- max drawdown,
- loss streaks,
- P&L by time-to-close,
- P&L by distance-to-strike,
- P&L by recross hazard,
- P&L by volatility regime,
- P&L by book freshness,
- P&L by spread,
- P&L by v28/successor disagreement,
- and comparison to regular v28 on the same rows.

## Live Capture Health And SLA

The live-forward system must report not only what it captured, but also what it missed.

For every 15m close window, report:

- expected BTC boundary markets,
- discovered markets,
- captured markets,
- missed markets,
- reason for miss,
- first capture timestamp,
- last pre-close capture timestamp,
- number of checkpoints per market,
- BTC feed freshness distribution,
- book freshness distribution,
- source errors,
- API/rate-limit errors,
- recorder process status,
- and whether capture quality was good enough for primary scoring.

Silent missing data is dangerous because it can look like a profitable skip filter. Missed markets must stay in the denominator as unscorable or missed, not disappear.

Research sidecars should have lightweight health checks:

- process liveness,
- write freshness,
- latest captured market close,
- latest artifact timestamp,
- row count growth,
- parse error count,
- and disk-space sanity.

If the recorder falls behind, primary P&L claims pause until the gap is explained.

## Success Criteria

A policy is successful only if it clears all of these.

### Material P&L Improvement

Target one or more of:

- at least `+30%` fee-adjusted net P&L versus regular v28,
- at least `+50%` fee-adjusted net P&L versus regular v28 for a high-confidence candidate,
- at least `+X` net cents per contract improvement, with `X` set after baseline refresh,
- at least `+Y` net cents per market improvement, with `Y` set after baseline refresh,
- positive lower-confidence-bound EV after fees.

Raw gross P&L does not count. All primary metrics must be fee-adjusted.

Percentage improvement is not meaningful by itself when regular v28 is near flat or negative. A policy must also show an absolute improvement:

- positive net P&L after fees,
- positive net cents per contract,
- positive net cents per observed market or eligible market,
- and positive market-level lower-confidence-bound EV after fees.

Use market-level confidence intervals or bootstrap summaries. Row-level confidence can be misleading because many rows from the same market are correlated. Reports should show both row-weighted and market-equal metrics.

Research P&L is unit-normalized. Do not claim material improvement by multiplying size. Sizing can reduce risk or improve capital use later, but it cannot rescue a weak one-contract edge.

### Live-Forward Evidence

Use a staged evidence ladder. Do not make the first milestone so large that the project burns all time collecting before it learns anything.

#### Bootstrap Evidence

Purpose:

Validate that the capture, freeze, label-join, fee math, same-row v28 comparison, and report generation all work.

Minimum:

- `10` finalized close windows, or
- `25` finalized paired market opportunities, whichever comes first.

Allowed conclusions:

- infrastructure works or does not work,
- obvious bad policies can be rejected,
- obvious missing fields can be fixed,
- first loss clusters can guide the next policy version.

Not allowed:

- no readiness claim,
- no controlled live-use recommendation,
- no claim of durable P&L edge.

#### Initial Policy Checkpoint

Purpose:

Decide whether a frozen policy is worth continuing or should be replaced quickly.

Minimum:

- `25` to `40` finalized paired market opportunities,
- at least `1` reasonably continuous live capture session,
- same-market comparison versus regular v28,
- no post-resolution recomputed rows in the decision set,
- no missing settlement labels for scored rows,
- no hidden survivorship filters.

Allowed conclusions:

- continue collecting this policy,
- retire the policy,
- make a new frozen version based on observed live failure modes.

Not allowed:

- no controlled live-use recommendation unless the result is extremely strong and the user explicitly accepts the low-sample risk.

#### Provisional Research Readiness

Purpose:

Show that a policy has a real-looking signal worth deeper forward collection.

Minimum:

- `50` to `75` finalized paired market opportunities,
- preferably at least `2` distinct live sessions,
- positive absolute and percentage fee-adjusted P&L versus regular v28,
- positive market-equal or lower-confidence-bound EV if sample size permits,
- no single-market dependence,
- source quality, capture health, and fill model checks pass.

Allowed conclusions:

- policy is a serious research candidate,
- continue toward controlled-live-test readiness,
- prioritize implementation quality and monitoring around this policy.

#### Controlled-Live-Test Readiness

Purpose:

Decide whether a separate, explicit controlled live-test decision is justified.

Minimum:

- `75` to `100` finalized paired market opportunities,
- at least `2` separate live sessions or calendar days where possible,
- stable performance after removing best `1`, `3`, and `5` markets,
- stable performance under strict freshness and fillability filters,
- drawdown acceptable versus regular v28,
- clear readiness report.

This is the practical first "done enough to decide" threshold. It is intentionally smaller than a final proof standard, but still large enough to avoid pure noise.

#### Stronger Evidence

Purpose:

Build confidence after a controlled live-test decision or before broader deployment.

Preferred:

- `150` to `250+` finalized paired market opportunities,
- multiple volatility regimes,
- multiple time-of-day regimes,
- stable performance after removing questionable fillability rows,
- stable performance across days rather than one lucky session.

### Coverage

The goal is broad live-market usefulness, not a tiny sniper. A default target is:

- `70%` to `80%` of recurring BTC 15m market opportunities observed and scored,
- or lower coverage only if the risk-adjusted P&L improvement is large enough to justify it.

Every report must show the denominator:

```text
observed live markets
eligible markets
entered markets
skipped markets
unscorable markets
```

No candidate may claim success without denominator discipline.

Separate these coverage concepts:

- observation coverage: markets successfully captured and scored,
- policy eligibility coverage: markets where the policy had enough information to decide,
- entry coverage: markets where the policy actually entered,
- exit-observation coverage: entered markets where later exit checkpoints were observed,
- label coverage: markets with settlement labels joined after close.

A narrow entry policy is allowed only if observation and eligibility coverage remain broad enough to prove the strategy is not hiding from hard markets.

### Risk

The policy must not create unacceptable account risk.

Required:

- max drawdown no worse than regular v28 unless compensated by much higher return,
- loss streaks explained by regime,
- no catastrophic late-boundary cluster,
- no dependence on rare single-market windfalls,
- no fragile edge that disappears after fees.

Risk must be measured over market chronology, not shuffled rows. A policy should report:

- chronological equity curve,
- max drawdown,
- longest loss streak,
- worst `N`-market run,
- largest one-market loss,
- market-equal return distribution,
- sensitivity to removing the best `1`, `3`, and `5` markets,
- and performance by day/session.

### Probability Safety

P&L is primary, but probability quality must not become reckless.

The candidate must not materially degrade:

- Brier score,
- log loss,
- near-boundary calibration,
- side accuracy,
- calibration bins,
- source-quality filtered rows.

If P&L improves while probability degrades, the policy must explain why. For example, it might be an execution filter rather than a probability model. That is acceptable only if the live-forward P&L evidence is strong and the risk profile is controlled.

## Policy Version Lifecycle

Every policy version must be treated like a frozen experimental object.

### Explore

Use historical replay, old live logs, and already-settled forward rows to generate ideas. Exploration may inspect outcomes, but it must mark all resulting evidence as diagnostic.

### Freeze

Before a policy can earn live-forward credit, write:

- policy id,
- policy hash,
- feature list,
- rule text,
- parameters,
- expected fee model,
- fill assumption,
- entry/exit logic,
- skip reason taxonomy,
- creation timestamp,
- allowed validation window.

### Collect

Only rows captured after the policy is frozen count toward that policy's live-forward evidence.

### Score

Score after settlement on identical rows versus regular v28 and successor FV-only.

### Iterate

If live data reveals a weakness, create a new version. Do not mutate the old policy and keep its old evidence. The new version starts with zero live-forward credit.

This lifecycle is the main anti-overfitting tool. It lets the project be clever without letting settled labels leak into proof.

## Multiple Testing And Research Debt

This project will naturally try many ideas. That creates false discoveries unless the plan keeps score of failed attempts too.

Every policy experiment should record:

- policy id,
- parent policy id if any,
- hypothesis,
- changed parameters,
- date frozen,
- allowed validation start,
- allowed validation end if predeclared,
- result,
- whether it was abandoned,
- and why.

The leaderboard must include failed and deprecated policies, not only survivors.

When many variants are tested, reports should include at least one of:

- held-forward lockbox markets untouched by tuning,
- market-level bootstrap with cautious interpretation,
- lower-confidence-bound EV,
- simple multiple-comparison warning,
- or a statement that the result is exploratory only.

Avoid "policy garden" behavior where dozens of tiny variants are created until one wins by chance. Prefer fewer, better-motivated versions tied to observed live failure modes.

## P&L Accounting Rules

The P&L scoreboard must be boring and strict.

Default assumptions:

- one-contract unit economics,
- taker-style fill at the observed available ask unless a separate maker-fill model is proven,
- Kalshi fee calculation documented in code and report,
- second fee for exits or flips,
- slippage buffer when book quality is weak,
- no fill when ask size is insufficient,
- no fill when quote/book age violates freshness limits,
- no hidden execution at prices not visible at decision time.

Required P&L views:

- gross P&L before fees,
- fees,
- net P&L after fees,
- expected EV after fees,
- realized minus expected EV,
- net cents per entry,
- net cents per eligible market,
- net cents per observed market,
- market-equal net P&L,
- row-weighted net P&L.

If live exchange reconciliation becomes available, compare shadow assumptions against read-only Kalshi-side fills, fees, and balances. Differences should update the simulator before any controlled live-use decision.

## Simulator Calibration And Fill Model Audits

The shadow simulator is part of the model. If it is wrong, the P&L result is wrong.

The simulator should be audited separately for:

- fee formula correctness,
- price rounding,
- contract count assumptions,
- YES/NO payoff math,
- visible depth requirements,
- stale-book rejection,
- fill at displayed ask or bid,
- exit fill assumptions,
- and treatment of partial or missing fills.

When possible, compare simulated fills against real read-only exchange/account records from approved historical live trades. The goal is not to trade during research, but to make sure the shadow simulator is not fantasy.

If strict freshness and relaxed freshness disagree materially, treat the candidate as not ready. This protects against backfill-compatible rows making a policy look better than native live capture would.

## Exit Logic Rules

Exit logic is allowed only as shadow research in this goal.

To score exits fairly:

- the entry decision must be frozen before entry time,
- later exit checkpoints must be observed before close,
- exit rules must be frozen before the market resolves,
- exit fills must use visible book prices and sizes,
- exit fees must be counted,
- a missing exit checkpoint means the strategy either holds or follows a predeclared fallback.

Do not score an exit using a best future price unless the rule would actually have known to exit at that time. Exit policies are especially prone to hindsight leakage, so they need their own source-quality checks.

## Candidate Discovery And Triage

Before inventing a new policy family, inspect the existing workspace for useful candidates, probes, and features. Reuse strong existing work when it fits the live-forward P&L goal.

Candidate triage should answer:

- Does this candidate target entry, skip, exit, sizing, fee realism, or risk?
- Does it have causal inputs available live?
- Does it preserve broad observation coverage?
- Does it have plausible unit edge after fees?
- Does it reduce known loss clusters?
- Can it be expressed simply enough to monitor?
- Can it be frozen and scored prospectively?

Only strong candidates should enter the live-forward policy queue. The queue should not become a zoo.

## Hypothesis Families To Explore

This is where the work should be clever.

### 1. Boundary Thermodynamics

Treat the strike boundary like an energy barrier. The system is not just "above or below strike"; it has momentum, volatility, diffusion, and a finite averaging window.

Possible features:

- normalized distance to strike,
- local volatility,
- realized-vol regime,
- time-to-close,
- recross count,
- recross hazard,
- signed path energy,
- compression or expansion of uncertainty near the final averaging window.

Possible rule:

```text
Skip or demand larger edge when the boundary state has high kinetic energy and low directional commitment.
```

### 2. Brownian Bridge And First-Passage Risk

BTC near strike before close is a bridge problem, not just a terminal-normal problem. A trade can look good at one timestamp but have high probability of recrossing before settlement.

Use:

- Brownian bridge probability of ending above strike,
- first-passage or recross hazard,
- probability mass crossing the strike multiple times,
- expected occupation time above strike,
- final-average approximation.

Potential edge:

```text
Enter only when terminal probability and path-stability probability agree.
```

### 3. Entropy Filter

When the model is uncertain and the book is uncertain, do not force a trade.

Use probability entropy:

```text
entropy = -p log(p) - (1-p) log(1-p)
```

High entropy near 50/50 plus high fees/spread is often a tax. The strategy should demand more edge when entropy is high.

Potential rule:

```text
dynamic_min_edge = base_edge + entropy_penalty + fee_penalty + spread_penalty
```

### 4. Information Disagreement Filter

The best live signal may be disagreement, not level.

Compare:

- regular v28,
- successor FV,
- book implied probability,
- recent transport,
- static boundary field,
- anchor,
- short-term drift,
- realized vol.

Useful disagreement patterns:

- book disagrees with FV but book is stale,
- book disagrees with FV and BTC just moved,
- v28 and successor disagree near boundary,
- transport and static field disagree,
- probability says edge but path memory says danger.

Potential rule:

```text
Trade only when the disagreement is explainable and points toward exploitable mispricing.
Skip when disagreement is unclassified noise.
```

### 5. Adverse Path Memory

If BTC recently moved hard against the side, the fair value may lag the path risk. Track path scars:

- max adverse move over 1m, 3m, 5m,
- distance recovered,
- time since adverse move,
- whether the market recrossed after the signal,
- whether the book caught up.

Potential rule:

```text
Raise required edge after recent adverse path movement unless recovery is confirmed.
```

### 6. Fee Gravity

Fees are like friction. Many edges that look real in probability space are not tradable after fees.

For every candidate decision:

```text
net_edge = fair_side_cents - ask_cents - expected_fee_cents - slippage_buffer
```

Potential rule:

```text
No trade unless net_edge clears a regime-specific threshold and the expected value survives a pessimistic fee/fill scenario.
```

### 7. Fillability Reality Check

Shadow P&L can lie if it assumes fills that would not happen.

Track:

- best ask size,
- spread,
- quote age,
- book age,
- orderbook update freshness,
- whether the displayed ask persisted,
- whether price moved away immediately,
- simulated taker fill,
- simulated maker fill only if queue realism exists.

Initial scoring should prefer conservative taker assumptions. Maker assumptions need separate evidence.

### 8. Regime Switching

The policy should know when the market has changed character.

Regimes:

- calm drift,
- choppy recross,
- high-vol breakout,
- stale-book quiet,
- late-boundary compression,
- book/FV disagreement,
- post-jump reprice.

Use simple regime tags first. A good policy may be a small set of regime-specific rules rather than one global threshold.

### 9. Opportunity Cost And Selectivity

Skipping is a position. A good strategy might improve P&L mostly by avoiding low-quality v28 entries.

But skip filters must be denominator-aware:

- how many markets skipped,
- how much v28 P&L avoided,
- how much winning v28 P&L was also skipped,
- whether remaining entries are enough to matter.

### 10. Controlled Exit Logic

Holding to settlement may be suboptimal. Explore:

- profit lock after favorable book move,
- loss cut after model invalidation,
- no exit unless edge flips,
- exit when recross hazard spikes,
- exit when book/FV disagreement reverses,
- time-based exit in final chaos window.

Exit logic must be scored fee-aware. A second trade has a second fee and can destroy small edges.

## Problem-Solving Research Protocol

When the work hits a technical, statistical, execution, or modeling problem, do not simply guess.

Use this protocol:

1. Define the problem precisely.
2. Search the internet and arXiv for relevant methods.
3. Find `3` to `5` plausible solutions.
4. Compare them on:
   - correctness,
   - causal validity,
   - statistical robustness,
   - implementation cost,
   - fit to this codebase,
   - runtime cost,
   - interpretability,
   - live-forward testability.
5. Choose the simplest high-quality option that advances live-forward P&L validation.
6. Implement it in the research pipeline.
7. Add tests for the key invariant.
8. Score it on frozen live-incoming rows.
9. Write down why the rejected alternatives were not chosen.

Use official or primary sources first when the issue involves exchange mechanics, APIs, fees, settlement definitions, statistical methods, or model implementation details. Use blogs and forum posts only as idea sources.

The internet/arXiv step is mandatory when the problem is genuinely open-ended or method-sensitive. It is not a license to overcomplicate small implementation details. If a local fix is obvious and low risk, implement it directly and document why no broader search was needed.

Examples of problems that should trigger research:

- better first-passage probability approximation,
- final-average settlement probability,
- confidence intervals for low-count live P&L,
- sequential testing without overfitting,
- robust drawdown estimation,
- fill probability modeling,
- fee/slippage modeling,
- online calibration,
- regime-change detection,
- dynamic thresholding under uncertainty.

Internet/arXiv research should help us choose tools. It must not override live-forward evidence.

## Data Schema Requirements

Every live-forward policy row should include:

### Identity

- row id,
- opportunity id,
- market ticker,
- strike,
- close timestamp,
- decision timestamp,
- side,
- candidate policy id,
- candidate policy hash,
- baseline id,
- policy lifecycle state: exploratory/frozen/scored/deprecated.

### Denominator And Pairing State

- market window id,
- market ticker count within the close window,
- observed opportunity flag,
- eligible opportunity flag,
- entered opportunity flag,
- skipped opportunity flag,
- unscorable opportunity flag,
- unscorable reason,
- paired regular-v28 row id,
- paired successor-FV row id,
- same-row comparison flag.

### Market State

- BTC spot/reference,
- strike distance dollars,
- `d_sigma`,
- `sigma_t_dollars`,
- time to close,
- market status,
- book timestamp,
- best bid,
- best ask,
- bid size,
- ask size,
- spread,
- book age,
- feed age.

### Probability State

- regular v28 probability,
- v28 successor probability,
- fair YES cents,
- fair NO cents,
- side fair cents,
- book-implied probability,
- v28/book disagreement,
- successor/book disagreement,
- calibration bucket,
- entropy.

### Physics And Path State

- realized vol regime,
- recent drift,
- short-horizon return,
- recross count,
- recross hazard,
- adverse path memory,
- first-passage proxy,
- Brownian bridge proxy,
- final-average proxy,
- boundary energy score.

### Decision State

- candidate action: enter/skip/exit/hold,
- side,
- target entry price,
- assumed fill type,
- visible ask size at decision,
- visible bid size at decision,
- expected fee,
- expected slippage buffer,
- net edge after fees,
- skip reason,
- exit reason,
- size recommendation for research only.

### Outcome State

Added only after resolution:

- settlement price,
- settlement side,
- YES win label,
- side win label,
- realized gross P&L,
- fees,
- realized net P&L,
- expected EV at decision,
- EV error,
- drawdown contribution,
- label available timestamp.

## Artifact Plan

Suggested durable files:

```text
docs/v28_successor_live_pnl_improvement_goal_plan.md
research_particle/v28_successor/live_pnl_policy_registry_latest.csv
research_particle/v28_successor/live_pnl_policy_registry_latest.json
research_particle/v28_successor/live_pnl_labeled_decisions_latest.csv
research_particle/v28_successor/live_pnl_labeled_decisions_latest.json
logs/edge_research/v28_successor_live_pnl_baseline_latest.json
logs/edge_research/v28_successor_live_pnl_baseline_latest.md
logs/edge_research/v28_successor_live_pnl_policy_score_latest.json
logs/edge_research/v28_successor_live_pnl_policy_score_latest.md
logs/edge_research/v28_successor_live_pnl_policy_score_latest.csv
logs/edge_research/v28_successor_live_pnl_readiness_latest.json
logs/edge_research/v28_successor_live_pnl_readiness_latest.md
logs/edge_research/v28_successor_live_pnl_research_decision_log_latest.md
logs/edge_research/v28_successor_live_pnl_source_contract_latest.json
logs/edge_research/v28_successor_live_pnl_verifier_latest.json
logs/edge_research/v28_successor_live_pnl_capture_health_latest.json
logs/edge_research/v28_successor_live_pnl_fill_model_audit_latest.json
logs/edge_research/v28_successor_live_pnl_policy_experiment_ledger_latest.csv
```

The plan file is the human source of truth. The JSON/CSV/MD reports are machine-checkable evidence.

## First Implementation Phases

### Phase 1: Baseline Refresh

Goal:

Establish the true regular-v28 live-forward P&L baseline.

Actions:

- Read existing live logs and current v28 successor forward registry.
- Identify identical decision points where regular v28 and successor FV can be compared.
- Compute fee-aware P&L under the same conservative fill assumptions.
- Report net cents per contract, net cents per market, coverage, drawdown, and slices.
- Establish the regular-v28 denominator: observed markets, scorable markets, entered markets, skipped markets, and unscorable markets.
- Set absolute `X` and `Y` materiality thresholds after seeing the refreshed baseline scale.

Completion evidence:

- baseline report exists,
- fee logic documented,
- same-row comparison available,
- denominator reported,
- materiality thresholds written to the report.

### Phase 2: Live Policy Row Capture

Goal:

Capture policy decisions for incoming markets before resolution.

Actions:

- Build a research-only live policy recorder.
- Freeze candidate policy decisions before close.
- Include regular v28, successor FV, book state, physics features, and skip reasons.
- Do not place orders.

Completion evidence:

- registry rows are pre-resolution,
- policy hash is frozen,
- settlement labels absent until after close,
- source contract blocks any bad rows,
- rows include paired v28 and successor-FV baseline ids,
- observation and eligibility denominators are preserved,
- capture-health report includes missed-market accounting.

### Phase 3: First Simple P&L Policy

Goal:

Build the first inspectable P&L policy.

Recommended first policy shape:

```text
Enter only when:
  successor_net_edge_after_fees >= dynamic_threshold
  book_age_ms <= freshness_limit
  spread <= spread_limit
  fillability_size >= minimum_size
  recross_hazard <= hazard_limit
  boundary_energy not in danger zone

Skip when:
  book/FV disagreement is unexplained
  entropy is high and net edge is marginal
  late boundary chaos is active
  adverse path memory is high
```

Completion evidence:

- policy is described in plain English,
- policy has a stable hash,
- every skip has a reason,
- every entry has fee-adjusted edge,
- tests cover no-posthoc labels and fee math,
- unit-normalized P&L is reported before any sizing analysis.

### Phase 4: Live-Forward Scoring

Goal:

Score the policy against regular v28 on incoming finalized markets.

Actions:

- Join labels after settlement.
- Score regular v28, successor FV only, and P&L policy on identical rows.
- Report P&L and safety metrics.
- Slice by regime.

Completion evidence:

- live-forward score report,
- no post-resolution decision rows,
- denominator discipline,
- P&L after fees,
- market-equal confidence interval or lower-confidence-bound EV,
- fill-model audit attached or explicitly unchanged from the current audited version.

### Phase 5: Iterative Improvement

Goal:

Use live-market failures as the roadmap.

For each loss cluster:

1. Identify the shared state.
2. Determine if the failure was probability, book, timing, fee, fillability, or path behavior.
3. Generate possible fixes.
4. If needed, search internet/arXiv for 3-5 solution families.
5. Implement the simplest robust fix.
6. Freeze it as a new policy version.
7. Score only future rows for the new version.

No retroactive credit.

Every iteration should write a short decision note:

- what live-forward failure motivated the change,
- which solution families were considered,
- whether internet/arXiv research was used,
- what was implemented,
- what was deliberately not implemented,
- and what future rows are allowed to count.

### Phase 6: Readiness Review

Goal:

Decide whether a policy is worth controlled live testing.

Readiness checklist:

- material fee-adjusted net P&L improvement,
- enough finalized live incoming markets,
- broad enough market coverage,
- source quality pass,
- capture health pass,
- fill-model audit pass,
- stable under freshness/fillability filters,
- drawdown acceptable,
- no single-market dependence,
- policy is simple enough to monitor,
- failure modes are understood,
- no live-order code touched yet,
- percentage and absolute P&L thresholds both pass,
- market-level lower-confidence-bound EV is positive,
- result survives removing best markets and questionable fillability rows.

## Required Reports

### Daily Live P&L Report

Must answer:

- Did the policy beat regular v28 today?
- Was the improvement from better entries, better skips, or exits?
- How much of the result was fees?
- What was the worst loss cluster?
- What did incoming live data teach us?
- What should the next policy version change?

### Candidate Policy Card

For each policy version:

- policy id,
- policy hash,
- plain-English rule,
- features used,
- live-forward rows,
- live-forward markets,
- net P&L,
- v28 baseline net P&L,
- delta vs v28,
- coverage,
- drawdown,
- win/loss distribution,
- confidence interval or lower-confidence-bound EV,
- observation/eligibility/entry coverage,
- known weakness,
- next action.

### Failure Autopsy

For major loss clusters:

- market tickers,
- timestamps,
- state before entry,
- probability values,
- book state,
- physics state,
- decision reason,
- outcome,
- likely cause,
- proposed fix,
- whether internet/arXiv research was used,
- whether the fix is simple enough.

## How To Think While Working

Use live data as a collaborator. The incoming markets are not just test rows; they are telling us where the edge is and where the model is hallucinating.

Be clever, but keep the cleverness pinned down:

- Use probability theory to understand uncertainty.
- Use theoretical physics analogies to find useful state variables.
- Use Brownian motion, first-passage, entropy, and energy-barrier thinking as hypothesis generators.
- Use live-forward P&L to decide whether those ideas are real.
- Prefer a simple rule that survives future markets over a beautiful model that wins old data.

The mindset:

```text
Live incoming market behavior is the teacher.
Probability theory is the language.
Physics is the metaphor engine.
P&L after fees is the scoreboard.
Source quality is the referee.
Drawdown is the survival test.
```

## Anti-Patterns

Do not:

- optimize only Brier/log loss and assume P&L will follow,
- trust retrospective replay more than live-forward rows,
- hide denominator shrinkage,
- use broad P&L without fees,
- accept low-count wins,
- let one huge market define success,
- add opaque complexity before simple policies are exhausted,
- treat stale or unfillable book prices as real fills,
- tune on a settled market and then count that same market as proof,
- claim success from percentage lift when absolute net P&L is tiny,
- claim success from bigger size instead of better one-contract unit economics,
- mix multiple policy hashes under one candidate id in the primary leaderboard,
- change live order behavior while still in research mode.

## Compact Goal For Codex

```text
Goal: Build a research-only live-incoming-market P&L improvement layer on top of the v28 successor FV engine. Keep live order logic untouched unless explicitly approved. Use regular v28 as the baseline and validate primarily on BTC 15m boundary markets captured before resolution as they arrive live. Use past replay only for research, debugging, and initial screening. Start with a small bootstrap milestone of at least 10 finalized close windows or 25 finalized paired market opportunities to prove the live-forward P&L lab works, then scale toward controlled-live-test readiness at 75-100 paired opportunities. Develop simple inspectable entry/skip/exit policies that materially improve both percentage and absolute fee-adjusted one-contract net P&L versus regular v28 while preserving broad observation coverage, fillability, calibration, source quality, and drawdown control. Treat the strategy's performance against incoming live markets as the primary guide for improving P&L. Freeze every policy version before it earns evidence, compare on paired same-row opportunities, and never count retroactive rows. When blocked by a modeling, statistical, execution, or engineering problem, search the internet and arXiv for 3-5 plausible solutions, compare them, and implement the simplest high-quality option that best advances live-forward P&L validation.
```

## Completion Definition

Use two completion levels so the first goal is achievable quickly without pretending the strategy is proven forever.

### Level 1: Bootstrap Goal Complete

This is the recommended first completion target.

Level 1 is complete when the workspace has:

1. a reproducible research-only live policy capture pipeline,
2. at least one frozen inspectable policy version,
3. frozen pre-resolution policy rows for incoming live markets,
4. post-resolution labels joined after settlement,
5. fee-aware same-row comparison against regular v28 and successor FV-only,
6. at least `10` finalized close windows or `25` finalized paired market opportunities,
7. denominator reporting for observed, eligible, entered, skipped, missed, and unscorable markets,
8. source-quality verification,
9. capture-health evidence proving missed markets are accounted for,
10. a fill-model audit or explicit current fill-model assumption report,
11. tests for causality, fee math, policy hash freezing, and no-retroactive-credit rules,
12. an experiment ledger that includes failed and deprecated policies,
13. and a bootstrap report saying whether the first policy should continue, be retired, or be replaced.

Level 1 does not mean the policy is ready for live orders. It means the live-forward P&L lab works and has produced enough real incoming-market evidence to guide the next iteration.

### Level 2: Controlled-Live-Test Readiness

Level 2 is complete only when the workspace has everything from Level 1 plus:

1. at least one simple inspectable policy with material net P&L improvement,
2. `75` to `100` finalized paired market opportunities,
3. preferably at least `2` separate live sessions or calendar days,
4. broad enough live-market observation and eligibility coverage,
5. positive absolute and percentage one-contract P&L improvement after fees,
6. positive market-level confidence or lower-confidence-bound evidence,
7. acceptable drawdown and loss clustering,
8. proof that results are not driven by one or two best markets,
9. stable performance under strict freshness and fillability filters,
10. a frozen policy version whose validation rows occur after the policy hash was created,
11. and a readiness report explaining whether controlled live use is justified.

Level 2 still does not authorize live orders by itself. It means the research evidence is strong enough for the user to make a separate controlled-live-test decision.

### Level 3: Strong Evidence

Level 3 is a later confidence target, not the first milestone.

Level 3 means:

- `150` to `250+` finalized paired market opportunities,
- multiple regimes,
- stable market-equal P&L,
- stable drawdown,
- robust fillability,
- and continued advantage versus regular v28 after several policy iterations.

Until a separate explicit live-test approval exists, every level remains research-only.
