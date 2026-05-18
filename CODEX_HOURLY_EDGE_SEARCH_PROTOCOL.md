# Codex Hourly Edge Search Protocol

This protocol is for the hourly research automation. Codex is the researcher. Truffle is optional infrastructure to evaluate, benchmark, or stress-test; Truffle should not be treated as the primary source of ideas.

## Mission

Search for real, evidence-backed edge in the Kalshi BTC 15 minute bot using the local repo, logs, fills, research lab, and historical datasets as source of truth.

Each activation should attempt 1-3 new research ideas, equations, filters, thresholds, or supervisory policies and backtest them. The goal is not novelty for its own sake; the goal is loss mitigation, higher expected value, better false-exit control, and robust evidence that could eventually improve the bot.

## Current 48-Hour Focus

For the 2026-04-25 to 2026-04-27 run window, make the automation more forward-looking:

- Start each run with the latest live dwell state, execution telemetry, bot log, morning summary, strategy memory, idea index, ledger tail, and this automation's memory.
- Treat `liquidity_dwell_p05_q065_hold` as the current best practical candidate and the live reference strategy, not as an invitation to retune live behavior.
- Keep the validated production exit baseline as `hold_to_settlement`. `deep_panic_10_confirm1` is shadow/watchlist only. Routine 60c/70c/78c stops are rejected unless fresh evidence overturns that conclusion.
- Run a short forward-evidence preflight every hour: live dwell arms, rejections, approvals, fills, settlements, reject quality, fillability, depth, slippage, loop gaps, account refresh failures, WS/DNS errors, and whether live paths match backtest assumptions.
- The preflight is monitoring, not the research deliverable. Every run must also produce at least one substantive edge-research result unless there is an active live-bot safety issue.
- Substantive research means one of: a genuinely new decision-time equation/feature/policy family, a materially new fixed-parameter validation or stress test of a promising candidate, or a concrete execution/fillability hypothesis investigated with data.
- If fresh forward data is thin, do not end with "no useful new sample." Switch to the next research track from the backlog.
- Rotate tracks across runs: fresh math families, fixed-parameter BTC spot EV or conformal-neighbor validation, dwell reject opportunity and fillability, execution quality/slippage/IOC depth, side-specific no-trade or entry timing alternatives, and Truffle shadow-only consistency checks.
- Every run should explicitly say whether it produced new forward evidence, replay/backtest evidence, execution evidence, or no useful live sample, and should name the hypothesis tested beyond the preflight.

## Hard Guardrails

- Do not change live entry logic.
- Do not change live exit logic.
- Do not restart or stop the live bot.
- Do not alter live run scripts or production config unless explicitly asked by the user in the active thread.
- Research-only code, reports, notebooks, caches, and scripts are allowed.
- Prefer writing outputs under `logs/edge_research`, `stats`, or clearly named research files.
- If a hypothesis only works by hindsight-leaking settlement/result information, reject it or mark it as invalid.

## Per-Run Workflow

1. Read the latest research outputs, recent bot logs, current trade/fill data, strategy memory, and the idea ledger at `logs/edge_research/edge_idea_ledger.jsonl`.
2. Identify what has already failed so the run does not repeat old weak variants, equivalent equations, or renamed versions of the same idea.
3. Check whether new live dwell telemetry or settlements exist since the previous run and score them as a concise preflight.
4. Choose at least one substantive research task beyond the preflight: a new decision-time idea, a distinct fixed-parameter validation, or a concrete execution/fillability hypothesis. Use math, market microstructure, path geometry, execution-state features, RSI/MACD-style indicators, drawdown/rebound features, or regime concepts when useful.
5. Implement the tests in research-only code or extend existing research scripts.
6. Backtest against the largest relevant local dataset available, especially the 600+ trade `live_90_70` / research-lab data when applicable, but label data concentration clearly.
7. Compare against meaningful baselines: actual recorded PnL, no-stop hold-to-settlement, current live dwell hold-to-settlement behavior, current Truffle-supervised behavior if available, and simple deterministic rules.
8. Look for robustness: holdout, walk-forward, parameter sensitivity, false-exit count, missed true-loser count, dataset/day concentration, scale sensitivity, fillability, and whether the edge survives transaction/friction assumptions.
9. Append every invented/tested idea to `logs/edge_research/edge_idea_ledger.jsonl` with status, equation, dataset, result summary, and report path.
10. Write a concise report with the tested ideas, equations, results, failures, and the next most promising branch.

## Non-Repetition Rule

- Do not rerun an idea already present in `edge_idea_ledger.jsonl`, `edge_idea_index.json`, or `strategy_memory.json`.
- Treat cosmetic renames as repeats if the equation, feature family, or decision rule is materially the same.
- If the built-in catalog is exhausted, extend the research-only catalog with genuinely new feature families instead of resetting tested IDs.
- If a prior idea almost worked, test a clearly distinct follow-up and explicitly state how it differs from the original.

## What Counts As Promising

- Improves PnL versus actual recorded behavior without simply increasing catastrophic settlement losses.
- Catches true settlement losers earlier while avoiding mass exits of eventual winners.
- Reduces clustered-loss drawdowns or identifies reliable bad-market regimes.
- Shows stability across nearby thresholds rather than a single lucky parameter.
- Uses only features available at decision time.

## What To Be Skeptical Of

- Rules that look good only because they know settlement result.
- Thresholds that only work at one exact value.
- Truffle or LLM calls that are inconsistent, slow, or mainly restate obvious drawdown information.
- Strategies that improve no-stop hold but are much worse than actual recorded PnL.
- Apparent edge from stale data, failed fills, or unrealistic exit assumptions.

## Truffle Role

Use Truffle only when useful as:

- A candidate live supervisor to benchmark.
- A consistency/reliability target.
- A prompt/output-contract test subject.
- A source of labels to compare against deterministic features.

Do not rely on Truffle to invent the strategies. Codex should do the strategy design and decide what to test.
