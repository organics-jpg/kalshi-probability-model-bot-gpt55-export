# Carr/Lopez de Prado Implementation Audit

Generated: 2026-05-14

## Verdict

Our current OU work does not match the Carr/Lopez de Prado paper exactly.

The closer file is `probe_ou_exit_mesh_strategy.py`, because it studies profit-taking and stop-loss exits for positions that already existed. Even that file is an adapted Kalshi/log-accounting probe, not a paper-exact reproduction.

The profitable backtest and forward shadow in `ou_mispricing_strategy_lab.py` are a new Carr-inspired strategy hypothesis. They should not be described as proving that the paper's method is profitable on our data.

## Paper-Exact Requirements

A paper-exact implementation should:

- Start from an already-open opportunity or position.
- Model the price or mark-to-market PnL process associated with that opportunity.
- Fit the discrete OU input parameters on that process.
- Create a mesh of profit-taking and stop-loss pairs.
- Simulate forward paths from the observed initial condition.
- Stop each path at profit-taking, stop-loss, or max holding period.
- Score each node by Sharpe ratio, meaning mean outcome divided by standard deviation.
- Select the PT/SL node from simulation output, not by historical grid backtest.

## What We Actually Have

| Artifact | Status | Why |
|---|---|---|
| `probe_ou_exit_mesh_strategy.py` | Carr-inspired, not exact | It does exit-corridor testing and OU simulation, but it uses Kalshi bid reconstruction, fees, slippage, API-reconciled historical trades, bootstrapped initial PnLs, and an extra historical-grid walk-forward comparator. |
| `ou_mispricing_strategy_lab.py` | New strategy, not exact | It creates Brownian fair value, defines Kalshi probability mispricing `z = market_mid_yes - fair_yes`, adds entry gates, simulates exits on mispricing, and then scores historical PnL. The paper explicitly does not solve entry selection. |
| Forward shadow | Research-only, not exact | It shadows `ou_mispricing_optimal_stopping`, writes decisions only, and does not place orders. It is useful for forward evidence on the new hypothesis, not for proving paper fidelity. |

## Main Mismatches

1. Entry logic: the paper says the position already exists. `ou_mispricing_strategy_lab.py` adds entry selection through fair-value edge, z alignment, spread, time-window, and simulation gates.

2. State variable: the paper models price or opportunity MtM PnL. `ou_mispricing_strategy_lab.py` models Kalshi probability mispricing relative to a Brownian fair value.

3. Objective function: the paper's central selection criterion is Sharpe ratio. `ou_mispricing_strategy_lab.py` ranks first by expected net cents, then Sharpe-like score, then loss probability.

4. Backtest-free claim: the paper avoids choosing the trading rule by historical simulation. `probe_ou_exit_mesh_strategy.py` includes a retrospective real-path grid and a historical-grid walk-forward comparator, and `ou_mispricing_strategy_lab.py` reports historical-tape backtest PnL.

5. Initial condition: the paper's simulation starts from the observed initial condition for the opportunity. `probe_ou_exit_mesh_strategy.py` samples initial PnL values from prior observed path starts.

6. Practical frictions: both local probes add Kalshi fees, bid/ask spread, slippage, settlement labels, and binary contract mechanics. Those are sensible for our market, but they are not in the paper's experiment.

7. Simulation shape: the paper's appendix uses a 21x21 PT/SL mesh, 100,000 iterations, max holding period 100, `phi = 2 ** (-1 / half_life)`, and Sharpe selection. Our defaults are smaller and adapted to the live-tape cadence.

## What Is Still Useful

- The earlier exit probe correctly showed that a historical grid can find attractive-looking nodes while the simulation-selected OU walk-forward result stayed negative. That is exactly the kind of anti-overfitting warning the paper is about.
- The mispricing strategy backtest can still be a valid new hypothesis, but its positive PnL projection must be treated as backtest evidence for a new strategy, not as a Carr/Lopez de Prado replication.
- The forward shadow is safe from an order-routing perspective: it is marked `research_only` and `places_orders: false`.

## Corrective Path

To test the paper exactly, build a separate `carr_otr_exact` harness with no entry logic:

1. Feed it only pre-existing/exogenous entry timestamps.
2. Choose one state variable before testing: held-position MtM PnL is the cleanest local analogue.
3. Fit the OU process on that state variable using the paper's parameterization.
4. Simulate 100,000 paths from each observed initial PnL.
5. Score the PT/SL mesh solely by Sharpe ratio.
6. Report the selected exits separately from any historical-grid comparator.
7. Validate the selected rule forward in shadow mode before treating it as tradable.
