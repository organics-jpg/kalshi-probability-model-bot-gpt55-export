# Paired Sidecar Spot Aggregate Diagnostic

Research-only aggregate across paired live sidecar/independent-spot diagnostics.

## Summary

- Generated UTC: `2026-05-13T02:02:09.225419+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `True`
- Diagnostic files ready / skipped / total: `82` / `1` / `83`
- Joined rows / markets: `1410` / `68`
- Rows / markets remaining for predeclared shadow floor: `0` / `0`
- Issue count: `1`
- Best model by Brier: `v28`
- Best model by log loss: `market_side_ask`
- Market-equal best model by Brier: `v28`
- Market-equal best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `-0.0005015872627756324`
- Tick Brownian delta log loss vs candle: `-0.000975902265224482`
- Market-equal tick Brownian delta Brier vs candle: `-0.0007303955855719468`
- Market-equal tick Brownian delta log loss vs candle: `-0.0014331700269436531`
- Tick Brownian better capture counts: Brier `23`, log loss `23`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 1410 | 68 | 0.27354961096998787 | 0.9144251002683972 | 683 | 2108.1 | -431.7 |
| `v28` | 1410 | 68 | 0.21048805396487674 | 0.6199110108478341 | 658 | 4906.0 | 39.7 |
| `candle_brownian` | 1410 | 68 | 0.2160451395784026 | 0.6191320592106702 | 679 | 85.00000000000001 | 3393.4 |
| `tick_brownian` | 1410 | 68 | 0.21554355231562697 | 0.6181561569454457 | 679 | -788.0 | 2649.4 |
| `market_side_ask` | 1410 | 68 | 0.21136906950354611 | 0.605671800393208 | 199 | 1758.6000000000001 | 1758.6000000000001 |

## Read

- This aggregates instrumentation diagnostics only; it is not a promotion artifact.
- The candidate-ready flag is a coverage floor for future predeclared shadow tests, not live-trading approval.
