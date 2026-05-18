# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T02:01:51.791505+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.003794820749754374`
- Tick Brownian delta log loss vs candle: `0.007595108088840674`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.3764693867748681 | 1.3247482883668211 | 9 | 147.0 | -2.0 |
| `v28` | 18 | 1 | 0.19783552385078598 | 0.5884035532386086 | 9 | 450.0 | 200.0 |
| `candle_brownian` | 18 | 1 | 0.23491587446159545 | 0.6629695583845834 | 9 | 450.0 | 200.0 |
| `tick_brownian` | 18 | 1 | 0.23871069521134983 | 0.670564666473424 | 9 | 450.0 | 200.0 |
| `market_side_ask` | 18 | 1 | 0.25505 | 0.703248534218705 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
