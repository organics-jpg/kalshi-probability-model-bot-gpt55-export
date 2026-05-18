# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:34.612196+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `-0.02416299540383382`
- Tick Brownian delta log loss vs candle: `-0.048335883067936125`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.22231381731697444 | 0.615802122526655 | 9 | -224.0 | -4.0 |
| `v28` | 18 | 1 | 0.2772695563695016 | 0.7477383592052491 | 9 | -396.0 | -176.0 |
| `candle_brownian` | 18 | 1 | 0.2638107839370852 | 0.7207756345145865 | 9 | -396.0 | -176.0 |
| `tick_brownian` | 18 | 1 | 0.23964778853325136 | 0.6724397514466504 | 9 | -396.0 | -176.0 |
| `market_side_ask` | 18 | 1 | 0.185 | 0.5622728353473071 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
